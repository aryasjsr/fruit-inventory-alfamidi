# Sistem Inventaris Buah untuk ALFAMIDI- Flask & MySQL

Aplikasi web sederhana yang dibangun menggunakan Flask untuk mengelola inventaris produk segar (buah), lengkap dengan sistem otentikasi pengguna, manajemen data, dasbor visual, dan sistem peringatan kadaluarsa.

## Fitur Utama

-   🔐 **Otentikasi Pengguna:**
    -   Halaman Register & Login.
    -   Password di-hash menggunakan `Werkzeug`.
    -   Dua level pengguna: Admin & Anak PKL.
    -   Proteksi halaman yang memerlukan login.
-   📊 **Dashboard Statistik:**
    -   Menampilkan ringkasan data: Stok Masuk, Stok Tersisa, Produk Mendekati Kadaluarsa, dan Food Waste.
    -   Visualisasi data menggunakan grafik bar dengan **Chart.js**.
-   📝 **Manajemen Data Produk (CRUD):**
    -   Tambah, Lihat, Edit, dan Hapus data produk.
    -   Menggunakan modal Bootstrap untuk form input dan edit yang interaktif.
-   ⏰ **Sistem Peringatan Kadaluarsa:**
    -   Daftar produk dengan indikator warna (Merah, Kuning, Hijau) berdasarkan tanggal kadaluarsa.
    -   Notifikasi peringatan jika ada produk yang sudah kadaluarsa.
-   📄 **Ekspor Laporan:**
    -   Fitur untuk mengunduh semua data inventaris menjadi file Excel (.xlsx).

## Teknologi yang Digunakan

-   **Backend:** Python, Flask, Flask-SQLAlchemy (ORM), Flask-Migrate, Flask-Login, Flask-WTF.
-   **Database:** MySQL.
-   **Frontend:** HTML, Bootstrap 5, CSS, JavaScript, Chart.js.
-   **Lainnya:** Pandas & openpyxl (untuk ekspor Excel).

---

## Instalasi & Setup

Berikut adalah langkah-langkah untuk menjalankan proyek ini secara lokal.

### 1. Prasyarat

-   Python 3.8+
-   MySQL Server
-   Git (opsional)

### 2. Clone Repositori

```bash
git clone https://github.com/aryasjsr/fruit-inventory-alfamidi.git
cd fruit-inventory-alfamidi

3. Setup Lingkungan
Buat dan aktifkan Virtual Environment:

# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate

Install semua dependensi:

pip install -r requirements.txt

4. Konfigurasi Database
Buat database baru di MySQL Anda, misalnya dengan nama fruit_inventory_db.

Salin file .env.example menjadi .env (jika ada) atau buat file .env baru.

Isi file .env dengan kredensial database Anda:

DB_USER=root
DB_PASSWORD=password_database_anda
DB_HOST=localhost
DB_NAME=db_anda

Buat file .flaskenv dan isi dengan:

FLASK_APP=run.py

5. Inisialisasi Database
Jalankan perintah berikut secara berurutan:

# 1. Inisialisasi folder migrasi (hanya sekali saat pertama kali)
flask db init

# 2. Buat file migrasi pertama
flask db migrate -m "Initial migration."

# 3. Terapkan migrasi ke database
flask db upgrade

# 4. Masukkan data dummy untuk testing
flask seed

Menjalankan Aplikasi
Setelah semua setup selesai, jalankan server pengembangan Flask:

python run.py

Buka browser Anda dan akses http://127.0.0.1:5000.

Struktur Proyek
/
├── app/
│   ├── static/
│   ├── templates/
│   ├── __init__.py
│   ├── forms.py
│   ├── models.py
│   └── routes.py
├── migrations/
├── .env
├── .flaskenv
├── .gitignore
├── config.py
├── requirements.txt
└── run.py
