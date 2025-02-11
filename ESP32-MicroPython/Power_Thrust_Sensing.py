''' Script is called Power_Thrust_Sensing.py '''
import time
from machine import Pin, Timer, I2C, ADC
from hx711 import HX711  			# Loadcell ADC library
from ina228 import INA228  			# Power Monitor ADC library
import uos							# Library for file system interaction

import network
import espnow						# For streaming values to receiver


''' - - - - - Initializing ESP-NOW  - - - - - '''
# A WLAN interface must be active to send()/recv()
sta = network.WLAN(network.WLAN.IF_STA)  # Or network.WLAN.IF_AP
sta.active(True)

e = espnow.ESPNow()
e.active(True)
receiver_esp = b'\x14\x2b\x2f\xaf\x58\x58'   	# MAC address of peer's wifi interface
e.add_peer(receiver_esp)      					# Must add_peer() before send()

monitor_led = Pin(13, mode=Pin.OUT)

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

''' - - - - - INA228 Setup - - - - - '''
# MATEK INA Properties
matek_shunt_resistor = 200 * pow(10, -6)

# Initializing I2C and INA228
i2c = I2C(0, scl=Pin(14), sda=Pin(22), freq=100000)
ina = INA228(i2c, address=0x45, shunt_resistance=matek_shunt_resistor)
ina.initialize()

''' - - - - - Pre-allocated Arrays - - - - - '''
max_data_points = 1500			# Set an initial amount of data points
force_values = [0.0] * max_data_points
voltage_values = [0.0] * max_data_points
current_values = [0.0] * max_data_points
power_values = [0.0] * max_data_points
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
        
        print(data_index)
        
        data_index = data_index + 1
        
        # Stop logging when reached the end
        if data_index >= max_data_points:
            # Stopping the timers
            load_cell_timer.deinit()
            power_monitor_timer.deinit()
            espnow_timer.deinit()
            
            print("Timers deinitialized. Data collection complete.")        
        

# MATEK Power Monitor Timer Callback
def read_power_monitor(timer):
    global data_index, max_data_points
    
    voltage = ina.read_bus_voltage()
    current = ina.read_current()
    power = voltage * current
    
    # Check if within range of storing values
    if data_index < max_data_points:
        # Saving voltage, current and power values
        voltage_values[data_index] = voltage
        current_values[data_index] = current
        power_values[data_index] = power
        
# ESPNOW Timer Callback
def espnow_transmit(timer):
    # Creating string message
    if data_index < max_data_points:
        force = force_values[data_index - 1]
        voltage = voltage_values[data_index - 1]
        current = current_values[data_index - 1]
        power = power_values[data_index - 1]
        
        message = (f"{force:7.2f} N, {voltage:7.2f} V, "
                   f"{current:7.2f} A, {power:7.2f} W")
    else:
        message = f"Finished Data Collection"
        
    # Transmitting message
    e.send(receiver_esp, message)
        

# --- Timer Setup ---
power_monitor_timer = Timer(0)
load_cell_timer = Timer(1)

espnow_timer = Timer(2)

sampling_rate = 50  # ms

''' - - - - - Main Logic - - - - - '''
# Asking user how long they plan on recording sensor data; then calculate the max number of data points
recording_duration = int(input("Enter recording duration (seconds): "))
print(f"Sensor recording will occur for {recording_duration} seconds")
max_data_points = int((recording_duration * 1000) / sampling_rate)

# Proper Pre-Allocation of Lists/Arrays
force_values = [0.0] * max_data_points
voltage_values = [0.0] * max_data_points
current_values = [0.0] * max_data_points
power_values = [0.0] * max_data_points
timestamps = [0.0] * max_data_points

# Timers for the Power Monitor, Loadcell, and ESPNOW
e.send(receiver_esp, "Starting . . . ")

power_monitor_timer.init(period=sampling_rate, mode=Timer.PERIODIC, callback=read_power_monitor)
load_cell_timer.init(period=sampling_rate, mode=Timer.PERIODIC, callback=read_load_cell)
espnow_timer.init(period=sampling_rate, mode=Timer.PERIODIC, callback=espnow_transmit)


# Keeping the main thread alive and still active /
# not busy constanty checking data_index [which would strain CPU]
while data_index < max_data_points:
    # Sleep for 100 milli-seconds to avoid busy waiting
    time.sleep_ms(100) 

# Asking user for the file name to save to
name_of_file = input("Enter filename to save (e.g., thrust_data): ")
filename = f"{name_of_file}.csv"


# --- Save Data ---
try:
    with open(filename, 'w') as file:
        file.write("Timestamp (ms),Force (N),Voltage (V),Current (A),Power (W)\n")
        for i in range(data_index): # only write the data that was collected
            file.write("{},{},{},{},{}\n".format(timestamps[i], force_values[i], voltage_values[i], current_values[i], power_values[i]))
    print("Data saved to {}".format(filename))
except OSError as e:
    print("Error saving data:", e)

load_cell_timer.deinit()  # Ensure timers are stopped in finally block
power_monitor_timer.deinit()
espnow_timer.deinit()

