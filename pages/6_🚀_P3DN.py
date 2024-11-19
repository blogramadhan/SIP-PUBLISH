# Library Utama
import pandas as pd
import numpy as np
import plotly.express as px
import duckdb
import openpyxl
import io
import xlsxwriter
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

# Dataset P3DN
DatasetKamusTKDN = "https://data.pbj.my.id/p3dn/KamusTKDN.xlsx"
DatasetRUPPaketPenyediaTerumumkan = "https://data.pbj.my.id/D197/sirup/RUP-PaketPenyedia-Terumumkan2024.parquet"
DatasetRUPPaketAnggaranPenyedia = "https://data.pbj.my.id/D197/sirup/RUP-PaketAnggaranPenyedia2024.parquet"

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

    upload_realisasi_p3dn = st.file_uploader("Unggah file Excel Realisasi P3DN", type=["xlsx"])
    upload_komitmen_p3dn = st.file_uploader("Unggah file Excel Komitmen P3DN", type=["xlsx"])

    if upload_realisasi_p3dn and upload_komitmen_p3dn is not None:

        try:

            baca_tkdn = tarik_data_excel(DatasetKamusTKDN)
            baca_RUPPaketPenyediaTerumumkan = tarik_data_parquet(DatasetRUPPaketPenyediaTerumumkan)
            baca_RUPPaketAnggaranPenyedia = tarik_data_parquet(DatasetRUPPaketAnggaranPenyedia)

            baca_realisasi_p3dn = tarik_data_excel(upload_realisasi_p3dn) 
            df_realisasi_p3dn = pd.merge(baca_realisasi_p3dn, baca_tkdn, left_on="Kode Akun", right_on="kode_akun", how="left")
            df_realisasi_p3dn["TKDN"] = df_realisasi_p3dn["tkdn"]
            df_realisasi_p3dn = df_realisasi_p3dn.drop(["kode_akun", "nama_akun", "tkdn"], axis=1)
            df_realisasi_p3dn["kode_sub_kegiatan"] = df_realisasi_p3dn["Kode Sub Kegiatan"].apply(lambda x: x[:8] + x[-9:] if len(x) == 28 else x)
            df_realisasi_p3dn["sub_kegiatan_akun"] = df_realisasi_p3dn["kode_sub_kegiatan"] + "." + df_realisasi_p3dn["Kode Akun"]

            baca_RUPPaketPenyediaTerumumkan = baca_RUPPaketPenyediaTerumumkan[baca_RUPPaketPenyediaTerumumkan["status_umumkan_rup"] == "Terumumkan"]
            baca_RUPPaketAnggaranPenyedia_filter = baca_RUPPaketAnggaranPenyedia[["kd_rup", "mak"]]
            df_RUPMAK = baca_RUPPaketPenyediaTerumumkan.merge(baca_RUPPaketAnggaranPenyedia_filter, how='left', on='kd_rup')
            df_RUPMAK["sub_kegiatan_akun_rup"] = df_RUPMAK["mak"].apply(lambda x: x[:35])
            df_RUPMAK_filter = df_RUPMAK[["kd_rup", "mak", "sub_kegiatan_akun_rup", "status_pdn"]].drop_duplicates(subset=["sub_kegiatan_akun_rup"])

            df_p3dn_ruptkdn = pd.merge(df_realisasi_p3dn, df_RUPMAK_filter, left_on="sub_kegiatan_akun", right_on="sub_kegiatan_akun_rup", how="left")

            df_p3dn_ruptkdn["Kode RUP"] = df_p3dn_ruptkdn["kd_rup"]
            df_p3dn_ruptkdn_filter = df_p3dn_ruptkdn.drop(["kode_sub_kegiatan", "sub_kegiatan_akun", "kd_rup", "mak", "sub_kegiatan_akun_rup", "status_pdn"], axis=1)

            baca_komitmen_p3dn = tarik_data_excel(upload_komitmen_p3dn)

            st.write(df_realisasi_p3dn.shape)
            st.write(df_p3dn_ruptkdn_filter.shape)

            st.dataframe(baca_komitmen_p3dn["TKDN(%)"].head(10))

            unduh_P3DN = download_excel(df_p3dn_ruptkdn_filter)

            st.download_button(
                label = "📥 Download Data P3DN Hasil Olahan",
                data = unduh_P3DN,
                file_name = f"P3DN_Olahan.xlsx",
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