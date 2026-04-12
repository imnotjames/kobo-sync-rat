from typing import Any, Mapping

from fastapi.responses import JSONResponse
from pydantic import TypeAdapter
from starlette.background import BackgroundTask


class PydanticResponse(JSONResponse):
    def __init__(
        self,
        resource_type: Any,
        content: Any,
        status_code: int = 200,
        headers: Mapping[str, str] | None = None,
        media_type: str | None = None,
        background: BackgroundTask | None = None,
        by_alias: bool = True,
        exclude_none: bool = False,
        exclude_unset: bool = False,
    ) -> None:
        self._type_adapter = TypeAdapter(resource_type)
        self._by_alias = by_alias
        self._exclude_none = exclude_none
        self._exclude_unset = exclude_unset

        super().__init__(content, status_code, headers, media_type, background)

    def render(self, content: Any) -> bytes:
        return super().render(
            self._type_adapter.dump_python(
                content,
                mode="json",
                by_alias=self._by_alias,
                exclude_none=self._exclude_none,
                exclude_unset=self._exclude_unset,
            )
        )
