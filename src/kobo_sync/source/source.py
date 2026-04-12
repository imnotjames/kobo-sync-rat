from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import date, datetime
from enum import Enum
from typing import IO, Generator, Sequence
from uuid import UUID


class EbookEventType(Enum):
    CREATED = "CREATED"
    MODIFIED = "MODIFIED"


@dataclass
class EbookAuthor:
    name: str


@dataclass
class EbookLanguage:
    code: str


class EbookFormat(Enum):
    EPUB = "epub"
    KEPUB = "kepub"
    PDF = "pdf"
    CBR = "cbr"


@dataclass
class EbookSeries:
    name: str

    index: float | int


@dataclass
class EbookMetadata:
    id: UUID

    title: str

    description: str

    publisher: str | None

    publication_date: date | None

    authors: Sequence[EbookAuthor]

    isbn: str | None

    tags: Sequence[str]

    series: EbookSeries | None

    language: EbookLanguage

    format: EbookFormat


@dataclass
class EbookEvent:
    event_id: UUID

    event_type: EbookEventType

    timestamp: datetime

    metadata: EbookMetadata


def uuid6(nanoseconds: int, node: int, clock_seq: int) -> UUID:
    # 0x01b21dd213814000 is the number of 100-ns intervals between the
    # UUID epoch 1582-10-15 00:00:00 and the Unix epoch 1970-01-01 00:00:00.
    timestamp = nanoseconds // 100 + 0x01B21DD213814000

    time_hi_and_mid = (timestamp >> 12) & 0xFFFF_FFFF_FFFF
    time_lo = timestamp & 0x0FFF  # keep 12 bits and clear version bits
    clock_s = clock_seq & 0x3FFF  # keep 14 bits and clear variant bits

    # --- 32 + 16 ---   -- 4 --   -- 12 --  -- 2 --   -- 14 ---    48
    # time_hi_and_mid | version | time_lo | variant | clock_seq | node
    int_uuid_6 = time_hi_and_mid << 80
    int_uuid_6 |= time_lo << 64
    int_uuid_6 |= clock_s << 48
    int_uuid_6 |= node & 0xFFFF_FFFF_FFFF
    # by construction, the variant and version bits are already cleared
    int_uuid_6 |= (6 << 76) | (0x8000 << 48)

    return UUID(int=int_uuid_6)


class EbookSource(ABC):
    @abstractmethod
    def get_events(
        self, after_event_id: UUID | None = None
    ) -> Generator[EbookEvent, None, None]:
        raise NotImplementedError()

    @abstractmethod
    def get_book_metadata(self, book_id: UUID) -> EbookMetadata:
        raise NotImplementedError()

    @abstractmethod
    def get_cover_stream(self, book_id: UUID) -> IO[bytes]:
        raise NotImplementedError()

    @abstractmethod
    def get_content_stream(self, book_id: UUID) -> IO[bytes]:
        raise NotImplementedError()
