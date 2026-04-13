from dataclasses import field
from datetime import date
from typing import Mapping, Optional, Sequence
from uuid import UUID

from pydantic.dataclasses import dataclass

from kobo_sync_rat.models.dataclass import config
from kobo_sync_rat.models.kobo.generic import (
    KoboAccessibility,
    KoboContributor,
    KoboDownloadUrl,
    KoboLocale,
    KoboPrice,
)


@dataclass(config=config)
class KoboEbookPublisher:
    imprint: str

    name: str


@dataclass(config=config)
class KoboEbookSeries:
    id: UUID

    name: str

    number: str

    number_float: float


@dataclass(config=config)
class KoboEbookEmptySeries:
    pass


@dataclass(config=config)
class KoboEbookMetadata:
    entitlement_id: UUID

    cross_revision_id: UUID

    revision_id: UUID

    work_id: UUID

    publication_date: date

    title: str

    download_urls: Sequence[KoboDownloadUrl] = field(default_factory=list)

    cover_image_id: UUID | None = None

    cover_image_url: str | None = None

    subtitle: Optional[str] = None

    description: Optional[str] = None

    language: Optional[str] = "en"

    publisher: KoboEbookPublisher = field(
        default_factory=lambda: KoboEbookPublisher("Example", "Example")
    )

    isbn: Optional[str] = None

    slug: Optional[str] = None

    locale: KoboLocale = field(default_factory=lambda: KoboLocale())

    accessibility_details: KoboAccessibility = field(
        default_factory=lambda: KoboAccessibility()
    )

    related_group_id: Optional[UUID] = None

    categories: Sequence[UUID] = field(default_factory=lambda: [UUID(int=1)])

    phonetic_pronunciations: Mapping[str, str] = field(default_factory=dict)

    current_display_price: KoboPrice = field(
        default_factory=lambda: KoboPrice(currency="USD")
    )

    external_ids: Sequence[str] = field(default_factory=list)

    contributor_roles: Sequence[KoboContributor] = field(default_factory=list)

    contributors: Sequence[str] = field(default_factory=list)

    series: KoboEbookSeries | KoboEbookEmptySeries = field(
        default_factory=lambda: KoboEbookEmptySeries()
    )

    genre: str = "Read"

    is_internet_archive: bool = field(default=False)

    is_a_i_summary_enabled: bool = field(default=False)

    is_annotation_export_enabled: bool = field(default=False)

    is_pre_order: bool = field(default=False)

    is_social_enabled: bool = field(default=False)

    age_verification_required: bool = field(default=False)

    is_recommendation: bool = field(default=False)

    redirect_preview_urls: Sequence[KoboDownloadUrl] = field(default_factory=list)

    has_preview: bool = field(default=False)

    promo_code_allowed: bool = field(default=False)

    is_eligible_for_kobo_love: bool = field(default=False)

    current_love_display_price: KoboPrice = field(default_factory=lambda: KoboPrice())

    love_points_price: int = field(default=0)

    love_savings: float = field(default=0)
