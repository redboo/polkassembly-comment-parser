import logging
import os
import time
from datetime import datetime
from urllib.parse import urlparse

from arg_parser import parse_args
from logging_utils import setup_logging
from process_url import process_url

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def fetch_urls_from_file(file_path: str) -> list[str]:
    """
    Функция выдает из файла список URL-адресов, предварительно удаляя все комментарии и пустые строки.

    :param `file_path` (str): путь к файлу со списком URL-адресов.
    :return: `list[str]` список URL-адресов.
    """
    with open(file_path, "r") as urls_file:
        return [url.strip() for url in urls_file if url.strip() and not url.startswith("#")]


def run(one_file=True) -> None:
    args = parse_args()
    setup_logging(args.log)

    start_date = datetime.strptime(args.start, "%Y%m%d") if args.start else None
    end_date = datetime.strptime(args.end, "%Y%m%d") if args.end else None

    if start_date and end_date and end_date <= start_date:
        logging.error("Дата завершения не может быть меньше даты начала. Завершение программы.")
        return

    while True:
        start_time = time.monotonic()

        urls = [args.url.strip()] if args.url else fetch_urls_from_file(args.urls_file)
        if not urls:
            logging.error("Список URL-адресов пуст. Завершение программы.")
            break

        downloads_dir = (
            os.path.join("downloads", datetime.now().strftime("%Y-%m-%d_%H-%M-%S")) if not one_file else "downloads"
        )
        os.makedirs(downloads_dir, exist_ok=True)

        filename = f"{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}_polkassembly.csv"
        file_pathname = os.path.join(BASE_DIR, downloads_dir, filename)

        written = False
        for url in urls:
            url = url.strip()
            network = urlparse(url).netloc.split(".")[0]
            logging.info(f"Парсинг запущен для URL: {url}")
            if not one_file:
                filename = f"{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}_{network}.csv"
                file_pathname = os.path.join(BASE_DIR, downloads_dir, filename)

            has_data = process_url(url, network, file_pathname, start_date=start_date, end_date=end_date)

            if not has_data:
                logging.info(f"Парсинг завершен для URL: {url} Результатов не найдено")
            else:
                written = True
                logging.info(f"Парсинг завершен для URL: {url} Результат сохранен в {file_pathname}")

        if not written:
            os.remove(file_pathname)

        if not args.interval:
            break

        elapsed_time = max(time.monotonic() - start_time, 0)
        sleep_length = max(args.interval - elapsed_time, 0)
        time.sleep(sleep_length)

    logging.info("Программа завершена.")


if __name__ == "__main__":
    try:
        run()
    except KeyboardInterrupt:
        print("\nПрограмма остановлена пользователем.")
