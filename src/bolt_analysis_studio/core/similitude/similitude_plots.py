#!/usr/bin/env python3
"""
Similitude Visualization Module
Bolt Analysis Studio v4.0

Generates comprehensive plots for similitude analysis including:
- Scaling relationship curves (F vs λ, f vs λ, etc.)
- Π-group comparison charts
- Scale effect severity visualization
- Prototype vs model comparison dashboards

Prof. Leonardo Rosa Ribeiro da Silva, PhD
January 2026
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Circle, Wedge
from matplotlib.collections import PatchCollection
from matplotlib.gridspec import GridSpec
import matplotlib.colors as mcolors
from typing import List, Dict, Tuple, Optional, Any
from pathlib import Path

# Import from similitude module
try:
    from .similitude import (
        SimilitudeAnalysis, ScaleFactors, PrototypeData, PiGroup,
        ScaleEffect, ScaleEffectSeverity, MaterialSimilarity
    )
except ImportError:
    from similitude import (
        SimilitudeAnalysis, ScaleFactors, PrototypeData, PiGroup,
        ScaleEffect, ScaleEffectSeverity, MaterialSimilarity
    )

# Import Theme for dynamic color lookup
try:
    from bolt_analysis_studio.gui.theme import Theme
    _HAS_THEME = True
except ImportError:
    _HAS_THEME = False


# =============================================================================
# Color Schemes (Theme-aware)
# =============================================================================

def _get_colors():
    """Get color dict from Theme (dynamic on each call)."""
    if _HAS_THEME:
        return {
            'primary': Theme.BLUE,
            'secondary': Theme.SKY,
            'accent': Theme.PEACH,
            'success': Theme.GREEN,
            'warning': Theme.YELLOW,
            'error': Theme.RED,
            'neutral': Theme.OVERLAY,
            'background': Theme.BASE,
            'prototype': Theme.BLUE,
            'model': Theme.PEACH,
            'matched': Theme.GREEN,
            'unmatched': Theme.RED,
        }
    return {
        'primary': '#1E3A5F', 'secondary': '#2E86AB', 'accent': '#F18F01',
        'success': '#2E7D32', 'warning': '#F57C00', 'error': '#C62828',
        'neutral': '#455A64', 'background': '#FAFAFA', 'prototype': '#1565C0',
        'model': '#E65100', 'matched': '#4CAF50', 'unmatched': '#FF5722',
    }


def _get_severity_colors():
    """Get severity color dict from Theme (dynamic on each call)."""
    if _HAS_THEME:
        return {
            ScaleEffectSeverity.NEGLIGIBLE: Theme.GREEN,
            ScaleEffectSeverity.LOW: Theme.TEAL,
            ScaleEffectSeverity.MEDIUM: Theme.YELLOW,
            ScaleEffectSeverity.HIGH: Theme.PEACH,
            ScaleEffectSeverity.CRITICAL: Theme.RED,
        }
    return {
        ScaleEffectSeverity.NEGLIGIBLE: '#4CAF50',
        ScaleEffectSeverity.LOW: '#8BC34A',
        ScaleEffectSeverity.MEDIUM: '#FFC107',
        ScaleEffectSeverity.HIGH: '#FF9800',
        ScaleEffectSeverity.CRITICAL: '#F44336',
    }


def _apply_theme_to_axes(fig, ax):
    """Apply Theme facecolors and text colors to a figure/axes pair."""
    if not _HAS_THEME:
        return
    fig.set_facecolor(Theme.BASE)
    if hasattr(ax, '__iter__'):
        for a in np.ravel(ax):
            a.set_facecolor(Theme.SURFACE0)
            a.tick_params(colors=Theme.TEXT)
            a.xaxis.label.set_color(Theme.TEXT)
            a.yaxis.label.set_color(Theme.TEXT)
            a.title.set_color(Theme.TEXT)
            for spine in a.spines.values():
                spine.set_edgecolor(Theme.SURFACE2)
    else:
        ax.set_facecolor(Theme.SURFACE0)
        ax.tick_params(colors=Theme.TEXT)
        ax.xaxis.label.set_color(Theme.TEXT)
        ax.yaxis.label.set_color(Theme.TEXT)
        ax.title.set_color(Theme.TEXT)
        for spine in ax.spines.values():
            spine.set_edgecolor(Theme.SURFACE2)


# =============================================================================
# Individual Plot Functions
# =============================================================================

def plot_scaling_relationships(analysis: SimilitudeAnalysis,
                               ax: Optional[plt.Axes] = None,
                               figsize: Tuple[float, float] = (12, 5)) -> plt.Figure:
    """
    Plot scaling relationship curves showing how physical quantities
    scale with geometric scale factor λ.

    Creates dual plots:
    1. Frequency vs Scale (f_model = f_proto / λ)
    2. Force vs Scale (F_model = F_proto × λ²)
    """
    COLORS = _get_colors()

    if ax is None:
        fig, axes = plt.subplots(1, 2, figsize=figsize)
    else:
        fig = ax[0].figure
        axes = ax

    # Scale factor range
    lambdas = np.linspace(0.1, 1.0, 100)
    current_lambda = analysis.scale_factor

    # -------------------------------------------------------------------------
    # Plot 1: Frequency vs Scale
    # -------------------------------------------------------------------------
    ax1 = axes[0]

    # f/f₀ = 1/λ for same material
    freq_ratio = 1 / lambdas

    ax1.semilogy(lambdas, freq_ratio, color=COLORS['primary'], linewidth=2.5, label='f_model / f_proto = 1/λ')
    ax1.axhline(y=1, color=COLORS['neutral'], linestyle='--', alpha=0.5, label='Prototype (λ=1)')

    # Mark current scale
    current_freq = 1 / current_lambda
    ax1.plot(current_lambda, current_freq, 'o', color=COLORS['error'], markersize=12,
             label=f'Current: λ={current_lambda}, f/f₀={current_freq:.1f}')

    # Mark common scales
    for lam, label in [(0.5, '1:2'), (0.25, '1:4'), (0.125, '1:8')]:
        if lam != current_lambda:
            ax1.plot(lam, 1/lam, '^', color=COLORS['neutral'], markersize=8, alpha=0.6)
            ax1.annotate(label, (lam, 1/lam), textcoords='offset points',
                        xytext=(5, 5), fontsize=9)

    ax1.set_xlabel('Geometric Scale Factor λ', fontsize=12)
    ax1.set_ylabel('Frequency Ratio f_m / f_p', fontsize=12)
    ax1.set_title('Natural Frequency Scaling\n(Same Material Similitude)', fontsize=13)
    ax1.set_xlim(0, 1.1)
    ax1.set_ylim(0.8, 15)
    ax1.grid(True, alpha=0.3)
    ax1.legend(loc='upper right', fontsize=10)

    # Add formula annotation
    bbox_color = Theme.SURFACE1 if _HAS_THEME else 'wheat'
    ax1.text(0.65, 8, r'$f_{model} = \frac{f_{proto}}{\lambda}$',
             fontsize=14, bbox=dict(boxstyle='round', facecolor=bbox_color, alpha=0.8))

    # -------------------------------------------------------------------------
    # Plot 2: Force vs Scale
    # -------------------------------------------------------------------------
    ax2 = axes[1]

    # F/F₀ = λ² for stress similitude
    force_ratio = lambdas ** 2

    ax2.semilogy(lambdas, force_ratio, color=COLORS['primary'], linewidth=2.5, label='F_model / F_proto = λ²')
    ax2.axhline(y=1, color=COLORS['neutral'], linestyle='--', alpha=0.5, label='Prototype (λ=1)')

    # Mark current scale
    current_force = current_lambda ** 2
    ax2.plot(current_lambda, current_force, 'o', color=COLORS['error'], markersize=12,
             label=f'Current: λ={current_lambda}, F/F₀={current_force:.4f}')

    # Mark common scales
    for lam, label in [(0.5, '1:2'), (0.25, '1:4'), (0.125, '1:8')]:
        if lam != current_lambda:
            ax2.plot(lam, lam**2, '^', color=COLORS['neutral'], markersize=8, alpha=0.6)
            ax2.annotate(label, (lam, lam**2), textcoords='offset points',
                        xytext=(5, -12), fontsize=9)

    ax2.set_xlabel('Geometric Scale Factor λ', fontsize=12)
    ax2.set_ylabel('Force Ratio F_m / F_p', fontsize=12)
    ax2.set_title('Force Scaling for Stress Similitude\n(σ_model = σ_proto)', fontsize=13)
    ax2.set_xlim(0, 1.1)
    ax2.set_ylim(0.005, 2)
    ax2.grid(True, alpha=0.3)
    ax2.legend(loc='upper left', fontsize=10)

    # Add formula annotation
    ax2.text(0.55, 0.4, r'$F_{model} = F_{proto} \cdot \lambda^2$',
             fontsize=14, bbox=dict(boxstyle='round', facecolor=bbox_color, alpha=0.8))

    _apply_theme_to_axes(fig, axes)

    if ax is None:
        plt.tight_layout()

    return fig


def plot_pi_groups_comparison(analysis: SimilitudeAnalysis,
                              ax: Optional[plt.Axes] = None,
                              figsize: Tuple[float, float] = (12, 6)) -> plt.Figure:
    """
    Plot bar chart comparing Π-groups between prototype and model.
    
    Shows deviation percentages and match status for each dimensionless
    parameter group.
    """
    if ax is None:
        fig, ax = plt.subplots(figsize=figsize)
    else:
        fig = ax.figure
    
    # Get primary Π-groups
    pi_groups = [pi for pi in analysis.pi_groups if pi.category == 'primary']
    n_groups = len(pi_groups)
    
    # Prepare data
    names = [f"{pi.symbol}\n{pi.name}" for pi in pi_groups]
    proto_values = [pi.prototype_value for pi in pi_groups]
    model_values = [pi.model_value for pi in pi_groups]
    deviations = [pi.deviation_percent for pi in pi_groups]
    matched = [pi.is_matched for pi in pi_groups]
    
    # Bar positions
    x = np.arange(n_groups)
    width = 0.35
    
    COLORS = _get_colors()

    # Create bars
    bars_proto = ax.bar(x - width/2, proto_values, width, label='Prototype',
                        color=COLORS['prototype'], alpha=0.8)
    bars_model = ax.bar(x + width/2, model_values, width, label='Model',
                        color=COLORS['model'], alpha=0.8)

    # Add match status markers
    for i, (m, dev) in enumerate(zip(matched, deviations)):
        color = COLORS['matched'] if m else COLORS['unmatched']
        marker = '✓' if m else '✗'
        y_pos = max(proto_values[i], model_values[i]) * 1.1
        ax.annotate(f'{marker} {dev:.1f}%', (x[i], y_pos),
                   ha='center', va='bottom', fontsize=10,
                   color=color, fontweight='bold')

    ax.set_xlabel('Dimensionless Π-Groups', fontsize=12)
    ax.set_ylabel('Value', fontsize=12)
    ax.set_title(f'Π-Group Comparison: Prototype vs Model ({analysis.scale_ratio_string})',
                fontsize=14)
    ax.set_xticks(x)
    ax.set_xticklabels(names, fontsize=9)
    ax.legend(loc='upper right')
    ax.grid(True, axis='y', alpha=0.3)

    # Add scale info
    n_matched = sum(matched)
    box_color = COLORS['success'] if n_matched == n_groups else COLORS['warning']
    ax.text(0.02, 0.98, f'Matched: {n_matched}/{n_groups}',
            transform=ax.transAxes, fontsize=11,
            verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor=box_color, alpha=0.4))

    _apply_theme_to_axes(fig, ax)

    if ax is None:
        plt.tight_layout()

    return fig


def plot_scale_effects_radar(analysis: SimilitudeAnalysis,
                             ax: Optional[plt.Axes] = None,
                             figsize: Tuple[float, float] = (8, 8)) -> plt.Figure:
    """
    Create radar/spider chart showing scale effect magnitudes
    and their severity levels.
    """
    if ax is None:
        fig, ax = plt.subplots(figsize=figsize, subplot_kw=dict(polar=True))
    else:
        fig = ax.figure
    
    effects = analysis.scale_effects
    n_effects = len(effects)
    
    # Prepare data
    categories = [e.name for e in effects]
    corrections = [e.correction_factor for e in effects]
    severities = [e.severity for e in effects]
    
    # Calculate angles
    angles = np.linspace(0, 2 * np.pi, n_effects, endpoint=False).tolist()
    angles += angles[:1]  # Complete the circle
    
    corrections_closed = corrections + corrections[:1]
    
    COLORS = _get_colors()
    SEVERITY_COLORS = _get_severity_colors()

    # Plot
    ax.plot(angles, corrections_closed, 'o-', linewidth=2, color=COLORS['primary'])
    ax.fill(angles, corrections_closed, alpha=0.25, color=COLORS['primary'])

    # Add severity colors to markers
    for i, (angle, corr, sev) in enumerate(zip(angles[:-1], corrections, severities)):
        ax.scatter(angle, corr, s=150, c=SEVERITY_COLORS[sev],
                   edgecolors=COLORS['neutral'], linewidth=1, zorder=5)

    # Set labels
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories, fontsize=10)

    # Set radial limits (correction factors are typically 1.0 to 1.3)
    ax.set_ylim(0.9, max(corrections) * 1.2)

    ax.set_title(f'Scale Effects Magnitude\n(λ = {analysis.scale_factor})', fontsize=14, pad=20)

    # Add legend for severity colors
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor=SEVERITY_COLORS[ScaleEffectSeverity.NEGLIGIBLE], label='Negligible'),
        Patch(facecolor=SEVERITY_COLORS[ScaleEffectSeverity.LOW], label='Low'),
        Patch(facecolor=SEVERITY_COLORS[ScaleEffectSeverity.MEDIUM], label='Medium'),
        Patch(facecolor=SEVERITY_COLORS[ScaleEffectSeverity.HIGH], label='High'),
    ]
    ax.legend(handles=legend_elements, loc='upper right', bbox_to_anchor=(1.3, 1.0))

    if _HAS_THEME:
        fig.set_facecolor(Theme.BASE)

    return fig


def plot_correction_factor_breakdown(analysis: SimilitudeAnalysis,
                                     ax: Optional[plt.Axes] = None,
                                     figsize: Tuple[float, float] = (10, 6)) -> plt.Figure:
    """
    Create horizontal bar chart showing contribution of each scale
    effect to the combined correction factor.
    """
    if ax is None:
        fig, ax = plt.subplots(figsize=figsize)
    else:
        fig = ax.figure
    
    effects = analysis.scale_effects
    
    SEVERITY_COLORS = _get_severity_colors()
    COLORS = _get_colors()

    # Sort by correction factor magnitude
    effects_sorted = sorted(effects, key=lambda e: e.correction_factor, reverse=True)

    names = [e.name for e in effects_sorted]
    corrections = [e.correction_factor for e in effects_sorted]
    deviations = [e.deviation_percent for e in effects_sorted]
    severities = [e.severity for e in effects_sorted]
    colors = [SEVERITY_COLORS[s] for s in severities]
    
    y_pos = np.arange(len(names))
    
    # Create horizontal bars
    bars = ax.barh(y_pos, corrections, align='center', color=colors, alpha=0.8,
                   edgecolor=COLORS['neutral'], linewidth=1)

    # Add reference line at 1.0
    ax.axvline(x=1.0, color=COLORS['neutral'], linestyle='--', linewidth=1.5, label='Unity (no correction)')

    # Add value labels
    for i, (corr, dev) in enumerate(zip(corrections, deviations)):
        label = f'{corr:.3f} ({dev:+.1f}%)'
        ax.text(corr + 0.005, i, label, va='center', fontsize=10)

    ax.set_yticks(y_pos)
    ax.set_yticklabels(names)
    ax.set_xlabel('Correction Factor', fontsize=12)
    ax.set_title(f'Scale Effect Corrections (λ = {analysis.scale_factor})\n'
                f'Combined: {analysis.combined_correction:.3f}', fontsize=14)
    ax.set_xlim(0.95, max(corrections) * 1.15)
    ax.grid(True, axis='x', alpha=0.3)
    ax.legend(loc='lower right')

    _apply_theme_to_axes(fig, ax)

    if ax is None:
        plt.tight_layout()

    return fig


def plot_prototype_model_schematic(analysis: SimilitudeAnalysis,
                                   ax: Optional[plt.Axes] = None,
                                   figsize: Tuple[float, float] = (12, 6)) -> plt.Figure:
    """
    Create side-by-side schematic comparing prototype and model
    joint dimensions visually.
    """
    if ax is None:
        fig, axes = plt.subplots(1, 2, figsize=figsize)
    else:
        fig = ax[0].figure
        axes = ax
    
    proto = analysis.prototype
    lam = analysis.scale_factor
    
    COLORS = _get_colors()

    def draw_bolt_joint(ax, d, L, t, is_prototype=True):
        """Draw simplified bolt joint schematic."""
        ax.set_xlim(-L*0.8, L*0.8)
        ax.set_ylim(-L*0.7, L*0.7)
        ax.set_aspect('equal')
        ax.axis('off')

        # Colors
        bolt_color = COLORS['prototype'] if is_prototype else COLORS['model']
        flange_color = Theme.OVERLAY if _HAS_THEME else '#90A4AE'
        
        # Scale factor for drawing
        scale = L / 100  # Normalize to L=100
        
        # Draw flanges (top and bottom)
        flange_width = d * 3
        for y_offset in [-t/2 - t, t/2]:
            rect = plt.Rectangle((-flange_width/2, y_offset), flange_width, t,
                                  facecolor=flange_color, edgecolor='black',
                                  linewidth=1.5)
            ax.add_patch(rect)
        
        # Draw bolt head
        head_width = d * 1.5
        head_height = d * 0.7
        head = plt.Rectangle((-head_width/2, t/2 + t), head_width, head_height,
                              facecolor=bolt_color, edgecolor='black', linewidth=2)
        ax.add_patch(head)
        
        # Draw bolt shank
        shank = plt.Rectangle((-d/2, -t/2 - t), d, L,
                               facecolor=bolt_color, edgecolor='black',
                               linewidth=1.5, alpha=0.8)
        ax.add_patch(shank)
        
        # Draw nut
        nut_height = d * 0.8
        nut = plt.Rectangle((-head_width/2, -t/2 - t - nut_height),
                             head_width, nut_height,
                             facecolor=bolt_color, edgecolor='black', linewidth=2)
        ax.add_patch(nut)
        
        # Thread lines
        thread_start = -t/2 - t
        thread_end = -t/2
        n_threads = int(t / (d * 0.1))
        for i in range(n_threads):
            y = thread_start + i * t / n_threads
            ax.plot([-d/2, -d/3], [y, y + t/(n_threads*2)], 'k-', linewidth=0.5, alpha=0.5)
            ax.plot([d/3, d/2], [y, y + t/(n_threads*2)], 'k-', linewidth=0.5, alpha=0.5)
        
        # Dimension annotations
        # Diameter
        ax.annotate('', xy=(-d/2, -L*0.5), xytext=(d/2, -L*0.5),
                    arrowprops=dict(arrowstyle='<->', color=COLORS['error'], lw=1.5))
        ax.text(0, -L*0.55, f'd = {d:.1f} mm', ha='center', va='top',
                fontsize=11, color=COLORS['error'])

        # Grip length
        ax.annotate('', xy=(d*2, t/2 + t), xytext=(d*2, -t/2 - t),
                    arrowprops=dict(arrowstyle='<->', color=COLORS['primary'], lw=1.5))
        ax.text(d*2.5, 0, f'L = {L:.1f} mm', ha='left', va='center',
                fontsize=11, color=COLORS['primary'], rotation=90)
        
        # Title
        title = 'PROTOTYPE' if is_prototype else f'MODEL ({analysis.scale_ratio_string})'
        ax.set_title(title, fontsize=14, fontweight='bold', color=bolt_color)
    
    # Draw prototype
    draw_bolt_joint(axes[0], proto.bolt_diameter, proto.grip_length,
                    proto.flange_thickness, is_prototype=True)
    
    # Draw model (scaled)
    draw_bolt_joint(axes[1], proto.bolt_diameter * lam, proto.grip_length * lam,
                    proto.flange_thickness * lam, is_prototype=False)
    
    # Add comparison info between plots
    bbox_color = Theme.SURFACE1 if _HAS_THEME else 'lightyellow'
    text_color = Theme.TEXT if _HAS_THEME else 'black'
    fig.text(0.5, 0.02, f'Scale Factor λ = {lam} ({analysis.scale_ratio_string})\n'
             f'Force Scale = λ² = {lam**2:.4f}  |  Frequency Scale = 1/λ = {1/lam:.1f}',
             ha='center', fontsize=11, color=text_color,
             bbox=dict(boxstyle='round', facecolor=bbox_color, alpha=0.8))

    if _HAS_THEME:
        fig.set_facecolor(Theme.BASE)

    if ax is None:
        plt.tight_layout()
        plt.subplots_adjust(bottom=0.15)

    return fig


def plot_multi_scale_comparison(prototype: PrototypeData,
                                scale_factors: List[float] = None,
                                ax: Optional[plt.Axes] = None,
                                figsize: Tuple[float, float] = (14, 6)) -> plt.Figure:
    """
    Compare multiple scale factors showing how key parameters
    change across different model sizes.
    """
    if scale_factors is None:
        scale_factors = [0.5, 0.25, 0.125]
    
    if ax is None:
        fig, axes = plt.subplots(1, 3, figsize=figsize)
    else:
        fig = ax[0].figure
        axes = ax
    
    COLORS = _get_colors()
    SEVERITY_COLORS = _get_severity_colors()

    # Analyze each scale
    analyses = [SimilitudeAnalysis(prototype=prototype, scale_factor=lam)
                for lam in scale_factors]

    # Data for plotting
    labels = [f"1:{int(1/lam)}" for lam in scale_factors]
    diameters = [a.model_diameter for a in analyses]
    preloads = [a.model_preload / 1000 for a in analyses]  # kN
    corrections = [a.combined_correction for a in analyses]

    colors = plt.cm.Blues(np.linspace(0.3, 0.8, len(scale_factors)))

    # Plot 1: Model diameters
    axes[0].bar(labels, diameters, color=colors)
    axes[0].axhline(prototype.bolt_diameter, color=COLORS['error'], linestyle='--',
                   label=f'Prototype: {prototype.bolt_diameter} mm')
    axes[0].set_ylabel('Bolt Diameter [mm]')
    axes[0].set_title('Model Bolt Diameter')
    axes[0].legend()
    for i, d in enumerate(diameters):
        axes[0].text(i, d + 0.5, f'{d:.1f}', ha='center', fontsize=10)

    # Plot 2: Model preloads
    axes[1].bar(labels, preloads, color=colors)
    axes[1].axhline(prototype.preload_force/1000, color=COLORS['error'], linestyle='--',
                   label=f'Prototype: {prototype.preload_force/1000:.0f} kN')
    axes[1].set_ylabel('Preload Force [kN]')
    axes[1].set_title('Model Preload (Stress Similitude)')
    axes[1].legend()
    axes[1].set_yscale('log')
    for i, p in enumerate(preloads):
        axes[1].text(i, p * 1.3, f'{p:.1f}', ha='center', fontsize=10)

    # Plot 3: Correction factors
    axes[2].bar(labels, corrections, color=[SEVERITY_COLORS[ScaleEffectSeverity.MEDIUM]
                                            if c > 1.15 else SEVERITY_COLORS[ScaleEffectSeverity.LOW]
                                            for c in corrections])
    axes[2].axhline(1.0, color=COLORS['success'], linestyle='--', label='Unity (no correction)')
    axes[2].set_ylabel('Combined Correction Factor')
    axes[2].set_title('Scale Effect Corrections')
    axes[2].legend()
    axes[2].set_ylim(0.95, max(corrections) * 1.1)
    for i, c in enumerate(corrections):
        axes[2].text(i, c + 0.02, f'{c:.3f}', ha='center', fontsize=10)

    for ax_i in axes:
        ax_i.set_xlabel('Scale Ratio')
        ax_i.grid(True, axis='y', alpha=0.3)
    
    suptitle_color = Theme.TEXT if _HAS_THEME else 'black'
    plt.suptitle(f'Multi-Scale Comparison\nPrototype: M{int(prototype.bolt_diameter)}, '
                 f'Fp = {prototype.preload_force/1000:.0f} kN', fontsize=14, color=suptitle_color)

    _apply_theme_to_axes(fig, axes)

    if ax is None:
        plt.tight_layout()

    return fig


# =============================================================================
# Comprehensive Dashboard
# =============================================================================

def create_similitude_dashboard(analysis: SimilitudeAnalysis,
                                figsize: Tuple[float, float] = (16, 12)) -> plt.Figure:
    """
    Create comprehensive dashboard with all similitude visualizations.
    
    Layout:
    - Top row: Scaling relationships (Freq vs λ, Force vs λ)
    - Middle row: Π-group comparison, Scale effects radar
    - Bottom row: Schematic comparison, Correction breakdown
    """
    COLORS = _get_colors()
    SEVERITY_COLORS = _get_severity_colors()

    fig = plt.figure(figsize=figsize)
    gs = GridSpec(3, 4, figure=fig, height_ratios=[1, 1.2, 1])

    suptitle_color = Theme.TEXT if _HAS_THEME else 'black'
    # Title
    fig.suptitle(f'Similitude Analysis Dashboard - Scale {analysis.scale_ratio_string}\n'
                 f'Prototype: M{int(analysis.prototype.bolt_diameter)} × {int(analysis.prototype.grip_length)} mm, '
                 f'Fp = {analysis.prototype.preload_force/1000:.0f} kN',
                 fontsize=16, fontweight='bold', y=0.98, color=suptitle_color)
    
    # -------------------------------------------------------------------------
    # Top Row: Scaling Relationships
    # -------------------------------------------------------------------------
    ax1 = fig.add_subplot(gs[0, :2])
    ax2 = fig.add_subplot(gs[0, 2:])
    
    # Frequency vs Scale
    lambdas = np.linspace(0.1, 1.0, 100)
    ax1.semilogy(lambdas, 1/lambdas, color=COLORS['primary'], linewidth=2, label='f/f₀ = 1/λ')
    ax1.plot(analysis.scale_factor, 1/analysis.scale_factor, 'o', color=COLORS['error'], markersize=12,
             label=f'Current: {analysis.scale_ratio_string}')
    ax1.axhline(1, color=COLORS['neutral'], linestyle='--', alpha=0.5)
    ax1.set_xlabel('Scale Factor λ')
    ax1.set_ylabel('Frequency Ratio')
    ax1.set_title('Frequency Scaling')
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    # Force vs Scale
    ax2.semilogy(lambdas, lambdas**2, color=COLORS['primary'], linewidth=2, label='F/F₀ = λ²')
    ax2.plot(analysis.scale_factor, analysis.scale_factor**2, 'o', color=COLORS['error'], markersize=12,
             label=f'Current: {analysis.scale_ratio_string}')
    ax2.axhline(1, color=COLORS['neutral'], linestyle='--', alpha=0.5)
    ax2.set_xlabel('Scale Factor λ')
    ax2.set_ylabel('Force Ratio')
    ax2.set_title('Force Scaling (Stress Similitude)')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # -------------------------------------------------------------------------
    # Middle Row: Π-Groups and Radar
    # -------------------------------------------------------------------------
    ax3 = fig.add_subplot(gs[1, :3])
    
    # Π-group comparison
    pi_groups = [pi for pi in analysis.pi_groups if pi.category == 'primary']
    n_groups = len(pi_groups)
    x = np.arange(n_groups)
    width = 0.35
    
    proto_vals = [pi.prototype_value for pi in pi_groups]
    model_vals = [pi.model_value for pi in pi_groups]
    
    ax3.bar(x - width/2, proto_vals, width, label='Prototype', color=COLORS['prototype'], alpha=0.8)
    ax3.bar(x + width/2, model_vals, width, label='Model', color=COLORS['model'], alpha=0.8)

    # Add match status
    for i, pi in enumerate(pi_groups):
        color = COLORS['matched'] if pi.is_matched else COLORS['unmatched']
        ax3.annotate(pi.status_icon, (x[i], max(proto_vals[i], model_vals[i]) * 1.05),
                    ha='center', fontsize=14, color=color)
    
    ax3.set_xticks(x)
    ax3.set_xticklabels([f"{pi.symbol}" for pi in pi_groups], fontsize=10)
    ax3.set_ylabel('Π-Group Value')
    ax3.set_title('Dimensionless Π-Groups Comparison')
    ax3.legend(loc='upper right')
    ax3.grid(True, axis='y', alpha=0.3)
    
    # Scale effects radar
    ax4 = fig.add_subplot(gs[1, 3], polar=True)
    effects = analysis.scale_effects
    n_effects = len(effects)
    angles = np.linspace(0, 2 * np.pi, n_effects, endpoint=False).tolist()
    angles += angles[:1]
    corrections = [e.correction_factor for e in effects] + [effects[0].correction_factor]
    
    ax4.plot(angles, corrections, 'o-', linewidth=2, color=COLORS['primary'])
    ax4.fill(angles, corrections, alpha=0.25, color=COLORS['primary'])
    ax4.set_xticks(angles[:-1])
    ax4.set_xticklabels([e.name[:10] for e in effects], fontsize=8)
    ax4.set_title('Scale Effects', fontsize=11, pad=10)
    
    # -------------------------------------------------------------------------
    # Bottom Row: Summary Tables
    # -------------------------------------------------------------------------
    ax5 = fig.add_subplot(gs[2, :2])
    ax5.axis('off')
    
    # Create comparison table
    comparison_data = [
        ['Parameter', 'Prototype', 'Model', 'Scale'],
        ['Bolt Ø (d)', f'{analysis.prototype.bolt_diameter:.1f} mm', 
         f'{analysis.model_diameter:.2f} mm', f'λ = {analysis.scale_factor:.3f}'],
        ['Grip (L)', f'{analysis.prototype.grip_length:.1f} mm',
         f'{analysis.model_grip_length:.2f} mm', f'λ = {analysis.scale_factor:.3f}'],
        ['Preload (Fp)', f'{analysis.prototype.preload_force/1000:.1f} kN',
         f'{analysis.model_preload/1000:.3f} kN', f'λ² = {analysis.scale_factor**2:.4f}'],
        ['Frequency', 'f₀', f'f₀ × {1/analysis.scale_factor:.1f}', f'1/λ = {1/analysis.scale_factor:.2f}'],
    ]
    
    table = ax5.table(cellText=comparison_data, loc='center', cellLoc='center',
                      colWidths=[0.25, 0.25, 0.25, 0.25])
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1.2, 1.5)
    
    # Header styling
    header_bg = Theme.SURFACE0 if _HAS_THEME else '#E3F2FD'
    cell_bg = Theme.SURFACE1 if _HAS_THEME else '#FAFAFA'
    cell_text = Theme.TEXT if _HAS_THEME else 'black'
    for (row, col), cell in table.get_celld().items():
        cell.set_text_props(color=cell_text)
        if row == 0:
            cell.set_text_props(fontweight='bold', color=cell_text)
            cell.set_facecolor(header_bg)
        else:
            cell.set_facecolor(cell_bg)

    ax5.set_title('Prototype vs Model Comparison', fontsize=12, pad=10)
    
    # Scale effects summary
    ax6 = fig.add_subplot(gs[2, 2:])
    ax6.axis('off')
    
    effects_data = [['Effect', 'Deviation', 'Correction', 'Severity']]
    for e in analysis.scale_effects:
        effects_data.append([
            e.name,
            f'{e.deviation_percent:+.1f}%',
            f'{e.correction_factor:.3f}',
            e.severity.value.upper()
        ])
    effects_data.append(['COMBINED', '', f'{analysis.combined_correction:.3f}', ''])
    
    table2 = ax6.table(cellText=effects_data, loc='center', cellLoc='center',
                       colWidths=[0.35, 0.2, 0.2, 0.25])
    table2.auto_set_font_size(False)
    table2.set_fontsize(9)
    table2.scale(1.2, 1.4)
    
    # Color by severity (Theme-aware)
    if _HAS_THEME:
        severity_cell_colors = {
            'NEGLIGIBLE': Theme.GREEN, 'LOW': Theme.TEAL,
            'MEDIUM': Theme.YELLOW, 'HIGH': Theme.PEACH, 'CRITICAL': Theme.RED,
        }
        header_bg2 = Theme.SURFACE0
        combined_bg = Theme.SURFACE1
    else:
        severity_cell_colors = {
            'NEGLIGIBLE': '#E8F5E9', 'LOW': '#C8E6C9',
            'MEDIUM': '#FFF9C4', 'HIGH': '#FFECB3', 'CRITICAL': '#FFCDD2',
        }
        header_bg2 = '#E3F2FD'
        combined_bg = '#BBDEFB'

    for (row, col), cell in table2.get_celld().items():
        cell.set_text_props(color=cell_text)
        if row == 0:
            cell.set_text_props(fontweight='bold', color=cell_text)
            cell.set_facecolor(header_bg2)
        elif row == len(effects_data) - 1:  # Combined row
            cell.set_text_props(fontweight='bold', color=cell_text)
            cell.set_facecolor(combined_bg)
        elif col == 3 and row > 0:  # Severity column
            sev = effects_data[row][3]
            if sev in severity_cell_colors:
                cell.set_facecolor(severity_cell_colors[sev] + '40' if _HAS_THEME else severity_cell_colors[sev])
        else:
            cell.set_facecolor(cell_bg)

    ax6.set_title('Scale Effects Summary', fontsize=12, pad=10)

    if _HAS_THEME:
        fig.set_facecolor(Theme.BASE)

    plt.tight_layout(rect=[0, 0, 1, 0.96])

    return fig


# =============================================================================
# Export Functions
# =============================================================================

def save_all_plots(analysis: SimilitudeAnalysis,
                   output_dir: str = "output_plots",
                   prefix: str = "similitude") -> List[str]:
    """
    Generate and save all similitude analysis plots.
    
    Args:
        analysis: SimilitudeAnalysis instance
        output_dir: Directory for output files
        prefix: Filename prefix
    
    Returns:
        List of saved file paths
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    saved_files = []
    
    # 1. Scaling relationships
    fig = plot_scaling_relationships(analysis)
    filepath = output_path / f"{prefix}_01_scaling_relationships.png"
    fig.savefig(filepath, dpi=150, bbox_inches='tight', facecolor=fig.get_facecolor())
    plt.close(fig)
    saved_files.append(str(filepath))
    
    # 2. Π-group comparison
    fig = plot_pi_groups_comparison(analysis)
    filepath = output_path / f"{prefix}_02_pi_groups.png"
    fig.savefig(filepath, dpi=150, bbox_inches='tight', facecolor=fig.get_facecolor())
    plt.close(fig)
    saved_files.append(str(filepath))
    
    # 3. Scale effects radar
    fig = plot_scale_effects_radar(analysis)
    filepath = output_path / f"{prefix}_03_scale_effects_radar.png"
    fig.savefig(filepath, dpi=150, bbox_inches='tight', facecolor=fig.get_facecolor())
    plt.close(fig)
    saved_files.append(str(filepath))
    
    # 4. Correction breakdown
    fig = plot_correction_factor_breakdown(analysis)
    filepath = output_path / f"{prefix}_04_corrections.png"
    fig.savefig(filepath, dpi=150, bbox_inches='tight', facecolor=fig.get_facecolor())
    plt.close(fig)
    saved_files.append(str(filepath))
    
    # 5. Schematic comparison
    fig = plot_prototype_model_schematic(analysis)
    filepath = output_path / f"{prefix}_05_schematic.png"
    fig.savefig(filepath, dpi=150, bbox_inches='tight', facecolor=fig.get_facecolor())
    plt.close(fig)
    saved_files.append(str(filepath))
    
    # 6. Multi-scale comparison
    fig = plot_multi_scale_comparison(analysis.prototype)
    filepath = output_path / f"{prefix}_06_multi_scale.png"
    fig.savefig(filepath, dpi=150, bbox_inches='tight', facecolor=fig.get_facecolor())
    plt.close(fig)
    saved_files.append(str(filepath))
    
    # 7. Complete dashboard
    fig = create_similitude_dashboard(analysis)
    filepath = output_path / f"{prefix}_07_dashboard.png"
    fig.savefig(filepath, dpi=150, bbox_inches='tight', facecolor=fig.get_facecolor())
    plt.close(fig)
    saved_files.append(str(filepath))
    
    return saved_files


# =============================================================================
# Test Suite
# =============================================================================

def run_visualization_tests():
    """Run visualization test suite and generate sample plots."""
    print("=" * 70)
    print("SIMILITUDE VISUALIZATION MODULE - TEST SUITE")
    print("Bolt Analysis Studio v4.0")
    print("=" * 70)
    
    # Create test prototype
    proto = PrototypeData(
        name="M24 Flanged Joint - Test",
        bolt_diameter=24.0,
        grip_length=100.0,
        flange_thickness=30.0,
        thread_pitch=3.0,
        preload_force=160000.0,
        external_axial_force=48000.0,
        bolt_yield_strength=724.0,
        surface_roughness_Rz=6.3,
    )
    
    # Create analysis (1:4 scale)
    analysis = SimilitudeAnalysis(prototype=proto, scale_factor=0.25)
    
    print(f"\nTest Analysis: {analysis.scale_ratio_string}")
    print(f"  Model diameter: {analysis.model_diameter:.1f} mm")
    print(f"  Model preload: {analysis.model_preload:.0f} N")
    
    # Generate and save all plots
    print("\nGenerating plots...")
    output_dir = "/home/claude/bolt_analysis_studio/output_plots"
    saved_files = save_all_plots(analysis, output_dir=output_dir)
    
    print(f"\nSaved {len(saved_files)} plots:")
    for filepath in saved_files:
        print(f"  ✓ {Path(filepath).name}")
    
    print("\n" + "=" * 70)
    print("VISUALIZATION TESTS COMPLETED ✓")
    print("=" * 70)
    
    return saved_files


if __name__ == "__main__":
    run_visualization_tests()
