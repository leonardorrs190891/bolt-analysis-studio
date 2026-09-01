# -*- coding: utf-8 -*-
"""Probe da DERIVA TARDIA (cluster liu2016/zhang18/li2022ti, achado do D2').

Duas perguntas, ambas respondiveis do store (zero simulacao):
  P1  qual mecanismo carrega a taxa de perda do MODELO alem de 200k, e ela
      esta saturando? (decomposicao gravada no store)
  P2  a CAUDA DO DADO segue log(N) (a lei de creep do engine) ou uma
      potencia N^m (Norton-Bailey)? Fit das duas formas na janela tardia,
      comparado pelo RMS -- e o mesmo fit no MODELO como controle (o modelo
      tem que sair log-like por construcao).

Saida: New_Theory/deriva_tardia_probe.json + prints ASCII.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bolt_analysis_studio.validation.store import ValidationStore  # noqa: E402

CLUSTER = [
    "liu2016wear_fig7_run1_1e6cyc",
    "liu2016wear_fig7_run2_5e6cyc",
    "liu2016wear_fig9a_m30nm",
    "liu2016wear_fig9a_m40nm",
    "zhang18_fig2_test4_20kN_5e5cyc_preload_vs_cycles",
    "zhang18_fig13_14kN_preload_vs_cycles",
    "zhang18_fig16_without_locker_preload_vs_cycles",
    "li2022ti_axial_10Hz_full",
]
CUT = 200_000.0


def _fit_rms(x, y, basis):
    A = np.vstack([basis(x), np.ones_like(x)]).T
    coef, *_ = np.linalg.lstsq(A, y, rcond=None)
    return float(np.sqrt(np.mean((A @ coef - y) ** 2))), [float(c) for c in coef]


def main() -> int:
    st = ValidationStore()
    out = {"cut": CUT, "casos": {}}
    for cid in CLUSTER:
        r = st.get(cid)
        if r is None:
            print(f"AVISO: {cid} ausente do store — pulado")
            continue
        d = r.to_dict()
        row: dict = {}

        # ---- P1: decomposicao tardia do modelo -----------------------------
        # decomp = fracoes CUMULATIVAS de perda por mecanismo, no grid
        # d["cycles"] (400 pts) — o eixo mora no registro, nao no dict.
        dec = d.get("decomp") or {}
        cx = np.asarray(d.get("cycles") or [], float)
        if dec and cx.size:
            m = cx > CUT
            if m.sum() >= 2:
                tard, tot_t = {}, 0.0
                for k, v in dec.items():
                    v = np.asarray(v, float)
                    dv = float(v[-1] - v[m][0])   # perda so na cauda
                    tard[k] = dv
                    tot_t += dv
                row["late_share"] = {k: (v / tot_t if tot_t else 0.0)
                                     for k, v in tard.items()}
                row["late_total_frac"] = tot_t   # fracao de F0 perdida na cauda
        if "late_share" not in row:
            row["late_share"] = None  # curva sem cauda alem do corte

        # ---- P2: forma funcional da cauda (dado vs modelo) -----------------
        x = np.asarray(r.metric_x, float)
        pd = np.asarray(r.metric_pred, float)
        dt = np.asarray(r.metric_data, float)
        m = x > CUT
        row["n_tail"] = int(m.sum())
        if m.sum() >= 4:
            xt = x[m]
            for rot, y in (("dado", dt[m]), ("modelo", pd[m])):
                rms_log, c_log = _fit_rms(xt, y, np.log)
                best = {"m": None, "rms": np.inf}
                for mm in (0.1, 0.2, 0.3, 0.4, 0.5):
                    rms_p, c_p = _fit_rms(xt, y, lambda v, mm=mm: v ** mm)
                    if rms_p < best["rms"]:
                        best = {"m": mm, "rms": rms_p, "coef": c_p}
                row[f"fit_{rot}"] = {
                    "rms_log": rms_log, "slope_log": c_log[0],
                    "rms_pow": best["rms"], "m_pow": best["m"],
                    "veredicto": ("pow" if best["rms"] < 0.8 * rms_log
                                  else "log" if rms_log < 0.8 * best["rms"]
                                  else "empate"),
                }
        out["casos"][cid] = row

    p = ROOT / "New_Theory" / "deriva_tardia_probe.json"
    p.write_text(json.dumps(out, indent=1), encoding="utf-8")

    print(f"{'curva':34s} {'late share (top2)':32s} {'dado':>7s} {'modelo':>7s}")
    for cid, row in out["casos"].items():
        ls = row.get("late_share")
        if ls:
            top = sorted(ls.items(), key=lambda kv: -abs(kv[1]))[:2]
            s = " ".join(f"{k}={v:.0%}" for k, v in top)
        else:
            s = "(sem decomp no store)"
        fd = row.get("fit_dado", {}).get("veredicto", "-")
        fm = row.get("fit_modelo", {}).get("veredicto", "-")
        print(f"{cid[:34]:34s} {s:32s} {fd:>7s} {fm:>7s}")
    print("\n(veredicto: 'pow' = cauda power-law, 'log' = cauda log, "
          "'empate' = <20% de diferenca de RMS)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
