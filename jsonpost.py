'''

Matchability - Testing POST requests to API

'''

import requests
import json

# lets use the dummmydata.json file
with open('Data/dummydatamissing.json') as f:
    d = json.load(f)

# define the target URL
url = "http://localhost:5000/api/opportunity"

data = d
res = requests.post(url, verify=False, json=data)
try:
    res_json = res.json()
    print("\n")
    print(res_json)
    print("\n")
except:
    print("\n")
    print(res.text)
    print("\n")
