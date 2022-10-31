# Структурировать вначале вызываемые модули, потом пакеты
from database.create_db import Association

from utils.request_for_api.get_location import city_markup
from database.create_data.create_history import create_new_history
from . import bestdeal  # Для доп.вопросов для команды bestdeal
from database.create_db import History, session
from telegram_bot_calendar import DetailedTelegramCalendar, LSTEP
import datetime
import time

from telebot.types import Message, InputMediaPhoto  # Для аннотации типов
from states.data_for_lowprice import UserInfoForLowprice
from utils.request_for_api.get_result import get_result
from loader import bot
from loguru import logger


# УДАЛИТЬ (ИСПОЛЬЗУЕТСЯ ДЛЯ ПРОВЕРКИ)
COMMAND = ''
TIMESTAMP_DATA_START = ''


@bot.message_handler(commands=['lowprice', 'highprice', 'bestdeal'])
def bot_lowprice(message: Message) -> None:
    """ Запрашиваем город для поиска """

    # УДАЛИТЬ (ПОДУАМТЬ КАК ПЕРЕДАВАТЬ НАЗВАНИЕ КОМАНДЫ В КОНТЕКСТЕ)
    global COMMAND, TIMESTAMP_DATA_START
    COMMAND = message.text  # Выполняемая команда
    TIMESTAMP_DATA_START = message.date  # Время выполнения команды в формате timestamp

    logger.info(f'Запуск сценария {COMMAND}')

    bot.send_message(message.from_user.id, 'Укажите город для поиска')
    # Присваиваем пользователю состояние (чтобы сработал следующий хендлер (шаг))
    bot.set_state(message.from_user.id, UserInfoForLowprice.city, message.chat.id)  # message.chat.id - не обязательно


@bot.message_handler(state=UserInfoForLowprice.city)
def city(message: Message):
    """ Уточняем локацию по найденным совпадениям """

    if message.text.isalpha():  # Если введены слова (ЛОКЦИИ С ДЕФИСОМ НЕ ПРОХОДЯТ ПРОВЕРКУ!!!)

        if message.text.lower() == 'стоп':
            bot.send_message(message.from_user.id, 'Возвращайтесь...')
            logger.warning(f'user_id({message.from_user.id}) | пользователь прекратил сценарий')

        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['location_name'] = message.text  # Сохраняем название локации
            logger.debug(f'user_id({message.from_user.id}) | данные сохранены: location_name - {message.text}')

            # Передаем в функцию текст от пользователя, получаем локации от API и возвращаем пользователю
            # варианты для уточнения локации в виде кнопок
            result_location = city_markup(message.text)

            if not result_location:
                logger.error('Локации НЕ получены')
                bot.send_message(message.from_user.id,
                                 'К сожалению, сервис по предоставлению предложений по отелям не отвечает. '
                                 'Попробуйте позже...')
            else:
                logger.info('Локации получены')
                bot.send_message(message.from_user.id,
                                 'Пожалуйста, уточните место из предложенных или введите другую локацию '
                                 '(или введите "Стоп" для остановки):',
                                  reply_markup=result_location)
    else:
        logger.warning(f'user_id({message.from_user.id}) | не корректные данные: {message.text}')
        bot.send_message(message.from_user.id, 'Название города может содержать только буквы!')


@bot.callback_query_handler(func=lambda call: not call.data.startswith('cbcal'))
def callback_for_city(call):
    """ Сохраняем точный id выбранной локации """

    # id локации из кнопки (в data сохраняется id локации той кнопки, по которой нажал пользователь)
    id_location = call.data

    # Сохраняем id выбранной локации
    with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
        data['city_id'] = id_location  # Сохраняем id локации
        logger.debug(f'user_id({call.from_user.id}) | данные сохранены: city_id - {id_location}')
        # ДОБАВИТЬ ОТОБРАЖЕНИЕ ВЫБРАННОЙ ЛОКАЦИИ!!!

    bot.send_message(call.from_user.id, f'Желаете выбрать дату заселения/выезда?')
    bot.set_state(call.from_user.id, UserInfoForLowprice.check_date, call.message.chat.id)


@bot.message_handler(state=UserInfoForLowprice.check_date)
def get_check_in_date(message: Message) -> None:
    """ Запрашиваем дату заселения """  # Изменить

    if message.text.isalpha():
        if message.text.lower() == 'да':
            bot.send_message(message.from_user.id, f'Выберите дату заселения...')
            # Создаем объект календаря - calendar и шаг - step, в котором поочередно будет выводиться год, месяц и дни
            calendar, step = DetailedTelegramCalendar(calendar_id=1, locale='ru').build()
            bot.send_message(message.from_user.id, f"Выберите год", reply_markup=calendar)

        elif message.text.lower() == 'нет':

            # Доп.вопросы для команды bestdeal
            if COMMAND == '/bestdeal':
                bot.send_message(message.from_user.id, f'Укажите диапазон цен')
                bot.send_message(message.from_user.id, f'Минимальная цена (в руб.)')
                bot.set_state(message.from_user.id, UserInfoForLowprice.min_price, message.chat.id)

            else:
                bot.send_message(message.from_user.id,
                                 'Хорошо. Сколько отелей показать в выдаче (не более 15!)?')
                bot.set_state(message.from_user.id, UserInfoForLowprice.number_of_hotels, message.chat.id)

    else:
        logger.warning(f'user_id({message.from_user.id}) | не корректные данные: {message.text}')
        bot.send_message(message.from_user.id, f'Пожалуйста, выберите "Да" или "Нет"!')


@bot.callback_query_handler(func=DetailedTelegramCalendar.func(calendar_id=1))
def callback_for_check_dates(call):
    """ Сохраняем выбор даты заселения """

    result, key, step = DetailedTelegramCalendar(calendar_id=1, locale='ru').process(call.data)

    if not result and key:
        if LSTEP[step] == 'month':
            bot.edit_message_text(f"Выберите месяц", call.message.chat.id, call.message.message_id,
                                  reply_markup=key)
        else:
            bot.edit_message_text(f"Выберите число", call.message.chat.id, call.message.message_id,
                                  reply_markup=key)
    elif result:
        if result < datetime.date.today():
            logger.warning(f'user_id({call.from_user.id}) | не корректные данные: {result} < {datetime.date.today()}')
            bot.edit_message_text(f"Выбранная дата не может быть раньше сегодняшней, повторите ввод",
                                  call.message.chat.id, call.message.message_id)

            calendar, step = DetailedTelegramCalendar(calendar_id=1, locale='ru').build()
            bot.send_message(call.from_user.id, f"Выберите год", reply_markup=calendar)
        else:
            # Сохраняем введенные пользователем данные
            with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
                data['check_in_date'] = result  # Сохраняем дату заселения
                logger.debug(f'user_id({call.from_user.id}) | данные сохранены: check_in_date - {result}')
                bot.edit_message_text(f"Выбрана дата заселения: *{result.strftime('%d.%m.%y')}*", call.message.chat.id,
                                          call.message.message_id, parse_mode='Markdown')

                bot.send_message(call.message.chat.id, f'Выберите дату выселения...')
                calendar, step = DetailedTelegramCalendar(calendar_id=2, locale='ru').build()
                bot.send_message(call.message.chat.id, f"Выберите год", reply_markup=calendar)


@bot.callback_query_handler(func=DetailedTelegramCalendar.func(calendar_id=2))
def callback_for_check_dates(call):
    """ Сохраняем выбор даты выселения """

    result, key, step = DetailedTelegramCalendar(calendar_id=2, locale='ru').process(call.data)

    if not result and key:
        if LSTEP[step] == 'month':
            bot.edit_message_text(f"Выберите месяц", call.message.chat.id, call.message.message_id,
                                  reply_markup=key)
        else:
            bot.edit_message_text(f"Выберите число", call.message.chat.id, call.message.message_id,
                                  reply_markup=key)
    elif result:
        with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
            if result <= data['check_in_date']:
                logger.warning(
                    f'user_id({call.from_user.id}) | не корректные данные: {result} < {datetime.date.today()} or '
                    f'{result} < {data["check_in_date"]}')

                bot.edit_message_text(f"Выбранная дата не может быть раньше или равна дате заселения, повторите ввод",
                                      call.message.chat.id, call.message.message_id)

                calendar, step = DetailedTelegramCalendar(calendar_id=2, locale='ru').build()
                bot.send_message(call.from_user.id, f"Выберите год", reply_markup=calendar)

            else:
                data['check_out_date'] = result  # Сохраняем дату выселения
                logger.debug(f'user_id({call.from_user.id}) | данные сохранены: check_out_date - {result}')
                bot.edit_message_text(f"Выбрана дата выселения: *{result.strftime('%d.%m.%y')}*", call.message.chat.id,
                                      call.message.message_id, parse_mode='Markdown')

                delta = data['check_out_date'] - data['check_in_date']
                data['count_night'] = delta.days
                logger.debug(f'Кол-во ночей: {data["count_night"]}')

                # Доп.вопросы для команды bestdeal
                if COMMAND == '/bestdeal':
                    bot.send_message(call.from_user.id, f'Укажите диапазон цен')
                    bot.set_state(call.from_user.id, UserInfoForLowprice.min_price, call.message.chat.id)

                else:
                    bot.send_message(call.from_user.id,
                                     'Запомнил. Сколько отелей показать в выдаче (не более 15!)?')

                    bot.set_state(call.from_user.id, UserInfoForLowprice.number_of_hotels, call.message.chat.id)


# Следующим шагом ловим отлавливаем состояние UserInfoForLowprice.number_of_hotels - предыдущий шаг
@bot.message_handler(state=UserInfoForLowprice.number_of_hotels)
def get_number_of_hotels(message: Message) -> None:
    """ Запрашиваем нужно ли выводить фото отелей """

    # Проверка на корректность входных данных
    if message.text.isdigit():
        logger.info(f'user_id({message.from_user.id}) | данные приняты: {message.text}')

        # Сохраняем введенные пользователем данные
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            if int(message.text) > 15:
                logger.warning(f'user_id({message.from_user.id}) | выбрано больше допустимого значения: {message.text}')
                count_hotels = 15
                bot.send_message(message.from_user.id, 'Будет выведено максимально допустимое кол-во отелей: 10')
            else:
                count_hotels = message.text

            data['number_of_hotels'] = count_hotels  # Сохраняем введенное пользователем число (не больше 25)

        logger.debug(f'user_id({message.from_user.id}) | данные сохранены: number_of_hotels - {count_hotels}')

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

    result = None  # Флаг

    if message.text.lower() == 'да':
        logger.info(f'user_id({message.from_user.id}) | выбрано вывод фото')
        result = True
        # Принимаем ответ и задаем новый вопрос
        bot.send_message(message.from_user.id, 'Ок. По сколько фотографий выводить к отелям (от 2 до 10)?')
        # Присваиваем пользователю состояние (чтобы сработал следующий хендлер (шаг))
        bot.set_state(message.from_user.id, UserInfoForLowprice.number_of_photos, message.chat.id)

    elif message.text.lower() == 'нет':
        result = False
        logger.info(f'user_id({message.from_user.id}) | выбрано не выводить фото')
        bot.send_message(message.from_user.id, 'Все понял, сейчас поищу варианты...')

    else:  # Если введен НЕ корректный ответ
        logger.warning(f'user_id({message.from_user.id}) | не корректные данные: {message.text}')
        bot.send_message(message.from_user.id, 'Пожалуйста, введите "Да" или "Нет"')

    # Сохраняем введенные пользователем данные
    if result is not None:
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['photos'] = result  # Сохраняем булевое значение (выводить или не выводить фото к отелям)
            logger.debug(f'user_id({message.from_user.id}) | данные сохранены: photos - {message.text}')

    # УДАЛИТЬ ПОСЛЕ
    if result is False:
        main_text = f'Будет произведен поиск по следующим данным: \n' \
                    f' - Город: {data["location_name"]}\n' \
                    f' - id локации: {data["city_id"]}\n' \
                    f' - Кол-во отелей: {data["number_of_hotels"]}\n' \
                    f' - Выводить фото: нет'

        bot.send_message(message.from_user.id, main_text)
        bot.send_message(message.from_user.id, 'Нажми кнопку для поиска')

        logger.info('Данные собраны, передача параметров для запроса к API')

        bot.register_next_step_handler(message, response_to_the_user)


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
            elif int(message.text) < 2:
                logger.warning(f'user_id({message.from_user.id}) | выбрано меньше допустимого значения: {message.text}')
                count_photos = 2
                bot.send_message(message.from_user.id, 'Будет выведено минимально допустимое кол-во фото: 2')
            else:
                count_photos = message.text

            data['number_of_photos'] = count_photos  # Сохраняем введенное пользователем число

        logger.debug(f'user_id({message.from_user.id}) | данные сохранены: number_of_photos - {count_photos}')

        bot.send_message(message.from_user.id, 'Все понял, сейчас поищу варианты...')

        # УДАЛИТЬ ПОСЛЕ
        main_text = f'Будет произведен поиск по следующим данным: \n' \
                    f' - Город: {data["location_name"]}\n' \
                    f' - id локации: {data["city_id"]}\n' \
                    f' - Кол-во отелей: {data["number_of_hotels"]}\n' \
                    f' - Выводить фото: да\n' \
                    f' - Кол-во выводимых фото: {data["number_of_photos"]}'

        bot.send_message(message.from_user.id, main_text)
        bot.send_message(message.from_user.id, 'Нажми кнопку для поиска')

        logger.info('Данные собраны, передача параметров для запроса к API')

        bot.register_next_step_handler(message, response_to_the_user)

    else:  # Если введены НЕ числа
        logger.warning(f'user_id({message.from_user.id}) | не корректные данные: {message.text}')
        bot.send_message(message.from_user.id, 'Пожалуйста, введите число')


# СДЕЛАТЬ ВЫЗОВ ФУНКЦИИ БЕЗ ДОП. НАЖАТИЯ КЛАВИШИ!!!
def response_to_the_user(message: Message):
    """ Возвращаем пользователю найденные ответы """

    bot.send_message(message.from_user.id, 'Ищем варианты, ожидайте...')

    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        try:
            check_in_date = data['check_in_date']
            check_out_date = data['check_out_date']
            count_night = int(data['count_night'])
        except KeyError:
            logger.warning('check_in_date, check_out_date, count_night отсутствуют')
            check_in_date, check_out_date, count_night = None, None, None

        try:
            number_of_photos = data["number_of_photos"]
        except KeyError:
            logger.warning('number_of_photos отсутствует')
            number_of_photos = None

        try:
            min_price = data['min_price']
            max_price = data['max_price']
            min_distance_to_center = data['min_distance_to_center']
            max_distance_to_center = data['max_distance_to_center']
        except KeyError:
            logger.warning('Диапазоны цен и расстояний отсутствуют')
            min_price, max_price, min_distance_to_center, max_distance_to_center = None, None, None, None

        result = get_result(
            command=COMMAND,
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
            logger.error('Данные не получены')
            bot.send_message(message.from_user.id, 'К сожалению, API не отвечает...')
        else:
            logger.info('Данные получены')

            if COMMAND == '/bestdeal':
                bot.send_message(message.from_user.id, 'Лучшие предложения по цене и расстоянию до центра '
                                                       '(цена в приоритете)')

            new_history = create_new_history(
                user_id=message.from_user.id,
                command=COMMAND,
                date_of_entry=datetime.datetime.fromtimestamp(float(TIMESTAMP_DATA_START))
            )

            for hotel in result:
                # Сохраняем историю запросов
                new_record = Association()
                new_record.hotel = hotel['object']
                new_history.hotels.append(new_record)  # Добавляем отель в историю

                data_for_hotel = f"*Отель:* {hotel['hotel']}\n" \
                                 f"*Адрес:* {hotel['address']}\n" \
                                 f"*Расстояние до центра:* {hotel['distance_to_center']} км\n"

                if count_night is None:
                    data_for_hotel += f"*Стоимость:* {hotel['price']} руб/сут\n"

                elif count_night is not None:
                    data_for_hotel += f"*Стоимость проживания:* \n" \
                                      f"        за ночь - {hotel['price']} руб.\n" \
                                      f"        с *{check_in_date.strftime('%d.%m.%Y')}* по " \
                                      f"*{check_out_date.strftime('%d.%m.%Y')}* - " \
                                      f"{int(hotel['price']) * count_night} руб.\n"

                data_for_hotel += f"*Ссылка на отель:* \n" \
                                  f"        https://www.hotels.com/ho{hotel['id']}\n"

                # Отправка результатов с фото
                if number_of_photos is not None:
                    # Указываем описание к отелю для 1 фото
                    media_group = [InputMediaPhoto(
                        hotel['photos'][0],
                        caption=data_for_hotel, parse_mode='Markdown'  # Для вывода жирного текста
                    )]

                    # Добавляем оставшиеся фото
                    for photo in hotel['photos'][1:11]:  # До 10 медиафайлов в одном сообщении
                        media_group.append(InputMediaPhoto(photo))

                    bot.send_media_group(message.from_user.id, media=media_group)
                    logger.info('Отправлены данные с фото')

                else:
                    bot.send_message(message.from_user.id, data_for_hotel, parse_mode='Markdown')
                    logger.info('Отправлены данные без фото')

            session.add(new_history)
            session.commit()
            logger.debug('id всех отелей успешно добавлены в историю')

            bot.delete_state(message.from_user.id, message.chat.id)  # Удаляем состояние (для запуска новых команд)

            logger.info('Все данные по отелям успешно собраны и отправлены пользователю')
