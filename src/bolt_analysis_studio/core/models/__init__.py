"""
MSD Models module for Bolt Analysis Studio.

Classes:
--------
- MSDElementData: Complete element data class with geometry, material, friction, loading
- MSDModel: Full model with matrix assembly and analysis methods
"""

from .element import (
    MSDElementData,
    GeometryData,
    MaterialData,
    FrictionData,
    LoadingData,
    MSDParameters,
    ConnectionType,
    ElementType,
    FrictionModel,
    LoadingType,
    ThreadStandard,
    MaterialGrade,
    # Factory functions
    create_bolt_head,
    create_bolt_shank,
    create_thread_element,
    create_nut,
    create_flange,
    create_gasket,
    create_washer,
    create_ground,
    create_timoshenko_beam_element,
)

from .model import MSDModel

__all__ = [
    # Element data classes
    'MSDElementData',
    'GeometryData',
    'MaterialData', 
    'FrictionData',
    'LoadingData',
    'MSDParameters',
    # Enums
    'ConnectionType',
    'ElementType',
    'FrictionModel',
    'LoadingType',
    'ThreadStandard',
    'MaterialGrade',
    # Factory functions
    'create_bolt_head',
    'create_bolt_shank',
    'create_thread_element',
    'create_nut',
    'create_flange',
    'create_gasket',
    'create_washer',
    'create_ground',
    'create_timoshenko_beam_element',
    # Model class
    'MSDModel'
]
