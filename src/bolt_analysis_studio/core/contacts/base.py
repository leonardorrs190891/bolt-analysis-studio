"""
Base Contact Class and Property Definitions.

Every interface in a bolted joint is modeled as a Contact object that:
- Connects two components (nodes/DOFs)
- Has mechanical properties (stiffness, damping)
- Has tribological properties (friction, wear)
- Evolves over time (degradation, wear accumulation)
- Contributes to specific locations in global [M], [K], [C] matrices and {F} vector

Based on MSD_Contact_System_Architecture.md Section 3.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Optional, Callable, List, Tuple, Dict, Any
import math
import numpy as np


# =============================================================================
# ENUMERATIONS
# =============================================================================

class ContactMechanicalType(Enum):
    """Mechanical behavior classification."""
    LINEAR_ELASTIC = auto()      # k = constant
    NONLINEAR_ELASTIC = auto()   # k = f(F) or k = f(δ)
    PLASTIC = auto()             # Permanent deformation
    VISCOELASTIC = auto()        # Time-dependent (creep, relaxation)
    ELASTOPLASTIC = auto()       # Loading ≠ Unloading (hysteresis)


class FrictionModelType(Enum):
    """Friction model types."""
    COULOMB = auto()             # F = μ × N × sign(v)
    VISCOUS = auto()             # F = c × v
    STRIBECK = auto()            # μ = f(v) with dip
    LUGRE = auto()               # Dynamic state-based
    RATE_STATE = auto()          # μ = f(v, θ_state)
    REGULARIZED = auto()         # μ × N × tanh(v/v_reg)


class WearModelType(Enum):
    """Wear model types."""
    NONE = auto()
    ARCHARD = auto()             # V = K × F × s / H
    FRETTING = auto()            # Cyclic microslip
    ADHESIVE = auto()            # Galling/seizure
    OXIDATIVE = auto()           # High-temp degradation


class StiffnessModelType(Enum):
    """Stiffness behavior types."""
    LINEAR = auto()
    NONLINEAR_ELASTIC = auto()
    ELASTOPLASTIC = auto()
    VISCOELASTIC = auto()


class SlipState(Enum):
    """Contact slip state."""
    STUCK = "stuck"              # No relative motion
    MICRO_SLIP = "micro_slip"    # Small relative motion
    GROSS_SLIP = "gross_slip"    # Full sliding


# =============================================================================
# PROPERTY DATACLASSES
# =============================================================================

@dataclass
class ContactGeometry:
    """
    Geometric parameters for contact interface.

    Used to calculate contact area, effective radii, and stiffness.
    """
    inner_radius: float = 0.0       # [m] Inner radius (hole)
    outer_radius: float = 0.0       # [m] Outer radius (bearing surface)
    contact_area: float = 0.0       # [m²] Contact area (calculated or specified)
    thickness: float = 0.0          # [m] Effective thickness for stiffness
    roughness_Ra: float = 1.6e-6    # [m] Surface roughness

    def __post_init__(self):
        """Auto-calculate area if not specified."""
        if self.contact_area == 0.0 and self.outer_radius > self.inner_radius:
            self.contact_area = self.calc_annular_area()

    def calc_annular_area(self) -> float:
        """Calculate annular contact area."""
        return np.pi * (self.outer_radius**2 - self.inner_radius**2)

    def calc_effective_radius(self) -> float:
        """
        Calculate effective friction radius for annular contact.

        r_eff = (2/3) × (r_o³ - r_i³) / (r_o² - r_i²)
        """
        ri, ro = self.inner_radius, self.outer_radius
        if ro <= ri:
            return 0.0
        return (2/3) * (ro**3 - ri**3) / (ro**2 - ri**2)

    def to_dict(self) -> Dict[str, float]:
        return {
            "inner_radius": self.inner_radius,
            "outer_radius": self.outer_radius,
            "contact_area": self.contact_area,
            "thickness": self.thickness,
            "roughness_Ra": self.roughness_Ra,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, float]) -> 'ContactGeometry':
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


@dataclass
class FrictionProperties:
    """
    Friction parameters with time evolution capability.

    Friction coefficient can evolve due to:
    - Running-in (initial wear)
    - Lubricant spreading
    - Coating degradation
    - Temperature effects
    """
    mu_static: float = 0.15         # Static friction coefficient
    mu_kinetic: float = 0.12        # Kinetic friction coefficient
    mu_current: float = 0.15        # Current (evolving) value

    # Friction model
    model: FrictionModelType = FrictionModelType.COULOMB

    # Stribeck parameters
    v_stribeck: float = 0.01        # Stribeck velocity [m/s]
    stribeck_exp: float = 2.0       # Stribeck exponent

    # Viscous component
    viscous_coeff: float = 0.0      # [N·s/m]

    # Regularization (for numerical stability)
    v_reg: float = 1e-4             # Regularization velocity [m/s]

    # Time evolution parameters
    degradation_rate: float = 0.0   # [1/cycle] friction decrease per cycle
    min_friction: float = 0.05      # Minimum friction coefficient

    # State tracking
    accumulated_slip: float = 0.0   # [m] total slip distance
    cycles: int = 0

    def __post_init__(self):
        if self.mu_current == 0.0:
            self.mu_current = self.mu_static

    def update_friction(self, slip_increment: float, n_cycles: int = 1):
        """Update friction coefficient due to wear/degradation."""
        self.accumulated_slip += abs(slip_increment)
        self.cycles += n_cycles

        if self.degradation_rate > 0:
            # Friction decreases with accumulated cycles
            decay = np.exp(-self.degradation_rate * self.cycles)
            self.mu_current = self.min_friction + (self.mu_static - self.min_friction) * decay

    def get_friction_force(self, velocity: float, normal_force: float) -> float:
        """
        Calculate friction force based on model.

        Args:
            velocity: Relative velocity [m/s]
            normal_force: Normal force [N]

        Returns:
            Friction force [N] (opposes motion)
        """
        if self.model == FrictionModelType.COULOMB:
            if abs(velocity) < self.v_reg:
                # Stuck: return static friction resisting the last slip direction
                slip_sign = np.sign(self.accumulated_slip) if self.accumulated_slip != 0.0 else 0.0
                return -slip_sign * self.mu_static * abs(normal_force)
            return -self.mu_current * normal_force * np.sign(velocity)

        elif self.model == FrictionModelType.REGULARIZED:
            # Smooth approximation using tanh
            return -self.mu_current * normal_force * np.tanh(velocity / self.v_reg)

        elif self.model == FrictionModelType.STRIBECK:
            # Stribeck model: μ(v) = μ_k + (μ_s - μ_k) × exp(-(v/v_s)^n)
            if abs(velocity) < 1e-10:
                return 0.0

            mu = self.mu_kinetic + (self.mu_current - self.mu_kinetic) * \
                 np.exp(-(abs(velocity) / self.v_stribeck) ** self.stribeck_exp)

            F_friction = -mu * normal_force * np.sign(velocity)

            # Add viscous component
            F_friction -= self.viscous_coeff * velocity

            return F_friction

        elif self.model == FrictionModelType.VISCOUS:
            return -self.viscous_coeff * velocity

        # Default to regularized Coulomb
        return -self.mu_current * normal_force * np.tanh(velocity / self.v_reg)

    def get_max_static_force(self, normal_force: float) -> float:
        """Maximum force before slip occurs."""
        return self.mu_static * normal_force

    def to_dict(self) -> Dict[str, Any]:
        return {
            "mu_static": self.mu_static,
            "mu_kinetic": self.mu_kinetic,
            "mu_current": self.mu_current,
            "model": self.model.name,
            "v_stribeck": self.v_stribeck,
            "stribeck_exp": self.stribeck_exp,
            "viscous_coeff": self.viscous_coeff,
            "degradation_rate": self.degradation_rate,
            "min_friction": self.min_friction,
            "accumulated_slip": self.accumulated_slip,
            "cycles": self.cycles,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FrictionProperties':
        data = data.copy()
        if 'model' in data and isinstance(data['model'], str):
            data['model'] = FrictionModelType[data['model']]
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


@dataclass
class WearProperties:
    """
    Wear parameters and state tracking.

    Implements:
    - Archard wear law: V = K × F × s / H
    - Fretting wear for cyclic microslip
    """
    wear_model: WearModelType = WearModelType.ARCHARD

    # Archard parameters
    wear_coeff_K: float = 1e-6      # Wear coefficient [-]
    hardness: float = 2.5e9         # Surface hardness [Pa]

    # Fretting parameters
    fretting_threshold: float = 5e-6    # Slip amplitude for fretting [m]
    fretting_coeff: float = 1e-5        # Fretting wear coefficient

    # State
    wear_volume: float = 0.0        # Accumulated wear volume [m³]
    wear_depth: float = 0.0         # Effective wear depth [m]

    def calc_wear_increment(self, normal_force: float, slip_distance: float,
                           contact_area: float) -> float:
        """
        Calculate wear for one increment.

        Args:
            normal_force: Normal contact force [N]
            slip_distance: Relative slip distance [m]
            contact_area: Contact area [m²]

        Returns:
            Wear volume increment [m³]
        """
        if self.wear_model == WearModelType.NONE:
            return 0.0

        elif self.wear_model == WearModelType.ARCHARD:
            # Archard: V = K × F × s / H
            dV = self.wear_coeff_K * normal_force * abs(slip_distance) / self.hardness
            self.wear_volume += dV
            self.wear_depth = self.wear_volume / contact_area if contact_area > 0 else 0
            return dV

        elif self.wear_model == WearModelType.FRETTING:
            # Fretting only if slip amplitude in fretting regime
            if abs(slip_distance) < self.fretting_threshold:
                dV = self.fretting_coeff * normal_force * abs(slip_distance) / self.hardness
                self.wear_volume += dV
                self.wear_depth = self.wear_volume / contact_area if contact_area > 0 else 0
                return dV
            return 0.0

        return 0.0

    def get_preload_loss(self, system_stiffness: float) -> float:
        """
        Calculate preload loss from wear depth.

        ΔF = k × δ_wear
        """
        return system_stiffness * self.wear_depth

    def to_dict(self) -> Dict[str, Any]:
        return {
            "wear_model": self.wear_model.name,
            "wear_coeff_K": self.wear_coeff_K,
            "hardness": self.hardness,
            "fretting_threshold": self.fretting_threshold,
            "fretting_coeff": self.fretting_coeff,
            "wear_volume": self.wear_volume,
            "wear_depth": self.wear_depth,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WearProperties':
        data = data.copy()
        if 'wear_model' in data and isinstance(data['wear_model'], str):
            data['wear_model'] = WearModelType[data['wear_model']]
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


@dataclass
class StiffnessProperties:
    """
    Stiffness parameters for contact.

    Supports linear and nonlinear stiffness models.
    """
    stiffness_model: StiffnessModelType = StiffnessModelType.LINEAR

    # Linear stiffness
    k_axial: float = 1e9            # Axial stiffness [N/m]
    k_torsional: float = 0.0        # Torsional stiffness [N·m/rad]
    k_transverse: float = 0.0       # Transverse stiffness [N/m]

    # Nonlinear parameters (functions can be set externally)
    k_loading_factor: float = 1.0   # Multiplier for loading
    k_unloading_factor: float = 1.5 # Multiplier for unloading (hysteresis)

    # Viscoelastic parameters (Kelvin-Voigt model)
    E_instantaneous: float = 0.0    # Instantaneous modulus [Pa]
    E_equilibrium: float = 0.0      # Long-term modulus [Pa]
    tau_relax: float = 1.0          # Relaxation time [s]

    # Plasticity
    yield_stress: float = float('inf')  # Yield stress for plastic contact
    plastic_strain: float = 0.0         # Accumulated plastic strain

    def get_tangent_stiffness(self, force: float = 0.0, loading: bool = True) -> float:
        """Get current tangent stiffness."""
        if self.stiffness_model == StiffnessModelType.LINEAR:
            return self.k_axial

        elif self.stiffness_model == StiffnessModelType.ELASTOPLASTIC:
            if loading:
                return self.k_axial * self.k_loading_factor
            else:
                return self.k_axial * self.k_unloading_factor

        return self.k_axial

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stiffness_model": self.stiffness_model.name,
            "k_axial": self.k_axial,
            "k_torsional": self.k_torsional,
            "k_transverse": self.k_transverse,
            "k_loading_factor": self.k_loading_factor,
            "k_unloading_factor": self.k_unloading_factor,
            "E_instantaneous": self.E_instantaneous,
            "E_equilibrium": self.E_equilibrium,
            "tau_relax": self.tau_relax,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'StiffnessProperties':
        data = data.copy()
        if 'stiffness_model' in data and isinstance(data['stiffness_model'], str):
            data['stiffness_model'] = StiffnessModelType[data['stiffness_model']]
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


@dataclass
class DampingProperties:
    """Damping parameters for contact."""
    damping_ratio: float = 0.02     # ζ for c = 2ζ√(km)
    c_viscous: float = 0.0          # Direct viscous damping [N·s/m]
    c_friction_equiv: float = 0.0   # Equivalent viscous from friction

    def get_damping(self, stiffness: float, mass: float = 0.01) -> float:
        """
        Calculate total damping coefficient.

        c = 2ζ√(km) + c_viscous + c_friction_equiv
        """
        c_material = 2 * self.damping_ratio * np.sqrt(stiffness * mass)
        return c_material + self.c_viscous + self.c_friction_equiv

    def to_dict(self) -> Dict[str, float]:
        return {
            "damping_ratio": self.damping_ratio,
            "c_viscous": self.c_viscous,
            "c_friction_equiv": self.c_friction_equiv,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, float]) -> 'DampingProperties':
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


# =============================================================================
# BASE CONTACT CLASS
# =============================================================================

class Contact(ABC):
    """
    Abstract base class for all contact types.

    Each contact connects two components and contributes to:
    - [K] stiffness matrix (elastic behavior)
    - [C] damping matrix (viscous/material damping + friction equivalent)
    - {F} force vector (Coulomb friction, wear effects)

    The contact also tracks state variables that evolve over time.

    Matrix Contribution Pattern for contact between nodes i and j:

    STIFFNESS [K]:           DAMPING [C]:            FORCE {F}:
         i      j                i      j
       ┌─────┬─────┐          ┌─────┬─────┐         ┌─────┐
     i │ +k  │ -k  │        i │ +c  │ -c  │       i │ +F  │
       ├─────┼─────┤          ├─────┼─────┤         ├─────┤
     j │ -k  │ +k  │        j │ -c  │ +c  │       j │ -F  │
       └─────┴─────┘          └─────┴─────┘         └─────┘
    """

    def __init__(self,
                 contact_id: str,
                 contact_type: str,
                 node_i: int,
                 node_j: int,
                 geometry: ContactGeometry,
                 friction: FrictionProperties,
                 wear: WearProperties,
                 stiffness: StiffnessProperties,
                 damping: DampingProperties):
        """
        Initialize contact.

        Args:
            contact_id: Unique identifier for this contact
            contact_type: Type name (e.g., "THREAD", "BEARING_HEAD")
            node_i: First component DOF index
            node_j: Second component DOF index (-1 for ground)
            geometry: Contact geometry parameters
            friction: Friction properties
            wear: Wear properties
            stiffness: Stiffness properties
            damping: Damping properties
        """
        self.id = contact_id
        self.type = contact_type
        self.node_i = node_i        # First component DOF
        self.node_j = node_j        # Second component DOF (-1 for ground)

        self.geometry = geometry
        self.friction = friction
        self.wear = wear
        self.stiffness = stiffness
        self.damping = damping

        # State variables
        self.normal_force: float = 0.0      # Current normal force (from preload)
        self.slip_state: SlipState = SlipState.STUCK
        self.relative_displacement: float = 0.0
        self.relative_velocity: float = 0.0
        self.time: float = 0.0
        self.cycles: int = 0

    @abstractmethod
    def get_stiffness_contribution(self) -> List[Tuple[int, int, float]]:
        """
        Returns stiffness contributions to global [K] matrix.

        Returns:
            List of (row, col, value) contributions to add to [K]
        """
        pass

    @abstractmethod
    def get_damping_contribution(self) -> List[Tuple[int, int, float]]:
        """
        Returns damping contributions to global [C] matrix.

        Returns:
            List of (row, col, value) contributions to add to [C]
        """
        pass

    @abstractmethod
    def get_force_contribution(self, x: np.ndarray, x_dot: np.ndarray,
                               t: float) -> np.ndarray:
        """
        Returns force contributions to {F} vector.

        This includes:
        - Coulomb friction forces (nonlinear)
        - Wear-induced forces
        - Plastic deformation forces

        Args:
            x: Displacement vector
            x_dot: Velocity vector
            t: Current time

        Returns:
            Force vector contribution (same size as x)
        """
        pass

    def get_basic_stiffness_contribution(self) -> List[Tuple[int, int, float]]:
        """
        Standard stiffness contribution pattern for two-node contact.

        K[i,i] += k, K[j,j] += k, K[i,j] -= k, K[j,i] -= k
        """
        k = self.stiffness.k_axial
        i, j = self.node_i, self.node_j

        contributions = [(i, i, k)]

        if j >= 0:  # Not grounded
            contributions.extend([
                (j, j, k),
                (i, j, -k),
                (j, i, -k),
            ])

        return contributions

    def get_basic_damping_contribution(self, mass_eff: float = 0.01) -> List[Tuple[int, int, float]]:
        """
        Standard damping contribution pattern for two-node contact.
        """
        k = self.stiffness.k_axial
        c = self.damping.get_damping(k, mass_eff)

        i, j = self.node_i, self.node_j

        contributions = [(i, i, c)]

        if j >= 0:
            contributions.extend([
                (j, j, c),
                (i, j, -c),
                (j, i, -c),
            ])

        return contributions

    def update_state(self, x: np.ndarray, x_dot: np.ndarray,
                    dt: float, preload: float):
        """
        Update contact state after a time step.

        Args:
            x: Current displacement vector
            x_dot: Current velocity vector
            dt: Time step
            preload: Current preload force
        """
        # Update relative motion
        if self.node_j >= 0 and self.node_j < len(x):
            self.relative_displacement = x[self.node_i] - x[self.node_j]
            self.relative_velocity = x_dot[self.node_i] - x_dot[self.node_j]
        else:
            self.relative_displacement = x[self.node_i]
            self.relative_velocity = x_dot[self.node_i]

        # Update normal force (from preload)
        self.normal_force = preload

        # Update friction state
        slip_distance = abs(self.relative_velocity) * dt
        self.friction.update_friction(slip_distance)

        # Update wear state
        if self.geometry.contact_area > 0:
            self.wear.calc_wear_increment(
                self.normal_force,
                slip_distance,
                self.geometry.contact_area
            )

        self.time += dt

    def check_slip_state(self, tangential_force: float) -> SlipState:
        """
        Determine if contact is stuck or slipping.

        Args:
            tangential_force: Applied tangential force [N]

        Returns:
            Current slip state
        """
        F_slip = self.friction.mu_current * self.normal_force

        if abs(tangential_force) < F_slip * 0.9:
            self.slip_state = SlipState.STUCK
        elif abs(tangential_force) < F_slip:
            self.slip_state = SlipState.MICRO_SLIP
        else:
            self.slip_state = SlipState.GROSS_SLIP

        return self.slip_state

    def get_preload_loss(self, system_stiffness: float) -> float:
        """
        Calculate total preload loss from this contact.

        Base implementation returns wear-based loss.
        Subclasses can add rotational loosening, etc.
        """
        return self.wear.get_preload_loss(system_stiffness)

    # ------------------------------------------------------------------
    # Phase D: Fretting Wear Coupling
    # ------------------------------------------------------------------

    def compute_fretting_regime(self, slip_amplitude_m: float) -> str:
        """
        Classify fretting regime from slip amplitude (Vingsbo-Söderberg map).

        Regimes (ISO/TR 15144-1 annex, Vingsbo & Söderberg 1988):
          - 'stick':        δ < δ_micro  — no measurable surface damage
          - 'partial_slip': δ_micro ≤ δ < δ_fretting  — fretting fatigue dominant
          - 'fretting':     δ_fretting ≤ δ < δ_gross   — fretting wear dominant
          - 'gross_slip':   δ ≥ δ_gross               — reciprocating sliding wear

        Default thresholds for machined steel M12:
          δ_micro   ≈ 1 µm   (elastic limit of asperities)
          δ_fretting ≈ 5 µm  (stored in wear.fretting_threshold)
          δ_gross   ≈ 50 µm  (transition to gross sliding wear)

        Args:
            slip_amplitude_m: Absolute slip amplitude [m]

        Returns:
            Regime string: 'stick' | 'partial_slip' | 'fretting' | 'gross_slip'
        """
        delta = abs(slip_amplitude_m)
        delta_micro    = 1e-6    # 1 µm
        delta_fretting = getattr(self.wear, 'fretting_threshold', 5e-6)
        delta_gross    = 50e-6   # 50 µm

        if delta < delta_micro:
            return 'stick'
        if delta < delta_fretting:
            return 'partial_slip'
        if delta < delta_gross:
            return 'fretting'
        return 'gross_slip'

    def compute_slip_index(self, slip_amplitude_m: float,
                           normal_force: float) -> float:
        """
        Compute dimensionless Slip Index (SI) for fretting map position.

        SI = (µ_kinetic × N × δ) / E*  (Waterhouse energy criterion)

        where E* = combined elastic modulus × contact area (normalised energy).
        When no geometry/material data is available, SI falls back to a
        normalised slip ratio δ / δ_gross.

        Args:
            slip_amplitude_m: Absolute slip amplitude [m]
            normal_force:     Normal contact force [N]

        Returns:
            Dimensionless Slip Index ≥ 0
        """
        delta = abs(slip_amplitude_m)
        if delta <= 0:
            return 0.0

        mu_k = getattr(self.friction, 'mu_kinetic', self.friction.mu_current)
        # Attempt energy-based SI if combined modulus is available
        E_star = getattr(self.stiffness, 'E_combined', None)
        A_nom  = getattr(self.geometry, 'area', None)
        if E_star and A_nom and E_star > 0 and A_nom > 0:
            SI = mu_k * normal_force * delta / (E_star * A_nom)
        else:
            # Fallback: normalised slip ratio
            delta_gross = 50e-6
            SI = min(delta / delta_gross, 1.0)

        return float(SI)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize contact to dictionary."""
        return {
            "id": self.id,
            "type": self.type,
            "node_i": self.node_i,
            "node_j": self.node_j,
            "geometry": self.geometry.to_dict(),
            "friction": self.friction.to_dict(),
            "wear": self.wear.to_dict(),
            "stiffness": self.stiffness.to_dict(),
            "damping": self.damping.to_dict(),
            "normal_force": self.normal_force,
            "slip_state": self.slip_state.value,
            "time": self.time,
            "cycles": self.cycles,
        }


# =============================================================================
# FRACTAL CONTACT STIFFNESS (NI2 - Phase 10)
# =============================================================================

def compute_fractal_contact_stiffness(
    nominal_area: float,                    # Nominal contact area [m^2]
    normal_force: float,                    # Normal contact force [N]
    E_star: float,                          # Combined elastic modulus [Pa]
    fractal_dimension: float = 2.4,         # Fractal dimension D (2 < D < 3)
    roughness_G: float = 1e-11,             # Fractal roughness parameter [m]
    hardness: float = 2e9,                  # Material hardness [Pa]
) -> Dict[str, float]:
    """
    Semi-analytical contact stiffness using Majumdar-Bhushan fractal model (NI2).

    The Majumdar-Bhushan (M-B) model treats real engineering surfaces as
    fractals with self-affine roughness described by two parameters: the
    fractal dimension D and the roughness scaling parameter G. The real
    contact area is a collection of micro-contacts (asperities) whose
    size distribution follows a power law derived from the Weierstrass-
    Mandelbrot fractal surface profile.

    The fractal dimension D characterizes the surface complexity:
    - D close to 2: smooth, gentle undulations (polished surfaces)
    - D close to 3: extremely rough, many asperities (as-machined)
    - Typical machined steel: D = 2.3 - 2.6

    For a single asperity of contact area a, the deformation is:

        delta(a) = G^(D-2) * a^((3-D)/2)      (elastic)
        delta(a) = G^(D-2) * a^((3-D)/2)      (plastic, for a < a_c)

    where the critical area separating elastic/plastic regimes is:

        a_c = (G^2 * (E_star / H)^2)^(1/(D-2))

    The size distribution of asperities with area a in a surface with
    largest contact spot a_L follows:

        n(a) = (D-1)/2 * a_L^((D-1)/2) * a^(-(D+1)/2)

    The total real contact area is:

        A_r = integral[0 to a_L] n(a) * a da
            = (D-1)/(3-D) * a_L    (for 2 < D < 3, D != 3)

    The total normal force is obtained by integrating elastic (Hertzian)
    and plastic contributions over the asperity size distribution.

    Normal contact stiffness is obtained by differentiating the
    force-displacement relation:

        k_n = dF/d(delta)

    Tangential stiffness is related to normal stiffness through:

        k_t = k_n * 2(1-nu)/(2-nu)

    For typical steel nu=0.3, k_t ~ 0.76 * k_n.

    References:
        - Majumdar, A. & Bhushan, B. (1991). "Fractal model of
          elastic-plastic contact between rough surfaces." ASME
          J. Tribology, 113(1): 1-11.
        - Jiang, S., Zheng, Y., & Zhu, H. (2010). "A contact
          stiffness model of machined plane joint based on fractal
          theory." ASME J. Tribology, 132(1): 011401.
        - Zhang, X., Wen, S., & Lan, G. (2020). "Fractal model
          for normal contact damping and stiffness of bolted joint
          surface." Chinese J. Mechanical Engineering, 33: 67.

    Args:
        nominal_area: Nominal (apparent) contact area [m^2].
        normal_force: Applied normal contact force [N].
        E_star: Combined (reduced) elastic modulus [Pa]:
                1/E_star = (1-nu1^2)/E1 + (1-nu2^2)/E2
        fractal_dimension: Fractal dimension D of the surface
                          (must satisfy 2 < D < 3).
        roughness_G: Fractal roughness parameter G [m].
                    Larger G = rougher surface.
                    Typical machined steel: 1e-12 to 1e-9 m.
        hardness: Material hardness H [Pa] (e.g. Vickers or flow stress).
                 Used to determine elastic/plastic transition.

    Returns:
        Dictionary containing:
        - k_normal: Normal contact stiffness [N/m]
        - k_tangential: Tangential contact stiffness [N/m]
        - real_contact_area: Real contact area A_r [m^2]
        - area_ratio: Real/nominal area ratio A_r / A_n [-]
        - n_asperities: Estimated number of contact asperities [-]
        - critical_area: Critical area a_c for elastic-plastic
                        transition [m^2]
        - largest_contact_area: Largest asperity contact area a_L [m^2]
        - elastic_force: Force carried by elastic asperities [N]
        - plastic_force: Force carried by plastic asperities [N]
        - plastic_ratio: Fraction of force carried plastically [-]

    Raises:
        ValueError: If fractal_dimension not in (2, 3) or other
                   invalid parameters.
    """
    D = fractal_dimension
    G_f = roughness_G
    An = nominal_area
    F_n = normal_force
    H = hardness

    # --- Input validation ---
    if D <= 2.0 or D >= 3.0:
        raise ValueError(
            f"Fractal dimension D must satisfy 2 < D < 3, got D={D}"
        )
    if An <= 0:
        raise ValueError(f"Nominal area must be positive, got {An}")
    if F_n <= 0:
        raise ValueError(f"Normal force must be positive, got {F_n}")
    if E_star <= 0:
        raise ValueError(f"Combined modulus must be positive, got {E_star}")
    if G_f <= 0:
        raise ValueError(f"Roughness parameter G must be positive, got {G_f}")
    if H <= 0:
        raise ValueError(f"Hardness must be positive, got {H}")

    # --- Derived fractal exponents ---
    # d = D - 1 is the profile fractal dimension (1 < d < 2)
    # We work with the surface dimension D (2 < D < 3)

    # Critical contact area: separates elastic (a > a_c) from plastic (a < a_c)
    # a_c = G^2 * (E_star / H)^(2/(D-2))
    # From M-B: critical truncation area where contact transitions
    # from elastic to plastic deformation
    a_c = G_f**2 * (E_star / H) ** (2.0 / (D - 2.0))

    # --- Determine largest asperity contact area a_L from force balance ---
    # The total force must equal F_n. We solve iteratively.
    #
    # For the M-B model, the force from elastic asperities (a > a_c):
    #   F_e = integral[a_c to a_L] p_e(a) * n(a) da
    # where for elastic Hertzian contact:
    #   p_e(a) = (4/3) * E_star * G^(D-2) * a^((4-D)/2) / sqrt(pi)
    #
    # And from plastic asperities (a < a_c):
    #   F_p = integral[0 to min(a_c, a_L)] H * a * n(a) da
    #
    # n(a) = (D-1)/2 * a_L^((D-1)/2) * a^(-(D+1)/2)
    #
    # We solve for a_L such that F_e + F_p = F_n.

    # First define helper exponents
    # For elastic force integral:
    #   F_e = (4/3) * E_star * G^(D-2) / sqrt(pi) *
    #         (D-1)/2 * a_L^((D-1)/2) *
    #         integral[a_c to a_L] a^((4-D)/2 - (D+1)/2) da
    #       = C_e * a_L^((D-1)/2) * integral[a_c to a_L] a^((3-2D)/2) da
    #
    # Exponent of a in elastic integrand: (4-D)/2 - (D+1)/2 = (3-2D)/2

    exp_e = (3.0 - 2.0 * D) / 2.0  # Exponent in elastic force integrand

    # Prefactor for elastic force (per unit a_L^((D-1)/2))
    C_e = (4.0 / 3.0) * E_star * G_f**(D - 2.0) / math.sqrt(math.pi) * (D - 1.0) / 2.0

    # For plastic force integral:
    #   F_p = H * (D-1)/2 * a_L^((D-1)/2) *
    #         integral[0 to a_c'] a^(1 - (D+1)/2) da
    #       = C_p * a_L^((D-1)/2) * integral[0 to a_c'] a^((1-D)/2) da
    #
    # Exponent of a in plastic integrand: 1 - (D+1)/2 = (1-D)/2

    exp_p = (1.0 - D) / 2.0  # Exponent in plastic force integrand
    C_p = H * (D - 1.0) / 2.0

    def _compute_force(a_L_trial: float) -> Tuple[float, float, float]:
        """Compute elastic and plastic force for a given a_L."""
        a_L_half = a_L_trial ** ((D - 1.0) / 2.0)

        # Elastic contribution: integrate from a_c to a_L (if a_c < a_L)
        F_elastic = 0.0
        if a_c < a_L_trial:
            # Integral of a^exp_e from a_c to a_L
            if abs(exp_e + 1.0) < 1e-12:
                # Special case: exp_e = -1 => log integral
                integral_e = math.log(a_L_trial / a_c)
            else:
                integral_e = (
                    a_L_trial**(exp_e + 1.0) - a_c**(exp_e + 1.0)
                ) / (exp_e + 1.0)
            F_elastic = C_e * a_L_half * integral_e

        # Plastic contribution: integrate from 0 to min(a_c, a_L)
        a_c_eff = min(a_c, a_L_trial)
        F_plastic = 0.0
        if a_c_eff > 0:
            # Integral of a^exp_p from 0 to a_c_eff
            # exp_p = (1-D)/2, for D>1 this is negative
            # Since D in (2,3), exp_p in (-1, -0.5) so exp_p+1 in (0, 0.5) > 0
            # The integral converges at a=0.
            if abs(exp_p + 1.0) < 1e-12:
                integral_p = math.log(a_c_eff / 1e-30)  # won't happen
            else:
                integral_p = a_c_eff**(exp_p + 1.0) / (exp_p + 1.0)
            F_plastic = C_p * a_L_half * integral_p

        return F_elastic, F_plastic, F_elastic + F_plastic

    # --- Solve for a_L using bisection ---
    # Bounds for a_L: very small to nominal area
    a_L_min = 1e-30
    a_L_max = An  # a_L cannot exceed nominal area

    # Check if maximum yields enough force
    _, _, F_max = _compute_force(a_L_max)
    if F_max < F_n:
        # Force is too high for this surface; saturate at a_L = An
        a_L = An
    else:
        # Bisection search
        for _ in range(200):
            a_L_mid = math.sqrt(a_L_min * a_L_max)  # geometric mean for log-space
            _, _, F_mid = _compute_force(a_L_mid)
            if F_mid < F_n:
                a_L_min = a_L_mid
            else:
                a_L_max = a_L_mid
            if abs(a_L_max / a_L_min - 1.0) < 1e-10:
                break
        a_L = math.sqrt(a_L_min * a_L_max)

    # --- Compute results at converged a_L ---
    F_elastic, F_plastic, F_total = _compute_force(a_L)

    # Real contact area:
    #   A_r = integral[0 to a_L] n(a) * a da
    #       = (D-1)/2 * a_L^((D-1)/2) * integral[0 to a_L] a^((1-D)/2) da
    #       = (D-1)/2 * a_L^((D-1)/2) * a_L^((3-D)/2) / ((3-D)/2)
    #       = (D-1)/(3-D) * a_L
    A_r = (D - 1.0) / (3.0 - D) * a_L

    # Clamp real area to not exceed nominal
    A_r = min(A_r, An)

    # Area ratio
    area_ratio = A_r / An if An > 0 else 0.0

    # --- Normal contact stiffness ---
    # k_n = dF/d(delta_global)
    #
    # From Jiang et al. (2010), the normal stiffness is:
    #
    # For the elastic regime:
    #   k_n_elastic = integral[a_c to a_L]  (dF_e/d_delta) * n(a) da
    #
    # The single-asperity elastic stiffness is:
    #   dF_e/d_delta = 2 * E_star * sqrt(a / pi)
    #
    # Integrating over the asperity distribution:
    #   k_n_e = (D-1)/2 * a_L^((D-1)/2) * 2*E_star/sqrt(pi) *
    #           integral[a_c to a_L] a^((1-D)/2) * a^(1/2) da
    #         = (D-1) * E_star / sqrt(pi) * a_L^((D-1)/2) *
    #           integral[a_c to a_L] a^((2-D)/2) da
    #
    # Exponent in stiffness integrand: (1-D)/2 + 1/2 - (D+1)/2 + 1
    #   Wait, let me be more careful.
    #   n(a) has a^(-(D+1)/2), and the per-asperity stiffness has a^(1/2).
    #   So the integrand exponent is: -(D+1)/2 + 1/2 = -D/2
    #   But we also multiply by a from n(a)... no.
    #
    # Actually, n(a) da gives the number of asperities with area in [a, a+da].
    # Each asperity of area a has stiffness dk = 2*E_star*sqrt(a/pi).
    # The total stiffness contribution from elastic asperities is:
    #
    #   k_n_e = integral[a_c to a_L] 2*E_star*sqrt(a/pi) * n(a) da
    #
    # n(a) = (D-1)/2 * a_L^((D-1)/2) * a^(-(D+1)/2)
    #
    # So integrand power of a: 1/2 - (D+1)/2 = (1-D-1)/2 = -D/2
    #
    #   k_n_e = (D-1)*E_star/sqrt(pi) * a_L^((D-1)/2) *
    #           integral[a_c to a_L] a^(-D/2) da

    exp_k = -D / 2.0  # Exponent in stiffness integrand

    a_L_half = a_L ** ((D - 1.0) / 2.0)
    C_k = (D - 1.0) * E_star / math.sqrt(math.pi)

    # Elastic stiffness
    k_n_elastic = 0.0
    if a_c < a_L:
        if abs(exp_k + 1.0) < 1e-12:
            integral_k = math.log(a_L / a_c)
        else:
            integral_k = (
                a_L**(exp_k + 1.0) - a_c**(exp_k + 1.0)
            ) / (exp_k + 1.0)
        k_n_elastic = C_k * a_L_half * integral_k

    # Plastic asperities contribute approximately:
    #   k_n_plastic ~ H * A_r_plastic / delta_avg_plastic
    # But in the M-B model, plastic asperities are treated as having
    # constant pressure = H, so their stiffness is effectively zero
    # (perfectly plastic). The total stiffness comes only from elastic
    # asperities. However, for numerical convenience we add a small
    # plastic stiffness proportional to the plastic area.
    A_r_plastic = 0.0
    if a_c > 0 and a_c < a_L:
        # Plastic real area: integral from 0 to a_c of n(a)*a da
        A_r_plastic = (D - 1.0) / (3.0 - D) * a_c * (a_c / a_L) ** ((D - 3.0) / 2.0)
        # Approximate a small stiffness for plastic zone
        # (Zhang et al. 2020 approach)
        if A_r_plastic > 0:
            # Average plastic asperity deformation
            delta_p_avg = G_f**(D - 2.0) * a_c**((3.0 - D) / 2.0)
            if delta_p_avg > 0:
                k_n_plastic = H * A_r_plastic / delta_p_avg * 0.1
            else:
                k_n_plastic = 0.0
        else:
            k_n_plastic = 0.0
    elif a_c >= a_L:
        # All contacts are plastic
        A_r_plastic = A_r
        # Estimate stiffness from average deformation
        delta_avg = G_f**(D - 2.0) * (a_L / 2.0)**((3.0 - D) / 2.0)
        if delta_avg > 0:
            k_n_plastic = H * A_r_plastic / delta_avg * 0.1
        else:
            k_n_plastic = 0.0
    else:
        k_n_plastic = 0.0

    k_normal = k_n_elastic + k_n_plastic

    # Ensure stiffness is positive and physically reasonable
    if k_normal <= 0:
        # Fallback: use Hertzian estimate based on real contact area
        k_normal = 2.0 * E_star * math.sqrt(A_r / math.pi)

    # --- Tangential stiffness ---
    # Mindlin theory: k_t/k_n = 2(1-nu)/(2-nu)
    # For typical steel nu=0.3: ratio ~ 0.765
    # Since we have E_star = E / (2*(1-nu^2)) for identical materials,
    # we estimate nu from E_star and the individual E.
    # Default assumption: nu = 0.3
    nu = 0.3
    tangential_ratio = 2.0 * (1.0 - nu) / (2.0 - nu)
    k_tangential = k_normal * tangential_ratio

    # --- Estimate number of asperities ---
    # N = integral[0 to a_L] n(a) da
    #   = (D-1)/2 * a_L^((D-1)/2) * integral[0 to a_L] a^(-(D+1)/2) da
    #   = (D-1)/2 * a_L^((D-1)/2) * a_L^((1-D)/2) / ((1-D)/2)   [if D > 1]
    #   = ... diverges at a=0 for D > 1
    #
    # In practice, we truncate at a minimum asperity area a_min.
    # Use the atomic/grain scale as lower cutoff.
    a_min = 1e-18  # ~ (1 nm)^2 minimum asperity area
    if D > 1.0:
        # N ~ (D-1)/(D-1) * (a_L / a_min)^((D-1)/2)   (approximate)
        n_asperities = (a_L / a_min) ** ((D - 1.0) / 2.0)
        # Cap at a reasonable number
        n_asperities = min(n_asperities, 1e15)
    else:
        n_asperities = 1.0

    # Plastic ratio
    plastic_ratio = F_plastic / F_total if F_total > 0 else 0.0

    return {
        'k_normal': k_normal,
        'k_tangential': k_tangential,
        'real_contact_area': A_r,
        'area_ratio': area_ratio,
        'n_asperities': n_asperities,
        'critical_area': a_c,
        'largest_contact_area': a_L,
        'elastic_force': F_elastic,
        'plastic_force': F_plastic,
        'plastic_ratio': plastic_ratio,
    }


def compute_combined_elastic_modulus(
    E1: float, nu1: float, E2: float, nu2: float
) -> float:
    """
    Compute the combined (reduced) elastic modulus for two contacting bodies.

    E* = 1 / ((1-nu1^2)/E1 + (1-nu2^2)/E2)

    This is used as the E_star input for compute_fractal_contact_stiffness().

    Args:
        E1: Young's modulus of body 1 [Pa]
        nu1: Poisson's ratio of body 1 [-]
        E2: Young's modulus of body 2 [Pa]
        nu2: Poisson's ratio of body 2 [-]

    Returns:
        Combined elastic modulus E* [Pa]
    """
    return 1.0 / ((1.0 - nu1**2) / E1 + (1.0 - nu2**2) / E2)
