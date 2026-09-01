"""
Washer Contact Implementation with Embedding Models.

Models washer-flange interface with:
- Embedding: plastic deformation of softer material into harder
- Time-dependent embedding: δ(t) = f_z × L × (1 - e^(-N/N_c))
- Preload loss from embedding
- Different washer types (plain, spring, Belleville, Nord-Lock)

Key Features:
- WasherType enum for different washer designs
- Embedding model with exponential saturation
- Time-dependent preload loss
- Spring washer nonlinear stiffness
- Belleville washer force-deflection curves

Based on VDI 2230 Part 1 Section 5.5.4 and experimental embedding data.
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
    StiffnessModelType,
    DampingProperties,
    SlipState,
)


# =============================================================================
# WASHER TYPE CLASSIFICATION
# =============================================================================

class WasherType(Enum):
    """Washer design types."""
    PLAIN = auto()              # Flat washer (ASME B18.21.1)
    SPRING = auto()             # Split spring washer
    BELLEVILLE = auto()         # Conical disc spring (DIN 2093)
    WAVE = auto()               # Wave washer
    NORD_LOCK = auto()          # Wedge-locking washer
    TENSION_INDICATING = auto()  # Squirter/DTI washer
    HARDENED = auto()           # Hardened flat washer


# =============================================================================
# WASHER PROPERTIES
# =============================================================================

@dataclass
class WasherProperties:
    """
    Washer-specific properties including embedding behavior.

    Based on VDI 2230 Part 1 and experimental embedding data.
    """
    washer_type: WasherType = WasherType.PLAIN

    # Material properties
    hardness: float = 200e6         # Vickers hardness [Pa] (HV to Pa)
    yield_strength: float = 300e6   # Yield strength [Pa]

    # Embedding parameters (VDI 2230 Section 5.5.4)
    # δ_embed = f_z × L_K × (1 - exp(-F_preload / F_critical))
    embedding_factor_fz: float = 0.1    # Embedding factor f_z (0.05-0.15)
    clamping_length_LK: float = 0.002   # Effective clamping length [m]
    critical_force_Fc: float = 50000.0  # Force where embedding saturates [N]

    # Time-dependent embedding
    # δ(t) = δ_0 × (1 + β × log(1 + t/t_0))
    time_constant_t0: float = 60.0      # Time constant [s] (1 minute)
    time_exponent_beta: float = 0.05    # Time dependency factor (0-0.1)

    # Belleville-specific (if applicable)
    belleville_height: float = 0.0      # Cone height [m]
    belleville_thickness: float = 0.0   # Disc thickness [m]

    # Spring washer stiffness (nonlinear)
    spring_stiffness_nominal: float = 0.0  # Nominal stiffness [N/m]
    spring_stiffness_compressed: float = 0.0  # Compressed stiffness [N/m]

    # State tracking
    total_embedding: float = 0.0        # Total embedding depth [m]
    elastic_deformation: float = 0.0    # Elastic compression [m]
    plastic_set: float = 0.0            # Permanent set [m]
    time_under_load: float = 0.0        # Time at load [s]

    def calculate_embedding(self, preload: float, time_under_load: float = 0.0) -> float:
        """
        Calculate embedding depth using VDI 2230 model.

        δ_embed = f_z × L_K × (1 - exp(-F / F_c)) × (1 + β × log(1 + t/t_0))

        Args:
            preload: Applied preload force [N]
            time_under_load: Time under load [s]

        Returns:
            Embedding depth [m]
        """
        # Initial embedding (load-dependent)
        if self.critical_force_Fc > 0:
            delta_initial = (self.embedding_factor_fz * self.clamping_length_LK *
                            (1 - np.exp(-preload / self.critical_force_Fc)))
        else:
            delta_initial = 0.0

        # Time-dependent increase
        if time_under_load > 0 and self.time_constant_t0 > 0:
            time_factor = 1 + self.time_exponent_beta * np.log(1 + time_under_load / self.time_constant_t0)
            delta_total = delta_initial * time_factor
        else:
            delta_total = delta_initial

        return delta_total

    def to_dict(self) -> Dict[str, Any]:
        return {
            "washer_type": self.washer_type.name,
            "hardness": self.hardness,
            "yield_strength": self.yield_strength,
            "embedding_factor_fz": self.embedding_factor_fz,
            "clamping_length_LK": self.clamping_length_LK,
            "critical_force_Fc": self.critical_force_Fc,
            "time_constant_t0": self.time_constant_t0,
            "time_exponent_beta": self.time_exponent_beta,
            "belleville_height": self.belleville_height,
            "belleville_thickness": self.belleville_thickness,
            "spring_stiffness_nominal": self.spring_stiffness_nominal,
            "spring_stiffness_compressed": self.spring_stiffness_compressed,
            "total_embedding": self.total_embedding,
            "time_under_load": self.time_under_load,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WasherProperties':
        data = data.copy()
        if 'washer_type' in data and isinstance(data['washer_type'], str):
            data['washer_type'] = WasherType[data['washer_type']]
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


# =============================================================================
# WASHER CONTACT CLASS
# =============================================================================

class WasherFlangeContact(Contact):
    """
    Washer-flange interface contact with embedding.

    KEY CHARACTERISTICS:
    - Embedding into softer material (plastic deformation)
    - Time-dependent preload loss
    - Nonlinear stiffness for spring/Belleville washers
    - Different behavior for plain vs. spring washers

    MATRIX CONTRIBUTIONS:
    - [K]: Stiffness (high for plain, nonlinear for spring/Belleville)
    - [C]: Low damping (metal contact)
    - {F}: Embedding forces (reduce preload over time)

    PRELOAD LOSS MECHANISM:
    δ_embed(t) → ΔF = k_joint × δ_embed
    Primary mechanism for plain washers: embedding
    Spring washers: elastic recovery helps maintain preload
    """

    def __init__(self,
                 contact_id: str,
                 dof_washer: int,
                 dof_flange: int,
                 washer_props: WasherProperties,
                 geometry: ContactGeometry,
                 friction: FrictionProperties,
                 wear: WearProperties):
        """
        Initialize washer-flange contact.

        Args:
            contact_id: Unique identifier
            dof_washer: Washer axial DOF
            dof_flange: Flange axial DOF
            washer_props: Washer properties
            geometry: Contact geometry
            friction: Friction properties
            wear: Wear properties
        """
        # Determine stiffness based on washer type
        if washer_props.washer_type == WasherType.PLAIN or washer_props.washer_type == WasherType.HARDENED:
            # High stiffness (metal contact)
            E_eff = 105e9  # Steel effective modulus
            A = geometry.calc_annular_area()
            t_eff = 0.001  # Washer thickness ~1mm
            k_washer = E_eff * A / t_eff if t_eff > 0 else 1e10
            stiff_model = StiffnessModelType.LINEAR

        elif washer_props.washer_type == WasherType.BELLEVILLE:
            # Belleville washer stiffness (nonlinear)
            k_washer = self._calculate_belleville_stiffness(washer_props, geometry)
            stiff_model = StiffnessModelType.NONLINEAR_ELASTIC

        elif washer_props.washer_type == WasherType.SPRING or washer_props.washer_type == WasherType.WAVE:
            # Spring washer (lower stiffness)
            k_washer = washer_props.spring_stiffness_nominal if washer_props.spring_stiffness_nominal > 0 else 5e7
            stiff_model = StiffnessModelType.NONLINEAR_ELASTIC

        else:
            # Default
            k_washer = 1e9
            stiff_model = StiffnessModelType.LINEAR

        stiff = StiffnessProperties(
            stiffness_model=stiff_model,
            k_axial=k_washer
        )

        damp = DampingProperties(
            damping_ratio=0.01,  # Low damping
            c_viscous=0.0
        )

        super().__init__(
            contact_id=contact_id,
            contact_type=f"WASHER_{washer_props.washer_type.name}",
            node_i=dof_washer,
            node_j=dof_flange,
            geometry=geometry,
            friction=friction,
            wear=wear,
            stiffness=stiff,
            damping=damp
        )

        self.washer = washer_props

        # State tracking
        self.embedding_prev = 0.0
        self.force_prev = 0.0

    def _calculate_belleville_stiffness(self, washer_props: WasherProperties,
                                       geometry: ContactGeometry) -> float:
        """
        Calculate Belleville washer stiffness from geometry.

        k = (4 × E × t³) / [(1 - ν²) × D² × (h - δ/2) × (h - δ) / δ]

        Simplified for initial loading.

        Args:
            washer_props: Washer properties
            geometry: Contact geometry

        Returns:
            Stiffness [N/m]
        """
        E = 205e9  # Steel modulus
        nu = 0.3   # Poisson's ratio
        t = washer_props.belleville_thickness
        D = geometry.outer_radius * 2  # Outer diameter
        h = washer_props.belleville_height

        if h > 0 and t > 0 and D > 0:
            # Simplified stiffness at half deflection
            k = (4 * E * t**3) / ((1 - nu**2) * D**2 * h)
            return k
        else:
            return 1e9  # Default

    def get_stiffness_contribution(self) -> List[Tuple[int, int, float]]:
        """
        Washer stiffness contribution.

        Updates stiffness if nonlinear (Belleville, spring).
        """
        # Update tangent stiffness if nonlinear
        if self.stiffness.stiffness_model != StiffnessModelType.LINEAR:
            k_tangent = self._calculate_tangent_stiffness()
            self.stiffness.k_axial = k_tangent

        return self.get_basic_stiffness_contribution()

    def get_damping_contribution(self) -> List[Tuple[int, int, float]]:
        """
        Washer damping (low - metal contact).
        """
        return self.get_basic_damping_contribution(mass_eff=0.01)

    def get_force_contribution(self, x: np.ndarray, x_dot: np.ndarray,
                               t: float) -> np.ndarray:
        """
        Washer force contribution (includes nonlinear effects).

        Args:
            x: Displacement vector
            x_dot: Velocity vector
            t: Current time

        Returns:
            Force vector contribution
        """
        n_dof = len(x)
        F = np.zeros(n_dof)

        i, j = self.node_i, self.node_j

        # Get relative compression
        if j >= 0 and j < n_dof:
            delta = x[i] - x[j]
        else:
            delta = x[i]

        # Nonlinear force for Belleville/spring washers
        if self.washer.washer_type == WasherType.BELLEVILLE:
            F_washer = self._calculate_belleville_force(delta)
        else:
            # Linear force
            F_washer = self.stiffness.k_axial * delta

        # Apply forces
        F[i] += F_washer
        if j >= 0 and j < n_dof:
            F[j] -= F_washer

        self.force_prev = F_washer

        return F

    def _calculate_tangent_stiffness(self) -> float:
        """
        Calculate tangent stiffness for nonlinear washers.

        Returns:
            Tangent stiffness [N/m]
        """
        # Simplified: use nominal stiffness with load correction
        if self.washer.washer_type == WasherType.SPRING:
            # Spring washer stiffens as it compresses
            if self.force_prev > 0:
                return self.washer.spring_stiffness_compressed
            else:
                return self.washer.spring_stiffness_nominal

        return self.stiffness.k_axial

    def _calculate_belleville_force(self, delta: float) -> float:
        """
        Calculate force from Belleville washer deflection.

        F = (4 × E × δ) / [(1 - ν²) × D²] × t³ × [(h - δ/2) / (h - δ)²]

        Args:
            delta: Deflection [m]

        Returns:
            Force [N]
        """
        E = 205e9
        nu = 0.3
        t = self.washer.belleville_thickness
        D = self.geometry.outer_radius * 2
        h = self.washer.belleville_height

        if h <= 0 or t <= 0 or D <= 0 or delta >= h:
            return 0.0

        # Belleville formula
        numerator = 4 * E * delta * t**3 * (h - delta / 2)
        denominator = (1 - nu**2) * D**2 * (h - delta)**2

        F = numerator / denominator if denominator > 0 else 0.0

        return F

    def update_embedding(self, dt: float):
        """
        Update embedding depth based on current load and time.

        Args:
            dt: Time step [s]
        """
        # Update time under load
        self.washer.time_under_load += dt

        # Calculate current embedding
        delta_embed = self.washer.calculate_embedding(
            self.normal_force,
            self.washer.time_under_load
        )

        # Store total embedding
        self.washer.total_embedding = delta_embed
        self.embedding_prev = delta_embed

    def get_preload_loss(self, system_stiffness: float) -> float:
        """
        Calculate preload loss from washer embedding.

        ΔF = k_joint × δ_embed

        Args:
            system_stiffness: Joint stiffness [N/m]

        Returns:
            Preload loss [N]
        """
        # Loss from embedding
        loss_embedding = system_stiffness * self.washer.total_embedding

        # Loss from wear (minor for washers)
        loss_wear = self.wear.get_preload_loss(system_stiffness)

        return loss_embedding + loss_wear

    def get_washer_summary(self) -> Dict[str, Any]:
        """
        Get washer state summary for analysis.

        Returns:
            Dictionary with washer state data
        """
        return {
            "washer_type": self.washer.washer_type.name,
            "total_embedding_um": self.washer.total_embedding * 1e6,
            "time_under_load_hrs": self.washer.time_under_load / 3600.0,
            "current_force_N": self.force_prev,
            "tangent_stiffness_MN_m": self.stiffness.k_axial / 1e6,
            "preload_loss_percentage": (self.get_preload_loss(self.stiffness.k_axial) /
                                       self.normal_force * 100 if self.normal_force > 0 else 0),
        }

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "contact_id": self.id,
            "contact_type": self.type,
            "dof_washer": self.node_i,
            "dof_flange": self.node_j,
            "washer_properties": self.washer.to_dict(),
            "geometry": self.geometry.to_dict(),
            "friction": self.friction.to_dict(),
            "wear": self.wear.to_dict(),
            "stiffness": self.stiffness.to_dict(),
            "damping": self.damping.to_dict(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WasherFlangeContact':
        """Deserialize from dictionary."""
        washer_props = WasherProperties.from_dict(data["washer_properties"])
        geometry = ContactGeometry.from_dict(data["geometry"])
        friction = FrictionProperties.from_dict(data["friction"])
        wear = WearProperties.from_dict(data["wear"])

        return cls(
            contact_id=data["contact_id"],
            dof_washer=data["dof_washer"],
            dof_flange=data["dof_flange"],
            washer_props=washer_props,
            geometry=geometry,
            friction=friction,
            wear=wear
        )


# =============================================================================
# FACTORY FUNCTIONS
# =============================================================================

def create_plain_washer_contact(
    dof_washer: int,
    dof_flange: int,
    inner_diameter: float,
    outer_diameter: float,
    washer_hardness: str = "STANDARD"
) -> WasherFlangeContact:
    """
    Create plain flat washer contact (ASME B18.21.1).

    Args:
        dof_washer: Washer DOF
        dof_flange: Flange DOF
        inner_diameter: Washer ID [m]
        outer_diameter: Washer OD [m]
        washer_hardness: "STANDARD", "HARDENED", or "SOFT"

    Returns:
        WasherFlangeContact instance
    """
    geometry = ContactGeometry(
        inner_radius=inner_diameter / 2,
        outer_radius=outer_diameter / 2,
        thickness=0.002,  # 2mm typical
        roughness_Ra=3.2e-6
    )

    # Embedding parameters depend on hardness
    if washer_hardness == "HARDENED":
        fz = 0.03  # Low embedding
        hardness = 500e6
        washer_type = WasherType.HARDENED
    elif washer_hardness == "SOFT":
        fz = 0.15  # High embedding
        hardness = 150e6
        washer_type = WasherType.PLAIN
    else:  # STANDARD
        fz = 0.08  # Medium embedding
        hardness = 200e6
        washer_type = WasherType.PLAIN

    washer_props = WasherProperties(
        washer_type=washer_type,
        hardness=hardness,
        embedding_factor_fz=fz,
        clamping_length_LK=0.002,
        critical_force_Fc=50000.0,
        time_constant_t0=60.0,
        time_exponent_beta=0.05
    )

    friction = FrictionProperties(
        mu_static=0.15,
        mu_kinetic=0.13,
        mu_current=0.15
    )

    wear = WearProperties(
        wear_model=WearModelType.ARCHARD,
        wear_coeff_K=5e-7,
        hardness=hardness
    )

    return WasherFlangeContact(
        contact_id="washer_plain",
        dof_washer=dof_washer,
        dof_flange=dof_flange,
        washer_props=washer_props,
        geometry=geometry,
        friction=friction,
        wear=wear
    )


def create_belleville_washer_contact(
    dof_washer: int,
    dof_flange: int,
    inner_diameter: float,
    outer_diameter: float,
    cone_height: float,
    thickness: float
) -> WasherFlangeContact:
    """
    Create Belleville disc spring washer contact (DIN 2093).

    Args:
        dof_washer: Washer DOF
        dof_flange: Flange DOF
        inner_diameter: Washer ID [m]
        outer_diameter: Washer OD [m]
        cone_height: Cone height h [m]
        thickness: Disc thickness t [m]

    Returns:
        WasherFlangeContact instance
    """
    geometry = ContactGeometry(
        inner_radius=inner_diameter / 2,
        outer_radius=outer_diameter / 2,
        thickness=thickness,
        roughness_Ra=1.6e-6  # Ground finish
    )

    washer_props = WasherProperties(
        washer_type=WasherType.BELLEVILLE,
        hardness=500e6,  # Hardened spring steel
        embedding_factor_fz=0.02,  # Low embedding (hardened)
        clamping_length_LK=thickness,
        critical_force_Fc=100000.0,
        time_constant_t0=600.0,  # Slower creep
        time_exponent_beta=0.02,
        belleville_height=cone_height,
        belleville_thickness=thickness
    )

    friction = FrictionProperties(
        mu_static=0.15,
        mu_kinetic=0.12,
        mu_current=0.15
    )

    wear = WearProperties(
        wear_model=WearModelType.NONE,  # Hardened, minimal wear
        wear_coeff_K=1e-8,
        hardness=500e6
    )

    return WasherFlangeContact(
        contact_id="washer_belleville",
        dof_washer=dof_washer,
        dof_flange=dof_flange,
        washer_props=washer_props,
        geometry=geometry,
        friction=friction,
        wear=wear
    )


def create_nord_lock_washer_contact(
    dof_washer: int,
    dof_flange: int,
    inner_diameter: float,
    outer_diameter: float
) -> WasherFlangeContact:
    """
    Create Nord-Lock wedge-locking washer contact.

    Args:
        dof_washer: Washer DOF
        dof_flange: Flange DOF
        inner_diameter: Washer ID [m]
        outer_diameter: Washer OD [m]

    Returns:
        WasherFlangeContact instance
    """
    geometry = ContactGeometry(
        inner_radius=inner_diameter / 2,
        outer_radius=outer_diameter / 2,
        thickness=0.003,  # 3mm typical
        roughness_Ra=3.2e-6
    )

    washer_props = WasherProperties(
        washer_type=WasherType.NORD_LOCK,
        hardness=450e6,  # Hardened
        embedding_factor_fz=0.02,  # Very low embedding (wedge effect)
        clamping_length_LK=0.003,
        critical_force_Fc=80000.0,
        time_constant_t0=3600.0,  # Slow relaxation
        time_exponent_beta=0.01   # Minimal time dependency
    )

    # Nord-Lock has high friction due to cam surfaces
    friction = FrictionProperties(
        mu_static=0.35,  # High friction from wedge
        mu_kinetic=0.30,
        mu_current=0.35,
        degradation_rate=0.0  # No degradation
    )

    wear = WearProperties(
        wear_model=WearModelType.NONE,
        wear_coeff_K=1e-9,
        hardness=450e6
    )

    return WasherFlangeContact(
        contact_id="washer_nord_lock",
        dof_washer=dof_washer,
        dof_flange=dof_flange,
        washer_props=washer_props,
        geometry=geometry,
        friction=friction,
        wear=wear
    )
