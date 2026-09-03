"""Abrir e salvar projeto no chrome V2 (2026-09-03).

Ate' esta data o menu Arquivo do chrome padrao tinha "Nova Analise" e "Sair":
nao dava para abrir um .msd salvo nem para gravar o que foi editado. Os 210
casos da validacao ja' existiam como modelo desde 02-09 e nao havia porta.

O teste de ida e volta e' o que importa aqui, e pegou um defeito real: salvar
exportando so' do ESQUEMATICO perdia as 23 constantes adotadas, a geometria e
a citacao da fonte, porque o desenho nao conhece esses campos — eles vivem no
modelo do AppState. O arquivo abria com os 11 elementos e o F0 certos e estava
errado, que e' a mesma perda silenciosa que MSDModel.to_dict tinha, um andar
acima.
"""
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "src"))

import pytest                                                    # noqa: E402

CASO = RAIZ / "Models" / "SAVED_CASES" / "LU_2024" / "lu2024_M8_fig18_amp0p5.msd"


@pytest.fixture
def janela(qapp):
    from bolt_analysis_studio.core.app_state import get_app_state
    from bolt_analysis_studio.gui.chrome.app_window import ChromeWindow
    return ChromeWindow(get_app_state())


def test_o_menu_arquivo_tem_abrir_e_salvar(janela):
    from PyQt6.QtWidgets import QMenu

    arq = [m for m in janela.menuBar().findChildren(QMenu)
           if m.title() == "Arquivo"]
    assert arq, "o chrome V2 nao tem menu Arquivo"
    textos = [a.text() for a in arq[0].actions()]
    for esperado in ("Nova Análise…", "Abrir projeto…", "Salvar",
                     "Salvar como…"):
        assert esperado in textos, f"{esperado} ausente: {textos}"

    atalhos = {a.text(): a.shortcut().toString() for a in arq[0].actions()}
    assert atalhos["Abrir projeto…"] == "Ctrl+O"
    assert atalhos["Salvar"] == "Ctrl+S"


def test_a_pasta_padrao_e_a_dos_casos_dos_artigos(janela, monkeypatch, tmp_path):
    """Na primeira vez o dialogo abre nos 210 modelos dos artigos, que e' o
    que alguem quer antes de ter projeto proprio."""
    monkeypatch.setattr(type(janela), "_PREFS", tmp_path / "sem_prefs.json")
    d = janela._dir_inicial_projeto()
    assert "SAVED_CASES" in d, d
    assert list(Path(d).glob("*/*.msd")), "a pasta padrao nao tem .msd"


def test_a_pasta_padrao_passa_a_ser_a_ultima_usada(janela, monkeypatch, tmp_path):
    """Senao quem trabalha nos proprios modelos voltaria sempre aos artigos."""
    prefs = tmp_path / "prefs.json"
    monkeypatch.setattr(type(janela), "_PREFS", prefs)
    meu = tmp_path / "meus_projetos"
    meu.mkdir()
    janela._lembra_dir_projeto(str(meu / "x.msd"))
    assert janela._dir_inicial_projeto() == str(meu)


@pytest.mark.skipif(not CASO.is_file(), reason="rode build_saved_cases.py")
def test_abrir_carrega_o_modelo_e_reconstroi_o_esquematico(janela, qapp):
    from bolt_analysis_studio.core.models.model import MSDModel

    janela._after_wizard(MSDModel.load(str(CASO)))
    for _ in range(40):
        qapp.processEvents()
    m = janela.app_state.model
    assert len(m.elements) == 11
    assert m.global_loading.F_preload == pytest.approx(12000, rel=1e-3)
    assert len(getattr(m, "_v2_tuner_overrides", {})) == 23
    assert janela.model_controller.schematic.scene().items()


@pytest.mark.skipif(not CASO.is_file(), reason="rode build_saved_cases.py")
def test_salvar_preserva_constantes_adotadas_e_citacao(janela, qapp, tmp_path):
    """O invariante central. Salvar so' com o export do esquematico devolvia
    0 constantes e nenhuma citacao, e o arquivo PARECIA bom."""
    from bolt_analysis_studio.core.models.model import MSDModel

    janela._after_wizard(MSDModel.load(str(CASO)))
    for _ in range(40):
        qapp.processEvents()
    antes = janela.app_state.model

    alvo = tmp_path / "projeto.msd"
    janela._grava_projeto(str(alvo))
    assert alvo.is_file()

    volta = MSDModel.load(str(alvo))
    assert (getattr(volta, "_v2_tuner_overrides", {})
            == getattr(antes, "_v2_tuner_overrides", {}))
    assert (getattr(volta, "_v2_geometry_overrides", {})
            == getattr(antes, "_v2_geometry_overrides", {}))
    assert "validation case" in (volta.description or "")
    assert len(volta.elements) == len(antes.elements)


@pytest.mark.skipif(not CASO.is_file(), reason="rode build_saved_cases.py")
def test_o_titulo_da_janela_mostra_o_projeto_aberto(janela, qapp, tmp_path):
    from bolt_analysis_studio.core.models.model import MSDModel

    janela._after_wizard(MSDModel.load(str(CASO)))
    janela._grava_projeto(str(tmp_path / "meu.msd"))
    assert "meu.msd" in janela.windowTitle()
