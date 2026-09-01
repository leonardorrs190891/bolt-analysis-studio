"""
Regression Test for Task #13: Independent Joint Analysis
==========================================================

This test verifies that different joint configurations produce
independent preload decay curves, confirming the fix for the bug
where multiple joints showed identical decay behavior.

Author: Bolt Analysis Studio Team
Date: February 2026
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import numpy as np
from bolt_analysis_studio.numerical.coupled_loosening_analyzer import (
    CoupledLooseningAnalyzer,
    ThreadGeometryParams,
    BearingGeometryParams,
    FrictionEvolutionParams,
    WearModelParams,
    TwoStageLooseningParams
)


def test_independent_joint_analyses():
    """
    Test that two different joint configurations produce different results.

    Creates two analyzers with different preload and stiffness values,
    runs analyses, and verifies that the preload decay curves are different.
    """
    print("=" * 70)
    print("REGRESSION TEST: Independent Joint Analysis")
    print("=" * 70)
    print()

    # Configuration 1: High preload, stiff joint
    print("Creating Joint Configuration 1:")
    print("  - Preload: 50,000 N")
    print("  - k_bolt: 500e6 N/m")
    print("  - k_member: 1500e6 N/m")
    print("  - Transverse force: 5,000 N")
    print()

    analyzer1 = CoupledLooseningAnalyzer(
        thread_geometry=ThreadGeometryParams(
            pitch=2.0e-3,
            pitch_diameter=14.7e-3,
            major_diameter=16.0e-3
        ),
        bearing_geometry=BearingGeometryParams(
            inner_diameter=17.0e-3,
            outer_diameter=24.0e-3
        ),
        friction_params=FrictionEvolutionParams(
            mu_initial=0.15,
            mu_peak=0.18,
            mu_steady=0.10
        ),
        wear_params=WearModelParams(
            K_archard=1e-6
        ),
        k_bolt=500e6,
        k_member=1500e6,
        transverse_displacement_mm=0.65
    )

    # Configuration 2: Lower preload, more compliant joint
    print("Creating Joint Configuration 2:")
    print("  - Preload: 30,000 N")
    print("  - k_bolt: 300e6 N/m")
    print("  - k_member: 900e6 N/m")
    print("  - Transverse force: 8,000 N")
    print()

    analyzer2 = CoupledLooseningAnalyzer(
        thread_geometry=ThreadGeometryParams(
            pitch=2.0e-3,
            pitch_diameter=14.7e-3,
            major_diameter=16.0e-3
        ),
        bearing_geometry=BearingGeometryParams(
            inner_diameter=17.0e-3,
            outer_diameter=24.0e-3
        ),
        friction_params=FrictionEvolutionParams(
            mu_initial=0.12,
            mu_peak=0.15,
            mu_steady=0.08
        ),
        wear_params=WearModelParams(
            K_archard=1.5e-6  # More wear
        ),
        k_bolt=300e6,
        k_member=900e6,
        transverse_displacement_mm=0.80  # Larger displacement
    )

    # Run analyses
    print("Running Analysis 1...")
    results1 = analyzer1.run_analysis(
        preload_initial=50000,
        F_transverse=5000,
        n_cycles=1000,
        output_interval=10
    )
    print(f"  [OK] Completed. Final preload: {results1.preload[-1]:.1f} N "
          f"({results1.preload_ratio[-1]*100:.1f}%)")
    print()

    print("Running Analysis 2...")
    results2 = analyzer2.run_analysis(
        preload_initial=30000,
        F_transverse=8000,
        n_cycles=1000,
        output_interval=10
    )
    print(f"  [OK] Completed. Final preload: {results2.preload[-1]:.1f} N "
          f"({results2.preload_ratio[-1]*100:.1f}%)")
    print()

    # Verify independence
    print("-" * 70)
    print("VERIFICATION:")
    print("-" * 70)

    # Check that preload curves are different
    # We compare the final preload ratios - they should be significantly different
    ratio1_final = results1.preload_ratio[-1]
    ratio2_final = results2.preload_ratio[-1]

    print(f"Joint 1 final preload ratio: {ratio1_final:.4f}")
    print(f"Joint 2 final preload ratio: {ratio2_final:.4f}")
    print(f"Difference: {abs(ratio1_final - ratio2_final):.4f}")
    print()

    # Check that the curves are different at multiple points
    differences = []
    for i in range(min(len(results1.preload_ratio), len(results2.preload_ratio))):
        diff = abs(results1.preload_ratio[i] - results2.preload_ratio[i])
        differences.append(diff)

    mean_difference = np.mean(differences)
    max_difference = np.max(differences)

    print(f"Mean difference across all cycles: {mean_difference:.4f}")
    print(f"Maximum difference: {max_difference:.4f}")
    print()

    # Test assertions
    tests_passed = True

    # Test 1: Final ratios should be different (tolerance 5%)
    if abs(ratio1_final - ratio2_final) < 0.05:
        print("[FAIL] Final preload ratios are too similar!")
        print("       This indicates the bug is still present.")
        tests_passed = False
    else:
        print("[PASS] Final preload ratios are different")

    # Test 2: Mean difference should be significant (>2%)
    if mean_difference < 0.02:
        print("[FAIL] Preload curves are too similar!")
        print("       This indicates state leakage between analyses.")
        tests_passed = False
    else:
        print("[PASS] Preload curves show significant differences")

    # Test 3: Verify wear accumulation is independent
    wear1_final = results1.total_wear_um[-1]
    wear2_final = results2.total_wear_um[-1]
    print()
    print(f"Joint 1 final wear: {wear1_final:.2f} um")
    print(f"Joint 2 final wear: {wear2_final:.2f} um")

    if wear2_final <= wear1_final:
        print("[FAIL] Joint 2 should have more wear (higher K, more aggressive loading)")
        tests_passed = False
    else:
        print("[PASS] Wear accumulation is independent")

    # Test 4: Run analyzer1 again to check it doesn't retain state from first run
    print()
    print("-" * 70)
    print("ADDITIONAL TEST: State Reset Between Runs")
    print("-" * 70)
    print("Running Analysis 1 again with same parameters...")

    results1_repeat = analyzer1.run_analysis(
        preload_initial=50000,
        F_transverse=5000,
        n_cycles=1000,
        output_interval=10
    )
    print(f"  [OK] Completed. Final preload: {results1_repeat.preload[-1]:.1f} N "
          f"({results1_repeat.preload_ratio[-1]*100:.1f}%)")
    print()

    # Should match first run exactly
    repeat_difference = abs(results1.preload_ratio[-1] - results1_repeat.preload_ratio[-1])
    print(f"Difference from first run: {repeat_difference:.6f}")

    if repeat_difference > 0.001:  # Should be identical
        print("[FAIL] Repeated analysis gives different results!")
        print("       Analyzer retains state between runs.")
        tests_passed = False
    else:
        print("[PASS] Repeated analysis is consistent")

    # Final verdict
    print()
    print("=" * 70)
    if tests_passed:
        print("[SUCCESS] ALL TESTS PASSED")
        print()
        print("Task #13 FIX VERIFIED:")
        print("  - Different joints produce different decay curves")
        print("  - No state leakage between analyses")
        print("  - Analyzer state resets properly between runs")
    else:
        print("[FAILURE] TESTS FAILED")
        print()
        print("The bug persists. Further investigation needed.")
    print("=" * 70)

    return tests_passed


if __name__ == "__main__":
    try:
        success = test_independent_joint_analyses()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n[ERROR] TEST ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
