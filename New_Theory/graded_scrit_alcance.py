"""SONDA DE ALCANCE do `graded_scrit` — a capacidade que já existe no engine.

Atividade B pré-pipeline (2026-07-29). PROBE, não adoção: nada é escrito no store
nem no `adopted_configs.json`.

Por que esta capacidade e por que agora. O engine tem, default-inerte desde a
spec §4.37, uma taxa de afrouxamento GRADUADA:
    loose_rate_mode="graded_scrit" + s_crit_loose [m] + k_loose_graded
    d_theta = gates · k_loose_graded · max(0, slip − s_crit_loose) / (d_2/2)
A promessa registrada dela inclui **"colapso quase-LINEAR"** (Karlsen §4.35,
"near-linear catastrophic back-off") e ausência de runaway.

Isso casa com o achado da atividade A: o cluster **DERIVA** (10 curvas, R² ≥ 0,7)
tem resíduo em RAMPA — nas 4 do CHU_2026 com β ≈ +0,58 e R² ≈ 0,82, ou seja o
modelo termina muito acima do dado porque o colapso medido não acontece. Uma taxa
que produz colapso quase-linear é a candidata natural.

A pergunta é de ALCANCE, não de ajuste: **existe algum par (s_crit, k) que traga o
σ_res daquelas curvas abaixo do limite sem estourar MAE nem res.máx?** Se não
existir em 3 décadas de k, a capacidade não resolve e o pipeline não deve gastar
prereg com ela.

Alvos, dois grupos com propósitos diferentes:
 · CHU_2026 ×4 — o cluster DERIVA, cuja assinatura casa com a promessa;
 · YANG_2019 / YANG_2023_IJPEM — os alvos para os quais a capacidade foi
   ORIGINALMENTE proposta (candidato "limiar graduado"), que a atividade A
   classificou como ONDULADO/mista. Servem de controle: se a capacidade só
   funcionar onde a assinatura casa, isso é evidência de que a assinatura prediz.

`s_crit_loose` tem procedência (Bauer 76–108 µm, curva amplitude-vs-vida);
`k_loose_graded` NÃO tem — por isso ele é varrido por décadas, e qualquer valor
que "funcione" seria constante sem procedência, o que a adoção teria de resolver
depois. Aqui só se pergunta se a capacidade ALCANÇA.

Run: py -3.12 New_Theory/graded_scrit_alcance.py [--quick]   (~10-20 min)
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bolt_analysis_studio.validation import report_html as rh  # noqa
from bolt_analysis_studio.validation import runner as rn  # noqa
from bolt_analysis_studio.validation.case_registry import record  # noqa

QUICK = "--quick" in sys.argv
CAP = 100_000
OUT = ROOT / "New_Theory" / "graded_scrit_alcance.json"

ALVOS = {
    "DERIVA (assinatura casa)": [
        "chu2026ti_D0p4mm_F0_49kN_test2",
        "chu2026ti_D0p4mm_F0_61kN_test7",
        "chu2026ti_D0p4mm_F0_73kN_test8",
        "chu2026ti_D0p7mm_F0_49kN_test4",
    ],
    "alvo original (ONDULADO/mista)": [
        "yang2019_M10_amp0p4_5Hz",
        "10_Yang_2023_phenomenological_model__0_50_mm__9",
    ],
}
S_CRIT = [50e-6, 100e-6, 200e-6]        # m — banda de procedência Bauer 76-108 um
K_GRAD = [1e-4, 1e-3, 1e-2, 1e-1]       # sem procedência: varrido por décadas
if QUICK:
    ALVOS = {"DERIVA (assinatura casa)": ALVOS["DERIVA (assinatura casa)"][:1]}
    S_CRIT, K_GRAD = S_CRIT[:1], K_GRAD[:2]

_EXTRA: dict = {}
_orig = rn._effective_overrides


def _patched(rec, base):
    ov = dict(_orig(rec, base))
    ov.update(_EXTRA)
    return ov


rn._effective_overrides = _patched


def med(cid):
    r = rn.simulate_case(record(cid), n_cap=CAP)
    if not r.ok or r.mae is None or r.resid_std is None:
        return None
    mp, md, mx = r.metric_pred, r.metric_data, r.metric_x
    beta = 0.0
    if mp and md and mx and len(mp) == len(md) == len(mx) >= 3:
        e = np.asarray(mp, float) - np.asarray(md, float)
        x = np.asarray(mx, float)
        s = (x - x[0]) / (x[-1] - x[0]) if x[-1] > x[0] else np.linspace(0, 1, len(x))
        beta = float(np.polyfit(s, e, 1)[0])
    return dict(mae=float(r.mae), mx=float(r.maxerr), sd=float(r.resid_std),
                beta=beta)


def ok3(v):
    return (v["mx"] <= rh.META_MAX and v["mae"] <= rh.META_MAE
            and v["sd"] <= rh.META_SRES)


saida = []
for grupo, cids in ALVOS.items():
    print(f"\n{'=' * 74}\n{grupo}\n{'=' * 74}")
    for cid in cids:
        _EXTRA.clear()
        base = med(cid)
        if base is None:
            print(f"  {cid}: NÃO SIMULÁVEL")
            continue
        print(f"\n  {cid}")
        print(f"    nominal            MAE {base['mae']:.4f} max {base['mx']:.4f} "
              f"σ {base['sd']:.4f} β {base['beta']:+.3f}")
        melhor, linhas = None, []
        for sc in S_CRIT:
            for k in K_GRAD:
                _EXTRA.clear()
                _EXTRA.update(loose_rate_mode="graded_scrit",
                              s_crit_loose=sc, k_loose_graded=k)
                try:
                    v = med(cid)
                except Exception as exc:                       # noqa: BLE001
                    print(f"    s_crit {sc*1e6:5.0f}um k {k:<7g} ERRO "
                          f"{type(exc).__name__}")
                    continue
                if v is None:
                    continue
                linhas.append(dict(s_crit_um=sc * 1e6, k=k, **v))
                marca = "  <== TRIPÉ" if ok3(v) else ""
                if v["sd"] < base["sd"] - 1e-6 or ok3(v):
                    print(f"    s_crit {sc*1e6:5.0f}um k {k:<7g} MAE {v['mae']:.4f} "
                          f"max {v['mx']:.4f} σ {v['sd']:.4f} β {v['beta']:+.3f}"
                          f"{marca}")
                if melhor is None or v["sd"] < melhor["sd"]:
                    melhor = v | {"s_crit_um": sc * 1e6, "k": k}
        _EXTRA.clear()
        if melhor:
            d = melhor["sd"] - base["sd"]
            print(f"    MELHOR σ_res: {melhor['sd']:.4f} "
                  f"({d:+.4f} vs nominal) em s_crit {melhor['s_crit_um']:.0f}um "
                  f"k {melhor['k']:g} · passa o tripé: {ok3(melhor)}")
        saida.append(dict(grupo=grupo, case=cid, nominal=base, grade=linhas))

OUT.write_text(json.dumps(saida, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"\n{'=' * 74}\nRESUMO DE ALCANCE\n{'=' * 74}")
for l in saida:
    if not l["grade"]:
        print(f"  {l['case'][:46]:46s} sem célula válida")
        continue
    b = l["nominal"]
    mel = min(l["grade"], key=lambda z: z["sd"])
    passa = sum(1 for z in l["grade"] if ok3(z))
    print(f"  {l['case'][:46]:46s} σ {b['sd']:.4f} -> {mel['sd']:.4f} "
          f"({mel['sd'] - b['sd']:+.4f}) · células no tripé: {passa}/{len(l['grade'])}")
print(f"\nescrito: {OUT.relative_to(ROOT)}")
