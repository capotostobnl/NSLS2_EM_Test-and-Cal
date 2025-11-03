# pylint: disable=broad-except
"""This module is for carrying out Fan Header
Voltage measurements as part of EM Acceptance Tests

M. Capotosto
9/3/2025
NSLS-II Diagnostics and Instrumentation
"""
from time import sleep

from instrument_modules.plc import Plc
from instrument_modules.keithley_2100 import Keithley2100

# *****************************************************************************
# ******Pass/Fail Constants******
PIN_1_V_LOW = -0.1
PIN_1_V_HIGH = 0.1

PIN_2_V_LOW = 4.75
PIN_2_V_HIGH = 5.25

PIN_3_V_LOW = 4.75
PIN_3_V_HIGH = 5.25
# *****************************************************************************


def fan_header_voltage_test(plc: Plc, dmm: Keithley2100):
    """
    Measures the voltage on fan header pins (CR13, CR14, and CR15) and
    checks if they pass or fail.
    """

    print("Initializing fan header voltage test...")

    # Dictionary to store all test results
    results = {}

    # Define the pins to be tested and their corresponding pass/fail limits
    pins_to_test = {
        "CR13": {"low": PIN_1_V_LOW, "high": PIN_1_V_HIGH},
        "CR14": {"low": PIN_2_V_LOW, "high": PIN_2_V_HIGH},
        "CR15": {"low": PIN_3_V_LOW, "high": PIN_3_V_HIGH},
    }

    # Iterate through the pins and their limits
    for pin_name, limits in pins_to_test.items():
        print(f"\nTesting fan header pin: {pin_name}...")

        try:
            # Enable the CR relay to connect the pin to the DMM
            plc.write_tag(pin_name, 1)
            sleep(0.5)  # Wait for the relay to settle

            # Measure the voltage and round to 3 decimal places
            measured_voltage = round(dmm.meas_dcv(), 3)

            # Check if the measured voltage is within the specified limits
            test_passed = (limits["low"] <= measured_voltage <= limits["high"])

            # Store the results
            results[pin_name] = {
                "measured_voltage": measured_voltage,
                "test_passed": test_passed
            }

            # Print the results for the current pin
            print(
                f"Fan header pin {pin_name} measured "
                f"{results[pin_name]['measured_voltage']}V. "
                f"Test passed: {results[pin_name]['test_passed']}"
            )

        except Exception as e:
            # Handle any errors that occur during the test
            print(f"Error while testing {pin_name}: {e}")
            results[pin_name] = {
                "measured_voltage": None,
                "test_passed": False
            }

        finally:
            # Ensure the CR relay is disabled, even if an error occurred
            plc.write_tag(pin_name, 0)
            sleep(0.1)

    print("\nFan header voltage test complete.")
    print("-"*75)
    return results
