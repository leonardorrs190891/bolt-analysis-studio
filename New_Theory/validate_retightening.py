"""Validacao da renovacao de embedding no re-aperto (spec/plan 2026-07-07).

Reproduz o protocolo Liu2022 (Structures, M12, transverso disp 0.3mm 12.5Hz,
T=80 Nm): apertar -> 5000 ciclos -> retighten x3 (fig6a/6b/7a: t0..t3), para DRY
e OIL, com UMA fisica (constantes congeladas do Estagio A) diferindo SO por mu.
NAO adota nada; e validacao falsify-first.

mu de cada lube e DERIVADO do F0 de primeiro aperto medido (Motosh, D=0) -> a
recuperacao prevista fica auto-consistente (com k_dmg_mu=0, plana em F0_first).

Metrica de afrouxamento: cada fase normalizada no PROPRIO inicio, isolando a FORMA
do decaimento da RECUPERACAO pos-aperto (o offset de recuperacao = G4). Gate G2
checa a aceleracao nas fases de RE-APERTO (t1..t3; t0 = primeiro aperto).

Run:  python New_Theory/validate_retightening.py [--quick]
"""
from __future__ import annotations
import json
import sys
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "New_Theory"))
from bolt_analysis_studio.numerical.dynamic_stiffness_analyzer import (  # noqa: E402
    DynamicStiffnessAnalyzer, JointMaterial, THREAD_FLANK_ANGLE)
from library_common import (  # noqa: E402
    frozen_constants, geometry_for, emb_depth_vdi, load_full_curve)

DIG = "Models/CALIBRATION_AND_VALIDATION/curve_library/digitized_csv"
N_PHASE = 5000
N_RETIGHT = 3            # fig6a/6b/7a: t0 (1o aperto) + t1..t3 (3 re-apertos)
FREQ = 12.5
DELTA = 0.3e-3
F_AMP = 5000.0          # forca transversa (variante load-controlled 5 kN), prov=paper
TORQUE = 80.0           # N.m
GRIP_MM = 50.0          # 2 placas + celula de carga 20mm; prov=assumed (sens.)

# Achieved first-tightening F0 (N), medido no paper (prov=paper); mu DERIVADO dele.
COND = {
    "dry_release": dict(F0_first=20.6e3, grp="liu2022_fig6a_dry_release"),
    "oil_release": dict(F0_first=27.0e3, grp="liu2022_fig6b_oil_release"),
    "oil_direct":  dict(F0_first=27.0e3, grp="liu2022_fig7a_oil_direct"),
}


def _mu_from_first_tightening(F0_first, geom, torque=TORQUE):
    """mu (=mu_thread=mu_bearing) implicado por torque + F0_first (Motosh, D=0):
        torque = F0*(lead + mu*(d2/(2cos a) + r_bearing))."""
    lead = geom.lead_per_radian
    fric_arm = geom.d_2 / (2.0 * np.cos(THREAD_FLANK_ANGLE)) + geom.r_bearing
    return max((torque / F0_first - lead) / fric_arm, 0.0)


def run_sequence(F0_first, k_emb_renew, consts, geom, emb_m, cap=None):
    n_phase = cap or N_PHASE
    mu = _mu_from_first_tightening(F0_first, geom)
    mat = JointMaterial(mu_thread=mu, mu_bearing=mu, emb_depth=emb_m,
                        k_emb_renew=k_emb_renew, **consts)
    ana = DynamicStiffnessAnalyzer(geom, mat, F0_first)
    phases = []
    for t in range(N_RETIGHT + 1):
        rf = [max(ana.state.F_0, 0.0) / F0_first]
        for _ in range(n_phase):
            ana.step_cycle(F_AMP, np.pi / 2.0, FREQ, delta_amp=DELTA)
            rf.append(max(ana.state.F_0, 0.0) / F0_first)
        phases.append(np.array(rf))
        if t < N_RETIGHT:
            ana.retighten(applied_torque=TORQUE)     # preve recuperacao (plana em k_dmg_mu=0)
    return mu, phases


def _decay_mae(sim_rf, csv):
    """MAE da FORMA do afrouxamento (cada fase normalizada no proprio inicio)."""
    cyc_d, r_d = load_full_curve(csv)
    keep = cyc_d <= (len(sim_rf) - 1)
    cyc_d, r_d = cyc_d[keep], r_d[keep]
    if len(cyc_d) < 2:
        return float("nan")
    sim_loc = sim_rf / max(sim_rf[0], 1e-9)
    r_d_loc = r_d / max(r_d[0], 1e-9)
    pred = np.interp(cyc_d, np.arange(len(sim_loc)), sim_loc)
    return float(np.mean(np.abs(pred - r_d_loc)))


def _sim_phase_loss(phases):
    return [float(1.0 - p[-1] / max(p[0], 1e-9)) for p in phases]


def _data_series(grp, which):
    vals = []
    for t in range(N_RETIGHT + 1):
        _, r_d = load_full_curve(f"{DIG}/{grp}_t{t}.csv")
        vals.append(float(1.0 - r_d[-1] / max(r_d[0], 1e-9)) if which == "loss"
                    else float(r_d[0]))
    return vals


def _decay_maes(grp, phases):
    return [_decay_mae(phases[t], f"{DIG}/{grp}_t{t}.csv")
            for t in range(N_RETIGHT + 1)]


def evaluate(consts, geom, emb_m, cap=None):
    out = {}
    dry = COND["dry_release"]
    best = None
    for k in [0.0, 0.25, 0.5, 1.0, 2.0]:
        _, phases = run_sequence(dry["F0_first"], k, consts, geom, emb_m, cap)
        maes = _decay_maes(dry["grp"], phases)
        med = float(np.nanmedian(maes))
        if best is None or med < best["med"]:
            best = dict(k=k, med=med, maes=maes, phases=phases)
    out["dry_release"] = best
    # G5 parsimony: freeing k_emb_renew beats k=0 (wear-amp alone) by > tol?
    _, ph0 = run_sequence(dry["F0_first"], 0.0, consts, geom, emb_m, cap)
    med0 = float(np.nanmedian(_decay_maes(dry["grp"], ph0)))
    out["G5_med_k0"] = med0
    out["G5_renewal_justified"] = bool(med0 - best["med"] > 0.005)
    # OIL: PREDICT with the dry-fit k_emb_renew (zero-refit transfer).
    for name in ("oil_release", "oil_direct"):
        c = COND[name]
        _, phases = run_sequence(c["F0_first"], best["k"], consts, geom, emb_m, cap)
        out[name] = dict(k=best["k"], maes=_decay_maes(c["grp"], phases),
                         phases=phases)
    return out


def _monotone_incr(xs):
    return all(xs[i] <= xs[i + 1] + 1e-9 for i in range(len(xs) - 1))


def main():
    quick = "--quick" in sys.argv
    cap = 500 if quick else None
    consts, _ = frozen_constants(include_damage=True)
    emb_m, _ = emb_depth_vdi("Rz<10", 2)     # M12 fino, 2 interfaces internas; prov=handbook
    geom = geometry_for("M12x1.75", GRIP_MM)
    for name, c in COND.items():
        print(f"{name}: F0_first={c['F0_first']/1e3:.1f}kN -> "
              f"mu={_mu_from_first_tightening(c['F0_first'], geom):.3f}")
    res = evaluate(consts, geom, emb_m, cap)

    dry = res["dry_release"]
    sim_loss = _sim_phase_loss(dry["phases"])
    data_loss = _data_series(COND["dry_release"]["grp"], "loss")
    data_rec = _data_series(COND["dry_release"]["grp"], "recovery")
    print(f"\nDRY k_emb_renew*={dry['k']} decay-MAE/tN={[round(m,3) for m in dry['maes']]} "
          f"med={dry['med']:.3f} (k=0 med={res['G5_med_k0']:.3f})")
    print(f"  sim  per-phase loss t0..t3={[round(x,3) for x in sim_loss]}")
    print(f"  data per-phase loss t0..t3={[round(x,3) for x in data_loss]}")
    print(f"  data recovery t0..t3={[round(x,3) for x in data_rec]}  (sim recovery = flat ~1.0)")
    for name in ("oil_release", "oil_direct"):
        print(f"{name:12s} decay-MAE/tN={[round(m,3) for m in res[name]['maes']]}")

    # ---- Gates (pre-registered, spec 5) ----
    oil = res["oil_release"]
    g1 = float(np.nanmedian(oil["maes"])) < 0.05
    # G2/G3 sobre as fases de RE-APERTO (t1..t3); t0 = 1o aperto (assentamento fresco).
    d_ret, s_ret = data_loss[1:], sim_loss[1:]
    g2 = (_monotone_incr(d_ret) and _monotone_incr(s_ret)
          and all(sl <= 2 * dl + 1e-9 and dl <= 2 * sl + 1e-9
                  for sl, dl in zip(s_ret, d_ret) if dl > 1e-6))
    g3 = (float(np.nanmedian(dry["maes"])) < 0.05) or _monotone_incr(s_ret)
    g5 = res["G5_renewal_justified"]
    print(f"\nGATES: G1(oil decay MAE<0.05)={g1}  G2(dry accel t1..t3 model~data)={g2}  "
          f"G3(dry loosening shape)={g3}  G5(renewal justified +>0.005)={g5}")
    print(f"G4(recovery): frozen k_dmg_mu=0 => sim recovery FLAT ~1.0 each retighten; "
          f"data dry recovery {[round(x,3) for x in data_rec]} DECLINES => documented "
          "finding (missing galling/geometric term, spec 7), NOT a gate.")
    if quick:
        print("--quick: smoke only, nao grava artefatos.")
        return
    payload = dict(
        dry=dict(k=dry["k"], decay_mae=dry["maes"], med=dry["med"],
                 sim_loss=sim_loss, data_loss=data_loss, data_recovery=data_rec),
        oil_release=dict(decay_mae=res["oil_release"]["maes"]),
        oil_direct=dict(decay_mae=res["oil_direct"]["maes"]),
        gates=dict(G1=bool(g1), G2=bool(g2), G3=bool(g3), G5=bool(g5),
                   G5_med_k0=res["G5_med_k0"]))
    (ROOT / "New_Theory" / "retightening_results.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print("Artefato: New_Theory/retightening_results.json")


if __name__ == "__main__":
    main()
