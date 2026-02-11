import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import json
import os


st.set_page_config(page_title="Milano Air Dashboard", layout="wide", initial_sidebar_state="expanded")


st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stTitle { color: #00ffc8; font-family: 'Courier New', monospace; text-align: center; border-bottom: 2px solid #00ffc8; }
    h3 { color: #00d4ff !important; }
    </style>
    """, unsafe_allow_html=True)

st.title(" MONITORAGGIO ATMOSFERICO: MILANO")


with st.sidebar:
    st.header("Glossario Inquinanti")
    info_dict = {
        "Biossido di Azoto (NO2)": "Generato dai motori termici. Infiamma le vie aeree e favorisce lo smog.",
        "Ozono (O3)": "Gas instabile e reattivo. Irrita i polmoni e danneggia la vegetazione urbana.",
        "Biossido di Zolfo (SO2)": "Deriva da combustibili fossili pesanti. Causa piogge acide e irritazioni bronchiali."
    }
    for gas, desc in info_dict.items():
        with st.expander(gas):
            st.caption(desc)


base_path = os.path.dirname(_file_)

@st.cache_data
def load_environmental_data():
    
    file_stazioni = os.path.join(base_path, "qaria_stazione.geojson")
    with open(file_stazioni, "r", encoding="utf8") as f:
        geo_data = json.load(f)
    
    stazioni_list = []
    for feat in geo_data["features"]:
        stazioni_list.append({
            "id": str(feat["properties"]["id_amat"]),
            "nome": feat["properties"]["nome"],
            "coords": feat["geometry"]["coordinates"]
        })
    
    
    records = []
    for yr in range(2016, 2026):
        path = os.path.join(base_path, f"{yr}_stazioni.json")
        if os.path.exists(path):
            with open(path, "r", encoding="utf8") as f:
                records.extend(json.load(f))
    
    df = pd.DataFrame(records)
    df['data'] = pd.to_datetime(df['data'])
    df['valore'] = pd.to_numeric(df['valore'], errors='coerce')
    df['stazione_id'] = df['stazione_id'].astype(str)
    return df, pd.DataFrame(stazioni_list)

df_main, df_geo = load_environmental_data()


st.subheader(" Analisi Quantitativa del Database")
if not df_main.empty:
    fig1, ax1 = plt.subplots(figsize=(12, 4))
    
    plt.style.use('dark_background')
    
    count_data = df_main['data'].dt.year.value_counts().sort_index()
    count_data.plot(kind='bar', color='#00ffc8', ax=ax1, edgecolor='white')
    
    ax1.set_title("Volume campionamenti per anno", pad=20)
    ax1.set_ylabel("N. Record")
    st.pyplot(fig1)

st.divider()


col_ctrl1, col_ctrl2 = st.columns([1, 2])
with col_ctrl1:
    target_year = st.select_slider("Seleziona Periodo", options=list(range(2016, 2026)), value=2025)
with col_ctrl2:
    target_gas = st.selectbox("Inquinante target", df_main['inquinante'].unique())

st.subheader(f" Trend Mensile: {target_gas} ({target_year})")

df_filtered = df_main[(df_main['data'].dt.year == target_year) & (df_main['inquinante'] == target_gas)]
monthly_avg = df_filtered.groupby(df_filtered['data'].dt.month)['valore'].mean()

if not monthly_avg.empty:
    fig2, ax2 = plt.subplots(figsize=(10, 4))
    ax2.fill_between(monthly_avg.index, monthly_avg.values, color='#00d4ff', alpha=0.3)
    ax2.plot(monthly_avg.index, monthly_avg.values, marker='h', ls='--', lw=2, color='#00d4ff')
    
    ax2.set_xticks(range(1, 13))
    ax2.set_xticklabels(['G', 'F', 'M', 'A', 'M', 'G', 'L', 'A', 'S', 'O', 'N', 'D'])
    ax2.grid(axis='y', alpha=0.2)
    st.pyplot(fig2)
else:
    st.warning("Dati non pervenuti per questa selezione.")

st.divider()


st.subheader(" Classifica Criticità per Stazione (Media 2016-2025)")


df_merged = pd.merge(df_main, df_geo, left_on='stazione_id', right_on='id')

gas_rank = st.radio("Scegli parametro di confronto:", df_merged['inquinante'].unique(), horizontal=True)

ranking = df_merged[df_merged['inquinante'] == gas_rank].groupby('nome')['valore'].mean().sort_values()

c1, c2 = st.columns([2, 1])
with c1:
    fig3, ax3 = plt.subplots(figsize=(10, 6))
    colors = plt.cm.viridis(np.linspace(0, 1, len(ranking)))
    ranking.plot(kind='barh', color=colors, ax=ax3)
    ax3.set_xlabel("µg/m³ (Media Storica)")
    st.pyplot(fig3)
with c2:
    st.dataframe(ranking.rename("Media").to_frame(), use_container_width=True)

st.divider()


latest_yr = int(df_main['data'].dt.year.max())
st.subheader(f" Deep Dive {latest_yr}: Focus Località")

localita = st.selectbox("Seleziona Punto di Rilevazione:", sorted(df_merged['nome'].unique()))
gas_localita = st.segmented_control("Vettore:", sorted(df_merged[df_merged['nome'] == localita]['inquinante'].unique()))

if gas_localita:
    data_focus = df_merged[(df_merged['nome'] == localita) & 
                           (df_merged['inquinante'] == gas_localita) & 
                           (df_merged['data'].dt.year == latest_yr)]
    
    res_mensile = data_focus.groupby(data_focus['data'].dt.month)['valore'].mean()
    
    if not res_mensile.empty:
        fig4, ax4 = plt.subplots(figsize=(12, 4))
        sns.barplot(x=res_mensile.index, y=res_mensile.values, palette="flare", ax=ax4)
        
        
        max_val = res_mensile.max()
        max_idx = res_mensile.idxmax()
        ax4.annotate(f'PICCO: {max_val:.2f}', xy=(max_idx-1, max_val), xytext=(max_idx-1, max_val+5),
                     arrowprops=dict(facecolor='white', shrink=0.05))
        
        ax4.set_title(f"Profilo annuale {gas_localita} - Stazione {localita}")
        st.pyplot(fig4)

st.caption("Dati estratti dal dataset AMAT Milano. Elaborazione automatica.")