from flask import Flask, Response, jsonify, request
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
    with open('attractions.json', 'r') as file:
        data = file.read()
    attractions = json.loads(data)
    response = jsonify(attractions["attractions"][0])
    response.headers.add('Access-Control-Allow-Origin', '*')
    print(response)
    return response


@app.route("/randomsuggestions")
def randomSuggestions():
    with open('attractions.json', 'r') as file:
        data = file.read()
    attractions = json.loads(data)
    response = jsonify(random.sample(attractions["attractions"], 3))
    response.headers.add('Access-Control-Allow-Origin', '*')
    print(response)
    return response


@app.route("/suggest")
def text_search():
    key = str(request.args['key'])
    query = str(request.args['query'])
    exclude = str(request.args['exclude'])
    if not validate(key):
        return "unauthorized"
    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?"
    params = {"location": query,
              "key": API_KEY, "radius": 15000, "type": "tourist_attraction"}
    url_params = urllib.parse.urlencode(params)
    url = f"{url}{url_params}"
    payload = {}
    headers = {}
    response = requests.request(
        "GET", url, headers=headers, data=payload)
    candidates = [p for p in response.json()["results"] if p["place_id"] not in exclude]
    return {"results": candidates[0:3]}
