"""
Similitude Analysis Module
Bolt Analysis Studio v4.0

Provides dimensional analysis and scaling laws for bolted flanged joints
using Buckingham-Π theorem with scale effect corrections.

Main Classes:
- SimilitudeAnalysis: Complete similitude analysis
- PrototypeData: Full-scale joint parameters
- ScaleFactors: Derived scaling factors
- PiGroup: Dimensionless Π-groups
- ScaleEffect: Scale effect corrections

Prof. Leonardo Rosa Ribeiro da Silva, PhD
January 2026
"""

from .similitude import (
    # Enumerations
    MaterialSimilarity,
    ScaleEffectSeverity,
    SimilitudeType,

    # Data Classes
    ScaleFactors,
    PiGroup,
    ScaleEffect,
    PrototypeData,
    SimilitudeAnalysis,

    # HS1-HS7 New Features
    ThermalScaleFactors,
    MultiScaleValidation,
    ScaleEffectWithUncertainty,
    DistortedScaleFactors,
    PiGroupCategory,
    PiGroupDefinition,
    PiGroupRegistry,
    EquivalenceMode,

    # Utility Functions
    find_standard_bolt_size,
    get_available_standards,
    calculate_standard_scales,
    interpolate_prototype_results,
    kuguel_fatigue_correction,
    kuguel_from_scale,
    compute_hersey_number,
    check_lubrication_regime_preservation,
    monte_carlo_prototype_prediction,
    verify_dynamic_similitude,
    scale_factor_sensitivity,
)

from .similitude_plots import (
    # Individual Plots
    plot_scaling_relationships,
    plot_pi_groups_comparison,
    plot_scale_effects_radar,
    plot_correction_factor_breakdown,
    plot_prototype_model_schematic,
    plot_multi_scale_comparison,
    
    # Dashboard
    create_similitude_dashboard,
    
    # Export
    save_all_plots,
)


__all__ = [
    # Enumerations
    'MaterialSimilarity',
    'ScaleEffectSeverity',
    'SimilitudeType',

    # Data Classes
    'ScaleFactors',
    'PiGroup',
    'ScaleEffect',
    'PrototypeData',
    'SimilitudeAnalysis',

    # HS1-HS7 New Features
    'ThermalScaleFactors',
    'MultiScaleValidation',
    'ScaleEffectWithUncertainty',
    'DistortedScaleFactors',
    'PiGroupCategory',
    'PiGroupDefinition',
    'PiGroupRegistry',
    'EquivalenceMode',

    # Utility Functions
    'find_standard_bolt_size',
    'get_available_standards',
    'calculate_standard_scales',
    'interpolate_prototype_results',
    'kuguel_fatigue_correction',
    'kuguel_from_scale',
    'compute_hersey_number',
    'check_lubrication_regime_preservation',
    'monte_carlo_prototype_prediction',
    'verify_dynamic_similitude',
    'scale_factor_sensitivity',

    # Visualization
    'plot_scaling_relationships',
    'plot_pi_groups_comparison',
    'plot_scale_effects_radar',
    'plot_correction_factor_breakdown',
    'plot_prototype_model_schematic',
    'plot_multi_scale_comparison',
    'create_similitude_dashboard',
    'save_all_plots',
]

__version__ = '4.0.0'
