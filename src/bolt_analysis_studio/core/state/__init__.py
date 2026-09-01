"""
State Management Package for Bolt Analysis.

Complete preload tracking and state update management system.

Modules:
- preload_tracker: Comprehensive preload loss tracking with all mechanisms

Classes:
- PreloadTracker: Tracks all preload loss mechanisms
- PreloadLossMechanism: Individual loss mechanism data
- StateUpdateManager: Coordinates state updates across all components

Enums:
- LossMechanismType: ROTATIONAL, EMBEDDING, WEAR, CREEP, RELAXATION, THERMAL, ELASTIC_INTERACTION

Functions:
- compute_vdi_2230_embedding_factor: VDI 2230 embedding factors for material pairs
- compute_system_stiffness: Joint stiffness calculation (series combination)
- estimate_embedding_length: Estimate L_K from geometry

Author: Bolt Analysis Studio Team
Version: 4.0
"""

from .preload_tracker import (
    LossMechanismType,
    PreloadLossMechanism,
    PreloadTracker,
    StateUpdateManager,
    compute_vdi_2230_embedding_factor,
    compute_system_stiffness,
    estimate_embedding_length,
)

__all__ = [
    # Enums
    'LossMechanismType',

    # Classes
    'PreloadLossMechanism',
    'PreloadTracker',
    'StateUpdateManager',

    # Helper functions
    'compute_vdi_2230_embedding_factor',
    'compute_system_stiffness',
    'estimate_embedding_length',
]
