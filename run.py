import click
from app import create_app, db
from app.models import User, Product
from werkzeug.security import generate_password_hash
from datetime import date, timedelta

# Buat instance aplikasi menggunakan factory
app = create_app()

@app.cli.command("seed")
def seed():
    """Seed the database with initial data."""
    print("Seeding database...")
    
    # Hapus data lama jika ada
    Product.query.delete()
    User.query.delete()
    
    # Buat Pengguna
    admin = User(
        email="admin@example.com",
        username="admin",
        password_hash=generate_password_hash("admin123", method='pbkdf2:sha256'),
        level=1 # Level Admin
    )
    pkl_user = User(
        email="pkl@example.com",
        username="anak_pkl",
        password_hash=generate_password_hash("pkl123", method='pbkdf2:sha256'),
        level=0 # Level Anak PKL
    )
    db.session.add(admin)
    db.session.add(pkl_user)
    
    # Buat Produk Dummy
    products_data = [
        {'name': 'Apel Fuji', 'quantity': 100, 'reception_date': date.today() - timedelta(days=2), 'expiry_duration': 14},
        {'name': 'Pisang Cavendish', 'quantity': 150, 'reception_date': date.today() - timedelta(days=1), 'expiry_duration': 7},
        {'name': 'Jeruk Sunkist', 'quantity': 80, 'reception_date': date.today(), 'expiry_duration': 20},
        {'name': 'Stroberi', 'quantity': 50, 'reception_date': date.today() - timedelta(days=4), 'expiry_duration': 5},
        {'name': 'Mangga Harum Manis', 'quantity': 70, 'reception_date': date.today() - timedelta(days=3), 'expiry_duration': 8},
        {'name': 'Anggur Merah', 'quantity': 60, 'reception_date': date.today() - timedelta(days=6), 'expiry_duration': 10}
    ]

    for p_data in products_data:
        product = Product(
            name=p_data['name'],
            initial_quantity=p_data['quantity'],
            current_quantity=p_data['quantity'],
            reception_date=p_data['reception_date'],
            expiry_date=p_data['reception_date'] + timedelta(days=p_data['expiry_duration']),
            condition="Baik"
        )
        db.session.add(product)

    db.session.commit()
    print("Database seeded!")

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001,debug=True)