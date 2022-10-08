from config_data.config import RAPID_API_KEY
from database.create_db import Cities, session
from database.create_db import Base, engine  # УДАЛИТЬ ПОСЛЕ ОТЛАДКИ!!!
import requests
from requests import request, get
import json
import re
from loguru import logger  # Для логирования


URL = 'https://hotels4.p.rapidapi.com/locations/v2/search'
HEADERS = {
    'x-rapidapi-host': "hotels4.p.rapidapi.com",
    'x-rapidapi-key': RAPID_API_KEY
}


# Сделать получение данных из БД, если идентичный запрос


# Шаблон общей функции для запросов к API
def request_to_api(url, headers, querystring) -> json:
    """ Запрос к API """
    try:
        response = get(url, headers=headers, params=querystring, timeout=10)
        logger.debug(f' запрос к API | url: {URL}, город: {querystring["query"]}')
        if response.status_code == requests.codes.ok:  # Проверка успешности ответа перед возвращением результата
            logger.debug(f' запрос к API | успешно')
            return response
    # Обработка долгого соединения
    except:
        logger.error(f' запрос к API | url: {URL}, город: {querystring["query"]} - НЕУДАЧА!')
        # Добавить вывод сообщения в телеграмм



def get_id_location(city: str) -> None:
    """ Получаем id локации """
    response = request_to_api(url=URL, headers=HEADERS, querystring={"query": city, "locale": "ru_RU"})

    # Проверка шаблоном перед извлечением ключа
    pattern = r'(?<="CITY_GROUP",).+?[\]]'
    find = re.search(pattern, response.text)
    if find:
        logger.debug(f' проверка полученных данных API | CITY_GROUP найден')
        result = json.loads(f"{{{find[0]}}}")
        data = result['entities']
        logger.debug(f' проверка полученных данных API | entities найден')
        start_index = 0
        parent_id = None

        if data[0]['type'] == 'CITY':
            start_index = 1
            # print('\nРодительская запись')
            # print('Город:', data[0]['name'])
            # print('id:', data[0]['destinationId'])

            parent_id = data[0]['destinationId']
            parent_city = data[0]['name']
            logger.info(f' сохранение данных локации | родительская локация: id - {parent_id}, city: {city}')

            # Создаем РОДИТЕЛЬСКУЮ запись в БД
            new_parent_location = Cities(
                id=parent_id,
                city=parent_city
            )

            session.merge(new_parent_location)  # Сохраняем данные в текущей сессии
            logger.info(f' сохранение данных локации в БД | родительская локация: id - {parent_id}, city: {parent_city}')

        # for place in result['entities'][start_index:]:
        for place in data[start_index:]:
            id_child_city = place['destinationId']
            city_child = place['name']

            # print('\nДочерняя запись')
            # print('Город:', place['name'])
            # print('id:', place['destinationId'])

            # Создаем ДОЧЕРНИЕ записи в БД
            new_child_location = Cities(
                id=id_child_city,
                parent_id=parent_id,
                city=city_child
            )

            session.merge(new_child_location)  # Сохраняем данные в текущей сессии
            logger.info(f' сохранение данных локации в БД | дочерняя локация: id - {id_child_city}, city: {city_child}')

        session.commit()  # Сохраняем записи в БД
        logger.info(f' сохранение данных локации в БД | внесение новых данных в БД')




if __name__ == '__main__':
    TEST_CITY = 'Лондон'
    # Base.metadata.create_all(engine)  # # УДАЛИТЬ ПОСЛЕ ОТЛАДКИ!!!
    get_id_location(TEST_CITY)
