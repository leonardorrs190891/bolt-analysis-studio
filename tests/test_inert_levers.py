"""Alavancas inertes: o que e' decidivel do config vs o que exige o caso.

Importa SO `calibration.parameter_registry` — de proposito. O engine estava sendo
editado por outra sessao quando isto foi escrito, e um teste que o importasse
falharia por motivo alheio. Os defaults de modo entram INJETADOS.
"""
from bolt_analysis_studio.calibration.parameter_registry import (
    channel_gated_levers, inert_levers)

# defaults de modo do engine, injetados para o teste nao depender dele
DEFAULTS = {"k_tr_mode": "axial_frac", "loose_torsion_mode": "legacy"}


def test_c_bend_inerte_no_modo_default():
    """`c_bend` sem `k_tr_mode='bending'` e' no-op — medido: delta 0 exato."""
    fora = inert_levers({"c_bend": 50.0}, defaults=DEFAULTS)
    assert "c_bend" in fora
    msg = fora["c_bend"]
    assert "INERTE" in msg
    assert "k_tr_mode" in msg and "bending" in msg   # diz COMO consertar
    assert "axial_frac" in msg                        # e qual e' o modo efetivo


def test_c_bend_vivo_quando_o_modo_liga():
    """Com o modo certo no proprio overrides, nada de inercia estatica."""
    assert inert_levers({"c_bend": 50.0, "k_tr_mode": "bending"},
                        defaults=DEFAULTS) == {}
    # e' o override que manda, nao o default injetado
    assert inert_levers({"c_bend": 5.0, "k_tr_mode": "bending"},
                        defaults={"k_tr_mode": "axial_frac"}) == {}


def test_campo_ausente_nao_e_reportado():
    """So reporta o que o config REALMENTE seta — nao especula."""
    assert inert_levers({}, defaults=DEFAULTS) == {}
    assert inert_levers({"emb_depth": 3e-5}, defaults=DEFAULTS) == {}


def test_sem_defaults_cai_no_default_do_engine():
    """Sem `defaults`, usa o default de modo tabelado (nao importa o engine)."""
    assert "c_bend" in inert_levers({"c_bend": 1.5})


def test_dict_vazio_NAO_significa_que_a_alavanca_vai_agir():
    """A distincao que da nome ao modulo, presa em teste.

    `loose_arrest_floor` NAO e' gate por modo: a comporta do engine e'
    `if floor <= 0: return 1.0`, chamada sem condicao de modo. Logo `inert_levers`
    corretamente NAO a reporta — e isso nao quer dizer que ela vai surtir efeito.
    Quem responde por ela e' a decomposicao do caso.
    """
    assert inert_levers({"loose_arrest_floor": 0.25}, defaults=DEFAULTS) == {}
    assert "loose_arrest_floor" in channel_gated_levers()


# Canais da DECOMPOSICAO por mecanismo — o vocabulario que uma entrada de
# `channel_gated_levers` tem de usar. Ate 2026-08-05 o teste exigia a palavra
# literal "afrouxamento", o que so funcionava porque as 3 entradas eram todas do
# canal rotacional; a 4a (`flank_fret_depth`, ADOCAO D-Q) nomeia o canal de
# FRETTING DE FLANCO e o teste reprovou uma entrada CORRETA. O invariante que se
# queria e' "a entrada nomeia UM canal", nao "diz esta palavra".
_CANAIS = ("afrouxamento", "fretting", "wear", "creep", "embedding", "fadiga",
           "dano")


def test_canal_gateado_nomeia_o_canal():
    canais = channel_gated_levers()
    assert {"loose_arrest_floor", "eta_loose", "k_j_init"} <= set(canais)
    for campo, canal in canais.items():
        low = canal.lower()
        assert any(c in low for c in _CANAIS), (
            f"{campo}: a descricao tem de NOMEAR o canal gateado (um de "
            f"{_CANAIS}), nao so descrever o campo -- e' o canal que decide a "
            f"inercia, e quem le a tabela precisa saber qual olhar na "
            f"decomposicao. Descricao atual: {canal!r}")
    # nenhuma alavanca aparece nos DOIS mapas: as classes sao disjuntas por
    # construcao (uma nao pode agir; a outra pode nao ter agido)
    estaticas = set(inert_levers({c: 1.0 for c in canais}, defaults=DEFAULTS))
    assert not (estaticas & set(canais))


def test_channel_gated_levers_devolve_copia():
    """Mutar o retorno nao pode corromper a tabela do modulo."""
    a = channel_gated_levers()
    a["xpto"] = "lixo"
    assert "xpto" not in channel_gated_levers()
