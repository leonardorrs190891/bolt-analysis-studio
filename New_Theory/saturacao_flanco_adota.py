# -*- coding: utf-8 -*-
"""Adocao D-Q — SATURACAO DO CANAL DE FLANCO por profundidade restante.

    d_w *= max(0, 1 - state.delta_thread_fret / flank_fret_depth)

Mesma estrutura state-based que o `EmbeddingLoss` recebeu em 2026-07-02: o
incremento depende da profundidade que AINDA FALTA, nao do relogio. E fecha um
laco que estava aberto: `delta_thread_fret` era acumulado (engine linha 1853) e
lido SO para contabilidade de energia (linha 2374) — nunca realimentava a lei.

Fisica: o fretting de flanco remove material ate a folga acomodar o movimento;
entao o contato re-conforma, a area cresce, a pressao cai e o transporte liquido
para. Regime de SHAKEDOWN que o docstring de `flank_wear_from_slip` ja citava
(Mantyla 2020 / Juoksukangas 2016).

O valor e' COMPARTILHADO entre as duas fontes que tem o canal de flanco ativo —
`LI_2022_TRIBOINT` (alvo) e `LIU_2016` (held-out cego, 14/14 no tripe). E' essa
transferencia que o G1 do prereg decide.

    py -3.12 New_Theory/saturacao_flanco_adota.py --dep 2.5e-6 [--dry]
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

CFG = ROOT / "New_Theory" / "adopted_configs.json"
# grupos com o canal de flanco ATIVO (flank_wear_on) — os dois recebem o MESMO valor
GRUPOS = ("LI_2022_TRIBOINT", "LIU_2016")

PROV_TPL = (
    "SATURACAO DO CANAL DE FLANCO (D-Q, 2026-08-05; prereg "
    "2026-08-05-saturacao-flanco). Forma state-based: "
    "d_w *= max(0, 1 - delta_thread_fret/flank_fret_depth) — o incremento "
    "depende da profundidade que AINDA FALTA, nao do relogio. Mesma estrutura "
    "que o EmbeddingLoss recebeu em 2026-07-02, e fecha um laco que estava "
    "aberto: `delta_thread_fret` era acumulado (engine linha 1853) e lido SO "
    "para energia (linha 2374), nunca realimentava a lei que o alimenta. "
    "Fisica: o fretting remove material ate a folga acomodar o movimento; o "
    "contato re-conforma, a area cresce, a pressao cai, o transporte liquido "
    "para (regime de SHAKEDOWN, ja citado no docstring de "
    "flank_wear_from_slip: Mantyla 2020 / Juoksukangas 2016). "
    "VALOR = {dep:.3e} m ({dep_um:.2f} um), COMPARTILHADO entre as duas fontes "
    "com o canal ativo. Escala: comparavel ao emb_depth=9,5 um da tabela VDI "
    "para este rig — a escala de rugosidade da interface, onde o fretting de "
    "flanco opera. Otimo INTERIOR (grade varrida 4e-5 .. 1e-6; sigma da "
    "`full` cai monotonicamente de 0,0365 ate ~0,0214 e o MAE degrada abaixo "
    "de ~2e-6). "
    "MOTIVACAO MEDIDA: a `li2022ti_axial_10Hz_full` tinha o dado SATURANDO e o "
    "modelo nao — residuo +0,0466 em 20k, cruzando zero em 200k, -0,0441 em "
    "330k, com 49,7 % da variancia nos 2 pontos tardios. "
    "⚠️ NAO combinar com re-atribuicao creep->flanco: o teto em PARES mostrou "
    "ANTI-SINERGIA (a razao de frequencia 20Hz/10Hz degrada de 0,529 para "
    "0,593->0,814 conforme a saturacao aperta, porque o sinal de frequencia "
    "esta na MAGNITUDE do flanco e a saturacao a corta). Ver "
    "li2022_reatribuicao_resultado.md. "
    "⚠️ LIMITE DECLARADO: a `axialmin_10Hz` piora monotonicamente (MAE 0,0526 "
    "-> {mae10:.4f}, dentro da tolerancia) — ela e' MAE-bound e precisa de MAIS "
    "perda, enquanto a `full` e' sigma-bound e precisa de MENOS perda tardia. "
    "Duas curvas do MESMO ensaio com demandas opostas; nenhuma profundidade "
    "serve as duas, e a fonte fica em 3/4.")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dep", type=float, required=True,
                    help="flank_fret_depth em metros (ex.: 2.5e-6)")
    ap.add_argument("--mae10", type=float, default=0.0589,
                    help="MAE resultante da axialmin_10Hz, p/ o prov")
    ap.add_argument("--dry", action="store_true")
    a = ap.parse_args()

    d = json.loads(CFG.read_text(encoding="utf-8"))
    for g in GRUPOS:
        if g not in d["sources"]:
            print(f"!! grupo ausente: {g}")
            return 2
        if not d["sources"][g]["cfg"].get("flank_wear_on"):
            print(f"!! {g} nao tem flank_wear_on — a saturacao seria inerte")
            return 2
    print(f"adotando flank_fret_depth = {a.dep:.3e} m ({a.dep*1e6:.2f} um) "
          f"nos grupos {GRUPOS}")
    if a.dry:
        print("--dry: nada escrito")
        return 0

    shutil.copy2(CFG, CFG.with_suffix(".json.bkp_dq"))
    prov = PROV_TPL.format(dep=a.dep, dep_um=a.dep * 1e6, mae10=a.mae10)
    for g in GRUPOS:
        d["sources"][g]["cfg"]["flank_fret_depth"] = a.dep
        d["sources"][g].setdefault("prov", {})["flank_fret_depth"] = prov
    CFG.write_text(json.dumps(d, indent=1, ensure_ascii=False), encoding="utf-8")
    print("adopted_configs.json escrito · backup adopted_configs.json.bkp_dq")

    import importlib
    import bolt_analysis_studio.calibration.knowledge_base as kb
    importlib.reload(kb)
    import bolt_analysis_studio.validation.runner as rn
    importlib.reload(rn)
    from bolt_analysis_studio.validation.case_registry import record, all_records
    from bolt_analysis_studio.validation.store import ValidationStore

    st = ValidationStore()
    alvo = sorted(r.case_id for r in all_records()
                  if r.source in ("LI_2022_TRIBOINT", "LIU_2016"))
    print(f"\nverificacao nas {len(alvo)} curvas das duas fontes:")
    entrou, saiu, pior = [], [], []
    for cid in alvo:
        r = rn.simulate_case(record(cid))
        if not r.ok:
            print(f"  !! {cid}: {r.error}")
            return 2
        s = st.get(cid)
        tb = (s.mae <= 0.05 and s.maxerr <= 0.10 and s.resid_std <= 0.025)
        ta = (r.mae <= 0.05 and r.maxerr <= 0.10 and r.resid_std <= 0.025)
        if ta and not tb:
            entrou.append(cid)
        if tb and not ta:
            saiu.append(cid)
        dm = max(r.mae - s.mae, r.maxerr - s.maxerr, r.resid_std - s.resid_std)
        if dm > 0.010:
            pior.append((cid, round(dm, 4)))
        marca = "  <= ENTROU" if (ta and not tb) else (
            "  << SAIU" if (tb and not ta) else "")
        print(f"  {'OK ' if ta else 'FORA'} {cid[:36]:36s} "
              f"mae {s.mae:.4f}->{r.mae:.4f} sig {s.resid_std:.4f}->"
              f"{r.resid_std:.4f}{marca}")
    print(f"\n  entraram: {[c[-16:] for c in entrou] or 'nenhuma'}")
    print(f"  sairam:   {[c[-16:] for c in saiu] or 'nenhuma'}")
    print(f"  pior >+0.010: {pior or 'nenhuma'}")
    if saiu or pior:
        print("\n!! ABORTAR — gate violado. Restaure o backup .bkp_dq.")
        return 3
    print("\nADOCAO CONFIRMADA. Proximo: re-stamp uniforme do store.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
