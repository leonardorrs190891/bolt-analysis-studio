"""Fundacao da Fase 1 (confronto com a biblioteca) — spec 2026-07-03 §1.3/§2."""
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "New_Theory"))

from library_common import (  # noqa: E402
    ISO_THREADS, Provenance, emb_depth_vdi, emb_depth_from_early_drop,
    emb_depth_from_curve, frozen_constants, geometry_for, load_full_curve,
)


def test_emb_from_early_drop_matches_li2022ti_provenance():
    # sec4.40 / L24: Li2022ti 15Hz, queda inicial 7.5%, F0=10kN, k_b=4.64e8
    # => emb ~1.6 um (data-implicito), 2x MENOR que o handbook VDI Rz<4 (3.5 um)
    emb, prov = emb_depth_from_early_drop(0.075, 10e3, 4.64e8, vdi_ref_m=3.5e-6)
    assert emb == pytest.approx(1.6e-6, rel=0.05)
    assert prov["provenance"] == "data_implied_early_drop"
    assert prov["ratio_data_over_handbook"] == pytest.approx(1.6 / 3.5, rel=0.05)
    assert prov["diverges"] is True                    # >2x divergencia do handbook


def test_emb_from_early_drop_physics():
    # delta_emb = drop_frac * F0 / k_b (dF_0 = -k_b*delta_emb)
    emb, _ = emb_depth_from_early_drop(0.10, 50e3, 1e8)
    assert emb == pytest.approx(0.10 * 50e3 / 1e8)      # = 5e-5 m
    # queda negativa/zero => emb 0 (clip)
    assert emb_depth_from_early_drop(-0.1, 50e3, 1e8)[0] == 0.0
    # dentro de 2x do handbook => nao marca divergencia
    _, p = emb_depth_from_early_drop(0.05, 10e3, 1e8, vdi_ref_m=4e-6)
    assert p["diverges"] is False


def test_emb_from_curve_reads_second_point():
    cyc = np.array([0.0, 5000.0, 100000.0])
    ratio = np.array([1.0, 0.925, 0.86])               # queda 7.5% ao 2o ponto
    emb, prov = emb_depth_from_curve(cyc, ratio, 10e3, 4.64e8, early_index=1)
    assert emb == pytest.approx(0.075 * 10e3 / 4.64e8, rel=1e-6)
    assert prov["early_cycle"] == 5000.0
    # normaliza por ratio[0] (curva que nao comeca em 1.0)
    emb2, _ = emb_depth_from_curve(cyc, ratio * 1.08, 10e3, 4.64e8, early_index=1)
    assert emb2 == pytest.approx(emb, rel=1e-6)


def test_emb_from_curve_degrades_on_short_curve():
    emb, prov = emb_depth_from_curve([0.0], [1.0], 10e3, 4.64e8, early_index=1)
    assert emb == 0.0 and prov["provenance"] == "degraded"


def test_iso_threads_table_has_the_library_sizes():
    for size, As in [("M6x1.0", 20.1), ("M8x1.25", 36.6), ("M10x1.5", 58.0),
                     ("M12x1.75", 84.3), ("M12x1.5", 88.1), ("M16x2.0", 157.0),
                     ("M30x3.5", 561.0), ("M42x4.5", 1121.0)]:
        assert ISO_THREADS[size]["A_s_mm2"] == pytest.approx(As, rel=0.01), size
    # d2 via ISO 724: d - 0.6495*P
    assert ISO_THREADS["M12x1.75"]["d2_mm"] == pytest.approx(12 - 0.6495 * 1.75,
                                                             abs=0.01)


def test_emb_depth_vdi_axial_fine_ground_two_plates():
    # Rz<10, 1 interface interna, axial: rosca 3 + 2 apoios 2.5 + 1 interface 1.5
    fz, br = emb_depth_vdi("Rz<10", n_inner_interfaces=1, loading="axial")
    assert fz == pytest.approx(9.5e-6, rel=1e-6)
    assert br["thread_um"] == 3.0 and br["bearing_um"] == 2.5
    # classe mais grossa aumenta monotonicamente
    fz_mid, _ = emb_depth_vdi("Rz10-40", 1)
    fz_hi, _ = emb_depth_vdi("Rz40-160", 1)
    assert fz < fz_mid < fz_hi
    # Rz<4 (retificado/lapeado fino; Bolt Science ~1um/interface — NAO VDI) fica
    # ABAIXO do piso VDI: rosca 1.0 + 2 apoios 1.0 + 1 interface 0.5 = 3.5 um << 9.5
    fz_fine, _ = emb_depth_vdi("Rz<4", n_inner_interfaces=1, loading="axial")
    assert fz_fine == pytest.approx(3.5e-6, rel=1e-6)
    assert fz_fine < fz


def test_frozen_constants_read_stage_a_shared_block():
    import json
    from pathlib import Path
    kw, prov = frozen_constants()
    # C_creep = o valor do bloco shared canonico (tracka o fit adotado, NAO um
    # numero fixo — sobrevive a re-fits/adocoes, ex.: adocao da conformacao
    # 2026-07-04 moveu C_creep 1.165e-11 -> 1.867e-11).
    block = json.loads((Path(__file__).resolve().parents[1] / "New_Theory"
                        / "joint_calibrations.json").read_text(encoding="utf-8"))
    assert kw["C_creep"] == pytest.approx(block["shared"]["constants"]["C_creep"])
    assert 1e-12 < kw["C_creep"] < 1e-10          # ordem fisica plausivel
    assert "emb_depth" not in kw          # emb_depth e input por junta (§1.3a)
    assert all(k not in kw for k in ("k_emb_scale", "Phi_tr_correction"))
    assert prov["C_creep"].source == "stage_a"
    # Estagio B (§4.42c): o bloco shared migrou K_archard -> k_wear_spec (razao K/H)
    assert prov["k_wear_spec"].source == "stage_a"   # prior nao-fitado tambem congelado


def test_load_full_curve_reads_digitized_csv():
    cyc, ratio = load_full_curve(
        "Models/CALIBRATION_AND_VALIDATION/curve_library/digitized_csv/"
        "liu2017_axial_F0_18kN.csv")
    assert len(cyc) >= 10 and cyc[0] < cyc[-1]
    assert ratio[-1] == pytest.approx(0.885, abs=0.01)   # nota de aparato


def test_geometry_for_builds_joint_geometry():
    g = geometry_for("M12x1.75", grip_mm=30.0)
    assert g.A_s == pytest.approx(84.3e-6, rel=0.01)
    assert g.L_eff == pytest.approx(0.030)
    assert g.d_2 == pytest.approx(10.863e-3, abs=2e-5)
    assert g.pitch == pytest.approx(1.75e-3)


def test_provenance_record():
    p = Provenance(0.15, "assumed", "mu default MSD_BLOCK_COVERAGE regra 3")
    assert p.source == "assumed"


def test_vdi_adjacent_classes_edges_and_middle():
    from library_common import vdi_adjacent_classes
    assert vdi_adjacent_classes("Rz10-40") == ("Rz<10", "Rz40-160")
    assert vdi_adjacent_classes("Rz<10") == ("Rz<4", "Rz10-40")       # Rz<4 agora e a mais fina
    assert vdi_adjacent_classes("Rz<4") == ("Rz<4", "Rz<10")          # borda inferior (fine-ground)
    assert vdi_adjacent_classes("Rz40-160") == ("Rz10-40", "Rz40-160")  # borda superior


def test_frozen_constants_include_damage_flag():
    from library_common import frozen_constants
    kw, prov = frozen_constants(include_damage=True)
    assert kw["c_D"] == 2.0 and kw["k_dmg_wear"] == 4.0
    assert prov["c_D"].source == "stage_a"
    assert "emb_depth" not in kw          # input por junta SEMPRE excluido
    kw2, _ = frozen_constants()           # default: sem dano (trilho axial)
    assert "c_D" not in kw2


def test_a_contact_is_per_rig_real_bearing_area():
    """roadmap 11g: A_contact = area REAL do anel de apoio por parafuso (nao
    mais 100mm2 fixo). Escala com d^2 => pressao de contato fisica por rig."""
    a8 = geometry_for("M8x1.25", 30.0).A_contact
    a16 = geometry_for("M16x2.0", 40.0).A_contact
    a30 = geometry_for("M30x3.5", 60.0).A_contact
    a42 = geometry_for("M42x4.5", 80.0).A_contact
    assert a8 < a16 < a30 < a42                        # escala com o tamanho
    # M16: pi*(12^2 - 8.8^2) = 209 mm^2 (era 100 mm2 fixo)
    assert a16 == pytest.approx(2.09e-4, rel=0.02)
    # override explicito ainda vence
    assert geometry_for("M16x2.0", 40.0,
                        A_contact_mm2=100.0).A_contact == pytest.approx(1e-4)


def test_a_contact_fix_kills_karlsen_pressure_artifact():
    """Antes (100mm2 fixo) Karlsen M30/M42 dava p/p_ref~7-14 espurio; com a area
    real p=F0/A_contact fica fisica -> p/p_ref ~O(1) (§4.9 Fase 3, 11g)."""
    P_REF = 5e8
    for bolt, A_s_mm2 in [("M30x3.5", 561.0), ("M42x4.5", 1121.0)]:
        F0 = 0.7 * 940e6 * A_s_mm2 * 1e-6             # 70% escoamento (10.9)
        A = geometry_for(bolt, 60.0).A_contact
        assert 0.3 < (F0 / A) / P_REF < 3.0          # O(1), nao 7-14
        assert (F0 / 1e-4) / P_REF > 5.0             # sanity: 100mm2 antigo = espurio
