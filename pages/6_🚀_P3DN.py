# Library Utama
import pandas as pd
import numpy as np
import math
import plotly.express as px
import duckdb
import openpyxl
import io
import xlsxwriter
from openpyxl import load_workbook
from openpyxl.utils.dataframe import dataframe_to_rows
# Library Currency
from babel.numbers import format_currency
# Library AgGrid
from st_aggrid import AgGrid
from st_aggrid.grid_options_builder import GridOptionsBuilder
# Library Streamlit Extras
from streamlit_extras.metric_cards import style_metric_cards
from streamlit_extras.app_logo import add_logo
# Library Fungsi Personal
from personal import *

# Konfigurasi Dasar
st.set_page_config(
    page_title="Sistem Informasi Pelaporan Pengadaan Barang dan Jasa",
    page_icon="🧊",
    layout="wide",
    initial_sidebar_state="expanded"
)

logo()

# Konten
# region_config = {
#     "PROV. KALBAR": {"folder": "prov", "RUP": "D197", "LPSE": "97"},
    # "KOTA PONTIANAK": {"folder": "ptk", "RUP": "D199", "LPSE": "62"},
    # "KAB. KUBU RAYA": {"folder": "kkr", "RUP": "D202", "LPSE": "188"},
    # "KAB. MEMPAWAH": {"folder": "mpw", "RUP": "D552", "LPSE": "118"},
    # "KOTA SINGKAWANG": {"folder": "skw", "RUP": "D200", "LPSE": "132"},
    # "KAB. BENGKAYANG": {"folder": "bky", "RUP": "D206", "LPSE": "444"},
    # "KAB. LANDAK": {"folder": "ldk", "RUP": "D205", "LPSE": "496"},
    # "KAB. SANGGAU": {"folder": "sgu", "RUP": "D204", "LPSE": "298"},
    # "KAB. SEKADAU": {"folder": "skd", "RUP": "D198", "LPSE": "175"},
    # "KAB. MELAWI": {"folder": "mlw", "RUP": "D210", "LPSE": "540"},
    # "KAB. SINTANG": {"folder": "stg", "RUP": "D211", "LPSE": "345"},
    # "KAB. KAPUAS HULU": {"folder": "kph", "RUP": "D209", "LPSE": "488"},
    # "KAB. KETAPANG": {"folder": "ktp", "RUP": "D201", "LPSE": "110"},
    # "KAB. TANGGERANG": {"folder": "tgr", "RUP": "D50", "LPSE": "333"},
    # "KAB. KATINGAN": {"folder": "ktg", "RUP": "D236", "LPSE": "438"}
# }

# daerah = list(region_config.keys())
# tahuns = ["2024"]

# pilih = st.sidebar.selectbox("Pilih UKPBJ :", daerah)
# tahun = st.sidebar.selectbox("Pilih Tahun :", tahuns)

# selected_region = region_config.get(pilih, {})
# kodeFolder = selected_region.get("folder")
# kodeRUP = selected_region.get("RUP")
# kodeLPSE = selected_region.get("LPSE")

# Baca Dataset
con = duckdb.connect(database=':memory:')
# duckdb.sql("INSTALL httpfs")
# duckdb.sql("LOAD httpfs")

#####
# Presentasi P3DN
#####

# Sajikan Menu
menu_p3dn_1, menu_p3dn_2 = st.tabs(["| TOOLS P3DN |", "| SUMBER DATA |"])

## Tab menu PREDIKSI P3DN
with menu_p3dn_1:

    st.header(f"TOOLS P3DN")
    st.divider()

    st.subheader("Unggah Template Excel Realisasi dan Komitmen P3DN")

    bulans = ["Januari", "Februari", "Maret", "April", "Mei", "Juni"
              "Juli", "Agustus", "September", "Oktober", "November", "Desember"]
    bulans = np.insert(bulans, 0, "Akumulasi")
    bulan = st.sidebar.selectbox("Pilih Bulan :", bulans)

    # Dataset P3DN
    DatasetKamusTKDN = "https://data.pbj.my.id/p3dn/KamusTKDN.xlsx"
    DatasetRealisasi = f"https://data.pbj.my.id/p3dn/Realisasi_{bulan}.xlsx"
    DatasetPenunjang = "https://data.pbj.my.id/p3dn/kode_penunjang.xlsx"
    DatasetRUPPaketPenyediaTerumumkan = "https://data.pbj.my.id/D197/sirup/RUP-PaketPenyedia-Terumumkan2024.parquet"
    DatasetRUPPaketAnggaranPenyedia = "https://data.pbj.my.id/D197/sirup/RUP-PaketAnggaranPenyedia2024.parquet"

    upload_realisasi_p3dn = st.file_uploader("Unggah file Excel Realisasi P3DN", type=["xlsx"])
    upload_komitmen_p3dn = st.file_uploader("Unggah file Excel Komitmen P3DN", type=["xlsx"])

    # if upload_realisasi_p3dn and upload_komitmen_p3dn is not None:
    if upload_realisasi_p3dn and upload_komitmen_p3dn is not None:
        try:

            baca_tkdn = tarik_data_excel(DatasetKamusTKDN)
            baca_realisasi = tarik_data_excel(DatasetRealisasi)
            baca_penunjang = tarik_data_excel(DatasetPenunjang)
            baca_RUPPaketPenyediaTerumumkan = tarik_data_parquet(DatasetRUPPaketPenyediaTerumumkan)
            baca_RUPPaketAnggaranPenyedia = tarik_data_parquet(DatasetRUPPaketAnggaranPenyedia)

            ### Realisasi
            baca_realisasi_p3dn = tarik_data_excel(upload_realisasi_p3dn) 

            ### Betulkan "Kode Program" jika "Nama Program" contains "PROGRAM PENUNJANG"
            # Filter data dari tabel baca_realisasi_p3dn berdasarkan kata "PROGRAM PENUNJANG" (case-insensitive)
            filter_penunjang = baca_realisasi_p3dn["Nama Program"].str.contains("PROGRAM PENUNJANG", case=False, na=False)

            # Gabungkan kedua tabel (baca_realisasi_p3dn dan baca_penunjang) berdasarkan "Nama Sub SKPD"
            gabungan = baca_realisasi_p3dn.merge(baca_penunjang, on="Nama Sub SKPD", suffixes=("_tabel1", "_tabel2"))

            # Perbarui kolom "Kode Program" di tabel baca_realisasi_p3dn hanya untuk baris yang memenuhi syarat
            baca_realisasi_p3dn.loc[filter_penunjang, "Kode Program"] = gabungan.loc[
                filter_penunjang, "Kode Program_tabel2"
            ].values

            # Perbarui kolom "Kode Kegiatan" hanya untuk baris yang memenuhi syarat
            baca_realisasi_p3dn.loc[filter_penunjang, "Kode Kegiatan"] = baca_realisasi_p3dn.loc[filter_penunjang, "Kode Program"] + "." + baca_realisasi_p3dn.loc[
                filter_penunjang, "Kode Kegiatan"
            ].str.split(".", n=3).str[3]

            # Perbarui kolom "Kode Sub Kegiatan" hanya untuk baris yang memenuhi syarat
            baca_realisasi_p3dn.loc[filter_penunjang, "Kode Sub Kegiatan"] = baca_realisasi_p3dn.loc[filter_penunjang, "Kode Program"] + "." + baca_realisasi_p3dn.loc[
                filter_penunjang, "Kode Sub Kegiatan"
            ].str.split(".", n=3).str[3]
            ###

            df_realisasi_p3dn = pd.merge(baca_realisasi_p3dn, baca_tkdn, left_on="Kode Akun", right_on="kode_akun", how="left")
            df_realisasi_p3dn["TKDN"] = df_realisasi_p3dn["tkdn"]
            df_realisasi_p3dn = df_realisasi_p3dn.drop(["kode_akun", "nama_akun", "tkdn"], axis=1)
            df_realisasi_p3dn["kode_sub_kegiatan"] = df_realisasi_p3dn["Kode Sub Kegiatan"].apply(lambda x: x[:8] + x[-9:] if len(x) == 28 else x)
            df_realisasi_p3dn["sub_kegiatan_akun"] = df_realisasi_p3dn["kode_sub_kegiatan"] + "." + df_realisasi_p3dn["Kode Akun"]
            df_realisasi_p3dn["sub_kegiatan_akun"] = df_realisasi_p3dn["sub_kegiatan_akun"].apply(lambda x: "5.02.01" + x[7:] if x.startswith("2.21.01") else x)

            baca_RUPPaketPenyediaTerumumkan = baca_RUPPaketPenyediaTerumumkan[baca_RUPPaketPenyediaTerumumkan["status_umumkan_rup"] == "Terumumkan"]
            baca_RUPPaketAnggaranPenyedia_filter = baca_RUPPaketAnggaranPenyedia[["kd_rup", "mak"]]
            df_RUPMAK = baca_RUPPaketPenyediaTerumumkan.merge(baca_RUPPaketAnggaranPenyedia_filter, how='left', on='kd_rup')
            df_RUPMAK["sub_kegiatan_akun_rup"] = df_RUPMAK["mak"].apply(lambda x: x[:35])
            df_RUPMAK_filter = df_RUPMAK[["kd_rup", "mak", "sub_kegiatan_akun_rup", "status_pdn"]].drop_duplicates(subset=["sub_kegiatan_akun_rup"])

            df_p3dn_ruptkdn = pd.merge(df_realisasi_p3dn, df_RUPMAK_filter, left_on="sub_kegiatan_akun", right_on="sub_kegiatan_akun_rup", how="left")
            df_p3dn_ruptkdn["Kode RUP"] = df_p3dn_ruptkdn["kd_rup"]

            proporsi_sql = f'SELECT sub_kegiatan_akun, SUM(CAST("Anggaran Belanja" AS BIGINT)) AS anggaran_belanja FROM df_p3dn_ruptkdn GROUP BY sub_kegiatan_akun'
            proporsi = con.execute(proporsi_sql).df()
            baca_realisasi["sub_kegiatan_akun"] = baca_realisasi["Kode Gabungan"].apply(lambda x: x[:22]) 
            baca_realisasi["total_realisasi"] = baca_realisasi["Total Realisasi"]
            baca_realisasi_filter = baca_realisasi[["sub_kegiatan_akun", "total_realisasi"]].drop_duplicates(subset=["cobe"])

            df_proporsi = pd.merge(proporsi, baca_realisasi_filter, left_on="sub_kegiatan_akun", right_on="sub_kegiatan_akun", how="left")
            df_proporsi_ok = con.execute(f"SELECT sub_kegiatan_akun, anggaran_belanja, total_realisasi, total_realisasi / NULLIF(anggaran_belanja, 0) AS proporsi FROM df_proporsi").df()
            df_proporsi_ok_filter = df_proporsi_ok[["sub_kegiatan_akun", "proporsi"]]

            df_p3dn_ruptkdn = pd.merge(df_p3dn_ruptkdn, df_proporsi_ok_filter, left_on="sub_kegiatan_akun", right_on="sub_kegiatan_akun", how="left")
            df_p3dn_ruptkdn["Realisasi Belanja"] = (((df_p3dn_ruptkdn["proporsi"] * df_p3dn_ruptkdn["Anggaran Belanja"]) // 1000) * 1000).fillna(0)
            df_p3dn_ruptkdn_filter = df_p3dn_ruptkdn.drop(["kode_sub_kegiatan", "sub_kegiatan_akun", "kd_rup", "mak", "sub_kegiatan_akun_rup", "status_pdn", "proporsi"], axis=1)

            ### Komitmen
            df_komitmen = pd.read_excel(upload_komitmen_p3dn, header=[0,1], dtype=str)
            
            # Kolom untuk kode urusan/program/kegiatan/subkegiatan
            kode_col = ('KODE URUSAN/BIDANG URUSAN/PROGRAM KEG/SUBKEG', 'Unnamed: 1_level_1')

            # Gabungkan semua kode di bawah header utama KODE AKUN di df_komitmen menjadi satu kolom
            kode_akun_columns = [col for col in df_komitmen.columns if col[0] == 'KODE AKUN']
            df_komitmen[('kode_akun_gabungan', '')] = (
                df_komitmen[kode_col].apply(lambda x: x[:8] + x[-9:] if len(x) == 28 else x) + "." +
                df_komitmen[kode_akun_columns].astype(str).apply(lambda row: '.'.join(row), axis=1)
            )

            # Flatten Multiindex header to single level for manipulation
            df_komitmen.columns = [' '.join(col).strip() for col in df_komitmen.columns]

            # Gabungkan data berdasarkan kode_akun_gabungan dari df_komitmen dan sub_kegiatan_akun dari Realisasi Olahan            
            merged_df = df_komitmen.merge(
                df_p3dn_ruptkdn[["sub_kegiatan_akun", "status_pdn", "TKDN"]].drop_duplicates(subset=["sub_kegiatan_akun"]),
                left_on="kode_akun_gabungan",
                right_on="sub_kegiatan_akun",
                how="left"
            )

            # Kolom yang kita gunakan: SIPD - ANGGARAN SIPD dan KOMITMEN PDN ANGGARAN
            anggaran_sipd_col = "SIPD ANGGARAN SIPD"
            anggaran_pdn_col = "KOMITMEN NILAI PRODUK DALAM NEGERI(PDN) ANGGARAN PDN"
            tkdn_col = "TKDN(%) Unnamed: 14_level_1"

            merged_df[anggaran_sipd_col] = pd.to_numeric(merged_df[anggaran_sipd_col], errors='coerce')
            merged_df[tkdn_col] = pd.to_numeric(merged_df[tkdn_col], errors='coerce')

            merged_df[anggaran_sipd_col].fillna(0, inplace=True)
            merged_df[tkdn_col].fillna(0, inplace=True)

            # Jika TKDN > 0, salin nilai TKDN * nilai ANGGARAN SIPD ke ANGGARAN PDN
            merged_df.loc[merged_df['TKDN'] > 0, anggaran_pdn_col] = (
                merged_df[anggaran_sipd_col] * merged_df["TKDN"] / 100
            )

            # Perbarui kolom TKDN(%) dengan nilai dari TKDN dari df_p3dn_ruptkdn
            merged_df[tkdn_col] = merged_df["TKDN"]
            merged_df_filter = merged_df.drop(["kode_akun_gabungan", "sub_kegiatan_akun", "status_pdn", "TKDN"], axis=1)

            st.write(df_realisasi_p3dn.shape)
            st.write(df_p3dn_ruptkdn_filter.shape)

            unduh_P3DN = download_excel(df_p3dn_ruptkdn_filter)

            st.download_button(
                label = "📥 Download Data Realisasi P3DN Hasil Olahan",
                data = unduh_P3DN,
                file_name = f"Realisasi_P3DN_Olahan.xlsx",
                mime = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )        

            st.write(df_komitmen.shape)
            st.write(merged_df.shape)

            unduh_KOMITMEN = download_excel(merged_df_filter)

            st.download_button(
                label = "📥 Download Data Komitmen P3DN Hasil Olahan",
                data = unduh_KOMITMEN,
                file_name = f"Komitmen_P3DN_Olahan.xlsx",
                mime = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' 
            )

        except Exception as e:
            
            st.error(f"Terjadi Kesalahan: {e}")


with menu_p3dn_2:

    st.header(f"SUMBER DATA P3DN")
    st.markdown(
        """
        * [Template P3DN](https://data.pbj.my.id/p3dn/P3DN%20Format%20Realisasi%20-%20Bulan%20Oktober%20Tahun%202024.xlsx)
        * [Kamus TKDN](https://data.pbj.my.id/p3dn/KamusTKDN.xlsx)
        """
    )