''' Script is called PowerMonitor_Sensor_ESP32.py '''
from machine import I2C, Pin
import time
from ina228 import INA228

# Initial values
matek_shunt_resistor = 200 * pow(10, -6)    # Shunt resistor: 200 micro-Ohms

i2c = I2C(0, scl=Pin(14), sda=Pin(22), freq=100000)

# Creating INA228 Object, specifying device i2c address
ina = INA228(i2c, address=0x45, shunt_resistance=matek_shunt_resistor)

ina.initialize()


while True:
    # Read from MATEK - INA228 (Raw Values)
    bus_voltage = ina.read_bus_voltage()
    current = ina.read_current()
    power = ina.read_power()

    print("Bus Voltage: {:.4f} V".format(bus_voltage))
    print("Current: {:.4f} A".format(current))
    print("Power: {:.4f} W".format(power))
    print("--------------------")

    time.sleep(1)