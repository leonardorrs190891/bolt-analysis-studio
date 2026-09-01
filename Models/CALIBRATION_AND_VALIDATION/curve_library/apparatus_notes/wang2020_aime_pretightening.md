# Wang 2020 (Adv. Mech. Eng.) — pre-tightening & relaxation mechanism, M14 [REFERENCE ONLY]

**Citation:** "Research on bolt pre-tightening and relaxation mechanism under transverse
load", *Advances in Mechanical Engineering* 12(12) (2020).
**DOI:** [10.1177/1687814020975919](https://doi.org/10.1177/1687814020975919) (gold OA)
**PDF:** `pdfs_manual_download/wang2020_aime_pretightening.pdf`

## Status: NO curves digitized

The preload-attenuation curves (Figs 15/17) are **finite-element results** (2 transverse
cycles, friction-coefficient sweeps), not experiments — fails the library's
experimental-curve criterion. Kept as a modeling reference.

## Useful reference content (MSD/V2 modeling)

- **M14** bolted joint FE model with real helix thread mesh; preload 20 kN; torque 40 N·m.
- Experimentally-anchored **torque-vs-preload relation** (Fig 3: FEM vs Yamamoto theory vs
  test-machine data) — useful for torque-coefficient checks.
- Clean taxonomy of bearing-surface contact states under transverse load: **viscous
  (stick) → partial slip → full slip**, with hysteresis loops (Fig 10) — the same slip
  taxonomy behind V2's `slip_onset_factor` / partial-slip gating.
- Friction-coefficient sweeps (bearing vs thread) showing which interface controls
  loosening onset — qualitative support for `mu_bearing_eff` being the damage-modulated
  friction in V2.
