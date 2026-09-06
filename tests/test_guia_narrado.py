# -*- coding: utf-8 -*-
"""Guia de uso narrado (2026-09-05): um HTML por aba, PT e EN, voz Antonio.

O conteudo (New_Theory/guia_conteudo.py) e' a unica fonte; este teste garante
que ele esta completo nas duas linguas, que so pede prints que o build tira,
que fala a lingua do usuario (nada de vocabulario de desenvolvimento) e que
as paginas geradas trazem print, player e cada controle. O menu Ajuda abre o
guia no idioma corrente e, sem o guia instalado, avisa em vez de quebrar.
"""
from __future__ import annotations

import os
import re
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "New_Theory"))
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import guia_conteudo as gc                                   # noqa: E402
import build_guia_narrado as bg                              # noqa: E402

# vocabulario de quem desenvolve, que o usuario nunca deve ler (mesma lista
# do smoke do chrome) — mais o nome que saiu do projeto em 2026-09-04
_PROIBIDO = ("repositório", "repositorio", "gerador de casos", "registry",
             "fingerprint", "UFU")
_STORE = re.compile("[^a-z]store[^a-z]")


def _textos(passo, idx):
    yield passo["titulo"][idx]
    yield passo["narracao"][idx]
    for nome, txt in passo["controles"]:
        yield bg.nome_no_idioma(nome, idx)
        yield txt[idx]
    if passo.get("erro_comum"):
        yield passo["erro_comum"][idx]


def test_conteudo_completo_nas_duas_linguas():
    chaves = [p["chave"] for p in gc.PASSOS]
    assert len(chaves) == len(set(chaves)), "chave repetida"
    assert len(gc.PASSOS) >= 12, "o guia cobre cada aba e cada dialogo"
    for p in gc.PASSOS:
        assert re.fullmatch(r"[0-9]{2}_[a-z_]+", p["chave"]), p["chave"]
        for campo in ("titulo", "narracao"):
            assert len(p[campo]) == 2 and all(p[campo]), (p["chave"], campo)
        assert p["controles"], f"{p['chave']}: nenhum controle explicado"
        for nome, txt in p["controles"]:
            ok_nome = bool(nome) if isinstance(nome, str) else (len(nome) == 2 and all(nome))
            assert ok_nome and len(txt) == 2 and all(txt), (p["chave"], nome)
        if p.get("erro_comum"):
            assert len(p["erro_comum"]) == 2 and all(p["erro_comum"])
        # a narracao e' para ser ouvida: PT e EN sao textos distintos
        assert p["narracao"][0] != p["narracao"][1], p["chave"]


def test_so_pede_prints_que_o_build_tira():
    pedidos = {ch for p in gc.PASSOS for ch, _ in bg.imagens_do(p)}
    assert pedidos <= set(bg.PRINTS), sorted(pedidos - set(bg.PRINTS))


def test_licoes_tem_varias_imagens_com_legenda():
    """O pedido de 2026-09-05 e' explicito: "mais de uma imagem por tema".
    As licoes de construir modelo e de consultar a validacao sao as duas que
    precisam disso, e toda imagem multipla tem legenda nas duas linguas."""
    varios = [p for p in gc.PASSOS if len(bg.imagens_do(p)) > 1]
    assert len(varios) >= 6, [p["chave"] for p in varios]
    for chave in ("05_primeiro_modelo", "12_consultar_validacao"):
        p = next(x for x in gc.PASSOS if x["chave"] == chave)
        assert len(bg.imagens_do(p)) >= 4, chave
    for p in varios:
        for ch, leg in bg.imagens_do(p):
            assert leg and len(leg) == 2 and all(leg), (p["chave"], ch)


def test_vozes_sao_as_pedidas():
    assert gc.VOZES == {"pt": "pt-BR-AntonioNeural", "en": "en-US-AndrewNeural"}


@pytest.mark.parametrize("idx", [0, 1], ids=["pt", "en"])
def test_fala_a_lingua_do_usuario(idx):
    for p in gc.PASSOS:
        for t in _textos(p, idx):
            baixo = t.lower()
            for palavra in _PROIBIDO:
                assert palavra.lower() not in baixo, (p["chave"], palavra, t)
            assert not _STORE.search(" " + baixo + " "), (p["chave"], t)


def test_pagina_traz_print_player_transcricao_e_cada_controle():
    p = gc.PASSOS[4]
    audio = {p["chave"]: p["chave"] + ".mp3"}
    primeira = bg.imagens_do(p)[0][0]
    for lang, idx in (("pt", 0), ("en", 1)):
        html = bg._pagina(lang, p, 4, len(gc.PASSOS), gc.PASSOS, audio)
        assert f'src="img/{primeira}.png"' in html
        assert f'src="audio/{p["chave"]}.mp3"' in html
        assert gc.VOZES[lang] in html
        assert p["narracao"][idx] in html or bg.html.escape(p["narracao"][idx]) in html
        for nome, txt in p["controles"]:
            assert bg.html.escape(bg.nome_no_idioma(nome, idx)) in html
            assert bg.html.escape(txt[idx]) in html
        # navegacao: anterior, proximo e a outra lingua
        assert gc.PASSOS[3]["chave"] + ".html" in html
        assert gc.PASSOS[5]["chave"] + ".html" in html
        outro = "en" if lang == "pt" else "pt"
        assert f"../{outro}/{p['chave']}.html" in html


def test_nome_de_controle_segue_o_idioma_da_pagina():
    """Defeito da 1a versao (2026-09-05): nomes so' em PT apareciam nas paginas
    EN ao lado de prints EN. Agora um nome e' str (rotulo igual nas duas linguas)
    ou (pt, en); a pagina EN mostra o EN e nao o PT quando diferem."""
    n = len(gc.PASSOS)
    pares = 0
    for i, p in enumerate(gc.PASSOS):
        en = bg._pagina("en", p, i, n, gc.PASSOS, {})
        pt = bg._pagina("pt", p, i, n, gc.PASSOS, {})
        for nome, _ in p["controles"]:
            if isinstance(nome, tuple) and nome[0] != nome[1]:
                pares += 1
                assert f"<td>{bg.html.escape(nome[1])}</td>" in en, (p["chave"], nome)
                assert f"<td>{bg.html.escape(nome[0])}</td>" not in en, (p["chave"], nome)
                assert f"<td>{bg.html.escape(nome[0])}</td>" in pt, (p["chave"], nome)
    assert pares >= 30, "o guia traduz os nomes de controle que a tela traduz"


def test_glossario_completo_nas_duas_linguas():
    assert len(gc.GLOSSARIO) >= 30
    termos_pt = [g[0] for g in gc.GLOSSARIO]
    assert len(termos_pt) == len(set(termos_pt)), "termo PT repetido"
    for g in gc.GLOSSARIO:
        assert len(g) == 4 and all(isinstance(x, str) and x.strip() for x in g), g
    for lang, idx in (("pt", 0), ("en", 1)):
        html = bg._glossario(lang, gc.GLOSSARIO)
        for g in gc.GLOSSARIO:
            assert bg.html.escape(g[idx]) in html and bg.html.escape(g[2 + idx]) in html
        for palavra in _PROIBIDO:
            assert palavra.lower() not in html.lower(), palavra


def test_pagina_sem_audio_nao_quebra_e_avisa():
    p = gc.PASSOS[0]
    html = bg._pagina("pt", p, 0, len(gc.PASSOS), gc.PASSOS, audio={})
    assert "<audio" not in html
    assert "Áudio não gerado" in html


def test_indice_lista_todos_os_passos():
    html = bg._indice("en", gc.PASSOS, audio={})
    for p in gc.PASSOS:
        assert f'href="{p["chave"]}.html"' in html
        assert bg.html.escape(p["titulo"][1]) in html


# --- o produto gerado, quando existe --------------------------------------

_GUIA = RAIZ / "New_Theory" / "guia_uso"


@pytest.mark.skipif(not (_GUIA / "pt" / "index.html").is_file(),
                    reason="rode New_Theory/build_guia_narrado.py")
@pytest.mark.parametrize("lang", ["pt", "en"])
def test_guia_gerado_tem_pagina_print_e_audio_por_passo(lang):
    pasta = _GUIA / lang
    assert (pasta / "index.html").is_file()
    assert (pasta / "glossario.html").is_file()
    for p in gc.PASSOS:
        assert (pasta / f"{p['chave']}.html").is_file(), p["chave"]
        for ch, _ in bg.imagens_do(p):
            png = pasta / "img" / f"{ch}.png"
            assert png.is_file() and png.stat().st_size > 5_000, png
        mp3 = pasta / "audio" / f"{p['chave']}.mp3"
        assert mp3.is_file() and mp3.stat().st_size > 10_000, mp3


# --- o menu Ajuda ----------------------------------------------------------

def _janela(qapp):
    """`qapp` e' a fixture de sessao: um QApplication criado aqui como
    temporario sem referencia e' destruido na hora pelo PyQt6, e o ChromeWindow
    nasce sem aplicacao — qFatal, processo morto sem traceback (2026-09-05)."""
    from bolt_analysis_studio.core.app_state import get_app_state
    from bolt_analysis_studio.gui.chrome.app_window import ChromeWindow
    return ChromeWindow(get_app_state())


def _acoes(win, menu_titulo):
    for a in win.menuBar().actions():
        if a.menu() is not None and a.menu().title() == menu_titulo:
            return {x.text(): x for x in a.menu().actions() if x.text()}
    raise AssertionError(f"menu {menu_titulo!r} nao existe")


def test_menu_ajuda_tem_o_guia_nas_duas_linguas(qapp):
    from bolt_analysis_studio.gui.i18n import Lang
    win = _janela(qapp)
    try:
        acoes = _acoes(win, "Ajuda")
        alvo = [t for t in acoes if "Guia de uso narrado" in t]
        assert alvo, acoes
        # primeiro item do menu, e com atalho proprio: um item que ninguem
        # acha e' um item que nao existe (2026-09-05)
        assert list(acoes)[0] == alvo[0], list(acoes)
        assert acoes[alvo[0]].shortcut().toString() == "Shift+F1"
        Lang.set_lang("en")
        win._tr.retranslate()
        acoes = _acoes(win, "Help")
        assert [t for t in acoes if "Narrated user guide" in t], acoes
    finally:
        Lang.set_lang("pt")
        win.close()


def test_a_documentacao_tem_botao_para_o_guia(qapp, monkeypatch):
    """Segunda porta: quem esta' perdido abre a documentacao, nao o menu."""
    from PyQt6.QtWidgets import QPushButton
    import bolt_analysis_studio.gui.documentation_tab as doc_mod

    chamou = []
    monkeypatch.setattr(doc_mod, "abrir_guia_narrado",
                        lambda: chamou.append(True) or "")
    doc = doc_mod.DocumentationTab()
    try:
        botoes = [b for b in doc.findChildren(QPushButton)
                  if "narrado" in b.text().lower() or "narrated" in b.text().lower()]
        assert botoes, [b.text() for b in doc.findChildren(QPushButton)]
        botoes[0].click()
        assert chamou, "o botao da documentacao nao abre o guia"
    finally:
        doc.close()


def test_abrir_guia_sem_arquivo_avisa_e_com_arquivo_abre_no_idioma(qapp, tmp_path, monkeypatch):
    import webbrowser
    import bolt_analysis_studio.validation.inputs as inputs
    from bolt_analysis_studio.gui.i18n import Lang
    monkeypatch.setattr(inputs, "repo_root", lambda: tmp_path)
    abertos, avisos = [], []
    monkeypatch.setattr(webbrowser, "open", lambda u, *a, **k: abertos.append(u))
    win = _janela(qapp)
    monkeypatch.setattr(win.prompt, "set_prompt", lambda t, *a, **k: avisos.append(t))
    try:
        win._open_guia()
        assert not abertos and avisos and "não está instalado" in avisos[-1]
        alvo = tmp_path / "New_Theory" / "guia_uso" / "en" / "index.html"
        alvo.parent.mkdir(parents=True)
        alvo.write_text("<html></html>", encoding="utf-8")
        Lang.set_lang("en")
        win._open_guia()
        assert abertos and abertos[-1].endswith("guia_uso/en/index.html")
    finally:
        Lang.set_lang("pt")
        win.close()


# --- lexico: o guia so' nomeia o que existe na tela ------------------------

# nomes de REGIAO (descrevem o que se ve, nao sao rotulos): nao se cobram
_DESCRITIVOS = {
    "Barra de módulos (1 Model … 6 Report)", "Module bar (1 Model … 6 Report)",
    "Campo de busca", "Search field", "Coluna Censo", "Census column",
    "Coluna Critério", "Criterion column", "Coluna MAE", "MAE column",
    "Rodapé", "Footer", "Bloco no viewport", "Block in the viewport",
    "≡ / ▾ ao lado de k, c, m", "≡ / ▾ next to k, c, m",
    "Distintivo RUNNING / DONE / ERROR", "RUNNING / DONE / ERROR badge",
    "Aba Run", "Run tab", "Aba Validation", "Validation tab",
    "Árvore fonte → curva", "Source → curve tree", "Gráfico", "Plot",
    "Métricas", "Metrics", "Linha de prompt", "Prompt line",
    "Árvore de seções", "Section tree", "E, Sy, Su, ρ",
    "Decomposição por mecanismo", "Decomposition by mechanism",
    "Curva de referência: Caso da validação / Arquivo CSV…",
    "Reference curve: Validation case / CSV file…",
}
_ATALHO = re.compile(r"\((Ctrl|Shift|F1)[^)]*\)|Ctrl\+\S+|Shift\+\S+|^F1$")


def _fonte_da_tela() -> str:
    """Todo o codigo da interface, com os escapes \\uXXXX resolvidos: o
    inspector escreve "Initial \\u03bc:" e "Preload F\\u2080:" no fonte, e a
    tela mostra "Initial μ:" e "Preload F₀:"."""
    gui = RAIZ / "src" / "bolt_analysis_studio" / "gui"
    fonte = "\n".join(f.read_text(encoding="utf-8", errors="replace")
                      for f in gui.rglob("*.py"))
    fonte = re.sub(r"\\u([0-9a-fA-F]{4})",
                   lambda m: chr(int(m.group(1), 16)), fonte)
    return fonte.replace("...", "…")


def test_cada_controle_do_guia_existe_no_codigo_da_tela():
    """Revisao lexica de 2026-09-05: um controle que o guia nomeia e a tela
    nao mostra e' um erro de leitura para quem segue o guia. Cada nome (ou
    cada parte, separada por ' / ' e ' → ') tem de existir, letra por letra,
    no codigo da interface — nas duas linguas."""
    fonte = _fonte_da_tela()
    faltam = []
    for p in gc.PASSOS:
        for nome, _ in p["controles"]:
            for n in (nome if isinstance(nome, tuple) else (nome,)):
                if n in _DESCRITIVOS:
                    continue
                limpo = _ATALHO.sub("", n).replace("...", "…").strip(" /")
                if not limpo or limpo in fonte:
                    continue
                for parte in re.split(r" / | → | › ", limpo):
                    parte = parte.strip()
                    if parte and not _ATALHO.search(parte) and parte not in fonte:
                        faltam.append((p["chave"], n, parte))
    assert not faltam, faltam


def test_os_numeros_da_narracao_sao_os_do_corpus():
    """A narracao fala 'duzentas e sete curvas', 'duzentas e cinco do censo',
    'vinte e oito fontes', 'vinte e cinco secoes' — por extenso, para a voz.
    Aqui cada numero e' conferido com o que o programa realmente tem, pelos
    mesmos predicados do artigo; se o corpus mudar, a narracao envelhece
    gritando, nao calada."""
    from bolt_analysis_studio.validation.case_registry import all_records
    from bolt_analysis_studio.validation.report_html import caso_comparavel
    from bolt_analysis_studio.gui.documentation_tab import DOCUMENTATION
    recs = all_records()
    vivos = {"total": len(recs),
             "censo": sum(1 for r in recs if caso_comparavel(r.source, r.case_id)),
             "fontes": len({r.source for r in recs}),
             "secoes": len(DOCUMENTATION)}
    pt = " ".join(p["narracao"][0] for p in gc.PASSOS)
    en = " ".join(p["narracao"][1] for p in gc.PASSOS)
    afirmado = {
        "total": (r"duzent[ao]s e sete", r"two hundred and seven", 207),
        "censo": (r"duzentas e cinco", r"two hundred and five", 205),
        "fontes": (r"vinte e oito", r"twenty-eight", 28),
        "secoes": (r"vinte e cinco", r"twenty-five", 25),
    }
    for chave, (rx_pt, rx_en, valor) in afirmado.items():
        assert re.search(rx_pt, pt) and re.search(rx_en, en), chave
        assert vivos[chave] == valor, (chave, "programa tem", vivos[chave],
                                       "narracao diz", valor)
