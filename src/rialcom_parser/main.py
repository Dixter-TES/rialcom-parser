import argparse
import os
import logging

import httpx

from rialcom_parser.config import TARGET_URL, FLAT_TARIFFS_BLOCK_ID, PRIVATE_HOUSE_TARIFFS_BLOCK_ID
from rialcom_parser.export import export_to_excel
from rialcom_parser.parser import RialcomParser
from rialcom_parser.utils import format_tv_tariff_title, copy_channels_by_pack_name


def _args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", help="Путь для сохранения Excel-файла")
    parser.add_argument("--offline", help="Путь до Html-дампа страницы.")
    return parser.parse_args()


def _get_html(html_path: str | None = None) -> str:
    if html_path is not None:
        if not os.path.exists(html_path):
            raise ValueError("Invalid html path")

        with open(html_path, encoding="utf-8") as f:
            return f.read()
    else:
        resp = httpx.get(TARGET_URL, follow_redirects=True, timeout=10)
        resp.raise_for_status()

        return resp.text


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )

    args = _args()

    if args.output is None or not args.output.endswith(".xlsx"):
        logging.error("Ошибка: не указан или неверный путь для Excel-файла.")
        return

    if args.offline is not None and not args.offline.endswith(".html"):
        logging.error("Ошибка: указан неверный формат HTML-файла.")
        return

    logging.info("Получаю содержимое страницы...")

    try:
        content = _get_html(args.offline)
    except (httpx.HTTPError, OSError, ValueError):
        logging.error("Ошибка получения содержимого страницы", exc_info=True)
        return

    logging.info("Содержимое получено!")

    parser = RialcomParser(content)

    logging.info("Ищу тарифы...")

    try:
        flat_internet_tariffs = parser.get_internet_tariffs_table(FLAT_TARIFFS_BLOCK_ID)
        flat_internet_tv_tariffs = parser.get_internet_tv_tariffs_table(FLAT_TARIFFS_BLOCK_ID)

        if flat_internet_tariffs is None or flat_internet_tv_tariffs is None:
            logging.error("Не удалось получить все тарифы из блока «Многоквартирные дома»")
            return
    except ValueError:
        logging.error(f"Ошибка при получении тарифов из блока «Многоквартирные дома»", exc_info=True)
        return

    logging.info("Получены тарифы блока «Многоквартирные дома». Продолжаю...")

    try:
        private_house_internet_tariffs = parser.get_internet_tariffs_table(PRIVATE_HOUSE_TARIFFS_BLOCK_ID)
        private_house_internet_tv_tariffs = parser.get_internet_tv_tariffs_table(PRIVATE_HOUSE_TARIFFS_BLOCK_ID)

        if private_house_internet_tariffs is None or private_house_internet_tv_tariffs is None:
            logging.error("Не удалось получить все тарифы из блока «Частные дома и коттеджи»")
            return
    except ValueError:
        logging.error(f"Ошибка при получении тарифов из блока «Частные дома и коттеджи»", exc_info=True)
        return

    logging.info("Получены тарифы блока «Частные дома и коттеджи»")

    logging.info("Форматирую заголовки и подсчитываю каналы...")
    format_tv_tariff_title(flat_internet_tv_tariffs.tariffs, is_house=False)
    format_tv_tariff_title(private_house_internet_tv_tariffs.tariffs, is_house=True)
    copy_channels_by_pack_name(
        flat_internet_tv_tariffs.tariffs,
        private_house_internet_tv_tariffs.tariffs,
    )

    tariffs = [
        *flat_internet_tariffs.tariffs,
        *flat_internet_tv_tariffs.tariffs,
        *private_house_internet_tariffs.tariffs,
        *private_house_internet_tv_tariffs.tariffs,
    ]

    logging.info(f"Всего получено тарифов: {len(tariffs)}")
    logging.info(f"Экспортирую в Excel-файл: {args.output}")

    try:
        success = export_to_excel(args.output, tariffs)

        if success:
            logging.info(f"Экспорт успешно выполнен!")
        else:
            logging.error(f"Не удалось выполнить экспорт в Excel-файл")
    except Exception:
        logging.error(f"Непредвиденная ошибка экспорта", exc_info=True)
        return


if __name__ == "__main__":
    main()
