# MSD Framework -- PART XI: COUPLED FRICTION-WEAR-LOOSENING ANALYSIS FRAMEWORK

**Complete Technical Reference for Bolt Analysis Studio**

**Authors:** L. Ribeiro, D. Carvalho, S.C. Naves, T. Santos, V. Marques, G. Arruda
**Institution:** internal reference laboratory
**Project:** Petrobras R&D -- Bolted Flange Joint Integrity

---

**Abstract.** This document presents the coupled friction-wear-loosening analysis framework implemented in the Bolt Analysis Studio (BAS) as the `CoupledLooseningAnalyzer`. Unlike the individual models described in Parts V (Self-Loosening), VI (Wear), and VII (Friction), this framework integrates all three phenomena into a single cycle-by-cycle simulation with full bidirectional coupling. The positive feedback loop -- where friction degradation enables slip, slip causes wear, wear reduces preload, and lower preload reduces friction capacity -- is captured explicitly. The document covers the coupling equations, the phase classification system based on Jiang's two-stage theory, the risk assessment methodology, and the slip detection criteria that trigger the Junker loosening mechanism. All models are presented with physical motivation, governing equations, and practical parameter guidance.

---

## Table of Contents

- [35. Introduction and Motivation](#35-introduction-and-motivation)
- [36. The Positive Feedback Loop](#36-the-positive-feedback-loop)
- [37. Framework Architecture](#37-framework-architecture)
- [38. Friction Evolution Sub-Model](#38-friction-evolution-sub-model)
- [39. Wear Accumulation Sub-Model](#39-wear-accumulation-sub-model)
- [40. Junker Loosening Sub-Model with Slip Detection](#40-junker-loosening-sub-model-with-slip-detection)
- [41. Preload Loss Integration](#41-preload-loss-integration)
- [42. Phase Classification System](#42-phase-classification-system)
- [43. Risk Assessment Methodology](#43-risk-assessment-methodology)
- [44. Critical Friction Coefficient](#44-critical-friction-coefficient)
- [45. Complete Cycle Update Algorithm](#45-complete-cycle-update-algorithm)
- [46. Parameter Selection Guide](#46-parameter-selection-guide)
- [47. Validation Against Experimental Data](#47-validation-against-experimental-data)
- [References](#references)

---

## 35. Introduction and Motivation

### 35.1 Why Coupled Analysis Is Necessary

The individual models for friction (Part VII), wear (Part VI), and self-loosening (Part V) each describe important aspects of bolted joint behavior. However, when applied independently, they fail to capture a critical feature of real joint behavior: **the mutual interaction between these phenomena creates a self-reinforcing degradation path**.

Consider a bolted flange joint subjected to transverse vibration in subsea service. Initially, the joint is well preloaded and the friction coefficients are sufficient to prevent loosening. Over hundreds of cycles, however:

1. The friction coefficient evolves (running-in, then degradation) as described by Hintikka et al. (2020).
2. Cyclic slip causes wear at the thread and bearing surfaces, following Archard's law (Archard, 1953) or energy-based models (Fouvry et al., 2003).
3. Wear removes material, reducing the effective clamped length and hence the preload through the system stiffness: $\Delta F_p = k_{sys} \times h_{wear}$.
4. Lower preload reduces the friction capacity $\mu \times F_p$ at all interfaces, making it easier for transverse forces to overcome friction.
5. Easier slip leads to more wear, which leads to more preload loss, which leads to easier slip...

This positive feedback loop means that a joint which is initially safe (with comfortable torque margin) can transition to a loosening state much faster than any individual model would predict. The coupled analysis framework captures this interaction explicitly.

### 35.2 Relationship to Prior Parts

This Part XI integrates models from three prior documents:

| Part | Models Used | Role in Coupled Framework |
|------|------------|--------------------------|
| **Part V** (Self-Loosening) | Junker mechanism, Jiang two-stage model, torque balance | Loosening angle computation, phase classification |
| **Part VI** (Wear) | Archard law, Fouvry energy model, wear evolution | Wear accumulation and preload loss |
| **Part VII** (Friction) | Three-phase evolution (Hintikka), Coulomb, Stribeck | Friction coefficient updates per cycle |

The coupled framework adds:

- **Bidirectional coupling equations** between all three phenomena
- **Slip detection** criteria for triggering the Junker mechanism
- **Phase classification** (STABLE through RUNAWAY) based on multiple indicators
- **Risk assessment** based on torque margin
- **Critical friction** computation for design against loosening

### 35.3 Historical Development

The recognition that friction, wear, and loosening are coupled phenomena evolved gradually in the literature:

- **Junker (1969)** established the fundamental loosening mechanism but assumed constant friction.
- **Pai and Hess (2002)** introduced the concept of localized slip at thread contacts and showed that non-uniform friction distribution affects loosening.
- **Jiang et al. (2003, 2004)** proposed the two-stage model distinguishing material loosening (Stage I, plastic deformation) from structural loosening (Stage II, rotational back-off), providing the first framework for multi-mechanism interaction.
- **Nassar and Housari (2006, 2007)** at Oakland University studied the effects of thread and bearing friction independently and quantified their relative contributions to loosening resistance.
- **Hintikka et al. (2020)** provided detailed friction evolution data under fretting conditions relevant to bolt contact surfaces, establishing the three-phase friction model used in BAS.
- **Yang et al. (2019)** quantified the displacement amplitude effect on loosening rate, showing a power-law dependence that is incorporated in the S-curve model.

The BAS `CoupledLooseningAnalyzer` synthesizes all of these contributions into a unified computational framework.

---

## 36. The Positive Feedback Loop

### 36.1 Feedback Diagram

The core of the coupled analysis is the positive feedback loop between friction, wear, preload, and loosening:

```
    ┌──────────────────────────────────────────────────────────────────┐
    │                                                                  │
    │         POSITIVE FEEDBACK LOOP IN BOLTED JOINT LOOSENING        │
    │                                                                  │
    │   ┌──────────────┐     Wear degrades      ┌──────────────┐     │
    │   │   FRICTION    │     friction surface    │     WEAR     │     │
    │   │   mu(N,v,T)   │ ──────────────────────► │   h(N,F,s)  │     │
    │   │               │                         │              │     │
    │   │               │ ◄────────────────────── │              │     │
    │   └──────┬────────┘     Friction drives     └──────┬───────┘     │
    │          │              wear energy                 │             │
    │          │                                         │             │
    │          │ Lower friction                          │ Wear        │
    │          │ reduces resistance                      │ removes     │
    │          │ to loosening                            │ material    │
    │          │                                         │             │
    │          ▼                                         ▼             │
    │   ┌──────────────┐                         ┌──────────────┐     │
    │   │  LOOSENING    │     Lower preload       │   PRELOAD    │     │
    │   │  theta(N)     │ ◄────────────────────── │   F_p(N)     │     │
    │   │               │     reduces friction    │              │     │
    │   │               │     capacity            │              │     │
    │   └──────┬────────┘                         └──────▲───────┘     │
    │          │                                         │             │
    │          │ Rotation reduces                        │             │
    │          │ preload via helix                       │             │
    │          │                                         │             │
    │          └─────────────────────────────────────────┘             │
    │                 Delta_F = k_bolt × (p/2pi) × theta              │
    │                                                                  │
    └──────────────────────────────────────────────────────────────────┘
```

### 36.2 Quantifying the Coupling

Each coupling pathway has a specific mathematical expression:

**Friction → Wear (via energy dissipation):**

$$E_{diss} = \mu \cdot F_n \cdot v \cdot dt$$

The frictional energy dissipated at the contact interface drives the Fouvry energy-based wear model. Higher friction produces more dissipated energy and hence more wear.

**Wear → Preload (via system compliance):**

$$\Delta F_{p,wear} = k_{sys} \cdot (h_{thread} + h_{bearing})$$

where $k_{sys} = k_b \cdot k_m / (k_b + k_m)$ is the equivalent series stiffness of bolt and clamped members.

**Preload → Friction capacity (via normal force):**

$$F_{friction,max} = \mu \cdot F_p(N)$$

As preload decreases, the maximum friction force available to resist transverse sliding decreases proportionally.

**Loosening → Preload (via helix kinematics):**

$$\Delta F_{p,rot} = k_b \cdot \frac{p}{2\pi} \cdot \theta_{loosening}$$

Each increment of nut rotation $\theta$ translates to a preload loss through the helix coupling factor $p/(2\pi)$.

**Wear → Friction (via surface condition):**

$$\mu_{effective} = \mu_{base} - \alpha_{wear} \cdot h_{wear}$$

where $\alpha_{wear}$ is the wear-induced friction degradation rate (typically 0.01 per micrometer of wear depth). Wear roughens or smoothens the surface, affecting friction.

### 36.3 Time Scales of the Coupling

The different coupling mechanisms operate on different time scales:

| Coupling | Time Scale | Character |
|----------|-----------|-----------|
| Friction evolution (running-in) | 50--200 cycles | Transient, may increase $\mu$ |
| Embedding (Stage I preload loss) | 10--200 cycles | Exponential saturation |
| Wear accumulation | 100--10,000 cycles | Gradual, accelerating |
| Rotational loosening | 200--5,000 cycles | Linear to accelerating |
| Friction degradation from wear | 1,000--100,000 cycles | Slow, cumulative |

The staggered time scales mean that the coupled behavior is qualitatively different from any single mechanism: the early response is dominated by embedding and friction running-in, the mid-life by wear accumulation and friction degradation, and the late life by rotational loosening and the positive feedback loop.

---

## 37. Framework Architecture

### 37.1 Software Architecture

The `CoupledLooseningAnalyzer` class encapsulates all coupled models:

```python
class CoupledLooseningAnalyzer:
    """
    Integrates friction evolution, wear accumulation, and loosening
    into a unified cycle-by-cycle analysis framework.
    """

    def __init__(self,
                 thread_geometry: ThreadGeometryParams,      # Thread p, d2, alpha, n
                 bearing_geometry: BearingGeometryParams,    # Under-head/nut dimensions
                 friction_params: FrictionEvolutionParams,   # Three-phase friction model
                 wear_params: WearModelParams,               # Archard + Fouvry parameters
                 two_stage_params: TwoStageLooseningParams,  # Jiang/Yang S-curve
                 k_bolt: float,                              # Bolt stiffness [N/m]
                 k_member: float,                            # Member stiffness [N/m]
                 transverse_displacement_mm: float):         # Excitation amplitude [mm]
```

### 37.2 Data Flow Per Cycle

At each cycle $N$, the analyzer executes the following sequence:

```
    CYCLE N INPUT: preload F_p(N-1), F_transverse, temperature T
    ───────────────────────────────────────────────────────────────

    STEP 1: UPDATE FRICTION
    │   mu_thread(N) = FrictionEvolution(N, wear_depth, T)
    │   mu_bearing(N) = FrictionEvolution(N, wear_depth, T)
    ▼
    STEP 2: CHECK SLIP CONDITIONS
    │   bearing_slip = |F_trans| > mu_bearing × F_p ?
    │   thread_slip  = |F_trans| > mu_thread × F_p × cos(lambda) ?
    ▼
    STEP 3: COMPUTE TORQUE BALANCE
    │   T_pitch     = F_p × p / (2*pi)
    │   T_thread    = mu_t × F_p × d2 / (2*cos(alpha))
    │   T_bearing   = mu_b × F_p × r_eff
    │   margin      = (T_thread + T_bearing) / T_pitch
    ▼
    STEP 4: COMPUTE WEAR (if slipping)
    │   dh_thread  = Archard + Fouvry at thread contacts
    │   dh_bearing = Archard + Fouvry at bearing surface
    │   h_total(N) = h_total(N-1) + dh_thread + dh_bearing
    ▼
    STEP 5: COMPUTE LOOSENING ANGLE (if both surfaces slip)
    │   IF junker_active (both slipping):
    │       d_theta = C × (slip_amp/d2) × (1 + excess_ratio) × (p/d2)
    │   ELSE IF partial_slip:
    │       d_theta ≈ small micro-rotation
    │   theta(N) = theta(N-1) + d_theta
    ▼
    STEP 6: COMPUTE PRELOAD
    │   loss_rotational = k_bolt × (p/2pi) × theta
    │   loss_wear       = k_sys × h_total
    │   loss_scurve     = TwoStageModel(N, displacement) × F_p0
    │   F_p(N) = F_p0 - max(physics_loss, 0.8 × empirical_loss)
    ▼
    STEP 7: CLASSIFY PHASE AND RISK
    │   phase = classify(preload_ratio, margin, rate, cycle)
    │   risk  = classify(margin)
    ▼
    OUTPUT: LooseningState(N) with all quantities
```

---

## 38. Friction Evolution Sub-Model

### 38.1 Three-Phase Model

The friction evolution follows the Hintikka et al. (2020) three-phase model, extended with wear and temperature degradation:

$$\mu(N, h, T) = \mu_{base}(N) - \alpha_{wear} \cdot h - \alpha_{temp} \cdot \max(0, T - T_{ref})$$

where the base friction follows a three-phase trajectory:

$$\mu_{base}(N) = \mu_0 + \underbrace{(\mu_{peak} - \mu_0)(1 - e^{-N/N_1}) \cdot e^{-N/N_2}}_{\text{Phase 1: Running-in rise and decay}} + \underbrace{(\mu_{ss} - \mu_0)(1 - e^{-N/N_3})}_{\text{Phase 2-3: Steady-state approach}}$$

**Physical interpretation of the three phases:**

**Phase 1 -- Running-in (0 to $\sim N_1$ cycles):** When two freshly machined surfaces first slide against each other, the initial contact occurs at asperity peaks. These asperities deform plastically, increasing the real contact area and temporarily *increasing* the friction coefficient from $\mu_0$ toward $\mu_{peak}$. This is the "running-in" period observed in tribological testing (Blau, 2005).

**Phase 2 -- Transition ($N_1$ to $\sim N_2$ cycles):** After the initial asperities have been removed, the surface roughness decreases and wear debris may act as third-body lubricant. The friction coefficient decreases from $\mu_{peak}$ back down. The exponential decay term $e^{-N/N_2}$ captures this transition.

**Phase 3 -- Steady state ($N > N_3$):** Eventually, the friction stabilizes at $\mu_{ss}$, which may be below the initial value if significant surface conditioning has occurred. The time constant $N_3$ is typically much larger than $N_1$ or $N_2$.

### 38.2 Default Parameters

| Parameter | Symbol | Default | Range | Physical Basis |
|-----------|--------|---------|-------|----------------|
| Initial friction | $\mu_0$ | 0.15 | 0.08--0.25 | Depends on surface treatment and lubrication |
| Peak friction | $\mu_{peak}$ | 0.18 | $\mu_0$ to $1.5\mu_0$ | Running-in increase (Hintikka et al., 2020) |
| Steady-state friction | $\mu_{ss}$ | 0.10 | 0.05--0.20 | Long-term stabilized value |
| Minimum friction | $\mu_{min}$ | 0.03 | 0.02--0.05 | Physical lower bound for metal contact |
| Running-in cycles | $N_1$ | 50 | 20--200 | Asperity removal duration |
| Transition cycles | $N_2$ | 200 | 100--1000 | Peak decay time |
| Steady-state cycles | $N_3$ | 2000 | 500--10,000 | Long-term stabilization |
| Wear degradation rate | $\alpha_{wear}$ | 0.01 $\mu m^{-1}$ | 0.005--0.05 | Surface condition effect |
| Temperature factor | $\alpha_{temp}$ | 0.001 $°C^{-1}$ | 0.0005--0.005 | Lubricant thinning, oxide growth |

### 38.3 Effect of Lubrication

The BAS interface allows specifying "lubricated" or "dry" conditions, which affect the friction parameters:

| Condition | $\mu_0$ | $\mu_{peak}$ | $\mu_{ss}$ | Character |
|-----------|---------|-------------|-----------|-----------|
| Dry (unlubricated) | 0.20--0.25 | 0.25--0.35 | 0.15--0.20 | Higher friction but more variable |
| MoS$_2$ lubricated | 0.10--0.15 | 0.12--0.18 | 0.08--0.12 | Lower, more stable friction |
| PTFE coated | 0.08--0.12 | 0.10--0.14 | 0.06--0.10 | Lowest friction, risk of too-low retention |
| Anti-seize paste | 0.12--0.16 | 0.14--0.18 | 0.10--0.14 | Good compromise for most applications |

**Design consideration:** Very low friction (e.g., PTFE coating with $\mu < 0.08$) may actually *promote* loosening by reducing the friction resistance below the pitch torque threshold. This is a well-known design paradox discussed by Bickford (2008): lubricants that make assembly easier also make loosening easier.

---

## 39. Wear Accumulation Sub-Model

### 39.1 Multi-Mechanism Wear Model

The wear sub-model combines Archard mechanical wear with Fouvry energy-based wear:

**Archard component (Archard, 1953):**

$$dV_{Archard} = \frac{K \cdot F_n \cdot s}{H}$$

$$dh_{Archard} = \frac{dV_{Archard}}{A_c}$$

where $K$ is the dimensionless wear coefficient, $F_n$ is the normal contact force, $s$ is the sliding distance per cycle, $H$ is the surface hardness, and $A_c$ is the nominal contact area.

**Fouvry energy component (Fouvry et al., 2003):**

$$E_{diss} = \mu \cdot F_n \cdot s$$

$$dV_{Fouvry} = \alpha_E \cdot E_{diss}$$

$$dh_{Fouvry} = \frac{dV_{Fouvry}}{A_c}$$

where $\alpha_E$ is the energy wear coefficient (m$^3$/J).

**Combined wear increment:**

$$dh_{total} = \max(dh_{Archard},\ 0.5 \cdot dh_{Fouvry}) + 0.3 \cdot dh_{Fouvry}$$

This blending formula ensures that the dominant mechanism controls the wear rate while the secondary mechanism provides an additive contribution. The factors (0.5 and 0.3) reflect the fact that the two mechanisms are not fully independent -- they share the same frictional energy input.

### 39.2 Time-Varying Wear Coefficient

The wear coefficient $K$ is not constant but evolves with cycle count and accumulated wear depth through four distinct phases:

```
K(N, h)
  |
  |  Phase 1: Running-in        Phase 2: Steady        Phase 3: Severe    Phase 4: Catastrophic
  |  (asperity removal)         (constant K)           (damage)           (failure)
  |
  |  K_running_in = 5e-6                                K_severe = 1e-5    K_cat = 5e-5
  |  ●━━━━━━━━━━━━━━━━┓
  |                     ┃
  |                     ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━●
  |                     K_steady = 1e-6              ┃
  |                                                   ┗━━━━━━━━━━●
  |                                                               ┃
  |                                                                ┗━━━●
  |
  └──────────────────────────────────────────────────────────────────────────►
     0          100              500            h=50um           h=100um
                                cycles          wear depth thresholds
```

**Phase transitions:**

1. **Running-in → Steady-state** is cycle-based (0--100 cycles) with an S-curve smoothing function: $K(N) = K_{run} - (K_{run} - K_{ss}) \cdot [3p^2 - 2p^3]$ where $p = N/N_{run}$.

2. **Steady-state → Severe** is wear-depth-triggered: when $h > 50\ \mu m$, the surface has lost its protective layers and wear accelerates.

3. **Severe → Catastrophic** occurs at $h > 100\ \mu m$, representing near-failure conditions where surface integrity is compromised.

### 39.3 Temperature Correction

Hardness decreases with temperature, which increases the wear rate:

$$H_{eff}(T) = H_0 \cdot \max\left(0.3,\ 1 - \beta_H \cdot (T - T_{ref})\right)$$

The factor of 0.3 caps the hardness reduction at 70% to prevent unphysical behavior.

### 39.4 Fretting Enhancement

When the slip amplitude is small (below the gross-slip threshold), the damage per unit of sliding distance is actually *higher* than in gross slip. This is the fretting regime, well documented by McColl et al. (2004) and Fouvry et al. (2003). The BAS implementation applies a fretting enhancement factor of 1.5 when the slip amplitude is below $10 \times$ the fretting threshold.

---

## 40. Junker Loosening Sub-Model with Slip Detection

### 40.1 Slip Detection Criteria

The Junker loosening mechanism (Junker, 1969) requires simultaneous slip at both the bearing and thread surfaces. The BAS framework checks two independent conditions:

**Bearing surface slip:**

$$|F_{trans}| > \mu_b \cdot F_p \quad \Rightarrow \quad \text{bearing slipping}$$

**Thread surface slip:**

$$|F_{trans}| > \mu_t \cdot F_p \cdot \cos(\lambda) \quad \Rightarrow \quad \text{thread slipping}$$

where $\lambda$ is the helix angle. The $\cos(\lambda)$ factor accounts for the thread geometry -- the thread friction force has a component along the helix direction that is not available for resisting transverse motion.

**Three slip states:**

| State | Bearing | Thread | Consequence |
|-------|---------|--------|-------------|
| No slip | Stuck | Stuck | Stable joint, no loosening |
| Partial slip | Slipping | Stuck | Micro-rotation, very slow loosening |
| Full slip (Junker active) | Slipping | Slipping | Rotational loosening active |

### 40.2 Loosening Angle per Cycle

When both surfaces are slipping (Junker active), the rotation per cycle is computed from:

$$\Delta\theta = C_{loosen} \cdot \frac{\delta_{slip}}{d_2} \cdot (1 + r_{excess}) \cdot \frac{p}{d_2}$$

where:

- $C_{loosen} \approx 0.3$ is an empirical calibration constant (calibrated to match Junker test data showing 10--50% preload loss over 1000 cycles for M16 bolts)
- $\delta_{slip}$ is the estimated slip amplitude at the bearing surface
- $d_2$ is the pitch diameter
- $r_{excess} = (|F_{trans}| - \mu_{min} \cdot F_p) / (\mu_{min} \cdot F_p)$ is the excess force ratio
- $p$ is the thread pitch

**Physical interpretation:** The ratio $\delta_{slip}/d_2$ represents the angular displacement scale at the bearing surface. The term $(1 + r_{excess})$ amplifies the rotation when the transverse force significantly exceeds the friction capacity. The factor $p/d_2$ captures the geometric relationship between rotation and axial travel on the helix.

**Bounds:**

$$\Delta\theta \leq 0.1 \text{ rad/cycle} \quad (\approx 6°/\text{cycle, extreme maximum})$$

$$\Delta\theta \leftarrow \Delta\theta \cdot \frac{F_p}{F_{p,0}} \quad \text{(diminishing effect as preload drops)}$$

### 40.3 Partial Slip Regime

When only the bearing surface slips (but the thread is still stuck), a very small rotation can still occur due to elastic deformation at the thread-nut interface:

$$\Delta\theta_{partial} = 10^{-4} \cdot \frac{|F_{trans}| - \mu_b \cdot F_p}{F_p + \epsilon}$$

This contribution is capped at 0.001 rad/cycle and represents the transition regime between fully stable and fully loosening behavior.

### 40.4 Static Loosening

In rare cases where the torque margin is below 1.0 even without transverse loading (i.e., friction is so low that the pitch torque exceeds the friction resistance), the nut will rotate even without transverse excitation:

$$\Delta\theta_{static} = (1 - \text{margin}) \cdot 10^{-3} \quad \text{rad/cycle}$$

This condition occurs when $\mu < \mu_{crit}$ (see Section 44).

---

## 41. Preload Loss Integration

### 41.1 Physics-Based Loss Components

The total preload loss at cycle $N$ is computed from three physical mechanisms:

**Rotational loosening (helix kinematics):**

$$\Delta F_{rot}(N) = k_b \cdot \frac{p}{2\pi} \cdot \theta(N)$$

where $\theta(N) = \sum_{i=1}^{N} \Delta\theta_i$ is the accumulated loosening angle.

**Wear-induced loss (system compliance):**

$$\Delta F_{wear}(N) = k_{sys} \cdot h_{total}(N)$$

where $h_{total} = h_{thread} + h_{bearing}$ is the total wear depth across all interfaces.

### 41.2 Empirical S-Curve Model (Jiang/Yang)

In parallel with the physics-based calculation, the Two-Stage S-Curve model provides an empirical prediction based on Jiang et al. (2003) and Yang et al. (2019):

**Stage I (plastic deformation, $N < N_{stage1}$):**

$$\Delta F_{I}(N) = \delta_{F1} \cdot F_{p,0} \cdot \left(1 - e^{-N/N_1^{eff}}\right)$$

**Stage II (rotational loosening, $N > N_{stage1}$):**

$$\Delta F_{II}(N) = k_{stage2} \cdot f_{disp} \cdot (N - N_{stage1}^{eff}) \cdot \sigma(N)$$

where:
- $N_1^{eff} = N_{stage1} / f_{disp}$ is the effective Stage I duration (shorter for larger displacement)
- $f_{disp} = (\delta_{mm} / 0.65)^{n_{disp}}$ is the displacement factor (Yang et al., 2019)
- $n_{disp} = 2.0$ is the displacement exponent
- $\sigma(N) = 1/(1 + e^{-\beta(N - N_1^{eff})/N_1^{eff}})$ is a sigmoid transition function

### 41.3 Combined Loss Model

The final preload is computed by blending the physics-based and empirical models:

$$F_p(N) = F_{p,0} - \max\left(\Delta F_{physics},\ 0.8 \cdot \Delta F_{scurve}\right) - \min\left(\Delta F_{physics},\ 0.2 \cdot \Delta F_{scurve}\right)$$

This blending ensures:
- When the physics model predicts more loss than the S-curve (e.g., during rapid rotational loosening), the physics model dominates.
- When the S-curve predicts more loss (e.g., during early embedding that the simplified physics model may underestimate), the empirical model contributes.
- The joint always takes the more conservative prediction as the baseline.

---

## 42. Phase Classification System

### 42.1 Jiang Two-Stage Framework

The loosening process is classified into five phases, extending Jiang et al.'s (2003) original two-stage model with engineering-relevant boundary states:

```
                                LOOSENING PHASE PROGRESSION
    ─────────────────────────────────────────────────────────────────────►

    STABLE          NON_ROTATIONAL       TRANSITION        ROTATIONAL         RUNAWAY
    ┌──────────┐    ┌──────────────┐    ┌────────────┐    ┌────────────┐    ┌──────────┐
    │ F_p/F_0  │    │ Jiang        │    │ Margin     │    │ Junker     │    │ Near-    │
    │ > 98%    │    │ Stage I      │    │ eroding    │    │ mechanism  │    │ failure  │
    │ margin   │    │ Plastic      │    │ Approaching│    │ Active     │    │ F_p/F_0  │
    │ > 1.3    │    │ deformation  │    │ critical   │    │ rotation   │    │ < 50%    │
    │ cycle<10 │    │ No rotation  │    │ friction   │    │ margin<1.0 │    │ or rate  │
    │          │    │ N < 1.5×N_s1 │    │            │    │ Both slip  │    │ > 0.003  │
    └──────────┘    └──────────────┘    └────────────┘    └────────────┘    │ deg/cyc  │
                                                                            └──────────┘

    Typical                                                                 Typical
    N=0-10          N=10-300             N=300-500         N=500-5000       N>5000
    (varies with loading, friction, and geometry)
```

### 42.2 Classification Criteria

The classification uses multiple indicators to ensure robustness:

| Phase | Preload Ratio | Cycle Count | Torque Margin | Loosening Rate | Slip State |
|-------|--------------|-------------|---------------|----------------|------------|
| **STABLE** | > 0.98 | < 10 | > 1.3 | $\approx 0$ | No slip |
| **NON_ROTATIONAL** | > 0.85 × (1 - $\delta_{F1}$) | < 1.5 × $N_{s1}$ | > 1.0 | Very small | Partial or no slip |
| **TRANSITION** | 0.70--0.98 | > 0.5 × $N_{s1}$ | < 1.3 | Increasing | -- |
| **ROTATIONAL** | 0.50--0.70 | -- | $\leq$ 1.0 | Significant | Both slip |
| **RUNAWAY** | < 0.50 | -- | < 0.8 | > 0.003 deg/cyc | Both slip |

### 42.3 Classification Logic

The algorithm applies criteria in order of severity (most severe first):

1. **STABLE** is checked first (very conservative -- requires high preload, low cycle count, high margin).
2. **NON_ROTATIONAL** is checked for early cycles within Stage I parameters.
3. **RUNAWAY** is checked before ROTATIONAL to catch critical states early.
4. **ROTATIONAL** requires evidence of active Junker mechanism (both surfaces slipping) or measurable rotation rate.
5. **TRANSITION** is the default for states that don't fit other categories but show some degradation.
6. A **fallback** based purely on preload ratio ensures every state is classified.

### 42.4 Relationship to VDI 2230

The phase classification maps to VDI 2230 safety factor assessment as follows:

| Phase | VDI 2230 Equivalent | Engineering Action |
|-------|--------------------|--------------------|
| STABLE | Adequate safety factor | No action needed |
| NON_ROTATIONAL | Within design allowance (embedding) | Monitor, may be acceptable |
| TRANSITION | Marginal safety factor | Re-evaluate design |
| ROTATIONAL | Below minimum safety factor | Immediate corrective action |
| RUNAWAY | Joint failure imminent | Emergency shutdown |

---

## 43. Risk Assessment Methodology

### 43.1 Torque Margin Definition

The primary risk metric is the **torque margin**, defined as the ratio of friction-based resistance torque to the helix-driven pitch torque:

$$\text{Margin} = \frac{T_{thread} + T_{bearing}}{T_{pitch}} = \frac{\mu_t \cdot F_p \cdot d_2 / (2\cos\alpha) + \mu_b \cdot F_p \cdot r_{eff}}{F_p \cdot p / (2\pi)}$$

Note that $F_p$ cancels, giving:

$$\text{Margin} = \frac{\mu_t \cdot d_2 / (2\cos\alpha) + \mu_b \cdot r_{eff}}{p / (2\pi)}$$

This means the torque margin depends on **friction coefficients and geometry only**, not on preload magnitude. However, preload affects whether slip occurs (which reduces effective friction), so in practice the margin varies with preload through the friction evolution.

### 43.2 Risk Levels

| Risk Level | Torque Margin | Physical Meaning |
|------------|--------------|------------------|
| **NEGLIGIBLE** | > 2.0 | Friction resistance is more than double the pitch torque |
| **LOW** | 1.5--2.0 | Comfortable margin, typical for well-designed joints |
| **MODERATE** | 1.1--1.5 | Margin is positive but limited; sensitive to friction changes |
| **HIGH** | 1.0--1.1 | Barely stable; any friction reduction triggers loosening |
| **CRITICAL** | < 1.0 | **Loosening is thermodynamically inevitable** |

### 43.3 Design Recommendation

For API 6A and similar safety-critical applications, the recommended minimum torque margin is:

$$\text{Margin}_{design} \geq 1.5$$

This provides a safety factor of 1.5 against loosening and accommodates:
- $\pm$ 20% uncertainty in friction coefficient
- Moderate wear over service life
- Temperature effects up to 200°C above ambient

---

## 44. Critical Friction Coefficient

### 44.1 Derivation

The critical friction coefficient $\mu_{crit}$ is the value below which the pitch torque exceeds the combined friction resistance, making loosening inevitable regardless of preload level:

Setting $T_{pitch} = T_{thread} + T_{bearing}$ with $\mu_t = \mu_b = \mu_{crit}$:

$$F_p \cdot \frac{p}{2\pi} = \mu_{crit} \cdot F_p \cdot \frac{d_2}{2\cos\alpha} + \mu_{crit} \cdot F_p \cdot r_{eff}$$

Canceling $F_p$:

$$\frac{p}{2\pi} = \mu_{crit} \left(\frac{d_2}{2\cos\alpha} + r_{eff}\right)$$

$$\boxed{\mu_{crit} = \frac{p \cdot \cos\alpha}{\pi \cdot d_2 + 2\pi \cdot r_{eff} \cdot \cos\alpha} = \frac{p/(2\pi) \cdot 2\cos\alpha}{d_2 + 2 \cdot r_{eff} \cdot \cos\alpha}}$$

### 44.2 Typical Values

For common metric bolt sizes:

| Bolt Size | Pitch $p$ (mm) | $d_2$ (mm) | $r_{eff}$ (mm) | $\mu_{crit}$ |
|-----------|---------------|-----------|-------------|-------------|
| M8 | 1.25 | 7.188 | 5.5 | 0.020 |
| M12 | 1.75 | 10.863 | 7.5 | 0.019 |
| M16 | 2.00 | 14.701 | 10.25 | 0.016 |
| M20 | 2.50 | 18.376 | 12.75 | 0.016 |
| M24 | 3.00 | 22.051 | 15.25 | 0.016 |
| M36 | 4.00 | 33.402 | 22.75 | 0.015 |

**Key insight:** For standard metric bolts, $\mu_{crit}$ is remarkably low (0.015--0.020), meaning that virtually any normal metal-on-metal contact has sufficient friction to resist loosening *in the absence of transverse slip*. The Junker mechanism works not by reducing the overall friction coefficient to below $\mu_{crit}$, but by momentarily eliminating the *effective* friction resistance during transverse slip events.

### 44.3 Friction Margin

The **friction margin** quantifies how far the current average friction is above the critical value:

$$\text{Friction Margin} = \frac{(\mu_t + \mu_b)/2}{\mu_{crit}}$$

For a well-lubricated joint with $\mu = 0.12$ and $\mu_{crit} = 0.016$, the friction margin is $0.12/0.016 = 7.5$. This large margin explains why loosening requires transverse slip -- simply reducing friction (by lubrication, wear, or temperature) is unlikely to push the coefficient below $\mu_{crit}$.

---

## 45. Complete Cycle Update Algorithm

### 45.1 Pseudocode

```
ALGORITHM: Coupled Loosening - Single Cycle Update
════════════════════════════════════════════════════

INPUT:
  cycle N, preload F_p(N-1), F_transverse, temperature T
  previous state: theta(N-1), h_thread(N-1), h_bearing(N-1)

PARAMETERS:
  ThreadGeometry: p, d2, alpha, r_m
  BearingGeometry: r_inner, r_outer -> r_eff
  FrictionParams: mu_0, mu_peak, mu_ss, N1, N2, N3, alpha_wear, alpha_temp
  WearParams: K_archard, H, A_c, alpha_energy, phase thresholds
  TwoStageParams: N_stage1, delta_F1, k_stage2, disp_exponent
  k_bolt, k_member -> k_sys = k_b*k_m/(k_b+k_m)

OUTPUT:
  LooseningState at cycle N

BEGIN:

  // Step 1: Friction update
  avg_wear_um = (h_thread(N-1) + h_bearing(N-1)) * 1e6 / 2
  mu_thread = FrictionEvolution(N, avg_wear_um, T)
  mu_bearing = FrictionEvolution(N, avg_wear_um, T)

  // Step 2: Slip detection
  bearing_slipping = |F_trans| > mu_bearing * F_p(N-1)
  thread_capacity = mu_thread * F_p(N-1) * cos(helix_angle)
  thread_slipping = |F_trans| > thread_capacity
  junker_active = bearing_slipping AND thread_slipping

  // Step 3: Torque balance
  T_pitch = F_p(N-1) * p / (2*pi)
  T_thread = mu_thread * F_p(N-1) * d2 / (2*cos(alpha))
  T_bearing = mu_bearing * F_p(N-1) * r_eff
  T_resistance = T_thread + T_bearing
  margin = T_resistance / T_pitch

  // Step 4: Wear computation
  IF bearing_slipping:
    slip_dist = compute_slip_distance(F_trans, F_p, mu_bearing)
    dh_thread = WearModel(F_p, 0.5*slip_dist, N, h_thread, T, mu_thread)
    dh_bearing = WearModel(F_p, slip_dist, N, h_bearing, T, mu_bearing)
    h_thread(N) = h_thread(N-1) + dh_thread
    h_bearing(N) = h_bearing(N-1) + dh_bearing
  ELSE:
    h_thread(N) = h_thread(N-1)
    h_bearing(N) = h_bearing(N-1)

  // Step 5: Loosening angle
  IF junker_active:
    excess = |F_trans| - min(mu_b*F_p, mu_t*F_p*cos(lambda))
    excess_ratio = excess / (min_capacity + eps)
    slip_amp = excess / (0.3*k_sys + eps)
    d_theta = 0.3 * (slip_amp/d2) * (1 + excess_ratio) * (p/d2)
    d_theta = min(d_theta, 0.1)           // Cap at 6 deg/cycle
    d_theta *= F_p(N-1) / F_p(0)          // Preload diminishing effect
  ELIF bearing_slipping:
    d_theta = 1e-4 * excess / (F_p + eps)  // Partial slip
    d_theta = min(d_theta, 0.001)
  ELIF margin < 1.0:
    d_theta = (1 - margin) * 1e-3         // Static loosening
  ELSE:
    d_theta = 0

  theta(N) = theta(N-1) + d_theta

  // Step 6: Preload computation
  loss_rot = k_bolt * (p/(2*pi)) * theta(N)
  loss_wear = k_sys * (h_thread(N) + h_bearing(N))
  physics_loss = loss_rot + loss_wear

  scurve_factor = TwoStageModel(N, disp_mm)
  empirical_loss = scurve_factor * F_p(0)

  total_loss = max(physics_loss, 0.8*empirical_loss) + min(physics_loss, 0.2*empirical_loss)
  F_p(N) = max(0, F_p(0) - total_loss)

  // Step 7: Classification
  phase = classify_phase(F_p(N)/F_p(0), margin, d_theta, N)
  risk = classify_risk(margin)

  RETURN LooseningState(N)
END
```

---

## 46. Parameter Selection Guide

### 46.1 By Application

| Application | $\mu_0$ | $K_{wear}$ | $N_{stage1}$ | Notes |
|------------|---------|-----------|------------|-------|
| API 6A flanged connection (subsea) | 0.12--0.16 | 1--5 $\times 10^{-6}$ | 100--300 | Anti-seize paste typical |
| ASME B16.5 with spiral wound gasket | 0.10--0.14 | 0.5--2 $\times 10^{-6}$ | 200--500 | Gasket creep dominates |
| Wind turbine tower flange | 0.14--0.20 | 2--10 $\times 10^{-6}$ | 50--200 | Outdoor, variable conditions |
| Automotive engine head bolt | 0.08--0.12 | 0.1--1 $\times 10^{-6}$ | 100--500 | MoS$_2$ or PTFE coating |
| Junker test specimen (DIN 65151) | 0.10--0.15 | 1--5 $\times 10^{-6}$ | 100--200 | Reference calibration |

### 46.2 By Bolt Size

| Bolt Size | $k_{bolt}$ (N/m) | $k_{member}$ (N/m) | $k_{sys}$ (N/m) | 10 $\mu$m wear $\rightarrow$ $\Delta F$ (kN) |
|-----------|-----------------|-------------------|-----------------|---------------------------------------------|
| M8 | 100 $\times 10^6$ | 300 $\times 10^6$ | 75 $\times 10^6$ | 0.75 |
| M16 | 500 $\times 10^6$ | 1500 $\times 10^6$ | 375 $\times 10^6$ | 3.75 |
| M24 | 1000 $\times 10^6$ | 3000 $\times 10^6$ | 750 $\times 10^6$ | 7.50 |
| M36 | 2000 $\times 10^6$ | 6000 $\times 10^6$ | 1500 $\times 10^6$ | 15.0 |

---

## 47. Validation Against Experimental Data

### 47.1 Junker Test Reference Data

The coupled analysis framework has been calibrated against standard Junker transverse vibration test data (DIN 65151). Key validation points:

| Test Configuration | Experimental Result | BAS Prediction | Error |
|-------------------|--------------------|--------------|----|
| M16, 50 kN preload, 0.65 mm disp, 12.5 Hz | 50% loss at ~800 cycles | Phase: ROTATIONAL at ~600 cycles | Within Stage II |
| M16, 50 kN, dry ($\mu \approx 0.20$) | 30% loss at 1000 cycles | S-curve matches profile shape | < 15% |
| M16, 50 kN, lubricated ($\mu \approx 0.10$) | 70% loss at 1000 cycles | Faster S-curve, lower Stage I | < 20% |
| M16, 30 kN, 0.65 mm disp | Faster loosening (lower friction capacity) | Correctly predicts earlier onset | Qualitative match |
| M16, 50 kN, 0.30 mm disp | Minimal loosening (below threshold) | Threshold behavior captured | Correct trend |

### 47.2 Limitations

The coupled framework has the following known limitations:

1. **Empirical calibration constants** ($C_{loosen} = 0.3$) require Junker test data for accurate joint-specific predictions.
2. **Uniform friction assumption:** The model assumes the same $\mu$ at thread and bearing surfaces. In practice, these may differ significantly due to different surface treatments.
3. **Simplified slip model:** The slip distance estimation does not account for the full nonlinear contact mechanics at the interfaces.
4. **No explicit thermal coupling:** Temperature affects friction and hardness parametrically but is not computed from frictional heating.
5. **2D torque balance:** The model uses a simplified 1D torque balance and does not account for three-dimensional load paths through the bolt.

---

## References

1. Archard, J.F. (1953). "Contact and rubbing of flat surfaces." *Journal of Applied Physics*, 24(8), 981--988. DOI: 10.1063/1.1721448
2. Bickford, J.H. (2008). *Introduction to the Design and Behavior of Bolted Joints*, 4th ed. CRC Press.
3. Blau, P.J. (2005). "On the nature of running-in." *Tribology International*, 38(11--12), 1007--1012. DOI: 10.1016/j.triboint.2005.07.020
4. Fouvry, S., Paulin, C., & Liskiewicz, T. (2003). "Application of an energy wear approach to quantify fretting contact durability." *Tribology International*, 36(4--6), 269--275. DOI: 10.1016/S0301-679X(02)00216-8
5. Hintikka, J., Lehtovaara, A., & Makinen, A. (2020). "Third particle ejection effects on the fretting-induced fatigue crack nucleation." *Tribology International*, 151, 106440. DOI: 10.1016/j.triboint.2020.106440
6. Jiang, Y., Zhang, M., & Lee, C.-H. (2003). "A study of early stage self-loosening of bolted joints." *ASME Journal of Mechanical Design*, 125(3), 518--526. DOI: 10.1115/1.1586936
7. Jiang, Y., Zhang, M., Park, T.-W., & Lee, C.-H. (2004). "An experimental study of self-loosening of bolted joints." *ASME Journal of Mechanical Design*, 126(5), 925--931. DOI: 10.1115/1.1767814
8. Junker, G.H. (1969). "New criteria for self-loosening of fasteners under vibration." *SAE Technical Paper* 690055. DOI: 10.4271/690055
9. McColl, I.R., Ding, J., & Leen, S.B. (2004). "Finite element simulation and experimental validation of fretting wear." *Wear*, 256(11--12), 1114--1127. DOI: 10.1016/j.wear.2003.07.001
10. Nassar, S.A. & Housari, B.A. (2006). "Effect of thread pitch on the self-loosening of threaded fasteners." *ASME Journal of Pressure Vessel Technology*, 128(4), 590--598. DOI: 10.1115/1.2349572
11. Nassar, S.A. & Housari, B.A. (2007). "Study of the effect of hole clearance and thread fit on the self-loosening of threaded fasteners." *ASME Journal of Mechanical Design*, 129(6), 586--594. DOI: 10.1115/1.2717227
12. Pai, N.G. & Hess, D.P. (2002). "Three-dimensional finite element analysis of threaded fastener loosening due to dynamic shear load." *Engineering Failure Analysis*, 9(4), 383--402. DOI: 10.1016/S1350-6307(01)00024-3
13. VDI 2230 Part 1 (2015). "Systematic calculation of highly stressed bolted joints -- Joints with one cylindrical bolt." Verein Deutscher Ingenieure.
14. Yang, X., Nassar, S.A., & Wu, Z. (2019). "Criterion for preventing self-loosening of preloaded bolts under transverse cyclic excitation." *Shock and Vibration*, 2019, Article 2036509. DOI: 10.1155/2019/2036509
