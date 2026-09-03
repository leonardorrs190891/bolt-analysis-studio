# -*- coding: utf-8 -*-
"""Seletor de caso da validacao para importar (2026-09-03).

Abrir um dos 205 casos do censo pelo dialogo de arquivo obriga a navegar 29
pastas e saber o nome do arquivo. Este dialogo lista todos com busca, mostra a
que artigo cada um pertence e o erro do modelo naquela curva, e carrega o
escolhido.

Le `Models/SAVED_CASES/indice.json`, gerado junto com os .msd, e NAO o registry:
carregar 210 casos e o store a cada abertura custaria segundos por nada, e o
indice ja' traz censo, criterio e MAE prontos.

Por padrao mostra so' o CENSO DO ARTIGO (205 de 210). Os 5 de fora existem e
sao abriveis, mas ficam atras de uma caixa de selecao: nao contam em nenhum
numero do manuscrito, e apresenta-los misturados convidaria a usar um deles
pensando que conta.
"""
from __future__ import annotations

import json
from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (QCheckBox, QDialog, QDialogButtonBox, QHBoxLayout,
                             QLabel, QLineEdit, QTreeWidget, QTreeWidgetItem,
                             QVBoxLayout)


def caminho_indice() -> Path | None:
    try:
        from ....validation.inputs import repo_root
        alvo = repo_root() / "Models" / "SAVED_CASES" / "indice.json"
        return alvo if alvo.is_file() else None
    except Exception:                                        # noqa: BLE001
        return None


class CasePicker(QDialog):
    """Escolhe um caso da validacao. `escolhido` traz o caminho do .msd."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Importar caso da validação")
        self.resize(820, 560)
        self.escolhido: str | None = None
        self._dados = self._carrega()
        self._monta()
        self._preenche()

    # --- dados ---
    def _carrega(self) -> dict:
        alvo = caminho_indice()
        if alvo is None:
            return {"casos": [], "total": 0, "no_censo": 0,
                    "atendem_criterio": 0}
        try:
            return json.loads(alvo.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return {"casos": [], "total": 0, "no_censo": 0,
                    "atendem_criterio": 0}

    def _raiz_casos(self) -> Path | None:
        alvo = caminho_indice()
        return alvo.parent if alvo else None

    # --- ui ---
    def _monta(self):
        lay = QVBoxLayout(self)
        d = self._dados
        self.resumo = QLabel(
            f"<b>{d.get('no_censo', 0)}</b> casos no censo do artigo, dos quais "
            f"<b>{d.get('atendem_criterio', 0)}</b> atendem ao critério. "
            f"<span style='color:gray'>{d.get('total', 0)} no total.</span>")
        lay.addWidget(self.resumo)

        topo = QHBoxLayout()
        self.busca = QLineEdit()
        self.busca.setPlaceholderText(
            "Buscar por artigo, caso ou referência…  (ex.: lu2024, M8, Sensors)")
        self.busca.textChanged.connect(self._preenche)
        topo.addWidget(self.busca, stretch=1)
        self.so_censo = QCheckBox("Somente o censo do artigo")
        self.so_censo.setChecked(True)
        self.so_censo.toggled.connect(self._preenche)
        topo.addWidget(self.so_censo)
        lay.addLayout(topo)

        self.arvore = QTreeWidget()
        self.arvore.setHeaderLabels(["Caso", "Censo", "Critério", "MAE"])
        self.arvore.setColumnWidth(0, 460)
        self.arvore.itemDoubleClicked.connect(self._duplo)
        self.arvore.currentItemChanged.connect(self._mudou)
        lay.addWidget(self.arvore, stretch=1)

        self.detalhe = QLabel("")
        self.detalhe.setWordWrap(True)
        lay.addWidget(self.detalhe)

        self.botoes = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Open
            | QDialogButtonBox.StandardButton.Cancel)
        # O texto padrao dos botoes vem da traducao do Qt, que segue o locale
        # do sistema e sai "Open/Cancel" no meio de um dialogo em portugues.
        self.botoes.button(
            QDialogButtonBox.StandardButton.Open).setText("Abrir")
        self.botoes.button(
            QDialogButtonBox.StandardButton.Cancel).setText("Cancelar")
        self.botoes.accepted.connect(self._aceitar)
        self.botoes.rejected.connect(self.reject)
        self.botoes.button(
            QDialogButtonBox.StandardButton.Open).setEnabled(False)
        lay.addWidget(self.botoes)

    def _preenche(self):
        termo = (self.busca.text() or "").strip().lower()
        so_censo = self.so_censo.isChecked()
        self.arvore.clear()
        por_fonte = {}
        for c in self._dados.get("casos", []):
            if so_censo and not c.get("censo"):
                continue
            if termo and termo not in " ".join(
                    str(c.get(k, "")) for k in
                    ("case_id", "source", "name", "reference", "doi")).lower():
                continue
            por_fonte.setdefault(c["source"], []).append(c)

        for fonte in sorted(por_fonte):
            itens = sorted(por_fonte[fonte], key=lambda z: z["case_id"])
            topo = QTreeWidgetItem([f"{fonte}  ({len(itens)})", "", "", ""])
            for c in itens:
                mae = c.get("mae")
                filho = QTreeWidgetItem([
                    c["case_id"],
                    "sim" if c.get("censo") else "não",
                    "sim" if c.get("criterio") else "—",
                    "" if mae is None else f"{mae:.4f}"])
                filho.setData(0, Qt.ItemDataRole.UserRole, c)
                topo.addChild(filho)
            self.arvore.addTopLevelItem(topo)
        self.arvore.expandAll()
        # Ja' deixa o primeiro caso escolhido: com a busca digitada, Enter abre
        # o resultado sem tirar a mao do teclado, e o rodape mostra a citacao
        # em vez de uma faixa vazia.
        primeiro = self.arvore.topLevelItem(0)
        if primeiro is not None and primeiro.childCount():
            self.arvore.setCurrentItem(primeiro.child(0))
        else:
            self._mudou(None)

    def _mudou(self, atual, _anterior=None):
        c = atual.data(0, Qt.ItemDataRole.UserRole) if atual else None
        self.botoes.button(
            QDialogButtonBox.StandardButton.Open).setEnabled(c is not None)
        if not c:
            self.detalhe.setText("")
            return
        ref = c.get("reference") or c["source"]
        doi = c.get("doi")
        alvo = f"<a href='https://doi.org/{doi}'>{doi}</a>" if doi else "sem DOI"
        fora = ("" if c.get("censo") else
                "<br><span style='color:#e0a900'>Fora do censo do artigo: "
                "não é contado em nenhum número do manuscrito.</span>")
        self.detalhe.setText(f"<b>{c.get('name') or c['case_id']}</b><br>"
                             f"{ref} &mdash; {alvo}{fora}")

    def _duplo(self, item, _col=0):
        if item.data(0, Qt.ItemDataRole.UserRole):
            self._aceitar()

    def _aceitar(self):
        item = self.arvore.currentItem()
        c = item.data(0, Qt.ItemDataRole.UserRole) if item else None
        raiz = self._raiz_casos()
        if not c or raiz is None:
            return
        alvo = raiz / c["arquivo"]
        if not alvo.is_file():
            self.detalhe.setText(
                f"<span style='color:#d20f39'>Arquivo ausente: {alvo.name}. "
                f"Rode <code>build_saved_cases.py</code>.</span>")
            return
        self.escolhido = str(alvo)
        self.accept()
