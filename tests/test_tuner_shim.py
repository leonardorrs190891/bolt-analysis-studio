# -*- coding: utf-8 -*-
"""Estagio B — shim de traducao de tuners legados -> constantes fisicas.

NOTA: a FOLD-EQUIVALENCE numerica (JM(tuner=v) == JM(tuner=1, const=base*v) na
trajetoria de ratio) foi provada na FASE 1 (commit db77eb6), QUANDO os campos de
tuner ainda existiam no dataclass. Na FASE 4 os 9 campos foram REMOVIDOS de
JointMaterial, entao esses testes agora cobrem: (a) o shim traduz corretamente
(mapa/multiply/idempotente/roteamento) e (b) as constantes que o shim produz
sao aceitas pelo engine e rodam (smoke). Nao ha mais "JM com tuner" para comparar.
"""
import warnings

import numpy as np
import pytest

from bolt_analysis_studio.calibration.tuner_shim import translate_legacy_tuners
from bolt_analysis_studio.numerical.dynamic_stiffness_analyzer import (
    DynamicStiffnessAnalyzer, JointGeometry, JointMaterial,
)

BASE = dict(emb_depth=5e-6, mu_thread=0.14, mu_bearing=0.14)


def _geom():
    return JointGeometry(E=210e9, A_s=157e-6, L_eff=30e-3, d_2=14.7e-3,
                         pitch=2.0e-3, r_bearing=12e-3, A_contact=1e-4)


def _run(kw, n=800, F0=50e3):
    ana = DynamicStiffnessAnalyzer(_geom(), JointMaterial(**kw), F0)
    for _ in range(n):
        ana.step_cycle(0.4 * F0, np.pi / 2, 0.5, delta_amp=0.5e-3)
    return max(ana.state.F_0, 0.0) / F0


# -------------------------------------------------- traducao (mapa) do shim
def test_maps_each_tuner_to_its_constant():
    b = dict(BASE)
    assert translate_legacy_tuners({"k_emb_scale": 0.66}, base=b, warn=False) \
        == {"emb_depth": pytest.approx(0.66 * 5e-6)}
    assert translate_legacy_tuners({"k_creep_scale": 0.4}, warn=False) \
        == {"C_creep": pytest.approx(0.4 * JointMaterial().C_creep)}
    assert translate_legacy_tuners({"k_wear_scale_tr": 0.44}, warn=False) \
        == {"K_archard": pytest.approx(0.44 * JointMaterial().K_archard)}
    # Phi_tr e k_loose_tr compoem em tr_loose_gain
    out = translate_legacy_tuners({"Phi_tr_correction": 2.0,
                                   "k_loose_scale_tr": 1.5}, warn=False)
    assert out["tr_loose_gain"] == pytest.approx(2.0 * 2.0 * 1.5)
    assert translate_legacy_tuners({"k_damage_scale": 3.0}, base=dict(BASE, c_D=2.0),
                                   warn=False) == {"c_D": pytest.approx(6.0)}


def test_routes_wear_to_k_wear_spec_when_active():
    base = dict(BASE, k_wear_spec=5e-14)
    out = translate_legacy_tuners({"k_wear_scale_tr": 0.5}, base=base, warn=False)
    assert out["k_wear_spec"] == pytest.approx(2.5e-14)
    assert "K_archard" not in out


def test_multiply_never_overwrite():
    out = translate_legacy_tuners({"k_emb_scale": 0.5, "emb_depth": 10e-6},
                                  warn=False)
    assert out["emb_depth"] == pytest.approx(5e-6)
    assert "k_emb_scale" not in out


def test_unity_noop_and_idempotent():
    out = translate_legacy_tuners({"k_emb_scale": 1.0, "c_bend": 3.0}, warn=False)
    assert out == {"c_bend": 3.0}
    assert translate_legacy_tuners(out, warn=False) == out


def test_drops_ax_with_deprecation_warning():
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        out = translate_legacy_tuners({"k_wear_scale_ax": 2.0, "k_emb_scale": 1.0})
    assert "k_wear_scale_ax" not in out
    assert any(issubclass(x.category, DeprecationWarning) for x in w)


def test_passes_physical_keys_untouched():
    src = {"emb_depth": 2e-6, "C_creep": 1e-11, "conform_driver": "effective"}
    assert translate_legacy_tuners(dict(src), warn=False) == src


# -------------------- as constantes foldadas SAO aceitas pelo engine (smoke)
def test_folded_constants_run_in_engine():
    """O engine (sem os campos de tuner) aceita e roda as constantes que o shim
    produz — e o tuner de wear reduzido perde MENOS que o cheio."""
    folded_lo = translate_legacy_tuners({"k_wear_scale_tr": 0.1}, base=BASE, warn=False)
    folded_hi = translate_legacy_tuners({"k_wear_scale_tr": 1.0}, base=BASE, warn=False)
    r_lo = _run(dict(BASE, **folded_lo))
    r_hi = _run(dict(BASE, **{k: v for k, v in folded_hi.items()}))
    # k_wear_scale_tr=1.0 e no-op (nao injeta K_archard) => usa o default;
    # 0.1 reduz K_archard => menos wear => retem mais preload.
    assert r_lo > r_hi
    # e os antigos nomes de tuner nao existem mais no dataclass
    assert "k_emb_scale" not in JointMaterial.__dataclass_fields__
    assert "k_wear_scale_tr" not in JointMaterial.__dataclass_fields__
