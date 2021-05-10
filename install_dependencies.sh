#!/bin/bash

sudo apt update
sudo apt install libgpiod2 python3-pip python3-venv -y

python3 -m venv venv
./venv/bin/pip install adafruit-circuitpython-dht flask gpiozero pymongo

curl https://ajax.googleapis.com/ajax/libs/jquery/3.6.0/jquery.min.js > templates/long_scripts.js
curl https://cdn.jsdelivr.net/npm/js-cookie@rc/dist/js.cookie.min.js >> templates/long_scripts.js

printf "\nto run python or pip commands, use 'source venv/bin/activate' before doing so to keep everything locally inside the rpi-thermostat directory\n"
