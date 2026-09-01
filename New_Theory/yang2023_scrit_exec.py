# -*- coding: utf-8 -*-
"""EXECUCAO do prereg specs/2026-07-29-yang2023ijpem-scrit-prereg.md.

Ordem OBRIGATORIA (G1): a ancora e' calculada e IMPRESSA na FASE A, antes de
qualquer metrica ser lida. As fases seguintes nao podem alterar s_crit.

  FASE A  le o slip resolvido do ciclo 1 nas 9 amplitudes -> s_crit (media
          GEOMETRICA dos slips de 0,18 e 0,25 mm) + checagem F2 (dentro da bracket)
  FASE B  sonda F4: o canal de afrouxamento CRESCE ao ligar o modo? (2 pontos,
          licao do Beco 2 da D1b — fracao a posteriori nao decide inercia)
  FASE C  fita k_loose_graded SO em 0,25/0,35/0,50
  FASE D  avalia as 4 HELD-OUT (0,30/0,45/0,55/0,65) => G2
  FASE E  G3 (ramo sub-critico intacto) e resumo dos gates

O canonico NAO e' tocado: tudo roda por override em memoria no material.
Prints ASCII (charmap do console Windows).
"""
from __future__ import annotations

import json
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
from bolt_analysis_studio.validation.inputs import (emb_depth_vdi,  # noqa: E402
                                                    frozen_constants,
                                                    geometry_for_case)
from bolt_analysis_studio.validation.store import ValidationStore  # noqa: E402

FONTE = "YANG_2023_IJPEM"
FIT_AMPS = (0.25, 0.35, 0.50)          # onde k e' fitado
HELD_AMPS = (0.30, 0.45, 0.55, 0.65)   # held-out (G2)
SUB_AMPS = (0.15, 0.18)                # ramo sub-critico (G3)
BRACKET = (0.18, 0.25)                 # amplitudes que cercam a transicao


def monta(rec):
    """geom/mat/F0/load como o runner monta — nunca uma 2a implementacao."""
    load = RN._loading_for(rec)
    inp = load["inputs"]
    consts, _ = frozen_constants()
    geom = geometry_for_case(rec.validation_case,
                             grip_mm=inp["grip_mm"]["value"],
                             E=(inp.get("E") or {}).get("value"))
    geom = RN._apply_adopted_geometry(geom, rec.source, rec.case_id,
                                      rec.validation_case.bolt_size)
    ov = RN._effective_overrides(rec, consts)
    mat = JointMaterial(**RN.material_kwargs_for(rec, inp))
    return geom, mat, float(rec.validation_case.initial_preload_N), load, ov


def casos():
    out = {}
    for rec in all_records():
        if rec.source != FONTE:
            continue
        load = RN._loading_for(rec)
        out[round(float(load["delta_mm"]), 3)] = rec
    return out


def main() -> int:
    st = ValidationStore()
    cs = casos()
    print(f"casos do {FONTE}: {len(cs)} amplitudes {sorted(cs)}\n")

    # =============== FASE A — A ANCORA (antes de qualquer metrica) ===========
    print("=" * 72)
    print("FASE A — ANCORA (G1: nada de metrica olhado ainda)")
    print("=" * 72)
    slips = {}
    for amp in sorted(cs):
        rec = cs[amp]
        geom, mat, F0, load, _ov = monta(rec)
        ana = DynamicStiffnessAnalyzer(geom, mat, F0)
        s = resolve_transverse_slip(ana.state, mat, load["F_amp_N"],
                                   load["theta"], delta_amp=amp * 1e-3,
                                   geom=geom)
        slips[amp] = float(s)
        print(f"  delta={amp:5.2f} mm  F0={F0/1e3:5.1f} kN  "
              f"slip(ciclo 1)={s*1e6:8.2f} um")
    lo, hi = slips[BRACKET[0]], slips[BRACKET[1]]
    if lo <= 0 or hi <= 0:
        print(f"\n  F2 FALSIFICA: slip nao-positivo na bracket "
              f"({lo*1e6:.3f}, {hi*1e6:.3f} um) - o engine poe 0,25 mm em STICK.")
        print("  Media geometrica de zeros nao e' ancora. PARA aqui, por F2:")
        print("  'corrigir a conversao antes de qualquer conclusao sobre a forma'")
        # DIAGNOSTICO: decompor o onset diz QUAL termo desalinha o limiar.
        print("\n  onset = delta_free + F_slip/k_tr, por subgrupo:")
        vis = set()
        for a in sorted(cs):
            geom, mat, F0, load, _o = monta(cs[a])
            ana = DynamicStiffnessAnalyzer(geom, mat, F0)
            el = F_slip_transverse(ana.state, mat) / k_tr_transverse(geom, mat)
            chave = round(mat.delta_free, 9)
            if chave in vis:
                continue
            vis.add(chave)
            print(f"    F0={F0/1e3:5.1f} kN  delta_free={mat.delta_free*1e6:6.1f}"
                  f"  F_slip/k_tr={el*1e6:5.1f}"
                  f"  ONSET={(mat.delta_free+el)*1e6:6.1f} um")
        print("\n  O DADO troca de regime entre 0,18 e 0,25 mm (0,93 -> 0,52).")
        print("  Para o onset cair nessa janela: delta_free em (96, 166) um.")
        print("  Adotado no m8 = 180 um => FORA. No m6 = 150 um => dentro.")
        print("  => A VARREDURA ANCORA delta_free, NAO s_crit_loose.")
        print("  Resultado completo: New_Theory/yang2023_scrit_resultado.md")
        return 1
    s_crit = float(np.sqrt(lo * hi))
    print(f"\n  bracket de slip [{lo*1e6:.2f}, {hi*1e6:.2f}] um "
          f"(x{hi/lo:.2f})")
    print(f"  s_crit_loose = media GEOMETRICA = {s_crit*1e6:.2f} um "
          f"= {s_crit:.6e} m")
    f2_ok = lo <= s_crit <= hi
    print(f"  F2 (s_crit dentro da bracket): {'ok' if f2_ok else 'FALSIFICA'}")
    if not f2_ok:
        return 1
    ancora = dict(s_crit_m=s_crit, bracket_um=[lo * 1e6, hi * 1e6],
                  slips_um={str(k): v * 1e6 for k, v in slips.items()})
    (RAIZ / "New_Theory" / "yang2023_scrit_ancora.json").write_text(
        json.dumps(ancora, indent=1), encoding="utf-8")
    print("  ancora CONGELADA em New_Theory/yang2023_scrit_ancora.json")

    # =============== FASE B — sonda F4 (o canal cresce?) ====================
    print("\n" + "=" * 72)
    print("FASE B — sonda F4: o canal de afrouxamento CRESCE ao ligar o modo?")
    print("=" * 72)

    def simula(rec, k_graded, n_cap=None):
        """re-simula 1 caso com o modo graduado ligado; devolve metricas."""
        ov = {"loose_rate_mode": "graded_scrit", "s_crit_loose": s_crit,
              "k_loose_graded": float(k_graded)}
        orig = RN._effective_overrides

        def patched(r, consts):
            d = dict(orig(r, consts))
            if r.source == FONTE:
                d.update(ov)
            return d
        RN._effective_overrides = patched
        try:
            return RN.simulate_case(rec, n_cap=n_cap)
        finally:
            RN._effective_overrides = orig

    probe = cs[0.35]
    base = st.get(probe.case_id)
    for k in (0.0, 1.0):
        r = simula(probe, k)
        lo_ch = (r.decomp or {}).get("rotational_loosening")
        v = abs(float(np.asarray(lo_ch, float)[-1])) if lo_ch is not None else 0.0
        print(f"  k_loose_graded={k:4.1f}  canal rotacional final={v:8.4f} kN"
              f"  MAE={r.mae:.4f}")
    print("  (k=0 => branch nunca roda, por design do engine: bit-identico)")

    # =============== FASE C — fit de k nas 3 amplitudes =====================
    print("\n" + "=" * 72)
    print("FASE C — fit de k_loose_graded SO em " + str(FIT_AMPS))
    print("=" * 72)
    grade = [0.0, 0.05, 0.1, 0.2, 0.35, 0.5, 0.75, 1.0, 1.5, 2.0, 3.0, 5.0]
    melhor, melhor_k = None, None
    for k in grade:
        errs = []
        for amp in FIT_AMPS:
            r = simula(cs[amp], k)
            if r.maxerr is None:
                errs = None
                break
            errs.append(r.maxerr)
        if not errs:
            continue
        med = float(np.median(errs))
        print(f"  k={k:5.2f}  res.max das 3 fitadas: "
              + " ".join(f"{e:.4f}" for e in errs) + f"  mediana={med:.4f}")
        if melhor is None or med < melhor:
            melhor, melhor_k = med, k
    print(f"\n  k_loose_graded ESCOLHIDO = {melhor_k} "
          f"(mediana res.max das fitadas {melhor:.4f})")

    # =============== FASE D — held-out (G2) ================================
    print("\n" + "=" * 72)
    print("FASE D — HELD-OUT " + str(HELD_AMPS) + "  => G2")
    print("=" * 72)
    print(f"  {'amp':>5} {'res.max antes':>14} {'depois':>9} {'delta':>9}")
    antes_h, depois_h = [], []
    for amp in HELD_AMPS:
        b = st.get(cs[amp].case_id)
        n = simula(cs[amp], melhor_k)
        antes_h.append(b.maxerr)
        depois_h.append(n.maxerr)
        print(f"  {amp:5.2f} {b.maxerr:14.4f} {n.maxerr:9.4f} "
              f"{n.maxerr-b.maxerr:+9.4f}")
    ma, md = float(np.median(antes_h)), float(np.median(depois_h))
    g2 = md < ma
    print(f"\n  mediana res.max held-out: {ma:.4f} -> {md:.4f}  "
          f"({md-ma:+.4f})")
    print(f"  G2 {'PASSA' if g2 else 'REPROVA'} "
          f"(exige queda da mediana das held-out)")

    # =============== FASE E — G3 + resumo ==================================
    print("\n" + "=" * 72)
    print("FASE E — G3 (ramo sub-critico) e resumo")
    print("=" * 72)
    g3 = True
    for amp in SUB_AMPS:
        b = st.get(cs[amp].case_id)
        n = simula(cs[amp], melhor_k)
        okb = R._tripe_ok(b)
        okn = (n.mae <= R.META_MAE and n.maxerr <= R.META_MAX
               and n.resid_std is not None and n.resid_std <= R.META_SRES)
        g3 = g3 and okn
        print(f"  delta={amp:5.2f}  tripe antes={okb}  depois={okn}  "
              f"(MAE {b.mae:.4f}->{n.mae:.4f}, sd {b.resid_std:.4f}->"
              f"{n.resid_std:.4f})")
    print(f"  G3 {'PASSA' if g3 else 'REPROVA'}")
    print("\n  RESUMO: F2 ok . G1 ok (ancora antes das metricas) . "
          f"G2 {'PASSA' if g2 else 'REPROVA'} . G3 {'PASSA' if g3 else 'REPROVA'}")
    print("  G4 (resto do store) e G5 (transferencia) na proxima passada.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
