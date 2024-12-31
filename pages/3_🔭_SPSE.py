# "KAB. TANGGERANG": {"folder": "tgr", "RUP": "D50", "LPSE": "333"},
# "KAB. KATINGAN": {"folder": "ktg", "RUP": "D236", "LPSE": "438"}

# Library Utama
import streamlit as st
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
# Library fungsi Personal
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
region_config = {
    "PROV. KALBAR": {"folder": "prov", "RUP": "D197", "LPSE": "97"},
    "KOTA PONTIANAK": {"folder": "ptk", "RUP": "D199", "LPSE": "62"},
    "KAB. KUBU RAYA": {"folder": "kkr", "RUP": "D202", "LPSE": "188"},
    "KAB. MEMPAWAH": {"folder": "mpw", "RUP": "D552", "LPSE": "118"},
    "KOTA SINGKAWANG": {"folder": "skw", "RUP": "D200", "LPSE": "132"},
    "KAB. BENGKAYANG": {"folder": "bky", "RUP": "D206", "LPSE": "444"},
    "KAB. LANDAK": {"folder": "ldk", "RUP": "D205", "LPSE": "496"},
    "KAB. SANGGAU": {"folder": "sgu", "RUP": "D204", "LPSE": "298"},
    "KAB. SEKADAU": {"folder": "skd", "RUP": "D198", "LPSE": "175"},
    "KAB. MELAWI": {"folder": "mlw", "RUP": "D210", "LPSE": "540"},
    "KAB. SINTANG": {"folder": "stg", "RUP": "D211", "LPSE": "345"},
    "KAB. KAPUAS HULU": {"folder": "kph", "RUP": "D209", "LPSE": "488"},
    "KAB. KETAPANG": {"folder": "ktp", "RUP": "D201", "LPSE": "110"},
    "KAB. TANGGERANG": {"folder": "tgr", "RUP": "D50", "LPSE": "333"},
    "KAB. KATINGAN": {"folder": "ktg", "RUP": "D236", "LPSE": "438"}
}

daerah = list(region_config.keys())
tahuns = ["2025", "2024", "2023"]

pilih = st.sidebar.selectbox("Pilih UKPBJ :", daerah)
tahun = st.sidebar.selectbox("Pilih Tahun :", tahuns)

selected_region = region_config.get(pilih, {})
kodeFolder = selected_region.get("folder")
kodeRUP = selected_region.get("RUP")
kodeLPSE = selected_region.get("LPSE")

# Baca Dataset
con = duckdb.connect(database=':memory:')
# duckdb.sql("INSTALL httpfs")
# duckdb.sql("LOAD httpfs")

## Akses Dataset Tender (PARQUET)
DatasetSPSETenderPengumuman = f"https://data.pbj.my.id/{kodeLPSE}/spse/SPSE-TenderPengumuman{tahun}.parquet"
DatasetSPSETenderSelesai = f"https://data.pbj.my.id/{kodeLPSE}/spse/SPSE-TenderSelesai{tahun}.parquet"
DatasetSPSETenderSelesaiNilai = f"https://data.pbj.my.id/{kodeLPSE}/spse/SPSE-TenderSelesaiNilai{tahun}.parquet"
DatasetSPSETenderSPPBJ = f"https://data.pbj.my.id/{kodeLPSE}/spse/SPSE-TenderEkontrak-SPPBJ{tahun}.parquet"
DatasetSPSETenderKontrak = f"https://data.pbj.my.id/{kodeLPSE}/spse/SPSE-TenderEkontrak-Kontrak{tahun}.parquet"
DatasetSPSETenderSPMK = f"https://data.pbj.my.id/{kodeLPSE}/spse/SPSE-TenderEkontrak-SPMKSPP{tahun}.parquet"
DatasetSPSETenderBAST = f"https://data.pbj.my.id/{kodeLPSE}/spse/SPSE-TenderEkontrak-BAPBAST{tahun}.parquet"

## Akses Dataset Non Tender (PARQUET)
DatasetSPSENonTenderPengumuman = f"https://data.pbj.my.id/{kodeLPSE}/spse/SPSE-NonTenderPengumuman{tahun}.parquet"
DatasetSPSENonTenderSelesai = f"https://data.pbj.my.id/{kodeLPSE}/spse/SPSE-NonTenderSelesai{tahun}.parquet"
DatasetSPSENonTenderSPPBJ = f"https://data.pbj.my.id/{kodeLPSE}/spse/SPSE-NonTenderEkontrak-SPPBJ{tahun}.parquet"
DatasetSPSENonTenderKontrak = f"https://data.pbj.my.id/{kodeLPSE}/spse/SPSE-NonTenderEkontrak-Kontrak{tahun}.parquet"
DatasetSPSENonTenderSPMK = f"https://data.pbj.my.id/{kodeLPSE}/spse/SPSE-NonTenderEkontrak-SPMKSPP{tahun}.parquet"
DatasetSPSENonTenderBAST = f"https://data.pbj.my.id/{kodeLPSE}/spse/SPSE-NonTenderEkontrak-BAPBAST{tahun}.parquet"

## Akses Dataset Catat Non Tender (PARQUET)
DatasetCatatNonTender = f"https://data.pbj.my.id/{kodeLPSE}/spse/SPSE-PencatatanNonTender{tahun}.parquet"
DatasetCatatNonTenderRealisasi = f"https://data.pbj.my.id/{kodeLPSE}/spse/SPSE-PencatatanNonTenderRealisasi{tahun}.parquet"
DatasetCatatSwakelola = f"https://data.pbj.my.id/{kodeLPSE}/spse/SPSE-PencatatanSwakelola{tahun}.parquet"
DatasetCatatSwakelolaRealisasi = f"https://data.pbj.my.id/{kodeLPSE}/spse/SPSE-PencatatanSwakelolaRealisasi{tahun}.parquet"

## Akses Dataset Peserta Tender (PARQUET)
DatasetPesertaTender = f"https://data.pbj.my.id/{kodeLPSE}/spse/SPSE-PesertaTender{tahun}.parquet"

## Akses Dataset RUP Master Satker (PARQUET)
DatasetRUPMasterSatker = f"https://data.pbj.my.id/{kodeRUP}/sirup/RUP-MasterSatker{tahun}.parquet"

## Akses Dataset RUP Paket Penyedia Terumumkan (PARQUET)
DatasetRUPPP = f"https://data.pbj.my.id/{kodeRUP}/sirup/RUP-PaketPenyedia-Terumumkan{tahun}.parquet"

#####
# Presentasi Data SPSE
#####

# Sajikan menu
menu_spse_1, menu_spse_2, menu_spse_3, menu_spse_4 = st.tabs(["| TENDER |", "| NON TENDER |", "| PENCATATAN |", "| PESERTA TENDER |"])

## Tab SPSE - TENDER
with menu_spse_1:

    st.header(f"SPSE - TENDER - {pilih} - TAHUN {tahun}")

    ### Tab Sub Menu SPSE - TENDER
    menu_spse_1_1, menu_spse_1_2, menu_spse_1_3, menu_spse_1_4, menu_spse_1_5 = st.tabs(["| PENGUMUMAN |", "| SPPBJ |", "| KONTRAK |", "| SPMK |", "| BAPBAST |"])

    ### Tab Sub Menu SPSE - Tender - Pengumuman
    with menu_spse_1_1:

        try:

            ### Analisa DATA SPSE - TENDER - PENGUMUMAN
            df_SPSETenderPengumuman = tarik_data_parquet(DatasetSPSETenderPengumuman)
            df_SPSETenderPengumuman = df_SPSETenderPengumuman.drop(columns=['nama_pokja'])

            ### Unduh Dataframe Data SPSE - Tender - Pengumuman
            unduh_SPSE_Pengumuman_excel = download_excel(df_SPSETenderPengumuman)
            
            SPSE_Umumkan_1, SPSE_Umumkan_2 = st.columns((7,3))
            with SPSE_Umumkan_1:
                st.subheader("SPSE - Tender - Pengumuman")
            with SPSE_Umumkan_2:
                st.download_button(
                    label = "📥 Download Data Pengumuman Tender",
                    data = unduh_SPSE_Pengumuman_excel,
                    file_name = f"SPSETenderPengumuman-{kodeFolder}-{tahun}.xlsx",
                    mime = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )

            st.divider()

            SPSE_radio_1, SPSE_radio_2, SPSE_radio_3 = st.columns((1,1,8))
            with SPSE_radio_1:
                sumber_dana_unik_array = df_SPSETenderPengumuman['sumber_dana'].unique()
                sumber_dana_unik_array_ok = np.insert(sumber_dana_unik_array, 0, "Gabungan")
                sumber_dana = st.radio("**Sumber Dana**", sumber_dana_unik_array_ok, key="Sumber_Dana_Tender_pengumuman")
            with SPSE_radio_2:
                status_tender_unik_array = df_SPSETenderPengumuman['status_tender'].unique()
                status_tender_unik_array_ok = np.insert(status_tender_unik_array, 0, "Gabungan")
                status_tender = st.radio("**Status Tender**", status_tender_unik_array_ok, key="Status_Tender_Pengumuman")
            with SPSE_radio_3:
                nama_satker_unik_array = df_SPSETenderPengumuman['nama_satker'].unique()
                nama_satker_unik_array_ok = np.insert(nama_satker_unik_array, 0, "Semua Perangkat Daerah")
                nama_satker = st.selectbox("Pilih Perangkat Daerah :", nama_satker_unik_array_ok, key='Nama_Satker_Pengumuman')
            st.write(f"Anda memilih : **{sumber_dana}** dan **{status_tender}**")

            # Buat logika untuk query dari pilihan 3 kondisi
            df_SPSETenderPengumuman_filter_query = f"SELECT * FROM df_SPSETenderPengumuman WHERE 1=1"

            if sumber_dana != "Gabungan":
                df_SPSETenderPengumuman_filter_query += f" AND sumber_dana = '{sumber_dana}'"
            if status_tender != "Gabungan":
                df_SPSETenderPengumuman_filter_query += f" AND status_tender = '{status_tender}'"
            if nama_satker != "Semua Perangkat Daerah":
                df_SPSETenderPengumuman_filter_query += f" AND nama_satker = '{nama_satker}'"

            df_SPSETenderPengumuman_filter = con.execute(df_SPSETenderPengumuman_filter_query).df()
            
            jumlah_trx_spse_pengumuman = df_SPSETenderPengumuman_filter['kd_tender'].unique().shape[0]
            nilai_trx_spse_pengumuman_pagu = df_SPSETenderPengumuman_filter['pagu'].sum()
            nilai_trx_spse_pengumuman_hps = df_SPSETenderPengumuman_filter['hps'].sum()

            data_umum_1, data_umum_2, data_umum_3 = st.columns(3)
            data_umum_1.metric(label="Jumlah Tender Diumumkan", value="{:,}".format(jumlah_trx_spse_pengumuman))
            data_umum_2.metric(label="Nilai Pagu Tender Diumumkan", value="{:,.2f}".format(nilai_trx_spse_pengumuman_pagu))
            data_umum_3.metric(label="Nilai HPS Tender Diumumkan", value="{:,.2f}".format(nilai_trx_spse_pengumuman_hps))

            st.divider()
          
            with st.container(border=True):

                ### Tabel dan Grafik Jumlah dan Nilai Transaksi SPSE - Tender - Pengumuman Berdasarkan Kualifikasi Paket
                grafik_kp_1, grafik_kp_2 = st.tabs(["| Berdasarkan Jumlah Kualifikasi Paket |", "| Berdasarkan Nilai Kualifikasi Paket |"])

                with grafik_kp_1:

                    st.subheader("Berdasarkan Jumlah Kualifikasi Paket")

                    #### Query data grafik jumlah transaksi pengumuman SPSE berdasarkan kualifikasi paket

                    sql_kp_jumlah = """
                        SELECT kualifikasi_paket AS KUALIFIKASI_PAKET, COUNT(DISTINCT(kd_tender)) AS JUMLAH_PAKET
                        FROM df_SPSETenderPengumuman_filter GROUP BY KUALIFIKASI_PAKET ORDER BY JUMLAH_PAKET DESC
                    """
                    
                    tabel_kp_jumlah_trx = con.execute(sql_kp_jumlah).df()

                    grafik_kp_1_1, grafik_kp_1_2 = st.columns((3,7))

                    with grafik_kp_1_1:

                        st.dataframe(
                            tabel_kp_jumlah_trx,
                            column_config={
                                "KUALIFIKASI_PAKET": "KUALIFIKASI PAKET",
                                "JUMLAH_PAKET": "JUMLAH PAKET"
                            },
                            use_container_width=True,
                            hide_index=True
                        )

                    with grafik_kp_1_2:

                        st.bar_chart(tabel_kp_jumlah_trx, x="KUALIFIKASI_PAKET", y="JUMLAH_PAKET", color="KUALIFIKASI_PAKET")
            
                with grafik_kp_2:

                    st.subheader("Berdasarkan Nilai Kualifikasi Paket")

                    #### Query data grafik nilai transaksi pengumuman SPSE berdasarkan kualifikasi paket

                    sql_kp_nilai = """
                        SELECT kualifikasi_paket AS KUALIFIKASI_PAKET, SUM(pagu) AS NILAI_PAKET
                        FROM df_SPSETenderPengumuman_filter GROUP BY KUALIFIKASI_PAKET ORDER BY NILAI_PAKET DESC
                    """
                    
                    tabel_kp_nilai_trx = con.execute(sql_kp_nilai).df()

                    grafik_kp_2_1, grafik_kp_2_2 = st.columns((3,7))

                    with grafik_kp_2_1:

                        st.dataframe(
                            tabel_kp_nilai_trx,
                            column_config={
                                "KUALIFIKASI_PAKET": "KUALIFIKASI PAKET",
                                "NILAI_PAKET": "NILAI PAKET"
                            },
                            use_container_width=True,
                            hide_index=True    
                        )

                    with grafik_kp_2_2:

                        st.bar_chart(tabel_kp_nilai_trx, x="KUALIFIKASI_PAKET", y="NILAI_PAKET", color="KUALIFIKASI_PAKET")

            with st.container(border=True):

                ### Tabel dan Grafik Jumlah dan Nilai Transaksi SPSE - Tender - Pengumuman Berdasarkan Jenis Pengadaan
                grafik_jp_1, grafik_jp_2 = st.tabs(["| Berdasarkan Jumlah Jenis Pengadaan |", "| Berdasarkan Nilai Jenis Pengadaan |"])

                with grafik_jp_1:

                    st.subheader("Berdasarkan Jumlah Jenis Pengadaan")

                    #### Query data grafik jumlah transaksi pengumuman SPSE berdasarkan Jenis Pengadaan

                    sql_jp_jumlah = """
                        SELECT jenis_pengadaan AS JENIS_PENGADAAN, COUNT(DISTINCT(kd_tender)) AS JUMLAH_PAKET
                        FROM df_SPSETenderPengumuman_filter GROUP BY JENIS_PENGADAAN ORDER BY JUMLAH_PAKET DESC
                    """
                    
                    tabel_jp_jumlah_trx = con.execute(sql_jp_jumlah).df()

                    grafik_jp_1_1, grafik_jp_1_2 = st.columns((3,7))

                    with grafik_jp_1_1:

                        st.dataframe(
                            tabel_jp_jumlah_trx,
                            column_config={
                                "JENIS_PENGADAAN": "JENIS PENGADAAN",
                                "JUMLAH_PAKET": "JUMLAH PAKET"
                            },
                            use_container_width=True,
                            hide_index=True    
                        )

                    with grafik_jp_1_2:

                        st.bar_chart(tabel_jp_jumlah_trx, x="JENIS_PENGADAAN", y="JUMLAH_PAKET", color="JENIS_PENGADAAN")
            
                with grafik_jp_2:

                    st.subheader("Berdasarkan Nilai Jenis Pengadaan")

                    #### Query data grafik nilai transaksi pengumuman SPSE berdasarkan Jenis Pengadaan

                    sql_jp_nilai = """
                        SELECT jenis_pengadaan AS JENIS_PENGADAAN, SUM(pagu) AS NILAI_PAKET
                        FROM df_SPSETenderPengumuman_filter GROUP BY JENIS_PENGADAAN ORDER BY NILAI_PAKET DESC
                    """
                    
                    tabel_jp_nilai_trx = con.execute(sql_jp_nilai).df()

                    grafik_jp_2_1, grafik_jp_2_2 = st.columns((3,7))

                    with grafik_jp_2_1:

                        st.dataframe(
                            tabel_jp_nilai_trx,
                            column_config={
                                "JENIS_PENGADAAN": "JENIS PENGADAAN",
                                "NILAI_PAKET": "NILAI PAKET"
                            },
                            use_container_width=True,
                            hide_index=True    
                        )

                    with grafik_jp_2_2:

                        st.bar_chart(tabel_jp_nilai_trx, x="JENIS_PENGADAAN", y="NILAI_PAKET", color="JENIS_PENGADAAN")

            with st.container(border=True):

                ### Tabel dan Grafik Jumlah dan Nilai Transaksi SPSE - Tender - Pengumuman Berdasarkan Metode Pemilihan
                grafik_mp_1, grafik_mp_2 = st.tabs(["| Berdasarkan Jumlah Metode Pemilihan |", "| Berdasarkan Nilai Metode Pemilihan |"])

                with grafik_mp_1:

                    st.subheader("Berdasarkan Jumlah Metode Pemilihan")

                    #### Query data grafik jumlah transaksi pengumuman SPSE berdasarkan Metode Pemilihan

                    sql_mp_jumlah = """
                        SELECT mtd_pemilihan AS METODE_PEMILIHAN, COUNT(DISTINCT(kd_tender)) AS JUMLAH_PAKET
                        FROM df_SPSETenderPengumuman_filter GROUP BY METODE_PEMILIHAN ORDER BY JUMLAH_PAKET DESC
                    """
                    
                    tabel_mp_jumlah_trx = con.execute(sql_mp_jumlah).df()

                    grafik_mp_1_1, grafik_mp_1_2 = st.columns((3,7))

                    with grafik_mp_1_1:

                        st.dataframe(
                            tabel_mp_jumlah_trx,
                            column_config={
                                "METODE_PEMILIHAN": "METODE PEMILIHAN",
                                "JUMLAH_PAKET": "JUMLAH PAKET"
                            },
                            use_container_width=True,
                            hide_index=True
                        )

                    with grafik_mp_1_2:

                        st.bar_chart(tabel_mp_jumlah_trx, x="METODE_PEMILIHAN", y="JUMLAH_PAKET", color="METODE_PEMILIHAN")
            
                with grafik_mp_2:

                    st.subheader("Berdasarkan Nilai Metode Pemilihan")

                    #### Query data grafik nilai transaksi pengumuman SPSE berdasarkan Metode Pemilihan

                    sql_mp_nilai = """
                        SELECT mtd_pemilihan AS METODE_PEMILIHAN, SUM(pagu) AS NILAI_PAKET
                        FROM df_SPSETenderPengumuman_filter GROUP BY METODE_PEMILIHAN ORDER BY NILAI_PAKET DESC
                    """
                    
                    tabel_mp_nilai_trx = con.execute(sql_mp_nilai).df()

                    grafik_mp_2_1, grafik_mp_2_2 = st.columns((3,7))

                    with grafik_mp_2_1:

                        st.dataframe(
                            tabel_mp_nilai_trx,
                            column_config={
                                "METODE_PEMILIHAN": "METODE PEMILIHAN",
                                "NILAI_PAKET": "JUMLAH PAKET"
                            },
                            use_container_width=True,
                            hide_index=True
                        )

                    with grafik_mp_2_2:

                        st.bar_chart(tabel_mp_nilai_trx, x="METODE_PEMILIHAN", y="NILAI_PAKET", color="METODE_PEMILIHAN")

            with st.container(border=True):

                ### Tabel dan Grafik Jumlah dan Nilai Transaksi SPSE - Tender - Pengumuman Berdasarkan Metode Evaluasi
                grafik_me_1, grafik_me_2 = st.tabs(["| Berdasarkan Jumlah Metode Evaluasi |", "| Berdasarkan Nilai Metode Evaluasi |"])

                with grafik_me_1:

                    st.subheader("Berdasarkan Jumlah Metode Evaluasi")

                    #### Query data grafik jumlah transaksi pengumuman SPSE berdasarkan Metode Evaluasi

                    sql_me_jumlah = """
                        SELECT mtd_evaluasi AS METODE_EVALUASI, COUNT(DISTINCT(kd_tender)) AS JUMLAH_PAKET
                        FROM df_SPSETenderPengumuman_filter GROUP BY METODE_EVALUASI ORDER BY JUMLAH_PAKET DESC
                    """
                    
                    tabel_me_jumlah_trx = con.execute(sql_me_jumlah).df()

                    grafik_me_1_1, grafik_me_1_2 = st.columns((3,7))

                    with grafik_me_1_1:

                        st.dataframe(
                            tabel_me_jumlah_trx,
                            column_config={
                                "METODE_EVALUASI": "METODE EVALUASI",
                                "JUMLAH_PAKET": "JUMLAH PAKET"
                            },
                            use_container_width=True,
                            hide_index=True    
                        )

                    with grafik_me_1_2:

                        st.bar_chart(tabel_me_jumlah_trx, x="METODE_EVALUASI", y="JUMLAH_PAKET", color="METODE_EVALUASI")
            
                with grafik_me_2:

                    st.subheader("Berdasarkan Nilai Metode Evaluasi")

                    #### Query data grafik nilai transaksi pengumuman SPSE berdasarkan Metode Evaluasi

                    sql_me_nilai = """
                        SELECT mtd_evaluasi AS METODE_EVALUASI, SUM(pagu) AS NILAI_PAKET
                        FROM df_SPSETenderPengumuman_filter GROUP BY METODE_EVALUASI ORDER BY NILAI_PAKET DESC
                    """
                    
                    tabel_me_nilai_trx = con.execute(sql_me_nilai).df()

                    grafik_me_2_1, grafik_me_2_2 = st.columns((3,7))

                    with grafik_me_2_1:

                        st.dataframe(
                            tabel_me_nilai_trx,
                            column_config={
                                "METODE_EVALUASI": "METODE EVALUASI",
                                "NILAI_PAKET": "NILAI PAKET"
                            },
                            use_container_width=True,
                            hide_index=True    
                        )

                    with grafik_me_2_2:

                        st.bar_chart(tabel_me_nilai_trx, x="METODE_EVALUASI", y="NILAI_PAKET", color="METODE_EVALUASI")

            with st.container(border=True):

                ### Tabel dan Grafik Jumlah dan Nilai Transaksi SPSE - Tender - Pengumuman Berdasarkan Metode Kualifikasi
                grafik_mk_1, grafik_mk_2 = st.tabs(["| Berdasarkan Jumlah Metode Kualifikasi |", "| Berdasarkan Nilai Metode Kualifikasi |"])

                with grafik_mk_1:

                    st.subheader("Berdasarkan Jumlah Metode Kualifikasi")

                    #### Query data grafik jumlah transaksi pengumuman SPSE berdasarkan Metode Kualifikasi

                    sql_mk_jumlah = """
                        SELECT mtd_kualifikasi AS METODE_KUALIFIKASI, COUNT(DISTINCT(kd_tender)) AS JUMLAH_PAKET
                        FROM df_SPSETenderPengumuman_filter GROUP BY METODE_KUALIFIKASI ORDER BY JUMLAH_PAKET DESC
                    """
                    
                    tabel_mk_jumlah_trx = con.execute(sql_mk_jumlah).df()

                    grafik_mk_1_1, grafik_mk_1_2 = st.columns((3,7))

                    with grafik_mk_1_1:

                        st.dataframe(
                            tabel_mk_jumlah_trx,
                            column_config={
                                "METODE_KUALIFIKASI": "METODE KUALIFIKASI",
                                "JUMLAH_PAKET": "JUMLAH PAKET"
                            },
                            use_container_width=True,
                            hide_index=True    
                        )

                    with grafik_mk_1_2:

                        st.bar_chart(tabel_mk_jumlah_trx, x="METODE_KUALIFIKASI", y="JUMLAH_PAKET", color="METODE_KUALIFIKASI")
            
                with grafik_mk_2:

                    st.subheader("Berdasarkan Nilai Metode Kualifikasi")

                    #### Query data grafik nilai transaksi pengumuman SPSE berdasarkan Metode Kualifikasi

                    sql_mk_nilai = """
                        SELECT mtd_kualifikasi AS METODE_KUALIFIKASI, SUM(pagu) AS NILAI_PAKET
                        FROM df_SPSETenderPengumuman_filter GROUP BY METODE_KUALIFIKASI ORDER BY NILAI_PAKET DESC
                    """
                    
                    tabel_mk_nilai_trx = con.execute(sql_mk_nilai).df()

                    grafik_mk_2_1, grafik_mk_2_2 = st.columns((3,7))

                    with grafik_mk_2_1:

                        st.dataframe(
                            tabel_mk_nilai_trx,
                            column_config={
                                "METODE_KUALIFIKASI": "METODE KUALIFIKASI",
                                "NILAI_PAKET": "NILAI PAKET"
                            },
                            use_container_width=True,
                            hide_index=True
                        )

                    with grafik_mk_2_2:

                        st.bar_chart(tabel_mk_nilai_trx, x="METODE_KUALIFIKASI", y="NILAI_PAKET", color="METODE_KUALIFIKASI")

            with st.container(border=True):

                ### Tabel dan Grafik Jumlah dan Nilai Transaksi SPSE - Tender - Pengumuman Berdasarkan Kontrak Pembayaran
                grafik_kontrak_1, grafik_kontrak_2 = st.tabs(["| Berdasarkan Jumlah Kontrak Pembayaran |", "| Berdasarkan Nilai Kontrak Pembayaran |"])

                with grafik_kontrak_1:

                    st.subheader("Berdasarkan Jumlah Kontrak Pembayaran")

                    #### Query data grafik jumlah transaksi pengumuman SPSE berdasarkan Kontrak Pembayaran

                    sql_kontrak_jumlah = """
                        SELECT kontrak_pembayaran AS KONTRAK_PEMBAYARAN, COUNT(DISTINCT(kd_tender)) AS JUMLAH_PAKET
                        FROM df_SPSETenderPengumuman_filter GROUP BY KONTRAK_PEMBAYARAN ORDER BY JUMLAH_PAKET DESC
                    """
                    
                    tabel_kontrak_jumlah_trx = con.execute(sql_kontrak_jumlah).df()

                    grafik_kontrak_1_1, grafik_kontrak_1_2 = st.columns((3,7))

                    with grafik_kontrak_1_1:

                        st.dataframe(
                            tabel_kontrak_jumlah_trx,
                            column_config={
                                "KONTRAK_PEMBAYARAN": "KONTRAK PEMBAYARAN",
                                "JUMLAH_PAKET": "JUMLAH PAKET"
                            },
                            use_container_width=True,
                            hide_index=True    
                        )

                    with grafik_kontrak_1_2:

                        st.bar_chart(tabel_kontrak_jumlah_trx, x="KONTRAK_PEMBAYARAN", y="JUMLAH_PAKET", color="KONTRAK_PEMBAYARAN")
            
                with grafik_kontrak_2:

                    st.subheader("Berdasarkan Nilai Kontrak Pembayaran")

                    #### Query data grafik nilai transaksi pengumuman SPSE berdasarkan Kontrak Pembayaran

                    sql_kontrak_nilai = """
                        SELECT kontrak_pembayaran AS KONTRAK_PEMBAYARAN, SUM(pagu) AS NILAI_PAKET
                        FROM df_SPSETenderPengumuman_filter GROUP BY KONTRAK_PEMBAYARAN ORDER BY NILAI_PAKET DESC
                    """
                    
                    tabel_kontrak_nilai_trx = con.execute(sql_kontrak_nilai).df()

                    grafik_kontrak_2_1, grafik_kontrak_2_2 = st.columns((3,7))

                    with grafik_kontrak_2_1:

                        st.dataframe(
                            tabel_kontrak_nilai_trx, 
                            column_config={
                                "KONTRAK_PEMBAYARAN": "KONTRAK PEMBAYARAN",
                                "NILAI_PAKET": "NILAI PAKET"
                            }    
                        )

                    with grafik_kontrak_2_2:

                        st.bar_chart(tabel_kontrak_nilai_trx, x="KONTRAK_PEMBAYARAN", y="NILAI_PAKET", color="KONTRAK_PEMBAYARAN")

        except Exception:

            st.error("Gagal Baca Dataset SPSE - Tender - Pengumuman")

    ### Tab Sub Menu SPSE - Tender - SPPBJ
    with menu_spse_1_2:

        try:

            ### Analisa DATA SPSE - TENDER - SPPBJ
            df_SPSETenderSPPBJ = tarik_data_parquet(DatasetSPSETenderSPPBJ)

            ### Unduh Dataframe Data SPSE - Tender - SPPBJ
            unduh_SPSE_Tender_SPPBJ_excel = download_excel(df_SPSETenderSPPBJ)

            SPSE_SPPBJ_1, SPSE_SPPBJ_2 = st.columns((7,3))
            with SPSE_SPPBJ_1:
                st.subheader("SPSE - TENDER - SPPBJ")
            with SPSE_SPPBJ_2:
                st.download_button(
                    label = "📥 Download Data Tender SPPBJ",
                    data = unduh_SPSE_Tender_SPPBJ_excel,
                    file_name = f"SPSETenderSPPBJ-{kodeFolder}-{tahun}.xlsx",
                    mime = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )

            st.divider()

            jumlah_trx_spse_sppbj_total = df_SPSETenderSPPBJ['kd_tender'].unique().shape[0]
            nilai_trx_spse_sppbj_final_total = df_SPSETenderSPPBJ['harga_final'].sum()

            data_sppbj_total_1, data_sppbj_total_2 = st.columns(2)
            data_sppbj_total_1.metric(label="Jumlah Total Tender SPPBJ", value="{:,}".format(jumlah_trx_spse_sppbj_total))
            data_sppbj_total_2.metric(label="Nilai Total Tender SPPBJ", value="{:,.2f}".format(nilai_trx_spse_sppbj_final_total))

            st.divider()

            SPSE_SPPBJ_radio_1, SPSE_SPPBJ_radio_2 = st.columns((2,8))
            with SPSE_SPPBJ_radio_1:
                status_kontrak_TSPPBJ = st.radio("**Status Kontrak**", df_SPSETenderSPPBJ['status_kontrak'].unique(), key='Tender_Status_SPPBJ')
            with SPSE_SPPBJ_radio_2:
                opd_TSPPBJ = st.selectbox("Pilih Perangkat Daerah :", df_SPSETenderSPPBJ['nama_satker'].unique(), key='Tender_OPD_SPPBJ')
            st.write(f"Anda memilih : **{status_kontrak_TSPPBJ}** dari **{opd_TSPPBJ}**")

            df_SPSETenderSPPBJ_filter = con.execute(f"SELECT * FROM df_SPSETenderSPPBJ WHERE status_kontrak = '{status_kontrak_TSPPBJ}' AND nama_satker = '{opd_TSPPBJ}'").df()
            jumlah_trx_spse_sppbj = df_SPSETenderSPPBJ_filter['kd_tender'].unique().shape[0]
            nilai_trx_spse_sppbj_final = df_SPSETenderSPPBJ_filter['harga_final'].sum()

            data_sppbj_1, data_sppbj_2 = st.columns(2)
            data_sppbj_1.metric(label="Jumlah Tender SPPBJ", value="{:,}".format(jumlah_trx_spse_sppbj))
            data_sppbj_2.metric(label="Nilai Tender SPPBJ", value="{:,.2f}".format(nilai_trx_spse_sppbj_final))

            st.divider()
            
            sql_tender_sppbj_trx = """
                SELECT nama_paket AS NAMA_PAKET, no_sppbj AS NO_SPPBJ, tgl_sppbj AS TGL_SPPBJ, 
                nama_ppk AS NAMA_PPK, nama_penyedia AS NAMA_PENYEDIA, npwp_penyedia AS NPWP_PENYEDIA, 
                harga_final AS HARGA_FINAL FROM df_SPSETenderSPPBJ_filter
            """
            tabel_tender_sppbj_tampil = con.execute(sql_tender_sppbj_trx).df()

            ### Tabel SPSE - Tender - SPPBJ
            st.dataframe(
                tabel_tender_sppbj_tampil, 
                column_config={
                    "NAMA_PAKET": "NAMA PAKET",
                    "NO_SPPBJ": "NO SPPBJ",
                    "TGL_SPPBJ": "TGL SPPBJ",
                    "NAMA_PPK": "NAMA PPK",
                    "NAMA_PENYEDIA": "NAMA PENYEDIA",
                    "NPWP_PENYEDIA": "NPWP PENYEDIA",
                    "HARGA_FINAL": "HARGA FINAL"
                },
                use_container_width=True,
                hide_index=True
            ) 

        except Exception:
            st.error("Gagal Baca Dataset SPSE - Tender - SPPBJ")

    ### Tab Sub Menu SPSE - Tender - Kontrak
    with menu_spse_1_3:

        try:

            ### Analisa DATA SPSE - TENDER - KONTRAK
            df_SPSETenderKontrak = tarik_data_parquet(DatasetSPSETenderKontrak)

            ### Unduh Dataframe Data SPSE - Tender - Kontrak
            unduh_SPSE_Tender_KONTRAK_excel = download_excel(df_SPSETenderKontrak)

            SPSE_KONTRAK_1, SPSE_KONTRAK_2 = st.columns((7,3))
            with SPSE_KONTRAK_1:
                st.subheader("SPSE - TENDER - KONTRAK")
            with SPSE_KONTRAK_2:
                st.download_button(
                    label = "📥 Download Data Tender Kontrak",
                    data = unduh_SPSE_Tender_KONTRAK_excel,
                    file_name = f"SPSETenderKontrak-{kodeFolder}-{tahun}.xlsx",
                    mime = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )

            st.divider()

            jumlah_trx_spse_kontrak_total = df_SPSETenderKontrak['kd_tender'].unique().shape[0]
            nilai_trx_spse_kontrak_nilaikontrak_total = df_SPSETenderKontrak['nilai_kontrak'].sum()

            data_kontrak_total_1, data_kontrak_total_2 = st.columns(2)
            data_kontrak_total_1.metric(label="Jumlah Total Tender Berkontrak", value="{:,}".format(jumlah_trx_spse_kontrak_total))
            data_kontrak_total_2.metric(label="Nilai Total Tender Berkontrak", value="{:,.2f}".format(nilai_trx_spse_kontrak_nilaikontrak_total))

            st.divider()

            SPSE_KONTRAK_radio_1, SPSE_KONTRAK_radio_2 = st.columns((2,8))
            with SPSE_KONTRAK_radio_1:
                status_kontrak_TKONTRAK = st.radio("**Status Kontrak**", df_SPSETenderKontrak['status_kontrak'].unique(), key='Tender_Status_Kontrak')
            with SPSE_KONTRAK_radio_2:
                opd_TKONTRAK = st.selectbox("Pilih Perangkat Daerah :", df_SPSETenderKontrak['nama_satker'].unique(), key='Tender_OPD_Kontrak')
            st.write(f"Anda memilih : **{status_kontrak_TKONTRAK}** dari **{opd_TKONTRAK}**")

            df_SPSETenderKontrak_filter = con.execute(f"SELECT * FROM df_SPSETenderKontrak WHERE status_kontrak = '{status_kontrak_TKONTRAK}' AND nama_satker = '{opd_TKONTRAK}'").df()
            jumlah_trx_spse_kontrak = df_SPSETenderKontrak_filter['kd_tender'].unique().shape[0]
            nilai_trx_spse_kontrak_nilaikontrak = df_SPSETenderKontrak_filter['nilai_kontrak'].sum()

            data_kontrak_1, data_kontrak_2 = st.columns(2)
            data_kontrak_1.metric(label="Jumlah Tender Berkontrak", value="{:,}".format(jumlah_trx_spse_kontrak))
            data_kontrak_2.metric(label="Nilai Tender Berkontrak", value="{:,.2f}".format(nilai_trx_spse_kontrak_nilaikontrak))

            st.divider()

            sql_tender_kontrak_trx = """
                SELECT nama_paket AS NAMA_PAKET, no_kontrak AS NO_KONTRAK, tgl_kontrak AS TGL_KONTRAK,
                nama_ppk AS NAMA_PPK, nama_penyedia AS NAMA_PENYEDIA, wakil_sah_penyedia AS WAKIL_SAH,
                npwp_penyedia AS NPWP_PENYEDIA, nilai_kontrak AS NILAI_KONTRAK, nilai_pdn_kontrak AS NILAI_PDN, nilai_umk_kontrak AS NILAI_UMK
                FROM df_SPSETenderKontrak_filter 
            """
            tabel_tender_kontrak_tampil = con.execute(sql_tender_kontrak_trx).df()

            ### Tabel SPSE - Tender - Kontrak
            st.dataframe(
                tabel_tender_kontrak_tampil, 
                column_config={
                    "NAMA_PAKET": "NAMA PAKET",
                    "NO_KONTRAK": "NO KONTRAK",
                    "TGL_KONTRAK": "TGL KONTRAK",
                    "NAMA_PPK": "NAMA PPK",
                    "NAMA_PENYEDIA": "NAMA PENYEDIA",
                    "NILAI_KONTRAK": "NILAI_KONTRAK",
                    "NILAI_PDN": "NILAI PDN",
                    "NILAI_UMK": "NILAI UMK"
                },
                use_container_width=True,
                hide_index=True
            )

        except Exception:
            st.error("Gagal Baca Dataset SPSE - Tender - Kontrak")

    ### Tab Sub Menu SPSE - Tender - SPMK
    with menu_spse_1_4:

        try:

            ### Analisa DATA SPSE - TENDER - SPMK 
            df_SPSETenderKontrak = tarik_data_parquet(DatasetSPSETenderKontrak)
            df_SPSETenderSPMK = tarik_data_parquet(DatasetSPSETenderSPMK)

            df_SPSETenderKontrak_filter_kolom = df_SPSETenderKontrak[["kd_tender", "nilai_kontrak", "nilai_pdn_kontrak", "nilai_umk_kontrak"]]
            df_SPSETenderSPMK_OK = df_SPSETenderSPMK.merge(df_SPSETenderKontrak_filter_kolom, how='left', on='kd_tender')

            ### Unduh Dataframe Data SPSE - Tender - SPMK
            unduh_SPSE_Tender_SPMK_excel = download_excel(df_SPSETenderSPMK_OK)

            SPSE_SPMK_1, SPSE_SPMK_2 = st.columns((7,3))
            with SPSE_SPMK_1:
                st.subheader("SPSE - TENDER - SPMK")
            with SPSE_SPMK_2:
                st.download_button(
                    label = "📥 Download Data Tender SPMK",
                    data = unduh_SPSE_Tender_SPMK_excel,
                    file_name = f"SPSETenderSPMK-{kodeFolder}-{tahun}.xlsx",
                    mime = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )

            st.divider()

            jumlah_trx_spse_spmk_total = df_SPSETenderSPMK_OK['kd_tender'].unique().shape[0]
            nilai_trx_spse_spmk_nilaikontrak_total = df_SPSETenderSPMK_OK['nilai_kontrak'].sum()

            data_spmk_total_1, data_spmk_total_2 = st.columns(2)
            data_spmk_total_1.metric(label="Jumlah Total Tender SPMK", value="{:,}".format(jumlah_trx_spse_spmk_total))
            data_spmk_total_2.metric(label="Nilai Total Tender SPMK", value="{:,.2f}".format(nilai_trx_spse_spmk_nilaikontrak_total))
            
            st.divider()
            
            opd_TSPMK = st.selectbox("Pilih Perangkat Daerah :", df_SPSETenderSPMK_OK['nama_satker'].unique(), key='Tender_OPD_SPMK')
            st.write(f"Anda memilih : **{opd_TSPMK}**")

            df_SPSETenderSPMK_filter = con.execute(f"SELECT * FROM df_SPSETenderSPMK_OK WHERE nama_satker = '{opd_TSPMK}'").df()
            jumlah_trx_spse_spmk = df_SPSETenderSPMK_filter['kd_tender'].unique().shape[0]
            nilai_trx_spse_spmk_nilaikontrak = df_SPSETenderSPMK_filter['nilai_kontrak'].sum()

            data_spmk_1, data_spmk_2 = st.columns(2)
            data_spmk_1.metric(label="Jumlah Tender SPMK", value="{:,}".format(jumlah_trx_spse_spmk))
            data_spmk_2.metric(label="Nilai Tender SPMK", value="{:,.2f}".format(nilai_trx_spse_spmk_nilaikontrak))

            st.divider()

            sql_tender_spmk_trx = """
                SELECT nama_paket AS NAMA_PAKET, no_spmk_spp AS NO_SPMK, tgl_spmk_spp AS TGL_SPMK,
                nama_ppk AS NAMA_PPK, nama_penyedia AS NAMA_PENYEDIA, wakil_sah_penyedia AS WAKIL_SAH,
                npwp_penyedia AS NPWP_PENYEDIA, nilai_kontrak AS NILAI_KONTRAK, nilai_pdn_kontrak AS NILAI_PDN, nilai_umk_kontrak AS NILAI_UMK
                FROM df_SPSETenderSPMK_filter 
            """
            tabel_tender_spmk_tampil = con.execute(sql_tender_spmk_trx).df()
            
            ### Tabel SPSE - Tender - SPMK
            st.dataframe(
                tabel_tender_spmk_tampil,
                column_config={
                    "NAMA_PAKET": "NAMA PAKET",
                    "NO_SPMK": "NO SPMK",
                    "TGL_SPMK": "TGL SPMK",
                    "NAMA_PPK": "NAMA PPK",
                    "NAMA_PENYEDIA": "NAMA PENYEDIA",
                    "WAKIL_SAH": "WAKIL SAH",
                    "NPWP_PENYEDIA": "NPWP PENYEDIA",
                    "NILAI_KONTRAK": "NILAI KONTRAK",
                    "NILAI_PDN": "NILAI PDN",
                    "NILAI_UMK": "NILAI UMK"
                },
                use_container_width=True,
                hide_index=True
            )

        except Exception:
            st.error("Gagal Baca Dtaset SPSE - Tender - SPMK")        


    ### Tab Sub Menu SPSE - Tender - BAPBAST
    with menu_spse_1_5:

        try:
            ### Analisa DATA SPSE - TENDER - BAPBAST
            df_SPSETenderBAST = tarik_data_parquet(DatasetSPSETenderBAST)
        
            ### Unduh Dataframe Data SPSE - Tender - BAPBAST
            unduh_SPSE_Tender_BAST_excel = download_excel(df_SPSETenderBAST)

            SPSE_BAST_1, SPSE_BAST_2 = st.columns((7,3))
            with SPSE_BAST_1:
                st.subheader("SPSE - TENDER - BAPBAST")
            with SPSE_BAST_2:
                st.download_button(
                    label = "📥 Download Data Tender BAPBAST",
                    data = unduh_SPSE_Tender_BAST_excel,
                    file_name = f"SPSETenderBAPBAST-{kodeFolder}-{tahun}.xlsx",
                    mime = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )

            st.divider()

            jumlah_trx_spse_bast_total = df_SPSETenderBAST['kd_tender'].unique().shape[0]
            nilai_trx_spse_bast_total = df_SPSETenderBAST['nilai_kontrak'].sum()

            data_bast_total_1, data_bast_total_2 = st.columns(2)
            data_bast_total_1.metric(label="Jumlah Total Tender BAPBAST", value="{:,}".format(jumlah_trx_spse_bast_total))
            data_bast_total_2.metric(label="Nilai Total Tender BAPBAST", value="{:,.2f}".format(nilai_trx_spse_bast_total))

            st.divider()

            SPSE_BAST_radio_1, SPSE_BAST_radio_2 = st.columns((2,8))
            with SPSE_BAST_radio_1:
                status_kontrak_TBAST = st.radio("**Status Kontrak**", df_SPSETenderBAST['status_kontrak'].unique(), key='Tender_Status_BAPBAST')
            with SPSE_BAST_radio_2:
                opd_TBAST = st.selectbox("Pilih Perangkat Daerah :", df_SPSETenderBAST['nama_satker'].unique(), key='Tender_OPD_BAPBAST')
            st.write(f"Anda memilih : **{status_kontrak_TBAST}** dari **{opd_TBAST}**")

            df_SPSETenderBAST_filter = con.execute(f"SELECT * FROM df_SPSETenderBAST WHERE status_kontrak = '{status_kontrak_TBAST}' AND nama_satker = '{opd_TBAST}'").df()
            jumlah_trx_spse_bast = df_SPSETenderBAST_filter['kd_tender'].unique().shape[0]
            nilai_trx_spse_bast_nilaikontrak = df_SPSETenderBAST_filter['nilai_kontrak'].sum()

            data_bast_1, data_bast_2 = st.columns(2)
            data_bast_1.metric(label="Jumlah Tender BAPBAST", value="{:,}".format(jumlah_trx_spse_bast))
            data_bast_2.metric(label="Nilai Tender BAPBAST", value="{:,.2f}".format(nilai_trx_spse_bast_nilaikontrak))

            st.divider()

            sql_tender_bast_trx = """
                SELECT nama_paket AS NAMA_PAKET, no_bast AS NO_BAST, tgl_bast AS TGL_BAST,
                nama_ppk AS NAMA_PPK, nama_penyedia AS NAMA_PENYEDIA, wakil_sah_penyedia AS WAKIL_SAH,
                npwp_penyedia AS NPWP_PENYEDIA, nilai_kontrak AS NILAI_KONTRAK, besar_pembayaran AS NILAI_PEMBAYARAN
                FROM df_SPSETenderBAST_filter 
            """
            tabel_tender_bast_tampil = con.execute(sql_tender_bast_trx).df()

            ### Tabel SPSE - Tender - BAPBAST
            st.dataframe(
                tabel_tender_bast_tampil,
                column_config={
                    "NAMA_PAKET": "NAMA PAKET",
                    "NO_BAST": "NO BAST",
                    "TGL_BAST": "TGL BAST",
                    "NAMA_PPK": "NAMA PPK",
                    "NAMA_PENYEDIA": "NAMA PENYEDIA",
                    "WAKIL_SAH": "WAKIL SAH",
                    "NPWP_PENYEDIA": "NPWP PENYEDIA",
                    "NILAI_KONTRAK": "NILAI KONTRAK",
                    "NILAI_PEMBAYARAN": "NILAI PEMBAYARAN"
                },
                use_container_width=True,
                hide_index=True                
            )

        except Exception:
            st.error("Gagal Baca Dataset SPSE - Tender - BAPBAST")

## Tab SPSE - NON TENDER
with menu_spse_2:

    st.header(f"SPSE - NON TENDER - {pilih} - TAHUN {tahun}")

    ### Tab Sub Menu SPSE - Non Tender
    menu_spse_2_1, menu_spse_2_2, menu_spse_2_3, menu_spse_2_4, menu_spse_2_5 = st.tabs(["| PENGUMUMAN |", "| SPPBJ |", "| KONTRAK |", "| SPMK |", "| BAPAST |"])

    ### Tab Sub Menu SPSE - Non Tender - Pengumuman
    with menu_spse_2_1:

        try:

            ### Analisa DATA SPSE - NON TENDER - PENGUMUMAN
            df_SPSENonTenderPengumuman = tarik_data_parquet(DatasetSPSENonTenderPengumuman)

            ### Unduh Dataframe Data SPSE - Non Tender - Pengumuman
            unduh_SPSE_NT_Pengumuman_excel = download_excel(df_SPSENonTenderPengumuman)

            SPSE_NT_Umumkan_1, SPSE_NT_Umumkan_2 = st.columns((7,3))
            with SPSE_NT_Umumkan_1:
                st.subheader("SPSE - NON TENDER - PENGUMUMAN")
            with SPSE_NT_Umumkan_2:
                st.download_button(
                    label = "📥 Download Data Pengumuman Non Tender",
                    data = unduh_SPSE_NT_Pengumuman_excel,
                    file_name = f"SPSENonTenderPengumuman-{kodeFolder}-{tahun}.xlsx",
                    mime = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )

            st.divider()

            SPSE_NT_radio_1, SPSE_NT_radio_2, SPSE_NT_radio_3 = st.columns((1,1,8))
            with SPSE_NT_radio_1:
                sumber_dana_nt = st.radio("**Sumber Dana**", df_SPSENonTenderPengumuman['sumber_dana'].unique(), key="Sumber_Dana_NT_Pengumuman")
            with SPSE_NT_radio_2:
                status_nontender = st.radio("**Status Non Tender**", df_SPSENonTenderPengumuman['status_nontender'].unique(), key="Status_NT_Pengumuman")
            st.write(f"Anda memilih : **{sumber_dana_nt}** dan **{status_nontender}**")

            df_SPSENonTenderPengumuman_filter = con.execute(f"SELECT kd_nontender, pagu, hps, kualifikasi_paket, jenis_pengadaan, mtd_pemilihan, kontrak_pembayaran FROM df_SPSENonTenderPengumuman WHERE sumber_dana = '{sumber_dana_nt}' AND status_nontender = '{status_nontender}'").df()
            jumlah_trx_spse_nt_pengumuman = df_SPSENonTenderPengumuman_filter['kd_nontender'].unique().shape[0]
            nilai_trx_spse_nt_pengumuman_pagu = df_SPSENonTenderPengumuman_filter['pagu'].sum()
            nilai_trx_spse_nt_pengumuman_hps = df_SPSENonTenderPengumuman_filter['hps'].sum()

            data_umum_nt_1, data_umum_nt_2, data_umum_nt_3 = st.columns(3)
            data_umum_nt_1.metric(label="Jumlah Paket Non Tender Diumumkan", value="{:,}".format(jumlah_trx_spse_nt_pengumuman))
            data_umum_nt_2.metric(label="Nilai Pagu Paket Non Tender Diumumkan", value="{:,}".format(nilai_trx_spse_nt_pengumuman_pagu))
            data_umum_nt_3.metric(label="Nilai HPS Paket Non Tender Diumumkan", value="{:,}".format(nilai_trx_spse_nt_pengumuman_hps))

            st.divider()

            with st.container(border=True):

                ### Tabel dan Grafik Jumlah dan Nilai Transaksi SPSE - Non Tender - Pengumuman Berdasarkan Kualifikasi Paket
                grafik_kp_nt_1, grafik_kp_nt_2 = st.tabs(["| Berdasarkan Jumlah Kualifikasi Paket |", "| Berdasarkan Nilai Kualifikasi Paket |"])

                with grafik_kp_nt_1:

                    st.subheader("Berdasarkan Jumlah Kualifikasi Paket (Non Tender)")

                    #### Query data grafik jumlah transaksi pengumuman SPSE - Non Tender - Pengumuman berdasarkan kualifikasi paket
                    sql_kp_nt_jumlah = """
                        SELECT kualifikasi_paket AS KUALIFIKASI_PAKET, COUNT(DISTINCT(kd_nontender)) AS JUMLAH_PAKET
                        FROM df_SPSENonTenderPengumuman_filter GROUP BY KUALIFIKASI_PAKET ORDER BY JUMLAH_PAKET DESC
                    """
                    
                    tabel_kp_nt_jumlah_trx = con.execute(sql_kp_nt_jumlah).df()

                    grafik_kp_nt_1_1, grafik_kp_nt_1_2 = st.columns((3,7))

                    with grafik_kp_nt_1_1:

                        st.dataframe(
                            tabel_kp_nt_jumlah_trx,
                            column_config={
                                "KUALIFIKASI_PAKET": "KUALIFIKASI PAKET",
                                "JUMLAH_PAKET": "JUMLAH PAKET"
                            },
                            use_container_width=True,
                            hide_index=True
                        )

                    with grafik_kp_nt_1_2:

                        st.bar_chart(tabel_kp_nt_jumlah_trx, x="KUALIFIKASI_PAKET", y="JUMLAH_PAKET", color="KUALIFIKASI_PAKET")

                with grafik_kp_nt_2:

                    st.subheader("Berdasarkan Nilai Kualifikasi Paket (Non Tender)")

                    #### Query data grafik nilai transaksi pengumuman SPSE - Non Tender - Pengumuman berdasarkan kualifikasi paket

                    sql_kp_nt_nilai = """
                        SELECT kualifikasi_paket AS KUALIFIKASI_PAKET, SUM(pagu) AS NILAI_PAKET
                        FROM df_SPSENonTenderPengumuman_filter GROUP BY KUALIFIKASI_PAKET ORDER BY NILAI_PAKET DESC
                    """
                    
                    tabel_kp_nt_nilai_trx = con.execute(sql_kp_nt_nilai).df()

                    grafik_kp_nt_2_1, grafik_kp_nt_2_2 = st.columns((3,7))

                    with grafik_kp_nt_2_1:

                        st.dataframe(
                            tabel_kp_nt_nilai_trx,
                            column_config={
                                "KUALIFIKASI_PAKET": "KUALIFIKASI PAKET",
                                "NILAI_PAKET": "NILAI PAKET (Rp.)"
                            },
                            use_container_width=True,
                            hide_index=True
                        )

                    with grafik_kp_nt_2_2:

                        st.bar_chart(tabel_kp_nt_nilai_trx, x="KUALIFIKASI_PAKET", y="NILAI_PAKET", color="KUALIFIKASI_PAKET")

            with st.container(border=True):

                ### Tabel dan Grafik Jumlah dan Nilai Transaksi SPSE - Non Tender - Pengumuman Berdasarkan Jenis Pengadaan
                grafik_jp_nt_1, grafik_jp_nt_2 = st.tabs(["| Berdasarkan Jumlah Jenis Pengadaan |", "| Berdasarkan Nilai Jenis Pengadaan |"])

                with grafik_jp_nt_1:

                    st.subheader("Berdasarkan Jumlah Jenis Pengadaan (Non Tender)")

                    #### Query data grafik jumlah transaksi  SPSE - Non Tender - Pengumuman berdasarkan Jenis Pengadaan

                    sql_jp_nt_jumlah = """
                        SELECT jenis_pengadaan AS JENIS_PENGADAAN, COUNT(DISTINCT(kd_nontender)) AS JUMLAH_PAKET
                        FROM df_SPSENonTenderPengumuman_filter GROUP BY JENIS_PENGADAAN ORDER BY JUMLAH_PAKET DESC
                    """
                    
                    tabel_jp_nt_jumlah_trx = con.execute(sql_jp_nt_jumlah).df()

                    grafik_jp_nt_1_1, grafik_jp_nt_1_2 = st.columns((3,7))

                    with grafik_jp_nt_1_1:

                        st.dataframe(
                            tabel_jp_nt_jumlah_trx,
                            column_config={
                                "JENIS_PENGADAAN": "JENIS PENGADAAN",
                                "JUMLAH_PAKET": "JUMLAH PAKET"
                            },
                            use_container_width=True,
                            hide_index=True
                        )

                    with grafik_jp_nt_1_2:

                        st.bar_chart(tabel_jp_nt_jumlah_trx, x="JENIS_PENGADAAN", y="JUMLAH_PAKET", color="JENIS_PENGADAAN")
            
                with grafik_jp_nt_2:

                    st.subheader("Berdasarkan Nilai Jenis Pengadaan (Non Tender)")

                    #### Query data grafik nilai transaksi SPSE - Non Tender - Pengumuman berdasarkan Jenis Pengadaan

                    sql_jp_nt_nilai = """
                        SELECT jenis_pengadaan AS JENIS_PENGADAAN, SUM(pagu) AS NILAI_PAKET
                        FROM df_SPSENonTenderPengumuman_filter GROUP BY JENIS_PENGADAAN ORDER BY NILAI_PAKET DESC
                    """
                    
                    tabel_jp_nt_nilai_trx = con.execute(sql_jp_nt_nilai).df()

                    grafik_jp_nt_2_1, grafik_jp_nt_2_2 = st.columns((3,7))

                    with grafik_jp_nt_2_1:

                        st.dataframe(
                            tabel_jp_nt_nilai_trx, 
                            column_config={
                                "JENIS_PENGADAAN": "JENIS PENGADAAN",
                                "NILAI_PAKET": "NILAI PAKET (Rp.)"
                            },
                            use_container_width=True,
                            hide_index=True
                        )

                    with grafik_jp_nt_2_2:

                        st.bar_chart(tabel_jp_nt_nilai_trx, x="JENIS_PENGADAAN", y="NILAI_PAKET", color="JENIS_PENGADAAN")

            with st.container(border=True):

                ### Tabel dan Grafik Jumlah dan Nilai Transaksi SPSE - Non Tender - Pengumuman Berdasarkan Metode Pemilihan
                grafik_mp_nt_1, grafik_mp_nt_2 = st.tabs(["| Berdasarkan Jumlah Metode Pemilihan |", "| Berdasarkan Nilai Metode Pemilihan |"])

                with grafik_mp_nt_1:

                    st.subheader("Berdasarkan Jumlah Metode Pemilihan (Non Tender)")

                    #### Query data grafik jumlah transaksi SPSE - Non Tender - Pengumuman berdasarkan Metode Pemilihan

                    sql_mp_nt_jumlah = """
                        SELECT mtd_pemilihan AS METODE_PEMILIHAN, COUNT(DISTINCT(kd_nontender)) AS JUMLAH_PAKET
                        FROM df_SPSENonTenderPengumuman_filter GROUP BY METODE_PEMILIHAN ORDER BY JUMLAH_PAKET DESC
                    """
                    
                    tabel_mp_nt_jumlah_trx = con.execute(sql_mp_nt_jumlah).df()

                    grafik_mp_nt_1_1, grafik_mp_nt_1_2 = st.columns((3,7))

                    with grafik_mp_nt_1_1:

                        st.dataframe(
                            tabel_mp_nt_jumlah_trx,
                            column_config={
                                "METODE_PEMILIHAN": "METODE PEMILIHAN",
                                "JUMLAH_PAKET": "JUMLAH PAKET"
                            },
                            use_container_width=True,
                            hide_index=True
                        )

                    with grafik_mp_nt_1_2:

                        st.bar_chart(tabel_mp_nt_jumlah_trx, x="METODE_PEMILIHAN", y="JUMLAH_PAKET", color="METODE_PEMILIHAN")
            
                with grafik_mp_nt_2:

                    st.subheader("Berdasarkan Nilai Metode Pemilihan (Non Tender)")

                    #### Query data grafik nilai transaksi SPSE - Non Tender - Pengumuman berdasarkan Metode Pemilihan

                    sql_mp_nt_nilai = """
                        SELECT mtd_pemilihan AS METODE_PEMILIHAN, SUM(pagu) AS NILAI_PAKET
                        FROM df_SPSENonTenderPengumuman_filter GROUP BY METODE_PEMILIHAN ORDER BY NILAI_PAKET DESC
                    """
                    
                    tabel_mp_nt_nilai_trx = con.execute(sql_mp_nt_nilai).df()

                    grafik_mp_nt_2_1, grafik_mp_nt_2_2 = st.columns((3,7))

                    with grafik_mp_nt_2_1:

                        st.dataframe(
                            tabel_mp_nt_nilai_trx,
                            column_config={
                                "METODE_PEMILIHAN": "METODE PEMILIHAN",
                                "NILAI_PAKET": "NILAI PAKET (Rp.)"
                            },
                            use_container_width=True,
                            hide_index=True
                        )

                    with grafik_mp_nt_2_2:

                        st.bar_chart(tabel_mp_nt_nilai_trx, x="METODE_PEMILIHAN", y="NILAI_PAKET", color="METODE_PEMILIHAN")

            with st.container(border=True):

                ### Tabel dan Grafik Jumlah dan Nilai Transaksi SPSE - Non Tender - Pengumuman Berdasarkan Kontrak Pembayaran
                grafik_kontrak_nt_1, grafik_kontrak_nt_2 = st.tabs(["| Berdasarkan Jumlah Kontrak Pembayaran |", "| Berdasarkan Nilai Kontrak Pembayaran |"])

                with grafik_kontrak_nt_1:

                    st.subheader("Berdasarkan Jumlah Kontrak Pembayaran (Non Tender)")

                    #### Query data grafik jumlah transaksi SPSE - Non Tender - Pengumuman berdasarkan Kontrak Pembayaran

                    sql_kontrak_nt_jumlah = """
                        SELECT kontrak_pembayaran AS KONTRAK_PEMBAYARAN, COUNT(DISTINCT(kd_nontender)) AS JUMLAH_PAKET
                        FROM df_SPSENonTenderPengumuman_filter GROUP BY KONTRAK_PEMBAYARAN ORDER BY JUMLAH_PAKET DESC
                    """
                    
                    tabel_kontrak_nt_jumlah_trx = con.execute(sql_kontrak_nt_jumlah).df()

                    grafik_kontrak_nt_1_1, grafik_kontrak_nt_1_2 = st.columns((3,7))

                    with grafik_kontrak_nt_1_1:

                        st.dataframe(
                            tabel_kontrak_nt_jumlah_trx,
                            column_config={
                                "KONTRAK_PEMBAYARAN": "KONTRAK PEMBAYARAN",
                                "JUMLAH_PAKET": "JUMLAH PAKET"
                            },
                            use_container_width=True,
                            hide_index=True
                        )

                    with grafik_kontrak_nt_1_2:

                        st.bar_chart(tabel_kontrak_nt_jumlah_trx, x="KONTRAK_PEMBAYARAN", y="JUMLAH_PAKET", color="KONTRAK_PEMBAYARAN")
            
                with grafik_kontrak_nt_2:

                    st.subheader("Berdasarkan Nilai Kontrak Pembayaran (Non Tender)")

                    #### Query data grafik nilai transaksi SPSE - Non Tender - Pengumuman berdasarkan Kontrak Pembayaran

                    sql_kontrak_nt_nilai = """
                        SELECT kontrak_pembayaran AS KONTRAK_PEMBAYARAN, SUM(pagu) AS NILAI_PAKET
                        FROM df_SPSENonTenderPengumuman_filter GROUP BY KONTRAK_PEMBAYARAN ORDER BY NILAI_PAKET DESC
                    """
                    
                    tabel_kontrak_nt_nilai_trx = con.execute(sql_kontrak_nt_nilai).df()

                    grafik_kontrak_nt_2_1, grafik_kontrak_nt_2_2 = st.columns((3,7))

                    with grafik_kontrak_nt_2_1:

                        st.dataframe(
                            tabel_kontrak_nt_nilai_trx,
                            column_config={
                                "KONTRAK_PEMBAYARAN": "KONTRAK PEMBAYARAN",
                                "NILAI_PAKET": "NILAI PAKET (Rp.)"
                            },
                            use_container_width=True,
                            hide_index=True
                        )

                    with grafik_kontrak_nt_2_2:

                        st.bar_chart(tabel_kontrak_nt_nilai_trx, x="KONTRAK_PEMBAYARAN", y="NILAI_PAKET", color="KONTRAK_PEMBAYARAN")
            
        except Exception:

            st.error("Gagal Baca Dataset SPSE - Non Tender - Pengumuman")


    ### Tab Sub Menu SPSE - Non Tender - SPPBJ
    with menu_spse_2_2:

        try:

            ### Analisa DATA SPSE - NON TENDER - SPPBJ
            df_SPSENonTenderSPPBJ = tarik_data_parquet(DatasetSPSENonTenderSPPBJ)

            ### Unduh Dataframe Data SPSE - Non Tender - SPPBJ
            unduh_SPSE_NT_SPPBJ_excel = download_excel(df_SPSENonTenderSPPBJ)

            SPSE_SPPBJ_NT_1, SPSE_SPPBJ_NT_2 = st.columns((7,3))
            with SPSE_SPPBJ_NT_1:
                st.subheader("SPSE - NON TENDER - SPPBJ")
            with SPSE_SPPBJ_NT_2:
                st.download_button(
                    label = "📥 Download Data Non Tender SPPBJ",
                    data = unduh_SPSE_NT_SPPBJ_excel,
                    file_name = f"SPSENonTenderSPPBJ-{kodeFolder}-{tahun}.xlsx",
                    mime = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )

            st.divider()

            jumlah_trx_spse_nt_sppbj_total = df_SPSENonTenderSPPBJ['kd_nontender'].unique().shape[0]
            nilai_trx_spse_nt_sppbj_final_total = df_SPSENonTenderSPPBJ['harga_final'].sum()

            data_sppbj_nt_total_1, data_sppbj_nt_total_2 = st.columns(2)
            data_sppbj_nt_total_1.metric(label="Jumlah Total Non Tender SPPBJ", value="{:,}".format(jumlah_trx_spse_nt_sppbj_total))
            data_sppbj_nt_total_2.metric(label="Nilai Total Non Tender SPPBJ", value="{:,.2f}".format(nilai_trx_spse_nt_sppbj_final_total))

            st.divider()

            SPSE_SPPBJ_NT_radio_1, SPSE_SPPBJ_NT_radio_2 = st.columns((2,8))
            with SPSE_SPPBJ_NT_radio_1:
                status_kontrak_nt = st.radio("**Status Kontrak**", df_SPSENonTenderSPPBJ['status_kontrak'].unique())
            with SPSE_SPPBJ_NT_radio_2:
                opd_nt = st.selectbox("Pilih Perangkat Daerah :", df_SPSENonTenderSPPBJ['nama_satker'].unique())
            st.write(f"Anda memilih : **{status_kontrak_nt}** dari **{opd_nt}**")

            df_SPSENonTenderSPPBJ_filter = con.execute(f"SELECT * FROM df_SPSENonTenderSPPBJ WHERE status_kontrak = '{status_kontrak_nt}' AND nama_satker = '{opd_nt}'").df()
            jumlah_trx_spse_nt_sppbj = df_SPSENonTenderSPPBJ_filter['kd_nontender'].unique().shape[0]
            nilai_trx_spse_nt_sppbj_final = df_SPSENonTenderSPPBJ_filter['harga_final'].sum()

            data_sppbj_nt_1, data_sppbj_nt_2 = st.columns(2)
            data_sppbj_nt_1.metric(label="Jumlah Non Tender SPPBJ", value="{:,}".format(jumlah_trx_spse_nt_sppbj))
            data_sppbj_nt_2.metric(label="Nilai Non Tender SPPBJ", value="{:,.2f}".format(nilai_trx_spse_nt_sppbj_final))

            st.divider()

            sql_sppbj_nt_trx = """
                SELECT nama_paket AS NAMA_PAKET, no_sppbj AS NO_SPPBJ, tgl_sppbj AS TGL_SPPBJ, 
                nama_ppk AS NAMA_PPK, nama_penyedia AS NAMA_PENYEDIA, npwp_penyedia AS NPWP_PENYEDIA, 
                harga_final AS HARGA_FINAL FROM df_SPSENonTenderSPPBJ_filter
            """
            tabel_sppbj_nt_tampil = con.execute(sql_sppbj_nt_trx).df()

            ### Tabel SPSE - Non Tender - SPPBJ
            st.dataframe(
                tabel_sppbj_nt_tampil,
                column_config={
                    "NAMA_PAKET": "NAMA PAKET",
                    "NO_SPPBJ": "NO SPPBJ",
                    "TGL_SPPBJ": "TGL SPPBJ",
                    "NAMA_PPK": "NAMA PPK",
                    "NAMA_PENYEDIA": "NAMA PENYEDIA",
                    "NPWP_PENYEDIA": "NPWP PENYEDIA",
                    "HARGA_FINAL": "HARGA FINAL"
                },
                use_container_width=True,
                hide_index=True
            )

        except Exception:

            st.error("Gagal Baca Dataset SPSE - Non Tender - SPPBJ")

    ### Tab Sub Menu SPSE - Non Tender - KONTRAK
    with menu_spse_2_3:

        try:

            ### Analisa DATA SPSE - NON TENDER - KONTRAK
            df_SPSENonTenderKontrak = tarik_data_parquet(DatasetSPSENonTenderKontrak)

            ### Unduh Dataframe Data SPSE - Non Tender - Kontrak
            unduh_SPSE_NT_KONTRAK_excel = download_excel(df_SPSENonTenderKontrak)

            SPSE_KONTRAK_NT_1, SPSE_KONTRAK_NT_2 = st.columns((7,3))
            with SPSE_KONTRAK_NT_1:
                st.subheader("SPSE - NON TENDER - KONTRAK")
            with SPSE_KONTRAK_NT_2:
                st.download_button(
                    label = "📥 Download Data Non Tender KONTRAK",
                    data = unduh_SPSE_NT_KONTRAK_excel,
                    file_name = f"SPSENonTenderKONTRAK-{kodeFolder}-{tahun}.xlsx",
                    mime = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )

            st.divider()

            jumlah_trx_spse_nt_kontrak_total = df_SPSENonTenderKontrak['kd_nontender'].unique().shape[0]
            nilai_trx_spse_nt_kontrak_total = df_SPSENonTenderKontrak['nilai_kontrak'].sum()

            data_kontrak_nt_total_1, data_kontrak_nt_total_2 = st.columns(2)
            data_kontrak_nt_total_1.metric(label="Jumlah Total Non Tender KONTRAK", value="{:,}".format(jumlah_trx_spse_nt_kontrak_total))
            data_kontrak_nt_total_2.metric(label="Nilai Total Non Tender KONTRAK", value="{:,.2f}".format(nilai_trx_spse_nt_kontrak_total))

            st.divider()

            SPSE_KONTRAK_NT_radio_1, SPSE_KONTRAK_NT_radio_2 = st.columns((2,8))
            with SPSE_KONTRAK_NT_radio_1:
                status_kontrak_nt_kontrak = st.radio("**Status Kontrak**", df_SPSENonTenderKontrak['status_kontrak'].unique(), key='NonTender_Kontrak')
            with SPSE_KONTRAK_NT_radio_2:
                opd_nt_kontrak = st.selectbox("Pilih Perangkat Daerah :", df_SPSENonTenderKontrak['nama_satker'].unique(), key='NonTender_Kontrak_OPD')
            st.write(f"Anda memilih : **{status_kontrak_nt_kontrak}** dari **{opd_nt_kontrak}**")

            df_SPSENonTenderKontrak_filter = con.execute(f"SELECT * FROM df_SPSENonTenderKontrak WHERE status_kontrak = '{status_kontrak_nt_kontrak}' AND nama_satker = '{opd_nt_kontrak}'").df()
            jumlah_trx_spse_nt_kontrak = df_SPSENonTenderKontrak_filter['kd_nontender'].unique().shape[0]
            nilai_trx_spse_nt_kontrak = df_SPSENonTenderKontrak_filter['nilai_kontrak'].sum()
            
            data_kontrak_nt_1, data_kontrak_nt_2 = st.columns(2)
            data_kontrak_nt_1.metric(label="Jumlah Non Tender KONTRAK", value="{:,}".format(jumlah_trx_spse_nt_kontrak))
            data_kontrak_nt_2.metric(label="Nilai Non Tender KONTRAK", value="{:,.2f}".format(nilai_trx_spse_nt_kontrak))

            st.divider()

            sql_kontrak_nt_trx = """
                SELECT nama_paket AS NAMA_PAKET, no_kontrak AS NO_KONTRAK, tgl_kontrak AS TGL_KONTRAK, 
                nama_ppk AS NAMA_PPK, nama_penyedia AS NAMA_PENYEDIA, npwp_penyedia AS NPWP_PENYEDIA, wakil_sah_penyedia AS WAKIL_SAH, 
                nilai_kontrak AS NILAI_KONTRAK, nilai_pdn_kontrak AS NILAI_PDN, nilai_umk_kontrak AS NILAI_UMK FROM df_SPSENonTenderKontrak_filter
            """
            tabel_kontrak_nt_tampil = con.execute(sql_kontrak_nt_trx).df()

            ### Tabel SPSE - Non Tender - Kontrak
            st.dataframe(
                tabel_kontrak_nt_tampil,
                column_config={
                    "NAMA_PAKET": "NAMA PAKET",
                    "NO_KONTRAK": "NO KONTRAK",
                    "TGL_KONTRAK": "TGL KONTRAK",
                    "NAMA_PPK": "NAMA PPK",
                    "NAMA_PENYEDIA": "NAMA PENYEDIA",
                    "NPWP_PENYEDIA": "NPWP PENYEDIA",
                    "WAKIL_SAH": "WAKIL SAH",
                    "NILAI_KONTRAK": "NILAI KONTRAK",
                    "NILAI_PDN": "NILAI PDN",
                    "NILAI_UMK": "NILAI UMK"
                },
                use_container_width=True,
                hide_index=True
            )

        except Exception:

            st.error("Gagal Baca Dataset SPSE - Non Tender - KONTRAK")

    ### Tab Sub Menu SPSE - Non Tender - SPMK
    with menu_spse_2_4:

        try:

            ### Analisa DATA SPSE - NON TENDER - SPMK
            df_SPSENonTenderKontrak = tarik_data_parquet(DatasetSPSENonTenderKontrak)
            df_SPSENonTenderSPMK = tarik_data_parquet(DatasetSPSENonTenderSPMK)

            df_SPSENonTenderKontrak_filter_kolom = df_SPSENonTenderKontrak[["kd_nontender", "nilai_kontrak", "nilai_pdn_kontrak", "nilai_umk_kontrak"]]
            df_SPSENonTenderSPMK_OK = df_SPSENonTenderSPMK.merge(df_SPSENonTenderKontrak_filter_kolom, how='left', on='kd_nontender')

            ### Unduh Dataframe Data SPSE - Non Tender - SPMK
            unduh_SPSE_NT_SPMK_excel = download_excel(df_SPSENonTenderSPMK_OK)

            SPSE_SPMK_NT_1, SPSE_SPMK_NT_2 = st.columns((7,3))
            with SPSE_SPMK_NT_1:
                st.subheader("SPSE - NON TENDER - SPMK")
            with SPSE_SPMK_NT_2:
                st.download_button(
                    label = "📥 Download Data Non Tender SPMK",
                    data = unduh_SPSE_NT_SPMK_excel,
                    file_name = f"SPSENonTenderSPMK-{kodeFolder}-{tahun}.xlsx",
                    mime = "text/csv"
                )

            st.divider()

            jumlah_trx_spse_nt_spmk_total = df_SPSENonTenderSPMK_OK['kd_nontender'].unique().shape[0]
            nilai_trx_spse_nt_spmk_total = df_SPSENonTenderSPMK_OK['nilai_kontrak'].sum()

            data_spmk_nt_total_1, data_spmk_nt_total_2 = st.columns(2)
            data_spmk_nt_total_1.metric(label="Jumlah Total Non Tender SPMK", value="{:,}".format(jumlah_trx_spse_nt_spmk_total))
            data_spmk_nt_total_2.metric(label="Nilai Total Non Tender SPMK", value="{:,.2f}".format(nilai_trx_spse_nt_spmk_total))

            st.divider()

            SPSE_SPMK_NT_radio_1, SPSE_SPMK_NT_radio_2 = st.columns((2,8))
            with SPSE_SPMK_NT_radio_1:
                status_kontrak_nt_spmk = st.radio("**Status Kontrak**", df_SPSENonTenderSPMK_OK['status_kontrak'].unique(), key='NonTender_Status_SPMK')
            with SPSE_SPMK_NT_radio_2:
                opd_nt_spmk = st.selectbox("Pilih Perangkat Daerah :", df_SPSENonTenderSPMK_OK['nama_satker'].unique(), key='NonTender_OPD_SPMK')
            st.write(f"Anda memilih : **{status_kontrak_nt_spmk}** dari **{opd_nt_spmk}**")

            df_SPSENonTenderSPMK_filter = con.execute(f"SELECT * FROM df_SPSENonTenderSPMK_OK WHERE nama_satker = '{opd_nt_spmk}' AND status_kontrak = '{status_kontrak_nt_spmk}'").df()
            jumlah_trx_spse_nt_spmk = df_SPSENonTenderSPMK_filter['kd_nontender'].unique().shape[0]
            nilai_trx_spse_nt_spmk = df_SPSENonTenderSPMK_filter['nilai_kontrak'].sum()

            data_spmk_nt_1, data_spmk_nt_2 = st.columns(2)
            data_spmk_nt_1.metric(label="Jumlah Non Tender SPMK", value="{:,}".format(jumlah_trx_spse_nt_spmk))
            data_spmk_nt_2.metric(label="Nilai Non Tender SPMK", value="{:,.2f}".format(nilai_trx_spse_nt_spmk))

            st.divider()

            sql_spmk_nt_trx = """
                SELECT nama_paket AS NAMA_PAKET, no_spmk_spp AS NO_SPMK, tgl_spmk_spp AS TGL_SPMK, 
                nama_ppk AS NAMA_PPK, nama_penyedia AS NAMA_PENYEDIA, npwp_penyedia AS NPWP_PENYEDIA, wakil_sah_penyedia AS WAKIL_SAH, 
                nilai_kontrak AS NILAI_KONTRAK, nilai_pdn_kontrak AS NILAI_PDN, nilai_umk_kontrak AS NILAI_UMK FROM df_SPSENonTenderSPMK_filter
            """
            tabel_spmk_nt_tampil = con.execute(sql_spmk_nt_trx).df()

            ### Tabel SPSE - Non Tender - SPMK
            st.dataframe(
                tabel_spmk_nt_tampil,
                column_config={
                    "NAMA_PAKET": "NAMA PAKET",
                    "NO_SPMK": "NO SPMK",
                    "TGL_SPMK": "TGL SPMK",
                    "NAMA_PPK": "NAMA PPK",
                    "NAMA_PENYEDIA": "NAMA PENYEDIA",
                    "NPWP_PENYEDIA": "WAKIL SAH",
                    "NILAI_KONTRAK": "NILAI KONTRAK",
                    "NILAI_PDN": "NILAI PDN",
                    "NILAI_UMK": "NILAI UMK"
                },
                use_container_width=True,
                hide_index=True
            )

        except Exception:

            st.error("Gagal Baca Dataset SPSE - Non Tender - SPMK")

    ### Tab Sub Menu SPSE - Non Tender - BAPBAST
    with menu_spse_2_5:

        try:

            ### Analisa DATA SPSE - NON TENDER - BAPBAST
            df_SPSENonTenderBAST = tarik_data_parquet(DatasetSPSENonTenderBAST)

            ### Unduh Dataframe Data SPSE - Non Tender - BAPBAST
            unduh_SPSE_NT_BAST_excel = download_excel(df_SPSENonTenderBAST)

            SPSE_BAST_NT_1, SPSE_BAST_NT_2 = st.columns((7,3))
            with SPSE_BAST_NT_1:
                st.subheader("SPSE - NON TENDER - BAPBAST")
            with SPSE_BAST_NT_2:
                st.download_button(
                    label = "📥 Download Data Non Tender BAPBAST",
                    data = unduh_SPSE_NT_BAST_excel,
                    file_name = f"SPSENonTenderBAPBAST-{kodeFolder}-{tahun}.xlsx",
                    mime = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )

            st.divider()

            jumlah_trx_spse_nt_bast_total = df_SPSENonTenderBAST['kd_nontender'].unique().shape[0]
            nilai_trx_spse_nt_bast_total = df_SPSENonTenderBAST['nilai_kontrak'].sum()

            data_bast_nt_total_1, data_bast_nt_total_2 = st.columns(2)
            data_bast_nt_total_1.metric(label="Jumlah Total Non Tender BAPBAST", value="{:,}".format(jumlah_trx_spse_nt_bast_total))
            data_bast_nt_total_2.metric(label="Nilai Total Non Tender BAPBAST", value="{:,.2f}".format(nilai_trx_spse_nt_bast_total))

            st.divider()

            SPSE_BAST_NT_radio_1, SPSE_BAST_NT_radio_2 = st.columns((2,8))
            with SPSE_BAST_NT_radio_1:
                status_kontrak_nt_bast = st.radio("**Status Kontrak**", df_SPSENonTenderBAST['status_kontrak'].unique(), key='NonTender_Status_BAST')
            with SPSE_BAST_NT_radio_2:
                opd_nt_bast = st.selectbox("Pilih Perangkat Daerah :", df_SPSENonTenderBAST['nama_satker'].unique(), key='NonTender_OPD_BAST')
            st.write(f"Anda memilih : **{status_kontrak_nt_bast}** dari **{opd_nt_bast}**")

            df_SPSENonTenderBAST_filter = con.execute(f"SELECT * FROM df_SPSENonTenderBAST WHERE nama_satker = '{opd_nt_bast}' AND status_kontrak = '{status_kontrak_nt_bast}'").df()
            jumlah_trx_spse_nt_bast = df_SPSENonTenderBAST_filter['kd_nontender'].unique().shape[0]
            nilai_trx_spse_nt_bast = df_SPSENonTenderBAST_filter['nilai_kontrak'].sum()

            data_bast_nt_1, data_bast_nt_2 = st.columns(2)
            data_bast_nt_1.metric(label="Jumlah Non Tender BAPBAST", value="{:,}".format(jumlah_trx_spse_nt_bast))
            data_bast_nt_2.metric(label="Nilai Non Tender BAPBAST", value="{:,.2f}".format(nilai_trx_spse_nt_bast))

            st.divider()

            sql_bast_nt_trx = """
                SELECT nama_paket AS NAMA_PAKET, no_bap AS NO_BAP, tgl_bap AS TGL_BAP, no_bast AS NO_BAST, tgl_bast AS TGL_BAST, 
                nama_ppk AS NAMA_PPK, nama_penyedia AS NAMA_PENYEDIA, npwp_penyedia AS NPWP_PENYEDIA, wakil_sah_penyedia AS WAKIL_SAH, 
                nilai_kontrak AS NILAI_KONTRAK, besar_pembayaran AS NILAI_PEMBAYARAN FROM df_SPSENonTenderBAST_filter
            """
            tabel_bast_nt_tampil = con.execute(sql_bast_nt_trx).df()

            ### Tabel SPSE - Non Tender - BAPBAST
            st.dataframe(
                tabel_bast_nt_tampil,
                column_config={
                    "NAMA_PAKET": "NAMA PAKET",
                    "NO_BAP": "NO BAP",
                    "NO_BAST": "NO BAST",
                    "TGL_BAST": "TGL BAST",
                    "NAMA_PPK": "NAMA PPK",
                    "NAMA_PENYEDIA": "NAMA PENYEDIA",
                    "NPWP_PENYEDIA": "NPWP PENYEDIA",
                    "WAKIL_SAH": "WAKIL SAH",
                    "NILAI_KONTRAK": "NILAI KONTRAK",
                    "NILAI_PEMBAYARAN": "NILAI PEMBAYARAN"
                },
                use_container_width=True,
                hide_index=True
            )

        except Exception:

            st.error("Gagal Baca Dataset SPSE - Non Tender - BAPBAST")

## Tab SPSE - PENCATATAN
with menu_spse_3:

    st.header(f"SPSE - PENCATATAN TRANSAKSI PBJ - {pilih} - TAHUN {tahun}")

    ### Tab Sub Menu SPSE - Pencatatan Transaksi PBJ
    menu_spse_3_1, menu_spse_3_2 = st.tabs(["| Pencatatan Non Tender |", "| Pencatatan Swakelola |"])

    ### Tab Sub Menu SPSE - Pencatatan Non Tender
    with menu_spse_3_1:

        try:

            ### Analisa DATA SPSE - PENCATATAN NON TENDER
            df_CatatNonTenderRealisasi = tarik_data_parquet(DatasetCatatNonTenderRealisasi)
            df_CatatNonTender = tarik_data_parquet(DatasetCatatNonTender)

            ### Gabungkan Dataset
            df_CatatNonTenderRealisasi_filter = df_CatatNonTenderRealisasi[["kd_nontender_pct", "jenis_realisasi", "no_realisasi", "tgl_realisasi", "nilai_realisasi", "nama_penyedia", "npwp_penyedia"]]
            df_CatatNonTender_OK = df_CatatNonTender.merge(df_CatatNonTenderRealisasi_filter, how='left', on='kd_nontender_pct')

            ### Unduh Dataframe Data SPSE - Pencatatan Non Tender
            unduh_CATAT_NT_excel = download_excel(df_CatatNonTender_OK)

            SPSE_CATAT_NonTender_1, SPSE_CATAT_NonTender_2 = st.columns((7,3))
            with SPSE_CATAT_NonTender_1:
                st.subheader(f"PENCATATAN NON TENDER TAHUN {tahun}")
            with SPSE_CATAT_NonTender_2:
                st.download_button(
                    label = "📥 Download Data Pencatatan Non Tender",
                    data = unduh_CATAT_NT_excel,
                    file_name = f"SPSEPencatatanNonTender-{kodeFolder}-{tahun}.xlsx",
                    mime = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )

            st.divider()

            sumber_dana_cnt = st.radio("**Sumber Dana :**", df_CatatNonTender_OK['sumber_dana'].unique(), key="CatatNonTender")
            st.write(f"Anda memilih : **{sumber_dana_cnt}**")

            df_CatatNonTender_OK_filter = df_CatatNonTender_OK.query(f"sumber_dana == '{sumber_dana_cnt}'")
            jumlah_CatatNonTender_Berjalan = df_CatatNonTender_OK_filter.query("status_nontender_pct_ket == 'Paket Sedang Berjalan'")
            jumlah_CatatNonTender_Selesai = df_CatatNonTender_OK_filter.query("status_nontender_pct_ket == 'Paket Selesai'")
            jumlah_CatatNonTender_Dibatalkan = df_CatatNonTender_OK_filter.query("status_nontender_pct_ket == 'Paket Dibatalkan'")

            data_cnt_1, data_cnt_2, data_cnt_3 = st.columns(3)
            data_cnt_1.metric(label="Jumlah Pencatatan NonTender Berjalan", value="{:,}".format(jumlah_CatatNonTender_Berjalan.shape[0]))
            data_cnt_2.metric(label="Jumlah Pencatatan NonTender Selesai", value="{:,}".format(jumlah_CatatNonTender_Selesai.shape[0]))
            data_cnt_3.metric(label="Jumlah Pencatatan NonTender Dibatalkan", value="{:,}".format(jumlah_CatatNonTender_Dibatalkan.shape[0]))

            st.divider()

            with st.container(border=True):

                ### Tabel dan Grafik Jumlah dan Nilai Transaksi Berdasarkan Kategori Pengadaan dan Metode Pemilihan
                grafik_cnt_1, grafik_cnt_2, grafik_cnt_3, grafik_cnt_4 = st.tabs(["| Jumlah Transaksi - Kategori Pengadaan |","| Nilai Transaksi - Kategori Pengadaan |","| Jumlah Transaksi - Metode Pemilihan |","| Nilai Transaksi - Metode Pemilihan |"])
                
                with grafik_cnt_1:

                    st.subheader("Berdasarkan Jumlah Kategori Pemilihan")

                    ##### Query data grafik jumlah transaksi Pencatatan Non Tender berdasarkan Kategori Pengadaan

                    sql_cnt_kp_jumlah = """
                        SELECT kategori_pengadaan AS KATEGORI_PENGADAAN, COUNT(kd_nontender_pct) AS JUMLAH_PAKET
                        FROM df_CatatNonTender_OK_filter GROUP BY KATEGORI_PENGADAAN ORDER BY JUMLAH_PAKET DESC
                    """

                    tabel_cnt_kp_jumlah = con.execute(sql_cnt_kp_jumlah).df()

                    grafik_cnt_1_1, grafik_cnt_1_2 = st.columns((3,7))

                    with grafik_cnt_1_1:

                        st.dataframe(
                            tabel_cnt_kp_jumlah,
                            column_config={
                                "KATEGORI_PENGADAAN": "KATEGORI PENGADAAN",
                                "JUMLAH_PAKET": "JUMLAH PAKET"
                            },
                            use_container_width=True,
                            hide_index=True
                        )

                    with grafik_cnt_1_2:

                        figcntkph = px.pie(tabel_cnt_kp_jumlah, values="JUMLAH_PAKET", names="KATEGORI_PENGADAAN", title="Grafik Pencatatan Non Tender - Jumlah Paket - Kategori Pengadaan", hole=.3)
                        st.plotly_chart(figcntkph, theme="streamlit", use_container_width=True)

                with grafik_cnt_2:

                    st.subheader("Berdasarkan Nilai Kategori Pemilihan")

                    ##### Query data grafik nilai transaksi Pencatatan Non Tender berdasarkan Kategori Pengadaan

                    sql_cnt_kp_nilai = """
                        SELECT kategori_pengadaan AS KATEGORI_PENGADAAN, SUM(nilai_realisasi) AS NILAI_REALISASI
                        FROM df_CatatNonTender_OK_filter GROUP BY KATEGORI_PENGADAAN ORDER BY NILAI_REALISASI
                    """

                    tabel_cnt_kp_nilai = con.execute(sql_cnt_kp_nilai).df()

                    grafik_cnt_2_1, grafik_cnt_2_2 = st.columns((3,7))

                    with grafik_cnt_2_1:

                        st.dataframe(
                            tabel_cnt_kp_nilai,
                            column_config={
                                "KATEGORI_PENGADAAN": "KATEGORI PENGADAAN",
                                "NILAI_REALISASI": "NILAI REALISASI"
                            },
                            use_container_width=True,
                            hide_index=True
                        )    

                    with grafik_cnt_2_2:

                        figcntkpn = px.pie(tabel_cnt_kp_nilai, values="NILAI_REALISASI", names="KATEGORI_PENGADAAN", title="Grafik Pencatatan Non Tender - Nilai Transaksi - Kategori Pengadaan", hole=.3)
                        st.plotly_chart(figcntkpn, theme="streamlit", use_container_width=True)

                with grafik_cnt_3:

                    st.subheader("Berdasarkan Jumlah Metode Pemilihan")

                    ##### Query data grafik jumlah transaksi Pencatatan Non Tender berdasarkan Metode Pemilihan

                    sql_cnt_mp_jumlah = """
                        SELECT mtd_pemilihan AS METODE_PEMILIHAN, COUNT(kd_nontender_pct) AS JUMLAH_PAKET
                        FROM df_CatatNonTender_OK_filter GROUP BY METODE_PEMILIHAN ORDER BY JUMLAH_PAKET DESC
                    """

                    tabel_cnt_mp_jumlah = con.execute(sql_cnt_mp_jumlah).df()

                    grafik_cnt_3_1, grafik_cnt_3_2 = st.columns((3,7))

                    with grafik_cnt_3_1:

                        st.dataframe(
                            tabel_cnt_mp_jumlah,
                            column_config={
                                "METODE_PEMILIHAN": "METODE PEMILIHAN",
                                "JUMLAH_PAKET": "JUMLAH PAKET"
                            },
                            use_container_width=True,
                            hide_index=True
                        )

                    with grafik_cnt_3_2:

                        figcntmph = px.pie(tabel_cnt_mp_jumlah, values="JUMLAH_PAKET", names="METODE_PEMILIHAN", title="Grafik Pencatatan Non Tender - Jumlah Paket - Metode Pemilihan", hole=.3)
                        st.plotly_chart(figcntmph, theme="streamlit", use_container_width=True)

                with grafik_cnt_4:

                    st.subheader("Berdasarkan Nilai Metode Pemilihan")

                    ##### Query data grafik nilai transaksi Pencatatan Non Tender berdasarkan Metode Pemilihan

                    sql_cnt_mp_nilai = """
                        SELECT mtd_pemilihan AS METODE_PEMILIHAN, SUM(nilai_realisasi) AS NILAI_REALISASI
                        FROM df_CatatNonTender_OK_filter GROUP BY METODE_PEMILIHAN ORDER BY NILAI_REALISASI
                    """

                    tabel_cnt_mp_nilai = con.execute(sql_cnt_mp_nilai).df()

                    grafik_cnt_4_1, grafik_cnt_4_2 = st.columns((3,7))

                    with grafik_cnt_4_1:

                        st.dataframe(
                            tabel_cnt_mp_nilai,
                            column_config={
                                "METODE_PEMILIHAN": "METODE PEMILIHAN",
                                "NILAI_REALISASI": "NILAI REALISASI"
                            },
                            use_container_width=True,
                            hide_index=True
                        )    

                    with grafik_cnt_4_2:

                        figcntmpn = px.pie(tabel_cnt_mp_nilai, values="NILAI_REALISASI", names="METODE_PEMILIHAN", title="Grafik Pencatatan Non Tender - Nilai Transaksi - Metode Pemilihan", hole=.3)
                        st.plotly_chart(figcntmpn, theme="streamlit", use_container_width=True)

            st.divider()
            
            SPSE_CNT_radio_1, SPSE_CNT_radio_2 = st.columns((2,8))
            with SPSE_CNT_radio_1:
                status_nontender_cnt = st.radio("**Status NonTender :**", df_CatatNonTender_OK_filter['status_nontender_pct_ket'].unique())
            with SPSE_CNT_radio_2:
                status_opd_cnt = st.selectbox("**Pilih Satker :**", df_CatatNonTender_OK_filter['nama_satker'].unique())

            st.divider()

            sql_CatatNonTender_query = f"""
                SELECT nama_paket AS NAMA_PAKET, jenis_realisasi AS JENIS_REALISASI, no_realisasi AS NO_REALISASI, tgl_realisasi AS TGL_REALISASI, pagu AS PAGU,
                total_realisasi AS TOTAL_REALISASI, nilai_realisasi AS NILAI_REALISASI FROM df_CatatNonTender_OK_filter
                WHERE status_nontender_pct_ket = '{status_nontender_cnt}' AND
                nama_satker = '{status_opd_cnt}'
            """

            sql_CatatNonTender_query_grafik = f"""
                SELECT kategori_pengadaan AS KATEGORI_PENGADAAN, mtd_pemilihan AS METODE_PEMILIHAN, nilai_realisasi AS NILAI_REALISASI
                FROM df_CatatNonTender_OK_filter
                WHERE status_nontender_pct_ket = '{status_nontender_cnt}' AND
                nama_satker = '{status_opd_cnt}'
            """

            df_CatatNonTender_tabel = con.execute(sql_CatatNonTender_query).df()
            df_CatatNonTender_grafik = con.execute(sql_CatatNonTender_query_grafik).df()

            data_cnt_pd_1, data_cnt_pd_2, data_cnt_pd_3, data_cnt_pd_4 = st.columns((2,3,3,2))
            data_cnt_pd_1.subheader("")
            data_cnt_pd_2.metric(label=f"Jumlah Pencatatan Non Tender ({status_nontender_cnt})", value="{:,}".format(df_CatatNonTender_tabel.shape[0]))
            data_cnt_pd_3.metric(label=f"Nilai Total Pencatatan Non Tender ({status_nontender_cnt})", value="{:,}".format(df_CatatNonTender_tabel['NILAI_REALISASI'].sum()))
            data_cnt_pd_4.subheader("")

            st.divider()

            ### Tabel Pencatatan Non Tender
            st.dataframe(
                df_CatatNonTender_tabel, 
                column_config={
                    "NAMA_PAKET": "NAMA PAKET",
                    "JENIS_REALISASI": "JENIS REALISASI",
                    "NO_REALISASI": "NO REALISASI",
                    "TGL_REALISASI": "TGL REALISASI",
                    "PAGU": "PAGU",
                    "TOTAL_REALISASI": "TOTAL REALISASI",
                    "NILAI_REALISASI": "NILAI REALISASI"
                },
                use_container_width=True,
                hide_index=True,
                height=1000
            )

        except Exception:

            st.error("Gagal Baca Dataset SPSE - Pencatatan Non Tender")

    ### Tab Sub Menu SPSE - Pencatatan Swakelola
    with menu_spse_3_2:

        try:

            ### Analisa DATA SPSE - PENCATATAN SWAKELOLA
            df_CatatSwakelola = tarik_data_parquet(DatasetCatatSwakelola)
            df_CatatSwakelolaRealisasi = tarik_data_parquet(DatasetCatatSwakelolaRealisasi)

            ### Gabungkan Dataset
            df_CatatSwakelolaRealisasi_filter = df_CatatSwakelolaRealisasi[["kd_swakelola_pct", "jenis_realisasi", "no_realisasi", "tgl_realisasi", "nilai_realisasi"]] 
            df_CatatSwakelola_OK = df_CatatSwakelola.merge(df_CatatSwakelolaRealisasi_filter, how='left', on='kd_swakelola_pct')

            ### Unduh Dataframe Data SPSE - Pencatatan Swakelola
            unduh_CATAT_Swakelola_excel = download_excel(df_CatatSwakelola_OK)

            SPSE_CATAT_Swakelola_1, SPSE_CATAT_Swakelola_2 = st.columns((7,3))
            with SPSE_CATAT_Swakelola_1:
                st.subheader(f"PENCATATAN SWAKELOLA TAHUN {tahun}")
            with SPSE_CATAT_Swakelola_2:
                st.download_button(
                    label = "📥 Download Data Pencatatan Swakelola",
                    data = unduh_CATAT_Swakelola_excel,
                    file_name = f"SPSEPencatatanSwakelola-{kodeFolder}-{tahun}.xlsx",
                    mime = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )

            st.divider()

            sumber_dana_cs = st.radio("**Sumber Dana :**", df_CatatSwakelola_OK['sumber_dana'].unique(), key="CatatSwakelola")
            st.write(f"Anda memilih : **{sumber_dana_cs}**")

            df_CatatSwakelola_OK_filter = con.execute(f"SELECT * FROM df_CatatSwakelola_OK WHERE sumber_dana = '{sumber_dana_cs}'").df()
            jumlah_CatatSwakelola_Berjalan = con.execute(f"SELECT * FROM df_CatatSwakelola_OK_filter WHERE status_swakelola_pct_ket = 'Paket Sedang Berjalan'").df()
            jumlah_CatatSwakelola_Selesai = con.execute(f"SELECT * FROM df_CatatSwakelola_OK_filter WHERE status_swakelola_pct_ket = 'Paket Selesai'").df()
            jumlah_CatatSwakelola_Dibatalkan = con.execute(f"SELECT * FROM df_CatatSwakelola_OK_filter WHERE status_swakelola_pct_ket = 'Paket Dibatalkan'").df()

            data_cs_1, data_cs_2, data_cs_3 = st.columns(3)
            data_cs_1.metric(label="Jumlah Pencatatan Swakelola Berjalan", value="{:,}".format(jumlah_CatatSwakelola_Berjalan.shape[0]))
            data_cs_2.metric(label="Jumlah Pencacatan Swakelola Selesai", value="{:,}".format(jumlah_CatatSwakelola_Selesai.shape[0]))
            data_cs_3.metric(label="Jumlah Pencatatan Swakelola Dibatalkan", value="{:,}".format(jumlah_CatatSwakelola_Dibatalkan.shape[0]))

            st.divider()

            SPSE_CS_radio_1, SPSE_CS_radio_2 = st.columns((2,8))
            with SPSE_CS_radio_1:
                status_swakelola_cs = st.radio("**Status Swakelola :**", df_CatatSwakelola_OK_filter['status_swakelola_pct_ket'].unique())
            with SPSE_CS_radio_2:
                status_opd_cs = st.selectbox("**Pilih Satker :**", df_CatatSwakelola_OK_filter['nama_satker'].unique())

            st.divider()

            df_CatatSwakelola_tabel = con.execute(f"SELECT nama_paket AS NAMA_PAKET, jenis_realisasi AS JENIS_REALISASI, no_realisasi AS NO_REALISASI, tgl_realisasi AS TGL_REALISASI, pagu AS PAGU, total_realisasi AS TOTAL_REALISASI, nilai_realisasi AS NILAI_REALISASI, nama_ppk AS NAMA_PPK FROM df_CatatSwakelola_OK_filter WHERE nama_satker = '{status_opd_cs}' AND status_swakelola_pct_ket = '{status_swakelola_cs}'").df()

            data_cs_pd_1, data_cs_pd_2, data_cs_pd_3, data_cs_pd_4 = st.columns((2,3,3,2))
            data_cs_pd_1.subheader("")
            data_cs_pd_2.metric(label=f"Jumlah Pencatatan Swakelola ({status_swakelola_cs})", value="{:,}".format(df_CatatSwakelola_tabel.shape[0]))
            data_cs_pd_3.metric(label=f"Nilai Total Pencatatan Swakelola ({status_swakelola_cs})", value="{:,.2f}".format(df_CatatSwakelola_tabel['NILAI_REALISASI'].sum()))
            data_cs_pd_4.subheader("")

            ### Tabel Pencatatan Swakelola
            st.dataframe(
                df_CatatSwakelola_tabel,
                column_config={
                    "NAMA_PAKET": "NAMA PAKET",
                    "JENIS_REALISASI": "JENIS REALISASI",
                    "NO_REALISASI": "NO REALISASI",
                    "TGL_REALISASI": "TGL REALISASI",
                    "PAGU": "PAGU",
                    "TOTAL_REALISASI": "TOTAL REALISASI",
                    "NILAI_REALISASI": "NILAI REALISASI",
                    "NAMA_PPK": "NAMA PPK"
                },
                use_container_width=True,
                hide_index=True,
                height=1000
            )

        except Exception:

            st.error("Gagal Baca Dataset SPSE - Pencatatan Swakelola")

## Tab SPSE - PESERTA TENDER
with menu_spse_4:

    try:

        ### Analisa DATA SPSE - PESERTA TENDER
        df_RUPMasterSatker = tarik_data_parquet(DatasetRUPMasterSatker)
        df_SPSETenderPengumuman = tarik_data_parquet(DatasetSPSETenderPengumuman)
        df_PesertaTender = tarik_data_parquet(DatasetPesertaTender)

        ### Gabungkan Dataset
        df_RUPMasterSatker_filter_pt = df_RUPMasterSatker[["kd_satker_str", "nama_satker"]]
        df_SPSETenderPengumuman_filter_pt = df_SPSETenderPengumuman[["kd_tender", "nama_paket", "pagu", "hps", "sumber_dana"]]

        df_PesertaTenderDetail_1 = df_PesertaTender.merge(df_RUPMasterSatker_filter_pt, how='left', on='kd_satker_str')
        df_PesertaTenderDetail_2 = df_PesertaTenderDetail_1.merge(df_SPSETenderPengumuman_filter_pt, how='left', on='kd_tender')

        ### Unduh Dataframe Data SPSE - PESERTA TENDER
        unduh_Peserta_Tender_excel = download_excel(df_PesertaTenderDetail_2)

        SPSE_PT_D_1, SPSE_PT_D_2 = st.columns((7,3))
        with SPSE_PT_D_1:
            st.header(f"SPSE - PESERTA TENDER - {pilih} - TAHUN {tahun}")
        with SPSE_PT_D_2:
            st.download_button(
                label = "📥 Download Data Peserta Tender",
                data = unduh_Peserta_Tender_excel,
                file_name = f"SPSEPesertaTenderDetail-{kodeFolder}-{tahun}.xlsx",
                mime = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )

        st.divider()

        sumber_dana_pt = st.radio("**Sumber Dana :**", df_PesertaTenderDetail_2['sumber_dana'].unique(), key="DataPesertaTender")
        st.write(f"Anda memilih : **{sumber_dana_pt}**")

        df_PesertaTenderDetail_filter = df_PesertaTenderDetail_2.query(f"sumber_dana == '{sumber_dana_pt}'")
        jumlah_PesertaTender_daftar = df_PesertaTenderDetail_filter.query("nilai_penawaran == 0 and nilai_terkoreksi == 0")
        jumlah_PesertaTender_nawar = df_PesertaTenderDetail_filter.query("nilai_penawaran > 0 and nilai_terkoreksi > 0")
        jumlah_PesertaTender_menang = df_PesertaTenderDetail_filter.query("nilai_penawaran > 0 and nilai_terkoreksi > 0 and pemenang == 1")

        data_pt_1, data_pt_2, data_pt_3, data_pt_4 = st.columns(4)
        data_pt_1.metric(label="Jumlah Peserta Yang Mendaftar", value="{:,}".format(jumlah_PesertaTender_daftar.shape[0]))
        data_pt_2.metric(label="Jumlah Peserta Yang Menawar", value="{:,}".format(jumlah_PesertaTender_nawar.shape[0]))
        data_pt_3.metric(label="Jumlah Peserta Yang Menang", value="{:,}".format(jumlah_PesertaTender_menang.shape[0]))
        data_pt_4.metric(label="Nilai Total Terkoreksi Rp. (Pemenang)", value="{:,.2f}".format(jumlah_PesertaTender_menang['nilai_terkoreksi'].sum()))

        st.divider()

        SPSE_PT_radio_1, SPSE_PT_radio_2 = st.columns((2,8))
        with SPSE_PT_radio_1:
            status_pemenang_pt = st.radio("**Tabel Data Peserta :**", ["PEMENANG", "MENDAFTAR", "MENAWAR"])
        with SPSE_PT_radio_2:
            status_opd_pt = st.selectbox("**Pilih Satker :**", df_PesertaTenderDetail_filter['nama_satker'].unique())

        st.divider()

        if status_pemenang_pt == "PEMENANG":
            jumlah_PeserteTender = con.execute(f"SELECT nama_paket AS NAMA_PAKET, nama_penyedia AS NAMA_PENYEDIA, npwp_penyedia AS NPWP_PENYEDIA, pagu AS PAGU, hps AS HPS, nilai_penawaran AS NILAI_PENAWARAN, nilai_terkoreksi AS NILAI_TERKOREKSI FROM df_PesertaTenderDetail_filter WHERE NAMA_SATKER = '{status_opd_pt}' AND NILAI_PENAWARAN > 0 AND NILAI_TERKOREKSI > 0  AND pemenang = 1").df()
        elif status_pemenang_pt == "MENDAFTAR":
            jumlah_PeserteTender = con.execute(f"SELECT nama_paket AS NAMA_PAKET, nama_penyedia AS NAMA_PENYEDIA, npwp_penyedia AS NPWP_PENYEDIA, pagu AS PAGU, hps AS HPS, nilai_penawaran AS NILAI_PENAWARAN, nilai_terkoreksi AS NILAI_TERKOREKSI FROM df_PesertaTenderDetail_filter WHERE NAMA_SATKER = '{status_opd_pt}' AND NILAI_PENAWARAN = 0 AND NILAI_TERKOREKSI = 0").df()
        else:
            jumlah_PeserteTender = con.execute(f"SELECT nama_paket AS NAMA_PAKET, nama_penyedia AS NAMA_PENYEDIA, npwp_penyedia AS NPWP_PENYEDIA, pagu AS PAGU, hps AS HPS, nilai_penawaran AS NILAI_PENAWARAN, nilai_terkoreksi AS NILAI_TERKOREKSI FROM df_PesertaTenderDetail_filter WHERE NAMA_SATKER = '{status_opd_pt}' AND NILAI_PENAWARAN > 0 AND NILAI_TERKOREKSI > 0").df()

        data_pt_pd_1, data_pt_pd_2, data_pt_pd_3, data_pt_pd_4 = st.columns(4)
        data_pt_pd_1.subheader("")
        data_pt_pd_2.metric(label=f"Jumlah Peserta Tender ({status_pemenang_pt})", value="{:,}".format(jumlah_PeserteTender.shape[0]))
        data_pt_pd_3.metric(label=f"Nilai Total Terkoreksi ({status_pemenang_pt})", value="{:,.2f}".format(jumlah_PeserteTender['NILAI_TERKOREKSI'].sum()))
        data_pt_pd_4.subheader("")

        st.divider()

        ### Tabel Peserta Tender
        st.dataframe(
            jumlah_PeserteTender,
            column_config={
                "NAMA_PAKET": "NAMA PAKET",
                "NAMA_PENYEDIA": "NAMA PENYEDIA",
                "NPWP_PENYEDIA": "NPWP PENYEDIA",
                "PAGU": "PAGU",
                "HPS": "HPS",
                "NILAI_PENAWARAN": "NILAI PENAWARAN",
                "NILAI_TERKOREKSI": "NILAI TERKOREKSI"
            },
            use_container_width=True,
            hide_index=True,
            height=1000
        )

    except Exception:

        st.error("Gagal baca Dataset SPSE - Peserta Tender")

style_metric_cards(background_color="#000", border_left_color="#D3D3D3")

