from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Проверить, где именно создается БД
engine = create_engine('sqlite:///hostels_db', connect_args={'check_same_thread': False})
Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()


class Cities(Base):
    """ Структурная таблица с сохранением локаций, их id и их дочерних записей """
    __tablename__ = 'cities'

    # id локации - не может быть пустым, уникальное, автоматически НЕ заполняется
    id = Column(Integer, nullable=False, unique=True, primary_key=True, autoincrement=False)
    parent_id = Column(Integer, nullable=True)  # id родительской локации
    city = Column(String(200), nullable=False)  # Название локации
