def test_registry_covers_all_cases_with_unique_ids():
    from bolt_analysis_studio.validation.case_registry import all_records
    recs = all_records()
    core = [r for r in recs if r.source != "USER"]   # USER = casos importados
    # 206 desde 2026-09-04, e agora e' numero EXATO em vez de conta com
    # desconto. A conta antiga partia de 209 e subtraia duas lacunas conhecidas
    # de CSV: os 3 casos de bancada, cujos CSVs nao eram versionados, e a pasta
    # da Rodada 5, que podia faltar no checkout. A primeira deixou de ser
    # lacuna — aqueles casos sairam do projeto por inteiro naquela data, e
    # descontar do total quem ja' nao esta' no total contaria duas vezes. A
    # segunda virou verificacao explicita abaixo: se a pasta sumir, o teste
    # aponta a pasta, e nao um total misterioso.
    #
    # Historico do 209: 205 em 2026-07-31 (+3 corridas longas da Fig.14a do
    # LU_2024), 207 na mesma noite (+2 replicas 0.6mm-8kN do YANG_2021) e 209
    # em 2026-08-01 (+2 da Fig. 6 do ROUSSEAU_2025, pos-erratum).
    R5_SOURCES = {"ZHANG_2018", "ZHANG_2019", "LIU_2020_WEAR"}
    n_r5 = sum(1 for r in core if r.source in R5_SOURCES)
    assert n_r5 == 22, (
        f"Rodada 5 com {n_r5} casos, esperados 22 — a pasta "
        f"'BAS_V2_papers/F. Rodada 5 (limitacoes 2026-07-16)/' sumiu do "
        f"checkout?")
    assert len(core) == 206, (
        f"len(core)={len(core)} != 206 — uma fonte cabeada sumiu?")
    ids = [r.case_id for r in recs]
    assert len(set(ids)) == len(ids)


def test_classification_and_families():
    from bolt_analysis_studio.validation.case_registry import all_records
    recs = all_records()
    by_class = {}
    for r in recs:
        by_class.setdefault(r.case_class, []).append(r)
    assert len(by_class["full_curve"]) >= 110         # digitalizados + âncora interna c/ CSV
    assert "final_ratio" not in by_class              # removidos (diretriz 2026-07-11)
    fams = {r.family for r in recs}
    assert {"transverse", "axial", "creep"} <= fams
    assert "other" not in fams                        # nao-simulaveis removidos
    axial = [r for r in recs if r.family == "axial"]
    assert all(r.validation_case.transverse_displacement_mm == 0 for r in axial)


def test_gallery_matching_and_caveats():
    from bolt_analysis_studio.validation.case_registry import all_records
    recs = all_records()
    with_gallery = [r for r in recs if r.gallery_entry is not None]
    # 82 na galeria − 4 zhang2006 (curvas SEM ValidationCase estruturado;
    # lacuna de dados registrada no STATUS, nao do registry)
    assert len(with_gallery) == 78
    fract = [r for r in recs if any("fratura" in c for c in r.caveats)]
    assert fract                                       # caudas de fratura marcadas


def test_record_lookup_and_apparatus_note():
    from bolt_analysis_studio.validation.case_registry import all_records, record
    recs = all_records()
    r0 = next(r for r in recs if r.gallery_entry is not None)
    assert record(r0.case_id) is not None and record(r0.case_id).case_id == r0.case_id
    noted = [r for r in recs if r.apparatus_note_path]
    assert noted and all(n.exists() for n in {r.apparatus_note_path for r in noted})
