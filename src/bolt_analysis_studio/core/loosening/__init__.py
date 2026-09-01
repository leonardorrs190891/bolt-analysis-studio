"""
Bolt Loosening Models Package.

Comprehensive implementation of bolt loosening mechanisms based on experimental research.

Modules:
- junker_model: Classic Junker, Pai-Hess, Jiang two-stage, and Nassar-Housari models

Classes:
- JunkerLooseningModel: Classic transverse vibration loosening (1969)
- PaiHessExtension: Four-regime slip classification (2002)
- JiangTwoStageModel: Non-rotational + rotational stages (2003)
- NassarHousariModel: Integral formulation with slip history (2007)

Enums:
- JunkerSlipRegime: NO_SLIP, HEAD_ONLY, NUT_ONLY, COMPLETE_SLIP
- LooseningStage: NON_ROTATIONAL, TRANSITION, ROTATIONAL

Author: Bolt Analysis Studio Team
Version: 4.0
"""

from .junker_model import (
    JunkerSlipRegime,
    LooseningStage,
    ThreadContactParams,
    BearingContactParams,
    JunkerLooseningModel,
    PaiHessExtension,
    JiangTwoStageModel,
    NassarHousariModel,
    create_standard_junker_model,
)

__all__ = [
    # Enums
    'JunkerSlipRegime',
    'LooseningStage',

    # Dataclasses
    'ThreadContactParams',
    'BearingContactParams',

    # Models
    'JunkerLooseningModel',
    'PaiHessExtension',
    'JiangTwoStageModel',
    'NassarHousariModel',

    # Factory
    'create_standard_junker_model',
]
