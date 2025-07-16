import streamlit as st
import pandas as pd
import os
from datetime import date, timedelta
from whatsapp import kirim_whatsapp
from streamlit_autorefresh import st_autorefresh

# Refresh otomatis setiap 1 jam (3600000 ms)
st_autorefresh(interval=3600000, key="datarefresh")

st.title("📅 Penjadwalan Konsultasi Skripsi/Tesis/Disertasi")
db_path = "data_jadwal.csv"

# Load atau buat data
if os.path.exists(db_path):
    df = pd.read_csv(db_path)
else:
    df = pd.DataFrame(columns=["nama_klien", "topik", "jenis", "tgl_masuk", "estimasi_selesai", "nominal"])

# Form tambah pekerjaan
with st.form("form_tambah"):
    st.subheader("➕ Tambah Pekerjaan Baru")
    nama = st.text_input("Nama Klien")
    topik = st.text_input("Topik Konsultasi")
    jenis = st.text_input("Jenis Layanan (bebas diisi)")
    tgl_masuk = st.date_input("Tanggal Masuk", date.today())
    nominal = st.number_input("Nominal Pembayaran (Rp)", min_value=0)
    estimasi_hari = st.number_input("Estimasi Lama Pengerjaan (hari)", min_value=1, value=3)
    submit = st.form_submit_button("Tambah")

    if submit:
        estimasi_selesai = tgl_masuk + timedelta(days=estimasi_hari)
        df.loc[len(df)] = [nama, topik, jenis, str(tgl_masuk), str(estimasi_selesai), nominal]
        df.to_csv(db_path, index=False)
        st.success("✅ Data berhasil ditambahkan!")

# Tampilkan tabel pekerjaan
st.subheader("📋 Antrian Pekerjaan")
st.dataframe(df, use_container_width=True)

# Fitur Edit & Hapus
st.subheader("✏️ Edit / 🗑️ Hapus Pekerjaan")
for i, row in df.iterrows():
    col1, col2 = st.columns([5, 1])
    with col1:
        st.markdown(f"**{row['nama_klien']}** - {row['topik']} ({row['jenis']})")
    with col2:
        if st.button("Hapus", key=f"hapus_{i}"):
            df.drop(i, inplace=True)
            df.reset_index(drop=True, inplace=True)
            df.to_csv(db_path, index=False)
            st.experimental_rerun()

# Export ke Excel
st.download_button("⬇️ Download Excel", df.to_csv(index=False).encode("utf-8"), file_name="jadwal_konsultasi.csv")

# Estimasi Pendapatan
st.subheader("📊 Estimasi Pendapatan")
df["tgl_masuk"] = pd.to_datetime(df["tgl_masuk"])
df["estimasi_selesai"] = pd.to_datetime(df["estimasi_selesai"])
hari_ini = date.today()
bulan_ini = hari_ini.month
pendapatan_harian = df[df["estimasi_selesai"].dt.date == hari_ini]["nominal"].sum()
pendapatan_bulanan = df[df["estimasi_selesai"].dt.month == bulan_ini]["nominal"].sum()
st.info(f"💰 Hari ini: Rp {pendapatan_harian:,.0f} | Bulan ini: Rp {pendapatan_bulanan:,.0f}")

# Reminder WhatsApp H-1
besok = date.today() + timedelta(days=1)
reminder = df[df["estimasi_selesai"].dt.date == besok]

if not reminder.empty:
    pesan = f"🔔 Pengingat H-1 Konsultasi\nDeadline besok ({besok}):\n\n"
    for _, row in reminder.iterrows():
        pesan += f"• {row['nama_klien']} – {row['jenis']}: {row['topik']}\n"

    try:
        sid_msg = kirim_whatsapp(
            st.secrets["twilio"]["to"],
            pesan,
            st.secrets["twilio"]["sid"],
            st.secrets["twilio"]["token"],
            st.secrets["twilio"]["from"]
        )
        st.success("📱 Reminder WA berhasil dikirim.")
    except Exception as e:
        st.error(f"Gagal kirim WhatsApp: {e}")