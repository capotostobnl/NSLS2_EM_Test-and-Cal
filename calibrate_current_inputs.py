from __future__ import annotations
from dataclasses import dataclass
from typing import Sequence

import numpy as np

from electrometer import Electrometer
from instrument_module import Keithley6221

STABLE_WAIT_SEC = 5.0


@dataclass
class CurrentCalResult:
    chan: str
    range_index: int
    range_label: str
    source_currents_A: list[float]
    em_currents_A: list[float]
    adc_raw: list[int]
    gain_scaled: int
    offset_scaled: int


def run_channel_calibration(
    em: Electrometer,
    src: Keithley6221,
    chan: str,
    prefix: str,
) -> list[CurrentCalResult]:
    """
    Run full current calibration for one EM channel (A/B/C/D).
    Returns a list of CurrentCalResult, one per EM range.
    """

    # Map EM PV names via helper methods you already have or we can add them:
    Rpv   = em.get_range_pv(chan)          # e.g. RangeCtrl:A-SP
    Gpv   = em.get_current_scale_pv(chan)  # CurrentScale1
    Opv   = em.get_current_offset_pv(chan) # CurrentOffset1
    Spv   = em.get_em_slow_pv(chan)        # Current1:MeanValue_RBV
    ADCpv = em.get_adc_pv(chan)            # Reg44-I

    em.select_output_mux(chan)  # wrap your CHAN_TO_OUT + OUTn-Cmd logic into Electrometer

    # reuse your arrays:
    Krange = [2E-2, 2E-3, 2E-4, 2E-5, 2E-6, 2E-7]
    Erange = [0, 1, 2, 3, 4, 5]
    Er     = ["10000uA", "1000uA", "100uA", "10uA", "1uA", "0.1uA"]

    results: list[CurrentCalResult] = []

    for i in range(6):
        src.set_range(Krange[i])        # wrapper around SOUR:CURR:RANGE
        Rpv.put(Erange[i])
        Gpv.put(1.0)
        Opv.put(0.0)

        I6221: list[float] = []
        Isa: list[float] = []
        adc_vals: list[int] = []

        for j in range(-9, 10):
            curr = Krange[i] * j / 20.0
            src.set_current(curr)       # wrapper around SOUR:CURR:LEV:IMM:AMPL
            src.wait(STABLE_WAIT_SEC)

            em_val = float(Spv.get()) / 1_000_000.0
            adc    = int(ADCpv.get())

            I6221.append(curr)
            Isa.append(em_val)
            adc_vals.append(-adc)

        # fit
        P = np.polyfit(I6221, Isa, 1)
        max_val = 524287
        P0_scaled = int(P[0] * max_val)
        P1_scaled = int(P[1] * max_val)
        max_scaled = max(abs(P0_scaled), abs(P1_scaled))
        if max_scaled > max_val:
            scale = max_val / max_scaled
            P0_scaled = int(P0_scaled * scale)
            P1_scaled = int(P1_scaled * scale)

        results.append(
            CurrentCalResult(
                chan=chan,
                range_index=i,
                range_label=Er[i],
                source_currents_A=I6221,
                em_currents_A=Isa,
                adc_raw=adc_vals,
                gain_scaled=P0_scaled,
                offset_scaled=P1_scaled,
            )
        )

    return results


def run_full_current_calibration(
    em: Electrometer,
    src: Keithley6221,
    channels: Sequence[str] = ("A", "B", "C", "D"),
) -> dict[str, list[CurrentCalResult]]:
    all_results: dict[str, list[CurrentCalResult]] = {}
    for chan in channels:
        print(f"=== Calibrating channel {chan} ===")
        all_results[chan] = run_channel_calibration(em, src, chan, em.PV_PREFIX)
    return all_results
