# pylint: disable=broad-except
"""This module is for carrying out DAC voltage testing

M. Capotosto
9/1/2025
NSLS-II Diagnostics and Instrumentation
"""
from time import sleep

from instrument_modules.plc import Plc
from instrument_modules.keithley_2100 import Keithley2100
from instrument_modules.electrometer import Electrometer


# from instrument_modules.plc import Plc
# Test: Set DAC to 10V, verify output is 10V+/-0.25V. Set to -10V, verify.

# *****************************************************************************
# ******Pass/Fail Constants******
V_POS_LIM_HIGH = 10.25
V_POS_LIM_LOW = 9.75

V_ZERO_LIM_HIGH = 0.25
V_ZERO_LIM_LOW = -0.25

V_NEG_LIM_HIGH = -10.25
V_NEG_LIM_LOW = -9.75
# *****************************************************************************


def _test_dac_setpoint(dmm, em, pv_name, setpoint, lim_low, lim_high):
    """
    A helper function to set the PV, measure the voltage,
    and return the result
    """
    em.put_pv_value(pv_name, setpoint)
    sleep(1)
    measured_voltage = round(dmm.meas_dcv(), 3)

    # Check if the measured voltage is within the specified limits
    test_passed = lim_high <= measured_voltage <= lim_low

    return {
        "setpoint": setpoint,
        "measured_voltage": measured_voltage,
        "test_passed": test_passed
    }


def dac_test(plc: Plc, dmm: Keithley2100, em: Electrometer):
    """Set and measure DAC channel voltages"""
    print("Initializing DAC test...")

    # Make sure all CRs are OFF
    for i in range(16):
        try:
            tag_val = plc.read_tag(f"CR{i}")
            if tag_val != 0:
                plc.write_tag(f"CR{i}", 0)
            sleep(0.01)
        except Exception as e:
            print(f"Error during CR initialization: {e}")

    # Dictionary to store all test results
    results = {}

    # Use the specific PV names for each channel
    dac_pvs = ["DAC-Chan1-Sp", "DAC-Chan2-Sp", "DAC-Chan3-Sp", "DAC-Chan4-Sp"]

    # Iterate through all four DAC channels using their full PV name
    # Add a loop counter, starting at 5, for CR5 through 8 for DAC A to D
    for i, pv_name in enumerate(dac_pvs, start=5):
        results[pv_name] = {}

        # Enable CR for DAC to DMM Connection
        plc.write_tag(f"CR{i}", 1)
        sleep(0.01)

        # Test for 10V nominal
        print(f"Testing {pv_name} 10V setpoint...")
        results[pv_name]["10V"] = _test_dac_setpoint(
            dmm, em, pv_name, 10, V_POS_LIM_LOW, V_POS_LIM_HIGH
        )
        print(f"PV {pv_name} measured "
              f"{results[pv_name]['10V']['measured_voltage']}"
              f"V. Test passed: "
              f"{results[pv_name]['10V']['test_passed']}")

        # Test for -10V nominal
        print(f"Testing {pv_name} -10V setpoint...")
        results[pv_name]["-10V"] = _test_dac_setpoint(
            dmm, em, pv_name, -10, V_NEG_LIM_LOW, V_NEG_LIM_HIGH
        )
        print(f"PV {pv_name} measured "
              f"{results[pv_name]['-10V']['measured_voltage']}V. Test passed: "
              f"{results[pv_name]['-10V']['test_passed']}")

        # Test for 0V nominal
        print(f"Testing {pv_name} 0V setpoint...")
        results[pv_name]["0V"] = _test_dac_setpoint(
            dmm, em, pv_name, 0, V_ZERO_LIM_LOW, V_ZERO_LIM_HIGH
        )
        print(f"PV {pv_name} measured "
              f"{results[pv_name]['0V']['measured_voltage']}V. Test passed: "
              f"{results[pv_name]['0V']['test_passed']}")

        # Disable CR for DAC to DMM Connection
        plc.write_tag(f"CR{i}", 0)
        sleep(0.01)

    print("\nDAC test complete.")
    print("-"*75)
    return results
