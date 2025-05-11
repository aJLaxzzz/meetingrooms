# app/services/meeting_room_generator.py

from app import db
from app.models import MeetingRoom
from random import randint
from datetime import datetime
from flask import current_app


class MeetingRoomGenerator:
    # Генерация данных для переговорных комнат
    def generate_meeting_rooms(self, count):
        rooms = []
        descriptions = [
            "Современная переговорная комната с мультимедийным оборудованием.",
            "Уютная комната для встреч с комфортной мебелью.",
            "Переговорная с панорамными окнами и отличным видом.",
            "Комната для переговоров с возможностью видеоконференций.",
            "Просторная комната для больших групп.",
            "Инновационная переговорная с интерактивной доской.",
            "Комната для переговоров с уютной атмосферой.",
            "Переговорная с возможностью настройки освещения.",
            "Комната для встреч с доступом к кофе-уголку.",
            "Стильная переговорная с современным дизайном."
        ]

        for i in range(count):
            room = MeetingRoom(
                name=f"Конференц-зал {i + 1}",
                area=randint(15, 100),  # Площадь комнаты от 15 до 100 м²
                internet_speed=randint(100, 500),  # Скорость интернета от 100 до 500 Мбит/с
                capacity=randint(6, 25),  # Вместимость от 6 до 25 человек
                floor=randint(1, 25),  # Этаж от 1 до 25
                photo_url=f"/{randint(1, 14)}.jpeg",  # Случайное фото
                description=descriptions[randint(0, len(descriptions) - 1)]  # Случайное описание
            )
            rooms.append(room)

        return rooms

    # Метод для заполнения базы данных
    def fill_database(self):
        rooms = self.generate_meeting_rooms(20)  # Генерируем 20 комнат
        with current_app.app_context():  # Используем контекст приложения
            db.session.add_all(rooms)  # Добавляем все комнаты
            db.session.commit()  # Подтверждаем изменения
