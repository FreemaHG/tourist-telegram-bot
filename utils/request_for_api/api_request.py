from config_data.config import RAPID_API_KEY
import requests
from requests import get
import json
from loguru import logger


HEADERS = {
    'x-rapidapi-host': "hotels4.p.rapidapi.com",
    'x-rapidapi-key': RAPID_API_KEY
}


def request_to_api(url, querystring) -> json:  # Исправить аннотация - возвращает False
    """ Запрос к API """
    try:
        response = get(url, headers=HEADERS, params=querystring, timeout=10)
        logger.debug(f' запрос к API | url: {url}, параметры: {querystring}')
        if response.status_code == requests.codes.ok:  # Проверка успешности ответа перед возвращением результата
            logger.debug(f' запрос к API | успешно')
            return response
        else:
            logger.error(f' запрос к API | плохой ответ {response.status_code}')
            return False

    except requests.exceptions.Timeout as e:  # Обработка долгого соединения
        logger.error(f'запрос к API | НЕУДАЧА!')
        logger.exception(e)  # Проверить!!!
        return False
