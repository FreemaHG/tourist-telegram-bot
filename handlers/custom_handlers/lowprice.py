from utils.request_for_api.lowprice.low_get_location import get_id_location, city_markup

from telebot.types import Message  # Для аннотации типов
from states.data_for_lowprice import UserInfoForLowprice
from utils.request_for_api.lowprice.low_get_result import get_result
from loader import bot
from loguru import logger


@bot.message_handler(commands=['lowprice'])
def bot_lowprice(message: Message) -> None:
    """ Запрашиваем город для поиска """
    logger.info('Запуск сценария')
    bot.send_message(message.from_user.id, 'Укажите город для поиска')
    # Присваиваем пользователю состояние (чтобы сработал следующий хендлер (шаг))
    bot.set_state(message.from_user.id, UserInfoForLowprice.city, message.chat.id)  # message.chat.id - не обязательно


@bot.message_handler(state=UserInfoForLowprice.city)
def city(message: Message):
    """ Уточняем локацию по найденным совпадениям """

    if message.text.isalpha():  # Если введены слова

        if message.text == 'стоп':
            bot.send_message(message.from_user.id, 'Возвращайтесь...')
            logger.warning(f'user_id({message.from_user.id}) | пользователь прекратил сценарий')
            return False

        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['location_name'] = message.text  # Сохраняем id локации
            logger.info(f'user_id({message.from_user.id}) | введен город: {message.text}')
            bot.send_message(message.from_user.id,
                             'Пожалуйста, уточните место из предложенных или введите другую локацию '
                             '(или введите "стоп" для остановки):',
                              reply_markup=city_markup(message.text))  # Отправляем кнопки с вариантами

    else:
        logger.warning(f'user_id({message.from_user.id}) | не корректные данные: {message.text}')
        bot.send_message(message.from_user.id, 'Название города может содержать только буквы!')


@bot.callback_query_handler(func=lambda call: True)
def callback_for_city(call):
    """ Сохраняем точный id выбранной локации """

    id_location = call.data

    # Сохраняем id выбранной локации
    with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
        data['city_id'] = id_location  # Сохраняем id локации
        logger.info(f'user_id({call.from_user.id}) | данные сохранены: {id_location}')

    bot.send_message(call.from_user.id, 'Запомнил. Сколько отелей показать в выдаче (не более 25!)?')
    bot.set_state(call.from_user.id, UserInfoForLowprice.number_of_hotels, call.message.chat.id)


# Следующим шагом ловим отлавливаем состояние UserInfoForLowprice.number_of_hotels - предыдущий шаг
@bot.message_handler(state=UserInfoForLowprice.number_of_hotels)
def get_number_of_hotels(message: Message) -> None:
    """ Запрашиваем нужно ли выводить фото отелей """

    # Проверка на корректность ввода данных пользователем
    if message.text.isdigit():
        logger.info(f'user_id({message.from_user.id}) | данные приняты: {message.text}')

        # Сохраняем введенные пользователем данные
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            if int(message.text) > 25:
                logger.warning(f'user_id({message.from_user.id}) | выбрано больше допустимого значения: {message.text}')
                count_hotels = 25
                bot.send_message(message.from_user.id, 'Будет выведено максимально допустимое кол-во отелей: 25')
            else:
                count_hotels = message.text

            data['number_of_hotels'] = count_hotels  # Сохраняем введенное пользователем число

        logger.info(f'user_id({message.from_user.id}) | данные сохранены: {count_hotels}')

        # Задаем новый вопрос
        bot.send_message(message.from_user.id, 'Хорошо. Нужно выводить фото отелей?')

        # Присваиваем пользователю состояние (чтобы сработал следующий хендлер (шаг))
        bot.set_state(message.from_user.id, UserInfoForLowprice.photos, message.chat.id)

    else:  # Если введены НЕ числа
        bot.send_message(message.from_user.id, 'Пожалуйста, введите число (не более 25!)')
        logger.warning(f'user_id({message.from_user.id}) | не корректные данные: {message.text}')


# Следующим шагом ловим отлавливаем состояние UserInfoForLowprice.photos - предыдущий шаг
@bot.message_handler(state=UserInfoForLowprice.photos)
def get_photos(message: Message) -> None:
    """ Запрашиваем кол-во выводимых фото отелей """

    result = None

    # Проверка на корректность ввода данных пользователем
    if message.text.lower() == 'да':
        logger.info(f'user_id({message.from_user.id}) | выбрано вывод фото')
        result = True
        # Принимаем ответ и задаем новый вопрос
        bot.send_message(message.from_user.id, 'Ок. По сколько фотографий выводить к отелям (не более 10!)?')
        # Присваиваем пользователю состояние (чтобы сработал следующий хендлер (шаг))
        bot.set_state(message.from_user.id, UserInfoForLowprice.number_of_photos, message.chat.id)

    elif message.text.lower() == 'нет':
        result = False
        logger.info(f'user_id({message.from_user.id}) | выбрано не выводить фото')
        bot.send_message(message.from_user.id, 'Все понял, сейчас поищу варианты...')

    else:  # Если введен НЕ корректный ответ
        logger.warning(f'user_id({message.from_user.id}) | не корректные данные: {message.text}')
        bot.send_message(message.from_user.id, 'Пожалуйста, введите "Да" или "Нет"')

    # Сохраняем введенные пользователем данные (ВОЗМОЖНО СОХРАНИТЬ В СЛЕДУЮЩЕМ ШАГЕ!!!)
    if result is not None:
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['photos'] = result  # Сохраняем булевое значение (выводить или не выводить фото к отелям)
            logger.info(f'user_id({message.from_user.id}) | данные сохранены: {message.text}')

    if result is False:
        # ПРОВЕРКА ДАННЫХ
        main_text = f'Будет произведен поиск по следующим данным: \n' \
                    f' - Город: {data["location_name"]}\n' \
                    f' - id локации: {data["city_id"]}\n' \
                    f' - Кол-во отелей: {data["number_of_hotels"]}\n' \
                    f' - Выводить фото: нет'

        bot.send_message(message.from_user.id, main_text)

        # ВЫЗОВ ФУНКЦИИ ПОИСКА ВАРИАНТОВ!!!
        # При таком варианте при повторном вызове команды ошибка - TypeError: 'NoneType' object is not callable
        # bot.register_next_step_handler(message, get_result(
        #     location=data["city"],
        #     number_of_hotels=data["number_of_hotels"]
        # ))

        # ЗАПУСК СКРИПТА
        # get_result(
        #     location=data["city"],
        #     number_of_hotels=data["number_of_hotels"]
        # )

        # if not response:
        #     bot.send_message(message.from_user.id, 'К сожалению, сервер пока не доступен...')


# Следующим шагом ловим отлавливаем состояние UserInfoForLowprice.number_of_photos - предыдущий шаг
@bot.message_handler(state=UserInfoForLowprice.number_of_photos)
def get_number_of_photos(message: Message) -> None:

    # Проверка на корректность ввода данных пользователем
    if message.text.isdigit():  # Если введено число
        logger.info(f'user_id({message.from_user.id}) | данные приняты: {message.text}')

        # Сохраняем введенные пользователем данные
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            if int(message.text) > 10:
                logger.warning(f'user_id({message.from_user.id}) | выбрано больше допустимого значения: {message.text}')
                count_photos = 10
                bot.send_message(message.from_user.id, 'Будет выведено максимально допустимое кол-во фото: 10')
            else:
                count_photos = message.text

            data['number_of_photos'] = count_photos  # Сохраняем введенное пользователем число

        logger.info(f'user_id({message.from_user.id}) | данные сохранены: {count_photos}')

        bot.send_message(message.from_user.id, 'Все понял, сейчас поищу варианты...')

        # ПРОВЕРКА ДАННЫХ
        main_text = f'Будет произведен поиск по следующим данным: \n' \
                    f' - Город: {data["location_name"]}\n' \
                    f' - id локации: {data["city_id"]}\n' \
                    f' - Кол-во отелей: {data["number_of_hotels"]}\n' \
                    f' - Выводить фото: да\n' \
                    f' - Кол-во выводимых фото: {data["number_of_photos"]}'

        bot.send_message(message.from_user.id, main_text)

        # ВЫЗОВ ФУНКЦИИ ПОИСКА ВАРИАНТОВ!!!
        # При таком варианте при повторном вызове команды ошибка - TypeError: 'NoneType' object is not callable
        # bot.register_next_step_handler(message, get_result(
        #     location=data["city"],
        #     number_of_hotels=data["number_of_hotels"],
        #     number_of_photos=data["number_of_photos"]
        # ))

        # ЗАПУСК СКРИПТА
        # get_result(
        #     location=data["city"],
        #     number_of_hotels=data["number_of_hotels"],
        #     number_of_photos=data["number_of_photos"]
        # )

        # if not response:
        #     bot.send_message(message.from_user.id, 'К сожалению, сервер пока не доступен...')

        # Добавить кнопки с соседними районами (посмотреть варианты)

    else:  # Если введены НЕ числа
        logger.warning(f'user_id({message.from_user.id}) | не корректные данные: {message.text}')
        bot.send_message(message.from_user.id, 'Пожалуйста, введите число')


# def response_to_the_user(message: Message):
#     """ Возвращаем пользователю найденные ответы """
#     bot.send_message(message.from_user.id, 'Одну секунду, ищу подходящие варианты...')
