"""
Contact Analysis Visualization Module
Bolt Analysis Studio v4.0
Prof. Leonardo Rosa Ribeiro da Silva, PhD

Enhanced visualization for complete contact analysis results:
- Preload evolution with loss breakdown
- Loosening angle progression
- Per-thread wear and load distribution
- Friction evolution across contacts
- Contact force time histories
- Gasket compression curves
- Preload loss pie charts
- Junker test phase identification
- Multi-panel summary dashboards

Uses Catppuccin Mocha color scheme for dark-mode plots.
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.axes import Axes
from matplotlib.gridspec import GridSpec
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path

# Dynamic color scheme from central Theme
from bolt_analysis_studio.gui.theme import Theme as _Theme


class _ThemeColorProxy(dict):
    """Dict-like object that always reads from Theme.get_plot_colors()."""
    def __getitem__(self, key):
        return _Theme.get_plot_colors()[key]
    def get(self, key, default=None):
        return _Theme.get_plot_colors().get(key, default)
    def __contains__(self, key):
        return key in _Theme.get_plot_colors()
    def values(self):
        return _Theme.get_plot_colors().values()
    def keys(self):
        return _Theme.get_plot_colors().keys()
    def items(self):
        return _Theme.get_plot_colors().items()

COLORS = _ThemeColorProxy()


def _apply_contact_plot_style():
    """Apply current theme to matplotlib rcParams."""
    plt.style.use(_Theme.get_matplotlib_style_name())
    plt.rcParams.update(_Theme.get_plot_style())
    plt.rcParams.update({
        'legend.framealpha': 0.9,
    })

_apply_contact_plot_style()


def plot_preload_vs_cycles(
    cycle_data: Dict[str, np.ndarray],
    breakdown: Optional[Dict[str, np.ndarray]] = None,
    save_path: Optional[Path] = None
) -> Figure:
    """
    Plot preload evolution vs loading cycles with optional loss breakdown.

    Args:
        cycle_data: Dictionary with 'cycle' and 'preload' arrays
        breakdown: Optional breakdown of loss sources vs cycle
        save_path: Path to save figure

    Returns:
        matplotlib Figure
    """
    fig, ax = plt.subplots(figsize=(10, 6))

    cycles = np.array(cycle_data['cycle'])
    preload = np.array(cycle_data['preload'])

    # Main preload curve
    ax.plot(cycles, preload / 1000, linewidth=2.5, color=COLORS['blue'],
            label='Total Preload', zorder=10)

    # Loss breakdown (stacked area)
    if breakdown is not None:
        bottom = np.zeros_like(cycles)
        colors = [COLORS['red'], COLORS['yellow'], COLORS['green'], COLORS['peach']]
        for i, (source, values) in enumerate(breakdown.items()):
            ax.fill_between(cycles, bottom, bottom + values / 1000,
                           alpha=0.6, color=colors[i % len(colors)],
                           label=source, zorder=5)
            bottom += values / 1000

    ax.set_xlabel('Loading Cycles', fontsize=12, fontweight='bold')
    ax.set_ylabel('Preload [kN]', fontsize=12, fontweight='bold')
    ax.set_title('Preload Evolution vs Cycles', fontsize=14, fontweight='bold',
                 pad=15)
    ax.grid(True, alpha=0.3)
    ax.legend(loc='best', framealpha=0.9)

    # Add statistics box
    if len(preload) > 0:
        initial = preload[0]
        final = preload[-1]
        loss_pct = 100 * (initial - final) / initial if initial > 0 else 0
        textstr = f'Initial: {initial/1000:.1f} kN\nFinal: {final/1000:.1f} kN\nLoss: {loss_pct:.1f}%'
        props = dict(boxstyle='round', facecolor=COLORS['surface'], alpha=0.9,
                    edgecolor=COLORS['overlay'])
        ax.text(0.02, 0.98, textstr, transform=ax.transAxes, fontsize=10,
               verticalalignment='top', bbox=props)

    fig.tight_layout()

    if save_path:
        fig.savefig(save_path, dpi=300, facecolor=COLORS['background'])

    return fig


def plot_loosening_angle_vs_time(
    time: np.ndarray,
    angle_rad: np.ndarray,
    phases: Optional[List[Tuple[float, str]]] = None,
    save_path: Optional[Path] = None
) -> Figure:
    """
    Plot cumulative loosening angle vs time with phase identification.

    Args:
        time: Time array [s]
        angle_rad: Loosening angle array [rad]
        phases: Optional list of (time, phase_name) tuples
        save_path: Path to save figure

    Returns:
        matplotlib Figure
    """
    fig, ax = plt.subplots(figsize=(10, 6))

    angle_deg = np.degrees(angle_rad)

    # Main curve
    ax.plot(time, angle_deg, linewidth=2.5, color=COLORS['mauve'],
            label='Loosening Angle')

    # Phase regions
    if phases is not None:
        phase_colors = {
            'Phase I': COLORS['green'],
            'Phase II': COLORS['yellow'],
            'Phase III': COLORS['red']
        }
        for i, (t_phase, phase_name) in enumerate(phases[:-1]):
            t_next = phases[i+1][0] if i+1 < len(phases) else time[-1]
            ax.axvspan(t_phase, t_next, alpha=0.2,
                      color=phase_colors.get(phase_name, COLORS['overlay']),
                      label=phase_name if i == 0 or phases[i-1][1] != phase_name else "")

    ax.set_xlabel('Time [s]', fontsize=12, fontweight='bold')
    ax.set_ylabel('Loosening Angle [deg]', fontsize=12, fontweight='bold')
    ax.set_title('Cumulative Loosening Angle vs Time', fontsize=14, fontweight='bold',
                 pad=15)
    ax.grid(True, alpha=0.3)

    # Remove duplicate legend entries
    handles, labels = ax.get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    ax.legend(by_label.values(), by_label.keys(), loc='best', framealpha=0.9)

    fig.tight_layout()

    if save_path:
        fig.savefig(save_path, dpi=300, facecolor=COLORS['background'])

    return fig


def plot_per_thread_wear(
    thread_numbers: np.ndarray,
    wear_depth: np.ndarray,
    save_path: Optional[Path] = None
) -> Figure:
    """
    Plot wear depth for each engaged thread.

    Args:
        thread_numbers: Thread indices (1, 2, 3, ...)
        wear_depth: Wear depth for each thread [m]
        save_path: Path to save figure

    Returns:
        matplotlib Figure
    """
    fig, ax = plt.subplots(figsize=(10, 6))

    colors = [COLORS['blue'] if w == max(wear_depth) else COLORS['teal']
              for w in wear_depth]

    ax.bar(thread_numbers, wear_depth * 1e6, color=colors, alpha=0.8,
           edgecolor=COLORS['text'], linewidth=0.5)

    ax.set_xlabel('Thread Number', fontsize=12, fontweight='bold')
    ax.set_ylabel('Wear Depth [μm]', fontsize=12, fontweight='bold')
    ax.set_title('Per-Thread Wear Distribution', fontsize=14, fontweight='bold',
                 pad=15)
    ax.grid(True, alpha=0.3, axis='y')

    # Add average line
    avg_wear = np.mean(wear_depth) * 1e6
    ax.axhline(avg_wear, color=COLORS['yellow'], linestyle='--', linewidth=2,
               label=f'Average: {avg_wear:.2f} μm')
    ax.legend(loc='best', framealpha=0.9)

    fig.tight_layout()

    if save_path:
        fig.savefig(save_path, dpi=300, facecolor=COLORS['background'])

    return fig


def plot_per_thread_load_distribution(
    thread_numbers: np.ndarray,
    load_fraction: np.ndarray,
    save_path: Optional[Path] = None
) -> Figure:
    """
    Plot load distribution across engaged threads.

    Args:
        thread_numbers: Thread indices
        load_fraction: Fraction of total load per thread
        save_path: Path to save figure

    Returns:
        matplotlib Figure
    """
    fig, ax = plt.subplots(figsize=(10, 6))

    ax.bar(thread_numbers, load_fraction * 100, color=COLORS['green'],
           alpha=0.8, edgecolor=COLORS['text'], linewidth=0.5)

    ax.set_xlabel('Thread Number', fontsize=12, fontweight='bold')
    ax.set_ylabel('Load Fraction [%]', fontsize=12, fontweight='bold')
    ax.set_title('Per-Thread Load Distribution', fontsize=14, fontweight='bold',
                 pad=15)
    ax.grid(True, alpha=0.3, axis='y')

    # Add uniform line
    uniform = 100.0 / len(thread_numbers)
    ax.axhline(uniform, color=COLORS['yellow'], linestyle='--', linewidth=2,
               label=f'Uniform: {uniform:.1f}%')
    ax.legend(loc='best', framealpha=0.9)

    fig.tight_layout()

    if save_path:
        fig.savefig(save_path, dpi=300, facecolor=COLORS['background'])

    return fig


def plot_friction_evolution(
    time: np.ndarray,
    contact_friction: Dict[str, np.ndarray],
    save_path: Optional[Path] = None
) -> Figure:
    """
    Plot friction coefficient evolution for all contacts.

    Args:
        time: Time array [s]
        contact_friction: Dict of contact_name -> mu(t) array
        save_path: Path to save figure

    Returns:
        matplotlib Figure
    """
    fig, ax = plt.subplots(figsize=(10, 6))

    colors = [COLORS['blue'], COLORS['green'], COLORS['yellow'],
              COLORS['peach'], COLORS['pink']]

    for i, (contact_name, mu) in enumerate(contact_friction.items()):
        ax.plot(time, mu, linewidth=2, color=colors[i % len(colors)],
                label=contact_name, alpha=0.9)

    ax.set_xlabel('Time [s]', fontsize=12, fontweight='bold')
    ax.set_ylabel('Friction Coefficient μ', fontsize=12, fontweight='bold')
    ax.set_title('Friction Evolution Across Contacts', fontsize=14, fontweight='bold',
                 pad=15)
    ax.grid(True, alpha=0.3)
    ax.legend(loc='best', framealpha=0.9, ncol=2)

    fig.tight_layout()

    if save_path:
        fig.savefig(save_path, dpi=300, facecolor=COLORS['background'])

    return fig


def plot_contact_forces_time_history(
    time: np.ndarray,
    contact_forces: Dict[str, np.ndarray],
    save_path: Optional[Path] = None
) -> Figure:
    """
    Plot contact force time histories.

    Args:
        time: Time array [s]
        contact_forces: Dict of contact_name -> force(t) array [N]
        save_path: Path to save figure

    Returns:
        matplotlib Figure
    """
    fig, ax = plt.subplots(figsize=(10, 6))

    colors = [COLORS['blue'], COLORS['green'], COLORS['yellow'],
              COLORS['peach'], COLORS['pink']]

    for i, (contact_name, force) in enumerate(contact_forces.items()):
        ax.plot(time, force / 1000, linewidth=2, color=colors[i % len(colors)],
                label=contact_name, alpha=0.9)

    ax.set_xlabel('Time [s]', fontsize=12, fontweight='bold')
    ax.set_ylabel('Contact Force [kN]', fontsize=12, fontweight='bold')
    ax.set_title('Contact Force Time Histories', fontsize=14, fontweight='bold',
                 pad=15)
    ax.grid(True, alpha=0.3)
    ax.legend(loc='best', framealpha=0.9, ncol=2)

    fig.tight_layout()

    if save_path:
        fig.savefig(save_path, dpi=300, facecolor=COLORS['background'])

    return fig


def plot_gasket_compression_vs_time(
    time: np.ndarray,
    compression: np.ndarray,
    initial_thickness: float,
    save_path: Optional[Path] = None
) -> Figure:
    """
    Plot gasket compression vs time.

    Args:
        time: Time array [s]
        compression: Compression distance [m]
        initial_thickness: Initial gasket thickness [m]
        save_path: Path to save figure

    Returns:
        matplotlib Figure
    """
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), sharex=True)

    compression_mm = compression * 1000
    compression_pct = 100 * compression / initial_thickness

    # Absolute compression
    ax1.plot(time, compression_mm, linewidth=2.5, color=COLORS['teal'])
    ax1.set_ylabel('Compression [mm]', fontsize=12, fontweight='bold')
    ax1.set_title('Gasket Compression vs Time', fontsize=14, fontweight='bold',
                  pad=15)
    ax1.grid(True, alpha=0.3)

    # Percentage compression
    ax2.plot(time, compression_pct, linewidth=2.5, color=COLORS['peach'])
    ax2.set_xlabel('Time [s]', fontsize=12, fontweight='bold')
    ax2.set_ylabel('Compression [%]', fontsize=12, fontweight='bold')
    ax2.grid(True, alpha=0.3)

    fig.tight_layout()

    if save_path:
        fig.savefig(save_path, dpi=300, facecolor=COLORS['background'])

    return fig


def plot_preload_loss_pie_chart(
    loss_breakdown: Dict[str, float],
    save_path: Optional[Path] = None
) -> Figure:
    """
    Plot preload loss breakdown as pie chart.

    Args:
        loss_breakdown: Dict of source -> loss amount [N]
        save_path: Path to save figure

    Returns:
        matplotlib Figure
    """
    fig, ax = plt.subplots(figsize=(8, 8))

    sources = list(loss_breakdown.keys())
    values = list(loss_breakdown.values())

    colors_list = [COLORS['red'], COLORS['yellow'], COLORS['green'],
                   COLORS['blue'], COLORS['peach'], COLORS['pink']]

    wedges, texts, autotexts = ax.pie(
        values,
        labels=sources,
        autopct='%1.1f%%',
        startangle=90,
        colors=colors_list[:len(sources)],
        textprops={'color': COLORS['text'], 'fontsize': 11},
        wedgeprops={'edgecolor': COLORS['text'], 'linewidth': 1}
    )

    # Bold percentage text
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontweight('bold')
        autotext.set_fontsize(12)

    ax.set_title('Preload Loss Breakdown by Mechanism',
                fontsize=14, fontweight='bold', pad=20)

    fig.tight_layout()

    if save_path:
        fig.savefig(save_path, dpi=300, facecolor=COLORS['background'])

    return fig


def plot_junker_loosening_phases(
    time: np.ndarray,
    preload: np.ndarray,
    phase_transitions: List[Tuple[float, str]],
    save_path: Optional[Path] = None
) -> Figure:
    """
    Plot Junker test with phase identification.

    Args:
        time: Time array [s]
        preload: Preload array [N]
        phase_transitions: List of (time, phase_name)
        save_path: Path to save figure

    Returns:
        matplotlib Figure
    """
    fig, ax = plt.subplots(figsize=(12, 6))

    # Plot preload
    ax.plot(time, preload / 1000, linewidth=2.5, color=COLORS['blue'],
            label='Preload', zorder=10)

    # Phase regions
    phase_colors = {
        'Phase I': (COLORS['green'], 0.2),
        'Phase II': (COLORS['yellow'], 0.2),
        'Phase III': (COLORS['red'], 0.2)
    }

    for i, (t_trans, phase) in enumerate(phase_transitions[:-1]):
        t_next = phase_transitions[i+1][0] if i+1 < len(phase_transitions) else time[-1]
        color, alpha = phase_colors.get(phase, (COLORS['overlay'], 0.1))
        ax.axvspan(t_trans, t_next, alpha=alpha, color=color,
                  label=phase if i == 0 or phase_transitions[i-1][1] != phase else "")

    ax.set_xlabel('Time [s]', fontsize=12, fontweight='bold')
    ax.set_ylabel('Preload [kN]', fontsize=12, fontweight='bold')
    ax.set_title('Junker Test: Loosening Phases', fontsize=14, fontweight='bold',
                 pad=15)
    ax.grid(True, alpha=0.3)

    # Remove duplicate labels
    handles, labels = ax.get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    ax.legend(by_label.values(), by_label.keys(), loc='best', framealpha=0.9)

    fig.tight_layout()

    if save_path:
        fig.savefig(save_path, dpi=300, facecolor=COLORS['background'])

    return fig


def plot_contact_summary_dashboard(
    analysis_result: Any,
    save_path: Optional[Path] = None
) -> Figure:
    """
    Create multi-panel summary dashboard for contact analysis.

    Args:
        analysis_result: AnalysisResult object with all data
        save_path: Path to save figure

    Returns:
        matplotlib Figure
    """
    fig = plt.figure(figsize=(16, 12))
    gs = GridSpec(3, 3, figure=fig, hspace=0.3, wspace=0.3)

    # Panel 1: Preload vs Time
    ax1 = fig.add_subplot(gs[0, :2])
    ax1.plot(analysis_result.time, analysis_result.preload_history / 1000,
             linewidth=2, color=COLORS['blue'])
    ax1.set_xlabel('Time [s]')
    ax1.set_ylabel('Preload [kN]')
    ax1.set_title('Preload Evolution', fontweight='bold')
    ax1.grid(True, alpha=0.3)

    # Panel 2: Statistics Box
    ax2 = fig.add_subplot(gs[0, 2])
    ax2.axis('off')
    stats = analysis_result.statistics
    stats_text = (
        f"Analysis Results\n"
        f"{'='*30}\n"
        f"Initial Preload: {stats.get('initial_preload', 0)/1000:.1f} kN\n"
        f"Final Preload: {stats.get('final_preload', 0)/1000:.1f} kN\n"
        f"Preload Loss: {stats.get('preload_loss_percent', 0):.1f}%\n\n"
        f"Loosening Angle: {stats.get('total_loosening_angle_deg', 0):.2f}°\n\n"
        f"Max Displacement: {stats.get('max_displacement', 0)*1000:.3f} mm\n"
        f"Max Velocity: {stats.get('max_velocity', 0)*1000:.3f} mm/s\n"
    )
    ax2.text(0.1, 0.5, stats_text, transform=ax2.transAxes,
            fontsize=10, verticalalignment='center',
            fontfamily='monospace',
            bbox=dict(boxstyle='round', facecolor=COLORS['surface'],
                     alpha=0.9, edgecolor=COLORS['overlay']))

    # Panel 3: Loosening Angle
    ax3 = fig.add_subplot(gs[1, :2])
    angle_deg = np.degrees(analysis_result.loosening_angle_history)
    ax3.plot(analysis_result.time, angle_deg,
             linewidth=2, color=COLORS['mauve'])
    ax3.set_xlabel('Time [s]')
    ax3.set_ylabel('Angle [deg]')
    ax3.set_title('Loosening Angle', fontweight='bold')
    ax3.grid(True, alpha=0.3)

    # Panel 4: Displacement History (first DOF)
    ax4 = fig.add_subplot(gs[1, 2])
    if analysis_result.displacement.shape[1] > 0:
        ax4.plot(analysis_result.time,
                analysis_result.displacement[:, 0] * 1000,
                linewidth=1.5, color=COLORS['teal'])
    ax4.set_xlabel('Time [s]')
    ax4.set_ylabel('Displacement [mm]')
    ax4.set_title('DOF 1 Displacement', fontweight='bold')
    ax4.grid(True, alpha=0.3)

    # Panel 5: Preload vs Cycles (if available)
    ax5 = fig.add_subplot(gs[2, :2])
    if analysis_result.cycle_data is not None:
        cycles = np.array(analysis_result.cycle_data['cycle'])
        preload_cycles = np.array(analysis_result.cycle_data['preload'])
        ax5.plot(cycles, preload_cycles / 1000,
                linewidth=2, color=COLORS['green'], marker='o',
                markersize=3, markeredgecolor='none')
    ax5.set_xlabel('Cycle Number')
    ax5.set_ylabel('Preload [kN]')
    ax5.set_title('Preload per Cycle', fontweight='bold')
    ax5.grid(True, alpha=0.3)

    # Panel 6: Phase Space (Displacement vs Velocity)
    ax6 = fig.add_subplot(gs[2, 2])
    if analysis_result.displacement.shape[1] > 0:
        ax6.plot(analysis_result.displacement[:, 0] * 1000,
                analysis_result.velocity[:, 0] * 1000,
                linewidth=0.5, color=COLORS['pink'], alpha=0.6)
    ax6.set_xlabel('Displacement [mm]')
    ax6.set_ylabel('Velocity [mm/s]')
    ax6.set_title('Phase Space', fontweight='bold')
    ax6.grid(True, alpha=0.3)

    # Overall title
    fig.suptitle(f'Contact Analysis Summary: {analysis_result.config.name}',
                fontsize=16, fontweight='bold', y=0.98)

    if save_path:
        fig.savefig(save_path, dpi=300, facecolor=COLORS['background'])

    return fig


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def create_animation(
    time: np.ndarray,
    data: np.ndarray,
    output_path: Path,
    fps: int = 30
) -> None:
    """
    Create animation of time-varying data.

    Args:
        time: Time array
        data: Data array to animate
        output_path: Path to save animation
        fps: Frames per second
    """
    # Requires matplotlib.animation - placeholder
    print(f"Animation export not yet implemented. Would save to {output_path}")


if __name__ == "__main__":
    print("=" * 70)
    print("Contact Visualization Module - Test Suite")
    print("=" * 70)

    # Generate test data
    n_cycles = 100
    cycles = np.arange(n_cycles)
    preload = 50000 * np.exp(-0.01 * cycles)

    cycle_data = {
        'cycle': cycles,
        'preload': preload
    }

    print("\n[Test 1] Preload vs Cycles")
    fig1 = plot_preload_vs_cycles(cycle_data)
    print("  OK")

    print("\n[Test 2] Loosening Angle")
    time = np.linspace(0, 100, 1000)
    angle = 0.01 * time  # 0.01 rad/s
    fig2 = plot_loosening_angle_vs_time(time, angle)
    print("  OK")

    print("\n[Test 3] Per-Thread Wear")
    threads = np.arange(1, 9)
    wear = 1e-6 * np.exp(-0.3 * threads)  # Exponential decay
    fig3 = plot_per_thread_wear(threads, wear)
    print("  OK")

    print("\n[Test 4] Friction Evolution")
    friction = {
        'Thread': 0.12 * (1 - 0.2 * time / time[-1]),
        'Bearing Head': 0.15 * (1 - 0.15 * time / time[-1]),
        'Bearing Nut': 0.15 * (1 - 0.1 * time / time[-1]),
    }
    fig4 = plot_friction_evolution(time, friction)
    print("  OK")

    plt.show()

    print("\n" + "=" * 70)
    print("All visualization tests complete!")
    print("=" * 70)
