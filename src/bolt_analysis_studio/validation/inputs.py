# -*- coding: utf-8 -*-
"""Primitivas de input com proveniencia — PORT de New_Theory/library_common.py
(2026-07-10, spec 2026-07-10-validation-case-reports-design.md §2.4): a fonte
canonica passa a ser o produto; a sandbox delegara aqui em follow-up. Valores
IDENTICOS aos da campanha (teste de paridade tests/test_validation_inputs.py).
Constantes vem dos JSONs versionados (bloco shared de joint_calibrations.json).

Regras de proveniencia (spec 2026-07-03 §1.3/§1.3a): todo input carrega
Provenance ('paper' = nota de aparato; 'handbook' = tabela VDI 2230/DIN;
'iso' = tabela de rosca; 'assumed' = regra do MSD_BLOCK_COVERAGE;
'stage_a' = constante congelada do bloco shared)."""
from __future__ import annotations

import json
import re
import types
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Tuple

import numpy as np

from ..numerical.dynamic_stiffness_analyzer import JointGeometry


def repo_root() -> Path:
    root = Path(__file__).resolve().parents[3]
    if not (root / "New_Theory").exists():       # layout sem src/ intermediario
        root = Path(__file__).resolve().parents[2]
    return root


SHARED_JSON = repo_root() / "New_Theory" / "joint_calibrations.json"


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
#     coluna de carregamento axial). NB: a classe "Rz<4" NAO e VDI — proveniencia
#     HANDBOOK (Bolt Science, verificada 2026-07-07; MODEL_LEGITIMACY §4.6). -----
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
    consts.pop("emb_depth", None)
    if not include_damage:
        # c_D/k_dmg_wear crescem de trabalho de slip mesmo sem dano inicial;
        # doutrina Estagio A (MODEL_LEGITIMACY §4.8): dano so ativa em juntas
        # PRE-DANIFICADAS — juntas novas usam o default include_damage=False.
        consts.pop("c_D", None)
        consts.pop("k_dmg_wear", None)
    prov = {k: Provenance(v, "stage_a", "bloco shared (joint_calibrations.json)")
            for k, v in consts.items()}
    return consts, prov


def load_full_curve(csv_rel_path: str) -> Tuple[np.ndarray, np.ndarray]:
    """Curva de referencia (repo-relativa). 2 colunas (cycle, ratio) ou
    3 colunas UFU (cycle, F_kN, F_over_F0) — sempre col 0 e a ULTIMA."""
    d = np.genfromtxt(repo_root() / csv_rel_path, delimiter=",",
                      skip_header=1, encoding="utf-8")
    return d[:, 0], d[:, -1]


def geometry_for(bolt_size: str, grip_mm: float, r_bearing_mm: float = None,
                 A_contact_mm2: float = None, E: float = None) -> JointGeometry:
    """JointGeometry a partir da tabela ISO + grip. r_bearing default = 0.75*d.
    A_contact default = AREA REAL do anel de apoio POR PARAFUSO (roadmap 11g /
    MODEL_LEGITIMACY §4.9 Fase 3): A = pi*(r_bearing^2 - r_furo^2),
    r_furo = 0.55*d (folga ~1.1*d). Passe A_contact_mm2 explicito p/ sobrepor
    com a area REAL medida de um rig."""
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


def geometry_for_case(case, grip_mm: float, E: float = None) -> JointGeometry:
    """geometry_for pela tabela ISO quando bolt_size e' metrico conhecido;
    fallback GENERICO dos campos d/p do proprio caso (parafusos nao-metricos,
    ex. UFU 3/4\" UNC) com A_s = pi/4*(d - 0.9382p)^2 (formula padrao de area
    de tensao; ~1.5% do A_t tabelado UNC — proveniencia 'assumed')."""
    if case.bolt_size in ISO_THREADS:
        return geometry_for(case.bolt_size, grip_mm, E=E)
    d = float(case.bolt_diameter_mm)
    p = float(case.pitch_mm)
    if d <= 0 or p <= 0:
        raise ValueError(f"geometria sem proveniência: bolt_size "
                         f"{case.bolt_size!r} fora da tabela ISO e sem d/p")
    d_s = d - 0.9382 * p
    A_s_mm2 = np.pi / 4.0 * d_s ** 2
    r_bear_mm = 0.75 * d
    r_furo_mm = 0.55 * d
    A_contact_mm2 = max(np.pi * (r_bear_mm ** 2 - r_furo_mm ** 2), 1.0)
    kw = dict(A_s=A_s_mm2 * 1e-6, L_eff=grip_mm * 1e-3,
              d_2=_d2(d, p) * 1e-3, pitch=p * 1e-3,
              r_bearing=r_bear_mm * 1e-3, A_contact=A_contact_mm2 * 1e-6)
    if E is not None:
        kw["E"] = E
    return JointGeometry(**kw)


# --- inputs por caso (port de transfer_validation.inputs_for, estendido) ----
F_AMP_RATIO = 0.4          # literatura Pai&Hess 2002 (0.38-0.49 medido)
RZ_DEFAULT = "Rz10-40"
SOURCE_INPUTS = {
    "LIU_2025":      dict(grip=None, mu=(0.15, "assumed"), rz=RZ_DEFAULT),
    "BAUER_2024":    dict(grip=("bolt", "paper"), mu=(0.15, "assumed"), rz=RZ_DEFAULT),
    "LU_2024":       dict(grip=None, mu=(0.18, "paper"), rz=RZ_DEFAULT),
    "ICMEZ_2025":    dict(grip=("csv", "paper"), mu=(0.115, "paper"), rz=RZ_DEFAULT),
    "YANG_2019":     dict(grip=None, mu=(0.15, "assumed"), rz=RZ_DEFAULT),
    # F_amp=("csv", ...): carga AXIAL por ensaio lida do stem (`_axNkN` /
    # `_axNpNkN`), Tabela 1 do paper. Correcao de PROVENIENCIA (prereg
    # 2026-08-19-yang2021-famp-proveniencia): o fallback universal punha
    # 0,4*F0 com rotulo "Pai&Hess" numa fonte cujo paper PUBLICA o valor.
    # ⚠️ Efeito fisico ZERO, medido com instrumento validado ANTES da
    # correcao: o caso e' montado com theta=90 e `settling_amplitude_factor`
    # faz F_ax = |F_amp*cos(theta)| = 0 => guard 1,0 — o F_amp e'
    # estruturalmente inerte em fonte transversal-pura. A excitacao COMPOSTA
    # do rig (axial 90 graus defasada do transversal) NAO e' representavel na
    # config atual; isto aqui conserta o REGISTRO, nao a fisica.
    "YANG_2021":     dict(grip=None, mu=(0.15, "assumed"), rz=RZ_DEFAULT,
                          F_amp=("csv", "paper (Table 1)")),
    "ROUSSEAU_2025": dict(grip=("csv", "paper"), mu=(0.15, "assumed"), rz=RZ_DEFAULT),
    "KARLSEN_2022":  dict(grip=None, mu=(0.15, "assumed"), rz=RZ_DEFAULT),
    # fontes axiais (tabela curada de New_Theory/calibrate_axial.py CONDITIONS;
    # nomes = enum ValidationSource, nao os rotulos da galeria LIU_2017_P0/AF):
    "LIU_2017_AXIAL":   dict(grip=(30.0, "paper"), mu=(0.15, "assumed"), rz="Rz<4"),
    "LI_2022_TRIBOINT": dict(grip=(25.0, "assumed"), mu=(0.15, "assumed"), rz="Rz<10"),
    # creep estatico marstruc (PR-2 iter.3): geometria de PAPER do harness da
    # ancora Fase 1C (M16x80 304SS, L=20mm, E=193 GPa — anchor_creep.py:40)
    "LI_2022_MARSTRUC": dict(grip=(20.0, "paper"), mu=(0.15, "assumed"),
                             rz="Rz<4", E=(193e9, "paper")),
    # reaperto Liu2022 Structures (PR-6 iter.4): inputs da campanha rodada-4
    # (validate_galling.py/validate_retightening.py): grip 50mm = 2 placas +
    # celula 20mm (assumed c/ sensibilidade); mu oil 0.176 = Motosh derivado
    # de T=80N.m + F0 medido 27kN (paper/L3; dry 0.236 via grupo adotado _dry)
    "LIU_2022_RETIGHT": dict(grip=(50.0, "assumed"), mu=(0.176, "paper"),
                             rz="Rz<4"),
    # Yang2023 IJPEM (PR-8b iter.4): grip ~25mm estimado NO PAPER (nota
    # "Reproduction Notes"); mu 0.18 = meio da faixa 0.15-0.20 do paper
    # (nao-lubrificado); E de placas aco (paper). emb adotado numerico
    # per-size (leitor L24 nas curvas below-threshold).
    "YANG_2023_IJPEM": dict(grip=(25.0, "paper"), mu=(0.18, "paper"),
                            rz=RZ_DEFAULT, E=(210e9, "paper")),
    # Rodada 4 (ingestao 2026-07-14): so o que tem proveniencia de PAPER entra
    # aqui; as demais fontes R4 caem na regra assumed (degradacao honesta).
    # Liu2016 Wear: mu=0.132 dry MEDIDO (DIN 946, nota do aparato); grip None
    # => 2.5d = 30 mm (M12), coincide com o rig irmao Liu2017.
    "LIU_2016": dict(grip=None, mu=(0.132, "paper"), rz=RZ_DEFAULT),
    # Qin2024 (PR-29): stack "double-coupon" = 2x CFRP 4mm + 2x washer Ti
    # 1.8mm = 11.6mm (nota; ambiguidade single/double registrada — o ganho e'
    # absorvido no C_creep lido via sonda). E do PARAFUSO Ti-6Al-4V (Tabela 1).
    "QIN_2024": dict(grip=(11.6, "paper"), mu=(0.15, "assumed"),
                     rz=RZ_DEFAULT, E=(115e9, "paper")),
    # Caccese2009 (PR-33): espessura do painel composto = DIAMETRO do parafuso
    # (nota do aparato) => grip por caso via modo "boltd".
    "CACCESE_2009": dict(grip=("boltd", "paper"), mu=(0.15, "assumed"),
                         rz=RZ_DEFAULT),
    # CHU_2026 (item B ASSINADO 2026-08-13, aplicado 2026-08-14 22:xx sob
    # "assino tudo"): Ra 0,4 um do artigo (tests 1-8) => classe VDI Rz<4.
    # O test9 (Ra 1,6 => Rz<10 => 9,5 um) vem por per_case no adopted_configs.
    # Os 3 do tripe (test1/5/6) tem emb pinado nos proprios grupos => o rz
    # nao os alcanca (medido bit-identico na sandbox antes de aplicar).
    "CHU_2026": dict(grip=None, mu=(0.15, "assumed"), rz="Rz<4"),
}
ROUSSEAU_GRIPS = {"t10": 25.0, "t12": 29.0, "t14": 33.0}
ICMEZ_GRIPS = {"lk13p8": 13.8, "lk19p8": 19.8}
BAUER_GRIPS = {"M8": 8.0, "M12": 12.0}


def _d_mm(case) -> float:
    try:
        return float(case.bolt_size.split("x")[0][1:])
    except (ValueError, IndexError):
        # nao-metrico (ex. UFU 3/4" UNC): o caso carrega o diametro em mm
        return float(getattr(case, "bolt_diameter_mm", 0.0) or 0.0)


def inputs_for(case) -> dict:
    """grip/mu/rz/F_amp com proveniencia. Fontes fora de SOURCE_INPUTS caem na
    regra assumed (grip 2.5d, mu 0.15, Rz default) — degradacao honesta.
    Casos do usuario (.bascase) trazem `_user_inputs` com proveniencia 'user'
    — o que o usuario informou vence; o resto cai na regra assumed."""
    ui = getattr(case, "_user_inputs", None)
    if ui is not None:
        d = _d_mm(case)
        return dict(
            grip_mm=ui.get("grip_mm", dict(value=2.5 * d, prov="assumed")),
            mu=ui.get("mu", dict(value=0.15, prov="assumed")),
            rz=ui.get("rz", dict(value=RZ_DEFAULT, prov="assumed")),
            F_amp_N=ui.get("F_amp_N", dict(
                value=F_AMP_RATIO * case.initial_preload_N,
                prov="literature (Pai&Hess 2002: 0.38-0.49 medido)")))
    src = SOURCE_INPUTS.get(case.source.name,
                            dict(grip=None, mu=(0.15, "assumed"), rz=RZ_DEFAULT))
    stem = Path(getattr(case, "reference_csv_path", "") or "").stem
    g = src["grip"]
    if g is None:
        grip = dict(value=2.5 * _d_mm(case), prov="assumed")
    elif isinstance(g[0], float):
        grip = dict(value=g[0], prov=g[1])
    elif g[0] == "bolt":
        key = "M8" if case.bolt_size.startswith("M8") else "M12"
        grip = dict(value=BAUER_GRIPS[key], prov="paper")
    elif g[0] == "boltd":                 # PR-33: grip = diametro do parafuso
        grip = dict(value=_d_mm(case), prov=g[1])
    else:  # "csv": grip codificado no nome do arquivo
        table = ROUSSEAU_GRIPS if "rousseau" in stem else ICMEZ_GRIPS
        key = next((k for k in table if k in stem), None)
        grip = (dict(value=table[key], prov="paper") if key
                else dict(value=2.5 * _d_mm(case), prov="assumed"))
    # F_amp por caso, lido do STEM quando a fonte declara F_amp=("csv", prov)
    # — mesmo idioma do grip "csv". Padrao `_axNkN`/`_axNpNkN` (ax2kN -> 2000;
    # ax11p2kN -> 11200). Sem match (ex. fig2_typical, condicao nao fixada na
    # nota) => fallback universal com a proveniencia honesta que ja tinha.
    f_amp = dict(value=F_AMP_RATIO * case.initial_preload_N,
                 prov="literature (Pai&Hess 2002: 0.38-0.49 medido)")
    fa = src.get("F_amp")
    if fa is not None and fa[0] == "csv":
        m = re.search(r"_ax(\d+(?:p\d+)?)kN", stem)
        if m:
            f_amp = dict(value=float(m.group(1).replace("p", ".")) * 1000.0,
                         prov=fa[1])
    out = dict(
        grip_mm=grip,
        mu=dict(value=src["mu"][0], prov=src["mu"][1]),
        rz=dict(value=src["rz"], prov="assumed"),
        F_amp_N=f_amp)
    if "E" in src:                                # modulo de Young por fonte (paper)
        out["E"] = dict(value=src["E"][0], prov=src["E"][1])
    return out
