from telebot.types import Message  # Для аннотации типов
from states.data_for_lowprice import UserInfoForLowprice
from utils.request_for_api.lowprice.low_get_result import get_result
from loader import bot
from loguru import logger  # Для логирования


@bot.message_handler(commands=['lowprice'])
def bot_lowprice(message: Message) -> None:
    """ Запрашиваем город для поиска """
    bot.send_message(message.from_user.id, 'Укажите город для поиска')
    # Присваиваем пользователю состояние (чтобы сработал следующий хендлер (шаг))
    bot.set_state(message.from_user.id, UserInfoForLowprice.city, message.chat.id)  # message.chat.id - не обязательно


# Следующим шагом ловим указанное состояние пользователя (UserInfoForLowprice.city)
@bot.message_handler(state=UserInfoForLowprice.city)
def get_city(message: Message) -> None:
    """ Запрашиваем кол-во выводимых отелей """
    # Проверка на корректность ввода данных пользователем

    # ВАЖНО: сделать так, чтобы города с дефисом проходили проверку!!!

    if message.text.isalpha():  # Если введены слова
        # Принимаем ответ и задаем новый вопрос
        bot.send_message(message.from_user.id, 'Запомнил. Сколько отелей показать в выдаче (не более 25!)?')
        logger.info(f'user_id({message.from_user.id}) | данные приняты: {message.text}')

        # Присваиваем пользователю состояние (чтобы сработал следующий хендлер (шаг))
        bot.set_state(message.from_user.id, UserInfoForLowprice.number_of_hotels, message.chat.id)

        # Сохраняем введенные пользователем данные
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['city'] = message.text  # Сохраняем указанный город
            logger.info(f'user_id({message.from_user.id}) | данные сохранены: {message.text}')

    else:  # Если введены числа
        logger.warning(f'user_id({message.from_user.id}) | не корректные данные: {message.text}')
        bot.send_message(message.from_user.id, 'Название города может содержать только буквы!')


# Следующим шагом ловим отлавливаем состояние UserInfoForLowprice.number_of_hotels - предыдущий шаг
@bot.message_handler(state=UserInfoForLowprice.number_of_hotels)
def get_number_of_hotels(message: Message) -> None:
    """ Запрашиваем нужно ли выводить фото отелей """
    # Проверка на корректность ввода данных пользователем
    if message.text.isdigit():  # Если введено число (СДЕЛАТЬ ПРОВЕРКУ НЕ БОЛЕЕ 25!!!)
        logger.info(f'user_id({message.from_user.id}) | данные приняты: {message.text}')
        bot.send_message(message.from_user.id, 'Хорошо. Нужно выводить фото отелей?')  # Принимаем ответ и задаем новый вопрос

        # Присваиваем пользователю состояние (чтобы сработал следующий хендлер (шаг))
        bot.set_state(message.from_user.id, UserInfoForLowprice.photos, message.chat.id)

        # Сохраняем введенные пользователем данные
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['number_of_hotels'] = message.text  # Сохраняем введенное пользователем число
            logger.info(f'user_id({message.from_user.id}) | данные сохранены: {message.text}')

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
        bot.send_message(message.from_user.id, 'Ок. По сколько фотографий выводить к отелям?')  # Принимаем ответ и задаем новый вопрос
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
                    f' - Город: {data["city"]}\n' \
                    f' - Кол-во отелей: {data["number_of_hotels"]}\n' \
                    f' - Выводить фото: нет'

        bot.send_message(message.from_user.id, main_text)

        # ВЫЗОВ ФУНКЦИИ ПОИСКА ВАРИАНТОВ!!!
        # При таком варианте при повторном вызове команды ошибка - TypeError: 'NoneType' object is not callable
        # bot.register_next_step_handler(message, get_result(
        #     location=data["city"],
        #     number_of_hotels=data["number_of_hotels"]
        # ))

        get_result(
            location=data["city"],
            number_of_hotels=data["number_of_hotels"]
        )

        # if not response:
        #     bot.send_message(message.from_user.id, 'К сожалению, сервер пока не доступен...')

        # Добавить кнопки с соседними районами (посмотреть варианты)


# Следующим шагом ловим отлавливаем состояние UserInfoForLowprice.number_of_photos - предыдущий шаг
@bot.message_handler(state=UserInfoForLowprice.number_of_photos)
def get_number_of_photos(message: Message) -> None:

    # Проверка на корректность ввода данных пользователем
    if message.text.isdigit():  # Если введено число
        logger.info(f'user_id({message.from_user.id}) | данные приняты: {message.text}')
        bot.send_message(message.from_user.id, 'Все понял, сейчас поищу варианты...')

        # Сохраняем введенные пользователем данные
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['number_of_photos'] = message.text  # Сохраняем введенное пользователем число
            logger.info(f'user_id({message.from_user.id}) | данные сохранены: {message.text}')

        # ПРОВЕРКА ДАННЫХ
        main_text = f'Будет произведен поиск по следующим данным: \n' \
                    f' - Город: {data["city"]}\n' \
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

        get_result(
            location=data["city"],
            number_of_hotels=data["number_of_hotels"],
            number_of_photos=data["number_of_photos"]
        )

        # if not response:
        #     bot.send_message(message.from_user.id, 'К сожалению, сервер пока не доступен...')

        # Добавить кнопки с соседними районами (посмотреть варианты)

    else:  # Если введены НЕ числа
        logger.warning(f'user_id({message.from_user.id}) | не корректные данные: {message.text}')
        bot.send_message(message.from_user.id, 'Пожалуйста, введите число')


# def response_to_the_user(message: Message):
#     """ Возвращаем пользователю найденные ответы """
#     bot.send_message(message.from_user.id, 'Одну секунду, ищу подходящие варианты...')
