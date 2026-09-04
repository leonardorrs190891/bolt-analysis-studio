"""A curva experimental chega ao otimizador, pelas duas origens (2026-09-03).

O otimizador (`ParameterIdentifier`) e o dialogo com trava e limites por
parametro ja' existiam; nao havia como entregar a eles uma curva no chrome
padrao. Aqui se afere que as duas origens funcionam E que o ajuste parte da
fisica certa — que era onde estavam os defeitos:

1. `simulate_v2_curve` coagia TODO tuner com `float()`, e nove chaves do
   JointMaterial sao modo (string/bool). Estourava em todas as 210
   configuracoes adotadas.
2. `_simulate_v2` comecava com um dict VAZIO de tuners: ajustar um caso da
   validacao descartava as outras constantes adotadas daquele artigo e
   voltava aos defaults do engine. Travar um valor so' significa alguma coisa
   se o valor travado for de fato usado.
3. `_geom_from_model` ignorava `_v2_geometry_overrides` e montava L_eff=3,125d
   e A_contact=1e-4 fixos — o proprio gui_bridge ja' avisava que sem a
   geometria adotada "o Run nao reproduz o report".

O invariante que fecha os tres: o motor do otimizador tem de dar a MESMA curva
que o Run do aplicativo, para o mesmo modelo.
"""
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "src"))

import pytest                                                    # noqa: E402

CASO = "lu2024_M8_fig18_amp0p5"
MSD = RAIZ / "Models" / "SAVED_CASES" / "LU_2024" / f"{CASO}.msd"
precisa_caso = pytest.mark.skipif(
    not MSD.is_file(), reason="rode New_Theory/build_saved_cases.py")


@pytest.fixture
def janela(qapp):
    from bolt_analysis_studio.core.app_state import get_app_state
    from bolt_analysis_studio.gui.chrome.app_window import ChromeWindow
    return ChromeWindow(get_app_state())


@pytest.fixture(scope="module")
def modelo_do_caso(qapp):
    from bolt_analysis_studio.validation.case_registry import record
    from bolt_analysis_studio.validation.gui_bridge import build_case_model
    return build_case_model(record(CASO))


# --- o menu -----------------------------------------------------------------

def test_o_chrome_tem_porta_para_a_calibracao(janela):
    """Ate' 2026-09-03 o ajuste so' era alcancavel pela janela V1, que nao e'
    mais a interface padrao."""
    from PyQt6.QtWidgets import QMenu

    menus = {m.title(): m for m in janela.menuBar().findChildren(QMenu)}
    assert "Analisar" in menus, list(menus)
    acoes = {a.text(): a for a in menus["Analisar"].actions()}
    alvo = "Calibrar parâmetros do modelo…"
    assert alvo in acoes, list(acoes)
    assert acoes[alvo].shortcut().toString() == "Ctrl+K"


def test_apply_and_rerun_acha_o_run_do_chrome(janela):
    """O dialogo procura `_run_analysis` no pai; sem isso ele aplica e manda
    o usuario re-rodar a mao."""
    assert callable(getattr(janela, "_run_analysis", None))


# --- origem (a): o caso da validacao ----------------------------------------

@precisa_caso
def test_reconhece_de_qual_caso_o_modelo_veio(qapp):
    from bolt_analysis_studio.core.models.model import MSDModel
    from bolt_analysis_studio.gui.chrome.widgets.reference_curve import (
        caso_do_modelo)

    assert caso_do_modelo(MSDModel.load(str(MSD))) == CASO


def test_id_que_nao_existe_no_registry_nao_vale(qapp):
    """A marca vem da descricao, que e' prosa. Conferir contra o registry e' o
    que impede um texto editado a mao de virar um caso."""
    from bolt_analysis_studio.gui.chrome.widgets.reference_curve import (
        caso_do_modelo)

    class Falso:
        description = "Bolt Analysis Studio - validation case caso_inventado_9"

    assert caso_do_modelo(Falso()) is None
    assert caso_do_modelo(None) is None


@precisa_caso
def test_a_curva_do_caso_e_a_MESMA_que_o_artigo_usa(qapp):
    """Nao relemos o CSV digitalizado: o runner aplica escala de eixo,
    normalizacao e corte de piso pre-registrados, e reimplementar isso criaria
    um segundo dado experimental. Os pontos saem do store."""
    import numpy as np
    from bolt_analysis_studio.gui.chrome.widgets.reference_curve import (
        curva_do_caso)
    from bolt_analysis_studio.validation.store import ValidationStore

    res = ValidationStore().get(CASO)
    ref = curva_do_caso(CASO, F0_N=12000.0)
    assert ref is not None
    assert np.allclose(ref["cycle"], np.asarray(res.metric_x, float))
    assert np.allclose(ref["F_ratio"], np.asarray(res.metric_data, float))
    assert ref["F_ratio"][0] == pytest.approx(1.0, abs=1e-6)


def test_caso_inexistente_devolve_none_em_vez_de_estourar(qapp):
    from bolt_analysis_studio.gui.chrome.widgets.reference_curve import (
        curva_do_caso)

    assert curva_do_caso("nao_existe_este_caso", 1000.0) is None


# --- origem (b): CSV do usuario ---------------------------------------------

def test_le_o_csv_de_duas_colunas_do_corpus(tmp_path, qapp):
    """`cycle,F_over_F0` e' o formato que o proprio repo grava. O leitor da V1
    esperava tres colunas e, com ele, F/F0 caia na coluna de forca e a razao
    ficava zerada — a curva entrava achatada e ninguem via."""
    from bolt_analysis_studio.gui.chrome.widgets.reference_curve import (
        curva_de_csv)

    p = tmp_path / "duas.csv"
    p.write_text("cycle,F_over_F0\n0,1.0\n10,0.80\n20,0.61\n", encoding="utf-8")
    ref = curva_de_csv(str(p), F0_N=10000.0)
    assert list(ref["cycle"]) == [0.0, 10.0, 20.0]
    assert ref["F_ratio"][1] == pytest.approx(0.80)
    assert ref["F_kN"][0] == pytest.approx(10.0)      # F0 = 10 kN


def test_le_o_csv_de_tres_colunas_da_v1(tmp_path, qapp):
    from bolt_analysis_studio.gui.chrome.widgets.reference_curve import (
        curva_de_csv)

    p = tmp_path / "tres.csv"
    p.write_text("cycle,F_kN,F_over_F0\n0,20.0,1.0\n50,15.0,0.75\n",
                 encoding="utf-8")
    ref = curva_de_csv(str(p), F0_N=20000.0)
    assert ref["F_ratio"][1] == pytest.approx(0.75)
    assert ref["F_kN"][0] == pytest.approx(20.0)


def test_csv_sem_coluna_de_razao_acusa(tmp_path, qapp):
    from bolt_analysis_studio.gui.chrome.widgets.reference_curve import (
        curva_de_csv)

    p = tmp_path / "ruim.csv"
    p.write_text("cycle,algo\n0,0\n10,0\n", encoding="utf-8")
    with pytest.raises(ValueError):
        curva_de_csv(str(p), 1000.0)


# --- o dialogo das duas origens ---------------------------------------------

def test_o_dialogo_oferece_as_duas_origens(qapp):
    from bolt_analysis_studio.gui.chrome.widgets.reference_curve import (
        ReferenceSourceDialog)

    com = ReferenceSourceDialog(None, CASO)
    assert com.rb_caso.isEnabled() and com.rb_caso.isChecked()
    assert CASO in com.rb_caso.text()

    sem = ReferenceSourceDialog(None, None)
    assert not sem.rb_caso.isEnabled(), "sem caso, a origem tem de ficar off"
    assert sem.rb_csv.isChecked(), "o CSV vira o padrao"


# --- o que faz o ajuste valer -----------------------------------------------

@precisa_caso
def test_o_motor_do_otimizador_e_o_MESMO_do_run(modelo_do_caso, qapp):
    """O invariante central. Se o ajuste for medido num motor diferente do que
    o Run usa, calibrar aqui e rodar ali dao curvas diferentes e o ajuste nao
    quer dizer nada. Medido em 2026-09-03: antes dos consertos a diferenca
    final era 0,73 em F/F0; agora e' zero."""
    import numpy as np
    from bolt_analysis_studio.core.solver_worker import (
        PreloadAnalysisConfig, SolverWorker)
    from bolt_analysis_studio.numerical.parameter_identifier import (
        ParameterIdentifier, jm_k_wear_spec_param)

    m = modelo_do_caso
    gl = m.global_loading
    n = int(gl.n_cycles)

    w = SolverWorker()
    w._current_model = m
    cfg = PreloadAnalysisConfig()
    cfg.initial_preload = float(gl.F_preload)
    cfg.n_cycles = n
    prod = np.asarray(w._compute_v2_history(cfg, n)["ratio"], float)

    # Pelo caminho REAL do otimizador (`_simulate_v2`), que resolve theta e
    # amplitude do proprio carregamento — passar theta a mao aqui esconderia
    # justamente o tipo de erro que se quer pegar.
    idf = ParameterIdentifier(m, [0.0, 1.0], [1.0, 0.9],
                              params_to_fit=[jm_k_wear_spec_param()],
                              engine="v2", max_evals=1)
    adotado = (getattr(m, "_v2_tuner_overrides", {}) or {}).get(
        "k_wear_spec", 5e-14)
    _, sr = idf._simulate_v2({"k_wear_spec": adotado})

    k = min(len(prod), len(sr))
    assert np.max(np.abs(prod[:k] - sr[:k])) < 1e-9, (
        "o motor do otimizador divergiu do Run")


@precisa_caso
def test_o_ajuste_parte_das_constantes_adotadas_do_caso(modelo_do_caso, qapp):
    """Marcar 1 parametro nao pode apagar os outros 22. A base sao as
    constantes do modelo; a candidata entra por cima."""
    from bolt_analysis_studio.numerical.parameter_identifier import (
        ParameterIdentifier, jm_k_wear_spec_param)

    m = modelo_do_caso
    adotadas = dict(getattr(m, "_v2_tuner_overrides", {}) or {})
    assert len(adotadas) >= 20, "o caso deveria trazer as constantes adotadas"

    idf = ParameterIdentifier(m, [0.0, 1.0], [1.0, 0.9],
                              params_to_fit=[jm_k_wear_spec_param()],
                              engine="v2", max_evals=1)
    vistos = {}

    import bolt_analysis_studio.numerical.parameter_identifier as pi
    original = pi.simulate_v2_curve

    def espia(model, tuners, *a, **kw):
        vistos.update(tuners)
        return original(model, tuners, *a, **kw)

    pi.simulate_v2_curve = espia
    try:
        idf._simulate_v2({"k_wear_spec": 7e-14})
    finally:
        pi.simulate_v2_curve = original

    for chave, valor in adotadas.items():
        if chave == "k_wear_spec":
            continue
        assert vistos.get(chave) == valor, f"{chave} sumiu do ajuste"
    assert vistos["k_wear_spec"] == 7e-14, "a candidata tem de mandar"


@precisa_caso
def test_chave_de_modo_nao_estoura_o_ajuste(modelo_do_caso, qapp):
    """`conform_driver='effective'` e outras oito chaves sao modo, nao numero.
    float() nelas derrubava o ajuste em TODAS as 210 configuracoes."""
    from bolt_analysis_studio.numerical.parameter_identifier import (
        simulate_v2_curve)

    m = modelo_do_caso
    tun = dict(getattr(m, "_v2_tuner_overrides", {}) or {})
    modos = {k: v for k, v in tun.items() if isinstance(v, (str, bool))}
    assert modos, "esperava ao menos uma chave de modo na configuracao adotada"
    gl = m.global_loading
    _, sr = simulate_v2_curve(m, tun, 5,
                              str(getattr(gl, "control_mode", "displacement")),
                              F0=float(gl.F_preload), F_amp=0.0,
                              theta=1.5708, freq=1.0)
    assert len(sr) == 6


@precisa_caso
def test_o_caminho_inteiro_do_menu_ate_o_dialogo(janela, qapp, monkeypatch):
    """Ponta a ponta: importar um caso, acionar o item do menu e chegar ao
    dialogo de calibracao COM a curva daquele caso. So' os dois `exec()`
    modais sao substituidos; o resto e' o codigo de producao."""
    from PyQt6.QtWidgets import QMessageBox

    from bolt_analysis_studio.gui import main_window as mw
    from bolt_analysis_studio.gui.chrome.widgets import reference_curve as rc

    # Sem isto uma falha vira TRAVAMENTO em vez de erro: os caminhos de erro
    # de `_calibrar_parametros` abrem QMessageBox modal, que sem usuario espera
    # para sempre. Foi assim que o import errado de CalibrationDialog apareceu
    # como um teste pendurado, e nao como uma falha legivel.
    avisos = []
    for nome in ("critical", "warning", "information"):
        monkeypatch.setattr(QMessageBox, nome,
                            lambda *a, _n=nome, **k: avisos.append((_n, a[1:])))

    assert janela._carrega_projeto(str(MSD), como_projeto=False)
    for _ in range(40):
        qapp.processEvents()

    monkeypatch.setattr(rc.ReferenceSourceDialog, "exec",
                        lambda self: (setattr(self, "escolha", "caso"), 1)[1])
    visto = {}
    original = mw.CalibrationDialog.__init__

    def espia(self, parent, model, reference_curve, **kw):
        visto["ref"] = reference_curve
        visto["model"] = model
        return original(self, parent, model, reference_curve, **kw)

    monkeypatch.setattr(mw.CalibrationDialog, "__init__", espia)
    monkeypatch.setattr(mw.CalibrationDialog, "exec", lambda self: 0)

    janela._calibrar_parametros()
    for _ in range(20):
        qapp.processEvents()

    assert "ref" in visto, (
        f"o dialogo de calibracao nao chegou a ser aberto; avisos={avisos}")
    assert len(visto["ref"]["cycle"]) >= 2
    assert visto["ref"]["origem"].endswith(CASO)
    # e o modelo que chega ao ajuste traz as constantes adotadas do caso
    assert len(getattr(visto["model"], "_v2_tuner_overrides", {}) or {}) >= 20


@precisa_caso
def test_a_linha_de_base_do_dialogo_e_o_modelo_do_caso(modelo_do_caso, qapp):
    """A curva chamada "Current model" tem de ser o modelo ATUAL.

    `_preview_current` passava `tuners={}`: desenhava o modelo com os defaults
    do engine e chamava de atual, entao um caso da validacao aberto no dialogo
    parecia muito pior do que e' — MAE 0,1671 na tela contra 0,1324 no report
    do mesmo caso. O ajuste ja' partia das constantes do modelo; a linha de
    base tinha ficado para tras, e a tela comparava dois modelos diferentes.
    """
    import numpy as np
    from bolt_analysis_studio.gui.chrome.widgets.reference_curve import (
        curva_do_caso)
    from bolt_analysis_studio.gui.main_window import CalibrationDialog
    from bolt_analysis_studio.validation.store import ValidationStore

    m = modelo_do_caso
    F0 = float(m.global_loading.F_preload)
    ref = curva_do_caso(CASO, F0)
    dlg = CalibrationDialog(None, m, ref)
    for _ in range(30):
        qapp.processEvents()
    dlg._preview_current()
    for _ in range(30):
        qapp.processEvents()
    assert dlg._baseline_ratio is not None, "o preview nao produziu curva"

    pred = np.interp(np.asarray(ref["cycle"], float),
                     np.asarray(dlg._baseline_cycle, float),
                     np.asarray(dlg._baseline_ratio, float))
    mae = float(np.mean(np.abs(pred - np.asarray(ref["F_ratio"], float))))
    dlg.close()

    publicado = ValidationStore().get(CASO).mae
    # 2e-3 e' folga para a grade amostrada do preview contra a grade completa
    # do runner — a mesma razao pela qual os vetores metric_* existem. O que o
    # teste barra e' a divergencia de MODELO, que era de 0,035.
    assert mae == pytest.approx(publicado, abs=2e-3), (
        f"a linha de base do dialogo ({mae:.4f}) nao e' o modelo do caso "
        f"({publicado:.4f})")


@precisa_caso
def test_a_geometria_adotada_entra_no_ajuste(modelo_do_caso, qapp):
    """Sem ela o otimizador media o erro contra uma junta de L_eff=3,125d e
    A_contact=1e-4 nominais em vez da junta do caso."""
    from bolt_analysis_studio.numerical.parameter_identifier import (
        _geom_from_model)

    m = modelo_do_caso
    gov = dict(getattr(m, "_v2_geometry_overrides", {}) or {})
    assert gov, "o caso deveria trazer a geometria adotada"
    geom = _geom_from_model(m)
    for campo, valor in gov.items():
        if hasattr(geom, campo):
            assert getattr(geom, campo) == pytest.approx(float(valor)), campo
