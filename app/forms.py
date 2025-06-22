from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, IntegerField, DateField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError, NumberRange
from .models import User

class RegisterForm(FlaskForm):
    """Form untuk registrasi pengguna baru."""
    email = StringField('Email', validators=[DataRequired(), Email()])
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=25)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Konfirmasi Password', validators=[DataRequired(), EqualTo('password')])
    level = SelectField('Level', choices=[('0', 'Anak PKL SMK'), ('1', 'Admin')], validators=[DataRequired()])
    submit = SubmitField('Daftar')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email sudah terdaftar. Silakan gunakan email lain.')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username sudah terdaftar. Silakan gunakan username lain.')

class LoginForm(FlaskForm):
    """Form untuk login pengguna."""
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class ProductForm(FlaskForm):
    """Form untuk menambah dan mengedit produk."""
    name = StringField('Nama Produk', validators=[DataRequired()])
    quantity = IntegerField('Jumlah Stok', validators=[DataRequired(), NumberRange(min=1)])
    reception_date = DateField('Tanggal Penerimaan', format='%Y-%m-%d', validators=[DataRequired()])
    expiry_date = DateField('Tanggal Kadaluarsa', format='%Y-%m-%d', validators=[DataRequired()])
    condition = StringField('Kondisi Awal', validators=[DataRequired()], default='Baik')
    submit = SubmitField('Simpan Produk')

class FoodWasteForm(FlaskForm):
    """Form untuk mencatat food waste."""
    product_id = SelectField('Produk', coerce=int, validators=[DataRequired()])
    quantity = IntegerField('Jumlah Terbuang', validators=[DataRequired(), NumberRange(min=1)])
    reason = StringField('Alasan', default='Kadaluarsa')
    submit = SubmitField('Catat Waste')