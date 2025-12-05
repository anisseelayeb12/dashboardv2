import streamlit as st
from app import load_data, process_data, load_velib_data


df_full = load_velib_data()
df = process_data(df_full)


if 'selected_commune' in st.session_state and st.session_state['selected_commune'] != "Toutes":
    df = df[df['Commune'] == st.session_state['selected_commune']]

st.title("🗺️ Carte de Localisation des Stations")

if not df.empty and 'lat' in df.columns and 'lon' in df.columns:
    st.subheader("Localisation des stations")
    st.map(df, latitude='lat', longitude='lon', size='Vélos_Dispo', color='#00AA00')
else:
    st.info("Pas de données géographiques disponibles pour cette sélection.")
