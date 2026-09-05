# -*- coding: utf-8 -*-
"""A janela que um teste cria nao sobrevive ao teste (conftest, 2026-09-05).

Dois testes em ordem: o primeiro cria um ChromeWindow e so' fecha, como
dezenas de testes fazem; o segundo confere que ele nao esta' mais vivo. Sem
a limpeza do conftest, as janelas acumulavam e cada troca de tema re-poliu
todas — 47 min na varredura de temas da suite inteira, 23 s sozinha.
"""


def test_a_cria_uma_janela_e_so_fecha(qapp):
    from bolt_analysis_studio.gui.chrome.app_window import ChromeWindow
    win = ChromeWindow()
    win.show()
    qapp.processEvents()
    win.close()


def test_b_a_janela_do_teste_anterior_ja_morreu(qapp):
    from bolt_analysis_studio.gui.chrome.app_window import ChromeWindow
    vivas = [w for w in qapp.topLevelWidgets() if isinstance(w, ChromeWindow)]
    assert not vivas, f"{len(vivas)} ChromeWindow(s) vazaram do teste anterior"
