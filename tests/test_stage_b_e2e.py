# -*- coding: utf-8 -*-
"""Estagio B — E2E: o SHIM na fronteira do Run + engine SEM tuners produz um
resultado sensato para as fontes que usavam tuners (ICMEZ/Liu/HDPE/nova).

NOTA: a equivalencia shim==legado foi provada na FASE 3 (commit 978049e), com
os campos de tuner ainda presentes. Na FASE 4 os campos foram removidos; aqui
verificamos que o pipeline (tuners legados -> shim -> constantes -> engine) roda
e que a magnitude do wear per-rig e honrada (menos wear => retem mais).
"""
import numpy as np
import pytest

from bolt_analysis_studio.calibration.tuner_shim import translate_legacy_tuners
from bolt_analysis_studio.numerical.dynamic_stiffness_analyzer import (
    DynamicStiffnessAnalyzer, JointGeometry, JointMaterial,
)

BASE = dict(emb_depth=5e-6, mu_thread=0.14, mu_bearing=0.14, c_bend=1.0)


def _geom():
    return JointGeometry(E=210e9, A_s=157e-6, L_eff=30e-3, d_2=14.7e-3,
                         pitch=2.0e-3, r_bearing=12e-3, A_contact=1e-4)


def _run(kw, n=1500, F0=50e3, delta=0.5e-3):
    ana = DynamicStiffnessAnalyzer(_geom(), JointMaterial(**kw), F0)
    r = np.empty(n + 1); r[0] = 1.0
    for i in range(1, n + 1):
        ana.step_cycle(0.4 * F0, np.pi / 2, 0.5, delta_amp=delta)
        r[i] = max(ana.state.F_0, 0.0) / F0
    return r


@pytest.mark.parametrize("tuners", [
    {"k_wear_scale_tr": 0.15},                              # ICMEZ lk19p8
    {"k_wear_scale_tr": 0.06},                              # Liu2022 / Liu2025
    {"k_emb_scale": 0.6629, "k_wear_scale_tr": 0.4446},     # profile "nova"
    {"k_creep_scale": 1.0, "k_wear_scale_tr": 0.44},        # Rousseau HDPE-ish
])
def test_legacy_tuners_flow_through_shim_into_engine(tuners):
    """Tuners legados -> shim -> constantes -> engine roda sem erro e afrouxa."""
    folded = translate_legacy_tuners(dict(tuners), base=BASE, warn=False)
    kw = dict(BASE, **folded)
    # nenhum nome de tuner sobrevive ao shim
    assert not any(k.endswith("_scale") or k.endswith("_correction") for k in folded)
    r = _run(kw)
    assert 0.0 <= r[-1] <= 1.0                              # trajetoria valida
    assert r[-1] < 1.0                                      # afrouxou


def test_wear_magnitude_honored_end_to_end():
    """A magnitude per-rig do wear (era k_wear_scale_tr) e honrada: fator menor
    via shim => menos wear => retem mais preload."""
    r_lo = _run(dict(BASE, **translate_legacy_tuners(
        {"k_wear_scale_tr": 0.06}, base=BASE, warn=False)))
    r_hi = _run(dict(BASE, **translate_legacy_tuners(
        {"k_wear_scale_tr": 0.5}, base=BASE, warn=False)))
    assert r_lo[-1] > r_hi[-1]


def test_ax_tuner_dropped_end_to_end():
    """k_wear_scale_ax legado e dropado; sem wear axial em disp-mode
    transversal, o resultado bate com nao passar o tuner."""
    folded = translate_legacy_tuners({"k_wear_scale_ax": 2.0}, base=BASE, warn=False)
    assert "k_wear_scale_ax" not in folded
    assert np.array_equal(_run(dict(BASE, **folded)), _run(dict(BASE)))
