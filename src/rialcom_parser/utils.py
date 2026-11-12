from rialcom_parser.models import InternetTvTariff


def format_tv_tariff_title(tariffs: list[InternetTvTariff], is_house: bool) -> None:
    for tariff in tariffs:
        title = tariff.title

        if is_house:
            title += "_ч"

        tariff.title = f"{tariff.channels_pack} + {title}"


def copy_channels_by_pack_name(source_tariffs: list[InternetTvTariff], target_tariffs: list[InternetTvTariff]) -> None:
    tv_packs = {}

    for tariff in source_tariffs:
        tv_packs[tariff.channels_pack.lower()] = tariff.channels_count

    for tariff in target_tariffs:
        tv_pack = tariff.channels_pack.lower()

        if tv_pack in tv_packs:
            tariff.channels_count = tv_packs[tv_pack]