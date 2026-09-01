# MSD Framework -- PART VII: FRICTION MODELS AND EVOLUTION

**Complete Technical Reference for Bolt Analysis Studio**

**Authors:** L. Ribeiro, D. Carvalho, S.C. Naves, T. Santos, V. Marques, G. Arruda
**Institution:** LTAD/UFU -- Tribology and Wear Technology Laboratory, Federal University of Uberlandia
**Project:** Petrobras R&D -- Bolted Flange Joint Integrity

---

**Abstract.** Friction in a bolted joint plays a paradoxical role: it simultaneously prevents self-loosening (through thread and bearing friction torques) and enables loosening when it degrades below a critical threshold. This document provides a comprehensive treatment of all friction models implemented in the Bolt Analysis Studio, ranging from the classical regularized Coulomb model through advanced dynamic formulations. The LuGre model (Canudas de Wit et al., 1995) captures pre-sliding displacement, hysteresis, and the Stribeck velocity-weakening effect through a bristle-deformation state variable. The Dahl model (Dahl, 1976) provides a simpler rate-independent alternative for pre-sliding behavior. The Segalman four-parameter Iwan model (Segalman, 2005) uses a distribution of parallel Jenkins (spring-slider) elements to reproduce the power-law energy dissipation observed in jointed structures. A three-phase friction evolution model, based on the fretting experiments of Hintikka et al. (2019, 2020), tracks the running-in rise, peak decay, and steady-state approach of the friction coefficient over thousands of loading cycles. The coupled friction-preload model captures the bidirectional interaction where friction degradation promotes loosening and preload loss reduces normal forces. Lubrication regimes (boundary, mixed, hydrodynamic) are modeled through the Stribeck curve with lambda-ratio transitions. A friction model selection guide provides recommendations for each contact type and analysis scenario.

---

## Table of Contents

- [30. Introduction to Friction in Bolted Joints](#30-introduction-to-friction-in-bolted-joints)
- [31. Regularized Coulomb Friction Model](#31-regularized-coulomb-friction-model)
- [32. LuGre Dynamic Friction Model](#32-lugre-dynamic-friction-model)
- [33. Dahl Friction Model](#33-dahl-friction-model)
- [34. Iwan Distributed Element Model](#34-iwan-distributed-element-model)
- [35. Three-Phase Friction Evolution Model](#35-three-phase-friction-evolution-model)
- [36. Coupled Friction-Preload Model](#36-coupled-friction-preload-model)
- [37. Stribeck Curve and Lubrication Regimes](#37-stribeck-curve-and-lubrication-regimes)
- [38. Friction Model Comparison and Selection Guide](#38-friction-model-comparison-and-selection-guide)
- [References](#references)

---

## 30. Introduction to Friction in Bolted Joints

### 30.1 The Dual Role of Friction

Friction in a bolted joint plays a paradoxical role. It is simultaneously the mechanism that **prevents** self-loosening and the very quantity whose reduction **enables** loosening. To understand this apparent contradiction, one must distinguish between the three torque components acting on the nut during transverse excitation.

**Torque balance on the nut under transverse loading:**

```
                    LOOSENING DIRECTION
                  <=====================

  PITCH TORQUE          THREAD FRICTION        BEARING FRICTION
  (DRIVES loosening)    (RESISTS loosening)    (RESISTS loosening)

       p                 mu_t * F_p * d2         mu_b * F_p * r_b
  F_p ----               ---------------         ----------------
      2*pi                  2*cos(alpha)              (direct)

  +-----------+         +----------------+      +----------------+
  | Geometry  |    vs   |   Tribology    |  +   |   Tribology    |
  | (helix)   |         |   (threads)    |      |   (bearing)    |
  +-----------+         +----------------+      +----------------+
       |                        |                       |
       |     T_pitch > T_thread + T_bearing  =>  LOOSENING
       |     T_pitch < T_thread + T_bearing  =>  STABLE
       |                        |                       |
```

The critical insight, first identified by Junker (1969), is:

1. **Thread friction RESISTS loosening.** The friction torque at the thread interface opposes nut rotation. Higher thread friction makes the joint safer against loosening.

2. **Bearing friction RESISTS loosening.** The friction torque at the head-bearing or nut-bearing surface similarly opposes rotation. This is the "last line of defense" against nut back-off.

3. **Pitch torque DRIVES loosening.** This is purely geometric: the helix angle of the thread converts axial preload into a torque that tends to unscrew the nut. It is independent of friction.

The loosening condition is:

$$T_{pitch} > T_{thread} + T_{bearing}$$

where:

$$T_{pitch} = F_p \cdot \frac{p}{2\pi}$$

$$T_{thread} = \frac{\mu_t \cdot F_p \cdot d_2}{2 \cos \alpha}$$

$$T_{bearing} = \mu_b \cdot F_p \cdot r_{bearing}$$

When transverse vibration causes simultaneous slip at both the bearing and thread interfaces, the effective friction resistance drops momentarily. The pitch torque, which is always present as long as the bolt is loaded, seizes this opportunity to rotate the nut incrementally in the loosening direction. Over thousands of cycles, these small angular increments accumulate, reducing preload until the joint fails.

### 30.2 Why Friction Modeling Matters

The sensitivity of loosening life to friction coefficient is extreme. Consider an M16 bolt with pitch $p = 2.0$ mm, pitch diameter $d_2 = 14.701$ mm, and bearing radius $r_b = 10.25$ mm:

| $\mu$ | $T_{pitch}$ (N/kN) | $T_{thread}$ (N/kN) | $T_{bearing}$ (N/kN) | $T_{net}$ | Loosening? |
|:------:|:-------------------:|:--------------------:|:---------------------:|:---------:|:----------:|
| 0.08 | 0.318 | 0.680 | 0.820 | -1.182 | No |
| 0.10 | 0.318 | 0.850 | 1.025 | -1.557 | No |
| 0.12 | 0.318 | 1.020 | 1.230 | -1.932 | No |
| 0.15 | 0.318 | 1.275 | 1.538 | -2.495 | No |

The above table shows torques per kN of preload, all in Nm/kN. None of these static cases produce loosening because the resistance exceeds the driving torque by a comfortable margin. However, **during transverse slip**, the effective bearing friction momentarily drops toward zero in the slip direction, and the thread friction is similarly reduced. When both friction resistances are overcome by the transverse force, the pitch torque drives rotation.

A change from $\mu = 0.12$ to $\mu = 0.08$ (a mere 33% reduction, easily caused by lubricant migration or wear) can change a stable joint into one that loosens rapidly. This sensitivity is why accurate friction modeling is essential for any quantitative loosening prediction.

### 30.3 Friction at Different Joint Locations

A complete bolted joint has friction at multiple distinct interfaces, each with potentially different coefficients and behaviors:

```
                 BOLT HEAD
                     |
         +-----------+-----------+
         |                       |
    HEAD-BEARING            HEAD-FLANGE
    CONTACT                 (direct, no
    mu_b_head               washer)
         |
      WASHER
         |
    WASHER-FLANGE
    CONTACT
    mu_washer
         |
    ============ FLANGE 1 ============
         |
    FLANGE-FLANGE  or  FLANGE-GASKET
    mu_interface       mu_gasket
         |
    ============ FLANGE 2 ============
         |
    WASHER-FLANGE
    mu_washer
         |
      WASHER
         |
    NUT-BEARING
    CONTACT
    mu_b_nut
         |
         +
        NUT ------------ STUD/THREAD
                          |
                     THREAD CONTACT
                     mu_t (per thread)
                     n parallel threads
                     helix coupling
```

Each of these interfaces may have:
- Different surface roughness (Ra)
- Different coatings (zinc, phosphate, PTFE, MoS2)
- Different lubrication states (dry, oiled, greased, anti-seize)
- Different contact pressures, and therefore different friction regimes
- Different wear histories, evolving independently over time

### 30.4 Overview of the Five Friction Models in BAS

Bolt Analysis Studio implements five friction models of increasing physical fidelity. Each captures a different subset of the relevant friction phenomena:

| Model | Type | State Variables | Key Physics Captured |
|:------|:-----|:---------------:|:---------------------|
| **Regularized Coulomb** | Algebraic | 0 | Static/kinetic transition, smooth numerics |
| **Dahl** | 1st-order ODE in $x$ | 1 ($F$) | Pre-sliding stiffness, displacement-dependent hysteresis |
| **LuGre** | 1st-order ODE in $t$ | 1 ($z$) | Pre-sliding, Stribeck, friction lag, stick-slip |
| **Iwan** | Parallel Jenkins | $n$ (element states) | Microslip hysteresis, power-law energy dissipation |
| **Three-Phase Evolution** | Cycle-dependent | 1 ($N$) | Running-in, steady-state, degradation over 10^3--10^6 cycles |

The models are not mutually exclusive. In a typical BAS analysis, one might use a LuGre model for within-cycle dynamics and couple it with the Three-Phase Evolution model for cycle-to-cycle friction coefficient changes.

---

## 31. Regularized Coulomb Friction Model

### 31.1 Classical Coulomb Friction

The oldest and simplest friction model is attributed to Coulomb (1785) and Amontons (1699). It states that the friction force is proportional to the normal force, independent of contact area and sliding velocity:

$$F_f = -\mu \cdot F_n \cdot \text{sign}(v)$$

where $\mu$ takes two distinct values:

$$\mu = \begin{cases} \mu_s & \text{if } v = 0 \text{ (static)} \\ \mu_k & \text{if } v \neq 0 \text{ (kinetic)} \end{cases}$$

The static friction coefficient $\mu_s$ is always greater than the kinetic coefficient $\mu_k$. Typical values for steel-on-steel bolted joints are $\mu_s = 0.12$--$0.18$ and $\mu_k = 0.08$--$0.14$, depending on surface condition and lubrication.

### 31.2 The Numerical Discontinuity Problem

The sign function introduces a mathematical discontinuity at $v = 0$. In numerical integration, this creates several problems:

1. **Chattering:** The solver oscillates between positive and negative friction at every time step near $v = 0$.
2. **Stiffness:** The instantaneous switch requires extremely small time steps for convergence.
3. **Non-uniqueness:** At $v = 0$, the friction force is indeterminate -- it can take any value between $-\mu_s F_n$ and $+\mu_s F_n$.

```
  F_f
   ^
   |         +mu_s * F_n  ----+
   |                          |  <-- DISCONTINUITY at v = 0
   |                          |      friction jumps from
   |                          |      +mu_s*F_n to -mu_s*F_n
   |                          |
 --+-----|-----|-----|--------+--------> v
   |                          |
   |                          |
   |         -mu_s * F_n  ----+
   |
```

For structural dynamics with thousands of time steps, this discontinuity makes the classical Coulomb model impractical as a direct force evaluation.

### 31.3 Regularized Coulomb Formulation

The regularization replaces the discontinuous $\text{sign}(v)$ with a smooth hyperbolic tangent function:

$$F_f = -\mu(v) \cdot F_n \cdot \tanh\left(\frac{v}{v_{reg}}\right)$$

where $v_{reg}$ is a small regularization velocity, typically $v_{reg} \approx 10^{-4}$ m/s.

The hyperbolic tangent provides a smooth, differentiable transition through zero velocity:

$$\tanh\left(\frac{v}{v_{reg}}\right) \approx \begin{cases} \frac{v}{v_{reg}} & \text{for } |v| \ll v_{reg} \\ \text{sign}(v) & \text{for } |v| \gg v_{reg} \end{cases}$$

```
  F_f
   ^
   |         +mu * F_n  - - - - - - - - - - - - - +
   |                    .                         .
   |                  .      Smooth tanh curve   .
   |                .                           .
   |             .                             .
   |          .                               .
   |       .                                 .
 --+-----.------|------|-------.-------|-------> v
   |   .                         .
   |  .                           .
   | .                             .  v_reg
   |.                               . |
   .                                  .v
   |         -mu * F_n  - - - - - - - - - - - - - +
   |
```

Additionally, BAS implements a velocity-dependent friction coefficient that smoothly transitions between static and kinetic values:

$$\mu(v) = \mu_k + (\mu_s - \mu_k) \cdot \exp\left(-\frac{|v|}{v_{trans}}\right)$$

where $v_{trans}$ is the transition velocity scale (typically $v_{trans} = 0.01$ m/s). This captures the well-known observation that friction decreases as sliding velocity increases from zero, which is the essence of the Stribeck effect.

The combined regularized Coulomb model is therefore:

$$\boxed{F_f = -\left[\mu_k + (\mu_s - \mu_k)\,e^{-|v|/v_{trans}}\right] \cdot F_n \cdot \tanh\left(\frac{v}{v_{reg}}\right)}$$

### 31.4 Parameter Summary

| Parameter | Symbol | Default Value | Physical Meaning |
|:----------|:------:|:-------------:|:-----------------|
| Static friction coefficient | $\mu_s$ | 0.15 | Maximum friction at zero velocity |
| Kinetic friction coefficient | $\mu_k$ | 0.12 | Friction during steady sliding |
| Regularization velocity | $v_{reg}$ | $10^{-4}$ m/s | Width of smooth transition zone |
| Transition velocity | $v_{trans}$ | 0.01 m/s | Scale for $\mu_s \to \mu_k$ decay |

**Stiction ratio:** $\mu_s / \mu_k = 1.25$ (typical for lubricated steel).

### 31.5 When to Use This Model

**Recommended for:**
- Preliminary design calculations
- Parameter studies where computation speed is important
- Systems where pre-sliding behavior is not critical
- Coupling with loosening models that require only the friction coefficient, not the full force-displacement relationship

**Limitations:**
- No pre-sliding displacement (response is purely velocity-dependent)
- No history dependence or friction memory
- No hysteresis in the force-displacement plane
- Cannot capture the "friction lag" observed experimentally during velocity reversals
- The regularization velocity $v_{reg}$ introduces a small artificial compliance near $v = 0$, which must be checked against the physical microslip displacements

### 31.6 Rotational Form for Bearing and Thread Friction

For rotational contacts (bearing surfaces, threads), the model converts to torque form:

$$T_f = -\mu(\omega) \cdot F_n \cdot r_{eff} \cdot \tanh\left(\frac{\omega}{\omega_{reg}}\right)$$

where:

$$\omega_{reg} = \frac{v_{reg}}{r_{eff}}$$

and $r_{eff}$ is the effective friction radius of the contact (bearing radius for head/nut contacts, or the pitch radius for thread contacts, corrected by the flank angle).

### 31.7 References

- Amontons, G. (1699). "De la resistance causee dans les machines," *Memoires de l'Academie Royale*, pp. 206--222.
- Coulomb, C.A. (1785). "Theorie des machines simples," *Memoires de Mathematique et de Physique de l'Academie Royale des Sciences*, Vol. 10, pp. 161--342.
- Oden, J.T. and Martins, J.A.C. (1985). "Models and computational methods for dynamic friction phenomena," *Computer Methods in Applied Mechanics and Engineering*, Vol. 52, No. 1--3, pp. 527--634. DOI: 10.1016/0045-7825(85)90009-X.
- Karnopp, D. (1985). "Computer simulation of stick-slip friction in mechanical dynamic systems," *ASME Journal of Dynamic Systems, Measurement, and Control*, Vol. 107, No. 1, pp. 100--103. DOI: 10.1115/1.3140698.

---

## 32. LuGre Dynamic Friction Model

### 32.1 Physical Concept: The Bristle Analogy

The LuGre model, proposed by Canudas de Wit, Olsson, Astrom, and Lischinsky (1995), is named after the universities of Lund and Grenoble where it was developed. It represents the contact between two surfaces as an ensemble of microscopic elastic "bristles" that deform when a tangential force is applied.

```
    SURFACE 1 (moving with velocity v ->)
    ================================================
         \  |  /  \  |  /  \  |  /  \  |  /
          \ | /    \ | /    \ | /    \ | /
     Bristles (elastic + plastic deformation)
          / | \    / | \    / | \    / | \
         /  |  \  /  |  \  /  |  \  /  |  \
    ================================================
    SURFACE 2 (stationary reference)

    At low displacement:  bristles bend elastically
                          -> pre-sliding stiffness sigma_0
                          -> force proportional to displacement

    At large displacement: bristles reach yield, slip
                           -> steady-state Coulomb-like friction
                           -> force proportional to sign(v)
```

The physical intuition is as follows. When two surfaces are pressed together and a small tangential displacement is imposed, the asperity contacts deform elastically. This produces a force that increases linearly with displacement, governed by the bristle stiffness $\sigma_0$. If the displacement continues to increase, the bristle deflection $z$ saturates at a value determined by the Stribeck function $g(v)$, and the asperities slip. During steady sliding, the model reduces to the classical Coulomb/Stribeck behavior.

The key advantage of this formulation is that it captures the **transition** between sticking and sliding as a smooth, continuous process governed by a single first-order differential equation.

### 32.2 Mathematical Formulation

The LuGre model is defined by three equations:

**State equation (bristle deflection):**

$$\frac{dz}{dt} = v - \frac{\sigma_0 \, |v|}{g(v)} \, z$$

**Friction force:**

$$F = \sigma_0 \, z + \sigma_1 \, \frac{dz}{dt} + \sigma_2 \, v$$

**Stribeck function:**

$$g(v) = F_c + (F_s - F_c) \, \exp\left(-\left|\frac{v}{v_s}\right|^{\alpha}\right)$$

where:

- $z$ is the average bristle deflection [m], the internal state variable
- $v$ is the relative sliding velocity [m/s]
- $\sigma_0$ is the bristle stiffness [N/m]
- $\sigma_1$ is the bristle micro-damping coefficient [N$\cdot$s/m]
- $\sigma_2$ is the viscous friction coefficient [N$\cdot$s/m]
- $F_s$ is the maximum static friction force [N]
- $F_c$ is the Coulomb (kinetic) friction force [N]
- $v_s$ is the Stribeck velocity [m/s]
- $\alpha$ is the Stribeck exponent (dimensionless, typically 1--2)

### 32.3 Physical Meaning of Each Parameter

**Bristle stiffness $\sigma_0$** ($= 10^5$ N/m default):

This parameter controls the pre-sliding stiffness of the contact. Physically, it represents the combined tangential stiffness of all asperity junctions in the contact zone. For a Hertzian contact with radius $a$ and combined shear modulus $G^*$, an estimate is $\sigma_0 \approx 8 a G^*$ (Mindlin, 1949). A higher $\sigma_0$ means the contact is stiffer before slip onset, producing smaller pre-sliding displacements. In bolted joints, pre-sliding displacements at thread and bearing surfaces are on the order of 1--10 micrometers, which constrains $\sigma_0$ to the range $10^4$--$10^6$ N/m.

**Micro-damping $\sigma_1$** ($= 300$ N$\cdot$s/m default):

This parameter determines the energy dissipation during pre-sliding oscillations. Physically, it represents the viscous-like damping of asperity contacts during micro-deformation. It is responsible for the hysteresis loop observed in the pre-sliding regime. The value is bounded by stability: $\sigma_1 < 2\sqrt{\sigma_0 \cdot m}$ where $m$ is the effective mass. A typical guideline is $\sigma_1 \approx \sqrt{\sigma_0}$ for underdamped pre-sliding dynamics.

**Viscous coefficient $\sigma_2$** ($= 0.1$ N$\cdot$s/m default):

This parameter represents the true viscous friction component, which is significant only at high sliding velocities where a lubricant film forms. For dry contacts, $\sigma_2 \approx 0$. For lubricated bolted joints, a small but nonzero $\sigma_2$ captures the viscous drag of the lubricant. This term dominates the force at very high velocities, well beyond the Stribeck minimum.

**Static friction $F_s$** and **Coulomb friction $F_c$**:

$F_s$ is the maximum force required to initiate sliding from rest. $F_c$ is the force required to maintain sliding at high velocity (where the Stribeck exponential vanishes). The ratio $F_s/F_c > 1$ is the stiction ratio. For steel with zinc-phosphate coating, typical values are $F_s/F_c \approx 1.25$.

**Stribeck velocity $v_s$** ($= 0.001$ m/s default):

This is the velocity at which the Stribeck effect is most prominent -- the transition from boundary to mixed lubrication. Below $v_s$, friction drops rapidly from $F_s$ toward $F_c$. This velocity is related to the lubricant viscosity and surface roughness. For bolted joints under transverse vibration at 10--50 Hz, the peak sliding velocities at bearing surfaces are typically 0.001--0.01 m/s, placing the Stribeck transition squarely within the operating range.

**Stribeck exponent $\alpha$** ($= 2.0$ default):

This shapes the Stribeck curve. For $\alpha = 1$, the transition is a simple exponential decay. For $\alpha = 2$ (the most common choice, following the original LuGre paper), the curve has a Gaussian-like shape that matches experimental Stribeck data for many engineering surfaces.

### 32.4 Steady-State Analysis

At constant velocity $v = \text{const}$, the bristle deflection reaches a steady state where $dz/dt = 0$:

$$z_{ss} = \frac{g(v)}{\sigma_0} \cdot \text{sign}(v)$$

Substituting into the force equation gives the steady-state friction:

$$F_{ss}(v) = g(v) \cdot \text{sign}(v) + \sigma_2 \cdot v$$

$$= \left[F_c + (F_s - F_c) \exp\left(-\left|\frac{v}{v_s}\right|^{\alpha}\right)\right] \text{sign}(v) + \sigma_2 \cdot v$$

This is precisely the Stribeck curve plus a viscous term. The LuGre model therefore **contains** the classical Stribeck model as its steady-state limit, while adding transient dynamics through the bristle state.

```
  |F_ss|
   ^
   |  Fs ----+
   |          \
   |           \    Stribeck curve (steady-state LuGre)
   |            \
   |             \.
   |              '-.
   |  Fc ----........'--..___
   |                         ''---...__________    + sigma_2 * v
   |                                           '''----------->
   +-------|-------|-------|-------|-------|-------> |v|
   0      vs     2vs     3vs     4vs     5vs
```

### 32.5 Key Behaviors for Bolted Joint Analysis

The LuGre model captures five distinct phenomena that are important for self-loosening prediction:

**1. Pre-sliding displacement:**
Before the contact transitions to gross sliding, there is a finite tangential displacement on the order of $z_{max} = F_s / \sigma_0$. For typical values, this is $z_{max} = 100 / 10^5 = 10^{-3}$ m $= 1$ mm at the model level (or, for normalized parameters, $\sim 1$--$10$ micrometers). This pre-sliding displacement is the "microslip" observed at thread and bearing interfaces during the initial phase of each transverse vibration cycle.

**2. Stick-slip transitions:**
The smooth state equation avoids the numerical chattering of classical Coulomb. The transition from stick to slip (and back) occurs over a finite displacement, not instantaneously. This is physically accurate: real asperity junctions do not all break simultaneously.

**3. Friction lag (hysteresis):**
During velocity reversals, the bristle deflection takes time to reverse direction. This creates a hysteresis loop in the force-velocity plane that is not present in any algebraic (memoryless) friction model. The lag is controlled by $\sigma_0$ and $\sigma_1$: stiffer bristles produce less lag, while higher damping broadens the hysteresis.

**4. Variable break-away force:**
The force required to initiate sliding depends on the rate of force application. A slowly applied force reaches $F_s$ exactly; a rapidly applied force can momentarily exceed $F_s$ due to the viscous $\sigma_1 \dot{z}$ contribution.

**5. Stribeck effect (velocity-dependent steady state):**
The friction decreases with increasing velocity in the boundary-to-mixed lubrication transition, as described by the $g(v)$ function.

### 32.6 Numerical Integration

The bristle state equation is mildly stiff due to the potentially large value of $\sigma_0$. BAS implements implicit Euler integration for robust numerical behavior:

$$z^{n+1} = \frac{z^n + \Delta t \cdot v^{n+1}}{1 + \Delta t \cdot \sigma_0 \cdot |v^{n+1}| / g(v^{n+1})}$$

This implicit form is unconditionally stable for all parameter values and time step sizes, which is critical for the BAS time integration framework where the friction model is called at every sub-step of the Newmark-$\beta$ or HHT-$\alpha$ integrator.

### 32.7 Parameter Summary

| Parameter | Symbol | Default | Range | Unit |
|:----------|:------:|:-------:|:-----:|:----:|
| Bristle stiffness | $\sigma_0$ | $10^5$ | $10^4$--$10^6$ | N/m |
| Micro-damping | $\sigma_1$ | 300 | $10^2$--$10^4$ | N$\cdot$s/m |
| Viscous coefficient | $\sigma_2$ | 0.1 | 0.01--100 | N$\cdot$s/m |
| Static friction | $F_s$ | 100 | -- | N |
| Coulomb friction | $F_c$ | 80 | -- | N |
| Stribeck velocity | $v_s$ | 0.001 | 0.001--0.1 | m/s |
| Stribeck exponent | $\alpha$ | 2.0 | 1.0--2.0 | -- |

### 32.8 When to Use This Model

**Recommended for:**
- High-fidelity self-loosening simulations where transient dynamics within each cycle matter
- Stick-slip transition analysis at thread and bearing surfaces
- Studies of the influence of lubricant viscosity (via $\sigma_2$ and $v_s$)
- Situations where pre-sliding displacement affects the loosening initiation

**Limitations:**
- Seven parameters require calibration (though typical ranges are well established)
- More computationally expensive than Coulomb due to state integration at each time step
- Does not inherently capture the cycle-dependent friction evolution (must be coupled with Section 35)
- The bristle model is phenomenological: $\sigma_0$, $\sigma_1$ are not directly measurable material properties

### 32.9 References

- Canudas de Wit, C., Olsson, H., Astrom, K.J., and Lischinsky, P. (1995). "A New Model for Control of Systems with Friction," *IEEE Transactions on Automatic Control*, Vol. 40, No. 3, pp. 419--425. DOI: [10.1109/9.376053](https://doi.org/10.1109/9.376053).
- Olsson, H., Astrom, K.J., Canudas de Wit, C., Gafvert, M., and Lischinsky, P. (1998). "Friction Models and Friction Compensation," *European Journal of Control*, Vol. 4, No. 3, pp. 176--195. DOI: [10.1016/S0947-3580(98)70113-X](https://doi.org/10.1016/S0947-3580(98)70113-X).
- Mindlin, R.D. (1949). "Compliance of Elastic Bodies in Contact," *ASME Journal of Applied Mechanics*, Vol. 16, pp. 259--268.

---

## 33. Dahl Friction Model

### 33.1 Historical Context

The Dahl model was introduced by Philip Dahl at the Aerospace Corporation in 1968 for precision pointing and tracking systems (Dahl, 1968, 1976). It was one of the first dynamic friction models, predating the LuGre model by nearly three decades. Its distinctive feature is **rate independence**: the friction force depends on displacement, not velocity. This makes it particularly suitable for quasi-static loading or very low-velocity applications where the Stribeck effect is negligible.

### 33.2 Mathematical Formulation

The Dahl model is expressed as a first-order differential equation in displacement:

$$\frac{dF}{dx} = \sigma \left(1 - \frac{F}{F_c} \, \text{sign}(v)\right)^{\alpha}$$

where:

- $F$ is the friction force [N], the internal state variable
- $x$ is the displacement [m]
- $v = dx/dt$ is the velocity [m/s] (only the sign is used)
- $\sigma$ is the contact stiffness coefficient [N/m]
- $F_c$ is the Coulomb friction force (the friction force in steady sliding) [N]
- $\alpha$ is the shape exponent (dimensionless)

### 33.3 Physical Interpretation

The Dahl model has a direct analogy to the stress-strain curve of a material undergoing elasto-plastic deformation:

```
  F (friction force)
   ^
   |                              +------------- F_c (Coulomb limit)
   |                         .''''
   |                     .'''
   |                  .''
   |              .''     <-- Transition region
   |          .''             (shape controlled by alpha)
   |       .''
   |    .''    <-- Initial slope = sigma (pre-sliding stiffness)
   |  .''
   |.'
   +-----|-------|-------|-------|-------|-------> x (displacement)
   0   x_1     x_2     x_3     x_4     x_5
```

**At small displacements** ($F \ll F_c$), the term $(1 - F/F_c)^{\alpha} \approx 1$, and the equation reduces to $dF/dx = \sigma$. The friction force grows linearly with displacement at the rate $\sigma$, representing elastic deformation of asperity junctions.

**At large displacements** ($F \to F_c$), the term $(1 - F/F_c)^{\alpha} \to 0$, and the force asymptotically approaches $F_c$. This is the Coulomb limit -- steady sliding friction.

The shape exponent $\alpha$ controls how sharp the transition is:

- $\alpha = 1$: Smooth exponential transition (most common choice)
- $\alpha < 1$ (e.g., $\alpha = 1/3$): Very gradual transition, matches Mindlin partial-slip theory for Hertzian contacts
- $\alpha > 1$: Sharper elbow, closer to ideal elastic-perfectly-plastic behavior

### 33.4 Solution for Constant Velocity Loading

For constant velocity $v > 0$ with initial condition $F(0) = 0$ and $\alpha = 1$, the analytical solution is:

$$F(x) = F_c \left(1 - e^{-\sigma \, x / F_c}\right)$$

The characteristic pre-sliding displacement is:

$$x_{ps} = \frac{F_c}{\sigma}$$

For typical BAS parameters ($F_c = 100$ N, $\sigma = 10^5$ N/m), $x_{ps} = 10^{-3}$ m $= 1$ mm at the model scale, or on the order of micrometers when the forces are normalized by the actual normal load.

### 33.5 Hysteresis Upon Load Reversal

When the velocity reverses sign, the Dahl model produces hysteresis. If sliding was occurring in the positive direction with $F = F_c$, and the velocity reverses to negative, the friction force does not instantly jump to $-F_c$. Instead, it traces a new loading curve:

$$\frac{dF}{dx} = \sigma \left(1 + \frac{F}{F_c}\right)^{\alpha}$$

(note the sign change in the parenthetical term due to $\text{sign}(v) = -1$).

The resulting hysteresis loop encloses an area equal to the energy dissipated per cycle, which for small amplitudes is:

$$W_d \propto x_{amp}^{2 + 1/\alpha}$$

For $\alpha = 1$, this gives $W_d \propto x_{amp}^3$, which is the Mindlin partial-slip prediction for spherical contacts.

### 33.6 Relationship to the LuGre Model

The Dahl model is a subset of the LuGre model. Setting $\sigma_1 = 0$, $\sigma_2 = 0$, and making the Stribeck function constant $g(v) = F_c$, the LuGre bristle equation reduces to:

$$\frac{dz}{dt} = v - \frac{\sigma_0 |v|}{F_c} z$$

With $F = \sigma_0 z$ and $x = \int v \, dt$, this is equivalent to the Dahl equation with $\alpha = 1$ and $\sigma = \sigma_0$. Thus, **Dahl = LuGre without Stribeck and without viscous/damping terms**.

### 33.7 Parameter Summary

| Parameter | Symbol | Default | Range | Unit |
|:----------|:------:|:-------:|:-----:|:----:|
| Stiffness coefficient | $\sigma$ | $10^5$ | $10^4$--$10^7$ | N/m |
| Coulomb friction force | $F_c$ | 100 | -- | N |
| Shape exponent | $\alpha$ | 1.0 | 0.33--1.0 | -- |

### 33.8 Correlation with Mindlin Contact Theory

For a Hertzian sphere-on-flat contact (relevant to asperity models), the Mindlin (1949) partial-slip theory gives a tangential compliance that can be expressed in Dahl form with:

$$\sigma = 8 \, a \, G^*$$

$$\alpha = 1/3$$

where $a$ is the Hertzian contact radius and $G^*$ is the combined shear compliance. The $\alpha = 1/3$ exponent produces a loading curve $F \propto x^{2/3}$ at small displacements, matching the Mindlin solution exactly.

### 33.9 When to Use This Model

**Recommended for:**
- Low-velocity applications where the Stribeck effect is negligible
- Pre-sliding displacement analysis (e.g., thread microslip during initial loading)
- Systems where a simple displacement-based hysteresis model is sufficient
- Quasi-static loading and unloading cycles
- Simpler alternative to LuGre when rate effects are not important

**Limitations:**
- No velocity dependence: $\mu$ is the same at 0.001 m/s and 1 m/s
- No viscous friction component (irrelevant for dry contacts, but matters for lubricated)
- Does not capture the Stribeck minimum (friction dip at intermediate velocities)
- No friction lag in the velocity domain

### 33.10 References

- Dahl, P.R. (1968). "A Solid Friction Model," *TOR-0158(3107-18)-1*, The Aerospace Corporation, El Segundo, CA.
- Dahl, P.R. (1976). "Solid Friction Damping of Mechanical Vibrations," *AIAA Journal*, Vol. 14, No. 12, pp. 1675--1682. DOI: [10.2514/3.61511](https://doi.org/10.2514/3.61511).
- Mindlin, R.D. (1949). "Compliance of Elastic Bodies in Contact," *ASME Journal of Applied Mechanics*, Vol. 16, pp. 259--268.

---

## 34. Iwan Distributed Element Model

### 34.1 Concept: Parallel Jenkins Elements

The Iwan model, originally proposed by Iwan (1966) and later developed into the "four-parameter" form by Segalman (2002, 2005) at Sandia National Laboratories, represents friction using a continuous distribution of parallel Jenkins elements. Each Jenkins element consists of a spring in series with an ideal slip (Coulomb) element:

```
                 Applied displacement u
                        |
    ====================|=====================
    ||                  |                   ||
    ||   +---[k_1]---{mu_1}---+             ||
    ||   |                    |             ||
    ||   +---[k_2]---{mu_2}---+             ||
    ||   |                    |             ||
    ||   +---[k_3]---{mu_3}---+             ||
    ||   |                    |             ||
    ||   +---[k_4]---{mu_4}---+             ||
    ||   |         ...        |             ||
    ||   +---[k_n]---{mu_n}---+             ||
    ||                  |                   ||
    ====================|=====================
                        |
                    Fixed ground

    Each element:  k_i = spring stiffness
                   mu_i = slip force (yield threshold)

    Elements with LOW mu_i slip first (microslip)
    Elements with HIGH mu_i slip last (macroslip)
    All elements together produce smooth hysteresis
```

The physical picture is intuitive. Imagine the contact between two rough surfaces as consisting of many asperity junctions, each with its own strength. Under a small tangential load, only the weakest junctions slip (partial slip, or microslip). As the load increases, progressively stronger junctions yield, until finally all junctions are slipping (macroslip, or gross sliding). This progression from microslip to macroslip produces a smooth, nonlinear force-displacement curve with hysteresis.

### 34.2 Single Jenkins Element Behavior

Each Jenkins element $i$ behaves as follows. Define $u_i$ as the displacement of the slip element and $u$ as the total applied displacement. Then the spring deflection is $u - u_i$, and the element force is:

$$F_i = k_i \cdot (u - u_i)$$

subject to the constraint:

$$|F_i| \leq \phi_i$$

where $\phi_i$ is the critical slip force of element $i$. When $|F_i| = \phi_i$, the element slips ($\dot{u}_i \neq 0$); otherwise it sticks ($\dot{u}_i = 0$).

### 34.3 The Segalman Four-Parameter Model

Segalman (2002) showed that the distribution of critical slip forces $\phi_i$ can be described by a continuous density function:

$$\rho(\phi) = R \cdot \chi \cdot \frac{\phi^{\chi - 1}}{F_s^{\chi + 1}}$$

where:

- $R$ is the density function coefficient (normalization)
- $\chi$ is the power-law exponent (controls the shape of the distribution)
- $F_s$ is the critical macroslip force (the force at which all elements have yielded)

This power-law distribution, combined with the tangent stiffness $K_T$, fully characterizes the model with four parameters: $(K_T, F_s, \chi, R)$.

### 34.4 Backbone Curve

The virgin loading curve (backbone) of the Iwan model has an analytical expression:

$$F(u) = K_T \cdot u \cdot \left[1 - \frac{1}{\chi + 2}\left(\frac{K_T \cdot u}{F_s}\right)^{\chi + 2}\right] \quad \text{for} \quad K_T \cdot |u| < F_s$$

$$F(u) = F_s \cdot \text{sign}(u) \quad \text{for} \quad K_T \cdot |u| \geq F_s$$

At small displacements, $F \approx K_T \cdot u$ (linear stiffness). At large displacements, $F \to F_s$ (Coulomb limit). The transition is controlled by $\chi$: smaller $\chi$ produces a more gradual transition; larger $\chi$ makes it sharper.

### 34.5 Energy Dissipation: The Power-Law Exponent

The energy dissipated per cycle for sinusoidal loading at force amplitude $F_{amp}$ follows a power law:

$$W_d \propto F_{amp}^{\;\beta}$$

where the dissipation exponent is:

$$\boxed{\beta = \chi + 3}$$

This is a remarkable result. It means that the energy dissipation per cycle, which can be measured experimentally, is directly related to the power-law exponent $\chi$ through a simple algebraic relationship.

For bolted joints, experimental measurements consistently show $\beta$ in the range 2.5--3.0 (Segalman, 2002; Brake, 2018). This corresponds to $\chi = -0.5$ to $0.0$. The BAS default of $\chi = 0.5$ ($\beta = 3.5$) is slightly above this range, providing a conservative estimate (less energy dissipation, less damping).

| $\chi$ | $\beta = \chi + 3$ | Physical Interpretation |
|:------:|:------------------:|:------------------------|
| $-0.5$ | 2.5 | Highly dissipative; many weak junctions |
| 0.0 | 3.0 | Moderate dissipation; typical for lap joints |
| 0.5 | 3.5 | Conservative; fewer weak junctions (BAS default) |
| 1.0 | 4.0 | Stiff joint; mostly elastic response |

### 34.6 Hysteresis Loop Behavior

Upon load reversal from maximum displacement $u_0$, the unloading curve is given by the Masing rule:

$$F_{unload}(u) = F(u_0) - 2 \cdot f\left(\frac{u_0 - u}{2}\right)$$

where $f(\cdot)$ is the backbone function. This produces closed hysteresis loops whose area equals the energy dissipated per cycle.

```
  F
   ^
   |          . * * * * . F_s
   |        * .         * .
   |      *  .            *.
   |    *   .     LOADING   *
   |  *    .       -->       *
   | *    .                   *
   |*    .         Area =      *
 --+----+----------W_d--------+--> u
   |*    .                   *
   | *    .      <--        *
   |  *    .    UNLOADING  *
   |    *   .            *.
   |      *  .         * .
   |        * .       * .
   |          . * * * . -F_s
   |
```

### 34.7 Physical Significance for Bolted Joints

The Iwan model has become the standard model for mechanical joints in structural dynamics research for several reasons:

1. **Microslip modeling:** The progressive slip of Jenkins elements naturally represents the microslip that occurs at thread and bearing interfaces before the onset of macroslip. This is critical for understanding the initial stages of loosening (Jiang Stage 1).

2. **Realistic energy dissipation:** The power-law energy dissipation matches experimental data from dynamic characterization of bolted joints (Brake, 2018). This is important for correctly predicting the structural damping contributed by joints.

3. **History dependence:** The Iwan model exhibits "non-local memory" -- the state depends on the entire loading history, not just the current displacement and velocity. This captures phenomena such as the Masing behavior observed in bolted joint hysteresis experiments.

4. **Parameter identification from experiments:** The four parameters can be identified from a simple experiment: measure the hysteresis loop at several amplitudes, fit the power-law exponent $\beta$ to get $\chi$, measure the initial stiffness to get $K_T$, and measure the macroslip force to get $F_s$.

### 34.8 Parameter Summary

| Parameter | Symbol | Default | Physical Meaning |
|:----------|:------:|:-------:|:-----------------|
| Initial tangent stiffness | $K_T$ | $10^6$ N/m | Slope at origin of backbone curve |
| Critical slip force | $F_s$ | 100 N | Force for complete macroslip |
| Power-law exponent | $\chi$ | 0.5 | Controls slip force distribution shape |
| Density coefficient | $R$ | 1.0 | Normalization of density function |
| Number of elements | $n$ | 50 | Discretization (convergence $\geq$ 20) |

### 34.9 When to Use This Model

**Recommended for:**
- Detailed joint dynamics simulations requiring accurate energy dissipation
- Modal analysis where joint damping is important
- Lap joint and bolted flange vibration studies
- Research applications where comparison with Sandia experiments is desired
- Situations where the power-law energy dissipation exponent has been experimentally measured

**Limitations:**
- No velocity dependence (rate-independent, like Dahl)
- Computationally more expensive than single-state models due to tracking $n$ element states
- Parameter $R$ has limited physical interpretation and is primarily a normalization constant
- Does not directly model tribological phenomena (wear, lubrication) -- only the mechanical hysteresis

### 34.10 References

- Iwan, W.D. (1966). "A Distributed-Element Model for Hysteresis and Its Steady-State Dynamic Response," *ASME Journal of Applied Mechanics*, Vol. 33, No. 4, pp. 893--900. DOI: [10.1115/1.3625199](https://doi.org/10.1115/1.3625199).
- Segalman, D.J. (2002). "A Four-Parameter Iwan Model for Lap-Type Joints," *SAND2002-3828*, Sandia National Laboratories, Albuquerque, NM.
- Segalman, D.J. (2005). "A Four-Parameter Iwan Model for Lap-Type Joints," *ASME Journal of Applied Mechanics*, Vol. 72, No. 5, pp. 752--760. DOI: [10.1115/1.1989354](https://doi.org/10.1115/1.1989354).
- Brake, M.R.W. (2018). *The Mechanics of Jointed Structures*, Springer. DOI: [10.1007/978-3-319-56818-8](https://doi.org/10.1007/978-3-319-56818-8).

---

## 35. Three-Phase Friction Evolution Model

### 35.1 Motivation: Friction Changes Over Time

All of the models presented in Sections 31--34 describe the friction force at a given instant, given the current velocity and state. They assume that the friction parameters ($\mu_s$, $\mu_k$, $\sigma_0$, $F_s$, etc.) are constant. In reality, these parameters change over the life of the joint due to surface modification processes.

Experimental studies by Hintikka, Lehtovaara, and Mantyla (2019, 2020) on fretting contacts have conclusively demonstrated that the friction coefficient evolves through three distinct phases during cyclic loading. This evolution can change the friction coefficient by 20--50% over the life of the joint, which has a dramatic effect on loosening behavior.

### 35.2 The Three Phases

```
  mu (friction coefficient)
   ^
   |          mu_peak
   |           .
   |          / \
   |         /   \
   |        /     '-.       mu_steady_state
   |       /         ''--.._____________________________
   |      /                                              '.
   | mu_0/                                                 '.
   |   /                                                     '.  Phase III
   |  /     Phase I          Phase II                          '.
   | /     (Running-in)     (Steady-State Transition)           '.
   |/                                                             '.
   +-------|-------------|-------------------------------|-----------> N
   0      N_1           N_2                            N_critical
          (~50)        (~500)                          (~10^5)
```

**Phase I: Running-In** (0 to $N_1$ cycles, typically $N_1 \approx 50$)

During the initial loading cycles, the contacting surfaces undergo rapid modification:

- **Asperity truncation:** The highest asperity peaks are plastically deformed and flattened.
- **Coating wear:** If the bolt has a zinc-phosphate or other protective coating, the coating begins to wear through, exposing the substrate material.
- **Surface roughening:** For initially smooth surfaces, adhesive wear can actually increase roughness.
- **Oxide disruption:** The native oxide layer is broken and reformed.

The net effect is typically a rapid **increase** in friction from the initial value $\mu_0$ toward a peak value $\mu_{peak}$. The increase occurs because the freshly exposed substrate material (often bare steel) has higher adhesion than the coated surface. The rate of increase is governed by the characteristic cycle count $N_1$.

**Phase II: Steady-State Transition** ($N_1$ to $N_{critical}$ cycles, typically $N_{critical} \approx 10^5$)

After the running-in peak, the friction gradually decreases and stabilizes:

- **Oxide debris accumulation:** Iron oxide debris forms a third-body layer that acts as a solid lubricant.
- **Surface smoothening:** Continued sliding polishes the contact surface, reducing asperity heights.
- **Steady-state wear:** The wear rate stabilizes as the surface geometry reaches a quasi-equilibrium.
- **Chemical stabilization:** The surface chemistry stabilizes (oxide layer thickness, contamination).

The friction decays from $\mu_{peak}$ toward a steady-state value $\mu_{ss}$ with characteristic cycle count $N_2 \approx 500$. Long-term stabilization is governed by $N_3 \approx 5000$.

**Phase III: Long-Term Degradation** ($N > N_{critical}$, typically $N_{critical} \approx 10^5$)

Over very long service lives, additional degradation mechanisms emerge:

- **Fatigue damage:** Surface and sub-surface fatigue cracks develop.
- **Fretting damage:** Accumulation of fretting wear debris.
- **Lubricant depletion:** Initial lubricant is consumed or displaced.
- **Hydrogen embrittlement:** In some environments, hydrogen ingress weakens the surface.

The friction may slowly increase, decrease, or fluctuate depending on the dominant degradation mechanism. BAS models this as a logarithmic drift with rate parameter $\beta_{degrade}$.

### 35.3 Mathematical Model

The complete three-phase friction evolution is captured by a single equation:

$$\boxed{\mu(N) = \mu_0 + \underbrace{(\mu_{peak} - \mu_0)(1 - e^{-N/N_1}) \, e^{-N/N_2}}_{\text{Phase I: Running-in peak}} + \underbrace{(\mu_{ss} - \mu_0)(1 - e^{-N/N_3})}_{\text{Phase II: Stabilization}}}$$

For $N > N_{critical}$, a degradation term is added:

$$\mu(N) = \mu_{base}(N) + \beta_{degrade} \cdot \ln\left(\frac{N}{N_{critical}}\right) \quad \text{for } N > N_{critical}$$

**Analysis of each term:**

*Running-in peak term:* $(1 - e^{-N/N_1})$ rises from 0 to 1 over $\sim 3N_1$ cycles, while $e^{-N/N_2}$ decays from 1 to 0 over $\sim 3N_2$ cycles. The product creates a transient peak that appears at $N \approx N_1$ and disappears by $N \approx 3N_2$.

*Stabilization term:* $(1 - e^{-N/N_3})$ is a simple exponential rise toward the steady-state offset $(\mu_{ss} - \mu_0)$. Since $\mu_{ss} < \mu_0$ typically, this term is negative, representing the long-term decrease of friction.

*Degradation term:* The logarithmic form $\ln(N/N_{critical})$ grows very slowly, capturing the gradual nature of fatigue-driven changes. The sign of $\beta_{degrade}$ determines whether friction increases (positive, surface roughening) or decreases (negative, polishing).

### 35.4 Typical Parameters

| Parameter | Symbol | Default | Physical Meaning |
|:----------|:------:|:-------:|:-----------------|
| Initial friction | $\mu_0$ | 0.14 | As-installed (with coating/lubricant) |
| Peak friction | $\mu_{peak}$ | 0.18 | Maximum during running-in |
| Steady-state friction | $\mu_{ss}$ | 0.12 | Long-term stabilized value |
| Running-in rise cycles | $N_1$ | 50 | Rate of initial friction increase |
| Peak decay cycles | $N_2$ | 500 | Rate of peak-to-steady transition |
| Stabilization cycles | $N_3$ | 5000 | Rate of approach to $\mu_{ss}$ |
| Degradation rate | $\beta_{degrade}$ | 0.01 | Long-term drift rate |
| Degradation onset | $N_{critical}$ | $10^5$ | Cycle count for Phase III onset |

**Representative evolution for zinc-phosphate coated M16 bolt:**

| Cycles | $\mu(N)$ | Phase | Surface Condition |
|:------:|:--------:|:-----:|:------------------|
| 0 | 0.140 | I | Fresh coating, lubricated |
| 25 | 0.163 | I | Coating wearing, roughening |
| 50 | 0.175 | I | Peak roughness, coating breakthrough |
| 100 | 0.168 | I/II | Oxide debris forming |
| 500 | 0.138 | II | Debris layer established |
| 2000 | 0.124 | II | Near steady state |
| 10000 | 0.121 | II | Stable |
| $10^5$ | 0.120 | II/III | Degradation onset |
| $10^6$ | 0.143 | III | Surface fatigue accumulation |

### 35.5 Coupling with Instantaneous Friction Models

The Three-Phase Evolution model does not replace the LuGre, Dahl, or Iwan models. Rather, it modulates their parameters over the cycle count. In BAS, the coupling works as follows:

$$F_c(N) = \mu(N) \cdot F_n \qquad F_s(N) = \frac{\mu_s}{\mu_k} \cdot \mu(N) \cdot F_n$$

At each cycle $N$, the friction evolution model updates $\mu(N)$, which in turn updates the $F_c$ and $F_s$ parameters of the LuGre (or other) model used within that cycle.

```
    Cycle N        Cycle N+1       Cycle N+2       ...
   +----------+   +----------+   +----------+
   | LuGre    |   | LuGre    |   | LuGre    |
   | with     |   | with     |   | with     |
   | Fc(N)    |   | Fc(N+1)  |   | Fc(N+2)  |
   | Fs(N)    |   | Fs(N+1)  |   | Fs(N+2)  |
   +----+-----+   +----+-----+   +----+-----+
        |              |              |
        v              v              v
   Three-Phase Evolution: mu(N) -> mu(N+1) -> mu(N+2)
```

### 35.6 When to Use This Model

**Recommended for:**
- Long-duration loosening simulations ($> 1000$ cycles) where friction evolution matters
- Joints with sacrificial coatings (zinc, phosphate, PTFE) that wear through
- Studies of the effect of surface conditioning on loosening life
- Calibration against Junker test data that show non-monotonic friction behavior

**Limitations:**
- Requires experimental data for parameter calibration (the default values are representative but not universal)
- Assumes a single, averaged friction coefficient for the entire contact (no spatial variation)
- The three-phase structure may not apply to all surface conditions (e.g., bare steel-on-steel may lack a distinct running-in peak)

### 35.7 References

- Hintikka, J., Lehtovaara, A., and Mantyla, A. (2019). "Stable and Unstable Friction in Fretting Contacts," *Tribology International*, Vol. 131, pp. 73--82. DOI: [10.1016/j.triboint.2018.10.014](https://doi.org/10.1016/j.triboint.2018.10.014).
- Hintikka, J., Lehtovaara, A., and Mantyla, A. (2020). "Running-in in Fretting, Transition from near-stable to unstable friction," *Tribology International*, Vol. 143, Art. 106073. DOI: [10.1016/j.triboint.2019.106073](https://doi.org/10.1016/j.triboint.2019.106073).
- Fouvry, S., Liskiewicz, T., Paulin, C., and Pauber, T. (2007). "A Global-Local Wear Approach to Quantify the Contact Endurance Under Reciprocating-Fretting Sliding Conditions," *Wear*, Vol. 263, No. 1--6, pp. 518--531. DOI: [10.1016/j.wear.2007.01.072](https://doi.org/10.1016/j.wear.2007.01.072).

---

## 36. Coupled Friction-Preload Model

### 36.1 The Bidirectional Coupling Problem

In a real bolted joint under cyclic transverse loading, friction and preload are not independent. They form a coupled system with bidirectional feedback:

**Forward path:** Preload determines the contact pressure at all interfaces. Contact pressure, in turn, affects the friction coefficient (through the pressure dependence of asperity deformation and real contact area).

**Feedback path:** Friction determines the loosening resistance. If friction decreases, loosening accelerates, which reduces preload. Reduced preload lowers the contact pressure, which changes friction -- completing the loop.

```
     +------------------------------------------------------------------+
     |                                                                  |
     |   +--------------+       +-------------------+                   |
     |   |              |       |                   |                   |
     +-->|   PRELOAD    |------>|  CONTACT PRESSURE  |---+              |
         |              |       |                   |   |              |
         |    F_p(N)    |       |   p = F_p / A     |   |              |
         +------^-------+       +-------------------+   |              |
                |                                       |              |
                |                                       v              |
         +------+-------+       +-------------------+                  |
         |              |       |                   |                  |
         |  LOOSENING   |<------|     FRICTION      |<-----------------+
         |              |       |                   |
         |  dtheta/dN   |       |  mu = f(N, p, h)  |
         +--------------+       +-------------------+
                                        ^
                                        |
                                 +------+-------+
                                 |              |
                                 |     WEAR     |
                                 |              |
                                 |   h = g(N)   |
                                 +--------------+
```

### 36.2 Pressure-Dependent Friction

Experimental studies have shown that friction coefficients in metallic contacts depend weakly on contact pressure:

$$\mu \propto p^n$$

where $n$ is a small exponent, typically in the range $-0.1 \leq n \leq +0.2$. The sign and magnitude depend on the surface condition:

| Surface Condition | $n$ | Mechanism |
|:------------------|:---:|:----------|
| Bare metal, adhesive | $-0.1$ | Higher pressure flattens asperities, reducing real contact area growth rate |
| Coated (zinc, phosphate) | $+0.1$ to $+0.2$ | Higher pressure increases coating deformation, more ploughing |
| Lubricated | $\approx 0$ | Pressure effect screened by lubricant film |

In the coupled model, the friction coefficient at cycle $N$ is:

$$\mu_{coupled}(N) = \mu_{base}(N) \cdot \left(\frac{p(N)}{p_0}\right)^n$$

where $\mu_{base}(N)$ is the friction from the Three-Phase Evolution model (Section 35), $p(N)$ is the current contact pressure, and $p_0$ is the initial contact pressure.

### 36.3 Preload Feedback

The preload evolution is governed by the Jiang two-stage model (see Part V, Section 22), modified by the coupled friction:

**Stage I** (non-rotational, $N < N_{trans}$):

$$\frac{dF_p}{dN} = -\lambda_1 \cdot F_p \cdot \left[1 + \gamma \cdot \frac{\mu(N) - \mu_0}{\mu_0}\right]$$

**Stage II** (rotational, $N > N_{trans}$):

$$\frac{dF_p}{dN} = -\lambda_2 \cdot F_0 \cdot \left[1 - \gamma \cdot \frac{\mu(N) - \mu_0}{\mu_0}\right]$$

where $\gamma$ is the preload feedback parameter (default $\gamma = 0.1$). The key insight is:

- In Stage I (embedding), **higher friction increases the decay rate** because it causes more energy dissipation in the embedding process.
- In Stage II (rotational loosening), **higher friction decreases the decay rate** because it resists nut rotation.

This asymmetric effect of friction on the two loosening stages is physically motivated and produces realistic preload-vs-cycles curves.

### 36.4 Positive Feedback Instability

A critical feature of the coupled model is the potential for **positive feedback instability**. Consider the following scenario:

1. Wear reduces the friction coefficient slightly.
2. Lower friction allows more loosening per cycle.
3. More loosening reduces the preload.
4. Lower preload reduces the contact pressure.
5. For negative pressure exponent ($n < 0$), lower pressure further reduces friction.
6. Return to step 2 with even lower friction.

This positive feedback loop can cause accelerating preload loss, leading to sudden joint failure after an extended period of apparently stable behavior. The coupled model captures this instability, which cannot be predicted by models that treat friction as constant.

### 36.5 When to Use This Model

**Recommended for:**
- Joints where preload loss exceeds 30--40% (strong coupling regime)
- Long-duration simulations where wear significantly changes surface conditions
- Safety-critical joints where the acceleration of loosening must be predicted
- Studies of the interaction between coating wear and loosening life

**Limitations:**
- The pressure exponent $n$ is difficult to measure and varies with surface condition
- The feedback parameter $\gamma$ requires calibration against experimental data
- The simplified contact pressure calculation ($p = F_p / A$) does not account for the non-uniform pressure distribution under the bolt head

### 36.6 References

- Jiang, Y., Zhang, M., and Lee, C.H. (2003). "A Study of Early Stage Self-Loosening of Bolted Joints," *ASME Journal of Mechanical Design*, Vol. 125, No. 3, pp. 518--526. DOI: [10.1115/1.1586936](https://doi.org/10.1115/1.1586936).
- Pai, N.G. and Hess, D.P. (2002). "Three-Dimensional Finite Element Analysis of Threaded Fastener Loosening due to Dynamic Shear Load," *Engineering Failure Analysis*, Vol. 9, No. 4, pp. 383--402. DOI: [10.1016/S1350-6307(01)00024-3](https://doi.org/10.1016/S1350-6307(01)00024-3).

---

## 37. Stribeck Curve and Lubrication Regimes

### 37.1 The Stribeck Curve

The Stribeck curve, named after Richard Stribeck (1902), describes how the friction coefficient in a lubricated contact depends on the operating conditions. It is typically plotted as $\mu$ versus the Hersey number (or the Sommerfeld number, or the specific film thickness $\Lambda$):

$$\text{Hersey number:} \quad He = \frac{\eta \cdot N}{P}$$

where $\eta$ is the lubricant dynamic viscosity [Pa$\cdot$s], $N$ is the rotational speed [rev/s], and $P$ is the mean contact pressure [Pa].

Alternatively, BAS uses the specific film thickness ratio:

$$\Lambda = \frac{h_c}{\sqrt{R_{q1}^2 + R_{q2}^2}}$$

where $h_c$ is the lubricant film thickness and $R_{q1}$, $R_{q2}$ are the RMS surface roughnesses of the two contacting surfaces.

### 37.2 Three Lubrication Regimes

```
  mu (friction coefficient)
   ^
   |
   |  0.3 ----+
   |           |
   |  0.2      |
   |           |    BOUNDARY
   |  0.15 ----+...
   |                '..
   |                   '.     MIXED
   |  0.05               '..
   |                        '..
   |  0.01                    '..___        HYDRODYNAMIC
   |  0.005 -                       '''--.._______
   |  0.001                                       '''-------->
   +-----|-------|-------|-------|-------|-------|-------> Lambda
   0     0.5    1.0    1.5    2.0    2.5    3.0
```

**Boundary lubrication** ($\Lambda < 1$):

The lubricant film is thinner than the surface roughness. Asperity-to-asperity contact dominates, and friction is primarily controlled by the surface chemistry and thin boundary films. Friction coefficients are high: $\mu = 0.10$--$0.30$.

This is the regime relevant to **most bolted joint contacts** during service. Thread contacts, bearing surfaces, and flange interfaces operate almost exclusively in the boundary or mixed regime because the sliding velocities are low and the contact pressures are high.

**Mixed lubrication** ($1 < \Lambda < 3$):

The lubricant film is comparable to the surface roughness. Some asperity contact occurs, but the load is partially supported by the lubricant film. Friction decreases rapidly with increasing $\Lambda$.

In the BAS implementation, the mixed regime is modeled with a logarithmic interpolation:

$$\mu(\Lambda) = \mu_{boundary} \cdot \exp\left[\frac{\ln(\Lambda / \Lambda_1)}{\ln(\Lambda_2 / \Lambda_1)} \cdot \ln\left(\frac{\mu_{hydro}}{\mu_{boundary}}\right)\right]$$

for $\Lambda_1 \leq \Lambda \leq \Lambda_2$.

**Hydrodynamic lubrication** ($\Lambda > 3$):

The surfaces are fully separated by the lubricant film. Friction is due only to viscous shearing of the lubricant, producing very low friction: $\mu = 0.001$--$0.01$.

This regime is rarely relevant for bolted joints unless the joint is in a heavily oiled environment (e.g., engine crankcase applications). However, anti-seize compounds with viscous carriers can produce mixed-to-hydrodynamic conditions at bearing surfaces during tightening.

### 37.3 Relevance to Bolt Lubrication Selection

The Stribeck curve directly informs the choice of bolt lubrication in engineering practice:

| Lubricant Type | $\mu_{thread}$ | $\mu_{bearing}$ | Stribeck Regime | Application |
|:---------------|:--------------:|:---------------:|:---------------:|:------------|
| Dry (no lubricant) | 0.12--0.18 | 0.12--0.18 | Boundary | Structural steel, dry assembly |
| Oil (mineral) | 0.08--0.12 | 0.08--0.12 | Boundary/mixed | General machinery |
| MoS$_2$ paste | 0.06--0.10 | 0.06--0.10 | Boundary | Stainless steel, high temperature |
| PTFE coating | 0.04--0.08 | 0.04--0.08 | Boundary | Corrosive environments |
| Anti-seize compound | 0.08--0.14 | 0.08--0.14 | Mixed | Maintenance-critical joints |
| Zinc-phosphate + oil | 0.10--0.15 | 0.10--0.15 | Boundary | Standard industrial fasteners |

**Practical consequences for self-loosening:**

Lower friction (better lubrication) has a dual effect:
1. **Beneficial:** Lower tightening torque for the same preload, reducing torsional stress in the bolt.
2. **Detrimental:** Lower loosening resistance. Thread and bearing friction torques are both reduced, making it easier for the pitch torque to overcome the resistance.

The optimal lubrication is therefore a compromise: enough to achieve adequate preload without overtorquing, but not so much that the loosening resistance is compromised. VDI 2230 recommends $\mu_{total} = 0.08$--$0.16$ as the acceptable range for controlled tightening.

### 37.4 References

- Stribeck, R. (1902). "Die wesentlichen Eigenschaften der Gleit- und Rollenlager," *Zeitschrift des Vereins Deutscher Ingenieure*, Vol. 46, pp. 1341--1348, 1432--1438, 1463--1470.
- Hamrock, B.J., Schmid, S.R., and Jacobson, B.O. (2004). *Fundamentals of Fluid Film Lubrication*, 2nd ed., Marcel Dekker. DOI: [10.1201/9780203021187](https://doi.org/10.1201/9780203021187).
- VDI 2230 Part 1 (2015). "Systematic Calculation of Highly Stressed Bolted Joints," Verein Deutscher Ingenieure.

---

## 38. Friction Model Comparison and Selection Guide

### 38.1 Comprehensive Feature Comparison

| Feature | Regularized Coulomb | Dahl | LuGre | Iwan | Three-Phase |
|:--------|:-------------------:|:----:|:-----:|:----:|:-----------:|
| **Pre-sliding displacement** | No | Yes | Yes | Yes | N/A |
| **Rate (velocity) dependence** | Weak (Stribeck) | No | Yes | No | N/A |
| **Hysteresis in F-x plane** | No | Yes | Yes | Yes | N/A |
| **Stick-slip transitions** | Approximate | Good | Excellent | Excellent | N/A |
| **Stribeck effect** | Yes (algebraic) | No | Yes (dynamic) | No | N/A |
| **Friction lag** | No | No | Yes | No | N/A |
| **Friction memory** | No | 1-step | 1-step | Full history | N/A |
| **Cycle-dependent evolution** | No | No | No | No | Yes |
| **Energy dissipation law** | $\propto F^2$ | $\propto x^{2+1/\alpha}$ | (nonlinear) | $\propto F^{\chi+3}$ | N/A |
| **State variables** | 0 | 1 | 1 | $n$ | 1 |
| **Parameters to identify** | 2--4 | 3 | 7 | 4 + $n$ | 8 |
| **Computational cost** | Very low | Low | Medium | High | Very low |
| **Steady-state accuracy** | Good | Good | Excellent | Good | N/A |
| **Transient accuracy** | Low | Medium | High | High | N/A |
| **Numerical robustness** | Excellent | Good | Good (implicit) | Good | Excellent |

### 38.2 Detailed Model Comparison on Bolted Joint Test Cases

The following table compares the models on three canonical bolted joint scenarios:

| Scenario | Best Model | Why |
|:---------|:-----------|:----|
| **Quick loosening estimate** (< 1000 cycles) | Regularized Coulomb | Fastest computation, adequate for design screening |
| **Junker test simulation** (< 10,000 cycles, 5--50 Hz) | LuGre + Three-Phase | Captures within-cycle dynamics and cycle-to-cycle evolution |
| **Long-term service** ($> 10^5$ cycles) | Three-Phase + Coupled Preload | Friction evolution dominates; within-cycle details average out |
| **Modal analysis** (frequency response) | Iwan | Correct energy dissipation exponent for joint damping |
| **Pre-sliding behavior** (microslip studies) | Dahl or Iwan | Displacement-dependent models capture partial slip |
| **Detailed stick-slip dynamics** | LuGre | Only model with rate-dependent state and Stribeck transitions |
| **High-temperature joints** (> 300 C) | Three-Phase (modified) | Coating degradation and oxidation dominate |

### 38.3 Decision Flowchart

```
START: What is your analysis goal?
  |
  +-- Quick design calculation?
  |      |
  |      YES --> Use Regularized Coulomb (Section 31)
  |               Fast, simple, 2-4 parameters
  |
  +-- Detailed loosening dynamics?
  |      |
  |      +-- Velocity effects important?
  |      |      |
  |      |      YES --> Use LuGre (Section 32)
  |      |               7 parameters, captures Stribeck + pre-sliding
  |      |
  |      +-- Only displacement effects?
  |      |      |
  |      |      YES --> Use Dahl (Section 33)
  |      |               3 parameters, simpler than LuGre
  |      |
  |      +-- Energy dissipation critical?
  |             |
  |             YES --> Use Iwan (Section 34)
  |                      Power-law energy dissipation W ~ F^beta
  |
  +-- Long-term evolution (> 1000 cycles)?
  |      |
  |      YES --> Use Three-Phase Evolution (Section 35)
  |               Coupled with any of the above for within-cycle behavior
  |
  +-- Preload-friction interaction important?
         |
         YES --> Use Coupled Friction-Preload (Section 36)
                  Adds bidirectional feedback to Three-Phase model
```

### 38.4 Parameter Identification Guidelines

**From Junker test data (preload vs. cycles):**
1. Fit the overall decay curve to identify Three-Phase parameters ($\mu_0$, $\mu_{peak}$, $\mu_{ss}$, $N_1$, $N_2$, $N_3$).
2. The initial loosening rate gives the effective $\mu_0$.
3. The transition from fast to slow loosening gives $N_1$ and $N_2$.

**From dynamic shear test (force vs. displacement loops):**
1. Initial slope gives the contact stiffness ($\sigma_0$ for LuGre/Dahl, $K_T$ for Iwan).
2. Loop area gives the energy dissipation, which constrains $\chi$ for the Iwan model.
3. The maximum force gives $F_s$ or $F_c$.

**From torque-tension test (tightening torque vs. preload):**
1. The K-factor $K = T/(F_p \cdot d)$ gives the overall $\mu_{total}$.
2. Split between $\mu_t$ and $\mu_b$ using the VDI 2230 formulas or by testing with a torque washer.

**Standard surface condition parameters (BAS built-in library):**

| Surface Condition | $\mu_s$ | $\mu_k$ | $F_s$ (N) | $F_c$ (N) |
|:------------------|:-------:|:-------:|:---------:|:---------:|
| Bare steel | 0.20 | 0.15 | 200 | 150 |
| Zinc-phosphate | 0.15 | 0.12 | 150 | 120 |
| MoS$_2$ | 0.08 | 0.06 | 80 | 60 |
| PTFE | 0.06 | 0.04 | 60 | 40 |

### 38.5 Computational Performance Considerations

The choice of friction model has a direct impact on computation time:

| Model | Operations per step | Typical time for 10,000 cycles at 100 Hz |
|:------|:-------------------:|:-----------------------------------------:|
| Regularized Coulomb | $O(1)$ | < 1 second |
| Dahl | $O(1)$ | 1--2 seconds |
| LuGre | $O(1)$ | 2--5 seconds |
| Iwan ($n = 50$) | $O(n)$ | 10--30 seconds |
| Three-Phase (per cycle) | $O(1)$ | Negligible overhead |

For parametric studies or optimization runs that require thousands of analysis cases, the Regularized Coulomb model with Three-Phase evolution offers the best balance of accuracy and speed.

### 38.6 Eccles Experimental Validation

Eccles (2010) conducted an extensive experimental study of bolt friction during transverse vibration loosening tests, providing validation data for the models implemented in BAS. Key findings from that work include:

1. **Thread friction is not constant during loosening.** The effective $\mu_t$ decreases by 10--30% over the first 100 cycles (consistent with the Three-Phase model, Phase I).
2. **Bearing friction shows a running-in peak.** An initial increase of $\sim$20% is typical for zinc-phosphate coated bolts (consistent with Phase I, $\mu_{peak} / \mu_0 \approx 1.2$).
3. **Loosening rate accelerates after preload drops below ~50%.** This is consistent with the positive feedback mechanism described in Section 36.
4. **Lubricated bolts loosen faster than dry bolts** at the same preload level, confirming the direct relationship between friction coefficient and loosening resistance.

### 38.7 References for This Section

- Eccles, W. (2010). *Tribological Aspects of the Self-Loosening of Threaded Fasteners*, Ph.D. Thesis, University of Central Lancashire (UCLan), Preston, UK.
- Junker, G.H. (1969). "New Criteria for Self-Loosening of Fasteners Under Vibration," *SAE Transactions*, Vol. 78, pp. 314--335. SAE Paper 690055.
- Budynas, R.G. and Nisbett, J.K. (2020). *Shigley's Mechanical Engineering Design*, 11th ed., McGraw-Hill.

---

## References

### Friction Model Foundations

1. Amontons, G. (1699). "De la resistance causee dans les machines," *Memoires de l'Academie Royale*, pp. 206--222.

2. Coulomb, C.A. (1785). "Theorie des machines simples," *Memoires de Mathematique et de Physique de l'Academie Royale des Sciences*, Vol. 10, pp. 161--342.

3. Stribeck, R. (1902). "Die wesentlichen Eigenschaften der Gleit- und Rollenlager," *Zeitschrift des Vereins Deutscher Ingenieure*, Vol. 46, pp. 1341--1348, 1432--1438, 1463--1470.

### Dynamic Friction Models

4. Dahl, P.R. (1976). "Solid Friction Damping of Mechanical Vibrations," *AIAA Journal*, Vol. 14, No. 12, pp. 1675--1682. DOI: [10.2514/3.61511](https://doi.org/10.2514/3.61511).

5. Canudas de Wit, C., Olsson, H., Astrom, K.J., and Lischinsky, P. (1995). "A New Model for Control of Systems with Friction," *IEEE Transactions on Automatic Control*, Vol. 40, No. 3, pp. 419--425. DOI: [10.1109/9.376053](https://doi.org/10.1109/9.376053).

6. Olsson, H., Astrom, K.J., Canudas de Wit, C., Gafvert, M., and Lischinsky, P. (1998). "Friction Models and Friction Compensation," *European Journal of Control*, Vol. 4, No. 3, pp. 176--195. DOI: [10.1016/S0947-3580(98)70113-X](https://doi.org/10.1016/S0947-3580(98)70113-X).

### Iwan / Distributed Element Models

7. Iwan, W.D. (1966). "A Distributed-Element Model for Hysteresis and Its Steady-State Dynamic Response," *ASME Journal of Applied Mechanics*, Vol. 33, No. 4, pp. 893--900. DOI: [10.1115/1.3625199](https://doi.org/10.1115/1.3625199).

8. Segalman, D.J. (2002). "A Four-Parameter Iwan Model for Lap-Type Joints," *SAND2002-3828*, Sandia National Laboratories, Albuquerque, NM.

9. Segalman, D.J. (2005). "A Four-Parameter Iwan Model for Lap-Type Joints," *ASME Journal of Applied Mechanics*, Vol. 72, No. 5, pp. 752--760. DOI: [10.1115/1.1989354](https://doi.org/10.1115/1.1989354).

10. Brake, M.R.W. (2018). *The Mechanics of Jointed Structures*, Springer. DOI: [10.1007/978-3-319-56818-8](https://doi.org/10.1007/978-3-319-56818-8).

### Friction Evolution and Fretting

11. Hintikka, J., Lehtovaara, A., and Mantyla, A. (2019). "Stable and Unstable Friction in Fretting Contacts," *Tribology International*, Vol. 131, pp. 73--82. DOI: [10.1016/j.triboint.2018.10.014](https://doi.org/10.1016/j.triboint.2018.10.014).

12. Hintikka, J., Lehtovaara, A., and Mantyla, A. (2020). "Running-in in Fretting, Transition from near-stable to unstable friction," *Tribology International*, Vol. 143, Art. 106073. DOI: [10.1016/j.triboint.2019.106073](https://doi.org/10.1016/j.triboint.2019.106073).

13. Fouvry, S., Liskiewicz, T., Paulin, C., and Pauber, T. (2007). "A Global-Local Wear Approach to Quantify the Contact Endurance Under Reciprocating-Fretting Sliding Conditions," *Wear*, Vol. 263, No. 1--6, pp. 518--531. DOI: [10.1016/j.wear.2007.01.072](https://doi.org/10.1016/j.wear.2007.01.072).

### Bolted Joint Loosening and Friction

14. Junker, G.H. (1969). "New Criteria for Self-Loosening of Fasteners Under Vibration," *SAE Transactions*, Vol. 78, pp. 314--335. SAE Paper 690055. DOI: [10.4271/690055](https://doi.org/10.4271/690055).

15. Pai, N.G. and Hess, D.P. (2002). "Three-Dimensional Finite Element Analysis of Threaded Fastener Loosening due to Dynamic Shear Load," *Engineering Failure Analysis*, Vol. 9, No. 4, pp. 383--402. DOI: [10.1016/S1350-6307(01)00024-3](https://doi.org/10.1016/S1350-6307(01)00024-3).

16. Jiang, Y., Zhang, M., and Lee, C.H. (2003). "A Study of Early Stage Self-Loosening of Bolted Joints," *ASME Journal of Mechanical Design*, Vol. 125, No. 3, pp. 518--526. DOI: [10.1115/1.1586936](https://doi.org/10.1115/1.1586936).

17. Eccles, W. (2010). *Tribological Aspects of the Self-Loosening of Threaded Fasteners*, Ph.D. Thesis, University of Central Lancashire (UCLan), Preston, UK.

### General Mechanical Engineering References

18. Budynas, R.G. and Nisbett, J.K. (2020). *Shigley's Mechanical Engineering Design*, 11th ed., McGraw-Hill.

19. VDI 2230 Part 1 (2015). "Systematic Calculation of Highly Stressed Bolted Joints -- Joints with One Cylindrical Bolt," Verein Deutscher Ingenieure.

20. Mindlin, R.D. (1949). "Compliance of Elastic Bodies in Contact," *ASME Journal of Applied Mechanics*, Vol. 16, pp. 259--268.

### Contact Mechanics and Tribology

21. Oden, J.T. and Martins, J.A.C. (1985). "Models and computational methods for dynamic friction phenomena," *Computer Methods in Applied Mechanics and Engineering*, Vol. 52, No. 1--3, pp. 527--634. DOI: [10.1016/0045-7825(85)90009-X](https://doi.org/10.1016/0045-7825(85)90009-X).

22. Karnopp, D. (1985). "Computer simulation of stick-slip friction in mechanical dynamic systems," *ASME Journal of Dynamic Systems, Measurement, and Control*, Vol. 107, No. 1, pp. 100--103. DOI: [10.1115/1.3140698](https://doi.org/10.1115/1.3140698).

23. Hamrock, B.J., Schmid, S.R., and Jacobson, B.O. (2004). *Fundamentals of Fluid Film Lubrication*, 2nd ed., Marcel Dekker. DOI: [10.1201/9780203021187](https://doi.org/10.1201/9780203021187).

---

**END OF PART VII**

*Part VI covers Wear Models (Archard, Fouvry, Fretting, Wear-Geometry Coupling)*
*Part VIII covers Numerical Solvers (Newmark-beta, HHT-alpha, Central Difference, RK4, Modal Superposition)*
*Part XI covers the Coupled Friction-Wear-Loosening Analysis Framework*
*Part XII covers Force Excitation Functions and Rayleigh Damping*
