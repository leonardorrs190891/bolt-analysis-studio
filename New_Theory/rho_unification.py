"""G1 do item 1 (unificacao rho, spec 2026-07-08): ground-fit axial refeito com
S_rho = min(1,(rho/rho_ref)^q_amp), rho = A_F/F0, substituindo emb_conform_exp
no canal RAPIDO. Mesmo protocolo do §4.14a-rev: fit de 5 constantes nas 5 curvas
COMPLETAS do P0-sweep; o A_F-sweep e' avaliado ZERO-EXTRA-FIT (predicao pura).

Identidade estrutural: no P0-sweep (A_F=10 fixo, rho_ref=10/15) a forma nova e'
uma REPARAMETRIZACAO exata da antiga ((rho/rho_ref)^q == (15/F0)^q), logo o fit
P0 deve reproduzir o ground-fit. O conteudo NOVO todo esta no A_F-sweep: a forma
antiga preve UMA curva p/ as 4 amplitudes (S=cte em F0=18); S_rho as separa.

Gates pre-declarados (spec §3):
  G1: P0-sweep MAE medio <= 0.0033+0.005  E  A_F-sweep MAE medio <= 0.02 (hoje 0.035)
  G2: residuo final do A_F-sweep sem tendencia monotona em A_F
  G4: perfil SSE em q_amp sem vale degenerado (curvatura clara; largura reportada)

Run: python New_Theory/rho_unification.py
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
AF = [("7p5kN", 7.5e3), ("8p75kN", 8.75e3), ("11p25kN", 11.25e3), ("12p5kN", 12.5e3)]
FREQ, T0 = 30.0, 1.0
GEOM = geometry_for("M12x1.75", 30.0)
KB = GEOM.k_b
F0_REF = 15e3
A_F_P0 = 10e3                       # amplitude fixa do P0-sweep
RHO_REF = A_F_P0 / F0_REF           # 0.667 — ancora (input): S=1 no ponto de maior perda
GATE_P0, GATE_AF = 0.0033 + 0.005, 0.02


def load(entries, pattern):
    out = []
    for tag, val in entries:
        cyc, r = load_full_curve(f"{DIG}/{pattern}_{tag}.csv")
        r = r / r[0]
        out.append((val, cyc[1:], r[1:]))
    return out


def model_curve(F0, A_F, N, emb_cap, n_emb, c_rig, q_amp, exp_s, iters=3):
    """Canal axial analitico — identico ao axial_ground_fit.model_curve exceto
    o canal rapido: S_rho(amplitude relativa) no lugar de S_p(pressao)."""
    rho = A_F / F0
    Sf = min(1.0, (rho / RHO_REF) ** q_amp)
    Ss = min(1.0, (F0_REF / F0) ** exp_s)
    fast = (KB * emb_cap * Sf / F0) * (1.0 - np.exp(-N / n_emb))
    ln_t = np.log((N / FREQ + T0) / T0)
    ratio = np.ones_like(N, dtype=float)
    for _ in range(iters):
        favg = (1.0 + ratio) / 2.0
        slow = KB * c_rig * Ss * favg * ln_t
        ratio = np.clip(1.0 - fast - slow, 0.0, None)
    return ratio


def sse_p0(params, data):
    s = 0.0
    for F0, cyc, r in data:
        pred = model_curve(F0, A_F_P0, cyc, *params)
        s += float(np.sum((pred - r) ** 2))
    return s


def fit(data):
    best = [3.5e-6, 50.0, 1.8667e-11, 3.4, 2.0]   # priors (q prior = leitura 3.4)
    grids = [np.linspace(2.5e-6, 5.0e-6, 26), np.linspace(10, 90, 33),
             np.linspace(0.8e-11, 2.4e-11, 33), np.linspace(1.0, 6.0, 41),
             np.linspace(0.5, 4.0, 36)]
    for _ in range(6):
        for i, g in enumerate(grids):
            vals = []
            for v in g:
                p = list(best); p[i] = float(v)
                vals.append((sse_p0(p, data), float(v)))
            best[i] = min(vals)[1]
    return best


def eval_set(data, amp_of, params, label):
    print(f"\n{label}:")
    maes, finals_err, keys = [], [], []
    for key, cyc, r in data:
        F0, A_F = amp_of(key)
        pred = model_curve(F0, A_F, cyc, *params)
        mae = float(np.mean(np.abs(pred - r)))
        maes.append(mae); finals_err.append(float(pred[-1] - r[-1])); keys.append(key)
        print(f"  {key/1e3:6.2f}k  MAE {mae:.4f}  err_final {pred[-1]-r[-1]:+.3f}")
    print(f"  medio: {np.mean(maes):.4f}")
    return np.array(maes), np.array(finals_err), np.array(keys)


def main():
    p0_data = load(P0, "liu2017_axial_F0")
    af_data = load(AF, "liu2017_axial_AF")
    p = fit(p0_data)
    emb_cap, n_emb, c_rig, q_amp, exp_s = p
    print("RHO-UNIFICATION FIT (5 constantes no P0-sweep; rho_ref=0.667 input):")
    print(f"  emb_cap = {emb_cap*1e6:.2f} um   N_emb = {n_emb:.0f}   C_creep = {c_rig:.3e}")
    print(f"  q_amp   = {q_amp:.3f}  (leitura previa 3.4 no observavel; forma-depth => q~obs-1)")
    print(f"  exp_s   = {exp_s:.2f}")

    m_p0, _, _ = eval_set(p0_data, lambda F0: (F0, A_F_P0), p,
                          "P0-sweep (IN-FIT, curvas completas)")
    m_af, e_af, k_af = eval_set(af_data, lambda A: (18e3, A), p,
                                "A_F-sweep (ZERO-EXTRA-FIT, F0=18kN)")

    # baseline amplitude-cego: mesma curva p/ todo A_F (forma antiga, GF §4.14a-rev)
    from axial_ground_fit import model_curve as old_curve
    GF = [4.30e-6, 15.0, 1.450e-11, 2.375, 3.60]
    base = [float(np.mean(np.abs(old_curve(18e3, cyc, *GF) - r))) for _, cyc, r in af_data]
    print(f"\nbaseline (forma antiga, amplitude-cega): A_F medio {np.mean(base):.4f} "
          f"(cases {' '.join(f'{b:.3f}' for b in base)})")

    # G2: tendencia monotona do erro final vs A_F?
    order = np.argsort(k_af)
    diffs = np.diff(e_af[order])
    mono = bool(np.all(diffs > 0) or np.all(diffs < 0))
    print(f"\nG2 residuo final vs A_F: {['%+.3f' % v for v in e_af[order]]} "
          f"-> monotono: {mono}")

    # G4: perfil SSE em q_amp (demais re-otimizadas por coordenada, 2 passes)
    print("\nG4 perfil de identificabilidade em q_amp (SSE P0, demais re-otimizadas):")
    prof = []
    for q in np.linspace(1.0, 6.0, 11):
        best = list(p); best[3] = float(q)
        grids = [np.linspace(2.5e-6, 5.0e-6, 26), np.linspace(10, 90, 33),
                 np.linspace(0.8e-11, 2.4e-11, 33), None, np.linspace(0.5, 4.0, 36)]
        for _ in range(2):
            for i, g in enumerate(grids):
                if g is None:
                    continue
                vals = []
                for v in g:
                    pp = list(best); pp[i] = float(v)
                    vals.append((sse_p0(pp, p0_data), float(v)))
                best[i] = min(vals)[1]
        prof.append((q, sse_p0(best, p0_data)))
    smin = min(s for _, s in prof)
    for q, s in prof:
        bar = "#" * int(40 * smin / max(s, 1e-12))
        print(f"  q={q:4.1f}  SSE {s:.5f}  {bar}")
    within = [q for q, s in prof if s <= 1.1 * smin]
    print(f"  vale (SSE <= 1.1x min): q in [{min(within):.1f}, {max(within):.1f}]")

    g1 = np.mean(m_p0) <= GATE_P0 and np.mean(m_af) <= GATE_AF
    print(f"\n=== GATES ===")
    print(f"G1 P0 {np.mean(m_p0):.4f} <= {GATE_P0:.4f}: {np.mean(m_p0) <= GATE_P0}   "
          f"A_F {np.mean(m_af):.4f} <= {GATE_AF:.3f}: {np.mean(m_af) <= GATE_AF}   => {'PASS' if g1 else 'FAIL'}")
    print(f"G2 sem tendencia monotona: {'PASS' if not mono else 'FAIL'}")
    print(f"PARAMS_JSON: {dict(emb_cap=emb_cap, n_emb=n_emb, c_rig=c_rig, q_amp=q_amp, exp_s=exp_s, rho_ref=RHO_REF)}")


if __name__ == "__main__":
    main()
