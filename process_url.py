from __future__ import annotations

import csv
import logging
import os
from datetime import datetime

import requests

from get_post_data import get_post_and_comments_data
from parse_posts import parse_posts
from parse_topics import parse_topics


def process_url(
    url: str,
    network: str,
    file_pathname: str,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
) -> bool:
    """
    Запускает парсинг постов и комментариев с заданного URL-адреса и сохраняет результат в CSV-файл.

    Аргументы:
    - `url (str)`: URL-адрес, с которого нужно начать парсинг.
    - `network (str)`: название сети, для которой выполняется парсинг.
    - `file_pathname (str)`: путь к файлу, в который будут сохранены результаты парсинга.
    - `start_date (datetime, опционально)`: ограничение даты начала периода парсинга, только посты, созданные после
      этой даты, будут включены в результат. Если не указана, то не будет использоваться.
    - `end_date (datetime, опционально)`: ограничение даты конца периода парсинга, только посты, созданные до этой
      даты, будут включены в результат. Если не указана, то не будет использоваться.

    Возвращает:
    `bool`: `True`, если были получены данные и сохранены в файл, `False` в противном случае.

    Исключения:
    - Exception: если не удалось выполнить запрос к URL.
    """
    has_data = False
    with requests.Session() as session:
        session.headers.update({"x-network": network, "Accept": "application/json"})
        topics = parse_topics(url, session=session)
        if not topics:
            return has_data
        with open(file_pathname, mode="a", newline="") as file:
            writer = csv.writer(file, delimiter=",", quotechar='"', quoting=csv.QUOTE_MINIMAL)
            if not os.path.exists(file_pathname) or os.path.getsize(file_pathname) == 0:
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
                    if rows:
                        has_data = True
                    for row in rows:
                        writer.writerow(row)

    return has_data
