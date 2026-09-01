# -*- coding: utf-8 -*-
"""Leitores de PROVENIENCIA — constantes lidas de FEATURES medidas do dado
(sec4.40/L24 + sec4.42 proposta (d), "ler em vez de fitar"), no PACOTE do
software para consumo por GUI/solver/dialogo de calibracao.

Regra L24: quando um handbook (VDI f_Z por classe de rugosidade) e um valor
DATA-IMPLICITO divergem, o data-implicito — lido da feature que a constante
governa — e mais especifico e ganha. E' proveniencia, nao fit:
- embedding  <-> queda-inicial da curva (drop*F0/k_b)     [axial: -90% de erro]
- arrest floor <-> plato final da curva
- (delta_free <-> regressao de onset: por-campanha, nao portado)

Fonte UNICA: `New_Theory/library_common.py` DELEGA para este modulo (nunca
duplicar a logica — doutrina knowledge_base).
"""
from __future__ import annotations

from typing import Tuple

import numpy as np


def emb_depth_from_early_drop(early_drop_frac: float, F0_N: float, k_b: float,
                              vdi_ref_m: float = None) -> Tuple[float, dict]:
    """emb_depth [m] IMPLICITO da feature de QUEDA-INICIAL de uma curva medida.

    O embedding e a fonte da queda rapida da pre-carga no inicio do ensaio (VDI
    2230): o assentamento das asperezas remove delta_emb e dF_0 = -k_b*delta_emb,
    logo delta_emb = (queda inicial em fracao de F0) * F0 / k_b.

    Proveniencia 'data_implied_early_drop' (sec4.40 / L24): quando HA curva de
    referencia, ler o emb da queda-inicial (feature MEDIDA, como floor/W_crit) e
    mais especifico que o handbook VDI f_Z por classe de rugosidade — que pode
    super- ou sub-estimar o rig (Li2022ti: handbook Rz<4 = 3.5 um vs
    data-implicito 1.6 um; MAE axial 0.064->0.039). Regra: quando o handbook e o
    data-implicito divergem, o data-implicito ganha (feature que a constante
    governa: embedding <-> queda-inicial). E' proveniencia, nao fit.

    CAVEAT: a queda ate o primeiro ponto pos-inicio inclui um POUCO de creep
    (limite superior do embedding); use o 2o ponto amostrado (nao um ponto muito
    tardio). Passe `vdi_ref_m` (o valor handbook) p/ registrar a razao de
    divergencia no breakdown. FRONTEIRA (sec4.40 adendo 3): metodo AXIAL —
    no transversal a queda-inicial e loosening/creep-dominada (mis-atribuiria).
    """
    emb_m = max(float(early_drop_frac), 0.0) * float(F0_N) / max(float(k_b), 1.0)
    prov = dict(provenance="data_implied_early_drop",
                early_drop_frac=float(early_drop_frac),
                F0_N=float(F0_N), k_b=float(k_b), emb_um=emb_m * 1e6)
    if vdi_ref_m is not None:
        prov["vdi_handbook_um"] = float(vdi_ref_m) * 1e6
        prov["ratio_data_over_handbook"] = (
            emb_m / vdi_ref_m if vdi_ref_m > 0 else None)
        prov["diverges"] = (vdi_ref_m > 0
                            and not (0.5 <= emb_m / vdi_ref_m <= 2.0))
    return emb_m, prov


def emb_depth_from_curve(cyc, ratio, F0_N: float, k_b: float,
                         early_index: int = 1,
                         vdi_ref_m: float = None) -> Tuple[float, dict]:
    """emb_depth [m] data-implicito lendo a queda-inicial de (cyc, ratio).

    `ratio` e normalizado internamente (ratio/ratio[0]); a queda ate o ponto
    `early_index` (default 1 = 2o ponto amostrado) da a fracao de queda inicial.
    Wrapper de :func:`emb_depth_from_early_drop`. Falha -> banda VDI (nunca raise
    silencioso: retorna emb=0 com provenance 'degraded' se a curva e curta).
    """
    r = np.asarray(ratio, dtype=float)
    if r.size <= early_index or r[0] <= 0:
        return 0.0, dict(provenance="degraded", reason="curva curta/invalida")
    r = r / r[0]
    drop = max(1.0 - float(r[early_index]), 0.0)
    emb_m, prov = emb_depth_from_early_drop(drop, F0_N, k_b, vdi_ref_m)
    prov["early_index"] = early_index
    prov["early_cycle"] = float(np.asarray(cyc, dtype=float)[early_index])
    return emb_m, prov


def arrest_floor_from_curve(ratio, tail_frac: float = 0.05,
                            min_points: int = 2) -> Tuple[float, dict]:
    """loose_arrest_floor IMPLICITO do PLATO FINAL de uma curva medida.

    O piso de arresto (nucleo auto-travado, spec 2026-07-07) e a fracao de F0
    onde o dreno de preload trava — a feature que o governa e o plato do FIM da
    curva ("floor lido do fim do dado", pratica das campanhas §4.15/§4.22).
    Media dos ultimos max(min_points, ceil(tail_frac*n)) pontos, normalizada
    por ratio[0]. Curva que termina em queda (sem plato) => o valor e um
    LIMITE INFERIOR do floor: o breakdown marca plateau=False quando o ultimo
    trecho ainda cai mais que 2% relativo.
    """
    r = np.asarray(ratio, dtype=float)
    if r.size < 2 or r[0] <= 0:
        return 0.0, dict(provenance="degraded", reason="curva curta/invalida")
    r = r / r[0]
    k = max(int(min_points), int(np.ceil(tail_frac * r.size)))
    tail = r[-k:]
    floor = float(np.mean(tail))
    plateau = bool(abs(float(tail[0]) - float(tail[-1]))
                   <= 0.02 * max(float(tail[0]), 1e-9))
    return max(floor, 0.0), dict(provenance="data_end_plateau",
                                 n_tail=int(k), plateau=plateau,
                                 note=None if plateau else
                                 "fim ainda em queda: floor = limite inferior")
