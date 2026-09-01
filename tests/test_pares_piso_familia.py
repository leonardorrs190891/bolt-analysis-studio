# -*- coding: utf-8 -*-
"""Invariante: nenhuma FAMILIA DE PISO nova pode atravessar variavel varrida.

## O defeito que este teste existe para pegar

`report_html._pisos_medidos` agrupa curvas em "familias de replica" por uma
chave MECANICA:

    k = (src, round(delta_mm, 4), round(F_amp_N, 1), mode)

Ela e' **cega** a espessura, material, frequencia, torque, rugosidade e **carga
axial**. Quando a variavel varrida do paper e' uma dessas, a chave junta
condicoes DISTINTAS como se fossem replicas — e o "piso" resultante nao mede a
repetibilidade do ensaio, mede o efeito que o paper estava estudando.

O estrago nao e' cosmetico: piso INFLADO **afrouxa** `limite_sres` (que e'
`max(META_SRES, piso)`), e limite afrouxado **aprova curva que nao deveria
passar**. Esta classe ja custou TRES blocos de retratacao — ROUSSEAU (espessuras
pareadas como replicas), CACCESE (condicoes distintas) e SUN (piso invalido) —
e cada um foi descoberto por acidente, depois de assinaturas terem sido dadas.

Auditoria de 2026-08-07 (`pares_piso_auditoria.md`): **4 de 20** familias
automaticas tem membros com condicao divergente. So' **1** tem efeito hoje
(`ECCLES_2010`, piso 0,0828 contra 0,0250 sem ela) — as outras 3 tem piso medido
ABAIXO do global, entao `max` devolve 0,025 de qualquer modo. Erradas em
conceito, inocuas em efeito **por enquanto**: basta uma curva nova subir o piso
de uma delas para o pareamento errado passar a morder SEM AVISO. E' esse
"sem aviso" que este teste remove.

## O que ele NAO faz

**Nao muda estatuto.** Nao toca `limite_sres`, nao bloqueia familia, nao mexe no
censo — bloquear familia e' PROPOSTA (P-15), e proposta se assina, nao se
executa. Este arquivo so' **denuncia**, e denuncia apenas o que for NOVO em
relacao a lista declarada abaixo.

## Como falha

Dois modos, os dois ruidosos e com nome:

* **familia divergente NOVA** — apareceu um pareamento que atravessa condicao e
  ninguem o registrou. E' o caso perigoso: o piso da fonte pode ter mudado sem
  que ninguem tenha olhado;
* **familia declarada que SUMIU** — foi consertada (bloqueada) ou o dado mudou.
  Nao e' erro, mas exige retirar a entrada daqui, senao a lista vira ficcao.

O criterio ignora **dispersao de especime** de proposito: o `tr_loose_gain`
per-replica do BAUER e' *lido da vida N50 medida* e distingue especimes da MESMA
condicao — sao replicas legitimas. So' campos de GEOMETRIA/CONDICAO disparam.
"""
from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
STORE = (ROOT / "Models" / "CALIBRATION_AND_VALIDATION"
         / "validation_store.json")

# Campos de config que codificam GEOMETRIA ou CONDICAO. Divergencia neles dentro
# de uma familia significa "condicoes distintas", nao "espécimes distintos".
_CAMPOS_CONDICAO = (
    "c_bend", "emb_depth", "GA_member", "d_hole_mm", "d_washer_mm",
    "delta_free", "k_tr_mode", "conform_driver", "mu_bearing", "mu_thread",
)

# FAMILIAS DIVERGENTES CONHECIDAS (auditadas em 2026-08-07). Chave = (fonte, n).
# O `n` entra de proposito: se a familia crescer ou encolher, a auditoria tem de
# ser refeita — o piso muda com a composicao.
_DIVERGENTES_CONHECIDAS = {
    # ⚠️ A entrada ("ECCLES_2010", 10) foi RETIRADA em 2026-08-08 porque a P-15
    # foi assinada e EXECUTADA: as 10 curvas entraram em `_SEM_FAMILIA_MECANICA`,
    # logo a familia deixou de existir. Custo previsto e pago: censo 140 -> 139
    # (saiu a `eccles2010_fig7c_axial_2p7kN`, sigma 0,0258, que passava so'
    # porque o piso falso afrouxava o limite da fonte 3,3x).
    # Foi ESTE teste que exigiu a retirada — ele falhou em
    # `test_declaracao_nao_vira_ficcao`, que e' exatamente o modo de falha para
    # o qual foi desenhado.
    ("LIU_2022_RETIGHT", 18): "inocua HOJE (piso < global): junta oleo (mu "
                              "0,176) com seco (mu 0,236)",
    ("SUN_2025_REASSY", 5): "inocua HOJE (piso < global): junta numeros de "
                            "remontagem distintos (emb_depth 9,2e-6..1,06e-5)",
    ("LIU_2020_WEAR", 3): "inocua HOJE (piso < global): mu_thread divergente",
}


@pytest.fixture(scope="module")
def familias():
    """(fonte, n) -> [case_ids] das familias automaticas com condicao divergente.

    Reconstroi os grupos com a chave COPIADA DO SITIO (`_pisos_medidos`), nunca
    reinventada — se a chave do report mudar, este teste tem de ser atualizado
    junto, e e' melhor que ele quebre a que ele meça outra coisa em silencio.
    """
    import sys
    sys.path.insert(0, str(ROOT / "src"))
    import bolt_analysis_studio.validation.runner as rn
    from bolt_analysis_studio.validation import report_html as rh
    from bolt_analysis_studio.validation.case_registry import (
        all_records, record)
    from bolt_analysis_studio.validation.runner import CaseResult

    dados = json.loads(STORE.read_text(encoding="utf-8"))
    recs = {r.case_id: r for r in all_records()}
    grupos: dict = defaultdict(list)
    for cid, bruto in dados.items():
        if cid not in recs:
            continue
        res = CaseResult.from_dict(bruto)
        x, d = res.metric_x, res.metric_data
        if not (x and d and len(x) == len(d) >= 4):
            continue
        if cid in rh._SEM_FAMILIA_MECANICA:
            continue
        cfg = getattr(res, "config_used", None) or {}
        try:
            k = (recs[cid].source, round(float(cfg.get("delta_mm") or 0), 4),
                 round(float(cfg.get("F_amp_N") or 0), 1), cfg.get("mode"))
        except (TypeError, ValueError):
            continue
        grupos[k].append(cid)

    fora = {}
    for k, cids in grupos.items():
        if len(cids) < 2:
            continue
        ovs = {c: rn._effective_overrides(record(c), {}) for c in cids}
        dif = {f for f in _CAMPOS_CONDICAO
               if len({str(ovs[c].get(f)) for c in cids}) > 1}
        if dif:
            fora[(k[0], len(cids))] = (sorted(cids), sorted(dif))
    return fora


def test_nenhuma_familia_divergente_nova(familias):
    """Familia que atravessa condicao e NAO esta declarada = piso suspeito."""
    novas = {k: v for k, v in familias.items()
             if k not in _DIVERGENTES_CONHECIDAS}
    assert not novas, (
        "FAMILIA DE PISO DIVERGENTE NOVA — a chave mecânica juntou condições "
        "distintas e ninguém registrou.\n"
        "Piso inflado AFROUXA `limite_sres` e pode aprovar curva que não "
        "deveria passar (classe que já custou 3 retratações).\n"
        "Audite com `New_Theory/pares_piso_impacto.py` e: ou bloqueie a família "
        "(proposta, assinatura), ou declare-a aqui com o motivo.\n"
        + "\n".join(f"  {f} (n={n}): difere em {v[1]}\n    " + ", ".join(v[0])
                    for (f, n), v in sorted(novas.items())))


def test_declaracao_nao_vira_ficcao(familias):
    """Entrada declarada que sumiu = consertada ou dado mudou; retire-a."""
    sumiu = {k: v for k, v in _DIVERGENTES_CONHECIDAS.items()
             if k not in familias}
    assert not sumiu, (
        "ENTRADA DECLARADA QUE NÃO EXISTE MAIS — a família foi bloqueada, "
        "mudou de tamanho ou o dado mudou.\n"
        "Não é erro, mas a lista precisa acompanhar, senão vira ficção "
        "(a mesma razão pela qual `_VIVAS` falha por âncora perdida).\n"
        + "\n".join(f"  {f} (n={n}): {v}" for (f, n), v in sorted(sumiu.items())))


# Curvas que passam o tripé APENAS porque um par declarado afrouxa o limite da
# fonte (auditadas em 2026-08-07, `pares_piso_auditoria.md` §2). Os 7 pares
# declarados sustentam 5 pontos do censo: KARLSEN 0,0903 e LU_2024 0,1030 contra
# 0,0250 sem eles. Todos foram verificados e se sustentam — o mais consequente
# (`karlsen run2p2 × run7p1`) tem σ 0,0897 contra mediana 0,1126 da própria
# família M30 HV, ou seja é CONSERVADOR.
#
# Este conjunto é declarado para que a CONCENTRAÇÃO não cresça em silêncio:
# um par declarado é uma afirmação forte, e quanto mais censo repousa sobre ele,
# mais caro fica descobrir tarde que estava errado.
# ⛔ ATUALIZADO em 2026-08-14: a `lu2024_M8_fig18_amp1p5` SAIU deste conjunto.
# Motivo (o que o proprio assert pede que se registre): os 3 pares declarados do
# LU_2024 foram REMOVIDOS na retratacao LU-PROTOCOLO (commit `74e1500`) — o
# paper separa §3.1.3 (half-sine de maquina, 1 Hz: as `fig14_*_long`) do §3.2
# (controle MANUAL: Fig. 18/20), entao os pares cruzavam PROTOCOLOS e nao eram
# replicas. Sem par declarado no LU, `limite_sres(LU_2024)` voltou ao global
# 0,0250 e a `fig18_amp1p5` deixou de passar por afrouxamento — ela saiu do
# tripe junto (censo 147 -> 146), o que ja esta registrado naquela adocao.
#
# ⚠️ A guarda ficou VERMELHA entre `74e1500` (07:07) e este conserto: a
# retratacao mexeu no conjunto e a lista nao acompanhou. E' exatamente o modo de
# falha que este teste existe para tornar barulhento — funcionou; so faltou
# atualizar a lista no mesmo commit.
_DEPENDEM_DE_PAR_DECLARADO = {
    "karlsen2022_M30_HV_run2p2",
    "karlsen2022_M30_HV_run6p2",
    "karlsen2022_M30_HV_run7p1",
    "karlsen2022_M42_HV_run21p0",
}


def test_censo_que_repousa_em_par_declarado_nao_cresce_calado():
    """Quantas curvas passam SÓ porque um par declarado afrouxou o limite."""
    import sys
    sys.path.insert(0, str(ROOT / "src"))
    from bolt_analysis_studio.validation import report_html as rh
    from bolt_analysis_studio.validation.case_registry import all_records
    from bolt_analysis_studio.validation.runner import CaseResult

    dados = json.loads(STORE.read_text(encoding="utf-8"))
    recs = {r.case_id: r for r in all_records()}
    res = {c: CaseResult.from_dict(b) for c, b in dados.items() if c in recs}
    pares = [(recs[c].source, r) for c, r in res.items()]

    com = rh._pisos_medidos(pares)
    orig = rh._PARES_REPLICA_DECLARADOS
    try:
        rh._PARES_REPLICA_DECLARADOS = ()
        sem = rh._pisos_medidos(pares)
    finally:
        rh._PARES_REPLICA_DECLARADOS = orig

    def passa(f, r, pis):
        sd = rh.sres_para_censo(r)
        return (r.mae <= rh.META_MAE and r.maxerr <= rh.META_MAX
                and sd is not None and sd <= rh.limite_sres(f, pis))

    dep = {c for c, r in res.items()
           if rh.caso_comparavel(recs[c].source, c) and r.mae is not None
           and passa(recs[c].source, r, com)
           and not passa(recs[c].source, r, sem)}
    assert dep == _DEPENDEM_DE_PAR_DECLARADO, (
        "MUDOU o conjunto de curvas que repousa em par DECLARADO.\n"
        f"  entraram: {sorted(dep - _DEPENDEM_DE_PAR_DECLARADO) or '—'}\n"
        f"  saíram:   {sorted(_DEPENDEM_DE_PAR_DECLARADO - dep) or '—'}\n"
        "Par declarado é afirmação forte ('estes dois são réplicas'); quanto "
        "mais censo repousa sobre ele, mais caro é descobrir tarde que estava "
        "errado. Re-audite com `New_Theory/pares_declarados_impacto.py` e "
        "atualize esta lista com o motivo.")


# Curvas que passam o tripe APENAS porque o piso da FONTE (declarado OU
# automatico) afrouxa o limite da 3a perna acima do global 0,025.
#
# ⚠️ Por que este conjunto existe, alem do `_DEPENDEM_DE_PAR_DECLARADO`: aquele
# vigia so os 7 pares DECLARADOS — a afirmacao forte, feita a mao. Mas as
# familias AUTOMATICAS (chave mecanica `(fonte, delta, F_amp, modo)`) tambem
# levantam o limite, e a chave e' CEGA a parametros de primeira ordem que nao
# entram nela. Medido em 2026-08-14 (`New_Theory/icmez_chave_cega_ao_grip.md`):
# das 13 curvas abaixo, 9 repousam em familia AUTOMATICA, fora do alcance da
# guarda anterior.
#
# Classificacao medida (a familia e' replica DE FATO?):
#   KARLSEN_2022 x4  -> par DECLARADO; ja coberto pela outra guarda
#   BAUER_2024   x2  -> SIM: fig6_rep1..rep6, replicas pelo proprio nome
#   CHU_2026     x2  -> SIM: test5 x test6_REPEAT
#   ICMEZ_2025   x5  -> ❌ NAO: a familia pareia grip_mm 13,8 x 19,8 mm
#                       (comprimento de aperto), e os MAEs de piso dao
#                       0,105-0,209 — isso nao e' repetibilidade, e' diferenca
#                       de condicao. Mesma assinatura de SUN_2025 (crimp x
#                       padrao, MAE 0,448) e KARLSEN (Vibralock x HV), os dois
#                       JA bloqueados por este motivo. Custo de bloquear,
#                       medido: censo 146 -> 141 (3 das 8 sobrevivem por
#                       merito).
# ✅ EXECUTADO em 2026-08-14 (tarde), por delegacao "assine e continue em
# loop": os 8 casos do ICMEZ + o chu test9 entraram em _SEM_FAMILIA_MECANICA
# (bloqueio cirurgico recomendado pelo proprio audit; passo 3 — estender esta
# guarda — ja estava feito). Sairam deste conjunto as 5 demir (piso de grip) e
# o chu test5 (o limite 0,0507 era inflado pela familia ilegitima δ=0,5; com
# so a familia legitima test5×test6, o limite honesto reprova o test5 e mantem
# o test6). Censo 146 -> 140, custo declarado ANTES no audit.
_DEPENDEM_DE_PISO_DE_FONTE = {
    # ── 2026-08-23: as 2 do ECCLES que fecharam com `arrest_approach_exp`=2,0
    # escopado ao protocolo intermitente (prereg eccles-fig8-arrest-exp).
    # ⚠️ ELAS FECHAM SOB O LIMITE POR FONTE (0,0565), NAO SOB O GLOBAL
    # (0,025): sigma 0,0254 (fig8a, 1,02x do global) e 0,0341 (fig8c, 1,36x).
    # A guarda pegou isto e esta CERTA em pegar — o fato entra declarado, nao
    # escondido. E' propriedade da ROTA, nao da celula escolhida: nenhuma das
    # 4 celulas medidas (1,75/2,00/2,25/2,50) poe as duas sob o global
    # (0,0271/0,0339 · 0,0254/0,0341 · 0,0256/0,0351 · 0,0274/-).
    # A regua por fonte e' a D1, adotada em 2026-07-30, e o piso do ECCLES foi
    # RE-MEDIDO no mesmo dia pela adocao do item X (0,0698 -> 0,0565, apertou).
    "eccles2010_fig8a_no_axial_baseline1",
    "eccles2010_fig8c_no_axial_baseline2",
    # par declarado (tambem em _DEPENDEM_DE_PAR_DECLARADO)
    "karlsen2022_M30_HV_run2p2",
    "karlsen2022_M30_HV_run6p2",
    "karlsen2022_M30_HV_run7p1",
    "karlsen2022_M42_HV_run21p0",
    # familia automatica LEGITIMA (replicas de fato)
    "bauer2024_M8_fig6_rep2",
    "bauer2024_M8_fig6_rep3",
    # ENTROU 2026-08-20 (adocao bauer-fig8-scrit-especime): sigma 0,0282 >
    # global 0,025, repousa no piso da fonte (0,0900, medido nas fig6 M8).
    # ⚠️ A pergunta da guarda (fig6 e' M8, test1 e' M12 — pareamento cruzando
    # geometria?) foi respondida COM NUMERO antes de aceitar: o piso da
    # PROPRIA familia fig8 (test1/2/3 = 3 especimes na mesma condicao nominal
    # M12/50kN/espectro, par a par na janela comum) e' sigma 0,0532-0,1176
    # (mediana 0,1008) — MAIOR que os 0,0900 emprestados. O piso da fonte e'
    # CONSERVADOR contra o scatter da familia da propria curva; o modelo
    # (0,0282) esta 2-4x mais perto de cada replica do que elas entre si.
    "bauer2024_M12_fig8_test1",
    # ✅ A `chu2026ti_D1p0mm_F0_49kN_test6_repeat` SAIU em 2026-08-14 ~15:50, e a
    # saida e' na direcao BOA: a adocao do par nivel/forma do embedding (prereg
    # `2026-08-14-chu-test5-embedding`) levou o sigma dela de 0,0285 para 0,0122
    # — bem abaixo do global 0,025 —, entao ela deixou de DEPENDER do piso da
    # fonte e passa por MERITO. A irma `test5` entrou no tripe pelo mesmo par
    # (0,0436 -> 0,0183) e tambem nao depende de piso.
    # ⇒ menos censo repousando em piso e' exatamente o que este guard existe para
    # incentivar. Ele denunciou a MELHORA com o mesmo barulho com que denunciaria
    # uma piora — e isso esta certo: o conjunto mudou, e mudanca de conjunto tem
    # de ser audivel independentemente do sinal.
}


def test_censo_que_repousa_em_piso_de_fonte_nao_cresce_calado():
    """Curvas que passam SO porque o piso da fonte (qualquer um) afrouxou.

    Espelho do teste do par declarado, um nivel acima: nao pergunta de onde vem
    o piso, so se o censo depende dele. Pega familia AUTOMATICA, que a outra
    guarda nao ve.
    """
    import sys
    sys.path.insert(0, str(ROOT / "src"))
    from bolt_analysis_studio.validation import report_html as rh
    from bolt_analysis_studio.validation.case_registry import all_records
    from bolt_analysis_studio.validation.runner import CaseResult

    dados = json.loads(STORE.read_text(encoding="utf-8"))
    recs = {r.case_id: r for r in all_records()}
    res = {c: CaseResult.from_dict(b) for c, b in dados.items() if c in recs}
    pis = rh._pisos_medidos([(recs[c].source, r) for c, r in res.items()])

    def passa(f, r, lim):
        sd = rh.sres_para_censo(r)
        return (r.mae <= rh.META_MAE and r.maxerr <= rh.META_MAX
                and sd is not None and sd <= lim)

    dep = {c for c, r in res.items()
           if rh.caso_comparavel(recs[c].source, c) and r.mae is not None
           and passa(recs[c].source, r, rh.limite_sres(recs[c].source, pis))
           and not passa(recs[c].source, r, rh.META_SRES)}

    assert dep == _DEPENDEM_DE_PISO_DE_FONTE, (
        "MUDOU o conjunto de curvas que repousa em PISO DE FONTE.\n"
        f"  entraram: {sorted(dep - _DEPENDEM_DE_PISO_DE_FONTE) or '—'}\n"
        f"  saíram:   {sorted(_DEPENDEM_DE_PISO_DE_FONTE - dep) or '—'}\n"
        "Piso de fonte afrouxa a 3a perna acima do global 0,025. Antes de "
        "aceitar uma entrada NOVA, confirme que a familia que a sustenta e' de "
        "REPLICAS DE FATO — a chave mecanica e' cega a grip_mm, F0, duracao e "
        "estagio de reaperto, e ja pareou nao-replicas em 4 fontes. Re-audite "
        "com `New_Theory/icmez_chave_cega_ao_grip.md` e atualize a lista COM O "
        "MOTIVO.")


def test_nenhuma_familia_divergente_morde_o_limite(familias):
    """Pos-P-15: NENHUMA familia com condicao divergente pode afrouxar o limite.

    Era 'a unica com efeito segue sendo o ECCLES' ate 2026-08-08; com a P-15
    executada o ECCLES saiu, e o invariante endurece: agora o conjunto tem de
    ficar VAZIO. As 3 familias divergentes que restam sao inocuas SO' porque o
    piso medido delas esta abaixo do global — se uma subir, este teste avisa
    antes que um F7 invalido seja assinado sobre ela."""
    import sys
    sys.path.insert(0, str(ROOT / "src"))
    from bolt_analysis_studio.validation import report_html as rh
    from bolt_analysis_studio.validation.case_registry import all_records
    from bolt_analysis_studio.validation.runner import CaseResult

    dados = json.loads(STORE.read_text(encoding="utf-8"))
    recs = {r.case_id: r for r in all_records()}
    pares = [(recs[c].source, CaseResult.from_dict(b))
             for c, b in dados.items() if c in recs]
    pisos = rh._pisos_medidos(pares)
    mordem = sorted(
        f for (f, _n) in familias
        if rh.limite_sres(f, pisos) > rh.META_SRES + 1e-9)
    assert mordem == [], (
        "UMA FAMÍLIA DIVERGENTE VOLTOU A MORDER. Depois da execução da P-15 "
        "(2026-08-08) nenhuma família com condição divergente afrouxa mais o "
        f"`limite_sres` — hoje mordem: {mordem}.\n"
        "Ou uma das 3 famílias 'inócuas' subiu o piso acima de "
        f"{rh.META_SRES}, ou apareceu família nova. Nos dois casos o piso da "
        "fonte voltou a medir a VARIÁVEL VARRIDA em vez da repetibilidade: "
        "re-audite com `New_Theory/pares_piso_impacto.py`.")
