# -*- coding: utf-8 -*-
"""Executor do prereg D-I (2026-08-04) — grupo 45kN do CACCESE fora da banda.

O modelo esta ABAIXO das DUAS replicas da condicao tapered 45 kN (vies -0.0635
e -0.0253), ou seja fora da banda que o proprio dado nao distingue (piso
|rep1-rep2| = 0.0382). O alvo legitimo de uma condicao com replicas e' o
CENTRO delas.

G5 proibe escolher o valor que minimiza o MAE de UMA das replicas — foi isso
que produziu o defeito. O criterio e' o G1: ficar dentro de 0.0382 das DUAS.

O grupo serve 3 curvas: `protruding_45kN` (no tripe) e' o controle que paga a
conta se o ajuste exagerar.

    py -3.12 New_Theory/caccese_45kN_centro_exec.py [--json saida.json]
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

R1 = "caccese2009_tapered_45kN_rep1"
R2 = "caccese2009_tapered_45kN_rep2"
CTRL = "caccese2009_protruding_45kN"
GRUPO = [R1, R2, CTRL]
OUTROS = ["caccese2009_compblock_34kPa", "caccese2009_compblock_71kPa",
          "caccese2009_retighten_12p7mm_no_retighten",
          "caccese2009_retighten_19p1mm_no_retighten"]

_EXTRA: dict = {}
_orig = rn._effective_overrides
rn._effective_overrides = lambda rec, base: (
    {**_orig(rec, base), **_EXTRA} if _EXTRA and rec.case_id in GRUPO
    else _orig(rec, base))


def _sim(cids, ov=None):
    _EXTRA.clear()
    if ov:
        _EXTRA.update(ov)
    try:
        out = {}
        for cid in cids:
            r = rn.simulate_case(record(cid))
            if not r.ok:
                raise RuntimeError(f"{cid}: {r.error}")
            out[cid] = dict(mae=float(r.mae), mx=float(r.maxerr),
                            sd=float(r.resid_std),
                            x=np.asarray(r.metric_x, float),
                            p=np.asarray(r.metric_pred, float))
        return out
    finally:
        _EXTRA.clear()


def main() -> int:
    st = ValidationStore()
    pares = [(r.source, st.get(r.case_id)) for r in all_records()
             if st.get(r.case_id) is not None]
    lim = float(rh.limite_sres("CACCESE_2009", rh._pisos_medidos(pares)))

    def passa(v):
        return v["mae"] <= rh.META_MAE and v["mx"] <= rh.META_MAX and v["sd"] <= lim

    # dado das duas replicas na janela comum + piso
    d1 = np.asarray(st.get(R1).metric_data, float)
    x1 = np.asarray(st.get(R1).metric_x, float)
    d2 = np.asarray(st.get(R2).metric_data, float)
    x2 = np.asarray(st.get(R2).metric_x, float)
    g = np.linspace(max(x1[0], x2[0]), min(x1[-1], x2[-1]), 60)
    i1, i2 = np.interp(g, x1, d1), np.interp(g, x2, d2)
    PISO = float(np.mean(np.abs(i1 - i2)))

    def banda(v):
        """erro do modelo contra CADA replica, na janela comum."""
        m = np.interp(g, v["x"], v["p"])
        return (float(np.mean(np.abs(m - i1))), float(np.mean(np.abs(m - i2))))

    C0 = float(_orig(record(R1), {})["C_creep"])
    base = _sim(GRUPO + OUTROS)
    ruins = [c for c in GRUPO + OUTROS
             if abs(base[c]["mae"] - st.get(c).mae) > 1e-9]
    if ruins:
        print("!! INSTRUMENTO REPROVADO: " + ",".join(ruins))
        return 2
    e1, e2 = banda(base[R1])
    print(f"instrumento OK · limite sigma {lim:.4f} · C_creep atual {C0:.6e}")
    print(f"PISO |rep1-rep2| = {PISO:.4f}  (FORTE <= {PISO/np.sqrt(2):.4f})")
    print(f"BASELINE na banda: vs rep1 {e1:.4f} · vs rep2 {e2:.4f} "
          f"-> {'DENTRO' if max(e1,e2)<=PISO else 'FORA da banda'}")

    # ---- G0: sonda de 2 pontos (direcao) -----------------------------------
    for f in (0.8, 1.2):
        s = _sim([R1], {"C_creep": C0 * f})
        print(f"  G0 C*{f}: retencao final {s[R1]['p'][-1]:.4f} "
              f"(base {base[R1]['p'][-1]:.4f}) mae {s[R1]['mae']:.4f}")

    out = {"piso": PISO, "lim": lim, "C0": C0, "grade": []}
    escolhido = None
    for f in (0.95, 0.9, 0.85, 0.8, 0.75, 0.7, 0.65, 0.6):
        cur = _sim(GRUPO, {"C_creep": C0 * f})
        b1, b2 = banda(cur[R1])
        dentro = max(b1, b2) <= PISO
        g2 = (passa(cur[CTRL])
              and max(cur[CTRL][k] - base[CTRL][k] for k in ("mae", "mx", "sd"))
              <= 0.010)
        g4 = passa(cur[R1])
        ok = dentro and g2 and g4
        print(f"\n  C*{f:<5g} (C={C0*f:.4e})")
        print(f"    banda: vs rep1 {b1:.4f} · vs rep2 {b2:.4f} -> "
              f"{'DENTRO' if dentro else 'fora'}")
        for c in GRUPO:
            print(f"      {'OK ' if passa(cur[c]) else 'FORA'} {c[:42]:42s} "
                  f"mae {cur[c]['mae']:.4f} mx {cur[c]['mx']:.4f} "
                  f"sig {cur[c]['sd']:.4f}")
        print(f"    G2 controle protruding: {'OK' if g2 else 'REPROVA'} · "
              f"G4 rep1 no tripe: {'SIM' if g4 else 'nao'}")
        out["grade"].append(dict(f=f, C=C0 * f, b1=b1, b2=b2, dentro=dentro,
                                 g2=g2, g4=g4, ok=bool(ok),
                                 vals={c: {k: cur[c][k] for k in ("mae", "mx", "sd")}
                                       for c in GRUPO}))
        if ok and escolhido is None:
            escolhido = f

    print("\n" + "=" * 68)
    oks = [x for x in out["grade"] if x["ok"]]
    if oks:
        # G5: entre as que passam, a que CENTRA melhor (min |b1-b2|), nao a de
        # menor MAE de uma delas — e' a diferenca entre alvo no centro e alvo
        # numa replica.
        b = min(oks, key=lambda x: abs(x["b1"] - x["b2"]))
        print(f"VEREDICTO: ADOTA C_creep = {b['C']:.6e} (C0 x {b['f']:g})")
        print(f"  criterio G5: das {len(oks)} que passam, a mais CENTRADA "
              f"(|b1-b2| = {abs(b['b1']-b['b2']):.4f})")
        out["escolhido"] = b["f"]
    elif any(x["dentro"] and x["g4"] for x in out["grade"]):
        print("VEREDICTO: NAO ADOTA (a protruding paga) — entra na banda e "
              "fecha a rep1, mas o controle sai do tripe ou piora >0.010.")
    else:
        print("VEREDICTO: NAO ADOTA (nao entra na banda) — nenhum C_creep poe "
              "o modelo a <= piso das DUAS replicas. A dispersao entre elas tem "
              "estrutura que translacao nao alcanca.")
    if "--json" in sys.argv:
        dest = Path(sys.argv[sys.argv.index("--json") + 1])
        dest.write_text(json.dumps(out, indent=1, default=float),
                        encoding="utf-8")
        print(f"gravado: {dest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
