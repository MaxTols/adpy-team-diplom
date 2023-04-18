import sqlalchemy
from sqlalchemy.orm import sessionmaker
from sqlalchemy import func

import os
from dotenv import load_dotenv

from DataBase.database_table import create_tables, Users, Photos, Favorites, Black

load_dotenv()


DSN = (
    f'postgresql://{os.getenv("LOGIN")}:{os.getenv("PASSWORD")}@'
    f'{os.getenv("SERVER")}:{os.getenv("PORT")}/{os.getenv("DB_NAME")}'
)
engine = sqlalchemy.create_engine(DSN)
create_tables(engine)

Session = sessionmaker(bind=engine)
session = Session()


def add_user(user_id, first_name, last_name):
    session.add(Users(user_id=user_id, first_name=first_name, last_name=last_name))
    session.commit()
    session.close()


def add_photo(photo_id, count_of_like, user_id):
    session.add(Photos(photo_id=photo_id, count_of_like=count_of_like, user_id=user_id))
    session.commit()
    session.close()


def add_favorite(user_id, first_name, last_name):
    session.add(Favorites(user_id=user_id, first_name=first_name, last_name=last_name))
    session.commit()
    session.close()


def get_random():
    random_id = session.query(Users).order_by(func.random()).first()
    return random_id.user_id, random_id.first_name, random_id.last_name


def favorites_list():
    favorite = session.query(
        Favorites.user_id, Favorites.first_name, Favorites.last_name
    ).all()
    return favorite


def add_black(user_id, first_name, last_name):
    session.add(Black(user_id=user_id, first_name=first_name, last_name=last_name))
    session.commit()
    session.close()


def del_user(user_id):
    session.query(Favorites).filter(Favorites.user_id == f"{user_id}").delete()
    session.query(Photos).filter(Photos.user_id == f"{user_id}").delete()
    session.query(Users).filter(Users.user_id == f"{user_id}").delete()
    session.commit()
