from __future__ import annotations

import json
import logging
from typing import Any

import requests
from bs4 import BeautifulSoup as bs


def parse_topics(url: str, session: requests.Session, limit: int | None = None) -> dict[Any, Any]:
    """
    Получает список топиков для заданного URL.

    Аргументы:
    - `url` (str): URL, для которого необходимо получить список топиков
    - `session` (requests.Session): объект сессии requests для отправки запросов
    - `limit` (int|None): максимальное количество топиков, которые нужно вернуть. По умолчанию None.

    Возвращает:
    `dict`: словарь, в котором ключами являются названия топиков, а значениями - количество постов в каждом топике.
    Если не удалось получить список топиков, возвращает пустой словарь."""
    logging.info(f"Получение топиков для URL: {url}")
    try:
        response = session.get(url, timeout=20)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        logging.error(f"Не удалось выполнить запрос к URL: {url}: {e}")
        return {}

    soup = bs(response.text, "lxml")
    categories = soup.find("script", {"id": "__NEXT_DATA__"})
    if categories:
        data = json.loads(categories.text)
        try:
            topics = {
                title: topic["data"]["count"]
                for title, topic in data["props"]["pageProps"]["latestPosts"].items()
                if isinstance(topic, dict) and topic["data"]["count"] != 0 and title != "all"
            }
        except KeyError as e:
            logging.warning(f"Не удалось получить список топиков для URL: {url} KeyError: {e}")
            return {}

        if limit:
            topics = dict(list(topics.items())[:limit])
        return topics

    logging.warning(f"Не удалось получить список топиков для URL: {url}")
    return {}
