from dataclasses import field
from datetime import datetime
from enum import Enum
from typing import Sequence
from uuid import UUID

from pydantic.dataclasses import dataclass

from kobo_sync.models.dataclass import config


class Region(Enum):
    # I only know of these two.
    US = "US"
    JP = "JP"


class CultureCode(Enum):
    # This can probably be something from Python?
    EN_US = "en-US"


class OptInSetting(Enum):
    # TODO: There's some missing here but I don't have them
    EXPLICIT_NO = "ExplicitlyConsentedNo"


class AnalyticsPermission(Enum):
    FEATURE_RECOMMENDATION = "feature.recommendation"
    ANALYTICS_USER = "analytics.user"
    ANALYTICS_PLATFORM_FEATURES = "analytics.platform.features"
    ANALYTICS_CATALOG = "analytics.catalog"
    ANALYTICS_PLATFORM_CRASHREPORTING = "analytics.platform.crashreporting"
    ANALYTICS_PLATFORM_AB = "analytics.platform.AB"
    READING_STATS_SOCIAL = "readingstats.social"
    ANALYTICS_TRACKING_CAMPAIGNS = "analytics.tracking.campaigns"
    ANALYTICS_TRACKING = "analytics.tracking"
    ANALYTICS_TRACKING_GOOGLEANALYTICS = "analytics.tracking.googleAnalytics"
    ANALYTICS_TRACKING_GOOGLETAGMANAGER = "analytics.tracking.googleTagManager"
    ANALYTICS_TRACKING_MAXYMISER = "analytics.tracking.maxymiser"
    ANALYTICS_TRACKING_CRASHLYTICS = "analytics.tracking.crashlytics"
    ANALYTICS_TRACKING_HOTJAR = "analytics.tracking.hotjar"
    ANALYTICS_TRACKING_FIREBASE = "analytics.tracking.firebase"
    ANALYTICS_TRACKING_BUILDERIO = "analytics.tracking.builderio"
    ANALYTICS_TRACKING_VWO = "analytics.tracking.VWO"
    ANALYTICS_TRACKING_DATADOG = "analytics.tracking.datadog"
    ANALYTICS_TRACKING_LAUNCHDARKLY = "analytics.tracking.launchDarkly"
    ANALYTICS_TRACKING_ALGOLIA = "analytics.tracking.algolia"
    ANALYTICS_TRACKING_GOOGLEADWORDS = "analytics.tracking.googleadwords"
    ANALYTICS_TRACKING_FACEBOOKCONNECT = "analytics.tracking.facebookConnect"
    ANALYTICS_TRACKING_GOOGLEPLUSPLATFORM = "analytics.tracking.googlePlusPlatform"
    ANALYTICS_TRACKING_TWITTERBUTTON = "analytics.tracking.twitterButton"
    ANALYTICS_TRACKING_ADJUST = "analytics.tracking.adjust"
    ANALYTICS_TRACKING_FACEBOOK = "analytics.tracking.facebook"
    ANALYTICS_TRACKING_CRITEO = "analytics.tracking.criteo"
    ANALYTICS_TRACKING_BING = "analytics.tracking.bing"
    ANALYTICS_TRACKING_TALKABLE = "analytics.tracking.talkable"
    ANALYTICS_TRACKING_PINTEREST = "analytics.tracking.pinterest"
    ANALYTICS_TRACKING_RAKUTENLINKSHARE = "analytics.tracking.rakutenLinkshare"
    ANALYTICS_TRACKING_BRANCH = "analytics.tracking.branch"
    ANALYTICS_TRACKING_BUTTON = "analytics.tracking.button"
    ANALYTICS_TRACKING_RAKUTENADVERTISING = "analytics.tracking.rakutenAdvertising"
    ANALYTICS_TRACKING_LINKEDIN = "analytics.tracking.linkedIn"
    ANALYTICS_TRACKING_DROP = "analytics.tracking.drop"
    ANALYTICS_TRACKING_ICHANNEL = "analytics.tracking.iChannel"
    ANALYTICS_TRACKING_RESPONSYS = "analytics.tracking.responsys"
    ANALYTICS_TRACKING_EBAY = "analytics.tracking.eBay"
    ANALYTICS_TRACKING_TEADS = "analytics.tracking.teads"
    ANALYTICS_TRACKING_ONETAG = "analytics.tracking.onetag"
    ANALYTICS_TRACKING_RTBHOUSE = "analytics.tracking.rtbHouse"
    ANALYTICS_TRACKING_CISION = "analytics.tracking.cision"
    ANALYTICS_TRACKING_XANDR = "analytics.tracking.xandr"
    ANALYTICS_TRACKING_ADFORM = "analytics.tracking.adform"
    ANALYTICS_TRACKING_QUANTCAST = "analytics.tracking.quantcast"
    ANALYTICS_TRACKING_TIKTOK = "analytics.tracking.tikTok"
    ANALYTICS_TRACKING_ALKEMY = "analytics.tracking.alkemy"
    ANALYTICS_TRACKING_REDDIT = "analytics.tracking.reddit"


@dataclass(config=config)
class KoboLoyaltyDetails:
    loyalty_is_active: bool

    loyalty_start_date: datetime | None = None

    loyalty_tag_string: str | None = None

    loyalty_tags: int = 0

    loyalty_current_balance: int = 0


@dataclass(config=config)
class KoboUserProfile:
    affiliate_name: str = "Awful"

    country_code: Region = Region.US

    store_front: Region = Region.US

    geo: Region = Region.US

    iso_culture_code: CultureCode = CultureCode.EN_US

    is_one_store: bool = False

    is_child_account: bool = False

    is_library_migrated: bool = True

    vip_membership_purchased: bool = True

    has_purchased: bool = True

    has_purchased_book: bool = True

    has_purchased_audiobook: bool = False

    safe_search: bool = False

    audiobooks_enabled: bool = False

    is_orange_affiliated: bool = False

    is_eligible_for_orange_deal: bool = False

    platform_id: UUID = field(default_factory=lambda: UUID(int=1))

    partner_id: UUID = field(default_factory=lambda: UUID(int=1))

    loyalty_details: KoboLoyaltyDetails = field(
        default_factory=lambda: KoboLoyaltyDetails(loyalty_is_active=False)
    )

    kobo_crm_opt_in_setting: OptInSetting = OptInSetting.EXPLICIT_NO

    privacy_permissions: Sequence[AnalyticsPermission] = field(default_factory=list)

    linked_accounts: Sequence[str] = field(default_factory=list)
