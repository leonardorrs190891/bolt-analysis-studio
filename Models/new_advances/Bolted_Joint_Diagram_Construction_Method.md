# Bolted Joint Force-Extension Diagram: Complete Construction Method

## 1. Overview

The **bolted joint diagram** (also known as the joint diagram, Verspannungsschaubild, or force-deflection diagram) is the fundamental graphical tool from VDI 2230 for understanding how preload, external loads, and stiffness interact in a bolted joint. It provides a visual representation of:

- Bolt force increase under external loading
- Joint clamp force decrease under external loading
- The influence of bolt and member stiffness on load sharing
- The separation limit of the joint

This document provides all equations and step-by-step methods to construct the diagram for **any** bolted joint configuration.

---

## 1.1 Physical Intuition: Why the Diagram Looks the Way It Does

*This section captures the conceptual framing from the BoltScience tutorial (boltscience.com/pages/basics5.htm), which is essential for correctly interpreting the diagram before working through the mathematics.*

### 1.1.1 What Actually Happens When an External Force Is Applied

When an external tensile force $F_A$ is applied to a bolted joint, the intuitive assumption is that the bolt simply sees an additional force equal to $F_A$. **This is wrong**, and the joint diagram is the tool that shows why.

The correct statement, directly from BoltScience:

> *"When an external tensile force is applied to the joint it has the effect of **reducing some of the clamp force** caused by the bolt's preload **and applying an additional force to the bolt itself**."*

Both effects happen simultaneously and are inseparable. The load on the bolt **cannot** be increased without also decreasing the clamp force on the joint. This is not a coincidence — it is a direct consequence of equilibrium and compatibility of deformations.

### 1.1.2 The Load Path — Why the Force Is Placed at the Interface

In the joint diagram, the external force $F_A$ is drawn acting **at the joint interface** (between the clamped surfaces), not at the bolt head or nut. This placement may initially seem unusual — after all, in most engineering problems the load arrow is placed at the point where the load is applied to the component.

The reason it is drawn at the interface is the physical load path:

```
   BOLT HEAD
       │  Bolt in tension (preloaded)
       │
  ─────┼────── ← Joint interface: external force F_A applied here
       │  Members in compression
   NUT / FLANGE
```

When $F_A$ is applied at this interface (e.g., by internal pressure in a flange, or by a tensile load trying to separate the joint members):

1. The compressed members **begin to decompress** — they had been squeezed by the bolt preload, and the external force partially relieves this compression.
2. As the members decompress, the joint opening **increases slightly** — the two surfaces being pulled apart extend the bolt a tiny additional amount.
3. This additional bolt extension is what **increases the bolt force** by $\Phi \cdot F_A$.

The external force effectively "travels through" the compressed joint material before reaching the bolt. The joint material is the first line of resistance — it absorbs the majority of the external load as a release of its stored compression energy, while only a fraction ($\Phi$) reaches the bolt as additional tension.

**The key insight**: The force is NOT added to the bolt and subtracted from the joint independently. They are coupled: one cannot happen without the other.

### 1.1.3 Geometric Proof of Load Sharing from the Diagram

The geometry of the joint diagram makes this coupling visible. At the preload state, the bolt extension is $\delta_{b,0} = F_V / k_b$ and the member compression is $\delta_{m,0} = F_V / k_m$. The total joint deformation is:

$$\delta_{total,0} = \delta_{b,0} + \delta_{m,0} = F_V \left(\frac{1}{k_b} + \frac{1}{k_m}\right)$$

When $F_A$ is applied, the joint deformation increases by $\delta_{FA}$. Compatibility requires:

$$\delta_{FA} = \frac{F_A}{k_b + k_m}$$

This single extra deformation is **shared** between bolt and member according to their stiffnesses:
- Bolt gets: $\delta_{b,extra} = \frac{k_m}{k_b + k_m} \cdot \delta_{FA} = \frac{\Phi \cdot F_A}{k_b}$
- Member loses: $\delta_{m,loss} = \frac{k_b}{k_b + k_m} \cdot \delta_{FA} = \frac{(1-\Phi) \cdot F_A}{k_m}$

Multiplying by stiffnesses:
$$\Delta F_{bolt} = k_b \cdot \delta_{b,extra} = \Phi \cdot F_A$$
$$\Delta F_{member} = k_m \cdot \delta_{m,loss} = (1-\Phi) \cdot F_A$$

This geometric coupling is exactly what the **load line** (slope $= -k_m$, connecting $L_{bolt}$ to $L_{memb}$) represents in the diagram.

### 1.1.4 Stiffness Ratio Controls How Load Is Shared

The ratio between member stiffness and bolt stiffness is the single most important design parameter for a bolted joint under external loading:

| If $k_m \gg k_b$ (hard joint) | If $k_m \ll k_b$ (soft joint) |
|---|---|
| $\Phi \approx k_b/k_m \ll 1$ | $\Phi \approx 1$ |
| Bolt sees very little of $F_A$ | Bolt sees nearly all of $F_A$ |
| Clamp force drops rapidly toward zero | Clamp force barely changes |
| Good for bolt fatigue | Poor for bolt fatigue |
| Risk: joint separation at lower $F_A$ | Risk: bolt fatigue failure |

From BoltScience:
> *"Because of the steep stiffness slope of the joint [hard joint], the bolt will only sustain a small proportion of the applied force."*

> *"[In a soft joint], the bolt would sustain the majority of the applied force."*

### 1.1.5 Design Consequence: Reduced-Diameter Shank Bolts

Since a **lower bolt stiffness $k_b$** results in a lower $\Phi$ (better fatigue performance), high-performance fatigue-loaded bolts deliberately reduce the shank diameter below the thread root diameter. This is the "waisted" or "necked-down" shank design.

From BoltScience:
> *"If the shank diameter is not reduced to a diameter below that of the stress diameter then the strength of the fastener will not normally be impaired."*

The design logic:
- Reduced shank: $A_d < A_t$ → lower $k_b$ (longer effective spring) → lower $\Phi$ → smaller cyclic bolt stress $\sigma_a = \Phi \cdot F_A / (2A_t)$
- The yield/fracture strength is still governed by the threaded section stress area $A_t$ (the weakest cross-section), so reducing the shank does not reduce static strength if $A_d > A_t$ is not required
- However, the fatigue stress amplitude is reduced because the bolt "absorbs" less of the cyclic load

**Quantitative benefit example** (M16, standard vs. waisted shank):

| Parameter | Standard Shank | Waisted Shank |
|---|---|---|
| Shank diameter | 16 mm | 13.8 mm ($\approx d_3$) |
| $A_d$ | 201 mm² | 149.6 mm² |
| $k_b$ (relative) | 1.0 | ~0.85 |
| $\Phi$ (steel members, 30 mm grip) | 0.237 | 0.205 |
| Fatigue stress amplitude | $\sigma_a$ | $0.86 \sigma_a$ (14% reduction) |

This 14% reduction in fatigue stress amplitude can represent a significant increase in fatigue life on the S-N curve.

---

## 2. Fundamental Stiffness Calculations

### 2.1 Bolt Stiffness ($k_b$)

The bolt acts as a tension spring. Its stiffness is calculated by treating each section of the bolt as springs in series.

**General compliance (resilience) method:**

$$\delta_b = \sum_{i} \frac{l_i}{E_b \cdot A_i}$$

$$k_b = \frac{1}{\delta_b}$$

**For a bolt with distinct shank and threaded regions in the grip:**

$$k_b = \frac{A_d \cdot A_t \cdot E_b}{A_d \cdot l_t + A_t \cdot l_d}$$

where:
- $A_d = \frac{\pi d^2}{4}$ — shank (major diameter) cross-sectional area
- $A_t$ — tensile stress area (from thread tables)
- $E_b$ — bolt elastic modulus
- $l_d$ — length of unthreaded shank within the grip
- $l_t$ — length of threaded portion within the grip

**Detailed VDI 2230 compliance breakdown:**

$$\delta_b = \delta_{head} + \delta_{shank} + \delta_{thread,free} + \delta_{thread,engaged} + \delta_{nut}$$

$$\delta_b = \frac{0.5 \cdot d}{E_b \cdot A_N} + \frac{l_d}{E_b \cdot A_d} + \frac{l_t}{E_b \cdot A_t} + \frac{0.5 \cdot d}{E_b \cdot A_t} + \frac{0.4 \cdot d}{E_b \cdot A_N}$$

where $A_N = \frac{\pi d^2}{4}$ is the nominal area under the head/nut.

### 2.2 Member (Joint/Clamped Parts) Stiffness ($k_m$)

The clamped members act as a compression spring. The stress distribution follows a frustum cone (Rötscher cone).

**Shigley Frustum Cone Method** (half-apex angle $\alpha = 30°$):

$$k_m = \frac{\pi E_m \cdot d \cdot \tan(\alpha)}{\ln\left[\frac{(L \tan\alpha + d_w - d)(d_w + d)}{(L \tan\alpha + d_w + d)(d_w - d)}\right]}$$

For standard geometry ($d_w = 1.5d$, $\alpha = 30°$):

$$k_m = \frac{0.5774 \cdot \pi \cdot E_m \cdot d}{\ln\left[\frac{(0.5774 \cdot L + 0.5d)(2.5d)}{(0.5774 \cdot L + 2.5d)(0.5d)}\right]}$$

where:
- $E_m$ — member elastic modulus
- $d$ — nominal bolt diameter
- $d_w$ — effective bearing diameter (washer face diameter)
- $L$ — total grip length (total clamped length)

**Wileman's Empirical Correlation** (FEM-validated, error < 5%):

$$k_m = 0.78952 \cdot E_m \cdot d \cdot e^{0.62914 \cdot (d/L)}$$

Valid for $0.5 \leq d/L \leq 2.0$.

**For multi-material stacks** (different flange materials):

$$\frac{1}{k_m} = \frac{1}{k_{m1}} + \frac{1}{k_{m2}} + \cdots + \frac{1}{k_{mn}}$$

Each layer is computed using its own elastic modulus and effective frustum geometry.

---

## 3. Load Factor (Stiffness Ratio)

### 3.1 Concentric Loading

The **load factor** $\Phi$ determines how external axial force is shared between bolt and members:

$$\Phi = \frac{k_b}{k_b + k_m}$$

**Physical meaning:** $\Phi$ is the fraction of external load that goes to additionally loading the bolt. The remainder $(1 - \Phi)$ relieves the clamping force in the members.

Typical values: $\Phi = 0.10$ to $0.30$

### 3.2 Eccentric Loading (VDI 2230 Extension)

For loads not applied concentrically along the bolt axis:

$$\Phi_n = n \cdot \frac{k_b}{k_b + k_m} = n \cdot \Phi$$

where $n$ is the **load introduction factor**:
- $n = 0$ — load introduced at the clamping interface (most favorable)
- $n = 1$ — load introduced directly under the bolt head (least favorable)
- Typical: $n = 0.25$ to $0.50$

---

## 4. Force Relationships Under External Axial Load

Given:
- $F_V$ = assembly preload (initial bolt preload)
- $F_A$ = external axial tensile load applied to the joint

### 4.1 Bolt Force

$$F_B = F_V + \Phi \cdot F_A$$

The bolt force **increases** from the preload by a fraction $\Phi$ of the external load.

### 4.2 Clamping (Joint) Force

$$F_{clamp} = F_V - (1 - \Phi) \cdot F_A$$

The clamping force **decreases** from the preload by a fraction $(1 - \Phi)$ of the external load.

### 4.3 Separation Condition

Joint separation occurs when the clamping force drops to zero:

$$F_{clamp} = 0 \implies F_{A,sep} = \frac{F_V}{1 - \Phi}$$

Beyond separation, the bolt carries the entire external load directly:

$$F_B = F_A \quad \text{(for } F_A > F_{A,sep}\text{)}$$

---

## 5. Constructing the Joint Diagram — Step by Step

### 5.1 Axis Definitions

| Axis | Left Half (Bolt) | Right Half (Members) |
|------|-------------------|----------------------|
| **X-axis** | Bolt extension $\delta_b$ (positive left) | Member compression $\delta_m$ (positive right) |
| **Y-axis** | Force (N or kN) | Force (N or kN) |

The origin of the diagram is the **zero-force, zero-deflection** point.

### 5.2 Step-by-Step Construction

**Step 1: Draw the Bolt Line (tension spring)**

The bolt stiffness line starts at the origin and extends upward-left with slope $k_b$:

$$F = k_b \cdot \delta_b$$

This is a straight line from the origin with slope = $k_b$ (steeper line = stiffer bolt).

**Step 2: Draw the Member Line (compression spring)**

The member stiffness line starts at the origin and extends upward-right with slope $k_m$:

$$F = k_m \cdot \delta_m$$

This is a straight line from the origin with slope = $k_m$ (steeper line = stiffer members).

**Step 3: Mark the Preload Point**

The preload $F_V$ determines the operating point where the bolt and member lines intersect at the assembled state:

- Bolt extension at preload: $\delta_{b,0} = F_V / k_b$
- Member compression at preload: $\delta_{m,0} = F_V / k_m$

Draw a horizontal line at $F = F_V$ intersecting both stiffness lines. This is the **preload operating point**.

**Step 4: Apply External Load $F_A$**

When an external tensile force $F_A$ is applied, the diagram shifts:

- **Bolt force increases** by: $\Delta F_b = \Phi \cdot F_A$
- **Clamp force decreases** by: $\Delta F_m = (1 - \Phi) \cdot F_A$

The new operating point moves **along the member stiffness line slope** from the preload point. This is because the external force causes the joint to "open" slightly — the bolt extends further while the members decompress partially.

**Graphical construction:**

From the preload point, draw a line parallel to the member stiffness line (but with reversed slope direction, going up-left) with horizontal extent equal to $F_A / k_b + F_A / k_m$. The vertical rise of this line from $F_V$ equals $\Phi \cdot F_A$ at the bolt side.

**Step 5: Mark Critical Points**

| Point | Force Value | Description |
|-------|-------------|-------------|
| $F_V$ | Assembly preload | Initial bolt tension = initial clamp force |
| $F_B = F_V + \Phi F_A$ | Max bolt force | Bolt force under external load |
| $F_{clamp} = F_V - (1-\Phi)F_A$ | Residual clamp | Remaining joint clamping |
| $F_{A,sep} = F_V/(1-\Phi)$ | Separation load | External load causing joint opening |

**Step 6: Draw the Load Triangle**

The **load triangle** (the characteristic triangle of the joint diagram) is bounded by:
- The bolt stiffness line (left side)
- The member stiffness line (right side, reflected)
- The horizontal line at the preload level

The height of the triangle above $F_V$ is $\Phi \cdot F_A$ (bolt force increase).
The depth below $F_V$ is $(1-\Phi) \cdot F_A$ (clamp force decrease).

---

## 6. Numerical Construction Algorithm

### 6.1 Input Parameters

```
REQUIRED INPUTS:
  d       = nominal bolt diameter [mm]
  A_t     = tensile stress area [mm²]
  A_d     = shank area [mm²]
  E_b     = bolt elastic modulus [MPa]
  E_m     = member elastic modulus [MPa]
  l_d     = unthreaded grip length [mm]
  l_t     = threaded grip length [mm]
  L       = total grip length [mm]
  d_w     = bearing face diameter [mm]
  F_V     = assembly preload [N]
  F_A     = external axial load [N]
  n       = load introduction factor [-] (optional, default = 1.0)
```

### 6.2 Calculation Sequence

```
STEP 1: Compute Bolt Stiffness
  δ_b = l_d/(E_b × A_d) + l_t/(E_b × A_t) + 0.5d/(E_b × A_N) + 0.4d/(E_b × A_N)
  k_b = 1/δ_b

STEP 2: Compute Member Stiffness
  (Using Shigley or Wileman as appropriate)
  k_m = Shigley_frustum(E_m, d, d_w, L, α=30°)

STEP 3: Compute Load Factor
  Φ = k_b / (k_b + k_m)
  Φ_n = n × Φ   (if eccentric)

STEP 4: Compute Operating Forces
  F_bolt    = F_V + Φ_n × F_A
  F_clamp   = F_V - (1 - Φ_n) × F_A
  F_sep     = F_V / (1 - Φ_n)

STEP 5: Compute Deflections
  δ_b_preload = F_V / k_b
  δ_m_preload = F_V / k_m

  δ_b_loaded  = F_bolt / k_b
  δ_m_loaded  = F_clamp / k_m

STEP 6: Generate Diagram Coordinates
  (See Section 6.3)
```

### 6.3 Diagram Coordinate Generation

The diagram is constructed using the following coordinate pairs. The x-axis uses **bolt extension** (negative = left) and **member compression** (positive = right), with **force** on the y-axis.

```
BOLT STIFFNESS LINE:
  Point A: (0, 0)                         — Origin
  Point B: (-δ_b_max, k_b × δ_b_max)    — Extended to max force

MEMBER STIFFNESS LINE:
  Point C: (0, 0)                         — Origin
  Point D: (+δ_m_max, k_m × δ_m_max)    — Extended to max force

PRELOAD STATE:
  Point P_bolt: (-F_V/k_b, F_V)          — Bolt at preload
  Point P_memb: (+F_V/k_m, F_V)          — Member at preload

LOADED STATE:
  Point L_bolt: (-F_bolt/k_b, F_bolt)    — Bolt under load
  Point L_memb: (+F_clamp/k_m, F_clamp)  — Member under load

SEPARATION STATE:
  Point S_bolt: (-F_sep/k_b, F_sep)      — Bolt at separation
  Point S_memb: (0, 0)                    — Member fully decompressed

LOAD TRIANGLE VERTICES:
  Vertex 1: P_bolt  (-F_V/k_b, F_V)
  Vertex 2: L_bolt  (-F_bolt/k_b, F_bolt)
  Vertex 3: L_memb  (+F_clamp/k_m, F_clamp)
  Vertex 4: P_memb  (+F_V/k_m, F_V)
```

---

## 7. Hard Joint vs. Soft Joint Behavior

The **stiffness ratio** between members and bolt fundamentally determines the shape and behavior of the joint diagram. See also §1.1.4 for the conceptual explanation.

### 7.1 Hard Joint (High Member Stiffness / Low Bolt Stiffness)

A hard joint is defined as one with a **low stiffness bolt and a high stiffness joint** (stiff clamped members).

$$k_m \gg k_b \implies \Phi \approx \frac{k_b}{k_m} \ll 1$$

**BoltScience (boltscience.com/pages/basics5.htm):**
> *"Because of the steep stiffness slope of the joint, the bolt will only sustain a small proportion of the applied force."*

**Characteristics:**
- Member line is steep (nearly vertical) — very little compression deflection
- Bolt line is shallow — significant extension under load
- Small $\Phi$ → most of the external load relieves the clamp (good for fatigue)
- $\Delta F_b = \Phi \cdot F_A$ is small → bolt sees little additional load
- $\Delta F_m = (1-\Phi) \cdot F_A$ is large → clamp force drops quickly toward zero
- **Load triangle is tall and narrow**
- Separation risk: the joint can separate at a relatively low $F_A$ because clamp force erodes quickly

**Diagram appearance:** The member stiffness line is much steeper than the bolt line. The load triangle is a tall thin sliver. The bolt force increase ($\Phi \cdot F_A$) is a small upward step; the clamp force decrease ($(1-\Phi) \cdot F_A$) is a large downward step.

**Typical applications:** Steel-on-steel flanges, engine cylinder heads, structural steel connections (all metal, no gasket)

### 7.2 Soft Joint (Low Member Stiffness / High Bolt Stiffness)

A soft joint is defined as one with a **high stiffness bolt and a low stiffness joint** (compliant clamped members).

$$k_m \ll k_b \implies \Phi \approx 1$$

**BoltScience (boltscience.com/pages/basics5.htm):**
> *"[In a soft joint], the bolt would sustain the majority of the applied force."*

**Characteristics:**
- Member line is shallow — large compression deflection
- Bolt line is steep — relatively little extension
- Large $\Phi$ → most of the external load goes to additionally loading the bolt
- $\Delta F_b = \Phi \cdot F_A$ is large → bolt sees significant additional cyclic load (bad for fatigue)
- $\Delta F_m = (1-\Phi) \cdot F_A$ is small → clamp force is well maintained
- **Load triangle is short and wide**
- Separation risk: low, because clamp force remains relatively stable

**Diagram appearance:** The bolt stiffness line is much steeper than the member line. The load triangle is a wide flat shape. The bolt force increase is large; the clamp force decrease is small.

**Typical applications:** Gasketed pipe flanges, connections with polymer spacers, soft-washer assemblies, composite sandwich panels

### 7.3 Stiffness Ratio Summary

| Parameter | Hard Joint | Soft Joint |
|-----------|-----------|------------|
| Definition (BoltScience) | Low stiffness bolt, high stiffness joint | High stiffness bolt, low stiffness joint |
| $k_m / k_b$ | $\gg 1$ (typ. 3–10) | $\ll 1$ (typ. 0.3–1) |
| $\Phi$ | 0.05 – 0.15 | 0.30 – 0.60+ |
| Bolt force increase $\Phi F_A$ | Small | Large |
| Clamp force decrease $(1-\Phi) F_A$ | Large | Small |
| Fatigue behavior | Favorable (small $\sigma_a$) | Unfavorable (large $\sigma_a$) |
| Separation resistance | Lower (clamp drops fast) | Higher (clamp stable) |
| Diagram shape | Tall, narrow triangle | Short, wide triangle |
| Bolt stiffness line | Shallow slope | Steep slope |
| Member stiffness line | Steep slope | Shallow slope |

### 7.4 Design Strategy: Making a Hard Joint Harder

Since a hard joint (lower $\Phi$) is favorable for fatigue, designers use the following levers to reduce $\Phi$:

1. **Reduce bolt stiffness** — use a waisted (reduced-diameter) shank (see §1.1.5), or a longer grip length $L$
2. **Increase member stiffness** — use stiffer materials ($E_m$), larger flange thickness, or eliminate soft gaskets
3. **Eliminate compliant elements** — replace soft gaskets with metal ring joints (RTJ), or use metal-to-metal contact
4. **Increase grip length** — longer $L$ lowers $k_b$ proportionally; member stiffness is less sensitive to $L$ for thick flanges

Rule of thumb from VDI 2230: Target $k_m / k_b \geq 3$ for fatigue-critical bolted joints.

---

## 8. Additional Considerations for Real Joints

### 8.1 Preload Losses (Embedding, Relaxation)

The effective preload after losses:

$$F_{V,eff} = F_V - F_Z$$

where $F_Z$ is the embedding/relaxation loss:

$$F_Z = f_Z \cdot \frac{k_b \cdot k_m}{k_b + k_m}$$

$f_Z$ = total embedding amount (typically 3–10 µm per interface)

The joint diagram shifts **downward** by $F_Z$, reducing both the bolt force baseline and the clamp force reserve.

### 8.2 Thermal Effects

Differential thermal expansion alters preload:

$$\Delta F_{thermal} = (\alpha_m - \alpha_b) \cdot \Delta T \cdot L \cdot \frac{k_b \cdot k_m}{k_b + k_m}$$

If $\alpha_m > \alpha_b$ and $\Delta T > 0$: preload increases (members expand more than bolt).
If $\alpha_m < \alpha_b$ and $\Delta T > 0$: preload decreases.

### 8.3 Tightening Scatter (Assembly Uncertainty)

The tightening factor $\alpha_A$ accounts for scatter between minimum and maximum preload:

$$\alpha_A = \frac{F_{M,max}}{F_{M,min}}$$

| Tightening Method | $\alpha_A$ |
|-------------------|-----------|
| Manual torque wrench | 1.4 – 1.6 |
| Precision torque | 1.2 – 1.4 |
| Torque-angle method | 1.1 – 1.2 |
| Yield-point control | 1.0 – 1.2 |
| Hydraulic tensioning | 1.0 – 1.1 |

This means the diagram should be constructed for both $F_{M,min}$ (worst case for separation) and $F_{M,max}$ (worst case for bolt overload).

### 8.4 Post-Separation Behavior

Beyond the separation point ($F_A > F_{A,sep}$), the members lose contact and the bolt carries the full external load directly:

$$F_B = F_A \quad \text{(post-separation)}$$

$$\delta_B = \frac{F_A}{k_b} \quad \text{(bolt deflection post-separation)}$$

The diagram transitions from a slope of $\Phi \cdot k_b$ (pre-separation) to a slope of $k_b$ (post-separation) — a kink in the bolt force curve.

---

## 9. Design Safety Factors (VDI 2230)

### 9.1 Against Joint Separation

$$S_{sep} = \frac{F_{V,eff}}{(1 - \Phi_n) \cdot F_A} \geq 1.2$$

### 9.2 Against Bolt Yield

$$S_{yield} = \frac{R_{p0.2} \cdot A_t}{F_{M,max} + \Phi_n \cdot F_A} \geq 1.1$$

### 9.3 Fatigue Safety

$$S_D = \frac{\sigma_A}{\sigma_a} \geq 1.2$$

where:
- $\sigma_A$ = allowable alternating stress amplitude (33.5–50 MPa for rolled threads per VDI 2230)
- $\sigma_a = \frac{\Phi_n \cdot \Delta F_A}{2 \cdot A_t}$ = actual alternating stress from cyclic loading

---

## 10. Worked Example

### Given Data

| Parameter | Value |
|-----------|-------|
| Bolt | M12 × 1.75, Property Class 10.9 |
| $d$ | 12 mm |
| $A_t$ | 84.3 mm² |
| $A_d$ | 113.1 mm² |
| $E_b$ | 210,000 MPa |
| $E_m$ | 210,000 MPa (steel members) |
| $l_d$ | 15 mm |
| $l_t$ | 10 mm |
| $L$ (grip) | 25 mm |
| $d_w$ | 18 mm (1.5d) |
| $F_V$ | 50,000 N |
| $F_A$ | 15,000 N |

### Calculations

**Bolt stiffness:**

$$k_b = \frac{113.1 \times 84.3 \times 210{,}000}{113.1 \times 10 + 84.3 \times 15} = \frac{2.001 \times 10^{9}}{2{,}395.5} = 835{,}400 \text{ N/mm}$$

**Member stiffness (Wileman):**

$$k_m = 0.78952 \times 210{,}000 \times 12 \times e^{0.62914 \times (12/25)}$$

$$k_m = 1{,}989{,}590 \times e^{0.302} = 1{,}989{,}590 \times 1.3525 = 2{,}690{,}900 \text{ N/mm}$$

**Load factor:**

$$\Phi = \frac{835{,}400}{835{,}400 + 2{,}690{,}900} = \frac{835{,}400}{3{,}526{,}300} = 0.237$$

**Forces under load:**

$$F_{bolt} = 50{,}000 + 0.237 \times 15{,}000 = 53{,}555 \text{ N}$$

$$F_{clamp} = 50{,}000 - (1 - 0.237) \times 15{,}000 = 50{,}000 - 11{,}445 = 38{,}555 \text{ N}$$

$$F_{sep} = \frac{50{,}000}{1 - 0.237} = 65{,}530 \text{ N}$$

**Deflections:**

$$\delta_{b,preload} = \frac{50{,}000}{835{,}400} = 0.0598 \text{ mm}$$

$$\delta_{m,preload} = \frac{50{,}000}{2{,}690{,}900} = 0.0186 \text{ mm}$$

### Diagram Points Summary

| Point | x (mm) | y (N) | Description |
|-------|--------|-------|-------------|
| Origin | 0 | 0 | Zero reference |
| P_bolt | −0.0598 | 50,000 | Bolt at preload |
| P_memb | +0.0186 | 50,000 | Member at preload |
| L_bolt | −0.0641 | 53,555 | Bolt under load |
| L_memb | +0.0143 | 38,555 | Member under load |
| S_bolt | −0.0784 | 65,530 | Bolt at separation |
| S_memb | 0 | 0 | Member decompressed |

This joint has $k_m/k_b \approx 3.2$, placing it in the **moderately hard joint** category with a relatively narrow load triangle — favorable for fatigue performance.

---

## 11. Quick Reference Formulas

| Quantity | Formula |
|----------|---------|
| Bolt stiffness | $k_b = \frac{A_d \cdot A_t \cdot E_b}{A_d \cdot l_t + A_t \cdot l_d}$ |
| Member stiffness (Wileman) | $k_m = 0.78952 \cdot E_m \cdot d \cdot e^{0.62914 \cdot d/L}$ |
| Load factor | $\Phi = \frac{k_b}{k_b + k_m}$ |
| Bolt force | $F_B = F_V + \Phi \cdot F_A$ |
| Clamp force | $F_{clamp} = F_V - (1 - \Phi) \cdot F_A$ |
| Separation load | $F_{A,sep} = \frac{F_V}{1 - \Phi}$ |
| Embedding loss | $F_Z = f_Z \cdot \frac{k_b \cdot k_m}{k_b + k_m}$ |
| Thermal preload change | $\Delta F_T = (\alpha_m - \alpha_b) \Delta T \cdot L \cdot \frac{k_b \cdot k_m}{k_b + k_m}$ |
| Fatigue stress amplitude | $\sigma_a = \frac{\Phi_n \cdot \Delta F_A}{2 \cdot A_t}$ |
| Safety against separation | $S_{sep} = \frac{F_{V,eff}}{(1-\Phi_n) \cdot F_A} \geq 1.2$ |

---

## 12. Complete Graph Plotting Algorithm (VDI 2230 Joint Diagram)

This section provides the complete geometric construction and coordinate generation for plotting the bolted joint diagram exactly as shown in the VDI 2230 standard figure.

### 12.1 Graph Anatomy and Coordinate System

The joint diagram uses a **split-axis** coordinate system centered at the origin:

```
                    ▲ Force (F)
                    │
         F_bolt ────┤─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ○ L_bolt
                    │                                       ╱
           F_V ─────┤─ ─ ─ ─ ○ P_bolt ─ ─ ─ ─ ─ ─ ─ ─╱─ ─ ─ ○ P_memb
                    │       ╱                         ╱           ╲
        F_clamp ────┤─ ─ ╱─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ╱─ ─ ─ ─ ─ ─ ─ ─○ L_memb
                    │  ╱          LOAD          ╱                   ╲
                    │╱          TRIANGLE      ╱                      ╲
                    ○─────────────────────────────────────────────────→ Extension (δ)
                 ORIGIN
                    │
              ◄─────┼─────►
            Bolt    │  Joint (Member)
          Extension │  Compression
          (−δ_b)    │  (+δ_m)
```

**Convention used in this plotting algorithm:**

| Axis Direction | Physical Meaning | Sign Convention |
|----------------|-----------------|-----------------|
| X negative (left) | Bolt extension $\delta_b$ | Bolt stretches left |
| X positive (right) | Member compression $\delta_m$ | Members compress right |
| Y positive (up) | Force $F$ | Tension/compression force |

### 12.2 Core Geometric Elements

The diagram consists of **7 fundamental geometric elements** that must be plotted:

**Element 1 — Bolt Stiffness Line (from Origin, going upper-left):**

This line represents the bolt acting as a tension spring. It starts at the origin and extends with slope $-k_b$ in the x-direction (going left means negative x, force going up).

$$\text{Parametric form: } x(\lambda) = -\lambda, \quad y(\lambda) = k_b \cdot \lambda \quad \text{for } \lambda \in [0, \, \delta_{b,max}]$$

Where $\delta_{b,max}$ is chosen to extend slightly beyond the separation point:

$$\delta_{b,max} = 1.15 \times \frac{F_{sep}}{k_b}$$

Plot from: $(0, 0)$ to $(-\delta_{b,max}, \, k_b \cdot \delta_{b,max})$

**Element 2 — Member Stiffness Line (from Origin, going upper-right):**

This line represents the clamped members acting as a compression spring.

$$\text{Parametric form: } x(\lambda) = +\lambda, \quad y(\lambda) = k_m \cdot \lambda \quad \text{for } \lambda \in [0, \, \delta_{m,max}]$$

Where $\delta_{m,max}$ extends slightly beyond the preload deflection:

$$\delta_{m,max} = 1.3 \times \frac{F_V}{k_m}$$

Plot from: $(0, 0)$ to $(+\delta_{m,max}, \, k_m \cdot \delta_{m,max})$

**Element 3 — Load Application Line (the diagonal connecting loaded states):**

This is the **critical line** that connects the loaded bolt point to the loaded member point. It runs parallel to the member stiffness line, shifted by the preload. This line represents how the external force $F_A$ is shared.

$$\text{From: } \left(-\frac{F_{bolt}}{k_b}, \, F_{bolt}\right) \quad \text{To: } \left(+\frac{F_{clamp}}{k_m}, \, F_{clamp}\right)$$

The slope of this line equals $-k_m$ (same magnitude as the member line, but going from upper-left to lower-right).

**Proof of slope:**

$$\text{slope} = \frac{F_{clamp} - F_{bolt}}{\frac{F_{clamp}}{k_m} - \left(-\frac{F_{bolt}}{k_b}\right)} = \frac{F_{clamp} - F_{bolt}}{\frac{F_{clamp}}{k_m} + \frac{F_{bolt}}{k_b}}$$

Substituting $F_{bolt} = F_V + \Phi F_A$ and $F_{clamp} = F_V - (1-\Phi) F_A$:

$$\text{Numerator} = -F_A$$

$$\text{Denominator} = \frac{F_V - (1-\Phi)F_A}{k_m} + \frac{F_V + \Phi F_A}{k_b}$$

Using $\Phi = k_b/(k_b + k_m)$, after algebraic simplification:

$$\text{Denominator} = \frac{F_A}{k_m}$$

$$\therefore \text{slope} = \frac{-F_A}{F_A/k_m} = -k_m \quad \checkmark$$

**Element 4 — Preload Horizontal Line:**

$$y = F_V \quad \text{from } x = -\frac{F_V}{k_b} \text{ to } x = +\frac{F_V}{k_m}$$

**Element 5 — Bolt Force Horizontal Line (loaded state):**

$$y = F_{bolt} \quad \text{from } x = -\frac{F_{bolt}}{k_b} \text{ to beyond the load line}$$

**Element 6 — Clamp Force Horizontal Line (loaded state):**

$$y = F_{clamp} \quad \text{from the load line to } x = +\frac{F_{clamp}}{k_m}$$

**Element 7 — Separation Extension Line (post-separation bolt behavior):**

After separation, the bolt carries the full external load. The bolt force vs. extension curve kinks and follows the bolt stiffness line slope from the separation point:

$$\text{From: } \left(-\frac{F_{sep}}{k_b}, \, F_{sep}\right) \quad \text{extending further with slope } k_b$$

### 12.3 Annotation Arrows and Force Indicators

The diagram requires **three annotated force arrows** on the right side:

**Arrow A — Bolt Force Increase (green, upward):**

$$\Delta F_{bolt} = \Phi \cdot F_A = F_{bolt} - F_V$$

Vertical arrow from $F_V$ to $F_{bolt}$ at $x = x_{annotation}$:

$$x_{annotation} = +\frac{F_{clamp}}{k_m} + \text{offset}$$

**Arrow B — Joint Clamp Force Decrease (blue, downward):**

$$\Delta F_{clamp} = (1 - \Phi) \cdot F_A = F_V - F_{clamp}$$

Vertical arrow from $F_V$ down to $F_{clamp}$ at $x = x_{annotation}$

**Arrow C — Applied Force to Joint (black/red, total span):**

$$F_A = \Delta F_{bolt} + \Delta F_{clamp} = F_{bolt} - F_{clamp}$$

Vertical arrow spanning from $F_{clamp}$ to $F_{bolt}$ at $x = x_{annotation} + \text{offset}_2$

### 12.4 Load Triangle Geometry

The **load triangle** (or load parallelogram) is the quadrilateral formed by:

$$\text{Vertices (counterclockwise):}$$

$$V_1 = \left(-\frac{F_V}{k_b}, \, F_V\right) \quad \text{— Bolt at preload (P\_bolt)}$$

$$V_2 = \left(-\frac{F_{bolt}}{k_b}, \, F_{bolt}\right) \quad \text{— Bolt under load (L\_bolt)}$$

$$V_3 = \left(+\frac{F_{clamp}}{k_m}, \, F_{clamp}\right) \quad \text{— Member under load (L\_memb)}$$

$$V_4 = \left(+\frac{F_V}{k_m}, \, F_V\right) \quad \text{— Member at preload (P\_memb)}$$

The **upper triangle** (above $F_V$) has area proportional to bolt energy increase:

$$A_{upper} = \frac{1}{2} \cdot \frac{\Phi \cdot F_A}{k_b} \cdot \Phi \cdot F_A = \frac{(\Phi \cdot F_A)^2}{2 \cdot k_b}$$

The **lower triangle** (below $F_V$) has area proportional to member energy release:

$$A_{lower} = \frac{1}{2} \cdot \frac{(1-\Phi) \cdot F_A}{k_m} \cdot (1-\Phi) \cdot F_A = \frac{((1-\Phi) \cdot F_A)^2}{2 \cdot k_m}$$

### 12.5 Separation Line Construction

The separation envelope shows the maximum external force before joint opening:

$$\text{From origin } (0, 0) \text{ along member line to } \left(+\frac{F_V}{k_m}, \, F_V\right)$$

$$\text{Then vertically to } \left(+\frac{F_V}{k_m}, \, F_{sep}\right) \text{ — this is the bolt force at separation}$$

Where:

$$F_{sep} = \frac{F_V}{1 - \Phi}$$

The separation point on the bolt line is at:

$$\left(-\frac{F_{sep}}{k_b}, \, F_{sep}\right)$$

And the corresponding member point is the origin $(0, 0)$ — members fully decompressed.

### 12.6 Load Line Intersection with Preload Horizontal

The load application line (Element 3) intersects the preload horizontal ($y = F_V$) at:

$$x_{int} = -\frac{F_{bolt}}{k_b} + \frac{F_{bolt} - F_V}{k_m} = -\frac{F_{bolt}}{k_b} + \frac{\Phi \cdot F_A}{k_m}$$

This point divides the load quadrilateral into the upper and lower triangles.

### 12.7 Complete Coordinate Table for Plotting

Given computed values $k_b$, $k_m$, $\Phi$, $F_V$, $F_A$, $F_{bolt}$, $F_{clamp}$, $F_{sep}$:

**Primary Lines (x, y coordinate pairs):**

| Line | Start $(x_1, y_1)$ | End $(x_2, y_2)$ | Color | Style |
|------|---------------------|-------------------|-------|-------|
| Bolt stiffness | $(0, 0)$ | $\left(-1.15\frac{F_{sep}}{k_b},\; 1.15 \cdot F_{sep}\right)$ | Dark brown / orange | Solid, thick |
| Member stiffness | $(0, 0)$ | $\left(+1.3\frac{F_V}{k_m},\; 1.3 \cdot F_V\right)$ | Dark green | Solid, thick |
| Load line | $\left(-\frac{F_{bolt}}{k_b},\; F_{bolt}\right)$ | $\left(+\frac{F_{clamp}}{k_m},\; F_{clamp}\right)$ | Dark green / teal | Solid |
| Preload horiz. | $\left(-\frac{F_V}{k_b},\; F_V\right)$ | $\left(+\frac{F_V}{k_m},\; F_V\right)$ | Black | Dashed |

**Annotation Arrow Coordinates:**

| Arrow | From $(x, y_1)$ | To $(x, y_2)$ | Color | Label |
|-------|------------------|----------------|-------|-------|
| Bolt increase | $(x_a, F_V)$ | $(x_a, F_{bolt})$ | Green | $\Phi \cdot F_A$ |
| Clamp decrease | $(x_a, F_V)$ | $(x_a, F_{clamp})$ | Blue | $(1-\Phi) \cdot F_A$ |
| Applied force | $(x_b, F_{clamp})$ | $(x_b, F_{bolt})$ | Black/Red | $F_A$ |

Where:
$$x_a = +\frac{F_{clamp}}{k_m} + 0.15 \cdot \frac{F_V}{k_m}$$
$$x_b = x_a + 0.12 \cdot \frac{F_V}{k_m}$$

**Load Triangle Fill Coordinates (polygon):**

Upper triangle (bolt force increase region):
$$\left(-\frac{F_V}{k_b},\; F_V\right) \to \left(-\frac{F_{bolt}}{k_b},\; F_{bolt}\right) \to (x_{int},\; F_V) \to \text{close}$$

Lower triangle (clamp force decrease region):
$$\left(+\frac{F_V}{k_m},\; F_V\right) \to \left(+\frac{F_{clamp}}{k_m},\; F_{clamp}\right) \to (x_{int},\; F_V) \to \text{close}$$

### 12.8 Complete Visual Element Drawing Specification

This subsection provides an **exhaustive, element-by-element specification** of every drawable item on the joint diagram, matching the standard VDI 2230 figure. Each element is defined by its type, coordinates, visual style, and drawing order (z-index). This specification is **framework-agnostic** — it can be implemented in matplotlib, PyQt6, Plotly, SVG, HTML Canvas, or any 2D graphics system.

#### 12.8.1 Canvas and Viewport Setup

**Coordinate Ranges (computed from joint data):**

```
# Axis extents
x_left   = -1.20 × (F_sep / k_b)              # Left boundary (bolt side)
x_right  = +1.90 × (F_V / k_m)                 # Right boundary (member + arrows)
y_bottom = -0.03 × F_sep                        # Small padding below zero
y_top    = +1.25 × F_sep                        # Above separation force

# These define the visible plotting area
viewport = { x_min: x_left, x_max: x_right, y_min: y_bottom, y_max: y_top }
```

**Derived Layout Constants:**

```
# Annotation arrow x-positions (right of member line)
x_arrow_inner = (F_clamp / k_m) + 0.15 × (F_V / k_m)    # For bolt↑ and clamp↓ arrows
x_arrow_outer = x_arrow_inner + 0.12 × (F_V / k_m)       # For total F_A arrow
x_label_offset = 0.02 × (F_V / k_m)                       # Text offset from arrow

# Horizontal guide line extents
x_guide_left  = x_left × 0.3                               # How far guides extend left
x_guide_right = x_right × 0.85                             # How far guides extend right
```

#### 12.8.2 Master Element Table (Drawing Order)

Every visual element is listed in the order it should be drawn (back-to-front, lowest z-index first):

| Z | Element ID | Type | Description |
|---|-----------|------|-------------|
| 0 | `GRID` | grid | Background grid lines |
| 1 | `AXIS_V` | line | Vertical axis (y-axis) at x=0 |
| 2 | `AXIS_H` | line | Horizontal axis (x-axis) at y=0 |
| 3 | `FILL_UPPER` | polygon | Upper load triangle fill (bolt increase region) |
| 4 | `FILL_LOWER` | polygon | Lower load triangle fill (clamp decrease region) |
| 5 | `GUIDE_FV` | line | Horizontal dashed guide at preload level F_V |
| 6 | `GUIDE_FB` | line | Horizontal dotted guide at bolt force F_bolt |
| 7 | `GUIDE_FC` | line | Horizontal dotted guide at clamp force F_clamp |
| 8 | `LINE_BOLT` | line | Bolt stiffness line (origin → upper-left) |
| 9 | `LINE_MEMB` | line | Member stiffness line (origin → upper-right) |
| 10 | `LINE_LOAD` | line | Load application line (L_bolt → L_memb) |
| 11 | `LINE_POST_SEP` | line | Post-separation dashed extension |
| 12 | `POINT_P_BOLT` | marker | Bolt at preload (P_bolt) |
| 13 | `POINT_P_MEMB` | marker | Member at preload (P_memb) |
| 14 | `POINT_L_BOLT` | marker | Bolt under load (L_bolt) |
| 15 | `POINT_L_MEMB` | marker | Member under load (L_memb) |
| 16 | `POINT_SEP` | marker | Separation point (S_bolt) |
| 17 | `ARROW_BOLT_INC` | arrow | Bolt force increase (green ↕) |
| 18 | `ARROW_CLAMP_DEC` | arrow | Clamp force decrease (blue ↕) |
| 19 | `ARROW_FA_TOTAL` | arrow | Applied force to joint (red ↕) |
| 20 | `LABEL_BOLT_INC` | text | "Bolt force increase" label |
| 21 | `LABEL_CLAMP_DEC` | text | "Joint clamp force decrease" label |
| 22 | `LABEL_FA_TOTAL` | text | "Applied force to the joint" label |
| 23 | `LABEL_AXIS_X_L` | text | "Bolt Extension" (left of origin) |
| 24 | `LABEL_AXIS_X_R` | text | "Joint Compression" (right of origin) |
| 25 | `LABEL_AXIS_X_FAR` | text | "Extension" (far right) |
| 26 | `LABEL_AXIS_Y` | text | "Force" (top of y-axis) |
| 27 | `LABEL_SEP` | text | Separation point annotation |
| 28 | `YTICK_FV` | tick | Y-axis tick at F_V |
| 29 | `YTICK_FB` | tick | Y-axis tick at F_bolt |
| 30 | `YTICK_FC` | tick | Y-axis tick at F_clamp |
| 31 | `YTICK_FSEP` | tick | Y-axis tick at F_sep |

#### 12.8.3 Detailed Element Definitions

Each element below specifies: **coordinates**, **visual properties**, and **label content**.

---

**Element `GRID` (z=0):**

```
type:    grid
x_range: [x_left, x_right]
y_range: [0, y_top]
style:   { color: '#E8E8E8', linewidth: 0.5, alpha: 0.3 }
spacing: automatic (let framework decide)
```

---

**Element `AXIS_V` (z=1) — Y-Axis at x=0:**

```
type:    vertical_line
x:       0
y_range: [y_bottom, y_top]
style:   { color: 'black', linewidth: 1.2, alpha: 0.5 }
```

**Element `AXIS_H` (z=2) — X-Axis at y=0:**

```
type:    horizontal_line
y:       0
x_range: [x_left, x_right]
style:   { color: 'black', linewidth: 1.2, alpha: 0.5 }
```

---

**Element `FILL_UPPER` (z=3) — Upper Load Triangle (bolt increase):**

```
type:    filled_polygon
vertices: [
    (-F_V/k_b,     F_V),         # P_bolt
    (-F_bolt/k_b,  F_bolt),      # L_bolt
    (x_int_FV,     F_V)          # Load line ∩ preload horizontal
]
style:   { fill_color: '#90EE90', alpha: 0.35, edge: 'none' }

where:
    x_int_FV = -F_bolt/k_b + (F_bolt - F_V)/k_m
```

**Element `FILL_LOWER` (z=4) — Lower Load Triangle (clamp decrease):**

```
type:    filled_polygon
vertices: [
    (+F_V/k_m,     F_V),         # P_memb
    (+F_clamp/k_m, F_clamp),     # L_memb
    (x_int_FV,     F_V)          # Load line ∩ preload horizontal
]
style:   { fill_color: '#ADD8E6', alpha: 0.35, edge: 'none' }
```

---

**Element `GUIDE_FV` (z=5) — Preload Horizontal Guide:**

```
type:    line_segment
from:    (-F_V/k_b,   F_V)       # P_bolt
to:      (+F_V/k_m,   F_V)       # P_memb
style:   { color: 'black', linewidth: 1.0, linestyle: 'dashed', alpha: 0.6 }
extend:  optionally extend right to x_arrow_outer for annotation alignment
```

**Element `GUIDE_FB` (z=6) — Bolt Force Horizontal Guide:**

```
type:    line_segment
from:    (-F_bolt/k_b, F_bolt)
to:      (x_arrow_outer + x_label_offset, F_bolt)
style:   { color: 'gray', linewidth: 0.7, linestyle: 'dotted', alpha: 0.5 }
```

**Element `GUIDE_FC` (z=7) — Clamp Force Horizontal Guide:**

```
type:    line_segment
from:    (+F_clamp/k_m, F_clamp)
to:      (x_arrow_outer + x_label_offset, F_clamp)
style:   { color: 'gray', linewidth: 0.7, linestyle: 'dotted', alpha: 0.5 }
```

---

**Element `LINE_BOLT` (z=8) — Bolt Stiffness Line:**

This is the **left leg of the V-shape** starting at the origin going upper-left.

```
type:    line_segment
from:    (0, 0)                                        # Origin
to:      (-1.15 × F_sep/k_b,  1.15 × F_sep)          # Beyond separation
style:   { color: '#8B4513', linewidth: 2.5, linestyle: 'solid', cap: 'round' }
label:   "Bolt stiffness line (k_b)"

parametric:
    x(t) = -t
    y(t) = k_b × t
    for t ∈ [0, 1.15 × F_sep/k_b]
```

**Element `LINE_MEMB` (z=9) — Member Stiffness Line:**

This is the **right leg of the V-shape** starting at the origin going upper-right.

```
type:    line_segment
from:    (0, 0)                                        # Origin
to:      (+1.3 × F_V/k_m,  1.3 × F_V)                # Beyond preload
style:   { color: '#006400', linewidth: 2.5, linestyle: 'solid', cap: 'round' }
label:   "Member stiffness line (k_m)"

parametric:
    x(t) = +t
    y(t) = k_m × t
    for t ∈ [0, 1.3 × F_V/k_m]
```

**Element `LINE_LOAD` (z=10) — Load Application Line:**

This diagonal line connects the loaded bolt state to the loaded member state. It is **parallel to the member stiffness line** (slope = $-k_m$ in the x-y space).

```
type:    line_segment
from:    (-F_bolt/k_b,  F_bolt)                        # L_bolt (upper-left)
to:      (+F_clamp/k_m, F_clamp)                       # L_memb (lower-right)
style:   { color: '#008080', linewidth: 2.0, linestyle: 'solid' }
label:   "Load line (slope = -k_m)"

# Optional: extend slightly beyond endpoints for visual clarity
extension: 8% of line length on each end
from_ext:  from.x - 0.08 × (to.x - from.x),  from.y + 0.08 × k_m × (to.x - from.x)
to_ext:    to.x + 0.08 × (to.x - from.x),    to.y - 0.08 × k_m × (to.x - from.x)
```

**Element `LINE_POST_SEP` (z=11) — Post-Separation Extension:**

After separation, the bolt follows its own stiffness line from the separation point.

```
type:    line_segment
from:    (-F_sep/k_b,  F_sep)                          # S_bolt (separation point)
to:      (-F_sep/k_b - Δ,  F_sep + k_b × Δ)           # Extended
style:   { color: '#DC143C', linewidth: 1.5, linestyle: 'dashed', alpha: 0.7 }
label:   "Post-separation (bolt only)"

where:
    Δ = 0.15 × F_sep/k_b                               # Extension length
```

---

**Element `POINT_P_BOLT` (z=12) — Bolt at Preload:**

```
type:    circle_marker
center:  (-F_V/k_b,  F_V)
radius:  marker_size (6-8 px)
style:   { fill: '#8B4513', edge: 'black', edge_width: 0.5 }
tooltip: "P_bolt: Bolt at preload"
```

**Element `POINT_P_MEMB` (z=13) — Member at Preload:**

```
type:    circle_marker
center:  (+F_V/k_m,  F_V)
radius:  marker_size
style:   { fill: '#006400', edge: 'black', edge_width: 0.5 }
tooltip: "P_memb: Member at preload"
```

**Element `POINT_L_BOLT` (z=14) — Bolt Under Load:**

```
type:    circle_marker
center:  (-F_bolt/k_b,  F_bolt)
radius:  marker_size
style:   { fill: '#228B22', edge: 'black', edge_width: 0.5 }
tooltip: "L_bolt: Bolt under external load"
```

**Element `POINT_L_MEMB` (z=15) — Member Under Load:**

```
type:    circle_marker
center:  (+F_clamp/k_m,  F_clamp)
radius:  marker_size
style:   { fill: '#4169E1', edge: 'black', edge_width: 0.5 }
tooltip: "L_memb: Member under external load"
```

**Element `POINT_SEP` (z=16) — Separation Point:**

```
type:    x_marker
center:  (-F_sep/k_b,  F_sep)
size:    marker_size × 1.3
style:   { color: '#DC143C', linewidth: 2.0 }
tooltip: "S_bolt: Joint separation point"
```

---

**Elements `ARROW_BOLT_INC`, `ARROW_CLAMP_DEC`, `ARROW_FA_TOTAL` (z=17-19) — Annotation Arrows:**

These are the three double-headed vertical arrows on the right side of the diagram, matching the VDI 2230 figure exactly.

```
# ── Arrow A: Bolt Force Increase (green, inner position) ──
ARROW_BOLT_INC:
    type:      double_headed_arrow (vertical)
    x:         x_arrow_inner
    y_bottom:  F_V                              # From preload level
    y_top:     F_bolt                           # To bolt force level
    direction: vertical, pointing up from F_V
    style:     { color: '#228B22', linewidth: 2.0, head_size: 8 }
    span:      Φ × F_A                          # Arrow height in force units

# ── Arrow B: Joint Clamp Force Decrease (blue, inner position) ──
ARROW_CLAMP_DEC:
    type:      double_headed_arrow (vertical)
    x:         x_arrow_inner
    y_top:     F_V                              # From preload level
    y_bottom:  F_clamp                          # Down to clamp force level
    direction: vertical, pointing down from F_V
    style:     { color: '#4169E1', linewidth: 2.0, head_size: 8 }
    span:      (1-Φ) × F_A                      # Arrow height in force units

# ── Arrow C: Applied Force to the Joint (red, outer position) ──
ARROW_FA_TOTAL:
    type:      double_headed_arrow (vertical)
    x:         x_arrow_outer
    y_bottom:  F_clamp                          # From residual clamp level
    y_top:     F_bolt                           # To bolt force level
    direction: vertical, spanning full F_A
    style:     { color: '#DC143C', linewidth: 2.5, head_size: 10 }
    span:      F_A                               # Total external load
```

---

**Elements `LABEL_*` (z=20-27) — Text Labels:**

```
# ── Label for Bolt Force Increase Arrow ──
LABEL_BOLT_INC:
    type:     text_box
    position: (x_arrow_inner + x_label_offset, F_V + Φ×F_A/2)
    anchor:   left, vertical_center
    text:     "Bolt force\nincrease"
    subtext:  "Φ·F_A = {value} {unit}"
    style:    { font_size: 8, color: '#228B22',
                background: white, border: '#228B22', alpha: 0.8, padding: 3 }

# ── Label for Clamp Force Decrease Arrow ──
LABEL_CLAMP_DEC:
    type:     text_box
    position: (x_arrow_inner + x_label_offset, F_V - (1-Φ)×F_A/2)
    anchor:   left, vertical_center
    text:     "Joint clamp\nforce decrease"
    subtext:  "(1-Φ)·F_A = {value} {unit}"
    style:    { font_size: 8, color: '#4169E1',
                background: white, border: '#4169E1', alpha: 0.8, padding: 3 }

# ── Label for Applied Force Arrow ──
LABEL_FA_TOTAL:
    type:     text_box
    position: (x_arrow_outer + x_label_offset, F_clamp + F_A/2)
    anchor:   left, vertical_center
    text:     "Applied force\nto the joint"
    subtext:  "F_A = {value} {unit}"
    style:    { font_size: 9, color: '#DC143C', font_weight: bold,
                background: white, border: '#DC143C', alpha: 0.9, padding: 3 }

# ── Axis Region Labels ──
LABEL_AXIS_X_L:
    position: (-0.5 × F_sep/k_b, y_bottom + 0.01 × y_top)
    text:     "← Bolt Extension"
    style:    { font_size: 9, color: '#8B4513', font_weight: bold, anchor: center }

LABEL_AXIS_X_R:
    position: (+0.5 × F_V/k_m, y_bottom + 0.01 × y_top)
    text:     "Joint Compression →"
    style:    { font_size: 9, color: '#006400', font_weight: bold, anchor: center }

LABEL_AXIS_X_FAR:
    position: (x_right - 0.02 × (x_right - x_left), 0)
    text:     "Extension"
    style:    { font_size: 10, color: 'black', font_weight: bold, anchor: right }

LABEL_AXIS_Y:
    position: (0, y_top - 0.02 × (y_top - y_bottom))
    text:     "Force"
    style:    { font_size: 10, color: 'black', font_weight: bold, anchor: top_center }

# ── Separation Point Label ──
LABEL_SEP:
    position: offset from POINT_SEP, typically upper-left
    text:     "Separation\nF_A,sep = {value} {unit}"
    style:    { font_size: 8, color: '#DC143C' }
    leader:   arrow from label to POINT_SEP
```

---

**Y-Axis Tick Marks and Labels (z=28-31):**

```
YTICK_FV:
    position: (0, F_V)
    label:    "F_V = {value}"
    style:    { font_size: 8, anchor: right }

YTICK_FB:
    position: (0, F_bolt)
    label:    "F_B = {value}"
    style:    { font_size: 8, anchor: right }

YTICK_FC:
    position: (0, F_clamp)
    label:    "F_clamp = {value}"
    style:    { font_size: 8, anchor: right }

YTICK_FSEP:
    position: (0, F_sep)
    label:    "F_sep = {value}"
    style:    { font_size: 8, anchor: right }
```

#### 12.8.4 Color Scheme Reference

| Element | Hex Color | RGB | Name | Role |
|---------|-----------|-----|------|------|
| Bolt stiffness line | `#8B4513` | (139,69,19) | Saddle Brown | Bolt spring |
| Member stiffness line | `#006400` | (0,100,0) | Dark Green | Member spring |
| Load application line | `#008080` | (0,128,128) | Teal | Load sharing |
| Bolt force increase | `#228B22` | (34,139,34) | Forest Green | ΔF_bolt arrow |
| Clamp force decrease | `#4169E1` | (65,105,225) | Royal Blue | ΔF_clamp arrow |
| Applied force (F_A) | `#DC143C` | (220,20,60) | Crimson | Total load arrow |
| Upper triangle fill | `#90EE90` | (144,238,144) | Light Green | Bolt energy region |
| Lower triangle fill | `#ADD8E6` | (173,216,230) | Light Blue | Member energy region |
| Post-separation | `#DC143C` | (220,20,60) | Crimson | Separation line |
| Preload guide | `#000000` | (0,0,0) | Black | Dashed reference |
| Force level guides | `#808080` | (128,128,128) | Gray | Dotted reference |
| Grid | `#E8E8E8` | (232,232,232) | Light Gray | Background |

#### 12.8.5 Topology Map: How Elements Connect

The visual topology of the diagram follows this connection structure. Arrows (→) indicate which points lie on which lines:

```
ORIGIN (0,0)
    ├──→ LINE_BOLT  ──→ P_bolt ──→ S_bolt ──→ LINE_POST_SEP
    │                      │           │
    │                   GUIDE_FV    GUIDE_FB (extended)
    │                      │
    └──→ LINE_MEMB ──→ P_memb
                           │
                        GUIDE_FV

LINE_LOAD connects:
    L_bolt ◄────────────────────────► L_memb
       │          slope = -k_m           │
       ↓                                 ↓
    on LINE_BOLT                    on LINE_MEMB

Load Triangle (quadrilateral):
    P_bolt ──── L_bolt
       │     ╲    │
    GUIDE_FV  ╲   LINE_LOAD
       │       ╲  │
    P_memb ──── L_memb

Annotation Arrows (right of P_memb):
    ┌─ F_bolt ─── ARROW_BOLT_INC (top)
    │              │
    ├─ F_V ────── ARROW_BOLT_INC (bottom) / ARROW_CLAMP_DEC (top)
    │              │
    ├─ F_clamp ── ARROW_CLAMP_DEC (bottom)
    │
    │    ┌─ F_bolt ── ARROW_FA_TOTAL (top)
    │    │
    └────┤
         │
         └─ F_clamp ─ ARROW_FA_TOTAL (bottom)
```

### 12.9 Pseudocode Drawing Algorithm (Framework-Agnostic)

This algorithm can be implemented in any 2D graphics framework (matplotlib, PyQt6 QPainter, Plotly, SVG, HTML5 Canvas, etc.).

```
FUNCTION draw_joint_diagram(k_b, k_m, F_V, F_A, n=1.0, canvas, options):

    # ════════════════════════════════════════════
    # PHASE 1: COMPUTE ALL VALUES
    # ════════════════════════════════════════════

    Φ ← n × k_b / (k_b + k_m)

    F_bolt  ← F_V + Φ × F_A
    F_clamp ← MAX(F_V - (1 - Φ) × F_A, 0)
    F_sep   ← F_V / (1 - Φ)

    # Key point coordinates
    ORIGIN  ← (0, 0)
    P_bolt  ← (-F_V / k_b,     F_V)
    P_memb  ← (+F_V / k_m,     F_V)
    L_bolt  ← (-F_bolt / k_b,  F_bolt)
    L_memb  ← (+F_clamp / k_m, F_clamp)
    S_bolt  ← (-F_sep / k_b,   F_sep)

    # Load line intersection with preload horizontal
    x_int ← -F_bolt/k_b + (F_bolt - F_V)/k_m

    # Stiffness line endpoints (extended beyond data range)
    BOLT_END ← (-1.15 × F_sep/k_b,  1.15 × F_sep)
    MEMB_END ← (+1.30 × F_V/k_m,    1.30 × F_V)

    # Annotation positions
    x_arr_1 ← L_memb.x + 0.15 × P_memb.x    # Inner arrows
    x_arr_2 ← x_arr_1 + 0.12 × P_memb.x      # Outer arrow
    x_label ← 0.02 × P_memb.x                 # Label offset

    # ════════════════════════════════════════════
    # PHASE 2: SET UP CANVAS
    # ════════════════════════════════════════════

    x_min ← -1.20 × F_sep / k_b
    x_max ← +1.90 × F_V / k_m
    y_min ← -0.03 × F_sep
    y_max ← +1.25 × F_sep

    canvas.set_viewport(x_min, x_max, y_min, y_max)
    canvas.set_background('white')

    # ════════════════════════════════════════════
    # PHASE 3: DRAW BACKGROUND ELEMENTS (z=0-2)
    # ════════════════════════════════════════════

    IF options.show_grid:
        canvas.draw_grid(color='#E8E8E8', linewidth=0.5, alpha=0.3)

    canvas.draw_line(x=0, y1=y_min, y2=y_max,              # Y-axis
                     color='black', width=1.2, alpha=0.5)
    canvas.draw_line(y=0, x1=x_min, x2=x_max,              # X-axis
                     color='black', width=1.2, alpha=0.5)

    # ════════════════════════════════════════════
    # PHASE 4: DRAW FILLED REGIONS (z=3-4)
    # ════════════════════════════════════════════

    IF options.show_triangle_fill:

        # Upper triangle (bolt force increase zone)
        canvas.fill_polygon(
            vertices = [P_bolt, L_bolt, (x_int, F_V)],
            fill_color = '#90EE90', alpha = 0.35
        )

        # Lower triangle (clamp force decrease zone)
        canvas.fill_polygon(
            vertices = [P_memb, L_memb, (x_int, F_V)],
            fill_color = '#ADD8E6', alpha = 0.35
        )

    # ════════════════════════════════════════════
    # PHASE 5: DRAW GUIDE LINES (z=5-7)
    # ════════════════════════════════════════════

    # Preload horizontal (dashed)
    canvas.draw_line_segment(
        from = P_bolt, to = (x_arr_2 + x_label, F_V),
        color = 'black', width = 1.0, dash = 'dashed', alpha = 0.6
    )

    # Bolt force level (dotted, extends to arrows)
    canvas.draw_line_segment(
        from = L_bolt, to = (x_arr_2 + x_label, F_bolt),
        color = 'gray', width = 0.7, dash = 'dotted', alpha = 0.5
    )

    # Clamp force level (dotted, extends to arrows)
    canvas.draw_line_segment(
        from = L_memb, to = (x_arr_2 + x_label, F_clamp),
        color = 'gray', width = 0.7, dash = 'dotted', alpha = 0.5
    )

    # ════════════════════════════════════════════
    # PHASE 6: DRAW STIFFNESS & LOAD LINES (z=8-11)
    # ════════════════════════════════════════════

    # Bolt stiffness line (brown, from origin going upper-left)
    canvas.draw_line_segment(
        from = ORIGIN, to = BOLT_END,
        color = '#8B4513', width = 2.5, cap = 'round'
    )

    # Member stiffness line (green, from origin going upper-right)
    canvas.draw_line_segment(
        from = ORIGIN, to = MEMB_END,
        color = '#006400', width = 2.5, cap = 'round'
    )

    # Load application line (teal, from L_bolt to L_memb)
    # Optionally extend 8% on each side
    dx ← L_memb.x - L_bolt.x
    ext ← 0.08 × dx
    canvas.draw_line_segment(
        from = (L_bolt.x - ext,  L_bolt.y + k_m × ext),
        to   = (L_memb.x + ext,  L_memb.y - k_m × ext),
        color = '#008080', width = 2.0
    )

    # Post-separation dashed extension
    IF options.show_post_separation:
        Δ ← 0.15 × F_sep / k_b
        canvas.draw_line_segment(
            from = S_bolt,
            to   = (S_bolt.x - Δ, S_bolt.y + k_b × Δ),
            color = '#DC143C', width = 1.5, dash = 'dashed', alpha = 0.7
        )

    # ════════════════════════════════════════════
    # PHASE 7: DRAW MARKERS (z=12-16)
    # ════════════════════════════════════════════

    marker_size ← 6

    canvas.draw_circle(P_bolt, r=marker_size,
                       fill='#8B4513', edge='black', edge_width=0.5)
    canvas.draw_circle(P_memb, r=marker_size,
                       fill='#006400', edge='black', edge_width=0.5)
    canvas.draw_circle(L_bolt, r=marker_size,
                       fill='#228B22', edge='black', edge_width=0.5)
    canvas.draw_circle(L_memb, r=marker_size,
                       fill='#4169E1', edge='black', edge_width=0.5)

    IF options.show_separation:
        canvas.draw_x_marker(S_bolt, size=marker_size × 1.3,
                             color='#DC143C', width=2.0)

    # ════════════════════════════════════════════
    # PHASE 8: DRAW ANNOTATION ARROWS (z=17-19)
    # ════════════════════════════════════════════

    IF options.show_annotations:

        # Arrow A: Bolt force increase (green ↕)
        canvas.draw_double_arrow(
            x = x_arr_1,
            y_from = F_V,
            y_to = F_bolt,
            color = '#228B22', width = 2.0, head_size = 8
        )

        # Arrow B: Clamp force decrease (blue ↕)
        canvas.draw_double_arrow(
            x = x_arr_1,
            y_from = F_V,
            y_to = F_clamp,
            color = '#4169E1', width = 2.0, head_size = 8
        )

        # Arrow C: Applied force total (red ↕)
        canvas.draw_double_arrow(
            x = x_arr_2,
            y_from = F_clamp,
            y_to = F_bolt,
            color = '#DC143C', width = 2.5, head_size = 10
        )

    # ════════════════════════════════════════════
    # PHASE 9: DRAW TEXT LABELS (z=20-31)
    # ════════════════════════════════════════════

    IF options.show_annotations:

        canvas.draw_text_box(
            position = (x_arr_1 + x_label, F_V + Φ×F_A/2),
            text = "Bolt force\nincrease",
            sub  = FORMAT("Φ·F_A = {:.0f} {}", Φ×F_A, unit),
            color = '#228B22', size = 8, bg = 'white'
        )

        canvas.draw_text_box(
            position = (x_arr_1 + x_label, F_V - (1-Φ)×F_A/2),
            text = "Joint clamp\nforce decrease",
            sub  = FORMAT("(1-Φ)·F_A = {:.0f} {}", (1-Φ)×F_A, unit),
            color = '#4169E1', size = 8, bg = 'white'
        )

        canvas.draw_text_box(
            position = (x_arr_2 + x_label, F_clamp + F_A/2),
            text = "Applied force\nto the joint",
            sub  = FORMAT("F_A = {:.0f} {}", F_A, unit),
            color = '#DC143C', size = 9, bold = TRUE, bg = 'white'
        )

    # Axis region labels
    canvas.draw_text(
        position = (-0.5 × ABS(BOLT_END.x), y_min + 0.01 × y_max),
        text = "← Bolt Extension",
        color = '#8B4513', size = 9, bold = TRUE, anchor = 'center'
    )

    canvas.draw_text(
        position = (+0.5 × MEMB_END.x, y_min + 0.01 × y_max),
        text = "Joint Compression →",
        color = '#006400', size = 9, bold = TRUE, anchor = 'center'
    )

    canvas.draw_text(
        position = (x_max × 0.95, 0),
        text = "Extension",
        color = 'black', size = 10, bold = TRUE, anchor = 'right'
    )

    canvas.draw_text(
        position = (0, y_max × 0.98),
        text = "Force",
        color = 'black', size = 10, bold = TRUE, anchor = 'top_center'
    )

    # Y-axis tick labels
    FOR EACH (value, label) IN [
        (F_clamp, "F_clamp"),
        (F_V,     "F_V"),
        (F_bolt,  "F_B"),
        (F_sep,   "F_sep")   IF options.show_separation
    ]:
        canvas.draw_ytick(y=value, label=FORMAT("{} = {:.0f}", label, value))

    # ════════════════════════════════════════════
    # PHASE 10: FINALIZE
    # ════════════════════════════════════════════

    canvas.set_title(options.title)
    canvas.draw_legend()

    IF options.save_path:
        canvas.export(options.save_path, dpi=options.dpi)

    RETURN canvas

END FUNCTION
```

### 12.10 Normalized Coordinate System (Dimensionless)

For implementation in responsive/resizable GUI widgets, it is useful to normalize all coordinates to a unit-less $[0, 1]$ range.

**Normalization factors:**

$$x_{norm} = \frac{x - x_{min}}{x_{max} - x_{min}} \quad;\quad y_{norm} = \frac{y - y_{min}}{y_{max} - y_{min}}$$

**Key normalized positions (for a widget of pixel width $W$ and height $H$):**

$$x_{pixel} = x_{norm} \times W \quad;\quad y_{pixel} = (1 - y_{norm}) \times H \quad \text{(Y inverted for screen coords)}$$

**Normalized key points table:**

| Point | $x_{norm}$ | $y_{norm}$ |
|-------|-----------|-----------|
| Origin | $\frac{0 - x_{min}}{x_{max} - x_{min}}$ | $\frac{0 - y_{min}}{y_{max} - y_{min}}$ |
| P_bolt | $\frac{-F_V/k_b - x_{min}}{x_{max} - x_{min}}$ | $\frac{F_V - y_{min}}{y_{max} - y_{min}}$ |
| P_memb | $\frac{+F_V/k_m - x_{min}}{x_{max} - x_{min}}$ | $\frac{F_V - y_{min}}{y_{max} - y_{min}}$ |
| L_bolt | $\frac{-F_{bolt}/k_b - x_{min}}{x_{max} - x_{min}}$ | $\frac{F_{bolt} - y_{min}}{y_{max} - y_{min}}$ |
| L_memb | $\frac{+F_{clamp}/k_m - x_{min}}{x_{max} - x_{min}}$ | $\frac{F_{clamp} - y_{min}}{y_{max} - y_{min}}$ |
| S_bolt | $\frac{-F_{sep}/k_b - x_{min}}{x_{max} - x_{min}}$ | $\frac{F_{sep} - y_{min}}{y_{max} - y_{min}}$ |

This normalization allows the same diagram to be rendered at any resolution or aspect ratio while maintaining geometric correctness.

### 12.11 Graph State Machine for Interactive Rendering

For the Bolt Analysis Studio PyQt6 GUI, the diagram can be implemented as a state machine that redraws on parameter changes:

```
STATES:
    IDLE          → Diagram is static, showing current data
    COMPUTING     → Parameters changed, recalculating
    ANIMATING     → Smooth transition between states (optional)
    HOVERING      → Mouse over a point, showing tooltip

TRANSITIONS:
    parameter_changed(k_b, k_m, F_V, F_A, n):
        IDLE → COMPUTING
        recompute JointDiagramData
        COMPUTING → IDLE (triggers redraw)

    mouse_move(x_pixel, y_pixel):
        convert to data coordinates
        check proximity to key points (P_bolt, P_memb, L_bolt, L_memb, S_bolt)
        IF close to point:
            IDLE → HOVERING (show tooltip)
        ELSE:
            HOVERING → IDLE (hide tooltip)

    slider_drag(parameter, value):
        IDLE → ANIMATING
        interpolate from old_value to new_value
        for each frame: recompute + redraw
        ANIMATING → IDLE

SIGNALS (for PyQt6 integration):
    diagram_updated(JointDiagramData)     → emitted after recompute
    point_hovered(point_name, x, y, F)    → emitted on mouse proximity
    separation_warning(bool)               → emitted if F_A approaches F_sep
```

### 12.12 Overall Composite Figure Layout (Reference Figure Reproduction)

This subsection specifies the **complete composite figure** as shown in the VDI 2230 reference illustration — a two-panel figure with the **physical bolted joint schematic** on the left and the **force-extension diagram** on the right. This is the standard presentation format used in VDI 2230, Bickford, Shigley, and most bolted joint textbooks.

#### 12.12.1 Two-Panel Composite Layout

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                                                                                     │
│  ┌──────────────────────┐   ┌───────────────────────────────────────────────────┐   │
│  │                      │   │                                                   │   │
│  │   PANEL A            │   │   PANEL B                                         │   │
│  │   Physical Joint     │   │   Force-Extension Diagram                         │   │
│  │   Schematic          │   │                                                   │   │
│  │                      │   │   ▲ Force                                         │   │
│  │    ← Force applied   │   │   │         ╱                    ┃ Bolt force     │   │
│  │       to the joint   │   │   │       ╱     ╲               ┃ increase       │   │
│  │                      │   │   │     ╱         ╲   ┃         ┃───────────     │   │
│  │   ┌────┐             │   │   │   ╱    LOAD    ╲  ┃ Clamp   ┃               │   │
│  │   │BOLT│             │   │   │ ╱    TRIANGLE   ╲ ┃ force   ┃ Applied       │   │
│  │   │HEAD│             │   │   │╱                 ╲┃ decrease ┃ force         │   │
│  │   ├────┤  ┌──┐       │   │   ○───────────────────┃─────────┃──→ Extension  │   │
│  │   │SHANK│ │  │       │   │   │                                              │   │
│  │   │    │ │  │       │   │   │  ◄─ Bolt ─┼─ Joint ─►                        │   │
│  │   ├────┤ │  │       │   │   │  Extension │ Compression                      │   │
│  │   │THRD│ │FL│       │   │                                                   │   │
│  │   │    │ │AN│       │   │                                                   │   │
│  │   ├────┤ │GE│       │   │                                                   │   │
│  │   │NUT │ │  │       │   │                                                   │   │
│  │   └────┘ └──┘       │   │                                                   │   │
│  │                      │   │                                                   │   │
│  └──────────────────────┘   └───────────────────────────────────────────────────┘   │
│                                                                                     │
│  width ratio: ≈ 25%          width ratio: ≈ 75%                                    │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

**Layout Specification:**

| Property | Panel A (Schematic) | Panel B (Diagram) |
|----------|--------------------|--------------------|
| Width ratio | 0.22–0.28 of total | 0.72–0.78 of total |
| Height ratio | 1.0 (full height) | 1.0 (full height) |
| Background | Light gray or white | White |
| Border | Optional thin frame | Standard axes |
| Content origin | Center of panel | Data-driven (see §12.1) |

**Recommended figure dimensions:**

| Context | Total Width | Total Height | Aspect Ratio |
|---------|-------------|-------------|--------------|
| Publication/report | 180 mm (7") | 100 mm (4") | 1.8:1 |
| Slide/presentation | 254 mm (10") | 140 mm (5.5") | 1.8:1 |
| GUI widget | 800–1200 px | 450–700 px | 1.7–1.8:1 |
| Screen (matplotlib) | 14 in | 8 in | 1.75:1 |

#### 12.12.2 Panel A — Physical Joint Schematic

The left panel shows a **cross-sectional view** of the bolted joint assembly with an external force arrow. This provides physical context for the mathematical diagram.

**Schematic Elements (drawn in normalized panel coordinates [0,1] × [0,1]):**

```
PANEL A COORDINATE SYSTEM:
  Origin: top-left of panel
  X: 0 (left) → 1 (right)
  Y: 0 (top) → 1 (bottom)

ELEMENT LIST:

1. EXTERNAL FORCE ARROW
   Type:     thick arrow
   From:     (0.05, 0.20)
   To:       (0.35, 0.20)
   Head:     pointing right (toward bolt head)
   Color:    black
   Width:    3–4 pt
   Label:    "Force applied\nto the joint"
   Label_pos: (0.05, 0.12), left-aligned, italic
   Font:     9pt, black

2. BOLT HEAD (top member)
   Type:     filled rectangle
   Bounds:   x=[0.32, 0.52], y=[0.15, 0.25]
   Fill:     dark green (#006400)
   Outline:  black, 1.5pt

3. UPPER FLANGE (top clamped member)
   Type:     filled rectangle
   Bounds:   x=[0.25, 0.75], y=[0.25, 0.45]
   Fill:     dark green (#006400)
   Outline:  black, 1.5pt

4. BOLT SHANK (through flanges)
   Type:     filled rectangle (thin, vertical)
   Bounds:   x=[0.39, 0.45], y=[0.25, 0.75]
   Fill:     dark green (#2E8B57)
   Outline:  black, 1pt

5. LOWER FLANGE (bottom clamped member)
   Type:     filled rectangle
   Bounds:   x=[0.25, 0.75], y=[0.55, 0.75]
   Fill:     dark green (#006400)
   Outline:  black, 1.5pt

6. NUT (bottom)
   Type:     filled rectangle
   Bounds:   x=[0.32, 0.52], y=[0.75, 0.85]
   Fill:     dark green (#006400)
   Outline:  black, 1.5pt

7. CLAMPING INTERFACE (gap between flanges)
   Type:     dashed line or gap
   From:     (0.25, 0.50)
   To:       (0.75, 0.50)
   Style:    dashed, 1pt, gray

8. COMPRESSION CONE (Rötscher cone, optional)
   Type:     two diagonal dashed lines (frustum outline)
   Line 1:  (0.35, 0.25) → (0.20, 0.50) → (0.35, 0.75)
   Line 2:  (0.49, 0.25) → (0.64, 0.50) → (0.49, 0.75)
   Style:   dashed, thin, brown/orange, alpha=0.4

9. FORCE ARROWS ON BOLT (tension indicators)
   Arrow_up:   (0.42, 0.10) → (0.42, 0.17), red, thin
   Arrow_down: (0.42, 0.83) → (0.42, 0.90), red, thin
   Label:      "F_V" at (0.46, 0.08)
```

**Simplified Alternative (for matplotlib with patches):**

If drawing a detailed schematic is too complex, a simplified version uses rectangular patches:

```
SIMPLIFIED SCHEMATIC (matplotlib patches):

  # Bolt head (top hex represented as rect)
  Rectangle(xy=(0.35, 0.78), width=0.20, height=0.08, fc='#006400', ec='black')

  # Upper flange
  Rectangle(xy=(0.20, 0.45), width=0.50, height=0.33, fc='#2E8B57', ec='black')

  # Bolt shank
  Rectangle(xy=(0.41, 0.12), width=0.08, height=0.66, fc='#228B22', ec='black')

  # Lower flange
  Rectangle(xy=(0.20, 0.12), width=0.50, height=0.33, fc='#2E8B57', ec='black')

  # Nut (bottom)
  Rectangle(xy=(0.35, 0.04), width=0.20, height=0.08, fc='#006400', ec='black')

  # Force arrow (pointing down into bolt head)
  FancyArrow(x=0.45, y=0.98, dx=0, dy=-0.10, width=0.06, fc='black')

  # Label
  Text(0.10, 0.95, "Force applied\nto the joint", fontsize=8)
```

#### 12.12.3 Panel B — Force-Extension Diagram (Complete Drawing Specification)

Panel B contains the full force-extension diagram. All coordinates below are in **data units** (extension [mm] on x-axis, force [N or kN] on y-axis).

**Complete Element-by-Element Drawing Sequence:**

The figure from the reference shows the following distinct visual layers, listed in back-to-front order:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│     ▲ Force                        Bolt force                              │
│     │                              increase                                │
│     │                ╱          ╔══╗  ↕ (green)   ┃                        │
│ F_B ┤─ ─ ─ ─ ─ ─ ─╱─ ─ ─ ─ ─ ║  ║               ┃                        │
│     │            ╱╱            ║  ║  Joint         ┃ Applied               │
│     │          ╱╱  ╲           ║  ║  clamp         ┃ force                 │
│ F_V ┤─ ─ ─ ●╱─ ─ ─ ─╲─ ─ ─●  ║  ║  force         ┃ to the               │
│     │      ╱╱          ╲       ║  ║  decrease       ┃ joint                │
│     │    ╱╱    LOAD     ╲      ║  ║  ↕ (blue)      ┃ ↕ (red)             │
│F_cl ┤─ ╱╱─ ─ TRIANGLE─ ─╲─●  ╚══╝               ┃                        │
│     │╱╱                   ╲                        ┃                        │
│     ●═══════════════════════╲══════════════════════┃═══════════→ Extension  │
│  ORIGIN                                                                     │
│     │     ◄── Bolt ──┤── Joint ──►                                          │
│     │      Extension  │ Compression                                         │
│     │                                                                       │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Layer 0 — Background and Axes:**

| Element | Specification |
|---------|--------------|
| Background | White fill |
| Grid | Light gray lines (#E8E8E8), alpha=0.15–0.3 |
| Y-axis | Vertical black line at x=0, lw=1.2 |
| X-axis | Horizontal black line at y=0, lw=1.2 |
| Origin marker | Small circle or dot at (0,0) |

**Layer 1 — Load Triangle Fill (semi-transparent polygons):**

| Region | Vertices | Fill Color | Alpha |
|--------|----------|-----------|-------|
| Upper triangle (bolt increase) | P_bolt → L_bolt → $(x_{int}, F_V)$ → close | Light green (#90EE90) | 0.30–0.40 |
| Lower triangle (clamp decrease) | P_memb → L_memb → $(x_{int}, F_V)$ → close | Light blue (#ADD8E6) | 0.30–0.40 |

Where $x_{int} = -F_{bolt}/k_b + \Phi \cdot F_A / k_m$ (load line intersection at $y = F_V$).

**Layer 2 — Horizontal Guide Lines (dashed/dotted):**

| Line | Y-value | X-range | Style | Color | Width |
|------|---------|---------|-------|-------|-------|
| Preload | $F_V$ | $[-F_V/k_b,\; +F_V/k_m]$ | dashed `'--'` | black | 1.0 |
| Bolt force | $F_{bolt}$ | $[-F_{bolt}/k_b,\; x_{arrow\_inner}]$ | dotted `':'` | gray | 0.7 |
| Clamp force | $F_{clamp}$ | $[-F_V/k_b \times 0.3,\; +F_{clamp}/k_m]$ | dotted `':'` | gray | 0.7 |

**Layer 3 — Primary Stiffness Lines (the two main lines from origin):**

| Line | From | To | Color | Width | Cap |
|------|------|----|-------|-------|-----|
| Bolt stiffness | $(0, 0)$ | $(-1.15 \cdot F_{sep}/k_b,\; 1.15 \cdot F_{sep})$ | Dark brown (#8B4513) | 2.5 | Round |
| Member stiffness | $(0, 0)$ | $(+1.3 \cdot F_V/k_m,\; 1.3 \cdot F_V)$ | Dark green (#006400) | 2.5 | Round |

**Layer 4 — Load Application Line (diagonal connecting loaded states):**

| Line | From (L_bolt) | To (L_memb) | Color | Width |
|------|---------------|-------------|-------|-------|
| Load line | $(-F_{bolt}/k_b,\; F_{bolt})$ | $(+F_{clamp}/k_m,\; F_{clamp})$ | Teal (#008080) | 2.0 |

Extend slightly beyond both endpoints by $\Delta x = 0.08 \times |x_{L\_memb} - x_{L\_bolt}|$:

$$x_{ext,left} = -\frac{F_{bolt}}{k_b} - \Delta x \quad;\quad y_{ext,left} = F_{bolt} + k_m \cdot \Delta x$$

$$x_{ext,right} = +\frac{F_{clamp}}{k_m} + \Delta x \quad;\quad y_{ext,right} = F_{clamp} - k_m \cdot \Delta x$$

**Layer 5 — Post-Separation Line (dashed, after kink):**

| Line | From (S_bolt) | To (extended) | Color | Width | Style |
|------|---------------|--------------|-------|-------|-------|
| Post-separation | $(-F_{sep}/k_b,\; F_{sep})$ | $(-F_{sep}/k_b - \Delta,\; F_{sep} + k_b \cdot \Delta)$ | Crimson (#DC143C) | 1.5 | Dashed |

Where $\Delta = 0.15 \times F_{sep}/k_b$

**Layer 6 — Key Point Markers:**

| Point | Coordinates $(x, y)$ | Shape | Size | Fill Color | Edge |
|-------|---------------------|-------|------|-----------|------|
| P_bolt | $(-F_V/k_b,\; F_V)$ | circle | 60 | #8B4513 (brown) | black, 0.5pt |
| P_memb | $(+F_V/k_m,\; F_V)$ | circle | 60 | #006400 (green) | black, 0.5pt |
| L_bolt | $(-F_{bolt}/k_b,\; F_{bolt})$ | circle | 60 | #228B22 (forest) | black, 0.5pt |
| L_memb | $(+F_{clamp}/k_m,\; F_{clamp})$ | circle | 60 | #4169E1 (blue) | black, 0.5pt |
| S_bolt | $(-F_{sep}/k_b,\; F_{sep})$ | × marker | 80 | #DC143C (crimson) | 2pt lines |

**Layer 7 — Annotation Arrows (right side of diagram, matching reference figure):**

These are the three vertical double-headed arrows positioned to the **right** of the member stiffness line:

```
ARROW LAYOUT (right side of diagram):

                                      x_a         x_b
                                       │           │
                                       │           │
     F_bolt ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ┬ ─ ─ ─ ─ ─┬─ ─ ─ ─ ─
                                       │           │
                                       │ GREEN     │
                                       │ "Bolt     │  RED
                                       │  force    │  "Applied
                                       │  increase"│   force
                                       │           │   to the
        F_V ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ┤           │   joint"
                                       │           │
                                       │ BLUE      │
                                       │ "Joint    │
                                       │  clamp    │
                                       │  force    │
                                       │  decrease"│
                                       │           │
     F_clamp ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─┴ ─ ─ ─ ─ ─┴─ ─ ─ ─ ─
```

**Arrow coordinate specification:**

```
# Position computation
x_a = (+F_clamp / k_m) + 0.15 × (F_V / k_m)     # Inner column
x_b = x_a + 0.12 × (F_V / k_m)                    # Outer column
label_dx = 0.02 × (F_V / k_m)                      # Text offset from arrow

# ──── ARROW A: Bolt Force Increase (green, inner column) ────
arrow_A:
    type:        double-headed arrow (↕)
    x:           x_a
    y_bottom:    F_V
    y_top:       F_bolt
    color:       #228B22 (forest green)
    linewidth:   2.0
    head_scale:  15
    label:       "Bolt force\nincrease"
    label_pos:   (x_a + label_dx, F_V + Φ×F_A/2)     # centered vertically
    label_color: #228B22
    label_size:  8pt
    label_align: left, center
    label_value: "Φ·F_A = {value}"    # optional numeric readout
    label_box:   white fill, green edge, round corners, alpha=0.8

# ──── ARROW B: Joint Clamp Force Decrease (blue, inner column) ────
arrow_B:
    type:        double-headed arrow (↕)
    x:           x_a
    y_bottom:    F_clamp
    y_top:       F_V
    color:       #4169E1 (royal blue)
    linewidth:   2.0
    head_scale:  15
    label:       "Joint clamp\nforce decrease"
    label_pos:   (x_a + label_dx, F_V - (1-Φ)×F_A/2)  # centered vertically
    label_color: #4169E1
    label_size:  8pt
    label_align: left, center
    label_value: "(1-Φ)·F_A = {value}"
    label_box:   white fill, blue edge, round corners, alpha=0.8

# ──── ARROW C: Applied Force to the Joint (red, outer column) ────
arrow_C:
    type:        double-headed arrow (↕)
    x:           x_b
    y_bottom:    F_clamp
    y_top:       F_bolt
    color:       #DC143C (crimson red)
    linewidth:   2.5
    head_scale:  18
    label:       "Applied force\nto the joint"
    label_pos:   (x_b + label_dx, F_clamp + F_A/2)    # centered vertically
    label_color: #DC143C
    label_size:  9pt, bold
    label_align: left, center
    label_value: "F_A = {value}"
    label_box:   white fill, red edge, round corners, alpha=0.9
```

**Layer 8 — Axis Labels and Region Annotations:**

| Label | Text | Position | Font | Color | Alignment |
|-------|------|----------|------|-------|-----------|
| Y-axis title | "Force" | Top of y-axis | 11pt, bold | black | center |
| X-axis title | "Extension" | Right end of x-axis | 11pt, bold | black | right |
| Left region | "← Bolt Extension" | Below x-axis, left half | 9pt, bold | #8B4513 | center |
| Right region | "Joint Compression →" | Below x-axis, right half | 9pt, bold | #006400 | center |

**Layer 9 — Y-Axis Tick Labels (force levels):**

| Tick | Y-value | Label Format | Font |
|------|---------|-------------|------|
| Zero | 0 | "0" | 8pt |
| Clamp force | $F_{clamp}$ | "$F_{clamp}$ = {value}" | 8pt |
| Preload | $F_V$ | "$F_V$ = {value}" | 8pt |
| Bolt force | $F_{bolt}$ | "$F_B$ = {value}" | 8pt |
| Separation | $F_{sep}$ | "$F_{sep}$ = {value}" | 8pt (optional) |

#### 12.12.4 Composite Figure Drawing Algorithm

The complete composite figure is drawn with this sequence:

```
FUNCTION draw_composite_joint_figure(joint_params, canvas):

    # ════════════════════════════════════════════
    # STEP 1: CREATE FIGURE LAYOUT
    # ════════════════════════════════════════════

    figure_width  = 14 inches  (or 360 mm)
    figure_height = 8 inches   (or 200 mm)

    # Two panels: 25% left (schematic) + 75% right (diagram)
    panel_A = subplot(1, 2, 1, width_ratio=0.25)   # Physical schematic
    panel_B = subplot(1, 2, 2, width_ratio=0.75)   # Force-extension diagram

    # Panel A has no standard axes (custom drawing)
    panel_A.set_axis_off()
    panel_A.set_xlim(0, 1)
    panel_A.set_ylim(0, 1)

    # ════════════════════════════════════════════
    # STEP 2: DRAW PANEL A — PHYSICAL SCHEMATIC
    # ════════════════════════════════════════════

    # Force arrow (pointing right/down toward joint)
    draw_arrow(panel_A, from=(0.05, 0.82), to=(0.32, 0.82),
               color='black', width=0.04, head_width=0.08)
    draw_text(panel_A, (0.05, 0.92),
              "Force applied\nto the joint",
              fontsize=8, fontstyle='italic')

    # Bolt head (top)
    draw_rect(panel_A, (0.33, 0.76), w=0.22, h=0.08,
              fill='#006400', edge='black', lw=1.5)

    # Upper flange
    draw_rect(panel_A, (0.18, 0.46), w=0.52, h=0.30,
              fill='#2E8B57', edge='black', lw=1.5)

    # Bolt shank (through both flanges)
    draw_rect(panel_A, (0.40, 0.16), w=0.08, h=0.60,
              fill='#228B22', edge='black', lw=1.0)

    # Lower flange
    draw_rect(panel_A, (0.18, 0.16), w=0.52, h=0.30,
              fill='#2E8B57', edge='black', lw=1.5)

    # Nut (bottom)
    draw_rect(panel_A, (0.33, 0.08), w=0.22, h=0.08,
              fill='#006400', edge='black', lw=1.5)

    # Clamping interface line
    draw_line(panel_A, from=(0.18, 0.46), to=(0.70, 0.46),
              color='gray', style='dashed', lw=0.8)

    # Optional: Rötscher compression cone (faint dashed lines)
    draw_line(panel_A, from=(0.37, 0.76), to=(0.22, 0.46),
              color='#8B4513', style='dashed', lw=0.5, alpha=0.4)
    draw_line(panel_A, from=(0.51, 0.76), to=(0.66, 0.46),
              color='#8B4513', style='dashed', lw=0.5, alpha=0.4)
    draw_line(panel_A, from=(0.37, 0.16), to=(0.22, 0.46),
              color='#8B4513', style='dashed', lw=0.5, alpha=0.4)
    draw_line(panel_A, from=(0.51, 0.16), to=(0.66, 0.46),
              color='#8B4513', style='dashed', lw=0.5, alpha=0.4)

    # ════════════════════════════════════════════
    # STEP 3: DRAW PANEL B — FORCE-EXTENSION DIAGRAM
    # ════════════════════════════════════════════

    # (Use the full drawing algorithm from §12.9 or §13.2)
    # All Layers 0–9 from §12.12.3 are drawn on panel_B

    draw_joint_diagram(panel_B, joint_params)

    # ════════════════════════════════════════════
    # STEP 4: FINALIZE COMPOSITE FIGURE
    # ════════════════════════════════════════════

    tight_layout()
    RETURN figure

END FUNCTION
```

#### 12.12.5 Reference Color Palette (Matching VDI 2230 Standard Figure)

| Element | Hex Code | RGB | Name | Usage |
|---------|---------|-----|------|-------|
| Bolt line | `#8B4513` | (139, 69, 19) | Saddle Brown | Bolt stiffness line |
| Member line | `#006400` | (0, 100, 0) | Dark Green | Member stiffness line |
| Load line | `#008080` | (0, 128, 128) | Teal | Load application diagonal |
| Bolt increase arrow | `#228B22` | (34, 139, 34) | Forest Green | ΦF_A annotation |
| Clamp decrease arrow | `#4169E1` | (65, 105, 225) | Royal Blue | (1-Φ)F_A annotation |
| Applied force arrow | `#DC143C` | (220, 20, 60) | Crimson | F_A total annotation |
| Upper triangle fill | `#90EE90` | (144, 238, 144) | Light Green | Bolt force increase region |
| Lower triangle fill | `#ADD8E6` | (173, 216, 230) | Light Blue | Clamp decrease region |
| Post-separation | `#DC143C` | (220, 20, 60) | Crimson | Dashed post-sep line |
| Joint schematic | `#006400` | (0, 100, 0) | Dark Green | Bolt/flange components |
| Joint schematic alt | `#2E8B57` | (46, 139, 87) | Sea Green | Flange body fill |
| Guides | `#808080` | (128, 128, 128) | Gray | Dotted force-level lines |
| Preload line | `#000000` | (0, 0, 0) | Black | Dashed preload horizontal |

#### 12.12.6 Overall Graph Mapping: Figure Element ↔ Physical Meaning ↔ Equation

This table provides the **complete mapping** between every visual element in the reference figure, its physical meaning, and the equation that computes it:

| Visual Element in Figure | Physical Meaning | Governing Equation | Plot Coordinates |
|--------------------------|-----------------|--------------------|--------------------|
| Brown line (origin → upper-left) | Bolt acts as tension spring | $F = k_b \cdot \delta_b$ | $(0,0)$ to $(-\delta_b, k_b \delta_b)$ |
| Green line (origin → upper-right) | Members act as compression spring | $F = k_m \cdot \delta_m$ | $(0,0)$ to $(+\delta_m, k_m \delta_m)$ |
| Teal diagonal line | External load shared between bolt & members | slope $= -k_m$ (parallel to member line) | L_bolt to L_memb |
| Horizontal dashed at $F_V$ | Assembly preload (initial tension) | $F_V$ = controlled by torque | $y = F_V$ across both lines |
| Upper green shaded triangle | Energy stored in bolt from external load | $\Delta E_b = \frac{(\Phi F_A)^2}{2 k_b}$ | P_bolt → L_bolt → $x_{int}$ |
| Lower blue shaded triangle | Energy released from members by external load | $\Delta E_m = \frac{((1-\Phi)F_A)^2}{2 k_m}$ | P_memb → L_memb → $x_{int}$ |
| Green arrow (right side) | Bolt force increases by fraction Φ of F_A | $\Delta F_b = \Phi \cdot F_A$ | Vertical from $F_V$ to $F_{bolt}$ |
| Blue arrow (right side) | Clamp force decreases by fraction (1-Φ) of F_A | $\Delta F_m = (1-\Phi) \cdot F_A$ | Vertical from $F_V$ to $F_{clamp}$ |
| Red arrow (right side) | Total external force applied to joint | $F_A = \Delta F_b + \Delta F_m$ | Vertical from $F_{clamp}$ to $F_{bolt}$ |
| "Bolt Extension" label | Bolt stretching under tension | $\delta_b = F / k_b$ | X-axis, left of origin |
| "Joint Compression" label | Members compressing under clamp | $\delta_m = F / k_m$ | X-axis, right of origin |
| × marker (separation) | Joint opens, members lose contact | $F_{A,sep} = F_V / (1-\Phi)$ | $(-F_{sep}/k_b, F_{sep})$ |
| Dashed line (post-separation) | Bolt carries full load alone | $F_B = F_A$ (slope = $k_b$) | Extension of bolt line beyond S_bolt |
| Left panel: bolt/flange assembly | Physical bolted joint cross-section | N/A (schematic) | Panel A normalized coords |
| Left panel: force arrow | External load direction | $F_A$ direction | Panel A, pointing at joint |

#### 12.12.7 Verification Checklist for Plotted Figure

After plotting, verify these geometric properties hold:

```
CHECK 1: Load line slope
  Measured slope of load line ≈ -k_m
  Tolerance: < 1% error

CHECK 2: Triangle vertex alignment
  L_bolt must lie ON the bolt stiffness line
  L_memb must lie ON the member stiffness line
  P_bolt must lie ON the bolt stiffness line
  P_memb must lie ON the member stiffness line

CHECK 3: Arrow heights
  Green arrow height = F_bolt - F_V = Φ × F_A     ✓
  Blue arrow height  = F_V - F_clamp = (1-Φ) × F_A ✓
  Red arrow height   = F_bolt - F_clamp = F_A       ✓
  Green + Blue = Red                                 ✓

CHECK 4: Separation point
  S_bolt lies ON the bolt stiffness line             ✓
  At S_bolt, the corresponding member deflection = 0 ✓
  (i.e., the member is completely decompressed)

CHECK 5: Preload consistency
  F at P_bolt = F at P_memb = F_V                    ✓
  (both points are at the same force level)

CHECK 6: Force balance
  F_bolt = F_V + Φ × F_A                             ✓
  F_clamp = F_V - (1-Φ) × F_A                        ✓
  F_bolt + F_clamp = 2×F_V - (1-2Φ)×F_A              ✓

CHECK 7: Axis region labels
  "Bolt Extension" appears LEFT of origin              ✓
  "Joint Compression" appears RIGHT of origin          ✓
  "Force" label at TOP of y-axis                       ✓
  "Extension" label at RIGHT end of x-axis             ✓
```

---

## 13. Python Plotting Implementation

### 13.1 Data Structures and Computation Functions

```python
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from dataclasses import dataclass
from typing import Optional, Tuple
import math


@dataclass
class JointDiagramData:
    """All computed data needed to plot the joint diagram."""
    # Input parameters
    k_b: float          # Bolt stiffness [N/mm]
    k_m: float          # Member stiffness [N/mm]
    F_V: float          # Assembly preload [N]
    F_A: float          # External axial load [N]
    Phi: float          # Load factor [-]

    # Computed forces
    F_bolt: float       # Bolt force under load [N]
    F_clamp: float      # Clamping force under load [N]
    F_sep: float        # Separation force [N]

    # Computed deflections — preload state
    delta_b_preload: float   # Bolt extension at preload [mm]
    delta_m_preload: float   # Member compression at preload [mm]

    # Computed deflections — loaded state
    delta_b_loaded: float    # Bolt extension under load [mm]
    delta_m_loaded: float    # Member compression under load [mm]

    # Computed deflections — separation state
    delta_b_sep: float       # Bolt extension at separation [mm]

    # Force increments
    delta_F_bolt: float      # Bolt force increase = Φ × F_A [N]
    delta_F_clamp: float     # Clamp force decrease = (1-Φ) × F_A [N]


def compute_joint_diagram(
    k_b: float, k_m: float, F_V: float, F_A: float, n: float = 1.0
) -> JointDiagramData:
    """
    Compute all values needed for the bolted joint diagram.

    Parameters
    ----------
    k_b : float  — Bolt stiffness [N/mm]
    k_m : float  — Member (joint) stiffness [N/mm]
    F_V : float  — Assembly preload [N]
    F_A : float  — External axial tensile load [N]
    n   : float  — Load introduction factor (0 to 1), default 1.0

    Returns
    -------
    JointDiagramData with all computed diagram values
    """
    Phi = n * k_b / (k_b + k_m)
    F_bolt = F_V + Phi * F_A
    F_clamp = max(F_V - (1 - Phi) * F_A, 0.0)
    F_sep = F_V / (1 - Phi)

    return JointDiagramData(
        k_b=k_b, k_m=k_m, F_V=F_V, F_A=F_A, Phi=Phi,
        F_bolt=F_bolt, F_clamp=F_clamp, F_sep=F_sep,
        delta_b_preload=F_V / k_b, delta_m_preload=F_V / k_m,
        delta_b_loaded=F_bolt / k_b, delta_m_loaded=F_clamp / k_m,
        delta_b_sep=F_sep / k_b,
        delta_F_bolt=Phi * F_A, delta_F_clamp=(1 - Phi) * F_A,
    )


def compute_bolt_stiffness(
    A_d: float, A_t: float, E_b: float,
    l_d: float, l_t: float, d: Optional[float] = None
) -> float:
    """
    Bolt stiffness via VDI 2230 compliance method.

    Parameters
    ----------
    A_d : float — Shank area [mm²]
    A_t : float — Tensile stress area [mm²]
    E_b : float — Elastic modulus [MPa]
    l_d : float — Unthreaded grip length [mm]
    l_t : float — Threaded grip length [mm]
    d   : float — Nominal diameter [mm] (if given, adds head/nut compliance)

    Returns
    -------
    float — k_b [N/mm]
    """
    A_N = A_d
    delta = l_d / (E_b * A_d) + l_t / (E_b * A_t)
    if d is not None:
        delta += 0.5 * d / (E_b * A_N)    # Head
        delta += 0.5 * d / (E_b * A_t)    # Free thread in nut
        delta += 0.4 * d / (E_b * A_N)    # Nut
    return 1.0 / delta


def compute_member_stiffness_wileman(E_m: float, d: float, L: float) -> float:
    """Wileman empirical member stiffness (valid 0.5 ≤ d/L ≤ 2.0)."""
    return 0.78952 * E_m * d * math.exp(0.62914 * d / L)


def compute_member_stiffness_shigley(
    E_m: float, d: float, d_w: float, L: float, alpha_deg: float = 30.0
) -> float:
    """Shigley frustum cone member stiffness."""
    alpha = math.radians(alpha_deg)
    tan_a = math.tan(alpha)
    num = math.pi * E_m * d * tan_a
    arg = ((L * tan_a + d_w - d) * (d_w + d)) / \
          ((L * tan_a + d_w + d) * (d_w - d))
    return num / math.log(arg)
```

### 13.2 Main Plot Function (Matches VDI 2230 Figure)

```python
def plot_joint_diagram(
    data: JointDiagramData,
    title: str = "Bolted Joint Diagram (VDI 2230)",
    figsize: Tuple[float, float] = (14, 9),
    force_unit: str = "N",
    force_scale: float = 1.0,
    length_unit: str = "mm",
    show_triangle_fill: bool = True,
    show_separation: bool = True,
    show_post_separation: bool = True,
    show_annotations: bool = True,
    show_grid: bool = True,
    color_bolt_line: str = '#8B4513',
    color_member_line: str = '#006400',
    color_load_line: str = '#008080',
    color_bolt_increase: str = '#228B22',
    color_clamp_decrease: str = '#4169E1',
    color_applied_force: str = '#DC143C',
    color_triangle_upper: str = '#90EE90',
    color_triangle_lower: str = '#ADD8E6',
    save_path: Optional[str] = None,
    dpi: int = 150
) -> Tuple[plt.Figure, plt.Axes]:
    """
    Plot the complete bolted joint diagram matching VDI 2230 figure style.

    Parameters
    ----------
    data : JointDiagramData
        Computed diagram data from compute_joint_diagram()
    title : str
        Plot title
    figsize : tuple
        Figure size in inches
    force_unit / force_scale / length_unit : str / float / str
        Units and scaling for display
    show_* : bool
        Toggle visibility of diagram elements
    color_* : str
        Color specifications for each element
    save_path : str, optional
        Path to save figure
    dpi : int
        Resolution for saved figure

    Returns
    -------
    (fig, ax) : tuple of matplotlib Figure and Axes
    """
    k_b = data.k_b
    k_m = data.k_m
    F_V = data.F_V
    F_A = data.F_A
    Phi = data.Phi
    F_bolt = data.F_bolt
    F_clamp = data.F_clamp
    F_sep = data.F_sep
    fs = force_scale

    # ──────────────────────────────────────────────
    # COORDINATE COMPUTATION
    # ──────────────────────────────────────────────

    x_bolt_max = 1.2 * F_sep / k_b
    x_memb_max = 1.4 * F_V / k_m
    y_max = 1.25 * F_sep

    # Element 1: Bolt stiffness line
    bolt_line_x = np.array([0, -x_bolt_max])
    bolt_line_y = np.array([0, k_b * x_bolt_max])

    # Element 2: Member stiffness line
    memb_line_x = np.array([0, x_memb_max])
    memb_line_y = np.array([0, k_m * x_memb_max])

    # Element 3: Load application line (with slight extension)
    load_line_x = np.array([-F_bolt / k_b, F_clamp / k_m])
    load_line_y = np.array([F_bolt, F_clamp])
    load_ext = 0.08 * (load_line_x[1] - load_line_x[0])
    load_line_ext_x = np.array([
        load_line_x[0] - load_ext,
        load_line_x[1] + load_ext
    ])
    load_line_ext_y = np.array([
        F_bolt + k_m * load_ext,
        F_clamp - k_m * load_ext
    ])

    # Key points
    P_bolt = (-F_V / k_b, F_V)
    P_memb = (F_V / k_m, F_V)
    L_bolt = (-F_bolt / k_b, F_bolt)
    L_memb = (F_clamp / k_m, F_clamp)
    S_bolt = (-F_sep / k_b, F_sep)

    # Load line ∩ preload horizontal
    x_int_FV = -F_bolt / k_b + (F_bolt - F_V) / k_m

    # ──────────────────────────────────────────────
    # PLOTTING
    # ──────────────────────────────────────────────

    fig, ax = plt.subplots(1, 1, figsize=figsize)

    # Load triangle fill
    if show_triangle_fill:
        # Upper triangle: P_bolt → L_bolt → (x_int, F_V) → close
        ax.fill(
            [P_bolt[0], L_bolt[0], x_int_FV, P_bolt[0]],
            [P_bolt[1]/fs, L_bolt[1]/fs, F_V/fs, P_bolt[1]/fs],
            color=color_triangle_upper, alpha=0.35,
            label='Bolt force increase region'
        )
        # Lower triangle: P_memb → L_memb → (x_int, F_V) → close
        ax.fill(
            [P_memb[0], L_memb[0], x_int_FV, P_memb[0]],
            [P_memb[1]/fs, L_memb[1]/fs, F_V/fs, P_memb[1]/fs],
            color=color_triangle_lower, alpha=0.35,
            label='Clamp force decrease region'
        )

    # Stiffness lines
    ax.plot(bolt_line_x, bolt_line_y / fs,
            color=color_bolt_line, linewidth=2.5, solid_capstyle='round',
            label=f'Bolt line ($k_b$ = {k_b:,.0f} N/mm)')
    ax.plot(memb_line_x, memb_line_y / fs,
            color=color_member_line, linewidth=2.5, solid_capstyle='round',
            label=f'Member line ($k_m$ = {k_m:,.0f} N/mm)')

    # Load application line
    ax.plot(load_line_ext_x, load_line_ext_y / fs,
            color=color_load_line, linewidth=2.0, linestyle='-',
            label='Load line (slope = $-k_m$)')

    # Preload horizontal dashed
    ax.plot([P_bolt[0], P_memb[0]], [F_V/fs, F_V/fs],
            color='black', linewidth=1.0, linestyle='--', alpha=0.6)

    # Force level horizontals (dotted guides)
    ax.plot([-F_bolt/k_b, x_memb_max*0.85], [F_bolt/fs, F_bolt/fs],
            color='gray', linewidth=0.7, linestyle=':', alpha=0.5)
    ax.plot([-x_bolt_max*0.3, F_clamp/k_m], [F_clamp/fs, F_clamp/fs],
            color='gray', linewidth=0.7, linestyle=':', alpha=0.5)

    # Key point markers
    ps = 60
    ax.scatter(P_bolt[0], P_bolt[1]/fs, s=ps, color=color_bolt_line,
               zorder=5, edgecolors='black', linewidths=0.5)
    ax.scatter(P_memb[0], P_memb[1]/fs, s=ps, color=color_member_line,
               zorder=5, edgecolors='black', linewidths=0.5)
    ax.scatter(L_bolt[0], L_bolt[1]/fs, s=ps, color=color_bolt_increase,
               zorder=5, edgecolors='black', linewidths=0.5)
    ax.scatter(L_memb[0], L_memb[1]/fs, s=ps, color=color_clamp_decrease,
               zorder=5, edgecolors='black', linewidths=0.5)

    # Separation point
    if show_separation:
        ax.scatter(S_bolt[0], S_bolt[1]/fs, s=80, color=color_applied_force,
                   marker='x', zorder=5, linewidths=2)
        ax.annotate(
            f'Separation\n$F_{{A,sep}}$ = {F_sep/fs:.0f} {force_unit}',
            xy=(S_bolt[0], S_bolt[1]/fs),
            xytext=(S_bolt[0] - 0.15*x_bolt_max,
                    S_bolt[1]/fs + 0.05*y_max/fs),
            fontsize=8, color=color_applied_force,
            arrowprops=dict(arrowstyle='->', color=color_applied_force, lw=1),
            ha='center'
        )

    # Post-separation bolt line (dashed extension)
    if show_post_separation:
        ext = 0.15 * x_bolt_max
        ax.plot([S_bolt[0], S_bolt[0] - ext],
                [F_sep/fs, (F_sep + k_b*ext)/fs],
                color=color_applied_force, linewidth=1.5, linestyle='--',
                alpha=0.7, label='Post-separation (bolt only)')

    # ──────────────────────────────────────────────
    # ANNOTATION ARROWS (right side of diagram)
    # ──────────────────────────────────────────────

    if show_annotations:
        x_a = P_memb[0] + 0.18 * x_memb_max
        x_b = P_memb[0] + 0.35 * x_memb_max

        # Arrow A: Bolt Force Increase (green ↕)
        ax.annotate('', xy=(x_a, F_bolt/fs), xytext=(x_a, F_V/fs),
                    arrowprops=dict(arrowstyle='<->', color=color_bolt_increase,
                                    lw=2.0, mutation_scale=15))
        ax.text(x_a + 0.02*x_memb_max, (F_V + data.delta_F_bolt/2)/fs,
                f'Bolt force\nincrease\n$\\Phi F_A$ = {data.delta_F_bolt/fs:.0f} {force_unit}',
                fontsize=8, color=color_bolt_increase, ha='left', va='center',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='white',
                          edgecolor=color_bolt_increase, alpha=0.8))

        # Arrow B: Clamp Force Decrease (blue ↕)
        ax.annotate('', xy=(x_a, F_clamp/fs), xytext=(x_a, F_V/fs),
                    arrowprops=dict(arrowstyle='<->', color=color_clamp_decrease,
                                    lw=2.0, mutation_scale=15))
        ax.text(x_a + 0.02*x_memb_max, (F_V - data.delta_F_clamp/2)/fs,
                f'Joint clamp\nforce decrease\n$(1-\\Phi)F_A$ = {data.delta_F_clamp/fs:.0f} {force_unit}',
                fontsize=8, color=color_clamp_decrease, ha='left', va='center',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='white',
                          edgecolor=color_clamp_decrease, alpha=0.8))

        # Arrow C: Total Applied Force (red ↕)
        ax.annotate('', xy=(x_b, F_bolt/fs), xytext=(x_b, F_clamp/fs),
                    arrowprops=dict(arrowstyle='<->', color=color_applied_force,
                                    lw=2.5, mutation_scale=18))
        ax.text(x_b + 0.02*x_memb_max, (F_clamp + F_A/2)/fs,
                f'Applied force\nto the joint\n$F_A$ = {F_A/fs:.0f} {force_unit}',
                fontsize=9, fontweight='bold', color=color_applied_force,
                ha='left', va='center',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='white',
                          edgecolor=color_applied_force, alpha=0.9))

    # ──────────────────────────────────────────────
    # AXIS FORMATTING
    # ──────────────────────────────────────────────

    y_ticks = [0, F_clamp/fs, F_V/fs, F_bolt/fs]
    y_labels = ['0',
                f'$F_{{clamp}}$ = {F_clamp/fs:.0f}',
                f'$F_V$ = {F_V/fs:.0f}',
                f'$F_B$ = {F_bolt/fs:.0f}']
    if show_separation:
        y_ticks.append(F_sep / fs)
        y_labels.append(f'$F_{{sep}}$ = {F_sep/fs:.0f}')

    ax.set_yticks(y_ticks)
    ax.set_yticklabels(y_labels, fontsize=8)

    ax.set_xlim(-x_bolt_max * 1.05, x_memb_max * 1.9)
    ax.set_ylim(-0.03 * y_max / fs, y_max / fs)

    ax.set_xlabel(f'Extension [{length_unit}]', fontsize=11, fontweight='bold')
    ax.set_ylabel(f'Force [{force_unit}]', fontsize=11, fontweight='bold')
    ax.set_title(title, fontsize=13, fontweight='bold', pad=15)

    # Region labels
    ax.text(-x_bolt_max*0.5, -0.015*y_max/fs,
            '← Bolt Extension', fontsize=9, ha='center', va='top',
            color=color_bolt_line, fontweight='bold')
    ax.text(x_memb_max*0.5, -0.015*y_max/fs,
            'Joint Compression →', fontsize=9, ha='center', va='top',
            color=color_member_line, fontweight='bold')

    ax.axvline(x=0, color='black', linewidth=0.8, alpha=0.3)
    ax.axhline(y=0, color='black', linewidth=0.8, alpha=0.3)

    if show_grid:
        ax.grid(True, alpha=0.15, linestyle='-')

    ax.legend(loc='upper left', fontsize=8, framealpha=0.9)
    plt.tight_layout()

    if save_path:
        fig.savefig(save_path, dpi=dpi, bbox_inches='tight',
                    facecolor='white', edgecolor='none')
        print(f"Diagram saved to: {save_path}")

    return fig, ax
```

### 13.3 Hard vs. Soft Joint Comparison Plot

```python
def plot_hard_vs_soft_comparison(
    k_b_hard: float, k_m_hard: float,
    k_b_soft: float, k_m_soft: float,
    F_V: float, F_A: float,
    figsize: Tuple[float, float] = (16, 7),
    force_scale: float = 1.0,
    force_unit: str = "N",
    save_path: Optional[str] = None,
    dpi: int = 150
) -> Tuple[plt.Figure, Tuple[plt.Axes, plt.Axes]]:
    """
    Plot side-by-side Hard Joint vs Soft Joint comparison.

    Parameters
    ----------
    k_b_hard, k_m_hard : float — Hard joint stiffnesses [N/mm]
    k_b_soft, k_m_soft : float — Soft joint stiffnesses [N/mm]
    F_V : float — Assembly preload [N]
    F_A : float — External load [N]
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize)
    data_hard = compute_joint_diagram(k_b_hard, k_m_hard, F_V, F_A)
    data_soft = compute_joint_diagram(k_b_soft, k_m_soft, F_V, F_A)

    def _plot_on_axis(ax, data, subtitle):
        k_b, k_m, Phi = data.k_b, data.k_m, data.Phi
        F_bolt, F_clamp, F_sep = data.F_bolt, data.F_clamp, data.F_sep
        fs = force_scale

        x_bm = 1.2 * F_sep / k_b
        x_mm = 1.4 * F_V / k_m
        y_max = 1.2 * F_sep

        # Stiffness lines
        ax.plot([0, -x_bm], [0, k_b*x_bm/fs],
                color='#8B4513', lw=2.5, label=f'Bolt ($k_b$={k_b:,.0f})')
        ax.plot([0, x_mm], [0, k_m*x_mm/fs],
                color='#006400', lw=2.5, label=f'Member ($k_m$={k_m:,.0f})')

        # Load line
        ax.plot([-F_bolt/k_b, F_clamp/k_m], [F_bolt/fs, F_clamp/fs],
                color='#008080', lw=2.0)

        # Preload horizontal
        ax.plot([-F_V/k_b, F_V/k_m], [F_V/fs, F_V/fs],
                color='black', lw=1.0, ls='--', alpha=0.6)

        # Triangle fill
        x_int = -F_bolt/k_b + (F_bolt - F_V)/k_m
        ax.fill([-F_V/k_b, -F_bolt/k_b, x_int],
                [F_V/fs, F_bolt/fs, F_V/fs], color='#90EE90', alpha=0.35)
        ax.fill([F_V/k_m, F_clamp/k_m, x_int],
                [F_V/fs, F_clamp/fs, F_V/fs], color='#ADD8E6', alpha=0.35)

        # Annotation arrows
        x_a = F_clamp/k_m + 0.2*x_mm
        x_b = x_a + 0.15*x_mm

        ax.annotate('', xy=(x_a, F_bolt/fs), xytext=(x_a, F_V/fs),
                    arrowprops=dict(arrowstyle='<->', color='#228B22', lw=2))
        ax.annotate('', xy=(x_a, F_clamp/fs), xytext=(x_a, F_V/fs),
                    arrowprops=dict(arrowstyle='<->', color='#4169E1', lw=2))
        ax.annotate('', xy=(x_b, F_bolt/fs), xytext=(x_b, F_clamp/fs),
                    arrowprops=dict(arrowstyle='<->', color='#DC143C', lw=2.5))
        ax.text(x_b + 0.02*x_mm, (F_clamp + F_A/2)/fs, '$F_A$',
                fontsize=10, fontweight='bold', color='#DC143C',
                ha='left', va='center', rotation=90)

        ax.set_xlabel(f'Extension', fontsize=10)
        ax.set_ylabel(f'Force [{force_unit}]', fontsize=10)
        ax.set_title(f"{subtitle}\n$\\Phi$ = {Phi:.3f}, $k_m/k_b$ = {k_m/k_b:.2f}",
                     fontsize=11, fontweight='bold')

        ax.text(-x_bm*0.4, -0.02*y_max/fs, '← Bolt Extension',
                fontsize=8, ha='center', color='#8B4513', fontweight='bold')
        ax.text(x_mm*0.4, -0.02*y_max/fs, 'Joint Compression →',
                fontsize=8, ha='center', color='#006400', fontweight='bold')

        ax.axvline(x=0, color='black', lw=0.5, alpha=0.3)
        ax.axhline(y=0, color='black', lw=0.5, alpha=0.3)
        ax.grid(True, alpha=0.15)
        ax.legend(fontsize=8, loc='upper left')

    _plot_on_axis(ax1, data_hard,
                  "'Hard' Joint\nHigh stiffness joint, low stiffness bolt")
    _plot_on_axis(ax2, data_soft,
                  "'Soft' Joint\nLow stiffness joint, high stiffness bolt")

    plt.tight_layout()
    if save_path:
        fig.savefig(save_path, dpi=dpi, bbox_inches='tight', facecolor='white')
    return fig, (ax1, ax2)
```

### 13.4 Full Pipeline: Geometry → Diagram → Plot

```python
def joint_diagram_from_geometry(
    d: float, A_t: float, A_d: float,
    E_b: float, E_m: float,
    l_d: float, l_t: float, L: float, d_w: float,
    F_V: float, F_A: float,
    n: float = 1.0,
    stiffness_method: str = "shigley",
    title: str = "Bolted Joint Diagram",
    **plot_kwargs
):
    """
    Complete pipeline: bolt geometry → stiffness → diagram → plot.

    Parameters
    ----------
    d, A_t, A_d : float — Bolt geometry [mm, mm², mm²]
    E_b, E_m    : float — Elastic moduli [MPa]
    l_d, l_t, L : float — Grip lengths [mm]
    d_w         : float — Bearing diameter [mm]
    F_V, F_A    : float — Preload and external load [N]
    n           : float — Load introduction factor
    stiffness_method : str — "shigley" or "wileman"
    **plot_kwargs passed to plot_joint_diagram()

    Returns
    -------
    (data, fig, ax) : tuple
    """
    k_b = compute_bolt_stiffness(A_d, A_t, E_b, l_d, l_t, d)

    if stiffness_method == "shigley":
        k_m = compute_member_stiffness_shigley(E_m, d, d_w, L)
    else:
        k_m = compute_member_stiffness_wileman(E_m, d, L)

    data = compute_joint_diagram(k_b, k_m, F_V, F_A, n)
    fig, ax = plot_joint_diagram(data, title=title, **plot_kwargs)

    print(f"\n{'='*55}")
    print(f"  BOLTED JOINT DIAGRAM SUMMARY")
    print(f"{'='*55}")
    print(f"  Bolt:  d = {d} mm, A_t = {A_t} mm²")
    print(f"  Grip:  L = {L} mm (l_d={l_d}, l_t={l_t})")
    print(f"  k_b  = {k_b:>12,.0f} N/mm")
    print(f"  k_m  = {k_m:>12,.0f} N/mm")
    print(f"  k_m/k_b = {k_m/k_b:.2f}")
    print(f"  Φ    = {data.Phi:.4f}")
    print(f"  n    = {n}")
    print(f"{'─'*55}")
    print(f"  F_V      = {F_V:>10,.0f} N  (preload)")
    print(f"  F_A      = {F_A:>10,.0f} N  (external)")
    print(f"  F_bolt   = {data.F_bolt:>10,.0f} N  (bolt under load)")
    print(f"  F_clamp  = {data.F_clamp:>10,.0f} N  (residual clamp)")
    print(f"  F_sep    = {data.F_sep:>10,.0f} N  (separation)")
    print(f"  ΔF_bolt  = {data.delta_F_bolt:>10,.0f} N  (bolt increase)")
    print(f"  ΔF_clamp = {data.delta_F_clamp:>10,.0f} N  (clamp decrease)")
    print(f"{'='*55}")

    return data, fig, ax
```

### 13.5 Extended Diagram with Losses, Scatter, and Yield

```python
def plot_extended_joint_diagram(
    data: JointDiagramData,
    F_Z: float = 0.0,
    alpha_A: float = 1.0,
    F_Kerf: float = 0.0,
    R_p02: float = 0.0,
    A_t: float = 0.0,
    **kwargs
):
    """
    Extended diagram with preload losses, scatter, and yield limit.

    Parameters
    ----------
    F_Z     : float — Embedding/relaxation loss [N]
    alpha_A : float — Tightening factor
    F_Kerf  : float — Minimum required clamping force [N]
    R_p02   : float — Bolt proof stress [MPa]
    A_t     : float — Tensile stress area [mm²]
    """
    fig, ax = plot_joint_diagram(data, **kwargs)
    fs = kwargs.get('force_scale', 1.0)
    fu = kwargs.get('force_unit', 'N')
    x_lim = ax.get_xlim()

    if F_Z > 0:
        F_eff = data.F_V - F_Z
        ax.axhline(y=F_eff/fs, color='orange', lw=1.2, ls='-.', alpha=0.7)
        ax.text(x_lim[1]*0.7, F_eff/fs,
                f'$F_{{V,eff}}$ = {F_eff/fs:.0f} {fu}\n(after embedding)',
                fontsize=7, color='orange', va='bottom')

    if alpha_A > 1.0:
        F_max = alpha_A * data.F_V
        ax.axhspan(data.F_V/fs, F_max/fs, alpha=0.08, color='purple',
                   label=f'Scatter (α_A={alpha_A})')
        ax.axhline(y=F_max/fs, color='purple', lw=1, ls=':', alpha=0.6)
        ax.text(x_lim[0]*0.8, F_max/fs,
                f'$F_{{M,max}}$ = {F_max/fs:.0f} {fu}',
                fontsize=7, color='purple', va='bottom')

    if F_Kerf > 0:
        ax.axhline(y=F_Kerf/fs, color='red', lw=1.5, ls='--', alpha=0.8)
        ax.text(x_lim[1]*0.7, F_Kerf/fs,
                f'$F_{{Kerf}}$ = {F_Kerf/fs:.0f} {fu}\n(min. clamp)',
                fontsize=7, color='red', va='top')

    if R_p02 > 0 and A_t > 0:
        F_y = R_p02 * A_t
        ax.axhline(y=F_y/fs, color='darkred', lw=2.0, alpha=0.5)
        ax.text(x_lim[0]*0.5, F_y/fs,
                f'$F_{{yield}}$ = {F_y/fs:.0f} {fu}',
                fontsize=8, color='darkred', fontweight='bold', va='bottom')

    ax.legend(loc='upper left', fontsize=7, framealpha=0.9)
    return fig, ax
```

### 13.6 Usage Examples

```python
if __name__ == "__main__":

    # ── EXAMPLE 1: Single joint from geometry ──
    data, fig, ax = joint_diagram_from_geometry(
        d=12, A_t=84.3, A_d=113.1,
        E_b=210_000, E_m=210_000,
        l_d=15, l_t=10, L=25, d_w=18,
        F_V=50_000, F_A=15_000,
        title="M12 × 1.75 — PC 10.9",
        save_path="joint_diagram.png"
    )
    plt.show()

    # ── EXAMPLE 2: Hard vs soft comparison ──
    fig2, axes = plot_hard_vs_soft_comparison(
        k_b_hard=300_000, k_m_hard=2_500_000,
        k_b_soft=1_200_000, k_m_soft=400_000,
        F_V=40_000, F_A=12_000,
        save_path="hard_vs_soft.png"
    )
    plt.show()

    # ── EXAMPLE 3: Extended diagram with losses ──
    data3 = compute_joint_diagram(835_400, 2_690_900, 50_000, 15_000)
    fig3, ax3 = plot_extended_joint_diagram(
        data3, F_Z=3_000, alpha_A=1.4,
        F_Kerf=10_000, R_p02=940, A_t=84.3,
        title="Extended Joint Diagram with Losses",
        save_path="extended_diagram.png"
    )
    plt.show()

    # ── EXAMPLE 4: kN display ──
    fig4, ax4 = plot_joint_diagram(
        data3, title="Joint Diagram (kN)",
        force_unit="kN", force_scale=1000.0,
        save_path="diagram_kN.png"
    )
    plt.show()

    # ── EXAMPLE 5: API 6A flange ──
    data5, fig5, ax5 = joint_diagram_from_geometry(
        d=25.4, A_t=353.0, A_d=506.7,
        E_b=205_000, E_m=210_000,
        l_d=30, l_t=45, L=75, d_w=38.1,
        F_V=150_000, F_A=50_000,
        title='API 6A — 1" A320 L7M on 6BX Flange',
        force_unit="kN", force_scale=1000.0,
        save_path="api6a_diagram.png"
    )
    plt.show()

    # ── EXAMPLE 6: Quick one-liner ──
    # quick_joint_diagram(835400, 2690900, 50000, 15000)
```

### 13.7 Composite Figure with Physical Schematic (Reference Figure Layout)

This function produces the **complete two-panel composite figure** matching the VDI 2230 reference illustration: physical joint schematic on the left, force-extension diagram on the right.

```python
def draw_bolt_schematic(ax):
    """
    Draw the physical bolted joint cross-section schematic.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        Axes with xlim/ylim set to [0,1]×[0,1], axis_off.
        Coordinate system: (0,0)=bottom-left, (1,1)=top-left.
    """
    from matplotlib.patches import FancyArrowPatch, FancyArrow, Rectangle

    # ── Force arrow (pointing right toward bolt head) ──
    ax.annotate(
        '', xy=(0.38, 0.82), xytext=(0.05, 0.82),
        arrowprops=dict(arrowstyle='->', color='black', lw=3,
                        mutation_scale=20)
    )
    ax.text(0.04, 0.92, "Force applied\nto the joint",
            fontsize=8, fontstyle='italic', fontweight='bold',
            va='bottom', ha='left', color='black')

    # ── Bolt head (top) ──
    bolt_head = Rectangle((0.35, 0.76), 0.20, 0.07,
                           facecolor='#006400', edgecolor='black', lw=1.5, zorder=4)
    ax.add_patch(bolt_head)

    # ── Upper flange ──
    upper_flange = Rectangle((0.20, 0.48), 0.50, 0.28,
                              facecolor='#2E8B57', edgecolor='black', lw=1.5, zorder=3)
    ax.add_patch(upper_flange)

    # ── Lower flange ──
    lower_flange = Rectangle((0.20, 0.20), 0.50, 0.28,
                              facecolor='#2E8B57', edgecolor='black', lw=1.5, zorder=3)
    ax.add_patch(lower_flange)

    # ── Bolt shank (through both flanges) ──
    shank = Rectangle((0.42, 0.13), 0.06, 0.63,
                       facecolor='#228B22', edgecolor='black', lw=1.0, zorder=5)
    ax.add_patch(shank)

    # ── Nut (bottom) ──
    nut = Rectangle((0.35, 0.10), 0.20, 0.07,
                     facecolor='#006400', edgecolor='black', lw=1.5, zorder=4)
    ax.add_patch(nut)

    # ── Clamping interface (dashed line between flanges) ──
    ax.plot([0.20, 0.70], [0.48, 0.48],
            color='gray', linewidth=1.0, linestyle='--', zorder=6)

    # ── Rötscher compression cones (faint dashed) ──
    cone_style = dict(color='#8B4513', linewidth=0.8,
                      linestyle=':', alpha=0.5, zorder=2)
    # Upper cone
    ax.plot([0.39, 0.24], [0.76, 0.48], **cone_style)
    ax.plot([0.51, 0.66], [0.76, 0.48], **cone_style)
    # Lower cone
    ax.plot([0.39, 0.24], [0.20, 0.48], **cone_style)
    ax.plot([0.51, 0.66], [0.20, 0.48], **cone_style)

    # ── Thread indication (small horizontal lines on shank) ──
    for y_t in np.linspace(0.22, 0.38, 6):
        ax.plot([0.41, 0.49], [y_t, y_t],
                color='#004400', linewidth=0.4, alpha=0.6, zorder=6)

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_aspect('equal')
    ax.axis('off')


def plot_composite_joint_figure(
    data: JointDiagramData,
    title: str = "Bolted Joint Diagram (VDI 2230)",
    figsize: Tuple[float, float] = (16, 8),
    force_unit: str = "N",
    force_scale: float = 1.0,
    length_unit: str = "mm",
    show_triangle_fill: bool = True,
    show_separation: bool = True,
    show_post_separation: bool = True,
    show_annotations: bool = True,
    show_grid: bool = True,
    show_schematic: bool = True,
    schematic_width_ratio: float = 0.25,
    color_bolt_line: str = '#8B4513',
    color_member_line: str = '#006400',
    color_load_line: str = '#008080',
    color_bolt_increase: str = '#228B22',
    color_clamp_decrease: str = '#4169E1',
    color_applied_force: str = '#DC143C',
    color_triangle_upper: str = '#90EE90',
    color_triangle_lower: str = '#ADD8E6',
    save_path: Optional[str] = None,
    dpi: int = 150
) -> Tuple[plt.Figure, Tuple]:
    """
    Plot the COMPLETE composite joint figure matching the VDI 2230
    reference illustration: physical schematic (left) + diagram (right).

    Parameters
    ----------
    data : JointDiagramData
        Computed diagram data from compute_joint_diagram()
    title : str
        Overall figure title
    figsize : tuple
        Total figure size (width, height) in inches
    force_unit / force_scale / length_unit : str / float / str
        Display units and scaling
    show_schematic : bool
        Include the physical joint schematic (Panel A)
    schematic_width_ratio : float
        Fraction of total width for schematic panel (0.20–0.30)
    color_* : str
        Color specifications for each element
    save_path : str, optional
        Path to save the figure
    dpi : int
        Resolution for saved figure

    Returns
    -------
    (fig, (ax_schematic, ax_diagram)) : tuple
    """
    # ──────────────────────────────────────────────
    # FIGURE LAYOUT
    # ──────────────────────────────────────────────

    if show_schematic:
        width_ratios = [schematic_width_ratio, 1.0 - schematic_width_ratio]
        fig, (ax_sch, ax_dia) = plt.subplots(
            1, 2, figsize=figsize,
            gridspec_kw={'width_ratios': width_ratios, 'wspace': 0.05}
        )
    else:
        fig, ax_dia = plt.subplots(1, 1, figsize=figsize)
        ax_sch = None

    # ──────────────────────────────────────────────
    # PANEL A: PHYSICAL SCHEMATIC
    # ──────────────────────────────────────────────

    if show_schematic and ax_sch is not None:
        draw_bolt_schematic(ax_sch)

    # ──────────────────────────────────────────────
    # PANEL B: FORCE-EXTENSION DIAGRAM
    # (complete implementation inline for self-containment)
    # ──────────────────────────────────────────────

    k_b = data.k_b
    k_m = data.k_m
    F_V = data.F_V
    F_A = data.F_A
    Phi = data.Phi
    F_bolt = data.F_bolt
    F_clamp = data.F_clamp
    F_sep = data.F_sep
    fs = force_scale

    # --- Axis extents ---
    x_bolt_max = 1.2 * F_sep / k_b
    x_memb_max = 1.4 * F_V / k_m
    y_max = 1.25 * F_sep

    # --- Key points ---
    P_bolt = (-F_V / k_b, F_V)
    P_memb = (F_V / k_m, F_V)
    L_bolt = (-F_bolt / k_b, F_bolt)
    L_memb = (F_clamp / k_m, F_clamp)
    S_bolt = (-F_sep / k_b, F_sep)

    # Load line ∩ preload horizontal
    x_int_FV = -F_bolt / k_b + (F_bolt - F_V) / k_m

    # --- LAYER 0: Grid ---
    if show_grid:
        ax_dia.grid(True, alpha=0.15, linestyle='-')

    # --- LAYER 1: Load triangle fill ---
    if show_triangle_fill:
        ax_dia.fill(
            [P_bolt[0], L_bolt[0], x_int_FV, P_bolt[0]],
            [P_bolt[1]/fs, L_bolt[1]/fs, F_V/fs, P_bolt[1]/fs],
            color=color_triangle_upper, alpha=0.35,
            label='Bolt force increase region'
        )
        ax_dia.fill(
            [P_memb[0], L_memb[0], x_int_FV, P_memb[0]],
            [P_memb[1]/fs, L_memb[1]/fs, F_V/fs, P_memb[1]/fs],
            color=color_triangle_lower, alpha=0.35,
            label='Clamp force decrease region'
        )

    # --- LAYER 2: Horizontal guide lines ---
    ax_dia.plot([P_bolt[0], P_memb[0]], [F_V/fs, F_V/fs],
                color='black', linewidth=1.0, linestyle='--', alpha=0.6)
    ax_dia.plot([-F_bolt/k_b, x_memb_max*0.85], [F_bolt/fs, F_bolt/fs],
                color='gray', linewidth=0.7, linestyle=':', alpha=0.5)
    ax_dia.plot([-x_bolt_max*0.3, F_clamp/k_m], [F_clamp/fs, F_clamp/fs],
                color='gray', linewidth=0.7, linestyle=':', alpha=0.5)

    # --- LAYER 3: Stiffness lines ---
    ax_dia.plot([0, -x_bolt_max], [0, k_b*x_bolt_max/fs],
                color=color_bolt_line, linewidth=2.5, solid_capstyle='round',
                label=f'Bolt line ($k_b$ = {k_b:,.0f} N/mm)')
    ax_dia.plot([0, x_memb_max], [0, k_m*x_memb_max/fs],
                color=color_member_line, linewidth=2.5, solid_capstyle='round',
                label=f'Member line ($k_m$ = {k_m:,.0f} N/mm)')

    # --- LAYER 4: Load application line (with slight extension) ---
    dx_load = 0.08 * (F_clamp/k_m - (-F_bolt/k_b))
    ax_dia.plot(
        [-F_bolt/k_b - dx_load, F_clamp/k_m + dx_load],
        [(F_bolt + k_m*dx_load)/fs, (F_clamp - k_m*dx_load)/fs],
        color=color_load_line, linewidth=2.0, linestyle='-',
        label='Load line (slope = $-k_m$)'
    )

    # --- LAYER 5: Post-separation line ---
    if show_post_separation:
        ext = 0.15 * x_bolt_max
        ax_dia.plot([S_bolt[0], S_bolt[0] - ext],
                    [F_sep/fs, (F_sep + k_b*ext)/fs],
                    color=color_applied_force, linewidth=1.5, linestyle='--',
                    alpha=0.7, label='Post-separation (bolt only)')

    # --- LAYER 6: Key point markers ---
    ps = 60
    ax_dia.scatter(P_bolt[0], P_bolt[1]/fs, s=ps, color=color_bolt_line,
                   zorder=5, edgecolors='black', linewidths=0.5)
    ax_dia.scatter(P_memb[0], P_memb[1]/fs, s=ps, color=color_member_line,
                   zorder=5, edgecolors='black', linewidths=0.5)
    ax_dia.scatter(L_bolt[0], L_bolt[1]/fs, s=ps, color=color_bolt_increase,
                   zorder=5, edgecolors='black', linewidths=0.5)
    ax_dia.scatter(L_memb[0], L_memb[1]/fs, s=ps, color=color_clamp_decrease,
                   zorder=5, edgecolors='black', linewidths=0.5)

    if show_separation:
        ax_dia.scatter(S_bolt[0], S_bolt[1]/fs, s=80, color=color_applied_force,
                       marker='x', zorder=5, linewidths=2)
        ax_dia.annotate(
            f'Separation\n$F_{{A,sep}}$ = {F_sep/fs:.0f} {force_unit}',
            xy=(S_bolt[0], S_bolt[1]/fs),
            xytext=(S_bolt[0] - 0.15*x_bolt_max,
                    S_bolt[1]/fs + 0.05*y_max/fs),
            fontsize=8, color=color_applied_force,
            arrowprops=dict(arrowstyle='->', color=color_applied_force, lw=1),
            ha='center'
        )

    # --- LAYER 7: Annotation arrows (right side) ---
    if show_annotations:
        x_a = P_memb[0] + 0.18 * x_memb_max
        x_b = P_memb[0] + 0.35 * x_memb_max

        # Arrow A: Bolt Force Increase (green)
        ax_dia.annotate('', xy=(x_a, F_bolt/fs), xytext=(x_a, F_V/fs),
                        arrowprops=dict(arrowstyle='<->', color=color_bolt_increase,
                                        lw=2.0, mutation_scale=15))
        ax_dia.text(x_a + 0.02*x_memb_max, (F_V + data.delta_F_bolt/2)/fs,
                    f'Bolt force\nincrease\n$\\Phi F_A$ = {data.delta_F_bolt/fs:.0f} {force_unit}',
                    fontsize=8, color=color_bolt_increase, ha='left', va='center',
                    bbox=dict(boxstyle='round,pad=0.3', facecolor='white',
                              edgecolor=color_bolt_increase, alpha=0.8))

        # Arrow B: Clamp Force Decrease (blue)
        ax_dia.annotate('', xy=(x_a, F_clamp/fs), xytext=(x_a, F_V/fs),
                        arrowprops=dict(arrowstyle='<->', color=color_clamp_decrease,
                                        lw=2.0, mutation_scale=15))
        ax_dia.text(x_a + 0.02*x_memb_max, (F_V - data.delta_F_clamp/2)/fs,
                    f'Joint clamp\nforce decrease\n$(1-\\Phi)F_A$ = {data.delta_F_clamp/fs:.0f} {force_unit}',
                    fontsize=8, color=color_clamp_decrease, ha='left', va='center',
                    bbox=dict(boxstyle='round,pad=0.3', facecolor='white',
                              edgecolor=color_clamp_decrease, alpha=0.8))

        # Arrow C: Applied Force (red)
        ax_dia.annotate('', xy=(x_b, F_bolt/fs), xytext=(x_b, F_clamp/fs),
                        arrowprops=dict(arrowstyle='<->', color=color_applied_force,
                                        lw=2.5, mutation_scale=18))
        ax_dia.text(x_b + 0.02*x_memb_max, (F_clamp + F_A/2)/fs,
                    f'Applied force\nto the joint\n$F_A$ = {F_A/fs:.0f} {force_unit}',
                    fontsize=9, fontweight='bold', color=color_applied_force,
                    ha='left', va='center',
                    bbox=dict(boxstyle='round,pad=0.3', facecolor='white',
                              edgecolor=color_applied_force, alpha=0.9))

    # --- LAYER 8: Axis labels and region annotations ---
    ax_dia.set_xlabel(f'Extension [{length_unit}]', fontsize=11, fontweight='bold')
    ax_dia.set_ylabel(f'Force [{force_unit}]', fontsize=11, fontweight='bold')

    ax_dia.text(-x_bolt_max*0.5, -0.015*y_max/fs,
                '← Bolt Extension', fontsize=9, ha='center', va='top',
                color=color_bolt_line, fontweight='bold')
    ax_dia.text(x_memb_max*0.5, -0.015*y_max/fs,
                'Joint Compression →', fontsize=9, ha='center', va='top',
                color=color_member_line, fontweight='bold')

    # --- LAYER 9: Y-axis ticks ---
    y_ticks = [0, F_clamp/fs, F_V/fs, F_bolt/fs]
    y_labels = ['0',
                f'$F_{{clamp}}$ = {F_clamp/fs:.0f}',
                f'$F_V$ = {F_V/fs:.0f}',
                f'$F_B$ = {F_bolt/fs:.0f}']
    if show_separation:
        y_ticks.append(F_sep/fs)
        y_labels.append(f'$F_{{sep}}$ = {F_sep/fs:.0f}')
    ax_dia.set_yticks(y_ticks)
    ax_dia.set_yticklabels(y_labels, fontsize=8)

    # --- Axis limits and origin lines ---
    ax_dia.set_xlim(-x_bolt_max * 1.05, x_memb_max * 1.9)
    ax_dia.set_ylim(-0.03 * y_max / fs, y_max / fs)
    ax_dia.axvline(x=0, color='black', linewidth=0.8, alpha=0.3)
    ax_dia.axhline(y=0, color='black', linewidth=0.8, alpha=0.3)

    ax_dia.legend(loc='upper left', fontsize=7, framealpha=0.9)

    # --- Overall title ---
    fig.suptitle(title, fontsize=14, fontweight='bold', y=0.98)
    plt.tight_layout(rect=[0, 0, 1, 0.95])

    if save_path:
        fig.savefig(save_path, dpi=dpi, bbox_inches='tight',
                    facecolor='white', edgecolor='none')
        print(f"Composite figure saved to: {save_path}")

    return fig, (ax_sch, ax_dia)


def composite_from_geometry(
    d: float, A_t: float, A_d: float,
    E_b: float, E_m: float,
    l_d: float, l_t: float, L: float, d_w: float,
    F_V: float, F_A: float,
    n: float = 1.0,
    stiffness_method: str = "shigley",
    title: str = "Bolted Joint Diagram",
    **plot_kwargs
):
    """
    Complete pipeline with composite figure:
    bolt geometry → stiffness → diagram → composite plot.

    Same parameters as joint_diagram_from_geometry(),
    returns (data, fig, (ax_sch, ax_dia)).
    """
    k_b = compute_bolt_stiffness(A_d, A_t, E_b, l_d, l_t, d)
    if stiffness_method == "shigley":
        k_m = compute_member_stiffness_shigley(E_m, d, d_w, L)
    else:
        k_m = compute_member_stiffness_wileman(E_m, d, L)

    data = compute_joint_diagram(k_b, k_m, F_V, F_A, n)
    fig, axes = plot_composite_joint_figure(data, title=title, **plot_kwargs)

    print(f"\n{'='*55}")
    print(f"  BOLTED JOINT DIAGRAM SUMMARY")
    print(f"{'='*55}")
    print(f"  Bolt:    d = {d} mm, A_t = {A_t} mm²")
    print(f"  Grip:    L = {L} mm (l_d={l_d}, l_t={l_t})")
    print(f"  k_b    = {k_b:>12,.0f} N/mm")
    print(f"  k_m    = {k_m:>12,.0f} N/mm")
    print(f"  k_m/k_b = {k_m/k_b:.2f}")
    print(f"  Φ      = {data.Phi:.4f}")
    print(f"{'─'*55}")
    print(f"  F_V      = {F_V:>10,.0f} N  (preload)")
    print(f"  F_A      = {F_A:>10,.0f} N  (external)")
    print(f"  F_bolt   = {data.F_bolt:>10,.0f} N  (bolt under load)")
    print(f"  F_clamp  = {data.F_clamp:>10,.0f} N  (residual clamp)")
    print(f"  F_sep    = {data.F_sep:>10,.0f} N  (separation)")
    print(f"  ΔF_bolt  = {data.delta_F_bolt:>10,.0f} N  (Φ·F_A)")
    print(f"  ΔF_clamp = {data.delta_F_clamp:>10,.0f} N  ((1-Φ)·F_A)")
    print(f"{'='*55}")

    return data, fig, axes
```

### 13.8 Composite Figure Usage Examples

```python
if __name__ == "__main__":

    # ── COMPOSITE: M12 bolt with physical schematic ──
    data_c, fig_c, (ax_s, ax_d) = composite_from_geometry(
        d=12, A_t=84.3, A_d=113.1,
        E_b=210_000, E_m=210_000,
        l_d=15, l_t=10, L=25, d_w=18,
        F_V=50_000, F_A=15_000,
        title="M12 × 1.75 PC 10.9 — Complete Joint Diagram",
        save_path="composite_joint_diagram.png"
    )
    plt.show()

    # ── COMPOSITE: API 6A with kN units ──
    data_api, fig_api, _ = composite_from_geometry(
        d=25.4, A_t=353.0, A_d=506.7,
        E_b=205_000, E_m=210_000,
        l_d=30, l_t=45, L=75, d_w=38.1,
        F_V=150_000, F_A=50_000,
        title='API 6A — 1" A320 L7M on 6BX Flange',
        force_unit="kN", force_scale=1000.0,
        save_path="api6a_composite.png"
    )
    plt.show()

    # ── COMPOSITE: Diagram only (no schematic) ──
    data_ns = compute_joint_diagram(835_400, 2_690_900, 50_000, 15_000)
    fig_ns, _ = plot_composite_joint_figure(
        data_ns, show_schematic=False,
        title="Diagram Only (no schematic)",
        save_path="diagram_only.png"
    )
    plt.show()
```

---

## 14. Parametric Sensitivity: How Input Changes Affect the Diagram

### 14.1 Effect of Changing Preload $F_V$

Increasing $F_V$ shifts the operating point **upward** along both stiffness lines:

$$\frac{\partial F_{bolt}}{\partial F_V} = 1 \quad \text{(bolt force increases 1:1)}$$

$$\frac{\partial F_{clamp}}{\partial F_V} = 1 \quad \text{(clamp force increases 1:1)}$$

$$\frac{\partial F_{sep}}{\partial F_V} = \frac{1}{1-\Phi} > 1 \quad \text{(separation margin increases faster)}$$

The load triangle **shape remains identical** — it simply translates vertically.

### 14.2 Effect of Changing External Load $F_A$

Increasing $F_A$ expands the load triangle proportionally:

$$\frac{\partial F_{bolt}}{\partial F_A} = \Phi \quad \text{(bolt force sensitivity)}$$

$$\frac{\partial F_{clamp}}{\partial F_A} = -(1-\Phi) \quad \text{(clamp force sensitivity)}$$

For a hard joint ($\Phi = 0.15$): bolt sees only 15% of load increase, clamp loses 85%.
For a soft joint ($\Phi = 0.50$): bolt and clamp share equally.

### 14.3 Effect of Changing Stiffness Ratio

The stiffness ratio $k_m/k_b$ controls the **shape** of the entire diagram:

| $k_m/k_b$ | $\Phi$ | Bolt Line Angle | Member Line Angle | Triangle Shape |
|-----------|--------|-----------------|-------------------|----------------|
| 1 | 0.50 | 45° | 45° | Symmetric |
| 3 | 0.25 | Shallower | Steeper | Narrow, tall |
| 5 | 0.17 | Shallow | Very steep | Very narrow |
| 10 | 0.09 | Very shallow | Near vertical | Extremely narrow |
| 0.5 | 0.67 | Steep | Shallow | Wide, short |

### 14.4 Effect of Load Introduction Factor $n$

Reducing $n$ (moving load introduction closer to the interface) reduces the effective load factor:

$$\Phi_n = n \cdot \Phi$$

At $n = 0.3$ with $\Phi = 0.237$: effective $\Phi_n = 0.071$ — the bolt sees only 7.1% of external load.

This is **the most effective design lever** for improving fatigue life in bolted joints.

---

## 15. Extended Diagram: Including Preload Losses and Tightening Scatter

### 15.1 Complete VDI 2230 Joint Diagram with All Effects

The full engineering diagram includes:

$$F_{M,max} = \alpha_A \cdot F_{M,min}$$

$$F_{M,min} = F_{Kerf} + (1-\Phi_n) \cdot F_A + F_Z + \Delta F_{thermal}$$

Where $F_{Kerf}$ is the minimum required clamping force.

**Diagram force levels (bottom to top):**

| Level | Force | Description |
|-------|-------|-------------|
| 1 | $F_{Kerf}$ | Minimum required clamp force |
| 2 | $F_{Kerf} + (1-\Phi_n) F_A$ | Clamp force before embedding loss |
| 3 | $F_{M,min} = F_{Kerf} + (1-\Phi_n)F_A + F_Z$ | Minimum assembly preload |
| 4 | $F_{M,max} = \alpha_A \cdot F_{M,min}$ | Maximum assembly preload |
| 5 | $F_{M,max} + \Phi_n F_A$ | Maximum bolt force (design check) |
| 6 | $R_{p0.2} \cdot A_t$ | Bolt yield force (must not be exceeded) |

---

## 16. Complete Formula Reference

| Quantity | Formula |
|----------|---------|
| Bolt stiffness | $k_b = \frac{A_d \cdot A_t \cdot E_b}{A_d \cdot l_t + A_t \cdot l_d}$ |
| Member stiffness (Wileman) | $k_m = 0.78952 \cdot E_m \cdot d \cdot e^{0.62914 \cdot d/L}$ |
| Member stiffness (Shigley) | $k_m = \frac{\pi E_m d \tan\alpha}{\ln\left[\frac{(L\tan\alpha+d_w-d)(d_w+d)}{(L\tan\alpha+d_w+d)(d_w-d)}\right]}$ |
| Load factor | $\Phi = \frac{k_b}{k_b + k_m}$ |
| Effective load factor | $\Phi_n = n \cdot \Phi$ |
| Bolt force | $F_B = F_V + \Phi \cdot F_A$ |
| Clamp force | $F_{clamp} = F_V - (1 - \Phi) \cdot F_A$ |
| Separation load | $F_{A,sep} = \frac{F_V}{1 - \Phi}$ |
| Embedding loss | $F_Z = f_Z \cdot \frac{k_b \cdot k_m}{k_b + k_m}$ |
| Thermal preload change | $\Delta F_T = (\alpha_m - \alpha_b) \Delta T \cdot L \cdot \frac{k_b \cdot k_m}{k_b + k_m}$ |
| Fatigue stress amplitude | $\sigma_a = \frac{\Phi_n \cdot \Delta F_A}{2 \cdot A_t}$ |
| Safety against separation | $S_{sep} = \frac{F_{V,eff}}{(1-\Phi_n) \cdot F_A} \geq 1.2$ |
| Safety against yield | $S_y = \frac{R_{p0.2} \cdot A_t}{F_{M,max} + \Phi_n F_A} \geq 1.1$ |
| Load line slope | slope $= -k_m$ (parallel to member line) |
| Upper triangle area | $\frac{(\Phi \cdot F_A)^2}{2 \cdot k_b}$ |
| Lower triangle area | $\frac{((1-\Phi) \cdot F_A)^2}{2 \cdot k_m}$ |
| Load line @ $F_V$ | $x_{int} = -\frac{F_{bolt}}{k_b} + \frac{\Phi \cdot F_A}{k_m}$ |

---

## References

- VDI 2230 Part 1 (2015): *Systematic Calculation of Highly Stressed Bolted Joints — Joints with One Cylindrical Bolt*
- Bickford, J.H. (2008): *An Introduction to the Design and Behavior of Bolted Joints*, 4th Ed.
- Shigley, J.E. & Mischke, C.R.: *Mechanical Engineering Design*
- Wileman, J., Choudhury, M., Green, I. (1991): *Computation of Member Stiffness in Bolted Connections*, ASME J. Mechanical Design, 113, pp. 432–437
- Motosh, N. (1976): *Determination of Joint Stiffness in Bolted Connections*, ASME J. Engineering for Industry
- Eccles, W. (2010): *Bolted Joint Design*, Industrial Press
- ISO 898-1: *Mechanical properties of fasteners made of carbon steel and alloy steel*
- API 6A (2018): *Specification for Wellhead and Tree Equipment*
- ASME PCC-1-2022: *Guidelines for Pressure Boundary Bolted Flange Joint Assembly*
- **BoltScience** (2024): *Tutorial on the Basics of Bolted Joints — Joint Diagrams with External Forces Applied*, https://www.boltscience.com/pages/basics5.htm
  - Source for §1.1 (Physical Intuition) and §7 (Hard/Soft joint qualitative framing)
  - Key conceptual contributions: load path explanation, hard/soft joint definitions, reduced-shank design rationale
