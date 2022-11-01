from database.create_db import History, Hotels, session
from loguru import logger
from typing import Union, List, Dict


def get_history_user(id_user: int) -> Union[List[Dict], bool]:
    """ Получаем историю запросов (последние 5 записей) по переданному id пользователя """

    logger.info(f'поиск истории запросов для пользователя {id_user}')
    result_data = []

    history_records = session.query(History)\
        .filter(History.user_id == id_user)\
        .order_by(History.date_of_entry.desc()).limit(5).all()  # Последние 5 запросов пользователя

    if not history_records:
        logger.error('История запросов не найдена')
        return False

    for record in history_records:
        command_data = {
            'command': record.command,
            'date_of_entry': record.date_of_entry,
            'hotels': []
        }

        # Добавляем отели из истории запросов в ответ
        for hotel in record.hotels:
            hotel_data = session.query(Hotels).filter(Hotels.id == hotel.hotel_id).one_or_none()
            command_data['hotels'].append(hotel_data)

        result_data.append(command_data)

    return result_data
