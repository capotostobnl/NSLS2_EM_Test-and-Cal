# pylint: disable=broad-except
"""This module is for carrying out
VOLTAGE daughter board calibration

M. Capotosto
9/1/2025
NSLS-II Diagnostics and Instrumentation
"""

import numpy as np
import matplotlib.pyplot as plt
from time import sleep
import epics

from instrument_modules.plc import Plc
from instrument_modules.keithley_2100 import Keithley2100
from instrument_modules.keithley_6221 import Keithley6221
from instrument_modules.electrometer import Electrometer
from main import PV_PREFIX


# *************************************************************************
# ******Initialize PVs******
Rpv = epics.PV(PV_PREFIX+"ADC:Range:"+chan+"-SP")
Gpv = epics.PV(PV_PREFIX+"ADC:"+chan+":Gain-SP")
Opv = epics.PV(PV_PREFIX+"ADC:"+chan+":Offset-SP")
Spv = epics.PV(PV_PREFIX+"SA:"+chan+"-I")


dac_pvs = ["DAC-Chan1-Sp", "DAC-Chan2-Sp", "DAC-Chan3-Sp", "DAC-Chan4-Sp"]


def initialize_voltage_cal(em, plc: Plc):
    """Initialize PLC Outputs to OFF, DACs to 0V"""

    em.put_pv_value(pv_name, setpoint)
