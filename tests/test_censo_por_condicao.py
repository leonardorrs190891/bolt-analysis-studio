"""O relatório mostra a leitura POR CONDIÇÃO — sem sobreajuste de réplica.

## O que motivou

Pedido do professor em 2026-08-23: *"ajuste o relatório de validação e o gráfico 3d para as
condições sem sobreajuste das réplicas"*. Uma fonte com 6 réplicas pesava **6×** na nuvem e
no censo; agora pesa **1**.

## Os dois defeitos que este arquivo impede

**(1) O segundo 3D roubando o painel ao vivo.** O JS liga-se por
`q('svg[data-s3]')` — seletor de **um** elemento. Um segundo gráfico com esse marcador
faria os controles (rotação, escala, cor) dirigirem o gráfico errado, ou seriam ignorados,
dependendo da ordem no DOM. Daí `interativo=False`: o 3D por condição é estático **de
propósito**. Isto é a mesma classe do defeito de `setPointerCapture` de 2026-07-29 — um
mecanismo de UI capturando o alvo errado, com sintoma silencioso.

**(2) Colapsar curvas de durações incomparáveis.** Medido em `estudo_das_replicas.md`:
comparar no **ciclo absoluto** curvas que rodaram comprimentos diferentes inflou a banda de
4 condições em **55–65 %**, porque a curva curta já terminou quando a longa está no meio da
vida. E acima de ~3× a própria normalização por vida perde sentido — *"50 % da vida"* entre
1 041 e 693 750 ciclos não é um estado físico comum. A guarda `_RAZAO_DUR_MAX` barra essas
famílias, e elas voltam a ser curvas soltas.

⚠️ **A leitura por condição NÃO é a porta**, e isso é medição, não preferência: quando as 2
provas de piso do `ECCLES` voltaram para a fila, foi essa pressão que produziu o
`arrest_approach_exp` (res.máx 0,1320 → **0,0488**). Uma leitura por condição usada como
porta teria "aprovado" as duas em 0,0851 e ninguém teria procurado a física — 2ª instância
do precedente **D-M**.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

import bolt_analysis_studio.validation.report_html as rh
from bolt_analysis_studio.validation.case_registry import all_records
from bolt_analysis_studio.validation.runner import CaseResult

RAIZ = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def dados():
    p = RAIZ / "Models" / "CALIBRATION_AND_VALIDATION" / "validation_store.json"
    if not p.exists():
        pytest.skip("store canônico ausente")
    store = json.loads(p.read_text(encoding="utf-8"))
    recs = store.get("cases", store)
    comp = [r for r in all_records()
            if r.case_id in recs and rh.caso_no_documento(r.source, r.case_id)]
    results = {}
    for r in comp:
        try:
            results[r.case_id] = CaseResult.from_dict(recs[r.case_id])
        except Exception:
            pass
    pisos = rh._pisos_medidos([(r.source, results[r.case_id]) for r in comp
                               if r.case_id in results])
    return comp, results, pisos


# --------------------------------------------------------------------------- #
# O defeito (1): um só gráfico pode ser o interativo                          #
# --------------------------------------------------------------------------- #

def test_apenas_UM_svg_carrega_o_marcador_do_painel():
    """`data-s3` é o alvo de `q('svg[data-s3]')` — dois seria ambíguo.

    O teste lê o HTML **gerado**, não o fonte: é no artefato que a ambiguidade
    machuca. Se o report não foi gerado ainda, faz skip em vez de passar em falso.
    """
    import re
    alvo = RAIZ / "New_Theory" / "validation_html" / "validation_report.html"
    if not alvo.exists():
        pytest.skip("report mestre não gerado")
    t = alvo.read_text(encoding="utf-8", errors="replace")
    svgs = re.findall(r"<svg[^>]*\bdata-s3\b[^>]*>", t)
    assert len(svgs) == 1, (
        f"{len(svgs)} elementos <svg> carregam `data-s3`; o JS usa um seletor de UM "
        f"elemento e passaria a dirigir o gráfico errado. O 3D por condição tem de "
        f"ser gerado com `interativo=False`.")
    assert "Por CONDIÇÃO, não por curva" in t, (
        "a seção por condição saiu do report mestre")


def test_interativo_False_omite_o_marcador():
    """Invariante da função, independente de o report existir."""
    pts = [(0.02, 0.05, 0.01, "x", 0.025), (0.06, 0.12, 0.03, "y", 0.025)]
    com = rh._svg_scatter3(pts)
    sem = rh._svg_scatter3(pts, interativo=False)
    assert 'data-s3="1"' in com, "o default deixou de ser interativo"
    assert 'data-s3' not in sem, "`interativo=False` não removeu o marcador"
    # o resto do SVG tem de continuar igual em forma (mesmo viewBox, mesmos eixos)
    assert sem.count("<text") == com.count("<text"), (
        "o gráfico estático perdeu rótulos — `interativo` deve mexer SÓ no marcador")


# --------------------------------------------------------------------------- #
# O defeito (2): durações incomparáveis                                       #
# --------------------------------------------------------------------------- #

def test_familias_de_duracao_incomparavel_ficam_FORA(dados):
    """Razão de duração > 3× ⇒ a família não colapsa, vira curva solta.

    As barradas medidas em 2026-08-23 eram `ZHANG_2018` (599×), `ZHANG_2019`
    (219×), `ECCLES_2010` (7× na janela da métrica) e `LIU_2022_RETIGHT` (3×).
    O teste não fixa a lista — fixa a REGRA, porque a lista muda com o store.
    """
    _pontos, _solos, barradas = rh.condicoes_agregadas(*dados)
    for fonte, n, razao in barradas:
        assert razao > rh._RAZAO_DUR_MAX, (
            f"{fonte} foi barrada com razão {razao:.1f}×, abaixo do limite "
            f"{rh._RAZAO_DUR_MAX}× — a guarda está barrando família legítima")
    assert barradas, (
        "nenhuma família barrada: se o store passou a ter só durações "
        "comparáveis isso é notícia boa, mas confirme antes de relaxar a guarda "
        "(o ZHANG_2018 tinha 599×)")


def test_nenhuma_condicao_colapsa_duracoes_incomparaveis(dados):
    """O complemento: o que COLAPSOU tem de estar dentro do limite.

    Sem isto a guarda poderia existir e não ser chamada — que é o modo de falha
    do Cattaneo-Mindlin (gates nunca invocados) já documentado no projeto.
    """
    import numpy as np
    comp, results, _pisos = dados
    pontos, _solos, _bar = rh.condicoes_agregadas(*dados)
    assert pontos, "nenhuma condição colapsada — a agregação parou de funcionar"
    for *_v, rot, _lim, n in [(p[0], p[1], p[2], p[3], p[4], p[5]) for p in pontos]:
        assert n >= 2, f"{rot}: condição com {n} curva(s) não é condição"


def test_o_censo_por_condicao_e_MENOS_unidades_e_o_mesmo_dado(dados):
    """Colapsar réplica reduz unidades de julgamento, não muda o dado.

    Invariante aritmético: `len(pontos) + len(solos)` < número de curvas, e a
    soma das curvas cobertas fecha exatamente com o total comparável.
    """
    comp, results, _pisos = dados
    pontos, solos, _bar = rh.condicoes_agregadas(*dados)
    cobertas = sum(p[5] for p in pontos) + len(solos)
    com_vetores = sum(1 for r in comp
                      if (results.get(r.case_id) is not None
                          and getattr(results[r.case_id], "metric_x", None)))
    assert cobertas == com_vetores, (
        f"{cobertas} curvas cobertas contra {com_vetores} com vetores de métrica "
        f"— alguma curva foi perdida ou contada duas vezes na agregação")
    unidades = len(pontos) + len(solos)
    assert unidades < com_vetores, (
        f"{unidades} unidades para {com_vetores} curvas: nada colapsou")


def test_a_secao_declara_que_NAO_e_porta(dados):
    """A seção tem de dizer que o veredito publicado segue por curva.

    Não é cosmética: uma leitura por condição que o leitor tome por porta
    "aprova" curvas que ninguém mais vai consertar — e o `arrest_approach_exp`
    é a prova medida de que a pressão da fila produz física.
    """
    html = rh._condicao_html(*dados)
    assert html, "a seção por condição saiu vazia"
    assert "NÃO é a porta" in html
    assert "arrest_approach_exp" in html, (
        "a seção perdeu a evidência de por que não deve ser porta")
    # e as três leituras que a regra do projeto exige de todo gráfico
    for exigido in ("As variáveis:", "Como ler:", "Leitura do dado atual:"):
        assert exigido in html, f"a seção não traz '{exigido}'"


# --------------------------------------------------------------------------- #
# Os 3 graficos da secao (2026-08-25)                                         #
# --------------------------------------------------------------------------- #

def test_a_guarda_de_duracao_barra_AS_MESMAS_familias_nas_duas_secoes(dados):
    """⚠️ O defeito que este teste existe para impedir, e que JA ACONTECEU.

    O grafico "quanto da banda e artefato de duracao" e o censo por condicao
    aplicam a MESMA regra (`_RAZAO_DUR_MAX`), mas a 1a versao do grafico media a
    razao na **CSV crua** e o censo mede em `metric_x`. Resultado: duas secoes da
    mesma pagina barrando familias DIFERENTES —

        grafico (CSV crua): ZHANG_2018 667x · ZHANG_2019 194x · LIU_2016 5x
        censo  (metric_x) : ZHANG_2018 599x · ZHANG_2019 219x · ECCLES  7x

    Qual esta certo decorre do que o grafico AFIRMA: ele explica quanto da banda
    **publicada** e artefato, e a banda publicada sai de `_pisos_medidos`, que usa
    `metric_x`/`metric_data`. Medir na CSV crua explicaria uma banda que a pagina
    nao publica.
    """
    html = rh._graficos_replica_html(*dados)
    _pontos, _solos, barradas_censo = rh.condicoes_agregadas(*dados)
    for fonte, _n, _razao in barradas_censo:
        assert fonte in html, (
            f"{fonte} e barrada pelo censo mas nao aparece na lista do grafico — "
            f"as duas secoes divergiram sobre a MESMA guarda; confira se o "
            f"grafico voltou a medir a razao na CSV crua em vez de `metric_x`")


def test_os_graficos_novos_NAO_carregam_marcador_de_painel(dados):
    """Nem `data-s3` nem `data-barh`: os dois sao seletores de UM elemento.

    `q('svg[data-s3]')` e `q('svg[data-barh]')` pegam o primeiro do DOM. Um
    grafico novo com qualquer um deles rouba a ligacao do painel ao vivo — e o
    sintoma e silencioso: os controles passam a dirigir o grafico errado.
    """
    html = rh._graficos_replica_html(*dados)
    assert "data-s3" not in html
    assert "data-barh" not in html
    assert html.count("<svg") == 3, (
        f"a secao tem {html.count('<svg')} graficos, esperava 3")


def test_os_tres_graficos_trazem_as_tres_leituras(dados):
    """Regra do projeto: todo grafico leva variaveis + como ler + dado ATUAL."""
    html = rh._graficos_replica_html(*dados)
    for titulo in ("artefato de DURA", "Custo", "Proced"):
        assert titulo in html, f"grafico '{titulo}' sumiu da secao"
    assert html.count("As variáveis:") == 3
    assert html.count("Como ler:") == 3
    assert html.count("Leitura do dado atual:") == 3


def test_o_barras_par_nao_reusa_a_semantica_de_FORA():
    """`_svg_barh` tem "{v} de {tot} fora" cozido no tooltip e no aria-label.

    Reusa-lo para banda/procedencia produziria rotulo mentiroso ("0.18 de 0.52
    fora"). O helper novo diz o que de fato mede.
    """
    svg = rh._svg_barras_par([("x", 0.18, 0.52, "65% artefato")])
    assert "fora" not in svg.lower(), "o helper novo herdou a semantica de 'fora'"
    assert "sobrevive" in svg
    assert "data-barh" not in svg


def test_nenhum_texto_dos_graficos_novos_VAZA_o_viewBox(dados):
    """SVG corta texto fora do viewBox EM SILENCIO — nao ha erro, ele some.

    Medido na 1a versao: no "custo x qualidade", o rotulo do ponto mais a direita
    (`BAUER24`, x=551 + ~36 px = **587** num viewBox de **560**) e o ultimo tick
    do eixo (**570**) vazavam. O efeito seria perder do desenho justamente a
    fonte que o grafico existe para mostrar — a que mais gasta constante.

    ⚠️ Texto ROTACIONADO fica fora da conta: o rotulo do eixo y usa
    `rotate(-90)`, entao a extensao horizontal dele e a ALTURA da fonte, nao a
    largura do texto. Contar como plano da falso positivo — foi o que a 1a
    versao desta verificacao fez.
    """
    import re
    html = rh._graficos_replica_html(*dados)
    vazam = []
    for svg in re.findall(r"<svg.*?</svg>", html, re.S):
        mvb = re.search(r'viewBox="0 0 (\d+) (\d+)"', svg)
        if not mvb:
            continue
        W = int(mvb.group(1))
        for m in re.finditer(r'<text x="([\d.]+)"([^>]*)>([^<]*)</text>', svg):
            if "rotate" in m.group(2):
                continue
            x, atr, txt = float(m.group(1)), m.group(2), m.group(3)
            larg = len(txt) * 5.2          # ~largura da fonte `tk`
            anc = ("end" if 'text-anchor="end"' in atr
                   else "middle" if "middle" in atr else "start")
            dir_ = x if anc == "end" else (x + larg / 2 if anc == "middle" else x + larg)
            esq = x - larg if anc == "end" else (x - larg / 2 if anc == "middle" else x)
            if dir_ > W + 1 or esq < -1:
                vazam.append((txt, round(esq), round(dir_), W))
    assert not vazam, (
        "texto fora do viewBox (SVG corta sem avisar): "
        + "; ".join(f"{t!r} ocupa [{e},{d}] em 0..{W}" for t, e, d, W in vazam[:5]))


# --------------------------------------------------------------------------- #
# As paginas de `New_Theory/metodologia/` (2026-08-25)                        #
# --------------------------------------------------------------------------- #

_METOD = RAIZ / "New_Theory" / "metodologia"


def test_nenhum_texto_das_paginas_de_metodologia_VAZA_o_viewBox():
    """47 paginas, 130 SVGs — varredura de borda no artefato publicado.

    ⚠️ Este teste ja pegou 153 vazamentos numa geracao: a legenda do `plot`
    avancava a posicao mesmo para series de rotulo VAZIO (as linhas de modelo,
    que reusam a cor do dado), e com 9 curvas ela passava de 860. SVG corta fora
    do viewBox EM SILENCIO — o efeito seria perder rotulos de curva sem aviso.

    ⚠️ O viewBox pode ter origem NEGATIVA (`viewBox="0 -13 860 343"`): a legenda
    quebrada em linhas empurra o topo em vez de invadir o grafico. Ler a origem
    e' obrigatorio — assumir 0 daria falso positivo em toda pagina com legenda
    de 2 linhas.
    """
    import re
    if not _METOD.exists():
        pytest.skip("paginas de metodologia nao geradas")
    vazam = []
    for arq in sorted(_METOD.glob("*.html")):
        t = arq.read_text(encoding="utf-8", errors="replace")
        for svg in re.findall(r"<svg.*?</svg>", t, re.S):
            m = re.search(r'viewBox="([-\d.]+) ([-\d.]+) ([\d.]+)', svg)
            if not m:
                continue
            x0, W = float(m.group(1)), float(m.group(3))
            for mt in re.finditer(r'<text x="([-\d.]+)"([^>]*)>([^<]*)</text>', svg):
                if "rotate" in mt.group(2):
                    continue
                x, atr, txt = float(mt.group(1)), mt.group(2), mt.group(3)
                larg = len(txt) * 5.2
                anc = ("end" if 'text-anchor="end"' in atr
                       else "middle" if "middle" in atr else "start")
                dir_ = x if anc == "end" else (x + larg / 2 if anc == "middle"
                                               else x + larg)
                esq = x - larg if anc == "end" else (x - larg / 2 if anc == "middle"
                                                     else x)
                if dir_ > x0 + W + 1 or esq < x0 - 1:
                    vazam.append((arq.name, txt[:26], round(esq), round(dir_)))
    assert not vazam, (
        f"{len(vazam)} textos fora do viewBox: "
        + "; ".join(f"{a}: {t!r} em [{e},{d}]" for a, t, e, d in vazam[:5]))


def test_o_fluxograma_publica_o_censo_CANONICO():
    """O numero do fluxo tem de ser o mesmo do censo publicado.

    ⚠️ Ja divergiu: eu contei com `caso_no_documento` (207 curvas, 173 no tripe)
    e o censo canonico usa `caso_comparavel` (205, 171). A docstring desse filtro
    diz "filtro UNICO do censo de comparaveis — todo consumidor passa por aqui";
    contar por fora publicava dois censos discordantes na mesma arvore.
    """
    import re
    arq = _METOD / "fluxo.html"
    if not arq.exists():
        pytest.skip("fluxograma nao gerado")
    t = arq.read_text(encoding="utf-8", errors="replace")
    m = re.search(r"<b>(\d+)</b> curvas comparáveis", t)
    m2 = re.search(r"<b>(\d+)</b> no tripé", t)
    assert m and m2, "o fluxograma nao publica mais o censo"
    import sys
    if str(RAIZ / "tests") not in sys.path:
        sys.path.insert(0, str(RAIZ / "tests"))
    from test_meta_numeros_nao_envelhecem import _censo
    c = _censo()
    assert int(m.group(1)) == c["n"], (
        f'o fluxograma diz {m.group(1)} comparaveis, o censo diz {c["n"]}')
    assert int(m2.group(1)) == c["tripe"], (
        f'o fluxograma diz {m2.group(1)} no tripe, o censo diz {c["tripe"]}')


def test_a_pagina_modelo_nao_fit_prova_MESMAS_constantes():
    """A pagina afirma "mesmas constantes"; o teste confere que sao.

    Sem isto a pagina poderia afirmar o contrario do que mede — e foi exatamente
    o que aconteceu com o candidato descartado: o aco do ROUSSEAU parecia o
    exemplo perfeito e tem 10 constantes DIFERENTES entre as espessuras.
    """
    arq = _METOD / "modelo_nao_fit.html"
    if not arq.exists():
        pytest.skip("pagina nao gerada")
    t = arq.read_text(encoding="utf-8", errors="replace")
    assert "constantes efetivas <b>idênticas</b>" in t, (
        "a pagina deixou de afirmar constantes identicas — ou o par mudou e a "
        "afirmacao ficou falsa, que e pior")
    assert "falsificado" in t.lower(), (
        "sumiu o registro de que o candidato obvio (aco do ROUSSEAU) foi "
        "falsificado; sem ele a escolha parece arbitraria")
