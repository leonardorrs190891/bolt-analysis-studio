"""
Contact Factory for Creating Complete Joint Contact Systems.

Provides high-level factory methods to create all contacts for standard joint
configurations (API 6A, ASME B16.5, etc.) with one function call.

Key Features:
- ContactFactory class for managing contact creation
- create_complete_joint() returns all contacts for a bolted joint
- Standard configurations (API 6A, ASME B16.5, VDI 2230)
- DOF mapping helpers
- Contact verification and validation

Based on MSD_Contact_System_Architecture.md Section 7.
"""

from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import numpy as np

from .base import (
    Contact,
    ContactGeometry,
    FrictionProperties,
    WearProperties,
    WearModelType,
    StiffnessProperties,
    DampingProperties,
)

from .thread_contact import (
    ThreadContact,
    ThreadGeometry,
    ThreadLoadDistribution,
    create_standard_thread_contact,
)

from .bearing_contact import (
    BearingContact,
    create_bearing_head_contact,
    create_bearing_nut_contact,
)

from .gasket_contact import (
    FlangeGasketContact,
    GasketType,
    GasketProperties,
    create_spiral_wound_gasket_contact,
    create_rtj_gasket_contact,
)

from .flange_contact import (
    FlangeFlangeContact,
    create_flange_flange_contact,
)

from .washer_contact import (
    WasherFlangeContact,
    WasherType,
    WasherProperties,
    create_plain_washer_contact,
    create_belleville_washer_contact,
    create_nord_lock_washer_contact,
)


# =============================================================================
# JOINT CONFIGURATION DATACLASS
# =============================================================================

@dataclass
class JointConfiguration:
    """
    Complete joint configuration parameters.

    Contains all geometric and material data needed to create a full
    contact system for a bolted joint.
    """
    # Joint type
    joint_type: str = "ASME_B16_5"  # "API_6A", "ASME_B16_5", "VDI_2230"

    # Bolt geometry
    bolt_size: str = "M20"
    bolt_head_diameter: float = 0.030       # [m]
    bolt_shank_diameter: float = 0.020      # [m]
    hole_diameter: float = 0.022            # [m]

    # Thread geometry
    thread_pitch: float = 0.0025            # [m]
    thread_major_diameter: float = 0.020    # [m]
    thread_minor_diameter: float = 0.01727  # [m]
    thread_pitch_diameter: float = 0.01854  # [m]
    n_engaged_threads: int = 8

    # Nut geometry
    nut_bearing_diameter: float = 0.030     # [m]

    # Washer geometry (if used)
    use_washer_head: bool = True
    use_washer_nut: bool = True
    washer_inner_diameter: float = 0.022    # [m]
    washer_outer_diameter: float = 0.037    # [m]
    washer_type: str = "PLAIN"              # "PLAIN", "BELLEVILLE", "NORD_LOCK"

    # Gasket geometry (if gasketed joint)
    use_gasket: bool = True
    gasket_type: str = "SPIRAL_WOUND"       # "SPIRAL_WOUND", "RTJ", "NONE"
    gasket_inner_diameter: float = 0.100    # [m]
    gasket_outer_diameter: float = 0.150    # [m]
    gasket_thickness: float = 4.5e-3        # [m]

    # Friction coefficients — Phase 2.1: bearing defaults aligned to thread (= model.mu_initial)
    mu_thread: float = 0.12
    mu_bearing_head: float = 0.12
    mu_bearing_nut: float = 0.12
    mu_gasket: float = 0.20

    # Wear coefficients
    wear_coeff_thread: float = 1e-6
    wear_coeff_bearing: float = 5e-7
    wear_coeff_gasket: float = 1e-5

    # DOF mapping (14-DOF system)
    dof_head: int = 0
    dof_washer_head: int = 1
    dof_flange_top: int = 2
    dof_gasket: int = 3
    dof_flange_bottom: int = 4
    dof_washer_nut: int = 5
    dof_nut: int = 6
    dof_stud_axial: int = 7
    dof_stud_theta: int = 8
    dof_nut_theta: int = 9
    dof_trans_flange_top: Optional[int] = None
    dof_trans_flange_bottom: Optional[int] = None


# =============================================================================
# CONTACT FACTORY CLASS
# =============================================================================

class ContactFactory:
    """
    Factory for creating complete contact systems for bolted joints.

    Provides methods to:
    - Create individual contacts
    - Create complete joint systems
    - Validate DOF mappings
    - Generate standard configurations
    """

    def __init__(self):
        """Initialize contact factory."""
        self.contacts: List[Contact] = []

    def create_complete_joint(self, config: JointConfiguration) -> List[Contact]:
        """
        Create all contacts for a complete bolted joint.

        This is the main entry point for creating a full contact system.

        Args:
            config: Joint configuration parameters

        Returns:
            List of all Contact objects for the joint
        """
        contacts = []

        # 1. Thread contact (CRITICAL - drives loosening)
        thread_contact = self._create_thread_contact(config)
        contacts.append(thread_contact)

        # 2. Bearing contacts (head and nut)
        bearing_head = self._create_bearing_head(config)
        contacts.append(bearing_head)

        bearing_nut = self._create_bearing_nut(config)
        contacts.append(bearing_nut)

        # 3. Washer contacts (if used)
        if config.use_washer_head:
            washer_head_contact = self._create_washer_head(config)
            contacts.append(washer_head_contact)

        if config.use_washer_nut:
            washer_nut_contact = self._create_washer_nut(config)
            contacts.append(washer_nut_contact)

        # 4. Gasket or flange-flange contact
        if config.use_gasket and config.gasket_type != "NONE":
            gasket_contact = self._create_gasket_contact(config)
            contacts.append(gasket_contact)
        else:
            # Metal-to-metal flange contact
            flange_contact = self._create_flange_contact(config)
            contacts.append(flange_contact)

        self.contacts = contacts
        return contacts

    def _create_thread_contact(self, config: JointConfiguration) -> ThreadContact:
        """Create thread contact with helix coupling."""
        return create_standard_thread_contact(
            bolt_size=config.bolt_size,
            dof_axial_stud=config.dof_stud_axial,
            dof_axial_nut=config.dof_nut,
            dof_theta_stud=config.dof_stud_theta,
            dof_theta_nut=config.dof_nut_theta,
            mu_thread=config.mu_thread,
            wear_coeff=config.wear_coeff_thread
        )

    def _create_bearing_head(self, config: JointConfiguration) -> BearingContact:
        """Create bearing contact under bolt head."""
        if config.use_washer_head:
            mating_dof = config.dof_washer_head
        else:
            mating_dof = config.dof_flange_top

        return create_bearing_head_contact(
            dof_head=config.dof_head,
            dof_washer_or_flange=mating_dof,
            dof_theta_stud=config.dof_stud_theta,
            bolt_head_diameter=config.bolt_head_diameter,
            hole_diameter=config.hole_diameter,
            mu_bearing=config.mu_bearing_head,
            wear_coeff=config.wear_coeff_bearing
        )

    def _create_bearing_nut(self, config: JointConfiguration) -> BearingContact:
        """Create bearing contact under nut."""
        if config.use_washer_nut:
            mating_dof = config.dof_washer_nut
        else:
            mating_dof = config.dof_flange_bottom

        return create_bearing_nut_contact(
            dof_nut=config.dof_nut,
            dof_washer_or_flange=mating_dof,
            dof_theta_nut=config.dof_nut_theta,
            nut_bearing_diameter=config.nut_bearing_diameter,
            hole_diameter=config.hole_diameter,
            mu_bearing=config.mu_bearing_nut,
            wear_coeff=config.wear_coeff_bearing
        )

    def _create_washer_head(self, config: JointConfiguration) -> WasherFlangeContact:
        """Create washer contact under bolt head."""
        if config.washer_type == "BELLEVILLE":
            return create_belleville_washer_contact(
                dof_washer=config.dof_washer_head,
                dof_flange=config.dof_flange_top,
                inner_diameter=config.washer_inner_diameter,
                outer_diameter=config.washer_outer_diameter,
                cone_height=0.002,  # 2mm typical
                thickness=0.0015    # 1.5mm typical
            )
        elif config.washer_type == "NORD_LOCK":
            return create_nord_lock_washer_contact(
                dof_washer=config.dof_washer_head,
                dof_flange=config.dof_flange_top,
                inner_diameter=config.washer_inner_diameter,
                outer_diameter=config.washer_outer_diameter
            )
        else:  # PLAIN
            return create_plain_washer_contact(
                dof_washer=config.dof_washer_head,
                dof_flange=config.dof_flange_top,
                inner_diameter=config.washer_inner_diameter,
                outer_diameter=config.washer_outer_diameter,
                washer_hardness="STANDARD"
            )

    def _create_washer_nut(self, config: JointConfiguration) -> WasherFlangeContact:
        """Create washer contact under nut."""
        if config.washer_type == "BELLEVILLE":
            return create_belleville_washer_contact(
                dof_washer=config.dof_washer_nut,
                dof_flange=config.dof_flange_bottom,
                inner_diameter=config.washer_inner_diameter,
                outer_diameter=config.washer_outer_diameter,
                cone_height=0.002,
                thickness=0.0015
            )
        elif config.washer_type == "NORD_LOCK":
            return create_nord_lock_washer_contact(
                dof_washer=config.dof_washer_nut,
                dof_flange=config.dof_flange_bottom,
                inner_diameter=config.washer_inner_diameter,
                outer_diameter=config.washer_outer_diameter
            )
        else:  # PLAIN
            return create_plain_washer_contact(
                dof_washer=config.dof_washer_nut,
                dof_flange=config.dof_flange_bottom,
                inner_diameter=config.washer_inner_diameter,
                outer_diameter=config.washer_outer_diameter,
                washer_hardness="STANDARD"
            )

    def _create_gasket_contact(self, config: JointConfiguration) -> FlangeGasketContact:
        """Create gasket contact between flanges."""
        if config.gasket_type == "RTJ":
            return create_rtj_gasket_contact(
                dof_flange_top=config.dof_flange_top,
                dof_flange_bottom=config.dof_flange_bottom,
                ring_diameter=(config.gasket_inner_diameter + config.gasket_outer_diameter) / 2,
                ring_cross_section=0.006,  # 6mm R-ring
                material="INCONEL_625"
            )
        else:  # SPIRAL_WOUND (default)
            return create_spiral_wound_gasket_contact(
                dof_flange_top=config.dof_flange_top,
                dof_flange_bottom=config.dof_flange_bottom,
                inner_diameter=config.gasket_inner_diameter,
                outer_diameter=config.gasket_outer_diameter,
                thickness=config.gasket_thickness,
                material="316SS_GRAPHITE"
            )

    def _create_flange_contact(self, config: JointConfiguration) -> FlangeFlangeContact:
        """Create metal-to-metal flange contact (no gasket)."""
        return create_flange_flange_contact(
            dof_flange_top=config.dof_flange_top,
            dof_flange_bottom=config.dof_flange_bottom,
            inner_diameter=config.gasket_inner_diameter,
            outer_diameter=config.gasket_outer_diameter,
            surface_finish="MACHINED",
            dof_transverse_top=config.dof_trans_flange_top,
            dof_transverse_bottom=config.dof_trans_flange_bottom
        )

    def get_contact_by_id(self, contact_id: str) -> Optional[Contact]:
        """
        Retrieve contact by ID.

        Args:
            contact_id: Contact identifier

        Returns:
            Contact object or None if not found
        """
        for contact in self.contacts:
            if contact.id == contact_id:
                return contact
        return None

    def get_contacts_by_type(self, contact_type: str) -> List[Contact]:
        """
        Get all contacts of a specific type.

        Args:
            contact_type: Contact type string (e.g., "THREAD", "BEARING_HEAD")

        Returns:
            List of matching contacts
        """
        return [c for c in self.contacts if c.type == contact_type]

    def validate_dof_mapping(self, n_dof: int) -> Tuple[bool, List[str]]:
        """
        Validate that all contact DOFs are within valid range.

        Args:
            n_dof: Total number of DOFs in system

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []

        for contact in self.contacts:
            # Check node_i
            if contact.node_i >= n_dof:
                errors.append(f"Contact {contact.id}: node_i={contact.node_i} >= n_dof={n_dof}")

            # Check node_j
            if contact.node_j >= 0 and contact.node_j >= n_dof:
                errors.append(f"Contact {contact.id}: node_j={contact.node_j} >= n_dof={n_dof}")

            # Check additional DOFs for specific types
            if isinstance(contact, ThreadContact):
                if contact.dof_theta_stud >= n_dof:
                    errors.append(f"Thread {contact.id}: dof_theta_stud={contact.dof_theta_stud} >= n_dof={n_dof}")
                if contact.dof_theta_nut >= n_dof:
                    errors.append(f"Thread {contact.id}: dof_theta_nut={contact.dof_theta_nut} >= n_dof={n_dof}")

            if isinstance(contact, BearingContact):
                if contact.dof_theta >= n_dof:
                    errors.append(f"Bearing {contact.id}: dof_theta={contact.dof_theta} >= n_dof={n_dof}")

        is_valid = len(errors) == 0
        return is_valid, errors

    def get_summary(self) -> Dict[str, Any]:
        """
        Get summary of contact system.

        Returns:
            Dictionary with contact statistics
        """
        contact_types = {}
        for contact in self.contacts:
            contact_type = contact.type
            if contact_type not in contact_types:
                contact_types[contact_type] = 0
            contact_types[contact_type] += 1

        return {
            "total_contacts": len(self.contacts),
            "contact_types": contact_types,
            "contact_ids": [c.id for c in self.contacts],
        }


# =============================================================================
# STANDARD JOINT CONFIGURATIONS
# =============================================================================

def create_api_6a_joint_config(
    bolt_size: str = "M20",
    pressure_rating: str = "5K",
    gasket_type: str = "RTJ"
) -> JointConfiguration:
    """
    Create API 6A joint configuration.

    Args:
        bolt_size: Bolt size designation
        pressure_rating: API 6A pressure rating (2K, 5K, 10K, 15K, 20K)
        gasket_type: "RTJ", "SPIRAL_WOUND", or "NONE" (metal-to-metal)

    Returns:
        JointConfiguration for API 6A joint
    """
    # API 6A typical dimensions (simplified)
    config = JointConfiguration(
        joint_type="API_6A",
        bolt_size=bolt_size,
        bolt_head_diameter=0.030,
        bolt_shank_diameter=0.020,
        hole_diameter=0.022,
        thread_pitch=0.0025,
        thread_major_diameter=0.020,
        thread_minor_diameter=0.01727,
        thread_pitch_diameter=0.01854,
        n_engaged_threads=10,  # API 6A typically more threads
        nut_bearing_diameter=0.030,
        use_washer_head=False,  # API 6A typically no washers
        use_washer_nut=False,
        washer_type="NONE",
        use_gasket=gasket_type != "NONE",
        gasket_type=gasket_type,
        gasket_inner_diameter=0.100,
        gasket_outer_diameter=0.150,
        gasket_thickness=0.006 if gasket_type == "RTJ" else 4.5e-3,
        mu_thread=0.10,  # Lower friction (often lubricated)
        mu_bearing_head=0.12,
        mu_bearing_nut=0.12,
        mu_gasket=0.25 if gasket_type == "RTJ" else 0.20,
    )

    return config


def create_asme_b16_5_joint_config(
    bolt_size: str = "M20",
    flange_class: str = "150",
    use_spiral_wound: bool = True
) -> JointConfiguration:
    """
    Create ASME B16.5 flange joint configuration.

    Args:
        bolt_size: Bolt size designation
        flange_class: ASME class (150, 300, 600, 900, 1500, 2500)
        use_spiral_wound: Use spiral wound gasket (vs. sheet)

    Returns:
        JointConfiguration for ASME B16.5 joint
    """
    config = JointConfiguration(
        joint_type="ASME_B16_5",
        bolt_size=bolt_size,
        bolt_head_diameter=0.030,
        bolt_shank_diameter=0.020,
        hole_diameter=0.022,
        thread_pitch=0.0025,
        thread_major_diameter=0.020,
        thread_minor_diameter=0.01727,
        thread_pitch_diameter=0.01854,
        n_engaged_threads=8,
        nut_bearing_diameter=0.030,
        use_washer_head=True,  # ASME typically uses washers
        use_washer_nut=True,
        washer_type="PLAIN",
        washer_inner_diameter=0.022,
        washer_outer_diameter=0.037,
        use_gasket=True,
        gasket_type="SPIRAL_WOUND" if use_spiral_wound else "SHEET",
        gasket_inner_diameter=0.100,
        gasket_outer_diameter=0.150,
        gasket_thickness=4.5e-3,
        mu_thread=0.12,
        mu_bearing_head=0.12,
        mu_bearing_nut=0.12,
        mu_gasket=0.20,
    )

    return config


def create_vdi_2230_joint_config(
    bolt_size: str = "M20",
    use_belleville: bool = False
) -> JointConfiguration:
    """
    Create VDI 2230 standard joint configuration.

    Args:
        bolt_size: Metric bolt size
        use_belleville: Use Belleville washers for preload control

    Returns:
        JointConfiguration for VDI 2230 joint
    """
    config = JointConfiguration(
        joint_type="VDI_2230",
        bolt_size=bolt_size,
        bolt_head_diameter=0.030,
        bolt_shank_diameter=0.020,
        hole_diameter=0.022,
        thread_pitch=0.0025,
        thread_major_diameter=0.020,
        thread_minor_diameter=0.01727,
        thread_pitch_diameter=0.01854,
        n_engaged_threads=8,
        nut_bearing_diameter=0.030,
        use_washer_head=True,
        use_washer_nut=True,
        washer_type="BELLEVILLE" if use_belleville else "PLAIN",
        washer_inner_diameter=0.022,
        washer_outer_diameter=0.037,
        use_gasket=False,  # VDI examples typically metal-metal
        gasket_type="NONE",
        mu_thread=0.12,
        mu_bearing_head=0.12,
        mu_bearing_nut=0.12,
    )

    return config
