import os
from logging import getLogger as get_logger

from fastapi import FastAPI, HTTPException, Request

from kobo_sync_rat.middleware import LoggingMiddleware, OverrideBaseUrl
from kobo_sync_rat.routers import (
    auth_router,
    configuration_router,
    documentation_router,
    library_router,
    store_router,
)

logger = get_logger(__name__)


app = FastAPI()

app.add_middleware(LoggingMiddleware)
app.add_middleware(OverrideBaseUrl, base_url=os.environ.get("BASE_URL"))

app.include_router(configuration_router)
app.include_router(auth_router)
app.include_router(library_router)
app.include_router(store_router)
app.include_router(documentation_router)


@app.get("/elabels/{elabels_zip}")
def get_elabels_zip():
    raise HTTPException(status_code=404)


@app.api_route("/{full_path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def everything_else(request: Request):
    # Forward to the forward url
    logger.debug("Not implemented")

    for header, value in request.headers.items():
        logger.debug("%s: %s", header, value)

    logger.debug("Body:")
    logger.debug("-----------")
    logger.debug(await request.body())
    logger.debug("-----------")

    return None
