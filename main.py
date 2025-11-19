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

import electrometer
import 

from IP_Addresses_PVs import PLC_IP_ADDRESS, DMM_IP_ADDRESS, \
                             I_SOUR_IP_ADDRESS, PSU_IP_ADDRESS, \
                             EM_PV_PREFIX

from instrument_module import DP800
#from instrument_module import Keithley2100
from instrument_module import Keithley6221
from instrument_module import keysight_34461a

from plc import PLC


from functional_tests import bias_test
from functional_tests import dac_test
from functional_tests import gpio_test
from functional_tests import fan_test

# *****************************************************************************

def placeholder():
    raise NotImplementedError("Function not implemented yet")

# *****************************************************************************
# ******CONSTANTS******

# *****************************************************************************


# ******Create Instrument Objects******
psu = DP800(connection_method="IP", address=PSU_IP_ADDRESS)
#dmm = Keithley2100(connection_method="USB", address=DMM_ADDRESS)
dmm = keysight_34461a(connection_method="IP", address=DMM_IP_ADDRESS)
i_sour = Keithley6221(connection_method="IP", address=I_SOUR_IP_ADDRESS)
plc = PLC(PLC_IP_ADDRESS)
em = electrometer(pv_prefix=EM_PV_PREFIX)
# *****************************************************************************

# *****************************************************************************
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


    # *************************************************************************
    # ******Visual Inspection******
    while True:
        vis_insp = input("Did unit pass visual inspection? <Y/N> ").strip().upper()[:1]
        if vis_insp in ("Y", "N"):
            break
        print("Must enter <Y> or <N>...") 

    # *************************************************************************
    # ******Voltage Card - With/Without? ******
    while True:
        voltage_card_present = input("Does the unit contain a voltage card? <Y/N> ").strip().upper()[:1]
        if voltage_card_present in ("Y", "N"):
            if voltage_card_present == "Y":
                voltage_card_present=True
            else:
                voltage_card_present=False
            break
        print("Must enter <Y> or <N>...")

    # *************************************************************************
    # ******Functional Test Only, or CAL?******
        

    # *************************************************************************
    # ******Perform All Tests?******
    while True:
        test_skip = input("Will any tests be skipped? <Y/N>").strip().upper()[:1]
        if test_skip in ("Y", "N"):
            if test_skip == "Y":
                ###############################################################################
                break     
        else:
            #Invalid input...
            print("Must enter <Y> or <N>...")


    # *************************************************************************
    # ******Power On Test******
        # Power on, check V, I...
    
    # *************************************************************************
    # ******COM, ETH Test******
        
    # *************************************************************************
    # ******GPI/O Testing******
    # *************************************************************************

    # ******V_BIAS Testing******
    if test_skip
    print("\nBeginning Bias Voltage output testing...")
    bias_test_results = bias_test.v_bias_test(plc, dmm, em)
    print("-" * 75)


    # ******DAC Voltage Testing******
    print("\nBeginning DAC Voltage output testing...")
    dac_test_results = dac_test.dac_test(plc, dmm, em)
    print("-" * 75)

    # ******DIGITAL GPIO TESTING******
    print("\nBeginning Digital GPIO Testing...")
    gpio_test_results = gpio_test.gpio_input_test(plc, em)
    print("-" * 75)

    # ******Fan Test******
    print("\nBeginning Fan Test...")
    fan_test_results = fan_test.fan_header_voltage_test(plc, dmm)
    print("-" * 75)

    # ******Voltage Cal******
    if voltage_card_present: 
        print("\nBeginning Voltage Daughterboard Calibration...")
        voltage_cal_results = 
        print("-" * 75)

    # ******Current Calibration******
    print("\nBeginning Current Calibration...")
    current_cal_results = 
    print("-" * 75)
