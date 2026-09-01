# Bolt Analysis Studio v4.0

**Prof. Leonardo Rosa Ribeiro da Silva, PhD | January 2026**

A comprehensive engineering software system for analyzing bolted flange joints in oil and gas applications, featuring Mass-Spring-Damper (MSD) modeling, preload loss prediction, and dynamic analysis.

## 🎯 Features

### Part 1: Analysis Engine
- **Preload Loss Models**: Double exponential, power law, Jiang two-stage, logarithmic decay
- **Friction Models**: Coulomb, LuGre, Dahl, Iwan, Hintikka evolution
- **Wear Models**: Archard adhesive/abrasive, energy-based, fretting, fatigue wear
- **Visualization**: 9 comprehensive plots for loosening analysis

### Part 2: MSD Model Builder with Contact System
- **3-Layer Architecture**: Components → Contacts → Tribology hierarchy
- **Component Elements**: Bolt head, stud, nut, washers, flanges, gasket (mechanical properties only)
- **Contact Elements**: Thread (parallel array), bearing surfaces, interfaces (mechanical + tribology)
- **Thread Contact Models**: 5 load distribution laws (Equal, Linear, Power, Exponential, Yamamoto)
- **Surface Contacts**: Bearing, washer-flange, flange-gasket, flange-flange, specialized interfaces
- **Tribology Layer**: Friction, wear, lubrication, coating models attached to contacts only
- **Matrix Assembly**: [M], [K], [C] matrices with contact contributions and helix coupling
- **Material Database**: ASTM A193/A320, ISO 898, NACE MR0175 compliant with tribological data
- **Thread Database**: ISO metric, UNC/UNF, API 6A specifications with geometry parameters

### Part 3: Contact Modeling & Tribology
- **Friction Models**:
  - Coulomb: Static/kinetic with stick-slip transitions
  - Stribeck: Velocity-dependent with boundary/mixed/hydrodynamic regimes
  - Rate-Dependent: Rate-and-state friction for dynamic behavior
  - Elasto-Plastic: Pre-sliding stiffness with hysteresis
  - LuGre: Dynamic bristle model for detailed stick-slip
- **Wear Models**:
  - Archard: V = K×F×s/H for adhesive/abrasive wear
  - Energy-Based: Wear proportional to dissipated energy
  - Fretting: High-cycle micro-slip damage
  - Fatigue: Cyclic loading accumulation
- **Time Evolution**: Friction degradation, coating wear, running-in effects
- **Preload Loss Tracking**:
  - Rotational loosening (requires slip at thread AND bearing)
  - Embedding (VDI 2230 model)
  - Wear depth accumulation
  - Gasket creep and relaxation
  - Stress relaxation

### Part 4: Similitude Analysis
- **Buckingham Π Theorem**: 8 dimensionless groups for bolted joints
- **Scaling Laws**: Froude, Reynolds, Cauchy, custom scaling
- **7 Visualization Plots**: Scaling relationships, radar charts, dashboards

### Part 5: Numerical Solvers
- **Time Integration**: Newmark-β, HHT-α, Central Difference, RK4
- **Contact State Evolution**: Friction, wear, preload updates during simulation
- **Helix Coupling**: Axial-torsional DOF coupling in thread contacts
- **Modal Analysis**: Natural frequencies, mode shapes
- **State Space**: (A, B, C, D) matrices for control analysis

### Part 6: GUI Application
- **6-Tab Interface**: Project, Model Builder, Solver, Results, Similitude, Reports
- **MSD Builder Window**: Visual schematic editor with drag-drop elements
- **Contact Builder**: Define contact types, tribology properties, load distribution
- **Property Inspector**: Integrated material/tribology/environment settings
- **Matrix Viewer**: Visualize [M], [K], [C] assembly with contact contributions
- **Dark Theme**: Catppuccin Mocha color scheme

## 📁 Project Structure

```
bolt_analysis_studio/
├── src/bolt_analysis_studio/
│   ├── core/
│   │   ├── models/
│   │   │   ├── element.py      # MSD element data classes (1225 lines)
│   │   │   └── model.py        # MSD model with matrix assembly (989 lines)
│   │   ├── databases/
│   │   │   ├── materials.json  # ASTM/ISO material properties (545 lines)
│   │   │   └── threads.json    # Thread dimensions database (830 lines)
│   │   └── similitude/
│   │       ├── similitude.py   # Scaling analysis (1373 lines)
│   │       └── similitude_plots.py  # Similitude visualization (816 lines)
│   ├── numerical/
│   │   ├── preload_loss_models.py   # Loosening models (1365 lines)
│   │   ├── friction_models.py       # Tribological models (843 lines)
│   │   └── time_integration.py      # Solvers (1415 lines)
│   ├── visualization/
│   │   └── loosening_plots.py       # Analysis plots (907 lines)
│   └── gui/
│       ├── main_window.py      # Main 6-tab application (1534 lines)
│       └── msd_builder.py      # Visual schematic editor (1247 lines)
├── output_plots/               # Generated visualization plots
├── run_app.py                  # Application launcher
├── test_gui.py                 # GUI test suite
└── test_analysis_engine.py     # Analysis engine tests
```

**Total: 11,866 lines of Python + 1,375 lines of JSON**

## 🚀 Quick Start

### Installation

```bash
# Clone or copy the project
cd bolt_analysis_studio

# Install dependencies
pip install PyQt6 numpy scipy matplotlib

# Run tests
python test_gui.py

# Launch application
python run_app.py
```

### Command Line Options

```bash
python run_app.py              # Launch full application
python run_app.py --builder    # Launch MSD Builder only
python run_app.py --test       # Run test suite
python run_app.py --version    # Show version
```

## 🏗️ Model Architecture

The bolted joint is represented as a 3-layer hierarchical system:

```
┌──────────────────────────────────────────────────────────┐
│              BOLTED JOINT MSD SYSTEM                      │
├──────────────────────────────────────────────────────────┤
│                                                           │
│  External Loads → [Axial] [Transverse] [Thermal]         │
│                         ↓                                 │
│  ┌─────────────────────────────────────────────────┐     │
│  │  LAYER 1: Component MSD Elements                │     │
│  │  (Bolt, Nut, Washers, Flanges, Gasket)          │     │
│  │  Properties: m, k, c (mechanical only)           │     │
│  └──────────────────┬──────────────────────────────┘     │
│                     ↓                                     │
│  ┌─────────────────────────────────────────────────┐     │
│  │  LAYER 2: Contact MSD Elements                  │     │
│  │  (Thread, Bearing, Interfaces)                  │     │
│  │  Properties: k_contact, c_contact               │     │
│  └──────────────────┬──────────────────────────────┘     │
│                     ↓                                     │
│  ┌─────────────────────────────────────────────────┐     │
│  │  LAYER 3: Tribology Layer                       │     │
│  │  (Friction, Wear, Lubrication, Coating)         │     │
│  │  Attached to contacts only                      │     │
│  └─────────────────────────────────────────────────┘     │
│                                                           │
└──────────────────────────────────────────────────────────┘
```

### Key Principle
**Components have NO tribological properties.** All friction, wear, lubrication, and coating effects are modeled exclusively at contact interfaces in Layer 3.

### Matrix Assembly

Each contact contributes to global matrices:

**[K] Stiffness Matrix:**
- Component stiffnesses (diagonal/tridiagonal for series/parallel)
- Contact stiffnesses at interface DOFs
- **Thread helix coupling**: Off-diagonal k×(p/2π) terms
- Nonlinear gasket tangent stiffness k(δ)

**[C] Damping Matrix:**
- Material damping: c = 2ζ√(km)
- Contact viscous damping
- Gasket viscoelastic damping (higher)

**{F} Force Vector:**
- External loads (axial, transverse, thermal)
- Coulomb friction forces (from contacts)
- Thread helix torque (causes loosening)
- Bearing friction torque (resists loosening)
- Gasket plastic/creep forces

## 📊 Standards Compliance

- **VDI 2230** Part 1 (2015) - Systematic bolt calculation, embedding model
- **ASTM A193/A193M** - High temperature bolting
- **ASTM A320/A320M** - Low temperature bolting
- **ISO 898-1:2013** - Property classes, mechanical properties
- **API 6A** (2018) - Flanged connections, load ratings
- **NACE MR0175** - Sour service compliance, material selection
- **ASME B16.20** - Gasket factors and seating stresses
- **EN 13555** - Gasket tightness classes

## 🔧 Component Element Types (Layer 1)

Component elements have only mechanical properties (mass, stiffness, damping):

| Type | Symbol | Description | Default k (N/m) |
|------|--------|-------------|-----------------|
| HEAD | 🔩 | Hex bolt head (ISO 4014) | 1.85e9 |
| SHANK | │ | Unthreaded shank | 2.32e9 |
| THREAD | ≋ | Thread engagement | 6.6e7 |
| NUT | ⬡ | Hex nut (ISO 4032) | 1.5e9 |
| WASHER | ○ | Plain washer (ISO 7089) | 5e9 |
| FLANGE | █ | Clamped member | 1.58e9 |
| GASKET | ≡ | Seal element (nonlinear k) | 5e8 |
| GROUND | ⏚ | Fixed boundary | 1e15 |

## 🔗 Contact Types (Layer 2)

Contact elements connect components and include tribological properties:

| Contact Type | Location | Key Features | Matrix Contribution |
|--------------|----------|--------------|---------------------|
| **THREAD** | Stud-Nut | n parallel MSDs, helix coupling, load distribution | K: off-diagonal coupling, F: loosening torque |
| **BEARING_HEAD** | Head-Washer/Flange | Rotational friction resistance | F: resisting torque T_bearing |
| **BEARING_NUT** | Nut-Washer/Flange | Rotational friction resistance | F: resisting torque T_bearing |
| **WASHER_FLANGE** | Washer-Flange | Load spreading, embedding | K: contact stiffness, F: embedding loss |
| **FLANGE_GASKET** | Flange-Gasket | Nonlinear, creep, relaxation | K: tangent k(δ), C: viscoelastic, F: plastic/creep |
| **FLANGE_FLANGE** | Metal-to-metal | High stiffness, fretting | K: very high k_c, low damping |
| **HEAD_FLANGE** | Direct contact | No washer configuration | K: contact stiffness |
| **NUT_FLANGE** | Direct contact | No washer configuration | K: contact stiffness |

## 🎭 Tribology Models (Layer 3)

Tribological properties exist ONLY at contact interfaces:

### Friction Models
- **Coulomb**: μ_static, μ_kinetic with stick-slip behavior
- **Stribeck**: μ(v) with boundary/mixed/hydrodynamic regimes
- **Rate-Dependent**: Rate-and-state friction μ(v,θ) with state variable
- **Elasto-Plastic**: Pre-sliding stiffness k_σ with hysteresis
- **LuGre**: Dynamic bristle model dz/dt = v - (σ₀|v|/g(v))z

### Wear Models
- **Archard**: V = K×F×s/H (adhesive/abrasive)
- **Energy-Based**: Wear ∝ dissipated energy
- **Fretting**: Cyclic micro-slip damage
- **Fatigue**: Cyclic loading accumulation

### Lubrication Models
- **Dry**: No lubricant (μ ≈ 0.15-0.25)
- **Boundary**: Thin film (μ ≈ 0.10-0.15)
- **Mixed**: Partial separation (μ ≈ 0.05-0.10)
- **Hydrodynamic**: Full film (μ ≈ 0.01-0.05)

### Coating Models
- **Properties**: Thickness, hardness, adhesion
- **Degradation**: Time-dependent wear-through
- **Failure Detection**: Coating breakthrough monitoring

## 🧵 Thread Contact Modeling

The thread contact uses a parallel MSD array with sophisticated load distribution:

### Load Distribution Laws

| Law | Formula | Use Case | Example (n=5) |
|-----|---------|----------|---------------|
| **Equal** | φᵢ = 1/n | Idealized, new threads | [0.20, 0.20, 0.20, 0.20, 0.20] |
| **Linear** | φᵢ = 2(n-i+1)/(n(n+1)) | Conservative standard | [0.333, 0.267, 0.200, 0.133, 0.067] |
| **Power** | φᵢ = (n-i+1)^β/Σj^β | Adjustable, β=1.5-2.0 | [0.455, 0.273, 0.145, 0.073, 0.055] |
| **Exponential** | φᵢ = e^(-λ(i-1))/Σe^(-λ(j-1)) | Analytical, λ=0.3-0.5 | [0.330, 0.221, 0.148, 0.099, 0.066] |
| **Yamamoto** | φᵢ = sinh(γ(n-i+0.5))/Σsinh | Research-based | Matches experimental data |

### Helix Coupling

Thread contact creates axial-torsional coupling in [K] matrix:
- **Coupling term**: k × (p/2π) at (axial, torsional) DOFs
- **Enables**: Rotational loosening modeling
- **Effect**: Nut rotation → axial displacement → preload loss

### Thread Geometry

Key parameters calculated from thread specification:
- **Pitch (p)**: Distance between threads [m]
- **Helix angle (λ)**: λ = arctan(p/(π·d₂)) [rad]
- **Pitch diameter (d₂)**: Mean diameter for stress calculation [m]
- **Stress area (A_s)**: Effective load-bearing area [m²]
- **Load fraction per thread (φᵢ)**: From distribution law [-]

## 📉 Preload Loss Mechanisms

Total preload evolution: **F_p(t) = F_p0 - ΔF_total**

### Rotational Loosening
- **Formula**: ΔF_rot = k_bolt × (p/2π) × θ_loosening
- **Condition**: Requires slip at BOTH thread AND bearing surfaces
- **Driver**: Transverse loading F_trans > μ×F_p
- **Mechanism**: Thread helix torque T_helix = F_p × r × tan(λ)

### Non-Rotational Losses

| Mechanism | Formula | Source |
|-----------|---------|--------|
| **Embedding** | ΔF = k_sys × f_z × L × (1-e^(-N/N_c)) | VDI 2230 |
| **Wear** | ΔF = k_sys × K × F × s / (H × A) | Archard model |
| **Gasket Creep** | ΔF = k_sys × δ₀ × C_r × log(t) | Time-dependent |
| **Stress Relaxation** | ΔF = F_p0 × (1-e^(-t/τ)) | Material relaxation |

## 📈 Generated Plots

The analysis engine generates 16 visualization plots:

### Loosening Analysis (9 plots)
1. Preload vs Cycles (with loss mechanism breakdown)
2. Preload vs Time (rotational + non-rotational)
3. Loosening Rate (dF_p/dt and dθ/dt)
4. Stage Analysis (running-in, steady, severe)
5. Friction Evolution (μ(t) for all contacts)
6. Wear Evolution (wear depth accumulation)
7. D-N Curve (loosening diagram)
8. Coupled Evolution (friction-wear-preload)
9. Dashboard Summary (multi-panel overview)

### Similitude Analysis (7 plots)
1. Scaling Relationships (π-groups vs scale factor)
2. Π-Group Analysis (dimensionless groups)
3. Scale Effects Radar (multi-parameter comparison)
4. Correction Factors (scaling corrections)
5. Joint Schematic (geometric representation)
6. Multi-Scale Comparison (prototype vs model)
7. Similitude Dashboard (complete overview)

## 🧪 Testing

```bash
# Run all tests
python test_gui.py
python test_analysis_engine.py

# Test specific modules
python -c "from src.bolt_analysis_studio.core.models.element import *; print('Element OK')"
python -c "from src.bolt_analysis_studio.core.models.model import *; print('Model OK')"
python -c "from src.bolt_analysis_studio.gui import *; print('GUI OK')"
```

## 🧮 Key Formulas

### Thread Helix Coupling
```
Axial-Torsional Coupling: Δx = (p/2π) × Δθ
K-matrix off-diagonal term: K[i_axial, j_theta] = k_thread × (p/2π)
```

### Thread Load Distribution (Power Law, β=2)
```
φᵢ = (n-i+1)² / Σⱼ₌₁ⁿ j²
For n=5: φ = [0.455, 0.273, 0.145, 0.073, 0.055]
```

### Preload Loss Components
```
Total Loss: ΔF_total = ΔF_rot + ΔF_embed + ΔF_wear + ΔF_creep + ΔF_relax

Rotational:  ΔF_rot = k_bolt × (p/2π) × θ_loosening
Embedding:   ΔF_embed = k_sys × f_z × L × (1 - e^(-N/N_c))
Wear:        ΔF_wear = k_sys × (K × F × s) / (H × A)
Creep:       ΔF_creep = k_sys × δ₀ × C_r × log(t)
Relaxation:  ΔF_relax = F_p0 × (1 - e^(-t/τ))
```

### Friction Models
```
Coulomb:     F_f = μ × N × sign(v)
Stribeck:    μ(v) = μ_k + (μ_s - μ_k) × e^(-(|v|/v_s)^α) + γ|v|
Rate-State:  μ(v,θ) = μ₀ + a×ln(v/v_ref) + b×ln(v_ref×θ/D_c)
LuGre:       F = σ₀×z + σ₁×(dz/dt) + σ₂×v
```

### Wear Models
```
Archard:     V = K × F × s / H
             δ_wear = V / A_contact
Energy:      V = K_e × W_dissipated
Fretting:    V = K_f × F × s / H  (if s < s_threshold)
```

### Contact Stiffness
```
Metal-Metal: k_c = E_eff × A_real / t_eff
             E_eff = 1 / ((1-ν₁²)/E₁ + (1-ν₂²)/E₂)
Gasket:      k_g(δ) = dF/dδ  (tangent stiffness, nonlinear)
```

## 📚 Technical References

### Bolt Loosening
- Junker, G.H. (1969). "New Criteria for Self-Loosening of Fasteners Under Vibration"
- Jiang, Y. et al. (2003). "An Experimental Study of Self-Loosening of Bolted Joints"
- Nassar, S.A. & Housari, B.A. (2007). "Effect of Thread Pitch on Self-Loosening"

### Standards and Design
- VDI 2230 Part 1 (2015). "Systematic Calculation of Highly Stressed Bolted Joints"
- ASME B16.20. "Metallic Gaskets for Pipe Flanges"
- EN 13555. "Flanges and their Joints - Gasket Parameters"

### Tribology and Contacts
- Hintikka, J. (2016). "Fretting-Induced Friction and Wear in Large Flat-on-Flat Contact"
- Archard, J.F. (1953). "Contact and Rubbing of Flat Surfaces"
- Bowden, F.P. & Tabor, D. (2001). "The Friction and Lubrication of Solids"

### Thread Load Distribution
- Yamamoto, A. (1980). "The Theory and Computation of Thread Connection"
- Sopwith, D.G. (1948). "The Distribution of Load in Screw Threads"

### Friction Models
- Canudas de Wit, C. et al. (1995). "A New Model for Control of Systems with Friction"
- Olsson, H. et al. (1998). "Friction Models and Friction Compensation"

## 👥 Author

**Prof. Leonardo Rosa Ribeiro da Silva, PhD**

## 📄 License

This software is proprietary.

---

*Bolt Analysis Studio v4.0 - Comprehensive bolted joint analysis software*
