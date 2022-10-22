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


def get_id_location(city: str) -> Union[List[dict[str, Union[str, Any]]], bool]:
    """ Получаем id локаций """

    location_id_list = []  # Список для вывода результатов

    # Проверка локации в БД
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

        logger.info('возврат результатов локаций из БД')
        return location_id_list

    # Выполняем запрос к API
    response = request_to_api(url=URL, querystring={"query": city, "locale": "ru_RU"})

    if response is False:
        logger.error('локации от API не получены')
        return False

    pattern = r'(?<="CITY_GROUP",).+?[\]]'  # Проверка шаблоном перед извлечением ключа
    find = re.search(pattern, response.text)
    if find:
        logger.info('CITY_GROUP найден')
        result = json.loads(f"{{{find[0]}}}")
        data = result['entities']
        logger.info('entities найден')

        if not data:
            logger.error('данных по локациям нет в entities')
            return False

        for location in data:
            id_location = location['destinationId']  # id локации
            location_name = location['name']  # Название локации
            location = location['caption']  # Адрес
            correct_location_str = func_address_conversion(location)  # Убираем html-теги из строки

            if not correct_location_str:  # Если не удалось корректно преобразовать адрес
                logger.error(f'не удалось очистить строку от тегов: {location}')
                continue  # Пропускаем локацию

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
        logger.debug(f'db | сохранение локаций в БД')

        return location_id_list

    else:  # Ошибка в поиске данных ответа от API по шаблону
        logger.warning(f'CITY_GROUP не найден')
        return False


def city_markup(city_name: str) -> Union[InlineKeyboardMarkup, bool]:
    """ Возвращает варианты локаций для уточнения пользователем """
    cities = get_id_location(city_name)  # Делаем запрос к API, получаем список с id и адресами локаций

    if not cities:
        return False

    destinations = InlineKeyboardMarkup()  # Создаем клавиатуру
    for city in cities:
        # Добавляем в клавиатуру кнопку с данными по локации
        destinations.add(InlineKeyboardButton(text=city["location"],
                          callback_data=f'{city["id"]}'))

    logger.info('возврат клавиатуры с локациями для уточнения дальнейшего поиска')
    return destinations
