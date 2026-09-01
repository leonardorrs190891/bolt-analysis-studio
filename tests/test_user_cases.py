import json

VALID = {
    "bascase_version": 1, "name": "Ensaio teste M12",
    "description": "junker sintetico",
    "test": {"bolt_size": "M12x1.75", "grip_mm": 30.0, "preload_N": 30000.0,
             "loading_type": "TRANSVERSE", "control_mode": "displacement",
             "delta_amplitude_mm": 0.5, "F_amplitude_N": None,
             "frequency_Hz": 12.5, "n_cycles": 400, "mu": 0.18,
             "lubricated": False, "rz_class": "Rz10-40",
             "material_pair": "aço/aço", "notes": ""},
    "curve": {"x_unit": "cycles", "y_unit": "F_kN",
              "points": [[0, 30.0], [100, 28.5], [250, 27.0], [400, 26.1]]},
    "provenance": {"generated_by": "teste", "date": "2026-07-10"},
    "prefit": {},
}


def _write(tmp_path, data, name="caso.bascase.json"):
    p = tmp_path / name
    p.write_text(json.dumps(data), encoding="utf-8")
    return p


def test_validate_ok_and_errors(tmp_path):
    from bolt_analysis_studio.validation.user_cases import validate_bascase
    assert validate_bascase(VALID) == []
    bad = json.loads(json.dumps(VALID))
    bad["test"]["delta_amplitude_mm"] = 0
    bad["curve"]["points"] = [[0, 1.0]]
    errs = validate_bascase(bad)
    assert any("delta_amplitude_mm" in e for e in errs)
    assert any("points" in e for e in errs)


def test_import_normalizes_curve_and_writes_canonical(tmp_path):
    from bolt_analysis_studio.validation.user_cases import import_user_case
    rec = import_user_case(_write(tmp_path, VALID), dest_dir=tmp_path / "uc")
    assert rec.source == "USER" and rec.family == "transverse"
    assert rec.case_class == "full_curve" and rec.csv_path.exists()
    import numpy as np
    d = np.genfromtxt(rec.csv_path, delimiter=",", skip_header=1)
    assert abs(d[0, 1] - 1.0) < 1e-9              # kN normalizado p/ ratio
    assert (rec.csv_path.parent / rec.csv_path.name.replace(
        ".csv", ".bascase.json")).exists()
    case = rec.validation_case
    assert case.initial_preload_N == 30000.0
    assert case.source.name == "USER"
    # inputs do usuario com proveniencia 'user'
    from bolt_analysis_studio.validation.inputs import inputs_for
    inp = inputs_for(case)
    assert inp["grip_mm"] == {"value": 30.0, "prov": "user"}
    assert inp["mu"]["value"] == 0.18 and inp["mu"]["prov"] == "user"


def test_user_records_and_registry_integration(tmp_path, monkeypatch):
    from bolt_analysis_studio.validation import user_cases
    from bolt_analysis_studio.validation.case_registry import (all_records,
                                                               refresh_records)
    monkeypatch.setattr(user_cases, "USER_CASES_DIR", tmp_path / "uc")
    user_cases.import_user_case(_write(tmp_path, VALID))
    refresh_records()
    recs = all_records()
    users = [r for r in recs if r.source == "USER"]
    assert len(users) == 1
    core = [r for r in recs if r.source != "USER"]
    # Mesmo pin robusto de test_validation_registry.py::
    # test_registry_covers_all_cases_with_unique_ids (ver comentario la):
    # full-checkout = 202 (180 herdados + 22 Rodada 5); desconta o que
    # estiver de fato ausente entre os 3 CSVs UFU nao-versionados e a pasta
    # "BAS_V2_papers/F. Rodada 5 (limitacoes 2026-07-16)/" (T11 ledger),
    # mas exige exatidao no resto.
    UFU_IDS = {"UFU_5A_preload_decay", "UFU_13A_first_preload_decay",
               "UFU_13A_def_preload_decay"}
    R5_SOURCES = {"ZHANG_2018", "ZHANG_2019", "LIU_2020_WEAR"}
    n_ufu = sum(1 for r in core if r.case_id in UFU_IDS)
    n_r5 = sum(1 for r in core if r.source in R5_SOURCES)
    # 207 = 205 (+3 fig14 do LU, P4 2026-07-31) + 2 replicas YANG_2021
    # (Fig. 6b2/6b3, prereg 2026-07-31-yang2021-replicas-0p6). O desconto de
    # lacunas voltou a ser CODIGO (a versao anterior o deixou no comentario,
    # o que quebraria num clone sem os CSVs UFU/pasta F).
    # 209 desde 2026-08-01 (+2 da Fig. 6 do ROUSSEAU, recuperacao)
    expected = 209 - (len(UFU_IDS) - n_ufu) - (22 - n_r5)
    assert len(core) == expected
    refresh_records()                              # limpa p/ os demais testes
    monkeypatch.undo()
    refresh_records()


def test_cli_import(tmp_path):
    import os
    import subprocess
    import sys
    from pathlib import Path
    src_dir = str(Path(__file__).resolve().parents[1] / "src")
    env = {**os.environ,
           "PYTHONPATH": src_dir + os.pathsep + os.environ.get("PYTHONPATH", ""),
           "BAS_USER_CASES_DIR": str(tmp_path / "uc")}
    p = _write(tmp_path, VALID)
    out = subprocess.run(
        [sys.executable, "-m", "bolt_analysis_studio.validation.report",
         "--import", str(p), "--cap", "300", "--out", str(tmp_path / "html"),
         "--store", str(tmp_path / "store.json")],
        capture_output=True, text=True, env=env)
    assert out.returncode == 0, out.stderr
    assert "ensaio_teste_m12" in out.stdout.lower()


def test_runner_simulates_user_case(tmp_path, monkeypatch):
    from bolt_analysis_studio.validation import user_cases
    from bolt_analysis_studio.validation.case_registry import refresh_records
    from bolt_analysis_studio.validation.runner import simulate_case
    monkeypatch.setattr(user_cases, "USER_CASES_DIR", tmp_path / "uc")
    rec = user_cases.import_user_case(_write(tmp_path, VALID))
    res = simulate_case(rec, n_cap=400)
    assert res.ok and res.mae is not None
    assert res.decomp                              # decomposicao presente
    # limpa o cache do registry: sem isto o `ensaio_teste_m12` importado aqui
    # SOBREVIVE ao teardown do monkeypatch (que restaura USER_CASES_DIR mas nao
    # invalida o cache) e vaza para os arquivos seguintes. Foi essa combinacao
    # que fez `test_validation_browser` grava-lo no store canonico (2026-07-28).
    refresh_records()
