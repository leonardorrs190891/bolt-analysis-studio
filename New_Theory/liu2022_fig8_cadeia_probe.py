# -*- coding: utf-8 -*-
"""G0 do prereg 2026-08-04 — sonda de DIRECAO na cadeia fig8 do LIU_2022.

Executa o gate G0: sonda de **2 pontos** por candidato, para fixar o SINAL da
resposta antes de qualquer bissecao. Nao decide adocao; decide direcao.

## O que esta sonda mede que o MAE nao mede

O defeito da cadeia e' de FORMA ENTRE ESTAGIOS: a retencao final do dado cai
monotonicamente a cada reaperto (0.978 -> 0.960 -> 0.921 -> 0.845, vao 0.133)
e a do modelo e' plana e sobe no fim (0.890/0.888/0.890/0.930, vao 0.042).
Entao a sonda imprime, para cada dose, a **sequencia de retencao final** e o
**vao** — que sao o gate G1 — junto com as 3 pernas.

## Armadilhas ja pagas que esta sonda evita

* `k_wear_scale_tr` e' chave de CFG, nao campo do engine (traduz para
  K_archard/k_wear_spec). Injeta-la morreria no filtro do JointMaterial EM
  SILENCIO. O campo real, lido de `_effective_overrides`, e' `k_wear_spec`
  (3e-15) — e o `K_archard` do cfg e' a via LEGADA, que `k_wear_spec>0`
  sobrepoe.
* Delta = 0.0000 exato **nao** autoriza "alavanca morta" sem conferir os
  companheiros do canal (3 leituras erradas em 2026-08-01/02).
* O baseline e' RE-SIMULADO e comparado com o store: sem isso, um teto de
  simulacao diferente faria a metrica "melhorar" sozinha (erro medido em
  2026-07-30, que produziu um "7 curvas fecham" 100% artefato).

    py -3.12 New_Theory/liu2022_fig8_cadeia_probe.py [--json saida.json]
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import bolt_analysis_studio.validation.report_html as rh          # noqa: E402
import bolt_analysis_studio.validation.runner as rn               # noqa: E402
from bolt_analysis_studio.validation.case_registry import (       # noqa: E402
    all_records, record)
from bolt_analysis_studio.validation.store import ValidationStore  # noqa: E402

CIDS = [f"liu2022_fig8_multi_t{k}" for k in range(5)]

_EXTRA: dict = {}
_orig = rn._effective_overrides
rn._effective_overrides = lambda rec, base: {**_orig(rec, base), **_EXTRA}


def _sim(cid: str, ov: dict):
    _EXTRA.clear()
    _EXTRA.update(ov)
    try:
        return rn.simulate_case(record(cid))
    finally:
        _EXTRA.clear()


def _perfil(ov: dict) -> dict:
    """Simula os 5 estagios e devolve as pernas + a forma entre estagios."""
    fin, mae, sig, mx = {}, {}, {}, {}
    for cid in CIDS:
        r = _sim(cid, ov)
        if not r.ok:
            return {"erro": f"{cid}: {r.error}"}
        mp = np.asarray(r.metric_pred, float)
        fin[cid] = float(mp[-1])
        mae[cid] = float(r.mae)
        sig[cid] = float(r.resid_std)
        mx[cid] = float(r.maxerr)
    seq = [fin[c] for c in CIDS[1:]]                  # t1..t4 (G1 e' sobre eles)
    dec = all(seq[i] > seq[i + 1] for i in range(len(seq) - 1))
    return dict(fin=fin, mae=mae, sig=sig, mx=mx, seq=seq,
                vao=float(max(seq) - min(seq)), decrescente=bool(dec))


# candidato -> (campo do ENGINE, valor vigente, dose baixa, dose alta, papel)
CAND = [
    ("k_wear_spec",  3e-15, 1.5e-15, 6e-15, "perda de linha de base (wear)"),
    ("emb_depth",    4e-6,  2e-6,    8e-6,  "assentamento por estagio"),
    ("k_emb_renew",  1.0,   0.3,     1.0,   "renovacao do embedding no reaperto"),
    ("c_D",          0.5,   0.2,     2.0,   "taxa de crescimento do DANO (acumula)"),
    ("k_dmg_wear",   1.0,   0.3,     4.0,   "dano amplifica wear (acumula)"),
]


def main() -> int:
    st = ValidationStore()
    pares = [(r.source, st.get(r.case_id)) for r in all_records()
             if st.get(r.case_id) is not None]
    lim = float(rh.limite_sres("LIU_2022_RETIGHT", rh._pisos_medidos(pares)))

    print("G0 — SONDA DE DIRECAO, cadeia fig8 do LIU_2022")
    print(f"  limite sigma da fonte: {lim:.4f} · META_MAE {rh.META_MAE} "
          f"· META_MAX {rh.META_MAX}")
    dado = [float(np.asarray(st.get(c).metric_data, float)[-1]) for c in CIDS]
    print(f"  DADO, retencao final t0..t4: "
          + " ".join(f"{v:.4f}" for v in dado))
    print(f"  DADO, vao t1..t4: {max(dado[1:]) - min(dado[1:]):.4f} "
          f"(decrescente: {all(dado[1:][i] > dado[1:][i+1] for i in range(3))})\n")

    # ---- instrumento: o baseline re-simulado tem de reproduzir o store ------
    base = _perfil({})
    assert "erro" not in base, base
    ruim = []
    for c in CIDS:
        s = st.get(c)
        if abs(base["mae"][c] - s.mae) > 1e-9 or abs(base["sig"][c] - s.resid_std) > 1e-9:
            ruim.append((c, s.mae, base["mae"][c], s.resid_std, base["sig"][c]))
    if ruim:
        print("!! INSTRUMENTO REPROVADO — baseline re-simulado != store:")
        for c, a, b, x, y in ruim:
            print(f"   {c}: mae {a:.4f}->{b:.4f}  sigma {x:.4f}->{y:.4f}")
        print("   (sem isto qualquer 'melhora' pode ser teto/janela, nao fisica)")
        return 2
    print("instrumento OK — baseline re-simulado bate com o store ao 1e-9")
    print(f"  MODELO, retencao final t0..t4: "
          + " ".join(f"{base['fin'][c]:.4f}" for c in CIDS))
    print(f"  MODELO, vao t1..t4: {base['vao']:.4f} "
          f"(decrescente: {base['decrescente']})\n")

    out = {"lim_sd": lim, "dado_final": dado, "base": base, "cand": {}}
    for campo, atual, lo, hi, papel in CAND:
        print(f"--- {campo}  (vigente {atual:g})  ·  {papel}")
        linhas = []
        for dose in (lo, hi):
            if dose == atual:
                print(f"    dose {dose:g}: = vigente, pulada")
                continue
            p = _perfil({campo: dose})
            if "erro" in p:
                print(f"    dose {dose:g}: ERRO {p['erro']}")
                continue
            d_mae = {c: p["mae"][c] - base["mae"][c] for c in CIDS}
            d_sig = {c: p["sig"][c] - base["sig"][c] for c in CIDS}
            inerte = (max(abs(v) for v in d_mae.values()) < 1e-9
                      and max(abs(v) for v in d_sig.values()) < 1e-9)
            fecha = sum(1 for c in CIDS
                        if p["mae"][c] <= rh.META_MAE and p["mx"][c] <= rh.META_MAX
                        and p["sig"][c] <= lim)
            print(f"    dose {dose:g}: vao {p['vao']:.4f} "
                  f"decr={str(p['decrescente']):5s} fecham {fecha}/5"
                  f"{'   << INERTE (Delta=0 exato)' if inerte else ''}")
            print("        final t0..t4: "
                  + " ".join(f"{p['fin'][c]:.4f}" for c in CIDS))
            print("        d(MAE)      : "
                  + " ".join(f"{d_mae[c]:+.4f}" for c in CIDS))
            print("        d(sigma)    : "
                  + " ".join(f"{d_sig[c]:+.4f}" for c in CIDS))
            linhas.append(dict(dose=dose, vao=p["vao"], decr=p["decrescente"],
                               fecham=fecha, inerte=inerte,
                               fin=[p["fin"][c] for c in CIDS],
                               mae=[p["mae"][c] for c in CIDS],
                               sig=[p["sig"][c] for c in CIDS],
                               mx=[p["mx"][c] for c in CIDS]))
        out["cand"][campo] = linhas
        print()

    print("LEITURA — o que o G0 autoriza:")
    for campo, linhas in out["cand"].items():
        if not linhas:
            continue
        if all(x["inerte"] for x in linhas):
            print(f"  {campo:14s} INERTE nas 2 doses -> NAO conclua 'morto': "
                  f"confira companheiros do canal antes.")
            continue
        vaos = [x["vao"] for x in linhas]
        sinal = ("aumenta o vao" if vaos[-1] > base["vao"] else "reduz o vao")
        print(f"  {campo:14s} vao {base['vao']:.4f} -> "
              + "/".join(f"{v:.4f}" for v in vaos) + f"  ({sinal})")

    if "--json" in sys.argv:
        dest = Path(sys.argv[sys.argv.index("--json") + 1])
        dest.write_text(json.dumps(out, indent=1), encoding="utf-8")
        print(f"\ngravado: {dest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
