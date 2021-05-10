from flask import Flask, render_template, request, jsonify, send_file
from gpiozero import LED
import time
import threading
import adafruit_dht
import board
import pymongo
import secrets

app = Flask(__name__)
dhtSensor = adafruit_dht.DHT11(board.D18)
relay = LED(17)
client = pymongo.MongoClient()
database = client["rpi_thermostat_db"]
api_keys = database["api_keys"]
api_keys.delete_many({})

temperature_data = {
    "cur_temp": 70,
    "target_temp": 70,
    "running": 0,
    "humidity": 20,
    "auto": 1
}

address = {
    "street_address": "***insert address***",
    "city": "randolph",
    "state": "ma",
    "zip_code": "02368"
}
phone_numbers = ['1234567890']


def update():
    while True:
        try:
            temperature_data["cur_temp"] = dhtSensor.temperature * (9/5) + 32
            temperature_data["humidity"] = dhtSensor.humidity
            print("update sensor values")
        except RuntimeError as error:
            print(error.args[0])
            continue
        except Exception as error:
            dhtSensor.exit()
            raise error
            continue
        if temperature_data["target_temp"] > temperature_data["cur_temp"] and temperature_data["auto"]:
            temperature_data["running"] = 1
        else:
            temperature_data["running"] = 0
        time.sleep(1)


def updatePins():
    while temperature_data["auto"]:
        if temperature_data["running"]:
            relay.on()
        else:
            relay.off()
        print("updated pins")
        time.sleep(60 * 5)


def generate_api_key():
    key = secrets.token_urlsafe(128)
    api_keys.insert_one({"api_key": key})
    print(key)
    return jsonify({"api_key": key})


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/register_api_key', methods=['POST', 'GET'])
def register_api_key():
    if request.method == 'POST':
        request_dict = dict(request.form)
        print(request_dict)
        if "auth_type" in request_dict:
            if request_dict["auth_type"] == "phone_number":
                if request_dict["number"] in phone_numbers:
                    return generate_api_key()
                else:
                    return "no number provided or invalid number"
            elif request_dict["auth_type"] == "address":
                if request_dict["street_address"].lower() == address["street_address"] and \
                        request_dict["city"].lower() == address["city"] and \
                        request_dict["state"].lower() == address["state"] and \
                        request_dict["zip_code"] == address["zip_code"]:
                    return generate_api_key()
                else:
                    return "invalid address"
            else:
                return "invalid auth type"
        else:
            return "no auth type"


@app.route('/phone_authentication')
def phone_authentication():
    return render_template("phone_authentication.html")


@app.route('/address_authentication')
def address_authentication():
    return render_template("address_authentication.html")


@app.route('/api', methods=['POST', 'GET'])
def api():
    if request.method == 'POST':
        request_dict = dict(request.form)
        print(request_dict)
        if "api_key" in request_dict:
            if api_keys.find_one({"api_key": request_dict["api_key"]}) != None:
                for request_key in request_dict:
                    for temp_key in temperature_data:
                        if request_key == temp_key:
                            temperature_data[temp_key] = int(
                                request_dict[request_key])
                            print(temperature_data[temp_key])
                return "authenticated"
            else:
                return "invalid key"
        else:
            return "missing key"
    else:
        return jsonify(temperature_data)


@app.route('/settings')
def settings():
    return render_template("settings.html")


@app.route('/scripts')
def script():
    return send_file("templates/scripts.js")


@app.route('/long_scripts')
def long_scripts():
    return send_file("templates/long_scripts.js")


if __name__ == '__main__':
    updateThread = threading.Thread(target=update)
    updatePinsThread = threading.Thread(target=updatePins)
    updateThread.start()
    updatePinsThread.start()
    app.run(host='0.0.0.0')
    updateThread.join()
    updatePinsThread.join()
