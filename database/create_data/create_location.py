from database.create_db import Locations, session
from loguru import logger


def create_new_location(id_location: int, location: str, address: str, location_type: str, parent_id: int = None):
    """ Создаем новую запись о локации в БД """

    if parent_id is None:
        new_location = Locations(
            id=id_location,
            location=location,
            address=address,
            type=location_type
        )

        logger.info(
            f' сохранение данных локации в БД | родительская локация: id - {id_location}, '
            f'city: {location}')

    else:
        new_location = Locations(
            id=id_location,
            parent_id=parent_id,
            location=location,
            address=address,
            type=location_type
        )

        logger.info(
            f' сохранение данных локации в БД | дочерняя локация: id - {id_location}, '
            f'city: {location}'
        )

    session.merge(new_location)  # Сохраняем данные (только новые) в текущей сессии
