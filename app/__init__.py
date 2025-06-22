from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from config import Config

# Inisialisasi ekstensi
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = 'main.login' # Halaman login
login_manager.login_message_category = 'info'
login_manager.login_message = 'Silakan login untuk mengakses halaman ini.'

def create_app(config_class=Config):
    """
    Application Factory untuk membuat instance aplikasi Flask.
    """
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Inisialisasi ekstensi dengan aplikasi
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    # Daftarkan Blueprint
    from app.routes import main as main_blueprint
    app.register_blueprint(main_blueprint)

    with app.app_context():
        # Buat semua tabel database jika belum ada
        db.create_all()

    return app