import os
from dotenv import load_dotenv

# Muat variabel environment dari file .env
load_dotenv()

class Config:
    """Set Flask configuration from .env file."""

    # Kunci rahasia untuk keamanan sesi dan CSRF
    SECRET_KEY = os.environ.get('SECRET_KEY', 'your-fallback-secret-key')

    # Konfigurasi Database SQLAlchemy
    DB_USER = os.environ.get('DB_USER')
    DB_PASSWORD = os.environ.get('DB_PASSWORD')
    DB_HOST = os.environ.get('DB_HOST')
    DB_NAME = os.environ.get('DB_NAME')
    
    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False