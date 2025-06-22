from flask import (
    Blueprint, render_template, redirect, url_for, flash, request, jsonify, Response
)
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import User, Product, FoodWaste
from app.forms import RegisterForm, LoginForm, ProductForm, FoodWasteForm
from datetime import date, timedelta
import pandas as pd
import io

# Membuat Blueprint
main = Blueprint('main', __name__)

# --- Rute Otentikasi ---

@main.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=True)
            flash('Login berhasil!', 'success')
            return redirect(url_for('main.dashboard'))
        else:
            flash('Login gagal. Periksa kembali email dan password Anda.', 'danger')
    return render_template('login.html', title='Login', form=form)

@main.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(
            email=form.email.data,
            username=form.username.data,
            level=int(form.level.data)
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Registrasi berhasil! Silakan login.', 'success')
        return redirect(url_for('main.login'))
    return render_template('register.html', title='Register', form=form)

@main.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Anda telah logout.', 'info')
    return redirect(url_for('main.login'))

# --- Rute Utama Aplikasi ---

@main.route('/')
@main.route('/dashboard')
@login_required
def dashboard():
    # Statistik
    total_stock_in = db.session.query(db.func.sum(Product.initial_quantity)).scalar() or 0
    stock_remaining = db.session.query(db.func.sum(Product.current_quantity)).scalar() or 0
    food_waste = db.session.query(db.func.sum(FoodWaste.quantity)).scalar() or 0
    
    today = date.today()
    near_expiry_limit = today + timedelta(days=5)
    near_expiry_count = Product.query.filter(Product.expiry_date.between(today, near_expiry_limit)).count()
    
    # Data untuk Grafik
    chart_data = {
        'labels': ['Stok Masuk', 'Stok Tersisa', 'Nyaris Kadaluarsa', 'Food Waste'],
        'data': [total_stock_in, stock_remaining, near_expiry_count, food_waste]
    }
    
    return render_template('dashboard.html', title='Dashboard', chart_data=chart_data)

@main.route('/input_data', methods=['GET', 'POST'])
@login_required
def input_data():
    form = ProductForm()
    if form.validate_on_submit():
        new_product = Product(
            name=form.name.data,
            initial_quantity=form.quantity.data,
            current_quantity=form.quantity.data,
            reception_date=form.reception_date.data,
            expiry_date=form.expiry_date.data,
            condition=form.condition.data
        )
        db.session.add(new_product)
        db.session.commit()
        flash('Produk baru berhasil ditambahkan!', 'success')
        return redirect(url_for('main.input_data'))
        
    products = Product.query.order_by(Product.expiry_date.asc()).all()
    # PERBAIKAN: Tambahkan variabel 'today' di sini
    return render_template(
        'input_data.html', 
        title='Input Data Barang', 
        form=form, 
        products=products, 
        today=date.today()
    )

@main.route('/edit_product/<int:product_id>', methods=['POST'])
@login_required
def edit_product(product_id):
    product = Product.query.get_or_404(product_id)
    product.name = request.form['name']
    product.current_quantity = int(request.form['quantity'])
    product.reception_date = date.fromisoformat(request.form['reception_date'])
    product.expiry_date = date.fromisoformat(request.form['expiry_date'])
    db.session.commit()
    flash('Data produk berhasil diubah.', 'success')
    return redirect(url_for('main.input_data'))

@main.route('/delete_product/<int:product_id>', methods=['POST'])
@login_required
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    flash('Produk berhasil dihapus.', 'danger')
    return redirect(url_for('main.input_data'))


@main.route('/expiry_alerts')
@login_required
def expiry_alerts():
    products = Product.query.order_by(Product.expiry_date.asc()).all()
    today = date.today()
    return render_template('alert.html', title='Expiry Alerts', products=products, today=today)

@main.route('/food_waste', methods=['GET', 'POST'])
@login_required
def food_waste_page():
    form = FoodWasteForm()
    # Mengisi pilihan produk pada form
    form.product_id.choices = [(p.id, p.name) for p in Product.query.order_by('name').all()]
    
    if form.validate_on_submit():
        product = Product.query.get(form.product_id.data)
        waste_quantity = form.quantity.data
        
        if waste_quantity > product.current_quantity:
            flash(f'Jumlah waste ({waste_quantity}) melebihi stok saat ini ({product.current_quantity}).', 'danger')
        else:
            # Kurangi stok produk
            product.current_quantity -= waste_quantity
            
            # Catat food waste
            new_waste = FoodWaste(
                product_id=form.product_id.data,
                quantity=waste_quantity,
                reason=form.reason.data
            )
            db.session.add(new_waste)
            db.session.commit()
            flash('Food waste berhasil dicatat.', 'success')
        return redirect(url_for('main.food_waste_page'))
        
    wastes = FoodWaste.query.order_by(FoodWaste.recorded_at.desc()).all()
    return render_template('food_waste.html', title='Kelola Food Waste', form=form, wastes=wastes)


@main.route('/reports')
@login_required
def reports():
    return render_template('reports.html', title='Laporan')

@main.route('/reports/export')
@login_required
def export_reports():
    # Ambil semua data produk
    products_query = Product.query.all()
    
    # Siapkan data untuk DataFrame
    data = {
        "ID": [p.id for p in products_query],
        "Nama Produk": [p.name for p in products_query],
        "Stok Awal": [p.initial_quantity for p in products_query],
        "Stok Tersisa": [p.current_quantity for p in products_query],
        "Tanggal Terima": [p.reception_date for p in products_query],
        "Tanggal Kadaluarsa": [p.expiry_date for p in products_query],
        "Sisa Hari": [p.days_to_expiry for p in products_query],
        "Kondisi": [p.condition for p in products_query],
    }
    
    df = pd.DataFrame(data)

    # Buat file Excel di memori
    output = io.BytesIO()
    writer = pd.ExcelWriter(output, engine='openpyxl')
    df.to_excel(writer, index=False, sheet_name='Laporan Stok Buah')
    writer.close()
    output.seek(0)
    
    return Response(
        output,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment;filename=laporan_stok_buah.xlsx"}
    )
