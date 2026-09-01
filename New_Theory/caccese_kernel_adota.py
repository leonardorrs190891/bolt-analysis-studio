# -*- coding: utf-8 -*-
"""Adocao D-H — kernel de creep saturante no CACCESE_2009.

Escreve `adopted_configs.json` (com backup), verifica re-simulando as 7 curvas
contra os numeros que a sonda mediu, e ABORTA se divergirem.

Celula adotada: `creep_alpha_sat = 0.2`, `creep_t_c = 100 x t_end = 7.2e8 s`.
Escolhida entre as DUAS que passam todos os gates, por parcimonia e nao por
contagem: no regime `t_c >> t_end` o kernel e' lei de potencia e `t_c`/`C_sat`
nao sao separadamente identificaveis (1 parametro de forma efetivo); a
alternativa (alpha=0.3, t_c = 1x t_end) fecha 1 curva a mais mas tem constante
de tempo IGUAL A DURACAO DO ENSAIO — seria fitar a janela, nao o material.

⚠️ O fator de renormalizacao e' POR GRUPO, porque `t_0` difere:
   t_0 = 7200 s        -> log(1001)  = 6.9088 -> fator 21.037
   t_0 = 23340.76 s    -> log(309.4) = 5.7348 -> fator 17.459
Usar um fator unico moveria o compblock 20 % de nivel em silencio.

    py -3.12 New_Theory/caccese_kernel_adota.py [--dry]
"""
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

CFG = ROOT / "New_Theory" / "adopted_configs.json"
GRUPOS = ["CACCESE_2009_compblock", "CACCESE_2009_45kN",
          "CACCESE_2009_12p7mm", "CACCESE_2009_19p1mm"]
ALPHA = 0.2
T_END = 2000.0 * 3600.0            # 2000 h em segundos (janela das 7 curvas)
T_C = 100.0 * T_END                # 7.2e8 s
SAT_END = 1.0 - np.exp(-((T_END / T_C) ** ALPHA))

PROV = ("kernel saturante D-H (2026-08-04): as 7 curvas da fonte sao "
        "99,5-99,9 % creep e 6/7 tem o MESMO sinal de residuo (modelo devagar "
        "no inicio, rapido no fim) = curvatura do kernel log-t. alpha e t_c "
        "sao 2 numeros de FORMA fitados no conjunto da fonte (nao ancora de "
        "handbook). C_creep NAO foi refitado: e' o valor per-par anterior "
        "multiplicado pelo fator FECHADO log(t_end/t_0+1)/(1-e^-(t_end/t_c)^a), "
        "que preserva a perda no ponto final -> so a forma mudou. Regime "
        "t_c=100*t_end e' lei de potencia (t_c e C_sat nao separadamente "
        "identificaveis => 1 parametro de forma efetivo). Alternativa "
        "alpha=0.3/t_c=1*t_end fechava 1 curva a mais e foi RECUSADA: "
        "constante de tempo igual a duracao do ensaio.")


def main() -> int:
    d = json.loads(CFG.read_text(encoding="utf-8"))
    print(f"fator de saturacao no fim: 1-exp(-(1/100)^{ALPHA}) = {SAT_END:.6f}")
    plano = {}
    for g in GRUPOS:
        node = d["sources"].get(g)
        if node is None:
            print(f"!! grupo ausente: {g}")
            return 2
        cfg = node["cfg"]
        t0 = float(cfg["t_0"])
        f_log = float(np.log(T_END / t0 + 1.0))
        fator = f_log / SAT_END
        plano[g] = dict(t0=t0, f_log=f_log, fator=fator,
                        C_old=float(cfg["C_creep"]),
                        C_new=float(cfg["C_creep"]) * fator)
        print(f"  {g:26s} t_0={t0:10.2f}  log={f_log:.4f}  "
              f"fator={fator:7.3f}  C {cfg['C_creep']:.6e} -> "
              f"{plano[g]['C_new']:.6e}")
    if "--dry" in sys.argv:
        print("\n--dry: nada escrito")
        return 0

    bkp = CFG.with_suffix(".json.bkp_dh")
    shutil.copy2(CFG, bkp)
    print(f"\nbackup: {bkp.name}")
    for g in GRUPOS:
        cfg = d["sources"][g]["cfg"]
        cfg["C_creep"] = plano[g]["C_new"]
        cfg["creep_mode"] = "saturating"
        cfg["creep_alpha_sat"] = ALPHA
        cfg["creep_t_c"] = T_C
        prov = d["sources"][g].setdefault("prov", {})
        prov["creep_mode"] = PROV
        prov["C_creep"] = (
            f"renormalizado por aritmetica fechada (x{plano[g]['fator']:.3f}) "
            f"a partir do valor per-par anterior {plano[g]['C_old']:.6e}; "
            f"preserva a perda no ponto final. NAO refitado.")
    CFG.write_text(json.dumps(d, indent=1, ensure_ascii=False),
                   encoding="utf-8")
    print("adopted_configs.json escrito")

    # ---- verificacao: re-simular e comparar com o que a sonda mediu --------
    import importlib
    import bolt_analysis_studio.calibration.knowledge_base as kb
    importlib.reload(kb)
    import bolt_analysis_studio.validation.runner as rn
    importlib.reload(rn)
    from bolt_analysis_studio.validation.case_registry import record, all_records

    esperado = None
    probe = json.loads((ROOT / "New_Theory" /
                        "caccese_kernel_creep_exec.json").read_text(
                            encoding="utf-8"))
    for cel in probe["grade"]:
        if abs(cel["alpha"] - ALPHA) < 1e-12 and abs(cel["tc_mult"] - 100.0) < 1e-9:
            esperado = cel["sig"]
    if esperado is None:
        print("!! celula da sonda nao encontrada no JSON")
        return 2
    cids = sorted(r.case_id for r in all_records()
                  if r.source == "CACCESE_2009")
    print("\nverificacao (sigma re-simulado vs sonda):")
    ruim = []
    for c in cids:
        r = rn.simulate_case(record(c))
        if not r.ok:
            print(f"  !! {c}: {r.error}")
            return 2
        exp = esperado.get(c)
        d_ = abs(r.resid_std - exp) if exp is not None else float("nan")
        flag = "OK" if (exp is not None and d_ < 1e-9) else "DIVERGE"
        if flag != "OK":
            ruim.append(c)
        print(f"  {flag:8s} {c:44s} sonda {exp:.6f} agora {r.resid_std:.6f}")
    if ruim:
        print("\n!! ABORTAR — a adocao nao reproduz a sonda. Restaure o backup.")
        return 3
    print("\nadocao CONFIRMADA: reproduz a sonda ao 1e-9 nas 7 curvas.")
    print("Proximo: re-stamp uniforme do store (parallel_batch --store).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
