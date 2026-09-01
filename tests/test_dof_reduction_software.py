# -*- coding: utf-8 -*-
"""Programa de reducao de DOF (§4.42) IMPLEMENTADO NO SOFTWARE (2026-07-09,
"implemente tudo isso no bolt analysis studio").

Cobre:
  (c) congelados S≈0 no parameter_registry — enforcement em active_candidates;
  (d) leitores de proveniencia no pacote (provenance.py) + delegacao de
      library_common (fonte unica) + re-export no knowledge_base;
  (a') k_wear_spec na superficie do app (PRESET_PARAMS / V2_PARAM_NAMES);
  KB: sensitivity()/frozen_params()/dof_summary().
"""
import numpy as np
import pytest

from bolt_analysis_studio.calibration.parameter_registry import (
    FROZEN_S_ZERO, PARAMETER_REGISTRY, active_candidates)
from bolt_analysis_studio.calibration import knowledge_base as kb
from bolt_analysis_studio.calibration.provenance import (
    arrest_floor_from_curve, emb_depth_from_curve, emb_depth_from_early_drop)


# ---------------------------------------------------------------- (c) frozen
def test_frozen_set_is_the_tornado_verdict():
    assert set(FROZEN_S_ZERO) == {"k_j_init", "alpha_GW",
                                  "slip_capacity_coeff", "partial_slip_exp"}
    # todos tem regra nao-fittable no registry (documentacao viva p/ GUI)
    rules = {r.name: r for r in PARAMETER_REGISTRY if r.name in FROZEN_S_ZERO}
    assert set(rules) == set(FROZEN_S_ZERO)
    assert all(not r.fittable for r in rules.values())
    assert all("4.42" in r.rationale for r in rules.values())


def test_active_candidates_rejects_frozen_loudly():
    """Oferecer um congelado ao fit e ValueError CLARO (nao KeyError generico,
    nao drop silencioso)."""
    bounds = {"emb_depth": (1e-6, 5e-5), "k_j_init": (1e9, 1e10)}
    priors = {"emb_depth": 1e-5, "k_j_init": 4e9}
    with pytest.raises(ValueError, match="CONGELADOS.*4.42.*k_j_init"):
        active_candidates(bounds, priors, conditions=[], theta=np.pi / 2,
                          estimated=set())


def test_active_candidates_still_raises_keyerror_for_unknown():
    """A guarda antiga (constante nova sem regra) segue intacta."""
    bounds = {"constante_nova_xyz": (0, 1)}
    priors = {"constante_nova_xyz": 0.5}
    with pytest.raises(KeyError):
        active_candidates(bounds, priors, conditions=[], theta=np.pi / 2,
                          estimated=set())


# ------------------------------------------------------- (d) provenance em src
def test_provenance_pkg_matches_l24_numbers():
    """O modulo do pacote reproduz os numeros do §4.40 (Li2022ti 15Hz)."""
    emb, prov = emb_depth_from_early_drop(0.075, 10e3, 4.64e8, vdi_ref_m=3.5e-6)
    assert emb == pytest.approx(1.6e-6, rel=0.05)
    assert prov["provenance"] == "data_implied_early_drop"
    assert prov["diverges"] is True


def test_library_common_delegates_to_pkg():
    """library_common re-exporta AS MESMAS funcoes (fonte unica, sem fork)."""
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "New_Theory"))
    import library_common as lc
    assert lc.emb_depth_from_early_drop is emb_depth_from_early_drop
    assert lc.emb_depth_from_curve is emb_depth_from_curve
    assert lc.arrest_floor_from_curve is arrest_floor_from_curve


def test_arrest_floor_from_curve_plateau_and_falling():
    # plato final claro: floor = media do rabo, plateau=True
    r = np.array([1.0, 0.8, 0.5, 0.31, 0.30, 0.30, 0.30])
    floor, prov = arrest_floor_from_curve(r, tail_frac=0.4)
    assert floor == pytest.approx(0.30, abs=0.01)
    assert prov["plateau"] is True and prov["provenance"] == "data_end_plateau"
    # fim ainda caindo: limite inferior, plateau=False
    r2 = np.array([1.0, 0.9, 0.7, 0.5, 0.3, 0.1])
    _, prov2 = arrest_floor_from_curve(r2, tail_frac=0.5)
    assert prov2["plateau"] is False
    # degrada em curva curta
    f3, prov3 = arrest_floor_from_curve([1.0])
    assert f3 == 0.0 and prov3["provenance"] == "degraded"


# ------------------------------------------- (a') superficie do app + KB API
def test_k_wear_spec_in_app_surface():
    from bolt_analysis_studio.numerical.parameter_identifier import (
        PRESET_PARAMS, V2_PARAM_NAMES)
    assert "k_wear_spec" in PRESET_PARAMS
    assert "k_wear_spec" in V2_PARAM_NAMES
    p = PRESET_PARAMS["k_wear_spec"]()
    assert p.target == "jm.k_wear_spec"
    assert p.default == pytest.approx(5e-14)      # = 1e-4/2e9 (par legado)
    assert p.lo < p.default < p.hi


def _campos_tocados_por_adocao() -> set:
    """Campos de `JointMaterial` que ALGUMA config adotada seta.

    Esta e' a contagem honesta de "onde ha liberdade por rig": o resto do
    dataclass e' capacidade default-inerte, que existe para poder ser testada
    e falsificada sem virar grau de liberdade. Le o `adopted_configs.json`
    (grupo + `per_case`), nao uma lista digitada — lista digitada envelhece.
    """
    import dataclasses
    import json
    from pathlib import Path
    from bolt_analysis_studio.numerical.dynamic_stiffness_analyzer import (
        JointMaterial)

    raiz = Path(__file__).resolve().parents[1]
    d = json.loads((raiz / "New_Theory" / "adopted_configs.json")
                   .read_text(encoding="utf-8"))
    chaves = set()
    for node in d["sources"].values():
        cfg = node.get("cfg") or {}
        for k, v in cfg.items():
            if k == "per_case":
                for sub in (v or {}).values():
                    chaves |= set(sub or {})
            elif k not in ("prov", "verdict"):
                chaves.add(k)
    return chaves & {f.name for f in dataclasses.fields(JointMaterial)}


def _sem_dof_fitado(nomes: set) -> None:
    """Invariante que sustenta "campos != DOF" (§4.42) sem lista digitada.

    Campo que NENHUMA config adotada seta contribui ZERO grau de liberdade —
    e' capacidade dormente, nao ajuste. Falha nomeando quem passou a ser
    fitado, que e' o evento que de fato importa: capacidade virou DOF.
    """
    tocados = _campos_tocados_por_adocao()
    virou_dof = sorted(nomes & tocados)
    assert not virou_dof, (
        f"estes campos deixaram de ser dormentes e agora sao FITADOS por "
        f"config adotada: {virou_dof}. Isso muda a contagem honesta de DOF — "
        f"tire-os da lista e atualize §4.42/MODEL_LEGITIMACY, ou reverta a "
        f"adocao. (hoje: {len(tocados)} dos campos do engine sao tocados por "
        f"alguma adocao.)")


def test_kb_sensitivity_and_dof():
    s_tr = kb.sensitivity("transverse")
    if s_tr:                                       # estudo presente no repo
        assert s_tr["mu"]["mean"] > s_tr["K_archard"]["mean"]
        assert "tr_loose_gain" in s_tr
        s_ax = kb.sensitivity("axial")
        assert s_ax["emb_depth"]["mean"] > 0
    froz = kb.frozen_params()
    assert froz == dict(FROZEN_S_ZERO)
    d = kb.dof_summary()
    # Estagio B removeu 9 tuners do dataclass (era 89 -> 80, no main); campanhas
    # subsequentes (pre-L1-L7) elevaram para 82 antes deste branch (fork
    # d960b4b); plano L1-L7 Task 2 (+4: famp_couple_on/mu_eff_lo/
    # mu_eff_F0_ref/gross_ceiling_decay, L3 F_amp<=mu_eff*F0) -> 86; Task 3
    # (+3: flank_wear_on/k_wear_flank/flank_amp_exp, L1 canal de flanco ~A_F)
    # -> 89; Task 5 (+2: kj_mode/phi_load_dep, L2 k_j(geometria,material))
    # -> 91; Task 7 (+3: creep_mode/creep_t_c/creep_alpha_sat, L5 creep
    # saturante opt-in) -> 94 (teto com folga p/ absorver isso sem re-editar
    # o teste a cada campo fisico novo).
    #
    # TETO CRUZADO EM 2026-07-28 (97 -> 98) e subido DE PROPOSITO, com registro:
    # quem cruzou foi `arrest_approach_exp` (commit 73d75ab, expoente na comporta
    # de arresto), o candidato do prereg do kernel grupo A que FALHOU o gate
    # (G2 FAIL / G3 FAIL) e por isso NAO foi adotado. Este teto e' um TRIPWIRE,
    # nao um invariante fisico: ele existe para forcar alguem a olhar quando o
    # dataclass cresce. Subir por reflexo o degrada em ruido, entao a folga nova
    # vem acompanhada do assert abaixo, que prende o MOTIVO pelo qual o campo
    # novo nao mexe na contagem honesta de DOF (campos != DOF, §4.42).
    #
    # TETO CRUZADO EM 2026-08-02 (105 -> 115). Quem cruzou foram CINCO campos,
    # todos da classe "aceleracao tardia" ENCERRADA no mesmo dia pela regra de
    # parada: `s1_amp_gate_{dref,p,floor}` (gate de amplitude no estagio 1 —
    # falsificado POR CONSTRUCAO: contradominio (0,1], so sabe atrasar) e
    # `k_dmg_all`/`k_late_amp` (amplificadores; o gradual reprovou por perfil,
    # +53% a +397% de MAE, e o de interruptor funciona mas nao como constante
    # por rig). Nenhum foi adotado.
    #
    # E desta vez o teto sobe com um invariante GERAL no lugar de mais uma
    # nota: o assert `_sem_dof_fitado` abaixo mede o que de fato importa —
    # campo que NENHUMA config adotada seta carrega ZERO DOF fitado. Um
    # candidato falsificado que continue no dataclass entra sempre nos
    # dormentes, e e' por isso que "campos != DOF" (§4.42) se sustenta sem
    # listar campo a campo. O teto continua util so como aviso grosso.
    #
    # 2026-08-05 (D-L): +2 campos (105 -> 107), e estes NAO sao dormentes —
    # `retight_loss_base`/`retight_loss_gain` foram ADOTADOS (relogio por
    # contagem de reapertos no LIU_2022, 3 numeros COMPARTILHADOS entre seco e
    # oleo). Contagem honesta re-medida: **55 dos 107** campos tocados por
    # alguma adocao, **52 dormentes** (o numero de dormentes nao mudou, porque
    # os 2 novos entraram ja fitados). Registro do que a adocao afirma: a taxa
    # de re-dano por evento de reaperto e' propriedade da SUPERFICIE, nao do
    # lubrificante — as diferencas seco/oleo saem do `c_D` ja adotado, porque
    # `k_emb_renew` multiplica D.
    #
    # 2026-08-14: +1 campo (115 -> 116), `emb_clock_delta_ref` — relogio de
    # assentamento dependente de deslocamento, `N_emb_eff = N_emb*(dref/delta)`.
    # E' DORMENTE: a forma foi implementada, validada (paridade 8/8 ao 12o
    # digito contra a sonda que calculava o N_emb a mao) e **NAO ADOTADA** — a
    # aplicacao na fonte inteira do CHU ganhava 1 curva mas piorava a `test3` em
    # +0,0392 no sigma, 4x acima da tolerancia de +0,01, e nenhuma chave FISICA
    # isola os ganhadores ({delta=1,0 Ra 0,4} u {delta=0,5 Ra 1,6} nao e' um
    # conjunto que o artigo defina). Registro:
    # New_Theory/lei_relogio_implementada_e_nao_adotada.md.
    #
    # ⚠️ E o campo NAO acrescenta grau de liberdade num sentido mais forte que o
    # de "ninguem o setou": o EXPOENTE da lei e' 1 POR CONSTRUCAO do mecanismo
    # (esgotamento por distancia de slip acumulada), nao um ajuste — nao existe
    # campo para muda-lo, e `tests/test_emb_clock_delta.py` PROIBE que apareca.
    # O unico numero que ele introduz e' a REFERENCIA `dref`, que e' uma escolha
    # de unidade (qual delta chama-se 1), nao um parametro livre: fixar
    # (dref, N_emb) e' o mesmo que fixar N_emb numa amplitude qualquer.
    #
    # 2026-08-15: +1 campo (116 -> 117), `loose_arrest_residual` — taxa
    # RESIDUAL sub-arresto no canal rotacional, `g = max(r*(1-floor), g)`.
    # Motivo medido (item Q, ICMEZ_2025): sem ele o `self_locking_gate` ZERA
    # quando F_0 alcanca o piso, o canal MORRE, e o engine so oferecia o
    # binario arresto/runaway; o dado, porem, ATRAVESSA o piso adotado
    # (0,308) e segue caindo a ~50% da taxa de meio. O campo poe o
    # meio-termo: o arresto deixa de ser barreira absoluta e vira JOELHO.
    # Leitura fisica: o nucleo auto-travado de Cattaneo-Mindlin nao e
    # rigido — cede sob ciclagem continuada.
    #
    # E DORMENTE, e a NAO-ADOCAO e o resultado: a sessao B validou o
    # mecanismo (G5 verde — a taxa tardia das 3 alvo sobe 0,20 -> 0,47,
    # dentro da banda do dado 0,48-0,57 que o binario nunca alcancava) e
    # FALSIFICOU a adocao pelos proprios gates: o residual sozinho reprova
    # no G1, e o par que fecha 3 curvas quebra 2 protegidas, piora 3 e
    # desancora um input VDI. Commit 5702281; censo 143/205 intacto.
    #
    # 2026-08-16: +1 campo (117 -> 118), `emb_pressure_exp` — encaixe DIRIGIDO
    # POR PRESSAO, `S_p = min(1, (p_init/p_ref_emb) ** emb_pressure_exp)`. E o
    # RAMO OPOSTO do `emb_conform_exp`: aquele modela pre-conformacao (aperto
    # maior ja achatou aspereza, sobra MENOS residuo ciclico); este modela o
    # escoamento plastico dirigido por pressao (aperto MENOR => reservatorio de
    # encaixe mais RASO). Os dois compoem por multiplicacao e ambos leem
    # p_init = F_0_init/A_contact, nunca o F_0 corrente.
    #
    # E DORMENTE, e a NAO-ADOCAO e o resultado: prereg
    # 2026-08-16-lu2024-embedding-dirigido-por-pressao, ramo G8 (falsificacao
    # honesta). G0 passou EXATO (pior |delta| = 0,000e+00 nas 210 curvas) e o
    # G1 REPROVOU — "a lei conserta o defeito que nomeou e NAO fecha a curva".
    # A alvo (lu2024_fig20_T10Nm) segue na fila form_limited, com uma rota a
    # menos. Commits 945f363 e d70a38f.
    # (nota 2026-08-19: a T10 FECHOU 3 dias depois — a MESMA lei + o floor
    # 0,3195 LIDO do terminal publicado, destravado pelo precedente SUN.)
    #
    # 2026-08-19/20: +3 campos (118 -> 121), a leva das ADOCOES POR LEITURA:
    # `free_spin_kin` (sec4.56 — a rigidez de dreno da helice e' a SERIE do
    #   laco, LIDA de dF/dtheta publicado; ADOTADA em 4 curvas ROUSSEAU +
    #   5 ICMEZ, fontes 8/8 e 8/8);
    # `gth_accel_p` (aceleracao progressiva do ratchet de stick, LSQ da
    #   integral r2=0,969; ADOTADA na yang2019_amp0p4, fonte 5/5);
    # `loose_F_exp` (P-13 da mesa: taxa fracionaria (F/F0)^fe — o meio-termo
    #   entre os DOIS ATRATORES runaway/arresto; ADOTADA nas 3 YANG_2023 por
    #   LSQ da solucao fechada, r2 0,997-0,9999);
    # e `mu_kinetic_frac` (historese mu_s/mu_k, DORMENTE: a avalanche
    #   pos-ruptura e' mais rapida que o real — 6 estruturas falsificadas).
    # Todos default-inertes com teste proprio (test_free_spin_kin,
    # test_gth_accel, test_mu_kinetic). Censo 143 -> 159 na leva.
    #
    # 2026-08-20 (tarde): +3 campos (121 -> 124), a forma RUNAWAY DE PORCA
    # SOLTA (`loose_runaway_{frac,gain,sharpness}`) — transicao
    # lei-de-potencia -> runaway no ramo graded, pedida pelo professor
    # ("forma na engine") depois que a rota ROBUSTA da zhang2006_fig3 provou
    # a lacuna com constantes LIDAS (theta digitalizado: disparo 10->42 deg,
    # razao de taxas ~14x, onde a lei F^fe lida desacelera por construcao).
    # Ancoras de leitura: frac=0,25 (o paper define o fim do Estagio II em
    # P=25%) e gain~13 (razao de taxas - 1). Default frac=0 OU gain=0 = OFF
    # exato (test_loose_runaway, 5 invariantes). Estudo:
    # zhang2006_fig3_estudo_do_caso.md sec9-sec10.
    #
    # 2026-08-21: +2 campos (124 -> 126), o BURST DE RUPTURA
    # (`onset_burst_{frac,rate}`) — liberacao da energia incubada quando o
    # gate de slip_onset_W abre (o MESMO Hill, sem estado novo); dreno
    # exponencial ao alvo (1-frac)*F0 que desacelera sozinho. Motivo: as
    # DUAS fig14_long do LU (plato -> burst ate a inflexao ~0,36-0,47 ->
    # cauda). ADOTADO na fig14_amp1p0_long (frac 0,62 LIDO da inflexao;
    # fecha a PIOR declarada do projeto 0,4802 -> 0,0136); a amp0p5_long
    # melhora 2,6x e NAO fecha (2 regimes pos-burst — custo declarado).
    # Default frac=0 OU rate=0 = OFF exato (test_onset_burst, 5 invariantes,
    # 2 consertos de setup registrados no proprio arquivo).
    #
    # 2026-08-21 (tarde): +1 campo (126 -> 127), o RELOGIO SIGMOIDE do
    # embedding (`emb_clock_m`, Weibull m>1 = plato+joelho+saturacao;
    # state-based exata via N implicito; m=1 default = BIT-IDENTICO,
    # test_emb_clock_weibull 4/4). Construida para a fig14_amp0p25_long e
    # NAO USADA nela — a ERRATA do proprio ataque mediu que o dado e degrau+
    # arresto (exponencial de relogio curto fecha com ZERO fitados, tudo
    # lido). O campo fica DORMENTE ate um plato real exigi-lo.
    #
    # 2026-08-21 (16:5x): +1 campo (127 -> 128), o GATE PROPRIO do burst
    # (`onset_burst_W`; 0.0 default = usa o `g` compartilhado = BIT-IDENTICO
    # a adocao fig14, test_onset_burst_gate_proprio 4/4). Motivo: a ANATOMIA
    # do bloqueio da liu2025_M16_amp0p8 (unica curva da fila; par_de_taxas
    # sec6) — os 3 gates de estado sao monotonicos E COMPARTILHADOS, entao o
    # burst gateado pelo `g` do slip_onset so abre onde o WEAR abre (na
    # amp0p8 o onset 250k segura o wear ate o fim e o burst nunca ve o
    # miolo). Fisica: limiar de ADESAO (burst) != limiar de ABRASAO (wear),
    # duas escalas do MESMO W_slip_acc. Corolario testado: mudar
    # onset_burst_W NAO move o canal de wear (assert direcional).
    #
    # 2026-08-21 (16:4x): +1 campo (128 -> 129), o PISO DE ARRESTO ANULAVEL POR
    # CARGA AXIAL EXTERNA (`ax_floor_override`; prereg 2026-08-21-eccles-axial-
    # tres-camadas, C3). 0.0 default = OFF EXATO, e o ramo exige TRES condicoes
    # (campo>0 E state.F_ax_ext>0 E geom) => identidade por CONSTRUCAO, nao por
    # `x*1.0==x` (test_eccles_axial, 13 invariantes).
    # ⚠️ ESTE CAMPO NASCE FALSIFICADO, e o teto sobe mesmo assim de proposito:
    # o G3 do prereg reprovou em 4 doses (a fig7d, curva-alvo, PIORA de res.max
    # 0,0901 para 0,22-0,25; os 2 controles pioram junto). O motivo e aritmetico
    # e vale mais que o campo: os pisos adotados do ECCLES JA decrescem com a
    # carga axial (0,232 / 0,182 / 0,137 para 1,1 / 2,7 / 3,1 kN, prov
    # `fitado-this-rig`) => o efeito do axial ja estava ABSORVIDO no piso, e
    # anula-lo aplica o desconto DUAS VEZES. Capacidade fica; rota nao.
    # Corolario para a contagem honesta: NENHUMA config adotada seta este campo,
    # logo ele carrega ZERO DOF fitado — que e exatamente o que `_sem_dof_fitado`
    # abaixo mede, e por isso "campos != DOF" segue de pe com 129.
    assert 75 <= d["total_campos"] < 130
    # campo novo tem de nascer DEFAULT-INERTE: e' isso que sustenta "campos !=
    # DOF". `arrest_approach_exp=1.0` = expoente unitario = comporta original.
    from bolt_analysis_studio.numerical.dynamic_stiffness_analyzer import (
        JointMaterial)
    assert JointMaterial().arrest_approach_exp == 1.0
    # o campo de 2026-08-21 (16:4x), pinado no valor que o desliga
    assert JointMaterial().ax_floor_override == 0.0
    # os 5 de 2026-08-02, pinados com o valor que os desliga (o `_p` e' um
    # expoente que so e' LIDO com `dref>0`, entao quem desliga o trio e' o
    # `dref=0`; pinar o expoente junto documenta a leitura).
    jm = JointMaterial()
    assert (jm.s1_amp_gate_dref, jm.s1_amp_gate_floor) == (0.0, 0.0)
    assert jm.s1_amp_gate_p == 8.0
    assert (jm.k_dmg_all, jm.k_late_amp) == (0.0, 0.0)
    # ⚠️ O trio de FLANCO (flank_wear_on/k_wear_flank/flank_amp_exp) NAO entra
    # nesta lista, e a tentativa de inclui-lo foi pega pela propria medicao em
    # 2026-08-02: ele deixou de ser dormente em 2026-07-30, quando a adocao do
    # LIU_2016 re-atribuiu a cauda creep->fretting e passou a SETAR os tres.
    # A nota mais abaixo neste teste ("default-inertes na config canonica")
    # segue valida so onde ela se aplica — por rig AXIAL, que e' o que o
    # `livres_por_rig["axial"] == []` prende. Exemplo vivo de §4.43 dentro de
    # um teste: a frase envelheceu porque o mundo mudou de baixo dela.
    # o de 2026-08-14, pinado no valor que o desliga (0.0 = OFF EXATO; o ramo
    # novo nem roda, nao ha multiplicacao por 1.0 no caminho desligado).
    assert jm.emb_clock_delta_ref == 0.0
    # ⚠️ 2026-08-15 (D-AD): `s1_amp_gate_dref` e `s1_amp_gate_p` SAIRAM dos
    # dormentes — foram ADOTADOS (gate de amplitude no `LIU_2025`, commit
    # 42568f4). `s1_amp_gate_floor` FICA: a adocao o deixou no default 0,0.
    # Contagem honesta re-medida: **64 dos 115** campos tocados por alguma
    # adocao, **51 dormentes**.
    #
    # ⚠️ ISTO NAO CONTRADIZ A FALSIFICACAO DE 2026-08-02 registrada acima
    # ("falsificado POR CONSTRUCAO: contradominio (0,1], so sabe atrasar"), e a
    # distincao importa para quem ler as duas notas juntas e concluir que o
    # gate esta morto:
    #   * em 08-02 ele foi oferecido a classe "aceleracao tardia", que precisa
    #     ACELERAR a perda no fim. Contradominio (0,1] nao acelera nada — logo,
    #     falsificado por algebra, sem precisar de medicao.
    #   * em 08-15 ele foi adotado para REDUZIR a perda em amplitude baixa, que
    #     e' exatamente o que (0,1] sabe fazer. O alvo era a INCLINACAO em
    #     amplitude do LIU_2025 (rho(amp, vies) = +1,000 EXATO nas 6, R2 0,978).
    # ⇒ mesma forma, jobs OPOSTOS. Falsificacao por contradominio vale contra o
    # job, nao contra o campo.
    # `loose_arrest_residual` entra DORMENTE (2026-08-15): existe no engine,
    # nenhuma config adotada o seta, e a adocao foi FALSIFICADA pelos gates
    # da propria sessao que o construiu. Caso exemplar de "campos != DOF".
    # `emb_pressure_exp` entra DORMENTE (2026-08-16): construido, medido e
    # NAO adotado pelo ramo G8 do proprio prereg que o propos.
    # 2026-08-19/20: `emb_pressure_exp` e `arrest_approach_exp` SAIRAM desta
    # lista — viraram DOF por ADOCAO, e cada um com procedencia registrada:
    # emb_pressure_exp=3,0 no LU_2024 (a lei medida NESTA fonte, r=+0,995,
    # prereg lu2024-t10-pressao-mais-piso-lido — a T10 fechou com ela);
    # arrest_approach_exp=8,0 na SUN standard (fitado-declarado, prereg
    # sun-standard-kernel-cinematico) e 8,0/1,0 nas leituras ROUSSEAU/ICMEZ.
    # A guarda fez exatamente o seu trabalho: capacidade virou DOF e a
    # contagem honesta acompanha.
    # 2026-08-20 (tarde): `loose_runaway_sharpness` entra DORMENTE — a adocao
    # da fig3 usa o default 6,0 (celula lida pura, sem setar o campo); os
    # irmaos frac/gain nascem ADOTADOS (leituras do traco theta) e por isso
    # ficam FORA desta lista.
    # 2026-08-21: `k_dmg_all` saiu e VOLTOU aos dormentes NO MESMO DIA — a
    # adocao do chu test2 (incubacao + k_dmg_all, melhora 3,6-6,4x) foi
    # REVERTIDA pelo gate de censo: o sigma 0,0374 nao fecha o limite REAL da
    # fonte (0,0296, apertado pelo bloqueio G/H; o prereg usou 0,0507
    # vencido — 4a ocorrencia do erro de limite). Melhoria sem fecho nao
    # entra no canonico; o campo segue dormente com a rota parcial
    # registrada no prereg chu-test2-incubacao-damage.
    _sem_dof_fitado({"s1_amp_gate_floor", "loose_arrest_residual",
                     "k_dmg_all", "k_late_amp", "loose_runaway_sharpness",
                     "emb_clock_delta_ref", "emb_clock_m",
                     # 2026-08-21: gate proprio do burst — dormente ate a
                     # sonda da amp0p8 virar adocao gateada (ou morrer)
                     "onset_burst_W"})
    # a nota do resumo NAO pode contradizer o numero calculado ao lado dela
    # (em 2026-07-28 dizia "94 campos" com total_campos=98)
    assert str(d["total_campos"]) in d["nota"]
    assert d["congelados_s_zero"] == 4
    # L1 (Task 4, gate B1 re-executado 2026-07-17): o canal de flanco ~A_F
    # foi calibrado per-rig mas o gate prereg FALHOU 2x (slope Liu2017
    # -2.8e-6/N vs banda [-4.4e-5,-1.1e-5]/N) => falsificacao documentada,
    # capacidade validada NAO adotada. Os 3 campos (flank_wear_on/
    # k_wear_flank/flank_amp_exp) existem no dataclass (dai o teto 89+ acima)
    # mas ficam DEFAULT-INERTES na config canonica => ZERO DOF por rig
    # axial; a classificacao daqui espelha o que esta ADOTADO, nao o que um
    # experimento fitou (§4.42: campos != DOF). Registro:
    # New_Theory/l1_axial_gate_result.json (bloco "verdict").
    assert d["livres_por_rig"]["axial"] == []
    # leitores de proveniencia expostos pela KB (mesmos objetos)
    assert kb.emb_from_early_drop is emb_depth_from_early_drop
    assert kb.floor_from_curve is arrest_floor_from_curve
