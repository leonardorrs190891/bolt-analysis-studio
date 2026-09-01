"""Camada 4: parameter_registry expoe as bandas MEDIDAS das ancoras (sec4.26)
como priors de fit + guarda de proveniencia de input."""
from bolt_analysis_studio.calibration.parameter_registry import (
    anchor_priors, check_input_provenance)


def test_priors_load_from_registry():
    pri = anchor_priors()
    assert "mu_dry" in pri and "C_creep_por_par" in pri
    lo, hi = pri["mu_dry"]["banda_medida"]
    assert 0.10 < lo < hi < 0.25


def test_provenance_guard():
    assert check_input_provenance("mu_thread", 0.15) is None      # dentro
    msg = check_input_provenance("mu_thread", 0.40)               # seco absurdo
    assert msg and "fora da banda" in msg and "qiao" in msg.lower()
    assert check_input_provenance("emb_depth", 99.0) is None      # sem ancora -> None


def test_guarda_aceita_o_nome_do_PRIOR_e_nao_so_o_do_campo():
    """A armadilha de 2026-07-28: `mu_dry` devolvia None EM SILENCIO.

    O mapa de nomes so tinha campos do engine (`mu_thread`, `mu_bearing`), entao
    chamar a guarda com o nome do proprio prior (`mu_dry`) caia no ramo
    "desconhecido -> None" — indistinguivel de "dentro da banda". 0,35 esta muito
    fora de [0,14; 0,19] e passava calado. Achado ao verificar o comportamento
    para escrever o volume 3 do Manual.
    """
    # o nome do PRIOR agora avisa...
    msg = check_input_provenance("mu_dry", 0.35)
    assert msg and "fora da banda" in msg
    # ...e continua concordando com o nome do CAMPO, que e' o mesmo prior
    assert check_input_provenance("mu_bearing", 0.35)
    assert check_input_provenance("mu_dry", 0.15) is None          # dentro
    # F_amp_ratio tem banda medida e tambem era inalcancavel pelo nome do prior
    assert check_input_provenance("F_amp_ratio", 0.9)
    assert check_input_provenance("F_amp_ratio", 0.4) is None


def test_checkable_inputs_desambigua_o_None():
    """`None` significa "dentro da banda" OU "nao sei checar" — este set separa."""
    from bolt_analysis_studio.calibration.parameter_registry import (
        anchor_priors as _ap, checkable_inputs)
    nomes = checkable_inputs()
    # os que TEM banda medida entram, pelos dois nomes
    assert {"mu_dry", "mu_bearing", "mu_thread", "conform_pressure_exp",
            "fat_sigma_endurance", "F_amp_ratio", "k_wear_spec"} <= nomes
    # os que NAO tem banda ficam fora — e' exatamente sobre eles que o None mente
    for sem_banda in ("emb_depth", "N_emb", "C_creep_por_par"):
        assert sem_banda in _ap()                 # o prior existe...
        assert sem_banda not in nomes             # ...mas nao e' checavel
        assert check_input_provenance(sem_banda, 1e9) is None
    # invariante: todo nome checavel que recebe um valor absurdo TEM de avisar
    for nome in ("mu_dry", "conform_pressure_exp", "fat_sigma_endurance"):
        assert check_input_provenance(nome, -1.0), nome
