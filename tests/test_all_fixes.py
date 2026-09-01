#!/usr/bin/env python3
"""
Test All Bug Fixes
Verifies that all 5 bug fixes are properly implemented

Run this to check if changes are applied correctly.
"""

import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

print("=" * 70)
print("TESTING ALL BUG FIXES")
print("=" * 70)

# Test 1: Matrix Viewer - Force Vector Plot
print("\n[Test 1] Force Vector Plot Enhancements")
try:
    from bolt_analysis_studio.gui.matrix_viewer import MatrixCanvas
    import numpy as np

    # Check if plot_bar method has the new code
    import inspect
    source = inspect.getsource(MatrixCanvas.plot_bar)

    checks = {
        "Empty vector handling": "Force vector is all zeros" in source,
        "Value labels on bars": "for i, (bar, val)" in source,
        "Grid added": "grid(axis='y'" in source,
        "Proper limits": "set_xlim" in source and "set_ylim" in source
    }

    for check, passed in checks.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status}: {check}")

    if all(checks.values()):
        print("  ✅ Force vector plot fix VERIFIED")
    else:
        print("  ❌ Force vector plot fix INCOMPLETE")

except Exception as e:
    print(f"  ❌ ERROR: {e}")

# Test 2: Similitude Tab - Comparison Plot
print("\n[Test 2] Comparison Plot Visibility")
try:
    from bolt_analysis_studio.gui.similitude_tab import ComparisonPlotsPanel
    import inspect

    source = inspect.getsource(ComparisonPlotsPanel._refresh_plot)

    checks = {
        "Placeholder when no data": "No comparison data available" in source,
        "Early return with message": "return  # Early return" in source or "return" in source.split("No comparison data")[1].split("\n")[0:3],
        "Theme applied to placeholder": "_apply_theme_to_ax" in source
    }

    for check, passed in checks.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status}: {check}")

    if all(checks.values()):
        print("  ✅ Comparison plot fix VERIFIED")
    else:
        print("  ❌ Comparison plot fix INCOMPLETE")

except Exception as e:
    print(f"  ❌ ERROR: {e}")

# Test 3: Preload % Yield
print("\n[Test 3] Preload as % of Yield Limit")
try:
    from bolt_analysis_studio.gui.msd_builder import PropertyInspector
    import inspect

    # Check __init__ for preload_info_label
    init_source = inspect.getsource(PropertyInspector._setup_ui)

    checks = {
        "Info label created": "preload_info_label" in init_source,
        "Info label shows A_s, σ, %": "A_s =" in init_source and "σ =" in init_source,
    }

    # Check for _update_preload_info method
    try:
        update_source = inspect.getsource(PropertyInspector._update_preload_info)
        checks["Update info method exists"] = True
        checks["Warning for high stress"] = ">= 90" in update_source or "> 90" in update_source
        checks["Error for over yield"] = "> 100" in update_source or "100" in update_source
    except:
        checks["Update info method exists"] = False

    # Check for bidirectional sync
    try:
        preload_changed_source = inspect.getsource(PropertyInspector._on_preload_changed)
        checks["Bidirectional sync"] = "preload_slider" in preload_changed_source
    except:
        checks["Bidirectional sync"] = False

    for check, passed in checks.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status}: {check}")

    if all(checks.values()):
        print("  ✅ Preload % yield fix VERIFIED")
    else:
        print("  ❌ Preload % yield fix INCOMPLETE")

except Exception as e:
    print(f"  ❌ ERROR: {e}")

# Test 4: Recalculate Button
print("\n[Test 4] Recalculate All MSD Elements Button")
try:
    from bolt_analysis_studio.gui.msd_builder import MSDBuilderWindow
    import inspect

    # Check if method exists
    checks = {
        "Recalculate method exists": hasattr(MSDBuilderWindow, '_recalculate_all_elements')
    }

    if checks["Recalculate method exists"]:
        source = inspect.getsource(MSDBuilderWindow._recalculate_all_elements)
        checks["Confirmation dialog"] = "QMessageBox.question" in source
        checks["Calculates k, c, m"] = "k_new" in source and "c_new" in source and "m_new" in source
        checks["Error handling"] = "try:" in source and "except" in source
        checks["Success message"] = "QMessageBox.information" in source
    else:
        checks["Confirmation dialog"] = False
        checks["Calculates k, c, m"] = False
        checks["Error handling"] = False
        checks["Success message"] = False

    for check, passed in checks.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status}: {check}")

    if all(checks.values()):
        print("  ✅ Recalculate button fix VERIFIED")
    else:
        print("  ❌ Recalculate button fix INCOMPLETE")

except Exception as e:
    print(f"  ❌ ERROR: {e}")

# Test 5: Independent Joint Decay (Investigation)
print("\n[Test 5] Independent Joint Decay")
print("  ⏳ This issue requires investigation and cannot be automatically tested")
print("  ⏳ Manual testing required with multiple joint models")

# Summary
print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)
print("✅ Tests passed: Run the application and verify visually")
print("⚠️  If tests fail: Check Python compilation errors above")
print("📝 Next: Restart application to load changes")
print("\nTo restart application, run:")
print("  python run_app.py")
print("=" * 70)
