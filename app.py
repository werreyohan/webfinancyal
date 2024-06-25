import streamlit as st
import sqlite3
from datetime import datetime

# Fungsi untuk membuat koneksi ke database SQLite
def create_connection():
    conn = sqlite3.connect('ewallet.db')
    return conn

# Fungsi untuk membuat tabel ewallet dan transaksi jika belum ada
def create_tables():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ewallet (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            balance REAL NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transaksi (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            jenis TEXT NOT NULL,
            jumlah REAL NOT NULL,
            tanggal TEXT NOT NULL
        )
    ''')
    cursor.execute('''
        INSERT INTO ewallet (balance)
        SELECT 0
        WHERE NOT EXISTS (SELECT * FROM ewallet)
    ''')
    conn.commit()
    conn.close()

# Fungsi untuk mendapatkan saldo
def get_balance():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT balance FROM ewallet WHERE id = 1')
    balance = cursor.fetchone()[0]
    conn.close()
    return balance

# Fungsi untuk menyetorkan saldo
def deposit(amount):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE ewallet SET balance = balance + ? WHERE id = 1', (amount,))
    cursor.execute('INSERT INTO transaksi (jenis, jumlah, tanggal) VALUES (?, ?, ?)', ("Setor", amount, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
    conn.commit()
    conn.close()

# Fungsi untuk menarik saldo
def withdraw(amount):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE ewallet SET balance = balance - ? WHERE id = 1', (amount,))
    cursor.execute('INSERT INTO transaksi (jenis, jumlah, tanggal) VALUES (?, ?, ?)', ("Tarik", amount, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
    conn.commit()
    conn.close()

# Fungsi untuk mendapatkan riwayat transaksi
def get_transaction_history():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT jenis, jumlah, tanggal FROM transaksi ORDER BY tanggal DESC')
    transactions = cursor.fetchall()
    conn.close()
    return transactions

# Halaman Dasbor yang menampilkan saldo dan transaksi
def show_dashboard():
    st.title("Dasbor E-Wallet")
    
    balance = get_balance()
    st.write(f"Saldo Saat Ini: Rp {balance:.2f}")
    
    st.write("## Riwayat Transaksi")
    transactions = get_transaction_history()
    if transactions:
        for transaction in transactions:
            st.write(f"{transaction[2]} - {transaction[0]}: Rp {transaction[1]:.2f}")
    else:
        st.write("Tidak ada transaksi yang ditemukan.")

# Halaman untuk menyetorkan saldo
def show_deposit():
    st.title("Setor Saldo")
    
    deposit_amount = st.number_input("Masukkan jumlah yang akan disetor", min_value=0.0, format="%.2f")
    if st.button("Setor"):
        deposit(deposit_amount)
        st.success(f"Berhasil menyetor Rp {deposit_amount:.2f}")

# Halaman untuk menarik saldo
def show_withdraw():
    st.title("Tarik Saldo")
    
    balance = get_balance()
    withdraw_amount = st.number_input("Masukkan jumlah yang akan ditarik", min_value=0.0, max_value=balance, format="%.2f")
    if st.button("Tarik"):
        if withdraw_amount <= balance:
            withdraw(withdraw_amount)
            st.success(f"Berhasil menarik Rp {withdraw_amount:.2f}")
        else:
            st.error("Saldo tidak mencukupi")

# Fungsi utama untuk menampilkan halaman yang sesuai
def main():
    create_tables()
    
    st.sidebar.title("Navigasi")
    menu = ["Dasbor", "Setor", "Tarik"]
    choice = st.sidebar.selectbox("Pilih Halaman", menu)
    
    if choice == "Dasbor":
        show_dashboard()
    elif choice == "Setor":
        show_deposit()
    elif choice == "Tarik":
        show_withdraw()

if __name__ == '__main__':
    main()
