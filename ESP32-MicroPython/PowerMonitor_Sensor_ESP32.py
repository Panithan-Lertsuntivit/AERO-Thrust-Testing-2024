''' Script is called PowerMonitor_Sensor_ESP32.py '''
from machine import I2C, Pin
import time
from ina228 import INA228

# Initial values
matek_shunt_resistor = 200 * pow(10, -6)    # Shunt resistor: 200 micro-Ohms

i2c = I2C(0, scl=Pin(1), sda=Pin(0), freq=100000)

# Creating INA228 Object, specifying device i2c address
ina = INA228(i2c, address=0x45, shunt_resistance=matek_shunt_resistor)

ina.initialize()

while True:
    # Read from MATEK - INA228
    shunt_voltage1 = ina.read_shunt_voltage()
    current1 = ina.read_current()
    power1 = ina.read_power()

    print("Shunt Voltage: {:.4f} V".format(shunt_voltage1))
    print("Current: {:.4f} A".format(current1))
    print("Power: {:.4f} W".format(power1))
    print("--------------------")

    time.sleep(1)
