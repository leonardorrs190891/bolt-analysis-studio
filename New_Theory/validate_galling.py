"""Validacao do galling (declinio da recuperacao no re-aperto) no nivel M12 NAO-colapsante
(spec 2026-07-07 §4.10 G4). Prerequisito §5.1 resolvido pelo liu2022_level_probe.py:
nivel per-rig = emb Rz<4 + k_wear_scale_tr~0.06 + dano brando.

Testa se, sobre esse baseline, o galling (k_gall) reproduz o DECLINIO da recuperacao dry
E mantem o oil PLANO. Achado (2026-07-07): o contraste dry-vs-oil NAO e' uma forma faltante
— e' `c_D` PER-LUBE (o filme de oleo suprime o crescimento do dano ~15x: dry c_D~0.5, oil
c_D~0.03). Com c_D per-lube + o MESMO k_gall, dry declina e oil fica plano (§8: forma
transfere, c_D e' per-lube como mu).

Run: python New_Theory/validate_galling.py
"""
from __future__ import annotations
import sys
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "New_Theory"))
from bolt_analysis_studio.numerical.dynamic_stiffness_analyzer import (  # noqa: E402
    DynamicStiffnessAnalyzer, JointMaterial)
from library_common import geometry_for, emb_depth_vdi, load_full_curve  # noqa: E402

DIG = "Models/CALIBRATION_AND_VALIDATION/curve_library/digitized_csv"
N_PHASE, N_RETIGHT, FREQ, DELTA, F_AMP, TORQUE, GRIP = 5000, 3, 12.5, 0.3e-3, 5000.0, 80.0, 50.0
# Nivel M12 nao-colapsante (liu2022_level_probe), SEM c_D (agora per-lube em COND):
LEVEL = dict(emb_depth=emb_depth_vdi("Rz<4", 2)[0], k_wear_scale_tr=0.06,
             k_dmg_wear=1.0, W_ref=1.0e4, C_creep=1.8667e-11,
             conform_driver="effective", W_conf_ref=7671.0,
             conform_pressure_exp=2.0, p_ref_conform=5.0e8)
# c_D per-lube: oleo protege as superficies (crescimento de dano ~15x menor).
COND = {"dry": dict(mu=0.236, F0=20.6e3, c_D=0.50, grp="liu2022_fig6a_dry_release"),
        "oil": dict(mu=0.176, F0=27.0e3, c_D=0.03, grp="liu2022_fig6b_oil_release")}


def run(cond, k_gall):
    geom = geometry_for("M12x1.75", GRIP)
    mat = JointMaterial(mu_thread=cond["mu"], mu_bearing=cond["mu"],
                        k_gall=k_gall, c_D=cond["c_D"], **LEVEL)
    ana = DynamicStiffnessAnalyzer(geom, mat, cond["F0"])
    starts = [1.0]
    for t in range(N_RETIGHT + 1):
        for _ in range(N_PHASE):
            ana.step_cycle(F_AMP, np.pi / 2, FREQ, delta_amp=DELTA)
        if t < N_RETIGHT:
            ana.retighten(applied_torque=TORQUE)
            starts.append(float(max(ana.state.F_0, 0.0) / cond["F0"]))
    return starts, float(ana.state.D)


def data_recovery(grp):
    return [float(load_full_curve(f"{DIG}/{grp}_t{t}.csv")[1][0]) for t in range(N_RETIGHT + 1)]


def _mae(a, b):
    return float(np.mean(np.abs(np.array(a) - np.array(b))))


def main():
    dry_data, oil_data = data_recovery(COND["dry"]["grp"]), data_recovery(COND["oil"]["grp"])
    print(f"emb Rz<4={LEVEL['emb_depth']*1e6:.1f}um k_wear_tr={LEVEL['k_wear_scale_tr']} "
          f"c_D per-lube: dry={COND['dry']['c_D']} oil={COND['oil']['c_D']}")
    print(f"data dry recovery = {[round(x,3) for x in dry_data]}")
    print(f"data oil recovery = {[round(x,3) for x in oil_data]}\n")
    best = None
    for k in [0.0, 1.0, 2.0, 3.0, 5.0]:
        starts, Dend = run(COND["dry"], k)
        mae = _mae(starts, dry_data)
        print(f"  dry k_gall={k:4.1f} recovery={[round(x,3) for x in starts]} MAE={mae:.3f} D={Dend:.2f}")
        if best is None or mae < best["mae"]:
            best = dict(k=k, mae=mae, starts=starts)
    mae_k0 = _mae(run(COND["dry"], 0.0)[0], dry_data)
    oil_starts, oil_D = run(COND["oil"], best["k"])
    print(f"\nBEST dry k_gall={best['k']} MAE={best['mae']:.3f} (k=0 MAE={mae_k0:.3f})")
    print(f"OIL (same k_gall={best['k']}, c_D={COND['oil']['c_D']}): "
          f"recovery={[round(x,3) for x in oil_starts]} D_end={oil_D:.2f}")

    ds = best["starts"]
    g4 = all(ds[i] >= ds[i + 1] - 1e-9 for i in range(len(ds) - 1)) and best["mae"] < 0.05
    g_sign = all(x >= 0.95 for x in oil_starts[1:])
    g_pars = (mae_k0 - best["mae"]) > 0.005
    print(f"\nGATES: G4'(dry declines, MAE<0.05)={g4}  G-sign(oil flat >=0.95)={g_sign}  "
          f"G-parsimony(k_gall +>0.005)={g_pars}")
    print("Contraste dry-vs-oil = c_D PER-LUBE (nao forma faltante); §8: forma transfere, c_D per-lube.")


if __name__ == "__main__":
    main()
