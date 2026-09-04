# Complete Mathematical Framework for Mass-Spring-Damper Modeling of Bolted Flanged Joints

## PART I: SYSTEM ARCHITECTURE AND FUNDAMENTALS

**Version 4.0 - Extended English Edition**
**For: Bolt Analysis Studio - Petrobras/LTAD-âncora interna R&D Project**

**Authors:** L. Ribeiro, D. Carvalho, S.C. Naves, T. Santos, V. Marques, G. Arruda
**General Coordination:** Professor Leonardo Ribeiro, PhD (leorrs@ancora_interna.br)
**Institution:** internal reference - Tribology and Wear Technology Laboratory, Federal University of Uberlândia

---

**Abstract.** This document establishes the system architecture and fundamental modeling concepts for the Mass-Spring-Damper (MSD) representation of bolted flanged joints. The approach draws on the classical spring-analogy framework of Bickford (2008) and the systematic calculation methodology of VDI 2230 Part 1 (2015), extending them into a multi-degree-of-freedom dynamic formulation suitable for self-loosening prediction. The document defines the three-layer hierarchical model (components, contacts, tribology), the degree-of-freedom assignments for each element type, and the connectivity rules that govern how physical components map to mathematical DOFs. The formulation supports axial, torsional, and transverse degrees of freedom, enabling the coupled analysis of preload evolution, friction-driven loosening (Junker, 1969), and wear-induced degradation within a unified time-stepping framework. Target applications include API 6A wellhead connections, ASME B16.5 flanged joints, and subsea equipment operating under cyclic loading from 0 to 100 Hz.

---

# Table of Contents - Part I

1. Introduction and Scope
2. Hierarchical MSD Model Architecture
3. Degrees of Freedom Definition and Connectivity

---

## 1. Introduction and Scope

### 1.1 Purpose of This Document

This comprehensive technical reference provides the complete mathematical framework for modeling bolted flanged joints using Mass-Spring-Damper (MSD) representations. The document covers all aspects from fundamental theory through numerical implementation and visualization, specifically targeting the Bolt Analysis Studio software development for the Petrobras R&D project in collaboration with internal reference.

The document serves multiple purposes:

1. **Theoretical Foundation:** Complete mathematical derivations for all models
2. **Implementation Guide:** Ready-to-use Python code for all algorithms
3. **Validation Reference:** Comparison with experimental data
4. **Training Material:** Detailed explanations for engineering understanding

### 1.2 Scope of the Model

The MSD framework presented here addresses the following phenomena with full mathematical detail:

| Category | Phenomena Covered | Mathematical Models | Implementation Status |
|----------|------------------|---------------------|----------------------|
| **Mechanical** | Preload, stiffness, dynamics | Linear/nonlinear springs, masses [2][4] | Complete |
| **Self-Loosening** | Rotational back-off, slip | Junker [3], Pai-Hess [8], Jiang [7], Nassar | Complete |
| **Tribological** | Friction, wear, lubrication | Coulomb, LuGre [9], Archard, Fouvry | Complete |
| **Thermal** | Expansion, relaxation | Thermal strain, Norton-Bailey creep | Complete |
| **Degradation** | COF evolution, coating wear | Three-phase models (Hintikka et al.) | Complete |

### 1.3 Applicable Standards

The models comply with and reference the following international standards:

**Bolt Design:**
- **VDI 2230 Part 1 (2015):** Systematic calculation of highly stressed bolted joints - Joints with one cylindrical bolt
- **VDI 2230 Part 2 (2014):** Systematic calculation of highly stressed bolted joints - Multi-bolted joints
- **EN 1591-1 (2013):** Flanges and their joints - Design rules for gasketed circular flange connections

**Testing Standards:**
- **ISO 16130 (2015):** Aerospace - Dynamic testing of bolt loosening under transverse loading
- **DIN 65151 (2002):** Dynamic testing of locking characteristics of fasteners under transverse loading
- **NAS 3350 (1991):** Fastener test methods - Vibration

**Material Standards:**
- **ASTM A193/A193M:** Standard Specification for Alloy-Steel and Stainless Steel Bolting for High Temperature Service
- **ASTM A320/A320M:** Standard Specification for Alloy-Steel and Stainless Steel Bolting for Low-Temperature Service
- **ASTM A453/A453M:** Standard Specification for High-Temperature Bolting with Expansion Coefficients Comparable to Austenitic Stainless Steels

**Flange Standards:**
- **API 6A (2018):** Wellhead and Christmas Tree Equipment
- **ASME B16.5:** Pipe Flanges and Flanged Fittings
- **ASME PCC-1 (2019):** Guidelines for Pressure Boundary Bolted Flange Joint Assembly

### 1.4 Target Applications

The primary applications for this framework are:

**1. API 6A Flanged Connections:**
- Wellhead equipment for oil and gas
- Pressure classes: 2000, 3000, 5000, 10000, 15000, 20000 PSI
- Types: 6B, 6BX
- Materials: ASTM A182 F316, A350 LF2, etc.

**2. Pressure Vessel Flanges:**
- ASME B16.5 flanges with spiral wound gaskets
- Classes 150, 300, 600, 900, 1500, 2500
- Ring type joint (RTJ) connections

**3. Subsea Equipment:**
- High-pressure manifolds
- Subsea trees
- Pipeline connections

**4. High-Temperature/High-Pressure Applications:**
- L7/L7M studs per ASTM A320
- Temperature range: -100°C to +500°C
- Pressure range: 0 to 15000 PSI

**5. Cyclic Loading Environments:**
- Frequency range: 0-100 Hz
- Amplitude: 1-20% of yield stress
- Duration: up to 10⁶ cycles

### 1.5 Document Conventions

Throughout this document, the following conventions are used:

**Mathematical Notation:**
- Vectors are denoted with curly braces: {u}
- Matrices are denoted with square brackets: [K]
- Scalar quantities use standard italic: F, k, μ
- Time derivatives use dot notation: u̇ = du/dt, ü = d²u/dt²
- Partial derivatives: ∂F/∂x

**Units:**
- SI units are used unless otherwise specified
- Common conversions provided where useful
- API units (PSI, inches) noted for relevant standards

**Indices:**
- i, j for node numbers
- e for element numbers
- n for time step numbers
- α, β for material/method parameters

**Code Conventions:**
- Python 3.10+ syntax
- NumPy for numerical operations
- Type hints for clarity
- Dataclasses for structured data

---

## 2. Hierarchical MSD Model Architecture

### 2.1 Three-Layer Model Philosophy

The bolted joint system is organized into three distinct hierarchical layers, each with specific responsibilities and properties. This separation of concerns enables modular design, independent calibration, and efficient computation.

```
╔═══════════════════════════════════════════════════════════════════════════════════╗
║                    BOLTED JOINT MSD SYSTEM ARCHITECTURE                            ║
╠═══════════════════════════════════════════════════════════════════════════════════╣
║                                                                                    ║
║  ┌────────────────────────────────────────────────────────────────────────────┐   ║
║  │                         EXTERNAL LOADING LAYER                              │   ║
║  │                                                                             │   ║
║  │   {F_ext(t)} = {F_axial} + {F_transverse} + {F_bending} + {F_thermal}      │   ║
║  │                                                                             │   ║
║  │   Applied at specific DOFs based on loading location and type              │   ║
║  │   Time-dependent functions: constant, harmonic, ramp, spectrum             │   ║
║  └────────────────────────────────────────────────────────────────────────────┘   ║
║                                         │                                          ║
║                                         ▼                                          ║
║  ┌────────────────────────────────────────────────────────────────────────────┐   ║
║  │                    LAYER 1: COMPONENT MSD ELEMENTS                          │   ║
║  │                                                                             │   ║
║  │  Physical parts with BULK MATERIAL properties ONLY:                        │   ║
║  │                                                                             │   ║
║  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐       │   ║
║  │  │  BOLT HEAD  │  │    STUD     │  │     NUT     │  │   WASHER    │       │   ║
║  │  │             │  │   (Shank)   │  │             │  │             │       │   ║
║  │  │  m₁, J₁     │  │  m₂, J₂    │  │  m₃, J₃     │  │  m₄         │       │   ║
║  │  │  k₁_axial   │  │  k₂_axial  │  │  k₃_axial   │  │  k₄_axial   │       │   ║
║  │  │  k₁_tors    │  │  k₂_tors   │  │  k₃_tors    │  │             │       │   ║
║  │  │  c₁         │  │  c₂        │  │  c₃         │  │  c₄         │       │   ║
║  │  │             │  │             │  │             │  │             │       │   ║
║  │  │ Material:   │  │ Material:   │  │ Material:   │  │ Material:   │       │   ║
║  │  │ E, ν, ρ     │  │ E, ν, ρ    │  │ E, ν, ρ     │  │ E, ν, ρ     │       │   ║
║  │  │ NO friction │  │ NO friction │  │ NO friction │  │ NO friction │       │   ║
║  │  │ NO wear     │  │ NO wear     │  │ NO wear     │  │ NO wear     │       │   ║
║  │  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘       │   ║
║  │         │                │                │                │               │   ║
║  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                        │   ║
║  │  │   FLANGE 1  │  │   FLANGE 2  │  │   GASKET    │                        │   ║
║  │  │             │  │             │  │             │                        │   ║
║  │  │  m₅, k₅, c₅ │  │  m₆, k₆, c₆│  │  m₇, k₇(δ)  │  ← NONLINEAR          │   ║
║  │  │             │  │             │  │  Viscoelast.│                        │   ║
║  │  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘                        │   ║
║  │         │                │                │                               │   ║
║  └─────────│────────────────│────────────────│───────────────────────────────┘   ║
║            │                │                │                                    ║
║            ▼                ▼                ▼                                    ║
║  ┌────────────────────────────────────────────────────────────────────────────┐   ║
║  │                    LAYER 2: CONTACT MSD ELEMENTS                            │   ║
║  │                                                                             │   ║
║  │  Interfaces between components - MECHANICAL contact properties:            │   ║
║  │                                                                             │   ║
║  │  ╔═══════════════╗  ╔═══════════════╗  ╔═══════════════╗  ╔═══════════════╗│   ║
║  │  ║    THREAD     ║  ║  BEARING_HEAD ║  ║  BEARING_NUT  ║  ║ WASHER_FLANGE ║│   ║
║  │  ║    CONTACT    ║  ║    CONTACT    ║  ║    CONTACT    ║  ║    CONTACT    ║│   ║
║  │  ║               ║  ║               ║  ║               ║  ║               ║│   ║
║  │  ║ [T₁][T₂]...[Tₙ]║  ║  k_c, c_c    ║  ║  k_c, c_c    ║  ║  k_c, c_c    ║│   ║
║  │  ║ n parallel    ║  ║               ║  ║               ║  ║               ║│   ║
║  │  ║ thread MSD    ║  ║ Torsional DOF ║  ║ Torsional DOF ║  ║ Embedding    ║│   ║
║  │  ║ elements      ║  ║ coupling      ║  ║ coupling      ║  ║ model        ║│   ║
║  │  ║               ║  ║               ║  ║               ║  ║               ║│   ║
║  │  ║ HELIX COUPLING║  ║ FRICTION      ║  ║ FRICTION      ║  ║ FRETTING     ║│   ║
║  │  ║ Δx=(p/2π)Δθ  ║  ║ TORQUE        ║  ║ TORQUE        ║  ║              ║│   ║
║  │  ╚═══════╤═══════╝  ╚═══════╤═══════╝  ╚═══════╤═══════╝  ╚═══════╤═══════╝│   ║
║  │          │                  │                  │                  │        │   ║
║  │  ╔═══════════════╗  ╔═══════════════╗                                     │   ║
║  │  ║ FLANGE_GASKET ║  ║ FLANGE_FLANGE ║                                     │   ║
║  │  ║    CONTACT    ║  ║    CONTACT    ║                                     │   ║
║  │  ║               ║  ║               ║                                     │   ║
║  │  ║ k_g(δ) nonlin ║  ║  k_c, c_c    ║                                     │   ║
║  │  ║ Viscoelastic  ║  ║  Fretting    ║                                     │   ║
║  │  ║ Creep model   ║  ║  Microslip   ║                                     │   ║
║  │  ╚═══════╤═══════╝  ╚═══════╤═══════╝                                     │   ║
║  │          │                  │                                              │   ║
║  └──────────│──────────────────│──────────────────────────────────────────────┘   ║
║             │                  │                                                   ║
║             ▼                  ▼                                                   ║
║  ┌────────────────────────────────────────────────────────────────────────────┐   ║
║  │                    LAYER 3: TRIBOLOGICAL LAYER                              │   ║
║  │                                                                             │   ║
║  │  Surface interaction phenomena - ATTACHED TO EACH CONTACT ELEMENT:         │   ║
║  │                                                                             │   ║
║  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐             │   ║
║  │  │  FRICTION MODEL │  │   WEAR MODEL    │  │ LUBRICATION     │             │   ║
║  │  │                 │  │                 │  │     MODEL       │             │   ║
║  │  │ • Coulomb       │  │ • Archard       │  │ • Dry           │             │   ║
║  │  │ • Stribeck      │  │ • Energy-based  │  │ • Boundary      │             │   ║
║  │  │ • LuGre         │  │ • Fretting      │  │ • Mixed         │             │   ║
║  │  │ • Dahl          │  │ • Oxidative     │  │ • Hydrodynamic  │             │   ║
║  │  │ • Iwan          │  │                 │  │                 │             │   ║
║  │  │                 │  │ Parameters:     │  │                 │             │   ║
║  │  │ Parameters:     │  │ K, α, H         │  │ Parameters:     │             │   ║
║  │  │ μ_s, μ_k, σ₀   │  │                 │  │ η, h_min        │             │   ║
║  │  │ σ₁, σ₂, v_s    │  │                 │  │                 │             │   ║
║  │  └─────────────────┘  └─────────────────┘  └─────────────────┘             │   ║
║  │                                                                             │   ║
║  │  ┌─────────────────┐  ┌─────────────────┐                                  │   ║
║  │  │  COATING MODEL  │  │  DEGRADATION    │                                  │   ║
║  │  │                 │  │     MODEL       │                                  │   ║
║  │  │ • Zinc          │  │ • COF evolution │                                  │   ║
║  │  │ • Phosphate     │  │ • Running-in    │                                  │   ║
║  │  │ • PTFE          │  │ • Steady-state  │                                  │   ║
║  │  │ • MoS₂          │  │ • Long-term     │                                  │   ║
║  │  │ • DLC           │  │   degradation   │                                  │   ║
║  │  │                 │  │                 │                                  │   ║
║  │  │ Parameters:     │  │ Parameters:     │                                  │   ║
║  │  │ thickness, μ_c  │  │ λ₁, λ₂, N_c    │                                  │   ║
║  │  └─────────────────┘  └─────────────────┘                                  │   ║
║  │                                                                             │   ║
║  └────────────────────────────────────────────────────────────────────────────┘   ║
║                                                                                    ║
╚═══════════════════════════════════════════════════════════════════════════════════╝
```

### 2.2 Fundamental Design Principle: Separation of Concerns

**Critical Rule:** Tribological properties belong ONLY to contact elements, NOT to components.

| Layer | Contains | Does NOT Contain |
|-------|----------|-----------------|
| **Component (Layer 1)** | Mass, bulk stiffness, material damping, rotational inertia | Friction, wear, surface roughness effects |
| **Contact (Layer 2)** | Contact stiffness, connectivity, interface mechanics | Bulk material properties |
| **Tribology (Layer 3)** | Friction, wear, lubrication, coatings, degradation | Structural stiffness |

**Benefits of This Separation:**

1. **Modular Calibration:** Each layer can be calibrated independently
   - Component properties from material data sheets
   - Contact stiffness from Hertzian contact theory
   - Friction from tribological testing

2. **Efficient Updates:** When only friction changes, only tribology layer updates
   - No need to reassemble structural matrices
   - Significant computational savings

3. **Physical Traceability:** Clear connection to physical phenomena
   - Component properties = bulk material behavior
   - Contact properties = interface mechanics
   - Tribology = surface interaction physics

4. **Model Flexibility:** Easy substitution of models
   - Swap Coulomb for LuGre friction without touching structure
   - Change wear model from Archard to energy-based
   - Add/remove coating effects

### 2.3 Governing Equation of Motion

The complete equation of motion for the MSD system follows the standard structural dynamics formulation [10]:

$$[M]\{\ddot{u}\} + [C]\{\dot{u}\} + [K]\{u\} = \{F_{ext}(t)\} + \{F_{tribo}(u, \dot{u}, \text{state})\}$$

**Where:**

- **[M]** = Global mass matrix (n × n)
  - Diagonal for lumped mass formulation
  - Contains translational masses and rotational inertias
  - Units: kg (translational), kg·m² (rotational)

- **[C]** = Global damping matrix (n × n)
  - Rayleigh damping: [C] = α_M[M] + β_K[K] [10]
  - Plus contact damping contributions
  - Units: N·s/m (translational), N·m·s/rad (rotational)

- **[K]** = Global stiffness matrix (n × n)
  - Assembled from component and contact contributions
  - Includes helix coupling (off-diagonal) for threads
  - May be nonlinear (updated during solution)
  - Units: N/m (translational), N·m/rad (rotational)

- **{u}** = Displacement vector (n × 1)
  - Contains all DOF displacements
  - Mixed units: m (translational), rad (rotational)

- **{F_ext(t)}** = External force vector (n × 1)
  - Applied loads: axial, transverse, thermal
  - Time-dependent
  - Units: N (force), N·m (torque)

- **{F_tribo}** = Tribological force vector (n × 1)
  - Friction forces
  - Depends on state (velocity, displacement, history)
  - Units: N (force), N·m (torque)

### 2.4 Physical Assembly Representation

The following diagram shows how physical components map to the MSD model:

```
                        EXTERNAL LOADS
                        F_axial, F_trans, M_bend
                             │
                             ▼
                  ┌──────────────────────┐
                  │      BOLT HEAD       │ ◄─── Component MSD Element
                  │     Node 1           │      m_head = ρ × V_head
                  │     DOF: x₁          │      k_head = E × A / L_head
                  │     Mass: m₁         │      J_head = ½m₁r²
                  │     Inertia: J₁      │
                  └──────────┬───────────┘
                             │
                  ╔══════════╧══════════╗
                  ║   BEARING CONTACT   ║ ◄─── Contact MSD Element
                  ║   (Head-Washer)     ║      k_c = E_eff × A / t_eff
                  ║                     ║
                  ║   + TRIBOLOGY:      ║      ◄─── Tribology Layer
                  ║   • μ_bearing(N,p,v)║           Friction model
                  ║   • Wear K_archard  ║           Wear model
                  ║   • T_bearing       ║           Friction torque
                  ║                     ║
                  ║   DOFs: x₁ ↔ x₂     ║
                  ║         + θ_stud    ║      (Torsional coupling)
                  ╚══════════╤══════════╝
                             │
                  ┌──────────┴───────────┐
                  │      WASHER 1        │ ◄─── Component MSD Element
                  │     Node 2, DOF: x₂  │
                  │     Mass: m_washer   │
                  └──────────┬───────────┘
                             │
                  ╔══════════╧══════════╗
                  ║   WASHER-FLANGE     ║ ◄─── Contact MSD Element
                  ║      CONTACT        ║
                  ║                     ║
                  ║   + TRIBOLOGY:      ║
                  ║   • Embedding model ║      δ_embed(N)
                  ║   • Fretting wear   ║      
                  ║                     ║
                  ║   DOFs: x₂ ↔ x₃     ║
                  ╚══════════╤══════════╝
                             │
                  ┌──────────┴───────────┐
                  │      FLANGE 1        │ ◄─── Component MSD Element
                  │     Node 3           │
                  │     DOF: x₃, y₃, z₃  │      (Axial + Transverse)
                  │     Mass: m_flange1  │
                  │                      │
                  │     Rötscher cone    │      k_m = πEd·tanα/ln[...] [5]
                  │     stiffness model  │
                  └──────────┬───────────┘
                             │
                  ╔══════════╧══════════╗
                  ║   FLANGE-GASKET     ║ ◄─── Contact MSD Element (NONLINEAR)
                  ║      CONTACT        ║
                  ║                     ║
                  ║   k_g = k_g(δ)      ║      Tangent stiffness
                  ║   Loading ≠ Unload  ║      Hysteresis
                  ║   Creep: δ_c(t)     ║      Time-dependent relaxation
                  ║   Plastic: δ_p      ║      Permanent set
                  ║                     ║
                  ║   DOFs: x₃ ↔ x₄     ║
                  ╚══════════╤══════════╝
                             │
                  ┌──────────┴───────────┐
                  │       GASKET         │ ◄─── Component MSD Element (Nonlinear)
                  │     Node 4, DOF: x₄  │
                  │     Mass: m_gasket   │      Typically small
                  │                      │
                  │     Viscoelastic     │      Maxwell/Voigt models
                  │     behavior         │
                  └──────────┬───────────┘
                             │
                  ╔══════════╧══════════╗
                  ║   GASKET-FLANGE     ║
                  ║      CONTACT        ║
                  ║   (Mirror of above) ║
                  ║   DOFs: x₄ ↔ x₅     ║
                  ╚══════════╤══════════╝
                             │
                  ┌──────────┴───────────┐
                  │      FLANGE 2        │ ◄─── Component MSD Element
                  │     Node 5           │
                  │     DOF: x₅, y₄, z₄  │
                  │     Mass: m_flange2  │
                  └──────────┬───────────┘
                             │
                  ╔══════════╧══════════╗
                  ║   WASHER-FLANGE     ║
                  ║      CONTACT        ║
                  ║   DOFs: x₅ ↔ x₆     ║
                  ╚══════════╤══════════╝
                             │
                  ┌──────────┴───────────┐
                  │      WASHER 2        │
                  │     Node 6, DOF: x₆  │
                  └──────────┬───────────┘
                             │
                  ╔══════════╧══════════╗
                  ║   BEARING CONTACT   ║ ◄─── Contact MSD Element
                  ║   (Nut-Washer)      ║
                  ║                     ║
                  ║   + TRIBOLOGY:      ║
                  ║   • μ_bearing       ║
                  ║   • T_bearing       ║      RESISTS LOOSENING
                  ║                     ║
                  ║   DOFs: x₆ ↔ x₇     ║
                  ║         + θ_nut     ║
                  ╚══════════╤══════════╝
                             │
                  ┌──────────┴───────────┐
                  │         NUT          │ ◄─── Component MSD Element
                  │     Node 7           │
                  │     DOF: x₇, θ_nut   │
                  │     Mass: m_nut      │
                  │     Inertia: J_nut   │
                  └──────────┬───────────┘
                             │
     ╔═════════════════════════════════════════════════════════════════╗
     ║                    THREAD CONTACT                                ║
     ║                    (Stud-Nut Interface)                         ║
     ║                                                                  ║
     ║   ┌─────────────────────────────────────────────────────────┐   ║
     ║   │                                                         │   ║
     ║   │  INDIVIDUAL THREAD ELEMENTS (n = 8 typical):           │   ║
     ║   │                                                         │   ║
     ║   │  Thread 1: [k₁,c₁,μ₁,w₁] ████████████  φ₁ = 19.0%     │   ║
     ║   │  Thread 2: [k₂,c₂,μ₂,w₂] ██████████    φ₂ = 16.0%     │   ║
     ║   │  Thread 3: [k₃,c₃,μ₃,w₃] ████████      φ₃ = 13.5%     │   ║
     ║   │  Thread 4: [k₄,c₄,μ₄,w₄] ██████        φ₄ = 11.4%     │   ║
     ║   │  Thread 5: [k₅,c₅,μ₅,w₅] █████         φ₅ = 9.6%      │   ║
     ║   │  Thread 6: [k₆,c₆,μ₆,w₆] ████          φ₆ = 8.1%      │   ║
     ║   │  Thread 7: [k₇,c₇,μ₇,w₇] ███           φ₇ = 6.8%      │   ║
     ║   │  Thread 8: [k₈,c₈,μ₈,w₈] ██            φ₈ = 5.7%      │   ║
     ║   │                                                         │   ║
     ║   │  Each thread has INDEPENDENT:                          │   ║
     ║   │  • Stiffness k_i = φ_i × k_base                        │   ║
     ║   │  • Friction μ_i(N, p, wear)                            │   ║
     ║   │  • Wear state w_i accumulated                          │   ║
     ║   │  • Slip state (stick/partial/gross)                    │   ║
     ║   │  • Loosening contribution Δθ_i                         │   ║
     ║   │                                                         │   ║
     ║   └─────────────────────────────────────────────────────────┘   ║
     ║                                                                  ║
     ║   HELIX COUPLING (The Key to Self-Loosening) [3][7]:              ║
     ║                                                                  ║
     ║   Δx_axial = (p / 2π) × Δθ_rotation                            ║
     ║                                                                  ║
     ║   This kinematic constraint creates OFF-DIAGONAL terms in [K]:  ║
     ║                                                                  ║
     ║   [K_thread] = k_th × | 1      -λ      λ   |                   ║
     ║                       | -λ     λ²     -λ²  |  where λ = p/2π   ║
     ║                       | λ     -λ²      λ²  |                   ║
     ║                                                                  ║
     ║   DOFs: x_nut ↔ θ_stud ↔ θ_nut                                 ║
     ║                                                                  ║
     ╚════════════════════════════════════════════════════════════════╝
                                  │
                  ┌───────────────┴───────────────┐
                  │         STUD (Shank)           │ ◄─── Component MSD Element
                  │     Node 8                     │
                  │     DOF: x₈, θ_stud            │
                  │     Mass: m_stud               │
                  │     Inertia: J_stud            │
                  │                                │
                  │     Axial: k_b = EA/L         │
                  │     Torsional: k_θ = GJ/L     │
                  │                                │
                  │     THIS IS THE PRELOAD       │
                  │     CARRYING ELEMENT          │
                  └────────────────────────────────┘
```

### 2.5 Information Flow During Solution

The following diagram shows how information flows through the solver during a transient analysis:

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                         SOLUTION INFORMATION FLOW                                │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│  FOR EACH TIME STEP n:                                                          │
│  ═══════════════════════                                                        │
│                                                                                  │
│  ┌───────────────────────────────────────────────────────────────────────────┐ │
│  │  STEP 1: COMPUTE EXTERNAL FORCES                                          │ │
│  │                                                                            │ │
│  │  {F_ext}(t_n) = {F_preload} + {F_axial}(t_n) + {F_trans}(t_n)            │ │
│  │                 + {F_thermal}(t_n) + {F_bending}(t_n)                     │ │
│  │                                                                            │ │
│  │  Input: Loading protocol, current time t_n                                │ │
│  │  Output: External force vector {F_ext}                                    │ │
│  └──────────────────────────────────┬────────────────────────────────────────┘ │
│                                     │                                           │
│                                     ▼                                           │
│  ┌───────────────────────────────────────────────────────────────────────────┐ │
│  │  STEP 2: COMPUTE TRIBOLOGICAL FORCES                                      │ │
│  │                                                                            │ │
│  │  FOR EACH CONTACT ELEMENT:                                                │ │
│  │    • Get current state: u_local, v_local, F_normal                       │ │
│  │    • Compute friction: F_f = friction_model(v, F_n, state)               │ │
│  │    • Compute wear increment: Δh = wear_model(F_n, slip, E_d)             │ │
│  │    • Compute friction torque: T = μ × F_n × r_eff                        │ │
│  │    • Assemble into {F_tribo}                                              │ │
│  │                                                                            │ │
│  │  Input: Current {u}, {v}, contact states                                  │ │
│  │  Output: Tribological force vector {F_tribo}                              │ │
│  └──────────────────────────────────┬────────────────────────────────────────┘ │
│                                     │                                           │
│                                     ▼                                           │
│  ┌───────────────────────────────────────────────────────────────────────────┐ │
│  │  STEP 3: CHECK MATRIX UPDATES                                             │ │
│  │                                                                            │ │
│  │  IF significant stiffness change (nonlinear elements):                    │ │
│  │    • Update gasket tangent stiffness: k_g = dk/dδ                        │ │
│  │    • Update contact stiffness if separation occurs                        │ │
│  │    • Reassemble [K] if changes > tolerance                               │ │
│  │    • Recompute effective stiffness for Newmark                           │ │
│  │                                                                            │ │
│  │  Input: Contact states, gasket compression                                │ │
│  │  Output: Updated [K] if necessary                                         │ │
│  └──────────────────────────────────┬────────────────────────────────────────┘ │
│                                     │                                           │
│                                     ▼                                           │
│  ┌───────────────────────────────────────────────────────────────────────────┐ │
│  │  STEP 4: SOLVE EQUATION OF MOTION (Newmark-β or HHT-α)                   │ │
│  │                                                                            │ │
│  │  Equation: [M]{ü}ₙ₊₁ + [C]{u̇}ₙ₊₁ + [K]{u}ₙ₊₁ = {F_ext} + {F_tribo}     │ │
│  │                                                                            │ │
│  │  Newmark-β predictor:                                                     │ │
│  │    {ũ}ₙ₊₁ = {u}ₙ + Δt{u̇}ₙ + (0.5-β)Δt²{ü}ₙ                             │ │
│  │    {ṽ}ₙ₊₁ = {u̇}ₙ + (1-γ)Δt{ü}ₙ                                          │ │
│  │                                                                            │ │
│  │  Effective stiffness: [K_eff] = [K] + γ/(βΔt)[C] + 1/(βΔt²)[M]          │ │
│  │                                                                            │ │
│  │  Solve: [K_eff]{u}ₙ₊₁ = {F_eff}                                          │ │
│  │                                                                            │ │
│  │  Corrector:                                                               │ │
│  │    {ü}ₙ₊₁ = ({u}ₙ₊₁ - {ũ}ₙ₊₁)/(βΔt²)                                   │ │
│  │    {u̇}ₙ₊₁ = {ṽ}ₙ₊₁ + γΔt{ü}ₙ₊₁                                         │ │
│  │                                                                            │ │
│  │  Input: [M], [C], [K], {F}, {u}ₙ, {u̇}ₙ, {ü}ₙ                            │ │
│  │  Output: {u}ₙ₊₁, {u̇}ₙ₊₁, {ü}ₙ₊₁                                         │ │
│  └──────────────────────────────────┬────────────────────────────────────────┘ │
│                                     │                                           │
│                                     ▼                                           │
│  ┌───────────────────────────────────────────────────────────────────────────┐ │
│  │  STEP 5: UPDATE CONTACT STATES                                            │ │
│  │                                                                            │ │
│  │  FOR EACH CONTACT:                                                        │ │
│  │    • Update relative displacement: Δu = u_j - u_i                        │ │
│  │    • Update relative velocity: Δv = v_j - v_i                            │ │
│  │    • Update slip state (stick/partial/gross)                             │ │
│  │    • Update friction state (LuGre bristle z, Dahl force F)               │ │
│  │    • Accumulate wear: h_total += Δh                                      │ │
│  │    • Update friction coefficient: μ(N, p, wear)                          │ │
│  │                                                                            │ │
│  │  Input: New {u}, {v}, previous states                                    │ │
│  │  Output: Updated contact states                                           │ │
│  └──────────────────────────────────┬────────────────────────────────────────┘ │
│                                     │                                           │
│                                     ▼                                           │
│  ┌───────────────────────────────────────────────────────────────────────────┐ │
│  │  STEP 6: COMPUTE SELF-LOOSENING (Thread Elements) [3][7][8]              │ │
│  │                                                                            │ │
│  │  FOR EACH THREAD:                                                         │ │
│  │    • Check Junker criterion: T_pitch > T_thread + T_bearing?             │ │
│  │    • If YES and slipping: compute Δθ_i                                   │ │
│  │    • Accumulate: θ_total += Σ(φ_i × Δθ_i)                               │ │
│  │                                                                            │ │
│  │  Compute preload loss from rotation:                                      │ │
│  │    ΔF_rotation = k_bolt × (p/2π) × Δθ_total                              │ │
│  │                                                                            │ │
│  │  Input: Thread states, preload, transverse force                         │ │
│  │  Output: Loosening angle, preload loss                                    │ │
│  └──────────────────────────────────┬────────────────────────────────────────┘ │
│                                     │                                           │
│                                     ▼                                           │
│  ┌───────────────────────────────────────────────────────────────────────────┐ │
│  │  STEP 7: UPDATE PRELOAD                                                   │ │
│  │                                                                            │ │
│  │  F_p(t_n+1) = F_p(t_n) - ΔF_rotation - ΔF_embedding - ΔF_relaxation     │ │
│  │               - ΔF_creep - ΔF_wear - ΔF_thermal                           │ │
│  │                                                                            │ │
│  │  Each loss mechanism computed independently:                              │ │
│  │    • ΔF_rotation: From thread back-off (Junker)                          │ │
│  │    • ΔF_embedding: From surface settling                                  │ │
│  │    • ΔF_relaxation: From stress relaxation                               │ │
│  │    • ΔF_creep: From gasket creep                                         │ │
│  │    • ΔF_wear: From material removal                                      │ │
│  │    • ΔF_thermal: From differential expansion                             │ │
│  │                                                                            │ │
│  │  Input: All loss mechanisms                                               │ │
│  │  Output: Updated preload F_p                                              │ │
│  └──────────────────────────────────┬────────────────────────────────────────┘ │
│                                     │                                           │
│                                     ▼                                           │
│  ┌───────────────────────────────────────────────────────────────────────────┐ │
│  │  STEP 8: CYCLE COUNTING AND HISTORY                                       │ │
│  │                                                                            │ │
│  │  • Detect zero-crossings of transverse displacement                      │ │
│  │  • Increment cycle counter when full cycle completed                      │ │
│  │  • Update N-dependent quantities (COF evolution, wear rates)             │ │
│  │  • Store results for post-processing                                      │ │
│  │                                                                            │ │
│  │  Input: Displacement history                                              │ │
│  │  Output: Cycle count N, stored results                                    │ │
│  └──────────────────────────────────┬────────────────────────────────────────┘ │
│                                     │                                           │
│                                     ▼                                           │
│  ┌───────────────────────────────────────────────────────────────────────────┐ │
│  │  STEP 9: CONVERGENCE CHECK (if nonlinear)                                │ │
│  │                                                                            │ │
│  │  Check residual: ||{R}|| = ||{F_ext} + {F_tribo} - [M]{ü} - [C]{u̇}      │ │
│  │                           - [K]{u}|| < tolerance?                         │ │
│  │                                                                            │ │
│  │  Check displacement: ||Δu|| / ||u|| < tolerance?                         │ │
│  │                                                                            │ │
│  │  If NOT converged: iterate within time step (Newton-Raphson)             │ │
│  │  If converged: proceed to next time step                                  │ │
│  │                                                                            │ │
│  │  Input: Residual, displacement increment                                  │ │
│  │  Output: Convergence status                                               │ │
│  └───────────────────────────────────────────────────────────────────────────┘ │
│                                                                                  │
│  END FOR (time step loop)                                                       │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Degrees of Freedom Definition and Connectivity

### 3.1 Complete DOF Set for Comprehensive Loosening Analysis

For full self-loosening analysis including all relevant phenomena, a 14-DOF system is recommended:

**Displacement Vector:**

$$\{q\} = \begin{Bmatrix}
x_{bh} \\
x_{ws1} \\
x_{fl1} \\
x_{gasket} \\
x_{fl2} \\
x_{ws2} \\
x_{nut} \\
x_{stud} \\
\theta_{stud} \\
\theta_{nut} \\
y_{fl1} \\
z_{fl1} \\
y_{fl2} \\
z_{fl2}
\end{Bmatrix} = \begin{Bmatrix}
\text{Bolt head axial} \\
\text{Washer 1 axial} \\
\text{Flange 1 axial} \\
\text{Gasket axial} \\
\text{Flange 2 axial} \\
\text{Washer 2 axial} \\
\text{Nut axial} \\
\text{Stud axial} \\
\text{Stud rotation} \\
\text{Nut rotation} \\
\text{Flange 1 transverse Y} \\
\text{Flange 1 transverse Z} \\
\text{Flange 2 transverse Y} \\
\text{Flange 2 transverse Z}
\end{Bmatrix}$$

### 3.2 DOF Classification and Physical Meaning

| Index | Symbol | Type | Component | Physical Meaning | Primary Phenomenon |
|-------|--------|------|-----------|-----------------|-------------------|
| 1 | x_bh | Axial | Bolt head | Axial displacement of bolt head | Load transfer from head |
| 2 | x_ws1 | Axial | Washer 1 | Axial displacement of first washer | Embedding, load spreading |
| 3 | x_fl1 | Axial | Flange 1 | Axial displacement of first flange | Clamping, Rötscher cone |
| 4 | x_g | Axial | Gasket | Axial compression of gasket | Sealing, creep, nonlinear stiffness |
| 5 | x_fl2 | Axial | Flange 2 | Axial displacement of second flange | Clamping, Rötscher cone |
| 6 | x_ws2 | Axial | Washer 2 | Axial displacement of second washer | Embedding, load spreading |
| 7 | x_nut | Axial | Nut | Axial displacement of nut | Thread engagement force |
| 8 | x_stud | Axial | Stud | Axial stretch of stud | **PRELOAD STORAGE** |
| 9 | θ_stud | Torsional | Stud | Rotation angle of stud | Torque during tightening |
| 10 | θ_nut | Torsional | Nut | Rotation angle of nut | **SELF-LOOSENING** |
| 11 | y_fl1 | Transverse | Flange 1 | Y-displacement of flange 1 | **Junker mechanism driver** |
| 12 | z_fl1 | Transverse | Flange 1 | Z-displacement of flange 1 | **Junker mechanism driver** |
| 13 | y_fl2 | Transverse | Flange 2 | Y-displacement of flange 2 | **Junker mechanism driver** |
| 14 | z_fl2 | Transverse | Flange 2 | Z-displacement of flange 2 | **Junker mechanism driver** |

### 3.3 Reduced DOF Configurations for Specific Analyses

**Configuration A: 6-DOF Axial-Only (Preload Analysis)**

$$\{q_{6DOF}\} = \begin{Bmatrix} x_1 \\ x_2 \\ x_3 \\ x_4 \\ x_5 \\ x_6 \end{Bmatrix}$$

**Use Cases:**
- Static preload calculation
- Joint stiffness analysis
- Embedding settling
- Gasket seating
- Thermal expansion effects

**Configuration B: 8-DOF Axial + Torsional (Rotational Loosening Only)**

$$\{q_{8DOF}\} = \begin{Bmatrix} x_1 \\ x_2 \\ x_3 \\ x_4 \\ x_5 \\ x_6 \\ \theta_{stud} \\ \theta_{nut} \end{Bmatrix}$$

**Use Cases:**
- Torsional vibration analysis
- Pure rotational loosening (no transverse load)
- Torque transmission analysis

**Configuration C: 10-DOF Standard Junker Analysis**

$$\{q_{10DOF}\} = \begin{Bmatrix} x_1 \\ \vdots \\ x_6 \\ \theta_{stud} \\ \theta_{nut} \\ y_{joint} \\ z_{joint} \end{Bmatrix}$$

**Use Cases:**
- Standard Junker test simulation
- Single-point transverse loading
- Simplified loosening analysis

**Configuration D: 14-DOF Full Analysis**

$$\{q_{14DOF}\} = \text{(Full vector as shown in 3.1)}$$

**Use Cases:**
- Complete self-loosening analysis
- Distributed transverse loading
- Bending moment effects
- Most accurate loosening prediction

### 3.4 Connectivity Matrix (Incidence Matrix) Definition

The connectivity matrix [L_e] maps local element DOFs to global system DOFs:

$$\{q_{local}\}_e = [L_e]\{q_{global}\}$$

**Properties of [L_e]:**
- Dimensions: m × n where m = local DOFs, n = global DOFs
- Boolean matrix: entries are 0 or 1
- Each row has exactly one entry = 1
- Defines the DOF correspondence for element e

**General Construction:**

For element e connecting nodes i and j with local DOFs {u_i, u_j}:

$$[L_e] = \begin{bmatrix}
\cdots & 0 & 1 & 0 & \cdots & 0 & 0 & 0 & \cdots \\
\cdots & 0 & 0 & 0 & \cdots & 0 & 1 & 0 & \cdots
\end{bmatrix}$$

Where 1's appear at columns corresponding to global DOF indices.

### 3.5 Complete Connectivity Map for 14-DOF System

```
╔═══════════════════════════════════════════════════════════════════════════════════╗
║                         COMPLETE CONNECTIVITY MAP                                  ║
║                         (14-DOF Standard Configuration)                            ║
╠═══════════════════════════════════════════════════════════════════════════════════╣
║                                                                                    ║
║  GLOBAL DOF INDEX:  1    2    3    4    5    6    7    8    9   10   11   12  13  14
║  GLOBAL DOF NAME:  x_bh x_w1 x_f1 x_g  x_f2 x_w2 x_nt x_st θ_st θ_nt y_f1 z_f1 y_f2 z_f2
║                    ───────────────────────────────────────────────────────────────
║                                                                                    ║
║  CONTACT ELEMENT              LOCAL DOFs              GLOBAL DOF MAPPING          ║
║  ═══════════════              ══════════              ══════════════════          ║
║                                                                                    ║
║  ┌─────────────────────────────────────────────────────────────────────────────┐ ║
║  │ BEARING_HEAD               {x_head, x_washer,     DOFs: 1, 2, 9             │ ║
║  │ (Bolt head - Washer 1)      θ_stud}                                          │ ║
║  │                                                                              │ ║
║  │ [L] = | 1 0 0 0 0 0 0 0 0 0 0 0 0 0 |   x_head → DOF 1                      │ ║
║  │       | 0 1 0 0 0 0 0 0 0 0 0 0 0 0 |   x_washer → DOF 2                    │ ║
║  │       | 0 0 0 0 0 0 0 0 1 0 0 0 0 0 |   θ_stud → DOF 9                      │ ║
║  │                                                                              │ ║
║  │ Provides: Axial stiffness + Bearing friction torque                         │ ║
║  └─────────────────────────────────────────────────────────────────────────────┘ ║
║                                                                                    ║
║  ┌─────────────────────────────────────────────────────────────────────────────┐ ║
║  │ WASHER_FLANGE_1            {x_washer, x_flange}   DOFs: 2, 3                │ ║
║  │ (Washer 1 - Flange 1)                                                        │ ║
║  │                                                                              │ ║
║  │ [L] = | 0 1 0 0 0 0 0 0 0 0 0 0 0 0 |   x_washer → DOF 2                    │ ║
║  │       | 0 0 1 0 0 0 0 0 0 0 0 0 0 0 |   x_flange → DOF 3                    │ ║
║  │                                                                              │ ║
║  │ Provides: Axial stiffness + Embedding model                                 │ ║
║  └─────────────────────────────────────────────────────────────────────────────┘ ║
║                                                                                    ║
║  ┌─────────────────────────────────────────────────────────────────────────────┐ ║
║  │ FLANGE_GASKET_1            {x_flange, x_gasket}   DOFs: 3, 4                │ ║
║  │ (Flange 1 - Gasket)                                                          │ ║
║  │                                                                              │ ║
║  │ [L] = | 0 0 1 0 0 0 0 0 0 0 0 0 0 0 |   x_flange → DOF 3                    │ ║
║  │       | 0 0 0 1 0 0 0 0 0 0 0 0 0 0 |   x_gasket → DOF 4                    │ ║
║  │                                                                              │ ║
║  │ Provides: Nonlinear gasket stiffness + Creep                                │ ║
║  └─────────────────────────────────────────────────────────────────────────────┘ ║
║                                                                                    ║
║  ┌─────────────────────────────────────────────────────────────────────────────┐ ║
║  │ GASKET_FLANGE_2            {x_gasket, x_flange}   DOFs: 4, 5                │ ║
║  │ (Gasket - Flange 2)                                                          │ ║
║  │                                                                              │ ║
║  │ [L] = | 0 0 0 1 0 0 0 0 0 0 0 0 0 0 |   x_gasket → DOF 4                    │ ║
║  │       | 0 0 0 0 1 0 0 0 0 0 0 0 0 0 |   x_flange → DOF 5                    │ ║
║  │                                                                              │ ║
║  │ Provides: Nonlinear gasket stiffness + Creep                                │ ║
║  └─────────────────────────────────────────────────────────────────────────────┘ ║
║                                                                                    ║
║  ┌─────────────────────────────────────────────────────────────────────────────┐ ║
║  │ WASHER_FLANGE_2            {x_flange, x_washer}   DOFs: 5, 6                │ ║
║  │ (Flange 2 - Washer 2)                                                        │ ║
║  │                                                                              │ ║
║  │ [L] = | 0 0 0 0 1 0 0 0 0 0 0 0 0 0 |   x_flange → DOF 5                    │ ║
║  │       | 0 0 0 0 0 1 0 0 0 0 0 0 0 0 |   x_washer → DOF 6                    │ ║
║  │                                                                              │ ║
║  │ Provides: Axial stiffness + Embedding model                                 │ ║
║  └─────────────────────────────────────────────────────────────────────────────┘ ║
║                                                                                    ║
║  ┌─────────────────────────────────────────────────────────────────────────────┐ ║
║  │ BEARING_NUT                {x_washer, x_nut,      DOFs: 6, 7, 10            │ ║
║  │ (Washer 2 - Nut)            θ_nut}                                           │ ║
║  │                                                                              │ ║
║  │ [L] = | 0 0 0 0 0 1 0 0 0 0 0 0 0 0 |   x_washer → DOF 6                    │ ║
║  │       | 0 0 0 0 0 0 1 0 0 0 0 0 0 0 |   x_nut → DOF 7                       │ ║
║  │       | 0 0 0 0 0 0 0 0 0 1 0 0 0 0 |   θ_nut → DOF 10                      │ ║
║  │                                                                              │ ║
║  │ Provides: Axial stiffness + Bearing friction torque (RESISTS LOOSENING)     │ ║
║  └─────────────────────────────────────────────────────────────────────────────┘ ║
║                                                                                    ║
║  ┌─────────────────────────────────────────────────────────────────────────────┐ ║
║  │ THREAD_CONTACT             {x_nut, θ_stud, θ_nut} DOFs: 7, 9, 10            │ ║
║  │ (Nut - Stud)                                                                 │ ║
║  │                                                                              │ ║
║  │ [L] = | 0 0 0 0 0 0 1 0 0 0 0 0 0 0 |   x_nut → DOF 7                       │ ║
║  │       | 0 0 0 0 0 0 0 0 1 0 0 0 0 0 |   θ_stud → DOF 9                      │ ║
║  │       | 0 0 0 0 0 0 0 0 0 1 0 0 0 0 |   θ_nut → DOF 10                      │ ║
║  │                                                                              │ ║
║  │ CRITICAL: Contains HELIX COUPLING                                           │ ║
║  │ [K_local] creates axial-torsional coupling                                  │ ║
║  │                                                                              │ ║
║  │ Also contains: Individual thread elements with independent tribology        │ ║
║  └─────────────────────────────────────────────────────────────────────────────┘ ║
║                                                                                    ║
║  ┌─────────────────────────────────────────────────────────────────────────────┐ ║
║  │ TRANSVERSE_CONTACT         {y_fl1, z_fl1, y_fl2, z_fl2}  DOFs: 11, 12, 13, 14│ ║
║  │ (Flange 1 - Flange 2)                                                        │ ║
║  │                                                                              │ ║
║  │ [L] = | 0 0 0 0 0 0 0 0 0 0 1 0 0 0 |   y_fl1 → DOF 11                      │ ║
║  │       | 0 0 0 0 0 0 0 0 0 0 0 1 0 0 |   z_fl1 → DOF 12                      │ ║
║  │       | 0 0 0 0 0 0 0 0 0 0 0 0 1 0 |   y_fl2 → DOF 13                      │ ║
║  │       | 0 0 0 0 0 0 0 0 0 0 0 0 0 1 |   z_fl2 → DOF 14                      │ ║
║  │                                                                              │ ║
║  │ Provides: Transverse stiffness for JUNKER mechanism                         │ ║
║  └─────────────────────────────────────────────────────────────────────────────┘ ║
║                                                                                    ║
╚═══════════════════════════════════════════════════════════════════════════════════╝
```

### 3.6 Python Implementation: DOF and Connectivity

```python
from enum import Enum, auto
from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional
import numpy as np


class DOFType(Enum):
    """Types of degrees of freedom"""
    AXIAL = auto()          # Axial translation (along bolt axis)
    TORSIONAL = auto()      # Rotation about bolt axis
    TRANSVERSE_Y = auto()   # Transverse translation (Y direction)
    TRANSVERSE_Z = auto()   # Transverse translation (Z direction)


@dataclass
class DOFDefinition:
    """Definition of a single degree of freedom"""
    index: int              # Global DOF index (0-based)
    name: str               # Human-readable name
    dof_type: DOFType       # Type of DOF
    component: str          # Associated component name
    unit: str               # Physical unit
    description: str        # Detailed description
    
    def __repr__(self):
        return f"DOF[{self.index}]: {self.name} ({self.dof_type.name})"


class DOFManager:
    """
    Manages degree of freedom definitions and mappings.
    
    Provides consistent DOF handling across the MSD system.
    """
    
    def __init__(self, configuration: str = '14DOF'):
        """
        Initialize DOF manager with specified configuration.
        
        Args:
            configuration: DOF configuration ('6DOF', '8DOF', '10DOF', '14DOF')
        """
        self.configuration = configuration
        self.dofs: List[DOFDefinition] = []
        self.dof_map: Dict[str, int] = {}
        
        self._build_configuration(configuration)
        
    def _build_configuration(self, config: str):
        """Build DOF definitions based on configuration"""
        
        if config == '14DOF':
            self._build_14dof()
        elif config == '10DOF':
            self._build_10dof()
        elif config == '8DOF':
            self._build_8dof()
        elif config == '6DOF':
            self._build_6dof()
        else:
            raise ValueError(f"Unknown configuration: {config}")
        
        # Build name-to-index map
        self.dof_map = {dof.name: dof.index for dof in self.dofs}
        
    def _build_14dof(self):
        """Build full 14-DOF configuration"""
        self.dofs = [
            DOFDefinition(0, 'x_bolt_head', DOFType.AXIAL, 'bolt_head', 'm',
                         'Axial displacement of bolt head'),
            DOFDefinition(1, 'x_washer1', DOFType.AXIAL, 'washer1', 'm',
                         'Axial displacement of washer 1'),
            DOFDefinition(2, 'x_flange1', DOFType.AXIAL, 'flange1', 'm',
                         'Axial displacement of flange 1'),
            DOFDefinition(3, 'x_gasket', DOFType.AXIAL, 'gasket', 'm',
                         'Axial compression of gasket'),
            DOFDefinition(4, 'x_flange2', DOFType.AXIAL, 'flange2', 'm',
                         'Axial displacement of flange 2'),
            DOFDefinition(5, 'x_washer2', DOFType.AXIAL, 'washer2', 'm',
                         'Axial displacement of washer 2'),
            DOFDefinition(6, 'x_nut', DOFType.AXIAL, 'nut', 'm',
                         'Axial displacement of nut'),
            DOFDefinition(7, 'x_stud', DOFType.AXIAL, 'stud', 'm',
                         'Axial stretch of stud (preload storage)'),
            DOFDefinition(8, 'theta_stud', DOFType.TORSIONAL, 'stud', 'rad',
                         'Rotation of stud'),
            DOFDefinition(9, 'theta_nut', DOFType.TORSIONAL, 'nut', 'rad',
                         'Rotation of nut (loosening DOF)'),
            DOFDefinition(10, 'y_flange1', DOFType.TRANSVERSE_Y, 'flange1', 'm',
                         'Transverse Y displacement of flange 1'),
            DOFDefinition(11, 'z_flange1', DOFType.TRANSVERSE_Z, 'flange1', 'm',
                         'Transverse Z displacement of flange 1'),
            DOFDefinition(12, 'y_flange2', DOFType.TRANSVERSE_Y, 'flange2', 'm',
                         'Transverse Y displacement of flange 2'),
            DOFDefinition(13, 'z_flange2', DOFType.TRANSVERSE_Z, 'flange2', 'm',
                         'Transverse Z displacement of flange 2'),
        ]
        
    def _build_10dof(self):
        """Build 10-DOF configuration (standard Junker)"""
        self.dofs = [
            DOFDefinition(0, 'x_bolt_head', DOFType.AXIAL, 'bolt_head', 'm',
                         'Axial displacement of bolt head'),
            DOFDefinition(1, 'x_washer1', DOFType.AXIAL, 'washer1', 'm',
                         'Axial displacement of washer 1'),
            DOFDefinition(2, 'x_flange1', DOFType.AXIAL, 'flange1', 'm',
                         'Axial displacement of flange 1'),
            DOFDefinition(3, 'x_gasket', DOFType.AXIAL, 'gasket', 'm',
                         'Axial compression of gasket'),
            DOFDefinition(4, 'x_flange2', DOFType.AXIAL, 'flange2', 'm',
                         'Axial displacement of flange 2'),
            DOFDefinition(5, 'x_nut', DOFType.AXIAL, 'nut', 'm',
                         'Axial displacement of nut'),
            DOFDefinition(6, 'theta_stud', DOFType.TORSIONAL, 'stud', 'rad',
                         'Rotation of stud'),
            DOFDefinition(7, 'theta_nut', DOFType.TORSIONAL, 'nut', 'rad',
                         'Rotation of nut'),
            DOFDefinition(8, 'y_joint', DOFType.TRANSVERSE_Y, 'joint', 'm',
                         'Transverse Y displacement'),
            DOFDefinition(9, 'z_joint', DOFType.TRANSVERSE_Z, 'joint', 'm',
                         'Transverse Z displacement'),
        ]
        
    def _build_8dof(self):
        """Build 8-DOF configuration (axial + torsional)"""
        self.dofs = [
            DOFDefinition(i, f'x_{i+1}', DOFType.AXIAL, f'node_{i+1}', 'm',
                         f'Axial displacement {i+1}')
            for i in range(6)
        ] + [
            DOFDefinition(6, 'theta_stud', DOFType.TORSIONAL, 'stud', 'rad',
                         'Rotation of stud'),
            DOFDefinition(7, 'theta_nut', DOFType.TORSIONAL, 'nut', 'rad',
                         'Rotation of nut'),
        ]
        
    def _build_6dof(self):
        """Build 6-DOF configuration (axial only)"""
        self.dofs = [
            DOFDefinition(0, 'x_bolt_head', DOFType.AXIAL, 'bolt_head', 'm',
                         'Axial displacement of bolt head'),
            DOFDefinition(1, 'x_washer1', DOFType.AXIAL, 'washer1', 'm',
                         'Axial displacement of washer 1'),
            DOFDefinition(2, 'x_clamp1', DOFType.AXIAL, 'clamp1', 'm',
                         'Axial displacement of clamped member 1'),
            DOFDefinition(3, 'x_clamp2', DOFType.AXIAL, 'clamp2', 'm',
                         'Axial displacement of clamped member 2'),
            DOFDefinition(4, 'x_washer2', DOFType.AXIAL, 'washer2', 'm',
                         'Axial displacement of washer 2'),
            DOFDefinition(5, 'x_nut', DOFType.AXIAL, 'nut', 'm',
                         'Axial displacement of nut'),
        ]
    
    @property
    def n_dof(self) -> int:
        """Total number of DOFs"""
        return len(self.dofs)
    
    def get_dof_index(self, name: str) -> int:
        """Get DOF index by name"""
        return self.dof_map[name]
    
    def get_axial_dofs(self) -> List[int]:
        """Get indices of all axial DOFs"""
        return [d.index for d in self.dofs if d.dof_type == DOFType.AXIAL]
    
    def get_torsional_dofs(self) -> List[int]:
        """Get indices of all torsional DOFs"""
        return [d.index for d in self.dofs if d.dof_type == DOFType.TORSIONAL]
    
    def get_transverse_dofs(self) -> List[int]:
        """Get indices of all transverse DOFs"""
        return [d.index for d in self.dofs 
                if d.dof_type in (DOFType.TRANSVERSE_Y, DOFType.TRANSVERSE_Z)]
    
    def build_connectivity_matrix(self, local_dofs: List[str]) -> np.ndarray:
        """
        Build connectivity matrix for an element.
        
        Args:
            local_dofs: List of DOF names for the element
        
        Returns:
            Connectivity matrix [L] of shape (n_local, n_global)
        """
        n_local = len(local_dofs)
        n_global = self.n_dof
        
        L = np.zeros((n_local, n_global))
        
        for i, dof_name in enumerate(local_dofs):
            if dof_name in self.dof_map:
                j = self.dof_map[dof_name]
                L[i, j] = 1.0
        
        return L
    
    def print_dof_table(self):
        """Print formatted DOF table"""
        print("\nDOF Configuration:", self.configuration)
        print("=" * 80)
        print(f"{'Index':<6} {'Name':<15} {'Type':<12} {'Component':<12} {'Unit':<6} Description")
        print("-" * 80)
        for dof in self.dofs:
            print(f"{dof.index:<6} {dof.name:<15} {dof.dof_type.name:<12} "
                  f"{dof.component:<12} {dof.unit:<6} {dof.description}")
        print("=" * 80)


# Example usage
if __name__ == "__main__":
    # Create 14-DOF manager
    dof_mgr = DOFManager('14DOF')
    dof_mgr.print_dof_table()
    
    # Build connectivity matrix for thread contact
    L_thread = dof_mgr.build_connectivity_matrix(['x_nut', 'theta_stud', 'theta_nut'])
    print("\nThread contact connectivity matrix:")
    print(L_thread)
```

---

## References — Part I

[1] **VDI 2230 Part 1 (2015).** "Systematic Calculation of Highly Stressed Bolted Joints — Joints with One Cylindrical Bolt," Verein Deutscher Ingenieure, Düsseldorf, Germany. — *The internationally recognized standard for calculating high-strength bolted joints. Defines the systematic design methodology, safety factors, embedding losses, and load introduction factors used throughout this framework.*

[2] **Bickford, J.H. (2008).** *Introduction to the Design and Behavior of Bolted Joints: Non-Gasketed Joints*, 4th Edition, CRC Press (Taylor & Francis), Boca Raton, FL. ISBN: 978-0-8493-8176-8. — *Comprehensive reference for bolted joint stiffness models, preload behavior, and the spring analogy (bolt-as-spring, members-as-spring) that forms the basis of the MSD approach.*

[3] **Junker, G.H. (1969).** "New Criteria for Self-Loosening of Fasteners Under Vibration," *SAE Transactions*, Vol. 78, SAE Technical Paper 690055, pp. 314–335. DOI: 10.4271/690055. — *Foundational paper establishing transverse vibration as the primary self-loosening mechanism. The Junker test apparatus (DIN 65151) remains the standard loosening test method.*

[4] **Budynas, R.G. and Nisbett, J.K. (2020).** *Shigley's Mechanical Engineering Design*, 11th Edition, McGraw-Hill Education, New York. ISBN: 978-0-07-339821-1. — *Chapter 8 covers bolt stiffness (k_b = A_t × E / L), member stiffness via frustum cone model, and the load introduction factor n used in the DOF formulation.*

[5] **Wileman, J., Choudhury, M., and Green, I. (1991).** "Computation of Member Stiffness in Bolted Connections," *ASME J. Mechanical Design*, Vol. 113, No. 4, pp. 432–437. DOI: 10.1115/1.2912801. — *FEA-derived exponential formula for member stiffness: k_m = 0.78952 × E × d × exp(0.62914 × d/l). Used in the Rötscher cone stiffness calculation shown in Section 2.4.*

[6] **Motosh, N. (1976).** "Development of Design Charts for Bolts Preloaded up to the Plastic Range," *ASME J. Engineering for Industry*, Vol. 98, No. 3, pp. 849–851. DOI: 10.1115/1.3439041. — *Torque-tension relationship T = K × d × F_i used for preload application in the initial state computation.*

[7] **Jiang, Y., Zhang, M., and Lee, C.H. (2003).** "A Study of Early Stage Self-Loosening of Bolted Joints," *ASME J. Mechanical Design*, Vol. 125, No. 3, pp. 518–526. DOI: 10.1115/1.1586936. — *Two-stage loosening model (non-rotational + rotational) that guides the time-stepping algorithm in Section 2.5.*

[8] **Pai, N.G. and Hess, D.P. (2002).** "Three-Dimensional Finite Element Analysis of Threaded Fastener Loosening due to Dynamic Shear Load," *Engineering Failure Analysis*, Vol. 9, No. 4, pp. 383–402. DOI: 10.1016/S1350-6307(01)00024-3. — *Four slip regimes (no-slip, head-only, nut-only, complete) referenced in the contact state update (Step 5, Section 2.5).*

[9] **Canudas de Wit, C., Olsson, H., Åström, K.J., and Lischinsky, P. (1995).** "A New Model for Control of Systems with Friction," *IEEE Trans. Automatic Control*, Vol. 40, No. 3, pp. 419–425. DOI: 10.1109/9.376053. — *LuGre friction model used in the tribological force computation (Step 2, Section 2.5).*

[10] **Chopra, A.K. (2012).** *Dynamics of Structures: Theory and Applications to Earthquake Engineering*, 4th Edition, Prentice Hall. ISBN: 978-0-13-285803-8. — *Standard reference for the equation of motion [M]{ü} + [C]{u̇} + [K]{u} = {F}, Rayleigh damping, and the Newmark-β time integration used in Section 2.3 and Step 4.*

---

**END OF PART I**

*Part II covers the Contact Element Library*
*Part III covers Matrix Assembly and Coupling*
*Part IV covers Loading Models*
*Part V covers Self-Loosening Models*
*Part VI covers Wear Models*
*Part VII covers Friction Models and Evolution*
*Part VIII covers Numerical Solvers*
*Part IX covers Similitude and Scaling Analysis*
*Part X covers Preload Loss Models*
*Part XI covers the Coupled Friction-Wear-Loosening Analysis Framework*
*Part XII covers Force Excitation Functions and Rayleigh Damping*
