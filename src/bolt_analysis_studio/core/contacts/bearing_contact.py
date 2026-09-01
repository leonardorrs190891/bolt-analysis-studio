"""
Bearing Contact Implementation for Head and Nut Bearing Surfaces.

Models the friction interface under bolt head or nut face that provides
resistance to rotation. Critical for preventing/resisting rotational loosening.

Key Features:
- Rotational friction torque: T_b = μ × F_p × r_eff
- Resists nut/head rotation (opposes loosening)
- Slip state detection (STUCK → GROSS_SLIP transition)
- Effective friction radius for annular contact

Based on MSD_Part_II_Contact_Elements.md Section 4.2.
"""

from typing import List, Tuple, Optional, Dict, Any
import numpy as np

from .base import (
    Contact,
    ContactGeometry,
    FrictionProperties,
    WearProperties,
    StiffnessProperties,
    DampingProperties,
    SlipState,
)


class BearingContact(Contact):
    """
    Bearing surface contact (under bolt head or nut face).

    KEY CHARACTERISTICS:
    - Provides friction resistance to rotation (prevents loosening)
    - Must slip for rotational loosening to occur
    - Wear reduces friction over time
    - Critical for loosening prediction

    MATRIX CONTRIBUTIONS:
    - [K]: Contact stiffness (axial, high)
    - [C]: Bearing friction viscous equivalent
    - {F}: Coulomb friction torque (resists rotation)

    LOOSENING CRITERION:
    Loosening occurs when: F_transverse > μ_bearing × F_preload
    → Bearing slips → Allows nut rotation → Thread helix drives loosening
    """

    def __init__(self,
                 contact_id: str,
                 contact_type: str,  # "BEARING_HEAD" or "BEARING_NUT"
                 dof_axial_bolt_element: int,      # Bolt head or nut axial DOF
                 dof_axial_mating_surface: int,    # Washer or flange axial DOF
                 dof_theta_rotating_element: int,  # Rotational DOF (stud or nut)
                 geometry: ContactGeometry,
                 friction: FrictionProperties,
                 wear: WearProperties):
        """
        Initialize bearing contact.

        Args:
            contact_id: Unique identifier
            contact_type: "BEARING_HEAD" or "BEARING_NUT"
            dof_axial_bolt_element: Axial DOF of head/nut
            dof_axial_mating_surface: Axial DOF of washer/flange
            dof_theta_rotating_element: Torsional DOF for friction torque
            geometry: Contact geometry (annular)
            friction: Friction properties
            wear: Wear properties
        """
        # Calculate contact stiffness (metal-metal, very high)
        E_eff = 105e9  # Effective modulus for steel-steel [Pa]
        A = geometry.calc_annular_area() if geometry.contact_area == 0 else geometry.contact_area
        t_eff = 1e-6  # Effective contact thickness (asperity scale) [m]
        k_contact = E_eff * A / t_eff if t_eff > 0 else 1e12

        stiff = StiffnessProperties(k_axial=k_contact)
        damp = DampingProperties(damping_ratio=0.02)

        super().__init__(
            contact_id=contact_id,
            contact_type=contact_type,
            node_i=dof_axial_bolt_element,
            node_j=dof_axial_mating_surface,
            geometry=geometry,
            friction=friction,
            wear=wear,
            stiffness=stiff,
            damping=damp
        )

        self.dof_theta = dof_theta_rotating_element
        self.r_eff = geometry.calc_effective_radius()  # Effective friction radius

        # Bearing state
        self.friction_torque = 0.0          # Current friction torque [N·m]
        self.max_static_torque = 0.0        # Maximum torque before slip [N·m]
        self.is_slipping = False            # Slip state flag

    def get_stiffness_contribution(self) -> List[Tuple[int, int, float]]:
        """
        Bearing contact stiffness (very high - metal contact).

        Standard two-node stiffness pattern.
        """
        return self.get_basic_stiffness_contribution()

    def get_damping_contribution(self) -> List[Tuple[int, int, float]]:
        """
        Bearing damping (material + friction equivalent).
        """
        return self.get_basic_damping_contribution(mass_eff=0.01)

    def get_force_contribution(self, x: np.ndarray, x_dot: np.ndarray,
                               t: float) -> np.ndarray:
        """
        Bearing friction forces - CRITICAL FOR LOOSENING RESISTANCE.

        Computes:
        1. Rotational friction torque: T_b = μ × F_p × r_eff × sign(ω)
        2. This torque RESISTS rotation and must be overcome for loosening

        When bearing slips (F_transverse > μ × F_p):
        - Slip state → GROSS_SLIP
        - Thread contact can now rotate
        - Helix torque drives loosening

        Args:
            x: Displacement vector
            x_dot: Velocity vector
            t: Current time

        Returns:
            Force vector with friction torque at torsional DOF
        """
        n_dof = len(x)
        F = np.zeros(n_dof)

        # Check if torsional DOF is valid
        if self.dof_theta >= n_dof or self.dof_theta < 0:
            return F

        # Get rotational velocity
        omega = x_dot[self.dof_theta]

        # Bearing parameters
        mu = self.friction.mu_current
        N = self.normal_force  # Preload force
        r_eff = self.r_eff     # Effective friction radius

        # Maximum friction torque (static)
        self.max_static_torque = mu * N * r_eff

        # Friction torque (resists rotation)
        # Uses regularized Coulomb to avoid numerical issues
        T_friction = self.friction.get_friction_force(omega, N) * r_eff

        # Apply torque to rotating element
        F[self.dof_theta] += T_friction
        self.friction_torque = T_friction

        # Update slip state
        if abs(omega) > 1e-6:
            self.slip_state = SlipState.GROSS_SLIP
            self.is_slipping = True
        else:
            self.slip_state = SlipState.STUCK
            self.is_slipping = False

        return F

    def check_bearing_slip(self, F_transverse: float) -> bool:
        """
        Check if bearing surface has slipped due to transverse force.

        Junker loosening criterion:
        Bearing slips when: F_transverse > μ_bearing × F_preload

        Args:
            F_transverse: Applied transverse force [N]

        Returns:
            True if bearing has slipped (allows rotation)
        """
        F_slip_threshold = self.friction.mu_current * self.normal_force

        if abs(F_transverse) > F_slip_threshold:
            self.slip_state = SlipState.GROSS_SLIP
            self.is_slipping = True
            return True
        else:
            self.slip_state = SlipState.STUCK
            self.is_slipping = False
            return False

    def get_max_friction_torque(self) -> float:
        """
        Maximum friction torque before slip.

        T_max = μ_s × F_p × r_eff

        Returns:
            Maximum torque [N·m]
        """
        return self.friction.mu_static * self.normal_force * self.r_eff

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "contact_id": self.id,
            "contact_type": self.type,
            "dof_axial_bolt": self.node_i,
            "dof_axial_mating": self.node_j,
            "dof_theta": self.dof_theta,
            "geometry": self.geometry.to_dict(),
            "friction": self.friction.to_dict(),
            "wear": self.wear.to_dict(),
            "stiffness": self.stiffness.to_dict(),
            "damping": self.damping.to_dict(),
            "r_eff": self.r_eff,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BearingContact':
        """Deserialize from dictionary."""
        geometry = ContactGeometry.from_dict(data["geometry"])
        friction = FrictionProperties.from_dict(data["friction"])
        wear = WearProperties.from_dict(data["wear"])

        return cls(
            contact_id=data["contact_id"],
            contact_type=data["contact_type"],
            dof_axial_bolt_element=data["dof_axial_bolt"],
            dof_axial_mating_surface=data["dof_axial_mating"],
            dof_theta_rotating_element=data["dof_theta"],
            geometry=geometry,
            friction=friction,
            wear=wear,
        )


# =============================================================================
# FACTORY FUNCTIONS
# =============================================================================

def create_bearing_head_contact(
    dof_head: int,
    dof_washer_or_flange: int,
    dof_theta_stud: int,
    bolt_head_diameter: float,
    hole_diameter: float,
    mu_bearing: float = 0.12,   # Phase 2.1: aligned to model.mu_initial default
    wear_coeff: float = 5e-7
) -> BearingContact:
    """
    Create bearing contact under bolt head.

    Args:
        dof_head: Bolt head axial DOF index
        dof_washer_or_flange: Mating surface axial DOF index
        dof_theta_stud: Stud torsional DOF index
        bolt_head_diameter: Head bearing diameter [m]
        hole_diameter: Hole diameter [m]
        mu_bearing: Bearing friction coefficient
        wear_coeff: Archard wear coefficient

    Returns:
        BearingContact instance
    """
    geometry = ContactGeometry(
        inner_radius=hole_diameter / 2,
        outer_radius=bolt_head_diameter / 2
    )

    friction = FrictionProperties(
        mu_static=mu_bearing,
        mu_kinetic=mu_bearing * 0.85,
        mu_current=mu_bearing,
        degradation_rate=5e-6,
        min_friction=0.05
    )

    wear = WearProperties(
        wear_coeff_K=wear_coeff,
        hardness=2.5e9  # Steel hardness [Pa]
    )

    return BearingContact(
        contact_id="bearing_head",
        contact_type="BEARING_HEAD",
        dof_axial_bolt_element=dof_head,
        dof_axial_mating_surface=dof_washer_or_flange,
        dof_theta_rotating_element=dof_theta_stud,
        geometry=geometry,
        friction=friction,
        wear=wear
    )


def create_bearing_nut_contact(
    dof_nut: int,
    dof_washer_or_flange: int,
    dof_theta_nut: int,
    nut_bearing_diameter: float,
    hole_diameter: float,
    mu_bearing: float = 0.12,   # Phase 2.1: aligned to model.mu_initial default
    wear_coeff: float = 5e-7
) -> BearingContact:
    """
    Create bearing contact under nut.

    Args:
        dof_nut: Nut axial DOF index
        dof_washer_or_flange: Mating surface axial DOF index
        dof_theta_nut: Nut torsional DOF index
        nut_bearing_diameter: Nut bearing diameter [m]
        hole_diameter: Hole diameter [m]
        mu_bearing: Bearing friction coefficient
        wear_coeff: Archard wear coefficient

    Returns:
        BearingContact instance
    """
    geometry = ContactGeometry(
        inner_radius=hole_diameter / 2,
        outer_radius=nut_bearing_diameter / 2
    )

    friction = FrictionProperties(
        mu_static=mu_bearing,
        mu_kinetic=mu_bearing * 0.85,
        mu_current=mu_bearing,
        degradation_rate=5e-6,
        min_friction=0.05
    )

    wear = WearProperties(
        wear_coeff_K=wear_coeff,
        hardness=2.5e9
    )

    return BearingContact(
        contact_id="bearing_nut",
        contact_type="BEARING_NUT",
        dof_axial_bolt_element=dof_nut,
        dof_axial_mating_surface=dof_washer_or_flange,
        dof_theta_rotating_element=dof_theta_nut,
        geometry=geometry,
        friction=friction,
        wear=wear
    )
