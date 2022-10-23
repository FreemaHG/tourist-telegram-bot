from database.create_db import Photos, session
from loguru import logger
from sqlalchemy import and_


def get_photos_of_hotel(id_hotel: int, number_of_photos: int):
    """ Получаем фото отеля из БД """

    logger.info(f'поиск фото для отеля {id_hotel}')
    photo_of_hotel = session.query(Photos.url).filter(and_(Photos.id_hotel == id_hotel, Photos.type == 'hotel')).all()
    photo_of_rooms = session.query(Photos.url).filter(and_(Photos.id_hotel == id_hotel, Photos.type == 'room')).all()
    print('11 photo_of_hotel:', photo_of_hotel)
    print('12 photo_of_rooms:', photo_of_rooms)

    if not photo_of_hotel:
        logger.warning(f'db поиск фото | id отеля: {id_hotel}, фото отеля не найдено')
        photo_of_hotel = []

    if not photo_of_rooms:
        logger.warning(f'db поиск фото | id отеля: {id_hotel}, фото номеров не найдено')
        photo_of_rooms = []

    # В зависимости от выбранного кол-ва фото пользователем корректируем выдачу
    if number_of_photos == 2:
        return photo_of_hotel[:1], photo_of_rooms[:1]

    elif 3 < number_of_photos < 6:
        return photo_of_hotel[:1], photo_of_rooms[:4]

    else:
        return photo_of_hotel[:3], photo_of_rooms
