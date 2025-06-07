''' Script is called Static_Thrust_Calculations.py '''

import numpy as np
import matplotlib.pyplot as plt
from math import pi
from scipy.interpolate import interp1d

''' Functions '''
def static_thrust_calculation(propeller_diameters, propeller_pitch, rpms):
    # Following Equation from Electric RC Aircraft Guy
    # https://www.electricrcaircraftguy.com/2013/09/propeller-static-dynamic-thrust-equation.html

    multiplying_term_1 = 1.225 * pi * pow((0.0254 * propeller_diameters), 2) / 4
    multiplying_term_2 = (propeller_diameters / (3.29546 * propeller_pitch))

    velocity_exit_term = rpms * 0.0254 * prop_pitch * (1/60)

    thrust = (multiplying_term_1 * pow(velocity_exit_term, 2)
              * pow(multiplying_term_2, 1.5))

    return thrust


def thrust_rpm_percent_change(input_diameters, input_pitch, input_rpms, percent_change):
    # Reducing the RPM values before passing it to static_thrust_calculation()

    new_rpms = input_rpms * (1 + (percent_change/100))

    changed_thrust \
        = static_thrust_calculation(input_diameters, input_pitch, new_rpms)

    return changed_thrust

def thrust_function(x):
    return -0.19205 * x**2 + 10.9993 * x - 97.28493


''' Main Code '''
# Tested / Original Thrust and RPM values
tested_thrust_diameters = np.array([16, 20, 24, 26])
tested_thrust = np.array([27.92, 44.87, 50.06, 52.66])

# Original RPM Values with Propeller Diameters
tested_rpm = [5573, 4643, 3331]
tested_rpm_diameters = [16, 20, 26]

# Linear Interpolation for RPM Values
datapoints = 200
prop_diameters = np.linspace(12, 30, datapoints)
interp_func = interp1d(tested_rpm_diameters, tested_rpm, kind='linear',
                       fill_value="extrapolate")
interpolated_rpms = interp_func(prop_diameters)

# Propellers with Pitch of 10 inches
prop_pitch = np.full(datapoints, 10.0)

# Calculating Thrust with the Error Regions [+5% to -10%]
thrust_curve \
    = static_thrust_calculation(prop_diameters, prop_pitch, interpolated_rpms)

upper_error = thrust_rpm_percent_change(prop_diameters, prop_pitch,
                                        interpolated_rpms, 5)
lower_error = thrust_rpm_percent_change(prop_diameters, prop_pitch,
                                        interpolated_rpms, -10)

''' Graphing '''
fig_width = 8
fig_height = 6

plt.figure(figsize=(fig_width, fig_height), dpi=300)

# Plotting the thrust curve
plt.plot(prop_diameters, thrust_curve, label='Thrust Curve', color='blue')

# Filling +5% / -10% Error Region
plt.fill_between(prop_diameters, lower_error, upper_error,
                 color='blue', alpha=0.3, label='+5% / -10% Error Region')

# Plot the tested thrust values
plt.scatter(tested_thrust_diameters, tested_thrust, color='green',
            label='Measured Thrust', marker='s')

# Set x-axis ticks and range
plt.xticks(np.arange(14, 30, 2))  # Tick marks every 2 units
plt.xlim(14, 28)  # Set x-axis range
plt.ylim(10, 65)  # Adjust y-axis range

# Labels and title
plt.xlabel('Propeller Diameter [inches]')
plt.ylabel('Static Thrust [Newtons]')
plt.title('Static Thrust vs. Propeller Diameter')
plt.legend()
plt.grid(True)
plt.tight_layout()

# Show the plot
plt.show()



