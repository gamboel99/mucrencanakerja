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
df.columns = [str(col).strip().lower().replace(" ", "_") for col in df.columns]

df["tgl_masuk"] = pd.to_datetime(df["tgl_masuk"], errors="coerce")
df["estimasi_selesai"] = pd.to_datetime(df["estimasi_selesai"], errors="coerce")

rusak_masuk = df[df["tgl_masuk"].isna()]
rusak_estimasi = df[df["estimasi_selesai"].isna()]

if not rusak_masuk.empty or not rusak_estimasi.empty:
    st.warning("🚨 Ditemukan tanggal rusak pada data berikut:")

    if not rusak_masuk.empty:
        st.write("❌ Kolom `tgl_masuk` kosong/rusak:")
        st.dataframe(rusak_masuk)

    if not rusak_estimasi.empty:
        st.write("❌ Kolom `estimasi_selesai` kosong/rusak:")
        st.dataframe(rusak_estimasi)

    if st.button("🔧 Perbaiki Tanggal Otomatis"):
        for i, row in df.iterrows():
            if pd.isna(row["tgl_masuk"]):
                df.at[i, "tgl_masuk"] = date.today()
            if pd.isna(row["estimasi_selesai"]):
                try:
                    masuk = pd.to_datetime(row["tgl_masuk"], errors="coerce")
                    df.at[i, "estimasi_selesai"] = masuk + timedelta(days=5)
                except:
                    df.at[i, "estimasi_selesai"] = date.today() + timedelta(days=5)

        # Simpan kembali ke Google Sheets
        df_to_save = df.copy()
        df_to_save["tgl_masuk"] = df_to_save["tgl_masuk"].dt.strftime("%Y-%m-%d")
        df_to_save["estimasi_selesai"] = df_to_save["estimasi_selesai"].dt.strftime("%Y-%m-%d")

        wks.clear(start="A2", end=None)
        wks.set_dataframe(df_to_save, start="A2", copy_head=False)

        st.success("✅ Tanggal rusak telah diperbaiki dan disimpan!")
        st.rerun()
else:
    st.success("✅ Semua tanggal valid. Tidak ada kerusakan.")


required_cols = ["nama_klien", "topik", "jenis", "tgl_masuk", "estimasi_selesai", "nominal"]

# 🔍 DEBUG KOLOM
st.subheader("🧪 Debug Kolom dari Sheet")
st.write("📋 Kolom yang terbaca:", df.columns.tolist())
missing = [col for col in required_cols if col not in df.columns]
if missing:
    st.error(f"🚨 Kolom berikut belum ditemukan di Sheet: {missing}")
else:
    st.success("✅ Semua kolom wajib sudah tersedia!")

if not missing:
    # ➕ Tambah Data
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

    # 📋 Tampilkan Data
    st.subheader("📋 Data Jadwal Konsultasi (Langsung Edit/Hapus)")
if not df.empty:
    for i, row in df.iterrows():
        st.markdown("---")
        cols = st.columns([2, 2, 2, 2, 2, 2, 2, 1, 1])
        cols[0].markdown(f"**{row['nama_klien']}**")
        cols[1].write(row["topik"])
        cols[2].write(row["jenis"])
        cols[3].write(row["tgl_masuk"])
        cols[4].write(row["estimasi_selesai"])
        cols[5].write(f"Rp {int(row['nominal']):,}")
        
        if cols[6].button("✏️", key=f"edit_{i}"):
            st.session_state.edit_index = i

        if cols[7].button("🗑️", key=f"hapus_{i}"):
            df.drop(index=i, inplace=True)
            df.reset_index(drop=True, inplace=True)
            wks.clear(start="A2", end=None)
            wks.set_dataframe(df, start="A2", copy_head=False)
            st.success(f"✅ Data baris ke-{i+1} dihapus!")
            st.rerun()

    # ⬇️ Form edit akan muncul jika tombol edit ditekan
    if "edit_index" in st.session_state:
        idx = st.session_state.edit_index
        st.markdown("### ✏️ Edit Data")
        selected = df.loc[idx]

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

        if st.button("💾 Simpan Perubahan", key="simpan_edit"):
            df.loc[idx] = [nama_new, topik_new, jenis_new, str(tgl_masuk_new), str(estimasi_new), int(nominal_new)]
            wks.clear(start="A2", end=None)
            wks.set_dataframe(df, start="A2", copy_head=False)
            st.success("✅ Data berhasil diperbarui!")
            del st.session_state.edit_index
            st.rerun()

    
    # 📊 Statistik
    st.subheader("📊 Statistik Pendapatan")
    df["estimasi_selesai"] = pd.to_datetime(df["estimasi_selesai"], errors="coerce")
    harian = df[df["estimasi_selesai"].dt.date == date.today()]["nominal"].sum()
    bulanan = df[df["estimasi_selesai"].dt.month == date.today().month]["nominal"].sum()
    st.success(f"💰 Hari ini: Rp {harian:,.0f} | Bulan ini: Rp {bulanan:,.0f}")

    # 📦 Backup
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
