import requests
import os
from loguru import logger


ABS_PATH = os.path.abspath(os.path.join('..', '..', 'static'))


# Тестовое
URL = 'https://exp.cdn-hotels.com/hotels/37000000/36790000/36789900/36789845/d4aada11_z.jpg'


def test_save(url, id_hotel=1, id_img=123, type_photo='hotel'):

    resp_image = requests.get(URL)  # Получаем изображение по url

    if resp_image.status_code != 200:
        logger.error('images | изображение ОТЕЛЯ не найдено ')

    path = os.path.join(ABS_PATH, f'{id_hotel}', f'{type_photo}')  # Директория по номеру отеля и типу фото
    # Создаем директорию (exist_ok=True - не выдавать ошибку, если папка уже существует)
    os.makedirs(path, exist_ok=True)
    logger.debug(f'Директория {path} создана')

    with open(f'{path}/{id_img}.jpg', 'wb') as out:
        out.write(resp_image.content)
        logger.debug(f'Изображение {id_img} успешно создано')

    path_img = os.path.join(path, f'{id_img}.jpeg')  # Абсолютный путь до картинки

    print(path_img)


if __name__ == '__main__':
    test_save(URL)


# МОЖНО ОБЪЕДИНИТЬ ДВЕ ФУНКЦИИ В ОДНУ
# НЕ СОХРАНЯЮТСЯ ФОТО В STATIC
def save_img_hotel(url, id_hotel, id_img, type_photo) -> str:
    """ Сохраняем фото отеля в static, возвращаем путь до файла """

    resp_image = requests.get(url)  # Получаем изображение по url

    if resp_image.status_code != 200:
        logger.error('images | изображение ОТЕЛЯ не найдено ')

    path = os.path.join(ABS_PATH, f'{id_hotel}', f'{type_photo}')  # Директория по номеру отеля и типу фото
    # Создаем директорию (exist_ok=True - не выдавать ошибку, если папка уже существует)
    os.makedirs(path, exist_ok=True)
    logger.debug(f'Директория {path} создана')

    with open(f'{path}/{id_img}.jpg', 'wb') as out:
        out.write(resp_image.content)
        logger.debug(f'Изображение {id_img} успешно создано')

    path_img = os.path.join(path, f'{id_img}.jpeg')  # Абсолютный путь до картинки

    return path_img


def save_img_room(url, id_hotel, id_room, id_img, type_photo) -> str:
    """ Сохраняем фото комнаты в static, возвращаем путь до файла """

    # Обработка долгого соединения
    resp_image = requests.get(url, timeout=10)  # Получаем изображение по url

    if resp_image.status_code != 200:
        logger.error('images | изображение КОМНАТЫ не найдено ')

    path = os.path.join(ABS_PATH, f'{id_hotel}', f'{type_photo}, f{id_room}')  # Директория по номеру отеля и типу фото
    # Создаем директорию (exist_ok=True - не выдавать ошибку, если папка уже существует)
    os.makedirs(path, exist_ok=True)
    logger.debug(f'Директория {path} создана')

    with open(f'{path}/{id_img}.jpg', 'wb') as out:
        out.write(resp_image.content)
        logger.debug(f'Изображение {id_img} успешно создано')

    path_img = os.path.join(path, f'{id_img}.jpeg')  # Абсолютный путь до картинки

    return path_img



