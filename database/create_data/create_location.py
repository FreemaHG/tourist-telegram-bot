from database.create_db import Locations, session
from loguru import logger


def create_new_location(id_location: int, name_location: str, location: str):
    """ Создаем новую запись о локации в БД """

    new_location = Locations(
        id=id_location,
        name=name_location,
        location=location
    )

    session.merge(new_location)  # Сохраняем данные (merge - только новые) в текущей сессии
    logger.debug(
        f'db | сохранение данных в сессии: id - {id_location}, локация: {name_location}, адрес: {location}'
    )
