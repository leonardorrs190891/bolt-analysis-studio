def test_browser_populates_sources_and_cases(qapp):
    from bolt_analysis_studio.gui.chrome.widgets.validation_browser import ValidationBrowser
    b = ValidationBrowser()
    n_sources = b.tree.topLevelItemCount()
    assert n_sources >= 14                       # fontes (digitalizadas + legadas)
    total = sum(b.tree.topLevelItem(i).childCount() for i in range(n_sources))
    assert total >= 114                          # 114 comparaveis + casos USER


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


def test_all_listed_cases_are_openable(qapp):
    # diretriz 2026-07-11: o conjunto so contem comparaveis => todo caso
    # listado e simulavel e abrivel no Model (a guarda de 'other' vira defesa)
    from bolt_analysis_studio.gui.chrome.widgets.validation_browser import ValidationBrowser
    from bolt_analysis_studio.validation.case_registry import all_records
    assert all(r.family != "other" for r in all_records())
    b = ValidationBrowser()
    b.show_case(all_records()[0].case_id)
    assert b.btn_open_model.isEnabled()


def test_signals_fire(qapp):
    from bolt_analysis_studio.gui.chrome.widgets.validation_browser import ValidationBrowser
    b = ValidationBrowser()
    b.show_case("liu2025_M16_amp0p25")
    got = []
    b.open_in_model_requested.connect(got.append)
    b.btn_open_model.click()
    assert got == ["liu2025_M16_amp0p25"]


def test_browser_has_intake_buttons(qapp):
    from bolt_analysis_studio.gui.chrome.widgets.validation_browser import ValidationBrowser
    b = ValidationBrowser()
    assert "Importar" in b.btn_import.text()      # rotulado como passo "3."
    got = []
    b.copy_prompt_requested.connect(lambda: got.append(1))
    b.btn_prompt_copy.click()
    assert got == [1]


def test_intake_panel_is_prominent(qapp):
    # pedido do professor 2026-07-10: a secao de intake deve ficar CLARA e
    # DESTACADA — painel proprio no topo, explicando o fluxo com qualquer IA
    from bolt_analysis_studio.gui.chrome.widgets.validation_browser import ValidationBrowser
    b = ValidationBrowser()
    assert b.intake_group is not None
    assert "IA" in b.intake_group.title()
    txt = b.intake_explainer.text()
    assert "qualquer" in txt.lower()               # qualquer ferramenta de IA
    assert "bascase" in txt.lower() or ".bascase.json" in txt
    # os 3 botoes moram DENTRO do painel destacado
    for btn in (b.btn_prompt_copy, b.btn_prompt_save, b.btn_import):
        assert btn.parent() is not None
        p = btn.parent()
        while p is not None and p is not b.intake_group:
            p = p.parent()
        assert p is b.intake_group
    # feedback visual ao copiar
    assert b.intake_status.text() == ""
    b.set_intake_status("Prompt copiado.")
    assert "copiado" in b.intake_status.text()


def test_chrome_help_menu_copies_intake_prompt(qapp):
    from bolt_analysis_studio.gui.chrome.app_window import ChromeWindow
    from PyQt6.QtWidgets import QApplication
    w = ChromeWindow()
    help_menu = next(a.menu() for a in w.menuBar().actions()
                     if a.text() == "Ajuda")
    act = next(a for a in help_menu.actions() if "intake" in a.text().lower())
    QApplication.clipboard().setText("")
    act.trigger()
    assert "bascase_version" in QApplication.clipboard().text()


def test_controller_import_and_copy_prompt(qapp, tmp_path, monkeypatch):
    import json
    from tests.test_user_cases import VALID
    from bolt_analysis_studio.core.app_state import get_app_state
    from bolt_analysis_studio.gui.chrome.controllers.validation_controller import (
        ValidationController)
    from bolt_analysis_studio.validation import user_cases
    from bolt_analysis_studio.validation.case_registry import (all_records,
                                                               refresh_records)
    from bolt_analysis_studio.validation.store import ValidationStore
    monkeypatch.setattr(user_cases, "USER_CASES_DIR", tmp_path / "uc")
    st = get_app_state(); st.new_project()
    # store INJETADO (temporario). Sem isto o controller abre o store CANONICO e
    # `import_case` grava `ensaio_teste_m12` no arquivo versionado do repo —
    # medido em 2026-07-28: a suite completa subia o store de 203 p/ 204
    # registros, e o vazamento era invisivel porque o registro de um caso REAL
    # sai byte-identico. Ver o guarda em test_validation_store.py.
    c = ValidationController(st, store=ValidationStore(path=tmp_path / "s.json"))
    p = tmp_path / "novo.bascase.json"
    p.write_text(json.dumps(VALID), encoding="utf-8")
    cid = c.import_case(p, prefit=False)           # sem prefit no teste (rapido)
    assert cid is not None
    assert any(r.source == "USER" for r in all_records())
    c.copy_prompt()
    from PyQt6.QtWidgets import QApplication
    assert "bascase_version" in QApplication.clipboard().text()
    refresh_records(); st.new_project()


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
    # 250000 = valor adotado no PR-9 (iter.4); o pin segue o adopted_configs
    assert st.model._v2_tuner_overrides["slip_onset_W"] == 250000.0
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
