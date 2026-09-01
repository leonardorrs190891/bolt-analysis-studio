# MSD Framework - PART IX: SIMILITUDE AND SCALING ANALYSIS

**Complete Technical Reference for Bolt Analysis Studio**

**Version 4.0 - Extended English Edition**

**Authors:** L. Ribeiro, D. Carvalho, S.C. Naves, T. Santos, V. Marques, G. Arruda
**Institution:** LTAD/UFU - Tribology and Wear Technology Laboratory, Federal University of Uberlândia
**Project:** Petrobras R&D - Bolted Flange Joint Integrity

---

**Abstract.** Similitude analysis provides a rigorous mathematical framework for predicting the mechanical behavior of full-scale (prototype) bolted joints from experiments conducted on geometrically scaled models. This document develops the complete similitude theory for the MSD framework, starting from the Buckingham Pi theorem (Buckingham, 1914) and deriving the dimensionless groups that govern bolted joint self-loosening. Four types of similitude are defined -- geometric, kinematic, dynamic, and complete -- with complete similitude being the target for loosening analysis because friction plays a governing role. Scale factors are derived for all physical quantities (force, stress, stiffness, frequency, damping, energy, etc.) under three material similarity classifications: same material, similar material, and different material. Scale effects -- the deviations from ideal similitude that arise because certain physical phenomena do not scale linearly -- are quantified and classified by severity (Kuguel, 1961; Barenblatt, 2003). Correction factors are provided for surface roughness, thread geometry, grain size, residual stress, and lubrication film effects. A complete worked example demonstrates scaling from an M30 prototype to an M10 model, including scale effect assessment and corrected predictions. The similitude module implements `core/similitude/similitude.py` and `core/similitude/similitude_plots.py`.

---

## Table of Contents

- [36. Introduction to Similitude Analysis](#36-introduction-to-similitude-analysis)
- [37. Scale Factor Theory](#37-scale-factor-theory)
- [38. Dimensionless Pi-Groups](#38-dimensionless-pi-groups)
- [39. Scale Effects and Correction Factors](#39-scale-effects-and-correction-factors)
- [40. Practical Application Guidelines](#40-practical-application-guidelines)
- [41. Example: Scaling M30 Bolt to M10 Model](#41-example-scaling-m30-bolt-to-m10-model)
- [References](#references)

---

## 36. Introduction to Similitude Analysis

### 36.1 Purpose and Motivation

Similitude analysis provides a rigorous mathematical framework for predicting the mechanical behavior of a full-scale (prototype) bolted joint from experimental observations conducted on a geometrically scaled (model) specimen. The central premise is straightforward: if one can establish a complete set of dimensionless parameters that govern the physics of the prototype and reproduce those same dimensionless parameters in a smaller model, then the model's behavior, expressed in dimensionless form, will be identical to that of the prototype.

In the context of bolted flanged joints, the need for similitude arises from several practical constraints:

1. **Cost of full-scale testing.** Large-diameter bolted flanges --- such as those found in subsea wellhead connectors (API 6A/17D), pressure vessel closures (ASME BPVC VIII-2), or wind turbine tower segments --- may involve bolt diameters of M36 to M64 and preloads exceeding 500 kN per bolt. Full-scale Junker-type transverse vibration testing of such assemblies requires specialized fixtures, high-capacity actuators, and substantial material expenditure.

2. **Instrumentation limitations.** Embedding strain gauges, displacement sensors, or acoustic emission probes in large bolts is more difficult and expensive than in smaller, laboratory-scale fasteners. A well-designed scaled model enables the use of standard laboratory instrumentation.

3. **Parametric exploration.** During the design phase, one often needs to evaluate dozens of configurations (preload level, surface treatment, washer type, thread engagement length). Conducting all of these at full scale is rarely feasible within project timelines.

4. **Validation of numerical models.** The MSD framework implemented in Bolt Analysis Studio requires experimental validation. Scaled tests provide a practical pathway to generate validation data that can then be extrapolated to the prototype via similitude laws.

The theoretical underpinning of the entire approach is the **Buckingham Pi theorem** (Buckingham, 1914), which states that any physically meaningful equation involving $n$ dimensional variables expressible in terms of $k$ independent fundamental dimensions can be rewritten as an equation among $(n - k)$ independent dimensionless groups. If all such groups match between prototype and model, the two systems are dynamically similar, and measured quantities in the model can be converted to prototype predictions by applying the appropriate scale factors.

### 36.2 The Buckingham Pi Theorem

Consider a physical process governed by $n$ dimensional variables $q_1, q_2, \ldots, q_n$. Let these variables involve $k$ independent fundamental dimensions (for mechanical problems, typically mass $M$, length $L$, and time $T$, giving $k = 3$). The Buckingham Pi theorem guarantees the existence of $(n - k)$ independent dimensionless groups $\Pi_1, \Pi_2, \ldots, \Pi_{n-k}$ such that the governing relationship can be written as:

$$f(\Pi_1, \Pi_2, \ldots, \Pi_{n-k}) = 0$$

For bolted joint self-loosening, the relevant dimensional variables include: bolt diameter $d$, grip length $L$, preload force $F_p$, elastic modulus $E$, density $\rho$, friction coefficient $\mu$, excitation frequency $f$, transverse displacement amplitude $\delta$, and thread pitch $p$. Since $\mu$ and certain geometric ratios are already dimensionless, they appear directly as Pi-groups. The remaining variables form additional groups through systematic dimensional analysis.

**Complete similitude** requires that every independent Pi-group takes the same numerical value in both prototype and model:

$$\Pi_i^{\text{(model)}} = \Pi_i^{\text{(prototype)}}, \qquad i = 1, 2, \ldots, (n-k)$$

When this condition is satisfied, the physics is identical in dimensionless space, and results can be converted between scales using the derived scale factors.

### 36.3 Types of Similitude

The BAS similitude module recognizes four progressively more restrictive levels of similitude:

| Type | Requirements | What Is Preserved |
|------|-------------|-------------------|
| **Geometric** | All length ratios match | Shape, proportions |
| **Kinematic** | Geometric + velocity field similar | Motion patterns, streamlines |
| **Dynamic** | Kinematic + force ratios match | Force equilibrium, stress distributions |
| **Complete** | Dynamic + friction, wear, surface effects | Full tribomechanical behavior |

For self-loosening analysis, **complete similitude** is the target, because friction plays a governing role in determining whether rotational loosening occurs. In practice, complete similitude is difficult to achieve exactly due to scale effects (Section 39), so the analysis framework quantifies the deviation from ideal similitude and provides correction factors.

### 36.4 Material Similarity Classification

Three levels of material similarity are defined:

| Classification | Condition | Consequence |
|---------------|-----------|-------------|
| **Same material** | $E_m/E_p = 1$, $\rho_m/\rho_p = 1$ | Simplest scaling; stress and wave speed preserved automatically |
| **Similar material** | $E_m/\rho_m = E_p/\rho_p$ | Wave speed preserved; stress may differ |
| **Different material** | General $E_m/E_p$, $\rho_m/\rho_p$ | Full correction required; velocity and acceleration factors nontrivial |

When prototype and model use the **same material** (the most common case in practice, and the default in BAS), many scale factor expressions simplify dramatically because the elastic modulus ratio and density ratio both equal unity. All derivations in Sections 37 and 38 are presented in the general form, with simplifications noted for the same-material case.

---

## 37. Scale Factor Theory

### 37.1 The Geometric Scale Factor

The geometric scale factor $\lambda$ is defined as the ratio of a characteristic length in the model to the corresponding length in the prototype:

$$\lambda = \frac{L_{\text{model}}}{L_{\text{prototype}}}$$

By convention, $\lambda \in (0, 1]$ for a model smaller than the prototype. A value of $\lambda = 1$ corresponds to full-scale (no scaling). Typical values used in bolted joint research range from $\lambda = 0.5$ (1:2 scale) down to $\lambda = 0.125$ (1:8 scale).

Geometric similitude requires that **all** length dimensions in the model scale by the same factor $\lambda$:

$$d_m = \lambda \, d_p, \quad L_m = \lambda \, L_p, \quad t_m = \lambda \, t_p, \quad P_m = \lambda \, P_p$$

where $d$ is bolt diameter, $L$ is grip length, $t$ is flange thickness, and $P$ is thread pitch. This ensures that all geometric ratios (e.g., $L/d$, $t/d$, $P/d$) are identically preserved between model and prototype.

### 37.2 Derivation of Derived Scale Factors

Once the geometric scale $\lambda$ and the material property ratios are specified, every other physical quantity has a uniquely determined scale factor. The derivations proceed from dimensional analysis combined with the requirement that stress be preserved (elastic similitude).

**Stress similitude** requires:

$$\sigma_m = \sigma_p \cdot \frac{E_m}{E_p}$$

For the same material, $E_m/E_p = 1$, so stress is identically preserved. This is the fundamental constraint from which all other factors follow.

**Force.** Since $F = \sigma \cdot A$ and area scales as $\lambda^2$:

$$F_m = F_p \cdot \lambda^2 \cdot \frac{E_m}{E_p}$$

**Displacement.** Since $\delta = \varepsilon \cdot L$ and strain is preserved while length scales as $\lambda$:

$$\delta_m = \delta_p \cdot \lambda$$

**Stiffness.** From $k = F/\delta$:

$$k_m = k_p \cdot \frac{\lambda^2 (E_m/E_p)}{\lambda} = k_p \cdot \lambda \cdot \frac{E_m}{E_p}$$

**Mass.** From $m = \rho \cdot V$ and $V$ scales as $\lambda^3$:

$$m_m = m_p \cdot \lambda^3 \cdot \frac{\rho_m}{\rho_p}$$

**Natural frequency.** From $\omega = \sqrt{k/m}$:

$$f_m = f_p \cdot \frac{1}{\lambda} \cdot \sqrt{\frac{E_m/\rho_m}{E_p/\rho_p}}$$

For the same material, this simplifies to $f_m = f_p / \lambda$. A 1:4 scale model therefore has natural frequencies 4 times higher than the prototype --- a crucial consideration when designing the test excitation.

**Time.** As the reciprocal of frequency:

$$t_m = t_p \cdot \lambda \cdot \sqrt{\frac{\rho_m/E_m}{\rho_p/E_p}}$$

**Velocity.** From $v = \delta / t$:

$$v_m = v_p \cdot \sqrt{\frac{E_m/\rho_m}{E_p/\rho_p}}$$

For the same material, $v_m = v_p$: velocity is preserved. This is consistent with the elastic wave speed $c = \sqrt{E/\rho}$ being a material property.

**Acceleration.** From $a = v / t$:

$$a_m = a_p \cdot \frac{1}{\lambda} \cdot \frac{E_m/\rho_m}{E_p/\rho_p}$$

**Damping coefficient.** For viscous damping $c_{\text{damp}} = 2\zeta\sqrt{km}$:

$$c_{\text{damp},m} = c_{\text{damp},p} \cdot \lambda^2 \cdot \sqrt{\frac{E_m \rho_m}{E_p \rho_p}}$$

**Energy.** From $W = F \cdot \delta$:

$$W_m = W_p \cdot \lambda^3 \cdot \frac{E_m}{E_p}$$

**Power.** From $P = W / t$:

$$P_m = P_p \cdot \lambda^2 \cdot \sqrt{\frac{E_m^3 / \rho_m}{E_p^3 / \rho_p}}$$

**Moment and torque.** From $M = F \cdot L$:

$$M_m = M_p \cdot \lambda^3 \cdot \frac{E_m}{E_p}$$

### 37.3 Complete Scale Factor Table

The following table summarizes all derived scale factors. The "General Expression" column shows the factor for arbitrary material ratios. The "Same Material" column shows the simplified result when $E_m/E_p = 1$ and $\rho_m/\rho_p = 1$.

| Quantity | Symbol | General Expression | Same Material |
|----------|--------|-------------------|---------------|
| Length | $\lambda_L$ | $\lambda$ | $\lambda$ |
| Area | $\lambda_A$ | $\lambda^2$ | $\lambda^2$ |
| Volume | $\lambda_V$ | $\lambda^3$ | $\lambda^3$ |
| Mass | $\lambda_m$ | $\lambda^3 \cdot (\rho_m / \rho_p)$ | $\lambda^3$ |
| Force | $\lambda_F$ | $\lambda^2 \cdot (E_m / E_p)$ | $\lambda^2$ |
| Stress | $\lambda_\sigma$ | $E_m / E_p$ | $1$ |
| Strain | $\lambda_\varepsilon$ | $1$ | $1$ |
| Displacement | $\lambda_\delta$ | $\lambda$ | $\lambda$ |
| Stiffness | $\lambda_k$ | $\lambda \cdot (E_m / E_p)$ | $\lambda$ |
| Damping coeff. | $\lambda_c$ | $\lambda^2 \cdot \sqrt{E_m \rho_m / (E_p \rho_p)}$ | $\lambda^2$ |
| Frequency | $\lambda_f$ | $(1/\lambda) \cdot \sqrt{(E_m / \rho_m) \cdot (\rho_p / E_p)}$ | $1/\lambda$ |
| Time | $\lambda_t$ | $\lambda \cdot \sqrt{(\rho_m / E_m) \cdot (E_p / \rho_p)}$ | $\lambda$ |
| Velocity | $\lambda_v$ | $\sqrt{(E_m / \rho_m) \cdot (\rho_p / E_p)}$ | $1$ |
| Acceleration | $\lambda_a$ | $(1/\lambda) \cdot (E_m / \rho_m) \cdot (\rho_p / E_p)$ | $1/\lambda$ |
| Energy | $\lambda_W$ | $\lambda^3 \cdot (E_m / E_p)$ | $\lambda^3$ |
| Power | $\lambda_P$ | $\lambda^2 \cdot \sqrt{E_m^3 / (\rho_m E_p^3 / \rho_p)}$ | $\lambda^2$ |
| Moment / Torque | $\lambda_M$ | $\lambda^3 \cdot (E_m / E_p)$ | $\lambda^3$ |
| Area moment of inertia | $\lambda_I$ | $\lambda^4$ | $\lambda^4$ |
| Mass moment of inertia | $\lambda_J$ | $\lambda^5 \cdot (\rho_m / \rho_p)$ | $\lambda^5$ |

### 37.4 Physical Interpretation of Key Scaling Laws

Several of these results deserve physical intuition:

**Force scales as $\lambda^2$.** This is a direct consequence of stress preservation: since stress = force / area and stress is preserved while area scales as $\lambda^2$, force must also scale as $\lambda^2$. For a 1:4 model ($\lambda = 0.25$), the preload force is $0.25^2 = 0.0625$ times the prototype value --- only 6.25%. A prototype preload of 160 kN becomes 10 kN in the model.

**Frequency scales as $1/\lambda$.** Smaller structures vibrate at higher frequencies. This is familiar from everyday experience: a short guitar string produces a higher-pitched sound than a long one. For a 1:4 model, the natural frequency is 4 times higher than the prototype. If the prototype has a first bending mode at 250 Hz, the model's first mode is at 1000 Hz.

**Velocity is preserved (same material).** The elastic wave speed $c = \sqrt{E/\rho}$ depends only on material properties. Since both prototype and model are the same material, wave propagation velocities are identical. This means that impact phenomena and wave propagation are naturally similar.

**Energy scales as $\lambda^3$.** Energy dissipated per cycle (from friction, damping, or wear) scales with the cube of the geometric scale. For a 1:4 model, energy dissipation is $0.25^3 = 0.0156$ times the prototype --- about 1.6%. This has important implications for calorimetric or acoustic emission measurements.

**Torque scales as $\lambda^3$.** This is often initially counterintuitive. Since torque = force $\times$ lever arm, and force scales as $\lambda^2$ while lever arm scales as $\lambda$, the product scales as $\lambda^3$. A tightening torque of 450 N-m in the prototype becomes $450 \times 0.25^3 = 7.03$ N-m in a 1:4 model.

### 37.5 Using Scale Factors to Convert Results

To convert a measurement from the **model** to a **prototype prediction**, divide by the scale factor:

$$Q_{\text{prototype}} = \frac{Q_{\text{model}}}{\lambda_Q}$$

Conversely, to determine the required **model** test condition from a known **prototype** value, multiply by the scale factor:

$$Q_{\text{model}} = Q_{\text{prototype}} \cdot \lambda_Q$$

For example, if the model test measures a preload loss of $\Delta F_m = 250$ N, the predicted prototype preload loss is:

$$\Delta F_p = \frac{\Delta F_m}{\lambda_F} = \frac{250}{0.0625} = 4000 \text{ N}$$

---

## 38. Dimensionless Pi-Groups

### 38.1 Identification of Pi-Groups for Bolted Joints

The BAS similitude module identifies twelve dimensionless Pi-groups that characterize the complete mechanical state of a bolted flanged joint under transverse vibratory loading. These are divided into **primary groups** (nine, governing the fundamental mechanics) and **secondary groups** (three, capturing geometric detail).

For complete similitude, all Pi-groups must match between prototype and model. In practice, geometric similitude automatically preserves most groups; the friction coefficient (which is inherently dimensionless) is the principal group that may deviate due to scale effects.

### 38.2 Primary Pi-Groups

**Pi-1: Grip Ratio (Bolt Flexibility Parameter)**

$$\Pi_1 = \frac{L}{d}$$

The grip-to-diameter ratio is the single most important geometric parameter governing bolt flexibility. A longer grip relative to diameter produces a more compliant bolt, which is beneficial for fatigue resistance and loosening resistance. Under geometric similitude, $\Pi_1$ is exactly preserved because both $L$ and $d$ scale by $\lambda$.

Typical values: $\Pi_1 = 3$ to $6$ for standard joints; $\Pi_1 > 5$ preferred for vibration resistance (VDI 2230, 2015).

**Pi-2: Flange Aspect Ratio**

$$\Pi_2 = \frac{t}{d}$$

The ratio of clamped member thickness to bolt diameter governs the compression cone geometry and member stiffness. Preserved exactly under geometric similitude.

**Pi-3: Preload Utilization**

$$\Pi_3 = \frac{F_p}{\sigma_y \cdot A_t}$$

This is the ratio of bolt preload stress to yield strength, equivalently the fraction of yield capacity used. Under stress similitude with the same material, both $F_p / A_t$ and $\sigma_y$ are preserved, so $\Pi_3$ is naturally preserved.

Typical values: $\Pi_3 = 0.6$ to $0.9$ (VDI 2230 recommends 75--90% utilization for high-strength bolts).

**Pi-4: Load Ratio (Separation Margin)**

$$\Pi_4 = \frac{F_{\text{ext}}}{F_p}$$

The ratio of external axial force to preload is a measure of the margin against joint separation. Since both forces scale identically as $\lambda^2$, the ratio is preserved.

**Pi-5: Joint Stiffness Constant**

$$\Pi_5 = C = \frac{k_b}{k_b + k_m}$$

The load introduction factor $C$ determines how an external axial force is partitioned between the bolt and the clamped members. Under geometric similitude, both $k_b$ and $k_m$ scale by the same factor $\lambda$, so $C$ is preserved. Typical values: $C = 0.1$ to $0.3$.

**Pi-6: Material Elasticity Characteristic**

$$\Pi_6 = \frac{E}{\sigma_y}$$

This dimensionless ratio characterizes the elastic range of the bolt material. It is preserved identically when the same material is used.

**Pi-7: Nut Factor**

$$\Pi_7 = K$$

The nut factor (or torque coefficient) relates applied tightening torque to achieved preload via $T = K \cdot d \cdot F_p$. It depends on thread geometry and friction, and is dimensionless. For geometric similitude with the same surface treatment, $K$ should be preserved, though scale effects on friction (Section 39.2) may introduce small deviations.

**Pi-8: Friction Coefficient**

$$\Pi_8 = \mu$$

The friction coefficient at thread and bearing interfaces is already dimensionless. However, it is the Pi-group most susceptible to scale effects: contact mechanics at smaller scales can alter the effective friction coefficient due to changes in real contact area, surface roughness ratio, and contact pressure distribution (Section 39.2).

**Pi-9: Poisson's Ratio**

$$\Pi_9 = \nu$$

Poisson's ratio is a material constant that influences the compression cone shape and lateral contraction of the bolt under tension. It is preserved identically when the same material is used.

### 38.3 Secondary Pi-Groups

**Pi-10: Thread Pitch Ratio**

$$\Pi_{10} = \frac{P}{d}$$

The pitch-to-diameter ratio characterizes thread coarseness. For standard ISO metric coarse threads, this ratio follows the standards table and is generally well-preserved in geometric similitude. However, if the scaled model diameter does not correspond to a standard thread size, one must use a non-standard pitch to maintain the ratio, or accept a small deviation.

**Pi-11: Clearance Ratio**

$$\Pi_{11} = \frac{d_h}{d}$$

The bolt hole clearance ratio affects shear loading transfer and potential bolt bending. Preserved under geometric similitude.

**Pi-12: Washer Coverage Ratio**

$$\Pi_{12} = \frac{d_w}{d}$$

The washer outer diameter to bolt diameter ratio governs bearing pressure distribution and the compression cone base area. Preserved under geometric similitude.

### 38.4 Match Tolerance and Quality Rating

For each Pi-group, BAS computes the percentage deviation between model and prototype values:

$$\text{Deviation} = 100 \times \frac{|\Pi_m - \Pi_p|}{|\Pi_p|} \quad [\%]$$

The match quality is then classified:

| Deviation Range | Quality Rating | Interpretation |
|----------------|---------------|----------------|
| $\leq 1\%$ | **Excellent** | Negligible difference; no correction needed |
| $1\%$ to $5\%$ | **Good** | Minor difference; within normal experimental scatter |
| $5\%$ to $10\%$ | **Acceptable** | Noticeable difference; correction recommended |
| $10\%$ to $20\%$ | **Marginal** | Significant difference; correction mandatory |
| $> 20\%$ | **Poor** | Similitude substantially violated; results unreliable |

The default match tolerance is $\pm 5\%$ for most groups, with a relaxed tolerance of $\pm 10\%$ for friction-related groups (reflecting the inherently larger scatter in friction measurements).

### 38.5 Overall Similitude Quality Assessment

The overall quality of the similitude analysis is assessed by counting the number of matched Pi-groups and checking for critical scale effects:

- **Excellent:** All Pi-groups matched and no HIGH or CRITICAL scale effects
- **Good:** At most 2 groups unmatched and no HIGH or CRITICAL scale effects
- **Acceptable:** At most 3 groups unmatched
- **Poor -- review scale factor:** More than 3 groups unmatched or critical scale effects present

---

## 39. Scale Effects and Correction Factors

### 39.1 Why Scaling Is Not Perfect

Even when geometric similitude is meticulously maintained, certain physical phenomena do not scale in proportion to the geometric dimensions. These **scale effects** arise because:

1. **Manufacturing processes have absolute tolerances.** Surface roughness, thread form accuracy, and plating thickness are governed by manufacturing technology, not component size. A surface ground to $R_z = 6.3\ \mu\text{m}$ has the same roughness whether it belongs to an M8 or an M48 bolt.

2. **Contact mechanics introduces nonlinearity.** The real area of contact between two rough surfaces depends on normal pressure and surface statistics in ways that are not simply proportional to nominal area. Smaller components at the same stress level may exhibit different ratios of real to nominal contact area.

3. **Tribological behavior has intrinsic length scales.** Lubrication film thickness, asperity interaction range, and wear particle dimensions are governed by material properties and surface chemistry, not by component geometry.

4. **Microstructural features do not scale.** Grain size, inclusion spacing, and phase distribution in the bolt material are independent of bolt diameter. Their relative influence increases at smaller scales.

The BAS framework identifies five specific scale effects relevant to bolted joints, quantifies each through a correction factor, and classifies the severity. The correction factors are multiplicative: when applied to the scaled model prediction, they yield a corrected prototype estimate.

### 39.2 Surface Roughness Effect

**Physical mechanism.** Surface roughness ($R_z$) is determined by the machining process and does not scale with component size. Consequently, the dimensionless ratio $R_z / d$ is larger in the model than in the prototype:

$$\left(\frac{R_z}{d}\right)_m = \frac{R_z}{\lambda \cdot d_p} = \frac{1}{\lambda} \left(\frac{R_z}{d}\right)_p$$

This elevated relative roughness has two consequences: (a) the real contact area fraction may differ, affecting friction; and (b) embedding (plastic settling) at interfaces is proportionally more significant.

**Correction factor.** Based on the sensitivity of embedding to the $R_z/d$ ratio (informed by VDI 2230 embedment correlations):

$$C_{\text{roughness}} = 1 + 0.10 \times \frac{(R_z/d)_m - (R_z/d)_p}{(R_z/d)_p}$$

Since $(R_z/d)_m / (R_z/d)_p = 1/\lambda$, the deviation percentage is:

$$\text{Deviation} = 100 \times \left(\frac{1}{\lambda} - 1\right) \quad [\%]$$

**Severity classification:**

| Scale Factor $\lambda$ | Deviation | Severity |
|------------------------|-----------|----------|
| $\lambda > 0.5$ | $< 100\%$ | LOW to MEDIUM |
| $0.25 < \lambda \leq 0.5$ | $100\%$ to $300\%$ | MEDIUM to HIGH |
| $\lambda \leq 0.25$ | $> 300\%$ | HIGH to CRITICAL |

**Mitigation.** Use finer surface finish on model components (e.g., grinding to $R_z = 1.6\ \mu\text{m}$ instead of $6.3\ \mu\text{m}$) to reduce the $R_z/d$ discrepancy.

### 39.3 Friction Coefficient Effect

**Physical mechanism.** Empirical tribological studies consistently show that the effective friction coefficient at bolted joint interfaces increases slightly as the bolt diameter decreases, when all other surface conditions (roughness, lubrication, coating) are held constant. This effect is attributed to the higher nominal contact pressures in smaller fasteners at the same stress level, and to the increased ratio of surface energy to bulk deformation energy.

The empirical correlation implemented in BAS is:

$$\mu_m = \mu_p \times \left(1 + 0.08 \times (1 - \lambda)\right)$$

This states that the friction coefficient increases by approximately 8% for each factor-of-two reduction in scale. For a 1:4 scale model ($\lambda = 0.25$), the predicted friction increase is:

$$\mu_m = \mu_p \times (1 + 0.08 \times 0.75) = 1.06 \, \mu_p$$

which represents a 6% increase.

**Correction factor:**

$$C_{\text{friction}} = \frac{\mu_m}{\mu_p} = 1 + 0.08 \times (1 - \lambda)$$

**Consequences for loosening analysis.** Since self-loosening requires that the transverse force exceeds friction resistance at both thread and bearing surfaces, an elevated friction coefficient in the model means the model is **more resistant to loosening** than the prototype at the same stress level. The model test therefore provides a **conservative** (non-conservative for safety assessment) estimate of loosening tendency unless corrected.

**Severity classification:**

| Scale Factor $\lambda$ | Friction Increase | Severity |
|------------------------|------------------|----------|
| $\lambda > 0.5$ | $< 4\%$ | NEGLIGIBLE to LOW |
| $0.25 < \lambda \leq 0.5$ | $4\%$ to $6\%$ | LOW to MEDIUM |
| $\lambda \leq 0.25$ | $> 6\%$ | MEDIUM |

### 39.4 Embedding Loss Effect

**Physical mechanism.** Embedding (also called settling or plastic flattening) occurs at the mating surfaces of a bolted joint during the first loading cycles. The absolute magnitude of embedding deformation $\delta_{fp}$ per interface (typically 2 to 5 $\mu$m for machined steel surfaces, per VDI 2230 Table A8) is governed by local plastic deformation of asperities and is largely independent of bolt size.

The resulting relative preload loss, however, depends on the system stiffness and preload level. Since stiffness scales as $\lambda$ and preload scales as $\lambda^2$, the relative loss ratio becomes:

$$\frac{\Delta F_p}{F_p} \propto \frac{\delta_{fp} \cdot k_{\text{sys}}}{F_p} \propto \frac{\delta_{fp} \cdot \lambda}{\lambda^2} = \frac{\delta_{fp}}{\lambda}$$

This means that the relative preload loss from embedding scales inversely with $\lambda$: a 1:4 model loses 4 times more preload (as a fraction) than the prototype from the same absolute embedding deformation.

**Correction factor:**

$$C_{\text{embedding}} = 1 + 0.05 \times \left(\frac{1}{\lambda} - 1\right)$$

The coefficient 0.05 is a weighting factor reflecting that embedding is only one of several preload loss mechanisms (others include relaxation, thermal effects, and rotational loosening).

**Severity classification:**

| Scale Factor $\lambda$ | Relative Loss Multiplier $(1/\lambda)$ | Severity |
|------------------------|-----------------------------------------|----------|
| $\lambda > 0.5$ | $< 2\times$ | LOW |
| $0.25 < \lambda \leq 0.5$ | $2\times$ to $4\times$ | MEDIUM to HIGH |
| $\lambda \leq 0.25$ | $> 4\times$ | HIGH to CRITICAL |

**Mitigation.** (a) Apply multiple tightening cycles to the model bolts before testing to "seat" the interfaces. (b) Use finer surface finishes to reduce initial embedding deformation. (c) Account for the excess embedding analytically when converting model results to prototype predictions.

### 39.5 Thread Form Tolerance Effect

**Physical mechanism.** Thread manufacturing tolerances are specified as absolute values within each tolerance class (e.g., ISO 6g/6H). These tolerances do not scale proportionally with bolt diameter. For example, the pitch diameter tolerance for an M24 bolt is on the order of $\pm 30\ \mu\text{m}$, while for an M6 bolt it might be $\pm 18\ \mu\text{m}$ --- a much smaller absolute value, but a much larger **relative** value compared to the pitch diameter itself.

This means that thread geometry in a scaled model deviates relatively more from the nominal profile than in the prototype, potentially affecting thread load distribution and engagement stiffness.

**Deviation estimate:**

$$\text{Deviation} = 100 \times \left(\frac{1}{\lambda} - 1\right) \times 0.3 \quad [\%]$$

The factor 0.3 reflects the empirical observation that only about 30% of the geometric tolerance effect translates into a mechanical performance deviation (the remainder is absorbed by the thread's self-aligning behavior under load).

**Correction factor:**

$$C_{\text{thread}} = 1 + 0.02 \times \left(\frac{1}{\lambda} - 1\right)$$

**Severity classification:**

| Scale Factor $\lambda$ | Deviation | Severity |
|------------------------|-----------|----------|
| $\lambda > 0.5$ | $< 10\%$ | NEGLIGIBLE to LOW |
| $0.25 < \lambda \leq 0.5$ | $10\%$ to $30\%$ | LOW to MEDIUM |
| $\lambda \leq 0.25$ | $> 30\%$ | MEDIUM to HIGH |

### 39.6 Stress Concentration Effect

**Physical mechanism.** The stress concentration factor $K_t$ at the thread root depends on the ratio of root radius to pitch ($r/P$). For standard ISO metric threads, this ratio is a constant ($r/P \approx 0.144$) regardless of bolt size, because the thread profile is geometrically similar across the size range.

Consequently, $K_t$ is **preserved** under geometric similitude, and no correction is needed --- provided that the model uses a geometrically similar thread form.

**Correction factor:**

$$C_{\text{stress\,conc}} = 1.0 \quad \text{(no correction)}$$

**Severity:** NEGLIGIBLE (0% deviation).

**Caveat.** If the scaled model bolt uses a non-standard thread form (e.g., because the ideal scaled pitch is not commercially available), then $K_t$ may differ and this effect should be re-evaluated.

### 39.7 Severity Classification System

BAS classifies scale effect severity based on the absolute magnitude of the deviation:

| Severity | Deviation Range | Action Required |
|----------|----------------|-----------------|
| **NEGLIGIBLE** | $< 2\%$ | No action needed |
| **LOW** | $2\%$ to $5\%$ | Note in report; no correction required |
| **MEDIUM** | $5\%$ to $15\%$ | Apply correction factor; discuss in analysis |
| **HIGH** | $15\%$ to $30\%$ | Apply correction; consider alternative scale |
| **CRITICAL** | $> 30\%$ | Scaling may be inadequate; reconsider approach |

### 39.8 Combined Correction Factor

The combined correction factor is the product of all individual correction factors from effects with severity above NEGLIGIBLE:

$$C_{\text{combined}} = \prod_{i} C_i \qquad \text{for all } i \text{ where severity} \neq \text{NEGLIGIBLE}$$

This combined factor is applied to the raw model-to-prototype prediction:

$$Q_{p,\text{corrected}} = \frac{Q_m}{\lambda_Q} \times C_{\text{combined}}$$

In practice, $C_{\text{combined}}$ typically ranges from 1.0 to 1.3 for scale factors $\lambda \geq 0.25$ with same-material similitude.

---

## 40. Practical Application Guidelines

### 40.1 When to Use Similitude Analysis

Similitude analysis is most valuable in the following situations:

1. **Design optimization phase.** When multiple joint configurations must be evaluated and full-scale testing of each is prohibitively expensive, scaled model tests allow rapid screening of alternatives.

2. **Qualification by analysis.** Certain codes and standards (e.g., API 6A, ASME PCC-1) accept analytical predictions supported by validated test data. Similitude provides a framework for extrapolating limited test data to the design configuration.

3. **Failure investigation.** When a field failure occurs in a large joint, scaled reproductions of the failure mode can be conducted more quickly and cheaply than full-scale tests.

4. **Research and development.** University and research laboratory test rigs are typically sized for bolts in the M8 to M16 range. Similitude analysis enables these results to be applied to industrial applications using M30+ fasteners.

### 40.2 Minimum Recommended Scale Factor

Based on the scale effect analysis in Section 39, the minimum recommended geometric scale factor is:

$$\lambda_{\min} = 0.25 \qquad \text{(1:4 scale)}$$

Below this value, the combined correction factor exceeds approximately 1.15 (15% correction), and the uncertainties in the individual correction correlations begin to undermine confidence in the extrapolated predictions.

For critical applications (safety-relevant joints, subsea equipment), a more conservative limit is recommended:

$$\lambda_{\min,\text{critical}} = 0.33 \qquad \text{(1:3 scale)}$$

### 40.3 Test Planning Considerations

**Number of tests.** A minimum of three replicate tests at each condition is recommended to establish statistical confidence. For scale validation studies (where the objective is to verify the scaling laws themselves), tests at two or more scale factors are recommended, e.g., 1:2 and 1:4 relative to the prototype, so that the trend can be verified.

**Surface preparation.** The model bolts should receive the same surface treatment (zinc plating, phosphate coating, lubricant) as the prototype to maintain friction similitude. If identical coating thickness cannot be achieved at the model scale, the deviation should be documented and assessed.

**Instrumentation.** Preload should be measured by calibrated strain gauges or ultrasonic bolt tension monitors. For scaled bolts in the M8 to M12 range, piezoelectric load cells under the bolt head provide reliable direct measurement. For transverse displacement measurement, LVDT or laser vibrometer techniques are standard.

**Excitation parameters.** Under same-material similitude, the excitation frequency must be scaled by $1/\lambda$. If the prototype operates at 12.5 Hz, a 1:4 model requires excitation at 50 Hz. The transverse displacement amplitude scales as $\lambda$: if the prototype experiences 0.65 mm amplitude, the model requires 0.1625 mm.

### 40.4 Converting Model Results to Prototype Predictions

The general procedure for converting measured model results to prototype predictions is:

1. **Measure** the quantity of interest $Q_m$ in the model test (preload loss, number of cycles to loosening, rotation angle, etc.).

2. **Identify** the appropriate scale factor $\lambda_Q$ from the table in Section 37.3.

3. **Compute** the raw prototype prediction:

$$Q_{p,\text{raw}} = \frac{Q_m}{\lambda_Q}$$

4. **Apply** the combined correction factor (Section 39.8):

$$Q_{p,\text{corrected}} = Q_{p,\text{raw}} \times C_{\text{combined}}$$

5. **Report** the corrected prediction with an uncertainty bound reflecting the correction factor magnitude and experimental scatter.

### 40.5 Limitations and Caveats

The similitude framework has inherent limitations that the analyst must understand:

1. **Friction is the weakest link.** Friction coefficients have an intrinsic scatter of $\pm 10\%$ to $\pm 20\%$ even in well-controlled tests. This scatter may exceed the systematic scale effect, making it difficult to validate the friction correction factor experimentally.

2. **Lubrication regime may change.** If the prototype operates in a mixed lubrication regime but the model (at different contact pressure and sliding speed) operates in a boundary regime, the friction behavior will differ qualitatively, not just quantitatively. The correction factor for friction assumes the same lubrication regime.

3. **Discrete thread sizes.** The ideal scaled thread pitch may not correspond to a standard commercially available size. One must either use custom-machined threads (expensive) or accept the nearest standard size with a documented deviation in $\Pi_{10}$.

4. **Fatigue behavior does not scale simply.** If fatigue life is of interest, the scaling of S-N curves involves additional size effects (statistical volume effect, surface condition effect, stress gradient effect per Kuguel, 1961) that are not captured by the basic similitude framework.

5. **Thermal effects require separate scaling.** If the prototype experiences thermal transients, the thermal time constant scales as $\lambda^2 / \alpha$ (where $\alpha$ is thermal diffusivity), which differs from the mechanical time scaling. Thermal-mechanical coupling requires separate treatment.

---

## 41. Example: Scaling M30 Bolt to M10 Model

### 41.1 Problem Statement

An engineer needs to evaluate the self-loosening resistance of an M30 flanged joint used in a subsea Christmas tree assembly. Full-scale Junker testing is impractical due to the size of the test rig required. The engineer proposes to conduct scaled tests using standard M10 bolts.

**Prototype (full-scale) parameters:**

| Parameter | Value |
|-----------|-------|
| Bolt diameter $d_p$ | 30 mm (M30 $\times$ 3.5) |
| Thread pitch $P_p$ | 3.5 mm |
| Grip length $L_p$ | 120 mm |
| Flange thickness $t_p$ | 36 mm |
| Bolt material | ASTM A193 B7 ($E = 205$ GPa, $\sigma_y = 724$ MPa, $\rho = 7850$ kg/m$^3$) |
| Preload $F_{p,\text{proto}}$ | 220 kN (75% of yield) |
| Surface roughness $R_z$ | 6.3 $\mu$m |
| Thread friction $\mu_t$ | 0.15 |
| Bearing friction $\mu_b$ | 0.15 |
| Embedding per interface | 3 $\mu$m |
| Excitation frequency | 12.5 Hz |
| Transverse displacement | 0.65 mm |

### 41.2 Geometric Scale Factor

$$\lambda = \frac{d_m}{d_p} = \frac{10}{30} = 0.333$$

This corresponds to a 1:3 scale model.

### 41.3 Scaled Model Dimensions

Applying the geometric scale factor to all lengths:

| Parameter | Prototype | Scale Factor | Model (Scaled) | Nearest Standard |
|-----------|-----------|-------------|----------------|------------------|
| Bolt diameter | 30.0 mm | $\lambda = 0.333$ | 10.0 mm | M10 (exact) |
| Thread pitch | 3.5 mm | $\lambda$ | 1.167 mm | 1.5 mm (M10 coarse) |
| Grip length | 120 mm | $\lambda$ | 40.0 mm | 40 mm |
| Flange thickness | 36 mm | $\lambda$ | 12.0 mm | 12 mm |

The thread pitch deviates from the ideal scaled value: the standard M10 coarse pitch of 1.5 mm differs from the ideal 1.167 mm. This introduces a deviation in $\Pi_{10}$:

$$\Pi_{10,p} = \frac{P_p}{d_p} = \frac{3.5}{30} = 0.1167$$

$$\Pi_{10,m} = \frac{P_m}{d_m} = \frac{1.5}{10} = 0.150$$

$$\text{Deviation} = \frac{|0.150 - 0.1167|}{0.1167} \times 100\% = 28.6\%$$

This is a significant deviation. The options are: (a) use M10 $\times$ 1.25 fine pitch (giving $\Pi_{10} = 0.125$, deviation = 7.1%), or (b) accept the coarse pitch with documentation of the discrepancy. Option (a) is recommended.

### 41.4 Scaled Loading Parameters

| Quantity | Prototype | Scale Factor | Model Value |
|----------|-----------|-------------|-------------|
| Preload force | 220,000 N | $\lambda^2 = 0.111$ | 24,444 N $\approx$ 24.4 kN |
| Tightening torque | 990 N-m | $\lambda^3 = 0.0370$ | 36.7 N-m |
| Excitation frequency | 12.5 Hz | $1/\lambda = 3.0$ | 37.5 Hz |
| Transverse displacement | 0.65 mm | $\lambda = 0.333$ | 0.217 mm |
| Transverse force | (from $k \cdot \delta$) | $\lambda^2$ | $F_{t,p} \times 0.111$ |

### 41.5 Verification of Pi-Groups

| Pi-Group | Expression | Prototype | Model | Deviation | Status |
|----------|-----------|-----------|-------|-----------|--------|
| $\Pi_1$ | $L/d$ | 4.000 | 4.000 | 0.0% | Excellent |
| $\Pi_2$ | $t/d$ | 1.200 | 1.200 | 0.0% | Excellent |
| $\Pi_3$ | $F_p / (\sigma_y A_t)$ | 0.750 | 0.750 | 0.0% | Excellent |
| $\Pi_4$ | $F_{\text{ext}}/F_p$ | (same) | (same) | 0.0% | Excellent |
| $\Pi_5$ | $C$ | 0.22 | 0.22 | 0.0% | Excellent |
| $\Pi_6$ | $E/\sigma_y$ | 283 | 283 | 0.0% | Excellent |
| $\Pi_7$ | $K$ | 0.18 | 0.18 | 0.0% | Excellent |
| $\Pi_8$ | $\mu$ | 0.150 | 0.154 | 2.7% | Good |
| $\Pi_9$ | $\nu$ | 0.30 | 0.30 | 0.0% | Excellent |

All primary Pi-groups are matched within Good or Excellent tolerance. The only deviation arises from the friction scale effect ($\Pi_8$).

### 41.6 Scale Effect Analysis

**Surface Roughness:**

$$\left(\frac{R_z}{d}\right)_p = \frac{6.3}{30{,}000} = 2.10 \times 10^{-4}$$

$$\left(\frac{R_z}{d}\right)_m = \frac{6.3}{10{,}000} = 6.30 \times 10^{-4}$$

$$\text{Deviation} = \frac{6.30 - 2.10}{2.10} \times 100\% = +200\%$$

$$C_{\text{roughness}} = 1 + 0.10 \times \frac{6.30 - 2.10}{2.10} = 1.20$$

Severity: **HIGH** (200% deviation).

**Friction Coefficient:**

$$\mu_m = 0.15 \times (1 + 0.08 \times (1 - 0.333)) = 0.15 \times 1.053 = 0.158$$

$$\text{Deviation} = +5.3\%$$

$$C_{\text{friction}} = 1.053$$

Severity: **MEDIUM**.

**Embedding Loss:**

$$\text{Loss multiplier} = \frac{1}{\lambda} = 3.0 \times$$

$$\text{Deviation} = +200\%$$

$$C_{\text{embedding}} = 1 + 0.05 \times (3.0 - 1) = 1.10$$

Severity: **HIGH**.

**Thread Form Tolerance:**

$$\text{Deviation} = 100 \times (3.0 - 1) \times 0.3 = 60\%$$

$$C_{\text{thread}} = 1 + 0.02 \times (3.0 - 1) = 1.04$$

Severity: **HIGH**.

**Stress Concentration:**

$$C_{\text{stress\,conc}} = 1.0$$

Severity: **NEGLIGIBLE**.

### 41.7 Combined Correction Factor

$$C_{\text{combined}} = C_{\text{roughness}} \times C_{\text{friction}} \times C_{\text{embedding}} \times C_{\text{thread}}$$

$$C_{\text{combined}} = 1.20 \times 1.053 \times 1.10 \times 1.04 = 1.445$$

This indicates that the uncorrected model prediction would underestimate the prototype preload loss by approximately 44.5%.

### 41.8 Interpreting Model Test Results

Suppose the M10 model test measures a preload loss of $\Delta F_m = 800$ N after 2000 cycles of transverse vibration. The predicted prototype preload loss is:

1. **Raw scaling:**

$$\Delta F_{p,\text{raw}} = \frac{\Delta F_m}{\lambda_F} = \frac{800}{0.111} = 7{,}207 \text{ N}$$

2. **Corrected prediction:**

$$\Delta F_{p,\text{corrected}} = 7{,}207 \times 1.445 = 10{,}414 \text{ N} \approx 10.4 \text{ kN}$$

3. **As a fraction of prototype preload:**

$$\frac{\Delta F_p}{F_p} = \frac{10{,}414}{220{,}000} = 4.7\%$$

This prediction indicates that the prototype M30 joint is expected to lose approximately 4.7% of its preload after 2000 cycles under the specified transverse loading --- a value that should be compared against the design acceptance criteria (typically 10% maximum per VDI 2230).

### 41.9 Assessment Summary

| Item | Value | Assessment |
|------|-------|-----------|
| Scale factor $\lambda$ | 0.333 (1:3) | Acceptable (above $\lambda_{\min} = 0.25$) |
| Pi-groups matched | 9/9 primary | Excellent |
| Combined correction | 1.445 | Moderate; acceptable with documented uncertainty |
| Dominant scale effects | Surface roughness (HIGH), Embedding (HIGH) | Mitigable with surface preparation |
| Recommendation | Proceed with testing; use fine surface finish on model | --- |

---

## References

1. **Buckingham, E.** (1914). "On Physically Similar Systems; Illustrations of the Use of Dimensional Equations." *Physical Review*, Vol. 4, No. 4, pp. 345--376. DOI: [10.1103/PhysRev.4.345](https://doi.org/10.1103/PhysRev.4.345). -- *The foundational theorem of dimensional analysis. States that any physical equation involving $n$ variables expressible in $k$ fundamental dimensions can be rewritten as $(n-k)$ independent dimensionless groups.*

2. **VDI 2230 Part 1** (2015). *Systematic Calculation of Highly Stressed Bolted Joints -- Joints with One Cylindrical Bolt*. Verein Deutscher Ingenieure, Dusseldorf. -- *Provides the bolt stiffness, member stiffness, and load introduction factor formulas that underpin the dimensional analysis of bolted joints.*

3. **Bickford, J.H.** (2008). *Introduction to the Design and Behavior of Bolted Joints*, 4th ed. CRC Press, Boca Raton, FL. ISBN: 978-0-8493-8176-8. -- *Comprehensive reference for the spring analogy, stiffness ratios, and preload behavior used as the physical basis for similitude scaling.*

4. **Junker, G.H.** (1969). "New Criteria for Self-Loosening of Fasteners Under Vibration." *SAE Transactions*, Vol. 78, pp. 314--335. SAE Paper 690055. DOI: [10.4271/690055](https://doi.org/10.4271/690055). -- *The standard loosening test (DIN 65151) that defines the experimental protocol for which similitude scaling is most commonly applied.*

5. **Nassar, S.A. and Housari, B.A.** (2007). "Study of the Effect of Hole Clearance and Thread Fit on the Self-Loosening of Threaded Fasteners." *ASME Journal of Mechanical Design*, Vol. 129, No. 6, pp. 586--594. DOI: [10.1115/1.2717230](https://doi.org/10.1115/1.2717230). -- *Demonstrates the importance of geometric parameters (clearance, thread fit) on loosening, motivating the need for accurate geometric similitude.*

6. **Pai, N.G. and Hess, D.P.** (2002). "Three-Dimensional Finite Element Analysis of Threaded Fastener Loosening Due to Dynamic Shear Load." *Engineering Failure Analysis*, Vol. 9, No. 4, pp. 383--402. DOI: [10.1016/S1350-6307(01)00024-3](https://doi.org/10.1016/S1350-6307(01)00024-3). -- *FEA analysis of loosening that provides benchmark data for validating scaled model predictions.*

7. **Kuguel, R.** (1961). "A Relation Between Theoretical Stress Concentration Factor and Fatigue Notch Factor Deduced from the Concept of Highly Stressed Volume." *Proceedings ASTM*, Vol. 61, pp. 732--748. -- *Introduces the highly stressed volume concept that explains statistical size effects in fatigue, directly relevant to thread root scaling.*

8. **Barenblatt, G.I.** (2003). *Scaling*. Cambridge Texts in Applied Mathematics. Cambridge University Press. ISBN: 978-0-521-53394-2. DOI: [10.1017/CBO9780511814921](https://doi.org/10.1017/CBO9780511814921). -- *Rigorous mathematical treatment of scaling laws, self-similarity, and intermediate asymptotics applicable to contact and fracture problems.*

9. **Szirtes, T.** (2007). *Applied Dimensional Analysis and Modeling*, 2nd ed. Elsevier/Butterworth-Heinemann. ISBN: 978-0-12-370620-1. -- *Practical guide to dimensional analysis and the construction of dimensionless groups for engineering problems.*

10. **Jiang, Y., Zhang, M., and Lee, C.-H.** (2003). "A Study of Early Stage Self-Loosening of Bolted Joints." *ASME Journal of Mechanical Design*, Vol. 125, No. 3, pp. 518--526. DOI: [10.1115/1.1586936](https://doi.org/10.1115/1.1586936). -- *Two-stage loosening model providing the physical basis for cycle-dependent behavior that must be preserved in scaled testing.*

11. **Hintikka, J., Lehtovaara, A., and Mantyla, A.** (2020). "Running-in in Fretting, Transition from Near-Stable Friction Regime to Gross Sliding." *Tribology International*, Vol. 143, Art. 106073. DOI: [10.1016/j.triboint.2019.106073](https://doi.org/10.1016/j.triboint.2019.106073). -- *Friction evolution model demonstrating contact-pressure-dependent behavior that introduces scale effects in tribological similitude.*

---

*Part IX of the Bolt Analysis Studio MSD Framework Documentation. Implements `core/similitude/similitude.py` and `core/similitude/similitude_plots.py`.*

*LTAD/UFU -- Petrobras R&D Project, 2026.*
