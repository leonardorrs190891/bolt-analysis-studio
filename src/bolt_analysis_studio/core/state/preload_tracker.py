"""
Comprehensive Preload Loss Tracking System for Bolt Analysis.

This module implements a complete preload tracking system that monitors and accumulates
all mechanisms of preload loss in bolted joints:

1. ROTATIONAL LOOSENING (Junker mechanism) - ΔF = k × (p/2π) × θ
2. EMBEDDING LOSS (Surface settling) - ΔF = k × f_z × L_K × (1-e^(-N/N_c))
3. WEAR LOSS (Archard/fretting) - ΔF = k × Σh_wear
4. CREEP LOSS (Viscoelastic) - ΔF = k × δ₀ × C_r × log(t)
5. RELAXATION LOSS (Stress relaxation) - ΔF = F_p0 × (1-e^(-t/τ))
6. THERMAL LOSS (Differential expansion) - ΔF = k × Δα × ΔT × L
7. ELASTIC INTERACTION (External loads) - ΔF = Φ × F_ext

Key Features:
- Mechanism-specific tracking with individual loss rates
- Cumulative preload calculation
- Loss breakdown and percentage contribution
- State update manager for integration with time solver
- Cycle detection for fatigue/loosening analysis
- VDI 2230 compliance for embedding calculations

References:
[1] VDI 2230 Part 1 (2015). "Systematic calculation of highly stressed bolted joints."
[2] Bickford, J.H. (2008). "Introduction to the Design and Behavior of Bolted Joints."
[3] Shigley, J.E. (2020). "Mechanical Engineering Design."

Author: Bolt Analysis Studio Team
Version: 4.0
Date: January 2026
"""

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Dict, List, Optional, Tuple, Any, Callable
import numpy as np
import math


# =============================================================================
# ENUMERATIONS
# =============================================================================

class LossMechanismType(Enum):
    """Types of preload loss mechanisms."""
    ROTATIONAL = "rotational"           # Junker loosening
    EMBEDDING = "embedding"             # Surface settling
    WEAR = "wear"                       # Archard/fretting wear
    CREEP = "creep"                     # Viscoelastic deformation
    RELAXATION = "relaxation"           # Stress relaxation
    THERMAL = "thermal"                 # Thermal expansion mismatch
    ELASTIC_INTERACTION = "elastic"     # External load effects
    OTHER = "other"                     # User-defined


# =============================================================================
# DATACLASSES
# =============================================================================

@dataclass
class PreloadLossMechanism:
    """
    Data structure for a single preload loss mechanism.

    Tracks the accumulated loss, rate of loss, and contribution percentage
    for one specific mechanism.

    Attributes:
        mechanism_name: Name/type of loss mechanism
        loss_amount: Current accumulated loss [N]
        loss_rate: Current rate of loss [N/s] or [N/cycle]
        accumulated_loss: Total historical loss [N]
        percentage: Contribution percentage to total loss
        active: Whether this mechanism is currently active
    """
    mechanism_name: str
    mechanism_type: LossMechanismType
    loss_amount: float = 0.0            # Current loss [N]
    loss_rate: float = 0.0              # Current rate [N/s or N/cycle]
    accumulated_loss: float = 0.0       # Total historical loss [N]
    percentage: float = 0.0             # % contribution
    active: bool = True                 # Active flag
    metadata: Dict[str, Any] = field(default_factory=dict)

    def add_loss(self, delta_loss: float):
        """Add loss increment."""
        self.loss_amount += delta_loss
        self.accumulated_loss += delta_loss

    def reset_current_loss(self):
        """Reset current loss (keeps accumulated)."""
        self.loss_amount = 0.0
        self.loss_rate = 0.0


# =============================================================================
# PRELOAD TRACKER
# =============================================================================

class PreloadTracker:
    """
    Complete preload loss tracking system.

    Monitors all preload loss mechanisms and maintains current preload state.
    Provides breakdown analysis and percentage contributions.

    USAGE:
        tracker = PreloadTracker(k_bolt=2e9, k_member=5e9, F_preload_initial=100000)

        # Add losses
        tracker.add_rotational_loss(theta_loosening=0.01)
        tracker.add_embedding_loss(N_cycles=100, f_z=5e-6, L_K=0.05)
        tracker.add_wear_loss(wear_depth=1e-6)

        # Update state
        tracker.update_preload(dt=0.001)

        # Get results
        F_current = tracker.get_current_preload()
        breakdown = tracker.get_loss_breakdown()
        percentages = tracker.get_loss_percentages()
    """

    def __init__(self,
                 k_bolt: float,
                 k_member: float,
                 F_preload_initial: float,
                 enable_all_mechanisms: bool = True):
        """
        Initialize preload tracker.

        Args:
            k_bolt: Bolt stiffness [N/m]
            k_member: Member (clamped parts) stiffness [N/m]
            F_preload_initial: Initial preload F_p0 [N]
            enable_all_mechanisms: Enable all loss mechanisms by default
        """
        self.k_bolt = k_bolt
        self.k_member = k_member
        self.k_joint = compute_system_stiffness(k_bolt, k_member)
        self.F_p0 = F_preload_initial
        self.F_p_current = F_preload_initial

        # Loss mechanisms registry
        self.mechanisms: Dict[str, PreloadLossMechanism] = {}

        if enable_all_mechanisms:
            self._initialize_all_mechanisms()

        # State tracking
        self.time = 0.0
        self.cycles = 0
        self.total_loss = 0.0

        # History (optional - for plotting)
        self.history_time: List[float] = []
        self.history_preload: List[float] = []
        self.enable_history = False

    def _initialize_all_mechanisms(self):
        """Initialize all standard loss mechanisms."""
        mechanisms = [
            ("rotational_loosening", LossMechanismType.ROTATIONAL),
            ("embedding", LossMechanismType.EMBEDDING),
            ("wear", LossMechanismType.WEAR),
            ("creep", LossMechanismType.CREEP),
            ("relaxation", LossMechanismType.RELAXATION),
            ("thermal", LossMechanismType.THERMAL),
            ("elastic_interaction", LossMechanismType.ELASTIC_INTERACTION),
        ]

        for name, mech_type in mechanisms:
            self.mechanisms[name] = PreloadLossMechanism(
                mechanism_name=name,
                mechanism_type=mech_type,
                active=True
            )

    def add_rotational_loss(self, theta_loosening: float):
        """
        Add preload loss from rotational loosening (Junker mechanism).

        ΔF = k_bolt × (p/2π) × θ_loosening

        Args:
            theta_loosening: Loosening angle increment [rad]
        """
        if "rotational_loosening" not in self.mechanisms:
            self.mechanisms["rotational_loosening"] = PreloadLossMechanism(
                mechanism_name="rotational_loosening",
                mechanism_type=LossMechanismType.ROTATIONAL
            )

        mechanism = self.mechanisms["rotational_loosening"]

        if not mechanism.active:
            return

        # Get pitch from metadata (must be set externally)
        pitch = mechanism.metadata.get("pitch", 0.00175)  # Default M12 pitch

        # Calculate axial displacement from rotation
        delta_axial = (pitch / (2 * np.pi)) * theta_loosening

        # Calculate preload loss
        delta_F = self.k_bolt * delta_axial

        mechanism.add_loss(delta_F)
        mechanism.loss_rate = delta_F  # Per increment

    def add_embedding_loss(self, N: int, f_z: float, L_K: float):
        """
        Add preload loss from embedding (surface settling) per VDI 2230.

        EMBEDDING MODEL (VDI 2230):
        ΔF = k_joint × f_z × L_K × (1 - exp(-N / N_c))

        where:
        - f_z: Embedding factor [m] (typically 3-10 μm for steel)
        - L_K: Embedding length [m] (grip length)
        - N_c: Characteristic cycle count (typically 50-100)

        Args:
            N: Current cycle count
            f_z: Embedding factor [m]
            L_K: Embedding length [m]
        """
        if "embedding" not in self.mechanisms:
            self.mechanisms["embedding"] = PreloadLossMechanism(
                mechanism_name="embedding",
                mechanism_type=LossMechanismType.EMBEDDING
            )

        mechanism = self.mechanisms["embedding"]

        if not mechanism.active:
            return

        # Characteristic cycle count (material dependent)
        N_c = mechanism.metadata.get("N_characteristic", 75)

        # Embedding displacement (asymptotic with cycles)
        delta_embed = f_z * L_K * (1 - np.exp(-N / N_c))

        # Total embedding loss
        delta_F_total = self.k_joint * delta_embed

        # Incremental loss since last update
        previous_loss = mechanism.loss_amount
        delta_F_increment = delta_F_total - previous_loss

        if delta_F_increment > 0:
            mechanism.add_loss(delta_F_increment)
            mechanism.loss_rate = delta_F_increment

    def add_wear_loss(self, wear_depth: float):
        """
        Add preload loss from wear (Archard/fretting).

        ΔF = k_joint × Σh_wear

        Args:
            wear_depth: Cumulative wear depth [m]
        """
        if "wear" not in self.mechanisms:
            self.mechanisms["wear"] = PreloadLossMechanism(
                mechanism_name="wear",
                mechanism_type=LossMechanismType.WEAR
            )

        mechanism = self.mechanisms["wear"]

        if not mechanism.active:
            return

        # Calculate loss from wear depth
        delta_F_total = self.k_joint * wear_depth

        # Incremental loss
        previous_loss = mechanism.loss_amount
        delta_F_increment = delta_F_total - previous_loss

        if delta_F_increment > 0:
            mechanism.add_loss(delta_F_increment)
            mechanism.loss_rate = delta_F_increment

    def add_creep_loss(self, time: float, C_r: float, delta_0: float):
        """
        Add preload loss from creep (viscoelastic deformation).

        CREEP MODEL (Logarithmic):
        ΔF = k_joint × δ₀ × C_r × log(1 + t/t₀)

        where:
        - δ₀: Initial deformation [m]
        - C_r: Creep coefficient (material dependent, typically 0.01-0.1)
        - t₀: Reference time (typically 1 second)

        Args:
            time: Current time [s]
            C_r: Creep coefficient [-]
            delta_0: Initial deformation [m]
        """
        if "creep" not in self.mechanisms:
            self.mechanisms["creep"] = PreloadLossMechanism(
                mechanism_name="creep",
                mechanism_type=LossMechanismType.CREEP
            )

        mechanism = self.mechanisms["creep"]

        if not mechanism.active or time <= 0:
            return

        t_0 = mechanism.metadata.get("t_reference", 1.0)

        # Creep displacement
        delta_creep = delta_0 * C_r * np.log(1 + time / t_0)

        # Total creep loss
        delta_F_total = self.k_joint * delta_creep

        # Incremental loss
        previous_loss = mechanism.loss_amount
        delta_F_increment = delta_F_total - previous_loss

        if delta_F_increment > 0:
            mechanism.add_loss(delta_F_increment)
            mechanism.loss_rate = delta_F_increment

    def add_relaxation_loss(self, time: float, tau: float):
        """
        Add preload loss from stress relaxation.

        RELAXATION MODEL (Exponential):
        ΔF = F_p0 × (1 - exp(-t/τ))

        where τ is the relaxation time constant (material dependent).

        Args:
            time: Current time [s]
            tau: Relaxation time constant [s]
        """
        if "relaxation" not in self.mechanisms:
            self.mechanisms["relaxation"] = PreloadLossMechanism(
                mechanism_name="relaxation",
                mechanism_type=LossMechanismType.RELAXATION
            )

        mechanism = self.mechanisms["relaxation"]

        if not mechanism.active or time <= 0 or tau <= 0:
            return

        # Relaxation loss (total, not incremental)
        delta_F_total = self.F_p0 * (1 - np.exp(-time / tau))

        # Incremental loss
        previous_loss = mechanism.loss_amount
        delta_F_increment = delta_F_total - previous_loss

        if delta_F_increment > 0:
            mechanism.add_loss(delta_F_increment)
            mechanism.loss_rate = delta_F_increment

    def add_thermal_loss(self, delta_T: float, alpha_bolt: float,
                        alpha_member: float, grip_length: float):
        """
        Add preload loss from thermal expansion mismatch.

        THERMAL MODEL:
        ΔF = k_joint × Δα × ΔT × L_grip

        where:
        - Δα = α_member - α_bolt
        - ΔT: Temperature change [K]
        - L_grip: Grip length [m]

        Args:
            delta_T: Temperature change from assembly [K]
            alpha_bolt: Bolt thermal expansion coefficient [1/K]
            alpha_member: Member thermal expansion coefficient [1/K]
            grip_length: Grip length [m]
        """
        if "thermal" not in self.mechanisms:
            self.mechanisms["thermal"] = PreloadLossMechanism(
                mechanism_name="thermal",
                mechanism_type=LossMechanismType.THERMAL
            )

        mechanism = self.mechanisms["thermal"]

        if not mechanism.active:
            return

        # Differential expansion
        delta_alpha = alpha_member - alpha_bolt
        delta_thermal = delta_alpha * delta_T * grip_length

        # Thermal loss (can be positive or negative)
        delta_F = self.k_joint * delta_thermal

        # Update mechanism (can decrease or increase preload)
        mechanism.loss_amount = delta_F
        mechanism.accumulated_loss += abs(delta_F)
        mechanism.loss_rate = delta_F

    def add_elastic_interaction_loss(self, F_external: float, phi: float = 0.1):
        """
        Add preload loss from elastic interaction with external load.

        ELASTIC INTERACTION:
        ΔF = Φ × F_external

        where Φ is the load factor (typically 0.1-0.2 for typical joints).

        Φ = k_bolt / (k_bolt + k_member)

        Args:
            F_external: External tensile force [N]
            phi: Load factor Φ [-] (auto-calculated if not provided)
        """
        if "elastic_interaction" not in self.mechanisms:
            self.mechanisms["elastic_interaction"] = PreloadLossMechanism(
                mechanism_name="elastic_interaction",
                mechanism_type=LossMechanismType.ELASTIC_INTERACTION
            )

        mechanism = self.mechanisms["elastic_interaction"]

        if not mechanism.active:
            return

        # Calculate load factor if not provided
        if phi is None:
            phi = self.k_bolt / (self.k_bolt + self.k_member)

        # Preload reduction
        delta_F = phi * F_external

        mechanism.loss_amount = delta_F
        mechanism.accumulated_loss += abs(delta_F)
        mechanism.loss_rate = delta_F

    def update_preload(self, dt: float):
        """
        Update current preload based on all active loss mechanisms.

        Args:
            dt: Time step [s]
        """
        # Calculate total current loss
        self.total_loss = sum(m.loss_amount for m in self.mechanisms.values() if m.active)

        # Update current preload
        self.F_p_current = self.F_p0 - self.total_loss

        # Ensure non-negative preload
        if self.F_p_current < 0:
            self.F_p_current = 0.0

        # Update time
        self.time += dt

        # Update history if enabled
        if self.enable_history:
            self.history_time.append(self.time)
            self.history_preload.append(self.F_p_current)

        # Update percentages
        self._update_percentages()

    def _update_percentages(self):
        """Calculate percentage contribution of each mechanism."""
        if self.total_loss == 0:
            for mechanism in self.mechanisms.values():
                mechanism.percentage = 0.0
            return

        for mechanism in self.mechanisms.values():
            if mechanism.active:
                mechanism.percentage = (mechanism.loss_amount / self.total_loss) * 100
            else:
                mechanism.percentage = 0.0

    def get_current_preload(self) -> float:
        """
        Get current preload force.

        Returns:
            Current preload F_p [N]
        """
        return self.F_p_current

    def get_total_loss(self) -> float:
        """
        Get total preload loss.

        Returns:
            Total loss ΔF_total [N]
        """
        return self.total_loss

    def get_loss_breakdown(self) -> Dict[str, float]:
        """
        Get breakdown of losses by mechanism.

        Returns:
            Dictionary mapping mechanism name to loss amount [N]
        """
        breakdown = {}
        for name, mechanism in self.mechanisms.items():
            if mechanism.active:
                breakdown[name] = mechanism.loss_amount
        return breakdown

    def get_loss_percentages(self) -> Dict[str, float]:
        """
        Get percentage contribution of each mechanism.

        Returns:
            Dictionary mapping mechanism name to percentage
        """
        percentages = {}
        for name, mechanism in self.mechanisms.items():
            if mechanism.active:
                percentages[name] = mechanism.percentage
        return percentages

    def get_mechanism(self, name: str) -> Optional[PreloadLossMechanism]:
        """Get specific mechanism by name."""
        return self.mechanisms.get(name)

    def set_mechanism_active(self, name: str, active: bool):
        """Enable or disable a specific mechanism."""
        if name in self.mechanisms:
            self.mechanisms[name].active = active

    def reset(self):
        """Reset all loss mechanisms and preload to initial state."""
        for mechanism in self.mechanisms.values():
            mechanism.loss_amount = 0.0
            mechanism.loss_rate = 0.0
            mechanism.accumulated_loss = 0.0
            mechanism.percentage = 0.0

        self.F_p_current = self.F_p0
        self.total_loss = 0.0
        self.time = 0.0
        self.cycles = 0

        if self.enable_history:
            self.history_time.clear()
            self.history_preload.clear()

    def get_state_summary(self) -> Dict[str, Any]:
        """
        Get comprehensive state summary.

        Returns:
            Dictionary with current state information
        """
        return {
            'time': self.time,
            'cycles': self.cycles,
            'F_preload_initial': self.F_p0,
            'F_preload_current': self.F_p_current,
            'total_loss': self.total_loss,
            'loss_percentage': (self.total_loss / self.F_p0 * 100) if self.F_p0 > 0 else 0,
            'k_bolt': self.k_bolt,
            'k_member': self.k_member,
            'k_joint': self.k_joint,
            'breakdown': self.get_loss_breakdown(),
            'percentages': self.get_loss_percentages(),
        }


# =============================================================================
# STATE UPDATE MANAGER
# =============================================================================

class StateUpdateManager:
    """
    Manages state updates for all contacts and preload tracking.

    Coordinates updates between:
    - Contact interfaces (threads, bearing surfaces)
    - Preload tracker
    - Loosening models
    - Cycle detection

    USAGE:
        manager = StateUpdateManager(contacts, thread_contact, preload_tracker, junker_model)

        # In time integration loop:
        for t, x, x_dot in time_steps:
            manager.update_all_states(x, x_dot, F_trans, dt, t)

            if manager.detect_cycle_completion(x, x_dot):
                manager.increment_cycle()
    """

    def __init__(self,
                 contacts: List[Any],
                 thread_contact: Optional[Any],
                 preload_tracker: PreloadTracker,
                 junker_model: Optional[Any] = None):
        """
        Initialize state update manager.

        Args:
            contacts: List of contact objects (bearing, gasket, etc.)
            thread_contact: Thread contact object (special handling)
            preload_tracker: Preload tracker instance
            junker_model: Junker loosening model instance (optional)
        """
        self.contacts = contacts
        self.thread_contact = thread_contact
        self.tracker = preload_tracker
        self.junker_model = junker_model

        # Cycle detection state
        self.previous_displacement = 0.0
        self.previous_velocity = 0.0
        self.zero_crossings = 0
        self.cycle_completed = False

        # Time tracking
        self.time = 0.0
        self.dt_accumulated = 0.0

    def update_all_states(self,
                         x: np.ndarray,
                         x_dot: np.ndarray,
                         F_transverse: float,
                         dt: float,
                         t: float):
        """
        Update all contact states and preload tracker.

        Args:
            x: Current displacement vector
            x_dot: Current velocity vector
            F_transverse: Current transverse force [N]
            dt: Time step [s]
            t: Current time [s]
        """
        self.time = t
        self.dt_accumulated += dt

        F_preload = self.tracker.get_current_preload()

        # Update all contact interfaces
        for contact in self.contacts:
            if hasattr(contact, 'update_state'):
                contact.update_state(x, x_dot, dt, F_preload)

        # Update thread contact (special handling for loosening)
        if self.thread_contact is not None:
            self.thread_contact.update_state(x, x_dot, dt, F_preload)

            # Get loosening angle if available
            if hasattr(self.thread_contact, 'theta_loosening'):
                theta = self.thread_contact.theta_loosening
                self.tracker.add_rotational_loss(theta)

        # Update Junker model if active
        if self.junker_model is not None:
            will_loosen, regime = self.junker_model.check_loosening_criterion(
                F_transverse, F_preload
            )

            if will_loosen:
                dtheta = self.junker_model.evaluate_loosening_step(dt)
                self.tracker.add_rotational_loss(dtheta)

        # Update wear losses
        total_wear_depth = 0.0
        for contact in self.contacts:
            if hasattr(contact, 'wear') and hasattr(contact.wear, 'wear_depth'):
                total_wear_depth += contact.wear.wear_depth

        if total_wear_depth > 0:
            self.tracker.add_wear_loss(total_wear_depth)

        # Update preload
        self.tracker.update_preload(dt)

    def detect_cycle_completion(self, x: np.ndarray, x_dot: np.ndarray) -> bool:
        """
        Detect cycle completion using zero-crossing detection.

        A cycle is completed when:
        1. Displacement crosses zero (x[i] × x_prev < 0)
        2. Velocity is in consistent direction

        Args:
            x: Current displacement vector
            x_dot: Current velocity vector

        Returns:
            True if cycle completed
        """
        if len(x) == 0:
            return False

        # Use first DOF for cycle detection (typically input DOF)
        current_disp = x[0]
        current_vel = x_dot[0]

        # Check for zero crossing
        if self.previous_displacement * current_disp < 0 and current_vel > 0:
            self.cycle_completed = True
            self.zero_crossings += 1
        else:
            self.cycle_completed = False

        # Update previous values
        self.previous_displacement = current_disp
        self.previous_velocity = current_vel

        return self.cycle_completed

    def increment_cycle(self):
        """Increment cycle counter in tracker and models."""
        self.tracker.cycles += 1

        if self.junker_model is not None:
            self.junker_model.increment_cycle()

    def get_state_summary(self) -> Dict[str, Any]:
        """
        Get comprehensive state summary.

        Returns:
            Dictionary with all state information
        """
        summary = self.tracker.get_state_summary()

        # Add cycle information
        summary['zero_crossings'] = self.zero_crossings

        # Add contact-specific information
        if self.thread_contact is not None and hasattr(self.thread_contact, 'theta_loosening_deg'):
            summary['theta_loosening_deg'] = self.thread_contact.theta_loosening_deg

        # Add Junker model information
        if self.junker_model is not None:
            summary['junker_regime'] = self.junker_model.current_regime.name
            summary['junker_T_net'] = self.junker_model.T_net

        return summary


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def compute_vdi_2230_embedding_factor(material_pair: str) -> float:
    """
    Compute VDI 2230 embedding factor f_z for common material pairs.

    Args:
        material_pair: Material combination string
            (e.g., "steel_steel", "steel_aluminum", "steel_cast_iron")

    Returns:
        Embedding factor f_z [m]
    """
    # VDI 2230 Table A3 - Embedding factors
    embedding_factors = {
        # Material pair: f_z [μm]
        "steel_steel": 3.0e-6,
        "steel_steel_ground": 2.0e-6,
        "steel_aluminum": 8.0e-6,
        "steel_cast_iron": 5.0e-6,
        "steel_brass": 6.0e-6,
        "steel_plastic": 15.0e-6,
        "steel_copper": 7.0e-6,
        "stainless_stainless": 4.0e-6,
    }

    return embedding_factors.get(material_pair.lower(), 5.0e-6)


def compute_system_stiffness(k_bolt: float, k_member: float) -> float:
    """
    Compute joint system stiffness (series combination).

    k_joint = 1 / (1/k_bolt + 1/k_member)

    Args:
        k_bolt: Bolt stiffness [N/m]
        k_member: Member stiffness [N/m]

    Returns:
        System stiffness k_joint [N/m]
    """
    if k_bolt <= 0 or k_member <= 0:
        return 0.0

    return 1.0 / (1.0/k_bolt + 1.0/k_member)


def estimate_embedding_length(geometry: Dict[str, float]) -> float:
    """
    Estimate embedding length L_K from joint geometry.

    L_K includes effective contact length at:
    - Bolt head bearing surface
    - Nut bearing surface
    - Thread engagement

    Args:
        geometry: Dictionary with geometric parameters
            - 'grip_length': Total grip length [m]
            - 'head_height': Bolt head height [m]
            - 'nut_height': Nut height [m]
            - 'thread_length': Thread engagement length [m]

    Returns:
        Embedding length L_K [m]
    """
    grip_length = geometry.get('grip_length', 0.05)
    head_height = geometry.get('head_height', 0.01)
    nut_height = geometry.get('nut_height', 0.01)
    thread_length = geometry.get('thread_length', 0.015)

    # VDI 2230 approach: L_K ≈ grip_length + equivalent head/nut contact
    # Simplified: use 50% of head/nut height as effective contact
    L_K = grip_length + 0.5 * (head_height + nut_height) + thread_length

    return L_K


# =============================================================================
# MODULE TESTING
# =============================================================================

if __name__ == "__main__":
    print("="*80)
    print("PRELOAD TRACKER - TEST SUITE")
    print("="*80)

    # Test 1: Basic Tracker Initialization
    print("\n[Test 1] Initialize Tracker")
    k_bolt = 2e9  # 2 GN/m
    k_member = 5e9  # 5 GN/m
    F_p0 = 100000  # 100 kN

    tracker = PreloadTracker(k_bolt, k_member, F_p0)
    print(f"  k_bolt: {k_bolt/1e9:.1f} GN/m")
    print(f"  k_member: {k_member/1e9:.1f} GN/m")
    print(f"  k_joint: {tracker.k_joint/1e9:.2f} GN/m")
    print(f"  F_p0: {F_p0/1000:.1f} kN")
    print(f"  Mechanisms initialized: {len(tracker.mechanisms)}")

    # Test 2: Add Various Losses
    print("\n[Test 2] Add Multiple Loss Mechanisms")

    # Rotational loosening
    tracker.mechanisms["rotational_loosening"].metadata["pitch"] = 0.00175  # M12 pitch
    tracker.add_rotational_loss(theta_loosening=np.radians(2.0))  # 2° loosening

    # Embedding
    f_z = compute_vdi_2230_embedding_factor("steel_steel")
    L_K = 0.050  # 50 mm grip
    tracker.add_embedding_loss(N=100, f_z=f_z, L_K=L_K)

    # Wear
    tracker.add_wear_loss(wear_depth=2e-6)  # 2 μm wear

    # Creep
    tracker.add_creep_loss(time=3600, C_r=0.05, delta_0=1e-5)  # 1 hour

    # Relaxation
    tracker.add_relaxation_loss(time=3600, tau=7200)  # τ = 2 hours

    # Update preload
    tracker.update_preload(dt=0.001)

    print(f"  Current preload: {tracker.get_current_preload()/1000:.2f} kN")
    print(f"  Total loss: {tracker.get_total_loss()/1000:.2f} kN ({tracker.get_total_loss()/F_p0*100:.1f}%)")

    # Test 3: Loss Breakdown
    print("\n[Test 3] Loss Breakdown")
    breakdown = tracker.get_loss_breakdown()
    percentages = tracker.get_loss_percentages()

    for name, loss in breakdown.items():
        pct = percentages.get(name, 0)
        print(f"  {name:25s}: {loss/1000:6.2f} kN ({pct:5.1f}%)")

    # Test 4: State Summary
    print("\n[Test 4] State Summary")
    summary = tracker.get_state_summary()
    print(f"  Time: {summary['time']:.1f} s")
    print(f"  Cycles: {summary['cycles']}")
    print(f"  Loss percentage: {summary['loss_percentage']:.2f}%")

    # Test 5: State Update Manager
    print("\n[Test 5] State Update Manager")

    # Create mock contact list (empty for test)
    contacts = []

    # Create manager
    manager = StateUpdateManager(contacts, None, tracker, None)

    # Simulate time steps with cycle detection
    x = np.array([0.0])
    dt = 0.001

    print("  Simulating 10 cycles...")
    for i in range(1000):
        t = i * dt
        x[0] = 0.001 * np.sin(2 * np.pi * 25 * t)  # 25 Hz oscillation
        x_dot = np.array([0.001 * 2 * np.pi * 25 * np.cos(2 * np.pi * 25 * t)])

        manager.update_all_states(x, x_dot, F_transverse=5000, dt=dt, t=t)

        if manager.detect_cycle_completion(x, x_dot):
            manager.increment_cycle()

    print(f"  Cycles detected: {manager.tracker.cycles}")
    print(f"  Zero crossings: {manager.zero_crossings}")

    final_summary = manager.get_state_summary()
    print(f"  Final preload: {final_summary['F_preload_current']/1000:.2f} kN")

    print("\n" + "="*80)
    print("ALL TESTS COMPLETED")
    print("="*80)
