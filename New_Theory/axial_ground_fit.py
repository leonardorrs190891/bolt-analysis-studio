"""Revisao GROUND-UP do bloco axial (2026-07-08): fit per-rig nas CURVAS COMPLETAS.

Diagnostico (curvas cruas): (1) taxa de cauda do modelo e' F0-flat (0.024/dec)
enquanto o dado cai 0.020->0.010/dec (F0^-2); (2) o NIVEL da cauda esta ~20% alto
ja' na ancora 15kN => C_creep do par da âncora interna nao vale neste rig (doutrina §4.7:
C_creep e' PER-PAR, ICs disjuntos). A estrutura de duas escalas (assentamento
rapido exponencial + cauda log-ciclo) E' o que o dado mostra — o erro era tratar
as 4-5 amplitudes como universais.

Fit ANALITICO (formas fechadas do canal axial) de 5 constantes per-rig nas ~60
amostras das 5 curvas: emb_cap (prior Rz<4 3.5um), N_emb (prior 50), C_creep_rig
(prior âncora interna 1.867e-11), exp_fast (prior 4), exp_slow (prior 2). p_ref ancorado em
p(15kN) (input). Cada constante e' pinada por feature independente (fast-drop x5,
tail-rate x5, shape inicial). Verificacao final: engine a 1e6 (rodar depois com
--engine-check <params>).

Run: python New_Theory/axial_ground_fit.py
"""
from __future__ import annotations
import sys
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "New_Theory"))
from library_common import geometry_for, load_full_curve  # noqa: E402

DIG = "Models/CALIBRATION_AND_VALIDATION/curve_library/digitized_csv"
P0 = [("15kN", 15e3), ("16p5kN", 16.5e3), ("18kN", 18e3), ("19p5kN", 19.5e3), ("21kN", 21e3)]
FREQ, T0 = 30.0, 1.0
GEOM = geometry_for("M12x1.75", 30.0)
KB = GEOM.k_b
F0_REF = 15e3                      # ancora: S=1 no menor preload (input da matriz)


def load():
    out = []
    for tag, F0 in P0:
        cyc, r = load_full_curve(f"{DIG}/liu2017_axial_F0_{tag}.csv")
        r = r / r[0]
        out.append((F0, cyc[1:], r[1:]))          # exclui o ponto (0,1)
    return out


def model_curve(F0, N, emb_cap, n_emb, c_rig, exp_f, exp_s, iters=3):
    """Curva analitica do canal axial (embedding exponencial + creep log-t),
    com correcao iterativa do F0 declinante no driver do creep."""
    Sf = min(1.0, (F0_REF / F0) ** exp_f)
    Ss = min(1.0, (F0_REF / F0) ** exp_s)
    fast = (KB * emb_cap * Sf / F0) * (1.0 - np.exp(-N / n_emb))
    ln_t = np.log((N / FREQ + T0) / T0)
    ratio = np.ones_like(N, dtype=float)
    for _ in range(iters):                        # creep dirigido pelo F0 corrente
        favg = (1.0 + ratio) / 2.0
        slow = KB * c_rig * Ss * favg * ln_t
        ratio = np.clip(1.0 - fast - slow, 0.0, None)
    return ratio


def sse(params, data):
    emb_cap, n_emb, c_rig, exp_f, exp_s = params
    s = 0.0
    for F0, cyc, r in data:
        pred = model_curve(F0, cyc, emb_cap, n_emb, c_rig, exp_f, exp_s)
        s += float(np.sum((pred - r) ** 2))
    return s


def fit(data):
    # coordenada-descent em grades refinadas (analitico => barato)
    best = [3.5e-6, 50.0, 1.8667e-11, 4.0, 2.0]   # priors
    grids = [np.linspace(2.5e-6, 5.0e-6, 26), np.linspace(10, 90, 33),
             np.linspace(0.8e-11, 2.4e-11, 33), np.linspace(2.0, 6.0, 33),
             np.linspace(0.5, 4.0, 36)]
    for _ in range(6):                            # passes
        for i, g in enumerate(grids):
            vals = []
            for v in g:
                p = list(best); p[i] = float(v)
                vals.append((sse(p, data), float(v)))
            best[i] = min(vals)[1]
    return best


def main():
    data = load()
    p = fit(data)
    emb_cap, n_emb, c_rig, exp_f, exp_s = p
    print("GROUND FIT (5 constantes per-rig, curvas completas, p_ref=p(15kN) input):")
    print(f"  emb_cap  = {emb_cap*1e6:.2f} um   (prior Rz<4 3.5; 'fitted, this rig')")
    print(f"  N_emb    = {n_emb:.0f} ciclos     (prior 50)")
    print(f"  C_creep  = {c_rig:.3e}  (prior âncora interna 1.867e-11; §4.7 per-par)")
    print(f"  exp_fast = {exp_f:.2f}            (prior 4)")
    print(f"  exp_slow = {exp_s:.2f}            (prior 2)")
    print()
    maes, finals_p, finals_d, F0s = [], [], [], []
    print(f"{'F0':>7s} {'final dado':>11s} {'final mod':>10s} {'err':>7s} {'MAE curva':>10s} "
          f"{'tail dado':>10s} {'tail mod':>9s}  (tail = perda/decada 1e3->1e6)")
    for F0, cyc, r in data:
        pred = model_curve(F0, cyc, *p)
        mae = float(np.mean(np.abs(pred - r)))
        # taxa de cauda por decada no dado e no modelo (janela 1e3->1e6)
        m = cyc >= 1e3
        if m.sum() >= 2:
            dec = (np.log10(cyc[m][-1]) - np.log10(cyc[m][0]))
            t_d = float((r[m][0] - r[m][-1]) / max(dec, 1e-9))
            t_m = float((pred[m][0] - pred[m][-1]) / max(dec, 1e-9))
        else:
            t_d = t_m = float("nan")
        maes.append(mae); finals_p.append(pred[-1]); finals_d.append(r[-1]); F0s.append(F0)
        print(f"{F0/1e3:6.1f}k {r[-1]:11.3f} {pred[-1]:10.3f} {pred[-1]-r[-1]:+7.3f} "
              f"{mae:10.4f} {t_d:10.4f} {t_m:9.4f}")
    sl_p = float(np.polyfit(F0s, finals_p, 1)[0])
    sl_d = float(np.polyfit(F0s, finals_d, 1)[0])
    print(f"\nslope d(final)/dP0: modelo {sl_p:.2e} vs dado {sl_d:.2e} ({sl_p/sl_d*100:.0f}%)")
    print(f"MAE medio (todas as amostras): {np.mean(maes):.4f}; max |err final| = "
          f"{max(abs(a-b) for a,b in zip(finals_p,finals_d)):.3f}")
    print("\nEngine-check (rode em background):")
    print(f"  python New_Theory/embedding_conformance_axial.py  # com params acima via harness")
    print(f"PARAMS_JSON: {dict(emb_cap=emb_cap, n_emb=n_emb, c_rig=c_rig, exp_f=exp_f, exp_s=exp_s)}")


if __name__ == "__main__":
    main()
