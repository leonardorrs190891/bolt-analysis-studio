# Future Improvements — Bolt Analysis Studio v4.0

**LTAD/UFU — Petrobras R&D**
*Suggested by development team — February 2026*

---

## Scope

This document lists suggested improvements **beyond** the six implementation phases (A–F)
already planned in `LOOSENING_IMPLEMENTATION_PLAN.md`. Items here represent the next
evolution of the software after those phases are complete.

**Legend:** Effort S = < 1 week / M = 1–4 weeks / L = 1–3 months.
Impact: ★ = incremental, ★★ = significant, ★★★ = transformative.

> **Four-document companion set (theory → design → plan → future):**
> - `LOOSENING_MECHANISMS_QUANTITATIVE.md` (LMQ) — mechanism taxonomy, fretting map, five-stage
>   phase model, locking devices (§1–§13)
> - `LOOSENING_LOADING_CONDITIONS.md` (LLC) — loading-type analysis: axial, shear, bending,
>   impact, combined; 14-criterion transition table (§1–§7)
> - `LOAD_FACTORS_DESIGN.md` (LFD) — VDI 2230 load factors R, Φ, n, φ, waveform; GUI widget
>   design; code snippets for six files (§1–§11)
> - `LOOSENING_IMPLEMENTATION_PLAN.md` — phased roadmap (Phases A–F); theory→code mapping;
>   test plan
>
> Cross-references use `[LMQ §X]`, `[LLC §X]`, `[LFD §X]` notation.

---

## 1. Physics and Analysis Depth

### 1.1 Fatigue–Loosening Competition Model
**Effort M | Impact ★★★**

Currently, fatigue and self-loosening are treated independently. In practice they
compete: high preload prevents loosening but increases bolt stress amplitude. The joint
fails by whichever mechanism accumulates damage first.

**Approach:**
- Compute alternating bolt stress: `σ_a = Φ × F_alt / A_s` (using F_alt from Phase A
  R-factor, `[LFD §2.1]`)
- Evaluate bolt fatigue damage per cycle using S-N curves (VDI 2230 §5.6, ISO 3800)
- Compute loosening damage per cycle (Miner's D-N analog from Phase E, `[LMQ §12.3]`)
- Total failure index: `D_total = D_fatigue + D_loosening` → failure when `D_total ≥ 1`
- Show competition diagram: axes = F_preload vs. N_cycles; boundary curves for each
  failure mode; the five-stage phase boundaries from Phase B `[LMQ §12.1]` overlay
  naturally as iso-preload ratio contours

**Prerequisite:** Phase B (five-stage model) for the loosening damage axis; Phase A
(R-factor) for the fatigue stress amplitude calculation.

**Key files:** `coupled_loosening_analyzer.py`, `numerical/preload_loss_models.py`,
new `numerical/fatigue_models.py`

**Reference:** ASTM E647, VDI 2230 §5.6, ISO 3800 (bolt fatigue)

---

### 1.2 Probabilistic / Monte Carlo Analysis
**Effort M | Impact ★★★**

The friction coefficient scatter alone causes ±50% preload uncertainty for torque
tightening (`[LMQ §8.2]`). Torque distribution analysis shows ~51% of tightening torque
is absorbed by bearing-face friction — the component with the highest variance — and
the friction coefficient varies by up to 2:1 between nominal min and max for a given
surface condition. A single-point analysis is insufficient for reliability-critical
applications (pressure vessels, structural connections).

**Approach:**
- Define probability distributions for: µ (lognormal, σ ≈ 0.3 × µ_nominal as implied
  by `[LMQ §8.2]` data), F_preload (normal from tightening method scatter,
  TF = 1.4–2.0 for torque wrench), surface roughness Rz (lognormal per VDI 2230)
- Run N = 500–5 000 Monte Carlo samples through the loosening analyzer
- Output: P(loosening > 20% after 2 000 cycles), confidence intervals on preload decay
  curve, P(entering ROTATIONAL phase before N cycles)
- Sensitivity indices (Sobol): identify which parameter — µ or F_preload — contributes
  most to loosening scatter; literature suggests µ typically dominates for torque-tightened
  joints

**Key files:** new `analysis/monte_carlo.py`, `main_window.py` (new "Reliability" tab)
**GUI:** distribution editors per parameter, PDF/CDF output plots, reliability vs.
preload curve, Sobol bar chart

---

### 1.3 Thread Root Fatigue Crack Propagation
**Effort L | Impact ★★**

Bolt failure under cyclic loading is often by fatigue cracking at the thread root (first
engaged thread concentrates 30–40% of load). BAS currently tracks loosening but not
crack initiation/propagation.

**Approach:**
- Compute local stress at thread root: `σ_max = K_t × σ_nom` where `K_t ≈ 3–6` for threads
- Use Neuber correction for cyclic plasticity: `σ_local × ε_local = σ_nom² × K_t² / E`
- Initiation life from S-N (or ε-N for high plastic strain)
- Crack propagation: Paris law `da/dN = C × ΔK^m`; failure when `a ≥ a_crit`
- Cross-check: does loosening or fracture occur first?
- Note: thread rolling introduces −400 to −600 MPa compressive residual stress at root,
  improving fatigue life 2–4× vs. cut threads (see §1.6)

**Key files:** new `numerical/fatigue_models.py`, `coupled_loosening_analyzer.py`
**Reference:** BS 7910, ASTM E1820, VDI 2230 §5.6

---

### 1.4 Thermal–Structural Coupling (Heat Flow + CTE)
**Effort M | Impact ★★**

Current thermal model (`[LMQ §5]`) assumes uniform ΔT. Real flange joints in
piping/pressure vessels have through-thickness temperature gradients. Furthermore,
thermal cycling causes **ratcheting** — irreversible preload loss each cycle:
first thermal cycle ≈ 41% of initial preload lost, second ≈ 8.5%, converging to
a residual after ~5 cycles (`[LMQ §5.3]`). This is far larger than steady-state
thermal offset and is not captured by the current uniform-ΔT model.

**Approach:**
- Add a 1D axial heat flow model along the bolt/flange stack
- Compute temperature distribution T(z) for each material zone
- Integrate CTE × ΔT(z) × dz for effective thermal elongation per component
- Implement thermal ratcheting model: `F_p(N) = F_p0 × [1 − A × (1 − exp(−N/τ_th))]`
  where A = 0.6–0.8 and τ_th = 2–5 cycles for high Δα cases
- Support cyclic thermal loading (plant startup/shutdown cycles); check combined
  thermal + transverse interaction `[LLC §5]`
- Expose A_th and τ_th as user-configurable parameters

**Key files:** new `numerical/thermal_models.py`, `core/models/element.py` (thermal
properties), `coupled_loosening_analyzer.py` (ratcheting loop)

---

### 1.5 Gasket Nonlinear Pressure-Deflection (ASME VIII Division 1)
**Effort M | Impact ★★**

The current gasket model uses a linear stiffness. Real gaskets have nonlinear loading/
unloading curves, permanent set, and a minimum seating stress requirement (ASME BPVC
VIII Div.1 App. 2 `m` and `y` factors).

**Approach:**
- Implement ASME `m` (maintenance factor) and `y` (seating stress) gasket characterization
- Loading curve: `σ_g(δ) = k_g × δ^n` (power-law, n ≈ 0.3–0.8 for spiral wound)
- Unloading curve: different slope (hysteresis loss = damping energy)
- Creep: `δ_creep(t) = δ_0 × C_g × log10(1 + t)` (`[LMQ §4.3]`); PTFE/flexible
  graphite can lose 15–35% of clamp force in service
- Check: if `σ_g < m × P_internal` → seal loss warning
- Per-bolt gasket load distribution for multi-bolt flanges

**Key files:** `contacts/gasket.py`, `core/databases/` (new gasket materials JSON)
**Reference:** ASME BPVC VIII App. 2, EN 13555

---

### 1.6 Residual Stress from Thread Rolling / Cutting
**Effort M | Impact ★**

Thread rolling introduces beneficial compressive residual stress at the thread root
(~−400 to −600 MPa for M10 grade 10.9), improving fatigue life by 2–4× versus cut
threads. Thread cutting produces near-zero or tensile residual stress.

**Approach:**
- Add `thread_manufacturing: str` field to element: `"rolled"`, `"cut"`, `"ground"`
- Apply mean stress correction in fatigue model: `σ_eff = σ_a / (1 − σ_residual/σ_UTS)` (Goodman)
- Report: fatigue life ratio rolled/cut for same loading conditions

**Key files:** `core/models/element.py`, `numerical/fatigue_models.py`
**Reference:** VDI 2230 §3, ISO 3506

---

### 1.7 Torsional Vibration Loading Mode
**Effort M | Impact ★★**

LLC classifies **torsional (rotational) vibration** as a ★★★ moderate-severity loosening
mechanism (`[LLC §overview]`): cycles to 50% preload loss are 10³–10⁴, comparable to
bending/eccentric loading. Unlike the Junker mechanism, torsional vibration drives nut
rotation **directly** — no transverse displacement is needed. This loading type is common
in rotating machinery, valve actuators, and engine accessories, but is not modeled by BAS.

**Mechanism:** Cyclic torsional excitation oscillates the applied torque at the nut face.
When the oscillation amplitude exceeds the prevailing torque (thread + bearing friction
torque), the nut rotates forward and backward. Net loosening accumulates if the winding
direction is favored by the thread helix.

**Approach:**
- Add `TORSIONAL` to the load type enum alongside `TRANSVERSE`, `AXIAL_TENSION`, etc.
- Excitation: `M_T(t) = M_T_mean + M_T_alt × waveform(t)` applied to nut rotational DOF
- Slip condition: `M_T_peak > T_resist_total = T_thread + T_bearing`
  (the three-torque model from `[LMQ §13.3]`)
- Net nut rotation per cycle: `Δθ_net = Δθ_forward − Δθ_reverse`; accumulates when
  the helix makes forward rotation energetically favorable
- Combine with the five-stage phase model (Phase B) for severity classification
- GUI: add "Torsional Amplitude" and "Torsional Mean" spinboxes to Loading > Global

**Prerequisite:** Phase A (waveform support) and Phase B (phase classification).

**Key files:** `core/models/element.py` (LoadingData), `coupled_loosening_analyzer.py`,
`gui/msd_builder.py`

**Reference:** `[LLC §overview]` severity table; VDI 2230 §5.3 (torsional loading)

---

## 2. Multi-Bolt and System-Level Analysis

### 2.1 Multi-Bolt Flange Load Distribution
**Effort L | Impact ★★★**

Real flanges have 4–64 bolts. Bolt loads are non-uniform due to:
- Gasket seating non-uniformity
- Flange rotation / bending (prying)
- Bolt bending at eccentric loads
- Pass-sequence effects during assembly

**Approach:**
- Model flange as a ring beam; bolts as springs at bolt circle
- Solve for bolt load distribution under operating loads (pressure, weight, thermal)
- Identify the critical bolt (highest + lowest loaded)
- Run loosening analysis for the critical bolt
- Output: bolt load map visualization (polar plot); assembly pass-sequence optimization

**Key files:** new `analysis/multi_bolt_flange.py`, `gui/main_window.py` (new analysis mode)
**Reference:** ASME PCC-1 (2019 App. O), EN 1591-1

---

### 2.2 Pass-Sequence Optimizer for Bolt Assembly
**Effort M | Impact ★★**

Tightening sequence significantly affects final bolt load distribution. ASME PCC-1
recommends cross-pattern tightening in multiple passes. The optimal sequence and number
of passes is problem-dependent.

**Approach:**
- Define bolt positions (circular or rectangular pattern)
- Simulate sequential tightening: each bolt stretch affects neighbours via flange stiffness
- Apply interaction factors between bolts (influence matrix approach)
- Optimize: minimize max/min bolt load ratio after final pass
- Output: step-by-step sequence with target torque at each step

**Key files:** new `analysis/assembly_optimizer.py`

---

### 2.3 Bolt Cluster Loosening Interaction
**Effort M | Impact ★★**

In a multi-bolt cluster, loosening of one bolt redistributes its load to neighbours,
which may then exceed their loosening threshold — cascade failure. This is not captured
by single-bolt analysis.

**Approach:**
- Use the bolt load distribution model (2.1) to get initial loads
- When bolt i loosens, redistribute `ΔF_i` to neighbouring bolts proportional to inverse distance
- Recheck loosening condition for each bolt with updated loads
- Detect cascade: if bolt i loosening triggers bolt j to loosen within 100 cycles

**Key files:** new `analysis/cluster_loosening.py`

---

### 2.4 Combined Loading Interaction Margin Chart
**Effort S | Impact ★★**

LLC §5.2 shows that under combined torsional + transverse loading, loosening initiates
before either individual threshold is reached. The interaction boundary is approximately
elliptical `[LLC §5.2]`:

```
(F_T / F_T_crit)² + (M_T / M_T_crit)² ≤ 1.0
```

For axial + transverse, the interaction is linear (conservative) `[LLC §5.1]`:

```
F_T / (µ × F₀) + F_A / F_sep ≤ 1.0
```

Currently, BAS checks these conditions only internally and reports a pass/fail. A
**graphical interaction diagram** would let engineers visualize margin and adjust loading
parameters interactively.

**Approach:**
- Add an "Interaction Diagram" plot to the Results tab
- Axes: normalized transverse force vs. normalized torsional moment (or axial force)
- Plot the theoretical interaction boundary (ellipse or line)
- Mark the current operating point (filled circle) with margin annotation
- Allow the user to drag the operating point → live margin recalculation
- Show how margin changes as preload decays through the five phases

**Prerequisite:** Phase A (load factors, F_sep calculation) and Phase C (slip criterion).

**Key files:** `gui/main_window.py` (ResultsTab), new plot method in
`visualization/loosening_plots.py`

---

## 3. Experimental Data Integration

### 3.1 Junker Test Data Import and Curve Fitting
**Effort M | Impact ★★★**

The most direct validation path is to import real Junker test data (preload vs. cycles)
and fit the BAS loosening model to it. This produces calibrated µ, wear coefficients,
and stage parameters for specific material/surface combinations.

**Approach:**
- CSV import dialog: columns = cycles, bolt tension [kN], (optional) nut rotation [°]
- Auto-fit: scipy.optimize to match BAS two-stage model to imported data:
  - Stage 1 (double-exponential): fit A₁, N₁, A₂, N₂ (Phase B model, `[LMQ §12.2]`)
  - Stage 2 (linear rotational): fit dθ/dN → back-compute µ
  - Optional: fit D-N power-law exponent b from variable-amplitude data (Phase E,
    `[LMQ §12.4]`), enabling loosening life prediction from fitted parameters
- Overlay: plot imported data with fitted simulation on same axes
- Export: fitted parameter set as `.json` for reuse in other analyses
- Validation: show R² and residual error per phase

**Key files:** `gui/main_window.py` (import dialog), `analysis/curve_fitting.py` (new),
`coupled_loosening_analyzer.py`

---

### 3.2 Ultrasonic Bolt Tension Sensor Integration
**Effort M | Impact ★★★**

Ultrasonic bolt tension sensors (e.g., SmartBolts, Tensor Systems, Dakota Ultrasonics)
measure actual bolt elongation non-destructively. Integrating live sensor data creates
a real-time monitoring capability.

**Approach:**
- Define a data source interface: CSV/file polling OR serial/USB (sensor API)
- Import live or historical bolt tension vs. time data
- Overlay on simulation prediction: "measured" vs. "predicted" preload decay
- Trigger alerts: when measured F_p drops below threshold (customizable)
- Digital twin mode: continuously update simulation parameters to match sensor readings

**Key files:** new `io/sensor_interface.py`, `gui/main_window.py` (monitoring panel)

---

### 3.3 Standardized Validation Case Library Expansion
**Effort M | Impact ★★**

Current validation cases cover basic Junker scenarios. A richer library enables
systematic comparison across bolt sizes, surface conditions, and loading types.

**Suggested additional cases:**
- M6, M8, M12, M20, M36 coarse thread (current: M10, M16)
- Fine thread vs coarse thread comparison at same nominal diameter
- Dry vs lubricated (MoS₂, Dacromet) comparison
- Grade 8.8 vs 10.9 vs 12.9 comparison
- Aluminum clamped members (embedding 3× higher than steel per `[LMQ §2.3]`,
  where M16 embedding is 6–10% vs M6 at 25–38%)
- Square-wave Junker (DIN 65151) vs sinusoidal excitation (Phase A waveform)
- Variable-amplitude validation: Yang et al. (2019) M10 dataset for Miner's rule (Phase E)

**Key files:** `core/validation_cases.py` (add 12+ new cases)

---

### 3.4 Locking Device Selection Wizard
**Effort M | Impact ★★**

Phase F creates the locking device database (`locking_devices.json`) with ISO 2320 and
ISO 16130 data. A **design wizard** would go further: given the operating conditions
(temperature, vibration severity, required retention, reusability), it recommends
the most appropriate locking device and quantifies the expected benefit.

**Approach:**
- Wizard dialog: step 1 = operating conditions (T_max, vibration severity, n_reuses);
  step 2 = select from ranked device list, with expected retention range shown;
  step 3 = confirm and apply to model
- Rank devices by: ISO 16130 compliance probability, temperature margin, cost tier
- Show comparative Junker curves for top 3 candidates (from Phase F database retention data,
  `[LMQ §13.1]`)
- Warning when nyloc nut is selected and T_max > 100°C (nylon degrades above 100–120°C)
- Warning when chemical locking (Loctite) is selected and F_p is below minimum threshold
  (~4.4 kN for M16) required for complete cure

**Prerequisite:** Phase F (locking device database and selector).

**Key files:** new `gui/locking_wizard.py`, `core/databases/locking_devices.json`,
`gui/main_window.py`

**Reference:** `[LMQ §13.1–§13.4]` (retention data, failure conditions)

---

## 4. Solver and Numerical Methods

### 4.1 Contact Nonlinearity — Hertz Contact Model
**Effort M | Impact ★★**

Current contact elements use linear springs (`k_contact = constant`). Real contact
stiffness is nonlinear (Hertz contact theory): `k_c ∝ F_n^(1/3)` for spherical/
cylindrical contacts. This matters most at low preloads (contact stiffness drops steeply).

**Approach:**
- Implement Hertz contact stiffness: `k_c(F_n) = (4/3) E* sqrt(R_eff) × δ^(1/2)`
  where R_eff = effective contact radius, E* = combined modulus
- Use Newton iteration to solve nonlinear contact equilibrium each time step
- Fall back to linear for high preload (where nonlinearity is small, < 2%)
- Expose R_eff (curvature) as a contact element property

**Key files:** `contacts/base.py`, `contacts/bearing.py`, `core/models/model.py`

---

### 4.2 LuGre Friction Model Full Implementation
**Effort M | Impact ★★**

The LuGre friction model is listed in the friction model selector (CLAUDE.md Phase 3.1)
but the physics model in `numerical/friction_models.py` needs completion. LuGre captures:
- Pre-sliding stiffness (bristle elasticity)
- Stiction peak (static > kinetic transition)
- Velocity-dependent Stribeck effect
- State variable θ (bristle average deflection)

**Key equations:**
```
dθ/dt = v − (|v|/g(v)) × θ
F_friction = σ₀ × θ + σ₁ × dθ/dt + σ₂ × v
g(v) = µ_c + (µ_s − µ_c) × exp(−(v/v_s)²)
```

**Note:** This model is most relevant after Phase D (fretting wear µ coupling), since
LuGre's state variable θ naturally represents the average bristle deflection that
degrades under fretting. The Phase D fretting regime classification (`[LMQ §11.1]`)
provides the regime boundaries that determine which friction model is most appropriate.

**Key files:** `numerical/friction_models.py` (LuGre class exists but incomplete),
`contacts/base.py`, `core/models/model.py`

---

### 4.3 Parallel Batch Solver (Multi-Parameter Studies)
**Effort M | Impact ★★**

Currently `BatchAnalysisDialog` uses `ThreadPoolExecutor` but is limited to parameter
sweeps of a single variable. A proper parametric study needs simultaneous variation of
multiple parameters (e.g., F_p × µ grid, or F_p × δ × frequency 3D space).

**Approach:**
- Add parameter sweep mode: define N variables, each with range + steps
- Generate full factorial or Latin Hypercube Sampling design
- Submit to `ProcessPoolExecutor` (true CPU parallelism, bypasses GIL)
- Display results as heatmap, scatter matrix, or response surface
- Export: results table CSV + contour plot

**Key files:** `main_window.py` (`_BatchWorker`), new `analysis/parametric_sweep.py`

---

### 4.4 Adaptive Time-Stepping in Coupled Loosening Analyzer
**Effort S | Impact ★★**

The coupled loosening analyzer currently uses fixed cycle steps. Loosening is highly
nonlinear across the five phases (Phase B, `[LMQ §12.1]`): rapid in Stage 1 /
TRANSITION (first 50–500 cycles), slow in NON-ROTATIONAL, rapid again in RUNAWAY.
Adaptive stepping reduces computation by 5–10× without loss of accuracy.

**Phase-aware stepping strategy:**
- **STABLE**: step = 100–500 cycles (minimal change expected)
- **NON-ROTATIONAL**: step = 10–100 cycles (slow embedding + fretting)
- **TRANSITION**: step = 5–10 cycles (localized slip initiating)
- **ROTATIONAL**: step = 1–5 cycles (steady nut rotation, monitor carefully)
- **RUNAWAY**: step = 1 cycle (every cycle counts; imminent failure)

**Criterion:** if `|ΔF_p_step / F_p| > 0.5%`, halve step size; if < 0.05%, double it.
Phase change detection forces a step-size reset to the finer value for the new phase.

**Key files:** `coupled_loosening_analyzer.py`

---

### 4.5 GPU Acceleration for Large N-DOF Models
**Effort L | Impact ★**

For models with N ≥ 500 DOF (complex multi-element assemblies), matrix operations
dominate compute time. GPU acceleration via CuPy or PyTorch provides 10–100× speedup.

**Approach:**
- Add optional dependency: `cupy` (NVIDIA) or `torch` (cross-platform GPU)
- Abstract matrix operations behind a backend selector: `cpu` / `cuda` / `mps` (Apple)
- Auto-detect GPU and use it when N > 200 DOF
- Fallback gracefully to numpy/scipy when GPU unavailable

**Key files:** `core/models/model.py`, `numerical/time_integration.py`,
new `utils/backend.py`

---

### 4.6 Fretting Regime Map Visualization
**Effort S | Impact ★★**

Phase D implements the Vingsbo–Söderberg fretting regime classification (`[LMQ §11.1]`)
as internal logic (`compute_fretting_regime()` in `contacts/base.py`). Exposing this
as a **plot in the Results tab** would give engineers direct insight into which wear
regime their joint is operating in, and how close they are to regime transitions.

**Approach:**
- Plot the Vingsbo–Söderberg map: axes = slip amplitude δ [µm] vs. normal force F_n [N]
  (log-log scale); regions = STICK / PARTIAL SLIP / GROSS SLIP
- Overlay the current joint's operating point (computed from Phase D slip amplitude)
- Animate as a function of cycle count: the point moves as preload decays and µ degrades
- Show the Mindlin stick-zone annulus radius `c = a × (1 − Q/(µP))^(1/3)` and slip index
  SI = δ_slip/δ_total as a secondary indicator (`[LMQ §11.2]`)
- Highlight when operating point crosses the partial-slip → gross-slip boundary: this
  triggers 1–2 orders of magnitude increase in wear coefficient

**Prerequisite:** Phase D (fretting regime classification implemented).

**Key files:** `gui/main_window.py` (ResultsTab), `visualization/loosening_plots.py`
(new `plot_fretting_regime_map()` method)

**Reference:** Vingsbo & Söderberg (1988), Fouvry et al. (1996); `[LMQ §11.1–§11.2]`

---

## 5. Reporting and Standards Compliance

### 5.1 Full VDI 2230 Calculation Report (R0–R15)
**Effort L | Impact ★★★**

VDI 2230 defines a systematic 15-step procedure (R0–R15) for complete bolted joint
analysis. BAS implements most of the physics but does not follow the VDI numbering
or produce a formally compliant report.

**Steps not yet in BAS:**
- R4: Minimum assembly preload (tightening factor α_A)
- R6: Proof of no plastic deformation of clamped parts (surface pressure)
- R7: Fatigue strength assessment (SA, σ_a, safety against fatigue)
- R10: Axial loading factor (this is Φ — Phase A)
- R11: Assembly tightening torque
- R13: Shear stress check under tightening
- R15: Loosening safety — quantitative slip check (uses Pai-Hess from Phase C)

**Output:** Generate a numbered VDI 2230 checklist HTML report with PASS/FAIL for each R-step.

**Key files:** `gui/main_window.py` (Reports tab), new `reports/vdi_2230_report.py`
**Reference:** VDI 2230 Part 1 (2015), Part 2 (multi-bolt)

---

### 5.2 ASME PCC-1 Bolt-Up Procedure Calculator
**Effort M | Impact ★★**

ASME PCC-1 (2019) provides guidelines for pressure boundary bolted flange joint assembly.
It defines target assembly bolt stress, pass sequences, and retorque requirements.

**Approach:**
- Input: flange class (ANSI B16.5 / EN 1092), bolt size, gasket type, operating pressure
- Compute: minimum gasket seating stress, minimum bolt load, required assembly bolt stress
- Output: torque table (pass 1/2/3 targets), recommended retorque interval
- Check: bolt load vs. flange rating (flange integrity)

**Key files:** new `analysis/asme_pcc1.py`, `gui/main_window.py` (new analysis wizard)
**Reference:** ASME PCC-1 (2019), ASME B16.5, EN 1591-1

---

### 5.3 DIN 65151 / ISO 16130 Vibration Test Report
**Effort S | Impact ★**

When the loading is configured as a Junker transverse vibration test (square waveform,
standard amplitude, standard cycles), automatically generate a DIN 65151 / ISO 16130
compliant test report.

**Approach:**
- Detect configuration: load type = TRANSVERSE, waveform = square (Phase A), n_cycles
  = 2 000 (ISO 16130 reference) or 3 500 (DIN 65151)
- Phase B (ISO 16130 warning) already emits a text warning when F_p_final / F_p0 < 0.80;
  this report formalizes that into a structured document
- Report content: test parameters, preload retention curve, PASS/FAIL against 80%
  criterion `[LMQ §12.5]`, comparison to plain-nut reference result, locking device
  retention range overlay (Phase F data, `[LMQ §13.1]`)
- For Nyloc/prevailing torque devices: report residual plateau analysis vs.
  ISO 2320:2015 torque values `[LMQ §13.2]`

**Key files:** `gui/main_window.py` (Reports tab)
**Reference:** DIN 65151 (2002), ISO 16130:2015

---

### 5.4 ISO 16130:2015 Formal Test Simulation Protocol
**Effort S | Impact ★★**

Phase B introduces an inline ISO 16130 warning message when final preload retention
drops below 80%. This item goes further: a **standardized test simulation protocol**
that reproduces the exact ISO 16130 test procedure in software.

**ISO 16130 requires:**
- Fixed Junker amplitude (per bolt size table — 0.3–1.0 mm for M8–M16)
- 2 000 cycles at 12.5 Hz
- Reference specimen: plain nut on same bolt
- Locking device must retain ≥ 80% of initial preload

**Approach:**
- "Run ISO 16130 Test" button in Solver tab: auto-configures amplitude, waveform,
  n_cycles from bolt diameter using the standard's amplitude table
- Run two simulations: (1) plain nut reference, (2) current locking device
- Generate side-by-side report: preload curves, retention at 2 000 cycles,
  PASS/FAIL relative to 80% criterion and relative to plain nut
- Compare simulation result against Phase F locking device database retention ranges —
  if simulation result is outside the database's expected range, flag as anomaly

**Prerequisite:** Phase B (ISO 16130 warning), Phase F (locking device database).

**Key files:** `gui/main_window.py` (Solver tab + Reports tab),
new `reports/iso_16130_report.py`

**Reference:** ISO 16130:2015 §4–§6; `[LMQ §12.5, §13.1]`

---

## 6. GUI and User Experience

### 6.1 Interactive Plot Layer (Zoom, Pan, Cursor)
**Effort M | Impact ★★**

All BAS plots use static matplotlib figures. Adding zoom, pan, and hover cursor would
significantly improve usability for analyzing loosening curves and stage transitions.

**Approach:**
- Embed matplotlib NavigationToolbar2QT on each plot canvas
- Add a hover cursor that reads out (N_cycles, F_p/F_p0, current_phase) on mouseover
- Double-click to annotate a point permanently on the plot
- Right-click on plot → context menu: "Set as reference", "Add vertical marker", "Export point data"

**Key files:** `gui/main_window.py` (ResultsTab matplotlib canvases)

---

### 6.2 Dark / Light / High-Contrast Theme Toggle
**Effort S | Impact ★**

BAS uses Catppuccin Mocha (dark) exclusively. Users on high-brightness displays or
with visual accessibility needs may require a light or high-contrast theme.

**Approach:**
- Store theme name in `QSettings` (Preferences dialog already exists)
- Define `Theme.LIGHT` palette (Catppuccin Latte) alongside existing `Theme.MOCHA`
- Apply via `QApplication.setStyleSheet()` at startup and from Preferences
- High-contrast: WCAG AA compliant colour pairs (≥ 4.5:1 contrast ratio)

**Key files:** `gui/main_window.py` (Theme class), `gui/msd_builder.py`

---

### 6.3 Undo / Redo for All Operations
**Effort M | Impact ★★**

Undo/redo is currently only partially available. A full `QUndoStack`-based system
would make the MSD Builder and property changes much safer to explore.

**Approach:**
- Implement `QUndoCommand` subclasses for: add element, delete element, move element,
  change property, load from file, apply template
- Display undo history in a panel (Ctrl+Z = undo, Ctrl+Y = redo)
- Limit stack depth to 50 operations

**Key files:** `gui/msd_builder.py` (SchematicView, MSDBuilderWindow)

---

### 6.4 Comparison Mode — Side-by-Side Results
**Effort M | Impact ★★**

Engineers frequently want to compare two analyses (e.g., as-designed vs. worn µ, or
M16 vs. M20 bolt). Currently they must export results and compare manually.

**Approach:**
- Store up to 4 named result sets ("Run 1", "Run 2", …) alongside the existing pinned result
- ResultsTab: toggle "Comparison mode" → each plot shows all stored curves in distinct colours
- Summary table: delta column showing % change between runs
- Overlay on Stage Analysis animation: two simultaneous colored lines

**Key files:** `app_state.py`, `gui/main_window.py` (ResultsTab)

---

### 6.5 In-App Formula Reference Panel
**Effort S | Impact ★**

A collapsible side panel showing the key formulas for the currently active tab
(e.g., loading formula when in Solver tab, slip criterion when running coupled loosening).
Acts as a built-in quick reference, reducing the need to consult external documents.

**Approach:**
- QDockWidget on right side, toggleable with F1
- Content is HTML from a per-tab formula dictionary (LaTeX rendered via MathJax or
  matplotlib math text to PNG)
- Links to relevant sections: `[LMQ §12]` (phase model), `[LLC §5]` (combined loading),
  `[LFD §2]` (load factors), VDI 2230 clause references
- Loosening threshold table from `[LMQ §12.5]` always visible in the Solver tab panel

**Key files:** `gui/main_window.py`

---

### 6.6 Smart Parameter Suggestions
**Effort M | Impact ★★**

When the user enters a bolt diameter, many other parameters can be suggested:
recommended preload (70% yield), typical µ for common surface conditions,
recommended waveform/amplitude for Junker testing, etc.

**Approach:**
- After bolt diameter + grade + surface condition are entered, compute and display:
  `"Suggested: F_p = 95 kN (70% yield), µ = 0.12 (Dacromet), T_tighten = 195 N·m"`
- One-click "Apply suggestions" to fill all fields
- Suggestions sourced from VDI 2230 Table values, `[LMQ §8.2]` friction ranges,
  and `materials_database.py`
- Extend to suggest load type: "For rotating machinery → consider adding TORSIONAL
  loading (§1.7); for pressure vessel → AXIAL_TENSION dominant"

**Key files:** `gui/msd_builder.py` (PropertyInspector)

---

### 6.7 Self-Locking Condition Margin Dashboard
**Effort S | Impact ★★**

Phase D implements `_check_self_lock()` as an internal check (`[LMQ §11.4]`). The
self-locking condition `tan(λ) < µ × cos(α)` is the fundamental boundary between a
joint that can sustain preload and one that will spontaneously unwind. Exposing this
as a **live margin indicator** would give engineers continuous feedback during analysis.

**Self-locking margin:** `SL_margin = (µ × cos(α) − tan(λ)) / tan(λ)`
- `SL_margin > 1.0`: strongly self-locking (typical new bolt: µ=0.12, margin ≈ 1.4×)
- `SL_margin ≈ 0`: boundary condition (danger zone)
- `SL_margin < 0`: not self-locking → spontaneous loosening irreversible

**For M16 × 2.0 under fretting (Phase D):**
- New bolt: µ = 0.12 → margin = 1.40× (safe)
- After fretting wear: µ = 0.045 → margin ≈ 0.04× (boundary)
- `[LMQ §11.4]` shows µ drops 20–40% after 5 000 fretting cycles

**Approach:**
- Add a "Self-Locking Margin" gauge widget to the Results tab (or Solver progress panel)
- Gauge shows SL_margin vs. cycle count as a line plot
- Color: green (> 0.5), yellow (0.1–0.5), red (< 0.1)
- When SL_margin crosses zero: display "Self-locking lost at cycle N — transition to
  ROTATIONAL phase is irreversible"
- Inputs: helix angle λ (from thread geometry), flank angle α (30° for ISO metric),
  evolving µ from Phase D fretting model

**Prerequisite:** Phase D (fretting wear µ coupling and `_check_self_lock()`).

**Key files:** `gui/main_window.py` (ResultsTab), `visualization/loosening_plots.py`

**Reference:** `[LMQ §11.4]`

---

### 6.8 Loading Condition Advisor Panel
**Effort S | Impact ★★**

LLC classifies eight loading conditions by severity (★★ to ★★★★★) and identifies which
mechanisms are active for each `[LLC §overview]`. Currently, the user must know this
theory independently. A **loading condition advisor** would diagnose the configured
loading and provide actionable guidance within the application.

**Approach:**
- After loading parameters are entered (load type, amplitude, frequency, R-factor),
  auto-classify severity using the LLC ranking table
- Display a summary panel (collapsible, in Solver tab):
  ```
  Loading type:  TRANSVERSE (Junker)
  Severity:      ★★★★★ (Highest)
  Mechanism:     Rotational (bearing + thread simultaneous slip)
  Typical N50%:  10² – 10³ cycles
  Key risk:      Slip onset at only 46–66% of µ×F_p (Pai-Hess)
  Analysis:      Coupled Loosening Analyzer recommended
  Check:         F_K_min = 42 kN (>0 — no separation risk)
  ```
- Show the combined interaction margin (§2.4) as a compact ratio:
  `F_T / (µ×F₀) + F_A/F_sep = 0.67 (margin = 0.33)`
- Flag when loading is AXIAL_TENSION: "Axial loading does NOT cause Junker rotational
  loosening. Fatigue assessment is the critical check. `[LLC §1.1]`"
- Flag when transverse displacement exceeds 2 mm: "Complete loosening possible in
  < 50 cycles (bearing-type joint, 2 mm amplitude). `[LLC §2.3]`"

**Prerequisite:** Phase A (R-factor and F_K_min labels in GUI), Phase C (loading type gate).

**Key files:** `gui/main_window.py` (SolverTab), new `analysis/loading_advisor.py`

**Reference:** `[LLC §overview]` severity table; `[LLC §1.1, §2.3]` quantitative data

---

## 7. Integration and Interoperability

### 7.1 FEA Export (ANSYS APDL / Abaqus INP)
**Effort L | Impact ★★**

BAS provides a simplified MSD model. For detailed stress distribution or complex
geometries, exporting to full FEA is needed. This bridges BAS (rapid parameter study)
with FEA (detailed verification).

**Approach:**
- Export MSD elements as ANSYS COMBIN14 (spring-damper) or COMBIN39 (nonlinear spring)
- Export contact pairs as ANSYS CONTAC12 / Abaqus SPRING2 elements
- Write preload as ANSYS PSMETH or Abaqus `*INITIAL CONDITIONS, TYPE=STRESS`
- Include material properties, loads, boundary conditions
- Output: `.mac` (ANSYS) or `.inp` (Abaqus) file

**Key files:** new `io/fea_export.py`

---

### 7.2 CAD Bolt Data Import (SolidWorks / CATIA / STEP)
**Effort L | Impact ★**

Import bolt assembly geometry directly from CAD to auto-populate BAS element properties:
bolt length, grip length, washer geometry, flange contact areas.

**Approach:**
- Parse STEP AP214 or AP242 files using `pythonOCC` or `ifcopenshell`
- Detect bolted joint patterns (circular hole patterns = bolt circle)
- Extract: bolt nominal diameter (from hole size), grip length, contact areas
- Map to BAS element types automatically; user confirms and edits

**Key files:** new `io/cad_import.py`

---

### 7.3 Python API / SDK for External Scripts
**Effort M | Impact ★★**

Power users (researchers, Petrobras engineers) want to run BAS analyses from their own
Python scripts for batch parametric studies, integration into CI pipelines, or coupling
with other tools.

**Approach:**
- Expose a public Python API (no GUI required):
  ```python
  from bolt_analysis_studio import BoltJoint, LoadingConfig, run_loosening_analysis
  joint = BoltJoint.from_preset("M16_flanged")
  joint.loading.F_preload = 80_000   # N
  joint.loading.R_factor = -1.0      # Fully reversed (Junker)
  result = run_loosening_analysis(joint, n_cycles=5000)
  print(result.preload_ratio_at(1000))
  print(result.phase_at(1000))        # "ROTATIONAL"
  ```
- Document with docstrings + Sphinx-generated HTML reference
- Provide Jupyter notebook examples

**Key files:** new `bolt_analysis_studio/api.py`, `docs/` (Sphinx config)

---

### 7.4 CMMS / Maintenance System Export
**Effort S | Impact ★★**

For plant equipment, loosening predictions should flow into Computerised Maintenance
Management Systems (SAP PM, IBM Maximo) as maintenance task triggers.

**Approach:**
- Compute predicted retorque interval: `N_retorque = N at F_p/F_p0 = 0.85`
  (five-stage model Phase B: NON-ROTATIONAL → WARNING boundary at 0.75, so 0.85
  provides a conservative maintenance trigger)
- Express in operating hours: `T_hours = N_retorque / (frequency × 3600)`
- Export as ISO 15926 XML or simple CSV: `[Equipment_ID, Bolt_ID, Next_Retorque_Date, Torque_Nm]`
- Users can configure: equipment tag, bolt tag, current operating date

**Key files:** `gui/main_window.py` (Reports tab), new `io/cmms_export.py`

---

### 7.5 Material Database Community Sync
**Effort M | Impact ★**

The materials database currently includes ASTM/ISO standard materials. Extending it
with community-sourced tribological data (measured µ from real experiments) would
improve accuracy for real-world surface conditions.

**Approach:**
- Host a central JSON file at a GitHub repository (or project server)
- "Check for updates" button in Material Database dialog
- Contributions: users can submit validated µ measurements with surface condition tags
- Review process: project team approves before merging to the curated database

**Key files:** `core/databases/materials_database.py`, `gui/main_window.py`

---

## 8. Long-Term Research Directions

### 8.1 Machine Learning — Loosening Life Prediction
**Effort L | Impact ★★**

With enough simulation results + experimental data, a surrogate model (neural network
or Gaussian process) can predict loosening life orders of magnitude faster than full
simulation. This enables real-time optimization and digital twin applications.

**Approach:**
- Generate training set: 10 000+ simulations across (d, p, µ, F_p, δ, frequency, R,
  Φ, waveform) parameter space — the Phase A load factors significantly expand the
  meaningful parameter space
- Train a feed-forward neural network: inputs = 10–14 joint/loading parameters,
  output = (N_to_20%_loss, N_to_ROTATIONAL, final_preload_ratio, SL_margin_trajectory)
- Validate against held-out simulation results (R² > 0.95 target)
- Integrate as "Fast Predict" mode: instant result without full cycle simulation

**Key files:** new `analysis/ml_surrogate.py`, training script, saved model weights
**Dependency:** `scikit-learn` or `torch` (already optional per GPU item above)

---

### 8.2 Digital Twin with Live Sensor Feedback
**Effort L | Impact ★★★**

Combining sensor integration (§3.2), ML prediction (§8.1), and multi-bolt analysis
(§2.1) creates a true digital twin: a live-updating simulation that mirrors actual
equipment state and predicts future failure.

**Approach:**
- Continuously ingest sensor data (ultrasonic bolt tension, vibration, temperature)
- Update simulation parameters via Kalman filter or least-squares fitting
- Predict remaining useful life (RUL) and optimal retorque time
- Alert: when RUL < threshold → trigger maintenance work order (§7.4 CMMS export)

This is the long-term research direction most aligned with the Petrobras R&D mandate.

---

### 8.3 Corrosion–Loosening Interaction
**Effort L | Impact ★★**

Corrosion in a bolted joint:
1. Increases surface roughness (more embedding loss at each load cycle)
2. Changes µ: rust initially increases µ, then fretting debris lubricates → µ drops
3. Reduces effective cross-sectional area (pitting) → lower yield and fatigue strength
4. Galvanic corrosion (e.g., steel bolt + aluminium flange) accelerates material loss

**Approach:**
- Time-dependent corrosion models: uniform corrosion (Faraday law), pitting (Monte Carlo)
- Update Rz, µ, and A_s at each corrosion time increment
- Couple to loosening analysis: corroded joint loosens faster; reduced µ from corrosion
  debris accelerates self-locking condition violation (§6.7)
- Experimental validation: accelerated salt spray tests + Junker testing

**Reference:** ISO 9227, ASTM B117 (salt spray), NACE standards

---

### 8.4 Acoustic Emission / Vibration Signature for Looseness Detection
**Effort L | Impact ★★**

Non-destructive detection of loosening in service is a major industrial challenge.
Acoustic emission (AE) sensors detect micro-slip events as stress waves; vibration
signatures change as preload drops (natural frequency decreases).

**Approach:**
- Compute natural frequencies from assembled [M][K]: `f_n = (1/2π) sqrt(K/M)`
- Model the sensitivity: `Δf_n / f_n ≈ −0.5 × ΔF_p / F_p` (approximate)
- Generate synthetic AE signal characteristics (amplitude, frequency, count rate)
  as a function of loosening phase (Phase B five-stage model provides phase labels)
- Compare to measured AE data to identify loosening stage non-invasively

**Key files:** new `analysis/nde_signatures.py`

---

### 8.5 Variable-Amplitude Loosening Spectrum Analysis
**Effort L | Impact ★★**

Phase E implements Miner's rule for discrete amplitude blocks (`[LMQ §12.3]`). Real
service loads have continuous random spectra (PSD). Extending the damage model to
handle PSD inputs enables fatigue-loosening life prediction for complex service
environments (wind turbine bolts, automotive, aerospace).

**Approach:**
- Accept PSD input: `S(f)` spectral density vs. frequency [mm²/Hz]
- Rainflow-count the time history to extract amplitude distribution
- Apply D-N power law: `N_i = A × δ_i^(−b)` (fitted from Phase E validation)
- Compute cumulative loosening damage: `D = Σ(n_i / N_i)`; failure at D = 1
- Integrate with probabilistic model (§1.2): scatter in µ and F_p creates PDF of
  loosening life, not just a single predicted value
- Application: IEC 61400-1 wind turbine load spectrum → bolt maintenance interval prediction

**Prerequisite:** Phase E (Miner's rule D-N), and at minimum Phase C (Pai-Hess
corrected slip threshold for accurate N_i values).

**Key files:** new `analysis/spectrum_loosening.py`, `coupled_loosening_analyzer.py`

**Reference:** Yang et al. (2019), PMC Materials (2025); `[LMQ §12.3, §12.4]`

---

## 9. Priority Summary

| # | Improvement | Effort | Impact | Recommended Order |
|---|-------------|--------|--------|-------------------|
| 3.1 | Junker Test Data Import + Curve Fitting | M | ★★★ | 1st — immediate validation |
| 1.2 | Probabilistic / Monte Carlo Analysis | M | ★★★ | 2nd — industrial requirement |
| 1.1 | Fatigue–Loosening Competition | M | ★★★ | 3rd — completes failure model |
| 5.1 | Full VDI 2230 R0–R15 Report | L | ★★★ | 4th — compliance requirement |
| 2.1 | Multi-Bolt Flange Load Distribution | L | ★★★ | 5th — Petrobras use case |
| 6.7 | Self-Locking Condition Margin Dashboard | S | ★★ | 6th — high value, Phase D output |
| 6.8 | Loading Condition Advisor Panel | S | ★★ | 7th — user guidance, Phase A/C output |
| 1.7 | Torsional Vibration Loading Mode | M | ★★ | 8th — unmodeled severity mechanism |
| 5.4 | ISO 16130 Formal Test Simulation Report | S | ★★ | 9th — Phase B/F extension |
| 4.6 | Fretting Regime Map Visualization | S | ★★ | 10th — Phase D visualization |
| 2.4 | Combined Loading Interaction Margin Chart | S | ★★ | 11th — Phase A/C visualization |
| 7.3 | Python API / SDK | M | ★★ | 12th — research productivity |
| 4.3 | Parallel Batch / Parametric Sweep | M | ★★ | 13th — enables sensitivity studies |
| 4.2 | LuGre Friction — Full Implementation | M | ★★ | 14th — physics accuracy |
| 6.1 | Interactive Plot (Zoom/Pan/Cursor) | M | ★★ | 15th — daily usability |
| 6.4 | Side-by-Side Comparison Mode | M | ★★ | 16th — analysis workflow |
| 4.1 | Hertz Contact Nonlinearity | M | ★★ | 17th — low-preload accuracy |
| 3.2 | Ultrasonic Sensor Integration | M | ★★★ | 18th — digital twin foundation |
| 3.4 | Locking Device Selection Wizard | M | ★★ | 19th — Phase F extension |
| 1.4 | Thermal–Structural Coupling (ratcheting) | M | ★★ | 20th — process plant relevance |
| 5.2 | ASME PCC-1 Bolt-Up Calculator | M | ★★ | 21st — process industry |
| 8.5 | Variable-Amplitude Spectrum Analysis | L | ★★ | Long-term research |
| 8.1 | Machine Learning Surrogate | L | ★★ | Long-term research |
| 8.2 | Digital Twin — Full System | L | ★★★ | Long-term research |
| 8.3 | Corrosion–Loosening Interaction | L | ★★ | Long-term research |

---

*Document created 2026-02-23. Updated 2026-02-23 with insights from LOAD_FACTORS_DESIGN.md,
LOOSENING_LOADING_CONDITIONS.md, LOOSENING_MECHANISMS_QUANTITATIVE.md, and
LOOSENING_IMPLEMENTATION_PLAN.md. Update as items are completed or new requirements emerge.*
