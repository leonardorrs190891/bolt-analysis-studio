"""Taxa de loosening GRADUADA amplitude-sensivel — modo graded_scrit (sec4.37).

O kernel de torque (default) e RUNAWAY-TO-ZERO em disp-mode: a amplitude decide
SE dispara, nao a trajetoria (s_crit=delta_t~F0 -> g_gross->1). O modo
"graded_scrit" substitui por uma taxa cinematica no EXCESSO de slip sobre um
s_crit FIXO: amplitude-sensivel, sem runaway, sub-critico => zero.

Gates:
  1. default (mode="torque") => trajetoria BIT-IDENTICA.
  2. k_loose_graded=0 mesmo em modo graded => bit-identical (branch pulado).
  3. modo forca (sem slip_amp_override) => branch inativo, bit-identical.
  4. super-critico (slip>s_crit) => afrouxa.
  5. sub-critico (slip<=s_crit) => NAO afrouxa (so os outros mecanismos).
  6. amplitude-sensivel: mais slip => mais afrouxamento (trajetoria MUDA).
  7. sem runaway: a taxa por-ciclo NAO explode quando F0 cai (limitada).
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


def _mat(**kw):
    base = dict(
        emb_depth=5e-6, mu_thread=0.14, mu_bearing=0.14,
        slip_regime_mode="cattaneo_mindlin", slip_regime_sharpness=1.0,
        k_tr_mode="bending", loose_torsion_mode="bolt_torsion",
        eta_loose=15.0, c_bend=1.0, tr_loose_gain=2.0,
    )
    base.update(kw)
    return JointMaterial(**base)


def _run(mat, n=3000, F0=50e3, delta=0.5e-3, freq=0.5):
    ana = DynamicStiffnessAnalyzer(_geom(), mat, F0)
    r = np.empty(n + 1)
    r[0] = 1.0
    for i in range(1, n + 1):
        ana.step_cycle(0.4 * F0, np.pi / 2, freq, delta_amp=delta)
        r[i] = max(ana.state.F_0, 0.0) / F0
    return r


def test_default_torque_bit_identical():
    """mode='torque' (default) => identico a nao mexer no campo."""
    r_ref = _run(_mat())
    r_torque = _run(_mat(loose_rate_mode="torque"))
    assert np.array_equal(r_ref, r_torque)
    assert JointMaterial(emb_depth=5e-6).loose_rate_mode == "torque"


def test_graded_k0_bit_identical():
    """modo graded mas k_loose_graded=0 => branch pulado => bit-identical."""
    r_ref = _run(_mat())
    r_g0 = _run(_mat(loose_rate_mode="graded_scrit", s_crit_loose=100e-6,
                     k_loose_graded=0.0))
    assert np.array_equal(r_ref, r_g0)


def test_force_mode_untouched():
    """Sem slip_amp_override (modo forca) o branch graded e inativo."""
    m = _mat(loose_rate_mode="graded_scrit", s_crit_loose=100e-6, k_loose_graded=0.02)
    ana_g = DynamicStiffnessAnalyzer(_geom(), m, 50e3)
    ana_t = DynamicStiffnessAnalyzer(_geom(), _mat(), 50e3)
    for _ in range(400):
        ana_g.step_cycle(0.4 * 50e3, np.pi / 2, 0.5)   # sem delta_amp
        ana_t.step_cycle(0.4 * 50e3, np.pi / 2, 0.5)
    assert ana_g.state.F_0 == pytest.approx(ana_t.state.F_0, abs=1e-6)


# --- testes com a taxa graduada ATIVA: wear transversal OFF p/ ISOLAR o
#     loosening (em disp-mode o wear domina, nota CLAUDE.md) ------------------
def _matg(**kw):
    # Estagio B: wear OFF via K_archard=0.0 (era k_wear_scale_tr=0.0).
    return _mat(K_archard=0.0, loose_rate_mode="graded_scrit", **kw)


def test_graded_loosens_supercritical():
    """slip (>>s_crit) super-critico => afrouxa."""
    r = _run(_matg(s_crit_loose=100e-6, k_loose_graded=0.001))
    assert r[-1] < 0.9, f"deveria afrouxar em regime super-critico: fim={r[-1]:.3f}"


def test_subcritical_retains():
    """slip <= s_crit => a taxa graduada contribui ZERO. Com s_crit gigante
    (1 m) TODO slip e sub-critico => nao afrouxa (retem >> que super-critico,
    so o assentamento resta)."""
    r_sub = _run(_matg(s_crit_loose=1.0, k_loose_graded=0.001))
    r_super = _run(_matg(s_crit_loose=100e-6, k_loose_graded=0.001))
    assert r_sub[-1] > 0.4, f"sub-critico deveria so assentar: fim={r_sub[-1]:.3f}"
    assert r_sub[-1] > r_super[-1] + 0.1, (
        f"sub-critico deveria reter muito mais: sub={r_sub[-1]:.3f} super={r_super[-1]:.3f}"
    )


def test_amplitude_sensitive():
    """Mais slip (delta maior) => mais afrouxamento (a TRAJETORIA muda com a
    amplitude — o que o runaway-to-zero do modo torque nao faz)."""
    kw = dict(s_crit_loose=100e-6, k_loose_graded=0.0005)
    r_lo = _run(_matg(**kw), delta=0.3e-3)
    r_hi = _run(_matg(**kw), delta=0.6e-3)
    assert r_hi[-1] < r_lo[-1] - 0.05, (
        f"amplitude maior deveria afrouxar mais: hi={r_hi[-1]:.3f} lo={r_lo[-1]:.3f}"
    )


def test_no_runaway_rate_bounded():
    """A taxa por-ciclo de perda NAO explode quando F0 cai (sem runaway):
    a maior perda fracional por ciclo na 2a metade nao e >> da 1a metade.
    (k pequeno p/ colapso PARCIAL, senao a saturacao em 0 mascara o teste.)"""
    r = _run(_matg(s_crit_loose=100e-6, k_loose_graded=0.0005), delta=0.3e-3)
    assert 0.05 < r[-1] < 0.95, f"config precisa de colapso PARCIAL: fim={r[-1]:.3f}"
    dr = -np.diff(r)                       # perda por ciclo (fracao de F0)
    n = len(dr)
    first = np.max(dr[: n // 2])
    second = np.max(dr[n // 2:])
    # runaway seria second >> first (aceleracao a zero); graded => comparaveis
    assert second < 5.0 * first + 1e-6, (
        f"taxa acelerou como runaway: 1a metade max={first:.2e} 2a={second:.2e}"
    )
