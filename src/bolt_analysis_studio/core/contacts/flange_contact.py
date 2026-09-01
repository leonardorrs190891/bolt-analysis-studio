"""
Flange-to-Flange Metal Contact Implementation.

Models direct metal-to-metal contact between flanges (no gasket) with:
- Very high stiffness (metal contact)
- Fretting wear under cyclic loading
- Transverse DOF coupling for lateral motion
- Embedding effects

Key Features:
- High contact stiffness (metal-metal Hertzian contact)
- Fretting wear model for cyclic slip
- Lateral coupling (transverse forces)
- Surface roughness effects
- Embedding/plastic deformation

Based on Hertz contact theory and fretting wear models.
"""

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
# FLANGE CONTACT CLASS
# =============================================================================

class FlangeFlangeContact(Contact):
    """
    Metal-to-metal contact between flanges (no gasket).

    KEY CHARACTERISTICS:
    - Very high stiffness (metal contact, GPa range)
    - Fretting wear under vibration
    - Transverse coupling (lateral slip)
    - Can include surface treatments (coatings)
    - Used in metal-sealed joints (API 6A Type 6BX)

    MATRIX CONTRIBUTIONS:
    - [K]: Very high axial stiffness + transverse stiffness
    - [C]: Low damping (metal-metal)
    - {F}: Friction forces (axial + transverse)

    FAILURE MODES:
    - Fretting wear (loss of preload)
    - Galling (severe adhesive wear)
    - Surface damage
    """

    def __init__(self,
                 contact_id: str,
                 dof_flange_top: int,
                 dof_flange_bottom: int,
                 geometry: ContactGeometry,
                 friction: FrictionProperties,
                 wear: WearProperties,
                 dof_transverse_top: Optional[int] = None,
                 dof_transverse_bottom: Optional[int] = None):
        """
        Initialize flange-flange contact.

        Args:
            contact_id: Unique identifier
            dof_flange_top: Top flange axial DOF
            dof_flange_bottom: Bottom flange axial DOF
            dof_transverse_top: Top flange transverse DOF (optional)
            dof_transverse_bottom: Bottom flange transverse DOF (optional)
            geometry: Contact geometry
            friction: Friction properties
            wear: Wear properties (fretting)
        """
        # Calculate Hertzian contact stiffness
        # For flat annular contact: k = E* × A / h_eff
        E_eff = 105e9  # Effective modulus steel-steel [Pa]
        A = geometry.calc_annular_area()
        h_eff = 1e-6  # Effective contact thickness (asperity scale)

        k_contact = E_eff * A / h_eff if h_eff > 0 else 1e12

        # High stiffness for metal-metal contact
        stiff = StiffnessProperties(
            stiffness_model=StiffnessModelType.LINEAR,
            k_axial=k_contact,
            k_transverse=k_contact * 0.5 if dof_transverse_top is not None else 0.0
        )

        # Low damping (metal contact)
        damp = DampingProperties(
            damping_ratio=0.01,  # Low damping
            c_viscous=0.0
        )

        super().__init__(
            contact_id=contact_id,
            contact_type="FLANGE_FLANGE",
            node_i=dof_flange_top,
            node_j=dof_flange_bottom,
            geometry=geometry,
            friction=friction,
            wear=wear,
            stiffness=stiff,
            damping=damp
        )

        self.dof_trans_top = dof_transverse_top
        self.dof_trans_bottom = dof_transverse_bottom

        # Fretting state
        self.fretting_cycles = 0
        self.slip_amplitude = 0.0           # Current slip amplitude [m]
        self.is_fretting = False            # Fretting regime flag
        self.embedding_depth = 0.0          # Plastic embedding [m]

    def get_stiffness_contribution(self) -> List[Tuple[int, int, float]]:
        """
        Flange contact stiffness (very high for metal-metal).

        Includes axial and transverse stiffness if transverse DOFs defined.
        """
        contributions = self.get_basic_stiffness_contribution()

        # Add transverse stiffness if DOFs defined
        if self.dof_trans_top is not None and self.dof_trans_bottom is not None:
            k_trans = self.stiffness.k_transverse
            i_trans = self.dof_trans_top
            j_trans = self.dof_trans_bottom

            contributions.extend([
                (i_trans, i_trans, k_trans),
                (j_trans, j_trans, k_trans),
                (i_trans, j_trans, -k_trans),
                (j_trans, i_trans, -k_trans),
            ])

        return contributions

    def get_damping_contribution(self) -> List[Tuple[int, int, float]]:
        """
        Flange damping (low - metal contact).
        """
        contributions = self.get_basic_damping_contribution(mass_eff=0.1)

        # Add transverse damping if DOFs defined
        if self.dof_trans_top is not None and self.dof_trans_bottom is not None:
            k_trans = self.stiffness.k_transverse
            c_trans = self.damping.get_damping(k_trans, 0.1)

            i_trans = self.dof_trans_top
            j_trans = self.dof_trans_bottom

            contributions.extend([
                (i_trans, i_trans, c_trans),
                (j_trans, j_trans, c_trans),
                (i_trans, j_trans, -c_trans),
                (j_trans, i_trans, -c_trans),
            ])

        return contributions

    def get_force_contribution(self, x: np.ndarray, x_dot: np.ndarray,
                               t: float) -> np.ndarray:
        """
        Flange friction forces (axial + transverse).

        Computes:
        1. Axial friction (resists opening)
        2. Transverse friction (resists lateral slip)
        3. Fretting wear forces

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

        # Axial friction
        if j >= 0 and j < n_dof:
            v_axial = x_dot[i] - x_dot[j]
        else:
            v_axial = x_dot[i]

        F_friction_axial = self.friction.get_friction_force(v_axial, self.normal_force)
        F[i] += F_friction_axial
        if j >= 0 and j < n_dof:
            F[j] -= F_friction_axial

        # Transverse friction (if DOFs defined)
        if self.dof_trans_top is not None and self.dof_trans_bottom is not None:
            i_trans = self.dof_trans_top
            j_trans = self.dof_trans_bottom

            if i_trans < n_dof and j_trans < n_dof:
                v_trans = x_dot[i_trans] - x_dot[j_trans]

                F_friction_trans = self.friction.get_friction_force(v_trans, self.normal_force)
                F[i_trans] += F_friction_trans
                F[j_trans] -= F_friction_trans

                # Track slip amplitude for fretting
                delta_trans = abs(x[i_trans] - x[j_trans])
                self.slip_amplitude = delta_trans

                # Check if in fretting regime
                if self.slip_amplitude < self.wear.fretting_threshold:
                    self.is_fretting = True
                else:
                    self.is_fretting = False

        return F

    def update_fretting_wear(self, dt: float):
        """
        Update fretting wear specifically for metal-metal contact.

        Fretting occurs when slip amplitude is small (< ~50 μm).

        Args:
            dt: Time step [s]
        """
        if not self.is_fretting:
            return

        # Fretting wear calculation
        if self.wear.wear_model == WearModelType.FRETTING:
            slip_distance = self.slip_amplitude
            wear_vol = self.wear.calc_wear_increment(
                self.normal_force,
                slip_distance,
                self.geometry.contact_area
            )

            # Increment fretting cycle count
            if self.slip_amplitude > 1e-9:
                self.fretting_cycles += 1

    def update_embedding(self, dt: float):
        """
        Update plastic embedding under high contact stress.

        Embedding occurs when contact pressure exceeds yield strength.

        Args:
            dt: Time step [s]
        """
        if self.geometry.contact_area <= 0:
            return

        # Contact pressure
        p_contact = self.normal_force / self.geometry.contact_area

        # Yield pressure (approximately 3× yield strength for Brinell hardness)
        p_yield = self.wear.hardness / 3.0

        if p_contact > p_yield:
            # Plastic embedding (simplified model)
            # δ_embed = C × (p/p_yield - 1)^n × t^m
            overstress_ratio = (p_contact / p_yield) - 1.0
            if overstress_ratio > 0:
                embed_rate = 1e-9 * (overstress_ratio ** 1.5)  # [m/s]
                self.embedding_depth += embed_rate * dt

    def get_preload_loss(self, system_stiffness: float) -> float:
        """
        Calculate preload loss from flange contact.

        Includes:
        1. Fretting wear
        2. Plastic embedding
        3. Surface damage

        Args:
            system_stiffness: Joint stiffness [N/m]

        Returns:
            Total preload loss [N]
        """
        # Loss from wear
        loss_wear = self.wear.get_preload_loss(system_stiffness)

        # Loss from embedding
        loss_embedding = system_stiffness * self.embedding_depth

        return loss_wear + loss_embedding

    def get_contact_summary(self) -> Dict[str, Any]:
        """
        Get flange contact state summary.

        Returns:
            Dictionary with contact state data
        """
        return {
            "contact_type": self.type,
            "slip_state": self.slip_state.value,
            "is_fretting": self.is_fretting,
            "fretting_cycles": self.fretting_cycles,
            "slip_amplitude_um": self.slip_amplitude * 1e6,
            "wear_depth_um": self.wear.wear_depth * 1e6,
            "embedding_depth_um": self.embedding_depth * 1e6,
            "contact_pressure_MPa": (self.normal_force / self.geometry.contact_area / 1e6
                                    if self.geometry.contact_area > 0 else 0),
        }

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "contact_id": self.id,
            "contact_type": self.type,
            "dof_flange_top": self.node_i,
            "dof_flange_bottom": self.node_j,
            "dof_trans_top": self.dof_trans_top,
            "dof_trans_bottom": self.dof_trans_bottom,
            "geometry": self.geometry.to_dict(),
            "friction": self.friction.to_dict(),
            "wear": self.wear.to_dict(),
            "stiffness": self.stiffness.to_dict(),
            "damping": self.damping.to_dict(),
            "fretting_cycles": self.fretting_cycles,
            "slip_amplitude": self.slip_amplitude,
            "embedding_depth": self.embedding_depth,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FlangeFlangeContact':
        """Deserialize from dictionary."""
        geometry = ContactGeometry.from_dict(data["geometry"])
        friction = FrictionProperties.from_dict(data["friction"])
        wear = WearProperties.from_dict(data["wear"])

        contact = cls(
            contact_id=data["contact_id"],
            dof_flange_top=data["dof_flange_top"],
            dof_flange_bottom=data["dof_flange_bottom"],
            dof_transverse_top=data.get("dof_trans_top"),
            dof_transverse_bottom=data.get("dof_trans_bottom"),
            geometry=geometry,
            friction=friction,
            wear=wear
        )

        contact.fretting_cycles = data.get("fretting_cycles", 0)
        contact.slip_amplitude = data.get("slip_amplitude", 0.0)
        contact.embedding_depth = data.get("embedding_depth", 0.0)

        return contact


# =============================================================================
# FACTORY FUNCTION
# =============================================================================

def create_flange_flange_contact(
    dof_flange_top: int,
    dof_flange_bottom: int,
    inner_diameter: float,
    outer_diameter: float,
    surface_finish: str = "MACHINED",
    dof_transverse_top: Optional[int] = None,
    dof_transverse_bottom: Optional[int] = None
) -> FlangeFlangeContact:
    """
    Create metal-to-metal flange contact.

    Args:
        dof_flange_top: Top flange axial DOF
        dof_flange_bottom: Bottom flange axial DOF
        inner_diameter: Inner diameter [m]
        outer_diameter: Outer diameter [m]
        surface_finish: "MACHINED", "GROUND", or "LAPPED"
        dof_transverse_top: Optional transverse DOF for top flange
        dof_transverse_bottom: Optional transverse DOF for bottom flange

    Returns:
        FlangeFlangeContact instance
    """
    geometry = ContactGeometry(
        inner_radius=inner_diameter / 2,
        outer_radius=outer_diameter / 2
    )

    # Surface finish affects friction and roughness
    if surface_finish == "GROUND":
        mu = 0.18
        Ra = 0.8e-6  # 32 μin
    elif surface_finish == "LAPPED":
        mu = 0.15
        Ra = 0.4e-6  # 16 μin
    else:  # MACHINED
        mu = 0.20
        Ra = 3.2e-6  # 125 μin

    geometry.roughness_Ra = Ra

    friction = FrictionProperties(
        mu_static=mu,
        mu_kinetic=mu * 0.9,
        mu_current=mu,
        degradation_rate=1e-6,  # Slow degradation for metal-metal
        min_friction=mu * 0.7
    )

    wear = WearProperties(
        wear_model=WearModelType.FRETTING,
        wear_coeff_K=2e-7,  # Lower than soft materials
        hardness=2.5e9,     # Steel hardness [Pa]
        fretting_threshold=50e-6,  # 50 μm slip amplitude
        fretting_coeff=5e-7
    )

    return FlangeFlangeContact(
        contact_id="flange_flange",
        dof_flange_top=dof_flange_top,
        dof_flange_bottom=dof_flange_bottom,
        geometry=geometry,
        friction=friction,
        wear=wear,
        dof_transverse_top=dof_transverse_top,
        dof_transverse_bottom=dof_transverse_bottom
    )
