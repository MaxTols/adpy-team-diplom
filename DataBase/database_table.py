import sqlalchemy as sq
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Users(Base):
    __tablename__ = "users"

    user_id = sq.Column(sq.Integer, primary_key=True)
    first_name = sq.Column(sq.String(length=40))
    last_name = sq.Column(sq.String(length=40))

    def __str__(self):
        return f"{self.user_id}, {self.first_name}, {self.last_name}"


class Photos(Base):
    __tablename__ = "photos"

    id = sq.Column(sq.Integer, primary_key=True)
    photo_id = sq.Column(sq.Integer)
    count_of_like = sq.Column(sq.Integer)
    user_id = sq.Column(sq.Integer, sq.ForeignKey("users.user_id"), nullable=False)
    users = relationship(Users, backref="photo")

    def __str__(self):
        return f"{self.id}, {self.photo_id}, {self.like_count}, {self.user_id}"


class Favorites(Base):
    __tablename__ = "favorites"

    user_id = sq.Column(sq.Integer, primary_key=True)
    first_name = sq.Column(sq.String(length=40))
    last_name = sq.Column(sq.String(length=40))

    def __str__(self):
        return f"{self.user_id}, {self.first_name}, {self.last_name}"


def create_tables(engine):
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
