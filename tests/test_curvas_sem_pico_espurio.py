# -*- coding: utf-8 -*-
"""Guarda permanente: nenhuma curva de referência pode GANHAR um pico impossível.

**Por que este arquivo existe.** Em 2026-08-13 a adoção dado-only `a9541ec`
(minha) re-digitalizou 7 CSVs do `LU_2024` e **corrompeu o `y` de 5 pontos** em
4 delas: a pré-carga SUBIA e voltava a cair no ciclo seguinte (`T10Nm` x=85:
0,329 → **0,896** → 0,310). O gate daquela adoção conferia as âncoras das
Tabelas 8/9 em c1/c10/c50/c100 — e **o artefato caía entre c50 e c100**.
Round-trip em 4 pontos não vê pico entre âncoras.

A lição que virou este teste: **curva de decaimento de pré-carga é MONÓTONA**;
a checagem que faltava não era de âncora, era de monotonicidade.

**Por que NÃO se testa contra os vizinhos imediatos.** O critério óbvio
(`y[i] > y[i±1] + 0,01`) foi medido e **teria deixado passar a própria
regressão que este arquivo existe para pegar**: na `fig18_amp0p5` o artefato
ocupava DOIS pontos consecutivos (0,457 e 0,407), e o segundo *sustentava* o
primeiro ⇒ o salto contra vizinhos caía para **0,050**. Evidência local é
cega a defeito correlacionado; a estatística aqui é **global** —
`max(y − mínimo corrente)`, insensível a quantos pontos o artefato ocupa.

Separação medida no universo (207 curvas, 2026-08-16):

| população | valor |
|---|---:|
| mediana das 210 | **0,0000** (a maioria é exatamente monótona) |
| pior legítimo não isento (`jcsr2023_plain_outdoor`) | **0,083** |
| **barra deste teste** | **0,10** |
| artefato pré-existente (`fig18_amp1p0`, `fig20_T22Nm`) | 0,393 · 0,399 |
| a regressão `a9541ec` (4 curvas) | 0,146 · 0,261 · 0,485 · **0,612** |

A margem é assimétrica de propósito e fica declarada: 1,2× acima do pior
legítimo, **3,9× abaixo** do artefato mais brando. Prereg:
`docs/superpowers/specs/2026-08-16-lu2024-pico-espurio-prereg.md`.
"""
import numpy as np
import pytest

from bolt_analysis_studio.validation.case_registry import all_records
from bolt_analysis_studio.validation.inputs import load_full_curve

BARRA = 0.10

# Isenção NOMEADA com razão física — nunca whitelist silenciosa. Protocolo
# intermitente: a carga é retirada e re-aplicada, então a pré-carga medida
# RECUPERA de verdade; a não-monotonia é o ensaio, não um defeito de leitura.
ISENTAS = {
    "eccles2010_fig8d_axial_3p5kN_intermittent": (
        "protocolo INTERMITENTE (carga retirada e re-aplicada) — a recuperação "
        "de pré-carga é física; medido 0,429 em 2026-08-16"
    ),
}


def subida_acima_do_minimo(v) -> float:
    """`max(y − mínimo corrente)`, normalizada pela escala da própria curva.

    A normalização não é cosmética: a biblioteca tem curvas em **fração**
    (F/F₀ ≈ 1) e curvas em **porcento** (`LIU_2020_WEAR` chega a 95), e um
    limiar absoluto significaria coisas 100× diferentes nas duas.
    """
    v = np.asarray(v, dtype=float)
    if v.size < 3:
        return 0.0
    escala = float(np.percentile(v, 95)) or 1.0
    return float(np.max(v - np.minimum.accumulate(v))) / escala


def _curvas():
    for rec in all_records():
        try:
            _, ratio = load_full_curve(str(rec.csv_path))
        except Exception:
            continue                      # curva sem CSV legível não é objeto deste teste
        if len(ratio) >= 3:
            yield rec.case_id, rec.source, np.asarray(ratio, dtype=float)


def test_nenhuma_curva_tem_pico_impossivel():
    """O invariante. Falha NOMEANDO a curva, o valor e a distância da barra."""
    fora = [
        (cid, src, s)
        for cid, src, v in _curvas()
        if (s := subida_acima_do_minimo(v)) > BARRA and cid not in ISENTAS
    ]
    assert not fora, "curva(s) com pico impossível (pré-carga sobe e volta):\n" + "\n".join(
        f"  {s:.3f} ({s / BARRA:.1f}x a barra)  {src}  {cid}" for cid, src, s in fora
    )


def test_a_barra_separa_de_fato_o_legitimo_do_artefato():
    """A barra tem de ficar ACIMA de todo legítimo — senão o teste vira ruído.

    Sem isto, um aperto futuro da barra passaria a acusar curvas boas, o teste
    seria silenciado, e a guarda morreria pelo caminho mais comum: virar alarme
    falso e ser desligada.
    """
    pior = max(subida_acima_do_minimo(v)
               for cid, _, v in _curvas() if cid not in ISENTAS)
    assert pior <= BARRA, f"pior legítimo {pior:.3f} passou da barra {BARRA}"
    assert pior > 0.5 * BARRA, (
        f"pior legítimo caiu para {pior:.3f}: a barra ficou frouxa demais e "
        "deve ser reapertada (com a separação re-medida e escrita no docstring)"
    )


def test_isencao_so_vale_com_razao_escrita():
    """Isenção sem razão física escrita é whitelist — e whitelist apodrece."""
    for cid, razao in ISENTAS.items():
        assert len(razao) > 40, f"isenção de {cid} sem razão física escrita"
    validos = {cid for cid, _, _ in _curvas()}
    orfas = set(ISENTAS) - validos
    assert not orfas, f"isenção para curva que não existe mais: {sorted(orfas)}"


@pytest.mark.parametrize("n_pontos_corrompidos", [1, 2, 3])
def test_pega_artefato_de_qualquer_largura(n_pontos_corrompidos):
    """Validação por perturbação: injeta o defeito e exige que ele seja pego.

    O caso `n=2` é o que importa — foi exatamente ele que escapou do critério
    de vizinhos na `fig18_amp0p5`. Aqui a estatística global o pega igual.
    """
    v = np.linspace(1.0, 0.30, 20)                    # decaimento monótono limpo
    assert subida_acima_do_minimo(v) == 0.0
    v[10:10 + n_pontos_corrompidos] += 0.27           # a magnitude medida no LU_2024
    assert subida_acima_do_minimo(v) > BARRA


def test_criterio_de_vizinhos_seria_cego_ao_defeito_de_2_pontos():
    """Fixa a razão de projeto: por que a estatística é global e não local.

    Reproduz o par real da `fig18_amp0p5` (0,276 → 0,457 → 0,407 → 0,159). O
    critério de vizinhos vê um salto de 0,050; o global vê 0,26.
    """
    v = np.array([0.347, 0.324, 0.310, 0.276, 0.457, 0.407, 0.159, 0.129])
    vizinhos = max(min(v[i] - v[i - 1], v[i] - v[i + 1]) for i in range(1, len(v) - 1))
    assert vizinhos == pytest.approx(0.050, abs=1e-9)     # passaria num piso de 0,05
    assert subida_acima_do_minimo(v) > 2 * BARRA          # o global pega
