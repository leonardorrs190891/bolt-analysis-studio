# -*- coding: utf-8 -*-
"""A excecao per-especime da `run2p2` compensa DISPERSAO ou ERRO DE BASE?

## A pergunta

O D-X (2026-08-06) mediu a Fig. 10 do Karlsen contra o impresso e achou que
DUAS curvas — as soterradas no feixe inicial — tem F0 errado no registry:

    run1.2  315 -> 331   (+5,0 %)      run2.2  312 -> 332,7  (+6,6 %)
    run6.2  340 -> 343,4 (+1,0 %) ok   run7.1  312 -> 313,2  (+0,4 %) ok

A `run1.2` foi corrigida e passou a **0,0171 de MAE SEM parametro nenhum**
(roda no config de GRUPO). A `run2.2` NAO foi corrigida e carrega um
`k_ratchet = 0.003` **per-especime**, cuja procedencia diz textualmente:

    "scatter de coating HV medido 3x (PR-11/11b/11c — vidas 195/230/340 a
     312-315 kN NOMINAIS)"

Esses 312-315 kN sao justamente os F0 que o D-X mediu como baixos. Logo a
hipotese: **parte do que foi atribuido a dispersao de especime e' erro de
base**, e a excecao pode ser um curativo.

## O discriminante (1 simulacao, so-leitura)

Rodar a `run2p2` com o config de GRUPO (sem `k_ratchet`) e olhar o **SINAL do
vies**, nao so o MAE:

* A CSV registra `F(N)/315` onde deveria ser `F(N)/331` ⇒ os valores gravados
  sao ~5 % ALTOS ⇒ o modelo parece cair rapido demais ⇒ **vies NEGATIVO**
  (modelo abaixo do dado), aproximadamente uniforme.
* Se o defice que o `k_ratchet` cobre for **vies negativo quase uniforme da
  ordem de 5-6 %**, a hipotese de erro-de-base fica sustentada e vale pagar a
  extracao de pixel.
* Se for defice de FORMA (vies pequeno com resid_std grande, ou vies que troca
  de sinal), a excecao esta medindo outra coisa e a hipotese morre aqui —
  barato.

⚠️ Isto NAO adota nem corrige nada. Decide se a correcao completa (re-leitura
da figura + re-fit/remocao do parametro, com prereg) vale o custo.

    py -3.12 New_Theory/karlsen_run2p2_sonda.py [--json out.json]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import bolt_analysis_studio.validation.runner as rn                # noqa: E402
from bolt_analysis_studio.validation.case_registry import record    # noqa: E402
from bolt_analysis_studio.validation.store import ValidationStore   # noqa: E402

ALVO = "karlsen2022_M30_HV_run2p2"
CONTROLE = "karlsen2022_M30_HV_run7p1"   # F0 CERTO (+0,4 %) e tambem tem k_ratchet
_DROP: set = set()
_orig = rn._effective_overrides


def _patched(rec, base):
    ov = _orig(rec, base)
    if _DROP:
        ov = {k: v for k, v in ov.items() if k not in _DROP}
    return ov


rn._effective_overrides = _patched


def _perfil(r):
    """Vies, seu desvio, e fracao de pontos com o MESMO sinal."""
    p = np.asarray(r.metric_pred, float)
    d = np.asarray(r.metric_data, float)
    res = p - d
    vies = float(np.mean(res))
    return dict(
        n=int(len(res)),
        mae=float(r.mae), mx=float(r.maxerr), sd=float(r.resid_std),
        vies=vies,
        vies_rel=float(vies / np.mean(d)) if np.mean(d) else float("nan"),
        frac_mesmo_sinal=float(np.mean(np.sign(res) == np.sign(vies))),
        cruzamentos=int(np.sum(np.diff(np.sign(res)) != 0)),
        # quanto do erro e' NIVEL (vies) contra FORMA (desvio em torno dele)
        frac_nivel=float(vies ** 2 / (vies ** 2 + float(np.var(res))))
        if (vies ** 2 + float(np.var(res))) else float("nan"),
    )


def _linha(tag, p):
    print(f"  {tag:<26} MAE {p['mae']:.4f}  mx {p['mx']:.4f}  sig {p['sd']:.4f}"
          f"   vies {p['vies']:+.4f} ({p['vies_rel']*100:+.1f} %)"
          f"  mesmo-sinal {p['frac_mesmo_sinal']*100:.0f} %"
          f"  cruz {p['cruzamentos']}  nivel {p['frac_nivel']*100:.0f} %",
          flush=True)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", type=Path)
    a = ap.parse_args()

    st = ValidationStore()
    out: dict = {}

    # instrumento: o k_ratchet TEM de estar chegando, senao "sem efeito" seria
    # lido como "parametro inutil" quando e' "override nunca aplicado".
    ov = rn._effective_overrides(record(ALVO), {})
    kr = ov.get("k_ratchet")
    print(f"instrumento: k_ratchet no override do {ALVO} = {kr}", flush=True)
    assert kr, "k_ratchet NAO chega ao runner — sonda invalida"
    out["k_ratchet_vigente"] = kr

    for cid in (ALVO, CONTROLE):
        print(f"\n=== {cid}", flush=True)
        s = st.get(cid)
        print(f"  store: MAE {s.mae:.4f}  mx {s.maxerr:.4f}  "
              f"sig {s.resid_std:.4f}", flush=True)

        _DROP.clear()
        r_com = rn.simulate_case(record(cid))
        assert r_com.ok, r_com.error
        p_com = _perfil(r_com)
        _linha("COM k_ratchet", p_com)

        _DROP.clear(); _DROP.add("k_ratchet")
        r_sem = rn.simulate_case(record(cid))
        _DROP.clear()
        assert r_sem.ok, r_sem.error
        p_sem = _perfil(r_sem)
        _linha("SEM k_ratchet (grupo)", p_sem)

        out[cid] = dict(store_mae=s.mae, com=p_com, sem=p_sem)

    print()
    print("LEITURA:")
    print("  hipotese ERRO-DE-BASE sustentada se, no run2p2 SEM k_ratchet, o")
    print("  vies for NEGATIVO, |vies_rel| ~ 5-6 %, mesmo-sinal alto e")
    print("  'nivel' dominante. O run7p1 (F0 CERTO) e' o CONTROLE: se ele")
    print("  mostrar o MESMO perfil, o padrao nao discrimina base de especime.")

    if a.json:
        a.json.write_text(json.dumps(out, indent=1), encoding="utf-8")
        print(f"\njson -> {a.json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
