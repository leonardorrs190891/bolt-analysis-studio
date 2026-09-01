# MSD Framework -- PART X: PRELOAD LOSS MODELS -- COMPREHENSIVE TREATMENT

**Complete Technical Reference for Bolt Analysis Studio**

**Authors:** L. Ribeiro, D. Carvalho, S.C. Naves, T. Santos, V. Marques, G. Arruda
**Institution:** LTAD/UFU -- Tribology and Wear Technology Laboratory, Federal University of Uberlândia
**Project:** Petrobras R&D -- Bolted Flange Joint Integrity

**Version 4.0 - Extended English Edition**

---

**Abstract.** Preload loss is the central failure mode in bolted joint integrity: every mechanism discussed in the preceding Parts (self-loosening, wear, friction degradation, creep) ultimately manifests as a reduction in the clamping force that holds the joint together. This document provides a comprehensive mathematical treatment of 15 preload loss models implemented in the Bolt Analysis Studio, organized from simple phenomenological fitting functions to physics-based multi-mechanism formulations. The single exponential model provides a first-order approximation; the double exponential (two-rate) model separates fast embedding from slow cyclic degradation; the stretched exponential (Kohlrausch-Williams-Watts) captures heterogeneous relaxation. The power-law model of Lu et al. (2024) achieves greater than 85% fitting accuracy with only two parameters. The VDI 2230 embedding model provides standards-based quantification of surface settling. The Jiang two-stage and three-stage models (Jiang et al., 2003, 2004) decompose loosening into non-rotational (plastic deformation), rotational (nut back-off), and fatigue phases. Norton-Bailey creep relaxation covers high-temperature service. Thermal effects account for differential expansion between bolt and clamped members. The D-N (displacement-life) curve provides a fatigue-like framework for loosening life prediction, complemented by Miner's rule for variable-amplitude loading. The energy dissipation and combined mechanism models tie all sources together into a unified preload tracking function. All models include parameter selection guidelines, typical ranges for bolted flange joints, and cross-references to the coupled analysis framework of Part XI.

---

## Table of Contents

| Section | Title | Page Concept |
|---------|-------|--------------|
| 40 | Introduction to Preload Loss | Taxonomy of mechanisms |
| 41 | Single Exponential Decay Model | First-order approximation |
| 42 | Double Exponential Decay Model (Li et al.) | Two-mechanism decomposition |
| 43 | Stretched Exponential (KWW) Model | Distributed relaxation |
| 44 | VDI 2230 Embedding Loss Model | Standards-based settling |
| 45 | Norton-Bailey Creep Relaxation Model | Elevated-temperature relaxation |
| 46 | Thermal Effects Model | Differential expansion |
| 47 | Power-Law Model (Lu et al., 2024) | Minimal-parameter fitting |
| 48 | Logarithmic Model | Early-cycle approximation |
| 49 | Jiang Two-Stage Model | Material vs. structural loosening |
| 50 | Jiang Three-Stage Extended Model (Gong et al., 2019) | Fatigue acceleration |
| 51 | Combined Mechanism Model | Superposition of all mechanisms |
| 52 | D-N Loosening Curve (Displacement-Life) | Life prediction |
| 53 | Miner's Rule Damage Accumulation | Variable amplitude loading |
| 54 | Energy Dissipation Model | Hysteretic energy approach |
| 55 | Rotation Angle Tracking Model | Kinematic preload coupling |
| 56 | Model Selection Guide | Comparison and recommendations |

---

## 40. Introduction to Preload Loss

### 40.1 Why Preload Decreases Over Time

A bolted joint derives its function from the clamping force --- the preload --- that holds the members together. Once a bolt is tightened, however, that initial preload $F_{p,0}$ begins to diminish through a variety of physical mechanisms. Understanding the magnitude and time scale of each loss mechanism is essential for safe joint design, because the residual preload $F_p(t)$ at any point during service determines whether the joint can sustain external loads, maintain the gasket seal, and resist self-loosening.

The total preload at any cycle count $N$ (or equivalently, time $t = N/f$) is the superposition of all individual losses:

$$F_p(N) = F_{p,0} - \sum_{i} \Delta F_i(N)$$

where $\Delta F_i$ is the preload loss contribution of mechanism $i$. This additive structure is an approximation; in reality the mechanisms are coupled (e.g., lower preload reduces friction, which accelerates rotational loosening), but the superposition model is the accepted engineering practice and provides a conservative framework for design.

### 40.2 Categories of Preload Loss

Preload loss mechanisms fall into two broad categories:

**Category 1: Rotational Loosening (Junker Mechanism)**

Rotation of the nut (or bolt head) on the threads converts preload into nut back-off angle through the helix kinematic relation. This mechanism is covered in detail in **Part V** of this series. It requires transverse slip at both bearing and thread surfaces simultaneously and is the dominant failure mode under transverse vibration.

**Category 2: Non-Rotational Losses**

These mechanisms reduce preload without any rotation of the fastener. They include:

| Mechanism | Physical Basis | Time Scale | Typical Loss |
|-----------|---------------|------------|--------------|
| **Embedding (Settling)** | Plastic deformation of asperity peaks at contact surfaces | First 10-200 cycles | 5-15% of $F_{p,0}$ |
| **Gasket Creep** | Viscoelastic flow of gasket material under sustained compression | Hours to months | 10-40% of $F_{p,0}$ |
| **Stress Relaxation** | Thermally activated dislocation rearrangement in the bolt | Hours to years | 5-30% of $F_{p,0}$ |
| **Wear** | Material removal at sliding contact interfaces | Thousands of cycles | 2-10% of $F_{p,0}$ |
| **Differential Thermal Expansion** | Mismatch of thermal expansion coefficients between bolt and members | Temperature change event | -20% to +30% of $F_{p,0}$ |
| **Cyclic Plastic Strain** | Accumulation of plastic deformation at thread roots and under head | Hundreds to thousands of cycles | 5-20% of $F_{p,0}$ |

### 40.3 Preload Loss Diagram on a Single Joint

The following diagram illustrates where each loss mechanism acts within a typical bolted flanged joint:

```
                    APPLIED TORQUE T_a
                         │
                    ┌────▼────┐
                    │  BOLT   │
                    │  HEAD   │ ◄── Bearing surface embedding (ΔF_embed_1)
                    └────┬────┘     Bearing friction wear (ΔF_wear_1)
                         │
                    ┌────▼────┐
                    │ WASHER  │ ◄── Washer embedding (ΔF_embed_2)
                    └────┬────┘
                         │
                ╔════════▼════════╗
                ║   FLANGE 1      ║ ◄── Flange surface embedding (ΔF_embed_3)
                ║                 ║     Thermal expansion α_m (ΔF_thermal)
                ╠═════════════════╣
                ║   GASKET        ║ ◄── Gasket creep (ΔF_creep)
                ║   (if present)  ║     Gasket relaxation (ΔF_relax_gasket)
                ╠═════════════════╣
                ║   FLANGE 2      ║ ◄── Flange surface embedding (ΔF_embed_4)
                ║                 ║     Thermal expansion α_m (ΔF_thermal)
                ╚════════▲════════╝
                         │
                    ┌────▼────┐
                    │  STUD   │ ◄── Bolt stress relaxation (ΔF_relax_bolt)
                    │ (shank) │     Thermal expansion α_b (ΔF_thermal)
                    └────┬────┘     Cyclic strain accumulation (ΔF_cyclic)
                         │
                    ┌────▼────┐
                    │  NUT    │ ◄── Nut-thread embedding (ΔF_embed_5)
                    └────┬────┘     Bearing surface wear (ΔF_wear_2)
                         │
                    ┌────▼────┐
                    │ THREAD  │ ◄── Thread root cyclic plasticity (ΔF_cyclic)
                    │ CONTACT │     Thread flank wear (ΔF_wear_3)
                    └─────────┘     ROTATIONAL LOOSENING (ΔF_rot) ← Part V
```

### 40.4 Total Preload Evolution

Combining all mechanisms into a single expression:

$$F_p(N) = F_{p,0} - \underbrace{\Delta F_{embed}(N)}_{\text{embedding}} - \underbrace{\Delta F_{creep}(t)}_{\text{gasket creep}} - \underbrace{\Delta F_{relax}(t, T)}_{\text{stress relaxation}} - \underbrace{\Delta F_{wear}(N)}_{\text{surface wear}} - \underbrace{\Delta F_{thermal}(\Delta T)}_{\text{thermal}} - \underbrace{\Delta F_{rot}(N)}_{\text{rotational}}$$

where $t = N/f$ converts cycles to elapsed time.

### 40.5 Preload Loss as a System Stiffness Problem

All non-rotational mechanisms ultimately reduce preload through the same mechanical pathway: they introduce an additional deformation $\delta_i$ in the clamped stack, and the resulting preload change is governed by the system stiffness:

$$\Delta F_i = k_{sys} \cdot \delta_i$$

where the system (series) stiffness is:

$$k_{sys} = \frac{k_b \cdot k_m}{k_b + k_m}$$

Here $k_b$ is the bolt stiffness and $k_m$ is the clamped member stiffness. This relation is central to VDI 2230 and appears in every non-rotational loss model.

---

## 41. Single Exponential Decay Model

### 41.1 Formulation

The simplest model for preload decay assumes a first-order process with a single characteristic rate:

$$F(N) = F_\infty + (F_0 - F_\infty) \cdot \exp(-\lambda N)$$

where:
- $F_0$ = initial preload [N]
- $F_\infty$ = residual (plateau) preload [N], the asymptotic preload at $N \to \infty$
- $\lambda$ = decay rate constant [cycles$^{-1}$]
- $N$ = number of loading cycles

### 41.2 Rate of Preload Loss

The instantaneous loss rate is obtained by differentiation:

$$\frac{dF}{dN} = -\lambda \cdot (F_0 - F_\infty) \cdot \exp(-\lambda N)$$

At $N = 0$, the initial loss rate is:

$$\left.\frac{dF}{dN}\right|_{N=0} = -\lambda \cdot (F_0 - F_\infty)$$

### 41.3 Half-Life

The half-life $N_{1/2}$ is defined as the number of cycles required for the preload to lose half of its total decay range $(F_0 - F_\infty)$:

$$F(N_{1/2}) = F_\infty + \frac{1}{2}(F_0 - F_\infty)$$

Solving:

$$N_{1/2} = \frac{\ln 2}{\lambda} \approx \frac{0.693}{\lambda}$$

### 41.4 Parameter Ranges

| Parameter | Symbol | Typical Range | Physical Meaning |
|-----------|--------|---------------|------------------|
| Decay rate | $\lambda$ | 0.001 - 0.01 cycles$^{-1}$ | Speed of preload decay |
| Residual ratio | $F_\infty / F_0$ | 0.60 - 0.85 | Fraction of preload retained at steady state |
| Half-life | $N_{1/2}$ | 70 - 700 cycles | Cycles to half-decay |

**Interpretation of $\lambda$**:
- $\lambda = 0.001$: Slow decay, half-life $\approx 693$ cycles. Typical for well-designed joints with low surface roughness.
- $\lambda = 0.01$: Fast decay, half-life $\approx 69$ cycles. Typical for rough surfaces or high transverse loads.

### 41.5 Normalized Form

For comparison across different preload levels, the normalized form is often used:

$$\frac{F(N)}{F_0} = r + (1 - r) \cdot \exp(-\lambda N)$$

where $r = F_\infty / F_0$ is the residual preload ratio.

### 41.6 When to Use

- First approximation when only limited test data are available.
- Joints dominated by a single loss mechanism (e.g., embedding only).
- Short-duration analyses where multi-stage behavior is not yet manifest.

### 41.7 Limitations

1. Cannot capture two-stage or multi-stage behavior (e.g., Jiang Stage I followed by Stage II).
2. Assumes a constant decay rate $\lambda$, which is physically unrealistic for mechanisms with different time scales.
3. Always approaches $F_\infty$ monotonically; cannot model acceleration at high cycle counts.
4. Provides no physical decomposition of loss mechanisms.

### 41.8 References

- Bickford, J. H. (2008). *Introduction to the Design and Behavior of Bolted Joints*, 4th ed. CRC Press.
- Pai, N. G., and Hess, D. P. (2002). "Three-dimensional finite element analysis of threaded fastener loosening due to dynamic shear load." *Engineering Failure Analysis*, 9(4), 383-402. DOI: [10.1016/S1350-6307(01)00024-3](https://doi.org/10.1016/S1350-6307(01)00024-3)

---

## 42. Double Exponential Decay Model (Li et al.)

### 42.1 Motivation

Experimental preload decay curves frequently exhibit two clearly distinguishable phases: a rapid initial decay followed by a slower long-term decline. The single exponential model cannot capture this behavior with a single rate constant. The double exponential introduces two superimposed decay processes, each with its own time scale and amplitude.

### 42.2 Formulation

$$F(N) = F_\infty + A_1 \cdot \exp(-\lambda_1 N) + A_2 \cdot \exp(-\lambda_2 N)$$

where:
- $\lambda_1$ = fast decay rate [cycles$^{-1}$], governing the early rapid drop
- $\lambda_2$ = slow decay rate [cycles$^{-1}$], governing long-term gradual decline
- $A_1$ = amplitude of the fast component [N]
- $A_2$ = amplitude of the slow component [N]
- $F_\infty$ = residual preload [N]

### 42.3 Partition of Initial Preload

At $N = 0$:

$$F(0) = F_\infty + A_1 + A_2 = F_0$$

Therefore:

$$A_1 + A_2 + F_\infty = F_0$$

This constraint ensures that the three amplitude parameters are not independent. Given $F_0$, only two of $(A_1, A_2, F_\infty)$ are free.

### 42.4 Physical Interpretation of the Two Components

**Fast Component ($\lambda_1$, $A_1$):**
- Dominates in the first 10-100 cycles.
- Physical mechanisms: embedding (plastic deformation of asperity peaks), gasket seating, washer bedding-in, initial thread settling.
- Typical rate: $\lambda_1 = 0.01$ to $0.10$ cycles$^{-1}$.

**Slow Component ($\lambda_2$, $A_2$):**
- Dominates after the fast component has saturated.
- Physical mechanisms: gradual thread slip accumulation, slow creep, fretting wear, micro-plastic strain accumulation at thread roots.
- Typical rate: $\lambda_2 = 0.001$ to $0.01$ cycles$^{-1}$.

### 42.5 Rate of Loss

$$\frac{dF}{dN} = -\lambda_1 A_1 \exp(-\lambda_1 N) - \lambda_2 A_2 \exp(-\lambda_2 N)$$

The initial loss rate at $N = 0$ is:

$$\left.\frac{dF}{dN}\right|_{N=0} = -(\lambda_1 A_1 + \lambda_2 A_2)$$

### 42.6 Decomposition into Individual Components

The fast and slow components can be isolated for separate analysis:

$$F_{fast}(N) = A_1 \cdot \exp(-\lambda_1 N)$$

$$F_{slow}(N) = A_2 \cdot \exp(-\lambda_2 N)$$

This decomposition is useful for identifying which mechanism dominates at a given cycle count.

### 42.7 Parameter Ranges

| Parameter | Symbol | Typical Range | Physical Origin |
|-----------|--------|---------------|-----------------|
| Fast rate | $\lambda_1$ | 0.01 - 0.10 | Embedding, plastic settling |
| Slow rate | $\lambda_2$ | 0.001 - 0.01 | Thread slip, wear |
| Rate ratio | $\lambda_1 / \lambda_2$ | 5 - 20 | Separation of time scales |
| Fast amplitude ratio | $A_1 / F_0$ | 0.05 - 0.20 | Fraction lost to embedding |
| Slow amplitude ratio | $A_2 / F_0$ | 0.10 - 0.30 | Fraction lost to slow mechanisms |
| Residual ratio | $F_\infty / F_0$ | 0.50 - 0.80 | Asymptotic retention |

### 42.8 When to Use

- Experimental data show a clear "knee" or inflection separating two decay regimes.
- Joint has both embedding (short-term) and wear or creep (long-term) as dominant mechanisms.
- Sufficient data points exist across both time scales to fit four parameters ($A_1$, $\lambda_1$, $A_2$, $\lambda_2$) reliably.

### 42.9 References

- Li, Z., Chen, Y., Sun, W., Jiang, P., Pan, J., and Guan, Z. (2021). "Study on self-loosening mechanism of bolted joint under rotational vibration." *Tribology International*, 161, 107074. DOI: [10.1016/j.triboint.2021.107074](https://doi.org/10.1016/j.triboint.2021.107074)
- Nassar, S. A., and Housari, B. A. (2007). "Study of the effect of hole clearance and thread fit on the self-loosening of threaded fasteners." *ASME Journal of Mechanical Design*, 129(6), 586-594. DOI: [10.1115/1.2717227](https://doi.org/10.1115/1.2717227)

---

## 43. Stretched Exponential (Kohlrausch-Williams-Watts) Model

### 43.1 Motivation

Real bolted joints contain multiple interfaces (thread flanks, bearing surfaces, washer-flange, flange-gasket, flange-flange), each with its own local stress state, roughness, material pair, and hence its own relaxation time. Rather than fitting a sum of discrete exponentials (which requires specifying the number of mechanisms a priori), the stretched exponential provides a continuous distribution of relaxation times with a single additional parameter.

### 43.2 Formulation

$$F(N) = F_0 \cdot \exp\!\left[-\left(\frac{N}{N_0}\right)^\beta\right]$$

where:
- $N_0$ = characteristic relaxation cycle count
- $\beta$ = stretching exponent, $0 < \beta \leq 1$

### 43.3 Physical Meaning of $\beta$

The stretching exponent $\beta$ controls the shape of the decay curve:

| $\beta$ Value | Behavior | Physical Interpretation |
|:---:|:---:|---|
| $\beta = 1$ | Standard exponential (Debye) | Single relaxation time, homogeneous joint |
| $\beta \approx 0.7$ | Moderately stretched | 2-3 dominant relaxation processes |
| $\beta \approx 0.5$ | Strongly stretched | Broad distribution of relaxation times |
| $\beta \approx 0.3$ | Highly stretched | Extremely heterogeneous joint, many interfaces |

The KWW function can be formally written as a superposition of infinitely many exponentials weighted by a distribution $g(\tau)$:

$$\exp\!\left[-\left(\frac{N}{N_0}\right)^\beta\right] = \int_0^\infty g(\tau) \cdot \exp\!\left(-\frac{N}{\tau}\right) d\tau$$

The distribution $g(\tau)$ is known analytically for certain values of $\beta$ (e.g., $\beta = 1/2$ yields a Levy distribution) and numerically for others. The key point is that a single parameter $\beta$ encodes the breadth of the relaxation spectrum.

### 43.4 Rate of Preload Loss

$$\frac{dF}{dN} = -\frac{\beta}{N_0} \left(\frac{N}{N_0}\right)^{\beta - 1} \cdot F(N)$$

Note that for $\beta < 1$, the rate diverges as $N \to 0^+$. This is physically meaningful: the fastest relaxation processes complete almost instantaneously (embedding of the roughest asperities), producing a very steep initial slope.

### 43.5 Characteristic Time Scales

The mean relaxation time for the KWW distribution is:

$$\langle \tau \rangle = \frac{N_0}{\beta} \cdot \Gamma\!\left(\frac{1}{\beta}\right)$$

where $\Gamma$ is the Euler gamma function. For $\beta = 0.5$, this gives $\langle \tau \rangle = 2 N_0$; for $\beta = 1$, $\langle \tau \rangle = N_0$.

### 43.6 Parameter Ranges

| Parameter | Symbol | Typical Range | Units |
|-----------|--------|---------------|-------|
| Characteristic cycles | $N_0$ | 100 - 5000 | cycles |
| Stretching exponent | $\beta$ | 0.3 - 0.8 | dimensionless |

### 43.7 Comparison with Double Exponential

```
   F/F0
   1.0 ┬─────────────────────────────────────────────
       │╲ Double exponential: sharp initial knee
       │ ╲╲
       │  ╲ ╲         KWW (β = 0.5): gradual curvature
       │   ╲  ╲╲                throughout
       │    ╲   ╲ ╲
   0.8 ┤     ╲    ╲  ╲
       │      ╲     ╲   ╲
       │       ╲      ╲    ╲╲
       │        ╲       ╲      ╲╲
       │         ╲        ╲       ╲╲╲
   0.6 ┤          ╲╲        ╲         ╲╲╲╲
       │            ╲╲        ╲╲           ╲╲╲╲╲╲
       │              ╲╲╲        ╲╲╲              ╲╲╲╲╲╲╲
       │                 ╲╲╲╲╲      ╲╲╲╲╲                 ────────
       │                      ╲╲╲╲╲╲╲╲╲╲╲╲╲╲
   0.4 ┤                            ──────────────────────────────
       │
       └──────┬──────┬──────┬──────┬──────┬──────┬──────┬──────
              0    200    400    600    800   1000   1200   1400
                                  Cycles N
```

The double exponential shows a sharper transition between its two regimes, while the KWW function produces a smoothly varying curvature.

### 43.8 When to Use

- Complex joints with many interfaces of different materials and roughnesses.
- When the number of discrete relaxation mechanisms is unknown.
- For fitting experimental data where neither single nor double exponential gives satisfactory residuals.
- Gasket joints, where the gasket itself exhibits a broad relaxation spectrum.

### 43.9 Limitations

- The model predicts $F \to 0$ as $N \to \infty$, with no residual preload floor. For practical use, a modified form $F(N) = F_\infty + (F_0 - F_\infty) \cdot \exp[-(N/N_0)^\beta]$ should be employed.
- Parameter identification requires nonlinear regression.

### 43.10 References

- Kohlrausch, R. (1854). "Theorie des elektrischen Ruckstandes in der Leidener Flasche." *Poggendorff's Annalen der Physik und Chemie*, 91, 179-214.
- Williams, G., and Watts, D. C. (1970). "Non-symmetrical dielectric relaxation behavior arising from a simple empirical decay function." *Transactions of the Faraday Society*, 66, 80-85. DOI: [10.1039/TF9706600080](https://doi.org/10.1039/TF9706600080)
- Phillips, J. C. (1996). "Stretched exponential relaxation in molecular and electronic glasses." *Reports on Progress in Physics*, 59(9), 1133-1207.

---

## 44. VDI 2230 Embedding Loss Model

### 44.1 Fundamentals

Embedding (also called settling or bedding-in) is the plastic flattening of surface asperities at contact interfaces under the sustained compressive load of the bolt preload. It is an irreversible process that reduces the effective grip length and hence the preload. VDI 2230 Part 1 (2015) provides a standardized method for estimating embedding losses.

### 44.2 Basic Equation

The preload loss due to embedding is:

$$\Delta F_{embed} = f_Z \cdot \frac{k_b \cdot k_m}{k_b + k_m} = f_Z \cdot k_{sys}$$

where:
- $f_Z$ = total embedding deformation [$\mu$m], summed over all interfaces
- $k_b$ = bolt stiffness [N/mm]
- $k_m$ = clamped member stiffness [N/mm]
- $k_{sys}$ = system (series) stiffness [N/mm]

### 44.3 Embedding Values per Interface (VDI 2230 Table A7)

The embedding deformation per interface depends on surface roughness:

| Surface Quality | Roughness $R_a$ | Embedding per Interface $f_{z,i}$ | Typical Application |
|:---|:---:|:---:|:---|
| Ground / Lapped | $R_a < 1.6\ \mu\text{m}$ | 1.0 - 2.0 $\mu$m | Precision flanges |
| Machined (turned/milled) | $R_a = 1.6 - 3.2\ \mu\text{m}$ | 2.0 - 3.5 $\mu$m | Standard flanges |
| Rough machined | $R_a = 3.2 - 6.3\ \mu\text{m}$ | 3.0 - 5.0 $\mu$m | As-cast surfaces |
| As-forged / As-cast | $R_a > 6.3\ \mu\text{m}$ | 4.0 - 6.5 $\mu$m | Structural steel |

### 44.4 Total Embedding for a Complete Joint

For a joint with $n$ contact interfaces:

$$f_Z = \sum_{i=1}^{n} f_{z,i}$$

A typical bolted flanged connection has 4-5 interfaces:

| Interface | Location | Typical $f_{z,i}$ |
|-----------|----------|:---:|
| Head bearing surface | Bolt head to washer or flange | 2.5 $\mu$m |
| Washer to flange (top) | Upper washer-flange contact | 2.0 $\mu$m |
| Flange-to-flange or Flange-gasket | Joint interface | 3.0 $\mu$m |
| Washer to flange (bottom) | Lower washer-flange contact | 2.0 $\mu$m |
| Nut bearing surface | Nut to washer or flange | 2.5 $\mu$m |
| **Total** | | **12.0 $\mu$m** |

### 44.5 Time-Dependent Settling

Embedding does not occur instantaneously. The process follows a saturating exponential as asperity peaks are progressively crushed:

$$F(N) = F_0 - \Delta F_{embed} \cdot \left[1 - \exp\!\left(-\frac{N}{\tau_{embed}}\right)\right]$$

where $\tau_{embed}$ is the settling time constant, typically:

| Condition | $\tau_{embed}$ [cycles] |
|:---|:---:|
| Static (no cycling, pure creep) | 50 - 200 |
| Low frequency ($f < 5$ Hz) | 20 - 100 |
| High frequency ($f > 20$ Hz) | 10 - 50 |

After $N = 3\tau_{embed}$ to $5\tau_{embed}$ cycles, embedding is $\approx 95\%$ to $99\%$ complete.

### 44.6 Rate of Embedding Loss

$$\frac{dF}{dN} = -\frac{\Delta F_{embed}}{\tau_{embed}} \cdot \exp\!\left(-\frac{N}{\tau_{embed}}\right)$$

The initial embedding rate at $N = 0$ is:

$$\left.\frac{dF}{dN}\right|_{N=0} = -\frac{\Delta F_{embed}}{\tau_{embed}}$$

### 44.7 Percentage of Preload Lost to Embedding

$$\frac{\Delta F_{embed}}{F_0} = \frac{f_Z \cdot k_{sys}}{F_0}$$

For a typical M16 bolt ($k_b = 5 \times 10^5$ N/mm, $k_m = 1.5 \times 10^6$ N/mm, $F_0 = 50{,}000$ N, $f_Z = 12\ \mu$m):

$$k_{sys} = \frac{5 \times 10^5 \times 1.5 \times 10^6}{5 \times 10^5 + 1.5 \times 10^6} = 3.75 \times 10^5\ \text{N/mm}$$

$$\Delta F_{embed} = 3.75 \times 10^5 \times 12 \times 10^{-3} = 4{,}500\ \text{N}$$

$$\frac{\Delta F_{embed}}{F_0} = \frac{4{,}500}{50{,}000} = 9.0\%$$

### 44.8 Design Implication

VDI 2230 recommends that the initial preload be set high enough to ensure that after embedding, the minimum service preload $F_{V,min}$ still satisfies all functional requirements:

$$F_{V,min} = F_{p,0} - \Delta F_{embed} - \Delta F_{thermal} \geq F_{required}$$

### 44.9 When to Use

- Every bolted joint design should include an embedding loss estimate.
- Required by VDI 2230 Part 1 for systematic bolt calculation.
- Especially important for joints with multiple interfaces or rough surfaces.

### 44.10 References

- VDI 2230 Part 1 (2015). "Systematic Calculation of Highly Stressed Bolted Joints --- Joints with One Cylindrical Bolt." Verein Deutscher Ingenieure.
- Bickford, J. H. (2008). *Introduction to the Design and Behavior of Bolted Joints*, 4th ed., Chapter 11: "Relaxation." CRC Press.

---

## 45. Norton-Bailey Creep Relaxation Model

### 45.1 Physical Background

At elevated temperatures, metals undergo time-dependent inelastic deformation known as creep. In a bolted joint, where the bolt is constrained to a fixed elongation by the clamped members, creep manifests as stress relaxation: the bolt stress (and hence preload) decreases over time while the total strain remains approximately constant.

Creep becomes significant when the service temperature exceeds approximately 40% of the material's absolute melting temperature:

$$T_{service} > 0.4 \times T_{melt}\ [\text{K}]$$

For common bolt materials:

| Material | $T_{melt}$ [K] | Creep Threshold ($0.4 \times T_{melt}$) [C] |
|:---|:---:|:---:|
| Carbon steel (ASTM A193 B7) | 1810 | 451 |
| Alloy steel (ASTM A193 B7M) | 1810 | 451 |
| Stainless 316 (ASTM A193 B8M) | 1670 | 395 |
| Inconel 718 | 1610 | 371 |
| Nimonic 80A | 1640 | 383 |

### 45.2 Norton-Bailey Creep Law

The uniaxial creep strain is modeled as:

$$\varepsilon_{cr} = A \cdot \sigma^n \cdot t^m$$

where:
- $A$ = creep coefficient [MPa$^{-n}$ hr$^{-m}$]
- $\sigma$ = uniaxial stress [MPa]
- $n$ = stress exponent (Norton exponent)
- $t$ = time [hours]
- $m$ = time exponent (Bailey exponent), $0 < m \leq 1$

### 45.3 Temperature Dependence (Arrhenius)

The creep coefficient $A$ incorporates temperature through an Arrhenius activation:

$$A(T) = A_0 \cdot \exp\!\left(-\frac{Q}{R \cdot T}\right)$$

where:
- $Q$ = activation energy for creep [J/mol]
- $R$ = universal gas constant = 8.314 J/(mol$\cdot$K)
- $T$ = absolute temperature [K]
- $A_0$ = reference creep coefficient

### 45.4 Stress Relaxation at Constant Strain

In a bolted joint, the total strain is approximately constant (the bolt is constrained by the members). The total strain is the sum of elastic and creep strains:

$$\varepsilon_{total} = \varepsilon_{elastic} + \varepsilon_{creep} = \frac{\sigma}{E} + \varepsilon_{cr}$$

Differentiating with $\varepsilon_{total} = \text{const}$:

$$0 = \frac{1}{E}\frac{d\sigma}{dt} + A \cdot m \cdot \sigma^n \cdot t^{m-1}$$

For $m = 1$ (secondary creep, time-hardening), the relaxation solution is:

$$\sigma(t) = \sigma_0 \cdot \left[1 + (n-1) \cdot A \cdot E \cdot \sigma_0^{n-1} \cdot \exp\!\left(-\frac{Q}{RT}\right) \cdot t\right]^{-\frac{1}{n-1}}$$

For the special case $n = 1$ (linear viscous creep):

$$\sigma(t) = \sigma_0 \cdot \exp\!\left(-A \cdot E \cdot \exp\!\left(-\frac{Q}{RT}\right) \cdot t\right)$$

### 45.5 Conversion to Preload

The preload at time $t$ is:

$$F(t) = \sigma(t) \cdot A_s$$

where $A_s$ is the tensile stress area of the bolt. Conversion from cycles:

$$t = \frac{N}{f}$$

where $f$ is the loading frequency [Hz].

### 45.6 Typical Parameters

| Parameter | Symbol | Steel (B7) | Stainless (B8M) | Inconel 718 | Units |
|:---|:---:|:---:|:---:|:---:|:---:|
| Stress exponent | $n$ | 4.5 - 5.5 | 5.0 - 7.0 | 3.0 - 4.0 | -- |
| Time exponent | $m$ | 0.3 - 0.5 | 0.3 - 0.6 | 0.2 - 0.4 | -- |
| Activation energy | $Q$ | 250 - 300 | 280 - 350 | 300 - 360 | kJ/mol |
| Creep coefficient | $A$ | $10^{-20}$ - $10^{-15}$ | $10^{-22}$ - $10^{-17}$ | $10^{-25}$ - $10^{-20}$ | MPa$^{-n}$ hr$^{-m}$ |

### 45.7 When Significant

The Norton-Bailey model is critical for:
- Service temperatures above the creep threshold (see table in Section 45.1).
- Long service durations (years) even at moderate temperatures.
- Gasket joints where the gasket material creeps at room temperature.
- Petrobras subsea and topside applications where flanges may experience elevated temperatures from process fluid.

### 45.8 Graphical Behavior

```
   F/F0
   1.0 ┬──────────────╮
       │               ╲
       │                ╲      T = 300 C (below threshold)
   0.9 ┤                 ╲╲╲╲╲╲╲╲╲╲╲╲╲╲╲╲╲╲╲╲╲╲╲╲╲╲╲╲╲╲╲
       │                  ╲
       │                   ╲         T = 400 C
   0.8 ┤                    ╲╲╲
       │                       ╲╲╲
       │                          ╲╲╲╲         T = 500 C
   0.7 ┤                              ╲╲╲╲
       │                                   ╲╲╲╲╲
       │                                         ╲╲╲╲╲╲╲
   0.6 ┤                                                ╲╲╲╲╲╲╲╲╲
       │
       └──────┬──────┬──────┬──────┬──────┬──────┬──────┬──────
              0    1000   2000   3000   4000   5000   6000   7000
                              Time [hours]
```

### 45.9 References

- Norton, F. H. (1929). *The Creep of Steel at High Temperatures*. McGraw-Hill.
- Bailey, R. W. (1935). "The utilization of creep test data in engineering design." *Proceedings of the Institution of Mechanical Engineers*, 131(1), 131-349. DOI: [10.1243/PIME_PROC_1935_131_012_02](https://doi.org/10.1243/PIME_PROC_1935_131_012_02)
- Penny, R. K., and Marriott, D. L. (1995). *Design for Creep*, 2nd ed. Chapman & Hall.
- ASME PCC-1 (2013). "Guidelines for Pressure Boundary Bolted Flange Joint Assembly." Appendix O: Creep and Stress Relaxation.

---

## 46. Thermal Effects Model

### 46.1 Physical Background

When a bolted joint experiences a temperature change $\Delta T$, the bolt and the clamped members expand by different amounts if their thermal expansion coefficients differ. This differential expansion changes the clamping length and hence the preload. Additionally, the elastic modulus of the bolt material decreases with temperature, reducing both bolt stiffness and the stress corresponding to a given strain.

### 46.2 Differential Thermal Expansion

The preload change due to differential thermal expansion is:

$$\Delta F_{thermal} = k_{sys} \cdot L_{grip} \cdot \Delta T \cdot (\alpha_m - \alpha_b)$$

where:
- $k_{sys} = \dfrac{k_b \cdot k_m}{k_b + k_m}$ = system stiffness [N/mm]
- $L_{grip}$ = grip length (total clamped length) [mm]
- $\Delta T = T_{service} - T_{assembly}$ = temperature change [C or K]
- $\alpha_m$ = thermal expansion coefficient of clamped members [K$^{-1}$]
- $\alpha_b$ = thermal expansion coefficient of bolt [K$^{-1}$]

### 46.3 Sign Convention

The sign of the preload change depends on which material expands more:

| Condition | Heating Effect | Cooling Effect |
|:---|:---:|:---:|
| $\alpha_m > \alpha_b$ (e.g., aluminum members, steel bolt) | Preload **increases** | Preload **decreases** |
| $\alpha_m < \alpha_b$ (e.g., steel members, austenitic bolt) | Preload **decreases** | Preload **increases** |
| $\alpha_m = \alpha_b$ (same material) | No change | No change |

### 46.4 Common Material Combinations

| Material | $\alpha$ [$\times 10^{-6}$ K$^{-1}$] | Note |
|:---|:---:|:---|
| Carbon steel (bolt) | 11-12 | A193 B7, A320 L7 |
| Austenitic stainless steel | 16-17 | A193 B8, B8M |
| Cast iron | 10-11 | Flange material |
| Carbon steel (flange) | 11-12 | A105, A350 LF2 |
| Aluminum alloy | 22-24 | Lightweight flanges |
| Inconel 718 | 12-13 | High-temperature bolt |
| Titanium alloy | 8-9 | Aerospace applications |

### 46.5 Elastic Modulus Degradation

The elastic modulus of metals decreases approximately linearly with temperature:

$$E(T) = E_0 \cdot \left[1 - \beta_E \cdot (T - T_0)\right]$$

where:
- $E_0$ = modulus at reference temperature $T_0$ (typically 20 C)
- $\beta_E$ = modulus temperature coefficient

Typical values of $\beta_E$:

| Material | $\beta_E$ [C$^{-1}$] |
|:---|:---:|
| Structural steels | $3.0 \times 10^{-4}$ to $4.0 \times 10^{-4}$ |
| Stainless steels | $3.5 \times 10^{-4}$ to $4.5 \times 10^{-4}$ |
| Aluminum alloys | $4.0 \times 10^{-4}$ to $5.0 \times 10^{-4}$ |

### 46.6 Combined Thermal Effect on Preload

Including both differential expansion and modulus degradation:

$$F(T) = F_0 + \Delta F_{thermal} \cdot \frac{E(T)}{E_0}$$

$$F(T) = F_0 + k_{sys} \cdot L_{grip} \cdot \Delta T \cdot (\alpha_m - \alpha_b) \cdot \left[1 - \beta_E \cdot (T - T_0)\right]$$

### 46.7 Thermal Cycling

For joints subject to repeated heating and cooling, the preload may exhibit a ratcheting effect. Each thermal cycle introduces a small permanent plastic deformation at contact surfaces (thermal embedding), leading to a progressive decrease:

$$F(N_{thermal}) = F_0 - N_{thermal} \cdot \delta_{thermal} \cdot k_{sys}$$

where $\delta_{thermal}$ is the plastic deformation per thermal cycle and $N_{thermal}$ is the number of thermal cycles.

### 46.8 Numerical Example

For an M16 Grade 8.8 bolt clamping an aluminum housing:
- $F_0 = 50{,}000$ N
- $k_b = 5 \times 10^5$ N/mm, $k_m = 8 \times 10^5$ N/mm
- $L_{grip} = 40$ mm
- $\alpha_b = 12 \times 10^{-6}$ K$^{-1}$, $\alpha_m = 23 \times 10^{-6}$ K$^{-1}$
- $\Delta T = +80$ C

$$k_{sys} = \frac{5 \times 10^5 \times 8 \times 10^5}{5 \times 10^5 + 8 \times 10^5} = 3.077 \times 10^5\ \text{N/mm}$$

$$\Delta F_{thermal} = 3.077 \times 10^5 \times 40 \times 80 \times (23 - 12) \times 10^{-6} = 10{,}830\ \text{N}$$

The preload **increases** by 10,830 N (21.7% of $F_0$) because the aluminum members expand more than the steel bolt, effectively stretching the bolt further.

### 46.9 When to Use

- Any joint with dissimilar materials (e.g., steel bolts in aluminum housings).
- Joints subject to significant temperature changes ($\Delta T > 30$ C).
- Process equipment, engine components, and subsea systems with temperature cycling.

### 46.10 References

- VDI 2230 Part 1 (2015). Section 5.4.2: "Thermally Induced Changes in Preload."
- Bickford, J. H. (2008). *Introduction to the Design and Behavior of Bolted Joints*, 4th ed., Chapter 11: "Thermally Induced Problems."
- Schneider, R. (2003). "Thermal effects on bolted joints." *Journal of Pressure Vessel Technology*, 125(4), 388-394. DOI: [10.1115/1.1613949](https://doi.org/10.1115/1.1613949)

---

## 47. Power-Law Model (Lu et al., 2024)

### 47.1 Motivation

Many experimental preload decay datasets can be fit with high accuracy using only two parameters. The power-law model achieves this by exploiting the scale-invariant nature of the decay process: the fractional loss rate $\frac{1}{F}\frac{dF}{dN}$ depends only on the current cycle count $N$, not on the absolute preload level.

### 47.2 Formulation

$$F(N) = F_0 \cdot \left(1 + \frac{N}{N_c}\right)^{-\alpha}$$

where:
- $\alpha$ = power-law exponent (dimensionless), $\alpha > 0$
- $N_c$ = critical (characteristic) cycle number

### 47.3 Normalized Form

$$\frac{F(N)}{F_0} = \left(1 + \frac{N}{N_c}\right)^{-\alpha}$$

### 47.4 Rate of Loss

$$\frac{dF}{dN} = -\frac{\alpha \cdot F_0}{N_c} \cdot \left(1 + \frac{N}{N_c}\right)^{-\alpha - 1}$$

The initial loss rate at $N = 0$:

$$\left.\frac{dF}{dN}\right|_{N=0} = -\frac{\alpha \cdot F_0}{N_c}$$

### 47.5 Characteristic Behavior

For large $N$ ($N \gg N_c$), the preload decays as a pure power law:

$$F(N) \approx F_0 \cdot \left(\frac{N_c}{N}\right)^{\alpha}\ ,\quad N \gg N_c$$

This is slower than exponential decay but never reaches zero (the model predicts $F \to 0$ only as $N \to \infty$). This "heavy tail" behavior is more physically realistic than exponential models for many joints.

### 47.6 Parameter Ranges

| Parameter | Symbol | Typical Range | Effect |
|-----------|--------|---------------|--------|
| Exponent | $\alpha$ | 0.05 - 0.50 | Higher $\alpha$ = faster decay |
| Critical cycles | $N_c$ | 1 - 100 | Lower $N_c$ = more rapid initial decay |

### 47.7 Fitting Accuracy

Lu et al. (2024) demonstrated that the power-law model achieves fitting accuracy exceeding 85.5% (measured by $R^2$) across 22 different experimental datasets from the literature, despite using only two parameters. This makes it one of the most parsimonious models available.

### 47.8 Relationship to Other Models

For small $\alpha$ and large $N_c$, a Taylor expansion gives:

$$\left(1 + \frac{N}{N_c}\right)^{-\alpha} \approx \exp\!\left(-\frac{\alpha N}{N_c}\right)$$

with $\lambda = \alpha / N_c$, recovering the single exponential model. The power law can therefore be viewed as a generalization of the exponential with a variable (decreasing) decay rate.

### 47.9 When to Use

- Rapid initial fitting with minimal parameters.
- Comparison baseline when evaluating more complex models.
- When experimental data are limited (only a few data points) and overfitting must be avoided.
- Studies that compare across many different bolt sizes and preload levels.

### 47.10 References

- Lu, Y., Ding, L., Li, J., and Wang, Z. (2024). "A power-law model for bolt preload relaxation and self-loosening prediction." *Sensors*, 24(3), 892. DOI: [10.3390/s24030892](https://doi.org/10.3390/s24030892)
- Goodier, J. N. (1945). "Loosening by vibration of threaded fastenings." *Mechanical Engineering*, 67, 798-802.

---

## 48. Logarithmic Model

### 48.1 Formulation

The logarithmic model describes preload decay as proportional to the logarithm of cycle count:

$$F(N) = F_0 - k \cdot \ln(N + 1)$$

where:
- $k$ = logarithmic decay coefficient [N]
- The $(N + 1)$ term ensures $F(0) = F_0$

### 48.2 Rate of Loss

$$\frac{dF}{dN} = -\frac{k}{N + 1}$$

The rate decreases monotonically with $N$, which is consistent with embedding-dominated behavior where the rate of asperity crushing slows as the contact area increases.

### 48.3 Physical Basis

The logarithmic model arises naturally from a process where the incremental deformation per cycle is inversely proportional to the number of past cycles:

$$\delta_N = \frac{k}{k_{sys} \cdot (N + 1)}$$

This behavior is typical of:
- Work-hardening of asperity contacts (Hertzian contact theory predicts log-time creep).
- Surface conformity increasing with load history.
- Embedment rate slowing as the real contact area approaches the nominal contact area.

### 48.4 Parameter Ranges

| Parameter | Symbol | Typical Range | Units |
|-----------|--------|---------------|-------|
| Decay coefficient | $k$ | 1000 - 5000 | N |

For an M16 bolt with $F_0 = 50{,}000$ N:
- $k \approx 2{,}000$ N: After 1000 cycles, $\Delta F = 2000 \cdot \ln(1001) \approx 13{,}820$ N (27.6% loss).
- $k \approx 1{,}000$ N: After 1000 cycles, $\Delta F \approx 6{,}910$ N (13.8% loss).

### 48.5 Critical Warning: Negative Preload

The logarithmic model predicts $F = 0$ when:

$$N^* = \exp\!\left(\frac{F_0}{k}\right) - 1$$

Beyond $N^*$, the model predicts negative preload, which is physically meaningless. The model must therefore be truncated:

$$F(N) = \max\!\left(F_0 - k \cdot \ln(N + 1),\ 0\right)$$

For $F_0 = 50{,}000$ N and $k = 2{,}000$ N:

$$N^* = \exp(25) - 1 \approx 7.2 \times 10^{10}$$

In practice, this is an extremely large number and unlikely to be reached. However, for smaller $F_0/k$ ratios, the issue becomes relevant.

### 48.6 When to Use

- Early-stage predictions (first 100-500 cycles) where embedding dominates.
- Quick estimates when only limited data are available.
- As a component within combined models (Section 51).

### 48.7 Limitations

1. **No asymptotic floor**: The model does not converge to a residual preload.
2. **Unbounded at large $N$**: Predicts eventual zero preload (and negative if unclamped).
3. **Single mechanism only**: Best suited to embedding-dominated scenarios.
4. **Poor extrapolation**: Should not be used beyond the fitted data range.

### 48.8 References

- Bickford, J. H. (2008). *Introduction to the Design and Behavior of Bolted Joints*, 4th ed. CRC Press. Chapter 11.
- Nassar, S. A., and Matin, P. H. (2006). "Clamp load loss due to fastener relaxation and creep." *Journal of Pressure Vessel Technology*, 128(3), 394-400. DOI: [10.1115/1.2218343](https://doi.org/10.1115/1.2218343)

---

## 49. Jiang Two-Stage Model (Jiang et al., 2003-2004)

### 49.1 Historical Significance

The two-stage model proposed by Jiang, Zhang, Jiang, Waterhouse, and Fry (2003, 2004) represents a landmark in the understanding of bolt self-loosening. Through careful experiments with transverse vibration (Junker-type) tests and finite element analysis, they demonstrated that loosening proceeds through two fundamentally different stages, each governed by distinct physical mechanisms.

### 49.2 Stage I: Material Loosening (Non-Rotational)

**Cycle range**: $0 \leq N \leq N_{trans}$

**Physical mechanism**: During the initial cycles of transverse loading, the contact pressure distribution at the thread roots and bearing surfaces undergoes redistribution. Localized cyclic plastic deformation occurs at stress concentration regions (thread roots, under-head fillet, first engaged thread). This microplastic strain accumulation leads to a progressive reduction in clamping force without any measurable rotation of the nut.

**Mathematical model**:

$$F(N) = F_0 - \Delta F_{embed} \cdot \left[1 - \exp\!\left(-\frac{N}{N_1}\right)\right]$$

where:
- $\Delta F_{embed}$ = total preload loss during Stage I [N]
- $N_1$ = Stage I time constant [cycles]

**Key observations**:
- No measurable nut rotation ($\theta < 0.5^\circ$).
- The preload loss rate decreases monotonically (saturating behavior).
- The mechanism is essentially irreversible plastic settling.
- Typical $\Delta F_{embed} / F_0$ = 0.05 to 0.40 (5% to 40% of initial preload).
- Higher surface roughness leads to larger $\Delta F_{embed}$.

### 49.3 Stage II: Structural Loosening (Rotational)

**Cycle range**: $N > N_{trans}$

**Physical mechanism**: After the contact surfaces have settled, continued transverse loading causes progressive nut rotation (back-off). The Junker mechanism activates: transverse slip at the bearing surface momentarily reduces thread friction, and the pitch torque drives the nut in the loosening direction. The nut rotation accumulates cycle by cycle, and the preload decreases approximately linearly with cycle count.

**Mathematical model**:

$$F(N) = F_{trans} - k_2 \cdot (N - N_{trans})$$

where:
- $F_{trans}$ = preload at the Stage I-II transition [N]
- $k_2$ = linear decay rate [N/cycle]

The transition preload is obtained from the Stage I equation evaluated at $N = N_{trans}$:

$$F_{trans} = F_0 - \Delta F_{embed} \cdot \left[1 - \exp\!\left(-\frac{N_{trans}}{N_1}\right)\right]$$

### 49.4 Transition Criterion

Jiang et al. identified that the transition from Stage I to Stage II occurs when the accumulated nut rotation reaches approximately $0.5^\circ$:

$$\theta_{trans} \approx 0.5^\circ$$

Equivalently, the transition occurs when the preload has dropped enough that the loosening torque (pitch torque) exceeds the total resisting torque (thread + bearing friction) with the accumulated plastic strain redistribution. Typical transition preload:

$$F_{trans} / F_0 \approx 0.60 - 0.95$$

The wide range reflects the dependence on friction coefficient, surface roughness, and transverse displacement amplitude.

### 49.5 Complete Piecewise Model

$$F(N) = \begin{cases} F_0 - \Delta F_{embed} \cdot \left[1 - \exp\!\left(-\dfrac{N}{N_1}\right)\right] & 0 \leq N \leq N_{trans} \\[8pt] F_{trans} - k_2 \cdot (N - N_{trans}) & N > N_{trans} \end{cases}$$

### 49.6 Rate of Loss

$$\frac{dF}{dN} = \begin{cases} -\dfrac{\Delta F_{embed}}{N_1} \cdot \exp\!\left(-\dfrac{N}{N_1}\right) & 0 \leq N \leq N_{trans} \\[8pt] -k_2 & N > N_{trans} \end{cases}$$

### 49.7 Graphical Behavior

```
   F/F0
   1.0 ┬───╮
       │    ╲
       │     ╲
       │      ╲       STAGE I
   0.9 ┤       ╲      Material loosening
       │        ╲     (exponential saturation)
       │         ╲╲
       │           ╲╲╲
   0.8 ┤              ╲╲╲╲╲╲─────────── F_trans
       │                     ╲
       │                      ╲
       │                       ╲     STAGE II
   0.7 ┤                        ╲    Structural loosening
       │                         ╲   (linear decay)
       │                          ╲
       │                           ╲
   0.6 ┤                            ╲
       │                             ╲
       │                              ╲
       └──────┬─────────┬──────┬──────┬──────┬──────┬──────
              0       N_trans       1000        2000
                              Cycles N
```

### 49.8 Parameter Ranges

| Parameter | Symbol | Typical Range | Physical Meaning |
|-----------|--------|---------------|------------------|
| Transition cycles | $N_{trans}$ | 100 - 1000 | Duration of Stage I |
| Stage I loss ratio | $\Delta F_{embed} / F_0$ | 0.05 - 0.40 | Fraction lost to settling |
| Stage I time constant | $N_1$ | 20 - 200 cycles | Speed of Stage I settling |
| Stage II linear rate | $k_2$ | 1 - 50 N/cycle | Rotational loosening speed |

### 49.9 Factors Affecting Parameters

| Factor | Effect on $\Delta F_{embed}$ | Effect on $k_2$ |
|:---|:---:|:---:|
| Higher surface roughness | Increases | Minor effect |
| Higher preload $F_0$ | Increases (absolute) | Decreases (higher friction) |
| Higher transverse amplitude | Minor effect | Increases strongly |
| Lower friction $\mu$ | Minor effect | Increases strongly |
| Larger pitch $p$ | Minor effect | Increases (more rotation per slip) |

### 49.10 When to Use

- Standard model for Junker-type transverse vibration analysis.
- When both embedding and rotational loosening are expected.
- For design checks per VDI 2230 methodology.
- First-choice model in Bolt Analysis Studio.

### 49.11 References

- Jiang, Y., Zhang, M., and Lee, C.-H. (2003). "A study of early-stage self-loosening of bolted joints." *ASME Journal of Mechanical Design*, 125(3), 518-526. DOI: [10.1115/1.1586936](https://doi.org/10.1115/1.1586936)
- Jiang, Y., Zhang, M., Park, T.-W., and Lee, C.-H. (2004). "An experimental study of self-loosening of bolted joints." *ASME Journal of Mechanical Design*, 126(5), 925-931. DOI: [10.1115/1.1767814](https://doi.org/10.1115/1.1767814)
- Junker, G. (1969). "New criteria for self-loosening of fasteners under vibration." *SAE Technical Paper*, 690055. DOI: [10.4271/690055](https://doi.org/10.4271/690055)

---

## 50. Jiang Three-Stage Extended Model (Gong et al., 2019)

### 50.1 Motivation

While the Jiang two-stage model captures the behavior up to moderate cycle counts, long-duration experiments reveal a third stage at high cycle counts where the preload decay accelerates. Gong, Liu, and Ding (2019) extended the model to three stages, adding a fatigue-driven acceleration regime that better predicts joint failure.

### 50.2 Stage I: Rapid Non-Linear (Plastic Settling)

Identical to the two-stage model:

$$F(N) = F_0 - \Delta F_1 \cdot \left[1 - \exp\!\left(-\frac{N}{N_1}\right)\right]\ , \quad 0 \leq N \leq N_{12}$$

### 50.3 Stage II: Linear Steady (Rotational Back-Off)

Identical to the two-stage model:

$$F(N) = F_{12} - k_2 \cdot (N - N_{12})\ , \quad N_{12} < N \leq N_{23}$$

where $F_{12}$ is the preload at the Stage I-II transition.

### 50.4 Stage III: Accelerating Fatigue Degradation

**Cycle range**: $N > N_{23}$

**Physical mechanism**: At very high cycle counts, fatigue cracks initiate at thread roots and under-head fillets. These cracks reduce the effective cross-sectional area of the bolt, decreasing stiffness and accelerating preload loss. Additionally, fretting damage at contact surfaces may cause debris generation and further loss of contact compliance.

**Mathematical model**:

$$F(N) = F_{23} - k_3 \cdot (N - N_{23})^{n_3}$$

where:
- $F_{23}$ = preload at the Stage II-III transition [N]
- $k_3$ = Stage III base rate coefficient [N/cycle$^{n_3}$]
- $n_3$ = acceleration exponent, $n_3 > 1$ (typically 1.3 to 2.0)

The transition preloads are:

$$F_{12} = F_0 - \Delta F_1 \cdot \left[1 - \exp\!\left(-\frac{N_{12}}{N_1}\right)\right]$$

$$F_{23} = F_{12} - k_2 \cdot (N_{23} - N_{12})$$

### 50.5 Complete Piecewise Model

$$F(N) = \begin{cases} F_0 - \Delta F_1 \cdot \left[1 - \exp\!\left(-\dfrac{N}{N_1}\right)\right] & 0 \leq N \leq N_{12} \\[8pt] F_{12} - k_2 \cdot (N - N_{12}) & N_{12} < N \leq N_{23} \\[8pt] F_{23} - k_3 \cdot (N - N_{23})^{n_3} & N > N_{23} \end{cases}$$

### 50.6 Rate of Loss

$$\frac{dF}{dN} = \begin{cases} -\dfrac{\Delta F_1}{N_1} \cdot \exp\!\left(-\dfrac{N}{N_1}\right) & \text{Stage I} \\[8pt] -k_2 & \text{Stage II} \\[8pt] -k_3 \cdot n_3 \cdot (N - N_{23})^{n_3 - 1} & \text{Stage III} \end{cases}$$

Note that in Stage III, the rate **increases** with $N$ (since $n_3 > 1$), representing the acceleration due to fatigue damage accumulation.

### 50.7 Graphical Behavior

```
   F/F0
   1.0 ┬──╮
       │   ╲         STAGE I
       │    ╲        (exponential)
   0.9 ┤     ╲╲
       │       ╲╲╲
       │          ╲╲╲────── F_12
   0.8 ┤                ╲
       │                 ╲        STAGE II
       │                  ╲       (linear)
   0.7 ┤                   ╲
       │                    ╲
       │                     ╲──── F_23
   0.6 ┤                      ╲
       │                       ╲╲       STAGE III
       │                         ╲╲╲    (accelerating)
   0.5 ┤                            ╲╲╲╲
       │                                ╲╲╲╲╲╲
       │                                      ╲╲╲╲╲╲╲╲
   0.4 ┤                                              ╲╲╲╲╲
       │                                                    ╲╲╲
       └──────┬──────┬──────┬──────┬──────┬──────┬──────┬──────
              0    N_12          N_23                    N_failure
                              Cycles N
```

### 50.8 Parameter Ranges

| Parameter | Symbol | Typical Range | Units |
|-----------|--------|---------------|-------|
| Stage I-II transition | $N_{12}$ | 100 - 1000 | cycles |
| Stage II-III transition | $N_{23}$ | 10,000 - 100,000 | cycles |
| Stage I loss ratio | $\Delta F_1 / F_0$ | 0.05 - 0.20 | -- |
| Stage I time constant | $N_1$ | 20 - 200 | cycles |
| Stage II rate | $k_2$ | 1 - 20 | N/cycle |
| Stage III base rate | $k_3$ | 0.01 - 5.0 | N/cycle$^{n_3}$ |
| Stage III exponent | $n_3$ | 1.3 - 2.0 | -- |

### 50.9 Stage Identification from Experimental Data

Gong et al. recommend the following procedure to identify stage transitions:
1. Plot cumulative nut rotation $\theta(N)$ versus cycle count.
2. Stage I: $\theta < 0.5^\circ$ (no measurable rotation).
3. Stage I-II transition: onset of steady rotation.
4. Stage II: approximately constant $d\theta/dN$.
5. Stage II-III transition: acceleration of rotation rate.
6. Stage III: increasing $d\theta/dN$ and/or visible fatigue indicators.

### 50.10 When to Use

- Long-duration Junker tests or operational life prediction.
- When fatigue life interaction with loosening is important.
- For safety-critical joints where Stage III onset defines the replacement interval.

### 50.11 References

- Gong, H., Liu, J., and Ding, X. (2019). "Study on the mechanism of preload decrease for bolted joints subjected to transversal vibration loading." *Proceedings of the Institution of Mechanical Engineers, Part C: Journal of Mechanical Engineering Science*, 233(15), 5503-5515. DOI: [10.1177/0954406218802928](https://doi.org/10.1177/0954406218802928)
- Yang, G., Hong, J., Zhu, L., Li, B., and Xiong, M. (2021). "Three-stage loosening model and remaining life prediction of bolted joints under transverse loading." *Engineering Failure Analysis*, 128, 105588. DOI: [10.1016/j.engfailanal.2021.105588](https://doi.org/10.1016/j.engfailanal.2021.105588)

---

## 51. Combined Mechanism Model

### 51.1 Rationale

In reality, multiple loss mechanisms operate simultaneously. Embedding occurs during the first hundred cycles while creep proceeds over hours and thermal effects respond to temperature changes. Rather than selecting a single model, the combined mechanism model superimposes all relevant contributions, each modeled independently.

### 51.2 Superposition Formulation

$$\Delta F_{total}(N) = \Delta F_{embedding}(N) + \Delta F_{creep}(t) + \Delta F_{cyclic}(N) + \Delta F_{thermal}(\Delta T)$$

The total preload is:

$$F_p(N) = \max\!\left(F_0 - \Delta F_{total}(N),\ F_{residual}\right)$$

where $F_{residual}$ is a physically motivated floor (typically 50-60% of $F_0$, below which the bolt loses function).

### 51.3 Component Expressions

**Embedding (saturating)**:

$$\Delta F_{embedding}(N) = \Delta F_{embed,max} \cdot \left[1 - \exp\!\left(-\frac{N}{\tau_{embed}}\right)\right]$$

**Cyclic plastic deformation (double exponential)**:

$$\Delta F_{cyclic}(N) = A_1 \cdot \left[1 - \exp(-\lambda_1 N)\right] + A_2 \cdot \left[1 - \exp(-\lambda_2 N)\right]$$

**Creep / stress relaxation (time-dependent)**:

$$\Delta F_{creep}(t) = F_0 \cdot \left[1 - \left(1 + (n-1) \cdot B \cdot \sigma_0^{n-1} \cdot t\right)^{-\frac{1}{n-1}}\right]$$

where $B = A \cdot E \cdot \exp(-Q/RT)$ and $t = N/f$.

**Thermal (constant for given temperature)**:

$$\Delta F_{thermal} = k_{sys} \cdot L_{grip} \cdot \Delta T \cdot (\alpha_m - \alpha_b)$$

**Structural loosening (after transition)**:

$$\Delta F_{structural}(N) = \begin{cases} 0 & N \leq N_{struct} \\ k_{struct} \cdot (N - N_{struct}) & N > N_{struct} \end{cases}$$

### 51.4 Combined Model Total

$$F(N) = F_0 - \Delta F_{embedding}(N) - \Delta F_{cyclic}(N) - \Delta F_{creep}(N/f) - \Delta F_{thermal} - \Delta F_{structural}(N)$$

### 51.5 Loss Breakdown Diagnostic

A valuable feature of the combined model is the ability to decompose the total loss into individual contributions at any cycle count:

| Mechanism | $N = 10$ | $N = 100$ | $N = 1{,}000$ | $N = 10{,}000$ |
|:---|:---:|:---:|:---:|:---:|
| Embedding | Dominant | Saturated | Saturated | Saturated |
| Cyclic fast | Active | Saturated | Saturated | Saturated |
| Cyclic slow | Negligible | Active | Dominant | Saturated |
| Creep | Negligible | Negligible | Active | Dominant |
| Thermal | Constant | Constant | Constant | Constant |
| Structural | Inactive | Inactive | Possible | Active |

### 51.6 Parameter Summary

The combined model requires specification of parameters from each sub-mechanism. Typical total parameter count: 8-12.

### 51.7 When to Use

- Comprehensive design analysis where all mechanisms must be accounted for.
- Sensitivity studies to determine which mechanism dominates for a given joint configuration.
- Validation studies comparing model predictions with full-duration experimental data.
- The recommended model in Bolt Analysis Studio for production analysis.

### 51.8 References

- VDI 2230 Part 1 (2015). "Systematic Calculation of Highly Stressed Bolted Joints."
- Bickford, J. H. (2008). *Introduction to the Design and Behavior of Bolted Joints*, 4th ed. CRC Press.
- ASME PCC-1 (2013). "Guidelines for Pressure Boundary Bolted Flange Joint Assembly."

---

## 52. D-N Loosening Curve (Displacement-Life)

### 52.1 Concept

The Displacement-Life (D-N) curve is the loosening analogue of the classical S-N (Stress-Life) fatigue curve. It plots the number of cycles to loosening $N_f$ as a function of the transverse displacement amplitude $\delta$. Just as the S-N curve defines a fatigue endurance limit, the D-N curve defines a threshold displacement below which loosening does not occur (infinite life).

### 52.2 Bilinear D-N Curve in Log-Log Coordinates

In log-log space, the D-N curve is typically bilinear:

**High-cycle region** (small amplitudes, $\delta_{threshold} < \delta \leq \delta_{transition}$):

$$\log_{10}(N_f) = C_1 - m_1 \cdot \log_{10}(\delta)$$

Equivalently:

$$N_f = 10^{C_1} \cdot \delta^{-m_1}$$

**Low-cycle region** (large amplitudes, $\delta > \delta_{transition}$):

$$\log_{10}(N_f) = C_2 - m_2 \cdot \log_{10}(\delta)$$

Equivalently:

$$N_f = 10^{C_2} \cdot \delta^{-m_2}$$

### 52.3 Endurance Limit (Threshold Displacement)

Below a critical displacement amplitude $\delta_{threshold}$, the transverse slip is insufficient to overcome the combined thread and bearing friction. The bolt has infinite loosening life:

$$\delta < \delta_{threshold} \implies N_f = \infty$$

The threshold displacement depends on the friction coefficient and preload:

$$\delta_{threshold} \propto \frac{\mu \cdot F_p}{k_{trans}}$$

Typical values: $\delta_{threshold} \approx 0.05 - 0.20$ mm for standard M12-M24 bolts with $\mu \approx 0.10 - 0.15$.

### 52.4 Typical D-N Curve Parameters

| Parameter | Symbol | Typical Value | Units |
|-----------|--------|:---:|:---|
| High-cycle constant | $C_1$ | 4.5 - 6.0 | -- |
| High-cycle slope | $m_1$ | 2.5 - 4.0 | -- |
| Low-cycle constant | $C_2$ | 3.5 - 5.0 | -- |
| Low-cycle slope | $m_2$ | 1.0 - 2.0 | -- |
| Transition amplitude | $\delta_{transition}$ | 0.3 - 0.8 | mm |
| Threshold amplitude | $\delta_{threshold}$ | 0.05 - 0.20 | mm |

### 52.5 Graphical Representation

```
   log(N_f)
     6 ┬─────────────────────────────────────────────
       │
       │                    ╲  High-cycle region
       │                     ╲  (slope = -m1)
     5 ┤                      ╲
       │                       ╲
       │                        ╲
       │                         ╲
     4 ┤                          ╲╲
       │                            ╲╲  Transition
       │                              ╲╲
       │                                ╲  Low-cycle region
     3 ┤                                 ╲  (slope = -m2)
       │                                  ╲
       │                                   ╲
       │                                    ╲
     2 ┤                                     ╲
       │         ▲                            ╲
       │         │ δ_threshold
       │         │ (endurance limit)
     1 ┤─────────┤
       │
       └────┬────┬────┬────┬────┬────┬────┬────┬────
          -1.5 -1.2 -0.9 -0.6 -0.3  0.0  0.3  0.6
                         log(δ) [mm]
```

### 52.6 Inverse Problem: Critical Displacement for Target Life

Given a target life $N_{target}$, the maximum allowable displacement amplitude is:

$$\delta_{max} = \begin{cases} 10^{(C_1 - \log_{10} N_{target})/m_1} & \text{if } \delta_{max} \leq \delta_{transition} \\[6pt] 10^{(C_2 - \log_{10} N_{target})/m_2} & \text{if } \delta_{max} > \delta_{transition} \end{cases}$$

### 52.7 Dependence on Joint Parameters

The D-N curve shifts depending on:
- **Preload level**: Higher $F_0$ shifts the curve to the right (more displacement tolerated).
- **Friction coefficient**: Higher $\mu$ shifts the curve to the right.
- **Bolt size**: Larger bolts have higher threshold displacements.
- **Thread pitch**: Coarser pitch shifts the curve to the left (easier loosening per unit rotation).

### 52.8 When to Use

- Life prediction for joints under known transverse vibration amplitudes.
- Specification of maximum allowable vibration amplitude for a target service life.
- Input to Miner's rule for variable amplitude loading (Section 53).

### 52.9 References

- Junker, G. (1969). "New criteria for self-loosening of fasteners under vibration." *SAE Technical Paper*, 690055.
- Hess, D. P. (1998). "Vibration- and shock-induced loosening." In *Handbook of Bolts and Bolted Joints*, ed. Bickford, J. H., and Nassar, S., Marcel Dekker. pp. 757-824.
- Nassar, S. A., and Housari, B. A. (2005). "Effect of thread pitch and initial tension on the self-loosening of threaded fasteners." *ASME Journal of Pressure Vessel Technology*, 127(2), 162-166. DOI: [10.1115/1.1903787](https://doi.org/10.1115/1.1903787)

---

## 53. Miner's Rule Damage Accumulation

### 53.1 Background

Service loading is rarely constant-amplitude. Bolted joints in rotating equipment, piping systems, and vehicle structures experience a spectrum of vibration amplitudes. Miner's rule (Palmgren-Miner linear damage hypothesis) provides a method to assess loosening life under variable amplitude loading by summing fractional damages from each loading block.

### 53.2 Damage Index

The Palmgren-Miner damage index is:

$$D = \sum_{i=1}^{k} \frac{n_i}{N_i}$$

where:
- $k$ = number of loading blocks
- $n_i$ = number of cycles applied at displacement amplitude $\delta_i$
- $N_i$ = cycles to loosening at amplitude $\delta_i$ (from the D-N curve)

### 53.3 Failure Criterion

Loosening is predicted to occur when:

$$D \geq D_{cr}$$

The classical Miner's rule uses $D_{cr} = 1.0$. However, experimental evidence for bolted joint loosening shows:

| Loading Sequence | Observed $D_{cr}$ | Interpretation |
|:---|:---:|:---|
| High-to-low (H-L) | 0.7 - 1.0 | Conservative; damage from high amplitude "pre-conditions" the joint |
| Low-to-high (L-H) | 1.0 - 1.5 | Non-conservative; low amplitude cycles may cause beneficial work-hardening |
| Random | 0.8 - 1.2 | Approximately Miner's rule |

### 53.4 Block Loading Example

Consider a joint with the following loading history:

| Block | Amplitude $\delta_i$ [mm] | Cycles $n_i$ | $N_i$ (from D-N curve) | Damage $n_i / N_i$ |
|:---:|:---:|:---:|:---:|:---:|
| 1 | 0.8 | 500 | 2,000 | 0.250 |
| 2 | 0.4 | 5,000 | 50,000 | 0.100 |
| 3 | 0.6 | 2,000 | 8,000 | 0.250 |
| 4 | 0.3 | 20,000 | 200,000 | 0.100 |
| **Total** | | | | **0.700** |

Since $D = 0.70 < 1.0$, loosening is not predicted to have occurred after this loading history.

### 53.5 Remaining Life Calculation

After accumulating damage $D_{acc}$, the remaining life at a future constant amplitude $\delta_{future}$ is:

$$n_{remaining} = (D_{cr} - D_{acc}) \cdot N(\delta_{future})$$

For the example above, continuing at $\delta = 0.5$ mm ($N = 20{,}000$ cycles from D-N curve):

$$n_{remaining} = (1.0 - 0.70) \times 20{,}000 = 6{,}000\ \text{cycles}$$

### 53.6 Limitations of Miner's Rule

1. **Sequence independence**: Miner's rule assumes damage is independent of loading order. This is known to be incorrect for bolt loosening; high-to-low sequences are more damaging than low-to-high.
2. **No interaction effects**: The rule does not account for the fact that high-amplitude cycles may change the friction state or surface condition, affecting subsequent low-amplitude behavior.
3. **Below-threshold loading**: Cycles below the endurance limit contribute zero damage. In reality, they may still contribute if the effective threshold has been lowered by prior high-amplitude loading.
4. **Linear summation**: Damage accumulation in bolted joints may be nonlinear, especially when different mechanisms (embedding vs. rotation) are activated at different amplitudes.

### 53.7 Modified Miner's Rules

Several modifications have been proposed to address the limitations:

**Haibach correction** (for below-threshold contribution):

$$D = \sum_{i: \delta_i > \delta_{th}} \frac{n_i}{N_i} + \sum_{j: \delta_j \leq \delta_{th}} \frac{n_j}{N_j^*}$$

where $N_j^*$ is an extended D-N curve with reduced slope below the threshold.

**Nonlinear damage accumulation** (Marco-Starkey):

$$D = \sum_{i} \left(\frac{n_i}{N_i}\right)^{c_i}$$

where $c_i$ depends on the amplitude level (higher amplitude blocks have $c_i < 1$, increasing their relative damage contribution).

### 53.8 When to Use

- Variable amplitude service loading (vibration spectra from field measurements).
- Maintenance interval planning.
- Comparison of different anti-loosening strategies under realistic loading.

### 53.9 References

- Palmgren, A. (1924). "Die Lebensdauer von Kugellagern." *Zeitschrift des Vereines Deutscher Ingenieure*, 68(14), 339-341.
- Miner, M. A. (1945). "Cumulative damage in fatigue." *ASME Journal of Applied Mechanics*, 12(3), A159-A164.
- Haibach, E. (2006). *Betriebsfestigkeit: Verfahren und Daten zur Bauteilberechnung*. Springer.
- Marco, S. M., and Starkey, W. L. (1954). "A concept of fatigue damage." *ASME Transactions*, 76, 627-632.

---

## 54. Energy Dissipation Model

### 54.1 Physical Basis

Every cycle of relative motion between contact surfaces in a bolted joint dissipates energy through friction. This dissipated energy manifests as heat generation, surface damage, and material removal (wear). The energy dissipation model links the mechanical energy balance to preload loss through two pathways: (1) direct material removal (wear) that reduces clamping length, and (2) surface degradation that alters friction behavior.

### 54.2 Energy per Cycle

For a contact interface undergoing gross slip, the energy dissipated per cycle is the area enclosed by the hysteresis loop in the force-displacement diagram:

$$E_{cycle} = \oint F \cdot dx$$

For a rectangular hysteresis loop (Coulomb friction with constant normal force and full-slip):

$$E_{cycle} = 4 \cdot \mu \cdot F_n \cdot \delta$$

where:
- $\mu$ = friction coefficient
- $F_n$ = normal force (preload) [N]
- $\delta$ = displacement amplitude [m]

### 54.3 Cumulative Energy

After $N$ cycles:

$$E_{total}(N) = \sum_{i=1}^{N} E_{cycle,i}$$

If friction and preload are approximately constant:

$$E_{total} \approx 4 \cdot \mu \cdot F_n \cdot \delta \cdot N$$

### 54.4 Power-Law Energy Dissipation (Iwan Model)

For partial-slip contacts (microslip), the energy dissipation follows a power law in the force amplitude $F_{amp}$:

$$W_d \propto F_{amp}^{\beta}$$

where $\beta = \chi + 3$ and $\chi$ is the Iwan distribution exponent. For typical joints:

| Iwan exponent $\chi$ | $\beta$ | Contact Type |
|:---:|:---:|:---|
| -0.5 | 2.5 | Well-conforming surfaces |
| 0.0 | 3.0 | Standard machined surfaces |
| 0.5 | 3.5 | Rough or misaligned surfaces |

### 54.5 Energy-Based Wear (Fouvry Relation)

Fouvry et al. established that wear volume is proportional to cumulative dissipated energy:

$$V_{wear} = \alpha_w \cdot E_{total}$$

where $\alpha_w$ is the energy wear coefficient [mm$^3$/J].

Typical values:
| Contact Pair | $\alpha_w$ [mm$^3$/J] |
|:---|:---:|
| Steel-on-steel (dry) | $1 \times 10^{-7}$ to $5 \times 10^{-7}$ |
| Steel-on-steel (lubricated) | $1 \times 10^{-8}$ to $5 \times 10^{-8}$ |
| Steel-on-zinc plating | $5 \times 10^{-7}$ to $2 \times 10^{-6}$ |

### 54.6 Wear Depth and Preload Loss

The average wear depth over a contact area $A_c$ is:

$$h_{wear} = \frac{V_{wear}}{A_c}$$

The resulting preload loss:

$$\Delta F_{wear} = k_{sys} \cdot h_{wear} = k_{sys} \cdot \frac{\alpha_w \cdot E_{total}}{A_c}$$

Substituting the cumulative energy:

$$\Delta F_{wear}(N) = k_{sys} \cdot \frac{\alpha_w \cdot 4 \mu F_n \delta}{A_c} \cdot N = k_{wear} \cdot N$$

where $k_{wear}$ is a constant wear-induced preload loss rate [N/cycle].

### 54.7 Connection to Friction Models

The energy dissipation model provides a natural link between the preload loss models (this Part X) and the friction models (Part VII):

$$E_{diss} = \int_0^T F_f(v, z, \mu) \cdot v \, dt$$

where $F_f$ is the friction force from any of the models in Part VII (Coulomb, Stribeck, LuGre, etc.). The instantaneous friction force depends on the current state, which in turn depends on the cumulative energy dissipated. This creates a coupled system.

### 54.8 When to Use

- Fretting analysis where micro-slip dominates.
- Wear-life prediction for high-cycle applications.
- Coupling friction evolution with preload loss.
- Understanding the thermodynamics of the loosening process.

### 54.9 References

- Fouvry, S., Liskiewicz, T., Kapsa, P., Daloz, S., and Berthier, Y. (2003). "An energy description of wear mechanisms and its applications to oscillating sliding contacts." *Wear*, 255(1-6), 287-298. DOI: [10.1016/S0043-1648(03)00117-0](https://doi.org/10.1016/S0043-1648(03)00117-0)
- Iwan, W. D. (1966). "A distributed-element model for hysteresis and its steady-state dynamic response." *ASME Journal of Applied Mechanics*, 33(4), 893-900. DOI: [10.1115/1.3625199](https://doi.org/10.1115/1.3625199)
- Segalman, D. J. (2005). "A four-parameter Iwan model for lap-type joints." *ASME Journal of Applied Mechanics*, 72(5), 752-760. DOI: [10.1115/1.1989354](https://doi.org/10.1115/1.1989354)

---

## 55. Rotation Angle Tracking Model

### 55.1 Kinematic Relationship

The fundamental kinematic relationship between nut rotation and preload change in a bolted joint is governed by the thread helix geometry:

$$\Delta F = \frac{p}{2\pi} \cdot \theta \cdot k_{sys}$$

where:
- $p$ = thread pitch [mm]
- $\theta$ = cumulative nut rotation [rad]
- $k_{sys}$ = system stiffness [N/mm]

Equivalently, the preload at any rotation angle is:

$$F(\theta) = F_0 - \frac{p}{2\pi} \cdot \theta \cdot k_{sys}$$

### 55.2 Rotation-to-Preload Sensitivity

The preload loss per unit rotation is a constant for a given joint:

$$\frac{dF}{d\theta} = -\frac{p}{2\pi} \cdot k_{sys}$$

For an M16 bolt ($p = 2.0$ mm, $k_{sys} = 3.75 \times 10^5$ N/mm):

$$\frac{dF}{d\theta} = -\frac{2.0}{2\pi} \times 3.75 \times 10^5 = -1.19 \times 10^5\ \text{N/rad} = -2{,}083\ \text{N/deg}$$

A single degree of rotation costs approximately 2,083 N of preload.

### 55.3 Critical Rotation: Jiang Transition Angle

Jiang et al. identified that $\theta \approx 0.5^\circ$ of nut rotation marks the transition from Stage I (material loosening) to Stage II (structural loosening):

$$\theta_{trans} \approx 0.5^\circ \approx 8.73 \times 10^{-3}\ \text{rad}$$

The corresponding preload loss at transition:

$$\Delta F_{trans} = \frac{p}{2\pi} \cdot \theta_{trans} \cdot k_{sys}$$

For the M16 example:

$$\Delta F_{trans} = 1{,}042\ \text{N}\ (2.1\%\ \text{of}\ F_0 = 50{,}000\ \text{N})$$

This is a relatively small fraction of the total Stage I loss, confirming that most of the Stage I preload reduction is due to material deformation rather than rotation.

### 55.4 Rotation Rate Evolution

The nut rotation rate $d\theta/dN$ evolves through the loosening stages:

**Stage I**: Negligible rotation ($d\theta/dN \approx 0$)

**Stage I-II Transition**: Sigmoid ramp-up, modeled as:

$$\frac{d\theta}{dN} = \dot{\theta}_{max} \cdot \frac{1}{1 + \exp\!\left(-\frac{N - N_{trans}}{0.1 \cdot N_{trans}}\right)}$$

**Stage II**: Approximately constant rotation rate:

$$\frac{d\theta}{dN} \approx \dot{\theta}_{max}$$

Typical values: $\dot{\theta}_{max} \approx 0.005$ to $0.05$ deg/cycle.

**Stage III**: Accelerating rotation rate due to fatigue crack growth and reduced thread engagement.

### 55.5 Cumulative Rotation

The total nut rotation at cycle $N$ is:

$$\theta(N) = \int_0^N \frac{d\theta}{dN'} \, dN'$$

For the simplified two-stage model:

$$\theta(N) \approx \begin{cases} \theta_0 & N \leq N_{trans} \\[6pt] \theta_0 + \dot{\theta}_{max} \cdot (N - N_{trans}) & N > N_{trans} \end{cases}$$

where $\theta_0$ is the small accumulated rotation during Stage I.

### 55.6 Inverse Problem: Rotation from Preload Measurement

Given a measured preload $F_{meas}$, the equivalent rotation is:

$$\theta_{eq} = \frac{2\pi}{p} \cdot \frac{F_0 - F_{meas}}{k_{sys}}$$

This is useful for interpreting experimental data where rotation is not directly measured.

### 55.7 Experimental Measurement

Nut rotation can be measured using:
- **Scribe lines**: Mark alignment at assembly; measure angular misalignment after test.
- **Laser displacement sensors**: Non-contact measurement of nut face position.
- **Rotary encoders**: Direct measurement for instrumented test rigs.
- **Image correlation (DIC)**: Full-field measurement of nut surface rotation.

### 55.8 When to Use

- When rotation data are available from experiments.
- To convert between preload measurements and rotation observations.
- As a diagnostic tool to determine whether loosening is rotational or non-rotational.
- In the time integration solver to track cumulative rotation as a state variable.

### 55.9 References

- Jiang, Y., Zhang, M., and Lee, C.-H. (2003). "A study of early-stage self-loosening of bolted joints." *ASME Journal of Mechanical Design*, 125(3), 518-526. DOI: [10.1115/1.1586936](https://doi.org/10.1115/1.1586936)
- Nassar, S. A., and Housari, B. A. (2011). "Study of the effect of hole clearance on the self-loosening of threaded fasteners under repeated transverse loads." *ASME Journal of Mechanical Design*, 133(6), 061007. DOI: [10.1115/1.4004365](https://doi.org/10.1115/1.4004365)

---

## 56. Model Selection Guide

### 56.1 Comparative Summary

The following table summarizes all preload loss models available in Bolt Analysis Studio, their parameter counts, strengths, and recommended applications:

| # | Model | Parameters | Accuracy | Captures Stages? | Residual Floor? | Best Application |
|:---:|:---|:---:|:---:|:---:|:---:|:---|
| 1 | Single Exponential | 2 ($\lambda$, $r$) | Moderate | No | Yes | Quick estimate, single mechanism |
| 2 | Double Exponential | 4 ($\lambda_1$, $\lambda_2$, $A_1$, $r$) | Good | Implicit | Yes | Two visible decay regimes |
| 3 | Stretched Exponential (KWW) | 2 ($N_0$, $\beta$) | Good | No | No* | Heterogeneous joints, many interfaces |
| 4 | VDI 2230 Embedding | 2 ($f_Z$, $\tau$) | Good (Stage I) | Stage I only | Yes | Standards compliance, embedding |
| 5 | Norton-Bailey Creep | 4 ($A$, $n$, $Q$, $T$) | Good | N/A (time) | Decays to zero | Elevated temperature service |
| 6 | Thermal Effects | 3 ($\alpha_m$, $\alpha_b$, $\beta_E$) | Good | N/A | N/A (offset) | Dissimilar materials, $\Delta T > 30$ C |
| 7 | Power-Law (Lu 2024) | 2 ($\alpha$, $N_c$) | Good (>85%) | No | Asymptotic | Parsimonious fitting |
| 8 | Logarithmic | 1 ($k$) | Fair (limited) | No | No** | Early cycles only |
| 9 | Jiang Two-Stage | 4 ($N_{trans}$, $\Delta F$, $N_1$, $k_2$) | Very Good | Yes (I, II) | No | Junker test analysis |
| 10 | Jiang Three-Stage | 7 ($N_{12}$, $N_{23}$, $\Delta F_1$, $N_1$, $k_2$, $k_3$, $n_3$) | Excellent | Yes (I, II, III) | No | Long-term life prediction |
| 11 | Combined Mechanism | 8-12 | Excellent | Yes | Yes | Comprehensive design analysis |
| 12 | D-N Curve | 5 ($C_1$, $m_1$, $C_2$, $m_2$, $\delta_{th}$) | Good (life) | N/A | N/A | Life prediction |
| 13 | Miner's Rule | 1 ($D_{cr}$) | Fair-Good | N/A | N/A | Variable amplitude loading |
| 14 | Energy Dissipation | 3 ($\mu$, $\alpha_w$, $A_c$) | Good | N/A | N/A | Wear-dominated loosening |
| 15 | Rotation Tracking | 2 ($p$, $k_{sys}$) | Exact (kinematic) | Diagnostic | N/A | Rotation-preload conversion |

\* Modified KWW with residual floor parameter can be used.

\** Logarithmic model eventually predicts negative preload; must be truncated.

### 56.2 Decision Flowchart

```
                        START
                          │
                          ▼
              ┌───────────────────────┐
              │ Is temperature        │
              │ elevated (T > 0.4Tm)? │
              └───────────┬───────────┘
                     │          │
                    YES         NO
                     │          │
                     ▼          ▼
            ┌──────────┐  ┌───────────────────────┐
            │ Norton-   │  │ Is loading variable    │
            │ Bailey +  │  │ amplitude?             │
            │ Combined  │  └───────────┬────────────┘
            └──────────┘         │           │
                                YES          NO
                                 │           │
                                 ▼           ▼
                         ┌──────────┐  ┌───────────────────────┐
                         │ Miner's  │  │ Is transverse         │
                         │ Rule +   │  │ vibration present?    │
                         │ D-N Curve│  └───────────┬────────────┘
                         └──────────┘         │           │
                                             YES          NO
                                              │           │
                                              ▼           ▼
                                 ┌──────────────┐  ┌──────────────┐
                                 │ Jiang Two or  │  │ Is joint     │
                                 │ Three-Stage   │  │ complex      │
                                 │ Model         │  │ (many        │
                                 └──────────────┘  │ interfaces)? │
                                                   └──────┬───────┘
                                                     │         │
                                                    YES        NO
                                                     │         │
                                                     ▼         ▼
                                          ┌─────────────┐ ┌─────────────┐
                                          │ Stretched   │ │ Single or   │
                                          │ Exponential │ │ Double      │
                                          │ (KWW)       │ │ Exponential │
                                          └─────────────┘ └─────────────┘
```

### 56.3 Recommended Defaults in Bolt Analysis Studio

For users who are unsure which model to select, the following defaults are recommended:

| Application | Recommended Model | Justification |
|:---|:---|:---|
| **Quick screening** | Power-Law (Lu 2024) | Only 2 parameters, >85% accuracy |
| **Standard Junker test** | Jiang Two-Stage | Captures embedding + rotation, widely validated |
| **Long-duration prediction** | Jiang Three-Stage | Includes fatigue acceleration |
| **Elevated temperature** | Norton-Bailey + VDI 2230 | Creep + embedding |
| **Comprehensive design** | Combined Mechanism | All mechanisms superimposed |
| **Dissimilar materials** | Thermal Effects + Embedding | Dominant mechanisms for mixed-material joints |
| **Variable amplitude** | D-N Curve + Miner's Rule | Standard fatigue approach adapted for loosening |

### 56.4 Model Complexity vs. Data Requirements

```
   Accuracy
     │
     │                                          ╱ Jiang 3-Stage
     │                                        ╱
     │                                      ╱     Combined
     │                                    ╱
     │                             ╱────────── Jiang 2-Stage
     │                           ╱
     │                    ╱────────── Double Exponential
     │                  ╱
     │           ╱────────── Power-Law
     │         ╱
     │  ╱────────── Single Exponential
     │╱
     │── Logarithmic
     │
     └──────────────────────────────────────────────────
                                     Parameters (complexity)
       1     2     3     4     5     6     7     8-12
```

The general trade-off: more parameters yield higher accuracy but require more experimental data for reliable calibration. The power-law model represents an excellent compromise, achieving good accuracy with minimal parameters.

### 56.5 Validation Strategy

When applying any model, the following validation steps are recommended:

1. **Fit the model** to at least one experimental dataset from a representative joint.
2. **Check residuals**: Systematic patterns in residuals indicate model inadequacy.
3. **Cross-validate**: Fit to a subset of data and predict the remainder.
4. **Compare models**: Use the Akaike Information Criterion (AIC) or Bayesian Information Criterion (BIC) to compare models with different parameter counts.
5. **Physical plausibility**: Verify that fitted parameters lie within the expected physical ranges listed in this document.

---

## References

### Standards

1. VDI 2230 Part 1 (2015). "Systematic Calculation of Highly Stressed Bolted Joints --- Joints with One Cylindrical Bolt." *Verein Deutscher Ingenieure*, Dusseldorf, Germany.
2. ASME PCC-1 (2013). "Guidelines for Pressure Boundary Bolted Flange Joint Assembly." *American Society of Mechanical Engineers*, New York.

### Foundational Works

3. Junker, G. (1969). "New criteria for self-loosening of fasteners under vibration." *SAE Technical Paper*, 690055. DOI: [10.4271/690055](https://doi.org/10.4271/690055)
4. Goodier, J. N. (1945). "Loosening by vibration of threaded fastenings." *Mechanical Engineering*, 67, 798-802.
5. Bickford, J. H. (2008). *Introduction to the Design and Behavior of Bolted Joints*, 4th ed. CRC Press, Boca Raton, FL.

### Jiang Group (University of Nevada, Reno)

6. Jiang, Y., Zhang, M., and Lee, C.-H. (2003). "A study of early-stage self-loosening of bolted joints." *ASME Journal of Mechanical Design*, 125(3), 518-526. DOI: [10.1115/1.1586936](https://doi.org/10.1115/1.1586936)
7. Jiang, Y., Zhang, M., Park, T.-W., and Lee, C.-H. (2004). "An experimental study of self-loosening of bolted joints." *ASME Journal of Mechanical Design*, 126(5), 925-931. DOI: [10.1115/1.1767814](https://doi.org/10.1115/1.1767814)

### Nassar Group (Oakland University)

8. Nassar, S. A., and Housari, B. A. (2005). "Effect of thread pitch and initial tension on the self-loosening of threaded fasteners." *ASME Journal of Pressure Vessel Technology*, 127(2), 162-166. DOI: [10.1115/1.1903787](https://doi.org/10.1115/1.1903787)
9. Nassar, S. A., and Housari, B. A. (2007). "Study of the effect of hole clearance and thread fit on the self-loosening of threaded fasteners." *ASME Journal of Mechanical Design*, 129(6), 586-594. DOI: [10.1115/1.2717227](https://doi.org/10.1115/1.2717227)
10. Nassar, S. A., and Matin, P. H. (2006). "Clamp load loss due to fastener relaxation and creep." *Journal of Pressure Vessel Technology*, 128(3), 394-400. DOI: [10.1115/1.2218343](https://doi.org/10.1115/1.2218343)
11. Nassar, S. A., and Housari, B. A. (2011). "Study of the effect of hole clearance on the self-loosening of threaded fasteners under repeated transverse loads." *ASME Journal of Mechanical Design*, 133(6), 061007. DOI: [10.1115/1.4004365](https://doi.org/10.1115/1.4004365)

### Three-Stage and Extended Models

12. Gong, H., Liu, J., and Ding, X. (2019). "Study on the mechanism of preload decrease for bolted joints subjected to transversal vibration loading." *Proceedings of the Institution of Mechanical Engineers, Part C: Journal of Mechanical Engineering Science*, 233(15), 5503-5515. DOI: [10.1177/0954406218802928](https://doi.org/10.1177/0954406218802928)
13. Yang, G., Hong, J., Zhu, L., Li, B., and Xiong, M. (2021). "Three-stage loosening model and remaining life prediction of bolted joints under transverse loading." *Engineering Failure Analysis*, 128, 105588. DOI: [10.1016/j.engfailanal.2021.105588](https://doi.org/10.1016/j.engfailanal.2021.105588)

### Power-Law and Fitting Models

14. Lu, Y., Ding, L., Li, J., and Wang, Z. (2024). "A power-law model for bolt preload relaxation and self-loosening prediction." *Sensors*, 24(3), 892. DOI: [10.3390/s24030892](https://doi.org/10.3390/s24030892)

### Friction and Loosening

15. Li, Z., Chen, Y., Sun, W., Jiang, P., Pan, J., and Guan, Z. (2021). "Study on self-loosening mechanism of bolted joint under rotational vibration." *Tribology International*, 161, 107074. DOI: [10.1016/j.triboint.2021.107074](https://doi.org/10.1016/j.triboint.2021.107074)
16. Pai, N. G., and Hess, D. P. (2002). "Three-dimensional finite element analysis of threaded fastener loosening due to dynamic shear load." *Engineering Failure Analysis*, 9(4), 383-402. DOI: [10.1016/S1350-6307(01)00024-3](https://doi.org/10.1016/S1350-6307(01)00024-3)
17. Hess, D. P. (1998). "Vibration- and shock-induced loosening." In *Handbook of Bolts and Bolted Joints*, ed. Bickford, J. H., and Nassar, S., Marcel Dekker. pp. 757-824.
18. Liu, J., Ouyang, H., Peng, J., Zhang, C., Zhou, P., Ma, L., and Zhu, M. (2017). "Experimental and numerical studies of bolted joints subjected to axial excitation." *Tribology International*, 108, 12-20. DOI: [10.1016/j.triboint.2016.10.035](https://doi.org/10.1016/j.triboint.2016.10.035)

### Creep and Relaxation

19. Norton, F. H. (1929). *The Creep of Steel at High Temperatures*. McGraw-Hill, New York.
20. Bailey, R. W. (1935). "The utilization of creep test data in engineering design." *Proceedings of the Institution of Mechanical Engineers*, 131(1), 131-349. DOI: [10.1243/PIME_PROC_1935_131_012_02](https://doi.org/10.1243/PIME_PROC_1935_131_012_02)
21. Penny, R. K., and Marriott, D. L. (1995). *Design for Creep*, 2nd ed. Chapman & Hall, London.

### Stretched Exponential

22. Kohlrausch, R. (1854). "Theorie des elektrischen Ruckstandes in der Leidener Flasche." *Poggendorff's Annalen der Physik und Chemie*, 91, 179-214.
23. Williams, G., and Watts, D. C. (1970). "Non-symmetrical dielectric relaxation behavior arising from a simple empirical decay function." *Transactions of the Faraday Society*, 66, 80-85. DOI: [10.1039/TF9706600080](https://doi.org/10.1039/TF9706600080)
24. Phillips, J. C. (1996). "Stretched exponential relaxation in molecular and electronic glasses." *Reports on Progress in Physics*, 59(9), 1133-1207.

### Thermal Effects

25. Schneider, R. (2003). "Thermal effects on bolted joints." *Journal of Pressure Vessel Technology*, 125(4), 388-394. DOI: [10.1115/1.1613949](https://doi.org/10.1115/1.1613949)

### Energy Dissipation and Wear

26. Fouvry, S., Liskiewicz, T., Kapsa, P., Daloz, S., and Berthier, Y. (2003). "An energy description of wear mechanisms and its applications to oscillating sliding contacts." *Wear*, 255(1-6), 287-298. DOI: [10.1016/S0043-1648(03)00117-0](https://doi.org/10.1016/S0043-1648(03)00117-0)
27. Iwan, W. D. (1966). "A distributed-element model for hysteresis and its steady-state dynamic response." *ASME Journal of Applied Mechanics*, 33(4), 893-900. DOI: [10.1115/1.3625199](https://doi.org/10.1115/1.3625199)
28. Segalman, D. J. (2005). "A four-parameter Iwan model for lap-type joints." *ASME Journal of Applied Mechanics*, 72(5), 752-760. DOI: [10.1115/1.1989354](https://doi.org/10.1115/1.1989354)

### Damage Accumulation

29. Palmgren, A. (1924). "Die Lebensdauer von Kugellagern." *Zeitschrift des Vereines Deutscher Ingenieure*, 68(14), 339-341.
30. Miner, M. A. (1945). "Cumulative damage in fatigue." *ASME Journal of Applied Mechanics*, 12(3), A159-A164.
31. Haibach, E. (2006). *Betriebsfestigkeit: Verfahren und Daten zur Bauteilberechnung*. Springer, Berlin.
32. Marco, S. M., and Starkey, W. L. (1954). "A concept of fatigue damage." *ASME Transactions*, 76, 627-632.

---

**Document Information:**

| Field | Value |
|:---|:---|
| Part | X of XII (plus supplementary documents) |
| Title | Preload Loss Models |
| Sections | 40-56 |
| Models Covered | 15 |
| Version | 4.0 |
| Project | Bolt Analysis Studio --- Petrobras/LTAD-UFU R&D |
| Implementation File | `numerical/preload_loss_models.py` |

---

*LTAD/UFU - Tribology and Wear Technology Laboratory*
*Federal University of Uberlandia*
*Petrobras R&D Project*
