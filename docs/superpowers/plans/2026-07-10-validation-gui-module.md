# Módulo Validation no chrome V2 (Plano B) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: superpowers:executing-plans (inline) ou subagent-driven-development. Steps em checkbox `- [ ]`.

**Goal:** Módulo Validation no chrome V2: navegar os 128 casos (árvore fonte→caso), ver curva/erros/decomposição no app, re-simular (caso e batch em background), abrir reports HTML — e **"Abrir no Model/Run"**: um clique monta o caso completo no software (modelo MSD + carregamento + overrides de material E geometria com proveniência) para o usuário editar livremente e rodar (requisito do professor 2026-07-10).

**Architecture:** Três camadas. (1) `validation/gui_bridge.py` (GUI-free) traduz um `CaseRecord` em artefatos do software: `AnalysisSpec` → `build_model`, `_v2_tuner_overrides` (mesmos kwargs de material do runner — fonte única via refactor `material_kwargs_for`) e `_v2_geometry_overrides` (novo canal). (2) `solver_worker._compute_v2_history` ganha leitura **aditiva** de `model._v2_geometry_overrides` (campos de `JointGeometry`) — sem isso o Run usa L_eff=3d/A_contact=1e-4 e não reproduz o report. (3) Chrome: `ValidationBrowser` (widget: árvore + detalhe matplotlib + botões) + `ValidationController` (orquestra store/runner/bridge, re-sim em QThread) + página no `_center` ativada pelo módulo **Results** (sub-mode Validation; os plots de Run do Results vêm no Plano 5 da sequência chrome).

**Tech Stack:** PyQt6, matplotlib (`FigureCanvasQTAgg`, já usado na V1), pacote `validation` (Plano A), pytest offscreen.

## Global Constraints

- Mesmas dos planos anteriores: `utf-8`, `ast.parse` após cada edição, testes offscreen (fixture `qapp` + autouse `_reset_app_state`), um commit por tarefa, `Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>`.
- **NÃO tocar**: engine (`numerical/`), `msd_builder.py`, arquivos foreign (`New_Theory/frontier_polish.py`, `New_Theory/liu2025_nemb_probe.py`).
- `core/solver_worker.py`: SÓ o bloco de geometria de `_compute_v2_history` (~linha 1041), mudança aditiva com default = comportamento atual bit-idêntico.
- QThread em teste: **chamar `.run()` sincronamente**, nunca `.start()` + wait (flakiness).
- Fatos verificados: `JointGeometry` fields = `{E, A_s, L_eff, d_2, pitch, r_bearing, A_contact}` (`dynamic_stiffness_analyzer.py:51`); `AnalysisSpec` tem `bolt_diameter_mm, pitch_mm, preload_pct_yield, loading_type, control_mode, delta_amplitude_mm, F_amplitude_N, frequency_hz, n_cycles, reference_csv_path` (`new_analysis_wizard.py:135`); teste de solver usa `SolverWorker.__new__` + `SimpleNamespace` (padrão `tests/test_v2_solver_preload.py`); `_compute_v2_history` lê `self._current_model` p/ overrides (linha 1051).
- O Run computa `initial_preload` etc. do config da SolverTab — o "Abrir no Model" entrega o modelo pronto; a fidelidade do Run vem dos dois canais de override. Diferenças residuais (ex. F0 exato vs %yield arredondado) são documentadas no STATUS, não escondidas.

## File Structure

**Create:**
```
src/bolt_analysis_studio/validation/gui_bridge.py         # Task 2
src/bolt_analysis_studio/gui/chrome/widgets/validation_browser.py   # Task 3
src/bolt_analysis_studio/gui/chrome/controllers/validation_controller.py  # Task 4
tests/test_validation_gui_bridge.py
tests/test_v2_geometry_overrides.py
tests/test_validation_browser.py
tests/test_chrome_validation_module.py
```
**Modify:**
```
src/bolt_analysis_studio/validation/runner.py       # Task 1: extrai material_kwargs_for + loading_for público
src/bolt_analysis_studio/validation/report_html.py  # Task 1: _data_points -> data_points público (alias)
src/bolt_analysis_studio/core/solver_worker.py      # Task 2b: canal _v2_geometry_overrides
src/bolt_analysis_studio/gui/chrome/app_window.py   # Task 5: Results -> página Validation
tests/test_validation_runner.py                     # Task 1 (append)
```

---

## Task 1: Runner expõe a montagem (fonte única p/ o bridge)

**Files:**
- Modify: `src/bolt_analysis_studio/validation/runner.py`, `src/bolt_analysis_studio/validation/report_html.py`
- Test: `tests/test_validation_runner.py` (append)

**Interfaces:**
- Produces: `material_kwargs_for(rec, inp) -> dict` (kwargs completos de `JointMaterial` que `simulate_case` usa: consts congeladas + pack + cfg adotada + emb + mu + conform_driver); `loading_for(rec) -> dict` (alias público de `_loading_for`: `{mode, delta_mm, F_amp_N, theta, inputs}`); `report_html.data_points(rec)` (alias público de `_data_points`).

- [ ] **Step 1: Teste falhando** — append em `tests/test_validation_runner.py`:

```python
def test_material_kwargs_match_simulation_config():
    # fonte unica: os kwargs expostos sao EXATAMENTE o que simulate_case monta
    from bolt_analysis_studio.numerical.dynamic_stiffness_analyzer import JointMaterial
    from bolt_analysis_studio.validation.case_registry import record
    from bolt_analysis_studio.validation.inputs import inputs_for
    from bolt_analysis_studio.validation.runner import material_kwargs_for
    rec = record("liu2025_M16_amp0p25")
    kw = material_kwargs_for(rec, inputs_for(rec.validation_case))
    assert set(kw) <= set(JointMaterial.__dataclass_fields__)
    assert kw["emb_depth"] == 4.9999999999999996e-06     # adotada vence a VDI
    assert kw["slip_onset_W"] == 150000.0                # cfg adotada LIU_2025
    assert kw["k_tr_mode"] == "bending"                  # pack LEGACY
    JointMaterial(**kw)                                  # constroi sem erro


def test_loading_for_public_alias():
    from bolt_analysis_studio.validation.case_registry import all_records
    from bolt_analysis_studio.validation.runner import loading_for
    rec = next(r for r in all_records() if r.family == "axial")
    load = loading_for(rec)
    assert load["mode"] == "force" and load["F_amp_N"] > 0
```

- [ ] **Step 2: Rodar e ver falhar** — `python -m pytest tests/test_validation_runner.py -q` → 2 novos FAIL (ImportError), 5 antigos PASS.

- [ ] **Step 3: Implementar.** Em `runner.py`, extrair de `simulate_case` o bloco de montagem (entre `consts, _ = frozen_constants()` e `mat = JointMaterial(**kw)`) para:

```python
def material_kwargs_for(rec: CaseRecord, inp: dict) -> dict:
    """Kwargs COMPLETOS de JointMaterial p/ o caso (constantes congeladas +
    pack + cfg adotada per-rig + emb com proveniencia + mu). Fonte unica:
    simulate_case E o gui_bridge ("Abrir no Run") montam por aqui."""
    consts, _ = frozen_constants()
    emb_m, _ = emb_depth_vdi(inp["rz"]["value"], n_inner_interfaces=1)
    overrides = _adopted_overrides(rec.source, consts, rec.case_id)
    mu = inp["mu"]["value"]
    kw = dict(emb_depth=emb_m, mu_thread=mu, mu_bearing=mu,
              conform_driver="effective", **consts)
    fields = JointMaterial.__dataclass_fields__
    for k, v in overrides.items():                # adotadas per-rig por cima
        if k in fields:
            kw[k] = v
    return kw
```

Em `simulate_case`, substituir o bloco pelo uso da função (mantendo `emb_br` e
`overrides` p/ o `config_used` — chamar `emb_depth_vdi`/`_adopted_overrides`
uma vez e passar `kw = material_kwargs_for(...)`; para evitar recomputo,
implementar `material_kwargs_for` retornando só `kw` e dentro de
`simulate_case` manter as duas chamadas auxiliares como estão hoje — o custo é
desprezível e o contrato "mesmos kwargs" fica testado). Adicionar no fim do
módulo:

```python
loading_for = _loading_for            # API publica p/ o gui_bridge
```

Em `report_html.py`, adicionar após `_data_points`:

```python
data_points = _data_points            # API publica p/ o browser (plot no app)
```

- [ ] **Step 4: `ast.parse` + rodar** — `python -m pytest tests/test_validation_runner.py tests/test_validation_report_html.py -q` → **13 passed** (7+6). O teste de paridade continua verde (mesmos kwargs).
- [ ] **Step 5: Commit** — `git commit -m "refactor(validation): material_kwargs_for/loading_for/data_points publicos (fonte unica p/ GUI) (Plano B)"`

---

## Task 2: `gui_bridge.py` — caso → modelo/overrides do software

**Files:**
- Create: `src/bolt_analysis_studio/validation/gui_bridge.py`
- Test: `tests/test_validation_gui_bridge.py`

**Interfaces:**
- Consumes: Task 1 (`material_kwargs_for`, `loading_for`), `inputs.geometry_for_case/inputs_for/repo_root`, `new_analysis_wizard.AnalysisSpec/build_model` (import LAZY dentro das funções — módulo importa PyQt6).
- Produces: `analysis_spec_for(rec) -> AnalysisSpec`; `geometry_overrides_for(rec) -> dict` (subset de `JointGeometry` fields, unidades SI); `build_case_model(rec) -> MSDModel` (modelo pronto com `_v2_tuner_overrides` + `_v2_geometry_overrides` + fricção nos 2 níveis); levanta `ValueError` p/ família `other`.

- [ ] **Step 1: Teste falhando** `tests/test_validation_gui_bridge.py`:

```python
import pytest


def test_analysis_spec_transverse():
    from bolt_analysis_studio.validation.case_registry import record
    from bolt_analysis_studio.validation.gui_bridge import analysis_spec_for
    rec = record("liu2025_M16_amp0p25")
    spec = analysis_spec_for(rec)
    assert spec.bolt_diameter_mm == 16.0 and spec.pitch_mm == 2.0
    assert spec.loading_type == "TRANSVERSE" and spec.control_mode == "displacement"
    assert spec.delta_amplitude_mm == rec.validation_case.transverse_displacement_mm
    assert spec.n_cycles == rec.validation_case.n_cycles
    assert spec.reference_csv_path.endswith("liu2025_M16_amp0p25.csv")


def test_analysis_spec_axial_force_mode():
    from bolt_analysis_studio.validation.case_registry import all_records
    from bolt_analysis_studio.validation.gui_bridge import analysis_spec_for
    rec = next(r for r in all_records() if r.family == "axial")
    spec = analysis_spec_for(rec)
    assert spec.loading_type == "AXIAL" and spec.control_mode == "force"
    assert spec.F_amplitude_N > 0


def test_geometry_overrides_match_runner_geometry():
    from bolt_analysis_studio.validation.case_registry import record
    from bolt_analysis_studio.validation.gui_bridge import geometry_overrides_for
    from bolt_analysis_studio.validation.inputs import geometry_for_case, inputs_for
    rec = record("liu2025_M16_amp0p25")
    gov = geometry_overrides_for(rec)
    g = geometry_for_case(rec.validation_case,
                          grip_mm=inputs_for(rec.validation_case)["grip_mm"]["value"])
    for f in ("A_s", "L_eff", "d_2", "pitch", "r_bearing", "A_contact"):
        assert gov[f] == getattr(g, f)


def test_build_case_model_attaches_both_channels(qapp):
    from bolt_analysis_studio.validation.case_registry import record
    from bolt_analysis_studio.validation.gui_bridge import build_case_model
    rec = record("liu2025_M16_amp0p25")
    model = build_case_model(rec)
    assert len(model.elements) > 0                       # cadeia com GROUND
    ov = model._v2_tuner_overrides
    assert ov["slip_onset_W"] == 150000.0                # material do runner
    gov = model._v2_geometry_overrides
    assert abs(gov["L_eff"] - 0.040) < 1e-9              # grip 2.5d = 40 mm (SI)
    assert model.global_loading.F_preload == rec.validation_case.initial_preload_N


def test_build_case_model_other_family_raises(qapp):
    from bolt_analysis_studio.validation.case_registry import all_records
    from bolt_analysis_studio.validation.gui_bridge import build_case_model
    rec = next(r for r in all_records() if r.family == "other")
    with pytest.raises(ValueError):
        build_case_model(rec)
```

- [ ] **Step 2: Rodar e ver falhar.**
- [ ] **Step 3: Implementar** `gui_bridge.py`:

```python
# -*- coding: utf-8 -*-
"""Ponte caso-de-validacao -> software (Plano B, requisito do professor
2026-07-10: "todos esses estudos devem estar disponiveis para ser rodados
livremente no software"). Monta o modelo MSD + carregamento + overrides de
material (_v2_tuner_overrides) E geometria (_v2_geometry_overrides) a partir
do MESMO caminho de inputs do runner — o Run reproduz o report e o usuario
edita livremente a partir dai. GUI-free (imports do wizard sao lazy)."""
from __future__ import annotations

from .case_registry import CaseRecord
from .inputs import geometry_for_case, inputs_for, repo_root
from .runner import loading_for, material_kwargs_for

_GEOM_FIELDS = ("A_s", "L_eff", "d_2", "pitch", "r_bearing", "A_contact")


def geometry_overrides_for(rec: CaseRecord) -> dict:
    """Campos de JointGeometry (SI) com proveniencia do caso — o canal
    _v2_geometry_overrides do solver_worker (sem ele o Run usa L_eff=3d e
    A_contact=1e-4 fixos e nao reproduz o report)."""
    inp = inputs_for(rec.validation_case)
    g = geometry_for_case(rec.validation_case, grip_mm=inp["grip_mm"]["value"])
    return {f: float(getattr(g, f)) for f in _GEOM_FIELDS}


def analysis_spec_for(rec: CaseRecord):
    """AnalysisSpec do wizard preenchido com o caso (build_model-ready)."""
    from ..gui.new_analysis_wizard import AnalysisSpec    # lazy: modulo puxa PyQt6
    case = rec.validation_case
    load = loading_for(rec)                               # ValueError p/ 'other'
    transverse = rec.family == "transverse"
    csv_rel = (rec.csv_path.relative_to(repo_root()).as_posix()
               if rec.csv_path is not None else "")
    return AnalysisSpec(
        project_name=f"Validation: {rec.case_id}",
        bolt_diameter_mm=float(case.bolt_diameter_mm),
        pitch_mm=float(case.pitch_mm),
        preload_pct_yield=float(case.preload_percent_yield),
        loading_type="TRANSVERSE" if transverse else "AXIAL",
        control_mode="displacement" if load["mode"] == "displacement" else "force",
        delta_amplitude_mm=float(load["delta_mm"]),
        F_amplitude_N=float(load["F_amp_N"]),
        frequency_hz=float(case.frequency_Hz),
        n_cycles=int(case.n_cycles),
        reference_csv_path=csv_rel,
    )


def build_case_model(rec: CaseRecord):
    """Modelo MSD completo do caso, pronto p/ o AppState: cadeia com GROUND
    (build_model), F0 do caso, ambos os canais de override anexados e a
    friccao nos dois niveis (regra Level-2/Level-3 do CLAUDE.md)."""
    from ..gui.new_analysis_wizard import build_model     # lazy
    spec = analysis_spec_for(rec)                         # ValueError p/ 'other'
    model = build_model(spec)
    case = rec.validation_case
    inp = inputs_for(case)
    model.global_loading.F_preload = float(case.initial_preload_N)
    mu = float(inp["mu"]["value"])
    model.mu_initial = mu                                 # Level-3 persistente
    model.global_loading.mu_initial = mu                  # Level-2 in-session
    model._v2_tuner_overrides = material_kwargs_for(rec, inp)
    model._v2_geometry_overrides = geometry_overrides_for(rec)
    return model
```

- [ ] **Step 4: `ast.parse` + rodar** — `python -m pytest tests/test_validation_gui_bridge.py -q` → **5 passed**. (Se `build_model` não aceitar algum campo/preset, ler o erro e ajustar SÓ o bridge — nunca o wizard.)
- [ ] **Step 5: Commit** — `git commit -m "feat(validation): gui_bridge — caso -> modelo MSD + overrides material/geometria (Plano B)"`

---

## Task 3: Canal `_v2_geometry_overrides` no solver_worker

**Files:**
- Modify: `src/bolt_analysis_studio/core/solver_worker.py` (bloco `geom = JointGeometry(...)` de `_compute_v2_history`, ~linha 1041)
- Test: `tests/test_v2_geometry_overrides.py`

**Interfaces:**
- Consumes: `model._v2_geometry_overrides: dict` (anexado pelo gui_bridge; ausente = comportamento atual).
- Produces: Run V2 com geometria do caso quando presente.

- [ ] **Step 1: Teste falhando** `tests/test_v2_geometry_overrides.py` (padrão de `test_v2_solver_preload.py`):

```python
import os
import types

import numpy as np
import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")


@pytest.fixture(scope="module")
def qapp():
    from PyQt6.QtWidgets import QApplication
    app = QApplication.instance() or QApplication([])
    yield app


def _worker():
    from bolt_analysis_studio.core.solver_worker import SolverWorker
    return SolverWorker.__new__(SolverWorker)


def _cfg():
    return types.SimpleNamespace(initial_preload=50000.0, transverse_force=12000.0,
                                 bolt_diameter_mm=16.0, pitch_mm=2.0)


def _model(geom_overrides=None):
    gl = types.SimpleNamespace(control_mode="displacement", delta_amplitude=0.5,
                               frequency=0.5, type="TRANSVERSE")
    return types.SimpleNamespace(global_loading=gl, _v2_tuner_overrides=None,
                                 _v2_geometry_overrides=geom_overrides)


def test_geometry_overrides_change_the_run(qapp):
    w = _worker()
    w._current_model = _model()
    base = w._compute_v2_history(_cfg(), 800)["ratio"]
    w._current_model = _model({"L_eff": 0.080, "A_contact": 3.2e-4})
    over = w._compute_v2_history(_cfg(), 800)["ratio"]
    assert not np.allclose(base, over)          # geometria do caso muda o Run


def test_absent_or_invalid_overrides_are_noop(qapp):
    w = _worker()
    w._current_model = _model()
    base = w._compute_v2_history(_cfg(), 400)["ratio"]
    w._current_model = _model({})               # vazio = no-op
    assert np.allclose(base, w._compute_v2_history(_cfg(), 400)["ratio"])
    w._current_model = _model({"nao_existe": 9.9, "L_eff": "lixo"})
    r = w._compute_v2_history(_cfg(), 400)["ratio"]   # invalido ignorado, nao crasha
    assert np.allclose(base, r)
```

- [ ] **Step 2: Rodar e ver falhar** — o 1º teste FALHA (`allclose` — overrides ignorados hoje).
- [ ] **Step 3: Implementar.** Em `_compute_v2_history`, logo APÓS o bloco `geom = JointGeometry(...)` (linha ~1044) e ANTES do bloco de conformação (o `m = getattr(self, '_current_model', None)` da linha ~1051 precisa subir junto ou já estar acima — mover a linha `m = ...` para antes deste bloco se necessário):

```python
        # Geometria com proveniencia do caso (gui_bridge, Plano B 2026-07-10):
        # canal ADITIVO — presente, sobrepoe campos de JointGeometry (L_eff do
        # grip real, A_contact do anel §4.9-11g); ausente/invalido = geometria
        # do config (comportamento anterior bit-identico).
        gov = getattr(m, '_v2_geometry_overrides', None) if m is not None else None
        if isinstance(gov, dict) and gov:
            gfields = ('E', 'A_s', 'L_eff', 'd_2', 'pitch', 'r_bearing', 'A_contact')
            base_g = {f: getattr(geom, f) for f in gfields}
            for k, v in gov.items():
                if k in gfields:
                    try:
                        base_g[k] = float(v)
                    except (TypeError, ValueError):
                        pass                    # valor invalido: ignora o campo
            geom = JointGeometry(**base_g)
```

- [ ] **Step 4: `ast.parse` + rodar** — `python -m pytest tests/test_v2_geometry_overrides.py tests/test_v2_solver_preload.py -q` → verde (regressão do Run intacta).
- [ ] **Step 5: Commit** — `git commit -m "feat(solver): canal aditivo _v2_geometry_overrides no Run V2 (Plano B)"`

---

## Task 4: `ValidationBrowser` — widget de navegação e detalhe

**Files:**
- Create: `src/bolt_analysis_studio/gui/chrome/widgets/validation_browser.py`
- Test: `tests/test_validation_browser.py`

**Interfaces:**
- Consumes: `case_registry.all_records`, `store.ValidationStore`, `report_html.data_points`, matplotlib QtAgg.
- Produces: `ValidationBrowser(store=None, parent=None)` (QWidget) com: árvore `self.tree` (QTreeWidget, top-level = fonte, filho = caso, `Qt.UserRole` = case_id), painel `self.detail` (canvas + labels), botões `btn_open_model, btn_resim, btn_resim_all, btn_report, btn_master`; sinais `open_in_model_requested(str)`, `resim_case_requested(str)`, `resim_all_requested()`, `open_report_requested(str)`, `master_report_requested()`; métodos `populate()`, `current_case_id() -> str|None`, `show_case(case_id)`, `refresh_case(case_id)`.

- [ ] **Step 1: Teste falhando** `tests/test_validation_browser.py`:

```python
def test_browser_populates_sources_and_cases(qapp):
    from bolt_analysis_studio.gui.chrome.widgets.validation_browser import ValidationBrowser
    b = ValidationBrowser()
    n_sources = b.tree.topLevelItemCount()
    assert n_sources >= 14                       # fontes (digitalizadas + legadas)
    total = sum(b.tree.topLevelItem(i).childCount() for i in range(n_sources))
    assert total == 128


def test_selecting_case_shows_detail(qapp):
    from PyQt6.QtCore import Qt
    from bolt_analysis_studio.gui.chrome.widgets.validation_browser import ValidationBrowser
    b = ValidationBrowser()
    item = None
    for i in range(b.tree.topLevelItemCount()):
        src = b.tree.topLevelItem(i)
        for j in range(src.childCount()):
            if src.child(j).data(0, Qt.ItemDataRole.UserRole) == "liu2025_M16_amp0p25":
                item = src.child(j)
    assert item is not None
    b.tree.setCurrentItem(item)
    assert b.current_case_id() == "liu2025_M16_amp0p25"
    assert "MAE" in b.metrics_label.text()
    assert b.btn_open_model.isEnabled()


def test_other_family_disables_open_in_model(qapp):
    from PyQt6.QtCore import Qt
    from bolt_analysis_studio.gui.chrome.widgets.validation_browser import ValidationBrowser
    from bolt_analysis_studio.validation.case_registry import all_records
    other_id = next(r.case_id for r in all_records() if r.family == "other")
    b = ValidationBrowser()
    b.show_case(other_id)
    assert not b.btn_open_model.isEnabled()


def test_signals_fire(qapp):
    from bolt_analysis_studio.gui.chrome.widgets.validation_browser import ValidationBrowser
    b = ValidationBrowser()
    b.show_case("liu2025_M16_amp0p25")
    got = []
    b.open_in_model_requested.connect(got.append)
    b.btn_open_model.click()
    assert got == ["liu2025_M16_amp0p25"]
```

- [ ] **Step 2: Rodar e ver falhar.**
- [ ] **Step 3: Implementar** `validation_browser.py`:

```python
# -*- coding: utf-8 -*-
"""ValidationBrowser — navegador dos 128 casos de validacao (Plano B, spec
2026-07-10 §4): arvore fonte->caso + detalhe (curva dado vs modelo +
decomposicao + metricas + staleness) + acoes. Widget puro: emite sinais; quem
executa e o ValidationController."""
from __future__ import annotations

import numpy as np
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (QHBoxLayout, QLabel, QPushButton, QSplitter,
                             QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget)

from ....validation.case_registry import all_records, record
from ....validation.report_html import NICE, data_points
from ....validation.store import ValidationStore

_DECOMP_COLORS = {"embedding": "#2f6f8f", "creep": "#8f6f2f",
                  "wear": "#b3452c", "rotational_loosening": "#5f8f2f",
                  "thread_fretting": "#7f5fa0", "fatigue": "#a05f5f"}


class ValidationBrowser(QWidget):
    open_in_model_requested = pyqtSignal(str)
    resim_case_requested = pyqtSignal(str)
    resim_all_requested = pyqtSignal()
    open_report_requested = pyqtSignal(str)
    master_report_requested = pyqtSignal()

    def __init__(self, store: ValidationStore = None, parent=None):
        super().__init__(parent)
        self.store = store or ValidationStore()
        self._current_id = None
        self._build_ui()
        self.populate()

    def _build_ui(self):
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Caso", "MAE"])
        self.tree.currentItemChanged.connect(self._on_item)

        # detalhe: canvas matplotlib + metricas + acoes
        from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
        from matplotlib.figure import Figure
        self._fig = Figure(figsize=(5, 4), tight_layout=True)
        self.canvas = FigureCanvasQTAgg(self._fig)
        self.metrics_label = QLabel("Selecione um caso.")
        self.metrics_label.setWordWrap(True)
        self.stamp_label = QLabel("")
        self.btn_open_model = QPushButton("Abrir no Model/Run")
        self.btn_resim = QPushButton("Re-simular caso")
        self.btn_resim_all = QPushButton("Re-simular tudo")
        self.btn_report = QPushButton("Report HTML")
        self.btn_master = QPushButton("Report geral")
        self.btn_open_model.clicked.connect(
            lambda: self._emit(self.open_in_model_requested))
        self.btn_resim.clicked.connect(
            lambda: self._emit(self.resim_case_requested))
        self.btn_resim_all.clicked.connect(self.resim_all_requested.emit)
        self.btn_report.clicked.connect(
            lambda: self._emit(self.open_report_requested))
        self.btn_master.clicked.connect(self.master_report_requested.emit)
        for b in (self.btn_open_model, self.btn_resim, self.btn_report):
            b.setEnabled(False)

        btns = QHBoxLayout()
        for b in (self.btn_open_model, self.btn_resim, self.btn_resim_all,
                  self.btn_report, self.btn_master):
            btns.addWidget(b)
        right = QWidget()
        rl = QVBoxLayout(right)
        rl.addWidget(self.canvas, stretch=1)
        rl.addWidget(self.metrics_label)
        rl.addWidget(self.stamp_label)
        rl.addLayout(btns)
        self.detail = right

        split = QSplitter()
        split.addWidget(self.tree)
        split.addWidget(right)
        split.setStretchFactor(1, 1)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(split)

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
        self.btn_report.setEnabled(True)
        # metricas
        if res is None:
            self.metrics_label.setText(f"{case_id}: nunca simulado — re-simule.")
        elif not res.ok:
            self.metrics_label.setText(f"{case_id}: não simulável — {res.error}")
        else:
            mae = f"{res.mae:.4f}" if res.mae is not None else "—"
            camp = ""
            if rec.gallery_entry is not None:
                camp = f" · campanha {float(rec.gallery_entry['mae']):.4f}"
            self.metrics_label.setText(
                f"MAE {mae}{camp} · RMSE {res.rmse if res.rmse is None else f'{res.rmse:.4f}'}"
                f" · F/F₀ final: modelo {res.final_pred if res.final_pred is None else f'{res.final_pred:.3f}'}"
                f" vs dado {res.final_data if res.final_data is None else f'{res.final_data:.3f}'}")
        stale = self.store.is_stale(case_id)
        stamp = getattr(res, "generated_at", "—") if res else "—"
        self.stamp_label.setText(
            f"gerado em {stamp} · {'DESATUALIZADO (re-simule)' if stale else 'atual'}")
        self._plot(rec, res)

    def refresh_case(self, case_id: str):
        self.populate()
        self.show_case(case_id)

    def _plot(self, rec, res):
        self._fig.clear()
        ax = self._fig.add_subplot(211)
        try:
            dx, dy = data_points(rec)
            if len(dx):
                ax.plot(dx, dy, "o", ms=3, label="dado (artigo)")
        except Exception:
            pass
        if res is not None and res.ok and res.cycles:
            ax.plot(res.cycles, res.ratio, "-", label="modelo")
        ax.set_ylabel("F/F₀"); ax.set_ylim(0, 1.08); ax.legend(fontsize=7)
        ax2 = self._fig.add_subplot(212, sharex=ax)
        if res is not None and res.ok and res.decomp:
            mechs = list(res.decomp)
            ys = [res.decomp[m] for m in mechs]
            ax2.stackplot(res.cycles, *ys, labels=mechs,
                          colors=[_DECOMP_COLORS.get(m, "#888") for m in mechs])
            ax2.legend(fontsize=6, loc="upper left")
        else:
            ax2.text(0.5, 0.5, "sem decomposição — re-simule",
                     ha="center", va="center", transform=ax2.transAxes)
        ax2.set_xlabel("ciclos N"); ax2.set_ylabel("perda F/F₀")
        self.canvas.draw_idle()
```

- [ ] **Step 4: `ast.parse` + rodar** — `python -m pytest tests/test_validation_browser.py -q` → **4 passed**.
- [ ] **Step 5: Commit** — `git commit -m "feat(chrome): ValidationBrowser — arvore 128 casos + detalhe curva/decomposicao (Plano B)"`

---

## Task 5: `ValidationController` — orquestração + re-sim em thread

**Files:**
- Create: `src/bolt_analysis_studio/gui/chrome/controllers/validation_controller.py`
- Test: append em `tests/test_validation_browser.py`

**Interfaces:**
- Consumes: Tasks 2-4; `store/runner/report_html/report(ensure_reports)`; `get_app_state`.
- Produces: `ValidationController(app_state=None, parent=None)` (QObject): atributos `browser` (ValidationBrowser), `store`; sinal `case_opened_in_model(str)`; métodos `viewport_widget() -> QWidget`, `open_in_model(case_id)`, `resimulate(case_ids: list, n_cap=None)` (síncrono se 1 caso curto? NÃO — sempre via `_ResimWorker`; nos testes chama-se `worker.run()` direto); `_ResimWorker(QThread)` com sinais `case_done(str)`, `all_done()`.

- [ ] **Step 1: Teste falhando** — append em `tests/test_validation_browser.py`:

```python
def test_controller_open_in_model_sets_app_state(qapp):
    from bolt_analysis_studio.core.app_state import get_app_state
    from bolt_analysis_studio.gui.chrome.controllers.validation_controller import (
        ValidationController)
    st = get_app_state(); st.new_project()
    c = ValidationController(st)
    got = []
    c.case_opened_in_model.connect(got.append)
    c.open_in_model("liu2025_M16_amp0p25")
    assert st.model is not None and len(st.model.elements) > 0
    assert st.model._v2_tuner_overrides["slip_onset_W"] == 150000.0
    assert "L_eff" in st.model._v2_geometry_overrides
    assert got == ["liu2025_M16_amp0p25"]
    st.new_project()


def test_resim_worker_updates_store(qapp, tmp_path):
    from bolt_analysis_studio.gui.chrome.controllers.validation_controller import (
        _ResimWorker)
    from bolt_analysis_studio.validation.case_registry import all_records
    from bolt_analysis_studio.validation.store import ValidationStore
    store = ValidationStore(path=tmp_path / "s.json")
    rec = min((r for r in all_records()
               if r.family == "transverse" and r.case_class == "full_curve"),
              key=lambda r: r.validation_case.n_cycles)
    done = []
    w = _ResimWorker([rec.case_id], store, n_cap=300)
    w.case_done.connect(lambda cid: done.append(cid))
    w.run()                                       # sincrono no teste (sem .start())
    assert done == [rec.case_id]
    assert store.get(rec.case_id) is not None and store.get(rec.case_id).ok
```

- [ ] **Step 2: Rodar e ver falhar.**
- [ ] **Step 3: Implementar** `validation_controller.py`:

```python
# -*- coding: utf-8 -*-
"""ValidationController — orquestra o modulo Validation do chrome V2 (Plano B):
browser <-> store/runner/reports, re-simulacao em QThread, e "Abrir no
Model/Run" (requisito do professor: casos rodaveis livremente no software)."""
from __future__ import annotations

import webbrowser

from PyQt6.QtCore import QObject, QThread, pyqtSignal

from ....core.app_state import get_app_state
from ....validation.case_registry import record
from ....validation.gui_bridge import build_case_model
from ....validation.report import ensure_reports
from ....validation.report_html import write_reports
from ....validation.runner import simulate_case
from ....validation.store import ValidationStore
from ..widgets.validation_browser import ValidationBrowser


class _ResimWorker(QThread):
    case_done = pyqtSignal(str)
    all_done = pyqtSignal()

    def __init__(self, case_ids, store, n_cap=None, parent=None):
        super().__init__(parent)
        self._ids = list(case_ids)
        self._store = store
        self._n_cap = n_cap

    def run(self):
        for cid in self._ids:
            rec = record(cid)
            if rec is None:
                continue
            self._store.put(simulate_case(rec, n_cap=self._n_cap))
            self._store.save()
            self.case_done.emit(cid)
        self.all_done.emit()


class ValidationController(QObject):
    case_opened_in_model = pyqtSignal(str)

    def __init__(self, app_state=None, parent=None):
        super().__init__(parent)
        self.app_state = app_state or get_app_state()
        self.store = ValidationStore()
        if not self.store.all_ids():
            self.store.seed_from_gallery()
            self.store.save()
        self.browser = ValidationBrowser(store=self.store)
        self._worker = None
        b = self.browser
        b.open_in_model_requested.connect(self.open_in_model)
        b.resim_case_requested.connect(lambda cid: self.resimulate([cid]))
        b.resim_all_requested.connect(self._resim_all)
        b.open_report_requested.connect(self._open_case_report)
        b.master_report_requested.connect(self._open_master)

    def viewport_widget(self):
        return self.browser

    # --- acoes ---
    def open_in_model(self, case_id: str) -> None:
        rec = record(case_id)
        if rec is None:
            return
        try:
            self.app_state.model = build_case_model(rec)
        except ValueError:
            return                                # familia 'other': sem proveniencia
        self.case_opened_in_model.emit(case_id)

    def resimulate(self, case_ids, n_cap=None) -> None:
        if self._worker is not None and self._worker.isRunning():
            return
        self._worker = _ResimWorker(case_ids, self.store, n_cap=n_cap)
        self._worker.case_done.connect(self.browser.refresh_case)
        self._worker.start()

    def _resim_all(self) -> None:
        from ....validation.case_registry import all_records
        self.resimulate([r.case_id for r in all_records() if r.family != "other"])

    def _open_case_report(self, case_id: str) -> None:
        master = write_reports()                  # regenera do store (rapido)
        target = master.parent / "reports" / f"{case_id}.html"
        if target.exists():
            webbrowser.open(target.as_uri())

    def _open_master(self) -> None:
        webbrowser.open(ensure_reports().as_uri())
```

- [ ] **Step 4: `ast.parse` + rodar** — `python -m pytest tests/test_validation_browser.py -q` → **6 passed**.
- [ ] **Step 5: Commit** — `git commit -m "feat(chrome): ValidationController — re-sim em thread + Abrir no Model/Run (Plano B)"`

---

## Task 6: Integração no `ChromeWindow` (Results → Validation) + fim

**Files:**
- Modify: `src/bolt_analysis_studio/gui/chrome/app_window.py`
- Test: `tests/test_chrome_validation_module.py`

**Interfaces:**
- Consumes: `ValidationController` (Task 5), padrão `_center`/docks dos Planos 2-3.
- Produces: módulo **Results** mostra a página Validation; `case_opened_in_model` → `switch_module("Model")`.

- [ ] **Step 1: Teste falhando** `tests/test_chrome_validation_module.py`:

```python
from bolt_analysis_studio.gui.chrome.app_window import ChromeWindow
from bolt_analysis_studio.core.app_state import get_app_state


def test_results_module_shows_validation_browser(qapp):
    w = ChromeWindow()
    w.switch_module("Results")
    assert w._center.currentWidget() is w.validation_controller.browser
    assert not w._palette_dock.isVisibleTo(w)


def test_leaving_results_restores_placeholders(qapp):
    w = ChromeWindow()
    w.switch_module("Results")
    w.switch_module("Analysis")
    assert w._center.currentWidget() is w.viewport


def test_open_in_model_switches_module_and_loads(qapp):
    st = get_app_state(); st.new_project()
    w = ChromeWindow(app_state=st)
    w.switch_module("Results")
    w.validation_controller.open_in_model("liu2025_M16_amp0p25")
    assert w.current_module == "Model"
    assert len(w.model_controller.schematic.elements) > 0
    assert st.model._v2_geometry_overrides["L_eff"] > 0
    st.new_project()
```

- [ ] **Step 2: Rodar e ver falhar.**
- [ ] **Step 3: Editar `app_window.py`** (3 mudanças):

**(a)** Import: `from .controllers.validation_controller import ValidationController`.

**(b)** Em `_build_chrome`, após criar `self.model_controller` e a página do Model:

```python
        # Modulo Validation (Plano B): pagina do browser no stack (sub-mode do
        # Results ate o Plano 5 trazer os plots de Run).
        self.validation_controller = ValidationController(self.app_state)
        self._center.addWidget(self.validation_controller.viewport_widget())
```

**(c)** Em `_wire_signals`: `self.validation_controller.case_opened_in_model.connect(lambda _cid: self.switch_module("Model"))`. Em `switch_module`, ANTES do ramo placeholder, adicionar:

```python
        elif name == "Results":
            # Sub-mode Validation (Plano B): browser dos 128 casos; os plots
            # de Run do Results chegam no Plano 5.
            self._center.setCurrentWidget(self.validation_controller.viewport_widget())
            self._inspector_dock.setWidget(self.inspector)
            self._palette_dock.hide()
```

(estruturar como `if name in self._SCHEMATIC_MODULES: ... elif name == "Results": ... else: ...`).

- [ ] **Step 4: `ast.parse` + rodar** — `python -m pytest tests/test_chrome_validation_module.py tests/test_chrome_model_module.py tests/test_main_window_chrome.py -q` → verde (atenção: `test_all_modules_still_switch` agora passa pelo ramo Results novo).
- [ ] **Step 5: Suítes completas** — chrome inteira (Planos 1-3 + novos) + pacote validation + regressão de domínio (38) → verde.
- [ ] **Step 6: Smoke manual opcional (com display):** `python run_app.py --v2` → módulo Results → selecionar caso → ver curva+decomposição → "Abrir no Model/Run" → módulo Model com o caso → Analysis → Run.
- [ ] **Step 7: STATUS** — `docs/superpowers/plans/2026-07-10-validation-gui-module-STATUS.md`: entregue, números, decisões (sub-mode no Results; canal de geometria aditivo; fidelidade Run vs report e diferenças residuais MEDIDAS — rodar 1 caso pelos 2 caminhos e reportar o delta), limitações (família other; staleness não cobre código do engine), handoff (Plano 4 chrome / adoção configs por-curva). Atualizar CLAUDE.md (linha do pacote validation: + módulo GUI) e memória.
- [ ] **Step 8: Commit** — `git commit -m "feat(chrome): modulo Validation (Results sub-mode) + docs STATUS (Plano B)"`

---

## Self-Review

**Spec coverage:** spec §4 (browser nativo + botões) → Tasks 4-6; re-sim caso/tudo em background → Task 5; abrir report/geral → Task 5; **requisito "rodar livremente"** → Tasks 1-3 (bridge + canal geometria) + Task 6 (fluxo completo); menu V1 já feito no Plano A. ✔
**Placeholder scan:** sem TBD; todos os steps de código com código; comandos com resultado esperado. ✔
**Type consistency:** `material_kwargs_for(rec, inp)` (T1) usado no bridge (T2); `loading_for` (T1) no bridge (T2); `geometry_overrides_for`/`build_case_model` (T2) no controller (T5) e teste (T6); `_v2_geometry_overrides` (T2 produz, T3 consome, T6 verifica); `ValidationBrowser` sinais/botões (T4) conectados no controller (T5); `viewport_widget()` (T5) no `_center` (T6). ✔
**Riscos anotados:** (a) `build_model` pode exigir ajustes de preset (T2 Step 4 manda ajustar só o bridge); (b) fidelidade Run vs report tem diferenças residuais conhecidas (F0 vs %yield do config, cap 100k do Run) — o STATUS deve MEDIR o delta num caso, não presumir zero; (c) QThread nos testes sempre `.run()` síncrono; (d) `test_all_modules_still_switch` cobre o ramo Results novo.
