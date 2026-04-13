from datetime import date
from typing import IO, Literal, Mapping, Optional, Sequence
from uuid import UUID
from zipfile import BadZipFile, ZipFile

from lxml.etree import _Element as Element
from lxml.etree import fromstring

from kobo_sync_rat.metadata.base import IncompatibleEbookFormat, MetadataReader
from kobo_sync_rat.source.source import (
    EbookAuthor,
    EbookFormat,
    EbookLanguage,
    EbookMetadata,
    EbookSeries,
)

DEFAULT_LANGUAGE_CODE = "en"

OPF_NS_MAP = {
    "opf": "http://www.idpf.org/2007/opf",
    "dc": "http://purl.org/dc/elements/1.1/",
}

OD_NS_MAP = {"n": "urn:oasis:names:tc:opendocument:xmlns:container"}


class Epub2MetadataReader(MetadataReader):
    def _query_string(
        self,
        element: Element,
        query_path: str,
        namespaces: Optional[Mapping[str, str]] = None,
        default: Optional[str] = None,
    ) -> Optional[str]:
        value = element.xpath(query_path, namespaces=namespaces)

        if isinstance(value, Sequence) and len(value) > 0:
            value = value[0]

        if not isinstance(value, str):
            return default

        return value

    def _query_number(
        self,
        element: Element,
        query_path: str,
        namespaces: Optional[Mapping[str, str]] = None,
        default: Optional[str] = None,
    ) -> Optional[float | int]:
        value = self._query_string(element, query_path, namespaces, default)

        if value is None:
            return None

        return float(value)

    def _query_date(
        self,
        element: Element,
        query_path: str,
        namespaces: Optional[Mapping[str, str]] = None,
        default: Optional[str] = None,
    ) -> Optional[date]:
        value = self._parse_string(element, query_path, namespaces, default)

        if value is None:
            return None

        return date.fromisoformat(value)

    def _parse_string(
        self,
        element: Element,
        query_path: str,
        namespaces: Optional[Mapping[str, str]] = None,
        default: Optional[str] = None,
    ) -> str:
        value = self._query_string(element, query_path, namespaces, default)
        if value is None:
            raise Exception("not a string at path")
        return value

    def _parse_string_list(
        self,
        element: Element,
        query_path: str,
        namespaces: Optional[Mapping[str, str]] = None,
        default: Optional[Sequence[str]] = None,
    ) -> Sequence[str]:
        value = element.xpath(query_path, namespaces=namespaces)

        if not isinstance(value, Sequence):
            return default if default is not None else []

        return [v for v in value if isinstance(v, str)]

    def _get_opf_element(self, zip_file: ZipFile) -> Element:
        with zip_file.open("META-INF/container.xml", "r") as container_file:
            container_tree = fromstring(container_file.read())
            opf_path = self._parse_string(
                container_tree,
                "n:rootfiles/n:rootfile/@full-path",
                namespaces=OD_NS_MAP,
            )

            # Maybe filter on media-type == "application/oebps-package+xml"

        with zip_file.open(opf_path, "r") as opf_file:
            opf_content = opf_file.read()
            return fromstring(opf_content)

    def _query_identifier(
        self,
        element: Element,
        selector_scheme: Literal["ISBN"] | Literal["AMAZON"] | Literal["CALIBRE"],
    ) -> Optional[str]:
        identifiers: Sequence[Element] | None = element.xpath(
            "opf:metadata/dc:identifier", namespaces=OPF_NS_MAP
        )

        if not identifiers:
            return None

        # Clean up identifiers
        for identifier in identifiers:
            matching_schemes = identifier.xpath("./@opf:scheme", namespaces=OPF_NS_MAP)
            scheme = (
                str(matching_schemes[0]).upper() if len(matching_schemes) > 0 else None
            )

            value = str(identifier.text)

            if value.lower().startswith("urn:"):
                parts = value.split(":", 3)
                if scheme is None:
                    scheme = parts[1].upper()

                value = parts[2]

            if value.lower().startswith("isbn:"):
                if scheme is None:
                    scheme = "ISBN"
                value = value[5:]

            if scheme == selector_scheme:
                return value

        return None

    def _parse_series(self, opf: Element) -> Optional[EbookSeries]:
        series_name = self._query_string(
            opf,
            'opf:metadata/opf:meta[@name="calibre:series"]/@content',
            namespaces=OPF_NS_MAP,
        )
        series_index = self._query_number(
            opf,
            'opf:metadata/opf:meta[@name="calibre:series_index"]/@content',
            namespaces=OPF_NS_MAP,
        )

        if series_name and series_index:
            return EbookSeries(name=series_name, index=series_index)

        return None

    def _parse_title(self, opf: Element) -> str:
        return self._parse_string(
            opf, "opf:metadata/dc:title/text()", namespaces=OPF_NS_MAP, default=""
        )

    def _parse_description(self, opf: Element) -> str:
        # TODO: Strip HTML
        return self._parse_string(
            opf, "opf:metadata/dc:description/text()", namespaces=OPF_NS_MAP, default=""
        )

    def _parse_tags(self, opf: Element) -> Sequence[str]:
        return self._parse_string_list(
            opf, "opf:metadata/dc:subject/text()", namespaces=OPF_NS_MAP
        )

    def _parse_authors(self, opf: Element) -> Sequence[EbookAuthor]:
        values = self._parse_string_list(
            opf,
            'opf:metadata/dc:creator[@opf:role="aut" or not(@opf:role)]/text()',
            namespaces=OPF_NS_MAP,
        )

        return [EbookAuthor(v) for v in values]

    def _parse_language(self, opf: Element) -> EbookLanguage:
        language_code = self._parse_string(
            opf,
            "opf:metadata/dc:language/text()",
            namespaces=OPF_NS_MAP,
            default=DEFAULT_LANGUAGE_CODE,
        )

        return EbookLanguage(code=language_code)

    def _parse_uuid_id(self, opf: Element) -> UUID:
        urn_uuid = self._parse_string(
            opf,
            "opf:metadata/dc:identifier[@id='uuid_id']/text()",
            namespaces=OPF_NS_MAP,
            default=DEFAULT_LANGUAGE_CODE,
        )

        return UUID(hex=urn_uuid.replace(r"^urn:uuid:", ""))

    def _parse_publisher(self, opf: Element) -> str | None:
        return self._query_string(
            opf,
            "opf:metadata/dc:publisher/text()",
            namespaces=OPF_NS_MAP,
        )

    def _parse_publication_date(self, opf: Element) -> date | None:
        return self._query_date(
            opf,
            "opf:metadata/dc:date/text()",
            namespaces=OPF_NS_MAP,
        )

    def _parse_isbn(self, opf: Element) -> str | None:
        return self._query_identifier(opf, "ISBN")

    def _parse_metadata(self, opf: Element) -> EbookMetadata:
        return EbookMetadata(
            id=self._parse_uuid_id(opf),
            title=self._parse_title(opf),
            description=self._parse_description(opf),
            authors=self._parse_authors(opf),
            tags=self._parse_tags(opf),
            series=self._parse_series(opf),
            language=self._parse_language(opf),
            format=EbookFormat.EPUB,
            publisher=self._parse_publisher(opf),
            publication_date=self._parse_publication_date(opf),
            isbn=self._parse_isbn(opf),
        )

    def read_metadata(self, filename: str | IO[bytes]) -> EbookMetadata:
        try:
            with ZipFile(filename) as z:
                opf_element = self._get_opf_element(z)

                return self._parse_metadata(opf_element)
        except BadZipFile:
            raise IncompatibleEbookFormat()

    def read_thumbnail(self, filename: str):
        raise NotImplementedError()
