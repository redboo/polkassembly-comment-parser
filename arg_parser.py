import argparse


def parse_args() -> argparse.Namespace:
    """
    Парсит аргументы командной строки для скрипта парсера комментариев с сайтов.
    Аргументы:

    - `--url (str)`: URL-адрес сайта для парсинга. Может быть использован только один из двух аргументов: `--url` или `--urls-file`.
    - `--urls-file (str)`: путь к файлу со списком URL-адресов для парсинга. Может быть использован только один из двух аргументов: `--url` или `--urls-file`. По умолчанию установлено значение `urls.txt`.
    - `--interval (int)`: интервал в секундах между автоматическими запусками парсинга. По умолчанию не установлен.
    - `--start (str)`: дата начала периода парсинга в формате ГГГГММДД. По умолчанию не установлен.
    - `--end (str)`: дата окончания периода парсинга в формате ГГГГММДД. По умолчанию не установлен.
    - `--log (str)`: уровень логирования. Возможные значения: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`. По умолчанию установлено значение `WARNING`.

    Возвращает:
    `argparse.Namespace`: пространство имен с аргументами командной строки, которые могут быть использованы в скрипте парсера комментариев с сайтов.
    """
    parser = argparse.ArgumentParser(description="Парсер комментариев с сайтов")
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--url",
        default=None,
        type=str,
        help="Установите URL-адрес для парсинга",
    )
    group.add_argument(
        "--urls-file",
        default="urls.txt",
        type=str,
        help="Путь к файлу со списком URL-адресов для парсинга",
    )
    parser.add_argument(
        "--interval",
        default=None,
        type=int,
        help="Установите интервал в секундах для автоматического парсинга (по умолчанию не установлен)",
    )
    parser.add_argument(
        "--start",
        default=None,
        type=str,
        help="Установите дату начала в формате ГГГГММДД (по умолчанию не установлен)",
    )
    parser.add_argument(
        "--end",
        default=None,
        type=str,
        help="Установите дату окончания в формате ГГГГММДД (по умолчанию не установлен)",
    )
    log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    parser.add_argument(
        "--log",
        default="WARNING",
        choices=log_levels,
        help="Установите уровень логирования (по умолчанию: WARNING)",
    )

    return parser.parse_args()
