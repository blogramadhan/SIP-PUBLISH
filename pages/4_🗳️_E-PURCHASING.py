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

## Akses Dataset (Parquet)
### Dataset Katalog dan Toko Daring
DatasetPURCHASINGECAT = f"https://data.pbj.my.id/{kodeRUP}/epurchasing/Ecat-PaketEPurchasing{tahun}.parquet"
DatasetPURCHASINGBELA = f"https://data.pbj.my.id/{kodeRUP}/epurchasing/Bela-TokoDaringRealisasi{tahun}.parquet"
DatasetPURCHASINGECATKD = f"https://data.pbj.my.id/{kodeRUP}/epurchasing/ECATKomoditasDetail{tahun}.parquet"
DatasetPURCHASINGECATIS = f"https://data.pbj.my.id/{kodeRUP}/epurchasing/Ecat-InstansiSatker.parquet"
DatasetPURCHASINGECATPD = f"https://data.pbj.my.id/{kodeRUP}/epurchasing/ECATPenyediaDetail{tahun}.parquet"

#####
# Presentasi Katalog dan Toko Daring
#####

# Sajikan Menu
menu_purchasing_1, menu_purchasing_2 = st.tabs(["| E-KATALOG |", "| TOKO DARING |"])

## Tab menu Transaksi E-Katalog
with menu_purchasing_1:

    menu_purchasing_1_1, menu_purchasing_1_2, menu_purchasing_1_3 = st.tabs(["| TRANSAKSI KATALOG |", "| TRANSAKSI KATALOG (ETALASE) |", "| TABEL NILAI ETALASE |"])

    try:
        ### Baca file parquet E-Katalog
        df_ECAT = tarik_data_parquet(DatasetPURCHASINGECAT)
        df_ECAT_KD = tarik_data_parquet(DatasetPURCHASINGECATKD)
        df_ECAT_IS = tarik_data_parquet(DatasetPURCHASINGECATIS)
        df_ECAT_PD = tarik_data_parquet(DatasetPURCHASINGECATPD)

        ### Query E-Katalog
        df_ECAT_0 = df_ECAT.merge(df_ECAT_KD, how='left', on='kd_komoditas').drop('nama_satker', axis=1)
        df_ECAT_1 = pd.merge(df_ECAT_0, df_ECAT_IS, left_on='satker_id', right_on='kd_satker', how='left')
        df_ECAT_OK = df_ECAT_1.merge(df_ECAT_PD, how='left', on='kd_penyedia')

        ### Buat tombol unduh dataset
        unduh_ECAT_excel = download_excel(df_ECAT_OK)

        with menu_purchasing_1_1:

            #### Buat tombol unduh dataset
            ecat1, ecat2 = st.columns((8,2))
            with ecat1:
                st.header(f"TRANSAKSI E-KATALOG - {pilih} - TAHUN {tahun}")
            with ecat2:
                st.download_button(
                    label = "📥 Data Tramsaksi E-Katalog",
                    data = unduh_ECAT_excel,
                    file_name = f"TransaksiEKATALOG-{kodeFolder}-{tahun}.xlsx",
                    mime = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )

            st.divider()

            KATALOG_radio_1, KATALOG_radio_2, KATALOG_radio_3, KATALOG_radio_4 = st.columns((1,1,3,5))
            with KATALOG_radio_1:
                jenis_katalog_array = df_ECAT_OK['jenis_katalog'].unique()
                jenis_katalog_array_ok = np.insert(jenis_katalog_array, 0, "Gabungan")
                jenis_katalog = st.radio("**Jenis Katalog**", jenis_katalog_array_ok)
            with KATALOG_radio_2:
                # nama_sumber_dana_array = df_ECAT_OK['nama_sumber_dana'].unique()
                # nama_sumber_dana_array_ok = np.insert(nama_sumber_dana_array, 0, "Gabungan")
                nama_sumber_dana = st.radio("**Sumber Dana**", ["Gabungan", "APBD", "BLUD"])
            with KATALOG_radio_3:
                status_paket_array = df_ECAT_OK['status_paket'].unique()
                status_paket_array_ok = np.insert(status_paket_array, 0, "Gabungan")
                status_paket = st.radio("**Status Paket**", status_paket_array_ok)
            st.write(f"Anda memilih : **{status_paket}** dan **{jenis_katalog}** dan **{nama_sumber_dana}**")

            df_ECAT_filter_Query = f"SELECT * FROM df_ECAT_OK WHERE 1=1"

            # Buat logika untuk query dari pilihan kondisi (3 kondisi)
            if jenis_katalog != "Gabungan":
                df_ECAT_filter_Query += f" AND jenis_katalog = '{jenis_katalog}'"
            if nama_sumber_dana != "Gabungan":
                if "APBD" in nama_sumber_dana:
                    df_ECAT_filter_Query += f" AND nama_sumber_dana LIKE '%APBD%'"
                else:
                    df_ECAT_filter_Query += f" AND nama_sumber_dana = '{nama_sumber_dana}'"
            if status_paket != "Gabungan":
                df_ECAT_filter_Query += f" AND status_paket = '{status_paket}'"

            df_ECAT_filter = con.execute(df_ECAT_filter_Query).df()

            jumlah_produk = df_ECAT_filter['kd_produk'].unique().shape[0]
            jumlah_penyedia = df_ECAT_filter['kd_penyedia'].unique().shape[0]
            jumlah_trx = df_ECAT_filter['no_paket'].unique().shape[0]
            nilai_trx = df_ECAT_filter['total_harga'].sum()

            colokal1, colokal2, colokal3, colokal4 = st.columns(4)
            colokal1.metric(label="Jumlah Produk Katalog", value="{:,}".format(jumlah_produk))
            colokal2.metric(label="Jumlah Penyedia Katalog", value="{:,}".format(jumlah_penyedia))
            colokal3.metric(label="Jumlah Transaksi Katalog", value="{:,}".format(jumlah_trx))
            colokal4.metric(label="Nilai Transaksi Katalog", value="{:,.2f}".format(nilai_trx))

            st.divider()

            with st.container(border=True):

                st.subheader("Berdasarkan Kualifikasi Usaha")

                #### Buat grafik Katalog Penyedia UKM
                grafik_ukm_tab_1, grafik_ukm_tab_2 = st.tabs(["| Jumlah Transaksi Penyedia |", "| Nilai Transaksi Penyedia |"])

                with grafik_ukm_tab_1:

                    ##### Query data grafik jumlah transaksi penyedia ukm
                    sql_jumlah_ukm = f"""
                        SELECT penyedia_ukm AS PENYEDIA_UKM, COUNT(DISTINCT(kd_penyedia)) AS JUMLAH_UKM
                        FROM df_ECAT_filter GROUP BY PENYEDIA_UKM
                    """ 

                    tabel_jumlah_ukm = con.execute(sql_jumlah_ukm).df()
                    
                    grafik_ukm_tab_1_1, grafik_ukm_tab_1_2 = st.columns((3,7))
                    
                    with grafik_ukm_tab_1_1:

                        # AgGrid(tabel_jumlah_ukm)

                        ##### Tampilkan Data
                        st.dataframe(
                            tabel_jumlah_ukm,
                            column_config={
                                "PENYEDIA_UKM": "PENYEDIA UKM",
                                "JUMLAH_UKM": "JUMLAH UKM"
                            },
                            use_container_width=True,
                            hide_index=True
                        )

                    with grafik_ukm_tab_1_2:

                        fig_katalog_jumlah_ukm = px.pie(tabel_jumlah_ukm, values='JUMLAH_UKM', names="PENYEDIA_UKM", title='Grafik Jumlah Transaksi Katalog PENYEDIA UKM', hole=.3)
                        st.plotly_chart(fig_katalog_jumlah_ukm, theme='streamlit', use_container_width=True)      

                with grafik_ukm_tab_2:

                    #### Query data grafik nilai transaksi penyedia ukm
                    sql_nilai_ukm = f"""
                        SELECT penyedia_ukm AS PENYEDIA_UKM, SUM(total_harga) AS NILAI_UKM
                        FROM df_ECAT_filter GROUP BY PENYEDIA_UKM
                    """ 

                    tabel_nilai_ukm = con.execute(sql_nilai_ukm).df()
                    
                    grafik_ukm_tab_2_1, grafik_ukm_tab_2_2 = st.columns((3.5,6.5))
                    
                    with grafik_ukm_tab_2_1:

                        ##### Tampilkan Data
                        st.dataframe(
                            tabel_nilai_ukm,
                            column_config={
                                "PENYEDIA_UKM": "PENYEDIA UKM",
                                "NILAI_UKM": "NILAI UKM"
                            },
                            use_container_width=True,
                            hide_index=True
                        )

                    with grafik_ukm_tab_2_2:

                        fig_katalog_nilai_ukm = px.pie(tabel_nilai_ukm, values='NILAI_UKM', names="PENYEDIA_UKM", title='Grafik Nilai Transaksi Katalog PENYEDIA UKM', hole=.3)
                        st.plotly_chart(fig_katalog_nilai_ukm, theme='streamlit', use_container_width=True)      

            with st.container(border=True):

                st.subheader("Berdasarkan Nama Komoditas (10 Besar)")

                #### Buat Grafik Katalog Berdasarkan Nama Komoditas
                grafik_ecat_nk_1, grafik_ecat_nk_2 = st.tabs(["| Jumlah Transaksi Tiap Komoditas |", "| Nilai Transaksi Tiap Komoditas |"])

                with grafik_ecat_nk_1:

                    #### Query data grafik jumlah Transaksi Katalog Lokal berdasarkan Nama Komoditas
                    if jenis_katalog == "Lokal":
                        sql_jumlah_transaksi_lokal_nk = f"""
                            SELECT nama_komoditas AS NAMA_KOMODITAS, COUNT(DISTINCT(no_paket)) AS JUMLAH_TRANSAKSI
                            FROM df_ECAT_filter WHERE NAMA_KOMODITAS IS NOT NULL AND kd_instansi_katalog = '{kodeRUP}'
                            GROUP BY NAMA_KOMODITAS ORDER BY JUMLAH_TRANSAKSI DESC LIMIT 10
                        """
                    else:
                        sql_jumlah_transaksi_lokal_nk = f"""
                            SELECT nama_komoditas AS NAMA_KOMODITAS, COUNT(DISTINCT(no_paket)) AS JUMLAH_TRANSAKSI
                            FROM df_ECAT_filter WHERE NAMA_KOMODITAS IS NOT NULL 
                            GROUP BY NAMA_KOMODITAS ORDER BY JUMLAH_TRANSAKSI DESC LIMIT 10
                        """

                    tabel_jumlah_transaksi_lokal_nk = con.execute(sql_jumlah_transaksi_lokal_nk).df()

                    grafik_ecat_nk_11, grafik_ecat_nk_12 = st.columns((4,6))

                    with grafik_ecat_nk_11:
                        
                        # AgGrid(tabel_jumlah_transaksi_lokal_nk)
                        
                        st.dataframe(
                            tabel_jumlah_transaksi_lokal_nk,
                            column_config={
                                "NAMA_KOMODITAS": "NAMA KOMODITAS",
                                "JUMLAH_TRANSAKSI": "JUMLAH TRANSAKSI"
                            },
                            use_container_width=True,
                            hide_index=True
                        )

                    with grafik_ecat_nk_12:

                        grafik_jumlah_transaksi_katalog_lokal_nk = px.bar(tabel_jumlah_transaksi_lokal_nk, x='NAMA_KOMODITAS', y='JUMLAH_TRANSAKSI', text_auto='.2s', title='Grafik Jumlah Transaksi e-Katalog Lokal - Nama Komoditas')
                        grafik_jumlah_transaksi_katalog_lokal_nk.update_traces(textfont_size=12, textangle=0, textposition="outside", cliponaxis=False)
                        st.plotly_chart(grafik_jumlah_transaksi_katalog_lokal_nk, theme="streamlit", use_container_width=True)

                with grafik_ecat_nk_2:

                    #### Query data grafik nilai Transaksi Katalog Lokal berdasarkan Nama Komoditas
                    if jenis_katalog == "Lokal":
                        sql_nilai_transaksi_lokal_nk = f"""
                            SELECT nama_komoditas AS NAMA_KOMODITAS, SUM(total_harga) AS NILAI_TRANSAKSI
                            FROM df_ECAT_filter WHERE NAMA_KOMODITAS IS NOT NULL AND kd_instansi_katalog = '{kodeRUP}'
                            GROUP BY NAMA_KOMODITAS ORDER BY NILAI_TRANSAKSI DESC LIMIT 10
                        """
                    else:
                        sql_nilai_transaksi_lokal_nk = f"""
                            SELECT nama_komoditas AS NAMA_KOMODITAS, SUM(total_harga) AS NILAI_TRANSAKSI
                            FROM df_ECAT_filter WHERE NAMA_KOMODITAS IS NOT NULL
                            GROUP BY NAMA_KOMODITAS ORDER BY NILAI_TRANSAKSI DESC LIMIT 10
                        """

                    tabel_nilai_transaksi_lokal_nk = con.execute(sql_nilai_transaksi_lokal_nk).df()

                    grafik_ecat_nk_21, grafik_ecat_nk_22 = st.columns((4,6))

                    with grafik_ecat_nk_21:

                        st.dataframe(
                            tabel_nilai_transaksi_lokal_nk,
                            column_config={
                                "NAMA_KOMODITAS": "NAMA KOMODITAS",
                                "NILAI_TRANSAKSI": "NILAI TRANSAKSI"
                            },
                            use_container_width=True,
                            hide_index=True
                        )

                    with grafik_ecat_nk_22:
                        
                        grafik_nilai_transaksi_katalog_lokal_nk = px.bar(tabel_nilai_transaksi_lokal_nk, x='NAMA_KOMODITAS', y='NILAI_TRANSAKSI', text_auto='.2s', title='Grafik Nilai Transaksi e-Katalog Lokal - Nama Komoditas')
                        grafik_nilai_transaksi_katalog_lokal_nk.update_traces(textfont_size=12, textangle=0, textposition="outside", cliponaxis=False)
                        st.plotly_chart(grafik_nilai_transaksi_katalog_lokal_nk, theme="streamlit", use_container_width=True)

            with st.container(border=True):

                st.subheader("Berdasarkan Perangkat Daerah (10 Besar)")

                #### Buat Grafik Katalog Berdasarkan Perangkat Daerah
                grafik_ecat_pd_1, grafik_ecat_pd_2 = st.tabs(["| Jumlah Transaksi Perangkat Daerah |", "| Nilai Transaksi Perangkat Daerah |"])

                with grafik_ecat_pd_1:

                    #### Query data grafik jumlah Transaksi Katalog Lokal Perangkat Daerah
                    sql_jumlah_transaksi_lokal_pd = """
                        SELECT nama_satker AS NAMA_SATKER, COUNT(DISTINCT(no_paket)) AS JUMLAH_TRANSAKSI
                        FROM df_ECAT_filter WHERE NAMA_SATKER IS NOT NULL 
                        GROUP BY NAMA_SATKER ORDER BY JUMLAH_TRANSAKSI DESC LIMIT 10
                    """

                    tabel_jumlah_transaksi_lokal_pd = con.execute(sql_jumlah_transaksi_lokal_pd).df()

                    grafik_ecat_pd_11, grafik_ecat_pd_12 = st.columns((4,6))

                    with grafik_ecat_pd_11:
                        
                        # AgGrid(tabel_jumlah_transaksi_lokal_pd)

                        #### Tampilkan data
                        st.dataframe(
                            tabel_jumlah_transaksi_lokal_pd,
                            column_config={
                                "NAMA_SATKER": "NAMA SATKER",
                                "JUMLAH_TRANSAKSI": "JUMLAH TRANSAKSI"
                            },
                            use_container_width=True,
                            hide_index=True
                        )
                        
                    with grafik_ecat_pd_12:

                        grafik_jumlah_transaksi_katalog_lokal_pd = px.bar(tabel_jumlah_transaksi_lokal_pd, x='NAMA_SATKER', y='JUMLAH_TRANSAKSI', text_auto='.2s', title='Grafik Jumlah Transaksi e-Katalog Lokal Perangkat Daerah')
                        grafik_jumlah_transaksi_katalog_lokal_pd.update_traces(textfont_size=12, textangle=0, textposition="outside", cliponaxis=False)
                        st.plotly_chart(grafik_jumlah_transaksi_katalog_lokal_pd, theme="streamlit", use_container_width=True)

                with grafik_ecat_pd_2:

                    #### Query data grafik nilai Transaksi Katalog Lokal Perangkat Daerah
                    sql_nilai_transaksi_lokal_pd = """
                        SELECT nama_satker AS NAMA_SATKER, SUM(total_harga) AS NILAI_TRANSAKSI
                        FROM df_ECAT_filter WHERE NAMA_SATKER IS NOT NULL
                        GROUP BY NAMA_SATKER ORDER BY NILAI_TRANSAKSI DESC LIMIT 10
                    """

                    tabel_nilai_transaksi_lokal_pd = con.execute(sql_nilai_transaksi_lokal_pd).df()

                    grafik_ecat_pd_21, grafik_ecat_pd_22 = st.columns((4,6))

                    with grafik_ecat_pd_21:

                        #### Tampilkan Data
                        st.dataframe(
                            tabel_nilai_transaksi_lokal_pd,
                            column_config={
                                "NAMA_SATKER": "NAMA SATKER",
                                "NILAI_TRANSAKSI": "NILAI TRANSAKSI"
                            },
                            use_container_width=True,
                            hide_index=True
                        )

                    with grafik_ecat_pd_22:
                        
                        grafik_nilai_transaksi_katalog_lokal = px.bar(tabel_nilai_transaksi_lokal_pd, x='NAMA_SATKER', y='NILAI_TRANSAKSI', text_auto='.2s', title='Grafik Nilai Transaksi e-Katalog Lokal Perangkat Daerah')
                        grafik_nilai_transaksi_katalog_lokal.update_traces(textfont_size=12, textangle=0, textposition="outside", cliponaxis=False)
                        st.plotly_chart(grafik_nilai_transaksi_katalog_lokal, theme="streamlit", use_container_width=True)

            with st.container(border=True):

                st.subheader("Berdasarkan Pelaku Usaha (10 Besar)")

                #### Buat Grafik Katalog Berdasarkan Pelaku Usaha
                grafik_ecat_pu_1, grafik_ecat_pu_2 = st.tabs(["| Jumlah Transaksi Pelaku Usaha |", "| Nilai Transaksi Pelaku Usaha |"])

                with grafik_ecat_pu_1:

                    #### Query data grafik jumlah Transaksi Katalog Lokal Pelaku Usaha
                    sql_jumlah_transaksi_ecat_pu = """
                        SELECT nama_penyedia AS NAMA_PENYEDIA, COUNT(DISTINCT(no_paket)) AS JUMLAH_TRANSAKSI
                        FROM df_ECAT_filter WHERE NAMA_PENYEDIA IS NOT NULL 
                        GROUP BY NAMA_PENYEDIA ORDER BY JUMLAH_TRANSAKSI DESC LIMIT 10
                    """

                    tabel_jumlah_transaksi_ecat_pu = con.execute(sql_jumlah_transaksi_ecat_pu).df()

                    grafik_ecat_pu_1_1, grafik_ecat_pu_1_2 = st.columns((4,6))

                    with grafik_ecat_pu_1_1:
                        
                        # AgGrid(tabel_jumlah_transaksi_ecat_pu)
                        
                        #### Tampilkan data
                        st.dataframe(
                            tabel_jumlah_transaksi_ecat_pu,
                            column_config={
                                "NAMA_PENYEDIA": "NAMA PENYEDIA",
                                "JUMLAH_TRANSAKSI": "JUMLAH TRANSAKSI"
                            },
                            use_container_width=True,
                            hide_index=True
                        )

                    with grafik_ecat_pu_1_2:

                        grafik_jumlah_transaksi_ecat_pu = px.bar(tabel_jumlah_transaksi_ecat_pu, x='NAMA_PENYEDIA', y='JUMLAH_TRANSAKSI', text_auto='.2s', title='Grafik Jumlah Transaksi Katalog Pelaku Usaha')
                        grafik_jumlah_transaksi_ecat_pu.update_traces(textfont_size=12, textangle=0, textposition="outside", cliponaxis=False)
                        st.plotly_chart(grafik_jumlah_transaksi_ecat_pu, theme="streamlit", use_container_width=True)

                with grafik_ecat_pu_2:

                    #### Query data grafik nilai Transaksi Katalog Lokal Pelaku Usaha
                    sql_nilai_transaksi_ecat_pu = """
                        SELECT nama_penyedia AS NAMA_PENYEDIA, SUM(total_harga) AS NILAI_TRANSAKSI
                        FROM df_ECAT_filter WHERE NAMA_PENYEDIA IS NOT NULL
                        GROUP BY NAMA_PENYEDIA ORDER BY NILAI_TRANSAKSI DESC LIMIT 10
                    """

                    tabel_nilai_transaksi_ecat_pu = con.execute(sql_nilai_transaksi_ecat_pu).df()

                    grafik_ecat_pu_2_1, grafik_ecat_pu_2_2 = st.columns((4,6))

                    with grafik_ecat_pu_2_1:

                        st.dataframe(
                            tabel_nilai_transaksi_ecat_pu,
                            column_config={
                                "NAMA_PENYEDIA": "NAMA PENYEDIA",
                                "NILAI_TRANSAKSI": "NILAI TRANSAKSI"
                            },
                            use_container_width=True,
                            hide_index=True
                        )

                    with grafik_ecat_pu_2_2:
                        
                        grafik_nilai_transaksi_ecat_pu = px.bar(tabel_nilai_transaksi_ecat_pu, x='NAMA_PENYEDIA', y='NILAI_TRANSAKSI', text_auto='.2s', title='Grafik Nilai Transaksi Katalog Pelaku Usaha')
                        grafik_nilai_transaksi_ecat_pu.update_traces(textfont_size=12, textangle=0, textposition="outside", cliponaxis=False)
                        st.plotly_chart(grafik_nilai_transaksi_ecat_pu, theme="streamlit", use_container_width=True)

        with menu_purchasing_1_2:
            
            #### Buat tombol unduh dataset
            etalase1, etalase2 = st.columns((8,2))
            with etalase1:
                st.header(f"TRANSAKSI E-KATALOG (ETALASE) - {pilih} - TAHUN {tahun}")
            with etalase2:
                st.download_button(
                    label = "📥 Data Tramsaksi E-Katalog",
                    data = unduh_ECAT_excel,
                    file_name = f"TransaksiEKATALOG-{kodeFolder}-{tahun}.xlsx",
                    mime = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                    key = "Download Katalog Etalase"
                )

            st.divider()

            ETALASE_radio_1, ETALASE_radio_2, ETALASE_radio_3, ETALASE_radio_4 = st.columns((1,1,2,6))
            with ETALASE_radio_1:
                jenis_katalog_etalase_array = df_ECAT_OK['jenis_katalog'].unique()
                jenis_katalog_etalase_array_ok = np.insert(jenis_katalog_etalase_array, 0, "Gabungan")
                jenis_katalog_etalase = st.radio("**Jenis Katalog**", jenis_katalog_etalase_array_ok, key="Etalase_Jenis_Katalog")
            with ETALASE_radio_2:
                nama_sumber_dana_etalase = st.radio("**Sumber Dana**", ["Gabungan", "APBD", "BLUD"], key="Etalase_Sumber_Dana")
            with ETALASE_radio_3:
                status_paket_etalase_array = df_ECAT_OK['status_paket'].unique()
                status_paket_etalase_array_ok = np.insert(status_paket_etalase_array, 0, "Gabungan")
                status_paket_etalase = st.radio("**Status Paket**", status_paket_etalase_array_ok, key="Etalase_Status_Paket")

            df_ECAT_ETALASE_Query = f"SELECT * FROM df_ECAT_OK WHERE 1=1"

            # Buat logika untuk query dari pilihan kondisi (3 kondisi) 
            if jenis_katalog_etalase != "Gabungan":
                df_ECAT_ETALASE_Query += f" AND jenis_katalog = '{jenis_katalog_etalase}'"
            if nama_sumber_dana_etalase != "Gabungan":
                if "APBD" in nama_sumber_dana_etalase:
                    df_ECAT_ETALASE_Query += f" AND nama_sumber_dana LIKE '%APBD%'"
                else:
                    df_ECAT_ETALASE_Query += f" AND nama_sumber_dana = '{nama_sumber_dana_etalase}'"
            if status_paket != "Gabungan":
                df_ECAT_ETALASE_Query += f" AND status_paket = '{status_paket_etalase}'"

            df_ECAT_ETALASE = con.execute(df_ECAT_ETALASE_Query).df()

            # if status_paket_etalase == "Gabungan":
            #     df_ECAT_ETALASE = con.execute(f"SELECT * FROM df_ECAT_OK WHERE nama_sumber_dana = '{nama_sumber_dana_etalase}' AND jenis_katalog = '{jenis_katalog_etalase}'").df()
            # else:    
            #     df_ECAT_ETALASE = con.execute(f"SELECT * FROM df_ECAT_OK WHERE nama_sumber_dana = '{nama_sumber_dana_etalase}' AND jenis_katalog = '{jenis_katalog_etalase}' AND paket_status_str = '{status_paket_etalase}'").df()
   
            with ETALASE_radio_4:
                nama_komoditas = st.selectbox("Pilih Etalase Belanja :", df_ECAT_ETALASE['nama_komoditas'].unique(), key="Etalase_Nama_Komoditas")
            st.write(f"Anda memilih : **{jenis_katalog_etalase}** dan **{nama_sumber_dana_etalase}** dan **{status_paket_etalase}**")

            df_ECAT_ETALASE_filter = con.execute(f"SELECT * FROM df_ECAT_ETALASE WHERE nama_komoditas = '{nama_komoditas}'").df()

            jumlah_produk_etalase = df_ECAT_ETALASE_filter['kd_produk'].unique().shape[0]
            jumlah_penyedia_etalase = df_ECAT_ETALASE_filter['kd_penyedia'].unique().shape[0]
            jumlah_trx_etalase = df_ECAT_ETALASE_filter['no_paket'].unique().shape[0]
            nilai_trx_etalase = df_ECAT_ETALASE_filter['total_harga'].sum()

            coetalase1, coetalase2, coetalase3, coetalase4 = st.columns(4)
            coetalase1.metric(label="Jumlah Produk Katalog", value="{:,}".format(jumlah_produk_etalase))
            coetalase2.metric(label="Jumlah Penyedia Katalog", value="{:,}".format(jumlah_penyedia_etalase))
            coetalase3.metric(label="Jumlah Transaksi Katalog", value="{:,}".format(jumlah_trx_etalase))
            coetalase4.metric(label="Nilai Transaksi Katalog", value="{:,.2f}".format(nilai_trx_etalase))

            st.divider()

            with st.container(border=True):

                st.subheader("Berdasarkan Pelaku Usaha (10 Besar)")

                grafik_etalase_pu_1, grafik_etalase_pu_2 = st.tabs(["| Jumlah Transaksi Pelaku Usaha |", "| Nilai Transaksi Pelaku Usaha |"])

                with grafik_etalase_pu_1:
                    
                    #### Query data grafik jumlah Transaksi Katalog Lokal Pelaku Usaha tiap Etalase
                    sql_jumlah_transaksi_ecat_pu_etalase = """
                        SELECT nama_penyedia AS NAMA_PENYEDIA, COUNT(DISTINCT(no_paket)) AS JUMLAH_TRANSAKSI
                        FROM df_ECAT_ETALASE_filter WHERE NAMA_PENYEDIA IS NOT NULL
                        GROUP BY NAMA_PENYEDIA ORDER BY JUMLAH_TRANSAKSI DESC LIMIT 10
                    """

                    tabel_jumlah_transaksi_ecat_pu_etalase = con.execute(sql_jumlah_transaksi_ecat_pu_etalase).df()

                    grafik_etalase_pu_1_1, grafik_etalase_pu_1_2 = st.columns((4,6))

                    with grafik_etalase_pu_1_1:

                        # AgGrid(tabel_jumlah_transaksi_ecat_pu_etalase)

                        #### Tampilkan data
                        st.dataframe(
                            tabel_jumlah_transaksi_ecat_pu_etalase,
                            column_config={
                                "NAMA_PENYEDIA": "NAMA PENYEDIA",
                                "JUMLAH_TRANSAKSI": "JUMLAH TRANSAKSI"
                            },
                            use_container_width=True,
                            hide_index=True,
                        )

                    with grafik_etalase_pu_1_2:

                        grafik_jumlah_transaksi_ecat_pu_etalase = px.bar(tabel_jumlah_transaksi_ecat_pu_etalase, x='NAMA_PENYEDIA', y='JUMLAH_TRANSAKSI', text_auto='.2s', title='Grafik Jumlah Transaksi Katalog Pelaku Usaha')
                        grafik_jumlah_transaksi_ecat_pu_etalase.update_traces(textfont_size=12, textangle=0, textposition="outside", cliponaxis=False)
                        st.plotly_chart(grafik_jumlah_transaksi_ecat_pu_etalase, theme="streamlit", use_container_width=True)

                with grafik_etalase_pu_2:

                    #### Query data grafik nilai Transaksi Katalog Lokal Pelaku Usaha tiap Etalase
                    sql_nilai_transaksi_ecat_pu_etalase = """
                        SELECT nama_penyedia AS NAMA_PENYEDIA, SUM(total_harga) AS NILAI_TRANSAKSI
                        FROM df_ECAT_ETALASE_filter WHERE NAMA_PENYEDIA IS NOT NULL
                        GROUP BY NAMA_PENYEDIA ORDER BY NILAI_TRANSAKSI DESC LIMIT 10
                    """

                    tabel_nilai_transaksi_ecat_pu_etalase = con.execute(sql_nilai_transaksi_ecat_pu_etalase).df()

                    grafik_etalase_pu_2_1, grafik_etalase_pu_2_2 = st.columns((4,6))

                    with grafik_etalase_pu_2_1:

                        st.dataframe(
                            tabel_nilai_transaksi_ecat_pu_etalase,
                            column_config={
                                "NAMA_PENYEDIA": "NAMA PENYEDIA",
                                "NILAI_TRANSAKSI": "NILAI TRANSAKSI (Rp.)",
                            },
                            use_container_width=True,
                            hide_index=True,
                        )

                    with grafik_etalase_pu_2_2:

                        grafik_nilai_transaksi_ecat_pu_etalase = px.bar(tabel_nilai_transaksi_ecat_pu_etalase, x='NAMA_PENYEDIA', y='NILAI_TRANSAKSI', text_auto='.2s', title='Grafik Nilai Transaksi Katalog Pelaku Usaha')
                        grafik_nilai_transaksi_ecat_pu_etalase.update_traces(textfont_size=12, textangle=0, textposition="outside", cliponaxis=False)
                        st.plotly_chart(grafik_nilai_transaksi_ecat_pu_etalase, theme="streamlit", use_container_width=True)

        with menu_purchasing_1_3:
            
            #### Query E-Katalog Tabel Nilai Etalase
            df_ECAT_OK_PIVOT = con.execute("SELECT nama_komoditas, jenis_katalog, total_harga FROM df_ECAT_OK").df()
            df_ECAT_PIVOT_TABEL = con.execute("PIVOT df_ECAT_OK_PIVOT ON jenis_katalog USING SUM(total_harga)").df().fillna(0)
            df_ECAT_PIVOT_TABEL_OK = con.execute("SELECT nama_komoditas AS NAMA_KOMODITAS, Lokal AS LOKAL, Nasional AS NASIONAL, Sektoral AS SEKTORAL FROM df_ECAT_PIVOT_TABEL").df()

            #### Buat tombol unduh dataset
            unduh_ETALASE_PIVOT_excel = download_excel(df_ECAT_PIVOT_TABEL_OK)

            etalase_pivot_1, etalase_pivot_2 = st.columns((8,2))
            with etalase_pivot_1:
                st.header(f"TABEL NILAI ETALASE - {pilih} - TAHUN {tahun}")
            with etalase_pivot_2:
                st.download_button(
                    label = "📥 Download Tabel Nilai Etalase",
                    data = unduh_ETALASE_PIVOT_excel,
                    file_name = f"TabelNilaiEtalase-{kodeFolder}-{tahun}.xlsx",
                    mime = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )

            st.divider()

            #### Tampilkan data
            st.dataframe(
                df_ECAT_PIVOT_TABEL_OK,
                column_config={
                    "NAMA_KOMODITAS": "NAMA KOMODITAS",
                    "LOKAL": "LOKAL (Rp.)",
                    "NASIONAL": "NASIONAL (Rp.)",
                    "SEKTORAL": "SEKTORAL (Rp.)"
                },
                use_container_width=True,
                hide_index=True,
                height=1000
            )
            
    except Exception:
        st.error("Gagal Analisa Transaksi E-Katalog")

## Tab menu Transaksi Toko Daring
with menu_purchasing_2:

    try:
        ### Baca file parquet Toko Daring
        df_BELA = tarik_data_parquet(DatasetPURCHASINGBELA)

        ### Buat tombol unduh dataset
        unduh_BELA_excel = download_excel(df_BELA)

        menu_bela_1, menu_bela_2 = st.columns((7,3))
        with menu_bela_1:
            st.header(f"TRANSAKSI TOKO DARING - {pilih} - TAHUN {tahun}")
        with menu_bela_2:
            st.download_button(
                label = "📥 Data Tramsaksi Toko Daring",
                data = unduh_BELA_excel,
                file_name = f"TransaksiTokoDaring-{kodeFolder}-{tahun}.xlsx",
                mime = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )

        st.divider()

        DARING_radio_1, DARING_radio_2, DARING_radio_3 = st.columns((2,2,6))
        with DARING_radio_1:
            status_verifikasi = st.radio("**Status Verifikasi Transaksi**", ["verified", "unverified", "Gabungan"])
        with DARING_radio_2:
            status_ppmse = st.radio("**Status Konfirmasi PPMSE**", ["gagal", "selesai"])
        st.write(f"Anda memilih : **{status_verifikasi}** dan **{status_ppmse}**")

        ### Query Toko Daring
        if (status_verifikasi == "Gabungan"):
            if status_ppmse == "selesai":
                df_BELA_filter = con.execute(f"SELECT * FROM df_BELA WHERE LENGTH(nama_satker) > 1 AND (status_konfirmasi_ppmse = '{status_ppmse}' OR status_konfirmasi_ppmse IS NULL)").df()
            else:
                df_BELA_filter = con.execute(f"SELECT * FROM df_BELA WHERE LENGTH(nama_satker) > 1 AND status_konfirmasi_ppmse = '{status_ppmse}'").df()
        else:
            if status_ppmse == "selesai":
                df_BELA_filter = con.execute(f"SELECT * FROM df_BELA WHERE LENGTH(nama_satker) > 1 AND status_verif = '{status_verifikasi}' AND (status_konfirmasi_ppmse = '{status_ppmse}' OR status_konfirmasi_ppmse IS NULL)").df()
            else:
                df_BELA_filter = con.execute(f"SELECT * FROM df_BELA WHERE LENGTH(nama_satker) > 1 AND status_verif = '{status_verifikasi}' AND status_konfirmasi_ppmse = '{status_ppmse}'").df()
        
        jumlah_trx_daring = df_BELA_filter['order_id'].unique().shape[0]
        nilai_trx_daring = df_BELA_filter['valuasi'].sum()

        cobela1, cobela2, cobela3, cobela4 = st.columns(4)
        cobela1.subheader("")
        cobela2.metric(label="Jumlah Transaksi Toko Daring", value="{:,}".format(jumlah_trx_daring))
        cobela3.metric(label="Nilai Transaksi Toko Daring", value="{:,.2f}".format(nilai_trx_daring))
        cobela4.subheader("")

        style_metric_cards(background_color="#000", border_left_color="#D3D3D3")

        st.divider()

        with st.container(border=True):

            st.subheader("Berdasarkan Perangkat Daerah (10 Besar)")

            grafik_bela_pd_11, grafik_bela_pd_12 = st.tabs(["| Jumlah Transaksi Perangkat Daerah |", "| Nilai Transaksi Perangkat Daerah |"])

            with grafik_bela_pd_11:

                #### Query data grafik jumlah Transaksi Toko Daring Perangkat Daerah
                sql_jumlah_transaksi_bela_pd = """
                    SELECT nama_satker AS NAMA_SATKER, COUNT(DISTINCT(order_id)) AS JUMLAH_TRANSAKSI
                    FROM df_BELA_filter WHERE NAMA_SATKER IS NOT NULL
                    GROUP BY NAMA_SATKER ORDER BY JUMLAH_TRANSAKSI DESC LIMIT 10
                """

                tabel_jumlah_transaksi_bela_pd = con.execute(sql_jumlah_transaksi_bela_pd).df()

                grafik_bela_pd_11_1, grafik_bela_pd_11_2 = st.columns((4,6))

                with grafik_bela_pd_11_1:

                    # AgGrid(tabel_jumlah_transaksi_bela_pd)

                    st.dataframe(
                        tabel_jumlah_transaksi_bela_pd,
                        column_config={
                            "NAMA_SATKER": "NAMA SATKER",
                            "JUMLAH_TRANSAKSI": "JUMLAH TRANSAKSI"
                        },
                        use_container_width=True,
                        hide_index=True
                    )

                with grafik_bela_pd_11_2:

                    grafik_jumlah_transaksi_bela_pd = px.bar(tabel_jumlah_transaksi_bela_pd, x='NAMA_SATKER', y='JUMLAH_TRANSAKSI', text_auto='.2s', title='Grafik Jumlah Transaksi Toko Daring Perangkat Daerah')
                    grafik_jumlah_transaksi_bela_pd.update_traces(textfont_size=12, textangle=0, textposition="outside", cliponaxis=False)
                    st.plotly_chart(grafik_jumlah_transaksi_bela_pd, theme="streamlit", use_container_width=True)

            with grafik_bela_pd_12:

                #### Query data grafik nilai Transaksi Toko Daring Perangkat Daerah
                sql_nilai_transaksi_bela_pd = """
                    SELECT nama_satker AS NAMA_SATKER, SUM(valuasi) AS NILAI_TRANSAKSI
                    FROM df_BELA_filter WHERE NAMA_SATKER IS NOT NULL
                    GROUP BY NAMA_SATKER ORDER BY NILAI_TRANSAKSI DESC LIMIT 10
                """

                tabel_nilai_transaksi_bela_pd = con.execute(sql_nilai_transaksi_bela_pd).df()

                grafik_bela_pd_12_1, grafik_bela_pd_12_2 = st.columns((4,6))

                with grafik_bela_pd_12_1:

                    st.dataframe(
                        tabel_nilai_transaksi_bela_pd,
                        column_config={
                            "NAMA_SATKER": "NAMA SATKER",
                            "NILAI_TRANSAKSI": "NILAI TRANSAKSI (Rp.)" 
                        },
                        use_container_width=True,
                        hide_index=True
                    )

                with grafik_bela_pd_12_2:

                    grafik_nilai_transaksi_bela_pd = px.bar(tabel_nilai_transaksi_bela_pd, x='NAMA_SATKER', y='NILAI_TRANSAKSI', text_auto='.2s', title='Grafik Nilai Transaksi Toko Daring Perangkat Daerah')
                    grafik_nilai_transaksi_bela_pd.update_traces(textfont_size=12, textangle=0, textposition="outside", cliponaxis=False)
                    st.plotly_chart(grafik_nilai_transaksi_bela_pd, theme="streamlit", use_container_width=True)

        with st.container(border=True):

            st.subheader("Berdasarkan Pelaku Usaha (10 Besar)")

            grafik_bela_pu_11, grafik_bela_pu_12 = st.tabs(["| Jumlah Transaksi Pelaku Usaha |", "| Nilai Transaksi Pelaku Usaha |"])

            with grafik_bela_pu_11:

                #### Query data grafik jumlah Transaksi Toko Daring Pelaku Usaha
                sql_jumlah_transaksi_bela_pu = """
                    SELECT nama_merchant AS NAMA_TOKO, COUNT(DISTINCT(order_id)) AS JUMLAH_TRANSAKSI
                    FROM df_BELA_filter WHERE NAMA_TOKO IS NOT NULL
                    GROUP BY NAMA_TOKO ORDER BY JUMLAH_TRANSAKSI DESC LIMIT 10
                """

                tabel_jumlah_transaksi_bela_pu = con.execute(sql_jumlah_transaksi_bela_pu).df()

                grafik_bela_pu_11_1, grafik_bela_pu_11_2 = st.columns((4,6))

                with grafik_bela_pu_11_1:

                    # AgGrid(tabel_jumlah_transaksi_bela_pu)

                    st.dataframe(
                        tabel_jumlah_transaksi_bela_pu,
                        column_config={
                            "NAMA_TOKO": "NAMA TOKO",
                            "JUMLAH_TRANSAKSI": "JUMLAH TRANSAKSI" 
                        },
                        use_container_width=True,
                        hide_index=True
                    )

                with grafik_bela_pu_11_2:

                    grafik_jumlah_transaksi_bela_pu = px.bar(tabel_jumlah_transaksi_bela_pu, x='NAMA_TOKO', y='JUMLAH_TRANSAKSI', text_auto='.2s', title='Grafik Jumlah Transaksi Toko Daring Pelaku Usaha')
                    grafik_jumlah_transaksi_bela_pu.update_traces(textfont_size=12, textangle=0, textposition="outside", cliponaxis=False)
                    st.plotly_chart(grafik_jumlah_transaksi_bela_pu, theme="streamlit", use_container_width=True)

            with grafik_bela_pu_12:

                #### Query data grafik nilai Transaksi Toko Daring Pelaku Usaha
                sql_nilai_transaksi_bela_pu = """
                    SELECT nama_merchant AS NAMA_TOKO, SUM(valuasi) AS NILAI_TRANSAKSI
                    FROM df_BELA_filter WHERE NAMA_TOKO IS NOT NULL
                    GROUP BY NAMA_TOKO ORDER BY NILAI_TRANSAKSI DESC LIMIT 10
                """

                tabel_nilai_transaksi_bela_pu = con.execute(sql_nilai_transaksi_bela_pu).df()

                grafik_bela_pu_12_1, grafik_bela_pu_12_2 = st.columns((4,6))

                with grafik_bela_pu_12_1:

                    st.dataframe(
                        tabel_nilai_transaksi_bela_pu,
                        column_config={
                            "NAMA_TOKO": "NAMA TOKO",
                            "NILAI_TRANSAKSI": "NILAI TRANSAKSI (Rp.)" 
                        },
                        use_container_width=True,
                        hide_index=True
                    )

                with grafik_bela_pu_12_2:

                    grafik_nilai_transaksi_bela_pu = px.bar(tabel_nilai_transaksi_bela_pu, x='NAMA_TOKO', y='NILAI_TRANSAKSI', text_auto='.2s', title='Grafik Nilai Transaksi Toko Daring Pelaku Usaha')
                    grafik_nilai_transaksi_bela_pu.update_traces(textfont_size=12, textangle=0, textposition="outside", cliponaxis=False)
                    st.plotly_chart(grafik_nilai_transaksi_bela_pu, theme="streamlit", use_container_width=True)

    except Exception:
        st.error("Gagal Analisa Transaksi Toko Daring")