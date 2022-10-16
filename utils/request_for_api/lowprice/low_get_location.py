from utils.request_for_api.api_request import request_to_api
from database.create_db import session
from database.check_data.check_location_for_lowprice import check_location  # Проверка локации в БД
from database.create_data.create_location import create_new_location  # Проверка локации в БД
from utils.misc.address_conversion import func_address_conversion
import json
import re
from loguru import logger


URL = 'https://hotels4.p.rapidapi.com/locations/v2/search'


def get_id_location(city: str) -> int:
    """ Получаем id локации """

    # Проверка локации по уже имеющимся данным из БД
    location_id = check_location(city)
    if location_id:
        return location_id

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

        parent_location = data[0]
        parent_id = parent_location['destinationId']
        parent_location_name = parent_location['name']

        # Преобразуем адрес в строку корректного вида
        correct_address = func_address_conversion(parent_location['caption'])

        # Создаем РОДИТЕЛЬСКУЮ запись в БД
        create_new_location(
            id_location=parent_id,
            location=parent_location_name,
            address=correct_address,
            location_type=parent_location['type']
        )

        for location in data[1:]:
            address = location['caption']
            child_id = location['destinationId']
            child_location_name = location['name']

            # Преобразуем адрес в строку корректного вида
            correct_address = func_address_conversion(address)

            # Создаем ДОЧЕРНЮЮ запись в БД
            create_new_location(
                id_location=child_id,
                parent_id=parent_id,
                location=child_location_name,
                address=correct_address,
                location_type=location['type']
            )

        session.commit()  # Сохраняем записи в БД
        logger.info(f' сохранение данных локации в БД | внесение новых данных в БД')

        return parent_id

    else:  # Нет результатов
        logger.warning(f'API | id локации не найдена')
        return False
