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

required_cols = ["nama_klien", "topik", "jenis", "tgl_masuk", "estimasi_selesai", "nominal"]
if not all(col in df.columns for col in required_cols):
    st.warning(f"⚠️ Kolom tidak lengkap. Harus ada: {required_cols}")
else:
    with st.expander("➕ Tambah Pekerjaan Baru", expanded=True):
        with st.form("form_input"):
            nama = st.text_input("Nama Klien")
            topik = st.text_input("Topik / Judul")
            jenis = st.text_input("Jenis Layanan")
            tgl_masuk = st.date_input("Tanggal Masuk", date.today())
            estimasi_hari = st.number_input("Estimasi Hari Pengerjaan", min_value=1, max_value=30)
            nominal = st.number_input("Nominal Pembayaran", min_value=0)
            simpan = st.form_submit_button("Simpan")
            if simpan:
                estimasi_selesai = tgl_masuk + timedelta(days=int(estimasi_hari))
                wks.append_table([nama, topik, jenis, str(tgl_masuk), str(estimasi_selesai), int(nominal)])
                st.success("✅ Data berhasil ditambahkan!")
                st.rerun()

    st.subheader("📋 Data Jadwal Konsultasi")
    if not df.empty:
        df.index += 1
        st.dataframe(df, use_container_width=True)
    else:
        st.info("Belum ada data.")

    st.subheader("✏️ Edit / 🗑️ Hapus")
    if not df.empty:
        row_to_edit = st.number_input("Pilih nomor baris", min_value=1, max_value=len(df))
        selected = df.iloc[row_to_edit - 1]

        nama_new = st.text_input("Edit Nama", selected["nama_klien"], key="edit_nama")
        topik_new = st.text_input("Edit Topik", selected["topik"], key="edit_topik")
        jenis_new = st.text_input("Edit Jenis", selected["jenis"], key="edit_jenis")

        tgl_masuk_parsed = pd.to_datetime(selected["tgl_masuk"], errors="coerce")
        estimasi_parsed = pd.to_datetime(selected["estimasi_selesai"], errors="coerce")

        tgl_masuk_new = st.date_input("Edit Tgl Masuk", tgl_masuk_parsed.date() if not pd.isna(tgl_masuk_parsed) else date.today(), key="edit_masuk")
        estimasi_new = st.date_input("Edit Estimasi", estimasi_parsed.date() if not pd.isna(estimasi_parsed) else date.today(), key="edit_estimasi")

        try:
            nilai_nominal = int(selected["nominal"])
        except:
            nilai_nominal = 0
        nominal_new = st.number_input("Edit Nominal", nilai_nominal, key="edit_nominal")

        col1, col2 = st.columns(2)
        if col1.button("💾 Simpan Perubahan"):
            df.loc[row_to_edit - 1] = [nama_new, topik_new, jenis_new, str(tgl_masuk_new), str(estimasi_new), int(nominal_new)]
            wks.clear(start="A2", end=None)
            wks.set_dataframe(df, start="A2", copy_head=False)
            st.success("✅ Data diperbarui!")
            st.rerun()

        if col2.button("🗑️ Hapus"):
            df.drop(index=row_to_edit - 1, inplace=True)
            df.reset_index(drop=True, inplace=True)
            wks.clear(start="A2", end=None)
            wks.set_dataframe(df, start="A2", copy_head=False)
            st.warning("❌ Data dihapus.")
            st.rerun()

    st.subheader("📊 Statistik Pendapatan")
    df["estimasi_selesai"] = pd.to_datetime(df["estimasi_selesai"], errors="coerce")
    harian = df[df["estimasi_selesai"].dt.date == date.today()]["nominal"].sum()
    bulanan = df[df["estimasi_selesai"].dt.month == date.today().month]["nominal"].sum()
    st.success(f"💰 Hari ini: Rp {harian:,.0f} | Bulan ini: Rp {bulanan:,.0f}")

    st.subheader("📦 Ekspor & Backup")
    st.download_button("⬇️ Download Excel", df.to_csv(index=False).encode(), file_name="jadwal_konsultasi.csv")

    df_serial = df.copy()
    for k in ["tgl_masuk", "estimasi_selesai"]:
        if k in df_serial.columns:
            df_serial[k] = df_serial[k].astype(str)

    with open("backup_data.json", "w") as f:
        json.dump(df_serial.to_dict(orient="records"), f)
    st.download_button("💾 Backup JSON", data=open("backup_data.json", "rb"), file_name="jadwal_backup.json")

    # 🔔 Reminder WA
    besok = date.today() + timedelta(days=1)
    reminder = df[df["estimasi_selesai"].dt.date == besok]

    if not reminder.empty:
        SID = "AC2b7680b38f4a0dc2b2422f814b7c5bf4"
        TOKEN = "dcbcd85b10f3392852e3a88610edba60"
        FROM = "+14155238886"
        TO = "+6282228278397"

        pesan = f"🔔 Reminder pekerjaan H-1 ({besok}):\\n"
        for _, row in reminder.iterrows():
            pesan += f"• {row['nama_klien']} - {row['topik']}\\n"

        try:
            sid = kirim_whatsapp(TO, pesan, SID, TOKEN, FROM)
            st.success("📱 Reminder WA terkirim!")
        except Exception as e:
            st.warning(f"❌ Gagal kirim WA: {e}")
