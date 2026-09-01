# -*- coding: utf-8 -*-
"""Contrato da linha "Cobertura da métrica" do report por caso.

## O que ela existe para dizer

A janela pontuada pela métrica pode ser **menor que a curva**: `FLOOR_TRIM`=0,10
descarta o dado abaixo do piso (e encurta a simulação junto), o `trim_n_max`
declarado corta trecho *out-of-model*, e o último ponto pode cair além do
`n_max`. Medido em 2026-08-16: **82** curvas têm algum gap, e a página não dizia
nada — de modo que a `lu2024_M8_fig18_amp2p0` fechava o tripé com MAE 0,0110
**sendo julgada em 6 de 13 pontos**, com erro 6,3× maior na metade oculta.

## As duas coisas que este teste protege, e as duas já foram erradas

1. **A linha não pode ATRIBUIR a causa.** A 1ª redação dizia *"porque o dado cai
   abaixo do piso"* e as causas medidas são três: 32 por piso · 12 por
   `trim_n_max` · 8 por ambos · **30 por efeito de borda** (1 ponto além do
   `n_max`). Estaria errada em **42 das 82**.
2. **Ela precisa de MATERIALIDADE.** Sem filtro, dispararia nas 82 — incluindo
   30 casos de um único ponto de borda, que é ruído. Ruído desliga guarda, e
   este repositório já perdeu instrumentos assim. Filtro: **≥ 2 pontos E ≥ 10 %**
   ⇒ 37 curvas.
"""
from __future__ import annotations

import pytest

import bolt_analysis_studio.validation.report_html as rh


class _Res:
    """Mínimo que `_pontos_julgados` lê."""
    def __init__(self, n):
        self.metric_x = list(range(n))


def test_inerte_sem_total_e_sem_gap():
    """Sem `n_total`, ou com a curva inteira julgada, a página não muda."""
    assert rh._pontos_julgados(_Res(10), None) == ""
    assert rh._pontos_julgados(_Res(10), 10) == ""
    assert rh._pontos_julgados(_Res(10), 9) == ""      # n_total < julgados: absurdo, inerte


@pytest.mark.parametrize("n_ok,n_total,aparece", [
    (25, 26, False),    # 1 ponto de borda, 4 % — RUÍDO (é o caso bauer fig8_test1)
    (13, 14, False),    # 1 ponto, 7 % — ruído
    (98, 100, False),   # 2 pontos mas só 2 % — imaterial
    (12, 14, True),     # 2 pontos e 14 % — material
    (18, 20, True),     # 2 pontos e 10 % EXATO — a fronteira inclui
    (6, 13, True),      # lu2024_fig18_amp2p0 — o caso que motivou a linha
    (13, 17, True),     # lu2024_fig20_T22Nm — 24 % oculto
    (44, 134, True),    # liu2025_fig2_single — 67 % oculto
    (8, 35, True),      # eccles fig8b — 77 % oculto
])
def test_filtro_de_materialidade(n_ok, n_total, aparece):
    """≥2 pontos E ≥10 % — nem antes, nem depois.

    ⚠️ Os esperados são **fixos**, não recalculados da mesma fórmula da
    implementação. A 1ª versão deste teste derivava `esperado` com a regra que
    ele testa — comparava uma coisa consigo mesma e passaria com a regra
    trocada. É a armadilha "Δ=0 era instrumento morto", aqui no teste.
    """
    assert bool(rh._pontos_julgados(_Res(n_ok), n_total)) is aparece, (
        f"{n_ok}/{n_total}: esperado aparecer={aparece}")


def test_nao_atribui_a_causa():
    """A linha nomeia as TRÊS causas possíveis e não escolhe uma.

    É o conserto do defeito da 1ª redação: atribuir ao piso estaria errado em
    42 das 82 curvas com gap.
    """
    s = rh._pontos_julgados(_Res(6), 13)
    assert "FLOOR_TRIM" in s, "a causa do piso tem de ser citada"
    assert "trim_n_max" in s, "a causa do trim declarado tem de ser citada"
    assert "n_max" in s, "a causa de borda tem de ser citada"
    # e não pode afirmar UMA delas como a causa desta curva
    for proibido in ("porque o dado cai abaixo", "a causa é", "devido ao piso"):
        assert proibido not in s, f"a linha voltou a ATRIBUIR a causa: {proibido!r}"


def test_diz_que_nao_e_aviso_de_erro():
    """Fratura descartada é o piso ACERTANDO — a linha tem de dizer isso.

    Sem esta frase, um leitor lê "44 % oculto" como defeito, e nas duas curvas
    axiais do `SUN_2025_CRIMP` o ponto oculto é a **ruptura do parafuso**, que o
    modelo daquelas configs não modela de propósito.
    """
    s = rh._pontos_julgados(_Res(6), 13)
    assert "fratura" in s and "certo" in s
    assert "6,3" in s and "0,86" in s, "os dois números do lote sustentam a leitura"


def test_conta_os_numeros_certos():
    """N, M, quantos faltam e a fração — sem erro de um."""
    s = rh._pontos_julgados(_Res(6), 13)
    assert "6 de 13" in s
    assert "7 " in s and "54" in s        # 7 ocultos, 54 %
