"""Testes do Explorador Interativo de Variaveis (New_Theory/build_variable_explorer.py).

Carrega o gerador por caminho (nao e um modulo do pacote). conftest.py ja poe
src/ no sys.path.
"""
import importlib.util
import pathlib
import sys
from html.parser import HTMLParser

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
GEN = ROOT / "New_Theory" / "build_variable_explorer.py"


def _load():
    spec = importlib.util.spec_from_file_location("build_variable_explorer", GEN)
    mod = importlib.util.module_from_spec(spec)
    # registrar em sys.modules antes de exec: dataclasses (Py3.14) resolve as
    # anotacoes adiadas (from __future__ import annotations) via sys.modules[cls.__module__].
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def _parse_ok(html):
    HTMLParser().feed(html)   # nao levanta => bem-formado o bastante


# ---------------------------------------------------------------- T1
def test_spec_names_are_real_fields():
    mod = _load()
    from bolt_analysis_studio.numerical.dynamic_stiffness_analyzer import JointMaterial
    fields = set(JointMaterial.__dataclass_fields__)
    for s in mod.VARIABLE_SPECS:
        assert s.name in fields, f"{s.name} nao e campo de JointMaterial"
    names = [s.name for s in mod.VARIABLE_SPECS]
    assert len(names) == len(set(names)), "spec duplicado"


def test_baselines_build_valid_payloads():
    mod = _load()
    for bid in ("transverse", "axial", "creep"):
        p = mod.BASELINES[bid]()
        assert set(p["geom"]) == {"A_s", "L_eff", "d_2", "pitch", "r_bearing", "A_contact"}
        assert set(p["loading"]) == {"F0_init", "F_amp", "theta", "freq", "N", "delta_amp", "D_init"}
        assert set(p["segments"]) == {"N_I", "N_II"}


# ---------------------------------------------------------------- T2
def test_sweep_variable_moves_curve():
    mod = _load()
    from bolt_analysis_studio.numerical.dynamic_stiffness_analyzer import JointMaterial
    s = mod.VarSpec(
        name="emb_depth", symbol="d", unit="m", group="embedding",
        category="physical",
        context={"baseline": "transverse", "overrides": {}},
        physics_pt="x", physics_en="x", equation="x",
        sweep=(5e-6, 60e-6, 6, "lin"))
    res = mod.sweep_variable(s)
    assert res["default"] == JointMaterial().emb_depth
    assert len(res["curves"]) == 6
    for c in res["curves"]:
        # dados nativos p/ json.dumps
        assert isinstance(c["value"], float)
        assert isinstance(c["ratio"][0], float)
        assert c["ratio"][0] == 1.0
        assert all(r <= 1.0001 for r in c["ratio"])
    finals = [c["ratio"][-1] for c in res["curves"]]
    assert max(finals) - min(finals) > 1e-3   # slider vivo


def test_sweep_values_choices_passthrough():
    mod = _load()
    s = mod.VarSpec(
        name="k_tr_mode", symbol="", unit="", group="slip_regime", category="mode",
        context={"baseline": "transverse", "overrides": {}},
        physics_pt="x", physics_en="x", equation="x",
        choices=["axial_frac", "bending"])
    assert mod.sweep_values(s) == ["axial_frac", "bending"]
    res = mod.sweep_variable(s)
    assert res["baseline_idx"] is None   # nao-numerico
    assert len(res["curves"]) == 2


# ---------------------------------------------------------------- T3
def test_render_variable_page_smoke():
    mod = _load()
    s = mod.VarSpec(
        name="emb_depth", symbol="d", unit="m", group="embedding",
        category="physical",
        context={"baseline": "transverse", "overrides": {}},
        physics_pt="Assentamento plastico das asperezas.",
        physics_en="Plastic settling of asperities.",
        equation="delta_emb(N)=d(1-e^{-N/N_emb})",
        sweep=(5e-6, 60e-6, 6, "lin"),
        refs=[("VDI 2230", "VDI 2230", "vdi2230")],
        related=["N_emb"])
    # segundo spec p/ o TOC/nav ter um "proximo"
    other = mod.VarSpec(
        name="C_creep", symbol="C", unit="m", group="creep", category="physical",
        context={"baseline": "creep", "overrides": {}},
        physics_pt="x", physics_en="x", equation="x", sweep=(1e-12, 1e-10, 3, "log"))
    res = mod.sweep_variable(s)
    html = mod.render_variable_page(s, res, all_specs=[s, other], cur_index=0)
    _parse_ok(html)
    assert "<canvas" in html
    assert "const DATA" in html
    assert 'data-l="pt"' in html and 'data-l="en"' in html
    assert 'data-lang="pt"' in html
    assert "Assentamento plastico" in html and "Plastic settling" in html
    assert 'class="side"' in html               # sidebar/TOC presente
    assert 'class="tocitem' in html             # itens do sumario
    assert "var_C_creep.html" in html           # link no TOC / nav
    assert "var_N_emb.html" in html             # cross-link related
    assert "<input" in html or "<select" in html


def test_render_mode_uses_select():
    mod = _load()
    s = mod.VarSpec(
        name="k_tr_mode", symbol="", unit="", group="slip_regime", category="mode",
        context={"baseline": "transverse", "overrides": {}},
        physics_pt="a", physics_en="a", equation="e",
        choices=["axial_frac", "bending"])
    res = mod.sweep_variable(s)
    html = mod.render_variable_page(s, res, all_specs=[s], cur_index=0)
    _parse_ok(html)
    assert "<select" in html
    assert "axial_frac" in html and "bending" in html


def test_sidebar_marks_current_and_groups():
    mod = _load()
    a = mod.VarSpec(name="emb_depth", symbol="d", unit="m", group="embedding",
                    category="physical", context={"baseline": "transverse", "overrides": {}},
                    physics_pt="x", physics_en="x", equation="e", sweep=(5e-6, 60e-6, 3, "lin"))
    b = mod.VarSpec(name="mu_thread", symbol="mu", unit="-", group="friction",
                    category="physical", context={"baseline": "transverse", "overrides": {}},
                    physics_pt="x", physics_en="x", equation="e", sweep=(0.05, 0.3, 3, "lin"))
    html = mod._sidebar_html([a, b], current_name="mu_thread")
    assert 'href="var_mu_thread.html" data-name="mu_thread"' in html
    assert "current" in html
    # o item atual e o marcado
    assert 'class="tocitem current" href="var_mu_thread.html"' in html


def test_tier_controls_and_classification():
    mod = _load()
    # classificacao de tier
    def mk(cat, neg=False):
        return mod.VarSpec(name="x", symbol="", unit="", group="embedding", category=cat,
                           context={"baseline": "transverse", "overrides": {}},
                           physics_pt="x", physics_en="x", equation="e",
                           sweep=(0, 1, 3, "lin"), negligible=neg)
    assert mod._tier(mk("physical")) == "fisica"
    assert mod._tier(mk("form")) == "avancada"
    assert mod._tier(mk("mode")) == "avancada"
    assert mod._tier(mk("numerical")) == "rara"
    assert mod._tier(mk("form", neg=True)) == "rara"      # negligible -> rara
    assert mod._tier(mk("physical", neg=True)) == "rara"
    # o sidebar traz as 3 caixas de tier + data-tier nos itens
    a = mod.VarSpec(name="emb_depth", symbol="d", unit="m", group="embedding",
                    category="physical", context={"baseline": "transverse", "overrides": {}},
                    physics_pt="x", physics_en="x", equation="e", sweep=(5e-6, 60e-6, 3, "lin"))
    html = mod._sidebar_html([a], current_name="emb_depth")
    assert html.count('class="tierbox"') == 3
    assert 'data-tier="fisica"' in html


def test_all_specs_have_valid_tier():
    mod = _load()
    for s in mod.VARIABLE_SPECS:
        assert mod._tier(s) in ("fisica", "avancada", "rara")


# ---------------------------------------------------------------- Fundamentos (concept pages)
def test_concept_pages_present_and_unique():
    mod = _load()
    slugs = [p["slug"] for p in mod.CONCEPT_PAGES]
    # 15 desde 2026-07-28: entrou "manual", a pagina-hub da F6/S6 (3 volumes em
    # docs/MANUAL_BAS_V2/ + as 5 figuras geradas do store). E' a PRIMEIRA da
    # lista de proposito — a ordem define a barra lateral e a navegacao
    # anterior/proxima, e o hub e' a porta de entrada.
    assert len(slugs) == 15
    assert len(slugs) == len(set(slugs))
    assert slugs[0] == "manual"
    assert {"review", "equations", "references", "gallery", "anatomy",
            "glossary", "usage", "coverage", "manual"} <= set(slugs)
    for p in mod.CONCEPT_PAGES:
        for k in ("slug", "nav_pt", "nav_en", "title_pt", "title_en", "body"):
            assert p.get(k), f"{p.get('slug')} sem {k}"


def test_concept_pages_render_and_normalize():
    mod = _load()
    for p in mod.CONCEPT_PAGES:
        html = mod.render_concept_page(p, mod.VARIABLE_SPECS)
        _parse_ok(html)
        assert "&lt;p&gt;" not in html          # sem duplo-escape
        assert "Fundamentos" in html            # grupo no sidebar
        assert 'data-tier="base"' in html       # Fundamentos sempre visivel
        if p.get("widget"):
            assert 'id="cw"' in html            # widget montado


def test_concept_widget_data():
    mod = _load()
    # f0_sweep: 5 curvas preditas, F0 crescente
    wf = mod._widget_data("f0_sweep")
    assert wf["kind"] == "plot" and len(wf["curves"]) == 5
    assert all(c["ratio"][0] == 1.0 for c in wf["curves"])
    # decomp: mecanismos somam ~ (1 - ratio) no fim
    wd = mod._widget_data("decomp")
    assert wd["kind"] == "stack"
    stacked = sum(wd["mechs"][m][-1] for m in wd["mechs"])
    total = 1 - wd["ratio"][-1]
    assert abs(stacked - total) < 0.05, (stacked, total)
    # runaway: 2 curvas, arresto termina acima do runaway
    wr = mod._widget_data("runaway")
    assert len(wr["curves"]) == 2
    assert wr["curves"][1]["ratio"][-1] >= wr["curves"][0]["ratio"][-1]
    # energy: barras + total
    we = mod._widget_data("energy")
    assert we["kind"] == "bars" and len(we["items"]) == 4


def test_predict_interpolation_demo():
    """Demo 'nao e interpolacao': a interpolacao (ajustada em 0.25mm, aplicada sem
    mudar) acerta la e piora longe; o modelo fica baixo em todas as amplitudes."""
    mod = _load()
    wd = mod._widget_data("predict_liu2025")
    if wd is None:                                   # store de validacao ausente -> degrada
        import pytest
        pytest.skip("store de validacao ausente")
    assert wd["kind"] == "overlay"
    by = {s["label_pt"]: s for s in wd["series"]}
    ref, far = by.get("±0.25 mm"), by.get("±0.80 mm")
    assert ref and far, list(by)
    assert ref["interp_mae"] < 0.01                  # interpolacao perfeita onde foi ajustada
    assert far["interp_mae"] > ref["interp_mae"] + 0.1   # piora muito longe do ajuste
    assert far["mae"] < far["interp_mae"]            # modelo melhor que a interpolacao la
    assert len(ref["interp_r"]) == len(ref["model_N"])   # interpolante alinhado ao x do modelo


# ---------------------------------------------------------------- T4
def test_build_writes_files(tmp_path):
    mod = _load()
    specs = [
        mod.VarSpec(name="emb_depth", symbol="d", unit="m", group="embedding",
                    category="physical",
                    context={"baseline": "transverse", "overrides": {}},
                    physics_pt="a. b", physics_en="a. b", equation="e",
                    sweep=(5e-6, 60e-6, 4, "lin")),
        mod.VarSpec(name="C_creep", symbol="C", unit="m/dec", group="creep",
                    category="physical",
                    context={"baseline": "creep", "overrides": {}},
                    physics_pt="b. c", physics_en="b. c", equation="e",
                    sweep=(1e-12, 1e-10, 4, "log")),
    ]
    paths = mod.build(specs, tmp_path)
    assert (tmp_path / "index.html").exists()
    assert (tmp_path / "var_emb_depth.html").exists()
    assert (tmp_path / "var_C_creep.html").exists()
    idx = (tmp_path / "index.html").read_text(encoding="utf-8")
    _parse_ok(idx)
    assert "var_emb_depth.html" in idx and "var_C_creep.html" in idx
    # encadeamento prev/next
    pg = (tmp_path / "var_emb_depth.html").read_text(encoding="utf-8")
    assert "var_C_creep.html" in pg   # next
    # reports completos por caso + info do artigo importada (degrada s/ store)
    rep = tmp_path / "reports" / "liu2025_M16_amp0p25.html"
    if rep.exists():
        rh = rep.read_text(encoding="utf-8")
        assert 'id="secart"' in rh and "Trial matrix" in rh   # info do artigo no report
        assert '<a href="#secart">' in rh                     # entrada no indice
        assert 'nav.toc{display:block!important' in rh         # indice visivel inline


# ---------------------------------------------------------------- T22 (cobertura + conteudo)
def test_all_fields_covered():
    mod = _load()
    missing = mod.missing_fields()
    assert not missing, f"campos de JointMaterial sem VarSpec: {sorted(missing)}"
    # 1:1 entre specs e campos: cobertura total (missing vazio) + sem specs orfaos.
    # Sem numero magico -> nao quebra quando JointMaterial ganha um campo novo.
    assert len(mod.VARIABLE_SPECS) == len(mod.all_field_names())


def test_specs_valid_and_content_normalizes():
    mod = _load()
    mod.validate_specs()   # nao levanta
    # toda pagina renderiza e nao deixa duplo-escape na prosa
    for s in mod.VARIABLE_SPECS:
        res = mod.sweep_variable(s)
        html = mod.render_variable_page(s, res, all_specs=mod.VARIABLE_SPECS, cur_index=0)
        _parse_ok(html)
        assert "&lt;p&gt;" not in html, f"duplo-escape sobrou em {s.name}"
        assert "&amp;middot;" not in html, f"entidade duplo-escapada em {s.name}"


def test_non_negligible_sliders_are_live():
    """Todo campo nao-negligible deve mover a curva (metrica ponto-a-ponto,
    ciente de cliff). Marca dead sliders."""
    mod = _load()
    dead = []
    for s in mod.VARIABLE_SPECS:
        if s.negligible:
            continue
        res = mod.sweep_variable(s)
        if mod.curve_liveness(res) < 1e-3:
            dead.append(s.name)
    assert not dead, f"sliders mortos (nao-negligible, liveness<1e-3): {dead}"


# ---------------------------------------------------------------- T23 (estudos de caso)
def test_study_pages_render():
    """Estudos de caso por fonte: renderizam, bem-formados, sem duplo-escape,
    com grupo no sidebar + cards modelo-vs-dado; figuras referenciadas (quando
    existem) apontam p/ arquivos reais em paper_figures/."""
    import re
    mod = _load()
    studies = mod._study_sources()
    assert studies, "nenhum estudo de caso gerado"
    assert all(s["source"] != "USER" for s in studies)      # exemplo excluido
    figdir = ROOT / "New_Theory" / "variable_explorer" / "paper_figures"
    saw_note = False
    for sd in studies:
        html = mod.render_study_page(sd, mod.VARIABLE_SPECS)
        _parse_ok(html)
        assert "&lt;p&gt;" not in html, f"duplo-escape em {sd['slug']}"
        assert "Estudos de caso" in html                    # grupo no sidebar
        assert "GDATA" in html and "gal-card" in html        # cards modelo-vs-dado
        assert "reports/" in html, f"sem link de report em {sd['slug']}"   # report completo por card
        for fn in re.findall(r'paper_figures/([\w.\-]+\.png)', html):
            assert (figdir / fn).exists(), f"figura ausente: {fn} ({sd['slug']})"
        if sd.get("note"):
            assert "Informações do artigo" in html, f"sem info do artigo em {sd['slug']}"
            saw_note = True
    assert saw_note, "nenhum estudo renderizou a nota de aparato (info do artigo)"


def test_md_to_html_basic():
    """Conversor MD->HTML das notas: headings, tabela pipe, lista, bold/code/link."""
    mod = _load()
    md = ("## Apparatus\n\n- item **um**\n- item `dois`\n\n"
          "| a | b |\n|---|---|\n| 1 | 2 |\n\n[x](https://e.com) fim.")
    h = mod._md_to_html(md)
    assert "<h3>Apparatus</h3>" in h                  # ## -> h3 (aninhado sob o h2 do painel)
    assert "<ul><li>item <b>um</b></li>" in h and "<code>dois</code>" in h
    assert "<table" in h and "<th>a</th>" in h and "<td>1</td>" in h
    assert '<a href="https://e.com"' in h
    assert "&lt;script" not in h                     # escapou
