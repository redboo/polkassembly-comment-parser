import logging


def setup_logging(log_level: str) -> None:
    """
    Устанавливает уровень журналирования логгера и форматирование сообщений.

    Аргументы:
    - `log_level` (str): Уровень журналирования логгера, например, "DEBUG", "INFO", "WARNING", "ERROR" или "CRITICAL".

    Возвращает:
    `None`"""
    logging.basicConfig(level=log_level, format="%(asctime)s %(levelname)s: %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
