from config_data.config import RAPID_API_KEY
import time
from requests import get
import requests
import json
from loguru import logger


HEADERS = {
    'x-rapidapi-host': "hotels4.p.rapidapi.com",
    'x-rapidapi-key': RAPID_API_KEY
}


def request_to_api(url, querystring, count: int = 0) -> json:
    """ Запрос к API по переданному url и параметрам """

    if count > 3:
        logger.error(f'API | превышено максимальное кол-во запросов | url: {url}, параметры: {querystring}')
        return False

    try:
        response = get(url, headers=HEADERS, params=querystring, timeout=10)
        logger.debug(f' запрос к API | url: {url}, параметры: {querystring}')
        if response.status_code == requests.codes.ok:  # Проверка успешности ответа перед возвращением результата
            logger.debug(f' запрос к API | успешно')
            return response
        else:
            # В случае неудачного ответа повторяем запрос
            logger.error(f' запрос к API | плохой ответ {response.status_code}, повтор запроса ч/з 0.5 сек')
            count += 1
            time.sleep(0.5)
            response = request_to_api(url, querystring, count)
            return response

    except requests.exceptions.Timeout:  # Обработка долгого соединения
        logger.error(f'запрос к API | превышено время ожидания ответа!')
        return False
