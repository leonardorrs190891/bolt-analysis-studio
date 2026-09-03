"""Importar caso da validacao pelo nome (2026-09-03).

Os 210 .msd existiam e a unica porta era Ctrl+O: para abrir uma curva era
preciso saber em qual das 29 pastas de fonte ela mora e o nome exato do
arquivo. Este dialogo lista tudo com busca.

Dois invariantes valem mais que o resto:

1. O que o dialogo mostra por padrao e' o CENSO DO ARTIGO — 205 de 210, pelo
   mesmo `caso_comparavel` do Apendice B. Se o dialogo tivesse a sua propria
   nocao de censo, ela divergiria do manuscrito no primeiro ajuste.
2. Importar NAO adota o arquivo de origem como destino de Ctrl+S. Os casos
   sao regerados por `build_saved_cases.py` e versionados; um Ctrl+S
   distraido depois de mexer no modelo reescreveria a referencia do artigo.
"""
import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "src"))

import pytest                                                    # noqa: E402

CASOS = RAIZ / "Models" / "SAVED_CASES"
INDICE = CASOS / "indice.json"
precisa_indice = pytest.mark.skipif(
    not INDICE.is_file(), reason="rode New_Theory/build_saved_cases.py")


@pytest.fixture
def janela(qapp):
    from bolt_analysis_studio.core.app_state import get_app_state
    from bolt_analysis_studio.gui.chrome.app_window import ChromeWindow
    return ChromeWindow(get_app_state())


@pytest.fixture
def picker(qapp):
    from bolt_analysis_studio.gui.chrome.widgets.case_picker import CasePicker
    return CasePicker()


def _folhas(dlg):
    """Os casos visiveis: filhos dos nos de fonte."""
    arv = dlg.arvore
    return [arv.topLevelItem(i).child(j)
            for i in range(arv.topLevelItemCount())
            for j in range(arv.topLevelItem(i).childCount())]


def test_o_menu_arquivo_tem_importar_com_ctrl_i(janela):
    """O INDICE.md gerado anuncia Ctrl+I; se o item sumir, a documentacao
    passa a prometer um atalho que nao existe."""
    from PyQt6.QtWidgets import QMenu

    arq = [m for m in janela.menuBar().findChildren(QMenu)
           if m.title() == "Arquivo"][0]
    acoes = {a.text(): a for a in arq.actions()}
    assert "Importar caso da validação…" in acoes, list(acoes)
    assert acoes["Importar caso da validação…"].shortcut().toString() == "Ctrl+I"

    # ao lado de "Nova Analise", que foi o pedido
    textos = [a.text() for a in arq.actions()]
    assert (textos.index("Importar caso da validação…")
            - textos.index("Nova Análise…")) <= 2


@precisa_indice
def test_o_indice_conta_o_mesmo_censo_que_o_apendice_b():
    """A fonte da verdade e' `caso_comparavel`, nao um numero digitado."""
    from bolt_analysis_studio.validation.report_html import caso_comparavel

    d = json.loads(INDICE.read_text(encoding="utf-8"))
    for c in d["casos"]:
        assert c["censo"] == bool(caso_comparavel(c["source"], c["case_id"])), \
            c["case_id"]
    assert d["no_censo"] == sum(c["censo"] for c in d["casos"])
    assert d["total"] == len(d["casos"]) == 210
    assert d["no_censo"] == 205
    assert d["atendem_criterio"] == 171


@precisa_indice
def test_todo_caso_do_indice_tem_o_arquivo_no_lugar():
    d = json.loads(INDICE.read_text(encoding="utf-8"))
    faltando = [c["arquivo"] for c in d["casos"]
                if not (CASOS / c["arquivo"]).is_file()]
    assert not faltando, faltando[:5]


@precisa_indice
def test_por_padrao_mostra_o_censo_e_a_caixa_revela_os_210(picker):
    assert picker.so_censo.isChecked()
    assert len(_folhas(picker)) == 205

    picker.so_censo.setChecked(False)
    assert len(_folhas(picker)) == 210


@precisa_indice
def test_a_busca_filtra_por_artigo_e_por_caso(picker):
    from PyQt6.QtCore import Qt

    picker.busca.setText("lu2024")
    fontes = {picker.arvore.topLevelItem(i).text(0).split()[0]
              for i in range(picker.arvore.topLevelItemCount())}
    assert fontes == {"LU_2024"}

    picker.busca.setText("fig18_amp0p5")
    folhas = _folhas(picker)
    assert len(folhas) == 1
    assert folhas[0].data(0, Qt.ItemDataRole.UserRole)["case_id"] == \
        "lu2024_M8_fig18_amp0p5"


@precisa_indice
def test_a_busca_sem_resultado_nao_quebra(picker):
    picker.busca.setText("nao existe este caso")
    assert _folhas(picker) == []
    assert picker.arvore.topLevelItemCount() == 0


@precisa_indice
def test_escolher_devolve_o_caminho_do_msd(picker, qapp):
    picker.busca.setText("fig18_amp0p5")
    folha = _folhas(picker)[0]
    picker.arvore.setCurrentItem(folha)
    picker._aceitar()
    assert picker.escolhido is not None
    assert Path(picker.escolhido).is_file()
    assert Path(picker.escolhido).name == "lu2024_M8_fig18_amp0p5.msd"


@precisa_indice
def test_importar_carrega_as_constantes_adotadas(janela, qapp):
    """Importar tem que trazer o caso na configuracao do artigo, nao um
    esqueleto: sao as 23 constantes que fazem a curva bater."""
    alvo = CASOS / "LU_2024" / "lu2024_M8_fig18_amp0p5.msd"
    assert janela._carrega_projeto(str(alvo), como_projeto=False)
    for _ in range(40):
        qapp.processEvents()
    m = janela.app_state.model
    assert len(m.elements) == 11
    assert len(getattr(m, "_v2_tuner_overrides", {})) == 23
    assert janela.model_controller.schematic.scene().items()


@precisa_indice
def test_importar_nao_deixa_ctrl_s_sobrescrever_o_caso_do_repositorio(
        janela, qapp):
    """A protecao. Depois de importar, Ctrl+S nao pode gravar por cima do
    arquivo versionado — tem que cair em "Salvar como"."""
    alvo = CASOS / "LU_2024" / "lu2024_M8_fig18_amp0p5.msd"
    antes = alvo.read_bytes()
    janela._carrega_projeto(str(alvo), como_projeto=False)
    for _ in range(40):
        qapp.processEvents()
    assert janela._caminho_projeto is None

    chamou = []
    janela._salvar_projeto_como = lambda: chamou.append(True)
    janela._salvar_projeto()
    assert chamou == [True], "Ctrl+S gravou direto no caso do repositorio"
    assert alvo.read_bytes() == antes


def test_sem_indice_o_dialogo_abre_vazio_em_vez_de_estourar(qapp, monkeypatch):
    """O app instalado pode nao ter os casos gerados; abrir o dialogo nao
    pode virar traceback."""
    from bolt_analysis_studio.gui.chrome.widgets import case_picker

    monkeypatch.setattr(case_picker, "caminho_indice", lambda: None)
    dlg = case_picker.CasePicker()
    assert _folhas(dlg) == []
    assert "0" in dlg.resumo.text()
