"""Testes de GUI (V1): tema, ProjectInfo, tabela visual de elementos, abas,
MSD Builder e a integracao Builder -> janela principal.

RESSUSCITADO em 2026-07-28. Este arquivo estava na lista de `--ignore` da suite
desde o fork, registrado como "import `ElementCategory` quebrado". O import era
1 dos 3 problemas; os outros dois eram um runner artesanal (ver o comentario no
fim do arquivo) e duas asserts que envelheceram contra o codigo. Nenhum era do
codigo de producao: os tres eram do teste.

QApplication, offscreen e o reset do singleton `AppState` vem do
`tests/conftest.py` (fixture `qapp`) — nao construa nada disso aqui.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


def test_theme():
    """Test Theme class."""
    print("Testing Theme class...")
    
    from bolt_analysis_studio.gui.main_window import Theme
    
    # Verify all color attributes exist
    colors = ['BASE', 'MANTLE', 'CRUST', 'SURFACE0', 'SURFACE1', 'SURFACE2',
              'TEXT', 'SUBTEXT', 'OVERLAY', 'BLUE', 'GREEN', 'RED', 'PEACH',
              'YELLOW', 'MAUVE', 'TEAL', 'PINK', 'SKY', 'LAVENDER']
    
    for color in colors:
        assert hasattr(Theme, color), f"Missing color: {color}"
        value = getattr(Theme, color)
        assert value.startswith('#'), f"Invalid color format: {color}={value}"
    
    # Test stylesheet generation
    stylesheet = Theme.get_stylesheet()
    assert len(stylesheet) > 1000, "Stylesheet too short"
    assert 'QMainWindow' in stylesheet
    assert 'QTabWidget' in stylesheet
    assert 'QPushButton' in stylesheet
    
    print(f"  ✓ {len(colors)} colors defined")
    print(f"  ✓ Stylesheet: {len(stylesheet)} characters")
    print("  ✓ Theme test passed\n")


def test_project_info():
    """Test ProjectInfo dataclass."""
    print("Testing ProjectInfo...")
    
    from bolt_analysis_studio.gui.main_window import ProjectInfo
    
    # Create with defaults
    info = ProjectInfo()
    assert info.name == "Untitled Project"
    assert info.standard == "VDI 2230"
    # `company` tem default VAZIO. O teste exigia "Petrobras" — um default que o
    # codigo de producao ja nao tem (e nao deveria: cravar o nome de uma empresa
    # como default de um dataclass generico e' vazamento de contexto para dentro
    # da biblioteca). Aqui prendemos o default REAL; se alguem re-cravar um nome,
    # este assert reclama.
    assert info.company == ""
    assert info.revision == "A"
    assert info.length_unit == "mm"
    
    # Create with custom values
    info2 = ProjectInfo(
        name="Test Project",
        author="John Doe",
        standard="EN 1591-1 (2013)",
        material_standard="ASTM A320/A320M",
        length_unit="m"
    )
    
    # Test serialization
    data = info2.to_dict()
    assert data['name'] == "Test Project"
    assert data['author'] == "John Doe"
    assert data['standard'] == "EN 1591-1 (2013)"
    
    # Test deserialization
    info3 = ProjectInfo.from_dict(data)
    assert info3.name == info2.name
    assert info3.author == info2.author
    
    print("  ✓ Default values correct")
    print("  ✓ Custom values work")
    print("  ✓ Serialization/deserialization works")
    print("  ✓ ProjectInfo test passed\n")


def test_element_visuals():
    """A tabela visual de elementos esta completa e bem-formada.

    Reescrito em 2026-07-28. A versao anterior importava `ElementCategory` e
    exigia `isinstance(visual.category, ElementCategory)` — e **`ElementCategory`
    nunca existiu** em `src/` (verificado com grep no pacote inteiro), nem o campo
    `category` existe em `ElementVisual`. O teste foi escrito contra um desenho
    que nao foi implementado: as categorias vivem como COMENTARIOS agrupando o
    dict ("# Bolt Elements", "# Member Elements", "# Contact Elements"), nao como
    dado. Era um ImportError garantido desde o primeiro dia, o que explica o
    arquivo ter nascido excluido da suite.

    Tambem pedia a chave `'CONTACT'`, que nao existe — o generico e'
    `GENERIC_CONTACT`. Agora as chaves exigidas sao as que o codigo tem.
    """
    import dataclasses

    from bolt_analysis_studio.gui.msd_builder import ELEMENT_VISUALS, ElementVisual

    # o campo `category` NAO existe; se alguem o adicionar, este assert avisa que
    # ha um teste de categoria a escrever (em vez de ressuscitar o antigo)
    campos = {f.name for f in dataclasses.fields(ElementVisual)}
    assert campos == {"name", "symbol", "color", "description",
                      "default_k", "default_c", "default_m"}, campos

    # parafuso, membro, contato e contorno — um representante de cada familia,
    # pelos nomes REAIS das chaves
    required_types = ["HEAD", "SHANK", "THREAD", "NUT", "WASHER",
                      "FLANGE", "GASKET", "GENERIC_CONTACT", "GROUND"]
    for elem_type in required_types:
        assert elem_type in ELEMENT_VISUALS, f"Missing element type: {elem_type}"

    # forma de TODA entrada, nao so das exigidas: a tabela alimenta a paleta do
    # MSD Builder, e uma entrada sem simbolo ou sem cor quebra a UI em silencio
    for elem_type, visual in ELEMENT_VISUALS.items():
        assert isinstance(visual, ElementVisual), elem_type
        assert visual.name, f"No name for {elem_type}"
        assert visual.symbol, f"No symbol for {elem_type}"
        assert visual.color.startswith("#"), f"Invalid color for {elem_type}"
        assert visual.description, f"No description for {elem_type}"
        assert visual.default_k > 0, f"Invalid default_k for {elem_type}"
        assert visual.default_m > 0, f"Invalid default_m for {elem_type}"
        assert visual.default_c >= 0, f"Invalid default_c for {elem_type}"

    # GROUND e' o elemento sem o qual a validacao do modelo falha ("No ground
    # element defined"), entao ele nao pode desaparecer da tabela
    assert "GROUND" in ELEMENT_VISUALS
    assert len(ELEMENT_VISUALS) >= len(required_types)


def test_widgets(qapp):
    """Test Qt widget instantiation."""
    print("Testing Widget instantiation...")
    
    from bolt_analysis_studio.gui.main_window import (
        ProjectTab, ModelBuilderTab, SolverTab,
        ResultsTab, SimilitudeTab, ReportsTab
    )
    
    # Test each tab widget
    tabs = {
        'ProjectTab': ProjectTab,
        'ModelBuilderTab': ModelBuilderTab,
        'SolverTab': SolverTab,
        'ResultsTab': ResultsTab,
        'SimilitudeTab': SimilitudeTab,
        'ReportsTab': ReportsTab
    }
    
    for name, TabClass in tabs.items():
        try:
            tab = TabClass()
            assert tab is not None
            print(f"  ✓ {name} created")
        except Exception as e:
            print(f"  ✗ {name} failed: {e}")
            raise
    
    # Test ProjectTab methods
    project_tab = ProjectTab()
    info = project_tab.get_project_info()
    assert info is not None
    assert info.name is not None
    print("  ✓ ProjectTab.get_project_info() works")
    
    # Test ModelBuilderTab summary update
    model_tab = ModelBuilderTab()
    stats = {
        'n_elements': 5,
        'n_dof': 4,
        'total_mass': 0.156,
        'k_eq': 2.3e8,
        'c_eq': 150.0,
        'f_n': 612.0,
        'phi': 0.234
    }
    model_tab.update_summary(stats)
    print("  ✓ ModelBuilderTab.update_summary() works")
    
    print("  ✓ Widget tests passed\n")


def test_msd_builder(qapp):
    """Test MSD Builder components."""
    print("Testing MSD Builder components...")
    
    from bolt_analysis_studio.gui.msd_builder import (
        SchematicView, ElementPalette, PropertyInspector,
        ElementGraphicsItem, ELEMENT_VISUALS
    )
    
    # Test SchematicView
    schematic = SchematicView()
    assert schematic is not None
    assert len(schematic.elements) == 0
    
    # Add elements. A assinatura e' add_element(tipo, ROW, COL) — indices de
    # GRADE, nao pixels. O teste antigo passava (0, 0), (0, 80), (0, 160) como se
    # fossem coordenadas x/y, o que jogava os elementos nas colunas 0, 80 e 160:
    # nao-adjacentes, logo ZERO conexoes, e o assert de auto-conexao falhava
    # dando a impressao de que a auto-conexao havia sido removida. Ela nao foi —
    # medido em 2026-07-28: com linhas adjacentes as 2 conexoes aparecem
    # IMEDIATAMENTE no add_element, sem precisar de _rebuild_connections().
    elem1 = schematic.add_element("HEAD", 0, 0)
    assert elem1.element_id == 1
    assert elem1.element_type == "HEAD"

    elem2 = schematic.add_element("SHANK", 1, 0)
    assert elem2.element_id == 2

    elem3 = schematic.add_element("THREAD", 2, 0)
    assert elem3.element_id == 3

    assert len(schematic.elements) == 3

    # auto-conexao da cadeia: 3 elementos adjacentes -> 2 ligacoes
    assert len(schematic.connections) == 2

    # `elements` e' um DICT indexado por element_id (1..N), nao uma lista, e nao
    # existe `SchematicView.get_model_data()` — o teste antigo chamava esse metodo
    # e ele nao existe em lugar nenhum do pacote. Quem exporta modelo e' a JANELA
    # (`MSDBuilderWindow.export_to_msd_model()`), coberto em
    # test_msd_builder_window.
    assert isinstance(schematic.elements, dict)
    assert sorted(schematic.elements) == [1, 2, 3]
    assert schematic.elements[1].element_type == "HEAD"
    assert schematic.elements[2].element_type == "SHANK"
    assert schematic.elements[3].element_type == "THREAD"
    
    # Test ElementPalette
    palette = ElementPalette()
    assert palette is not None
    print("  ✓ ElementPalette created")
    
    # Test PropertyInspector
    inspector = PropertyInspector()
    assert inspector is not None
    inspector.set_element(None)
    inspector.set_element(elem1)
    print("  ✓ PropertyInspector works")
    
    # Test element removal
    schematic.remove_element(2)
    assert len(schematic.elements) == 2
    print("  ✓ Element removal works")
    
    # Test clear all
    schematic.clear_all()
    assert len(schematic.elements) == 0
    print("  ✓ Clear all works")
    
    print("  ✓ MSD Builder tests passed\n")


def test_main_window(qapp):
    """Test main window."""
    print("Testing Main Window...")
    
    from bolt_analysis_studio.gui.main_window import BoltAnalysisStudio
    
    # Create main window
    window = BoltAnalysisStudio()
    assert window is not None
    
    # Check tab widget. SETE abas, nao seis: a 7a ("Documentation") entrou depois
    # de o teste ser escrito, e o CLAUDE.md ja descreve a aplicacao como "7-tab".
    # Prendemos os ROTULOS, nao so a contagem — assim uma aba renomeada ou
    # reordenada aparece com nome no diff, em vez de virar "assert 7 == 7".
    assert window.tab_widget is not None
    rotulos = [window.tab_widget.tabText(i)
               for i in range(window.tab_widget.count())]
    assert rotulos == ["Project", "Model Builder", "Solver", "Results",
                       "Similitude", "Reports", "Documentation"], rotulos
    
    # Check individual tabs exist
    assert window.project_tab is not None
    assert window.model_builder_tab is not None
    assert window.solver_tab is not None
    assert window.results_tab is not None
    assert window.similitude_tab is not None
    assert window.reports_tab is not None
    print("  ✓ All tab references valid")
    
    # Check status bar
    assert window.model_status is not None
    assert window.analysis_status is not None
    print("  ✓ Status bar configured")
    
    print("  ✓ Main Window tests passed\n")


def test_msd_builder_window(qapp):
    """Test MSD Builder Window."""
    print("Testing MSD Builder Window...")
    
    from bolt_analysis_studio.gui.msd_builder import MSDBuilderWindow
    
    # Create window
    window = MSDBuilderWindow()
    assert window is not None
    
    # Check components
    assert window.palette is not None
    assert window.schematic is not None
    assert window.inspector is not None
    print("  ✓ MSD Builder window created")
    
    # Presets. `_add_preset` LIMPA o esquema antes de montar, entao as chamadas
    # em sequencia nao acumulam. As contagens sao 6/10/8, nao 5/9/7 do teste
    # antigo — cada preset ganhou UM elemento (o GROUND, sem o qual a validacao
    # falha com "No ground element defined"). Medido em 2026-07-28.
    for preset, n_esperado in (("single_bolt", 6),
                               ("flanged_joint", 10),
                               ("junker_test", 8)):
        window._add_preset(preset)
        assert len(window.schematic.elements) == n_esperado, (
            f"{preset}: {len(window.schematic.elements)} != {n_esperado}")
        # todo preset tem de sair conectado em cadeia
        assert len(window.schematic.connections) == n_esperado - 1, preset

    # Export. `window.get_model_data()` NAO existe (o teste antigo o chamava); a
    # API real e' `export_to_msd_model()`, que devolve um MSDModel de verdade —
    # e e' o mesmo caminho que o `model_changed` do Builder usa em producao.
    from bolt_analysis_studio.core.models.model import MSDModel
    modelo = window.export_to_msd_model()
    assert isinstance(modelo, MSDModel)
    assert len(modelo.elements) == 8            # junker_test, o ultimo montado
    assert modelo.n_dof > 0
    
    print("  ✓ MSD Builder Window tests passed\n")


def test_integration(qapp):
    """Test integration between components."""
    print("Testing Integration...")
    
    from bolt_analysis_studio.gui.main_window import BoltAnalysisStudio
    from bolt_analysis_studio.gui.msd_builder import MSDBuilderWindow
    
    # Create both windows
    main = BoltAnalysisStudio()
    builder = MSDBuilderWindow()
    
    # Add preset to builder
    builder._add_preset("flanged_joint")

    # O caminho REAL de dados Builder -> janela principal e'
    # `export_to_msd_model()` (o teste antigo chamava `get_model_data()`, que nao
    # existe em MSDBuilderWindow). O modelo exportado e' o mesmo objeto que o
    # `model_changed` propaga em producao.
    modelo = builder.export_to_msd_model()
    assert len(modelo.elements) == 10
    assert modelo.n_dof > 0

    # k/c/m vivem em `elemento.msd` (MSDParameters), nao no elemento — o teste
    # antigo somava `e.get('m', 0.01)` sobre dicts e, com o default 0.01, teria
    # dado um numero plausivel mesmo se a massa nao existisse. Aqui a soma vem do
    # campo real e o assert abaixo prova que ela nao e' zero.
    stats = {
        'n_elements': len(modelo.elements),
        'n_dof': modelo.n_dof,
        'total_mass': sum((getattr(e.msd, 'm', 0.0) or 0.0)
                          for e in modelo.elements),
        'k_eq': 2.3e8,
        'c_eq': 150.0,
        'f_n': 612.0,
        'phi': 0.234
    }
    assert stats['total_mass'] > 0
    assert stats['n_dof'] == len(modelo.elements) - 1   # a cadeia aterrada

    main.model_builder_tab.update_summary(stats)


# O `main()` que existia aqui foi REMOVIDO em 2026-07-28, e ele era a causa raiz
# de o arquivo inteiro estar excluido da suite desde o fork: era um runner
# artesanal que criava a propria `QApplication(sys.argv)` e passava como
# argumento `app` para 5 destes testes. Sob pytest, ninguem passa esse argumento
# => `fixture 'app' not found`, 5 ERRORS. O runner e' o pytest, e quem fornece o
# QApplication e' `tests/conftest.py` (fixture `qapp`, escopo de sessao) junto de
# duas coisas que o runner artesanal NAO fazia e sao necessarias:
# `QT_QPA_PLATFORM=offscreen` e o reset autouse do singleton `AppState`. Sem esse
# reset, janelas de GUI se acumulam entre testes ligadas ao mesmo sinal
# `model_changed` e as janelas velhas quebram depois em `_fit_view` — ou seja,
# rodar este arquivo "na mao" era ativamente pior que rodar pelo pytest.
