import streamlit as st
import pandas as pd
import pygsheets
from datetime import date, timedelta

st.title("📚 Penjadwalan Konsultasi dengan Google Sheets")

# Autentikasi dengan file JSON
gc = pygsheets.authorize(service_file="credentials.json")

# Buka Google Sheet (pastikan sudah dibuat dan dibagikan ke service account)
sh = gc.open("penjadwalan_konsultasi")
wks = sh.sheet1

# Ambil data dari Sheet
df = pd.DataFrame(wks.get_all_records())

# Form input data
with st.form("tambah_data"):
    st.subheader("➕ Tambah Pekerjaan Baru")
    nama = st.text_input("Nama Klien")
    topik = st.text_input("Topik / Judul")
    jenis = st.text_input("Jenis Layanan")
    tgl_masuk = st.date_input("Tanggal Masuk", date.today())
    estimasi_hari = st.number_input("Estimasi Hari Pengerjaan", min_value=1, max_value=30, value=3)
    nominal = st.number_input("Nominal Pembayaran (Rp)", min_value=0)
    simpan = st.form_submit_button("Simpan")

    if simpan:
        estimasi_selesai = tgl_masuk + timedelta(days=int(estimasi_hari))
        data_baru = [nama, topik, jenis, str(tgl_masuk), str(estimasi_selesai), nominal]
        wks.append_table(data_baru)
        st.success("✅ Data berhasil ditambahkan!")
        st.experimental_rerun()

# Tampilkan data
st.subheader("📋 Data Jadwal Konsultasi")
st.dataframe(df)