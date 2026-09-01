"""CMMS / Maintenance-system export (§7.4).

Converts a coupled-loosening analysis result into a maintenance work-order
row suitable for SAP PM or IBM Maximo import.

The retorque interval is defined as the first cycle at which the predicted
preload ratio F_p/F_p0 drops below the maintenance-trigger threshold
(default 0.85 — inside the LLC "non-rotational" band, conservative relative
to the WARNING boundary at 0.75).
"""

from __future__ import annotations

import csv
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from typing import Optional, Sequence

import numpy as np


@dataclass
class CMMSRecord:
    equipment_id: str
    bolt_id: str
    bolt_spec: str              # e.g. "M16 × 2.0, class 10.9"
    initial_preload_N: float
    retorque_cycles: int        # N at F/F₀ = threshold
    retorque_hours: float       # operating hours to reach threshold
    next_retorque_date: str     # ISO 8601 YYYY-MM-DD
    torque_nm: float            # target retorque torque
    threshold_ratio: float = 0.85
    frequency_hz: float = 0.0
    duty_cycle: float = 1.0     # fraction of time under load

    def as_row(self) -> list:
        """Row suitable for export_cmms_csv."""
        return [
            self.equipment_id, self.bolt_id, self.bolt_spec,
            f"{self.initial_preload_N:.1f}",
            self.retorque_cycles,
            f"{self.retorque_hours:.1f}",
            self.next_retorque_date,
            f"{self.torque_nm:.2f}",
            f"{self.threshold_ratio:.2f}",
        ]


def compute_retorque_interval(preload_array: Sequence[float],
                              cycles_array: Sequence[int],
                              threshold_ratio: float = 0.85) -> int:
    """Find the first cycle at which F/F₀ drops below threshold_ratio.

    Returns 0 if the threshold is never crossed (joint stays above threshold
    for the entire simulation — report as "no retorque needed in horizon").
    """
    F = np.asarray(preload_array, dtype=float)
    N = np.asarray(cycles_array, dtype=int)
    if F.size == 0 or N.size == 0:
        return 0
    F0 = float(F[0]) if F[0] > 0 else 1.0
    ratio = F / F0
    below = np.where(ratio < threshold_ratio)[0]
    if below.size == 0:
        return 0
    return int(N[below[0]])


def build_cmms_record(
    equipment_id: str,
    bolt_id: str,
    bolt_spec: str,
    preload_array: Sequence[float],
    cycles_array: Sequence[int],
    frequency_hz: float,
    torque_nm: float,
    threshold_ratio: float = 0.85,
    duty_cycle: float = 1.0,
    reference_date: Optional[datetime] = None,
) -> CMMSRecord:
    """Assemble a CMMSRecord from analysis arrays and metadata."""
    N_retorque = compute_retorque_interval(preload_array, cycles_array, threshold_ratio)
    F0 = float(preload_array[0]) if len(preload_array) else 0.0
    effective_freq = max(frequency_hz * max(duty_cycle, 0.0), 1e-9)
    T_hours = (N_retorque / (effective_freq * 3600.0)) if N_retorque > 0 else 0.0
    ref = reference_date or datetime.now()
    next_date = (ref + timedelta(hours=T_hours)).strftime("%Y-%m-%d") if N_retorque > 0 else "n/a"
    return CMMSRecord(
        equipment_id=equipment_id,
        bolt_id=bolt_id,
        bolt_spec=bolt_spec,
        initial_preload_N=F0,
        retorque_cycles=N_retorque,
        retorque_hours=T_hours,
        next_retorque_date=next_date,
        torque_nm=torque_nm,
        threshold_ratio=threshold_ratio,
        frequency_hz=frequency_hz,
        duty_cycle=duty_cycle,
    )


CSV_HEADER = [
    "Equipment_ID", "Bolt_ID", "Bolt_Spec",
    "Initial_Preload_N", "Retorque_Cycles", "Retorque_Hours",
    "Next_Retorque_Date", "Target_Torque_Nm", "Threshold_Ratio",
]


def export_cmms_csv(records: Sequence[CMMSRecord], filepath: str) -> None:
    """Write one or more CMMSRecords to a CMMS-compatible CSV file."""
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(CSV_HEADER)
        for rec in records:
            w.writerow(rec.as_row())
