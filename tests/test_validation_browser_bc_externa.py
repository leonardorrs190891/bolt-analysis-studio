"""O browser de casos mostra a CONDIÇÃO DE CONTORNO EXTERNA — e a limpa ao trocar de curva.

## Por que este arquivo existe

A carga axial externa do `ECCLES_2010` percorreu **três camadas** até ficar visível, e cada
uma precisou de conserto próprio:

1. **não existia** — as 10 curvas devolviam `to_solver_config()` idêntico, com a variável que
   o paper *varre* fora do modelo (consertado em `53996b7`, camadas C1/C2);
2. **existia e não aparecia no report** — `grep -c external_axial report_html.py` dava zero
   (consertado em `e0082b3`, com as 204 páginas sem axial saindo byte-idênticas);
3. **aparecia no report e não no app** — nenhum arquivo de `gui/` lia o campo. É o que este
   teste cobre.

⚠️ **O que a invisibilidade custou, medido:** no browser, a
`eccles2010_fig3_typical_no_axial` e a `eccles2010_fig6_annotated_4kN_axial` ficavam
**indistinguíveis**. Foi exatamente essa sobreposição que produziu, naquela fonte, provas de
exceção dizendo *"sobreposição axial"*, um bloqueio de pareamento por *"cegueira à carga
axial"* e um *"ensemble de 4 réplicas"* no teste de premissa F5 — porque **aos olhos do
modelo elas eram** réplicas.

## O defeito que o próprio teste pegou

A 1ª versão do widget usava só `setVisible(False)` para esconder o rótulo em curva sem
axial. `setVisible` **não limpa o texto**: ao alternar da `fig8b` (700 N) para a `fig3` (sem
axial), o rótulo guardava os 700 N da curva anterior. Enquanto a visibilidade for honrada
ninguém vê — mas tema, re-layout ou contexto offscreen quebram essa garantia, e então o app
exibe a carga axial da **curva errada**. **Dado obsoleto é pior que dado ausente**, e é por
isso que o conserto foi `clear()` antes de esconder, não um ajuste de visibilidade.
"""

from __future__ import annotations

import pytest

from bolt_analysis_studio.gui.chrome.widgets.validation_browser import ValidationBrowser

# (case_id, tem BC externa) — as 6 axiais do ECCLES contra baselines da MESMA
# fonte e uma curva de outra fonte (controle de vazamento entre fontes).
_CASOS = [
    ("eccles2010_fig6_annotated_4kN_axial", True),
    ("eccles2010_fig7b_axial_1p1kN_constant", True),
    ("eccles2010_fig7c_axial_2p7kN_constant", True),
    ("eccles2010_fig7d_axial_3p1kN_constant", True),
    ("eccles2010_fig8b_axial_0p7kN_intermittent", True),
    ("eccles2010_fig8d_axial_3p5kN_intermittent", True),
    ("eccles2010_fig3_typical_no_axial", False),
    ("eccles2010_fig7a_no_axial", False),
    ("eccles2010_fig8a_no_axial_baseline1", False),
    ("eccles2010_fig8c_no_axial_baseline2", False),
    ("liu2025_M16_amp0p8", False),
    ("bauer2024_M8_fig6_rep1", False),
]


@pytest.fixture(scope="module")
def browser(qapp):
    return ValidationBrowser()


@pytest.mark.parametrize("case_id,tem_bc", _CASOS)
def test_rotulo_aparece_exatamente_onde_ha_carga_axial(browser, case_id, tem_bc):
    browser.show_case(case_id)
    texto = browser.bc_label.text()
    assert bool(texto) == tem_bc, (
        f"{case_id}: esperava BC externa={tem_bc}, rótulo={texto!r}"
    )
    if tem_bc:
        assert "carga axial" in texto
        # o MODO importa: constant x intermittent decide se o termo é estático
        # ou pulsado, e a nota de aparato distingue os dois.
        assert ("constant" in texto) or ("intermittent" in texto), (
            f"{case_id}: o rótulo não diz o MODO — {texto!r}")


def test_o_valor_exibido_e_o_do_registry(browser):
    """O número na tela é o do `ValidationCase`, não um literal no widget."""
    from bolt_analysis_studio.validation.case_registry import record
    for case_id, tem_bc in _CASOS:
        if not tem_bc:
            continue
        browser.show_case(case_id)
        esperado = float(record(case_id).validation_case.external_axial_N)
        assert f"{esperado:.0f} N" in browser.bc_label.text(), (
            f"{case_id}: rótulo {browser.bc_label.text()!r} não traz {esperado:.0f} N")


def test_trocar_de_curva_LIMPA_o_rotulo():
    """⚠️ O defeito de origem: `setVisible(False)` não limpa o texto.

    Alternar de uma curva COM carga para uma SEM tem de zerar o rótulo. Sem isto o
    app exibe a carga axial da curva ANTERIOR sempre que a visibilidade não for
    honrada (tema, re-layout, offscreen) — e dado obsoleto é pior que dado ausente,
    porque parece informação.
    """
    from PyQt6.QtWidgets import QApplication
    assert QApplication.instance() is not None, "precisa da fixture qapp do conftest"
    w = ValidationBrowser()
    w.show_case("eccles2010_fig8b_axial_0p7kN_intermittent")
    assert "700 N" in w.bc_label.text()
    w.show_case("eccles2010_fig3_typical_no_axial")
    assert w.bc_label.text() == "", (
        "rótulo manteve o texto da curva anterior: "
        f"{w.bc_label.text()!r} — use clear(), não só setVisible(False)")
    # e volta a aparecer, com o valor NOVO (não o antigo em cache)
    w.show_case("eccles2010_fig6_annotated_4kN_axial")
    assert "4000 N" in w.bc_label.text()


def test_as_duas_curvas_que_eram_indistinguiveis_agora_diferem(browser):
    """O par que motivou tudo: baseline sem axial × mesma condição com 4 kN.

    Se este teste falhar, o browser voltou a mostrar as duas iguais — e é dessa
    igualdade que saíram as provas de exceção de "sobreposição axial".
    """
    browser.show_case("eccles2010_fig3_typical_no_axial")
    sem = browser.bc_label.text()
    browser.show_case("eccles2010_fig6_annotated_4kN_axial")
    com = browser.bc_label.text()
    assert sem != com and sem == "" and "4000 N" in com
