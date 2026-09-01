"""Espectro de amplitude -> cronograma determinístico por-ciclo (spec 2026-07-09).

Excitações reais de afrouxamento transversal muitas vezes NÃO são de amplitude
única: Bauer fig8 é um espectro (base ~80 µm + picos ~150 µm), Liu2025 reporta
ENVELOPES de oscilação (largura de banda = variação de amplitude), Yang/Rousseau
usam máquinas de amplitude variável. Uma amplitude única não reproduz o TIMING
do colapso, que é dirigido pela **cauda super-crítica** da distribuição (os picos
que cruzam s_crit e disparam o afrouxamento rotacional). Este módulo mapeia uma
distribuição de amplitude (normal média/desvio OU histograma empírico) para um
array por-ciclo DETERMINÍSTICO via uma sequência de baixa-discrepância
(golden-ratio): reprodutível, sem RNG, cobre a distribuição uniformemente.

`std=0` e `hist=None` => array CONSTANTE == mean (retrocompat bit-idêntico: o
engine vê a mesma amplitude única de sempre). A representação estatística
**descarta a ORDEM** (dois programas de bloco com a mesma distribuição dão o
mesmo cronograma) — para efeitos de ordem (Yang Fig10 vs Fig11) usar blocos.
"""
from __future__ import annotations

from typing import Optional, Sequence, Tuple

import numpy as np

# Incremento de baixa-discrepância (conjugado da razão áurea, (sqrt(5)-1)/2).
# frac(n*phi) preenche [0,1) mais uniformemente que qualquer racional -> a
# distribuição de amplitude é amostrada por igual sem RNG e sem blocagem.
_GOLDEN = 0.6180339887498949


def _norm_ppf(q: np.ndarray) -> np.ndarray:
    """Inversa da CDF normal padrão (aproximação racional de Acklam, ~1e-9).

    Sem dependência de scipy. Domínio (0,1); valores fora são clipados.
    """
    q = np.clip(np.asarray(q, dtype=float), 1e-12, 1.0 - 1e-12)
    a = [-3.969683028665376e+01, 2.209460984245205e+02, -2.759285104469687e+02,
         1.383577518672690e+02, -3.066479806614716e+01, 2.506628277459239e+00]
    b = [-5.447609879822406e+01, 1.615858368580409e+02, -1.556989798598866e+02,
         6.680131188771972e+01, -1.328068155288572e+01]
    c = [-7.784894002430293e-03, -3.223964580411365e-01, -2.400758277161838e+00,
         -2.549732539343734e+00, 4.374664141464968e+00, 2.938163982698783e+00]
    d = [7.784695709041462e-03, 3.224671290700398e-01, 2.445134137142996e+00,
         3.754408661907416e+00]
    plow, phigh = 0.02425, 1.0 - 0.02425
    out = np.empty_like(q)
    # cauda inferior
    lo = q < plow
    if np.any(lo):
        r = np.sqrt(-2.0 * np.log(q[lo]))
        out[lo] = (((((c[0]*r+c[1])*r+c[2])*r+c[3])*r+c[4])*r+c[5]) / \
                  ((((d[0]*r+d[1])*r+d[2])*r+d[3])*r+1.0)
    # cauda superior
    hi = q > phigh
    if np.any(hi):
        r = np.sqrt(-2.0 * np.log(1.0 - q[hi]))
        out[hi] = -(((((c[0]*r+c[1])*r+c[2])*r+c[3])*r+c[4])*r+c[5]) / \
                   ((((d[0]*r+d[1])*r+d[2])*r+d[3])*r+1.0)
    # região central
    mid = ~(lo | hi)
    if np.any(mid):
        r = q[mid] - 0.5
        s = r * r
        out[mid] = (((((a[0]*s+a[1])*s+a[2])*s+a[3])*s+a[4])*s+a[5])*r / \
                   (((((b[0]*s+b[1])*s+b[2])*s+b[3])*s+b[4])*s+1.0)
    return out


def _hist_ppf(q: np.ndarray, hist: Sequence[Tuple[float, float]]) -> np.ndarray:
    """Inversa da CDF de um histograma empírico [(amplitude, peso), ...].

    Distribuição discreta: cada quantil cai num bin conforme os pesos
    acumulados. Ordena por amplitude; pesos normalizados internamente.
    """
    amps = np.array([h[0] for h in hist], dtype=float)
    w = np.array([h[1] for h in hist], dtype=float)
    order = np.argsort(amps)
    amps, w = amps[order], w[order]
    w = np.clip(w, 0.0, None)
    tot = w.sum()
    if tot <= 0:
        return np.full_like(np.asarray(q, dtype=float), amps.mean())
    cum = np.cumsum(w) / tot                 # bordas superiores acumuladas
    idx = np.searchsorted(cum, np.clip(q, 0.0, 1.0 - 1e-12), side="right")
    idx = np.clip(idx, 0, len(amps) - 1)
    return amps[idx]


def spectrum_schedule(n_cycles: int,
                      mean: float,
                      std: float = 0.0,
                      hist: Optional[Sequence[Tuple[float, float]]] = None,
                      lo: float = 0.0,
                      hi: Optional[float] = None,
                      phase: float = 0.0) -> np.ndarray:
    """Cronograma determinístico de amplitude por ciclo a partir de uma distribuição.

    Parâmetros
    ----------
    n_cycles : int      -> comprimento do array retornado (>=0).
    mean     : float    -> amplitude média (mesmas unidades da saída).
    std      : float    -> desvio-padrão (normal truncada). 0 => constante.
    hist     : lista de (amplitude, peso) -> distribuição empírica; se dada,
               SOBREPÕE mean/std (usada p/ base+picos, ex.: Bauer 80/150 µm).
    lo, hi   : recorte físico das amplitudes (hi None => sem teto superior).
    phase    : float    -> offset [0,1) na sequência de baixa-discrepância. A
               MESMA distribuição com phase diferente => REALIZAÇÃO diferente
               (mesma média/desvio, ordem de picos diferente). Modela o fato de
               que repetições nominalmente idênticas amostram o espectro
               aleatório em fases distintas => scatter no ciclo de colapso. É
               inerentemente desconhecível por-teste (marginaliza-se sobre ele,
               não se fita). phase=0 => comportamento default.

    Retorna
    -------
    np.ndarray de comprimento n_cycles.

    Retrocompat: std=0 e hist=None => np.full(n_cycles, mean) EXATO
    (independe de phase — sem distribuição, não há o que reordenar).
    """
    n = int(max(n_cycles, 0))
    if n == 0:
        return np.zeros(0, dtype=float)
    if hist is None and (std is None or std <= 0.0):
        return np.full(n, float(mean), dtype=float)     # constante, bit-idêntico
    # sequência de quantis de baixa-discrepância, centrada (n+0.5) + fase
    q = np.mod((np.arange(n) + 0.5) * _GOLDEN + float(phase), 1.0)
    if hist is not None:
        amp = _hist_ppf(q, hist)
    else:
        amp = float(mean) + float(std) * _norm_ppf(q)
    hi_eff = np.inf if hi is None else float(hi)
    return np.clip(amp, float(lo), hi_eff)
