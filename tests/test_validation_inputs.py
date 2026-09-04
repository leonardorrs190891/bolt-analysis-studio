import numpy as np


def test_geometry_parity_with_library_common():
    # paridade bit-a-bit com a fonte portada (New_Theory/library_common.py)
    import sys
    from pathlib import Path
    from bolt_analysis_studio.validation.inputs import geometry_for, repo_root
    sys.path.insert(0, str(repo_root() / "New_Theory"))
    import library_common as lc
    for size, grip in [("M16x2.0", 40.0), ("M12x1.75", 30.0), ("M8x1.25", 8.0)]:
        a, b = geometry_for(size, grip), lc.geometry_for(size, grip)
        for f in ("A_s", "L_eff", "d_2", "pitch", "r_bearing", "A_contact"):
            assert getattr(a, f) == getattr(b, f), (size, f)


def test_emb_depth_vdi_table():
    from bolt_analysis_studio.validation.inputs import emb_depth_vdi
    total, br = emb_depth_vdi("Rz<10", n_inner_interfaces=1)
    assert abs(total - 9.5e-6) < 1e-12          # 3 + 2*2.5 + 1*1.5 um (trilho axial §4.6)
    assert br["total_um"] == 9.5
    total4, _ = emb_depth_vdi("Rz<4", n_inner_interfaces=1)
    assert abs(total4 - 3.5e-6) < 1e-12         # 1 + 2*1 + 0.5 (Bolt Science)


def test_frozen_constants_reads_shared_block():
    from bolt_analysis_studio.validation.inputs import frozen_constants
    consts, prov = frozen_constants()
    assert "C_creep" in consts and "emb_depth" not in consts    # input por junta, excluido
    assert "c_D" not in consts                                   # dano off por default
    assert all(p.source == "stage_a" for p in prov.values())
    consts_d, _ = frozen_constants(include_damage=True)
    assert "c_D" in consts_d


def test_load_full_curve_le_a_coluna_de_razao():
    """O leitor tem de devolver F/F0, nao a coluna de forca.

    Apontava para um CSV de bancada que saiu do projeto em 2026-09-04; passou a
    apontar para uma curva digitalizada do corpus, que e' versionada e cobre o
    mesmo invariante — o do leitor, nao o daquele ensaio."""
    from bolt_analysis_studio.validation.inputs import load_full_curve
    cyc, ratio = load_full_curve(
        "Models/CALIBRATION_AND_VALIDATION/curve_library/digitized_csv/"
        "lu2024_M8_fig18_amp0p5.csv")
    assert len(cyc) == len(ratio) > 3
    assert 0.0 <= ratio[-1] <= 1.5              # coluna F/F0, nao F_kN


def test_inputs_for_transverse_and_axial():
    from bolt_analysis_studio.core.validation_cases import DIGITIZED_CASES
    from bolt_analysis_studio.validation.inputs import inputs_for
    by_src = {}
    for c in DIGITIZED_CASES:
        by_src.setdefault(c.source.name, c)
    liu25 = inputs_for(by_src["LIU_2025"])
    assert liu25["grip_mm"]["prov"] == "assumed"          # regra 2.5d
    assert liu25["F_amp_N"]["value"] == 0.4 * by_src["LIU_2025"].initial_preload_N
    ax = inputs_for(by_src["LIU_2017_AXIAL"])             # fonte axial agora suportada
    assert ax["rz"]["value"] == "Rz<4"                    # fine-ground (§4.6 resolvido)
    assert ax["grip_mm"]["value"] == 30.0


def ancora_interna():
    # âncora interna 3/4" UNC: fora da tabela ISO, mas o caso carrega d/p em mm
    from bolt_analysis_studio.core.validation_cases import ValidationCaseManager
    from bolt_analysis_studio.validation.inputs import geometry_for_case, inputs_for
    ancora_interna = next(c for c in ValidationCaseManager.get_all_cases()
               if "âncora interna" in c.source.name)
    geom = geometry_for_case(ancora_interna, grip_mm=47.6)
    # A_s generica pi/4*(d-0.9382p)^2 ~ 218 mm2 (A_t tabelado 3/4-10 UNC = 215)
    assert abs(geom.A_s * 1e6 - 218.0) < 5.0
    inp = inputs_for(ancora_interna)                                 # _d_mm nao levanta
    assert abs(inp["grip_mm"]["value"] - 2.5 * 19.05) < 1e-9
