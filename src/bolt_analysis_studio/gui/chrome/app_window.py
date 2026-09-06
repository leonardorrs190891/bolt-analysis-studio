"""ChromeWindow — shell CAE do BAS (spec abaqus §3). Opt-in via run_app.py --v2.

Reutiliza Theme (design-system) e AppState (barramento) as-is; a V1 de 7 abas
permanece como fallback. Os viewports mostram placeholders nomeados — os modulos
reais vem em planos subsequentes.
"""
from __future__ import annotations

import json
from pathlib import Path

from PyQt6.QtCore import Qt, QSize
from PyQt6.QtWidgets import (QDockWidget, QLabel, QMainWindow, QStackedWidget,
                             QStatusBar, QToolBar)

from ..theme import Theme
from ...core.app_state import get_app_state
from .widgets.module_bar import ModuleBar, MODULES
from .widgets.context_bar import ContextBar
from .widgets.prompt_area import PromptArea
from .widgets.model_tree import ModelTree
from .widgets.property_inspector import ChromeInspector
from .widgets.multi_viewport import MultiViewport
from .widgets.message_area import MessageArea
from .widgets.dock_title_bar import DockTitleBar
from .widgets.context_block import ContextBlock
from .widgets.viewport_toolbar import ViewportToolbar
from .controllers.model_controller import ModelController
from .controllers.validation_controller import ValidationController
from .controllers.analysis_controller import AnalysisController
from .controllers.results_controller import ResultsController
from .controllers.report_controller import ReportController
from .controllers.v1_host import V1Host

# Prompt contextual por modulo (spec §3.5).
# (pt, en): resolvido por Lang.tr na hora de mostrar, para o toggle de idioma
# valer tambem no prompt do modulo corrente.
_PROMPTS = {
    "Model": ("Adicione ou selecione elementos no viewport.",
              "Add or select elements in the viewport."),
    "Contacts": ("Defina contatos e modelos de atrito/desgaste.",
                 "Define contacts and friction/wear models."),
    "Loads": ("Configure o carregamento global e por-elemento.",
              "Set the global and per-element loading."),
    "Analysis": ("Defina os steps e rode a análise.",
                 "Define the steps and run the analysis."),
    "Results": ("Inspecione os plots e overlays de validação.",
                "Inspect the plots and the validation overlays."),
    "Report": ("Monte o relatório e escolha o formato.",
               "Assemble the report and choose the format."),
}
# Layout default do viewport por modulo (spec abaqus §5).
_DEFAULT_LAYOUT = {"Model": "1", "Contacts": "1", "Loads": "1",
                   "Analysis": "1", "Results": "2x2", "Report": "1"}


class ChromeWindow(QMainWindow):
    # Familia schematic: modulos que mostram o SchematicView estavel no centro,
    # diferindo so na aba do inspector rico (spec §6: Model/Contacts/Loads).
    _SCHEMATIC_MODULES = {"Model": "element", "Contacts": "contact", "Loads": "loading"}
    # Bump quando o layout default muda → ignora estado salvo antigo (usa o novo).
    _LAYOUT_VERSION = "7"

    def __init__(self, app_state=None, parent=None):
        super().__init__(parent)
        self.app_state = app_state or get_app_state()
        self._current_module = None
        # O idioma escolhido era gravado no preferences.json e NUNCA lido de
        # volta: cada abertura voltava ao portugues. Lido aqui, antes de montar
        # qualquer texto (defeito encontrado no debug de 2026-09-04).
        from ..i18n import Lang
        Lang.load_preference()
        self.setWindowTitle("Bolt Analysis Studio")
        self.resize(1280, 800)
        self._build_chrome()
        self._wire_signals()
        try:
            self.setStyleSheet(Theme.get_stylesheet())
        except Exception:
            pass
        self._restore_layout()          # antes de switch_module (que gere o palette)
        if getattr(self.app_state, "model", None) is not None:
            self.tree.populate(self.app_state.model)
            self.model_controller.sync_from_app_state()
        self.switch_module("Model")

        # Reskin de ícones na troca de tema: limpa o cache (cor muda) e
        # reconstrói os ícones já aplicados no ModuleBar e na Tree.
        #
        # SEM `from ..theme import Theme` aqui: um import local torna `Theme`
        # variavel LOCAL da funcao inteira, e o `Theme.get_stylesheet()` la'
        # em cima passava a ler uma local ainda nao atribuida —
        # UnboundLocalError engolido pelo `except Exception: pass`, e a folha
        # de estilo inicial NUNCA era aplicada na construcao. O modulo ja'
        # importa Theme no topo. Achado pelo Pyright no debug de 2026-09-05.
        from ..icons import clear_icon_cache

        def _reskin_icons():
            clear_icon_cache()
            self.module_bar.rebuild_icons()
            self.tree.rebuild_icons()

        self._reskin_icons = _reskin_icons        # segura a referência
        Theme.register_callback(_reskin_icons)

        # Atalhos (Fase 6): Ctrl+1..6 trocam módulo, Ctrl+R roda, Shift+F fit view.
        from PyQt6.QtGui import QShortcut, QKeySequence
        for i, m in enumerate(MODULES, start=1):
            QShortcut(QKeySequence(f"Ctrl+{i}"), self,
                      activated=lambda name=m: self.switch_module(name))
        QShortcut(QKeySequence("Ctrl+R"), self, activated=self._run_shortcut)
        # F1: o rotulo do menu Ajuda promete o atalho, entao ele existe.
        QShortcut(QKeySequence("F1"), self,
                  activated=self._open_documentation)
        QShortcut(QKeySequence("Shift+F"), self,
                  activated=self.viewport_toolbar._fit)

        self.refresh_empty_state()

        # Pré-aquece a janela V1 oculta em background (2.5s) — o 1º Analysis/
        # Results/Report abre instantâneo em vez de travar ~2s construindo.
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(2500, self._prewarm_v1)

    # --- construcao ---
    def _build_chrome(self):
        self.module_bar = ModuleBar()
        self.module_bar.setObjectName("moduleBar")
        self.module_bar.setIconSize(QSize(16, 16))
        self.addToolBar(self.module_bar)
        self.addToolBarBreak()
        self.context_bar = ContextBar()
        self.context_bar.setObjectName("contextBar")
        self.context_bar.setIconSize(QSize(16, 16))
        self.addToolBar(self.context_bar)

        # Bloco de contexto ("Module · Model · Step") — vai para a STATUS BAR (libera
        # uma faixa no topo para a árvore/viewport crescerem).
        self.context_block = ContextBlock()

        self.tree = ModelTree()
        tree_dock = QDockWidget("Model Tree", self)
        tree_dock.setObjectName("treeDock")
        tree_dock.setWidget(self.tree)
        tree_dock.setFeatures(QDockWidget.DockWidgetFeature.DockWidgetMovable
                              | QDockWidget.DockWidgetFeature.DockWidgetClosable)
        tree_dock.setTitleBarWidget(DockTitleBar(tree_dock, "Model Tree"))
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, tree_dock)
        self._tree_dock = tree_dock

        self.inspector = ChromeInspector()
        insp_dock = QDockWidget("Properties", self)
        insp_dock.setObjectName("inspectorDock")
        insp_dock.setWidget(self.inspector)
        insp_dock.setFeatures(QDockWidget.DockWidgetFeature.DockWidgetMovable
                              | QDockWidget.DockWidgetFeature.DockWidgetClosable)
        insp_dock.setTitleBarWidget(DockTitleBar(insp_dock, "Properties"))
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, insp_dock)
        self._inspector_dock = insp_dock

        # Central: stack com pagina 0 = MultiViewport (placeholders/outros modulos)
        # e pagina 1 = schematic do Modulo Model (pagina ESTAVEL — nao deletada na
        # troca de modulo, ao contrario dos slots do MultiViewport).
        self.viewport = MultiViewport()
        self._center = QStackedWidget()
        self._center.addWidget(self.viewport)
        self.setCentralWidget(self._center)
        self.model_controller = ModelController(self.app_state)
        self._center.addWidget(self.model_controller.viewport_widget())

        # Toolbar de viewport (Abaqus §5): fit/zoom/screenshot. SEM break => senta
        # na mesma faixa do bloco de contexto (compacta a pilha de toolbars).
        self.viewport_toolbar = ViewportToolbar(
            lambda: self.model_controller.viewport_widget())
        self.viewport_toolbar.setObjectName("viewportBar")
        self.viewport_toolbar.setIconSize(QSize(16, 16))
        self.addToolBar(self.viewport_toolbar)

        # Modulo Validation (Plano B): pagina do browser no stack (sub-mode do
        # Results ate o Plano 5 trazer os plots de Run).
        self.validation_controller = ValidationController(self.app_state)
        self._center.addWidget(self.validation_controller.viewport_widget())

        # Host V1 compartilhado (lazy): Analysis/Results/Report re-hospedam as abas
        # de uma BoltAnalysisStudio oculta — construída só no 1º uso desses módulos.
        self._v1_host = V1Host(self.app_state)
        self.analysis_controller = AnalysisController(self.app_state, host=self._v1_host)
        self.analysis_controller.log_message.connect(
            lambda t: self.messages.append(t, "job"))
        self.analysis_controller.job_state.connect(self._on_job_state)
        self.results_controller = ResultsController(self.app_state, host=self._v1_host)
        self._results_tabs = None
        self.report_controller = ReportController(self.app_state, host=self._v1_host)

        # Dock da paleta de elementos (so visivel no Modulo Model).
        # Elements (palette): à DIREITA, junto de Properties (não mais sob a árvore),
        # colapsável + fechável como os demais painéis.
        self._palette_dock = QDockWidget("Elements", self)
        self._palette_dock.setObjectName("paletteDock")
        self._palette_dock.setWidget(self.model_controller.palette)
        self._palette_dock.setFeatures(QDockWidget.DockWidgetFeature.DockWidgetMovable
                                       | QDockWidget.DockWidgetFeature.DockWidgetClosable)
        self._palette_dock.setTitleBarWidget(DockTitleBar(self._palette_dock, "Elements"))
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self._palette_dock)
        # Lado a lado com Properties (não empilhado): divide o espaço na horizontal.
        self.splitDockWidget(self._inspector_dock, self._palette_dock,
                             Qt.Orientation.Horizontal)
        self._palette_dock.hide()

        # Prompt (instruções): NÃO fica numa faixa separada — o texto vai para a
        # área de mensagens. self.prompt continua existindo p/ set_prompt/coords.
        self.prompt = PromptArea()

        # Message area (Abaqus §3): Messages / Job Log — na parte INFERIOR, compacta,
        # colapsável pelo próprio cabeçalho (▼/▶) e pelo menu Exibir > Painéis.
        self.messages = MessageArea()
        msg_dock = QDockWidget("Messages", self)
        msg_dock.setObjectName("messageDock")
        msg_dock.setWidget(self.messages)
        msg_dock.setFeatures(QDockWidget.DockWidgetFeature.DockWidgetMovable)
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, msg_dock)
        self._msg_dock = msg_dock
        # Instruções ("Modelo criado…") fluem para a área de mensagens.
        self.prompt.prompted.connect(lambda t: self.messages.append(t, "messages"))

        # Readout de cursor (#8): coords da cena no prompt ao mover sobre o schematic.
        self._coords_view = self.model_controller.viewport_widget()
        self._coords_view.viewport().setMouseTracking(True)
        self._coords_view.viewport().installEventFilter(self)

        self.setStatusBar(QStatusBar())
        self._coords_label = QLabel("")
        self.statusBar().addPermanentWidget(self._coords_label)
        self.statusBar().addPermanentWidget(self.context_block)
        self.statusBar().showMessage("Projeto: — · Modulo: — · Job: idle")
        self._build_menus()

        # Proporções iniciais: árvore/viewport dominam; Messages compacto no topo.
        self.resizeDocks([msg_dock], [120], Qt.Orientation.Vertical)
        self.resizeDocks([tree_dock, insp_dock], [270, 300],
                         Qt.Orientation.Horizontal)

    def _build_menus(self):
        """Menus em duas linguas, retraduzidos ao vivo por Ajuda > Idioma.

        Cada titulo e cada acao entram no `TrGroup` da janela com (pt, en); o
        toggle chama os setters de novo. Os nomes de modulo ficam em ingles nas
        duas linguas de proposito — sao os substantivos do Abaqus e e' assim
        que o guia e a documentacao os citam.
        """
        from PyQt6.QtGui import QAction
        from ..i18n import TrGroup
        from ..theme import PALETTE_NAMES

        self._tr = TrGroup()
        T = self._tr.add
        mb = self.menuBar()

        file_menu = mb.addMenu("")
        T(file_menu.setTitle, "Arquivo", "File")
        act = file_menu.addAction("")
        T(act.setText, "Nova análise…", "New analysis…")
        act.setShortcut("Ctrl+Shift+N")
        act.triggered.connect(self._open_wizard)
        # Abrir ao lado de Nova analise: ate' 2026-09-03 o chrome nao tinha
        # como abrir um .msd salvo nem gravar o editado. Abrir sem salvar seria
        # armadilha, entao os dois entraram juntos.
        act = file_menu.addAction("")
        T(act.setText, "Abrir projeto…", "Open project…")
        act.setShortcut("Ctrl+O")
        act.triggered.connect(self._abrir_projeto)
        # Abrir por caminho serve para projeto proprio; para os casos do artigo
        # obrigava a saber em qual das 28 pastas de fonte esta' a curva e o nome
        # exato do arquivo. Este item lista as 205 do censo por nome.
        act = file_menu.addAction("")
        T(act.setText, "Importar caso da validação…", "Import validation case…")
        act.setShortcut("Ctrl+I")
        act.triggered.connect(self._importar_caso_validacao)
        file_menu.addSeparator()
        act = file_menu.addAction("")
        T(act.setText, "Salvar", "Save")
        act.setShortcut("Ctrl+S")
        act.triggered.connect(self._salvar_projeto)
        act = file_menu.addAction("")
        T(act.setText, "Salvar como…", "Save as…")
        act.setShortcut("Ctrl+Shift+S")
        act.triggered.connect(self._salvar_projeto_como)
        file_menu.addSeparator()
        act = file_menu.addAction("", self.close)
        T(act.setText, "Sair", "Quit")

        edit_menu = mb.addMenu("")
        T(edit_menu.setTitle, "Editar", "Edit")

        view_menu = mb.addMenu("")
        T(view_menu.setTitle, "Exibir", "View")
        theme_menu = view_menu.addMenu("")
        T(theme_menu.setTitle, "Tema", "Theme")
        for key, label in PALETTE_NAMES.items():
            theme_menu.addAction(
                label, lambda _c=False, k=key: self._apply_theme(k))
        # Paineis colapsaveis: laterais (Model Tree/Properties) ganham botao X
        # no titulo; Mensagens colapsa pelo cabecalho. Exibir > Paineis liga e
        # desliga cada um (toggled -> setVisible explicito, com sync nos dois
        # sentidos — o toggleViewAction nativo nao escondia os docks).
        view_menu.addSeparator()
        panels_menu = view_menu.addMenu("")
        T(panels_menu.setTitle, "Painéis", "Panels")
        for dock, pt, en, closable in (
                (self._tree_dock, "Model Tree", "Model Tree", True),
                (self._inspector_dock, "Properties", "Properties", True),
                (self._palette_dock, "Elements", "Elements", True),
                (self._msg_dock, "Área de mensagens", "Message area", False)):
            if closable:
                dock.setFeatures(dock.features()
                                 | QDockWidget.DockWidgetFeature.DockWidgetClosable)
            pact = QAction("", self)
            T(pact.setText, pt, en)
            pact.setCheckable(True)
            pact.setChecked(True)
            pact.toggled.connect(dock.setVisible)
            dock.visibilityChanged.connect(pact.setChecked)
            panels_menu.addAction(pact)

        # Analisar: o ajuste de parametros existia, com trava e limites por
        # parametro, e so' era alcancavel pela janela V1 — que nao e' mais a
        # interface padrao. Escrito e inalcancavel e' o mesmo que ausente.
        analise_menu = mb.addMenu("")
        T(analise_menu.setTitle, "Analisar", "Analyse")
        act = analise_menu.addAction("")
        T(act.setText, "Calibrar parâmetros do modelo…",
          "Calibrate model parameters…")
        act.setShortcut("Ctrl+K")
        T(act.setStatusTip,
          "Ajusta os parâmetros marcados contra uma curva experimental; o que "
          "não for marcado fica no valor que você mediu",
          "Fits the ticked parameters against an experimental curve; whatever "
          "is not ticked stays at the value you measured")
        act.triggered.connect(self._calibrar_parametros)

        # Nomes de modulo em ingles nas duas linguas (proper nouns do Abaqus).
        mod_menu = mb.addMenu("")
        T(mod_menu.setTitle, "Módulo", "Module")
        for m in MODULES:
            mod_menu.addAction(m, lambda _c=False, name=m: self.switch_module(name))

        help_menu = mb.addMenu("")
        T(help_menu.setTitle, "Ajuda", "Help")
        # A documentacao vem PRIMEIRO: ate' 2026-09-02 as 25 secoes so'
        # existiam na janela V1, e o chrome nao tinha porta para elas.
        # O guia narrado vem PRIMEIRO: e' por onde quem nunca abriu o
        # programa deve comecar, e um item de menu que ninguem acha e' um item
        # que nao existe. F1 abre a documentacao; Shift+F1, o guia.
        act = help_menu.addAction("", self._open_guia)
        T(act.setText, "Guia de uso narrado (Shift+F1)",
          "Narrated user guide (Shift+F1)")
        act.setShortcut("Shift+F1")
        act = help_menu.addAction("", self._open_documentation)
        T(act.setText, "Documentação (F1)", "Documentation (F1)")
        act = help_menu.addAction("", self._toggle_idioma)
        T(act.setText, "Idioma: Português / English",
          "Language: Português / English")
        help_menu.addSeparator()
        act = help_menu.addAction("", self._open_validation_docs)
        T(act.setText, "Reports de validação (207 casos)",
          "Validation reports (207 cases)")
        act = help_menu.addAction("", self._copy_intake_prompt)
        T(act.setText, "Prompt de intake (IA) — copiar",
          "Intake prompt (AI) — copy")

    # --- sinais ---
    def _wire_signals(self):
        self.module_bar.module_changed.connect(self.switch_module)
        self.context_bar.action_triggered.connect(self._on_context_action)
        self.tree.node_selected.connect(self._on_tree_node)
        st = self.app_state
        if hasattr(st, "model_changed"):
            st.model_changed.connect(self._on_model_changed)
        # "Abrir no Model/Run" do modulo Validation: carregou o caso -> Model
        self.validation_controller.case_opened_in_model.connect(
            lambda _cid: self.switch_module("Model"))
        # Run/Stop do ModuleBar -> AnalysisController (Fase 4).
        self.module_bar.run_requested.connect(self.analysis_controller.run)
        self.module_bar.stop_requested.connect(self.analysis_controller.stop)

    # --- maquina de modulos ---
    @property
    def current_module(self) -> str:
        return self._current_module

    def switch_module(self, name: str) -> None:
        if name not in MODULES:
            return
        self._current_module = name
        self.context_bar.set_module(name)
        self.tree.highlight_module(name)
        from ..i18n import Lang
        self.prompt.set_prompt(Lang.tr(*_PROMPTS.get(name, ("", ""))))
        if name in self._SCHEMATIC_MODULES:
            # Familia Model/Contacts/Loads: schematic estavel no centro.
            self._center.setCurrentWidget(self.model_controller.viewport_widget())
            self._palette_dock.setVisible(name == "Model")
            if name == "Loads":
                # #1: Loads no inspector chrome-nativo (CollapsibleGroup);
                # Model/Contacts seguem no inspector rico (feature-complete).
                self._inspector_dock.setWidget(self.inspector)
                self._populate_loads_inspector()
            else:
                self._inspector_dock.setWidget(self.model_controller.inspector)
                self.model_controller.show_inspector_tab(self._SCHEMATIC_MODULES[name])
            sv = self.model_controller.viewport_widget()
            if hasattr(sv, "set_stamp_enabled"):
                sv.set_stamp_enabled(True)
                mdl = getattr(self.app_state, "model", None)
                sv.set_title_block(getattr(mdl, "name", "") or "—", name,
                                   self.module_bar._step_combo.currentText(), "")
            # Enquadra o modelo no viewport (a menos que o usuário já tenha
            # dado zoom manual) — evita o schematic minúsculo no canto.
            if getattr(sv, "_auto_fit", True) and hasattr(sv, "fit_contents"):
                from PyQt6.QtCore import QTimer
                QTimer.singleShot(0, sv.fit_contents)
        elif name == "Results":
            # Sub-modos: Run (ResultsTab da janela V1) + Validation (browser dos casos).
            if self._results_tabs is None:
                from PyQt6.QtWidgets import QTabWidget
                self._results_tabs = QTabWidget()
                self._results_tabs.addTab(
                    self.results_controller.viewport_widget(), "Run")
                self._results_tabs.addTab(
                    self.validation_controller.viewport_widget(), "Validation")
                self._center.addWidget(self._results_tabs)
            self.results_controller.refresh()
            self._center.setCurrentWidget(self._results_tabs)
            self._inspector_dock.setWidget(self.inspector)
            self._palette_dock.hide()
            self._results_empty_hint()
        elif name == "Analysis":
            # Módulo Analysis: SolverTab da janela V1 oculta (lazy-build).
            w = self.analysis_controller.viewport_widget()
            if self._center.indexOf(w) < 0:
                self._center.addWidget(w)
            self._center.setCurrentWidget(w)
            self._inspector_dock.setWidget(self.inspector)
            self._populate_analysis_inspector()
            self._palette_dock.hide()
        elif name == "Report":
            # Módulo Report: ReportsTab da janela V1 oculta (lazy-build).
            w = self.report_controller.viewport_widget()
            if self._center.indexOf(w) < 0:
                self._center.addWidget(w)
            self._center.setCurrentWidget(w)
            self._inspector_dock.setWidget(self.inspector)
            self._palette_dock.hide()
            self._results_empty_hint()
        else:
            # Demais modulos: placeholders no MultiViewport, ChromeInspector.
            self._center.setCurrentWidget(self.viewport)
            self.viewport.set_layout(_DEFAULT_LAYOUT.get(name, "1"))
            for i in range(self.viewport.slot_count()):
                self.viewport.set_widget(i, QLabel(f"[ {name} · viewport {i + 1} ]"))
            self._inspector_dock.setWidget(self.inspector)
            self._palette_dock.hide()
        # Run/Stop só habilitados no módulo Analysis.
        self.module_bar.set_run_enabled(
            name == "Analysis", "Entre no módulo Analysis para rodar.")
        # O inspector trocou de widget → reaplica o colapso se estiver colapsado.
        self._reapply_collapse(self._inspector_dock)
        model_name = getattr(getattr(self.app_state, "model", None), "name", "") or "—"
        step = self.module_bar._step_combo.currentText()
        self.context_block.set_context(name, model_name, step)
        self.statusBar().showMessage(Lang.tr(
            f"Projeto: — · Módulo: {name} · Job: idle",
            f"Project: — · Module: {name} · Job: idle"))
        self.module_bar.mark_module(name)

    # --- handlers ---
    _ACTION_HELP = {
        "+ Element": ("Selecione um ponto no viewport para inserir o elemento.",
                      "Select a point in the viewport to insert the element."),
        "+ Thread": ("Selecione a porca e depois o parafuso para criar o "
                     "ThreadContact.",
                     "Select the nut and then the bolt to create the "
                     "ThreadContact."),
        "+ Bearing": ("Selecione as duas faces em contato para criar o bearing.",
                      "Select the two faces in contact to create the bearing."),
        "+ Global Load": ("Defina F0, amplitude e frequência no inspector à "
                          "direita.",
                          "Set F0, amplitude and frequency in the inspector on "
                          "the right."),
        "+ Coupled-Loosening": ("Configure dt e n_cycles e rode em Analysis.",
                                "Set dt and n_cycles and run in Analysis."),
    }

    def _on_context_action(self, label: str):
        from ..i18n import Lang
        par = self._ACTION_HELP.get(label)
        self.prompt.set_prompt(Lang.tr(*par) if par else Lang.tr(
            f"{label}: configure os parâmetros no inspector.",
            f"{label}: set the parameters in the inspector."))

    def _model_context(self) -> dict:
        """Contexto do modelo p/ os smart defaults (robusto a modelo ausente)."""
        m = getattr(self.app_state, "model", None)
        gl = getattr(m, "global_loading", None)
        fb = getattr(m, "friction_bolt", None)
        delta = getattr(gl, "delta_amplitude", None) if gl else None
        return {
            "delta_amplitude": delta,
            "damping": bool(delta),        # crank-driven → HHT-α
            "lubricated": bool(getattr(fb, "lubricated", False)) if fb else False,
        }

    def _populate_loads_inspector(self) -> None:
        """Inspector chrome-nativo do Loads: campos de carregamento em
        CollapsibleGroup (Basic/Advanced), editáveis com write-back in-place."""
        from PyQt6.QtWidgets import QDoubleSpinBox, QSpinBox
        gl = getattr(getattr(self.app_state, "model", None), "global_loading", None)
        self._loads_widgets = {}
        rows = []
        if gl is not None:
            specs = [
                ("F₀", "F_preload", getattr(gl, "F_preload", 0.0), 0.0, 1e7, 1000.0, " N", False),
                ("Amplitude δ", "delta_amplitude", getattr(gl, "delta_amplitude", 0.0), 0.0, 100.0, 0.05, " mm", False),
                ("Frequência", "frequency", getattr(gl, "frequency", 0.0), 0.0, 1e4, 0.5, " Hz", False),
            ]
            for label, key, val, lo, hi, step, suffix, adv in specs:
                sp = QDoubleSpinBox()
                sp.setObjectName("numeric")
                sp.setDecimals(3)
                sp.setRange(lo, hi)
                sp.setSingleStep(step)
                sp.setSuffix(suffix)
                sp.blockSignals(True)
                sp.setValue(float(val or 0.0))
                sp.blockSignals(False)
                sp.valueChanged.connect(lambda v, k=key: self._set_loading_field(k, v))
                self._loads_widgets[key] = sp
                rows.append({"label": label, "widget": sp, "advanced": adv})
            cyc = QSpinBox()
            cyc.setObjectName("numeric")
            cyc.setRange(0, 100_000_000)
            cyc.blockSignals(True)
            cyc.setValue(int(getattr(gl, "cycles", 0) or getattr(gl, "n_cycles", 0) or 0))
            cyc.blockSignals(False)
            cyc.valueChanged.connect(lambda v: self._set_loading_field("cycles", v))
            self._loads_widgets["cycles"] = cyc
            rows.append({"label": "Ciclos", "widget": cyc, "advanced": True})
        self.inspector.show_groups([{"title": "Carregamento", "rows": rows}])

    def _set_loading_field(self, key: str, value) -> None:
        """Escreve o campo de carregamento no modelo (in-place, sem re-emitir)."""
        gl = getattr(getattr(self.app_state, "model", None), "global_loading", None)
        if gl is not None:
            try:
                setattr(gl, key, value)
            except Exception:          # pragma: no cover - defensivo
                pass

    def _populate_analysis_inspector(self) -> None:
        """Grupo 'Auto-defaults' no inspector do Analysis com AutoComboBoxes que
        resolvem a escolha recomendada a partir do modelo (#2 smart defaults)."""
        from .widgets.auto_combo import AutoComboBox
        from .inference import (infer_integrator, infer_control_mode,
                                infer_friction_model)
        ctx = self._model_context()
        rows = []
        for label, options, fn in (
            ("Integrator", ["Newmark-β", "HHT-α"], infer_integrator),
            ("Control mode", ["Force", "Displacement"], infer_control_mode),
            ("Friction model", ["Coulomb", "Stribeck"], infer_friction_model),
        ):
            combo = AutoComboBox(options, inference_fn=fn)
            combo.set_context(ctx)
            rows.append({"label": label, "widget": combo})
        self.inspector.show_groups([{"title": "Auto-defaults", "rows": rows}])

    def _reapply_collapse(self, dock) -> None:
        tb = dock.titleBarWidget()
        if hasattr(tb, "reapply"):
            tb.reapply()

    def _on_job_state(self, state: str) -> None:
        badge = {"running": ("RUNNING", "info"), "done": ("DONE", "pass"),
                 "error": ("ERROR", "fail"), "idle": ("", "info")}
        text, kind = badge.get(state, ("", "info"))
        self.module_bar.set_badge(text, kind)
        if state == "running":
            # Ao rodar, revela a área de mensagens (mesmo se colapsada) no Job Log.
            self._msg_dock.show()
            self.messages._tabs.setCurrentIndex(1)
        from ..i18n import Lang
        self.statusBar().showMessage(Lang.tr(
            f"Projeto: — · Módulo: {self._current_module} · Job: {state}",
            f"Project: — · Module: {self._current_module} · Job: {state}"))
        if state == "error":
            self.prompt.set_prompt(Lang.tr(
                "A análise falhou — veja o Log do job para o motivo.",
                "The analysis failed — see the Job Log for the reason."))
        elif state == "done":
            self.prompt.set_prompt(Lang.tr(
                "Análise concluída — veja os plots no módulo Results.",
                "Analysis finished — see the plots in the Results module."))

    def _run_shortcut(self) -> None:
        if self.module_bar._run_btn.isEnabled():
            self.module_bar.run_requested.emit()

    def refresh_empty_state(self) -> None:
        """Sem modelo carregado, o prompt orienta a abrir o wizard."""
        from ..i18n import Lang
        if getattr(self.app_state, "model", None) is None:
            self.prompt.set_prompt(Lang.tr(
                "Nenhum modelo carregado — Ctrl+Shift+N abre o wizard de nova "
                "análise, Ctrl+I abre um caso do artigo.",
                "No model loaded — Ctrl+Shift+N opens the new-analysis wizard, "
                "Ctrl+I opens a case from the paper."))

    def _results_empty_hint(self) -> None:
        """Em Results/Report sem resultado, orienta a rodar a análise."""
        from ..i18n import Lang
        if getattr(self.app_state, "results", None) is None:
            self.prompt.set_prompt(Lang.tr(
                "Nenhum resultado ainda — rode uma análise no módulo Analysis "
                "(Ctrl+R).",
                "No results yet — run an analysis in the Analysis module "
                "(Ctrl+R)."))

    def _prewarm_v1(self) -> None:
        """Constrói a janela V1 oculta (lazy) para o 1º Analysis/Results/Report
        não pagar ~2s de construção. Idempotente (V1Host cacheia)."""
        try:
            _ = self._v1_host.window
        except Exception:              # pragma: no cover - defensivo
            pass

    def _save_layout(self) -> None:
        from PyQt6.QtCore import QSettings
        s = QSettings("BAS", "chrome")
        s.setValue("chrome/layoutVersion", self._LAYOUT_VERSION)
        s.setValue("chrome/geometry", self.saveGeometry())
        s.setValue("chrome/windowState", self.saveState())

    def _restore_layout(self) -> None:
        from PyQt6.QtCore import QSettings
        s = QSettings("BAS", "chrome")
        if str(s.value("chrome/layoutVersion", "")) != self._LAYOUT_VERSION:
            return                     # layout mudou de versão → usa o novo default
        geo = s.value("chrome/geometry")
        state = s.value("chrome/windowState")
        try:
            if geo is not None:
                self.restoreGeometry(geo)
            if state is not None:
                self.restoreState(state)
        except (TypeError, ValueError):   # pragma: no cover - estado corrompido
            pass

    def _on_tree_node(self, kind: str, payload):
        if kind == "module" and payload in MODULES:
            self.switch_module(payload)
        elif kind in ("element", "edit") and payload is not None:
            # Clicar/editar um elemento: traz o schematic e seleciona o item.
            if self._current_module not in self._SCHEMATIC_MODULES:
                self.switch_module("Model")
            self._select_element_in_viewport(payload)
        elif kind == "delete" and payload is not None:
            from ..i18n import Lang
            self.prompt.set_prompt(Lang.tr(
                "Exclusão pela árvore ainda não implementada — edite no Model "
                "(duplo-clique no elemento).",
                "Deleting from the tree is not implemented yet — edit in Model "
                "(double-click the element)."))

    def _select_element_in_viewport(self, el) -> None:
        """Seleciona/realça no schematic o elemento clicado na árvore (best-effort)."""
        sv = self.model_controller.viewport_widget()
        eid = getattr(el, "id", None)
        items = getattr(sv, "elements", {}) or {}
        try:
            scene = sv.scene()
            if scene is not None:
                scene.clearSelection()
            if eid in items:
                items[eid].setSelected(True)
        except Exception:              # pragma: no cover - defensivo
            pass

    def _on_model_changed(self, model):
        if model is not None:
            self.tree.populate(model)
        # sincroniza o schematic do Modulo Model (guarda de reentrancia no controller)
        self.model_controller.sync_from_app_state()
        self.refresh_empty_state()

    def _copy_intake_prompt(self):
        # atalho da biblioteca de documentacao: copia o prompt de intake p/
        # o usuario levar a qualquer IA com a curva experimental dele.
        from ..i18n import Lang
        self.validation_controller.copy_prompt()
        self.prompt.set_prompt(Lang.tr(
            "Prompt de intake copiado — cole em qualquer IA junto com sua curva "
            "experimental.",
            "Intake prompt copied — paste it into any AI together with your "
            "experimental curve."))

    def _open_documentation(self):
        """Abre a aba Documentation numa janela propria.

        Ate' 2026-09-02 as 25 secoes so' existiam na janela V1 (`--v1`): o
        chrome V2, que e' o padrao, nao tinha nenhuma porta para elas. Todo o
        help — revisao de literatura, fontes por artigo, tipos de elemento e
        de ligacao, guia do zero, catalogo de dialogos — estava escrito e
        inalcancavel para quem abre o programa normalmente.
        """
        from PyQt6.QtWidgets import QVBoxLayout, QWidget
        try:
            from ...gui.documentation_tab import DocumentationTab
        except Exception as exc:                              # pragma: no cover
            from ..i18n import Lang
            self.prompt.set_prompt(Lang.tr(f"Documentação indisponível: {exc}",
                                           f"Documentation unavailable: {exc}"))
            return
        if getattr(self, "_doc_win", None) is None:
            from ..i18n import Lang
            win = QWidget()
            win.setWindowTitle(Lang.tr("Bolt Analysis Studio — Documentação",
                                       "Bolt Analysis Studio — Documentation"))
            win.resize(1180, 820)
            lay = QVBoxLayout(win)
            lay.setContentsMargins(0, 0, 0, 0)
            lay.addWidget(DocumentationTab())
            self._doc_win = win
        self._doc_win.show()
        self._doc_win.raise_()
        self._doc_win.activateWindow()

    def _toggle_idioma(self):
        """Alterna PT/EN em toda a interface.

        Os textos estaticos (menus, botoes, tooltips, cabecalhos) sao
        retraduzidos pelos `TrGroup` registrados em `Lang`; os dinamicos —
        prompt do modulo, barra de status — sao recompostos aqui reentrando no
        modulo corrente. A documentacao aberta e' reconstruida porque suas
        secoes 23-25 sao bilingues; as 18 escritas a mao seguem em ingles.
        """
        from ...gui.i18n import Lang
        Lang.toggle()
        win = getattr(self, "_doc_win", None)
        if win is not None:
            lay = win.layout()
            antigo = lay.itemAt(0).widget()
            lay.removeWidget(antigo)
            antigo.deleteLater()
            from ...gui.documentation_tab import DocumentationTab
            lay.addWidget(DocumentationTab())
            win.setWindowTitle(Lang.tr("Bolt Analysis Studio — Documentação",
                                       "Bolt Analysis Studio — Documentation"))
        if self._current_module:
            self.switch_module(self._current_module)
        self.prompt.set_prompt(
            "Idioma: " + ("English" if Lang.is_en() else "Português"))

    def _open_guia(self):
        """Abre o guia narrado no navegador, no idioma corrente."""
        from ..documentation_tab import abrir_guia_narrado
        recado = abrir_guia_narrado()
        if recado:
            self.prompt.set_prompt(recado)

    def _open_validation_docs(self):
        # Biblioteca de documentacao: documento mestre dos 128 reports de
        # validacao (gera do store/seed se ausente — rapido, sem simular).
        try:
            import webbrowser
            from ...validation.report import ensure_reports
            webbrowser.open(ensure_reports().as_uri())
        except Exception as exc:  # pragma: no cover - defensivo
            self.prompt.set_prompt(f"Reports indisponíveis: {exc}")

    def _after_wizard(self, model) -> None:
        """Pós-wizard: adota o modelo, popula a tree e navega para Model."""
        self.app_state.model = model
        if model is not None:
            self.tree.populate(model)
            self.model_controller.sync_from_app_state()
        self.switch_module("Model")
        from ..i18n import Lang
        self.prompt.set_prompt(Lang.tr(
            "Modelo criado. Revise em Model → Loads → Analysis e rode em Analysis.",
            "Model created. Review in Model → Loads → Analysis and run in "
            "Analysis."))

    # --- abrir / salvar projeto (2026-09-03) ---------------------------------
    # O chrome V2, que e' o padrao, tinha um menu Arquivo com "Nova Analise" e
    # "Sair": NAO dava para abrir um modelo salvo nem para gravar o que voce
    # editou. Os 207 casos da validacao ja' vinham como .msd desde 02-09 e nao
    # havia porta para eles na interface.
    #
    # Abrir sem salvar seria armadilha — o usuario abre um caso, edita e perde.
    # Por isso os dois vieram juntos.
    _PREFS = Path.home() / ".bolt_analysis_studio" / "preferences.json"

    # export_model() le o ESQUEMATICO — e' o que garante que uma edicao no
    # canvas ainda nao propagada entre no arquivo. MAS o desenho nao conhece os
    # canais de override, a descricao nem o nome: esses vivem no modelo do
    # AppState. Salvar so' com o exportado perdia as 23 constantes adotadas e a
    # citacao da fonte — o arquivo abria com os 11 elementos e o F0 certos, e
    # estava errado (teste de ida e volta, 2026-09-03; mesma perda silenciosa
    # que MSDModel.to_dict tinha, um andar acima). Estrutura vem do
    # esquematico, metadado vem do estado. Calibrar usa a mesma composicao:
    # sem os overrides o ajuste partiria de uma fisica que nao e' a do caso.
    _CARREGA = ("_v2_tuner_overrides", "_v2_geometry_overrides",
                "_two_stage_overrides", "_fixture_overrides",
                "description", "name")

    def _dir_inicial_projeto(self) -> str:
        """Pasta que o dialogo abre.

        Na PRIMEIRA vez, os casos da validacao: e' onde estao os 207 modelos
        dos artigos, e e' o que alguem quer abrir antes de ter projeto proprio.
        Depois disso, a ultima pasta usada — senao quem trabalha nos proprios
        modelos voltaria sempre para os artigos.
        """
        try:
            if self._PREFS.is_file():
                ultimo = json.loads(self._PREFS.read_text(encoding="utf-8")
                                    ).get("ultimo_dir_projeto")
                if ultimo and Path(ultimo).is_dir():
                    return ultimo
        except (OSError, ValueError):
            pass
        try:
            from ...validation.inputs import repo_root
            casos = repo_root() / "Models" / "SAVED_CASES"
            if casos.is_dir():
                return str(casos)
        except Exception:                                    # noqa: BLE001
            pass
        return str(Path.home())

    def _lembra_dir_projeto(self, caminho: str) -> None:
        try:
            self._PREFS.parent.mkdir(parents=True, exist_ok=True)
            prefs = {}
            if self._PREFS.is_file():
                prefs = json.loads(self._PREFS.read_text(encoding="utf-8"))
            prefs["ultimo_dir_projeto"] = str(Path(caminho).parent)
            self._PREFS.write_text(json.dumps(prefs, indent=2),
                                   encoding="utf-8")
        except (OSError, ValueError):        # preferencia e' conveniencia:
            pass                              # falhar aqui nao pode travar nada

    def _carrega_projeto(self, caminho: str, *, como_projeto: bool = True,
                         rotulo: str = "Projeto aberto") -> bool:
        """Le um .msd e o poe na interface. Unico caminho de carga.

        `como_projeto=False` carrega sem adotar o arquivo como destino de
        Ctrl+S: e' o caso da importacao de um caso da validacao, que vive no
        repositorio, e' regenerado por `build_saved_cases.py` e nao pode ser
        sobrescrito por um Ctrl+S distraido. Quem importa e edita cai em
        "Salvar como" e grava onde quiser.
        """
        from PyQt6.QtWidgets import QMessageBox
        from ...core.models.model import MSDModel

        try:
            modelo = MSDModel.load(caminho)
        except Exception as exc:                             # noqa: BLE001
            from ..i18n import Lang
            QMessageBox.warning(self, Lang.tr("Abrir projeto", "Open project"),
                                Lang.tr(f"Não foi possível abrir:\n{exc}",
                                        f"Could not open:\n{exc}"))
            return False
        if como_projeto:
            self._caminho_projeto = caminho
            self._lembra_dir_projeto(caminho)
        else:
            self._caminho_projeto = None
        # mesmo caminho do wizard: poe no AppState, reconstroi o esquematico e
        # leva para o modulo Model
        self._after_wizard(modelo)
        nome = Path(caminho).name
        self.prompt.set_prompt(f"{rotulo}: {nome}")
        self.setWindowTitle(f"Bolt Analysis Studio — {nome}")
        return True

    def _abrir_projeto(self):
        from PyQt6.QtWidgets import QFileDialog

        from ..i18n import Lang
        caminho, _ = QFileDialog.getOpenFileName(
            self, Lang.tr("Abrir projeto", "Open project"),
            self._dir_inicial_projeto(),
            Lang.tr("Modelo MSD (*.msd);;Todos os arquivos (*)",
                    "MSD model (*.msd);;All files (*)"))
        if caminho:
            self._carrega_projeto(caminho)

    def _importar_caso_validacao(self):
        """Abre um dos casos da validacao pelo nome, sem navegar 28 pastas.

        SEM caixa de mensagem no fim. Havia uma, e ela era um defeito de duas
        camadas, reportado por um usuario em 2026-09-04:

          · falava de "repositorio" e "gerador de casos" — palavras que so'
            existem para quem tem o codigo. Para quem instalou o programa, a
            frase nao significa nada;
          · aparecia a CADA importacao, modal, com icone de informacao, o que
            se le como aviso de erro. Acao que deu certo nao interrompe.

        O que a mensagem tentava dizer sobre o Ctrl+S e' verdadeiro e util, mas
        o lugar de dizer isso e' na HORA de salvar, nao antes. Ver
        `_salvar_projeto`.
        """
        from .widgets.case_picker import CasePicker

        dlg = CasePicker(self)
        if not dlg.exec() or not dlg.escolhido:
            return
        self._carrega_projeto(dlg.escolhido, como_projeto=False,
                              rotulo="Caso do artigo aberto")

    # --- calibracao (2026-09-03) ---------------------------------------------
    # O otimizador e o dialogo com trava e limites por parametro ja' existiam;
    # faltava a curva experimental chegar ate' eles no chrome. Duas origens: o
    # caso da validacao de onde o modelo veio, e um CSV do usuario.
    def _modelo_corrente(self):
        """Modelo com a ESTRUTURA do esquematico e o METADADO do estado.

        Mesma composicao de `_grava_projeto`, e pelo mesmo motivo: o desenho
        nao conhece os canais de override, e calibrar a partir do exportado
        puro jogaria fora as constantes adotadas — que sao justamente o ponto
        de partida do ajuste.
        """
        modelo = None
        try:
            modelo = self.model_controller.export_model()
        except Exception:                                    # noqa: BLE001
            modelo = None
        estado = getattr(self.app_state, "model", None)
        if modelo is None:
            return estado
        if estado is not None:
            for campo in self._CARREGA:
                valor = getattr(estado, campo, None)
                if valor:
                    setattr(modelo, campo, valor)
        return modelo

    def _calibrar_parametros(self):
        from PyQt6.QtWidgets import QFileDialog, QMessageBox
        from .widgets.reference_curve import (ReferenceSourceDialog,
                                              caso_do_modelo, curva_de_csv,
                                              curva_do_caso)

        from ..i18n import Lang
        titulo = Lang.tr("Calibrar parâmetros", "Calibrate parameters")
        modelo = self._modelo_corrente()
        if modelo is None or getattr(modelo, "global_loading", None) is None:
            QMessageBox.information(self, titulo, Lang.tr(
                "Monte ou abra um modelo antes de calibrar.",
                "Build or open a model before calibrating."))
            return
        F0 = float(getattr(modelo.global_loading, "F_preload", 0.0) or 0.0)
        if F0 <= 0:
            QMessageBox.warning(self, titulo, Lang.tr(
                "A pré-carga precisa ser maior que zero para calibrar.",
                "The preload must be greater than zero to calibrate."))
            return

        origem = ReferenceSourceDialog(self, caso_do_modelo(modelo))
        if not origem.exec() or not origem.escolha:
            return
        if origem.escolha == "caso":
            ref = curva_do_caso(caso_do_modelo(modelo) or "", F0)
            if ref is None:
                QMessageBox.warning(self, titulo, Lang.tr(
                    "Não encontrei a curva experimental desse caso.",
                    "The experimental curve of this case was not found."))
                return
        else:
            caminho, _ = QFileDialog.getOpenFileName(
                self, Lang.tr("Curva experimental (CSV)",
                              "Experimental curve (CSV)"),
                self._dir_inicial_projeto(),
                Lang.tr("CSV (*.csv);;Todos os arquivos (*)",
                        "CSV (*.csv);;All files (*)"))
            if not caminho:
                return
            try:
                ref = curva_de_csv(caminho, F0)
            except (OSError, ValueError) as exc:
                QMessageBox.warning(self, titulo, Lang.tr(
                    f"Não consegui ler o CSV:\n{exc}",
                    f"Could not read the CSV:\n{exc}"))
                return

        try:
            # ..main_window = bolt_analysis_studio.gui.main_window. Com tres
            # pontos vira bolt_analysis_studio.main_window, que nao existe: o
            # import falhava e caia no QMessageBox de erro, que num ambiente
            # sem usuario simplesmente TRAVA. O v1_host usa tres pontos porque
            # esta' um pacote abaixo (chrome/controllers), nao dois.
            from ..main_window import CalibrationDialog
        except Exception as exc:                             # noqa: BLE001
            QMessageBox.critical(self, titulo, Lang.tr(
                f"Módulo de calibração indisponível:\n{exc}",
                f"Calibration module unavailable:\n{exc}"))
            return
        k_tr = None
        try:
            k_tr = float(getattr(modelo, "k_transverse", 0.0) or 0.0) or None
        except (TypeError, ValueError):
            k_tr = None
        dlg = CalibrationDialog(self, modelo, ref, transverse_stiffness=k_tr)
        dlg.exec()
        # Apply escreve nos canais de override do MESMO objeto; o esquematico e
        # o inspector precisam reler, senao a tela segue mostrando o de antes.
        self.app_state.model = modelo
        try:
            self.model_controller.sync_from_app_state()
        except Exception:                                    # noqa: BLE001
            pass
        self.prompt.set_prompt(Lang.tr(
            f"Calibração encerrada — referência: {ref.get('origem', '')}",
            f"Calibration closed — reference: {ref.get('origem', '')}"))

    def _run_analysis(self):
        """Nome que o botao 'Apply & Re-run' do dialogo procura no pai.

        Sem isto o dialogo aplica e mostra "re-rode a mao": o chrome tem Run,
        so' nao com o nome que a V1 usa.
        """
        self.module_bar.run_requested.emit()

    @staticmethod
    def _e_caso_instalado(caminho) -> bool:
        """Esta' dentro de Models/SAVED_CASES, que e' reinstalado a cada
        atualizacao? Entao nao e' destino de gravacao."""
        try:
            from ...validation.inputs import repo_root
            casos = (repo_root() / "Models" / "SAVED_CASES").resolve()
            return casos in Path(caminho).resolve().parents
        except Exception:                                    # noqa: BLE001
            return False

    def _salvar_projeto(self):
        caminho = getattr(self, "_caminho_projeto", None)
        if caminho and not self._e_caso_instalado(caminho):
            self._grava_projeto(caminho)
            return
        # Sem destino ainda — ou o destino e' um caso INSTALADO, aberto por
        # "Abrir projeto" direto em Models/SAVED_CASES: nos dois cai em
        # "Salvar como". Gravar em cima do caso instalado sumiria na proxima
        # atualizacao e mudava o arquivo de referencia (o smoke pegou isso em
        # 2026-09-05: a varredura Abrir→Salvar reescreveu o .msd do artigo).
        # Se o modelo veio de um caso, a razao e' essa, e dizer isso AQUI —
        # no momento em que o usuario pediu para salvar — e' o que substitui
        # a caixa de mensagem que aparecia na importacao e nao significava
        # nada para quem instalou o programa (defeito reportado em 2026-09-04).
        from ..i18n import Lang
        try:
            from .widgets.reference_curve import caso_do_modelo
            veio_de_caso = caso_do_modelo(getattr(self.app_state, "model", None))
        except Exception:                                    # noqa: BLE001
            veio_de_caso = None
        if veio_de_caso:
            self.prompt.set_prompt(Lang.tr(
                f"Este modelo veio do caso {veio_de_caso}, que é reinstalado a "
                f"cada atualização — escolha onde salvar a sua cópia.",
                f"This model came from case {veio_de_caso}, which is "
                f"reinstalled on every update — choose where to save your copy."))
        elif caminho:
            self.prompt.set_prompt(Lang.tr(
                "Este arquivo é um caso instalado com o programa, reinstalado a "
                "cada atualização — escolha onde salvar a sua cópia.",
                "This file is a case installed with the program, reinstalled "
                "on every update — choose where to save your copy."))
        self._salvar_projeto_como()

    def _salvar_projeto_como(self):
        from PyQt6.QtWidgets import QFileDialog
        from ..i18n import Lang

        sugestao = getattr(self, "_caminho_projeto", None) or str(
            Path(self._dir_inicial_projeto()) / "projeto.msd")
        if self._e_caso_instalado(sugestao):
            # sugerir o proprio caso convidaria a gravar em cima dele
            pasta = Path(self._dir_inicial_projeto())
            if self._e_caso_instalado(pasta / "x"):
                pasta = Path.home()
            sugestao = str(pasta / Path(sugestao).name)
        caminho, _ = QFileDialog.getSaveFileName(
            self, Lang.tr("Salvar projeto como", "Save project as"), sugestao,
            Lang.tr("Modelo MSD (*.msd);;Todos os arquivos (*)",
                    "MSD model (*.msd);;All files (*)"))
        if caminho:
            self._grava_projeto(caminho)

    def _grava_projeto(self, caminho: str) -> None:
        from PyQt6.QtWidgets import QMessageBox

        # export_model() le o ESQUEMATICO, e' o que garante que uma edicao no
        # canvas ainda nao propagada entre no arquivo. MAS o desenho nao conhece
        # os canais de override, a descricao nem o nome: esses vivem no modelo
        # do AppState. Salvar so' com o exportado perdia as 23 constantes
        # adotadas e a citacao da fonte — o arquivo abria com os 11 elementos e
        # o F0 certos, e estava errado. Pego pelo teste de ida e volta em
        # 2026-09-03, e e' a mesma perda silenciosa que MSDModel.to_dict tinha,
        # um andar acima. Estrutura vem do esquematico, metadado vem do estado.
        from ..i18n import Lang
        titulo = Lang.tr("Salvar projeto", "Save project")
        modelo = self._modelo_corrente()
        if modelo is None:
            QMessageBox.warning(self, titulo, Lang.tr(
                "Não há modelo para salvar.", "There is no model to save."))
            return
        try:
            modelo.save(caminho)
        except Exception as exc:                             # noqa: BLE001
            QMessageBox.warning(self, titulo, Lang.tr(
                f"Não foi possível salvar:\n{exc}", f"Could not save:\n{exc}"))
            return
        self._caminho_projeto = caminho
        self._lembra_dir_projeto(caminho)
        nome = Path(caminho).name
        from ..i18n import Lang
        self.prompt.set_prompt(Lang.tr(f"Projeto salvo: {caminho}",
                                       f"Project saved: {caminho}"))
        self.setWindowTitle(f"Bolt Analysis Studio — {nome}")

    def _open_wizard(self):
        try:
            from ..new_analysis_wizard import NewAnalysisWizard, build_model
            from PyQt6.QtWidgets import QDialog
            wiz = NewAnalysisWizard(self)
            if wiz.exec() == QDialog.DialogCode.Accepted:
                self._after_wizard(build_model(wiz.spec()))
        except Exception as exc:  # pragma: no cover - defensivo na fundacao
            self.prompt.set_prompt(f"Wizard indisponivel: {exc}")

    def _apply_theme(self, key: str) -> None:
        from PyQt6.QtWidgets import QApplication
        from ..theme import Theme
        try:
            Theme.set_theme(key)                  # dispara callbacks (ícones + browser)
            Theme.save_theme_preference()
            app = QApplication.instance()
            if app is not None:
                # nível-app: cascata para a janela V1 oculta + diálogos abertos
                app.setStyleSheet(Theme.get_stylesheet())
            self.setStyleSheet(Theme.get_stylesheet())   # janela chrome
            self._retheme_embedded_v1()           # canvases + labels inline embutidos
        except Exception as exc:  # pragma: no cover - defensivo
            self.prompt.set_prompt(f"Tema indisponível: {exc}")

    def _retheme_embedded_v1(self) -> None:
        """Re-tema o que a V1 embute no chrome (abas solver/results/report): as
        cores dos canvases matplotlib são assadas no draw e os stylesheets inline
        (ex.: summary_load_type, validation_label) congelam no build — nenhum dos
        dois segue a cascata de QSS. Anda pela árvore do CHROME porque as abas V1
        foram RE-PARENTADAS para cá; pula os canvases que se re-temam sozinhos."""
        from ..theme import Theme
        try:
            import matplotlib.pyplot as plt
            from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
            plt.rcParams.update(Theme.get_plot_style())
        except Exception:
            return
        base, surf, text, edge = (Theme.BASE, Theme.SURFACE0,
                                  Theme.TEXT, Theme.SURFACE2)
        for canvas in self.findChildren(FigureCanvasQTAgg):
            if canvas.property("selfThemed"):
                continue                          # ex.: ValidationBrowser (reskin())
            try:
                if hasattr(canvas, "_apply_theme"):
                    canvas._apply_theme()
                    continue
                fig = canvas.figure
                fig.set_facecolor(base)
                for ax in fig.get_axes():
                    ax.set_facecolor(surf)
                    ax.tick_params(colors=text)
                    ax.xaxis.label.set_color(text)
                    ax.yaxis.label.set_color(text)
                    ax.title.set_color(text)
                    for spine in ax.spines.values():
                        spine.set_color(edge)
                canvas.draw_idle()
            except Exception:
                pass
        # stylesheets inline dos tabs V1 (só se a janela V1 já existe)
        host = getattr(self, "_v1_host", None)
        if host is not None and getattr(host, "built", False):
            win = host.window
            for name in ("project_tab", "solver_tab", "results_tab",
                         "similitude_tab", "reports_tab"):
                tab = getattr(win, name, None)
                if tab is not None and hasattr(tab, "refresh_theme"):
                    try:
                        tab.refresh_theme()
                    except Exception:
                        pass

    def eventFilter(self, obj, event):
        from PyQt6.QtCore import QEvent
        cv = getattr(self, "_coords_view", None)
        if (cv is not None and getattr(self, "prompt", None) is not None
                and obj is cv.viewport()
                and event.type() == QEvent.Type.MouseMove):
            pt = cv.mapToScene(event.position().toPoint())
            txt = f"x={pt.x():.0f}  y={pt.y():.0f}"
            self.prompt.set_coords(txt)
            if getattr(self, "_coords_label", None) is not None:
                self._coords_label.setText(txt)
        return super().eventFilter(obj, event)

    def closeEvent(self, event):
        # Desliga do barramento ao fechar: sem isso, uma janela fechada
        # continuaria reagindo a model_changed do singleton AppState (fonte de
        # crash em _fit_view quando varias janelas coexistem/testes).
        try:
            self._save_layout()
        except Exception:               # pragma: no cover - defensivo
            pass
        try:
            self.app_state.model_changed.disconnect(self._on_model_changed)
        except (TypeError, RuntimeError):
            pass
        try:
            from ..theme import Theme
            Theme.unregister_callback(self._reskin_icons)
        except (AttributeError, ValueError):
            pass
        super().closeEvent(event)
