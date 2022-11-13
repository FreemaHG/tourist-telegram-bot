from telebot.types import Message
from loader import bot
from loguru import logger

from states.data_for_lowprice import UserInfoForLowprice  # Для отслеживания состояний
from handlers.custom_handlers import lowprice_and_highprice  # Для возврата к основной логике вопросов


@bot.message_handler(state=UserInfoForLowprice.min_price)
def get_min_price(message: Message) -> None:
    """ Сохраняем диапазон цен - минимальную стоимость проживания """

    if message.text.isdigit():
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['min_price'] = message.text
            logger.debug(f'user_id({message.from_user.id}) | данные приняты: min_price - {message.text}')
            bot.send_message(message.from_user.id, 'Записал. Укажите максимальную цену (в руб.)')
            bot.set_state(message.from_user.id, UserInfoForLowprice.max_price, message.chat.id)
    else:
        bot.send_message(message.from_user.id, 'Пожалуйста, введите число!')
        logger.warning(f'user_id({message.from_user.id}) | не корректные данные: min_price - {message.text}')


@bot.message_handler(state=UserInfoForLowprice.max_price)
def get_max_price(message: Message) -> None:
    """ Сохраняем диапазон цен - максимальную стоимость проживания """

    if message.text.isdigit():
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['max_price'] = message.text

            if int(data['max_price']) < int(data['min_price']):
                logger.warning(f'user_id({message.from_user.id}) | не корректные данные: '
                               f'min_price ({data["min_price"]}) > max_price ({data["max_price"]})')
                bot.send_message(message.from_user.id,
                                 'Максимальная цена не может быть меньше минимальной, повторите ввод')
                bot.send_message(message.from_user.id, 'Введите минимальную цену (в руб.)')
                bot.set_state(message.from_user.id, UserInfoForLowprice.min_price, message.chat.id)

            else:
                logger.debug(f'user_id({message.from_user.id}) | данные приняты: max_price - {message.text}')
                bot.send_message(message.from_user.id,
                                 'Хорошо. Укажите диапазон расстояний до центра')
                bot.send_message(message.from_user.id,
                                 'Минимально допустимое расстояние (в км)')
                bot.set_state(message.from_user.id, UserInfoForLowprice.min_distance_to_center, message.chat.id)
    else:
        bot.send_message(message.from_user.id, 'Пожалуйста, введите число!')
        logger.warning(f'user_id({message.from_user.id}) | не корректные данные: max_price - {message.text}')


@bot.message_handler(state=UserInfoForLowprice.min_distance_to_center)
def get_min_distance_to_center(message: Message) -> None:
    """ Сохраняем диапазон расстояний до центра - минимальное расстояние """

    if message.text.isdigit():
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['min_distance_to_center'] = message.text
            logger.debug(f'user_id({message.from_user.id}) | данные приняты: min_distance_to_center - {message.text}')
            bot.send_message(message.from_user.id,
                             'Записал. Укажите максимально допустимое расстояние до центра (в км)')
            bot.set_state(message.from_user.id, UserInfoForLowprice.max_distance_to_center, message.chat.id)
    else:
        bot.send_message(message.from_user.id, 'Пожалуйста, введите число!')
        logger.warning(f'user_id({message.from_user.id}) | '
                       f'не корректные данные: min_distance_to_center - {message.text}')


@bot.message_handler(state=UserInfoForLowprice.max_distance_to_center)
def get_max_distance_to_center(message: Message) -> None:
    """ Сохраняем диапазон расстояний до центра - максимальное расстояние """

    if message.text.isdigit():
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['max_distance_to_center'] = message.text

            if int(data['min_distance_to_center']) > int(data['max_distance_to_center']):
                logger.warning(f'user_id({message.from_user.id}) | не корректные данные: '
                               f'min_distance_to_center ({data["min_distance_to_center"]}) > '
                               f'max_distance_to_center ({data["max_distance_to_center"]})')
                bot.send_message(message.from_user.id, 'Максимальное расстояние не может быть меньше минимального, '
                                                       'повторите ввод')
                bot.send_message(message.from_user.id, 'Введите минимально допустимое расстояние до центра (в км)')
                bot.set_state(message.from_user.id, UserInfoForLowprice.min_distance_to_center, message.chat.id)

            else:
                bot.send_message(message.from_user.id, 'Запомнил. Сколько отелей показать в выдаче (не более 15!)?')
                logger.debug(f'user_id({message.from_user.id}) | '
                             f'данные приняты: max_distance_to_center - {message.text}')
                bot.set_state(message.from_user.id, UserInfoForLowprice.number_of_hotels, message.chat.id)
    else:
        bot.send_message(message.from_user.id, 'Пожалуйста, введите число!')
        logger.warning(f'user_id({message.from_user.id}) | '
                       f'не корректные данные: max_distance_to_center - {message.text}')
