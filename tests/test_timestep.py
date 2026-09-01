"""Adequacao do passo de tempo: dt vs a frequencia natural mais alta do modelo.

RESSUSCITADO em 2026-07-28. O arquivo anterior nao era um teste: era um SCRIPT
com `print()` no corpo do modulo, sem nenhum `def test_` e sem nenhum assert, que
carregava um `.msd` de um caminho absoluto cravado
(`C:\\Users\\leo_r\\OneDrive\\BPL\\Analitical\\bolt_analysis_studio\\model.msd`)
que nao existe. Como o nome casa `test_*.py`, o pytest importava o modulo, o
corpo executava, o `MSDModel.load` levantava `FileNotFoundError` e a COLETA
INTEIRA morria com exit 2 — por isso o arquivo vivia num `--ignore` da suite.

O conteudo tinha valor: e' a checagem CFL-like que diz se o passo de tempo do
integrador resolve o modo mais rapido da junta. Preservada aqui, com asserts, e
sem depender de nenhum arquivo: `build_model(AnalysisSpec())` devolve um modelo
minimo REAL (11 elementos, com o GROUND que o wizard prepende).
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from bolt_analysis_studio.gui.new_analysis_wizard import AnalysisSpec, build_model

# regra do script original: resolver o modo mais rapido com 10 passos por ciclo
PASSOS_POR_CICLO = 10


def _frequencias_naturais(model):
    """Frequencias naturais [Hz] de [K] e [M] montadas pelo proprio modelo."""
    M, K, _C = model.assemble_matrices()
    autovalores = np.linalg.eigvals(np.linalg.inv(M) @ K)
    return np.sqrt(np.abs(autovalores)) / (2 * np.pi)


def test_matrizes_montam_e_espectro_e_fisico():
    """[M], [K], [C] quadradas e coerentes com n_dof; espectro finito e positivo."""
    model = build_model(AnalysisSpec())
    M, K, C = model.assemble_matrices()

    assert M.shape == K.shape == C.shape
    assert M.shape[0] == M.shape[1] == model.n_dof

    freqs = _frequencias_naturais(model)
    assert len(freqs) == model.n_dof
    assert np.all(np.isfinite(freqs)), "frequencia nao-finita: [M] singular?"
    assert np.all(freqs > 0), "modo de frequencia nula: grau de liberdade solto"


def test_passo_de_tempo_recomendado_resolve_o_modo_mais_rapido():
    """`dt_rec = 1/(10 f_max)` e' a regra; um dt maior nao resolve o modo."""
    model = build_model(AnalysisSpec())
    f_max = float(np.max(_frequencias_naturais(model)))

    dt_rec = 1.0 / (PASSOS_POR_CICLO * f_max)
    assert dt_rec > 0
    # o proprio dt recomendado da, por construcao, 10 passos no modo mais rapido
    assert np.isclose(1.0 / (dt_rec * f_max), PASSOS_POR_CICLO)
    # e o dobro dele nao da (5 passos) — a regra tem de discriminar
    assert 1.0 / (2 * dt_rec * f_max) < PASSOS_POR_CICLO


def test_um_milissegundo_e_grosseiro_demais_para_uma_junta_aparafusada():
    """O achado que o script original demonstrava, agora preso num assert.

    Uma junta aparafusada e' RIGIDA: no modelo minimo o modo mais alto fica na
    faixa de centenas de kHz (medido 2026-07-28: f_max ~8,2e5 Hz, dt recomendado
    ~1,2e-7 s), entao dt = 1 ms e' ~3-4 ordens de grandeza grande demais e leva a
    overflow numerico. A banda abaixo e' larga de proposito: o teste existe para
    pegar uma mudanca de ORDEM DE GRANDEZA na rigidez montada, nao para congelar
    o valor exato de uma calibracao.
    """
    model = build_model(AnalysisSpec())
    f_max = float(np.max(_frequencias_naturais(model)))
    dt_rec = 1.0 / (PASSOS_POR_CICLO * f_max)

    assert 1e4 < f_max < 1e8, f"f_max fora da ordem esperada: {f_max:.3e} Hz"
    assert 1e-3 > dt_rec, "1 ms deixou de ser grosseiro: a junta amoleceu?"
    assert 1e-3 / dt_rec > 100, (
        f"1 ms e' apenas {1e-3 / dt_rec:.0f}x o recomendado; esperado >100x")
