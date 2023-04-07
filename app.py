#!flask/bin/python
import sys
import optparse
import datetime
import Adafruit_DHT
from flask import Flask, jsonify
from importlib import reload

app = Flask(__name__)
sensor_name1 = 'Sensor-DC-Room1'
gpio_pin1 = 4

last_measurement1 = (None, None)
last_measurement_time1 = None

debug_mode = False
debug_measurement = (22.7, 32)

# http://flask.pocoo.org/snippets/133/
def flaskrun(app,
                  default_host='127.0.0.1', 
                  default_port='5000', 
                  default_sensor_name='Sensor',
                  default_gpio_pin=4):
    global sensor_name1
    global gpio_pin1
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
    parser.add_option('-N', '--sensor-name',
                      help='The name of the sensor being read for measurements' + \
                           '[default %s]' % default_sensor_name,
                      default=default_sensor_name)
    parser.add_option('-G', '--gpio-pin',
                    help='The GPIO pin to which the sensor is connected' + \
                            '[default %s' % default_gpio_pin,
                            default=default_gpio_pin)
    parser.add_option('-d', '--debug',
                      action='store_true', dest='debug',
                      help=optparse.SUPPRESS_HELP)

    options, _ = parser.parse_args()

    sensor_name1 = options.sensor_name
    gpio_pin1 = options.gpio_pin
    debug_mode = options.debug

    app.run(debug=options.debug,
        host=options.host,
        port=int(options.port)
    )

def get_measurement():
    global last_measurement1
    global last_measurement_time1

    humidity1, temperature1 = Adafruit_DHT.read_retry(Adafruit_DHT.DHT22, gpio_pin1) if not debug_mode else debug_measurement
    
    last_measurement_time1 = datetime.datetime.now()
    last_measurement1 = (humidity1, temperature1)

    return last_measurement1

@app.route('/api/v1/temperature', methods=['GET'])
def get_temperature():
    temperature = get_measurement()[1]
    return jsonify({
        'name': sensor_name1, 
        'temperature': temperature, 
        'timestamp': last_measurement_time1.isoformat()
    })

@app.route('/api/v1/humidity', methods=['GET'])
def get_humidity():
    humidity = get_measurement()[0]
    return jsonify({
        'name': sensor_name1, 
        'humidity': humidity, 
        'timestamp': last_measurement_time1.isoformat()
    })

@app.route('/api/v1/temperature+humidity', methods=['GET'])
def get_temperature_and_humidity():
    humidity, temperature = get_measurement()
    return jsonify({
        'name': sensor_name1, 
        'temperature': temperature,
        'humidity': humidity, 
        'timestamp': last_measurement_time1.isoformat()
    })

if __name__ == '__main__':
    reload(sys)
    flaskrun(app)