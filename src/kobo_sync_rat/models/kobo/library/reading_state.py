from dataclasses import field
from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic.dataclasses import dataclass

from kobo_sync.models.dataclass import config


class KoboReadingStatus(Enum):
    READY_TO_READ = "ReadyToRead"
    READING = "Reading"
    FINISHED = "Finished"


@dataclass(config=config)
class KoboReadingStatusInfo:
    last_modified: datetime = field(default_factory=lambda: datetime.now())
    status: KoboReadingStatus = KoboReadingStatus.READY_TO_READ
    times_started_reading: int = 0
    last_time_started_reading: Optional[datetime] = None
    last_time_finished: Optional[datetime] = None


class KoboReadingBookmarkLocationType(Enum):
    KOBOSPAN = "KoboSpan"


@dataclass(config=config)
class KoboReadingBookmarkLocation:
    value: str
    type: KoboReadingBookmarkLocationType
    source: str = ""


@dataclass(config=config)
class KoboReadingBookmark:
    last_modified: datetime = field(default_factory=lambda: datetime.now())
    progress_percent: int = field(default=0)
    content_source_progress_percent: int = field(default=0)
    location: KoboReadingBookmarkLocation = field(
        default_factory=lambda: KoboReadingBookmarkLocation(
            type=KoboReadingBookmarkLocationType.KOBOSPAN, value="kobo.1.1"
        )
    )


@dataclass(config=config)
class KoboReadingStatistics:
    last_modified: datetime = field(default_factory=lambda: datetime.now())

    spent_reading_minutes: int = field(default=0)

    remaining_time_minutes: int = field(default=0)


@dataclass(config=config)
class KoboReadingState:
    entitlement_id: UUID

    created: datetime

    priority_timestamp: datetime | None = None

    last_modified: datetime = field(default_factory=lambda: datetime.now())

    status_info: KoboReadingStatusInfo = field(
        default_factory=lambda: KoboReadingStatusInfo()
    )

    statistics: KoboReadingStatistics = field(
        default_factory=lambda: KoboReadingStatistics()
    )

    current_bookmark: KoboReadingBookmark = field(
        default_factory=lambda: KoboReadingBookmark()
    )
