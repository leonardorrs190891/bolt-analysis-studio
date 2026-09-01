# -*- coding: utf-8 -*-
"""Formas de biblioteca (proveniência-primeiro) ACESSÍVEIS AO SOFTWARE — mesmo
espírito de `knowledge_base.py` (spec 2026-07-16, plano L1-L7, Fatia 3 / L2,
roadmap #10 / MODEL_LEGITIMACY §4.8).

`New_Theory/library_common.py` (campanhas) resolve geometria via `geometry_for`
e permanece a fonte para os scripts de calibração fora do pacote instalado;
este módulo é o lado "engine-facing" — mora em `src/` para que
`numerical/dynamic_stiffness_analyzer.py` (camada numérica) possa chamar
`kj_from_geometry` sem alcançar `New_Theory/` (fora do pacote, camada errada).
Mesmo padrão de merge usado por `provenance.py` (sec4.42d): fonte única aqui,
sem duplicação de valor — os coeficientes por-material do Wileman vêm de
`knowledge_base.kj_law()`, não são re-hardcoded.
"""
from __future__ import annotations

import math


def kj_from_geometry(d_mm: float, L_mm: float, E_Pa: float,
                     d_hole_mm: float, d_washer_mm: float,
                     mode: str = "pedersen", material: str = "steel") -> float:
    """k_j(geometria, material) — rigidez axial do membro/junta [N/m] (L2,
    roadmap #10 / MODEL_LEGITIMACY §4.8: o mapeamento grip→k_j com constante
    FIXA não escalava com a espessura do membro — Rousseau t10/12/14
    falsificou; esta é a forma física faltante).

    Duas leis cross-checáveis (`knowledge_base.kj_law()`, dados em
    `New_Theory/r5_anchors.json["kj_laws"]`):

    - ``mode="pedersen"`` (PRIMÁRIA — Pedersen 2008, doi
      10.1007/s00419-007-0142-0, Eq.31; rank "closest-to-truth", +24% vs
      medido, Rousseau 2024)::

          k_m = E·d·(0.59·(β²−α²)·d/L + 0.20·(β+α))

      α = d_furo/d, β = d_arruela/d (geometria do cone de pressão truncado —
      transição de largura entre o furo de folga e a borda da arruela).
      Material-independente (a Eq.31 não tabela A/B por material); `material`
      é ignorado neste modo.

    - ``mode="wileman"`` (CROSS-CHECK — Wileman/Choudhury/Hodges 1991, doi
      10.1115/1.2912799; rank "+45-59% (superestima)")::

          k_m/(E·d) = A·exp(B·d/L)

      A,B por material vêm de ``knowledge_base.kj_law("wileman1991")["AB"]``
      (sem duplicação de valor — tabela única no KB). ``d_hole_mm``/
      ``d_washer_mm`` não entram nesta lei (Wileman não modela furo/arruela
      separadamente — só a razão d/L).

    Args:
        d_mm: diâmetro NOMINAL do parafuso [mm] (não o diâmetro de passo d_2
            — ver `JointGeometry.d_nominal` no engine, invertido de d_2/pitch
            via ISO 724).
        L_mm: grip / comprimento efetivo [mm].
        E_Pa: módulo de Young [Pa].
        d_hole_mm / d_washer_mm: diâmetro do furo de folga / diâmetro externo
            da arruela [mm] — só usados por ``mode="pedersen"``.
        mode: ``"pedersen"`` (default) | ``"wileman"``. Outro valor levanta
            ``ValueError``.
        material: só usado por ``mode="wileman"``. Default ``"steel"`` — a
            maioria dos casos calibrados desta biblioteca é parafuso de aço
            (M16 shear UFU, Rousseau steel); chave ausente na tabela AB
            levanta ``KeyError`` (loud by design, mesmo idioma de
            ``wear_spec_anchor``/``mu_thread_anchor`` em `knowledge_base.py`
            — passe ``material="general"`` explicitamente p/ junta de
            material desconhecido/misto).

    Returns:
        k_j [N/m].
    """
    d, L = d_mm * 1e-3, L_mm * 1e-3
    if mode == "wileman":
        from bolt_analysis_studio.calibration import knowledge_base as kb
        A, B = kb.kj_law("wileman1991")["AB"][material]
        return E_Pa * d * A * math.exp(B * d / L)
    if mode == "pedersen":
        alpha, beta = d_hole_mm / d_mm, d_washer_mm / d_mm
        return E_Pa * d * (0.59 * (beta**2 - alpha**2) * d / L
                           + 0.20 * (beta + alpha))
    raise ValueError(mode)
