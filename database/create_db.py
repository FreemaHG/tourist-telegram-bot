from sqlalchemy import Column, Integer, String, Float, DateTime, create_engine, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base, relationship


engine = create_engine('sqlite:///hostels_db', connect_args={'check_same_thread': False})
Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()


class Locations(Base):
    """ Структурная таблица с сохранением локаций, их id и id их дочерних записей """
    __tablename__ = 'locations'

    # id локации - не может быть пустым, автоматически НЕ заполняется
    id = Column(Integer, nullable=False, primary_key=True, autoincrement=False)
    name = Column(String(200), nullable=False)  # Название локации
    location = Column(String(500), nullable=False)  # Местоположение

    hotels = relationship('Hotels', backref='locations')  # Связь с таблицей "Hotels"


class Hotels(Base):
    __tablename__ = 'hotels'

    id = Column(Integer, nullable=False, primary_key=True, autoincrement=False)
    id_location = Column(Integer, ForeignKey('locations.id'))  # Внешний ключ на id локации
    name = Column(String(300), nullable=False)
    address = Column(String(500), nullable=True)
    distance_to_center = Column(Float, nullable=True)
    price = Column(Integer, nullable=True)

    photos = relationship('Photos', backref='hotels')  # Связь с таблицей "Photos"
    history = relationship("Association", back_populates='hotel')


class Photos(Base):
    __tablename__ = 'photos'

    id = Column(Integer, nullable=False, primary_key=True, autoincrement=False)
    id_hotel = Column(Integer, ForeignKey('hotels.id'))  # Внешний ключ на id отеля
    url = Column(String, nullable=False)
    type = Column(String(50), nullable=False)  # room / hotel


# ПРОВЕРИТЬ НАСТРОЙКУ ТАБЛИЦ
class History(Base):
    __tablename__ = 'history'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    command = Column(String(100), nullable=False)
    date_of_entry = Column(DateTime, nullable=False)
    hotels = relationship("Association", back_populates='history')


class Association(Base):
    __tablename__ = "association_table"

    hotel_id = Column(ForeignKey("hotels.id"), primary_key=True)
    history_id = Column(ForeignKey("history.id"), primary_key=True)
    hotel = relationship("Hotels", back_populates="history")
    history = relationship("History", back_populates="hotels")
