from logging import getLogger as get_logger

from fastapi import APIRouter

logger = get_logger(__name__)
router = APIRouter()


@router.get("/v1/user/recommendations")
def get_recommendations():
    return []


@router.get("/v1/products/featured/{featured_list_id}")
def get_featured_products():
    return []


@router.get("/v1/products/featured")
def get_featured_products_lists():
    return []


@router.get("/v1/deals")
def get_deals():
    return {"Deals": []}
