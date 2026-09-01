# -*- coding: utf-8 -*-
"""Executor do prereg D-F (2026-08-04) — `k_emb_renew` por PROTOCOLO.

Claim: reaperto que NAO solta o parafuso (direto/multi) nao re-assenta a
interface, logo `delta_emb` nao renova => `k_emb_renew < 1`. Reaperto que
solta 30-60 graus (release) re-assenta => fica 1.0.

Estrutura do teste (a chave do prereg): o X e' aplicado a DOIS protocolos que
nao soltam, em lubrificacoes DIFERENTES —

  · fig8_multi (dry, 5 curvas)  = ALVO (t1/t2 estao na fila)
  · fig7a_oil_direct (oil, 4)   = HELD-OUT (as 4 estao no tripe hoje)

...e NAO e' aplicado aos que soltam (fig6a/fig6b) nem ao virgem (fig5), que
sao o controle bit-identico. Se X ajuda a fig8 e atrapalha a fig7a, a claim
"e' o protocolo" esta falsificada e o numero e' fit de uma figura.

G0 do prereg: adotar o MAIOR X que feche t1 e t2 — proibido escolher o de
menor MAE (o t1 precisa de -0.0033 de MAE; a dose 0.3 entrega -0.0274).

    py -3.12 New_Theory/liu2022_emb_renew_exec.py [--json saida.json]
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

ALVO = [f"liu2022_fig8_multi_t{k}" for k in range(5)]
HELD = [f"liu2022_fig7a_oil_direct_t{k}" for k in range(4)]
CTRL = ([f"liu2022_fig6a_dry_release_t{k}" for k in range(4)]
        + [f"liu2022_fig6b_oil_release_t{k}" for k in range(4)]
        + ["liu2022_fig5_dry_F19p78kN", "liu2022_fig5_dry_F21p50kN",
           "liu2022_fig5_oil_F26p00kN", "liu2022_fig5_oil_F28p18kN"])
FILA = ["liu2022_fig8_multi_t1", "liu2022_fig8_multi_t2"]
XS = [0.9, 0.8, 0.7, 0.6, 0.5, 0.3]          # varredura DECLARADA no prereg

# so os protocolos que NAO soltam recebem o X (isto e' o teste, nao um filtro
# de conveniencia: aplicar em tudo confundiria protocolo com fonte)
_SEM_SOLTAR = set(ALVO) | set(HELD)

_X: dict = {}
_orig = rn._effective_overrides


def _patched(rec, base):
    ov = _orig(rec, base)
    if _X and rec.case_id in _SEM_SOLTAR:
        ov = {**ov, "k_emb_renew": _X["v"]}
    return ov


rn._effective_overrides = _patched


def _sim(cids, x=None):
    _X.clear()
    if x is not None:
        _X["v"] = x
    try:
        out = {}
        for cid in cids:
            r = rn.simulate_case(record(cid))
            if not r.ok:
                raise RuntimeError(f"{cid}: {r.error}")
            out[cid] = (float(r.mae), float(r.maxerr), float(r.resid_std))
        return out
    finally:
        _X.clear()


def main() -> int:
    st = ValidationStore()
    pares = [(r.source, st.get(r.case_id)) for r in all_records()
             if st.get(r.case_id) is not None]
    pisos = rh._pisos_medidos(pares)
    lim = float(rh.limite_sres("LIU_2022_RETIGHT", pisos))

    def passa(v):
        return v[0] <= rh.META_MAE and v[1] <= rh.META_MAX and v[2] <= lim

    todos = ALVO + HELD + CTRL
    base = _sim(todos)
    # instrumento: baseline re-simulado tem de reproduzir o store
    ruins = [c for c in todos
             if abs(base[c][0] - st.get(c).mae) > 1e-9
             or abs(base[c][2] - st.get(c).resid_std) > 1e-9]
    if ruins:
        print("!! INSTRUMENTO REPROVADO — baseline != store: " + ", ".join(ruins))
        return 2
    print(f"instrumento OK · limite sigma {lim:.4f} · "
          f"META_MAE {rh.META_MAE} META_MAX {rh.META_MAX}\n")
    print("BASELINE")
    print(f"  alvo fig8    : " + " ".join(
        f"t{k}{'OK' if passa(base[ALVO[k]]) else 'xx'}" for k in range(5)))
    print(f"  held fig7a   : " + " ".join(
        f"t{k}{'OK' if passa(base[HELD[k]]) else 'xx'}" for k in range(4))
        + f"   soma MAE {sum(base[c][0] for c in HELD):.4f}")

    out = {"lim": lim, "base": base, "varredura": []}
    escolhido = None
    for x in XS:
        cur = _sim(todos, x)
        # G2: controles bit-identicos
        vaz = [c for c in CTRL
               if abs(cur[c][0] - base[c][0]) > 1e-12
               or abs(cur[c][2] - base[c][2]) > 1e-12]
        # G4: t1 e t2 no tripe
        fecha = [c for c in FILA if passa(cur[c])]
        # G1: held-out
        held_fora = [c for c in HELD if not passa(cur[c])]
        d_held = sum(cur[c][0] for c in HELD) - sum(base[c][0] for c in HELD)
        # G3: nenhum pior >0.010 em qualquer perna (nos 9 alterados)
        piores = []
        for c in ALVO + HELD:
            d = [cur[c][i] - base[c][i] for i in range(3)]
            if max(d) > 0.010:
                piores.append((c, [round(v, 4) for v in d]))
        d_t4 = [round(cur[ALVO[4]][i] - base[ALVO[4]][i], 4) for i in range(3)]
        linha = dict(X=x, g2_vazou=vaz, g4_fecham=len(fecha),
                     g1_held_fora=held_fora, g1b_d_held=round(d_held, 4),
                     g3_piores=piores, d_t4=d_t4,
                     fig8=[cur[c] for c in ALVO], fig7a=[cur[c] for c in HELD])
        out["varredura"].append(linha)
        ok = (not vaz) and len(fecha) == 2 and not held_fora and not piores
        print(f"\nX={x}")
        print(f"  G2 controles bit-identicos : "
              f"{'OK' if not vaz else 'VAZOU ' + ','.join(vaz)}")
        print(f"  G4 t1/t2 no tripe          : {len(fecha)}/2 "
              f"({', '.join(c[-2:] for c in fecha) or 'nenhuma'})")
        print(f"  G1 held-out fig7a fora     : "
              f"{'nenhuma' if not held_fora else ','.join(held_fora)}")
        print(f"  G1b soma MAE fig7a         : {d_held:+.4f} "
              f"({'MELHORA' if d_held < -1e-4 else 'piora' if d_held > 1e-4 else 'neutro'})")
        print(f"  G3 piora >0.010            : "
              f"{'nenhuma' if not piores else piores}")
        print(f"  d(t4) [mae,mx,sigma]       : {d_t4}")
        print(f"  => {'TODOS OS GATES PASSAM' if ok else 'reprova'}")
        if ok and escolhido is None:
            escolhido = x            # o 1o da lista = o MAIOR = o mais brando

    print("\n" + "=" * 66)
    if escolhido is None:
        print("VEREDICTO: nenhum X passa todos os gates.")
        n_held = [l for l in out["varredura"] if l["g1_held_fora"]]
        n_t4 = [l for l in out["varredura"]
                if any(c == ALVO[4] for c, _ in l["g3_piores"])]
        if n_held:
            print(f"  G1 (held-out) falha em {len(n_held)} de {len(XS)} doses "
                  f"=> ramo FALSIFICADO (e' fit da fig8, nao protocolo)")
        elif n_t4:
            print(f"  G1 passa; o bloqueio e' o t4 (fratura) em "
                  f"{len(n_t4)} de {len(XS)} doses => ramo NAO ADOTA (t4 bloqueia)")
    else:
        print(f"VEREDICTO: adotar k_emb_renew = {escolhido} "
              f"(o MAIOR/mais brando que fecha t1 e t2)")
    out["escolhido"] = escolhido
    if "--json" in sys.argv:
        dest = Path(sys.argv[sys.argv.index("--json") + 1])
        dest.write_text(json.dumps(out, indent=1, default=float),
                        encoding="utf-8")
        print(f"gravado: {dest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
