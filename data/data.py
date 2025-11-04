import pickle
import pandas as pd

with open('data/states.pkl', 'rb') as handle:
    states = pickle.load(handle)

df_states=pd.DataFrame()
for col in vars(states.states[0]):
    df_states[col]=None
for i in range(0,len(states.states)): #len(states.states)
    avion = states.states[i]
    for col in vars(avion).keys():
        df_states.loc[i,col]=vars(avion)[col]
df_states.to_parquet('data/df_states.parquet')
