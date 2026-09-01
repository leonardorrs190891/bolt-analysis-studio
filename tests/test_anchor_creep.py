"""Ancora de C_creep (creep estatico, sub-campanha C) — spec 2026-07-03 §1.7."""
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "New_Theory"))

from anchor_creep import fit_anchor, simulate_static  # noqa: E402


def test_registry_truth_wear_inert_in_static_mode():
    # F_amp=0: sem slip transversal => K_archard estruturalmente nao-lido
    # (mesma doutrina registry-truth, estendida ao regime estatico).
    a = simulate_static(10e3, C_creep=3e-11, emb_depth_m=2e-6, n_min=300,
                        K_archard=1e-4)
    b = simulate_static(10e3, C_creep=3e-11, emb_depth_m=2e-6, n_min=300,
                        K_archard=2e-4)
    assert np.array_equal(a, b)
    # loosening tambem inerte (T_loose=0 com F_amp=0): tr_loose_gain nao-lido
    c = simulate_static(10e3, C_creep=3e-11, emb_depth_m=2e-6, n_min=300,
                        tr_loose_gain=4.0)
    assert np.array_equal(a, c)


def test_static_mode_loses_preload_via_embedding_and_creep():
    r = simulate_static(10e3, C_creep=3e-11, emb_depth_m=2e-6, n_min=600)
    assert r[0] == 1.0 and r[-1] < 0.9        # perde algo
    # floor corrigido pelo controlador: com k_b=1.515e9 (grip 20mm) os
    # literais agressivos deste teste perdem ~66% (30% emb + creep
    # auto-suprimido) — intencao = "nao colapsa a ~0", nao "perde pouco".
    assert r[-1] > 0.2                         # mas nao colapsa a ~0
    # monotonico nao-crescente
    assert np.all(np.diff(r) <= 1e-12)


def test_fit_anchor_recovers_synthetic_C_creep():
    # Gera 3 curvas estaticas com C conhecido + ruido e recupera C (rel 25%).
    rng = np.random.default_rng(7)
    C_true, embs = 3e-11, {0.8: 3e-6, 0.122: 1e-6}
    curves = []
    for F0, ra in [(10e3, 0.8), (5e3, 0.8), (10e3, 0.122)]:
        r = simulate_static(F0, C_true, embs[ra], n_min=600)
        mins = np.linspace(1, 600, 12)
        vals = np.interp(mins, np.arange(601), r) + rng.normal(0, 0.003, 12)
        curves.append(dict(name=f"syn_{F0:.0f}_{ra}", F0_N=F0, Ra_um=ra,
                           minutes=mins, ratio=vals))
    res = fit_anchor(curves)
    assert res["C_creep_anchor"] == pytest.approx(C_true, rel=0.25)
    assert res["ci_factor"] >= 1.0
    assert set(res["emb_depth_um_by_Ra"]) == {"0.8", "0.122"}
