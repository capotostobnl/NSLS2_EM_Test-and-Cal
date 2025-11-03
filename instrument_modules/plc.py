# pylint: disable=broad-except
"""This module is for implementing remote control of an
AB PLC with an OB16 Module installed, configured for
electrometer testing.

M. Capotosto
8/29/2025
NSLS-II Diagnostics and Instrumentation
"""

from time import sleep
from pylogix import PLC


class Plc:
    """PLC Class"""
    def __init__(self, ip_address):
        self.ip_address = ip_address
        self._plc = PLC()
        self._plc.IPAddress = self.ip_address

    def init_outputs(self):
        """Initialize PLC to all outputs OFF"""
        for chan in range(16):
            self._plc.Write(f"DO1_{chan}", 0)
            sleep(0.5)

    def disconnect(self):
        """Gracefully disconnect from PLC"""
        self._plc.Close()

    def read_tag(self, tag_name):
        """Read a tag value back"""
        try:
            read = self._plc.Read(tag_name)
            if read.Status == "Success":
                return read.Value
            else:
                print(f"Error reading tag {tag_name}: {read.Status}")
                return None
        except Exception as e:
            print(f"An error occurred while reading tag {tag_name}: {e}")
            return None

    def write_tag(self, tag_name, tag_value):
        """Write a tag value"""
        try:
            write = self._plc.Write(tag_name, tag_value)
            if write.Status == "Success":
                return write.Value
            else:
                print(f"Error writing tag {tag_name}: {write.Status}")
                return None
        except Exception as e:
            print(f"An error occurred while writing tag {tag_name}: {e}")
            return None
