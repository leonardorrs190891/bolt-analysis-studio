"""#1 Blend continuo de fases — teto cinematico em serie (sec4.35).

O drive de afrouxamento por torque-excesso e ILIMITADO: quando F_0 cai,
(T_loose - T_resist) cresce e slip_fraction sobe => runaway abrupto (S-shape),
o modo de erro dominante da galeria (mid-over-loss, 35/82 curvas). O teto
cinematico limita d_theta EM SERIE com a disponibilidade de gross-slip
(media harmonica) => saturacao suave, sem quina.

Gates:
  1. default-inert: loose_kin_ceiling=0 => trajetoria BIT-IDENTICA.
  2. ativo: a queda no meio da curva e MENOS agressiva (runaway suavizado),
     sem alterar o inicio (early) — o teto so morde quando o torque-excess
     dispara.
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
    # config GRADUAL: incubacao (slip_onset_W) => plato de assentamento seguido
    # de runaway de loosening no meio da curva. Assim early (settling) e mid
    # (runaway) ficam bem separados e o efeito do teto e' localizavel.
    base = dict(
        emb_depth=5e-6, mu_thread=0.14, mu_bearing=0.14,
        slip_regime_mode="cattaneo_mindlin", slip_regime_sharpness=1.0,
        k_tr_mode="bending", loose_torsion_mode="bolt_torsion",
        eta_loose=15.0, c_bend=1.0, tr_loose_gain=2.0,
        slip_onset_W=3e4, slip_onset_sharpness=4.0,
    )
    base.update(kw)
    return JointMaterial(**base)


def _run(mat, n=4000, F0=50e3, delta=0.5e-3, freq=0.5):
    ana = DynamicStiffnessAnalyzer(_geom(), mat, F0)
    r = np.empty(n + 1)
    r[0] = 1.0
    for i in range(1, n + 1):
        ana.step_cycle(0.4 * F0, np.pi / 2, freq, delta_amp=delta)
        r[i] = max(ana.state.F_0, 0.0) / F0
    return r


def test_default_inert_bit_identical():
    """loose_kin_ceiling=0 (default) => trajetoria identica a sem o campo."""
    r_off = _run(_mat())                       # campo no default 0.0
    r_ref = _run(_mat(loose_kin_ceiling=0.0))  # explicito 0.0
    assert np.allclose(r_off, r_ref, atol=0.0, rtol=0.0)
    # e o default do dataclass e mesmo 0.0
    assert JointMaterial(emb_depth=5e-6).loose_kin_ceiling == 0.0


def test_ceiling_softens_runaway():
    """Com teto ativo, o runaway e' ESPALHADO: mais F_0 retido no meio-tardio
    da curva e o cruzamento de 0.5 acontece MAIS TARDE (colapso gradual)."""
    r_off = _run(_mat())
    r_on = _run(_mat(loose_kin_ceiling=0.02))
    # tem que haver afrouxamento nos dois (senao o teste e vazio)
    assert r_off[-1] < 0.5, "config base precisa afrouxar/colapsar"
    # no meio-tardio (75%) o teto retem VISIVELMENTE mais preload
    q = int(0.75 * (len(r_off) - 1))
    assert r_on[q] - r_off[q] > 0.02, (
        f"teto deveria suavizar o runaway (75%): "
        f"on={r_on[q]:.4f} off={r_off[q]:.4f}"
    )
    # o cruzamento de 0.5 (joelho) acontece MAIS TARDE com o teto
    n50_off = int(np.argmax(r_off < 0.5))
    n50_on = int(np.argmax(r_on < 0.5)) if (r_on < 0.5).any() else len(r_on)
    assert n50_on > n50_off, (
        f"teto deveria atrasar o joelho: on@{n50_on} off@{n50_off}"
    )


def test_ceiling_only_bites_in_runaway_not_early():
    """O teto nao deve alterar o assentamento inicial (early) — so o runaway
    de loosening. Early = platô de incubacao antes do joelho."""
    r_off = _run(_mat())
    r_on = _run(_mat(loose_kin_ceiling=0.02))
    early = max(1, len(r_off) // 20)  # primeiros 5% (settling/incubacao)
    assert np.allclose(r_on[:early], r_off[:early], atol=2e-3), (
        "teto nao deveria afetar o early (torque-excess ainda pequeno)"
    )


def test_force_mode_untouched():
    """Sem slip_amp_override (modo forca) o teto e inativo por construcao."""
    m = _mat(loose_kin_ceiling=0.02)
    ana_on = DynamicStiffnessAnalyzer(_geom(), m, 50e3)
    ana_off = DynamicStiffnessAnalyzer(_geom(), _mat(), 50e3)
    for _ in range(500):
        ana_on.step_cycle(0.4 * 50e3, np.pi / 2, 0.5)   # sem delta_amp
        ana_off.step_cycle(0.4 * 50e3, np.pi / 2, 0.5)
    assert ana_on.state.F_0 == pytest.approx(ana_off.state.F_0, abs=1e-6)
