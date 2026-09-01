"""Merge K/H -> k_wear_spec (sec4.42 proposta (a), 2026-07-09).

K_archard e hardness so aparecem como RAZAO K/H no engine (WearLoss e
ThreadFrettingLoss) => nao-identificaveis em separado. k_wear_spec = K/H [1/Pa]
e o parametro identificavel canonico; 0.0 (default) usa o caminho legado com a
aritmetica ORIGINAL.

Gates:
  1. default (k_wear_spec=0) => trajetoria BIT-IDENTICA ao legado.
  2. EQUIFINALIDADE exata do par legado: (2K, 2H) == (K, H) bit-a-bit — a
     prova de que o par nao e identificavel (motivacao do merge).
  3. equivalencia: k_wear_spec = K/H reproduz o legado (rtol FP: a ordem
     aritmetica muda, entao approx, nao bit).
  4. override: k_wear_spec por cima de K/H legado diferente => vence.
  5. o site de FRETTING axial tambem honra o merge.
"""
import numpy as np
import pytest

from bolt_analysis_studio.numerical.dynamic_stiffness_analyzer import (
    DynamicStiffnessAnalyzer, JointGeometry, JointMaterial,
)


def _geom():
    return JointGeometry(
        E=210e9, A_s=157e-6, L_eff=30e-3, d_2=14.7e-3, pitch=2.0e-3,
        r_bearing=12e-3, A_contact=1e-4,
    )


def _run_tr(mat, n=2000, F0=50e3, delta=0.5e-3):
    """Transversal disp-mode: wear domina a perda (CLAUDE.md) — bom sensor."""
    ana = DynamicStiffnessAnalyzer(_geom(), mat, F0)
    r = np.empty(n + 1)
    r[0] = 1.0
    for i in range(1, n + 1):
        ana.step_cycle(0.4 * F0, np.pi / 2, 0.5, delta_amp=delta)
        r[i] = max(ana.state.F_0, 0.0) / F0
    return r


def _mat(**kw):
    base = dict(emb_depth=5e-6, mu_thread=0.14, mu_bearing=0.14)
    base.update(kw)
    return JointMaterial(**base)


def test_default_legacy_bit_identical():
    """k_wear_spec=0 (default) => caminho legado, trajetoria BIT-IDENTICA."""
    r_leg = _run_tr(_mat(K_archard=1e-4, hardness=2e9))
    r_new = _run_tr(_mat(K_archard=1e-4, hardness=2e9, k_wear_spec=0.0))
    assert np.array_equal(r_leg, r_new)
    assert JointMaterial(emb_depth=1e-6).k_wear_spec == 0.0


def test_legacy_pair_exact_equifinality():
    """(2K, 2H) == (K, H) BIT-A-BIT — o par legado nao e identificavel.
    (Dobrar e' exato em FP: numerador e denominador escalam igual.)"""
    r_a = _run_tr(_mat(K_archard=1e-4, hardness=2e9))
    r_b = _run_tr(_mat(K_archard=2e-4, hardness=4e9))
    assert np.array_equal(r_a, r_b), "K/H igual deveria dar trajetoria identica"


def test_spec_equivalent_to_ratio():
    """k_wear_spec = K/H reproduz o legado (approx — ordem FP muda)."""
    K, H = 1e-4, 2e9
    r_leg = _run_tr(_mat(K_archard=K, hardness=H))
    r_new = _run_tr(_mat(k_wear_spec=K / H))
    assert np.allclose(r_leg, r_new, rtol=1e-7, atol=1e-9)
    # e o wear de fato aconteceu (teste nao-vazio)
    assert r_leg[-1] < 0.99


def test_spec_overrides_legacy():
    """k_wear_spec>0 vence os legados: dobrar a razao => mais perda."""
    base = _mat(K_archard=1e-4, hardness=2e9, k_wear_spec=5e-14)   # == K/H
    dbl = _mat(K_archard=1e-4, hardness=2e9, k_wear_spec=1e-13)    # 2x
    r_base = _run_tr(base)
    r_dbl = _run_tr(dbl)
    assert r_dbl[-1] < r_base[-1] - 1e-4, (
        f"razao dobrada deveria perder mais: {r_dbl[-1]:.4f} vs {r_base[-1]:.4f}"
    )


def test_fretting_site_honors_merge():
    """ThreadFrettingLoss (axial, k_thread_fret>0) tambem usa k_wear_spec."""
    def run_ax(mat, n=800):
        ana = DynamicStiffnessAnalyzer(_geom(), mat, 12.5e3)
        for _ in range(n):
            ana.step_cycle(10e3, 0.0, 15.0)     # axial
        return ana.state.F_0
    K, H = 1e-4, 2e9
    f_leg = run_ax(_mat(K_archard=K, hardness=H, k_thread_fret=1.0))
    f_new = run_ax(_mat(k_wear_spec=K / H, k_thread_fret=1.0))
    assert f_leg == pytest.approx(f_new, rel=1e-7)
    # e dobrar a razao via spec muda o fretting
    f_dbl = run_ax(_mat(k_wear_spec=2 * K / H, k_thread_fret=1.0))
    assert f_dbl < f_leg - 1e-3
