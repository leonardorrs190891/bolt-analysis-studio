# -*- coding: utf-8 -*-
"""EXECUCAO do prereg do PAR
specs/2026-07-30-yang2023ijpem-par-deltafree-arresto-prereg.md

G1 CONGELA:
    delta_free = 122.96 um (m6) / 129.18 um (m8)   [derivado e provado no v2]
    loose_arrest_floor = 0.1025                    [UM valor, mediana do plato]

Canonico e store NAO tocados (override em memoria). Prints ASCII.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))

import bolt_analysis_studio.validation.report_html as R  # noqa: E402
import bolt_analysis_studio.validation.runner as RN  # noqa: E402
from bolt_analysis_studio.validation.case_registry import all_records  # noqa: E402
from bolt_analysis_studio.validation.store import ValidationStore  # noqa: E402

FONTE = "YANG_2023_IJPEM"
# ---- G1: CONGELADOS ------------------------------------------------------
DF = {11000: 122.96e-6, 14300: 129.18e-6}
PISO_UNICO = 0.1025
# pisos PROPRIOS lidos por kb.floor_from_curve (usados so no G5)
PISO_PROPRIO = {0.30: 0.1400, 0.35: 0.1000, 0.45: 0.1050,
                0.50: 0.0700, 0.55: 0.1150, 0.65: 0.0950}
SUB = (0.15, 0.18)          # sub-criticas: piso inerte, exigir BIT-IDENTICO
TRANSICAO = 0.25            # fora do G4 por excecao declarada
SATURADAS = (0.30, 0.35, 0.45, 0.50, 0.55, 0.65)
MEDIDO_025 = 0.520
PISO_LIDO_025 = 0.580


def _f0(rec) -> int:
    return int(round(float(rec.validation_case.initial_preload_N)))


def casos():
    out = {}
    for rec in all_records():
        if rec.source == FONTE:
            out[round(float(RN._loading_for(rec)["delta_mm"]), 3)] = rec
    return out


def sim(rec, piso):
    """re-simula com delta_free novo + piso de arresto dado."""
    orig = RN._effective_overrides

    def patched(r, consts):
        d = dict(orig(r, consts))
        if r.source == FONTE:
            d["delta_free"] = DF[_f0(r)]
            d["loose_arrest_floor"] = float(piso)
        return d
    RN._effective_overrides = patched
    try:
        return RN.simulate_case(rec)
    finally:
        RN._effective_overrides = orig


def main() -> int:
    st = ValidationStore()
    cs = casos()
    falhas = []
    novo = {amp: sim(cs[amp], PISO_UNICO) for amp in sorted(cs)}

    # ---------------- G3 (bit-identico) e G4 (+0,01) ---------------------
    print("=" * 78)
    print("G3 (sub-critico BIT-IDENTICO) e G4 (nada pior +0,01; 0,25 isenta)")
    print("=" * 78)
    print(f"{'amp':>5} {'MAE':>17} {'res.max':>17} {'sigma':>17} tripe")
    g3 = g4 = True
    for amp in sorted(cs):
        b, n = st.get(cs[amp].case_id), novo[amp]
        okb, okn = R._tripe_ok(b), R._tripe_ok(n)
        marca = ""
        if amp in SUB:
            ident = (b.mae == n.mae and b.maxerr == n.maxerr
                     and b.resid_std == n.resid_std)
            if not ident:
                g3 = False
                marca = "  <<< G3/F1 REPROVA (nao bit-identico)"
            else:
                marca = "  [bit-identico]"
        elif amp == TRANSICAO:
            marca = "  [isenta do G4 — vai ao G6]"
        else:
            pior = [r_ for r_, va, vb in
                    (("MAE", b.mae, n.mae), ("max", b.maxerr, n.maxerr),
                     ("sd", b.resid_std, n.resid_std))
                    if va is not None and vb is not None and vb > va + 0.01]
            if pior:
                g4 = False
                marca = f"  <<< G4 ({','.join(pior)})"
        print(f"{amp:5.2f} {b.mae:7.4f}->{n.mae:7.4f} "
              f"{b.maxerr:7.4f}->{n.maxerr:7.4f} "
              f"{b.resid_std:7.4f}->{n.resid_std:7.4f} "
              f"{str(okb):>5}->{str(okn):<5}{marca}")
    print(f"\n  G3 {'PASSA' if g3 else 'REPROVA'}   "
          f"G4 {'PASSA' if g4 else 'REPROVA'}")
    if not g3:
        falhas.append("G3")
    if not g4:
        falhas.append("G4")

    # ---------------- G2 (ramo saturado melhora) -------------------------
    print("\n" + "=" * 78)
    print("G2 — mediana do res.max das 6 SATURADAS tem de CAIR")
    print("=" * 78)
    ba = [st.get(cs[a].case_id).maxerr for a in SATURADAS]
    de = [novo[a].maxerr for a in SATURADAS]
    ma, md = float(np.median(ba)), float(np.median(de))
    for a, x, y in zip(SATURADAS, ba, de):
        print(f"  {a:4.2f}  {x:.4f} -> {y:.4f}  ({y-x:+.4f})")
    print(f"\n  mediana {ma:.4f} -> {md:.4f}  ({md-ma:+.4f})")
    g2 = md < ma
    print(f"  G2 {'PASSA' if g2 else 'REPROVA (F2: dar o patamar nao melhora)'}")
    if not g2:
        falhas.append("G2")

    # ---------------- G5 (o piso unico basta?) ---------------------------
    print("\n" + "=" * 78)
    print("G5 — TESTE DE LEI: piso unico (0,1025) vs piso PROPRIO de cada curva")
    print("=" * 78)
    print(f"  {'amp':>5} {'proprio':>8} {'max unico':>10} {'max proprio':>12} "
          f"{'ganho do proprio':>17}")
    pior_que_proprio = 0
    for a in SATURADAS:
        n_p = sim(cs[a], PISO_PROPRIO[a])
        ganho = novo[a].maxerr - n_p.maxerr        # >0 = proprio e' melhor
        if ganho > 0.05:
            pior_que_proprio += 1
        print(f"  {a:5.2f} {PISO_PROPRIO[a]:8.4f} {novo[a].maxerr:10.4f} "
              f"{n_p.maxerr:12.4f} {ganho:+17.4f}"
              f"{'  <<< proprio ganha >0,05' if ganho > 0.05 else ''}")
    g5 = pior_que_proprio < 3
    print(f"\n  curvas em que o piso PROPRIO ganha por >0,05: {pior_que_proprio} de 6")
    print(f"  G5 {'PASSA (o piso unico basta)' if g5 else 'REPROVA (F3: piso e funcao da amplitude)'}")
    if not g5:
        falhas.append("G5")

    # ---------------- F4 + G6 -------------------------------------------
    print("\n" + "=" * 78)
    print("F4 (ninguem termina abaixo do piso imposto) e G6 (transicao)")
    print("=" * 78)
    f4 = True
    for a in SATURADAS:
        fim = float(np.asarray(novo[a].ratio, float)[-1])
        if fim < PISO_UNICO - 1e-6:
            f4 = False
            print(f"  {a:4.2f}  ratio final {fim:.4f} < piso {PISO_UNICO}"
                  f"  <<< F4 FALSIFICA")
        else:
            print(f"  {a:4.2f}  ratio final {fim:.4f}  (>= piso {PISO_UNICO}) ok")
    print(f"  F4 {'ok' if f4 else 'FALSIFICA'}")
    if not f4:
        falhas.append("F4")
    fim25 = float(np.asarray(novo[TRANSICAO].ratio, float)[-1])
    print(f"\n  G6 transicao 0,25 mm: ratio final previsto {fim25:.4f}")
    print(f"     medido {MEDIDO_025:.3f} · piso lido dela {PISO_LIDO_025:.3f}"
          f" · erro {fim25-MEDIDO_025:+.3f}")

    # ---------------- G7 ------------------------------------------------
    print("\n" + "=" * 78)
    print("G7 — resto do store bit-identico")
    print("=" * 78)
    g7 = True
    recs = {r.case_id: r for r in all_records()}
    for cid in ("liu2016wear_fig9a_m30nm", "zhang18_fig13_14kN_preload_vs_cycles",
                "eccles2010_fig7c_axial_2p7kN_constant", "karlsen2022_M30_HV_run6p2"):
        r = recs.get(cid)
        if r is None:
            continue
        b, n = st.get(cid), sim(r, PISO_UNICO)
        ident = (b.mae == n.mae and b.maxerr == n.maxerr
                 and b.resid_std == n.resid_std)
        g7 = g7 and ident
        print(f"  {cid[:46]:48} {'bit-identico' if ident else 'MUDOU <<< G7'}")
    print(f"  G7 {'PASSA' if g7 else 'REPROVA'}")
    if not g7:
        falhas.append("G7")

    print("\n" + "=" * 78)
    print("RESUMO: " + ("TODOS OS GATES BLOQUEANTES PASSAM" if not falhas
                        else "REPROVA em " + ", ".join(falhas)))
    print("=" * 78)
    return 0 if not falhas else 1


if __name__ == "__main__":
    raise SystemExit(main())
