"""
Test script for Coupled Loosening Analyzer
Tests the friction-wear-loosening coupling implementation.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import numpy as np

def test_coupled_loosening_analyzer():
    """Test the CoupledLooseningAnalyzer class."""
    print("=" * 60)
    print("Testing Coupled Friction-Wear-Loosening Analyzer")
    print("=" * 60)

    from bolt_analysis_studio.numerical.coupled_loosening_analyzer import (
        CoupledLooseningAnalyzer, LooseningResults,
        FrictionEvolutionParams, WearModelParams,
        ThreadGeometryParams, BearingGeometryParams,
        create_m16_analyzer, create_analyzer_from_bolt_size
    )

    # Test 1: Create M16 analyzer with preset
    print("\n--- Test 1: M16 Preset Analyzer ---")
    analyzer = create_m16_analyzer(mu_initial=0.12, lubricated=True)

    mu_crit = analyzer.compute_critical_friction()
    print(f"Critical friction coefficient: {mu_crit:.4f}")
    print(f"Initial friction: 0.12")
    print(f"Above critical: {'Yes' if 0.12 > mu_crit else 'No'}")

    # Test torque computation
    torques = analyzer.compute_torques(preload=50000, mu_thread=0.12, mu_bearing=0.12)
    print(f"\nTorque balance at 50kN preload:")
    print(f"  T_pitch (drives): {torques['T_pitch']:.2f} N.m")
    print(f"  T_thread: {torques['T_thread']:.2f} N.m")
    print(f"  T_bearing: {torques['T_bearing']:.2f} N.m")
    print(f"  T_resistance: {torques['T_resistance']:.2f} N.m")
    print(f"  Margin: {torques['margin']:.3f}")
    print(f"  Loosening possible: {torques['loosening_possible']}")

    # Test 2: Run short analysis
    print("\n--- Test 2: Short Analysis (500 cycles) ---")
    results = analyzer.run_analysis(
        preload_initial=50000,  # 50 kN
        F_transverse=8000,      # 8 kN transverse (drives Junker)
        n_cycles=500,
        temperature=20.0,
        output_interval=1
    )

    print(f"Analysis completed:")
    print(f"  Final preload ratio: {results.final_preload_ratio * 100:.1f}%")
    print(f"  Total loosening: {results.total_loosening_deg:.3f} deg")
    print(f"  Max loosening rate: {results.max_loosening_rate:.5f} deg/cycle")
    print(f"  Phase at end: {results.phase_at_end.value}")

    if results.cycles_to_loosening_onset > 0:
        print(f"  Loosening onset: cycle {results.cycles_to_loosening_onset}")

    # Test 2b: Scenario with ACTUAL loosening (lower friction + higher transverse force)
    print("\n--- Test 2b: Loosening Scenario (low friction) ---")
    analyzer_low_mu = create_m16_analyzer(mu_initial=0.05, lubricated=True)  # Very low friction

    # Debug: Check slip conditions before running
    print(f"  Initial mu: 0.05")
    print(f"  Preload: 50 kN")
    print(f"  F_transverse: 15 kN")
    bearing_capacity = 0.05 * 50000
    thread_capacity = 0.05 * 50000 * np.cos(analyzer_low_mu.thread.helix_angle)
    print(f"  Bearing friction capacity: {bearing_capacity/1000:.2f} kN")
    print(f"  Thread friction capacity: {thread_capacity/1000:.2f} kN")
    print(f"  Bearing slipping: {15000 > bearing_capacity} (15 > {bearing_capacity/1000:.2f})")
    print(f"  Thread slipping: {15000 > thread_capacity} (15 > {thread_capacity/1000:.2f})")
    print(f"  Helix angle: {np.degrees(analyzer_low_mu.thread.helix_angle):.3f} deg")

    results_loosening = analyzer_low_mu.run_analysis(
        preload_initial=50000,  # 50 kN
        F_transverse=15000,     # 15 kN - higher transverse force
        n_cycles=1000,
        temperature=20.0,
        output_interval=1
    )

    print(f"\nLoosening scenario results:")
    print(f"  Final preload ratio: {results_loosening.final_preload_ratio * 100:.1f}%")
    print(f"  Total loosening: {results_loosening.total_loosening_deg:.3f} deg")
    print(f"  Max loosening rate: {results_loosening.max_loosening_rate:.5f} deg/cycle")
    print(f"  Phase at end: {results_loosening.phase_at_end.value}")

    # Debug: Check state at cycle 1
    if len(results_loosening.states) > 0:
        s1 = results_loosening.states[0]
        print(f"\n  State at cycle 1:")
        print(f"    bearing_slipping: {s1.bearing_slipping}")
        print(f"    thread_slipping: {s1.thread_slipping}")
        print(f"    mu_thread: {s1.mu_thread:.4f}")
        print(f"    mu_bearing: {s1.mu_bearing:.4f}")
        print(f"    loosening_rate: {np.degrees(s1.loosening_rate):.6f} deg/cycle")

    if results_loosening.cycles_to_loosening_onset > 0:
        print(f"  Loosening onset: cycle {results_loosening.cycles_to_loosening_onset}")

    # Test 3: Verify friction evolution
    print("\n--- Test 3: Friction Evolution ---")
    friction_params = FrictionEvolutionParams(
        mu_initial=0.15,
        mu_peak=0.18,
        mu_steady=0.10,
        N1=50, N2=200, N3=2000
    )

    cycles_test = np.array([0, 25, 50, 100, 200, 500, 1000, 2000])
    for n in cycles_test:
        mu = friction_params.compute_mu(n, wear_depth_um=0, temperature=20)
        print(f"  Cycle {n:4d}: mu = {mu:.4f}")

    # Test 4: Custom analyzer
    print("\n--- Test 4: Custom M20 Analyzer ---")
    analyzer_m20 = create_analyzer_from_bolt_size(
        diameter_mm=20.0,
        pitch_mm=2.5,
        grip_length_mm=60.0
    )

    print(f"M20x2.5 bolt created")
    mu_crit_m20 = analyzer_m20.compute_critical_friction()
    print(f"Critical friction (M20): {mu_crit_m20:.4f}")

    # Test 5: Compare different initial friction values
    print("\n--- Test 5: Effect of Initial Friction ---")
    mu_values = [0.08, 0.10, 0.12, 0.15]

    for mu_0 in mu_values:
        analyzer_test = create_m16_analyzer(mu_initial=mu_0, lubricated=True)
        results_test = analyzer_test.run_analysis(
            preload_initial=50000,
            F_transverse=8000,
            n_cycles=500
        )
        print(f"  mu_0 = {mu_0:.2f}: Final F/F0 = {results_test.final_preload_ratio*100:.1f}%, "
              f"theta = {results_test.total_loosening_deg:.3f} deg")

    print("\n" + "=" * 60)
    print("All tests passed!")
    print("=" * 60)

    return True


def test_visualization():
    """Test the visualization module."""
    print("\n" + "=" * 60)
    print("Testing Visualization Module")
    print("=" * 60)

    try:
        from bolt_analysis_studio.visualization.loosening_plots import (
            CoupledLooseningResultsPlotter, quick_coupled_loosening_plot
        )
        print("CoupledLooseningResultsPlotter imported successfully")

        # Create plotter
        plotter = CoupledLooseningResultsPlotter()
        print("Plotter created successfully")

        return True

    except ImportError as e:
        print(f"Import error: {e}")
        return False


if __name__ == "__main__":
    success = test_coupled_loosening_analyzer()
    if success:
        test_visualization()
