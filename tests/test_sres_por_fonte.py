# -*- coding: utf-8 -*-
"""3ª perna com piso POR FONTE (D1) — ✅ ADOTADO em 2026-07-30.

Prereg: `docs/superpowers/specs/2026-07-29-sigma-res-por-fonte-prereg.md`,
gates 5/5; adoção = decisão do professor em sessão de 2026-07-30 (registro no
comentário da flag em `report_html.py`). Reverter = `git revert` do commit de
adoção — a flag e toda a fiação são inertes com False, e o teste de reversão
limpa abaixo garante isso.

A regra: `σ_res ≤ max(0,025 ; piso_σ da fonte)`. O `max` é o que garante que ela
**nunca aperte** — sem ele, fontes de piso baixo ganhariam limite MENOR que o
global e a "melhoria" reprovaria curvas hoje aprovadas (medido: piso puro dá
76/203 contra 105/203 de hoje).

Estes testes prendem as duas coisas que podem dar errado em silêncio:
inércia com a flag desligada, e os gates do prereg com ela ligada.
"""
from __future__ import annotations

import pytest


def _mod():
    from bolt_analysis_studio.validation import report_html
    return report_html


def _res(mae, maxerr, sd):
    from bolt_analysis_studio.validation.runner import CaseResult
    return CaseResult(case_id="x", ok=True, mae=mae, maxerr=maxerr,
                      resid_std=sd)


# ------------------------------------------------------------------ inércia

def test_flag_ADOTADA_em_2026_07_30():
    """D1 ADOTADO em 2026-07-30 — decisão do professor em sessão ("faça tudo que
    temos que fazer", dada após duas exposições de que D1 era o único bloqueio
    da calibração), commit de adoção com o G5 cumprido (docs re-sincronizados
    no mesmo commit). Se este teste falhar, ou a adoção foi revertida (aí
    reverta TAMBÉM os documentos vivos — git revert do commit faz os dois) ou
    alguém desligou a flag de lado."""
    assert _mod()._SRES_POR_FONTE is True


def test_limite_e_o_global_quando_a_flag_esta_desligada(monkeypatch):
    """A reversão tem de ser limpa: com a flag OFF, `limite_sres` devolve o
    global para TODO mundo e a fiação inteira (censo, 3D, páginas de caso,
    payload) fica bit-idêntica ao pré-D1."""
    m = _mod()
    monkeypatch.setattr(m, "_SRES_POR_FONTE", False)
    pisos = {"por_fonte": {"JCSR_2023": (0.3, 0.4, 0.2214)}}
    assert m.limite_sres("JCSR_2023", pisos) == m.META_SRES
    assert m.limite_sres("JCSR_2023", None) == m.META_SRES
    assert m.limite_sres("FONTE_INEXISTENTE", pisos) == m.META_SRES


def test_tripe_ok_sem_override_e_identico_ao_de_antes():
    """`lim_sd=None` tem de reproduzir exatamente a regra global."""
    m = _mod()
    casos = [(0.01, 0.02, 0.001, True), (0.01, 0.02, 0.026, False),
             (0.06, 0.02, 0.001, False), (0.01, 0.11, 0.001, False),
             (m.META_MAE, m.META_MAX, m.META_SRES, True)]
    for mae, mx, sd, esperado in casos:
        assert m._tripe_ok(_res(mae, mx, sd)) is esperado
        assert m._tripe_ok(_res(mae, mx, sd), None) is esperado


def test_sem_sigma_res_continua_nao_julgavel_com_qualquer_limite():
    m = _mod()
    assert m._tripe_ok(_res(0.01, 0.02, None)) is None
    assert m._tripe_ok(_res(0.01, 0.02, None), 0.5) is None


# ------------------------------------------- a regra, com a flag simulada ligada

@pytest.fixture
def ligada(monkeypatch):
    monkeypatch.setattr(_mod(), "_SRES_POR_FONTE", True)
    return _mod()


def test_o_max_nunca_aperta(ligada):
    """Piso ABAIXO do global não pode baixar o limite — é o falsificador F3 do
    prereg (um `min` no lugar do `max` inverteria a regra em silêncio)."""
    m = ligada
    baixo = {"por_fonte": {"QUIETA": (0.01, 0.02, 0.004)}}
    assert m.limite_sres("QUIETA", baixo) == m.META_SRES
    alto = {"por_fonte": {"RUIDOSA": (0.2, 0.3, 0.2214)}}
    assert m.limite_sres("RUIDOSA", alto) == pytest.approx(0.2214)


def test_fonte_sem_piso_cai_no_global_e_nao_em_estimativa(ligada):
    """G3: estimar piso onde não há réplica reprova a adoção. Seis fontes reais
    estão nessa situação (LU_2024 entre elas, a pior do conjunto)."""
    m = ligada
    pisos = {"por_fonte": {"OUTRA": (0.2, 0.3, 0.19)}}
    assert m.limite_sres("LU_2024", pisos) == m.META_SRES


def test_gates_do_prereg_no_store(ligada):
    """G1 (monotonia, bloqueante) e G2 (mérito declarado) medidos no store real.
    G1 é o gate que mata a adoção: nenhuma curva pode SAIR do tripé."""
    m = ligada
    from bolt_analysis_studio.validation.case_registry import all_records
    from bolt_analysis_studio.validation.store import ValidationStore
    st = ValidationStore()
    comp = []
    for r in all_records():
        if not m.caso_comparavel(r.source, r.case_id):
            continue
        res = st.get(r.case_id)
        if res and res.ok and res.mae is not None and res.maxerr is not None:
            comp.append((r, res))
    if len(comp) < 100:
        pytest.skip("store incompleto neste checkout")
    pisos = m._pisos_medidos([(r.source, res) for r, res in comp])
    hoje = {r.case_id for r, res in comp if m._tripe_ok(res) is True}
    novo = {r.case_id for r, res in comp
            if m._tripe_ok(res, m.limite_sres(r.source, pisos)) is True}
    # G1: monotonia estrita
    assert not (hoje - novo), (
        f"G1 REPROVA: saíram do tripé {sorted(hoje - novo)} — a regra apertou, "
        f"o que só é possível se o `max` de `limite_sres` foi quebrado")
    # G2: o ganho é de método, não de contagem — 19 das 20 já eram exceção
    # ASSINADA NO MOMENTO DA ADOÇÃO. Depois da retirada de 2026-07-30 essas 19
    # vivem em `_EXCECOES_RETIRADAS_D1` (não mais nas ativas), então o conjunto
    # certo para ESTE gate é a união: comparar só com as ativas faria o próprio
    # ato de retirar as assinaturas "inflar" o ganho de 1 para 20 — a retirada
    # não muda o mérito medido na adoção, só a contabilidade.
    ganho = novo - hoje
    assinadas_na_adocao = set(m._EXCECOES) | set(m._EXCECOES_RETIRADAS_D1)
    ja = {c for c in ganho if c in assinadas_na_adocao}
    assert len(ganho) - len(ja) <= 2, (
        f"o ganho REAL saltou para {len(ganho)-len(ja)} curvas não cobertas por "
        f"assinatura; o prereg mediu 1. Re-leia G2 antes de adotar.")
    # F3: ninguém aprovado acima do próprio piso
    for r, res in comp:
        if r.case_id in novo and res.resid_std is not None:
            assert res.resid_std <= m.limite_sres(r.source, pisos) + 1e-12


def test_piso_por_fonte_e_estavel_entre_leituras(ligada):
    """F2 do prereg: se o piso não for estável ao ser recomputado, ele não pode
    ser limite. A família é lida do `config_used`, não do nome do arquivo — duas
    leituras do mesmo store têm de dar o mesmo piso."""
    m = ligada
    from bolt_analysis_studio.validation.case_registry import all_records
    from bolt_analysis_studio.validation.store import ValidationStore
    st = ValidationStore()
    pares = [(r.source, st.get(r.case_id)) for r in all_records()
             if st.get(r.case_id) is not None]
    if len(pares) < 100:
        pytest.skip("store incompleto neste checkout")
    a = m._pisos_medidos(pares)["por_fonte"]
    b = m._pisos_medidos(list(reversed(pares)))["por_fonte"]
    assert set(a) == set(b), "o conjunto de fontes com piso mudou com a ordem"
    for src in a:
        assert a[src][2] == pytest.approx(b[src][2], abs=1e-12), (
            f"piso de {src} depende da ORDEM de leitura ({a[src][2]} vs "
            f"{b[src][2]}) — F2: piso instável não pode ser limite")
