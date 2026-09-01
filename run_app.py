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
    python run_app.py --skip-deps-check    # Start without the dependency check

Requirements:
    - Python 3.10+
    - PyQt6, numpy, scipy, matplotlib

    Read from requirements.txt at startup. Whatever is missing is listed with
    the interpreter it would go into, and installed after you agree; nothing is
    installed without being asked, and nothing at all when there is no terminal
    to ask on.
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


# --------------------------------------------------------------- dependencies
# What the application needs to start, used when requirements.txt cannot be
# read. Kept here and not imported from the package: the package itself pulls
# numpy, so nothing under src/ can run before this check has passed.
_DEPS_FALLBACK = [("numpy", (1, 21, 0)), ("scipy", (1, 7, 0)),
                  ("matplotlib", (3, 5, 0)), ("PyQt6", (6, 4, 0))]


def _version_tuple(texto):
    """Leading numeric segments of a version, or None when there are none.

    "6.4.0.dev0+g12ab" -> (6, 4, 0); "unknown" -> None. Stopping at the first
    non-numeric segment is what makes a pre-release compare as its own release
    rather than as something older."""
    partes = []
    for seg in str(texto).split("."):
        digitos = ""
        for ch in seg:
            if not ch.isdigit():
                break
            digitos += ch
        if not digitos:
            break
        partes.append(int(digitos))
    return tuple(partes) or None


def _parse_requirements(texto):
    """requirements.txt -> [(distribution, minimum version or None)].

    Comment lines are dropped whole rather than stripped inline, because the
    optional block of that file is commented out entry by entry: reading it as
    required would install the report generators on someone who only wants to
    open the GUI."""
    specs = []
    for linha in texto.splitlines():
        linha = linha.strip()
        if not linha or linha.startswith("#"):
            continue
        for sep in (">=", "==", ">"):
            if sep in linha:
                nome, _, versao = linha.partition(sep)
                specs.append((nome.strip(), _version_tuple(versao.strip())))
                break
        else:
            specs.append((linha, None))
    return specs


def _installed_version(nome):
    """Installed version of a distribution, or None when it is absent.

    A module that imports but carries no metadata reports "unknown", which
    compares as unreadable and therefore as good enough: this check exists to
    unblock someone who lacks a dependency, not to invent an obstacle for
    someone who has it."""
    import importlib.metadata
    import importlib.util

    try:
        return importlib.metadata.version(nome)
    except importlib.metadata.PackageNotFoundError:
        pass
    try:
        if importlib.util.find_spec(nome) is not None:
            return "unknown"
    except (ImportError, ValueError):
        pass
    return None


def _spec_text(nome, minimo):
    return f"{nome}>={'.'.join(str(x) for x in minimo)}" if minimo else nome


def _command_text(comando):
    """The command written so it survives being pasted into a shell.

    `pip install numpy>=1.21.0` unquoted is a redirection: the shell reads the
    '>' and writes a file called '=1.21.0' while installing plain numpy. That
    holds in bash, cmd and PowerShell alike, so every argument carrying a
    character a shell acts on is quoted. Only the printed form needs this;
    subprocess is handed the list and never sees a shell."""
    partes = []
    for arg in comando:
        if any(ch in arg for ch in ' <>|&^"'):
            partes.append('"' + arg.replace('"', '\\"') + '"')
        else:
            partes.append(arg)
    return " ".join(partes)


def _dependency_gaps(specs, version_of):
    """The specs that are absent or older than asked, worded as pip takes them.

    `version_of` is injected so the whole decision can be tested without
    touching the environment of whoever runs the tests."""
    faltando = []
    for nome, minimo in specs:
        atual = version_of(nome)
        if atual is None:
            faltando.append(_spec_text(nome, minimo))
            continue
        if minimo is None:
            continue
        tupla = _version_tuple(atual)
        if tupla is not None and tupla < minimo:
            faltando.append(_spec_text(nome, minimo))
    return faltando


def _ensure_dependencies():
    """Check the runtime dependencies and offer to install what is missing.

    Returns True when the application can start. With no terminal to ask (a
    service, a CI job) it never installs on its own: it prints the command and
    gives up, because a silent install is not something to do to an environment
    nobody is watching."""
    import subprocess

    arquivo = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           "requirements.txt")
    try:
        with open(arquivo, encoding="utf-8") as fh:
            specs = _parse_requirements(fh.read())
    except OSError:
        specs = []
    specs = specs or list(_DEPS_FALLBACK)

    faltando = _dependency_gaps(specs, _installed_version)
    if not faltando:
        return True

    comando = [sys.executable, "-m", "pip", "install", *faltando]
    plural = "y" if len(faltando) == 1 else "ies"
    verbo = "is" if len(faltando) == 1 else "are"
    print()
    print(f"Bolt Analysis Studio needs {len(faltando)} dependenc{plural} "
          f"that {verbo} not installed:")
    for spec in faltando:
        print(f"    {spec}")
    print()
    print(f"Target environment: {sys.executable}")

    try:
        interativo = sys.stdin is not None and sys.stdin.isatty()
    except (AttributeError, ValueError):
        interativo = False
    if not interativo:
        print()
        print("No terminal to ask on, so nothing was installed. Run:")
        print("    " + _command_text(comando))
        return False

    print()
    try:
        resposta = input("Install them now? [Y/n] ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        resposta = "n"
    if resposta not in ("", "y", "yes", "s", "sim"):
        print()
        print("Nothing installed. To do it by hand:")
        print("    " + _command_text(comando))
        return False

    print()
    try:
        subprocess.check_call(comando)
    except (subprocess.CalledProcessError, OSError) as exc:
        print()
        print(f"pip failed ({exc}). To do it by hand:")
        print("    " + _command_text(comando))
        return False

    import importlib
    importlib.invalidate_caches()
    ainda = _dependency_gaps(specs, _installed_version)
    if ainda:
        print()
        print("pip reported success but these are still missing: "
              + ", ".join(ainda))
        print("A virtual environment or a second Python may be in the way.")
        return False
    print()
    print("Dependencies installed. Starting.")
    print()
    return True


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
        '--skip-deps-check',
        action='store_true',
        help='Start without checking that the dependencies are installed'
    )
    parser.add_argument(
        '--version',
        action='version',
        version='Bolt Analysis Studio v4.0 (January 2026)'
    )

    args = parser.parse_args()

    # Before the first import that needs them, --test included: that path
    # shells out to the suite, which needs the same dependencies the GUI does.
    if not args.skip_deps_check and not _ensure_dependencies():
        return 1

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

    # Idioma (PT/EN) — restaura a preferência antes de construir a janela, para
    # que os textos já saiam no idioma salvo. Toggle na GUI em Exibir/View.
    from bolt_analysis_studio.gui.i18n import Lang
    Lang.load_preference()

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
