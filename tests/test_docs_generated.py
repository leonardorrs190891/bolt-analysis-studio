"""Secoes geradas da aba Documentation: literatura (19-21) e interface (22).

Escrito em 2026-09-02, com dois invariantes que valem mais que os outros:

1. NENHUM DOI nas secoes pode existir sem origem rastreavel — o corpus
   (`ValidationCase.doi`) ou `New_Theory/classics_verified.json`. No mesmo dia,
   25 DOIs gerados de memoria foram testados e varios RESOLVIAM para artigos
   sem relacao com o tema. DOI que resolve nao prova citacao correta, e um
   software que acompanha artigo submetido nao pode carregar bibliografia
   plausivel e falsa.

2. Todo <img> da secao 22 tem de apontar para arquivo que existe. Imagem
   quebrada num help e' pior que help sem imagem: parece que falta conteudo.
"""
import inspect
import json
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "src"))
sys.path.insert(0, str(RAIZ / "New_Theory"))

import pytest                                                    # noqa: E402

RECURSOS = RAIZ / "src" / "bolt_analysis_studio" / "resources"
DOCS = RECURSOS / "docs"


def _json(nome):
    arq = DOCS / nome
    if not arq.is_file():
        pytest.skip(f"{nome} ausente: rode o gerador correspondente")
    return json.loads(arq.read_text(encoding="utf-8"))


def test_secoes_de_literatura_existem_e_tem_conteudo():
    d = _json("literature.json")
    assert set(d) == {"literature_review", "validation_sources", "bibliography"}
    for chave, s in d.items():
        assert s["title"].strip(), chave
        assert len(s["content"]) > 2000, f"{chave} suspeitamente curta"


def test_secao_de_interface_existe_e_tem_conteudo():
    d = _json("ui_reference.json")
    assert set(d) == {"ui_reference"}
    assert len(d["ui_reference"]["content"]) > 2000


def test_todo_img_da_secao_22_aponta_para_arquivo_que_existe():
    d = _json("ui_reference.json")
    srcs = re.findall(r'<img src="([^"]+)"', d["ui_reference"]["content"])
    assert srcs, "a secao de interface nao tem uma unica imagem"
    faltando = [s for s in srcs if not (RECURSOS / s).is_file()]
    assert not faltando, f"{len(faltando)} imagens quebradas: {faltando[:5]}"


def test_toda_superficie_descrita_foi_capturada():
    """Uma entrada com prosa e sem print deixaria texto sobre uma tela que
    ninguem ve; o inverso deixaria print sem explicacao."""
    import build_ui_reference as bur

    d = _json("ui_reference.json")
    html = d["ui_reference"]["content"]
    descritas = {s[0] for s in bur.SUPERFICIES}
    nos_prints = {p.stem for p in (RECURSOS / "ui_reference").glob("*.png")}
    no_html = set(re.findall(r'<img src="ui_reference/([^."]+)\.png"', html))

    assert descritas <= nos_prints, f"sem print: {sorted(descritas - nos_prints)}"
    assert descritas == no_html, (
        f"descritas mas fora do HTML: {sorted(descritas - no_html)}; "
        f"no HTML mas nao descritas: {sorted(no_html - descritas)}")


def test_cada_superficie_tem_um_print_DIFERENTE():
    """Print presente nao e' print certo. As tres entradas do inspector saiam
    byte a byte iguais ao print do modulo Model: o dock "Properties" chegava
    escondido (o layout vem do QSettings da maquina do build) e a troca de aba
    acontecia atras de um painel invisivel. Tres legendas descreviam uma aba
    especifica e mostravam a mesma tela — o teste anterior passava."""
    import hashlib
    from collections import defaultdict

    por_hash = defaultdict(list)
    for p in sorted((RECURSOS / "ui_reference").glob("*.png")):
        por_hash[hashlib.sha256(p.read_bytes()).hexdigest()].append(p.stem)
    iguais = [v for v in por_hash.values() if len(v) > 1]
    assert not iguais, f"prints identicos entre si: {iguais}"


def test_o_print_do_inspector_mostra_um_elemento_selecionado():
    """Sem selecao o painel diz "No element selected" e exibe os defaults, e a
    legenda falaria de valores que o print nao tem. Com o SHANK selecionado
    aparecem a rigidez e o material do caso."""
    import build_ui_reference as bur

    fonte = (RAIZ / "New_Theory" / "build_ui_reference.py").read_text(
        encoding="utf-8")
    assert "_seleciona_elemento" in fonte
    assert "dock.setVisible(True)" in fonte
    # e o gerador para em vez de gravar um print mudo
    assert "SystemExit" in inspect.getsource(bur._seleciona_elemento)


def test_nenhum_doi_das_secoes_e_sem_origem():
    """O invariante central: cada DOI citado sai do corpus ou da lista
    verificada. Um DOI que nao esteja em nenhuma das duas foi inventado por
    alguem, e passaria por conferido."""
    from bolt_analysis_studio.validation.case_registry import all_records

    def norm(d):
        return d.lower().rstrip(".,);")

    permitidos = {norm(getattr(r.validation_case, "doi", "") or "")
                  for r in all_records()}
    permitidos.discard("")
    verif = RAIZ / "New_Theory" / "classics_verified.json"
    if verif.is_file():
        cj = json.loads(verif.read_text(encoding="utf-8"))
        for grupo in ("novas", "ja_citadas_no_repo"):
            permitidos |= {norm(v["doi"]) for v in cj.get(grupo, [])}

    d = _json("literature.json")
    citados = set()
    for s in d.values():
        citados |= {norm(x) for x in
                    re.findall(r"10\.[0-9]{4,}/[A-Za-z0-9./()_;-]+", s["content"])}
    orfaos = sorted(citados - permitidos)
    assert not orfaos, (
        f"{len(orfaos)} DOI sem origem no corpus nem na lista verificada: "
        f"{orfaos[:5]}")


def test_todo_artigo_do_corpus_com_doi_aparece_na_bibliografia():
    from bolt_analysis_studio.validation.case_registry import all_records

    d = _json("literature.json")
    bib = d["bibliography"]["content"].lower()
    fora = sorted({(getattr(r.validation_case, "doi", "") or "").strip().lower()
                   for r in all_records()} - {""} - {""})
    ausentes = [x for x in fora if x not in bib]
    assert not ausentes, f"{len(ausentes)} fontes do corpus fora da bibliografia"


def test_a_revisao_declara_que_nao_e_exaustiva():
    """Chamar de completa uma revisao que nao e' seria a mesma inexatidao que
    inventar DOI: o texto tem de dizer o que e'."""
    d = _json("literature.json")
    t = d["literature_review"]["content"].lower()
    assert "not" in t and "exhaustive" in t


def test_a_aba_de_documentacao_funde_as_secoes_geradas(qapp):
    from bolt_analysis_studio.gui.documentation_tab import DOCUMENTATION

    for chave in ("literature_review", "validation_sources", "bibliography",
                  "ui_reference"):
        assert chave in DOCUMENTATION, f"{chave} nao chegou a aba"
    # a busca da aba le content.lower() no dict inteiro: string, nao preguicoso
    for s in DOCUMENTATION.values():
        assert isinstance(s["content"], str)


# ---------------------------------------------------------------------------
# secoes 23-25 (bilingues) e a navegacao
# ---------------------------------------------------------------------------

def test_todo_tipo_de_elemento_tem_texto_revisado():
    """17 tipos no enum. Um tipo novo sem prosa tem de ACUSAR aqui: a doc
    explicava bem os corpos e quase nada as ligacoes, que e' onde a fisica do
    afrouxamento acontece."""
    from bolt_analysis_studio.core.models.element import ElementType
    import help_content

    faltando = [e.name for e in ElementType if e.name not in help_content.ELEMENTOS]
    assert not faltando, f"tipos sem texto: {faltando}"


def test_ligacoes_estao_marcadas_como_tal():
    """A separacao corpo/ligacao e' a informacao central da secao 23."""
    import help_content

    papeis = {v.get("papel") for v in help_content.ELEMENTOS.values()}
    assert papeis <= {"corpo", "ligacao", "fronteira"}, papeis
    ligas = [k for k, v in help_content.ELEMENTOS.items()
             if v.get("papel") == "ligacao"]
    assert len(ligas) >= 6, f"so {len(ligas)} ligacoes marcadas: {ligas}"


def test_todo_dialogo_do_codigo_aparece_na_secao_25():
    """Cobertura completa e' o requisito; profundidade e' proporcional. O que
    nao tem analise revisada aparece com o texto REAL da mensagem, marcado."""
    import build_help_sections as bhs

    d = _json("help_sections.json")
    html = d["dialogues"]["content"]
    dlgs = bhs.extrai_dialogos()
    assert dlgs, "nenhum dialogo extraido do codigo"
    # escapa o titulo antes de procurar: o gerador passa por html.escape, e um
    # titulo como 'Apply & Re-run' vira 'Apply &amp; Re-run' no HTML
    import html as _html
    fora = [t for t in dlgs if _html.escape(t, quote=False) not in html]
    assert not fora, f"{len(fora)} dialogos do codigo fora da secao: {fora[:5]}"


def test_secoes_novas_sao_bilingues():
    d = _json("help_sections.json")
    for chave, s in d.items():
        for campo in ("title", "content", "title_pt", "content_pt"):
            assert s.get(campo), f"{chave} sem {campo}"
        assert s["content"] != s["content_pt"], f"{chave}: PT igual ao EN"


def test_a_navegacao_mostra_TODAS_as_secoes(qapp):
    """Era lista escrita a mao com 16 pares contra 18 no dict: as secoes 17 e
    18 existiam e nao eram navegaveis. Agora a arvore sai do dict."""
    from bolt_analysis_studio.gui.documentation_tab import (
        DOCUMENTATION, DocumentationTab)

    t = DocumentationTab()
    assert t.nav_tree.topLevelItemCount() == len(DOCUMENTATION)


def test_o_alternador_de_idioma_troca_o_conteudo(qapp):
    from bolt_analysis_studio.gui.documentation_tab import DocumentationTab
    from bolt_analysis_studio.gui.i18n import Lang

    try:
        Lang.set_lang("en")
        t = DocumentationTab()
        t._show_section("element_types")
        en = t.content_browser.toPlainText()
        Lang.set_lang("pt")
        t2 = DocumentationTab()
        t2._show_section("element_types")
        pt = t2.content_browser.toPlainText()
        assert en and pt and en != pt
        assert "ligacao" in pt.lower() or "ligação" in pt.lower()
    finally:
        Lang.set_lang("en")


def test_o_menu_ajuda_do_chrome_V2_abre_a_documentacao(qapp):
    """A porta, nao so' o conteudo. Ate' 2026-09-02 as 25 secoes existiam e o
    chrome V2 — que E' o padrao — nao tinha item de menu para elas: estavam
    escritas e inalcancaveis para quem abre o programa normalmente. Conteudo
    sem porta e' o mesmo que conteudo ausente."""
    from PyQt6.QtWidgets import QMenu
    from bolt_analysis_studio.core.app_state import get_app_state
    from bolt_analysis_studio.gui.chrome.app_window import ChromeWindow

    w = ChromeWindow(get_app_state())
    ajuda = [m for m in w.menuBar().findChildren(QMenu) if m.title() == "Ajuda"]
    assert ajuda, "o chrome V2 nao tem menu Ajuda"
    textos = [a.text() for a in ajuda[0].actions()]
    assert any("Documenta" in t for t in textos), textos

    w._open_documentation()
    doc = getattr(w, "_doc_win", None)
    assert doc is not None, "o item de menu nao abriu janela"
    tab = doc.layout().itemAt(0).widget()

    from bolt_analysis_studio.gui.documentation_tab import DOCUMENTATION
    assert tab.nav_tree.topLevelItemCount() == len(DOCUMENTATION)

    # e a revisao de self-loosening abre de verdade
    tab._show_section("literature_review")
    assert "self-loosening" in tab.content_browser.toPlainText().lower()


def test_o_menu_ajuda_nao_promete_atalho_que_nao_existe(qapp):
    """O rotulo diz '(F1)'. Se o atalho nao estiver registrado, o menu mente."""
    from PyQt6.QtGui import QKeySequence, QShortcut
    from bolt_analysis_studio.core.app_state import get_app_state
    from bolt_analysis_studio.gui.chrome.app_window import ChromeWindow

    w = ChromeWindow(get_app_state())
    teclas = {s.key().toString() for s in w.findChildren(QShortcut)}
    assert QKeySequence("F1").toString() in teclas, sorted(teclas)


def test_a_contagem_do_menu_ajuda_nao_esta_vencida(qapp):
    """O item dizia '114 casos' quando o corpus ja' tinha 210. Contagem
    escrita a mao envelhece calada; esta afere contra o registry."""
    from PyQt6.QtWidgets import QMenu
    from bolt_analysis_studio.core.app_state import get_app_state
    from bolt_analysis_studio.gui.chrome.app_window import ChromeWindow
    from bolt_analysis_studio.validation.case_registry import all_records

    w = ChromeWindow(get_app_state())
    ajuda = [m for m in w.menuBar().findChildren(QMenu) if m.title() == "Ajuda"][0]
    alvo = [a.text() for a in ajuda.actions() if "Reports de Valida" in a.text()]
    assert alvo, "item de reports sumiu do menu"
    assert str(len(all_records())) in alvo[0], alvo[0]


# ---------------------------------------------------------------------------
# estetica do help: caixas, folha de estilo e equacoes
# ---------------------------------------------------------------------------

def test_nenhuma_caixa_sobra_como_div_ou_pre_solto(qapp):
    """MEDIDO em 2026-09-02: o motor de rich text do Qt IGNORA padding em div
    e pre. As 53 caixas escritas a mao apareciam com altura de uma linha e o
    texto colado na borda. Em td o padding e' honrado, entao caixa e' TABELA
    DE UMA CELULA."""
    import re as _re
    from bolt_analysis_studio.gui.documentation_tab import (
        DOCUMENTATION, _theme_html)

    for chave, sec in DOCUMENTATION.items():
        out = _theme_html(sec["content"])
        assert not _re.search(r"<div\b", out), f"{chave} ainda tem <div>"
        soltos = _re.findall(r"(?<!<td>)<pre\b", out)
        assert not soltos, f"{chave} tem <pre> fora de celula"


def test_a_folha_de_estilo_entra_no_documento(qapp):
    from bolt_analysis_studio.gui.documentation_tab import _theme_html

    out = _theme_html("<p>x</p>")
    assert "<style>" in out
    assert "border-collapse" in out
    assert "{{" not in out, "sobrou token nao resolvido na folha de estilo"


def test_toda_equacao_tem_as_DUAS_variantes_de_cor():
    """Um PNG transparente de cor unica fica invisivel num dos extremos de
    tema. Foi o que quase aconteceu com o icone do instalador."""
    import build_equations as be

    pasta = RECURSOS / "equations"
    faltando = []
    for nome, _latex, _alt in be.EQUACOES:
        for var in be.VARIANTES:
            if not (pasta / f"{nome}_{var}.png").is_file():
                faltando.append(f"{nome}_{var}")
    assert not faltando, f"variantes ausentes: {faltando}"


def test_a_variante_da_equacao_segue_o_tema(qapp):
    import re as _re
    from bolt_analysis_studio.gui.theme import Theme, THEME_DARK, THEME_LIGHT
    from bolt_analysis_studio.gui.documentation_tab import _theme_html

    html = '<p><img src="equations/eq_motion.png"></p>'
    saidas = {}
    for rot, pal in (("dark", THEME_DARK), ("light", THEME_LIGHT)):
        for k, v in pal.items():
            if hasattr(Theme, k):
                setattr(Theme, k, v)
        saidas[rot] = _re.search(r'src="([^"]+)"', _theme_html(html)).group(1)
    for k, v in THEME_DARK.items():          # devolve o tema
        if hasattr(Theme, k):
            setattr(Theme, k, v)
    assert saidas["dark"].endswith("_dark.png"), saidas
    assert saidas["light"].endswith("_light.png"), saidas


def test_toda_imagem_de_equacao_referenciada_existe(qapp):
    import re as _re
    from bolt_analysis_studio.gui.documentation_tab import (
        DOCUMENTATION, _theme_html)

    quebradas = []
    for chave, sec in DOCUMENTATION.items():
        for src in _re.findall(r'src="(equations/[^"]+)"',
                               _theme_html(sec["content"])):
            if not (RECURSOS / src).is_file():
                quebradas.append((chave, src))
    assert not quebradas, f"imagens de equacao quebradas: {quebradas[:5]}"
