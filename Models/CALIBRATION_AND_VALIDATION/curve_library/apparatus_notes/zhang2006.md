# Zhang, Jiang & Lee 2006 (J. Press. Vessel Tech.) — clamped length & loading direction, M12

**Citation:** Ming Zhang, Yanyao Jiang (Univ. Nevada Reno), Chu-Hwa Lee (Ford), "An
Experimental Investigation of the Effects of Clamped Length and Loading Direction on
Self-Loosening of Bolted Joints", *J. Pressure Vessel Technology* 128(3):388–393, Aug 2006.
**DOI:** [10.1115/1.2217972](https://doi.org/10.1115/1.2217972) — printed on the PDF's first
page. (`CALIBRATION_CURVE_DATABASE.md` lists `10.1115/1.2349572` for this paper — that DOI
is a different JPVT 128(4) item; the database entry needs correcting.)
**PDF:** `BAS_V2_papers/B. Biblioteca local catalogada (titulo + link + curvas extraidas)/An
Experimental Investigation of the Effects of Clamped Length and Loading Direction on
Self-Loosening of Bolted Joints.pdf` (6 pages, embedded rasters ~995 px wide)

## Why this source is special (and what it does NOT contain)

- It is the gallery's **grip-separatrix source (`ZHANG_2006`)** — but the paper does **NOT
  publish P-vs-N decay curves per grip/direction**. Its per-condition results (Figs. 4–9)
  are **endurance curves Δδ/2 vs N_L** (fatigue-S-N style scatter: Stage-I life N_I, N_75%,
  total-loosening life N_L, plus run-outs), same situation as Bauer 2024's boundary curves.
- The only genuine P-vs-N curves in the PDF are **Figs. 3, 12 and 16** — now digitized (see
  table below). The 9 `extracted_csv/03_Zhang_Jiang_2006_clamped_length__*` "table-approximate"
  F/F0 curves are **not traceable to this paper** (see Mismatch section).
- Real headline data: endurance limit grows with clamped length (0.165 → 0.285 mm, ~1.7×
  from L=48 to 68 mm) while the **load-carrying capacity stays ~constant** (ΔQ/2 ≈ 4.1–4.5 kN)
  — a direct target for the model's grip-scaling law (member compliance / c_bend / k_tr).

## Apparatus (MSD-block data)

- Servo-hydraulic **INSTRON** load frame; specially designed two-plate fixture attached by
  **pin joints** (no bending moment); line of action of the force lies in the contact plane
  of the two clamped plates. **Displacement-controlled**: extensometer (gage 25.4 mm) on the
  clamped plates controls the relative displacement δ between plates → V2 `delta_amp` mode.
- Plates **AISI 4340 steel**, 15.5 mm thick each, hole diameter 12.7 mm. Grip changed by
  adding insert pairs; per-side plate stack 15.5/19/20.5/25.5 mm. **Cast-iron changeable
  inserts at the sliding interface** + **LOCTITE nickel anti-seize** lubricant (low friction,
  inserts swapped as they wear).
- Overall clamped length **L = 48 / 54 / 58 / 68 mm** (includes 2 mm washer + 15 mm load
  cell); bolt lengths 70 / 80 / 80 / 95 mm respectively.
- **Bolt M12×1.75 class 10.9**, S301 coating; **flanged nut N802074-S427** (zinc undercoat +
  aluminum-rich dip-spin top coat); M12 zinc-plated washer, 2 mm, under the nut. Identical
  bolts/nuts throughout for constant friction.
- Clamping force: low-profile washer-type compression load cell (8 strain gauges, 15,000 lb)
  between bolt head and fixed plate. Nut rotation: **Schaevitz R60D RVIT** (±7.5 V for ±60°,
  125 mV/deg). DAQ 200 pts/cycle, continuous.
- **F0 = 25 kN for ALL self-loosening tests** (50–75% yield would be 25–52.5 kN; at 40 kN
  fatigue struck before loosening finished). **Frequency 0.5 Hz**, air, room temperature.
  Run-out = 40,000 cycles (~24 h).
- Loading-direction fixture (Fig. 2): Θ = angle between applied force and the contact
  surface; Θ=0° pure shear/transverse, 90° axial. Tested Θ = 0/15/30° at L = 54 mm.
- Stage demarcation: θ (nut-bolt rotation) = 0.5°; N_L defined at P reduced **to 25%** of
  P0; N_75% at P = 75% P0.
- Friction (measured, Figs. 14/15): current bolt/nut pair has **µ_thread inversely
  proportional to clamp force** (~0.21 mean at low P → ~0.08 at 40 kN); µ_bearing ≈
  0.125–0.14, ~independent of P. (Previous-study pair: both ~constant, µ_th ≈ 0.11,
  µ_b ≈ 0.14–0.17.) The paper credits the rising µ_thread during loosening for nut-rotation
  **arrest** near the endurance limit.

## Test matrix and REAL per-condition results (endurance, not P–N)

Amplitudes δ/2 = 0.10–0.45 mm, up-and-down method near the limit (run-out 40k cycles).

| Condition | Figure | Endurance limit Δδ/2 (range) | ΔQ/2 at limit |
|---|---|--:|--:|
| L=48 mm, Θ=0° | Fig. 4 | 0.165 (0.160–0.172) mm | 4.51 kN |
| L=54 mm, Θ=0° | Fig. 7 | 0.231 (0.220–0.242) mm | 4.48 kN |
| L=58 mm, Θ=0° | Fig. 5 | 0.252 (0.240–0.263) mm | 4.38 kN |
| L=68 mm, Θ=0° | Fig. 6 | 0.285 (0.278–0.301) mm | 4.11 kN |
| L=54 mm, Θ=15° | Fig. 8 | 0.234 (0.220–0.240) mm | — |
| L=54 mm, Θ=30° | Fig. 9 | 0.265 (0.256–0.276) mm | — |

(Endurance limits read from Figs. 10/11 with error bars; ΔQ/2 from Figs. 17/18 annotations.
Figs. 4–9 additionally hold N_I / N_75% / N_L scatter points per amplitude — digitizable as
life tables if ever needed, but they are **not** F/F0-vs-cycle curves.)

## Digitized curves (`digitized_csv/`, header `cycle,F_over_F0`)

| CSV | Fig | Conditions | pts | ratio range |
|---|---|---|--:|---|
| zhang2006_fig12_L54_phi15_25kN.csv | 12 | current rig, Θ=15°, L=54 mm, P0=25 kN, δ/2 **not reported** | 38 | 0.977 → 0.661 |
| zhang2006_fig3_illus_M12x125_20kN_amp0p35.csv | 3 | **previous-study rig**: M12×1.25 75 mm bolt, zinc-coated nut, P0=20 kN, δ/2=0.35 mm | 41 | 0.995 → 0.028 |
| zhang2006_fig16_runout_40kN_amp0p125.csv | 16 | **previous-study rig** "Combination I", P0=40 kN, δ/2=0.125 mm (just below its 0.13 mm limit) | 16 | 0.989 → 0.940 |

## Digitization caveats

- Digitized from the PDF's embedded rasters (~995×540 px, inverted polarity) via column-wise
  bright-run tracing calibrated on the axis ticks; overlay-verified. Resolution ≈ ±0.5% F/F0.
- **fig12**: after ~10³ cycles the decay is **fatigue-crack driven** (crack in the first
  engaged thread; dP/dN ≈ 1.0 N/cycle; nut rotation stops at θ≈1.55°). For pure-loosening
  calibration **trim to N ≤ 10³** (same convention as Yang2021 / li2022ti fracture tails).
  Test stops at N≈4.3×10⁴ with P≈16.5 kN (no total loosening). Amplitude δ/2 is not stated
  in figure or text.
- **fig3**: labeled "Illustration of self-loosening process" — conditions match the authors'
  PREVIOUS rig (Jiang 2003/2004, M12×1.25, P0=20 kN), not this paper's matrix; possible
  overlap with `02_Jiang_2003_2004` extracted curves. Final collapse is near-vertical at
  N≈1.5–1.7×10⁴ (read from the descending front's lower envelope); terminal points 0.012 →
  0.028 are the drawn end-hook (load-cell noise at P≈0) — kept as drawn.
- **fig16**: null benchmark (no loosening, θ≈0): only Stage-I settling 0.989→0.940 over
  4.6×10⁴ cycles. Previous-study bolts ("Combination I"), P0=40 kN.

## Mismatch with `extracted_csv` (IMPORTANT — provenance)

The 9 table-approximate curves `03_Zhang_Jiang_2006_clamped_length__*.csv` claim conditions
that **do not exist in this paper**:

- grips "l_c = 12.7 / 25.4 / 38.1 / 50.8 mm (l/d 1.06–4.23)" → real grips are **48/54/58/68
  mm** (12.7 mm is the plates' HOLE diameter);
- directions "0/30/45/60/90° from transverse" → real directions are **Θ = 0/15/30°**;
- 5–8-point F/F0-vs-cycle decay curves per condition → the paper publishes **endurance
  scatter**, not decay curves, for those conditions.

`New_Theory/zhang_grip_sweep.py`'s header ("AISI 1045, 5 Hz, δ=0.46 mm, N50 15/65/175/350")
also disagrees with the paper (AISI 4340 + lubricated cast-iron interface, **0.5 Hz**, δ/2 ≤
0.45 mm; no per-grip N50 data). The gallery's `ZHANG_2006` grip separatrix therefore has
**no provenance in this PDF** — treat those 4 cases as synthetic until re-derived from the
real endurance data above. (F0 = 25 kN and M12 are correct.)

## V2 calibration mapping

- **Endurance limits vs L (Fig. 10)** = the natural quantitative target for the grip/member
  -stiffness scaling law (roadmap #10: c_bend per-rig, k_tr bending, arrest): the model must
  predict run-out below δ_lim(L) and collapse above it — a threshold sweep, not an MAE fit.
- **ΔQ/2 ≈ const (Figs. 17/18)** while δ_lim grows with L: discriminates displacement-driven
  vs force-driven slip criteria (Cattaneo–Mindlin split) — free cross-check, zero fit.
- **Direction family (Fig. 11)**: Θ=15° ≈ no change vs Θ=0°, Θ=30° only +15% — decompose the
  imposed δ into transverse cos Θ (drives slip) + axial sin Θ (drives nothing in-model);
  a falsifiable near-null prediction.
- **µ_thread(P) rising as preload drops (Fig. 14)** = measured input for the arrest form near
  the limit (the paper's own explanation for nut-rotation arrest).
- fig16 CSV = null case (no-loosening guard, like Grzejda); fig3 CSV = full two-stage decay
  to total loosening at the previous rig's conditions; fig12 CSV (trimmed ≤10³) = oblique
  -direction Stage-I+II sample at the real rig.
