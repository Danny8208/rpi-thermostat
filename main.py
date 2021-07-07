from flask import Flask, render_template, request, jsonify, send_file
from gpiozero import LED
from hidden_vars import *
import time
import threading
import adafruit_dht
import pymongo
import secrets

app = Flask(__name__)
dhtSensor = adafruit_dht.DHT11(18)
heating_relay = LED(23)
cooling_relay = LED(24)
db_client = pymongo.MongoClient(mongo_uri)
thermostat_database = db_client["rpi_thermostat_db0"]
api_keys = thermostat_database["api_keys"]

temperature_data = {
    "current_temp": 70,
    "target_temp": 80,
    "target_heat_cool_state": 1,
    "current_heat_cool_state": 1,
    "temp_display_units": 0,
    "humidity": 20,
}


def generate_api_key():
    key = secrets.token_urlsafe(128)
    api_keys.insert_one({"api_key": key})
    print(key)
    return {"api_key": key}


def update():
    while True:
        try:
            if temperature_data["temp_display_units"] == 0:
                temperature_data["current_temp"] = dhtSensor.temperature
            elif temperature_data["temp_display_units"] == 1:
                temperature_data["current_temp"] = dhtSensor.temperature * (9 / 5) + 32
            temperature_data["humidity"] = dhtSensor.humidity
            print("update sensor values")
        except RuntimeError as error:
            print(error.args[0])
            time.sleep(2)
            continue
        except Exception as error:
            dhtSensor.exit()
            raise error
        if heating_relay.is_active:
            temperature_data["current_heat_cool_state"] = 1
        elif cooling_relay.is_active:
            temperature_data["current_heat_cool_state"] = 2
        elif not heating_relay.is_active and not cooling_relay.is_active:
            temperature_data["current_heat_cool_state"] = 0


def setRelays(relay):
    if relay == "cooling":
        heating_relay.off()
        cooling_relay.on()
    if relay == "heating":
        heating_relay.on()
        cooling_relay.off
    if relay == "off":
        heating_relay.off()
        cooling_relay.off()


def updatePins():
    while True:
        if (
            temperature_data["target_heat_cool_state"] == 1
            and temperature_data["target_temp"] > temperature_data["current_temp"]
        ):
            setRelays("heating")
        elif (
            temperature_data["target_heat_cool_state"] == 2
            and temperature_data["target_temp"] < temperature_data["current_temp"]
        ):
            setRelays("cooling")
        else:
            setRelays("off")
        time.sleep(10)
        print("updated pins")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/long_scripts")
def long_scripts():
    return send_file("templates/long_scripts.js")


@app.route("/scripts")
def scripts():
    return send_file("templates/scripts.js")


@app.route("/phone_authentication")
def phone_authentication():
    return render_template("phone_authentication.html")


@app.route("/address_authentication")
def address_authentication():
    return render_template("address_authentication.html")


@app.route("/api", methods=["POST", "GET"])
def api():
    if request.method == "POST":
        request_dict = dict(request.form) if dict(request.form) else request.json
        print(request_dict)
        if request_dict:
            if "api_key" in request_dict:
                if api_keys.find_one({"api_key": request_dict["api_key"]}) != None:
                    for request_key in request_dict:
                        for temp_key in temperature_data:
                            if request_key == temp_key:
                                temperature_data[temp_key] = int(request_dict[temp_key])
                    return "authenticated"
                else:
                    return "invalid key"
            else:
                return "missing key"
        else:
            print("recieved empty request")
            return "recieved empty request"
    else:
        return jsonify(temperature_data)


@app.route("/register_api_key", methods=["POST"])
def register_api_key():
    request_dict = dict(request.form) if dict(request.form) else request.json
    print(request_dict)
    if "auth_type" in request_dict:
        if request_dict["auth_type"] == "phone_number":
            if str(request_dict["number"]) in phone_numbers:
                return jsonify(generate_api_key())
            else:
                return "invalid number"
        elif request_dict["auth_type"] == "address":
            if (
                request_dict["street_address"].lower() == address["street_address"]
                and request_dict["city"].lower() == address["city"]
                and request_dict["state"].lower() == address["state"]
                and request_dict["zip_code"] == address["zip_code"]
            ):
                return generate_api_key()
            else:
                return "invalid address"
        else:
            return "invalid auth type"
    else:
        return "no auth type"


if __name__ == "__main__":
    updateThread = threading.Thread(target=update)
    updatePinsThread = threading.Thread(target=updatePins)
    updateThread.start()
    updatePinsThread.start()
    app.run(host="0.0.0.0")
    updateThread.join()
    updatePinsThread.join()
