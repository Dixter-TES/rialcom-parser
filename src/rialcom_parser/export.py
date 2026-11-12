from openpyxl import Workbook
from openpyxl.styles import Font, Border, Side
from openpyxl.worksheet.worksheet import Worksheet

from rialcom_parser.config import EXCEL_HEADER
from rialcom_parser.models import InternetTariff, InternetTvTariff

_FULL_BORDER = Border(
    left=Side(style='thin', color='000000'),
    right=Side(style='thin', color='000000'),
    top=Side(style='thin', color='000000'),
    bottom=Side(style='thin', color='000000'),
)


def _append_header(ws: Worksheet, header: list[str]) -> None:
    for index, header_title in enumerate(header):
        cell = ws.cell(row=1, column=index + 1)

        cell.value = header_title
        cell.font = Font(bold=True)

        cell.border = _FULL_BORDER


def export_to_excel(output_path: str, tariffs: list[InternetTariff]) -> bool:
    wb = Workbook()
    ws = wb.active

    if ws is None:
        return False

    ws.title = "Тарифы"

    _append_header(ws, EXCEL_HEADER)

    for index, tariff in enumerate(tariffs, start=2):
        title_col: str = tariff.title
        channels_count_col: int | None = None
        speed_mbps_col: float = tariff.speed_mbps
        price_col: int = tariff.price

        match tariff:
            case InternetTvTariff(channels_count=channels_count):
                channels_count_col = channels_count

        cols = [title_col, channels_count_col if channels_count_col else "null", speed_mbps_col, price_col]

        for col, value in enumerate(cols, start=1):
            cell = ws.cell(row=index, column=col)

            cell.value = value
            cell.border = _FULL_BORDER

    wb.save(output_path)

    return True
