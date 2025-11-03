# *****************************************************************************
"""This module is the main module for controlling the Allen Bradley PLC used
to switch I/Os

M. Capotosto
11/2/2025
NSLS-II Diagnostics and Instrumentation"""

import logging
from time import sleep
from pylogix import PLC
from IP_Addresses import PLC_IP


log = logging.getLogger(__name__)


# *************************************************************************
# ******Create Instrument Objects******
plc = PLC()
plc.IPAddress = PLC_IP

# *************************************************************************


# Build tag string for DO1_0 .. DO1_15
def _tag_for(bit: int) -> str:
    return f"DO1_{bit}"


# Initialize all outputs OFF
def plc_init():
    for chan in range(16):
        log.debug(plc.Write(_tag_for(chan), 0))
        sleep(0.05)


# Write helper
def set_do(bit: int, value: bool):
    tag = _tag_for(bit)
    return plc.Write(tag, bool(value))


# ---- Named Outputs ----
def plc_bias(value: bool): return set_do(0, value)   # DO1_0
def plc_gpo0(value: bool): return set_do(1, value)   # DO1_1
def plc_gpo1(value: bool): return set_do(2, value)   # DO1_2
def plc_gpo2(value: bool): return set_do(3, value)   # DO1_3
def plc_gpo3(value: bool): return set_do(4, value)   # DO1_4
def plc_dac_a(value: bool): return set_do(5, value)   # DO1_5
def plc_dac_b(value: bool): return set_do(6, value)   # DO1_6
def plc_dac_c(value: bool): return set_do(7, value)   # DO1_7
def plc_dac_d(value: bool): return set_do(8, value)   # DO1_8
def plc_curr_a(value: bool): return set_do(9, value)   # DO1_9
def plc_curr_b(value: bool): return set_do(10, value)  # DO1_10
def plc_curr_c(value: bool): return set_do(11, value)  # DO1_11
def plc_curr_d(value: bool): return set_do(12, value)  # DO1_12
def plc_fan_1(value: bool): return set_do(13, value)  # DO1_13
def plc_fan_2(value: bool): return set_do(14, value)  # DO1_14
def plc_fan_3(value: bool): return set_do(15, value)  # DO1_15


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    plc_init()
    plc_bias(1)
    sleep(0.2)
    plc_bias(0)
    plc.Close()
