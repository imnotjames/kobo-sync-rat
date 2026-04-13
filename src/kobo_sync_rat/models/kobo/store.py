from dataclasses import field
from datetime import datetime
from enum import Enum
from typing import Generic, Mapping, Sequence, TypeVar
from uuid import UUID

from pydantic import Field
from pydantic.dataclasses import dataclass

from kobo_sync_rat.models.dataclass import config
from kobo_sync_rat.models.kobo.generic import (
    KoboAccessibility,
    KoboContributor,
    KoboDownloadUrl,
    KoboLink,
    KoboLocale,
    KoboPrice,
)

RecordType = TypeVar("RecordType")


@dataclass(config=config)
class KoboStorePagination(Generic[RecordType]):
    items: Sequence[RecordType]
    item_count: int
    total_item_count: int
    total_page_count: int = field(default=1)
    current_page_index: int = field(default=1)
    items_per_page: int = field(default=10)
    filters: Mapping[str, Sequence[str]] | None = field(default=None)
    version_code: int = field(default=2)

    @classmethod
    def from_items(cls, items: Sequence[RecordType]):
        return cls(
            items=items,
            item_count=len(items),
            total_item_count=len(items),
        )

    @classmethod
    def empty(cls):
        return cls.from_items([])


class KoboProductType(Enum):
    BOOK = "Book"
    AUDIOBOOK = "AudioBook"


@dataclass(config=config)
class KoboFeaturedList:
    id: UUID
    name: str
    product_types: Sequence[KoboProductType] = field(
        default_factory=lambda: [KoboProductType.BOOK]
    )


# /v1/products/dailydeal
@dataclass(config=config)
class KoboProductHighlight:
    list_header: str

    title: str

    synopsis: str

    contributor_roles: Sequence[KoboContributor]

    series_number: str

    series_name: str

    series_id: UUID

    image_id: UUID

    price: KoboPrice

    cross_revision_id: UUID

    revision_id: UUID

    type: KoboProductType

    was_price: float


@dataclass(config=config)
class KoboProductBook:
    id: UUID

    cross_revision_id: UUID

    work_id: UUID

    related_group_id: UUID

    title: str

    subtitle: str

    slug: str

    publisher_name: str

    publication_date: datetime

    image_id: UUID

    description: str

    accessibility_details: KoboAccessibility = field(
        default_factory=lambda: KoboAccessibility()
    )

    language: str = "en"

    locale: KoboLocale = field(default_factory=lambda: KoboLocale())

    series_id: UUID | None = None

    series_name: str | None = None

    series_number: str | None = None

    series_number_float: float | int | None = None

    price: KoboPrice = field(default_factory=lambda: KoboPrice(currency="USD", price=0))

    isbn: str | None = Field(serialization_alias="ISBN", default=None)

    contributors: str | None = None

    contributor_roles: Sequence[KoboContributor] = field(default_factory=list)

    applicable_subscriptions: Sequence[str] = field(default_factory=list)

    eligible_for_kobo_love_discount: bool = False

    external_ids: Sequence[str] = field(default_factory=list)

    has_preview: bool = False

    age_verification_required: bool = False

    in_wishlist: bool = False

    is_content_sharing_enabled: bool = True

    is_free: bool = True

    is_internet_archive: bool = False

    is_pre_order: bool = False

    is_recommendation: bool = False

    promo_code_allowed: bool = False

    rating: int = 0

    rating_histogram: Mapping[int, int] = field(default_factory=dict)

    total_rating: int = 0

    redirect_preview_urls: Sequence[KoboDownloadUrl] = field(default_factory=list)

    was_price: int | float = 0


@dataclass(config=config)
class KoboProductBookContainer:
    book: KoboProductBook


@dataclass(config=config)
class KoboCategory:
    id: UUID

    name: str

    is_leaf: bool

    item_count: int = field(default=0)


@dataclass(config=config)
class KoboListReference:
    list_id: UUID

    title: str

    html_description: str

    items: Sequence[KoboProductBook]

    links: Mapping[str, KoboLink] = Field(serialization_alias="_links")


class KoboAutocompleteSuggestionType(Enum):
    AUDIOBOOK = "audiobook"
    BOOK = "book"
    PAGE = "page"
    SERIES = "series"


@dataclass(config=config)
class KoboAutocompleteSuggestion:
    type: KoboAutocompleteSuggestionType
    suggestion: str
    display: str
    title: str
    authors: Sequence[str] = field(default_factory=list)
    series: str | None = None


@dataclass(config=config)
class KoboProductPrice:
    id: UUID

    cross_revision_id: UUID

    price: KoboPrice

    eligible_for_kobo_love_discount: bool

    is_pre_order: bool


@dataclass(config=config)
class KoboDealEntry:
    id: UUID
    name: str
    url: str
    asset_group: str
    active_from: datetime = Field(serialization_alias="From")


@dataclass(config=config)
class KoboDeals:
    deals: Sequence[KoboDealEntry]

    @classmethod
    def empty(cls):
        return KoboDeals(deals=[])
