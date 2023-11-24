import time
import serial

lora = serial.Serial(port='/dev/ttyS0',baudrate = 9600,parity=serial.PARITY_NONE,stopbits=serial.STOPBITS_ONE,bytesize=serial.EIGHTBITS,timeout=1)

while True:
    data_read = lora.readline()#read data from other lora
    print(data_read)
    time.sleep(0.2)