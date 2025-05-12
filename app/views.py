from flask import Blueprint, request, render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from app.models import User, MeetingRoom, Booking
from app.extensions import db, bcrypt
from app.decorators import role_required  # Import your decorator

views_bp = Blueprint('views', __name__)

@views_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        role = request.form.get('role', 'user')

        if not username or not password:
            flash('Имя пользователя и пароль обязательны')
            return redirect(url_for('views.register'))

        if User.query.filter_by(username=username).first():
            flash('Пользователь уже существует')
            return redirect(url_for('views.register'))

        password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
        user = User(username=username, password_hash=password_hash, role=role)
        db.session.add(user)
        db.session.commit()

        login_user(user)

        flash('Регистрация прошла успешно. Войдите в систему.')
        return redirect(url_for('views.rooms'))

    return render_template('register.html')

@views_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()
        if user and bcrypt.check_password_hash(user.password_hash, password):
            login_user(user)

            if user.role == 'admin':
                return redirect('/admin')
            else:
                return redirect('/rooms')

        flash('Неверные учетные данные')

    return render_template('login.html')

@views_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Вы вышли из системы')
    return redirect(url_for('views.login'))

@views_bp.route('/')
def index():
    return redirect(url_for('views.login'))

@views_bp.route('/rooms')
@login_required
def rooms():
    return render_template('rooms.html', rooms=MeetingRoom.query.all())

@views_bp.route('/admin')
@login_required
@role_required('admin')  # Restrict access to admin role
def admin():
    rooms = MeetingRoom.query.all()
    bookings = Booking.query.all()
    return render_template('admin.html', rooms=rooms, bookings=bookings)

@views_bp.route('/account')
@login_required
@role_required('user')  # Restrict access to user role
def account():
    bookings = Booking.query.filter_by(user_id=current_user.id).order_by(Booking.start_date).all()
    rooms = MeetingRoom.query.all()
    return render_template('account.html', bookings=bookings, rooms=rooms)

@views_bp.route('/add', methods=['GET'])
@login_required
@role_required('admin')  # Restrict access to admin role
def add_room():
    return render_template('add.html')
