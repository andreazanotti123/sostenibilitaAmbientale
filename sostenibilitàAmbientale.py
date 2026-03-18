import streamlit as st              # importa streamlit per creare l'interfaccia web
import pandas as pd                # importa pandas per gestire tabelle (DataFrame)
import matplotlib.pyplot as plt    # importa matplotlib per creare grafici
import json                        # serve per leggere file JSON
import os                          # serve per gestire percorsi dei file

st.set_page_config(page_title="Milano Air Dashboard", layout="wide")  # imposta titolo pagina e layout largo

st.title("Monitoraggio atmosferico Milano")  # titolo principale mostrato nella pagina

with st.sidebar:                  # crea barra laterale                 # crea barra laterale
    st.header("Glossario Inquinanti")
    with st.expander("Biossido di Azoto (NO₂)"):
        st.write("Gas prodotto principalmente dai motori a combustione (auto, camion).")
        st.write("È uno dei principali responsabili dello smog urbano.")
        st.write("Effetti: irrita le vie respiratorie e peggiora asma e bronchiti.")

    with st.expander("Monossido di Azoto (NO)"):
        st.write("Gas emesso direttamente dai motori e dagli impianti industriali.")
        st.write("Si trasforma facilmente in NO₂ nell'atmosfera.")
        st.write("Effetti: contribuisce alla formazione di altri inquinanti.")

    with st.expander("Ozono (O₃)"):
        st.write("Gas che si forma con la luce solare a partire da altri inquinanti.")
        st.write("È un inquinante secondario (non emesso direttamente).")
        st.write("Effetti: irrita occhi e polmoni, dannoso per piante e colture.")

    with st.expander("Biossido di Zolfo (SO₂)"):
        st.write("Deriva dalla combustione di carbone e petrolio.")
        st.write("Tipico delle industrie e centrali energetiche.")
        st.write("Effetti: causa irritazioni respiratorie e piogge acide.")

    with st.expander("Monossido di Carbonio (CO)"):
        st.write("Gas prodotto da combustioni incomplete (motori, stufe).")
        st.write("È incolore e inodore, quindi molto pericoloso.")
        st.write("Effetti: riduce il trasporto di ossigeno nel sangue.")

    with st.expander("Anidride Carbonica (CO₂)"):
        st.write("Gas prodotto dalla combustione di carburanti fossili e respirazione.")
        st.write("Non è tossico a basse concentrazioni.")
        st.write("Effetti: principale responsabile dell'effetto serra e cambiamento climatico.")

    with st.expander("Particolato fine (PM10)"):
        st.write("Particelle solide o liquide sospese nell'aria con diametro < 10 µm.")
        st.write("Provengono da traffico, industrie e polveri.")
        st.write("Effetti: entrano nei polmoni causando problemi respiratori.")

    with st.expander("Particolato ultrafine (PM2.5)"):
        st.write("Particelle ancora più piccole (< 2.5 µm).")
        st.write("Più pericolose perché penetrano in profondità nei polmoni.")
        st.write("Effetti: malattie respiratorie e cardiovascolari.")

    with st.expander("Benzene (C₆H₆)"):
        st.write("Composto organico volatile presente nei carburanti.")
        st.write("Deriva soprattutto dal traffico.")
        st.write("Effetti: sostanza cancerogena.")

    with st.expander("Ammoniaca (NH₃)"):
        st.write("Gas prodotto soprattutto da attività agricole e allevamenti.")
        st.write("Contribuisce alla formazione del particolato.")
        st.write("Effetti: irritazione occhi e vie respiratorie.")

    with st.expander("Solfati (SO₄²⁻)"):
        st.write("Derivano dalla trasformazione del biossido di zolfo.")
        st.write("Sono componenti del particolato atmosferico.")
        st.write("Effetti: contribuiscono allo smog e alle piogge acide.")

    with st.expander("Nitrati (NO₃⁻)"):
        st.write("Derivano dagli ossidi di azoto (NOx).")
        st.write("Sono parte del particolato fine.")
        st.write("Effetti: contribuiscono all'inquinamento atmosferico e allo smog.")    # testo semplice
            
def carica_dati():              # funzione per caricare i dati
    base = os.path.dirname(__file__)   # prende la cartella dove si trova il file .python

    # apertura file geojson
    with open(os.path.join(base, "qaria_stazione.geojson"), "r", encoding="utf8") as f:  
        geo = json.load(f)      # carica il contenuto JSON in un dizionario Python

    stazioni = []               # lista vuota dove salvare le stazioni
    for f in geo["features"]:   # ciclo for su tutte le stazioni nel file
        stazioni.append({       # aggiunge un dizionario alla lista
            "id": str(f["properties"]["id_amat"]),   # prende id e lo converte in stringa
            "nome": f["properties"]["nome"]          # prende il nome della stazione
        })

    dati = []                  # lista per tutti i dati
    for anno in range(2016, 2026):   # ciclo sugli anni dal 2016 al 2025
        path = os.path.join(base, f"{anno}_stazioni.json")  # crea il percorso del file
        if os.path.exists(path):     # controlla se il file esiste
            with open(path, "r", encoding="utf8") as f:
                dati += json.load(f)   # aggiunge i dati alla lista (+= concatena liste)

    df = pd.DataFrame(dati)    # crea DataFrame (tabella) dai dati

    df["data"] = pd.to_datetime(df["data"])   # converte colonna in formato data
    df["valore"] = pd.to_numeric(df["valore"], errors="coerce")  # converte numeri (errori → NaN)
    df["stazione_id"] = df["stazione_id"].astype(str)  # converte ID in stringa

    return df, pd.DataFrame(stazioni)   # restituisce dati e stazioni come DataFrame

df, stazioni = carica_dati()   # chiama la funzione e salva i risultati

# ---------------- ANALISI 1 ----------------
st.subheader("Dati per anno")   # sottotitolo

conteggio = df["data"].dt.year.value_counts().sort_index()  
# prende l'anno (.dt.year), conta quante righe per anno (value_counts), ordina (sort_index)

fig, ax = plt.subplots()       # crea figura e assi del grafico
conteggio.plot(kind="bar", ax=ax)   # grafico a barre
ax.set_ylabel("Numero rilevazioni") # etichetta asse Y

st.pyplot(fig)                 # mostra il grafico in streamlit

# ---------------- ANALISI 2 ----------------
st.subheader("Trend mensile")   # sottotitolo

anno = st.slider("Anno", 2016, 2025, 2025)   # slider per scegliere anno
gas = st.selectbox("Gas", df["inquinante"].unique())  
# selectbox = menu a tendina, unique() prende valori unici

filtro = df[(df["data"].dt.year == anno) & (df["inquinante"] == gas)]  
# filtra dati: anno scelto AND gas scelto

media_mensile = filtro.groupby(filtro["data"].dt.month)["valore"].mean()  
# groupby = raggruppa per mese, mean = media

fig2, ax2 = plt.subplots()    # crea grafico
media_mensile.plot(ax=ax2, marker="o")  # linea con punti
ax2.set_xlabel("Mese")        # etichetta asse X
ax2.set_ylabel("Valore medio")# etichetta asse Y

st.pyplot(fig2)               # mostra grafico

# ---------------- ANALISI 3 ----------------
st.subheader("Classifica stazioni")  # sottotitolo

df_merge = pd.merge(df, stazioni, left_on="stazione_id", right_on="id")  
# merge = unisce due tabelle usando colonne in comune

gas_scelto = st.selectbox("Scegli gas", df_merge["inquinante"].unique())  

ranking = df_merge[df_merge["inquinante"] == gas_scelto] \
            .groupby("nome")["valore"].mean() \
            .sort_values()  
# filtra gas → raggruppa per stazione → fa media → ordina

fig3, ax3 = plt.subplots()   # crea grafico
ranking.plot(kind="barh", ax=ax3)   # grafico orizzontale

st.pyplot(fig3)              # mostra grafico

# ---------------- ANALISI 4 ----------------
st.subheader("Dettaglio stazione")  # sottotitolo

stazione = st.selectbox("Seleziona stazione", df_merge["nome"].unique())  
# scelta stazione

df_staz = df_merge[df_merge["nome"] == stazione]  
# filtro per stazione

gas_staz = st.selectbox("Gas", df_staz["inquinante"].unique())  
# scelta gas

df_finale = df_staz[df_staz["inquinante"] == gas_staz]  
# filtro finale

media = df_finale.groupby(df_finale["data"].dt.month)["valore"].mean()  
# media mensile

fig4, ax4 = plt.subplots()   # crea grafico
media.plot(kind="bar", ax=ax4)  # grafico a barre

st.pyplot(fig4)              # mostra grafico
