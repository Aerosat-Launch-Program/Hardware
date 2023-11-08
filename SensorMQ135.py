import time
from pySerialTransfer import pySerialTransfer as pst

# Create an instance of the SerialTransfer class
link = pst.SerialTransfer('COMX')  # Replace 'COMX' with the appropriate COM port

# Define your calibration values for different gases
CALIBRATION = {
    'NH3': 0.2,     # Calibration value for NH3
    'NOx': 0.3,     # Calibration value for NOx
    'Alcohol': 0.5, # Calibration value for Alcohol
    'Benzene': 0.4, # Calibration value for Benzene
    'Smoke': 0.6,   # Calibration value for Smoke
    'CO2': 0.7      # Calibration value for CO2
}

def read_mq135_gas_concentration():
    try:
        with link:
            while True:
                link.send([(8 + MQ135_CHANNEL) << 4])
                link.flush()
                link.send(MQ135_CHANNEL)
                link.flush()

                # Receive data
                gas_concentration = link.recv()
                
                # Estimate gas concentrations based on calibration values
                gas_concentration_nh3 = gas_concentration * CALIBRATION['NH3']
                gas_concentration_nox = gas_concentration * CALIBRATION['NOx']
                gas_concentration_alcohol = gas_concentration * CALIBRATION['Alcohol']
                gas_concentration_benzene = gas_concentration * CALIBRATION['Benzene']
                gas_concentration_smoke = gas_concentration * CALIBRATION['Smoke']
                gas_concentration_co2 = gas_concentration * CALIBRATION['CO2']
                
                # Print the estimated gas concentrations
                print("NH3 Concentration: {} ppm".format(gas_concentration_nh3))
                print("NOx Concentration: {} ppm".format(gas_concentration_nox))
                print("Alcohol Concentration: {} ppm".format(gas_concentration_alcohol))
                print("Benzene Concentration: {} ppm".format(gas_concentration_benzene))
                print("Smoke Concentration: {} ppm".format(gas_concentration_smoke))
                print("CO2 Concentration: {} ppm".format(gas_concentration_co2))
                
                time.sleep(2)  # Adjust the sleep time as needed

    except KeyboardInterrupt:
        pass

if __name__ == '__main__':
    read_mq135_gas_concentration()
