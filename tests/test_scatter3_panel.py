"""Invariantes do 3D do painel "Onde está o erro" (reforma de 2026-07-29).

Por que estes testes existem, e por que ESTES: o gráfico é desenhado DUAS vezes
— uma em Python (estático, o que imprime e o que vale sem JS) e uma em JS (o que
responde aos controles ao vivo). Duas implementações do mesmo desenho divergem
em silêncio, e a divergência não aparece em nenhum assert de "o HTML contém X".
Então aqui a maior parte dos testes é de SINCRONIA: as constantes da rampa, a
rotação default e o mapa de cores por perna são lidos do fonte do JS e comparados
com os do Python.

Duas regressões concretas que já aconteceram e ficam presas aqui:

· `fill:var(--#d13b2e)` — o JS re-embrulhava em `var(--...)` uma cor que já vinha
  como hexa, e o navegador resolve isso como PRETO. Os 202 pontos ficaram preto
  sobre fundo escuro. Nenhum teste de conteúdo pegaria: a string estava lá.
· 202 links `<a>` dentro do SVG sem `tabindex="-1"` = 202 paradas de tab antes do
  resto da página (armadilha de teclado).
"""
import re

import pytest


def _mod():
    from bolt_analysis_studio.validation import report_html
    return report_html


# --------------------------------------------------------------- rampa de cor

def test_rampa_ancoras():
    """A rampa tem de casar EXATAMENTE nos três pontos que a legenda promete:
    verde em 0, âmbar em 1× (a superfície da caixa) e vermelho no teto."""
    m = _mod()
    assert m._cor_rampa(0.0) == "#1f9d55"
    assert m._cor_rampa(1.0) == "#e0a411"
    assert m._cor_rampa(m._RAMPA_TETO) == "#d13b2e"
    # acima do teto satura, não dá a volta
    assert m._cor_rampa(50.0) == m._cor_rampa(m._RAMPA_TETO)
    assert m._cor_rampa(-1.0) == m._cor_rampa(0.0)


def test_rampa_ordena_do_verde_ao_vermelho():
    """Uma rampa que não ordena não é uma escala. O invariante NÃO é
    monotonicidade dos canais R e G isolados — verde→âmbar→vermelho sobe o verde
    de 0x9d para 0xa4 antes de cair (o âmbar é mais verde que o verde médio), e o
    vermelho cai de 0xe0 para 0xd1 no fim. Quem tem de ser monotônico é a
    DIFERENÇA R−G, que é o eixo verde↔vermelho de fato percebido."""
    m = _mod()
    xs = [i / 40 * m._RAMPA_TETO for i in range(41)]
    rg = [int(m._cor_rampa(d)[1:3], 16) - int(m._cor_rampa(d)[3:5], 16)
          for d in xs]
    assert rg == sorted(rg), "a rampa não ordena de verde a vermelho"
    assert rg[0] < 0 < rg[-1], "os extremos deveriam ser verde e vermelho"


def test_severidade_equivale_ao_tripe():
    """`_severidade <= 1` tem de ser IDÊNTICO ao veredito do tripé. É esta
    identidade que garante que a cor e a caixa tracejada nunca se contradigam —
    o motivo de a norma ser a do MÁXIMO e não a euclidiana."""
    m = _mod()
    lx, ly, lz = m.META_MAE, m.META_MAX, m.META_SRES
    casos = [
        (0.01, 0.02, 0.005),          # passa folgado
        (lx, ly, lz),                 # no canto exato da caixa
        (lx * 1.001, 0.01, 0.001),    # estoura só o MAE
        (0.01, ly * 1.001, 0.001),    # só o pico
        (0.01, 0.02, lz * 1.001),     # só o σ_res
        (0.30, 0.60, 0.10),           # fora de tudo
    ]
    for a, b, c in casos:
        passa_tripe = a <= lx and b <= ly and c <= lz
        assert (m._severidade(a, b, c, lx, ly, lz) <= 1.0) is passa_tripe, \
            f"cor e caixa discordam em {(a, b, c)}"
    # a euclidiana normalizada FALHARIA neste caso — é o contra-exemplo que
    # justifica a escolha, e ele fica no teste para ninguém "simplificar" de volta
    import math
    euclid = math.sqrt((1.5) ** 2 + 0.1 ** 2 + 0.1 ** 2) / math.sqrt(3)
    assert euclid < 1.0
    assert m._severidade(lx * 1.5, ly * 0.1, lz * 0.1, lx, ly, lz) > 1.0


def test_sem_sigma_res_nunca_e_verde():
    """Curva sem `resid_std` não é julgável na 3ª perna. Aprová-la seria ignorar
    a perna (mesma regra de `_tripe_ok`)."""
    m = _mod()
    assert m._severidade(0.0, 0.0, None, 0.05, 0.10, 0.025) == float("inf")
    assert m._perna_manda(0.0, 0.0, None, 0.05, 0.10, 0.025) == "sd"
    assert m._cor_rampa(m._severidade(0.0, 0.0, None, 0.05, 0.10, 0.025)) \
        == "#d13b2e"


def test_perna_manda_e_o_argmax_dos_multiplos():
    """A perna que manda é o MAIOR MÚLTIPLO estourado, não o maior valor bruto —
    é o que torna as três pernas comensuráveis."""
    m = _mod()
    lx, ly, lz = 0.05, 0.10, 0.025
    assert m._perna_manda(0.01, 0.02, 0.001, lx, ly, lz) is None
    # 0.12 nas duas: 2.4x no MAE contra 1.2x no pico => manda o MAE
    assert m._perna_manda(0.12, 0.12, 0.001, lx, ly, lz) == "mae"
    assert m._perna_manda(0.01, 0.5, 0.001, lx, ly, lz) == "mx"
    assert m._perna_manda(0.01, 0.02, 0.2, lx, ly, lz) == "sd"


# ------------------------------------------------- grade em múltiplos do limite

def test_grade_comeca_no_limite():
    """A 1ª linha de grade É o limite (e portanto coincide com a aresta da
    caixa): é o que permite ler "3–4× o limite" contando linhas."""
    m = _mod()
    g = m._mult_grade(0.30, 0.05)
    assert g[0] == pytest.approx(0.05)
    assert len(g) == 6
    assert g[-1] == pytest.approx(0.30)
    assert m._mult_grade(0.60, 0.10)[0] == pytest.approx(0.10)
    assert m._mult_grade(0.10, 0.025)[0] == pytest.approx(0.025)


def test_grade_cai_em_quartos_sem_limite():
    """RMSE e |viés| não têm limite declarado: a grade tem de degradar, não
    inventar um limite."""
    m = _mod()
    assert m._mult_grade(0.40, 0.0) == pytest.approx([0.1, 0.2, 0.3, 0.4])
    assert m._mult_grade(0.40, None) == pytest.approx([0.1, 0.2, 0.3, 0.4])
    # teto muito acima do limite => grade densa demais, cai em quartos
    assert len(m._mult_grade(1.0, 0.01)) == 4


# ------------------------------------------------------- SVG estático emitido

_PTS = [
    (0.005, 0.010, 0.002, "quase_perfeito"),
    (0.049, 0.099, 0.024, "no_canto_da_caixa"),
    (0.120, 0.250, 0.040, "fora"),
    (0.500, 0.900, 0.300, "recortado_em_tudo"),
]


def _svg():
    return _mod()._svg_scatter3(_PTS)


def test_recortado_vira_triangulo_e_os_outros_circulo():
    """Desenhar um círculo em cima da borda afirmaria um valor que não é o dado.
    O ponto recortado tem de ficar visualmente distinto."""
    svg = _svg()
    assert svg.count("<polygon") >= 1
    tri = re.search(r'data-cid="recortado_em_tudo"[^>]*>\s*<polygon', svg)
    assert tri, "o ponto fora do teto não saiu como triângulo"
    cir = re.search(r'data-cid="quase_perfeito"[^>]*>\s*<circle', svg)
    assert cir, "ponto dentro do teto deveria ser círculo"
    assert "recortada(s) na borda" in svg


def _forma(svg, cid):
    """(tag, n_pontos_do_polygon, tem_contorno) da marca daquela curva."""
    m = re.search(r'data-cid="%s"[^>]*>\s*<(\w+)([^>]*)>' % re.escape(cid), svg)
    assert m, f"{cid} não foi desenhada"
    tag, attrs = m.group(1), m.group(2)
    pts = re.search(r'points="([^"]+)"', attrs)
    return (tag, len(pts.group(1).split()) if pts else 0,
            "stroke:var(--ink)" in attrs)


def test_forma_do_marcador_carrega_o_estatuto(monkeypatch):
    """FORMA = ESTATUTO (pedido do professor, 2026-08-01): exceção e declarada
    NÃO podem ser desenhadas como uma curva julgada pela régua.

    Pinado com os dicionários REAIS monkeypatched (não com uma cópia da regra):
    se `estatuto_da_curva` deixar de ser a fonte única, o teste cai."""
    M = _mod()
    monkeypatch.setitem(M._EXCECOES, "no_canto_da_caixa", "exceção de teste")
    monkeypatch.setitem(M._DECLARADAS, "fora", "declarada de teste")
    svg = M._svg_scatter3(_PTS)
    assert _forma(svg, "quase_perfeito")[:2] == ("circle", 0)     # ● régua
    assert _forma(svg, "no_canto_da_caixa")[:2] == ("polygon", 4)  # ◆ exceção
    assert _forma(svg, "fora")[:2] == ("rect", 0)                  # ■ declarada
    assert "EXCEÇÃO assinada" in svg and "DECLARADA" in svg


def test_recorte_nao_rouba_a_forma_do_estatuto(monkeypatch):
    """O recorte é verdade sobre o DESENHO; o estatuto é sobre a CURVA. Com o
    triângulo vencendo, 16 dos 35 pontos com estatuto perdiam a marca no render
    real (medido 2026-08-01) — agora o recorte é contorno."""
    M = _mod()
    monkeypatch.setitem(M._EXCECOES, "recortado_em_tudo", "exceção recortada")
    svg = M._svg_scatter3(_PTS)
    tag, n, contorno = _forma(svg, "recortado_em_tudo")
    assert (tag, n) == ("polygon", 4), "exceção recortada perdeu o losango"
    assert contorno, "o recorte precisa continuar sinalizado (contorno)"
    # o caso SEM estatuto (recortado ⇒ triângulo, a convenção do ▲ da nota)
    # é pinado por `test_recortado_vira_triangulo_e_os_outros_circulo`, que
    # roda sem monkeypatch — repeti-lo aqui, com os dicts ainda pinados,
    # testava o contrário do que dizia (foi o que falhou na 1ª execução).


def test_cor_do_ponto_vem_da_severidade_dele():
    """Cada ponto sai com a cor da SUA severidade — a `d` vem do ponto, não de um
    número escolhido no teste (foi o erro da 1ª versão deste teste)."""
    m, svg = _mod(), _svg()
    lx, ly, lz = m.META_MAE, m.META_MAX, m.META_SRES
    for a, b, c, cid in _PTS:
        cor = m._cor_rampa(m._severidade(a, b, c, lx, ly, lz))
        assert re.search(rf'fill:{cor};[^>]*>\s*<title>{cid} ', svg) \
            or re.search(rf'data-cid="{cid}"[^>]*>\s*<\w+[^>]*fill:{cor}', svg), \
            f"{cid} não saiu com a cor {cor} da sua severidade"
    # e a ordem sobrevive: o quase-perfeito é mais verde que o pior
    bom = m._cor_rampa(m._severidade(*_PTS[0][:3], lx, ly, lz))
    ruim = m._cor_rampa(m._severidade(*_PTS[3][:3], lx, ly, lz))
    rg = lambda h: int(h[1:3], 16) - int(h[3:5], 16)
    assert rg(bom) < rg(ruim)


def _js_sem_comentarios():
    """O fonte do JS com as linhas de comentário removidas. Necessário porque os
    comentários CITAM os padrões proibidos ao explicar o bug — sem isto o teste
    reprova pela própria documentação (aconteceu na 1ª versão)."""
    return "\n".join(l for l in _mod()._JS_PAINEL.splitlines()
                     if not l.lstrip().startswith("//"))


def test_nenhum_var_com_hexa_dentro():
    """REGRESSÃO: `fill:var(--#d13b2e)` resolve como PRETO. Aconteceu no JS ao
    re-embrulhar em `var(--...)` uma cor que já vinha completa, e pintou os 202
    pontos de preto sobre fundo escuro."""
    assert "var(--#" not in _svg()
    js = _js_sem_comentarios()
    assert "var(--#" not in js
    # O erro esteve em `marca()`, que recebe a cor JÁ COMPLETA. Embrulhar é
    # correto em `corDe`, onde `corPerna` devolve só o nome da var — por isso o
    # assert é sobre o corpo de `marca`, não sobre o arquivo todo (a 1ª versão
    # deste teste reprovava o código certo).
    corpo = js.split("function marca(")[1].split("\n  }")[0].replace(" ", "")
    assert "fill:'+cor+'" in corpo
    assert "var(--'+cor" not in corpo


def test_links_fora_da_ordem_de_tab():
    """REGRESSÃO: 202 links dentro do SVG = 202 paradas de tab antes do resto da
    página. A rota acessível equivalente é a tabela de casos."""
    svg = _svg()
    n_links = svg.count("<a href=")
    assert n_links == len(_PTS)
    assert svg.count('tabindex="-1"') == n_links


def test_data_attrs_que_o_js_consome():
    """O JS reprojeta lendo os `data-*` do próprio SVG (invariante declarado no
    docstring). Se um deles sumir, o giro passa a usar constantes próprias e as
    duas implementações divergem."""
    svg = _svg()
    for k in ("data-s3", "data-cx", "data-cy", "data-cz", "data-ml", "data-mt",
              "data-wp", "data-hp", "data-y0", "data-dx", "data-dy",
              "data-zlab"):
        assert f'{k}="' in svg, f"{k} ausente"


def test_rotacao_default_e_a_medida():
    """A rotação default é o ótimo MEDIDO (separação angular máxima da nuvem);
    tem de sair no SVG e ser a MESMA no fallback do JS."""
    m, svg = _mod(), _svg()
    dx, dy = m._ROT3
    assert f'data-dx="{dx}"' in svg and f'data-dy="{dy}"' in svg
    js = m._JS_PAINEL
    assert f"+s3.dataset.dx : {dx}" in js
    assert f"+s3.dataset.dy : {dy}" in js


def test_legenda_da_rampa_no_cabecalho():
    svg = _svg()
    assert "distância à origem" in svg
    assert "1× = a caixa" in svg
    assert svg.count("<rect") >= 26          # a barra da rampa


# ------------------------------------------- sincronia Python <-> JS (o núcleo)

def test_js_rampa_identica_a_do_python():
    """As duas implementações desenham a MESMA rampa; se uma mudar sozinha, as
    cores da página passam a discordar da legenda estática."""
    m = _mod()
    js = m._JS_PAINEL
    esperado = ",".join(
        "[" + ",".join(f"0x{c:02x}" for c in anc) + "]" for anc in m._RAMPA)
    assert f"var RAMPA = [{esperado}]" in js, \
        "literal RAMPA do JS divergiu de _RAMPA"
    assert f"RTETO = {m._RAMPA_TETO:.0f}" in js


def test_js_cores_por_perna_iguais_ao_mapa_do_python():
    m = _mod()
    js = m._JS_PAINEL
    for perna, var in m._COR_PERNA.items():
        if perna is None:
            assert "return 'good'" in js
        else:
            assert f"'{var}'" in js, f"cor da perna {perna} ({var}) ausente do JS"


def test_js_severidade_espelha_a_regra_do_python():
    """A regra "sem σ_res => nunca verde" tem de estar nas DUAS pontas — e,
    desde a adoção do D1 (2026-07-30), a 3ª perna usa o limite EFETIVO
    `max(slider, piso da fonte)` também nas duas: severidade, cor e censo do JS
    leem `lsd(c)`, nunca `L.sd` cru (meia-régua em cada camada foi o defeito de
    2026-07-29 no report por caso)."""
    js = _mod()._JS_PAINEL
    assert "if (c.d === null) return 1/0;" in js
    assert "Math.max(c.a/L.mae, c.x/L.mx, c.d/lsd(c))" in js
    assert "function lsd(c){ return Math.max(L.sd, c.pf || 0); }" in js
    assert "c.d/L.sd" not in js, (
        "algum caminho do JS voltou a julgar a 3a perna pelo slider cru, "
        "ignorando o piso por fonte (D1)")


def test_js_arrasto_nao_gruda_e_nao_usa_captura():
    """Duas exigências que se opõem, e a ordem em que se resolvem importa:

    · soltar o botão FORA da janela não gera `pointerup`, e sem tratamento o
      gráfico continua girando quando o cursor volta (arrasto grudado);
    · `setPointerCapture` conserta isso — e QUEBRA O LINK DO PONTO, porque com
      captura ativa o navegador retargeta o `click` para o elemento que capturou
      (o `<svg>`) em vez do `<a>` sob o cursor. Aconteceu: a captura entrou como
      conserto do arrasto e o clique parou de abrir o report.

    A solução que atende às duas é `e.buttons === 0` no `pointermove`, sem
    captura nenhuma. Este teste proíbe a volta da captura."""
    js = _js_sem_comentarios()
    assert "setPointerCapture" not in js, \
        "captura de ponteiro voltou — ela retargeta o click e mata o link"
    assert "e.buttons === 0" in js, "sem a guarda do botão o arrasto gruda"
    assert "pointercancel" in js
    assert "'blur'" in js                         # e alt-tab no meio do gesto
    assert "keydown" in js and "ArrowRight" in js
    assert "requestAnimationFrame" in js          # redesenho a 1 por quadro
    assert "touchAction" in js


def test_limiar_de_clique_tolera_tremor():
    """Com limiar de 4 px na soma |dx|+|dy|, um tremor de 3+2 px durante o clique
    já cancelava a navegação. 8 px de arrasto mudam a rotação em 0.009 —
    invisível —, então folgar é barato e apertar é caro."""
    js = _js_sem_comentarios()
    assert "movimento > 8" in js


def test_href_do_ponto_segue_a_convencao_de_quem_escreve():
    """Os arquivos por caso são escritos em `<out>/reports/<case_id>.html`
    (`write_reports`), e é a MESMA convenção usada pela tabela, pela lista e
    pelos cards do report mestre. Se o subdiretório mudar num lugar só, os 202
    links do 3D viram 404 em silêncio — nada na página denuncia."""
    m = _mod()
    import inspect
    fonte = inspect.getsource(m.write_reports)
    assert '"reports"' in fonte, "write_reports não escreve mais em reports/"
    svg = _svg()
    assert svg.count('href="reports/') == len(_PTS)
    # e o link do leitor de foco (rota de teclado) usa a mesma convenção
    assert '\'<a href="reports/\' + c.c' in _mod()._JS_PAINEL
    # os pontos do JS também
    assert '\'<a href="reports/\'+c.c' in _mod()._JS_PAINEL


def test_leitor_de_foco_carrega_o_link():
    """Os pontos saíram da ordem de tab; então o leitor de foco tem de carregar o
    link, senão não existe caminho de teclado para o report do caso."""
    js = _js_sem_comentarios()
    bloco = js.split("info.innerHTML")[1].split(";")[0]
    assert 'href="reports/' in bloco
    assert "rel=\"noopener\"" in bloco or "rel='noopener'" in bloco


# ------------------------------------------------------------------ controles

def test_controles_tem_escala_cor_e_leitor():
    m = _mod()
    html = m._controles_html(m.META_MAE, m.META_MAX, m.META_SRES)
    for ident in ("in-mx", "in-mae", "in-sd", "in-z", "in-esc", "in-cor",
                  "bt-reset", "s3-info"):
        assert f'id="{ident}"' in html, f"controle {ident} ausente"
    assert 'value="lim"' in html and 'value="grad"' in html


def test_painel_vazio_nao_explode():
    assert _mod()._svg_scatter3([]) == ""


# ------------------------------------------------------- orçamento de layout

def test_cabecalho_cabe_no_viewbox():
    """O cabeçalho tem 2 linhas + a barra da rampa dentro de `MT`. As colisões
    deste bloco foram achadas varrendo `getBBox` na página (não a olho), e a
    aritmética que as evita fica aqui para não voltarem em silêncio: linha 1 em
    MT−40, rótulos da rampa em MT−25, barra em MT−22..MT−14, gráfico em MT."""
    svg = _svg()
    mt = int(re.search(r'data-mt="(\d+)"', svg).group(1))
    assert mt >= 46, "MT pequeno demais para o cabeçalho de 2 linhas + rampa"
    ys = [float(y) for y in re.findall(r'<text x="46(?:\.0)?" y="([\d.]+)"', svg)]
    assert ys, "nenhuma linha de cabeçalho começando em x=ML"
    assert max(ys) <= mt - 10, "cabeçalho invade a área do gráfico"
    # a barra da rampa fica ACIMA do topo do gráfico
    for y in re.findall(r'<rect x="[\d.]+" y="([\d.]+)" width="4.6"', svg):
        assert float(y) + 8 <= mt, "a barra da rampa invade o gráfico"


def test_tique_do_3o_eixo_nao_encosta_no_eixo_x():
    """REGRESSÃO medida: com o rótulo do 3º eixo ABAIXO da aresta, o 1º múltiplo
    sobrepunha o último tique do eixo x em 9.9 × 2.7 px. Agora vai acima-à-
    esquerda, na região `res.máx < MAE` que é vazia por teorema."""
    svg = _svg()
    # o rótulo do teto do eixo x fica em y = y0 + 13; os do 3º eixo, ACIMA da
    # aresta => y menor que y0
    y0 = float(re.search(r'data-y0="([\d.]+)"', svg).group(1))
    zt = [float(y) for y in
          re.findall(r'<text x="[\d.]+" y="([\d.]+)" text-anchor="end" '
                     r'class="tk" style="fill:var\(--accent\)"', svg)]
    assert zt, "tiques do 3º eixo ausentes"
    assert all(y < y0 - 6 for y in zt), \
        f"tique do 3º eixo na faixa do eixo x (y0={y0}, tiques={zt})"


# -------------------------------------- report POR CASO: tripé, RMSE, figuras
#
# A régua virou de duas para três pernas em 2026-07-29 e o painel mestre foi
# atualizado — o report por caso NÃO. Ele julgava o MAE contra 0.1 (limite
# velho), não mencionava o σ_res, e mostrava o RMSE como número solto. Uma curva
# reprovada no mestre abria a própria página com o cartão VERDE. Estes testes
# prendem as três pernas, a leitura do RMSE, e o limite lido de `META_*`.

def _case_html():
    from bolt_analysis_studio.validation.case_registry import all_records
    from bolt_analysis_studio.validation.runner import CaseResult
    from bolt_analysis_studio.validation.report_html import case_report_html
    rec = next(r for r in all_records() if r.case_class == "full_curve")
    # >=6 pontos na janela: com a regra n<6 (assinada 2026-08-01,
    # N_MIN_SRES) um sintetico de 3 pontos vira sigma NAO-JULGAVEL e o
    # bloco do tripe muda de forma legitima — este teste pina a leitura
    # do RMSE, nao o ramo n<6.
    res = CaseResult(
        case_id=rec.case_id, ok=True, cycles=[0, 200, 400, 600, 800, 1000],
        ratio=[1.0, 0.96, 0.92, 0.88, 0.84, 0.8], mae=0.123, rmse=0.1346,
        maxerr=0.2252,
        maxerr_at=800.0, resid_std=0.1165, final_pred=0.8, final_data=0.78,
        metric_x=[0.0, 200.0, 400.0, 600.0, 800.0, 1000.0],
        metric_data=[1.0, 0.97, 0.94, 0.91, 0.88, 0.85],
        metric_pred=[1.0, 0.95, 0.9, 0.85, 0.8, 0.74], decomp={},
        generated_at="2026-07-29T12:00:00", engine_fingerprint="teste")
    return rec, res, case_report_html(rec, res)


def test_report_por_caso_tem_as_tres_pernas():
    m = _mod()
    _, _, html = _case_html()
    assert "Veredicto do tripé" in html
    for perna in ("MAE", "resíduo máximo", "σ_res"):
        assert perna in html, f"perna {perna} ausente do report por caso"
    # os três limites, lidos das constantes e não escritos à mão
    for lim in (m.META_MAE, m.META_MAX, m.META_SRES):
        assert f"{lim:.4g}" in html
    # σ_res 0.1165 / 0.025 = 4.66x é o maior múltiplo => é a perna que manda
    assert "4.66×" in html
    assert "a perna que manda" in html


def test_report_por_caso_nao_usa_mais_a_regua_de_duas_pernas():
    """REGRESSÃO: o cartão do topo e a tabela de estágios pintavam contra 0.1.
    Com MAE 0.123 (viola os 0.05 de hoje) nada pode aparecer como 'no alvo'."""
    _, _, html = _case_html()
    assert "no alvo (&#8804;0.1)" not in html
    assert "acima do alvo 0.1<" not in html
    assert "fora do tripé" in html
    assert 'class="metric good"' not in html, \
        "cartão verde numa curva que viola as três pernas"


def test_rmse_ganha_leitura_e_nao_vira_porta():
    """O RMSE tem de aparecer COM as duas leituras que ele carrega — posição na
    cunha e a decomposição — e explicitamente NÃO como limite."""
    _, _, html = _case_html()
    assert "não é porta" in html
    assert "posição na cunha" in html
    assert "|viés| / RMSE" in html
    assert "RMSE² = viés² + σ_res²" in html
    assert "MAE &le; RMSE &le; res.máx" in html
    # a cunha: RMSE 0.1346 entre MAE 0.123 e maxerr 0.2252 => 0.11
    assert "0.11" in html


def test_tripe_block_degrada_sem_a_metrica():
    """Registro antigo sem `resid_std` não pode ser aprovado nem reprovado em
    silêncio na 3ª perna: tem de dizer 'não julgável'."""
    m = _mod()
    from bolt_analysis_studio.validation.runner import CaseResult
    res = CaseResult(case_id="x", ok=True, mae=0.02, rmse=0.03, maxerr=0.05,
                     resid_std=None)
    bloco = m._tripe_block(res)
    assert "não julgável" in bloco and "re-simule" in bloco
    # e sem MAE/maxerr o bloco simplesmente não sai (nada a julgar)
    assert m._tripe_block(CaseResult(case_id="x", ok=True)) == ""


def test_figura_do_artigo_fica_gravada_no_html():
    """A figura era `<img src="../../variable_explorer/paper_figures/...">`, o que
    (a) sobe acima da raiz do servidor — `http.server` normaliza os `..` fora e
    devolve **404** — e (b) quebra se a pasta mudar de lugar. Embutida como
    `data:` URI, funciona servida, em file://, num zip e depois de mover."""
    m = _mod()
    figdir = m.repo_root() / "New_Theory" / "variable_explorer" / "paper_figures"
    algum = sorted(figdir.glob("*.png"))
    if not algum:
        pytest.skip("acervo de figuras ausente neste checkout")
    uri = m._fig_data_uri(algum[0])
    assert uri and uri.startswith("data:image/png;base64,")
    # cache: a 2ª chamada devolve o MESMO objeto sem re-encodar (49 figuras
    # usadas 243 vezes — sem cache, 243 encodes)
    assert m._fig_data_uri(algum[0]) is uri


def test_figura_embutida_preserva_o_que_ela_serve_para_conferir():
    """A figura é o instrumento da conferência da digitalização (§3b). Comprimir
    com perda o artefato que serve para verificar a digitalização seria trocar a
    coisa medida pela medição — então o embutido é PNG indexado, e aqui se mede
    que o erro fica abaixo de 1/255 por canal."""
    m = _mod()
    figdir = m.repo_root() / "New_Theory" / "variable_explorer" / "paper_figures"
    algum = sorted(figdir.glob("*.png"))[:6]
    if not algum:
        pytest.skip("acervo de figuras ausente neste checkout")
    Image = pytest.importorskip("PIL.Image", reason="Pillow ausente")
    from PIL import ImageChops, ImageStat
    import base64 as _b64, io as _io
    for p in algum:
        uri = m._fig_data_uri(p)
        assert uri
        emb = Image.open(_io.BytesIO(
            _b64.b64decode(uri.split(",", 1)[1]))).convert("RGB")
        orig = Image.open(p).convert("RGB")
        if orig.width > m._FIG_MAXW:          # o embutido pode ter sido reduzido
            orig = orig.resize(emb.size, Image.LANCZOS)
        assert emb.size == orig.size
        mae = sum(ImageStat.Stat(ImageChops.difference(orig, emb)).mean) / 3
        assert mae < 2.0, f"{p.name}: erro medio {mae:.2f}/255 alto demais"


def test_uma_frase_de_grade_por_modo_no_js():
    """As duas frases juntas estouravam o viewBox (x=622 num viewBox de 560)."""
    js = _js_sem_comentarios()
    bloco = js.split("caixa tracejada = o trip")[1].split("</text>")[0]
    assert "uma linha de grade = um limite" in bloco
    assert "múltiplos do limite" in bloco
    assert bloco.count("' · '") <= 1, "as duas frases saem juntas outra vez"


# ------------------------------------------------- chave de FORMAS (2026-08-01)
# Pedido do professor: "legenda melhor, mais interpretável". O diagnóstico que
# saiu da medição: as formas (● ◆ ■ ▲) ganharam significado em 2026-08-01 — a
# FORMA passou a carregar o ESTATUTO — e a legenda do gráfico nunca soube disso.
# O vocabulário existia só no bloco `_explica`, a uma rolagem de distância, com
# glifos de TEXTO que o leitor tinha de casar de cabeça com o desenho.

def test_chave_de_formas_esta_no_svg_com_as_marcas_reais():
    """A chave tem de existir E ser desenhada por `_marca3`.

    Se a chave desenhasse glifos próprios, ela poderia divergir da marca — que
    é exatamente o defeito que se está consertando. `_marca3` com estatuto
    `exc` emite um losango (polygon de 4 pontos); a chave tem de conter esse
    mesmo polígono."""
    M = _mod()
    # `_PTS` não tem estatuto (os rótulos não estão no registry), então para ver
    # losango e quadrado é preciso alimentar case_ids REAIS — usar os inventados
    # testaria a chave contra um gráfico que ela nunca desenha.
    pts = list(_PTS)
    if M._EXCECOES:
        pts.append((0.02, 0.04, 0.01, sorted(M._EXCECOES)[0]))
    if M._DECLARADAS:
        pts.append((0.03, 0.05, 0.012, sorted(M._DECLARADAS)[0]))
    svg = M._svg_scatter3(pts)
    esperados = ["julgada pela régua", "sombra no piso"]
    if M._EXCECOES:
        esperados.append("exceção")
    if M._DECLARADAS:
        esperados.append("declarada")
    for rot in esperados:
        assert rot in svg, f"a chave não nomeia {rot!r}"
    # a marca da chave é a MESMA função: compara com uma emissão direta
    losango = M._marca3(0, 0, "var(--mut)", False, "exc")
    assert losango.startswith("<polygon"), "mudou a forma da exceção"
    assert "<polygon" in svg and "var(--mut)" in svg


def test_contagem_da_chave_bate_com_as_marcas_desenhadas():
    """O número na chave conta o que foi DESENHADO, não o que se supõe.

    `_cont_forma` classifica pela forma que a marca vai receber — e o estatuto
    vence o recorte. Contar pelo estatuto prometeria triângulos que o gráfico
    não desenha."""
    M = _mod()
    cont = {}
    # sem estatuto e recortado => triângulo
    assert M._cont_forma(cont, "nao_existe_no_registry", True) == ""
    assert cont["rec"] == 1
    # sem estatuto e dentro => círculo
    M._cont_forma(cont, "nao_existe_tambem", False)
    assert cont["reg"] == 1
    # uma exceção assinada de verdade, ainda que RECORTADA, conta como exceção
    if M._EXCECOES:
        cid = sorted(M._EXCECOES)[0]
        M._cont_forma(cont, cid, True)
        assert cont["exc"] == 1, "estatuto tem de vencer o recorte"
        assert cont.get("rec") == 1, "recorte não pode contar duas vezes"


def test_chave_nao_inventa_classe_vazia():
    """Classe sem nenhum ponto não vira entrada morta na chave.

    Os `_PTS` de teste não têm exceção nem declarada (não estão no registry),
    então a chave desses testes só pode falar de julgada/recortada."""
    M = _mod()
    svg = M._svg_scatter3(_PTS)
    assert "exceção 0" not in svg and "declarada 0" not in svg


def test_chave_de_formas_cabe_no_viewBox():
    """Guarda de LARGURA — o defeito real que a varredura de getBBox pegou.

    A linha 1 do Python terminava em x=597 num viewBox de 560 (53 px cortados,
    e só no render estático, que é o que imprime). Aqui a conta usa o mesmo
    `_CHAR_TK` que o layout usa, então um rótulo novo e longo reprova ANTES de
    alguém abrir o navegador."""
    M = _mod()
    W, ML, MR = 560, 46, 16
    rotulos = [("julgada pela régua", 999), ("exceção", 999),
               ("declarada", 999), ("recortada", 999)]
    cur = ML
    for rot, n in rotulos:
        cur += 11 + len(f"{rot} {n}") * M._CHAR_TK + 14
    cur += 11 + len("sombra no piso (z=0)") * M._CHAR_TK
    assert cur <= W - MR, (
        f"a chave de formas terminaria em x={cur:.0f} num viewBox de {W} "
        f"(limite {W - MR}) com contagens de 3 dígitos")


def test_python_e_js_usam_os_MESMOS_rotulos_na_chave():
    """SINCRONIA — o motivo pelo qual este arquivo existe.

    A divergência já aconteceu neste mesmo cabeçalho: o Python citava a sombra
    na linha 1 e o JS não, e era a versão do Python que estourava o viewBox.
    Aqui os rótulos são lidos dos DOIS fontes e comparados."""
    import pathlib
    M = _mod()
    src = pathlib.Path(M.__file__).read_text(encoding="utf-8")
    # assinatura com `oc` desde 2026-08-07: a chave declara as ocultas do
    # filtro de estatuto. Janela de 2000 porque a função cresceu junto.
    js = src[src.find("function formas(x, y, cf, oc)"):][:2000]
    assert js, "a função `formas` sumiu do JS — a chave deixou de ser redesenhada"
    for rot in ("julgada pela r", "declarada", "recortada", "sombra no piso"):
        assert rot in js, f"o JS não tem o rótulo {rot!r} que o Python tem"
    # e a largura de caractere usada nos dois tem de ser a mesma
    assert str(M._CHAR_TK) in js, (
        f"o JS não usa o mesmo _CHAR_TK ({M._CHAR_TK}) do Python — as duas "
        f"chaves vão quebrar linha em pontos diferentes")


# ----------------------------------------- rodapé do 3D (revisão 2026-08-07)
# Dois defeitos MEDIDOS na revisão, os dois de "o desenho afirma duas coisas":
#
# 1. o rodapé escrevia "▲ N recortada(s)" contando TODA curva recortada, e a
#    chave do cabeçalho contava só as que viram triângulo — mas o triângulo
#    PERDE para o estatuto (losango/quadrado vencem). Com uma recortada que
#    também é exceção, o mesmo gráfico exibia 5 e 2 para a mesma coisa.
# 2. as curvas sem σ_res julgável (n<6) sumiam do gráfico em SILÊNCIO: a chave
#    dizia "declarada 7" enquanto as tabelas mostravam 12 declaradas.

def test_rodape_reparte_as_recortadas_por_forma():
    """O rodapé tem de dizer quantas viraram ▲ e quantas guardaram o estatuto.

    Sem a repartição, rodapé e chave contam populações diferentes com o mesmo
    nome — e quem lê não tem como saber que a diferença é o estatuto."""
    M = _mod()
    pts = list(_PTS)
    if M._EXCECOES:                       # uma exceção RECORTADA: o caso duro
        pts.append((0.9, 1.5, 0.5, sorted(M._EXCECOES)[0]))
    svg = M._svg_scatter3(pts)
    assert "recortada(s) na borda" in svg
    assert "mantém a forma do estatuto" in svg, (
        "o rodapé não reparte — volta a contradizer a chave de formas")


def test_rodape_declara_as_curvas_omitidas():
    """Curva sem 3ª perna não pode sumir calada.

    `omitidas` é passado pelo chamador (`len(trio) - len(pts3)`); sem a nota, a
    contagem da chave contradiz as tabelas e o leitor não tem explicação."""
    M = _mod()
    svg = M._svg_scatter3(_PTS, omitidas=6)
    assert "6 curvas sem" in svg and "n&lt;6" in svg
    assert "fora deste gráfico" in svg
    # zero omitidas => nota nenhuma (não inventar linha vazia)
    assert "fora deste gráfico" not in M._svg_scatter3(_PTS, omitidas=0)


def test_o_rodape_nao_invade_a_faixa_do_eixo():
    """Guarda de LAYOUT do rodapé — a lacuna que deixou o defeito passar.

    A varredura de colisão original só olhava o CABEÇALHO (y < MT), então as
    duas notas novas caíram por cima dos tiques do eixo x e do rótulo MAE sem
    nenhum teste reclamar; só a captura de tela mostrou. Aqui as faixas são
    conferidas por construção: MAE acompanha o gráfico (y0+30) e as notas ficam
    na banda de baixo, depois dele."""
    M = _mod()
    svg = M._svg_scatter3(_PTS, omitidas=3)
    h = int(re.search(r'viewBox="0 0 \d+ (\d+)"', svg).group(1))
    ys = {}
    for tag, y, txt in re.findall(r'<text x="[-\d.]+" y="([\d.]+)"[^>]*>(?:)([^<]*)',
                                  svg) and []:
        pass
    def y_de(frag):
        m = re.search(r'<text[^>]*y="([\d.]+)"[^>]*>[^<]*' + re.escape(frag), svg)
        return float(m.group(1)) if m else None
    y_mae = y_de("MAE")
    y_omit = y_de("curvas sem")
    assert y_mae and y_omit, "rótulo MAE ou nota das omitidas sumiu"
    assert y_omit > y_mae, (
        f"a nota (y={y_omit}) tem de ficar ABAIXO do rótulo MAE (y={y_mae}) — "
        f"acima dela invade a faixa do eixo")
    assert y_omit <= h - 10, "a nota saiu do viewBox pela base"
