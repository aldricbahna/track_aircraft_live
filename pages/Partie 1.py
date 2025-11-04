import streamlit as st
import pandas as pd
from avion import Avion
from utils import plot_avions
import plotly.express as px


df=pd.read_parquet('data/df_states.parquet')
df['date'] = pd.to_datetime(df['time_position'], unit='s')

onglet = st.sidebar.radio(
    "Choisir l'onglet",
    ["Statistiques globales", "Carte avec tous les avions"],
)

if onglet=='Statistiques globales':
    st.subheader("states.pkl sous forme de dataframe (18/10/2025 à 11h50)")
    st.dataframe(df)


    nombre_avions=df['icao24'].nunique()
    nb_pays_origine=df['origin_country'].nunique()
    nb_avions_sol_transpondeur_allume=df[(df['on_ground']==1) & (df['squawk']!=None)].shape[0]

    au_sol=(df['on_ground'].value_counts(normalize=True).iloc[1]*100).round(1)
    taux_de_montee=df['vertical_rate'].mean()
    carre=(df['latitude']<=51)&(df['latitude']>=42)&(df['longitude']<=8)&(df['longitude']>=-5)
    vitesse_moyenne_carre=df[carre]['velocity'].mean()

    fig_velocity=px.histogram(df,x='velocity')
    fig_vertical_rate=px.histogram(df,x='vertical_rate')
    fig_baro_altitude=px.histogram(df,x='baro_altitude')


    a,b,c=st.columns(3)
    with a:
        st.metric("Nombre d'avions volant en ce moment dans le monde",nombre_avions)
        st.metric("Proportion d'avions au sol",f"{au_sol}%")
        st.plotly_chart(fig_velocity)
    with b: 
        st.metric("Nombre de pays d'origine",nb_pays_origine)
        st.metric("Taux de montée moyen",f"{taux_de_montee:.2f} m/s")
        st.plotly_chart(fig_vertical_rate)
    with c:
        st.metric("Nombre d'avions au sol avec le transpondeur allumé",nb_avions_sol_transpondeur_allume)
        st.metric("Vitesse moyenne des avions dans le carré métropolitain",f"{vitesse_moyenne_carre:.1f} m/s")
        st.plotly_chart(fig_baro_altitude)
else:
    carre=(df['latitude']<=51)&(df['latitude']>=42)&(df['longitude']<=8)&(df['longitude']>=-5)
    df_france=df[carre]

    st.subheader("Dataframe des avions en France")
    st.dataframe(df_france)

    st.write("Ouvrir l'image à l'aide du petit bouton en haut à droite")

    liste_france=[]
    for i in range(0,len(df_france)):
        liste_france.append(Avion.from_dict(df_france.iloc[i]))

    @st.cache_data
    def load_plot_avions():
        fig_carte=plot_avions(liste_france)
        return fig_carte

    fig_carte=load_plot_avions()
    st.pyplot(fig_carte, use_container_width=False)


