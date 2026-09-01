# -*- coding: utf-8 -*-
"""Executor do prereg P3-R2 LU_2024 (2026-07-31-lu2024-p3-r2-prereg.md).

Estagio A: triagem-c1 {emb_depth x frac x N_emb} com c_bend=4.8 (ancora
Fig.21), 8 condicoes (sem T4). Estagio B: sobreviventes x {k_ratchet x
floor} full-curve nas 5 LEITURAS. Gates G1-G5; --adotar so escreve com
PASSA. Held nunca olhadas antes do G3.

Saida: lu2024_p3_r2_exec.json + prints ASCII.
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

C_BEND = 30.0  # ANCORADO: k_tr(30)=98.3e6 vs 98.4e6 medido (Fig.21)
READS = ["lu2024_M8_fig18_amp0p25", "lu2024_M8_fig18_amp1p0",
         "lu2024_M8_fig20_T22Nm", "lu2024_M8_fig20_T10Nm",
         "lu2024_M8_fig18_amp2p0"]
HELD = ["lu2024_M8_fig18_amp0p5", "lu2024_M8_fig18_amp1p5",
        "lu2024_M8_fig20_T16Nm", "lu2024_M8_fig20_T28Nm"]
T4 = "lu2024_M8_fig20_T4Nm"
C1 = [  # (case, alvo Tabela 8/9) — SEM T4
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


def _ov(emb_um, frac, nemb, kr=None, floor=None, q=0.0):
    ov = {"c_bend": C_BEND, "emb_slip_gate": q,
          "emb_depth": emb_um * 1e-6, "emb_load_frac": frac, "N_emb": nemb}
    if kr is not None:
        ov["k_ratchet"] = kr
    if floor is not None:
        ov["loose_arrest_floor"] = floor
    return ov


def _sim(cid, ov, n_cap=None):
    _EXTRA.clear()
    _EXTRA.update(ov)
    try:
        return rn.simulate_case(record(cid), n_cap=n_cap)
    finally:
        _EXTRA.clear()


def _c1(cid, ov):
    d = _sim(cid, ov, n_cap=3).to_dict()
    for x, r in zip(d.get("cycles") or [], d.get("ratio") or []):
        if x >= 1.0:
            return 1.0 - float(r)
    return float("nan")


def main() -> int:
    st = ValidationStore()
    base = {c: st.get(c) for c in READS + HELD + [T4]}
    out = {"estagioA": [], "estagioB": []}

    # ---- Estagio A: triagem-c1 --------------------------------------------
    print("Estagio A: 27 pontos x 8 condicoes (c1)")
    A = []
    for emb in (8.0, 11.0, 14.0):
        for frac in (0.30, 0.40, 0.50):
            for nemb in (0.5, 1.0):
              for q in (0.5, 1.0, 2.0):
                ov = _ov(emb, frac, nemb, q=q)
                det = {cid: _c1(cid, ov) for cid, _ in C1}
                mae = float(np.mean([abs(det[c] - a) for c, a in C1]))
                mono = all(det[AMP_ORDER[i]] <= det[AMP_ORDER[i + 1]] + 0.02
                           for i in range(len(AMP_ORDER) - 1))
                ok025 = det["lu2024_M8_fig18_amp0p25"] <= 0.22
                A.append({"emb": emb, "frac": frac, "nemb": nemb, "q": q,
                          "mae_c1": mae, "mono": mono, "ok025": ok025,
                          "det": det})
                print(f"  emb={emb:4.1f} frac={frac:.2f} N={nemb:3.1f} "
                      f"q={q:.1f} MAE(c1)={mae:.4f} "
                      f"mono={'S' if mono else 'n'} "
                      f"c1_025={det['lu2024_M8_fig18_amp0p25']:.3f}")
    out["estagioA"] = [{k: v for k, v in a.items() if k != "det"} for a in A]
    surv = sorted([a for a in A if a["mono"] and a["ok025"]],
                  key=lambda a: a["mae_c1"])[:4]
    if not surv:
        surv = sorted(A, key=lambda a: a["mae_c1"])[:2]
        print("AVISO: nenhum ponto monotonico — 2 melhores por MAE seguem")
    print("\nsobreviventes:", [(s["emb"], s["frac"], s["nemb"],
                                round(s["mae_c1"], 4)) for s in surv])

    # ---- Estagio B: full-curve nas LEITURAS -------------------------------
    print("\nEstagio B: sobreviventes x {k_ratchet x floor}, 5 leituras")
    melhor = None
    for s in surv:
        for kr in (0.005, 0.01, 0.02):
            for fl in (0.0, 0.10, 0.21):
                ov = _ov(s["emb"], s["frac"], s["nemb"], kr, fl, q=s["q"])
                maes, sds = {}, {}
                for cid in READS:
                    r = _sim(cid, ov)
                    maes[cid] = r.mae
                    sds[cid] = r.resid_std
                ok_mae = sum(1 for v in maes.values() if v <= 0.05)
                J = float(np.sum([v ** 2 for v in sds.values()]))
                row = {**{k: s[k] for k in ("emb", "frac", "nemb", "q")},
                       "kr": kr, "floor": fl, "reads_mae_ok": ok_mae,
                       "J": J, "maes": {c.split("_")[-1]: round(v, 4)
                                        for c, v in maes.items()}}
                out["estagioB"].append(row)
                print(f"  emb={s['emb']:4.1f} frac={s['frac']:.1f} "
                      f"N={s['nemb']:3.1f} kr={kr:.3f} fl={fl:.2f} "
                      f"ok={ok_mae}/5 J={J:.4f} {row['maes']}")
                cand = (ok_mae, -J)
                if melhor is None or cand > (melhor["reads_mae_ok"],
                                             -melhor["J"]):
                    melhor = row
    out["melhor"] = melhor
    print(f"\nMELHOR: {melhor}")

    # ---- Gates -------------------------------------------------------------
    ov = _ov(melhor["emb"], melhor["frac"], melhor["nemb"],
             melhor["kr"], melhor["floor"], q=melhor["q"])
    # G1: k_tr com c_bend=4.8
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
    print(f"\nG1 k_tr(c_bend=4.8) = {ktr/1e6:.1f}e6 N/m "
          f"{'ok' if g1 else 'FALHA'}")

    # G2: c1 no ponto escolhido
    det = {cid: _c1(cid, ov) for cid, _ in C1}
    mae_c1 = float(np.mean([abs(det[c] - a) for c, a in C1]))
    mono = all(det[AMP_ORDER[i]] <= det[AMP_ORDER[i + 1]] + 0.02
               for i in range(len(AMP_ORDER) - 1))
    g2 = mae_c1 <= 0.08 and mono
    print(f"G2 MAE(c1)={mae_c1:.4f} mono={mono} {'ok' if g2 else 'FALHA'}")

    # G3: held-out (agora sim, e SO agora)
    antes_sd = {c: base[c].resid_std for c in HELD}
    antes_mae = {c: base[c].mae for c in HELD}
    dep_sd, dep_mae = {}, {}
    for cid in HELD:
        r = _sim(cid, ov)
        dep_sd[cid] = r.resid_std
        dep_mae[cid] = r.mae
    split = HoldoutSplit(criterio="2 por varredura; par mesmo-teste "
                                  "amp1p0==T22 junto nas leituras",
                         reads=tuple(READS), held=tuple(HELD))
    g3sd = veredicto_generalizacao(antes_sd, dep_sd, split, tol=TOL)
    g3ma = veredicto_generalizacao(antes_mae, dep_mae, split, tol=TOL)
    g3 = g3sd["generaliza"] and g3ma["generaliza"]
    print(f"G3 sd:{g3sd['generaliza']} (med {g3sd['mediana_held_antes']:.4f}"
          f"->{g3sd['mediana_held_depois']:.4f}) mae:{g3ma['generaliza']} "
          f"(med {g3ma['mediana_held_antes']:.4f}->"
          f"{g3ma['mediana_held_depois']:.4f}) {'ok' if g3 else 'FALHA'}")

    # G4: acervo 10 curvas vs pos-P0
    pioras = []
    dep_all = {}
    for cid in READS + HELD + [T4]:
        r = _sim(cid, ov)
        dep_all[cid] = r
        b = base[cid]
        for rot, va, vb in (("mae", b.mae, r.mae), ("mx", b.maxerr, r.maxerr),
                            ("sd", b.resid_std, r.resid_std)):
            if vb > va + TOL:
                pioras.append((cid.split("_")[-1], rot,
                               round(va, 3), round(vb, 3)))
    g4 = not pioras
    print(f"G4 acervo: {'ok' if g4 else 'FALHA'} {pioras[:8]}")

    # G5: rendimento
    med_antes = float(np.median([base[c].mae for c in READS + HELD + [T4]]))
    med_dep = float(np.median([dep_all[c].mae for c in READS + HELD + [T4]]))
    pares = [(x.source, st.get(x.case_id)) for x in all_records()
             if st.get(x.case_id) is not None]
    lim = rh.limite_sres("LU_2024", rh._pisos_medidos(pares))
    fecham = sum(1 for c in READS
                 if dep_all[c].resid_std <= lim
                 and dep_all[c].mae <= rh.META_MAE
                 and dep_all[c].maxerr <= rh.META_MAX)
    g5 = (med_dep <= 0.70 * med_antes) or (fecham >= 2)
    print(f"G5 mediana {med_antes:.4f}->{med_dep:.4f} "
          f"({med_dep/med_antes:.0%}) fecham={fecham} "
          f"{'ok' if g5 else 'FALHA'}")

    passa = g1 and g2 and g3 and g4 and g5
    out.update({"G1": {"ktr": ktr, "ok": g1},
                "G2": {"mae_c1": mae_c1, "mono": mono, "ok": g2},
                "G3": {"sd": g3sd, "mae": g3ma, "ok": g3},
                "G4": {"ok": g4, "pioras": pioras},
                "G5": {"med_antes": med_antes, "med_dep": med_dep,
                       "fecham": fecham, "ok": g5},
                "PASSA": passa})
    print(f"\n{'PASSA' if passa else 'NAO PASSA'}")

    if passa and "--adotar" in sys.argv:
        cfgp = ROOT / "New_Theory" / "adopted_configs.json"
        cfg = json.loads(cfgp.read_text(encoding="utf-8"))
        ent = cfg["sources"]["LU_2024"]
        novo = {"c_bend": C_BEND, "emb_depth": melhor["emb"] * 1e-6,
                "emb_load_frac": melhor["frac"], "N_emb": melhor["nemb"],
                "emb_slip_gate": melhor["q"],
                "k_ratchet": melhor["kr"],
                "loose_arrest_floor": melhor["floor"]}
        prov = ("P3 re-leitura sob drive corrigido (fig20 1.0mm): c_bend "
                "ANCORADO na Fig.21 (k_tr medido 98.4e6 N/m no F0 central); "
                "emb {depth,frac,N} ancorados nos c1 das Tabelas 8/9 (T4 "
                "fora — poluido por estagio-2, pendente P5); ratchet/floor "
                "full-curve nas 5 leituras; held-out 4 curvas generaliza; "
                "preregs 2026-07-31-lu2024-p3{,-r2}; adotado por delegacao "
                "(autorizacao em sessao: 'vai para o P3')")
        ent["cfg"].update(novo)
        for k in novo:
            ent.setdefault("prov", {})[k] = prov
        cfgp.write_text(json.dumps(cfg, ensure_ascii=False, indent=1),
                        encoding="utf-8")
        print("ADOTADO — re-carimbar store INTEIRO + exemplo + reports.")
    (ROOT / "New_Theory" / "lu2024_p3_r2_exec.json").write_text(
        json.dumps(out, indent=1), encoding="utf-8")
    return 0 if passa else 1


if __name__ == "__main__":
    raise SystemExit(main())
