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
    st.warning(f"⚠️ Kolom tidak lengkap. Beberapa fitur mungkin tidak tampil. Pastikan header sesuai: {required_cols}")

if all(col in df.columns for col in required_cols):

    st.subheader("📋 Data Jadwal Konsultasi")
    if not df.empty:
        df_display = df.copy()
        df_display.index += 1
        st.dataframe(df_display, use_container_width=True)
    else:
        st.info("Belum ada data.")

    with st.expander("➕ Tambah Pekerjaan Baru"):
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
                data_baru = [nama, topik, jenis, str(tgl_masuk), str(estimasi_selesai), int(nominal)]
                wks.append_table(data_baru)
                st.success("✅ Data berhasil ditambahkan!")
                st.rerun()

    st.subheader("✏️ Edit / 🗑️ Hapus")
    if not df.empty:
        row_to_edit = st.number_input("Pilih nomor baris untuk edit/hapus", min_value=1, max_value=len(df))
        selected = df.iloc[row_to_edit - 1]

        nama_new = st.text_input("Edit Nama", selected["nama_klien"], key="edit_nama")
        topik_new = st.text_input("Edit Topik", selected["topik"], key="edit_topik")
        jenis_new = st.text_input("Edit Jenis", selected["jenis"], key="edit_jenis")
        tgl_masuk_new = st.date_input("Edit Tgl Masuk", pd.to_datetime(selected["tgl_masuk"]), key="edit_masuk")
        estimasi_new = st.date_input("Edit Estimasi Selesai", pd.to_datetime(selected["estimasi_selesai"]), key="edit_estimasi")
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
            st.success("✅ Data berhasil diupdate!")
            st.rerun()

        if col2.button("🗑️ Hapus Baris Ini"):
            df.drop(index=row_to_edit - 1, inplace=True)
            df.reset_index(drop=True, inplace=True)
            wks.clear(start="A2", end=None)
            wks.set_dataframe(df, start="A2", copy_head=False)
            st.warning("❌ Data telah dihapus.")
            st.rerun()

    # Reminder WA
    besok = date.today() + timedelta(days=1)
    reminder = df[df["estimasi_selesai"] == str(besok)]

    SID = "AC2b7680b38f4a0dc2b2422f814b7c5bf4"
    TOKEN = "dcbcd85b10f3392852e3a88610edba60"
    FROM = "+14155238886"
    TO = "+6282228278397"

    if not reminder.empty:
        pesan = f"🔔 Pengingat H-1 Konsultasi besok ({besok}):\\n\\n"
        for _, row in reminder.iterrows():
            pesan += f"• {row['nama_klien']} - {row['jenis']} - {row['topik']}\\n"
        try:
            sid_msg = kirim_whatsapp(TO, pesan, SID, TOKEN, FROM)
            st.success("📱 WA dikirim: " + sid_msg)
        except Exception as e:
            st.error(f"❌ Gagal kirim WA: {e}")

    # Statistik pendapatan
    st.subheader("📊 Statistik Pendapatan")
    df["estimasi_selesai"] = pd.to_datetime(df["estimasi_selesai"], errors="coerce")
    harian = df[df["estimasi_selesai"].dt.date == date.today()]["nominal"].sum()
    bulanan = df[df["estimasi_selesai"].dt.month == date.today().month]["nominal"].sum()
    st.success(f"💰 Hari ini: Rp {harian:,.0f} | Bulan ini: Rp {bulanan:,.0f}")

    # Export
    st.download_button("⬇️ Download ke Excel", df.to_csv(index=False).encode(), file_name="jadwal_konsultasi.csv")
    with open("backup_data.json", "w") as f:
        json.dump(df.to_dict(orient="records"), f)
    st.download_button("📦 Backup ke JSON", data=open("backup_data.json", "rb"), file_name="jadwal_backup.json")
