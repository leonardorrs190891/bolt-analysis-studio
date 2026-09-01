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
