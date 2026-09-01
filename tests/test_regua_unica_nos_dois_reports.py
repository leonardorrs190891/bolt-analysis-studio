"""Os DOIS geradores de report por caso julgam pela MESMA régua.

## O defeito, medido

`case_report_html` tem dois chamadores — `report_html.write_reports` (que escreve
`New_Theory/validation_html/reports/`) e `build_variable_explorer` (que escreve
`New_Theory/variable_explorer/reports/`). O parâmetro `lim_sd` carrega o limite EFETIVO da
3ª perna daquela fonte (regra D1: `max(META_SRES, piso medido)`); omitido, ele cai no
**global 0,025**.

O `write_reports` passava; o explorador **não**. Resultado medido em 2026-08-23, com os dois
conjuntos gerados do MESMO store: **22 das 207 páginas discordavam** na distância à origem
e, em várias, na **perna que manda**.

| curva | explorador | documento mestre |
|---|---|---|
| `bauer2024_M8_fig6_rep4` | 3,73× | 1,71× |
| `chu2026ti_D0p4mm_F0_49kN_test2` | 7,64× | 6,46× |
| `eccles2010_fig8a_no_axial_baseline1` | σ_res manda, 1,58× | res.máx manda, 1,32× |

⚠️ **A direção do erro não salva o defeito.** A página do explorador era *injustamente
severa* (régua mais apertada que a vigente), não frouxa — então nada foi aprovado
indevidamente. Mas dois artefatos publicados discordando sobre a MESMA curva é defeito de
qualquer sinal: quem abre um dos dois não tem como saber que o outro diz outra coisa. E a
própria docstring de `case_report_html` já nomeava isso: *"a página do caso e o documento
mestre têm de julgar pela MESMA régua — meia-régua em cada lugar foi o defeito de
2026-07-29."* O mecanismo existia; o segundo chamador não o usava.

## Por que o teste é ESTRUTURAL e não compara os HTML

Comparar as páginas geradas exigiria que elas existissem — num clone fresco, ou antes da
primeira geração, o teste passaria por vacuidade (ou seria skip permanente), que é o pior
dos mundos: guarda que parece verde sem medir nada. O invariante durável é **todo chamador
de `case_report_html` passa `lim_sd`** — isso é verificável no fonte, sempre.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]

# Os dois geradores. Se um terceiro aparecer, acrescente-o aqui — e ele nasce
# obrigado a passar o limite, que é o ponto.
_CHAMADORES = [
    RAIZ / "src" / "bolt_analysis_studio" / "validation" / "report_html.py",
    RAIZ / "New_Theory" / "build_variable_explorer.py",
]


def _chamadas_de(arquivo: Path):
    """Toda chamada a `case_report_html` no arquivo, com os kwargs usados."""
    arvore = ast.parse(arquivo.read_text(encoding="utf-8"))
    fora = []
    for no in ast.walk(arvore):
        if not isinstance(no, ast.Call):
            continue
        f = no.func
        nome = (f.attr if isinstance(f, ast.Attribute)
                else f.id if isinstance(f, ast.Name) else None)
        if nome != "case_report_html":
            continue
        fora.append((no.lineno, {k.arg for k in no.keywords if k.arg}))
    return fora


@pytest.mark.parametrize("arquivo", _CHAMADORES, ids=lambda p: p.name)
def test_todo_chamador_passa_o_limite_por_fonte(arquivo):
    """`lim_sd` omitido = a página julga a 3ª perna pelo global, não pelo D1."""
    assert arquivo.exists(), f"{arquivo} não existe — o chamador mudou de lugar?"
    chamadas = _chamadas_de(arquivo)
    # a definição da função também aparece em report_html.py; chamadas é o que
    # importa, e tem de haver ao menos uma em cada arquivo desta lista
    assert chamadas, (
        f"{arquivo.name} não chama mais `case_report_html` — se o gerador foi "
        f"movido, mova a entrada de `_CHAMADORES` com ele, senão esta guarda "
        f"passa a vigiar o nada")
    sem = [ln for ln, kw in chamadas if "lim_sd" not in kw]
    assert not sem, (
        f"{arquivo.name}: chamada(s) a `case_report_html` sem `lim_sd` na(s) "
        f"linha(s) {sem}. Sem ele a página cai no META_SRES global e passa a "
        f"discordar do documento mestre — medido em 2026-08-23: 22 das 207 "
        f"páginas divergiam na distância à origem e algumas na PERNA QUE MANDA. "
        f"O valor vem de `limite_sres(fonte, _pisos_medidos(...))`, nunca de "
        f"uma constante.")


def test_o_default_do_parametro_segue_sendo_o_GLOBAL():
    """`lim_sd=None` -> global. É isso que torna a omissão perigosa e silenciosa.

    Se um dia o default virar "o piso da fonte", este teste falha e obriga a
    reescrever a guarda acima — porque aí omitir o parâmetro deixaria de ser
    defeito, e vigiar a omissão viraria ruído.
    """
    import inspect
    import bolt_analysis_studio.validation.report_html as rh
    sig = inspect.signature(rh.case_report_html)
    assert "lim_sd" in sig.parameters, "o parâmetro `lim_sd` desapareceu"
    assert sig.parameters["lim_sd"].default is None, (
        "o default de `lim_sd` deixou de ser None — a omissão já não cai no "
        "global, então a guarda `test_todo_chamador_passa_o_limite_por_fonte` "
        "precisa ser repensada")


def test_o_helper_do_limite_e_o_CANONICO():
    """Ninguém recalcula `max(0.025, piso)` à mão — chama `limite_sres`.

    Reimplementar a regra é como a triagem de 2026-07-30 publicou um censo
    inteiro sob a régua vencida: o número sai, parece plausível, e mede outra
    coisa.
    """
    import bolt_analysis_studio.validation.report_html as rh
    assert callable(rh.limite_sres)
    for arquivo in _CHAMADORES:
        fonte = arquivo.read_text(encoding="utf-8")
        # o padrão proibido: max( META_SRES ... ) escrito à mão junto de um piso
        assert "max(META_SRES, piso" not in fonte.replace(" ", ""), (
            f"{arquivo.name} recalcula o limite à mão — use `limite_sres`")
