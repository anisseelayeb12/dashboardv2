import streamlit as st
import pandas as pd
import plotly.express as px
from app import load_data, process_data, load_velib_data


df_full = load_velib_data()
df = process_data(df_full)

if 'selected_commune' in st.session_state and st.session_state['selected_commune'] != "Toutes":
    df = df[df['Commune'] == st.session_state['selected_commune']]

st.title("📊 Analyse & Jauges")

if not df.empty:
    col_g1, col_g2 = st.columns(2)
    
    with col_g1:
        st.subheader("Top 10 Stations les mieux approvisionnées")
        top_stations = df.nlargest(10, 'Vélos_Dispo')
        
        fig_bar = px.bar(
            top_stations,
            x='Vélos_Dispo',
            y='Station',
            orientation='h',
            title="Nombre de vélos disponibles",
            color='Vélos_Dispo',
            color_continuous_scale='Viridis'
        )
        fig_bar.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_bar, use_container_width=True)
        
    with col_g2:
        st.subheader("Répartition Élec vs Méca")
        if 'Vélos_Méca' in df.columns and 'Vélos_Elec' in df.columns:
            total_meca = df['Vélos_Méca'].sum()
            total_elec = df['Vélos_Elec'].sum()
            
            df_pie = pd.DataFrame({
                'Type': ['Mécanique', 'Électrique'],
                'Nombre': [total_meca, total_elec]
            })
            
            fig_pie = px.pie(
                df_pie,
                values='Nombre',
                names='Type',
                title="Proportion du parc (sur l'échantillon)",
                color_discrete_sequence=['#3498db', '#f1c40f'] # Bleu et Jaune
            )
            st.plotly_chart(fig_pie, use_container_width=True)
else:
    st.warning("Aucune donnée à afficher pour cette sélection.")
