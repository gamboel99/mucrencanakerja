import streamlit as st
import pandas as pd
import pygsheets
from datetime import date, timedelta

st.title("📚 Penjadwalan Konsultasi (Google Sheets by Key)")

# Autentikasi
gc = pygsheets.authorize(service_file="credentials.json")

# Gunakan ID dari Google Sheets kamu
sheet_id = "1jjwbjGwOBKkC7fOqHnZURBS_EezeeGEmn45CdcmWOeo"
sh = gc.open_by_key(sheet_id)
wks = sh.sheet1

# Ambil data
df = pd.DataFrame(wks.get_all_records())

# Form tambah pekerjaan
with st.form("form_input"):
    st.subheader("➕ Tambah Pekerjaan Baru")
    nama = st.text_input("Nama Klien")
    topik = st.text_input("Topik / Judul")
    jenis = st.text_input("Jenis Layanan")
    tgl_masuk = st.date_input("Tanggal Masuk", date.today())
    estimasi_hari = st.number_input("Estimasi Hari Pengerjaan", min_value=1, max_value=30)
    nominal = st.number_input("Nominal Pembayaran", min_value=0)
    submit = st.form_submit_button("Simpan")

    if submit:
        estimasi_selesai = tgl_masuk + timedelta(days=int(estimasi_hari))
        data_baru = [nama, topik, jenis, str(tgl_masuk), str(estimasi_selesai), nominal]
        wks.append_table(data_baru)
        st.success("✅ Data berhasil ditambahkan!")
        st.experimental_rerun()

# Tampilkan data
st.subheader("📋 Data Jadwal Konsultasi")
st.dataframe(df)
