"""Espectro de amplitude estatístico -> cronograma determinístico (spec 2026-07-09).

Gates:
  1. retrocompat: std=0 e hist=None => array CONSTANTE exato (bit-identical).
  2. determinismo: mesma chamada => mesmo array (sem RNG).
  3. estatística: a media/desvio do array batem com a distribuicao pedida.
  4. histograma: as fracoes dos bins sao respeitadas (base+picos do Bauer).
  5. recorte fisico lo/hi respeitado.
  6. cobertura de baixa-discrepancia (a cauda super-critica APARECE).
"""
import numpy as np
import pytest

from bolt_analysis_studio.numerical.amplitude_spectrum import (
    spectrum_schedule, _norm_ppf,
)


def test_constant_backward_compat():
    """std=0, hist=None => full(mean) EXATO (o engine ve a amplitude unica)."""
    s = spectrum_schedule(1000, mean=0.5e-3)
    assert s.shape == (1000,)
    assert np.array_equal(s, np.full(1000, 0.5e-3))
    # std explicitamente 0 idem
    s2 = spectrum_schedule(1000, mean=0.5e-3, std=0.0)
    assert np.array_equal(s2, np.full(1000, 0.5e-3))


def test_zero_length():
    assert spectrum_schedule(0, mean=0.5e-3, std=0.1e-3).shape == (0,)


def test_deterministic():
    """Sem RNG: duas chamadas identicas => arrays identicos."""
    a = spectrum_schedule(500, mean=90e-6, std=25e-6)
    b = spectrum_schedule(500, mean=90e-6, std=25e-6)
    assert np.array_equal(a, b)


def test_normal_statistics():
    """media/desvio do cronograma ~ os pedidos (baixa-discrepancia converge)."""
    s = spectrum_schedule(20000, mean=90e-6, std=25e-6, lo=0.0)
    assert abs(np.mean(s) - 90e-6) < 2e-6
    assert abs(np.std(s) - 25e-6) < 2e-6


def test_histogram_fractions():
    """base 80um (90%) + picos 150um (10%): as fracoes emergem."""
    hist = [(80e-6, 0.9), (150e-6, 0.1)]
    s = spectrum_schedule(10000, mean=0.0, hist=hist)
    frac_peak = np.mean(np.isclose(s, 150e-6))
    frac_base = np.mean(np.isclose(s, 80e-6))
    assert abs(frac_peak - 0.1) < 0.01
    assert abs(frac_base - 0.9) < 0.01
    # e so existem os dois valores do histograma
    assert set(np.unique(s).round(9)) == {round(80e-6, 9), round(150e-6, 9)}


def test_hist_overrides_meanstd():
    """hist dado sobrepoe mean/std."""
    hist = [(80e-6, 0.5), (150e-6, 0.5)]
    s = spectrum_schedule(1000, mean=999.0, std=999.0, hist=hist)
    assert s.max() <= 150e-6 + 1e-12
    assert s.min() >= 80e-6 - 1e-12


def test_clip_lo_hi():
    """recorte fisico: amplitudes nunca negativas nem acima de hi."""
    s = spectrum_schedule(5000, mean=50e-6, std=80e-6, lo=0.0, hi=120e-6)
    assert s.min() >= 0.0
    assert s.max() <= 120e-6 + 1e-12


def test_supercritical_tail_present():
    """a cauda super-critica (picos) DEVE aparecer no cronograma normal —
    e isso que uma amplitude unica (a media) nunca daria."""
    s = spectrum_schedule(5000, mean=90e-6, std=25e-6, lo=0.0)
    # ha ciclos bem acima da media (>s_crit ~99um cruzado pela cauda)
    assert np.max(s) > 130e-6, f"cauda ausente: max={np.max(s)*1e6:.0f}um"
    assert np.mean(s > 99e-6) > 0.1, "poucos ciclos super-criticos"


def test_phase_realizations():
    """Mesma distribuicao, phase diferente => realizacao diferente (ordem), mesma
    estatistica. Modela o scatter de repeticoes nominalmente identicas."""
    a = spectrum_schedule(3000, mean=90e-6, std=25e-6, phase=0.0)
    b = spectrum_schedule(3000, mean=90e-6, std=25e-6, phase=0.37)
    assert not np.array_equal(a, b)                      # realizacoes distintas
    # mas a distribuicao (media/desvio) e ~a mesma
    assert abs(np.mean(a) - np.mean(b)) < 3e-6
    assert abs(np.std(a) - np.std(b)) < 3e-6


def test_phase_ignored_when_constant():
    """Sem distribuicao (std=0), phase nao muda nada (bit-identical)."""
    a = spectrum_schedule(500, mean=0.5e-3, std=0.0, phase=0.0)
    b = spectrum_schedule(500, mean=0.5e-3, std=0.0, phase=0.6)
    assert np.array_equal(a, b)


def test_norm_ppf_symmetry():
    """sanidade do ppf: ppf(0.5)=0, simetrico, monotonico."""
    assert abs(_norm_ppf(np.array([0.5]))[0]) < 1e-6
    q = np.array([0.1, 0.25, 0.5, 0.75, 0.9])
    v = _norm_ppf(q)
    assert np.all(np.diff(v) > 0)                       # monotonico
    assert abs(v[0] + v[-1]) < 1e-6                      # simetrico
    assert abs(v[1] + v[-2]) < 1e-6
