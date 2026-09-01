"""#6: splash segue o tema (cores de chrome via Theme; materiais ficam físicos)."""


def test_splash_references_theme():
    import bolt_analysis_studio.gui.splash as m
    src = open(m.__file__, encoding="utf-8").read()
    assert "from .theme import Theme" in src or "import Theme" in src


def test_splash_bg_not_hardcoded_catppuccin():
    import bolt_analysis_studio.gui.splash as m
    src = open(m.__file__, encoding="utf-8").read()
    assert "'#1e1e2e'" not in src and "'#181825'" not in src


def test_splash_renders_without_crash(qapp):
    from bolt_analysis_studio.gui.splash import AnimatedSplashScreen
    s = AnimatedSplashScreen()
    try:
        pm = s.grab()          # dispara paintEvent
        assert pm.width() > 0 and pm.height() > 0
    finally:
        s.finish(None)         # para o timer + fecha
