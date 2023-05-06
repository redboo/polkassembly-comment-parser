import logging

import requests


def parse_posts(url: str, topic_type: str, count_posts: int, is_on: str, session: requests.Session) -> list[str]:
    """
    Получает список идентификаторов постов из API Polkassembly для указанной темы.

    Аргументы:
    - `url` (str): URL-адрес API Polkassembly.
    - `topic_type` (str): Тип темы (например, "referendum" или "motion").
    - `count_posts` (int): Количество постов для получения.
    - `is_on` (str): Тип предложения (например, "on" или "off").
    - `session` (requests.Session): Объект сессии для выполнения HTTP-запросов.

    Возвращает:
    `list[str]`: Список идентификаторов постов.
    """
    logging.info(f"Парсинг постов для темы [{topic_type}]")

    posts_url = f"https://api.polkassembly.io/api/v1/listing/{is_on}-chain-posts"
    params = {"page": 1, "listingLimit": count_posts, "proposalType": topic_type}
    try:
        response = session.get(posts_url, params=params, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise Exception(f"Не удалось выполнить запрос к URL: {url}") from e

    posts = response.json()["posts"]

    return [post["post_id"] for post in posts]
