from telebot.types import Message  # Для аннотации типов
from states.data_for_lowprice import UserInfoForLowprice
from loader import bot


# Возвращаем самые дешевые отели в городе
@bot.message_handler(commands=['lowprice'])
def bot_lowprice(message: Message) -> None:
    """ Запрашиваем город для поиска """
    bot.send_message(message.from_user.id, 'Укажите город для поиска')

    # city = message.text

    # Присваиваем пользователю состояние (чтобы сработал следующий хендлер (шаг))
    # message.chat.id - не обязательно
    bot.set_state(message.from_user.id, UserInfoForLowprice.city, message.chat.id)

    # print(f'Выбран город: {city}')
    # bot.register_next_step_handler(message, number_of_result)


# Следующим шагом ловим указанное состояние пользователя (UserInfoForLowprice.city)
@bot.message_handler(state=UserInfoForLowprice.city)
def get_city(message: Message) -> None:
    """ Запрашиваем кол-во выводимых отелей """
    # Проверка на корректность ввода данных пользователем
    if message.text.isalpha():  # Если введены слова
        bot.send_message(message.from_user.id, 'Запомнил. Сколько отелей показать в выдаче?')  # Принимаем ответ и задаем новый вопрос

        # Присваиваем пользователю состояние (чтобы сработал следующий хендлер (шаг))
        bot.set_state(message.from_user.id, UserInfoForLowprice.number_of_hotels, message.chat.id)

        # Сохраняем введенные пользователем данные
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['city'] = message.text  # Сохраняем указанный город

    else:  # Если введены числа
        bot.send_message(message.from_user.id, 'Название города может содержать только буквы!')


# Следующим шагом ловим отлавливаем состояние UserInfoForLowprice.number_of_hotels - предыдущий шаг
@bot.message_handler(state=UserInfoForLowprice.number_of_hotels)
def get_number_of_hotels(message: Message) -> None:
    """ Запрашиваем нужно ли выводить фото отелей """
    # Проверка на корректность ввода данных пользователем
    if message.text.isdigit():  # Если введено число (СДЕЛАТЬ ПРОВЕРКУ НЕ БОЛЕЕ 25!!!)
        bot.send_message(message.from_user.id, 'Хорошо. Нужно выводить фото отелей?')  # Принимаем ответ и задаем новый вопрос

        # Присваиваем пользователю состояние (чтобы сработал следующий хендлер (шаг))
        bot.set_state(message.from_user.id, UserInfoForLowprice.photos, message.chat.id)

        # Сохраняем введенные пользователем данные
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['number_of_hotels'] = message.text  # Сохраняем введенное пользователем число

    else:  # Если введены НЕ числа
        bot.send_message(message.from_user.id, 'Пожалуйста, введите число (не более 25!)')


# Следующим шагом ловим отлавливаем состояние UserInfoForLowprice.photos - предыдущий шаг
@bot.message_handler(state=UserInfoForLowprice.photos)
def get_photos(message: Message) -> None:
    """ Запрашиваем кол-во выводимых фото отелей """
    # Проверка на корректность ввода данных пользователем
    if message.text.isalpha():  # Если введено слово

        result = False

        if message.text.lower() == 'да':
            result = True
            bot.send_message(message.from_user.id, 'Ок. По сколько фотографий выводить к отелям?')  # Принимаем ответ и задаем новый вопрос
            # Присваиваем пользователю состояние (чтобы сработал следующий хендлер (шаг))
            bot.set_state(message.from_user.id, UserInfoForLowprice.number_of_photos, message.chat.id)

        elif message.text.lower() == 'нет':
            bot.send_message(message.from_user.id, 'Все понял, сейчас поищу варианты...')

        else:
            bot.send_message(message.from_user.id, 'Пожалуйста, введите "Да" или "Нет"')

        # Сохраняем введенные пользователем данные
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['photos'] = result  # Сохраняем булевое значение (выводить или не выводить фото к отелям)

    else:  # Если введено НЕ слово
        bot.send_message(message.from_user.id, 'Пожалуйста, введите "Да" или "Нет"')


# Следующим шагом ловим отлавливаем состояние UserInfoForLowprice.number_of_photos - предыдущий шаг
@bot.message_handler(state=UserInfoForLowprice.number_of_photos)
def get_number_of_photos(message: Message) -> None:

    # Проверка на корректность ввода данных пользователем
    if message.text.isdigit():  # Если введено число
        bot.send_message(message.from_user.id, 'Все понял, сейчас поищу варианты...')

        # Сохраняем введенные пользователем данные
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['number_of_photos'] = message.text  # Сохраняем введенное пользователем число

    else:  # Если введены НЕ числа
        bot.send_message(message.from_user.id, 'Пожалуйста, введите число')


# Запросили и сохранили все данные (остановился на 15:09!!!)
