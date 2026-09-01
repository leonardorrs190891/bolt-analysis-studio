def _res(case_id, mae, cycles=None, ratio=None, final_pred=0.9, final_data=0.85):
    from bolt_analysis_studio.validation.runner import CaseResult
    return CaseResult(case_id=case_id, ok=True, mae=mae,
                      cycles=cycles or [0, 500, 1000],
                      ratio=ratio or [1.0, 0.95, 0.90],
                      final_pred=final_pred, final_data=final_data,
                      generated_at="t", engine_fingerprint="f")


def test_classify_labels():
    from bolt_analysis_studio.validation.case_registry import all_records
    from bolt_analysis_studio.validation.error_budget import classify_case
    recs = [r for r in all_records() if r.source != "USER"]
    # no_piso: caso YANG (piso 0.081) com mae 0.09
    yang = next(r for r in recs if r.source == "YANG_2019")
    assert classify_case(yang, _res(yang.case_id, 0.09))["label"] == "no_piso"
    # gap_adocao: galeria boa, canonico muito pior
    gal = next(r for r in recs if r.gallery_entry is not None
               and float(r.gallery_entry["mae"]) < 0.05)
    c = classify_case(gal, _res(gal.case_id,
                                max(2.5 * float(gal.gallery_entry["mae"]), 0.12)))
    assert c["label"] == "gap_adocao"
    # sem_simulacao: resultado com erro (qualquer record)
    from bolt_analysis_studio.validation.runner import CaseResult
    bad = CaseResult(case_id=recs[0].case_id, ok=False, error="x",
                     generated_at="t", engine_fingerprint="f")
    assert classify_case(recs[0], bad)["label"] == "sem_simulacao"


def test_budget_aggregates_and_writes(tmp_path, monkeypatch):
    from bolt_analysis_studio.validation import error_budget as eb
    monkeypatch.setattr(eb, "BUDGET_PATH", tmp_path / "eb.json")
    out = eb.error_budget()
    assert out["totals"]["n"] >= 114
    assert sum(sum(v.values()) for v in out["by_source"].values()) == out["totals"]["n"]
    assert (tmp_path / "eb.json").exists()
    import json
    saved = json.loads((tmp_path / "eb.json").read_text(encoding="utf-8"))
    assert saved["totals"] == out["totals"]
