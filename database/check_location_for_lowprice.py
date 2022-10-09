from database.create_db import Cities, session
from loguru import logger


def check_location(location_name: str) -> int:
    """ Проверка локации в БД """

    location = session.query(Cities).filter(Cities.location == location_name).one_or_none()

    if location is None:
        logger.info(f'поиск результатов в БД | входные параметры: {location_name}, результатов не найдено')
        return False

    logger.info(f'поиск результатов в БД | входные параметры: {location_name}, найдены совпадения')
    return location.id
