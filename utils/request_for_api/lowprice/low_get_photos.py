from utils.request_for_api.api_request import request_to_api
from utils.misc.save_photo import save_img_hotel, save_img_room  # Для сохранения img в static
from database.create_data.create_photos import create_new_photo  # Для сохранения записи и местоположении фото в БД
from database.create_db import session

import re
from loguru import logger
import json
import requests


def get_and_save_photos(id_hotel: int) -> bool:
    """ Получаем и сохраняем фото по id переданного отеля """

    URL = "https://hotels4.p.rapidapi.com/properties/get-hotel-photos"
    response = request_to_api(url=URL, querystring={"id": id_hotel})

    if response is False:
        return False

    # Проверка шаблоном перед извлечением ключа
    pattern = r'("hotelId":\d*,.*),"featuredImageTrackingDetails"'  # Проверить!!!
    find = re.search(pattern, response.text)
    if find:
        logger.debug(f'API | hotelId найден')
        result = json.loads(f"{{{find.group(1)}}}")

        hotel_images = result['hotelImages']
        logger.debug(f'API | hotelImages найден')

        room_images = result['roomImages']
        logger.debug(f'API | roomImages найден')

        # СДЕЛАТЬ МНОГОПОТОЧНОСТЬ!!!
        # Для теста сохранять не более 3 фото отеля!!!
        # Получаем фото отеля из API
        for img_h in hotel_images:
            url = img_h['baseUrl']
            id_img = img_h['imageId']
            url = url.replace('{size}', 'z')  # Задаем фото нужного размера (1000*667)

            path_img = save_img_hotel(url, id_hotel, id_img, 'hotel')  # Сохраняем картинку в static

            if path_img:
                create_new_photo(id_hotel, path_img, 'hotel')  # Сохраняем картинку в БД
            else:
                logger.error('Ошибка! Путь до файла не получен')

        # Для теста сохранять не более 3 фото комнаты!!!
        # Получаем фото номеров из API
        for room in room_images:
            id_room = room['roomId']  # Сохраняем id комнаты
            images = room['images']  # Сохраняем все фото указанной комнаты

            for img in images:
                id_photo = img['imageId']
                url = img['baseUrl']
                url = url.replace('{size}', 'z')  # Задаем фото нужного размера (1000*667)

                path_img = save_img_room(url, id_hotel, id_room, id_photo, 'room')  # Сохраняем картинку в static

                if path_img:
                    create_new_photo(id_hotel, path_img, 'room')  # Сохраняем картинку в БД
                else:
                    logger.error('Ошибка! Путь до файла не получен')

        session.commit()  # Сохраняем записи в БД
        logger.debug(f'БД | все фото типа hotelImages сохранены')
        return True

    else:  # Нет результатов
        logger.warning(f'проверка полученных данных API | нет фото по указанному id отеля')
        return False
