import os
from contextlib import AbstractContextManager
from datetime import UTC, datetime
from logging import getLogger as get_logger
from threading import Lock
from typing import IO, Any, Generator, MutableMapping, Optional, Sequence
from uuid import UUID

from cachetools import LRUCache, cachedmethod

from kobo_sync_rat.metadata.base import MetadataReader
from kobo_sync_rat.source.source import (
    EbookEvent,
    EbookEventType,
    EbookMetadata,
    EbookSource,
    uuid6,
)

logger = get_logger(__name__)


SECOND_IN_NS = 1000000000


class FilesystemSource(EbookSource):
    def __init__(
        self,
        root_path: str,
        metadata_readers: Sequence[MetadataReader] = tuple(),
        ebook_metadata_cache: Optional[MutableMapping] = None,
        ebook_path_cache: Optional[MutableMapping] = None,
        lock: Optional[AbstractContextManager[Any, Optional[bool]]] = None,
    ):
        self._root_path = root_path
        self._metadata_readers = metadata_readers

        self._ebook_path_cache = (
            ebook_path_cache if ebook_path_cache is not None else LRUCache(maxsize=4096)
        )
        self._ebook_metadata_cache = (
            ebook_metadata_cache
            if ebook_metadata_cache is not None
            else LRUCache(maxsize=4096)
        )
        self._lock = lock if lock is not None else Lock()

    @cachedmethod(
        lambda self: self._ebook_metadata_cache,
        lock=lambda self: self._lock,
    )
    def _read_metadata(self, entry_path: str) -> EbookMetadata | None:
        for reader in self._metadata_readers:
            try:
                return reader.read_metadata(entry_path)
            except Exception:
                logger.exception(f"{str(type(reader))} cannot parse {entry_path}")

        return None

    @cachedmethod(
        lambda self: self._ebook_path_cache,
        lock=lambda self: self._lock,
    )
    def _get_ebook_path_by_id(self, book_id: UUID) -> str | None:
        for book_path, _, _, _ in self._walk_ebooks(self._root_path):
            metadata = self._read_metadata(book_path)
            if metadata.id == book_id:
                return book_path

        return None

    def _walk_ebooks(
        self, ebook_path: str, max_depth: int = 5
    ) -> Generator[tuple[str, int, int, int], None, None]:
        logger.debug(f"Walking {ebook_path} to scan for ebooks")

        # scandir instead of walk to have more control over the depth
        with os.scandir(ebook_path) as it:
            for entry in it:
                if entry.is_dir():
                    if max_depth <= 0:
                        # If the max-depth has run out, we can't recurse
                        # and should bail out.  In theory this should be
                        # an error but because I would rather fail
                        # in a way that is "working" let's log an error
                        # instead and pretend it never happened.
                        logger.warning("hit max depth for ebook search")
                        continue

                    yield from self._walk_ebooks(entry.path, max_depth=max_depth - 1)
                    continue

                if not entry.is_file():
                    # I don't think this is possible - it's either a file
                    # or a directory.  Still, this seems safer.
                    continue

                entry_stat = entry.stat()

                changed_ns = entry_stat.st_mtime_ns
                created_ns = getattr(entry_stat, "st_birthtime_ns", changed_ns)

                # TODO: use the statx system call to get birthtime?

                yield entry.path, created_ns, changed_ns, entry_stat.st_ino

    def _get_event_list(self) -> Sequence[tuple[UUID, EbookEventType, int, str]]:
        # TODO: Cache for 1m
        events: list[tuple[UUID, EbookEventType, int, str]] = []

        for entry_path, created_ns, changed_ns, inode in self._walk_ebooks(
            self._root_path
        ):
            events.append(
                (
                    uuid6(created_ns, 0, inode),
                    EbookEventType.CREATED,
                    created_ns,
                    entry_path,
                )
            )

            # If changed_ns is > some difference from created_ns, create a changed event
            if changed_ns - created_ns > SECOND_IN_NS:
                events.append(
                    (
                        uuid6(changed_ns, 0, inode),
                        EbookEventType.MODIFIED,
                        changed_ns,
                        entry_path,
                    )
                )

        # Sort by the UUID generated
        events.sort(key=lambda e: e[0])

        return events

    def get_events(
        self, after_event_id: UUID | None = None
    ) -> Generator[EbookEvent, None, None]:
        # While we could set up a listener to inotify events, tracking ebooks
        # that are changed based on that, it's not really as reliable across
        # multiple use cases.  In mine, it won't work because I use NFS.
        #
        # Instead, we walk the directory when asked for books.
        #
        # In the future, we could walk the directory async & store the books
        # we found in-memory?  Or in a SQLite database which is faster to query?
        #
        # But until we actually need that this should be good enough &
        # the API _should_ allow for that as a source?

        for (
            event_id,
            event_type,
            event_timestamp_ns,
            entry_path,
        ) in self._get_event_list():
            # If after_event_id is specified, skip events until we get where we want to be
            if after_event_id is not None and event_id <= after_event_id:
                continue

            # Start yielding & read metadata for each yielded item
            yield EbookEvent(
                event_id=event_id,
                event_type=event_type,
                timestamp=datetime.fromtimestamp(
                    event_timestamp_ns // SECOND_IN_NS, UTC
                ),
                metadata=self._read_metadata(entry_path),
            )

    def get_book_metadata(self, book_id: UUID) -> EbookMetadata:
        entry_path = self._get_ebook_path_by_id(book_id)

        if entry_path is None:
            raise RuntimeError("Missing book")

        return self._read_metadata(entry_path)

    def get_content_stream(self, book_id: UUID) -> IO[bytes]:
        entry_path = self._get_ebook_path_by_id(book_id)

        return open(entry_path, "rb")

    def get_cover_stream(self, book_id: UUID) -> IO[bytes]:
        raise NotImplementedError()
