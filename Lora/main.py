from time import sleep  # import
import struct
import smbus  # import SMBus module of I2C
import time
import bme280
from LoRaRF import SX126x, LoRaSpi, LoRaGpio
import os
import sys

currentdir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.dirname(os.path.dirname(currentdir)))

# some MPU6050 Registers and their Address
PWR_MGMT_1 = 0x6B
SMPLRT_DIV = 0x19
CONFIG = 0x1A
GYRO_CONFIG = 0x1B
INT_ENABLE = 0x38
ACCEL_XOUT_H = 0x3B
ACCEL_YOUT_H = 0x3D
ACCEL_ZOUT_H = 0x3F
GYRO_XOUT_H = 0x43
GYRO_YOUT_H = 0x45
GYRO_ZOUT_H = 0x47

# BME280 sensor address (default address)
address = 0x76

def MPU_Init():
    # write to sample rate register
    bus.write_byte_data(Device_Address, SMPLRT_DIV, 7)

    # Write to power management register
    bus.write_byte_data(Device_Address, PWR_MGMT_1, 1)

    # Write to Configuration register
    bus.write_byte_data(Device_Address, CONFIG, 0)

    # Write to Gyro configuration register
    bus.write_byte_data(Device_Address, GYRO_CONFIG, 24)

    # Write to interrupt enable register
    bus.write_byte_data(Device_Address, INT_ENABLE, 1)


def read_raw_data(addr):

    # Accelero and Gyro value are 16-bit
    high = bus.read_byte_data(Device_Address, addr)
    low = bus.read_byte_data(Device_Address, addr+1)

    # concatenate higher and lower value
    value = ((high << 8) | low)

    # to get signed value from mpu6050
    if(value > 32768):
        value = value - 65536
    return value


# Begin LoRa radio with connected SPI bus and IO pins (cs and reset) on GPIO
# SPI is defined by bus ID and cs ID and IO pins defined by chip and offset number
spi = LoRaSpi(0, 0)
cs = LoRaGpio(0, 8)
reset = LoRaGpio(0, 24)
busy = LoRaGpio(0, 23)
LoRa = SX126x(spi, cs, reset, busy)

print("Begin LoRa radio")

if not LoRa.begin():
    raise Exception("Something wrong, can't begin LoRa radio")


# Configure LoRa to use TCXO with DIO3 as control
print("Set RF module to use TCXO as clock reference")
LoRa.setDio3TcxoCtrl(LoRa.DIO3_OUTPUT_1_8, LoRa.TCXO_DELAY_10)

# Set frequency to 915 Mhz
print("Set frequency to 915 Mhz")
LoRa.setFrequency(915000000)


# Set TX power, default power for SX1262 and SX1268 are +22 dBm and for SX1261 is +14 dBm

# This function will set PA config with optimal setting for requested TX power
print("Set TX power to +17 dBm")

# TX power +17 dBm using PA boost pin
LoRa.setTxPower(17, LoRa.TX_POWER_SX1262)


# Configure modulation parameter including spreading factor (SF), bandwidth (BW), and coding rate (CR)

# Receiver must have same SF and BW setting with transmitter to be able to receive LoRa packet
print("Set modulation parameters:\n\tSpreading factor = 7\n\tBandwidth = 125 kHz\n\tCoding rate = 4/5")

# LoRa spreading factor: 7
sf = 7

# Bandwidth: 125 kHz
bw = 125000
cr = 5                                                          # Coding rate: 4/5
LoRa.setLoRaModulation(sf, bw, cr)


# Configure packet parameter including header type, preamble length, payload length, and CRC type
# The explicit packet includes header contain CR, number of byte, and CRC type
# Receiver can receive packet with different CR and packet parameters in explicit header mode
print("Set packet parameters:\n\tExplicit header type\n\tPreamble length = 12\n\tPayload Length = 15\n\tCRC on")

# Explicit header mode
headerType = LoRa.HEADER_EXPLICIT

# Set preamble length to 12
preambleLength = 12

# Initialize payloadLength to 15
payloadLength = 15

# Set CRC enable
crcType = True
LoRa.setLoRaPacket(headerType, preambleLength, payloadLength, crcType)


# Set syncronize word for public network (0x3444)
print("Set syncronize word to 0x3444")
LoRa.setSyncWord(0x3444)

print("\n-- LoRa Transmitter --\n")


# Initialize I2C bus
bus = smbus.SMBus(1) 	# or bus = smbus.SMBus(0) for older version boards
Device_Address = 0x68   # MPU6050 device address


MPU_Init()

# Load calibration parameters
calibration_params = bme280.load_calibration_params(bus, address)

def celsius_to_fahrenheit(celsius):
    return (celsius * 9/5) + 32

print(" Reading Data of Sensors")


# Transmit message continuously
while True:

    # Read Accelerometer raw value
    acc_x = read_raw_data(ACCEL_XOUT_H)
    acc_y = read_raw_data(ACCEL_YOUT_H)
    acc_z = read_raw_data(ACCEL_ZOUT_H)

    # Read Gyroscope raw value
    gyro_x = read_raw_data(GYRO_XOUT_H)
    gyro_y = read_raw_data(GYRO_YOUT_H)
    gyro_z = read_raw_data(GYRO_ZOUT_H)

    # Full scale range +/- 250 degree/C as per sensitivity scale factor
    Ax = acc_x/16384.0
    Ay = acc_y/16384.0
    Az = acc_z/16384.0
    Gx = gyro_x/131.0
    Gy = gyro_y/131.0
    Gz = gyro_z/131.0

    # print("Gx=%.2f" % Gx, u'\u00b0' + "/s", "\tGy=%.2f" % Gy, u'\u00b0' + "/s", "\tGz=%.2f" %
    #   Gz, u'\u00b0' + "/s", "\tAx=%.2f g" % Ax, "\tAy=%.2f g" % Ay, "\tAz=%.2f g" % Az)
    sleep(1)

    # Read sensor data
    data = bme280.sample(bus, address, calibration_params)

    # Extract temperature, pressure, and humidity
    prs = data.pressure
    hmd = data.humidity

    # Message to transmit
    message = [Gx, Gy, Gz, Ax, Ay, Az, prs, hmd]

    message = [int((val*1e2)+1e2) for val in message]

    #pack_data = struct.pack('!{}f'.format(len(message)), *message)
    messageList = list(message)

    counter = 0
    # print(pack_data)

    # Transmit message and counter
    # write() method must be placed between beginPacket() and endPacket()
    LoRa.beginPacket()
    LoRa.write(messageList, len(messageList))
    LoRa.write([counter], 1)
    LoRa.endPacket()

    # Print message and counter
    print(f"{message}  {counter}")

    # Wait until modulation process for transmitting packet finish
    LoRa.wait()

    # Print transmit time and data rate
    print("Transmit time: {0:0.2f} ms | Data rate: {1:0.2f} byte/s".format(
        LoRa.transmitTime(), LoRa.dataRate()))

    # Don't load RF module with continous transmit
    time.sleep(5)
    counter = (counter + 1) % 256
