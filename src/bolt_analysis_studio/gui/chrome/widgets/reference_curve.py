# -*- coding: utf-8 -*-
"""Curva experimental de referencia para o ajuste de parametros (2026-09-03).

O otimizador (`numerical/parameter_identifier.py`) e o dialogo que o pilota
(`CalibrationDialog`) existiam desde antes, com caixa de selecao e limites por
parametro, mas so' eram alcancaveis pela janela V1 e so' aceitavam curva vinda
de um CSV carregado a mao. Este modulo da' as DUAS origens:

  a) o CASO DA VALIDACAO de onde o modelo aberto veio — os pontos vem do store,
     ja' na convencao da campanha (`metric_x` / `metric_data`);
  b) um CSV do usuario.

Sobre (a): NAO relemos o CSV digitalizado. O runner aplica ao dado bruto uma
sequencia de convencoes pre-registradas — `csv_x_offset` e `csv_x_scale` (o
ECCLES vem em segundos, o LU ancora em x=1), normalizacao no primeiro ponto,
corte em `FLOOR_TRIM=0,10` e nova normalizacao — e reimplementar isso aqui
criaria um segundo dado experimental que divergiria do artigo. O store guarda
o resultado dessas convencoes nos 210 casos; e' de la' que se le.
"""
from __future__ import annotations

import csv
import re
from pathlib import Path

from PyQt6.QtWidgets import (QDialog, QDialogButtonBox, QLabel, QRadioButton,
                             QVBoxLayout)

# O gerador de casos escreve esta linha no .msd; e' a unica ligacao entre um
# arquivo aberto e o caso de onde ele veio. Ler prosa seria fragil sozinho,
# por isso o id e' SEMPRE conferido contra o registry antes de valer.
_MARCA = re.compile(r"validation case\s+([A-Za-z0-9_.\-]+)")


def caso_do_modelo(model) -> str | None:
    """case_id do caso de validacao que originou o modelo, ou None."""
    if model is None:
        return None
    cid = getattr(model, "validation_case_id", None)
    if not cid:
        m = _MARCA.search(str(getattr(model, "description", "") or ""))
        cid = m.group(1) if m else None
    if not cid:
        return None
    try:
        from ....validation.case_registry import record
        return cid if record(cid) is not None else None
    except Exception:                                        # noqa: BLE001
        return None


def curva_do_caso(case_id: str, F0_N: float = 0.0) -> dict | None:
    """Pontos experimentais do caso, na convencao da campanha."""
    try:
        from ....validation.store import ValidationStore
        res = ValidationStore().get(case_id)
    except Exception:                                        # noqa: BLE001
        return None
    x = list(getattr(res, "metric_x", None) or [])
    y = list(getattr(res, "metric_data", None) or [])
    if len(x) < 2 or len(x) != len(y):
        return None
    return _monta(x, y, F0_N, rotulo=case_id, caminho="",
                  origem=f"caso da validacao {case_id}")


def curva_de_csv(caminho: str, F0_N: float = 0.0) -> dict:
    """Le um CSV de decaimento. Aceita os DOIS layouts que o repo produz.

    O corpus digitalizado grava `cycle,F_over_F0` (2 colunas); o leitor da V1
    esperava `cycle,F_kN,F_over_F0` (3 colunas) e, lido com ele, um arquivo do
    corpus punha F/F0 na coluna de forca e deixava a razao zerada.
    """
    linhas = []
    with open(caminho, encoding="utf-8-sig", newline="") as f:
        for row in csv.reader(f):
            if not row:
                continue
            try:
                c = float(row[0])
            except ValueError:
                continue                                       # cabecalho
            linhas.append([c] + [_num(v) for v in row[1:]])
    if len(linhas) < 2:
        raise ValueError("nenhuma linha numerica utilizavel no CSV")

    ciclo = [l[0] for l in linhas]
    largura = max(len(l) for l in linhas)
    if largura >= 3:
        razao = [l[2] if len(l) > 2 else 0.0 for l in linhas]
        forca = [l[1] if len(l) > 1 else 0.0 for l in linhas]
        if not any(v > 0 for v in razao):        # 3a coluna vazia: usa a forca
            base = next((v for v in forca if v > 0), 0.0) or 1.0
            razao = [v / base for v in forca]
    else:
        razao = [l[1] if len(l) > 1 else 0.0 for l in linhas]
        forca = []
    if not any(v > 0 for v in razao):
        raise ValueError("nao encontrei uma coluna de F/F0 utilizavel")
    return _monta(ciclo, razao, F0_N, rotulo=Path(caminho).name,
                  caminho=caminho, origem="CSV do usuario",
                  forca_kN=forca or None)


def _num(v) -> float:
    try:
        return float(str(v).strip().replace(",", "."))
    except ValueError:
        return 0.0


def _monta(ciclo, razao, F0_N, rotulo, caminho, origem, forca_kN=None) -> dict:
    import numpy as np

    r = np.asarray(razao, dtype=float)
    if forca_kN:
        f = np.asarray(forca_kN, dtype=float)
    else:
        # F_kN so' e' informativo aqui: o dialogo prefere F_ratio quando > 0.
        f = r * (float(F0_N) / 1000.0) if F0_N else np.zeros_like(r)
    return {"cycle": np.asarray(ciclo, dtype=float), "F_ratio": r, "F_kN": f,
            "label": rotulo, "path": caminho, "origem": origem}


class ReferenceSourceDialog(QDialog):
    """As duas origens. `escolha` fica 'caso' ou 'csv'."""

    def __init__(self, parent=None, case_id: str | None = None):
        super().__init__(parent)
        self.setWindowTitle("Curva de referência")
        self.escolha: str | None = None
        self._case_id = case_id

        lay = QVBoxLayout(self)
        lay.addWidget(QLabel(
            "Contra qual curva experimental o modelo deve ser ajustado?"))

        self.rb_caso = QRadioButton()
        if case_id:
            self.rb_caso.setText(f"Caso da validação — {case_id}")
            self.rb_caso.setChecked(True)
            lay.addWidget(self.rb_caso)
            lay.addWidget(_nota(
                "Os pontos vêm do artigo de origem, digitalizados, já na "
                "convenção da campanha (escala do eixo, normalização e corte "
                "do piso). É a mesma curva que o relatório daquele caso usa."))
        else:
            self.rb_caso.setText("Caso da validação — indisponível")
            self.rb_caso.setEnabled(False)
            lay.addWidget(self.rb_caso)
            lay.addWidget(_nota(
                "O modelo aberto não veio de um caso da validação. Importe um "
                "por <b>Arquivo &rarr; Importar caso da validação</b> "
                "(Ctrl+I) para usar esta origem."))

        self.rb_csv = QRadioButton("Arquivo CSV…")
        self.rb_csv.setChecked(not case_id)
        lay.addWidget(self.rb_csv)
        lay.addWidget(_nota(
            "Duas ou três colunas: <code>ciclo, F/F₀</code> ou "
            "<code>ciclo, F[kN], F/F₀</code>. A primeira linha pode ser "
            "cabeçalho."))

        botoes = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok
                                  | QDialogButtonBox.StandardButton.Cancel)
        botoes.button(QDialogButtonBox.StandardButton.Ok).setText("Continuar")
        botoes.button(
            QDialogButtonBox.StandardButton.Cancel).setText("Cancelar")
        botoes.accepted.connect(self._ok)
        botoes.rejected.connect(self.reject)
        lay.addWidget(botoes)

    def _ok(self):
        self.escolha = "caso" if self.rb_caso.isChecked() else "csv"
        self.accept()


def _nota(html: str) -> QLabel:
    rot = QLabel(html)
    rot.setWordWrap(True)
    rot.setStyleSheet("color: palette(mid); margin-left: 22px;")
    return rot
