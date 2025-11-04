import pickle
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.markers import MarkerStyle
from matplotlib.colors import Normalize
from matplotlib.textpath import TextPath
from matplotlib.transforms import Affine2D
import cartopy.crs as ccrs
import cartopy.io.img_tiles as cimgt
import cartopy.feature as cf
import numpy as np
import math 
import streamlit as st
from PIL import Image
from io import BytesIO
import requests
from dotenv import load_dotenv
import os
import folium


def plot_avions(liste_avion, *args, **kwargs):
    """Affiche les avions sur une carte avec rotation selon direction et couleur selon vitesse.
    
    Arguments:
    liste_avion -- liste d'objets Avion avec attributs longitude, latitude, velocity, true_track, on_ground, callsign
    show_callsign -- (kwarg bool) afficher les indicatifs (défaut: False)
    show_ground -- (kwarg bool) afficher les avions au sol (défaut: False)
    
    Retourne:
    figure matplotlib
    """
    fig = plt.figure(figsize=(6, 6))
    
    stamen_terrain = cimgt.GoogleTiles("RGB")
    ax = fig.add_subplot(1, 1, 1, projection=stamen_terrain.crs)
    ax.set_extent([-5, 8, 42, 51], crs=ccrs.Geodetic())
    ax.add_image(cimgt.GoogleTiles("RGB"), 8)
    
    SYMBOL = TextPath((0, 0), "✈")
    
    show_callsign = kwargs.get('show_callsign', False)
    show_ground = kwargs.get('show_ground', False)
    
    avions_valides = []
    for avion in liste_avion:
        if avion.longitude is None or avion.latitude is None:
            continue
        if not show_ground and avion.on_ground:
            continue
        avions_valides.append(avion)
    
    if not avions_valides:
        print("Aucun avion à afficher")
        return
    
    vitesses = [a.velocity for a in avions_valides]
    if len(vitesses) > 0 and max(vitesses) > 0:
        norm = Normalize(vmin=min(vitesses), vmax=max(vitesses))
        cmap = plt.cm.cividis  
    else:
        norm = None
        cmap = None
    
    for avion in avions_valides:
        angle_rotation = 90 - avion.true_track
        
        t = Affine2D().rotate_deg(angle_rotation).scale(0.08)
        marker = MarkerStyle(SYMBOL)
        marker._transform = t
        
        if cmap and norm:
            couleur = cmap(norm(avion.velocity))
        else:
            couleur = 'red'
        
        if avion.on_ground:
            couleur = 'gray'
        
        ax.plot(
            avion.longitude,
            avion.latitude,
            marker=marker,
            color=couleur,
            markersize=20,
            transform=ccrs.PlateCarree(),
            markeredgecolor='white',
            markeredgewidth=0.8,
            zorder=10
        )
        
        if show_callsign and avion.callsign and avion.callsign != "N/A":
            ax.text(
                avion.longitude + 0.15,
                avion.latitude + 0.15,
                avion.callsign,
                fontsize=7,
                transform=ccrs.PlateCarree(),
                color="black",
                bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.7),
                zorder=11
            )
    
    if cmap and norm:
        sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
        sm.set_array([])
        cbar = plt.colorbar(sm, ax=ax, orientation='horizontal', 
                           pad=0.05, shrink=0.7, aspect=30)
        cbar.set_label('Vitesse (m/s)', fontsize=12)
    
    nb_vol = sum(1 for a in avions_valides if not a.on_ground)
    nb_sol = sum(1 for a in avions_valides if a.on_ground)
    
    titre = f'Trafic aérien - {nb_vol} avions en vol'
    if show_ground:
        titre += f', {nb_sol} au sol'
    ax.set_title(titre, fontsize=16, fontweight='bold', pad=20)
    
    return fig


def tracer_position_moyenne(df_af):
    """Trace les positions des vols et leur centre géographique moyen.
    
    Arguments:
    df_af -- DataFrame avec colonnes 'lat' et 'lon'
    
    Retourne:
    figure matplotlib
    """
    lat_moyenne = df_af['lat'].mean()
    lon_moyenne = df_af['lon'].mean()

    fig = plt.figure(figsize=(10, 8))
    ax = plt.axes(projection=ccrs.PlateCarree())

    ax.add_feature(cf.COASTLINE)
    ax.add_feature(cf.BORDERS, linestyle=':')
    ax.add_feature(cf.LAND)
    ax.add_feature(cf.OCEAN)
    ax.add_feature(cf.LAKES, alpha=0.5)
    ax.add_feature(cf.RIVERS)

    ax.scatter(df_af['lon'], df_af['lat'], s=20, marker='o', transform=ccrs.PlateCarree(), label="Vols")
    ax.scatter(lon_moyenne, lat_moyenne, s=100, color='red', marker='x',
            transform=ccrs.PlateCarree(), label="Position moyenne")

    ax.legend()

    ax.set_extent([
        df_af['lon'].min() - 1, df_af['lon'].max() + 1,
        df_af['lat'].min() - 1, df_af['lat'].max() + 1
    ])
    return fig


def plot_trajet_avion(df_vol):
    """Trace la trajectoire d'un avion unique avec dégradé de couleurs.
    
    Arguments:
    df_vol -- DataFrame avec colonnes 'longitude', 'latitude', 'manufacturericao', 'icao24', 'model'
    
    Retourne:
    figure matplotlib
    """
    long_min = df_vol['longitude'].min()
    long_max = df_vol['longitude'].max()
    lat_min = df_vol['latitude'].min()
    lat_max = df_vol['latitude'].max()

    fig = plt.figure(figsize=(6,6), dpi=100)

    tile = cimgt.GoogleTiles("RGB")
    ax = fig.add_subplot(1, 1, 1, projection=tile.crs)
    window = [long_min-5, long_max+5, lat_min-1, lat_max+1]
    ax.set_extent(window, crs=ccrs.Geodetic())

    ax.add_image(tile, 6)
    ax.add_feature(cf.BORDERS)
    ax.add_feature(cf.STATES)
    ax.add_feature(cf.COASTLINE)
    ax.set_title(f"{df_vol['manufacturericao'].unique()[0]}: {df_vol['icao24'].unique()[0]}, model {df_vol['model'].unique()[0]}")

    cmap = plt.cm.get_cmap('jet')
    for i in range(0, len(df_vol)):
        x = df_vol.loc[i, 'longitude']
        y = df_vol.loc[i, 'latitude']
        ax.scatter(x, y, color=cmap(i / len(df_vol)), s=30, transform=ccrs.Geodetic())
    return fig  

def plot_tous_les_vols(df):
    """Trace tous les vols d'une journée sur une seule carte.
    
    Arguments:
    df -- DataFrame avec colonnes 'longitude', 'latitude', 'icao24', 'date'
    
    Retourne:
    figure matplotlib
    """
    long_min = df['longitude'].min()
    long_max = df['longitude'].max()
    lat_min = df['latitude'].min()
    lat_max = df['latitude'].max()

    fig = plt.figure(figsize=(12, 12), dpi=100)
    tile = cimgt.GoogleTiles("RGB")
    ax2 = fig.add_subplot(1, 1, 1, projection=tile.crs)
    ax2.set_extent([long_min-5, long_max+5, lat_min-1, lat_max+1], crs=ccrs.Geodetic())
    ax2.add_image(tile, 6)
    ax2.add_feature(cf.BORDERS)
    ax2.add_feature(cf.STATES)
    ax2.add_feature(cf.COASTLINE)
    ax2.set_title(f"Tous les vols du {df['date'].dt.day.iloc[0]}/{df['date'].dt.month.iloc[0]}/{df['date'].dt.year.iloc[0]}")

    vol_ids = df['icao24'].unique()
    cmap = plt.cm.get_cmap('tab20', len(vol_ids))

    for idx, vol in enumerate(vol_ids):
        df_vol = df[df['icao24'] == vol]
        ax2.scatter(df_vol['longitude'], df_vol['latitude'], 
                    color=cmap(idx), s=20, alpha=0.6,
                    transform=ccrs.Geodetic(), label=vol if idx < 10 else "")

    return fig


def haversine(lat1, lon1, lat2, lon2):
    """Calcule la distance entre deux points géographiques.
    
    Arguments:
    lat1 -- latitude du premier point en degrés
    lon1 -- longitude du premier point en degrés
    lat2 -- latitude du deuxième point en degrés
    lon2 -- longitude du deuxième point en degrés
    
    Retourne:
    distance en kilomètres (float)
    """
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    return 2 * R * math.asin(math.sqrt(a))


@st.cache_data
def plot_approches_aeroport(df, lat_aero, lon_aero, airport_name):
    """Crée une carte interactive Folium des approches aéroportuaires dans un rayon de 5km.
    
    Arguments:
    df -- DataFrame avec colonnes 'on_ground', 'icao24', 'latitude', 'longitude', 'time'
    lat_aero -- latitude de l'aéroport (float)
    lon_aero -- longitude de l'aéroport (float)
    airport_name -- nom de l'aéroport (str)
    
    Retourne:
    objet folium.Map
    """
    import random
    
    # Haversine vectorisé
    R = 6371
    lat1_rad = np.radians(lat_aero)
    lat2_rad = np.radians(df['latitude'])
    dlat = lat2_rad - lat1_rad
    dlon = np.radians(df['longitude'] - lon_aero)
    
    a = np.sin(dlat/2)**2 + np.cos(lat1_rad) * np.cos(lat2_rad) * np.sin(dlon/2)**2
    distances = 2 * R * np.arcsin(np.sqrt(a))
    
    df_proche = df[distances <= 15].copy()
    
    m = folium.Map(location=[lat_aero, lon_aero], zoom_start=13)

    folium.Marker(
        [lat_aero, lon_aero],
        popup=airport_name,
        icon=folium.Icon(color="red", icon="plane", prefix="fa")
    ).add_to(m)

    df_ground = df_proche[df_proche['on_ground'] == True]

    arriving_planes = []
    for icao, g in df_ground.groupby('icao24'):
        last = g.sort_values('time').tail(1)
        if (abs(last['latitude'].iloc[0] - lat_aero) < 0.01) and \
           (abs(last['longitude'].iloc[0] - lon_aero) < 0.01):
            arriving_planes.append(icao)

    df_arrivals = df_proche[df_proche['icao24'].isin(arriving_planes)]

    colors = {icao: "#{:06x}".format(random.randint(0, 0xFFFFFF)) 
              for icao in df_arrivals['icao24'].unique()}

    for icao, g in df_arrivals.groupby('icao24'):
        g = g.sort_values('time').tail(150).dropna(subset=['latitude', 'longitude'])
        
        if len(g) < 2:
            continue
        
        points = list(zip(g['latitude'], g['longitude']))
        
        folium.CircleMarker(
            location=[g['latitude'].iloc[-1], g['longitude'].iloc[-1]],
            radius=10,
            color=colors[icao],
            fill=True,
            fill_color=colors[icao],
            fill_opacity=0.9,
            tooltip=f"ICAO24: {icao}"
        ).add_to(m)

        folium.PolyLine(
            locations=points,
            weight=2,
            opacity=0.8,
            color=colors[icao]
        ).add_to(m)

    return m


def charger_image_unsplash(model_name, largeur_max=200):
    """Charge et affiche une image aléatoire d'avion depuis l'API Unsplash.
    
    Arguments:
    model_name -- nom du modèle d'avion à rechercher (str)
    largeur_max -- largeur maximale de l'image en pixels (int, défaut: 200)
    
    Retourne:
    None (affiche directement dans Streamlit)
    """
    load_dotenv() 
    access_key = os.getenv("UNSPLASH_ACCESS_KEY")
    url = f"https://api.unsplash.com/photos/random?query={model_name}&client_id={access_key}"

    try:
        resp = requests.get(url, timeout=5).json()
        img_url = resp['urls']['regular']
        img = Image.open(BytesIO(requests.get(img_url).content))
        if img.width > largeur_max:
            ratio = largeur_max / img.width
            img = img.resize((largeur_max, int(img.height * ratio)))
        st.image(img, caption=f"Image de {model_name}", use_container_width=False)
    except:
        st.warning("Clé Unsplash non définie. Créez un fichier .env avec UNSPLASH_ACCESS_KEY")