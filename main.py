from flask import Flask, render_template, request, jsonify, send_file
from gpiozero import LED
import time
import threading
import adafruit_dht
import board

app = Flask(__name__)
dhtSensor = adafruit_dht.DHT11(board.D18)
relay = LED(17)

temperature_data = {
    "cur_temp": 70,
    "target_temp": 70, 
    "running": 0,
    "humidity": 20,
    "auto": 1
}

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
        if temperature_data["target_temp"] > temperature_data["cur_temp"] and temperature_data["auto"]: temperature_data["running"] = 1
        else: temperature_data["running"] = 0
        print("updated")
        time.sleep(1)

def updatePins():
    while temperature_data["auto"]:
        if temperature_data["running"]: relay.on()
        else: relay.off()
        print("updated pins")
        time.sleep(60 * 5)

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/api', methods = ['POST', 'GET'])
def api():
    if request.method == 'POST':
        request_dict = dict(request.form)
        for request_key in request_dict:
            for temp_key in temperature_data:
                if request_key == temp_key:
                    temperature_data[temp_key] = int(request_dict[request_key])
                    print(temperature_data[temp_key])
        return jsonify(temperature_data)
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