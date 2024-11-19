# Library Utama
import streamlit as st
import pandas as pd
import plotly.express as px
import duckdb
import openpyxl
import io
import xlsxwriter
# Library currency
from babel.numbers import format_currency
# Library Aggrid
from st_aggrid import AgGrid
from st_aggrid.grid_options_builder import GridOptionsBuilder
# Library Streamlit Extras
from streamlit_extras.metric_cards import style_metric_cards
from streamlit_extras.app_logo import add_logo

# Fungsi Personal Baca Data
@st.cache_data(ttl=3600)
def tarik_data_parquet(url):
    return pd.read_parquet(url)

# @st.cache_data(ttl=3600)
# def tarik_data_json(url):
#     return pd.read_json(url)

# @st.cache_data(ttl=3600)
# def tarik_data_duckdb(url):
#     return duckdb.sql(f"SELECT * FROM read_parquet('{url}')").df()

# Fungsi Personal Download Data Format Excel
def download_excel(df):
    # Buat BytesIO object untuk menyimpan File Excel
    excel_data = io.BytesIO()
    with pd.ExcelWriter(excel_data, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='sheet1')
    excel_data.seek(0)
    return excel_data.getvalue()

def logo():
    add_logo("https://storage.googleapis.com/bukanamel/img/instansi-logo.png", height=200)