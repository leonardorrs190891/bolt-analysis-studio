"""Carga axial externa do ECCLES: input real (C1/C2) + piso anulável FALSIFICADO (C3).

Prereg: `docs/superpowers/specs/2026-08-21-eccles-axial-tres-camadas-prereg.md`.

## O que este arquivo protege

**C1/C2 — o input que faltava.** Até 2026-08-21 as 10 curvas do `ECCLES_2010` devolviam
`to_solver_config()` **idêntico** (`initial_preload=15000`, `transverse_force=195000` em
todas), inclusive nas SEIS que trazem a carga axial no próprio nome. A variável que o paper
**varre** não entrava no modelo, e as 6 axiais eram simuladas como as baselines. Isso
explicava de uma vez por que elas falham, por que as provas de exceção dizem *"sobreposição
axial"* (a sobreposição era **literal**) e por que o teste de premissa F5 lia a `fig7` como
ensemble de 4 réplicas — aos olhos do modelo elas **eram**.

**C3 — a forma, e ela está FALSIFICADA.** A nota de aparato especifica o achado central do
paper: o piso residual é *"externally imposed and can also DEMAND the state fall BELOW where
it would otherwise arrest"*. Implementei `ax_floor_override` para anular o piso e o **G3
reprovou em 4 doses** — o alvo (`fig7d`) PIORA 2,4× e os controles pioram junto.

⚠️ **A razão da falsificação é o que este teste guarda:** os pisos vigentes do ECCLES já
DECRESCEM com a carga axial (`fig7b` 0,232 → `fig7c` 0,182 → `fig7d` 0,137, contra
1,1 / 2,7 / 3,1 kN), e a `prov` deles é `proxy-de-desaceleracao-de-cauda (fitado-this-rig)`.
⇒ a campanha **já havia absorvido o efeito do axial calibrando o piso por curva**, e anular
esse piso aplica o desconto **duas vezes**. Ligar o campo não é um ajuste pendente: é somar
o mesmo efeito com ele mesmo.
"""

from __future__ import annotations

import pytest

from bolt_analysis_studio.core.validation_cases import ValidationCase
from bolt_analysis_studio.numerical.dynamic_stiffness_analyzer import (
    JointGeometry, JointMaterial, SlowState, self_locking_gate)
from bolt_analysis_studio.validation.case_registry import all_records


# valores LIDOS do paper (estão nos nomes dos arquivos; a nota de aparato
# confirma o modo). ZERO nas baselines é o valor CERTO, não ausência de dado.
_ESPERADO = {
    "eccles2010_fig3_typical_no_axial": (0.0, ""),
    "eccles2010_fig7a_no_axial": (0.0, ""),
    "eccles2010_fig8a_no_axial_baseline1": (0.0, ""),
    "eccles2010_fig8c_no_axial_baseline2": (0.0, ""),
    "eccles2010_fig6_annotated_4kN_axial": (4000.0, "constant"),
    "eccles2010_fig7b_axial_1p1kN_constant": (1100.0, "constant"),
    "eccles2010_fig7c_axial_2p7kN_constant": (2700.0, "constant"),
    "eccles2010_fig7d_axial_3p1kN_constant": (3100.0, "constant"),
    "eccles2010_fig8b_axial_0p7kN_intermittent": (700.0, "intermittent"),
    "eccles2010_fig8d_axial_3p5kN_intermittent": (3500.0, "intermittent"),
}


@pytest.fixture(scope="module")
def eccles():
    return {r.case_id: r.validation_case for r in all_records()
            if r.case_id.startswith("eccles2010_")}


# --------------------------------------------------------------- C1: registry

def test_o_axial_do_paper_esta_no_registry(eccles):
    """O valor do nome do arquivo é o valor do campo — os 10, um a um."""
    assert set(eccles) == set(_ESPERADO), "o conjunto de curvas do ECCLES mudou"
    erros = []
    for cid, (n_esp, m_esp) in sorted(_ESPERADO.items()):
        vc = eccles[cid]
        if abs(vc.external_axial_N - n_esp) > 1e-9:
            erros.append(f"{cid}: axial {vc.external_axial_N} != {n_esp}")
        if vc.external_axial_mode != m_esp:
            erros.append(f"{cid}: modo {vc.external_axial_mode!r} != {m_esp!r}")
    assert not erros, "\n  ".join(erros)


def test_o_zero_das_baselines_e_afirmacao_nao_omissao(eccles):
    """As 4 baselines rodaram SEM axial; 0.0 é o dado, e o teste diz isso.

    Sem este caso, alguém poderia "consertar" a ausência preenchendo as baselines
    com algum valor — e elas são justamente o controle da fonte.
    """
    base = [c for c, (n, _) in _ESPERADO.items() if n == 0.0]
    assert len(base) == 4
    for cid in base:
        assert eccles[cid].external_axial_N == 0.0
        assert eccles[cid].external_axial_mode == ""


# ---------------------------------------------------------------- C2: config

def test_a_chave_so_aparece_quando_ha_axial(eccles):
    """Isolamento ESTRUTURAL: curva sem axial tem o dict SEM a chave.

    Condicional de propósito — posta sem condição, a chave mudaria o
    `to_solver_config()` dos 205 casos.
    """
    for cid, (n, _) in sorted(_ESPERADO.items()):
        cfg = eccles[cid].to_solver_config()
        tem = "external_axial_N" in cfg
        assert tem == (n > 0.0), f"{cid}: chave presente={tem} mas axial={n}"
        if tem:
            assert cfg["external_axial_N"] == n
            assert cfg["external_axial_mode"] in ("constant", "intermittent")


def test_curva_de_outra_fonte_nao_ganha_a_chave():
    """Regressão: o campo é do ECCLES, e nenhuma outra fonte deve carregá-lo."""
    fora = [r.case_id for r in all_records()
            if not r.case_id.startswith("eccles2010_")
            and float(getattr(r.validation_case, "external_axial_N", 0.0) or 0.0) > 0.0]
    assert not fora, f"curvas fora do ECCLES com axial externo: {fora}"


# ------------------------------------------------------- C3: OFF é EXATO

def _gate(floor, F_ax, override, F0=15000.0, F0_init=15000.0):
    st = SlowState(F_0=F0, F_0_init=F0_init, F_ax_ext=F_ax)
    mat = JointMaterial(loose_arrest_floor=floor, ax_floor_override=override)
    # campos REAIS do JointGeometry (M8: A_s ISO 36,6 mm2, d_2 7,188 mm).
    # A 1a versao deste helper passava d=/L=, que NAO existem — o Pyright
    # apontou antes do teste rodar, e o teste confirmou.
    geom = JointGeometry(E=210e9, A_s=36.6e-6, L_eff=30e-3, d_2=7.188e-3,
                         pitch=1.25e-3, r_bearing=6e-3, A_contact=8e-5)
    return self_locking_gate(st, mat, geom)


@pytest.mark.parametrize("F_ax", [0.0, 1100.0, 3100.0])
def test_override_zero_e_bit_identico(F_ax):
    """`ax_floor_override = 0` ⇒ o gate ignora a BC, qualquer que seja F_ax."""
    assert _gate(0.137, F_ax, 0.0) == _gate(0.137, 0.0, 0.0)


@pytest.mark.parametrize("override", [0.0, 0.18, 1.0])
def test_sem_BC_externa_e_identidade_exata(override):
    """`F_ax_ext = 0` ⇒ identidade EXATA, incluindo com o campo ligado.

    É o que cobre as 4 baselines do ECCLES e todas as fontes transversais: o ramo
    exige as TRÊS condições (campo > 0, BC > 0, geom), então não depende de
    `x * 1.0 == x`.
    """
    assert _gate(0.137, 0.0, override) == _gate(0.137, 0.0, 0.0)


def test_sem_geom_nao_aplica():
    """`geom=None` ⇒ o ramo não roda (chamador legado fica intacto)."""
    st = SlowState(F_0=15000.0, F_0_init=15000.0, F_ax_ext=3100.0)
    mat = JointMaterial(loose_arrest_floor=0.137, ax_floor_override=0.18)
    assert self_locking_gate(st, mat) == self_locking_gate(
        SlowState(F_0=15000.0, F_0_init=15000.0), mat)


def test_ligado_o_gate_ABRE_o_piso():
    """Com as 3 condições, o piso cai ⇒ o gate deixa passar MAIS afrouxamento.

    Isto é a mecânica funcionando — e é justamente por funcionar que o G3 pôde
    falsificar a rota: o efeito existe e tem o sinal errado para este dado.
    """
    g_off = _gate(0.137, 3100.0, 0.0)
    g_on = _gate(0.137, 3100.0, 1.0)
    assert g_on > g_off, "anular o piso tem de AUMENTAR o gate (menos arresto)"


# --------------------------------------------- a FALSIFICAÇÃO, presa como teste

def test_a_rota_do_piso_anulavel_esta_falsificada_e_o_motivo_fica_escrito():
    """⛔ NÃO ligar `ax_floor_override` no ECCLES — medido, não opinado.

    G3 do prereg, 4 doses (1,0 · 0,5 · 0,25 · 0,18): a `fig7d` (alvo, piso
    anulado pela nota) vai de res.máx **0,0901 → 0,2200–0,2530**, e os controles
    `fig7b`/`fig7c` pioram junto (MAE +0,07 a +0,18 contra tolerância +0,01).
    Nenhuma dose melhora nada.

    **A causa está nos pisos vigentes, e é aritmética:** eles JÁ decrescem com a
    carga axial, com `prov` de `fitado-this-rig` —

        fig7b  1,1 kN → floor 0,232
        fig7c  2,7 kN → floor 0,182
        fig7d  3,1 kN → floor 0,137

    ⇒ a campanha já absorveu o efeito do axial **calibrando o piso por curva**.
    Anular esse piso aplica o desconto **duas vezes**, e é por isso que piora
    monotonicamente. Este teste prende a monotonia (piso ↓ com axial ↑) para que
    a próxima pessoa veja o motivo em vez de re-medir a falsificação.

    A rota que sobra é **derivar** o piso do axial — uma lei `floor(F_ax)` com um
    número compartilhado, substituindo os 3 fitados — e não somar uma anulação
    por cima deles.
    """
    from bolt_analysis_studio.validation import runner as rn
    regs = {r.case_id: r for r in all_records()}
    pares = [("eccles2010_fig7b_axial_1p1kN_constant", 1100.0),
             ("eccles2010_fig7c_axial_2p7kN_constant", 2700.0),
             ("eccles2010_fig7d_axial_3p1kN_constant", 3100.0)]
    consts, _ = rn.frozen_constants()
    pisos = []
    for cid, ax in pares:
        ov = rn._effective_overrides(regs[cid], consts)
        f = ov.get("loose_arrest_floor")
        assert f is not None, f"{cid} perdeu o piso adotado — o argumento muda"
        assert regs[cid].validation_case.external_axial_N == ax
        pisos.append(float(f))
    assert pisos == sorted(pisos, reverse=True), (
        f"os pisos do ECCLES deixaram de decrescer com a carga axial: {pisos}. "
        "O argumento da falsificação (o piso fitado JA absorve o axial) depende "
        "desta monotonia — se ela caiu, a rota do piso anulável precisa ser "
        "RE-MEDIDA, não re-assumida.")
