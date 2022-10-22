from sqlalchemy import Column, Integer, String, Float, create_engine, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base, relationship


engine = create_engine('sqlite:///hostels_db', connect_args={'check_same_thread': False})
Base = declarative_base()
Session = sessionmaker(bind=engine, autoflush=False)
session = Session()


class Locations(Base):
    """ Структурная таблица с сохранением локаций, их id и id их дочерних записей """
    __tablename__ = 'locations'

    # id локации - не может быть пустым, уникальное, автоматически НЕ заполняется
    id = Column(Integer, nullable=False, unique=True, primary_key=True, autoincrement=False)
    name = Column(String(200), nullable=False)  # Название локации
    location = Column(String(500), nullable=False)  # Местоположение

    hotels = relationship('Hotels', backref='locations')  # Связь с таблицей "Hotels"


class Hotels(Base):
    __tablename__ = 'hotels'

    id = Column(Integer, nullable=False, unique=True, primary_key=True, autoincrement=False)
    id_location = Column(Integer, ForeignKey('locations.id'))  # Внешний ключ на id локации
    name = Column(String(300), nullable=False)
    address = Column(String(500), nullable=True)
    distance_to_center = Column(String(100), nullable=True)
    price = Column(Float, nullable=True)

    photos = relationship('Photos', backref='hotels')  # Связь с таблицей "Photos"


class Photos(Base):
    __tablename__ = 'photos'

    id = Column(Integer, nullable=False, unique=True, primary_key=True, autoincrement=False)
    id_hotel = Column(Integer, ForeignKey('hotels.id'))  # Внешний ключ на id отеля
    path = Column(String, nullable=False)
    type = Column(String(50), nullable=False)  # room / hotel
