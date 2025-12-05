import streamlit as st
import pandas as pd
import plotly.express as px
import requests

# Configuration de la page
st.set_page_config(
    page_title="Vélib' Métropole - Temps Réel",
    page_icon="🚲",
    layout="wide",
    initial_sidebar_state="expanded" # Assurer que la sidebar est visible pour les pages
)

# --- 1. CHARGEMENT DES DONNÉES (API OPEN DATA PARIS) ---

@st.cache_data(ttl=60)
def load_velib_data():
    """Récupère les données temps réel des stations Vélib'."""
    url = "https://opendata.paris.fr/api/explore/v2.1/catalog/datasets/velib-disponibilite-en-temps-reel/records?limit=100"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        results = data.get('results', [])
        df = pd.json_normalize(results)
        return df
        
    except Exception as e:
        st.error(f"Erreur de connexion à l'API Vélib' : {e}")
        return pd.DataFrame()

def process_data(df):
    """Nettoie et prépare les données pour l'analyse."""
    if df.empty:
        return df

    cols_to_keep = {
        'name': 'Station',
        'capacity': 'Capacité_Totale',
        'numbikesavailable': 'Vélos_Dispo',
        'numdocksavailable': 'Bornes_Libres',
        'ebike': 'Vélos_Elec',
        'mechanical': 'Vélos_Méca',
        'coordonnees_geo.lon': 'lon',
        'coordonnees_geo.lat': 'lat',
        'nom_arrondissement_communes': 'Commune'
    }
    
    existing_cols = [c for c in cols_to_keep.keys() if c in df.columns]
    df = df[existing_cols].rename(columns=cols_to_keep)
    
    # Calcul du taux de remplissage (%)
    df['Taux_Remplissage'] = df.apply(
        lambda x: (x['Vélos_Dispo'] / x['Capacité_Totale'] * 100) if x['Capacité_Totale'] > 0 else 0,
        axis=1
    )
    
    return df

# La fonction load_data (utilisée par les pages) retourne le DF complet 
# car le filtrage est appliqué directement dans chaque page.
load_data = load_velib_data 


# --- 2. INTERFACE UTILISATEUR (Page d'Accueil) ---

def main():
    st.title("🚲 Monitor Vélib' Métropole - Temps Réel")
    st.markdown("""
    Cette page d'accueil affiche les indicateurs clés de performance (KPI) sur l'échantillon de données temps réel.
    **Utilisez le menu latéral pour naviguer vers les analyses détaillées.**
    """)
    st.markdown("---")

    # Bouton de rafraîchissement
    if st.button("🔄 Actualiser les données"):
        st.cache_data.clear()
        # Nécessaire pour forcer le rechargement de la sidebar
        st.rerun()

    # Chargement
    with st.spinner('Connexion à OpenData Paris...'):
        raw_df = load_velib_data()
        df = process_data(raw_df)

    if df.empty:
        st.warning("Aucune donnée récupérée. L'API est peut-être inaccessible momentanément.")
        return

    # --- Filtres (Placés dans la Sidebar pour un accès constant) ---
    st.sidebar.header("🎛️ Filtres Communs")
    
    # Initialisation de l'état
    if 'selected_commune' not in st.session_state:
        st.session_state['selected_commune'] = "Toutes"
    
    # Filtre Commune
    df_all = process_data(load_velib_data()) # Utiliser le DF complet pour la liste des communes
    if 'Commune' in df_all.columns:
        communes = sorted(df_all['Commune'].dropna().unique())
        selected_commune = st.sidebar.selectbox(
            "Filtrer par Commune / Arrondissement", 
            ["Toutes"] + communes,
            key='sb_commune'
        )
        # Mise à jour de l'état de session pour que les pages y aient accès
        st.session_state['selected_commune'] = selected_commune

    # --- KPI (Indicateurs Clés) ---
    # Application du filtre à la DataFrame pour calculer les KPIs
    df_kpi = df
    if st.session_state['selected_commune'] != "Toutes":
        df_kpi = df[df['Commune'] == st.session_state['selected_commune']]
        st.subheader(f"KPI pour : {st.session_state['selected_commune']}")
    else:
        st.subheader("KPI Global")


    if df_kpi.empty:
        st.warning(f"Aucune station trouvée pour {st.session_state['selected_commune']}.")
        return


    col1, col2, col3, col4 = st.columns(4)
    
    total_velos = df_kpi['Vélos_Dispo'].sum()
    total_elec = df_kpi['Vélos_Elec'].sum() if 'Vélos_Elec' in df_kpi.columns else 0
    stations_vides = df_kpi[df_kpi['Vélos_Dispo'] == 0].shape[0]
    stations_pleines = df_kpi[df_kpi['Bornes_Libres'] == 0].shape[0]

    col1.metric("Vélos Dispo", total_velos)
    col2.metric("Dont Électriques ⚡", total_elec)
    col3.metric("Stations Vides ❌", stations_vides, delta_color="inverse")
    col4.metric("Stations Pleines ⚠️", stations_pleines, delta_color="inverse")

    st.markdown("---")
    
    st.info("Utilisez le **menu de navigation (en haut à gauche)** pour voir la carte et les graphiques détaillés.")

if __name__ == "__main__":
    main()