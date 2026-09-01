def test_registry_covers_all_cases_with_unique_ids():
    from bolt_analysis_studio.validation.case_registry import all_records
    recs = all_records()
    core = [r for r in recs if r.source != "USER"]   # USER = casos importados
    # Full-checkout (todos os CSVs presentes) = 202: 180 herdados (114 + 64
    # Rodada 4, 2026-07-14) + 22 Rodada 5 (Zhang2018/2019 + Liu2020_Wear,
    # 2026-07-17, fatia 7 do plano L1-L7). Duas lacunas de CSV CONHECIDAS
    # reduzem esse numero SEM erro (case_registry degrada p/ final_ratio-e
    # -descarta, spec §3): os 3 CSVs UFU nao-versionados (gitignored, dado
    # de lab) e a pasta ainda-nao-commitada "BAS_V2_papers/F. Rodada 5
    # (limitacoes 2026-07-16)/" de onde os 22 casos novos leem (T11 ledger:
    # o commit de wiring 9e3dd67 trouxe so o codigo, nao a pasta). O pin
    # abaixo mede quantas dessas DUAS lacunas conhecidas estao de fato
    # ausentes neste ambiente e exige EXATIDAO no resto -- falha se
    # qualquer OUTRA fonte wired sumir por acidente (o caso que a diretriz
    # do professor pede para nao tolerar).
    UFU_IDS = {"UFU_5A_preload_decay", "UFU_13A_first_preload_decay",
               "UFU_13A_def_preload_decay"}
    R5_SOURCES = {"ZHANG_2018", "ZHANG_2019", "LIU_2020_WEAR"}
    n_ufu = sum(1 for r in core if r.case_id in UFU_IDS)
    n_r5 = sum(1 for r in core if r.source in R5_SOURCES)
    # 205 desde 2026-07-31: +3 corridas longas da Fig.14a do LU_2024 (P4 do
    # plano lu2024_plano_melhoria.md, digitalizadas com gate de round-trip).
    # 207 desde 2026-07-31 (noite): +2 replicas 0.6mm-8kN do YANG_2021
    # (Fig. 6b2/6b3, prereg 2026-07-31-yang2021-replicas-0p6-prereg.md,
    # G1 round-trip 1.2% vs Tabela 3; ambas no tripe por merito).
    # 209 desde 2026-08-01: +2 da Fig. 6 do ROUSSEAU_2025 (recuperacao
    # pos-erratum; condicao NOVA 0.2mm/3.5kN nos dois materiais — o HDPE
    # entrou no tripe por predicao zero-refit).
    expected = 209 - (len(UFU_IDS) - n_ufu) - (22 - n_r5)
    assert len(core) == expected, (
        f"len(core)={len(core)} != {expected} -- uma fonte wired sumiu? "
        "(a ausencia dos 3 CSVs UFU e/ou da pasta F ja e' descontada acima)")
    ids = [r.case_id for r in recs]
    assert len(set(ids)) == len(ids)


def test_classification_and_families():
    from bolt_analysis_studio.validation.case_registry import all_records
    recs = all_records()
    by_class = {}
    for r in recs:
        by_class.setdefault(r.case_class, []).append(r)
    assert len(by_class["full_curve"]) >= 110         # digitalizados + UFU c/ CSV
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
