from flask import Flask, Response, jsonify
import json
import random

app = Flask(__name__)

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