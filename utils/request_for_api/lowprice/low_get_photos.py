from utils.request_for_api.api_request import request_to_api
from database.create_db import session

import re
from loguru import logger
import json


def get_and_save_photos(id_hotel: int) -> None:
    """ Получаем и сохраняем фото по id переданного отеля """

    URL = "https://hotels4.p.rapidapi.com/properties/get-hotel-photos"
    response = request_to_api(url=URL, querystring={"id": id_hotel})

    # Проверка шаблоном перед извлечением ключа
    pattern = r'("hotelId":\d*,.*),"featuredImageTrackingDetails"'  # Проверить!!!
    find = re.search(pattern, response.text)
    if find:
        logger.debug(f'API | hotelId найден')
        result = json.loads(f"{{{find.group(1)}}}")

        # Продолжить с этого момента

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
