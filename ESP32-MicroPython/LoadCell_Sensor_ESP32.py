''' Script is called LoadCell_Sensor_ESP32.py '''
import machine
import time
from machine import Pin, Timer
from hx711 import HX711
import uos				# For saving data points to csv file

'''Variables for the HX711 Amplifier'''
CHANNEL_A_128 = const(1)
CHANNEL_A_64 = const(3)
CHANNEL_B_32 = const(2)

'''HX 711 Pinouts'''
hx711_digitalout = 27
hx711_powerdown_sck = 12

# Initialize HX711 and LED
driver = HX711(d_out=hx711_digitalout, pd_sck=hx711_powerdown_sck,
               channel=CHANNEL_A_64)

monitor_led = Pin(13, mode=Pin.OUT)

'''Defining Test Duration, Sampling Rate and Calibration'''
test_time = 45						# Units in [seconds]
test_time_ms = test_time * 1000
sampling_rate = 100					# Units in [ms]

num_data_points = int(test_time_ms / sampling_rate) + 2

# Calibration Factor will be multiplied, Offset is added
calibration_factor = 0.000458
calibration_offset = -6

force_values = [0] * num_data_points

i = 0

# Function to read force/weight and apply the calibration factor
def read_force():
    monitor_led(1)
    raw_value = driver.read(raw=True)
    force_calibrated = (raw_value * calibration_factor) + calibration_offset
    return force_calibrated

# Function to be called periodically by a timer
def loadcell_reading(Timer):
    global i
    force = read_force()            # Read the calibrated weight/force
    force_values[i] = force
    print(f"Force: {force} Newtons")   # Units: Newton
    monitor_led(0)
    i = i + 1

# Timer setup
loadcell_timer = Timer(1)

# Period is in units of [ms]
loadcell_timer.init(period=sampling_rate, mode=loadcell_timer.PERIODIC,
                    callback=loadcell_reading)

time.sleep(test_time)
loadcell_timer.deinit()

print('All timers and PWM deinitialized.')

# Opening a file in write mode
with open('Thrust_values.csv', 'w') as file:
    for value in force_values:
        file.write(f"{value} \n")
        