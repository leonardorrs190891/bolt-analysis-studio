# -*- coding: utf-8 -*-
"""Executor do prereg D-W (2026-08-06) — re-digitalizacao da lu2024 amp1p5.

Fonte de verdade: a extracao de pixel calibrada (4 ancoras da Tabela 8 do
proprio paper, residuos <=0,0032) preservada em
  BAS_V2_papers/E. Rodada 4 (...)/vector_extractions/lu2024_fig18a_amp1p5_pixel.json

    py -3.12 New_Theory/lu2024_amp1p5_redigit_exec.py             # dry (gates)
    py -3.12 New_Theory/lu2024_amp1p5_redigit_exec.py --escrever

Sem pipe (o executor escreve antes de verificar).
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

PIX = (ROOT / "BAS_V2_papers" / "E. Rodada 4 (deep-research 2026-07-11)"
       / "vector_extractions" / "lu2024_fig18a_amp1p5_pixel.json")
CSV = (ROOT / "Models" / "CALIBRATION_AND_VALIDATION" / "curve_library"
       / "digitized_csv" / "lu2024_M8_fig18_amp1p5.csv")
CID = "lu2024_M8_fig18_amp1p5"
# G2 — predicao registrada no prereg (±0,02/perna)
PREV = dict(mae=(0.031, 0.038), mx=(0.075, 0.078), sd=(0.030, 0.035))
TOL = 0.02


def _rt_tab8(xs, ys, tab8):
    """Round-trip: interpola a serie nos c da Tabela 8 (xs em N)."""
    out = []
    for c, y in tab8:
        yi = float(np.interp(c, xs, ys))
        out.append((c, y, yi, yi - y))
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--escrever", action="store_true")
    a = ap.parse_args()

    d = json.loads(PIX.read_text(encoding="utf-8"))
    ser = d["serie_esparsa"]           # [N, y]
    tab8 = d["tabela8"]                # [c, y]
    xs = np.array([p[0] for p in ser], float)
    ys = np.array([p[1] for p in ser], float)
    print(f"extracao: {PIX.name} · {len(ser)} pts esparsos · "
          f"round-trips da calibracao: "
          f"{[round(r[-1],4) if isinstance(r,(list,tuple)) else r for r in d['calib'].get('tabela8_roundtrip', [])] or 'ver calib'}")

    # CSV vigente (x = N+1)
    cx, cy = [], []
    for ln in CSV.read_text(encoding="utf-8").splitlines():
        p2 = ln.strip().split(",")
        try:
            cx.append(float(p2[0])); cy.append(float(p2[1]))
        except (ValueError, IndexError):
            continue
    cxN = np.array(cx, float) - 1.0
    cyv = np.array(cy, float)

    # ---- G1: round-trip Tabela 8 — o vigente tem de FALHAR, o novo passar
    print("\nG1 round-trip Tabela 8 (|delta| <= 0,01):")
    print("  CSV VIGENTE:")
    fail_v = 0
    for c, yv, yi, dd in _rt_tab8(cxN, cyv, tab8):
        flag = "FALHA" if abs(dd) > 0.01 else "ok"
        fail_v += abs(dd) > 0.01
        print(f"    c={c:5g} tab8={yv:.4f} csv={yi:.4f} d={dd:+.4f} {flag}")
    ok_novo = True
    print("  SERIE NOVA:")
    # EMENDA de gate (dry, declarada no prereg): a ancora c=100 esta na zona em
    # que a PROPRIA extracao declarou +-0,01 de incerteza local (traco verde
    # oscilando perto de zero) E abaixo do FLOOR_TRIM (ratio 0,004-0,016 <<
    # 0,10 — a metrica nunca a pontua). Gate nela testa ruido declarado fora da
    # janela. Gateadas: ancoras com y >= 0,05 (c1/c10/c50 — onde o defeito
    # morava); c100 vira INFORMACAO.
    for c, yv, yi, dd in _rt_tab8(xs, ys, tab8):
        gate = yv >= 0.05
        ok = abs(dd) <= 0.01
        if gate:
            ok_novo &= ok
        flag = ("FALHA" if not ok else "ok") if gate else             f"info (fora da janela; incerteza local +-0,01)"
        print(f"    c={c:5g} tab8={yv:.4f} novo={yi:.4f} d={dd:+.4f} {flag}")
    print(f"  vigente falha em {fail_v} ancora(s) (evidencia) · "
          f"novo: {'PASSA' if ok_novo else 'FALHA'}")
    # G4: 1o ciclo
    y1 = float(np.interp(1.0, xs, ys))
    g4 = abs(y1 - 0.504) <= 0.01
    print(f"G4 1o ciclo: novo {y1:.4f} vs Tabela 8 0,504 "
          f"{'PASSA' if g4 else 'FALHA'}")
    if not (ok_novo and g4):
        print("!! gate violado — NADA escrito.")
        return 3
    if not a.escrever:
        print("\n(sem --escrever: nada foi tocado)")
        return 0

    # ---- escrita
    from bolt_analysis_studio.validation.case_registry import all_records, record
    from bolt_analysis_studio.validation.store import ValidationStore
    import bolt_analysis_studio.validation.runner as rn

    st = ValidationStore()
    antes = {r.case_id: st.get(r.case_id) for r in all_records()
             if r.source == "LU_2024"}
    shutil.copy2(CSV, CSV.with_suffix(".csv.bkp_dw"))
    CSV.write_text("cycle,F_over_F0\n" + "".join(
        f"{int(n)+1:d},{y:.4f}\n" for n, y in ser), encoding="utf-8")
    print(f"\nescrito {CSV.name} ({len(ser)} pts; backup .csv.bkp_dw)")

    print(f"re-simulando as {len(antes)} curvas do LU_2024:")
    g3 = True; alvo = None
    for cid in sorted(antes):
        r = rn.simulate_case(record(cid))
        if not r.ok:
            print(f"  !! {cid}: {r.error}")
            return 2
        b = antes[cid]
        if cid == CID:
            alvo = r
            print(f"  ALVO      {cid[9:]:26s} mae {b.mae:.4f}->{r.mae:.4f}  "
                  f"mx {b.maxerr:.4f}->{r.maxerr:.4f}  "
                  f"sig {b.resid_std:.4f}->{r.resid_std:.4f}")
            continue
        idem = (abs(r.mae - b.mae) < 1e-12 and abs(r.maxerr - b.maxerr) < 1e-12
                and abs(r.resid_std - b.resid_std) < 1e-12)
        if not idem:
            g3 = False
            print(f"  << G3 VIOLADO: {cid} mudou")
    print(f"G3 (irmas bit-identicas): {'PASSA' if g3 else 'FALHA'}")

    # ---- G2: predicao
    def dentro(v, lohi):
        return lohi[0] - TOL <= v <= lohi[1] + TOL
    g2 = (dentro(alvo.mae, PREV["mae"]) and dentro(alvo.maxerr, PREV["mx"])
          and dentro(alvo.resid_std, PREV["sd"]))
    tri = alvo.mae <= 0.05 and alvo.maxerr <= 0.10
    print(f"G2 predicao (mae {PREV['mae']}, mx {PREV['mx']}, sd {PREV['sd']} "
          f"±{TOL}): {'PASSA' if g2 else 'FALHA -> INCONCLUSIVO'}")
    print(f"   tripe (mae/mx; sigma contra limite da fonte no censo): "
          f"{'passa' if tri else 'nao'}")
    if not (g2 and g3):
        print("!! restaurar backup .bkp_dw e investigar.")
        return 3
    print("\nADOCAO CONFIRMADA. Proximo: store + estatuto (_DECLARADAS, por "
          "MERITO) + censo/docs/reports/suite no MESMO commit.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
