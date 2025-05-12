from flask_restful import Resource, reqparse
from flask import abort
from datetime import datetime
from app import db
from app.models import Booking
from flask_login import current_user

# Кастомная функция для парсинга ISO 8601 даты с 'Z' в конце
def iso_date_parser(date_string):
    # Убираем 'Z' в конце строки, если он есть
    if date_string.endswith('Z'):
        date_string = date_string[:-1]
    return datetime.fromisoformat(date_string)

# Обновляем парсер, чтобы использовать эту функцию
parser = reqparse.RequestParser()
parser.add_argument('object_id', type=int, required=True)
parser.add_argument('user_id', type=int, required=True)
parser.add_argument('start_date', type=iso_date_parser, required=True)
parser.add_argument('end_date', type=iso_date_parser, required=True)

class BookingListResource(Resource):
    def get(self):
        bookings = Booking.query.all()
        return [b.to_dict() for b in bookings], 200

    def post(self):
        args = parser.parse_args()
        start, end = args['start_date'], args['end_date']

        # Проверка: дата начала должна быть в будущем
        if start < datetime.now():
            abort(400, "Start date must be in the future")
        # Проверка: дата начала должна быть раньше даты конца
        if start >= end:
            abort(400, "Start date must be before end date")

        # Проверка на конфликты по объекту
        conflicts_object = Booking.query.filter(
            Booking.object_id == args['object_id'],
            Booking.start_date < end,
            Booking.end_date > start
        ).all()

        if conflicts_object:
            abort(409, "Room is already booked for this time")

        # Проверка на конфликты по пользователю
        conflicts_user = Booking.query.filter(
            Booking.user_id == args['user_id'],
            Booking.start_date < end,
            Booking.end_date > start
        ).all()

        if conflicts_user:
            abort(409, "User has a conflicting booking")

        # Создание нового бронирования
        booking = Booking(**args)
        db.session.add(booking)
        db.session.commit()
        return booking.to_dict(), 201

class BookingResource(Resource):
    def get(self, booking_id):
        booking = Booking.query.get_or_404(booking_id)
        return booking.to_dict(), 200



    def put(self, booking_id):
        booking = Booking.query.get_or_404(booking_id)
        args = parser.parse_args()

        # Проверка: дата начала должна быть раньше даты конца
        if args['start_date'] >= args['end_date']:
            abort(400, "Start date must be before end date")

        # Проверка на конфликты
        conflicts = Booking.query.filter(
            Booking.object_id == args['object_id'],
            Booking.id != booking_id,
            Booking.start_date < args['end_date'],
            Booking.end_date > args['start_date']
        ).all()

        if conflicts:
            abort(409, "Conflicting booking exists")

        # Обновление данных бронирования
        for key, value in args.items():
            setattr(booking, key, value)
        db.session.commit()
        return booking.to_dict(), 200

    def delete(self, booking_id):
        booking = Booking.query.get_or_404(booking_id)
        db.session.delete(booking)
        db.session.commit()
        return '', 204

class BookingByObjectResource(Resource):
    def get(self, object_id):
        bookings = Booking.query.filter_by(object_id=object_id).order_by(Booking.start_date).all()
        return [b.to_dict() for b in bookings], 200
