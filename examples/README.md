# Complete Analysis Workflow Examples

This directory contains complete, working examples demonstrating the end-to-end analysis workflow in Bolt Analysis Studio v4.0.

## Overview

The analysis workflow system provides:

1. **Joint Configuration** - Define bolt, gasket, washer, and flange properties
2. **Loading Protocol** - Specify loading type (Junker test, operational, thermal)
3. **Contact System** - Automatic creation of all contacts with tribology
4. **Time Integration** - Solve equations of motion with contact updates
5. **Preload Tracking** - Monitor preload loss from all mechanisms
6. **Visualization** - Generate publication-quality plots
7. **Data Export** - Save results to CSV and JSON

## Quick Start

### Run Example 1 (M20 Junker Test)

```bash
python examples/complete_analysis_example.py --example 1
```

### Run All Examples

```bash
python examples/complete_analysis_example.py --all
```

## Examples

### Example 1: M20 Junker Test (API 6A)

Standard transverse vibration test per DIN 65151 on M20 bolt with RTJ gasket.

**Configuration:**
- Bolt: M20 (pitch 2.5mm, 10 engaged threads)
- Joint: API 6A 5K pressure rating
- Gasket: Ring Type Joint (RTJ)
- Loading: Junker test (0.65mm amplitude, 12.5 Hz, 2000 cycles)
- Initial Preload: 50 kN

**Outputs:**
- Preload vs cycles curve
- Loosening angle evolution
- Contact force histories
- Wear distributions
- Phase identification (I, II, III)

**Run time:** ~5-10 minutes (2000 cycles)

---

### Example 2: ASME B16.5 Flange (Operational)

ASME B16.5 Class 300 flanged joint under static operational loading.

**Configuration:**
- Bolt: M20
- Joint: ASME B16.5 Class 300
- Gasket: Spiral wound (316SS + graphite)
- Loading: Static 10 kN operational load
- Initial Preload: 60 kN

**Outputs:**
- Preload relaxation curve
- Gasket compression vs time
- Friction evolution
- Flange separation monitoring

**Run time:** ~1-2 minutes

---

### Example 3: VDI 2230 Joint (Thermal Cycling)

VDI 2230 joint with Belleville washers under thermal cycling.

**Configuration:**
- Bolt: M20
- Joint: VDI 2230 standard
- Washers: Belleville (preload compensation)
- Loading: Thermal cycling (-40°C to 150°C, 10 cycles)
- Initial Preload: 55 kN

**Outputs:**
- Preload vs temperature
- Thermal expansion effects
- Belleville washer response
- Preload loss mechanisms

**Run time:** ~2-3 minutes

---

### Example 4: Comparative Study

Compares three joint configurations under identical Junker test conditions.

**Configurations Compared:**
1. API 6A with RTJ gasket
2. ASME B16.5 with spiral wound gasket
3. VDI 2230 with Belleville washers

**Outputs:**
- Comparative preload curves
- Loss mechanism breakdown
- Performance ranking
- Design recommendations

**Run time:** ~10-15 minutes

---

## File Structure

```
examples/
├── README.md                          # This file
├── complete_analysis_example.py       # Main examples script
└── results/                           # Generated results (created on run)
    ├── example_1_m20_junker/
    │   ├── preload_cycles.png
    │   ├── loosening_angle.png
    │   ├── summary_dashboard.png
    │   ├── time_history.csv
    │   ├── cycle_data.csv
    │   └── analysis_summary.json
    ├── example_2_asme_operational/
    ├── example_3_vdi_thermal/
    └── example_4_comparative/
```

## Workflow Architecture

### 1. Analysis Configuration

```python
from bolt_analysis_studio.core.workflow import (
    AnalysisManager, AnalysisConfiguration, LoadingProtocol
)

# Define joint
joint_config = create_api_6a_joint_config(bolt_size="M20")

# Define loading
loading = LoadingProtocol(
    protocol_type=LoadingProtocolType.JUNKER_TEST,
    junker_n_cycles=2000
)

# Create config
config = AnalysisConfiguration(
    name="My Analysis",
    joint_config=joint_config,
    loading=loading,
    initial_preload=50000.0
)
```

### 2. Run Analysis

```python
# Create manager
manager = AnalysisManager(config)

# Setup (creates contacts, assembles matrices)
manager.setup_model()

# Run (time integration with contact updates)
result = manager.run_analysis()
```

### 3. Post-Process

```python
# Generate plots
manager.post_process()

# Export data
manager.export_results()

# Access results
print(f"Final preload: {result.get_final_preload():.0f} N")
print(f"Loosening angle: {result.get_total_loosening_angle():.2f}°")
```

## Contact System

Each joint automatically creates:

1. **Thread Contact** - Helix geometry, friction, wear
2. **Bearing Contacts** - Head and nut bearing surfaces
3. **Washer Contacts** - Plain, Belleville, or Nord-Lock
4. **Gasket Contact** - Spiral wound, RTJ, or flange-flange
5. **Flange Contacts** - Metal-to-metal or with gasket

All contacts contribute to:
- **[M], [K], [C]** matrices (14-DOF system)
- **{F}** force vector (friction, wear effects)
- **Preload loss** (embedding, wear, rotation)

## Loading Protocols

### Junker Test (DIN 65151)

```python
loading = LoadingProtocol(
    protocol_type=LoadingProtocolType.JUNKER_TEST,
    junker_amplitude=0.00065,  # 0.65mm
    junker_frequency=12.5,     # 12.5 Hz
    junker_n_cycles=2000
)
```

### Operational Loads

```python
loading = LoadingProtocol(
    protocol_type=LoadingProtocolType.OPERATIONAL,
    operational_load_func=my_force_function  # F(t)
)
```

### Thermal Cycling

```python
loading = LoadingProtocol(
    protocol_type=LoadingProtocolType.THERMAL,
    temperature_min=-40.0,
    temperature_max=150.0,
    thermal_n_cycles=100
)
```

## Solver Configuration

### Time Integration Methods

- **Newmark-β** (default) - Unconditionally stable, implicit
- **HHT-α** - Enhanced damping for stiff contacts
- **Central Difference** - Explicit (for high-frequency response)

```python
from bolt_analysis_studio.numerical.time_integration import IntegratorType

config = AnalysisConfiguration(
    solver_method=IntegratorType.HHT_ALPHA,
    time_step=0.0001,  # 0.1ms
    # ...
)
```

## Visualization Outputs

### Standard Plots

1. **Preload vs Cycles** - Shows loss over loading cycles
2. **Loosening Angle vs Time** - Cumulative rotation
3. **Per-Thread Wear** - Wear distribution across threads
4. **Per-Thread Load** - Load fraction per thread
5. **Friction Evolution** - μ(t) for all contacts
6. **Contact Forces** - Force time histories
7. **Gasket Compression** - Compression vs time
8. **Summary Dashboard** - Multi-panel overview

All plots use Catppuccin Mocha color scheme (dark mode).

## Results Data

### CSV Exports

**time_history.csv:**
```
time,preload,loosening_angle
0.0,50000.0,0.0
0.0001,49995.2,0.00001
...
```

**cycle_data.csv:**
```
cycle,preload,angle_deg,time
1,49800.0,0.12,0.08
2,49200.0,0.28,0.16
...
```

### JSON Summary

**analysis_summary.json:**
```json
{
  "name": "M20 Junker Test",
  "timestamp": "2026-01-27T...",
  "runtime_seconds": 245.3,
  "statistics": {
    "initial_preload": 50000.0,
    "final_preload": 15230.5,
    "preload_loss_percent": 69.5,
    "total_loosening_angle_deg": 42.3,
    ...
  }
}
```

## Performance

Typical analysis times (Intel Core i7, 16GB RAM):

- **100 cycles** (Junker): ~30 seconds
- **500 cycles**: ~2 minutes
- **2000 cycles** (full test): ~8 minutes
- **Operational (1 hour)**: ~1 minute
- **Thermal (10 cycles)**: ~2 minutes

Time step `dt=0.0001` s (0.1ms) is recommended for Junker test.

## Advanced Usage

### Custom Force Functions

```python
def my_force_function(t: float) -> np.ndarray:
    """Custom time-varying force."""
    F = np.zeros(14)  # 14-DOF system
    F[0] = 10000 * np.sin(2 * np.pi * 5.0 * t)  # 5 Hz axial
    F[10] = 5000 * np.cos(2 * np.pi * 10.0 * t)  # 10 Hz transverse
    return F

loading = LoadingProtocol(
    protocol_type=LoadingProtocolType.CUSTOM,
    custom_force_func=my_force_function
)
```

### Progress Monitoring

```python
def progress_callback(percent: float):
    print(f"Progress: {percent:.0f}%")

result = manager.run_analysis(progress_callback=progress_callback)
```

### Accessing Contact Data

```python
# After analysis
for contact in manager.contacts:
    print(f"{contact.id}:")
    print(f"  Type: {contact.type}")
    print(f"  Friction: {contact.friction.mu_current:.3f}")
    print(f"  Wear depth: {contact.wear.wear_depth*1e6:.2f} μm")
    print(f"  Slip state: {contact.slip_state.value}")
```

## References

- **DIN 65151** - Junker vibration test for threaded fasteners
- **VDI 2230 Part 1** (2015) - Systematic calculation of bolted joints
- **API 6A** - Wellhead and Christmas tree equipment
- **ASME B16.5** - Pipe flanges and flanged fittings

## Support

For issues or questions:
- See main CLAUDE.md for project structure
- Check documentation in src/bolt_analysis_studio/
- Contact: internal reference - Petrobras R&D

---

**Bolt Analysis Studio v4.0**
internal reference + Petrobras R&D
January 2026
