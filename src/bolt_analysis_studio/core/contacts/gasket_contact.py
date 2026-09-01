"""
Gasket Contact Implementation with Nonlinear Stiffness, Creep, and Stress Relaxation.

Models the flange-gasket interface as a complex viscoelastic contact with:
- Nonlinear stiffness (loading/unloading hysteresis)
- Creep deformation under sustained load
- Stress relaxation (force decay at constant compression)
- Temperature effects
- Multiple gasket types (spiral wound, RTJ, sheet, etc.)

Key Features:
- GasketType enum for different gasket materials/designs
- LoadingState tracking (LOADING, UNLOADING, NEUTRAL)
- Nonlinear k(F) or k(δ) relationships
- Creep model: ε_creep(t) = A × σⁿ × tᵐ
- Stress relaxation: F(t) = F₀ × exp(-t/τ_relax)
- Preload loss from gasket deformation

Based on ASME PCC-1, EN 1591-1, and VDI 2230 gasket models.
"""

from dataclasses import dataclass
from enum import Enum, auto
from typing import List, Tuple, Optional, Dict, Any, Callable
import numpy as np

from .base import (
    Contact,
    ContactGeometry,
    FrictionProperties,
    WearProperties,
    StiffnessProperties,
    StiffnessModelType,
    DampingProperties,
    SlipState,
)


# =============================================================================
# GASKET TYPE CLASSIFICATION
# =============================================================================

class GasketType(Enum):
    """Gasket material and design types."""
    SPIRAL_WOUND = auto()       # Spiral wound with filler (ASME B16.20)
    RTJ = auto()                # Ring Type Joint (API 6A)
    SHEET = auto()              # Compressed fiber sheet
    KAMMPROFILE = auto()        # Serrated metal with soft core
    CORRUGATED_METAL = auto()   # Corrugated metal gasket
    SOFT_CUT = auto()           # Rubber, PTFE, graphite sheet
    METALLIC_O_RING = auto()    # Metal O-ring (aerospace)
    C_RING = auto()             # C-ring gasket (pressure-energized)
    LENS_RING = auto()          # Lens ring (API 6A Type R)


class LoadingState(Enum):
    """Gasket loading state for hysteresis tracking."""
    LOADING = "loading"         # Compression increasing
    UNLOADING = "unloading"     # Compression decreasing (springback)
    NEUTRAL = "neutral"         # No change


# =============================================================================
# GASKET PROPERTIES
# =============================================================================

@dataclass
class GasketProperties:
    """
    Gasket-specific material and behavioral properties.

    Based on ASME PCC-1 Appendix O and EN 1591-1 gasket parameters.
    """
    gasket_type: GasketType = GasketType.SPIRAL_WOUND

    # Nonlinear stiffness parameters
    # k(F) = k₀ × (F/F_ref)^n_exp
    k_initial: float = 1e8          # Initial stiffness [N/m]
    k_loading: float = 1e8          # Loading stiffness [N/m]
    k_unloading: float = 2e8        # Unloading stiffness (higher - hysteresis) [N/m]
    n_exp: float = 0.3              # Nonlinearity exponent (0 = linear, 0.3 typical)

    # ASME gasket factors
    m_gasket_factor: float = 3.0    # ASME gasket factor (2.5-6.5)
    y_seating_stress: float = 69e6  # Minimum seating stress [Pa] (10-200 MPa)

    # Creep parameters (Norton-Bailey law)
    # ε_creep = A × σⁿ × tᵐ
    creep_coeff_A: float = 1e-10    # Creep coefficient [1/(Pa^n·s^m)]
    creep_stress_exp_n: float = 2.0 # Stress exponent
    creep_time_exp_m: float = 0.5   # Time exponent

    # Stress relaxation (Maxwell model)
    tau_relax: float = 3600.0       # Relaxation time constant [s] (1 hour typical)
    relax_fraction: float = 0.3     # Fraction of stress that relaxes (0-1)

    # Thickness and compression
    thickness_initial: float = 3e-3 # Initial gasket thickness [m]
    thickness_current: float = 3e-3 # Current thickness [m]
    max_compression: float = 0.5    # Maximum compression ratio (0-1)

    # Temperature effects
    temperature: float = 293.15     # Operating temperature [K]
    thermal_expansion_coeff: float = 2e-5  # Thermal expansion [1/K]

    # State tracking
    accumulated_creep: float = 0.0  # Total creep strain [-]
    stress_at_loading: float = 0.0  # Stress when loading started [Pa]
    time_under_load: float = 0.0    # Time at current load [s]

    def get_current_compression_ratio(self) -> float:
        """Calculate current compression ratio."""
        return 1.0 - (self.thickness_current / self.thickness_initial)

    def get_seating_force(self, contact_area: float) -> float:
        """
        Calculate minimum seating force from ASME y parameter.

        F_seat = y × A_gasket

        Args:
            contact_area: Gasket contact area [m²]

        Returns:
            Minimum seating force [N]
        """
        return self.y_seating_stress * contact_area

    def to_dict(self) -> Dict[str, Any]:
        return {
            "gasket_type": self.gasket_type.name,
            "k_initial": self.k_initial,
            "k_loading": self.k_loading,
            "k_unloading": self.k_unloading,
            "n_exp": self.n_exp,
            "m_gasket_factor": self.m_gasket_factor,
            "y_seating_stress": self.y_seating_stress,
            "creep_coeff_A": self.creep_coeff_A,
            "creep_stress_exp_n": self.creep_stress_exp_n,
            "creep_time_exp_m": self.creep_time_exp_m,
            "tau_relax": self.tau_relax,
            "relax_fraction": self.relax_fraction,
            "thickness_initial": self.thickness_initial,
            "thickness_current": self.thickness_current,
            "max_compression": self.max_compression,
            "temperature": self.temperature,
            "accumulated_creep": self.accumulated_creep,
            "time_under_load": self.time_under_load,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GasketProperties':
        data = data.copy()
        if 'gasket_type' in data and isinstance(data['gasket_type'], str):
            data['gasket_type'] = GasketType[data['gasket_type']]
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


# =============================================================================
# GASKET CONTACT CLASS
# =============================================================================

class FlangeGasketContact(Contact):
    """
    Flange-gasket interface contact with complex nonlinear behavior.

    KEY CHARACTERISTICS:
    - Nonlinear stiffness: k(F) or k(δ) with hysteresis
    - Creep under sustained compression (primary loosening mechanism)
    - Stress relaxation reduces preload over time
    - Loading/unloading paths differ (hysteresis loop)
    - Critical for gasketed joint preload loss

    MATRIX CONTRIBUTIONS:
    - [K]: Nonlinear stiffness (tangent stiffness updated each step)
    - [C]: Viscoelastic damping (creep + relaxation equivalent)
    - {F}: Nonlinear force-displacement relationship

    PRELOAD LOSS MECHANISMS:
    1. Creep: δ_creep = ∫ A × σⁿ × tᵐ dt
    2. Stress relaxation: F(t) = F₀ × exp(-t/τ)
    3. Thermal expansion mismatch
    """

    def __init__(self,
                 contact_id: str,
                 dof_flange_top: int,
                 dof_flange_bottom: int,
                 gasket_props: GasketProperties,
                 geometry: ContactGeometry,
                 friction: FrictionProperties,
                 wear: WearProperties):
        """
        Initialize gasket contact.

        Args:
            contact_id: Unique identifier
            dof_flange_top: Top flange axial DOF
            dof_flange_bottom: Bottom flange axial DOF
            gasket_props: Gasket material properties
            geometry: Gasket geometry (contact area, thickness)
            friction: Friction properties (lateral slip)
            wear: Wear properties (embedding)
        """
        # Initial stiffness (will be updated based on state)
        stiff = StiffnessProperties(
            stiffness_model=StiffnessModelType.ELASTOPLASTIC,
            k_axial=gasket_props.k_initial,
            k_loading_factor=1.0,
            k_unloading_factor=gasket_props.k_unloading / gasket_props.k_loading,
            E_instantaneous=gasket_props.k_initial * gasket_props.thickness_initial / geometry.contact_area,
            tau_relax=gasket_props.tau_relax
        )

        # Gasket damping (viscoelastic)
        damp = DampingProperties(
            damping_ratio=0.05,  # Higher than metal contacts
            c_viscous=0.0
        )

        super().__init__(
            contact_id=contact_id,
            contact_type="GASKET",
            node_i=dof_flange_top,
            node_j=dof_flange_bottom,
            geometry=geometry,
            friction=friction,
            wear=wear,
            stiffness=stiff,
            damping=damp
        )

        self.gasket = gasket_props
        self.loading_state = LoadingState.NEUTRAL

        # State tracking
        self.compression_prev = 0.0         # Previous compression [m]
        self.force_prev = 0.0               # Previous force [N]
        self.creep_displacement = 0.0       # Cumulative creep displacement [m]
        self.relaxation_force_loss = 0.0    # Force lost to relaxation [N]

        # For hysteresis tracking
        self.loading_curve_points: List[Tuple[float, float]] = []  # (δ, F) pairs
        self.unloading_curve_points: List[Tuple[float, float]] = []

    def get_stiffness_contribution(self) -> List[Tuple[int, int, float]]:
        """
        Gasket stiffness contributions (tangent stiffness).

        Updates tangent stiffness based on current loading state and force level.
        """
        # Update tangent stiffness based on current state
        k_tangent = self._calculate_tangent_stiffness()

        # Store in stiffness property for matrix assembly
        self.stiffness.k_axial = k_tangent

        return self.get_basic_stiffness_contribution()

    def get_damping_contribution(self) -> List[Tuple[int, int, float]]:
        """
        Gasket damping (viscoelastic + creep equivalent).
        """
        # Add equivalent viscous damping for creep
        c_creep_equiv = self._calculate_creep_equivalent_damping()
        self.damping.c_viscous = c_creep_equiv

        return self.get_basic_damping_contribution(mass_eff=0.1)

    def get_force_contribution(self, x: np.ndarray, x_dot: np.ndarray,
                               t: float) -> np.ndarray:
        """
        Gasket nonlinear force contribution.

        Computes force from:
        1. Nonlinear elastic response: F = f(δ, loading_state)
        2. Creep forces (time-dependent)
        3. Stress relaxation (force decay)

        Args:
            x: Displacement vector
            x_dot: Velocity vector
            t: Current time

        Returns:
            Force vector contribution
        """
        n_dof = len(x)
        F_vec = np.zeros(n_dof)

        i, j = self.node_i, self.node_j

        # Get relative compression
        if j >= 0 and j < n_dof:
            delta = x[i] - x[j]  # Relative compression
        else:
            delta = x[i]

        # Calculate nonlinear gasket force
        F_gasket = self._calculate_nonlinear_force(delta)

        # Apply to nodes
        F_vec[i] += F_gasket
        if j >= 0 and j < n_dof:
            F_vec[j] -= F_gasket

        return F_vec

    def _calculate_tangent_stiffness(self) -> float:
        """
        Calculate tangent stiffness based on loading state and force level.

        Returns:
            Tangent stiffness [N/m]
        """
        if self.loading_state == LoadingState.LOADING:
            k_base = self.gasket.k_loading
        else:
            k_base = self.gasket.k_unloading

        # Nonlinear correction: k(F) = k₀ × (F/F_ref)^(n-1) × n
        if abs(self.force_prev) > 1.0:
            F_ref = self.gasket.get_seating_force(self.geometry.contact_area)
            if F_ref > 0:
                force_ratio = abs(self.force_prev) / F_ref
                k_tangent = k_base * (force_ratio ** (self.gasket.n_exp - 1)) * self.gasket.n_exp
            else:
                k_tangent = k_base
        else:
            k_tangent = k_base

        return max(k_tangent, k_base * 0.1)  # Minimum 10% of base stiffness

    def _calculate_nonlinear_force(self, delta: float) -> float:
        """
        Calculate nonlinear gasket force from compression.

        F(δ) = k × δ^(1+n) for n > 0 (power law)

        Args:
            delta: Compression displacement [m]

        Returns:
            Gasket force [N]
        """
        # Determine loading state
        if delta > self.compression_prev:
            self.loading_state = LoadingState.LOADING
            k = self.gasket.k_loading
        elif delta < self.compression_prev:
            self.loading_state = LoadingState.UNLOADING
            k = self.gasket.k_unloading
        else:
            self.loading_state = LoadingState.NEUTRAL
            k = self.gasket.k_loading

        # Nonlinear force law: F = k × δ^(1+n)
        if abs(delta) > 1e-10:
            exponent = 1.0 + self.gasket.n_exp
            F = k * (abs(delta) ** exponent) * np.sign(delta)
        else:
            F = k * delta

        # Store for next step
        self.compression_prev = delta
        self.force_prev = F

        return F

    def _calculate_creep_equivalent_damping(self) -> float:
        """
        Calculate equivalent viscous damping for creep behavior.

        Returns:
            Equivalent damping coefficient [N·s/m]
        """
        if self.gasket.time_under_load < 1.0:
            return 0.0

        # Simplified: c_equiv = k × τ_creep
        tau_creep = self.gasket.tau_relax * 0.1  # Creep time scale
        c_equiv = self.stiffness.k_axial * tau_creep / 100.0

        return c_equiv

    def update_creep(self, dt: float):
        """
        Update creep deformation using Norton-Bailey law.

        ε_creep(t) = A × σⁿ × tᵐ

        Args:
            dt: Time step [s]
        """
        if self.normal_force < 1.0:
            return

        # Update time under load
        self.gasket.time_under_load += dt

        # Calculate stress
        sigma = self.normal_force / self.geometry.contact_area if self.geometry.contact_area > 0 else 0

        # Norton-Bailey creep strain rate
        # dε/dt = A × σⁿ × m × t^(m-1)
        if self.gasket.time_under_load > 0:
            creep_rate = (self.gasket.creep_coeff_A *
                         (sigma ** self.gasket.creep_stress_exp_n) *
                         self.gasket.creep_time_exp_m *
                         (self.gasket.time_under_load ** (self.gasket.creep_time_exp_m - 1)))

            # Creep displacement increment
            d_creep = creep_rate * self.gasket.thickness_current * dt
            self.creep_displacement += d_creep
            self.gasket.accumulated_creep += creep_rate * dt

            # Update gasket thickness
            self.gasket.thickness_current = self.gasket.thickness_initial * (1 - self.gasket.accumulated_creep)

            # Ensure physical limits
            min_thickness = self.gasket.thickness_initial * (1 - self.gasket.max_compression)
            self.gasket.thickness_current = max(self.gasket.thickness_current, min_thickness)

    def update_stress_relaxation(self, dt: float):
        """
        Update stress relaxation using exponential decay.

        F(t) = F₀ × [1 - r × (1 - exp(-t/τ))]

        where r = relaxation fraction (0-1)

        Args:
            dt: Time step [s]
        """
        if self.normal_force < 1.0 or self.gasket.tau_relax <= 0:
            return

        # Relaxation factor for this time step
        decay = self.gasket.relax_fraction * (1 - np.exp(-dt / self.gasket.tau_relax))

        # Force loss this step
        dF_relax = self.normal_force * decay
        self.relaxation_force_loss += dF_relax

    def get_preload_loss(self, system_stiffness: float) -> float:
        """
        Calculate total preload loss from gasket behavior.

        Includes:
        1. Creep displacement
        2. Stress relaxation
        3. Wear (embedding)

        Args:
            system_stiffness: Joint stiffness [N/m]

        Returns:
            Total preload loss [N]
        """
        # Preload loss from creep
        loss_creep = system_stiffness * self.creep_displacement

        # Preload loss from stress relaxation
        loss_relax = self.relaxation_force_loss

        # Preload loss from wear/embedding
        loss_wear = self.wear.get_preload_loss(system_stiffness)

        return loss_creep + loss_relax + loss_wear

    def get_gasket_summary(self) -> Dict[str, Any]:
        """
        Get gasket state summary for analysis.

        Returns:
            Dictionary with gasket state data
        """
        return {
            "gasket_type": self.gasket.gasket_type.name,
            "loading_state": self.loading_state.value,
            "compression_ratio": self.gasket.get_current_compression_ratio(),
            "current_thickness_mm": self.gasket.thickness_current * 1e3,
            "creep_displacement_um": self.creep_displacement * 1e6,
            "accumulated_creep_strain": self.gasket.accumulated_creep,
            "relaxation_force_loss_N": self.relaxation_force_loss,
            "time_under_load_hrs": self.gasket.time_under_load / 3600.0,
            "tangent_stiffness_MN_m": self.stiffness.k_axial / 1e6,
        }

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "contact_id": self.id,
            "contact_type": self.type,
            "dof_flange_top": self.node_i,
            "dof_flange_bottom": self.node_j,
            "gasket_properties": self.gasket.to_dict(),
            "geometry": self.geometry.to_dict(),
            "friction": self.friction.to_dict(),
            "wear": self.wear.to_dict(),
            "stiffness": self.stiffness.to_dict(),
            "damping": self.damping.to_dict(),
            "loading_state": self.loading_state.value,
            "creep_displacement": self.creep_displacement,
            "relaxation_force_loss": self.relaxation_force_loss,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FlangeGasketContact':
        """Deserialize from dictionary."""
        gasket_props = GasketProperties.from_dict(data["gasket_properties"])
        geometry = ContactGeometry.from_dict(data["geometry"])
        friction = FrictionProperties.from_dict(data["friction"])
        wear = WearProperties.from_dict(data["wear"])

        contact = cls(
            contact_id=data["contact_id"],
            dof_flange_top=data["dof_flange_top"],
            dof_flange_bottom=data["dof_flange_bottom"],
            gasket_props=gasket_props,
            geometry=geometry,
            friction=friction,
            wear=wear
        )

        contact.loading_state = LoadingState(data.get("loading_state", "neutral"))
        contact.creep_displacement = data.get("creep_displacement", 0.0)
        contact.relaxation_force_loss = data.get("relaxation_force_loss", 0.0)

        return contact


# =============================================================================
# FACTORY FUNCTIONS
# =============================================================================

def create_spiral_wound_gasket_contact(
    dof_flange_top: int,
    dof_flange_bottom: int,
    inner_diameter: float,
    outer_diameter: float,
    thickness: float = 4.5e-3,
    material: str = "316SS_GRAPHITE"
) -> FlangeGasketContact:
    """
    Create spiral wound gasket contact (ASME B16.20).

    Args:
        dof_flange_top: Top flange DOF
        dof_flange_bottom: Bottom flange DOF
        inner_diameter: Gasket ID [m]
        outer_diameter: Gasket OD [m]
        thickness: Gasket thickness [m] (4.5mm typical)
        material: "316SS_GRAPHITE" or "316SS_PTFE"

    Returns:
        FlangeGasketContact instance
    """
    geometry = ContactGeometry(
        inner_radius=inner_diameter / 2,
        outer_radius=outer_diameter / 2,
        thickness=thickness,
        roughness_Ra=3.2e-6  # 125 μin finish typical
    )

    # Spiral wound parameters (from ASME PCC-1)
    if material == "316SS_PTFE":
        m_factor = 2.5
        y_stress = 40e6  # 40 MPa
    else:  # 316SS_GRAPHITE (default)
        m_factor = 3.0
        y_stress = 69e6  # 69 MPa (10 ksi)

    gasket_props = GasketProperties(
        gasket_type=GasketType.SPIRAL_WOUND,
        k_initial=2e8,
        k_loading=2e8,
        k_unloading=5e8,  # ~2.5x loading stiffness
        n_exp=0.3,
        m_gasket_factor=m_factor,
        y_seating_stress=y_stress,
        creep_coeff_A=5e-11,
        creep_stress_exp_n=2.5,
        creep_time_exp_m=0.3,
        tau_relax=7200.0,  # 2 hours
        relax_fraction=0.15,
        thickness_initial=thickness,
        thickness_current=thickness,
        max_compression=0.5
    )

    friction = FrictionProperties(
        mu_static=0.20,
        mu_kinetic=0.18,
        mu_current=0.20
    )

    wear = WearProperties(
        wear_coeff_K=1e-5,  # Soft material, higher wear
        hardness=200e6  # Graphite/PTFE effective hardness
    )

    return FlangeGasketContact(
        contact_id="gasket_spiral_wound",
        dof_flange_top=dof_flange_top,
        dof_flange_bottom=dof_flange_bottom,
        gasket_props=gasket_props,
        geometry=geometry,
        friction=friction,
        wear=wear
    )


def create_rtj_gasket_contact(
    dof_flange_top: int,
    dof_flange_bottom: int,
    ring_diameter: float,
    ring_cross_section: float = 0.006,  # R-ring ~6mm cross section
    material: str = "INCONEL_625"
) -> FlangeGasketContact:
    """
    Create Ring Type Joint (RTJ) gasket contact (API 6A).

    Args:
        dof_flange_top: Top flange DOF
        dof_flange_bottom: Bottom flange DOF
        ring_diameter: Ring pitch diameter [m]
        ring_cross_section: Ring cross section diameter [m]
        material: "INCONEL_625", "316SS", or "SOFT_IRON"

    Returns:
        FlangeGasketContact instance
    """
    # Effective contact area (line contact approximation)
    contact_width = ring_cross_section * 0.2  # ~20% of cross section width
    contact_area = np.pi * ring_diameter * contact_width

    geometry = ContactGeometry(
        inner_radius=ring_diameter / 2 - ring_cross_section / 2,
        outer_radius=ring_diameter / 2 + ring_cross_section / 2,
        contact_area=contact_area,
        thickness=ring_cross_section,
        roughness_Ra=0.8e-6  # 32 μin finish
    )

    # RTJ parameters (metallic, high seating stress)
    if material == "SOFT_IRON":
        m_factor = 5.5
        y_stress = 310e6  # 45 ksi
        k_load = 1e10
    elif material == "316SS":
        m_factor = 6.0
        y_stress = 400e6  # 58 ksi
        k_load = 1.5e10
    else:  # INCONEL_625 (default)
        m_factor = 6.5
        y_stress = 450e6  # 65 ksi
        k_load = 2e10

    gasket_props = GasketProperties(
        gasket_type=GasketType.RTJ,
        k_initial=k_load,
        k_loading=k_load,
        k_unloading=k_load * 1.2,  # Less hysteresis than soft gaskets
        n_exp=0.15,  # More linear
        m_gasket_factor=m_factor,
        y_seating_stress=y_stress,
        creep_coeff_A=1e-12,  # Low creep (metallic)
        creep_stress_exp_n=3.0,
        creep_time_exp_m=0.2,
        tau_relax=36000.0,  # 10 hours (slow relaxation)
        relax_fraction=0.05,  # Minimal relaxation
        thickness_initial=ring_cross_section,
        thickness_current=ring_cross_section,
        max_compression=0.15  # Limited compression
    )

    friction = FrictionProperties(
        mu_static=0.25,
        mu_kinetic=0.22,
        mu_current=0.25
    )

    wear = WearProperties(
        wear_coeff_K=5e-7,
        hardness=2.5e9  # Steel hardness
    )

    return FlangeGasketContact(
        contact_id="gasket_rtj",
        dof_flange_top=dof_flange_top,
        dof_flange_bottom=dof_flange_bottom,
        gasket_props=gasket_props,
        geometry=geometry,
        friction=friction,
        wear=wear
    )
