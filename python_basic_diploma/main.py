import telebot


bot = telebot.TeleBot('1876464698:AAFTukoK361uiDmYHKFlqBPkKvA5WvrY3aM')


@bot.message_handler(commands=['help'])
def hint(message):
    bot.reply_to(message, 'Вы можете управлять ботом, посылая следующие команды:\n'
                          '/help — помощь по командам бота\n'
                          '/lowprice — вывод самых дешёвых отелей в городе\n'
                          '/highprice — вывод самых дорогих отелей в городе\n'
                          '/bestdeal — вывод отелей, наиболее подходящих по цене и расположению от центра\n'
                          '/history — вывод истории поиска отелей')


@bot.message_handler(commands=['hello-world'])
def response_to_the_command_hello_world(message):
    bot.reply_to(message, 'Привет мир!!! Я родился 7.09.2021...')


@bot.message_handler(content_types=['text'])
def get_text_message(message):
    if message.text == 'Привет':
        bot.reply_to(message, 'Привет, меня зовут ТелеБот')
    else:
        bot.reply_to(message, 'Не понял...')



bot.polling(none_stop=True, interval=0)