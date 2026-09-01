# -*- coding: utf-8 -*-
"""F2 P2.2 (prereg 2026-07-21-master-f2-onda-b-prereg.md): creep saturante
vs log-t — confronto na ÚNICA fonte de creep com gap real: JCSR_2023.

Escopo (decisão registrada ANTES de rodar, coerente com o prereg + MEM):
- CACCESE/QIN_2024/LI_2022_MARSTRUC têm 0 violadores do tripé (todos os casos
  <=0,052/0,089) -> NÃO entram no fit: "no_piso" não se persegue (MEM §0.2) e
  parcimônia nega DOF novo sem ganho na meta. Log-t permanece o default lá.
- NAH_2014: curvas digitalizadas na pasta F, NÃO wired como casos de
  validação -> fora deste prereg (registrado).
- JCSR_2023 (5 casos, 4 violadores: galv_seawater 0,3115/0,4277,
  plain_outdoor 0,2182/0,3370, plain_seawater 0,1849/0,2743,
  stainless_seawater 0,2792/0,4133; plain_indoor 0,0009 no piso):
  fit per-fonte de (creep_t_c, creep_alpha_sat) com creep_mode="saturating",
  C_creep MANTIDO (per-par, §4.7), grade 2D log10(t_c) x alpha, curvas
  completas, sandbox BAS_ADOPTED_CONFIGS.

Gate (imutável, do prereg) + operacionalização de parcimônia (escrita ANTES
do resultado): adota SOMENTE se [mediana da fonte cai >0,005 OU count de
violadores da fonte cai] E nenhum caso piora >0,1 E count não sobe.
Senão: FAIL documentado (rótulo MEM 'forma' 3/5 sugere que a cinética
saturante pode não fechar sozinha) -> casos ficam para F3.

Uso: python New_Theory/f2_p22_creep_jcsr.py [--workers N]
Saída: New_Theory/f2_p22_result.json (grade, melhor par, veredito).
NÃO escreve no canônico (adoção é passo separado se PASS).
"""
from __future__ import annotations

import argparse
import io
import json
import os
import sys
import tempfile
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]

FONTE = "JCSR_2023"
CASOS = ["jcsr2023_galv_seawater", "jcsr2023_plain_indoor",
         "jcsr2023_plain_outdoor", "jcsr2023_plain_seawater",
         "jcsr2023_stainless_seawater"]
VIOL_BASE = 4


def _grupos_da_fonte(d):
    """Todos os grupos FONTE_token de JCSR (a fonte pode ter per-condição)."""
    return [k for k in d["sources"] if k == FONTE or k.startswith(FONTE + "_")
            or k.startswith("JCSR_")]


def _sandbox(t_c: float, alpha: float) -> str:
    src = _ROOT / "New_Theory/adopted_configs.json"
    d = json.loads(io.open(src, encoding="utf-8").read())
    # BUG da 1a rodada (2026-07-21): `or [FONTE]` so' disparava com lista
    # VAZIA — como JCSR_2023_indoor existia, o cfg ia so' pro grupo indoor
    # (caso no piso) e os 4 violadores ficavam em log-t => grade toda
    # identica ao baseline. FONTE precisa entrar SEMPRE.
    grupos = sorted(set(_grupos_da_fonte(d)) | {FONTE})
    for gk in grupos:
        cfg = d["sources"].setdefault(gk, {"pack": "PACK", "cfg": {}})["cfg"]
        cfg["creep_mode"] = "saturating"
        cfg["creep_t_c"] = float(t_c)
        cfg["creep_alpha_sat"] = float(alpha)
    fd, p = tempfile.mkstemp(suffix=f"_t{t_c:.2e}_a{alpha:.2f}.json",
                             prefix="p22_")
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
    res = simulate_case(record(cid), now="p22-fit")
    return {"case_id": cid, "sandbox": sandbox_path, "ok": res.ok,
            "mae": res.mae, "maxerr": res.maxerr, "error": res.error}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int,
                    default=max(2, (os.cpu_count() or 4) - 2))
    args = ap.parse_args(argv)
    sys.path.insert(0, str(_ROOT / "src"))
    import numpy as np

    store = json.loads(io.open(
        _ROOT / "Models/CALIBRATION_AND_VALIDATION/validation_store.json",
        encoding="utf-8").read())
    base = {c: {"mae": store[c]["mae"], "maxerr": store[c]["maxerr"]}
            for c in CASOS}
    med_base = float(np.median([base[c]["mae"] for c in CASOS]))
    print("baseline:", json.dumps(base), flush=True)

    def rodada(pares):
        sb = {pr: _sandbox(*pr) for pr in pares}
        tarefas = [(cid, p) for pr, p in sb.items() for cid in CASOS]
        out = {pr: {} for pr in pares}
        p2pr = {p: pr for pr, p in sb.items()}
        with ProcessPoolExecutor(max_workers=args.workers,
                                 initializer=_init_worker) as ex:
            futs = {ex.submit(_sim_one, t): t for t in tarefas}
            for fut in as_completed(futs):
                r = fut.result()
                out[p2pr[r["sandbox"]]][r["case_id"]] = r
        for p in sb.values():
            try:
                os.unlink(p)
            except OSError:
                pass
        return out

    def escore(pc):
        maes = [v["mae"] for v in pc.values() if v.get("mae") is not None]
        return float(np.median(maes)) if maes else 9e9

    res_grade = {}

    def registra(g):
        for pr, pc in g.items():
            res_grade[f"tc={pr[0]:.3e},a={pr[1]:.2f}"] = {
                c: {k: v[k] for k in ("mae", "maxerr", "ok")}
                for c, v in pc.items()}

    # grade 1: t_c 1e2..1e8 s (7; relaxacao outdoor = escala de meses),
    # alpha 0.4..1.4 (4) = 28 pares
    g1_pares = [(10 ** e, a) for e in np.linspace(2, 8, 7)
                for a in np.linspace(0.4, 1.4, 4)]
    print(f"[grade 1] {len(g1_pares)} pares × {len(CASOS)} curvas", flush=True)
    g1 = rodada(g1_pares)
    registra(g1)
    m1 = min(g1, key=lambda pr: escore(g1[pr]))
    print(f"[grade 1] melhor tc={m1[0]:.3e} a={m1[1]:.2f} "
          f"mediana={escore(g1[m1]):.4f}", flush=True)

    # grade 2: refino ±meia década em t_c, ±0.25 em alpha (5x3)
    lo, hi = np.log10(m1[0]) - 0.5, np.log10(m1[0]) + 0.5
    alo, ahi = max(0.1, m1[1] - 0.25), m1[1] + 0.25
    g2_pares = [(10 ** e, a) for e in np.linspace(lo, hi, 5)
                for a in np.linspace(alo, ahi, 3)]
    print(f"[grade 2] refino {len(g2_pares)} pares", flush=True)
    g2 = rodada(g2_pares)
    registra(g2)
    todos = {**g1, **g2}
    melhor = min(todos, key=lambda pr: escore(todos[pr]))
    fin = todos[melhor]
    med_fit = escore(fin)
    print(f"[fit] tc={melhor[0]:.4e} alpha={melhor[1]:.3f} "
          f"mediana {med_base:.4f}->{med_fit:.4f}", flush=True)

    viol_fit = sum(1 for c in CASOS
                   if (fin[c].get("mae") or 9) > 0.10
                   or (fin[c].get("maxerr") or 9) > 0.10)
    piora = any((fin[c].get("mae") or 9) > base[c]["mae"] + 0.10 for c in CASOS)
    melhora = (med_fit < med_base - 0.005) or (viol_fit < VIOL_BASE)
    verdict = "PASS" if (melhora and not piora and viol_fit <= VIOL_BASE) \
        else "FAIL"

    out = dict(
        prereg="docs/superpowers/specs/2026-07-21-master-f2-onda-b-prereg.md",
        fonte=FONTE, casos=CASOS, baseline=base,
        escopo_nota=("Caccese/Qin/MarStruc excluídos: 0 violadores (no_piso "
                     "não se persegue, parcimônia); Nah2014 não wired"),
        fit=dict(creep_t_c=float(melhor[0]), creep_alpha_sat=float(melhor[1])),
        tripe_fitado={c: dict(mae=fin[c].get("mae"),
                              maxerr=fin[c].get("maxerr")) for c in CASOS},
        mediana=dict(antes=med_base, depois=med_fit),
        violadores=dict(antes=VIOL_BASE, depois=viol_fit),
        grade=res_grade, verdict=verdict)
    p = _ROOT / "New_Theory/f2_p22_result.json"
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
