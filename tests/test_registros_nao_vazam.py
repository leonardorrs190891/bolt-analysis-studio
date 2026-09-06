# -*- coding: utf-8 -*-
"""Idioma e tema nao seguram janelas mortas (2026-09-05).

Dois registros globais guardavam METODOS LIGADOS de cada janela: `Lang`, para
retraduzir, e `Theme`, para repintar. Com referencia forte, toda janela ja'
criada ficava viva presa neles, e duas coisas saiam disso:

  · cada troca de tema repintava TODAS as janelas de TODOS os testes ja'
    rodados — a varredura de temas da suite levava 47 minutos, e sozinha 23
    segundos;
  · alternar o idioma chamava `setText` de widgets ja' destruidos, o que no
    PyQt6 nem sempre levanta RuntimeError: derruba o processo com violacao de
    acesso (o segfault que apareceu ao rodar cinco arquivos de teste juntos).

A correcao e' a mesma nos dois: metodo ligado entra como referencia FRACA, e
sai da lista sozinho quando o dono morre.
"""
import gc
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))


def _conta(registro) -> int:
    return len(registro._vivos())


def test_lang_solta_a_janela_quando_ela_morre(qapp):
    from bolt_analysis_studio.gui.chrome.app_window import ChromeWindow
    from bolt_analysis_studio.gui.i18n import Lang

    antes = _conta(Lang)
    win = ChromeWindow()
    assert _conta(Lang) > antes, "a janela nem chegou a se registrar"
    win.close()
    win.deleteLater()
    qapp.processEvents()
    del win
    gc.collect()
    assert _conta(Lang) == antes, "o idioma ficou segurando a janela morta"


def test_theme_solta_a_janela_quando_ela_morre(qapp):
    from bolt_analysis_studio.gui.chrome.app_window import ChromeWindow
    from bolt_analysis_studio.gui.theme import Theme

    antes = _conta(Theme)
    win = ChromeWindow()
    win.close()
    win.deleteLater()
    qapp.processEvents()
    del win
    gc.collect()
    assert _conta(Theme) <= antes, "o tema ficou segurando a janela morta"


def test_alternar_idioma_depois_de_fechar_nao_derruba(qapp):
    """A reproducao do segfault: cria, destroi, alterna. Tem de sobreviver."""
    from bolt_analysis_studio.gui.chrome.app_window import ChromeWindow
    from bolt_analysis_studio.gui.i18n import Lang

    for _ in range(3):
        win = ChromeWindow()
        win.close()
        win.deleteLater()
        qapp.processEvents()
        del win
    gc.collect()
    try:
        Lang.set_lang("en")
        qapp.processEvents()
        Lang.set_lang("pt")
        qapp.processEvents()
    finally:
        Lang.set_lang("pt")


def test_funcao_solta_continua_registrada():
    """So' o metodo ligado vira referencia fraca: uma funcao de modulo, que
    nao tem dono, precisa continuar valendo."""
    from bolt_analysis_studio.gui.i18n import Lang

    chamou = []

    def ouvinte():
        chamou.append(True)

    Lang.register_callback(ouvinte)
    try:
        Lang.set_lang("en")
        assert chamou, "callback de funcao solta foi perdido"
    finally:
        Lang.unregister_callback(ouvinte)
        Lang.set_lang("pt")


def test_criar_e_fechar_muitas_janelas_nao_incha_os_registros(qapp):
    """O invariante que a varredura de temas quebrou.

    Nao se exige que a janela morra na hora — o Qt e o coletor decidem quando.
    Exige-se que os REGISTROS globais nao cresçam sem limite, porque e' deles
    que sai o custo: cada troca de tema chama um callback por janela ainda
    registrada, e cada troca de idioma, um por grupo de traducao.
    """
    from bolt_analysis_studio.gui.chrome.app_window import ChromeWindow
    from bolt_analysis_studio.gui.i18n import Lang
    from bolt_analysis_studio.gui.theme import Theme

    gc.collect()
    base_tema, base_lang = _conta(Theme), _conta(Lang)
    for _ in range(4):
        win = ChromeWindow()
        win.close()
        del win
        gc.collect()
        qapp.processEvents()
    gc.collect()

    # margem de uma janela: o Qt pode segurar a ultima ate' o proximo ciclo
    por_janela_tema = 3      # medido: 3 callbacks de tema por ChromeWindow
    por_janela_lang = 7      # e 7 grupos de traducao
    assert _conta(Theme) <= base_tema + por_janela_tema, (
        f"tema: {base_tema} -> {_conta(Theme)} apos 4 janelas fechadas")
    assert _conta(Lang) <= base_lang + por_janela_lang, (
        f"idioma: {base_lang} -> {_conta(Lang)} apos 4 janelas fechadas")
