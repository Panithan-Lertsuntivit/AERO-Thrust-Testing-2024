import machine
import time
from machine import Pin, Timer
from hx711 import HX711
import uos				# For saving data points to csv file

'''Variables for the HX711 Amplifier'''
CHANNEL_A_128 = const(1)
CHANNEL_A_64 = const(3)
CHANNEL_B_32 = const(2)

'''Pinouts'''
hx711_digitalout = 27
hx711_powerdown_sck = 12

# Initialize HX711 and LED
driver = HX711(d_out = hx711_digitalout, pd_sck = hx711_powerdown_sck, channel = CHANNEL_A_64)

monitor_led = Pin(13, mode=Pin.OUT)

# Define your calibration factor and variables
test_time = 200						# Units in seconds
test_time_ms = test_time * 1000
sampling_rate = 500					# Units in [ms]

num_data_points = test_time_ms / sampling_rate

calibration_factor = 1

force_values = [0] * (2 * num_data_points)

i = 0

# Function to read force/weight and apply the calibration factor
def read_force():
    monitor_led(1)
    raw_value = driver.read(raw=True)
    force_calibrated = raw_value
    return force_calibrated

# Function to be called periodically by a timer
def loadcell_reading(Timer):
    global i
    force = read_force()  # Read the calibrated weight
    force_values[i] = force
#     force_values.append(force)
#     print(f"Force: {force} kg-f")
    monitor_led(0)
    i = i + 1

# Timer setup
loadcell_timer = Timer(1)
# Period is in units of [ms]
loadcell_timer.init(period = sampling_rate, mode = loadcell_timer.PERIODIC, callback = loadcell_reading)

time.sleep(100)
loadcell_timer.deinit()

print('All timers and PWM deinitialized.')

# Opening a file in write mode
with open('Thrust_values.csv', 'w') as file:
    for value in force_values:
        print(value)
        file.write(f"{value} \n")
        
        
        