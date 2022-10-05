# -*- coding: cp1251 -*-

import json
import telebot
import requests
import re
from collections import OrderedDict
from telebot.types import InputMediaPhoto



# Кавычки везде одинаковые!


bot = telebot.TeleBot('1876464698:AAFTukoK361uiDmYHKFlqBPkKvA5WvrY3aM')

@bot.message_handler(content_types=['text'])
def response_to_the_command_hello_world(message):
    if message.text == 'Результат':
        bot.send_message(message.from_user.id, 'Результаты:')
        with open('total_result.json', 'r', encoding='utf-8') as file:
            result = json.load(file)

            for i_hotel in result['Отели']:
                name_hotel = i_hotel['Название отеля']
                address = i_hotel['Адрес']
                distance = i_hotel['Расстояние до центра']
                price = i_hotel['Цена']
                photo_list = i_hotel['Фото']


                # #5 ЭТАП - Отправка результата поиска пользователю
                bot.send_message(message.from_user.id, 'Название отеля: {name_hotel}\n'
                                                       'Адрес: {address}\n'
                                                       'Расстояние до центра: {distance}\n'
                                                       'Стоимость за сутки: {price}\n'.format(
                    name_hotel=name_hotel,
                    address=address,
                    distance=distance,
                    price=price
                ))

                # Отправка фото
                bot.send_message(message.from_user.id, '*Фотографии*:', parse_mode='MarkdownV2')
                media = []
                for i_photo in photo_list:
                    media.append(InputMediaPhoto(i_photo))
                bot.send_media_group(message.from_user.id, media)


bot.polling(none_stop=True, interval=0)