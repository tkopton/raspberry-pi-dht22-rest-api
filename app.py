#!flask/bin/python
import sys
import optparse
import datetime
import Adafruit_DHT
from flask import Flask, jsonify
from importlib import reload

app = Flask(__name__)
sensor_name1 = 'Sensor-Rack01-Top'
sensor_id1= 1
gpio_pin1 = 4

sensor_name2 = 'Sensor-Rack02-Bottom'
sensor_id2 = 2
gpio_pin2 = 4

last_measurement = (None, None)
last_measurement_time = None

debug_mode = False
debug_measurement = (22.7, 32)

# http://flask.pocoo.org/snippets/133/
def flaskrun(app,
                  default_host='127.0.0.1', 
                  default_port='5000'):
    global sensor_name1
    global gpio_pin1
    global sensor_id1
    global sensor_name2
    global gpio_pin2
    global sensor_id2
    global debug_mode

    parser = optparse.OptionParser()
    parser.add_option('-H', '--host',
                      help='Hostname of the Flask app ' + \
                           '[default %s]' % default_host,
                      default=default_host)
    parser.add_option('-P', '--port',
                      help='Port for the Flask app ' + \
                           '[default %s]' % default_port,
                      default=default_port)
    parser.add_option('-d', '--debug',
                      action='store_true', dest='debug',
                      help=optparse.SUPPRESS_HELP)

    options, _ = parser.parse_args()
    debug_mode = options.debug

    app.run(debug=options.debug,
        host=options.host,
        port=int(options.port)
    )

def get_measurement(gpio_pin):
    global last_measurement
    global last_measurement_time
    
    humidity, temperature = Adafruit_DHT.read_retry(Adafruit_DHT.DHT22, gpio_pin) if not debug_mode else debug_measurement
    last_measurement_time = datetime.datetime.now()
    last_measurement = (humidity, temperature)

    return last_measurement
    
@app.route('/api/v1/sensors', methods=['GET'])
def get_sensors():
    humidity1, temperature1 = get_measurement(gpio_pin1)
    humidity2, temperature2 = get_measurement(gpio_pin2)
    return jsonify({
        "sensors": [
            {
                "id": sensor_id1,
                "name": sensor_name1,
                'temperature': temperature1,
                'humidity': humidity1,
                'timestamp': last_measurement_time.isoformat(),
            },
            {
                "id": sensor_id2,
                "name": sensor_name2,
                'temperature': temperature2,
                'humidity': humidity2,
                'timestamp': last_measurement_time.isoformat(),
            }
        ]
    })

@app.route('/api/v1/systeminfo', methods=['GET'])
def get_systeminfo():
    return jsonify({
        "System name": "Environment 01",
        "System Id": "E01" 
    })
    
if __name__ == '__main__':
    reload(sys)
    flaskrun(app)