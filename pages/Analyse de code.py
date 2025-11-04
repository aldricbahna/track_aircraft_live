import streamlit as st

st.title("Analyse rapide du code « ElonJet »")

st.header("1. Récupération des sources avec git")
st.markdown("""
git clone https://github.com/Jxck-S/plane-notify.git
""")

st.header("2. Description de la structure du projet")
st.markdown("""
- Le dépôt contient de nombreux fichiers Python (`.py`), un `Dockerfile`, un `docker-compose.yml`, des fichiers de configuration (`.ini`) et un dossier `configs`
- On trouve des modules tels que `planeClass.py`, `defOpenSky.py`, `defMap.py`, `fuel_calc.py` etc

""")

st.subheader("Documentation et installation")
st.markdown("""
- Le README explique les grandes lignes : dépendances Python/ Pipenv, utilisation de Selenium/ChromeDriver ou Google Static Maps
- L’installation est décrite (avec Docker ou non)
""")

st.subheader("Licence : usage personnel / commercial")
st.markdown("""
- Licence : GPL-3.0.
- Ok pour un usage personnel ou de recherche 
- Ok pour un usage commercial mais sous les contraintes de la GPL 
""")

st.header("3. Que fait le code ?")
st.markdown("""
**Fonctionnement général :**
- Récupère des données ADS-B (OpenSky / ADSB-Exchange)
- Détecte l’état du vol (au sol / décollage / en vol / atterrissage)
- Envoie des notifications (Twitter / Telegram / Discord / Mastodon)
- Peut générer des cartes ou captures (via Selenium / Google Maps)

**Dépendances principales :**
- Python 3, `requests`, `selenium`, `chromedriver`
- APIs OpenSky / ADSB-Exchange
- Optionnel : Docker et docker-compose
""")

st.header("4. Qualité du code")
st.markdown("""
- Projet perso, structure non optimale 
- PEP8 pas au top
""")

st.header("5. Utilité pour notre TP")
st.markdown("""
- Nécessite adaptation / simplification
- Modules réutilisables mais pas directement comme squelette
""")

st.header("6. Conclusion")
st.markdown("""
Projet très intéressant, on va s'en inspirer à notre sauce avec notre propre architecture
""")

