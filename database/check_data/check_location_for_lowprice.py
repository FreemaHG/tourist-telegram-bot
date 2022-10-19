from database.create_db import Locations, session
from loguru import logger
from sqlalchemy import or_


def check_location(location_name: str):  # Добавить аннотацию для возвращаемого результата
    """ Проверка локацию в БД """

    location_name = location_name.capitalize()

    # Проверить поиск с разными регистрами
    location = session.query(Locations)\
        .filter(or_(location_name == Locations.name, Locations.location.contains(location_name)))\
        .all()

    if location is None:
        logger.info(f'поиск результатов в БД | входные параметры: {location_name}, результатов не найдено')
        return False

    logger.info(f'поиск результатов в БД | входные параметры: {location_name}, найдены совпадения')
    return location
