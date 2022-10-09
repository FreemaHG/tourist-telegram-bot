from config_data.config import RAPID_API_KEY
from database.create_db import Cities, session
from database.check_location_for_lowprice import check_location  # Проверка локации в БД
from utils.misc.address_conversion import func_address_conversion
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



def get_id_location(city: str) -> int:
    """ Получаем id локации """

    # Проверка локации по уже имеющимся данным из БД
    location_id = check_location(city)

    # Проверить!!!
    if location_id:
        return location_id

    response = request_to_api(url=URL, headers=HEADERS, querystring={"query": city, "locale": "ru_RU"})

    # Проверка шаблоном перед извлечением ключа
    pattern = r'(?<="CITY_GROUP",).+?[\]]'
    find = re.search(pattern, response.text)
    if find:
        logger.debug(f' проверка полученных данных API | CITY_GROUP найден')
        result = json.loads(f"{{{find[0]}}}")
        data = result['entities']
        logger.debug(f' проверка полученных данных API | entities найден')
        parent_id = None

        for location in data:
            id_location = location['destinationId']
            location_name = location['name']
            type_location = location['type']
            address = location['caption']

            # Преобразуем адрес в строку корректного вида
            correct_address = func_address_conversion(address)

            # НЕ КОРРЕКТНО (СОВПАДЕНИЕ МОЖЕТ БЫТЬ И НЕ В ГОРОДЕ!!!)
            if type_location == 'CITY':
                parent_id = id_location

                if location_name == city:
                    output_id = parent_id

                # Создаем РОДИТЕЛЬСКУЮ запись в БД
                new_parent_location = Cities(
                    id=id_location,
                    location=location_name,
                    address=correct_address,
                    type=type_location)
                session.merge(new_parent_location)  # Сохраняем данные в текущей сессии
                logger.info(
                    f' сохранение данных локации в БД | родительская локация: id - {id_location}, '
                    f'city: {location_name}')
            else:
                # Создаем ДОЧЕРНЮЮ запись в БД
                new_child_location = Cities(
                    id=id_location,
                    parent_id=parent_id,
                    location=location_name,
                    address=correct_address,
                    type=type_location
                )
                session.merge(new_child_location)  # Сохраняем данные в текущей сессии
                logger.info(
                    f' сохранение данных локации в БД | дочерняя локация: id - {id_location}, '
                    f'city: {location_name}'
                )
        session.commit()  # Сохраняем записи в БД
        logger.info(f' сохранение данных локации в БД | внесение новых данных в БД')

        return output_id


def get_id_hostels(id_location: int):
    """ Получаем id отелей в указанной локации """
    ...



def get_result(location: str, number_of_hotels: int, number_of_photos: int = 0):
    """ Получение результатов по переданным данным """

    id_location = get_id_location(location)



if __name__ == '__main__':
    TEST_CITY = 'Лондон'
    # Base.metadata.create_all(engine)  # # УДАЛИТЬ ПОСЛЕ ОТЛАДКИ!!!
    get_id_location(TEST_CITY)
