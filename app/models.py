# app/models.py
# app/models.py

# app/models.py
from . import db
from flask_login import UserMixin


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), default='user')


class MeetingRoom(db.Model):

    __tablename__ = 'meeting_rooms'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(512), nullable=False)
    area = db.Column(db.Integer, nullable=False)  # Площадь
    internet_speed = db.Column(db.Integer, nullable=False)  # Скорость интернета
    capacity = db.Column(db.Integer, nullable=False)  # Вместимость
    floor = db.Column(db.Integer, nullable=False)  # Этаж
    photo_url = db.Column(db.String(512), nullable=False)  # Фото URL
    description = db.Column(db.String(1024), nullable=True)  # Описание

    def __repr__(self):
        return f"<MeetingRoom {self.name}>"
