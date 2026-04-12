import os
from functools import cache

from kobo_sync.metadata.epub2 import Epub2MetadataReader
from kobo_sync.source.filesystem import FilesystemSource
from kobo_sync.source.grimmory import GrimmorySource
from kobo_sync.source.source import EbookSource


@cache
def get_ebook_source() -> EbookSource:
    # TODO: Eventually via app config somehow?

    match os.environ.get("SYNC_SOURCE", "filesystem").lower():
        case "grimmory":
            return GrimmorySource(
                os.environ["GRIMMORY_BASE_URL"],
                os.environ["GRIMMORY_USERNAME"],
                os.environ["GRIMMORY_PASSWORD"],
            )

        case "filesystem":
            return FilesystemSource(
                os.environ.get("SYNC_SOURCE_DIRECTORY", "./books/"),
                metadata_readers=[Epub2MetadataReader()],
            )

    raise RuntimeError("unknown source")
