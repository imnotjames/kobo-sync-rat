from logging import getLogger as get_logger
from typing import Sequence
from uuid import UUID

from fastapi import APIRouter, HTTPException

from kobo_sync_rat.models.kobo.generic import KoboPrice
from kobo_sync_rat.models.kobo.store import (
    KoboAutocompleteSuggestion,
    KoboCategory,
    KoboDeals,
    KoboFeaturedList,
    KoboListReference,
    KoboProductBook,
    KoboProductBookContainer,
    KoboProductHighlight,
    KoboProductPrice,
    KoboStorePagination,
)

logger = get_logger(__name__)
router = APIRouter()


@router.get(
    "/v1/user/recommendations",
    response_model=KoboStorePagination[KoboProductBookContainer],
)
def get_recommendations():
    return KoboStorePagination.empty()


@router.get(
    "/v1/products/featured/{featured_list_id}",
    response_model=KoboStorePagination[KoboProductBookContainer],
)
def get_featured_products():
    return KoboStorePagination.empty()


@router.get(
    "/v1/products/featured/", response_model=KoboStorePagination[KoboFeaturedList]
)
def get_featured_products_lists():
    return KoboStorePagination.empty()


@router.get(
    "/v1/products/featuredforkoboplus/",
    response_model=KoboStorePagination[KoboFeaturedList],
)
def get_featured_products_kobo_plus():
    return KoboStorePagination.empty()


@router.get("/v1/deals", response_model=KoboDeals)
def get_deals():
    return KoboDeals.empty()


@router.get("/v1/products/{like_other_book_id}/recommendations")
def get_product_recommendations(like_other_book_id: UUID):
    return KoboStorePagination.empty()


@router.get(
    "/v1/products/autocomplete",
    response_model=KoboStorePagination[KoboAutocompleteSuggestion],
)
def get_product_search_autocomplete():
    return KoboStorePagination.empty()


@router.get("/v1/products", response_model=KoboStorePagination[KoboProductBook])
def get_products():
    return KoboStorePagination.empty()


@router.get("/v1/products/books/", response_model=KoboStorePagination[KoboProductBook])
def get_products_books():
    return []


@router.get("/v1/products/books/{book_id}/", response_model=KoboProductBookContainer)
def get_products_book(book_id: UUID):
    raise HTTPException(status_code=404)


@router.get("/v1/products/dailydeal", response_model=KoboProductHighlight)
def get_daily_deal():
    raise HTTPException(status_code=404)


@router.get("/v1/products/books/subscriptions")
def get_book_subscriptions():
    return []


@router.get(
    "/v1/categories/{category_id}", response_model=KoboStorePagination[KoboCategory]
)
def get_categories(category_id: UUID):
    return KoboStorePagination.empty()


@router.get(
    "/v1/categories/{category_id}/featured", response_model=Sequence[KoboListReference]
)
def get_category_featured_products(category_id: UUID):
    # Returns a list of featured lists for a category
    return []


@router.post("/v1/products/{product_id}/rating/{rating}")
def post_product_rating(product_id: UUID, rating: int):
    # Persist it somewhere?
    return


@router.get(
    "/v1/products/{comma_separated_product_ids}/price",
    response_model=Sequence[KoboProductPrice],
)
def get_product_prices(comma_separated_product_ids: str):
    product_ids = [
        UUID(hex=p) for p in comma_separated_product_ids.split(",") if len(p) > 0
    ]

    if len(product_ids) == 0:
        raise HTTPException(status_code=404)

    return [
        KoboProductPrice(
            id=product_id,
            cross_revision_id=product_id,
            price=KoboPrice(currency="USD", price=0),
            eligible_for_kobo_love_discount=False,
            is_pre_order=False,
        )
        for product_id in product_ids
    ]
