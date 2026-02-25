import datetime as dt
import json

import requests
from flask import Flask, jsonify, request

API_TOKEN = "secret"

RSA_KEY = "secret"

app = Flask(__name__)


class InvalidUsage(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv["message"] = self.message
        return rv


def generate_weather(location: str, date: str):
    url = f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{location}/{date}?key={RSA_KEY}"

    response = requests.get(url)

    if response.status_code == requests.codes.ok:
        return response.json()
    else:
        raise InvalidUsage(response.text, status_code=response.status_code)


@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


@app.route("/")
def home_page():
    return "<p><h2>Weather app.</h2></p>"


@app.route("/content/api/v1/integration/generate", methods=["POST"])
def joke_endpoint():
    start_dt = dt.datetime.now()
    json_data = request.get_json()

    if json_data.get("token") is None:
        raise InvalidUsage("token is required", status_code=400)

    token = json_data.get("token")

    if token != API_TOKEN:
        raise InvalidUsage("wrong API token", status_code=403)

    location = json_data.get("location")
    date = json_data.get("date")

    if not location or not date:
        raise InvalidUsage("location and date are required", status_code=400)

    weather = generate_weather(location, date)
    end_dt = dt.datetime.now()

    day = weather["days"][0]
    result = {
        "requester_name": "Markovska Taisia",
        "timestamp": end_dt.isoformat() + "Z",
        "location": location,
        "date": date,
        "weather": {
            "temp_c": day["temp"],
            "wind_kph": day["windspeed"],
            "pressure_mb": day["pressure"],
            "humidity": day["humidity"]
            }
        }
    return result

