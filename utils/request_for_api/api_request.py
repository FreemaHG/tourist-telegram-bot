from config_data.config import RAPID_API_KEY
import requests
from requests import get
import json
from loguru import logger


HEADERS = {
    'x-rapidapi-host': "hotels4.p.rapidapi.com",
    'x-rapidapi-key': RAPID_API_KEY
}


def request_to_api(url, querystring) -> json:
    """ Запрос к API """
    try:
        response = get(url, headers=HEADERS, params=querystring, timeout=10)
        logger.debug(f' запрос к API | url: {url}, город: {querystring["query"]}')
        if response.status_code == requests.codes.ok:  # Проверка успешности ответа перед возвращением результата
            logger.debug(f' запрос к API | успешно')
            return response
    # Обработка долгого соединения
    except:
        logger.error(f' запрос к API | url: {url}, город: {querystring["query"]} - НЕУДАЧА!')
        # Добавить вывод сообщения в телеграмм
