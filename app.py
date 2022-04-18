from flask import Flask, jsonify, request
import json
import random
import requests
import urllib

app = Flask(__name__)

API_KEY = "AIzaSyCw9ZcuO_ASGpg2nRcfFJOvVbI1ZHqVnYs"


def validate(key):
    return key == API_KEY


@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"


@app.route("/randomitem")
def randomItem():
    with open('./attractions.json', 'r') as file:
        data = file.read()
    attractions = json.loads(data)
    response = jsonify(attractions["attractions"][0])
    response.headers.add('Access-Control-Allow-Origin', '*')
    print(response)
    return response


@app.route("/randomsuggestions")
def randomSuggestions():
    with open('./attractions.json', 'r') as file:
        data = file.read()
    attractions = json.loads(data)
    response = jsonify(random.sample(attractions["attractions"], 3))
    response.headers.add('Access-Control-Allow-Origin', '*')
    print(response)
    return response


@app.route("/suggest")
def suggest():
    query = str(request.args['query'])
    exclude = str(request.args['exclude'])
    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?"
    params = {"location": query,
              "key": API_KEY, "radius": 15000, "type": "tourist_attraction"}
    url_params = urllib.parse.urlencode(params)
    url = f"{url}{url_params}"
    payload = {}
    headers = {}
    data = requests.request("GET", url, headers=headers, data=payload)
    candidates = [p for p in data.json()["results"]
                  if p["place_id"] not in exclude]

    response = jsonify(candidates[0:3])
    response.headers.add('Access-Control-Allow-Origin', '*')

    return response


@app.route("/citysearch")
def citySearch():
    query = str(request.args['query'])
    url = "https://maps.googleapis.com/maps/api/place/autocomplete/json?"
    params = {"input": query,
              "key": API_KEY, "types": "(cities)"}
    url_params = urllib.parse.urlencode(params)
    url = f"{url}{url_params}"
    payload = {}
    headers = {}
    data = requests.request("GET", url, headers=headers,
                            data=payload).json()["predictions"]
    for item in data:
        url = "https://maps.googleapis.com/maps/api/place/details/json?"
        params = {"place_id": item["place_id"],
                  "key": API_KEY, "fields": "geometry"}
        url_params = urllib.parse.urlencode(params)
        url = f"{url}{url_params}"
        payload = {}
        headers = {}
        geometry = requests.request("GET", url, headers=headers,
                                    data=payload).json()["result"]["geometry"]
        item["lat"] = geometry["location"]["lat"]
        item["long"] = geometry["location"]["lng"]
        item["name"] = item["description"]

    print(data)
    response = jsonify(data)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response
