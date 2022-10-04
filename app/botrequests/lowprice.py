import telebot
from decouple import config  # Импортируем переменные среды, хранящиеся в файле .env
#
TOKEN = config('TOKEN')  # Получаем токен из переменной среды
bot = telebot.TeleBot(TOKEN)  # Создаем бота (передаем токен)


import json
import requests
import re
from telebot.types import InputMediaPhoto

# 3 и 4 этапы можно объединить (2 раза пробегаюсь по отелям!!!!)
# Обработка ошибок и неверного ввода пользователем


class InputData:
    def __init__(self, city=None, number_or_results=3, output_photo=False, count_photo=False):
        self.city = city
        self.number_or_results = number_or_results
        self.output_of_photo = output_photo
        self.number_of_photo = count_photo


# city = ''
lot_result = str(0)  # Исправить!!!
photo_output = False  # См.!!!!!
lot_photo = 0
database = dict()  # База для сохранения результата


def lowprice(message):
    bot.send_message(message.from_user.id, 'Укажите город для поиска')
    city = message.text
    print(f'Выбран город: {city}')
    bot.register_next_step_handler(message, number_of_result)

def number_of_result(message):
    bot.send_message(message.from_user.id, 'Кол-во отелей в выдаче (не более 25!)')
    number_or_results = message.text
    print(f'Выбрано кол-во отелей: {number_or_results}')
    bot.register_next_step_handler(message, output_of_photo)

def output_of_photo(message):
    bot.send_message(message.from_user.id, 'Выводить фото отелей?')
    if message.text == 'Да' or message.text == 'да':
        print('Выбрано выводить фото')
        bot.register_next_step_handler(message, number_of_photo)
    else:
        bot.reply_to(message, 'Одну секунду, ищу подходящие варианты...')

def number_of_photo(message):
    bot.send_message(message.from_user.id, 'Кол-во фото в выдаче?')
    lot_photos = message.text
    print(f'Выбрано кол-во фото: {lot_photos}')
    bot.reply_to(message, 'Одну секунду, ищу подходящие варианты...')



# -----------------------------------------------------------------------------------
# Функция поиска подходящих вариантов
# def search_for_options(message):
#     global city, database
#
#     # Создаем словарь, в котором будем хранить все данные по поиску
#     database['Город'] = city
#
#     #print(database)
#
#     # 1 ЭТАП - По городу находим id локации
#     url = 'https://hotels4.p.rapidapi.com/locations/search'
#
#     querystring = {"query": city, "locale": "ru_RU"}
#
#     headers = {
#         'x-rapidapi-host': "hotels4.p.rapidapi.com",
#         'x-rapidapi-key': "dcd030f4dfmshc870424c587b149p142e84jsn6ec73810833f"
#     }
#
#     response_city = requests.request("GET", url, headers=headers, params=querystring)
#
#
#     #print('Ответ на запрос города:', response_city.text)
#
#     # with open('result_Moscow.json', 'r', encoding='utf-8') as file:
#     #     result = file.read()
#     #     places_id = re.search(r'CITY_GROUP".*?(\d{7}).*?CITY', result).group(1)
#
#     # Находим id локации
#     places_id = re.search(r'CITY_GROUP".*?"destinationId":"(\d*?)".*?CITY', response_city.text.replace('\'', '\"')).group(1)
#
#     #print('id места:', places_id)
#
#
#     # Для наглядного вывода результата
#     with open('result_Moscow.json', 'w', encoding='utf-8') as file:
#         json.dump(json.loads(response_city.text), file, ensure_ascii=False, indent=4)
#         file.write(f'\nid места: {places_id}')
#
#     # 2 ЭТАП - Собираем id отелей
#     url = "https://hotels4.p.rapidapi.com/properties/list"
#
#     querystring = {f"destinationId":f"{places_id}","pageNumber":"1","pageSize":lot_result,"checkIn":"2020-01-08","checkOut":"2020-01-15","adults1":"1","sortOrder":"PRICE","locale":"ru_RU","currency":"RUB"}
#
#     headers = {
#         'x-rapidapi-host': "hotels4.p.rapidapi.com",
#         'x-rapidapi-key': "dcd030f4dfmshc870424c587b149p142e84jsn6ec73810833f"
#     }
#
#     response_hotels = requests.request("GET", url, headers=headers, params=querystring)
#
#
#
#     #print('Ответ на запрос отелей: ', response_hotels.text)
#
#     # with open('result_hotels_in_Moscow.json', 'r', encoding='utf-8') as file:
#     #     result = file.read()
#     # Получаем список id отелей (25 шт.)
#
#     # Данные по найденным отелям
#     hotels_id_list = re.findall(r'"id":(\d*),"name"', response_hotels.text)[:int(lot_result)] # id отелей
#     name_hotel_list = re.findall(r'"name":"(.*?)","starRating"', response_hotels.text)[:int(lot_result)] # Названия отелей
#     # address_hotels_list = re.findall(r'"streetAddress":"(.*?)","extendedAddress"', response_hotels.text)[:int(lot_result)] # Адреса
#     address_hotels_list = list() # Адреса
#     distance_to_the_centre_list = re.findall(r'"label":"Центр города","distance":"(.*?)"', response_hotels.text)[:int(lot_result)] # Расстояние до центра
#     price_list = re.findall(r'"exactCurrent":(\d{1,10}.\d{1,2})', response_hotels.text)[:int(lot_result)] # Цена
#
#     #Для наглядного вывода результата
#     with open('result_hotels_in_Moscow.json', 'w', encoding='utf-8') as file:
#         #file.write(response.text)
#         json.dump(json.loads(response_hotels.text), file, ensure_ascii=False, indent=4)
#         file.write(f'\nid отелей: {str(hotels_id_list)}')
#         file.write(f'Названия отелей: {str(name_hotel_list)}')
#         file.write(f'Список адресов (пока пуст): {str(address_hotels_list)}')
#         file.write(f'Расстояние до центра: {str(distance_to_the_centre_list)}')
#         file.write(f'Цены: {str(price_list)}')
#
#     # 3 ЭТАП - подробная инфа по каждому отелю (т.к. не всегда выдает точный адрес во 2 этапе и программа ломается)
#     for i_hotel in hotels_id_list:
#         url = "https://hotels4.p.rapidapi.com/properties/get-details"
#
#         querystring = {"id": i_hotel, "checkIn": "2020-01-08", "checkOut": "2020-01-15", "adults1": "1",
#                        "currency": "RUB", "locale": "ru_RU"}
#
#         headers = {
#             'x-rapidapi-host': "hotels4.p.rapidapi.com",
#             'x-rapidapi-key': "dcd030f4dfmshc870424c587b149p142e84jsn6ec73810833f"
#         }
#
#         response_hotel = requests.request("GET", url, headers=headers, params=querystring)
#
#         #print('Ответ на запрос данных об отеле: ', response_hotel.text)
#
#         # Находим адрес отеля и добавляем в список адресов
#         address_hotel = re.search(r'"fullAddress":"(.*?)"}', response_hotel.text).group(1) # Адреса
#         address_hotels_list.append(address_hotel)
#
#         # print('\nid отелей:', hotels_id_list)
#         # print('Название отелей:', name_hotel_list)
#         # print('Адреса:', address_hotels_list)
#         # print('Расстояние до центра:', distance_to_the_centre_list)
#         # print('Цены:', price_list)
#         # print('Кол-во отелей:', len(hotels_id_list))
#
#         #hotels_id = ['1576233280', '1770270976', '1576222336', '1081948768', '1504049216', '927001696', '1219660160', '615475200', '927058496', '925846720', '938119456', '690694400', '665249', '702598', '798431136']
#
#
#         #Для наглядного вывода результата
#         with open('result_in_every_hostel.json', 'w', encoding='utf-8') as file:
#             #file.write(response.text)
#             json.dump(json.loads(response_hotel.text), file, ensure_ascii=False, indent=4)
#             file.write(f'\nАдреса отелей (заполненный список): {str(address_hotels_list)}')
#
#         database['Отели'] = list()
#
#     if photo_output == True:
#         # 4 ЭТАП - Пробегаемся по id отелям и запрашиваем фото каждого
#         url = "https://hotels4.p.rapidapi.com/properties/get-hotel-photos"
#
#         headers = {
#             'x-rapidapi-host': "hotels4.p.rapidapi.com",
#             'x-rapidapi-key': "dcd030f4dfmshc870424c587b149p142e84jsn6ec73810833f"
#         }
#
#         all_photo = list()
#
#         for i_id_hotel in hotels_id_list:
#             querystring = {"id": i_id_hotel}
#             response_photo = requests.request("GET", url, headers=headers, params=querystring)
#
#             # Список с фото (кол-во указанное пользователем) для каждого отеля
#             list_hotel_photo = re.findall(r'(https://.*?_{size}.jpg)', response_photo.text)[:int(lot_photo)]
#
#             # list_photo = ['https://exp.cdn-hotels.com/hotels/50000000/49230000/49226100/49226040/4211c79f_{size}.jpg', 'https://exp.cdn-hotels.com/hotels/50000000/49230000/49226100/49226040/214620c4_{size}.jpg', 'https://exp.cdn-hotels.com/hotels/50000000/49230000/49226100/49226040/f658f250_{size}.jpg', 'https://exp.cdn-hotels.com/hotels/50000000/49230000/49226100/49226040/99efb280_{size}.jpg', 'https://exp.cdn-hotels.com/hotels/50000000/49230000/49226100/49226040/c1a90de1_{size}.jpg']
#
#             for i_url_photo in range(len(list_hotel_photo)):
#                 list_hotel_photo[i_url_photo] = list_hotel_photo[i_url_photo].replace('_{size}', '')
#
#             #print(f'Фото {i_id_hotel} отеля:', list_hotel_photo)
#
#             # Сохраняем в словарь id отеля и список с фото
#             all_photo.append(list_hotel_photo)
#
#             #Для наглядного вывода результата
#             with open('result_photo_in_every_hostel.json', 'w', encoding='utf-8') as file:
#                 #file.write(response.text)
#                 json.dump(json.loads(response_photo.text), file, ensure_ascii=False, indent=4)
#                 file.write(f'\nФото: {str(all_photo)}')
#
#             # print(list_photo)
#             # print('Кол-во фото:', len(list_photo))
#
#
#
#     bot.send_message(message.from_user.id, '*Результаты*:', parse_mode='MarkdownV2')
#     for i_elem in range(int(lot_result)):
#         data_hostel = dict()
#         data_hostel['Название отеля'] = name_hotel_list[i_elem]
#         data_hostel['Адрес'] = address_hotels_list[i_elem]
#         data_hostel['Расстояние до центра'] = distance_to_the_centre_list[i_elem]
#         data_hostel['Цена'] = '{price} руб'.format(price=price_list[i_elem])
#         if photo_output == True:
#             data_hostel['Фото'] = all_photo[i_elem]
#         database['Отели'].append(data_hostel)
#
#         #send_result(message, name_hotel=name_hotel_list[i_elem], address=address_hotels_list[i_elem], distance=distance_to_the_centre_list[i_elem], price=price_list[i_elem], photo=all_photo[i_elem])
#
#
#         bot.send_message(message.from_user.id, 'Название отеля: {name_hotel}\n'
#                                                'Адрес: {address}\n'
#                                                'Расстояние до центра: {distance}\n'
#                                                'Стоимость за сутки: {price} руб\n'.format(
#             name_hotel=name_hotel_list[i_elem],
#             address=address_hotels_list[i_elem],
#             distance=distance_to_the_centre_list[i_elem],
#             price=price_list[i_elem]
#         ))
#
#         if photo_output == True:
#             # Отправка фото
#             bot.send_message(message.from_user.id, '*Фотографии*:', parse_mode='MarkdownV2')
#             media = []
#             for i_photo in all_photo[i_elem]:
#                 media.append(InputMediaPhoto(i_photo))
#             bot.send_media_group(message.from_user.id, media)
#
#
#
#         # Записываем результат в файл
#         with open('total_result.json', 'w', encoding='utf-8') as file:
#             json.dump(database, file, ensure_ascii=False, indent=4)


    # В КОНЦЕ ФУНКЦИЯ БУДЕТ ВОЗВРАЩАТЬ СЛОВАРЬ С РЕЗУЛЬТАТАМИ ВЫДАЧИ!!!
    # return database



# bot.polling(none_stop=True, interval=0)