"""This module is for implementing remote control of Keithley 622x
series AC/DC Precision Current/Voltage Sources.

M. Capotosto
8/29/2025
NSLS-II Diagnostics and Instrumentation
"""

from time import sleep
from instrument_modules.visa_utils import connect_ethernet_instrument

DELAY = 0.01  # 10ms delay


class Keithley6221:
    """Create V/I Source Class"""
    # *************************************************************************
    # ******Initialize Connection******
    def __init__(self, connection_method, address):
        if connection_method == "IP":
            self.device, self.address, self.status = \
                connect_ethernet_instrument(address)
            self.connected_with = 'Ethernet' \
                if self.status == "Connected" else None

    def idn(self):
        """Query the IDN"""
        idn_response = self.device.write("*IDN?")
        return idn_response

    def get_idn(self):
        """Measure resistance"""
        command = "*IDN?"
        idn = self.device.query(command)
        return idn

    # *************************************************************************
    # ******Factory Reset******
    def factory_reset(self):
        """define a FACTORY RESET function"""
        command = "*RST"
        self.device.write(command)
        sleep(5)  # 5 second delay to wait for reset to finish...

    # ************************************************************************
    # Global Commands
    def clear(self):
        """Turn OFF output, and set output level to zero"""
        command = "CLEar"
        self.device.write(command)

    def output(self, output="OFF"):
        """Turn the output ON or OFF"""
        command = f"OUTPut {output}"
        self.device.write(command)
        sleep(1)

    # *************************************************************************
    # DC Current Output Command Set

    def irange(self, irange="0.1"):
        """Set output current range. Use only if not using AUto-Ranging!
        Setting manual range will disable auto ranging

        1.  To select a fixed source range, specify the current output value
        that is going to be sourced. The Model 622x will go to the lowest range
        that can source that value. For example, If you are going to source
        25mA, let <n> = 25e-3. The 100mA range will be selected.

        2.  Selecting a fixed source range disables autorange.
        """
        command = f"CURRent:RANGe {irange}"
        self.device.write(command)
        sleep(1)

    def auto_range(self, autorange="OFF"):
        """Enable or disable autorange, ON or OFF"""
        command = f"CURRent:RANGe:AUTO {autorange}"
        self.device.write(command)
        sleep(1)

    def current(self, current):
        """Set DC current source output level (amps, -105mA to 105mA)"""
        command = f"CURRent {current}"
        self.device.write(command)
        sleep(1)

    def compliance(self, compliance="0"):
        """Set compliance voltage, 100mV to 105V"""
        command = f"CURRent:COMPliance {compliance}"
        self.device.write(command)
        sleep(1)

