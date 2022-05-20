from flask import Flask, jsonify, request
import numpy as np
import json
import random
import requests
import urllib
from keys import API_KEY
import engine

app = Flask(__name__)

types = ["bakery", "bar", "cafe", "casino", "museum", "night_club",
         "park", "restaurant", "shopping_mall", "tourist_attraction", "zoo"]


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
    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?"
    params = {"location": query,
              "key": API_KEY, "radius": 15000, "type": "tourist_attraction"}
    url_params = urllib.parse.urlencode(params)
    url = f"{url}{url_params}"
    payload = {}
    headers = {}
    data = requests.request("GET", url, headers=headers, data=payload)
    candidates = data.json()["results"]
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
    query = str(request.args['query'])
    exclude = str(request.args['exclude'])
    base_id = str(request.args['base_id'])

    base_text = get_embedded_reviews(get_place_details(base_id))
    base = [base_id, base_text]

    candidates = []
    for t in types:
        candidates_for_type = nearby_search(query, exclude, type=t)
        candidates += candidates_for_type

    print("nearby_search:")
    candidates = [c["place_id"] for c in candidates]
    candidates = set(candidates)
    print(candidates)
    print()
    print()
    print()
    candidates = [get_place_details(candidate) for candidate in candidates]
    print("place details:")
    print([c["name"] for c in candidates])
    # print()
    # print()
    # print()
    # candidates = filter_by_type(candidates, types)
    # print("filter:")
    # print([c["name"] for c in candidates])

    embedded_candidates = []
    for candidate in candidates:
        candidate_text = get_embedded_reviews(candidate)
        embedded_candidates.append([candidate["place_id"], candidate_text])

    recommendations = engine.get_recommendations(
        np.array(base), np.array(embedded_candidates))
    recommendations = recommendations[:5, :]

    candidates = [c for c in candidates if c["place_id"]
                  in recommendations[:, 1]]

    response = jsonify(candidates)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


def get_place_details(place_id):
    url = "https://maps.googleapis.com/maps/api/place/details/json?"
    params = {"key": API_KEY, "place_id": place_id,
              #   "fields": "name,type,reviews" TODO: filter fields?
              }
    url_params = urllib.parse.urlencode(params)
    url = f"{url}{url_params}"
    data = requests.request("GET", url).json()
    return data["result"]


def get_embedded_reviews(place):
    types = place["types"]
    name = place["name"]
    reviews = place.get("reviews", [])
    reviews = [reviews[i]["text"] for i in range(len(reviews))]
    embedded_reviews = name + " "
    for t in types:
        embedded_reviews += t + " "
    for review in reviews:
        embedded_reviews += review
    return embedded_reviews


def nearby_search(query, exclude=[], type=""):
    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?"
    params = {"location": query,
              "key": API_KEY, "radius": 15000, "type": type}
    url_params = urllib.parse.urlencode(params)
    url = f"{url}{url_params}"
    payload = {}
    headers = {}
    data = requests.request("GET", url, headers=headers, data=payload).json()
    candidates = [p for p in data["results"][:5]
                  if p["place_id"] not in exclude]
    return candidates


def filter_by_type(places, types):
    filtered_places = []
    for p in places:
        p_types = p["types"]
        added = False
        for p_type in p_types:
            for t in types:
                if p_type == t:
                    filtered_places.append(p)
                    added = True
                    break
            if added:
                break
    return filtered_places
