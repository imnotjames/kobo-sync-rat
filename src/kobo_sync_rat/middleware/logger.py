from logging import (
    CRITICAL,
    DEBUG,
    ERROR,
    INFO,
    NOTSET,
    WARNING,
)
from logging import (
    getLogger as get_logger,
)

from fastapi import Request, Response
from starlette.middleware.base import (
    BaseHTTPMiddleware,
    DispatchFunction,
    RequestResponseEndpoint,
)
from starlette.types import ASGIApp

logger = get_logger(__name__)


type LOG_LEVEL = NOTSET | DEBUG | INFO | WARNING | ERROR | CRITICAL


# Define logging middleware
class LoggingMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app: ASGIApp,
        dispatch: DispatchFunction | None = None,
        http_request_level: LOG_LEVEL = INFO,
        kobo_metadata_level: LOG_LEVEL = INFO,
    ):
        super().__init__(app, dispatch)
        self._http_request_level = http_request_level
        self._kobo_metadata_level = kobo_metadata_level

    def _log_kobo_headers(self, request: Request):
        for key, value in request.headers.items():
            if not key.lower().startswith("x-kobo-"):
                continue

            logger.log(self._kobo_metadata_level, "%s: %s", key, value)

    def _log_request(self, request: Request, response: Response):
        logger.log(
            self._http_request_level,
            "%s %s - %d",
            request.method,
            request.url.path,
            response.status_code,
        )

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        self._log_kobo_headers(request)

        response = await call_next(request)

        self._log_request(request, response)

        return response
