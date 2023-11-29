# for SX126x series or LLCC68
from LoRaRF import SX126x
import picamera
import smbus2
import bme280
import time

LoRa = SX126x()

LoRa.begin()

#------------------------------------------------------------------------------
#MPU6050

# MPU6050 Registers
PWR_MGMT_1 = 0x6B
GYRO_XOUT_H = 0x43
GYRO_YOUT_H = 0x45
GYRO_ZOUT_H = 0x47

# MPU6050 I2C address
MPU6050_ADDR = 0x68

# Initialize I2C bus
bus = smbus2.SMBus(1)

# Wake up MPU6050
bus.write_byte_data(MPU6050_ADDR, PWR_MGMT_1, 0)
#------------------------------------------------------------------------------
# Bme280
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

#------------------------------------------------------------------------------
# Camera

# Initialize the camera
camera = picamera.PiCamera()

try:
    # Start recording a video
    camera.start_recording('video.h264')
    # Record for 10 seconds (you can change the duration)
    camera.wait_recording(10)
    # Stop recording
    camera.stop_recording()
    print("Video captured and saved as 'video.h264'")
finally:
    # Close the camera to release resources
    camera.close()
    
#------------------------------------------------------------------------------
# MPU6050

# Read raw gyroscope data
def read_gyro_data(reg_addr):
    high_byte = bus.read_byte_data(MPU6050_ADDR, reg_addr)
    low_byte = bus.read_byte_data(MPU6050_ADDR, reg_addr + 1)
    gyro_data = (high_byte << 8) | low_byte
    return gyro_data

# Convert raw gyroscope data to degrees per second
def convert_raw_gyro(raw_value):
    if raw_value > 32768:
        raw_value -= 65536
    return raw_value / 131.0

# Read and print gyroscope data
while True:
    gyro_x = convert_raw_gyro(read_gyro_data(GYRO_XOUT_H))
    gyro_y = convert_raw_gyro(read_gyro_data(GYRO_YOUT_H))
    gyro_z = convert_raw_gyro(read_gyro_data(GYRO_ZOUT_H))

    print("Gyroscope (degrees per second):")
    print("X-axis: ", gyro_x)
    print("Y-axis: ", gyro_y)
    print("Z-axis: ", gyro_z)

    time.sleep(0.1)
