# -*- coding: utf-8 -*-
"""As 10 curvas ESPELHADO sao UMA classe? — assinatura de relogio de Estagio I.

## De onde vem a pergunta

`classe_parada_discriminante_resultado.md` achou **10 curvas ESPELHADO** (modelo
ABAIXO do dado no fim: desaba cedo) entre as 23 estacionadas em `classe_parada`.
`yang2019_s1gate_resultado.md` diagnosticou UMA delas com precisao:

* o modelo cruza 90 % **11x a 25x cedo**;
* no cruzamento, **100 % da perda e' Embedding+Creep**;
* o `s1_amp_gate` tem autoridade plena mas **nao depende de frequencia**, e o
  par 0,6 mm a 5/10 Hz mostra que o defeito depende;
* logo a forma que falta e' **frequencia nos relogios de Estagio I**.

Se as outras 9 tiverem a MESMA assinatura, a forma faltante cobre uma CLASSE, e
a decisao de implementa-la passa a ter numero. Se nao, sao defeitos distintos
que o rotulo ESPELHADO agrupou por acidente de sinal.

## As duas assinaturas medidas

1. **relogio**: N em que o MODELO cai a 90 % contra N em que o DADO cai a 90 %
   (razao << 1 = modelo cedo demais);
2. **autoridade**: fatia de Embedding+Creep na perda acumulada NO PONTO em que
   o modelo perde 10 % — nao no fim da janela (a leitura no fim da' 55-94 % e
   engana; ver o resultado do YANG_2019).

So'-leitura. Nao adota, nao escreve nada.

    py -3.12 New_Theory/espelhado_classe_assinatura.py [--json out.json]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import bolt_analysis_studio.validation.runner as rn                  # noqa: E402
from bolt_analysis_studio.validation import report_html as rh        # noqa: E402
from bolt_analysis_studio.validation.case_registry import (          # noqa: E402
    all_records, record)
from bolt_analysis_studio.validation.runner import CaseResult        # noqa: E402

STORE = (ROOT / "Models" / "CALIBRATION_AND_VALIDATION"
         / "validation_store.json")
# as 10 ESPELHADO do discriminante (vies terminal < 0)
ESPELHADO = [
    "chu2026ti_D0p5mm_F0_49kN_test3",
    "liu2025_M16_amp0p25", "liu2025_M16_amp0p3", "liu2025_M16_amp0p8",
    "lu2024_M8_fig14_amp0p5_long", "lu2024_M8_fig14_amp1p0_long",
    "sun2025efa109235_transverse_grease_crimp",
    "sun2025efa109235_transverse_grease_standard",
    "yang2019_M10_amp0p4_5Hz", "yang2019_M10_amp0p6_10Hz",
]
# controle: 3 CLASSE (vies terminal > 0) — a assinatura tem de DIFERIR nelas
CONTROLE = ["yang2021_amp0p5mm_ax8kN", "yang2019_M10_varamp_small_to_large",
            "jcsr2023_galv_seawater"]


def _cruza(x, y, lv):
    x, y = np.asarray(x, float), np.asarray(y, float)
    if len(y) < 2 or y.min() > lv or y.max() < lv:
        return None
    o = np.argsort(-y)
    return float(np.interp(-lv, -y[o], x[o]))


def _assina(r, lv=0.90):
    """(razao de relogio, fatia emb+creep no ponto de 10 % de perda)."""
    nm = _cruza(r.metric_x, r.metric_pred, lv)
    nd = _cruza(r.metric_x, r.metric_data, lv)
    raz = (nm / nd) if (nm and nd) else None
    frac = None
    dec = getattr(r, "decomp", None)
    if isinstance(dec, dict) and dec:
        arr = {k: np.abs(np.asarray(v, float)) for k, v in dec.items()}
        tot = sum(arr.values())
        ec = sum(v for k, v in arr.items()
                 if "emb" in k.lower() or "creep" in k.lower())
        if (tot >= 1.0 - lv).any():
            i = int(np.argmax(tot >= 1.0 - lv))
            if tot[i] > 0:
                frac = float(ec[i] / tot[i])
    return nm, nd, raz, frac


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", type=Path)
    a = ap.parse_args()

    store = json.loads(STORE.read_text(encoding="utf-8"))
    recs = {r.case_id: r for r in all_records()}
    out = {}
    for titulo, lista in (("ESPELHADO (10)", ESPELHADO),
                          ("CONTROLE — classe (3)", CONTROLE)):
        print(f"\n=== {titulo}")
        print(f"{'curva':<42}{'N90 mod':>9}{'N90 dado':>10}{'razao':>8}"
              f"{'ec@10%':>9}  leitura")
        for cid in lista:
            if cid not in recs:
                print(f"{cid[:42]:<42}  nao existe"); continue
            r = rn.simulate_case(record(cid))
            if not r.ok:
                print(f"{cid[:42]:<42}  erro: {r.error}"); continue
            nm, nd, raz, frac = _assina(r)
            if raz is None:
                lei = "sem cruzamento de 90 %"
            elif raz <= 0.5 and (frac or 0) >= 0.80:
                lei = "MESMA assinatura (relogio E1)"
            elif raz <= 0.5:
                lei = f"relogio cedo, mas ec={frac:.0%}" if frac else "relogio cedo"
            else:
                lei = "relogio OK -> outro defeito"
            print(f"{cid[:42]:<42}"
                  f"{(f'{nm:.0f}' if nm else '--'):>9}"
                  f"{(f'{nd:.0f}' if nd else '--'):>10}"
                  f"{(f'{raz:.2f}' if raz else '--'):>8}"
                  f"{(f'{frac:.0%}' if frac is not None else 'n/d'):>9}"
                  f"  {lei}")
            out[cid] = dict(grupo=titulo, n90_mod=nm, n90_dado=nd,
                            razao=raz, ec_em_10pct=frac, leitura=lei)
    n_mesma = sum(1 for k, v in out.items()
                  if v["grupo"].startswith("ESPELHADO")
                  and v["leitura"].startswith("MESMA"))
    print(f"\ncurvas ESPELHADO com a assinatura do YANG_2019: "
          f"{n_mesma} de {len(ESPELHADO)}")
    print("LEITURA: razao <= 0,5 (modelo cai a 90 % em menos da metade dos")
    print("ciclos do dado) E ec >= 80 % no ponto => o defeito e' o relogio de")
    print("Estagio I e a autoridade esta em Embedding/Creep. O CONTROLE tem de")
    print("diferir: se as 3 'classe' mostrarem a mesma coisa, a assinatura nao")
    print("discrimina e a conclusao nao vale.")
    out["_n_mesma_assinatura"] = n_mesma
    if a.json:
        a.json.write_text(json.dumps(out, indent=1, default=float),
                          encoding="utf-8")
        print(f"json -> {a.json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
