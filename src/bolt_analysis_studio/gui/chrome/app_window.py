"""ChromeWindow — shell CAE do BAS V2 (spec abaqus §3). Opt-in via run_app.py --v2.

Reutiliza Theme (design-system) e AppState (barramento) as-is; a V1 de 7 abas
permanece como fallback. Os viewports mostram placeholders nomeados — os modulos
reais vem em planos subsequentes.
"""
from __future__ import annotations

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
_PROMPTS = {
    "Model": "Adicione ou selecione elementos no viewport.",
    "Contacts": "Defina contatos e modelos de atrito/desgaste.",
    "Loads": "Configure o carregamento global e por-elemento.",
    "Analysis": "Defina os steps e rode a analise.",
    "Results": "Inspecione os plots e overlays de validacao.",
    "Report": "Monte o relatorio e escolha o formato.",
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
        self.setWindowTitle("Bolt Analysis Studio V2 (chrome)")
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
        from ..icons import clear_icon_cache
        from ..theme import Theme

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
        mb = self.menuBar()
        file_menu = mb.addMenu("Arquivo")
        act = file_menu.addAction("Nova Análise…")
        act.setShortcut("Ctrl+Shift+N")
        act.triggered.connect(self._open_wizard)
        file_menu.addSeparator()
        file_menu.addAction("Sair", self.close)
        mb.addMenu("Editar")
        view_menu = mb.addMenu("Exibir")
        theme_menu = view_menu.addMenu("Tema")
        from ..theme import PALETTE_NAMES
        for key, label in PALETTE_NAMES.items():
            theme_menu.addAction(
                label, lambda _c=False, k=key: self._apply_theme(k))
        # Painéis colapsáveis: laterais (Model Tree/Properties) ganham botão X no
        # título p/ colapsar direto; Messages colapsa pelo cabeçalho ▼. O menu
        # Exibir > Painéis liga/desliga cada painel (toggled -> setVisible explícito,
        # com sync bidirecional — o toggleViewAction nativo não escondia os docks).
        from PyQt6.QtGui import QAction
        view_menu.addSeparator()
        panels_menu = view_menu.addMenu("Painéis")
        for dock, plabel, closable in (
                (self._tree_dock, "Model Tree", True),
                (self._inspector_dock, "Properties", True),
                (self._palette_dock, "Elements", True),
                (self._msg_dock, "Área de mensagens", False)):
            if closable:
                dock.setFeatures(dock.features()
                                 | QDockWidget.DockWidgetFeature.DockWidgetClosable)
            pact = QAction(plabel, self)
            pact.setCheckable(True)
            pact.setChecked(True)
            pact.toggled.connect(dock.setVisible)
            dock.visibilityChanged.connect(pact.setChecked)
            panels_menu.addAction(pact)
        # Nomes de módulo em inglês (proper nouns do Abaqus): Model/Contacts/…
        mod_menu = mb.addMenu("Módulo")
        for m in MODULES:
            mod_menu.addAction(m, lambda _c=False, name=m: self.switch_module(name))
        help_menu = mb.addMenu("Ajuda")
        # A documentacao vem PRIMEIRO: ate' 2026-09-02 as 25 secoes so'
        # existiam na janela V1 e o chrome V2, que e' o padrao, nao tinha
        # porta para elas. Escrito e inalcancavel e' o mesmo que ausente.
        help_menu.addAction("Documentação (F1)", self._open_documentation)
        help_menu.addAction("Idioma: Português / English",
                            self._toggle_idioma)
        help_menu.addSeparator()
        help_menu.addAction("Reports de Validação (210 casos)",
                            self._open_validation_docs)
        help_menu.addAction("Prompt de intake (IA) — copiar",
                            self._copy_intake_prompt)

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
        self.prompt.set_prompt(_PROMPTS.get(name, ""))
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
        self.statusBar().showMessage(f"Projeto: — · Modulo: {name} · Job: idle")
        self.module_bar.mark_module(name)

    # --- handlers ---
    _ACTION_HELP = {
        "+ Element": "Selecione um ponto no viewport para inserir o elemento.",
        "+ Thread": "Selecione a porca e depois o parafuso para criar o ThreadContact.",
        "+ Bearing": "Selecione as duas faces em contato para criar o bearing.",
        "+ Global Load": "Defina F0, amplitude e frequência no inspector à direita.",
        "+ Coupled-Loosening": "Configure dt e n_cycles; rode pela V1 até a Fase 4.",
    }

    def _on_context_action(self, label: str):
        self.prompt.set_prompt(self._ACTION_HELP.get(
            label, f"{label}: configure os parâmetros no inspector."))

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
        self.statusBar().showMessage(
            f"Projeto: — · Modulo: {self._current_module} · Job: {state}")
        if state == "error":
            self.prompt.set_prompt("A análise falhou — veja o Job Log para o motivo.")
        elif state == "done":
            self.prompt.set_prompt("Análise concluída — veja os plots no módulo Results.")

    def _run_shortcut(self) -> None:
        if self.module_bar._run_btn.isEnabled():
            self.module_bar.run_requested.emit()

    def refresh_empty_state(self) -> None:
        """Sem modelo carregado, o prompt orienta a abrir o wizard."""
        if getattr(self.app_state, "model", None) is None:
            self.prompt.set_prompt("Nenhum modelo carregado — Ctrl+Shift+N abre o "
                                   "wizard de nova análise.")

    def _results_empty_hint(self) -> None:
        """Em Results/Report sem resultado, orienta a rodar a análise."""
        if getattr(self.app_state, "results", None) is None:
            self.prompt.set_prompt("Nenhum resultado ainda — rode uma análise no "
                                   "módulo Analysis (Ctrl+R).")

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
            self.prompt.set_prompt("Exclusão pela árvore ainda não implementada — "
                                   "edite no Model Builder (duplo-clique no elemento).")

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
        self.validation_controller.copy_prompt()
        self.prompt.set_prompt("Prompt de intake copiado — cole em qualquer "
                               "IA junto com sua curva experimental.")

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
            self.prompt.set_prompt(f"Documentação indisponível: {exc}")
            return
        if getattr(self, "_doc_win", None) is None:
            win = QWidget()
            win.setWindowTitle("Bolt Analysis Studio — Documentação")
            win.resize(1180, 820)
            lay = QVBoxLayout(win)
            lay.setContentsMargins(0, 0, 0, 0)
            lay.addWidget(DocumentationTab())
            self._doc_win = win
        self._doc_win.show()
        self._doc_win.raise_()
        self._doc_win.activateWindow()

    def _toggle_idioma(self):
        """Alterna PT/EN. As secoes 23-25 do help sao bilingues; as 18 antigas
        seguem em ingles, e a aba mostra o ingles nelas."""
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
        self.prompt.set_prompt(
            "Idioma: " + ("English" if Lang.is_en() else "Português"))

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
        self.prompt.set_prompt("Modelo criado. Revise em Model → Loads → Analysis "
                               "e rode em Analysis.")

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
