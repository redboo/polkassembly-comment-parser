import logging
from datetime import datetime
from typing import Any

import requests

from constants import URL_ENDPOINTS


def get_post_and_comments_data(
    url: str,
    is_on: str,
    proposal_type: str,
    post_id: int | str,
    session: requests.Session,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
) -> list[Any]:
    """
    Функция get_post_and_comments_data получает данные поста и комментариев по указанным параметрам.

    Аргументы:

    - `url (str)`: Базовый URL адрес сайта Polkassembly.
    - `is_on (str)`: Тип предложения (например, `"on" `или `"off"`).
    - `proposal_type (str)`: Тип поста (например, `"proposal"` или `"referendum"`).
    - `post_id (int|str)`: ID поста.
    - `session (requests.Session)`: Сессия для запросов к API.
    - `start_date (datetime, опционально)`: Дата начала периода, за который нужно получить данные. По умолчанию None.
    - `end_date (datetime, опционально)`: Дата конца периода, за который нужно получить данные. По умолчанию None.

    Возвращает:
    `list`: Список данных для записи в CSV-файл."""
    post_url = f"https://api.polkassembly.io/api/v1/posts/{is_on}-chain-post"
    params = {"postId": post_id, "proposalType": proposal_type}
    rows = []

    try:
        response_post = session.get(post_url, params=params, timeout=20)
        response_post.raise_for_status()
        post_data = response_post.json()

        post_id = post_data["post_id"] if post_data.get("post_id") else post_data.get("hash", "None")
        post_link = f"{url}{URL_ENDPOINTS.get(proposal_type, '')}/{post_id}"
        post_type = post_data.get("type", proposal_type.title())
        post_title = str(post_data.get("title", "Untitled")).strip() or "Untitled"
        post_comments = post_data.get("comments", [])
        post_date = datetime.strptime(post_data["created_at"], "%Y-%m-%dT%H:%M:%S.%fZ")

        if post_comments:
            comments = []
            for comment in post_comments:
                comment_date = datetime.strptime(comment["created_at"], "%Y-%m-%dT%H:%M:%S.%fZ")
                if (start_date and comment_date < start_date) or (end_date and comment_date > end_date):
                    continue
                comments.append(get_row_data(post_data, post_type, post_link, comment))
            if comments:
                rows.extend(comments)
                logging.info(f"Сохранено {len(comments)} комментариев для поста [{post_title}]: {post_link}")
        else:
            if (start_date and post_date < start_date) or (end_date and post_date > end_date):
                return rows
            rows.append(get_row_data(post_data, post_type, post_link))
            logging.info(f"Сохранен пост [{post_title}]: {post_link}")

    except requests.exceptions.ReadTimeout:
        logging.warning(f"Таймаут при запросе к {post_url} {params} {url}")
    except requests.exceptions.RequestException:
        logging.exception(f"Ошибка при получении данных поста: {post_id}")

    return rows


def get_row_data(post_data: dict, post_type: str, post_link: str, comment_data: dict | None = None) -> list[Any]:
    """
    Возвращает список данных для записи в CSV-файл.

    Аргументы:
    - `post_data(dict)` : Словарь данных поста.
    - `post_type(str)` : Тип поста (например, "proposal" или "referendum").
    - `post_link (str)`: Ссылка на пост.
    - `comment_data (dict | None)`: Словарь данных комментария, если есть.

    Возвращает:
    `list`: Список данных для записи в CSV-файл."""
    return [
        post_type,
        post_data["topic"]["name"],
        post_data["created_at"][:19].replace("T", " "),
        post_data.get("user_id"),
        post_data.get("username"),
        str(post_data.get("title", "Untitled")).strip() or "Untitled",
        post_data.get("content", "").replace("\n", " "),
        post_data.get("status"),
        post_data["post_reactions"]["👍"]["count"],
        post_data["post_reactions"]["👎"]["count"],
        comment_data["content"].replace("\n", " ") if comment_data else "",
        comment_data["username"] if comment_data else "",
        comment_data["created_at"][:19].replace("T", " ") if comment_data else "",
        comment_data["comment_reactions"]["👍"]["count"] if comment_data else "",
        comment_data["comment_reactions"]["👎"]["count"] if comment_data else "",
        post_link,
    ]
