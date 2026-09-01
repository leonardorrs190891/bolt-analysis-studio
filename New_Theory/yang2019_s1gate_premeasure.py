# -*- coding: utf-8 -*-
"""PREMEASURE do `s1_amp_gate` no YANG_2019 — antes do prereg.

## O defeito, medido

`yang2019_freq_sonda_resultado.md`: o modelo cruza 90 % de pre-carga residual
em **N=160 (5 Hz)** e **N=175 (10 Hz)** onde o dado cruza em **1900** e
**4263** — 11x a 25x cedo demais. Isso e' relogio de ESTAGIO I, e foi o que
criou o teto de autoridade do canal de frequencia (dano acumulado nao pode agir
antes de haver dano).

E o dado desta fonte esta BOM: `yang2019_dn_auditoria_resultado.md` conferiu a
`amp0p4_5Hz` contra a lei D-N impressa (d^m N = C, Tabela 5) e ela passa
(1,05 / 0,90). Ou seja, ha ancora independente para o relogio — a consistencia
interna que o LIU_2025 nao tem.

## A capacidade

`stage1_amp_gate` (PR-3, default-inerte): `g = floor + (1-floor) d^p/(d^p+dref^p)`
multiplicando o `d_delta` de **Embedding e Creep**. `dref<=0` => 1.0 exato.

## Pergunta 1 (a que decide se vale seguir)

O gate e' MULTIPLICADOR de canal, nao troca de lei — logo a **decomposicao
decide**: se Embedding+Creep nao carregam a perda ate 90 %, o gate nao alcanca
o alvo por construcao e o candidato morre aqui, barato.

## Pergunta 2

Se carregam, qual celula (dref, p, floor) leva o cruzamento de 90 % para a
faixa do dado SEM estragar as tres pernas nem as outras curvas da fonte.

So'-leitura. Nao adota, nao escreve config, nao toca o store.

    py -3.12 New_Theory/yang2019_s1gate_premeasure.py [--json out.json]
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

FONTE = "YANG_2019"
# N em que o DADO cruza 0,90 (auditoria D-N; None = nao cruza na janela)
ALVO90 = {"yang2019_M10_amp0p6_5Hz": 1900.0,
          "yang2019_M10_amp0p6_10Hz": 4263.0,
          "yang2019_M10_amp0p4_5Hz": 9015.0}
_E: dict = {}
_orig = rn._effective_overrides


def _patched(rec, base):
    ov = _orig(rec, base)
    return {**ov, **_E} if _E else ov


rn._effective_overrides = _patched


def _cruza(x, y, lv=0.90):
    x, y = np.asarray(x, float), np.asarray(y, float)
    if len(y) < 2 or y.min() > lv or y.max() < lv:
        return None
    o = np.argsort(-y)
    return float(np.interp(-lv, -y[o], x[o]))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", type=Path)
    a = ap.parse_args()

    cids = sorted(r.case_id for r in all_records() if r.source == FONTE)
    out: dict = {"decomposicao": {}, "grade": []}

    # ---------- instrumento: o campo chega? --------------------------
    from bolt_analysis_studio.numerical.dynamic_stiffness_analyzer import (
        JointMaterial)
    for f in ("s1_amp_gate_dref", "s1_amp_gate_p", "s1_amp_gate_floor"):
        assert f in JointMaterial.__dataclass_fields__, f"campo {f} ausente"
    _E.clear(); _E["s1_amp_gate_dref"] = 7e-4
    ov = rn._effective_overrides(record(cids[0]), {})
    assert ov.get("s1_amp_gate_dref") == 7e-4, "override NAO chega"
    _E.clear()
    print("instrumento: 3 campos presentes, override chega\n")

    # ---------- PERGUNTA 1: quem carrega a perda ate 90 %? -----------
    print("PERGUNTA 1 — decomposicao ate o cruzamento de 90 %")
    print(f"{'curva':<34}{'N@90 mod':>10}{'N@90 dado':>11}"
          f"{'ec@90%':>11}{'ec@fim':>8}")
    for cid in cids:
        r = rn.simulate_case(record(cid))
        if not r.ok:
            print(f"  !! {cid}: {r.error}"); continue
        n90 = _cruza(r.metric_x, r.metric_pred)
        # `decomp` e' SERIE por mecanismo (perda acumulada), nao escalar.
        # A pergunta e' no cruzamento de 90 %, que e' CEDO: le-se a fatia no
        # indice em que a perda TOTAL atinge 0,10, nao no fim da janela — no
        # fim, emb+creep dao 55 %, mas isso nao responde sobre o inicio.
        dec = getattr(r, "decomp", None)
        frac = frac_fim = None
        if isinstance(dec, dict) and dec:
            arr = {k: np.abs(np.asarray(v, float)) for k, v in dec.items()}
            tot_s = sum(arr.values())
            ec_s = sum(v for k, v in arr.items()
                       if "emb" in k.lower() or "creep" in k.lower())
            if tot_s[-1] > 0:
                frac_fim = float(ec_s[-1] / tot_s[-1])
            i = int(np.argmax(tot_s >= 0.10)) if (tot_s >= 0.10).any() else -1
            if tot_s[i] > 0:
                frac = float(ec_s[i] / tot_s[i])
        print(f"{cid[:34]:<34}"
              f"{(f'{n90:.0f}' if n90 else '--'):>10}"
              f"{(f'{ALVO90[cid]:.0f}' if cid in ALVO90 else '--'):>11}"
              f"{(f'{frac:.1%}' if frac is not None else 'n/d'):>11}"
              f"{(f'{frac_fim:.1%}' if frac_fim is not None else ''):>8}")
        out["decomposicao"][cid] = dict(n90_mod=n90, frac_emb_creep_em90=frac,
                                       frac_emb_creep_fim=frac_fim,
                                       mae=r.mae, mx=r.maxerr,
                                       sd=r.resid_std)
    print()

    # ---------- PERGUNTA 2: grade -----------------------------------
    pisos = None
    print("PERGUNTA 2 — grade (dref em mm, p, floor)")
    print(f"{'dref':>7}{'p':>5}{'floor':>7}   "
          f"{'|'.join(c.split('_M10_')[1][:12] for c in cids)}")
    GRADE = [(d, p, f) for d in (0.3, 0.5, 0.7, 1.0)
             for p in (2.0, 4.0, 8.0) for f in (0.0, 0.1)]
    for dref_mm, p, fl in GRADE:
        cel, pior = [], 0.0
        for cid in cids:
            _E.clear()
            _E.update({"s1_amp_gate_dref": dref_mm * 1e-3,
                       "s1_amp_gate_p": p, "s1_amp_gate_floor": fl})
            r = rn.simulate_case(record(cid))
            _E.clear()
            if not r.ok:
                cel.append("  ERRO"); continue
            n90 = _cruza(r.metric_x, r.metric_pred)
            raz = (n90 / ALVO90[cid]) if (n90 and cid in ALVO90) else None
            cel.append(f"{r.mae:.3f}/{(f'{raz:.1f}' if raz else '-')}")
            pior = max(pior, r.mae)
        print(f"{dref_mm:>7.2f}{p:>5.1f}{fl:>7.2f}   {' | '.join(cel)}")
        out["grade"].append(dict(dref_mm=dref_mm, p=p, floor=fl,
                                 celulas=cel, pior_mae=pior))

    print("\ncelula = MAE / (N@90 do modelo / N@90 do dado). Alvo: razao ~1")
    print("com MAE nao pior que o nominal. Se a razao nao subir com dref, o")
    print("gate nao alcanca — teto de autoridade, e o candidato morre.")
    if a.json:
        a.json.write_text(json.dumps(out, indent=1, default=float),
                          encoding="utf-8")
        print(f"json -> {a.json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
