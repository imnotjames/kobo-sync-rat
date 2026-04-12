from logging import getLogger as get_logger
from urllib.parse import urljoin, urlparse

from starlette.types import ASGIApp, Receive, Scope, Send

logger = get_logger(__name__)


class OverrideBaseUrl:
    def __init__(self, app: ASGIApp, base_url: str | None):
        self.app = app

        if base_url is not None:
            parsed_url = urlparse(base_url)

            self._scheme = parsed_url.scheme
            self._netloc = parsed_url.netloc
            self._path = parsed_url.path.rstrip("/") + "/"
        else:
            self._scheme = None
            self._netloc = None
            self._path = None

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        server_host, server_port = scope.get("server", (None, None))
        netloc = self._netloc or f"{server_host}:{server_port}"

        # Remove the host header and then replace it with our new host
        headers: list[tuple[bytes, bytes]] = scope.get("headers", [])
        headers = [(key, value) for key, value in headers if key != b"host"]
        headers.append((b"host", netloc.encode()))

        scope["headers"] = headers

        if self._scheme is not None:
            scope["scheme"] = self._scheme

        if self._path is not None:
            new_path = urljoin(self._path, scope.get("path", "").lstrip("/"))
            scope["path"] = new_path
            scope["raw_path"] = new_path.encode()

            # TODO: Somehow fix the routes so this only applies to the URL generation..

        await self.app(scope, receive, send)
