'''

Matchability - API
Receiving POST request and returning predictions.

'''

from flask import Flask, request
import json
# import our integration
from matchability import matchability

app = Flask(__name__) # create the Flask app

@app.route('/api/opportunity', methods=['GET', 'POST'])

def matcha_request():
    if request.method == "POST":
        req_data = request.get_json()
        data = req_data['data']
        res_as_json = matchability(data)

        return res_as_json

    else:
        return "Error: Method not allowed. Please use POST request."

# Run the app on port 5000
app.run(port=5000)
