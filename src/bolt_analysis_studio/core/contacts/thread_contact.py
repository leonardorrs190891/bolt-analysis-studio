"""
Thread Contact Implementation with Helix Coupling and Per-Thread Analysis.

Models the stud-nut thread interface as a parallel array of individual thread elements,
each with independent properties and contributing to rotational loosening.

Key Features:
- Parallel thread MSD array (n engaged threads)
- 5 load distribution laws (Equal, Linear, Power, Exponential, Yamamoto)
- Helix coupling between axial and torsional DOFs: Δx = (p/2π) × Δθ
- Per-thread friction and wear tracking
- Loosening angle computation

Based on MSD_Part_II_Contact_Elements.md Section 4.
"""

from dataclasses import dataclass
from enum import Enum, auto
from typing import List, Tuple, Optional, Dict, Any
import numpy as np

from .base import (
    Contact,
    ContactGeometry,
    FrictionProperties,
    WearProperties,
    WearModelType,
    StiffnessProperties,
    DampingProperties,
    SlipState,
)


# =============================================================================
# THREAD LOAD DISTRIBUTION LAWS
# =============================================================================

class ThreadLoadDistribution(Enum):
    """Thread load distribution models."""
    EQUAL = auto()          # φᵢ = 1/n
    LINEAR = auto()         # φᵢ = 2(n-i+1)/(n(n+1))
    POWER = auto()          # φᵢ = (n-i+1)^β / Σj^β
    EXPONENTIAL = auto()    # φᵢ = e^(-λ(i-1)) / Σe^(-λ(j-1))
    YAMAMOTO = auto()       # φᵢ = sinh(γ(n-i+0.5)) / Σsinh
    CUSTOM = auto()         # User-defined fractions


# =============================================================================
# THREAD GEOMETRY
# =============================================================================

@dataclass
class ThreadGeometry:
    """
    Complete thread geometry parameters.

    Includes dimensions, angles, and engagement parameters per ISO/ASME standards.
    """
    # Basic dimensions
    pitch: float                    # Thread pitch [m]
    major_diameter: float           # Major (nominal) diameter [m]
    minor_diameter: float           # Minor (root) diameter [m]
    pitch_diameter: float           # Pitch diameter [m]

    # Angular parameters
    flank_angle: float = np.radians(30)  # Half flank angle [rad] (30° for metric)

    # Engagement
    n_engaged_threads: int = 8      # Number of engaged threads

    # Optional thread profile
    thread_profile: str = "V_60"    # V_60, BUTTRESS, ACME, SQUARE

    @property
    def mean_radius(self) -> float:
        """Mean radius for friction calculations."""
        return self.pitch_diameter / 2

    @property
    def helix_angle(self) -> float:
        """Helix angle λ = arctan(p / (π·d₂)) [rad]."""
        return np.arctan(self.pitch / (np.pi * self.pitch_diameter))

    @property
    def helix_coupling_factor(self) -> float:
        """Helix coupling coefficient: p/(2π) [m/rad]."""
        return self.pitch / (2 * np.pi)

    @property
    def engagement_length(self) -> float:
        """Total engagement length [m]."""
        return self.n_engaged_threads * self.pitch

    @property
    def stress_area(self) -> float:
        """Effective stress area [m²]."""
        d_s = (self.pitch_diameter + self.minor_diameter) / 2
        return np.pi * d_s**2 / 4

    @property
    def thread_contact_area_per_thread(self) -> float:
        """Effective contact area per thread [m²]."""
        return np.pi * self.pitch_diameter * self.pitch * 0.5

    def to_dict(self) -> Dict[str, Any]:
        return {
            "pitch": self.pitch,
            "major_diameter": self.major_diameter,
            "minor_diameter": self.minor_diameter,
            "pitch_diameter": self.pitch_diameter,
            "flank_angle": self.flank_angle,
            "n_engaged_threads": self.n_engaged_threads,
            "thread_profile": self.thread_profile,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ThreadGeometry':
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


# =============================================================================
# THREAD CONTACT CLASS
# =============================================================================

class ThreadContact(Contact):
    """
    Thread contact between stud and nut with helix coupling.

    KEY CHARACTERISTICS:
    - Preload force acts through this contact
    - Helix couples axial and torsional motion: Δx = (p/2π) × Δθ
    - Critical for rotational loosening prediction
    - Load distribution across n engaged threads
    - Per-thread friction and wear tracking

    MATRIX CONTRIBUTIONS:
    - [K]: Axial stiffness + helix coupling terms (off-diagonal)
    - [C]: Thread friction viscous equivalent
    - {F}: Coulomb friction force + helix driving torque
    """

    def __init__(self,
                 contact_id: str,
                 dof_axial_stud: int,
                 dof_axial_nut: int,
                 dof_theta_stud: int,
                 dof_theta_nut: int,
                 thread_geom: ThreadGeometry,
                 friction: FrictionProperties,
                 wear: WearProperties,
                 load_distribution: ThreadLoadDistribution = ThreadLoadDistribution.POWER,
                 distribution_param: float = 2.0):
        """
        Initialize thread contact.

        Args:
            contact_id: Unique identifier
            dof_axial_stud: Stud axial DOF index
            dof_axial_nut: Nut axial DOF index
            dof_theta_stud: Stud torsional DOF index
            dof_theta_nut: Nut torsional DOF index
            thread_geom: Thread geometry parameters
            friction: Friction properties
            wear: Wear properties
            load_distribution: Load distribution law
            distribution_param: Parameter for distribution law (β, λ, or γ)
        """
        # Base geometry for contact
        geom = ContactGeometry(
            inner_radius=thread_geom.minor_diameter / 2,
            outer_radius=thread_geom.major_diameter / 2,
            contact_area=thread_geom.thread_contact_area_per_thread * thread_geom.n_engaged_threads
        )

        # Thread stiffness (simplified per VDI 2230)
        E_steel = 205e9  # Pa
        L_engaged = thread_geom.engagement_length
        A_stress = thread_geom.stress_area
        k_thread = E_steel * A_stress / L_engaged

        stiff = StiffnessProperties(
            k_axial=k_thread,
            k_torsional=0.0  # Torsion through helix coupling
        )

        damp = DampingProperties(damping_ratio=0.03)

        super().__init__(
            contact_id=contact_id,
            contact_type="THREAD",
            node_i=dof_axial_stud,
            node_j=dof_axial_nut,
            geometry=geom,
            friction=friction,
            wear=wear,
            stiffness=stiff,
            damping=damp
        )

        self.thread = thread_geom
        self.dof_theta_stud = dof_theta_stud
        self.dof_theta_nut = dof_theta_nut

        # Load distribution
        self.load_distribution_law = load_distribution
        self.distribution_param = distribution_param
        self.load_fractions = self._calculate_load_fractions()

        # Per-thread state tracking
        self.n_threads = thread_geom.n_engaged_threads
        self.per_thread_friction = [friction.mu_current] * self.n_threads
        self.per_thread_wear_depth = [0.0] * self.n_threads
        self.per_thread_slip_distance = [0.0] * self.n_threads

        # Rotational inertia and timestep (L4: configurable, not hardcoded)
        # Estimate nut inertia from geometry: J = 0.5*m*r² (approximate)
        nut_mass = 0.05  # Default nut mass [kg] - overridden by set_integration_params()
        r_nut = thread_geom.major_diameter  # Approximate outer radius
        self.J_nut = 0.5 * nut_mass * r_nut**2  # [kg·m²]
        self.dt_integration = None  # Set by solver when available

        # Loosening state
        self.theta_loosening = 0.0      # Cumulative loosening angle [rad]
        self.theta_loosening_deg = 0.0  # Cumulative loosening angle [deg]
        self.preload_loss_from_rotation = 0.0

    def _calculate_load_fractions(self) -> np.ndarray:
        """
        Calculate load fraction φᵢ for each thread based on distribution law.

        Returns:
            Array of n load fractions that sum to 1.0
        """
        n = self.thread.n_engaged_threads
        i_array = np.arange(1, n + 1)  # Thread indices 1 to n

        if self.load_distribution_law == ThreadLoadDistribution.EQUAL:
            # φᵢ = 1/n
            fractions = np.ones(n) / n

        elif self.load_distribution_law == ThreadLoadDistribution.LINEAR:
            # φᵢ = 2(n-i+1)/(n(n+1))
            fractions = 2 * (n - i_array + 1) / (n * (n + 1))

        elif self.load_distribution_law == ThreadLoadDistribution.POWER:
            # φᵢ = (n-i+1)^β / Σj^β
            beta = self.distribution_param
            weights = (n - i_array + 1) ** beta
            fractions = weights / np.sum(weights)

        elif self.load_distribution_law == ThreadLoadDistribution.EXPONENTIAL:
            # φᵢ = e^(-λ(i-1)) / Σe^(-λ(j-1))
            lambda_param = self.distribution_param
            weights = np.exp(-lambda_param * (i_array - 1))
            fractions = weights / np.sum(weights)

        elif self.load_distribution_law == ThreadLoadDistribution.YAMAMOTO:
            # φᵢ = sinh(γ(n-i+0.5)) / Σsinh
            gamma = self.distribution_param
            weights = np.sinh(gamma * (n - i_array + 0.5))
            fractions = weights / np.sum(weights)

        else:  # CUSTOM or default
            fractions = np.ones(n) / n

        return fractions

    def get_stiffness_contribution(self) -> List[Tuple[int, int, float]]:
        """
        Thread stiffness contributions including helix coupling.

        Returns contributions for:
        1. Axial stiffness (stud ↔ nut)
        2. Helix coupling (axial ↔ torsional DOFs)

        Helix coupling matrix pattern:
        [K] contributions:
        - K[i_axial_stud, i_axial_nut] ± k_thread
        - K[i_axial_stud, j_theta_nut] ± k_thread × (p/2π)
        - K[j_theta_nut, i_axial_stud] ± k_thread × (p/2π)
        """
        k = self.stiffness.k_axial
        i_stud = self.node_i  # Axial DOF of stud
        i_nut = self.node_j   # Axial DOF of nut
        theta_stud = self.dof_theta_stud
        theta_nut = self.dof_theta_nut

        # Helix coupling coefficient
        lambda_helix = self.thread.helix_coupling_factor  # p/(2π) [m/rad]

        contributions = [
            # Axial stiffness (standard pattern)
            (i_stud, i_stud, k),
            (i_nut, i_nut, k),
            (i_stud, i_nut, -k),
            (i_nut, i_stud, -k),

            # Helix coupling: axial-torsional (CRITICAL FOR LOOSENING)
            (i_stud, theta_nut, k * lambda_helix),
            (theta_nut, i_stud, k * lambda_helix),
            (i_nut, theta_nut, -k * lambda_helix),
            (theta_nut, i_nut, -k * lambda_helix),
        ]

        return contributions

    def get_damping_contribution(self) -> List[Tuple[int, int, float]]:
        """
        Thread damping contributions.

        Includes:
        - Material damping: c = 2ζ√(km)
        - Viscous friction component
        """
        k = self.stiffness.k_axial
        m_eff = 0.01  # Effective mass (approximate)
        c_total = self.damping.get_damping(k, m_eff) + self.friction.viscous_coeff

        i_stud = self.node_i
        i_nut = self.node_j

        contributions = [
            (i_stud, i_stud, c_total),
            (i_nut, i_nut, c_total),
            (i_stud, i_nut, -c_total),
            (i_nut, i_stud, -c_total),
        ]

        return contributions

    def set_integration_params(self, J_nut: float = None, dt: float = None,
                               nut_mass: float = None):
        """
        Set integration parameters from model/solver.

        Args:
            J_nut: Nut rotational inertia [kg*m^2]. If None, computed from nut_mass.
            dt: Integration time step [s]. If None, estimated from stiffness/mass.
            nut_mass: Nut mass [kg] for inertia estimation.
        """
        if J_nut is not None:
            self.J_nut = J_nut
        elif nut_mass is not None:
            r_nut = self.thread.major_diameter
            self.J_nut = 0.5 * nut_mass * r_nut**2
        if dt is not None:
            self.dt_integration = dt

    def get_force_contribution(self, x: np.ndarray, x_dot: np.ndarray,
                               t: float) -> Tuple[np.ndarray, float]:
        """
        Thread force contributions including loosening mechanism.

        Forces computed:
        1. AXIAL FRICTION: F_t = μ_t × N × cos(α) × sign(v_axial)
        2. THREAD FRICTION TORQUE: T_t = μ_t × N × r_m × sign(ω)
        3. HELIX DRIVING TORQUE (during slip): T_helix = F_p × r_m × tan(λ)
           → This DRIVES loosening!

        Returns:
            Tuple of (force_vector, loosening_angle_increment [rad])
        """
        n_dof = len(x)
        F = np.zeros(n_dof)

        i_stud, i_nut = self.node_i, self.node_j
        theta_stud, theta_nut = self.dof_theta_stud, self.dof_theta_nut

        # Check if DOFs are valid
        if theta_nut >= n_dof or theta_stud >= n_dof:
            return F, 0.0

        # Relative velocities
        v_axial_stud_nut = x_dot[i_stud] - x_dot[i_nut] if i_nut >= 0 and i_nut < n_dof else x_dot[i_stud]
        v_theta_nut = x_dot[theta_nut] if theta_nut < n_dof else 0.0
        v_theta_stud = x_dot[theta_stud] if theta_stud < n_dof else 0.0
        v_theta_rel = v_theta_nut - v_theta_stud

        # Thread parameters
        mu = self.friction.mu_current
        N = self.normal_force  # Preload
        r_m = self.thread.mean_radius
        alpha = self.thread.flank_angle
        lambda_h = self.thread.helix_angle

        # 1. Axial friction at threads
        F_friction_axial = self.friction.get_friction_force(v_axial_stud_nut, N * np.cos(alpha))
        F[i_stud] += F_friction_axial
        if i_nut >= 0 and i_nut < n_dof:
            F[i_nut] -= F_friction_axial

        # 2. Thread friction torque (RESISTS rotation)
        T_friction = self.friction.get_friction_force(v_theta_rel, N) * r_m
        F[theta_nut] += T_friction
        if theta_stud < n_dof:
            F[theta_stud] -= T_friction

        # 3. Check for loosening condition and compute helix torque
        dtheta_loosening = 0.0

        # Loosening occurs when bearing slip allows rotation
        # (This is checked externally by comparing with bearing friction)
        # If slip_state is GROSS_SLIP, compute helix driving torque

        if self.slip_state == SlipState.GROSS_SLIP:
            # Helix driving torque (DRIVES LOOSENING)
            T_helix = N * r_m * np.tan(lambda_h)

            # Net torque when in slip (helix torque minus friction)
            T_net = T_helix  # Friction is already at limit, overcome

            # Convert to rotation increment (simplified Euler)
            # Uses configurable inertia and timestep (L4 fix)
            dt = self.dt_integration if self.dt_integration is not None else 1e-4
            dtheta_loosening = T_net * dt / self.J_nut

            # Accumulate loosening
            self.theta_loosening += abs(dtheta_loosening)
            self.theta_loosening_deg = np.degrees(self.theta_loosening)

        return F, dtheta_loosening

    def update_per_thread_state(self, dt: float):
        """
        Update state for each individual thread.

        Tracks per-thread:
        - Friction coefficient evolution
        - Wear depth accumulation
        - Slip distance
        """
        for i in range(self.n_threads):
            # Load fraction for this thread
            phi_i = self.load_fractions[i]
            N_i = self.normal_force * phi_i

            # Slip distance (assume uniform for now)
            slip_i = abs(self.relative_velocity) * dt
            self.per_thread_slip_distance[i] += slip_i

            # Friction evolution (simple decay model)
            if self.friction.degradation_rate > 0:
                decay = np.exp(-self.friction.degradation_rate * self.cycles)
                self.per_thread_friction[i] = self.friction.min_friction + \
                    (self.friction.mu_static - self.friction.min_friction) * decay

            # Wear accumulation per thread (Archard)
            if self.wear.wear_model.name == "ARCHARD":
                contact_area_i = self.thread.thread_contact_area_per_thread
                dV_i = self.wear.wear_coeff_K * N_i * slip_i / self.wear.hardness
                self.per_thread_wear_depth[i] += dV_i / contact_area_i if contact_area_i > 0 else 0

    def get_preload_loss_from_rotation(self, k_bolt: float) -> float:
        """
        Calculate preload loss from rotational loosening.

        ΔF_p = k_bolt × (p/2π) × θ_loosening

        Args:
            k_bolt: Bolt stiffness [N/m]

        Returns:
            Preload loss [N]
        """
        delta_axial = self.thread.helix_coupling_factor * self.theta_loosening
        return k_bolt * delta_axial

    def get_total_preload_loss(self, k_bolt: float, k_member: float) -> float:
        """
        Total preload loss from rotation and wear.

        Args:
            k_bolt: Bolt stiffness [N/m]
            k_member: Member stiffness [N/m]

        Returns:
            Total preload loss [N]
        """
        k_joint = 1 / (1/k_bolt + 1/k_member)

        loss_rotation = self.get_preload_loss_from_rotation(k_bolt)
        loss_wear = self.wear.get_preload_loss(k_joint)

        return loss_rotation + loss_wear

    def get_per_thread_summary(self) -> Dict[str, Any]:
        """
        Get summary of per-thread state for analysis.

        Returns:
            Dictionary with per-thread data
        """
        return {
            "load_fractions": self.load_fractions.tolist(),
            "friction_coefficients": self.per_thread_friction,
            "wear_depths_um": [d * 1e6 for d in self.per_thread_wear_depth],
            "slip_distances_mm": [s * 1e3 for s in self.per_thread_slip_distance],
            "total_loosening_deg": self.theta_loosening_deg,
        }

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "contact_id": self.id,
            "contact_type": self.type,
            "dof_axial_stud": self.node_i,
            "dof_axial_nut": self.node_j,
            "dof_theta_stud": self.dof_theta_stud,
            "dof_theta_nut": self.dof_theta_nut,
            "thread_geometry": self.thread.to_dict(),
            "friction": self.friction.to_dict(),
            "wear": self.wear.to_dict(),
            "stiffness": self.stiffness.to_dict(),
            "damping": self.damping.to_dict(),
            "load_distribution": self.load_distribution_law.name,
            "distribution_param": self.distribution_param,
            "theta_loosening_deg": self.theta_loosening_deg,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ThreadContact':
        """Deserialize from dictionary."""
        thread_geom = ThreadGeometry.from_dict(data["thread_geometry"])
        friction = FrictionProperties.from_dict(data["friction"])
        wear = WearProperties.from_dict(data["wear"])

        load_dist = ThreadLoadDistribution[data.get("load_distribution", "POWER")]

        return cls(
            contact_id=data["contact_id"],
            dof_axial_stud=data["dof_axial_stud"],
            dof_axial_nut=data["dof_axial_nut"],
            dof_theta_stud=data["dof_theta_stud"],
            dof_theta_nut=data["dof_theta_nut"],
            thread_geom=thread_geom,
            friction=friction,
            wear=wear,
            load_distribution=load_dist,
            distribution_param=data.get("distribution_param", 2.0),
        )


# =============================================================================
# FACTORY FUNCTIONS
# =============================================================================

def create_standard_thread_contact(
    bolt_size: str,
    dof_axial_stud: int,
    dof_axial_nut: int,
    dof_theta_stud: int,
    dof_theta_nut: int,
    mu_thread: float = 0.12,   # Phase 2.1: should match model.mu_initial; caller overrides
    wear_coeff: float = 1e-6
) -> ThreadContact:
    """
    Create thread contact for standard bolt sizes.

    Args:
        bolt_size: Standard designation (e.g., "M20", "M24", "1-8 UNC")
        dof_axial_stud: Stud axial DOF index
        dof_axial_nut: Nut axial DOF index
        dof_theta_stud: Stud torsional DOF index
        dof_theta_nut: Nut torsional DOF index
        mu_thread: Thread friction coefficient
        wear_coeff: Archard wear coefficient

    Returns:
        ThreadContact instance
    """
    # Standard metric thread data (ISO 724)
    thread_data = {
        'M10': ThreadGeometry(
            pitch=0.0015,
            major_diameter=0.010,
            minor_diameter=0.00838,
            pitch_diameter=0.00913,
            n_engaged_threads=6
        ),
        'M12': ThreadGeometry(
            pitch=0.00175,
            major_diameter=0.012,
            minor_diameter=0.01004,
            pitch_diameter=0.01098,
            n_engaged_threads=7
        ),
        'M16': ThreadGeometry(
            pitch=0.002,
            major_diameter=0.016,
            minor_diameter=0.01373,
            pitch_diameter=0.01480,
            n_engaged_threads=8
        ),
        'M20': ThreadGeometry(
            pitch=0.0025,
            major_diameter=0.020,
            minor_diameter=0.01727,
            pitch_diameter=0.01854,
            n_engaged_threads=8
        ),
        'M24': ThreadGeometry(
            pitch=0.003,
            major_diameter=0.024,
            minor_diameter=0.02080,
            pitch_diameter=0.02227,
            n_engaged_threads=8
        ),
        'M30': ThreadGeometry(
            pitch=0.0035,
            major_diameter=0.030,
            minor_diameter=0.02589,
            pitch_diameter=0.02773,
            n_engaged_threads=10
        ),
    }

    geom = thread_data.get(bolt_size, thread_data['M20'])

    friction = FrictionProperties(
        mu_static=mu_thread,
        mu_kinetic=mu_thread * 0.9,
        mu_current=mu_thread,
        degradation_rate=1e-5,
        min_friction=0.05
    )

    wear = WearProperties(
        wear_model=WearModelType.FRETTING,
        wear_coeff_K=wear_coeff,
        fretting_coeff=wear_coeff * 10
    )

    return ThreadContact(
        contact_id=f"thread_{bolt_size}",
        dof_axial_stud=dof_axial_stud,
        dof_axial_nut=dof_axial_nut,
        dof_theta_stud=dof_theta_stud,
        dof_theta_nut=dof_theta_nut,
        thread_geom=geom,
        friction=friction,
        wear=wear,
        load_distribution=ThreadLoadDistribution.POWER,
        distribution_param=2.0  # β = 2 for typical steel bolts
    )
