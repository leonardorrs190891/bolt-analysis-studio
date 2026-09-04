# MSD Framework -- PART XII: FORCE EXCITATION FUNCTIONS, DAMPING MODELS, AND NONLINEAR SOLVERS

**Complete Technical Reference for Bolt Analysis Studio**

**Authors:** L. Ribeiro, D. Carvalho, S.C. Naves, T. Santos, V. Marques, G. Arruda
**Institution:** internal reference laboratory
**Project:** Petrobras R&D -- Bolted Flange Joint Integrity

---

**Abstract.** This document covers three topics that are essential for the time-domain simulation of bolted joint dynamics but are not fully addressed in Part VIII (Numerical Solvers): (1) the force excitation function library, which defines how external loading is applied to the MSD system as a function of time; (2) the Rayleigh proportional damping model, which provides a physically motivated damping matrix from target damping ratios; and (3) the nonlinear Newton-Raphson solver with multiple convergence criteria and line search, which is required when contact nonlinearities, gasket behavior, or large-amplitude loosening make the system response nonlinear. Each topic is presented with governing equations, implementation details, and guidance for parameter selection in the context of bolted joint analysis.

---

## Table of Contents

- [48. Force Excitation Functions](#48-force-excitation-functions)
  - [48.1 Harmonic Force](#481-harmonic-force)
  - [48.2 Step Force with Smooth Ramp](#482-step-force-with-smooth-ramp)
  - [48.3 Pulse Force](#483-pulse-force)
  - [48.4 Band-Limited Random Force](#484-band-limited-random-force)
  - [48.5 Superposition of Force Types](#485-superposition-of-force-types)
  - [48.6 Selection Guide for Bolted Joint Applications](#486-selection-guide-for-bolted-joint-applications)
- [49. Rayleigh Proportional Damping](#49-rayleigh-proportional-damping)
  - [49.1 Mathematical Formulation](#491-mathematical-formulation)
  - [49.2 Calibration from Target Damping Ratios](#492-calibration-from-target-damping-ratios)
  - [49.3 Frequency-Dependent Damping Behavior](#493-frequency-dependent-damping-behavior)
  - [49.4 Practical Guidelines for Bolted Joints](#494-practical-guidelines-for-bolted-joints)
- [50. Nonlinear Newton-Raphson Solver](#50-nonlinear-newton-raphson-solver)
  - [50.1 Nonlinear Sources in Bolted Joints](#501-nonlinear-sources-in-bolted-joints)
  - [50.2 Newton-Raphson Iteration within Newmark](#502-newton-raphson-iteration-within-newmark)
  - [50.3 Convergence Criteria](#503-convergence-criteria)
  - [50.4 Line Search](#504-line-search)
  - [50.5 Practical Convergence Issues](#505-practical-convergence-issues)
- [References](#references)

---

## 48. Force Excitation Functions

### 48.1 Harmonic Force

The simplest and most common excitation for loosening analysis is the harmonic (sinusoidal) force:

$$\mathbf{F}(t) = \mathbf{A} \sin(\omega t + \varphi)$$

where:
- $\mathbf{A}$ is the amplitude vector (one component per DOF) [N]
- $\omega = 2\pi f$ is the circular frequency [rad/s]
- $f$ is the excitation frequency [Hz]
- $\varphi$ is the phase angle [rad]

**Physical context:** In the standard Junker transverse vibration test (DIN 65151, ISO 16130), the loading is a prescribed sinusoidal transverse displacement at a fixed frequency (typically 12.5 Hz for DIN 65151). For force-controlled excitation, the harmonic force function directly represents this loading. For displacement-controlled tests, the equivalent force is $F_{trans}(t) = k_{trans} \cdot \delta_{trans} \sin(\omega t)$, where $k_{trans}$ is the transverse stiffness of the joint.

**Typical parameters for bolted joint testing:**

| Application | Frequency $f$ | Amplitude | Reference |
|------------|--------------|-----------|-----------|
| DIN 65151 Junker test | 12.5 Hz | 0.1--1.0 mm displacement | DIN 65151 (2002) |
| NAS 3350 vibration test | 30 Hz | 1--20 g acceleration | NAS 3350 (1991) |
| Subsea operational vibration | 0.1--10 Hz | 1--50 kN axial | API 17D (2011) |
| Machinery-induced vibration | 10--100 Hz | 0.5--5 kN transverse | -- |
| Thermal cycling (equivalent) | 0.001--0.01 Hz | 10--500 kN axial | ASME PCC-1 (2019) |

### 48.2 Step Force with Smooth Ramp

The step force represents a sudden load application, with an optional smooth ramp to avoid numerical difficulties from discontinuities:

$$\mathbf{F}(t) = \begin{cases} \mathbf{0} & t < t_0 \\ \mathbf{A} \cdot \frac{1}{2}\left(1 - \cos\left(\pi \frac{t - t_0}{t_r}\right)\right) & t_0 \leq t < t_0 + t_r \\ \mathbf{A} & t \geq t_0 + t_r \end{cases}$$

where:
- $t_0$ is the start time [s]
- $t_r$ is the rise time [s] (0 for instantaneous step)
- The half-cosine ramp provides $C^1$ continuity at both transitions

**Physical context:** A step force models:
- **Pressure test:** Sudden application of internal pressure to a flanged connection
- **Preload application:** Initial bolt tightening (though this is usually done quasi-statically)
- **Shock loading:** Impact events on bolted structures
- **External load change:** Shift in operational loading regime

**Recommendation:** Always use a nonzero rise time ($t_r \geq 5 \Delta t$, where $\Delta t$ is the integration time step) to avoid exciting spurious high-frequency content in the numerical solution. For the Newmark-$\beta$ method, a rise time of 10 time steps is a reasonable default.

### 48.3 Pulse Force

The pulse force represents a rectangular load of finite duration:

$$\mathbf{F}(t) = \begin{cases} \mathbf{A} & t_0 \leq t < t_0 + t_d \\ \mathbf{0} & \text{otherwise} \end{cases}$$

where $t_d$ is the pulse duration [s].

**Physical context:** A pulse force models:
- **Hammer impact testing** for modal identification of the bolted joint
- **Pressure surges** in piping systems
- **Seismic events** (simplified representation)
- **Bolt fracture:** Sudden loss of preload in one bolt of a multi-bolt pattern

**Frequency content:** A rectangular pulse of duration $t_d$ has significant frequency content up to $f_{max} \approx 1/t_d$. The time step must satisfy $\Delta t \leq 0.1 \cdot t_d$ to adequately resolve the pulse.

### 48.4 Band-Limited Random Force

For simulating random vibration environments, BAS provides a band-limited random force constructed by superposition of random-phase sinusoids:

$$\mathbf{F}(t) = \sum_{k=1}^{N_c} \mathbf{A}_k \sin(2\pi f_k t + \varphi_k)$$

where:
- $N_c = 50$ is the number of frequency components
- $f_k$ are frequencies drawn uniformly from $[f_{min}, f_{max}]$
- $\varphi_k$ are phases drawn uniformly from $[0, 2\pi)$, independently for each DOF
- $\mathbf{A}_k = \mathbf{A}_{rms} \sqrt{2/N_c}$ are scaled to achieve the desired RMS amplitude

**Spectral characteristics:** This construction produces an approximately flat power spectral density (PSD) within the specified frequency band, with the correct RMS value. The PSD approximation improves with increasing $N_c$.

**Physical context:** Random excitation models:
- **Ocean wave loading** on offshore structures (typical band: 0.05--0.5 Hz)
- **Broadband machinery vibration** (typical band: 10--500 Hz)
- **Wind-induced vibration** on exposed bolted structures (typical band: 0.1--10 Hz)
- **Seismic loading** (typical band: 0.1--25 Hz)

**Important:** The random seed should be specified for reproducibility. Different seeds produce different realizations of the same statistical process, which is useful for Monte Carlo studies of loosening probability.

### 48.5 Superposition of Force Types

Real loading on a bolted joint is often the combination of several force types. The BAS framework supports superposition by summing force functions:

$$\mathbf{F}_{total}(t) = \mathbf{F}_{preload} + \mathbf{F}_{harmonic}(t) + \mathbf{F}_{random}(t) + \mathbf{F}_{thermal}(t)$$

**Example for a subsea flanged connection:**
- Static preload: $F_p = 50$ kN per bolt (applied during assembly)
- Operational pressure: Step function, $F_{axial} = 30$ kN with 2-second ramp
- Wave-induced vibration: Harmonic at 0.2 Hz, $F_{trans} = 5$ kN amplitude
- Pressure fluctuations: Random, 0.5 kN RMS, 0.1--2 Hz band

### 48.6 Selection Guide for Bolted Joint Applications

| Analysis Goal | Recommended Force Type | Typical Parameters |
|--------------|----------------------|-------------------|
| Junker loosening test simulation | Harmonic | 12.5 Hz, 0.65 mm transverse |
| VDI 2230 static assessment | Step | Instantaneous to max working load |
| Modal identification | Pulse | Duration = 0.5/f_max |
| Operational life assessment | Random | Site-specific PSD |
| Thermal cycling | Harmonic (very low $f$) | 0.001 Hz, full $\Delta T$ range |
| Impact assessment | Pulse or step | Duration from shock spectrum |
| Fatigue life evaluation | Harmonic or random | Service load spectrum |

---

## 49. Rayleigh Proportional Damping

### 49.1 Mathematical Formulation

Rayleigh damping (Rayleigh, 1877) expresses the damping matrix as a linear combination of the mass and stiffness matrices:

$$[C] = \alpha [M] + \beta [K]$$

where:
- $\alpha$ is the mass-proportional damping coefficient [1/s]
- $\beta$ is the stiffness-proportional damping coefficient [s]

This formulation has the critical advantage that it preserves the **orthogonality of the modal damping matrix**: if $[\Phi]$ are the undamped mode shapes, then $[\Phi]^T [C] [\Phi]$ is diagonal, with modal damping ratios:

$$\zeta_i = \frac{\alpha}{2\omega_i} + \frac{\beta \omega_i}{2}$$

where $\omega_i$ is the $i$-th natural frequency.

### 49.2 Calibration from Target Damping Ratios

Given a desired damping ratio $\zeta$ at two frequencies $\omega_1$ and $\omega_2$, the coefficients $\alpha$ and $\beta$ are determined by solving:

$$\begin{bmatrix} \frac{1}{2\omega_1} & \frac{\omega_1}{2} \\ \frac{1}{2\omega_2} & \frac{\omega_2}{2} \end{bmatrix} \begin{Bmatrix} \alpha \\ \beta \end{Bmatrix} = \begin{Bmatrix} \zeta \\ \zeta \end{Bmatrix}$$

The solution is:

$$\alpha = \frac{2\zeta \cdot \omega_1 \omega_2}{\omega_1 + \omega_2}, \qquad \beta = \frac{2\zeta}{\omega_1 + \omega_2}$$

This ensures that modes at frequencies $\omega_1$ and $\omega_2$ have exactly the damping ratio $\zeta$. Modes between $\omega_1$ and $\omega_2$ are slightly under-damped (minimum at $\omega = \sqrt{\omega_1 \omega_2}$), while modes outside this range are over-damped.

### 49.3 Frequency-Dependent Damping Behavior

The damping ratio as a function of frequency has a characteristic "bathtub" shape:

```
zeta(omega)
  |
  |  alpha/(2*omega)                     beta*omega/2
  |  (mass-proportional)                 (stiffness-proportional)
  |  ╲                                       ╱
  |   ╲                                     ╱
  |    ╲          target zeta              ╱
  |     ╲       ●───────────────●         ╱
  |      ╲     ╱                 ╲       ╱
  |       ╲   ╱     UNDERDAMPED   ╲     ╱
  |        ╲ ╱      (slightly)     ╲   ╱
  |         ●                       ╲ ╱
  |         omega_min = sqrt(w1*w2)  ●
  |                                  omega_max
  |
  └──────────────────────────────────────────────────► omega
         omega_1                  omega_2
```

**Key property:** The minimum damping ratio occurs at:

$$\omega_{min} = \sqrt{\omega_1 \cdot \omega_2}, \qquad \zeta_{min} = \sqrt{\alpha \beta}$$

For equal damping at $\omega_1$ and $\omega_2$:

$$\zeta_{min} = \zeta \cdot \frac{2\sqrt{\omega_1 \omega_2}}{\omega_1 + \omega_2} \leq \zeta$$

The minimum is close to $\zeta$ when $\omega_1$ and $\omega_2$ are not too far apart (within one order of magnitude).

### 49.4 Practical Guidelines for Bolted Joints

**Selecting $\omega_1$ and $\omega_2$:**

- $\omega_1$ should correspond to the **fundamental natural frequency** of the bolted joint assembly (typically the lowest axial or transverse mode).
- $\omega_2$ should correspond to the **highest frequency of interest**, which is usually the excitation frequency or the highest mode that contributes significantly to the response.

**Selecting $\zeta$:**

| Component | Typical $\zeta$ | Source |
|-----------|----------------|--------|
| Steel-on-steel bolted joint (dry) | 0.01--0.03 | VDI 2230, experimental |
| Bolted joint with gasket | 0.03--0.08 | Gasket viscoelasticity |
| Thread contact interface | 0.02--0.05 | Microslip dissipation |
| Bearing contact (lubricated) | 0.01--0.03 | Viscous shear of lubricant film |
| Overall assembled joint | 0.02--0.05 | Combined |
| Joint with polymeric elements (e.g., Belleville springs) | 0.05--0.15 | Material damping |

**Recommendation for BAS analyses:**

For standard bolted joint loosening analysis:
- $\omega_1 = 2\pi \times 5$ rad/s (5 Hz, below typical excitation)
- $\omega_2 = 2\pi \times 50$ rad/s (50 Hz, above typical excitation)
- $\zeta = 0.02$ (2%, conservative for steel joints)

For joints with gaskets:
- Same frequency range
- $\zeta = 0.05$ (5%, accounting for gasket viscoelasticity)

### 49.5 Limitations of Rayleigh Damping

1. **Only two frequencies are matched exactly.** For systems with widely spaced natural frequencies (e.g., a 14-DOF model spanning 1 Hz to 1000 Hz), modes far from $\omega_1$ and $\omega_2$ may be severely over-damped.

2. **Proportional damping assumption.** Real bolted joint damping is strongly non-proportional: interface friction (a nonlinear, amplitude-dependent mechanism) provides the dominant energy dissipation, not material viscosity. Rayleigh damping is therefore a linearized approximation that works well for small-amplitude oscillation around the preloaded state but may be inaccurate during active loosening.

3. **No physical basis for individual $\alpha$ and $\beta$.** The mass-proportional term ($\alpha [M]$) lacks a clear physical interpretation for bolted joints (it would correspond to external viscous dashpots, which don't exist in most joint assemblies). The stiffness-proportional term ($\beta [K]$) corresponds to material (hysteretic) damping, which is more physically reasonable.

**Alternative for future implementation:** Caughey damping (Caughey & O'Kelly, 1965) allows matching damping ratios at more than two frequencies, at the cost of higher matrix bandwidth. For highly non-proportional damping, a full complex-mode approach or direct time integration with explicit friction forces (as implemented in the coupled loosening analyzer) is more appropriate.

---

## 50. Nonlinear Newton-Raphson Solver

### 50.1 Nonlinear Sources in Bolted Joints

The MSD system becomes nonlinear when any of the following effects are significant:

| Source | Mathematical Expression | When Significant |
|--------|----------------------|------------------|
| **Gasket behavior** | $k_g = k_g(\delta)$, nonlinear force-deflection | Always, for gasketed joints |
| **Friction forces** | $\mathbf{F}_f = f(\mathbf{v}, \mathbf{z}, \mu(N))$ | During slip (loosening) |
| **Contact separation** | $k_c = 0$ if gap opens | Near joint separation |
| **Wear-induced changes** | Geometry evolves with wear | Long-term simulation |
| **Thread stick-slip** | Discontinuous friction transitions | During loosening events |
| **Large rotations** | Geometric nonlinearity in helix coupling | Severe loosening |

When these nonlinearities are present, the standard linear solvers (Newmark-$\beta$, HHT-$\alpha$) cannot be applied directly because the effective stiffness and force depend on the unknown displacement at the new time step. The Newton-Raphson (NR) iteration resolves this by iteratively improving the solution within each time step until the residual force drops below a specified tolerance.

### 50.2 Newton-Raphson Iteration within Newmark

The Newmark-$\beta$ equations at time step $n+1$ with nonlinear internal forces become:

$$[M]\ddot{\mathbf{u}}_{n+1} + \mathbf{f}_{int}(\mathbf{u}_{n+1}, \dot{\mathbf{u}}_{n+1}) = \mathbf{F}_{ext}(t_{n+1})$$

where $\mathbf{f}_{int}$ includes both linear stiffness/damping and nonlinear contributions (friction, contact, gasket).

The **residual** at iteration $k$ is:

$$\mathbf{R}^{(k)} = [M]\ddot{\mathbf{u}}^{(k)} + \mathbf{f}_{int}(\mathbf{u}^{(k)}, \dot{\mathbf{u}}^{(k)}) - \mathbf{F}_{ext}$$

The NR correction is:

$$[K_{eff}^{(k)}] \Delta\mathbf{u}^{(k)} = -\mathbf{R}^{(k)}$$

where the effective tangent stiffness is:

$$[K_{eff}^{(k)}] = \frac{\partial \mathbf{R}}{\partial \mathbf{u}} = \frac{1}{\beta \Delta t^2}[M] + \frac{\gamma}{\beta \Delta t}\frac{\partial \mathbf{f}_{int}}{\partial \dot{\mathbf{u}}} + \frac{\partial \mathbf{f}_{int}}{\partial \mathbf{u}}$$

For the standard linear case, $\frac{\partial \mathbf{f}_{int}}{\partial \mathbf{u}} = [K]$ and $\frac{\partial \mathbf{f}_{int}}{\partial \dot{\mathbf{u}}} = [C]$.

**Update formulas:**

$$\mathbf{u}^{(k+1)} = \mathbf{u}^{(k)} + \Delta\mathbf{u}^{(k)}$$

$$\dot{\mathbf{u}}^{(k+1)} = \dot{\mathbf{u}}^{(k)} + \frac{\gamma}{\beta \Delta t}\Delta\mathbf{u}^{(k)}$$

$$\ddot{\mathbf{u}}^{(k+1)} = \ddot{\mathbf{u}}^{(k)} + \frac{1}{\beta \Delta t^2}\Delta\mathbf{u}^{(k)}$$

### 50.3 Convergence Criteria

The BAS implementation supports four convergence criteria, selectable by the user:

**1. Force criterion (residual norm):**

$$\|\mathbf{R}^{(k)}\| < \varepsilon_F$$

This is the most fundamental criterion: the iteration is converged when the out-of-balance force is small. Default: $\varepsilon_F = 10^{-6}$.

**Physical interpretation:** The force residual represents the equilibrium error -- how far the current state is from satisfying Newton's second law. For a joint with 50 kN preload, a tolerance of $10^{-6}$ means equilibrium is satisfied to within 1 mN.

**2. Displacement criterion (correction norm):**

$$\|\Delta\mathbf{u}^{(k)}\| < \varepsilon_u$$

The iteration is converged when the displacement correction becomes negligible. Default: $\varepsilon_u = 10^{-6}$.

**Physical interpretation:** For displacements on the order of micrometers (typical for a preloaded bolt), a tolerance of $10^{-6}$ means corrections smaller than 1 picometer -- well below the physical resolution of any measurement.

**3. Energy criterion (work of residual):**

$$|\Delta\mathbf{u}^{(k)} \cdot \mathbf{R}^{(k)}| < \varepsilon_E$$

The iteration is converged when the work done by the residual force over the correction displacement is small. Default: $\varepsilon_E = 10^{-9}$.

**Physical interpretation:** This criterion combines force and displacement information and is particularly useful when some DOFs have large forces but small displacements (e.g., stiff contact elements) and others have small forces but large displacements (e.g., soft gasket). It ensures that neither force *nor* displacement errors are individually significant.

**4. Combined criterion:**

$$\|\mathbf{R}^{(k)}\| < \varepsilon_F \quad \text{AND} \quad \|\Delta\mathbf{u}^{(k)}\| < \varepsilon_u \quad \text{AND} \quad |\Delta\mathbf{u}^{(k)} \cdot \mathbf{R}^{(k)}| < \varepsilon_E$$

All three criteria must be satisfied. This is the default and most robust option. It prevents convergence when one criterion is satisfied by coincidence (e.g., small residual with large correction, or vice versa).

### 50.4 Line Search

When the full NR correction $\Delta\mathbf{u}$ overshoots the solution (which can happen with strongly nonlinear contact or friction), a **line search** reduces the step size to ensure monotonic decrease of the residual:

$$\mathbf{u}^{(k+1)} = \mathbf{u}^{(k)} + \eta \cdot \Delta\mathbf{u}^{(k)}$$

where $\eta \in (0, 1]$ is determined by successive halving:

```
ALGORITHM: Line Search
═══════════════════════

INPUT: u(k), Delta_u, R(k)

  eta = 1.0
  FOR i = 1 TO max_iter_ls:
    u_trial = u(k) + eta * Delta_u
    R_trial = compute_residual(u_trial)

    IF ||R_trial|| < ||R(k)||:
      ACCEPT: u(k+1) = u_trial
      RETURN
    ELSE:
      eta = eta * 0.5    // Halve the step
    END IF
  END FOR

  ACCEPT with current eta (best found)
```

**Default parameters:**
- Maximum line search iterations: 10
- Reduction factor: 0.5
- Minimum $\eta$: $0.5^{10} \approx 10^{-3}$

### 50.5 Practical Convergence Issues

**Common convergence difficulties in bolted joint analysis:**

1. **Contact chattering:** When a contact element alternates between open and closed states within a single time step, the NR iteration may oscillate. **Remedy:** Use a smooth contact regularization (e.g., exponential penalty instead of hard contact) or reduce the time step.

2. **Friction stick-slip:** Sudden transitions between sticking and slipping create discontinuities in the force-displacement relationship. **Remedy:** Use a regularized friction model (e.g., LuGre instead of Coulomb) or the velocity regularization $\tanh(v/v_{reg})$ with $v_{reg} \sim 10^{-4}$ m/s.

3. **Gasket nonlinearity:** Highly nonlinear gasket force-deflection curves (e.g., spiral wound gaskets) may cause the NR to diverge if the initial guess is far from the solution. **Remedy:** Use incremental loading (subdivide the load step) or load the gasket in the initial static analysis.

4. **Near-singular stiffness:** When preload drops to near zero, the system stiffness becomes very small and the effective stiffness matrix may become ill-conditioned. **Remedy:** Add a small numerical stiffness regularization to prevent singularity.

**Maximum iterations:** The default limit is 50 iterations per time step. If convergence is not achieved within this limit, the solver reports a warning and proceeds with the best available solution. Persistent non-convergence (more than 5% of time steps failing) indicates that the time step is too large, the nonlinearity is too severe, or the model requires regularization.

---

## References

1. Bathe, K.-J. (1996). *Finite Element Procedures*. Prentice Hall.
2. Caughey, T.K. & O'Kelly, M.E.J. (1965). "Classical normal modes in damped linear dynamic systems." *ASME Journal of Applied Mechanics*, 32(3), 583--588. DOI: 10.1115/1.3627262
3. Chopra, A.K. (2012). *Dynamics of Structures: Theory and Applications to Earthquake Engineering*, 4th ed. Prentice Hall.
4. DIN 65151 (2002). "Dynamic testing of locking characteristics of fasteners under transverse loading." Deutsches Institut fur Normung.
5. Hilber, H.M., Hughes, T.J.R., & Taylor, R.L. (1977). "Improved numerical dissipation for time integration algorithms in structural dynamics." *Earthquake Engineering and Structural Dynamics*, 5(3), 283--292. DOI: 10.1002/eqe.4290050306
6. Hughes, T.J.R. (1987). *The Finite Element Method: Linear Static and Dynamic Finite Element Analysis*. Prentice Hall.
7. ISO 16130 (2015). "Aerospace -- Dynamic testing of bolt loosening under transverse loading." International Organization for Standardization.
8. NAS 3350 (1991). "Fastener test methods -- Vibration." National Aerospace Standard.
9. Newmark, N.M. (1959). "A method of computation for structural dynamics." *ASCE Journal of the Engineering Mechanics Division*, 85(EM3), 67--94.
10. Rayleigh, Lord (J.W.S.) (1877). *The Theory of Sound*, Vol. 1. Macmillan.
11. VDI 2230 Part 1 (2015). "Systematic calculation of highly stressed bolted joints -- Joints with one cylindrical bolt." Verein Deutscher Ingenieure.
12. Wriggers, P. (2006). *Computational Contact Mechanics*, 2nd ed. Springer. DOI: 10.1007/978-3-540-32609-0
