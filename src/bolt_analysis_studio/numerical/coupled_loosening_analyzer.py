"""
Coupled Friction-Wear-Loosening Analyzer
=========================================

This module integrates friction evolution, wear accumulation, and loosening
mechanisms into a unified analysis framework. It captures the positive feedback
loop where:
  - Friction decreases over cycles
  - Wear accumulates and reduces preload
  - Lower preload reduces friction capacity
  - Easier slip leads to more wear and faster loosening

Key Features:
- Three-phase friction evolution model
- Archard wear model with preload coupling
- Junker loosening with torque balance
- Per-cycle state tracking
- Loosening rate computation

References:
- Hintikka et al. (2020) for friction evolution
- Junker (1969) for loosening mechanism
- Jiang et al. (2003) for two-stage model
- VDI 2230 (2015) for torque calculations

Author: Bolt Analysis Studio Team
Version: 4.0
Date: January 2026
"""

import numpy as np
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple, Callable
from enum import Enum
import warnings
import copy


# =============================================================================
# ENUMERATIONS
# =============================================================================

class LooseningRisk(Enum):
    """Risk level classification for loosening"""
    NEGLIGIBLE = "negligible"   # Margin > 2.0
    LOW = "low"                 # Margin 1.5-2.0
    MODERATE = "moderate"       # Margin 1.1-1.5
    HIGH = "high"               # Margin 1.0-1.1
    CRITICAL = "critical"       # Margin < 1.0 (loosening active)


class LooseningPhase(Enum):
    """
    Loosening phase classification.

    Two model families are available, selected by CoupledLooseningAnalyzer.loading_type:

    Transverse / Junker (loading_type='transverse' or 'combined') — Jiang 5-stage
    ──────────────────────────────────────────────────────────────────────────────
      STABLE          F/F₀ > 0.90, Stage II latch open  — nearly full preload
      NON_ROTATIONAL  F/F₀ > 0.75, Stage II latch open  — Stage I embedding active
      TRANSITION      Stage I: F/F₀ ≤ 0.75              — heavy Stage I loss
                      Stage II: F/F₀ > 0.55             — early rotational loosening
      ROTATIONAL      Stage II latch fired, F/F₀ > 0.20 — full Junker back-off
      RUNAWAY         F/F₀ ≤ 0.20 or self_lock_lost     — catastrophic

    Axial (loading_type='axial') — 3-stage axial model
    ──────────────────────────────────────────────────────────────────────────────
      AXIAL_STAGE_I   rapid initial embedding drop (first ~50 cycles)
      AXIAL_STAGE_II  slow fretting / creep decay (bulk of the fatigue life)
      AXIAL_STAGE_III fatigue / runaway (F/F₀ ≤ 0.40 or Miner's D ≥ 0.80)

    References:
        Jiang et al. (2003, 2004, 2007) — transverse two-stage model
        Wang et al. (2021) Eng. Fail. Anal. — three-stage axial criterion
        LOOSENING_STAGE_DEFINITIONS.md §3 — full boundary table
    """
    # ── Transverse / Junker loading — Jiang 5-stage model ────────────────────
    STABLE         = "stable"          # No loosening; full preload retained
    NON_ROTATIONAL = "non_rotational"  # Stage I: embedding, micro-slip, no nut rotation
    TRANSITION     = "transition"      # Stage I/II boundary region
    ROTATIONAL     = "rotational"      # Stage II: Junker nut back-off active
    RUNAWAY        = "runaway"         # Catastrophic: joint integrity lost

    # ── Axial loading — 3-stage axial model ──────────────────────────────────
    AXIAL_STAGE_I   = "axial_stage_i"   # Rapid initial drop: asperity crushing, embedding
    AXIAL_STAGE_II  = "axial_stage_ii"  # Slow steady decay: fretting wear, creep
    AXIAL_STAGE_III = "axial_stage_iii" # Rapid failure: fatigue crack / gross slip


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class FrictionEvolutionParams:
    """
    Three-phase friction evolution parameters.

    Phase 1 (Running-in): mu increases from mu_initial to mu_peak
    Phase 2 (Transition): mu decreases from mu_peak
    Phase 3 (Steady-state): mu approaches mu_steady

    Additional degradation may occur due to wear, temperature, contamination.
    """
    mu_initial: float = 0.15      # Initial friction coefficient
    mu_peak: float = 0.18         # Peak during running-in
    mu_steady: float = 0.10       # Steady-state value
    mu_minimum: float = 0.03      # Absolute minimum (critical)

    N1: int = 50                  # Running-in rise cycles
    N2: int = 200                 # Transition decay cycles
    N3: int = 2000                # Steady-state approach cycles

    # Degradation factors
    wear_degradation_rate: float = 0.01    # mu reduction per um of wear
    temperature_factor: float = 0.001      # mu reduction per degree C above 20

    # M9: Separate thread/bearing friction initial values
    # When set (> 0), these override mu_initial for the respective surface.
    mu_thread_initial: float = 0.0         # Override for thread (0 = use mu_initial)
    mu_bearing_initial: float = 0.0        # Override for bearing (0 = use mu_initial)

    def get_mu_initial_thread(self) -> float:
        """Get initial friction for thread surface (M9)."""
        return self.mu_thread_initial if self.mu_thread_initial > 0 else self.mu_initial

    def get_mu_initial_bearing(self) -> float:
        """Get initial friction for bearing surface (M9)."""
        return self.mu_bearing_initial if self.mu_bearing_initial > 0 else self.mu_initial

    def compute_mu(self, cycles: int, wear_depth_um: float = 0.0,
                   temperature: float = 20.0) -> float:
        """
        Compute friction coefficient at given cycle with all effects.

        Args:
            cycles: Current cycle count
            wear_depth_um: Accumulated wear depth in micrometers
            temperature: Current temperature in Celsius

        Returns:
            Current friction coefficient
        """
        # Base three-phase model
        term1 = (self.mu_peak - self.mu_initial) * \
                (1 - np.exp(-cycles / self.N1)) * np.exp(-cycles / self.N2)
        term2 = (self.mu_steady - self.mu_initial) * (1 - np.exp(-cycles / self.N3))

        mu_base = self.mu_initial + term1 + term2

        # Wear degradation
        mu_wear_effect = self.wear_degradation_rate * wear_depth_um

        # Temperature effect (friction decreases with temperature)
        temp_above_ref = max(0, temperature - 20.0)
        mu_temp_effect = self.temperature_factor * temp_above_ref

        # Combined
        mu_final = mu_base - mu_wear_effect - mu_temp_effect

        # Enforce minimum
        return max(mu_final, self.mu_minimum)

    def compute_mu_for_surface(self, surface: str, cycles: int,
                                wear_depth_um: float = 0.0,
                                temperature: float = 20.0) -> float:
        """
        Compute friction for a specific surface with independent initial values (M9).

        Args:
            surface: 'thread' or 'bearing'
            cycles: Current cycle count
            wear_depth_um: Accumulated wear depth [um]
            temperature: Temperature [C]

        Returns:
            Surface-specific friction coefficient
        """
        # Get surface-specific initial mu
        if surface == 'thread':
            mu0 = self.get_mu_initial_thread()
        elif surface == 'bearing':
            mu0 = self.get_mu_initial_bearing()
        else:
            mu0 = self.mu_initial

        # Scale the three-phase model relative to this surface's initial value
        scale = mu0 / self.mu_initial if self.mu_initial > 0 else 1.0
        mu_peak_scaled = self.mu_peak * scale
        mu_steady_scaled = self.mu_steady * scale

        # Three-phase model with scaled values
        term1 = (mu_peak_scaled - mu0) * \
                (1 - np.exp(-cycles / self.N1)) * np.exp(-cycles / self.N2)
        term2 = (mu_steady_scaled - mu0) * (1 - np.exp(-cycles / self.N3))

        mu_base = mu0 + term1 + term2

        # Wear and temperature degradation (same as compute_mu)
        mu_wear_effect = self.wear_degradation_rate * wear_depth_um
        temp_above_ref = max(0, temperature - 20.0)
        mu_temp_effect = self.temperature_factor * temp_above_ref

        mu_final = mu_base - mu_wear_effect - mu_temp_effect
        return max(mu_final, self.mu_minimum)


@dataclass
class WearModelParams:
    """
    Advanced Time-Varying Wear Model Parameters.

    Combines multiple wear mechanisms:
    1. Archard adhesive/abrasive wear: V = K * F * s / H
    2. Energy-based wear (Fouvry): V = α * E_d (dissipated energy)
    3. Fretting wear with threshold effects
    4. Temperature-dependent hardness reduction

    Time/cycle evolution:
    - Running-in phase: Higher K, asperity removal
    - Steady-state: Constant K
    - Severe wear: Accelerated K when crossing threshold

    References:
    - Archard (1953) for adhesive wear law
    - Fouvry et al. (2003) for energy-based approach
    - Hintikka et al. (2020) for fretting-loosening coupling
    """
    # Archard parameters
    K_archard: float = 1e-6           # Dimensionless wear coefficient
    hardness: float = 2e9             # Surface hardness [Pa] (Vickers ~3 GPa for steel)
    contact_area: float = 1e-4        # Nominal contact area [m^2]

    # Three-phase wear evolution coefficients
    K_running_in: float = 5e-6        # Higher K during running-in (asperity removal)
    K_steady: float = 1e-6            # Steady-state K
    K_severe: float = 1e-5            # Severe wear K (surface damage)
    K_catastrophic: float = 5e-5      # Catastrophic wear K (near failure)

    # Phase transition parameters
    cycles_running_in: int = 100      # Running-in duration [cycles]
    cycles_to_steady: int = 500       # Full transition to steady-state
    wear_threshold_severe: float = 50e-6    # 50 μm threshold for severe wear
    wear_threshold_catastrophic: float = 100e-6  # 100 μm threshold

    # Energy-based wear (Fouvry model) - Fouvry et al. (2003): ~1e-15 to 1e-14 m³/J
    alpha_energy: float = 5e-15       # Energy wear coefficient [m³/J] (steel on steel, fretting)
    friction_for_energy: float = 0.12  # Reference friction for energy calc

    # Temperature effects
    temp_ref: float = 20.0            # Reference temperature [°C]
    hardness_temp_coeff: float = 0.001  # Hardness reduction per °C above ref

    # Fretting parameters
    fretting_threshold_um: float = 5.0  # Gross slip threshold [μm]
    fretting_enhancement: float = 1.5   # Enhancement factor in fretting regime

    # Generalized Archard exponents (Goryacheva 1998, Argatov 2022)
    # dh/dt = K_w * p^alpha * v^beta — nonlinear pressure/velocity dependence
    pressure_exponent: float = 1.2      # α > 1 → accelerating wear at high contact pressure
    velocity_exponent: float = 0.8      # β < 1 → sub-linear velocity dependence (typical fretting)

    # Fouvry energy wear threshold (Fouvry et al. 2003)
    # V = α_V * max(0, ΣE_d - E_th)  — no wear below energy threshold
    energy_threshold: float = 0.0       # E_th [J] — activation energy for wear onset

    # Wear-compliance feedback (wear increases bolt elongation → preload loss)
    # δ_wear = P*L / (A*E) contribution from worn geometry
    # compliance_growth_rate controls how fast compliance increases with wear
    compliance_growth_rate: float = 0.05  # Nonlinear compliance growth exponent

    # Accumulated state
    _accumulated_energy: float = 0.0
    _accumulated_cycles: int = 0

    def get_wear_coefficient(self, cycles: int, wear_depth: float,
                            temperature: float = 20.0,
                            slip_amplitude_um: float = 100.0) -> float:
        """
        Get current wear coefficient based on multi-factor state.

        The wear coefficient evolves through distinct phases:
        1. Running-in (0-100 cycles): High K, asperity removal
        2. Steady-state (100-severe): Constant K_steady
        3. Severe (>50 μm): Elevated K due to surface damage
        4. Catastrophic (>100 μm): Near-failure regime

        Args:
            cycles: Current cycle count
            wear_depth: Accumulated wear depth [m]
            temperature: Current temperature [°C]
            slip_amplitude_um: Slip amplitude [μm]

        Returns:
            Effective wear coefficient
        """
        # Base coefficient from cycle-dependent phase
        if cycles < self.cycles_running_in:
            # Phase 1: Running-in (exponential decay from K_running_in)
            progress = cycles / self.cycles_running_in
            # S-curve transition for smoother behavior
            smoothed_progress = 3 * progress**2 - 2 * progress**3
            K_base = self.K_running_in - (self.K_running_in - self.K_steady) * smoothed_progress

        elif cycles < self.cycles_to_steady:
            # Phase 1b: Transition to full steady-state
            progress = (cycles - self.cycles_running_in) / (self.cycles_to_steady - self.cycles_running_in)
            K_base = self.K_steady

        else:
            # Phase 2: Steady-state
            K_base = self.K_steady

        # Wear-depth dependent severity enhancement
        if wear_depth > self.wear_threshold_catastrophic:
            # Phase 4: Catastrophic wear
            K_wear = self.K_catastrophic
        elif wear_depth > self.wear_threshold_severe:
            # Phase 3: Severe wear (interpolate)
            progress = (wear_depth - self.wear_threshold_severe) / \
                      (self.wear_threshold_catastrophic - self.wear_threshold_severe)
            K_wear = self.K_severe + (self.K_catastrophic - self.K_severe) * progress
        else:
            K_wear = K_base

        # Temperature correction (hardness decreases with temperature)
        temp_factor = 1.0
        if temperature > self.temp_ref:
            delta_T = temperature - self.temp_ref
            # Hardness reduction increases wear coefficient
            hardness_reduction = 1.0 - self.hardness_temp_coeff * delta_T
            hardness_reduction = max(0.3, hardness_reduction)  # Cap at 70% reduction
            temp_factor = 1.0 / hardness_reduction

        # Fretting enhancement (low amplitude = more damage per unit slip)
        fretting_factor = 1.0
        if slip_amplitude_um < self.fretting_threshold_um * 10:
            # In fretting regime, damage per unit slip is higher
            fretting_factor = self.fretting_enhancement

        # Combined coefficient
        K_effective = K_wear * temp_factor * fretting_factor

        return K_effective

    def compute_wear_increment(self, normal_force: float, slip_distance: float,
                               cycles: int, current_depth: float,
                               temperature: float = 20.0,
                               friction_coeff: float = None) -> Tuple[float, Dict[str, float]]:
        """
        Compute wear depth increment with nonlinear multi-mechanism model.

        Implements Generalized Archard (Goryacheva 1998) + Fouvry energy wear
        with positive feedback through wear-compliance coupling.

        Models:
        1. Generalized Archard: dh = K * (p/H)^α * v^β * ds
           where α, β are nonlinear exponents (Goryacheva 1998, Argatov 2022)
        2. Fouvry energy wear: dV = α_V * max(0, E_d - E_th)
           with energy threshold for wear onset (Fouvry et al. 2003)
        3. Wear-depth acceleration: existing wear increases effective K
           via surface roughening feedback (McColl et al. 2004)

        Args:
            normal_force: Normal contact force [N]
            slip_distance: Sliding distance this cycle [m]
            cycles: Current cycle count
            current_depth: Current accumulated wear depth [m]
            temperature: Current temperature [°C]
            friction_coeff: Current friction coefficient (for energy calc)

        Returns:
            Tuple of (total wear increment [m], breakdown dict)
        """
        if friction_coeff is None:
            friction_coeff = self.friction_for_energy

        slip_amplitude_um = slip_distance * 1e6 / 4  # Convert to amplitude

        # Get effective wear coefficient (phase-dependent)
        K = self.get_wear_coefficient(cycles, current_depth, temperature, slip_amplitude_um)

        # Temperature-adjusted hardness
        H_effective = self.hardness
        if temperature > self.temp_ref:
            delta_T = temperature - self.temp_ref
            H_effective *= max(0.3, 1.0 - self.hardness_temp_coeff * delta_T)

        # 1. GENERALIZED ARCHARD (nonlinear pressure & velocity exponents)
        # dh = K * (F/A)^α * v^β * ds / H^α
        # References: Goryacheva (1998), Argatov & Chai (2022)
        dh_archard = 0.0
        if self.contact_area > 0 and H_effective > 0:
            contact_pressure = normal_force / self.contact_area  # Pa
            # Normalized pressure (p/H) raised to nonlinear exponent
            p_normalized = contact_pressure / H_effective
            # Sliding velocity proxy (slip_distance per cycle, assume 1 Hz reference)
            v_proxy = max(slip_distance, 1e-12)  # Avoid zero

            dh_archard = (K * (p_normalized ** self.pressure_exponent)
                          * (v_proxy ** self.velocity_exponent))

            # Surface roughening feedback: existing wear increases local K
            # Based on McColl et al. (2004) — worn surfaces have more asperities
            if current_depth > 0:
                roughening_factor = 1.0 + self.compliance_growth_rate * (current_depth * 1e6)  # μm scale
                dh_archard *= min(roughening_factor, 3.0)  # Cap at 3x enhancement

        # 2. FOUVRY ENERGY WEAR with threshold (Fouvry et al. 2003)
        # V = α_V * max(0, ΣE_d - E_th)
        # Wear only begins after energy threshold is exceeded
        E_dissipated = friction_coeff * normal_force * slip_distance
        self._accumulated_energy += E_dissipated

        dh_energy = 0.0
        if self.contact_area > 0:
            # Energy above threshold contributes to wear
            E_effective = max(0, E_dissipated - self.energy_threshold / max(cycles, 1))
            dV_energy = self.alpha_energy * E_effective

            # Nonlinear energy scaling: wear per unit energy increases
            # as accumulated energy grows (surface degradation feedback)
            if self._accumulated_energy > 0:
                energy_ratio = self._accumulated_energy / max(E_dissipated * 1000, 1e-20)
                # Logarithmic acceleration: slow initially, faster as surface degrades
                energy_acceleration = 1.0 + 0.1 * np.log1p(energy_ratio)
                dV_energy *= min(energy_acceleration, 2.5)  # Cap at 2.5x

            dh_energy = dV_energy / self.contact_area

        self._accumulated_cycles = cycles

        # 3. COMBINED WEAR per reference Section 39.3:
        # dh_total = max(dh_Archard, 0.5×dh_Fouvry) + 0.3×dh_Fouvry
        dh_total = max(dh_archard, 0.5 * dh_energy) + 0.3 * dh_energy

        # Breakdown for analysis
        breakdown = {
            'dh_archard': dh_archard,
            'dh_energy': dh_energy,
            'dh_total': dh_total,
            'K_effective': K,
            'H_effective': H_effective,
            'E_dissipated': E_dissipated,
            'E_accumulated': self._accumulated_energy,
            'wear_phase': self._get_wear_phase(cycles, current_depth),
        }

        return dh_total, breakdown

    def _get_wear_phase(self, cycles: int, wear_depth: float) -> str:
        """Get current wear phase description."""
        if cycles < self.cycles_running_in:
            return "running_in"
        elif wear_depth > self.wear_threshold_catastrophic:
            return "catastrophic"
        elif wear_depth > self.wear_threshold_severe:
            return "severe"
        else:
            return "steady_state"

    def get_wear_rate(self, cycles: int, wear_depth: float,
                     normal_force: float, temperature: float = 20.0) -> float:
        """
        Get instantaneous wear rate [m/cycle] for given conditions.

        Useful for plotting wear rate evolution over time.
        """
        K = self.get_wear_coefficient(cycles, wear_depth, temperature)

        # Estimate slip distance per cycle (typical for transverse vibration)
        typical_slip_per_cycle = 1e-3  # 1 mm per cycle estimate

        H_effective = self.hardness
        if temperature > self.temp_ref:
            delta_T = temperature - self.temp_ref
            H_effective *= max(0.3, 1.0 - self.hardness_temp_coeff * delta_T)

        rate = K * normal_force * typical_slip_per_cycle / (H_effective * self.contact_area)
        return rate


@dataclass
class TwoStageLooseningParams:
    """
    Two-Stage S-Curve Preload Decay Model Parameters.

    Based on Jiang et al. (2003) and Yang et al. (2019):
    - Stage I: Early rapid loss from plastic deformation at thread roots
    - Stage II: Gradual rotational loosening (Junker mechanism)

    The S-curve profile emerges from the combination of:
    1. Fast exponential decay in Stage I
    2. Slower linear/exponential decay in Stage II
    3. Transition region creating the characteristic "knee"

    References:
    - Jiang, Y. et al. (2003) ASME J. Mech. Des. 125(3): 518-526
    - Yang, X. et al. (2019) Shock and Vibration, 2036509
    """
    # Stage I (plastic deformation dominated)
    N_stage1: int = 200                   # Characteristic cycles for Stage I
    delta_F1_ratio: float = 0.15          # Max preload loss ratio in Stage I (10-40% typical)

    # Stage II (rotational loosening dominated)
    N_stage2: int = 2000                  # Characteristic cycles for Stage II onset
    k_stage2: float = 0.0003              # Stage II decay rate (per cycle); 1e-4 to 1e-3 gives visible curvature over 1-10k cycles (Lu 2024 / Jiang 2003 calibration)

    # S-curve shape parameters
    transition_sharpness: float = 3.0     # Controls knee sharpness (higher = sharper)

    # Displacement amplitude effect (key finding from Yang 2019)
    # Higher displacement = faster loosening
    displacement_exponent: float = 2.0    # F_loss ~ disp^exponent

    # Threshold displacement below which no significant loosening occurs
    displacement_threshold_mm: float = 0.15  # Below this, minimal loosening

    # M8: Junker loosening coefficient (formerly hardcoded 0.3)
    # C = 0.1-0.5 for lubricated, 0.5-2.0 for dry (more stick-slip)
    # Calibrated to match Junker test data (~10-50% preload loss over 1000 cycles)
    C_loosening: float = 0.3

    # M9: Displacement-driven loosening coefficient (for Junker machine / controlled displacement)
    # Separate from C_loosening; uses helix-geometry formula:
    #   d_theta = C_disp * tan(helix_angle) * slip_amplitude / d2
    # Calibrated: C_disp=0.03 → 50% preload loss in ~7000-12000 cycles for M12×1.75 at δ=0.5mm
    C_disp_loosening: float = 0.03

    # ── Curve-shape enhancements (2026-04-23) ─────────────────────────────────
    # Damped-exponential Stage II asymptote: per-cycle d_theta is multiplied by
    #   gap = max(0, (F/F0 − F_inf_ratio) / (1 − F_inf_ratio))
    # so the rate decays smoothly to zero as preload approaches the floor F∞,
    # producing the natural concave shape seen in Junker tests instead of a
    # linear segment that hits a hard cap.
    F_infinity_ratio: float = 0.20         # asymptotic preload floor F∞/F₀

    # Friction-recovery feedback gain: amplifies d_mu/h_um in _update_friction_wear.
    # Larger values create a sharper positive-feedback loop (μ↓ → slip↑ → wear↑ → μ↓),
    # which converts straight Stage II tails into clearly concave curves.
    # Default 1.0 preserves the historical 0.001 µ/µm calibration.
    friction_recovery_gain: float = 1.0

    # Norton-Bailey creep overlay (off by default; enable for gasketed/polymer joints).
    # Adds ΔF_creep(N) = k_sys · creep_coefficient · (N / creep_N_ref)^creep_exponent
    # as a smooth log-time concave bend on top of the cyclic loss budget.
    creep_coefficient: float = 0.0          # ε₀ — strain-equivalent gain [m]
    creep_exponent: float = 0.25            # n — Norton-Bailey exponent
    creep_N_ref: float = 1000.0             # reference cycles for normalisation

    # Stochastic per-cycle slip (Gaussian smearing). 0 = deterministic.
    # The d_theta increment is multiplied by (1 + N(0, noise_amplitude)),
    # turning piecewise-linear segments into noisy curves while preserving
    # the mean trajectory.
    noise_amplitude: float = 0.0

    def compute_scurve_factor(self, cycle: int, displacement_mm: float) -> float:
        """
        Compute S-curve preload loss factor at given cycle.

        Returns a factor 0-1 representing fraction of preload lost.
        The S-curve has characteristic shape:
        - Rapid rise in Stage I (plastic deformation)
        - Knee/transition region
        - Slower rise in Stage II (rotational)
        - Asymptotic approach to maximum loss

        Args:
            cycle: Current cycle number
            displacement_mm: Transverse displacement amplitude [mm]

        Returns:
            Preload loss factor (0 = no loss, 1 = complete loss)
        """
        if cycle <= 0:
            return 0.0

        # Check displacement threshold
        if displacement_mm < self.displacement_threshold_mm:
            # Below threshold: only minor embedding losses
            embedding_factor = 0.02 * (1 - np.exp(-cycle / 500))
            return embedding_factor

        # Displacement effect factor (normalized to reference 0.65mm)
        disp_factor = (displacement_mm / 0.65) ** self.displacement_exponent
        disp_factor = min(disp_factor, 5.0)  # Cap at 5x

        # Effective characteristic cycles (faster for larger displacement)
        N1_eff = self.N_stage1 / disp_factor
        N2_eff = self.N_stage2 / disp_factor

        # Stage I: Exponential plastic deformation loss
        # F_loss_1 = delta_F1 * (1 - exp(-N/N1))
        stage1_loss = self.delta_F1_ratio * (1 - np.exp(-cycle / N1_eff))

        # Stage II: Exponential saturation rotational loosening (Jiang 2003, Yang 2019)
        # Replaces the previous linear accumulation; the exponential form naturally
        # decelerates as the preload approaches its floor — matching real Junker curves.
        # Rate constant k_stage2 used as decay rate: tau = 1 / (k_stage2 * disp_factor)
        if cycle > N1_eff:
            # Smooth onset transition (sigmoid)
            transition = 1 / (1 + np.exp(-self.transition_sharpness * (cycle - N1_eff) / N1_eff))

            cycles_in_stage2 = max(0, cycle - N1_eff)
            delta_F2_max = max(0.0, 0.85 - self.delta_F1_ratio)

            # Exponential saturation: F_loss_2 = ΔF2_max * (1 - exp(-k2 * disp * N2))
            # Self-decelerating: fast early loss that asymptotes to ΔF2_max
            stage2_loss = delta_F2_max * (1.0 - np.exp(
                -self.k_stage2 * disp_factor * cycles_in_stage2)) * transition
        else:
            stage2_loss = 0.0

        # Total loss (capped at 95%)
        total_loss = min(stage1_loss + stage2_loss, 0.95)

        return total_loss


@dataclass
class ThreadGeometryParams:
    """Thread geometry for torque calculations."""
    pitch: float = 2.0e-3             # Thread pitch [m]
    pitch_diameter: float = 14.7e-3   # Pitch diameter d2 [m]
    major_diameter: float = 16.0e-3   # Major diameter [m]
    flank_angle: float = np.radians(30)  # Half flank angle [rad]
    num_engaged_threads: int = 8      # Number of engaged threads

    @property
    def helix_angle(self) -> float:
        """Thread helix angle [rad]."""
        return np.arctan(self.pitch / (np.pi * self.pitch_diameter))

    @property
    def helix_coupling_factor(self) -> float:
        """Axial-torsional coupling factor p/(2*pi) [m/rad]."""
        return self.pitch / (2 * np.pi)

    @property
    def mean_radius(self) -> float:
        """Mean thread radius [m]."""
        return self.pitch_diameter / 2


@dataclass
class BearingGeometryParams:
    """Bearing surface geometry for torque calculations."""
    inner_diameter: float = 17.0e-3   # Hole diameter [m]
    outer_diameter: float = 24.0e-3   # Under-head diameter [m]

    @property
    def effective_radius(self) -> float:
        """Load-weighted effective radius [m]."""
        r_o = self.outer_diameter / 2
        r_i = self.inner_diameter / 2
        if r_o > r_i:
            return (2/3) * (r_o**3 - r_i**3) / (r_o**2 - r_i**2)
        return r_o

    @property
    def contact_area(self) -> float:
        """Annular contact area [m^2]."""
        return np.pi / 4 * (self.outer_diameter**2 - self.inner_diameter**2)


@dataclass
class LooseningState:
    """Current state of the loosening process."""
    cycle: int = 0

    # Friction state
    mu_thread: float = 0.15
    mu_bearing: float = 0.15
    mu_critical: float = 0.0          # Critical friction for self-loosening

    # Wear state
    thread_wear_depth: float = 0.0    # [m]
    bearing_wear_depth: float = 0.0   # [m]
    total_wear_depth: float = 0.0     # [m]
    wear_phase: str = "initial"       # running_in, steady_state, severe, catastrophic

    # Preload state
    preload: float = 0.0              # [N]
    preload_initial: float = 0.0      # [N]
    preload_ratio: float = 1.0        # F_p / F_p0

    # Loosening state
    loosening_angle: float = 0.0           # [rad]
    loosening_angle_deg: float = 0.0       # [deg]
    loosening_rate: float = 0.0            # [rad/cycle]
    cumulative_rotation_deg: float = 0.0   # cumulative |Δθ| [deg] — LMQ §12.1 boundary input

    # Torque state
    T_pitch: float = 0.0              # [N.m]
    T_thread: float = 0.0             # [N.m]
    T_bearing: float = 0.0            # [N.m]
    T_resistance: float = 0.0         # [N.m]
    T_net: float = 0.0                # [N.m]
    torque_margin: float = 0.0        # T_resistance / T_pitch

    # Friction margin (mu_avg / mu_critical)
    friction_margin: float = 0.0

    # Preload loss breakdown
    loss_rotational: float = 0.0      # [N]
    loss_wear: float = 0.0            # [N]
    loss_embedding: float = 0.0       # [N]
    loss_thermal: float = 0.0         # [N] (H3)

    # Classification
    phase: LooseningPhase = LooseningPhase.STABLE
    risk: LooseningRisk = LooseningRisk.NEGLIGIBLE

    # Slip state
    bearing_slipping: bool = False
    thread_slipping: bool = False
    self_lock_lost: bool = False          # True once torque margin < 1 — ISO 16130 warning trigger
    damage_fraction: float = 0.0          # Miner's rule D = Σ(1/N_f) per cycle — Phase E (M15)

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            'cycle': self.cycle,
            'mu_thread': self.mu_thread,
            'mu_bearing': self.mu_bearing,
            'mu_critical': self.mu_critical,
            'friction_margin': self.friction_margin,
            'thread_wear_um': self.thread_wear_depth * 1e6,
            'bearing_wear_um': self.bearing_wear_depth * 1e6,
            'total_wear_um': self.total_wear_depth * 1e6,
            'wear_phase': self.wear_phase,
            'preload': self.preload,
            'preload_ratio': self.preload_ratio,
            'loosening_angle_deg': self.loosening_angle_deg,
            'cumulative_rotation_deg': self.cumulative_rotation_deg,
            'loosening_rate_deg_cycle': np.degrees(self.loosening_rate),
            'T_pitch': self.T_pitch,
            'T_resistance': self.T_resistance,
            'torque_margin': self.torque_margin,
            'phase': self.phase.value,
            'risk': self.risk.value,
            'bearing_slipping': self.bearing_slipping,
            'thread_slipping': self.thread_slipping,
            'damage_fraction': self.damage_fraction,
        }


@dataclass
class LooseningResults:
    """Complete results from loosening analysis."""
    # Arrays (one entry per cycle)
    cycles: np.ndarray = field(default_factory=lambda: np.array([]))
    preload: np.ndarray = field(default_factory=lambda: np.array([]))
    preload_ratio: np.ndarray = field(default_factory=lambda: np.array([]))
    mu_thread: np.ndarray = field(default_factory=lambda: np.array([]))
    mu_bearing: np.ndarray = field(default_factory=lambda: np.array([]))
    total_wear_um: np.ndarray = field(default_factory=lambda: np.array([]))
    loosening_angle_deg: np.ndarray = field(default_factory=lambda: np.array([]))
    loosening_rate: np.ndarray = field(default_factory=lambda: np.array([]))
    torque_margin: np.ndarray = field(default_factory=lambda: np.array([]))
    friction_margin: np.ndarray = field(default_factory=lambda: np.array([]))

    # Scalar results
    final_preload_ratio: float = 0.0
    total_loosening_deg: float = 0.0
    cycles_to_50_percent: int = 0
    cycles_to_loosening_onset: int = 0
    max_loosening_rate: float = 0.0
    phase_at_end: LooseningPhase = LooseningPhase.STABLE
    mu_critical: float = 0.0

    # Miner's rule fatigue damage (M15 / Phase E)
    miner_damage: np.ndarray = field(default_factory=lambda: np.array([]))
    miner_damage_final: float = 0.0        # D at end of simulation
    cycles_to_failure_miner: int = 0       # cycle when D ≥ 1.0 (0 = not reached)

    # State history
    states: List[LooseningState] = field(default_factory=list)


# =============================================================================
# MAIN ANALYZER CLASS
# =============================================================================

class CoupledLooseningAnalyzer:
    """
    Coupled Friction-Wear-Loosening Analyzer.

    This class integrates all loosening mechanisms with full coupling:
    - Friction evolution affects resistance torques
    - Wear affects preload and may affect friction
    - Preload loss affects friction capacity
    - Positive feedback loop captured accurately

    Usage:
        analyzer = CoupledLooseningAnalyzer(
            thread_geometry=ThreadGeometryParams(pitch=2e-3, ...),
            bearing_geometry=BearingGeometryParams(inner_diameter=17e-3, ...),
            friction_params=FrictionEvolutionParams(mu_initial=0.15, ...),
            wear_params=WearModelParams(K_archard=1e-6, ...)
        )
        results = analyzer.run_analysis(
            preload_initial=50000,
            F_transverse=5000,
            n_cycles=2000
        )
    """

    def __init__(self,
                 thread_geometry: ThreadGeometryParams = None,
                 bearing_geometry: BearingGeometryParams = None,
                 friction_params: FrictionEvolutionParams = None,
                 wear_params: WearModelParams = None,
                 two_stage_params: TwoStageLooseningParams = None,
                 k_bolt: float = 500e6,      # Bolt stiffness [N/m]
                 k_member: float = 1500e6,   # Member stiffness [N/m]
                 transverse_displacement_mm: float = 0.65,  # Transverse disp [mm]
                 thread_contact: 'ThreadContact' = None,
                 bearing_contact: 'BearingContact' = None,
                 grip_length: float = 0.048,
                 alpha_bolt: float = 12e-6,
                 alpha_member: float = 12e-6,
                 slip_onset_factor: float = 0.46,
                 sun_curve_params: 'SuNCurveParams' = None,
                 wear_model_type: str = 'archard',
                 loading_type: str = 'transverse',
                 n_stage_i_cycles: int = 50,
                 adaptive_stepping: bool = False):
                 # slip_onset_factor: Pai-Hess (2002) empirical correction — actual slip
                 # initiates at ~46 % of the classical Coulomb threshold µ×N.
                 # Set to 1.0 to revert to classical (unconservative for Junker tests).
                 # sun_curve_params: Su-N curve for Miner's rule damage (Phase E / M15).
                 #   None → SuNCurveParams() defaults (M16, Kt=3.5, A_s=157 mm²).
                 # wear_model_type: Pluggable wear model (Phase 3.2).
                 #   'archard' (default), 'energy', 'fretting', 'fatigue'.
                 # loading_type: Stage classification model.
                 #   'transverse' (default) → 5-stage Jiang (Junker mechanism).
                 #   'axial'                → 3-stage axial model (embedding/fretting/fatigue).
                 #   'combined'             → 5-stage Jiang (transverse mechanism dominant).
                 #   Any other value        → falls back to 'transverse'.
                 # n_stage_i_cycles: Axial model only. Cycles for Stage I rapid-drop phase.
                 #   Default 50 matches Jiang (2003) "first 5–50 cycles" observation.
        """
        Initialize the coupled analyzer.

        Args:
            thread_geometry: Thread geometry parameters
            bearing_geometry: Bearing geometry parameters
            friction_params: Friction evolution parameters
            wear_params: Wear model parameters
            two_stage_params: Two-stage S-curve model parameters (Jiang/Yang)
            k_bolt: Bolt axial stiffness [N/m]
            k_member: Clamped member stiffness [N/m]
            transverse_displacement_mm: Transverse displacement amplitude [mm]
            thread_contact: Optional ThreadContact object (H2). If provided,
                geometry is extracted and friction/wear state is synced each cycle.
            bearing_contact: Optional BearingContact object (H2). If provided,
                geometry is extracted and friction/wear state is synced each cycle.
            grip_length: Bolt grip length [m] for thermal expansion (H3)
            alpha_bolt: Bolt thermal expansion coefficient [1/K] (H3)
            alpha_member: Member thermal expansion coefficient [1/K] (H3)
        """
        # CRITICAL FIX: Use deep copies to ensure complete parameter independence
        # between analyzer instances. This prevents state leakage where accumulated
        # wear/friction state from one analysis affects another analysis.
        self.thread = copy.deepcopy(thread_geometry or ThreadGeometryParams())
        self.bearing = copy.deepcopy(bearing_geometry or BearingGeometryParams())
        self.friction = copy.deepcopy(friction_params or FrictionEvolutionParams())
        self.wear = copy.deepcopy(wear_params or WearModelParams())
        self.two_stage = copy.deepcopy(two_stage_params or TwoStageLooseningParams())

        # H2: Contact object integration
        self._thread_contact = thread_contact
        self._bearing_contact = bearing_contact

        # Extract geometry from Contact objects if provided (H2)
        if thread_contact is not None:
            self._extract_from_thread_contact(thread_contact)
        if bearing_contact is not None:
            self._extract_from_bearing_contact(bearing_contact)

        self.k_bolt = k_bolt
        self.k_member = k_member
        self.transverse_displacement_mm = transverse_displacement_mm

        # H3: Thermal parameters
        self.grip_length = grip_length
        self.alpha_bolt = alpha_bolt
        self.alpha_member = alpha_member

        # System stiffness
        self.k_system = (k_bolt * k_member) / (k_bolt + k_member)

        # State
        self.state = LooseningState()
        self.history: List[LooseningState] = []
        self.initial_preload: float = 0.0  # Set in run_analysis

        # Alias for S-curve parameters
        self.scurve_params = self.two_stage

        # Phase C: Pai-Hess (2002) slip onset correction
        # Empirical factor: actual Junker slip threshold is ~46 % of µ×N
        self.slip_onset_factor: float = float(slip_onset_factor)

        # Phase E: Su-N curve for per-cycle Miner's rule damage accumulation (M15)
        self._sun_curve = SuNCurveModel(sun_curve_params or SuNCurveParams())

        # Phase 3.2: Pluggable wear model dispatch
        self.wear_model_type: str = wear_model_type
        self._wear_total_depth_m: float = 0.0
        try:
            from .wear_models import create_wear_model as _cwm
            self._wear_model = _cwm(wear_model_type, self.wear)
        except Exception:
            self._wear_model = None  # fallback → inline Archard in _update_friction_wear

        # ── Jiang (2004) Stage II one-way latch ──────────────────────────────
        # Set True the first time cumulative_rotation_deg reaches 0.5°.
        # Never resets within a single analysis run — Stage II is physically
        # irreversible once initiated. See _classify_phase() for the full
        # literature derivation.
        self._stage_II_triggered: bool = False

        # ── Standards-compliance warning guard ───────────────────────────────
        # Emitted once per run when preload retention first drops below the
        # DIN 25201-4 (80 %) / ISO 16130 (85 %) thresholds.
        # See _check_self_lock() for the full citation.
        self._iso16130_warning_emitted: bool = False

        # ── Axial 3-stage model state ─────────────────────────────────────────
        # loading_type controls which _classify_phase*() branch is used.
        # 'transverse' and 'combined' → Jiang 5-stage.
        # 'axial'                     → 3-stage axial.
        self._loading_type: str = str(loading_type).lower()
        # Configurable Stage I end: default 50 cycles (Jiang 2003 "5–50 cycles").
        self.n_stage_i_cycles: int = int(n_stage_i_cycles)
        # One-way latch: True after rapid initial embedding phase ends.
        # Analogous to _stage_II_triggered for the axial model.
        self._axial_rapid_done: bool = False

        # Phase-aware adaptive cycle stepping (§4.4). When enabled, run_analysis
        # jumps the cycle counter by a phase-dependent dN and scales per-cycle
        # accumulations (wear, loosening angle, Miner's damage) by dN.
        self.adaptive_stepping: bool = bool(adaptive_stepping)

        # Curve-shape enhancements: seeded RNG for stochastic slip smearing
        # (deterministic per-instance — same model + same seed → same trace).
        self._rng = np.random.default_rng(42)

        # Calibration hooks (2026-04-23). Exposed for ParameterIdentifier so
        # the user can tune the fixture/joint compliance without editing the
        # geometry. Defaults preserve the legacy hardcoded behaviour.
        self._k_transverse_ratio: float = 0.3   # k_trans = k_system × ratio
        self._damping_zeta: float = 0.0         # informational; quasi-static
                                                # preload decay is insensitive
                                                # to damping (placeholder for
                                                # future time-integration use).

    # Phase-aware cycle step sizes used when adaptive_stepping is True.
    # Keys are LooseningPhase values; values are the number of cycles advanced
    # per physics evaluation. Slow phases get larger steps.
    _ADAPTIVE_STEP_BY_PHASE: Dict = None  # populated lazily below

    @classmethod
    def _init_adaptive_step_table(cls):
        if cls._ADAPTIVE_STEP_BY_PHASE is None:
            cls._ADAPTIVE_STEP_BY_PHASE = {
                LooseningPhase.STABLE: 100,
                LooseningPhase.NON_ROTATIONAL: 20,
                LooseningPhase.TRANSITION: 5,
                LooseningPhase.ROTATIONAL: 2,
                LooseningPhase.RUNAWAY: 1,
                LooseningPhase.AXIAL_STAGE_I: 5,
                LooseningPhase.AXIAL_STAGE_II: 20,
                LooseningPhase.AXIAL_STAGE_III: 1,
            }

    def _compute_adaptive_step(self, phase, prev_delta_ratio: float) -> int:
        """Phase-aware step with error-based refinement.

        Starts from _ADAPTIVE_STEP_BY_PHASE[phase], halves if the previous step's
        |ΔF/F| > 0.5%, doubles (up to phase base) if < 0.05%.
        """
        self._init_adaptive_step_table()
        base = self._ADAPTIVE_STEP_BY_PHASE.get(phase, 1)
        if prev_delta_ratio > 0.005:
            return max(1, base // 2)
        if prev_delta_ratio < 0.0005:
            return base
        return base

    def reset_state(self):
        """
        Reset all accumulated state in the analyzer.

        This method ensures that the analyzer is ready for a fresh analysis
        by clearing all accumulated state from previous runs. This is critical
        for preventing state leakage between analyses of different joint
        configurations.

        Resets:
        - Loosening state (preload, wear, rotation)
        - Analysis history
        - Accumulated wear energy and cycles
        - Friction state tracking

        Note: Geometry and model parameters (thread, bearing, etc.) are NOT
        reset, only the runtime accumulated state.
        """
        # Reset main state
        self.state = LooseningState()
        self.history = []
        self.initial_preload = 0.0

        # Reset accumulated wear state
        self.wear._accumulated_energy = 0.0
        self.wear._accumulated_cycles = 0
        self._wear_total_depth_m = 0.0

        # Reset per-run flags so warnings and latches fire correctly on re-run
        self._stage_II_triggered = False
        self._iso16130_warning_emitted = False
        self._axial_rapid_done = False

        # Reseed RNG so stochastic smearing is reproducible across re-runs.
        self._rng = np.random.default_rng(42)

    def recompute_k_system(self) -> None:
        """Recompute k_system from the current k_bolt and k_member.

        Call this after externally overriding k_bolt or k_member (e.g. from
        ParameterIdentifier) to keep the series-spring combination consistent.
        """
        kb, km = float(self.k_bolt), float(self.k_member)
        if kb > 0 and km > 0:
            self.k_system = (kb * km) / (kb + km)

    # =========================================================================
    # H2: CONTACT OBJECT INTEGRATION
    # =========================================================================

    def _extract_from_thread_contact(self, tc):
        """
        Extract thread geometry from a ThreadContact object (H2).

        Populates self.thread (ThreadGeometryParams) from the Contact's
        ThreadGeometry, and extracts initial friction from the Contact.
        """
        if hasattr(tc, 'thread'):
            tg = tc.thread  # ThreadGeometry dataclass
            self.thread.pitch = tg.pitch
            self.thread.pitch_diameter = tg.pitch_diameter
            self.thread.major_diameter = tg.major_diameter
            self.thread.flank_angle = tg.flank_angle
            self.thread.num_engaged_threads = tg.n_engaged_threads

        # Extract initial friction from contact
        if hasattr(tc, 'friction') and tc.friction is not None:
            self.friction.mu_initial = tc.friction.mu_static

    def _extract_from_bearing_contact(self, bc):
        """
        Extract bearing geometry from a BearingContact object (H2).

        Populates self.bearing (BearingGeometryParams) from the Contact's
        ContactGeometry.
        """
        if hasattr(bc, 'geometry') and bc.geometry is not None:
            self.bearing.inner_diameter = bc.geometry.inner_radius * 2
            self.bearing.outer_diameter = bc.geometry.outer_radius * 2

    def sync_contacts_from_state(self, state: LooseningState):
        """
        Push analyzer state to Contact objects (H2).

        Updates Contact objects' normal_force, friction.mu_current, and
        wear state to match the analyzer's per-cycle state. This keeps
        contacts in sync for use by the time-integration solver.

        Args:
            state: Current LooseningState
        """
        if self._thread_contact is not None:
            self._thread_contact.normal_force = state.preload
            self._thread_contact.friction.mu_current = state.mu_thread
            self._thread_contact.friction.cycles = state.cycle
            # Sync wear depth
            if state.thread_wear_depth > 0:
                self._thread_contact.wear.wear_depth = state.thread_wear_depth

        if self._bearing_contact is not None:
            self._bearing_contact.normal_force = state.preload
            self._bearing_contact.friction.mu_current = state.mu_bearing
            self._bearing_contact.friction.cycles = state.cycle
            # Sync wear depth
            if state.bearing_wear_depth > 0:
                self._bearing_contact.wear.wear_depth = state.bearing_wear_depth

            # Update slip state
            if state.bearing_slipping:
                try:
                    from ..core.contacts.base import SlipState
                except ImportError:
                    from bolt_analysis_studio.core.contacts.base import SlipState
                self._bearing_contact.slip_state = SlipState.GROSS_SLIP
                self._bearing_contact.is_slipping = True
            else:
                try:
                    from ..core.contacts.base import SlipState
                except ImportError:
                    from bolt_analysis_studio.core.contacts.base import SlipState
                self._bearing_contact.slip_state = SlipState.STUCK
                self._bearing_contact.is_slipping = False

    def sync_state_from_contacts(self, state: LooseningState):
        """
        Pull Contact objects' evolved state into analyzer state (H2).

        When Contact objects have been updated by the time-integration
        solver (via update_state()), their evolved friction/wear values
        are read back into the analyzer state.

        Args:
            state: LooseningState to update (modified in place)
        """
        if self._thread_contact is not None:
            tc = self._thread_contact
            if tc.friction.mu_current > 0:
                state.mu_thread = tc.friction.mu_current
            if tc.wear.wear_depth > 0:
                state.thread_wear_depth = tc.wear.wear_depth
            # Read loosening angle from ThreadContact
            if hasattr(tc, 'theta_loosening') and tc.theta_loosening > 0:
                state.loosening_angle = tc.theta_loosening
                state.loosening_angle_deg = tc.theta_loosening_deg

        if self._bearing_contact is not None:
            bc = self._bearing_contact
            if bc.friction.mu_current > 0:
                state.mu_bearing = bc.friction.mu_current
            if bc.wear.wear_depth > 0:
                state.bearing_wear_depth = bc.wear.wear_depth

    @property
    def has_contacts(self) -> bool:
        """True if Contact objects are attached (H2)."""
        return self._thread_contact is not None or self._bearing_contact is not None

    def compute_critical_friction(self) -> float:
        """
        Compute the critical friction coefficient below which loosening occurs.

        mu_crit = (p/2*pi) * 2*cos(alpha) / (d2 + 2*r_eff*cos(alpha))

        This is the threshold where T_pitch = T_thread + T_bearing
        """
        p = self.thread.pitch
        d2 = self.thread.pitch_diameter
        alpha = self.thread.flank_angle
        r_eff = self.bearing.effective_radius

        cos_alpha = np.cos(alpha)

        numerator = (p / (2 * np.pi)) * 2 * cos_alpha
        denominator = d2 + 2 * r_eff * cos_alpha

        return numerator / denominator

    def compute_torques(self, preload: float, mu_thread: float,
                        mu_bearing: float) -> Dict[str, float]:
        """
        Compute all torque components for loosening analysis.

        Args:
            preload: Current preload force [N]
            mu_thread: Current thread friction coefficient
            mu_bearing: Current bearing friction coefficient

        Returns:
            Dictionary with torque values
        """
        p = self.thread.pitch
        d2 = self.thread.pitch_diameter
        alpha = self.thread.flank_angle
        r_m = self.thread.mean_radius
        r_eff = self.bearing.effective_radius

        # Pitch torque (DRIVES loosening)
        T_pitch = preload * p / (2 * np.pi)

        # Thread friction torque (RESISTS loosening)
        T_thread = mu_thread * preload * d2 / (2 * np.cos(alpha))

        # Bearing friction torque (RESISTS loosening)
        T_bearing = mu_bearing * preload * r_eff

        # Total resistance
        T_resistance = T_thread + T_bearing

        # Net torque (positive = loosening direction)
        T_net = T_pitch - T_resistance

        # Torque margin (>1 = stable, <1 = loosening)
        margin = T_resistance / T_pitch if T_pitch > 0 else float('inf')

        return {
            'T_pitch': T_pitch,
            'T_thread': T_thread,
            'T_bearing': T_bearing,
            'T_resistance': T_resistance,
            'T_net': T_net,
            'margin': margin,
            'loosening_possible': T_net > 0
        }

    def check_slip_condition(self, preload: float, F_transverse: float,
                              mu_bearing: float) -> bool:
        """
        Check if bearing surface is slipping (required for Junker loosening).

        Classical condition:   |F_transverse| > µ × N
        Pai-Hess correction:  |F_transverse| > slip_onset_factor × µ × N

        Pai & Hess (2002) measured that actual gross slip in Junker tests begins
        at ~46 % of the classical Coulomb threshold because partial (micro) slip
        already distributes load at the interface before gross sliding.
        slip_onset_factor=0.46 (default) matches their experimental data for
        machined steel interfaces; set to 1.0 to revert to classical Coulomb.
        """
        friction_capacity = self.slip_onset_factor * mu_bearing * preload
        return abs(F_transverse) > friction_capacity

    def compute_slip_distance(self, F_transverse: float, preload: float,
                               mu: float) -> float:
        """
        Estimate slip distance per cycle.

        Simplified model: slip distance proportional to excess force
        """
        friction_capacity = mu * preload
        excess_force = max(0, abs(F_transverse) - friction_capacity)

        # Estimate slip distance (simplified - could be more sophisticated)
        # Using system compliance
        if excess_force > 0:
            slip = excess_force / self.k_system * 4  # 4 slip events per cycle
        else:
            slip = 0.0

        return slip

    def compute_thermal_preload_loss(self, delta_T: float) -> float:
        """
        Compute preload loss from differential thermal expansion (H3).

        When bolt and clamped members have different thermal expansion
        coefficients, a temperature change causes differential elongation
        that changes preload.

        ΔF_thermal = k_sys * L * ΔT * (α_member - α_bolt)

        Positive ΔT with α_member > α_bolt → members expand more → preload INCREASES.
        Positive ΔT with α_member < α_bolt → bolt expands more → preload DECREASES.

        Args:
            delta_T: Temperature change from reference [K or °C]

        Returns:
            Preload change [N] (negative = preload loss)
        """
        delta_alpha = self.alpha_member - self.alpha_bolt
        delta_F = self.k_system * self.grip_length * delta_T * delta_alpha
        return delta_F

    def update_state(self, cycle: int, preload: float, F_transverse: float,
                     temperature: float = 20.0, cycle_step: int = 1) -> LooseningState:
        """
        Update state for one cycle (or one adaptive super-cycle).

        This is the core integration step that couples all effects:
        1. Update friction coefficient (evolution model)
        2. Check slip conditions
        3. Compute wear increment
        4. Compute loosening angle increment
        5. Update preload
        6. Classify phase and risk

        Args:
            cycle: Current cycle number
            preload: Current preload [N]
            F_transverse: Transverse force amplitude [N]
            temperature: Current temperature [C]
            cycle_step: Number of cycles this physics step represents. When
                using adaptive_stepping, per-cycle accumulators (wear increment,
                loosening angle increment) are scaled by cycle_step so that a
                single call advances the state by cycle_step cycles.

        Returns:
            Updated LooseningState
        """
        dN = max(1, int(cycle_step))
        state = LooseningState()
        state.cycle = cycle
        state.preload_initial = self.state.preload_initial if cycle > 0 else preload

        # 1. Update friction coefficients (M9: separate thread/bearing evolution)
        thread_wear_um = self.state.thread_wear_depth * 1e6
        bearing_wear_um = self.state.bearing_wear_depth * 1e6

        state.mu_thread = self.friction.compute_mu_for_surface(
            'thread', cycle, thread_wear_um, temperature)
        state.mu_bearing = self.friction.compute_mu_for_surface(
            'bearing', cycle, bearing_wear_um, temperature)

        # 2. Check slip conditions
        # Force-driven path: classical Junker force criterion
        force_bearing_slip = self.check_slip_condition(
            preload, F_transverse, state.mu_bearing
        )
        thread_capacity = state.mu_thread * preload * np.cos(self.thread.helix_angle)
        force_thread_slip = abs(F_transverse) > thread_capacity

        # Displacement-driven path: Junker machine imposes a controlled plate
        # displacement that physically forces gross sliding at all contact surfaces
        # whenever delta > micro-slip threshold — regardless of F_transverse value.
        _disp_driven = (
            not force_bearing_slip
            and self.transverse_displacement_mm > self.two_stage.displacement_threshold_mm
        )

        # Effective transverse force for Junker mechanism.
        # In displacement-controlled mode the machine generates: F = k_transverse * delta
        # where k_transverse ≈ 30 % of the series axial stiffness.
        if _disp_driven:
            state.bearing_slipping = True
            state.thread_slipping = True   # Same displacement drives thread slip
            k_trans_eff = self.k_system * 0.3
            F_trans_eff = k_trans_eff * self.transverse_displacement_mm * 1e-3
        else:
            state.bearing_slipping = force_bearing_slip
            state.thread_slipping = force_thread_slip
            F_trans_eff = F_transverse

        # 3. Compute torques
        torques = self.compute_torques(preload, state.mu_thread, state.mu_bearing)
        state.T_pitch = torques['T_pitch']
        state.T_thread = torques['T_thread']
        state.T_bearing = torques['T_bearing']
        state.T_resistance = torques['T_resistance']
        state.T_net = torques['T_net']
        state.torque_margin = torques['margin']

        # 4. Compute slip distances and wear (time-varying model)
        if state.bearing_slipping:
            if _disp_driven:
                # Displacement-controlled: slip = 4 × amplitude per cycle
                # (2 directions × forward + return = 4 half-amplitudes)
                slip_distance = 4.0 * self.transverse_displacement_mm * 1e-3
            else:
                slip_distance = self.compute_slip_distance(
                    F_transverse, preload, state.mu_bearing
                )

            # Thread wear (use half slip distance for thread)
            dh_thread, thread_wear_info = self.wear.compute_wear_increment(
                preload, slip_distance * 0.5, cycle, self.state.thread_wear_depth,
                temperature=temperature, friction_coeff=state.mu_thread
            )
            state.thread_wear_depth = self.state.thread_wear_depth + dh_thread * dN

            # Bearing wear (full slip distance)
            dh_bearing, bearing_wear_info = self.wear.compute_wear_increment(
                preload, slip_distance, cycle, self.state.bearing_wear_depth,
                temperature=temperature, friction_coeff=state.mu_bearing
            )
            state.bearing_wear_depth = self.state.bearing_wear_depth + dh_bearing * dN

            # Store wear phase info
            state.wear_phase = bearing_wear_info.get('wear_phase', 'unknown')
        else:
            state.thread_wear_depth = self.state.thread_wear_depth
            state.bearing_wear_depth = self.state.bearing_wear_depth
            state.wear_phase = 'no_slip'

        state.total_wear_depth = state.thread_wear_depth + state.bearing_wear_depth

        # 5. Compute loosening increment (JUNKER MECHANISM)
        # =====================================================
        # CRITICAL: Junker loosening occurs when BOTH surfaces slip, REGARDLESS
        # of static torque margin. During transverse slip, friction is overcome
        # momentarily, allowing the pitch torque to cause rotation.
        #
        # Reference: Junker (1969), Jiang et al. (2003)
        # Typical loosening rates from experiments: 0.001-0.1 deg/cycle
        #
        # Conditions for Junker loosening:
        # 1. Bearing surface must be slipping (F_trans > mu_bearing * F_p)
        # 2. Thread surface must be slipping (F_trans > mu_thread * F_p * cos(lambda))
        # 3. When both slip, friction resistance is temporarily zero
        # 4. Pitch torque causes backward rotation

        junker_active = state.bearing_slipping and state.thread_slipping

        if junker_active:
            # =================================================================
            # JUNKER LOOSENING MODEL (based on experimental correlations)
            # =================================================================
            # During complete slip, the nut can rotate freely under pitch torque
            # The rotation per cycle is governed by:
            #   d_theta = C * (F_trans - F_friction) / (F_p * d2) * slip_amplitude
            #
            # where:
            #   C = empirical constant (~1-10 for lubricated surfaces)
            #   F_trans = transverse force
            #   F_friction = friction capacity
            #   F_p = preload
            #   d2 = pitch diameter
            #   slip_amplitude = transverse displacement amplitude

            # Calculate excess force using effective force (F_trans_eff accounts for
            # displacement-driven mode where the machine imposes the displacement)
            friction_capacity_bearing = state.mu_bearing * preload
            friction_capacity_thread = state.mu_thread * preload * np.cos(self.thread.helix_angle)
            min_capacity = min(friction_capacity_bearing, friction_capacity_thread)

            excess_force = abs(F_trans_eff) - min_capacity
            excess_ratio = excess_force / (min_capacity + 1e-10)

            # Slip amplitude: in displacement-driven mode use measured amplitude;
            # in force-driven mode derive from excess force / k_transverse.
            # Transverse stiffness = k_system × _k_transverse_ratio (default 0.3,
            # exposed for fixture calibration via ParameterIdentifier).
            k_transverse = self.k_system * float(getattr(self, '_k_transverse_ratio', 0.3))
            if _disp_driven:
                slip_amplitude = self.transverse_displacement_mm * 1e-3
            else:
                slip_amplitude = excess_force / (k_transverse + 1e-10)

            # M8: Loosening coefficient from TwoStageLooseningParams (not hardcoded)
            C_loosening = self.two_stage.C_loosening

            # Compute rotation per cycle [rad]
            d2 = self.thread.pitch_diameter
            p = self.thread.pitch

            if _disp_driven:
                # M9: Displacement-controlled Junker machine formula.
                # The plate displacement is kinematically imposed, so excess_ratio
                # reflects machine stiffness (>> friction capacity) and is NOT a
                # reliable amplifier of the actual loosening rate.
                # Use a helix-geometry formula instead (Pai & Hess 2002 basis):
                #   d_theta = C_disp × tan(λ) × δ / d2
                # C_disp accounts for the fraction of geometric slip converted to
                # net rotation (typically 0.01–0.05 for lubricated self-locking threads).
                C_disp = getattr(self.two_stage, 'C_disp_loosening', 0.03)
                d_theta = C_disp * np.tan(self.thread.helix_angle) * slip_amplitude / d2
            else:
                # Force-driven mode: rotation scales with excess transverse force ratio
                d_theta = C_loosening * (slip_amplitude / d2) * (1 + excess_ratio) * (p / d2)

            # Cap at physical maximum (can't rotate more than what slip allows)
            max_rotation_per_cycle = 0.1  # ~6 deg/cycle is extreme
            d_theta = min(d_theta, max_rotation_per_cycle)

            # Apply diminishing effect as preload drops (less driving force)
            preload_factor = preload / self.state.preload_initial if self.state.preload_initial > 0 else 1.0
            d_theta *= preload_factor

            # Damped-exponential gap factor (curve-shape enhancement #1).
            # Smoothly drives d_theta to zero as preload approaches its asymptote
            # F∞ = F_infinity_ratio · F₀, replacing the linear segment that
            # otherwise produces a straight Stage II tail in the live simulation.
            F_inf_r = getattr(self.two_stage, 'F_infinity_ratio', 0.20)
            if F_inf_r < 1.0:
                gap = (state.preload_ratio - F_inf_r) / (1.0 - F_inf_r)
                d_theta *= max(0.0, gap)

            # Stochastic smearing (curve-shape enhancement #4).
            # Multiplicative Gaussian noise on the per-cycle increment turns
            # piecewise-linear segments into noisy curves while preserving the
            # mean trajectory. Seeded RNG → reproducible.
            sigma = getattr(self.two_stage, 'noise_amplitude', 0.0)
            if sigma > 0:
                d_theta *= max(0.0, 1.0 + float(self._rng.normal(0.0, sigma)))

            state.loosening_rate = d_theta
            state.loosening_angle = self.state.loosening_angle + d_theta * dN

        elif state.bearing_slipping and not state.thread_slipping:
            # Partial slip - some micro-motion but limited rotation
            # This is the transition regime - much slower loosening
            excess_force = abs(F_transverse) - state.mu_bearing * preload
            d_theta = 0.0001 * excess_force / (preload + 1e-10)  # Very small contribution
            d_theta = min(d_theta, 0.001)  # Cap at 0.001 rad/cycle

            state.loosening_rate = d_theta
            state.loosening_angle = self.state.loosening_angle + d_theta * dN

        else:
            # No slip - stable (or static loosening if margin < 1)
            if state.torque_margin < 1.0:
                # Static loosening (rare, very low friction)
                # When T_resistance < T_pitch, nut rotates even without transverse load
                margin_deficit = 1.0 - state.torque_margin
                d_theta = margin_deficit * 0.001  # 0.1% of deficit per cycle
                state.loosening_rate = d_theta
                state.loosening_angle = self.state.loosening_angle + d_theta * dN
            else:
                state.loosening_rate = 0.0
                state.loosening_angle = self.state.loosening_angle

        state.loosening_angle_deg = np.degrees(state.loosening_angle)

        # Accumulate cumulative rotation (LMQ §12.1 — absolute sum of per-cycle increments)
        delta_deg = np.degrees(state.loosening_angle - self.state.loosening_angle)
        state.cumulative_rotation_deg = (self.state.cumulative_rotation_deg
                                         + max(0.0, delta_deg))
        # Track self-locking loss (once lost, flag remains set)
        state.self_lock_lost = (self.state.self_lock_lost
                                 or state.torque_margin < 1.0)

        # 6. Compute preload losses using TWO-STAGE S-CURVE MODEL
        # ==========================================================
        # Based on Jiang et al. (2003) and Yang et al. (2019):
        # The S-curve emerges from:
        #   Stage I: Rapid plastic deformation at thread roots (10-40% loss in ~200 cycles)
        #   Stage II: Rotational loosening via Junker mechanism (slower, gradual)
        #
        # The model blends physics-based calculations with empirical S-curve fit

        # A) Physics-based losses (mechanical model)
        # Loss from rotational loosening
        # Use k_system (series combination of bolt + member), not k_bolt alone.
        # Physical cap: rotational loss cannot exceed the initial preload.
        loss_rotational = self.k_system * self.thread.helix_coupling_factor * \
                          state.loosening_angle
        loss_rotational = min(loss_rotational, state.preload_initial)

        # Loss from wear — NONLINEAR compliance model
        # Wear removes material, increasing bolt elongation: δ = PL/AE
        # As wear depth h grows, effective compliance increases nonlinearly:
        #   C_wear(h) = C_0 * (1 + γ*h)^n  where n > 1 for accelerating loss
        # Preload loss = k_system * h * (1 + γ*h)  — quadratic in wear depth
        # This creates positive feedback: more wear → more compliance → less
        # clamping → more slip → more wear (Pai & Hess 2002)
        h = state.total_wear_depth
        gamma = self.wear.compliance_growth_rate if hasattr(self.wear, 'compliance_growth_rate') else 0.05
        h_um = h * 1e6  # Convert to μm for scaling
        compliance_amplifier = 1.0 + gamma * h_um + 0.5 * (gamma * h_um) ** 2
        loss_wear = self.k_system * h * compliance_amplifier

        # B) S-curve empirical correction (Jiang/Yang model)
        # Captures the characteristic two-stage decay profile
        # Get displacement for S-curve calculation
        disp_mm = self.transverse_displacement_mm

        # Calculate S-curve loss factor
        scurve_loss_factor = self.two_stage.compute_scurve_factor(cycle, disp_mm)

        # S-curve contributes to preload loss, scaled by initial preload
        loss_scurve = scurve_loss_factor * state.preload_initial

        # C) H3: Thermal preload loss
        delta_T = temperature - 20.0  # Delta from reference
        loss_thermal = 0.0
        if abs(delta_T) > 0.1:
            delta_F_thermal = self.compute_thermal_preload_loss(delta_T)
            # Negative delta_F means preload loss (bolt expands more than member)
            loss_thermal = max(0, -delta_F_thermal)

        # D) Combined loss model
        # Blend physics-based and empirical S-curve losses.
        # Use the AVERAGE of both (not the max) to avoid over-prediction.
        # The S-curve captures the empirical profile shape while physics
        # adds rotational and wear contributions.
        physics_loss = loss_rotational + loss_wear + loss_thermal
        empirical_loss = loss_scurve

        # Weighted average: S-curve provides shape, physics adds incremental
        total_loss = 0.6 * empirical_loss + 0.4 * physics_loss

        # E) Norton-Bailey creep overlay (curve-shape enhancement #3).
        # ΔF_creep(N) = k_sys · ε₀ · (N / N_ref)^n  — log-time concave bend
        # that complements the cyclic loss budget for gasketed/polymer joints.
        # Disabled when creep_coefficient = 0 (default).
        eps_0 = getattr(self.two_stage, 'creep_coefficient', 0.0)
        if eps_0 > 0:
            n_creep = getattr(self.two_stage, 'creep_exponent', 0.25)
            N_ref = max(1.0, getattr(self.two_stage, 'creep_N_ref', 1000.0))
            loss_creep = self.k_system * eps_0 * (max(1, cycle) / N_ref) ** n_creep
            total_loss += loss_creep

        # Store individual components for analysis
        state.loss_rotational = loss_rotational
        state.loss_wear = loss_wear
        state.loss_thermal = loss_thermal
        state.loss_embedding = empirical_loss * self.two_stage.delta_F1_ratio / max(scurve_loss_factor, 0.01)

        # Total preload
        state.preload = max(0, state.preload_initial - total_loss)
        state.preload_ratio = state.preload / state.preload_initial if state.preload_initial > 0 else 0

        # 6b. Phase D: fretting wear coupling — apply Archard µ correction
        if state.bearing_slipping:
            _slip_amp_d = (self.transverse_displacement_mm * 1e-3
                           if _disp_driven else
                           abs(slip_distance))   # slip_distance is defined above in step 4
            self._update_friction_wear(state, _slip_amp_d)

        # 7. Compute critical friction and friction margin
        state.mu_critical = self.compute_critical_friction()
        mu_avg = (state.mu_thread + state.mu_bearing) / 2
        state.friction_margin = mu_avg / state.mu_critical if state.mu_critical > 0 else float('inf')

        # 7b. Phase D: self-lock check (ISO 16130)
        self._check_self_lock(state)

        # 8. Classify phase and risk
        state.phase = self._classify_phase(state)
        state.risk = self._classify_risk(state)

        # 9. H2: Sync state to Contact objects (if attached)
        if self.has_contacts:
            self.sync_contacts_from_state(state)

        return state

    # ------------------------------------------------------------------
    # Phase D: Fretting Wear Coupling helpers
    # ------------------------------------------------------------------

    def _update_friction_wear(self, state: LooseningState,
                               slip_amplitude_m: float) -> None:
        """
        Apply per-cycle wear correction to friction coefficients.

        Dispatches to the pluggable wear model selected at construction
        (Phase 3.2: 'archard' | 'energy' | 'fretting' | 'fatigue').
        Falls back to inline Archard if self._wear_model is unavailable.

        Regime gate: no correction applied for stick / partial-slip
        (delta < fretting_threshold_um).

        Args:
            state:            Current LooseningState (modified in place)
            slip_amplitude_m: Peak slip amplitude this cycle [m]
        """
        delta = abs(slip_amplitude_m)
        # Determine regime threshold from WearModelParams
        delta_fretting = getattr(self.wear, 'fretting_threshold_um', 5.0) * 1e-6  # µm → m

        if delta < delta_fretting:
            return  # Stick or partial-slip — no additional correction

        F_n = state.preload
        A_nom = max(self.thread.pitch_diameter ** 2 * np.pi / 4, 1e-6)

        # Dispatch to pluggable wear model (Phase 3.2)
        if self._wear_model is not None:
            try:
                h_m = self._wear_model.compute_wear_increment(
                    F_normal=F_n,
                    slip_distance_m=delta,
                    cycle=state.cycle,
                    total_depth_m=self._wear_total_depth_m,
                    slip_amplitude_m=delta,
                    mu=state.mu_thread,
                )
                self._wear_total_depth_m += max(0.0, h_m)
            except Exception:
                h_m = 0.0
        else:
            # Inline Archard fallback
            delta_gross = 50e-6   # 50 µm
            K_wear = (self.wear.K_running_in if delta < delta_gross
                      else self.wear.K_steady)
            H = self.wear.hardness if self.wear.hardness > 0 else 2e9
            dV = K_wear * F_n * delta / H   # m³/cycle
            h_m = dV / A_nom                # m depth this cycle
            self._wear_total_depth_m += max(0.0, h_m)

        h_um = h_m * 1e6           # m → µm wear depth this cycle
        # 0.001 µ per µm is the Jiang 2003/2004 baseline; multiply by the
        # tuneable friction_recovery_gain (curve-shape enhancement #2) to
        # amplify the μ↓→slip↑→wear↑ positive-feedback loop and produce
        # visibly concave Stage II tails.
        gain = getattr(self.two_stage, 'friction_recovery_gain', 1.0)
        d_mu = 0.001 * h_um * gain

        # Apply — ensure µ doesn't go below absolute minimum
        mu_min = getattr(self.friction, 'mu_minimum', 0.03)
        state.mu_thread  = max(mu_min, state.mu_thread  - d_mu)
        state.mu_bearing = max(mu_min, state.mu_bearing - d_mu)

    def _check_self_lock(self, state: LooseningState) -> None:
        """
        Evaluate Junker/Jiang self-locking condition and emit standards warnings.

        ── Self-locking criterion ───────────────────────────────────────────────
        Self-locking is maintained while the torque margin ≥ 1.0, i.e. while
        thread-friction + bearing-friction torques collectively exceed the helix
        pitch torque that drives nut back-off (Junker 1969, SAE Paper 690055):

            M_K + M_G ≥ M_TP
            torque_margin = (M_K + M_G) / M_TP ≥ 1.0

        Once torque_margin falls below 1.0 the self_lock_lost flag is set
        permanently on the state object, modelling the physical irreversibility
        of self-locking loss.

        ── Standards-compliance warnings ────────────────────────────────────────
        Two distinct retention thresholds from the applicable standards:

          85 % — ISO 16130:2015 (aerospace fasteners, Junker test method)
                 Lower boundary of the "good self-locking" zone
                 (100 %–85 % = good; 85 %–40 % = acceptable; < 40 % = poor).
                 Source: ISO 16130:2015 evaluation zones.

          80 % — DIN 25201-4 (2010) (industrial fasteners, supersedes DIN 65151)
                 Minimum pass criterion: ≥ 80 % preload retained after 2 000
                 cycles at 12.5 Hz. Below 80 % = test failure.
                 Source: DIN 25201-4:2010, §5 pass criterion.

        A single warning is emitted at the 85 % boundary (the more conservative
        of the two), guarded by _iso16130_warning_emitted so it fires only once
        per analysis run.

        Note: Earlier revisions of this code cited "ISO 16130 §6.3" for the 80 %
        threshold. This was a misattribution — 80 % belongs to DIN 25201-4; the
        ISO 16130 upper-zone boundary is 85 %. Both are documented here for
        complete traceability.

        Args:
            state: Current LooseningState (modified in place: self_lock_lost flag).

        References:
            Junker (1969) SAE Paper 690055 — self-locking torque balance
            DIN 25201-4 (2010) — 80 % / 2 000 cycle industrial pass criterion
            ISO 16130:2015 — 85 %/40 % aerospace fastener evaluation zones
        """
        if state.torque_margin < 1.0:
            state.self_lock_lost = True

        # Warn at 85 % — ISO 16130:2015 upper-zone boundary (more conservative).
        # DIN 25201-4 uses 80 %; both thresholds documented in docstring above.
        if state.preload_ratio < 0.85 and not self._iso16130_warning_emitted:
            import warnings
            warnings.warn(
                f"Preload retention {state.preload_ratio:.1%} "
                f"< 85 % (ISO 16130:2015 'good' zone boundary) at cycle "
                f"{state.cycle}. DIN 25201-4 pass limit is 80 %. "
                f"Joint may not maintain adequate sealing or friction-grip force.",
                UserWarning, stacklevel=3
            )
            self._iso16130_warning_emitted = True

    def _classify_phase_axial(self, state: LooseningState) -> LooseningPhase:
        """
        Three-stage axial loading classification.

        ── Physical model ───────────────────────────────────────────────────────
        Under axial (non-transverse) cyclic loading the dominant loosening
        mechanisms differ from the Junker transverse case. Three stages are
        observed experimentally (Wang et al. 2021; Chinese J. Mech. Eng. 2021):

        Stage I — Rapid initial drop:
          Mechanism: Asperity crushing and initial micro-plastic deformation of
            mating surfaces. High preload loss rate per cycle. Thread and bearing
            surfaces "bed in". Fretting begins at thread contacts.
          Duration: Literature reports first 5–50 cycles; default n_stage_i_cycles
            = 50 (calibrated to Jiang 2003 "5–50 cycles" observation).
          Curve shape: Very steep initial drop; rapidly decelerating.

        Stage II — Slow steady decay:
          Mechanism: Fretting wear at thread contacts (Vingsbo-Söderberg
            partial-slip regime), viscoelastic creep / stress relaxation of
            clamped members, continued low-amplitude micro-slip.
          Duration: Hundreds to thousands of cycles — the bulk of service life.
          Curve shape: Nearly flat lin-lin; much lower dF/dN than Stage I.

        Stage III — Rapid failure:
          Mechanism: Fatigue crack initiation at thread root (cyclic stress has
            consumed sufficient Miner's damage) OR gross rotational back-off
            triggered by the now-low preload reducing friction below the Junker
            self-locking threshold.
          Trigger (BAS): F/F₀ ≤ 0.40 (ISO 16130:2015 "poor self-locking" zone
            entry) OR Miner's D ≥ 0.80 (fatigue crack initiation imminent).

        ── Stage I → II latch (_axial_rapid_done) ───────────────────────────────
        Set True (one-way) when EITHER:
          1. state.cycle > self.n_stage_i_cycles  (time-based; default 50)
          2. The 10-cycle rolling preload loss rate drops below 0.1 %/cycle
             (plateau detected from self.history; fires when embedding is done)
        Whichever occurs first.

        ── Stage II → III boundary ───────────────────────────────────────────────
        Checked as unconditional override (before latch logic):
          F/F₀ ≤ 0.40  — ISO 16130:2015 lower boundary of "acceptable" zone
          Miner's D ≥ 0.80 — fatigue crack initiation threshold

        ── Expected animation progression ────────────────────────────────────────
        AXIAL_STAGE_I → AXIAL_STAGE_II → AXIAL_STAGE_III

        Args:
            state: Current LooseningState. The _axial_rapid_done flag may be
                mutated as a side-effect when the embedding plateau is detected.

        Returns:
            LooseningPhase.AXIAL_STAGE_I, AXIAL_STAGE_II, or AXIAL_STAGE_III.

        References:
            Wang, J. et al. (2021) Eng. Fail. Anal. — three-stage criterion
            Chinese J. Mech. Eng. (2021) — competitive fatigue + loosening
            ISO 16130:2015 — 40 % lower boundary of "acceptable" zone
            LOOSENING_STAGE_DEFINITIONS.md §2 — full axial model description
        """
        preload_ratio = (state.preload / self.initial_preload
                         if self.initial_preload > 0 else 1.0)

        # ── Stage III override: fatigue / runaway ─────────────────────────────
        # ISO 16130:2015 "poor self-locking" zone entry at 40 %.
        # Also fires on Miner's D ≥ 0.80 (crack initiation imminent).
        if preload_ratio <= 0.40 or state.damage_fraction >= 0.80:
            return LooseningPhase.AXIAL_STAGE_III

        # ── Stage I → II latch ────────────────────────────────────────────────
        if not self._axial_rapid_done:
            # Criterion 1: cycle count past the rapid-drop window
            if state.cycle > self.n_stage_i_cycles:
                self._axial_rapid_done = True
            # Criterion 2: 10-cycle rolling loss rate drops below 0.1 %/cycle
            # (embedding plateau reached before n_stage_i_cycles)
            elif len(self.history) >= 10:
                prev = self.history[-10]
                if prev.preload > 0:
                    loss_rate = (prev.preload - state.preload) / (prev.preload * 10.0)
                    if loss_rate < 0.001:      # < 0.1 %/cycle → plateau reached
                        self._axial_rapid_done = True

        # ── Stage I: rapid embedding drop ─────────────────────────────────────
        if not self._axial_rapid_done:
            return LooseningPhase.AXIAL_STAGE_I

        # ── Stage II: slow fretting / creep decay ─────────────────────────────
        return LooseningPhase.AXIAL_STAGE_II

    def _classify_phase(self, state: LooseningState) -> LooseningPhase:
        """
        Classify the current loosening phase using the Jiang (2003/2004) two-stage
        model combined with quantitative preload-ratio sub-bands (Option C).

        ── Physical model ───────────────────────────────────────────────────────
        The Jiang body of work defines two mechanistically distinct regimes:

        Stage I — Non-rotational loosening ("early stage"):
          Mechanism: Cyclic micro-slip at thread and bearing surfaces drives
            local plastic ratcheting at thread roots. The bolt shank is
            effectively shortened by stress redistribution, reducing preload
            without any macroscopic nut rotation (Jiang et al. 2003).
            Secondary contribution from fretting wear of the thread interface
            continues as a slow, gradual decay (Jiang et al. 2007).
          Diagnostic: Cumulative nut rotation < 0.5°.
          Preload loss: Variable — Jiang (2004) reports 10–40 % F₀ drop
            before 0.5° rotation is reached, depending on loading amplitude.
          Curve shape (F/F₀ vs. cycles): Rapid initial drop in first 5–50
            cycles, then slow gradual decay. On a lin-log plot: steep initial
            descent flattening to a gentle slope.

        Stage II — Rotational loosening (nut back-off):
          Trigger: Cumulative nut rotation first reaches 0.5° (the single
            most-cited Jiang quantitative threshold, confirmed in the 2003,
            2004, and 2007 papers and widely adopted in subsequent literature).
          Mechanism: Simultaneous gross slip at BOTH thread contact AND bearing
            head eliminates both friction torques (M_K and M_G), leaving the
            helix pitch torque M_TP = F_p · r_m · tan(λ) unopposed → nut
            backs off along the bolt thread (Junker 1969, SAE Paper 690055).
          Curve shape: Faster, roughly linear F/F₀ decline vs. cycles on a
            linear scale. Distinctly steeper slope than Stage I.

        ── Why cumulative rotation is used as a ONE-WAY LATCH, not a gate ──────
        A prior implementation gated Stage I classification as:
            if preload_ratio > 0.90 AND cumulative_rotation_deg < 0.1 → STABLE
            if preload_ratio > 0.75 AND cumulative_rotation_deg < 0.5 → NON_ROTATIONAL

        This was mechanistically wrong. cumulative_rotation_deg is a monotonically
        increasing accumulator: even 0.002°/cycle of micro-slip (well within Stage I)
        exceeds 0.1° after 50 cycles and 0.5° after 250 cycles. The gated form
        prevented STABLE and NON_ROTATIONAL from ever being classified in typical
        simulations, leaving the animation stuck on TRANSITION.

        The Jiang 0.5° criterion is a ONE-TIME TRANSITION DETECTOR, not a
        per-state predicate. It marks the cycle where Stage II BEGINS — after that
        it is irrelevant as a gate because Stage II is physically irreversible.

        Implementation: self._stage_II_triggered is a boolean latch, set to True
        when cumulative_rotation_deg first reaches 0.5°, never reset within a
        single analysis run. See LOOSENING_STAGE_DEFINITIONS.md §7.4 Option C.

        ── Phase boundaries ─────────────────────────────────────────────────────
        Sub-bands within each Jiang stage are defined by F/F₀ (preload retention
        ratio). The exact boundary percentages (0.90, 0.75, 0.55, 0.20) are
        engineering interpolations — not individually published in any single
        source — but are consistent with:
          • DIN 25201-4 (2010): ≥ 80 % retention = pass at 2 000 cycles
          • ISO 16130:2015:     85–100 % = good; 40–85 % = acceptable; <40 % = poor

        Stage I sub-bands (self._stage_II_triggered is False):
          STABLE         F/F₀ > 0.90   Nearly full preload; embedding minimal.
                                        No significant micro-slip accumulation.
          NON_ROTATIONAL F/F₀ > 0.75   Stage I active. Fretting, embedding,
                                        and thread-root ratcheting are the
                                        dominant loss mechanisms.
          TRANSITION     F/F₀ ≤ 0.75   Heavy Stage I loss; friction margin
                                        approaching the Junker slip threshold.
                                        Stage II may be imminent.

        Stage II sub-bands (self._stage_II_triggered is True):
          TRANSITION     F/F₀ > 0.55   Early rotational loosening. Nut is
                                        backing off but preload still above
                                        the estimated full-slip Junker threshold.
          ROTATIONAL     F/F₀ > 0.20   Full Junker back-off. Self-loosening
                                        torque exceeds resisting friction;
                                        nut rotates freely per cycle.
          RUNAWAY        F/F₀ ≤ 0.20   Catastrophic loss. Joint integrity
                                        effectively lost (DIN 25201-4 far
                                        below pass; ISO 16130 poor zone).

        ── Unconditional overrides (evaluated first) ────────────────────────────
          RUNAWAY if self_lock_lost AND torque_margin < 0.5 (irreversible)
          RUNAWAY if F/F₀ ≤ 0.20 regardless of latch state

        ── Expected animation progression ───────────────────────────────────────
        STABLE → NON_ROTATIONAL → TRANSITION (Stage I)
          → [latch fires at 0.5°] → TRANSITION (Stage II) → ROTATIONAL → RUNAWAY

        Args:
            state: Current LooseningState snapshot for this cycle. The instance
                flag self._stage_II_triggered may be mutated as a side-effect
                when the 0.5° latch threshold is first crossed.

        Returns:
            LooseningPhase enum member for the current cycle.

        References:
            Junker, G.H. (1969) SAE Paper 690055 — transverse vibration; torque
              balance M_TP > M_K + M_G as loosening condition.
            Jiang, Y.Y., Zhang, M., Lee, C.H. (2003) J. Mech. Des. 125(3):518–526
              — Stage I micro-slip mechanism; early-stage non-rotational model.
            Zhang, M., Jiang, Y.Y. (2004) J. Mech. Des. 126(6):1062–1064
              — Experimental validation; 0.5° cumulative rotation = Stage I/II
              boundary (the single most-cited Jiang quantitative threshold).
            Jiang, Y.Y. et al. (2007) J. Mech. Des. 129(2):218–226
              — FEA of Stage II; 3-D helix coupling; confirms 0.5° boundary.
            DIN 25201-4 (2010) — 80 % preload retention at 2 000 cycles (12.5 Hz)
              as industrial pass/fail criterion.
            ISO 16130:2015 — aerospace Junker test; 85 %/40 % evaluation zones.
            LOOSENING_STAGE_DEFINITIONS.md §7.4 — Option A/B/C comparison;
              rationale for choosing Option C (Jiang-faithful one-way latch).
            LOOSENING_STAGE_DEFINITIONS.md §3 — loading_type dispatch table.
        """
        # ── Model dispatch ────────────────────────────────────────────────────
        # Route to the axial 3-stage model when configured; otherwise proceed
        # with the Junker 5-stage model below.
        if self._loading_type == 'axial':
            return self._classify_phase_axial(state)

        preload_ratio = (state.preload / self.initial_preload
                         if self.initial_preload > 0 else 1.0)

        # ── Override 0: irreversible torque-margin collapse ───────────────────
        # Both self-lock lost AND margin far below unity → no recovery path.
        if state.self_lock_lost and state.torque_margin < 0.5:
            return LooseningPhase.RUNAWAY

        # ── Override 1: catastrophic preload loss ─────────────────────────────
        # Below 20 % retention the joint has effectively failed regardless of
        # which Jiang stage is nominally active.
        if preload_ratio <= 0.20:
            return LooseningPhase.RUNAWAY

        # ── Jiang Stage II latch (Jiang 2004, 0.5° criterion) ────────────────
        # Apply the threshold as a one-way latch: set the flag on the first
        # cycle that crosses 0.5°; never reset it within a run.
        if state.cumulative_rotation_deg >= 0.5 and not self._stage_II_triggered:
            self._stage_II_triggered = True

        # ── Stage II classification (rotational loosening — nut backing off) ──
        if self._stage_II_triggered:
            # Early Stage II: preload still reasonably high; full Junker back-off
            # not yet at maximum rate.
            if preload_ratio > 0.55:
                return LooseningPhase.TRANSITION
            # Full Junker back-off: pitch torque dominates, continuous nut rotation.
            if preload_ratio > 0.20:
                return LooseningPhase.ROTATIONAL
            return LooseningPhase.RUNAWAY  # guard — already caught by Override 1

        # ── Stage I classification (non-rotational — rotation < 0.5°) ─────────
        # STABLE: preload essentially intact; embedding losses minimal.
        if preload_ratio > 0.90:
            return LooseningPhase.STABLE

        # NON_ROTATIONAL: Stage I active — fretting, embedding, thread ratcheting
        # dominate. Nut has not yet rotated to 0.5°.
        if preload_ratio > 0.75:
            return LooseningPhase.NON_ROTATIONAL

        # TRANSITION: heavy Stage I loss with rotation still sub-0.5°. Friction
        # margin is eroding toward the Junker slip threshold. Stage II imminent.
        return LooseningPhase.TRANSITION

    @staticmethod
    def _stage1_decay(N: float, A1: float, N1: float, A2: float, N2: float) -> float:
        """
        Double-exponential model for Stage I (non-rotational) preload decay.

        F_loss(N) / F_p0 = A1·(1 − e^(−N/N1)) + A2·(1 − e^(−N/N2))

        Calibrated defaults from Jiang et al. (2003) M12 dry tests:
          A1=0.08, N1=20  — rapid embedding (first ~50 cycles)
          A2=0.07, N2=150 — slower plastic relaxation

        Args:
            N:  cycle number
            A1: amplitude of fast component (fraction of F_p0)
            N1: characteristic cycle count of fast component
            A2: amplitude of slow component (fraction of F_p0)
            N2: characteristic cycle count of slow component

        Returns:
            Fractional preload loss at cycle N  (0 … A1+A2)
        """
        return A1 * (1.0 - np.exp(-N / N1)) + A2 * (1.0 - np.exp(-N / N2))

    def _classify_risk(self, state: LooseningState) -> LooseningRisk:
        """Classify loosening risk level."""
        margin = state.torque_margin

        if margin > 2.0:
            return LooseningRisk.NEGLIGIBLE
        elif margin > 1.5:
            return LooseningRisk.LOW
        elif margin > 1.1:
            return LooseningRisk.MODERATE
        elif margin > 1.0:
            return LooseningRisk.HIGH
        else:
            return LooseningRisk.CRITICAL

    def run_analysis(self, preload_initial: float, F_transverse: float,
                     n_cycles: int, temperature: float = 20.0,
                     output_interval: int = 1,
                     progress_callback: Callable[[int, int], None] = None
                     ) -> LooseningResults:
        """
        Run complete coupled loosening analysis.

        Args:
            preload_initial: Initial preload force [N]
            F_transverse: Transverse force amplitude [N]
            n_cycles: Number of cycles to simulate
            temperature: Operating temperature [C]
            output_interval: Store results every N cycles
            progress_callback: Optional callback(current, total) for progress

        Returns:
            LooseningResults with complete history
        """
        # Initialize - reset all state to ensure clean analysis
        # This is CRITICAL for preventing state leakage between different analyses
        self.reset_state()

        results = LooseningResults()
        self.state.preload_initial = preload_initial
        self.state.preload = preload_initial
        self.state.preload_ratio = 1.0
        self.initial_preload = preload_initial  # Store for phase classification

        # Pre-allocate arrays
        n_stored = n_cycles // output_interval + 1
        results.cycles = np.zeros(n_stored)
        results.preload = np.zeros(n_stored)
        results.preload_ratio = np.zeros(n_stored)
        results.mu_thread = np.zeros(n_stored)
        results.mu_bearing = np.zeros(n_stored)
        results.total_wear_um = np.zeros(n_stored)
        results.loosening_angle_deg = np.zeros(n_stored)
        results.loosening_rate = np.zeros(n_stored)
        results.torque_margin = np.zeros(n_stored)
        results.friction_margin = np.zeros(n_stored)
        results.miner_damage = np.zeros(n_stored)

        # Compute and store critical friction
        results.mu_critical = self.compute_critical_friction()

        # Initial state
        results.cycles[0] = 0
        results.preload[0] = preload_initial
        results.preload_ratio[0] = 1.0
        results.mu_thread[0] = self.friction.mu_initial
        results.mu_bearing[0] = self.friction.mu_initial
        mu_avg_initial = self.friction.mu_initial
        results.friction_margin[0] = mu_avg_initial / results.mu_critical if results.mu_critical > 0 else float('inf')

        store_idx = 1
        preload = preload_initial
        loosening_onset_cycle = 0
        cycles_to_50_found = False

        # Phase E: Miner's rule per-cycle state
        miner_total = 0.0
        miner_failure_cycle = 0
        # Stress area from thread geometry: A_s = π/4 × ((d2+d1)/2)²
        # d1 ≈ major_diameter − 1.0825×pitch  (ISO 724 minor diameter)
        _d2_m = self.thread.pitch_diameter
        _d1_m = self.thread.major_diameter - 1.0825 * self.thread.pitch
        _As_m2 = np.pi / 4.0 * ((_d2_m + _d1_m) / 2.0) ** 2
        if _As_m2 <= 0.0:
            _As_m2 = self._sun_curve.params.bolt_stress_area  # fallback to default

        # Convergence early-exit constants
        _STEADY_WINDOW = 200        # cycles over which to measure change
        _STEADY_THRESHOLD = 0.001   # <0.1 % relative change → steady state
        _LOOSE_THRESHOLD = 0.02     # preload < 2 % of initial → fully loosened
        _preload_history: list = []  # rolling buffer for convergence check

        # Main simulation loop — adaptive or fixed-step
        use_adaptive = bool(getattr(self, 'adaptive_stepping', False))
        prev_delta_ratio = 0.0  # |ΔF/F| from the previous step (for refinement)

        cycle = 1
        while cycle <= n_cycles:
            if use_adaptive:
                cycle_step = self._compute_adaptive_step(self.state.phase, prev_delta_ratio)
                # Don't overshoot n_cycles
                cycle_step = min(cycle_step, n_cycles - cycle + 1)
            else:
                cycle_step = 1

            preload_before = preload
            new_state = self.update_state(cycle, preload, F_transverse,
                                          temperature, cycle_step=cycle_step)
            self.state = new_state
            preload = new_state.preload
            if preload_before > 0:
                prev_delta_ratio = abs(preload_before - preload) / preload_before

            # Phase E: per-cycle Miner's rule damage increment, scaled by step
            _sigma = self._sun_curve.compute_thread_root_stress(
                F_transverse, preload, _As_m2)
            _N_life = self._sun_curve.predict_loosening_life(_sigma)
            miner_total += (cycle_step / _N_life) if _N_life < float('inf') else 0.0
            new_state.damage_fraction = miner_total
            if miner_failure_cycle == 0 and miner_total >= 1.0:
                miner_failure_cycle = cycle

            # Store at intervals (or every adaptive step)
            if use_adaptive or cycle % output_interval == 0:
                if store_idx < results.cycles.size:
                    results.cycles[store_idx] = cycle
                    results.preload[store_idx] = new_state.preload
                    results.preload_ratio[store_idx] = new_state.preload_ratio
                    results.mu_thread[store_idx] = new_state.mu_thread
                    results.mu_bearing[store_idx] = new_state.mu_bearing
                    results.total_wear_um[store_idx] = new_state.total_wear_depth * 1e6
                    results.loosening_angle_deg[store_idx] = new_state.loosening_angle_deg
                    results.loosening_rate[store_idx] = np.degrees(new_state.loosening_rate)
                    results.torque_margin[store_idx] = new_state.torque_margin
                    results.friction_margin[store_idx] = new_state.friction_margin
                    results.miner_damage[store_idx] = miner_total
                    results.states.append(new_state)
                    store_idx += 1

            # Track milestones
            if loosening_onset_cycle == 0 and new_state.torque_margin < 1.0:
                loosening_onset_cycle = cycle

            if not cycles_to_50_found and new_state.preload_ratio < 0.5:
                results.cycles_to_50_percent = cycle
                cycles_to_50_found = True

            # Progress callback — fires whenever the loop crosses a 100-cycle boundary
            prev_cycle = cycle - cycle_step + 1  # inclusive start of this step
            crossed_100 = (cycle // 100) > ((prev_cycle - 1) // 100)
            if progress_callback and crossed_100:
                progress_callback(cycle, n_cycles)

            # --- Convergence / early-exit checks (every 100 cycles) ---
            if crossed_100:
                _preload_history.append(preload)
                # Keep only the last _STEADY_WINDOW/100 entries
                _window_entries = _STEADY_WINDOW // 100
                if len(_preload_history) > _window_entries:
                    _preload_history.pop(0)

                # Full loosening check
                if preload_initial > 0 and preload < _LOOSE_THRESHOLD * preload_initial:
                    if hasattr(self, '_log'):
                        self._log(
                            f"[Convergence] Bolt fully loosened at cycle {cycle} "
                            f"(F/F0 = {preload/preload_initial:.3f}). Stopping."
                        )
                    break

                # Steady-state check (need a full window of history)
                if len(_preload_history) >= _window_entries:
                    _p_old = _preload_history[0]
                    if _p_old > 0:
                        _change_rate = abs(preload - _p_old) / _p_old
                        if _change_rate < _STEADY_THRESHOLD:
                            if hasattr(self, '_log'):
                                self._log(
                                    f"[Convergence] Steady state reached at cycle {cycle} "
                                    f"(Δ preload over last {_STEADY_WINDOW} cycles = "
                                    f"{_change_rate*100:.4f}%). Stopping."
                                )
                            break

            cycle += cycle_step

        # Trim arrays
        results.cycles = results.cycles[:store_idx]
        results.preload = results.preload[:store_idx]
        results.preload_ratio = results.preload_ratio[:store_idx]
        results.mu_thread = results.mu_thread[:store_idx]
        results.mu_bearing = results.mu_bearing[:store_idx]
        results.total_wear_um = results.total_wear_um[:store_idx]
        results.loosening_angle_deg = results.loosening_angle_deg[:store_idx]
        results.loosening_rate = results.loosening_rate[:store_idx]
        results.torque_margin = results.torque_margin[:store_idx]
        results.friction_margin = results.friction_margin[:store_idx]
        results.miner_damage = results.miner_damage[:store_idx]

        # Final summary
        results.final_preload_ratio = self.state.preload_ratio
        results.total_loosening_deg = self.state.loosening_angle_deg
        results.cycles_to_loosening_onset = loosening_onset_cycle
        results.max_loosening_rate = float(np.max(results.loosening_rate))
        results.phase_at_end = self.state.phase
        results.miner_damage_final = miner_total
        results.cycles_to_failure_miner = miner_failure_cycle

        return results

    def get_summary(self) -> Dict:
        """Get summary of current analysis state."""
        mu_crit = self.compute_critical_friction()

        return {
            'current_state': self.state.to_dict(),
            'mu_critical': mu_crit,
            'mu_thread_above_critical': self.state.mu_thread > mu_crit,
            'mu_bearing_above_critical': self.state.mu_bearing > mu_crit,
            'k_system': self.k_system,
            'helix_coupling': self.thread.helix_coupling_factor,
        }


# =============================================================================
# H7: NASSAR-YANG (2009) PER-CYCLE LOOSENING MODEL
# =============================================================================

@dataclass
class NassarYangParams:
    """
    Parameters for Nassar-Yang (2009) per-cycle torque balance model.

    Models loosening as a per-cycle torque balance between driving pitch
    torque and resisting friction torques at thread and bearing surfaces.

    Reference: Nassar, S.A. & Yang, X. (2009). ASME J. Pressure Vessel
    Technology, 131(2): 021204.

    ΔF_p/cycle = F_p * (T_pitch - T_thread - T_bearing) / (k_sys * (p/2π)²)
    """
    # Thread geometry (used if not taken from analyzer)
    pitch: float = 2.0e-3                # Thread pitch [m]
    pitch_diameter: float = 14.7e-3      # Pitch diameter [m]
    flank_angle: float = np.radians(30)  # Half flank angle [rad]

    # Bearing geometry
    bearing_r_eff: float = 10.25e-3      # Effective bearing radius [m]

    # Friction coefficients
    mu_thread: float = 0.12
    mu_bearing: float = 0.12

    # Model parameters
    efficiency_factor: float = 0.85      # Torque transfer efficiency
    slip_fraction: float = 1.0           # Fraction of cycle with active slip (0-1)


class NassarYangLooseningModel:
    """
    Nassar-Yang (2009) per-cycle loosening model (H7).

    Computes preload loss per cycle based on torque balance:
    - Driving torque: T_pitch = F_p * p / (2π)
    - Thread resistance: T_thread = μ_t * F_p * d₂ / (2·cos α)
    - Bearing resistance: T_bearing = μ_b * F_p * r_eff

    When T_pitch > T_thread + T_bearing during transverse slip,
    the nut rotates by:
        Δθ = (T_net * η * f_slip) / (k_sys * (p/2π))

    And preload changes by:
        ΔF_p = k_bolt * (p/2π) * Δθ
    """

    def __init__(self, params: NassarYangParams = None,
                 analyzer: CoupledLooseningAnalyzer = None):
        """
        Initialize from params or extract from CoupledLooseningAnalyzer.

        Args:
            params: NassarYangParams (used if analyzer not given)
            analyzer: CoupledLooseningAnalyzer to extract geometry from
        """
        if analyzer is not None:
            self.pitch = analyzer.thread.pitch
            self.pitch_diameter = analyzer.thread.pitch_diameter
            self.flank_angle = analyzer.thread.flank_angle
            self.bearing_r_eff = analyzer.bearing.effective_radius
            self.k_bolt = analyzer.k_bolt
            self.k_system = analyzer.k_system
            self.efficiency_factor = 0.85
            self.slip_fraction = 1.0
        elif params is not None:
            self.pitch = params.pitch
            self.pitch_diameter = params.pitch_diameter
            self.flank_angle = params.flank_angle
            self.bearing_r_eff = params.bearing_r_eff
            self.k_bolt = 500e6
            self.k_system = 375e6
            self.efficiency_factor = params.efficiency_factor
            self.slip_fraction = params.slip_fraction
        else:
            p = NassarYangParams()
            self.pitch = p.pitch
            self.pitch_diameter = p.pitch_diameter
            self.flank_angle = p.flank_angle
            self.bearing_r_eff = p.bearing_r_eff
            self.k_bolt = 500e6
            self.k_system = 375e6
            self.efficiency_factor = p.efficiency_factor
            self.slip_fraction = p.slip_fraction

        self.helix_factor = self.pitch / (2 * np.pi)  # p/(2π)

    def compute_preload_loss_per_cycle(self, F_preload: float,
                                        mu_thread: float,
                                        mu_bearing: float,
                                        is_slipping: bool = True,
                                        F_transverse: float = 0.0) -> float:
        """
        Compute preload loss for one cycle using Nassar-Yang torque balance.

        KEY PHYSICS (Nassar & Yang 2009, Junker 1969):
        During transverse slip, friction forces are redirected to oppose
        the imposed transverse motion. The rotational friction resistance
        is effectively reduced because the friction cone tilts toward the
        transverse direction. With full transverse slip, the pitch torque
        drives loosening nearly unopposed.

        The effective friction resistance to rotation depends on the ratio
        of transverse force to friction capacity:
            f_reduction = 1 - min(1, F_trans / (mu*F_p))^2

        At full slip (F_trans >> mu*F_p), f_reduction → 0 (no resistance).

        Args:
            F_preload: Current preload [N]
            mu_thread: Current thread friction coefficient
            mu_bearing: Current bearing friction coefficient
            is_slipping: Whether bearing surface is in slip
            F_transverse: Transverse force amplitude [N]

        Returns:
            Preload loss [N] (positive = loss)
        """
        if not is_slipping or F_preload <= 0:
            return 0.0

        # Friction capacity
        F_friction_bearing = mu_bearing * F_preload
        F_friction_thread = mu_thread * F_preload * np.cos(self.flank_angle)

        # Compute friction reduction factor during transverse slip
        # When F_trans > mu*F_p, friction is redirected transversely
        if F_transverse > 0:
            ratio_bearing = min(1.0, abs(F_transverse) / (F_friction_bearing + 1e-10))
            ratio_thread = min(1.0, abs(F_transverse) / (F_friction_thread + 1e-10))
            # Quadratic reduction: at full slip, resistance → 0
            f_red_bearing = max(0, 1.0 - ratio_bearing ** 2)
            f_red_thread = max(0, 1.0 - ratio_thread ** 2)
        else:
            # Default: assume moderate slip (50% reduction)
            f_red_bearing = 0.5
            f_red_thread = 0.5

        # Torque components
        T_pitch = F_preload * self.helix_factor

        # Reduced friction resistance during transverse slip
        T_thread = f_red_thread * mu_thread * F_preload * \
                   self.pitch_diameter / (2 * np.cos(self.flank_angle))
        T_bearing = f_red_bearing * mu_bearing * F_preload * self.bearing_r_eff

        # Net torque (positive = loosening direction)
        T_net = T_pitch - T_thread - T_bearing

        if T_net <= 0:
            return 0.0  # Still no loosening

        # Rotation increment per cycle
        d_theta = (T_net * self.efficiency_factor * self.slip_fraction) / \
                  (self.k_system * self.helix_factor)

        # Preload loss from rotation
        delta_F = self.k_bolt * self.helix_factor * d_theta

        return delta_F


# =============================================================================
# M14: YANG ET AL. (2025) Su-N CURVE LOOSENING LIFE
# =============================================================================

@dataclass
class SuNCurveParams:
    """
    Parameters for Yang et al. (2025) Su-N bilinear loosening life curve.

    Converts transverse loads to screw root stress, then uses a bilinear
    S-N type curve to predict loosening life (cycles to specified preload loss).

    The Su-N curve has two regimes:
    - High stress (above knee): N = C₁ * σ^(-m₁)  (steep slope)
    - Low stress (below knee):  N = C₂ * σ^(-m₂)  (shallower slope)

    Reference: Yang, X. et al. (2025) - Su-N curve for bolt loosening.
    """
    # Bilinear curve parameters
    # Calibrated for M16 class 10.9 bolt (Kt=3.5, A_s=157mm²)
    # High-stress: ~5000 cycles at 150 MPa amplitude
    # Low-stress: ~100000 cycles at 30 MPa amplitude
    sigma_knee: float = 50e6         # Knee stress [Pa] (transition point)
    C1: float = 5e32                 # High-stress coefficient
    m1: float = 3.5                  # High-stress exponent
    C2: float = 5e49                 # Low-stress coefficient
    m2: float = 6.0                  # Low-stress exponent

    # Endurance limit
    sigma_endurance: float = 10e6    # Below this, infinite life [Pa]

    # Stress conversion parameters
    stress_concentration_Kt: float = 3.5   # Thread root stress concentration
    bolt_stress_area: float = 157e-6       # Bolt stress area A_s [m²]

    # Target preload loss for "failure"
    failure_preload_ratio: float = 0.5     # 50% preload loss = loosening failure


class SuNCurveModel:
    """
    Yang et al. (2025) Su-N curve loosening life model (M14).

    Converts operational loads to equivalent thread root stress amplitude,
    then uses bilinear Su-N curve to predict loosening life.
    """

    def __init__(self, params: SuNCurveParams = None):
        self.params = params or SuNCurveParams()

    def compute_thread_root_stress(self, F_transverse: float,
                                    F_preload: float,
                                    stress_area: float = None) -> float:
        """
        Convert transverse force to thread root stress amplitude.

        σ_root = Kt * F_trans / A_s + F_preload / A_s
        σ_amplitude = Kt * F_trans / A_s  (cyclic component)

        Args:
            F_transverse: Transverse force amplitude [N]
            F_preload: Preload force [N]
            stress_area: Bolt stress area [m²] (None = use params)

        Returns:
            Thread root stress amplitude [Pa]
        """
        A_s = stress_area or self.params.bolt_stress_area
        Kt = self.params.stress_concentration_Kt

        sigma_amp = Kt * abs(F_transverse) / A_s
        return sigma_amp

    def predict_loosening_life(self, sigma_amplitude: float) -> float:
        """
        Predict loosening life from bilinear Su-N curve.

        Args:
            sigma_amplitude: Thread root stress amplitude [Pa]

        Returns:
            Predicted cycles to loosening failure (inf if below endurance limit)
        """
        p = self.params

        if sigma_amplitude <= p.sigma_endurance:
            return float('inf')

        if sigma_amplitude >= p.sigma_knee:
            # High-stress regime (steep slope)
            N = p.C1 * sigma_amplitude ** (-p.m1)
        else:
            # Low-stress regime (shallow slope)
            N = p.C2 * sigma_amplitude ** (-p.m2)

        return max(1, N)

    def predict_from_loading(self, F_transverse: float,
                              F_preload: float,
                              stress_area: float = None) -> Dict[str, float]:
        """
        Full prediction from loading conditions.

        Args:
            F_transverse: Transverse force amplitude [N]
            F_preload: Preload force [N]
            stress_area: Bolt stress area [m²]

        Returns:
            Dictionary with stress, life, and regime information
        """
        sigma = self.compute_thread_root_stress(F_transverse, F_preload, stress_area)
        N_life = self.predict_loosening_life(sigma)

        return {
            'sigma_amplitude_MPa': sigma * 1e-6,
            'N_loosening': N_life,
            'regime': 'high_stress' if sigma >= self.params.sigma_knee else 'low_stress',
            'above_endurance': sigma > self.params.sigma_endurance,
            'failure_criterion': f'{self.params.failure_preload_ratio*100:.0f}% preload loss',
        }


# =============================================================================
# M15: MINER'S RULE FOR VARIABLE AMPLITUDE LOADING
# =============================================================================

@dataclass
class LoadBlock:
    """A block of constant-amplitude loading for Miner's rule."""
    F_transverse: float    # Transverse force amplitude [N]
    n_cycles: int          # Number of cycles at this amplitude
    frequency: float = 1.0 # Frequency [Hz] (informational)


class MinersRuleAccumulator:
    """
    Miner's rule cumulative damage for variable amplitude loosening (M15).

    D = Σ(nᵢ / Nᵢ)

    where:
    - nᵢ = number of cycles at load level i
    - Nᵢ = loosening life at load level i (from Su-N curve or analyzer)

    Loosening failure when D >= 1.0.
    """

    def __init__(self, sun_curve: SuNCurveModel = None,
                 analyzer: CoupledLooseningAnalyzer = None):
        """
        Initialize with a life prediction model.

        Args:
            sun_curve: Su-N curve model for life prediction
            analyzer: CoupledLooseningAnalyzer (used to run per-block analysis)
        """
        self.sun_curve = sun_curve or SuNCurveModel()
        self.analyzer = analyzer
        self.damage = 0.0
        self.block_history: List[Dict] = []

    def reset(self):
        """Reset accumulated damage."""
        self.damage = 0.0
        self.block_history = []

    def add_block(self, block: LoadBlock, F_preload: float,
                  stress_area: float = None) -> Dict[str, float]:
        """
        Add a loading block and compute damage increment.

        Args:
            block: Loading block definition
            F_preload: Current preload [N]
            stress_area: Bolt stress area [m²]

        Returns:
            Dictionary with damage increment and cumulative damage
        """
        # Get life for this load level
        result = self.sun_curve.predict_from_loading(
            block.F_transverse, F_preload, stress_area)
        N_life = result['N_loosening']

        # Damage increment
        if N_life == float('inf'):
            d_damage = 0.0
        else:
            d_damage = block.n_cycles / N_life

        self.damage += d_damage

        block_info = {
            'F_transverse': block.F_transverse,
            'n_cycles': block.n_cycles,
            'N_life': N_life,
            'damage_increment': d_damage,
            'cumulative_damage': self.damage,
            'sigma_amplitude_MPa': result['sigma_amplitude_MPa'],
            'regime': result['regime'],
        }
        self.block_history.append(block_info)

        return block_info

    def compute_variable_amplitude_damage(self, blocks: List[LoadBlock],
                                           F_preload: float,
                                           stress_area: float = None
                                           ) -> Dict[str, Any]:
        """
        Compute total Miner's damage from a sequence of load blocks.

        Args:
            blocks: List of LoadBlock definitions
            F_preload: Initial preload [N]
            stress_area: Bolt stress area [m²]

        Returns:
            Dictionary with total damage, per-block breakdown, and prediction
        """
        self.reset()

        for block in blocks:
            self.add_block(block, F_preload, stress_area)

        total_cycles = sum(b.n_cycles for b in blocks)

        return {
            'total_damage': self.damage,
            'failed': self.damage >= 1.0,
            'remaining_life_fraction': max(0, 1.0 - self.damage),
            'total_cycles': total_cycles,
            'n_blocks': len(blocks),
            'block_details': self.block_history,
        }

    def estimate_remaining_cycles(self, F_transverse_next: float,
                                   F_preload: float,
                                   stress_area: float = None) -> float:
        """
        Estimate remaining cycles at a given load level before failure.

        Args:
            F_transverse_next: Next block's transverse force [N]
            F_preload: Current preload [N]
            stress_area: Bolt stress area [m²]

        Returns:
            Remaining cycles before D = 1.0
        """
        result = self.sun_curve.predict_from_loading(
            F_transverse_next, F_preload, stress_area)
        N_life = result['N_loosening']

        remaining_damage = max(0, 1.0 - self.damage)

        if N_life == float('inf'):
            return float('inf')

        return remaining_damage * N_life


# =============================================================================
# M14: STANDALONE compute_screw_root_stress() — Full Von Mises
# =============================================================================

def compute_screw_root_stress(F_axial: float, M_bending: float,
                               F_trans: float, d: float, d3: float,
                               p: float, At: float) -> float:
    """
    Normalized screw root equivalent stress per Yang et al. (2025) (M14).

    Computes the von Mises equivalent stress at the screw thread root
    from combined axial, bending, and transverse shear loading. This
    enables size-independent loosening life prediction via the Su-N curve.

    Args:
        F_axial: Axial force on bolt [N]
        M_bending: Bending moment at thread root [N·m]
        F_trans: Transverse shear force [N]
        d: Bolt nominal diameter [m]
        d3: Thread root diameter [m] (d3 = d - 1.2268*p)
        p: Thread pitch [m]
        At: Tensile stress area [m²]

    Returns:
        Von Mises equivalent stress at thread root [Pa]

    Reference:
        Yang, S. et al. (2025). "Bolt loosening evaluation method based on
        normalized screw root equivalent stress and loosening life curve."
        Scientific Reports, 15, 20815.
    """
    # Axial stress
    sigma_axial = F_axial / At if At > 0 else 0.0

    # Bending stress at thread root (circular section)
    if d3 > 0:
        sigma_bending = 32.0 * abs(M_bending) / (np.pi * d3 ** 3)
    else:
        sigma_bending = 0.0

    # Thread shear stress (distributed over one pitch engagement)
    if d3 > 0 and p > 0:
        tau_thread = F_trans / (np.pi * d3 * p * 0.5)
    else:
        tau_thread = 0.0

    # Von Mises equivalent stress
    sigma_eq = np.sqrt(
        (sigma_axial + sigma_bending) ** 2 + 3.0 * tau_thread ** 2
    )
    return sigma_eq


# =============================================================================
# M15: STANDALONE miners_rule_loosening() convenience function
# =============================================================================

def miners_rule_loosening(load_blocks: List[tuple],
                          F_preload: float,
                          stress_area: float = None,
                          sun_params: SuNCurveParams = None) -> Dict[str, Any]:
    """
    Miner's rule cumulative damage applied to bolt loosening (M15).

    Simple interface for computing cumulative loosening damage from
    variable amplitude loading blocks.

    D = Σ(nᵢ / Nᵢ)

    Loosening failure predicted when D >= 1.0.

    Args:
        load_blocks: List of (F_transverse [N], n_cycles) tuples
        F_preload: Bolt preload force [N]
        stress_area: Bolt tensile stress area [m²] (None = default 157 mm²)
        sun_params: Su-N curve parameters (None = default M16 10.9)

    Returns:
        Dict with:
            - total_damage: Miner's damage sum D
            - failed: True if D >= 1.0
            - remaining_life_fraction: max(0, 1 - D)
            - total_cycles: Total cycles across all blocks
            - block_details: Per-block breakdown

    Example:
        >>> result = miners_rule_loosening(
        ...     load_blocks=[(5000, 1000), (3000, 5000), (8000, 200)],
        ...     F_preload=50000.0
        ... )
        >>> print(f"Damage: {result['total_damage']:.3f}")

    Reference:
        Yang, H. et al. (2025). "Prediction of Bolt Loosening Life:
        A Practical Approach Considering Variable Amplitude Loading
        and Multi-Bolted Structures." Materials, 18(5), 1069.
    """
    sun_curve = SuNCurveModel(sun_params) if sun_params else SuNCurveModel()
    accumulator = MinersRuleAccumulator(sun_curve=sun_curve)

    blocks = [LoadBlock(F_transverse=ft, n_cycles=nc) for ft, nc in load_blocks]

    return accumulator.compute_variable_amplitude_damage(
        blocks, F_preload, stress_area
    )


# =============================================================================
# FACTORY FUNCTIONS
# =============================================================================

def create_m16_analyzer(mu_initial: float = 0.15,
                        lubricated: bool = True,
                        transverse_displacement_mm: float = 0.65) -> CoupledLooseningAnalyzer:
    """
    Create analyzer for M16 bolt (common size).

    Args:
        mu_initial: Initial friction coefficient
        lubricated: Whether surfaces are lubricated
        transverse_displacement_mm: Transverse displacement amplitude [mm]
            - < 0.3 mm: Minimal loosening risk
            - 0.3-0.5 mm: Moderate loosening
            - > 0.65 mm: Severe loosening (DIN 65151 standard)

    Returns:
        Configured CoupledLooseningAnalyzer
    """
    thread = ThreadGeometryParams(
        pitch=2.0e-3,
        pitch_diameter=14.701e-3,
        major_diameter=16.0e-3,
        flank_angle=np.radians(30),
        num_engaged_threads=8
    )

    bearing = BearingGeometryParams(
        inner_diameter=17.0e-3,
        outer_diameter=24.0e-3
    )

    # Two-stage model parameters adjusted for displacement amplitude
    # Higher displacement = faster Stage I, steeper S-curve.
    # k_stage2 scaled linearly with disp_factor (Jiang 2003 / Lu 2024); the
    # previous disp_factor**2 with a 3e-5 prefactor produced k·N≪1 over
    # 1k–10k cycles — i.e. an essentially linear curve.
    disp_factor = max(transverse_displacement_mm / 0.65, 0.3)
    two_stage = TwoStageLooseningParams(
        N_stage1=int(300 / disp_factor),
        delta_F1_ratio=0.10 + 0.05 * disp_factor,
        N_stage2=int(3000 / disp_factor),
        k_stage2=3e-4 * disp_factor,
        displacement_exponent=2.0
    )

    if lubricated:
        friction = FrictionEvolutionParams(
            mu_initial=mu_initial,
            mu_peak=mu_initial * 1.1,
            mu_steady=mu_initial * 0.7,
            N1=100, N2=500, N3=5000
        )
        wear = WearModelParams(K_archard=1e-7, K_running_in=5e-7, K_steady=1e-7)
    else:
        friction = FrictionEvolutionParams(
            mu_initial=mu_initial,
            mu_peak=mu_initial * 1.3,
            mu_steady=mu_initial * 0.8,
            N1=50, N2=200, N3=2000
        )
        wear = WearModelParams(K_archard=1e-6, K_running_in=5e-6, K_steady=1e-6)

    return CoupledLooseningAnalyzer(
        thread_geometry=thread,
        bearing_geometry=bearing,
        friction_params=friction,
        wear_params=wear,
        two_stage_params=two_stage,
        k_bolt=500e6,
        k_member=1500e6,
        transverse_displacement_mm=transverse_displacement_mm
    )


def _make_friction_params(mu_initial: float, lubricated: bool,
                          evolution_model: str = "Three-Phase") -> FrictionEvolutionParams:
    """Build FrictionEvolutionParams for the chosen evolution model.

    Args:
        mu_initial:      Initial friction coefficient.
        lubricated:      Lubrication state (affects magnitude of peak/steady ratios).
        evolution_model: One of "Constant", "Exponential Decay", "Three-Phase",
                         "Stribeck", "LuGre".

    Returns:
        Configured FrictionEvolutionParams instance.
    """
    # Lubrication scaling: lubricated surfaces have smaller peak and faster stabilisation
    if lubricated:
        peak_ratio   = 1.10   # small running-in bump
        steady_ratio = 0.70   # settles lower (fluid film)
        n1, n2, n3   = 100, 500, 5000
    else:
        peak_ratio   = 1.30
        steady_ratio = 0.80
        n1, n2, n3   = 50, 200, 2000

    model = evolution_model.strip()

    if model == "Constant":
        # μ never changes — set peak = steady = initial, trivial N values
        return FrictionEvolutionParams(
            mu_initial=mu_initial,
            mu_peak=mu_initial,
            mu_steady=mu_initial,
            N1=1, N2=1, N3=1,
        )

    elif model == "Exponential Decay":
        # No running-in rise; purely exponential decay toward mu_steady
        return FrictionEvolutionParams(
            mu_initial=mu_initial,
            mu_peak=mu_initial,              # term1 ≈ 0 (no rise)
            mu_steady=mu_initial * steady_ratio,
            N1=1, N2=1,                      # skip running-in
            N3=n3,                           # decay time constant
        )

    elif model == "Three-Phase":
        # Default three-phase: rise → peak → decay → steady
        return FrictionEvolutionParams(
            mu_initial=mu_initial,
            mu_peak=mu_initial * peak_ratio,
            mu_steady=mu_initial * steady_ratio,
            N1=n1, N2=n2, N3=n3,
        )

    elif model == "Stribeck":
        # Velocity-dependent (approximated in cycle space): very rapid drop to
        # low hydrodynamic friction, then gradual approach to steady state.
        return FrictionEvolutionParams(
            mu_initial=mu_initial,
            mu_peak=mu_initial * 1.05,       # tiny initial bump
            mu_steady=mu_initial * 0.50,     # hydrodynamic regime: significantly lower
            N1=max(5, n1 // 10),
            N2=max(20, n2 // 10),            # fast transition
            N3=max(100, n3 // 5),
        )

    elif model == "LuGre":
        # Dynamic bristle model (approximated in cycle space): pronounced stick-slip
        # peak then relatively fast decay to a moderate steady state.
        return FrictionEvolutionParams(
            mu_initial=mu_initial,
            mu_peak=mu_initial * 1.4,        # high initial bristle stiffness → high peak
            mu_steady=mu_initial * 0.60,
            N1=max(10, n1 // 5),
            N2=max(40, n2 // 5),             # moderate transition speed
            N3=max(300, n3 // 3),
        )

    else:
        # Unknown model — fall back to Three-Phase
        return FrictionEvolutionParams(
            mu_initial=mu_initial,
            mu_peak=mu_initial * peak_ratio,
            mu_steady=mu_initial * steady_ratio,
            N1=n1, N2=n2, N3=n3,
        )


def create_analyzer_from_bolt_size(diameter_mm: float, pitch_mm: float,
                                    grip_length_mm: float = None,
                                    mu_initial: float = 0.15,
                                    lubricated: bool = True,
                                    transverse_displacement_mm: float = 0.65,
                                    k_bolt: float = None,
                                    k_member: float = None,
                                    friction_evolution_model: str = "Three-Phase",
                                    **kwargs) -> CoupledLooseningAnalyzer:
    """
    Create analyzer from bolt size specification.

    Args:
        diameter_mm: Nominal bolt diameter [mm]
        pitch_mm: Thread pitch [mm]
        grip_length_mm: Grip length [mm] (defaults to 3*diameter)
        mu_initial: Initial friction coefficient
        lubricated: Whether surfaces are lubricated
        transverse_displacement_mm: Transverse displacement amplitude [mm]
        **kwargs: Additional parameters passed to analyzer

    Returns:
        Configured CoupledLooseningAnalyzer
    """
    d = diameter_mm * 1e-3
    p = pitch_mm * 1e-3
    L = (grip_length_mm or diameter_mm * 3) * 1e-3

    # ISO metric thread dimensions
    d2 = d - 0.6495 * p  # Pitch diameter
    d3 = d - 1.2268 * p  # Minor diameter

    thread = ThreadGeometryParams(
        pitch=p,
        pitch_diameter=d2,
        major_diameter=d,
        num_engaged_threads=int(8 * d / 0.016)  # Scale with diameter
    )

    # Bearing dimensions (approximate)
    bearing = BearingGeometryParams(
        inner_diameter=d + 0.001,  # Clearance hole
        outer_diameter=d * 1.5     # Under-head diameter
    )

    # Stiffness (use provided or compute from geometry)
    if k_bolt is None or k_member is None:
        E = 210e9  # Steel
        A_s = np.pi / 4 * ((d2 + d3) / 2) ** 2
        k_bolt_computed = E * A_s / L
        k_member_computed = 3 * k_bolt_computed  # Typical ratio

        if k_bolt is None:
            k_bolt = k_bolt_computed
        if k_member is None:
            k_member = k_member_computed

    # Two-stage S-curve model parameters
    # k_stage2 scaled linearly with disp_factor (Jiang 2003 / Lu 2024); the
    # previous disp_factor**2 with a 3e-5 prefactor produced k·N≪1 over
    # 1k–10k cycles — i.e. an essentially linear curve.
    disp_factor = max(transverse_displacement_mm / 0.65, 0.3)
    two_stage = TwoStageLooseningParams(
        N_stage1=int(300 / disp_factor),
        delta_F1_ratio=0.10 + 0.05 * disp_factor,
        N_stage2=int(3000 / disp_factor),
        k_stage2=3e-4 * disp_factor,
        displacement_exponent=2.0
    )

    # Friction parameters — use selected evolution model
    friction = _make_friction_params(mu_initial, lubricated, friction_evolution_model)
    wear = (WearModelParams(K_archard=1e-7, K_running_in=5e-7, K_steady=1e-7)
            if lubricated else
            WearModelParams(K_archard=1e-6, K_running_in=5e-6, K_steady=1e-6))

    return CoupledLooseningAnalyzer(
        thread_geometry=thread,
        bearing_geometry=bearing,
        friction_params=friction,
        wear_params=wear,
        two_stage_params=two_stage,
        k_bolt=k_bolt,
        k_member=k_member,
        transverse_displacement_mm=transverse_displacement_mm,
        **kwargs
    )


# =============================================================================
# MSD MODEL INTEGRATION - FACTORY FUNCTION
# =============================================================================

def create_analyzer_from_msd_model(
    model: 'MSDModel',
    mu_initial: float = None,
    lubricated: bool = True,
    transverse_displacement_mm: float = 0.65,
    friction_evolution_model: str = None,
) -> Tuple[CoupledLooseningAnalyzer, Dict[str, Any]]:
    """
    Create a CoupledLooseningAnalyzer from an MSDModel.

    This function extracts bolt geometry, preload, and system stiffness from
    the MSD model and creates a properly configured analyzer.

    Args:
        model: MSDModel instance from the MSD Builder
        mu_initial: Override initial friction (None = use model's contact friction)
        lubricated: Whether surfaces are lubricated
        transverse_displacement_mm: Transverse displacement amplitude [mm]

    Returns:
        Tuple of (CoupledLooseningAnalyzer, extraction_info_dict)
        The extraction_info_dict contains what was extracted from the model.

    Raises:
        ValueError: If model doesn't have required elements
    """
    # Import here to avoid circular imports
    try:
        from ..core.models.model import MSDModel
        from ..core.models.element import ElementType
    except ImportError:
        from bolt_analysis_studio.core.models.model import MSDModel
        from bolt_analysis_studio.core.models.element import ElementType

    if model is None:
        raise ValueError("MSD model is None")

    # Initialize extraction info
    info = {
        'source': 'MSDModel',
        'model_name': model.name,
        'elements_found': [],
        'warnings': [],
    }

    # =========================================================================
    # 1. EXTRACT BOLT GEOMETRY FROM ELEMENTS
    # =========================================================================

    # Find thread/shank elements for diameter and pitch
    thread_elements = model.get_elements_by_type(ElementType.THREAD)
    shank_elements = model.get_elements_by_type(ElementType.SHANK)
    head_elements = model.get_elements_by_type(ElementType.HEAD)
    nut_elements = model.get_elements_by_type(ElementType.NUT)
    flange_elements = model.get_elements_by_type(ElementType.FLANGE)

    # Track what we found
    info['elements_found'] = {
        'threads': len(thread_elements),
        'shanks': len(shank_elements),
        'heads': len(head_elements),
        'nuts': len(nut_elements),
        'flanges': len(flange_elements),
    }

    # Extract diameter from thread or shank
    diameter_mm = 16.0  # Default M16
    pitch_mm = 2.0      # Default M16 pitch
    grip_length_mm = 48.0  # Default 3*d

    if thread_elements:
        elem = thread_elements[0]
        if hasattr(elem, 'geometry') and elem.geometry:
            if elem.geometry.diameter > 0:
                diameter_mm = elem.geometry.diameter
            if elem.geometry.pitch > 0:
                pitch_mm = elem.geometry.pitch
            if elem.geometry.length > 0:
                grip_length_mm = elem.geometry.length
        info['diameter_source'] = 'thread_element'
    elif shank_elements:
        elem = shank_elements[0]
        if hasattr(elem, 'geometry') and elem.geometry:
            if elem.geometry.diameter > 0:
                diameter_mm = elem.geometry.diameter
            if elem.geometry.length > 0:
                grip_length_mm = elem.geometry.length
        info['diameter_source'] = 'shank_element'
    elif head_elements:
        elem = head_elements[0]
        if hasattr(elem, 'geometry') and elem.geometry:
            if elem.geometry.diameter > 0:
                diameter_mm = elem.geometry.diameter
        info['diameter_source'] = 'head_element'
    else:
        info['warnings'].append('No bolt elements found, using default M16')
        info['diameter_source'] = 'default'

    # Calculate total grip length from all elements
    total_grip = 0.0
    for elem in model.elements:
        if hasattr(elem, 'geometry') and elem.geometry and elem.geometry.length > 0:
            if elem.type not in (ElementType.GROUND, ElementType.HEAD):
                total_grip += elem.geometry.length

    if total_grip > 0:
        grip_length_mm = total_grip
        info['grip_source'] = 'sum_of_elements'
    else:
        grip_length_mm = diameter_mm * 3  # Default 3*d
        info['grip_source'] = 'default_3d'

    info['bolt_diameter_mm'] = diameter_mm
    info['pitch_mm'] = pitch_mm
    info['grip_length_mm'] = grip_length_mm

    # =========================================================================
    # 2. EXTRACT PRELOAD FROM GLOBAL LOADING
    # =========================================================================

    preload = 50000.0  # Default
    transverse_force = 8000.0  # Default
    n_cycles = 2000  # Default

    if hasattr(model, 'global_loading') and model.global_loading:
        loading = model.global_loading
        if loading.F_preload > 0:
            preload = loading.F_preload
            info['preload_source'] = 'global_loading'
        else:
            info['preload_source'] = 'default'
            info['warnings'].append('No preload set in model, using default 50kN')

        if loading.F_transverse > 0:
            transverse_force = loading.F_transverse
            info['transverse_source'] = 'global_loading'
        else:
            info['transverse_source'] = 'default'

        if loading.n_cycles > 0:
            n_cycles = loading.n_cycles
            info['n_cycles_source'] = 'global_loading'
        else:
            info['n_cycles_source'] = 'default'
    else:
        info['preload_source'] = 'default'
        info['transverse_source'] = 'default'
        info['warnings'].append('No loading data in model')

    info['preload_N'] = preload
    info['transverse_force_N'] = transverse_force
    info['n_cycles'] = n_cycles

    # =========================================================================
    # 3. EXTRACT FRICTION FROM CONTACTS OR USE DEFAULT (5-level hierarchy)
    # =========================================================================

    # Level 1: Explicit mu_initial parameter (highest priority)
    if mu_initial and mu_initial > 0:
        friction_initial = mu_initial
        info['friction_source'] = 'parameter'
    # Level 2: model.global_loading.mu_initial (single source of truth)
    elif hasattr(model, 'global_loading') and model.global_loading is not None and \
            hasattr(model.global_loading, 'mu_initial') and \
            getattr(model.global_loading, 'mu_initial', 0) > 0:
        friction_initial = model.global_loading.mu_initial
        info['friction_source'] = 'global_loading'
    # Level 3: model.mu_initial field
    elif hasattr(model, 'mu_initial') and getattr(model, 'mu_initial', 0) > 0:
        friction_initial = model.mu_initial
        info['friction_source'] = 'model_field'
    # Level 4: Average of ThreadContact friction (mu_thread) or BearingContact (mu_bearing)
    elif model.contacts:
        thread_mu_vals = []
        bearing_mu_vals = []
        for contact in model.contacts:
            ctype = getattr(contact, 'contact_type', '')
            mu_val = None
            if hasattr(contact, 'friction') and contact.friction is not None:
                mu_val = getattr(contact.friction, 'mu_static', None)
            elif hasattr(contact, 'mu_static'):
                mu_val = contact.mu_static
            if mu_val and mu_val > 0:
                if 'THREAD' in str(ctype).upper():
                    thread_mu_vals.append(mu_val)
                elif 'BEARING' in str(ctype).upper():
                    bearing_mu_vals.append(mu_val)
        all_vals = thread_mu_vals + bearing_mu_vals
        if all_vals:
            friction_initial = float(np.mean(all_vals))
            info['friction_source'] = 'contact_average'
            if thread_mu_vals:
                info['mu_thread_from_contacts'] = float(np.mean(thread_mu_vals))
            if bearing_mu_vals:
                info['mu_bearing_from_contacts'] = float(np.mean(bearing_mu_vals))
        else:
            friction_initial = 0.12
            info['friction_source'] = 'default'
    # Level 5: Check element friction_properties (contact interface elements)
    else:
        friction_initial = 0.12
        info['friction_source'] = 'default'
        for elem in model.elements:
            if getattr(getattr(elem, 'type', None), 'is_contact_interface', False):
                if hasattr(elem, 'friction') and elem.friction:
                    mu_val = getattr(elem.friction, 'mu_static', 0)
                    if mu_val > 0:
                        friction_initial = mu_val
                        info['friction_source'] = 'element_friction'
                        break

    info['mu_initial'] = friction_initial

    # Resolve friction evolution model: argument → model attribute → default
    if friction_evolution_model is None:
        friction_evolution_model = getattr(model, 'friction_evolution_model', 'Three-Phase')
    info['friction_evolution_model'] = friction_evolution_model

    # =========================================================================
    # 4. COMPUTE SYSTEM STIFFNESS FROM ASSEMBLED MATRICES
    # =========================================================================

    k_bolt = 500e6  # Default
    k_member = 1500e6  # Default

    try:
        M, K, C = model.assemble_matrices()

        if K.size > 0 and K.shape[0] > 0:
            # HIGH-02: Use series stiffness model from assembled [K] matrix.
            # For a bolted joint in series: 1/k_sys = sum(1/k_i)
            # Then bolt vs member split based on DOF partitioning.

            # Get diagonal stiffnesses (filter significant values)
            k_diagonal = np.diag(K)
            k_significant = k_diagonal[k_diagonal > 1e3]  # Only significant stiffnesses

            if len(k_significant) >= 2:
                # Series equivalent of all DOFs: 1/k_sys = sum(1/k_i)
                k_sys_series = 1.0 / np.sum(1.0 / k_significant)

                # Partition: first half = bolt elements, second half = member/contact elements
                n_bolt_dof = min(len(k_significant) // 2, 3)
                k_bolt_elements = k_significant[:n_bolt_dof]
                k_member_elements = k_significant[n_bolt_dof:]

                # Series combination for each partition
                k_bolt_estimate = 1.0 / np.sum(1.0 / k_bolt_elements) if len(k_bolt_elements) > 0 else k_sys_series
                k_member_estimate = 1.0 / np.sum(1.0 / k_member_elements) if len(k_member_elements) > 0 else 3 * k_sys_series

                if k_bolt_estimate > 1e6:
                    k_bolt = k_bolt_estimate
                    info['k_bolt_source'] = 'matrix_series'
                else:
                    info['k_bolt_source'] = 'default'

                if k_member_estimate > 1e6:
                    k_member = k_member_estimate
                    info['k_member_source'] = 'matrix_series'
                else:
                    info['k_member_source'] = 'default'

                info['k_system_series'] = float(k_sys_series)
            elif len(k_significant) == 1:
                # Only one significant stiffness — use as bolt, assume 3x for members
                k_bolt = float(k_significant[0])
                k_member = 3.0 * k_bolt
                info['k_bolt_source'] = 'matrix_single'
                info['k_member_source'] = 'matrix_single'
        else:
            info['k_bolt_source'] = 'default'
            info['k_member_source'] = 'default'
            info['warnings'].append('Empty stiffness matrix, using default stiffness')
    except Exception as e:
        info['k_bolt_source'] = 'default'
        info['k_member_source'] = 'default'
        info['warnings'].append(f'Could not assemble matrices: {e}')

    info['k_bolt'] = k_bolt
    info['k_member'] = k_member

    # =========================================================================
    # 5. CREATE THE ANALYZER
    # =========================================================================

    # =========================================================================
    # 4b. EXTRACT VDI 2230 / PHASE-A LOAD FACTORS FROM global_loading
    # =========================================================================
    slip_onset_factor = 0.46  # Pai-Hess default (Phase C)
    # Determine loading_type for stage classification model selection.
    # Default 'transverse' (Junker 5-stage). 'axial' → 3-stage axial model.
    loading_type: str = 'transverse'
    if hasattr(model, 'global_loading') and model.global_loading is not None:
        gl = model.global_loading
        # slip_onset_factor: user can override via global_loading if stored
        _sof = getattr(gl, 'slip_onset_factor', None)
        if _sof is not None and 0 < _sof <= 1.0:
            slip_onset_factor = float(_sof)
        info['slip_onset_factor'] = slip_onset_factor
        info['R_factor'] = getattr(gl, 'R_factor', 0.0)
        info['dynamic_factor'] = getattr(gl, 'dynamic_factor', 1.0)
        info['load_waveform'] = getattr(gl, 'load_waveform', 'sinusoidal')

        # Map MSD load_type → analyzer loading_type.
        # 'AXIAL' (no 'TRANS' component) → 3-stage axial.
        # Everything else → 5-stage Junker (transverse or combined).
        _lt = getattr(gl, 'load_type', '') or getattr(gl, 'type', '')
        if hasattr(_lt, 'value'):
            _lt = _lt.value          # unwrap Enum
        _lt_upper = str(_lt).upper()
        if 'AXIAL' in _lt_upper and 'TRANS' not in _lt_upper:
            loading_type = 'axial'
        elif 'COMBINED' in _lt_upper:
            loading_type = 'combined'
        info['loading_type'] = loading_type

    # =========================================================================
    # 5. CREATE THE ANALYZER
    # =========================================================================

    # Use the bolt-size factory with extracted parameters.
    # loading_type propagates via **kwargs → CoupledLooseningAnalyzer.__init__().
    analyzer = create_analyzer_from_bolt_size(
        diameter_mm=diameter_mm,
        pitch_mm=pitch_mm,
        grip_length_mm=grip_length_mm,
        mu_initial=friction_initial,
        lubricated=lubricated,
        transverse_displacement_mm=transverse_displacement_mm,
        k_bolt=k_bolt,
        k_member=k_member,
        friction_evolution_model=friction_evolution_model,
        slip_onset_factor=slip_onset_factor,
        loading_type=loading_type,
    )

    # Apply calibrated two_stage overrides (written by CalibrationDialog.apply())
    overrides = getattr(model, '_two_stage_overrides', None)
    if isinstance(overrides, dict) and overrides:
        for attr, value in overrides.items():
            if hasattr(analyzer.two_stage, attr):
                setattr(analyzer.two_stage, attr, value)
        info['two_stage_overrides_applied'] = dict(overrides)

    # Apply fixture (k/c/μ) overrides written by CalibrationDialog._apply_staged.
    # Mirrors the two_stage_overrides path so any calibrated fixture profile
    # survives save/load and is reapplied on every fresh analyzer build.
    fix = getattr(model, '_fixture_overrides', None)
    if isinstance(fix, dict) and fix:
        if "k_bolt" in fix:
            analyzer.k_bolt = float(fix["k_bolt"])
        if "k_member" in fix:
            analyzer.k_member = float(fix["k_member"])
        if "k_bolt" in fix or "k_member" in fix:
            analyzer.recompute_k_system()
        if "k_transverse_ratio" in fix:
            analyzer._k_transverse_ratio = float(fix["k_transverse_ratio"])
        if "damping_zeta" in fix:
            analyzer._damping_zeta = float(fix["damping_zeta"])
        if "mu_thread" in fix and hasattr(analyzer.friction, "mu_thread_initial"):
            analyzer.friction.mu_thread_initial = float(fix["mu_thread"])
        if "mu_bearing" in fix and hasattr(analyzer.friction, "mu_bearing_initial"):
            analyzer.friction.mu_bearing_initial = float(fix["mu_bearing"])
        if "slip_onset_factor" in fix:
            analyzer.slip_onset_factor = float(fix["slip_onset_factor"])
        # Friction ratios — applied as multiples of the (post-override) mu_initial.
        mu_init = getattr(analyzer.friction, "mu_initial", None) or 0.0
        if mu_init > 0:
            if "friction.mu_steady_ratio" in fix and hasattr(analyzer.friction, "mu_steady"):
                analyzer.friction.mu_steady = mu_init * float(fix["friction.mu_steady_ratio"])
            if "friction.mu_peak_ratio" in fix and hasattr(analyzer.friction, "mu_peak"):
                analyzer.friction.mu_peak = mu_init * float(fix["friction.mu_peak_ratio"])
        info['fixture_overrides_applied'] = dict(fix)

    # Store extraction info in analyzer for reference
    analyzer._msd_extraction_info = info

    return analyzer, info


def get_msd_model_summary(model: 'MSDModel') -> Dict[str, Any]:
    """
    Get a summary of what can be extracted from an MSD model for loosening analysis.

    This is useful for displaying to the user what parameters will be used.
    """
    try:
        _, info = create_analyzer_from_msd_model(model, mu_initial=0.12)
        return info
    except Exception as e:
        return {
            'error': str(e),
            'source': 'MSDModel',
            'valid': False
        }


# =============================================================================
# H2: FACTORY FROM CONTACT OBJECTS
# =============================================================================

def create_analyzer_from_contacts(
    thread_contact: 'ThreadContact',
    bearing_contact: 'BearingContact' = None,
    k_bolt: float = None,
    k_member: float = None,
    transverse_displacement_mm: float = 0.65,
    lubricated: bool = True,
    two_stage_params: TwoStageLooseningParams = None
) -> CoupledLooseningAnalyzer:
    """
    Create a CoupledLooseningAnalyzer from Contact objects (H2).

    Extracts thread/bearing geometry and friction parameters directly from
    Contact objects, ensuring consistency between the time-domain solver
    and the per-cycle loosening analyzer.

    Args:
        thread_contact: ThreadContact object with thread geometry and friction
        bearing_contact: Optional BearingContact object for bearing geometry
        k_bolt: Bolt stiffness [N/m]. If None, estimated from thread contact.
        k_member: Member stiffness [N/m]. If None, uses 3*k_bolt.
        transverse_displacement_mm: Transverse displacement amplitude [mm]
        lubricated: Whether surfaces are lubricated
        two_stage_params: Optional two-stage loosening parameters

    Returns:
        CoupledLooseningAnalyzer with Contact objects attached
    """
    # Extract thread geometry
    tg = thread_contact.thread if hasattr(thread_contact, 'thread') else None
    if tg is None:
        raise ValueError("ThreadContact must have a 'thread' (ThreadGeometry) attribute")

    thread_geom = ThreadGeometryParams(
        pitch=tg.pitch,
        pitch_diameter=tg.pitch_diameter,
        major_diameter=tg.major_diameter,
        flank_angle=tg.flank_angle,
        num_engaged_threads=tg.n_engaged_threads
    )

    # Extract bearing geometry
    if bearing_contact is not None:
        bg = bearing_contact.geometry
        bearing_geom = BearingGeometryParams(
            inner_diameter=bg.inner_radius * 2,
            outer_diameter=bg.outer_radius * 2
        )
    else:
        # Default bearing from thread geometry
        d = tg.major_diameter
        bearing_geom = BearingGeometryParams(
            inner_diameter=d + 0.001,
            outer_diameter=d * 1.5
        )

    # Extract friction
    mu_initial = thread_contact.friction.mu_static if thread_contact.friction else 0.15

    if lubricated:
        friction_params = FrictionEvolutionParams(
            mu_initial=mu_initial,
            mu_peak=mu_initial * 1.1,
            mu_steady=mu_initial * 0.7,
            N1=100, N2=500, N3=5000
        )
        wear_params = WearModelParams(K_archard=1e-7, K_running_in=5e-7, K_steady=1e-7)
    else:
        friction_params = FrictionEvolutionParams(
            mu_initial=mu_initial,
            mu_peak=mu_initial * 1.3,
            mu_steady=mu_initial * 0.8,
            N1=50, N2=200, N3=2000
        )
        wear_params = WearModelParams(K_archard=1e-6, K_running_in=5e-6, K_steady=1e-6)

    # Estimate stiffness from thread contact if not provided
    if k_bolt is None:
        k_bolt = thread_contact.stiffness.k_axial if thread_contact.stiffness else 500e6
    if k_member is None:
        k_member = 3 * k_bolt

    return CoupledLooseningAnalyzer(
        thread_geometry=thread_geom,
        bearing_geometry=bearing_geom,
        friction_params=friction_params,
        wear_params=wear_params,
        two_stage_params=two_stage_params,
        k_bolt=k_bolt,
        k_member=k_member,
        transverse_displacement_mm=transverse_displacement_mm,
        thread_contact=thread_contact,
        bearing_contact=bearing_contact,
    )


# =============================================================================
# NL1: MULTI-BOLT STRUCTURE COMPLIANCE MODEL
# =============================================================================

@dataclass
class MultiBoltComplianceModel:
    """
    Multi-bolt structure compliance model (NL1).

    Models load redistribution between bolts in a multi-bolt pattern
    when individual bolts lose preload. Uses a compliance influence
    matrix [C] relating bolt forces to structural displacements.

    Reference: Nassar & Abboud (2009), Multi-bolt Interaction.

    The compliance matrix C_ij represents the displacement at bolt i
    due to unit force at bolt j. For a symmetric circular pattern:
        C_ii = 1/k_local (self compliance)
        C_ij = alpha / (k_structure * r_ij) (cross compliance, decays with distance)

    When bolt j loosens (F_j decreases), the equilibrium:
        {delta} = [C]{F}
    requires redistribution: other bolts pick up the released load.

    Supported patterns:
    - 'circular': Equally-spaced bolts on a bolt circle (default)
    - 'linear': Bolts in a straight line with equal spacing
    - 'rectangular': Bolts on a rectangular grid (n_bolts should be a perfect square)

    Usage:
        model = MultiBoltComplianceModel(n_bolts=8, bolt_circle_radius=0.15)
        C = model.build_compliance_matrix()
        adjusted = model.redistribute_load(current_preloads, external_force=10000)
    """
    n_bolts: int = 8                    # Number of bolts in pattern
    bolt_circle_radius: float = 0.15    # Bolt circle radius [m]
    k_local: float = 500e6             # Local bolt+member stiffness [N/m]
    k_structure: float = 2000e6        # Global structure stiffness [N/m]
    coupling_alpha: float = 0.1        # Cross-coupling coefficient (0-1)
    pattern: str = 'circular'          # 'circular', 'linear', or 'rectangular'

    def compute_bolt_positions(self) -> np.ndarray:
        """
        Compute bolt positions based on pattern type.

        Returns:
            Array of shape (n_bolts, 2) with [x, y] coordinates [m].
        """
        n = self.n_bolts

        if self.pattern == 'circular':
            # Equally-spaced bolts on a circle
            angles = np.linspace(0, 2 * np.pi, n, endpoint=False)
            positions = np.column_stack([
                self.bolt_circle_radius * np.cos(angles),
                self.bolt_circle_radius * np.sin(angles)
            ])

        elif self.pattern == 'linear':
            # Bolts in a straight line, total span = 2 * bolt_circle_radius
            total_span = 2 * self.bolt_circle_radius
            if n > 1:
                x_coords = np.linspace(-total_span / 2, total_span / 2, n)
            else:
                x_coords = np.array([0.0])
            positions = np.column_stack([x_coords, np.zeros(n)])

        elif self.pattern == 'rectangular':
            # Rectangular grid: try to make as square as possible
            n_side = int(np.ceil(np.sqrt(n)))
            n_rows = n_side
            n_cols = int(np.ceil(n / n_rows))
            total_span = 2 * self.bolt_circle_radius
            spacing = total_span / max(n_cols - 1, 1) if n_cols > 1 else 0.0
            positions_list = []
            for row in range(n_rows):
                for col in range(n_cols):
                    if len(positions_list) >= n:
                        break
                    x = -total_span / 2 + col * spacing if n_cols > 1 else 0.0
                    y = -total_span / 2 + row * spacing if n_rows > 1 else 0.0
                    positions_list.append([x, y])
            positions = np.array(positions_list[:n])

        else:
            raise ValueError(f"Unknown pattern type: {self.pattern}. "
                             f"Use 'circular', 'linear', or 'rectangular'.")

        return positions

    def _compute_distance_matrix(self, positions: np.ndarray) -> np.ndarray:
        """
        Compute pairwise distance matrix between bolt positions.

        Args:
            positions: Array of shape (n_bolts, 2) with bolt positions.

        Returns:
            Symmetric distance matrix of shape (n_bolts, n_bolts) [m].
        """
        n = positions.shape[0]
        dist = np.zeros((n, n))
        for i in range(n):
            for j in range(i + 1, n):
                d = np.sqrt((positions[i, 0] - positions[j, 0]) ** 2 +
                            (positions[i, 1] - positions[j, 1]) ** 2)
                dist[i, j] = d
                dist[j, i] = d
        return dist

    def build_compliance_matrix(self) -> np.ndarray:
        """
        Build the n_bolts x n_bolts compliance influence matrix.

        The diagonal terms represent self-compliance (1/k_local).
        The off-diagonal terms represent cross-compliance that decays
        with distance between bolts:
            C_ij = alpha / (k_structure * r_ij)

        For bolts that are very close together, the cross-compliance
        is capped at a fraction of the self-compliance to avoid
        numerical issues.

        Returns:
            Compliance matrix [C] of shape (n_bolts, n_bolts) [m/N].
        """
        n = self.n_bolts
        positions = self.compute_bolt_positions()
        dist_matrix = self._compute_distance_matrix(positions)

        C = np.zeros((n, n))

        # Self compliance (diagonal)
        c_self = 1.0 / self.k_local
        np.fill_diagonal(C, c_self)

        # Cross compliance (off-diagonal)
        # Decays inversely with distance, scaled by coupling coefficient
        for i in range(n):
            for j in range(i + 1, n):
                r_ij = dist_matrix[i, j]
                if r_ij > 1e-10:
                    c_cross = self.coupling_alpha / (self.k_structure * r_ij)
                    # Cap cross-compliance at 50% of self-compliance
                    c_cross = min(c_cross, 0.5 * c_self)
                else:
                    c_cross = 0.5 * c_self

                C[i, j] = c_cross
                C[j, i] = c_cross

        return C

    def redistribute_load(self, preloads: np.ndarray,
                          external_force: float = 0.0) -> np.ndarray:
        """
        Compute adjusted preloads after redistribution.

        When a bolt loses preload, the structural compliance causes
        neighboring bolts to carry additional load. This method solves
        the equilibrium problem:
            {delta} = [C] {F}
        with the constraint that total clamping force is maintained
        (or reduced by the external force).

        The approach:
        1. Compute target displacements from initial (uniform) state
        2. Solve for force distribution that satisfies equilibrium
        3. Enforce non-negativity (bolt cannot push)

        Args:
            preloads: Array of current bolt preloads [N], shape (n_bolts,)
            external_force: Total external force on flange [N] (positive = tension)

        Returns:
            Adjusted preloads accounting for compliance interaction [N].
        """
        n = self.n_bolts
        preloads = np.asarray(preloads, dtype=float)
        if preloads.shape[0] != n:
            raise ValueError(f"preloads array length {preloads.shape[0]} != n_bolts {n}")

        C = self.build_compliance_matrix()

        # Compute current displacements from current preloads
        delta_current = C @ preloads

        # Reference displacement: mean of all bolt displacements
        # In a rigid flange, all bolts deflect equally; compliance breaks this
        delta_mean = np.mean(delta_current)

        # Target displacements: enforce flange compatibility
        # The flange tends to equalize displacements (rigid body constraint)
        # Deviation from mean is reduced by the flange stiffness
        # delta_target_i = delta_mean + (1 - coupling) * (delta_i - delta_mean)
        rigidity_factor = 1.0 - self.coupling_alpha
        delta_target = delta_mean + rigidity_factor * (delta_current - delta_mean)

        # Add external force effect (distributed equally by default)
        if abs(external_force) > 0:
            # External force reduces clamping force
            F_external_per_bolt = external_force / n
            delta_external = F_external_per_bolt / self.k_local
            delta_target += delta_external

        # Solve for adjusted forces: F_adj = C^{-1} * delta_target
        try:
            # Use least-squares for robustness (handles near-singular C)
            F_adjusted, _, _, _ = np.linalg.lstsq(C, delta_target, rcond=None)
        except np.linalg.LinAlgError:
            warnings.warn("MultiBoltComplianceModel: Singular compliance matrix. "
                          "Returning original preloads.")
            return preloads.copy()

        # Enforce non-negativity: bolt preload cannot be negative
        F_adjusted = np.maximum(F_adjusted, 0.0)

        # Scale to preserve total clamping force (minus external)
        total_original = np.sum(preloads) - external_force
        total_adjusted = np.sum(F_adjusted)
        if total_adjusted > 1e-10 and total_original > 0:
            scale = total_original / total_adjusted
            F_adjusted *= scale

        return F_adjusted

    def run_coupled_analysis(self, analyzers: List[CoupledLooseningAnalyzer],
                             F_preload_initial: float,
                             F_transverse: float,
                             n_cycles: int,
                             temperature: float = 20.0) -> Dict:
        """
        Run coupled multi-bolt loosening analysis.

        Simulates cycle-by-cycle loosening with load redistribution between
        bolts. At each cycle:
        1. Each analyzer computes one-cycle loosening for its bolt
        2. Updated preloads are redistributed through the compliance model
        3. Redistributed preloads feed back into the next cycle

        This captures the cascade effect: when one bolt loosens, its neighbors
        carry more load, increasing their friction capacity but also their
        stress, and the loosened bolt carries less load, further reducing its
        friction capacity.

        Args:
            analyzers: List of CoupledLooseningAnalyzer instances (one per bolt).
                       If fewer than n_bolts, the last analyzer is duplicated.
            F_preload_initial: Initial preload for all bolts [N]
            F_transverse: Transverse force amplitude [N]
            n_cycles: Number of cycles to simulate
            temperature: Operating temperature [C]

        Returns:
            Dictionary containing:
            - 'cycles': Array of cycle numbers
            - 'preloads': Array (n_cycles+1, n_bolts) of preload history
            - 'preload_ratios': Preload ratios relative to initial
            - 'total_preload': Sum of all bolt preloads vs cycle
            - 'bolt_positions': Bolt positions array
            - 'min_preload_ratio': Minimum preload ratio across all bolts at each cycle
            - 'max_load_increase': Maximum additional load carried by any bolt (%)
            - 'redistribution_events': Cycles where significant redistribution occurred
        """
        n = self.n_bolts

        # Ensure we have enough analyzers
        if len(analyzers) < n:
            # Duplicate last analyzer (deep copy) to fill
            while len(analyzers) < n:
                analyzers.append(copy.deepcopy(analyzers[-1]))
        elif len(analyzers) > n:
            analyzers = analyzers[:n]

        # Reset all analyzers
        for analyzer in analyzers:
            analyzer.reset_state()
            analyzer.state.preload_initial = F_preload_initial
            analyzer.state.preload = F_preload_initial
            analyzer.state.preload_ratio = 1.0
            analyzer.initial_preload = F_preload_initial

        # Storage arrays
        cycles_arr = np.arange(n_cycles + 1)
        preloads_history = np.zeros((n_cycles + 1, n))
        preloads_history[0, :] = F_preload_initial
        current_preloads = np.full(n, F_preload_initial)

        redistribution_events = []
        REDISTRIBUTION_THRESHOLD = 0.02  # 2% change triggers logging

        for cycle in range(1, n_cycles + 1):
            # Step 1: Run one cycle of each bolt's loosening analysis
            new_preloads = np.zeros(n)
            for i in range(n):
                state = analyzers[i].update_state(
                    cycle, current_preloads[i], F_transverse, temperature
                )
                analyzers[i].state = state
                new_preloads[i] = state.preload

            # Step 2: Redistribute load through structural compliance
            redistributed = self.redistribute_load(new_preloads)

            # Step 3: Check for significant redistribution
            if np.max(np.abs(redistributed - new_preloads)) > REDISTRIBUTION_THRESHOLD * F_preload_initial:
                redistribution_events.append(cycle)

            # Step 4: Update preloads for next cycle, clamp to [0, 1.5 * F_initial]
            # The 1.5x cap prevents unrealistic load concentration
            current_preloads = np.clip(redistributed, 0.0, 1.5 * F_preload_initial)

            # Update analyzer states with redistributed preloads
            for i in range(n):
                analyzers[i].state.preload = current_preloads[i]
                analyzers[i].state.preload_ratio = (
                    current_preloads[i] / F_preload_initial
                    if F_preload_initial > 0 else 0.0
                )

            preloads_history[cycle, :] = current_preloads

        # Compute summary results
        preload_ratios = preloads_history / F_preload_initial if F_preload_initial > 0 else preloads_history
        total_preload = np.sum(preloads_history, axis=1)
        min_preload_ratio = np.min(preload_ratios, axis=1)

        # Maximum load increase: highest ratio of any bolt's load relative to initial
        max_load_increase_pct = (np.max(preload_ratios, axis=1) - 1.0) * 100.0

        return {
            'cycles': cycles_arr,
            'preloads': preloads_history,
            'preload_ratios': preload_ratios,
            'total_preload': total_preload,
            'bolt_positions': self.compute_bolt_positions(),
            'min_preload_ratio': min_preload_ratio,
            'max_load_increase': max_load_increase_pct,
            'redistribution_events': redistribution_events,
            'compliance_matrix': self.build_compliance_matrix(),
            'n_bolts': n,
            'pattern': self.pattern,
        }


# =============================================================================
# NL2: BOLT BENDING EFFECTS ON LOOSENING
# =============================================================================

@dataclass
class BoltBendingParams:
    """
    Parameters for bolt bending effect model (NL2).

    Defines the geometric and material properties needed to compute
    bending effects on bolt loosening. Eccentric loading and misalignment
    create bending moments that non-uniformly distribute contact pressure,
    reducing effective friction capacity and accelerating loosening.

    Reference: Nassar & Yang (2007), Bending Effects on Self-Loosening.
    """
    eccentricity: float = 0.0          # Loading eccentricity [m]
    misalignment_angle: float = 0.0    # Bolt axis misalignment [rad]
    bolt_diameter: float = 16e-3       # Bolt nominal diameter [m]
    grip_length: float = 48e-3         # Grip length [m]
    E_bolt: float = 210e9              # Bolt Young's modulus [Pa]
    moment_of_inertia: float = 0.0     # I = pi*d^4/64 (computed if 0)
    beta_empirical: float = 0.4        # Empirical friction reduction factor (0.3-0.5)
    yield_strength: float = 900e6      # Bolt yield strength [Pa] (for bending limit checks)


class BoltBendingModel:
    """
    Bolt bending effects on loosening (NL2).

    Eccentric loading or misalignment causes bolt bending, which:
    1. Creates non-uniform contact pressure at bearing surface
    2. Increases peak thread stress (stress concentration amplified)
    3. Causes cyclic bending stress that accelerates fatigue loosening
    4. Reduces effective friction capacity (non-uniform normal force)

    Reference: Nassar & Yang (2007), Bending Effects on Self-Loosening.

    The bending stress at the thread root:
        sigma_bending = M * c / I = (F * e + F * L * sin(alpha)) * d/2 / (pi*d^4/64)

    The friction reduction factor due to non-uniform pressure:
        f_bending = 1 - (sigma_bending / sigma_axial) * beta
    where beta is an empirical factor (0.3-0.5 typical).

    When f_bending < 1.0, effective friction is reduced, making loosening easier.
    When sigma_bending approaches sigma_axial, the bearing surface partially lifts
    off and friction is dramatically reduced.

    Usage:
        params = BoltBendingParams(eccentricity=2e-3, misalignment_angle=0.01)
        model = BoltBendingModel(params)
        factor = model.friction_reduction_factor(50000, 5000)
        modified_rate = model.modified_loosening_rate(base_rate, 50000, 5000)
    """

    def __init__(self, params: BoltBendingParams = None):
        """
        Initialize the bolt bending model.

        Args:
            params: BoltBendingParams with geometry and material properties.
                    If None, default M16 bolt parameters are used.
        """
        self.params = params or BoltBendingParams()

        # Auto-compute moment of inertia if not provided
        if self.params.moment_of_inertia <= 0:
            d = self.params.bolt_diameter
            self.params.moment_of_inertia = np.pi * d ** 4 / 64

        # Derived geometric properties
        self._section_modulus = (
            self.params.moment_of_inertia / (self.params.bolt_diameter / 2)
        )  # W = I / c [m^3]
        self._cross_section_area = np.pi * self.params.bolt_diameter ** 2 / 4

    def compute_bending_moment(self, F_preload: float,
                                F_transverse: float = 0.0) -> float:
        """
        Compute bending moment at the critical section (thread root).

        The bending moment arises from two sources:
        1. Loading eccentricity: M_e = F_preload * eccentricity
        2. Misalignment: M_a = F_preload * grip_length * sin(misalignment_angle)
        3. Transverse force: M_t = F_transverse * grip_length / 2
           (approximation: bolt as fixed-fixed beam with mid-span load)

        Args:
            F_preload: Current bolt preload [N]
            F_transverse: Transverse force on bolt [N]

        Returns:
            Maximum bending moment at critical section [N*m]
        """
        p = self.params

        # Bending from eccentricity
        M_eccentricity = abs(F_preload) * abs(p.eccentricity)

        # Bending from misalignment
        # Small angle: sin(alpha) ~ alpha for angles < 0.1 rad
        M_misalignment = abs(F_preload) * p.grip_length * np.sin(abs(p.misalignment_angle))

        # Bending from transverse force (fixed-guided beam model)
        # M = F_trans * L / 4 for simply supported, F_trans * L / 8 for fixed-fixed
        # Use intermediate value for bolted joint (partially constrained)
        M_transverse = abs(F_transverse) * p.grip_length / 6.0

        # Total bending moment (SRSS combination for independent sources)
        M_total = np.sqrt(M_eccentricity ** 2 + M_misalignment ** 2 + M_transverse ** 2)

        return M_total

    def compute_bending_stress(self, F_preload: float,
                                F_transverse: float = 0.0) -> float:
        """
        Compute maximum bending stress at the thread root.

        sigma_bending = M / W

        where W = I / c is the elastic section modulus of the bolt shank.

        Args:
            F_preload: Current bolt preload [N]
            F_transverse: Transverse force [N]

        Returns:
            Maximum bending stress [Pa]
        """
        M = self.compute_bending_moment(F_preload, F_transverse)
        sigma_bending = M / self._section_modulus if self._section_modulus > 0 else 0.0
        return sigma_bending

    def compute_axial_stress(self, F_preload: float) -> float:
        """
        Compute nominal axial stress in the bolt.

        sigma_axial = F_preload / A

        Args:
            F_preload: Current bolt preload [N]

        Returns:
            Nominal axial stress [Pa]
        """
        return abs(F_preload) / self._cross_section_area if self._cross_section_area > 0 else 0.0

    def compute_stress_ratio(self, F_preload: float,
                              F_transverse: float = 0.0) -> float:
        """
        Compute ratio of bending stress to axial stress.

        This ratio quantifies how severe the bending effect is relative
        to the axial clamping. When ratio -> 0, bending is negligible.
        When ratio -> 1, one side of the bearing surface has zero contact
        pressure (incipient liftoff). When ratio > 1, partial liftoff occurs.

        Args:
            F_preload: Current bolt preload [N]
            F_transverse: Transverse force [N]

        Returns:
            Stress ratio sigma_bending / sigma_axial (dimensionless)
        """
        sigma_b = self.compute_bending_stress(F_preload, F_transverse)
        sigma_a = self.compute_axial_stress(F_preload)

        if sigma_a < 1e-3:
            # Very low preload: bending dominates completely
            return float('inf') if sigma_b > 0 else 0.0

        return sigma_b / sigma_a

    def friction_reduction_factor(self, F_preload: float,
                                   F_transverse: float = 0.0) -> float:
        """
        Compute friction reduction factor due to non-uniform contact pressure.

        The non-uniform pressure distribution under bending causes the
        effective friction coefficient to be lower than the nominal value.
        This is because friction force is proportional to local normal force,
        and non-uniform pressure is less efficient than uniform pressure
        for resisting rotation.

        The reduction factor:
            f = 1 - beta * (sigma_bending / sigma_axial)

        where beta is an empirical factor (0.3-0.5 for typical joints).

        When stress ratio > 1 (partial liftoff), a more aggressive
        reduction applies based on the contact arc fraction.

        Args:
            F_preload: Current bolt preload [N]
            F_transverse: Transverse force [N]

        Returns:
            Friction reduction factor in range [0.1, 1.0].
            1.0 = no reduction (concentric loading)
            0.1 = severe reduction (near total liftoff)
        """
        stress_ratio = self.compute_stress_ratio(F_preload, F_transverse)
        beta = self.params.beta_empirical

        if stress_ratio <= 0.0:
            return 1.0

        if stress_ratio < 1.0:
            # Linear reduction regime (before liftoff)
            f = 1.0 - beta * stress_ratio
        else:
            # Partial liftoff regime
            # Contact arc reduces: theta_contact = 2 * arccos(1 - 1/stress_ratio)
            # Effective friction ~ theta_contact / (2*pi)
            # But simplified: exponential decay beyond liftoff
            f_at_liftoff = 1.0 - beta  # Value at stress_ratio = 1.0
            excess = stress_ratio - 1.0
            f = f_at_liftoff * np.exp(-2.0 * excess)

        # Enforce physical bounds
        return np.clip(f, 0.1, 1.0)

    def modified_loosening_rate(self, base_rate: float, F_preload: float,
                                F_transverse: float = 0.0) -> float:
        """
        Compute modified loosening rate accounting for bending effects.

        The bending amplifies the loosening rate through two mechanisms:
        1. Friction reduction: lower effective mu -> easier nut rotation
        2. Cyclic bending: stress cycling at thread root promotes fatigue
           loosening even at loads below the static loosening threshold

        The amplification factor:
            A = 1 / f_bending + gamma * (sigma_b / sigma_y)^2

        where:
        - f_bending is the friction reduction factor
        - gamma = 0.5 is a cyclic fatigue contribution factor
        - sigma_y is bolt yield strength

        Args:
            base_rate: Base loosening rate without bending [rad/cycle]
            F_preload: Current bolt preload [N]
            F_transverse: Transverse force [N]

        Returns:
            Modified loosening rate [rad/cycle] >= base_rate
        """
        f_bending = self.friction_reduction_factor(F_preload, F_transverse)

        # Friction-based amplification: lower f -> higher rate
        # When f = 1.0 (no bending), amplification = 1.0
        # When f = 0.5, amplification = 2.0
        friction_amplification = 1.0 / max(f_bending, 0.1)

        # Cyclic bending fatigue contribution
        # Additional loosening from bending stress cycling at thread root
        sigma_b = self.compute_bending_stress(F_preload, F_transverse)
        sigma_y = self.params.yield_strength
        gamma_fatigue = 0.5  # Cyclic fatigue loosening sensitivity

        if sigma_y > 0:
            fatigue_factor = gamma_fatigue * (sigma_b / sigma_y) ** 2
        else:
            fatigue_factor = 0.0

        # Combined amplification
        total_amplification = friction_amplification + fatigue_factor

        # Modified rate: always >= base_rate
        return base_rate * total_amplification

    def get_summary(self, F_preload: float,
                    F_transverse: float = 0.0) -> Dict[str, float]:
        """
        Get comprehensive summary of bending effects.

        Args:
            F_preload: Current bolt preload [N]
            F_transverse: Transverse force [N]

        Returns:
            Dictionary with all bending effect quantities.
        """
        M = self.compute_bending_moment(F_preload, F_transverse)
        sigma_b = self.compute_bending_stress(F_preload, F_transverse)
        sigma_a = self.compute_axial_stress(F_preload)
        stress_ratio = self.compute_stress_ratio(F_preload, F_transverse)
        f_red = self.friction_reduction_factor(F_preload, F_transverse)

        sigma_y = self.params.yield_strength
        sigma_combined = np.sqrt(sigma_a ** 2 + 3 * (sigma_b * 0.5) ** 2)  # von Mises approx

        return {
            'bending_moment_Nm': M,
            'bending_stress_MPa': sigma_b * 1e-6,
            'axial_stress_MPa': sigma_a * 1e-6,
            'stress_ratio': stress_ratio,
            'friction_reduction_factor': f_red,
            'von_mises_stress_MPa': sigma_combined * 1e-6,
            'yield_utilization': sigma_combined / sigma_y if sigma_y > 0 else 0.0,
            'partial_liftoff': stress_ratio > 1.0,
            'eccentricity_mm': self.params.eccentricity * 1e3,
            'misalignment_deg': np.degrees(self.params.misalignment_angle),
        }


# =============================================================================
# NL3: TIGHTENING PROCESS RESIDUAL STRESS MODEL
# =============================================================================

class TighteningMethod(Enum):
    """Tightening method enumeration for NL3 residual stress model."""
    TORQUE_CONTROLLED = "torque_controlled"
    ANGLE_CONTROLLED = "angle_controlled"
    YIELD_CONTROLLED = "yield_controlled"
    TENSION_CONTROLLED = "tension_controlled"


@dataclass
class TighteningParams:
    """
    Parameters for tightening process residual stress model (NL3).

    Defines the tightening method, target preload, and bolt/friction
    properties needed to compute residual stress state and its effect
    on subsequent loosening behavior.

    Reference: VDI 2230 (2015) Part 1, Section 5.4
    """
    method: TighteningMethod = TighteningMethod.TORQUE_CONTROLLED
    target_preload: float = 50000.0      # Target preload [N]
    applied_torque: float = 0.0          # Applied tightening torque [N*m]
    tightening_angle: float = 0.0        # Tightening angle [deg] (for angle method)
    mu_thread: float = 0.12              # Thread friction during tightening
    mu_bearing: float = 0.12             # Bearing friction during tightening
    bolt_yield_strength: float = 900e6   # Bolt yield strength [Pa]
    bolt_stress_area: float = 157e-6     # Bolt stress area [m^2]
    bolt_shank_diameter: float = 14.0e-3  # Shank diameter for polar section modulus [m]
    relaxation_time_constant: float = 72.0  # Torsional relaxation time constant [hours]
    relaxation_fraction: float = 0.10    # Typical fraction of torsion that relaxes (5-20%)


class TighteningResidualModel:
    """
    Tightening process residual stress model (NL3).

    Models the residual stress state after tightening and its effect on
    subsequent loosening behavior. Different tightening methods leave
    different residual stress patterns:

    1. Torque-controlled: Highest uncertainty (+/-25-35%), moderate residual torsion
    2. Angle-controlled: Lower uncertainty (+/-10-15%), known plastic deformation
    3. Yield-controlled: Bolt at yield, high residual stress
    4. Tension-controlled: No residual torsion (ideal)

    Reference: VDI 2230 (2015) Part 1, Section 5.4

    The residual torsional stress from tightening:
        tau_residual = T_thread / W_p
    where W_p = pi*d_s^3/16 is the polar section modulus

    The von Mises equivalent stress:
        sigma_eq = sqrt(sigma_axial^2 + 3*tau_residual^2)

    After snug-down, some torsional stress relaxes (typically 5-20%),
    reducing preload by:
        delta_F_relax = (tau_initial - tau_final) / tau_initial * F_p * R_t
    where R_t is the torsional-to-total preload ratio.

    Usage:
        params = TighteningParams(method=TighteningMethod.TORQUE_CONTROLLED,
                                  target_preload=50000, mu_thread=0.12)
        thread_geom = ThreadGeometryParams(pitch=2e-3, pitch_diameter=14.7e-3)
        model = TighteningResidualModel(params, thread_geom)
        torque = model.compute_tightening_torque()
        relaxation = model.compute_torsion_relaxation(time_hours=24)
        F_eff = model.get_effective_preload()
    """

    def __init__(self, params: TighteningParams = None,
                 thread_geometry: ThreadGeometryParams = None):
        """
        Initialize the tightening residual stress model.

        Args:
            params: TighteningParams with tightening method and properties.
            thread_geometry: ThreadGeometryParams for torque calculations.
        """
        self.params = params or TighteningParams()
        self.thread = thread_geometry or ThreadGeometryParams()

        # Polar section modulus W_p = pi * d_s^3 / 16
        d_s = self.params.bolt_shank_diameter
        self._W_p = np.pi * d_s ** 3 / 16  # [m^3]

        # Cross-section area of shank
        self._A_shank = np.pi * d_s ** 2 / 4  # [m^2]

    def compute_tightening_torque(self) -> float:
        """
        Compute tightening torque using VDI 2230 torque-preload relationship.

        T_A = F_V * (d2/2 * (p/(pi*d2) + mu_t/cos(alpha)) / (1 - mu_t*p/(pi*d2*cos(alpha)))
              + mu_b * r_eff)

        Simplified (VDI 2230 K-factor approach):
            T_A = F_V * (0.16 * p + 0.58 * d2 * mu_t + D_km * mu_b)
        where D_km is the mean bearing diameter.

        If applied_torque is already specified in params and is non-zero,
        that value is used directly.

        Returns:
            Tightening torque [N*m]
        """
        p = self.params
        t = self.thread

        # If torque already specified, use it
        if p.applied_torque > 0:
            return p.applied_torque

        F_V = p.target_preload
        d2 = t.pitch_diameter
        pitch = t.pitch
        alpha = t.flank_angle
        mu_t = p.mu_thread
        mu_b = p.mu_bearing

        # VDI 2230 thread torque
        # T_thread = F_V * d2/2 * (tan(lambda) + mu_t/cos(alpha)) / (1 - mu_t*tan(lambda)/cos(alpha))
        helix_angle = t.helix_angle
        tan_lambda = np.tan(helix_angle)
        cos_alpha = np.cos(alpha)

        # Thread torque component
        numerator = tan_lambda + mu_t / cos_alpha
        denominator = 1.0 - mu_t * tan_lambda / cos_alpha
        if abs(denominator) < 1e-10:
            denominator = 1e-10  # Avoid division by zero

        T_thread = F_V * (d2 / 2) * (numerator / denominator)

        # Bearing torque component
        # Effective bearing radius (default estimate from bolt diameter)
        d_hole = t.major_diameter + 1e-3  # Clearance hole
        d_head = t.major_diameter * 1.5   # Under-head diameter estimate
        r_eff = (d_head + d_hole) / 4     # Mean bearing radius

        T_bearing = F_V * mu_b * r_eff

        # Total tightening torque
        T_total = T_thread + T_bearing

        return T_total

    def compute_thread_torque_component(self) -> float:
        """
        Compute only the thread friction torque component.

        This is the portion of tightening torque that creates residual
        torsional stress in the bolt shank.

        T_thread = F_V * d2/2 * (tan(lambda) + mu_t/cos(alpha)) / (1 - mu_t*tan(lambda)/cos(alpha))

        Returns:
            Thread friction torque [N*m]
        """
        p = self.params
        t = self.thread

        F_V = p.target_preload
        d2 = t.pitch_diameter
        alpha = t.flank_angle
        mu_t = p.mu_thread

        helix_angle = t.helix_angle
        tan_lambda = np.tan(helix_angle)
        cos_alpha = np.cos(alpha)

        numerator = tan_lambda + mu_t / cos_alpha
        denominator = 1.0 - mu_t * tan_lambda / cos_alpha
        if abs(denominator) < 1e-10:
            denominator = 1e-10

        T_thread = F_V * (d2 / 2) * (numerator / denominator)

        # Subtract the pitch torque (which creates axial force, not torsion)
        T_pitch = F_V * t.pitch / (2 * np.pi)
        T_friction_only = T_thread - T_pitch

        return max(T_friction_only, 0.0)

    def compute_residual_torsion(self) -> float:
        """
        Compute residual torsional stress after tightening [Pa].

        The thread friction torque component creates torsional stress
        in the bolt shank. For tension-controlled tightening, this is zero.

        tau_residual = T_thread_friction / W_p

        Returns:
            Residual torsional shear stress [Pa]
        """
        if self.params.method == TighteningMethod.TENSION_CONTROLLED:
            # Direct tension: no torsion applied
            return 0.0

        T_friction = self.compute_thread_torque_component()
        tau = T_friction / self._W_p if self._W_p > 0 else 0.0

        return tau

    def compute_axial_stress(self) -> float:
        """
        Compute axial tensile stress in the bolt from preload.

        sigma_axial = F_V / A_s

        Returns:
            Axial stress [Pa]
        """
        return self.params.target_preload / self.params.bolt_stress_area \
            if self.params.bolt_stress_area > 0 else 0.0

    def compute_von_mises_stress(self) -> float:
        """
        Compute von Mises equivalent stress in bolt after tightening.

        sigma_eq = sqrt(sigma_axial^2 + 3 * tau_residual^2)

        This is critical for yield-controlled tightening, where the bolt
        is intentionally loaded to yield under the combined stress state.

        Returns:
            Von Mises equivalent stress [Pa]
        """
        sigma_a = self.compute_axial_stress()
        tau = self.compute_residual_torsion()

        sigma_vm = np.sqrt(sigma_a ** 2 + 3.0 * tau ** 2)
        return sigma_vm

    def compute_torsion_relaxation(self, time_hours: float = 24.0) -> Dict[str, float]:
        """
        Compute preload change from torsional stress relaxation.

        After tightening, the torsional stress gradually relaxes (5-20%
        typically), which causes a corresponding preload loss. The
        relaxation follows an exponential decay model.

        The process:
        1. Initial torsional stress tau_0 is locked in during tightening
        2. Over time, micro-plastic flow relaxes the torsion:
           tau(t) = tau_0 * (1 - R_f * (1 - exp(-t/tau_c)))
        3. As torsion relaxes, the bolt shortens slightly, losing preload
        4. Preload loss = F_V * R_t * delta_tau/tau_0
           where R_t = torsional contribution ratio

        Args:
            time_hours: Time after tightening [hours]. Default 24h.

        Returns:
            Dictionary with:
            - 'tau_initial_MPa': Initial torsional stress [MPa]
            - 'tau_final_MPa': Torsional stress after relaxation [MPa]
            - 'tau_reduction_pct': Percentage reduction in torsion
            - 'preload_loss_N': Preload loss from torsion relaxation [N]
            - 'preload_loss_pct': Percentage preload loss
            - 'F_effective': Effective preload after relaxation [N]
            - 'von_mises_initial_MPa': Initial von Mises stress [MPa]
            - 'von_mises_final_MPa': Final von Mises stress [MPa]
        """
        tau_initial = self.compute_residual_torsion()
        sigma_axial = self.compute_axial_stress()
        F_V = self.params.target_preload
        p = self.params

        # Relaxation fraction over time (exponential approach)
        tau_c = p.relaxation_time_constant  # Time constant [hours]
        R_f = p.relaxation_fraction  # Maximum fraction of torsion that relaxes
        relaxation_progress = 1.0 - np.exp(-time_hours / tau_c)
        tau_relaxed_fraction = R_f * relaxation_progress

        # Final torsional stress
        tau_final = tau_initial * (1.0 - tau_relaxed_fraction)

        # Torsional contribution ratio R_t
        # The thread torque creates both axial force (via helix) and torsion.
        # R_t = tau_component / (sigma_total) characterizes how much of the
        # tightening effort went into torsion vs axial loading.
        T_total = self.compute_tightening_torque()
        T_pitch = F_V * self.thread.pitch / (2 * np.pi)

        if T_total > 1e-10:
            R_t = 1.0 - T_pitch / T_total  # Fraction of torque that is friction
        else:
            R_t = 0.0

        # Preload loss from torsion relaxation
        # When torsion relaxes, the bolt "unwinds" slightly:
        #   delta_theta = delta_tau * L / (G * d_s)
        #   delta_F = k_bolt * (p/2pi) * delta_theta
        # Simplified: proportional to tau reduction and R_t
        if tau_initial > 0:
            delta_tau_ratio = (tau_initial - tau_final) / tau_initial
        else:
            delta_tau_ratio = 0.0

        preload_loss = F_V * R_t * delta_tau_ratio
        preload_loss = max(preload_loss, 0.0)

        F_effective = max(F_V - preload_loss, 0.0)

        # Von Mises stresses
        vm_initial = np.sqrt(sigma_axial ** 2 + 3.0 * tau_initial ** 2)
        # After relaxation, axial stress also decreases due to preload loss
        sigma_axial_final = F_effective / p.bolt_stress_area if p.bolt_stress_area > 0 else 0.0
        vm_final = np.sqrt(sigma_axial_final ** 2 + 3.0 * tau_final ** 2)

        return {
            'tau_initial_MPa': tau_initial * 1e-6,
            'tau_final_MPa': tau_final * 1e-6,
            'tau_reduction_pct': tau_relaxed_fraction * 100.0,
            'preload_loss_N': preload_loss,
            'preload_loss_pct': (preload_loss / F_V * 100.0) if F_V > 0 else 0.0,
            'F_effective': F_effective,
            'von_mises_initial_MPa': vm_initial * 1e-6,
            'von_mises_final_MPa': vm_final * 1e-6,
            'time_hours': time_hours,
            'relaxation_progress_pct': relaxation_progress * 100.0,
            'torsional_contribution_ratio': R_t,
        }

    def get_effective_preload(self, time_hours: float = 24.0) -> float:
        """
        Get effective preload after short-term torsional relaxation.

        This is the preload available for resisting loosening, accounting
        for the initial relaxation that occurs in the first hours/days
        after tightening.

        For tension-controlled tightening, there is no relaxation loss
        (no residual torsion to relax).

        Args:
            time_hours: Time after tightening [hours]. Default 24h.

        Returns:
            Effective preload [N]
        """
        result = self.compute_torsion_relaxation(time_hours)
        return result['F_effective']

    def compute_preload_scatter(self) -> Dict[str, float]:
        """
        Compute preload scatter based on tightening method.

        Different tightening methods produce different levels of
        preload uncertainty. This method returns the expected
        min/nominal/max preload for the given method.

        Scatter values (VDI 2230):
        - Torque-controlled:  alpha_A = 1.4-1.8 (up to +/-30% scatter)
        - Angle-controlled:   alpha_A = 1.2-1.4 (up to +/-15% scatter)
        - Yield-controlled:   alpha_A = 1.1-1.2 (up to +/-10% scatter)
        - Tension-controlled: alpha_A = 1.0-1.1 (up to +/-5% scatter)

        where alpha_A = F_max / F_min (tightening factor).

        Returns:
            Dictionary with:
            - 'F_nominal': Nominal (target) preload [N]
            - 'F_min': Minimum expected preload [N]
            - 'F_max': Maximum expected preload [N]
            - 'alpha_A': Tightening factor
            - 'scatter_pct': Scatter as percentage (+/-)
            - 'method': Tightening method name
        """
        F_nom = self.params.target_preload
        method = self.params.method

        # Tightening factor alpha_A per VDI 2230
        alpha_A_map = {
            TighteningMethod.TORQUE_CONTROLLED: 1.6,
            TighteningMethod.ANGLE_CONTROLLED: 1.3,
            TighteningMethod.YIELD_CONTROLLED: 1.15,
            TighteningMethod.TENSION_CONTROLLED: 1.05,
        }
        alpha_A = alpha_A_map.get(method, 1.6)

        # Friction variation also affects scatter for torque-controlled
        if method == TighteningMethod.TORQUE_CONTROLLED:
            mu_t = self.params.mu_thread
            # Higher friction uncertainty increases scatter
            if mu_t > 0.2:
                alpha_A *= 1.1  # Dry joints have more scatter
            elif mu_t < 0.08:
                alpha_A *= 0.95  # Well-lubricated joints have less scatter

        # Compute min/max from alpha_A
        # alpha_A = F_max / F_min, nominal is geometric mean
        # F_nom = sqrt(F_max * F_min)
        # F_max = F_nom * sqrt(alpha_A)
        # F_min = F_nom / sqrt(alpha_A)
        sqrt_alpha = np.sqrt(alpha_A)
        F_max = F_nom * sqrt_alpha
        F_min = F_nom / sqrt_alpha

        scatter_pct = (sqrt_alpha - 1.0) * 100.0

        return {
            'F_nominal': F_nom,
            'F_min': F_min,
            'F_max': F_max,
            'alpha_A': alpha_A,
            'scatter_pct': scatter_pct,
            'method': method.value,
        }

    def get_summary(self) -> Dict[str, float]:
        """
        Get comprehensive summary of tightening process effects.

        Returns:
            Dictionary with all tightening process quantities.
        """
        T_A = self.compute_tightening_torque()
        tau_res = self.compute_residual_torsion()
        sigma_a = self.compute_axial_stress()
        sigma_vm = self.compute_von_mises_stress()
        relaxation_24h = self.compute_torsion_relaxation(time_hours=24.0)
        scatter = self.compute_preload_scatter()

        return {
            'method': self.params.method.value,
            'target_preload_N': self.params.target_preload,
            'tightening_torque_Nm': T_A,
            'axial_stress_MPa': sigma_a * 1e-6,
            'residual_torsion_MPa': tau_res * 1e-6,
            'von_mises_stress_MPa': sigma_vm * 1e-6,
            'yield_utilization': sigma_vm / self.params.bolt_yield_strength
                if self.params.bolt_yield_strength > 0 else 0.0,
            'preload_after_24h_N': relaxation_24h['F_effective'],
            'preload_loss_24h_pct': relaxation_24h['preload_loss_pct'],
            'scatter_alpha_A': scatter['alpha_A'],
            'scatter_F_min_N': scatter['F_min'],
            'scatter_F_max_N': scatter['F_max'],
            'scatter_pct': scatter['scatter_pct'],
        }
