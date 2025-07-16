# 1. Form Tambah
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
            data_baru = [nama, topik, jenis, str(tgl_masuk), str(estimasi_selesai), int(nominal)]
            wks.append_table(data_baru)
            st.success("✅ Data berhasil ditambahkan!")
            st.rerun()

# 2. Data Tabel
st.subheader("📋 Data Jadwal Konsultasi")
if not df.empty:
    df_display = df.copy()
    df_display.index += 1
    st.dataframe(df_display, use_container_width=True)
else:
    st.info("Belum ada data.")

# 3. Edit / Hapus
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

# 4. Statistik Pendapatan
st.subheader("📊 Statistik Pendapatan")
df["estimasi_selesai"] = pd.to_datetime(df["estimasi_selesai"], errors="coerce")
harian = df[df["estimasi_selesai"].dt.date == date.today()]["nominal"].sum()
bulanan = df[df["estimasi_selesai"].dt.month == date.today().month]["nominal"].sum()
st.success(f"💰 Hari ini: Rp {harian:,.0f} | Bulan ini: Rp {bulanan:,.0f}")

# 5. Export & Backup
st.subheader("📦 Ekspor & Cadangan")
st.download_button("⬇️ Download ke Excel", df.to_csv(index=False).encode(), file_name="jadwal_konsultasi.csv")

df_serial = df.copy()
for kolom in ["tgl_masuk", "estimasi_selesai"]:
    if kolom in df_serial.columns:
        df_serial[kolom] = df_serial[kolom].astype(str)

with open("backup_data.json", "w") as f:
    json.dump(df_serial.to_dict(orient="records"), f)
st.download_button("📦 Backup ke JSON", data=open("backup_data.json", "rb"), file_name="jadwal_backup.json")
