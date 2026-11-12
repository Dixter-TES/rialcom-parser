import re

TARGET_URL = "https://www.rialcom.ru/internet_tariffs/"

FLAT_TARIFFS_BLOCK_ID = "collapse1"
PRIVATE_HOUSE_TARIFFS_BLOCK_ID = "collapse2"

INTERNET_TARIFFS_TABLE_INDEX = 0
INTERNET_TV_TARIFFS_TABLE_INDEX = 1

EXCEL_HEADER = ["Название тарифа", "Количество каналов", "Скорость доступа", "Абонентская плата"]

CONNECTION_SPEED_PATTERN = re.compile(r"до\s*(?P<speed>\d+)\s*кб")
CHANNELS_COUNT_PATTERN = re.compile(r"\((?P<count>\d{2,4})\s*канал\w*\)")
NUMBER_PATTERN = re.compile(r"(?P<number>\d+)")
TV_PACK_TITLE_PATTERN = re.compile(r"(?P<title>[\s\w+]+)\s*\(?")
