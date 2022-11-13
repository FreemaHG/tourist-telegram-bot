import time
import threading

from loguru import logger
from sqlalchemy.exc import InvalidRequestError

from database.create_db import Photos, session


def check_img(id_img: int, count: int = 1) -> bool:
    """ Проверка фото в БД по id """

    name, ident = threading.current_thread().name, threading.get_ident()  # имя и id потока

    if count > 3:
        logger.error(f'DB | превышено максимальное кол-во попыток')
        return False

    try:
        photo = session.query(Photos).filter(Photos.id == id_img).one_or_none()

        if photo is None:
            logger.warning(f'db поиск фото | id фото: {id_img}, результатов не найдено')
            return False

        logger.info(f'db поиск фото | id фото: {id_img}, найдены совпадения')
        return True

    except InvalidRequestError:
        logger.error(f'DB | поток: {name}, id: {ident} | сеанс запроса к БД отклонен, повтор ч/з 3 сек...')
        count += 1
        time.sleep(3)
        result = check_img(id_img, count)
        return result
