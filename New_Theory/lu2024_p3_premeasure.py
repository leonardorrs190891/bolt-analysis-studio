# -*- coding: utf-8 -*-
"""P3 do plano LU_2024 — premeasure da re-leitura com as ancoras do paper.

ANCORAS (lidas do PDF, lu2024_plano_melhoria.md A3):
  T8/T9 (1o ciclo): perda fracional apos o ciclo 1 —
    Tabela 8 (22 N.m, por amplitude): 0.25mm=17.1% 0.5=36.2% 1.0=36.8%
                                      1.5=49.6% 2.0=50.2%
    Tabela 9 (1.0 mm, por torque):    4Nm=16.2% 10=36.2% 16=35.9%
                                      22=36.8% 28=38.3%
  Fig21 (rigidez tangencial inicial por torque, N/mm):
    4Nm=5.0438e4 10=8.5500e4 16=9.2083e4 22=9.8404e4 28=11.52e4

HISTORIA DE PARAMETROS (a testar, nao a assumir):
  perda_1o_ciclo = ESTATICA (emb_depth, VDI ~11um — hoje ZERADA na config)
                 + FRACIONAL (emb_load_frac) gateada por slip
                   (emb_slip_gate q — hoje OFF; e' o que ordena por amplitude)
  Previsoes qualitativas ANTES de rodar:
    - amp0p25 (slip~0 com delta_free=0.28): so estatica => ~17% pede
      emb_depth ~VDI e NAO ~0;
    - T4 (F0=2105, slip fundo): 16.2% << 36% dos demais torques — a fracional
      NAO e' F0-flat no T4; candidato: o gate de slip tambem morde via
      delta_t ∝ F0 (slip ENORME a F0 baixo => gate satura ~1; entao por que
      16%? — talvez a ESTATICA ~F0-prop: 11um*k_b/F0 e' fracao MAIOR a F0
      baixo, nao menor... MEDIR, nao teorizar).
  c_bend: ancorar k_tr do modelo na Fig21 (leitura direta por torque).

Este script: (1) mede a perda de 1o ciclo do modelo em grade
{emb_depth, emb_load_frac, emb_slip_gate} x 9 condicoes (sims de 1-3
ciclos, baratissimas) e compara com T8/T9; (2) mede k_tr efetivo do engine
por torque em grade de c_bend e compara com Fig21. SO-LEITURA (nada
escrito em config); a saida alimenta o prereg do P3.

Saida: lu2024_p3_premeasure.json + tabelas ASCII.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import bolt_analysis_studio.validation.runner as rn        # noqa: E402
from bolt_analysis_studio.validation.case_registry import (  # noqa: E402
    all_records, record)

# (condicao, case_id, perda fracional apos ciclo 1 — Tabelas 8/9)
T89 = [
    ("18_amp0p25", "lu2024_M8_fig18_amp0p25", 0.171),
    ("18_amp0p5",  "lu2024_M8_fig18_amp0p5",  0.362),
    ("18_amp1p0",  "lu2024_M8_fig18_amp1p0",  0.368),
    ("18_amp1p5",  "lu2024_M8_fig18_amp1p5",  0.496),
    ("18_amp2p0",  "lu2024_M8_fig18_amp2p0",  0.502),
    ("20_T4",      "lu2024_M8_fig20_T4Nm",    0.162),
    ("20_T10",     "lu2024_M8_fig20_T10Nm",   0.362),
    ("20_T16",     "lu2024_M8_fig20_T16Nm",   0.359),
    ("20_T28",     "lu2024_M8_fig20_T28Nm",   0.383),
]
FIG21 = {4: 5.0438e4, 10: 8.5500e4, 16: 9.2083e4, 22: 9.8404e4, 28: 11.52e4}
T_CASE = {4: "lu2024_M8_fig20_T4Nm", 10: "lu2024_M8_fig20_T10Nm",
          16: "lu2024_M8_fig20_T16Nm", 22: "lu2024_M8_fig20_T22Nm",
          28: "lu2024_M8_fig20_T28Nm"}

_EXTRA: dict = {}
_orig = rn._effective_overrides
rn._effective_overrides = lambda rec, base: {**_orig(rec, base), **_EXTRA}


def _ratio_no_ciclo1(cid, ov):
    """Simula a curva com n_cap=3 e devolve o ratio no ciclo 1 (cru)."""
    _EXTRA.clear()
    _EXTRA.update(ov)
    try:
        res = rn.simulate_case(record(cid), n_cap=3)
        d = res.to_dict()
        cyc = d.get("cycles") or []
        rat = d.get("ratio") or []
        for x, r in zip(cyc, rat):
            if x >= 1.0:
                return float(r)
        return float(rat[-1]) if rat else float("nan")
    finally:
        _EXTRA.clear()


def main() -> int:
    out = {"ciclo1": [], "k_tr": []}

    # ---- 1. grade do 1o ciclo ---------------------------------------------
    grade = []
    for emb_um in (0.0, 6.0, 11.0, 16.0):
        for frac in (0.30, 0.40, 0.50, 0.55):
            for q in (0.0, 0.5, 1.0, 2.0):
                grade.append((emb_um, frac, q))
    print(f"grade 1o ciclo: {len(grade)} pontos x {len(T89)} condicoes")
    melhor = None
    for emb_um, frac, q in grade:
        ov = {"emb_depth": emb_um * 1e-6, "emb_load_frac": frac,
              "emb_slip_gate": q}
        errs = []
        det = {}
        for rot, cid, alvo in T89:
            r1 = _ratio_no_ciclo1(cid, ov)
            perda = 1.0 - r1
            errs.append(abs(perda - alvo))
            det[rot] = round(perda, 3)
        mae = sum(errs) / len(errs)
        out["ciclo1"].append({"emb_um": emb_um, "frac": frac, "q": q,
                              "mae_c1": mae, "det": det})
        if melhor is None or mae < melhor["mae_c1"]:
            melhor = out["ciclo1"][-1]
        print(f"  emb={emb_um:4.1f}um frac={frac:.2f} q={q:.1f} "
              f"MAE(c1)={mae:.4f}")
    print(f"\nMELHOR c1: emb={melhor['emb_um']}um frac={melhor['frac']} "
          f"q={melhor['q']} MAE={melhor['mae_c1']:.4f}")
    print("  perdas por condicao (modelo vs alvo):")
    for rot, cid, alvo in T89:
        print(f"    {rot:10s} {melhor['det'][rot]:.3f} vs {alvo:.3f}")

    # ---- 2. k_tr por torque vs Fig21 (leitura de c_bend) -------------------
    # k_tr efetivo do engine: rigidez do ramo transversal no estado virgem.
    # Medimos EMPIRICO: F_slip/delta_t do primeiro ciclo nao e' exposto;
    # entao usamos a via analitica do engine se disponivel, senao pulamos
    # para o prereg com a sonda dedicada.
    try:
        from bolt_analysis_studio.numerical import dynamic_stiffness_analyzer as dsa
        import inspect
        fn = [n for n, f in vars(dsa).items()
              if callable(f) and "k_tr" in n.lower()]
        print("\nfuncoes k_tr no engine:", fn)
        out["k_tr_funcs"] = fn
    except Exception as e:
        print("inspecao k_tr falhou:", e)

    (ROOT / "New_Theory" / "lu2024_p3_premeasure.json").write_text(
        json.dumps(out, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
