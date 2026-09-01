# Basava & Hess (1998) — Bolted joint clamping force variation due to axial vibration

## Citation + DOI

S. Basava, D. P. Hess, "Bolted joint clamping force variation due to axial
vibration," *Journal of Sound and Vibration* 210(2) (1998) 255–265.
DOI: 10.1006/jsvi.1997.1330.

## Gap tag + why

**G1** — axial dynamic loading; intended as a second, independent axial rig to
complement Liu2016/Liu2017 in the calibration library. **Caveat up front: this
paper supplies no physical rig at all** (see "Rig/apparatus" below) — it is a
numerical-simulation companion to the real rig used in Hess & Sudhirkashyap
(1997, ref. [7], not in this batch). It still earns the G1 tag because its
level×preload regime map (steady / loosen / tighten, with a measured maximum
loosening of 52.9% and maximum tightening of 83.4%) is an independent,
quantitative axial-vibration data source not derivable from Liu2016/Liu2017,
and it supplies a **structural constraint** (sign change) that any V2 axial
mechanism must respect — see "V2 mapping" below.

## Rig/apparatus

**There is no physical rig in this paper.** It is a purely numerical study: the
"single-bolt assembly" is a lumped-parameter dynamic model (bolt mass `m_b`,
clamped-component mass `m_c`, base) connected through **non-linear
spring–damper contacts** (bolt-head `k_h,c_h`; thread `k_t,c_t`; clamped
component/base `k_i,c_i`) with a **Karnopp (1985) stick–slip friction model**
(kinetic/static friction pairs at head and thread, with a velocity dead-zone
`v_min`). The system input is a **prescribed sinusoidal base displacement**
`w = w₀·sin(ωt)` (i.e., an idealized shaker driving the base), fixed at
`ω = 2π(500) rad/s = 500 Hz` for every run in this paper. The "vibration
level" swept in Figures 4–6 is the **input acceleration amplitude
`ω²w₀`** (10–2000 m/s²) — so the control variable is **acceleration**, not
force or displacement directly (though displacement amplitude follows from
`w₀ = level/ω²`).

- **Loading direction**: axial (base motion along the bolt axis); the bolt is
  modeled as translating circumferentially at the pitch radius (`x`, coupled
  to twist angle `θ = x/r_p`) and axially (`y`), with the clamped component
  moving axially (`z`) — i.e., helix/thread coupling is built directly into the
  contact kinematics, analogous to V2's helix off-diagonal coupling.
- **Control mode**: **acceleration-controlled**, imposed through the governing
  ODEs (5th-order Runge–Kutta integration, `Δt = 4×10⁻⁶ s`).
- **"Clamping force" measurement**: **not measured** — it is the model's
  internal reaction `F_c = k_i·δ_i` at the clamped-component/base interface,
  read out directly from the simulated state at every instant. There is no
  load cell, no physical specimen, and no experimental noise floor; whatever
  point-to-point jitter appears in the plotted curves is purely numerical
  (integration/friction-model artifacts), confirmed by the paper's own
  numerical-convergence figures (see below).
- Model parameters (stiffnesses, dampers, friction coefficients) were
  originally **back-fit from acceleration measurements and bolt-twist
  observations** on a real single-bolt test apparatus described in the
  companion experimental papers (refs. [5]-[7]: Hess & Davis 1996 *JVA* Parts
  I–II; Hess & Sudhirkashyap 1997 *JVA* — none of these are in this digitization
  batch). This paper reuses that calibrated parameter set and runs it for much
  longer (up to ~2–3×10⁴ cycles) than the original short-time simulations in
  ref. [7].

## Specimen/materials

No physical specimen — abstracted into effective lumped constants (not tied to
a specific bolt class/material designation in the text):

- `r_p = 3.17 mm (0.125 in.)` — pitch radius, implying a small fastener
  (roughly 1/4"-scale thread), consistent with the "moderate pre-load...
  electronic equipment and joints with gaskets" framing in the text (the model
  explicitly targets **rigid-bolt-with-elastic-interfaces** behavior, not
  heavily preloaded structural bolts with axial/torsional bolt elasticity —
  flagged by the authors as future work).
- Lead angle `β = 0.05 rad (2.87°)`; thread clearance without pre-load
  `d₀ = 0.015 mm`.
- Contact stiffnesses: `k_h = 2.025×10⁷ N/m` (head), `k_i = 7.578×10⁴ N/m`
  (clamped-component/base), `k_t = 2.80×10⁷ N/m` (thread). Note `k_i` is
  ~300× softer than `k_h`/`k_t` — the clamped-component/base interface is the
  compliant one (this is what sets the clamping-force scale, `F_c = k_i·δ_i`).
- Damping: `c_h = 8.0×10⁶`, `c_i = 1.80×10⁴`, `c_t = 1.3×10⁸ Ns/m²` (non-linear,
  Hunt–Crossley-style, to avoid discontinuous contact/separation forces).
- Friction: `μ_h = μ_t = 0.2` (kinetic), `μ_ts = μ_hs = 0.22` (static) at both
  head and thread interfaces — plain Coulomb-type dry friction, no lubrication
  regime or surface-finish parameter given.
- No nut/washer/gasket geometry beyond what is folded into `k_h`/`k_i`/`k_t`.

## Test matrix

All at fixed frequency `f = 500 Hz` (never swept in this paper):

| Figure | Swept variable | Values | Fixed variable | #curves plotted |
|---|---|---|---|---|
| 2 | integration time-step `Δt` | 4×10⁻⁴, 4×10⁻⁵, 4×10⁻⁶, 4×10⁻⁷ s | P=45 N, level=750 m/s² | 4 (numerical check, **not digitized**) |
| 3 | Karnopp dead-zone `v_min` | 1×10⁻³, 1×10⁻⁴, 1×10⁻⁵, 4×10⁻⁹ m/s | P=45 N, level=750 m/s² | 4 (numerical check, **not digitized**) |
| 4 | initial pre-load `P` | 30, 35, 40, 45, 55, 75, 100 N | level = 750 m/s² | 7 — **loosening** |
| 5 | initial pre-load `P` | 12, 15, 17, 20, 25, 30 N | level = 750 m/s² | 6 — **tightening** (30 N shared with Fig. 4, boundary case) |
| 6 | acceleration level `ω²w₀` | 10, 80, 250, 500, 600, 750, 1000, 2000 m/s² | P = 20 N | 8 (a 9th level, 100 m/s², appears only in Table 2, not plotted) |

Duration: each run continues until the clamping force visibly "settles"
(the paper's own "cycles to steady state" column, Tables 1–2), ranging from
~150 cycles (fastest) to **31 250 cycles** (slowest, level=10 m/s²); plotted
x-axis extends to ~2–3×10⁴ cycles throughout (log scale).

**21 curves digitized** total (Figs. 4+5+6); Figs. 2–3 intentionally excluded
(see caveats).

## Experimental nuances

- **Central finding**: clamping force under axial vibration can **remain
  steady, decrease (loosen), or increase (tighten)**, depending on the
  preload × vibration-level combination — a genuine three-way qualitative
  split, not just a magnitude effect.
- **Transient-to-steady character**: every curve (however it moves) reaches a
  **new steady value** within the simulated window — none of the "good"
  (converged) curves show sustained drift or runaway. (One of the
  *non*-converged numerical-check curves in Fig. 2, at a too-coarse
  `Δt=4×10⁻⁴s`, does show a spurious dip-then-oscillate pattern — the paper
  itself flags this as a **numerical artifact**, not physical behavior.)
- **Preload boundary ("neutral band")**: at level=750 m/s², preload
  **27–32 N gives an essentially flat response** (steady, or steady with small
  oscillatory fluctuation, e.g. the 35 N curve, whose table entry shows a
  larger noise band `34.760 ± 0.520 N` than its neighbors). Below this band →
  tightening; above it → loosening. Cycles-to-steady-state and %-change both
  **increase monotonically with distance from the boundary** on the loosening
  side (30→100 N: 0→26 650 cycles, 0%→−30.4%) and on the tightening side
  (30→12 N: 0→15 050 cycles, 0%→+75.1%).
- **Non-monotonic vibration-level dependence** (at fixed P=20 N): loosening
  **deepens** as level drops from 250 to 80 m/s² (−15.7%→−52.9%, the
  **maximum loosening** in the whole study), then **recovers** as level drops
  further from 80 to 10 m/s² (−52.9%→−45.9%) — the worst case is at an
  **intermediate** level, not the lowest. Tightening onset is at level≈500 m/s²
  and grows monotonically to +83.4% at 2000 m/s² (the paper notes simulations
  at still-higher levels were in progress to see if tightening keeps growing).
- **Numerical robustness pre-checked** (Figs. 2–3) before trusting the
  long-time results: converged for `Δt ≤ 4×10⁻⁶ s` and `v_min` from
  10⁻⁴ to 10⁻⁹ m/s; the paper explicitly used the least-expensive converged
  setting (`Δt=4×10⁻⁶s`, `v_min=1×10⁻⁴ m/s`) for all of Figs. 4–6.
- **Model is a 2-translational-DOF equivalent**, not a true axial+torsional
  bolt: "the model described here represents an equivalent system in which the
  bolt can translate in two directions, x and y" — explicitly a simplification
  the authors flag as a target for future work (real axial/torsional bolt
  elasticity, relevant for more heavily preloaded bolts than modeled here).

## Main conclusions

1. Axial vibration produces one of three regimes — steady / loosen / tighten —
   set jointly by initial preload and vibration (acceleration) level.
2. Changes in clamping force are **transient**; a new steady value is always
   reached given enough cycles (150–31 250 in this study).
3. Maximum loosening found: **52.9%** (level=80 m/s², P=20 N) — the paper
   notes this is **~10% more severe** than Bickford's textbook claim of "up to
   40% reduction" for axial vibration (ref. [11]).
4. Maximum tightening found: **83.4%** (level=2000 m/s², P=20 N).
5. Combined axial+transverse+angular vibration (ref. [12], a companion thesis)
   achieves comparably large tightening (+50%, 80→120 N) at a **much lower**
   vibration level (25 g) than pure axial vibration needs in this paper —
   i.e., multi-axis excitation is a far more efficient tightening driver than
   axial alone.
6. The authors' own framing: this is a **simulation-only extension** of the
   short-time model+experiment pairing in ref. [7], now run to much longer
   times specifically to characterize the *transient-to-steady* behavior that
   short simulations could not show.

## Curve inventory

| Figure | CSV(s) | x-unit | F0 | #pts | Notes |
|---|---|---|---|---|---|
| 4 (loosening, P-sweep @750 m/s²) | `basavahess1998_fig4_preload_{100,75,55,45,40,35,30}N.csv` | cycles | own preload | 18–31 | 7 files |
| 5 (tightening, P-sweep @750 m/s²) | `basavahess1998_fig5_preload_{30,25,20,17,15,12}N.csv` | cycles | own preload | 10–26 | 6 files; 30N reconstructed flat (see caveats) |
| 6 (level-sweep @P=20N) | `basavahess1998_level_{2000,1000,750,600,500,250,10,80}.csv` | cycles | 20 N | 17–20 | 8 files, named by acceleration level (m/s²) |
| 2, 3 (numerical checks) | — not digitized — | — | — | — | redundant w/ Fig.4's 45N curve; see caveats |

All 21 CSVs' final points were cross-validated against the paper's own Tables
1–2 (exact steady-state force, % change, cycles-to-steady-state for every
curve) — final-point agreement is within 0.05–1.7% across all 21 curves.

## V2 mapping

- **Loading mode**: acceleration-controlled base excitation → closest V2
  analog is the **force-controlled axial** mode (`step_cycle(F_amp,
  theta_load, freq)` without `delta_amp`), *not* Junker displacement-control;
  but note the excitation here is imposed on the *base*, not as a bolt-axial
  force amplitude directly, so even the "force-mode" analogy is approximate.
- **Constants are NOT transferable.** This is a friction/stick-slip
  lumped-parameter model (Karnopp), physically and mathematically unrelated to
  V2's energy-dissipation mechanism formalism (`EmbeddingLoss`, `CreepLoss`,
  `WearLoss`, `RotationalLoosening`). None of `k_h,k_i,k_t,c_h,c_i,c_t,μ,v_min`
  map onto any `JointMaterial` field. Only the **observed phenomenology**
  is portable.
- **Structural constraint the axial mechanism must respect — sign change.**
  This paper's central result is that net clamping force can **increase**
  (tighten) under pure axial vibration at low preload / high level. **All
  four current V2 loss mechanisms are one-signed** (`dF_0 ≤ 0` always —
  Embedding, Creep, Wear, RotationalLoosening only ever remove preload, never
  add it). V2 as currently built **cannot reproduce a tightening regime at
  all**, under any parameter choice, in either force- or displacement-control
  mode. This is a capability gap distinct from — and more fundamental than —
  roadmap item 9's amplitude-sensitivity gap: it is not that the *slope* is
  wrong, it's that the *sign* is structurally unreachable. No CSV in this
  digitization batch should be fit against the current engine (a fit would
  necessarily fail on every Fig. 5/Fig. 6 tightening curve, and "succeed" only
  on Fig. 4's loosening curves by accident of sign). Flag for
  `MODEL_LEGITIMACY.md` if/when an axial-tightening mechanism is scoped.
- **Second, independent confirmation of non-monotonic dose/level response**:
  the worst-case loosening at an *intermediate* vibration level (not the
  extreme) here echoes the same qualitative shape noted in the (unrelated,
  already-falsified) predictive-damage-trigger work — useful corroborating
  context if a level/dose-based driver is revisited, but this paper's specific
  numbers are not transferable (different rig entirely, in fact no rig at all).
- **Preload "neutral band"** (27–32 N boundary at fixed level) is a second,
  independent qualitative echo of pressure/preload-dependent threshold
  behavior (cf. `MODEL_LEGITIMACY.md` §4.9 conformation work) — again, shape
  only, not constants (this model's constants are per-simulation, not
  per-rig-measured).

## Digitization caveats

1. **This paper contains zero experimental clamp-force curves.** Figures 2–6
   are 5th-order Runge–Kutta numerical-simulation output of the lumped
   stick-slip model described above. The paper's abstract references "recent
   experiments," but those live entirely in companion papers (refs. [5]-[7]),
   not in this PDF. Flagged per task instructions; digitized anyway per the
   assignment brief (the level×preload regime map is the paper's real
   contribution and is legitimate simulation data in its own right).
2. **Figures 2 and 3 were not digitized.** Both are numerical-method
   sensitivity checks (integration time-step; Karnopp dead-zone parameter) at
   a single condition (P=45N, level=750 m/s²) already covered by Figure 4's
   45N curve — not new physical/parametric data, and the non-converged traces
   in Fig. 2 are explicitly flagged by the authors as inaccurate.
3. **Digitization method**: axis calibration via automated tick-mark pixel
   detection (linear regression against 3–4 independent tick positions per
   axis; residuals <1% of one decade on the log-cycle axis, <0.3 N on the
   linear force axis). Curve traces were extracted via column-wise dark-pixel
   clustering; curve **identity** (which of the 6–8 overlapping line styles in
   each figure a given cluster belongs to) was resolved by matching against
   each curve's **exact tabulated endpoint** (Tables 1–2 give steady-state
   force, % change, and cycles-to-steady-state for literally every curve in
   Figs. 4–6 — an unusually strong cross-validation this paper affords). All
   21 curves' final digitized points agree with the tabulated steady-state
   force within 0.05–1.7%.
4. **Curve overlap/occlusion** limited transient-shape resolution in a few
   windows: Figure 5's 15/17/20 N curves converge to final values only
   1.0–1.5 N apart; Figure 6's 8 curves all originate from the *exact same*
   point (P=20N at cycle≈1) and separate gradually. In these windows (roughly
   cycles 300–4000 for several Fig. 6 tightening curves; cycles 1000–10000 for
   Fig. 5's slower 12N/15N curves), points are sparser and the shape between
   the last confident pre-transition point and the tabulated
   (cycles-to-steady, final-force) anchor is a smoother reconstruction rather
   than a dense pixel trace. The **force values** at those anchors are solid
   (sourced from the table text, not pixels); the **exact timing/shape** of
   the fastest part of the transition in these specific windows carries more
   uncertainty.
5. **Figure 5's 30N curve has no pixel trace.** Its value (~30 N) fell above
   the calibrated crop's visible pixel range (crop top edge ≈28.75 N — cropped
   before re-checking against this specific curve's range). Reconstructed as a
   flat line at the paper's exact tabulated value (29.975 N, 0.0% change),
   consistent with the text's explicit description ("remains steady").
6. **Table 2's level=100 m/s² row (final 9.507N) has no corresponding curve**
   — Figure 6's legend lists only 8 levels (10,80,250,500,600,750,1000,2000);
   100 m/s² was not digitized (no curve exists to trace).
7. For several of the **fastest tightening curves** (Fig. 5's 15N/17N/20N;
   Fig. 6's 750/1000/2000 m/s²), the pixel trace appears to reach the
   tabulated final value **somewhat later** in cycle-count than the paper's
   own stated "cycles to steady state" (by roughly a factor of 2–5×). This
   suggests the paper's tabulated cycle-count may use an early/approximate
   convergence criterion rather than full visual settling. CSVs follow the
   pixel-traced shape (not forced to the tabulated cycle number); only the
   **force** values are anchored exactly.
8. Figure quality is modest (1998, small print, up to 8 overlapping
   line-styles per plot) as flagged in the task brief; no further caveats
   beyond those above were required.
9. `F_over_F0` values **exceeding 1.0** in several CSVs (all of Fig. 5, most of
   Fig. 6) are the paper's real, central finding (tightening) — not a
   normalization or digitization error.
