# Стандартная библиотека
import datetime
import time

# Сторонние библиотеки
from telebot.types import Message, InputMediaPhoto  # Аннотация типов
from telegram_bot_calendar import DetailedTelegramCalendar, LSTEP  # Выбор дат заселения/выселения
from loader import bot
from loguru import logger

# Внутренние модули
from database.create_db import Association
from database.create_data.create_history import create_new_history
from database.create_db import session
from utils.request_for_api.get_location import city_markup
from utils.request_for_api.get_result import get_result
from states.data_for_lowprice import UserInfoForLowprice
from handlers.custom_handlers import bestdeal  # Для доп.вопросов для команды bestdeal


@bot.message_handler(commands=['lowprice', 'highprice', 'bestdeal'])
def bot_lowprice(message: Message) -> None:
    """ Запрашиваем город для поиска """

    user_id = message.from_user.id
    chat_id = message.chat.id

    bot.send_message(user_id, 'Укажите город для поиска')
    # Присваиваем пользователю состояние (чтобы сработал следующий хендлер (шаг))
    bot.set_state(user_id, UserInfoForLowprice.city, chat_id)  # message.chat.id - не обязательно

    with bot.retrieve_data(user_id, chat_id) as data:
        data['command'] = message.text  # Выполняемая команда
        data['timestamp_data_start'] = message.date  # Время выполнения команды в формате timestamp
        logger.info(f'Запуск сценария {data["command"]}')


@bot.message_handler(state=UserInfoForLowprice.city)
def city(message: Message):
    """ Уточняем локацию по найденным совпадениям """

    user_id = message.from_user.id

    if message.text.isalpha():  # Если введены слова (ЛОКЦИИ С ДЕФИСОМ НЕ ПРОХОДЯТ ПРОВЕРКУ!!!)

        if message.text.lower() == 'стоп':
            bot.send_message(user_id, 'Возвращайтесь...')
            logger.warning(f'user_id({user_id}) | пользователь прекратил сценарий')

        with bot.retrieve_data(user_id, message.chat.id) as data:
            data['location_name'] = message.text.capitalize()  # Сохраняем название локации (1 буква заглавная)
            logger.debug(f'user_id({user_id}) | данные сохранены: location_name - {message.text}')

            # Передаем в функцию текст от пользователя, получаем локации от API и возвращаем пользователю
            # варианты для уточнения локации в виде кнопок
            result_location = city_markup(message.text)

            if not result_location:
                logger.error('Локации НЕ получены')
                bot.send_message(user_id, 'К сожалению, сервис по предоставлению предложений по отелям не отвечает. '
                                          'Попробуйте позже...')
            else:
                logger.info('Локации получены')
                bot.send_message(user_id, 'Пожалуйста, уточните место из предложенных или введите другую локацию '
                                          '(или введите "Стоп" для остановки):',
                                          reply_markup=result_location)
    else:
        logger.warning(f'user_id({user_id}) | не корректные данные: {message.text}')
        bot.send_message(user_id, 'Название города может содержать только буквы!')


@bot.callback_query_handler(func=lambda call: not call.data.startswith('cbcal'))
def callback_for_city(call):
    """ Сохраняем точный id выбранной локации """
    user_id = call.from_user.id
    chat_id = call.message.chat.id

    # id локации из кнопки (в data сохраняется id локации той кнопки, по которой нажал пользователь)
    id_location = call.data

    # Сохраняем id выбранной локации
    with bot.retrieve_data(user_id, chat_id) as data:
        data['city_id'] = id_location  # Сохраняем id локации
        logger.debug(f'user_id({user_id}) | данные сохранены: city_id - {id_location}')

    bot.send_message(user_id, f'Желаете выбрать дату заселения/выезда?')
    bot.set_state(user_id, UserInfoForLowprice.check_date, chat_id)


@bot.message_handler(state=UserInfoForLowprice.check_date)
def get_check_in_date(message: Message) -> None:
    """ Запрашиваем дату заселения / кол-во отелей в выдаче / минимальную стоимость """

    user_id = message.from_user.id
    chat_id = message.chat.id

    if message.text.isalpha():
        if message.text.lower() == 'да':
            bot.send_message(user_id, f'Выберите дату заселения...')
            # Создаем объект календаря - calendar и шаг - step, в котором поочередно будет выводиться год, месяц и дни
            calendar, step = DetailedTelegramCalendar(calendar_id=1, locale='ru').build()
            bot.send_message(user_id, f"Выберите год", reply_markup=calendar)

        elif message.text.lower() == 'нет':
            with bot.retrieve_data(user_id, chat_id) as data:
                # Доп.вопросы для команды bestdeal
                if data['command'] == '/bestdeal':
                    bot.send_message(user_id, f'Укажите диапазон цен')
                    bot.send_message(user_id, f'Минимальная цена (в руб.)')
                    bot.set_state(user_id, UserInfoForLowprice.min_price, chat_id)
                else:
                    bot.send_message(user_id,
                                     'Хорошо. Сколько отелей показать в выдаче (не более 15!)?')
                    bot.set_state(user_id, UserInfoForLowprice.number_of_hotels, chat_id)
        else:
            logger.warning(f'user_id({user_id}) | не корректные данные: {message.text}')
            bot.send_message(user_id, f'Пожалуйста, выберите "Да" или "Нет"!')
    else:
        logger.warning(f'user_id({user_id}) | не корректные данные: {message.text}')
        bot.send_message(user_id, f'Пожалуйста, выберите "Да" или "Нет"!')


@bot.callback_query_handler(func=DetailedTelegramCalendar.func(calendar_id=1))
def callback_for_check_dates(call):
    """ Сохраняем выбор даты заселения """

    user_id = call.from_user.id
    chat_id = call.message.chat.id
    message_id = call.message.message_id

    result, key, step = DetailedTelegramCalendar(calendar_id=1, locale='ru').process(call.data)

    if not result and key:
        if LSTEP[step] == 'month':
            bot.edit_message_text(f"Выберите месяц", chat_id, message_id, reply_markup=key)
        else:
            bot.edit_message_text(f"Выберите число", chat_id, message_id, reply_markup=key)

    elif result:
        if result < datetime.date.today():
            logger.warning(f'user_id({user_id}) | не корректные данные: {result} < {datetime.date.today()}')
            bot.edit_message_text(f"Выбранная дата не может быть раньше текущей! Повторите ввод.",
                                  chat_id, message_id)

            calendar, step = DetailedTelegramCalendar(calendar_id=1, locale='ru').build()
            bot.send_message(user_id, f"Выберите год", reply_markup=calendar)
        else:
            # Сохраняем введенные пользователем данные
            with bot.retrieve_data(user_id, chat_id) as data:
                data['check_in_date'] = result  # Сохраняем дату заселения
                logger.debug(f'user_id({user_id}) | данные сохранены: check_in_date - {result}')
                bot.edit_message_text(f"Выбрана дата заселения: *{result.strftime('%d.%m.%y')}*", chat_id,
                                      message_id, parse_mode='Markdown')

                bot.send_message(chat_id, f'Выберите дату выселения...')
                calendar, step = DetailedTelegramCalendar(calendar_id=2, locale='ru').build()
                bot.send_message(chat_id, f"Выберите год", reply_markup=calendar)


@bot.callback_query_handler(func=DetailedTelegramCalendar.func(calendar_id=2))
def callback_for_check_dates(call):
    """ Сохраняем выбор даты выселения """

    user_id = call.from_user.id
    chat_id = call.message.chat.id
    message_id = call.message.message_id

    result, key, step = DetailedTelegramCalendar(calendar_id=2, locale='ru').process(call.data)

    if not result and key:
        if LSTEP[step] == 'month':
            bot.edit_message_text(f"Выберите месяц", chat_id, message_id,
                                  reply_markup=key)
        else:
            bot.edit_message_text(f"Выберите число", chat_id, message_id,
                                  reply_markup=key)
    elif result:
        with bot.retrieve_data(user_id, chat_id) as data:
            if result <= data['check_in_date']:
                logger.warning(
                    f'user_id({user_id}) | не корректные данные: {result} < {datetime.date.today()} or '
                    f'{result} < {data["check_in_date"]}')

                bot.edit_message_text(f"Выбранная дата не может быть раньше или равна дате заселения! Повторите ввод.",
                                      chat_id, message_id)

                calendar, step = DetailedTelegramCalendar(calendar_id=2, locale='ru').build()
                bot.send_message(user_id, f"Выберите год", reply_markup=calendar)

            else:
                data['check_out_date'] = result  # Сохраняем дату выселения
                logger.debug(f'user_id({user_id}) | данные сохранены: check_out_date - {result}')
                bot.edit_message_text(f"Выбрана дата выселения: *{result.strftime('%d.%m.%y')}*", chat_id,
                                      message_id, parse_mode='Markdown')

                delta = data['check_out_date'] - data['check_in_date']
                data['count_night'] = delta.days
                logger.debug(f'Кол-во ночей: {data["count_night"]}')

                # Доп.вопросы для команды bestdeal
                if data['command'] == '/bestdeal':
                    bot.send_message(user_id, f'Укажите диапазон цен')
                    bot.send_message(user_id, f'Введите минимальную стоимость (в руб.)')
                    bot.set_state(user_id, UserInfoForLowprice.min_price, chat_id)
                else:
                    bot.send_message(user_id,
                                     'Запомнил. Сколько отелей показать в выдаче (не более 15!)?')

                    bot.set_state(user_id, UserInfoForLowprice.number_of_hotels, chat_id)


# Следующим шагом ловим отлавливаем состояние UserInfoForLowprice.number_of_hotels - предыдущий шаг
@bot.message_handler(state=UserInfoForLowprice.number_of_hotels)
def get_number_of_hotels(message: Message) -> None:
    """ Запрашиваем нужно ли выводить фото отелей """

    user_id = message.from_user.id
    chat_id = message.chat.id

    # Проверка на корректность входных данных
    if message.text.isdigit():
        logger.info(f'user_id({user_id}) | данные приняты: {message.text}')

        # Сохраняем введенные пользователем данные
        with bot.retrieve_data(user_id, chat_id) as data:
            if int(message.text) > 15:
                logger.warning(f'user_id({user_id}) | выбрано больше допустимого значения: {message.text}')
                count_hotels = 15
                bot.send_message(user_id, 'Будет выведено максимально допустимое кол-во отелей: 15')
            else:
                count_hotels = message.text

            data['number_of_hotels'] = count_hotels  # Сохраняем введенное пользователем число (не больше 15)

        logger.debug(f'user_id({user_id}) | данные сохранены: number_of_hotels - {count_hotels}')

        # Задаем новый вопрос
        bot.send_message(user_id, 'Хорошо. Нужно выводить фото отелей?')

        # Присваиваем пользователю состояние (чтобы сработал следующий хендлер (шаг))
        bot.set_state(user_id, UserInfoForLowprice.photos, chat_id)

    else:  # Если введены НЕ числа
        bot.send_message(user_id, 'Пожалуйста, введите число (не более 15!)')
        logger.warning(f'user_id({user_id}) | не корректные данные: {message.text}')


# Следующим шагом ловим отлавливаем состояние UserInfoForLowprice.photos - предыдущий шаг
@bot.message_handler(state=UserInfoForLowprice.photos)
def get_photos(message: Message) -> None:
    """ Запрашиваем кол-во выводимых фото отелей """

    user_id = message.from_user.id
    chat_id = message.chat.id

    result = None  # Флаг

    if message.text.lower() == 'да':
        logger.info(f'user_id({user_id}) | выбрано вывод фото')
        result = True
        # Принимаем ответ и задаем новый вопрос
        bot.send_message(user_id, 'Ок. По сколько фотографий выводить к отелям (от 2 до 10)?')
        # Присваиваем пользователю состояние (чтобы сработал следующий хендлер (шаг))
        bot.set_state(user_id, UserInfoForLowprice.number_of_photos, chat_id)

    elif message.text.lower() == 'нет':
        result = False
        logger.info(f'user_id({user_id}) | выбрано не выводить фото')
        bot.send_message(user_id, 'Все понял, сейчас поищу варианты...')

    else:  # Если введен НЕ корректный ответ
        logger.warning(f'user_id({user_id}) | не корректные данные: {message.text}')
        bot.send_message(user_id, 'Пожалуйста, введите "Да" или "Нет"')

    # Сохраняем введенные пользователем данные
    if result is not None:
        with bot.retrieve_data(user_id, chat_id) as data:
            data['photos'] = result  # Сохраняем булевое значение (выводить или не выводить фото к отелям)
            logger.debug(f'user_id({user_id}) | данные сохранены: photos - {message.text}')

    if result is False:
        response_to_user(message)  # Поиск предложений


# Следующим шагом ловим отлавливаем состояние UserInfoForLowprice.number_of_photos - предыдущий шаг
@bot.message_handler(state=UserInfoForLowprice.number_of_photos)
def get_number_of_photos(message: Message) -> None:

    user_id = message.from_user.id

    # Проверка на корректность ввода данных пользователем
    if message.text.isdigit():  # Если введено число
        logger.info(f'user_id({user_id}) | данные приняты: {message.text}')

        # Сохраняем введенные пользователем данные
        with bot.retrieve_data(user_id, message.chat.id) as data:
            if int(message.text) > 10:
                logger.warning(f'user_id({user_id}) | выбрано больше допустимого значения: {message.text}')
                count_photos = 10
                bot.send_message(user_id, 'Будет выведено максимально допустимое кол-во фото: 10')
            elif int(message.text) < 2:
                logger.warning(f'user_id({user_id}) | выбрано меньше допустимого значения: {message.text}')
                count_photos = 2
                bot.send_message(user_id, 'Будет выведено минимально допустимое кол-во фото: 2')
            else:
                count_photos = message.text

            data['number_of_photos'] = count_photos  # Сохраняем введенное пользователем число

        logger.debug(f'user_id({user_id}) | данные сохранены: number_of_photos - {count_photos}')
        response_to_user(message)  # Поиск предложений

    else:  # Если введены НЕ числа
        logger.warning(f'user_id({user_id}) | не корректные данные: {message.text}')
        bot.send_message(user_id, 'Пожалуйста, введите число')


def response_to_user(message: Message):
    """ Возвращаем найденные предложения """

    user_id = message.from_user.id
    chat_id = message.chat.id

    bot.send_message(user_id, 'Ищем варианты, ожидайте...')

    with bot.retrieve_data(user_id, chat_id) as data:
        try:
            check_in_date = data['check_in_date']
            check_out_date = data['check_out_date']
            count_night = int(data['count_night'])
        except KeyError:
            logger.warning('check_in_date, check_out_date, count_night отсутствуют')
            check_in_date, check_out_date, count_night = None, None, None

        try:
            min_price = data['min_price']
            max_price = data['max_price']
            min_distance_to_center = data['min_distance_to_center']
            max_distance_to_center = data['max_distance_to_center']
        except KeyError:
            logger.warning('Диапазоны цен и расстояний отсутствуют')
            min_price, max_price, min_distance_to_center, max_distance_to_center = None, None, None, None

        try:
            number_of_photos = data["number_of_photos"]
        except KeyError:
            logger.warning('number_of_photos отсутствует')
            number_of_photos = None

        result = get_result(
            command=data['command'],
            id_location=int(data["city_id"]),
            check_in_date=check_in_date,
            check_out_date=check_out_date,
            min_price=min_price,
            max_price=max_price,
            min_distance_to_center=min_distance_to_center,
            max_distance_to_center=max_distance_to_center,
            number_of_hotels=int(data["number_of_hotels"]),
            number_of_photos=number_of_photos
        )

        if result is False:
            logger.error('Данные по отелям не получены')
            if data['command'] == '/bestdeal':
                bot.send_message(user_id, 'К сожалению, предложения, соответствующие условиям, не найдены.'
                                          'Попробуйте ввести другие диапазоны цен и расстояний до центра')
            else:
                bot.send_message(user_id, 'К сожалению, API не отвечает...')
        else:
            logger.info('Данные получены')

            if data['command'] == '/bestdeal':
                flag = False
                bot.send_message(user_id, 'Лучшие предложения по цене и расстоянию до центра (цена в приоритете)')
            # Сохраняем историю запроса
            new_history = create_new_history(
                user_id=user_id,
                command=data['command'],
                date_of_entry=datetime.datetime.fromtimestamp(float(data['timestamp_data_start']))
            )

            for hotel in result:
                # Сохраняем историю запросов
                new_record = Association()
                new_record.hotel = hotel['object']
                new_history.hotels.append(new_record)  # Добавляем отель в историю

                address = hotel['object'].address if hotel['object'].address is not None else 'нет данных'
                distance_to_center = str(hotel['object'].distance_to_center) + \
                                     ' км' if hotel['object'].distance_to_center is not None else 'нет данных'
                price = hotel['object'].price

                data_for_hotel = f"*Отель:* [{hotel['object'].name}](https://www.hotels.com/ho{hotel['object'].id})\n" \
                                 f"*Адрес:* {address}\n" \
                                 f"*Расстояние до центра:* {distance_to_center}\n"

                if price is not None:
                    if count_night is None:
                        data_for_hotel += f"*Стоимость:* {price} руб/сут\n"
                    else:
                        data_for_hotel += f"*Стоимость проживания:* \n" \
                                          f"      - за ночь - {hotel['object'].price} руб.\n" \
                                          f"      - с *{check_in_date.strftime('%d.%m.%Y')}* по " \
                                          f"*{check_out_date.strftime('%d.%m.%Y')}* - " \
                                          f"{int(hotel['object'].price) * count_night} руб.\n"
                else:
                    data_for_hotel += f"*Стоимость:* нет данных\n"

                # Отправка результатов с фото
                if number_of_photos is not None:
                    if hotel['photos'] is None:
                        bot.send_message(user_id, data_for_hotel, parse_mode='Markdown')
                        bot.send_message(user_id, 'Извините, но для данного отеля нет фото...')
                        logger.info('Отправлены данные без фото')

                    else:
                        # Указываем описание к отелю для 1 фото
                        media_group = [InputMediaPhoto(
                            hotel['photos'][0],
                            caption=data_for_hotel, parse_mode='Markdown'  # Для вывода жирного текста
                        )]

                        # Добавляем оставшиеся фото
                        for photo in hotel['photos'][1:10]:  # До 10 медиафайлов в одном сообщении (доп.проверка)
                            media_group.append(InputMediaPhoto(photo))

                        bot.send_media_group(user_id, media=media_group)
                        logger.info('Отправлены данные с фото')
                else:
                    bot.send_message(user_id, data_for_hotel, parse_mode='Markdown')
                    logger.info('Отправлены данные без фото')

                # Проверка данных по отелю условиям поиска (для вывода сообщения в конце)
                if data['command'] == '/bestdeal' and flag is False \
                        and ((type(hotel['object'].distance_to_center) == float
                             and (float(min_distance_to_center) > hotel['object'].distance_to_center or hotel['object']
                                 .distance_to_center > float(max_distance_to_center)))
                             or (type(price) == int and (int(min_price) > price or price > int(max_price)))):
                    flag = True
                    logger.debug('Смена флага')

                # Задержка между сообщениями (для избежания 429 ошибки от TeleBot - слишком много запросов)
                time.sleep(0.3)

            if data['command'] == '/bestdeal' and flag is False:
                bot.send_message(user_id, f'*Найдено предложений, соответствующих условиям*: {len(result)}',
                                 parse_mode='Markdown')
            elif data['command'] == '/bestdeal' and flag is True:
                bot.send_message(user_id, '* не найдено результатов, соответствующих заданным условиям '
                                          'по цене и расстоянию до центра. '
                                          'Выведены все найденные предложения в указанной местности...')
            else:
                bot.send_message(user_id, f'*Найдено предложений*: {len(result)}', parse_mode='Markdown')

            session.add(new_history)
            session.commit()
            logger.debug('id всех отелей успешно добавлены в историю')

            logger.info('Все данные по отелям успешно собраны и отправлены пользователю')

    bot.delete_state(user_id, chat_id)  # Удаляем состояние (для запуска новых команд)
