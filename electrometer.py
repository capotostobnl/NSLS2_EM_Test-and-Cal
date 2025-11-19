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
    PV_PREFIX = 

    # *****************************************************************************
# ******Ranges******
    # 0: 10mA, 1: 1mA, 2: 100uA, 3: 10uA, 4: 1uA, 5: 100nA
    I_RANGE_MODE = {
        '10mA': 0,
        '1mA': 1,
        '100uA': 2,
        '10uA': 3,
        '1uA': 4,
        '100nA': 5,
    }

    def __init__(self, pv_prefix):
        """Initialize PVs"""
        self.PV_PREFIX = pv_prefix
        # Store all PVs in one dictionary for easy access
        self._pvs: dict[str, epics.PV] = {}

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

        #******SET EM AMP UNIT******
        self._pvs["compute_current_offset_proc"] = epics.PV(
            f"{self.PV_PREFIX}ComputeCurrentOffset1.PROC"
        )


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

    # **********************************************************
    # Calibration helpers adapted from electrometer_init.py
    # **********************************************************
    #  Adapted from Sukho Kongtawong: 
    #  "set_XBPM_gain_20bit_default.py for EM initalization"
    #  Version: 11/5/2025
    def _create_cal_pvs_for_range(self, I_range: str):
        """
        Create (or fetch) the gain/offset PVs for a given current range.

        Returns four lists of PV objects:
            gain_SP_pv, gain_I_pv, offset_SP_pv, offset_I_pv
        """
        if I_range not in self.I_RANGE_MODE:
            raise ValueError(
                f"Invalid I_range '{I_range}'. "
                f"Valid keys: {list(self.I_RANGE_MODE.keys())}"
            )

        gain_SP_pv = []
        gain_I_pv = []
        offset_SP_pv = []
        offset_I_pv = []

        for ch in ["A", "B", "C", "D"]:
            # Keys for our internal dict (purely a convention)
            gsp_key = f"gain_{I_range}_{ch}_SP"
            gi_key = f"gain_{I_range}_{ch}_I"
            osp_key = f"offset_{I_range}_{ch}_SP"
            oi_key = f"offset_{I_range}_{ch}_I"

            # Build full PV names exactly like electrometer_init.py
            gsp_name = f"{self.PV_PREFIX}Ch{ch}-{I_range}-Gain-SP"
            gi_name = f"{self.PV_PREFIX}Ch{ch}-{I_range}-Gain-I"
            osp_name = f"{self.PV_PREFIX}Ch{ch}-{I_range}-Ofst-SP"
            oi_name = f"{self.PV_PREFIX}Ch{ch}-{I_range}-Ofst-I"

            # Create on first use, then reuse
            if gsp_key not in self._pvs:
                self._pvs[gsp_key] = epics.PV(gsp_name)
            if gi_key not in self._pvs:
                self._pvs[gi_key] = epics.PV(gi_name)
            if osp_key not in self._pvs:
                self._pvs[osp_key] = epics.PV(osp_name)
            if oi_key not in self._pvs:
                self._pvs[oi_key] = epics.PV(oi_name)

            gain_SP_pv.append(self._pvs[gsp_key])
            gain_I_pv.append(self._pvs[gi_key])
            offset_SP_pv.append(self._pvs[osp_key])
            offset_I_pv.append(self._pvs[oi_key])

        return gain_SP_pv, gain_I_pv, offset_SP_pv, offset_I_pv

    def calibration_initialization(self):
        """
        Replicate Sukho's electrometer_init.py behavior:

        - For each current range (10mA .. 100nA):
            * Set 19-bit gain SPs to negative full-scale
            * Set 19-bit offset SPs to zero
        - Set 15-bit Reg24–27 to full-scale gain
        - Set 15-bit Reg20–23 to zero offset
        - Trigger ComputeCurrentOffset1.PROC
        """
        t0 = time.time()
        nkey = len(self.I_RANGE_MODE)

        # ---------- Per-range 19-bit gain/offset ----------
        for ikey, I_range in enumerate(self.I_RANGE_MODE.keys()):
            print(f"{ikey + 1}/{nkey}: {I_range}")

            gain_SP_pv, _, offset_SP_pv, _ = self._create_cal_pvs_for_range(I_range)

            # 19-bit settings
            gain_19bits = 2**19 - 1  # max
            offset_19bits = 0

            # Negative full-scale, as in Sukho's script
            gain_19bits = -1 * gain_19bits

            # Write to all channels (A–D) for this range
            for pv in gain_SP_pv:
                pv.put(gain_19bits)
            for pv in offset_SP_pv:
                pv.put(offset_19bits)

        # ---------- Shared 15-bit Reg* PVs ----------
        gain_15bits = 2**15 - 1
        offset_15bits = 0

        # Gain: Reg24–27
        gain_15bits_pvs = []
        for reg in range(24, 27 + 1):
            key = f"reg{reg}_gain_sp"
            name = f"{self.PV_PREFIX}Reg{reg}-Sp"
            if key not in self._pvs:
                self._pvs[key] = epics.PV(name)
            gain_15bits_pvs.append(self._pvs[key])

        # Offset: Reg20–23
        offset_15bits_pvs = []
        for reg in range(20, 23 + 1):
            key = f"reg{reg}_offset_sp"
            name = f"{self.PV_PREFIX}Reg{reg}-Sp"
            if key not in self._pvs:
                self._pvs[key] = epics.PV(name)
            offset_15bits_pvs.append(self._pvs[key])

        for pv in gain_15bits_pvs:
            pv.put(gain_15bits)
        for pv in offset_15bits_pvs:
            pv.put(offset_15bits)

        # ---------- Tell IOC to recompute current offsets ----------
        self._pvs["compute_current_offset_proc"].put(1)

        print(f"Calibration init done (in {time.time() - t0:.6f} s)")
