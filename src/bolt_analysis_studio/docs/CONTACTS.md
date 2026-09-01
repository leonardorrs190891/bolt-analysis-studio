# Bolt Analysis Studio v4.0 — Contact System Reference

**Source:** `core/contacts/`, `Models/models/Part_II_Contact_Elements.md`, `Part_III_Matrix_Assembly.md`

---

## 1. Contact Class Hierarchy

```
Contact (ABC)  ← core/contacts/base.py
├── ThreadContact          ← core/contacts/thread_contact.py
├── BearingContact         ← core/contacts/bearing_contact.py
│   ├── BearingHeadContact
│   └── BearingNutContact
├── FlangeGasketContact    ← core/contacts/gasket_contact.py
├── FlangeFlangeContact    ← core/contacts/flange_contact.py
└── WasherFlangeContact    ← core/contacts/washer_contact.py
```

---

## 2. Abstract Contact Interface

```python
class Contact(ABC):
    def __init__(self, contact_id, contact_type, node_i, node_j,
                 geometry, friction, wear, stiffness, damping):
        # Identification and connectivity
        # State: normal_force, slip_state, relative_displacement

    @abstractmethod
    def get_stiffness_contribution(self) -> List[Tuple[int, int, float]]:
        """Returns [(row, col, k_value), ...] for [K] matrix"""

    @abstractmethod
    def get_damping_contribution(self) -> List[Tuple[int, int, float]]:
        """Returns [(row, col, c_value), ...] for [C] matrix"""

    @abstractmethod
    def get_force_contribution(self, x, x_dot, t) -> np.ndarray:
        """Returns force vector from friction, wear, plastic effects"""

    def update_state(self, x, x_dot, dt, preload):
        """Updates friction evolution, wear accumulation, internal states"""
```

### Standard Matrix Pattern

For a contact between nodes i and j:

```
[K] contribution:          [C] contribution:          {F} contribution:
     i    j                     i    j                     i
  ┌─────────┐              ┌─────────┐               ┌─────┐
i │ +k  -k  │            i │ +c  -c  │             i │ +F  │
  ├─────────┤              ├─────────┤               ├─────┤
j │ -k  +k  │            j │ -c  +c  │             j │ -F  │
  └─────────┘              └─────────┘               └─────┘
```

---

## 3. Property Dataclasses

### ContactGeometry

```python
@dataclass
class ContactGeometry:
    inner_radius: float    # m — inner contact radius (hole radius)
    outer_radius: float    # m — outer contact radius (under-head or bearing)
    contact_area: float    # m² — net contact area
    thickness: float       # m — contact layer thickness
    roughness_Ra: float    # m — arithmetic mean surface roughness
```

Effective bearing radius (centroid of annular contact):
```
r_eff = (2/3) · (r_o³ − r_i³) / (r_o² − r_i²)
```

### FrictionProperties

```python
@dataclass
class FrictionProperties:
    mu_static: float        # Maximum static friction coefficient
    mu_kinetic: float       # Kinetic (sliding) friction coefficient
    mu_current: float       # Current value (evolves with cycle count)
    v_stribeck: float       # Stribeck transition velocity [m/s]
    stribeck_exp: float     # Stribeck curve exponent
    viscous_coeff: float    # Viscous friction coefficient [N·s/m]
    degradation_rate: float # Friction decay per cycle
    accumulated_slip: float # State tracking [m]
    cycles: int             # Cycle counter
```

### WearProperties

```python
@dataclass
class WearProperties:
    wear_model: WearModel   # ARCHARD, FRETTING, ADHESIVE, ENERGY_BASED
    wear_coeff_K: float     # Archard coefficient (dimensionless/Pa)
    hardness: float         # Surface hardness [Pa]
    fretting_threshold: float  # Min slip amplitude for fretting [m]
    wear_volume: float      # Accumulated wear volume [m³]
    wear_depth: float       # Accumulated wear depth [m]
```

**Archard model:**
```
V = K · F_n · s / H        (wear volume)
h = V / A                  (wear depth)
ΔF_p = k_sys · h           (preload loss)
```

### StiffnessProperties

```python
@dataclass
class StiffnessProperties:
    stiffness_model: StiffnessModel  # LINEAR, NONLINEAR, ELASTOPLASTIC, VISCOELASTIC
    k_axial: float           # Axial stiffness [N/m]
    k_torsional: float       # Torsional stiffness [N·m/rad]
    k_transverse: float      # Transverse stiffness [N/m]
    k_loading: Optional[Callable]    # Nonlinear k(δ) for loading
    k_unloading: Optional[Callable]  # Nonlinear k(δ) for unloading
```

---

## 4. Thread Contact — The Critical Element

### 4.1 Physical Representation

```
INDIVIDUAL THREAD ELEMENTS (n = 8 typical):

Thread 1: [k₁,c₁,μ₁,w₁] ████████████  φ₁ = 19.0%  (highest load)
Thread 2: [k₂,c₂,μ₂,w₂] ██████████    φ₂ = 16.0%
Thread 3: [k₃,c₃,μ₃,w₃] ████████      φ₃ = 13.5%
Thread 4: [k₄,c₄,μ₄,w₄] ██████        φ₄ = 11.4%
Thread 5: [k₅,c₅,μ₅,w₅] █████         φ₅ = 9.6%
Thread 6: [k₆,c₆,μ₆,w₆] ████          φ₆ = 8.1%
Thread 7: [k₇,c₇,μ₇,w₇] ███           φ₇ = 6.8%
Thread 8: [k₈,c₈,μ₈,w₈] ██            φ₈ = 5.7%  (Power Law β=2)
```

Each thread element has INDEPENDENT: stiffness, friction, wear state, slip state, loosening contribution.

### 4.2 Thread Geometry Parameters

| Parameter | Symbol | Formula (ISO Metric) |
|---|---|---|
| Major diameter | d | Input |
| Pitch | p | Input (or from ISO table) |
| Pitch diameter | d₂ | d − 0.6495p |
| Minor diameter | d₁ | d − 1.0825p |
| Helix angle | λ | arctan(p / (π·d₂)) |
| Flank angle (half) | α | 30° (metric) |
| Stress area | A_t | π/4 · ((d₂+d₁)/2)² |

### 4.3 Helix Coupling in [K]

The helical thread geometry creates axial-torsional coupling — the fundamental mechanism of self-loosening:

```
Δx_axial = (p/2π) · Δθ_rotation      (kinematic constraint)

Local stiffness matrix (DOFs: x_nut, θ_stud, θ_nut):

[K_thread] = k_th × | 1      -λ      λ  |   where λ = p/(2π)
                     | -λ     λ²    -λ²  |
                     |  λ    -λ²     λ²  |
```

**Meaning:** When the nut rotates by Δθ_nut, the axial stretch changes by (p/2π)·Δθ_nut. This converts preload into a loosening torque.

### 4.4 Load Distribution Laws

Five models available (`core/load_distribution.py`):

| Model | φ_i Formula | Notes |
|---|---|---|
| Equal | 1/n | Idealized uniform |
| Linear | 2(n−i+1)/(n(n+1)) | Conservative, first thread dominant |
| Power Law | (n−i+1)^β / Σ(j^β) | β=1.5–2.0 typical; used in examples |
| Exponential | e^(−λ(i−1)) / Σ | λ=0.3–0.5; physically motivated |
| Yamamoto | sinh(γ(n−i+0.5)) / Σ | Most accurate; matches FEA |

### 4.5 [K] Contributions from ThreadContact

```
Axial (bolt stiffness):         K[x_stud, x_stud] += k_thread
                                 K[x_nut, x_nut]   += k_thread
                                 K[x_stud, x_nut]  -= k_thread
                                 K[x_nut, x_stud]  -= k_thread

Helix coupling (off-diagonal):   K[x_nut, θ_stud]  += k_thread · (p/2π)
                                 K[θ_stud, x_nut]  += k_thread · (p/2π)
                                 K[θ_nut, x_nut]   -= k_thread · (p/2π)
                                 ...etc (full 3×3 from matrix above)
```

### 4.6 {F} Contributions from ThreadContact

During slip (T_pitch > T_thread):
```
{F}[θ_nut] += −T_pitch + T_thread_friction
            = −F_p·(p/2π) + μ_t·F_p·d₂/(2cosα)
```

When loosening occurs (net torque in back-off direction):
```
Δθ_loosening = C_loosening · (T_net / k_torsional) per cycle
ΔF_preload   = k_bolt · (p/2π) · Δθ_loosening
```

### 4.7 Validation Rule

```
len(ThreadContacts) >= len(Nuts)    MUST be true!
```

Every nut must have at least one ThreadContact. For double-nut (lock nut):
- Bottom nut: Primary ThreadContact (6–10 threads)
- Top nut: Secondary ThreadContact (3–5 threads)

---

## 5. Bearing Contact

### 5.1 BearingHeadContact (Head/Washer or Head/Flange)

**[K] contributions (axial stiffness + torsional coupling):**
```
K[x_head, x_head] += k_c       K[x_head, x_washer] -= k_c
K[x_washer, x_washer] += k_c   K[x_washer, x_head] -= k_c
```

**{F} contributions (bearing friction torque — RESISTS loosening):**
```
T_bearing = μ_b · F_p · r_eff

{F}[θ_stud] += T_bearing    (torque direction opposes loosening)
```

Contact stiffness (Hertz contact theory):
```
k_c = E_eff · A_contact / t_eff
E_eff = 1 / ((1−ν₁²)/E₁ + (1−ν₂²)/E₂)
```

### 5.2 BearingNutContact (Nut/Washer or Nut/Flange)

Symmetric to BearingHeadContact. Torque contribution:
```
{F}[θ_nut] += T_bearing    (opposes loosening at nut end)
```

---

## 6. Washer-Flange Contact

### 6.1 Physics

Models load spreading and embedding between washer and flange face:

**Embedding model (VDI 2230):**
```
δ_embed(N) = f_z · (1 − exp(−N/N_c))
ΔF_embed   = k_sys · δ_embed
```

**[K] contributions:**
```
K[x_washer, x_washer] += k_contact
K[x_flange, x_flange] += k_contact
K[x_washer, x_flange] -= k_contact
K[x_flange, x_washer] -= k_contact
```

**{F} contributions:**
```
{F}[x_washer] += −ΔF_embed(N)    (reduces preload contribution)
{F}[x_flange] += +ΔF_embed(N)
```

### 6.2 Fretting Effects

For repeated micro-slip: activates fretting wear model:
```
h_fretting = K_f · F_n · δ_slip · N / A_contact
```

where δ_slip is the local microslip amplitude.

---

## 7. Flange-Gasket Contact (Nonlinear)

### 7.1 Nonlinear Stiffness

The gasket contact is the only **nonlinear** element in the standard assembly:

```
k_g(δ) = dk_g/dδ    (tangent stiffness, updates at each step)

Loading:   k_g_load(δ) = k₀ · (1 + a·δ)    (stiffening)
Unloading: k_g_unload(δ) = k₀ · (1 + b·δ)  (softer unloading = hysteresis)
```

This produces load-dependent gasket behavior, critical for sealing analysis.

### 7.2 Creep Relaxation

```
δ_creep(t) = δ₀ · C_r · log(1 + t/t_ref)
ΔF_creep   = k_sys · δ_creep(t)
```

Typical creep parameters for spiral wound gaskets:
- C_r = 0.02–0.05 per decade
- t_ref = 1 hour

### 7.3 Plastic Set

After first loading cycle, plastic deformation creates permanent set:
```
δ_plastic = (σ/σ_yield)^n · δ₀
```

### 7.4 [K] Contributions

Updated at each time step due to tangent stiffness:
```
K[x_flange, x_flange] += k_g(δ_current)
K[x_gasket, x_gasket] += k_g(δ_current)
K[x_flange, x_gasket] -= k_g(δ_current)
K[x_gasket, x_flange] -= k_g(δ_current)
```

### 7.5 [C] Contributions (Viscoelastic)

Gasket has higher damping than metallic contacts:
```
C[x_flange, x_flange] += c_visco
C[x_gasket, x_gasket] += c_visco
c_visco = 2·ζ_g · √(k_g · m_g)    ζ_g ≈ 0.05–0.15 for spiral wound
```

---

## 8. Flange-Flange Contact

For metal-to-metal joints (no gasket):

**Characteristics:**
- Very high contact stiffness (k_c ≈ 10⁸–10¹⁰ N/m)
- Low damping (metallic contact)
- Fretting wear at microslip amplitudes (δ < 50 μm)
- Transverse stiffness provides Junker mechanism coupling

**[K] contributions:**
```
Axial:      K[x_fl1, x_fl1] += k_axial    (etc., standard pattern)
Transverse: K[y_fl1, y_fl1] += k_trans    (drives Junker mechanism)
            K[y_fl2, y_fl2] += k_trans
            K[y_fl1, y_fl2] -= k_trans
            K[y_fl2, y_fl1] -= k_trans
```

---

## 9. Complete Contact Map — Typical Flanged Joint

```
                    BOLT HEAD
                        │
         ┌──────────────┼──────────────┐
         │              │              │
    BEARING_HEAD   BEARING_HEAD   HEAD_FLANGE
    (Head-Washer)  (Head-Flange)  (direct, no WS)
         │
      WASHER 1
         │
    WASHER_FLANGE_1
         │
    ═══ FLANGE 1 ═══
         │
    FLANGE_GASKET_1   OR   FLANGE_FLANGE
         │
      GASKET (if present)
         │
    GASKET_FLANGE_2 (symmetric)
    ═══ FLANGE 2 ═══
         │
    WASHER_FLANGE_2
         │
      WASHER 2
         │
    BEARING_NUT
    (Washer-Nut)
         │
       NUT ═══════ STUD ═══════ THREAD_CONTACT
                                (n parallel threads)
                                HELIX COUPLING
```

### DOF Connectivity per Contact (14-DOF system)

| Contact | DOF 1 | DOF 2 | DOF 3 | Stiffness Type |
|---|---|---|---|---|
| BEARING_HEAD | x_bh | x_ws1 | θ_stud | Axial + torsional |
| WASHER_FLANGE_1 | x_ws1 | x_fl1 | — | Axial |
| FLANGE_GASKET_1 | x_fl1 | x_g | — | Nonlinear axial |
| GASKET_FLANGE_2 | x_g | x_fl2 | — | Nonlinear axial |
| WASHER_FLANGE_2 | x_fl2 | x_ws2 | — | Axial |
| BEARING_NUT | x_ws2 | x_nut | θ_nut | Axial + torsional |
| THREAD_CONTACT | x_nut | θ_stud | θ_nut | Axial + helix coupling |
| FLANGE_FLANGE (trans) | y_fl1 | y_fl2 | z_fl1, z_fl2 | Transverse |

---

## 10. Contact Factory

`core/contacts/factory.py` dispatches to the correct contact class:

```python
# Contact type dispatch map
_CONTACT_TYPE_MAP = {
    "THREAD_CONTACT":  ThreadContact,
    "BEARING_HEAD":    BearingContact,
    "BEARING_NUT":     BearingContact,
    "WASHER_FLANGE":   WasherFlangeContact,
    "WASHER_PLAIN":    WasherFlangeContact,
    "WASHER_BELLEVILLE": WasherFlangeContact,
    "WASHER_SPRING":   WasherFlangeContact,
    "WASHER_NORDLOCK": WasherFlangeContact,
    "FLANGE_FLANGE":   FlangeFlangeContact,
    "FLANGE_GASKET":   FlangeGasketContact,
    "HEAD_FLANGE":     BearingContact,
    "NUT_FLANGE":      BearingContact,
}
```

Explicit entries for all washer types were added (BATCH 1, LOW-01 fix) to avoid fragile prefix matching.

---

## 11. Lubrication Models

Stribeck curve with lambda-ratio transitions:

```
Λ = h_c / √(R_q1² + R_q2²)    (specific film thickness)

Λ < 1:   Boundary lubrication    μ = 0.10–0.30
1<Λ<3:   Mixed lubrication       μ = interpolated (logarithmic)
Λ > 3:   Hydrodynamic            μ = 0.001–0.01
```

Lubrication parameters by contact type for standard M16 bolt:

| Lubricant | μ_thread | μ_bearing | Regime |
|---|---|---|---|
| Dry | 0.12–0.18 | 0.12–0.18 | Boundary |
| Oil (mineral) | 0.08–0.12 | 0.08–0.12 | Boundary/Mixed |
| MoS₂ paste | 0.06–0.10 | 0.06–0.10 | Boundary |
| PTFE coating | 0.04–0.08 | 0.04–0.08 | Boundary |
| Zinc-phosphate + oil | 0.10–0.15 | 0.10–0.15 | Boundary |

VDI 2230 recommended range: μ_total = 0.08–0.16 for controlled tightening.

---

## 12. Contact State Update (Per Time Step)

```python
def update_state(self, x: np.ndarray, x_dot: np.ndarray,
                 dt: float, preload: float) -> None:
    # 1. Compute relative displacement and velocity
    delta_u = x[self.dof_j] - x[self.dof_i]
    delta_v = x_dot[self.dof_j] - x_dot[self.dof_i]

    # 2. Update normal force from preload
    self.normal_force = preload * self.load_fraction

    # 3. Determine slip state (Stick/Partial/Gross)
    F_tangential = self.friction.mu_current * self.normal_force
    if abs(delta_v) < self.v_reg:
        self.slip_state = SlipState.STICK
    else:
        self.slip_state = SlipState.GROSS_SLIP

    # 4. Update friction coefficient (three-phase evolution)
    self.friction.cycles += 1
    self.friction.mu_current = self._evolve_friction(self.friction.cycles)

    # 5. Accumulate wear
    if self.slip_state == SlipState.GROSS_SLIP:
        slip_distance = abs(delta_v) * dt
        delta_wear = (self.wear.wear_coeff_K * self.normal_force
                      * slip_distance / self.wear.hardness)
        self.wear.wear_depth += delta_wear / self.geometry.contact_area

    # 6. Update accumulated slip
    self.friction.accumulated_slip += abs(delta_u)
```

---

*Source: `core/contacts/base.py`, `thread_contact.py`, `bearing_contact.py`, `gasket_contact.py`, `flange_contact.py`, `washer_contact.py`*

*Reference: Models/models/Part_II_Contact_Elements.md, Part_III_Matrix_Assembly.md*
