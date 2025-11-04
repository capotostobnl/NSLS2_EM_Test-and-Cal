"""This module is the main module for controlling and testing the NSLS-II
PLC relay interface used for EM test and calibration switching.

States by output (0 → 1)
------------------------
bias:   open → DMM
gpo0-3: bgpin → DMM
dac_a-d: vin → DMM
curr_a-d: short → ISOUR
fan_1-3: open → DMM
"""

from __future__ import annotations
from typing import Union, Literal
from time import sleep
from pylogix import PLC as _PLC
from IP_Addresses import PLC_IP


# ---- readable tokens (bare names) ----
dmm = "DMM"
bgpin = "bgpin"
vin = "vin"
short = "short"
isour = "ISOUR"
open_ = "open"   # avoid shadowing builtin open()

StateArg = Union[
    bool, int,
    Literal["0", "1", "open", "DMM", "bgpin", "vin", "short", "ISOUR"]
]


def _coerce(value: StateArg, zero_label: str, one_label: str) -> int:
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, int):
        if value in (0, 1):
            return value
        raise ValueError("State int must be 0 or 1.")
    v = str(value).strip()
    if v in ("0", "1"):
        return int(v)
    vlow = v.lower()
    if vlow == zero_label.lower():
        return 0
    if vlow == one_label.lower():
        return 1
    raise ValueError(f"Use 0/1 or '{zero_label}' / '{one_label}'")


def _tag_for(bit: int) -> str:
    return f"DO1_{bit}"


class PLC:
    """
    Convenience wrapper exposing one method per output line.

    Available methods (bit → states):
        bias:   open → DMM
        gpo0-3: bgpin → DMM
        dac_a-d: vin → DMM
        curr_a-d: short → ISOUR
        fan_1-3: open → DMM
    """

    def __init__(self, ip: str = PLC_IP):
        self._plc = _PLC()
        self._plc.IPAddress = ip

    # ---- init all to 0 ----
    def init_all(self):
        """Set all 16 outputs to state 0."""
        for b in range(16):
            self._plc.Write(_tag_for(b), 0)
            sleep(0.05)

    # ---- one method per tag (hover shows states) ----
    def bias(self, value: StateArg):
        """Bias relay — States: 0=open, 1=DMM."""
        return self._plc.Write(_tag_for(0), _coerce(value, "open", "DMM"))

    def gpo0(self, value: StateArg):
        """GPO0 route — States: 0=bgpin, 1=DMM."""
        return self._plc.Write(_tag_for(1), _coerce(value, "bgpin", "DMM"))

    def gpo1(self, value: StateArg):
        """GPO1 route — States: 0=bgpin, 1=DMM."""
        return self._plc.Write(_tag_for(2), _coerce(value, "bgpin", "DMM"))

    def gpo2(self, value: StateArg):
        """GPO2 route — States: 0=bgpin, 1=DMM."""
        return self._plc.Write(_tag_for(3), _coerce(value, "bgpin", "DMM"))

    def gpo3(self, value: StateArg):
        """GPO3 route — States: 0=bgpin, 1=DMM."""
        return self._plc.Write(_tag_for(4), _coerce(value, "bgpin", "DMM"))

    def dac_a(self, value: StateArg):
        """DAC A routing — States: 0=vin, 1=DMM."""
        return self._plc.Write(_tag_for(5), _coerce(value, "vin", "DMM"))

    def dac_b(self, value: StateArg):
        """DAC B routing — States: 0=vin, 1=DMM."""
        return self._plc.Write(_tag_for(6), _coerce(value, "vin", "DMM"))

    def dac_c(self, value: StateArg):
        """DAC C routing — States: 0=vin, 1=DMM."""
        return self._plc.Write(_tag_for(7), _coerce(value, "vin", "DMM"))

    def dac_d(self, value: StateArg):
        """DAC D routing — States: 0=vin, 1=DMM."""
        return self._plc.Write(_tag_for(8), _coerce(value, "vin", "DMM"))

    def curr_a(self, value: StateArg):
        """Current A path — States: 0=short, 1=ISOUR."""
        return self._plc.Write(_tag_for(9), _coerce(value, "short", "ISOUR"))

    def curr_b(self, value: StateArg):
        """Current B path — States: 0=short, 1=ISOUR."""
        return self._plc.Write(_tag_for(10), _coerce(value, "short", "ISOUR"))

    def curr_c(self, value: StateArg):
        """Current C path — States: 0=short, 1=ISOUR."""
        return self._plc.Write(_tag_for(11), _coerce(value, "short", "ISOUR"))

    def curr_d(self, value: StateArg):
        """Current D path — States: 0=short, 1=ISOUR."""
        return self._plc.Write(_tag_for(12), _coerce(value, "short", "ISOUR"))

    def fan_1(self, value: StateArg):
        """Fan 1 relay — States: 0=open, 1=DMM."""
        return self._plc.Write(_tag_for(13), _coerce(value, "open", "DMM"))

    def fan_2(self, value: StateArg):
        """Fan 2 relay — States: 0=open, 1=DMM."""
        return self._plc.Write(_tag_for(14), _coerce(value, "open", "DMM"))

    def fan_3(self, value: StateArg):
        """Fan 3 relay — States: 0=open, 1=DMM."""
        return self._plc.Write(_tag_for(15), _coerce(value, "open", "DMM"))

    def list_methods(self) -> dict[str, str]:
        """Return {name: first-line-of-docstring} for all tag methods."""
        out = {}
        for name, fn in self._methods.items():
            if fn.__doc__:
                doc = fn.__doc__.strip().splitlines()[0]
            else:
                doc = ""
            out[name] = doc
        return out


if __name__ == "__main__":
    plc = PLC()
    plc.init_all()
    print("Simple PLC test mode. Enter method then value. 'q' to quit.")

    tokens = {
              "open": "open",
              "dmm": "DMM",
              "bgpin": "bgpin",
              "vin": "vin",
              "short": "short",
              "isour": "ISOUR"
              }

    while True:
        try:
            m = input("Method: ").strip()
            if not m or m.lower() == "q":
                break
            v = input("Value (0/1 or label): ").strip()
            if v.lower() == "q":
                break
            v = tokens.get(v.lower(), v)  # normalize common labels

            fn = getattr(plc, m, None)
            if not callable(fn):
                print(f"Unknown method '{m}'.")
                continue

            fn(v)  # each method enforces exclusive=1 via _set_exclusive
            print(f"{m} -> {v}")
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}")

    plc.init_all()  # safe shutdown
    print("Exiting.")
