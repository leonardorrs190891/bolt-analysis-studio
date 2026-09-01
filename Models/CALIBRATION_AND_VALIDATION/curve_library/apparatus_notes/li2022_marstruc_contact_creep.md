# Y. Li 2022 (Marine Structures) — contact-creep clamping-force relaxation, M16

**Citation:** Y. Li et al., "A combined theoretical and experimental study on contact
creep-induced clamping force relaxation of bolted joints at ambient temperature",
*Marine Structures* 85 (2022) 103263.
**DOI:** [10.1016/j.marstruc.2022.103263](https://doi.org/10.1016/j.marstruc.2022.103263) (paywall; institutional copy)
**PDF:** `pdfs_manual_download/marstruc2022_contact_creep.pdf` (= `BAS_V2_papers/D. Rodada 3.../A combined theoretical and experimental study...pdf`)

## Why this source is special

**Pure static creep — NO vibration.** Isolates `k_creep_scale` (Norton/Burgers tail) from
wear/loosening completely. Also supplies **directly usable MSD spring-damper values**
(Burgers virtual-material model of the rough contact interface, Table 1):

| Param | Meaning | Value (AV of 3 tests) |
|---|---|---|
| K_B | bolt stiffness | 3.4089e8 N/m |
| K_P | clamped-part stiffness | 3.3892e9 N/m |
| K_1 | Burgers (Kelvin) spring of contact layer | 2.6084e9 N/m (scatter 1.0–4.8e9) |
| K_2 | Burgers (Maxwell) spring | 5.8673e7 N/m |
| C_1 | Kelvin damper | 4.3168e10 N·s/m |
| C_2 | Maxwell damper | 9.1695e12 N·s/m |

Model geometry inputs used: D = 60 mm, d = 16 mm, L = 20 mm, γ = 1.5, α = 36°,
E_P = 206 GPa. Max model-vs-test error 6.67% (10 kN case).

## Apparatus (MSD-block data)

- Single bolted joint **without gasket**, two identical connected parts, contact 60×60 mm.
- **Bolt: M16 × 80, 304 stainless steel** (E = 193 GPa, tensile 700 MPa) + nut.
- Preload by digital torque wrench (range 20–200 N·m), two-step per **EN 1090-2**
  (75% → 110% of target): 16 N·m → 5 kN; 30 N·m → 10 kN; 48 N·m → 15 kN.
- Clamp force: **FC-LW-150kN washer load cell** + Smacq USB-4000 DAQ, real time,
  **600 min** per relaxation run at 24–26 °C (25.2 °C reported).
- Burgers parameters from separate **Instron-8801 compression-creep tests** (10 kN,
  90 min, Ra 0.8, 3 repeats).
- Surface topography by ST 400 instrument; roughness variants Ra 0.078 / 0.122 / 0.306 /
  0.8 µm.

## Digitized curves (x column = TIME IN MINUTES, not cycles!)

| CSV | F0 | Ra (µm) | pts | R_F 600 min |
|---|--:|--:|--:|--:|
| li2022marstruc_creep_10kN_Ra0p8_min.csv | 10 kN | 0.8 | 12 | 0.9415 |
| li2022marstruc_creep_10kN_Ra0p078_min.csv | 10 kN | 0.078 | 12 | 0.9545 |
| li2022marstruc_creep_10kN_Ra0p122_min.csv | 10 kN | 0.122 | 11 | 0.9570 |
| li2022marstruc_creep_10kN_Ra0p306_min.csv | 10 kN | 0.306 | 13 | 0.9640 |
| li2022marstruc_creep_5kN_Ra0p8_min.csv | 5 kN | 0.8 | 7 | 0.9740 |
| li2022marstruc_creep_15kN_Ra0p8_min.csv | 15 kN | 0.8 | 10 | 0.9815 |

## Digitization caveats

- Digitized from the **fitting-curve centerlines**; the raw load-cell data is a ±2% scatter
  cloud around them (sensor noise), visible in Figs 9/14.
- Curves start at the post-tightening reading (96.7–100.4%), not at exactly 100% — the
  first seconds of relaxation happen during/right after torquing.
- **The x column holds minutes.** To use with cycle-based tooling, treat each minute as a
  pseudo-cycle at "0 Hz" (no transverse motion; delta_amp = 0, F_amp = 0).

## V2 calibration mapping

- **The dedicated `k_creep_scale` source** (gap since R2): fit V2's Norton creep tail with
  wear/loosening OFF (k_wear=k_loose=0, delta_amp=0) against the 600-min curves.
- Preload family (5/10/15 kN): creep-rate vs contact pressure → Norton stress exponent.
- Roughness family (0.078–0.8 µm): rougher → MORE relaxation retained?? No — Ra 0.8
  relaxes most (94.2%), Ra 0.306 least (96.4%) among 10 kN tests as plotted; supports
  emb_depth/roughness scaling of the Greenwood-Williamson layer and `emb_depth` defaults.
- K_B/K_P/K_1/K_2/C_1/C_2 can seed the MSD contact-layer element (Layer 2 contact
  stiffness + viscous damper) directly.
