from __future__ import annotations

from dataclasses import dataclass

from rialcom_parser.config import CONNECTION_SPEED_PATTERN, NUMBER_PATTERN, TV_PACK_TITLE_PATTERN, \
    CHANNELS_COUNT_PATTERN


def normalize_tv_pack_title(title: str) -> str:
    return " ".join(title.replace("+", " + ").split())


@dataclass
class BaseTable:
    header: list[str] | None


@dataclass
class Table(BaseTable):
    body: list[list[str]] | None


@dataclass
class InternetTariff:
    title: str
    price: int
    speed_mbps: float


@dataclass
class InternetTvTariff(InternetTariff):
    channels_pack: str
    channels_count: int | None


@dataclass
class InternetTariffTable(BaseTable):
    """Таблица для тарифов \"Интернет\". Не совместима с тарифами \"Интернет + Интерактивное ТВ\"."""

    tariffs: list[InternetTariff]

    @classmethod
    def create_from_table(cls, table: Table) -> InternetTariffTable | None:
        if table.body is None:
            return None

        tariffs = []

        for row in table.body:
            match row:
                case [title, raw_price, _, raw_speed]:
                    speed_search = CONNECTION_SPEED_PATTERN.search(raw_speed)
                    price_search = NUMBER_PATTERN.search(raw_price)

                    if not speed_search:
                        raise ValueError(f"Invalid tariff speed: {row}")

                    if not price_search:
                        raise ValueError(f"Invalid tariff price: {row}")

                    speed_kbps = speed_search.group("speed")
                    price = price_search.group("number")

                    tariffs.append(
                        InternetTariff(
                            title=title.replace("*", ""),
                            price=int(price),
                            speed_mbps=float(speed_kbps) / 1000.0,
                        )
                    )
                case _:
                    raise ValueError(f"Invalid tariff data: {row}")

        return InternetTariffTable(header=table.header, tariffs=tariffs)


@dataclass
class InternetTvTariffTable(BaseTable):
    """Таблица для тарифов \"Интернет + Интерактивное ТВ\". Не совместима с тарифами \"Интернет\"."""

    tariffs: list[InternetTvTariff]

    @classmethod
    def create_from_table(cls, table: Table) -> InternetTvTariffTable | None:
        if table.header is None or table.body is None:
            return None

        tariffs = []

        tariff_titles = [title.replace("*", "") for title in
                         table.header[1:]]  # Обрезаю пустую ячейку под столбец ТВ пакетов

        for row in table.body:
            match row:
                case [raw_pack, *tariff_prices]:
                    pack_title_search = TV_PACK_TITLE_PATTERN.search(raw_pack)

                    if not pack_title_search:
                        raise ValueError(f"Invalid tariff pack: {row}")

                    pack_title = normalize_tv_pack_title(pack_title_search.group("title"))

                    channels_count_search = CHANNELS_COUNT_PATTERN.search(raw_pack)
                    channels_count = None

                    if channels_count_search:
                        channels_count = int(channels_count_search.group("count"))

                    for index, price in enumerate(tariff_prices):
                        tariff_title = tariff_titles[index]

                        speed_mbps = NUMBER_PATTERN.search(tariff_title).group("number")

                        tariff = InternetTvTariff(
                            title=tariff_titles[index],
                            price=int(price),
                            channels_pack=pack_title,
                            channels_count=channels_count,
                            speed_mbps=float(speed_mbps),
                        )

                        tariffs.append(tariff)

        return InternetTvTariffTable(header=table.header, tariffs=tariffs)
