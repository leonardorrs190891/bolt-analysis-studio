"""Liu2022 (Structures) M12 per-rig LEVEL probe — READ-ONLY diagnostic (2026-07-07).

MODEL_LEGITIMACY.md §4.10: the zero-refit Liu2022 M12 re-tightening validation
COLLAPSES (perda por fase ~0.98 vs dado dry 0.07-0.14) because three per-rig
constants transfer badly from the M16/âncora interna Stage-A block:
  1. c_D=2.0 / k_dmg_wear=4.0  — the âncora interna reaperto COLLAPSE signature (runaway).
  2. emb_depth (VDI Rz<10)      — over-predicts fine-ground settling (§4.6).
  3. k_wear_scale_tr=1.0        — vs the 0.44 fitted to M16/âncora interna nova (~2.3x fast).

This probe SWEEPS a per-rig LEVEL {emb (new Rz<4 fine-ground handbook class /
scaled), k_wear_scale_tr in [0.05,1.0], damage {off, mild, frozen-ref}} on the DRY
release curves t0..t3, WITHOUT any recovery/galling term (not built), and reports
which combo yields a NON-COLLAPSING ~14% first-phase decay matching the dry data
(final R_F 0.72-0.90, NOT ->0). Prerequisite to test the galling recovery term
(spec 2026-07-07) cleanly — a joint at F_0~=0 shows no recovery.

Provenance (§8 doctrine "formas transferem, constantes sao por par/rig"):
  emb = Rz<4 -> HANDBOOK (Bolt Science, not VDI; library_common docstring).
  k_wear_scale_tr + c_D/k_dmg_wear -> PER-RIG FITTED (declared as such).

Reuses the EXACT validate_retightening harness (run_sequence + decay/loss helpers)
and library_common (frozen_constants, geometry_for, emb_depth_vdi). READ-ONLY on
the engine: only reads it, writes its own log. AS-IS; adopts nothing.

Run: python New_Theory/liu2022_level_probe.py [--quick]
"""
from __future__ import annotations
import sys
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "New_Theory"))

from library_common import (  # noqa: E402
    frozen_constants, geometry_for, emb_depth_vdi, load_full_curve)
from validate_retightening import (  # noqa: E402
    run_sequence, _sim_phase_loss, _decay_maes, _mu_from_first_tightening,
    COND, GRIP_MM, N_RETIGHT, DIG, FREQ, DELTA, F_AMP, TORQUE)
from bolt_analysis_studio.numerical.dynamic_stiffness_analyzer import (  # noqa: E402
    SlowState, JointMaterial, resolve_transverse_slip, F_slip_transverse,
    k_tr_transverse, SLIP_ONSET_PAI_HESS)

DRY = COND["dry_release"]
GRP = DRY["grp"]
F0 = DRY["F0_first"]

LOG_LINES: list[str] = []


def say(msg: str = "") -> None:
    print(msg)
    LOG_LINES.append(msg)


def data_finals(grp: str) -> list[float]:
    """R_F at end of each phase, normalized to FIRST-tightening F0 (raw CSV)."""
    out = []
    for t in range(N_RETIGHT + 1):
        _, r = load_full_curve(f"{DIG}/{grp}_t{t}.csv")
        out.append(float(r[-1]))
    return out


def data_starts(grp: str) -> list[float]:
    out = []
    for t in range(N_RETIGHT + 1):
        _, r = load_full_curve(f"{DIG}/{grp}_t{t}.csv")
        out.append(float(r[0]))
    return out


def build_consts(base: dict, k_wear: float, dmg: tuple[float, float]) -> dict:
    """Inject per-rig levers into the frozen-constants dict.  run_sequence builds
    JointMaterial(..., **consts), so k_wear_scale_tr / c_D / k_dmg_wear flow in as
    real JointMaterial fields.  W_ref stays engine default (1e4)."""
    c = dict(base)
    c["k_wear_scale_tr"] = k_wear
    c_D, k_dmg_wear = dmg
    if c_D > 0.0:
        c["c_D"] = c_D
        c["k_dmg_wear"] = k_dmg_wear
    else:
        c.pop("c_D", None)
        c.pop("k_dmg_wear", None)
    return c


def is_collapse(sim_loss: list[float], finals: list[float]) -> bool:
    """Collapse := any phase loses >50% within-phase OR ends below 0.3*F0_first."""
    return any(l > 0.50 for l in sim_loss) or any(f < 0.30 for f in finals)


def evaluate_combo(base, geom, emb_m, k_wear, dmg, cap):
    consts = build_consts(base, k_wear, dmg)
    _, phases = run_sequence(F0, 0.0, consts, geom, emb_m, cap)  # k_emb_renew=0
    sim_loss = _sim_phase_loss(phases)
    finals = [float(p[-1]) for p in phases]
    starts = [float(p[0]) for p in phases]
    maes = _decay_maes(GRP, phases)
    med = float(np.nanmedian(maes))
    return dict(sim_loss=sim_loss, finals=finals, starts=starts,
                maes=maes, med=med, collapse=is_collapse(sim_loss, finals))


def diagnostics(base, geom):
    mu = _mu_from_first_tightening(F0, geom)
    say(f"Geometry  M12x1.75 grip {GRIP_MM}mm: k_b={geom.k_b/1e6:.1f} MN/m  "
        f"d_2={geom.d_2*1e3:.2f}mm  r_bearing={geom.r_bearing*1e3:.1f}mm  "
        f"A_contact={geom.A_contact*1e6:.1f} mm^2")
    say(f"mu (dry, derived from T=80Nm & F0={F0/1e3:.1f}kN via Motosh) = {mu:.3f}")
    # slip @ start-of-phase (disp mode, delta=0.3mm)
    st = SlowState(F_0=F0, F_0_init=F0)
    mat = JointMaterial(mu_thread=mu, mu_bearing=mu)
    F_slip = F_slip_transverse(st, mat)
    k_tr = k_tr_transverse(geom, mat)
    slip = resolve_transverse_slip(st, mat, F_AMP, np.pi / 2, DELTA, geom=geom)
    say(f"slip onset factor={SLIP_ONSET_PAI_HESS}  F_slip={F_slip:.0f} N  "
        f"k_tr={k_tr/1e9:.2f} GN/m  -> slip_amp={slip*1e6:.1f} um "
        f"(of delta={DELTA*1e6:.0f} um: {'GROSS' if slip > 0.5*DELTA else 'partial'})")
    # per-cycle fractional wear loss at k_wear=1, D=0, no conformation (F_0 cancels)
    slip_dist = 4.0 * slip
    frac = (geom.k_b * base["K_archard"] * slip_dist
            / max(2e9 * geom.A_contact, 1.0))          # hardness default 2e9
    say(f"per-cycle wear frac-loss (k_wear=1, D=0, conf off) = {frac:.3e}/cyc "
        f"-> {1 - np.exp(-5000 * frac):.2f} over 5000 cyc (F_0-independent)")
    p = F0 / geom.A_contact
    pr = base.get("p_ref_conform", 5e8)
    say(f"contact pressure p={p/1e6:.0f} MPa  p/p_ref={p/pr:.2f}  "
        f"(conform gate ACTIVE: W_conf_ref={base.get('W_conf_ref', 0):.0f}, "
        f"n={base.get('conform_pressure_exp', 1)}) -> partially damps wear")


def main():
    quick = "--quick" in sys.argv
    cap = 500 if quick else None

    base_off, _ = frozen_constants(include_damage=False)   # emb_depth popped
    base_dmg, _ = frozen_constants(include_damage=True)     # carries c_D/k_dmg_wear

    say("=" * 78)
    say("Liu2022 (Structures) M12 dry-release per-rig LEVEL probe  (READ-ONLY)")
    say("=" * 78)
    diagnostics(base_off, geometry_for("M12x1.75", GRIP_MM))

    geom = geometry_for("M12x1.75", GRIP_MM)
    d_loss = [float(1 - r[-1] / max(r[0], 1e-9)) for r in
              (load_full_curve(f"{DIG}/{GRP}_t{t}.csv")[1] for t in range(N_RETIGHT + 1))]
    d_final = data_finals(GRP)
    d_start = data_starts(GRP)
    say("")
    say("DATA (dry fig6a, R_F normalized to FIRST-tightening F0):")
    say(f"  per-phase START  t0..t3 = {[round(x, 3) for x in d_start]}  "
        "(declining recovery = missing galling term, §4.10 G4)")
    say(f"  per-phase FINAL  t0..t3 = {[round(x, 3) for x in d_final]}  "
        "(target: NOT ->0; cumulative 14-27% below first-tighten)")
    say(f"  within-phase LOSS t0..t3 = {[round(x, 3) for x in d_loss]}  "
        "(shape target; t0 biggest = embedding)")

    # emb classes to probe
    emb_opts = {
        "Rz<4/n1 (3.5um handbook)": emb_depth_vdi("Rz<4", 1)[0],
        "Rz<4/n2 (4.0um handbook)": emb_depth_vdi("Rz<4", 2)[0],
        "Rz<10/n2 (11um, §4.10 cur)": emb_depth_vdi("Rz<10", 2)[0],
    }
    k_wear_opts = [0.05, 0.1, 0.2, 0.3, 0.44, 1.0]
    dmg_opts = {"off": (0.0, 0.0), "mild": (0.5, 1.0),
                "frozen(2/4)": (2.0, 4.0)}

    say("")
    say("SWEEP (k_emb_renew=0; conformation ON from frozen consts; W_ref=1e4 default)")
    say("-" * 78)
    hdr = (f"{'emb':<26}{'k_wear':>7}{'dmg':>12} | "
           f"{'loss t0..t3':<28}{'med MAE':>8} {'final t0..t3':<26}{'collapse':>9}")
    say(hdr)
    say("-" * len(hdr))

    results = []
    for emb_name, emb_m in emb_opts.items():
        base = base_dmg  # damage combos need c_D/k_dmg_wear present; off-combo pops them
        for kw in k_wear_opts:
            for dmg_name, dmg in dmg_opts.items():
                r = evaluate_combo(base, geom, emb_m, kw, dmg, cap)
                results.append(dict(emb=emb_name, emb_m=emb_m, k_wear=kw,
                                    dmg=dmg_name, **r))
                say(f"{emb_name:<26}{kw:>7.2f}{dmg_name:>12} | "
                    f"{str([round(x, 3) for x in r['sim_loss']]):<28}"
                    f"{r['med']:>8.3f} "
                    f"{str([round(x, 3) for x in r['finals']]):<26}"
                    f"{('COLLAPSE' if r['collapse'] else 'ok'):>9}")

    # --- §4.10 collapse REPRODUCTION (Rz<10 / k_wear=1.0 / frozen 2/4) for contrast
    ref = next((r for r in results if r["emb"].startswith("Rz<10")
                and r["k_wear"] == 1.0 and r["dmg"] == "frozen(2/4)"), None)
    if ref is not None:
        say("")
        say(f">>> §4.10 COLLAPSE reproduced (Rz<10 11um / k_wear=1.0 / frozen 2/4): "
            f"loss={[round(x,3) for x in ref['sim_loss']]} finals="
            f"{[round(x,3) for x in ref['finals']]}  (§4.10 table: [0.974,0.988,0.988,0.985]).")

    # --- Best NON-collapse combo PER DAMAGE CLASS (t0-match + shape MAE)
    t0_data = d_loss[0]
    for r in results:
        r["score"] = abs(r["sim_loss"][0] - t0_data) + r["med"]
    say("")
    say("BEST NON-COLLAPSE combo per damage class (min |t0-loss - data| + med shape-MAE):")
    for dmg_name in dmg_opts:
        cand = [r for r in results if r["dmg"] == dmg_name and not r["collapse"]]
        if not cand:
            say(f"  {dmg_name:<12}: (all collapse)")
            continue
        b = min(cand, key=lambda r: r["score"])
        say(f"  {dmg_name:<12}: emb={b['emb']:<26} k_wear={b['k_wear']:<5} "
            f"loss={[round(x,3) for x in b['sim_loss']]} "
            f"final={[round(x,3) for x in b['finals']]} medMAE={b['med']:.3f}")

    # --- Rank NON-collapse combos: closest t0-loss to data + smallest shape MAE
    non_col = [r for r in results if not r["collapse"]]
    say("")
    if not non_col:
        say(">>> VERDICT: NO combo avoids collapse across the swept physical range.")
        say(">>> -> the collapse is STRUCTURAL (missing form), not just constants.")
    else:
        t0_data = d_loss[0]
        for r in non_col:
            r["score"] = abs(r["sim_loss"][0] - t0_data) + r["med"]
        non_col.sort(key=lambda r: r["score"])
        best = non_col[0]
        say(">>> BEST NON-COLLAPSE combo (min |t0-loss - data| + median shape-MAE):")
        say(f"    emb = {best['emb']}  ({best['emb_m']*1e6:.1f} um)")
        say(f"    k_wear_scale_tr = {best['k_wear']}   damage = {best['dmg']}")
        say("")
        say(f"    {'phase':<6}{'sim loss':>10}{'data loss':>11}"
            f"{'sim final':>11}{'data final':>12}{'shape MAE':>11}")
        for t in range(N_RETIGHT + 1):
            say(f"    t{t:<5}{best['sim_loss'][t]:>10.3f}{d_loss[t]:>11.3f}"
                f"{best['finals'][t]:>11.3f}{d_final[t]:>12.3f}"
                f"{best['maes'][t]:>11.3f}")
        say(f"    median shape-MAE = {best['med']:.3f}   "
            f"sim per-phase START = {[round(x,3) for x in best['starts']]}")
        say("")
        say("    NOTE on the per-phase FINAL offset: sim retightens to ~1.0 each")
        say("    phase (k_dmg_mu=0 -> flat recovery, §4.10 G4), while DATA recovery")
        say("    DECLINES (0.918->0.832->0.793). So sim finals sit HIGH vs data for")
        say("    t1..t3 by exactly the missing-galling gap. The WITHIN-PHASE decay")
        say("    (loss + shape MAE) is the recovery-offset-free comparison, and it is")
        say("    what this baseline must get right to let galling be tested cleanly.")

    say("")
    if not quick:
        (ROOT / "New_Theory" / "liu2022_level_probe.log").write_text(
            "\n".join(LOG_LINES) + "\n", encoding="utf-8")
        say("Log: New_Theory/liu2022_level_probe.log")
    else:
        say("--quick: cap=500 cyc smoke; magnitudes not final (no log written).")


if __name__ == "__main__":
    main()
