from utils.request_for_api.api_request import request_to_api
from database.create_db import session
from database.create_data.create_hotels import create_new_hotel   # Проверка локации в БД
from utils.misc.save_distance_to_center import save_distance
from database.check_data.check_hotel_for_lowprice import check_location  # Проверка отеля в БД
import json
import re
import datetime
from loguru import logger
from typing import List, Union


URL = 'https://hotels4.p.rapidapi.com/properties/list'


def get_id_hostels(id_location: int) -> Union[List[int], bool]:
    """ Получаем id отелей """

    check_in_date = datetime.datetime.today().date()  # Дата заселения
    departure_date = check_in_date + datetime.timedelta(days=1)  # Дата выезда

    params = {
        "destinationId": id_location,
        "pageNumber": 1,
        "pageSize": 25,
        "checkIn": check_in_date,
        "checkOut": departure_date,
        "adults1": 1,
        "sortOrder": "PRICE",
        "locale": "ru_RU",
        "currency": "RUB"
    }

    # Выполняем запрос к API
    response = request_to_api(url=URL, querystring=params)

    # Проверка шаблоном перед извлечением ключа
    pattern = r'("results":.*),"pagination"'  # Возможно этот шаблон при использовании API
    find = re.search(pattern, response.text)
    if find:
        logger.debug(f'API | searchResults найден')
        result = json.loads(f"{{{find.group(1)}}}")
        data = result['results']
        logger.debug(f'API | results найден')

        hostels_id_list = []  # Для возврата id отелей

        for hotel in data:
            id_hotel = hotel['id']
            name = hotel['name']
            distance_data = hotel['landmarks']
            price = hotel['ratePlan']['price']['exactCurrent']

            try:
                address = hotel['address']['streetAddress']
                locality = hotel['address']['locality']
                region = hotel['address']['region']

                full_address = ', '.join([address, locality, region])
                logger.info(f'address | успешно сохранен')
            except KeyError as ext:
                logger.error(f'address | не найден. {ext}')
                full_address = ''

            # Сохраняем расстояние до центра
            distance_to_center = save_distance(distance_data)

            hostels_id_list.append(id_hotel)  # Сохраняем id отеля в список для возврата

            # ПРОВЕРИТЬ!!! ВОЗМОЖНО ПРАВИЛЬНО if check_location(id_hotel) is False:
            if not check_location(id_hotel):
                # Создаем новый отель в БД
                create_new_hotel(
                    id_hotel=id_hotel,
                    id_location=id_location,
                    name=name,
                    address=full_address,
                    distance_to_center=distance_to_center,
                    price=price
                )

        session.commit()  # Сохраняем записи в БД
        logger.debug(f'БД | сохранение данных отелей')

        return hostels_id_list

    else:  # Нет результатов
        logger.warning(f'проверка полученных данных API | id отелей не получены')
        return False
