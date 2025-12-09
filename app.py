import streamlit as st
import pandas as pd
import plotly.express as px

# Konfigurasi halaman
st.set_page_config(
    page_title="Visualisasi Data Gempa Bumi",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Judul Aplikasi ---
st.title("Visualisasi Data Gempa Bumi 🌍")
st.markdown("Visualisasi hanya menggunakan data lokasi (`latitude`, `longitude`) dan hasil clustering (`cluster`, `dbscan_cluster`).")

# --- Sidebar untuk Unggah File ---
st.sidebar.header("Unggah File Data")
uploaded_file = st.sidebar.file_uploader("Pilih file CSV gempa Anda", type=['csv'])

df = pd.DataFrame()
if uploaded_file:
    try:
        with st.spinner("Memuat data..."):
            df = pd.read_csv(uploaded_file)

            # Normalisasi kolom cluster → string
            for col in ['cluster', 'dbscan_cluster']:
                if col in df.columns:
                    df[col] = df[col].fillna(-1).astype(int).astype(str)
                    df[col] = df[col].replace("-1", "N/A")

    except Exception as e:
        st.error(f"Error membaca file CSV: {e}")
        st.stop()

# Jika data siap
if not df.empty and all(col in df.columns for col in ['latitude', 'longitude']):

    # ------------------------------------------------------
    # --- OPSI PILIH MODEL VISUALISASI ---
    # ------------------------------------------------------
    st.sidebar.header("Pilih Model Visualisasi")
    view_model = st.sidebar.radio(
        "Tampilkan Scatter Berdasarkan:",
        ["Semua Model", "K-Means", "DBSCAN"]
    )

    # Warna scatter tergantung model
    if view_model == "K-Means":
        color_col = "cluster"
    elif view_model == "DBSCAN":
        color_col = "dbscan_cluster"
    else:
        # default gabungan → pakai DBSCAN (lebih informatif)
        color_col = "dbscan_cluster"

    # ------------------------------------------------------
    # --- SCATTER LAT-LONG ---
    # ------------------------------------------------------
    st.header("1. Visualisasi Scatter Berdasarkan Pilihan Model")

    fig = px.scatter(
        df,
        x="longitude",
        y="latitude",
        color=color_col,
        hover_data=["latitude", "longitude", "cluster", "dbscan_cluster"],
        height=700,
        title=f"Scatter Plot Berdasarkan Model: {view_model}"
    )

    fig.update_layout(
        xaxis_title="Longitude",
        yaxis_title="Latitude",
        margin={"r":0, "t":40, "l":0, "b":0}
    )

    st.plotly_chart(fig, use_container_width=True)

    # ------------------------------------------------------
    # --- DISTRIBUSI CLUSTER ---
    # ------------------------------------------------------
    st.header("2. Distribusi Cluster")

    col1, col2 = st.columns(2)

    with col1:
        if "cluster" in df.columns:
            st.subheader("K-Means")
            count_k = df["cluster"].value_counts().reset_index()
            count_k.columns = ["Cluster", "Count"]

            fig_k = px.bar(count_k, x="Cluster", y="Count",
                           title="Distribusi Cluster K-Means")
            st.plotly_chart(fig_k, use_container_width=True)

    with col2:
        if "dbscan_cluster" in df.columns:
            st.subheader("DBSCAN")
            count_d = df["dbscan_cluster"].value_counts().reset_index()
            count_d.columns = ["DBSCAN Cluster", "Count"]

            fig_d = px.bar(count_d, x="DBSCAN Cluster", y="Count",
                           title="Distribusi Cluster DBSCAN")
            st.plotly_chart(fig_d, use_container_width=True)

    # ------------------------------------------------------
    # --- TABEL DATA ---
    # ------------------------------------------------------
    st.header("3. Data Mentah")
    st.dataframe(df)

else:
    st.info("Silakan unggah file CSV untuk menampilkan visualisasi.")
