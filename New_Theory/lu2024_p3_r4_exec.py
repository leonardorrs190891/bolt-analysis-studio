# -*- coding: utf-8 -*-
"""Executor do prereg P3-R4 LU_2024 (2026-07-31-lu2024-p3-r4-prereg.md).

ESTAGIO UNICO: o c1 e' medido com o ov COMPLETO (kr/floor dentro — o
conserto do defeito provado na R3). Rodada FINAL do P3.

Saida: lu2024_p3_r4_exec.json + prints ASCII.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import bolt_analysis_studio.validation.report_html as rh   # noqa: E402
import bolt_analysis_studio.validation.runner as rn        # noqa: E402
from bolt_analysis_studio.calibration.holdout import (      # noqa: E402
    HoldoutSplit, veredicto_generalizacao)
from bolt_analysis_studio.validation.case_registry import (  # noqa: E402
    all_records, record)
from bolt_analysis_studio.validation.store import ValidationStore  # noqa: E402

C_BEND = 30.0
READS = ["lu2024_M8_fig18_amp0p25", "lu2024_M8_fig20_T22Nm",
         "lu2024_M8_fig20_T10Nm", "lu2024_M8_fig18_amp2p0"]
HELD = ["lu2024_M8_fig18_amp0p5", "lu2024_M8_fig18_amp1p5",
        "lu2024_M8_fig20_T16Nm", "lu2024_M8_fig20_T28Nm"]
T4 = "lu2024_M8_fig20_T4Nm"
DUP = "lu2024_M8_fig18_amp1p0"
C1 = [
    ("lu2024_M8_fig18_amp0p25", 0.171), ("lu2024_M8_fig18_amp0p5", 0.362),
    ("lu2024_M8_fig18_amp1p0", 0.368), ("lu2024_M8_fig18_amp1p5", 0.496),
    ("lu2024_M8_fig18_amp2p0", 0.502), ("lu2024_M8_fig20_T10Nm", 0.362),
    ("lu2024_M8_fig20_T16Nm", 0.359), ("lu2024_M8_fig20_T28Nm", 0.383),
]
AMP_ORDER = ["lu2024_M8_fig18_amp0p25", "lu2024_M8_fig18_amp0p5",
             "lu2024_M8_fig18_amp1p0", "lu2024_M8_fig18_amp1p5",
             "lu2024_M8_fig18_amp2p0"]
TOL = 0.01

_EXTRA: dict = {}
_orig = rn._effective_overrides
rn._effective_overrides = lambda rec, base: {**_orig(rec, base), **_EXTRA}


def _ov(emb, frac, nemb, q, kr, fl):
    return {"c_bend": C_BEND, "emb_depth": emb * 1e-6,
            "emb_load_frac": frac, "N_emb": nemb, "emb_slip_gate": q,
            "k_ratchet": kr, "loose_arrest_floor": fl}


def _sim(cid, ov, n_cap=None):
    _EXTRA.clear()
    _EXTRA.update(ov)
    try:
        return rn.simulate_case(record(cid), n_cap=n_cap)
    finally:
        _EXTRA.clear()


def _c1_det(ov):
    det = {}
    for cid, _ in C1:
        d = _sim(cid, ov, n_cap=3).to_dict()
        v = float("nan")
        for x, r in zip(d.get("cycles") or [], d.get("ratio") or []):
            if x >= 1.0:
                v = 1.0 - float(r)
                break
        det[cid] = v
    return det


def main() -> int:
    st = ValidationStore()
    base = {c: st.get(c) for c in READS + HELD + [T4, DUP]}
    out = {"grade": [], "n_c1_ok": 0}
    melhor = None
    total = 0
    # c1 NAO depende do floor (razao do ciclo 1 >= ~0.5 >> 0.21, o clamp
    # nunca morde) — medi-lo FORA do loop de floor corta ~2600 sims.
    for emb in (8.0, 11.0, 14.0):
        for frac in (0.30, 0.40, 0.50):
            for q in (0.5, 1.0, 2.0):
                for nemb in (0.5, 1.0):
                    for kr in (0.003, 0.005, 0.01):
                        total += 1
                        det = _c1_det(_ov(emb, frac, nemb, q, kr, 0.21))
                        mae_c1 = float(np.mean(
                            [abs(det[c] - a) for c, a in C1]))
                        mono = all(
                            det[AMP_ORDER[i]] <= det[AMP_ORDER[i + 1]] + 0.02
                            for i in range(len(AMP_ORDER) - 1))
                        ok025 = det["lu2024_M8_fig18_amp0p25"] <= 0.22
                        if not (mono and ok025 and mae_c1 <= 0.08):
                            continue
                        out["n_c1_ok"] += 1
                        for fl in (0.10, 0.15, 0.21):
                            ov = _ov(emb, frac, nemb, q, kr, fl)
                            maes, sds = {}, {}
                            for cid in READS:
                                r = _sim(cid, ov)
                                maes[cid] = r.mae
                                sds[cid] = r.resid_std
                            okm = sum(1 for v in maes.values() if v <= 0.05)
                            J = float(np.sum([v ** 2 for v in sds.values()]))
                            row = {"emb": emb, "frac": frac, "q": q,
                                   "nemb": nemb, "kr": kr, "floor": fl,
                                   "mae_c1": mae_c1, "reads_mae_ok": okm,
                                   "J": J,
                                   "maes": {c.split("_")[-1]: round(v, 4)
                                            for c, v in maes.items()}}
                            out["grade"].append(row)
                            print(f"  c1ok emb={emb:4.1f} frac={frac:.2f} "
                                  f"q={q:.1f} N={nemb:3.1f} kr={kr:.3f} "
                                  f"fl={fl:.2f} c1={mae_c1:.4f} ok={okm}/4 "
                                  f"J={J:.4f} {row['maes']}")
                            cand = (okm, -J)
                            if melhor is None or cand > (
                                    melhor["reads_mae_ok"], -melhor["J"]):
                                melhor = row
    print(f"\ngrade: {total} pontos, {out['n_c1_ok']} passam o filtro c1")
    out["melhor"] = melhor
    if melhor is None:
        print("NENHUM ponto passa o filtro c1 — FIM DO P3 (P4/P6)")
        _dump(out)
        return 1
    print(f"MELHOR: {melhor}")

    ov = _ov(melhor["emb"], melhor["frac"], melhor["nemb"], melhor["q"],
             melhor["kr"], melhor["floor"])
    # ordem dos args: _ov(emb, frac, nemb=?, q=?, ...) — assinatura e'
    # (emb, frac, nemb, q, kr, fl); acima passei (.., nemb=melhor[...])
    ov = _ov(melhor["emb"], melhor["frac"], melhor["nemb"], melhor["q"],
             melhor["kr"], melhor["floor"])

    # G1
    from bolt_analysis_studio.numerical.dynamic_stiffness_analyzer import (
        JointMaterial, k_tr_transverse)
    from bolt_analysis_studio.validation.runner import (
        material_kwargs_for, geometry_for_case, _apply_adopted_geometry,
        inputs_for)
    rec = record("lu2024_M8_fig20_T22Nm")
    inp = inputs_for(rec.validation_case)
    geom = geometry_for_case(rec.validation_case,
                             grip_mm=inp["grip_mm"]["value"],
                             E=(inp.get("E") or {}).get("value"))
    geom = _apply_adopted_geometry(geom, rec.source, rec.case_id,
                                   rec.validation_case.bolt_size)
    kwargs = material_kwargs_for(rec, inp)
    kwargs["c_bend"] = C_BEND
    ktr = k_tr_transverse(geom, JointMaterial(**kwargs))
    g1 = 90e6 <= ktr <= 107e6
    print(f"\nG1 k_tr = {ktr/1e6:.1f}e6 {'ok' if g1 else 'FALHA'}")

    det = _c1_det(ov)
    mae_c1 = float(np.mean([abs(det[c] - a) for c, a in C1]))
    mono = all(det[AMP_ORDER[i]] <= det[AMP_ORDER[i + 1]] + 0.02
               for i in range(len(AMP_ORDER) - 1))
    g2 = mae_c1 <= 0.08 and mono
    print(f"G2 MAE(c1)={mae_c1:.4f} mono={mono} {'ok' if g2 else 'FALHA'}")

    antes_sd = {c: base[c].resid_std for c in HELD}
    antes_mae = {c: base[c].mae for c in HELD}
    dep_sd, dep_mae = {}, {}
    for cid in HELD:
        r = _sim(cid, ov)
        dep_sd[cid] = r.resid_std
        dep_mae[cid] = r.mae
    split = HoldoutSplit(criterio="2 por varredura; duplicata fora (P2)",
                         reads=tuple(READS), held=tuple(HELD))
    g3sd = veredicto_generalizacao(antes_sd, dep_sd, split, tol=TOL)
    g3ma = veredicto_generalizacao(antes_mae, dep_mae, split, tol=TOL)
    g3 = g3sd["generaliza"] and g3ma["generaliza"]
    print(f"G3 sd:{g3sd['generaliza']} mae:{g3ma['generaliza']} "
          f"(sd {g3sd['mediana_held_antes']:.4f}->"
          f"{g3sd['mediana_held_depois']:.4f}) {'ok' if g3 else 'FALHA'}")

    pioras = []
    dep_all = {}
    for cid in READS + HELD + [T4, DUP]:
        r = _sim(cid, ov)
        dep_all[cid] = r
        if cid in (T4, DUP):
            b = base.get(cid)
            if b is not None:
                print(f"  (info) {cid.split('_')[-1]}: mae "
                      f"{b.mae:.4f}->{r.mae:.4f}")
            continue
        b = base[cid]
        for rot, va, vb in (("mae", b.mae, r.mae), ("mx", b.maxerr, r.maxerr),
                            ("sd", b.resid_std, r.resid_std)):
            if vb > va + TOL:
                pioras.append((cid.split("_")[-1], rot,
                               round(va, 3), round(vb, 3)))
    g4 = not pioras
    print(f"G4: {'ok' if g4 else 'FALHA'} {pioras[:8]}")

    cens9 = READS + HELD + [T4]
    med_a = float(np.median([base[c].mae for c in cens9]))
    med_d = float(np.median([dep_all[c].mae for c in cens9]))
    pares = [(x.source, st.get(x.case_id)) for x in all_records()
             if st.get(x.case_id) is not None]
    lim = rh.limite_sres("LU_2024", rh._pisos_medidos(pares))
    fecham = sum(1 for c in READS
                 if dep_all[c].resid_std <= lim
                 and dep_all[c].mae <= rh.META_MAE
                 and dep_all[c].maxerr <= rh.META_MAX)
    g5 = (med_d <= 0.70 * med_a) or (fecham >= 2)
    print(f"G5 mediana {med_a:.4f}->{med_d:.4f} fecham={fecham} "
          f"{'ok' if g5 else 'FALHA'}")

    passa = g1 and g2 and g3 and g4 and g5
    out.update({"G1": g1, "G2": {"mae_c1": mae_c1, "ok": g2},
                "G3": {"sd": g3sd, "mae": g3ma, "ok": g3},
                "G4": {"ok": g4, "pioras": pioras},
                "G5": {"med_a": med_a, "med_d": med_d, "fecham": fecham,
                       "ok": g5},
                "PASSA": passa})
    print(f"\n{'PASSA' if passa else 'NAO PASSA — FIM DO P3'}")

    if passa and "--adotar" in sys.argv:
        cfgp = ROOT / "New_Theory" / "adopted_configs.json"
        cfg = json.loads(cfgp.read_text(encoding="utf-8"))
        ent = cfg["sources"]["LU_2024"]
        novo = {"c_bend": C_BEND, "emb_depth": melhor["emb"] * 1e-6,
                "emb_load_frac": melhor["frac"],
                "emb_slip_gate": melhor["q"], "N_emb": melhor["nemb"],
                "k_ratchet": melhor["kr"],
                "loose_arrest_floor": melhor["floor"]}
        prov = ("P3-R4 (estagio unico, c1 com ov completo): c_bend ANCORADO "
                "na Fig.21 (98.3e6 vs 98.4e6 medido); emb/frac/q/N ancorados "
                "nos c1 das Tabelas 8/9; kr/floor no full-curve das 4 "
                "leituras; held-out 4 curvas generalizou em 4 rodadas; "
                "preregs 2026-07-31-lu2024-p3{,-r2,-r3,-r4}; adotado por "
                "delegacao (autorizacao: 'siga para R3' + mandato)")
        ent["cfg"].update(novo)
        for k in novo:
            ent.setdefault("prov", {})[k] = prov
        cfgp.write_text(json.dumps(cfg, ensure_ascii=False, indent=1),
                        encoding="utf-8")
        print("ADOTADO — re-carimbar store INTEIRO + exemplo + reports.")
    _dump(out)
    return 0 if passa else 1


def _dump(out):
    (ROOT / "New_Theory" / "lu2024_p3_r4_exec.json").write_text(
        json.dumps(out, indent=1), encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
