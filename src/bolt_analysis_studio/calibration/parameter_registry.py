"""Registro declarativo de ativacao de parametros por regime de carregamento.

Spec: docs/superpowers/specs/2026-07-03-parameter-activation-registry-design.md.
Fonte UNICA que a calibracao (v1) e, futuramente, validacao e GUI consomem:
um parametro cujo mecanismo nao e excitado pelo regime tem coluna ~0 no
Jacobiano (MODEL_LEGITIMACY §4) — estruturalmente nao-identificavel — e por
isso nao deve ser pedido ao usuario nem oferecido ao otimizador.

Os predicados sao verificados contra as equacoes reais do engine pelos testes
registry-truth em tests/test_parameter_registry.py.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import (TYPE_CHECKING, Callable, Dict, Iterable, List, Set,
                    Tuple)

import numpy as np

if TYPE_CHECKING:                                   # sem import em runtime:
    from .shared_calibrator import ConditionSpec    # evita ciclo de imports


@dataclass(frozen=True)
class LoadingRegime:
    """Dimensoes de regime que os predicados enxergam (tabela completa,
    decisao §0.1 do spec): carregamento, estado da junta, termico e
    proveniencia de F0. Consumidores adotam as dimensoes conforme seus dados."""
    has_transverse_slip: bool
    has_axial: bool
    damage_active: bool
    delta_T_nonzero: bool = False   # calibracao atual: sempre False
    F0_provenance: str = "nominal"  # nominal | estimated | torque | measured


@dataclass(frozen=True)
class ParameterRule:
    name: str            # campo de JointMaterial (ou estado nomeado)
    layer: str           # 'physical' | 'damage' | 'state' | 'friction'
    fittable: bool       # candidato do SharedCalibrator?
    active: Callable[[LoadingRegime], bool]
    rationale: str       # uma frase fisica (tooltip futuro da GUI)
    role: str = ""       # campos com 2 papeis (mu_*: 'servico' | 'aperto')


def regime_from_condition(cond: "ConditionSpec", theta: float,
                          estimated: bool) -> LoadingRegime:
    """Deriva o regime de UMA condicao de calibracao. `theta` e global na
    SharedCalibrationConfig; a variacao por condicao vem de delta_amp e
    damage_active. `estimated` = o F0 desta condicao esta em estimate_F0."""
    has_tr = (abs(np.sin(theta)) > 1e-12) or (cond.delta_amp > 0.0)
    has_ax = abs(np.cos(theta)) > 1e-12
    return LoadingRegime(
        has_transverse_slip=has_tr,
        has_axial=has_ax,
        damage_active=cond.damage_active,
        delta_T_nonzero=False,
        F0_provenance="estimated" if estimated else "nominal",
    )


def _sempre(r: LoadingRegime) -> bool:
    return True


def _transversal(r: LoadingRegime) -> bool:
    return r.has_transverse_slip


def _dano(r: LoadingRegime) -> bool:
    return r.damage_active


def _aperto_por_torque(r: LoadingRegime) -> bool:
    return r.F0_provenance == "torque"


def _axial_forca(r: LoadingRegime) -> bool:
    """Inverso de `_transversal`: dirigido por A_F (amplitude de carga axial)
    em modo FORCA pura -- so onde ha componente axial de carga E NAO ha slip
    transversal (has_transverse_slip ja engloba delta_amp>0, que nesta
    convencao do engine e' SEMPRE transversal, mesmo com theta=0). Espelho
    invertido de `_transversal` (plano L1-L7 task-3, 2026-07-16)."""
    return r.has_axial and not r.has_transverse_slip


def _pressao_elevada(r: LoadingRegime) -> bool:
    # Conformacao slip-driven so e excitada sob pressao de contato elevada
    # (over-torque). Proxy no dataset compartilhado: F0 nao-nominal (estimado
    # ou por torque) => pre-carga elevada. Este predicado e o gate de OFERTA ao
    # otimizador; o pressure-weighting no engine e o gate fino (inerte em F0
    # nominal de qualquer forma).
    return r.F0_provenance in ("estimated", "torque")


# ---------------------------------------------------------------------------
# CONGELADOS POR DECISAO (§4.42c, estudo de sensibilidade OAT 2026-07-09):
# S≈0 em TODOS os casos representativos (transversal E axial) — bypassed pelos
# modos canonicos (bolt_torsion / k_tr bending / CM kappa=1). Ficam no nominal;
# NUNCA oferecidos ao otimizador. Congelamento vale DENTRO da formulacao
# canonica (L25) — a forma nao e removida do engine.
# ---------------------------------------------------------------------------
FROZEN_S_ZERO: Dict[str, str] = {
    # ERRATA 2026-07-29: as razoes destes DOIS estavam factualmente erradas — as
    # duas diziam "nao e' lido / bypassed nos caminhos canonicos", e os dois SAO
    # lidos SEMPRE, por `k_j_ax()` (`k_j_init * ratio**alpha_GW`), chamada em 11
    # sitios SEM gate nenhum: laco principal, U_int da energia, rho=k_j_ax/k_b.
    # A varredura de sigma_res no config CANONICO ADOTADO mediu efeito NAO-NULO
    # (k_j_init: 4,5e-4 no chu2026, 3,3e-4 no liu2022, 2,3e-4 no eccles; zero nos
    # outros 7). O congelamento CONTINUA justificado — 4,5e-4 e' 1,8% do limite
    # de sigma_res — mas por MAGNITUDE, nao por ausencia. A diferenca importa: a
    # razao antiga levaria o proximo leitor a ignorar um parametro que esta no
    # caminho da rigidez, e portanto no orcamento de energia.
    # A citacao "§4.42" e' OBRIGATORIA em todo racional daqui (preso em
    # test_dof_reduction_software::test_frozen_set_is_the_tornado_verdict): ela e' o
    # elo de procedencia ao estudo tornado do MODEL_LEGITIMACY.md, e a GUI renderiza
    # este texto. Ao corrigir o CONTEUDO destes dois em 2026-07-29 eu derrubei a
    # citacao e quebrei o elo — o teste pegou. Refina-se o veredicto do §4.42; nao
    # se apaga de onde ele vem.
    "k_j_init": "S~0 no tornado §4.42, mas por MAGNITUDE e nao por ausencia: e' "
                "lido sempre via k_j_ax(); delta medido <= 4,5e-4 nas tres reguas "
                "em 10 casos canonicos (2026-07-29) = 1,8% do limite de sigma_res",
    "alpha_GW": "S~0 no tornado §4.42, por MAGNITUDE: expoente do mesmo k_j_ax() "
                "(sempre lido); delta = 0 exato nos 10 casos canonicos medidos "
                "(2026-07-29)",
    "slip_capacity_coeff": "S=0 no tornado §4.42 (kappa CM=1 canonico)",
    "partial_slip_exp": "S=0 no tornado §4.42 (gate de partial-slip inerte no "
                        "working point canonico)",
}


PARAMETER_REGISTRY: Tuple[ParameterRule, ...] = (
    # --- CONGELADOS §4.42c (fittable=False; enforcement em active_candidates) ---
    ParameterRule("k_j_init", "physical", False, _sempre, FROZEN_S_ZERO["k_j_init"]),
    ParameterRule("alpha_GW", "physical", False, _sempre, FROZEN_S_ZERO["alpha_GW"]),
    ParameterRule("slip_capacity_coeff", "physical", False, _sempre,
                  FROZEN_S_ZERO["slip_capacity_coeff"]),
    ParameterRule("partial_slip_exp", "physical", False, _sempre,
                  FROZEN_S_ZERO["partial_slip_exp"]),
    # --- fisicos sempre ativos sob carga ciclica ---
    ParameterRule("emb_depth", "physical", True, _sempre,
                  "assentamento plastico ocorre sob qualquer ciclo"),
    ParameterRule("N_emb", "physical", True, _sempre,
                  "constante de tempo do assentamento"),
    ParameterRule("C_creep", "physical", True, _sempre,
                  "fluencia e funcao do tempo sob carga; dT!=0 promove de "
                  "opcional a obrigatorio nos consumidores de validacao"),
    # --- forma saturante opt-in do creep (Alamos 2021/2022; plano L1-L7
    #     task-7, 2026-07-17). Mesmo predicado de C_creep (_sempre): e' a
    #     MESMA fisica (assentamento sob tempo/carga), so troca log-t
    #     ilimitado por saturante limitado — nao e' um regime de excitacao
    #     diferente. So identificavel quando creep_mode=="saturating" (mode
    #     switch, ver abaixo), mas o registro nao condiciona em OUTRO campo
    #     -- oferta segue o regime fisico, igual ao C_creep. creep_mode (str)
    #     NAO entra aqui -- mesmo idioma de kj_mode/conform_driver/k_tr_mode
    #     (omitidos: mode switches nunca sao fittable=True, licao da revisao
    #     da Task 2). ---
    ParameterRule("creep_t_c", "physical", True, _sempre,
                  "constante de tempo da forma saturante de creep (Alamos); "
                  "mesmo regime de C_creep — assentamento sob carga"),
    ParameterRule("creep_alpha_sat", "physical", True, _sempre,
                  "expoente de forma (stretched exponential) da saturante "
                  "de creep; mesmo regime de C_creep"),
    # --- excitados por slip transversal ---
    ParameterRule("k_wear_spec", "physical", True, _transversal,
                  "razao K/H identificavel (merge sec4.42a) — o parametro de "
                  "wear canonico; K_archard/hardness sao a via legada"),
    ParameterRule("K_archard", "physical", True, _transversal,
                  "o wear do modelo e dirigido por slip transversal "
                  "(LEGADO: so lido se k_wear_spec=0; ver merge sec4.42a)"),
    ParameterRule("tr_loose_gain", "physical", True, _transversal,
                  "fator 1 transversal do two-factor loosening"),
    # --- fisica de dano (generaliza o antigo filtro _DAMAGE_CONSTANTS) ---
    ParameterRule("c_D", "damage", True, _dano,
                  "taxa de crescimento do dano superficial"),
    ParameterRule("k_dmg_wear", "damage", True, _dano,
                  "amplificacao de wear pelo dano"),
    ParameterRule("W_ref", "damage", False, _dano,
                  "escala de energia de referencia do dano"),
    ParameterRule("k_dmg_mu", "damage", False, _dano,
                  "acoplamento dano -> perda de atrito"),
    # --- onset do dano (predictive trigger, spec 2026-07-05): so identificavel
    #     onde o dano cresce (c_D>0), i.e. sob _dano. W_crit gateia dD; sem dano
    #     dD=0 => W_crit inerte (registry-truth). O trigger substitui o disparo
    #     manual pela fisica no RUNTIME/validacao, mas a OFERTA ao fit segue o
    #     regime onde e identificavel (dano ativo). ---
    ParameterRule("W_crit", "damage", True, _dano,
                  "dose critica de fretting p/ ONSET do dano (predictive "
                  "trigger); so identificavel onde D cresce"),
    ParameterRule("dmg_onset_sharpness", "damage", False, _dano,
                  "expoente do gate de onset do dano (= slip_onset_sharpness)"),
    # --- estados nomeados ---
    ParameterRule("D_init", "state", False, _dano,
                  "estado inicial de dano (junta reusada/reapertada)"),
    ParameterRule("emb_consumed_frac", "state", False, _dano,
                  "assentamento ja consumido (junta reusada)"),
    # --- incubacao (opt-in, default 0). Nuance de equacao descoberta no
    #     design: o gate multiplica TAMBEM o loosening axial, mas W_slip_acc
    #     so acumula com slip transversal => em axial puro com slip_onset_W>0
    #     o loosening ficaria permanentemente suprimido. Predicado honesto =
    #     sempre potencialmente ativo; ver MODEL_LEGITIMACY (changelog). ---
    ParameterRule("slip_onset_W", "physical", False, _sempre,
                  "gate de incubacao Hill (alimentado por W_slip_acc); "
                  "multiplica dF_0 de wear E loosening — util com slip "
                  "transversal, mas nao-inerte em axial (ver nuance)"),
    ParameterRule("slip_onset_sharpness", "physical", False, _sempre,
                  "expoente do gate de incubacao"),
    # --- conformacao dependente de pressao (sobretorque, spec 2026-07-04) ---
    ParameterRule("W_conf_ref", "physical", True, _pressao_elevada,
                  "conformacao slip-driven excitada so sob pressao de contato "
                  "elevada (over-torque); inerte em F0 nominal"),
    ParameterRule("conform_pressure_exp", "physical", True, _pressao_elevada,
                  "expoente de pressao da conformacao"),
    ParameterRule("p_ref_conform", "physical", False, _pressao_elevada,
                  "pressao de contato de referencia (input, nao fitado)"),
    # --- atritos: dois papeis fisicos distintos ---
    ParameterRule("mu_thread", "friction", False, _transversal,
                  "servico: resistencia ao slip no filete", role="servico"),
    ParameterRule("mu_bearing", "friction", False, _transversal,
                  "servico: resistencia ao slip na flange", role="servico"),
    ParameterRule("mu_thread", "friction", False, _aperto_por_torque,
                  "aperto: conversao torque->F0", role="aperto"),
    ParameterRule("mu_bearing", "friction", False, _aperto_por_torque,
                  "aperto: conversao torque->F0", role="aperto"),
    # --- teto de Coulomb F_amp<=mu_eff(F0)*F0 em disp-mode (L3, roadmap #4,
    #     2026-07-16): mesmo regime de excitacao de tr_loose_gain/
    #     k_wear_spec (so ha teto de gross-slip a aplicar onde ha slip
    #     transversal); NUNCA oferecido no axial puro. ---
    # famp_couple_on: switch BINARIO (guard e' `> 0.0` no site de uso,
    # step_cycle -- o clamp liga por inteiro, sem escala pelo valor acima de
    # 0); gradiente-nao-fitavel (adjudicacao revisao Task-2, fix wave
    # task-5): um otimizador continuo nao tem sinal de gradiente entre
    # "ligado" e "mais ligado". Fica fittable=False; comportamento
    # (on/off, nao a magnitude) segue coberto por tests/test_l3_famp_coupling.py.
    ParameterRule("famp_couple_on", "physical", False, _transversal,
                  "liga o teto de Coulomb sobre F_amp em disp-mode (idioma "
                  "continuo 0=off identico a c_D)"),
    ParameterRule("mu_eff_lo", "physical", True, _transversal,
                  "knockdown do mu efetivo em F0->0 (proveniencia Murai/"
                  "IJAMT-2023: mu 0.46->0.24 com F0 crescente)"),
    ParameterRule("mu_eff_F0_ref", "physical", True, _transversal,
                  "F0 de referencia do knockdown (proveniencia "
                  "Measurement-2021: limiares de slip-onset proporcionais "
                  "a F0)"),
    ParameterRule("gross_ceiling_decay", "physical", True, _transversal,
                  "decaimento do teto de gross-slip com o desgaste "
                  "(proveniencia JMP-2021: F_S->F_R degrada com D)"),
    # --- canal L1 de flanco ~ A_F (plano L1-L7 task-3, 2026-07-16): forma
    #     complementar ao k_thread_fret legado, mesmo regime de excitacao
    #     invertido de tr_loose_gain/k_wear_spec (so onde ha carga axial E
    #     NAO ha slip transversal). ---
    # flank_wear_on: switch BINARIO (guard e' `> 0.0` no site de uso,
    # ThreadFrettingLoss.rate -- o canal liga por inteiro, sem escala pelo
    # valor acima de 0); mesma adjudicacao de famp_couple_on (revisao Task-2,
    # fix wave final/task-11): gradiente-nao-fitavel, um otimizador continuo
    # nao tem sinal entre "ligado" e "mais ligado". O proprio gate B1
    # (New_Theory/l1_axial_gate.py) ja fixa flank_wear_on=1.0 como config e
    # fita so {k_wear_flank, flank_amp_exp} -- nunca ofereceu o gate ao fit.
    # Fica fittable=False; comportamento (on/off) coberto por
    # tests/test_l1_flank_wear_axial.py.
    ParameterRule("flank_wear_on", "physical", False, _axial_forca,
                  "liga o canal L1 de desgaste de flanco ~ A_F (forma "
                  "independente do k_thread_fret legado, idioma continuo "
                  "0=off identico a c_D/famp_couple_on); so modo forca axial"),
    ParameterRule("k_wear_flank", "physical", True, _axial_forca,
                  "razao de wear especifica do flanco [1/Pa] (KB "
                  "wear_spec_anchor thread|35CrMo-SCM435, Zhang 2019); so "
                  "modo forca axial"),
    ParameterRule("flank_amp_exp", "physical", True, _axial_forca,
                  "expoente de amplitude do desgaste de flanco (candidato "
                  "literatura 1.5-1.6, Liu 2020 super-linear); so modo "
                  "forca axial"),
    # L1 v2 (F4, prereg B1-v3 2026-07-22): limiar de slip do flanco —
    # candidato (c) da falsificacao T4 (power-law puro nao e' fraco no nivel
    # E forte no slope; o limiar zera o canal em amplitude baixa e maximiza
    # d(wear)/dA_F perto do limiar). 0.0 = bit-identico ao v1.
    ParameterRule("flank_s_crit", "physical", True, _axial_forca,
                  "limiar de slip do flanco [m] (stick/shakedown abaixo — "
                  "Mantyla 2020/Juoksukangas 2016); wear ~ (s-s_crit)+^exp; "
                  "so modo forca axial"),
    # L1 v2 rota transversal (F4, 2026-07-22): switch BINARIO como
    # flank_wear_on (gradiente-nao-fitavel; ligado por PREREG/config, nunca
    # pelo otimizador). Predicado _transversal: a rota so existe onde ha slip
    # transversal resolvido (zhang18/19/liu2020 — desgaste de flanco SEM
    # rotacao sob disp-mode). Os fitaveis da rota sao os MESMOS do canal
    # axial (k_wear_flank/flank_amp_exp/flank_s_crit) — nucleo compartilhado
    # flank_wear_from_slip; NOTA: as ParameterRules desses 3 declaram
    # _axial_forca (regime historico do T4); o fit transversal per-rig e'
    # conduzido por prereg/config explicito (nao via active_candidates), como
    # em F2-P2.1 — reavaliar o predicado se/quando a rota for adotada.
    ParameterRule("flank_transverse_on", "physical", False, _transversal,
                  "liga a rota TRANSVERSAL do canal L1 de flanco (slip de "
                  "flanco = slip transversal resolvido; zhang18/19/liu2020 "
                  "R5: perda por desgaste de flanco sem rotacao); switch "
                  "binario, 0=off identico"),
    # --- L2 (plano L1-L7 task-5, 2026-07-17): dependencia de carga de Phi via
    #     forma eliptica de Grosse (1990), so em U_loaded (particao Phi de um
    #     F_ax_ext explicito). Generico -- qualquer junta pre-carregada pode
    #     exercer o regime (nao regime-especifico como o canal L1 axial, sem
    #     par registry-truth exigido). kj_mode (str, mode switch) NAO entra
    #     aqui -- mesmo idioma de conform_driver/k_tr_mode (omitidos: mode
    #     switches nunca sao fittable=True, licao da revisao da Task 2). ---
    # phi_load_dep: declarado, ainda nao identificavel (so afeta U_loaded
    # diagnostico); reavaliar quando entrar no objetivo (Task-5 review).
    ParameterRule("phi_load_dep", "physical", False, _sempre,
                  "deformacao/carga critica de separacao da forma eliptica "
                  "de Grosse (1990) que modula a particao Phi do lado do "
                  "membro em U_loaded; per-junta"),
)


def active_candidates(bounds: Dict[str, tuple], priors: Dict[str, float],
                      conditions: Iterable["ConditionSpec"], theta: float,
                      estimated: Set[str]) -> List[str]:
    """Candidatos fitaveis do fit compartilhado: nome em bounds E priors E
    com regra fittable ativada por ALGUMA condicao do dataset. A ordem segue
    a ordem de `bounds` (preserva o determinismo da forward selection).

    Nome fitavel sem regra no registro => KeyError (o registro e o dono da
    lista; drop silencioso mascararia uma constante nova nunca fitada)."""
    pool = [n for n in bounds if n in priors]
    # Congelados por decisao (§4.42c): oferecer um deles ao fit e ERRO alto e
    # claro (nao silencioso) — a decisao de descongelar e do professor, nao de
    # quem monta bounds/priors.
    frozen = [n for n in pool if n in FROZEN_S_ZERO]
    if frozen:
        raise ValueError(
            "Parametros CONGELADOS por decisao (§4.42c, S≈0 no tornado) "
            f"oferecidos ao fit: {frozen} — "
            + "; ".join(f"{n}: {FROZEN_S_ZERO[n]}" for n in frozen))
    known_fittable = {r.name for r in PARAMETER_REGISTRY if r.fittable}
    unknown = [n for n in pool if n not in known_fittable]
    if unknown:
        raise KeyError(
            f"Constantes sem regra fittable no PARAMETER_REGISTRY: {unknown}"
            " — adicione a regra (o registro e a fonte unica, spec"
            " 2026-07-03 §5.5).")
    regimes = [regime_from_condition(c, theta, c.name in estimated)
               for c in conditions]
    ativos = {r.name for r in PARAMETER_REGISTRY
              if r.fittable and any(r.active(reg) for reg in regimes)}
    return [n for n in pool if n in ativos]


# ---------------------------------------------------------------------------
# Camada 4 da validacao de software (2026-07-08): PRIORS DAS ANCORAS.
# Le New_Theory/adopted_configs.json (registro unico de calibracao) e expoe
# as bandas MEDIDAS da campanha de ancoras (sec4.26) como priors/guardas:
# fits futuros partem de banda medida; a GUI pode avisar input fora-da-banda.
# ---------------------------------------------------------------------------

def anchor_priors() -> dict:
    """Priors de proveniencia (bandas medidas) do registro de calibracao.
    Retorna {} se o registro nao existir (registry continua funcional)."""
    import io as _io
    import json as _json
    from pathlib import Path as _Path
    reg = _Path(__file__).resolve().parents[3] / "New_Theory" / "adopted_configs.json"
    if not reg.exists():
        # fallback: layout sem src/ intermediario
        reg = _Path(__file__).resolve().parents[2] / "New_Theory" / "adopted_configs.json"
    if not reg.exists():
        return {}
    data = _json.loads(_io.open(reg, encoding="utf-8").read())
    return data.get("priors_ancoras", {})


def _r5_anchors() -> dict:
    """New_Theory/r5_anchors.json lido direto (mesmo idioma de anchor_priors;
    NAO via knowledge_base — kb importa este modulo, seria ciclo). {} se
    ausente (guarda continua funcional)."""
    import io as _io
    import json as _json
    from pathlib import Path as _Path
    p = _Path(__file__).resolve().parents[3] / "New_Theory" / "r5_anchors.json"
    if not p.exists():
        p = _Path(__file__).resolve().parents[2] / "New_Theory" / "r5_anchors.json"
    if not p.exists():
        return {}
    return _json.loads(_io.open(p, encoding="utf-8").read())


# --------------------------------------------------------------------------
# ALAVANCAS INERTES — o que e' decidivel do CONFIG vs o que exige o CASO
#
# Motivo de existir (2026-07-28): setar `c_bend` numa config sem o modo certo, ou
# `loose_arrest_floor` num caso onde o afrouxamento rotacional nao carrega perda,
# e' um NO-OP SILENCIOSO. Isso custou um dia de trabalho duplicado em duas sessoes
# paralelas, que interpretaram "a alavanca esta morta" como "a direcao do ajuste
# esta errada".
#
# E CORRIGE UM GOTCHA ERRADO do CLAUDE.md, que dizia "`c_bend`/`loose_arrest_floor`
# INERTES sem pack na ENTRY". Medido com sonda de 2 pontos no engine:
#   * `c_bend`  -> inerte com `k_tr_mode="axial_frac"` (o DEFAULT), vivo com
#     "bending": delta -0,057 (c_bend=5) e -0,068 (c_bend=50). Gate por MODO,
#     decidivel do config. O pack e' so quem costuma ligar o modo.
#   * `loose_arrest_floor` -> a comporta e' `if floor <= 0: return 1.0`, chamada
#     SEM condicao de modo (a docstring do engine diz "compoe (ortogonal) com
#     loose_torsion_mode"). Ela NAO precisa de pack. O que a torna inerte e' o
#     CANAL que ela gateia (afrouxamento rotacional) carregar ~0 da perda —
#     medido: floor=0,25 e 0,50 dao delta EXATAMENTE 0 num caso cujo canal
#     rotacional e' 0,0% da perda, com e sem pack. Nao e' decidivel do config.
#
# Por isso a API tem DUAS funcoes, e nao uma lista: a distincao entre "nao pode
# agir" e "nao agiu neste caso" e' a substancia do problema.
# --------------------------------------------------------------------------

# campo -> (campo de modo, valor que o ativa, default do modo, o que ele faz)
# So entram gates VERIFICADOS nos dois sentidos (inerte E vivo) por sonda.
_GATE_POR_MODO = {
    "c_bend": ("k_tr_mode", "bending", "axial_frac",
               "compliance de flexao do parafuso em k_tr"),
    # 2026-07-29: DEMONSTRADO por sonda de 2 pontos nos DOIS sentidos, que e' a
    # regra da casa. Em `liu2022_fig8_multi_t1`, sharpness 1,0 -> 2,5:
    #   modo "off" (default)        -> mae/max/sigma IDENTICOS ao digito (delta 0
    #                                  EXATO) => a alavanca e' IMPOSSIVEL ali;
    #   modo "cattaneo_mindlin"     -> 0,053269 -> 0,053244 (delta ~2,5e-5).
    # Registrar aqui EVITA o erro que a varredura de sigma_res quase produziu:
    # ela mediu delta=0 em 10 casos canonicos e o parametro parecia candidato a
    # FROZEN_S_ZERO ("S=0 sempre"). Nao e' — e' um gate de MODO, e o modo
    # cattaneo_mindlin e' CANDIDATO DE FORMA da campanha. Congela-lo mataria um
    # candidato em silencio. Caveat medido: mesmo com o modo aceso o efeito e'
    # ~2e-5, ou seja 0,08% do limite de sigma_res — ele nao resgata aquela perna.
    "slip_regime_sharpness": ("slip_regime_mode", "cattaneo_mindlin", "off",
                              "afiamento da fracao de gross-slip "
                              "(Cattaneo-Mindlin)"),
}

# Alavancas que gateiam um CANAL: a inercia depende do caso, nao do config.
_ALAVANCAS_DE_CANAL = {
    "loose_arrest_floor": "afrouxamento rotacional (comporta de auto-travamento)",
    "eta_loose": "afrouxamento rotacional (k_torsional, modo bolt_torsion)",
    # ATENCAO (auditoria 2026-07-29): esta entrada e' VERDADEIRA mas INCOMPLETA.
    # `k_j_init` tem QUATRO sitios de leitura no engine, nao um:
    #   778  `k_j_ax()` — rigidez GW da junta, INCONDICIONAL (11 chamadas: laco
    #        principal, U_int da energia, rho = k_j_ax/k_b, ...);
    #   1038 rigidez de take-up do slip (0,3*k_j_init);
    #   1906 `k_torsional` DENTRO do ramo loose_torsion_mode=="bolt_torsion" —
    #        e' esta rota que a linha abaixo descreve;
    #   2057 reescrita dinamica (`replace(material, k_j_init=kj_new)`).
    # Logo: a rota rotacional e' gateada por canal, mas a rota de RIGIDEZ age
    # sempre. Medido: delta nao-nulo em 3 de 10 casos canonicos (ate 4,5e-4).
    # Quem ler so esta linha vai supor que zerar o canal rotacional torna o
    # parametro inerte — nao torna.
    "k_j_init": "afrouxamento rotacional (k_torsional, modo bolt_torsion) — "
                "MAS tambem age SEMPRE pela rigidez GW (k_j_ax); ver o "
                "comentario acima antes de trata-lo como inerte",
    # Adicionado 2026-08-05 (D-Q). Satura o canal de fretting de FLANCO por
    # profundidade restante. DUAS condicoes de inercia, e sao diferentes:
    #  (a) COMPANHEIRO: exige `flank_wear_on=1` no cfg — sem ele
    #      `flank_wear_from_slip` nunca e' chamada e o fator nem e' avaliado.
    #      Isto e' decidivel do CONFIG (classe do `c_bend`-sem-pack).
    #      Medido: das 28 fontes, so LIU_2016 e LI_2022_TRIBOINT o tem ativo —
    #      17 de 207 casos do store.
    #  (b) CANAL: mesmo com o companheiro ligado, se `thread_fretting` carrega
    #      ~0 da perda naquele caso o fator nao move nada. Medido em 4 curvas
    #      (JCSR com F_amp=0; YANG_2021 em stick permanente): canal fica em
    #      ZERO ate com os companheiros forcados.
    # ⚠️ E o contradominio e' [0,1]: ele so DESACELERA. Nao serve a classe que
    # precisa de ACELERACAO tardia (falsificada por construcao em 2026-08-02) —
    # medido Delta=0 EXATO nas 21 curvas dela.
    "flank_fret_depth": "fretting de FLANCO (thread_fretting) — exige "
                        "flank_wear_on=1 (decidivel do config) E que o canal "
                        "carregue perda (decidivel da decomposicao); "
                        "contradominio [0,1], so desacelera",
}


def inert_levers(overrides: dict, defaults: dict | None = None) -> dict:
    """Campos de `overrides` que NAO PODEM agir, com o motivo. So o estatico.

    Cobre gates por MODO: o campo e' lido apenas num ramo do engine, e o modo
    efetivo (o do proprio `overrides`, senao o default) nao seleciona esse ramo.
    Devolve ``{campo: motivo}``; dict vazio = nenhuma inercia ESTATICA detectada.

    **Nao cobre** inercia por canal vazio — para essa nao existe resposta a partir
    do config; ver `channel_gated_levers()`. Um dict vazio aqui significa "nenhuma
    alavanca impossivel", NAO "todas as alavanca vao surtir efeito".

    `defaults` permite injetar os defaults do modo (evita importar o engine).
    """
    fora = {}
    for campo, (campo_modo, ativa, default_modo, o_que) in _GATE_POR_MODO.items():
        if campo not in overrides:
            continue
        modo = overrides.get(campo_modo)
        if modo is None and defaults is not None:
            modo = defaults.get(campo_modo)
        if modo is None:
            modo = default_modo
        if modo != ativa:
            fora[campo] = (
                f"{campo}={overrides[campo]} e' INERTE: e' lido so quando "
                f"{campo_modo}=='{ativa}', e o modo efetivo e' '{modo}' "
                f"({o_que}). Ligue {campo_modo} ou use um pack que o ligue.")
    return fora


def channel_gated_levers() -> dict:
    """Alavancas cuja inercia depende do CASO: ``{campo: canal que ela gateia}``.

    Elas modulam um canal de perda. Se o canal carrega ~0 da perda naquele caso, a
    alavanca nao move nada — e nenhuma inspecao do config revela isso. Verifique
    contra a DECOMPOSICAO (o `decomp` do store ja a carrega), nao contra o config.

    E' a forma generalizada da licao do Lu2024 registrada no ledger: varrer
    `k_wear_running` ate 20x nao moveu nada porque o wear era 1% da perda. *Antes
    de girar um lever, olhar a decomposicao.*
    """
    return dict(_ALAVANCAS_DE_CANAL)


# Nomes de CAMPO do engine que apontam para uma ancora cujo nome e' outro. Ate
# 2026-07-28 este mapa era a UNICA porta de entrada do guarda, e isso o tornava
# uma armadilha: `check_input("mu_dry", 0.35)` devolvia None EM SILENCIO — 0,35
# esta fora da banda [0,14; 0,19], mas "mu_dry" e' o nome do PRIOR, nao de um
# campo, e nao estava no mapa. Agora o nome do proprio prior tambem vale (ver
# `_prior_key`), e `checkable_inputs()` existe para desambiguar o None.
_ALIAS_CAMPO_ENGINE = {"mu_thread": "mu_dry", "mu_bearing": "mu_dry"}


def _prior_key(name: str, pri: dict | None = None) -> str | None:
    """Chave de `anchor_priors()` que checa `name`, ou None se nao ha nenhuma.

    Aceita as duas formas: o nome do CAMPO do engine (`mu_bearing`) e o nome do
    PRIOR (`mu_dry`). Devolve None quando o prior existe mas nao tem banda
    medida (`C_creep_por_par`, `emb_depth`, `N_emb`) — nesses casos nao ha o que
    checar, e o contrato de "None = sem aviso" se mantem.
    """
    pri = anchor_priors() if pri is None else pri
    key = _ALIAS_CAMPO_ENGINE.get(name, name)
    if key not in pri or not pri[key].get("banda_medida"):
        return None
    return key


def checkable_inputs() -> set[str]:
    """Nomes que `check_input_provenance` sabe checar de fato.

    Existe porque `None` e' ambiguo: significa "dentro da banda" OU "nao sei
    checar isso". Quem exibe avisos (dialogo de calibracao) deve usar isto para
    nao dar a impressao de que um parametro passou por uma guarda que nunca
    rodou. `k_wear_spec` entra por um caminho proprio (bandas R5 por
    interface|par), por isso e' acrescentado explicitamente.
    """
    pri = anchor_priors()
    nomes = {k for k, v in pri.items() if v.get("banda_medida")}
    nomes |= {campo for campo, chave in _ALIAS_CAMPO_ENGINE.items()
              if chave in pri and pri[chave].get("banda_medida")}
    if (_r5_anchors().get("wear_spec") or {}):
        nomes.add("k_wear_spec")
    return nomes


def check_input_provenance(name: str, value: float) -> str | None:
    """Guarda de proveniencia: retorna None se o input esta dentro da banda
    medida (ou sem ancora), senao uma mensagem de aviso citando a fonte.
    Cobre as ancoras §4.26 (priors_ancoras) e, F1 item 3 (prereg 2026-07-21),
    as bandas R5 de k_wear_spec por interface|par (uniao das bandas em 1/Pa;
    valor fora de TODAS = aviso listando cada banda com fonte). mu_thread R5
    sao PONTOS (sem banda) — a banda de mu segue a do §4.26 (mu_dry); nao
    inventamos tolerancia."""
    # --- R5: k_wear_spec = K/H [1/Pa] por interface|par (banda medida) ------
    if name == "k_wear_spec":
        ws = (_r5_anchors().get("wear_spec") or {})
        bandas = {k: v for k, v in ws.items()
                  if v.get("unit") == "1/Pa" and v.get("band")}
        if not bandas:
            return None
        v = float(value)
        if any(float(b["band"][0]) <= v <= float(b["band"][1])
               for b in bandas.values()):
            return None
        det = "; ".join(
            f"{k}: [{float(b['band'][0]):.3g}, {float(b['band'][1]):.3g}] "
            f"({b.get('source', 'R5')})" for k, b in sorted(bandas.items()))
        return (f"k_wear_spec={value} fora de TODAS as bandas medidas R5 "
                f"(1/Pa) — {det}")
    pri = anchor_priors()
    key = _prior_key(name, pri)
    if key is None:
        return None
    banda = pri[key].get("banda_medida")
    if not banda:
        return None
    lo, hi = float(banda[0]), float(banda[1])
    if lo <= float(value) <= hi:
        return None
    return (f"{name}={value} fora da banda MEDIDA [{lo}, {hi}] "
            f"({pri[key].get('fonte', 'ancora')}, verdict {pri[key].get('verdict')})")
