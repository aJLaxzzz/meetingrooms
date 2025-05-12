from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from app.models import User, MeetingRoom, Booking
from app.extensions import db, bcrypt
from functools import wraps


auth_bp = Blueprint('auth', __name__, template_folder='templates')


def role_required(role):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not current_user.is_authenticated:
                return jsonify({"error": "Authentication required"}), 401
            if current_user.role != role:
                return jsonify({"error": "Access forbidden: role required"}), 403
            return func(*args, **kwargs)
        return wrapper
    return decorator

# --- API Routes ---

@auth_bp.route('/api/register', methods=['POST'])
def api_register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    role = data.get('role', 'user')

    if not username or not password:
        return jsonify({'error': 'Username and password required'}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({'error': 'User already exists'}), 400

    password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    user = User(username=username, password_hash=password_hash, role=role)
    db.session.add(user)
    db.session.commit()

    return jsonify({'message': 'Registration successful'}), 201

@auth_bp.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username).first()
    if user and bcrypt.check_password_hash(user.password_hash, password):
        login_user(user)
        return jsonify({'message': 'Login successful'})
    return jsonify({'error': 'Invalid credentials'}), 401

@auth_bp.route('/api/logout', methods=['POST'])
@login_required
def api_logout():
    logout_user()
    return jsonify({'message': 'Logout successful'})


# --- HTML Routes ---
from flask_login import login_user

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        role = request.form.get('role', 'user')

        if not username or not password:
            flash('Имя пользователя и пароль обязательны')
            return redirect(url_for('auth.register'))

        if User.query.filter_by(username=username).first():
            flash('Пользователь уже существует')
            return redirect(url_for('auth.register'))

        password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
        user = User(username=username, password_hash=password_hash, role=role)
        db.session.add(user)
        db.session.commit()

        # Логиним пользователя сразу после регистрации
        login_user(user)

        flash('Регистрация прошла успешно. Войдите в систему.')
        print("Регистрация прошла успешно. Войдите в систему.")

        # Перенаправляем на страницу с комнатами
        return redirect(url_for('auth.rooms'))

    return render_template('register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()
        if user and bcrypt.check_password_hash(user.password_hash, password):
            login_user(user)
            print("Авторизация прошла успешно")

            # Проверка роли пользователя
            if user.role == 'admin':
                return redirect('/admin')  # Для админа перенаправляем на /add
            else:
                return redirect('/rooms')  # Для обычного пользователя перенаправляем на /rooms

        flash('Неверные учетные данные')
        print("Неверные учетные данные")

    return render_template('login.html')



@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Вы вышли из системы')
    return redirect(url_for('auth.login'))

@auth_bp.route('/')
def index():
    return redirect(url_for('auth.login'))

@auth_bp.route('/rooms')
@login_required
def rooms():
    # Делаем запрос к API, чтобы получить список комнат
    rooms = MeetingRoom.query.all()  # Это можно сделать через SQLAlchemy напрямую
    return render_template('rooms.html', rooms=rooms)

@auth_bp.route('/add', methods=['GET'])
def add_room():
    return render_template('add.html')




from datetime import datetime

def calculate_duration(start_date, end_date):
    """
    Функция для вычисления продолжительности между двумя датами.

    :param start_date: Начальная дата (datetime)
    :param end_date: Конечная дата (datetime)
    :return: продолжительность в минутах
    """
    duration = end_date - start_date  # Разница между датами
    return duration.total_seconds() / 60  # Переводим в минуты

# HTML
@auth_bp.route('/account')
@login_required
def account():
    bookings = Booking.query.filter_by(user_id=current_user.id).order_by(Booking.start_date).all()
    rooms = MeetingRoom.query.all()  # Получаем все комнаты
    return render_template('account.html', bookings=bookings, rooms=rooms)


# API
@auth_bp.route('/api/bookings')
@login_required
def get_bookings():
    bookings = Booking.query.filter_by(user_id=current_user.id).order_by(Booking.start_date).all()
    return jsonify([{
        'id': booking.id,
        'object_id': booking.object_id,
        'start_date': booking.start_date.isoformat(),
        'end_date': booking.end_date.isoformat(),
    } for booking in bookings])



@auth_bp.route('/admin')
@login_required
@role_required('admin')  # Убедитесь, что роль пользователя — admin
def admin():
    # Получаем все бронирования и комнаты для отображения
    rooms = MeetingRoom.query.all()
    bookings = Booking.query.all()  # Получаем все бронирования
    return render_template('admin.html', rooms=rooms, bookings=bookings)


