# -*- coding: utf-8 -*-
"""Base de conhecimento do BAS V2 — o aprendizado das campanhas ACESSIVEL AO
SOFTWARE (pedido do professor 2026-07-08: "devemos salvar e ter isso tudo
implementado no software").

Fontes (versionadas no repo, escritas pelas campanhas):
- New_Theory/adopted_configs.json  — configs por fonte + priors de ancoras
- New_Theory/anchors_verdicts.json — 164 veredictos de proveniencia
- New_Theory/paper_study_ledger.md — licoes L# (parseadas do markdown)

API p/ GUI/solver:
- adopted_sources() / adopted_config(source)  — presets validados por rig
- anchor_priors() / check_input(name, value)  — bandas medidas + guarda
- lessons()                                    — licoes L# (texto)
- suggest_overrides(source)                    — dict pronto p/ _v2_tuner_overrides
  (filtrado a campos de engine via coerce_v2_overrides no solver_worker)
- sensitivity(fam) / frozen_params() / dof_summary()  — estudo §4.42 (tornado
  OAT, congelados por decisao, contagem honesta de DOF) acessivel ao software
- emb_from_curve / floor_from_curve            — leitores de proveniencia (L24)
  re-exportados de calibration.provenance ("ler em vez de fitar", §4.42d)
- wear_spec_anchor/mu_thread_anchor/creep_class/removal_energy_bound/kj_law —
  ancoras de proveniencia Rodada 5 (New_Theory/r5_anchors.json, §D1-D6 do
  plano L1-L7)
"""
from __future__ import annotations

import io
import json
import re
import time
from pathlib import Path
from typing import Dict, List, Optional

_ROOT = Path(__file__).resolve().parents[3]
if not (_ROOT / "New_Theory").exists():          # layout sem src/ intermediario
    _ROOT = Path(__file__).resolve().parents[2]
_NT = _ROOT / "New_Theory"

# campos de harness que NAO sao campos de JointMaterial (traduzidos ou ignorados
# pelo suggest_overrides; documentados nos configs)
_NON_ENGINE = {"emb_um", "GA_member", "F_eff", "emb", "mu", "c_D_dry", "c_D_oil",
               "c_D_per_lube", "k_creep", "floor",
               # F1 (2026-07-21): geometria adotada — consumida pelo runner
               # via cfg cru (_apply_adopted_geometry), nao e' campo de
               # JointMaterial
               "d_hole_mm", "d_washer_mm"}
_TRANSLATE = {"emb_um": ("emb_depth", 1e-6), "k_creep": ("k_creep_scale", 1.0),
              "floor": ("loose_arrest_floor", 1.0)}


def _load_json(name: str) -> dict:
    p = _NT / name
    # Sandbox p/ campanhas PARALELAS (2026-07-15): BAS_ADOPTED_CONFIGS aponta
    # uma COPIA de adopted_configs.json — cada processo de fit escreve na sua,
    # sem colisao; a adocao real (arquivo canonico) segue single-writer.
    if name == "adopted_configs.json":
        import os
        alt = os.environ.get("BAS_ADOPTED_CONFIGS")
        if alt:
            p = Path(alt)
    if not p.exists():
        return {}
    # retry-guard de LEITURA: o OneDrive segura lock transiente durante o
    # sync (o guard de escrita ja existia nos scripts de campanha; um
    # PermissionError de leitura derrubou o PR-31 em 2026-07-15)
    for _ in range(80):
        try:
            return json.loads(io.open(p, encoding="utf-8").read())
        except PermissionError:
            time.sleep(0.05)
    return json.loads(io.open(p, encoding="utf-8").read())


def adopted_sources() -> List[str]:
    return sorted(_load_json("adopted_configs.json").get("sources", {}))


def adopted_config(source: str) -> Optional[dict]:
    return _load_json("adopted_configs.json").get("sources", {}).get(source)


def anchor_priors() -> dict:
    return _load_json("adopted_configs.json").get("priors_ancoras", {})


def anchor_verdicts() -> dict:
    return _load_json("anchors_verdicts.json")


def check_input(name: str, value: float) -> Optional[str]:
    """Guarda de proveniencia: None se dentro da banda medida (ou sem ancora);
    senao mensagem citando a fonte. Espelha parameter_registry (unica logica).

    Aceita o nome do CAMPO do engine (`mu_bearing`) e o nome do PRIOR
    (`mu_dry`) — ate 2026-07-28 so o primeiro funcionava, e passar o segundo
    devolvia None em silencio. Como `None` continua ambiguo por contrato ("dentro
    da banda" OU "nao sei checar"), use `checkable_inputs()` para saber se a
    guarda de fato rodou."""
    from .parameter_registry import check_input_provenance
    return check_input_provenance(name, value)


def checkable_inputs() -> set:
    """Nomes que `check_input` sabe checar de fato (desambigua o None)."""
    from .parameter_registry import checkable_inputs as _ci
    return _ci()


def inert_levers(overrides: dict, defaults: Optional[dict] = None) -> dict:
    """Campos do config que NAO PODEM agir (gate por modo), com o motivo.

    Dict vazio = nenhuma inercia ESTATICA — NAO significa "todas vao agir". Para a
    inercia que depende do caso (alavanca que gateia um canal sem perda), ver
    `channel_gated_levers()` + a decomposicao do store."""
    from .parameter_registry import inert_levers as _il
    return _il(overrides, defaults=defaults)


def channel_gated_levers() -> dict:
    """Alavancas cuja inercia depende do CASO: {campo: canal que ela gateia}.

    Confira contra a decomposicao, nao contra o config. *Antes de girar um lever,
    olhar a decomposicao* (licao do Lu2024: 20x no wear nao moveu nada porque o
    wear era 1% da perda)."""
    from .parameter_registry import channel_gated_levers as _cg
    return _cg()


def lessons() -> Dict[str, str]:
    """Licoes L# do ledger do paper-study (parseadas do markdown)."""
    p = _NT / "paper_study_ledger.md"
    if not p.exists():
        return {}
    txt = io.open(p, encoding="utf-8").read()
    out: Dict[str, str] = {}
    for m in re.finditer(r"- \*\*(L\d+[a-z]?) \(([^)]*)\)\*\*:\s*(.+?)(?=\n- \*\*L|\n\n|\Z)",
                         txt, re.S):
        out[m.group(1)] = f"({m.group(2)}) " + " ".join(m.group(3).split())
    return out


# --- estudo de sensibilidade §4.42 (campanha ESCREVE o JSON; software LE) ---

def sensitivity(fam: Optional[str] = None) -> Dict[str, dict]:
    """Ranking OAT do estudo §4.42: {param: {"mean": S_medio, "max": S_max,
    "n": casos}} — S = deslocamento medio da predicao [F/F0] por ±20%.
    `fam` filtra por familia ('transverse' | 'axial'); None agrega as duas.
    {} se o estudo nao existir (API continua funcional)."""
    res = _load_json("sensitivity_study.json")
    if not isinstance(res, list):
        return {}
    agg: Dict[str, list] = {}
    for case in res:
        if fam and case.get("fam") != fam:
            continue
        for p, s in case.get("params", {}).items():
            if s.get("mean") is not None:
                agg.setdefault(p, []).append(float(s["mean"]))
    return {p: {"mean": sum(v) / len(v), "max": max(v), "n": len(v)}
            for p, v in agg.items()}


def frozen_params() -> Dict[str, str]:
    """Parametros CONGELADOS por decisao (§4.42c, S≈0 no tornado): {nome:
    razao}. Espelha parameter_registry.FROZEN_S_ZERO (fonte unica)."""
    from .parameter_registry import FROZEN_S_ZERO
    return dict(FROZEN_S_ZERO)


def dof_summary() -> dict:
    """Contagem honesta de graus de liberdade (§4.42): campos por classe +
    os DOF livres por bancada nova. Numeros derivados do engine + registry
    (nao hard-coded onde ha fonte viva)."""
    import dataclasses
    from bolt_analysis_studio.numerical.dynamic_stiffness_analyzer import JointMaterial
    n_fields = len(dataclasses.fields(JointMaterial))
    return dict(
        total_campos=n_fields,
        tuners_congelados=9,          # k_*_scale/Phi_* ≡1.0 (Estagio B remove)
        congelados_s_zero=len(frozen_params()),
        livres_por_rig=dict(
            transversal=["c_bend", "loose_arrest_floor (lido do fim)"],
            # L1 (plano L1-L7 task-4, gate B1 re-executado 2026-07-17): o
            # canal de flanco ~A_F (flank_wear_on/k_wear_flank/
            # flank_amp_exp, +3 campos da Task 3) foi CALIBRADO per-rig e o
            # gate prereg FALHOU 2x (slope Liu2017 -2.8e-6/N vs banda
            # [-4.4e-5,-1.1e-5]/N; forma flanco-elastico x Archard ~8x rasa
            # demais) => FALSIFICACAO DOCUMENTADA, capacidade validada NAO
            # adotada. Os 3 campos ficam DEFAULT-INERTES (flank_wear_on=0)
            # na config canonica => contribuem ZERO DOF por rig axial.
            # Registro completo: New_Theory/l1_axial_gate_result.json
            # (bloco "verdict").
            axial=[],                 # emb lido da queda-inicial (L24); L1 nao adotado (gate FAIL)
        ),
        # A contagem vem do MESMO n_fields que `total_campos` — era digitada a
        # mao ("94 campos") e envelheceu: em 2026-07-28 o dict contradizia a si
        # mesmo, total_campos=98 ao lado de uma nota dizendo 94. Mesma doenca que
        # a regra do fingerprint (§4.43) pega no roadmap, dentro de um dict.
        nota=f"{n_fields} campos != DOF: ~45 capabilities default-inertes "
             "(0 DOF), incl. o canal L1 de flanco (gate B1 FAIL 2026-07-17, "
             "nao adotado) e o arrest_approach_exp (gate grupo A FAIL 2026-07-27); "
             "constantes compartilhadas fitadas 1x (Estagio A); ver "
             "validation_html/sensitivity.html e MODEL_LEGITIMACY §4.42.")


# --- leitores de proveniencia (L24 / §4.42d): "ler em vez de fitar" ---------
from .provenance import (  # noqa: E402
    emb_depth_from_curve as emb_from_curve,
    emb_depth_from_early_drop as emb_from_early_drop,
    arrest_floor_from_curve as floor_from_curve,
)


# --- ancoras de proveniencia Rodada 5 (§D1-D6 do plano L1-L7) --------------

def _r5() -> dict:
    return _load_json("r5_anchors.json")


def wear_spec_anchor(interface: str, pair: str) -> dict:
    """Ancora de k_wear_spec (=K/H) por interface tribologica: {"value","band",
    "unit","source","provenance"}. `interface` ex. "thread"/"faying"/"fretting";
    `pair` ex. "35CrMo-SCM435". KeyError alto p/ par desconhecido (por design)."""
    return dict(_r5()["wear_spec"][f"{interface}|{pair}"])


def mu_thread_anchor(coating: str) -> dict:
    """Ancora de mu_thread por revestimento (ex. "zinc"/"DLC"): {"value",
    "source","provenance"}. KeyError alto p/ revestimento desconhecido."""
    return dict(_r5()["mu_thread"][coating])


def creep_class(pair_class: str) -> dict:
    """Classe de creep (par tribologico + revestimento) com o modelo
    alpha+beta*log10(t_h) e as linhas medidas por espessura: {"model","rows",
    "source","provenance"}. KeyError alto p/ classe desconhecida."""
    return dict(_r5()["creep_class"][pair_class])


def removal_energy_bound() -> dict:
    """Banda [lo,hi] (J/mm^3) de energia especifica de remocao p/ o bound L7
    (wear-removal energetics): {"lo","hi","unit","source","provenance"}."""
    return dict(_r5()["removal_energy_bound"])


def kj_law(name: str) -> dict:
    """Lei de rigidez de membro k_j(geometria) por nome ("pedersen2008" |
    "wileman1991"): {"eq","source","rank"[,"AB" tabela por-material, so
    wileman1991]}. Consumida por calibration.library_common.kj_from_geometry
    (L2, plano L1-L7 task-5) -- fonte unica, sem duplicacao de valor.
    KeyError alto p/ nome desconhecido."""
    return dict(_r5()["kj_laws"][name])


def suggest_overrides(source: str) -> dict:
    """Config adotada da fonte como dict de overrides de engine (numericos/str/
    bool); campos de harness sao traduzidos quando ha mapeamento direto e
    descartados quando dependem de calculo por-caso (GA/F_eff/mu-Motosh)."""
    cfg = (adopted_config(source) or {}).get("cfg", {})
    out = {}
    for k, v in cfg.items():
        if k in _TRANSLATE and isinstance(v, (int, float)):
            name, scale = _TRANSLATE[k]
            out[name] = float(v) * scale
        elif k not in _NON_ENGINE and isinstance(v, (int, float, str, bool)):
            out[k] = v
    return out
