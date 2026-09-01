"""
Contact System Module for Bolt Analysis Studio.

Implements the complete contact hierarchy for bolted joint modeling:
- Base Contact class with matrix contribution methods
- Specific contact types (Thread, Bearing, Gasket, etc.)
- Property classes (Geometry, Friction, Wear, Stiffness, Damping)
- Time-evolving properties

Based on MSD_Contact_System_Architecture.md
"""

from .base import (
    # Enums
    ContactMechanicalType,
    FrictionModelType,
    WearModelType,
    StiffnessModelType,
    SlipState,

    # Property dataclasses
    ContactGeometry,
    FrictionProperties,
    WearProperties,
    StiffnessProperties,
    DampingProperties,

    # Base class
    Contact,
)

from .thread_contact import (
    ThreadGeometry,
    ThreadContact,
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
    LoadingState,
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

from .factory import (
    ContactFactory,
    JointConfiguration,
    create_api_6a_joint_config,
    create_asme_b16_5_joint_config,
    create_vdi_2230_joint_config,
)

__all__ = [
    # Enums
    'ContactMechanicalType',
    'FrictionModelType',
    'WearModelType',
    'StiffnessModelType',
    'SlipState',
    'ThreadLoadDistribution',
    'GasketType',
    'LoadingState',
    'WasherType',

    # Properties
    'ContactGeometry',
    'FrictionProperties',
    'WearProperties',
    'StiffnessProperties',
    'DampingProperties',
    'ThreadGeometry',
    'GasketProperties',
    'WasherProperties',

    # Contact classes
    'Contact',
    'ThreadContact',
    'BearingContact',
    'FlangeGasketContact',
    'FlangeFlangeContact',
    'WasherFlangeContact',

    # Factory
    'ContactFactory',
    'JointConfiguration',

    # Factory functions
    'create_standard_thread_contact',
    'create_bearing_head_contact',
    'create_bearing_nut_contact',
    'create_spiral_wound_gasket_contact',
    'create_rtj_gasket_contact',
    'create_flange_flange_contact',
    'create_plain_washer_contact',
    'create_belleville_washer_contact',
    'create_nord_lock_washer_contact',
    'create_api_6a_joint_config',
    'create_asme_b16_5_joint_config',
    'create_vdi_2230_joint_config',
]
