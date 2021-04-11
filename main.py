from flask import Flask, render_template, request, jsonify, send_file
import json

app = Flask(__name__)

temperature_data = {
    "cur_temp": 70,
    "target_temp": 80,
    "running": 0,
    "humidity": 20
}

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
        if temperature_data["target_temp"] > temperature_data["cur_temp"]:
            temperature_data["running"] = 1
        else: temperature_data["running"] = 0
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
    app.run(host='0.0.0.0')