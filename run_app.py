#!/usr/bin/env python
"""
Bolt Analysis Studio v4.0 - Application Launcher

Prof. Leonardo Rosa Ribeiro da Silva, PhD
January 2026

This script launches the main Bolt Analysis Studio application.

Usage:
    python run_app.py              # Launch V2 chrome (Abaqus-style CAE shell, default)
    python run_app.py --v1         # Launch classic V1 (7 tabs, fallback)
    python run_app.py --builder    # Launch MSD Model Builder
    python run_app.py --help       # Show help

Requirements:
    - Python 3.10+
    - PyQt6
    - numpy
    - scipy
    - matplotlib
"""

import sys
import os
import argparse

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))


def _install_crash_logging():
    """Capture crashes (incl. C-level segfaults) + uncaught Python exceptions
    to a log file, so 'the app just closed' becomes diagnosable.

    Writes to ``crash_log.txt`` next to this script. faulthandler catches
    native crashes (Qt/segfault) that never reach a Python traceback;
    sys.excepthook catches uncaught Python exceptions in the main thread.
    """
    import faulthandler
    import traceback
    log_path = os.path.join(os.path.dirname(__file__), 'crash_log.txt')
    try:
        _fh = open(log_path, 'a', encoding='utf-8')
    except Exception:
        return
    faulthandler.enable(file=_fh, all_threads=True)

    _prev_hook = sys.excepthook

    def _hook(exc_type, exc, tb):
        try:
            _fh.write("\n=== Uncaught exception ===\n")
            traceback.print_exception(exc_type, exc, tb, file=_fh)
            _fh.flush()
        except Exception:
            pass
        # Also print to stderr and keep the app alive instead of dying silently.
        traceback.print_exception(exc_type, exc, tb)
        if _prev_hook is not None:
            try:
                _prev_hook(exc_type, exc, tb)
            except Exception:
                pass

    sys.excepthook = _hook


def main():
    """Main entry point."""
    _install_crash_logging()
    parser = argparse.ArgumentParser(
        description='Bolt Analysis Studio v4.0 - MSD-based bolt joint analysis'
    )
    parser.add_argument(
        '--builder',
        action='store_true',
        help='Launch MSD Model Builder'
    )
    parser.add_argument(
        '--v2',
        action='store_true',
        help='Launch the V2 chrome (Abaqus-style CAE shell) — now the default'
    )
    parser.add_argument(
        '--v1',
        action='store_true',
        help='Launch the classic V1 7-tab window (fallback)'
    )
    parser.add_argument(
        '--test',
        action='store_true',
        help='Run test suite instead of launching GUI'
    )
    parser.add_argument(
        '--theme',
        choices=['dark', 'light', 'green', 'engineering'],
        default=None,
        help='Override saved theme (dark, light, green, engineering)'
    )
    parser.add_argument(
        '--version',
        action='version',
        version='Bolt Analysis Studio v4.0 (January 2026)'
    )

    args = parser.parse_args()

    if args.test:
        # Run test suite
        import subprocess
        return subprocess.call([sys.executable, 'test_gui.py'])

    # Initialize Qt application
    from PyQt6.QtWidgets import QApplication
    from PyQt6.QtCore import QTimer

    app = QApplication(sys.argv)
    app.setApplicationName("Bolt Analysis Studio")
    app.setApplicationVersion("4.0")
    app.setOrganizationName("Bolt Analysis Studio")

    # Load and apply theme
    from bolt_analysis_studio.gui.theme import Theme
    if args.theme:
        saved = args.theme
    elif not args.v1 and not Theme._PREFS_FILE.exists():
        # Chrome (default) estreia na paleta Engineering Dark sem preferência salva.
        saved = "engineering"
    else:
        saved = Theme.load_theme_preference()
    Theme.set_theme(saved)
    app.setStyleSheet(Theme.get_stylesheet())

    from bolt_analysis_studio.gui.icons import icon
    app.setWindowIcon(icon("app_icon", size=256))

    # --- Splash screen ---
    # A splash ANIMA só enquanto o event loop está livre. Como a janela principal
    # é construída de forma SÍNCRONA (bloqueia o loop por ~1 s), construí-la logo
    # após splash.show() faz a animação NÃO rodar — o loop fica ocupado e, quando
    # volta, a splash já é dispensada. Por isso a janela é criada só DEPOIS de a
    # splash animar por _SPLASH_ANIM_SECONDS (bloco abaixo).
    _SPLASH_ANIM_SECONDS = 1.8
    if not args.builder:
        from bolt_analysis_studio.gui.splash import AnimatedSplashScreen
        _splash = AnimatedSplashScreen()
        _splash.show()
        app.processEvents()
    else:
        _splash = None

    if args.builder:
        # Launch MSD Model Builder
        from bolt_analysis_studio.gui.msd_builder import MSDBuilderWindow

        window = MSDBuilderWindow()
        window.showMaximized()

        # Add preset for demonstration
        window._add_preset("single_bolt")
    else:
        # Default agora é o chrome V2 (Abaqus-style CAE shell). --v1 força a V1
        # clássica de 7 abas, que permanece intacta como fallback.
        #
        # A construção da janela é adiada (QTimer) para a splash animar antes: a
        # __init__ bloqueia o loop, então só depois de _SPLASH_ANIM_SECONDS de
        # animação livre é que a janela é criada e assume. `_kept` segura a
        # referência — sem ela o PyQt coletaria a janela recém-criada no fim do
        # callback e ela sumiria.
        _kept = []

        def _build_and_show():
            if args.v1:
                from bolt_analysis_studio.gui.main_window import BoltAnalysisStudio
                window = BoltAnalysisStudio()
            else:
                from bolt_analysis_studio.gui.chrome.app_window import ChromeWindow
                window = ChromeWindow()
            _kept.append(window)
            window.showMaximized()
            if _splash is not None:
                _splash.finish(window)

        if _splash is not None:
            QTimer.singleShot(int(_SPLASH_ANIM_SECONDS * 1000), _build_and_show)
        else:
            _build_and_show()

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
