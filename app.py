import streamlit as st
import pandas as pd
import uuid
from datetime import date, timedelta
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
            estimasi_hari INTEGER,
            nominal REAL,
            status_pembayaran TEXT
        )
    ''')
    conn.commit()
    conn.close()

create_table()
st.set_page_config(page_title="Penjadwalan Konsultasi", layout="wide")
st.title("📚 Aplikasi Penjadwalan Konsultasi Ilmiah")

with st.form("form_input"):
    st.subheader("✍️ Input Layanan Baru")
    nama = st.text_input("Nama Klien")
    topik = st.text_input("Topik / Judul Pekerjaan")
    jenis = st.text_input("Jenis Layanan (misal: Bab 1, Revisi Proposal, dll)")
    estimasi_hari = st.number_input("Estimasi Lama Pengerjaan (hari)", min_value=1, max_value=60)
    nominal = st.number_input("Nominal Pembayaran", min_value=0)
    status = st.selectbox("Status Pembayaran", ["Belum", "Lunas", "Tidak Dibayar"])
    submitted = st.form_submit_button("Simpan")

    if submitted:
        conn = connect_db()
        df = pd.read_sql("SELECT * FROM penjadwalan ORDER BY tanggal_masuk", conn)
        total_hari_antri = df['estimasi_hari'].sum() if not df.empty else 0
        tanggal_mulai = date.today() + timedelta(days=total_hari_antri)
        tanggal_selesai = tanggal_mulai + timedelta(days=estimasi_hari)

        conn.execute('''
            INSERT INTO penjadwalan 
            (id, nama_klien, topik, jenis, tanggal_masuk, estimasi_selesai, estimasi_hari, nominal, status_pembayaran)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            str(uuid.uuid4()), nama, topik, jenis, str(date.today()),
            str(tanggal_selesai), estimasi_hari, nominal, status
        ))
        conn.commit()
        conn.close()
        st.success(f"✅ Disimpan! Estimasi mulai: {tanggal_mulai}, selesai: {tanggal_selesai}")

conn = connect_db()
df = pd.read_sql("SELECT * FROM penjadwalan ORDER BY tanggal_masuk", conn)
conn.close()

if df.empty:
    st.warning("Belum ada data pekerjaan.")
else:
    besok = date.today() + timedelta(days=1)
    df['estimasi_selesai'] = pd.to_datetime(df['estimasi_selesai'])
    reminder = df[df['estimasi_selesai'] == pd.to_datetime(besok)]

    with st.expander("🔔 Reminder Deadline Besok"):
        if reminder.empty:
            st.success("Tidak ada deadline besok.")
        else:
            st.warning("⚠️ Ada pekerjaan dengan deadline besok:")
            st.dataframe(reminder)

    df['tanggal_masuk'] = pd.to_datetime(df['tanggal_masuk'])
    df['bulan'] = df['tanggal_masuk'].dt.strftime('%Y-%m')

    hari_ini = date.today()
    bulan_ini = hari_ini.strftime('%Y-%m')

    pemasukan_hari_ini = df[df['tanggal_masuk'] == pd.to_datetime(hari_ini)]['nominal'].sum()
    pemasukan_bulanan = df[df['bulan'] == bulan_ini]['nominal'].sum()

    st.metric("💰 Pendapatan Hari Ini", f"Rp {pemasukan_hari_ini:,.0f}")
    st.metric("📆 Pendapatan Bulan Ini", f"Rp {pemasukan_bulanan:,.0f}")

    total_antri = df['estimasi_hari'].sum()
    jadwal_kosong = date.today() + timedelta(days=total_antri)
    st.info(f"📆 Estimasi jadwal kosong berikutnya: **{jadwal_kosong}** (Antrian {total_antri} hari kerja)")

    st.subheader("📋 Daftar Antrian Pekerjaan")
    st.dataframe(df.drop(columns=['bulan']))