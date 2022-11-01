from database.create_db import Photos, session
from loguru import logger
from sqlalchemy import and_
from itertools import chain
from typing import Union, List, Tuple


def get_photos_of_hotel(id_hotel: int, number_of_photos: int) -> Union[List, Tuple[List, List]]:
    """ Получаем фото отеля из БД """

    logger.info(f'поиск фото для отеля {id_hotel}')
    photo_of_hotel = session.query(Photos.url).filter(and_(Photos.id_hotel == id_hotel, Photos.type == 'hotel')).all()
    photo_of_rooms = session.query(Photos.url).filter(and_(Photos.id_hotel == id_hotel, Photos.type == 'room')).all()

    # Извлекаем url картинок из кортежей внутри списка
    photo_of_hotel = list(chain(*photo_of_hotel))
    photo_of_rooms = list(chain(*photo_of_rooms))

    if not photo_of_hotel:
        logger.warning(f'db поиск фото | id отеля: {id_hotel}, фото отеля не найдено')
        photo_of_hotel = []

    if not photo_of_rooms:
        logger.warning(f'db поиск фото | id отеля: {id_hotel}, фото номеров не найдено')
        photo_of_rooms = []

    # В зависимости от выбранного кол-ва фото пользователем корректируем соотношение и кол-во возвращаемых картинок
    if number_of_photos == 2:
        return photo_of_hotel[:1] + photo_of_rooms[:1]

    elif 2 < number_of_photos < 6:
        return photo_of_hotel[:2] + photo_of_rooms[:number_of_photos - 2]

    else:
        return photo_of_hotel[:3] + photo_of_rooms[:8]  # макс. 10 фото
