''' Script is called LoadCell_Sensor_ESP32.py '''
import time
from machine import Pin, Timer, I2C, ADC
from hx711 import HX711  			# Loadcell ADC library
from ina228 import INA228  			# Power Monitor ADC library
import uos							# Library for file system interaction

''' - - - - - Load Cell Setup - - - - - '''
# Variables for the HX711 Amplifier
CHANNEL_A_128 = const(1)
CHANNEL_A_64 = const(3)
CHANNEL_B_32 = const(2)

# I/O Pins
hx711_digitalout = 27
hx711_powerdown_sck = 12

# Initialize HX711 and Calibration Settings
loadcell_driver = HX711(d_out=hx711_digitalout, pd_sck=hx711_powerdown_sck,
                        channel=CHANNEL_A_64)

calibration_factor = 0.000458
calibration_offset = -6

monitor_led = Pin(13, mode=Pin.OUT)

''' - - - - - Pre-allocated Arrays - - - - - '''
max_data_points = 1500			# Set an initial amount of data points
force_values = [0.0] * max_data_points
timestamps = [0.0] * max_data_points

data_index = 0
time_ms = 0

''' - - - - - Timer Callbacks - - - - - '''
# Loadcell Timer Callback
def read_load_cell(timer):
    global data_index, max_data_points, time_ms, sampling_rate

    raw_force = loadcell_driver.read(raw=True)
    calibrated_force = (raw_force * calibration_factor) + calibration_offset

    time_ms = time_ms + sampling_rate

    # Check if within range of storing values
    if data_index < max_data_points:
        # Saving force value and timestamp; then increment
        force_values[data_index] = calibrated_force
        timestamps[data_index] = time_ms / 1000

        print(calibrated_force)

        data_index = data_index + 1

        # Stop logging when reached the end
        if data_index >= max_data_points:
            # Stopping the timers
            load_cell_timer.deinit()
            print("Timers deinitialized. Data collection complete.")

# --- Timer Setup ---
load_cell_timer = Timer(1)

sampling_rate = 50  # ms

''' - - - - - Main Logic - - - - - '''
# Asking user how long they plan on recording sensor data; then calculate the max number of data points
recording_duration = int(input("Enter recording duration (seconds): "))
print(f"Sensor recording will occur for {recording_duration} seconds")
max_data_points = int((recording_duration * 1000) / sampling_rate)

# Proper Pre-Allocation of Lists/Arrays
force_values = [0.0] * max_data_points
timestamps = [0.0] * max_data_points

# Timers for the Loadcell
load_cell_timer.init(period=sampling_rate, mode=Timer.PERIODIC, callback=read_load_cell)

# Keeping the main thread alive and still active /
# not busy constanty checking data_index [which would strain CPU]
while data_index < max_data_points:
    # Sleep for 100 milli-seconds to avoid busy waiting
    time.sleep_ms(25)

# Asking user for the file name to save to
name_of_file = input("Enter filename to save (e.g., thrust_data): ")
filename = f"{name_of_file}.csv"

# --- Save Data ---
try:
    with open(filename, 'w') as file:
        file.write("Timestamp (ms),Force (N)\n")
        for i in range(data_index): # only write the data that was collected
            file.write("{},{} \n".format(timestamps[i], force_values[i]))
    print("Data saved to {}".format(filename))
except OSError as e:
    print("Error saving data:", e)
    with open('Thrust_data.csv', 'w') as file:
        file.write("Timestamp (ms),Force (N)\n")
        for i in range(data_index):
            file.write("{},{} \n".format(timestamps[i]))
    print("Data saved to backup file Thrust_data.csv")

load_cell_timer.deinit()  # Ensure timers are stopped in finally block
