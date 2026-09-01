# -*- coding: utf-8 -*-
"""Executor do prereg R2 2026-07-30-zhang18-creep-onset-r2 (G1'-G5').

R2 = engenharia de adocao DENTRO da familia validada na R1 (G2+G3 da R1
provaram mecanismo + generalizacao; a R1 reprovou so no G4 por MAE em 3
curvas). Leitura CONGELADA: A=0.00700, N0=1081 ciclos (t_0=108.1 s @10Hz).
UMA execucao; gates imutaveis; sem iterar.

Com --adotar e PASSA: escreve a config adotada. A re-carimbagem do store e'
do chamador (fingerprint muda -> batch completo + exemplo_m12_sintetico).

Saida: New_Theory/zhang18_creep_onset_exec2.json + prints ASCII.
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
from bolt_analysis_studio.validation.case_registry import (  # noqa: E402
    all_records, record)
from bolt_analysis_studio.validation.store import ValidationStore  # noqa: E402

A_FROZEN = 0.00700
N0_CICLOS = 1081.0
C_TEST = 1.867e-11
LE = "zhang18_fig2_test4_20kN_5e5cyc_preload_vs_cycles"
PREV_SD = {   # sigma' analitico congelado no prereg R2 — G2' confere ±0.005
    "zhang18_fig2_test1_20kN_1e3cyc_preload_vs_cycles": 0.0078,
    "zhang18_fig2_test2_20kN_1e4cyc_preload_vs_cycles": 0.0101,
    "zhang18_fig2_test3_20kN_1e5cyc_preload_vs_cycles": 0.0150,
    "zhang18_fig2_test4_20kN_5e5cyc_preload_vs_cycles": 0.0157,
    "zhang18_fig13_14kN_preload_vs_cycles": 0.0181,
    "zhang18_fig13_20kN_preload_vs_cycles": 0.0118,
    "zhang18_fig13_26kN_preload_vs_cycles": 0.0056,
    "zhang18_fig16_with_locker_preload_vs_cycles": 0.0064,
    "zhang18_fig16_without_locker_preload_vs_cycles": 0.0143,
}
FILA = [LE, "zhang18_fig13_14kN_preload_vs_cycles",
        "zhang18_fig16_without_locker_preload_vs_cycles"]
TOL_G2, TOL_G4 = 0.005, 0.01

_EXTRA: dict = {}
_orig = rn._effective_overrides
rn._effective_overrides = lambda rec, base: {**_orig(rec, base), **_EXTRA}


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

    base = st.get(LE)
    xb = np.asarray(base.metric_x, float)
    pb = np.asarray(base.metric_pred, float)
    h = np.log(xb + N0_CICLOS) - np.log(xb[0] + N0_CICLOS)

    def _A_medido(res):
        d = pb - np.asarray(res.metric_pred, float)
        return float((d @ h) / (h @ h))

    r1 = _sim(LE, C_TEST, t0)
    A1 = _A_medido(r1)
    C_lin = C_TEST * A_FROZEN / A1
    r2 = _sim(LE, C_lin, t0)
    A2 = _A_medido(r2)
    g1_ok = abs(A2 - A_FROZEN) <= 0.10 * A_FROZEN
    print(f"G1': C_test={C_TEST:.3e} -> A1={A1:.5f}; C'={C_lin:.3e} -> "
          f"A2={A2:.5f} (alvo {A_FROZEN:.5f}) "
          f"{'ok' if g1_ok else 'FALHA -> INCONCLUSIVO'}")
    out = {"freq": freq, "t_0": t0, "C_linha": C_lin,
           "G1": {"A1": A1, "A2": A2, "ok": g1_ok}, "curvas": {}}
    if not g1_ok:
        _dump(out)
        return 1

    g2_falhas, g4_pioras = [], []
    for cid in PREV_SD:
        b = st.get(cid)
        r = r2 if cid == LE else _sim(cid, C_lin, t0)
        d_g2 = abs(r.resid_std - PREV_SD[cid])
        if d_g2 > TOL_G2:
            g2_falhas.append((cid, PREV_SD[cid], r.resid_std))
        for rot, va, vb in (("mae", b.mae, r.mae),
                            ("mx", b.maxerr, r.maxerr),
                            ("sd", b.resid_std, r.resid_std)):
            if vb > va + TOL_G4:
                g4_pioras.append((cid, rot, round(va, 4), round(vb, 4)))
        out["curvas"][cid] = {
            "antes": {"mae": b.mae, "mx": b.maxerr, "sd": b.resid_std},
            "depois": {"mae": r.mae, "mx": r.maxerr, "sd": r.resid_std},
            "sd_prev": PREV_SD[cid], "d_g2": d_g2}
        print(f"  {cid[:46]:46s} sd {b.resid_std:.4f}->{r.resid_std:.4f} "
              f"(prev {PREV_SD[cid]:.4f}, d={d_g2:.4f}) mae {r.mae:.4f} "
              f"mx {r.maxerr:.4f}")

    g2_ok = len(g2_falhas) <= 2
    g4_ok = not g4_pioras
    pares = [(r.source, st.get(r.case_id)) for r in all_records()
             if st.get(r.case_id) is not None]
    pisos = rh._pisos_medidos(pares)
    lim_sd = rh.limite_sres("ZHANG_2018", pisos)
    fecha = {}
    for cid in PREV_SD:
        c = out["curvas"][cid]["depois"]
        fecha[cid] = (c["sd"] <= lim_sd and c["mae"] <= rh.META_MAE
                      and c["mx"] <= rh.META_MAX)
    g5_ok = all(fecha[c] for c in FILA)
    out.update({"G2": {"ok": g2_ok, "falhas": g2_falhas},
                "G4": {"ok": g4_ok, "pioras": g4_pioras},
                "G5": {"ok": g5_ok, "lim_sd": lim_sd, "fecha": fecha}})
    passa = g1_ok and g2_ok and g4_ok and g5_ok
    out["PASSA"] = passa
    print(f"\nG2' superposicao: {'ok' if g2_ok else 'FALHA'} "
          f"({len(g2_falhas)} fora de ±{TOL_G2})")
    print(f"G4' acervo: {'ok' if g4_ok else 'FALHA'} {g4_pioras or ''}")
    print(f"G5' fila fecha: {'ok' if g5_ok else 'FALHA'}; fonte inteira "
          f"fecha: {sum(fecha.values())}/9 (lim_sd={lim_sd:.4f})")
    print(f"\n{'PASSA' if passa else 'NAO PASSA'}")

    if passa and "--adotar" in sys.argv:
        cfgp = ROOT / "New_Theory" / "adopted_configs.json"
        cfg = json.loads(cfgp.read_text(encoding="utf-8"))
        ent = cfg["sources"]["ZHANG_2018"]
        ent["cfg"]["C_creep"] = C_lin
        ent["cfg"]["t_0"] = t0
        prov = ("creep com onset lido do residuo (L24): A=0.00700, N0=1081 "
                "ciclos; generalizacao provada na R1 (G3: 8 held, mediana "
                "sigma 0.0242->0.0106, 0 pioras); R2 = selecao viavel sob "
                "acervo completo, gates 4/4; preregs 2026-07-30-zhang18-"
                "creep-onset{,-r2}; adotado por delegacao (mandato "
                "2026-07-30)")
        ent.setdefault("prov", {})["C_creep"] = prov
        ent["prov"]["t_0"] = prov
        cfgp.write_text(json.dumps(cfg, ensure_ascii=False, indent=1),
                        encoding="utf-8")
        print("ADOTADO em adopted_configs.json — re-carimbar o store "
              "INTEIRO + exemplo_m12_sintetico + reports.")
    _dump(out)
    return 0 if passa else 1


def _dump(out):
    p = ROOT / "New_Theory" / "zhang18_creep_onset_exec2.json"
    p.write_text(json.dumps(out, indent=1), encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
