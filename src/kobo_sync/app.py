import os
from logging import getLogger as get_logger

from fastapi import FastAPI, HTTPException, Request

from kobo_sync.middleware import LoggingMiddleware, OverrideBaseUrl
from kobo_sync.routers import (
    auth_router,
    configuration_router,
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


@app.get("/")
def index():
    return "This is the kobo sync server.  Read more at.."


@app.get("/elabels/{elabels_zip}")
def get_elabels_zip():
    raise HTTPException(status_code=404)


@app.api_route("/{full_path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def everything_else(request: Request):
    # Forward to the forward url
    logger.info("Not implemented")

    for header, value in request.headers.items():
        logger.info("%s: %s", header, value)

    logger.info("Body:")
    logger.info("-----------")
    logger.info(await request.body())
    logger.info("-----------")

    return None
