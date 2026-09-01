import json


def test_prompt_is_self_contained():
    from bolt_analysis_studio.validation.intake_prompt import (INTAKE_PROMPT,
                                                               SCHEMA_EXAMPLE)
    p = INTAKE_PROMPT
    # perguntas do ensaio (bloco test do schema)
    for termo in ("pré-carga", "frequência", "ciclos", "controle",
                  "deslocamento", "força", "amplitude", "lubrifica",
                  "rugosidade", "grip", "parafuso"):
        assert termo in p.lower() or termo in p, termo
    # regras de normalizacao da curva
    for termo in ("F/F₀", "kN", "csv", "txt"):
        assert termo in p or termo.lower() in p.lower(), termo
    assert "bascase_version" in p                     # schema embutido
    assert "APENAS o JSON" in p or "apenas o JSON" in p
    json.loads(SCHEMA_EXAMPLE)                        # exemplo parseia


def test_docs_file_matches_prompt():
    from pathlib import Path
    from bolt_analysis_studio.validation.intake_prompt import INTAKE_PROMPT
    md = Path("src/bolt_analysis_studio/docs/INTAKE_PROMPT.md").read_text(encoding="utf-8")
    assert INTAKE_PROMPT.strip() in md                # doc = prompt + cabecalho
