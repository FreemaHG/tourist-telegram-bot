from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from utils.request_for_api.api_request import request_to_api
from database.create_db import session
from database.check_data.check_location_for_lowprice import check_location  # Проверка локации в БД
from database.create_data.create_location import create_new_location  # Проверка локации в БД
from utils.misc.address_conversion import func_address_conversion
import json
import re
from loguru import logger
from typing import Union, List, Dict, Any


URL = 'https://hotels4.p.rapidapi.com/locations/v2/search'


def get_id_location(city: str) -> Union[List[dict[str, Union[str, Any]]], bool]:  # Добавить аннотацию для возвращаемого результата
    """ Получаем id локаций """

    location_id_list = []  # Список для вывода результатов

    # Проверка локации по уже имеющимся данным из БД
    locations = check_location(city)

    if locations:
        for location in locations:
            # Добавляем локацию в список для передачи пользователю для уточнения результата
            location_id_list.append(
                {
                    'id': location.id,
                    'location': location.location
                }
            )

        return location_id_list

    # Выполняем запрос к API
    response = request_to_api(url=URL, querystring={"query": city, "locale": "ru_RU"})

    if response is False:
        return False

    # Проверка шаблоном перед извлечением ключа
    pattern = r'(?<="CITY_GROUP",).+?[\]]'
    find = re.search(pattern, response.text)
    if find:
        logger.debug('API | CITY_GROUP найден')
        result = json.loads(f"{{{find[0]}}}")
        data = result['entities']
        logger.debug('API | entities найден')

        if not data:
            logger.error('API | данных по локациям нет')
            return False

        for location in data:
            id_location = location['destinationId']  # id локации
            location_name = location['name']  # Название локации
            location = location['caption']  # Адрес
            correct_location_str = func_address_conversion(location)  # Убираем html-теги из строки

            # Добавляем локацию в список для передачи пользователю для уточнения результата
            location_id_list.append(
                {
                    'id': id_location,
                    'location': correct_location_str
                }
            )

            # Создаем запись в БД
            create_new_location(
                id_location=id_location,
                name_location=location_name,
                location=correct_location_str
            )

        session.commit()  # Сохраняем записи в БД
        logger.info(f' сохранение данных локации в БД | внесение новых данных в БД')

        return location_id_list

    else:  # Нет результатов
        logger.warning(f'API | id локации не найдена')
        return False


def city_markup(city_name: str):
    """ Возвращает варианты локация для уточнения """
    cities = get_id_location(city_name)  # Делаем запрос к API, получаем список с id и адресами локаций
    destinations = InlineKeyboardMarkup()
    for city in cities:
        destinations.add(InlineKeyboardButton(text=city["location"],
                          callback_data=f'{city["id"]}'))
    return destinations
