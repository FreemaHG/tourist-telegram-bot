from database.create_db import Photos, session
from loguru import logger


def create_new_photo(id_hotel: int, path: str, type_photo: str):
    """ Создаем новую запись с фото в БД """

    new_photo = Photos(
        id_hotel=id_hotel,
        path=path,
        type=type_photo
    )

    session.merge(new_photo)  # Сохраняем данные (только новые) в текущей сессии
    logger.debug(f'сохранение нового фото | id отеля: {id_hotel}, путь: {path}, тип: {type_photo}')
