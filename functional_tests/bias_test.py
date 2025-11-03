# pylint: disable=broad-except
"""This module is for carrying out bias voltage testing

M. Capotosto
9/1/2025
NSLS-II Diagnostics and Instrumentation
"""
from time import sleep

from instrument_modules.plc import Plc
from instrument_modules.keithley_2100 import Keithley2100
from instrument_modules.electrometer import Electrometer


# from instrument_modules.plc import Plc
# Test: Set V_Bias to 10V, verify output is 10V+/-0.25V. Set to -10V, verify.

# *****************************************************************************
# ******Pass/Fail Constants******
V_POS_LIM_HIGH = 10.25
V_POS_LIM_LOW = 9.75

V_ZERO_LIM_HIGH = 0.25
V_ZERO_LIM_LOW = -0.25

V_NEG_LIM_HIGH = -10.25
V_NEG_LIM_LOW = -9.75
# *****************************************************************************


def _test_voltage_setpoint(dmm, em, setpoint, lim_low, lim_high):
    """
    A helper function to set the PV, measure the voltage,
    and return the result
    """
    em.put_pv_value("bias_v_sp", setpoint)
    sleep(1)
    measured_voltage = round(dmm.meas_dcv(), 3)

    # Check if the measured voltage is within the specified limits
    test_passed = lim_high <= measured_voltage <= lim_low

    return {
        "setpoint": setpoint,
        "measured_voltage": measured_voltage,
        "test_passed": test_passed
    }


def v_bias_test(plc: Plc, dmm: Keithley2100, em: Electrometer):
    """Set and measure V_Bias"""
    # Make sure all CRs are OFF
    for i in range(16):
        tag_val = plc.read_tag(f"CR{i}")
        if tag_val != 0:
            plc.write_TAG(f"CR{i}, 0")
        sleep(0.01)

    # Enable CR for Bias to DMM Connection
    plc.write_tag("CR0", 1)
    sleep(0.01)

    # Set Bias Voltage Output

    # Dictionary to store all test results
    results = {}

    # Test for 0V nominal
    print("Testing 0V setpoint...")
    results["0V"] = _test_voltage_setpoint(
        dmm, em, 0, V_ZERO_LIM_LOW, V_ZERO_LIM_HIGH
    )
    print(f"Measured {results['0V']['measured_voltage']}V. Test passed: "
          f"{results['0V']['test_passed']}")

    # Test for 10V nominal
    print("Testing 10V setpoint...")
    results["10V"] = _test_voltage_setpoint(
        dmm, em, 10, V_POS_LIM_LOW, V_POS_LIM_HIGH
    )
    print(f"Measured {results['10V']['measured_voltage']}V. Test passed: "
          f"{results['10V']['test_passed']}")

    # Test for -10V nominal
    print("Testing -10V setpoint...")
    results["-10V"] = _test_voltage_setpoint(
        dmm, em, -10, V_NEG_LIM_LOW, V_NEG_LIM_HIGH
    )
    print(f"Measured {results['-10V']['measured_voltage']}V. Test passed: "
          f"{results['-10V']['test_passed']}")

    # Disable CR for Bias to DMM Connection
    plc.write_tag("CR0", 0)
    sleep(0.01)
    print("\nBias test complete.")
    print("-" * 75)
    return results
