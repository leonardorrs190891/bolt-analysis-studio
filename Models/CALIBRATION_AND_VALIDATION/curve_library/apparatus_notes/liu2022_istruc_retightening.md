# Z. Liu 2022 (Structures) — retightening (reaperto) after loosening, M12

**Citation:** Z. Liu et al., "The effect of tightening again on bolt loosening under
transverse load: Experimental and finite element analysis", *Structures* 44 (2022) 1303–1311.
**DOI:** [10.1016/j.istruc.2022.08.049](https://doi.org/10.1016/j.istruc.2022.08.049) (paywall; institutional copy)
**PDF:** `pdfs_manual_download/liu2022_istruc_retightening.pdf` (= `BAS_V2_papers/D. Rodada 3.../The effect of tightening again...pdf`)

## Apparatus (MSD-block data)

- Transverse-vibration rig per **GB/T 10431-2008**, sine wave, **12.5 Hz**,
  **displacement-controlled 0.3 mm** (main experiments) or load-controlled 5 kN;
  measured plate relative displacement ~0.2 mm at high clamp force (hysteresis Fig 3).
- Clamp force via **washer-type compression load cell** (20 mm thick, 60 kN capacity)
  in the stack — add 20 mm to the clamp package when building the MSD model.
- Two clamped plates, **45 carbon steel** (E = 209 GPa, ν = 0.269), equal thickness.
- Preload by torque control: **T = 80 N·m → F0 ≈ 26 kN nominal** (achieved 19.78–21.50 kN
  dry, 26.00–28.18 kN oiled — friction scatter; recommended-preload range 27.5–34.5 kN).
- Retightening protocols: (i) directly to target torque; (ii) **release 30°–60° then
  retighten to target torque** (paper's recommended method).

## Specimen (MSD-block data)

- **M12 × 1.75, class 8.8** bolt + nut, material **35CrMn** (E = 213 GPa, ν = 0.286),
  σ_s = 640 MPa, A_s = 84.3 mm². Thread/bearing μ ≈ 0.2 assumed (dry); oil lubrication
  variant. Fatigue fracture (4th retightening) at first engaged thread near bearing surface.

## Trial matrix / digitized curves (21 CSVs, R_F normalized to FIRST-tightening F0)

| CSV group | Condition | Curves |
|---|---|---|
| liu2022_fig5_{dry/oil}_F*.csv | first tightening, 2 lube × 2 achieved-F0 | 4 |
| liu2022_fig6a_dry_release_t0..t3.csv | dry, release-angle retightening (t0=first, tN=Nth retight) | 4 |
| liu2022_fig6b_oil_release_t0..t3.csv | oil, release-angle retightening — **restores ~100% F0** | 4 |
| liu2022_fig7a_oil_direct_t0..t3.csv | oil, retightened directly to torque — restores only ~88–90% | 4 |
| liu2022_fig8_multi_t0..t4.csv | dry, multiple retightenings; **t4 = fatigue fracture at ~1,500 cyc** | 5 |

## Digitization caveats

- All 5,000-cycle runs; marker-line reading, error ±0.5% R_F.
- Retightening curves start at their post-retightening R_F (can exceed 100% with oil);
  cycle counter restarts at each retightening.
- Fig 7(b) duplicates Fig 6(b) (comparison panel) — digitized once as fig6b.
- fig8_multi_t4 ends at the fracture dive (~78% at 1,500 cycles), not a loosening endpoint.

## V2 calibration mapping

- **PRIMARY reaperto/embedding-renewal target (project priority #5)**: sequential
  retightening curves show whether δ_emb should reset on retighten. Dry: each retighten
  recovers less and loosens faster (surface damage D accumulates, μ degrades). Oil:
  release-angle retightening fully restores F0 (oil film protects surfaces → D stays low)
  — direct evidence for D modulating friction (k_dmg_mu) and for `D` persisting across
  retightenings while δ_emb partially renews.
- Fig 8 t3→t4 acceleration = the reaperto/TP7 collapse analogue at M12; note t4 is
  fatigue-driven (out-of-model, trim).
- Fig 5 lube/preload family: cross-check of `k_emb_scale` (stage-I drop 8%/500 cyc)
  and μ sensitivity.
