# -*- coding: utf-8 -*-
"""Adocao D-V (P-1 ASSINADO, 2026-08-06) — fret_freq_exp = 1,0 no LI_2022.

Assinatura do professor em sessao, com a margem de 0,4% na mesa. Ver o registro
em docs/superpowers/specs/2026-08-06-li2022-fret-freq-adocao.md.

    py -3.12 New_Theory/li2022_fret_freq_adota.py [--dry]

Sem pipe (o executor escreve antes de verificar).
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
GRUPO = "LI_2022_TRIBOINT"
VALOR = 1.0
# predicoes registradas (varredura 2026-08-05, celula exp=1,00; +-0,02/perna)
PREV = {
    "li2022ti_axial_10Hz_full":  (0.0217, None, 0.0249),
    "li2022ti_axialmin_10Hz":    (0.0481, None, 0.0215),
    "li2022ti_axialmin_15Hz":    (0.0323, 0.0497, 0.0166),   # inalterada (pivo)
    "li2022ti_axialmin_20Hz":    (0.0110, None, 0.0140),
}
PROV = (
    "LEI DE FREQUENCIA DO FRETTING DE FLANCO (D-V, ASSINADA pelo professor em "
    "2026-08-06; registro 2026-08-06-li2022-fret-freq-adocao). "
    "fret_freq_exp = 1,0 => taxa de fretting proporcional a 1/f: desgaste por "
    "unidade de TEMPO, nao por ciclo (ejecao de detritos e oxidacao sao "
    "processos temporais). E' o expoente que o DADO pede independentemente "
    "(a = 1,006 no par 10-20 Hz; 0,978 global; banda [0,603..1,415] EXCLUI "
    "zero) — duas derivacoes independentes apontam 1. Janela viavel medida "
    "[0,85..1,02] fecha a fonte em 4/4; o valor derivado 3,57 foi FALSIFICADO "
    "por gate (li2022_fret_freq_exp_resultado.md). "
    "⚠️ DECLARADO NA ASSINATURA: constante PER-FONTE SEM HELD-OUT — o unico "
    "outro grupo com canal de flanco (LIU_2016) e' de frequencia UNICA, entao "
    "a lei so e' observavel nesta fonte; a regra de transferencia foi "
    "conscientemente relaxada AQUI por assinatura (P-1 da fila). "
    "⚠️ MARGEM ACEITA: sigma da axial_10Hz_full fica a 0,4% do limite "
    "(0,0249 vs 0,025). "
    "⚠️ NAO combinar com re-atribuicao creep->flanco (anti-sinergia medida).")


def _tri(m, x, s):
    return m <= 0.05 and x <= 0.10 and s <= 0.025


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true")
    a = ap.parse_args()

    d = json.loads(CFG.read_text(encoding="utf-8"))
    cfg = d["sources"][GRUPO]["cfg"]
    print(f"{GRUPO}: fret_freq_exp atual = {cfg.get('fret_freq_exp')!r} -> {VALOR}")
    assert cfg.get("flank_wear_on"), "canal de flanco desligado?!"
    if a.dry:
        print("--dry: nada escrito")
        return 0

    shutil.copy2(CFG, CFG.with_suffix(".json.bkp_dv"))
    cfg["fret_freq_exp"] = VALOR
    d["sources"][GRUPO].setdefault("prov", {})["fret_freq_exp"] = PROV
    CFG.write_text(json.dumps(d, indent=1, ensure_ascii=False), encoding="utf-8")
    print("config escrito · backup adopted_configs.json.bkp_dv")

    import importlib
    import bolt_analysis_studio.calibration.knowledge_base as kb
    importlib.reload(kb)
    import bolt_analysis_studio.validation.runner as rn
    importlib.reload(rn)
    from bolt_analysis_studio.validation.case_registry import all_records, record
    from bolt_analysis_studio.validation.store import ValidationStore

    v = kb.adopted_config(GRUPO)["cfg"].get("fret_freq_exp")
    print(f"kb le fret_freq_exp = {v!r}")
    if v != VALOR:
        print("!! kb NAO le o valor — ABORTAR (restaure o backup)")
        return 2

    st = ValidationStore()
    print("\nG1 — as 4 do LI_2022 contra as predicoes (+-0,02/perna):")
    falha = []
    for cid, (pm, px, ps) in PREV.items():
        r = rn.simulate_case(record(cid))
        if not r.ok:
            print(f"  !! {cid}: {r.error}")
            return 2
        b = st.get(cid)
        ok = abs(r.mae - pm) <= 0.02 and abs(r.resid_std - ps) <= 0.02 and \
             (px is None or abs(r.maxerr - px) <= 0.02) and r.maxerr <= 0.10
        if not ok:
            falha.append(cid)
        tri = _tri(r.mae, r.maxerr, r.resid_std)
        print(f"  {cid[9:]:22s} mae {b.mae:.4f}->{r.mae:.4f} (prev {pm:.4f})  "
              f"mx {r.maxerr:.4f}  sig {b.resid_std:.4f}->{r.resid_std:.4f} "
              f"(prev {ps:.4f})  {'TRIPE' if tri else 'fora'}"
              f"{'' if ok else '   << FORA DA PREDICAO'}")

    print("\nG2 — isolamento estrutural: re-sim de 2 curvas do LIU_2016 "
          "(o outro grupo com canal de flanco):")
    for cid in ("liu2016wear_fig7_run2_5e6cyc", "liu2016wear_fig13a_mos2"):
        r = rn.simulate_case(record(cid))
        b = st.get(cid)
        idem = (abs(r.mae - b.mae) < 1e-12 and abs(r.maxerr - b.maxerr) < 1e-12
                and abs(r.resid_std - b.resid_std) < 1e-12)
        print(f"  {cid[9:]:24s} {'bit-identica' if idem else 'MUDOU << G2 VIOLADO'}")
        if not idem:
            falha.append(cid)

    if falha:
        print(f"\n!! INCONCLUSIVO — fora da predicao/isolamento: {falha}")
        print("   Restaure adopted_configs.json.bkp_dv e investigue.")
        return 3
    print("\nADOCAO CONFIRMADA no G1/G2. Proximo: re-stamp uniforme dos 210 "
          "(batch + exemplo_m12 direto) + censo/docs/suite no MESMO commit.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
