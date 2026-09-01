def test_roundtrip_and_staleness(tmp_path):
    from bolt_analysis_studio.validation.runner import CaseResult, engine_fingerprint
    from bolt_analysis_studio.validation.store import ValidationStore
    st = ValidationStore(path=tmp_path / "store.json")
    res = CaseResult(case_id="x", ok=True, mae=0.05,
                     generated_at="2026-07-10T00:00:00",
                     engine_fingerprint=engine_fingerprint())
    st.put(res); st.save()
    st2 = ValidationStore(path=tmp_path / "store.json")
    assert st2.get("x").mae == 0.05
    assert st2.is_stale("x") is False
    stale = CaseResult(case_id="y", ok=True, engine_fingerprint="deadbeef0000")
    st2.put(stale)
    assert st2.is_stale("y") is True              # fingerprint diverge
    assert st2.is_stale("nao-existe") is True     # ausente = stale


def test_seed_from_gallery(tmp_path):
    from bolt_analysis_studio.validation.store import ValidationStore
    st = ValidationStore(path=tmp_path / "store.json")
    n = st.seed_from_gallery()
    # 78 = records com entrada de galeria (82 - 4 zhang2006 sem ValidationCase)
    assert n == 78
    seeded = st.get("liu2025_M16_amp0p25")
    assert seeded is not None and seeded.ok
    assert seeded.mae is not None
    assert seeded.decomp == {}                    # seed nao tem decomposicao
    assert seeded.engine_fingerprint == "gallery-seed"
    assert st.is_stale("liu2025_M16_amp0p25")     # seed e' sempre stale (honesto)


def test_store_canonico_nao_tem_id_fora_do_registry():
    """O store VERSIONADO só pode conter casos que o registry conhece.

    Guarda-corpo de 2026-07-28. O que ele pega: escrita no store canônico por
    quem não devia. Achado real — `ValidationController` abria
    `ValidationStore()` (canônico) sem costura de injeção, então
    `test_validation_browser::test_controller_import_and_copy_prompt` gravava
    `ensaio_teste_m12` no arquivo do repo; a suíte completa subia 203 -> 204
    registros e o número entrava nos censos.

    Por que a invariante é a CERTA e não só um remendo do sintoma: o vazamento
    era INVISÍVEL quando o caso importado era real (o registro sai
    byte-idêntico, então nem o md5 acusava). O id fora do registry é o único
    rastro observável da classe inteira de escritas indevidas. Para um usuário
    de verdade a invariante continua valendo: importar um caso grava o
    `.bascase.json`, e aí o registry passa a conhecê-lo.

    O S2 declarou esta higiene fechada em 2026-07-27 medindo os arquivos de
    teste ISOLADOS — e isolados eles não poluem mesmo. A poluição só aparece na
    INTERAÇÃO (test_user_cases deixa o caso no cache do registry; o browser
    escreve). Gate medido em conjunto errado passa.
    """
    import json
    from bolt_analysis_studio.validation.case_registry import all_records
    from bolt_analysis_studio.validation.inputs import repo_root
    p = (repo_root() / "Models" / "CALIBRATION_AND_VALIDATION"
         / "validation_store.json")
    if not p.exists():                            # checkout sem o store: nada a checar
        return
    ids = set(json.loads(p.read_text(encoding="utf-8")))
    conhecidos = {r.case_id for r in all_records()}
    intrusos = sorted(ids - conhecidos)
    assert not intrusos, (
        f"o store canônico ganhou {len(intrusos)} id(s) que o registry não "
        f"conhece: {intrusos}. Alguém escreveu no store versionado — procure "
        f"por ValidationStore() sem `path=` em teste ou script.")
