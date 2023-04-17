import sqlalchemy
from sqlalchemy.orm import sessionmaker
from sqlalchemy import func

from DataBase.database_table import create_tables, Users, Photos, Favorites


DSN = "postgresql://postgres:postgres@localhost:5432/project"
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
    favorite = session.query(Favorites.user_id, Favorites.first_name, Favorites.last_name).all()
    return favorite
