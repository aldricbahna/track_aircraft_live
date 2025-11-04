from opensky_api import OpenSkyApi
import pickle

api = OpenSkyApi()

print("Récupération des données en cours...")
states = api.get_states()

with open('data/states.pkl', 'wb') as handle:
    pickle.dump(states, handle)
    
print(f"Données sauvegardées ! Nombre d'avions détectés : {len(states.states) if states else 0}")