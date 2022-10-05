import telebot
from decouple import config  # Импортируем переменные среды, хранящиеся в файле .env
from telebot import types
from botrequests.lowprice import func_lowprice


TOKEN = config('TOKEN')  # Получаем токен из переменной среды
bot = telebot.TeleBot(TOKEN)  # Создаем бота (передаем токен)


# 1 вариант
# Вообще не работает
def register_handlers():
    bot.register_message_handler(func_lowprice, commands=['lowprice1'], admin=True, pass_bot=True)

register_handlers()


# 2 вариант
# Работает только 1 шаг (выбор города)
@bot.message_handler(commands=['lowprice2'])
def wrap_lowprice(message):
    print('Сработала команда lowprice')
    func_lowprice(message, bot)





@bot.message_handler(commands=['hello-world'])
def hello_world(message):
    bot.send_message(message.chat.id, 'Привет мир!!!')


@bot.message_handler(commands=['help'])  # Не работает
def hint(message):
    bot.send_message(message.chat.id, 'Вы можете управлять ботом, посылая следующие команды:\n'
                          '/help — помощь по командам бота\n'
                          '/lowprice — вывод самых дешёвых отелей в городе\n'
                          '/highprice — вывод самых дорогих отелей в городе\n'
                          '/bestdeal — вывод отелей, наиболее подходящих по цене и расположению от центра\n'
                          '/history — вывод истории поиска отелей')





# bot.message_handler(commands=['lowprice'])(lowprice)

#     bot.send_message(message.from_user.id, 'Укажите город для поиска')
#     bot.register_next_step_handler(message, choosing_a_city)
#
#
# def choosing_a_city(message):
#     global city
#     city = message.text
#     bot.send_message(message.from_user.id, 'Кол-во отелей в выдаче (не более 25!)')
#     bot.register_next_step_handler(message, number_of_result)
#
#
# def number_of_result(message):
#     global lot_result
#     lot_result = message.text
#     bot.send_message(message.from_user.id, 'Выводить фото отелей?')
#     bot.register_next_step_handler(message, output_of_photo)
#
#
# def output_of_photo(message):
#     global photo_output
#     if message.text == 'Да':
#         photo_output = True
#         bot.send_message(message.from_user.id, 'Кол-во фото в выдаче?')
#         bot.register_next_step_handler(message, number_of_photo)
#     else:
#         photo_output = False
#         bot.reply_to(message, 'Одну секунду, ищу подходящие варианты...')
#         # bot.register_next_step_handler(message, search_for_options)
#
#
# def number_of_photo(message):
#     global lot_photo
#     lot_photo = message.text
#     bot.send_message(message.from_user.id, 'Одну секунду, ищу подходящие варианты...')
#
#     bot.reply_to(message, 'Поиск будет произведен...')



# ВАЖНО: текст обрабатывается ПОЛСЕ команд!!!
# @bot.message_handler(content_types=['text'])
# def message_reply(message):
#     if message.text == 'Привет':
#         first_name = message.from_user.first_name
#         if first_name:
#             bot.send_message(message.chat.id, f'Привет, {first_name}!')
#         else:
#             bot.send_message(message.chat.id, 'Привет!')
#     else:
#         bot.reply_to(message, message.text)


# @bot.message_handler(commands=['button'])
# def button_message(message):
#     markup = types.ReplyKeyboardMarkup(resize_keyboard=True)  # Создаем клавиатуру
#     item1 = types.KeyboardButton('Кнопка')  # Создаем кнопку с текстом "Кнопка" внутри
#     markup.add(item1)  # Добавляем кнопку в клавиатуру
#     bot.send_message(message.chat.id, 'Выберите, что вам нужно...', reply_markup=markup)  # Отправялем сообщение с текстом и кнопкой







# @bot.message_handler(content_types=['text'])
# def get_text_message(message):
#     global city, lot_result, photo_output, lot_photo
#     if message.text == 'Привет':
#         bot.send_message(message.from_user.id, 'Привет, меня зовут ТелеБот')
#     elif message.text == 'Результат':
#         output_data(message)
#
#     # Вторая функция сразу запускается не передавая нужные данные!!!
#     elif message.text == '/lowprice':
#         first_input_data(message)
#         output_data(message)
#
#     elif message.text == '/highprice':
#         first_input_data(message)
#     elif message.text == '/bestdeal':
#         first_input_data(message)
#     else:
#         bot.send_message(message.from_user.id, 'Не понял...')



# 1 этап сбора данных для поиска (для lowprice и highprice)
# def first_input_data(message):
#     global switch
#     if message.text == '/bestdeal':
#         switch = True
#     bot.send_message(message.from_user.id, 'Укажите город для поиска')
#     bot.register_next_step_handler(message, choosing_a_city)

# def choosing_a_city(message):
#     global city
#     city = message.text
#     bot.send_message(message.from_user.id, 'Кол-во отелей в выдаче (не более 25!)')
#     bot.register_next_step_handler(message, number_of_result)

# def number_of_result(message):
#     global lot_result
#     lot_result = message.text
#     bot.send_message(message.from_user.id, 'Выводить фото отелей?')
#     bot.register_next_step_handler(message, output_of_photo)

# def output_of_photo(message):
#     global photo_output
#     if message.text == 'Да':
#         photo_output = True
#         bot.send_message(message.from_user.id, 'Кол-во фото в выдаче?')
#         bot.register_next_step_handler(message, number_of_photo)

# def number_of_photo(message):
#     global switch
#     global lot_photo
#     lot_photo = message.text
#     if switch == True:
#         bot.send_message(message.from_user.id, 'Укажите диапазон цен:\nМинимальная цена')
#         bot.register_next_step_handler(message, min_price_range)


# 2 этап сбора данных (для bestdeal)
# def min_price_range(message):
#     global min_price
#     min_price = message.text
#     bot.send_message(message.from_user.id, 'Максимальная цена')
#     bot.register_next_step_handler(message, max_price_range)

# def max_price_range(message):
#     global max_price
#     max_price = message.text
#     bot.send_message(message.from_user.id, 'Укажите диапазон расстояния, на котором находится отель от центра:\nМинимальное расстояние от центра')
#     bot.register_next_step_handler(message, min_distance_range)

# def min_distance_range(message):
#     global min_distance
#     min_distance = message.text
#     bot.send_message(message.from_user.id, 'Максимальное расстояние от центра')
#     bot.register_next_step_handler(message, max_distance_range)

# def max_distance_range(message):
#     global max_distance
#     max_distance = message.text


# Вывод результата
# def output_data(message):
#     global city, lot_result, photo_output, max_price, min_price, max_distance, min_distance
#     bot.send_message(message.from_user.id, 'Будет осуществлен поиск по следующим критериям:\n'
#                                            'Город: {city}\n'
#                                            'Кол-во результатов: {lot_result}\n'
#                                            'Вывод фото: {answer}\n'
#                                            'Диапазон цен: {meaning_price}\n'
#                                            'Диапазон расстояний: {meaning_distance}'.format(
#         city=city,
#         lot_result=lot_result,
#         answer='Да' if photo_output == True else 'Нет',
#         meaning_price='{min_price} - {max_price}'.format(min_price=min_price, max_price=max_price) if min_price != 0 else 'не указано',
#         meaning_distance='{min_distance} - {max_distance}'.format(min_distance=min_distance, max_distance=max_distance) if min_distance != 0 else 'не указано'
#     ))


if __name__ == '__main__':
    # bot.polling(none_stop=True, interval=0)
    bot.infinity_polling()


