# -*- coding: utf-8 -*-
"""Teste D-T (prereg 2026-08-05-li2022-fret-freq-exp): `fret_freq_exp` pos-D-Q.

NAO adota nada — rota OVERRIDE, comparacao contra o store vigente com o MESMO
n_max nas duas pontas.

O valor testado (3,57) e' DERIVADO da conta, nao varrido:
    e = ln[(r_alvo - 1)/s + 1] / ln(f_hi/f_lo)
com s = 0,093 (fatia do flanco a 10 Hz, decomposicao pos-D-Q) e r_alvo = 2,009.

    py -3.12 New_Theory/li2022_fret_freq_exp_teste.py [--exp 3.57]
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import bolt_analysis_studio.validation.runner as rn               # noqa: E402
from bolt_analysis_studio.validation.case_registry import (       # noqa: E402
    all_records, record)
from bolt_analysis_studio.validation.store import ValidationStore  # noqa: E402

FONTE = "LI_2022_TRIBOINT"
HELD = "LIU_2016"                    # G4: tem canal de flanco e fica INTOCADO
FREQ = {"li2022ti_axialmin_10Hz": 10.0, "li2022ti_axialmin_15Hz": 15.0,
        "li2022ti_axialmin_20Hz": 20.0, "li2022ti_axial_10Hz_full": 10.0}
R_ALVO = 2.009

_EXTRA: dict = {}
_orig = rn._effective_overrides


def _patched(rec, base):
    ov = _orig(rec, base)
    # G4: o override so' vale para a fonte ALVO
    if _EXTRA and rec.source == FONTE:
        return {**ov, **_EXTRA}
    return ov


rn._effective_overrides = _patched


def _tri(m, x, s):
    return m <= 0.05 and x <= 0.10 and s <= 0.025


def _varredura(exps) -> int:
    """Existe JANELA de expoente em que a alvo entra E a `full` NAO sai?

    O prereg testou UM valor derivado (3,57) e o falsificou. Isso falsifica o
    VALOR, nao a alavanca — e a alvo entrou com MAE 0,0220, folga enorme contra
    0,05. Sem varrer, declarar o membro morto seria conclusao sobre a populacao
    errada (mesma classe do erro de 2026-07-30, quando a triagem julgou a regua
    vencida).
    """
    st = ValidationStore()
    cids = sorted(r.case_id for r in all_records() if r.source == FONTE)
    base = {c: st.get(c) for c in cids}
    print(f"{'exp':>6s} " + " ".join(f"{c[9:26]:>19s}" for c in cids)
          + "   tripe  alvo  full")
    print(f"{'0 (base)':>6s} " + " ".join(
        f"{base[c].mae:6.4f}/{base[c].resid_std:6.4f}".rjust(19) for c in cids))
    for e in exps:
        _EXTRA.clear(); _EXTRA["fret_freq_exp"] = e
        row, n = {}, 0
        for c in cids:
            r = rn.simulate_case(record(c))
            if not r.ok:
                print(f"  !! {c}: {r.error}"); return 2
            row[c] = (r.mae, r.maxerr, r.resid_std)
            n += _tri(*row[c])
        _EXTRA.clear()
        alvo = _tri(*row["li2022ti_axialmin_10Hz"])
        full = _tri(*row["li2022ti_axial_10Hz_full"])
        print(f"{e:6.2f} " + " ".join(
            f"{row[c][0]:6.4f}/{row[c][2]:6.4f}".rjust(19) for c in cids)
            + f"   {n}/4  {'IN ' if alvo else 'out'}  {'IN ' if full else 'out'}"
            + ("   <== JANELA" if (alvo and full) else ""))
    _EXTRA.clear()
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--exp", type=float, default=3.57)
    ap.add_argument("--varre", type=str, default="",
                    help="lista de expoentes; varre e nao julga o ramo")
    a = ap.parse_args()
    if a.varre:
        return _varredura([float(x) for x in a.varre.split(",")])

    st = ValidationStore()
    cids = sorted(r.case_id for r in all_records() if r.source == FONTE)

    # ---- G0 instrumento
    _EXTRA.clear(); _EXTRA["fret_freq_exp"] = a.exp
    ov = rn._effective_overrides(record(cids[0]), {})
    print(f"G0 instrumento: fret_freq_exp no runner = "
          f"{ov.get('fret_freq_exp')!r} · flank_wear_on = "
          f"{ov.get('flank_wear_on')!r} · flank_fret_depth = "
          f"{ov.get('flank_fret_depth')!r}")
    if ov.get("fret_freq_exp") != a.exp or not ov.get("flank_wear_on"):
        print("!! G0 FALHA -- o teste nao testaria nada. INCONCLUSIVO.")
        return 3
    ov_held = rn._effective_overrides(
        record(sorted(r.case_id for r in all_records() if r.source == HELD)[0]), {})
    print(f"   G4: {HELD} recebe fret_freq_exp? "
          f"{ov_held.get('fret_freq_exp')!r} (tem de ser None)")
    if ov_held.get("fret_freq_exp") is not None:
        print("!! G4 FALHA -- vazou para o held-out.")
        return 3

    print(f"\n{'curva':30s} {'mae b':>7s} {'mae a':>7s} {'mx a':>7s} "
          f"{'sig b':>7s} {'sig a':>7s} {'perda':>7s}  estado")
    perdas, saiu, pior, alvo_ok = {}, [], [], None
    for cid in cids:
        b = st.get(cid)
        _EXTRA.clear(); _EXTRA["fret_freq_exp"] = a.exp
        r = rn.simulate_case(record(cid))
        _EXTRA.clear()
        if not r.ok:
            print(f"  !! {cid}: {r.error}")
            return 2
        p = np.asarray(r.metric_pred, float)
        perdas[FREQ[cid]] = perdas.get(FREQ[cid]) or float(p[0] - p[-1])
        if cid == "li2022ti_axialmin_10Hz":
            perdas[10.0] = float(p[0] - p[-1])
        tb = _tri(b.mae, b.maxerr, b.resid_std)
        ta = _tri(r.mae, r.maxerr, r.resid_std)
        if tb and not ta:
            saiu.append(cid)
        dm = max(r.mae - b.mae, r.maxerr - b.maxerr, r.resid_std - b.resid_std)
        if dm > 0.010:
            pior.append((cid, round(dm, 4)))
        if cid == "li2022ti_axialmin_10Hz":
            alvo_ok = ta
        est = ("ENTROU" if (ta and not tb) else "SAIU" if (tb and not ta)
               else ("ok" if ta else "fora"))
        print(f"{cid[9:39]:30s} {b.mae:7.4f} {r.mae:7.4f} {r.maxerr:7.4f} "
              f"{b.resid_std:7.4f} {r.resid_std:7.4f} "
              f"{float(p[0]-p[-1]):7.4f}  {est}")

    razao = perdas[10.0] / perdas[20.0]
    print(f"\nG5 razao de frequencia do MODELO (10 Hz / 20 Hz): {razao:.3f} "
          f"(alvo {R_ALVO:.3f}; base 1,003)")
    print(f"   predicao registrada: entre 1,5 e 2,5  -> "
          f"{'DENTRO' if 1.5 <= razao <= 2.5 else 'FORA da faixa prevista'}")
    print(f"G1 (a alvo entra no tripe):        {'PASSA' if alvo_ok else 'FALHA'}")
    print(f"G2 (nenhuma aprovada sai):         "
          f"{'PASSA' if not saiu else 'FALHA ' + str(saiu)}")
    print(f"G3 (nenhum pior > +0,010):         "
          f"{'PASSA' if not pior else 'FALHA ' + str(pior)}")
    if not (1.2 <= razao <= 2.5):
        ramo = "INCONCLUSIVO (a predicao errou a faixa: o teste nao testou)"
    elif alvo_ok and not saiu:
        ramo = "PROMOVIDO (merece prereg de adocao)"
    else:
        ramo = "FALSIFICADO"
    print(f"\n==> RAMO: {ramo}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
