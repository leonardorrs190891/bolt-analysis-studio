"""Invariantes do modulo de robustez do artigo (New_Theory/robustness_checks.py).

1. `veredito` com os limites NOMINAIS reproduz `rh._tripe_ok` + `rh.limite_sres`
   curva a curva — a varredura fala a lingua do report, ou nao vale nada;
2. `_constantes_da_curva` ignora `prov`/`verdict` e per_case de IRMAS — so o
   que muda a predicao desta curva conta como mudanca;
3. `t_cfg_curva` devolve a data da ULTIMA mudanca das constantes da curva numa
   historia sintetica (criacao, mudanca de irma, mudanca propria, so-prov).
"""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "New_Theory"))

import robustness_checks as RB                           # noqa: E402
import bolt_analysis_studio.validation.report_html as rh  # noqa: E402


@pytest.fixture(scope="module")
def dados():
    import build_annex_docx as A
    comp, res, pisos, store, todos, res_all = A.carrega()
    return comp, res, pisos


def test_veredito_nominal_reproduz_o_report_curva_a_curva(dados):
    comp, res, pisos = dados
    nom = (rh.META_MAX, rh.META_MAE, rh.META_SRES)
    for r in comp:
        rr = res[r.case_id]
        esperado = rh._tripe_ok(rr, rh.limite_sres(r.source, pisos))
        obtido = RB.veredito(rr, *nom, RB.piso_fonte(pisos, r.source))
        assert bool(esperado) == bool(obtido), r.case_id


def test_constantes_da_curva_ignora_prov_e_irmas():
    entry = {"pack": "PACK", "cfg": {"C_creep": 1e-11},
             "per_case": {"t10": {"emb_um": 4.0}, "t12": {"emb_um": 6.0}},
             "prov": {"C_creep": "read from the paper"}, "verdict": "ok"}
    c10 = RB._constantes_da_curva(entry, "rousseau2025_steel_t10")
    assert "prov" not in c10 and "verdict" not in c10
    assert c10["per_case"] == {"t10": {"emb_um": 4.0}}
    e2 = dict(entry, prov={"C_creep": "other text"}, verdict="changed")
    assert RB._constantes_da_curva(e2, "rousseau2025_steel_t10") == c10
    e3 = dict(entry, per_case={"t10": {"emb_um": 4.0}, "t12": {"emb_um": 9.0}})
    assert RB._constantes_da_curva(e3, "rousseau2025_steel_t10") == c10   # irma mudou
    e4 = dict(entry, per_case={"t10": {"emb_um": 5.0}, "t12": {"emb_um": 6.0}})
    assert RB._constantes_da_curva(e4, "rousseau2025_steel_t10") != c10   # a propria


def test_t_cfg_curva_historia_sintetica():
    base = {"cfg": {"C_creep": 1e-11}, "per_case": {"t10": {"emb_um": 4.0}}, "prov": {}}
    versoes = [
        ("2026-07-08", "a", {}),                                    # grupo nao existe
        ("2026-07-10", "b", {"G": base}),                           # criacao -> muda
        ("2026-07-12", "c", {"G": dict(base, per_case={"t10": {"emb_um": 4.0},
                                                        "t12": {"emb_um": 1.0}})}),  # irma
        ("2026-07-15", "d", {"G": dict(base, per_case={"t10": {"emb_um": 5.0},
                                                        "t12": {"emb_um": 1.0}})}),  # propria
        ("2026-07-20", "e", {"G": dict(base, per_case={"t10": {"emb_um": 5.0},
                                                        "t12": {"emb_um": 1.0}},
                                       prov={"x": "text"})}),      # so prov
    ]
    assert RB.t_cfg_curva(versoes, "G", "src_t10") == "2026-07-15"
    assert RB.t_cfg_curva(versoes, "G", "src_t12") == "2026-07-12"
    assert RB.t_cfg_curva(versoes, "H", "src_t10") is None
