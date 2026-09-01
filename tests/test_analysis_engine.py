#!/usr/bin/env python3
"""
Bolt Analysis Studio - Part 1: Analysis Engine Test Suite
=========================================================

This script generates all plots for loosening phenomena analysis:
1. Preload loss over cycles (multiple models)
2. Preload loss over time
3. Loosening rate (dF/dN) evolution
4. Friction coefficient evolution over cycles
5. Wear evolution over cycles
6. D-N curves (displacement-life)
7. Stage identification (Jiang model)
8. Model comparison dashboard
9. Coupled friction-preload evolution

Run: python test_analysis_engine.py

LTAD/UFU + Petrobras R&D
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.gridspec import GridSpec
import os
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum


# =============================================================================
# CATPPUCCIN MOCHA COLOR SCHEME
# =============================================================================

COLORS = {
    'background': '#1e1e2e',
    'surface': '#313244',
    'overlay': '#6c7086',
    'text': '#cdd6f4',
    'subtext': '#a6adc8',
    'red': '#f38ba8',
    'peach': '#fab387',
    'yellow': '#f9e2af',
    'green': '#a6e3a1',
    'teal': '#94e2d5',
    'blue': '#89b4fa',
    'mauve': '#cba6f7',
    'pink': '#f5c2e7',
    'lavender': '#b4befe',
    'sapphire': '#74c7ec',
}


def setup_plot_style():
    """Configure matplotlib for publication-quality dark theme plots"""
    plt.style.use('dark_background')
    plt.rcParams.update({
        'figure.facecolor': COLORS['background'],
        'axes.facecolor': COLORS['surface'],
        'axes.edgecolor': COLORS['overlay'],
        'axes.labelcolor': COLORS['text'],
        'text.color': COLORS['text'],
        'xtick.color': COLORS['subtext'],
        'ytick.color': COLORS['subtext'],
        'grid.color': COLORS['overlay'],
        'grid.alpha': 0.3,
        'legend.facecolor': COLORS['surface'],
        'legend.edgecolor': COLORS['overlay'],
        'font.family': 'sans-serif',
        'font.size': 10,
        'axes.titlesize': 12,
        'axes.labelsize': 11,
        'legend.fontsize': 9,
        'figure.dpi': 100,
        'savefig.dpi': 300,
        'savefig.bbox': 'tight',
    })


# =============================================================================
# STANDARD TEST DATA
# =============================================================================

@dataclass
class TestBoltParameters:
    """M12 L7 stud parameters"""
    diameter: float = 12.0        # mm
    pitch: float = 1.75           # mm
    length: float = 60.0          # mm
    elastic_modulus: float = 210e3  # MPa
    yield_strength: float = 720.0   # MPa
    
    @property
    def pitch_diameter(self) -> float:
        return self.diameter - 0.6495 * self.pitch
    
    @property
    def stress_area(self) -> float:
        d2 = self.pitch_diameter
        d3 = self.diameter - 1.0825 * self.pitch
        return np.pi / 4 * ((d2 + d3) / 2) ** 2


@dataclass  
class TestJointParameters:
    """Standard joint parameters"""
    bolt_stiffness: float = 5e5      # N/mm
    member_stiffness: float = 1.5e6  # N/mm
    mu_thread: float = 0.12
    mu_bearing: float = 0.14


@dataclass
class TestConditions:
    """Loading conditions"""
    initial_preload: float = 50000.0   # N
    frequency: float = 25.0            # Hz
    displacement_amplitude: float = 0.5  # mm


# Create global test data
BOLT = TestBoltParameters()
JOINT = TestJointParameters()
CONDITIONS = TestConditions()
F0 = CONDITIONS.initial_preload


# =============================================================================
# PRELOAD LOSS MODELS
# =============================================================================

def single_exponential(N: np.ndarray, 
                      lambda_decay: float = 0.005,
                      F_inf_ratio: float = 0.6) -> np.ndarray:
    """F(N) = F∞ + (F0 - F∞)·exp(-λN)"""
    F_inf = F_inf_ratio * F0
    return F_inf + (F0 - F_inf) * np.exp(-lambda_decay * N)


def double_exponential(N: np.ndarray,
                      lambda1: float = 0.05,
                      lambda2: float = 0.005,
                      A1_ratio: float = 0.15,
                      A2_ratio: float = 0.25,
                      F_inf_ratio: float = 0.6) -> np.ndarray:
    """F(N) = F∞ + A1·exp(-λ1·N) + A2·exp(-λ2·N)"""
    F_inf = F_inf_ratio * F0
    A1 = A1_ratio * F0
    A2 = A2_ratio * F0
    return F_inf + A1 * np.exp(-lambda1 * N) + A2 * np.exp(-lambda2 * N)


def stretched_exponential(N: np.ndarray,
                         N0: float = 500.0,
                         beta: float = 0.5) -> np.ndarray:
    """F(N) = F0·exp(-(N/N0)^β) - Kohlrausch-Williams-Watts"""
    return F0 * np.exp(-np.power(N / N0, beta))


def power_law(N: np.ndarray,
             alpha: float = 0.15,
             Nc: float = 10.0) -> np.ndarray:
    """F(N) = F0·(1 + N/Nc)^(-α) - Lu et al. 2024"""
    return F0 * np.power(1 + N / Nc, -alpha)


def logarithmic(N: np.ndarray,
               k: float = 2000.0) -> np.ndarray:
    """F(N) = F0 - k·ln(N+1)"""
    F = F0 - k * np.log(N + 1)
    return np.maximum(F, 0)


def jiang_two_stage(N: np.ndarray,
                   N_trans: float = 500.0,
                   delta_F_embed_ratio: float = 0.12,
                   N1: float = 50.0,
                   k2: float = 5.0) -> np.ndarray:
    """Jiang et al. two-stage loosening model"""
    N = np.atleast_1d(N)
    delta_F_embed = delta_F_embed_ratio * F0
    
    # Stage I preload at transition
    F_trans = F0 - delta_F_embed * (1 - np.exp(-N_trans / N1))
    
    F = np.zeros_like(N, dtype=float)
    
    # Stage I: Material loosening
    s1 = N <= N_trans
    F[s1] = F0 - delta_F_embed * (1 - np.exp(-N[s1] / N1))
    
    # Stage II: Structural loosening
    s2 = N > N_trans
    F[s2] = F_trans - k2 * (N[s2] - N_trans)
    
    return np.maximum(F, 0)


def jiang_three_stage(N: np.ndarray,
                     N_trans_12: float = 500.0,
                     N_trans_23: float = 50000.0,
                     delta_F1_ratio: float = 0.15,
                     N1: float = 50.0,
                     k2: float = 3.0,
                     k3: float = 0.5,
                     n3: float = 1.5) -> np.ndarray:
    """Extended Jiang three-stage model"""
    N = np.atleast_1d(N)
    delta_F1 = delta_F1_ratio * F0
    
    F_trans_12 = F0 - delta_F1 * (1 - np.exp(-N_trans_12 / N1))
    F_trans_23 = F_trans_12 - k2 * (N_trans_23 - N_trans_12)
    
    F = np.zeros_like(N, dtype=float)
    
    # Stage I
    s1 = N <= N_trans_12
    F[s1] = F0 - delta_F1 * (1 - np.exp(-N[s1] / N1))
    
    # Stage II
    s2 = (N > N_trans_12) & (N <= N_trans_23)
    F[s2] = F_trans_12 - k2 * (N[s2] - N_trans_12)
    
    # Stage III
    s3 = N > N_trans_23
    delta_N = N[s3] - N_trans_23
    F[s3] = F_trans_23 - k3 * np.power(delta_N, n3)
    
    return np.maximum(F, 0)


# =============================================================================
# PRELOAD RATE MODELS
# =============================================================================

def preload_rate_double_exp(N: np.ndarray,
                           lambda1: float = 0.05,
                           lambda2: float = 0.005,
                           A1_ratio: float = 0.15,
                           A2_ratio: float = 0.25) -> np.ndarray:
    """dF/dN for double exponential"""
    A1 = A1_ratio * F0
    A2 = A2_ratio * F0
    return -lambda1 * A1 * np.exp(-lambda1 * N) - lambda2 * A2 * np.exp(-lambda2 * N)


def preload_rate_jiang(N: np.ndarray,
                      N_trans: float = 500.0,
                      delta_F_embed_ratio: float = 0.12,
                      N1: float = 50.0,
                      k2: float = 5.0) -> np.ndarray:
    """dF/dN for Jiang two-stage"""
    N = np.atleast_1d(N)
    delta_F_embed = delta_F_embed_ratio * F0
    
    rate = np.zeros_like(N, dtype=float)
    
    # Stage I
    s1 = N <= N_trans
    rate[s1] = -delta_F_embed / N1 * np.exp(-N[s1] / N1)
    
    # Stage II
    s2 = N > N_trans
    rate[s2] = -k2
    
    return rate


# =============================================================================
# FRICTION EVOLUTION MODEL
# =============================================================================

def friction_evolution(N: np.ndarray,
                      mu_initial: float = 0.14,
                      mu_peak: float = 0.18,
                      mu_steady: float = 0.12,
                      N1: float = 50.0,
                      N2: float = 500.0,
                      N3: float = 5000.0,
                      beta_degrade: float = 0.01,
                      N_critical: float = 1e5) -> np.ndarray:
    """
    Hintikka three-phase friction evolution model:
    μ(N) = μ0 + (μ_peak - μ0)·(1 - e^(-N/N1))·e^(-N/N2) + (μ_ss - μ0)·(1 - e^(-N/N3))
    """
    N = np.atleast_1d(N)
    
    # Running-in peak term
    peak_term = (mu_peak - mu_initial) * (1 - np.exp(-N / N1)) * np.exp(-N / N2)
    
    # Stabilization term
    steady_term = (mu_steady - mu_initial) * (1 - np.exp(-N / N3))
    
    # Degradation term
    degrade_term = np.zeros_like(N, dtype=float)
    degrade_mask = N > N_critical
    if np.any(degrade_mask):
        degrade_term[degrade_mask] = beta_degrade * np.log(N[degrade_mask] / N_critical)
    
    mu = mu_initial + peak_term + steady_term + degrade_term
    
    return np.clip(mu, 0.02, 0.5)


# =============================================================================
# WEAR MODELS
# =============================================================================

def archard_wear_depth(N: np.ndarray,
                      K: float = 1e-6,
                      p_contact: float = 500.0,
                      delta: float = 0.5,
                      H: float = 3000.0) -> np.ndarray:
    """Cumulative Archard wear depth (mm)"""
    sliding_per_cycle = 4 * delta  # mm
    return K * p_contact * sliding_per_cycle * N / H


def fouvry_wear_depth(N: np.ndarray,
                     alpha: float = 3e-8,
                     mu: float = 0.12,
                     p_contact: float = 500.0,
                     delta: float = 0.5) -> np.ndarray:
    """Energy-based Fouvry wear (mm)"""
    E_per_cycle = mu * p_contact * delta  # Energy per cycle
    return alpha * E_per_cycle * N


# =============================================================================
# D-N CURVE MODEL
# =============================================================================

def dn_curve(d: np.ndarray,
            d_threshold: float = 0.1,
            C1: float = 5.0,
            m1: float = 3.0,
            C2: float = 4.0,
            m2: float = 1.5,
            d_transition: float = 0.5) -> np.ndarray:
    """D-N curve: displacement amplitude vs. cycles to loosening"""
    d = np.atleast_1d(d)
    N = np.zeros_like(d, dtype=float)
    
    # Below threshold: infinite life
    below_thresh = d <= d_threshold
    N[below_thresh] = np.inf
    
    # High-cycle region
    high_cycle = (d > d_threshold) & (d <= d_transition)
    N[high_cycle] = np.power(10, C1 - m1 * np.log10(d[high_cycle]))
    
    # Low-cycle region
    low_cycle = d > d_transition
    N[low_cycle] = np.power(10, C2 - m2 * np.log10(d[low_cycle]))
    
    return N


# =============================================================================
# PLOT FUNCTIONS
# =============================================================================

def plot_1_preload_vs_cycles() -> Figure:
    """Plot 1: Preload loss over cycles (multiple models)"""
    fig, ax = plt.subplots(figsize=(14, 8))
    
    N = np.linspace(0, 10000, 500)
    
    models = {
        'Single Exponential': (single_exponential(N), COLORS['blue']),
        'Double Exponential (Li et al.)': (double_exponential(N), COLORS['green']),
        'Stretched Exp. (KWW)': (stretched_exponential(N), COLORS['yellow']),
        'Power Law (Lu et al.)': (power_law(N), COLORS['peach']),
        'Jiang Two-Stage': (jiang_two_stage(N), COLORS['mauve']),
    }
    
    for name, (F, color) in models.items():
        F_pct = F / F0 * 100
        ax.plot(N, F_pct, label=name, color=color, linewidth=2)
    
    # Threshold lines
    ax.axhline(y=90, color=COLORS['yellow'], linestyle=':', alpha=0.7, label='90% threshold')
    ax.axhline(y=80, color=COLORS['red'], linestyle=':', alpha=0.7, label='80% threshold')
    
    # Stage boundary
    ax.axvline(x=500, color=COLORS['overlay'], linestyle='--', alpha=0.5)
    ax.text(550, 95, 'Stage I→II', fontsize=9, color=COLORS['subtext'])
    
    ax.set_xlabel('Number of Cycles (N)', fontsize=12)
    ax.set_ylabel('Preload Retention (%)', fontsize=12)
    ax.set_title('Preload Loss vs. Cycles: Multiple Model Comparison\n'
                f'M{BOLT.diameter} L7 Stud, F₀ = {F0/1000:.1f} kN', fontsize=14)
    ax.legend(loc='lower left', ncol=2)
    ax.grid(True, alpha=0.3)
    ax.set_ylim([40, 105])
    ax.set_xlim([0, 10000])
    
    return fig


def plot_2_preload_vs_time() -> Figure:
    """Plot 2: Preload loss over time"""
    fig, ax = plt.subplots(figsize=(14, 8))
    
    t_max = 100.0  # seconds
    f = CONDITIONS.frequency
    t = np.linspace(0, t_max, 500)
    N = t * f
    
    models = {
        'Double Exponential': (double_exponential(N), COLORS['green']),
        'Jiang Two-Stage': (jiang_two_stage(N), COLORS['mauve']),
        'Power Law': (power_law(N), COLORS['peach']),
    }
    
    for name, (F, color) in models.items():
        ax.plot(t, F / 1000, label=name, color=color, linewidth=2)
    
    # Secondary axis for cycles
    ax2 = ax.twiny()
    ax2.set_xlim(ax.get_xlim())
    ax2.set_xlabel('Equivalent Cycles (N)', color=COLORS['subtext'])
    cycle_ticks = np.array([0, 500, 1000, 1500, 2000, 2500])
    ax2.set_xticks(cycle_ticks / f)
    ax2.set_xticklabels([f'{int(c)}' for c in cycle_ticks])
    
    ax.set_xlabel('Time (s)', fontsize=12)
    ax.set_ylabel('Preload Force (kN)', fontsize=12)
    ax.set_title(f'Preload Loss vs. Time (f = {f} Hz)\n'
                f'M{BOLT.diameter} L7 Stud', fontsize=14)
    ax.legend(loc='lower left')
    ax.grid(True, alpha=0.3)
    
    return fig


def plot_3_loosening_rate() -> Figure:
    """Plot 3: Loosening rate (dF/dN) evolution"""
    fig, ax = plt.subplots(figsize=(14, 8))
    
    N = np.logspace(0, 4, 500)
    
    # Double exponential rate
    rate_double = -preload_rate_double_exp(N)
    rate_double_pct = rate_double / F0 * 100
    
    # Jiang rate
    rate_jiang = -preload_rate_jiang(N)
    rate_jiang_pct = rate_jiang / F0 * 100
    
    ax.loglog(N, rate_double_pct, label='Double Exponential', 
             color=COLORS['green'], linewidth=2)
    ax.loglog(N, rate_jiang_pct, label='Jiang Two-Stage',
             color=COLORS['mauve'], linewidth=2)
    
    # Stage boundary
    ax.axvline(x=500, color=COLORS['overlay'], linestyle='--', alpha=0.7)
    ax.text(520, 0.001, 'Stage I→II', fontsize=9, color=COLORS['subtext'])
    
    ax.set_xlabel('Number of Cycles (N)', fontsize=12)
    ax.set_ylabel('Loosening Rate (%/cycle)', fontsize=12)
    ax.set_title('Preload Loss Rate Evolution', fontsize=14)
    ax.legend()
    ax.grid(True, alpha=0.3, which='both')
    
    return fig


def plot_4_stage_analysis() -> Figure:
    """Plot 4: Jiang three-stage model with stage identification"""
    fig, ax = plt.subplots(figsize=(14, 8))
    
    N_max = 100000
    N = np.logspace(0, np.log10(N_max), 1000)
    
    N_trans_12 = 500
    N_trans_23 = 50000
    
    F = jiang_three_stage(N, N_trans_12=N_trans_12, N_trans_23=N_trans_23)
    F_trans_12 = jiang_three_stage(np.array([N_trans_12]))[0]
    F_trans_23 = jiang_three_stage(np.array([N_trans_23]))[0]
    
    # Plot each stage
    s1 = N <= N_trans_12
    s2 = (N > N_trans_12) & (N <= N_trans_23)
    s3 = N > N_trans_23
    
    ax.semilogx(N[s1], F[s1] / 1000, color=COLORS['green'], linewidth=2.5, label='Stage I')
    ax.semilogx(N[s2], F[s2] / 1000, color=COLORS['yellow'], linewidth=2.5, label='Stage II')
    ax.semilogx(N[s3], F[s3] / 1000, color=COLORS['red'], linewidth=2.5, label='Stage III')
    
    # Stage boundaries
    ax.axvline(x=N_trans_12, color=COLORS['overlay'], linestyle='--', linewidth=1.5)
    ax.axvline(x=N_trans_23, color=COLORS['overlay'], linestyle='--', linewidth=1.5)
    
    # Annotations
    ax.annotate('Stage I\nPlastic Deformation\n(Embedding)', 
               xy=(50, F0/1000*0.92), fontsize=10, color=COLORS['green'],
               bbox=dict(boxstyle='round', facecolor=COLORS['surface'], alpha=0.8))
    ax.annotate('Stage II\nRotational Loosening\n(Linear Decay)',
               xy=(3000, F_trans_12/1000*0.85), fontsize=10, color=COLORS['yellow'],
               bbox=dict(boxstyle='round', facecolor=COLORS['surface'], alpha=0.8))
    ax.annotate('Stage III\nFatigue Degradation\n(Accelerating)',
               xy=(60000, F_trans_23/1000*0.75), fontsize=10, color=COLORS['red'],
               bbox=dict(boxstyle='round', facecolor=COLORS['surface'], alpha=0.8))
    
    ax.set_xlabel('Number of Cycles (N)', fontsize=12)
    ax.set_ylabel('Preload Force (kN)', fontsize=12)
    ax.set_title('Jiang Three-Stage Loosening Model\n'
                f'Stage I→II at {N_trans_12} cycles, Stage II→III at {N_trans_23} cycles', 
                fontsize=14)
    ax.legend(loc='lower left')
    ax.grid(True, alpha=0.3, which='both')
    
    return fig


def plot_5_friction_evolution() -> Figure:
    """Plot 5: Friction coefficient evolution over cycles"""
    fig, ax = plt.subplots(figsize=(14, 8))
    
    N_max = 200000
    N = np.logspace(0, np.log10(N_max), 500)
    
    mu_init = 0.14
    mu_peak = 0.18
    mu_steady = 0.12
    N_critical = 1e5
    
    mu = friction_evolution(N)
    
    ax.semilogx(N, mu, color=COLORS['mauve'], linewidth=2.5, label='μ(N)')
    
    # Reference lines
    ax.axhline(y=mu_init, color=COLORS['blue'], linestyle='--', 
              alpha=0.7, label=f'μ₀ = {mu_init}')
    ax.axhline(y=mu_peak, color=COLORS['peach'], linestyle='--',
              alpha=0.7, label=f'μ_peak = {mu_peak}')
    ax.axhline(y=mu_steady, color=COLORS['green'], linestyle='--',
              alpha=0.7, label=f'μ_ss = {mu_steady}')
    
    # Phase regions
    ax.axvspan(1, 100, alpha=0.1, color=COLORS['blue'])
    ax.axvspan(100, N_critical, alpha=0.1, color=COLORS['green'])
    ax.axvspan(N_critical, N_max, alpha=0.1, color=COLORS['red'])
    
    ax.annotate('Running-in', xy=(20, 0.20), fontsize=10, color=COLORS['blue'])
    ax.annotate('Steady-state', xy=(5000, 0.20), fontsize=10, color=COLORS['green'])
    ax.annotate('Degradation', xy=(120000, 0.20), fontsize=10, color=COLORS['red'])
    
    ax.set_xlabel('Number of Cycles (N)', fontsize=12)
    ax.set_ylabel('Friction Coefficient (μ)', fontsize=12)
    ax.set_title('Friction Coefficient Evolution (Hintikka Three-Phase Model)', fontsize=14)
    ax.legend(loc='upper right')
    ax.grid(True, alpha=0.3, which='both')
    ax.set_ylim([0.05, 0.22])
    
    return fig


def plot_6_wear_evolution() -> Figure:
    """Plot 6: Wear depth evolution"""
    fig, ax = plt.subplots(figsize=(14, 8))
    
    N_max = 100000
    N = np.linspace(0, N_max, 500)
    
    h_archard = archard_wear_depth(N) * 1000  # Convert to μm
    h_fouvry = fouvry_wear_depth(N) * 1000
    
    ax.plot(N, h_archard, color=COLORS['peach'], linewidth=2.5, 
           label='Archard Model')
    ax.plot(N, h_fouvry, color=COLORS['teal'], linewidth=2.5,
           label='Fouvry Energy-Based')
    
    # Critical wear thresholds
    ax.axhline(y=5, color=COLORS['yellow'], linestyle=':', 
              alpha=0.7, label='5 μm warning')
    ax.axhline(y=10, color=COLORS['red'], linestyle=':',
              alpha=0.7, label='10 μm critical')
    
    ax.set_xlabel('Number of Cycles (N)', fontsize=12)
    ax.set_ylabel('Cumulative Wear Depth (μm)', fontsize=12)
    ax.set_title('Wear Depth Evolution: Archard vs. Fouvry Models\n'
                f'p = 500 MPa, δ = 0.5 mm', fontsize=14)
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    return fig


def plot_7_dn_curve() -> Figure:
    """Plot 7: D-N curve (displacement vs. cycles to loosening)"""
    fig, ax = plt.subplots(figsize=(14, 8))
    
    d = np.logspace(-1.5, 1, 100)
    N = dn_curve(d)
    
    # Filter infinite lives
    valid = np.isfinite(N)
    
    ax.loglog(d[valid], N[valid], color=COLORS['mauve'], linewidth=2.5, label='D-N Curve')
    
    # Threshold and transition lines
    d_th = 0.1
    d_trans = 0.5
    
    ax.axvline(x=d_th, color=COLORS['green'], linestyle='--', 
              alpha=0.7, label=f'd_threshold = {d_th} mm')
    ax.axvline(x=d_trans, color=COLORS['yellow'], linestyle=':',
              alpha=0.7, label=f'd_transition = {d_trans} mm')
    
    # Simulated experimental data
    np.random.seed(42)
    d_exp = np.array([0.2, 0.3, 0.5, 0.7, 1.0, 1.5, 2.0])
    N_exp = dn_curve(d_exp)
    N_exp_scatter = N_exp * (1 + 0.3 * (np.random.rand(len(d_exp)) - 0.5))
    ax.scatter(d_exp, N_exp_scatter, color=COLORS['peach'], s=80, zorder=5,
              label='Experimental data', edgecolor=COLORS['text'], linewidth=1)
    
    # Endurance region
    ax.fill_between([0.03, d_th], [1, 1], [1e8, 1e8], alpha=0.15, 
                   color=COLORS['green'])
    ax.annotate('Endurance\nRegion', xy=(0.05, 1e6), fontsize=10, 
               color=COLORS['green'])
    
    ax.set_xlabel('Displacement Amplitude (mm)', fontsize=12)
    ax.set_ylabel('Cycles to Loosening (N_L)', fontsize=12)
    ax.set_title('D-N Curve: Displacement-Life Relationship\n'
                '(Analogous to S-N Fatigue Curve)', fontsize=14)
    ax.legend(loc='lower left')
    ax.grid(True, alpha=0.3, which='both')
    ax.set_xlim([0.03, 10])
    ax.set_ylim([10, 1e8])
    
    return fig


def plot_8_coupled_evolution() -> Figure:
    """Plot 8: Coupled friction-preload evolution"""
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(14, 12), sharex=True)
    
    N_max = 50000
    N = np.linspace(0, N_max, 500)
    
    # Base models
    F = jiang_two_stage(N)
    mu = friction_evolution(N)
    
    # Coupled effect: friction affects preload rate
    # Simple coupling: higher friction = slower loosening
    coupling_factor = mu / 0.12
    F_coupled = F * (1 + 0.05 * (coupling_factor - 1))
    
    # Preload plot
    ax1.plot(N, F / 1000, color=COLORS['blue'], linewidth=2, 
            label='Uncoupled')
    ax1.plot(N, F_coupled / 1000, color=COLORS['teal'], linewidth=2,
            linestyle='--', label='Coupled')
    ax1.axhline(y=F0 * 0.9 / 1000, color=COLORS['yellow'], linestyle=':', alpha=0.7)
    ax1.set_ylabel('Preload (kN)', fontsize=12)
    ax1.set_title('Coupled Friction-Preload Evolution Analysis', fontsize=14)
    ax1.legend(loc='lower left')
    ax1.grid(True, alpha=0.3)
    
    # Friction plot
    ax2.plot(N, mu, color=COLORS['mauve'], linewidth=2)
    ax2.set_ylabel('Friction Coef. (μ)', fontsize=12)
    ax2.grid(True, alpha=0.3)
    
    # Contact pressure (proportional to preload)
    p_contact = F / 100
    p_coupled = F_coupled / 100
    ax3.plot(N, p_contact, color=COLORS['blue'], linewidth=2, label='Uncoupled')
    ax3.plot(N, p_coupled, color=COLORS['teal'], linewidth=2, 
            linestyle='--', label='Coupled')
    ax3.set_xlabel('Number of Cycles (N)', fontsize=12)
    ax3.set_ylabel('Contact Pressure (MPa)', fontsize=12)
    ax3.legend(loc='lower left')
    ax3.grid(True, alpha=0.3)
    
    plt.tight_layout()
    return fig


def plot_9_comprehensive_dashboard() -> Figure:
    """Plot 9: Comprehensive dashboard with all phenomena"""
    fig = plt.figure(figsize=(20, 16))
    gs = GridSpec(3, 3, figure=fig, hspace=0.35, wspace=0.3)
    
    # 1. Preload vs Cycles (top left, wide)
    ax1 = fig.add_subplot(gs[0, :2])
    N = np.linspace(0, 10000, 500)
    for name, (model_func, color) in [
        ('Double Exp.', (double_exponential, COLORS['green'])),
        ('Jiang', (jiang_two_stage, COLORS['mauve'])),
        ('Power Law', (power_law, COLORS['peach']))
    ]:
        F = model_func(N)
        ax1.plot(N, F / F0 * 100, label=name, color=color, linewidth=2)
    ax1.axhline(y=90, color=COLORS['yellow'], linestyle=':', alpha=0.7)
    ax1.axhline(y=80, color=COLORS['red'], linestyle=':', alpha=0.7)
    ax1.set_xlabel('Cycles')
    ax1.set_ylabel('Preload (%)')
    ax1.set_title('Preload Loss vs. Cycles')
    ax1.legend(loc='lower left')
    ax1.grid(True, alpha=0.3)
    ax1.set_ylim([50, 105])
    
    # 2. Loosening Rate (top right)
    ax2 = fig.add_subplot(gs[0, 2])
    N_log = np.logspace(0, 4, 300)
    rate = -preload_rate_double_exp(N_log) / F0 * 100
    ax2.loglog(N_log, rate, color=COLORS['green'], linewidth=2)
    ax2.set_xlabel('Cycles')
    ax2.set_ylabel('Rate (%/cycle)')
    ax2.set_title('Loosening Rate')
    ax2.grid(True, alpha=0.3, which='both')
    
    # 3. Stage Analysis (middle left)
    ax3 = fig.add_subplot(gs[1, 0])
    N_log = np.logspace(0, 5, 500)
    F = jiang_three_stage(N_log)
    stages = np.ones_like(N_log)
    stages[N_log > 500] = 2
    stages[N_log > 50000] = 3
    for s, color in [(1, COLORS['green']), (2, COLORS['yellow']), (3, COLORS['red'])]:
        mask = stages == s
        if np.any(mask):
            ax3.semilogx(N_log[mask], F[mask] / 1000, color=color, linewidth=2)
    ax3.set_xlabel('Cycles')
    ax3.set_ylabel('Preload (kN)')
    ax3.set_title('Three-Stage Model')
    ax3.grid(True, alpha=0.3, which='both')
    
    # 4. Friction Evolution (middle center)
    ax4 = fig.add_subplot(gs[1, 1])
    N_log = np.logspace(0, np.log10(200000), 500)
    mu = friction_evolution(N_log)
    ax4.semilogx(N_log, mu, color=COLORS['mauve'], linewidth=2)
    ax4.axhline(y=0.12, color=COLORS['green'], linestyle='--', alpha=0.7)
    ax4.set_xlabel('Cycles')
    ax4.set_ylabel('Friction (μ)')
    ax4.set_title('Friction Evolution')
    ax4.grid(True, alpha=0.3, which='both')
    ax4.set_ylim([0.08, 0.20])
    
    # 5. Wear Evolution (middle right)
    ax5 = fig.add_subplot(gs[1, 2])
    N = np.linspace(0, 100000, 500)
    h_a = archard_wear_depth(N) * 1000
    h_f = fouvry_wear_depth(N) * 1000
    ax5.plot(N, h_a, color=COLORS['peach'], linewidth=2, label='Archard')
    ax5.plot(N, h_f, color=COLORS['teal'], linewidth=2, label='Fouvry')
    ax5.set_xlabel('Cycles')
    ax5.set_ylabel('Wear (μm)')
    ax5.set_title('Wear Depth')
    ax5.legend(fontsize=8)
    ax5.grid(True, alpha=0.3)
    
    # 6. D-N Curve (bottom left)
    ax6 = fig.add_subplot(gs[2, 0])
    d = np.logspace(-1.5, 1, 100)
    N_dn = dn_curve(d)
    valid = np.isfinite(N_dn)
    ax6.loglog(d[valid], N_dn[valid], color=COLORS['mauve'], linewidth=2)
    ax6.axvline(x=0.1, color=COLORS['green'], linestyle='--', alpha=0.7)
    ax6.set_xlabel('Displacement (mm)')
    ax6.set_ylabel('Cycles to Loosen')
    ax6.set_title('D-N Curve')
    ax6.grid(True, alpha=0.3, which='both')
    
    # 7. Model Comparison (bottom center and right)
    ax7 = fig.add_subplot(gs[2, 1:])
    N = np.linspace(0, 5000, 500)
    models = [
        ('Single Exp.', single_exponential, COLORS['blue']),
        ('Double Exp.', double_exponential, COLORS['green']),
        ('Stretched Exp.', stretched_exponential, COLORS['yellow']),
        ('Power Law', power_law, COLORS['peach']),
        ('Logarithmic', logarithmic, COLORS['pink']),
        ('Jiang 2-Stage', jiang_two_stage, COLORS['mauve']),
    ]
    for name, func, color in models:
        F = func(N)
        ax7.plot(N, F / F0 * 100, label=name, color=color, linewidth=1.5)
    ax7.axhline(y=90, color=COLORS['yellow'], linestyle=':', alpha=0.7)
    ax7.axhline(y=80, color=COLORS['red'], linestyle=':', alpha=0.7)
    ax7.set_xlabel('Cycles')
    ax7.set_ylabel('Preload (%)')
    ax7.set_title('All Models Comparison')
    ax7.legend(loc='lower left', ncol=3, fontsize=8)
    ax7.grid(True, alpha=0.3)
    ax7.set_ylim([40, 105])
    
    # Main title
    fig.suptitle('Bolt Analysis Studio - Comprehensive Loosening Analysis Dashboard\n'
                f'M{BOLT.diameter} L7 Stud, F₀ = {F0/1000:.1f} kN, f = {CONDITIONS.frequency} Hz',
                fontsize=16, fontweight='bold', y=0.98)
    
    return fig


# =============================================================================
# MAIN EXECUTION
# =============================================================================

def main():
    """Generate all plots and save them"""
    print("="*70)
    print("BOLT ANALYSIS STUDIO - PART 1: ANALYSIS ENGINE")
    print("Comprehensive Loosening Phenomena Visualization")
    print("="*70)
    print()
    
    # Setup style
    setup_plot_style()
    
    # Create output directory
    output_dir = Path("output_plots")
    output_dir.mkdir(exist_ok=True)
    
    # Generate all plots
    plots = [
        ("01_preload_vs_cycles.png", plot_1_preload_vs_cycles, "Preload vs. Cycles (Multiple Models)"),
        ("02_preload_vs_time.png", plot_2_preload_vs_time, "Preload vs. Time"),
        ("03_loosening_rate.png", plot_3_loosening_rate, "Loosening Rate Evolution"),
        ("04_stage_analysis.png", plot_4_stage_analysis, "Jiang Three-Stage Model"),
        ("05_friction_evolution.png", plot_5_friction_evolution, "Friction Coefficient Evolution"),
        ("06_wear_evolution.png", plot_6_wear_evolution, "Wear Depth Evolution"),
        ("07_dn_curve.png", plot_7_dn_curve, "D-N Curve (Displacement-Life)"),
        ("08_coupled_evolution.png", plot_8_coupled_evolution, "Coupled Friction-Preload"),
        ("09_dashboard.png", plot_9_comprehensive_dashboard, "Comprehensive Dashboard"),
    ]
    
    print(f"Test Parameters:")
    print(f"  Bolt: M{BOLT.diameter} L7 grade stud")
    print(f"  Pitch: {BOLT.pitch} mm")
    print(f"  Initial Preload: {F0/1000:.1f} kN")
    print(f"  Frequency: {CONDITIONS.frequency} Hz")
    print(f"  μ_thread: {JOINT.mu_thread}, μ_bearing: {JOINT.mu_bearing}")
    print()
    
    print("Generating plots...")
    print("-"*70)
    
    for filename, plot_func, description in plots:
        try:
            print(f"  [{len([p for p in plots if p[0] <= filename])}/{len(plots)}] {description}...", end=" ")
            fig = plot_func()
            filepath = output_dir / filename
            fig.savefig(filepath, dpi=300, facecolor=fig.get_facecolor(), 
                       edgecolor='none', bbox_inches='tight')
            plt.close(fig)
            print(f"✓ Saved: {filepath}")
        except Exception as e:
            print(f"✗ Error: {e}")
    
    print("-"*70)
    print()
    print(f"All plots saved to: {output_dir.absolute()}")
    print()
    print("Generated Plots:")
    for filename, _, description in plots:
        print(f"  • {filename}: {description}")
    
    print()
    print("="*70)
    print("ANALYSIS COMPLETE")
    print("="*70)


if __name__ == "__main__":
    main()
