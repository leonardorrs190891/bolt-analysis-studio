"""Pytest config: coloca src/ no sys.path pra os testes importarem
`bolt_analysis_studio` sem editable install."""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

# Qt headless: precisa vir antes de qualquer import de QtWidgets.
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest  # noqa: E402


@pytest.fixture(scope="session")
def qapp():
    """QApplication única para os testes de widget do chrome V2 (sem pytest-qt)."""
    from PyQt6.QtWidgets import QApplication
    app = QApplication.instance() or QApplication([])
    yield app


@pytest.fixture(autouse=True)
def _reset_app_state():
    """Zera o singleton AppState entre testes: desconecta receivers de
    model_changed e limpa model/results. Sem isto, ChromeWindows de testes
    anteriores se acumulam no singleton e quebram em _fit_view quando um teste
    seta st.model. NO-OP p/ testes que nunca importaram a GUI (checa
    sys.modules — nao forca import de PyQt6 nos testes numericos)."""
    import sys

    def _clear():
        mod = sys.modules.get("bolt_analysis_studio.core.app_state")
        inst = getattr(getattr(mod, "AppState", None), "_instance", None)
        if inst is None:
            return
        try:
            inst.model_changed.disconnect()
        except (TypeError, RuntimeError):
            pass
        inst._model = None
        inst._results = None

    _clear()
    yield
    _clear()


@pytest.fixture(autouse=True)
def _preferencias_isoladas(tmp_path_factory, monkeypatch):
    """Nenhum teste escreve em ~/.bolt_analysis_studio/preferences.json.

    Em 2026-09-03 dois testes de "abrir/salvar projeto" chamaram
    `_grava_projeto` com um tmp_path e gravaram `ultimo_dir_projeto` no arquivo
    REAL do usuario. Efeito na maquina dele: o Ctrl+O passou a abrir num
    diretorio temporario do pytest com 1 arquivo solto, em vez dos 207 casos
    dos artigos. Os modelos estavam la'; o que quebrou foi para onde o dialogo
    apontava.

    Um teste que altera a configuracao de quem o roda e' um defeito do teste.
    Isolar aqui, e nao em cada arquivo, e' o que impede o proximo esquecimento:
    protege a suite inteira, inclusive testes que ainda nao existem.

    NO-OP para quem nunca importou a GUI — checa sys.modules em vez de forcar
    o import de PyQt6 nos testes numericos.
    """
    import sys as _sys

    destino = tmp_path_factory.mktemp("prefs")

    # i18n e' Python puro (json + pathlib), entao pode ser importado SEMPRE —
    # e tem de ser. A versao anterior so' o remendava se ja' estivesse em
    # sys.modules; um teste que importava o chrome dentro da funcao chegava
    # aqui antes do import, saia sem remendo, e o toggle de idioma gravou
    # `lang=en` no preferences.json REAL do usuario (2026-09-04, a mesma
    # classe de defeito do `ultimo_dir_projeto`). O idioma tambem e' fixado em
    # portugues para a suite ser deterministica: testes que procuram o menu
    # "Arquivo" pelo titulo quebrariam numa maquina cuja preferencia e' ingles.
    import bolt_analysis_studio.gui.i18n as mod_i18n
    monkeypatch.setattr(mod_i18n, "_PREFS_DIR", destino, raising=False)
    monkeypatch.setattr(mod_i18n, "_PREFS_FILE",
                        destino / "preferences.json", raising=False)
    monkeypatch.setattr(mod_i18n.Lang, "current", "pt")

    mod_win = _sys.modules.get("bolt_analysis_studio.gui.chrome.app_window")
    janela = getattr(mod_win, "ChromeWindow", None) if mod_win else None
    if janela is not None and hasattr(janela, "_PREFS"):
        monkeypatch.setattr(janela, "_PREFS", destino / "preferences.json",
                            raising=False)
    yield


@pytest.fixture(autouse=True)
def _widgets_do_teste_morrem_com_ele():
    """Toda janela criada DENTRO de um teste e' destruida no fim dele.

    Medido em 2026-09-05, suite inteira num so' processo: a varredura de temas
    do smoke levou 2812 s (47 min) — sozinha, leva 23 s. `_apply_theme` aplica
    o stylesheet no nivel da aplicacao, e o Qt re-polia TODOS os widgets vivos:
    centenas de ChromeWindows que testes anteriores fecharam (`close()` esconde,
    nao destroi) continuavam no processo, cada uma com milhares de widgets.
    O custo de cada troca de tema crescia com o numero de testes ja' rodados.

    Regra: o que nasce no teste morre no teste. Fixtures de modulo/sessao
    nascem ANTES desta (pytest instancia por escopo, do maior para o menor),
    entao ja' estao na fotografia inicial e sao preservadas. NO-OP para quem
    nunca importou QtWidgets — nao forca PyQt6 nos testes numericos.
    """
    import sys as _sys

    def _vivos():
        qtw = _sys.modules.get("PyQt6.QtWidgets")
        app = qtw.QApplication.instance() if qtw else None
        return app, (set(app.topLevelWidgets()) if app else set())

    _, antes = _vivos()
    yield
    app, depois = _vivos()
    if app is None:
        return
    for w in depois - antes:
        try:
            w.hide()            # NAO close(): o closeEvent da janela V1 abre
            w.deleteLater()     # um QMessageBox modal e a suite trava (medido)
        except RuntimeError:                      # ja' destruido pelo teste
            pass
    from PyQt6.QtCore import QEvent
    app.sendPostedEvents(None, QEvent.Type.DeferredDelete)
    app.processEvents()
