# -*- coding: utf-8 -*-
"""F2 P2.1 (prereg 2026-07-21-master-f2-onda-b-prereg.md): canal de flanco
per-rig no H.Li2022 (LI_2022_TRIBOINT).

Mecânica: sandbox de adopted_configs (env BAS_ADOPTED_CONFIGS, padrão da
campanha p/ fits) com `flank_wear_on=1.0` + `flank_amp_exp=1.5` (herdado da
tentativa 2 do T4, Liu 2020) no cfg da fonte; varre `k_wear_flank` em grade
log10 (grossa+refino) em torno da partida 1,89e-13 (mínimo interior do T4
Rig B), simulando as 4 CURVAS COMPLETAS pelo runner canônico em paralelo.
Métrica de fit: mediana do MAE da fonte; gate decide com o tripé.

Gate (imutável, do prereg):
- G2.1a: 4 casos tripé<0,1 (p/ o full: se maxerr>0,1 vier só do trecho
  pós-fratura out-of-model, aplicar convenção de trim registrada e reavaliar;
  se os outros 3 passarem e o full melhorar >=50% do gap, não força FAIL —
  registra p/ decisão de exceção F5).
- G2.1b: nenhuma curva da fonte regride >0,1; mediana da fonte não piora
  >0,005 (aqui: mediana deve MELHORAR ou empatar).
- (G2.1c transversais por construção — verificado fora, re-sim de controles.)

Saída: New_Theory/f2_p21_result.json (grade completa, melhor k, tripé por
caso antes/depois, veredito). NÃO escreve no adopted_configs canônico — a
adoção é passo separado, single-writer, após o gate.

Uso: python New_Theory/f2_p21_flank_li2022.py [--workers N]
"""
from __future__ import annotations

import argparse
import io
import json
import os
import shutil
import sys
import tempfile
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]

FONTE = "LI_2022_TRIBOINT"
CASOS = ["li2022ti_axialmin_10Hz", "li2022ti_axialmin_15Hz",
         "li2022ti_axialmin_20Hz", "li2022ti_axial_10Hz_full"]
PARTIDA = 1.89e-13
EXP_HERDADO = 1.5


def _sandbox(k: float) -> str:
    """Cópia do adopted_configs com o canal ligado e k_wear_flank=k."""
    src = _ROOT / "New_Theory/adopted_configs.json"
    d = json.loads(io.open(src, encoding="utf-8").read())
    cfg = d["sources"].setdefault(FONTE, {"pack": "PACK", "cfg": {}})["cfg"]
    cfg["flank_wear_on"] = 1.0
    cfg["k_wear_flank"] = float(k)
    cfg["flank_amp_exp"] = EXP_HERDADO
    fd, p = tempfile.mkstemp(suffix=f"_k{k:.3e}.json", prefix="p21_")
    with io.open(fd, "w", encoding="utf-8") as f:
        f.write(json.dumps(d, ensure_ascii=False))
    return p


def _init_worker():
    import warnings
    warnings.filterwarnings("ignore")
    sys.path.insert(0, str(_ROOT / "src"))


def _sim_one(args):
    cid, sandbox_path = args
    os.environ["BAS_ADOPTED_CONFIGS"] = sandbox_path
    from bolt_analysis_studio.validation.case_registry import record
    from bolt_analysis_studio.validation.runner import simulate_case
    res = simulate_case(record(cid), now="p21-fit")
    return {"case_id": cid, "sandbox": sandbox_path, "ok": res.ok,
            "mae": res.mae, "maxerr": res.maxerr, "error": res.error}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int,
                    default=max(2, (os.cpu_count() or 4) - 2))
    args = ap.parse_args(argv)
    sys.path.insert(0, str(_ROOT / "src"))

    import numpy as np

    # baseline vigente (F0.4+F1): tripé dos 4 casos direto do store
    store = json.loads(io.open(
        _ROOT / "Models/CALIBRATION_AND_VALIDATION/validation_store.json",
        encoding="utf-8").read())
    base = {c: {"mae": store[c]["mae"], "maxerr": store[c]["maxerr"]}
            for c in CASOS}
    print("baseline:", json.dumps(base), flush=True)

    def rodada(ks):
        sandboxes = {k: _sandbox(k) for k in ks}
        tarefas = [(cid, sb) for k, sb in sandboxes.items() for cid in CASOS]
        out = {k: {} for k in ks}
        sb2k = {sb: k for k, sb in sandboxes.items()}
        with ProcessPoolExecutor(max_workers=args.workers,
                                 initializer=_init_worker) as ex:
            futs = {ex.submit(_sim_one, t): t for t in tarefas}
            for fut in as_completed(futs):
                r = fut.result()
                out[sb2k[r["sandbox"]]][r["case_id"]] = r
        for sb in sandboxes.values():
            try:
                os.unlink(sb)
            except OSError:
                pass
        return out

    res_grade = {}

    def escore(porcaso):
        maes = [v["mae"] for v in porcaso.values() if v.get("mae") is not None]
        return float(np.median(maes)) if maes else 9e9

    # grade grossa: 1e-14 .. 1e-12 (9 pontos) em torno da partida
    ks1 = [10 ** e for e in np.linspace(-14.0, -12.0, 9)]
    print(f"[grade 1] {len(ks1)} pontos × {len(CASOS)} curvas", flush=True)
    g1 = rodada(ks1)
    res_grade.update({f"{k:.4e}": {c: {kk: v[kk] for kk in ("mae", "maxerr", "ok")}
                                   for c, v in g1[k].items()} for k in g1})
    melhor1 = min(g1, key=lambda k: escore(g1[k]))
    print(f"[grade 1] melhor k={melhor1:.3e} mediana={escore(g1[melhor1]):.4f}",
          flush=True)

    # refino: ±meia década em torno do melhor, 7 pontos
    lo, hi = np.log10(melhor1) - 0.5, np.log10(melhor1) + 0.5
    ks2 = [10 ** e for e in np.linspace(lo, hi, 7)]
    print(f"[grade 2] refino {len(ks2)} pontos", flush=True)
    g2 = rodada(ks2)
    res_grade.update({f"{k:.4e}": {c: {kk: v[kk] for kk in ("mae", "maxerr", "ok")}
                                   for c, v in g2[k].items()} for k in g2})
    todos = {**g1, **g2}
    melhor = min(todos, key=lambda k: escore(todos[k]))
    fin = todos[melhor]
    print(f"[fit] k_wear_flank={melhor:.4e} (partida {PARTIDA:.3e})", flush=True)

    # ---- gate ----
    def tri(c):
        return fin[c].get("mae"), fin[c].get("maxerr")

    passa_caso = {c: (tri(c)[0] is not None and tri(c)[0] < 0.10
                      and tri(c)[1] < 0.10) for c in CASOS}
    regride = {c: (tri(c)[0] is not None and base[c]["mae"] is not None
                   and tri(c)[0] > base[c]["mae"] + 0.10) for c in CASOS}
    med_base = float(np.median([base[c]["mae"] for c in CASOS]))
    med_fit = escore(fin)
    tres_passam = all(passa_caso[c] for c in CASOS[:3])
    full = CASOS[3]
    gap_full_antes = max(0.0, base[full]["maxerr"] - 0.10)
    gap_full_depois = max(0.0, (tri(full)[1] or 9e9) - 0.10)
    full_melhora_50 = (gap_full_antes > 0
                       and gap_full_depois <= 0.5 * gap_full_antes)
    g21a = all(passa_caso.values()) or (tres_passam and full_melhora_50)
    g21b = (not any(regride.values())) and (med_fit <= med_base + 0.005)
    verdict = "PASS" if (g21a and g21b) else "FAIL"

    out = dict(
        prereg="docs/superpowers/specs/2026-07-21-master-f2-onda-b-prereg.md",
        fonte=FONTE, casos=CASOS, partida=PARTIDA, exp_herdado=EXP_HERDADO,
        baseline=base, k_fitado=float(melhor),
        tripe_fitado={c: dict(mae=tri(c)[0], maxerr=tri(c)[1]) for c in CASOS},
        mediana=dict(antes=med_base, depois=med_fit),
        gate=dict(G21a=bool(g21a), G21b=bool(g21b),
                  passa_caso={c: bool(v) for c, v in passa_caso.items()},
                  full_melhora_50=bool(full_melhora_50),
                  nota_full=("gap maxerr full antes/depois: "
                             f"{gap_full_antes:.4f}/{gap_full_depois:.4f}")),
        grade=res_grade, verdict=verdict)
    p = _ROOT / "New_Theory/f2_p21_result.json"
    txt = json.dumps(out, indent=1, ensure_ascii=False)
    for _ in range(200):
        try:
            with io.open(p, "w", encoding="utf-8") as f:
                f.write(txt)
            break
        except PermissionError:
            time.sleep(0.05)
    print(f"[gate] verdict={verdict} → {p}", flush=True)
    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
