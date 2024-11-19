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
DatasetP3DN = ""

## Baca file parquet


#####
# Presentasi P3DN
#####

# Sajikan Menu
menu_p3dn_1, menu_p3dn_2 = st.tabs(["| TOOLS P3DN |", "| SUMBER DATA |"])

## Tab menu PREDIKSI P3DN
with menu_p3dn_1:

    st.header(f"TOOLS P3DN")
    st.divider()

    st.subheader("Unggah Template Excel P3DN")

    upload_p3dn = st.file_uploader("Unggah file Excel P3DN", type=["xlsx"])

    if upload_p3dn is not None:

        baca_p3dn = pd.read_excel(upload_p3dn, sheet="Sheet1") 
        st.write("Data dari file yang diunggah:")
        st.table(baca_p3dn)


with menu_p3dn_2:

    st.header(f"SUMBER DATA P3DN")

    menu_p3dn_2_1, menu_p3dn_2_2 = st.tabs(["| DATA REALISASI |", "| KAMUS TKDN |"])

    ## Data Realisasi
    with menu_p3dn_2_1:

        st.subheader("DATA REALISASI")
        st.error("Data Tidak Ada, Sedang Disiapkan")

    with menu_p3dn_2_2:

        st.subheader("KAMUS TKDN")
        st.error("Data Tidak Ada, Sedang Disiapkan")