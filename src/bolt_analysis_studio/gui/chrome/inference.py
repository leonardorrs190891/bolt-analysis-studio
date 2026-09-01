"""Funções de inferência para os smart defaults (AutoComboBox) — puras/testáveis.

Cada função recebe um dict de contexto (extraído do modelo/carregamento) e
devolve a escolha recomendada. Usadas pelo AutoComboBox como `inference_fn`.
"""
from __future__ import annotations


def infer_control_mode(ctx: dict) -> str:
    # Amplitude de deslocamento imposta (Junker) → controle por deslocamento.
    return "Displacement" if ctx.get("delta_amplitude") else "Force"


def infer_integrator(ctx: dict) -> str:
    # HHT-α adiciona amortecimento numérico (filtra alta frequência do impacto
    # em ensaios crank-driven); Newmark-β é o default de propósito geral.
    return "HHT-α" if ctx.get("damping") else "Newmark-β"


def infer_friction_model(ctx: dict) -> str:
    # Junta lubrificada → regime de Stribeck; a seco → Coulomb.
    return "Stribeck" if ctx.get("lubricated") else "Coulomb"
