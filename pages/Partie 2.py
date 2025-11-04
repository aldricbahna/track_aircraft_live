import streamlit as st
import pandas as pd
from utils import plot_trajet_avion, plot_tous_les_vols, haversine, plot_approches_aeroport, tracer_position_moyenne,charger_image_unsplash
import time
import folium
from streamlit_folium import st_folium

@st.cache_data
def load_data_air_france(): 
    return pd.read_pickle("data/AF_daily.dat")

@st.cache_data
def load_data_aeronefs(): 
    return pd.read_csv("data/aircraftDatabase-2022-06.csv")

df_af=load_data_air_france()
df_af['date'] = pd.to_datetime(df_af['time'], unit='s')
df_ae=load_data_aeronefs()
df_merge=pd.merge(df_af,df_ae[['icao24','manufacturername','manufacturericao','model','engines','serialnumber']],on='icao24',how='inner')
df_merge=df_merge.rename(columns={'lon':'longitude',
                             'lat':'latitude',
                             'onground':'on_ground'})
df_merge=df_merge.iloc[::30] # Important ! Pas de 30 pour alléger les données
onglet = st.sidebar.radio(
    "Choisir l'onglet",
    ["Air France", "Aéronefs", "Tracé d'un vol", "Tracé de tous les vols","Aéroport"],
)

if onglet=='Air France':
    st.dataframe(df_af)
    debut=time.time()
    min_date=df_af['date'].min()
    max_date=df_af['date'].max()
    delta=max_date-min_date
    fin=time.time()
    st.write(f"La plage horaire est de : (temps pris : {fin-debut:.2f}s)")
    st.write(delta)

    debut=time.time()
    vitesse_moyenne=df_af['velocity'].mean()
    fin=time.time()
    st.metric(f"Vitesse moyenne (temps pris : {fin-debut:.2f}s)",f"{vitesse_moyenne:.1f} m/s")

    df_af['hour']=df_af['date'].dt.hour
    debut=time.time()
    df_af_hour = df_af.groupby('hour')['icao24'].nunique().reset_index()
    df_af_hour = df_af_hour.rename(columns={'icao24':'amount'})
    st.subheader("Nombre d'avions par tranche horaire")
    st.line_chart(data=df_af_hour, x="hour", y="amount")
    fin=time.time()
    st.write(f"{fin-debut:.2f} secondes pour générer le graphique")

    st.subheader("Position moyenne des avions Air France")
    debut=time.time()
    fig_position_moyenne = tracer_position_moyenne(df_af)
    st.pyplot(fig_position_moyenne)
    fin=time.time()
    st.write(f"{fin-debut:.2f} secondes pour générer l'image")
    

elif onglet=='Aéronefs':
    st.subheader("Dataframe des aéronefs")
    st.dataframe(df_ae)

    nombre_aeronefs = df_ae['icao24'].nunique()
    nb_modeles = df_ae['model'].nunique()
    nb_fabricants = df_ae['manufacturername'].nunique()

  
    a, b, c = st.columns(3)

    with a:
        st.metric("Nombre total d'aéronefs", nombre_aeronefs)
    with b:
        st.metric("Nombre de modèles différents", nb_modeles)
    with c:
        st.metric("Nombre de fabricants différents", nb_fabricants)
 
    st.subheader("Top 5 des types d'appareils les plus représentés")
    st.write(df_ae['icaoaircrafttype'].value_counts().head(5))

    st.subheader("Compagnie la plus représentée")
    st.write(df_ae['manufacturername'].value_counts().head(1))

    st.header("Jointure des 2 Dataframes (Air France et aéronefs)")
    st.subheader("Une position toutes les 5 minutes (pour moins de lenteur)")
    st.dataframe(df_merge)

elif onglet=="Tracé d'un vol":
    vols = df_merge['icao24'].unique()
    index_defaut = list(vols).index("39cf0a")
    choix_vol=st.sidebar.selectbox("Choisissez un vol", df_merge['icao24'].unique(),index=index_defaut)
    df_vol=df_merge[df_merge['icao24']==choix_vol]
    st.write(f"Nombre de données manquantes pour la latitude :{df_vol['latitude'].isna().mean()*100:.1f}%")
    st.write(f"Nombre de données manquantes pour la longitude : {df_vol['longitude'].isna().mean()*100:.1f}%")
    df_vol=df_vol[(~df_vol['latitude'].isna())&(~df_vol['longitude'].isna())]
    df_vol=df_vol.reset_index(drop=True)
    st.subheader(f"Dataframe du {choix_vol}")
    st.dataframe(df_vol)

    a,b=st.columns(2)
    with a:
        debut=time.time()
        fig_trajet_avion=plot_trajet_avion(df_vol)
        st.pyplot(fig_trajet_avion, use_container_width=False)
        fin=time.time()
        st.write(f"{fin-debut:.1f} secondes pour charger le tracé")
    with b:
        debut=time.time()
        model = df_vol['model'].unique()[0]
        charger_image_unsplash(model, largeur_max=400)
        fin=time.time()
        st.write(f"{fin-debut:.1f} secondes pour charger l'image")
    
elif onglet=="Tracé de tous les vols":
    st.subheader("Tracé de tous les vols : patientez un tout petit peu")
    debut=time.time()
    fig2=plot_tous_les_vols(df_merge)
    st.pyplot(fig2)
    fin=time.time()
    st.write(f"{fin-debut:.1f} secondes pour charger l'image")




else:
    st.header("Utilisation de Streamlit Folium pour cette dernière partie (une vue plus dynamique)")
    df_ground = df_merge[df_merge["on_ground"] == True]
    # Pour chaque avion, on garde la première apparition au sol 
    df_airports = (
        df_ground.sort_values(["icao24", "time"])
                .groupby("icao24")
                .first()[["latitude", "longitude", "date"]]
                .reset_index()
    )
    df_airports=df_airports[~df_airports['latitude'].isna()]
    df_airports=df_airports.reset_index()
    st.subheader("Tous les aéroports accueillant des Air France (13 juin 22)")
    st.write("Il y a des doublons que l'on va supprimer")
    st.dataframe(df_airports)

    dict_aeroports={f"aeroport{i+1}":(df_airports.loc[i,'latitude'],df_airports.loc[i,'longitude']) for i in range(len(df_airports))}
   
    # Il y a certains doublons d'aéroports, on va garder une seule position par aéroport à l'aide de la formule de haversine
    dict_aero_clean = {}

    for name, (lat, lon) in dict_aeroports.items():
        already_found = False
        
        for keep_name, (keep_lat, keep_lon) in dict_aero_clean.items():
            if haversine(lat, lon, keep_lat, keep_lon) < 10:  # 10 km est un bon range
                already_found = True
                break
        
        if not already_found:
            dict_aero_clean[name] = (lat, lon)

    
    lat_center = sum([v[0] for v in dict_aero_clean.values()]) / len(dict_aero_clean)
    lon_center = sum([v[1] for v in dict_aero_clean.values()]) / len(dict_aero_clean)

    st.subheader("Tous les aéroports accueillant des Air France (13 juin 22)")
    m = folium.Map(location=[lat_center, lon_center], zoom_start=2)

    for name, (lat, lon) in dict_aero_clean.items():
        folium.Marker(
            location=[lat, lon],
            popup=name,
            icon=folium.Icon(icon="plane", prefix="fa")
        ).add_to(m)

    st_folium(m, width=800, height=600)





    aeroport_cdg="aeroport1"
    lat_aero, lon_aero = dict_aero_clean[aeroport_cdg]

    st.subheader("Avions arrivant à l'aéroport Charles de Gaulle")

    m = plot_approches_aeroport(df_merge, lat_aero, lon_aero, aeroport_cdg)
    st_folium(m, width=800, height=600)

    
  