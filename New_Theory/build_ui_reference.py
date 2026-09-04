# -*- coding: utf-8 -*-
"""Referencia de interface COM PRINTS, gerada da propria GUI (2026-09-02).

    py -3.12 New_Theory/build_ui_reference.py

Captura as superficies do chrome V2 com o QPA offscreen e escreve:

    src/bolt_analysis_studio/resources/ui_reference/*.png
    src/bolt_analysis_studio/resources/docs/ui_reference.json   (secao 22)

Um CASO DA VALIDACAO e' carregado antes de capturar. Sem isso os paineis
aparecem vazios, e o print de um painel vazio nao ensina nada — e' a diferenca
entre uma referencia util e uma galeria de telas em branco.

As 11 superficies sao as que se alcancam de forma confiavel por API: os 6
modulos da barra, as 2 sub-abas de Results e as 3 abas do inspector
(`_TAB_INDEX` do model_controller). Preferi 11 capturadas e descritas a 24
prometidas e quebradas; `test_ui_reference.py` afere que a lista aqui cobre o
que a GUI viva expoe, entao uma aba nova amanha acusa em vez de faltar em
silencio.

Os prints saem no BUILD, nunca colados a mao: colado, envelhece calado quando
a UI muda.
"""
from __future__ import annotations

import html
import json
import os
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
if os.name == "nt":
    os.environ.setdefault(
        "QT_QPA_FONTDIR",
        os.path.join(os.environ.get("WINDIR", r"C:\Windows"), "Fonts"))

RECURSOS = RAIZ / "src" / "bolt_analysis_studio" / "resources"
PRINTS = RECURSOS / "ui_reference"
SAIDA = RECURSOS / "docs" / "ui_reference.json"
CASO = "lu2024_M8_fig18_amp0p5"

MODULOS = ["Model", "Contacts", "Loads", "Analysis", "Results", "Report"]

# Prosa por superficie, escrita LENDO os widgets. Cada entrada:
#   (id, titulo, para que serve, [controles])
SUPERFICIES = [
    ("chrome_model", "Model", "Model",
     "The joint as the solver sees it: a chain of mass-spring-damper elements "
     "between the bolt head and the nut, with the clamped members in parallel "
     "and each contact in series. This canvas is the MSD Builder, hosted "
     "inside the module rather than opened as a separate window, so what you "
     "draw here is what runs.",
     ["Palette on the left: drag an element type onto the grid to add it to "
      "the chain.",
      "Double-click an element to edit it; the Element tab of the inspector "
      "opens on the right.",
      "The schematic and the model are kept in sync in both directions: an "
      "edit here updates the model, and loading a case rebuilds the drawing.",
      "Shift+F frames the contents; the framing re-arms whenever a new model "
      "is loaded, so an imported case is never left as a speck in a corner."]),

    ("chrome_contacts", "Contacts", "Contacts",
     "The same chain, with the tribological interfaces in focus. Two of them "
     "decide loosening: the bearing face under the head or nut, and the "
     "thread flank. Friction and wear live on these, not on the bolt.",
     ["Select an interface to open the Contact tab of the inspector.",
      "Friction is set at two levels: a persistent value on the model and an "
      "in-session value on the loading, and the solver honours the more "
      "specific one.",
      "A case loaded from the validation corpus arrives with the friction "
      "coefficient of its adopted configuration already in place."]),

    ("chrome_loads", "Loads", "Loads",
     "Where the excitation is defined and where you can see how it flows "
     "through the joint. Transverse displacement-controlled loading is the "
     "Junker condition; axial force-controlled loading is the other family in "
     "the corpus.",
     ["Loading type, amplitude, frequency and cycle count.",
      "Preload, in newtons or as a percentage of yield; leaving the force at "
      "zero makes the model compute it from the percentage.",
      "The load-flow overlay annotates the chain with the share each element "
      "carries, which is the quickest way to see an implausible stiffness "
      "partition before running anything."]),

    ("chrome_analysis", "Analysis", "Analysis",
     "Solver settings and the run itself. The integration is cycle by cycle "
     "over a slow state, so the settings that matter are the ones that decide "
     "how many cycles are integrated and how finely.",
     ["Cycle count and the sub-stepping inside a cycle.",
      "Which loss mechanisms are active: embedding, creep, fretting wear and "
      "nut rotation act in parallel and can be examined one at a time.",
      "Ctrl+R runs from any module."]),

    ("chrome_results", "Results", "Results",
     "Two sub-tabs: <b>Run</b> shows the curves of the analysis you just ran, "
     "and <b>Validation</b> is the corpus browser. Section 20 of this "
     "documentation lists the sources behind it.",
     ["Run: preload against cycles, the mechanism decomposition, the friction "
      "and phase plots.",
      "Validation: the tree of sources and curves, described in the next "
      "entry.",
      "The context bar above the viewport switches between plot families "
      "without leaving the module."]),

    ("chrome_results_validation", "Results \u2192 Validation",
     "Results, Validation sub-tab",
     "The corpus, as a tree of <b>source paper \u2192 curve</b>. Every curve "
     "carries the model's mean absolute error against the digitised "
     "measurement, so the quality of the fit is visible before you open "
     "anything.",
     ["<b>Abrir no Model/Run</b> loads that curve as the editable model, with "
      "the adopted constants of its case, and switches to the Model module.",
      "<b>Re-simular caso</b> and <b>Re-simular tudo</b> run the engine again "
      "and rewrite the stored result.",
      "<b>Report HTML</b> opens the full report of that case: conditions, the "
      "mass-spring-damper model, the residual against the three legs of the "
      "acceptance criterion, the mechanism decomposition and every constant "
      "with its provenance.",
      "<b>Salvar caso como .msd</b> writes the model to a file with the "
      "adopted configuration and the citation of the source paper inside it. "
      "The whole corpus is already saved that way under "
      "<code>Models/SAVED_CASES/</code>.",
      "The highlighted intake panel at the top imports a case of your own "
      "from a .bascase.json file."]),

    ("dialog_case_picker", "File → Import validation case",
     "File menu, <i>Import validation case</i> (Ctrl+I)",
     "Opens any curve of the corpus by name. The corpus ships as one .msd "
     "per curve under <code>Models/SAVED_CASES/</code>, one folder per source "
     "paper; finding a curve through the file dialogue means knowing which of "
     "the 29 folders holds it and the exact file name, so this dialogue lists "
     "them instead.",
     ["The list shows the <b>205 curves of the paper census</b> by default. "
      "The five records outside the census are reachable by clearing "
      "<i>census only</i>; they are kept apart because no number in the "
      "manuscript counts them, and the reason for each is in Appendix B.",
      "The search box matches the case, the source, the reference and the "
      "DOI, so <code>lu2024</code>, <code>M8</code> or <code>Sensors</code> "
      "all narrow the list.",
      "Each row carries the mean absolute error of the model on that curve "
      "and whether it meets the three-leg acceptance criterion.",
      "The chosen case arrives in its adopted configuration, with the "
      "calibrated constants and the citation of the source paper inside the "
      "model.",
      "The source file is version controlled and regenerated by the case "
      "builder, so an imported case is not adopted as the target of Ctrl+S: "
      "saving asks for a new destination instead of overwriting the "
      "reference."]),

    ("dialog_calibrate", "Analyse → Calibrate model parameters",
     "Analyse menu, <i>Calibrate model parameters</i> (Ctrl+K)",
     "Identifies the constants that were not measured, against an "
     "experimental preload-decay curve. The rule that makes it usable is the "
     "one in the leftmost column: <b>a parameter you do not tick is held at "
     "the value in the model</b>. That is how a quantity you measured stays "
     "fixed while the rest is searched.",
     ["One row per parameter: a checkbox and the two bounds of the search. "
      "The bounds are pre-filled with the physically sensible range of that "
      "constant, and each row carries a tooltip saying what the constant is.",
      "Rows for the k, c and m of individual elements of the chain appear "
      "below the global ones, bounded at half and twice the current value.",
      "Objective (mean absolute error or RMS), evaluation budget and engine. "
      "The forward model is the one the Run uses, so a fit obtained here is "
      "reproduced when the analysis is run.",
      "The preview draws the measurement, the current model and the candidate "
      "fit together; <b>Apply</b> writes the result into the model, "
      "<b>Discard</b> leaves no trace.",
      "The selection and the bounds can be saved as a profile and reloaded "
      "for the next joint of the same fixture."]),

    ("dialog_reference_source", "Reference curve",
     "Curve chosen before calibrating",
     "Which experimental curve the fit is measured against. Two sources: the "
     "validation case the model was imported from, or a CSV of your own.",
     ["From the case: the points come from the source paper, digitised, "
      "already in the campaign's convention (axis scaling, normalisation and "
      "floor trim), which is the same curve the report of that case scores.",
      "From a CSV: two or three columns, <code>cycle, F/F₀</code> or "
      "<code>cycle, F[kN], F/F₀</code>; the first line may be a header.",
      "The case option is offered only when the open model came from a "
      "registered case; otherwise it is disabled and says so."]),

    ("chrome_report", "Report", "Report",
     "Assembles a document from the current analysis. The per-case reports of "
     "the validation corpus are generated from the same machinery, which is "
     "why a report of your own joint has the same sections as the ones behind "
     "Section 20.",
     ["Choice of sections to include.",
      "Export to HTML; the report opens in the system browser rather than in "
      "an embedded view, so no web engine is required."]),

    ("inspector_element", "Inspector \u2192 Element", "Inspector, Element tab",
     "The properties of the selected element. Stiffness, damping and mass can "
     "be typed directly or computed from geometry and material, which is the "
     "usual choice: a bolt's stiffness follows from its diameter, grip length "
     "and modulus.",
     ["k, c and m, each with an <i>auto-calculate</i> switch. With the switch "
      "on, the value is recomputed from geometry and material whenever either "
      "changes.",
      "Geometry: diameter, length, thread pitch.",
      "Material, from the bundled database.",
      "A case from the corpus arrives with the geometry overrides of its "
      "adopted configuration already applied."]),

    ("inspector_loading", "Inspector \u2192 Loading", "Inspector, Loading tab",
     "The excitation and the preload of the selected loading, at the level "
     "that applies in the current session.",
     ["Preload force, or percentage of yield.",
      "Transverse displacement amplitude, or axial force amplitude.",
      "Frequency and number of cycles.",
      "The in-session friction coefficient, which overrides the persistent "
      "one on the model."]),

    ("inspector_contact", "Inspector \u2192 Contact", "Inspector, Contact tab",
     "The tribology of the selected interface: this is where the constants "
     "that the validation calibrates actually live.",
     ["Friction coefficient of the interface.",
      "Contact stiffness and the embedding parameters.",
      "Wear coefficients.",
      "For a case from the corpus, these are the adopted constants; the "
      "provenance of each one is in the case report (Section 20)."]),
]


def _esc(t) -> str:
    return html.escape(str(t or ""), quote=False)


def _captura(app, win, alvo: Path) -> tuple:
    """Grava o print, forcando repintura SINCRONA antes do grab.

    Sem o repaint(), o QPA offscreen entregava frames com FANTASMA: no primeiro
    lote, o painel de propriedades saiu com os rotulos do modulo anterior
    pintados por baixo dos novos, dois textos no mesmo retangulo. Nao era
    defeito de layout — medido, zero dos 38 QLabels visiveis tem geometria
    sobreposta — era o backing store nao limpo entre a troca de modulo e o
    grab. processEvents() sozinho nao garante o repaint; repaint() e' sincrono.
    """
    for _ in range(60):
        app.processEvents()
    win.repaint()
    for _ in range(20):
        app.processEvents()
    pm = win.grab()
    pm.save(str(alvo), "PNG")
    return pm.size().width(), pm.size().height()


def _seleciona_elemento(app, win, nome: str) -> bool:
    """Seleciona um elemento no esquematico para o inspector ter o que mostrar.

    Sem selecao o painel exibe "No element selected" e os valores default, e a
    legenda ficaria falando de um elemento que o print nao mostra. Selecionado
    o SHANK, aparecem a rigidez, o material e a geometria REAIS do caso.
    """
    from bolt_analysis_studio.gui.msd_builder import ElementGraphicsItem

    cena = win.model_controller.schematic.scene()
    itens = [i for i in cena.items() if isinstance(i, ElementGraphicsItem)]

    def _nome(i) -> str:
        d = getattr(i, "element_data", None)
        return " ".join(str(x) for x in (
            getattr(i, "element_id", ""), getattr(i, "element_type", ""),
            getattr(d, "name", ""), getattr(d, "element_id", ""))).lower()

    alvo = next((i for i in itens if nome.lower() in _nome(i)), None)
    if alvo is None:
        raise SystemExit(                     # print mudo e' pior que build que
            f"nenhum elemento '{nome}' no esquematico: "  # para: a legenda
            f"{[_nome(i)[:40] for i in itens]}")          # promete o que o
                                                          # print nao mostra
    cena.clearSelection()
    alvo.setSelected(True)
    for _ in range(20):
        app.processEvents()
    return True


def capturar() -> dict:
    from PyQt6.QtWidgets import QApplication
    app = QApplication.instance() or QApplication(sys.argv)

    from bolt_analysis_studio.core.app_state import get_app_state
    st = get_app_state()
    from bolt_analysis_studio.validation.case_registry import record
    from bolt_analysis_studio.validation.gui_bridge import build_case_model
    st.model = build_case_model(record(CASO))

    from bolt_analysis_studio.gui.chrome.app_window import ChromeWindow
    win = ChromeWindow(st)
    win.resize(1500, 900)
    win.show()
    for _ in range(30):
        app.processEvents()

    PRINTS.mkdir(parents=True, exist_ok=True)
    feitos = {}
    for mod in MODULOS:
        win.switch_module(mod)
        ident = f"chrome_{mod.lower()}"
        feitos[ident] = _captura(app, win, PRINTS / f"{ident}.png")

        if mod == "Results":
            tabs = getattr(win, "_results_tabs", None)
            if tabs is not None:
                for i in range(tabs.count()):
                    if tabs.tabText(i) == "Validation":
                        tabs.setCurrentIndex(i)
                        br = win.validation_controller.browser
                        br.show_case(CASO)
                        feitos["chrome_results_validation"] = _captura(
                            app, win, PRINTS / "chrome_results_validation.png")
        if mod == "Model":
            # As tres entradas do inspector saiam BYTE A BYTE iguais ao print do
            # modulo Model: o dock "Properties" chega escondido (o layout vem do
            # QSettings da maquina que roda o build) e as abas trocavam atras de
            # um painel invisivel. Tres legendas prometiam uma aba especifica e
            # mostravam a mesma tela. Aqui o dock e' forcado a aparecer, e o que
            # se grava e' o PAINEL, nao a janela inteira: num quadro de 1500 px
            # o inspector tem 240 e ficava ilegivel.
            dock = win._inspector_dock
            dock.setVisible(True)
            dock.raise_()
            dock.resize(340, dock.height() or 640)
            _seleciona_elemento(app, win, "SHANK")
            for kind in ("element", "loading", "contact"):
                win.model_controller.show_inspector_tab(kind)
                ident = f"inspector_{kind}"
                feitos[ident] = _captura(app, dock, PRINTS / f"{ident}.png")

    # O seletor e' um dialogo modal: nao entra em nenhum print de modulo. E'
    # grabado direto, sem exec(), que bloquearia o build.
    from bolt_analysis_studio.gui.chrome.widgets.case_picker import CasePicker
    dlg = CasePicker()
    dlg.resize(900, 620)
    dlg.show()
    feitos["dialog_case_picker"] = _captura(app, dlg,
                                            PRINTS / "dialog_case_picker.png")
    dlg.close()

    # Escolha da curva de referencia e o dialogo de calibracao, com o caso
    # carregado: sem modelo E sem curva o painel sai vazio e a legenda falaria
    # de linhas que o print nao tem.
    from bolt_analysis_studio.gui.chrome.widgets.reference_curve import (
        ReferenceSourceDialog, curva_do_caso)
    src = ReferenceSourceDialog(None, CASO)
    src.resize(560, 300)
    src.show()
    feitos["dialog_reference_source"] = _captura(
        app, src, PRINTS / "dialog_reference_source.png")
    src.close()

    ref = curva_do_caso(CASO, float(st.model.global_loading.F_preload))
    if ref is None:
        raise SystemExit(f"sem curva de referencia para {CASO}: rode o runner")
    from bolt_analysis_studio.gui.main_window import CalibrationDialog
    cal = CalibrationDialog(None, st.model, ref)
    cal.resize(1400, 820)
    cal.show()
    feitos["dialog_calibrate"] = _captura(app, cal,
                                          PRINTS / "dialog_calibrate.png")
    cal.close()
    return feitos


def secao(feitos: dict) -> str:
    p = ["<h2>22. Interface reference</h2>",
         "<p>One entry per screen, with a capture of that screen taken from "
         "the running program. A validation case is loaded in every capture, "
         "so the panels show real content. The captures are generated when "
         "the documentation is built, never pasted by hand: a pasted "
         "screenshot goes stale silently when the interface changes.</p>",
         "<p>The module bar at the top of the window switches between "
         "<b>Model</b>, <b>Contacts</b>, <b>Loads</b>, <b>Analysis</b>, "
         "<b>Results</b> and <b>Report</b>. <b>Ctrl+1</b> to <b>Ctrl+6</b> do "
         "the same, <b>Ctrl+R</b> runs, and <b>Shift+F</b> frames the "
         "drawing.</p>"]
    n = 0
    for ident, titulo, _legenda, proposito, controles in SUPERFICIES:
        if ident not in feitos:
            continue
        n += 1
        p.append(f"<h3>22.{n} {_esc(titulo)}</h3>")
        p.append(f"<p>{proposito}</p>")
        larg, alt = feitos[ident]
        p.append(f'<p><img src="ui_reference/{ident}.png" width="900"></p>')
        p.append(f"<p style='color:{{{{SUBTEXT}}}};font-size:{{{{FONT_SIZE_MICRO}}}}'>"
                 f"Capture of {_esc(titulo)} at {larg}\u00d7{alt} px, with case "
                 f"<code>{_esc(CASO)}</code> loaded.</p>")
        if controles:
            p.append("<p><b>Controls</b></p><ul>")
            p += [f"<li>{c}</li>" for c in controles]
            p.append("</ul>")
    return "\n".join(p)


def main(argv=None) -> int:
    feitos = capturar()
    esperados = {s[0] for s in SUPERFICIES}
    faltando = sorted(esperados - set(feitos))
    if faltando:
        raise SystemExit(
            f"[ui-ref] {len(faltando)} superficies descritas mas NAO "
            f"capturadas: {faltando}. Uma entrada sem print deixaria a secao "
            f"com texto sobre uma tela que ninguem ve.")

    SAIDA.parent.mkdir(parents=True, exist_ok=True)
    SAIDA.write_text(json.dumps({
        "ui_reference": {
            "title": f"22. Interface Reference ({len(feitos)} screens)",
            "content": secao(feitos),
        }}, ensure_ascii=False, indent=1), encoding="utf-8")

    total = sum(f.stat().st_size for f in PRINTS.glob("*.png")) / 2**20
    print(f"  {len(feitos)} prints -> {PRINTS}  ({total:.1f} MB)")
    for ident, (w, h) in sorted(feitos.items()):
        print(f"    {ident:32s} {w}x{h}")
    print(f"  secao -> {SAIDA}  ({SAIDA.stat().st_size/1024:.0f} KB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
