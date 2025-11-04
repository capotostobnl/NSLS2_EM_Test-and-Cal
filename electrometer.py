# pylint: disable=broad-except
# flake8: noqa E501
"""This module is for accessing the Electrometer PVs.

M. Capotosto
3/5/2025
NSLS-II Diagnostics and Instrumentation
"""
# *****************************************************************************



# *****************************************************************************
# ******IMPORTS******
import epics
# *****************************************************************************


# *****************************************************************************
# ******CONSTANTS******

# *****************************************************************************


# *****************************************************************************
# ******PV Setup******
class Electrometer:
    """Class for interfacing EM IOC"""
    PV_PREFIX = "SR:C09-BI{XBPM:1}"

    def __init__(self):
        """Initialize PVs"""

        # Store all PVs in one dictionary for easy access
        self._pvs = {}

        # ******Bias Voltage******
        self._pvs["bias_v_sp"] = epics.PV(self.PV_PREFIX + "Bias-Sp")
        self._pvs["bias_v_sp_counts"] = epics.PV(self.PV_PREFIX + "Reg32-Sp")

        #******DAC Outputs******
        for channel in ['A', 'B', 'C', 'D']:
            pv_name = f"{self.PV_PREFIX}DAC-Chan{channel}-Sp"
            self._pvs[f"dac_{channel}"] = epics.PV(pv_name)

        #******GPIO Outputs******
        for channel in [0, 1, 2, 3]:
            pv_name = f"{self.PV_PREFIX}OUT{channel}-Cmd"
            self._pvs[f"gpout_{channel}"] = epics.PV(pv_name)
        #******GPIO inputs******
        for channel in ['B0', 'B1', 'B2', 'B3']:
            pv_name = f"{self.PV_PREFIX}GPIO:OUT-I.B{channel}"
            self._pvs[f"gpin_{channel}"] = epics.PV(pv_name)




    # ******Channel Access Functions******

    def get_pv_value(self, pv_name):
        """
        A generic method to get the value of any PV by its name.
        """
        if pv_name in self._pvs:
            return self._pvs[pv_name].get()
        else:
            print(f"Error: PV '{pv_name}' not found.")
            return None

    def put_pv_value(self, pv_name, value):
        """
        A generic method to put a value to any PV by its name.
        """
        if pv_name in self._pvs:
            self._pvs[pv_name].put(value)
        else:
            print(f"Error: PV '{pv_name}' not found.")
