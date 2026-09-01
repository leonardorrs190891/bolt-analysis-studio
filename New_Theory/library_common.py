"""Fundacao comum da Fase 1 do confronto com a biblioteca (spec 2026-07-03).

Regras de proveniencia (spec §1.3/§1.3a): todo input carrega Provenance
('paper' = nota de aparato; 'handbook' = tabela VDI 2230/DIN; 'iso' = tabela
de rosca; 'assumed' = regra do MSD_BLOCK_COVERAGE, sujeito a banda de
sensibilidade; 'stage_a' = constante congelada do bloco shared).
"""
from __future__ import annotations

import json
import types
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Tuple

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
import sys  # noqa: E402
sys.path.insert(0, str(ROOT / "src"))

from bolt_analysis_studio.numerical.dynamic_stiffness_analyzer import (  # noqa: E402
    JointGeometry,
)

SHARED_JSON = ROOT / "New_Theory" / "joint_calibrations.json"


@dataclass(frozen=True)
class Provenance:
    value: float
    source: str      # 'paper' | 'handbook' | 'iso' | 'assumed' | 'stage_a'
    note: str = ""


# --- ISO 898-1 / ISO 724: roscas usadas pela biblioteca ----------------------
def _d2(d: float, p: float) -> float:
    return d - 0.6495 * p


ISO_THREADS: Dict[str, dict] = types.MappingProxyType({
    "M6x1.0":   dict(d_mm=6.0,  p_mm=1.0,  A_s_mm2=20.1,  d2_mm=_d2(6, 1.0)),
    "M8x1.25":  dict(d_mm=8.0,  p_mm=1.25, A_s_mm2=36.6,  d2_mm=_d2(8, 1.25)),
    "M10x1.5":  dict(d_mm=10.0, p_mm=1.5,  A_s_mm2=58.0,  d2_mm=_d2(10, 1.5)),
    "M12x1.75": dict(d_mm=12.0, p_mm=1.75, A_s_mm2=84.3,  d2_mm=_d2(12, 1.75)),
    "M12x1.5":  dict(d_mm=12.0, p_mm=1.5,  A_s_mm2=88.1,  d2_mm=_d2(12, 1.5)),
    "M16x2.0":  dict(d_mm=16.0, p_mm=2.0,  A_s_mm2=157.0, d2_mm=_d2(16, 2.0)),
    "M30x3.5":  dict(d_mm=30.0, p_mm=3.5,  A_s_mm2=561.0, d2_mm=_d2(30, 3.5)),
    "M42x4.5":  dict(d_mm=42.0, p_mm=4.5,  A_s_mm2=1121.0, d2_mm=_d2(42, 4.5)),
})

# --- VDI 2230-1 Tabela 5 (valores-guia de assentamento f_Z, um, POR SUPERFICIE;
#     coluna de carregamento axial; carregamento cisalhante tem interfaces
#     maiores — aproximacao documentada: usar coluna axial + banda de classe
#     adjacente como sensibilidade, spec §1.3a).
#     NB (2026-07-07): a classe "Rz<4" (retificado/lapeado fino) NAO e VDI — a
#     tabela VDI 2230-1 5.4/1 tem PISO em Rz<10 (nao sub-divide superficies finas
#     => sobre-preve ~4x p/ roscas retificadas; MODEL_LEGITIMACY §4.6). "Rz<4" e
#     proveniencia HANDBOOK (Bolt Science / consenso de engenharia: assentamento
#     ~1 um/interface no canto liso da faixa 1-7 um; boltscience.com/pages/
#     embedding.htm), verificada externamente 2026-07-07. Total ~3.5 um p/ pilha
#     rosqueada (n_if=1), dentro da faixa implicada pelo Liu2017 (1.4-4 um). -------
_VDI_FZ_UM = types.MappingProxyType({
    #  classe        rosca  apoio(cabeca/porca)  interface interna
    "Rz<4":      dict(thread=1.0, bearing=1.0, interface=0.5),   # ground/lapped — Bolt Science (handbook), NAO VDI
    "Rz<10":     dict(thread=3.0, bearing=2.5, interface=1.5),
    "Rz10-40":   dict(thread=3.0, bearing=3.0, interface=2.0),
    "Rz40-160":  dict(thread=3.0, bearing=4.0, interface=3.0),
})
_VDI_ORDER = ["Rz<4", "Rz<10", "Rz10-40", "Rz40-160"]


def emb_depth_vdi(rz_class: str, n_inner_interfaces: int,
                  loading: str = "axial") -> Tuple[float, dict]:
    """f_Z total da pilha [m] = rosca + 2 apoios + n interfaces internas.
    Proveniencia 'handbook'. `loading` registrado no breakdown (coluna axial
    usada para ambos — aproximacao pre-registrada)."""
    row = _VDI_FZ_UM[rz_class]
    total_um = (row["thread"] + 2.0 * row["bearing"]
                + n_inner_interfaces * row["interface"])
    return total_um * 1e-6, dict(rz_class=rz_class, loading=loading,
                                 thread_um=row["thread"],
                                 bearing_um=row["bearing"],
                                 interface_um=row["interface"],
                                 n_inner_interfaces=n_inner_interfaces,
                                 total_um=total_um)


# Leitores de proveniencia (sec4.40/L24) — MOVIDOS para o pacote do software
# (sec4.42d, "implemente no bolt analysis studio"): fonte unica em
# bolt_analysis_studio.calibration.provenance; aqui so re-export (as campanhas
# continuam importando de library_common sem mudanca).
from bolt_analysis_studio.calibration.provenance import (  # noqa: E402,F401
    emb_depth_from_early_drop, emb_depth_from_curve, arrest_floor_from_curve)


def vdi_adjacent_classes(rz_class: str) -> Tuple[str, str]:
    """Classes vizinhas para a banda de sensibilidade (§1.3a)."""
    i = _VDI_ORDER.index(rz_class)
    lo = _VDI_ORDER[max(i - 1, 0)]
    hi = _VDI_ORDER[min(i + 1, len(_VDI_ORDER) - 1)]
    return lo, hi


def frozen_constants(json_path: Path = SHARED_JSON,
                     include_damage: bool = False) -> Tuple[dict, Dict[str, Provenance]]:
    """Constantes fisicas CONGELADAS do Estagio A: priors do bloco shared com
    os valores fitados por cima; emb_depth EXCLUIDO (input por junta, §1.3a).
    Tuners nao entram (defaults 1.0 do engine)."""
    data = json.loads(json_path.read_text(encoding="utf-8"))
    consts = dict(data["shared"]["constants"])
    # NB (2026-07-04): desde a adocao da conformacao o bloco shared inclui
    # W_conf_ref/conform_pressure_exp/p_ref_conform, entao consts os carrega.
    # A_contact JA eh per-rig (geometry_for computa a area real do anel de apoio,
    # 11g) => p=F0/A_contact e FISICA cross-rig (Karlsen fora do espurio ~7-14).
    # Caveat RESIDUAL (§4.9 Fase 3): p_ref_conform=5e8 e W_conf_ref=7671 sao
    # constantes POR PAR (UFU, sem ancora) aplicadas cross-pair -> a MAGNITUDE da
    # conformacao e aproximada fora do par UFU (honesto per-par, nao artefato).
    consts.pop("emb_depth", None)
    if not include_damage:
        # c_D/k_dmg_wear crescem de trabalho de slip mesmo sem dano inicial;
        # inertes em axial puro (slip=0), mas NAO em transversal. Doutrina
        # (Fase 1A, MODEL_LEGITIMACY §4.8): no Estagio A o dano so ativa em
        # juntas PRE-DANIFICADAS (damage_active), entao juntas novas usam o
        # default include_damage=False; passe True apenas para condicoes que
        # declarem dano previo (reuso/reaperto).
        consts.pop("c_D", None)
        consts.pop("k_dmg_wear", None)
    prov = {k: Provenance(v, "stage_a", "bloco shared (joint_calibrations.json)")
            for k, v in consts.items()}
    return consts, prov


def load_full_curve(csv_rel_path: str) -> Tuple[np.ndarray, np.ndarray]:
    d = np.genfromtxt(ROOT / csv_rel_path, delimiter=",", skip_header=1,
                      encoding="utf-8")
    return d[:, 0], d[:, 1]


def geometry_for(bolt_size: str, grip_mm: float, r_bearing_mm: float = None,
                 A_contact_mm2: float = None, E: float = None) -> JointGeometry:
    """JointGeometry a partir da tabela ISO + grip. r_bearing default = 0.75*d
    (raio efetivo do apoio da cabeca = raio EXTERNO, 12mm/16mm p/ M16).

    A_contact default = AREA REAL do anel de apoio POR PARAFUSO (roadmap 11g /
    MODEL_LEGITIMACY §4.9 Fase 3 — antes era 100 mm2 FIXO p/ qualquer parafuso):
        A = pi * (r_bearing^2 - r_furo^2),  r_furo = 0.55*d  (folga ~1.1*d)
    Escala com d^2 (~A_s), entao a pressao de contato p = F0/A_contact fica
    FISICA por rig e a conformacao cross-rig deixa de ser artefato — Karlsen
    M30/M42 saem do espurio p/p_ref~7-14 (que vinha do 100 mm2 fixo) p/ ~1.
    Como A_contact ~ 1.29-1.43*A_s (A_s nao escala perfeito com d^2), o p_ref=5e8
    do bloco passa a corresponder a ~77-86% do proof (80% no M16) — referencia de
    sobretorque razoavelmente consistente entre tamanhos, nao uma constante exata.
    NB: A_contact tambem e o denominador da profundidade de wear de Archard
    (depth=V/A_contact), entao esta correcao torna FISICOS tanto o gate de pressao
    quanto o wear cross-rig no harness de transferencia.
    Passe A_contact_mm2 explicito p/ sobrepor com a area REAL medida de um rig."""
    t = ISO_THREADS[bolt_size]
    d_mm = t["d_mm"]
    r_bear_mm = r_bearing_mm if r_bearing_mm is not None else 0.75 * d_mm
    if A_contact_mm2 is None:
        r_furo_mm = 0.55 * d_mm                       # furo de folga ~1.1*d
        A_contact_mm2 = max(np.pi * (r_bear_mm ** 2 - r_furo_mm ** 2), 1.0)
    kw = dict(A_s=t["A_s_mm2"] * 1e-6,
              L_eff=grip_mm * 1e-3,
              d_2=t["d2_mm"] * 1e-3,
              pitch=t["p_mm"] * 1e-3,
              r_bearing=r_bear_mm * 1e-3,
              A_contact=A_contact_mm2 * 1e-6)
    if E is not None:
        kw["E"] = E
    return JointGeometry(**kw)
