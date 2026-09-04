# MSD Framework -- PART VI: WEAR MODELS

**Complete Technical Reference for Bolt Analysis Studio**

**Authors:** L. Ribeiro, D. Carvalho, S.C. Naves, T. Santos, V. Marques, G. Arruda
**Institution:** internal reference laboratory
**Project:** Petrobras R&D -- Bolted Flange Joint Integrity

---

**Abstract.** Wear at contact interfaces in bolted joints, though producing material removal on the order of micrometers, translates directly into preload loss through the joint's finite stiffness: $\Delta F_p = k_{sys} \cdot h_{total}$. This document provides the complete mathematical treatment of all wear models implemented in the Bolt Analysis Studio. Starting from the classical Archard adhesive/abrasive law (Archard, 1953), we develop the generalized power-law extension (Goryacheva, 1998), the Fouvry energy-based fretting model (Fouvry et al., 2003), and a synergistic combined model that captures both Archard and energy-based contributions. Fretting wear at thread interfaces is treated following McColl et al. (2004), with attention to the unique geometry and load distribution of engaged threads. A four-phase wear evolution model tracks the transition from running-in through steady-state, severe, and catastrophic regimes, with phase-dependent wear coefficients and S-curve smoothing between transitions. The bidirectional coupling between wear and preload -- wear reduces preload, lower preload increases slip amplitude, which accelerates wear -- establishes a positive feedback loop that can transition a joint from stable operation to runaway loosening. Wear-limited joint life prediction completes the treatment, providing the tools to estimate the number of cycles before wear-induced preload loss exceeds a specified threshold. All models include temperature and hardness corrections and are linked to the coupled analysis framework of Part XI.

---

## Table of Contents

- [25. Introduction to Wear in Bolted Joints](#25-introduction-to-wear-in-bolted-joints)
- [26. Classical Archard Wear Law](#26-classical-archard-wear-law-archard-1953)
- [27. Generalized Archard Model](#27-generalized-archard-model-goryacheva-1998-bas-implementation)
- [28. Fouvry Energy-Based Wear Model](#28-fouvry-energy-based-wear-model-fouvry-et-al-2003)
- [29. Synergistic Wear Model](#29-synergistic-wear-model-bas-combined-implementation)
- [30. Fretting Wear at Thread Interfaces](#30-fretting-wear-at-thread-interfaces-mccoll-et-al-2004)
- [31. Wear Evolution Model](#31-wear-evolution-model-bas-wearevolutionmodel)
- [32. Wear-Preload Coupling](#32-wear-preload-coupling-nonlinear-compliance-amplification)
- [33. Wear-Geometry Coupling](#33-wear-geometry-coupling)
- [34. Wear-Limited Joint Life Prediction](#34-wear-limited-joint-life-prediction)
- [References](#references)

---

## 25. Introduction to Wear in Bolted Joints

### 25.1 Why Wear Matters for Preload Retention

In a bolted joint subjected to cyclic loading, material is progressively removed from contacting surfaces through wear mechanisms. Although the wear depths involved are characteristically small -- on the order of micrometers to tens of micrometers -- these losses translate directly into preload degradation through the joint's finite stiffness. A bolted joint is, in essence, a compliant spring system: the bolt is stretched and the clamped members are compressed to generate the clamping force. Any reduction in the effective clamped length, however minute, relaxes this stored elastic energy and reduces the preload.

The quantitative relationship is straightforward. For a joint with system stiffness $k_{sys}$, a total wear depth $h_{total}$ accumulated across all interfaces produces a first-order preload loss of:

$$\Delta F_{p,wear} = k_{sys} \cdot h_{total}$$

For typical bolted flange joints in petrochemical service, $k_{sys}$ is on the order of $10^8$ to $10^9$ N/m. Consequently, even $10\ \mu\text{m}$ of total wear across all interfaces can produce preload losses of $1\text{--}10\ \text{kN}$, which is significant relative to typical initial preloads of $30\text{--}100\ \text{kN}$ (Bickford, 2008; Pai and Hess, 2002).

More importantly, wear-induced preload loss creates a positive feedback loop: as preload decreases, the friction capacity at the interfaces decreases, slip becomes easier and more extensive, and the wear rate accelerates. This self-reinforcing mechanism can transition a joint from a stable condition to runaway loosening within relatively few additional cycles.

### 25.2 Wear Locations in a Bolted Joint

Wear occurs at every contacting interface in a bolted joint, but the severity and character differ substantially depending on the interface type:

```
                     BOLT HEAD
                         |
            +------------+------------+
            |            |            |
     +------v------+ +--v---+ +------v------+
     | HEAD-FLANGE | |HEAD- | |  (no ws)    |
     |   BEARING   | |WASHER| |             |
     |   CONTACT   | |BEAR. | |             |
     +-------------+ +--+---+ +-------------+
                         |
              WEAR ZONE 1: BEARING SURFACE
              Gross slip fretting, high contact
              pressure under bolt head.
              Typical K: 1-10 x 10^-6 (lubricated)
                         |
                    +----v----+
                    | WASHER  |
                    +----+----+
                         |
              WEAR ZONE 2: WASHER-FLANGE INTERFACE
              Load spreading, embedding combined
              with micro-slip wear.
              Typical K: 0.5-5 x 10^-6
                         |
    +====================v====================+
    ||           FLANGE 1                    ||
    ||========================================||
    ||                                        ||
    ||   WEAR ZONE 3: FLANGE-GASKET or       ||
    ||   FLANGE-FLANGE INTERFACE              ||
    ||   Metal-to-metal: fretting wear        ||
    ||   With gasket: creep + micro-slip      ||
    ||   Typical K: 0.1-1 x 10^-6            ||
    ||                                        ||
    ||========================================||
    ||           FLANGE 2                    ||
    +=========================================+
                         |
                    (symmetric)
                         |
                    +----v----+        +----------+
                    |   NUT   |<-------|   STUD   |
                    +---------+        +----------+
                         |                   |
                         +-----> THREAD <----+
                               CONTACT
                         (n parallel threads)

              WEAR ZONE 4: THREAD INTERFACES
              Most critical for loosening.
              Non-uniform load distribution.
              Partial slip fretting dominant.
              First thread carries 30-50% of load.
              Typical K: 0.5-5 x 10^-6 (lubricated)
```

### 25.3 Wear Regimes in Bolted Joints

The nature of relative motion between contacting surfaces in a bolted joint determines which wear regime governs. Two fundamentally different regimes exist, and the boundary between them is one of the most important concepts in bolted joint tribology:

**Partial Slip Fretting** ($\delta < 10\ \mu\text{m}$): Under moderate transverse loading, the central portion of each contact interface remains stuck while annular zones at the edges undergo micro-slip. This is the most common regime for well-designed joints. Wear rates are low but damage is concentrated, and the dominant failure mechanism shifts from material removal to surface fatigue and crack initiation. The wear coefficient in this regime is typically one to two orders of magnitude lower than in gross slip.

**Gross Slip** ($\delta > 50\ \mu\text{m}$): When the transverse force exceeds the friction capacity of the interface, the entire contact slides. This is the regime associated with Junker-type self-loosening. Wear rates are high, material removal is substantial, and the positive feedback between wear and preload loss can produce rapid joint degradation.

**Mixed Fretting** ($10\ \mu\text{m} < \delta < 50\ \mu\text{m}$): A transitional regime where both partial slip and gross slip occur during portions of the loading cycle. Behavior is highly variable and depends on the precise loading waveform.

The Vingsbo and Soderberg (1988) fretting map provides a useful framework for identifying the regime:

```
  Wear Rate
  (Volume/cycle)
       |
       |                           /
       |                          /  GROSS SLIP
       |                         /   (Sliding Wear)
       |                        /
       |        Maximum        /
       |        wear      .../
       |        rate     / :
       |              ../  :
       |           ../     :
       |  PARTIAL /  :     :
       |  SLIP   /   :     :
       |  (Fatigue)  :     :
       |       /     :     :
       |      /      :     :
       |    ./       :     :
       +----+--------+-----+---------> Slip Amplitude
            |   10   |  50 |
            |  um    | um  |
```

### 25.4 Industrial Context: Subsea Flanges and Pressure Vessels

In the petrochemical and subsea industries, wear-induced preload loss is a critical integrity concern. Subsea flange joints in risers and wellheads experience millions of loading cycles from wave-induced motion, thermal cycling, and operational pressure fluctuations. The cumulative effect of wear at thread and bearing interfaces can reduce preload below the sealing threshold, leading to leakage of hydrocarbons. API 6A (2018) and ASME PCC-1 (2022) guidelines address bolt retorquing intervals partly to compensate for wear-induced preload loss, but these intervals are often based on operational experience rather than quantitative wear predictions.

Pressure vessel flanges governed by ASME Boiler and Pressure Vessel Code Section VIII experience similar concerns, particularly at elevated temperatures where hardness decreases and wear rates increase. The VDI 2230 (2015) systematic calculation method acknowledges embedding losses (a form of initial wear-related settlement) but does not provide detailed guidance on progressive wear under cyclic loading, motivating the development of the models presented in this document.

---

## 26. Classical Archard Wear Law (Archard, 1953)

### 26.1 Fundamental Formulation

The Archard wear law, first proposed by J.F. Archard in 1953, relates the volume of material removed by wear to the normal force, sliding distance, and hardness of the softer contacting material. Despite its simplicity, it remains the most widely used wear model in engineering practice and serves as the foundation for the more advanced models implemented in Bolt Analysis Studio.

**Volumetric Form:**

$$V = K \cdot \frac{F \cdot s}{H}$$

where:
- $V$ is the total wear volume $[\text{m}^3]$
- $K$ is the dimensionless Archard wear coefficient (probability that an asperity contact produces a wear particle)
- $F$ is the normal contact force $[\text{N}]$
- $s$ is the total sliding distance $[\text{m}]$
- $H$ is the Vickers hardness of the softer material $[\text{Pa}]$

The physical interpretation of $K$ is instructive. Archard derived the model by considering the repeated formation and destruction of asperity junctions. Each time two asperities meet, there is a probability $K$ that a hemispherical wear particle will be detached. The wear coefficient thus encapsulates the entire complexity of the tribological system -- surface chemistry, oxide films, third-body effects, lubrication -- into a single dimensionless number.

**Rate Form (time-domain):**

$$\frac{dV}{dt} = K \cdot \frac{F \cdot v}{H}$$

where $v = ds/dt$ is the instantaneous sliding velocity $[\text{m/s}]$. This form is used in time-stepping numerical integration schemes.

**Depth Form (most useful for bolted joints):**

For uniform wear over a contact area $A$, the wear volume can be expressed as $V = A \cdot h$, giving the wear depth:

$$dh = \frac{K}{H} \cdot p \cdot ds$$

where $p = F/A$ is the contact pressure $[\text{Pa}]$ and $ds$ is the incremental sliding distance. The dimensional wear coefficient $k_w = K/H$ $[\text{m}^2/\text{N}]$ is sometimes used directly:

$$dh = k_w \cdot p \cdot ds$$

This depth form is the most practical for bolted joint analysis because it is the wear depth, not the wear volume, that governs preload loss through the relationship $\Delta F_p = k_{sys} \cdot h$.

### 26.2 Physical Meaning of Each Parameter

**Normal Force $F$:** In a bolted joint, the normal force at thread interfaces equals the preload $F_p$ distributed across the engaged threads according to a load distribution law (see Part II). At the bearing surface, $F = F_p$ acts on the annular contact area. Critically, as preload decreases due to wear, the normal force decreases, creating the aforementioned positive feedback loop.

**Sliding Distance $s$:** For cyclic transverse loading with displacement amplitude $\delta_0$, the sliding distance per cycle is approximately $s_{cycle} \approx 4\delta_0$ (four quarter-cycle traversals). At thread interfaces, the slip distance is reduced by the helix angle and the constraint of the helical geometry.

**Hardness $H$:** The Vickers hardness of the softer surface in contact. For most bolt steel-on-steel contacts, $H \approx 2\text{--}4\ \text{GPa}$. For coated surfaces (zinc, phosphate), the coating hardness governs initially, transitioning to substrate hardness after coating breakthrough.

**Wear Coefficient $K$:** The most uncertain parameter. It can vary over six orders of magnitude depending on the tribological system. The following table provides typical values for bolted joint interfaces.

### 26.3 Typical $K$ Values for Bolt Materials

| Material Pair | Condition | $K\ (\times 10^{-6})$ | Notes |
|---|---|---|---|
| Steel/Steel | Dry | 10--100 | Bare, unlubricated surfaces |
| Steel/Steel | Lubricated (oil) | 1--10 | Standard machine oil |
| Thread contact | Lubricated (anti-seize) | 0.5--5 | MoS$_2$ or PTFE-based paste |
| Bearing surface | Lubricated | 1--10 | Under bolt head or nut |
| Zinc coating on steel | Dry | 50--200 | Sacrificial soft coating |
| Phosphate coating on steel | Dry or oiled | 20--100 | Common bolt finish |
| Cadmium on steel | Lubricated | 5--30 | Aerospace applications |
| PTFE-impregnated | On steel | 0.1--1 | Self-lubricating coatings |
| Stainless/Stainless | Dry | 50--500 | Galling tendency |
| Stainless/Stainless | Lubricated | 5--50 | Anti-galling compound essential |
| Inconel/Inconel | Dry | 30--200 | Subsea, high-temperature |

These values are compiled from Archard (1953), Rabinowicz (1965), Bhushan (2013), and experimental data from internal reference test programs on ASTM A193 B7 and A320 L7 fastener materials.

### 26.4 Per-Cycle Wear for Harmonic Loading

For a bolted joint subjected to sinusoidal transverse displacement $\delta(t) = \delta_0 \sin(2\pi f t)$, the total sliding distance per cycle is:

$$s_{cycle} = 4 \cdot \delta_0$$

The wear depth per cycle is therefore:

$$\Delta h_{cycle} = \frac{K}{H} \cdot p \cdot 4\delta_0$$

And the cumulative wear after $N$ cycles (assuming constant conditions):

$$h(N) = \frac{4K \cdot p \cdot \delta_0}{H} \cdot N$$

This linear accumulation is the simplest model and is adequate for order-of-magnitude estimates, but it neglects the important effects of running-in, surface evolution, and the positive feedback between wear and preload. These effects are addressed by the advanced models in Sections 27--32.

### 26.5 Limitations of the Linear Archard Law

The classical Archard model assumes:

1. **Constant $K$**: In reality, $K$ evolves through distinct phases (running-in, steady-state, severe wear) as the surface topography changes.
2. **Linear pressure dependence**: At high pressures, subsurface plastic deformation and adhesive transfer mechanisms introduce nonlinearity.
3. **Linear velocity dependence**: Fretting contacts exhibit sub-linear velocity dependence because the sliding distance per cycle is constrained.
4. **No feedback**: The model does not inherently capture the coupling between wear and preload, or between wear and friction coefficient evolution.
5. **Single mechanism**: The Archard law implicitly assumes a single dominant wear mechanism, whereas real bolted joint interfaces may experience simultaneous adhesive, abrasive, and oxidative wear.

These limitations motivate the Generalized Archard model (Section 27) and the Fouvry energy-based approach (Section 28).

> **Reference:** Archard, J.F. (1953). "Contact and Rubbing of Flat Surfaces." *Journal of Applied Physics*, Vol. 24, No. 8, pp. 981--988. DOI: [10.1063/1.1721448](https://doi.org/10.1063/1.1721448)

---

## 27. Generalized Archard Model (Goryacheva, 1998; BAS Implementation)

### 27.1 Nonlinear Pressure and Velocity Exponents

The Generalized Archard model, formulated by Goryacheva (1998) and further developed by Argatov and Chai (2022), introduces nonlinear exponents for pressure and velocity dependence, providing a more physically realistic description of wear in complex tribological systems:

$$dh = K \cdot \left(\frac{p}{H}\right)^{\alpha} \cdot v^{\beta} \cdot ds$$

where:
- $\alpha$ is the pressure exponent (BAS default: $\alpha = 1.2$)
- $\beta$ is the velocity exponent (BAS default: $\beta = 0.8$)
- $p = F/A$ is the contact pressure $[\text{Pa}]$
- $v$ is the sliding velocity (or a velocity proxy based on slip distance per cycle) $[\text{m/s}]$
- $K$ is the wear coefficient (phase-dependent, see Section 31)

When $\alpha = 1$ and $\beta = 1$, this reduces exactly to the classical Archard law (with the $1/H$ factor absorbed into the exponent).

### 27.2 Physical Justification of the Exponents

**Pressure exponent $\alpha > 1$ (super-linear pressure dependence):**

At elevated contact pressures, the wear mechanism transitions from purely adhesive asperity removal to a regime where subsurface plastic deformation contributes significantly. The Hertzian stress field beneath a loaded asperity scales nonlinearly with contact pressure, and when the subsurface von Mises stress exceeds the material yield strength, plastic flow nucleates wear particles from beneath the surface rather than only at asperity tips. This produces more wear volume per unit of additional pressure than the linear Archard model predicts.

Mathematically, if the volume of plastically deformed material per asperity contact scales as $\sim p^{3/2}$ (from Hertz theory), while the number of contacting asperities scales as $\sim p^{2/3}$ (from the Greenwood-Williamson model), the net wear rate scales approximately as $p^{1.17}$, which is close to the BAS default of $\alpha = 1.2$.

Typical range: $1.0 \leq \alpha \leq 1.5$

**Velocity exponent $\beta < 1$ (sub-linear velocity dependence):**

In fretting and reciprocating contact -- the dominant motion regime in bolted joints under transverse vibration -- the wear rate per unit sliding distance decreases at higher velocities. This is because:

1. At higher sliding velocities, the contact time per unit distance decreases, reducing the time available for adhesive junction formation.
2. Oxidative wear, which produces protective oxide films, is time-dependent rather than distance-dependent. Faster sliding disrupts oxide films but also moves past any given point before significant adhesion can develop.
3. In bolted joints specifically, higher transverse velocities correspond to higher excitation frequencies, which produce shorter contact dwell times at the reversal points where maximum damage occurs.

Typical range: $0.6 \leq \beta \leq 1.0$

### 27.3 Surface Roughening Feedback

As wear progresses, the surface topography evolves. Initially smooth (machined or ground) surfaces develop wear scars, micro-pits, and transferred material that increase the effective surface roughness. This rougher surface has more and sharper asperities, which increases the local contact pressure at asperity tips and thus accelerates the wear rate. BAS implements this feedback as a multiplicative roughening amplification factor:

$$A = 1 + 0.15 \cdot \frac{h_{\mu m}}{10}$$

where $h_{\mu m}$ is the cumulative wear depth in micrometers. This factor is applied to the Archard wear increment:

$$dh_{effective} = A \cdot dh_{Archard}$$

The factor is capped at a maximum of $3.0\times$ to prevent unbounded growth, reflecting the physical observation that surfaces eventually reach a steady-state roughness (McColl et al., 2004).

The roughening factor of $0.015\ \mu\text{m}^{-1}$ was calibrated against fretting wear data from Hintikka et al. (2020), who measured surface roughness evolution in bolt-like contacts over $10^4$ to $10^5$ cycles.

### 27.4 Implementation in BAS

In Bolt Analysis Studio, the Generalized Archard computation within the `WearModelParams.compute_wear_increment()` method proceeds as follows:

1. The contact pressure is computed as $p = F_n / A_{contact}$.
2. The normalized pressure ratio $(p/H)$ is raised to the power $\alpha$.
3. The slip distance per cycle (a velocity proxy) is raised to the power $\beta$.
4. The product is multiplied by the phase-dependent wear coefficient $K$ (Section 31) and the contact area to convert volume to depth.
5. If current cumulative wear depth is nonzero, the roughening factor $A$ is applied, capped at $3.0\times$.

### 27.5 Parameters Table

| Parameter | Symbol | Default | Typical Range | Units | Physical Meaning |
|---|---|---|---|---|---|
| Pressure exponent | $\alpha$ | 1.2 | 1.0--1.5 | -- | Nonlinearity of pressure effect |
| Velocity exponent | $\beta$ | 0.8 | 0.6--1.0 | -- | Sub-linear velocity scaling |
| Wear coefficient | $K$ | $1 \times 10^{-6}$ | $10^{-7}$ to $10^{-4}$ | -- | Phase-dependent (Section 31) |
| Hardness | $H$ | $2 \times 10^{9}$ | $1$--$5 \times 10^{9}$ | Pa | Vickers hardness of softer surface |
| Contact area | $A$ | $1 \times 10^{-4}$ | $10^{-5}$ to $10^{-3}$ | m$^2$ | Nominal contact area |
| Roughening rate | -- | 0.015 $\mu\text{m}^{-1}$ | 0.005--0.03 | $\mu\text{m}^{-1}$ | Surface roughening per $\mu$m of wear |
| Roughening cap | -- | 3.0 | 2.0--5.0 | -- | Maximum roughening amplification |

> **Reference:** Goryacheva, I.G. (1998). *Contact Mechanics in Tribology.* Solid Mechanics and Its Applications, Vol. 61. Kluwer Academic Publishers. DOI: [10.1007/978-94-015-9048-8](https://doi.org/10.1007/978-94-015-9048-8)
>
> **Reference:** Argatov, I.I. and Chai, Y.S. (2022). "Wear Contact Problem with Friction: Steady-State Regime and Wearing-In Period." *International Journal of Solids and Structures*, Vol. 253, Art. 111757. DOI: [10.1016/j.ijsolstr.2022.111757](https://doi.org/10.1016/j.ijsolstr.2022.111757)

---

## 28. Fouvry Energy-Based Wear Model (Fouvry et al., 2003)

### 28.1 Fundamental Concept: Wear Proportional to Dissipated Energy

The Fouvry energy-based wear model represents a fundamentally different philosophy from the Archard approach. Rather than relating wear to the mechanical quantities of force and distance separately, it relates wear to the friction energy dissipated at the contact interface. The physical reasoning is that wear is the result of energy being deposited into the surface material, and the total dissipated energy is the most natural measure of this input regardless of how it was generated.

The basic relation is:

$$V = \alpha_V \cdot E_d$$

where:
- $V$ is the total wear volume $[\text{m}^3]$
- $\alpha_V$ is the energy wear coefficient $[\text{m}^3/\text{J}]$
- $E_d$ is the total dissipated friction energy $[\text{J}]$

The dissipated energy per cycle is the area enclosed by the friction force--displacement hysteresis loop. This is computed as:

$$E_d = \oint F_f \cdot ds = \int_0^T F_f(t) \cdot \dot{s}(t)\, dt$$

### 28.2 Energy per Cycle for Harmonic Loading

For a sinusoidal transverse displacement $\delta(t) = \delta_0 \sin(\omega t)$ with gross slip (Coulomb friction at coefficient $\mu$), the friction force--displacement loop is a parallelogram and the dissipated energy per cycle is:

$$E_{d,cycle} = \pi \cdot \mu \cdot F_n \cdot \delta_0$$

This compact expression encapsulates the combined effects of friction coefficient, normal force, and displacement amplitude into a single energy quantity. Note that $\pi$ appears because the full integral of $\sin(\theta)\cos(\theta)$ over one cycle of a parallelogram-shaped hysteresis loop evaluates to $\pi$ times the product of the force and displacement amplitudes.

For non-harmonic or partial-slip conditions, the energy must be computed numerically from the actual hysteresis loop, which BAS performs during time integration.

### 28.3 Energy Threshold (BAS Implementation)

Experimental observations by Fouvry et al. (2003) and subsequent work by Paulin et al. (2008) demonstrate that wear does not initiate until a threshold energy has been dissipated. Below this threshold, the surface accommodates the imposed deformation through elastic and reversible plastic deformation without producing detachable wear particles. BAS implements this as:

$$V = \alpha_V \cdot \max\!\left(0,\; E_d - E_{th}\right)$$

where $E_{th}$ is the energy threshold $[\text{J}]$. In the BAS implementation, the threshold is applied on a per-cycle basis by dividing $E_{th}$ by the current cycle count to distribute the activation energy across the loading history:

$$E_{effective} = \max\!\left(0,\; E_{d,cycle} - \frac{E_{th}}{N}\right)$$

This formulation ensures that early cycles (small $N$) must overcome a proportionally larger threshold, which is physically consistent with the observation that initial cycles require more energy to initiate wear (surface oxide films, work-hardened layers, etc.).

### 28.4 Energy Acceleration at High Dissipation

As cumulative dissipated energy grows, the surface progressively degrades: oxide layers are disrupted, work-hardened material is removed, and fresh reactive surfaces are exposed. BAS models this as a logarithmic acceleration of the effective wear coefficient:

$$\alpha_{eff} = \alpha_V \cdot \left(1 + 0.3 \cdot \ln\!\left(1 + \frac{E_d}{E_0}\right)\right)$$

In the BAS implementation, the acceleration factor uses the ratio of accumulated energy to current-cycle dissipation as the scaling variable:

$$\text{energy\_acceleration} = 1.0 + 0.1 \cdot \ln\!\left(1 + \frac{\Sigma E_d}{1000 \cdot E_{d,cycle}}\right)$$

This factor is capped at $2.5\times$ to prevent unrealistic wear predictions. The logarithmic form ensures slow initial growth with accelerating contribution as the surface degrades over many thousands of cycles.

### 28.5 Advantages over Archard

The energy-based approach offers several important advantages for bolted joint analysis:

1. **Consistency across conditions:** A single value of $\alpha_V$ often characterizes a material pair across a wide range of normal forces, displacement amplitudes, and frequencies. In contrast, the Archard coefficient $K$ must often be adjusted for different loading conditions.

2. **Natural accounting for friction variations:** Because the dissipated energy incorporates the friction coefficient directly, any evolution of friction over cycles (running-in, degradation) is automatically reflected in the wear prediction without requiring explicit coupling.

3. **Better for fretting wear:** In the partial slip regime, the Archard model struggles because the slip distance is difficult to define (it varies across the contact zone). The energy approach naturally handles this because the dissipated energy integrates over the entire contact.

4. **Single parameter often sufficient:** For preliminary design, a single value of $\alpha_V$ (with appropriate energy threshold) provides reasonable wear predictions without the need for separate hardness, coefficient, and area parameters.

### 28.6 $\alpha_V$ Values for Bolted Joint Materials

| Material Pair | Condition | $\alpha_V\ [\text{m}^3/\text{J}]$ | Reference |
|---|---|---|---|
| Steel/Steel (mild) | Dry | $1\text{--}5 \times 10^{-10}$ | Fouvry et al. (2003) |
| Steel/Steel (hardened) | Dry | $5\text{--}50 \times 10^{-11}$ | Fouvry et al. (2003) |
| Steel/Steel | Lubricated | $1\text{--}10 \times 10^{-11}$ | Paulin et al. (2008) |
| Stainless/Stainless | Dry | $2\text{--}20 \times 10^{-10}$ | Heredia and Bielsa (2012) |
| Ti-6Al-4V/Ti-6Al-4V | Dry | $5\text{--}50 \times 10^{-10}$ | Fouvry et al. (2003) |
| Inconel 718 | Elevated temp. | $1\text{--}10 \times 10^{-10}$ | Estimated |

The BAS default value is $\alpha_V = 5 \times 10^{-11}\ \text{m}^3/\text{J}$, which is appropriate for lubricated steel-on-steel thread contacts typical of ASTM A193 B7 fasteners with anti-seize compound.

### 28.7 Conversion to Wear Depth

The energy wear model produces a volumetric wear rate. For a contact of area $A$, the wear depth increment is:

$$dh_{energy} = \frac{dV_{energy}}{A} = \frac{\alpha_V \cdot E_{effective}}{A}$$

This depth is directly comparable to the Archard depth and can be combined with it as described in Section 29.

> **Reference:** Fouvry, S., Liskiewicz, T., Kapsa, Ph., Hannel, S., and Sauger, E. (2003). "An Energy Description of Wear Mechanisms and Its Applications to Oscillating Sliding Contacts." *Wear*, Vol. 255, No. 1--6, pp. 287--298. DOI: [10.1016/S0043-1648(03)00117-0](https://doi.org/10.1016/S0043-1648(03)00117-0)
>
> **Reference:** Paulin, C., Fouvry, S., and Deyber, S. (2008). "Wear Kinetics of Ti-6Al-4V under Constant and Variable Fretting Sliding Conditions." *Wear*, Vol. 265, No. 11--12, pp. 1440--1449. DOI: [10.1016/j.wear.2008.01.036](https://doi.org/10.1016/j.wear.2008.01.036)

---

## 29. Synergistic Wear Model (BAS Combined Implementation)

### 29.1 Rationale for Combining Archard and Fouvry

The Archard model (Section 26--27) captures wear driven by mechanical contact pressure and sliding distance, while the Fouvry model (Section 28) captures wear driven by dissipated friction energy. In a real bolted joint interface, both mechanisms operate simultaneously but with different relative importance depending on conditions:

- At **high contact pressures and moderate slip**, the Archard mechanism dominates because subsurface plastic deformation generates wear particles irrespective of friction energy.
- At **moderate pressures and large slip amplitudes**, the Fouvry mechanism dominates because the large hysteresis loops dissipate substantial energy into surface damage.
- At **intermediate conditions** (the most common case in bolted joints), both mechanisms contribute comparably.

Moreover, the two mechanisms are not independent. Mechanically-generated wear debris (Archard) acts as a third body that increases friction energy dissipation (Fouvry). Conversely, energy-driven surface degradation creates stress concentrators that promote mechanical delamination.

### 29.2 BAS Synergistic Combination Formula

BAS combines the Archard and Fouvry wear increments using a synergistic formula that is neither purely additive nor purely based on the maximum:

$$dh_{total} = \sqrt{dh_{Archard}^2 + dh_{energy}^2} + 0.2 \cdot \min\!\left(dh_{Archard},\; dh_{energy}\right)$$

This formula has two terms:

**Geometric mean term** $\sqrt{dh_A^2 + dh_E^2}$: This treats the two mechanisms as independent contributors whose combined effect follows a Pythagorean-style composition. When one mechanism dominates heavily (e.g., $dh_A \gg dh_E$), the result is approximately $dh_A$. When both contribute equally, the result is $\sqrt{2} \approx 1.41$ times either one, reflecting the genuine increase in total wear when two independent mechanisms operate simultaneously.

**Synergistic interaction term** $0.2 \cdot \min(dh_A, dh_E)$: This adds a synergistic enhancement proportional to the weaker mechanism. The coefficient 0.2 reflects the experimental observation (Fouvry et al., 2003; McColl et al., 2004) that the interaction between mechanisms enhances total wear by approximately 10--30% beyond what either mechanism alone would predict. Using the minimum ensures the synergistic term is bounded by the smaller contributor and does not produce unrealistically large enhancement when one mechanism dominates.

### 29.3 Behavior in Limiting Cases

```
  Total Wear
  dh_total
       |
       |                              .
       |                           ..
       |                        ..    Synergistic
       |                     ..       (both contribute)
       |                  ..
       |               ..     - - - - Additive (dh_A + dh_E)
       |            ..   .........
       |         ..  ...
       |      .. ...      Geometric mean
       |   .....          sqrt(dh_A^2 + dh_E^2)
       | ..
       |.
       +-----------------------------------> dh_A / dh_E ratio
       0         1.0        2.0       3.0
```

When $dh_A = dh_E$ (ratio = 1.0):
- Geometric mean: $\sqrt{2} \cdot dh_A = 1.414 \cdot dh_A$
- Synergistic term: $0.2 \cdot dh_A$
- Total: $1.614 \cdot dh_A$ (compared to $2.0 \cdot dh_A$ for pure addition)

When $dh_A = 10 \cdot dh_E$ (ratio = 10):
- Geometric mean: $\sqrt{101} \cdot dh_E \approx 10.05 \cdot dh_E$
- Synergistic term: $0.2 \cdot dh_E$
- Total: $\approx 10.25 \cdot dh_E$ (essentially just $dh_A$, as expected)

### 29.4 Diagram: Mechanism Dominance Regimes

```
  +---------------------------------------------------------------+
  |                                                               |
  |   HIGH PRESSURE                                               |
  |   LOW SLIP           ARCHARD DOMINATES                        |
  |                       dh_A >> dh_E                            |
  |                       dh_total ~ dh_A                         |
  |                                                               |
  |   p > 200 MPa                                                 |
  |   delta < 20 um                                               |
  |                                                               |
  +---------------------------------------------------------------+
  |                                                               |
  |   MODERATE PRESSURE                                           |
  |   MODERATE SLIP       SYNERGISTIC REGIME                      |
  |                       dh_A ~ dh_E                             |
  |                       dh_total ~ 1.6 * max(dh_A, dh_E)       |
  |                                                               |
  |   50 < p < 200 MPa                                            |
  |   20 < delta < 100 um                                         |
  |                                                               |
  +---------------------------------------------------------------+
  |                                                               |
  |   LOW PRESSURE                                                |
  |   HIGH SLIP           FOUVRY DOMINATES                        |
  |                       dh_E >> dh_A                            |
  |                       dh_total ~ dh_E                         |
  |                                                               |
  |   p < 50 MPa                                                  |
  |   delta > 100 um                                              |
  |                                                               |
  +---------------------------------------------------------------+
```

---

## 30. Fretting Wear at Thread Interfaces (McColl et al., 2004)

### 30.1 Fretting Wear Regimes in Thread Contacts

Thread interfaces in bolted joints experience a special form of fretting wear because the relative motion is constrained by the helical geometry, the load is non-uniformly distributed across the engaged threads, and the contact conditions vary dramatically from the first loaded thread (adjacent to the bearing surface of the nut) to the last engaged thread.

The concept of fretting maps, introduced by Vingsbo and Soderberg (1988) and applied to bolted joints by McColl et al. (2004), identifies three distinct regimes based on the slip amplitude at each thread:

| Regime | Slip Amplitude | Wear Rate | Dominant Mechanism | $K_{eff}$ Relative to $K$ |
|---|---|---|---|---|
| Partial Slip | $< 10\ \mu\text{m}$ | Low | Surface fatigue, micro-cracking | $K_{eff} = 0.1 \cdot K$ |
| Mixed Fretting | $10\text{--}50\ \mu\text{m}$ | Variable | Combined fatigue + abrasion | $K_{eff} = 0.5 \cdot K$ |
| Gross Slip | $> 50\ \mu\text{m}$ | High | Sliding wear (Archard-type) | $K_{eff} = K$ |

The transition between partial slip and gross slip is one of the most important phenomena in fretting tribology. In partial slip, the central "stuck" zone shields the interface from gross material loss, and damage manifests primarily as surface fatigue cracks. In gross slip, the entire contact slides and conventional sliding wear governs. The mixed regime exhibits the highest damage rates per unit energy because the contact alternates between sticking and sliding, producing high stress gradients at the stick-slip boundary.

### 30.2 Per-Thread Fretting Analysis

In a bolted joint with $n$ engaged threads, the load is distributed non-uniformly according to a load distribution law (equal, linear, power, exponential, or Yamamoto -- see Part II, Section 10). The first thread adjacent to the nut bearing surface carries the largest fraction of the preload, and consequently experiences the highest contact pressure and the smallest slip amplitude (it is most constrained). Conversely, the last engaged thread carries the least load but may experience the largest relative displacement.

For thread $i$ with load fraction $\phi_i$:

$$F_i = \phi_i \cdot F_p$$

$$p_i = \frac{F_i}{A_{thread,i}}$$

The slip amplitude at thread $i$ depends on the local compliance and the applied transverse displacement. A simplified estimate is:

$$\delta_i \approx \delta_{trans} \cdot \frac{z_i}{L_{engaged}}$$

where $z_i$ is the axial position of thread $i$ measured from the nut bearing face and $L_{engaged}$ is the total engaged length. This reflects the observation that threads further from the bearing face experience larger relative displacements due to bolt bending.

Each thread independently falls into one of the three fretting regimes, and the effective wear coefficient at each thread is adjusted accordingly:

$$K_{eff,i} = \begin{cases}
0.1 \cdot K & \text{if } \delta_i < 10\ \mu\text{m (partial slip)} \\
0.5 \cdot K & \text{if } 10\ \mu\text{m} \leq \delta_i < 50\ \mu\text{m (mixed)} \\
K & \text{if } \delta_i \geq 50\ \mu\text{m (gross slip)}
\end{cases}$$

### 30.3 Non-Uniform Wear Pattern

The combination of non-uniform load distribution and position-dependent slip amplitude produces a characteristic non-uniform wear pattern across the engaged threads:

```
  Wear Depth (um)
       |
   8.0 |                                          *
       |                                       *
   6.0 |                                    *
       |                                 *
   4.0 |                              *
       |                          * *
   2.0 |                      * *
       |                  * *
   1.0 |           * * *
       |  * * * *
   0.0 +--+--+--+--+--+--+--+--+--+--+----> Thread Number
       1  2  3  4  5  6  7  8  9  10
       |<- High load,     Low load, ->|
       |   small slip     large slip  |
       |   PARTIAL SLIP   GROSS SLIP  |
```

Thread 1 (most loaded): High pressure but constrained slip. Partial slip regime. Wear is low but fatigue damage accumulates.

Threads in the middle: Moderate pressure and moderate slip. Mixed fretting regime. May exhibit the highest damage rate per unit energy.

Last threads (least loaded): Low pressure but largest slip. Gross slip regime. Material removal is highest in absolute terms.

The total effective wear depth for the thread contact is the load-weighted sum:

$$h_{thread,total} = \sum_{i=1}^{n} \phi_i \cdot h_i$$

This weighted sum reflects the contribution of each thread to the overall change in bolt elongation. The BAS implementation in `CoupledLooseningAnalyzer` uses half the bearing-surface slip distance for the thread contact wear calculation, reflecting the geometric constraint imposed by the helical thread path.

### 30.4 Implications for Joint Design

The fretting wear analysis reveals that:

1. **Increasing the number of engaged threads** distributes the load more uniformly, reducing the maximum per-thread contact pressure and wear rate.
2. **Thread lubrication** (anti-seize, MoS$_2$) reduces $K$ by one to two orders of magnitude and is the single most effective measure against thread wear.
3. **Lock nuts** (double nut configurations) experience independent fretting at each nut-stud interface, and both must be accounted for in the total wear budget.

> **Reference:** McColl, I.R., Ding, J., and Leen, S.B. (2004). "Finite Element Simulation and Experimental Validation of Fretting Wear." *Wear*, Vol. 256, No. 11--12, pp. 1114--1127. DOI: [10.1016/j.wear.2003.07.001](https://doi.org/10.1016/j.wear.2003.07.001)
>
> **Reference:** Vingsbo, O. and Soderberg, S. (1988). "On Fretting Maps." *Wear*, Vol. 126, No. 2, pp. 131--147. DOI: [10.1016/0043-1648(88)90134-2](https://doi.org/10.1016/0043-1648(88)90134-2)

---

## 31. Wear Evolution Model (BAS WearEvolutionModel)

### 31.1 Four Wear Phases

The BAS WearEvolutionModel captures the experimentally observed evolution of wear rate over the lifetime of a bolted joint. Rather than using a constant wear coefficient, the model transitions through four distinct phases, each with its own characteristic wear coefficient. This approach was motivated by the experimental observations of Hintikka et al. (2020), who demonstrated that bolt-like contacts exhibit a pronounced running-in phase followed by a transition to steady-state, and eventually -- if wear is sufficiently severe -- a transition to accelerated damage.

The four phases are:

```
  Wear Coefficient K
  (log scale)
       |
 5e-5  |                                              .........
       |                                       ......
       |                                ......  PHASE 4:
       |                         ......   CATASTROPHIC
 1e-5  |                  ......          K = 5 x 10^-5
       |           ......
       |     .....   PHASE 3: SEVERE
       |  ...        K = 1 x 10^-5
       |
 5e-6  |**
       | **  PHASE 1:
       |  ** RUNNING-IN
       |   ** K = 5 x 10^-6
 1e-6  |    *****
       |         ********************************
       |              PHASE 2: STEADY-STATE
       |              K = 1 x 10^-6
       +--+--------+------------------+---------+-------->
          0       100                 h=50um   h=100um
                cycles                wear depth thresholds
```

**Phase 1 -- Running-In** (0 to ~100 cycles, $K = K_{running\_in} = 5 \times 10^{-6}$):

During the initial loading cycles, the high points of the machined or ground surface are plastically deformed and removed. This running-in process produces a relatively high wear rate that decreases as the surface conforms. The transition follows an S-curve (smooth Hermite interpolation) from $K_{running\_in}$ to $K_{steady}$:

$$K_{base}(N) = K_{running\_in} - \left(K_{running\_in} - K_{steady}\right) \cdot S\!\left(\frac{N}{N_{running\_in}}\right)$$

where $S(x) = 3x^2 - 2x^3$ is the smoothstep function that provides a gradual, physically realistic transition (avoiding discontinuities in the wear rate derivative).

**Phase 2 -- Steady-State** (after running-in, $h < 50\ \mu\text{m}$, $K = K_{steady} = 1 \times 10^{-6}$):

The surface has reached a quasi-equilibrium topography. The wear rate is approximately constant per unit sliding distance. This is the phase that governs the majority of the joint's operational life under normal conditions.

**Phase 3 -- Severe Wear** ($h > 50\ \mu\text{m}$, $K = K_{severe} = 1 \times 10^{-5}$):

When the cumulative wear depth exceeds a threshold (default: $50\ \mu\text{m}$), the surface enters a severe wear regime. The coating (if present) has been penetrated, the work-hardened surface layer has been removed, and the softer substrate is exposed. The wear coefficient increases by an order of magnitude. The transition from steady-state to severe is interpolated linearly with wear depth.

**Phase 4 -- Catastrophic Wear** ($h > 100\ \mu\text{m}$, $K = K_{catastrophic} = 5 \times 10^{-5}$):

Beyond $100\ \mu\text{m}$ of cumulative wear, the joint has entered a failure condition. Surface pitting, delamination, and possible thread damage produce very high wear rates. This phase serves primarily as a diagnostic indicator that the joint has exceeded its useful life.

### 31.2 Running-In Acceleration Factor

The running-in phase deserves special attention because it can account for a disproportionate fraction of the total wear in a joint's life. The BAS `WearEvolutionModel` (in `friction_models.py`) implements the running-in acceleration as:

$$h_{cumulative}(N) = h_{rate} \cdot N \cdot \left(1 + 2 \cdot e^{-N/50}\right)$$

At $N = 0$, the factor in parentheses equals $3.0$, meaning the initial wear rate is three times the steady-state rate. By $N = 50$ cycles, the factor has decayed to $1 + 2e^{-1} \approx 1.74$. By $N = 150$ cycles, it is approximately $1.10$, and the wear rate is essentially at its steady-state value.

This exponential running-in model is consistent with the observations of Hintikka et al. (2020), who found that running-in in bolt-like fretting contacts typically completes within 50--200 cycles, depending on surface roughness, hardness, and lubrication.

### 31.3 Temperature Effects on Wear

The BAS WearModelParams includes temperature-dependent hardness reduction, which directly affects the wear rate through the Archard relationship ($dh \propto 1/H$):

$$H_{effective}(T) = H_0 \cdot \max\!\left(0.3,\; 1 - \alpha_T \cdot (T - T_{ref})\right)$$

where:
- $H_0$ is the hardness at the reference temperature $T_{ref} = 20\degree\text{C}$
- $\alpha_T = 0.001\ \text{K}^{-1}$ is the hardness-temperature coefficient (default)
- The factor is capped at a minimum of 0.3 (70% maximum hardness reduction) to prevent non-physical behavior

The effective wear coefficient at elevated temperature is then:

$$K_{T} = \frac{K_{base}}{H_{effective}/H_0} = K_{base} \cdot \frac{1}{1 - \alpha_T \cdot \Delta T}$$

For a $200\degree\text{C}$ temperature rise, $K_T \approx 1.25 \cdot K_{base}$, indicating a 25% increase in wear rate. This is significant for bolted joints in pressure vessels and turbine applications.

### 31.4 Fretting Enhancement Factor

When the slip amplitude is in the fretting regime ($\delta < 10 \cdot \delta_{threshold}$ where $\delta_{threshold} = 5\ \mu\text{m}$ by default), the wear coefficient is multiplied by a fretting enhancement factor (default: 1.5). This accounts for the observation that fretting produces more damage per unit sliding distance than gross sliding, due to the accumulation of trapped wear debris, oxide formation at the contact boundary, and cyclic stress concentrations at the stick-slip transition zone.

> **Reference:** Hintikka, J., Lehtovaara, A., Makinen, A., and Frondelius, T. (2020). "Running-in in Fretting, Transition from Near-Stable Friction Regime to Gross Sliding." *Tribology International*, Vol. 143, Art. 106073. DOI: [10.1016/j.triboint.2019.106073](https://doi.org/10.1016/j.triboint.2019.106073)

---

## 32. Wear-Preload Coupling (Nonlinear Compliance Amplification)

### 32.1 The Central Problem

The relationship between wear depth and preload loss is the key coupling that determines whether a bolted joint will maintain its integrity under cyclic loading. The simplest model assumes a linear relationship:

$$\Delta F_p = k_{sys} \cdot h_{wear}$$

where $k_{sys} = k_{bolt} \cdot k_{member} / (k_{bolt} + k_{member})$ is the system stiffness of the bolt-member series combination. This linear model is adequate for small wear depths (first few micrometers) but becomes increasingly inaccurate as wear progresses, for reasons explained below.

### 32.2 Nonlinear Compliance Amplifier (BAS Implementation)

As material is removed from contacting surfaces, the contact geometry changes in ways that increase the effective compliance of the joint beyond what simple material removal would predict:

1. **Contact area redistribution:** Wear changes the conformity of the contacting surfaces. Initially flat (or slightly crowned) surfaces develop wear scars that alter the pressure distribution, creating local stress concentrations that accelerate further wear.

2. **Thread geometry degradation:** In thread contacts, wear on the thread flanks changes the effective pitch diameter and flank angle, altering the helix coupling between axial and torsional DOFs.

3. **Surface layer removal:** Removal of hardened surface layers, coatings, and oxide films exposes softer substrate material with different elastic properties.

BAS implements a nonlinear compliance amplifier that captures these effects through a polynomial expansion:

$$\Delta F_p = k_{sys} \cdot h \cdot \left(1 + \gamma \cdot h_{\mu m} + \frac{1}{2}\left(\gamma \cdot h_{\mu m}\right)^2\right)$$

where:
- $h$ is the total wear depth $[\text{m}]$
- $h_{\mu m} = h \times 10^6$ is the wear depth in micrometers (for scaling)
- $\gamma = 0.05\ \mu\text{m}^{-1}$ is the compliance growth rate (default)
- The polynomial $(1 + x + x^2/2)$ is the truncated Taylor expansion of $e^x$

The compliance amplifier has the following behavior:

| Wear Depth $h$ | Amplifier Value | Preload Loss Enhancement |
|---|---|---|
| $0\ \mu\text{m}$ | 1.00 | None (linear model) |
| $5\ \mu\text{m}$ | 1.28 | 28% more than linear |
| $10\ \mu\text{m}$ | 1.63 | 63% more than linear |
| $20\ \mu\text{m}$ | 3.00 | 200% more than linear |
| $50\ \mu\text{m}$ | 8.13 | 713% more than linear |
| $100\ \mu\text{m}$ | 26.0 | 2500% more than linear |

The rapid growth of the amplifier at large wear depths captures the physical reality that severely worn joints experience disproportionately large preload losses. This is the mechanism by which wear-induced loosening transitions from a gradual process to a catastrophic one.

### 32.3 Graphical Comparison: Linear vs. Nonlinear

```
  Preload Loss
  Delta_F (kN)
       |
  50   |                                              /
       |                                            /
  40   |                                          /  Nonlinear
       |                                        /   (BAS model)
  30   |                                      /
       |                                    /
  20   |                                 ./
       |                              ../
  10   |                          .../
       |                     ..../..............  Linear
   5   |               ...../...               (k_sys * h)
       |          ...../..
   1   |     .../..
       | ../..
       +--+--------+--------+--------+-------->
          0       25       50       75      100
                  Wear Depth h (um)
```

The divergence between the linear and nonlinear models becomes significant around $h \approx 10\ \mu\text{m}$ and dramatic beyond $h \approx 30\ \mu\text{m}$. For joints with typical system stiffness ($k_{sys} \sim 10^8\ \text{N/m}$), a wear depth of $20\ \mu\text{m}$ produces:

- Linear model: $\Delta F_p = 10^8 \times 20 \times 10^{-6} = 2.0\ \text{kN}$
- Nonlinear model: $\Delta F_p = 10^8 \times 20 \times 10^{-6} \times 3.0 = 6.0\ \text{kN}$

The factor-of-three difference can determine whether a joint remains above its sealing threshold.

### 32.4 Hyperbolic Stiffness Degradation

An alternative perspective on the same physics is to model the effective joint stiffness as decreasing with wear depth. BAS implements this in the `WearEvolutionModel` class using a hyperbolic degradation:

$$k(h) = \frac{k_0}{1 + \gamma \cdot h}$$

where $k_0$ is the initial (unworn) stiffness and $\gamma$ is the same compliance growth rate parameter.

This hyperbolic form has a critical advantage over the linear alternative $k(h) = k_0(1 - \gamma h)$: it naturally remains positive for all values of $h$. The linear form becomes zero at $h = 1/\gamma$ and negative beyond, which is non-physical. The hyperbolic form asymptotically approaches zero but never reaches it, correctly reflecting that a worn joint retains some stiffness as long as material remains in contact.

The preload at wear depth $h$ is then:

$$F_p(h) = F_{p,0} \cdot \frac{k(h)}{k_0} = \frac{F_{p,0}}{1 + \gamma \cdot h}$$

The BAS implementation caps the stiffness reduction at 70% ($k \geq 0.3 k_0$) to prevent numerical issues and to reflect the reality that other mechanisms (bolt relaxation, gasket creep) will dominate before stiffness drops below this level.

### 32.5 The Positive Feedback Loop

The most critical aspect of wear-preload coupling is the positive feedback loop it creates:

```
  +-----------+     less clamping    +----------+
  |           | <------------------- |          |
  | LOWER     |                      |  WEAR    |
  | PRELOAD   | ------------------> | INCREASES |
  |           |     more slip        |          |
  +-----------+                      +----------+
       |                                  ^
       |     less friction                |
       |     resistance                   |
       v                                  |
  +-----------+     larger slip      +----------+
  |           | ------------------> |          |
  | REDUCED   |     amplitude       | HIGHER   |
  | FRICTION  |                     | SLIP     |
  | CAPACITY  |                     | DISTANCE |
  |           | <------------------ |          |
  +-----------+     worn surface    +----------+
                    roughens, then
                    polishes
```

This feedback loop is captured quantitatively in the BAS `CoupledLooseningAnalyzer`:

1. **Wear reduces preload** (Section 32.2 nonlinear amplifier)
2. **Lower preload reduces friction capacity** ($F_{friction} = \mu \cdot F_p$)
3. **Lower friction capacity allows more slip** (Junker criterion)
4. **More slip produces more wear** (Archard: $dh \propto s$)
5. **Go to step 1**

The coupled analyzer solves this loop at each cycle, updating all state variables self-consistently. The nonlinear compliance amplifier ensures that the loop accelerates appropriately at high wear depths, producing the characteristic transition from gradual preload loss (Stage I) to rapid loosening (Stage II/runaway) observed in Junker tests (Junker, 1969; Jiang et al., 2003).

> **Reference:** Pai, N.G. and Hess, D.P. (2002). "Three-Dimensional Finite Element Analysis of Threaded Fastener Loosening Due to Dynamic Shear Load." *Engineering Failure Analysis*, Vol. 9, No. 4, pp. 383--402. DOI: [10.1016/S1350-6307(01)00024-3](https://doi.org/10.1016/S1350-6307(01)00024-3)

---

## 33. Wear-Geometry Coupling

### 33.1 The Feedback Loop

Wear and contact geometry are coupled through a feedback loop that can either amplify or attenuate the wear process depending on the contact configuration:

```
     +-------------------------------------------------------------+
     |                                                             |
     |   +--------------+     +-----------------------+            |
     |   |              |     |                       |            |
     +-->|    WEAR      |---->|   GEOMETRY CHANGE     |--------+   |
         |              |     |                       |        |   |
         |  dh = f(p,v) |     |  * Profile evolution  |        |   |
         |              |     |  * Area expansion     |        |   |
         +--------------+     |  * Conformity change  |        |   |
                              +-----------+-----------+        |   |
                                          |                    |   |
                                          v                    |   |
                              +-----------------------+        |   |
                              |                       |        |   |
                              |  PRESSURE REDISTR.    |        |   |
                              |                       |        |   |
                              |  p_new = F / A(h)     |--------+   |
                              |                       |            |
                              |  Stress concentration |            |
                              |  relief or increase   |            |
                              +-----------------------+            |
                                                                   |
     <-------------------------------------------------------------+
```

### 33.2 Contact Area Expansion with Wear

As material is removed from contacting surfaces, the contact area generally expands. For an initially point-like or line-like contact (such as a thread flank), wear flattens the high spots and increases the conformity between the surfaces. BAS models this as:

$$A(h) = A_0 \cdot \left(1 + 0.1 \cdot \frac{h}{t_0}\right)$$

where $A_0$ is the initial contact area and $t_0$ is the initial effective thickness of the contact region. The coefficient 0.1 is conservative; some experimental observations suggest values up to 0.3 for initially non-conformal contacts.

### 33.3 Pressure Concentration Relief

The expansion of contact area has a direct consequence for the contact pressure:

$$p(h) = \frac{F}{A(h)} = \frac{F}{A_0 \cdot (1 + 0.1 \cdot h/t_0)}$$

As wear depth increases, the pressure decreases (for constant force). Since the Archard wear rate is proportional to pressure ($dh \propto p$), this creates a **negative feedback** that partially stabilizes the wear process. The wear rate decreases as the contact area grows, and the system approaches a steady state where the wear rate is just sufficient to maintain the current geometry.

### 33.4 Self-Limiting Behavior at Moderate Wear

The interplay between the positive feedback (wear-preload coupling, Section 32.5) and the negative feedback (pressure relief through area expansion) determines the overall stability of the joint. At moderate wear depths, the negative feedback can dominate, producing a self-limiting regime where wear slows and preload stabilizes at a reduced but acceptable level. This is the regime where most well-designed joints operate over their service life.

However, if the preload drops below a critical threshold (where the transverse load exceeds the friction capacity), the Junker loosening mechanism activates and the positive feedback of rotational loosening overwhelms the geometric self-limiting effect. This transition marks the boundary between stable operation and incipient failure.

### 33.5 Iterative Solution in BAS

The BAS `WearGeometryCoupling` class solves the coupled wear-geometry problem using a fixed-point iteration at each loading step:

1. Compute wear depth increment at current geometry and pressure.
2. Update contact geometry (area, thickness) based on new cumulative wear.
3. Recompute contact pressure at new geometry.
4. Check convergence (pressure change < tolerance).
5. If not converged, return to step 1.

Convergence is typically achieved in 2--4 iterations due to the weakly nonlinear nature of the coupling (the area expansion coefficient 0.1 ensures that geometry changes are small per step).

---

## 34. Wear-Limited Joint Life Prediction

### 34.1 Cycles to Threshold Preload

The most fundamental life prediction question is: *how many loading cycles can the joint sustain before the preload drops below a critical threshold?* The threshold preload $F_{min}$ is typically determined by the sealing requirement (for gasketted joints) or the loosening criterion (for non-gasketted joints).

**Linear estimate (conservative for small wear):**

$$N_{life} = \frac{F_{p,0} - F_{min}}{k_{sys} \cdot \dot{h}_{cycle}}$$

where $\dot{h}_{cycle}$ is the total wear depth per cycle across all interfaces. This is an upper bound because it neglects the nonlinear compliance amplification (which accelerates preload loss at higher wear depths) and the positive feedback loop.

**Nonlinear estimate (BAS approach):**

With the nonlinear compliance amplifier, the preload loss at wear depth $h$ is:

$$\Delta F_p(h) = k_{sys} \cdot h \cdot \left(1 + \gamma h_{\mu m} + \frac{1}{2}(\gamma h_{\mu m})^2\right)$$

Setting $\Delta F_p = F_{p,0} - F_{min}$ and solving for $h_{max}$ (the maximum allowable wear depth) requires solving a cubic equation. The life is then:

$$N_{life} = \frac{h_{max}}{\dot{h}_{cycle}(N)}$$

where $\dot{h}_{cycle}(N)$ is the cycle-dependent wear rate from the WearEvolutionModel (Section 31). Because $\dot{h}_{cycle}$ varies with cycle count (running-in, steady-state, severe), the life is most accurately determined by the full BAS simulation that integrates the wear, friction, and preload state variables cycle-by-cycle.

### 34.2 Safety Factor Against Wear-Induced Failure

Following the VDI 2230 (2015) philosophy of safety factors for bolted joints, a wear safety factor can be defined as:

$$n_{wear} = \frac{h_{max}}{h_{predicted}(N_{service})}$$

where $h_{predicted}(N_{service})$ is the predicted wear depth at the end of the specified service life. Recommended values:

| Application | $n_{wear}$ Minimum | Justification |
|---|---|---|
| General machinery | $\geq 2.0$ | Moderate consequence of failure |
| Pressure vessels | $\geq 3.0$ | High consequence, inspection intervals |
| Subsea flanges | $\geq 4.0$ | Inaccessible, high consequence |
| Nuclear | $\geq 5.0$ | Safety-critical, long service life |

### 34.3 Comparison with Loosening Life

In a bolted joint under transverse vibration, three mechanisms compete to cause preload loss:

1. **Rotational loosening** (Junker mechanism): Dominates at high transverse displacements ($\delta_0 > 0.3\ \text{mm}$) and low friction coefficients ($\mu < \mu_{crit}$). Produces rapid preload loss (10--50% in hundreds of cycles).

2. **Wear-induced preload loss**: Dominates at moderate transverse displacements and over long service lives ($N > 10^4$ cycles). Produces gradual preload loss that accelerates due to the positive feedback loop.

3. **Embedding and relaxation**: Dominates in the first few cycles (embedding) or over long time periods (stress relaxation). Typically produces 5--15% preload loss.

The BAS `CoupledLooseningAnalyzer` integrates all three mechanisms simultaneously, using the S-curve empirical model (Jiang et al., 2003) for embedding and the physics-based models for rotational loosening and wear. The total preload loss is the maximum of the physics-based sum and the empirical S-curve (blended with appropriate weights), ensuring that both short-term transient effects and long-term wear degradation are captured.

### 34.4 Design Recommendations from Wear Analysis

Based on the wear models implemented in BAS and calibrated against experimental data:

1. **Specify anti-seize or thread lubricant** for all bolted joints subject to cyclic loading. Lubrication reduces $K$ by one to two orders of magnitude and dramatically extends the wear-limited life.

2. **Use phosphate-coated fasteners** as a minimum surface treatment. The phosphate layer provides a sacrificial wear surface during running-in (first ~100 cycles), after which the underlying steel surface operates in steady-state.

3. **Design for the steady-state wear regime.** Ensure that the coating (if any) is thick enough to survive the running-in phase without exposing bare substrate to severe wear conditions.

4. **Monitor preload** at intervals shorter than the predicted wear-limited life divided by the safety factor. For critical applications, strain-gauged bolts or ultrasonic measurement provide direct preload monitoring.

5. **Consider retorquing schedules** that account for both initial embedding (first retorque after 24--48 hours) and progressive wear (subsequent retorques at intervals determined by the BAS analysis).

---

## References

1. **Archard, J.F.** (1953). "Contact and Rubbing of Flat Surfaces." *Journal of Applied Physics*, Vol. 24, No. 8, pp. 981--988. DOI: [10.1063/1.1721448](https://doi.org/10.1063/1.1721448)

2. **Argatov, I.I. and Chai, Y.S.** (2022). "Wear Contact Problem with Friction: Steady-State Regime and Wearing-In Period." *International Journal of Solids and Structures*, Vol. 253, Art. 111757. DOI: [10.1016/j.ijsolstr.2022.111757](https://doi.org/10.1016/j.ijsolstr.2022.111757)

3. **Bhushan, B.** (2013). *Introduction to Tribology*, 2nd ed. John Wiley & Sons, Chichester. ISBN: 978-1-119-94453-9.

4. **Bickford, J.H.** (2008). *Introduction to the Design and Behavior of Bolted Joints*, 4th ed. CRC Press, Boca Raton. ISBN: 978-0-8493-8176-8.

5. **Fouvry, S., Liskiewicz, T., Kapsa, Ph., Hannel, S., and Sauger, E.** (2003). "An Energy Description of Wear Mechanisms and Its Applications to Oscillating Sliding Contacts." *Wear*, Vol. 255, No. 1--6, pp. 287--298. DOI: [10.1016/S0043-1648(03)00117-0](https://doi.org/10.1016/S0043-1648(03)00117-0)

6. **Goryacheva, I.G.** (1998). *Contact Mechanics in Tribology.* Solid Mechanics and Its Applications, Vol. 61. Kluwer Academic Publishers. DOI: [10.1007/978-94-015-9048-8](https://doi.org/10.1007/978-94-015-9048-8)

7. **Heredia, S. and Bielsa, J.M.** (2012). "Fretting Wear Evolution of Stainless Steel Contacts." *Tribology Transactions*, Vol. 55, No. 6, pp. 766--776.

8. **Hintikka, J., Lehtovaara, A., Makinen, A., and Frondelius, T.** (2020). "Running-in in Fretting, Transition from Near-Stable Friction Regime to Gross Sliding." *Tribology International*, Vol. 143, Art. 106073. DOI: [10.1016/j.triboint.2019.106073](https://doi.org/10.1016/j.triboint.2019.106073)

9. **Jiang, Y., Zhang, M., and Lee, C.-H.** (2003). "A Study of Early Stage Self-Loosening of Bolted Joints." *ASME Journal of Mechanical Design*, Vol. 125, No. 3, pp. 518--526. DOI: [10.1115/1.1586936](https://doi.org/10.1115/1.1586936)

10. **Junker, G.H.** (1969). "New Criteria for Self-Loosening of Fasteners under Vibration." *SAE Transactions*, Vol. 78, pp. 314--335. SAE Paper 690055. DOI: [10.4271/690055](https://doi.org/10.4271/690055).

11. **McColl, I.R., Ding, J., and Leen, S.B.** (2004). "Finite Element Simulation and Experimental Validation of Fretting Wear." *Wear*, Vol. 256, No. 11--12, pp. 1114--1127. DOI: [10.1016/j.wear.2003.07.001](https://doi.org/10.1016/j.wear.2003.07.001)

12. **Pai, N.G. and Hess, D.P.** (2002). "Three-Dimensional Finite Element Analysis of Threaded Fastener Loosening Due to Dynamic Shear Load." *Engineering Failure Analysis*, Vol. 9, No. 4, pp. 383--402. DOI: [10.1016/S1350-6307(01)00024-3](https://doi.org/10.1016/S1350-6307(01)00024-3)

13. **Paulin, C., Fouvry, S., and Deyber, S.** (2008). "Wear Kinetics of Ti-6Al-4V under Constant and Variable Fretting Sliding Conditions." *Wear*, Vol. 265, No. 11--12, pp. 1440--1449. DOI: [10.1016/j.wear.2008.01.036](https://doi.org/10.1016/j.wear.2008.01.036)

14. **Rabinowicz, E.** (1965). *Friction and Wear of Materials*. John Wiley & Sons, New York.

15. **VDI 2230 Part 1** (2015). *Systematic Calculation of Highly Stressed Bolted Joints -- Joints with One Cylindrical Bolt.* Verein Deutscher Ingenieure, Dusseldorf.

16. **Vingsbo, O. and Soderberg, S.** (1988). "On Fretting Maps." *Wear*, Vol. 126, No. 2, pp. 131--147. DOI: [10.1016/0043-1648(88)90134-2](https://doi.org/10.1016/0043-1648(88)90134-2)

17. **Yang, X., Nassar, S.A., and Wu, Z.** (2019). "Self-Loosening Behavior of Bolted Joints Subjected to Dynamic Excitation." *Shock and Vibration*, Vol. 2019, Art. 2036509. DOI: [10.1155/2019/2036509](https://doi.org/10.1155/2019/2036509)

18. **API 6A** (2018). *Specification for Wellhead and Christmas Tree Equipment*, 21st ed. American Petroleum Institute, Washington, DC.

19. **ASME PCC-1** (2022). *Guidelines for Pressure Boundary Bolted Flange Joint Assembly*. American Society of Mechanical Engineers, New York.

---

**END OF PART VI -- WEAR MODELS**

*Part V covers Self-Loosening Models*
*Part VII covers Friction Models and Evolution*
*Part XI covers the Coupled Friction-Wear-Loosening Analysis Framework*
*Part XII covers Force Excitation Functions and Rayleigh Damping*
