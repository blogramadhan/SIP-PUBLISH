# Library Utama
import streamlit as st
import pandas as pd
import plotly.express as px
import duckdb
import openpyxl
import io
import xlsxwriter
# Library Currency
from babel.numbers import format_currency
# Librady AgGrid
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
}

daerah = list(region_config.keys())
tahuns = ["2024", "2023", "2022"]

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

## Akses Dataset (PARQUET)
DatasetRUPPP = f"https://data.pbj.my.id/{kodeRUP}/sirup/RUP-PaketPenyedia-Terumumkan{tahun}.parquet"
DatasetRUPPS = f"https://data.pbj.my.id/{kodeRUP}/sirup/RUP-PaketSwakelola-Terumumkan{tahun}.parquet"
DatasetRUPSA = f"https://data.pbj.my.id/{kodeRUP}/sirup/RUP-StrukturAnggaranPD{tahun}.parquet"

## Akses Dataset (PARQUET) 31 Maret Tahun Berjalan
DatasetRUPPP31Mar = f"https://data.pbj.my.id/{kodeRUP}/sirup/RUP-PaketPenyedia-Terumumkan-{tahun}-03-31.parquet"
DatasetRUPPS31Mar = f"https://data.pbj.my.id/{kodeRUP}/sirup/RUP-PaketSwakelola-Terumumkan-{tahun}-03-31.parquet"
DatasetRUPSA31Mar = f"https://data.pbj.my.id/{kodeRUP}/sirup/RUP-StrukturAnggaranPD-{tahun}-03-31.parquet"

## Dataframe RUP
try:

    ### Baca file parquet RUP Paket Penyedia
    df_RUPPP = tarik_data_parquet(DatasetRUPPP)

    ### Query RUP Paket Penyedia
    df_RUPPP_umumkan = con.execute("SELECT * FROM df_RUPPP WHERE status_umumkan_rup = 'Terumumkan' AND status_aktif_rup = 'TRUE' AND metode_pengadaan <> '0'").df()
    df_RUPPP_umumkan_ukm = con.execute("SELECT * FROM df_RUPPP_umumkan WHERE status_ukm = 'UKM'").df()
    df_RUPPP_umumkan_pdn = con.execute("SELECT * FROM df_RUPPP_umumkan WHERE status_pdn = 'PDN'").df()

    namaopd = df_RUPPP_umumkan['nama_satker'].unique()

except Exception:
    st.error("Gagal baca dataset RUP Paket Penyedia")

try:

    ### Baca file parquet RUP Paket Swakelola
    df_RUPPS = tarik_data_parquet(DatasetRUPPS)

    ### Query RUP Paket Swakelola
    RUPPS_umumkan_sql = """
        SELECT nama_satker, kd_rup, nama_paket, pagu, tipe_swakelola, volume_pekerjaan, uraian_pekerjaan, 
        tgl_pengumuman_paket, tgl_awal_pelaksanaan_kontrak, nama_ppk, status_umumkan_rup
        FROM df_RUPPS
        WHERE status_umumkan_rup = 'Terumumkan'
    """
    df_RUPPS_umumkan = con.execute(RUPPS_umumkan_sql).df()

except Exception:
    st.error("Gagal baca dataset RUP Paket Swakelola")

try:

    df_RUPSA = tarik_data_parquet(DatasetRUPSA)

    ### Baca file parquet RUP Struktur Anggaran
    df_RUPSA = tarik_data_parquet(DatasetRUPSA)
    
except Exception:
    st.error("Gagal baca dataset RUP Struktur Anggaran")

######
# Presentasi Data RUP
######

# Sajikan menu
menu_rup_1, menu_rup_2, menu_rup_3, menu_rup_4, menu_rup_5, menu_rup_6, menu_rup_7 = st.tabs(["| PROFIL RUP DAERAH |", "| PROFIL RUP PERANGKAT DAERAH |", "| STRUKTUR ANGGARAN |", "| RUP PAKET PENYEDIA |", "| RUP PAKET SWAKELOLA |", "| INPUT RUP (PERSEN) |", "| INPUT RUP (PERSEN) 31 Maret |"])

## Tab PROFIL RUP DAERAH
with menu_rup_1:

    ### Analisa Profil RUP Daerah
    df_RUPPP_mp_hitung = con.execute("SELECT metode_pengadaan AS METODE_PENGADAAN, COUNT(metode_pengadaan) AS JUMLAH_PAKET FROM df_RUPPP_umumkan WHERE metode_pengadaan IS NOT NULL GROUP BY metode_pengadaan").df() 
    df_RUPPP_mp_nilai = con.execute("SELECT metode_pengadaan AS METODE_PENGADAAN, SUM(pagu) AS NILAI_PAKET FROM df_RUPPP_umumkan WHERE metode_pengadaan IS NOT NULL GROUP BY metode_pengadaan").df()
    df_RUPPP_jp_hitung = con.execute("SELECT jenis_pengadaan AS JENIS_PENGADAAN, COUNT(jenis_pengadaan) AS JUMLAH_PAKET FROM df_RUPPP_umumkan WHERE jenis_pengadaan IS NOT NULL GROUP BY jenis_pengadaan").df()
    df_RUPPP_jp_nilai = con.execute("SELECT jenis_pengadaan AS JENIS_PENGADAAN, SUM(pagu) AS NILAI_PAKET FROM df_RUPPP_umumkan WHERE jenis_pengadaan IS NOT NULL GROUP BY Jenis_pengadaan").df()
    df_RUPPP_ukm_hitung = con.execute("SELECT status_ukm AS STATUS_UKM, COUNT(status_ukm) AS JUMLAH_PAKET FROM df_RUPPP_umumkan WHERE status_ukm IS NOT NULL GROUP BY status_ukm").df()
    df_RUPPP_ukm_nilai = con.execute("SELECT status_ukm AS STATUS_UKM, SUM(pagu) AS NILAI_PAKET FROM df_RUPPP_umumkan WHERE status_ukm IS NOT NULL GROUP BY status_ukm").df()
    df_RUPPP_pdn_hitung = con.execute("SELECT status_pdn AS STATUS_PDN, COUNT(status_pdn) AS JUMLAH_PAKET FROM df_RUPPP_umumkan WHERE status_pdn IS NOT NULL GROUP BY status_pdn").df()
    df_RUPPP_pdn_nilai = con.execute("SELECT status_pdn AS STATUS_PDN, SUM(pagu) AS NILAI_PAKET FROM df_RUPPP_umumkan WHERE status_pdn IS NOT NULL GROUP BY status_pdn").df()

    ### Unduh Dataframe Analisa Profil RUP Daerah
    unduh_RUPPP_excel = download_excel(df_RUPPP_umumkan)
    unduh_RUPPS_excel = download_excel(df_RUPPS_umumkan)

    prd1, prd2, prd3 = st.columns((6,2,2))
    with prd1:
        st.header(f"PROFIL RUP {pilih} TAHUN {tahun}")
    with prd2:
        st.download_button(
            label = "📥 Download RUP Paket Penyedia",
            data = unduh_RUPPP_excel,
            file_name = f"RUPPaketPenyedia-{kodeFolder}-{tahun}.xlsx",
            mime = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    with prd3:
        st.download_button(
            label = "📥 Download RUP Paket Swakelola",
            data = unduh_RUPPS_excel,
            file_name = f"RUPPaketSwakelola-{kodeFolder}-{tahun}.xlsx",
            mime = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    st.subheader("STRUKTUR ANGGARAN")

    belanja_pengadaan = df_RUPSA['belanja_pengadaan'].sum()
    belanja_operasional = df_RUPSA['belanja_operasi'].sum()
    belanja_modal = df_RUPSA['belanja_modal'].sum()
    belanja_total = belanja_operasional + belanja_modal

    colsa11, colsa12, colsa13 = st.columns(3)
    colsa11.metric(label="Belanja Operasional", value="{:,.2f}".format(belanja_operasional))
    colsa12.metric(label="Belanja Modal", value="{:,.2f}".format(belanja_modal))
    colsa13.metric(label="Belanja Pengadaan", value="{:,.2f}".format(belanja_total))  

    st.divider()

    st.subheader("POSISI INPUT RUP")

    jumlah_total_rup = df_RUPPP_umumkan.shape[0] + df_RUPPS_umumkan.shape[0]
    nilai_total_rup = df_RUPPP_umumkan['pagu'].sum() + df_RUPPS_umumkan['pagu'].sum()
    persen_capaian_rup = nilai_total_rup / belanja_total

    colir11, colir12, colir13 = st.columns(3)
    colir11.subheader("Jumlah Total")
    colir12.metric(label="Jumlah Total Paket RUP", value="{:,}".format(jumlah_total_rup))
    colir13.metric(label="Nilai Total Paket RUP", value="{:,.2f}".format(nilai_total_rup))

    colir21, colir22, colir23 = st.columns(3)
    colir21.subheader("Paket Penyedia")
    colir22.metric(label="Jumlah Total Paket Penyedia", value="{:,}".format(df_RUPPP_umumkan.shape[0]))
    colir23.metric(label="Nilai Total Paket Penyedia", value="{:,.2f}".format(df_RUPPP_umumkan['pagu'].sum()))

    colir31, colir32, colir33 = st.columns(3)
    colir31.subheader("Paket Swakelola")
    colir32.metric(label="Jumlah Total Paket Swakelola", value="{:,}".format(df_RUPPS_umumkan.shape[0]))
    colir33.metric(label="Nilai Total Paket Swakelola", value="{:,.2f}".format(df_RUPPS_umumkan['pagu'].sum()))

    colir41, colir42, colir43 = st.columns(3)
    colir41.subheader("")
    colir42.subheader("")
    colir43.metric(label="Persentase Capaian RUP", value="{:.2%}".format(persen_capaian_rup))

    st.divider()

    with st.container(border=True):

        st.subheader("STATUS UKM DAN PDN")

        ### Tabel dan Grafik RUP Status UKM
        grafik_rup_ukm_tab_1, grafik_rup_ukm_tab_2 = st.tabs(["| JUMLAH PAKET UKM |", "| NILAI PAKET UKM |"])

        with grafik_rup_ukm_tab_1:

            grafik_rup_ukm_tab_1_1, grafik_rup_ukm_tab_1_2 = st.columns((3,7))

            with grafik_rup_ukm_tab_1_1:

                st.dataframe(
                    df_RUPPP_ukm_hitung, 
                    column_config={
                        "STATUS_UKM": "STATUS UKM",
                        "JUMLAH_PAKET": "JUMLAH PAKET"
                    }, 
                    use_container_width=True,
                    hide_index=True
                )
            
            with grafik_rup_ukm_tab_1_2:

                figukmh = px.pie(df_RUPPP_ukm_hitung, values='JUMLAH_PAKET', names='STATUS_UKM', title='Grafik Status UKM - Jumlah Paket', hole=.3)
                st.plotly_chart(figukmh, theme="streamlit", use_container_width=True)

        with grafik_rup_ukm_tab_2:

            grafik_rup_ukm_tab_2_1, grafik_rup_ukm_tab_2_2 = st.columns((3,7))

            with grafik_rup_ukm_tab_2_1:

                st.dataframe(
                    df_RUPPP_ukm_nilai, 
                    column_config={
                        "STATUS_UKM": "STATUS UKM",
                        "NILAI_PAKET": "NILAI PAKET (Rp.)"
                    },
                    use_container_width=True,
                    hide_index=True
                )

            with grafik_rup_ukm_tab_2_2:

                figukmn = px.pie(df_RUPPP_ukm_nilai, values='NILAI_PAKET', names='STATUS_UKM', title='Grafik Status UKM - Nilai Paket', hole=.3)
                st.plotly_chart(figukmn, theme='streamlit', use_container_width=True)

        st.divider()

        ### Tabel dan Grafik RUP Status PDN
        grafik_rup_pdn_tab_1, grafik_rup_pdn_tab_2 = st.tabs(["| JUMLAH PAKET PDN |", "| NILAI PAKET PDN |"])

        with grafik_rup_pdn_tab_1:

            grafik_rup_pdn_tab_1_1, grafik_rup_pdn_tab_1_2 = st.columns((3,7))

            with grafik_rup_pdn_tab_1_1:

                st.dataframe(
                    df_RUPPP_pdn_hitung,
                    column_config={
                        "STATUS_PDN": "STATUS PDN",
                        "JUMLAH_PAKET": "JUMLAT PAKET"
                    },
                    use_container_width=True,
                    hide_index=True
                )

            with grafik_rup_pdn_tab_1_2:

                figpdnh = px.pie(df_RUPPP_pdn_hitung, values='JUMLAH_PAKET', names='STATUS_PDN', title='Grafik Status PDN - Jumlah Paket', hole=.3)
                st.plotly_chart(figpdnh, theme="streamlit", use_container_width=True)

        with grafik_rup_pdn_tab_2:

            grafik_rup_pdn_tab_2_1, grafik_rup_pdn_tab_2_2 = st.columns((3,7))

            with grafik_rup_pdn_tab_2_1:

                st.dataframe(
                    df_RUPPP_pdn_nilai,
                    column_config={
                        "STATUS_PDN": "STATUS PDN",
                        "NILAI_PAKET": "NILAI PAKET (Rp.)"
                    },
                    use_container_width=True,
                    hide_index=True
                )

            with grafik_rup_pdn_tab_2_2:

                figpdnn = px.pie(df_RUPPP_pdn_nilai, values='NILAI_PAKET', names='STATUS_PDN', title='Grafik Status PDN - Nilai Paket', hole=.3)
                st.plotly_chart(figpdnn, theme='streamlit', use_container_width=True)

    with st.container(border=True):

        st.subheader("BERDASARKAN METODE PENGADAAN")

        ### Tabel dan Grafik RUP Berdasarkan Metode Pengadaan
        grafik_rup_mp_tab_1, grafik_rup_mp_tab_2 = st.tabs(["| JUMLAH PAKET - MP |", "| NILAI PAKET - MP |"])

        with grafik_rup_mp_tab_1:

            grafik_rup_mp_tab_1_1, grafik_rup_mp_tab_1_2 = st.columns((3,7))

            with grafik_rup_mp_tab_1_1:

                st.dataframe(
                    df_RUPPP_mp_hitung,
                    column_config={
                        "METODE_PENGADAAN": "METODE PENGADAAN",
                        "JUMLAH_PAKET": "JUMLAH PAKET"
                    },
                    use_container_width=True,
                    hide_index=True
                )

            with grafik_rup_mp_tab_1_2:

                figmph = px.pie(df_RUPPP_mp_hitung, values='JUMLAH_PAKET', names='METODE_PENGADAAN', title='Grafik Metode Pengadaan - Jumlah Paket', hole=.3)
                st.plotly_chart(figmph, theme="streamlit", use_container_width=True)

        with grafik_rup_mp_tab_2:

            grafik_rup_mp_tab_2_1, grafik_rup_mp_tab_2_2 = st.columns((3,7))

            with grafik_rup_mp_tab_2_1:

                st.dataframe(
                    df_RUPPP_mp_nilai,
                    column_config={
                        "METODE_PENGADAAN": "METODE PENGADAAN",
                        "NILAI_PAKET": "NILAI PAKET (Rp.)"
                    },
                    use_container_width=True,
                    hide_index=True
                )

            with grafik_rup_mp_tab_2_2:

                figmpn = px.pie(df_RUPPP_mp_nilai, values='NILAI_PAKET', names='METODE_PENGADAAN', title='Grafik Metode Pengadaan - Nilai Paket', hole=.3)
                st.plotly_chart(figmpn, theme='streamlit', use_container_width=True)

    with st.container(border=True):

        st.subheader("BERDASARKAN JENIS PENGADAAN")

        ### Tabel dan Grafik RUP Berdasarkan Jenis Pengadaan
        grafik_rup_jp_tab_1, grafik_rup_jp_tab_2 = st.tabs(["| JUMLAH PAKET - JP |", "| NILAI PAKET - JP |"])

        with grafik_rup_jp_tab_1:

            grafik_rup_jp_tab_1_1, grafik_rup_jp_tab_1_2 = st.columns((3,7))

            with grafik_rup_jp_tab_1_1:

                st.dataframe(
                    df_RUPPP_jp_hitung,
                    column_config={
                        "JENIS_PENGADAAN": "JENIS PENGADAAN",
                        "JUMLAH_PAKET": "JUMLAH PAKET"
                    },
                    use_container_width=True,
                    hide_index=True
                )

            with grafik_rup_jp_tab_1_2:

                figjph = px.pie(df_RUPPP_jp_hitung, values='JUMLAH_PAKET', names='JENIS_PENGADAAN', title='Grafik Jenis Pengadaan - Jumlah Paket', hole=.3)
                st.plotly_chart(figjph, theme="streamlit", use_container_width=True)

        with grafik_rup_jp_tab_2:

            grafik_rup_jp_tab_2_1, grafik_rup_jp_tab_2_2 = st.columns((3,7))

            with grafik_rup_jp_tab_2_1:

                st.dataframe(
                    df_RUPPP_jp_nilai,
                    column_config={
                        "JENIS_PENGADAAN": "JENIS PENGADAAN",
                        "NILAI_PAKET": "NILAI PAKET"
                    },
                    use_container_width=True,
                    hide_index=True
                )

            with grafik_rup_jp_tab_2_2:

                figjpn = px.pie(df_RUPPP_jp_nilai, values='NILAI_PAKET', names='JENIS_PENGADAAN', title='Grafik Jenis Pengadaan - Nilai Paket', hole=.3)
                st.plotly_chart(figjpn, theme='streamlit', use_container_width=True)

## Tab PROFIL RUP PERANGKAT DAERAH
with menu_rup_2:

    st.header(f"PROFIL RUP {pilih} PERANGKAT DAERAH TAHUN {tahun}")

    ### Analisa Profil RUP Daerah Perangkat Daerah
    opd = st.selectbox("Pilih Perangkat Daerah :", namaopd)

    df_RUPPP_PD = con.execute(f"SELECT * FROM df_RUPPP_umumkan WHERE nama_satker = '{opd}'").df()
    df_RUPPS_PD = con.execute(f"SELECT * FROM df_RUPPS_umumkan WHERE nama_satker = '{opd}'").df()
    df_RUPSA_PD = con.execute(f"SELECT * FROM df_RUPSA WHERE nama_satker = '{opd}'").df()

    df_RUPPP_PD_mp_hitung = con.execute("SELECT metode_pengadaan AS METODE_PENGADAAN, COUNT(metode_pengadaan) AS JUMLAH_PAKET FROM df_RUPPP_PD WHERE metode_pengadaan IS NOT NULL GROUP BY metode_pengadaan").df()
    df_RUPPP_PD_mp_nilai = con.execute("SELECT metode_pengadaan AS METODE_PENGADAAN, SUM(pagu) AS NILAI_PAKET FROM df_RUPPP_PD WHERE metode_pengadaan IS NOT NULL GROUP BY metode_pengadaan").df()
    df_RUPPP_PD_jp_hitung = con.execute("SELECT jenis_pengadaan AS JENIS_PENGADAAN, COUNT(jenis_pengadaan) AS JUMLAH_PAKET FROM df_RUPPP_PD WHERE jenis_pengadaan IS NOT NULL GROUP BY jenis_pengadaan").df()
    df_RUPPP_PD_jp_nilai = con.execute("SELECT jenis_pengadaan AS JENIS_PENGADAAN, SUM(pagu) AS NILAI_PAKET FROM df_RUPPP_PD WHERE jenis_pengadaan IS NOT NULL GROUP BY Jenis_pengadaan").df()
    df_RUPPP_PD_ukm_hitung = con.execute("SELECT status_ukm AS STATUS_UKM, COUNT(status_ukm) AS JUMLAH_PAKET FROM df_RUPPP_PD WHERE status_ukm IS NOT NULL GROUP BY status_ukm").df()
    df_RUPPP_PD_ukm_nilai = con.execute("SELECT status_ukm AS STATUS_UKM, SUM(pagu) AS NILAI_PAKET FROM df_RUPPP_PD WHERE status_ukm IS NOT NULL GROUP BY status_ukm").df()
    df_RUPPP_PD_pdn_hitung = con.execute("SELECT status_pdn AS STATUS_PDN, COUNT(status_pdn) AS JUMLAH_PAKET FROM df_RUPPP_PD WHERE status_pdn IS NOT NULL GROUP BY status_pdn").df()
    df_RUPPP_PD_pdn_nilai = con.execute("SELECT status_pdn AS STATUS_PDN, SUM(pagu) AS NILAI_PAKET FROM df_RUPPP_PD WHERE status_pdn IS NOT NULL GROUP BY status_pdn").df()

    ### Unduh Dataframe Analisa Profil RUP Daerah Perangkat Daerah
    unduh_RUPPP_PD_excel = download_excel(df_RUPPP_PD)
    unduh_RUPPS_PD_excel = download_excel(df_RUPPS_PD)

    prpd1, prpd2, prpd3 = st.columns((6,2,2))
    with prpd1:
        st.subheader(f"{opd}")
    with prpd2:
        st.download_button(
            label = "📥 Download RUP Paket Penyedia",
            data = unduh_RUPPP_PD_excel,
            file_name = f"RUPPaketPenyedia-PD-{kodeFolder}-{tahun}.xlsx",
            mime = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    with prpd3:
        st.download_button(
            label = "📥 Download RUP Paket Swakelola",
            data = unduh_RUPPS_PD_excel,
            file_name = f"RUPPaketSwakelola-PD-{kodeFolder}-{tahun}.xlsx",
            mime = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    st.subheader("STRUKTUR ANGGARAN")

    belanja_pengadaan_pd = df_RUPSA_PD['belanja_pengadaan'].sum()
    belanja_operasional_pd = df_RUPSA_PD['belanja_operasi'].sum()
    belanja_modal_pd = df_RUPSA_PD['belanja_modal'].sum()
    belanja_total_pd = belanja_operasional_pd + belanja_modal_pd

    colsapd11, colsapd12, colsapd13 = st.columns(3)
    colsapd11.metric(label="Belanja Operasional", value="{:,.2f}".format(belanja_operasional_pd))
    colsapd12.metric(label="Belanja Modal", value="{:,.2f}".format(belanja_modal_pd))
    colsapd13.metric(label="Belanja Pengadaan", value="{:,.2f}".format(belanja_total_pd))  

    st.divider()

    st.subheader("POSISI INPUT RUP")

    jumlah_total_rup_pd = df_RUPPP_PD.shape[0] + df_RUPPS_PD.shape[0]
    nilai_total_rup_pd = df_RUPPP_PD['pagu'].sum() + df_RUPPS_PD['pagu'].sum()
    persen_capaian_rup_pd = nilai_total_rup_pd / belanja_pengadaan_pd

    colirpd11, colirpd12, colirpd13 = st.columns(3)
    colirpd11.subheader("Jumlah Total")
    colirpd12.metric(label="Jumlah Total Paket RUP", value="{:,}".format(jumlah_total_rup_pd))
    colirpd13.metric(label="Nilai Total Paket RUP", value="{:,.2f}".format(nilai_total_rup_pd))

    colirpd21, colirpd22, colirpd23 = st.columns(3)
    colirpd21.subheader("Paket Penyedia")
    colirpd22.metric(label="Jumlah Total Paket Penyedia", value="{:,}".format(df_RUPPP_PD.shape[0]))
    colirpd23.metric(label="Nilai Total Paket Penyedia", value="{:,.2f}".format(df_RUPPP_PD['pagu'].sum()))

    colirpd31, colirpd32, colirpd33 = st.columns(3)
    colirpd31.subheader("Paket Swakelola")
    colirpd32.metric(label="Jumlah Total Paket Swakelola", value="{:,}".format(df_RUPPS_PD.shape[0]))
    colirpd33.metric(label="Nilai Total Paket Swakelola", value="{:,.2f}".format(df_RUPPS_PD['pagu'].sum()))

    colirpd41, colirpd42, colirpd43 = st.columns(3)
    colirpd41.subheader("")
    colirpd42.subheader("")
    colirpd43.metric(label="Persentase Capaian RUP", value="{:.2%}".format(persen_capaian_rup_pd))

    st.divider()

    with st.container(border=True):

        st.subheader("STATUS UKM DAN PDN")

        ### Tabel dan Grafik RUP Status UKM Perangkat Daerah
        grafik_rup_ukm_pd_tab_1, grafik_rup_ukm_pd_tab_2 = st.tabs(["| Berdasarkan Jumlah Paket - UKM |", "| Berdasarkan Nilai Paket - UKM |"])

        with grafik_rup_ukm_pd_tab_1:

            grafik_rup_ukm_pd_tab_1_1, grafik_rup_ukm_pd_tab_1_2 = st.columns((3,7))

            with grafik_rup_ukm_pd_tab_1_1:

                st.dataframe(
                    df_RUPPP_PD_ukm_hitung,
                    column_config={
                        "STATUS_UKM": "STATUS UKM",
                        "JUMLAH_PAKET": "JUMLAH PAKET"
                    },
                    use_container_width=True,
                    hide_index=True
                )

            with grafik_rup_ukm_pd_tab_1_2:

                figukmh = px.pie(df_RUPPP_PD_ukm_hitung, values='JUMLAH_PAKET', names='STATUS_UKM', title='Grafik Status UKM - Jumlah Paket', hole=.3)
                st.plotly_chart(figukmh, theme="streamlit", use_container_width=True)

        with grafik_rup_ukm_pd_tab_2:

            grafik_rup_ukm_pd_tab_2_1, grafik_rup_ukm_pd_tab_2_2 = st.columns((3,7))

            with grafik_rup_ukm_pd_tab_2_1:

                st.dataframe(
                    df_RUPPP_PD_ukm_nilai,
                    column_config={
                        "STATUS_UKM": "STATUS UKM",
                        "NILAI_PAKET": "NILAI PAKET (Rp.)"
                    },
                    use_container_width=True,
                    hide_index=True
                )

            with grafik_rup_ukm_pd_tab_2_2:

                figukmn = px.pie(df_RUPPP_PD_ukm_nilai, values='NILAI_PAKET', names='STATUS_UKM', title='Grafik Status UKM - Nilai Paket', hole=.3)
                st.plotly_chart(figukmn, theme='streamlit', use_container_width=True)

        st.divider()

        ### Tabel dan Grafik RUP Status PDN Perangkat Daerah
        grafik_rup_pdn_pd_tab_1, grafik_rup_pdn_pd_tab_2 = st.tabs(["| Berdasarkan Jumlah Paket - PDN |", "| Berdasarkan Nilai Paket - PDN |"])

        with grafik_rup_pdn_pd_tab_1:

            grafik_rup_pdn_pd_tab_1_1, grafik_rup_pdn_pd_tab_1_2 = st.columns((3,7))

            with grafik_rup_pdn_pd_tab_1_1:

                st.dataframe(
                    df_RUPPP_PD_pdn_hitung,
                    column_config={
                        "STATUS_PDN": "STATUS PDN",
                        "JUMLAH_PAKET": "JUMLAH PAKET"
                    },
                    use_container_width=True,
                    hide_index=True
                )

            with grafik_rup_pdn_pd_tab_1_2:

                figpdnh = px.pie(df_RUPPP_PD_pdn_hitung, values='JUMLAH_PAKET', names='STATUS_PDN', title='Grafik Status PDN - Jumlah Paket', hole=.3)
                st.plotly_chart(figpdnh, theme="streamlit", use_container_width=True)

        with grafik_rup_pdn_pd_tab_2:

            grafik_rup_pdn_pd_tab_2_1, grafik_rup_pdn_pd_tab_2_2 = st.columns((3,7))

            with grafik_rup_pdn_pd_tab_2_1:

                st.dataframe(
                    df_RUPPP_PD_pdn_nilai,
                    column_config={
                        "STATUS_PDN": "STATUS PDN",
                        "NILAI_PAKET": "NILAI PAKET (Rp.)"
                    },
                    use_container_width=True,
                    hide_index=True
                )

            with grafik_rup_pdn_pd_tab_2_2:

                figpdnn = px.pie(df_RUPPP_PD_pdn_nilai, values='NILAI_PAKET', names='STATUS_PDN', title='Grafik Status PDN - Nilai Paket', hole=.3)
                st.plotly_chart(figpdnn, theme='streamlit', use_container_width=True)

    with st.container(border=True):

        st.subheader("BERDASARKAN METODE PENGADAAN")

        ### Tabel dan Grafik RUP Berdasarkan Metode Pengadaan Perangkat Daerah
        grafik_rup_mp_pd_tab_1, grafik_rup_mp_pd_tab_2 = st.tabs(["| Berdasarkan Jumlah Paket - MP |", "| Berdasarkan Nilai Paket - MP |"])

        with grafik_rup_mp_pd_tab_1:

            grafik_rup_mp_pd_tab_1_1, grafik_rup_mp_pd_tab_1_2 = st.columns((3,7))

            with grafik_rup_mp_pd_tab_1_1:

                st.dataframe(
                    df_RUPPP_PD_mp_hitung,
                    column_config={
                        "METODE_PENGADAAN": "METODE PENGADAAN",
                        "JUMLAH_PAKET": "JUMLAH PAKET"
                    },
                    use_container_width=True,
                    hide_index=True
                )

            with grafik_rup_mp_pd_tab_1_2:

                figmph = px.pie(df_RUPPP_PD_mp_hitung, values='JUMLAH_PAKET', names='METODE_PENGADAAN', title='Grafik Metode Pengadaan - Jumlah Paket', hole=.3)
                st.plotly_chart(figmph, theme="streamlit", use_container_width=True)

        with grafik_rup_mp_pd_tab_2:

            grafik_rup_mp_pd_tab_2_1, grafik_rup_mp_pd_tab_2_2 = st.columns((3,7))

            with grafik_rup_mp_pd_tab_2_1:

                st.dataframe(
                    df_RUPPP_PD_mp_nilai, 
                    column_config={
                        "METODE_PENGADAAN": "METODE PENGADAAN",
                        "NILAI_PAKET": "NILAI PAKET (Rp.)"
                    },
                    use_container_width=True,
                    hide_index=True
                )
        
            with grafik_rup_mp_pd_tab_2_2:

                figmpn = px.pie(df_RUPPP_PD_mp_nilai, values='NILAI_PAKET', names='METODE_PENGADAAN', title='Grafik Metode Pengadaan - Nilai Paket', hole=.3)
                st.plotly_chart(figmpn, theme='streamlit', use_container_width=True)

    with st.container(border=True):
    
        st.subheader("BERDASARKAN JENIS PENGADAAN")

        ### Tabel dan Grafik RUP Berdasarkan jenis pengadaan Perangkat Daerah
        grafik_rup_jp_pd_tab_1, grafik_rup_jp_pd_tab_2 = st.tabs(["| Berdasarkan Jumlah Paket - JP |", "| Berdasarkan Nilai Paket - JP |"])

        with grafik_rup_jp_pd_tab_1:

            grafik_rup_jp_pd_tab_1_1, grafik_rup_jp_pd_tab_1_2 = st.columns((3,7))

            with grafik_rup_jp_pd_tab_1_1:

                st.dataframe(
                    df_RUPPP_PD_jp_hitung,
                    column_config={
                        "JENIS_PENGADAAN": "JENIS PENGADAAN",
                        "JUMLAH_PAKET": "JUMLAH PAKET"
                    },
                    use_container_width=True,
                    hide_index=True    
                )

            with grafik_rup_jp_pd_tab_1_2:

                figjph = px.pie(df_RUPPP_PD_jp_hitung, values='JUMLAH_PAKET', names='JENIS_PENGADAAN', title='Grafik Jenis Pengadaan - Jumlah Paket', hole=.3)
                st.plotly_chart(figjph, theme="streamlit", use_container_width=True)

        with grafik_rup_jp_pd_tab_2:

            grafik_rup_jp_pd_tab_2_1, grafik_rup_jp_pd_tab_2_2 = st.columns((3,7))

            with grafik_rup_jp_pd_tab_2_1:

                st.dataframe(
                    df_RUPPP_PD_jp_nilai, 
                    column_config={
                        "JENIS_PENGADAAN": "JENIS PENGADAAN",
                        "NILAI_PAKET": "NILAI PAKET (Rp.)"
                    },
                    use_container_width=True,
                    hide_index=True   
                )

            with grafik_rup_jp_pd_tab_2_2:

                figjpn = px.pie(df_RUPPP_PD_jp_nilai, values='NILAI_PAKET', names='JENIS_PENGADAAN', title='Grafik Jenis Pengadaan - Nilai Paket', hole=.3)
                st.plotly_chart(figjpn, theme='streamlit', use_container_width=True)

with menu_rup_3:
    
    st.header(f"STRUKTUR ANGGARAN {pilih} TAHUN {tahun}")

    ### Analisa Struktur Anggaran
    sql_query_sa = """
        SELECT nama_satker AS NAMA_SATKER, SUM(belanja_operasi) AS BELANJA_OPERASI, SUM(belanja_modal) AS BELANJA_MODAL, SUM(belanja_btt) AS BELANJA_BTT, 
        SUM(belanja_non_pengadaan) AS BELANJA_NON_PENGADAAN, SUM(belanja_pengadaan) AS BELANJA_PENGADAAN, SUM(total_belanja) AS TOTAL_BELANJA
        FROM df_RUPSA
        WHERE BELANJA_PENGADAAN > 0
        GROUP BY nama_satker
        ORDER BY total_belanja DESC;
    """

    df_RUPSA_tampil = con.execute(sql_query_sa).df()

    ### Tabel Struktur Anggaran
    st.dataframe(
        df_RUPSA_tampil,
        column_config={
            "BELANJA_OPERASI": "BELANJA OPERASI",
            "BELANJA_MODAL": "BELANJA MODAL",
            "BELANJA_BTT": "BELANJA BTT",
            "BELANJA_NON_PENGADAAN": "BELANJA NON PENGADAAN",
            "BELANJA_PENGADAAAN": "BELANJA PENGADAAN",
            "TOTAL_BELANJA": "TOTAL BELANJA"
        },
        use_container_width=True,
        hide_index=True,
        height=1500
    )

with menu_rup_4:
    
    st.header(f"TABEL RUP PERANGKAT DAERAH PAKET PENYEDIA TAHUN {tahun}")

    ### Analisa Paket Penyedia Perangkat Daerah
    opd_tbl_pp = st.selectbox("Pilih Perangkat Daerah :", namaopd, key='menu_rup_4')

    st.divider()

    df_RUPPP_PD_tbl = con.execute(f"SELECT * FROM df_RUPPP_umumkan WHERE nama_satker = '{opd_tbl_pp}'").df()

    st.subheader(opd_tbl_pp)

    unduh_df_RUPPP_PD_tbl_excel = download_excel(df_RUPPP_PD_tbl)

    st.download_button(
        label = "📥 Download RUP Paket Penyedia",
        data = unduh_df_RUPPP_PD_tbl_excel,
        file_name = f"RUPPaketPenyedia-{kodeFolder}-{tahun}.xlsx",
        mime = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        key = "download_paket_penyedia_detail"
    )

    sql_query_pp_tbl = """
        SELECT nama_paket AS NAMA_PAKET, kd_rup AS ID_RUP, metode_pengadaan AS METODE_PEMILIHAN, jenis_pengadaan AS JENIS_PENGADAAN,  
        status_pradipa AS STATUS_PRADIPA, status_pdn AS STATUS_PDN, status_ukm AS STATUS_UKM, tgl_pengumuman_paket AS TANGGAL_PENGUMUMAN, 
        tgl_awal_pemilihan AS TANGGAL_RENCANA_PEMILIHAN, pagu AS PAGU FROM df_RUPPP_PD_tbl
    """
    df_RUPPP_PD_tbl_tampil = con.execute(sql_query_pp_tbl).df()

    ### Tabel RUP Paket Penyedia
    st.dataframe(
        df_RUPPP_PD_tbl_tampil,
        column_config={
            "NAMA_PAKET": "NAMA PAKET",
            "ID_RUP": "KODE RUP",
            "METODE_PEMILIHAN": "METODE PEMILIHAN",
            "JENIS_PENGADAAN": "JENIS PENGADAAN",
            "STATUS_PRADIPA": "STATUS PRADIPA",
            "STATUS_PDN": "STATUS PDN",
            "STATUS_UKM": "STATUS UKM",
            "TGL_PENGUMUMAN": "TANGGAL PENGUMUMAN",
            "TGL_RENCANA_PEMILIHAN": "TANGGAL RENCANA PEMILIHAN",
            "PAGU": "PAGU"
        },
        use_container_width=True,
        hide_index=True,
        height=1000
    )

with menu_rup_5:

    st.header(f"TABEL RUP PERANGKAT DAERAH PAKET SWAKELOLA TAHUN {tahun}")

    ### Analisa Paket Swakelola Perangkat Daerah
    opd_tbl_ps = st.selectbox("Pilih Perangkat Daerah :", namaopd, key='menu_rup_5')

    st.divider()

    df_RUPPS_PD_tbl = con.execute(f"SELECT * FROM df_RUPPS_umumkan WHERE nama_satker = '{opd_tbl_ps}'").df()

    st.subheader(opd_tbl_ps)

    unduh_df_RUPPS_PD_tbl_excel = download_excel(df_RUPPS_PD_tbl)
    st.download_button(
        label = "📥 Download RUP Paket Swakelola",
        data = unduh_df_RUPPS_PD_tbl_excel,
        file_name = f"RUPPaketSwakelola-{kodeFolder}-{tahun}.xlsx",
        mime = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        key = "download_paket_swakelola_detail"
    )

    sql_query_ps_tbl = """
        SELECT nama_paket AS NAMA_PAKET, kd_rup AS ID_RUP, tipe_swakelola AS TIPE_SWAKELOLA, 
        tgl_pengumuman_paket AS TANGGAL_PENGUMUMAN, tgl_awal_pelaksanaan_kontrak AS TANGGAL_PELAKSANAAN, pagu AS PAGU 
        FROM df_RUPPS_PD_tbl
    """
    df_RUPPS_PD_tbl_tampil = con.execute(sql_query_ps_tbl).df()

    ### Tabel RUP Paket Swakelola

    st.dataframe(
        df_RUPPS_PD_tbl_tampil,
        column_config={
            "NAMA_PAKET": "NAMA PAKET",
            "ID_RUP": "KODE RUP",
            "TIPE_SWAKELOLA": "TIPE SWAKELOLA",
            "TANGGAL_PENGUMUMAN": "TANGGAL PENGUMUMAN",
            "TANGGAL_PELAKSANAAN": "TANGGAL PELAKSANAAN",
            "PAGU": "PAGU"
        },
        use_container_width=True,
        hide_index=True,
        height=1000
    )

with menu_rup_6:

    st.header(f"INPUT RUP (PERSEN) {pilih} TAHUN {tahun}")

    ### Analisa Data INPUT RUP (PERSEN)
    persen_rup_query = """
        SELECT
            df_RUPSA.nama_satker AS NAMA_SATKER,
            df_RUPSA.belanja_pengadaan AS STRUKTUR_ANGGARAN 
        FROM
            df_RUPSA
        LEFT JOIN
            df_RUPPP_umumkan ON df_RUPSA.nama_satker = df_RUPPP_umumkan.nama_satker
        LEFT JOIN
            df_RUPPS_umumkan ON df_RUPSA.nama_satker = df_RUPPS_umumkan.nama_satker
        WHERE
            df_RUPSA.belanja_pengadaan > 0
        GROUP BY
            df_RUPSA.nama_satker, df_RUPSA.belanja_pengadaan       
    """
    ir_gabung_final = con.execute(persen_rup_query).df()

    # ir_strukturanggaran = con.execute("SELECT nama_satker AS NAMA_SATKER, belanja_pengadaan AS STRUKTUR_ANGGARAN FROM df_RUPSA WHERE STRUKTUR_ANGGARAN > 0").df()
    # ir_paketpenyedia = con.execute("SELECT nama_satker AS NAMA_SATKER, SUM(pagu) AS RUP_PENYEDIA FROM df_RUPPP_umumkan GROUP BY NAMA_SATKER").df()
    # ir_paketswakelola = con.execute("SELECT nama_satker AS NAMA_SATKER, SUM(pagu) AS RUP_SWAKELOLA FROM df_RUPPS_umumkan GROUP BY NAMA_SATKER").df()   

    # ir_gabung = pd.merge(pd.merge(ir_strukturanggaran, ir_paketpenyedia, how='left', on='NAMA_SATKER'), ir_paketswakelola, how='left', on='NAMA_SATKER')
    # ir_gabung_totalrup = ir_gabung.assign(TOTAL_RUP = lambda x: x.RUP_PENYEDIA + x.RUP_SWAKELOLA)
    # ir_gabung_selisih = ir_gabung_totalrup.assign(SELISIH = lambda x: x.STRUKTUR_ANGGARAN - x.RUP_PENYEDIA - x.RUP_SWAKELOLA) 
    # ir_gabung_final = ir_gabung_selisih.assign(PERSEN = lambda x: round(((x.RUP_PENYEDIA + x.RUP_SWAKELOLA) / x.STRUKTUR_ANGGARAN * 100), 2)).fillna(0)

    unduh_perseninputrup_excel = download_excel(ir_gabung_final)

    st.download_button(
        label = "📥 Download Data % Input RUP",
        data = unduh_perseninputrup_excel,
        file_name = f"TabelPersenInputRUP-{pilih}-{tahun}.xlsx",
        mime = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    ### Tabel INPUT RUP (PERSEN)

    st.dataframe(
        ir_gabung_final,
        column_config={
            "STRUKTUR_ANGGARAN": "STRUKTUR ANGGARAN",
            "RUP_PENYEDIA": "RUP PENYEDIA",
            "RUP_SWAKELOLA": "RUP SWAKELOLA",
            "TOTAL_RUP": "TOTAL RUP",
            "SELISIH": "SELISIH"
        },
        use_container_width=True,
        hide_index=True,
        height=1000
    )

with menu_rup_7:

    ### Analisa Data INPUT RUP (PERSEN) 31 Maret
    try:
        #### Baca file parquet dataset RUP 31 Maret
        df_RUPPP31Mar = tarik_data_parquet(DatasetRUPPP31Mar)
        df_RUPPS31Mar = tarik_data_parquet(DatasetRUPPS31Mar)
        df_RUPSA31Mar = tarik_data_parquet(DatasetRUPSA31Mar)

        df_RUPPP_umumkan_31Mar = con.execute("SELECT * FROM df_RUPPP31Mar WHERE status_umumkan_rup = 'Terumumkan' AND status_aktif_rup = 'TRUE' AND metode_pengadaan <> '0'").df()
        df_RUPPS_umumkan_31Mar = con.execute("SELECT * FROM df_RUPPS31Mar WHERE status_umumkan_rup = 'Terumumkan'").df() 

    except Exception:
        st.error("Gagal baca dataset RUP 31 Maret Tahun Berjalan")

    ### Tabel INPUT RUP (PERSEN) 31 Maret
    st.header(f"INPUT RUP (PERSEN - 31 Maret) {pilih} TAHUN {tahun}")

    # persen_rup_query_31Mar = """
    #     SELECT
    #         df_RUPSA31Mar.nama_satker AS NAMA_SATKER,
    #         df_RUPSA31Mar.belanja_pengadaan AS STRUKTUR_ANGGARAN,
    #         COALESCE(SUM(df_RUPPP_umumkan_31Mar.pagu), 0) AS RUP_PENYEDIA,
    #         COALESCE(SUM(df_RUPPS_umumkan_31Mar.pagu), 0) AS RUP_SWAKELOLA,
    #         COALESCE(SUM(df_RUPPP_umumkan_31Mar.pagu), 0) + COALESCE(SUM(df_RUPPS_umumkan_31Mar.pagu), 0) AS TOTAL_RUP,
    #         df_RUPSA31Mar.belanja_pengadaan - COALESCE(SUM(df_RUPPP_umumkan_31Mar.pagu), 0) - COALESCE(SUM(df_RUPPS_umumkan_31Mar.pagu), 0) AS SELISIH,
    #         ROUND((COALESCE(SUM(df_RUPPP_umumkan_31Mar.pagu), 0) + COALESCE(SUM(df_RUPPS_umumkan_31Mar.pagu), 0)) / df_RUPSA31Mar.belanja_pengadaan * 100, 2) AS PERSEN 
    #     FROM
    #         df_RUPSA31Mar
    #     LEFT JOIN
    #         df_RUPPP_umumkan_31Mar ON df_RUPSA31Mar.nama_satker = df_RUPPP_umumkan_31Mar.nama_satker
    #     LEFT JOIN
    #         df_RUPPS_umumkan_31Mar ON df_RUPSA31Mar.nama_satker = df_RUPPS_umumkan_31Mar.nama_satker
    #     WHERE
    #         df_RUPSA31Mar.belanja_pengadaan > 0
    #     GROUP BY
    #         df_RUPSA31Mar.nama_satker, df_RUPSA31Mar.belanja_pengadaan       
    # """
    # ir_gabung_final_31Mar = con.execute(persen_rup_query_31Mar).df()

    ir_strukturanggaran_31Mar = con.execute("SELECT nama_satker AS NAMA_SATKER, belanja_pengadaan AS STRUKTUR_ANGGARAN FROM df_RUPSA31Mar WHERE STRUKTUR_ANGGARAN > 0").df()
    ir_paketpenyedia_31Mar = con.execute("SELECT nama_satker AS NAMA_SATKER, SUM(pagu) AS RUP_PENYEDIA FROM df_RUPPP_umumkan_31Mar GROUP BY NAMA_SATKER").df()
    ir_paketswakelola_31Mar = con.execute("SELECT nama_satker AS NAMA_SATKER, SUM(pagu) AS RUP_SWAKELOLA FROM df_RUPPS_umumkan_31Mar GROUP BY NAMA_SATKER").df()   

    ir_gabung_31Mar = pd.merge(pd.merge(ir_strukturanggaran_31Mar, ir_paketpenyedia_31Mar, how='left', on='NAMA_SATKER'), ir_paketswakelola_31Mar, how='left', on='NAMA_SATKER')
    ir_gabung_totalrup_31Mar = ir_gabung_31Mar.assign(TOTAL_RUP = lambda x: x.RUP_PENYEDIA + x.RUP_SWAKELOLA)
    ir_gabung_selisih_31Mar = ir_gabung_totalrup_31Mar.assign(SELISIH = lambda x: x.STRUKTUR_ANGGARAN - x.RUP_PENYEDIA - x.RUP_SWAKELOLA) 
    ir_gabung_final_31Mar = ir_gabung_selisih_31Mar.assign(PERSEN = lambda x: round(((x.RUP_PENYEDIA + x.RUP_SWAKELOLA) / x.STRUKTUR_ANGGARAN * 100), 2)).fillna(0)

    unduh_perseninputrup_31Mar_excel = download_excel(ir_gabung_final_31Mar)

    st.download_button(
        label = "📥 Download Data % Input RUP",
        data = unduh_perseninputrup_31Mar_excel,
        file_name = f"TabelPersenInputRUP31Mar-{pilih}-{tahun}.xlsx",
        mime = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    ### Tabel Input RUP (31 Maret)

    st.dataframe(
        ir_gabung_final_31Mar,
        column_config={
            "STRUKTUR_ANGGARAN": "STRUKTUR ANGGARAN",
            "RUP_PENYEDIA": "RUP PENYEDIA",
            "RUP_SWAKELOLA": "RUP SWAKELOLA",
            "TOTAL_RUP": "TOTAL RUP",
            "SELISIH": "SELISIH"
        },
        use_container_width=True,
        hide_index=True,
        height=1000
    )

style_metric_cards(background_color="#000", border_left_color="#D3D3D3")