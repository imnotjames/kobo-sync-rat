from importlib.metadata import metadata
from logging import getLogger as get_logger
from urllib.parse import urljoin

from fastapi import APIRouter, Request
from fastapi.responses import PlainTextResponse

import kobo_sync_rat

logger = get_logger(__name__)
router = APIRouter()


@router.get("/", response_class=PlainTextResponse)
def index(request: Request):
    package_metadata = metadata(kobo_sync_rat.__name__)
    package_name = package_metadata.get("name")
    package_version = package_metadata.get("version")
    package_summary = package_metadata.get("summary")

    config_url = request.url_for("get_kobo_config")

    readme_text = [
        f"Welcome to {package_name} v{package_version}!",
        package_summary,
        "You can get started by downloading the config "
        f"at `{config_url}` and placing on your Kobo at "
        "`.kobo/Kobo/Kobo eReader.conf`.",
    ]

    return "\n\n".join(readme_text)


@router.get("/kobo.conf", response_class=PlainTextResponse)
def get_kobo_config(request: Request):
    api_endpoint = urljoin(str(request.base_url), "/").rstrip("/")

    config = f"[OneStoreServices]\napi_endpoint={api_endpoint}"

    return config
