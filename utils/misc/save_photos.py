import re
import threading
import requests
import os
from loguru import logger

from typing import Union, List, Dict

from database.check_data.check_image import check_img
from database.create_data.create_photos import create_new_photo  # Для сохранения записи и местоположении фото в БД

ABS_PATH = os.path.abspath(os.path.join('..', '..', 'static'))  # Путь по папки static с фото


def save_photo(data: Dict) -> bool:
    """ Сохраняем фото в static и БД """

    name, ident = threading.current_thread().name, threading.get_ident()  # имя и id потока
    logger.info(f'img | поток: {name}, id: {ident} | сохраняем фото: {data["id_image"]}')

    # Получаем фото
    try:
        resp_image = requests.get(data['url'], timeout=10)  # Получаем изображение по url
    except requests.exceptions.Timeout:
        logger.error(f'img | поток: {name}, id: {ident} | фото не получено, превышено время ожидания от сервера')
        return False

    if resp_image.status_code != 200:
        logger.error(f'img | поток: {name}, id: {ident} | изображение не найдено, url - {data["url"]}')
        return False

    # Абсолютный путь для изображения
    if data['type'] == 'room':
        path = os.path.join(ABS_PATH, f'{data["id_hotel"]}', f'{data["type"]}', f'{data["id_room"]}')
    else:
        path = os.path.join(ABS_PATH, f'{data["id_hotel"]}', f'{data["type"]}')

    img_url = os.path.join(path, f'{data["id_image"]}.jpeg')
    logger.info(f'img | проверка пути {img_url}')

    # Проверка изображения в каталоге
    if os.path.exists(img_url):
        logger.info('img | изображение уже есть в каталоге')
    else:
        # Создаем директорию (exist_ok=True - не выдавать ошибку, если папка уже существует)
        os.makedirs(path, exist_ok=True)
        logger.info(f'img | директория {path} создана')

        with open(f'{path}/{data["id_image"]}.jpg', 'wb') as out:
            out.write(resp_image.content)
            logger.debug(f'img | изображение успешно создано: {img_url}')

    # Проверка изображения в БД
    if check_img(data['id_image']):
        logger.info('img | запись об изображении есть в БД')
    else:
        # Ссылка вида \static\<id_hotel>\<type_photo>\<id_room>\<id_img>.jpeg
        try:
            img_path = re.search(r'(.static.*)', img_url).group(1)
        except AttributeError:
            logger.error(f'img | поток: {name}, id: {ident} | не удалось вычленить относительную ссылку')
            return False

        create_new_photo(
            id_img=data['id_image'],
            id_hotel=data['id_hotel'],
            path=img_path,
            type_photo=data['type']
        )

    return True
