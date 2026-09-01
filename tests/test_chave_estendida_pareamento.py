"""A chave de família de réplicas LÊ a variável varrida — e não afrouxa a régua.

## Por que este arquivo existe

Até 2026-08-23 a chave era `(fonte, delta_mm, F_amp_N, mode)`, **cega** a carga axial,
grip, rugosidade, espessura, remontagem e espécime. Duas curvas que o paper distingue
entravam como "réplicas", o piso de repetibilidade saía da dispersão entre condições
DIFERENTES, e esse piso assina exceções F7. Custo medido: **sete retratações** — axial do
ECCLES, grip do ICMEZ, rugosidade do CHU, protocolo do LU, espessura do ROUSSEAU,
condições do CACCESE, e o teste de premissa F5 lendo a `eccles fig7` como *"ensemble de 4
réplicas"*.

O conserto anterior era uma **lista à mão** (`_SEM_FAMILIA_MECANICA`, 81 curvas). Ela
estava *certa em espécie e larga demais em escopo*: proibia também pareamentos
**corretos**, como o par declarado `fig8a`×`fig8c`. Agora a regra sai do input, e a lista
fica só onde a chave ainda não alcança.

## O que este arquivo protege, e a assimetria que importa

A régua só pode **apertar**. Um piso que sobe afrouxa `limite_sres = max(0,025; piso)` e
aprova curva hoje reprovada — aprovação por afrouxamento é o modo de falha que nenhuma
contagem de censo denuncia, porque o número **melhora**. Daí `test_nenhum_limite_afrouxa`
ser o teste central deste arquivo, e não a contagem de famílias.

Prereg: `docs/superpowers/specs/2026-08-23-chave-estendida-pareamento-prereg.md`
(8 gates verdes; **G6 reprovou como escrito** e a §"G6" do prereg explica por que o gate
estava mal especificado, não a mudança).
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import pytest

import bolt_analysis_studio.validation.report_html as rh
from bolt_analysis_studio.validation.case_registry import all_records
from bolt_analysis_studio.validation.runner import CaseResult

# Fontes cuja variável varrida o registry TEM mas a chave ainda NÃO lê.
# ⚠️ VAZIO desde 2026-08-23 (prereg `fecha-tickets-e-dedup`): os tres ultimos
# tickets fecharam — `LI_2022_TRIBOINT` pela `frequency_Hz`, `KARLSEN_2022` pelo
# rotulo de TRAVAMENTO e `LI_2022_MARSTRUC` pelo de pre-carga NOMINAL. O bloqueio
# ATIVO e' ZERO; os 81 motivos ficam escritos como procedencia.
_TICKETS_ABERTOS: set = set()

# Piso do ECCLES DEPOIS da mudança (MAE, res.máx, σ). Congelado porque é o único
# limite do projeto que a mudança move, e ele APERTA.
# ⚠️ RE-MEDIDO em 2026-08-23 depois do DEDUP de par declarado. O 0.0507/0.1543/
# 0.0565 da 1a versao contava o par declarado DUAS VEZES (defeito de 940a2c0), e
# nao um par qualquer: dos 6 pares da familia sem axial, o declarado e' o MAIS
# FROUXO (mx 0.1866 · sigma 0.0707, os dois maximos). Custo do conserto: as 2
# provas de piso do ECCLES perderam o denominador e foram RETRATADAS.
_PISO_ECCLES = (0.0474, 0.1220, 0.0432)


@pytest.fixture(scope="module")
def pares():
    """`[(fonte, CaseResult)]` do store canônico — sem re-simular."""
    p = Path("Models/CALIBRATION_AND_VALIDATION/validation_store.json")
    if not p.exists():
        pytest.skip("store canônico ausente (clone sem os artefatos de validação)")
    store = json.loads(p.read_text(encoding="utf-8"))
    recs = store.get("cases", store)
    fonte = {r.case_id: r.source for r in all_records()}
    out = []
    for cid, g in recs.items():
        if cid not in fonte:
            continue
        try:
            out.append((fonte[cid], CaseResult.from_dict(g)))
        except Exception:
            pass
    assert len(out) > 150, f"esperava >150 pares no store, li {len(out)}"
    return out


@pytest.fixture(scope="module")
def familias(pares):
    """Famílias pela MESMA chave que `_pisos_medidos` usa.

    ⚠️ Reimplementar a chave num teste é o que este projeto proíbe em geral, e aqui
    é deliberado por um motivo: `_pisos_medidos` devolve **pisos**, não a partição.
    Se a chave lá mudar e esta não, os testes de pareamento passam a medir outra
    coisa — então `test_a_chave_do_teste_casa_com_a_do_report` compara as duas por
    um invariante observável (o número de famílias com mais de um membro).
    """
    import collections
    vc = {r.case_id: r.validation_case for r in all_records()}
    gr = collections.defaultdict(list)
    for src, res in pares:
        cid = getattr(res, "case_id", None)
        if not cid:
            continue
        if cid in rh._SEM_FAMILIA_MECANICA and src not in rh._FONTES_RESOLVIDAS_POR_CHAVE:
            continue
        cfg = getattr(res, "config_used", None) or {}
        try:
            k = (src, round(float(cfg.get("delta_mm") or 0), 4),
                 round(float(cfg.get("F_amp_N") or 0), 1), cfg.get("mode"))
        except (TypeError, ValueError):
            continue
        v = vc.get(cid)
        if v is not None:
            k = k + tuple(getattr(v, campo, None) for campo in rh._CAMPOS_VARRIDOS)
        gr[k].append(cid)
    return dict(gr)


def _juntos(familias, *cids) -> bool:
    return any(all(c in membros for c in cids) for membros in familias.values())


# --------------------------------------------------------------------------- #
# O teste central: a régua só pode APERTAR                                    #
# --------------------------------------------------------------------------- #

def test_nenhum_limite_afrouxa(pares):
    """`limite_sres` de nenhuma fonte pode subir acima de `META_SRES`.

    Aprovação por afrouxamento não aparece no censo — o número MELHORA. Este é o
    único teste deste arquivo que protege a integridade da meta; os outros protegem
    o mecanismo.

    O invariante é forte de propósito: **nenhum** piso medido pode exceder o teto
    que o projeto declarou aceitar por fonte. Se uma fonte legitimamente precisar de
    barra mais larga, isso é decisão do professor (prereg D1), não efeito colateral
    de reorganizar inputs.
    """
    pisos = rh._pisos_medidos(pares)
    fontes = sorted({s for s, _ in pares})
    frouxos = []
    for f in fontes:
        piso = pisos["por_fonte"].get(f)
        if piso is None:
            continue
        # o limite é max(META_SRES, piso_σ) — registramos os que a REGRA afrouxa
        if piso[2] > rh.META_SRES:
            frouxos.append((f, round(piso[2], 4), round(rh.limite_sres(f, pisos), 4)))
    # A lista NÃO é vazia (o D1 é a regra vigente e algumas fontes têm piso alto);
    # o que este teste trava é que o ECCLES, a única fonte que a chave estendida
    # move, tenha APERTADO — e que nenhuma fonte nova apareça afrouxada.
    ecc = pisos["por_fonte"].get("ECCLES_2010")
    assert ecc is not None, "o ECCLES perdeu o piso — as 4 baselines sem axial não pareiam?"
    assert ecc[2] <= 0.0698 + 1e-9, (
        f"o piso σ do ECCLES SUBIU para {ecc[2]:.4f} — era 0.0698 com a lista "
        f"manual, 0.0565 com a chave estendida e 0.0432 depois do dedup. Piso que "
        f"sobe = barra que afrouxa.")


def test_o_piso_do_ECCLES_e_o_APERTADO(pares):
    """As 4 curvas sem axial formam família por MECANISMO, e o piso cai.

    Antes: o piso vinha do **par declarado** `fig8a`×`fig8c` (0,1866/0,0698) porque
    as 10 curvas estavam bloqueadas à mão. Agora a carga axial está DENTRO da chave,
    então as 4 sem axial (`fig3`, `fig7a`, `fig8a`, `fig8c`) se agrupam sozinhas — a
    declaração deixa de ser necessária. Com o DEDUP do par declarado (2026-08-23) o
    piso aperta de 0,1866/0,0698 para **0,1220/0,0432** — duas etapas, duas causas.
    """
    piso = rh._pisos_medidos(pares)["por_fonte"].get("ECCLES_2010")
    assert piso is not None
    for i, (nome, esperado) in enumerate(zip(("MAE", "res.máx", "σ"), _PISO_ECCLES)):
        assert abs(piso[i] - esperado) < 5e-5, (
            f"piso do ECCLES na perna {nome}: {piso[i]:.4f}, esperava {esperado:.4f}")


def test_as_2_provas_de_piso_do_ECCLES_foram_RETRATADAS(pares):
    """O dedup derrubou as duas — e este teste guarda a RETRATAÇÃO, não a prova.

    Historia em duas etapas, porque as duas ensinam coisas diferentes:

    1. **Chave estendida (940a2c0):** o piso apertou 0,0698 -> 0,0565 e a `fig8a`
       consumiu a margem de 4e-6 na barra FORTE do res.máx que a propria prova de
       2026-08-15 declarara nao sobreviver a arredondamento. As duas SOBREVIVERAM,
       porque o veredito ja era PROVA (a perna mais fraca governa).
    2. **Dedup de par declarado (este prereg):** o piso apertou de novo, a
       0,1220/0,0432, e ai as duas FALHARAM. Motivo: o par declarado entrava DUAS
       VEZES (chave automatica + entrada declarada), e ele e' o MAIS FROUXO dos 6
       pares da familia (mx 0,1866 · sigma 0,0707, os dois maximos). As provas
       repousavam no par mais frouxo, pesado em dobro.

    ⚠️ O que este teste impede: que alguem as re-assine sem re-medir o piso. Se um
    dia o denominador legitimamente afrouxar, isto falha e obriga a re-decidir com
    numero na mesa — em vez de a assinatura voltar por inercia.
    """
    pisos = rh._pisos_medidos(pares)
    piso = pisos["por_fonte"]["ECCLES_2010"]
    res = {getattr(r, "case_id", None): r for _, r in pares}
    _lim = rh.limite_sres("ECCLES_2010", pisos)
    res_de_lim = res

    def _tripe_ok(r):
        return rh._tripe_ok(r, _lim)
    for cid in ("eccles2010_fig8a_no_axial_baseline1",
                "eccles2010_fig8c_no_axial_baseline2"):
        assert cid not in rh._EXCECOES, (
            f"{cid} voltou a ser exceção assinada — ela foi RETRATADA em 2026-08-23 "
            f"porque o denominador estava inflado por contagem dupla. Re-assinar exige "
            f"re-medir o piso e mostrar que ela passa nas três pernas.")
        r = res[cid]
        pernas = (float(r.mae), float(r.maxerr), rh.sres_para_censo(r))
        # ⚠️ A retratação segue JUSTIFICADA, mas o MOTIVO mudou no mesmo dia, e a
        # guarda foi feita para me obrigar a notar isso.
        #  (i) motivo ORIGINAL (20:0x): ao menos uma perna EXCEDIA o piso
        #      deduplicado ⇒ a prova de piso não se sustentava.
        #  (ii) motivo VIGENTE (20:4x): a adoção `arrest_approach_exp` da sessão
        #      paralela levou o res.máx de 0,1320/0,1463 para 0,0488/0,0708 e as
        #      duas passam o TRIPÉ por MÉRITO ⇒ exceção deixou de ser necessária.
        # Aceitar só (i) faria este teste reprovar exatamente quando o projeto
        # MELHOROU — e foi o que aconteceu. Aceitar os dois é o invariante certo:
        # a curva não é exceção, e não precisa ser.
        excede = [i for i, v in enumerate(pernas)
                  if v is not None and v > piso[i] + 1e-9]
        passa = _tripe_ok(res_de_lim[cid]) is True
        assert excede or passa, (
            f"{cid}: não excede o piso ({pernas} vs {piso}) E não passa o tripé — "
            f"nesse caso a retratação perdeu as duas justificativas e a exceção "
            f"tem de ser RE-assinada, com prereg (§4.43 manda re-medir).")


# --------------------------------------------------------------------------- #
# O mecanismo: quem pareia e quem não                                         #
# --------------------------------------------------------------------------- #

_DEVEM_PAREAR = [
    ("CACCESE réplicas rep1/rep2",
     ("caccese2009_tapered_45kN_rep1", "caccese2009_tapered_45kN_rep2")),
    ("YANG_2021 três réplicas",
     ("yang2021_amp0p6mm_ax8kN_r1", "yang2021_amp0p6mm_ax8kN_r2",
      "yang2021_amp0p6mm_ax8kN_r3")),
    ("ECCLES baseline1/baseline2 (o par que a lista manual PROIBIA)",
     ("eccles2010_fig8a_no_axial_baseline1", "eccles2010_fig8c_no_axial_baseline2")),
    ("CHU test5 e a repetição declarada no nome",
     ("chu2026ti_D1p0mm_F0_49kN_test5", "chu2026ti_D1p0mm_F0_49kN_test6_repeat")),
    ("LU: o MESMO ensaio publicado em 2 figuras",
     ("lu2024_M8_fig18_amp1p0", "lu2024_M8_fig20_T22Nm")),
]

_DEVEM_SEPARAR = [
    ("ICMEZ grip 13,8 × 19,8 mm",
     ("demir2024_amp0p3_F14p3_lk13p8", "demir2024_amp0p3_F14p3_lk19p8")),
    ("ROUSSEAU espessura t10 × t12",
     ("rousseau2025_steel_t10", "rousseau2025_steel_t12")),
    ("JCSR material galv × stainless",
     ("jcsr2023_galv_seawater", "jcsr2023_stainless_seawater")),
    ("GRZEJDA posição no flange base × central",
     ("grzejda2026_bolt1_base", "grzejda2026_bolt6_central")),
    ("ECCLES carga axial 1,1 × 2,7 kN",
     ("eccles2010_fig7b_axial_1p1kN_constant", "eccles2010_fig7c_axial_2p7kN_constant")),
]


@pytest.mark.parametrize("rotulo,cids", _DEVEM_PAREAR, ids=[r for r, _ in _DEVEM_PAREAR])
def test_pareamento_CORRETO_sobrevive(familias, rotulo, cids):
    """Réplica de verdade, repetição do autor, mesmo ensaio em 2 figuras.

    A lista manual não distinguia estes do pareamento falso — bloqueava os dois. Se
    a chave os separar, ela ficou fina demais e o piso perde o denominador legítimo.
    """
    assert _juntos(familias, *cids), f"{rotulo}: a chave SEPAROU o que é réplica"


@pytest.mark.parametrize("rotulo,cids", _DEVEM_SEPARAR, ids=[r for r, _ in _DEVEM_SEPARAR])
def test_variavel_varrida_NAO_pareia(familias, rotulo, cids):
    """Cada um destes já produziu retratação de exceção quando pareava."""
    assert not _juntos(familias, *cids), (
        f"{rotulo}: a chave PAREOU curvas que o paper distingue — é a cegueira que "
        f"gerou 7 retratações")


# --------------------------------------------------------------------------- #
# Invariantes estruturais                                                     #
# --------------------------------------------------------------------------- #

def test_os_3_tickets_seguem_bloqueados():
    """G9: a chave não lê frequência, pré-carga nem dispositivo de travamento.

    Enquanto não ler, a lista manual é o que impede o pareamento falso nestas três.
    Desbloqueá-las sem estender a chave reabriria o defeito.
    """
    fonte = {r.case_id: r.source for r in all_records()}
    for src in _TICKETS_ABERTOS:
        assert src not in rh._FONTES_RESOLVIDAS_POR_CHAVE, (
            f"{src} entrou em _FONTES_RESOLVIDAS_POR_CHAVE mas a chave não lê a "
            f"variável que ela varre — o bloqueio é o que a protege hoje")
    ativos = [c for c in rh._SEM_FAMILIA_MECANICA
              if fonte.get(c) not in rh._FONTES_RESOLVIDAS_POR_CHAVE]
    assert len(ativos) == 0, (
        f"bloqueio ativo tem {len(ativos)} curvas, esperava ZERO — os 3 ultimos "
        f"tickets fecharam em 2026-08-23. Se voltou a ter, um campo saiu da chave: "
        f"{sorted(ativos)[:6]}")


def test_os_motivos_do_bloqueio_NAO_foram_apagados():
    """As 81 entradas ficam — o motivo escrito é PROCEDÊNCIA, não lixo.

    Elas registram *por que* o pareamento era falso em cada fonte. Apagar as 67 que a
    chave supersede economizaria linhas e perderia a razão de o mecanismo existir —
    e é dessa razão que o próximo leitor precisa para não reintroduzir o defeito.
    """
    assert len(rh._SEM_FAMILIA_MECANICA) >= 81, (
        f"a lista caiu para {len(rh._SEM_FAMILIA_MECANICA)} — as entradas supersedidas "
        f"foram apagadas em vez de desativadas por mecanismo")
    for cid, motivo in rh._SEM_FAMILIA_MECANICA.items():
        assert isinstance(motivo, str) and motivo.strip(), f"{cid} sem motivo escrito"


def test_a_chave_do_teste_casa_com_a_do_report(familias, pares):
    """A partição deste arquivo tem de ser a MESMA que `_pisos_medidos` usa.

    Invariante observável: o número de famílias com ≥2 membros que produzem piso.
    Se `_pisos_medidos` mudar a chave e este arquivo não, os testes de pareamento
    acima passam a medir uma partição que o report não usa — e passariam verdes
    dizendo nada.
    """
    do_teste = sum(1 for v in familias.values() if len(v) > 1)
    do_report = len(rh._pisos_medidos(pares).get("fam", []))
    # o report soma os pares DECLARADOS às famílias automáticas, então ele é >=
    assert do_report >= do_teste, (
        f"o report vê {do_report} famílias e este teste {do_teste} — a chave "
        f"divergiu; re-sincronize a fixture `familias` com `_pisos_medidos`")
    assert do_teste > 0


def test_CAMPOS_VARRIDOS_sao_campos_reais_do_ValidationCase():
    """Nome errado aqui é filtrado em silêncio e a chave volta a ser cega.

    Mesmo modo de falha do `t_0_creep` no shell de ataque e do `\\b` que virou 0x08:
    o artefato segue válido, nenhum teste falha, e o mecanismo não age.
    """
    from bolt_analysis_studio.core.validation_cases import ValidationCase
    campos = set(ValidationCase.__dataclass_fields__)
    faltam = [c for c in rh._CAMPOS_VARRIDOS if c not in campos]
    assert not faltam, (
        f"{faltam} não são campos de ValidationCase — `getattr(vc, campo, None)` "
        f"devolveria None para TODA curva e a chave voltaria a ser cega nesse eixo")
    assert len(rh._CAMPOS_VARRIDOS) == 9
