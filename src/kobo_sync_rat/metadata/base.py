from abc import ABC, abstractmethod
from typing import IO

from kobo_sync_rat.source.source import EbookMetadata


class IncompatibleEbookFormat(Exception):
    pass


class MetadataReader(ABC):
    @abstractmethod
    def read_metadata(self, filename: str) -> EbookMetadata:
        pass

    @abstractmethod
    def read_thumbnail(self, filename: str) -> IO[bytes]:
        pass
