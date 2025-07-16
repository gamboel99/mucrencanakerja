import streamlit as st
import pandas as pd
import uuid
from datetime import date, timedelta
from database import connect_db, create_table

create_table()

st.title("📋 Jadwal Konsultasi Ilmiah (Offline Mode)")

with st.form("input_form"):
    nama = st.text_input("Nama Klien")
    topik = st.text_input("Topik")
    jenis = st.text_input("Jenis Layanan (misal: Revisi, Bab 1, Review Proposal, dll)")
    estimasi_hari = st.number_input("Estimasi Hari Pengerjaan", min_value=1, max_value=30)
    nominal = st.number_input("Nominal Pembayaran", min_value=0)
    status = st.selectbox("Status Pembayaran", ["Belum", "Lunas", "Tidak Dibayar"])
    submitted = st.form_submit_button("Simpan")

    if submitted:
        tanggal = str(date.today())
        estimasi_selesai = date.today() + timedelta(days=estimasi_hari)
        conn = connect_db()
        cur = conn.cursor()
        cur.execute('''
            INSERT INTO penjadwalan (id, nama_klien, topik, jenis, tanggal_masuk, estimasi_selesai, nominal, status_pembayaran)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            str(uuid.uuid4()),
            nama,
            topik,
            jenis,
            tanggal,
            str(estimasi_selesai),
            nominal,
            status
        ))
        conn.commit()
        conn.close()
        st.success("✅ Data berhasil disimpan!")

# --- Tampilkan Data ---
st.subheader("📄 Daftar Antrian")
conn = connect_db()
df = pd.read_sql("SELECT * FROM penjadwalan ORDER BY tanggal_masuk", conn)
conn.close()
st.dataframe(df)
