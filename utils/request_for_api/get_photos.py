import threading
from threading import Lock
import re
import json

from loguru import logger

from database.create_data.create_photos import create_new_photo
from utils.request_for_api.api_request import request_to_api


LOCK = Lock()
URL = "https://hotels4.p.rapidapi.com/properties/get-hotel-photos"


def preparation_photos(id_hotel: int) -> bool:
    """ Получаем и подготавливаем данные по фото по id переданного отеля """

    name, ident = threading.current_thread().name, threading.get_ident()  # имя и id потока
    response = request_to_api(url=URL, querystring={"id": id_hotel})

    if not response:
        logger.error(f'API | поток: {name}, id: {ident} | фото не получены')
        return False

    # Проверка шаблоном перед извлечением ключа
    pattern = r'("hotelId":\d*,.*),"featuredImageTrackingDetails"'
    find = re.search(pattern, response.text)
    if find:
        logger.info(f'thread | поток: {name}, id: {ident} | hotelId найден')
        result = json.loads(f"{{{find.group(1)}}}")

        hotel_images = result['hotelImages'][:2]  # по 2 фото отеля
        logger.info(f'thread | поток: {name}, id: {ident} | hotelImages найден')

        room_images = result['roomImages'][:8]  # по 8 номеров в отеле
        logger.debug(f'thread | поток: {name}, id: {ident} | roomImages найден')

        with LOCK:
            # Фото отеля
            for img_h in hotel_images:
                url_img = img_h['baseUrl']  # url фото из ответа API
                id_img = img_h['imageId']  # id картинки (чтобы не повторялись в БД)
                url_img_with_size = url_img.replace('{size}', 'z')  # Задаем фото нужного размера (1000*667)

                create_new_photo(
                    id_photo=id_img,
                    id_hotel=id_hotel,
                    url=url_img_with_size,
                    type_photo='hotel'
                )

            # Фото комнат
            for room in room_images:
                images = room['images'][:3]  # По 3 фото каждой комнаты (с запасом на случай, если кол-во номеров
                # будет малым и кол-во фото будет не хватать)

                for img in images:
                    url_img = img['baseUrl']
                    id_img = img['imageId']  # id картинки (чтобы не повторялись в БД)
                    url_img_with_size = url_img.replace('{size}', 'z')  # Задаем фото нужного размера (1000*667)

                    # Подготавливаем данные по фото для запроса с сайта и сохранения локально в БД
                    create_new_photo(
                        id_photo=id_img,
                        id_hotel=id_hotel,
                        url=url_img_with_size,
                        type_photo='room'
                    )

    else:  # Ошибка в поиске данных ответа от API по шаблону
        logger.error(f'thread | поток: {name}, id: {ident} | hotelId не найден')
        return False
