# -*- coding: utf-8 -*-
"""Forma NOVA: relogio de assentamento dependente de deslocamento.

    N_emb_eff(delta) = N_emb * (emb_clock_delta_ref / delta_amp)

Assinada pelo professor em 2026-08-14; derivacao e validacao em
`New_Theory/lei_relogio_embedding_por_deslocamento.md`.

## O que estes testes protegem

1. **INERCIA** — com o default (`emb_clock_delta_ref = 0.0`) o ramo novo nem
   roda, e o incremento e' BIT-A-BIT o de antes. E' o gate que protege as 207
   curvas ja adotadas; sem ele, uma forma "default-inerte" pode silenciosamente
   mover tudo (ja aconteceu nesta campanha com `k_gall` e com o Cattaneo-Mindlin,
   nos dois sentidos).
2. **A LEI** — o relogio efetivo escala com 1/delta, com expoente 1.
3. **O EXPOENTE NAO E' LIVRE** — nao existe campo para ajusta-lo. Se alguem
   acrescentar um, este teste falha e obriga a justificar: o 1 vem do mecanismo
   (esgotamento por slip acumulado: N = S/slip_por_ciclo, slip ~ delta), e
   torna-lo parametro seria converter uma consequencia em ajuste.
4. **DEGENERESCENCIA** — sem `delta_amp` (modo forca) a forma NAO age, porque
   nao ha deslocamento imposto que a defina.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from bolt_analysis_studio.numerical.dynamic_stiffness_analyzer import (  # noqa: E402
    EmbeddingLoss, JointMaterial)


def _geom():
    import math
    from bolt_analysis_studio.numerical.dynamic_stiffness_analyzer import (
        JointGeometry)
    d, p = 16e-3, 2e-3
    d2 = d - 0.6495 * p
    d1 = d - 1.0825 * p
    A_s = math.pi / 4 * ((d2 + d1) / 2) ** 2
    return JointGeometry(A_s=A_s, L_eff=0.05, d_2=d2, pitch=p,
                         r_bearing=0.75 * d, A_contact=1e-4)


def _incremento(mat_kw, delta_amp):
    """Incremento de assentamento de UM ciclo, isolado do resto do engine."""
    from bolt_analysis_studio.numerical.dynamic_stiffness_analyzer import (
        DynamicStiffnessAnalyzer)
    mat = JointMaterial(**mat_kw)
    ana = DynamicStiffnessAnalyzer(_geom(), mat, 50000.0)
    out = EmbeddingLoss().rate(ana.state, ana.geom, mat, F_amp=5000.0,
                               theta_load=0.0, freq=10.0, cycle_N=1,
                               delta_amp=delta_amp)
    # ⚠️ A chave e' `ds.delta_emb`, NAO `d_delta`. A 1a versao deste helper
    # chutou `d_delta` e caiu no fallback, devolvendo 0.0 nos DOIS lados — os
    # testes de inercia passavam comparando ZERO COM ZERO. E' a armadilha
    # "delta=0 era instrumento morto", catalogada 6x nesta campanha, agora
    # dentro do proprio teste que deveria proteger contra ela. Por isso o
    # acesso aqui e' DIRETO: se a chave mudar, KeyError ruidoso em vez de zero
    # silencioso.
    return float(out["ds"]["delta_emb"])


def test_default_e_off_exato():
    """Sem a forma, o incremento e' identico ao de sempre — BIT A BIT."""
    assert JointMaterial().emb_clock_delta_ref == 0.0, (
        "o default TEM de ser 0.0: qualquer outro valor liga a forma nas 210 "
        "curvas adotadas de uma vez")
    for d in (0.25e-3, 0.5e-3, 1.0e-3, None):
        a = _incremento({}, d)
        b = _incremento({"emb_clock_delta_ref": 0.0}, d)
        assert a == b, ("declarar o campo em 0.0 mudou o resultado — o ramo "
                        "novo esta rodando quando nao deveria")
        # ⚠️ GUARDA ANTI-VACUIDADE: sem isto o assert acima passa comparando
        # ZERO com ZERO e nao prova nada. Foi o que aconteceu na 1a versao
        # deste arquivo, por ler a chave errada do dicionario.
        assert a > 0.0, ("o incremento medido e' ZERO — o teste de inercia "
                         "estaria passando por vacuidade, nao por igualdade")


def test_lei_escala_com_inverso_do_deslocamento():
    """delta 2x menor => relogio 2x maior => incremento por ciclo MENOR."""
    kw = {"emb_clock_delta_ref": 1.0e-3, "N_emb": 400.0}
    dg = _incremento(kw, 1.0e-3)
    dp = _incremento(kw, 0.5e-3)
    assert dg > dp > 0, (
        "com delta MENOR o assentamento tem de avancar mais DEVAGAR por ciclo "
        f"(N_emb_eff maior): dg={dg} dp={dp}")
    # razao esperada: (1-e^{-1/400}) / (1-e^{-1/800}) ~ 2 (regime linear)
    razao = dg / dp
    assert 1.9 < razao < 2.1, (
        f"a lei e' N ~ 1/delta com EXPOENTE 1; razao medida {razao:.3f} deveria "
        "ser ~2 para delta 2x. Se mudou, o expoente deixou de ser 1.")


def test_expoente_nao_e_parametro_livre():
    """Nao pode existir campo para ajustar o expoente.

    O 1 vem do mecanismo: se o assentamento se esgota apos uma distancia de slip
    acumulada S, entao N_emb = S/(slip por ciclo) e slip ~ delta. Deixa-lo livre
    converteria uma CONSEQUENCIA em ajuste — e a campanha ja pagou caro por
    parametros que compensam uns aos outros.
    """
    campos = set(JointMaterial.__dataclass_fields__)
    proibidos = {"emb_clock_delta_exp", "emb_clock_exp", "emb_clock_q"}
    assert not (campos & proibidos), (
        f"apareceu expoente ajustavel para o relogio: {campos & proibidos}. "
        "Ele e' 1 POR CONSTRUCAO do mecanismo; se a medicao passou a exigir "
        "outro, a forma esta errada e precisa de prereg proprio, nao de knob.")


def test_caminho_desligado_e_a_forma_fechada_exata():
    """Com a forma OFF o incremento e' a forma fechada, SEM guard nenhum.

    ⚠️ Esta guarda existe por um defeito real cometido na implementacao: o
    `max(n_eff, 1e-9)` que protege a divisao ficou, na 1a versao, FORA do ramo
    novo. Assim posto, ele mudava tambem o caminho desligado — com N_emb=0 o
    original divide por zero (inf/nan) e o guard devolvia um numero limpo.

    "Default-inerte" tem de valer INCLUSIVE para entrada degenerada; e' por onde
    uma forma opt-in vaza, porque ninguem testa o valor que ninguem usa. O teste
    fixa a expressao exata: qualquer guard que reapareca fora do `if` falha aqui.
    """
    # ⚠️ O DISCRIMINANTE E' O VALOR DEGENERADO, e so ele. A 1a versao deste teste
    # varria N_emb de 0,5 a 400 e teria passado COM O BUG DE VOLTA — o guard
    # fora do `if` so muda o resultado para N_emb <= 1e-9. Um teste que nao
    # separa as duas implementacoes nao e' guarda, e' decoracao.
    with pytest.raises(ZeroDivisionError):
        _incremento({"N_emb": 0.0}, 0.5e-3)

    # E o mesmo N_emb degenerado COM a forma ligada tem de ser bem-comportado:
    # ai o guard vale, porque o ramo e' o novo.
    v = _incremento({"N_emb": 0.0, "emb_clock_delta_ref": 1.0e-3}, 0.5e-3)
    assert np.isfinite(v) and v > 0.0, (
        "com a forma LIGADA o guard do ramo novo tem de valer — N_emb=0 nao "
        f"pode propagar inf/nan; obtido {v!r}")


def test_modo_forca_nao_e_afetado():
    """Sem deslocamento imposto a forma nao tem o que modular."""
    kw = {"emb_clock_delta_ref": 1.0e-3, "N_emb": 400.0}
    com = _incremento(kw, None)
    sem = _incremento({"N_emb": 400.0}, None)
    assert com == sem, (
        "em modo forca (delta_amp=None) a forma NAO pode agir — nao ha "
        "deslocamento que a defina, e agir ali seria re-escalar N_emb em "
        "silencio (o defeito que o `s1_freq_exp` documenta)")
