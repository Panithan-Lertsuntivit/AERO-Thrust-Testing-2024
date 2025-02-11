# ina228.py (Library File)

from machine import I2C

class INA228:
    def __init__(self, i2c, address=0x45, shunt_resistance=0.0002):
        # shunt_resistance is a parameter
        self.i2c = i2c
        # i2c address - default value assumed to be 69
        # [based on MATEK Power Module]
        self.address = address
        # Shunt resistance - default value assumed to be 200 micro-Ohms
        self.shunt_resistance = shunt_resistance

        # INA228 Registers
        self.INA228_CONFIG = 0x00
        self.INA228_SHUNT_VOLTAGE = 0x01
        self.INA228_BUS_VOLTAGE = 0x02
        self.INA228_POWER = 0x03
        self.INA228_CURRENT = 0x04
        self.INA228_CALIBRATION = 0x05
        self.INA228_MASK_ENABLE = 0x06
        self.INA228_ALERT_LIMIT = 0x07

        self.current_LSB = None  # Will be calculated during initialization
        self.power_LSB = None    # Will be calculated during initialization

    def _write_register(self, register, value):
        self.i2c.writeto_mem(self.address, register, value.to_bytes(2, 'big'),
                             addrsize=8)

    def _read_register(self, register):
        return int.from_bytes(self.i2c.readfrom_mem(self.address, register, 2,
                                                    addrsize=8), 'big')

    def read_shunt_voltage(self):
        raw = self._read_register(self.INA228_SHUNT_VOLTAGE)
        return raw * 2.5e-6  # Shunt voltage in Volts

    def read_bus_voltage(self):
        raw = self._read_register(self.INA228_BUS_VOLTAGE)
        return (raw >> 3) * 1.25e-3  # Bus voltage in Volts

    def read_current(self):
        raw = self._read_register(self.INA228_CURRENT)
        return raw * self.current_LSB if self.current_LSB else 0.0  # Current in Amps

    def read_power(self):
        raw = self._read_register(self.INA228_POWER)
        return raw * self.power_LSB if self.power_LSB else 0.0  # Power in Watts

    def initialize(self, config=0x6000):
        self._write_register(self.INA228_CONFIG, config)

        # Calculate Current and Power LSBs using the stored shunt_resistance
        cal = self._read_register(self.INA228_CALIBRATION)
        self.current_LSB = (0.00512 / (self.shunt_resistance * 32768))
        self.power_LSB = self.current_LSB * 25

        # Program the calibration register
        calibration_value = int(0.00512 / (self.shunt_resistance * 0.00002048))
        self._write_register(self.INA228_CALIBRATION, calibration_value)
