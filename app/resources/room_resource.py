from flask_restful import Resource, reqparse
from app.models import MeetingRoom
from app.db import db

# Обновленный парсер для POST запросов
parser = reqparse.RequestParser()
parser.add_argument('name', type=str, required=True, help='Name is required')
parser.add_argument('area', type=int, required=True, help='Area is required')  # Площадь
parser.add_argument('internet_speed', type=int, required=True, help='Internet speed is required')  # Скорость интернета
parser.add_argument('capacity', type=int, required=True, help='Capacity is required')  # Вместимость
parser.add_argument('floor', type=int, required=True, help='Floor is required')  # Этаж
parser.add_argument('photo_url', type=str, required=True, help='Photo URL is required')  # Фото URL
parser.add_argument('description', type=str, required=False)  # Описание (не обязательно)

class RoomListResource(Resource):
    def get(self):
        rooms = MeetingRoom.query.all()
        return [
            {
                "id": r.id,
                "name": r.name,
                "capacity": r.capacity,
                "area": r.area,
                "internet_speed": r.internet_speed,
                "floor": r.floor,
                "photo_url": r.photo_url,
                "description": r.description
            } for r in rooms
        ]

    def post(self):
        args = parser.parse_args()
        room = MeetingRoom(
            name=args['name'],
            area=args['area'],
            internet_speed=args['internet_speed'],
            capacity=args['capacity'],
            floor=args['floor'],
            photo_url=args['photo_url'],
            description=args.get('description')  # Описание может быть None
        )
        db.session.add(room)
        db.session.commit()
        return {
            "id": room.id,
            "name": room.name,
            "capacity": room.capacity,
            "area": room.area,
            "internet_speed": room.internet_speed,
            "floor": room.floor,
            "photo_url": room.photo_url,
            "description": room.description
        }, 201

class RoomResource(Resource):
    def delete(self, room_id):
        room = MeetingRoom.query.get(room_id)
        if not room:
            return {"error": "Not found"}, 404
        db.session.delete(room)
        db.session.commit()
        return {"message": "Deleted"}, 200
