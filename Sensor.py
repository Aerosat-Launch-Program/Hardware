import smbus2
import bme280

# Define the I2C bus number (usually 1 for Raspberry Pi)
bus_number = 1

# Define the I2C address of the BMP280 sensor
address = 0x76

# Initialize the I2C bus
bus = smbus2.SMBus(bus_number)

# Initialize the BMP280 sensor
calibration_params = bme280.load_calibration_params(bus, address)

# Read sensor data
data = bme280.sample(bus, address, calibration_params)

# Print the sensor data
print(f"Temperature: {data.temperature:.2f} °C")
print(f"Pressure: {data.pressure:.2f} hPa")
print(f"Humidity: {data.humidity:.2f} %")


import board
import busio
import adafruit_ahtx0

# Create I2C bus
i2c = busio.I2C(board.SCL, board.SDA)

# Create an AHT10 sensor object
sensor = adafruit_ahtx0.AHTx0(i2c)

while True:
    # Read temperature and humidity data
    temperature = sensor.temperature
    humidity = sensor.relative_humidity

    # Print the data
    print("Temperature: {:.2f}°C".format(temperature))
    print("Humidity: {:.2f}%".format(humidity))

    # You can add a delay if needed
    # time.sleep(1)


