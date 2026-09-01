"""Particiona a curva de loosening em estágios (janelas de ciclos) ajustáveis
e calcula MAE por segmento contra uma curva de referência."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence

import numpy as np

# Tuners "donos" de cada estágio (quem domina fisicamente aquela janela)
_OWNED = {
    "I": ["k_emb_scale"],
    "II": ["k_wear_scale_tr", "k_loose_scale_tr", "Phi_tr_correction",
           "k_damage_scale"],
    "III": ["k_creep_scale"],
}


@dataclass
class Stage:
    name: str
    n_start: float
    n_end: float
    owned_tuners: List[str]


class StageSegmentation:
    """Três estágios com fronteiras ajustáveis: I [0,n_I), II [n_I,n_II),
    III [n_II, n_end]. n_end é inclusivo no último estágio."""

    def __init__(self, n_I: float, n_II: float, n_end: float):
        if not (0 < n_I < n_II <= n_end):
            raise ValueError(f"Esperado 0 < n_I < n_II <= n_end; "
                             f"recebi n_I={n_I}, n_II={n_II}, n_end={n_end}")
        self.n_I = float(n_I)
        self.n_II = float(n_II)
        self.n_end = float(n_end)
        self.stages: List[Stage] = [
            Stage("I", 0.0, self.n_I, list(_OWNED["I"])),
            Stage("II", self.n_I, self.n_II, list(_OWNED["II"])),
            Stage("III", self.n_II, self.n_end, list(_OWNED["III"])),
        ]

    def segment_of(self, n: float) -> str:
        if n < self.n_I:
            return "I"
        if n < self.n_II:
            return "II"
        return "III"

    def mae_per_segment(self, sim_N: Sequence[float], sim_ratio: Sequence[float],
                        ref_N: Sequence[float], ref_ratio: Sequence[float]
                        ) -> Dict[str, Optional[float]]:
        """MAE de |sim_interp(ref_N) − ref_ratio| por estágio. None se o
        estágio não tem ponto de referência."""
        sim_N = np.asarray(sim_N, dtype=float)
        sim_ratio = np.asarray(sim_ratio, dtype=float)
        ref_N = np.asarray(ref_N, dtype=float)
        ref_ratio = np.asarray(ref_ratio, dtype=float)
        sim_at_ref = np.interp(ref_N, sim_N, sim_ratio)
        abs_err = np.abs(sim_at_ref - ref_ratio)
        out: Dict[str, Optional[float]] = {}
        for stage in self.stages:
            mask = np.array([self.segment_of(n) == stage.name for n in ref_N])
            out[stage.name] = float(np.mean(abs_err[mask])) if mask.any() else None
        return out
