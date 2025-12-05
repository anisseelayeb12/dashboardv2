import streamlit as st
from app import load_data, process_data, load_velib_data

df_full = load_velib_data()
df = process_data(df_full)

if 'selected_commune' in st.session_state and st.session_state['selected_commune'] != "Toutes":
    df = df[df['Commune'] == st.session_state['selected_commune']]

st.title("📄 Données Brutes Détaillées")

if not df.empty:
    st.subheader(f"Stations affichées : {df.shape[0]}")
    st.dataframe(df, use_container_width=True)
else:
    st.warning("Aucune donnée à afficher pour cette sélection.")
