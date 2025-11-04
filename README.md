Track Aircraft Live

Ce projet permet de suivre les avions d'une date donnée grâce aux données ADS-B et de visualiser leur position sur une carte interactive avec Streamlit.

1ère solution : installation et exécution en local :

Cloner le dépôt :

git clone https://github.com/aldricbahna/track_aircraft_live.git
cd track_aircraft_live

Installer les dépendances avec uv :

uv sync

Exécuter l'application Streamlit :

streamlit run Home.py

L'application sera accessible dans votre navigateur à l'adresse indiquée par Streamlit (généralement http://localhost:8501)

2ème solution : naviguer sur le streamlit cloud

[Streamlit cloud ](https://trackaircraftlive-papy.streamlit.app/)