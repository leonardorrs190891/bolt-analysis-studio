"""Checks de OVERFIT do ground-fit axial (pergunta do professor, 2026-07-08):
"curve fit ou model improvement? como checar overfit?"

Bateria (todas analiticas, formas fechadas do canal axial — instantaneo):
  1. LOCO por preload: fit em 4 curvas, prediz a 5a (15/21 kN = EXTRAPOLACAO).
  2. Escada de parcimonia + BIC: 0-param (zero-refit) / 2-param (so expoentes) /
     3-param (+C_creep) / 5-param (ground-fit).
  3. Residuos: MAE vs piso de digitizacao (~0.003-0.005) + estrutura por F0.
  4. Out-of-sample REAL: o sweep A_F (4 curvas, F0=18) NUNCA visto pelo fit —
     o bloco fitado prediz com zero liberdade (a dependencia de A_F em si e' a
     forma faltante conhecida §4.6 — reportada, nao escondida).
  5. Estabilidade: refit em metades impar/par dos pontos.

Run: python New_Theory/axial_overfit_checks.py
"""
from __future__ import annotations
import sys
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "New_Theory"))
from axial_ground_fit import load, fit, model_curve, sse, P0, DIG  # noqa: E402
from library_common import load_full_curve  # noqa: E402

AF = [("7p5kN", 7.5e3), ("8p75kN", 8.75e3), ("11p25kN", 11.25e3), ("12p5kN", 12.5e3)]


def mae_curve(F0, cyc, r, p):
    return float(np.mean(np.abs(model_curve(F0, cyc, *p) - r)))


def n_points(data):
    return sum(len(c) for _, c, _ in data)


def bic(params_k, data, p):
    n = n_points(data)
    return n * np.log(max(sse(p, data), 1e-12) / n) + params_k * np.log(n)


def fit_subset(data, free):
    """Fit so os indices `free` (demais fixos nos priors handbook/UFU)."""
    base = [3.5e-6, 50.0, 1.8667e-11, 4.0, 2.0]
    grids = [np.linspace(2.5e-6, 5.0e-6, 26), np.linspace(10, 90, 33),
             np.linspace(0.8e-11, 2.4e-11, 33), np.linspace(2.0, 6.0, 33),
             np.linspace(0.5, 4.0, 36)]
    best = list(base)
    for _ in range(6):
        for i in free:
            vals = []
            for v in grids[i]:
                p = list(best); p[i] = float(v)
                vals.append((sse(p, data), float(v)))
            best[i] = min(vals)[1]
    return best


def main():
    data = load()
    p_full = fit(data)

    # ---- 1. LOCO por preload ----
    print("== 1. LOCO por preload (fit em 4, prediz a 5a) ==")
    print(f"{'held-out':>9s} {'MAE in-fit':>11s} {'MAE held-out':>13s} {'razao':>7s}  tipo")
    ratios = []
    for i, (F0, cyc, r) in enumerate(data):
        sub = [d for j, d in enumerate(data) if j != i]
        p_i = fit(sub)
        m_in = mae_curve(F0, cyc, r, p_full)
        m_out = mae_curve(F0, cyc, r, p_i)
        kind = "EXTRAPOLA" if i in (0, len(data) - 1) else "interpola"
        ratios.append(m_out / max(m_in, 1e-9))
        print(f"{F0/1e3:8.1f}k {m_in:11.4f} {m_out:13.4f} {m_out/max(m_in,1e-9):7.2f}  {kind}")
    print(f"  razao mediana held-out/in-fit = {np.median(ratios):.2f} "
          f"(overfit grosseiro => >>2-3; estrutura real => ~1)")

    # ---- 2. Escada de parcimonia + BIC ----
    print("\n== 2. Escada de parcimonia (todas as ~amostras) ==")
    ladder = [("0-param (zero-refit rev.2)", [], [3.5e-6, 50.0, 1.8667e-11, 0.0, 0.0]),
              ("2-param (exp_f, exp_s)", [3, 4], None),
              ("3-param (+C_creep)", [2, 3, 4], None),
              ("5-param (ground-fit)", [0, 1, 2, 3, 4], None)]
    print(f"{'variante':>28s} {'k':>3s} {'MAE':>8s} {'BIC':>9s}")
    for name, free, fixed in ladder:
        p = fixed if fixed is not None else fit_subset(data, free)
        m = float(np.mean([mae_curve(F0, c, r, p) for F0, c, r in data]))
        b = bic(len(free), data, p)
        print(f"{name:>28s} {len(free):3d} {m:8.4f} {b:9.1f}")
    print("  (BIC menor = melhor; se 5-param nao ganha do 2/3-param, os dof extras nao pagam)")

    # ---- 3. Residuos ----
    print("\n== 3. Residuos vs piso de ruido ==")
    res_by = []
    for F0, cyc, r in data:
        res = model_curve(F0, cyc, *p_full) - r
        res_by.append((F0, float(np.mean(res)), float(np.mean(np.abs(res)))))
    for F0, mu, ma in res_by:
        print(f"  F0={F0/1e3:4.1f}k  residuo medio={mu:+.4f}  MAE={ma:.4f}")
    print("  piso de digitizacao ~0.003-0.005: MAE NO piso = saudavel; MUITO abaixo = comendo ruido.")
    print("  estrutura por F0: monotona => forma errada; alternada/1-outlier => scatter.")

    # ---- 4. Out-of-sample: sweep A_F (nunca visto) ----
    print("\n== 4. Out-of-sample REAL: sweep A_F @F0=18kN (fit nunca viu) ==")
    for tag, F_amp in AF:
        cyc, r = load_full_curve(f"{DIG}/liu2017_axial_AF_{tag}.csv")
        r = r / r[0]
        m = mae_curve(18e3, cyc[1:], r[1:], p_full)
        print(f"  AF={F_amp/1e3:5.2f}kN  MAE={m:.4f}  fim dado={r[-1]:.3f} "
              f"pred={model_curve(18e3, cyc[-1:], *p_full)[0]:.3f}")
    print("  NB: o modelo e' A_F-cego neste canal (forma faltante §4.6) => deve acertar")
    print("  o MEIO do sweep (A_F~10, condicao compartilhada) e errar as pontas pelo")
    print("  gradiente conhecido. Se acerta o meio, o BLOCO fitado generaliza.")

    # ---- 5. Estabilidade impar/par ----
    print("\n== 5. Estabilidade: refit em metades impar/par dos pontos ==")
    halves = []
    for k in (0, 1):
        sub = [(F0, c[k::2], r[k::2]) for F0, c, r in data]
        halves.append(fit(sub))
    names = ["emb_cap", "N_emb", "C_creep", "exp_f", "exp_s"]
    print(f"{'const':>9s} {'full':>10s} {'half-A':>10s} {'half-B':>10s}")
    for i, nm in enumerate(names):
        print(f"{nm:>9s} {p_full[i]:10.3g} {halves[0][i]:10.3g} {halves[1][i]:10.3g}")
    print("  constantes ~estaveis entre metades => pinadas por estrutura, nao por pontos individuais.")

    print("\nVEREDICTO: ver numeros acima — LOCO ~1 + BIC favoravel + residuo no piso +")
    print("meio do A_F acertado + metades estaveis => calibracao de estrutura real;")
    print("qualquer um desses falhando => reportar como fit fragil. Cross-rig segue impossivel")
    print("(unico P0-sweep da biblioteca) — teto epistemico declarado.")


if __name__ == "__main__":
    main()
