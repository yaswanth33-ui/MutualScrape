import requests as rq
import pandas as pd

api = "https://api.mfapi.in/mf"

response = rq.get(api).json()
all_mf = pd.DataFrame(response)

all_mf.to_csv("all_mf.csv", index=False)

for sample in all_mf['schemeCode']:
    response = rq.get(api +"/"+ str(sample)).json()
    data = pd.DataFrame(response['data'])
    data.to_csv(f"test/{sample}.csv", index=False)

print("All data downloaded successfully.")
