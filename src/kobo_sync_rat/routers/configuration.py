from logging import getLogger as get_logger
from typing import Mapping
from urllib.parse import urljoin

from fastapi import APIRouter, Request

from kobo_sync.models.kobo.configuration import KoboResourceContainer, KoboUserProfile
from kobo_sync.responses import PydanticResponse

logger = get_logger(__name__)


router = APIRouter()

INITIALIZATION_FLAGS = {
    "gpb_flow_enabled": "False",
    "instapaper_enabled": "False",
    "kobo_audiobooks_credit_redemption": "False",
    "kobo_audiobooks_enabled": "False",
    "kobo_audiobooks_orange_deal_enabled": "False",
    "kobo_audiobooks_subscriptions_enabled": "False",
    "kobo_display_price": "False",
    "kobo_dropbox_link_account_enabled": "False",
    "kobo_google_tax": "False",
    "kobo_googledrive_link_account_enabled": "False",
    "kobo_nativeborrow_enabled": "False",
    "kobo_onedrive_link_account_enabled": "False",
    "kobo_onestorelibrary_enabled": "False",
    "kobo_redeem_enabled": "False",
    "kobo_shelfie_enabled": "False",
    "kobo_subscriptions_enabled": "False",
    "kobo_superpoints_enabled": "False",
    "kobo_wishlist_enabled": "False",
    "use_one_store": "False",
}

EXTERNAL_RESOURCES: Mapping[str, str | Mapping[str, str]] = {
    "account_page": "https://www.kobo.com/account/settings",
    "account_page_rakuten": "https://my.rakuten.co.jp/",
    "audiobook_detail_page": "https://www.kobo.com/{region}/{language}/audiobook/{slug}",
    "audiobook_landing_page": "https://www.kobo.com/{region}/{language}/audiobooks",
    "audiobook_subscription_orange_deal_inclusion_url": "https://authorize.kobo.com/inclusion",
    "book_detail_page": "https://www.kobo.com/{region}/{language}/ebook/{slug}",
    "book_detail_page_rakuten": "http://books.rakuten.co.jp/rk/{crossrevisionid}",
    "book_landing_page": "https://www.kobo.com/ebooks",
    "categories_page": "https://www.kobo.com/ebooks/categories",
    "client_authd_referral": "https://authorize.kobo.com/api/AuthenticatedReferral/client/v1/getLink",
    "customer_care_live_chat": "https://v2.zopim.com/widget/livechat.html?key=Y6gwUmnu4OATxN3Tli4Av9bYN319BTdO",
    "dictionary_host": "https://ereaderfiles.kobo.com",
    "discovery_host": "https://discovery.kobobooks.com",
    "eula_page": "https://www.kobo.com/termsofuse?style=onestore",
    "free_books_page": {
        "EN": "https://www.kobo.com/{region}/{language}/p/free-ebooks",
        "FR": "https://www.kobo.com/{region}/{language}/p/livres-gratuits",
        "IT": "https://www.kobo.com/{region}/{language}/p/libri-gratuiti",
        "NL": "https://www.kobo.com/{region}/{language}/List/bekijk-het-overzicht-van-gratis-ebooks/QpkkVWnUw8sxmgjSlCbJRg",
        "PT": "https://www.kobo.com/{region}/{language}/p/livros-gratis",
    },
    "giftcard_epd_redeem_url": "https://www.kobo.com/{storefront}/{language}/redeem-ereader",
    "giftcard_redeem_url": "https://www.kobo.com/{storefront}/{language}/redeem",
    "help_page": "http://www.kobo.com/help",
    "instapaper_env_url": "https://www.instapaper.com/api/kobo",
    "instapaper_link_account_start": "https://authorize.kobo.com/{region}/{language}/linkinstapaper",
    "kobo_privacyCentre_url": "https://www.kobo.com/privacy",
    "love_dashboard_page": "https://www.kobo.com/{region}/{language}/kobosuperpoints",
    "love_points_redemption_page": "https://www.kobo.com/{region}/{language}/KoboSuperPointsRedemption?productId={ProductId}",
    "magazine_landing_page": "https://www.kobo.com/emagazines",
    "ppx_purchasing_url": "https://purchasing.kobo.com",
    "privacy_page": "https://www.kobo.com/privacypolicy?style=onestore",
    "reading_services_host": "https://readingservices.kobo.com",
    "redeem_interstitial_page": "https://www.kobo.com",
    "store_home": "www.kobo.com/{region}/{language}",
    "store_host": "www.kobo.com",
    "store_newreleases": "https://www.kobo.com/{region}/{language}/List/new-releases/961XUjtsU0qxkFItWOutGA",
    "store_search": "https://www.kobo.com/{region}/{language}/Search?Query={query}",
    "store_top50": "https://www.kobo.com/{region}/{language}/ebooks/Top",
    "subs_landing_page": "https://www.kobo.com/{region}/{language}/plus",
    "subs_management_page": "https://www.kobo.com/{region}/{language}/account/subscriptions",
    "subs_plans_page": "https://www.kobo.com/{region}/{language}/plus/plans",
    "subs_purchase_buy_templated": "https://www.kobo.com/{region}/{language}/Checkoutoption/{ProductId}/{TierId}",
    "terms_of_sale_page": "https://authorize.kobo.com/{region}/{language}/terms/termsofsale",
    "userguide_host": "https://ereaderfiles.kobo.com",
    "wishlist_page": "https://www.kobo.com/{region}/{language}/account/wishlist",
}


LOCAL_RESOURCES = {
    "add_device": "/v1/user/add-device",
    "add_entitlement": "/v1/library/{RevisionIds}",
    "affiliaterequest": "/v1/affiliate",
    "assets": "/v1/assets",
    "audiobook": "/v1/products/audiobooks/{ProductId}",
    "audiobook_preview": "/v1/products/audiobooks/{Id}/preview",
    "audiobook_purchase_withcredit": "/v1/store/audiobook/{Id}",
    "authorproduct_recommendations": "/v1/products/books/authors/recommendations",
    "autocomplete": "/v1/products/autocomplete",
    "book": "/v1/products/books/{ProductId}",
    "book_subscription": "/v1/products/books/subscriptions",
    "browse_history": "/v1/user/browsehistory",
    "categories": "/v1/categories",
    "category": "/v1/categories/{CategoryId}",
    "category_featured_lists": "/v1/categories/{CategoryId}/featured",
    "category_products": "/v1/categories/{CategoryId}/products",
    "checkout_borrowed_book": "/v1/library/borrow",
    "configuration_data": "/v1/configuration",
    "content_access_book": "/v1/products/books/{ProductId}/access",
    "daily_deal": "/v1/products/dailydeal",
    "deals": "/v1/deals",
    "delete_entitlement": "/v1/library/{Ids}",
    "delete_tag": "/v1/library/tags/{TagId}",
    "delete_tag_items": "/v1/library/tags/{TagId}/items/delete",
    "device_auth": "/v1/auth/device",
    "device_refresh": "/v1/auth/refresh",
    "ereaderdevices": "/v2/products/EReaderDeviceFeeds",
    "exchange_auth": "/v1/auth/exchange",
    "external_book": "/v1/products/books/external/{Ids}",
    "featured_list": "/v1/products/featured/{FeaturedListId}",
    "featured_lists": "/v1/products/featured",
    "fte_feedback": "/v1/products/ftefeedback",
    "funnel_metrics": "/v1/funnelmetrics",
    "get_download_keys": "/v1/library/downloadkeys",
    "get_download_link": "/v1/library/downloadlink",
    "get_tests_request": "/v1/analytics/gettests",
    "library_book": "/v1/user/library/books/{LibraryItemId}",
    "library_items": "/v1/user/library",
    "library_metadata": "/v1/library/{Ids}/metadata",
    "library_prices": "/v1/user/library/previews/prices",
    "library_search": "/v1/library/search",
    "library_sync": "/v1/library/sync",
    "notebooks": "/api/internal/notebooks",
    "personalizedrecommendations": "/v2/users/personalizedrecommendations",
    "post_analytics_event": "/v1/analytics/event",
    "product_nextread": "/v1/products/{ProductIds}/nextread",
    "product_prices": "/v1/products/{ProductIds}/prices",
    "product_recommendations": "/v1/products/{ProductId}/recommendations",
    "product_reviews": "/v1/products/{ProductIds}/reviews",
    "products": "/v1/products",
    "productsv2": "/v2/products",
    "quickbuy_checkout": "/v1/store/quickbuy/{PurchaseId}/checkout",
    "quickbuy_create": "/v1/store/quickbuy/purchase",
    "rakuten_token_exchange": "/v1/auth/rakuten_token_exchange",
    "rating": "/v1/products/{ProductId}/rating/{Rating}",
    "reading_state": "/v1/library/{Ids}/state",
    "related_items": "/v1/products/{Id}/related",
    "remaining_book_series": "/v1/products/books/series/{SeriesId}",
    "rename_tag": "/v1/library/tags/{TagId}",
    "review": "/v1/products/reviews/{ReviewId}",
    "review_sentiment": "/v1/products/reviews/{ReviewId}/sentiment/{Sentiment}",
    "shelfie_recommendations": "/v1/user/recommendations/shelfie",
    "tag_items": "/v1/library/tags/{TagId}/Items",
    "tags": "/v1/library/tags",
    "taste_profile": "/v1/products/tasteprofile",
    "update_accessibility_to_preview": "/v1/library/{EntitlementIds}/preview",
    "user_loyalty_benefits": "/v1/user/loyalty/benefits",
    "user_platform": "/v1/user/platform",
    "user_profile": "/v1/user/profile",
    "user_ratings": "/v1/user/ratings",
    "user_recommendations": "/v1/user/recommendations",
    "user_reviews": "/v1/user/reviews",
    "user_wishlist": "/v1/user/wishlist",
    "facebook_sso_page": "/signin/provider/Facebook/login",
    "password_retrieval_page": "/passwordretrieval.html",
    "pocket_link_account_start": "/linkpocket",
    "registration_page": "/signup",
    "social_authorization_host": "/social",
    "social_host": "/social",
    "more_sign_in_options": "/signin",
    "provider_external_sign_in_page": "/ExternalSignIn/{providerName}",
    "oauth_host": "",
    "sign_in_page": "/signin",
    "image_host": "/",
    "image_url_template": "/thumbnails/{ImageId}/{Width}/{Height}/default/{IsGreyscale}/image.jpg",
    "image_url_quality_template": "/thumbnails/{ImageId}/{Width}/{Height}/{Quality}/{IsGreyscale}/image.jpg",
}


@router.get("/v1/initialization", response_model=KoboResourceContainer)
def request_sync_initialization(request: Request):
    resources = {}

    for key, value in INITIALIZATION_FLAGS.items():
        resources[key] = value

    for key, object in EXTERNAL_RESOURCES.items():
        resources[key] = object

    for key, path in LOCAL_RESOURCES.items():
        resources[key] = urljoin(str(request.base_url), path)

    # Hack for oauth_host to work - without this we get `//.well-known`
    if "oauth_host" in resources:
        resources["oauth_host"] = str(resources["oauth_host"]).rstrip("/")

    headers = {
        "x-kobo-apitoken": "e30=",
    }
    content = KoboResourceContainer(resources=resources)

    return PydanticResponse(KoboResourceContainer, content=content, headers=headers)


@router.get("/v1/user/profile", response_model=KoboUserProfile)
def get_user_profile():
    return KoboUserProfile()


@router.get("/v1/user/loyalty/benefits")
def get_user_loyalty_benefits():
    return []


@router.get("/v1/user/wishlist")
def get_user_wishlist():
    return []


@router.post("/v1/analytics/gettests")
def post_analytics_get_tests():
    # I don't think we need to do much here
    return {
        "Result": "Success",
        "TestKey": "EXAMPLE",
        "Tests": {},
    }
