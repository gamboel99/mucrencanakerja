import streamlit as st
import pandas as pd
import pygsheets
from datetime import date, timedelta
import json
from whatsapp import kirim_whatsapp

st.set_page_config(page_title="Penjadwalan Konsultasi", layout="wide")
st.title("📚 Penjadwalan Konsultasi Ilmiah")

gc = pygsheets.authorize(service_file="credentials.json")
sheet = gc.open_by_url("https://docs.google.com/spreadsheets/d/1jjwbjGwOBKkC7fOqHnZURBS_EezeeGEmn45CdcmWOeo")
wks = sheet.sheet1

df = pd.DataFrame(wks.get_all_records())
df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

st.write("🧪 Kolom terdeteksi:", df.columns.tolist())

required_cols = ["nama_klien", "topik", "jenis", "tgl_masuk", "estimasi_selesai", "nominal"]
if not all(col in df.columns for col in required_cols):
    st.error(f"❌ Kolom tidak lengkap. Pastikan Google Sheet mengandung header: {required_cols}")
    st.stop()

# ... (kode lanjutan tetap sama seperti versi sebelumnya) ...