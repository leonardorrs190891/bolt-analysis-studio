"""
Wear Evolution Models for Bolted Joint Analysis
================================================

Four physically-grounded wear models for per-cycle wear depth computation:

  1. ArchardWearModel      — Classical Archard adhesive/abrasive wear with
                             3-phase K evolution (running-in → steady → severe)
  2. EnergyBasedWearModel  — Fouvry et al. (2003) energy-based fretting wear
                             V = α·E_d  (dissipated energy per cycle)
  3. FrettingWearModel     — Vingsbo-Söderberg fretting map with regime-dispatched
                             Archard K (stick / partial slip / fretting / gross slip)
  4. FatigueWearModel      — Sub-surface fatigue accumulation via Miner's rule;
                             delamination events when D ≥ D_critical

All models share a common interface::

    model.compute_wear_increment(F_normal, slip_distance_m, **kwargs) -> float [m]

Factory function::

    model = create_wear_model('archard', wear_params_obj)

References:
-----------
- Archard (1953): Adhesive wear law V = K·F·s / H
- Goryacheva (1998): Generalised exponents p^α·v^β
- Fouvry et al. (2003): Energy-based fretting wear coefficient α_V
- Vingsbo & Söderberg (1988): Fretting map stick/partial/fretting/gross regimes
- Hintikka et al. (2020): Fretting-loosening coupling
- Waterhouse (1981): Sub-surface fatigue delamination wear

Author: Bolt Analysis Studio Team
Version: 4.0
Date: February 2026
"""

import numpy as np
from dataclasses import dataclass, field
from typing import Dict, Optional
from enum import Enum


# =============================================================================
# ENUMERATIONS
# =============================================================================

class WearRegimeEnum(Enum):
    """Vingsbo-Söderberg fretting map regimes."""
    STICK        = "stick"
    PARTIAL_SLIP = "partial_slip"
    FRETTING     = "fretting"     # peak specific wear rate
    GROSS_SLIP   = "gross_slip"


class WearPhaseEnum(Enum):
    """Archard 3-phase wear evolution stages."""
    RUNNING_IN   = "running_in"
    STEADY       = "steady_state"
    SEVERE       = "severe"
    CATASTROPHIC = "catastrophic"


# =============================================================================
# WEAR STATE DATACLASS
# =============================================================================

@dataclass
class WearState:
    """
    Running wear state tracked across cycles.

    Shared by all model types; updated by the caller after each
    ``compute_wear_increment()`` call.
    """
    total_depth_m: float = 0.0         # Accumulated wear depth [m]
    cycles: int = 0                    # Cycles elapsed
    phase: WearPhaseEnum = WearPhaseEnum.RUNNING_IN
    accumulated_energy_J: float = 0.0  # For EnergyBasedWearModel
    damage_fraction: float = 0.0       # For FatigueWearModel (Miner's D)
    mu_reduction: float = 0.0          # Friction reduction due to wear

    def to_dict(self) -> Dict:
        return {
            'total_depth_um':       self.total_depth_m * 1e6,
            'cycles':               self.cycles,
            'phase':                self.phase.value,
            'accumulated_energy_J': self.accumulated_energy_J,
            'damage_fraction':      self.damage_fraction,
            'mu_reduction':         self.mu_reduction,
        }


# =============================================================================
# MODEL 1: ARCHARD WEAR
# =============================================================================

class ArchardWearModel:
    """
    Classical Archard (1953) adhesive/abrasive wear with 3-phase K evolution.

    **Wear law** (per cycle)::

        dV = K(cycle, depth) × F_n × s / H     [m³]
        dh = dV / A                              [m]

    **Phase-dependent K** (Hintikka et al. 2020):

    - Running-in  (cycles ≤ N_ri):      K = K_running_in   (high, asperity removal)
    - Transition  (N_ri < N ≤ N_ss):    K interpolated linearly
    - Steady-state (N > N_ss):          K = K_steady        (polished surfaces)
    - Severe      (depth > thr_severe): K = K_severe        (surface damage)
    - Catastrophic(depth > thr_cat):    K = K_catastrophic  (near-failure)

    **Generalised form** (Goryacheva 1998) when exponents ≠ 1::

        dh = K × p^α × s^β / H     where p = F_n / A
    """

    def __init__(self,
                 K_running_in: float = 5e-6,
                 K_steady: float = 1e-6,
                 K_severe: float = 1e-5,
                 K_catastrophic: float = 5e-5,
                 hardness: float = 2e9,
                 contact_area: float = 1e-4,
                 cycles_running_in: int = 100,
                 cycles_to_steady: int = 500,
                 wear_threshold_severe: float = 50e-6,
                 wear_threshold_catastrophic: float = 100e-6,
                 pressure_exponent: float = 1.0,
                 velocity_exponent: float = 1.0):
        self.K_running_in   = K_running_in
        self.K_steady       = K_steady
        self.K_severe       = K_severe
        self.K_catastrophic = K_catastrophic
        self.hardness       = max(hardness, 1e6)
        self.contact_area   = max(contact_area, 1e-12)
        self.N_ri           = cycles_running_in
        self.N_ss           = cycles_to_steady
        self.thr_severe     = wear_threshold_severe
        self.thr_cat        = wear_threshold_catastrophic
        self.p_exp          = pressure_exponent
        self.v_exp          = velocity_exponent

    # ------------------------------------------------------------------
    def get_wear_coefficient(self, cycle: int, total_depth_m: float) -> float:
        """Return phase-dependent dimensionless Archard K."""
        if total_depth_m >= self.thr_cat:
            return self.K_catastrophic
        if total_depth_m >= self.thr_severe:
            return self.K_severe
        if cycle <= self.N_ri:
            return self.K_running_in
        if cycle <= self.N_ss:
            frac = (cycle - self.N_ri) / max(1, self.N_ss - self.N_ri)
            return self.K_running_in + frac * (self.K_steady - self.K_running_in)
        return self.K_steady

    def get_wear_phase(self, cycle: int, total_depth_m: float) -> WearPhaseEnum:
        """Classify current wear phase."""
        if total_depth_m >= self.thr_cat:
            return WearPhaseEnum.CATASTROPHIC
        if total_depth_m >= self.thr_severe:
            return WearPhaseEnum.SEVERE
        if cycle <= self.N_ss:
            return WearPhaseEnum.RUNNING_IN
        return WearPhaseEnum.STEADY

    # ------------------------------------------------------------------
    def compute_wear_increment(self, F_normal: float, slip_distance_m: float,
                               cycle: int = 0, total_depth_m: float = 0.0,
                               **_) -> float:
        """
        Wear depth increment for one cycle [m].

        Args:
            F_normal:       Normal contact force [N]
            slip_distance_m: Slip path per cycle [m]  (= 4·δ_amplitude for harmonic)
            cycle:          Current cycle number
            total_depth_m:  Accumulated wear depth [m] (for phase dispatch)

        Returns:
            dh [m]  (≥ 0)
        """
        if F_normal <= 0.0 or slip_distance_m <= 0.0:
            return 0.0

        K = self.get_wear_coefficient(cycle, total_depth_m)
        H = self.hardness
        A = self.contact_area

        if self.p_exp != 1.0 or self.v_exp != 1.0:
            p = F_normal / A
            dV = K * (p ** self.p_exp) * (slip_distance_m ** self.v_exp) / H
        else:
            dV = K * F_normal * slip_distance_m / H   # [m³]

        return max(0.0, dV / A)


# =============================================================================
# MODEL 2: ENERGY-BASED WEAR (FOUVRY)
# =============================================================================

class EnergyBasedWearModel:
    """
    Fouvry et al. (2003) energy-based fretting wear.

    **Wear law** (per cycle)::

        E_d = μ × F_n × s          [J]  dissipated energy
        V   = α_V × max(0, E_d − E_th_per_cycle)   [m³]
        dh  = V / A                 [m]

    Typical values (steel-on-steel, fretting):
    - α_V ≈ 1 × 10⁻¹⁵ to 5 × 10⁻¹⁵  m³/J

    An optional cumulative energy threshold E_th can be set so that wear
    only begins once the total dissipated energy exceeds a critical value.

    References:
    - Fouvry et al. (2003) Wear 255:287-303
    - Paulin et al. (2008) Wear 264:743-753
    """

    def __init__(self,
                 alpha_energy: float = 5e-15,
                 contact_area: float = 1e-4,
                 energy_threshold: float = 0.0,
                 mu_ref: float = 0.12):
        self.alpha            = alpha_energy
        self.contact_area     = max(contact_area, 1e-12)
        self.energy_threshold = energy_threshold   # cumulative J threshold
        self.mu_ref           = mu_ref
        self._cum_energy: float = 0.0

    def reset(self):
        """Reset accumulated energy (call before a new analysis run)."""
        self._cum_energy = 0.0

    def compute_wear_increment(self, F_normal: float, slip_distance_m: float,
                               mu: float = None, **_) -> float:
        """
        Wear depth increment for one cycle [m].

        Args:
            F_normal:       Normal contact force [N]
            slip_distance_m: Slip path per cycle [m]
            mu:             Current friction coefficient (uses mu_ref if None)

        Returns:
            dh [m]  (≥ 0)
        """
        if F_normal <= 0.0 or slip_distance_m <= 0.0:
            return 0.0

        mu_use = mu if mu is not None else self.mu_ref
        E_d = mu_use * F_normal * slip_distance_m   # [J]
        self._cum_energy += E_d

        # Apply cumulative energy threshold
        if self._cum_energy < self.energy_threshold:
            return 0.0

        # Effective energy this cycle (only excess above threshold contributes)
        prev_cum = self._cum_energy - E_d
        if prev_cum < self.energy_threshold:
            # Partially above threshold this cycle
            E_eff = self._cum_energy - self.energy_threshold
        else:
            E_eff = E_d

        dV = self.alpha * max(0.0, E_eff)   # [m³]
        return max(0.0, dV / self.contact_area)


# =============================================================================
# MODEL 3: FRETTING WEAR (VINGSBO-SÖDERBERG)
# =============================================================================

class FrettingWearModel:
    """
    Vingsbo-Söderberg fretting map with regime-dispatched Archard wear.

    Regime boundaries (slip amplitude δ):
    - Stick          δ < 0.5 µm  → no wear
    - Partial slip   0.5 – 3 µm  → low wear (subsurface crack initiation)
    - Fretting       3 – 20 µm   → peak wear (oxide debris, 3rd body effect)
    - Gross sliding  δ ≥ 20 µm   → standard Archard sliding wear

    The **fretting** regime has the highest specific wear rate because
    oxidative debris accumulates in the contact without being expelled,
    acting as an abrasive 3rd body.

    Each regime uses a K multiplier × K_steady::

        K_eff = K_steady × {0, 0.3, 2.5, 1.0}

    References:
    - Vingsbo & Söderberg (1988) Wear 126:131-147
    - Fouvry et al. (1997) Wear 203:93-103
    - Hintikka et al. (2020) Tribol. Int. 143:106053
    """

    # Default Vingsbo-Söderberg boundaries [m]
    DELTA_STICK_M    = 0.5e-6
    DELTA_FRETTING_M = 3.0e-6
    DELTA_GROSS_M    = 20.0e-6

    # K multipliers relative to base Archard K_steady
    _K_MULT: Dict[WearRegimeEnum, float] = {
        WearRegimeEnum.STICK:        0.0,
        WearRegimeEnum.PARTIAL_SLIP: 0.3,
        WearRegimeEnum.FRETTING:     2.5,   # Peak — debris accumulation
        WearRegimeEnum.GROSS_SLIP:   1.0,
    }

    def __init__(self,
                 K_steady: float = 1e-6,
                 hardness: float = 2e9,
                 contact_area: float = 1e-4,
                 delta_stick_m: float = DELTA_STICK_M,
                 delta_fretting_m: float = DELTA_FRETTING_M,
                 delta_gross_m: float = DELTA_GROSS_M):
        self.K_steady      = K_steady
        self.hardness      = max(hardness, 1e6)
        self.contact_area  = max(contact_area, 1e-12)
        self.delta_stick   = delta_stick_m
        self.delta_fretting = delta_fretting_m
        self.delta_gross   = delta_gross_m

    def get_regime(self, slip_amplitude_m: float) -> WearRegimeEnum:
        """Classify slip amplitude into Vingsbo-Söderberg fretting regime."""
        if slip_amplitude_m < self.delta_stick:
            return WearRegimeEnum.STICK
        if slip_amplitude_m < self.delta_fretting:
            return WearRegimeEnum.PARTIAL_SLIP
        if slip_amplitude_m < self.delta_gross:
            return WearRegimeEnum.FRETTING
        return WearRegimeEnum.GROSS_SLIP

    def compute_wear_increment(self, F_normal: float, slip_distance_m: float,
                               slip_amplitude_m: float = None, **_) -> float:
        """
        Regime-dispatched fretting wear depth increment [m].

        Args:
            F_normal:         Normal contact force [N]
            slip_distance_m:  Total slip path per cycle [m]  (= 4·δ for harmonic)
            slip_amplitude_m: Half-amplitude of oscillation [m] (for regime lookup)
                              If None, defaults to slip_distance_m / 4

        Returns:
            dh [m]  (≥ 0)
        """
        if F_normal <= 0.0 or slip_distance_m <= 0.0:
            return 0.0

        amp = slip_amplitude_m if slip_amplitude_m is not None else slip_distance_m / 4.0
        regime = self.get_regime(amp)
        K_eff = self.K_steady * self._K_MULT[regime]
        if K_eff <= 0.0:
            return 0.0

        dV = K_eff * F_normal * slip_distance_m / self.hardness   # [m³]
        return max(0.0, dV / self.contact_area)


# =============================================================================
# MODEL 4: FATIGUE WEAR (DELAMINATION)
# =============================================================================

class FatigueWearModel:
    """
    Sub-surface fatigue wear via Miner's rule (delamination mechanism).

    **Mechanism**: Repeated micro-contact loading causes sub-surface crack
    initiation, propagation, and eventual delamination (plate-like wear fragments).

    **Fatigue life** at contact pressure p::

        N_f = C_f × p^(−m_f)      (contact-fatigue S-N curve)

    **Miner accumulation** per cycle::

        D += 1 / N_f(p)

    When D ≥ D_critical, a delamination event occurs:
    - dh_event [m] of material is removed
    - D is reduced by D_critical (residual damage preserved)

    A small background Archard contribution is always added to account
    for simultaneous adhesive wear between delamination events.

    References:
    - Waterhouse (1981) "Fretting Fatigue"
    - Fouvry et al. (1997), sub-surface crack model
    - Vingsbo & Söderberg (1988)
    """

    def __init__(self,
                 C_f: float = 1e18,
                 m_f: float = 4.0,
                 D_critical: float = 1.0,
                 delta_h_event: float = 0.5e-6,
                 K_background: float = 2e-8,
                 hardness: float = 2e9,
                 contact_area: float = 1e-4):
        self.C_f           = C_f
        self.m_f           = m_f
        self.D_critical    = D_critical
        self.delta_h_event = delta_h_event
        self.K_bg          = K_background
        self.hardness      = max(hardness, 1e6)
        self.contact_area  = max(contact_area, 1e-12)
        self._damage: float = 0.0

    def reset(self):
        """Reset Miner's damage counter."""
        self._damage = 0.0

    @property
    def damage(self) -> float:
        """Current Miner's fatigue damage fraction."""
        return self._damage

    def N_failure(self, contact_pressure_Pa: float) -> float:
        """
        Fatigue life [cycles] at given contact pressure [Pa].

        N_f = C_f × p^(−m_f)
        """
        p = max(contact_pressure_Pa, 1.0)
        return max(1.0, self.C_f * (p ** (-self.m_f)))

    def compute_wear_increment(self, F_normal: float, slip_distance_m: float,
                               **_) -> float:
        """
        Per-cycle fatigue wear depth increment [m].

        Accumulates Miner's damage; emits a delamination event (delta_h_event)
        when D ≥ D_critical, then subtracts D_critical from D.
        A background Archard contribution is always added.

        Args:
            F_normal:        Normal contact force [N]
            slip_distance_m: Slip path per cycle [m] (for background Archard)

        Returns:
            dh [m]  (≥ 0)
        """
        if F_normal <= 0.0:
            return 0.0

        p = F_normal / self.contact_area
        N_f = self.N_failure(p)
        self._damage += 1.0 / N_f

        # Background Archard (adhesive) contribution
        dh_bg = 0.0
        if slip_distance_m > 0.0:
            dh_bg = self.K_bg * F_normal * slip_distance_m / (
                self.hardness * self.contact_area)

        # Delamination event
        if self._damage >= self.D_critical:
            self._damage -= self.D_critical
            return self.delta_h_event + dh_bg

        return dh_bg


# =============================================================================
# FACTORY FUNCTION
# =============================================================================

def create_wear_model(model_type: str, params=None):
    """
    Factory — instantiate a wear model from a name string + WearModelParams.

    Args:
        model_type: ``'archard'`` | ``'energy'`` | ``'fretting'`` | ``'fatigue'``
        params:     ``WearModelParams`` instance from ``coupled_loosening_analyzer``
                    (or None for defaults).  Uses ``getattr`` duck-typing so any
                    object with the right attributes works.

    Returns:
        One of: ArchardWearModel, EnergyBasedWearModel, FrettingWearModel,
                FatigueWearModel

    Raises:
        ValueError: Unknown model_type string.
    """
    def _g(attr, default):
        return getattr(params, attr, default) if params is not None else default

    t = model_type.lower().strip()

    if t == 'archard':
        return ArchardWearModel(
            K_running_in=_g('K_running_in', 5e-6),
            K_steady=_g('K_steady', 1e-6),
            K_severe=_g('K_severe', 1e-5),
            K_catastrophic=_g('K_catastrophic', 5e-5),
            hardness=_g('hardness', 2e9),
            contact_area=_g('contact_area', 1e-4),
            cycles_running_in=_g('cycles_running_in', 100),
            cycles_to_steady=_g('cycles_to_steady', 500),
            wear_threshold_severe=_g('wear_threshold_severe', 50e-6),
            wear_threshold_catastrophic=_g('wear_threshold_catastrophic', 100e-6),
            pressure_exponent=_g('pressure_exponent', 1.0),
            velocity_exponent=_g('velocity_exponent', 1.0),
        )

    if t == 'energy':
        return EnergyBasedWearModel(
            alpha_energy=_g('alpha_energy', 5e-15),
            contact_area=_g('contact_area', 1e-4),
            energy_threshold=_g('energy_threshold', 0.0),
            mu_ref=_g('friction_for_energy', 0.12),
        )

    if t == 'fretting':
        return FrettingWearModel(
            K_steady=_g('K_steady', 1e-6),
            hardness=_g('hardness', 2e9),
            contact_area=_g('contact_area', 1e-4),
        )

    if t == 'fatigue':
        return FatigueWearModel(
            hardness=_g('hardness', 2e9),
            contact_area=_g('contact_area', 1e-4),
        )

    raise ValueError(
        f"Unknown wear model type '{model_type}'. "
        "Choose from: 'archard', 'energy', 'fretting', 'fatigue'"
    )
