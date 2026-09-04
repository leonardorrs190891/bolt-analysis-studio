# -*- coding: utf-8 -*-
"""Task 0 (plano L1-L7): snapshot baseline global do gate MEM.

Le o `validation_store.json` CANONICO ja existente (via `bolt_analysis_studio
.validation.store.ValidationStore`) casado com o registry de casos
(`case_registry.all_records()`) e grava `New_Theory/l1l7_baseline.json` com
as metricas globais que TODOS os gates das fatias L1-L7 usam como referencia:
mediana/media/desvio-padrao populacional do MAE, contagens de excedencia
(MAE>0.10, MAE>0.15, maxerr>0.10) e o "tripe" MAE/maxerr/sigma_res por caso
(para os gates poderem checar regressao caso-a-caso, nao so no agregado).

NAO re-simula nada (isso seria `python -m bolt_analysis_studio.validation
.report --all`, ~30-90 min) — o store esta fresco (ledger #59, batches do
dia da campanha continua; ver .superpowers/sdd/task-0-report.md), so agrega
o que ja esta' persistido.

Filtro "comparavel" = mesmo criterio de `validation.error_budget
.error_budget()`: todo registro de `case_registry.all_records()` cuja fonte
NAO e "USER" (casos importados ad hoc pela GUI, fora da biblioteca curada).
Dentro dos comparaveis, um caso so entra nas estatisticas se o store tiver
um CaseResult com ok=True e mae != None; os demais (ausentes do store,
ok=False, ou sem MAE — ex. final_ratio-only) vao para "missing" COM motivo
(sem drop silencioso).

Uso:
    PYTHONPATH=src python scripts/l1l7_baseline.py
(ou, a partir do root do repo, sem PYTHONPATH: o script insere src/ em
sys.path sozinho)

CAVEAT DE ARVORE (achado ao gerar o snapshot desta task): os 3 CSVs de
referencia âncora interna (Models/EXPERIMENTAL_ANCORA/reference_curves/ancora_interna*.csv,
ancora_interna{first,def}_*.csv) NAO sao versionados no git -- existem so como
arquivos locais na arvore de trabalho onde foram colocados. Um worktree/
clone fresco desta branch (sem esses 3 arquivos copiados manualmente) ve
177 casos comparaveis em vez de 180 (os 3 âncora interna caem para case_class=
"final_ratio" por falta do CSV e saem do filtro de `all_records()`). O
`New_Theory/l1l7_baseline.json` committado nesta task foi gerado a partir
da arvore principal (onde os 3 CSVs existem), batendo com o ledger #59
(180/0.0429/32/77) citado em `.superpowers/sdd/progress.md`; rodar este
script direto neste worktree reproduz so os 177 (registrado, nao e' bug).
"""
from __future__ import annotations

import json
import statistics
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from bolt_analysis_studio.validation.case_registry import all_records  # noqa: E402
from bolt_analysis_studio.validation.runner import engine_fingerprint  # noqa: E402
from bolt_analysis_studio.validation.store import ValidationStore  # noqa: E402

OUT_PATH = ROOT / "New_Theory" / "l1l7_baseline.json"


def _head_commit() -> str:
    try:
        out = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT,
                              capture_output=True, text=True, check=True)
        return out.stdout.strip()
    except (OSError, subprocess.CalledProcessError) as exc:
        return f"unknown ({exc})"


def _criterio() -> dict:
    """A regua vigente, lida da FONTE UNICA (`validation.report_html`)."""
    from bolt_analysis_studio.validation import report_html as rh
    return {"res_max": rh.META_MAX, "mae": rh.META_MAE,
            "sigma_res": rh.META_SRES,
            "nota": "tripe de 3 pernas (2026-07-29); a regua anterior era "
                    "MAE<=0.10 E maxerr<=0.10"}


def _censo_tripe(cases: dict) -> dict:
    """Censo sob a regua vigente + o que cada perna reprova SOZINHA.

    `n_sem_sigma` existe porque registro sem `resid_std` NAO e' julgavel na 3a
    perna: conta-lo como aprovado inflaria a meta em silencio, e reprova-lo
    inventaria medicao. Ele sai do censo, e o numero fica visivel.
    """
    from bolt_analysis_studio.validation import report_html as rh
    lim = (rh.META_MAX, rh.META_MAE, rh.META_SRES)
    ok = so_mae = so_mx = so_sd = varios = sem_sd = 0
    for c in cases.values():
        mae, mx, sd = c.get("mae"), c.get("maxerr"), c.get("resid_std")
        if mae is None or mx is None:
            continue
        if sd is None:
            sem_sd += 1
            continue
        f = [mx > lim[0], mae > lim[1], sd > lim[2]]
        if not any(f):
            ok += 1
        elif sum(f) > 1:
            varios += 1
        elif f[0]:
            so_mx += 1
        elif f[1]:
            so_mae += 1
        else:
            so_sd += 1
    from bolt_analysis_studio.validation.report_html import _EXCECOES
    exc_fora = sum(1 for cid, c in cases.items()
                   if cid in _EXCECOES and not (
                       c.get("mae") is not None and c.get("maxerr") is not None
                       and c.get("resid_std") is not None
                       and c["maxerr"] <= lim[0] and c["mae"] <= lim[1]
                       and c["resid_std"] <= lim[2]))
    return {"n_tripe": ok, "n_so_res_max": so_mx, "n_so_mae": so_mae,
            "n_so_sigma_res": so_sd, "n_multiplas_pernas": varios,
            "n_sem_sigma_res_nao_julgavel": sem_sd,
            "n_excecoes_assinadas_fora_do_tripe": exc_fora,
            "n_resolvidos": ok + exc_fora}


def build_baseline(store: "ValidationStore | None" = None) -> dict:
    store = store or ValidationStore()
    comparable = [r for r in all_records() if r.source != "USER"]

    cases: dict = {}
    missing: list = []
    for rec in comparable:
        res = store.get(rec.case_id)
        if res is None:
            missing.append({"case_id": rec.case_id, "source": rec.source,
                             "reason": "ausente do ValidationStore"})
            continue
        if not res.ok or res.mae is None:
            missing.append({"case_id": rec.case_id, "source": rec.source,
                             "reason": (res.error if res.error else
                                        "sem MAE (ok=False ou nao-simulavel, "
                                        "ex. final_ratio-only)")})
            continue
        cases[rec.case_id] = {"source": rec.source, "family": rec.family,
                               "mae": res.mae, "maxerr": res.maxerr,
                               "resid_std": res.resid_std}

    maes = [c["mae"] for c in cases.values()]
    maxerrs = [c["maxerr"] for c in cases.values() if c["maxerr"] is not None]

    snap = {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "base_commit": _head_commit(),
        "source_note": ("ValidationStore canonico (Models/CALIBRATION_AND_VALIDATION/"
                         "validation_store.json), ledger #59 -- lido AS IS, sem "
                         "re-simulacao (ver .superpowers/sdd/task-0-report.md)"),
        "store_path": str(store.path),
        "engine_fingerprint": engine_fingerprint(),
        "n": len(maes),
        "n_registry_comparable": len(comparable),
        "n_missing_or_unsimulated": len(missing),
        "mediana": statistics.median(maes) if maes else None,
        "media": statistics.mean(maes) if maes else None,
        "mae_std": statistics.pstdev(maes) if maes else None,
        # --- REGUA ANTIGA (2 pernas, limiares fixos em 0.10/0.15). Mantidos
        # para os gates L1-L7 que os citam nominalmente; NAO sao o tripe atual.
        "gt_010": sum(1 for m in maes if m > 0.10),
        "gt_015": sum(1 for m in maes if m > 0.15),
        "n_maxerr": len(maxerrs),
        "maxerr_gt_010": sum(1 for m in maxerrs if m > 0.10),
        # --- REGUA VIGENTE, gravada NO PROPRIO snapshot (2026-07-29). Sem isto o
        # arquivo nao diz sob que criterio foi medido, e um baseline que nao
        # carrega a propria regua e' exatamente o que fez o roadmap envelhecer em
        # silencio (regra §4.43). Os limites saem de report_html — fonte unica.
        "criterio": _criterio(),
        **_censo_tripe(cases),
        "missing": missing,
        "cases": cases,
    }
    return snap


def main() -> int:
    snap = build_baseline()
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(snap, ensure_ascii=False, indent=1) + "\n",
                         encoding="utf-8")
    summary = {k: v for k, v in snap.items() if k not in ("cases", "missing")}
    print(json.dumps(summary, ensure_ascii=False, indent=1))
    print(f"gravado em {OUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
