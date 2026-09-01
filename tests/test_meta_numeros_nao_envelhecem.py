# -*- coding: utf-8 -*-
"""Os números da META não podem envelhecer em silêncio nos documentos.

## O defeito que este arquivo existe para impedir

Em 2026-07-29 a régua da meta trocou de duas pernas para três. O painel mestre
foi atualizado no mesmo dia. **Nove arquivos não foram**, e a afirmação vencida
("o gargalo é o resíduo máximo, não o MAE") continuou sendo lida como vigente —
inclusive no relatório executivo do manual, que a apresentava como *"a leitura
estratégica"*. Pior: o **report por caso** seguiu julgando o MAE contra 0,10, e
uma curva reprovada no documento mestre abria a própria página com o cartão
VERDE.

O `MODEL_LEGITIMACY.md` §4.43 já enuncia a regra certa — *toda falsificação
carrega o fingerprint contra o qual foi medida, e vira suspeita assim que o
fingerprint muda* — mas **nada a fazia valer**. Regra em prosa não é invariante.
Este arquivo é a execução dela.

## O que ele NÃO faz, de propósito

Não policia todo número `N/202` do repositório. A maioria é **registro datado**
(`metrica_banda_results.md`, logs de campanha, preregs) e reescrevê-los seria
falsificar histórico — exatamente o oposto do objetivo. Ele policia uma lista
**declarada** de AFIRMAÇÕES VIGENTES, e recomputa a verdade do store.

## Como se comporta quando falha

Dois modos, os dois ruidosos de propósito:

* **âncora não encontrada** → alguém reescreveu a frase. O teste falha pedindo
  para re-apontar a âncora, em vez de passar em silêncio sobre um número que
  deixou de ser verificado (o `None` ambíguo que a `knowledge_base` já aprendeu
  a evitar: "dentro da banda" e "não sei checar" não podem ser o mesmo
  resultado).
* **número divergente** → imprime o do documento e o do store, e diz qual doc
  atualizar.

Nenhum dos dois se conserta editando o teste: conserta-se atualizando o
documento, ou registrando explicitamente que a afirmação virou histórico.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest


# --------------------------------------------------------------- o censo, do store

def _censo():
    """Recomputa o censo da meta do STORE, com os mesmos helpers que o report
    usa — nunca uma segunda implementação da regra (é o que garante que o teste
    e a página não possam divergir entre si)."""
    import bolt_analysis_studio.validation.report_html as R
    from bolt_analysis_studio.validation.case_registry import all_records
    from bolt_analysis_studio.validation.store import ValidationStore
    st = ValidationStore()
    comp, manda = [], {}
    # A EXCLUSÃO TEM DE SER A DO REPORT, não uma cópia: casos do usuário e
    # sintéticos entram no documento e NÃO no censo (202 comparáveis, não 203).
    # A 1ª versão deste teste usou `getattr(R, "_FORA_DO_CENSO", ())`, um nome
    # que não existe — o `getattr` com default devolveu `()` EM SILÊNCIO, o censo
    # contou 203/105 e o teste acusou a página de estar errada quando o errado
    # era ele. Por isso agora é acesso DIRETO ao atributo: se o nome mudar, o
    # teste quebra com AttributeError em vez de medir a coisa errada.
    # P2 2026-07-31: o filtro canônico virou o helper `caso_comparavel`
    # (fonte E caso — a duplicata amp1p0==T22 sai do censo por caso).
    # Acesso direto ao helper: se o nome mudar, AttributeError ruidoso.
    for rec in all_records():
        if not R.caso_comparavel(rec.source, rec.case_id):
            continue
        res = st.get(rec.case_id)
        if not (res and res.ok and res.mae is not None
                and res.maxerr is not None):
            continue
        comp.append((rec, res))
    # D1 (adotado 2026-07-30): o limite da 3a perna e' POR FONTE —
    # max(META_SRES, piso medido) via `limite_sres`, que le a flag
    # `_SRES_POR_FONTE`. O teste usa o MESMO helper que o report (nunca uma
    # 2a implementacao da regra): se a flag for revertida, este censo volta
    # sozinho para o global, junto com a pagina.
    pisos = R._pisos_medidos([(rec.source, res) for rec, res in comp])
    # sigma SEMPRE via `sres_para_censo` (regra n<6 assinada 2026-08-01):
    # None = nao-julgavel e `_perna_manda` ja trata como "nao passa".
    # Acesso direto ao helper — se o nome mudar, AttributeError ruidoso.
    for rec, res in comp:
        p = R._perna_manda(res.mae, res.maxerr, R.sres_para_censo(res),
                           R.META_MAE, R.META_MAX,
                           R.limite_sres(rec.source, pisos))
        manda[p] = manda.get(p, 0) + 1
    n = len(comp)
    n_ok = manda.get(None, 0)
    so_mae = sum(1 for rec, res in comp
                 if res.mae > R.META_MAE and res.maxerr <= R.META_MAX
                 and (lambda _s: _s is not None
                      and _s <= R.limite_sres(rec.source, pisos)
                      )(R.sres_para_censo(res)))
    porf = {}
    for rec, res in comp:
        e = porf.setdefault(rec.source, [0, 0])
        e[1] += 1
        if R._perna_manda(res.mae, res.maxerr, R.sres_para_censo(res),
                          R.META_MAE, R.META_MAX,
                          R.limite_sres(rec.source, pisos)):
            e[0] += 1
    n_exc = sum(1 for rec, _ in comp if rec.case_id in R._EXCECOES)
    n_decl = sum(1 for rec, _ in comp if rec.case_id in R._DECLARADAS)
    # SPLIT DAS FORA (2026-08-07): quantas das reprovadas ja tem estatuto e
    # quantas seguem ABERTAS. E' o par que envelhece mais rapido — ele muda a
    # cada assinatura (P-10/P-11/P-12 o mudaram 3x no mesmo dia) — e estava
    # publicado em 2 documentos sem invariante nenhum.
    # ⚠️ NAO e' `n_exc + n_decl`: aqueles contam sobre TODAS as comparaveis,
    # incluindo curvas que passam o tripe E carregam estatuto (uma excecao
    # assinada nao some quando a curva melhora por merito — foi assim que as
    # 19 assinaturas redundantes do D1 apareceram).
    fora_estat = sum(
        1 for rec, res in comp
        if R._perna_manda(res.mae, res.maxerr, R.sres_para_censo(res),
                          R.META_MAE, R.META_MAX,
                          R.limite_sres(rec.source, pisos))
        and (rec.case_id in R._EXCECOES or rec.case_id in R._DECLARADAS))
    # SPLIT POR PERNA VIOLADA + RESOLVIDOS + TOP-3 (ancorados 2026-08-16).
    # ⚠️ Ate aqui, da tabela "leitura estrategica VIGENTE" do relatorio
    # executivo so `so_mae`, `tripe`, `manda_*` e `fontes_100` tinham chave. As
    # outras CINCO celulas envelheceram em silencio AO LADO delas — medido no
    # dia: `resolvidos` publicava 155 contra 167 (defasagem de 12), "so
    # res.max" 4 contra 7, "so sigma_res" 10 contra 13, "mais de uma" 42 contra
    # 39, "3 maiores fontes" 36 % (26 de 73) contra 41 % (25 de 61).
    # A vizinhanca de celulas vigiadas faz a nao-vigiada PARECER conferida.
    viol = []
    for rec, res in comp:
        s = R.sres_para_censo(res)
        lim = R.limite_sres(rec.source, pisos)
        v = (res.mae > R.META_MAE, res.maxerr > R.META_MAX,
             s is None or s > lim)
        if any(v):
            viol.append(v)
    fora_exc = sum(
        1 for rec, res in comp
        if R._perna_manda(res.mae, res.maxerr, R.sres_para_censo(res),
                          R.META_MAE, R.META_MAX,
                          R.limite_sres(rec.source, pisos))
        and rec.case_id in R._EXCECOES)
    top3 = sorted((v[0] for v in porf.values()), reverse=True)[:3]
    return {
        "so_mx": sum(1 for v in viol if v == (False, True, False)),
        "so_sd": sum(1 for v in viol if v == (False, False, True)),
        "mais_de_uma": sum(1 for v in viol if sum(v) > 1),
        # "resolvido" = fecha o tripé OU tem exceção assinada. DECLARADA não
        # entra: declarar é "não dá para julgar", não "o modelo acertou".
        "resolvidos": n_ok + fora_exc,
        "top3_n": sum(top3),
        "top3_pct": round(100.0 * sum(top3) / max(n - n_ok, 1)),
        "n": n, "tripe": n_ok, "fora": n - n_ok,
        "fora_estatuto": fora_estat, "fora_aberta": (n - n_ok) - fora_estat,
        "declarado_total": n_ok + n_exc + n_decl,
        "manda_sd": manda.get("sd", 0), "manda_mae": manda.get("mae", 0),
        "manda_mx": manda.get("mx", 0), "so_mae": so_mae,
        "pct_sd": round(100.0 * manda.get("sd", 0) / max(n - n_ok, 1)),
        "fontes": len(porf),
        "fontes_100": sum(1 for v in porf.values() if not v[0]),
        # PASSIVO DE PROCEDENCIA (acrescentado 2026-08-14). Nao e' censo de
        # curva, mas envelhece igual e ja envelheceu: a linha do item A na
        # tabela da MESA ficou parada em "141 de 467" por DEZ fases enquanto a
        # tabela de mudancas do mesmo arquivo dizia 24. O motivo de o guarda nao
        # pegar era simples — ele so cobria afirmacoes ancoradas, e aquela linha
        # nao estava ancorada.
        # ⚠️ Importa o helper da CATRACA em vez de reimplementar o lookup: sao
        # SEIS convencoes de chave de `prov` (exata, composta, nome curto de
        # familia, composta anotada, narrativa, e descrita-por-papel em prosa),
        # e uma 2a implementacao mediria a propria suposicao — foi exatamente
        # assim que a auditoria original inflou o passivo em 32.
        "prov_sem": _passivo_prov(),
    }


def _passivo_prov() -> int:
    """Constantes adotadas sem procedencia, pelo MESMO lookup da catraca."""
    import importlib.util
    import json
    cam = Path(__file__).resolve().parent / "test_procedencia_catraca.py"
    spec = importlib.util.spec_from_file_location("_cat", cam)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    cfg = json.loads(
        (_raiz() / "New_Theory" / "adopted_configs.json").read_text(
            encoding="utf-8"))
    return len(mod._sem_prov(cfg["sources"]))


def _camadas() -> dict:
    """As 5 camadas de ESTATUTO, pelo classificador CANONICO da triagem.

    ## Por que existe (medido 2026-08-15, duas vezes no mesmo dia)

    O cabecalho da MESA publica a decomposicao das `fora` por camada. Ela e'
    escrita a mao e **nao estava sob guarda nenhuma**: as 21 afirmacoes de
    `_VIVAS` cobrem tripe/declarado_total/pernas, nunca as camadas.

    Custo observado: `estatuto das 64 ... classe-encerrada 8` conviveu com
    `fora 62` **no mesmo paragrafo** (residuo de antes da D-AD). Corrigi a mao
    as 14:5x; **as 15:51 ja estava errada de novo** (excecao 22->23 e
    indecidivel 15->14, pela assinatura SUB-SLIP das 15:09). Uma linha que
    envelhece em UMA HORA nao se conserta a mao — se guarda.

    ⚠️ Importa o classificador de `regra_de_parada_triagem` em vez de
    reimplementa-lo. Eu reimplementei a SELECAO das `fora` tres vezes em uma
    unica sessao e errei as tres (classifiquei tambem as que passam o tripe ->
    25 contra 6; fundi `_EXCECOES` com `_DECLARADAS` -> 18 declaradas viraram
    excecao; `continue` em `sd is None` -> 6 curvas evaporaram). Os tres erros
    eram INVISIVEIS na contagem de `classe_parada`, que deu 6 nos tres casos,
    porque os ramos de excecao e declaracao precedem o dela.

    Idioma de import copiado de `_passivo_prov`: caminho de arquivo +
    `importlib`, porque `New_Theory/` nao e' pacote instalado.
    """
    import importlib.util
    import json
    import bolt_analysis_studio.validation.report_html as R
    from bolt_analysis_studio.validation.case_registry import all_records
    from bolt_analysis_studio.validation.runner import CaseResult

    cam = _raiz() / "New_Theory" / "regra_de_parada_triagem.py"
    spec = importlib.util.spec_from_file_location("_triagem", cam)
    T = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(T)

    store = json.loads(T.STORE.read_text(encoding="utf-8"))
    recs = {r.case_id: r for r in all_records()}
    pisos = T.pisos_medidos(store, recs)
    exc = set(R._EXCECOES)          # SO' as excecoes; `_DECLARADAS` e' ramo
                                    # proprio DENTRO de `classificar`.
    out: dict = {}
    for cid, raw in store.items():
        rec = recs.get(cid)
        if rec is None or not raw.get("ok"):
            continue
        src = str(rec.source)
        if not R.caso_comparavel(src, cid):
            continue
        res = CaseResult.from_dict(raw)
        if res.mae is None or res.maxerr is None:
            continue
        sd = R.sres_para_censo(res)
        # A SELECAO tem de ser a do canonico: `sd is None` (n<6) NAO descarta
        # a curva — ela cai em `fora`, porque a condicao do tripe falha.
        if (res.mae <= R.META_MAE and res.maxerr <= R.META_MAX
                and sd is not None and sd <= R.limite_sres(src, pisos)):
            continue
        c = T.classificar(cid, raw, src, T.piso_da_fonte(pisos, src), exc)
        out[c] = out.get(c, 0) + 1
    return out


_CAMADA_CHAVE = {
    "camada_excecao": "excecao_assinada",
    "camada_declarada": "declarada",
    "camada_classe_parada": "classe_parada(aceleracao tardia)",
    "camada_indecidivel": "indecidivel_sem_piso",
    "camada_metric_colapso": "metric_limited_colapso",
    # ⚠️ ACRESCENTADO 2026-08-16: a `form_limited` ficou em ZERO a sessao
    # inteira e por isso passou despercebida — constante parada e facil de
    # deixar sem guarda. Hoje ela vale 1 e SE MOVE (a correcao de dado db88dcd
    # tirou a lu2024_fig20_T10Nm de metric_limited_colapso e ela caiu aqui), e
    # e a UNICA camada que significa TRABALHO. Um numero que so muda quando ha
    # trabalho novo e exatamente o que nao pode envelhecer em silencio.
    "camada_form_limited": "form_limited",
}


@pytest.fixture(scope="module")
def censo():
    c = _censo()
    cam = _camadas()
    for chave, rotulo in _CAMADA_CHAVE.items():
        c[chave] = cam.get(rotulo, 0)
    c["camadas_soma"] = sum(cam.values())
    return c


def test_a_soma_das_camadas_e_o_fora(censo):
    """As 5 camadas particionam as `fora` — se nao somam, uma sumiu.

    Guarda estrutural: protege contra camada nova que ninguem publicou e
    contra curva que deixa de ser classificada.
    """
    assert censo["camadas_soma"] == censo["fora"], (
        "as camadas somam %d e as `fora` sao %d — a decomposicao deixou de "
        "particionar. Camada nova? Curva sem classificacao?"
        % (censo["camadas_soma"], censo["fora"]))


def _raiz() -> Path:
    from bolt_analysis_studio.validation.inputs import repo_root
    return repo_root()


# -------------------------------------------------- as AFIRMAÇÕES VIGENTES declaradas
#
# (arquivo, rótulo, regex com UM grupo de captura, chave do censo).
# A regex tem de ancorar em texto suficiente para não casar por acidente com um
# número datado da vizinhança.
# `depois_de` existe porque um MESMO rótulo de linha aparece em DUAS tabelas do
# manual: a certificada de 2026-07-27 (régua de 2 pernas, preservada de
# propósito) e a vigente. Sem o recorte de seção, a regex de "fontes fechando
# 100 %" casava a tabela CERTIFICADA — o teste acusou 13 vs 6 e o errado era ele.
# Ancorar por seção, não por linha: registro histórico e afirmação vigente podem
# ter a mesma forma, e é o CONTEXTO que os separa.
_VIVAS = [
    # AS 5 CAMADAS DE ESTATUTO no cabeçalho da MESA (ancoradas 2026-08-15).
    # ⚠️ Cada parcela tem âncora PRÓPRIA — a lição do "perna que MANDA", logo
    # abaixo: proteger o primeiro número de uma afirmação composta não protege
    # os outros, e eles envelhecem juntos. Aqui são CINCO parcelas, e a linha
    # já errou 2 delas em intervalo de 1 h.
    # ⚠️ O LOCALIZADOR não pode repetir um número que a própria linha publica
    # (conserto 2026-08-16). As 3 regexes abaixo travavam em "estatuto das 62";
    # quando o censo andou (143→144, `fora` 62→61) a frase virou "estatuto das
    # 61" e as 3 âncoras se PERDERAM — falha ruidosa, sim, mas pelo motivo
    # errado: o número estava certo e a busca é que envelheceu. O total `fora`
    # tem âncora PRÓPRIA logo abaixo, então trocar por `\d+` aqui não deixa nada
    # sem verificação; só separa "onde está a afirmação" de "quanto ela diz".
    ("New_Theory/DECISOES_PENDENTES.md", "mesa: camada exceção",
     r"estatuto das \d+ — exceção \*\*(\d+)\*\*", "camada_excecao", None),
    ("New_Theory/DECISOES_PENDENTES.md", "mesa: camada declarada",
     r"estatuto das \d+ —[^\n]*· declarada \*\*(\d+)\*\*", "camada_declarada",
     None),
    ("New_Theory/DECISOES_PENDENTES.md", "mesa: camada classe-encerrada",
     r"estatuto das \d+ —[^\n]*· classe-encerrada \*\*(\d+)\*\*",
     "camada_classe_parada", None),
    ("New_Theory/DECISOES_PENDENTES.md", "mesa: camada indecidível",
     r"indecidível-sem-piso \*\*(\d+)\*\* · metric-limited",
     "camada_indecidivel", None),
    ("New_Theory/DECISOES_PENDENTES.md", "mesa: camada metric-limited",
     r"· metric-limited \*\*(\d+)\*\* \(soma", "camada_metric_colapso", None),
    ("New_Theory/DECISOES_PENDENTES.md", "mesa: fila form-limited",
     r"\+ fila \*\*(\d+)\*\* =", "camada_form_limited", None),
    ("CLAUDE.md", "manchete da régua nova",
     r"Na régua nova: \*\*(\d+)/205\*\*", "tripe", None),
    ("CLAUDE.md", "leitura dupla: resolvida/declarada",
     r"resolvida/declarada\s*>?\s*\*\*(\d+)/205\*\*", "declarado_total", None),
    ("docs/MANUAL_BAS_V2/00-relatorio-executivo.md", "vigente: no tripé",
     r"\| curvas no tripé \| \*\*(\d+)\*\* de 205", "tripe",
     "leitura estratégica VIGENTE"),
    ("docs/MANUAL_BAS_V2/00-relatorio-executivo.md", "vigente: só o MAE",
     r"\| violam \*\*só\*\* o MAE \| \*\*(\d+)\*\*", "so_mae",
     "leitura estratégica VIGENTE"),
    # AS 5 CÉLULAS DESCOBERTAS da mesma tabela (ancoradas 2026-08-16 — ver o
    # bloco de medição em `_censo`). Estavam vencidas TODAS, ao lado das quatro
    # vigiadas que estavam certas.
    ("docs/MANUAL_BAS_V2/00-relatorio-executivo.md", "vigente: resolvidos",
     r"\| \*\*resolvidos\*\*[^|]*\| \*\*(\d+)\*\* de 205", "resolvidos",
     "leitura estratégica VIGENTE"),
    ("docs/MANUAL_BAS_V2/00-relatorio-executivo.md", "vigente: só o res.máx",
     r"\| violam \*\*só\*\* o resíduo máximo \| \*\*(\d+)\*\*", "so_mx",
     "leitura estratégica VIGENTE"),
    ("docs/MANUAL_BAS_V2/00-relatorio-executivo.md", "vigente: só o σ_res",
     r"\| violam \*\*só\*\* o σ_res \| \*\*(\d+)\*\*", "so_sd",
     "leitura estratégica VIGENTE"),
    ("docs/MANUAL_BAS_V2/00-relatorio-executivo.md", "vigente: mais de uma perna",
     r"\| violam mais de uma perna \| \*\*(\d+)\*\*", "mais_de_uma",
     "leitura estratégica VIGENTE"),
    ("docs/MANUAL_BAS_V2/00-relatorio-executivo.md", "vigente: 3 maiores fontes",
     r"\| 3 maiores fontes, share do que falta \| \*\*(\d+) %\*\*", "top3_pct",
     "leitura estratégica VIGENTE"),
    ("docs/MANUAL_BAS_V2/00-relatorio-executivo.md", "vigente: perna que manda",
     r"perna que MANDA[^|]*\| \*\*σ_res (\d+) ", "manda_sd",
     "leitura estratégica VIGENTE"),
    # ⚠️ ANCORAGEM PARCIAL DE AFIRMAÇÃO COMPOSTA (medido 2026-08-15): a linha
    # "perna que MANDA" publica TRÊS números e só o σ_res estava ancorado. Foi o
    # mesmo modo de falha da tabela inteira nesta madrugada — 4 células vencidas,
    # 1 vigiada. Uma afirmação composta precisa de âncora por PARCELA: proteger
    # o primeiro número não protege os outros dois, e eles envelhecem juntos com
    # a aparência de estarem cobertos.
    ("docs/MANUAL_BAS_V2/00-relatorio-executivo.md", "vigente: manda MAE",
     r"perna que MANDA[^|]*\| \*\*σ_res \d+ · MAE (\d+) ", "manda_mae",
     "leitura estratégica VIGENTE"),
    ("docs/MANUAL_BAS_V2/00-relatorio-executivo.md", "vigente: manda res.máx",
     r"perna que MANDA[^|]*\| \*\*σ_res \d+ · MAE \d+ · res\.máx (\d+)",
     "manda_mx", "leitura estratégica VIGENTE"),
    # ⚠️ O CABEÇALHO que o cron manda TODA sessão ler publicava `fora` sem
    # guarda. Medido 2026-08-15 na 1ª auditoria de COBERTURA do próprio sistema
    # de guardas: 9 das 14 chaves do censo tinham âncora, e esta era a lacuna
    # com maior exposição — é a linha que decide o que cada retomada acredita.
    ("New_Theory/DECISOES_PENDENTES.md", "cabeçalho: fora do tripé",
     r"censo \*\*\d+/205\*\* · fora \*\*(\d+)\*\*", "fora", None),
    ("docs/MANUAL_BAS_V2/00-relatorio-executivo.md", "vigente: fontes 100%",
     r"\| fontes fechando 100 % \| \*\*(\d+)\*\* de 27", "fontes_100",
     "leitura estratégica VIGENTE"),
    # A FILA DO PROFESSOR (acrescentada 2026-08-14). ⚠️ O buraco que estas duas
    # entradas fecham foi MEDIDO, nao imaginado: o arquivo tem DUAS linhas de
    # "item A" — uma na tabela "o que mudou", outra na tabela DA MESA — e a da
    # mesa ficou parada em "141 de 467" por DEZ fases do backfill enquanto a
    # outra dizia 24. Quem le a fila para decidir le a da MESA. O guarda nao
    # pegou porque cobria so' o que estava ancorado, e aquela linha nao estava.
    # ⇒ a licao geral: guarda de envelhecimento protege o que voce ANCORA; toda
    # linha que carrega numero de decisao precisa de ancora propria.
    ("New_Theory/DECISOES_PENDENTES.md", "cabeçalho: censo vigente",
     r"censo \*\*(\d+)/205\*\*", "tripe", None),
    ("New_Theory/DECISOES_PENDENTES.md", "mesa, item A: passivo de procedência",
     r"→ (?:\*\*)?(\d+)(?:\*\*)? de 467", "prov_sem", "Na mesa do professor"),
    ("New_Theory/MODEL_LEGITIMACY.md", "§8: perna que manda",
     r"\*\*σ_res (\d+) · MAE \d+ · res\.máx", "manda_sd", None),
    ("New_Theory/MODEL_LEGITIMACY.md", "§8: domínio do σ_res",
     r"σ_res domina (\d+)% das \d+ fora", "pct_sd", None),
    # SPLIT DAS FORA (2026-08-07). Estes dois pares mudam a CADA assinatura de
    # estatuto — as P-10/P-11/P-12 os moveram 3x no mesmo dia — e estavam
    # publicados sem invariante. Ancorados nas duas pontas (estatuto E aberta)
    # de propósito: proteger só uma deixaria a outra derivar em silêncio, e a
    # soma tem de fechar em `fora`.
    ("New_Theory/mapa_das_65_fora_resultado.md", "split das fora: com estatuto",
     r"fora do tripé\*\* = \*\*(\d+) com estatuto", "fora_estatuto", None),
    ("New_Theory/mapa_das_65_fora_resultado.md", "split das fora: sem estatuto",
     r"\+\s*\n?\*\*(\d+) sem estatuto", "fora_aberta", None),
    ("New_Theory/censo_por_proposta_resultado.md", "split das fora: com estatuto",
     r"As \d+ fora = (\d+) com estatuto", "fora_estatuto", None),
    ("New_Theory/censo_por_proposta_resultado.md", "split das fora: abertas",
     r"As \d+ fora = \d+ com estatuto \+ (\d+) abertas", "fora_aberta", None),
]


@pytest.mark.parametrize("arquivo,rotulo,padrao,chave,depois_de", _VIVAS,
                         ids=[f"{t[0].split('/')[-1]}:{t[1]}" for t in _VIVAS])
def test_afirmacao_viva_bate_com_o_store(arquivo, rotulo, padrao, chave,
                                         depois_de, censo):
    p = _raiz() / arquivo
    assert p.exists(), f"{arquivo} não existe"
    txt = p.read_text(encoding="utf-8")
    if depois_de:
        i = txt.find(depois_de)
        assert i >= 0, (
            f"SEÇÃO PERDIDA em {arquivo}: o marcador {depois_de!r} não existe "
            f"mais. Sem ele a regex pode casar a tabela histórica em vez da "
            f"vigente — que é exatamente o erro que este mecanismo evita.")
        txt = txt[i:]
    m = re.search(padrao, txt)
    assert m, (
        f"ÂNCORA PERDIDA em {arquivo} ({rotulo}).\n"
        f"A frase foi reescrita e o número deixou de ser verificado. "
        f"Re-aponte a regex em tests/test_meta_numeros_nao_envelhecem.py, "
        f"ou mova a afirmação para registro datado (e retire-a de `_VIVAS`).\n"
        f"regex: {padrao}")
    assert int(m.group(1)) == censo[chave], (
        f"NÚMERO VENCIDO em {arquivo} ({rotulo}): o documento diz "
        f"{m.group(1)}, o store diz {censo[chave]}.\n"
        f"Atualize o documento — não o teste. Se a afirmação passou a ser "
        f"histórica, marque-a como datada e retire-a de `_VIVAS`.")


def test_censo_do_store_e_o_publicado_na_pagina_batem(censo):
    """Ponta a ponta: store -> página. O painel publica o censo num `<b>` com id;
    se a página tiver sido gerada de outro store, isto denuncia."""
    pag = _raiz() / "New_Theory" / "validation_html" / "validation_report.html"
    if not pag.exists():
        pytest.skip("report mestre não gerado neste checkout")
    txt = pag.read_text(encoding="utf-8")
    m = re.search(r'id="tri-n">(\d+)</b>', txt)
    assert m, "o contador do tripé (#tri-n) saiu da página"
    assert int(m.group(1)) == censo["tripe"], (
        f'a página publica {m.group(1)} no tripé e o store diz {censo["tripe"]}'
        " — regenere o report (python -m bolt_analysis_studio.validation.report)")


def test_a_soma_do_censo_fecha(censo):
    """Invariante aritmético: quem manda + quem passa = o total. Se um dia
    `_perna_manda` devolver uma 4ª categoria, isto quebra antes de virar número
    publicado."""
    assert (censo["manda_sd"] + censo["manda_mae"] + censo["manda_mx"]
            + censo["tripe"]) == censo["n"]
    assert censo["fora"] == censo["n"] - censo["tripe"]


def test_limites_da_meta_nao_tem_literal_solto_no_report():
    """Os três limites só podem vir de `META_*`. O report por caso julgava o MAE
    contra `0.1` literal (régua de duas pernas) meses depois da troca — cartão
    verde em curva reprovada no mestre."""
    import bolt_analysis_studio.validation.report_html as R
    src = Path(R.__file__).read_text(encoding="utf-8")
    # tira comentários e docstrings-de-uma-linha do rastreio: eles CITAM o
    # literal ao explicar o defeito, e proibir a citação proibiria a memória
    codigo = "\n".join(l for l in src.splitlines()
                       if not l.lstrip().startswith("#"))
    for proibido in ('<= 0.1 else', '> 0.1 else', 'alvo 0.1"',
                     '(&#8804;0.1)'):
        assert proibido not in codigo, (
            f"literal de régua antiga no código: {proibido!r} — use META_MAE/"
            f"META_MAX/META_SRES")


def test_regua_declarada_e_a_de_tres_pernas():
    """Guarda de sanidade: se alguém mexer nas constantes, os documentos que
    este arquivo policia passam a estar errados em bloco — e é melhor falhar
    aqui, com a explicação, que numa comparação de número solto."""
    import bolt_analysis_studio.validation.report_html as R
    assert (R.META_MAX, R.META_MAE, R.META_SRES) == (0.10, 0.05, 0.025), (
        "as constantes da meta mudaram. Isto NÃO é um teste a consertar: "
        "atualize os documentos vivos (a lista está em `_VIVAS` neste arquivo) "
        "e só então ajuste esta guarda, no MESMO commit.")
