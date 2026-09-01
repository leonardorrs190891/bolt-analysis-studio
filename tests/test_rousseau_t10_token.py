# -*- coding: utf-8 -*-
"""Blindagem de token da adocao ROUSSEAU steel_t10 (2026-08-19).

`steel_t10` e' substring de `steel_t10_amp0p2` e o matcher per_case do runner
aplica o PRIMEIRO token que casa NA ORDEM DO DICT (break). A adocao depende de
a entrada vazia `steel_t10_amp0p2: {}` vir ANTES do pacote `steel_t10` — este
teste fixa o invariante (se alguem reordenar o JSON, falha aqui, nao em
silencio na metrica da irma).
"""
from bolt_analysis_studio.validation.runner import _adopted_overrides


def _inputs(cid):
    # a camada que resolve o per_case e' _adopted_overrides (nao inputs_for)
    return _adopted_overrides("ROUSSEAU_2025", {}, case_id=cid)


def test_pacote_aplica_na_steel_t10():
    ov = _inputs("rousseau2025_steel_t10")
    assert ov.get("loose_rate_mode") == "graded_scrit"
    assert abs(ov.get("free_spin_kin", 0.0) - 0.7195) < 1e-12
    assert ov.get("emb_depth") == 0.0
    assert ov.get("C_creep") == 0.0


def test_amp0p2_casa_a_propria_entrada():
    # A irma amp0p2 casa a PROPRIA entrada primeiro (mesma mecanica da
    # blindagem original; desde 2026-08-19 21:4x ela carrega o pacote
    # proprio da adocao fig6-theta em vez de {}).
    ov = _inputs("rousseau2025_steel_t10_amp0p2")
    assert ov.get("loose_rate_mode") == "graded_scrit"
    assert abs(ov.get("free_spin_kin", 0.0) - 0.9283) < 1e-12
    assert abs(ov.get("k_loose_graded", 0.0) - 0.01729) < 1e-12
    # ela NAO recebe os campos exclusivos do pacote da steel_t10
    assert "emb_depth" not in {k: v for k, v in ov.items() if v == 0.0 and k == "emb_depth"} or ov.get("emb_depth") != 0.0
    assert "slip_onset_W" not in ov
    # o emb_um=1.0 do GRUPO continua valendo para ela (nao o 0.0 da t10)
    assert abs(ov.get("emb_depth", 0.0) - 1.0e-6) < 1e-12


def test_ordem_do_dict_no_json():
    # O invariante de ORDEM em si: a chave vazia vem antes do pacote.
    import json
    import pathlib
    p = pathlib.Path(__file__).resolve().parents[1] / "New_Theory" / "adopted_configs.json"
    cfg = json.loads(p.read_text(encoding="utf-8"))
    pc = cfg["sources"]["ROUSSEAU_2025"]["cfg"]["per_case"]
    keys = list(pc.keys())
    assert keys.index("steel_t10_amp0p2") < keys.index("steel_t10")
    # desde a adocao fig6-theta a entrada carrega o pacote da amp0p2 (nao {})
    assert pc["steel_t10_amp0p2"].get("loose_rate_mode") == "graded_scrit"


def test_demais_irmas_nao_casam_nenhum_token():
    # hdpe_t12 e hdpe_t10 sairam da lista em 2026-08-19 (21:4x-21:5x): tem
    # pacotes PROPRIOS no grupo ROUSSEAU_HDPE (preregs rousseau-hdpe-t1{2,0}-
    # particao). A hdpe_t10_amp0p2 fica: blindada pela entrada-vazia
    # (token hdpe_t10 e' substring dela — mesma mecanica da steel_t10).
    for cid in ("rousseau2025_steel_t12", "rousseau2025_steel_t14",
                "rousseau2025_hdpe_t14", "rousseau2025_hdpe_t10_amp0p2"):
        ov = _inputs(cid)
        assert "loose_rate_mode" not in ov, cid
        assert "free_spin_kin" not in ov, cid
