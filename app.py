from flask import Flask, jsonify, request
import numpy as np
import json
import random
import requests
import urllib
from keys import API_KEY
import engine

app = Flask(__name__)


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


@app.route("/simplesuggest")
def simplesuggest():
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


@app.route("/suggest")
def suggest():
    # query = str(request.args['query'])
    # exclude = str(request.args['exclude'])
    # base_id = str(request.args['base_id'])
    query = "48.8584,2.2945"
    exclude = []
    base_id = "ChIJbWdK0eZv5kcROmLZY2qD4gk"
    base_text = get_reviews(base_id)
    base = [base_id, base_text]
    candidates = get_suggestion_candidates(query, exclude)
    embedded_candidates = []
    for candidate in candidates:
        candidate_id = candidate["place_id"]
        candidate_text = get_reviews(candidate_id)
        embedded_candidates.append([candidate_id, candidate_text])
    recommendations = engine.get_recommendations(
        np.array(base), np.array(embedded_candidates))
    recommendations = recommendations[:5,:]
    print(recommendations[:,1])
    candidates = [c for c in candidates if c["place_id"] in recommendations[:,1]]
    response = jsonify(candidates)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


def get_reviews(place_id):
    # place_id = "ChIJbWdK0eZv5kcROmLZY2qD4gk"
    url = "https://maps.googleapis.com/maps/api/place/details/json?"
    params = {"key": API_KEY, "place_id": place_id,
              "fields": "name,type,reviews"}
    url_params = urllib.parse.urlencode(params)
    url = f"{url}{url_params}"
    payload = {}
    headers = {}
    data = requests.request("GET", url, headers=headers, data=payload).json()
    types = data["result"]["types"]
    name = data["result"]["name"]
    reviews = data["result"]["reviews"]
    reviews = [reviews[i]["text"] for i in range(len(reviews))]
    embedded_reviews = name + " "
    for t in types:
        embedded_reviews += t + " "
    for review in reviews:
        embedded_reviews += review
    return embedded_reviews


def get_suggestion_candidates(query, exclude):
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
    return candidates
