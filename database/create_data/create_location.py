from database.create_db import Locations, session
from loguru import logger


def create_new_location(id_location: int, name_location: str, location: str):
    """ Создаем новую запись о локации в БД """

    new_location = Locations(
        id=id_location,
        name=name_location,
        location=location
    )

    logger.info(
        f' сохранение данных локации в БД | id - {id_location}, локация: {name_location}, адрес: {location}'
    )

    session.merge(new_location)  # Сохраняем данные (только новые) в текущей сессии
