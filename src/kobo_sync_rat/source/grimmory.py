from dataclasses import field
from datetime import date, datetime
from logging import getLogger as get_logger
from typing import IO, Generator, Sequence
from urllib.parse import urljoin
from uuid import UUID

import requests
from bs4 import BeautifulSoup
from cachetools import TTLCache, cachedmethod
from pydantic import ConfigDict, TypeAdapter
from pydantic.alias_generators import to_camel
from pydantic.dataclasses import dataclass

from kobo_sync_rat.source.source import (
    EbookAuthor,
    EbookEvent,
    EbookEventType,
    EbookFormat,
    EbookLanguage,
    EbookMetadata,
    EbookSource,
    uuid6,
)

logger = get_logger(__name__)


URL_LOGIN = "api/v1/auth/login"
URL_BOOKS = "api/v1/books?withDescription=true&stripForListView=false"
URL_BOOK = "api/v1/books/{book_id}?withDescription=true&stripForListView=false"
URL_BOOK_CONTENTS = "api/v1/books/{book_id}/content?bookType=EPUB"
URL_BOOK_THUMBNAIL = "/api/v1/media/book/{book_id}/cover?token={token}"

BOOK_ID_PREFIX = 0x800C1023


GRIMMORY_OBJECT_CONFIG = ConfigDict(
    alias_generator=to_camel,
)


@dataclass(config=GRIMMORY_OBJECT_CONFIG)
class ResponseShelf:
    id: int

    user_id: int

    name: str

    public_shelf: bool

    book_count: int


@dataclass(config=GRIMMORY_OBJECT_CONFIG)
class ResponseFile:
    id: int

    added_on: datetime

    book_type: str

    extension: str

    file_name: str

    file_path: str

    file_size_kb: int


@dataclass(config=GRIMMORY_OBJECT_CONFIG)
class ResponseMetadata:
    title: str

    published_date: date | None = None

    publisher: str | None = None

    authors: Sequence[str] = field(default_factory=list)

    isbn_10: str | None = None

    isbn_13: str | None = None

    description: str | None = None

    series_name: str | None = None

    series_number: float | None = None


@dataclass(config=GRIMMORY_OBJECT_CONFIG)
class ResponseBook:
    id: int

    added_on: datetime

    metadata: ResponseMetadata

    shelves: Sequence[ResponseShelf]

    primary_file: ResponseFile

    read_status: str | None = None


class GrimmorySource(EbookSource):
    def __init__(
        self,
        base_url: str,
        username: str,
        password: str,
    ):
        self._base_url = base_url
        self._username = username
        self._password = password
        self._auth_cache = TTLCache(maxsize=10, ttl=300)

    @cachedmethod(lambda self: self._auth_cache)
    def _get_auth_token(self) -> str:
        payload = {
            "username": self._username,
            "password": self._password,
        }
        response = requests.post(
            urljoin(self._base_url, URL_LOGIN),
            json=payload,
        )

        if not response.ok:
            logger.error(f"Failed to auth: {response.text}")
            raise RuntimeError("something went wrong idk")

        data = response.json()

        token = data.get("accessToken")

        if not token:
            raise RuntimeError("no token")

        return token

    def _get_book_id(self, grimmory_id: int) -> UUID:
        return UUID(fields=(BOOK_ID_PREFIX, 0, 0, 0, 0, grimmory_id))

    def _get_grimmory_id(self, book_id: UUID) -> int:
        if book_id.fields[0] != BOOK_ID_PREFIX:
            raise RuntimeError("not a valid grimmory book ID")

        return book_id.fields[5]

    def _clean_description(self, description: str | None) -> str:
        if description is None:
            return ""

        return BeautifulSoup(description, "html.parser").text

    def _translate_grimmory_metadata(self, book: ResponseBook) -> EbookMetadata:
        if book.primary_file.book_type.lower() == "epub":
            format = EbookFormat.EPUB
        else:
            raise RuntimeError("Unknown book format")

        return EbookMetadata(
            id=self._get_book_id(book.id),
            title=book.metadata.title,
            description=self._clean_description(book.metadata.description),
            publisher=book.metadata.publisher,
            publication_date=book.metadata.published_date,
            isbn=book.metadata.isbn_13 or book.metadata.isbn_10,
            authors=[EbookAuthor(name=name) for name in book.metadata.authors],
            tags=[],
            series=None,
            language=EbookLanguage(code="en"),
            format=format,
        )

    def _get_grimmory_books(self) -> Sequence[ResponseBook]:
        token = self._get_auth_token()

        response = requests.get(
            urljoin(self._base_url, URL_BOOKS),
            headers={"Authorization": f"Bearer {token}"},
        )

        return TypeAdapter(
            Sequence[ResponseBook],
        ).validate_json(response.text, by_alias=True)

    def _translate_grimmory_events(self, books: Sequence[ResponseBook]):
        events: list[EbookEvent] = []

        # Do basically the same thing as filesystem for now.
        # If there's a way to actually event source using the API I haven't
        # figured it out yet.  Maybe the audit log?

        for book in books:
            event_id = uuid6(int(book.added_on.timestamp() * 1000000000), 0, book.id)

            events.append(
                EbookEvent(
                    event_id=event_id,
                    event_type=EbookEventType.CREATED,
                    timestamp=book.added_on,
                    metadata=self._translate_grimmory_metadata(book),
                )
            )

            # TODO: Once the metadata updated is available create a changed event

        return events

    def get_events(
        self, after_event_id: UUID | None = None
    ) -> Generator[EbookEvent, None, None]:
        for event in self._translate_grimmory_events(self._get_grimmory_books()):
            if after_event_id is not None and event.event_id <= after_event_id:
                continue

            yield event

    def get_book_metadata(self, book_id: UUID) -> EbookMetadata:
        grimmory_id = self._get_grimmory_id(book_id)
        token = self._get_auth_token()

        response = requests.get(
            urljoin(self._base_url, URL_BOOK.format(book_id=grimmory_id)),
            headers={"Authorization": f"Bearer {token}"},
        )

        book = TypeAdapter(
            ResponseBook,
        ).validate_json(response.text, by_alias=True)

        return self._translate_grimmory_metadata(book)

    def get_content_stream(self, book_id: UUID) -> IO[bytes]:
        token = self._get_auth_token()
        grimmory_id = self._get_grimmory_id(book_id)

        response = requests.get(
            urljoin(self._base_url, URL_BOOK_CONTENTS.format(book_id=grimmory_id)),
            headers={"Authorization": f"Bearer {token}"},
            stream=True,
        )

        if not response.ok:
            raise RuntimeError("error with request")

        return response.iter_content(chunk_size=4096)

    def get_cover_stream(self, book_id: UUID) -> IO[bytes]:
        token = self._get_auth_token()
        grimmory_id = self._get_grimmory_id(book_id)

        # TODO: in next grimmory release we can drop the token from the URL
        response = requests.get(
            urljoin(
                self._base_url,
                URL_BOOK_THUMBNAIL.format(book_id=grimmory_id, token=token),
            ),
            headers={"Authorization": f"Bearer {token}"},
            stream=True,
        )

        if not response.ok:
            raise RuntimeError("error with request")

        return response.iter_content(chunk_size=4096)
