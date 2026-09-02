# -*- coding: utf-8 -*-
"""ValidationBrowser — navegador dos 128 casos de validacao (Plano B, spec
2026-07-10 §4): arvore fonte->caso + detalhe (curva dado vs modelo +
decomposicao + metricas + staleness) + acoes. Widget puro: emite sinais; quem
executa e o ValidationController."""
from __future__ import annotations

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (QGroupBox, QHBoxLayout, QLabel, QPushButton,
                             QSplitter, QTreeWidget, QTreeWidgetItem,
                             QVBoxLayout, QWidget)

from ....validation.case_registry import all_records, record
from ....validation.report_html import NICE, data_points
from ....validation.store import ValidationStore
from ...theme import Theme

_DECOMP_COLORS = {"embedding": "#2f6f8f", "creep": "#8f6f2f",
                  "wear": "#b3452c", "rotational_loosening": "#5f8f2f",
                  "thread_fretting": "#7f5fa0", "fatigue": "#a05f5f"}


def _f(v, fmt="{:.4f}"):
    return "—" if v is None else fmt.format(v)


class ValidationBrowser(QWidget):
    open_in_model_requested = pyqtSignal(str)
    resim_case_requested = pyqtSignal(str)
    resim_all_requested = pyqtSignal()
    open_report_requested = pyqtSignal(str)
    save_msd_requested = pyqtSignal(str)
    master_report_requested = pyqtSignal()
    import_case_requested = pyqtSignal()
    copy_prompt_requested = pyqtSignal()
    save_prompt_requested = pyqtSignal()

    def __init__(self, store: ValidationStore = None, parent=None):
        super().__init__(parent)
        self.store = store or ValidationStore()
        self._current_id = None
        self._build_ui()
        self.populate()
        # re-tema o painel de intake + gráfico quando o usuário troca de tema
        Theme.register_callback(self.reskin)

    def _build_ui(self):
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Caso", "MAE"])
        self.tree.setColumnWidth(0, 320)
        self.tree.currentItemChanged.connect(self._on_item)

        # detalhe: canvas matplotlib + metricas + acoes
        from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
        from matplotlib.figure import Figure
        self._fig = Figure(figsize=(5, 4), tight_layout=True)
        self.canvas = FigureCanvasQTAgg(self._fig)
        self.canvas.setProperty("selfThemed", True)   # re-temado por reskin()
        self.metrics_label = QLabel("Selecione um caso.")
        self.metrics_label.setWordWrap(True)
        # CONDICAO DE CONTORNO EXTERNA (2026-08-23). Rotulo proprio, OCULTO por
        # default: aparece so' em curva com carga axial externa. Motivo medido —
        # sem ele, no browser a `eccles2010_fig3_typical_no_axial` e a
        # `eccles2010_fig6_annotated_4kN_axial` ficam INDISTINGUIVEIS, e foi
        # exatamente essa invisibilidade que produziu as provas de excecao de
        # "sobreposicao axial", o bloqueio de pareamento e o "ensemble de 4
        # replicas" na fonte. Terceira camada do mesmo defeito: o input nao
        # existia (53996b7), existia e nao aparecia no report (e0082b3), e
        # aparecia no report e nao no app.
        self.bc_label = QLabel("")
        self.bc_label.setVisible(False)
        self.stamp_label = QLabel("")
        self.btn_open_model = QPushButton("Abrir no Model/Run")
        self.btn_resim = QPushButton("Re-simular caso")
        self.btn_resim_all = QPushButton("Re-simular tudo")
        self.btn_report = QPushButton("Report HTML")
        self.btn_master = QPushButton("Report geral")
        self.btn_save_msd = QPushButton("Salvar caso como .msd…")
        self.btn_open_model.clicked.connect(
            lambda: self._emit(self.open_in_model_requested))
        self.btn_resim.clicked.connect(
            lambda: self._emit(self.resim_case_requested))
        self.btn_resim_all.clicked.connect(self.resim_all_requested.emit)
        self.btn_report.clicked.connect(
            lambda: self._emit(self.open_report_requested))
        self.btn_master.clicked.connect(self.master_report_requested.emit)
        self.btn_save_msd.clicked.connect(
            lambda: self._emit(self.save_msd_requested))
        for b in (self.btn_open_model, self.btn_resim, self.btn_report,
                  self.btn_save_msd):
            b.setEnabled(False)

        # intake de casos do usuario — PAINEL DESTACADO (pedido do professor
        # 2026-07-10: secao clara e destacada; o prompt funciona em QUALQUER IA
        # e devolve os dados prontos no formato que o software le)
        self.btn_import = QPushButton("3. Importar caso…")
        self.btn_prompt_copy = QPushButton("1. Copiar prompt")
        self.btn_prompt_save = QPushButton("Salvar prompt…")
        self.btn_import.clicked.connect(self.import_case_requested.emit)
        self.btn_prompt_copy.clicked.connect(self.copy_prompt_requested.emit)
        self.btn_prompt_save.clicked.connect(self.save_prompt_requested.emit)
        self.intake_group = QGroupBox(
            "📥  Importe o SEU ensaio — via qualquer IA")
        self.intake_group.setObjectName("intakeGroup")
        self.intake_explainer = QLabel(
            "<b>1.</b> Copie o prompt · <b>2.</b> cole em qualquer ferramenta "
            "de IA (ChatGPT, Claude, Gemini…) junto com a sua curva "
            "experimental (txt/csv/planilha) e responda às perguntas do "
            "ensaio · <b>3.</b> importe o arquivo <code>.bascase.json</code> "
            "que ela devolve — o software valida, faz o ajuste prévio do "
            "modelo e gera o report completo.")
        self.intake_explainer.setWordWrap(True)
        self.intake_status = QLabel("")
        self.intake_status.setObjectName("intakeStatus")
        ig_btns = QHBoxLayout()
        for b in (self.btn_prompt_copy, self.btn_prompt_save, self.btn_import):
            ig_btns.addWidget(b)
        ig_btns.addWidget(self.intake_status, stretch=1)
        ig_lay = QVBoxLayout(self.intake_group)
        ig_lay.addWidget(self.intake_explainer)
        ig_lay.addLayout(ig_btns)
        self._apply_intake_style()

        btns = QHBoxLayout()
        for b in (self.btn_open_model, self.btn_resim, self.btn_resim_all,
                  self.btn_report, self.btn_master, self.btn_save_msd):
            btns.addWidget(b)
        right = QWidget()
        rl = QVBoxLayout(right)
        rl.addWidget(self.canvas, stretch=1)
        rl.addWidget(self.metrics_label)
        rl.addWidget(self.bc_label)
        rl.addWidget(self.stamp_label)
        rl.addLayout(btns)
        self.detail = right

        split = QSplitter()
        split.addWidget(self.tree)
        split.addWidget(right)
        split.setStretchFactor(1, 1)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(self.intake_group)          # destaque no TOPO do modulo
        lay.addWidget(split, stretch=1)

    def set_intake_status(self, text: str) -> None:
        self.intake_status.setText(text)

    def _emit(self, sig):
        if self._current_id:
            sig.emit(self._current_id)

    # --- populacao/estado ---
    def populate(self):
        self.tree.clear()
        by_src = {}
        for r in all_records():
            by_src.setdefault(r.source, []).append(r)
        for src in sorted(by_src):
            top = QTreeWidgetItem([NICE.get(src, src), ""])
            for r in sorted(by_src[src], key=lambda z: z.case_id):
                res = self.store.get(r.case_id)
                mae = (f"{res.mae:.3f}" if res and res.ok and res.mae is not None
                       else ("erro" if res and not res.ok else "—"))
                it = QTreeWidgetItem([r.case_id, mae])
                it.setData(0, Qt.ItemDataRole.UserRole, r.case_id)
                top.addChild(it)
            self.tree.addTopLevelItem(top)

    def current_case_id(self):
        return self._current_id

    def _on_item(self, cur, _prev=None):
        cid = cur.data(0, Qt.ItemDataRole.UserRole) if cur is not None else None
        if cid:
            self.show_case(cid)

    def show_case(self, case_id: str):
        rec = record(case_id)
        if rec is None:
            return
        self._current_id = case_id
        res = self.store.get(case_id)
        runnable = rec.family != "other"
        self.btn_open_model.setEnabled(runnable)
        self.btn_resim.setEnabled(runnable)
        # mesmo criterio do 'Abrir no Model/Run': um caso family='other'
        # nao monta modelo, entao nao ha' o que salvar.
        self.btn_save_msd.setEnabled(runnable)
        self.btn_report.setEnabled(True)
        # metricas
        if res is None:
            self.metrics_label.setText(f"{case_id}: nunca simulado — re-simule.")
        elif not res.ok:
            self.metrics_label.setText(f"{case_id}: não simulável — {res.error}")
        else:
            camp = ""
            if rec.gallery_entry is not None:
                camp = f" · campanha {float(rec.gallery_entry['mae']):.4f}"
            self.metrics_label.setText(
                f"MAE {_f(res.mae)}{camp} · RMSE {_f(res.rmse)}"
                f" · F/F₀ final: modelo {_f(res.final_pred, '{:.3f}')}"
                f" vs dado {_f(res.final_data, '{:.3f}')}")
        # BC externa: le do ValidationCase e mostra valor + MODO. Condicional
        # (isolamento estrutural): curva sem axial nao ganha linha nenhuma.
        _ax = float(getattr(rec.validation_case, "external_axial_N", 0.0) or 0.0)
        if _ax > 0.0:
            _md = getattr(rec.validation_case, "external_axial_mode", "") or "constant"
            self.bc_label.setText(
                f"condição de contorno externa: carga axial {_ax:.0f} N ({_md})"
                " — lida do paper")
            self.bc_label.setVisible(True)
        else:
            # LIMPA o texto, nao so' esconde: `setVisible(False)` deixa o
            # conteudo da curva ANTERIOR no rotulo, e se a visibilidade falhar
            # (tema, re-layout, teste offscreen) o app exibe a carga axial da
            # curva ERRADA. Dado obsoleto e' pior que dado ausente. Pego pelo
            # proprio teste deste widget em 2026-08-23: a fig3 (sem axial)
            # aparecia com os 700 N da fig8b.
            self.bc_label.clear()
            self.bc_label.setVisible(False)
        stale = self.store.is_stale(case_id)
        stamp = getattr(res, "generated_at", "—") if res else "—"
        self.stamp_label.setText(
            f"gerado em {stamp} · {'DESATUALIZADO (re-simule)' if stale else 'atual'}")
        self._plot(rec, res)

    def refresh_case(self, case_id: str):
        self.populate()
        self.show_case(case_id)

    def _apply_intake_style(self):
        """Estilo do painel de intake a partir dos tokens do tema (segue a
        troca de tema em vez de congelar em hex)."""
        self.intake_group.setStyleSheet(
            "QGroupBox#intakeGroup{font-weight:bold;border:2px solid %s;"
            "border-radius:8px;margin-top:10px;padding-top:14px}"
            "QGroupBox#intakeGroup::title{subcontrol-origin:margin;left:10px;"
            "padding:0 4px}QLabel#intakeStatus{color:%s;font-weight:bold}"
            % (Theme.BLUE, Theme.GREEN))

    def reskin(self):
        """Callback de troca de tema: recolore o intake e re-renderiza o gráfico
        atual com a paleta nova (o canvas assa a cor no draw). Auto-remove o
        callback se o widget C++ já foi destruído (evita vazar entre janelas)."""
        try:
            self.intake_group.objectName()      # toca o C++; RuntimeError se morto
        except RuntimeError:
            Theme.unregister_callback(self.reskin)
            return
        self._apply_intake_style()
        if self._current_id:
            self.show_case(self._current_id)    # re-desenha dado+modelo+decomp
        else:
            self._fig.set_facecolor(Theme.BASE)
            self.canvas.draw_idle()

    def _style_axes(self, ax):
        """Aplica a paleta atual aos eixos (facecolor, ticks, spines, legenda)."""
        ax.set_facecolor(Theme.SURFACE0)
        ax.tick_params(colors=Theme.SUBTEXT)
        ax.xaxis.label.set_color(Theme.TEXT)
        ax.yaxis.label.set_color(Theme.TEXT)
        ax.title.set_color(Theme.TEXT)
        for spine in ax.spines.values():
            spine.set_color(Theme.SURFACE2)
        leg = ax.get_legend()
        if leg is not None:
            leg.get_frame().set_facecolor(Theme.SURFACE0)
            leg.get_frame().set_edgecolor(Theme.SURFACE2)
            for txt in leg.get_texts():
                txt.set_color(Theme.TEXT)

    def _plot(self, rec, res):
        self._fig.clear()
        self._fig.set_facecolor(Theme.BASE)
        ax = self._fig.add_subplot(211)
        try:
            dx, dy = data_points(rec)
            if len(dx):
                ax.plot(dx, dy, "o", ms=3, label="dado (artigo)")
        except Exception:
            pass
        if res is not None and res.ok and res.cycles:
            ax.plot(res.cycles, res.ratio, "-", label="modelo")
        ax.set_ylabel("F/F₀")
        ax.set_ylim(0, 1.08)
        ax.legend(fontsize=7)
        ax2 = self._fig.add_subplot(212, sharex=ax)
        if res is not None and res.ok and res.decomp:
            mechs = list(res.decomp)
            ys = [res.decomp[m] for m in mechs]
            ax2.stackplot(res.cycles, *ys, labels=mechs,
                          colors=[_DECOMP_COLORS.get(m, "#888") for m in mechs])
            ax2.legend(fontsize=6, loc="upper left")
        else:
            ax2.text(0.5, 0.5, "sem decomposição — re-simule",
                     ha="center", va="center", transform=ax2.transAxes,
                     color=Theme.SUBTEXT)
        ax2.set_xlabel("ciclos N")
        ax2.set_ylabel("perda F/F₀")
        for a in (ax, ax2):
            self._style_axes(a)
        self.canvas.draw_idle()
