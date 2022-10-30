from telebot.handler_backends import State, StatesGroup


# Описываем класс состояний пользователя при вводе данных для хендлера
class UserInfoForLowprice(StatesGroup):
    # Каждый вопрос должен быть объектом класса State
    city = State()  # Город
    check_date = State()  # Ввод дат заселения и выселения
    min_price = State()  # Диапазон цен (минимальная цена)
    max_price = State()  # Диапазон цен (максимальная цена)
    min_distance_to_center = State()  # Диапазон расстояний до центра (минимальное расстояние)
    max_distance_to_center = State()  # Диапазон расстояний до центра (максимальное расстояние)
    number_of_hotels = State()  # Кол-во отелей в выдаче (не более 25!)
    photos = State()  # Выводить фото отелей? (Да / Нет)
    number_of_photos = State()  # Кол-во фото в выдаче? (Если "Да")
