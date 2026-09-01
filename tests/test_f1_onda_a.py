# -*- coding: utf-8 -*-
"""F1 Onda A (prereg 2026-07-21, gates G1b/G2a/G3b): adocoes risco-zero.

Cobre as tres pecas de wiring da onda A SEM simular curvas longas:
- item 1: _apply_adopted_geometry (cfg cru -> JointGeometry, mm->m; sem as
  chaves -> objeto INTOCADO, mesmo id) e engate kj_mode no __init__;
- item 2: CaseResult.l7_check round-trip (from_dict com/sem o campo — store
  antigo continua carregavel) e contrato do removal_energy_check;
- item 3: check_input k_wear_spec contra as bandas R5 (dentro de qualquer
  banda -> None; fora de todas -> mensagem com fonte; sem quebrar as ancoras
  §4.26 existentes).
"""
import math

from bolt_analysis_studio.calibration.knowledge_base import check_input
from bolt_analysis_studio.numerical.dynamic_stiffness_analyzer import (
    DynamicStiffnessAnalyzer, JointGeometry, JointMaterial)
from bolt_analysis_studio.validation.runner import (CaseResult,
                                                    _apply_adopted_geometry)


# ---------------------------------------------------------------- item 1 ---

def test_apply_adopted_geometry_noop_sem_chaves():
    g = JointGeometry()
    out = _apply_adopted_geometry(g, "FONTE_INEXISTENTE_XYZ", "caso_x", "M12")
    assert out is g                    # intocada (nem copia): paridade por construcao
    assert out.d_hole == 0.0 and out.d_washer == 0.0


def test_apply_adopted_geometry_rousseau_mm_para_m():
    g = JointGeometry()
    out = _apply_adopted_geometry(g, "ROUSSEAU_2025",
                                  "rousseau2025_steel_t10", "M12x1.75")
    # se a adocao F1 ja esta no adopted_configs: 13.6mm/24.0mm em METROS
    if out is not g:
        assert math.isclose(out.d_hole, 13.6e-3)
        assert math.isclose(out.d_washer, 24.0e-3)
        assert out.A_s == g.A_s and out.L_eff == g.L_eff   # resto intocado


def test_kj_mode_engaja_so_com_geometria():
    mat = JointMaterial(kj_mode="pedersen")
    ana_sem = DynamicStiffnessAnalyzer(JointGeometry(), mat, 20e3)
    assert ana_sem.kj_mode_engaged is False       # fallback silencioso
    geo = JointGeometry(d_hole=13.6e-3, d_washer=24e-3)
    ana_com = DynamicStiffnessAnalyzer(geo, JointMaterial(kj_mode="pedersen"),
                                       20e3)
    assert ana_com.kj_mode_engaged is True


# ---------------------------------------------------------------- item 2 ---

def test_caseresult_l7_roundtrip_e_back_compat():
    d_novo = CaseResult(case_id="x", ok=True,
                        l7_check={"implied_J_per_mm3": 5e3, "in_bound": True,
                                  "bound": {"lo": 1.8e3, "hi": 1.05e4}}).to_dict()
    r = CaseResult.from_dict(d_novo)
    assert r.l7_check["in_bound"] is True
    d_antigo = {"case_id": "y", "ok": True}       # store pre-F1: sem o campo
    r2 = CaseResult.from_dict(d_antigo)
    assert r2.l7_check is None


def test_removal_energy_check_contrato_sem_wear():
    ana = DynamicStiffnessAnalyzer(JointGeometry(), JointMaterial(), 20e3)
    chk = ana.energy.removal_energy_check()
    assert chk["implied_J_per_mm3"] is None and chk["in_bound"] is None
    assert chk["bound"]["lo"] > 0                 # banda sempre presente


def test_removal_energy_check_serializavel_com_wear():
    """Regressao do batch 2026-07-21: np.bool_/np.float64 no l7_check
    derrubavam o json.dump do store — tipos devem ser NATIVOS."""
    import json as _json
    ana = DynamicStiffnessAnalyzer(JointGeometry(), JointMaterial(), 30e3)
    for _ in range(30):                            # disp-mode: wear ativo
        ana.step_cycle(0.0, math.pi / 2, 5.0, delta_amp=0.5e-3)
    chk = ana.energy.removal_energy_check()
    _json.dumps(chk)                               # nao pode lancar
    if chk["implied_J_per_mm3"] is not None:
        assert type(chk["implied_J_per_mm3"]) is float
        assert type(chk["in_bound"]) is bool


# ---------------------------------------------------------------- item 3 ---

def test_check_input_k_wear_spec_dentro_de_uma_banda():
    assert check_input("k_wear_spec", 8.34e-15) is None      # thread Zhang
    assert check_input("k_wear_spec", 6.7e-12) is None       # faying Li2025


def test_check_input_k_wear_spec_fora_de_todas():
    msg = check_input("k_wear_spec", 5e-9)
    assert msg is not None and "fora de TODAS as bandas" in msg
    assert "Zhang" in msg or "Li 2025" in msg                # cita fonte


def test_check_input_ancoras_antigas_intactas():
    assert check_input("nome_sem_ancora_qualquer", 1.0) is None
    # mu segue a banda §4.26 (mu_dry) — fora dela avisa, como antes
    aviso = check_input("mu_thread", 9.9)
    assert aviso is None or "banda MEDIDA" in aviso
