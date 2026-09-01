# -*- coding: utf-8 -*-
"""EXECUCAO do prereg specs/2026-07-30-yang2023ijpem-delta-free-prereg.md.

Correcao ALGEBRICA (zero grau de liberdade):  delta_free := limiar - F_slip/k_tr

Valores CONGELADOS pelo G1 — nao podem ser tocados por esta execucao:
    M6 (F0 11,0 kN):  65.774 um    => onset deve dar 150,0 um
    M8 (F0 14,3 kN):  95.968 um    => onset deve dar 180,0 um

Ordem: G2 (cinematico, SEM olhar erro) -> G3/G4 (metricas) -> G5 (escopo).
Canonico e store NAO sao tocados: override em memoria.
Prints ASCII (charmap do console Windows).
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))

import bolt_analysis_studio.validation.report_html as R  # noqa: E402
import bolt_analysis_studio.validation.runner as RN  # noqa: E402
from bolt_analysis_studio.numerical.dynamic_stiffness_analyzer import (  # noqa: E402
    DynamicStiffnessAnalyzer, F_slip_transverse, JointMaterial,
    k_tr_transverse, resolve_transverse_slip)
from bolt_analysis_studio.validation.case_registry import all_records  # noqa: E402
from bolt_analysis_studio.validation.inputs import (frozen_constants,  # noqa: E402
                                                    geometry_for_case)
from bolt_analysis_studio.validation.store import ValidationStore  # noqa: E402

FONTE = "YANG_2023_IJPEM"
# --- G1: CONGELADOS. Qualquer edicao aqui invalida a execucao. -------------
NOVO_DF = {11000: 65.774e-6, 14300: 95.968e-6}      # m, por F0 (m6 / m8)
LIMIAR = {11000: 150.0e-6, 14300: 180.0e-6}         # limiar DECLARADO no artigo
SUB_AMPS = (0.15, 0.18)                             # ramo sub-critico (G3)
TOL_ONSET_UM = 0.1


def _f0(rec) -> int:
    return int(round(float(rec.validation_case.initial_preload_N)))


def monta(rec, df=None):
    load = RN._loading_for(rec)
    inp = load["inputs"]
    geom = geometry_for_case(rec.validation_case,
                             grip_mm=inp["grip_mm"]["value"],
                             E=(inp.get("E") or {}).get("value"))
    geom = RN._apply_adopted_geometry(geom, rec.source, rec.case_id,
                                      rec.validation_case.bolt_size)
    kw = RN.material_kwargs_for(rec, inp)
    if df is not None:
        kw["delta_free"] = df
    mat = JointMaterial(**kw)
    return geom, mat, float(rec.validation_case.initial_preload_N), load


def casos():
    out = {}
    for rec in all_records():
        if rec.source != FONTE:
            continue
        out[round(float(RN._loading_for(rec)["delta_mm"]), 3)] = rec
    return out


def com_override(rec):
    """re-simula com o delta_free novo, injetado por subgrupo (F0)."""
    orig = RN._effective_overrides

    def patched(r, consts):
        d = dict(orig(r, consts))
        if r.source == FONTE:
            d["delta_free"] = NOVO_DF[_f0(r)]
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

    # ================= G2 — CINEMATICO (sem olhar erro) ====================
    print("=" * 74)
    print("G2 — ALINHAMENTO CINEMATICO (primario; nenhuma metrica olhada aqui)")
    print("=" * 74)
    print(f"{'amp':>5} {'F0kN':>6} {'df novo um':>11} {'onset um':>9} "
          f"{'esperado':>9} {'slip um':>9}")
    onsets = {}
    for amp in sorted(cs):
        rec = cs[amp]
        f0 = _f0(rec)
        geom, mat, F0, load = monta(rec, NOVO_DF[f0])
        ana = DynamicStiffnessAnalyzer(geom, mat, F0)
        el = F_slip_transverse(ana.state, mat) / k_tr_transverse(geom, mat)
        onset = mat.delta_free + el
        slip = resolve_transverse_slip(ana.state, mat, load["F_amp_N"],
                                       load["theta"], delta_amp=amp * 1e-3,
                                       geom=geom)
        onsets[f0] = onset
        print(f"{amp:5.2f} {F0/1e3:6.1f} {mat.delta_free*1e6:11.3f} "
              f"{onset*1e6:9.3f} {LIMIAR[f0]*1e6:9.1f} {slip*1e6:9.2f}")
    ok_onset = all(abs(onsets[f0] - LIMIAR[f0]) * 1e6 <= TOL_ONSET_UM
                   for f0 in onsets)
    def slip_de(amp: float) -> float:
        rec = cs[amp]
        geom, mat, F0, load = monta(rec, NOVO_DF[_f0(rec)])
        ana = DynamicStiffnessAnalyzer(geom, mat, F0)
        return float(resolve_transverse_slip(
            ana.state, mat, load["F_amp_N"], load["theta"],
            delta_amp=amp * 1e-3, geom=geom))

    s015, s018, s025 = slip_de(0.15), slip_de(0.18), slip_de(0.25)
    print(f"\n  onset == limiar declarado (tol {TOL_ONSET_UM} um): "
          f"{'ok' if ok_onset else 'FALSIFICA (F2)'}")
    print(f"  slip(0,15) = {s015*1e6:.3f} um  (exige 0)  "
          f"{'ok' if s015 == 0 else 'FALHA'}")
    print(f"  slip(0,18) = {s018*1e6:.3f} um  (exige 0)  "
          f"{'ok' if s018 == 0 else 'FALHA'}")
    print(f"  slip(0,25) = {s025*1e6:.3f} um  (exige >0) "
          f"{'ok' if s025 > 0 else 'FALHA'}")
    g2 = ok_onset and s015 == 0 and s018 == 0 and s025 > 0
    print(f"  G2 {'PASSA' if g2 else 'REPROVA'}")
    if not g2:
        falhas.append("G2")

    # ================= G3 / G4 — metricas =================================
    print("\n" + "=" * 74)
    print("G3 (ramo sub-critico) e G4 (nenhuma pior que +0,01)")
    print("=" * 74)
    print(f"{'amp':>5} {'MAE antes':>10} {'depois':>8} | {'max antes':>10} "
          f"{'depois':>8} | {'sd antes':>9} {'depois':>8} | tripe")
    g3 = g4 = True
    med_a, med_d = [], []
    for amp in sorted(cs):
        b = st.get(cs[amp].case_id)
        n = com_override(cs[amp])
        okb = R._tripe_ok(b)
        okn = R._tripe_ok(n)
        piorou = [rot for rot, va, vb in
                  (("MAE", b.mae, n.mae), ("max", b.maxerr, n.maxerr),
                   ("sd", b.resid_std, n.resid_std))
                  if va is not None and vb is not None and vb > va + 0.01]
        marca = ""
        if amp in SUB_AMPS:
            if okb is True and okn is not True:
                g3 = False
                marca = "  <<< G3 REPROVA"
        else:
            med_a.append(b.maxerr)
            med_d.append(n.maxerr)
            if piorou:
                g4 = False
                marca = f"  <<< G4 REPROVA ({','.join(piorou)})"
        print(f"{amp:5.2f} {b.mae:10.4f} {n.mae:8.4f} | {b.maxerr:10.4f} "
              f"{n.maxerr:8.4f} | {b.resid_std:9.4f} {n.resid_std:8.4f} | "
              f"{str(okb):>5}->{str(okn):<5}{marca}")
    print(f"\n  G3 {'PASSA' if g3 else 'REPROVA'}   G4 "
          f"{'PASSA' if g4 else 'REPROVA'}")
    ma, md = float(np.median(med_a)), float(np.median(med_d))
    print(f"  mediana res.max das 7 acima do limiar: {ma:.4f} -> {md:.4f} "
          f"({md-ma:+.4f})   [REPORTADA, nao exigida]")
    if md > ma:
        print("  F4: a mediana PIOROU -> o desalinhamento nao era o defeito")
        print("      dominante. A correcao segue certa como procedencia.")
    if not g3:
        falhas.append("G3")
    if not g4:
        falhas.append("G4")

    # ================= G5 — escopo ========================================
    print("\n" + "=" * 74)
    print("G5 — escopo (o override vaza para outra fonte?)")
    print("=" * 74)
    outras = ["liu2016wear_fig9a_m30nm", "zhang18_fig13_14kN_preload_vs_cycles",
              "eccles2010_fig7c_axial_2p7kN_constant"]
    recs = {r.case_id: r for r in all_records()}
    g5 = True
    for cid in outras:
        r = recs.get(cid)
        if r is None:
            continue
        b = st.get(cid)
        n = com_override(r)
        ident = (b.mae == n.mae and b.maxerr == n.maxerr
                 and b.resid_std == n.resid_std)
        g5 = g5 and ident
        print(f"  {cid[:44]:46} {'bit-identico' if ident else 'MUDOU <<< G5'}")
    print(f"  G5 {'PASSA' if g5 else 'REPROVA'}")
    print("  NOTA: este harness injeta por FONTE, logo o vazamento por empate de")
    print("  token de config NAO e' testavel aqui — so na adocao real no")
    print("  adopted_configs.json. G5 aqui cobre o escopo da sonda, nao da adocao.")
    if not g5:
        falhas.append("G5")

    print("\n" + "=" * 74)
    print(f"RESUMO: {'TODOS OS GATES PASSAM' if not falhas else 'REPROVA em ' + ', '.join(falhas)}")
    print("=" * 74)
    return 0 if not falhas else 1


if __name__ == "__main__":
    raise SystemExit(main())
