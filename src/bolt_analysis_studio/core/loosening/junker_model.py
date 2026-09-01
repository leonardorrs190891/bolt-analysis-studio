"""
Comprehensive Junker Loosening Mechanism Models for Bolt Analysis.

This module implements multiple bolt loosening models based on experimental research:
1. Junker (1969) - Classic transverse vibration loosening mechanism
2. Pai & Hess (2002) - Four-regime slip classification with graduated loosening
3. Jiang et al. (2003) - Two-stage model (non-rotational + rotational)
4. Nassar & Housari (2007) - Integral formulation with slip history tracking

Key Concepts:
- LOOSENING CRITERION: T_pitch > T_thread + T_bearing
- SLIP REGIMES: NO_SLIP → HEAD_ONLY → NUT_ONLY → COMPLETE_SLIP
- PRELOAD LOSS: ΔF_p = k_bolt × (p/2π) × θ_loosening
- CYCLE-DEPENDENT DEGRADATION: Friction and resistance decrease with cycles

References:
[1] Junker, G.H. (1969). "New criteria for self-loosening of fasteners under vibration."
    SAE Technical Paper 690055.
[2] Pai, N.G., Hess, D.P. (2002). "Three-dimensional finite element analysis of
    threaded fastener loosening due to dynamic shear load." Engineering Failure
    Analysis 9(4):383-402.
[3] Jiang, Y., et al. (2003). "A study of early stage self-loosening of bolted joints."
    Journal of Mechanical Design 125:518-526.
[4] Nassar, S.A., Housari, B.A. (2007). "Effect of thread pitch on the self-loosening
    of threaded fasteners." Journal of Pressure Vessel Technology 129:426-440.

Author: Bolt Analysis Studio Team
Version: 4.0
Date: January 2026
"""

from enum import Enum, auto
from dataclasses import dataclass, field
from typing import Optional, Tuple, Dict, Any, List, Callable
import numpy as np
import math


# =============================================================================
# ENUMERATIONS
# =============================================================================

class JunkerSlipRegime(Enum):
    """
    Slip regime classification per Pai & Hess (2002).

    Defines which interfaces are undergoing gross slip during vibration.
    Each regime has distinct loosening characteristics.
    """
    NO_SLIP = auto()            # All interfaces stuck - no loosening
    HEAD_ONLY = auto()          # Bolt head slipping on washer/flange - minor loosening
    NUT_ONLY = auto()           # Nut bearing slipping - moderate loosening
    COMPLETE_SLIP = auto()      # Both head and nut slipping - maximum loosening


class LooseningStage(Enum):
    """
    Two-stage loosening model classification (Jiang et al. 2003).

    STAGE 1: Non-rotational phase - embedding, plastic deformation
    STAGE 2: Rotational phase - screw-out loosening due to thread slip
    """
    NON_ROTATIONAL = auto()     # Stage 1: Local deformation, no rotation
    TRANSITION = auto()         # Critical transition point (~200 cycles)
    ROTATIONAL = auto()         # Stage 2: Active screw-out loosening


# =============================================================================
# DATACLASSES FOR CONTACT INTERFACES
# =============================================================================

@dataclass
class ThreadContactParams:
    """
    Thread interface parameters for loosening calculations.

    Attributes:
        pitch: Thread pitch [m]
        mean_radius: Thread pitch radius r_m = d₂/2 [m]
        flank_angle: Thread flank angle α [rad] (typically π/6 for metric)
        helix_angle: Thread helix angle λ = arctan(p/(π·d₂)) [rad]
        mu_thread: Thread friction coefficient μ_t
        effective_diameter: Effective thread diameter for stress [m]
    """
    pitch: float                    # p [m]
    mean_radius: float              # r_m = d₂/2 [m]
    flank_angle: float = np.pi/6    # α = 30° for ISO metric
    helix_angle: float = 0.0        # λ [rad] - auto-calculated
    mu_thread: float = 0.12         # μ_t
    effective_diameter: float = 0.0 # d_eff [m]

    def __post_init__(self):
        """Calculate helix angle from pitch and mean radius."""
        if self.helix_angle == 0.0:
            self.helix_angle = np.arctan(self.pitch / (2 * np.pi * self.mean_radius))
        if self.effective_diameter == 0.0:
            self.effective_diameter = 2 * self.mean_radius


@dataclass
class BearingContactParams:
    """
    Bearing interface parameters (head or nut on washer/flange).

    Attributes:
        inner_radius: Inner contact radius [m]
        outer_radius: Outer contact radius [m]
        effective_radius: Load-weighted effective radius [m]
        mu_bearing: Bearing friction coefficient μ_b
        contact_area: Annular contact area [m²]
    """
    inner_radius: float             # r_i [m]
    outer_radius: float             # r_o [m]
    effective_radius: float = 0.0   # r_eff [m] - auto-calculated
    mu_bearing: float = 0.15        # μ_b
    contact_area: float = 0.0       # A_contact [m²] - auto-calculated

    def __post_init__(self):
        """Calculate effective radius and contact area."""
        if self.effective_radius == 0.0:
            # Load-weighted effective radius for annular contact
            # r_eff = (2/3) × (r_o³ - r_i³) / (r_o² - r_i²)
            r_o, r_i = self.outer_radius, self.inner_radius
            if r_o > r_i:
                self.effective_radius = (2/3) * (r_o**3 - r_i**3) / (r_o**2 - r_i**2)
            else:
                self.effective_radius = r_o

        if self.contact_area == 0.0:
            self.contact_area = np.pi * (self.outer_radius**2 - self.inner_radius**2)


# =============================================================================
# JUNKER LOOSENING MODEL (CLASSIC)
# =============================================================================

class JunkerLooseningModel:
    """
    Classic Junker loosening mechanism (1969).

    MECHANISM:
    Under transverse vibration, relative slip between bearing surfaces causes
    the nut/bolt to rotate. Loosening occurs when the helix driving torque
    exceeds the resisting friction torques.

    GOVERNING EQUATIONS:

    1. Pitch torque (DRIVES loosening):
       T_pitch = F_p × r_m × tan(λ)
       where λ = helix angle, r_m = pitch radius

    2. Thread friction torque (RESISTS loosening):
       T_thread = μ_t × F_p × (d₂/2) × sec(α)
       where α = flank angle, d₂ = pitch diameter

    3. Bearing friction torques (RESIST loosening):
       T_bearing_head = μ_b_head × F_p × r_eff_head
       T_bearing_nut = μ_b_nut × F_p × r_eff_nut

    4. LOOSENING CRITERION:
       Loosening occurs when: T_pitch > T_thread + T_bearing_total

    5. PRELOAD LOSS from rotation:
       ΔF_p = k_bolt × (p/2π) × θ_loosening

    USAGE:
        thread = ThreadContactParams(pitch=0.00175, mean_radius=0.00549)
        head = BearingContactParams(inner_radius=0.007, outer_radius=0.011)
        nut = BearingContactParams(inner_radius=0.007, outer_radius=0.011)

        model = JunkerLooseningModel(thread, head, nut)
        will_loosen, regime = model.check_loosening_criterion(F_trans=1000, F_preload=50000)

        if will_loosen:
            torques = model.compute_loosening_torques()
            dtheta = model.evaluate_loosening_step(dt=0.001)
    """

    def __init__(self,
                 thread_contact: ThreadContactParams,
                 bearing_head_contact: BearingContactParams,
                 bearing_nut_contact: BearingContactParams,
                 rotational_inertia_nut: float = 1e-4):
        """
        Initialize Junker loosening model.

        Args:
            thread_contact: Thread interface parameters
            bearing_head_contact: Bolt head bearing interface parameters
            bearing_nut_contact: Nut bearing interface parameters
            rotational_inertia_nut: Nut rotational inertia J_nut [kg·m²]
        """
        self.thread = thread_contact
        self.bearing_head = bearing_head_contact
        self.bearing_nut = bearing_nut_contact
        self.J_nut = rotational_inertia_nut

        # State variables
        self.current_regime = JunkerSlipRegime.NO_SLIP
        self.F_preload = 0.0
        self.F_transverse = 0.0
        self.theta_loosening = 0.0          # Cumulative loosening angle [rad]
        self.loosening_rate = 0.0           # Current dθ/dt [rad/s]
        self.cycles = 0

        # Torque components (cached)
        self.T_pitch = 0.0
        self.T_thread = 0.0
        self.T_bearing_head = 0.0
        self.T_bearing_nut = 0.0
        self.T_net = 0.0

    def check_loosening_criterion(self,
                                   F_transverse: float,
                                   F_preload: float) -> Tuple[bool, JunkerSlipRegime]:
        """
        Check if loosening criterion is satisfied.

        Evaluates the balance of torques to determine if the fastener will loosen.
        Also determines which slip regime is active.

        Args:
            F_transverse: Transverse (shear) force [N]
            F_preload: Current preload force [N]

        Returns:
            Tuple of (will_loosen: bool, slip_regime: JunkerSlipRegime)
        """
        self.F_preload = F_preload
        self.F_transverse = F_transverse

        # Compute all torque components
        torques = self.compute_loosening_torques()
        self.T_pitch = torques['T_pitch']
        self.T_thread = torques['T_thread']
        self.T_bearing_head = torques['T_bearing_head']
        self.T_bearing_nut = torques['T_bearing_nut']

        # Determine slip regime based on transverse force
        # Higher transverse force → more interfaces slip
        slip_ratio = F_transverse / F_preload if F_preload > 0 else 0

        # Threshold ratios (empirical - can be calibrated)
        slip_threshold_none = 0.05
        slip_threshold_head = 0.15
        slip_threshold_nut = 0.25

        if slip_ratio < slip_threshold_none:
            self.current_regime = JunkerSlipRegime.NO_SLIP
        elif slip_ratio < slip_threshold_head:
            self.current_regime = JunkerSlipRegime.HEAD_ONLY
        elif slip_ratio < slip_threshold_nut:
            self.current_regime = JunkerSlipRegime.NUT_ONLY
        else:
            self.current_regime = JunkerSlipRegime.COMPLETE_SLIP

        # Calculate net torque based on regime
        if self.current_regime == JunkerSlipRegime.NO_SLIP:
            self.T_net = 0.0
            return False, self.current_regime

        elif self.current_regime == JunkerSlipRegime.HEAD_ONLY:
            # Only head slipping - nut bearing still resists
            T_resist = self.T_thread + self.T_bearing_nut
            self.T_net = self.T_pitch - T_resist

        elif self.current_regime == JunkerSlipRegime.NUT_ONLY:
            # Only nut slipping - head bearing still resists
            T_resist = self.T_thread + self.T_bearing_head
            self.T_net = self.T_pitch - T_resist

        else:  # COMPLETE_SLIP
            # Both bearing surfaces slipping - only thread friction resists
            T_resist = self.T_thread
            self.T_net = self.T_pitch - T_resist

        will_loosen = self.T_net > 0

        return will_loosen, self.current_regime

    def compute_loosening_torques(self) -> Dict[str, float]:
        """
        Compute all torque components in the loosening mechanism.

        Returns:
            Dictionary with torque components [N·m]:
                - T_pitch: Helix driving torque (DRIVES loosening)
                - T_thread: Thread friction torque (RESISTS)
                - T_bearing_head: Head bearing friction torque (RESISTS)
                - T_bearing_nut: Nut bearing friction torque (RESISTS)
                - T_total_resist: Total resisting torque
                - T_net: Net loosening torque (T_pitch - T_total_resist)
        """
        F_p = self.F_preload

        # 1. PITCH TORQUE (drives loosening)
        # T_pitch = F_p × r_m × tan(λ)
        T_pitch = F_p * self.thread.mean_radius * np.tan(self.thread.helix_angle)

        # 2. THREAD FRICTION TORQUE (resists loosening)
        # T_thread = μ_t × F_p × r_m × sec(α)
        # sec(α) accounts for normal force component on thread flanks
        sec_alpha = 1.0 / np.cos(self.thread.flank_angle)
        T_thread = self.thread.mu_thread * F_p * self.thread.mean_radius * sec_alpha

        # 3. BEARING FRICTION TORQUES (resist loosening)
        # T_bearing = μ_b × F_p × r_eff
        T_bearing_head = self.bearing_head.mu_bearing * F_p * self.bearing_head.effective_radius
        T_bearing_nut = self.bearing_nut.mu_bearing * F_p * self.bearing_nut.effective_radius

        # Total resistance
        T_total_resist = T_thread + T_bearing_head + T_bearing_nut

        # Net torque
        T_net = T_pitch - T_total_resist

        return {
            'T_pitch': T_pitch,
            'T_thread': T_thread,
            'T_bearing_head': T_bearing_head,
            'T_bearing_nut': T_bearing_nut,
            'T_total_resist': T_total_resist,
            'T_net': T_net
        }

    def evaluate_loosening_step(self, dt: float) -> float:
        """
        Evaluate loosening angle increment for a time step.

        Uses simplified rotational dynamics:
        J × α = T_net  →  α = T_net / J
        θ(t + dt) = θ(t) + ω × dt + 0.5 × α × dt²

        Args:
            dt: Time step [s]

        Returns:
            Loosening angle increment dθ [rad]
        """
        if self.T_net <= 0:
            self.loosening_rate = 0.0
            return 0.0

        # Angular acceleration
        alpha = self.T_net / self.J_nut  # [rad/s²]

        # Update angular velocity (simple Euler)
        d_omega = alpha * dt

        # Update loosening rate
        self.loosening_rate += d_omega

        # Increment angle
        dtheta = self.loosening_rate * dt + 0.5 * alpha * dt**2
        self.theta_loosening += dtheta

        return dtheta

    def get_loosening_rate(self) -> float:
        """
        Get current loosening rate.

        Returns:
            Current dθ/dt [rad/s]
        """
        return self.loosening_rate

    def get_preload_loss(self, k_bolt: float) -> float:
        """
        Calculate preload loss from rotational loosening.

        ΔF_p = k_bolt × Δx
        where Δx = (p/2π) × θ_loosening

        Args:
            k_bolt: Bolt stiffness [N/m]

        Returns:
            Preload loss [N]
        """
        delta_x = (self.thread.pitch / (2 * np.pi)) * self.theta_loosening
        return k_bolt * delta_x

    def increment_cycle(self):
        """Increment cycle counter for degradation models."""
        self.cycles += 1

    def reset(self):
        """Reset loosening state."""
        self.theta_loosening = 0.0
        self.loosening_rate = 0.0
        self.cycles = 0
        self.current_regime = JunkerSlipRegime.NO_SLIP


# =============================================================================
# PAI & HESS EXTENSION (2002)
# =============================================================================

class PaiHessExtension(JunkerLooseningModel):
    """
    Extended Junker model with four slip regimes (Pai & Hess 2002).

    ENHANCEMENTS:
    - Regime-dependent loosening rates
    - Percentage of loosening per regime (0-100%)
    - Finite element calibrated slip thresholds
    - Progressive degradation with cycles

    SLIP REGIME LOOSENING PERCENTAGES (typical):
    - NO_SLIP: 0% loosening
    - HEAD_ONLY: 10-20% of maximum loosening rate
    - NUT_ONLY: 30-50% of maximum loosening rate
    - COMPLETE_SLIP: 100% maximum loosening rate

    References:
    Pai, N.G., Hess, D.P. (2002). "Three-dimensional finite element analysis
    of threaded fastener loosening due to dynamic shear load."
    Engineering Failure Analysis 9(4):383-402.
    """

    def __init__(self,
                 thread_contact: ThreadContactParams,
                 bearing_head_contact: BearingContactParams,
                 bearing_nut_contact: BearingContactParams,
                 rotational_inertia_nut: float = 1e-4,
                 regime_loosening_factors: Optional[Dict[JunkerSlipRegime, float]] = None):
        """
        Initialize Pai-Hess extended model.

        Args:
            thread_contact: Thread interface parameters
            bearing_head_contact: Bolt head bearing interface parameters
            bearing_nut_contact: Nut bearing interface parameters
            rotational_inertia_nut: Nut rotational inertia [kg·m²]
            regime_loosening_factors: Dict mapping regime to loosening percentage (0-1)
        """
        super().__init__(thread_contact, bearing_head_contact, bearing_nut_contact,
                        rotational_inertia_nut)

        # Default loosening factors per regime
        if regime_loosening_factors is None:
            self.regime_factors = {
                JunkerSlipRegime.NO_SLIP: 0.0,
                JunkerSlipRegime.HEAD_ONLY: 0.15,
                JunkerSlipRegime.NUT_ONLY: 0.40,
                JunkerSlipRegime.COMPLETE_SLIP: 1.0
            }
        else:
            self.regime_factors = regime_loosening_factors

    def evaluate_loosening_step(self, dt: float) -> float:
        """
        Evaluate loosening with regime-dependent factor.

        Applies loosening percentage based on current slip regime.

        Args:
            dt: Time step [s]

        Returns:
            Loosening angle increment dθ [rad]
        """
        # Get base loosening increment from parent class
        dtheta_base = super().evaluate_loosening_step(dt)

        # Apply regime-dependent factor
        factor = self.regime_factors.get(self.current_regime, 0.0)
        dtheta_actual = dtheta_base * factor

        # Adjust accumulated loosening
        self.theta_loosening = self.theta_loosening - dtheta_base + dtheta_actual

        return dtheta_actual

    def get_regime_loosening_percentage(self) -> float:
        """
        Get current regime loosening percentage.

        Returns:
            Loosening percentage (0-100%)
        """
        return self.regime_factors.get(self.current_regime, 0.0) * 100


# =============================================================================
# JIANG TWO-STAGE MODEL (2003)
# =============================================================================

class JiangTwoStageModel:
    """
    Two-stage bolt loosening model (Jiang et al. 2003).

    STAGE 1: NON-ROTATIONAL LOOSENING (Cycles 1 to N_trans, typically ~200)
    - Mechanism: Embedding, plastic deformation, wear
    - Preload decay: F_p = F_p0 × exp(-λ₁ × N)
    - No rotation of nut/bolt
    - Rapid initial preload loss (30-50% in first 100 cycles)

    STAGE 2: ROTATIONAL LOOSENING (Cycles > N_trans)
    - Mechanism: Screw-out loosening (Junker mechanism)
    - Preload decay: F_p = F_trans × exp(-λ₂ × (N - N_trans))
    - Active rotation with θ_loosening accumulation
    - Slower but continuous preload loss

    TRANSITION POINT:
    - Occurs at N_trans ≈ 200 cycles (material/geometry dependent)
    - Triggered when F_p drops to ~60-70% of F_p0
    - Or when nut rotation first exceeds threshold (e.g., 0.5°)

    References:
    Jiang, Y., Zhang, M., Lee, C.H. (2003). "A study of early stage
    self-loosening of bolted joints." Journal of Mechanical Design 125:518-526.
    """

    def __init__(self,
                 F_preload_initial: float,
                 lambda_stage1: float = 0.015,
                 lambda_stage2: float = 0.005,
                 N_transition: int = 200,
                 F_transition_ratio: float = 0.65):
        """
        Initialize two-stage model.

        Args:
            F_preload_initial: Initial preload F_p0 [N]
            lambda_stage1: Stage 1 decay constant λ₁ [1/cycle]
            lambda_stage2: Stage 2 decay constant λ₂ [1/cycle]
            N_transition: Transition cycle count N_trans
            F_transition_ratio: Preload ratio at transition (F_trans/F_p0)
        """
        self.F_p0 = F_preload_initial
        self.lambda1 = lambda_stage1
        self.lambda2 = lambda_stage2
        self.N_trans = N_transition
        self.F_trans_ratio = F_transition_ratio
        self.F_trans = F_preload_initial * F_transition_ratio

        # State
        self.current_stage = LooseningStage.NON_ROTATIONAL
        self.N_cycles = 0
        self.F_preload_current = F_preload_initial
        self.theta_loosening = 0.0

        # Tracking
        self.stage1_loss = 0.0
        self.stage2_loss = 0.0

    def compute_stage1_loss(self, N: int) -> float:
        """
        Compute preload loss in Stage 1 (non-rotational).

        F_p(N) = F_p0 × exp(-λ₁ × N)

        Args:
            N: Number of cycles

        Returns:
            Current preload F_p [N]
        """
        if N <= 0:
            return self.F_p0

        F_p = self.F_p0 * np.exp(-self.lambda1 * N)
        return F_p

    def compute_stage2_loss(self, N: int) -> float:
        """
        Compute preload loss in Stage 2 (rotational).

        F_p(N) = F_trans × exp(-λ₂ × (N - N_trans))

        Args:
            N: Number of cycles (must be > N_trans)

        Returns:
            Current preload F_p [N]
        """
        if N <= self.N_trans:
            return self.F_trans

        N_stage2 = N - self.N_trans
        F_p = self.F_trans * np.exp(-self.lambda2 * N_stage2)
        return F_p

    def detect_transition(self) -> bool:
        """
        Detect if transition from Stage 1 to Stage 2 has occurred.

        Transition criteria:
        1. Cycle count reaches N_trans
        2. Preload drops below transition threshold

        Returns:
            True if transition detected
        """
        if self.current_stage == LooseningStage.ROTATIONAL:
            return True

        # Check cycle count
        if self.N_cycles >= self.N_trans:
            self.current_stage = LooseningStage.TRANSITION
            return True

        # Check preload threshold
        if self.F_preload_current <= self.F_trans:
            self.current_stage = LooseningStage.TRANSITION
            return True

        return False

    def update_preload(self, N_cycles: int) -> float:
        """
        Update preload based on current cycle count.

        Args:
            N_cycles: Current cycle number

        Returns:
            Current preload F_p [N]
        """
        self.N_cycles = N_cycles

        # Detect transition
        if self.detect_transition():
            # Stage 2: Rotational loosening
            if self.current_stage == LooseningStage.TRANSITION:
                self.current_stage = LooseningStage.ROTATIONAL

            self.F_preload_current = self.compute_stage2_loss(N_cycles)
            self.stage2_loss = self.F_trans - self.F_preload_current
        else:
            # Stage 1: Non-rotational loosening
            self.F_preload_current = self.compute_stage1_loss(N_cycles)
            self.stage1_loss = self.F_p0 - self.F_preload_current

        return self.F_preload_current

    def get_loss_breakdown(self) -> Dict[str, float]:
        """
        Get preload loss breakdown by stage.

        Returns:
            Dictionary with loss components [N]
        """
        total_loss = self.F_p0 - self.F_preload_current

        return {
            'stage1_loss': self.stage1_loss,
            'stage2_loss': self.stage2_loss,
            'total_loss': total_loss,
            'remaining_preload': self.F_preload_current,
            'loss_percentage': (total_loss / self.F_p0 * 100) if self.F_p0 > 0 else 0
        }


# =============================================================================
# NASSAR & HOUSARI MODEL (2007)
# =============================================================================

class NassarHousariModel:
    """
    Integral formulation of bolt loosening with slip history (Nassar & Housari 2007).

    APPROACH:
    Uses integral formulation to track cumulative effect of slip over full loading cycle:

    θ_loosening(N) = ∫[0 to T] (T_net(t) / J) dt

    where T_net varies throughout each vibration cycle.

    FEATURES:
    - Tracks slip history over complete vibration cycle
    - Accounts for partial slip phases
    - Pitch effect: Coarse pitch → faster loosening
    - More accurate for non-sinusoidal loading

    References:
    Nassar, S.A., Housari, B.A. (2007). "Effect of thread pitch on the
    self-loosening of threaded fasteners." Journal of Pressure Vessel
    Technology 129:426-440.
    """

    def __init__(self,
                 thread_contact: ThreadContactParams,
                 bearing_head_contact: BearingContactParams,
                 bearing_nut_contact: BearingContactParams,
                 rotational_inertia_nut: float = 1e-4,
                 loading_function: Optional[Callable[[float], float]] = None):
        """
        Initialize Nassar-Housari integral model.

        Args:
            thread_contact: Thread interface parameters
            bearing_head_contact: Bolt head bearing interface parameters
            bearing_nut_contact: Nut bearing interface parameters
            rotational_inertia_nut: Nut rotational inertia [kg·m²]
            loading_function: F_transverse(t) function, default sinusoidal
        """
        self.thread = thread_contact
        self.bearing_head = bearing_head_contact
        self.bearing_nut = bearing_nut_contact
        self.J_nut = rotational_inertia_nut

        # Loading function F_trans(t)
        if loading_function is None:
            # Default: F_trans(t) = F_amp × sin(2π × f × t)
            self.loading_func = lambda t: 1000 * np.sin(2 * np.pi * 25 * t)
        else:
            self.loading_func = loading_function

        # State
        self.theta_loosening = 0.0
        self.slip_history: List[Tuple[float, float]] = []  # (time, slip_distance)
        self.F_preload = 0.0
        self.cycles = 0

    def evaluate_cycle_integral(self,
                                 F_preload: float,
                                 cycle_period: float,
                                 n_samples: int = 100) -> float:
        """
        Evaluate loosening over one complete cycle using integral formulation.

        θ_cycle = ∫[0 to T] (T_net(t) / J) dt

        Numerically integrated using trapezoidal rule.

        Args:
            F_preload: Current preload [N]
            cycle_period: Period of one cycle T [s]
            n_samples: Number of integration points

        Returns:
            Loosening angle increment over one cycle [rad]
        """
        self.F_preload = F_preload

        t_points = np.linspace(0, cycle_period, n_samples)
        theta_rate = np.zeros(n_samples)

        for i, t in enumerate(t_points):
            # Get transverse load at this instant
            F_trans_t = self.loading_func(t)

            # Compute net torque
            T_net = self._compute_net_torque(F_trans_t, F_preload)

            # Angular acceleration
            if T_net > 0:
                theta_rate[i] = T_net / self.J_nut
            else:
                theta_rate[i] = 0.0

        # Integrate using trapezoidal rule
        dtheta_cycle = np.trapz(theta_rate, t_points)

        self.theta_loosening += dtheta_cycle
        self.cycles += 1

        return dtheta_cycle

    def _compute_net_torque(self, F_transverse: float, F_preload: float) -> float:
        """
        Compute net loosening torque at an instant.

        T_net = T_pitch - T_thread - T_bearing(F_trans)

        Args:
            F_transverse: Instantaneous transverse force [N]
            F_preload: Current preload [N]

        Returns:
            Net torque [N·m]
        """
        # Pitch torque (drives loosening)
        T_pitch = F_preload * self.thread.mean_radius * np.tan(self.thread.helix_angle)

        # Thread friction (resists)
        sec_alpha = 1.0 / np.cos(self.thread.flank_angle)
        T_thread = self.thread.mu_thread * F_preload * self.thread.mean_radius * sec_alpha

        # Bearing friction (depends on whether slip occurs)
        # Simplified: bearing resistance reduced when F_trans is high
        slip_factor = min(1.0, F_transverse / (0.5 * F_preload)) if F_preload > 0 else 0

        T_bearing_head = self.bearing_head.mu_bearing * F_preload * \
                        self.bearing_head.effective_radius * (1 - slip_factor)
        T_bearing_nut = self.bearing_nut.mu_bearing * F_preload * \
                       self.bearing_nut.effective_radius * (1 - slip_factor)

        T_net = T_pitch - T_thread - T_bearing_head - T_bearing_nut

        return T_net

    def get_preload_loss(self, k_bolt: float) -> float:
        """
        Calculate preload loss from accumulated loosening.

        Args:
            k_bolt: Bolt stiffness [N/m]

        Returns:
            Preload loss [N]
        """
        delta_x = (self.thread.pitch / (2 * np.pi)) * self.theta_loosening
        return k_bolt * delta_x


# =============================================================================
# FACTORY FUNCTIONS
# =============================================================================

def create_standard_junker_model(bolt_size: str,
                                  mu_thread: float = 0.12,
                                  mu_bearing: float = 0.15) -> JunkerLooseningModel:
    """
    Create Junker model for standard bolt sizes.

    Args:
        bolt_size: Standard designation (e.g., "M12", "M20", "M24")
        mu_thread: Thread friction coefficient
        mu_bearing: Bearing friction coefficient

    Returns:
        JunkerLooseningModel instance
    """
    # Standard thread parameters (ISO metric)
    thread_params = {
        'M12': (0.00175, 0.01098/2),  # (pitch, pitch_radius)
        'M16': (0.002, 0.01480/2),
        'M20': (0.0025, 0.01854/2),
        'M24': (0.003, 0.02227/2),
        'M30': (0.0035, 0.02773/2),
    }

    pitch, r_m = thread_params.get(bolt_size, (0.00175, 0.00549))

    thread = ThreadContactParams(
        pitch=pitch,
        mean_radius=r_m,
        mu_thread=mu_thread
    )

    # Standard bearing dimensions (washer under head and nut)
    d_nominal = float(bolt_size[1:]) / 1000  # Convert mm to m
    bearing_head = BearingContactParams(
        inner_radius=d_nominal * 0.55,
        outer_radius=d_nominal * 0.95,
        mu_bearing=mu_bearing
    )

    bearing_nut = BearingContactParams(
        inner_radius=d_nominal * 0.55,
        outer_radius=d_nominal * 0.95,
        mu_bearing=mu_bearing
    )

    return JunkerLooseningModel(thread, bearing_head, bearing_nut)


# =============================================================================
# MODULE TESTING
# =============================================================================

if __name__ == "__main__":
    print("="*80)
    print("JUNKER LOOSENING MODEL - TEST SUITE")
    print("="*80)

    # Test 1: Basic Junker Model
    print("\n[Test 1] Basic Junker Model - M20 Bolt")
    model = create_standard_junker_model("M20", mu_thread=0.12, mu_bearing=0.15)

    F_preload = 100000  # 100 kN
    F_transverse = 15000  # 15 kN

    will_loosen, regime = model.check_loosening_criterion(F_transverse, F_preload)
    print(f"  Preload: {F_preload/1000:.1f} kN")
    print(f"  Transverse: {F_transverse/1000:.1f} kN")
    print(f"  Will loosen: {will_loosen}")
    print(f"  Slip regime: {regime.name}")

    torques = model.compute_loosening_torques()
    print(f"  T_pitch (drives): {torques['T_pitch']:.3f} N·m")
    print(f"  T_thread (resists): {torques['T_thread']:.3f} N·m")
    print(f"  T_bearing_total (resists): {torques['T_bearing_head'] + torques['T_bearing_nut']:.3f} N·m")
    print(f"  T_net: {torques['T_net']:.3f} N·m")

    # Test 2: Loosening over time
    print("\n[Test 2] Loosening Evolution - 100 steps")
    dt = 0.001  # 1 ms time steps
    k_bolt = 2e9  # 2 GN/m

    for i in range(100):
        dtheta = model.evaluate_loosening_step(dt)
        model.increment_cycle()

    print(f"  Total loosening: {np.degrees(model.theta_loosening):.4f}°")
    print(f"  Preload loss: {model.get_preload_loss(k_bolt)/1000:.2f} kN")
    print(f"  Loosening rate: {model.get_loosening_rate():.3e} rad/s")

    # Test 3: Jiang Two-Stage Model
    print("\n[Test 3] Jiang Two-Stage Model")
    jiang = JiangTwoStageModel(F_preload_initial=100000, N_transition=200)

    stages = [50, 150, 250, 500, 1000]
    for N in stages:
        F_p = jiang.update_preload(N)
        breakdown = jiang.get_loss_breakdown()
        print(f"  N={N:4d}: F_p={F_p/1000:5.1f} kN, Loss={breakdown['loss_percentage']:5.1f}%, Stage={jiang.current_stage.name}")

    print("\n" + "="*80)
    print("ALL TESTS COMPLETED")
    print("="*80)
