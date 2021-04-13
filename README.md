# rpi-thermostat
a thermostat created with mostly python that runs on a raspberry pi

when this becomes more tested, i will update on how to build and publish for production

## dependencies:
- python [flask](https://flask.palletsprojects.com) as a web framework 
- [jquery](https://jquery.com/) as a javascript library because i dont know how to javascript
- [js-cookie](https://github.com/js-cookie/js-cookie) to write and retrive user configuration for the web interface
- python [venv](https://docs.python.org/3/library/venv.html) to install python dependencies for other python libraries locally for the project
- adafruits [circuitpython-dht](https://github.com/adafruit/Adafruit_CircuitPython_DHT) library used for the current temperature sensor

### installing the dependencies on raspberry pi os:

\# indicating that you have to be able to run commands with root permissions (run with `sudo`)

$ indicating that you can be any user on the system
 
    # apt update
    # apt install libgpiod2 python3-pip python3-venv
if you want to seperate global python libraries from the one used in the rpi-thermostat directory, use `source venv/bin/activate` after initallizing the python evironment(run `python3 -v venv venv` after running installing python3-venv)

    $ pip3 install adafruit-circuitpython-dht gpiozero
    $ pip3 install flask
or run the following which just automates all the steps and also collects the javascript libraries: 

    $ chmod +x install_dependencies.sh
    # ./install_dependencies.sh

if you would like to change where the libraries are downloaded from, edit the links in the [install-dependencies.sh](./install_dependencies.sh) file which just download js-cookies and jquery and appends it to templates/long_scripts

materials to build(currently which is testing):
- any raspberry pi(preferably a pi zero w for small size and wireless capabillities)
- a dht11 temperature and humitity sensor