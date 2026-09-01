# -*- coding: utf-8 -*-
"""Executor do prereg 2026-07-30-zhang18-creep-onset (gates G1-G5).

Leitura CONGELADA no prereg: A=0.01261, N0=562 ciclos (=> t_0=N0/freq).
Este script NAO re-otimiza nada — calibra o mapa A->C_creep (G1), simula as
9 curvas com (C', t_0) e confere G2-G5. Com --adotar e PASSA, escreve a
config adotada (procedencia por delegacao) — a re-carimbagem do store e
regeneracao de reports ficam para o chamador (batch completo: o fingerprint
cobre as configs adotadas, entao TODO o store re-carimba).

Saida: New_Theory/zhang18_creep_onset_exec.json + prints ASCII.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import bolt_analysis_studio.validation.report_html as rh   # noqa: E402
import bolt_analysis_studio.validation.runner as rn        # noqa: E402
from bolt_analysis_studio.calibration.holdout import (      # noqa: E402
    HoldoutSplit, veredicto_generalizacao)
from bolt_analysis_studio.validation.case_registry import (  # noqa: E402
    all_records, record)
from bolt_analysis_studio.validation.store import ValidationStore  # noqa: E402

# ---- constantes CONGELADAS no prereg (nao mexer) ---------------------------
A_FROZEN = 0.01261
N0_CICLOS = 562.0
C_TEST = 1.867e-11          # ponto de partida da calibracao (shared)
LE = "zhang18_fig2_test4_20kN_5e5cyc_preload_vs_cycles"
PREV = {   # previsoes analiticas congeladas (sigma') — G2 confere ±0.005
    "zhang18_fig2_test4_20kN_5e5cyc_preload_vs_cycles": 0.0070,
    "zhang18_fig13_14kN_preload_vs_cycles": 0.0126,
    "zhang18_fig13_20kN_preload_vs_cycles": 0.0082,
    "zhang18_fig13_26kN_preload_vs_cycles": 0.0116,
    "zhang18_fig16_with_locker_preload_vs_cycles": 0.0185,
    "zhang18_fig16_without_locker_preload_vs_cycles": 0.0098,
    "zhang18_fig2_test1_20kN_1e3cyc_preload_vs_cycles": 0.0091,
    "zhang18_fig2_test2_20kN_1e4cyc_preload_vs_cycles": 0.0105,
    "zhang18_fig2_test3_20kN_1e5cyc_preload_vs_cycles": 0.0091,
}
FILA = [LE, "zhang18_fig13_14kN_preload_vs_cycles",
        "zhang18_fig16_without_locker_preload_vs_cycles"]
TOL_G2, TOL_G34 = 0.005, 0.01

_EXTRA: dict = {}
_orig = rn._effective_overrides
rn._effective_overrides = lambda rec, base: {**_orig(rec, base), **_EXTRA}


def _g_anch(x, N0):
    return np.log(x + N0) - np.log(x[0] + N0)


def _sim(cid, C, t0):
    _EXTRA.clear()
    _EXTRA.update({"C_creep": C, "t_0": t0})
    try:
        return rn.simulate_case(record(cid))
    finally:
        _EXTRA.clear()


def main() -> int:
    st = ValidationStore()
    freq = record(LE).validation_case.frequency_Hz
    t0 = N0_CICLOS / freq
    print(f"freq={freq} Hz -> t_0={t0:.1f} s (N0={N0_CICLOS:.0f} ciclos)")

    # ---- G1: mapa A->C linear ---------------------------------------------
    base = st.get(LE)
    xb = np.asarray(base.metric_x, float)
    pb = np.asarray(base.metric_pred, float)

    def _A_medido(res):
        p = np.asarray(res.metric_pred, float)
        h = _g_anch(xb, N0_CICLOS)
        d = pb - p                      # perda ADICIONAL vs baseline adotado
        return float((d @ h) / (h @ h))

    r1 = _sim(LE, C_TEST, t0)
    A1 = _A_medido(r1)
    C_lin = C_TEST * A_FROZEN / A1
    r2 = _sim(LE, C_lin, t0)
    A2 = _A_medido(r2)
    g1_ok = abs(A2 - A_FROZEN) <= 0.10 * A_FROZEN
    print(f"G1: C_test={C_TEST:.3e} -> A1={A1:.5f}; "
          f"C'={C_lin:.3e} -> A2={A2:.5f} (alvo {A_FROZEN:.5f}) "
          f"{'ok' if g1_ok else 'FALHA -> INCONCLUSIVO'}")
    out = {"freq": freq, "t_0": t0, "C_linha": C_lin,
           "G1": {"A1": A1, "A2": A2, "ok": g1_ok}, "curvas": {}}
    if not g1_ok:
        _dump(out)
        return 1

    # ---- sims das 9 + G2/G3/G4/G5 -----------------------------------------
    antes_sd, depois_sd = {}, {}
    g2_falhas, g4_pioras = [], []
    for cid in PREV:
        b = st.get(cid)
        r = r2 if cid == LE else _sim(cid, C_lin, t0)
        antes_sd[cid] = b.resid_std
        depois_sd[cid] = r.resid_std
        d_g2 = abs(r.resid_std - PREV[cid])
        if d_g2 > TOL_G2:
            g2_falhas.append((cid, PREV[cid], r.resid_std))
        for rot, va, vb in (("mae", b.mae, r.mae),
                            ("mx", b.maxerr, r.maxerr),
                            ("sd", b.resid_std, r.resid_std)):
            if vb > va + TOL_G34:
                g4_pioras.append((cid, rot, va, vb))
        out["curvas"][cid] = {
            "antes": {"mae": b.mae, "mx": b.maxerr, "sd": b.resid_std},
            "depois": {"mae": r.mae, "mx": r.maxerr, "sd": r.resid_std},
            "sd_prev": PREV[cid], "d_g2": d_g2,
        }
        print(f"  {cid[:46]:46s} sd {b.resid_std:.4f}->{r.resid_std:.4f} "
              f"(prev {PREV[cid]:.4f}, d={d_g2:.4f}) mae {r.mae:.4f} "
              f"mx {r.maxerr:.4f}")

    g2_ok = len(g2_falhas) <= 2
    split = HoldoutSplit(
        criterio="resolucao da cauda: >=4 pontos alem de 200k le; "
                 "cauda esparsa segura",
        reads=(LE,), held=tuple(c for c in PREV if c != LE))
    g3 = veredicto_generalizacao(antes_sd, depois_sd, split, tol=TOL_G34)
    g4_ok = not g4_pioras

    pares = [(r.source, st.get(r.case_id)) for r in all_records()
             if st.get(r.case_id) is not None]
    pisos = rh._pisos_medidos(pares)
    lim_sd = rh.limite_sres("ZHANG_2018", pisos)
    g5_fecha = []
    for cid in FILA:
        c = out["curvas"][cid]["depois"]
        g5_fecha.append(c["sd"] <= lim_sd and c["mae"] <= rh.META_MAE
                        and c["mx"] <= rh.META_MAX)
    g5_ok = all(g5_fecha)

    out.update({"G2": {"ok": g2_ok, "falhas": g2_falhas},
                "G3": g3, "G4": {"ok": g4_ok, "pioras": g4_pioras},
                "G5": {"ok": g5_ok, "lim_sd": lim_sd,
                       "fila": dict(zip(FILA, g5_fecha))}})
    passa = g1_ok and g2_ok and g3["generaliza"] and g4_ok and g5_ok
    out["PASSA"] = passa
    print(f"\nG2 superposicao: {'ok' if g2_ok else 'FALHA'} "
          f"({len(g2_falhas)} fora de ±{TOL_G2})")
    print(f"G3 generaliza: {g3['generaliza']} (mediana held "
          f"{g3['mediana_held_antes']:.4f}->{g3['mediana_held_depois']:.4f}, "
          f"pioras={list(g3['pioras_held'])})")
    print(f"G4 acervo: {'ok' if g4_ok else f'FALHA {g4_pioras}'}")
    print(f"G5 fila fecha: {'ok' if g5_ok else dict(zip(FILA, g5_fecha))} "
          f"(lim_sd={lim_sd:.4f})")
    print(f"\n{'PASSA' if passa else 'NAO PASSA'}")

    if passa and "--adotar" in sys.argv:
        cfgp = ROOT / "New_Theory" / "adopted_configs.json"
        cfg = json.loads(cfgp.read_text(encoding="utf-8"))
        ent = cfg["sources"]["ZHANG_2018"]
        ent["cfg"]["C_creep"] = C_lin
        ent["cfg"]["t_0"] = t0
        ent.setdefault("prov", {})["C_creep"] = (
            "onset lido do residuo (L24), held-out 8 curvas generaliza; "
            "prereg 2026-07-30-zhang18-creep-onset; adotado por delegacao "
            "(mandato 2026-07-30)")
        ent["prov"]["t_0"] = ent["prov"]["C_creep"]
        cfgp.write_text(json.dumps(cfg, ensure_ascii=False, indent=1),
                        encoding="utf-8")
        print("ADOTADO em adopted_configs.json — re-carimbar o store INTEIRO "
              "(fingerprint muda) + exemplo_m12_sintetico direto + reports.")
    _dump(out)
    return 0 if passa else 1


def _dump(out):
    p = ROOT / "New_Theory" / "zhang18_creep_onset_exec.json"
    p.write_text(json.dumps(out, indent=1), encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
