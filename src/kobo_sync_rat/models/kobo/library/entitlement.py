from dataclasses import field
from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import Field
from pydantic.dataclasses import dataclass

from kobo_sync_rat.models.dataclass import config


class KoboEntitlementAccessibility(Enum):
    FULL = "Full"


class KoboEntitlementStatus(Enum):
    ACTIVE = "Active"


class KoboEntitlementOrigin(Enum):
    PURCHASED = "Purchased"
    IMPORTED = "Imported"


@dataclass(config=config)
class KoboEntitlementRange:
    range_from: datetime = Field(serialization_alias="From")


@dataclass(config=config)
class KoboEntitlementMetadata:
    pass


@dataclass(config=config)
class KoboEntitlement:
    id: UUID

    revision_id: UUID

    cross_revision_id: UUID

    active_period: KoboEntitlementRange

    last_modified: datetime

    created: datetime

    accessibility: KoboEntitlementAccessibility = KoboEntitlementAccessibility.FULL

    origin_category: KoboEntitlementOrigin = KoboEntitlementOrigin.PURCHASED

    is_removed: bool = False

    is_hidden_from_archive: bool = False

    is_locked: bool = False

    status: KoboEntitlementStatus = KoboEntitlementStatus.ACTIVE

    metadata: KoboEntitlementMetadata = field(
        default_factory=lambda: KoboEntitlementMetadata()
    )
