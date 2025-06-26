from flask import (
    Blueprint, render_template, redirect, url_for, flash, request, jsonify, Response
)
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import User, Product, FoodWaste, LoginLog
from app.forms import RegisterForm, LoginForm, ProductForm, FoodWasteForm
from datetime import date, timedelta
import pandas as pd
import io
from functools import wraps

# Membuat Blueprint
main = Blueprint('main', __name__)

# === DECORATOR BARU UNTUK ADMIN ===
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.level != 1:
            flash('Halaman ini hanya bisa diakses oleh Admin.', 'warning')
            return redirect(url_for('main.dashboard'))
        return f(*args, **kwargs)
    return decorated_function





# --- Rute Otentikasi ---

@main.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            
            # === PERBAIKAN LOGIKA PENCATATAN LOGIN ===
            # Proses login dan pencatatan dijadikan satu transaksi
            try:
                # 1. Lakukan Login
                login_user(user, remember=True)
                
                # 2. Buat entri log
                log_entry = LoginLog(user_id=user.id, username=user.username)
                db.session.add(log_entry)
                
                # 3. Commit ke database
                db.session.commit()
                
                # 4. Beri pesan sukses HANYA jika semua berhasil
                flash('Login berhasil!', 'success')
                
                return redirect(url_for('main.dashboard'))

            except Exception as e:
                # Jika ada error, batalkan semua perubahan
                db.session.rollback()
                flash(f'Terjadi error saat proses login: {e}', 'danger')
                return redirect(url_for('main.login'))
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

@main.route('/admin')
@login_required
@admin_required
def admin_dashboard():
    # Ambil data log, urutkan dari yang terbaru
    logs = LoginLog.query.order_by(LoginLog.timestamp.desc()).all()
    # Ambil data pengguna dengan level 0 (Anak PKL)
    pkl_users = User.query.filter_by(level=0).all()
    return render_template('admin.html', title='Panel Admin', logs=logs, pkl_users=pkl_users)

@main.route('/admin/delete_user/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    user_to_delete = User.query.get_or_404(user_id)
    # Keamanan tambahan: pastikan hanya akun level 0 yang bisa dihapus
    if user_to_delete.level == 0:
        db.session.delete(user_to_delete)
        db.session.commit()
        flash(f'Akun "{user_to_delete.username}" berhasil dihapus.', 'success')
    else:
        flash('Hanya akun level PKL yang dapat dihapus.', 'warning')
    return redirect(url_for('main.admin_dashboard'))
