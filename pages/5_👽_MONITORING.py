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
    "KAB. TANGGERANG": {"folder": "tgr", "RUP": "D50", "LPSE": "333"},
    "KAB. KATINGAN": {"folder": "ktg", "RUP": "D236", "LPSE": "438"}
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
### Dataset SIRUP
if int(tahun) < 2024:
    DatasetRUPPP = f"https://data.pbj.my.id/{kodeRUP}/sirup/RUP-PaketPenyedia-Terumumkan{tahun}.parquet"
    DatasetRUPPS = f"https://data.pbj.my.id/{kodeRUP}/sirup/RUP-PaketSwakelola-Terumumkan{tahun}.parquet"
    DatasetRUPSA = f"https://data.pbj.my.id/{kodeRUP}/sirup/RUP-StrukturAnggaranPD{tahun}.parquet"
else:
    DatasetRUPPP = f"https://data.pbj.my.id/{kodeRUP}/sirup/RUP-PaketPenyedia-Terumumkan-{tahun}-03-31.parquet"
    DatasetRUPPS = f"https://data.pbj.my.id/{kodeRUP}/sirup/RUP-PaketSwakelola-Terumumkan-{tahun}-03-31.parquet"
    DatasetRUPSA = f"https://data.pbj.my.id/{kodeRUP}/sirup/RUP-StrukturAnggaranPD-{tahun}-03-31.parquet"

### Dataset Tender
DatasetSPSETenderPengumuman = f"https://data.pbj.my.id/{kodeLPSE}/spse/SPSE-TenderPengumuman{tahun}.parquet"
DatasetSPSETenderKontrak = f"https://data.pbj.my.id/{kodeLPSE}/spse/SPSE-TenderEkontrak-Kontrak{tahun}.parquet"
DatasetSIKAPTender = f"https://data.pbj.my.id/{kodeRUP}/sikap/SIKaP-PenilaianKinerjaPenyedia-Tender{tahun}.parquet"

### Dataset Non Tender
DatasetSPSENonTenderPengumuman = f"https://data.pbj.my.id/{kodeLPSE}/spse/SPSE-NonTenderPengumuman{tahun}.parquet"
DatasetSIKAPNonTender = f"https://data.pbj.my.id/{kodeRUP}/sikap/SiKAP-PenilaianKinerjaPenyedia-NonTender{tahun}.parquet"

### Dataset E-Purchasing (Katalog dan Toko Daring)
DatasetPURCHASINGECAT = f"https://data.pbj.my.id/{kodeRUP}/epurchasing/Ecat-PaketEPurchasing{tahun}.parquet"
DatasetPURCHASINGBELA = f"https://data.pbj.my.id/{kodeRUP}/epurchasing/Bela-TokoDaringRealisasi{tahun}.parquet"

## Baca file parquet
try:
    df_RUPPP = tarik_data_parquet(DatasetRUPPP)
    df_RUPPS = tarik_data_parquet(DatasetRUPPS)
    df_RUPSA = tarik_data_parquet(DatasetRUPSA)
    df_SPSETenderPengumuman = tarik_data_parquet(DatasetSPSETenderPengumuman)
    df_SPSENonTenderPengumuman = tarik_data_parquet(DatasetSPSENonTenderPengumuman)
    df_SPSETenderKontrak = tarik_data_parquet(DatasetSPSETenderKontrak)
    df_ECAT = tarik_data_parquet(DatasetPURCHASINGECAT)

except Exception:
    st.error("Gagal Baca data Monitoring ITKP")

#####
# Presentasi Monitoring dan SIKAP
#####

# Sajikan Menu
menu_monitoring_1, menu_monitoring_2 = st.tabs(["| PREDIKSI ITKP |", "| PENILAIAN SIKAP |"])

## Tab menu monitoring ITKP
with menu_monitoring_1:

    st.header(f"PREDIKSI ITKP PEMANFAATAN SISTEM PENGADAAN - {pilih} - TAHUN {tahun}")
    st.divider()

    nama_satker_unik_array = df_RUPPP['nama_satker'].unique()
    nama_satker_unik_array_ok = np.insert(nama_satker_unik_array, 0, "Semua Perangkat Daerah")
    nama_satker = st.selectbox("Pilih Perangkat Daerah :", nama_satker_unik_array_ok, key="Nama_Satker_Monitoring")

    st.divider()

    ## Prediksi ITKP RUP
    try:
        ### Baca file parquet RUP
        # df_RUPPP = tarik_data_parquet(DatasetRUPPP)
        # df_RUPPS = tarik_data_parquet(DatasetRUPPS)
        # df_RUPSA = tarik_data_parquet(DatasetRUPSA)

        ### Query RUP
        RUPPP_umumkan_sql = f"SELECT * FROM df_RUPPP WHERE status_umumkan_rup = 'Terumumkan' AND status_aktif_rup = 'TRUE' AND metode_pengadaan <> '0'"
        RUPPS_umumkan_sql = f"""
            SELECT nama_satker, kd_rup, nama_paket, pagu, tipe_swakelola, volume_pekerjaan, uraian_pekerjaan, 
            tgl_pengumuman_paket, tgl_awal_pelaksanaan_kontrak, nama_ppk, status_umumkan_rup
            FROM df_RUPPS
            WHERE status_umumkan_rup = 'Terumumkan'
        """
        RUPSA_umumkan_sql = f"SELECT * FROM df_RUPSA WHERE 1=1"

        if nama_satker != "Semua Perangkat Daerah":
            RUPPP_umumkan_sql += f" AND nama_satker = '{nama_satker}'" 
            RUPPS_umumkan_sql += f" AND nama_satker = '{nama_satker}'"
            RUPSA_umumkan_sql += f" AND nama_satker = '{nama_satker}'"

        df_RUPPP_umumkan = con.execute(RUPPP_umumkan_sql).df()
        df_RUPPS_umumkan = con.execute(RUPPS_umumkan_sql).df()
        df_RUPSA_umumkan = con.execute(RUPSA_umumkan_sql).df()

        belanja_pengadaan = df_RUPSA_umumkan['belanja_pengadaan'].sum()
        nilai_total_rup = df_RUPPP_umumkan['pagu'].sum() + df_RUPPS_umumkan['pagu'].sum()
        persen_capaian_rup = nilai_total_rup / belanja_pengadaan
        if persen_capaian_rup > 1:
            prediksi_itkp_rup = (1 - (persen_capaian_rup - 1)) * 10
        elif persen_capaian_rup > 0.5:
            prediksi_itkp_rup = persen_capaian_rup * 10
        else:
            prediksi_itkp_rup = 0

        ### Tampilan Prediksi ITKP
        st.subheader("**RENCANA UMUM PENGADAAN**")
        itkp_sirup_1, itkp_sirup_2, itkp_sirup_3, itkp_sirup_4 = st.columns(4)
        itkp_sirup_1.metric(label="BELANJA PENGADAAN (MILYAR)", value="{:,.2f}".format(belanja_pengadaan / 1000000000))
        itkp_sirup_2.metric(label="NILAI RUP (MILYAR)", value="{:,.2f}".format(nilai_total_rup / 1000000000))
        itkp_sirup_3.metric(label="PERSENTASE", value="{:.2%}".format(persen_capaian_rup))
        itkp_sirup_4.metric(label="NILAI PREDIKSI (DARI 10)", value="{:,}".format(round(prediksi_itkp_rup, 2)))

    except Exception:
        st.error("Gagal Analisa Prediksi ITKP RUP")

    ## Prediksi ITKP E-Tendering
    try:
        ### Baca file Parquet E-Tendering
        # df_SPSETenderPengumuman = tarik_data_parquet(DatasetSPSETenderPengumuman)
        
        ### Query E-Tendering
        df_SPSETenderPengumuman_filter = con.execute("SELECT kd_tender, pagu, hps FROM df_SPSETenderPengumuman WHERE status_tender = 'Selesai'").df()
        df_RUPPP_umumkan_etendering = con.execute("SELECT pagu FROM df_RUPPP_umumkan WHERE metode_pengadaan IN ('Tender', 'Tender Cepat', 'Seleksi')").df()

        nilai_etendering_rup = df_RUPPP_umumkan_etendering['pagu'].sum()
        nilai_etendering_spse = df_SPSETenderPengumuman_filter['pagu'].sum()
        persen_capaian_etendering = nilai_etendering_spse / nilai_etendering_rup
        if persen_capaian_etendering > 1:
            prediksi_itkp_etendering = (1 - (persen_capaian_etendering - 1)) * 5
        elif persen_capaian_etendering > 0.5:
            prediksi_itkp_etendering = persen_capaian_etendering * 5
        else:
            prediksi_itkp_etendering = 0

        ### Tampilan Prediksi E-Tendering
        st.subheader("**E-TENDERING**")
        itkp_etendering_1, itkp_etendering_2, itkp_etendering_3, itkp_etendering_4 = st.columns(4)
        itkp_etendering_1.metric(label="NILAI RUP E-TENDERING (MILYAR)", value="{:,.2f}".format(nilai_etendering_rup / 1000000000))
        itkp_etendering_2.metric(label="E-TENDERING SELESAI (MILYAR)", value="{:,.2f}".format(nilai_etendering_spse / 1000000000))
        itkp_etendering_3.metric(label="PERSENTASE", value="{:.2%}".format(persen_capaian_etendering))
        itkp_etendering_4.metric(label="NILAI PREDIKSI (DARi 5)", value="{:,}".format(round(prediksi_itkp_etendering, 2)))

    except Exception:
        st.error("Gagal Analisa Prediksi ITKP E-TENDERING")

    ## Prediksi ITKP Non E-Tendering
    try:
        ### Baca file Parquet Non E-Tendering
        # df_SPSENonTenderPengumuman = tarik_data_parquet(DatasetSPSENonTenderPengumuman)

        ### Query Non E-Tendering
        df_SPSENonTenderPengumuman_filter = con.execute("SELECT pagu, hps FROM df_SPSENonTenderPengumuman WHERE status_nontender = 'Selesai'").df()
        df_RUPPP_umumkan_nonetendering = con.execute("SELECT pagu FROM df_RUPPP_umumkan WHERE metode_pengadaan IN ('Pengadaan Langsung', 'Penunjukan Langsung')").df()

        nilai_nonetendering_rup = df_RUPPP_umumkan_nonetendering['pagu'].sum()
        nilai_nonetendering_spse = df_SPSENonTenderPengumuman_filter['pagu'].sum()
        persen_capaian_nonetendering = nilai_nonetendering_spse / nilai_nonetendering_rup
        if persen_capaian_nonetendering > 1:
            prediksi_itkp_nonetendering = (1 - (persen_capaian_nonetendering - 1)) * 5
        elif persen_capaian_nonetendering > 0.5:
            prediksi_itkp_nonetendering = persen_capaian_nonetendering * 5
        else:
            prediksi_itkp_nonetendering = 0

        ### Tampilan Prediksi Non E-Tendering
        st.subheader("**NON E-TENDERING**")
        itkp_nonetendering_1, itkp_nonetendering_2, itkp_nonetendering_3, itkp_nonetendering_4 = st.columns(4)
        itkp_nonetendering_1.metric(label="NILAI RUP NON E-TENDERING (MILYAR)", value="{:,.2f}".format(nilai_nonetendering_rup / 1000000000))
        itkp_nonetendering_2.metric(label="NON E-TENDERING SELESAI (MILYAR)", value="{:,.2f}".format(nilai_nonetendering_spse / 1000000000))
        itkp_nonetendering_3.metric(label="PERSENTASE", value="{:.2%}".format(persen_capaian_nonetendering))
        itkp_nonetendering_4.metric(label="NILAI PREDIKSI (DARI 5)", value="{:,}".format(round(prediksi_itkp_nonetendering, 2)))

    except Exception:
        st.error("Gagal Analisa Prediksi ITKP NON E-TENDERING")

    ## Prediksi ITKP E-KONTRAK
    try:
        ### Baca file Parquet E-Kontrak
        # df_SPSETenderKontrak = tarik_data_parquet(DatasetSPSETenderKontrak)
        df_SPSETenderKontrak_filter = con.execute("SELECT kd_tender FROM df_SPSETenderKontrak").df()

        ### Query E-Kontrak
        jumlah_tender_selesai = df_SPSETenderPengumuman_filter['kd_tender'].count()
        jumlah_tender_kontrak = df_SPSETenderKontrak_filter['kd_tender'].count()
        persen_capaian_ekontrak = jumlah_tender_kontrak / jumlah_tender_selesai
        if persen_capaian_ekontrak > 1:
            prediksi_itkp_ekontrak = (1 - (persen_capaian_ekontrak - 1)) * 5
        elif persen_capaian_ekontrak > 0.5:
            prediksi_itkp_ekontrak = persen_capaian_ekontrak * 5
        else:
            prediksi_itkp_ekontrak = 0

        ### Tampilan Prediksi E-Kontrak
        st.subheader("**E-KONTRAK**")
        itkp_ekontrak_1, itkp_ekontrak_2, itkp_ekontrak_3, itkp_ekontrak_4 = st.columns(4)
        itkp_ekontrak_1.metric(label="JUMLAH PAKET TENDER SELESAI", value="{:,}".format(jumlah_tender_selesai))
        itkp_ekontrak_2.metric(label="JUMLAH PAKET TENDER BERKONTRAK", value="{:,}".format(jumlah_tender_kontrak))
        itkp_ekontrak_3.metric(label="PERSENTASE", value="{:.2%}".format(persen_capaian_ekontrak))
        itkp_ekontrak_4.metric(label="NILAI PREDIKSI (DARI 5)", value="{:,}".format(round(prediksi_itkp_ekontrak, 2)))

    except Exception:
        st.error("Gagal Analisa Prediksi ITKP E-KONTRAK")

    ## Prediksi ITKP E-KATALOG
    try:
        ### Baca file Parquet E-Katalog
        # df_ECAT = tarik_data_parquet(DatasetPURCHASINGECAT)
        df_ECAT_filter = df_ECAT[df_ECAT['paket_status_str'] == 'Paket Selesai']

        ### Query E-Katalog
        jumlah_trx_ekatalog = df_ECAT['kd_paket'].nunique()
        jumlah_trx_ekatalog_selesai = df_ECAT_filter['kd_paket'].nunique()
        persen_capaian_ekatalog = jumlah_trx_ekatalog_selesai / jumlah_trx_ekatalog
        if persen_capaian_ekatalog > 1:
            prediksi_itkp_ekatalog = (1 - (persen_capaian_ekatalog - 1)) * 4
        elif persen_capaian_ekatalog > 0.5:
            prediksi_itkp_ekatalog = persen_capaian_ekatalog * 4
        else:
            prediksi_itkp_ekatalog = 0

        ### Tampilan Prediksi E-Katalog
        st.subheader("**E-KATALOG**")
        itkp_ekatalog_1, itkp_ekatalog_2, itkp_ekatalog_3, itkp_ekatalog_4 = st.columns(4)
        itkp_ekatalog_1.metric(label="JUMLAH TRANSAKDI E-KATALOG", value="{:,}".format(jumlah_trx_ekatalog))
        itkp_ekatalog_2.metric(label="JUMLAH TRANSAKSI E-KATALOG (SELESAI)", value="{:,}".format(jumlah_trx_ekatalog_selesai))
        itkp_ekatalog_3.metric(label="PERSENTASE", value="{:.2%}".format(persen_capaian_ekatalog))
        itkp_ekatalog_4.metric(label="NILAI PREDIKSI (DARI 4)", value="{:,}".format(round(prediksi_itkp_ekatalog, 2)))
        
    except Exception:
        st.error("Gagal Analisa Prediksi ITKP E-KATALOG")

    ## Prediksi ITKP TOKO DARING
    try:
        ### Baca file Parquet Toko Daring
        df_BELA = tarik_data_parquet(DatasetPURCHASINGBELA)
        df_BELA_filter = con.execute("SELECT valuasi FROM df_BELA WHERE nama_satker IS NOT NULL AND status_verif = 'verified' AND status_konfirmasi_ppmse = 'selesai'").df()

        ### Query Toko Daring
        jumlah_trx_bela = df_BELA_filter['valuasi'].count()
        nilai_trx_bela = df_BELA_filter['valuasi'].sum()
        if jumlah_trx_bela >= 1:
            prediksi_itkp_bela = 1
        else:
            prediksi_itkp_bela = 0

        ### Tampilan Prediksi Toko Daring
        st.subheader("**TOKO DARING**")
        itkp_bela_1, itkp_bela_2, itkp_bela_3 = st.columns(3)
        itkp_bela_1.metric(label="JUMLAH TRANSAKSI TOKO DARING", value="{:,}".format(jumlah_trx_bela))
        itkp_bela_2.metric(label="NILAI TRANSAKSI TOKO DARING", value="{:,.2f}".format(nilai_trx_bela))
        itkp_bela_3.metric(label="NILAI PREDIKSI (DARI 1)", value="{:,}".format(round(prediksi_itkp_bela, 2)))

    except Exception:
        st.error("Gagal Analisa Prediksi ITKP TOKO DARING")

## Tab menu monitoring SIKAP
with menu_monitoring_2:

    st.header(f"PENILAIAN SIKAP - {pilih} - TAHUN {tahun}")

    menu_monitoring_2_1, menu_monitoring_2_2 = st.tabs(["| SIKAP TENDER |", "| SIKAP NON TENDER |"])

    ## Penilaian SIKAP TENDER
    with menu_monitoring_2_1:

        try:
            st.subheader("SIKAP TENDER")

            ### Baca file parquet SIKAP TENDER
            df_SPSETenderPengumuman = tarik_data_parquet(DatasetSPSETenderPengumuman)
            df_SIKAPTender = tarik_data_parquet(DatasetSIKAPTender)

            ### Query SIKAP TENDER
            df_SPSETenderPengumuman_filter = con.execute(f"SELECT kd_tender, nama_satker, pagu, hps, jenis_pengadaan, mtd_pemilihan, FROM df_SPSETenderPengumuman WHERE status_tender = 'Selesai'").df()
            df_SIKAPTender_filter = con.execute(f"SELECT kd_tender, nama_paket, nama_ppk, nama_penyedia, npwp_penyedia, indikator_penilaian, nilai_indikator, total_skors FROM df_SIKAPTender").df()
            df_SIKAPTender_OK = df_SPSETenderPengumuman_filter.merge(df_SIKAPTender_filter, how='right', on='kd_tender')

            jumlah_trx_spse_t_pengumuman = df_SPSETenderPengumuman_filter['kd_tender'].unique().shape[0]
            jumlah_trx_sikap_t = df_SIKAPTender_filter['kd_tender'].unique().shape[0]
            selisih_sikap_t = jumlah_trx_spse_t_pengumuman - jumlah_trx_sikap_t

            ### Tampilan SIKAP TENDER
            data_sikap_t_1, data_sikap_t_2, data_sikap_t_3 = st.columns(3)
            data_sikap_t_1.metric(label="Jumlah Paket Tender Selesai", value="{:,}".format(jumlah_trx_spse_t_pengumuman))
            data_sikap_t_2.metric(label="Jumlah Paket Tender Sudah Dinilai", value="{:,}".format(jumlah_trx_sikap_t))
            data_sikap_t_3.metric(label="Jumlah Paket Tender Belum Dinilai", value="{:,}".format(selisih_sikap_t))

            st.divider()

            df_SIKAPTender_OK_filter = con.execute("SELECT nama_paket AS NAMA_PAKET, kd_tender AS KODE_PAKET, jenis_pengadaan AS JENIS_PENGADAAN, nama_ppk AS NAMA_PPK, nama_penyedia AS NAMA_PENYEDIA, AVG(total_skors) AS SKOR_PENILAIAN FROM df_SIKAPTender_OK GROUP BY KODE_PAKET, NAMA_PAKET, JENIS_PENGADAAN, NAMA_PPK, NAMA_PENYEDIA").df()
            df_SIKAPTender_OK_filter_final = df_SIKAPTender_OK_filter.assign(KETERANGAN = np.where(df_SIKAPTender_OK_filter['SKOR_PENILAIAN'] >= 3, "SANGAT BAIK", np.where(df_SIKAPTender_OK_filter['SKOR_PENILAIAN'] >= 2, "BAIK", np.where(df_SIKAPTender_OK_filter['SKOR_PENILAIAN'] >= 1, "CUKUP", "BURUK"))))

            unduh_SIKAP_Tender_excel = download_excel(df_SIKAPTender_OK_filter_final)

            st.download_button(
                label = "📥 Download Data SIKAP Tender",
                data = unduh_SIKAP_Tender_excel,
                file_name = f"SIKAPTender-{kodeFolder}-{tahun}.xlsx",
                mime = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )        

            st.dataframe(
                df_SIKAPTender_OK_filter_final,
                column_config={
                    "NAMA_PAKET": "NAMA PAKET",
                    "KODE_PAKET": st.column_config.TextColumn("KODE PAKET"),
                    "JENIS_PENGADAAN": "JENIS PENGADAAN",
                    "NAMA_PPK": "NAMA PPK",
                    "NAMA_PENYEDIA": "NAMA PENYEDIA",
                    "SKOR_PENILAIAN": "SKOR",
                    "KETERANGAN": "KETERANGAN"
                },
                use_container_width=True,
                hide_index=True
            )

        except Exception:
            st.error("Gagal Analisa Penilaian SIKAP TENDER")

    ## Penilaian SIKAP NON TENDER
    with menu_monitoring_2_2:

        try:
            st.subheader("SIKAP NON TENDER")

            ### Baca file parquet SIKAP NON TENDER
            df_SPSENonTenderPengumuman = tarik_data_parquet(DatasetSPSENonTenderPengumuman)
            df_SIKAPNonTender = tarik_data_parquet(DatasetSIKAPNonTender)

            ### Query SIKAP NON TENDER
            df_SPSENonTenderPengumuman_filter = con.execute(f"SELECT kd_nontender, nama_satker, pagu, hps, jenis_pengadaan, mtd_pemilihan FROM df_SPSENonTenderPengumuman WHERE status_nontender = 'Selesai'").df()
            df_SIKAPNonTender_filter = con.execute(f"SELECT kd_nontender, nama_paket, nama_ppk, nama_penyedia, npwp_penyedia, indikator_penilaian, nilai_indikator, total_skors FROM df_SIKAPNonTender").df()
            df_SIKAPNonTender_OK = df_SPSENonTenderPengumuman_filter.merge(df_SIKAPNonTender_filter, how='right', on='kd_nontender')

            jumlah_trx_spse_nt_pengumuman = df_SPSENonTenderPengumuman_filter['kd_nontender'].unique().shape[0]
            jumlah_trx_sikap_nt = df_SIKAPNonTender_filter['kd_nontender'].unique().shape[0]
            selisih_sikap_nt = jumlah_trx_spse_nt_pengumuman - jumlah_trx_sikap_nt

            ### Tampilan SIKAP NON TENDER
            data_sikap_nt_1, data_sikap_nt_2, data_sikap_nt_3 = st.columns(3)
            data_sikap_nt_1.metric(label="Jumlah Paket Non Tender", value="{:,}".format(jumlah_trx_spse_nt_pengumuman))
            data_sikap_nt_2.metric(label="Jumlah Paket Sudah Dinilai", value="{:,}".format(jumlah_trx_sikap_nt))
            data_sikap_nt_3.metric(label="Jumlah Paket Belum Dinilai", value="{:,}".format(selisih_sikap_nt))

            st.divider()

            df_SIKAPNonTender_OK_filter = con.execute("SELECT nama_paket AS NAMA_PAKET, kd_nontender AS KODE_PAKET, jenis_pengadaan AS JENIS_PENGADAAN, nama_ppk AS NAMA_PPK, nama_penyedia AS NAMA_PENYEDIA, AVG(total_skors) AS SKOR_PENILAIAN FROM df_SIKAPNonTender_OK GROUP BY KODE_PAKET, NAMA_PAKET, JENIS_PENGADAAN, NAMA_PPK, NAMA_PENYEDIA").df()
            df_SIKAPNonTender_OK_filter_final = df_SIKAPNonTender_OK_filter.assign(KETERANGAN = np.where(df_SIKAPNonTender_OK_filter['SKOR_PENILAIAN'] >= 3, "SANGAT BAIK", np.where(df_SIKAPNonTender_OK_filter['SKOR_PENILAIAN'] >= 2, "BAIK", np.where(df_SIKAPNonTender_OK_filter['SKOR_PENILAIAN'] >= 1, "CUKUP", "BURUK"))))

            unduh_SIKAP_NonTender_excel = download_excel(df_SIKAPNonTender_OK_filter_final)

            st.download_button(
                label = "📥 Download Data SIKAP Non Tender",
                data = unduh_SIKAP_NonTender_excel,
                file_name = f"SIKAPNonTender-{kodeFolder}-{tahun}.xlsx",
                mime = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )        

            st.dataframe(
                df_SIKAPNonTender_OK_filter_final,
                column_config={
                    "NAMA_PAKET": "NAMA PAKET",
                    "KODE_PAKET": st.column_config.TextColumn("KODE PAKET"),
                    "JENIS_PENGADAAN": "JENIS PENGADAAN",
                    "NAMA_PPK": "NAMA PPK",
                    "NAMA_PENYEDIA": "NAMA PENYEDIA",
                    "SKOR_PENILAIAN": "SKOR",
                    "KETERANGAN": "KETERANGAN"
                },
                use_container_width=True,
                hide_index=True
            )

        except Exception:
            st.error("Gagal Analisa Penilaian SIKAP NON TENDER")


style_metric_cards(background_color="#000", border_left_color="#D3D3D3")