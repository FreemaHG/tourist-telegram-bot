from database.create_db import session
from database.create_data.create_hotels import create_new_hotel
from utils.request_for_api.api_request import request_to_api
from utils.misc.save_distance_to_center import save_distance
import json
import re
import datetime
from loguru import logger
from datetime import date
from typing import List, Union


URL = 'https://hotels4.p.rapidapi.com/properties/list'


def get_hostels(
        id_location: int,
        check_in_date: Union[date, None],
        departure_date: Union[date, None]) -> Union[List, bool]:

    """ Получаем id отелей по переданной id локации """

    hostels_list = []  # Для возврата id отелей

    if check_in_date is None or departure_date is None:
        logger.warning(f'check_in_date и departure_date не заданы, будут выбраны значения по-умолчанию')
        check_in_date = datetime.datetime.today().date()  # Дата заселения (текущая)
        departure_date = check_in_date + datetime.timedelta(days=1)  # Дата выезда (текущая + 1 день)
    else:
        check_in_date.strftime("%Y-%m-%d")  # Преобразуем в правильный формат для передачи в API
        departure_date.strftime("%Y-%m-%d")

    params = {
        "destinationId": id_location,
        "pageNumber": 1,
        "pageSize": 25,
        "checkIn": check_in_date,
        "checkOut": departure_date,
        "adults1": 1,
        "sortOrder": "PRICE",  # Сортировка по цене (по возрастанию)
        "locale": "ru_RU",
        "currency": "RUB"  # Вывод стоимости проживания в рублях
    }

    response = request_to_api(url=URL, querystring=params)  # Выполняем запрос к API

    if response is False:
        logger.error('отели от API не получены')
        return False

    # Проверка шаблоном перед извлечением ключа
    pattern = r'("results":.*),"pagination"'  # Шаблон для извлечения нужных данных из ответа от API
    # pattern = r'(?<=,)"results":.+?(?=,"pagination)'  # Шаблон из примера
    find = re.search(pattern, response.text)

    if find:
        logger.info(f'searchResults найден')
        result = json.loads(f"{{{find.group(1)}}}")
        data = result['results']
        logger.info(f'results найден')

        if not data:
            logger.error('данных по отелям нет в results')
            return False

        for hotel in data:
            id_hotel = hotel['id']  # id отеля
            name = hotel['name']  # Название отеля

            try:
                distance_data = hotel['landmarks']
                distance_to_center = save_distance(distance_data)  # Сохраняем расстояние до центра
            except KeyError as ext:
                logger.error(f'landmarks | данных по расстоянию до центра города нет. {ext}')
                distance_to_center = False

            try:
                price = int(hotel['ratePlan']['price']['exactCurrent'])
            except KeyError:
                logger.error(f'price | данных о стоимости нет, id отеля - {id_hotel}')
                price = False

            try:
                address = hotel['address']['streetAddress']
                locality = hotel['address']['locality']
                region = hotel['address']['region']

                full_address = ', '.join([address, locality, region])
                logger.info(f'address | успешно сохранен')
            except KeyError:
                logger.error(f'address | не найден')
                full_address = False

            hostels_list.append(id_hotel)  # Сохраняем id отеля в список для возврата (для сохранения фото)

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
        logger.debug(f'db | сохранение отелей в БД')

        return hostels_list

    else:  # Ошибка в поиске данных ответа от API по шаблону
        logger.warning(f'проверка полученных данных API | id отелей не получены')
        return False
