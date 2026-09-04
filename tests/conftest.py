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

    mod_i18n = _sys.modules.get("bolt_analysis_studio.gui.i18n")
    if mod_i18n is not None:
        monkeypatch.setattr(mod_i18n, "_PREFS_DIR", destino, raising=False)
        monkeypatch.setattr(mod_i18n, "_PREFS_FILE",
                            destino / "preferences.json", raising=False)

    mod_win = _sys.modules.get("bolt_analysis_studio.gui.chrome.app_window")
    janela = getattr(mod_win, "ChromeWindow", None) if mod_win else None
    if janela is not None and hasattr(janela, "_PREFS"):
        monkeypatch.setattr(janela, "_PREFS", destino / "preferences.json",
                            raising=False)
    yield
