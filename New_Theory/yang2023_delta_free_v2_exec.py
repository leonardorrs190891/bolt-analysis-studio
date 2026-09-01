# -*- coding: utf-8 -*-
"""EXECUCAO do prereg v2 specs/2026-07-30-yang2023ijpem-delta-free-v2-prereg.md.

delta_free := media GEOMETRICA da janela admissivel (interior, nao borda).
Valores CONGELADOS pelo G1 — esta execucao nao pode toca-los:
    m6 (F0 11,0 kN):  122.96 um
    m8 (F0 14,3 kN):  129.18 um

G2 e' o conserto do que o v1 errou: checa slip em TODOS os ciclos, nao no 1o.
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
from bolt_analysis_studio.numerical.dynamic_stiffness_analyzer import (  # noqa: E402
    DynamicStiffnessAnalyzer, JointMaterial, resolve_transverse_slip)
from bolt_analysis_studio.validation.case_registry import all_records  # noqa: E402
from bolt_analysis_studio.validation.inputs import (geometry_for_case,  # noqa: E402
                                                    load_full_curve, repo_root)
from bolt_analysis_studio.validation.store import ValidationStore  # noqa: E402

FONTE = "YANG_2023_IJPEM"
# --- G1: CONGELADOS -------------------------------------------------------
NOVO_DF = {11000: 122.96e-6, 14300: 129.18e-6}
SUB_AMPS = (0.15, 0.18)          # devem ter slip 0 em TODOS os ciclos
DEVE_ESCORREGAR = (0.25, 0.30)   # devem ter slip > 0 em algum ciclo
MEDIDO_FIM = {0.25: 0.520, 0.30: 0.220}      # G6


def _f0(rec) -> int:
    return int(round(float(rec.validation_case.initial_preload_N)))


def monta(rec, df):
    load = RN._loading_for(rec)
    inp = load["inputs"]
    geom = geometry_for_case(rec.validation_case,
                             grip_mm=inp["grip_mm"]["value"],
                             E=(inp.get("E") or {}).get("value"))
    geom = RN._apply_adopted_geometry(geom, rec.source, rec.case_id,
                                      rec.validation_case.bolt_size)
    kw = RN.material_kwargs_for(rec, inp)
    kw["delta_free"] = df
    return geom, JointMaterial(**kw), float(rec.validation_case.initial_preload_N), load


def casos():
    out = {}
    for rec in all_records():
        if rec.source == FONTE:
            out[round(float(RN._loading_for(rec)["delta_mm"]), 3)] = rec
    return out


def n_max_de(rec) -> int:
    cx, _ = load_full_curve(rec.csv_path.relative_to(repo_root()).as_posix())
    return int(np.asarray(cx, float).max())


def trajetoria_slip(rec, amp, df):
    """(n_slip_positivo, slip_max_um, n_primeiro_slip) na corrida COMPLETA."""
    geom, mat, F0, load = monta(rec, df)
    ana = DynamicStiffnessAnalyzer(geom, mat, F0)
    n_max = n_max_de(rec)
    npos, smax, primeiro = 0, 0.0, None
    for n in range(1, n_max + 1):
        s = float(resolve_transverse_slip(ana.state, mat, load["F_amp_N"],
                                          load["theta"], delta_amp=amp * 1e-3,
                                          geom=geom))
        if s > 0:
            npos += 1
            smax = max(smax, s)
            if primeiro is None:
                primeiro = n
        ana.step_cycle(load["F_amp_N"], load["theta"],
                       rec.validation_case.frequency_Hz, delta_amp=amp * 1e-3)
    return npos, smax * 1e6, primeiro, n_max


def com_override(rec):
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

    print("=" * 76)
    print("G2 — CINEMATICA em TODOS os ciclos (nenhuma metrica olhada aqui)")
    print("=" * 76)
    print(f"{'amp':>5} {'df um':>7} {'n_max':>6} {'ciclos c/ slip':>15} "
          f"{'1o slip':>8} {'slip max um':>12}")
    g2 = True
    for amp in sorted(cs):
        rec = cs[amp]
        df = NOVO_DF[_f0(rec)]
        npos, smax, prim, nmx = trajetoria_slip(rec, amp, df)
        alvo = ""
        if amp in SUB_AMPS:
            if npos != 0:
                g2 = False
                alvo = f"  <<< G2/F1 REPROVA (deveria ser 0)"
        elif amp in DEVE_ESCORREGAR:
            if npos == 0:
                g2 = False
                alvo = "  <<< G2/F2 REPROVA (deveria escorregar)"
        print(f"{amp:5.2f} {df*1e6:7.2f} {nmx:6d} {npos:15d} "
              f"{str(prim):>8} {smax:12.2f}{alvo}")
    print(f"\n  G2 {'PASSA' if g2 else 'REPROVA'}")
    if not g2:
        falhas.append("G2")

    print("\n" + "=" * 76)
    print("G3 (sub-critico no tripe) · G4 (nada pior que +0,01) · G6 (regime)")
    print("=" * 76)
    print(f"{'amp':>5} {'MAE':>17} {'res.max':>17} {'sigma':>17} tripe")
    g3 = g4 = True
    med_a, med_d = [], []
    g6 = {}
    for amp in sorted(cs):
        b = st.get(cs[amp].case_id)
        n = com_override(cs[amp])
        okb, okn = R._tripe_ok(b), R._tripe_ok(n)
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
                marca = f"  <<< G4 ({','.join(piorou)})"
        if amp in MEDIDO_FIM:
            g6[amp] = (float(np.asarray(n.ratio, float)[-1]) if n.ratio is not None
                       and len(n.ratio) else float("nan"))
        print(f"{amp:5.2f} {b.mae:7.4f}->{n.mae:7.4f} "
              f"{b.maxerr:7.4f}->{n.maxerr:7.4f} "
              f"{b.resid_std:7.4f}->{n.resid_std:7.4f} "
              f"{str(okb):>5}->{str(okn):<5}{marca}")
    ma, md = float(np.median(med_a)), float(np.median(med_d))
    print(f"\n  G3 {'PASSA' if g3 else 'REPROVA'}   "
          f"G4 {'PASSA' if g4 else 'REPROVA'}")
    print(f"  mediana res.max das 7: {ma:.4f} -> {md:.4f} ({md-ma:+.4f})"
          f"   [reportada]")
    print("\n  G6 (informacional) ratio final previsto vs MEDIDO:")
    for amp, prev in g6.items():
        print(f"     {amp:4.2f} mm  previsto {prev:6.3f}   medido "
              f"{MEDIDO_FIM[amp]:6.3f}   ({prev-MEDIDO_FIM[amp]:+.3f})")
    if not g3:
        falhas.append("G3")
    if not g4:
        falhas.append("G4")

    print("\n" + "=" * 76)
    print("G5 — escopo")
    print("=" * 76)
    g5 = True
    recs = {r.case_id: r for r in all_records()}
    for cid in ("liu2016wear_fig9a_m30nm", "zhang18_fig13_14kN_preload_vs_cycles",
                "eccles2010_fig7c_axial_2p7kN_constant"):
        r = recs.get(cid)
        if r is None:
            continue
        b, n = st.get(cid), com_override(r)
        ident = (b.mae == n.mae and b.maxerr == n.maxerr
                 and b.resid_std == n.resid_std)
        g5 = g5 and ident
        print(f"  {cid[:46]:48} {'bit-identico' if ident else 'MUDOU <<< G5'}")
    print(f"  G5 {'PASSA' if g5 else 'REPROVA'}")
    if not g5:
        falhas.append("G5")

    print("\n" + "=" * 76)
    print("RESUMO: " + ("TODOS OS GATES BLOQUEANTES PASSAM" if not falhas
                        else "REPROVA em " + ", ".join(falhas)))
    print("=" * 76)
    return 0 if not falhas else 1


if __name__ == "__main__":
    raise SystemExit(main())
