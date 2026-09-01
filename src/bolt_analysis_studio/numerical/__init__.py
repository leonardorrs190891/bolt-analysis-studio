"""
Numerical module for Bolt Analysis Studio.

Submodules:
-----------
- preload_loss_models: Double exponential, power law, Jiang two-stage models
- friction_models: Coulomb, LuGre, Dahl, Iwan, Hintikka models
- time_integration: Newmark-β, HHT-α, Central Difference, RK4 solvers
"""

from .preload_loss_models import (
    # Enums
    LooseningStage,
    LoadingType,
    DecayModelType,
    # Data classes
    BoltParameters,
    JointParameters,
    PreloadConditions,
    # Models
    PreloadLossModel,
    SingleExponentialModel,
    DoubleExponentialModel,
    StretchedExponentialModel,
    VDI2230EmbeddingModel,
    NortonBaileyCreepModel,
    ThermalEffectsModel,
    CombinedMechanismModel,
    PowerLawModel,
    LogarithmicModel,
    JiangTwoStageModel,
    JiangThreeStageModel,
    CombinedPreloadLossModel,
    # Analysis classes
    DNLooseningCurve,
    MinersRuleDamageModel,
    MinersRuleAccumulation,
    EnergyDissipationModel,
    RotationAngleModel,
    EmbeddingLossModel
)

from .friction_models import (
    # Enums
    FrictionModelType,
    LubricationRegime,
    WearRegime,
    # Parameters
    CoulombParameters,
    LuGreParameters,
    DahlParameters,
    IwanParameters,
    WearParameters,
    FrictionEvolutionParameters,
    # Models
    FrictionModel,
    CoulombFriction,
    LuGreFriction,
    DahlFriction,
    IwanFriction,
    FrictionEvolutionModel,
    CoupledFrictionPreloadModel,
    WearModel,
    WearEvolutionModel,
    StribeckModel
)

from .wear_models import (
    WearRegimeEnum,
    WearPhaseEnum,
    WearState,
    ArchardWearModel,
    EnergyBasedWearModel,
    FrettingWearModel,
    FatigueWearModel,
    create_wear_model,
)

from .time_integration import (
    # Enums
    IntegratorType,
    ConvergenceType,
    # Parameters
    TimeParams,
    NewmarkParams,
    HHTParams,
    NonlinearParams,
    # Results
    IntegrationResult,
    # Integrators
    NewmarkIntegrator,
    HHTIntegrator,
    CentralDifferenceIntegrator,
    ModalSuperposition,
    RungeKutta4,
    NonlinearNewmark
)

__all__ = [
    # Preload loss enums
    'LooseningStage',
    'LoadingType', 
    'DecayModelType',
    # Preload loss data
    'BoltParameters',
    'JointParameters',
    'PreloadConditions',
    # Preload loss models
    'PreloadLossModel',
    'SingleExponentialModel',
    'DoubleExponentialModel',
    'StretchedExponentialModel',
    'VDI2230EmbeddingModel',
    'NortonBaileyCreepModel',
    'ThermalEffectsModel',
    'CombinedMechanismModel',
    'PowerLawModel',
    'LogarithmicModel',
    'JiangTwoStageModel',
    'JiangThreeStageModel',
    'CombinedPreloadLossModel',
    # Preload loss analysis
    'DNLooseningCurve',
    'MinersRuleDamageModel',
    'MinersRuleAccumulation',
    'EnergyDissipationModel',
    'RotationAngleModel',
    'EmbeddingLossModel',
    # Friction enums
    'FrictionModelType',
    'LubricationRegime',
    'WearRegime',
    # Friction parameters
    'CoulombParameters',
    'LuGreParameters',
    'DahlParameters',
    'IwanParameters',
    'WearParameters',
    'FrictionEvolutionParameters',
    # Friction models
    'FrictionModel',
    'CoulombFriction',
    'LuGreFriction',
    'DahlFriction',
    'IwanFriction',
    'FrictionEvolutionModel',
    'CoupledFrictionPreloadModel',
    'WearModel',
    'WearEvolutionModel',
    'StribeckModel',
    # Time integration enums
    'IntegratorType',
    'ConvergenceType',
    # Time integration parameters
    'TimeParams',
    'NewmarkParams',
    'HHTParams',
    'NonlinearParams',
    # Time integration results
    'IntegrationResult',
    # Integrators
    'NewmarkIntegrator',
    'HHTIntegrator',
    'CentralDifferenceIntegrator',
    'ModalSuperposition',
    'RungeKutta4',
    'NonlinearNewmark',
    # Wear evolution models (Phase 3.2)
    'WearRegimeEnum',
    'WearPhaseEnum',
    'WearState',
    'ArchardWearModel',
    'EnergyBasedWearModel',
    'FrettingWearModel',
    'FatigueWearModel',
    'create_wear_model',
]
