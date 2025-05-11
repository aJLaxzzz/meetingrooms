from flask import Flask
from flask_restful import Api
from app.db import db
from app.resources.room_resource import RoomListResource, RoomResource
from app.services.meeting_room_generator import MeetingRoomGenerator

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    # Создаем все таблицы (если они еще не созданы)
    with app.app_context():
        db.drop_all()  # Удаляем все таблицы
        db.create_all()

        # Генерация комнат при старте приложения
        generator = MeetingRoomGenerator()
        generator.fill_database()

    api = Api(app)
    api.add_resource(RoomListResource, '/api/rooms')
    api.add_resource(RoomResource, '/api/rooms/<int:room_id>')

    return app
