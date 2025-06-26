from app import db, login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import date,datetime

@login_manager.user_loader
def load_user(user_id):
    """Callback untuk memuat user dari sesi."""
    return User.query.get(int(user_id))

class User(UserMixin, db.Model):
    """Model untuk tabel pengguna."""
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False, index=True)
    username = db.Column(db.String(50), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    level = db.Column(db.Integer, nullable=False, default=0) # 0: PKL, 1: Admin

    # Relasi dengan tabel login logs
    logs = db.relationship('LoginLog', backref='user', lazy='dynamic', cascade="all, delete-orphan")

    def set_password(self, password):
        """Membuat hash dari password."""
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')

    def check_password(self, password):
        """Memeriksa apakah password cocok dengan hash."""
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'

class Product(db.Model):
    """Model untuk tabel produk."""
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, index=True)
    initial_quantity = db.Column(db.Integer, nullable=False)
    current_quantity = db.Column(db.Integer, nullable=False)
    reception_date = db.Column(db.Date, nullable=False, default=date.today)
    expiry_date = db.Column(db.Date, nullable=False)
    condition = db.Column(db.String(100), nullable=False, default="Baik")
    
    # Properti untuk menghitung sisa hari sebelum kadaluarsa
    @property
    def days_to_expiry(self):
        return (self.expiry_date - date.today()).days

    def __repr__(self):
        return f'<Product {self.name}>'

class FoodWaste(db.Model):
    """Model untuk mencatat food waste."""
    __tablename__ = 'food_waste'
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    reason = db.Column(db.String(255), nullable=True)
    recorded_at = db.Column(db.Date, default=date.today)

    product = db.relationship('Product', backref=db.backref('wastes', lazy=True))

class LoginLog(db.Model):
    """Model untuk mencatat riwayat login."""
    __tablename__ = 'login_logs'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    username = db.Column(db.String(50), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f'<LoginLog {self.username} at {self.timestamp}>'