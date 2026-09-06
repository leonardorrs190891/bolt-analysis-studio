# -*- coding: utf-8 -*-
"""Guia de uso NARRADO: um HTML por aba, com print, voz e cada controle explicado.

    py -3.12 New_Theory/build_guia_narrado.py [--sem-audio] [--so pt|en]

Pedido do professor (2026-09-04): "html narrado (Antonio Neural) por cada tab do
software, um html por tab/passo, explicando cada variavel e botao que aparecer",
nas duas linguas.

O que sai, em New_Theory/guia_uso/<lang>/:
  index.html            — sumario com um cartao por passo
  NN_<passo>.html       — a pagina do passo: print, player de audio, transcricao
                          e a tabela "cada controle, o que faz"
  img/<chave>.png       — prints tirados DO APP NAQUELE IDIOMA, neste build
  audio/<chave>.mp3     — narracao sintetizada (pt-BR-AntonioNeural /
                          en-US-AndrewNeural), com cache por hash do texto

Tres disciplinas, herdadas do resto do repositorio:
  · print nunca e' colado a mao — colado, envelhece calado quando a UI muda;
  · o texto vem de `guia_conteudo.py`, um so' lugar, PT e EN lado a lado;
  · a voz e' cacheada por sha1(voz + texto): rodar de novo sem mudar o texto
    nao chama a rede, e mudar uma frase re-sintetiza so' aquela pagina.

A sintese usa o servico online do Microsoft Edge (pacote edge-tts). Sem rede,
`--sem-audio` gera as paginas sem player, e o build diz isso em vez de falhar.
"""
from __future__ import annotations

import hashlib
import html
import json
import os
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))
sys.path.insert(0, str(RAIZ / "New_Theory"))
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
if os.name == "nt":
    os.environ.setdefault(
        "QT_QPA_FONTDIR",
        os.path.join(os.environ.get("WINDIR", r"C:\Windows"), "Fonts"))

from guia_conteudo import GLOSSARIO, PASSOS, VOZES  # noqa: E402  (depois do sys.path)

SAIDA = RAIZ / "New_Theory" / "guia_uso"
CASO = "lu2024_M8_fig18_amp0p5"
# tudo que `capturar` tira; o conteudo so pode pedir prints desta lista
PRINTS = ("chrome_model", "chrome_contacts", "chrome_loads", "chrome_analysis",
          "chrome_results", "chrome_report", "chrome_results_validation",
          "inspector_element", "inspector_loading", "inspector_contact",
          "dialog_case_picker", "dialog_reference_source", "dialog_calibrate",
          "wizard_p1", "documentation_tab",
          # licao "primeiro modelo MSD" (2026-09-05)
          "paleta_elementos", "modelo_vazio", "cadeia_serie", "cadeia_paralelo",
          "diagrama_serie_paralelo", "grid_position",
          # licao "consultar os casos da validacao"
          "validation_arvore", "validation_detalhe",
          # mais telas didaticas (2026-09-05)
          "wizard_p2", "wizard_p3", "wizard_p4", "wizard_p5",
          "model_tree", "tema_claro", "cadeia_gaxeta", "log_do_job")
LINGUAS = ("pt", "en")

# --------------------------------------------------------------------------
# capturas
# --------------------------------------------------------------------------

def _captura(app, widget, alvo: Path) -> None:
    """Grab com repaint sincrono — sem ele o QPA offscreen entrega fantasmas
    (medido em 2026-09-02 na referencia de interface)."""
    for _ in range(60):
        app.processEvents()
    widget.repaint()
    for _ in range(20):
        app.processEvents()
    alvo.parent.mkdir(parents=True, exist_ok=True)
    widget.grab().save(str(alvo), "PNG")


def _seleciona(app, win, nome: str) -> None:
    from bolt_analysis_studio.gui.msd_builder import ElementGraphicsItem
    cena = win.model_controller.schematic.scene()
    for it in cena.items():
        if isinstance(it, ElementGraphicsItem):
            rot = " ".join(str(x) for x in (
                getattr(it, "element_id", ""), getattr(it, "element_type", ""),
                getattr(getattr(it, "element_data", None), "name", ""))).lower()
            if nome.lower() in rot:
                cena.clearSelection()
                it.setSelected(True)
                for _ in range(20):
                    app.processEvents()
                return


def _demo_gaxeta():
    """A mesma junta, com uma gaxeta no lugar de um dos flanges.

    A gaxeta e' tres ordens de grandeza mais macia; em serie, e' ela que manda
    na rigidez do conjunto. E' a regra "1/k = soma dos 1/k" ficando visivel no
    proprio desenho, com o k e a fracao de carga de cada bloco."""
    from bolt_analysis_studio.core.models.element import (ElementType,
                                                          MSDElementData)
    from bolt_analysis_studio.core.models.model import MSDModel

    m = MSDModel()
    m.name = "Gasket"
    receita = [
        ("Ground", ElementType.GROUND, 1e9),
        ("Bolt Head", ElementType.HEAD, 8.2e8),
        ("Shank", ElementType.SHANK, 2.1e8),
        ("Bearing (Head)", ElementType.BEARING_HEAD, 1.0e10),
        ("Flange", ElementType.FLANGE, 3.9e9),
        ("Gasket", ElementType.GASKET, 4.5e6),        # ~1000x mais macia
        ("Bearing (Nut)", ElementType.BEARING_NUT, 1.0e10),
        ("Nut", ElementType.NUT, 8.2e8),
    ]
    for i, (nome, tipo, k) in enumerate(receita, start=1):
        el = MSDElementData(id=i, name=nome, type=tipo)
        el.msd.k = k
        el.msd.c = 0.0
        el.msd.m = 0.05
        el.grid_position.row = i - 1
        el.grid_position.column = 0
        m.add_element(el)
    m.global_loading.F_preload = 12000.0
    return m


def _roda_analise(app, win, segundos: float = 240.0) -> bool:
    """Roda a analise e espera terminar. Sem isto, Results e Report sao
    fotografados vazios — foi o que aconteceu ate' 2026-09-05."""
    import time
    estados = []
    try:
        win.analysis_controller.job_state.connect(estados.append)
        win.switch_module("Analysis")
        for _ in range(30):
            app.processEvents()
        win._run_shortcut()
        limite = time.time() + segundos
        while time.time() < limite:
            for _ in range(10):
                app.processEvents()
            if any(e in ("done", "error") for e in estados):
                break
            time.sleep(0.05)
    except Exception as exc:                                 # noqa: BLE001
        print(f"  [aviso] analise nao rodou: {exc}")
        return False
    if "done" not in estados:
        print(f"  [aviso] analise nao terminou a tempo: {estados[-3:]}")
        return False
    for _ in range(40):
        app.processEvents()
    return True


def _demo(paralelo: bool):
    """Duas juntas iguais em tudo, menos na topologia dos membros apertados.

    Em serie os dois flanges ocupam LINHAS diferentes: a mesma carga atravessa
    os dois e as flexibilidades se somam. Em paralelo ocupam a MESMA linha, em
    COLUNAS diferentes: a carga se divide entre eles e as rigidezes se somam.
    E' a diferenca que a licao precisa mostrar com o desenho do proprio
    programa, e nao com um desenho meu."""
    from bolt_analysis_studio.core.models.element import (ElementType,
                                                          MSDElementData)
    from bolt_analysis_studio.core.models.model import MSDModel

    m = MSDModel()
    m.name = "Paralelo" if paralelo else "Serie"
    receita = [
        ("Ground", ElementType.GROUND, 1e9, 0),
        ("Bolt Head", ElementType.HEAD, 8.2e8, 0),
        ("Shank", ElementType.SHANK, 2.1e8, 0),
        ("Bearing (Head)", ElementType.BEARING_HEAD, 1.0e10, 0),
        ("Flange A", ElementType.FLANGE, 3.9e9, 0),
        ("Flange B", ElementType.FLANGE, 3.9e9, 1 if paralelo else 0),
        ("Bearing (Nut)", ElementType.BEARING_NUT, 1.0e10, 0),
        ("Nut", ElementType.NUT, 8.2e8, 0),
    ]
    linha = 0
    for i, (nome, tipo, k, coluna) in enumerate(receita, start=1):
        el = MSDElementData(id=i, name=nome, type=tipo)
        el.msd.k = k
        el.msd.c = 0.0
        el.msd.m = 0.05
        # a posicao mora em grid_position; `el.column` seria atributo novo que
        # o desenho nunca le (pego em 2026-09-05, os dois prints sairam iguais)
        el.grid_position.column = coluna
        if paralelo and nome == "Flange B":
            el.grid_position.row = linha - 1   # divide a linha com o irmao
        else:
            el.grid_position.row = linha
            linha += 1
        m.add_element(el)
    m.global_loading.F_preload = 12000.0
    return m


def _diagrama(alvo: Path, lang: str) -> None:
    """Desenho das duas topologias com as formulas. E' DESENHO, nao print: a
    legenda na pagina diz isso."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import FancyArrowPatch, Rectangle

    pt = lang == "pt"
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9.2, 4.4))
    fig.patch.set_facecolor("white")

    def caixa(ax, x, y, w, h, texto, cor):
        ax.add_patch(Rectangle((x, y), w, h, facecolor=cor, edgecolor="#334155",
                               linewidth=1.4, zorder=2))
        ax.text(x + w / 2, y + h / 2, texto, ha="center", va="center",
                fontsize=9.5, zorder=3, color="#0f172a")

    def seta(ax, x0, y0, x1, y1):
        ax.add_patch(FancyArrowPatch((x0, y0), (x1, y1), arrowstyle="-",
                                     color="#334155", linewidth=1.4, zorder=1))

    # --- serie
    ax1.set_title("Em série" if pt else "In series", fontsize=12, pad=12,
                  color="#0f172a")
    caixa(ax1, 1.0, 3.4, 2.0, 0.8, "Flange A", "#dbeafe")
    caixa(ax1, 1.0, 2.0, 2.0, 0.8, "Flange B", "#dbeafe")
    seta(ax1, 2.0, 3.4, 2.0, 2.8)
    seta(ax1, 2.0, 4.2, 2.0, 4.8)
    seta(ax1, 2.0, 2.0, 2.0, 1.4)
    ax1.text(2.0, 5.05, "F", ha="center", fontsize=11, color="#b91c1c")
    ax1.text(2.0, 1.15, "F", ha="center", fontsize=11, color="#b91c1c")
    ax1.text(3.25, 3.8, "F", fontsize=10, color="#b91c1c")
    ax1.text(3.25, 2.4, "F", fontsize=10, color="#b91c1c")
    ax1.text(2.0, 0.55,
             "1/k = 1/k$_A$ + 1/k$_B$" if pt else "1/k = 1/k$_A$ + 1/k$_B$",
             ha="center", fontsize=11.5, color="#0f172a")
    ax1.text(2.0, 0.05,
             "a mesma carga atravessa os dois;\nas flexibilidades se somam"
             if pt else
             "the same load passes through both;\nflexibilities add",
             ha="center", fontsize=9, color="#475569")

    # --- paralelo
    ax2.set_title("Em paralelo" if pt else "In parallel", fontsize=12, pad=12,
                  color="#0f172a")
    caixa(ax2, 0.25, 2.7, 1.6, 0.8, "Flange A", "#dcfce7")
    caixa(ax2, 2.15, 2.7, 1.6, 0.8, "Flange B", "#dcfce7")
    seta(ax2, 2.0, 4.8, 2.0, 4.2)
    seta(ax2, 1.05, 4.2, 2.95, 4.2)
    seta(ax2, 1.05, 4.2, 1.05, 3.5)
    seta(ax2, 2.95, 4.2, 2.95, 3.5)
    seta(ax2, 1.05, 2.7, 1.05, 2.0)
    seta(ax2, 2.95, 2.7, 2.95, 2.0)
    seta(ax2, 1.05, 2.0, 2.95, 2.0)
    seta(ax2, 2.0, 2.0, 2.0, 1.4)
    ax2.text(2.0, 5.05, "F", ha="center", fontsize=11, color="#b91c1c")
    ax2.text(2.0, 1.15, "F", ha="center", fontsize=11, color="#b91c1c")
    ax2.text(0.72, 3.75, "F$_A$", fontsize=10, color="#b91c1c")
    ax2.text(3.05, 3.75, "F$_B$", fontsize=10, color="#b91c1c")
    ax2.text(2.0, 0.55, "k = k$_A$ + k$_B$", ha="center", fontsize=11.5,
             color="#0f172a")
    ax2.text(2.0, 0.05,
             "a carga se divide entre os dois;\nas rigidezes se somam"
             if pt else
             "the load splits between them;\nstiffnesses add",
             ha="center", fontsize=9, color="#475569")

    for ax in (ax1, ax2):
        ax.set_xlim(-0.1, 4.1)
        ax.set_ylim(-0.5, 5.4)
        ax.axis("off")
    fig.tight_layout()
    alvo.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(alvo, dpi=132, facecolor="white")
    plt.close(fig)


def capturar(lang: str, img_dir: Path) -> dict:
    """Tira todos os prints que o conteudo pede, no idioma dado."""
    from PyQt6.QtWidgets import QApplication
    app = QApplication.instance() or QApplication(sys.argv)

    from bolt_analysis_studio.gui.i18n import Lang
    Lang.set_lang(lang)

    from bolt_analysis_studio.core.app_state import get_app_state
    from bolt_analysis_studio.validation.case_registry import record
    from bolt_analysis_studio.validation.gui_bridge import build_case_model
    st = get_app_state()
    st.model = build_case_model(record(CASO))

    from bolt_analysis_studio.gui.chrome.app_window import ChromeWindow
    win = ChromeWindow(st)
    win.resize(1500, 900)
    win.show()
    for _ in range(30):
        app.processEvents()

    feitos = {}
    # a analise roda primeiro: Results e Report so' ensinam com resultado na
    # tela (ate' 2026-09-05 as duas saiam com "nenhum resultado ainda")
    rodou = _roda_analise(app, win)
    if rodou:
        _captura(app, win.messages, img_dir / "log_do_job.png")
        feitos["log_do_job"] = True

    for mod in ("Model", "Contacts", "Loads", "Analysis", "Results", "Report"):
        win.switch_module(mod)
        chave = f"chrome_{mod.lower()}"
        _captura(app, win, img_dir / f"{chave}.png")
        feitos[chave] = True
        if mod == "Results":
            tabs = getattr(win, "_results_tabs", None)
            if tabs is not None:
                for i in range(tabs.count()):
                    if tabs.tabText(i) == "Validation":
                        tabs.setCurrentIndex(i)
                        win.validation_controller.browser.show_case(CASO)
                        _captura(app, win, img_dir / "chrome_results_validation.png")
                        feitos["chrome_results_validation"] = True
        if mod == "Model":
            dock = win._inspector_dock
            dock.setVisible(True)
            dock.raise_()
            dock.resize(340, dock.height() or 640)
            _seleciona(app, win, "SHANK")
            for kind in ("element", "loading", "contact"):
                win.model_controller.show_inspector_tab(kind)
                _captura(app, dock, img_dir / f"inspector_{kind}.png")
                feitos[f"inspector_{kind}"] = True

    # --- licao "primeiro modelo MSD": paleta, vazio, serie, paralelo --------
    win.switch_module("Model")
    pal = win._palette_dock
    pal.setVisible(True)
    pal.raise_()
    _captura(app, pal, img_dir / "paleta_elementos.png")
    feitos["paleta_elementos"] = True

    insp = win._inspector_dock
    insp.setVisible(True)
    insp.raise_()
    _seleciona(app, win, "SHANK")
    win.model_controller.show_inspector_tab("element")
    _captura(app, insp, img_dir / "grid_position.png")
    feitos["grid_position"] = True

    from bolt_analysis_studio.core.models.model import MSDModel
    vazio = MSDModel()
    vazio.name = "New Analysis"
    st.model = vazio
    win.tree.populate(vazio)
    win.model_controller.sync_from_app_state()
    _captura(app, win, img_dir / "modelo_vazio.png")
    feitos["modelo_vazio"] = True

    for chave, paralelo in (("cadeia_serie", False), ("cadeia_paralelo", True)):
        st.model = _demo(paralelo)
        win.tree.populate(st.model)
        win.model_controller.sync_from_app_state()
        try:
            win.model_controller.schematic.fit_view()
        except Exception:                                    # noqa: BLE001
            pass
        _captura(app, win, img_dir / f"{chave}.png")
        feitos[chave] = True

    st.model = _demo_gaxeta()
    win.tree.populate(st.model)
    win.model_controller.sync_from_app_state()
    try:
        win.model_controller.schematic.fit_view()
    except Exception:                                        # noqa: BLE001
        pass
    _captura(app, win, img_dir / "cadeia_gaxeta.png")
    feitos["cadeia_gaxeta"] = True

    _diagrama(img_dir / "diagrama_serie_paralelo.png", lang)
    feitos["diagrama_serie_paralelo"] = True

    # volta ao caso do artigo para o resto das capturas
    st.model = build_case_model(record(CASO))
    win.tree.populate(st.model)
    win.model_controller.sync_from_app_state()

    # --- licao "consultar os casos da validacao" ---------------------------
    win.switch_module("Results")
    tabs = getattr(win, "_results_tabs", None)
    if tabs is not None:
        for i in range(tabs.count()):
            if tabs.tabText(i) == "Validation":
                tabs.setCurrentIndex(i)
                break
    browser = win.validation_controller.browser
    browser.show_case(CASO)
    for _ in range(20):
        app.processEvents()
    arvore = getattr(browser, "tree", None) or getattr(browser, "_tree", None)
    if arvore is not None:
        _captura(app, arvore, img_dir / "validation_arvore.png")
        feitos["validation_arvore"] = True
    _captura(app, browser, img_dir / "validation_detalhe.png")
    feitos["validation_detalhe"] = True

    # arvore do modelo, sozinha
    tree_dock = win._tree_dock
    tree_dock.setVisible(True)
    tree_dock.raise_()
    _captura(app, tree_dock, img_dir / "model_tree.png")
    feitos["model_tree"] = True

    # tema claro: existe e quase ninguem descobre
    try:
        atual = None
        from bolt_analysis_studio.gui.theme import Theme
        atual = Theme._current
        win._apply_theme("light")
        win.switch_module("Model")
        _captura(app, win, img_dir / "tema_claro.png")
        feitos["tema_claro"] = True
    except Exception as exc:                                 # noqa: BLE001
        print(f"  [aviso] tema claro: {exc}")
    finally:
        if atual:
            win._apply_theme(atual)
            for _ in range(20):
                app.processEvents()

    # dialogos, grabados direto (exec() bloquearia o build)
    from bolt_analysis_studio.gui.chrome.widgets.case_picker import CasePicker
    dlg = CasePicker()
    dlg.resize(900, 620)
    dlg.show()
    _captura(app, dlg, img_dir / "dialog_case_picker.png")
    dlg.close()
    feitos["dialog_case_picker"] = True

    from bolt_analysis_studio.gui.chrome.widgets.reference_curve import (
        ReferenceSourceDialog, curva_do_caso)
    src = ReferenceSourceDialog(None, CASO)
    src.resize(560, 300)
    src.show()
    _captura(app, src, img_dir / "dialog_reference_source.png")
    src.close()
    feitos["dialog_reference_source"] = True

    ref = curva_do_caso(CASO, float(st.model.global_loading.F_preload))
    if ref is not None:
        from bolt_analysis_studio.gui.main_window import CalibrationDialog
        cal = CalibrationDialog(None, st.model, ref)
        cal.resize(1400, 820)
        cal.show()
        _captura(app, cal, img_dir / "dialog_calibrate.png")
        cal.close()
        feitos["dialog_calibrate"] = True

    # as CINCO paginas do assistente, e nao so' a primeira
    from bolt_analysis_studio.gui.new_analysis_wizard import NewAnalysisWizard
    wiz = NewAnalysisWizard(None)
    wiz.show()
    for n in range(1, 6):
        _captura(app, wiz, img_dir / f"wizard_p{n}.png")
        feitos[f"wizard_p{n}"] = True
        if n < 5:
            wiz.next()
            for _ in range(20):
                app.processEvents()
    wiz.close()

    from bolt_analysis_studio.gui.documentation_tab import DocumentationTab
    doc = DocumentationTab()
    doc.resize(1180, 820)
    doc.show()
    doc._show_section("workflow")
    _captura(app, doc, img_dir / "documentation_tab.png")
    doc.close()
    feitos["documentation_tab"] = True

    win.close()
    for _ in range(10):
        app.processEvents()
    return feitos


# --------------------------------------------------------------------------
# voz
# --------------------------------------------------------------------------

def _hash_voz(voz: str, texto: str) -> str:
    return hashlib.sha1((voz + "\n" + texto).encode("utf-8")).hexdigest()[:16]


def sintetizar(passos, lang: str, audio_dir: Path) -> dict:
    """Um .mp3 por passo, com cache por hash. Devolve {chave: nome_do_mp3}."""
    import asyncio
    try:
        import edge_tts
    except ImportError:
        print("  [aviso] edge-tts nao instalado: paginas sem audio "
              "(py -3.12 -m pip install edge-tts)")
        return {}

    audio_dir.mkdir(parents=True, exist_ok=True)
    cache_path = audio_dir / "_cache.json"
    cache = {}
    if cache_path.is_file():
        try:
            cache = json.loads(cache_path.read_text(encoding="utf-8"))
        except ValueError:
            cache = {}
    voz = VOZES[lang]
    idx = 0 if lang == "pt" else 1
    saida = {}

    async def _um(chave: str, texto: str, alvo: Path) -> None:
        await edge_tts.Communicate(texto, voz).save(str(alvo))

    novos = 0
    for p in passos:
        texto = p["narracao"][idx]
        h = _hash_voz(voz, texto)
        alvo = audio_dir / f"{p['chave']}.mp3"
        if cache.get(p["chave"]) == h and alvo.is_file():
            saida[p["chave"]] = alvo.name
            continue
        try:
            asyncio.run(_um(p["chave"], texto, alvo))
        except Exception as exc:                             # noqa: BLE001
            print(f"  [aviso] sem audio para {p['chave']}: {exc}")
            continue
        cache[p["chave"]] = h
        saida[p["chave"]] = alvo.name
        novos += 1
    cache_path.write_text(json.dumps(cache, indent=1), encoding="utf-8")
    print(f"  audio {lang}: {len(saida)} paginas, {novos} sintetizadas agora, "
          f"voz {voz}")
    return saida


# --------------------------------------------------------------------------
# html
# --------------------------------------------------------------------------

_CSS = """
:root{--ink:#1f2937;--sub:#6b7280;--line:#e5e7eb;--bg:#fafafa;--card:#fff;
--acc:#2b6cb0;--warn:#b7791f}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);
font:16px/1.6 system-ui,Segoe UI,Roboto,sans-serif}
.wrap{max-width:1100px;margin:0 auto;padding:28px 22px 60px}
nav.top{display:flex;gap:14px;align-items:center;font-size:14px;color:var(--sub);
flex-wrap:wrap}nav.top a{color:var(--acc);text-decoration:none}
h1{font-size:30px;margin:14px 0 4px}h2{font-size:21px;margin:30px 0 10px}
.sub{color:var(--sub);margin:0 0 18px}
.print{border:1px solid var(--line);border-radius:8px;background:var(--card);
padding:6px;margin:14px 0}.print img{display:block;max-width:100%;height:auto;
border-radius:4px}
.print figcaption{padding:9px 10px 4px;color:var(--sub);font-size:14px;
line-height:1.5}
figure.print{margin:14px 0}
.player{display:flex;gap:14px;align-items:center;background:var(--card);
border:1px solid var(--line);border-radius:8px;padding:12px 16px;margin:14px 0}
.player audio{flex:1;min-width:240px}.player .voz{font-size:13px;color:var(--sub)}
.transcricao{background:var(--card);border-left:4px solid var(--acc);
padding:14px 18px;border-radius:0 8px 8px 0;margin:14px 0}
table.ctl{width:100%;border-collapse:collapse;background:var(--card);
border:1px solid var(--line);border-radius:8px;overflow:hidden;margin:14px 0}
table.ctl th,table.ctl td{padding:10px 12px;border-bottom:1px solid var(--line);
vertical-align:top;text-align:left}table.ctl th{background:#f3f4f6;font-size:13px;
text-transform:uppercase;letter-spacing:.04em;color:var(--sub)}
table.ctl td:first-child{white-space:nowrap;font-weight:600;width:30%}
table.ctl td:nth-child(2):not(:last-child){color:var(--sub);white-space:nowrap}
.erro{border:1px solid #f3d9a4;background:#fff8e6;border-radius:8px;padding:12px 16px;
margin:14px 0}.erro b{color:var(--warn)}
.pager{display:flex;justify-content:space-between;margin-top:34px;gap:12px}
.pager a{color:var(--acc);text-decoration:none;font-weight:600}
.cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));
gap:16px;margin-top:18px}.card{background:var(--card);border:1px solid var(--line);
border-radius:10px;overflow:hidden;text-decoration:none;color:inherit;display:block}
.card img{width:100%;height:170px;object-fit:cover;object-position:top;
border-bottom:1px solid var(--line)}.card .t{padding:12px 14px;font-weight:600}
.card .n{color:var(--sub);font-size:13px;padding:0 14px 12px}
@media(max-width:700px){table.ctl td:first-child{white-space:normal;width:auto}}
"""

_T = {
    "pt": dict(guia="Guia de uso narrado", inicio="Sumário", ouvir="Ouça a narração",
               voz="voz", transcricao="Transcrição", controles="Cada controle desta tela",
               controle="Controle", oque="O que faz", erro="Erro comum",
               anterior="← Anterior", proximo="Próximo →", outro="English version",
               intro=("Um passo por aba do programa. Cada página tem o print da tela "
                      "neste build, a narração em áudio, a transcrição e uma tabela "
                      "com cada botão e cada variável que aparece ali."),
               passo="Passo", semaudio="Áudio não gerado neste build.",
               glossario="Glossário", termo="Termo", equivalente="Em inglês",
               definicao="Definição",
               glossario_intro=("Os termos técnicos usados neste guia, no programa e no "
                                "artigo, com o equivalente em inglês. Os nomes dos módulos "
                                "e dos botões Run, Stop e Step ficam em inglês nas duas "
                                "línguas: são nomes próprios da interface, como no Abaqus.")),
    "en": dict(guia="Narrated user guide", inicio="Contents", ouvir="Listen to the narration",
               voz="voice", transcricao="Transcript", controles="Every control on this screen",
               controle="Control", oque="What it does", erro="Common mistake",
               anterior="← Previous", proximo="Next →", outro="Versão em português",
               intro=("One step per tab of the program. Each page has the screenshot "
                      "from this build, the audio narration, the transcript and a "
                      "table with every button and every variable that appears there."),
               passo="Step", semaudio="Audio not generated in this build.",
               glossario="Glossary", termo="Term", equivalente="In Portuguese",
               definicao="Definition",
               glossario_intro=("The technical terms used in this guide, in the program "
                                "and in the paper, with their Portuguese equivalent. Module "
                                "names and the Run, Stop and Step buttons stay in English in "
                                "both languages: they are proper names of the interface, as "
                                "in Abaqus.")),
}


def imagens_do(passo: dict):
    """Lista [(chave_da_captura, legenda_ou_None)] do passo.

    Um passo simples traz `print_="chrome_model"`; um passo que ensina traz
    `prints=[(chave, (legenda_pt, legenda_en)), ...]` — varias imagens sobre o
    mesmo tema, cada uma com a sua legenda, que e' o que o pedido de 2026-09-05
    exige para as licoes de modelagem e de consulta a validacao."""
    if passo.get("prints"):
        return [(ch, leg) for ch, leg in passo["prints"]]
    return [(passo["print_"], None)]


def nome_no_idioma(nome, idx: int) -> str:
    """Nome de controle: str quando o rotulo e' o mesmo nas duas linguas
    (rotulos ingleses fixos do inspector), (pt, en) quando a tela traduz."""
    return nome if isinstance(nome, str) else nome[idx]


def _pagina(lang: str, p: dict, i: int, n: int, passos, audio: dict) -> str:
    idx = 0 if lang == "pt" else 1
    T = _T[lang]
    outro = "en" if lang == "pt" else "pt"
    e = html.escape
    titulo = p["titulo"][idx]
    ant = passos[i - 1]["chave"] if i > 0 else None
    prx = passos[i + 1]["chave"] if i + 1 < n else None

    linhas = "".join(
        f"<tr><td>{e(nome_no_idioma(nome, idx))}</td><td>{e(txt[idx])}</td></tr>"
        for nome, txt in p["controles"])
    player = (f'<div class="player"><audio controls preload="none" '
              f'src="audio/{audio[p["chave"]]}"></audio>'
              f'<span class="voz">{e(T["ouvir"])} · {e(T["voz"])}: '
              f'{e(VOZES[lang])}</span></div>'
              if p["chave"] in audio else
              f'<div class="player"><span class="voz">{e(T["semaudio"])}</span></div>')
    figuras = "".join(
        f'<figure class="print"><img src="img/{ch}.png" alt="{e(titulo)}">'
        + (f"<figcaption>{e(leg[idx])}</figcaption>" if leg else "")
        + "</figure>"
        for ch, leg in imagens_do(p))
    erro = ""
    if p.get("erro_comum"):
        erro = (f'<div class="erro"><b>{e(T["erro"])}.</b> '
                f'{e(p["erro_comum"][idx])}</div>')
    return f"""<!doctype html><html lang="{lang}"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(titulo)} — Bolt Analysis Studio</title><style>{_CSS}</style></head>
<body><div class="wrap">
<nav class="top"><a href="index.html">{e(T["inicio"])}</a> · {e(T["passo"])} {i+1}/{n}
 · <a href="glossario.html">{e(T["glossario"])}</a>
 · <a href="../{outro}/{p['chave']}.html">{e(T["outro"])}</a></nav>
<h1>{e(titulo)}</h1>
<p class="sub">Bolt Analysis Studio 1.0.0 · {e(T["guia"])}</p>
{player}
{figuras}
<h2>{e(T["transcricao"])}</h2>
<div class="transcricao">{e(p["narracao"][idx])}</div>
<h2>{e(T["controles"])}</h2>
<table class="ctl"><thead><tr><th>{e(T["controle"])}</th><th>{e(T["oque"])}</th></tr></thead>
<tbody>{linhas}</tbody></table>
{erro}
<div class="pager"><span>{f'<a href="{ant}.html">{e(T["anterior"])}</a>' if ant else ''}</span>
<span>{f'<a href="{prx}.html">{e(T["proximo"])}</a>' if prx else ''}</span></div>
</div></body></html>"""


def _indice(lang: str, passos, audio: dict) -> str:
    idx = 0 if lang == "pt" else 1
    T = _T[lang]
    outro = "en" if lang == "pt" else "pt"
    e = html.escape
    cards = "".join(
        f'<a class="card" href="{p["chave"]}.html">'
        f'<img src="img/{imagens_do(p)[0][0]}.png" alt="">'
        f'<div class="t">{i+1}. {e(p["titulo"][idx])}</div>'
        f'<div class="n">{len(p["controles"])} {e("controles" if lang=="pt" else "controls")}'
        f'{" · 🔊" if p["chave"] in audio else ""}</div></a>'
        for i, p in enumerate(passos))
    return f"""<!doctype html><html lang="{lang}"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(T["guia"])} — Bolt Analysis Studio</title><style>{_CSS}</style></head>
<body><div class="wrap">
<nav class="top"><a href="glossario.html">{e(T["glossario"])}</a>
 · <a href="../{outro}/index.html">{e(T["outro"])}</a></nav>
<h1>{e(T["guia"])}</h1>
<p class="sub">Bolt Analysis Studio 1.0.0 · {e(T["intro"])}</p>
<div class="cards">{cards}</div>
</div></body></html>"""


def _glossario(lang: str, glossario) -> str:
    """Tabela termo / equivalente / definicao, ordenada pelo termo do idioma."""
    idx = 0 if lang == "pt" else 1
    T = _T[lang]
    outro = "en" if lang == "pt" else "pt"
    e = html.escape
    linhas = "".join(
        f"<tr><td>{e(g[idx])}</td><td>{e(g[1 - idx])}</td><td>{e(g[2 + idx])}</td></tr>"
        for g in sorted(glossario, key=lambda g: g[idx].lower()))
    return f"""<!doctype html><html lang="{lang}"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(T["glossario"])} — Bolt Analysis Studio</title><style>{_CSS}</style></head>
<body><div class="wrap">
<nav class="top"><a href="index.html">{e(T["inicio"])}</a>
 · <a href="../{outro}/glossario.html">{e(T["outro"])}</a></nav>
<h1>{e(T["glossario"])}</h1>
<p class="sub">Bolt Analysis Studio 1.0.0 · {e(T["glossario_intro"])}</p>
<table class="ctl"><thead><tr><th>{e(T["termo"])}</th><th>{e(T["equivalente"])}</th>
<th>{e(T["definicao"])}</th></tr></thead><tbody>{linhas}</tbody></table>
</div></body></html>"""


def _isola_preferencias() -> None:
    """A captura troca idioma e tema; nada disso pode ir para o preferences.json
    REAL de quem roda o build (em 2026-09-05 o build do guia deixou o programa
    do usuario em ingles). Aponta i18n — e, por ele, Theme — para um temporario
    e parte do portugues, para prints deterministicos."""
    import tempfile
    import bolt_analysis_studio.gui.i18n as i18n
    iso = Path(tempfile.mkdtemp(prefix="bas_prefs_"))
    i18n._PREFS_DIR, i18n._PREFS_FILE = iso, iso / "preferences.json"
    i18n.Lang.current = "pt"


# --------------------------------------------------------------------------
# main
# --------------------------------------------------------------------------

def main(argv=None) -> int:
    import argparse
    ap = argparse.ArgumentParser(description="Guia de uso narrado, um HTML por aba")
    ap.add_argument("--sem-audio", action="store_true", help="nao sintetiza voz")
    ap.add_argument("--so", choices=LINGUAS, help="gera so' um idioma")
    args = ap.parse_args(argv)
    _isola_preferencias()

    linguas = (args.so,) if args.so else LINGUAS
    for lang in linguas:
        pasta = SAIDA / lang
        (pasta / "img").mkdir(parents=True, exist_ok=True)
        feitos = capturar(lang, pasta / "img")
        pedidos = {ch for p in PASSOS for ch, _ in imagens_do(p)}
        faltam = sorted(pedidos - set(feitos))
        if faltam:
            raise SystemExit(f"[guia] {lang}: conteudo pede prints que o build nao "
                             f"tirou: {faltam}")
        audio = {} if args.sem_audio else sintetizar(PASSOS, lang, pasta / "audio")
        n = len(PASSOS)
        for i, p in enumerate(PASSOS):
            (pasta / f"{p['chave']}.html").write_text(
                _pagina(lang, p, i, n, PASSOS, audio), encoding="utf-8")
        (pasta / "index.html").write_text(_indice(lang, PASSOS, audio),
                                          encoding="utf-8")
        (pasta / "glossario.html").write_text(_glossario(lang, GLOSSARIO),
                                              encoding="utf-8")
        # paginas e audios orfaos de uma renumeracao anterior: sem isto o
        # indice aponta para 17 passos e a pasta guarda os 15 antigos ao lado
        vivos = {f"{p['chave']}.html" for p in PASSOS} | {"index.html",
                                                          "glossario.html"}
        for arq in pasta.glob("*.html"):
            if arq.name not in vivos:
                arq.unlink()
                print(f"  removido (renumeracao): {lang}/{arq.name}")
        mp3_vivos = {f"{p['chave']}.mp3" for p in PASSOS}
        for arq in (pasta / "audio").glob("*.mp3"):
            if arq.name not in mp3_vivos:
                arq.unlink()
        tam = sum(f.stat().st_size for f in pasta.rglob("*") if f.is_file())
        print(f"  {lang}: {n} paginas, {len(feitos)} prints, "
              f"{len(audio)} audios -> {pasta}  ({tam/1e6:.1f} MB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
