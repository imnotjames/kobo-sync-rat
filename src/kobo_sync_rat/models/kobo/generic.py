from dataclasses import field
from enum import Enum
from typing import Optional, Sequence

from pydantic import Field
from pydantic.dataclasses import dataclass

from kobo_sync_rat.models.dataclass import config


@dataclass(config=config)
class KoboPrice:
    currency: str | None = None

    price: float = 0


@dataclass(config=config)
class KoboLink:
    href: str = Field(serialization_alias="href")

    title: str = Field(serialization_alias="title")


@dataclass(config=config)
class KoboAccessibilityType:
    accessibility_type: str

    value: Optional[str] = None


@dataclass(config=config)
class KoboAccessibility:
    is_accessible: bool = False

    is_fixed_layout: bool = False

    is_text_to_speech_allowed: bool = False

    primary_content_type: str = "10"

    content_types: Sequence[str] = field(default_factory=list)

    e_pub_accessibilities: Sequence[KoboAccessibilityType] = field(default_factory=list)

    hazard_warning_types: Sequence[KoboAccessibilityType] = field(default_factory=list)


class KoboDownloadPlatform(Enum):
    GENERIC = "Generic"
    ANDROID = "Android"
    DESKTOP = "Desktop"


class KoboDownloadDRM(Enum):
    NONE = "None"
    ADOBE_DRM = "AdobeDrm"
    KDRM = "KDRM"


class KoboDownloadFormat(Enum):
    KEPUB = "KEPUB"
    EPUB3 = "EPUB3"
    EPUB3WEB = "EPUB3WEB"


@dataclass(config=config)
class KoboDownloadUrl:
    format: KoboDownloadFormat

    url: str

    size: int

    platform: KoboDownloadPlatform = KoboDownloadPlatform.GENERIC

    drm_type: KoboDownloadDRM = KoboDownloadDRM.NONE


class KoboContributorRole(Enum):
    AUTHOR = "Author"


@dataclass(config=config)
class KoboContributor:
    name: str

    role: KoboContributorRole = KoboContributorRole.AUTHOR


@dataclass(config=config)
class KoboLocale:
    language_code: str = "eng"

    script_code: str = ""

    country_code: str = ""
