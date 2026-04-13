from typing import Mapping

from pydantic.dataclasses import dataclass

from kobo_sync_rat.models.dataclass import config


@dataclass(config=config)
class KoboResourceContainer:
    resources: Mapping[str, str | Mapping[str, str]]
