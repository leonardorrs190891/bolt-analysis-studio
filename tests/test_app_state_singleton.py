# -*- coding: utf-8 -*-
"""Invariantes do singleton AppState — e a armadilha que os motiva.

CONTEXTO (medido em 2026-07-28). Sob PyQt6 6.11.0, um `__new__` de subclasse de
QObject que devolve instancia pre-existente recursiona no nivel C e mata o
processo com STATUS_STACK_OVERFLOW (0xC00000FD, rc=3221225725). `AppState` usava
exatamente esse idioma, entao `get_app_state()` matava o interpretador — e com
ele TODA a GUI (`run_app.py` e `run_app.py --v2`) mais 4 arquivos de teste. No
CLAUDE.md o sintoma estava registrado como "break PRE-EXISTENTE, crash Qt
isolado no docs_library, suspeito = PyQt6 6.11.0": o suspeito estava certo, o
escopo ("1 teste") errado por duas ordens de grandeza.

Repro minimo que isolou a causa: QObject puro passa; subclasse com pyqtSignal
passa; o `__new__` mata — com ou sem QApplication, e igual com `super().__new__`,
`QObject.__new__` ou `super(C, cls).__new__`.

POR QUE O TESTE ESTRUTURAL VEM PRIMEIRO. Se o idioma voltar, o sintoma nao e' um
teste que falha, e' um processo que MORRE — e processo morto derruba a coleta
inteira sem mensagem util (foi assim que o defeito ficou escondido). O assert em
`__dict__` falha legivel ANTES de qualquer instanciacao. O teste de
comportamento cobre o erro oposto: tirar o `__new__` mas manter a guarda
`_init_done`, que devolveria um QObject meio-construido (sem `super().__init__()`
= sinais mortos), pior que o bug original.
"""


def test_app_state_nao_define_new():
    """Guarda estrutural: `__new__` em subclasse de QObject e' proibido aqui."""
    from bolt_analysis_studio.core.app_state import AppState
    assert "__new__" not in AppState.__dict__, (
        "AppState voltou a definir __new__ — sob PyQt6 6.11.0 isso estoura a "
        "pilha e MATA o processo (nao falha o teste). O singleton pertence ao "
        "getter get_app_state(); ver a nota em AppState._instance.")


def test_guarda_de_init_nao_voltou():
    """`_init_done` nao pode voltar: sem `__new__`, ela produz QObject
    meio-construido em qualquer segunda construcao."""
    from bolt_analysis_studio.core.app_state import AppState
    assert not hasattr(AppState, "_init_done"), (
        "a guarda _init_done voltou sem __new__ — isso faz __init__ retornar "
        "antes de super().__init__() numa 2a construcao (sinais mortos)")


def test_get_app_state_devolve_sempre_a_mesma_instancia(qapp):
    """A GUI depende disto: todos os widgets ligados ao MESMO model_changed."""
    from bolt_analysis_studio.core.app_state import AppState, get_app_state
    a = get_app_state()
    b = get_app_state()
    assert a is b
    # o conftest desconecta receivers lendo AppState._instance — se o cache
    # deixar de ser publicado ali, janelas velhas voltam a acumular entre testes
    assert AppState._instance is a


def test_a_instancia_e_um_qobject_de_fato_construido(qapp):
    """`super().__init__()` rodou: sinais existem e emitem sem estourar."""
    from bolt_analysis_studio.core.app_state import get_app_state
    st = get_app_state()
    recebidos = []
    st.status_changed.connect(recebidos.append)
    st.status_changed.emit("vivo")
    assert recebidos == ["vivo"]
    st.status_changed.disconnect()


def test_construcao_direta_produz_objeto_utilizavel(qapp):
    """Sem a guarda `_init_done`, um `AppState()` direto e' um objeto VALIDO
    (independente, nao o singleton) — e nao um meio-construido."""
    from bolt_analysis_studio.core.app_state import AppState, get_app_state
    solto = AppState()
    assert solto is not get_app_state()
    recebidos = []
    solto.status_changed.connect(recebidos.append)
    solto.status_changed.emit("ok")
    assert recebidos == ["ok"]
