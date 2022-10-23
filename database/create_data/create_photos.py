from database.create_db import Photos, session
from loguru import logger
from typing import Dict


def create_new_photo(data) -> None:
    """ Создаем новую запись с фото в БД """

    new_photo = Photos(
        id_hotel=data['id_hotel'],
        url=data['url'],
        type=data['type']
    )

    session.merge(new_photo)  # Сохраняем данные (только новые) в текущей сессии
    logger.debug(f'сохранение нового фото | id отеля: {data["id_hotel"]}, url: {data["url"]}, тип: {data["type"]}')
