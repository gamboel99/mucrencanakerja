import sqlite3

def connect_db():
    conn = sqlite3.connect("penjadwalan.db")
    return conn

def create_table():
    conn = connect_db()
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS penjadwalan (
            id TEXT PRIMARY KEY,
            nama_klien TEXT,
            topik TEXT,
            jenis TEXT,
            tanggal_masuk TEXT,
            estimasi_selesai TEXT,
            nominal REAL,
            status_pembayaran TEXT
        )
    ''')
    conn.commit()
    conn.close()
