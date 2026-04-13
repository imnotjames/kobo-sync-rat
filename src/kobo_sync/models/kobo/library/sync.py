from pydantic.dataclasses import dataclass

from kobo_sync.models.dataclass import config

from .book import KoboEbookMetadata
from .entitlement import KoboEntitlement
from .reading_state import KoboReadingState


@dataclass(config=config)
class KoboSyncItemEntitlement:
    book_entitlement: KoboEntitlement

    book_metadata: KoboEbookMetadata

    reading_state: KoboReadingState


@dataclass(config=config)
class KoboSyncItem:
    new_entitlement: KoboSyncItemEntitlement | None

    changed_entitlement: KoboSyncItemEntitlement | None
