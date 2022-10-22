from utils.request_for_api.api_request import request_to_api
from database.create_db import session
from database.create_data.create_hotels import create_new_hotel   # Проверка локации в БД
from utils.misc.save_distance_to_center import save_distance
from database.check_data.check_hotel_for_lowprice import check_hotel, check_hotels_by_id_location  # Проверка отеля в БД
import json
import re
import datetime
from loguru import logger
from typing import List, Union


URL = 'https://hotels4.p.rapidapi.com/properties/list'


def get_id_hostels(id_location: int) -> Union[List[int], bool]:
    """ Получаем id отелей нужной локации """

    hostels_id_list = []  # Для возврата id отелей

    # Проверка отелей в БД
    hotels = check_hotels_by_id_location(id_location)

    if hotels:
        for hotel in hotels:
            # Добавляем локацию в список для передачи пользователю для уточнения результата
            hostels_id_list.append(hotel.id)

        logger.info('возврат результатов по отелям из БД')
        return hostels_id_list

    check_in_date = datetime.datetime.today().date()  # Дата заселения (сегодня)
    departure_date = check_in_date + datetime.timedelta(days=1)  # Дата выезда (сегодня + 1 день)

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

    # Выполняем запрос к API
    response = request_to_api(url=URL, querystring=params)

    if response is False:
        logger.error('отели от API не получены')
        return False

    # Проверка шаблоном перед извлечением ключа
    pattern = r'("results":.*),"pagination"'  # Возможно этот шаблон при использовании API
    # pattern = r'(?<=,)"results":.+?(?=,"pagination)'  # Из примера (ПРОВЕРИТЬ!!!)
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
                logger.exception(ext)  # ПРОВЕРИТЬ!!!
                distance_to_center = False

            try:
                price = hotel['ratePlan']['price']['exactCurrent']
            except KeyError as ext:
                logger.error(f'price | данных о стоимости нет, id отеля - {id_hotel}')
                logger.exception(ext)  # ПРОВЕРИТЬ!!!
                price = False

            try:
                address = hotel['address']['streetAddress']
                locality = hotel['address']['locality']
                region = hotel['address']['region']

                full_address = ', '.join([address, locality, region])
                logger.info(f'address | успешно сохранен')
            except KeyError as ext:
                logger.error(f'address | не найден')
                full_address = False

            hostels_id_list.append(id_hotel)  # Сохраняем id отеля в список для возврата

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

        return hostels_id_list

    else:  # Ошибка в поиске данных ответа от API по шаблону
        logger.warning(f'проверка полученных данных API | id отелей не получены')
        return False
