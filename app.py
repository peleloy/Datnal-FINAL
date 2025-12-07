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
st.markdown("Pilih model clustering (K-Means / DBSCAN) lalu lihat visualisasinya.")

# --- Sidebar: Upload File ---
st.sidebar.header("Unggah File Data")
uploaded_file = st.sidebar.file_uploader("Pilih file CSV gempa", type=['csv'])

df = pd.DataFrame()
if uploaded_file is not None:
    try:
        with st.spinner("Memuat dan memproses data..."):
            df = pd.read_csv(uploaded_file)

            # pastikan kolom cluster berbentuk string
            for col in ['cluster', 'dbscan_cluster']:
                if col in df.columns:
                    df[col] = df[col].fillna(-1).astype(int).astype(str)
                    df[col] = df[col].replace('-1', 'N/A')

    except Exception as e:
        st.error(f"Gagal memproses file. Error: {e}")
        st.stop()

# --- Jika CSV sudah dimuat ---
if not df.empty and all(col in df.columns for col in ['latitude', 'longitude']):

    # --- Sidebar: PILIH MODEL ---
    st.sidebar.header("Pengaturan Visualisasi")

    model_choice = st.sidebar.radio(
        "Pilih model clustering untuk divisualisasikan:",
        ["K-Means", "DBSCAN", "Bandingkan Keduanya"]
    )

    # Menentukan kolom cluster mana yang dipakai untuk warna map
    if model_choice == "K-Means":
        active_cluster_col = "cluster"
    elif model_choice == "DBSCAN":
        active_cluster_col = "dbscan_cluster"
    else:
        active_cluster_col = None  # nanti di-handle khusus

    # --- Sidebar: FILTER berdasar cluster ---
    if active_cluster_col is not None:
        cluster_options = ['Semua'] + sorted(df[active_cluster_col].unique().tolist())
        selected_cluster = st.sidebar.selectbox(
            f"Filter berdasarkan '{active_cluster_col}':",
            cluster_options
        )

        filtered_df = df.copy()
        if selected_cluster != 'Semua':
            filtered_df = filtered_df[filtered_df[active_cluster_col] == selected_cluster]

    else:
        # jika mode bandingkan, tidak ada filter cluster
        filtered_df = df.copy()
        st.sidebar.info("Mode bandingkan aktif — filter dinonaktifkan.")

    st.sidebar.markdown(f"**Jumlah Data Setelah Filter:** {len(filtered_df)}")
    st.sidebar.markdown(f"**Total Data Awal:** {len(df)}")

    # -------------------------------------------------------
    # 1. VISUALISASI MAP
    # -------------------------------------------------------
    st.header("1. Visualisasi Persebaran Gempa (Mapbox)")

    if model_choice == "Bandingkan Keduanya":
        # Layout 2 kolom: K-Means kiri, DBSCAN kanan
        col1, col2 = st.columns(2)

        # ---- K-Means Map ----
        with col1:
            if 'cluster' in df.columns:
                st.subheader("K-Means")
                fig_kmeans = px.scatter_mapbox(
                    df,
                    lat="latitude",
                    lon="longitude",
                    color="cluster",
                    zoom=3,
                    height=650,
                    mapbox_style="open-street-map",
                    title="K-Means Clustering"
                )
                fig_kmeans.update_layout(margin={"r":0,"t":30,"l":0,"b":0})
                st.plotly_chart(fig_kmeans, use_container_width=True)
            else:
                st.warning("Kolom 'cluster' tidak ditemukan.")

        # ---- DBSCAN Map ----
        with col2:
            if 'dbscan_cluster' in df.columns:
                st.subheader("DBSCAN")
                fig_db = px.scatter_mapbox(
                    df,
                    lat="latitude",
                    lon="longitude",
                    color="dbscan_cluster",
                    zoom=3,
                    height=650,
                    mapbox_style="open-street-map",
                    title="DBSCAN Clustering"
                )
                fig_db.update_layout(margin={"r":0,"t":30,"l":0,"b":0})
                st.plotly_chart(fig_db, use_container_width=True)
            else:
                st.warning("Kolom 'dbscan_cluster' tidak ditemukan.")

    else:
        # Mode normal: hanya 1 model
        fig_map = px.scatter_mapbox(
            filtered_df,
            lat="latitude",
            lon="longitude",
            color=active_cluster_col,
            zoom=3,
            height=800,
            mapbox_style="open-street-map",
            title=f"Distribusi Cluster Berdasarkan {model_choice}"
        )
        fig_map.update_layout(margin={"r":0,"t":30,"l":0,"b":0})
        st.plotly_chart(fig_map, use_container_width=True)

    # -------------------------------------------------------
    # 2. DISTRIBUSI CLUSTER
    # -------------------------------------------------------
    st.header("2. Distribusi Frekuensi Cluster")

    if model_choice == "Bandingkan Keduanya":
        colA, colB = st.columns(2)

        with colA:
            if "cluster" in df.columns:
                st.subheader("Distribusi K-Means")
                ccount = df['cluster'].value_counts().reset_index()
                ccount.columns = ['Cluster','Count']
                figA = px.bar(ccount, x='Cluster', y='Count', title="Bar Chart K-Means")
                st.plotly_chart(figA, use_container_width=True)

        with colB:
            if "dbscan_cluster" in df.columns:
                st.subheader("Distribusi DBSCAN")
                dcount = df['dbscan_cluster'].value_counts().reset_index()
                dcount.columns = ['DBSCAN','Count']
                figB = px.bar(dcount, x='DBSCAN', y='Count', title="Bar Chart DBSCAN")
                st.plotly_chart(figB, use_container_width=True)

    else:
        if active_cluster_col in df.columns:
            count = filtered_df[active_cluster_col].value_counts().reset_index()
            count.columns = ['Cluster','Count']
            fig_bar = px.bar(count, x='Cluster', y='Count',
                             title=f"Distribusi Cluster ({model_choice})")
            st.plotly_chart(fig_bar, use_container_width=True)

    # -------------------------------------------------------
    # 3. DATAFRAME
    # -------------------------------------------------------
    st.header("3. Data Mentah")
    st.dataframe(filtered_df)

else:
    st.info("Silakan unggah file CSV Anda di sidebar untuk menampilkan visualisasi.")
