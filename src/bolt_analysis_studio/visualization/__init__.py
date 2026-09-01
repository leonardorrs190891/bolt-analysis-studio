"""
Visualization module for Bolt Analysis Studio.

Provides comprehensive plotting functions for:
- Preload vs cycles/time
- Loosening rate evolution
- Stage analysis (Jiang model)
- Friction coefficient evolution
- Wear depth evolution
- D-N curves
- Coupled evolution
- Dashboard summaries
"""

from .loosening_plots import (
    setup_plot_style,
    PreloadLossPlotter,
    FrictionEvolutionPlotter,
    WearEvolutionPlotter,
    DNPlotter,
    CoupledAnalysisPlotter,
    CoupledLooseningResultsPlotter,
    create_comprehensive_dashboard,
    quick_preload_loss_plot,
    quick_friction_plot
)

__all__ = [
    'setup_plot_style',
    'PreloadLossPlotter',
    'FrictionEvolutionPlotter',
    'WearEvolutionPlotter',
    'DNPlotter',
    'CoupledAnalysisPlotter',
    'CoupledLooseningResultsPlotter',
    'create_comprehensive_dashboard',
    'quick_preload_loss_plot',
    'quick_friction_plot'
]
