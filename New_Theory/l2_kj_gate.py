# -*- coding: utf-8 -*-
"""L1-L7 plano, Task 6 (fatia 3b): gate PRE-REGISTRADO D5 da lei L2
k_j(geometria, material) (Task 5, `kj_mode="pedersen"|"wileman"`) contra os
casos Rousseau2025 (steel + HDPE, t10/12/14) e Zhang2006 (2 casos wired:
fig3/fig16) -- os unicos da biblioteca com furo/arruela documentaveis o
suficiente para engatar a lei.

PRE-REGISTRO (verbatim, task-6-brief.md Step 1 + instrucoes do controlador,
ANTES de rodar qualquer comparacao):

    PREREG (task-6-brief.md): "com kj_mode='pedersen' (sem re-fit de mais
    nada), erro nos 6 casos Rousseau steel/HDPE e nos Zhang <= estado atual
    (com capacidades adotadas ligadas); se pior, a lei fica como proveniencia
    documentada (D5), PASS-doc" -- decidir SO depois de rodar.

    Operacionalizacao (controlador, Task 6): por caso, MAE_with_law <=
    MAE_baseline + tol (tol=0.005) => PASS; qualquer caso pior => overall
    PASS-doc (nao FAIL -- D5 e' "substituicao de proveniencia com erro <=
    igual", nao promessa de ganho de MAE, ver design doc
    2026-07-16-limitacoes-L1-L7-implementacao-design.md linha D5/Fatia 3).
    Se `kj_mode_engaged` vier False em QUALQUER run with-law, a comparacao
    para aquele caso e' VOID -- reporta BLOCKED em vez de PASS/PASS-doc
    espurio (risco de corrupcao de gate identificado na review da Task 5,
    ver docstring de `DynamicStiffnessAnalyzer.__init__`/`kj_mode_engaged`
    em dynamic_stiffness_analyzer.py e tests/test_l2_kj_law.py).

Metodo (item 3 do brief, PREFERIDO a comparar contra o ValidationStore):
re-simula AMBOS os bracos (baseline = config adotada tal como esta' hoje,
kj_mode="" default; with-law = MESMA config + kj_mode="pedersen" + d_hole/
d_washer novos) no MESMO processo, usando o runner CANONICO
(`bolt_analysis_studio.validation.runner.simulate_case`) -- a paridade de
config com o relatorio mestre e' garantida por construcao (mesma funcao,
mesmas adopted_overrides/pack/PACK, mesma frozen_constants). NENHUM arquivo
do pacote e' modificado (adopted_configs.json/joint_calibrations.json
intocados, D3 do design doc) -- a injecao de kj_mode/d_hole/d_washer e' feita
por 3 monkeypatches CIRURGICOS e escopados (restaurados apos cada chamada)
sobre nomes de modulo do proprio `runner.py`:

    1. `runner.geometry_for_case` -- wrapper que, quando "ativo", aplica
       `dataclasses.replace(geom, d_hole=.., d_washer=..)` sobre a geometria
       que a funcao ORIGINAL ja constroi (grip/A_s/E/etc. inalterados).
    2. `runner.material_kwargs_for` -- wrapper que, quando "ativo", injeta
       `kj_mode` no dict de kwargs que a funcao ORIGINAL ja monta (pack +
       cfg adotada + emb + mu inalterados).
    3. `runner.DynamicStiffnessAnalyzer` -- subclasse fina que, apos
       `__init__`, CAPTURA `self.kj_mode_engaged`/`self.mat.k_j_init` do
       analyzer real que o runner constroi -- nao muda nenhum numero, so'
       observa o sinal de engate exigido pela Task 5.

Nenhum destes 3 pontos e' o "engine" (dynamic_stiffness_analyzer.py em si) --
sao monkeypatches de modulo dentro deste script, revertidos implicitamente ao
processo terminar; o arquivo fonte do runner nunca e' editado em disco.

Confrontacao Pedersen-vs-Wileman (design doc linha 83: "registrar... no
relatorio"): roda-se tambem um braco `wileman` (mesmo d_hole/d_washer) POR
CURIOSIDADE/DOCUMENTACAO -- NAO participa do veredito PASS/PASS-doc/BLOCKED
(o pre-registro e' so' sobre `kj_mode='pedersen'`, task-6-brief.md +
instrucoes do controlador). Rank de literatura: Pedersen +24% vs medido
(Rousseau 2024), Wileman +45-59% (superestima) -- `kb.kj_law(...)["rank"]`.

CAVEATS DE ARQUITETURA (achados desta gate, importantes p/ Task 9 -- nao
"bugs" desta task, sao limitacoes JA EMBUTIDAS no wiring da Task 5 que este
gate apenas expoe por ser o primeiro consumidor real com furo/arruela):

  (a) `JointGeometry.E` e' um UNICO campo usado tanto por `k_b` (rigidez
      AXIAL DO PARAFUSO, deve ser aco -- Rousseau/Zhang usam parafuso de aco
      em TODAS as series, inclusive a serie HDPE) quanto por
      `kj_from_geometry(..., geometry.E, ...)` (rigidez do MEMBRO/junta, que
      fisicamente deveria usar o E do MEMBRO -- aco nas series 'steel', HDPE
      (~1 GPa, ~200x menor) nas series 'hdpe'). Como o engine so' tem um
      campo, nao ha' como este script (script-only, sem mudanca de engine)
      fornecer o E correto simultaneamente para as duas leis sem quebrar UMA
      delas. Escolha (preserva o parafuso, fisicamente correto, e' o
      parametro que NUNCA muda entre series): geometry.E fica no default aco
      (E_STEEL=200e9) em TODOS os 8 casos, inclusive HDPE -- ou seja,
      `kj_mode="pedersen"` roda com o modulo do ACO tambem para o MEMBRO
      HDPE. Isso significa que a lei L2, DA FORMA COMO FOI LIGADA (Task 5),
      estrutralmente NAO PODE capturar o contraste de ~100x em modulo entre
      HDPE e aco que motivou a serie Rousseau -- so' captura a dependencia em
      GRIP (L_eff 25/29/33mm) e furo/arruela (constantes entre series, mesmo
      parafuso M12x1.75). Isto e' uma limitacao real do wiring atual (exigi-
      ria um campo `E_member` separado no engine -- fora do escopo desta
      task, script-only) -- documentado aqui para o Task 9 (MODEL_LEGITIMACY
      doc) decidir se vale a pena estender.
  (b) Pelo mesmo motivo, o braco `wileman` (nao-gating) tambem usa
      `material="steel"` (default hardcoded de `kj_from_geometry` -- o
      proprio ENGINE nunca passa `material=` explicito na chamada dentro de
      `__init__`, entao nao ha' canal para selecionar HDPE/aluminio/etc. na
      tabela A/B do Wileman via kj_mode hoje).
  (c) Os 2 casos "Zhang2006 clamped-length" wired na suite (fig3/fig16) NAO
      SAO uma varredura de comprimento-de-aperto -- ambos usam o "rig do
      estudo anterior" (Jiang 2003/2004, M12x1.25), NAO a propria matriz
      L=48/54/58/68mm do paper Zhang2006 (apparatus_notes/zhang2006.md,
      secao "Mismatch com extracted_csv": as 9 curvas antigas de
      "clamped_length" l_c=12.7/25.4/38.1/50.8mm sao SINTETICAS/nao-
      rastreaveis ao PDF e ja' foram removidas da galeria canonica, frota
      2026-07-15, validation_cases.py:1162-1164). O rotulo "clamped-length"
      do brief e' historico (herdado do nome da fonte ZHANG_2006); os 2
      casos REALMENTE wired nao variam grip entre si (grip assumido
      identico, 2.5d=30mm, `SOURCE_INPUTS` nao tem entrada 'ZHANG_2006' =>
      cai no default). Furo/arruela para o rig realmente usado por eles
      tambem nao consta na nota (a nota so' da' 12.7mm para o rig PROPRIO da
      Zhang2006, que NAO e' o rig usado por fig3/fig16) -- daí' o default ISO
      (nao o 12.7mm do rig errado), conforme instrucao do controlador.
  (d) "Sem regressao global": kj_mode fica "" (off, bit-identico) em
      QUALQUER outro caso da biblioteca -- nenhum adopted_config alem dos 3
      lidos aqui (ROUSSEAU_2025, ROUSSEAU_HDPE, ZHANG_2006) sequer conhece o
      campo, e este script NAO escreve em adopted_configs.json (D3 do design
      doc) -- o risco de regressao global e' estruturalmente nulo, nao
      precisa de re-simulacao dos 128 casos para confirmar.

Run: python New_Theory/l2_kj_gate.py
Runtime esperado: segundos (6 casos Rousseau com 180-400 ciclos + 2 Zhang
com ~2-4.7e4 ciclos, x3 bracos (baseline/pedersen/wileman) -- tudo
transversal/displacement-mode, ordens de grandeza abaixo do teto axial de
1e6 do gate B1). Foreground, conforme item 6 do brief.
"""
from __future__ import annotations

import dataclasses
import datetime
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bolt_analysis_studio.calibration import knowledge_base as kb  # noqa: E402
from bolt_analysis_studio.numerical.dynamic_stiffness_analyzer import (  # noqa: E402
    DynamicStiffnessAnalyzer as _RealDSA,
)
from bolt_analysis_studio.validation import case_registry  # noqa: E402
from bolt_analysis_studio.validation import runner as vrunner  # noqa: E402

# ---------------------------------------------------------------------------
PREREG = {
    "gate": "D5-L2-kj-law-rousseau-zhang",
    "source_of_truth": ".superpowers/sdd/task-6-brief.md (Step 1) + "
                       "docs/superpowers/specs/"
                       "2026-07-16-limitacoes-L1-L7-implementacao-design.md "
                       "(linha D5 / Fatia 3) + instrucoes do controlador Task 6",
    "prereg_verbatim_brief": "com kj_mode='pedersen' (sem re-fit de mais "
        "nada), erro nos 6 casos Rousseau steel/HDPE e nos Zhang <= estado "
        "atual (com capacidades adotadas ligadas); se pior, a lei fica como "
        "proveniencia documentada (D5), PASS-doc",
    "prereg_verbatim_design_doc_D5": "Gate L2 = substituicao de proveniencia "
        "com erro <= igual (nao promessa de ganho de MAE) -- o erro Rousseau "
        "ja foi fechado pela capacidade Cattaneo-Mindlin (2026-07-07, "
        "opt-in); a lei fisica k_j(geom) da' a mesma resposta COM "
        "proveniencia -- se der pior, a lei fica documentada e o CM "
        "permanece",
    "operational_pass_rule": "por caso: MAE_with_law(kj_mode=pedersen) <= "
        "MAE_baseline(kj_mode='', estado atual) + tol",
    "tol": 0.005,
    "operational_blocked_rule": "kj_mode_engaged is not True em QUALQUER run "
        "with-law (ou ok=False em qualquer braco) => aquele caso e' BLOCKED "
        "(comparacao VOID), nunca PASS/PASS-doc espurio",
    "overall_verdict_rule": "algum caso BLOCKED => overall=BLOCKED; senao, "
        "TODOS os casos PASS => overall=PASS; senao => overall=PASS-doc "
        "(lei fica como proveniencia documentada, comportamento default "
        "recomendado permanece o atual)",
    "gating_metric": "MAE apenas (maxerr/resid_std reportados como 'tripe' "
        "de diagnostico, NAO gateiam)",
    "n_cases_prereg": 8,
    "case_ids_prereg": [
        "rousseau2025_steel_t10", "rousseau2025_steel_t12",
        "rousseau2025_steel_t14", "rousseau2025_hdpe_t10",
        "rousseau2025_hdpe_t12", "rousseau2025_hdpe_t14",
        "zhang2006_fig3_illus_M12x125_20kN_amp0p35",
        "zhang2006_fig16_runout_40kN_amp0p125"],
    "non_gating_side_arm": "wileman (mesmo d_hole/d_washer, kj_mode="
        "'wileman') -- so' documentacao do confronto Pedersen-vs-Wileman "
        "pedido pelo design doc, nao entra no veredito",
    "adopted_configs_touched": False,           # D3: intocados
    "joint_calibrations_touched": False,        # D3: intocado
}

# --- Geometria (furo/arruela) por fonte, com proveniencia (ver caveat (c)) --
GEOMETRY_HW = {
    "ROUSSEAU_2025": dict(
        d_hole_mm=13.6, d_washer_mm=24.0,
        d_hole_prov="paper (Rousseau & Bouzid 2025, apparatus_notes/"
                    "rousseau2025_materials_M12.md: 'hole diameter 13.6 mm "
                    "(1.6 mm clearance)' -- M12 bolt, d=12mm + 1.6mm "
                    "clearance = 13.6mm)",
        d_washer_prov="iso (ISO 7089 M12 washer OD=24mm -- a nota so' da' a "
                      "ESPESSURA da arruela, '2.4 mm each', nao o diametro "
                      "externo; 24mm e' o OD normal-series ISO 7089 p/ M12, "
                      "familia coerente com a espessura 2.4mm ~ 2.5mm "
                      "nominal da norma)"),
    "ZHANG_2006": dict(
        d_hole_mm=13.5, d_washer_mm=24.0,
        d_hole_prov="assumed (ISO 273 M12 furo de folga, ajuste MEDIO "
                    "13.5mm -- ver caveat (c): a nota SO' da' 12.7mm para o "
                    "rig PROPRIO do paper (L=48-68mm), que NAO e' o rig "
                    "usado pelos 2 casos wired fig3/fig16 ('rig do estudo "
                    "anterior', Jiang 2003/2004, M12x1.25); banda "
                    "controlador 13.5-14mm, 13.5 escolhido por proximidade "
                    "ao valor real medido do irmao Rousseau M12 (13.6mm, "
                    "mesmo diametro nominal))",
        d_washer_prov="iso (ISO 7089 M12 washer OD=24mm; nao declarado para "
                      "nenhum dos dois rigs do paper)"),
}

TOL = 0.005


# ---------------------------------------------------------------------------
# Monkeypatches cirurgicos sobre `runner.py` (ver docstring do modulo) --
# escopados via flags "ativo" setadas/limpas em `_simulate_arm` a cada
# chamada; a funcao ORIGINAL de cada ponto e' sempre chamada primeiro (o
# comportamento canonico nunca e' pulado, so' aumentado).
# ---------------------------------------------------------------------------
_ORIG_GEOM_FOR_CASE = vrunner.geometry_for_case
_ORIG_MATERIAL_KWARGS_FOR = vrunner.material_kwargs_for

_HW_ACTIVE = {"d_hole": 0.0, "d_washer": 0.0}
_KJ_ACTIVE = {"mode": None}
_CAPTURE = {"engaged": None, "k_j_init": None, "L_eff_mm": None,
           "d_nominal_mm": None, "E_used": None, "n_dsa_calls": 0,
           "Phi_eff_0": None, "U_internal_0": None}


def _patched_geometry_for_case(case, grip_mm, E=None):
    geom = _ORIG_GEOM_FOR_CASE(case, grip_mm=grip_mm, E=E)
    if _HW_ACTIVE["d_hole"] > 0.0 and _HW_ACTIVE["d_washer"] > 0.0:
        geom = dataclasses.replace(geom, d_hole=_HW_ACTIVE["d_hole"],
                                   d_washer=_HW_ACTIVE["d_washer"])
    return geom


def _patched_material_kwargs_for(rec, inp):
    kw = _ORIG_MATERIAL_KWARGS_FOR(rec, inp)
    if _KJ_ACTIVE["mode"]:
        kw["kj_mode"] = _KJ_ACTIVE["mode"]
    return kw


class _CapturingDSA(_RealDSA):
    """Subclasse fina: delega 100% ao engine real, so' OBSERVA
    kj_mode_engaged/k_j_init/geometria apos __init__ (nenhum numero da
    simulacao muda -- e' a mesma classe, so' com um side-effect de leitura)."""

    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        _CAPTURE["engaged"] = self.kj_mode_engaged
        _CAPTURE["k_j_init"] = self.mat.k_j_init
        _CAPTURE["L_eff_mm"] = self.geom.L_eff * 1e3
        _CAPTURE["d_nominal_mm"] = self.geom.d_nominal * 1e3
        _CAPTURE["E_used"] = self.geom.E
        _CAPTURE["n_dsa_calls"] += 1
        # Diagnostico (nao gating): prova DIRETA de que k_j_init realmente
        # mudou o estado interno do analyzer (Phi_eff/U_internal, os dois
        # unicos consumidores de k_j_ax no ciclo-0) mesmo quando a
        # TRAJETORIA (ratio/MAE) fica bit-identica -- ver "mechanism_note"
        # no JSON final para a explicacao completa (theta_load=pi/2 exato
        # em todo caso 'transverse' zera a contribuicao axial de
        # RotationalLooseningLoss em precisao double, np.hypot(L_ax~1e-15,
        # L_tr~1e1-1e4) == L_tr bit-a-bit).
        _CAPTURE["Phi_eff_0"] = self.Phi_eff()
        _CAPTURE["U_internal_0"] = self.U_internal()


vrunner.geometry_for_case = _patched_geometry_for_case
vrunner.material_kwargs_for = _patched_material_kwargs_for
vrunner.DynamicStiffnessAnalyzer = _CapturingDSA


def _simulate_arm(rec, kj_mode, d_hole_mm: float, d_washer_mm: float, now: str):
    """Roda `simulate_case` (runner canonico) com os 3 patches acima
    ATIVADOS so' durante esta chamada (flags limpas no finally -- nenhum
    estado vaza entre casos/bracos)."""
    _CAPTURE["engaged"] = None
    _CAPTURE["k_j_init"] = None
    _CAPTURE["n_dsa_calls"] = 0
    _CAPTURE["Phi_eff_0"] = None
    _CAPTURE["U_internal_0"] = None
    _KJ_ACTIVE["mode"] = kj_mode
    _HW_ACTIVE["d_hole"] = d_hole_mm * 1e-3
    _HW_ACTIVE["d_washer"] = d_washer_mm * 1e-3
    try:
        res = vrunner.simulate_case(rec, now=now)
    finally:
        _KJ_ACTIVE["mode"] = None
        _HW_ACTIVE["d_hole"] = 0.0
        _HW_ACTIVE["d_washer"] = 0.0
    return res, dict(_CAPTURE)


def _tripe(res) -> dict:
    return dict(ok=res.ok, error=res.error, mae=res.mae, maxerr=res.maxerr,
               maxerr_at=res.maxerr_at, resid_std=res.resid_std,
               final_pred=res.final_pred, final_data=res.final_data,
               D_final=res.D_final)


# ---------------------------------------------------------------------------
def run_case(case_id: str, now: str, log=print) -> dict:
    rec = case_registry.record(case_id)
    if rec is None:
        return dict(case_id=case_id, blocked=True, verdict="BLOCKED",
                   error=f"case_id nao encontrado no registry: {case_id}")
    hw = GEOMETRY_HW.get(rec.source)
    if hw is None:
        return dict(case_id=case_id, blocked=True, verdict="BLOCKED",
                   error=f"sem geometria furo/arruela cadastrada p/ fonte "
                         f"{rec.source!r}")

    # braco baseline: estado atual (config adotada tal como esta', kj_mode
    # default "" -- nenhum override deste script).
    res_base, cap_base = _simulate_arm(rec, kj_mode=None, d_hole_mm=0.0,
                                       d_washer_mm=0.0, now=now)
    # braco with-law (GATING): mesma config + kj_mode='pedersen' + furo/arruela.
    res_law, cap_law = _simulate_arm(rec, kj_mode="pedersen",
                                     d_hole_mm=hw["d_hole_mm"],
                                     d_washer_mm=hw["d_washer_mm"], now=now)
    # braco wileman (NAO-GATING, so' documentacao do confronto -- design doc).
    res_wil, cap_wil = _simulate_arm(rec, kj_mode="wileman",
                                     d_hole_mm=hw["d_hole_mm"],
                                     d_washer_mm=hw["d_washer_mm"], now=now)

    engaged_law = cap_law["engaged"]
    blocked = (not res_base.ok or not res_law.ok
               or engaged_law is not True
               or res_base.mae is None or res_law.mae is None)
    delta_mae = (None if blocked else res_law.mae - res_base.mae)
    case_pass = (not blocked) and (delta_mae <= TOL)
    verdict = "BLOCKED" if blocked else ("PASS" if case_pass else "WORSE")

    delta_phi = (None if cap_base["Phi_eff_0"] is None or cap_law["Phi_eff_0"] is None
                else cap_law["Phi_eff_0"] - cap_base["Phi_eff_0"])

    log(f"[{case_id}] baseline MAE={res_base.mae} (kj_engaged="
        f"{cap_base['engaged']}, Phi_eff_0={cap_base['Phi_eff_0']:.4f})  "
        f"pedersen MAE={res_law.mae} (kj_engaged={engaged_law}, "
        f"k_j={cap_law['k_j_init']:.4g} N/m @ L_eff={cap_law['L_eff_mm']:.1f}mm, "
        f"Phi_eff_0={cap_law['Phi_eff_0']:.4f})  wileman MAE={res_wil.mae} "
        f"(k_j={cap_wil['k_j_init']:.4g} N/m)  delta_MAE={delta_mae}  "
        f"delta_Phi_eff_0={delta_phi}  -> {verdict}")

    return dict(
        case_id=case_id, source=rec.source, name=rec.name,
        bolt_size=rec.validation_case.bolt_size,
        F0_N=rec.validation_case.initial_preload_N,
        amp_mm=rec.validation_case.transverse_displacement_mm,
        freq_Hz=rec.validation_case.frequency_Hz,
        n_cycles=rec.validation_case.n_cycles,
        geometry_hw_mm=dict(d_hole_mm=hw["d_hole_mm"],
                            d_hole_prov=hw["d_hole_prov"],
                            d_washer_mm=hw["d_washer_mm"],
                            d_washer_prov=hw["d_washer_prov"]),
        baseline=dict(kj_mode="", kj_mode_engaged=bool(cap_base["engaged"]),
                     k_j_init_N_per_m=cap_base["k_j_init"],
                     Phi_eff_0=cap_base["Phi_eff_0"],
                     U_internal_0_J=cap_base["U_internal_0"], **_tripe(res_base)),
        with_law_pedersen=dict(kj_mode="pedersen", kj_mode_engaged=engaged_law,
                              k_j_init_N_per_m=cap_law["k_j_init"],
                              L_eff_mm=cap_law["L_eff_mm"],
                              d_nominal_mm=cap_law["d_nominal_mm"],
                              E_used_Pa=cap_law["E_used"],
                              Phi_eff_0=cap_law["Phi_eff_0"],
                              U_internal_0_J=cap_law["U_internal_0"], **_tripe(res_law)),
        side_arm_wileman=dict(kj_mode="wileman",
                             kj_mode_engaged=cap_wil["engaged"],
                             k_j_init_N_per_m=cap_wil["k_j_init"],
                             Phi_eff_0=cap_wil["Phi_eff_0"],
                             U_internal_0_J=cap_wil["U_internal_0"],
                             gating=False, **_tripe(res_wil)),
        delta_mae_pedersen_minus_baseline=delta_mae, tol=TOL,
        delta_Phi_eff_0_pedersen_minus_baseline=delta_phi,
        blocked=blocked, verdict=verdict,
    )


def main() -> int:
    t_start = time.time()
    now = datetime.datetime.now().isoformat(timespec="seconds")

    def log(msg):
        print(msg, flush=True)

    log("PREREG: " + json.dumps(PREREG, ensure_ascii=False, indent=2))

    # sanity: confirma que a suite tem EXATAMENTE os 8 casos esperados nas
    # 2 fontes-alvo (nenhum caso a mais/a menos silenciosamente incluido).
    all_recs = case_registry.all_records()
    found = sorted(r.case_id for r in all_recs
                   if r.source in ("ROUSSEAU_2025", "ZHANG_2006"))
    expected = sorted(PREREG["case_ids_prereg"])
    registry_sanity = dict(found=found, expected=expected, match=found == expected)
    log(f"registry sanity (ROUSSEAU_2025+ZHANG_2006 == 8 casos prereg): "
        f"{registry_sanity['match']}")
    if not registry_sanity["match"]:
        log("AVISO: conjunto de casos no registry difere do pre-registrado "
            "-- rodando MESMO ASSIM os case_ids do PREREG (nao os achados), "
            "verdict fica BLOCKED por caso ausente se aplicavel.")

    cases = [run_case(cid, now, log=log) for cid in PREREG["case_ids_prereg"]]

    n_pass = sum(1 for c in cases if c["verdict"] == "PASS")
    n_worse = sum(1 for c in cases if c["verdict"] == "WORSE")
    n_blocked = sum(1 for c in cases if c["verdict"] == "BLOCKED")
    blocked_ids = [c["case_id"] for c in cases if c["verdict"] == "BLOCKED"]
    worse_ids = [c["case_id"] for c in cases if c["verdict"] == "WORSE"]

    if n_blocked > 0:
        overall = "BLOCKED"
    elif n_worse == 0:
        overall = "PASS"
    else:
        overall = "PASS-doc"

    all_delta_zero = all(c.get("delta_mae_pedersen_minus_baseline") == 0.0
                         for c in cases if not c.get("blocked"))
    phi_deltas = [abs(c["delta_Phi_eff_0_pedersen_minus_baseline"]) for c in cases
                 if c.get("delta_Phi_eff_0_pedersen_minus_baseline") is not None]
    mean_abs_delta_phi = (sum(phi_deltas) / len(phi_deltas)) if phi_deltas else None

    log(f"\n{'=' * 70}\nFINAL: overall={overall}  n_pass={n_pass} "
        f"n_worse={n_worse} n_blocked={n_blocked}\n"
        f"worse_cases={worse_ids}  blocked_cases={blocked_ids}\n"
        f"all_delta_mae_exactly_zero={all_delta_zero}  "
        f"mean_abs_delta_Phi_eff_0={mean_abs_delta_phi}\n{'=' * 70}")

    out = dict(
        prereg=PREREG,
        geometry_provenance=GEOMETRY_HW,
        caveats=dict(
            E_conflation="JointGeometry.E e' um unico campo usado por k_b "
                "(parafuso) E por kj_from_geometry (deveria ser o E do "
                "MEMBRO) -- fica no default aco (200 GPa) em TODOS os 8 "
                "casos, inclusive HDPE (ver docstring do modulo, caveat a). "
                "kj_mode='pedersen', da forma como foi ligado na Task 5, "
                "NAO PODE capturar o contraste HDPE-vs-aco (~100x em E) que "
                "motivou a serie Rousseau -- so' captura a dependencia em "
                "grip (L_eff) e furo/arruela.",
            wileman_material_hardcode="O braco wileman (nao-gating) usa "
                "material='steel' hardcoded (o engine nunca passa "
                "material= explicito em kj_from_geometry) -- mesma limitacao "
                "do item acima, side-arm apenas documental.",
            zhang_clamped_length_mislabel="Os 2 casos Zhang2006 wired "
                "(fig3/fig16) NAO variam clamped-length entre si -- ambos "
                "usam o 'rig do estudo anterior' (Jiang 2003/2004, "
                "M12x1.25), nao a matriz L=48-68mm do proprio paper "
                "Zhang2006 (apparatus_notes/zhang2006.md, secao Mismatch). "
                "O rotulo 'clamped-length' no brief e' historico (nome da "
                "fonte ZHANG_2006); grip usado e' 'assumed' 2.5d=30mm p/ "
                "ambos (SOURCE_INPUTS sem entrada ZHANG_2006 -> default).",
            no_global_regression_risk="kj_mode fica '' (off, bit-identico) "
                "em todo o resto da biblioteca -- nenhum outro adopted_config "
                "referencia o campo e este script nao escreve em "
                "adopted_configs.json/joint_calibrations.json (D3); risco de "
                "regressao global estruturalmente nulo, nao exigiu "
                "re-simulacao dos 128 casos.",
        ),
        pedersen_vs_wileman_literature_rank=dict(
            pedersen2008=kb.kj_law("pedersen2008")["rank"],
            wileman1991=kb.kj_law("wileman1991")["rank"]),
        mechanism_note=(
            "Achado (verificado, nao e' bug do script): delta_mae = 0.0 "
            "EXATO (nao so' 'pequeno') em TODOS os 8 casos, apesar de "
            "k_j_init mudar de fato (4e9 N/m fixo -> 2.90-3.35e9 N/m via "
            "Pedersen, variando com L_eff -- ver baseline.k_j_init_N_per_m "
            "vs with_law_pedersen.k_j_init_N_per_m por caso) e de Phi_eff_0 "
            "mudar de fato (delta_Phi_eff_0 tipicamente +0.02 a +0.03, "
            "capturado no ciclo-0 de cada analyzer -- prova de que a lei "
            "ENGATOU substantivamente no estado interno). Explicacao: para "
            "TODO caso 'transverse' (Rousseau/Zhang, os 8 aqui), o runner "
            "fixa theta_load=pi/2 EXATO. Em RotationalLooseningLoss (unico "
            "mecanismo que le k_j, via Phi_eff/Phi_ax), L_ax = "
            "Phi_ax*sin(beta)*F_ax com F_ax=F_amp*cos(pi/2)=F_amp*6.12e-17 "
            "(residuo de ponto-flutuante de pi/2, nao exatamente zero); "
            "L_tr = Phi_tr_active*cos(beta)*F_tr (SEM dependencia de k_j) e' "
            "O(10^1-10^4). L_total=hypot(L_ax,L_tr): com L_ax ~15-17 ordens "
            "de grandeza menor que L_tr, (L_ax)^2 cai ABAIXO da precisao "
            "double (~2.2e-16 relativo) na soma hipot -- L_total fica "
            "BIT-IDENTICO independente de Phi_ax/k_j (verificado "
            "numericamente, nao so' por inspecao de codigo -- ver "
            "New_Theory/l2_kj_gate.py commit message/task-6-report.md). "
            "k_torsional tambem nao le k_j aqui (PACK usa "
            "loose_torsion_mode='bolt_torsion', nao 'legacy'). "
            "W_viscous_per_cycle tambem le k_j_ax mas e' multiplicado por "
            "F_ax=F_amp*cos(pi/2) -- mesmo colapso. Consequencia: k_j_init/ "
            "kj_mode e' inerte na TRAJETORIA (ratio/MAE/maxerr) destes 8 "
            "casos transversais NO PACK ADOTADO -- so' afeta "
            "U_internal/U_loaded/conservation_residual (ledger de energia "
            "elastica). CORRECAO DE ALCANCE (review 2026-07-17): a inercia "
            "e' CONDICIONAL A CONFIG, nao estrutural p/ todo transversal: "
            "(i) o underflow em theta=pi/2 mata o caminho L_ax "
            "estruturalmente; (ii) MAS a inercia total exige ADICIONALMENTE "
            "k_tr_mode != 'axial_frac' -- aqui garantido pelo PACK "
            "(k_tr_mode='bending', validation/runner.py); com o default "
            "'axial_frac' do engine, k_tr_transverse=0.3*k_j_init alimenta "
            "resolve_transverse_slip e k_j 4.0e9->3.05e9 moveria o "
            "wear-slip do Zhang-fig16 ~0.6% => delta nao-zero. A lei so' "
            "MUDA a trajetoria em casos com componente AXIAL real (theta != "
            "pi/2 ou familia 'axial') ou em configs axial_frac -- nenhum "
            "dos 8 casos-alvo desta gate e' desses tipos."),
        method="re-simulacao de AMBOS os bracos no worktree via runner "
            "canonico (bolt_analysis_studio.validation.runner.simulate_case) "
            "com 3 monkeypatches escopados (geometry_for_case injeta "
            "d_hole/d_washer; material_kwargs_for injeta kj_mode; "
            "DynamicStiffnessAnalyzer capturado p/ ler kj_mode_engaged) -- "
            "PREFERIDO a comparar contra o ValidationStore (paridade de "
            "config garantida por construcao, ver docstring do modulo).",
        registry_sanity=registry_sanity,
        engine_fingerprint=vrunner.engine_fingerprint(),
        generated_at=now,
        cases=cases,
        summary=dict(
            n_cases=len(cases), n_pass=n_pass, n_worse=n_worse,
            n_blocked=n_blocked, worse_case_ids=worse_ids,
            blocked_case_ids=blocked_ids, overall_verdict=overall,
            all_delta_mae_exactly_zero=all_delta_zero,
            mean_abs_delta_Phi_eff_0_pedersen_vs_baseline=mean_abs_delta_phi,
        ),
        runtime_total_s=time.time() - t_start,
    )

    out_path = ROOT / "New_Theory" / "l2_kj_gate_result.json"
    out_path.write_text(json.dumps(out, indent=2, ensure_ascii=False),
                        encoding="utf-8")
    log(f"JSON: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
