# -*- coding: utf-8 -*-
"""O modelo reproduz a razao de VIDA entre 5 Hz e 10 Hz do YANG_2019?

## O que a auditoria da lei D-N encontrou

As duas curvas de 0,6 mm do YANG_2019 diferem so' na frequencia e cruzam 90 %
de pre-carga residual em **1900 ciclos (5 Hz)** e **4263 ciclos (10 Hz)** —
razao medida **2,24x** (`yang2019_dn_auditoria_resultado.md`).

## Por que isso e' um teste, e nao so' uma curiosidade

Se a perda for governada por **TEMPO** e nao por ciclo, dobrar a frequencia
dobra a vida em ciclos: razao **2,00x** exata. E esse expoente esta ADOTADO em
DUAS fontes independentes, por canais DIFERENTES:

* `YANG_2019`: `dmg_dwell_exp = 1.0` com `f_ref_dmg = 10.0` (dano por dwell);
* `LI_2022_TRIBOINT`: `fret_freq_exp = 1.0` (fretting de flanco, adocao D-V).

A P-1 registrou como custo do D-V que *"nao existe held-out — o unico outro
grupo com canal de flanco e' de frequencia unica"*. Esta sonda pergunta se o
canal do YANG (outro mecanismo, outro rig) entrega a razao medida.

## Ramos

* razao do MODELO em [2,0 ; 2,5]  => reproduz; o par vira corroboracao FORTE
  da familia 1/f, ainda que por canal diferente;
* razao ~1,0                      => o canal de frequencia esta INERTE aqui, e
  o `dmg_dwell_exp` adotado nao age (checar companheiros antes de concluir);
* razao muito fora               => o expoente 1,0 nao serve a esta fonte.

⚠️ Nao e' held-out formal e a sonda nao o transforma em um: n=1 de cada lado,
canais distintos, e a comparacao e' de VIDA, nao de trajetoria.

    py -3.12 New_Theory/yang2019_freq_sonda.py [--json out.json]
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
from bolt_analysis_studio.validation.case_registry import record      # noqa: E402

PAR = {"5Hz": "yang2019_M10_amp0p6_5Hz", "10Hz": "yang2019_M10_amp0p6_10Hz"}
DADO = {"5Hz": 1900.0, "10Hz": 4263.0}      # N em ratio 0,90, da auditoria D-N
NIVEIS = (0.90, 0.85, 0.80)


def _cruza(x, y, lv):
    x, y = np.asarray(x, float), np.asarray(y, float)
    if y.min() > lv or y.max() < lv:
        return None
    o = np.argsort(-y)
    return float(np.interp(-lv, -y[o], x[o]))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", type=Path)
    a = ap.parse_args()

    out = {}
    # instrumento: o canal de frequencia CHEGA e esta ligado?
    for k, cid in PAR.items():
        rec = record(cid)
        ov = rn._effective_overrides(rec, {})
        f = getattr(rec.validation_case, "frequency_Hz", None)
        print(f"{k:>5}  freq={f}  dmg_dwell_exp={ov.get('dmg_dwell_exp')}"
              f"  f_ref_dmg={ov.get('f_ref_dmg')}  c_D={ov.get('c_D')}",
              flush=True)
        out.setdefault("instrumento", {})[k] = dict(
            freq=f, dmg_dwell_exp=ov.get("dmg_dwell_exp"),
            f_ref_dmg=ov.get("f_ref_dmg"), c_D=ov.get("c_D"))
    assert out["instrumento"]["5Hz"]["freq"] != \
        out["instrumento"]["10Hz"]["freq"], "as duas tem a MESMA frequencia"

    print("\nsimulando o par...", flush=True)
    sim = {}
    for k, cid in PAR.items():
        r = rn.simulate_case(record(cid))
        assert r.ok, f"{cid}: {r.error}"
        sim[k] = r
        print(f"  {k:>5}  MAE {r.mae:.4f}  mx {r.maxerr:.4f}"
              f"  sig {r.resid_std:.4f}   n={len(r.metric_x)}", flush=True)

    print(f"\n{'nivel':>7}{'N mod 5Hz':>11}{'N mod 10Hz':>12}"
          f"{'razao mod':>11}{'razao dado':>12}")
    razoes = []
    for lv in NIVEIS:
        n5 = _cruza(sim["5Hz"].metric_x, sim["5Hz"].metric_pred, lv)
        n10 = _cruza(sim["10Hz"].metric_x, sim["10Hz"].metric_pred, lv)
        raz = (n10 / n5) if (n5 and n10) else None
        # razao do DADO no mesmo nivel, dos vetores da metrica
        d5 = _cruza(sim["5Hz"].metric_x, sim["5Hz"].metric_data, lv)
        d10 = _cruza(sim["10Hz"].metric_x, sim["10Hz"].metric_data, lv)
        rd = (d10 / d5) if (d5 and d10) else None
        print(f"{lv:>7.2f}{(f'{n5:.0f}' if n5 else '--'):>11}"
              f"{(f'{n10:.0f}' if n10 else '--'):>12}"
              f"{(f'{raz:.2f}' if raz else '--'):>11}"
              f"{(f'{rd:.2f}' if rd else '--'):>12}")
        if raz:
            razoes.append(raz)
        out.setdefault("niveis", []).append(
            dict(nivel=lv, n_mod_5=n5, n_mod_10=n10, razao_mod=raz,
                 razao_dado=rd))

    print(f"\nrazao do DADO a 90 % pela auditoria D-N (curva crua): "
          f"{DADO['10Hz']/DADO['5Hz']:.2f}x")
    if razoes:
        m = float(np.median(razoes))
        print(f"razao MEDIANA do modelo: {m:.2f}x")
        if 2.0 <= m <= 2.5:
            v = "REPRODUZ (corroboracao da familia 1/f)"
        elif m < 1.15:
            v = "CANAL INERTE (o dmg_dwell_exp nao age aqui)"
        else:
            v = "FORA da banda"
        print(f"veredicto: {v}")
        out["razao_mediana_modelo"] = m
        out["veredicto"] = v
    if a.json:
        a.json.write_text(json.dumps(out, indent=1, default=float),
                          encoding="utf-8")
        print(f"json -> {a.json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
