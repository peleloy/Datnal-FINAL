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

# --- Sidebar: Upload File ---
st.sidebar.header("Unggah File Data")
uploaded_file = st.sidebar.file_uploader("Pilih file CSV gempa Anda", type=['csv'])

df = pd.DataFrame()
if uploaded_file:
    try:
        with st.spinner("Memuat data..."):
            df = pd.read_csv(uploaded_file)

            # Normalisasi kolom cluster menjadi string
            for col in ['cluster', 'dbscan_cluster']:
                if col in df.columns:
                    df[col] = df[col].fillna(-1).astype(int).astype(str)
                    df[col] = df[col].replace('-1', 'N/A')

    except Exception as e:
        st.error(f"Error membaca file CSV: {e}")
        st.stop()

# Jika data valid
if not df.empty and all(c in df.columns for c in ['latitude', 'longitude']):

    # --------------------------------------------------------
    # --- PILIHAN MODEL VISUALISASI ---
    # --------------------------------------------------------
    st.sidebar.header("Model Visualisasi")
    view_model = st.sidebar.radio(
        "Tampilkan Scatter Berdasarkan:",
        ["K-Means", "DBSCAN"]
    )

    # Pilih warna berdasarkan model
    if view_model == "K-Means":
        color_col = "cluster"
    else:
        color_col = "dbscan_cluster"

    # --------------------------------------------------------
    # --- SCATTER LAT-LONG ---
    # --------------------------------------------------------
    st.header(f"1. Scatter Plot Berdasarkan {view_model}")

    fig = px.scatter(
        df,
        x="longitude",
        y="latitude",
        color=color_col,
        hover_data=["latitude", "longitude", "cluster", "dbscan_cluster"],
        height=700,
        title=f"Scatter Plot Gempa Berdasarkan {view_model}"
    )

    fig.update_layout(
        xaxis_title="Longitude",
        yaxis_title="Latitude",
        margin={"r":0,"t":40,"l":0,"b":0}
    )

    st.plotly_chart(fig, use_container_width=True)

    # --------------------------------------------------------
    # --- DISTRIBUSI CLUSTER ---
    # --------------------------------------------------------
    st.header("2. Distribusi Frekuensi Cluster")

    col1, col2 = st.columns(2)

    with col1:
        if 'cluster' in df.columns:
            st.subheader("Distribusi K-Means")
            c1 = df['cluster'].value_counts().reset_index()
            c1.columns = ['Cluster', 'Count']
            st.plotly_chart(
                px.bar(c1, x='Cluster', y='Count', title="Distribusi Cluster K-Means"),
                use_container_width=True
            )

    with col2:
        if 'dbscan_cluster' in df.columns:
            st.subheader("Distribusi DBSCAN")
            c2 = df['dbscan_cluster'].value_counts().reset_index()
            c2.columns = ['DBSCAN Cluster', 'Count']
            st.plotly_chart(
                px.bar(c2, x='DBSCAN Cluster', y='Count', title="Distribusi Cluster DBSCAN"),
                use_container_width=True
            )

    # --------------------------------------------------------
    # --- DATA TABEL ---
    # --------------------------------------------------------
    st.header("3. Data Mentah")
    st.dataframe(df)

else:
    st.info("Silakan unggah file CSV untuk menampilkan visualisasi.")
