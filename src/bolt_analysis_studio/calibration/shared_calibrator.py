"""Calibrador compartilhado (Estagio A, spec 2026-07-02 §2.5): UMA fisica
(constantes do par tribologico) fitada em conjunto sobre TODAS as condicoes;
condicoes diferem apenas por estados nomeados (D_init, emb_consumed_frac, F0).

Tuners (k_*_scale, Phi_*_correction, k_damage_scale) NUNCA sao fitados aqui —
ficam no default 1.0. O fit e em log-espaco (constantes positivas, ordens de
magnitude variadas) com prior de literatura: residuo += sqrt(lambda)*(ln p -
ln p_default), substituindo o pull-to-1 do StagedCalibrator.
"""
from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import Dict, List, Tuple

import numpy as np
from scipy.optimize import least_squares

from ..numerical.dynamic_stiffness_analyzer import (
    DynamicStiffnessAnalyzer, JointGeometry, JointMaterial,
)
from .parameter_registry import active_candidates

# Constantes fisicas que o calibrador conhece + prior de literatura (default).
PHYSICAL_PRIORS: Dict[str, float] = {
    "emb_depth": 30e-6,
    "N_emb": 50.0,
    "k_wear_spec": 5e-14,   # razao K/H [1/Pa] identificavel (merge §4.42a);
                            #   = 1e-4/2e9 (K_archard/hardness legados)
    "C_creep": 5e-11,
    "tr_loose_gain": 2.0,
    "c_D": 2.0,          # fisica de dano — so afeta condicoes damage_active
    "k_dmg_wear": 4.0,   # idem
}
_DAMAGE_CONSTANTS = ("c_D", "k_dmg_wear")


@dataclass
class ConditionSpec:
    """Uma condicao experimental: curvas + estados nomeados (inputs fisicos)."""
    name: str
    curves: List[dict]              # [{"name", "cycles", "ratio"}, ...]
    F0_init: float                  # pre-carga do ensaio [N]
    F_amp: float                    # amplitude de forca [N]
    delta_amp: float                # amplitude de deslocamento imposto [m]
    D_init: float = 0.0
    emb_consumed_frac: float = 0.0
    damage_active: bool = False


@dataclass
class SharedCalibrationConfig:
    geom: JointGeometry
    conditions: List[ConditionSpec]
    theta: float
    freq: float
    n_cycles: int
    bounds: Dict[str, Tuple[float, float]]   # bounds das constantes fisicas
    priors: Dict[str, float] = field(
        default_factory=lambda: dict(PHYSICAL_PRIORS))
    lambda_reg: float = 0.001
    # Fallback §2.3: F0 estimado UMA vez — nome da condicao -> (lo, hi) em N.
    estimate_F0: Dict[str, Tuple[float, float]] = field(default_factory=dict)
    # fisica de dano fixa aplicada as condicoes damage_active
    W_ref: float = 1.0e4
    k_dmg_mu: float = 1.0
    max_nfev: int = 40
    # modo do driver de conformacao propagado ao JointMaterial. Nao-numerico,
    # portanto NAO vai em priors/constants (que sao log-fitadas e serializadas
    # via float(v)) — viaja na config e e aplicado em _material.
    conform_driver: str = "raw"


class SharedCalibrator:
    def __init__(self, config: SharedCalibrationConfig):
        self.cfg = config
        self.constants: Dict[str, float] = dict(config.priors)
        # centro geometrico dos bounds como chute inicial do F0 estimado
        self.F0_estimates: Dict[str, float] = {
            name: float(np.sqrt(lo * hi))
            for name, (lo, hi) in config.estimate_F0.items()}

    # ---- simulacao ----
    def _material(self, cond: ConditionSpec) -> JointMaterial:
        kw = {k: v for k, v in self.constants.items()
              if k not in _DAMAGE_CONSTANTS}
        if cond.damage_active:
            kw.update(c_D=self.constants["c_D"],
                      k_dmg_wear=self.constants["k_dmg_wear"],
                      W_ref=self.cfg.W_ref, k_dmg_mu=self.cfg.k_dmg_mu)
        kw["conform_driver"] = self.cfg.conform_driver
        return JointMaterial(**kw)

    def _F0(self, cond: ConditionSpec) -> float:
        return self.F0_estimates.get(cond.name, cond.F0_init)

    def _run_condition(self, cond: ConditionSpec):
        F0 = self._F0(cond)
        ana = DynamicStiffnessAnalyzer(
            self.cfg.geom, self._material(cond), F0,
            initial_damage=cond.D_init,
            initial_embedding_frac=cond.emb_consumed_frac)
        ratio = [1.0]
        for _ in range(self.cfg.n_cycles):
            ana.step_cycle(cond.F_amp, self.cfg.theta, self.cfg.freq,
                           delta_amp=cond.delta_amp)
            ratio.append(max(ana.state.F_0, 0.0) / F0)
        return np.arange(self.cfg.n_cycles + 1), np.array(ratio)

    # ---- metricas ----
    def mae_by_condition(self) -> Dict[str, float]:
        out = {}
        for cond in self.cfg.conditions:
            sim_N, sim_ratio = self._run_condition(cond)
            maes = [float(np.mean(np.abs(
                np.interp(c["cycles"], sim_N, sim_ratio) - c["ratio"])))
                for c in cond.curves]
            out[cond.name] = float(np.mean(maes))
        return out

    def global_mae(self) -> float:
        """Media sobre CONDICOES (nao curvas): TP6/TP7 pesam igual a nova."""
        by = self.mae_by_condition()
        return float(np.mean(list(by.values())))

    # ---- fit (log-espaco) ----
    def _apply_x(self, x, free_consts: List[str], f0_names: List[str]) -> None:
        for name, xi in zip(free_consts, x[:len(free_consts)]):
            self.constants[name] = float(np.exp(xi))
        for name, xi in zip(f0_names, x[len(free_consts):]):
            self.F0_estimates[name] = float(np.exp(xi))

    def _residuals(self, x, free_consts: List[str], f0_names: List[str]):
        self._apply_x(x, free_consts, f0_names)
        res: List[float] = []
        for cond in self.cfg.conditions:
            sim_N, sim_ratio = self._run_condition(cond)
            w_cond = np.sqrt(max(len(cond.curves), 1))
            for c in cond.curves:
                err = np.interp(c["cycles"], sim_N, sim_ratio) - c["ratio"]
                res.extend(err / (np.sqrt(max(len(err), 1)) * w_cond))
        # prior de literatura em log-espaco (substitui o pull-to-1)
        lam = np.sqrt(self.cfg.lambda_reg)
        for name, xi in zip(free_consts, x[:len(free_consts)]):
            res.append(lam * (xi - np.log(self.cfg.priors[name])))
        return np.array(res) if res else np.array([0.0])

    def _fit_subset(self, free_consts: List[str]) -> None:
        """Fita `free_consts` + os estados F0 configurados (sempre ativos)."""
        f0_names = list(self.cfg.estimate_F0.keys())
        if not free_consts and not f0_names:
            return
        x0, lo, hi = [], [], []
        for name in free_consts:
            x0.append(np.log(self.constants[name]))
            b = self.cfg.bounds[name]
            lo.append(np.log(b[0])); hi.append(np.log(b[1]))
        for name in f0_names:
            x0.append(np.log(self.F0_estimates[name]))
            b = self.cfg.estimate_F0[name]
            lo.append(np.log(b[0])); hi.append(np.log(b[1]))
        result = least_squares(self._residuals, x0, bounds=(lo, hi),
                               args=(free_consts, f0_names), method="trf",
                               xtol=1e-8, ftol=1e-8, diff_step=1e-2,
                               max_nfev=self.cfg.max_nfev)
        # a ultima avaliacao interna nao e necessariamente o otimo — reaplica
        self._apply_x(result.x, free_consts, f0_names)

    def fit_parsimonious(self, tol: float = 0.005,
                         max_constants: int = 5) -> dict:
        """Forward selection sobre CONSTANTES FISICAS: parte dos priors de
        literatura e so libera uma constante se ela cortar o MAE global > tol
        (anti-overfitting, mesma filosofia do StagedCalibrator.fit_parsimonious).
        Estados F0 configurados participam de todo subset (sao estados, nao
        candidatos)."""
        # Candidatos vem do registro de ativacao (spec 2026-07-03): so
        # constantes cujo mecanismo e excitado por ALGUMA condicao do
        # dataset. Generaliza o antigo filtro _DAMAGE_CONSTANTS (que segue
        # existindo para o _material injetar a fisica de dano).
        cands = active_candidates(self.cfg.bounds, self.cfg.priors,
                                  self.cfg.conditions, self.cfg.theta,
                                  set(self.cfg.estimate_F0))
        self.constants = dict(self.cfg.priors)
        free: List[str] = []
        self._fit_subset(free)                    # baseline: so estados
        best = self.global_mae()
        history: List[tuple] = [("(defaults+estados)", best)]
        while len(free) < max_constants:
            trials = []
            for cand in cands:
                if cand in free:
                    continue
                saved_c = dict(self.constants)
                saved_f = dict(self.F0_estimates)
                self._fit_subset(free + [cand])
                trials.append((cand, self.global_mae(),
                               dict(self.constants), dict(self.F0_estimates)))
                self.constants, self.F0_estimates = saved_c, saved_f
            if not trials:
                break
            cand, m, snap_c, snap_f = min(trials, key=lambda z: z[1])
            if best - m < tol:
                break
            free.append(cand)
            best = m
            self.constants, self.F0_estimates = snap_c, snap_f
            history.append((cand, m))
        return {
            "free_constants": free,
            "candidates": cands,
            "constants": {k: float(v) for k, v in self.constants.items()},
            "F0_estimates": {k: float(v) for k, v in self.F0_estimates.items()},
            "mae_global": float(best),
            "mae_by_condition": self.mae_by_condition(),
            "selection_history": history,
        }

    def loco(self, free_constants: List[str]) -> dict:
        """Leave-one-condition-out: refita as demais condicoes (mesmo conjunto
        livre) e PREDIZ a retida usando so os estados nomeados dela. Se o F0 da
        retida era estimado (sobretorque), usa o valor do fit completo e marca
        state_F0_from_full_fit=True (limitacao documentada, spec §2.5)."""
        out: Dict[str, dict] = {}
        full_f0 = dict(self.F0_estimates)
        full_consts = dict(self.constants)
        for held in self.cfg.conditions:
            rest = [c for c in self.cfg.conditions if c.name != held.name]
            sub_cfg = replace(
                self.cfg, conditions=rest,
                estimate_F0={k: v for k, v in self.cfg.estimate_F0.items()
                             if k != held.name})
            sub = SharedCalibrator(sub_cfg)
            sub._fit_subset(list(free_constants))
            pred = SharedCalibrator(replace(self.cfg, conditions=[held]))
            pred.constants = dict(sub.constants)
            pred.F0_estimates = ({held.name: full_f0[held.name]}
                                 if held.name in full_f0 else {})
            out[held.name] = {
                "MAE_pred": pred.mae_by_condition()[held.name],
                "state_F0_from_full_fit": held.name in full_f0,
            }
        # restaura o estado do fit completo
        self.constants, self.F0_estimates = full_consts, full_f0
        return out
