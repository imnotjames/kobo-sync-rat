import base64
import re
from dataclasses import dataclass
from itertools import islice
from logging import getLogger as get_logger
from typing import Annotated, Sequence
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import Field, TypeAdapter

from kobo_sync.dependencies import get_ebook_source
from kobo_sync.models.kobo.generic import (
    KoboContributor,
    KoboDownloadFormat,
    KoboDownloadPlatform,
    KoboDownloadUrl,
)
from kobo_sync.models.kobo.library import (
    KoboEbookMetadata,
    KoboEntitlement,
    KoboEntitlementRange,
    KoboReadingState,
    KoboSyncItem,
    KoboSyncItemEntitlement,
)
from kobo_sync.responses import PydanticResponse
from kobo_sync.source.source import (
    EbookEvent,
    EbookEventType,
    EbookMetadata,
    EbookSource,
)

logger = get_logger(__name__)
router = APIRouter()

LIMIT_PER_SYNC = 10
PATTERN_INVALID_SLUG_CHARACTERS = re.compile(r"[^a-z0-9]+")


@dataclass
class SyncToken:
    cursor: UUID = Field(serialization_alias="c")


def build_sync_item(request: Request, book: EbookEvent) -> KoboSyncItem:
    entitlement = KoboSyncItemEntitlement(
        book_entitlement=build_ebook_entitlement(book),
        book_metadata=build_ebook_metadata(request, book.metadata),
        reading_state=KoboReadingState(
            priority_timestamp=book.timestamp,
            entitlement_id=book.metadata.id,
            created=book.timestamp,
        ),
    )

    is_new = book.event_type == EbookEventType.CREATED

    return KoboSyncItem(
        new_entitlement=entitlement if is_new else None,
        changed_entitlement=entitlement if not is_new else None,
    )


def build_ebook_entitlement(book: EbookEvent) -> KoboEntitlement:
    return KoboEntitlement(
        id=book.metadata.id,
        revision_id=book.metadata.id,
        cross_revision_id=book.metadata.id,
        active_period=KoboEntitlementRange(range_from=book.timestamp),
        created=book.timestamp,
        last_modified=book.timestamp,
    )


def build_slug(metadata: EbookMetadata) -> str:
    # This sucks and there could be better.
    return str(metadata.id)


def build_cover_image_url(request: Request, metadata: EbookMetadata) -> str:
    return str(
        request.url_for(
            "get_thumbnail",
            book_id=metadata.id,
            width=0,
            height=0,
            quality="default",
            is_greyscale=False,
        )
    )


def build_download_url(request: Request, metadata: EbookMetadata, format: str):
    return str(
        request.url_for("download_book", book_id=metadata.id, book_format=format)
    )


def build_ebook_metadata(
    request: Request, metadata: EbookMetadata
) -> KoboEbookMetadata:
    return KoboEbookMetadata(
        entitlement_id=metadata.id,
        cross_revision_id=metadata.id,
        revision_id=metadata.id,
        work_id=metadata.id,
        # cover_image_id=book.metadata.id,
        cover_image_url=build_cover_image_url(request, metadata),
        title=metadata.title,
        description=metadata.description,
        slug=build_slug(metadata),
        isbn=metadata.isbn,
        publication_date=metadata.publication_date,
        contributors=[a.name for a in metadata.authors],
        contributor_roles=[KoboContributor(name=a.name) for a in metadata.authors],
        download_urls=[
            KoboDownloadUrl(
                platform=KoboDownloadPlatform.GENERIC,
                format=KoboDownloadFormat.EPUB3,
                size=0,
                url=build_download_url(request, metadata, "EPUB"),
            )
        ],
    )


def _parse_last_event_id(request: Request) -> UUID | None:
    sync_token_header = request.headers.get("x-kobo-synctoken")

    if sync_token_header is None:
        return None

    try:
        serialized_token = base64.b64decode(sync_token_header)

        sync_token: SyncToken = TypeAdapter(SyncToken).validate_json(
            serialized_token,
            by_alias=True,
        )

        return sync_token.cursor
    except Exception:
        logger.exception("Failed to parse sync token, starting from scratch")

    return None


def _generate_sync_token(request: Request, records: list[EbookEvent]) -> str | None:
    if len(records) == 0:
        return request.headers.get("x-kobo-synctoken")

    try:
        sync_token = SyncToken(
            cursor=records[-1].event_id,
        )

        serialized_token = TypeAdapter(SyncToken).dump_json(sync_token, by_alias=True)

        return base64.b64encode(serialized_token).decode()
    except Exception:
        logger.exception("Failed to generate sync token")

    return None


@router.get("/v1/library/sync", response_model=Sequence[KoboSyncItem])
def library_sync(
    request: Request, ebook_source: Annotated[EbookSource, Depends(get_ebook_source)]
):
    # Validate expected kobo user via `x-kobo-userkey` or something else?
    # Read headers for `x-kobo-sync` token
    # Parse `x-kobo-sync` and figure out where we need to start reading from
    # Generate N book entitlements - of either new or changes based on how old the book is
    # If there are more than N book entitlements, set `continue` and a sync token

    # NewEntitlement
    # ChangedEntitlement
    #   BookEntitlement
    #   ReadingState
    #   BookMetadata

    # Request:
    #
    # x-kobo-userkey - used for authenticating some calls
    # x-kobo-synctoken - Read to get current state
    #
    # Log from the following headers:
    # x-kobo-affiliatename: Kobo
    # x-kobo-appversion: 4.45.23640
    # x-kobo-deviceid: HEXDEVICEID
    # x-kobo-devicemodel: Kobo Clara BW
    # x-kobo-deviceos: 4.9.77
    # x-kobo-deviceosversion: NA
    # x-kobo-platformid: 00000000-0000-0000-0000-000000000391

    # If need to keep syncing, set `x-kobo-sync`
    #
    # "x-kobo-sync" - if specified as "continue", kobo keeps syncing
    # "x-kobo-sync-mode" - something for the server to send back for how to merge?
    #      "delta"
    # "x-kobo-recent-reads" - ???
    # "x-kobo-synctoken" -- always passed back in.  App state

    cursor = _parse_last_event_id(request)

    records = list(
        islice(ebook_source.get_events(after_event_id=cursor), LIMIT_PER_SYNC)
    )
    has_more_records = False

    content = [build_sync_item(request, book_event) for book_event in records]
    sync_token = _generate_sync_token(request, records)

    headers = {
        "x-kobo-sync-mode": "delta",
    }

    if sync_token is not None:
        headers["x-kobo-synctoken"] = sync_token

    if has_more_records:
        headers["x-kobo-sync"] = "continue"

    return PydanticResponse(
        Sequence[KoboSyncItem],
        content=content,
        headers=headers,
        exclude_none=True,
    )


@router.get(
    "/v1/library/{book_id}/metadata", response_model=Sequence[KoboEbookMetadata]
)
def get_library_metadata(
    book_id: UUID,
    request: Request,
    ebook_source: Annotated[EbookSource, Depends(get_ebook_source)],
):
    book_metadata = ebook_source.get_book_metadata(book_id)

    if book_metadata is None:
        raise HTTPException(status_code=404)

    return PydanticResponse(
        Sequence[KoboEbookMetadata], [build_ebook_metadata(request, book_metadata)]
    )


@router.get("/v1/library/{book_id}/state", response_model=KoboReadingState)
def get_reading_state(
    book_id: UUID,
):
    return None


@router.put("/v1/library/{book_id}/state")
def update_reading_state(book_id: UUID, reading_state: KoboReadingState):
    return None


@router.get("/thumbnails/{book_id}/{width}/{height}/{quality}/{is_greyscale}/image.jpg")
def get_thumbnail(
    book_id: UUID,
    width: int,
    height: int,
    quality: str,
    is_greyscale: bool,
    ebook_source: Annotated[EbookSource, Depends(get_ebook_source)],
):
    cover_stream = ebook_source.get_cover_stream(book_id)

    # TODO: Read and resize the thumbnail?
    return StreamingResponse(content=cover_stream)


@router.get("/v1/library/{book_id}/download/{book_format}")
def download_book(
    book_id: UUID,
    book_format: str,
    ebook_source: Annotated[EbookSource, Depends(get_ebook_source)],
):
    # Look up book by book_id
    # Look up book format for book
    # Read book file to FileResponse()
    if book_format.lower() == "epub":
        content_stream = ebook_source.get_content_stream(book_id)

        return StreamingResponse(content=content_stream)
    elif book_format.lower() == "kepub":
        # Create kepub file in cache if possible
        # Read kepub file if exists

        raise RuntimeError()

    raise HTTPException(status_code=404)
