import csv
import logging
import os
from datetime import datetime
from urllib.parse import urlparse

import requests

from get_post_data import get_post_and_comments_data
from parse_posts import parse_posts
from parse_topics import parse_topics

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def process_url(url: str, downloads_dir, start_date: datetime | None = None, end_date: datetime | None = None) -> None:
    """
    Запускает парсинг постов и комментариев с заданного URL-адреса и сохраняет результат в CSV-файл.

    Аргументы:
    - `url` (str): URL-адрес, с которого нужно начать парсинг.
    - `downloads_dir` (str): относительный путь к директории для сохранения файла с результатами.
    - `start_date` (datetime | None, опционально): ограничение даты начала периода парсинга, только посты, созданные после
      этой даты, будут включены в результат. Если не указана, то не будет использоваться.
    - `end_date` (datetime | None, опционально): ограничение даты конца периода парсинга, только посты, созданные до
      этой даты, будут включены в результат. Если не указана, то не будет использоваться.

    Возвращает:
    `None`: функция ничего не возвращает, а сохраняет результаты в CSV-файл.

    Исключения:
    - Exception: если не удалось выполнить запрос к URL.

    """
    url = url.strip()
    network = urlparse(url).netloc.split(".")[0]
    logging.info(f"Парсинг запущен для URL: {url}")
    filename = f"{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}_{network}.csv"
    file_pathname = os.path.join(BASE_DIR, downloads_dir, filename)

    with requests.Session() as session:
        session.headers.update({"x-network": network, "Accept": "application/json"})
        topics = parse_topics(url, session=session)
        if not topics:
            return
        with open(file_pathname, mode="w", newline="") as file:
            writer = csv.writer(file, delimiter=",", quotechar='"', quoting=csv.QUOTE_MINIMAL)
            writer.writerow(
                [
                    "Post type",
                    "Topic",
                    "Created at",
                    "User ID",
                    "Username",
                    "Post title",
                    "Post content",
                    "Status",
                    "Likes",
                    "Dislikes",
                    "Comment content",
                    "Comment username",
                    "Comment created at",
                    "Comment likes",
                    "Comment dislikes",
                    "Post link",
                ]
            )
            for topic_type, count_posts in topics.items():
                is_on = "off" if topic_type in ["discussions", "grants"] else "on"
                posts = parse_posts(
                    url=url,
                    topic_type=topic_type,
                    count_posts=count_posts,
                    is_on=is_on,
                    session=session,
                )
                logging.info(f"[{topic_type}] Количество постов: {count_posts}")
                for post_id in posts:
                    rows = get_post_and_comments_data(
                        url=url,
                        is_on=is_on,
                        proposal_type=topic_type,
                        post_id=post_id,
                        session=session,
                        start_date=start_date,
                        end_date=end_date,
                    )
                    for row in rows:
                        writer.writerow(row)

    logging.info(f"Парсинг завершен для URL: {url} Результат сохранен в {file_pathname}")
