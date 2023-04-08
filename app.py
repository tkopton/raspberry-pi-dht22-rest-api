#!flask/bin/python
import sys
import optparse
import datetime
import Adafruit_DHT
from flask import Flask, jsonify
from importlib import reload

app = Flask(__name__)
sensor_name1 = 'Sensor-DC-Room1'
sensor_id1= 1
gpio_pin1 = 4

sensor_name2 = 'Sensor-DC-Room2'
sensor_id2 = 2
gpio_pin2 = 22

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

    if gpio_pin == 4:
        humidity, temperature = Adafruit_DHT.read_retry(Adafruit_DHT.DHT22, gpio_pin) if not debug_mode else debug_measurement
    else:
        humidity, temperature = Adafruit_DHT.read_retry(
            Adafruit_DHT.DHT11, gpio_pin) if not debug_mode else debug_measurement
    
    last_measurement_time = datetime.datetime.now()
    last_measurement = (humidity, temperature)

    return last_measurement

@app.route('/api/v1/<int:sensorId>/temperature', methods=['GET'])
def get_temperature(sensorId):
    if sensorId == 1:
        gpio = 4
    else:
        gpio = 22 
    temperature = get_measurement(gpio)[1]
    return jsonify({
        'temperature': temperature, 
        'timestamp': last_measurement_time.isoformat()
    })


@app.route('/api/v1/<int:sensorId>/humidity', methods=['GET'])
def get_humidity(sensorId):
    if sensorId == 1:
        gpio = 4
    else:
        gpio = 22 
    humidity = get_measurement(gpio)[0]
    return jsonify({
        'humidity': humidity, 
        'timestamp': last_measurement_time.isoformat()
    })


@app.route('/api/v1/<int:sensorId>/temperature+humidity', methods=['GET'])
def get_temperature_and_humidity(sensorId):
    if sensorId == 1:
        gpio = 4
    else:
        gpio = 22 
    humidity, temperature = get_measurement(gpio)
    return jsonify({
        'temperature': temperature,
        'humidity': humidity, 
        'timestamp': last_measurement_time.isoformat()
    })
    
@app.route('/api/v1/sensors', methods=['GET'])
def get_sensors():
    return jsonify({
        "sensors": [
            {
                "id": sensor_id1,
                "name": sensor_name1
            },
            {
                "id": sensor_id2,
                "name": sensor_name2
            }
        ]
    })

if __name__ == '__main__':
    reload(sys)
    flaskrun(app)