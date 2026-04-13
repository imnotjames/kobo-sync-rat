from enum import Enum
from uuid import UUID

from pydantic.dataclasses import dataclass

from kobo_sync_rat.models.dataclass import config


class TokenType(Enum):
    BEARER = "Bearer"


@dataclass(config=config)
class KoboTokenResponse:
    token_type: TokenType
    access_token: str
    refresh_token: str


@dataclass(config=config)
class KoboTokenAndUserResponse:
    token_type: TokenType
    access_token: str
    refresh_token: str
    user_key: UUID
    tracking_id: str
