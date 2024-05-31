##############################
# Source Code: Dashboard SIP #
# @ Pontianak, 2024          #
##############################

# Library Utama
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import duckdb
import openpyxl
# Library Currency
from babel.numbers import format_currency
# Library AgGrid
from st_aggrid import AgGrid
from st_aggrid.grid_options_builder import GridOptionsBuilder
# Library Streamlit-Extras
from streamlit_extras.metric_cards import style_metric_cards
from streamlit_extras.app_logo import add_logo
# Library Social Media
from st_social_media_links import SocialMediaIcons
# Library Personal
from personal import *

# Konfigurasi Dasar
st.set_page_config(
    page_title="Sistem Informasi Pelaporan Pengadaan Barang dan Jasa",
    page_icon="🧊",
    layout="wide",
    initial_sidebar_state="expanded",
)

logo()

# Konten
st.title("Sistem Informasi Pelaporan - Biro Pengadaan Barang dan Jasa")

st.divider()

with st.container(border=True):

    st.subheader("Data yang disajikan di dalam aplikasi :red[SIP-SPSE] ini adalah :")

    col_menu_1, col_menu_2 = st.columns(2, gap="medium")

    with col_menu_1:

        with st.container(border=True):
            st.subheader("SIRUP")
            st.markdown(
            """
            * Profil RUP Daerah
            * Profil RUP Perangkat Daerah
            * Struktur Anggaran
            * RUP Paket Penyedia (Perangkat Daerah)
            * RUP Paket Swakelola (Perangkat Daerah)
            * Persentase Inputan RUP
            * Persentase Inputan RUP (31 Maret Tahun Berjalan)
            """
            )

        with st.container(border=True):
            st.subheader("E-PURCHASING")
            st.markdown(
            """
            * Transaksi Katalog
            * Transaksi Toko Daring
            """
            )

        with st.container(border=True):
            st.subheader("MONITORING")
            st.markdown(
            """
            * ITKP
            * SIKAP
                * Tender
                * Non Tender
            """
            )

    with col_menu_2:

        with st.container(border=True):
            st.subheader("SPSE")
            st.markdown(
            """
            * Tender
                * Pengumuman
                * SPPBJ
                * Kontrak
                * SPMK
                * BAPBAST
            * Non Tender
                * Pengumuman
                * SPPBJ
                * Kontrak
                * SPMK
                * BAPBAST
            * Pencatatan
                * Pencatatan Non Tender
                * Pencatatan Swakelola
            * Peserta Tender
            """
            )

col_footer_1, col_footer_2, col_footer_3 = st.columns(3, gap="medium")

with col_footer_1:

    with st.container(border=True):
        st.subheader("Tentang")
        st.markdown(
        """
        **:red[SIP-SPSE]** adalah Aplikasi yang menampilkan data dan informasi Pengadaan Barang dan Jasa untuk memudahkan para pengelola pengadaan melakukan 
        monitoring dan evaluasi pengadaan barang dan jasa. Aplikasi ini menganalisa data yang bersumber dari **ISB** (*Internet Service Bus*) 
        [LKPP](https://lkpp.go.id).
        """
        )

with col_footer_2:

    with st.container(border=True):
        st.subheader("Alamat")
        st.markdown(
        """
        **:red[Biro Pengadaan Barang dan Jasa] Setda Provinsi Kalimantan Barat**, Lantai 3 Gedung Utama (Sayap Timur), Kantor Gubernur Kalimantan Barat,
        Jl. Jendral Ahmad Yani, Kelurahan Bansir Darat, Kecamatan Pontianak Tenggara, Kota Pontianak, Kalimantan Barat, 78124.
        """
        )

with col_footer_3:

    with st.container(border=True):
        st.subheader("Version")
        st.markdown(
        """
        * Update V.7.20240531
        """
        )

social_media_links = [
    "https://www.facebook.com/biropbjkalbar",
    "https://youtube.com/@biropengadaanbarangdanjasa8573?si=jHg5uFTfMQjbF_a3",
    "https://www.instagram.com/barjaskalbar",
]

social_media_icons = SocialMediaIcons(social_media_links)

social_media_icons.render()