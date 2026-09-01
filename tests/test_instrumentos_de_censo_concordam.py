# -*- coding: utf-8 -*-
"""Os DOIS instrumentos de censo têm de concordar sobre o que é fila de trabalho.

## Por que este arquivo existe

Em 2026-08-14 o `New_Theory/censo_por_proposta.py` — o script que o **cron** manda
rodar para decidir onde trabalhar — reportava **19 ABERTAS** enquanto a triagem
canônica reportava **0 form-limited**. A causa era uma linha:

    tem = cid in rh._EXCECOES or cid in rh._DECLARADAS

DUAS camadas de estatuto num sistema que hoje tem CINCO. As curvas de
`classe_parada`, `metric_limited_colapso` e `indecidivel_sem_piso` caíam em
"ABERTAS", e quem lesse a saída concluiria que havia 19 curvas acionáveis.

⚠️ O cabeçalho daquele arquivo documenta, com precisão, o §4.43 que ele foi feito
para evitar (re-medir a PERTINÊNCIA contra o store) — e faz isso certo. Ele
envelheceu num eixo que o autor não previu: não a LISTA de curvas, e sim o
VOCABULÁRIO de estatuto. **Guardar contra uma forma de envelhecimento não guarda
contra as outras**, e é por isso que a guarda aqui é sobre o ACORDO entre os
instrumentos, não sobre nenhum número em particular.

## O que se protege

1. ESTRUTURAL — o script não pode voltar a reimplementar a regra de estatuto; ele
   tem de importar o classificador canônico. Estrutural porque a regressão é
   SILENCIOSA: ela devolve um número plausível (19), não um erro.
2. COMPORTAMENTAL — a contagem de "abertas" do script tem de bater, curva a
   curva, com a contagem de `form_limited` da triagem sobre a mesma população.
"""
from __future__ import annotations

import io
import json
import sys
from pathlib import Path

import pytest

_RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_RAIZ / "src"))
sys.path.insert(0, str(_RAIZ / "New_Theory"))

_SCRIPT = _RAIZ / "New_Theory" / "censo_por_proposta.py"
_MAPA = _RAIZ / "New_Theory" / "mapa_das_65_fora.json"


def test_nao_reimplementa_a_regra_de_estatuto():
    """A regressão de 2026-08-14, presa por estrutura.

    Comportamental não basta aqui: se alguém reintroduzir a checagem de duas
    camadas, o script volta a publicar um número PLAUSÍVEL. Foi por ser
    plausível que o defeito sobreviveu semanas.
    """
    txt = io.open(_SCRIPT, encoding="utf-8").read()
    assert "from regra_de_parada_triagem import" in txt and "classificar" in txt, (
        "censo_por_proposta.py deixou de importar o classificador canonico da "
        "triagem. A regra de estatuto NAO pode ser reimplementada ali — foi "
        "exatamente isso que fez o script publicar 19 'abertas' onde havia 0.")
    # ⚠️ COMENTARIOS FORA antes de procurar. A 1a versao deste teste falhou
    # contra o arquivo JA CONSERTADO, porque a expressao proibida aparece no
    # comentario que DOCUMENTA o defeito. Um grep de fonte nao distingue codigo
    # de comentario sobre o codigo — e o comentario tem de ficar, porque a
    # regressao e' silenciosa e o proximo leitor precisa saber por que.
    codigo = "\n".join(l.split("#", 1)[0] for l in txt.splitlines())
    compacto = "".join(codigo.split())
    assert "cidinrh._EXCECOESorcidinrh._DECLARADAS" not in compacto, (
        "voltou a checagem de DUAS camadas de estatuto. O sistema tem cinco: "
        "excecao_assinada, declarada, classe_parada, metric_limited_* e "
        "indecidivel_sem_piso. Use `classificar()` da triagem.")


def test_abertas_do_script_batem_com_form_limited_da_triagem():
    """Acordo curva a curva sobre o que é fila de trabalho.

    Não fixa NENHUM número: fixa que os dois instrumentos, sobre a MESMA
    população (as curvas do mapa congelado), nomeiam o mesmo conjunto.
    """
    if not _MAPA.exists():
        pytest.skip("mapa_das_65_fora.json ausente")
    import regra_de_parada_triagem as T
    import bolt_analysis_studio.validation.report_html as rh
    from bolt_analysis_studio.validation import case_registry as cr
    from bolt_analysis_studio.validation.runner import CaseResult

    store = json.loads(T.STORE.read_text(encoding="utf-8"))
    recs = {r.case_id: r for r in cr.all_records()}
    pisos = T.pisos_medidos(store, recs)
    exc = set(rh._EXCECOES)

    def fora(cid: str) -> bool:
        """Regra canônica do censo, pelos helpers — nunca reimplementada.

        ⚠️ `sres_para_censo` recebe um CaseResult, NÃO o dict cru do store. Com
        o dict ela devolve None em tudo e a sonda acusa '205 de 205 fora' — erro
        cometido em 2026-08-14 na própria conferência deste conserto.
        """
        raw = store[cid]
        if not raw.get("ok") or cid not in recs:
            return False
        if not rh.caso_comparavel(recs[cid].source, cid):
            return False
        r = CaseResult.from_dict(raw)
        sd = rh.sres_para_censo(r)
        return not (sd is not None
                    and r.maxerr <= rh.META_MAX and r.mae <= rh.META_MAE
                    and sd <= rh.limite_sres(recs[cid].source, pisos))

    # ⚠️ A 1a versao deste teste computava os DOIS lados com codigo identico —
    # comparava uma coisa consigo mesma e teria passado com o defeito de volta.
    # E' a armadilha "Delta=0 era instrumento morto", agora no teste. O lado do
    # SCRIPT tem de vir do SCRIPT: roda-se de verdade e le-se a saida.
    import subprocess

    mapa = [L["cid"] for L in json.loads(_MAPA.read_text(encoding="utf-8"))]
    esperado = sum(
        1 for cid in mapa
        if cid in store and fora(cid)
        and T.classificar(cid, store[cid], recs[cid].source,
                          T.piso_da_fonte(pisos, recs[cid].source),
                          exc) == "form_limited")

    env = dict(**{k: v for k, v in __import__("os").environ.items()})
    env["PYTHONPATH"] = str(_RAIZ / "src")
    env["PYTHONIOENCODING"] = "utf-8"
    # ⚠️ `text=True` sozinho decodifica no encoding do LOCALE (cp1252 no
    # Windows) e o script imprime "⚠️" e "·" => UnicodeDecodeError dentro do
    # subprocess e stdout None. Encoding explicito.
    saida = subprocess.run([sys.executable, str(_SCRIPT)], cwd=str(_RAIZ),
                           capture_output=True, env=env, timeout=900,
                           encoding="utf-8", errors="replace")
    assert saida.returncode == 0, f"o script falhou:\n{saida.stderr[-1500:]}"

    import re
    m = re.search(r"ABERTAS\s+(\d+)", saida.stdout)
    if m is None:                      # formato antigo: linha de total
        m = re.search(r"ABERTAS\s*(\d+)\s*$", saida.stdout, re.M)
    assert m, ("nao achei a contagem de ABERTAS na saida do script — o formato "
               f"mudou:\n{saida.stdout[-800:]}")
    obtido = int(m.group(1))
    assert obtido == esperado, (
        f"o script publica {obtido} ABERTAS e a triagem canonica nomeia "
        f"{esperado} form-limited sobre a MESMA populacao. Foi exatamente esta "
        "divergencia (19 x 0) que o conserto de 2026-08-14 fechou.")


def test_toda_curva_fora_recebe_uma_camada_conhecida():
    """Nenhuma curva pode ficar sem estatuto NOMEADO.

    Se aparecer camada nova (ou o classificador devolver algo inesperado), o
    censo publicado passa a somar categorias que os documentos não descrevem.
    """
    import regra_de_parada_triagem as T
    import bolt_analysis_studio.validation.report_html as rh
    from bolt_analysis_studio.validation import case_registry as cr
    from bolt_analysis_studio.validation.runner import CaseResult

    store = json.loads(T.STORE.read_text(encoding="utf-8"))
    recs = {r.case_id: r for r in cr.all_records()}
    pisos = T.pisos_medidos(store, recs)
    exc = set(rh._EXCECOES)
    conhecidas = {"excecao_assinada", "declarada",
                  "classe_parada(aceleracao tardia)", "metric_limited_n_baixo",
                  "metric_limited_colapso", "data_limited_piso",
                  "indecidivel_sem_piso", "form_limited"}

    vistas = set()
    for cid, raw in store.items():
        if not raw.get("ok") or cid not in recs:
            continue
        if not rh.caso_comparavel(recs[cid].source, cid):
            continue
        r = CaseResult.from_dict(raw)
        sd = rh.sres_para_censo(r)
        if (sd is not None and r.maxerr <= rh.META_MAX and r.mae <= rh.META_MAE
                and sd <= rh.limite_sres(recs[cid].source, pisos)):
            continue
        src = recs[cid].source
        vistas.add(T.classificar(cid, raw, src, T.piso_da_fonte(pisos, src), exc))

    assert vistas, "nenhuma curva fora do tripe — o teste nao testou nada"
    assert vistas <= conhecidas, (
        f"camada de estatuto NAO documentada: {sorted(vistas - conhecidas)}. "
        "Atualize a lista aqui E os documentos vivos no mesmo commit.")


def test_forma_nomeada_nao_tem_citacao_muda():
    """O documento citado tem de NOMEAR a curva, nao so existir.

    A guarda irma ja exige que o arquivo exista. Isso nao basta: um doc pode
    ser citado para uma curva que ele nunca menciona, e a citacao vira
    decorativa — ninguem consegue ir da entrada ate a prova.

    Medido em 2026-08-16: 3 das 21 citacoes eram MUDAS, e eram as MINHAS
    (`yang2023_piso_nunca_lido.md` descrevia as curvas so por amplitude,
    "0,30 / 0,35 / 0,50 mm", sem escrever nenhum case_id). Mesma classe do
    problema das excecoes sem trio conferivel: prova que nao se amarra ao
    sujeito.

    Aceita o `case_id` inteiro OU o sufixo distintivo (os cids sao longos e a
    prosa costuma abreviar) — a barra e "da para achar a curva no doc", nao
    "o doc repete a string exata".
    """
    import re
    import inspect
    import regra_de_parada_triagem as T

    src = inspect.getsource(T.main)
    m = re.search(r"_FORMA_NOMEADA = \{(.*?)\}", src, re.S)
    assert m, "`_FORMA_NOMEADA` sumiu de `regra_de_parada_triagem.main`."
    pares = re.findall(r'"([a-zA-Z0-9_.]+)":\s*"([^"]+)"', m.group(1), re.S)
    assert pares, "nao consegui ler os pares (cid, doc) — o formato mudou."

    raiz = Path(__file__).resolve().parents[1] / "New_Theory"
    mudas = []
    for cid, doc in pares:
        f = raiz / doc
        txt = f.read_text(encoding="utf-8", errors="replace") if f.exists() else ""
        if cid in txt:
            continue
        suf3 = "_".join(cid.split("_")[-3:])
        suf2 = "_".join(cid.split("_")[-2:])
        if suf3 in txt or suf2 in txt:
            continue
        mudas.append((cid, doc))

    assert not mudas, (
        "citacao MUDA — o doc nao nomeia a curva:\n  %s\n"
        "Escreva o `case_id` no documento (numa tabela, no titulo de secao, "
        "onde for). Descrever a curva so por amplitude/torque deixa a prova "
        "impossivel de amarrar ao sujeito."
        % "\n  ".join("%s -> %s" % x for x in mudas))


def test_forma_nomeada_sem_chave_duplicada():
    """⚠️ Um dict Python COLAPSA chave repetida — a guarda abaixo nao a ve.

    Medido em 2026-08-16: acrescentei `lu2024_M8_fig20_T10Nm` a
    `_FORMA_NOMEADA` sem notar que a sessao paralela ja a tinha posto. O
    numero publicado NAO se moveu (18 -> 18) e nada falhou: o dict tinha 18
    entradas para 19 linhas de fonte, e a duplicata ficou invisivel.

    E a MESMA classe do incidente do `adopted_configs.json` (mesmo dia, de
    manha), ja registrada nos gotchas do CLAUDE.md: `json.loads` tambem nao
    reclama de chave repetida. La foi a MINHA escrita que sumiu; aqui foi a
    minha ENTRADA que sumiu. Nos dois casos o arquivo seguia valido.

    ⚠️ Por que este teste le o FONTE e nao o dict: pelo dict e IMPOSSIVEL
    detectar — ele ja colapsou. A deteccao tem de acontecer antes do parse.
    E o mesmo motivo pelo qual `test_nao_reimplementa_a_regra_de_estatuto`
    e estrutural.

    Sintoma que denuncia sem o teste: um numero publicado que NAO SE MOVE
    depois de uma adicao que deveria move-lo. Se isso acontecer, suspeite de
    duplicata antes de suspeitar da regra.
    """
    import re
    import inspect
    from collections import Counter
    import regra_de_parada_triagem as T

    src = inspect.getsource(T.main)
    m = re.search(r"_FORMA_NOMEADA = \{(.*?)\}", src, re.S)
    assert m, ("`_FORMA_NOMEADA` sumiu de `regra_de_parada_triagem.main` — a "
               "2a linha da fila foi removida sem passar por aqui.")
    chaves = re.findall(r'"([a-zA-Z0-9_.]+)":', m.group(1))
    dup = sorted(k for k, v in Counter(chaves).items() if v > 1)
    assert not dup, (
        "chave(s) DUPLICADA(s) em `_FORMA_NOMEADA`: %s.\n"
        "O dict colapsa e o numero publicado nao se move — a adicao some em "
        "silencio. Remova o bloco redundante (comentario incluido) e mantenha "
        "o que veio primeiro; se a sua medicao acrescenta algo, escreva-a como "
        "COMPLEMENTO no comentario da entrada existente." % dup)


def test_forma_nomeada_e_declaracao_honesta():
    """A 2a linha da fila (assinada 2026-08-15 20:04) nao pode apodrecer.

    `_FORMA_NOMEADA` responde "ja sabemos o que consertar?" para curvas que o
    rotulo `form_limited` NUNCA alcanca — porque `indecidivel_sem_piso` precede
    `form_limited` e curva de fonte sem piso e' barrada por construcao (55 das
    205; medido em `fila_zero_e_parcialmente_estrutural.md`).

    Tres invariantes, cada um contra um modo de apodrecer diferente:
      (a) toda chave e' um case_id REAL — senao a linha conta fantasma;
      (b) toda chave esta de fato FORA e SEM estatuto assinado — se a curva
          fechar por merito, ou receber assinatura, ela sai da 2a linha e
          manter isso aqui infla o numero;
      (c) todo documento citado EXISTE — prova que ninguem consegue abrir nao
          e' prova (licao das 20 excecoes sem trio conferivel).
    """
    import regra_de_parada_triagem as T
    import bolt_analysis_studio.validation.report_html as rh
    from bolt_analysis_studio.validation import case_registry as cr
    from bolt_analysis_studio.validation.runner import CaseResult
    import inspect
    import re

    src_txt = inspect.getsource(T.main)
    m = re.search(r"_FORMA_NOMEADA = \{(.*?)\}", src_txt, re.S)
    assert m, ("`_FORMA_NOMEADA` sumiu de `regra_de_parada_triagem.main` — a 2a "
               "linha da fila foi removida sem passar por aqui.")
    chaves = re.findall(r'"([^"]+)":\s*"([^"]+)"', m.group(1))
    assert chaves, "`_FORMA_NOMEADA` esta vazio; se for intencional, ajuste este teste."

    store = json.loads(T.STORE.read_text(encoding="utf-8"))
    recs = {r.case_id: r for r in cr.all_records()}
    pisos = T.pisos_medidos(store, recs)
    raiz = Path(__file__).resolve().parents[1]

    fantasma, fechadas, assinadas, sem_doc = [], [], [], []
    for cid, doc in chaves:
        rec = recs.get(cid)
        if rec is None or cid not in store:
            fantasma.append(cid)
            continue
        r = CaseResult.from_dict(store[cid])
        sd = rh.sres_para_censo(r)
        srcn = str(rec.source)
        if (r.mae is not None and r.maxerr is not None and sd is not None
                and r.mae <= rh.META_MAE and r.maxerr <= rh.META_MAX
                and sd <= rh.limite_sres(srcn, pisos)):
            fechadas.append(cid)
        if cid in rh._EXCECOES or cid in rh._DECLARADAS:
            assinadas.append(cid)
        if not (raiz / "New_Theory" / doc).exists():
            sem_doc.append((cid, doc))

    assert not fantasma, ("case_id inexistente em `_FORMA_NOMEADA`: %s — a 2a "
                          "linha da fila estaria contando fantasma."
                          % fantasma)
    assert not fechadas, ("estas FECHARAM o tripé e seguem em `_FORMA_NOMEADA`: "
                          "%s. Tire-as: a 2a linha conta trabalho ABERTO."
                          % fechadas)
    assert not assinadas, ("estas ganharam estatuto ASSINADO e seguem em "
                           "`_FORMA_NOMEADA`: %s. Exceção/declaração e forma "
                           "nomeada são leituras distintas, mas a 2a linha diz "
                           "'SEM estatuto assinado' — some as duas e o número "
                           "mente." % assinadas)
    assert not sem_doc, ("prova que ninguém abre não é prova — documento "
                         "ausente: %s" % sem_doc)


def test_o_ponto_cego_do_mapa_congelado_nao_esconde_trabalho():
    """⚠️ O `censo_por_proposta` roda sobre um MAPA CONGELADO, nao sobre o store.

    Ele sempre reportou as que FECHARAM desde o mapa; nunca as que estao fora
    HOJE e o mapa nao conhece. A assimetria mostrava progresso e escondia
    crescimento — vies errado num relatorio de COBERTURA de proposta.

    Medido em 2026-08-15: mapa 66 · fora hoje 62 · interseccao 56 · fecharam 10
    · ausentes do mapa **6** (5 do `DEMIR_2024`, fonte posterior ao mapa, e a
    `lu2024_fig18_amp1p5`). O script passou a imprimir as duas direcoes.

    Este teste prende o que de fato importa: **nenhuma ausente pode ser
    `form_limited`**. Ausente com estatuto e' escrituracao atrasada; ausente que
    e' FILA DE TRABALHO e' trabalho que nenhuma proposta cobre e que ninguem
    esta vendo.

    Se falhar, o conserto NAO e' relaxar aqui — e' re-gerar
    `mapa_das_65_fora.json` e re-atribuir as curvas novas a propostas.
    """
    import regra_de_parada_triagem as T
    import bolt_analysis_studio.validation.report_html as rh
    from bolt_analysis_studio.validation import case_registry as cr
    from bolt_analysis_studio.validation.runner import CaseResult

    store = json.loads(T.STORE.read_text(encoding="utf-8"))
    recs = {r.case_id: r for r in cr.all_records()}
    pisos = T.pisos_medidos(store, recs)
    exc = set(rh._EXCECOES)
    mapa = {L["cid"] for L in json.loads(
        (Path(__file__).resolve().parents[1] / "New_Theory"
         / "mapa_das_65_fora.json").read_text(encoding="utf-8"))}

    orfas_fl = []
    for cid, raw in store.items():
        if not raw.get("ok") or cid not in recs or cid in mapa:
            continue
        src = recs[cid].source
        if not rh.caso_comparavel(src, cid):
            continue
        r = CaseResult.from_dict(raw)
        sd = rh.sres_para_censo(r)
        if (sd is not None and r.maxerr <= rh.META_MAX and r.mae <= rh.META_MAE
                and sd <= rh.limite_sres(src, pisos)):
            continue
        if T.classificar(cid, raw, src,
                         T.piso_da_fonte(pisos, src), exc) == "form_limited":
            orfas_fl.append(cid)

    assert not orfas_fl, (
        "estas curvas sao FILA DE TRABALHO (`form_limited`) e estao FORA do "
        "mapa congelado, logo nenhuma proposta as cobre e o "
        "`censo_por_proposta` nao as contava:\n  %s\n"
        "Re-gere `mapa_das_65_fora.json` e atribua-as a propostas."
        % "\n  ".join(sorted(orfas_fl)))
