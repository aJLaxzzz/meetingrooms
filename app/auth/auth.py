from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from app.models import User, MeetingRoom
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
        flash('Регистрация прошла успешно. Войдите в систему.')
        print("Регистрация прошла успешно. Войдите в систему.")
        return redirect('/rooms')

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
            return redirect('/rooms')
        flash('Неверные учетные данные')
        print("Неверные учетеные данные")

    return render_template('login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Вы вышли из системы')
    return redirect(url_for('auth.login'))


@auth_bp.route('/profile')
@login_required
def profile():
    return render_template('profile.html', user=current_user)


@auth_bp.route('/admin')
@role_required('admin')
def admin_area():
    return render_template('admin.html', user=current_user)
@auth_bp.route('/')
def index():
    return redirect(url_for('auth.login'))

@auth_bp.route('/rooms')
@login_required
def rooms():
    # Делаем запрос к API, чтобы получить список комнат
    rooms = MeetingRoom.query.all()  # Это можно сделать через SQLAlchemy напрямую
    return render_template('rooms.html', rooms=rooms)

