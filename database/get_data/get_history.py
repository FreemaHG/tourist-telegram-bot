from sqlalchemy.orm import joinedload

from database.create_db import History, Hotels, Association, session
from database.get_data.get_photos import get_photos_of_hotel
from loguru import logger
from sqlalchemy import and_
from itertools import chain
from typing import Union, List, Dict, Tuple


def get_history_user(id_user: int) -> Union[List[Dict], bool]:
    """ Получаем историю запросов пользователя """

    logger.info(f'поиск истории запросов для пользователя {id_user}')
    result_data = []

    # Сделать жадную загрузку связных записей
    history_records = session.query(History)\
        .filter(History.user_id == id_user)\
        .order_by(History.date_of_entry.desc()).limit(5).all()  # Последние 5 запросов пользователя

    logger.debug(f'Кол-во найденных записей: {len(history_records)}')

    if not history_records:
        logger.error('История запросов не найдена')
        return False

    for record in history_records:
        command_data = {
            'command': record.command,
            'date_of_entry': record.date_of_entry,
            'hotels': []
        }

        for hotel in record.hotels:
            # Переместить запрос в жадную загрузку выше
            hotel_data = session.query(Hotels).filter(Hotels.id == hotel.hotel_id).one_or_none()
            command_data['hotels'].append(hotel_data)

        result_data.append(command_data)

    return result_data
