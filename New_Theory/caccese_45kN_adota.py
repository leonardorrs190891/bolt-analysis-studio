# -*- coding: utf-8 -*-
"""Adocao D-I — `C_creep` do grupo 45kN do CACCESE, alvo no CENTRO das replicas.

Escreve `adopted_configs.json` (com backup), verifica re-simulando as 3 curvas
do grupo contra o que a sonda mediu, e ABORTA se divergirem.

Valor: C0 x 0.85 = 5.477047e-10. Escolhido entre as 2 celulas que passam TODOS
os gates pelo criterio do G5 — a mais CENTRADA na banda de replicas
(|erro_rep1 - erro_rep2| = 0.0065), NAO a de menor MAE de uma delas: foi
exatamente essa escolha implicita que colou o modelo na rep2 e o deixou fora
da banda das duas.

    py -3.12 New_Theory/caccese_45kN_adota.py [--dry]
"""
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

CFG = ROOT / "New_Theory" / "adopted_configs.json"
GRUPO = "CACCESE_2009_45kN"
FATOR = 0.85
CIDS = ["caccese2009_tapered_45kN_rep1", "caccese2009_tapered_45kN_rep2",
        "caccese2009_protruding_45kN"]

PROV = ("D-I (2026-08-04): alvo no CENTRO das replicas. O valor anterior "
        "deixava o modelo ABAIXO das DUAS replicas da condicao tapered 45 kN "
        "(vies -0.0635 e -0.0253) — fora da banda que o proprio dado nao "
        "distingue (piso |rep1-rep2| = 0.0382). Fit de 1 numero (C0 x 0.85), "
        "escolhido pela CENTRAGEM na banda (|b1-b2| = 0.0065), nunca por "
        "minimizar o MAE de uma das replicas — foi essa escolha implicita que "
        "produziu o defeito. Modelo agora a 0.0206 (rep1) e 0.0271 (rep2), as "
        "duas <= piso. C x0.80 centrava melhor e foi REPROVADA no G2: a "
        "protruding_45kN (mesma config, no tripe) piorava +0.0222 no MAE, o "
        "dobro da tolerancia. creep_mode/alpha/t_c do D-H ficam CONGELADOS: "
        "isto e' nivel, nao forma.")


def main() -> int:
    d = json.loads(CFG.read_text(encoding="utf-8"))
    cfg = d["sources"][GRUPO]["cfg"]
    C0 = float(cfg["C_creep"])
    C1 = C0 * FATOR
    print(f"{GRUPO}: C_creep {C0:.6e} -> {C1:.6e}  (x{FATOR})")
    if "--dry" in sys.argv:
        print("--dry: nada escrito")
        return 0

    bkp = CFG.with_suffix(".json.bkp_di")
    shutil.copy2(CFG, bkp)
    cfg["C_creep"] = C1
    d["sources"][GRUPO].setdefault("prov", {})["C_creep"] = PROV
    CFG.write_text(json.dumps(d, indent=1, ensure_ascii=False),
                   encoding="utf-8")
    print(f"backup {bkp.name} · adopted_configs.json escrito")

    import importlib
    import bolt_analysis_studio.calibration.knowledge_base as kb
    importlib.reload(kb)
    import bolt_analysis_studio.validation.runner as rn
    importlib.reload(rn)
    from bolt_analysis_studio.validation.case_registry import record

    probe = json.loads(
        (ROOT / "New_Theory" / "caccese_45kN_centro_exec.json").read_text(
            encoding="utf-8"))
    cel = next((g for g in probe["grade"] if abs(g["f"] - FATOR) < 1e-12), None)
    if cel is None:
        print("!! celula da sonda ausente no JSON")
        return 2
    print("\nverificacao (vs sonda):")
    ruim = []
    for cid in CIDS:
        r = rn.simulate_case(record(cid))
        if not r.ok:
            print(f"  !! {cid}: {r.error}")
            return 2
        e = cel["vals"][cid]
        d3 = max(abs(r.mae - e["mae"]), abs(r.maxerr - e["mx"]),
                 abs(r.resid_std - e["sd"]))
        flag = "OK" if d3 < 1e-9 else "DIVERGE"
        if flag != "OK":
            ruim.append(cid)
        print(f"  {flag:8s} {cid:42s} mae {r.mae:.4f} mx {r.maxerr:.4f} "
              f"sig {r.resid_std:.4f}")
    if ruim:
        print("\n!! ABORTAR — nao reproduz a sonda. Restaure o backup.")
        return 3
    print("\nadocao CONFIRMADA ao 1e-9. Proximo: re-stamp uniforme do store.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
