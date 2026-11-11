import time
import board
from flask import Flask, render_template, jsonify
from adafruit_bme280 import basic as adafruit_bme280

# Initialize sensor
i2c = board.I2C()
bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c)
bme280.sea_level_pressure = 1013.25  # Adjust as needed

# Create Flask app
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/sensor_data')
def sensor_data():
    data = {
        "temperature": round(bme280.temperature, 1),
        "humidity": round(bme280.relative_humidity, 1),
        "pressure": round(bme280.pressure, 1),
        "altitude": round(bme280.altitude, 2)
    }
    return jsonify(data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
