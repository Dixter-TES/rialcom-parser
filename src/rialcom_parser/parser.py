from selectolax.lexbor import LexborHTMLParser, LexborNode

from rialcom_parser.config import INTERNET_TARIFFS_TABLE_INDEX, INTERNET_TV_TARIFFS_TABLE_INDEX
from rialcom_parser.models import Table, InternetTariffTable, InternetTvTariffTable


def _parse_table_header(table: LexborNode) -> list | None:
    header_row = table.css_first('thead > tr')

    if header_row is None:
        return None

    return [
        col.text(strip=True)
        for col in header_row.css("th")
    ]


def _parse_table_body(table: LexborNode) -> list | None:
    body_rows = table.css('tbody > tr')

    if not body_rows:
        return None

    return [
        [col.text(strip=True) for col in row.css("td")]
        for row in body_rows
    ]


def _parse_table(node: LexborNode, check_integrity=True) -> Table:
    header = _parse_table_header(node)
    body = _parse_table_body(node)

    if check_integrity:
        if header is None:
            raise ValueError("Header not found in table")

        if body is None:
            raise ValueError("Body not found in table")

    return Table(header=header, body=body)


def _format_id(_id: str) -> str:
    return _id if _id.startswith("#") else f"#{_id}"


class RialcomParser:
    def __init__(self, document: str) -> None:
        self.tree = LexborHTMLParser(document)

    def get_internet_tariffs_table(self, block_id: str) -> InternetTariffTable | None:
        table = self._get_table_by_index(block_id, INTERNET_TARIFFS_TABLE_INDEX)
        return InternetTariffTable.create_from_table(table) if table else None

    def get_internet_tv_tariffs_table(self, block_id: str) -> InternetTvTariffTable | None:
        table = self._get_table_by_index(block_id, INTERNET_TV_TARIFFS_TABLE_INDEX)
        return InternetTvTariffTable.create_from_table(table) if table else None

    def get_tables(self, block_id: str) -> list[Table]:
        block = self._get_block_by_id(block_id)

        table_nodes = block.css("table")

        return [_parse_table(node) for node in table_nodes]

    def _get_table_by_index(self, block_id: str, index: int) -> Table | None:
        tables = self.get_tables(_format_id(block_id))

        if not tables or len(tables) < index + 1:
            return None

        return tables[index]

    def _get_block_by_id(self, block_id: str) -> LexborNode:
        node = self.tree.css_first(_format_id(block_id))

        if not node:
            raise ValueError(f"Block with id '{block_id}' not found")

        return node
