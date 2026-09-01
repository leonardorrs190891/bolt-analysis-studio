"""Calibrador em estágios: coordenada-descida por janela de ciclos, com
travas entre estágios e regularização física (pull dos tuners pra 1.0)."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

import numpy as np
from scipy.optimize import least_squares

from ..numerical.dynamic_stiffness_analyzer import (
    DynamicStiffnessAnalyzer, JointGeometry, JointMaterial,
)
from .segmentation import StageSegmentation
from .decomposition import MechanismDecomposition

# Todos os tuners que o calibrador conhece, com valor neutro (default fisico).
_ALL_TUNERS = ["k_emb_scale", "k_creep_scale", "k_wear_scale_tr",
               "k_loose_scale_tr", "Phi_tr_correction", "k_damage_scale"]


@dataclass
class CalibrationConfig:
    geom: JointGeometry
    F0_init: float
    F_amp: float
    theta: float
    freq: float
    n_cycles: int
    delta_amp: float
    segmentation: StageSegmentation
    bounds: Dict[str, tuple]
    # Regularizacao fraca: empurra tuners pra perto de 1 e evita saturacao
    # nos bounds, SEM dominar o fit (lambda alto puxava demais e piorava o
    # MAE; 0.001 da tuners interpretaveis com MAE ~0.04).
    lambda_reg: float = 0.001
    fit_damage: bool = False
    c_D: float = 2.0
    W_ref: float = 1.0e4
    k_dmg_mu: float = 1.0
    k_dmg_wear: float = 4.0


class StagedCalibrator:
    """APOSENTADO no Estagio B (2026-07-09, spec 2026-07-02 §3.3): fitava a
    camada de TUNERS adimensionais (k_*_scale/Phi_*_correction), removida do
    engine. O caminho canonico e o `SharedCalibrator` (constantes fisicas
    compartilhadas) OU o `ParameterIdentifier(engine="v2")` com
    `default_v2_params()` (constantes fisicas per-junta). .msd/payloads legados
    com tuners: `calibration.tuner_shim.translate_legacy_tuners`.
    """
    def __init__(self, config: CalibrationConfig, curves: List[dict]):
        raise NotImplementedError(
            "StagedCalibrator foi APOSENTADO no Estagio B (tuners removidos do "
            "engine). Use SharedCalibrator (fisica compartilhada) ou "
            "ParameterIdentifier(engine='v2', params_to_fit=default_v2_params()) "
            "(constantes fisicas). Tuners legados: tuner_shim.translate_legacy_tuners.")
        self.cfg = config
        self.curves = curves
        # estado corrente dos tuners (parte do default fisico = 1.0)
        self.tuners: Dict[str, float] = {t: 1.0 for t in _ALL_TUNERS}
        self.D_init: float = 0.3 if config.fit_damage else 0.0

    # ---- simulação ----
    def _material(self) -> JointMaterial:
        kw = dict(self.tuners)
        if self.cfg.fit_damage:
            kw.update(c_D=self.cfg.c_D, W_ref=self.cfg.W_ref,
                      k_dmg_mu=self.cfg.k_dmg_mu, k_dmg_wear=self.cfg.k_dmg_wear)
        return JointMaterial(**kw)

    def _run_sim(self) -> tuple:
        ana = DynamicStiffnessAnalyzer(self.cfg.geom, self._material(),
                                       self.cfg.F0_init,
                                       initial_damage=self.D_init)
        ratio = [1.0]
        for _ in range(self.cfg.n_cycles):
            ana.step_cycle(self.cfg.F_amp, self.cfg.theta, self.cfg.freq,
                           delta_amp=self.cfg.delta_amp)
            ratio.append(max(ana.state.F_0, 0.0) / self.cfg.F0_init)
        return np.arange(self.cfg.n_cycles + 1), np.array(ratio), ana.history

    # ---- custo de um estágio ----
    def _stage_residuals(self, x, free_names, stage, fit_D):
        # aplica os valores livres
        for name, val in zip(free_names, x[:len(free_names)]):
            self.tuners[name] = float(val)
        if fit_D:
            self.D_init = float(x[-1])
        sim_N, sim_ratio, _ = self._run_sim()
        res = []
        for c in self.curves:
            in_win = np.array([stage.n_start <= n < stage.n_end
                               or (stage.name == "III" and n == stage.n_end)
                               for n in c["cycles"]])
            if not in_win.any():
                continue
            sim_at = np.interp(c["cycles"][in_win], sim_N, sim_ratio)
            err = sim_at - c["ratio"][in_win]
            res.extend(err / np.sqrt(max(in_win.sum(), 1)))
        # regularizacao fisica: puxa cada tuner livre pra 1.0
        lam = np.sqrt(self.cfg.lambda_reg)
        for name in free_names:
            res.append(lam * (self.tuners[name] - 1.0))
        return np.array(res) if res else np.array([0.0])

    def _fit_stage(self, stage):
        free = [t for t in stage.owned_tuners if t in self.cfg.bounds]
        if self.cfg.fit_damage and stage.name == "II":
            fit_D = True
        else:
            if not self.cfg.fit_damage:
                free = [t for t in free if t != "k_damage_scale"]
            fit_D = False
        if not free and not fit_D:
            return
        x0 = [self.tuners[t] for t in free]
        lo = [self.cfg.bounds[t][0] for t in free]
        hi = [self.cfg.bounds[t][1] for t in free]
        if fit_D:
            x0.append(self.D_init)
            lo.append(0.0)
            hi.append(0.9)
        least_squares(self._stage_residuals, x0, bounds=(lo, hi),
                      args=(free, stage, fit_D),
                      method="trf", xtol=1e-8, ftol=1e-8, max_nfev=200)

    # ---- driver ----
    def fit(self, n_passes: int = 2) -> dict:
        for _ in range(n_passes):
            for stage in self.cfg.segmentation.stages:
                self._fit_stage(stage)
        sim_N, sim_ratio, hist = self._run_sim()
        seg = self.cfg.segmentation
        # MAE por segmento agregado sobre todas as curvas
        per_seg = {s.name: [] for s in seg.stages}
        glob = []
        for c in self.curves:
            m = seg.mae_per_segment(sim_N, sim_ratio, c["cycles"], c["ratio"])
            for k, v in m.items():
                if v is not None:
                    per_seg[k].append(v)
            sim_at = np.interp(c["cycles"], sim_N, sim_ratio)
            glob.append(float(np.mean(np.abs(sim_at - c["ratio"]))))
        mae_per_segment = {k: (float(np.mean(v)) if v else None)
                           for k, v in per_seg.items()}
        # checa saturacao APENAS no bound superior (amplificacao patologica,
        # tipo o antigo k_loose=10). Saturar no bound inferior = mecanismo
        # "desligado" (ex: creep~0, embedding~0 no reusada) e' uma conclusao
        # fisica legitima, nao um problema.
        saturated = []
        for t, val in self.tuners.items():
            if t in self.cfg.bounds:
                lo, hi = self.cfg.bounds[t]
                if val >= hi - 0.01 * (hi - lo):
                    saturated.append(t)
        return {
            "tuners": {t: float(v) for t, v in self.tuners.items()},
            "D_init": float(self.D_init),
            "mae_per_segment": mae_per_segment,
            "mae_global": float(np.mean(glob)) if glob else None,
            "shares": MechanismDecomposition.shares_per_segment(hist, seg),
            "bounds_saturated": saturated,
        }

    # ------------------------------------------------------------------
    # Parcimonia — forward selection (anti-overfitting)
    # ------------------------------------------------------------------
    def _global_mae(self) -> float:
        sim_N, sim_ratio, _ = self._run_sim()
        g = []
        for c in self.curves:
            sim_at = np.interp(c["cycles"], sim_N, sim_ratio)
            g.append(np.mean(np.abs(sim_at - c["ratio"])))
        return float(np.mean(g)) if g else 0.0

    def _fit_subset(self, free_names) -> None:
        """Fit only `free_names` (others held at current value) against all curves."""
        free = [t for t in free_names if t in self.cfg.bounds]
        if not free:
            return
        x0 = [self.tuners[t] for t in free]
        lo = [self.cfg.bounds[t][0] for t in free]
        hi = [self.cfg.bounds[t][1] for t in free]

        def resid(x):
            for n, v in zip(free, x):
                self.tuners[n] = float(v)
            sim_N, sim_ratio, _ = self._run_sim()
            out = []
            for c in self.curves:
                err = np.interp(c["cycles"], sim_N, sim_ratio) - c["ratio"]
                out.extend(err / np.sqrt(max(len(err), 1)))
            lam = np.sqrt(self.cfg.lambda_reg)
            for n in free:
                out.append(lam * (self.tuners[n] - 1.0))
            return np.array(out)

        least_squares(resid, x0, bounds=(lo, hi), method="trf",
                      xtol=1e-8, ftol=1e-8, max_nfev=60, diff_step=1e-3)

    def fit_parsimonious(self, tol: float = 0.005, max_tuners: int = 4) -> dict:
        """Forward selection: start from all tuners = 1.0 (physical default) and
        add a tuner only if it cuts global MAE by more than `tol`. Yields the
        MINIMAL tuner set the data actually justifies — the anti-overfitting
        calibration (see New_Theory/MODEL_LEGITIMACY.md §4, §6)."""
        cands = [t for t in _ALL_TUNERS if t in self.cfg.bounds]
        if not self.cfg.fit_damage:
            cands = [t for t in cands if t != "k_damage_scale"]
        self.tuners = {t: 1.0 for t in _ALL_TUNERS}
        if self.cfg.fit_damage and self.D_init == 0.0:
            self.D_init = 0.3
        free: list = []
        best = self._global_mae()
        history = [("(defaults)", best)]
        while len(free) < max_tuners:
            trials = []
            for c in cands:
                if c in free:
                    continue
                saved = dict(self.tuners)
                self._fit_subset(free + [c])
                trials.append((c, self._global_mae(), dict(self.tuners)))
                self.tuners = saved
            if not trials:
                break
            cand, m, snap = min(trials, key=lambda z: z[1])
            if best - m < tol:        # candidate doesn't earn its keep
                break
            free.append(cand)
            best = m
            self.tuners = snap
            history.append((cand, m))
        return {
            "free_tuners": free,
            "tuners": {t: float(v) for t, v in self.tuners.items()},
            "D_init": float(self.D_init),
            "mae_global": float(best),
            "selection_history": history,
        }
