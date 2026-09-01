# -*- coding: utf-8 -*-
"""
Exporta as figuras de calibração/validação do BAS e capturas de tela da
interface, para uso na tese e no artigo.

Fontes de dados (somente leitura, nada é re-simulado por padrão):
  - Store canônica:  Models/CALIBRATION_AND_VALIDATION/validation_store.json
  - Registry:        bolt_analysis_studio.validation.case_registry
  - Livro-razão:     New_Theory/convergence_ledger.json

Uso:
    python scripts/export_thesis_figures.py                 # tudo
    python scripts/export_thesis_figures.py --no-gui        # só gráficos
    python scripts/export_thesis_figures.py --no-plots      # só screenshots
    python scripts/export_thesis_figures.py --sources LIU_2016,LIU_2022_RETIGHT
    python scripts/export_thesis_figures.py --out "D:\\figs" --dpi 300 --pdf
    python scripts/export_thesis_figures.py --load jiang_1.msd  # popula o builder
    python scripts/export_thesis_figures.py --show              # tela real (canvas
                                                                # renderizado c/ modelo)

Saída (default): C:/Users/leo_r/OneDrive/Mestrado/Doutorado_Buiatti/figuras/
    graficos/     curvas modelo × dado, decomposição, agregados
    screenshots/  janela principal (todas as abas) + MSD Builder
    manifest.txt  lista do que foi gerado + fingerprint do motor

Notas sobre a captura da GUI:
  - Renderização offscreen por padrão (nenhuma janela pisca na tela); usa
    C:/Windows/Fonts e fonte Arial para os textos saírem legíveis.
  - O canvas do MSD Builder pode aparecer vazio em modo offscreen (o modelo
    é carregado no app_state, mas o enquadramento/"Fit to View" do desenho
    depende do backend de tela). Para uma captura com o esquemático desenhado,
    rode com --show (usa a tela real) e/ou --load de um .msd.
  - --v2 (chrome estilo Abaqus) é experimental: a construção da janela pode
    bloquear; use apenas interativamente.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import sys
import traceback
from datetime import datetime
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

import matplotlib
matplotlib.use("Agg")                         # gráficos sem GUI
import matplotlib.pyplot as plt

DEFAULT_OUT = Path(r"C:\Users\leo_r\OneDrive\Mestrado\Doutorado_Buiatti\figuras")

# fontes-chave para as figuras da tese (grades por grupo)
# ⚠️ `UFU_LAB` SAIU desta lista em 2026-08-25: a fonte saiu do projeto em
# 2026-08-01 (decisao do professor). As 3 curvas seguem no store por
# preservacao e sao **0 comparaveis pelo censo** — publicar figura delas num
# artigo seria erro material. Preservar no store nao e' publicar.
DEFAULT_SOURCES = ["LIU_2016", "LIU_2022_RETIGHT", "LIU_2017_AXIAL",
                   "LI_2022_MARSTRUC", "LI_2022_TRIBOINT", "KARLSEN_2022"]

MECH_LABELS = {
    "embedding": "Embutimento",
    "creep": "Fluência",
    "wear": "Desgaste",
    "rotational_loosening": "Afrouxamento rotacional",
    "thread_fretting": "Fretting de flanco",
    "fatigue": "Fadiga",
}

plt.rcParams.update({
    "font.family": "serif",
    "font.size": 10,
    "axes.grid": True,
    "grid.alpha": 0.3,
    # autolayout desligado: usamos constrained_layout por figura, que
    # posiciona o suptitle sem colidir com os subtítulos dos painéis
    "figure.autolayout": False,
})


# ---------------------------------------------------------------- dados

def load_store() -> dict:
    p = REPO / "Models/CALIBRATION_AND_VALIDATION/validation_store.json"
    return json.loads(p.read_text(encoding="utf-8"))


def load_ledger() -> list:
    p = REPO / "New_Theory/convergence_ledger.json"
    return json.loads(p.read_text(encoding="utf-8"))


def read_reference_curve(rec) -> tuple[list, list] | None:
    """Curva experimental do caso: galeria (se houver) ou CSV bruto."""
    e = rec.gallery_entry
    if e and "data" in e:
        return ([float(x) for x in e["data"]["x"]],
                [float(y) for y in e["data"]["y"]])
    if not rec.csv_path or not Path(rec.csv_path).exists():
        return None
    xs, ys = [], []
    with open(rec.csv_path, encoding="utf-8-sig", newline="") as f:
        for row in csv.reader(f):
            if len(row) < 2:
                continue
            try:
                vals = [float(c) for c in row[:3]]
            except ValueError:
                continue                      # cabeçalho
            xs.append(vals[0])
            ys.append(vals[2] if len(vals) >= 3 else vals[1])
    if not xs:
        return None
    if max(ys) > 1.5:                          # normaliza F -> F/F0
        y0 = ys[0] if ys[0] else max(ys)
        ys = [y / y0 for y in ys]
    return xs, ys


def savefig(fig, out: Path, name: str, dpi: int, pdf: bool, manifest: list):
    out.mkdir(parents=True, exist_ok=True)
    png = out / f"{name}.png"
    fig.savefig(png, dpi=dpi, bbox_inches="tight")
    manifest.append(str(png))
    if pdf:
        fig.savefig(out / f"{name}.pdf", bbox_inches="tight")
        manifest.append(str(out / f"{name}.pdf"))
    plt.close(fig)
    print(f"  [fig] {png.name}")


# ---------------------------------------------------------------- gráficos

def fig_model_vs_data_grid(records, store, source: str, out: Path,
                           dpi: int, pdf: bool, manifest: list):
    recs = [r for r in records if r.source == source
            and store.get(r.case_id, {}).get("ok")]
    if not recs:
        print(f"  [aviso] fonte sem casos na store: {source}")
        return
    n = len(recs)
    ncols = min(3, n)
    nrows = (n + ncols - 1) // ncols
    fig, axes = plt.subplots(nrows, ncols,
                             figsize=(4.2 * ncols, 3.2 * nrows),
                             squeeze=False, layout="constrained")
    for ax in axes.flat[n:]:
        ax.set_visible(False)
    for ax, rec in zip(axes.flat, recs):
        res = store[rec.case_id]
        ref = read_reference_curve(rec)
        if ref:
            ax.plot(ref[0], ref[1], "o", ms=2.5, color="#555555",
                    label="Experimento", zorder=2)
        ax.plot(res["cycles"], res["ratio"], "-", lw=1.6, color="#b02a2a",
                label="Modelo (BAS)", zorder=3)
        ax.set_title(f"{rec.case_id}\nMAE = {res['mae']:.3f}", fontsize=8)
        ax.set_xlabel("Ciclos")
        ax.set_ylabel("F/F₀")
        ax.legend(fontsize=7, loc="best")
    fig.suptitle(f"Modelo × experimento — {source}", fontsize=11)
    savefig(fig, out, f"fig_grupo_{source.lower()}", dpi, pdf, manifest)


def fig_decomposition(records, store, case_id: str, out: Path,
                      dpi: int, pdf: bool, manifest: list):
    res = store.get(case_id)
    if not res or not res.get("decomp"):
        print(f"  [aviso] sem decomposição na store: {case_id}")
        return
    cycles = res["cycles"]
    ratio = res["ratio"]
    decomp = {k: v for k, v in res["decomp"].items()
              if v and max(abs(x) for x in v) > 0}
    if not decomp:
        print(f"  [aviso] decomposição vazia: {case_id}")
        return
    # normaliza para F/F0: a soma das parcelas finais == perda total final
    total_final = sum(v[-1] for v in decomp.values())
    loss_final = 1.0 - ratio[-1]
    scale = (loss_final / total_final) if total_final else 0.0
    n = min(len(cycles), *(len(v) for v in decomp.values()))
    series = [[x * scale for x in v[:n]] for v in decomp.values()]
    labels = [MECH_LABELS.get(k, k) for k in decomp]

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(6.4, 6.4), sharex=True,
                                   layout="constrained")
    rec = next((r for r in records if r.case_id == case_id), None)
    ref = read_reference_curve(rec) if rec else None
    if ref:
        ax1.plot(ref[0], ref[1], "o", ms=2.5, color="#555555",
                 label="Experimento")
    ax1.plot(cycles, ratio, "-", lw=1.6, color="#b02a2a", label="Modelo (BAS)")
    ax1.set_ylabel("F/F₀")
    ax1.legend(fontsize=8)
    ax1.set_title(f"{case_id} — MAE = {res['mae']:.3f}", fontsize=10)

    ax2.stackplot(cycles[:n], *series, labels=labels, alpha=0.85)
    ax2.set_xlabel("Ciclos")
    ax2.set_ylabel("Perda acumulada (fração de F₀)")
    ax2.legend(fontsize=7, loc="upper left")
    savefig(fig, out, f"fig_decomposicao_{case_id}", dpi, pdf, manifest)


def fig_reference_set(records, store, out: Path, dpi: int, pdf: bool,  # noqa: E501
                      # ⚠️ APOSENTADA em 2026-08-25 — nao e mais chamada pelo
                      # main. Ela plota as condicoes de referencia da UFU_LAB, e
                      # a UFU saiu do projeto em 2026-08-01: as 3 curvas seguem
                      # no store por preservacao e sao 0 comparaveis pelo censo.
                      # Fica aqui como registro; se voltar a ser usada, confira
                      # antes se a fonte voltou ao escopo.
                      manifest: list):
    """Casos UFU (conjunto de calibração de referência) em um painel único."""
    recs = [r for r in records if r.source == "UFU_LAB"
            and store.get(r.case_id, {}).get("ok")]
    if not recs:
        return
    fig, ax = plt.subplots(figsize=(6.6, 4.4), layout="constrained")
    colors = plt.cm.tab10.colors
    for i, rec in enumerate(recs):
        res = store[rec.case_id]
        ref = read_reference_curve(rec)
        c = colors[i % len(colors)]
        if ref:
            ax.plot(ref[0], ref[1], "o", ms=2.5, color=c, alpha=0.5)
        ax.plot(res["cycles"], res["ratio"], "-", lw=1.8, color=c,
                label=f"{rec.case_id} (MAE {res['mae']:.3f})")
    ax.set_xlabel("Ciclos")
    ax.set_ylabel("F/F₀")
    ax.set_title("Conjunto de referência (bancada UFU): modelo × experimento")
    ax.legend(fontsize=8)
    savefig(fig, out, "fig_condicoes_referencia_ufu", dpi, pdf, manifest)


def fig_ledger(out: Path, dpi: int, pdf: bool, manifest: list):
    entries = load_ledger()
    canon = [e for e in entries if "canonico" in (e.get("basis") or "")]
    if not canon:
        canon = entries
    xs = list(range(1, len(canon) + 1))
    fig, ax1 = plt.subplots(figsize=(6.8, 4.2), layout="constrained")
    ax1.plot(xs, [e["mean"] for e in canon], "-o", ms=3, color="#b02a2a",
             label="Média")
    ax1.plot(xs, [e["median"] for e in canon], "-s", ms=3, color="#1f5fa8",
             label="Mediana")
    ax1.set_xlabel("Iteração da MEM (régua canônica)")
    ax1.set_ylabel("MAE em F/F₀")
    ax2 = ax1.twinx()
    ax2.bar(xs, [e.get("n_above_bound", 0) for e in canon], alpha=0.18,
            color="#444444", label="Casos > 0,10")
    ax2.set_ylabel("Casos com MAE > 0,10")
    ax2.grid(False)
    h1, l1 = ax1.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    ax1.legend(h1 + h2, l1 + l2, fontsize=8, loc="upper right")
    ax1.set_title("Convergência do modelo sobre a régua canônica")
    savefig(fig, out, "fig_convergencia_mem", dpi, pdf, manifest)


def fig_per_source_medians(out: Path, dpi: int, pdf: bool, manifest: list):
    entries = load_ledger()
    last = next((e for e in reversed(entries) if e.get("per_source")), None)
    if not last:
        return
    # ⚠️ DOIS formatos: `{fonte: float}` (atual) e `{fonte: {"median","n"}}`
    # (ate ~jul/2026). O codigo antigo assumia o segundo e estourava com
    # `TypeError: 'float' object is not subscriptable`.
    def _med(v):
        return float(v["median"]) if isinstance(v, dict) else float(v)

    def _n(v):
        return f" (n={v['n']})" if isinstance(v, dict) and "n" in v else ""

    items = sorted(last["per_source"].items(), key=lambda kv: _med(kv[1]))
    names = [f"{k}{_n(v)}" for k, v in items]
    meds = [_med(v) for k, v in items]
    # ⚠️ O limite vem de `META_MAE`, NUNCA de literal: a regua mudou em
    # 2026-07-29 e o MAE passou de 0,10 para 0,05. A versao anterior desenhava
    # 0,10 sob o titulo "regua canonica", o que faria toda fonte parecer folgada
    # — num artigo, erro material.
    import bolt_analysis_studio.validation.report_html as rh
    lim = rh.META_MAE
    fig, ax = plt.subplots(figsize=(6.8, 0.34 * len(items) + 1.6),
                           layout="constrained")
    ax.barh(names, meds, color="0.5")
    ax.axvline(lim, color="k", ls="--", lw=1.1,
               label=f"Limite do MAE = {lim:.3g}".replace(".", ","))
    ax.set_xlabel("Mediana do MAE em $F/F_0$")
    ax.set_title("Mediana de erro por fonte experimental "
                 "(régua vigente, 3 pernas)")
    ax.legend(fontsize=8)
    savefig(fig, out, "fig_medianas_por_fonte", dpi, pdf, manifest)


# ---------------------------------------------------------------- screenshots

_LOAD_MSD: Path | None = None       # definido em main() a partir de --load


def _maybe_load_model(win, app):
    """Carrega um .msd no app SEM abrir diálogos (via API, não pelo menu).
    Sem --load, deixa o builder vazio (captura da interface limpa)."""
    if _LOAD_MSD is None:
        return
    try:
        from bolt_analysis_studio.io.msd_io import load_msd_model  # type: ignore
        model = load_msd_model(str(_LOAD_MSD))
    except Exception:
        try:
            import json
            from bolt_analysis_studio.core.models.model import MSDModel
            model = MSDModel.from_dict(
                json.loads(Path(_LOAD_MSD).read_text(encoding="utf-8")))
        except Exception:
            print(f"  [aviso] não foi possível carregar {_LOAD_MSD}:")
            traceback.print_exc(limit=1)
            return
    # padrão da main_window: setar app_state.model; o _open_msd_builder() da
    # etapa 2 (grab_gui) faz o render — não chamamos aqui para evitar a
    # reentrância de clear_all() alertada no CLAUDE.md do repositório
    try:
        if hasattr(win, "app_state"):
            win.app_state.model = model
            for _ in range(6):
                app.processEvents()
            print(f"  [ok] modelo aplicado ao app_state: {_LOAD_MSD.name}")
            return
    except Exception:
        print(f"  [aviso] falha ao aplicar modelo {_LOAD_MSD.name}:")
        traceback.print_exc(limit=1)
        return
    print("  [aviso] janela sem app_state; modelo não aplicado")


def grab_gui(out: Path, manifest: list, show: bool = False,
             include_v2: bool = False):
    """Captura a janela principal (todas as abas), o MSD Builder e o chrome V2.
    Renderização offscreen por padrão (nenhuma janela pisca na tela)."""
    if not show:
        os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
        # o plugin offscreen não acha as fontes do Qt no Windows — sem isto,
        # as capturas sairiam sem nenhum texto renderizado
        os.environ.setdefault("QT_QPA_FONTDIR", r"C:\Windows\Fonts")
    from PyQt6.QtWidgets import QApplication, QTabWidget, QMainWindow
    from PyQt6.QtGui import QFont
    out.mkdir(parents=True, exist_ok=True)
    app = QApplication.instance() or QApplication(sys.argv[:1])
    if not show:
        # offscreen: fixa uma família com cobertura completa de glifos
        # (a resolução default pode cair numa fonte incompleta)
        app.setFont(QFont("Arial", 9))

    def snap(widget, name):
        widget.resize(1600, 950)
        widget.show()
        for _ in range(6):
            app.processEvents()
        pix = widget.grab()
        p = out / f"{name}.png"
        pix.save(str(p))
        manifest.append(str(p))
        print(f"  [img] {p.name}")

    # 1) janela principal V1 (7 abas)
    try:
        import bolt_analysis_studio.gui.main_window as mw_mod
        # classe de janela DEFINIDA no módulo (não os QMainWindow importados)
        cls = next(c for n, c in vars(mw_mod).items()
                   if isinstance(c, type) and issubclass(c, QMainWindow)
                   and c is not QMainWindow
                   and getattr(c, "__module__", "") == mw_mod.__name__)
        win = cls()
        win.resize(1600, 950)
        win.show()
        for _ in range(10):
            app.processEvents()
        # Nota: aplicar um Quick Preset por clique programático abre um
        # diálogo modal (wizard) que bloqueia em modo offscreen; para popular
        # o canvas, abra o app com --show e carregue um modelo manualmente
        # antes de capturar, ou passe um .msd por --load (ver README do script).
        _maybe_load_model(win, app)
        tabs = win.findChild(QTabWidget)
        if tabs is not None:
            for i in range(tabs.count()):
                tabs.setCurrentIndex(i)
                for _ in range(6):
                    app.processEvents()
                label = tabs.tabText(i) or f"aba{i}"
                safe = "".join(ch if ch.isalnum() else "_"
                               for ch in label.lower()).strip("_")
                snap(win, f"bas_v1_aba{i}_{safe}")
        else:
            snap(win, "bas_v1_janela_principal")
        # 2) MSD Builder (janela flutuante)
        try:
            if hasattr(win, "_open_msd_builder"):
                win._open_msd_builder()
                for _ in range(10):
                    app.processEvents()
                b = getattr(win, "msd_builder_window", None)
                if b is not None:
                    snap(b, "bas_msd_builder")
        except Exception:
            print("  [aviso] MSD Builder não capturado:")
            traceback.print_exc(limit=1)
        # sem win.close(): closeEvent pode abrir diálogo modal e travar o
        # processo offscreen; o interpretador encerra tudo ao final
    except Exception:
        print("  [aviso] janela principal V1 não capturada:")
        traceback.print_exc(limit=1)

    # 3) chrome V2 (Abaqus-style) — opt-in: frontend em desenvolvimento,
    # a construção pode bloquear; use --v2 para tentar capturar
    if include_v2:
        try:
            from bolt_analysis_studio.gui.chrome.app_window import ChromeWindow
            w2 = ChromeWindow()
            snap(w2, "bas_v2_chrome")
        except Exception:
            print("  [aviso] chrome V2 não capturado (ok):")
            traceback.print_exc(limit=1)


# ---------------------------------------------------------------- main



# ==================================================================== #
# FIGURAS DO ARTIGO (2026-08-25) — as 8 que faltavam                   #
#                                                                      #
# Plano e justificativa de cada uma: `New_Theory/figuras_para_o_artigo.md`.
# Todas leem o store canonico; nenhuma re-simula. O censo passa SEMPRE
# por `caso_comparavel`, o filtro unico — contar por fora ja produziu
# dois censos discordantes na mesma arvore (medido 2026-08-25).
# ==================================================================== #

def _comparaveis(records, store):
    """(records comparaveis, results, pisos) — o universo do censo."""
    import bolt_analysis_studio.validation.report_html as rh
    from bolt_analysis_studio.validation.runner import CaseResult
    recs = store.get("cases", store)
    comp = [r for r in records
            if r.case_id in recs and rh.caso_comparavel(r.source, r.case_id)]
    res = {}
    for r in comp:
        try:
            res[r.case_id] = CaseResult.from_dict(recs[r.case_id])
        except Exception:
            pass
    pisos = rh._pisos_medidos([(r.source, res[r.case_id]) for r in comp
                               if r.case_id in res])
    return comp, res, pisos


def fig_paridade(records, store, out: Path, dpi: int, pdf: bool, manifest: list):
    """Fig. 6 — previsto x observado, com a reta 1:1 e o quadrante perigoso."""
    import bolt_analysis_studio.validation.report_html as rh
    comp, res, pisos = _comparaveis(records, store)
    O, M, perigo = [], [], []
    for r in comp:
        rr = res.get(r.case_id)
        if rr is None or not (rr.metric_data and rr.metric_pred):
            continue
        o, p = float(rr.metric_data[-1]), float(rr.metric_pred[-1])
        O.append(o)
        M.append(p)
        perigo.append(o < 0.85 <= p)
    if not O:
        return
    import numpy as np
    O = np.array(O)
    M = np.array(M)
    perigo = np.array(perigo)
    b = M - O
    r2 = 1 - float(np.sum(b ** 2) / np.sum((O - O.mean()) ** 2))
    fig, ax = plt.subplots(figsize=(4.4, 4.2), constrained_layout=True)
    ax.axhspan(0.85, 1.02, xmin=0, xmax=0.85 / 1.02, color="0.85", zorder=0)
    ax.plot([0, 1], [0, 1], "k-", lw=1.2, label="1:1")
    for d, ls in ((0.05, "--"), (0.10, ":")):
        ax.plot([0, 1 - d], [d, 1], "k" + ls, lw=0.7)
        ax.plot([d, 1], [0, 1 - d], "k" + ls, lw=0.7)
    ax.scatter(O[~perigo], M[~perigo], s=14, c="0.35", alpha=.65, lw=0,
               label="205 curvas")
    ax.scatter(O[perigo], M[perigo], s=34, facecolors="none", edgecolors="k",
               lw=1.3, label="falso seguro (ISO 16130)")
    ax.axvline(0.85, color="k", lw=0.6, alpha=.5)
    ax.axhline(0.85, color="k", lw=0.6, alpha=.5)
    ax.set_xlim(0, 1.02)
    ax.set_ylim(0, 1.02)
    ax.set_xlabel("Retenção observada, $F/F_0$ (fim do ensaio)")
    ax.set_ylabel("Retenção prevista, $F/F_0$")
    ax.set_title(f"$R^2$ = {r2:.4f} · viés = {b.mean():+.4f} · "
                 f"{100*np.mean(np.abs(b)<=0.05):.0f}% em ±0,05", fontsize=9)
    ax.legend(fontsize=7.5, loc="lower right", framealpha=.9)
    savefig(fig, out, "fig_paridade", dpi, pdf, manifest)


def fig_decisao(records, store, out: Path, dpi: int, pdf: bool, manifest: list):
    """Fig. 8 — a decisao de engenharia e os falsos seguros nomeados."""
    import numpy as np
    comp, res, pisos = _comparaveis(records, store)
    O, M, ids, src = [], [], [], []
    for r in comp:
        rr = res.get(r.case_id)
        if rr is None or not (rr.metric_data and rr.metric_pred):
            continue
        O.append(float(rr.metric_data[-1]))
        M.append(float(rr.metric_pred[-1]))
        ids.append(r.case_id)
        src.append(r.source)
    O = np.array(O)
    M = np.array(M)
    fig, axes = plt.subplots(1, 2, figsize=(6.6, 3.0), constrained_layout=True)
    for ax, (lim, norma) in zip(axes, ((0.85, "ISO 16130"),
                                       (0.80, "DIN 25201-4"))):
        vp = int(np.sum((O < lim) & (M < lim)))
        vn = int(np.sum((O >= lim) & (M >= lim)))
        fa = int(np.sum((O >= lim) & (M < lim)))
        fs = int(np.sum((O < lim) & (M >= lim)))
        mat = np.array([[vn, fa], [fs, vp]], float)
        ax.imshow(mat, cmap="Greys", vmin=0, vmax=mat.max() * 1.35)
        for i in range(2):
            for j in range(2):
                peri = (i == 1 and j == 0)
                ax.text(j, i, f"{int(mat[i, j])}", ha="center", va="center",
                        fontsize=13 if peri else 11,
                        fontweight="bold" if peri else "normal",
                        color="k")
                if peri:
                    ax.add_patch(plt.Rectangle((j - .5, i - .5), 1, 1,
                                               fill=False, ec="k", lw=2.2))
        ax.set_xticks([0, 1])
        ax.set_yticks([0, 1])
        ax.set_xticklabels(["retém", "afrouxa"], fontsize=8)
        ax.set_yticklabels(["retém", "afrouxa"], fontsize=8)
        ax.set_xlabel("previsto pelo modelo", fontsize=8.5)
        ax.set_ylabel("medido no ensaio", fontsize=8.5)
        ax.set_title(f"{norma} — limiar {lim:.0%}\nacerto "
                     f"{(vp+vn)/len(O):.1%} · falso seguro {fs}", fontsize=8.5)
        ax.grid(False)
    savefig(fig, out, "fig_decisao_iso_din", dpi, pdf, manifest)

    # painel companheiro: os falsos seguros, nomeados
    import bolt_analysis_studio.validation.report_html as rh
    fs_i = [i for i in range(len(O)) if O[i] < 0.85 <= M[i]]
    if not fs_i:
        return
    fs_i.sort(key=lambda i: M[i] - O[i], reverse=True)
    fig, ax = plt.subplots(figsize=(6.6, 0.42 * len(fs_i) + 1.1),
                           constrained_layout=True)
    y = np.arange(len(fs_i))
    ax.barh(y, [M[i] - O[i] for i in fs_i], color="0.55", height=.6)
    for k, i in enumerate(fs_i):
        rr = res[ids[i]]
        ok = rh._tripe_ok(rr, rh.limite_sres(src[i], pisos))
        ax.text(M[i] - O[i] + .004, k,
                f"{O[i]:.3f}→{M[i]:.3f}" + ("  (no tripé)" if ok else ""),
                va="center", fontsize=7.5,
                fontweight="bold" if ok else "normal")
    ax.set_yticks(y)
    ax.set_yticklabels([ids[i][:38] for i in fs_i], fontsize=7)
    ax.invert_yaxis()
    ax.set_xlabel("sobrestimação da retenção (previsto − observado)")
    ax.set_title("Falsos seguros no limiar da ISO 16130 — em negrito, "
                 "os aprovados pelo critério", fontsize=8.5)
    ax.grid(axis="x", alpha=.3)
    savefig(fig, out, "fig_falsos_seguros", dpi, pdf, manifest)


def fig_envelope(records, store, out: Path, dpi: int, pdf: bool, manifest: list):
    """Fig. 7 — onde o corpus vive, e onde nao ha dado."""
    import bolt_analysis_studio.validation.report_html as rh
    comp, res, pisos = _comparaveis(records, store)
    A, F, D, Q, OK = [], [], [], [], []
    for r in comp:
        rr = res.get(r.case_id)
        if rr is None:
            continue
        vc = r.validation_case
        A.append(float(getattr(vc, "transverse_displacement_mm", 0) or 0))
        F.append(float(getattr(vc, "initial_preload_N", 0) or 0) / 1000)
        D.append(float(getattr(vc, "bolt_diameter_mm", 0) or 0))
        Q.append(float(getattr(vc, "frequency_Hz", 0) or 0))
        OK.append(bool(rh._tripe_ok(rr, rh.limite_sres(r.source, pisos))))
    import numpy as np
    A, F, D, Q = map(np.array, (A, F, D, Q))
    OK = np.array(OK)
    fig, axes = plt.subplots(1, 2, figsize=(6.8, 3.1), constrained_layout=True)
    for ax, (x, y, xl, yl, m) in zip(axes, (
            (A, F, "Amplitude transversal [mm]", "Pré-carga $F_0$ [kN]", A > 0),
            (D, Q, "Diâmetro do parafuso [mm]", "Frequência [Hz]", Q > 0))):
        ax.scatter(x[m & OK], y[m & OK], s=15, c="0.3", alpha=.6, lw=0,
                   label="no tripé")
        ax.scatter(x[m & ~OK], y[m & ~OK], s=22, facecolors="none",
                   edgecolors="0.2", lw=.9, label="fora do tripé")
        ax.set_xscale("log")
        ax.set_yscale("log")
        ax.set_xlabel(xl)
        ax.set_ylabel(yl)
        ax.grid(alpha=.3, which="both")
        ax.legend(fontsize=7.5)
    fig.suptitle("Envelope de validade: um ponto por curva", fontsize=9.5)
    savefig(fig, out, "fig_envelope", dpi, pdf, manifest)


def fig_uma_fisica(records, store, out: Path, dpi: int, pdf: bool, manifest: list):
    """Fig. 5 (⭐) — mesmas constantes, comportamentos opostos."""
    import json as _json
    import numpy as np
    import bolt_analysis_studio.validation.runner as rn
    import bolt_analysis_studio.validation.report_html as rh
    from bolt_analysis_studio.calibration import knowledge_base as kb
    comp, res, pisos = _comparaveis(records, store)
    porid = {r.case_id: r for r in comp}

    def sig(cid):
        r = porid[cid]
        g = rn._adopted_for(r.source, cid,
                            getattr(r.validation_case, "bolt_size", "") or "")
        c = (kb.adopted_config(g) or {}).get("cfg") or {}
        eff = {k: v for k, v in c.items() if k != "per_case"}
        for tok, d in (c.get("per_case") or {}).items():
            if tok in cid and isinstance(d, dict):
                eff.update(d)
        return _json.dumps({k: str(v) for k, v in sorted(eff.items())},
                           sort_keys=True), eff

    fam = [c for c in porid if c.startswith("lu2024_M8_fig18_amp")
           and res.get(c) is not None and getattr(res[c], "metric_x", None)]
    if len(fam) < 3:
        return
    por = {}
    for c in fam:
        s, eff = sig(c)
        por.setdefault(s, []).append(c)
    # ⚠️ SO' o maior subconjunto com constantes IDENTICAS. A familia inteira NAO
    # compartilha, e afirmar o contrario seria o proprio defeito que a figura nega.
    fam = sorted(max(por.values(), key=len))
    if len(fam) < 2:
        return
    nk = sum(1 for v in sig(fam[0])[1].values()
             if isinstance(v, (int, float)) and not isinstance(v, bool))
    fora = sum(len(v) for v in por.values()) - len(fam)

    fig, axes = plt.subplots(1, 2, figsize=(6.8, 3.2), constrained_layout=True)
    ax = axes[0]
    marks = "os^Dv<>"
    for i, c in enumerate(sorted(fam, key=lambda q: -float(
            res[q].metric_data[-1]))):
        rr = res[c]
        amp = float(getattr(porid[c].validation_case,
                            "transverse_displacement_mm", 0) or 0)
        g = 0.15 + 0.6 * i / max(len(fam) - 1, 1)
        ax.plot(rr.metric_x, rr.metric_data, marks[i % len(marks)],
                ms=3.4, color=str(g), label=f"{amp:g} mm")
        ax.plot(rr.metric_x, rr.metric_pred, "-", lw=1.5, color=str(g))
    ax.set_xlabel("Ciclos")
    ax.set_ylabel("$F/F_0$")
    ax.set_title(f"(a) {len(fam)} amplitudes, {nk} constantes — as MESMAS",
                 fontsize=8.5)
    ax.legend(fontsize=7.5, title="amplitude", title_fontsize=7.5)
    ax.grid(alpha=.3)

    ax = axes[1]
    par = [c for c in ("rousseau2025_hdpe_t10", "rousseau2025_hdpe_t10_amp0p2")
           if c in porid and res.get(c) is not None]
    if len(par) == 2:
        for i, c in enumerate(par):
            rr = res[c]
            amp = float(getattr(porid[c].validation_case,
                                "transverse_displacement_mm", 0) or 0)
            g = "0.15" if i == 0 else "0.55"
            ax.plot(rr.metric_x, rr.metric_data, marks[i], ms=4, color=g,
                    label=f"{amp:g} mm (MAE {rr.mae:.4f})")
            ax.plot(rr.metric_x, rr.metric_pred, "-", lw=1.6, color=g)
        ax.set_xlabel("Ciclos")
        ax.set_ylabel("$F/F_0$")
        ax.set_title("(b) predição zero-refit: condição inédita,\nnenhuma "
                     "constante tocada", fontsize=8.5)
        ax.legend(fontsize=7.5)
        ax.grid(alpha=.3)
    nota = (f"  ({fora} curva(s) da mesma figura fora do painel (a): "
            f"constantes diferentes)" if fora else "")
    fig.suptitle("Uma física, vários comportamentos" + nota, fontsize=9.5)
    savefig(fig, out, "fig_uma_fisica", dpi, pdf, manifest)


def fig_custo_calibracao(records, store, out: Path, dpi: int, pdf: bool,
                         manifest: list):
    """Fig. 10 — curvas por constante, e a procedencia declarada."""
    import collections
    import numpy as np
    import bolt_analysis_studio.validation.runner as rn
    from bolt_analysis_studio.calibration import knowledge_base as kb
    comp, res, pisos = _comparaveis(records, store)
    ncur = collections.Counter()
    nk = collections.Counter()
    vistos = set()
    for r in comp:
        ncur[r.source] += 1
        g = rn._adopted_for(r.source, r.case_id,
                            getattr(r.validation_case, "bolt_size", "") or "")
        if not g or g in vistos:
            continue
        vistos.add(g)
        c = (kb.adopted_config(g) or {}).get("cfg") or {}
        n = sum(1 for k, v in c.items() if k != "per_case"
                and isinstance(v, (int, float)) and not isinstance(v, bool))
        n += sum(len(d) for d in (c.get("per_case") or {}).values()
                 if isinstance(d, dict))
        nk[r.source] += n
    fontes = [f for f in sorted(ncur) if nk.get(f)]
    razao = [ncur[f] / nk[f] for f in fontes]
    ordem = np.argsort(razao)[::-1]
    com, tot = 0, 0
    for s in kb.adopted_sources():
        e = kb.adopted_config(s) or {}
        prov = e.get("prov") or {}
        for _t, d in ((e.get("cfg") or {}).get("per_case") or {}).items():
            if isinstance(d, dict):
                for campo in d:
                    tot += 1
                    com += 1 if campo in prov else 0
    fig, axes = plt.subplots(1, 2, figsize=(6.9, 3.4), constrained_layout=True,
                             gridspec_kw={"width_ratios": [2.1, 1]})
    ax = axes[0]
    y = np.arange(len(fontes))
    ax.barh(y, [razao[i] for i in ordem], color="0.55", height=.66)
    ax.axvline(1.0, color="k", ls="--", lw=1.1)
    ax.set_yticks(y)
    ax.set_yticklabels([f"{fontes[i]} ({ncur[fontes[i]]}c/{nk[fontes[i]]}k)"
                        for i in ordem], fontsize=6.6)
    ax.invert_yaxis()
    ax.set_xlabel("Curvas por constante")
    ax.set_title("(a) quanto mais à direita, mais predição\ne menos ajuste",
                 fontsize=8.5)
    ax.grid(axis="x", alpha=.3)
    ax = axes[1]
    ax.bar([0], [com], color="0.35", label="com procedência")
    ax.bar([0], [tot - com], bottom=[com], color="0.8",
           label="sem procedência")
    ax.set_xticks([])
    ax.set_ylabel("Entradas por curva (`per_case`)")
    ax.set_title(f"(b) procedência declarada\n{com} de {tot} "
                 f"({100*com/max(tot,1):.0f}%)", fontsize=8.5)
    ax.legend(fontsize=7.5)
    ax.grid(axis="y", alpha=.3)
    savefig(fig, out, "fig_custo_calibracao", dpi, pdf, manifest)


def fig_cadeia_extracao(records, store, out: Path, dpi: int, pdf: bool,
                        manifest: list, ref: str = "liu2016wear_fig11a_af7p5kn",
                        ex_trim: str = "liu2016wear_fig7_run2_5e6cyc"):
    """Fig. 3 — a cadeia, em 4 paineis."""
    import numpy as np
    from bolt_analysis_studio.validation.inputs import load_full_curve
    comp, res, pisos = _comparaveis(records, store)
    porid = {r.case_id: r for r in comp}
    if ref not in porid or res.get(ref) is None:
        return
    rec, rr = porid[ref], res[ref]
    try:
        xc, yc = load_full_curve(rec.csv_path)
    except Exception:
        return
    xc = np.asarray(xc, float)
    yc = np.asarray(yc, float)
    mx = np.asarray(rr.metric_x, float)
    md = np.asarray(rr.metric_data, float)
    mp = np.asarray(rr.metric_pred, float)
    fig, ax = plt.subplots(2, 2, figsize=(6.8, 5.0), constrained_layout=True)
    a = ax[0][0]
    a.plot(xc, yc, "ko", ms=3.4)
    a.set_title(f"(a) digitalização — {len(xc)} pontos", fontsize=8.5)
    a.set_xlabel("x da CSV")
    a.set_ylabel("$F/F_0$")
    a.grid(alpha=.3)
    a = ax[0][1]
    if ex_trim in porid and res.get(ex_trim) is not None:
        rt = res[ex_trim]
        try:
            xt, yt = load_full_curve(porid[ex_trim].csv_path)
            xt = np.asarray(xt, float)
            yt = np.asarray(yt, float)
            mtx = np.asarray(rt.metric_x, float)
            dentro = xt <= mtx.max() + 1e-9
            a.plot(xt[~dentro], yt[~dentro], "o", ms=3.4, mfc="none",
                   mec="0.55")
            a.plot(xt[dentro], yt[dentro], "ko", ms=3.4)
            a.axhline(0.10, color="k", ls="--", lw=.9)
            a.set_title(f"(b) janela da métrica — {int(dentro.sum())} de "
                        f"{len(xt)} pontuados", fontsize=8.5)
        except Exception:
            pass
    a.set_xlabel("Ciclos")
    a.set_ylabel("$F/F_0$")
    a.grid(alpha=.3)
    a = ax[1][0]
    a.plot(mx, md, "ko", ms=3.6, label="dado")
    a.plot(mx, mp, "k-", lw=1.6, label="modelo")
    a.set_title("(c) o que a métrica compara", fontsize=8.5)
    a.set_xlabel("Ciclos")
    a.set_ylabel("$F/F_0$")
    a.legend(fontsize=7.5)
    a.grid(alpha=.3)
    a = ax[1][1]
    resid = mp - md
    a.plot(mx, resid, "ko-", ms=3.2, lw=.9)
    a.axhline(0, color="k", lw=.8)
    a.axhline(resid.max(), color="0.5", ls=":", lw=1)
    a.axhline(resid.min(), color="0.5", ls=":", lw=1)
    a.set_title(f"(d) resíduo — MAE {rr.mae:.4f}, "
                f"máx {rr.maxerr:.4f}", fontsize=8.5)
    a.set_xlabel("Ciclos")
    a.set_ylabel("modelo − dado")
    a.grid(alpha=.3)
    fig.suptitle(f"Cadeia de extração — {ref}", fontsize=9.5)
    savefig(fig, out, "fig_cadeia_extracao", dpi, pdf, manifest)


def fig_sensibilidade(out: Path, dpi: int, pdf: bool, manifest: list):
    """Opcional — tornado OAT por familia, com os inertes visiveis."""
    import numpy as np
    from bolt_analysis_studio.calibration import knowledge_base as kb
    fams = [("transverse", "transversal"), ("axial", "axial")]
    dados = []
    for fam, nome in fams:
        try:
            s = kb.sensitivity(fam)
        except Exception:
            s = None
        if s:
            dados.append((nome, sorted(((k, v.get("mean", 0.0),
                                         v.get("max", 0.0))
                                        for k, v in s.items()),
                                       key=lambda q: -q[1])))
    if not dados:
        return
    fig, axes = plt.subplots(1, len(dados),
                             figsize=(3.5 * len(dados), 3.6),
                             constrained_layout=True)
    if len(dados) == 1:
        axes = [axes]
    for ax, (nome, itens) in zip(axes, dados):
        y = np.arange(len(itens))
        ax.barh(y, [i[2] for i in itens], color="0.85", height=.72)
        ax.barh(y, [i[1] for i in itens], color="0.4", height=.72)
        ax.set_yticks(y)
        ax.set_yticklabels([i[0] for i in itens], fontsize=6.4)
        ax.invert_yaxis()
        n_in = sum(1 for i in itens if i[2] <= 1e-12)
        ax.set_title(f"{nome} — {len(itens)-n_in} com efeito, "
                     f"{n_in} inertes", fontsize=8.5)
        ax.set_xlabel("Efeito no $F/F_0$ (OAT)")
        ax.grid(axis="x", alpha=.3)
    fig.suptitle("Sensibilidade por parâmetro: barra escura = média, "
                 "clara = máximo", fontsize=9)
    savefig(fig, out, "fig_sensibilidade", dpi, pdf, manifest)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", default=str(DEFAULT_OUT))
    ap.add_argument("--dpi", type=int, default=300)
    ap.add_argument("--pdf", action="store_true",
                    help="salva também em PDF vetorial")
    ap.add_argument("--no-gui", action="store_true")
    ap.add_argument("--no-plots", action="store_true")
    ap.add_argument("--show", action="store_true",
                    help="usa a tela real (em vez de renderização offscreen)")
    ap.add_argument("--v2", action="store_true",
                    help="tenta capturar também o chrome V2 (experimental)")
    ap.add_argument("--sources", default=",".join(DEFAULT_SOURCES),
                    help="fontes para as grades modelo × dado (CSV)")
    ap.add_argument("--decomp-cases", default="",
                    help="case_ids extras para figuras de decomposição (CSV)")
    ap.add_argument("--load", default="",
                    help="caminho de um .msd para popular o builder na captura")
    args = ap.parse_args()

    global _LOAD_MSD
    _LOAD_MSD = Path(args.load) if args.load else None

    out = Path(args.out)
    manifest: list[str] = []

    if not args.no_plots:
        print("== Gráficos de calibração (store canônica) ==")
        from bolt_analysis_studio.validation.case_registry import all_records
        records = all_records()
        store = load_store()
        gdir = out / "graficos"

        # ⚠️ `fig_reference_set` (condicoes de referencia da UFU) NAO e mais
        # chamada: a UFU saiu do projeto em 2026-08-01. A funcao fica no
        # arquivo com a marca, porque apaga-la perderia o registro.
        # fig_reference_set(records, store, gdir, args.dpi, args.pdf, manifest)
        fig_cadeia_extracao(records, store, gdir, args.dpi, args.pdf, manifest)
        fig_uma_fisica(records, store, gdir, args.dpi, args.pdf, manifest)
        fig_paridade(records, store, gdir, args.dpi, args.pdf, manifest)
        fig_envelope(records, store, gdir, args.dpi, args.pdf, manifest)
        fig_decisao(records, store, gdir, args.dpi, args.pdf, manifest)
        fig_custo_calibracao(records, store, gdir, args.dpi, args.pdf, manifest)
        fig_sensibilidade(gdir, args.dpi, args.pdf, manifest)
        for src in [s.strip() for s in args.sources.split(",") if s.strip()]:
            fig_model_vs_data_grid(records, store, src, gdir,
                                   args.dpi, args.pdf, manifest)
        # decomposição: casos UFU + extras pedidos
        # ⚠️ era `if r.source == "UFU_LAB"`; a UFU saiu do projeto. Agora usa
        # uma curva de mecanismo dominante distinto por fonte, o que e o que a
        # figura de decomposicao quer mostrar de fato.
        decomp_ids = ["liu2016wear_fig11a_af7p5kn",
                      "li2022marstruc_creep_10kN_Ra0p8_min",
                      "liu2022_fig7a_oil_direct_t3",
                      "caccese2009_compblock_71kPa"]
        decomp_ids += [c.strip() for c in args.decomp_cases.split(",")
                       if c.strip()]
        for cid in decomp_ids:
            fig_decomposition(records, store, cid, gdir,
                              args.dpi, args.pdf, manifest)
        fig_ledger(gdir, args.dpi, args.pdf, manifest)
        fig_per_source_medians(gdir, args.dpi, args.pdf, manifest)

    if not args.no_gui:
        print("== Capturas de tela do Bolt Analysis Studio ==")
        grab_gui(out / "screenshots", manifest, show=args.show,
                 include_v2=args.v2)

    out.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    try:
        from bolt_analysis_studio.validation.runner import engine_fingerprint
        fp = engine_fingerprint()
    except Exception:
        fp = "(indisponível)"
    (out / "manifest.txt").write_text(
        f"Figuras exportadas em {stamp}\n"
        f"Fingerprint do motor: {fp}\n\n" + "\n".join(manifest) + "\n",
        encoding="utf-8")
    print(f"\n{len(manifest)} arquivos gerados em {out}")
    print(f"manifesto: {out / 'manifest.txt'}")


if __name__ == "__main__":
    main()
