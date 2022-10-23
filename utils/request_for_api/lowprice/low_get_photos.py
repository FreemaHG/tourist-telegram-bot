import threading
from threading import Lock

from utils.request_for_api.api_request import request_to_api
from utils.misc.save_photos import save_photo  # Для сохранения img в static
from database.create_db import session
from database.create_data.create_photos import create_new_photo

import re
from loguru import logger
import json
import requests

from multiprocessing.pool import ThreadPool
import multiprocessing

LOCK = Lock()
URL = "https://hotels4.p.rapidapi.com/properties/get-hotel-photos"


def preparation_photos(id_hotel: int) -> bool:
    """ Получаем и подготавливаем данные по фото по id переданного отеля """

    name, ident = threading.current_thread().name, threading.get_ident()  # имя и id потока
    images_urls_list = []  # Ссылки на нужные фото

    response = request_to_api(url=URL, querystring={"id": id_hotel})

    if not response:
        logger.error(f'API | поток: {name}, id: {ident} | фото не получены')
        return False

    # Проверка шаблоном перед извлечением ключа
    pattern = r'("hotelId":\d*,.*),"featuredImageTrackingDetails"'  # Проверить!!!
    find = re.search(pattern, response.text)
    if find:
        logger.info(f'thread | поток: {name}, id: {ident} | hotelId найден')
        result = json.loads(f"{{{find.group(1)}}}")

        hotel_images = result['hotelImages'][:5]  # 5 фото отеля
        logger.info(f'thread | поток: {name}, id: {ident} | hotelImages найден')

        room_images = result['roomImages'][:10]  # 10 номеров
        logger.debug(f'thread | поток: {name}, id: {ident} | roomImages найден')

        # Фото отеля
        for img_h in hotel_images:
            url_img = img_h['baseUrl']  # url фото из ответа API
            url_img_with_size = url_img.replace('{size}', 'z')  # Задаем фото нужного размера (1000*667)

            # Подготавливаем данные по фото для запроса с сайта и сохранения локально в БД
            images_urls_list.append(
                {
                    'url': url_img_with_size,
                    'id_hotel': id_hotel,
                    'type': 'hotel'
                }
            )

        logger.info(f'thread | поток: {name}, id: {ident} | данные по фото ОТЕЛЯ подготовлены')

        # Фото комнат
        for room in room_images:
            images = room['images'][:3]  # По 3 фото каждой комнаты

            for img in images:
                url_img = img['baseUrl']
                url_img_with_size = url_img.replace('{size}', 'z')  # Задаем фото нужного размера (1000*667)

                # Подготавливаем данные по фото для запроса с сайта и сохранения локально в БД
                images_urls_list.append(
                    {
                        'url': url_img_with_size,
                        'id_hotel': id_hotel,
                        'type': 'room'
                    }
                )

        logger.info(f'thread | поток: {name}, id: {ident} | данные по фото НОМЕРОВ подготовлены')

        # Многопоточная загрузка фото
        with LOCK:  # Замок для сессии (во избежания ошибок при сохранении данных в БД)
            child_pool = ThreadPool(
                processes=multiprocessing.cpu_count() * 5)  # Запускаем потоков в 5 раз больше, чем есть у нас ядер

            logger.info(f'thread | поток: {name}, id: {ident} | запуск многопоточной загрузки фото')
            child_pool.map(create_new_photo, images_urls_list)

            child_pool.close()  # Обязательно закрываем объект Pool
            child_pool.join()

            session.commit()  # Сохраняем записи в БД
            logger.debug(f'db | сохранение фото в БД')

    else:  # Ошибка в поиске данных ответа от API по шаблону
        logger.error(f'thread | поток: {name}, id: {ident} | hotelId не найден')
        return False
