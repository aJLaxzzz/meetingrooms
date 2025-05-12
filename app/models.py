# app/models.py
# app/models.py

# app/models.py
from . import db
from flask_login import UserMixin


class User(db.Model, UserMixin):
    __tablename__ = 'users'

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


class Booking(db.Model):
    __tablename__ = 'bookings'

    id = db.Column(db.Integer, primary_key=True)
    object_id = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'object_id': self.object_id,
            'user_id': self.user_id,
            'start_date': self.start_date.isoformat(),
            'end_date': self.end_date.isoformat()
        }