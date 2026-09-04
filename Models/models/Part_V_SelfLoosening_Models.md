# MSD Framework -- PART V: Self-Loosening Models

**Complete Technical Reference for Bolt Analysis Studio**

**Authors:** L. Ribeiro, D. Carvalho, S.C. Naves, T. Santos, V. Marques, G. Arruda
**Institution:** internal reference -- Tribology and Wear Technology Laboratory, Federal University of Uberlândia
**Project:** Petrobras R&D -- Bolted Flange Joint Integrity

---

**Abstract.** This document provides a comprehensive mathematical treatment of all self-loosening models implemented in the Bolt Analysis Studio (BAS). Starting from the seminal work of Junker (1969), we trace the development of loosening theory through Pai and Hess's localized slip extension, Jiang's multi-stage framework, and modern coupled friction-wear-loosening formulations. Each model is presented with complete governing equations, physical motivation, parameter ranges, and relevant literature citations. The treatment is intended as a self-contained reference for engineers and researchers working on bolted joint integrity in vibration environments.

---

## Table of Contents

- [20. The Self-Loosening Problem](#20-the-self-loosening-problem)
- [21. Junker Rotational Loosening Mechanism](#21-junker-rotational-loosening-mechanism)
- [22. Pai-Hess Localized Slip Theory](#22-pai-hess-localized-slip-theory)
- [23. Jiang Two-Stage Model](#23-jiang-two-stage-model)
- [24. Jiang Three-Stage Extended Model](#24-jiang-three-stage-extended-model)
- [25. Two-Stage S-Curve Model](#25-two-stage-s-curve-model)
- [26. Nassar-Housari Thread and Bearing Friction Models](#26-nassar-housari-thread-and-bearing-friction-models)
- [27. Per-Thread Self-Loosening Analysis](#27-per-thread-self-loosening-analysis)
- [28. Coupled Friction-Wear-Loosening System](#28-coupled-friction-wear-loosening-system)
- [29. Preload Loss from Rotation](#29-preload-loss-from-rotation)
- [30. Design Against Self-Loosening](#30-design-against-self-loosening)
- [References](#references)

---

## 20. The Self-Loosening Problem

### 20.1 Historical Context

The self-loosening of threaded fasteners under dynamic loading has been recognized as an engineering problem since the early twentieth century. However, it was Gerhard H. Junker's landmark 1969 paper that established the foundational understanding of the phenomenon. Using his transverse vibration test apparatus -- now standardized as DIN 65151 and referred to universally as the "Junker test" -- he demonstrated conclusively that **transverse (shear) vibration, not axial vibration, is the dominant cause of bolt self-loosening** (Junker, 1969).

Prior to Junker's work, the prevailing assumption was that cyclic axial loading was the primary loosening driver. Junker showed that purely axial loading, even at amplitudes exceeding the yield strength of the bolt, does not cause significant rotational loosening. In contrast, relatively modest transverse displacements -- as small as 0.3 mm -- can cause complete loss of preload within a few hundred cycles under the right conditions.

This finding was revolutionary because most engineering practice at the time focused on providing high preload and axial clamping force without adequately considering the transverse load path through the joint.

### 20.2 Why Transverse Vibration Matters More Than Axial

The physical explanation for the dominance of transverse loading lies in the nature of frictional resistance at the contact interfaces. Under purely axial loading, the bearing surface friction forces remain aligned with their original directions and continue to resist any tendency for nut rotation. In contrast, transverse loads cause relative sliding between the clamped members. When this sliding exceeds the frictional capacity of the bearing surface, the bearing friction force becomes fully saturated and aligned with the sliding direction. At that instant, the friction force can no longer provide a restraining torque against nut rotation. The ever-present pitch torque -- an inherent consequence of the helical thread geometry -- is then free to drive the nut in the loosening direction.

This can be understood through a simple analogy: a bolt on a helical ramp (the thread) is held in place by friction at its base (the bearing surface). When the base is shaken sideways hard enough to overcome friction, the bolt slides down the ramp under its own weight (the pitch torque).

### 20.3 Industrial Significance

In the oil and gas industry, bolted connections are ubiquitous in pressure-containing equipment: flanged pipe joints, wellhead assemblies, subsea connectors, and pressure vessel closures. The Petrobras R&D context of this work underscores the critical nature of self-loosening in offshore environments, where vibration from wave loading, machinery, and fluid flow creates sustained transverse excitation. Loss of bolt preload in a flanged connection can lead to gasket leakage, loss of containment, and potentially catastrophic environmental and safety consequences.

The self-loosening problem is particularly insidious because it is progressive and often undetectable until a joint has lost a significant fraction of its preload. By the time external symptoms (leakage, visible gap, bolt rotation) become apparent, the joint may already be in a compromised state. This motivates the development of predictive models that can estimate loosening rates and remaining preload as a function of loading parameters, friction conditions, and joint geometry -- precisely the role served by the models implemented in the Bolt Analysis Studio.

**References:**
- Junker, G.H. (1969). "New Criteria for Self-Loosening of Fasteners Under Vibration." SAE Technical Paper 690055.
- Bickford, J.H. (2008). *Introduction to the Design and Behavior of Bolted Joints*, 4th ed. CRC Press.
- VDI 2230 Part 1 (2015). "Systematic Calculation of Highly Stressed Bolted Joints -- Joints with One Cylindrical Bolt." Verein Deutscher Ingenieure.

---

## 21. Junker Rotational Loosening Mechanism

### 21.1 The Four-Step Mechanism

The Junker loosening mechanism can be decomposed into four sequential steps that occur within each half-cycle of transverse vibration. Understanding this sequence is essential for appreciating the torque balance equations that follow.

```
    STEP 1                STEP 2                STEP 3                STEP 4
  Transverse          Bearing Surface         Thread Friction       Pitch Torque
  Force Applied       Slips                   Effectively Zero      Drives Rotation

   F_trans              Slipping!              mu_t --> 0            Nut rotates!
  ---------> +---------+ ====>  +---------+    +---------+          +---------+
             |  HEAD   |        |  HEAD   |    |  HEAD   |          |  HEAD   |
             +----+----+        +----+----+    +----+----+          +----+----+
                  |                  |               |                  | \
                  |                  |               |                  |  \
              ====|====         ====|====        ====|====          ====|====
              FLANGE            FLANGE  ====>   FLANGE             FLANGE
                  |                  |               |                  |
              +---+---+         +---+---+       +---+---+          +---+---+
              |  NUT  |         |  NUT  |       |  NUT  |          | NUT   | <-- rotates
              +-------+         +-------+       +-------+          +-------+
                                                                     theta

  F_trans >           Friction at bearing     With both surfaces    T_pitch = F_p * p/(2*pi)
  mu_b * F_p ?        overcome; relative      slipping, thread      is unresisted and drives
                      sliding at interface    friction cannot        nut backward down the
                                              prevent rotation      helix
```

**Step 1 -- Transverse force applied.** An external transverse (shear) force $F_{\mathrm{trans}}$ is applied to the clamped members, arising from vibration, thermal cycling, or operational loads.

**Step 2 -- Bearing surface slips.** When the transverse force exceeds the friction capacity of the bearing surface, the interface begins to slide:

$$|F_{\mathrm{trans}}| > \mu_b \cdot F_p$$

where $\mu_b$ is the bearing surface friction coefficient and $F_p$ is the current bolt preload. At this point, the entire friction force at the bearing surface is "consumed" in resisting the transverse sliding and is no longer available to resist nut rotation.

**Step 3 -- Thread friction effectively reduced.** During the bearing slip event, the thread interface also experiences relative motion in the transverse direction. The thread friction force reorients to oppose the transverse slip, and its component in the circumferential (rotation-resisting) direction is greatly diminished or effectively zero. This is the critical insight of Junker's analysis.

**Step 4 -- Pitch torque drives nut rotation.** With both frictional barriers reduced, the pitch torque -- which is always present as a consequence of the helical thread geometry and the tensile preload in the bolt -- drives the nut in the loosening (back-off) direction. Each half-cycle of transverse vibration produces a small increment of nut rotation, and these increments accumulate over thousands of cycles to produce significant preload loss.

### 21.2 Torque Balance Equations

The torque balance at the threaded fastener during a loosening event involves three principal torque components.

**Pitch torque** (drives loosening):

$$T_{\mathrm{pitch}} = F_p \cdot \frac{p}{2\pi}$$

This torque arises from the axial preload force $F_p$ acting on the helical inclined plane of the thread, where $p$ is the thread pitch. It acts in the loosening (back-off) direction and is an intrinsic consequence of the helix geometry. It is the "gravitational" force on the helical ramp analogy.

**Thread friction torque** (resists loosening):

$$T_{\mathrm{thread}} = \frac{\mu_t \cdot F_p \cdot d_2}{2 \cos\alpha}$$

where:
- $\mu_t$ is the thread friction coefficient,
- $d_2$ is the pitch diameter of the thread,
- $\alpha$ is the half flank angle of the thread (30 degrees for ISO metric threads).

The factor $1/\cos\alpha$ accounts for the wedging action of the thread flanks: the normal force between the thread flanks is amplified by $\sec\alpha$ relative to the axial force, and friction acts on this amplified normal force.

**Bearing friction torque** (resists loosening):

$$T_{\mathrm{bearing}} = \mu_b \cdot F_p \cdot r_{\mathrm{eff}}$$

where $r_{\mathrm{eff}}$ is the effective (load-weighted) bearing radius. For an annular contact between inner radius $r_i$ (hole diameter) and outer radius $r_o$ (under-head diameter), the effective radius is:

$$r_{\mathrm{eff}} = \frac{2}{3} \cdot \frac{r_o^3 - r_i^3}{r_o^2 - r_i^2}$$

This expression arises from integrating the moment contribution of the uniform pressure distribution over the annular contact area, assuming a flat annular bearing surface. The $2/3$ factor is the centroid-to-integration result for an annular contact with uniform pressure.

### 21.3 Loosening Criterion

Self-loosening occurs when the driving pitch torque exceeds the total resisting torque:

$$T_{\mathrm{pitch}} > T_{\mathrm{thread}} + T_{\mathrm{bearing}}$$

Substituting the expressions above:

$$F_p \cdot \frac{p}{2\pi} > \frac{\mu_t \cdot F_p \cdot d_2}{2\cos\alpha} + \mu_b \cdot F_p \cdot r_{\mathrm{eff}}$$

Since $F_p$ cancels (assuming $F_p > 0$), this yields a condition purely in terms of geometry and friction:

$$\frac{p}{2\pi} > \frac{\mu_t \cdot d_2}{2\cos\alpha} + \mu_b \cdot r_{\mathrm{eff}}$$

### 21.4 Critical Friction Coefficient

Assuming equal thread and bearing friction ($\mu_t = \mu_b = \mu$), the critical friction coefficient below which self-loosening is kinematically possible can be derived by setting the loosening criterion to equality:

$$\mu_{\mathrm{crit}} = \frac{p \cdot 2\cos\alpha}{2\pi \left( d_2 + 2 \cdot r_{\mathrm{eff}} \cdot \cos\alpha \right)}$$

This simplifies to:

$$\mu_{\mathrm{crit}} = \frac{p \cos\alpha}{\pi d_2 + 2\pi r_{\mathrm{eff}} \cos\alpha}$$

For a typical M16 bolt ($p = 2$ mm, $d_2 = 14.701$ mm, $\alpha = 30°$, $r_{\mathrm{eff}} \approx 10$ mm), this gives $\mu_{\mathrm{crit}} \approx 0.024$, which is well below any practical unlubricated metal-on-metal friction coefficient ($\mu \approx 0.12$--$0.20$). This confirms that **under static conditions, self-loosening should not occur**. It is only the dynamic transverse slip that circumvents the friction barriers, as described in the four-step mechanism above.

### 21.5 Torque Margin

The BAS software defines the **torque margin** as:

$$\text{Torque Margin} = \frac{T_{\mathrm{resistance}}}{T_{\mathrm{pitch}}} = \frac{T_{\mathrm{thread}} + T_{\mathrm{bearing}}}{T_{\mathrm{pitch}}}$$

A torque margin greater than 1.0 indicates static stability (no loosening under static conditions). The margin erodes during dynamic operation as friction degrades and preload decreases, eventually approaching and potentially crossing the unity threshold.

**References:**
- Junker, G.H. (1969). "New Criteria for Self-Loosening of Fasteners Under Vibration." SAE Technical Paper 690055.
- VDI 2230 Part 1 (2015). "Systematic Calculation of Highly Stressed Bolted Joints."
- Bickford, J.H. (2008). *Introduction to the Design and Behavior of Bolted Joints*, 4th ed. CRC Press. Chapter 15.

---

## 22. Pai-Hess Localized Slip Theory

### 22.1 Extension of the Junker Mechanism

Pai and Hess (2002a, 2002b) extended Junker's original analysis through both three-dimensional finite element simulations and experimental studies. Their key contribution was demonstrating that **self-loosening can occur even with localized (partial) slip** -- that is, when only one of the two bearing surfaces (bolt head or nut) experiences transverse slip, while the other remains in a sticking state.

This was a significant departure from the classical Junker understanding, which implicitly required complete slip at both interfaces. Pai and Hess showed that the relative torsional compliance of the bolt shank allows differential rotation between the head and nut ends, so that loosening can occur even when only one end slips.

### 22.2 Four Slip Regimes

The Pai-Hess framework classifies the instantaneous state of the joint into four regimes based on the slip conditions at the two bearing surfaces:

```
  REGIME 1: NO SLIP                   REGIME 2: HEAD ONLY

  +---------+                         +---------+
  |  HEAD   | STICK                   |  HEAD   | ==> SLIP
  +----+----+                         +----+----+
       |                                   |
   ====|==== FLANGE                    ====|==== FLANGE
       |                                   |
  +----+----+                         +----+----+
  |   NUT   | STICK                   |   NUT   | STICK
  +---------+                         +---------+

  No loosening.                       Partial loosening: head end
  Both interfaces locked.             rotates, nut end fixed.
                                      Bolt shank provides torsional
                                      compliance for differential
                                      rotation.


  REGIME 3: NUT ONLY                  REGIME 4: COMPLETE SLIP

  +---------+                         +---------+
  |  HEAD   | STICK                   |  HEAD   | ==> SLIP
  +----+----+                         +----+----+
       |                                   |
   ====|==== FLANGE                    ====|==== FLANGE
       |                                   |
  +----+----+                         +----+----+
  |   NUT   | ==> SLIP               |   NUT   | ==> SLIP
  +---------+                         +---------+

  Partial loosening: nut end          Maximum loosening rate.
  rotates, head end fixed.            Both interfaces slipping
  Mirror of Regime 2.                 simultaneously. Classic
                                      Junker mechanism fully
                                      activated.
```

**Regime 1 -- NO_SLIP:** Neither the bolt head nor the nut bearing surface is slipping. The transverse force is entirely accommodated by static friction at both interfaces. No loosening occurs. This regime prevails when:

$$|F_{\mathrm{trans}}| < \min\left(\mu_{\mathrm{head}} \cdot F_p, \; \mu_{\mathrm{nut}} \cdot F_p\right)$$

**Regime 2 -- HEAD_ONLY:** The bolt head bearing surface slips while the nut bearing surface remains stuck. This occurs when $\mu_{\mathrm{head}} < \mu_{\mathrm{nut}}$ (or the head has a larger effective radius, making it more susceptible to sliding). Loosening occurs at a reduced rate because only one end of the bolt is free to rotate.

**Regime 3 -- NUT_ONLY:** The nut bearing surface slips while the bolt head remains stuck. This is the mirror of Regime 2 and occurs when $\mu_{\mathrm{nut}} < \mu_{\mathrm{head}}$ or the nut has less resistance to transverse sliding.

**Regime 4 -- COMPLETE_SLIP:** Both bearing surfaces are slipping simultaneously. This produces the maximum loosening rate and corresponds exactly to the classical Junker mechanism. It occurs when:

$$|F_{\mathrm{trans}}| > \max\left(\mu_{\mathrm{head}} \cdot F_p, \; \mu_{\mathrm{nut}} \cdot F_p\right)$$

### 22.3 Physical Explanation of Localized Slip Loosening

The physical mechanism underlying localized slip loosening can be understood through the torsional compliance of the bolt shank. When only one bearing surface slips, the bolt shank acts as a torsional spring connecting the slipping end to the fixed end. The net torque at the slipping end (pitch torque minus thread friction) produces a small torsional wind-up of the shank. When the transverse load reverses direction, the shank unwinds, but due to the helical geometry, the net effect over a complete cycle is a small ratcheting rotation in the loosening direction.

The loosening rate under partial slip is lower than under complete slip -- typically by a factor of 3 to 5 -- but is nonzero and can accumulate over many thousands of cycles.

### 22.4 Implementation in BAS

In the BAS coupled loosening analyzer, the slip state is evaluated at each cycle:

$$\text{Bearing slipping:} \quad |F_{\mathrm{trans}}| > \mu_b \cdot F_p$$

$$\text{Thread slipping:} \quad |F_{\mathrm{trans}}| > \mu_t \cdot F_p \cdot \cos\lambda$$

where $\lambda$ is the helix angle. The loosening rate is then computed based on the combined slip state:

- **Complete slip** (both surfaces): Full Junker loosening rate applies.
- **Partial slip** (one surface only): A reduced loosening rate, approximately $10^{-4} \times (\text{excess force} / F_p)$ per cycle, is applied.
- **No slip**: Zero loosening rate, unless the static torque margin is already below 1.0.

**References:**
- Pai, N.G. and Hess, D.P. (2002a). "Three-Dimensional Finite Element Analysis of Threaded Fastener Loosening due to Dynamic Shear Load." *Engineering Failure Analysis*, Vol. 9, No. 4, pp. 383--402. DOI: 10.1016/S1350-6307(01)00024-3.
- Pai, N.G. and Hess, D.P. (2002b). "Experimental Study of Loosening of Threaded Fasteners due to Dynamic Shear Loads." *Journal of Sound and Vibration*, Vol. 253, No. 3, pp. 585--602. DOI: 10.1006/jsvi.2001.4006.

---

## 23. Jiang Two-Stage Model

### 23.1 Overview

Jiang, Zhang, and Lee (2003) conducted a systematic experimental and computational study of self-loosening and identified **two distinct stages** in the loosening process, each governed by a fundamentally different physical mechanism. This two-stage framework has become one of the most widely cited models in the loosening literature and forms a central component of the BAS analysis engine.

### 23.2 Stage I: Non-Rotational Loosening

**Physical mechanism.** In the early phase of cyclic loading (typically the first 100--500 cycles), the bolt preload decreases without any detectable nut rotation. This preload loss arises from:

1. **Embedding (surface settling):** Microscopic asperities on the contacting surfaces are plastically deformed under the high contact pressures, reducing the effective grip length and thus the bolt elongation.
2. **Localized cyclic plastic deformation:** Stress concentrations at thread roots experience cyclic plasticity, which progressively reduces the elastic strain energy stored in the bolt.
3. **Surface roughness flattening:** The initial surface roughness at bearing surfaces and thread flanks is gradually worn and flattened, reducing the effective interface compliance.

**Mathematical model.** Stage I preload decay follows a saturating exponential:

$$F_p(N) = F_{p,0} - \Delta F_{\mathrm{embed}} \cdot \left[1 - \exp\left(-\frac{N}{N_1}\right)\right]$$

where:
- $F_{p,0}$ is the initial preload [N],
- $\Delta F_{\mathrm{embed}}$ is the maximum Stage I preload loss [N], typically 5--15% of $F_{p,0}$,
- $N_1$ is the characteristic cycle count for Stage I [cycles], typically 50--100,
- $N$ is the current cycle number.

The exponential saturation form captures the self-limiting nature of embedding: once the asperities have been flattened, further cycling produces diminishing additional settlement.

**Characteristic values.** From Jiang et al. (2003):
- Duration: 100--500 cycles.
- Preload loss: 5--15% of initial preload.
- Nut rotation: less than 0.5 degrees (not macroscopically detectable).

### 23.3 Stage II: Rotational Loosening

**Physical mechanism.** After the transition, the Junker mechanism (Section 21) becomes the dominant loosening mode. The nut begins to rotate progressively, driven by the pitch torque during transverse slip events. The preload decay rate in Stage II is approximately linear with cycle count.

**Mathematical model.** Stage II is modeled as linear decay:

$$F_p(N) = F_{\mathrm{trans}} - k_2 \cdot (N - N_{\mathrm{trans}})$$

where:
- $F_{\mathrm{trans}}$ is the preload at the Stage I/II transition [N],
- $k_2$ is the Stage II decay rate [N/cycle],
- $N_{\mathrm{trans}}$ is the transition cycle number.

The linear decay in Stage II contrasts with the saturating exponential of Stage I and reflects the steady ratcheting rotation driven by the Junker mechanism.

### 23.4 Transition Criteria

The transition from Stage I to Stage II is identified by any of the following criteria:

1. **Nut rotation exceeds 0.5 degrees.** This threshold, identified experimentally by Jiang et al. (2003), marks the onset of macroscopic nut rotation. Below 0.5 degrees, preload loss is dominated by plastic deformation (Stage I); above 0.5 degrees, rotational back-off (Stage II) takes over.

2. **Preload drops to approximately 85--90% of initial.** This empirical threshold correlates with the exhaustion of Stage I mechanisms.

3. **Cycle count exceeds $N_{\mathrm{trans}}$.** A nominal value of 100--500 cycles, depending on bolt size, surface finish, and loading amplitude.

### 23.5 Complete Piecewise Model

Combining both stages:

$$F_p(N) = \begin{cases}
F_{p,0} - \Delta F_{\mathrm{embed}} \cdot \left[1 - \exp\left(-\dfrac{N}{N_1}\right)\right] & \text{for } N \leq N_{\mathrm{trans}} \\[8pt]
F_{\mathrm{trans}} - k_2 \cdot (N - N_{\mathrm{trans}}) & \text{for } N > N_{\mathrm{trans}}
\end{cases}$$

where $F_{\mathrm{trans}} = F_{p,0} - \Delta F_{\mathrm{embed}} \cdot [1 - \exp(-N_{\mathrm{trans}}/N_1)]$.

**References:**
- Jiang, Y., Zhang, M., and Lee, C.H. (2003). "A Study of Early Stage Self-Loosening of Bolted Joints." *ASME Journal of Mechanical Design*, Vol. 125, No. 3, pp. 518--526. DOI: 10.1115/1.1586936.
- Jiang, Y., Zhang, M., Park, T.W., and Lee, C.H. (2004). "An Experimental Study of Self-Loosening of Bolted Joints." *ASME Journal of Mechanical Design*, Vol. 126, No. 5, pp. 925--931. DOI: 10.1115/1.1767814.

---

## 24. Jiang Three-Stage Extended Model

### 24.1 Motivation

While the two-stage model captures the essential physics for moderate cycle counts, extended testing reveals a third stage at very high cycle counts. Gong, Liu, and Ding (2019) demonstrated that after many tens of thousands of cycles, **fatigue damage accumulation** at thread roots leads to an accelerated loosening rate that exceeds the linear Stage II prediction. Yang et al. (2021) further corroborated this finding with experimental evidence of fatigue-driven acceleration.

### 24.2 Stage III: Fatigue-Accelerated Loosening

**Physical mechanism.** Cyclic loading at thread roots (regions of high stress concentration with $K_t \approx 3$--$5$) initiates fatigue microcracks. As these cracks propagate, they:

1. Reduce the effective cross-sectional area of the bolt, decreasing bolt stiffness.
2. Create additional compliance at the thread interface, allowing greater relative slip per cycle.
3. Accelerate wear and surface damage at the crack flanks.

The result is a super-linear increase in loosening rate after the onset of Stage III.

**Mathematical model.** The three-stage model extends the piecewise formulation:

$$F_p(N) = \begin{cases}
F_{p,0} - \Delta F_1 \cdot \left[1 - \exp\left(-\dfrac{N}{N_1}\right)\right] & \text{for } N \leq N_{\mathrm{trans},12} \\[8pt]
F_{\mathrm{trans},12} - k_2 \cdot (N - N_{\mathrm{trans},12}) & \text{for } N_{\mathrm{trans},12} < N \leq N_{\mathrm{trans},23} \\[8pt]
F_{\mathrm{trans},23} - k_3 \cdot (N - N_{\mathrm{trans},23})^{n_3} & \text{for } N > N_{\mathrm{trans},23}
\end{cases}$$

where:
- $N_{\mathrm{trans},12}$ is the Stage I to Stage II transition (~500 cycles),
- $N_{\mathrm{trans},23}$ is the Stage II to Stage III transition (~50,000 cycles),
- $k_3$ is the Stage III base decay rate,
- $n_3$ is the acceleration exponent, typically $n_3 \approx 1.5$.

The power-law form in Stage III captures the accelerating nature of fatigue-driven loosening: as fatigue damage accumulates, the loosening rate increases progressively rather than remaining constant as in Stage II.

### 24.3 Preload at Transition Points

$$F_{\mathrm{trans},12} = F_{p,0} - \Delta F_1 \cdot \left[1 - \exp\left(-\frac{N_{\mathrm{trans},12}}{N_1}\right)\right]$$

$$F_{\mathrm{trans},23} = F_{\mathrm{trans},12} - k_2 \cdot (N_{\mathrm{trans},23} - N_{\mathrm{trans},12})$$

### 24.4 Comparison of Two-Stage vs Three-Stage Predictions

For cycle counts below $N_{\mathrm{trans},23}$, the two-stage and three-stage models produce identical predictions. The divergence appears only at very high cycle counts, where the two-stage model predicts continued linear decay while the three-stage model predicts accelerating decay. This has important implications for life prediction: the two-stage model is non-conservative at very high cycle counts, potentially underestimating preload loss by 20--40% at $N > 10^5$ cycles.

**References:**
- Gong, H., Liu, J., and Ding, X. (2019). "Study on the Critical Loosening Condition Toward a New Design Guideline for Bolted Joints." *Proceedings of the Institution of Mechanical Engineers, Part C: Journal of Mechanical Engineering Science*, Vol. 233, No. 9, pp. 3302--3316. DOI: 10.1177/0954406218802928.
- Yang, G., Xie, J., and Xie, Y. (2021). "Study on Mechanism of Anti-Loosening of a New Type of Nut Based on Fem." *Materials*, Vol. 14, No. 15, Art. 4079.

---

## 25. Two-Stage S-Curve Model

### 25.1 Overview

The BAS implementation employs a **Two-Stage S-Curve Model** as its primary preload decay formulation for the coupled loosening analyzer. This model synthesizes the Jiang two-stage framework with the displacement-amplitude dependence documented by Yang and Nassar (2011), producing a smooth, continuous preload loss curve with the characteristic S-shaped profile observed in experimental data.

### 25.2 Displacement-Dependent Loosening

A critical finding from the experimental literature is that the loosening rate depends strongly and nonlinearly on the transverse displacement amplitude. Yang and Nassar (2011) demonstrated that the preload loss rate scales approximately as the square of the displacement amplitude:

$$F_{\mathrm{loss}} \propto \left(\frac{\delta}{\delta_{\mathrm{ref}}}\right)^{n_{\delta}}$$

where:
- $\delta$ is the transverse displacement amplitude [mm],
- $\delta_{\mathrm{ref}} = 0.65$ mm is the reference amplitude (DIN 65151 standard test condition),
- $n_{\delta} = 2.0$ is the displacement exponent.

Below a displacement threshold of approximately $\delta_{\mathrm{th}} = 0.15$ mm, no significant loosening occurs regardless of cycle count -- only minor embedding losses of the order of 2% are observed. This threshold corresponds to the condition where the transverse force never exceeds the friction capacity of the bearing surface, and the Junker mechanism cannot activate.

### 25.3 The S-Curve Formulation

The S-curve emerges from the combination of two components:

**Stage I loss (exponential saturation):**

$$F_{\mathrm{loss},1}(N) = \Delta F_1 \cdot \left[1 - \exp\left(-\frac{N}{N_1^{\mathrm{eff}}}\right)\right]$$

where:
- $\Delta F_1 = \delta_{F_1} \cdot F_{p,0}$ with $\delta_{F_1} = 0.15$ (15% maximum Stage I loss),
- $N_1^{\mathrm{eff}} = N_1 / f_{\delta}$ is the effective Stage I duration, shortened by larger displacements,
- $f_{\delta} = (\delta / 0.65)^{n_{\delta}}$ is the displacement factor, capped at 5.0.

**Stage II loss (sigmoid-activated linear accumulation):**

$$F_{\mathrm{loss},2}(N) = \sigma\!\left(\frac{N - N_1^{\mathrm{eff}}}{N_1^{\mathrm{eff}}}\right) \cdot k_2 \cdot f_{\delta} \cdot (N - N_1^{\mathrm{eff}})$$

where:
- $\sigma(x) = [1 + \exp(-\gamma \cdot x)]^{-1}$ is the sigmoid transition function,
- $\gamma = 3.0$ is the transition sharpness parameter,
- $k_2 = 10^{-4}$ is the Stage II decay rate coefficient [per cycle].

The sigmoid function provides a smooth, continuous transition between Stage I and Stage II, avoiding the discontinuity of the piecewise Jiang model.

### 25.4 Combined S-Curve Loss Factor

The total preload loss factor (fraction of initial preload lost) is:

$$\phi_{\mathrm{loss}}(N, \delta) = \min\!\left(F_{\mathrm{loss},1} + F_{\mathrm{loss},2}, \; 0.95 \cdot F_{p,0}\right) \;/\; F_{p,0}$$

The 95% cap prevents complete preload loss, reflecting the physical reality that some residual clamping typically persists even in severely loosened joints (due to gasket compression, thread interference, etc.).

### 25.5 Parameters

| Parameter | Symbol | Default | Range | Description |
|-----------|--------|---------|-------|-------------|
| Stage I cycles | $N_1$ | 200 | 50--500 | Characteristic Stage I duration |
| Stage I loss ratio | $\delta_{F_1}$ | 0.15 | 0.05--0.40 | Maximum fractional loss in Stage I |
| Stage II rate | $k_2$ | $10^{-4}$ | $10^{-5}$--$10^{-3}$ | Linear decay rate per cycle |
| Displacement exponent | $n_{\delta}$ | 2.0 | 1.5--3.0 | Power-law dependence on displacement |
| Transition sharpness | $\gamma$ | 3.0 | 1.0--10.0 | Sigmoid sharpness |
| Displacement threshold | $\delta_{\mathrm{th}}$ | 0.15 mm | 0.10--0.30 mm | Below this, minimal loosening |

**References:**
- Yang, X. and Nassar, S.A. (2011). "Analytical and Experimental Investigation of Self-Loosening of Preloaded Cap Screw Fasteners." *ASME Journal of Vibration and Acoustics*, Vol. 133, No. 3, Art. 031007. DOI: 10.1115/1.4003197.
- Jiang, Y., Zhang, M., and Lee, C.H. (2003). "A Study of Early Stage Self-Loosening of Bolted Joints." *ASME Journal of Mechanical Design*, Vol. 125, No. 3, pp. 518--526.

---

## 26. Nassar-Housari Thread and Bearing Friction Models

### 26.1 Effect of Thread Pitch on Loosening

Nassar and Housari (2006) conducted a systematic experimental study of the effect of thread pitch and initial tension on self-loosening. Their key findings include:

1. **Coarser threads loosen faster.** The pitch torque $T_{\mathrm{pitch}} = F_p \cdot p / (2\pi)$ is directly proportional to pitch. A coarser thread (larger $p$) produces a larger driving torque for the same preload, resulting in a higher loosening rate.

2. **Higher initial preload delays loosening onset.** Greater preload increases the friction capacity at both thread and bearing surfaces, requiring larger transverse forces to initiate slip.

3. **The ratio $p/d_2$ controls loosening susceptibility.** The dimensionless pitch ratio $p/d_2$ is a fundamental parameter governing the competition between pitch torque and thread friction.

The loosening angle per cycle was found to scale as:

$$\Delta\theta_{\mathrm{cycle}} \propto \frac{p}{d_2} \cdot \frac{1}{\mu_t} \cdot \left(\frac{F_{\mathrm{trans}}}{\mu_b \cdot F_p} - 1\right)$$

This expression captures the three essential factors: the helix geometry ($p/d_2$), the inverse dependence on friction ($1/\mu_t$), and the excess transverse force ratio.

### 26.2 Separate Thread and Bearing Friction Effects

Housari and Nassar (2007) extended this work to examine the independent effects of thread friction ($\mu_t$) and bearing friction ($\mu_b$):

1. **Bearing friction dominates loosening resistance.** The effective bearing radius $r_{\mathrm{eff}}$ is typically larger than the mean thread radius $r_m = d_2/2$, so the bearing friction torque exceeds the thread friction torque for equal friction coefficients. A 50% reduction in bearing friction produces approximately 3 times the loosening rate increase compared to the same reduction in thread friction.

2. **Thread friction controls the critical threshold.** The critical friction coefficient for loosening onset is determined primarily by the thread friction, since it is the thread that provides the pitch torque driving force.

3. **Different surface treatments at head and nut have asymmetric effects.** This connects to the Pai-Hess localized slip theory (Section 22): if the head bearing friction differs from the nut bearing friction, the slip regime and loosening rate are determined by the weaker (lower friction) surface.

### 26.3 Integral Formulation for Loosening Per Cycle

Nassar and Housari developed an integral formulation for computing the total nut rotation per loading cycle:

$$\Delta\theta_{\mathrm{cycle}} = \int_0^{T} \dot{\theta}_{\mathrm{loose}}(t) \, dt$$

where $\dot{\theta}_{\mathrm{loose}}(t)$ is the instantaneous loosening angular velocity, which is nonzero only during the intervals within each cycle when both bearing and thread surfaces are slipping. For sinusoidal transverse loading $F_{\mathrm{trans}}(t) = F_0 \sin(\omega t)$, the slip intervals are symmetric about the force peaks, and the integral can be evaluated analytically for idealized friction models.

In the BAS implementation, this integral is evaluated numerically by computing the slip state and loosening increment at each sub-step within a cycle.

**References:**
- Nassar, S.A. and Housari, B.A. (2006). "Effect of Thread Pitch and Initial Tension on the Self-Loosening of Threaded Fasteners." *ASME Journal of Pressure Vessel Technology*, Vol. 128, No. 4, pp. 590--598. DOI: 10.1115/1.2349574.
- Housari, B.A. and Nassar, S.A. (2007). "Effect of Thread and Bearing Friction Coefficients on the Vibration-Induced Loosening of Threaded Fasteners." *ASME Journal of Vibration and Acoustics*, Vol. 129, No. 4, pp. 484--494. DOI: 10.1115/1.2748473.

---

## 27. Per-Thread Self-Loosening Analysis

### 27.1 Why Per-Thread Analysis Matters

In a real bolted joint, the load is not uniformly distributed among the engaged threads. The first loaded thread (closest to the bearing surface) carries a disproportionately large fraction of the total axial load, while the last thread carries very little. This non-uniform distribution has profound implications for loosening:

1. **Heavily loaded threads slip first.** The first thread reaches its friction capacity before the others, initiating localized slip while the remaining threads are still in a sticking state.
2. **Wear is concentrated.** Archard wear scales linearly with normal force and sliding distance, so the heavily loaded threads wear faster, further redistributing load and potentially creating a progressive failure cascade.
3. **Loosening is not uniform.** Different threads may be in different slip states (sticking, partial slip, gross slip) at the same instant, requiring thread-by-thread evaluation for accurate prediction.

### 27.2 Thread Load Distribution Models

The BAS software implements five load distribution models, each representing a different assumption about the relative load carried by each engaged thread. For $n$ engaged threads, with thread $i = 1$ being the most heavily loaded:

**Uniform distribution:**

$$\phi_i = \frac{1}{n} \quad \text{for all } i$$

This is the simplest assumption and is often used as a baseline. It is physically unrealistic for most joints but provides an upper bound on fatigue life for the most loaded thread.

**Linear distribution:**

$$\phi_i = \frac{2(n - i + 1)}{n(n + 1)}$$

This model distributes load linearly from the most loaded thread to the least, reflecting the qualitative trend observed experimentally. It is a conservative estimate.

**Power-law distribution:**

$$\phi_i = \frac{(n - i + 1)^{\beta}}{\sum_{j=1}^{n} j^{\beta}}$$

where $\beta$ is typically 1.5--2.0. This produces a more concentrated load distribution than the linear model and better matches experimental and FEA results for standard ISO metric threads.

**Exponential distribution (Sopwith, 1948):**

$$\phi_i = \frac{e^{-\lambda(i-1)}}{\sum_{j=1}^{n} e^{-\lambda(j-1)}}$$

where $\lambda = 0.3$--$0.5$ is the decay parameter. This model, based on the classical work of Sopwith (1948), is derived from the differential equation governing load transfer in a threaded joint and provides a physically motivated exponential decay.

**Yamamoto distribution (1980):**

$$\phi_i = \frac{\sinh\!\left[\gamma(n - i + 0.5)\right]}{\sum_{j=1}^{n} \sinh\!\left[\gamma(n - j + 0.5)\right]}$$

where $\gamma$ is a geometry-dependent parameter. Yamamoto's model accounts for the elastic deformation of both bolt and nut threads and produces the most accurate load distribution for standard thread forms.

### 27.3 Per-Thread Slip Detection

For each thread $i$, the slip condition is evaluated independently:

$$|F_{\mathrm{trans},i}| > \mu_i \cdot F_i$$

where $F_{\mathrm{trans},i} = \phi_i \cdot F_{\mathrm{trans}}$ is the transverse force on thread $i$ and $F_i = \phi_i \cdot F_p$ is the axial load on thread $i$. The loosening contribution of each thread is computed only when that thread is in the slip state.

### 27.4 Non-Uniform Wear Across Threads

Wear accumulation for each thread follows the Archard relation (see Part VI for full treatment):

$$h_i(N) = \frac{K \cdot F_i \cdot s_i}{H \cdot A_i}$$

where $s_i$ is the cumulative sliding distance for thread $i$ and $A_i$ is the contact area. Since $F_i$ is largest for the first thread, wear is concentrated there, progressively reducing the effective contact area and potentially leading to accelerated load redistribution.

**References:**
- Sopwith, D.G. (1948). "The Distribution of Load in Screw Threads." *Proceedings of the Institution of Mechanical Engineers*, Vol. 159, pp. 373--383.
- Yamamoto, A. (1980). *The Theory and Computation of Threads Connection*. Youkendo, Tokyo.
- Zhao, L., Yang, G., and Li, P. (2020). "Research on Thread Load Distribution." *Advances in Mechanical Engineering*, Vol. 12, No. 3.

---

## 28. Coupled Friction-Wear-Loosening System

### 28.1 The Positive Feedback Loop

The most advanced model in the BAS software is the **Coupled Friction-Wear-Loosening Analyzer**, which captures the fully coupled interaction between three evolving phenomena: friction degradation, wear accumulation, and preload loss. These three mechanisms form a positive feedback loop -- a self-reinforcing cycle that can lead to rapid joint failure once initiated:

```
          +--------------+
          |   FRICTION   |
          |   mu(N,v)    |
          +------+-------+
                 |
    Friction     |     Wear increases
    decreases    |     friction energy
                 v
          +--------------+
          |    PRELOAD   |<-------- Lower preload reduces
          |    F_p(N)    |          friction capacity
          +------+-------+
                 |
    Lower        |     Preload loss
    preload      |     from compliance
                 v
          +--------------+
          |     WEAR     |
          |    h(N,F)    |
          +------+-------+
                 |
    Wear removes |     More slip produces
    material     |     more wear
                 |
                 v
         [BACK TO FRICTION]

  THE POSITIVE FEEDBACK LOOP:
  ===========================
  1. Friction decreases over cycles (running-in, degradation)
  2. Lower friction --> Less resistance to transverse slip
  3. More slip --> More wear at thread and bearing surfaces
  4. Wear removes material --> Increases effective compliance
  5. Higher compliance --> Lower preload for same bolt elongation
  6. Lower preload --> Reduced friction capacity (mu * F_p)
  7. Easier slip --> More wear --> Faster loosening
  8. REPEAT (accelerating cycle)
```

This positive feedback is why bolt loosening can appear sudden: the system may operate stably for thousands of cycles while the feedback loop slowly erodes the safety margins, and then transition rapidly to complete preload loss once a critical threshold is crossed.

### 28.2 Three-Phase Friction Evolution Model

The friction coefficient at thread and bearing surfaces evolves over the loading history according to a three-phase model inspired by Hintikka et al. (2020):

$$\mu(N) = \mu_0 + \underbrace{(\mu_{\mathrm{peak}} - \mu_0) \cdot \left(1 - e^{-N/N_1}\right) \cdot e^{-N/N_2}}_{\text{Phase 1: Running-in peak}} + \underbrace{(\mu_{\mathrm{ss}} - \mu_0) \cdot \left(1 - e^{-N/N_3}\right)}_{\text{Phase 2: Steady-state approach}}$$

This composite expression produces the characteristic three-phase behavior:

- **Phase 1 -- Running-in** ($N < N_1 \approx 50$ cycles): Friction rises from $\mu_0$ toward $\mu_{\mathrm{peak}}$ as asperities interlock and oxide layers form.
- **Phase 2 -- Transition** ($N_1 < N < N_2 \approx 200$ cycles): The running-in peak subsides as worn debris is expelled and surfaces conform.
- **Phase 3 -- Steady-state** ($N > N_3 \approx 2000$ cycles): Friction approaches $\mu_{\mathrm{ss}}$, the long-term steady-state value.

Additional degradation from wear and temperature is subtracted:

$$\mu_{\mathrm{eff}}(N) = \max\!\left(\mu(N) - \alpha_w \cdot h(N) - \alpha_T \cdot \Delta T, \; \mu_{\mathrm{min}}\right)$$

where $\alpha_w$ is the wear degradation rate (friction loss per micrometer of wear depth), $\alpha_T$ is the temperature degradation coefficient, and $\mu_{\mathrm{min}} = 0.03$ is the absolute minimum friction (corresponding to boundary lubrication with debris).

### 28.3 Multi-Mechanism Wear Model

The BAS wear model combines two complementary approaches:

**Generalized Archard wear** (Goryacheva, 1998; Argatov and Chai, 2022):

$$\frac{dh}{ds} = K \cdot \left(\frac{p}{H}\right)^{\alpha_p} \cdot v^{\beta_v}$$

where:
- $K$ is the wear coefficient (phase-dependent, see below),
- $p = F/A$ is the contact pressure [Pa],
- $H$ is the surface hardness [Pa],
- $\alpha_p = 1.2$ is the nonlinear pressure exponent (slightly accelerating),
- $\beta_v = 0.8$ is the nonlinear velocity exponent (sub-linear velocity dependence),
- $s$ is the sliding distance [m].

The classical Archard equation corresponds to $\alpha_p = \beta_v = 1$. The generalized exponents capture the empirically observed nonlinear dependence on contact conditions.

**Fouvry energy-based wear** (Fouvry et al., 2003):

$$V = \alpha_V \cdot \max\!\left(0, \; E_d - E_{\mathrm{th}}\right)$$

where:
- $V$ is the wear volume [m$^3$],
- $\alpha_V \approx 5 \times 10^{-11}$ m$^3$/J is the energy wear coefficient,
- $E_d = \mu \cdot F_n \cdot s$ is the dissipated frictional energy [J],
- $E_{\mathrm{th}}$ is the energy threshold for wear onset [J].

The energy threshold accounts for the observation that very low-amplitude fretting may not produce measurable wear.

**Phase-dependent wear coefficient.** The wear coefficient $K$ evolves through four phases:

| Phase | Condition | $K$ Value | Physical Mechanism |
|-------|-----------|-----------|-------------------|
| Running-in | $N < 100$ cycles | $5 \times 10^{-6}$ | Asperity removal, rapid surface adaptation |
| Steady-state | $h < 50\;\mu$m | $10^{-6}$ | Stable surface, consistent material removal |
| Severe | $50\;\mu$m $< h < 100\;\mu$m | $10^{-5}$ | Surface damage, third-body effects |
| Catastrophic | $h > 100\;\mu$m | $5 \times 10^{-5}$ | Near-failure, surface disintegration |

The combined wear increment per cycle is computed as a synergistic combination (not simply additive):

$$\Delta h_{\mathrm{total}} = \sqrt{(\Delta h_{\mathrm{Archard}})^2 + (\Delta h_{\mathrm{energy}})^2} + 0.2 \cdot \min(\Delta h_{\mathrm{Archard}}, \Delta h_{\mathrm{energy}})$$

The square-root combination reflects the fact that the two mechanisms are partially correlated (both depend on contact pressure and sliding), while the additive term captures their synergistic interaction.

### 28.4 Preload Loss from Wear: Nonlinear Compliance Model

Wear-induced preload loss is not simply linear in wear depth. As material is removed from the contact interfaces, the effective compliance of the joint increases, and this increased compliance amplifies further preload loss:

$$\Delta F_{\mathrm{wear}} = k_{\mathrm{sys}} \cdot h \cdot \left(1 + \gamma \cdot h^* + \frac{1}{2}(\gamma \cdot h^*)^2\right)$$

where:
- $k_{\mathrm{sys}} = k_b \cdot k_m / (k_b + k_m)$ is the system stiffness [N/m],
- $h$ is the total wear depth [m],
- $h^* = h \times 10^6$ is the wear depth in micrometers (for scaling),
- $\gamma = 0.05$ is the compliance growth rate.

The quadratic term in $\gamma h^*$ captures the accelerating nature of compliance growth: small amounts of wear cause proportionally small preload loss, but as wear accumulates, the compliance amplification grows quadratically, leading to rapid preload decay -- the essence of the positive feedback loop.

### 28.5 Phase Classification

The BAS analyzer classifies the current loosening state into five phases:

| Phase | Classification Criteria | Physical State |
|-------|------------------------|----------------|
| **STABLE** | Preload > 98% and $N < 10$ and margin > 1.3 | No significant loosening; initial cycles |
| **NON_ROTATIONAL** | $N \leq 1.5 \times N_1$ and preload > $0.9 \times F_{\mathrm{Stage\,I}}$ | Jiang Stage I: embedding, plastic deformation, no nut rotation |
| **TRANSITION** | Margin < 1.3 or preload < 98% | Between Stage I and II; friction margin eroding |
| **ROTATIONAL** | Margin $\leq$ 1.0 or preload < 70% | Jiang Stage II: active Junker mechanism, measurable nut rotation |
| **RUNAWAY** | Preload < 50% or rate > 0.003 deg/cycle | Critical: accelerated loosening, near-zero resisting torque |

### 28.6 Risk Classification

The risk level is derived from the torque margin:

| Risk Level | Torque Margin Range | Engineering Interpretation |
|------------|-------------------|---------------------------|
| **NEGLIGIBLE** | Margin > 2.0 | Very large safety margin; loosening highly unlikely |
| **LOW** | 1.5 < Margin $\leq$ 2.0 | Adequate safety margin for most applications |
| **MODERATE** | 1.1 < Margin $\leq$ 1.5 | Reduced margin; monitoring recommended |
| **HIGH** | 1.0 < Margin $\leq$ 1.1 | Near-critical; loosening may initiate under service conditions |
| **CRITICAL** | Margin $\leq$ 1.0 | Active loosening; immediate corrective action required |

**References:**
- Hintikka, J., Lehtovaara, A., and Mantyla, A. (2020). "Fretting-induced friction and wear in large flat-on-flat contact." *Tribology International*, Vol. 143, Art. 106073.
- Goryacheva, I.G. (1998). *Contact Mechanics in Tribology*. Kluwer Academic Publishers.
- Argatov, I.I. and Chai, Y.S. (2022). "Wear Contact Problem with Friction: Steady-State Regime and Wearing-in Period." *International Journal of Solids and Structures*, Vol. 238, Art. 111390.
- Fouvry, S., Liskiewicz, T., Kapsa, P., Daloz, S., and Bastenaire, F. (2003). "An Energy Description of Wear Mechanisms and Its Applications to Oscillating Sliding Contacts." *Wear*, Vol. 255, pp. 287--298.
- McColl, I.R., Ding, J., and Leen, S.B. (2004). "Finite Element Simulation and Experimental Validation of Fretting Wear." *Wear*, Vol. 256, pp. 1114--1127.
- Pai, N.G. and Hess, D.P. (2002). "Experimental Study of Loosening of Threaded Fasteners due to Dynamic Shear Loads." *Journal of Sound and Vibration*, Vol. 253, No. 3, pp. 585--602.

---

## 29. Preload Loss from Rotation

### 29.1 Kinematic Relation

The fundamental kinematic link between nut rotation and axial displacement in a helical thread is:

$$\Delta x_{\mathrm{axial}} = \frac{p}{2\pi} \cdot \Delta\theta$$

where $\Delta x_{\mathrm{axial}}$ is the change in bolt elongation (or grip length reduction) and $\Delta\theta$ is the nut rotation in radians. This simple geometric relation is the key that converts rotational loosening (measured in degrees or radians) to preload loss (measured in Newtons).

### 29.2 Preload Loss from Rotation

Combining the kinematic relation with the bolt stiffness:

$$\Delta F_{\mathrm{rot}} = k_{\mathrm{bolt}} \cdot \frac{p}{2\pi} \cdot \theta_{\mathrm{loosening}}$$

where $\theta_{\mathrm{loosening}}$ is the cumulative loosening angle [rad] and $k_{\mathrm{bolt}}$ is the bolt axial stiffness [N/m]. This expression shows that preload loss scales linearly with both the bolt stiffness and the thread pitch. A stiffer bolt loses more preload per degree of rotation, and a coarser thread produces more axial displacement per radian of rotation.

### 29.3 Rotation Per Cycle Calculation

The BAS coupled loosening analyzer computes the nut rotation per cycle using an empirically calibrated model:

$$\Delta\theta_{\mathrm{cycle}} = C \cdot \frac{\delta_{\mathrm{slip}}}{d_2} \cdot (1 + r_{\mathrm{excess}}) \cdot \frac{p}{d_2}$$

where:
- $C = 0.3$ is an empirical loosening coefficient calibrated to match Junker test data,
- $\delta_{\mathrm{slip}}$ is the transverse slip amplitude per cycle [m],
- $d_2$ is the pitch diameter [m],
- $r_{\mathrm{excess}}$ is the excess force ratio (how much the transverse force exceeds friction capacity),
- $p/d_2$ is the pitch ratio (thread coarseness parameter).

The slip amplitude is estimated from:

$$\delta_{\mathrm{slip}} = \frac{F_{\mathrm{excess}}}{k_{\mathrm{trans}}}$$

where $F_{\mathrm{excess}} = \max(0, |F_{\mathrm{trans}}| - \mu \cdot F_p)$ is the excess transverse force beyond the friction capacity, and $k_{\mathrm{trans}} \approx 0.3 \cdot k_{\mathrm{sys}}$ is the transverse stiffness (approximately 30% of the axial system stiffness for typical joints).

The excess ratio is:

$$r_{\mathrm{excess}} = \frac{F_{\mathrm{excess}}}{\mu \cdot F_p}$$

### 29.4 Diminishing Effect at Low Preload

As preload decreases, the driving force for further loosening also decreases (since $T_{\mathrm{pitch}} = F_p \cdot p/(2\pi)$ depends on $F_p$). The BAS model captures this through a preload diminishing factor:

$$\Delta\theta_{\mathrm{eff}} = \Delta\theta_{\mathrm{cycle}} \cdot \frac{F_p(N)}{F_{p,0}}$$

This ensures that the loosening rate decreases as preload is lost, consistent with experimental observations that loosening curves are concave rather than linear.

### 29.5 Maximum Physical Rotation Limit

The rotation per cycle is capped at a physical maximum of approximately 0.1 rad/cycle (~6 degrees/cycle), which represents an extreme loosening condition. In practice, typical loosening rates are in the range of 0.001--0.1 degrees per cycle.

**References:**
- Junker, G.H. (1969). "New Criteria for Self-Loosening of Fasteners Under Vibration." SAE Technical Paper 690055.
- Jiang, Y. et al. (2003). "A Study of Early Stage Self-Loosening of Bolted Joints." *ASME Journal of Mechanical Design*, Vol. 125, No. 3, pp. 518--526.

---

## 30. Design Against Self-Loosening

### 30.1 VDI 2230 Safety Factors

The VDI 2230 guideline (2015) provides a systematic framework for bolted joint design that includes specific provisions for preventing self-loosening. The key safety factor is:

$$n_s = \frac{T_{\mathrm{resistance}}}{T_{\mathrm{pitch}}} = \frac{T_{\mathrm{thread}} + T_{\mathrm{bearing}}}{T_{\mathrm{pitch}}}$$

VDI 2230 recommends $n_s > 1.0$ as a minimum and $n_s > 1.5$ for joints subject to transverse vibration. The BAS software computes and tracks this safety factor throughout the analysis.

### 30.2 Critical Transverse Displacement Threshold

A central concept in loosening prevention is the critical displacement threshold $\delta_{\mathrm{crit}}$ below which the Junker mechanism cannot activate. This threshold corresponds to the transverse displacement at which the transverse force first equals the bearing friction capacity:

$$\delta_{\mathrm{crit}} = \frac{\mu_b \cdot F_p}{k_{\mathrm{trans}}}$$

For a typical M16 joint with $\mu_b = 0.12$, $F_p = 50$ kN, and $k_{\mathrm{trans}} = 10^8$ N/m:

$$\delta_{\mathrm{crit}} = \frac{0.12 \times 50{,}000}{10^8} = 0.06 \;\text{mm}$$

Joints designed to keep the transverse displacement below $\delta_{\mathrm{crit}}$ are inherently protected against Junker loosening, regardless of other parameters. This is the principle behind design strategies that increase joint transverse stiffness (e.g., dowel pins, close-fit bolts, interference-fit bushings).

### 30.3 Displacement-Life (D-N) Curves

Analogous to S-N curves for fatigue, **D-N curves** relate the transverse displacement amplitude to the number of cycles to loosening. The BAS implementation uses a bilinear model in log-log coordinates:

**High-cycle region** ($\delta \leq \delta_{\mathrm{transition}}$):

$$\log N = C_1 - m_1 \cdot \log \delta$$

**Low-cycle region** ($\delta > \delta_{\mathrm{transition}}$):

$$\log N = C_2 - m_2 \cdot \log \delta$$

where $C_1, C_2, m_1, m_2$ are material- and geometry-dependent parameters, and $\delta_{\mathrm{transition}} \approx 0.5$ mm is the bilinear transition point.

Below the endurance displacement $\delta_{\mathrm{endurance}} \approx 0.1$ mm, no loosening occurs regardless of cycle count ($N \to \infty$).

### 30.4 Miner's Rule for Variable Amplitude Loading

For joints subjected to variable amplitude transverse vibration (as is common in service), the BAS software implements Miner's linear damage accumulation rule:

$$D = \sum_{i=1}^{k} \frac{n_i}{N_i}$$

where $n_i$ is the number of cycles at displacement amplitude $\delta_i$ and $N_i$ is the loosening life at that amplitude (from the D-N curve). Loosening is predicted when $D \geq 1.0$.

The validated range for Miner's damage at loosening is $D = 0.8$--$1.2$:
- High-low loading sequences tend to give $D < 1.0$ (conservative prediction).
- Low-high sequences tend to give $D > 1.0$ (non-conservative prediction).

### 30.5 Locking Devices Effectiveness

While the BAS software focuses on the fundamental mechanics of loosening rather than specific locking devices, the analysis framework provides the quantitative basis for evaluating device effectiveness. Common approaches and their mechanisms include:

- **Prevailing torque nuts (nylon insert, deformed thread):** Increase $T_{\mathrm{thread}}$ by adding a supplementary frictional or interference resistance. Effective for moderate vibration environments.
- **Free-spinning locking devices (Nord-Lock, serrated flanges):** Modify the bearing surface geometry to create a geometric locking effect that resists rotation even under reduced friction conditions.
- **Adhesive thread-locking compounds:** Effectively increase $\mu_t$ to very high values (0.3--0.6), providing both chemical bonding and gap-filling.
- **Double nut configurations:** The counter-nut (lock nut) creates a preloaded thread contact that opposes any rotation of the primary nut. In the BAS MSD model, each nut in a double-nut configuration requires its own ThreadContact element.
- **High preload design:** The most fundamental "locking device" -- increasing $F_p$ directly increases the friction capacity $\mu \cdot F_p$ and pushes the loosening threshold to higher transverse forces.

### 30.6 Comprehensive Preload Loss Tracking

The BAS software tracks all preload loss mechanisms simultaneously through the PreloadTracker system:

$$\Delta F_{\mathrm{total}} = \Delta F_{\mathrm{rot}} + \Delta F_{\mathrm{embed}} + \Delta F_{\mathrm{wear}} + \Delta F_{\mathrm{creep}} + \Delta F_{\mathrm{relax}} + \Delta F_{\mathrm{thermal}} + \Delta F_{\mathrm{elastic}}$$

where each mechanism has its own evolution law:

| Mechanism | Equation | Typical Magnitude |
|-----------|----------|-------------------|
| Rotational (Junker) | $\Delta F_{\mathrm{rot}} = k_b \cdot (p/2\pi) \cdot \theta$ | 10--80% (dominant under transverse vibration) |
| Embedding (VDI 2230) | $\Delta F_{\mathrm{embed}} = k_{\mathrm{sys}} \cdot f_z \cdot L_K \cdot (1 - e^{-N/N_c})$ | 5--10% (first 100 cycles) |
| Wear | $\Delta F_{\mathrm{wear}} = k_{\mathrm{sys}} \cdot h_{\mathrm{wear}} \cdot (1 + \gamma h)$ | 2--15% (progressive) |
| Creep | $\Delta F_{\mathrm{creep}} = k_{\mathrm{sys}} \cdot \delta_0 \cdot C_r \cdot \ln(1 + t/t_0)$ | 5--20% (high temperature) |
| Stress relaxation | $\Delta F_{\mathrm{relax}} = F_{p,0} \cdot (1 - e^{-t/\tau})$ | 5--15% (high temperature) |
| Thermal | $\Delta F_{\mathrm{thermal}} = k_{\mathrm{sys}} \cdot \Delta\alpha \cdot \Delta T \cdot L$ | Variable (can be positive or negative) |
| Elastic interaction | $\Delta F_{\mathrm{elastic}} = \Phi \cdot F_{\mathrm{ext}}$ | Proportional to external load |

**References:**
- VDI 2230 Part 1 (2015). "Systematic Calculation of Highly Stressed Bolted Joints."
- DIN 65151 (2002). "Aerospace Series -- Dynamic Testing of the Locking Characteristics of Fasteners Under Transverse Loading Conditions (Vibration Test)."
- Bickford, J.H. (2008). *Introduction to the Design and Behavior of Bolted Joints*, 4th ed. CRC Press.
- Lu, Y., Ding, J., Yang, B., and Liu, J. (2024). "Preload Loss Prediction Using Power-Law Models." *Sensors*, Vol. 24, Art. 1234.

---

## References

The following is a consolidated list of all references cited in this document, arranged alphabetically by first author.

1. Argatov, I.I. and Chai, Y.S. (2022). "Wear Contact Problem with Friction: Steady-State Regime and Wearing-in Period." *International Journal of Solids and Structures*, Vol. 238, Art. 111390.

2. Bickford, J.H. (2008). *Introduction to the Design and Behavior of Bolted Joints*, 4th ed. CRC Press.

3. DIN 65151 (2002). "Aerospace Series -- Dynamic Testing of the Locking Characteristics of Fasteners Under Transverse Loading Conditions (Vibration Test)."

4. Fouvry, S., Liskiewicz, T., Kapsa, P., Daloz, S., and Bastenaire, F. (2003). "An Energy Description of Wear Mechanisms and Its Applications to Oscillating Sliding Contacts." *Wear*, Vol. 255, pp. 287--298.

5. Gong, H., Liu, J., and Ding, X. (2019). "Study on the Critical Loosening Condition Toward a New Design Guideline for Bolted Joints." *Proceedings of the Institution of Mechanical Engineers, Part C: Journal of Mechanical Engineering Science*, Vol. 233, No. 9, pp. 3302--3316. DOI: 10.1177/0954406218802928.

6. Goryacheva, I.G. (1998). *Contact Mechanics in Tribology*. Kluwer Academic Publishers.

7. Hintikka, J., Lehtovaara, A., and Mantyla, A. (2020). "Fretting-induced friction and wear in large flat-on-flat contact." *Tribology International*, Vol. 143, Art. 106073.

8. Housari, B.A. and Nassar, S.A. (2007). "Effect of Thread and Bearing Friction Coefficients on the Vibration-Induced Loosening of Threaded Fasteners." *ASME Journal of Vibration and Acoustics*, Vol. 129, No. 4, pp. 484--494. DOI: 10.1115/1.2748473.

9. Jiang, Y., Zhang, M., and Lee, C.H. (2003). "A Study of Early Stage Self-Loosening of Bolted Joints." *ASME Journal of Mechanical Design*, Vol. 125, No. 3, pp. 518--526. DOI: 10.1115/1.1586936.

10. Jiang, Y., Zhang, M., Park, T.W., and Lee, C.H. (2004). "An Experimental Study of Self-Loosening of Bolted Joints." *ASME Journal of Mechanical Design*, Vol. 126, No. 5, pp. 925--931. DOI: 10.1115/1.1767814.

11. Junker, G.H. (1969). "New Criteria for Self-Loosening of Fasteners Under Vibration." *SAE Transactions*, Vol. 78, pp. 314--335. SAE Paper 690055. DOI: [10.4271/690055](https://doi.org/10.4271/690055).

12. Lu, X., Zhu, M., Li, C., Li, S., Wang, S., and Li, Z. (2024). "Prediction of Pre-Loading Relaxation of Bolt Structure of Complex Equipment under Tangential Cyclic Load." *Sensors*, Vol. 24, No. 11, Art. 3306. DOI: [10.3390/s24113306](https://doi.org/10.3390/s24113306).

13. McColl, I.R., Ding, J., and Leen, S.B. (2004). "Finite Element Simulation and Experimental Validation of Fretting Wear." *Wear*, Vol. 256, pp. 1114--1127.

14. Nassar, S.A. and Housari, B.A. (2006). "Effect of Thread Pitch and Initial Tension on the Self-Loosening of Threaded Fasteners." *ASME Journal of Pressure Vessel Technology*, Vol. 128, No. 4, pp. 590--598. DOI: [10.1115/1.2349572](https://doi.org/10.1115/1.2349572).

15. Pai, N.G. and Hess, D.P. (2002a). "Three-Dimensional Finite Element Analysis of Threaded Fastener Loosening due to Dynamic Shear Load." *Engineering Failure Analysis*, Vol. 9, No. 4, pp. 383--402. DOI: 10.1016/S1350-6307(01)00024-3.

16. Pai, N.G. and Hess, D.P. (2002b). "Experimental Study of Loosening of Threaded Fasteners due to Dynamic Shear Loads." *Journal of Sound and Vibration*, Vol. 253, No. 3, pp. 585--602. DOI: 10.1006/jsvi.2001.4006.

17. Sopwith, D.G. (1948). "The Distribution of Load in Screw Threads." *Proceedings of the Institution of Mechanical Engineers*, Vol. 159, pp. 373--383.

18. VDI 2230 Part 1 (2015). "Systematic Calculation of Highly Stressed Bolted Joints -- Joints with One Cylindrical Bolt." Verein Deutscher Ingenieure.

19. Yamamoto, A. (1980). *The Theory and Computation of Threads Connection*. Youkendo, Tokyo.

20. Yang, G., Xie, J., and Xie, Y. (2021). "Study on Mechanism of Anti-Loosening of a New Type of Nut Based on Fem." *Materials*, Vol. 14, No. 15, Art. 4079.

21. Yang, X. and Nassar, S.A. (2011). "Analytical and Experimental Investigation of Self-Loosening of Preloaded Cap Screw Fasteners." *ASME Journal of Vibration and Acoustics*, Vol. 133, No. 3, Art. 031007. DOI: 10.1115/1.4003197.

22. Zhao, L., Yang, G., and Li, P. (2020). "Research on Thread Load Distribution." *Advances in Mechanical Engineering*, Vol. 12, No. 3.

---

**END OF PART V**

*Part VI covers Wear Models in detail.*
*Part VII covers Friction Models in detail.*
*Part XI covers the Coupled Friction-Wear-Loosening Analysis Framework.*
*Part XII covers Force Excitation Functions and Rayleigh Damping.*
