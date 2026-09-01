# Sandia 2021 (IMAC XXXVIII) — C-Beam modal-excitation preload loss

**Citation:** "Bolt Preload Loss due to Modal Excitation of a C-Beam Structure", *Nonlinear
Structures and Systems Vol. 1* (IMAC XXXVIII, 2021). Sandia SAND2019-12525C.
**DOI:** [10.1007/978-3-030-47626-7_30](https://doi.org/10.1007/978-3-030-47626-7_30)
(OA accepted manuscript: [OSTI purl/1642845](https://www.osti.gov/servlets/purl/1642845))
**PDF:** `BAS_V2_papers/B.../Bolt Preload Loss due to Modal Excitation of a C-Beam Structure.pdf`

## Apparatus

- Two **4340 steel C-beams** bolted together (2 bolts), excited by a **modal shaker** at
  the assembly's **mode 1 (~275–288 Hz, in-phase bending)** — bending produces shear
  across the bolted interface (transverse-slip loading at very low amplitude).
- **Instrumented bolts (STRAINSERT internal strain gauge, 22.2 kN max)** give direct,
  continuous preload; DAQ streams preload during dwell tests of 5 / 15 / 30 min.
- Preload very low (~170–177 lbf ≈ 780 N) so the joint operates near the microslip
  threshold. Figs 6–11 of the paper are FEA — excluded.

## Specimen

- SAE grade 9 instrumented bolts; **nominal diameter not stated in the manuscript**
  (flagged: assume 1/4"–3/8" class from the STRAINSERT range when building the MSD model).
- 4340 steel C-beam pair, joint at beam ends.

## Trial matrix / digitized curves

| CSV | Test | Duration | x-axis conversion |
|---|---|---|---|
| sandia2021_cbeam_5min_bolt1.csv / _bolt2.csv | Fig 4 (lbf vs time) | 5 min | t × 280 Hz |
| sandia2021_cbeam_15min_bolt1.csv / _bolt2.csv | Fig 5 | 15 min | t × 280 Hz |
| sandia2021_cbeam_30min_bolt1.csv / _bolt2.csv | Fig 5 | 30 min | t × 280 Hz |

Losses: ~3.6% (5 min), ~4.9–5.9% (15 min), ~1.9–2.9% (30 min — later runs on
already-run-in joints lose less).

## Digitization caveats

- **Time→cycles conversion assumes 280 Hz** (paper: mode 1 at ~275–288 Hz depending on
  configuration) — cycle counts carry ±3% scale uncertainty; 5 min ≈ 84,000 cycles.
- Fig 4 normalized by each bolt's initial lbf (176.7 / 176.2).
- 30-min curves were run after prior tests (run-in surfaces) — NOT virgin joints; that is
  why they lose less than the 15-min tests. Treat each curve's history accordingly.

## V2 calibration mapping

- **Low-amplitude / slip-onset anchor**: exponential-then-linear decay, no stage II/III,
  no gross rotation. A calibrated V2 model must reproduce <6% loss over ~10^5–10^5.5
  cycles WITHOUT triggering rotational loosening → regularizer for `slip_onset_W`
  (upper bound on gate opening) and for `k_emb_scale`+`k_creep_scale` split.
- 5/15/30-min self-consistency: same joint, increasing accumulated cycles — checks state
  accumulation (`W_slip_acc`, δ_emb) across runs including run-in effects.
- Weak as a primary fitting target (preload ~780 N, size unknown) — use for validation.
