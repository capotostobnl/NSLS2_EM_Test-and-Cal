# flake8: noqa E501
# pylint: disable=broad-except
# *****************************************************************************
"""This module is the main module for testing NSLS-II PicoZed Electrometers, Rev. D.
With or without the voltage daughter card. 

M. Capotosto
8/29/2025
NSLS-II Diagnostics and Instrumentation"""

# *****************************************************************************
# ******IMPORTS******
import csv
import sys
import os
from time import sleep
from datetime import datetime

from directory_manager import ProjectDirectoryManager as dirman

from instrument_modules.electrometer import Electrometer
from instrument_modules.plc import Plc
from instrument_modules.rigol_dp800 import DP800
from instrument_modules.keithley_2100 import Keithley2100
from instrument_modules.keithley_6221 import Keithley6221

from functional_tests import bias_test
from functional_tests import dac_test
# *****************************************************************************


# *****************************************************************************
# ******CONSTANTS******

# *****************************************************************************
PV_PREFIX = ""

# *************************************************************************
# ******Set Insturment IP Addresses******

PSU_IP_ADDRESS = "10.0.142.1"  # Set PSU IP Address here
DMM_ADDRESS = "USB0::0x05E6::0x2100::8020357::INSTR"
I_SOUR_ADDRESS = ""
PLC_IP_ADDRESS = ""

# *************************************************************************

# *************************************************************************
# ******Create Instrument Objects******

psu = DP800(connection_method="IP", address=PSU_IP_ADDRESS)
dmm = Keithley2100(connection_method="USB", address=DMM_ADDRESS)
i_sour = Keithley6221(connection_method="IP", address=I_SOUR_ADDRESS)
plc = Plc(PLC_IP_ADDRESS)
em = Electrometer()
# *************************************************************************

# *************************************************************************
# ******Get Tech Info******
def get_test_tech_info():
    """Acquire static test technician information"""
    while True:
        tester_name_l = input("Enter your name: ")
        tester_life_l = input("Enter your Life #: ")

        if input(f"You entered: {tester_name_l}, {tester_life_l}, "
                 f"is this correct? <Y/N>: ").lower() == "y":
            return tester_name_l, tester_life_l

def save_test_tech_info(raw_data_path_l, dut_sn_l, tester_name_l, tester_life_l):
    """Save test technician info"""

    file_path_l = os.path.join(raw_data_path_l, f"{dut_sn_l}_Technician_Data.csv")

    data = [
        ["tester_name", "tester_life"],
        [tester_name_l, tester_life_l]
    ]

    try:
        # Open the file in write mode (will create the file if it doesn't exist)
        with open(file_path_l, mode='w', newline='', encoding='utf-8') as file_l:
            writer = csv.writer(file_l)
            # Write the header and the data rows
            writer.writerows(data)

        print(f"Tester data saved to: {file_path_l}")
        return True

    except Exception as e:
        print(f"Error writing to {file_path_l}: {e}")
        return False
# *************************************************************************

# *************************************************************************
# ******Get DUT Info******
def get_dut_info():
    """Acquire eib Serial No./Type Information"""
    while True:
        dut_sn_l = input("Enter DUT S/N: ")
        if input(f"You entered: {dut_sn_l}, is this correct? <Y/N>: ") \
                in ("Y", "y"):
            return dut_sn_l

# *************************************************************************

# ******Create File Structure******

def init_dir_struct(dut_sn_l):
    """Initialize the directory structure for the electrometer test and cal"""
    ec_manager = dirman(
        project_name="EC",
        root_directory="./Test_Data/EC_Tests"
    )
    ec_report_path, ec_raw_data_path, ec_report_date, ec_report_time = \
            ec_manager.generate_paths(dut_sn_l)
    print("Paths generated:")
    print(f"Report Path: {ec_report_path}")
    print(f"Raw Data Path: {ec_raw_data_path}")
    print(f"Report Date: {ec_report_date}")
    print(f"Report Time: {ec_report_time}")

    print("\nCreating directories...")
    created_report_path, created_raw_data_path = ec_manager.create_directories(dut_sn_l)

    if created_report_path and created_raw_data_path:
        print("\nSuccessfully created directories for the 'EC' project.")

    return created_report_path, created_raw_data_path, ec_report_date, ec_report_time
# *************************************************************************


# *************************************************************************
# ******Begin Testing.....******
if __name__ == '__main__':

    # ******Collect Tester, DUT data******
    tester_name, tester_life = get_test_tech_info()
    dut_sn = get_dut_info()
    print("-" * 75)
    report_path, raw_data_path, report_date, report_time = init_dir_struct(dut_sn)

    print("Directory structure is prepared...")
    print("-" * 75)

    # ******V_BIAS Testing******
    print("\nBeginning Bias Voltage output testing...")
    bias_test_results = bias_test.v_bias_test(plc, dmm, em)
    print("-" * 75)


    # ******DAC Voltage Testing******
    print("\nBeginning DAC Voltage output testing...")
    dac_test_results = dac_test.dac_test(plc, dmm, em)
    print("-" * 75)
