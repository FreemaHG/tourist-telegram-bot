from telebot.types import Message
from loader import bot
from loguru import logger

from database.get_data.get_history import get_history_user


@bot.message_handler(commands=['history'])
def history_return(message: Message) -> None:
    """ Отправляем историю поиска пользователя """

    user_id = int(message.from_user.id)
    logger.info(f'Запуск сценария {message.text} для пользователя - {user_id}')

    result = get_history_user(user_id)  # Получаем историю запросов пользователя

    if not result:
        bot.send_message(message.from_user.id, 'История запросов не найдена')
    else:
        bot.send_message(message.from_user.id, 'Будут выведены последние 5 запросов')

        for record in result:
            # Данные по команде
            data_for_record = f"*Введенная команда:* {record['command']}\n" \
                              f"*Дата ввода:* {record['date_of_entry'].strftime('%d.%m.%y %H:%M:%S')}\n"

            bot.send_message(message.from_user.id, data_for_record, parse_mode='Markdown')

            # Данные по найденным отелям
            for hotel in record['hotels']:
                data_for_hotel = f"*Отель:* [{hotel.name}](https://www.hotels.com/ho{hotel.id})\n" \
                                 f"*Адрес:* {hotel.address}\n" \
                                 f"*Расстояние до центра:* {hotel.distance_to_center} км\n" \
                                 f"*Стоимость:* {hotel.price} руб/сут\n"\

                bot.send_message(message.from_user.id, data_for_hotel, parse_mode='Markdown')

        logger.info('Все данные по отелям успешно собраны и отправлены пользователю')
