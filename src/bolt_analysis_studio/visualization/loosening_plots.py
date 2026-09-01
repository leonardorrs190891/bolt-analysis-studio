"""
Comprehensive Visualization Module for Bolt Analysis Studio
============================================================

This module provides extensive plotting capabilities for loosening phenomena:
- Preload loss over cycles (multiple models)
- Preload loss over time
- Loosening rate (dF/dN) evolution
- Friction coefficient evolution
- Wear evolution
- D-N curves (displacement-life)
- Stage identification plots
- Comparative analysis plots

Uses matplotlib with publication-quality formatting.

BAS +  R&D
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.axes import Axes
from matplotlib.gridspec import GridSpec
from matplotlib.ticker import ScalarFormatter, LogLocator
from typing import Dict, List, Tuple, Optional, Union
from dataclasses import dataclass
import warnings

# Import models (when available)
try:
    from .preload_loss_models import (
        BoltParameters, JointParameters, PreloadConditions,
        SingleExponentialModel, DoubleExponentialModel, 
        StretchedExponentialModel, PowerLawModel, LogarithmicModel,
        JiangTwoStageModel, JiangThreeStageModel,
        DNLooseningCurve, EmbeddingLossModel,
        generate_standard_test_data, LoadingType
    )
    from .friction_models import (
        FrictionEvolutionModel, FrictionEvolutionParameters,
        WearEvolutionModel, WearParameters, CoupledFrictionPreloadModel,
        LuGreFriction, LuGreParameters
    )
except ImportError:
    # For standalone testing
    pass


# =============================================================================
# STYLE CONFIGURATION (dynamic from central Theme)
# =============================================================================

from bolt_analysis_studio.gui.theme import Theme


def _get_colors():
    """Return COLORS dict from the current theme."""
    return Theme.get_plot_colors()

# For backwards compatibility: module-level name that resolves dynamically.
# Code using COLORS['blue'] etc. will work as long as it calls _get_colors()
# at use-time. We provide a lazy-dict wrapper to support existing call sites.

class _ThemeColorProxy(dict):
    """Dict-like object that always reads from Theme.get_plot_colors()."""
    def __getitem__(self, key):
        return Theme.get_plot_colors()[key]
    def get(self, key, default=None):
        return Theme.get_plot_colors().get(key, default)
    def __contains__(self, key):
        return key in Theme.get_plot_colors()
    def values(self):
        return Theme.get_plot_colors().values()
    def keys(self):
        return Theme.get_plot_colors().keys()
    def items(self):
        return Theme.get_plot_colors().items()

COLORS = _ThemeColorProxy()


class _ModelColorProxy(dict):
    """Dict-like that maps model names to current theme accent colors."""
    _MAP = {
        'single_exp': 'blue', 'double_exp': 'green',
        'stretched_exp': 'yellow', 'power_law': 'peach',
        'logarithmic': 'pink', 'jiang_2stage': 'mauve',
        'jiang_3stage': 'red', 'combined': 'teal',
    }
    def __getitem__(self, key):
        return Theme.get_plot_colors()[self._MAP[key]]
    def get(self, key, default=None):
        ckey = self._MAP.get(key)
        if ckey is None:
            return default
        return Theme.get_plot_colors().get(ckey, default)
    def __contains__(self, key):
        return key in self._MAP
    def values(self):
        c = Theme.get_plot_colors()
        return [c[v] for v in self._MAP.values()]
    def keys(self):
        return self._MAP.keys()
    def items(self):
        c = Theme.get_plot_colors()
        return [(k, c[v]) for k, v in self._MAP.items()]

MODEL_COLORS = _ModelColorProxy()


class _StageColorProxy(dict):
    """Dict-like that maps stage numbers to current theme colors."""
    _MAP = {1: 'green', 2: 'yellow', 3: 'red'}
    def __getitem__(self, key):
        return Theme.get_plot_colors()[self._MAP[key]]
    def get(self, key, default=None):
        ckey = self._MAP.get(key)
        if ckey is None:
            return default
        return Theme.get_plot_colors().get(ckey, default)
    def __contains__(self, key):
        return key in self._MAP

STAGE_COLORS = _StageColorProxy()


def setup_plot_style(dark_mode: bool = True):
    """Configure matplotlib style for professional plots."""
    plt.style.use(Theme.get_matplotlib_style_name())
    plt.rcParams.update(Theme.get_plot_style())


# =============================================================================
# PRELOAD LOSS PLOTS
# =============================================================================

class PreloadLossPlotter:
    """Comprehensive preload loss visualization"""
    
    def __init__(self, 
                 bolt: 'BoltParameters',
                 joint: 'JointParameters', 
                 conditions: 'PreloadConditions'):
        self.bolt = bolt
        self.joint = joint
        self.conditions = conditions
        self.F0 = conditions.initial_preload
        
    def plot_preload_vs_cycles(self, 
                               N_max: int = 10000,
                               models: List[str] = None,
                               log_scale: bool = False,
                               show_stages: bool = True,
                               ax: Optional[Axes] = None) -> Figure:
        """
        Plot preload loss over cycles for multiple models.
        
        Args:
            N_max: Maximum cycle count
            models: List of model names to include
            log_scale: Use logarithmic x-axis
            show_stages: Show Jiang stage boundaries
            ax: Optional axes to plot on
        """
        if models is None:
            models = ['double_exp', 'jiang_2stage', 'power_law']
            
        if ax is None:
            fig, ax = plt.subplots(figsize=(12, 7))
        else:
            fig = ax.figure
            
        # Create cycle array
        if log_scale:
            N = np.logspace(0, np.log10(N_max), 500)
        else:
            N = np.linspace(0, N_max, 500)
            
        # Plot each model
        for model_name in models:
            model = self._create_model(model_name)
            F = model.preload(N)
            F_norm = F / self.F0 * 100
            
            ax.plot(N, F_norm, 
                   label=self._get_model_label(model_name),
                   color=MODEL_COLORS.get(model_name, COLORS['blue']),
                   linewidth=2)
            
        # Stage boundaries for Jiang
        if show_stages and 'jiang_2stage' in models:
            ax.axvline(x=500, color=COLORS['overlay'], linestyle='--', 
                      linewidth=1, alpha=0.7)
            ax.text(520, 95, 'Stage I→II', fontsize=9, color=COLORS['subtext'])
            
        # Threshold lines
        ax.axhline(y=90, color=COLORS['yellow'], linestyle=':', 
                  linewidth=1, alpha=0.7, label='90% threshold')
        ax.axhline(y=80, color=COLORS['red'], linestyle=':', 
                  linewidth=1, alpha=0.7, label='80% threshold')
        
        ax.set_xlabel('Number of Cycles (N)')
        ax.set_ylabel('Preload Retention (%)')
        ax.set_title('Preload Loss vs. Loading Cycles\n(Multiple Models Comparison)')
        ax.legend(loc='lower left')
        ax.grid(True, alpha=0.3)
        ax.set_ylim([50, 105])
        
        if log_scale:
            ax.set_xscale('log')
            
        return fig
    
    def plot_preload_vs_time(self,
                            t_max: float = 100.0,
                            frequency: float = 25.0,
                            models: List[str] = None,
                            ax: Optional[Axes] = None) -> Figure:
        """
        Plot preload loss over time.
        
        Args:
            t_max: Maximum time in seconds
            frequency: Loading frequency (Hz)
            models: List of model names
        """
        if models is None:
            models = ['double_exp', 'jiang_2stage']
            
        if ax is None:
            fig, ax = plt.subplots(figsize=(12, 7))
        else:
            fig = ax.figure
            
        # Time and cycle arrays
        t = np.linspace(0, t_max, 500)
        N = t * frequency
        
        for model_name in models:
            model = self._create_model(model_name)
            F = model.preload(N)
            
            ax.plot(t, F / 1000,  # Convert to kN
                   label=self._get_model_label(model_name),
                   color=MODEL_COLORS.get(model_name, COLORS['blue']),
                   linewidth=2)
        
        # Add secondary x-axis for cycles
        ax2 = ax.twiny()
        ax2.set_xlim(ax.get_xlim())
        ax2.set_xlabel('Equivalent Cycles (N)', color=COLORS['subtext'])
        ax2.tick_params(axis='x', labelcolor=COLORS['subtext'])
        # Set tick positions for cycles
        cycle_ticks = np.array([0, 500, 1000, 1500, 2000, 2500])
        ax2.set_xticks(cycle_ticks / frequency)
        ax2.set_xticklabels([f'{int(c)}' for c in cycle_ticks])
        
        ax.set_xlabel('Time (s)')
        ax.set_ylabel('Preload Force (kN)')
        ax.set_title(f'Preload Loss vs. Time (f = {frequency} Hz)')
        ax.legend(loc='lower left')
        ax.grid(True, alpha=0.3)
        
        return fig
    
    def plot_loosening_rate(self,
                           N_max: int = 10000,
                           models: List[str] = None,
                           normalize: bool = True,
                           log_scale: bool = True,
                           ax: Optional[Axes] = None) -> Figure:
        """
        Plot loosening rate dF/dN vs. cycles.
        
        Shows evolution of decay rate through different stages.
        """
        if models is None:
            models = ['double_exp', 'jiang_2stage', 'jiang_3stage']
            
        if ax is None:
            fig, ax = plt.subplots(figsize=(12, 7))
        else:
            fig = ax.figure
            
        N = np.logspace(0, np.log10(N_max), 500) if log_scale else np.linspace(1, N_max, 500)
        
        for model_name in models:
            model = self._create_model(model_name)
            rate = -model.preload_rate(N)  # Negative for loss rate
            
            if normalize:
                rate = rate / self.F0 * 100  # Percent per cycle
                
            ax.plot(N, rate,
                   label=self._get_model_label(model_name),
                   color=MODEL_COLORS.get(model_name, COLORS['blue']),
                   linewidth=2)
        
        ax.set_xlabel('Number of Cycles (N)')
        ylabel = 'Loosening Rate (%/cycle)' if normalize else 'Loosening Rate (N/cycle)'
        ax.set_ylabel(ylabel)
        ax.set_title('Preload Loss Rate Evolution')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        if log_scale:
            ax.set_xscale('log')
            ax.set_yscale('log')
            
        return fig
    
    def plot_stage_analysis(self,
                           N_max: int = 100000,
                           ax: Optional[Axes] = None) -> Figure:
        """
        Plot Jiang three-stage model with stage identification.
        
        Stage I: Rapid plastic deformation (green)
        Stage II: Linear rotational loosening (yellow)  
        Stage III: Fatigue acceleration (red)
        """
        if ax is None:
            fig, ax = plt.subplots(figsize=(12, 7))
        else:
            fig = ax.figure
            
        model = JiangThreeStageModel(
            self.bolt, self.joint, self.conditions,
            N_trans_12=500, N_trans_23=50000,
            delta_F1_ratio=0.15, N1=50, k2=3.0, k3=0.5, n3=1.5
        )
        
        N = np.logspace(0, np.log10(N_max), 1000)
        F = model.preload(N)
        stages = model.get_stage(N)
        
        # Plot each stage with different colors
        for stage in [1, 2, 3]:
            mask = stages == stage
            if np.any(mask):
                ax.plot(N[mask], F[mask] / 1000,
                       color=STAGE_COLORS[stage],
                       linewidth=2.5,
                       label=f'Stage {["I", "II", "III"][stage-1]}')
        
        # Add stage boundary lines
        ax.axvline(x=model.N_trans_12, color=COLORS['overlay'], 
                  linestyle='--', linewidth=1.5)
        ax.axvline(x=model.N_trans_23, color=COLORS['overlay'],
                  linestyle='--', linewidth=1.5)
        
        # Annotations
        ax.annotate('Stage I\nPlastic Deformation', 
                   xy=(100, self.F0/1000*0.92), fontsize=9,
                   color=STAGE_COLORS[1])
        ax.annotate('Stage II\nRotational Loosening',
                   xy=(5000, model.F_trans_12/1000*0.9), fontsize=9,
                   color=STAGE_COLORS[2])
        ax.annotate('Stage III\nFatigue Acceleration',
                   xy=(60000, model.F_trans_23/1000*0.85), fontsize=9,
                   color=STAGE_COLORS[3])
        
        ax.set_xscale('log')
        ax.set_xlabel('Number of Cycles (N)')
        ax.set_ylabel('Preload Force (kN)')
        ax.set_title('Jiang Three-Stage Loosening Model')
        ax.legend(loc='lower left')
        ax.grid(True, alpha=0.3)
        
        return fig
    
    def plot_model_comparison(self,
                             N_max: int = 5000,
                             ax: Optional[Axes] = None) -> Figure:
        """
        Comprehensive comparison of all preload loss models.
        """
        if ax is None:
            fig, ax = plt.subplots(figsize=(14, 8))
        else:
            fig = ax.figure
            
        models = ['single_exp', 'double_exp', 'stretched_exp', 
                 'power_law', 'logarithmic', 'jiang_2stage']
        
        N = np.linspace(0, N_max, 500)
        
        for model_name in models:
            model = self._create_model(model_name)
            F_norm = model.normalized_preload(N) * 100
            
            ax.plot(N, F_norm,
                   label=self._get_model_label(model_name),
                   color=MODEL_COLORS.get(model_name, COLORS['blue']),
                   linewidth=2)
        
        # Thresholds
        ax.axhline(y=90, color=COLORS['yellow'], linestyle=':', alpha=0.7)
        ax.axhline(y=80, color=COLORS['red'], linestyle=':', alpha=0.7)
        
        ax.set_xlabel('Number of Cycles (N)')
        ax.set_ylabel('Preload Retention (%)')
        ax.set_title('Comprehensive Preload Loss Model Comparison')
        ax.legend(loc='lower left', ncol=2)
        ax.grid(True, alpha=0.3)
        ax.set_ylim([40, 105])
        
        return fig
    
    def _create_model(self, model_name: str):
        """Create model instance by name"""
        models = {
            'single_exp': lambda: SingleExponentialModel(
                self.bolt, self.joint, self.conditions,
                lambda_decay=0.005, F_inf_ratio=0.6
            ),
            'double_exp': lambda: DoubleExponentialModel(
                self.bolt, self.joint, self.conditions,
                lambda1=0.05, lambda2=0.005, A1_ratio=0.15, 
                A2_ratio=0.25, F_inf_ratio=0.6
            ),
            'stretched_exp': lambda: StretchedExponentialModel(
                self.bolt, self.joint, self.conditions,
                N0=500, beta=0.5
            ),
            'power_law': lambda: PowerLawModel(
                self.bolt, self.joint, self.conditions,
                alpha=0.15, Nc=10
            ),
            'logarithmic': lambda: LogarithmicModel(
                self.bolt, self.joint, self.conditions,
                k=2000
            ),
            'jiang_2stage': lambda: JiangTwoStageModel(
                self.bolt, self.joint, self.conditions,
                N_trans=500, delta_F_embed_ratio=0.12, N1=50, k2=5.0
            ),
            'jiang_3stage': lambda: JiangThreeStageModel(
                self.bolt, self.joint, self.conditions,
                N_trans_12=500, N_trans_23=50000,
                delta_F1_ratio=0.15, N1=50, k2=3.0, k3=0.5, n3=1.5
            ),
        }
        return models[model_name]()
    
    def _get_model_label(self, model_name: str) -> str:
        """Get display label for model"""
        labels = {
            'single_exp': 'Single Exponential',
            'double_exp': 'Double Exponential (Li et al.)',
            'stretched_exp': 'Stretched Exponential (KWW)',
            'power_law': 'Power Law (Lu et al.)',
            'logarithmic': 'Logarithmic',
            'jiang_2stage': 'Jiang Two-Stage',
            'jiang_3stage': 'Jiang Three-Stage',
            'combined': 'Combined Model',
        }
        return labels.get(model_name, model_name)


# =============================================================================
# FRICTION EVOLUTION PLOTS
# =============================================================================

class FrictionEvolutionPlotter:
    """Visualization for friction coefficient evolution"""
    
    def __init__(self, params: 'FrictionEvolutionParameters' = None):
        if params is None:
            params = FrictionEvolutionParameters(
                mu_initial=0.14, mu_peak=0.18, mu_steady=0.12,
                N1=50, N2=500, N3=5000, 
                beta_degrade=0.01, N_critical=1e5
            )
        self.model = FrictionEvolutionModel(params)
        self.params = params
        
    def plot_friction_evolution(self,
                                N_max: int = 200000,
                                log_scale: bool = True,
                                ax: Optional[Axes] = None) -> Figure:
        """
        Plot friction coefficient evolution over cycles.
        
        Shows three-phase behavior:
        - Running-in (rise to peak)
        - Stabilization (decay to steady-state)
        - Degradation (slow change at high cycles)
        """
        if ax is None:
            fig, ax = plt.subplots(figsize=(12, 7))
        else:
            fig = ax.figure
            
        N = np.logspace(0, np.log10(N_max), 500) if log_scale else np.linspace(1, N_max, 500)
        mu = self.model.friction_coefficient(N)
        
        # Plot main curve
        ax.plot(N, mu, color=COLORS['mauve'], linewidth=2.5, label='μ(N)')
        
        # Reference lines
        ax.axhline(y=self.params.mu_initial, color=COLORS['blue'], 
                  linestyle='--', alpha=0.7, label=f'μ₀ = {self.params.mu_initial}')
        ax.axhline(y=self.params.mu_peak, color=COLORS['peach'],
                  linestyle='--', alpha=0.7, label=f'μ_peak = {self.params.mu_peak}')
        ax.axhline(y=self.params.mu_steady, color=COLORS['green'],
                  linestyle='--', alpha=0.7, label=f'μ_ss = {self.params.mu_steady}')
        
        # Phase regions
        ax.axvspan(1, self.params.N1 * 2, alpha=0.1, color=COLORS['blue'], label='Running-in')
        ax.axvspan(self.params.N1 * 2, self.params.N_critical, alpha=0.1, 
                  color=COLORS['green'], label='Steady-state')
        ax.axvspan(self.params.N_critical, N_max, alpha=0.1, 
                  color=COLORS['red'], label='Degradation')
        
        if log_scale:
            ax.set_xscale('log')
            
        ax.set_xlabel('Number of Cycles (N)')
        ax.set_ylabel('Friction Coefficient (μ)')
        ax.set_title('Friction Coefficient Evolution (Hintikka Three-Phase Model)')
        ax.legend(loc='upper right')
        ax.grid(True, alpha=0.3)
        ax.set_ylim([0.05, 0.25])
        
        return fig
    
    def plot_friction_rate(self,
                          N_max: int = 200000,
                          ax: Optional[Axes] = None) -> Figure:
        """Plot friction change rate dμ/dN"""
        if ax is None:
            fig, ax = plt.subplots(figsize=(12, 7))
        else:
            fig = ax.figure
            
        N = np.logspace(0, np.log10(N_max), 500)
        rate = self.model.friction_rate(N)
        
        # Separate positive and negative rates
        pos_rate = np.maximum(rate, 0)
        neg_rate = np.minimum(rate, 0)
        
        ax.fill_between(N, 0, pos_rate * 1000, alpha=0.5, 
                       color=COLORS['green'], label='Increasing μ')
        ax.fill_between(N, 0, neg_rate * 1000, alpha=0.5,
                       color=COLORS['red'], label='Decreasing μ')
        ax.plot(N, rate * 1000, color=COLORS['text'], linewidth=1)
        
        ax.axhline(y=0, color=COLORS['overlay'], linestyle='-', linewidth=0.5)
        
        ax.set_xscale('log')
        ax.set_xlabel('Number of Cycles (N)')
        ax.set_ylabel('Friction Rate (×10⁻³ per cycle)')
        ax.set_title('Friction Coefficient Change Rate')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        return fig


# =============================================================================
# WEAR EVOLUTION PLOTS
# =============================================================================

class WearEvolutionPlotter:
    """Visualization for wear evolution"""
    
    def __init__(self, 
                 initial_preload: float = 50000,
                 contact_pressure: float = 500,
                 displacement_amplitude: float = 0.5,
                 friction_coefficient: float = 0.12):
        self.F0 = initial_preload
        self.p_contact = contact_pressure
        self.delta = displacement_amplitude
        self.mu = friction_coefficient
        
        # Create wear model
        wear_params = WearParameters(
            K_archard=1e-6,
            k_dimensional=1e-8,
            hardness=3000,
            alpha_fouvry=3e-8
        )
        self.wear_model = WearEvolutionModel(
            wear_params, initial_stiffness=5e5, wear_to_stiffness_ratio=0.1
        )
        
    def plot_wear_depth_evolution(self,
                                  N_max: int = 100000,
                                  ax: Optional[Axes] = None) -> Figure:
        """Plot cumulative wear depth over cycles"""
        if ax is None:
            fig, ax = plt.subplots(figsize=(12, 7))
        else:
            fig = ax.figure
            
        N = np.linspace(0, N_max, 500)
        
        # Archard wear
        sliding_per_cycle = 4 * self.delta
        h_archard = (self.wear_model.wear_model.params.K_archard * 
                    self.p_contact * sliding_per_cycle * N / 
                    self.wear_model.wear_model.params.hardness)
        
        ax.plot(N, h_archard * 1000, color=COLORS['peach'], 
               linewidth=2.5, label='Archard Wear')
        
        # Fouvry energy-based (proportional to dissipated energy)
        E_per_cycle = self.mu * self.p_contact * self.delta
        h_fouvry = self.wear_model.wear_model.params.alpha_fouvry * E_per_cycle * N
        ax.plot(N, h_fouvry * 1000, color=COLORS['teal'],
               linewidth=2.5, label='Fouvry Energy-Based')
        
        ax.set_xlabel('Number of Cycles (N)')
        ax.set_ylabel('Cumulative Wear Depth (μm)')
        ax.set_title('Wear Depth Evolution: Archard vs. Fouvry Models')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        return fig
    
    def plot_stiffness_degradation(self,
                                   N_max: int = 100000,
                                   ax: Optional[Axes] = None) -> Figure:
        """Plot stiffness reduction due to wear"""
        if ax is None:
            fig, ax = plt.subplots(figsize=(12, 7))
        else:
            fig = ax.figure
            
        N = np.linspace(0, N_max, 500)
        k = self.wear_model.stiffness_evolution(
            N, self.p_contact, self.delta, self.mu
        )
        
        k_ratio = k / self.wear_model.k0 * 100
        
        ax.plot(N, k_ratio, color=COLORS['blue'], linewidth=2.5)
        
        # Danger zone
        ax.axhline(y=80, color=COLORS['yellow'], linestyle='--', 
                  alpha=0.7, label='20% reduction warning')
        ax.axhline(y=50, color=COLORS['red'], linestyle='--',
                  alpha=0.7, label='50% reduction limit')
        ax.fill_between(N, 50, k_ratio, where=k_ratio < 80, 
                       alpha=0.2, color=COLORS['yellow'])
        
        ax.set_xlabel('Number of Cycles (N)')
        ax.set_ylabel('Relative Stiffness (%)')
        ax.set_title('Contact Stiffness Degradation Due to Wear')
        ax.legend()
        ax.grid(True, alpha=0.3)
        ax.set_ylim([40, 105])
        
        return fig


# =============================================================================
# D-N CURVE PLOTS
# =============================================================================

class DNPlotter:
    """D-N curve (displacement-life) visualization"""
    
    def __init__(self):
        self.dn_curve = DNLooseningCurve(
            d_threshold=0.1, C1=5.0, m1=3.0, 
            C2=4.0, m2=1.5, d_transition=0.5
        )
        
    def plot_dn_curve(self,
                     d_range: Tuple[float, float] = (0.05, 5.0),
                     ax: Optional[Axes] = None) -> Figure:
        """
        Plot D-N curve (displacement vs. cycles to loosening).
        
        Analogous to S-N fatigue curve.
        """
        if ax is None:
            fig, ax = plt.subplots(figsize=(12, 7))
        else:
            fig = ax.figure
            
        d = np.logspace(np.log10(d_range[0]), np.log10(d_range[1]), 100)
        N = self.dn_curve.cycles_to_loosening(d)
        
        # Filter infinite lives
        valid = np.isfinite(N)
        
        ax.loglog(d[valid], N[valid], color=COLORS['mauve'], 
                 linewidth=2.5, label='D-N Curve')
        
        # Threshold line
        ax.axvline(x=self.dn_curve.d_threshold, color=COLORS['green'],
                  linestyle='--', alpha=0.7, label=f'd_th = {self.dn_curve.d_threshold} mm')
        
        # Bilinear transition
        ax.axvline(x=self.dn_curve.d_transition, color=COLORS['yellow'],
                  linestyle=':', alpha=0.7, label=f'd_trans = {self.dn_curve.d_transition} mm')
        
        # Sample points (experimental data representation)
        d_exp = np.array([0.2, 0.3, 0.5, 0.7, 1.0, 1.5, 2.0])
        N_exp = self.dn_curve.cycles_to_loosening(d_exp)
        # Add some scatter
        N_exp_scatter = N_exp * (1 + 0.2 * (np.random.rand(len(d_exp)) - 0.5))
        ax.scatter(d_exp, N_exp_scatter, color=COLORS['peach'], 
                  s=60, zorder=5, label='Experimental data')
        
        ax.set_xlabel('Displacement Amplitude (mm)')
        ax.set_ylabel('Cycles to Loosening (N_L)')
        ax.set_title('D-N Curve: Displacement-Life Relationship')
        ax.legend()
        ax.grid(True, alpha=0.3, which='both')
        
        # Add endurance limit region
        ax.fill_between([d_range[0], self.dn_curve.d_threshold],
                       [1, 1], [1e8, 1e8], alpha=0.1, color=COLORS['green'],
                       label='Endurance region')
        
        return fig


# =============================================================================
# COUPLED ANALYSIS PLOTS
# =============================================================================

class CoupledAnalysisPlotter:
    """Visualization for coupled friction-preload-wear analysis"""
    
    def __init__(self,
                 friction_params: 'FrictionEvolutionParameters' = None,
                 initial_preload: float = 50000,
                 k_bolt: float = 5e5,
                 k_member: float = 1.5e6):
        if friction_params is None:
            friction_params = FrictionEvolutionParameters()
            
        self.coupled_model = CoupledFrictionPreloadModel(
            friction_params, initial_preload, k_bolt, k_member
        )
        self.F0 = initial_preload
        
    def plot_coupled_evolution(self,
                              N_max: int = 50000,
                              ax: Optional[Axes] = None) -> Figure:
        """Plot coupled friction and preload evolution"""
        if ax is None:
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10), sharex=True)
        else:
            fig = ax.figure
            ax1, ax2 = fig.subplots(2, 1, sharex=True)
            
        # Run coupled simulation
        results = self.coupled_model.coupled_evolution(N_max)
        
        # Preload plot
        ax1.plot(results['cycles'], results['preload'] / 1000,
                color=COLORS['blue'], linewidth=2, label='Coupled Model')
        ax1.axhline(y=self.F0 * 0.9 / 1000, color=COLORS['yellow'],
                   linestyle='--', alpha=0.7)
        ax1.set_ylabel('Preload (kN)')
        ax1.set_title('Coupled Friction-Preload Evolution')
        ax1.legend(loc='lower left')
        ax1.grid(True, alpha=0.3)
        
        # Friction plot
        ax2.plot(results['cycles'], results['friction'],
                color=COLORS['mauve'], linewidth=2)
        ax2.set_xlabel('Number of Cycles (N)')
        ax2.set_ylabel('Friction Coefficient (μ)')
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        return fig


# =============================================================================
# COMPREHENSIVE DASHBOARD
# =============================================================================

def create_comprehensive_dashboard(
    bolt: 'BoltParameters',
    joint: 'JointParameters',
    conditions: 'PreloadConditions',
    N_max: int = 50000,
    save_path: Optional[str] = None
) -> Figure:
    """
    Create comprehensive dashboard with all loosening phenomena plots.
    
    Includes:
    - Preload vs. cycles (multiple models)
    - Loosening rate evolution
    - Stage analysis
    - Friction evolution
    - Wear evolution
    - D-N curve
    """
    setup_plot_style(dark_mode=True)
    
    fig = plt.figure(figsize=(20, 16))
    gs = GridSpec(3, 3, figure=fig, hspace=0.3, wspace=0.3)
    
    # Initialize plotters
    preload_plotter = PreloadLossPlotter(bolt, joint, conditions)
    friction_plotter = FrictionEvolutionPlotter()
    wear_plotter = WearEvolutionPlotter(initial_preload=conditions.initial_preload)
    dn_plotter = DNPlotter()
    
    # 1. Preload vs Cycles (top left, large)
    ax1 = fig.add_subplot(gs[0, :2])
    preload_plotter.plot_preload_vs_cycles(
        N_max=N_max, 
        models=['double_exp', 'jiang_2stage', 'power_law'],
        ax=ax1
    )
    
    # 2. Loosening Rate (top right)
    ax2 = fig.add_subplot(gs[0, 2])
    preload_plotter.plot_loosening_rate(
        N_max=N_max,
        models=['double_exp', 'jiang_2stage'],
        ax=ax2
    )
    
    # 3. Stage Analysis (middle left)
    ax3 = fig.add_subplot(gs[1, 0])
    preload_plotter.plot_stage_analysis(N_max=100000, ax=ax3)
    
    # 4. Friction Evolution (middle center)
    ax4 = fig.add_subplot(gs[1, 1])
    friction_plotter.plot_friction_evolution(N_max=200000, ax=ax4)
    
    # 5. Wear Evolution (middle right)
    ax5 = fig.add_subplot(gs[1, 2])
    wear_plotter.plot_wear_depth_evolution(N_max=100000, ax=ax5)
    
    # 6. D-N Curve (bottom left)
    ax6 = fig.add_subplot(gs[2, 0])
    dn_plotter.plot_dn_curve(ax=ax6)
    
    # 7. Model Comparison (bottom center and right)
    ax7 = fig.add_subplot(gs[2, 1:])
    preload_plotter.plot_model_comparison(N_max=5000, ax=ax7)
    
    # Title
    fig.suptitle('Bolt Analysis Studio - Comprehensive Loosening Analysis Dashboard\n'
                f'M{bolt.diameter} L7 Stud, F₀ = {conditions.initial_preload/1000:.1f} kN',
                fontsize=14, color=COLORS['text'])
    
    if save_path:
        fig.savefig(save_path, dpi=300, facecolor=fig.get_facecolor())
        
    return fig


# =============================================================================
# QUICK PLOT FUNCTIONS
# =============================================================================

def quick_preload_loss_plot(N_max: int = 10000, 
                           models: List[str] = None,
                           save_path: Optional[str] = None) -> Figure:
    """Quick function to generate preload loss plot with default parameters"""
    setup_plot_style()
    
    # Use standard test data
    data = generate_standard_test_data()
    plotter = PreloadLossPlotter(data['bolt'], data['joint'], data['conditions'])
    
    if models is None:
        models = ['double_exp', 'jiang_2stage', 'power_law']
        
    fig = plotter.plot_preload_vs_cycles(N_max=N_max, models=models)
    
    if save_path:
        fig.savefig(save_path, dpi=300)
        
    return fig


def quick_friction_plot(N_max: int = 100000,
                       save_path: Optional[str] = None) -> Figure:
    """Quick function to generate friction evolution plot"""
    setup_plot_style()
    
    plotter = FrictionEvolutionPlotter()
    fig = plotter.plot_friction_evolution(N_max=N_max)
    
    if save_path:
        fig.savefig(save_path, dpi=300)
        
    return fig


# =============================================================================
# COUPLED LOOSENING RESULTS PLOTTER
# =============================================================================

class CoupledLooseningResultsPlotter:
    """
    Visualization for CoupledLooseningAnalyzer results.

    Plots the coupled friction-wear-loosening analysis including:
    - Preload ratio and friction evolution
    - Loosening rate vs cycles
    - Torque balance (T_pitch vs T_resistance)
    - Wear accumulation
    - Phase/risk classification
    - Critical friction threshold

    Usage:
        from numerical.coupled_loosening_analyzer import (
            CoupledLooseningAnalyzer, create_m16_analyzer
        )

        analyzer = create_m16_analyzer(mu_initial=0.12)
        results = analyzer.run_analysis(preload_initial=50000, F_transverse=8000, n_cycles=2000)

        plotter = CoupledLooseningResultsPlotter()
        fig = plotter.plot_comprehensive_dashboard(results, analyzer)
    """

    def __init__(self):
        setup_plot_style(dark_mode=True)

    def plot_preload_friction_evolution(self,
                                        results: 'LooseningResults',
                                        ax1: Optional[Axes] = None,
                                        ax2: Optional[Axes] = None) -> Figure:
        """
        Plot preload ratio and friction coefficient evolution.

        Two-panel plot:
        - Top: Preload retention percentage
        - Bottom: Friction coefficient with critical threshold
        """
        if ax1 is None or ax2 is None:
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True)
        else:
            fig = ax1.figure

        cycles = results.cycles

        # Top panel: Preload ratio
        ax1.plot(cycles, results.preload_ratio * 100,
                color=COLORS['blue'], linewidth=2.5, label='Preload Retention')

        # Threshold lines
        ax1.axhline(y=90, color=COLORS['yellow'], linestyle='--',
                   linewidth=1, alpha=0.7, label='90% threshold')
        ax1.axhline(y=80, color=COLORS['peach'], linestyle='--',
                   linewidth=1, alpha=0.7, label='80% threshold')
        ax1.axhline(y=50, color=COLORS['red'], linestyle='--',
                   linewidth=1, alpha=0.7, label='50% critical')

        ax1.set_ylabel('Preload Retention (%)')
        ax1.set_title('Coupled Friction-Wear-Loosening Analysis')
        ax1.legend(loc='lower left')
        ax1.grid(True, alpha=0.3)
        ax1.set_ylim([0, 105])

        # Bottom panel: Friction coefficient
        ax2.plot(cycles, results.mu_thread, color=COLORS['mauve'],
                linewidth=2.5, label='μ_thread')
        ax2.plot(cycles, results.mu_bearing, color=COLORS['teal'],
                linewidth=2, linestyle='--', label='μ_bearing')

        ax2.set_xlabel('Number of Cycles (N)')
        ax2.set_ylabel('Friction Coefficient (μ)')
        ax2.legend(loc='upper right')
        ax2.grid(True, alpha=0.3)
        ax2.set_ylim([0, 0.25])

        plt.tight_layout()
        return fig

    def plot_loosening_rate_evolution(self,
                                      results: 'LooseningResults',
                                      log_scale: bool = False,
                                      ax: Optional[Axes] = None) -> Figure:
        """
        Plot loosening rate (deg/cycle) evolution.

        Shows how loosening accelerates through phases.
        """
        if ax is None:
            fig, ax = plt.subplots(figsize=(12, 7))
        else:
            fig = ax.figure

        cycles = results.cycles
        rate = results.loosening_rate  # Already in deg/cycle

        # Main rate curve
        ax.plot(cycles, rate, color=COLORS['red'], linewidth=2.5,
               label='Loosening Rate')

        # Fill under curve to show accumulation
        ax.fill_between(cycles, 0, rate, alpha=0.3, color=COLORS['red'])

        # Annotation for max rate
        max_idx = np.argmax(rate)
        if rate[max_idx] > 0:
            ax.annotate(f'Max: {rate[max_idx]:.4f}°/cycle',
                       xy=(cycles[max_idx], rate[max_idx]),
                       xytext=(cycles[max_idx] * 0.7, rate[max_idx] * 1.2),
                       fontsize=9, color=COLORS['text'],
                       arrowprops=dict(arrowstyle='->', color=COLORS['overlay']))

        ax.set_xlabel('Number of Cycles (N)')
        ax.set_ylabel('Loosening Rate (°/cycle)')
        ax.set_title('Loosening Rate Evolution\n(dθ/dN over cycles)')
        ax.legend()
        ax.grid(True, alpha=0.3)

        if log_scale and np.any(rate > 0):
            ax.set_yscale('log')

        return fig

    def plot_torque_balance(self,
                           results: 'LooseningResults',
                           ax: Optional[Axes] = None) -> Figure:
        """
        Plot torque balance evolution: T_pitch vs T_resistance.

        Shows margin erosion leading to loosening.
        """
        if ax is None:
            fig, ax = plt.subplots(figsize=(12, 7))
        else:
            fig = ax.figure

        cycles = results.cycles

        # Extract torques from states
        if results.states:
            T_pitch = np.array([s.T_pitch for s in results.states])
            T_resistance = np.array([s.T_resistance for s in results.states])
            T_thread = np.array([s.T_thread for s in results.states])
            T_bearing = np.array([s.T_bearing for s in results.states])
            state_cycles = np.array([s.cycle for s in results.states])
        else:
            # Fallback - use torque margin to estimate
            state_cycles = cycles
            T_pitch = results.preload * 0.002 / (2 * np.pi)  # Estimate
            T_resistance = T_pitch * results.torque_margin
            T_thread = T_resistance * 0.4
            T_bearing = T_resistance * 0.6

        # Plot torques
        ax.plot(state_cycles, T_pitch, color=COLORS['red'], linewidth=2.5,
               label='T_pitch (drives loosening)')
        ax.plot(state_cycles, T_resistance, color=COLORS['green'], linewidth=2.5,
               label='T_resistance (resists loosening)')
        ax.plot(state_cycles, T_thread, color=COLORS['blue'], linewidth=1.5,
               linestyle='--', label='T_thread')
        ax.plot(state_cycles, T_bearing, color=COLORS['teal'], linewidth=1.5,
               linestyle='--', label='T_bearing')

        # Fill between showing margin
        ax.fill_between(state_cycles, T_pitch, T_resistance,
                       where=T_resistance >= T_pitch,
                       alpha=0.2, color=COLORS['green'], label='Safety margin')
        ax.fill_between(state_cycles, T_pitch, T_resistance,
                       where=T_resistance < T_pitch,
                       alpha=0.2, color=COLORS['red'], label='Loosening zone')

        ax.set_xlabel('Number of Cycles (N)')
        ax.set_ylabel('Torque (N·m)')
        ax.set_title('Torque Balance: Driving vs. Resisting Torques\n'
                    '(Loosening occurs when T_pitch > T_resistance)')
        ax.legend(loc='upper right')
        ax.grid(True, alpha=0.3)

        return fig

    def plot_wear_accumulation(self,
                              results: 'LooseningResults',
                              ax: Optional[Axes] = None) -> Figure:
        """
        Plot wear depth accumulation over cycles with time-varying phases.

        Shows:
        - Total wear depth evolution
        - Wear phases (running-in, steady-state, severe, catastrophic)
        - Wear rate (secondary axis)
        - Severity zones
        """
        if ax is None:
            fig, ax = plt.subplots(figsize=(12, 7))
        else:
            fig = ax.figure

        cycles = results.cycles
        wear = results.total_wear_um

        # Define wear phase boundaries (in micrometers)
        RUNNING_IN_CYCLES = 100
        SEVERE_WEAR_UM = 50
        CATASTROPHIC_WEAR_UM = 100

        # Color regions for wear phases
        # Running-in phase
        running_in_mask = cycles <= RUNNING_IN_CYCLES
        if np.any(running_in_mask):
            ax.axvspan(cycles[0], min(RUNNING_IN_CYCLES, cycles[-1]),
                      alpha=0.15, color=COLORS['blue'], label='Running-in')

        # Steady-state phase region (between running-in and severe wear threshold)
        steady_end_idx = np.argmax(wear >= SEVERE_WEAR_UM) if np.any(wear >= SEVERE_WEAR_UM) else len(wear)-1
        if steady_end_idx > 0 and RUNNING_IN_CYCLES < cycles[-1]:
            ax.axvspan(RUNNING_IN_CYCLES, cycles[steady_end_idx],
                      alpha=0.1, color=COLORS['green'], label='Steady-state')

        # Severe wear region
        severe_mask = wear >= SEVERE_WEAR_UM
        if np.any(severe_mask):
            severe_start = cycles[np.argmax(severe_mask)]
            cat_start = cycles[np.argmax(wear >= CATASTROPHIC_WEAR_UM)] if np.any(wear >= CATASTROPHIC_WEAR_UM) else cycles[-1]
            ax.axvspan(severe_start, cat_start, alpha=0.15, color=COLORS['peach'], label='Severe')

        # Catastrophic wear region
        if np.any(wear >= CATASTROPHIC_WEAR_UM):
            cat_start = cycles[np.argmax(wear >= CATASTROPHIC_WEAR_UM)]
            ax.axvspan(cat_start, cycles[-1], alpha=0.2, color=COLORS['red'], label='Catastrophic')

        # Main wear curve
        ax.plot(cycles, wear, color=COLORS['peach'], linewidth=2.5,
               label='Total Wear', zorder=3)
        ax.fill_between(cycles, 0, wear, alpha=0.2, color=COLORS['peach'])

        # Severity threshold lines
        ax.axhline(y=10, color=COLORS['yellow'], linestyle='--',
                  linewidth=1.5, alpha=0.8)
        ax.annotate('Light (10 μm)', xy=(cycles[-1] * 0.02, 11),
                   fontsize=9, color=COLORS['yellow'])

        ax.axhline(y=SEVERE_WEAR_UM, color=COLORS['peach'], linestyle='--',
                  linewidth=1.5, alpha=0.8)
        ax.annotate(f'Severe ({SEVERE_WEAR_UM} μm)', xy=(cycles[-1] * 0.02, SEVERE_WEAR_UM + 2),
                   fontsize=9, color=COLORS['peach'])

        ax.axhline(y=CATASTROPHIC_WEAR_UM, color=COLORS['red'], linestyle='--',
                  linewidth=1.5, alpha=0.8)
        ax.annotate(f'Catastrophic ({CATASTROPHIC_WEAR_UM} μm)', xy=(cycles[-1] * 0.02, CATASTROPHIC_WEAR_UM + 2),
                   fontsize=9, color=COLORS['red'])

        # Wear rate on secondary axis
        ax2 = ax.twinx()
        if len(wear) > 5:
            # Compute wear rate (smoothed derivative)
            wear_rate = np.gradient(wear, cycles)
            # Smooth it
            window = min(10, len(wear_rate) // 5)
            if window > 1:
                wear_rate_smooth = np.convolve(wear_rate, np.ones(window)/window, mode='same')
            else:
                wear_rate_smooth = wear_rate

            ax2.plot(cycles, wear_rate_smooth * 1000, color=COLORS['teal'], linewidth=1.5,
                    linestyle='--', alpha=0.7, label='Wear Rate')
            ax2.set_ylabel('Wear Rate (nm/cycle)', color=COLORS['teal'], fontsize=10)
            ax2.tick_params(axis='y', labelcolor=COLORS['teal'])

            # Set reasonable y-limits for rate
            rate_max = np.percentile(wear_rate_smooth * 1000, 95)
            if rate_max > 0:
                ax2.set_ylim([0, rate_max * 1.2])

        ax.set_xlabel('Number of Cycles (N)', fontsize=11)
        ax.set_ylabel('Wear Depth (μm)', fontsize=11)
        ax.set_title('Cumulative Wear Depth with Phase Evolution', fontsize=12, fontweight='bold')

        # Combined legend
        lines1, labels1 = ax.get_legend_handles_labels()
        ax.legend(lines1, labels1, loc='upper left', fontsize=9, ncol=2)

        ax.grid(True, alpha=0.3)

        # Set y-limit with some headroom
        max_wear = np.max(wear) if len(wear) > 0 else 10
        ax.set_ylim([0, max(max_wear * 1.2, CATASTROPHIC_WEAR_UM * 1.1)])

        return fig

    def plot_torque_margin_evolution(self,
                                     results: 'LooseningResults',
                                     analyzer: 'CoupledLooseningAnalyzer' = None,
                                     ax: Optional[Axes] = None) -> Figure:
        """
        Plot torque margin and critical friction threshold.
        """
        if ax is None:
            fig, ax = plt.subplots(figsize=(12, 7))
        else:
            fig = ax.figure

        cycles = results.cycles
        margin = results.torque_margin

        # Main margin curve
        ax.plot(cycles, margin, color=COLORS['blue'], linewidth=2.5,
               label='Torque Margin (T_res/T_pitch)')

        # Critical threshold line
        ax.axhline(y=1.0, color=COLORS['red'], linestyle='-',
                  linewidth=2, label='Loosening threshold')

        # Safety zones
        ax.fill_between(cycles, 1.0, margin, where=margin >= 1.0,
                       alpha=0.2, color=COLORS['green'])
        ax.fill_between(cycles, 1.0, margin, where=margin < 1.0,
                       alpha=0.2, color=COLORS['red'])

        # Risk zones
        ax.axhline(y=1.5, color=COLORS['yellow'], linestyle='--',
                  linewidth=1, alpha=0.7, label='Low risk (margin > 1.5)')
        ax.axhline(y=2.0, color=COLORS['green'], linestyle='--',
                  linewidth=1, alpha=0.7, label='Negligible risk (margin > 2.0)')

        ax.set_xlabel('Number of Cycles (N)')
        ax.set_ylabel('Torque Margin (dimensionless)')
        ax.set_title('Torque Margin Evolution\n(Loosening when margin < 1.0)')
        ax.legend(loc='upper right')
        ax.grid(True, alpha=0.3)

        # Add critical friction annotation if analyzer provided
        if analyzer:
            mu_crit = analyzer.compute_critical_friction()
            ax.annotate(f'μ_crit = {mu_crit:.4f}',
                       xy=(cycles[-1] * 0.7, 1.5),
                       fontsize=10, color=COLORS['text'],
                       bbox=dict(boxstyle='round', facecolor=COLORS['surface'],
                                edgecolor=COLORS['overlay']))

        return fig

    def plot_phase_diagram(self,
                          results: 'LooseningResults',
                          ax: Optional[Axes] = None) -> Figure:
        """
        Comprehensive Phase Diagram for Loosening Analysis.

        Creates a 3-panel visualization showing:
        - Top: Preload retention with S-curve fit and phase backgrounds
        - Middle: Torque margin and friction margin evolution
        - Bottom: Nut rotation angle accumulation

        Phases (based on Jiang 2003 two-stage model):
        - STABLE: Torque margin > 1.5, no loosening
        - NON_ROTATIONAL: Stage I - Plastic deformation at thread roots
        - TRANSITION: Approaching critical friction, intermittent slip
        - ROTATIONAL: Stage II - Junker mechanism active
        - RUNAWAY: Rapid loosening, near-zero resisting torque

        Key improvements:
        - S-curve overlay showing two-stage model fit
        - Critical milestone markers (onset, 50% loss, Stage I/II transition)
        - Nut rotation visualization
        - Better phase region visualization
        """
        if ax is None:
            fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(14, 10),
                                                 sharex=True,
                                                 height_ratios=[2.5, 1.5, 1])
            fig.subplots_adjust(hspace=0.1)
        else:
            fig = ax.figure
            ax1 = ax
            ax2 = None
            ax3 = None

        if not results.states:
            ax1.text(0.5, 0.5, 'No state data available',
                    ha='center', va='center', transform=ax1.transAxes,
                    fontsize=12, color=COLORS['text'])
            return fig

        cycles = np.array([s.cycle for s in results.states])

        # Map phases to numeric values and colors
        # ── Phase → integer index mapping ─────────────────────────────────────
        # Transverse/Junker model (Jiang 5-stage): indices 0–4
        # Axial 3-stage model: indices 5–7
        # References: LOOSENING_STAGE_DEFINITIONS.md §3
        phase_map = {
            # Transverse / Junker — Jiang 5-stage
            'stable':          0,
            'non_rotational':  1,
            'transition':      2,
            'rotational':      3,
            'runaway':         4,
            # Axial — 3-stage axial model
            'axial_stage_i':   5,
            'axial_stage_ii':  6,
            'axial_stage_iii': 7,
        }
        phase_colors = {
            # Transverse / Junker
            0: COLORS['green'],
            1: COLORS['blue'],
            2: COLORS['yellow'],
            3: COLORS['peach'],
            4: COLORS['red'],
            # Axial 3-stage
            5: COLORS.get('teal',  COLORS['green']),
            6: COLORS.get('mauve', COLORS['blue']),
            7: COLORS['red'],   # same as RUNAWAY — catastrophic
        }
        phase_labels = {
            # Transverse / Junker
            0: 'STABLE',
            1: 'STAGE I\n(Non-rot)',
            2: 'TRANSITION',
            3: 'STAGE II\n(Rotational)',
            4: 'RUNAWAY',
            # Axial 3-stage
            5: 'AXIAL I\n(Rapid Drop)',
            6: 'AXIAL II\n(Slow Decay)',
            7: 'AXIAL III\n(Failure)',
        }
        phase_descriptions = {
            # Transverse / Junker
            0: 'No loosening',
            1: 'Plastic deformation',
            2: 'Intermittent slip',
            3: 'Junker mechanism',
            4: 'Critical',
            # Axial 3-stage
            5: 'Asperity crushing',
            6: 'Fretting / creep',
            7: 'Fatigue / runaway',
        }

        phases = np.array([
            phase_map.get(s.phase.value, 4)  # default → RUNAWAY if unknown value
            for s in results.states
        ])

        # =================================================================
        # TOP PANEL: Preload with S-curve fit and phase backgrounds
        # =================================================================
        # Plot colored phase regions as background
        prev_phase = phases[0]
        region_start = cycles[0]

        for i in range(1, len(cycles)):
            if phases[i] != prev_phase or i == len(cycles) - 1:
                region_end = cycles[i] if i < len(cycles) - 1 else cycles[-1]
                ax1.axvspan(region_start, region_end,
                           color=phase_colors[prev_phase], alpha=0.2,
                           zorder=0)
                region_start = cycles[i]
                prev_phase = phases[i]

        if region_start < cycles[-1]:
            ax1.axvspan(region_start, cycles[-1],
                       color=phase_colors[phases[-1]], alpha=0.2,
                       zorder=0)

        # Plot experimental preload curve (thick line)
        ax1.plot(results.cycles, results.preload_ratio * 100,
                color=COLORS['text'], linewidth=3, label='Preload Retention',
                zorder=3)

        # Add S-curve fit overlay (dashed)
        # Fit a two-stage model to the data
        try:
            from scipy.optimize import curve_fit

            def two_stage_model(N, a1, N1, a2, N2):
                """Two-stage S-curve: rapid initial + slower continued"""
                stage1 = a1 * (1 - np.exp(-N / N1))
                stage2 = a2 * (1 - np.exp(-N / N2))
                return 100 * (1 - stage1 - stage2)

            # Fit to data
            popt, _ = curve_fit(
                two_stage_model,
                results.cycles,
                results.preload_ratio * 100,
                p0=[0.15, 200, 0.3, 2000],
                bounds=([0, 1, 0, 10], [0.5, 5000, 0.8, 50000]),
                maxfev=5000
            )
            fitted_curve = two_stage_model(results.cycles, *popt)
            ax1.plot(results.cycles, fitted_curve,
                    color=COLORS['mauve'], linewidth=2, linestyle='--',
                    label=f'S-curve fit (N₁={popt[1]:.0f}, N₂={popt[3]:.0f})',
                    zorder=2, alpha=0.8)
        except:
            pass  # Skip fit if it fails

        # Threshold lines with annotations
        ax1.axhline(y=90, color=COLORS['yellow'], linestyle='--',
                   linewidth=1.5, alpha=0.8)
        ax1.annotate('10% loss', xy=(results.cycles[-1] * 0.02, 91),
                    fontsize=9, color=COLORS['yellow'], va='bottom')

        ax1.axhline(y=50, color=COLORS['red'], linestyle='--',
                   linewidth=1.5, alpha=0.8)
        ax1.annotate('50% loss (critical)', xy=(results.cycles[-1] * 0.02, 51),
                    fontsize=9, color=COLORS['red'], va='bottom')

        # Find and mark key milestones
        preload_pct = results.preload_ratio * 100

        # Mark 90% retention point
        idx_90 = np.argmax(preload_pct < 90) if np.any(preload_pct < 90) else None
        if idx_90 and idx_90 > 0:
            ax1.axvline(x=results.cycles[idx_90], color=COLORS['yellow'],
                       linestyle=':', linewidth=1.5, alpha=0.7)
            ax1.scatter([results.cycles[idx_90]], [90], color=COLORS['yellow'],
                       s=100, zorder=4, marker='o', edgecolors='white', linewidths=2)
            ax1.annotate(f'N={results.cycles[idx_90]:.0f}',
                        xy=(results.cycles[idx_90], 85),
                        fontsize=8, color=COLORS['yellow'], ha='center')

        # Mark 50% retention point
        idx_50 = np.argmax(preload_pct < 50) if np.any(preload_pct < 50) else None
        if idx_50 and idx_50 > 0:
            ax1.axvline(x=results.cycles[idx_50], color=COLORS['red'],
                       linestyle=':', linewidth=1.5, alpha=0.7)
            ax1.scatter([results.cycles[idx_50]], [50], color=COLORS['red'],
                       s=100, zorder=4, marker='o', edgecolors='white', linewidths=2)
            ax1.annotate(f'N={results.cycles[idx_50]:.0f}',
                        xy=(results.cycles[idx_50], 45),
                        fontsize=8, color=COLORS['red'], ha='center')

        # Phase transition markers with labels
        phase_changes = np.where(np.diff(phases) != 0)[0] + 1
        for idx in phase_changes:
            if idx < len(cycles):
                ax1.axvline(x=cycles[idx], color=COLORS['overlay'],
                           linestyle='-', linewidth=2, alpha=0.6)
                preload_at_trans = np.interp(cycles[idx], results.cycles,
                                            results.preload_ratio * 100)
                # Add phase label box
                bbox = dict(boxstyle='round,pad=0.3', facecolor=phase_colors[phases[idx]],
                           alpha=0.7, edgecolor='none')
                ax1.annotate(phase_labels[phases[idx]],
                            xy=(cycles[idx], preload_at_trans),
                            xytext=(cycles[idx] + results.cycles[-1]*0.02, preload_at_trans + 8),
                            fontsize=8, color=COLORS['text'], fontweight='bold',
                            bbox=bbox, va='bottom', ha='left',
                            arrowprops=dict(arrowstyle='->', color=COLORS['overlay'], lw=1))

        ax1.set_ylabel('Preload Retention (%)', fontsize=11, color=COLORS['text'])
        ax1.set_ylim([0, 110])
        ax1.grid(True, alpha=0.3, zorder=0)

        # Legend
        from matplotlib.patches import Patch
        from matplotlib.lines import Line2D
        legend_elements = [
            Line2D([0], [0], color=COLORS['text'], linewidth=3, label='Measured'),
            Line2D([0], [0], color=COLORS['mauve'], linewidth=2, linestyle='--', label='S-curve fit'),
            Patch(facecolor=COLORS['green'], alpha=0.4, label='Stable'),
            Patch(facecolor=COLORS['blue'], alpha=0.4, label='Stage I'),
            Patch(facecolor=COLORS['peach'], alpha=0.4, label='Stage II'),
            Patch(facecolor=COLORS['red'], alpha=0.4, label='Runaway'),
        ]
        ax1.legend(handles=legend_elements, loc='lower left', fontsize=9, ncol=2,
                  framealpha=0.9, facecolor=COLORS['surface'])

        ax1.set_title('Loosening Phase Diagram (Jiang Two-Stage Model)',
                     fontsize=13, color=COLORS['text'], fontweight='bold')

        # =================================================================
        # MIDDLE PANEL: Torque & Friction Margins
        # =================================================================
        if ax2 is not None:
            # Plot torque margin
            ax2.plot(results.cycles, results.torque_margin,
                    color=COLORS['blue'], linewidth=2.5, label='Torque Margin (T_res/T_pitch)')

            # Plot friction margin if available
            if hasattr(results, 'friction_margin') and results.friction_margin is not None:
                ax2.plot(results.cycles, results.friction_margin,
                        color=COLORS['mauve'], linewidth=2, linestyle='--',
                        label='Friction Margin (μ/μ_crit)')

            # Critical thresholds
            ax2.axhline(y=1.0, color=COLORS['red'], linestyle='-',
                       linewidth=2.5, label='Loosening threshold', alpha=0.8)
            ax2.axhline(y=1.5, color=COLORS['yellow'], linestyle='--',
                       linewidth=1.5, alpha=0.7, label='Safety margin (1.5)')

            # Colored fill for margin zones
            ax2.fill_between(results.cycles, 1.5, results.torque_margin,
                            where=results.torque_margin >= 1.5,
                            alpha=0.15, color=COLORS['green'], label='Safe zone')
            ax2.fill_between(results.cycles, 1.0, results.torque_margin,
                            where=(results.torque_margin >= 1.0) & (results.torque_margin < 1.5),
                            alpha=0.15, color=COLORS['yellow'])
            ax2.fill_between(results.cycles, 0, results.torque_margin,
                            where=results.torque_margin < 1.0,
                            alpha=0.2, color=COLORS['red'], label='Loosening zone')

            ax2.set_ylabel('Margin', fontsize=11, color=COLORS['text'])
            ax2.legend(loc='upper right', fontsize=8, ncol=2)
            ax2.grid(True, alpha=0.3)
            ax2.set_ylim([0, max(3.0, np.max(results.torque_margin) * 1.1)])

        # =================================================================
        # BOTTOM PANEL: Nut Rotation Angle
        # =================================================================
        if ax3 is not None and hasattr(results, 'loosening_angle_deg'):
            # Plot accumulated rotation
            ax3.plot(results.cycles, results.loosening_angle_deg,
                    color=COLORS['peach'], linewidth=2.5, label='Nut Rotation')

            # Add rate on secondary axis
            ax3_twin = ax3.twinx()

            # Compute rate (smoothed)
            if len(results.loosening_angle_deg) > 10:
                window = min(50, len(results.loosening_angle_deg) // 10)
                rate = np.gradient(results.loosening_angle_deg, results.cycles)
                # Smooth the rate
                rate_smooth = np.convolve(rate, np.ones(window)/window, mode='same')
                ax3_twin.plot(results.cycles, rate_smooth * 1000,  # Convert to mdeg/cycle
                             color=COLORS['teal'], linewidth=1.5, linestyle='--',
                             label='Rate', alpha=0.7)
                ax3_twin.set_ylabel('Rate (mdeg/cycle)', fontsize=10, color=COLORS['teal'])
                ax3_twin.tick_params(axis='y', colors=COLORS['teal'])

            # Threshold for significant loosening (0.5 deg based on Jiang)
            ax3.axhline(y=0.5, color=COLORS['yellow'], linestyle='--',
                       linewidth=1.5, alpha=0.7)
            ax3.annotate('0.5° threshold', xy=(results.cycles[-1] * 0.7, 0.55),
                        fontsize=8, color=COLORS['yellow'])

            ax3.set_xlabel('Number of Cycles (N)', fontsize=11, color=COLORS['text'])
            ax3.set_ylabel('Rotation (deg)', fontsize=11, color=COLORS['peach'])
            ax3.tick_params(axis='y', colors=COLORS['peach'])
            ax3.grid(True, alpha=0.3)
            ax3.legend(loc='upper left', fontsize=9)

            # Set y-limit based on data
            max_angle = np.max(results.loosening_angle_deg) if len(results.loosening_angle_deg) > 0 else 1
            ax3.set_ylim([0, max(1.0, max_angle * 1.2)])

        plt.tight_layout()
        return fig

    def plot_comprehensive_dashboard(self,
                                     results: 'LooseningResults',
                                     analyzer: 'CoupledLooseningAnalyzer' = None,
                                     save_path: Optional[str] = None) -> Figure:
        """
        Create comprehensive 6-panel dashboard.

        Layout:
        ┌────────────┬────────────┬────────────┐
        │  Preload & │  Loosening │   Torque   │
        │  Friction  │    Rate    │  Balance   │
        ├────────────┼────────────┼────────────┤
        │   Wear     │   Torque   │   Phase    │
        │  Accum.    │   Margin   │  Diagram   │
        └────────────┴────────────┴────────────┘
        """
        fig = plt.figure(figsize=(18, 12))
        gs = GridSpec(2, 3, figure=fig, hspace=0.3, wspace=0.25)

        # Row 1
        ax1 = fig.add_subplot(gs[0, 0])
        ax1_twin = ax1.twinx()

        # Preload & Friction (simplified single panel)
        ax1.plot(results.cycles, results.preload_ratio * 100,
                color=COLORS['blue'], linewidth=2, label='Preload %')
        ax1_twin.plot(results.cycles, results.mu_thread,
                     color=COLORS['mauve'], linewidth=2, linestyle='--', label='μ')
        ax1.set_xlabel('Cycles')
        ax1.set_ylabel('Preload (%)', color=COLORS['blue'])
        ax1_twin.set_ylabel('Friction μ', color=COLORS['mauve'])
        ax1.set_title('Preload & Friction')
        ax1.grid(True, alpha=0.3)

        ax2 = fig.add_subplot(gs[0, 1])
        self.plot_loosening_rate_evolution(results, ax=ax2)

        ax3 = fig.add_subplot(gs[0, 2])
        self.plot_torque_balance(results, ax=ax3)

        # Row 2
        ax4 = fig.add_subplot(gs[1, 0])
        self.plot_wear_accumulation(results, ax=ax4)

        ax5 = fig.add_subplot(gs[1, 1])
        self.plot_torque_margin_evolution(results, analyzer, ax=ax5)

        ax6 = fig.add_subplot(gs[1, 2])
        self.plot_phase_diagram(results, ax=ax6)

        # Title
        final_preload = results.final_preload_ratio * 100
        total_loosening = results.total_loosening_deg
        fig.suptitle(
            f'Coupled Friction-Wear-Loosening Analysis Dashboard\n'
            f'Final Preload: {final_preload:.1f}% | '
            f'Total Loosening: {total_loosening:.2f}° | '
            f'Max Rate: {results.max_loosening_rate:.4f}°/cycle',
            fontsize=14, color=COLORS['text']
        )

        if save_path:
            fig.savefig(save_path, dpi=300, facecolor=fig.get_facecolor())

        return fig

    def plot_friction_vs_loosening_rate(self,
                                        results: 'LooseningResults',
                                        analyzer: 'CoupledLooseningAnalyzer' = None,
                                        ax: Optional[Axes] = None) -> Figure:
        """
        Plot friction coefficient vs loosening rate correlation.

        Shows the direct relationship: lower friction → higher loosening rate.
        """
        if ax is None:
            fig, ax = plt.subplots(figsize=(10, 8))
        else:
            fig = ax.figure

        mu = results.mu_thread
        rate = results.loosening_rate
        cycles = results.cycles

        # Scatter with color by cycle count
        scatter = ax.scatter(mu, rate, c=cycles, cmap='viridis',
                            s=30, alpha=0.7)
        plt.colorbar(scatter, ax=ax, label='Cycle Count')

        # Critical friction line
        if analyzer:
            mu_crit = analyzer.compute_critical_friction()
            ax.axvline(x=mu_crit, color=COLORS['red'], linestyle='--',
                      linewidth=2, label=f'μ_crit = {mu_crit:.4f}')

        ax.set_xlabel('Friction Coefficient (μ)')
        ax.set_ylabel('Loosening Rate (°/cycle)')
        ax.set_title('Friction vs. Loosening Rate Correlation\n'
                    '(Lower μ → Higher loosening rate)')
        ax.legend()
        ax.grid(True, alpha=0.3)

        return fig


def quick_coupled_loosening_plot(preload_initial: float = 50000,
                                 F_transverse: float = 8000,
                                 n_cycles: int = 2000,
                                 mu_initial: float = 0.12,
                                 save_path: Optional[str] = None) -> Figure:
    """
    Quick function to generate coupled loosening analysis dashboard.

    Args:
        preload_initial: Initial preload force [N]
        F_transverse: Transverse force amplitude [N]
        n_cycles: Number of cycles
        mu_initial: Initial friction coefficient
        save_path: Optional path to save figure

    Returns:
        Matplotlib Figure
    """
    # Import here to avoid circular imports
    try:
        from ..numerical.coupled_loosening_analyzer import create_m16_analyzer
    except ImportError:
        # For standalone testing
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).parent.parent))
        from numerical.coupled_loosening_analyzer import create_m16_analyzer

    # Create analyzer and run
    analyzer = create_m16_analyzer(mu_initial=mu_initial, lubricated=True)
    results = analyzer.run_analysis(
        preload_initial=preload_initial,
        F_transverse=F_transverse,
        n_cycles=n_cycles
    )

    # Plot
    plotter = CoupledLooseningResultsPlotter()
    fig = plotter.plot_comprehensive_dashboard(results, analyzer, save_path)

    return fig


# =============================================================================
# ADDITIONAL PLOTTERS — §2.4, §4.6, §6.7 from FUTURE_IMPROVEMENTS.md
# =============================================================================

def plot_fretting_regime_map(results: 'LooseningResults',
                             analyzer: 'CoupledLooseningAnalyzer' = None,
                             ax: Optional[Axes] = None) -> Figure:
    """Vingsbo-Söderberg fretting regime map (§4.6).

    Axes: slip amplitude [µm] (log) vs. normal force [N] (log).
    Regions: STICK / PARTIAL SLIP / GROSS SLIP.
    Overlays the joint's operating-point trajectory (one point per stored cycle).
    """
    if ax is None:
        fig, ax = plt.subplots(figsize=(10, 7))
    else:
        fig = ax.figure

    # Derive slip amplitude history. Prefer analyzer's per-cycle value; fall
    # back to a constant from analyzer.transverse_displacement_mm.
    delta_um = None
    if analyzer is not None and results.states:
        # Use transverse_displacement_mm scaled by preload-ratio dependent
        # slip fraction (the Junker mechanism causes plate-amplitude slip).
        base = float(getattr(analyzer, 'transverse_displacement_mm', 0.0)) * 1e3  # mm→µm
        delta_um = np.full_like(results.preload, base)

    F_n = results.preload

    # Regime boundaries (Vingsbo & Söderberg 1988, Fouvry 1996):
    #   δ < ~5 µm                → STICK
    #   5 µm < δ < ~50 µm        → PARTIAL SLIP (where fretting wear peaks)
    #   δ > ~50 µm               → GROSS SLIP (Archard dominates)
    ax.axvspan(0.1, 5,    color=COLORS['green'],  alpha=0.12, label='Stick')
    ax.axvspan(5,   50,   color=COLORS['yellow'], alpha=0.15, label='Partial slip (fretting)')
    ax.axvspan(50,  5000, color=COLORS['red'],    alpha=0.10, label='Gross slip (wear)')
    ax.axvline(5,  color=COLORS['text'], ls='--', lw=0.8, alpha=0.5)
    ax.axvline(50, color=COLORS['text'], ls='--', lw=0.8, alpha=0.5)

    if delta_um is not None and len(delta_um) > 0 and F_n.size > 0:
        ax.plot(delta_um, F_n, color=COLORS['blue'], lw=1.2, alpha=0.6, label='Trajectory')
        ax.scatter(delta_um[:1],  F_n[:1],  color=COLORS['green'], s=60, zorder=5, label='Start')
        ax.scatter(delta_um[-1:], F_n[-1:], color=COLORS['red'],   s=60, zorder=5, label='End')

    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set_xlim(0.5, 2000)
    ax.set_xlabel('Slip amplitude δ [µm]')
    ax.set_ylabel('Normal force F_n [N]')
    ax.set_title('Vingsbo–Söderberg fretting regime map')
    ax.grid(True, alpha=0.3, which='both')
    ax.legend(loc='upper right', fontsize=9)
    plt.tight_layout()
    return fig


def plot_self_locking_margin(results: 'LooseningResults',
                             analyzer: 'CoupledLooseningAnalyzer' = None,
                             ax: Optional[Axes] = None) -> Figure:
    """Self-locking margin gauge (§6.7).

    SL_margin(N) = (µ(N) · cos α − tan λ) / tan λ
    - > 1.0: strongly self-locking (green)
    - 0.1–1.0: caution (yellow)
    - < 0.1: boundary / lost (red)
    """
    if ax is None:
        fig, ax = plt.subplots(figsize=(10, 5))
    else:
        fig = ax.figure

    # Thread geometry
    if analyzer is not None and hasattr(analyzer, 'thread'):
        lam = float(getattr(analyzer.thread, 'helix_angle', 0.05))
        alpha = float(getattr(analyzer.thread, 'flank_angle', np.radians(30.0)))
    else:
        lam = 0.05
        alpha = np.radians(30.0)

    cycles = results.cycles
    # Use thread µ (the dominant term in self-locking criterion)
    mu = results.mu_thread if getattr(results, 'mu_thread', None) is not None else None
    if mu is None or len(mu) == 0:
        ax.text(0.5, 0.5, 'No friction history', ha='center', va='center',
                transform=ax.transAxes)
        return fig

    tan_lam = np.tan(lam)
    if tan_lam <= 0:
        tan_lam = 1e-6
    sl_margin = (mu * np.cos(alpha) - tan_lam) / tan_lam

    # Zone bands
    ax.axhspan(1.0, max(1.5, float(np.nanmax(sl_margin)) + 0.2), color=COLORS['green'],  alpha=0.10)
    ax.axhspan(0.1, 1.0, color=COLORS['yellow'], alpha=0.12)
    ax.axhspan(min(-0.5, float(np.nanmin(sl_margin)) - 0.1), 0.1,
               color=COLORS['red'], alpha=0.12)

    ax.plot(cycles, sl_margin, color=COLORS['blue'], lw=2, label='SL margin')
    ax.axhline(0.0, color=COLORS['text'], ls='--', lw=0.8, alpha=0.5)
    ax.axhline(1.0, color=COLORS['green'], ls=':', lw=1.0)

    # Flag first cycle at which SL_margin < 0 (irreversible)
    if np.any(sl_margin < 0):
        idx = int(np.argmax(sl_margin < 0))
        ax.axvline(cycles[idx], color=COLORS['red'], lw=1.0, ls='--', alpha=0.7)
        ax.annotate(f'Self-locking lost\ncycle {int(cycles[idx])}',
                    xy=(cycles[idx], 0.0),
                    xytext=(0.6, 0.6), textcoords='axes fraction',
                    color=COLORS['red'], fontsize=9,
                    arrowprops=dict(arrowstyle='->', color=COLORS['red']))

    ax.set_xlabel('Cycles')
    ax.set_ylabel('SL margin = (µ·cos α − tan λ) / tan λ')
    ax.set_title('Self-locking condition margin')
    ax.grid(True, alpha=0.3)
    ax.legend(loc='best', fontsize=9)
    plt.tight_layout()
    return fig


def plot_interaction_diagram(F_transverse: float,
                             F_preload: float,
                             mu: float,
                             F_axial_op: float = 0.0,
                             F_sep: float = None,
                             M_torsional: float = 0.0,
                             M_torsional_crit: float = None,
                             ax: Optional[Axes] = None) -> Figure:
    """Combined-loading interaction diagram (§2.4).

    Two modes (auto-selected):
    - If M_torsional_crit is given → transverse vs. torsional ellipse
      (F_T/F_Tc)² + (M_T/M_Tc)² ≤ 1 (LLC §5.2).
    - Otherwise → transverse vs. axial linear (LLC §5.1)
      F_T/(µ·F₀) + F_A/F_sep ≤ 1.
    """
    if ax is None:
        fig, ax = plt.subplots(figsize=(8, 7))
    else:
        fig = ax.figure

    if M_torsional_crit is not None and M_torsional_crit > 0:
        F_Tc = max(mu * F_preload, 1e-6)
        theta = np.linspace(0, np.pi / 2, 180)
        ax.plot(np.cos(theta), np.sin(theta), color=COLORS['red'], lw=2, label='Boundary')
        op_x = F_transverse / F_Tc
        op_y = M_torsional / M_torsional_crit
        ax.scatter([op_x], [op_y], s=120, color=COLORS['blue'], zorder=5,
                   label=f'Operating point')
        margin = 1.0 - np.hypot(op_x, op_y)
        ax.set_xlabel('F_T / (µ·F₀)')
        ax.set_ylabel('M_T / M_T_crit')
        ax.set_title(f'Transverse–Torsional interaction (margin = {margin:+.2f})')
    else:
        F_Tc = max(mu * F_preload, 1e-6)
        F_Ac = F_sep if (F_sep is not None and F_sep > 0) else max(F_preload, 1.0)
        ax.plot([0, 1], [1, 0], color=COLORS['red'], lw=2, label='Boundary')
        op_x = F_transverse / F_Tc
        op_y = F_axial_op / F_Ac
        ax.scatter([op_x], [op_y], s=120, color=COLORS['blue'], zorder=5,
                   label='Operating point')
        margin = 1.0 - (op_x + op_y)
        ax.set_xlabel('F_T / (µ·F₀)')
        ax.set_ylabel('F_A / F_sep')
        ax.set_title(f'Transverse–Axial interaction (margin = {margin:+.2f})')

    ax.fill_between([0, 1.2], 0, 1.2, color=COLORS['red'],   alpha=0.05)
    ax.set_xlim(0, max(1.2, op_x * 1.1 if op_x < 1.5 else op_x + 0.2))
    ax.set_ylim(0, max(1.2, op_y * 1.1 if op_y < 1.5 else op_y + 0.2))
    ax.grid(True, alpha=0.3)
    ax.legend(loc='upper right', fontsize=9)
    plt.tight_layout()
    return fig


# =============================================================================
# TEST/DEMO FUNCTION
# =============================================================================

if __name__ == "__main__":
    # Generate all plots for testing
    print("Generating comprehensive loosening analysis plots...")
    
    # Create standard test data
    data = generate_standard_test_data()
    
    # Generate dashboard
    fig = create_comprehensive_dashboard(
        data['bolt'], data['joint'], data['conditions'],
        N_max=50000,
        save_path='loosening_dashboard.png'
    )
    
    plt.show()
    print("Done!")
