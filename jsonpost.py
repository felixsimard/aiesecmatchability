'''

Matchability - Testing POST requests to API

'''

import requests
import json

# lets use the dummmydata.json file
with open('dummydata.json') as f:
    d = json.load(f)

# define the target URL
url = "http://localhost:5000/api/opportunity"

data = d
res = requests.post(url, verify=False, json=data)
res_json = res.json()
print("\n")
print(res_json)
print("\n")
