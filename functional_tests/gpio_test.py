# pylint: disable=broad-except
"""This module is for carrying out GPIO testing

M. Capotosto
9/1/2025
NSLS-II Diagnostics and Instrumentation

Overview
--------
Two primary test routines are implemented:

1. gpio_out_test()
   - Drives each GPIO output channel (OUT0–OUT3) to LOW and HIGH states
     via EPICS PV writes.
   - Enables the corresponding PLC-controlled cross-connect relay to route the
     output signal to the Keithley 2100 DMM.
   - Measures the actual voltage level and validates it against configurable
     tolerance limits for LOW (≈0 V) and HIGH (≈5 V).
   - Returns a structured dictionary summarizing pass/fail status and measured
     voltages for each channel.

2. gpio_input_test()
   - Sequentially drives each GPIO output channel and reads its associated
     input status PV (Status-I.B0–B3).
   - Confirms that the digital input readback correctly reflects the output
     logic level.
   - Produces a per-channel summary of expected vs. observed input states.

"""
from time import sleep

from plc import PLC
from electrometer import Electrometer

from instrument_module.keithley_2100 import Keithley2100



# *****************************************************************************
# ******Pass/Fail Constants******
V_POS_LIM_HIGH = 5.25
V_POS_LIM_LOW = 4.75

V_ZERO_LIM_HIGH = 0.25
V_ZERO_LIM_LOW = -0.25


def _test_gpio_out_setpoint(dmm, em, pv_name, setpoint, lim_low, lim_high):
    """
    A helper function to set the PV, measure the voltage,
    and return the result
    """
    em.put_pv_value(pv_name, setpoint)
    sleep(1)
    measured_voltage = round(dmm.meas_dcv(), 3)

    # Check if the measured voltage is within the specified limits
    test_passed = lim_low <= measured_voltage <= lim_high

    return {
        "setpoint": setpoint,
        "measured_voltage": measured_voltage,
        "test_passed": test_passed
    }


def gpio_out_test(plc: PLC, dmm: Keithley2100, em: Electrometer):
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
    gpio_out_pvs = ["OUT0-Cmd", "OUT1-Cmd", "OUT2-Cmd", "OUT3-Cmd"]
    # Iterate through all four GPIO Output channels using their full PV name
    # Add a loop counter, starting at 1, for CR1 through 4 for bgpout0-3
    for i, pv_name in enumerate(gpio_out_pvs, start=1):
        results[pv_name] = {}

        # Enable CR for GPIO Output to DMM Connection
        plc.write_tag(f"CR{i}", 1)
        sleep(0.01)

        # Test for LOW output...
        print(f"Testing {pv_name} LOW setpoint...")
        results[pv_name]["LOW"] = _test_gpio_out_setpoint(
            dmm, em, pv_name, 0, V_ZERO_LIM_LOW, V_ZERO_LIM_HIGH
        )
        print(f"PV {pv_name} measured "
              f"{results[pv_name]['LOW']['measured_voltage']}V. Test passed: "
              f"{results[pv_name]['LOW']['test_passed']}")

        # Test for HIGH output...
        print(f"Testing {pv_name} HIGH output...")
        results[pv_name]["HIGH"] = _test_gpio_out_setpoint(
            dmm, em, pv_name, 1, V_POS_LIM_LOW, V_POS_LIM_HIGH
        )
        print(f"PV {pv_name} measured "
              f"{results[pv_name]['HIGH']['measured_voltage']}V. Test passed: "
              f"{results[pv_name]['HIGH']['test_passed']}")

        # Return all I/Os to LOW
        _ = _test_gpio_out_setpoint(
            dmm, em, pv_name, 0, V_ZERO_LIM_LOW, V_ZERO_LIM_HIGH
        )

        # Disable CR for GPIO Output to DMM Connection
        plc.write_tag(f"CR{i}", 0)
        sleep(0.01)

    print("\nGPIO test complete.")
    print("-"*75)
    return results


def gpio_input_test(em: Electrometer, plc: PLC):
    """Test GPIO Inputs"""
    gpio_input_pvs = ["Status-I.B0", "Status-I.B1", "Status-I.B2",
                      "Status-I.B3"]
    gpio_out_pvs = ["OUT0-Cmd", "OUT1-Cmd", "OUT2-Cmd", "OUT3-Cmd"]

    results = {}

    for i, pv_name in enumerate(gpio_input_pvs):
        results[pv_name] = {}

        output_pv_name = gpio_out_pvs[i]

        # Test for LOW output (0) and read GPIO Input
        em.put_pv_value(output_pv_name, 0)
        sleep(0.5)
        results[pv_name]["LOW"] = em.get_pv_value(pv_name)
        low_test_passed = not results[pv_name]["LOW"]

        # Test for HIGH output (1) and read GPIO Input
        em.put_pv_value(output_pv_name, 1)
        sleep(0.5)
        results[pv_name]["HIGH"] = em.get_pv_value(pv_name)
        high_test_passed = results[pv_name]["HIGH"]

        # Return output to 0
        em.put_pv_value(output_pv_name, 0)

        # Record the overall test result for this channel
        results[pv_name]["overall_test_passed"] = low_test_passed and \
            high_test_passed

        print(f"Testing PV {pv_name} with output {output_pv_name}...")
        print(f"LOW setpoint: Input read {results[pv_name]['LOW']}. "
              f"Test passed: {low_test_passed}")
        print(f"HIGH setpoint: Input read {results[pv_name]['HIGH']}. Test "
              f"passed: {high_test_passed}")
        print(f"Overall test for {pv_name} passed: "
              f"{results[pv_name]['overall_test_passed']} \n")

        print("GPIO Input test complete.")
        print("-"*75)
        return results
