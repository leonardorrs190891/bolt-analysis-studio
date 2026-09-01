# -*- coding: utf-8 -*-
"""Shim de traducao de TUNERS LEGADOS -> constantes fisicas (Estagio B §3.3,
spec 2026-07-02; plano 2026-07-08; executado 2026-07-09 por decisao do
professor).

A camada de tuners (k_*_scale / Phi_*_correction / k_damage_scale) e removida
do engine na Fase 4; entradas legadas (overrides de sessao, payloads do server,
`.msd` antigos se algum dia carregarem tuners) sao traduzidas AQUI, uma vez, na
fronteira de consumo (solver_worker/_compute_v2_history e server/_material) —
nunca na deserializacao.

Mapa de fold (exatidao VERIFICADA por teste, tests/test_tuner_shim.py):
  k_emb_scale        -> emb_depth     *= v   EXATO (dF_0 e dE; a asintota escala)
  k_creep_scale      -> C_creep       *= v   EXATO (Norton linear no C)
  k_wear_scale_tr    -> k_wear_spec   *= v   (se ativo) senao K_archard *= v
                                             RATIO-EXATO com dano OFF; com dano
                                             ON e' APROXIMADO (dE do wear carrega
                                             k_scale mas nao K => W_slip_cycle
                                             muda => trajetoria de D desloca) —
                                             warning explicito
  Phi_tr_correction  -> tr_loose_gain *= v   EXATO no ramo transversal ativo
                                             (Phi_tr_active = gain*corr; o ramo
                                             Phi_eff transversal e' sobreposto)
  k_loose_scale_tr   -> tr_loose_gain *= v   APROXIMADO (d_theta e' linear no
                                             k_scale, mas o gain entra em
                                             slip_fraction nao-linearmente) —
                                             warning explicito
  k_damage_scale     -> c_D           *= v   EXATO (dD ~ k_damage*c_D linear)
  k_wear_scale_ax / k_loose_scale_ax / Phi_ax_correction:
                     DROPADAS com DeprecationWarning (spec §3.2: anisotropia
                     axial futura entra como razao fisica nomeada, nao tuner).

Semantica: MULTIPLICA sobre a base efetiva (overrides > base > default de
JointMaterial); nunca sobrescreve. Idempotente (a saida nao contem chaves de
tuner). v==1.0 => no-op (nao injeta a constante alvo).
"""
from __future__ import annotations

import dataclasses
import warnings
from typing import Dict, Optional

from bolt_analysis_studio.numerical.dynamic_stiffness_analyzer import JointMaterial

# tuner -> (alvo, exato?, nota)
_FOLD = {
    "k_emb_scale":       ("emb_depth", True, ""),
    "k_creep_scale":     ("C_creep", True, ""),
    "k_wear_scale_tr":   ("__wear__", False,
                          "ratio-exato com dano OFF; aproximado com dano ON "
                          "(dE do wear carrega o tuner, nao a constante)"),
    "Phi_tr_correction": ("tr_loose_gain", True, ""),
    "k_loose_scale_tr":  ("tr_loose_gain", False,
                          "aproximado: gain entra em slip_fraction "
                          "nao-linearmente"),
    "k_damage_scale":    ("c_D", True, ""),
}
_DROP_AX = ("k_wear_scale_ax", "k_loose_scale_ax", "Phi_ax_correction")

_JM_DEFAULTS = {f.name: f.default for f in dataclasses.fields(JointMaterial)}


def _base_value(name: str, out: Dict, base: Optional[Dict]) -> float:
    if name in out:
        return float(out[name])
    if base and name in base:
        return float(base[name])
    return float(_JM_DEFAULTS[name])


def translate_legacy_tuners(overrides: Dict, base: Optional[Dict] = None,
                            warn: bool = True) -> Dict:
    """Traduz chaves de tuner legadas em `overrides` para constantes fisicas.

    Retorna um NOVO dict sem nenhuma chave de tuner; as demais chaves passam
    intactas. `base` (opcional) e o dict de constantes efetivas sob o qual os
    overrides serao aplicados (para o multiply-never-overwrite); ausente, usa
    os defaults de JointMaterial. Idempotente por construcao.
    """
    out = {k: v for k, v in overrides.items()
           if k not in _FOLD and k not in _DROP_AX}
    for k in _DROP_AX:
        if k in overrides:
            v = overrides[k]
            if warn and float(v) != 1.0:
                warnings.warn(
                    f"Estagio B: tuner axial legado '{k}={v}' DROPADO (spec "
                    "§3.2 — anisotropia axial futura sera uma razao fisica "
                    "nomeada, nao tuner).", DeprecationWarning, stacklevel=2)
    for k, (target, exact, note) in _FOLD.items():
        if k not in overrides:
            continue
        v = float(overrides[k])
        if v == 1.0:
            continue                                    # no-op: nao injeta alvo
        if target == "__wear__":
            # roteia p/ k_wear_spec se a razao identificavel esta ativa na
            # base/overrides (merge §4.42a), senao K_archard (via legada)
            spec_active = _base_value("k_wear_spec", out, base) > 0.0
            target = "k_wear_spec" if spec_active else "K_archard"
        out[target] = _base_value(target, out, base) * v
        if warn and not exact:
            warnings.warn(
                f"Estagio B: fold '{k}={v}' -> '{target}' e APROXIMADO "
                f"({note}).", DeprecationWarning, stacklevel=2)
    return out
