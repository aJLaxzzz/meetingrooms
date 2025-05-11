from flask import Flask
from flask_restful import Api
from app.extensions import db, bcrypt, login_manager
from app.resources.room_resource import RoomListResource, RoomResource
from app.services.meeting_room_generator import MeetingRoomGenerator
from app.auth.auth import auth_bp
from app.models import User

def create_app():
    app = Flask(__name__, static_folder='static', template_folder='templates')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'mysecretkey'
    app.config['TEMPLATES_AUTO_RELOAD'] = True

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    with app.app_context():
        db.drop_all()
        db.create_all()
        generator = MeetingRoomGenerator()
        generator.fill_database()

    api = Api(app)
    api.add_resource(RoomListResource, '/api/rooms')
    api.add_resource(RoomResource, '/api/rooms/<int:room_id>')

    app.register_blueprint(auth_bp)  # без url_prefix

    return app
