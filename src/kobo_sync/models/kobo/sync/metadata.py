from dataclasses import field
from datetime import date
from enum import Enum
from typing import Mapping, Optional, Sequence
from uuid import UUID

from pydantic.dataclasses import dataclass

from kobo_sync.models.dataclass import config


@dataclass(config=config)
class KoboEbookPrice:
    currency_code: str | None = None

    total_amount: float = 0


@dataclass(config=config)
class KoboEbookPublisher:
    imprint: str

    name: str


class KoboEbookContributorRole(Enum):
    AUTHOR = "Author"


@dataclass(config=config)
class KoboEbookContributor:
    name: str

    role: KoboEbookContributorRole = KoboEbookContributorRole.AUTHOR


@dataclass(config=config)
class KoboEbookSeries:
    id: UUID

    name: str

    number: str

    number_float: float


@dataclass(config=config)
class KoboEbookEmptySeries:
    pass


class KoboEbookDownloadPlatform(Enum):
    GENERIC = "Generic"
    ANDROID = "Android"
    DESKTOP = "Desktop"


class KoboEbookDownloadDRM(Enum):
    NONE = "None"
    ADOBE_DRM = "AdobeDrm"
    KDRM = "KDRM"


class KoboEbookDownloadFormat(Enum):
    KEPUB = "KEPUB"
    EPUB3 = "EPUB3"
    EPUB3WEB = "EPUB3WEB"


@dataclass(config=config)
class KoboEbookDownloadUrl:
    format: KoboEbookDownloadFormat

    url: str

    size: int

    platform: KoboEbookDownloadPlatform = KoboEbookDownloadPlatform.GENERIC

    drm_type: KoboEbookDownloadDRM = KoboEbookDownloadDRM.NONE


@dataclass(config=config)
class KoboEbookLocale:
    language_code: str = "eng"
    script_code: str = ""
    country_code: str = ""


@dataclass(config=config)
class KoboEbookAccessibilityType:
    accessibility_type: str

    value: Optional[str] = None


@dataclass(config=config)
class EbookAccessibility:
    is_accessible: bool = False

    is_fixed_layout: bool = False

    is_text_to_speech_allowed: bool = False

    primary_content_type: str = "10"

    content_types: Sequence[str] = field(default_factory=list)

    e_pub_accessibilities: Sequence[KoboEbookAccessibilityType] = field(
        default_factory=list
    )

    hazard_warning_types: Sequence[KoboEbookAccessibilityType] = field(
        default_factory=list
    )


@dataclass(config=config)
class KoboEbookMetadata:
    entitlement_id: UUID

    cross_revision_id: UUID

    revision_id: UUID

    work_id: UUID

    download_urls: Sequence[KoboEbookDownloadUrl]

    publication_date: date

    title: str

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

    locale: KoboEbookLocale = field(default_factory=lambda: KoboEbookLocale())

    # accessibility_details: EbookAccessibility = field(default_factory=lambda: EbookAccessibility())

    related_group_id: Optional[UUID] = None

    categories: Sequence[UUID] = field(default_factory=lambda: [UUID(int=1)])

    phonetic_pronunciations: Mapping[str, str] = field(default_factory=dict)

    current_display_price: KoboEbookPrice = field(
        default_factory=lambda: KoboEbookPrice(currency_code="USD")
    )

    external_ids: Sequence[str] = field(default_factory=list)

    contributor_roles: Sequence[KoboEbookContributor] = field(default_factory=list)

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

    redirect_preview_urls: Sequence[KoboEbookDownloadUrl] = field(default_factory=list)

    has_preview: bool = field(default=False)

    promo_code_allowed: bool = field(default=False)

    is_eligible_for_kobo_love: bool = field(default=False)

    current_love_display_price: KoboEbookPrice = field(
        default_factory=lambda: KoboEbookPrice()
    )

    love_points_price: int = field(default=0)

    love_savings: float = field(default=0)
