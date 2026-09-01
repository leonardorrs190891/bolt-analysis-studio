import numpy as np
import pytest
from bolt_analysis_studio.calibration import server as S


def _payload(N=300, N_I=50, N_II=200, reference=None):
    # mantem N_I < N_II <= N pra StageSegmentation ser valida
    return {
        "geom": {"A_s": 157e-6, "L_eff": 0.050, "d_2": 14.701e-3,
                 "pitch": 2.0e-3, "r_bearing": 12e-3, "A_contact": 1e-4},
        "mat": {"k_emb_scale": 1.0, "k_creep_scale": 1.0,
                "k_wear_scale_tr": 1.0, "k_loose_scale_tr": 1.0,
                "Phi_tr_correction": 1.0, "k_damage_scale": 1.0,
                "c_D": 0.0, "W_ref": 1.0e4, "k_dmg_mu": 0.0, "k_dmg_wear": 0.0},
        "loading": {"F0_init": 50_000.0, "F_amp": 20_000.0,
                    "theta": np.pi / 2, "freq": 0.5, "N": N,
                    "delta_amp": 0.5e-3, "D_init": 0.0},
        "segments": {"N_I": N_I, "N_II": N_II},
        "reference": reference if reference is not None
        else [[0, 1.0], [50, 0.78], [200, 0.57]],
    }


def test_simulate_shape_and_fidelity():
    out = S.handle_simulate(_payload(N=300))
    assert len(out["curve"]["N"]) == 301
    assert "embedding" in out["decomposition"]
    assert set(out["segments"]) == {"I", "II", "III"}
    assert "conservation_residual" in out["energy"]
    # fidelidade: bate com chamada in-process direta do engine
    from bolt_analysis_studio.numerical.dynamic_stiffness_analyzer import (
        DynamicStiffnessAnalyzer, JointGeometry, JointMaterial)
    geom = JointGeometry(A_s=157e-6, L_eff=0.050, d_2=14.701e-3,
                         pitch=2.0e-3, r_bearing=12e-3, A_contact=1e-4)
    ana = DynamicStiffnessAnalyzer(geom, JointMaterial(), 50_000.0)
    for _ in range(300):
        ana.step_cycle(20_000.0, np.pi / 2, 0.5, delta_amp=0.5e-3)
    assert abs(out["curve"]["ratio"][-1] - ana.state.F_0 / 50_000.0) < 1e-9


def test_simulate_bad_payload_raises():
    with pytest.raises(ValueError):
        S.handle_simulate({"geom": {}})       # faltando campos


def test_material_accepts_sequence_field_mu_bearing_schedule():
    """Campo SEQUENCIAL de JointMaterial nao pode derrubar o /simulate.

    Bug reproduzido em 2026-07-28 (item 6 "LATENTE" da auditoria de 07-27):
    `_material` fazia float() em todo campo nao-str, entao um payload com
    `mu_bearing_schedule` (tupla (N, mu), default `()`) levantava TypeError.
    E' justamente o campo que o encanamento do mu(N) per-ciclo precisa mandar
    pela via do tuner HTML. O JSON entrega lista de listas => tupla de tuplas.
    """
    p = _payload(N=250)                              # N >= N_II do _payload
    p["mat"] = {"mu_bearing_schedule": [[0, 0.20], [250, 0.10]]}
    out = S.handle_simulate(p)                       # nao levanta TypeError
    assert len(out["curve"]["ratio"]) == 251

    # e o schedule tem EFEITO: mu(N) interpolado muda a trajetoria vs o default.
    # `mat` nao pode ser vazio (o server recusa), entao o controle manda o
    # PROPRIO default de emb_depth — payload nao-vazio e fisicamente neutro.
    base = _payload(N=250)
    base["mat"] = {"emb_depth": 30e-6}
    assert (abs(out["curve"]["ratio"][-1]
                - S.handle_simulate(base)["curve"]["ratio"][-1]) > 1e-6)


def test_material_coercion_is_type_aware():
    """str passa, sequencia passa como tupla, numero vira float."""
    p = _payload(N=10)
    p["mat"] = {"conform_driver": "effective", "emb_depth": 3e-5,
                "mu_bearing_schedule": [[0, 0.15]]}
    mat = S._material(p)
    assert mat.conform_driver == "effective"        # str intacta
    assert isinstance(mat.emb_depth, float)         # numero coagido
    assert mat.mu_bearing_schedule == ((0, 0.15),)  # lista -> tupla de tuplas


def test_calibrate_retired_stage_b():
    # ESTAGIO B (2026-07-09): /calibrate (StagedCalibrator, fit de tuners)
    # aposentado com a remocao da camada de tuners. Deve recusar claramente.
    p = _payload(N=2500, N_I=100, N_II=1000,
                 reference=[[0, 1.0], [100, 0.64], [500, 0.43], [2500, 0.26]])
    with pytest.raises(NotImplementedError, match="Estagio B"):
        S.handle_calibrate(p)


def test_profiles_reads_json():
    out = S.handle_profiles()
    assert "profiles" in out
    assert "nova" in out["profiles"]


# ------------------------------------------------------------------ /shared
def test_shared_returns_canonical_constants():
    # bloco `shared` = caminho canonico pos-Estagio-B (constantes fisicas).
    out = S.handle_shared()
    assert isinstance(out, dict)
    assert "constants" in out
    c = out["constants"]
    for k in ("emb_depth", "C_creep", "k_wear_spec", "tr_loose_gain", "W_conf_ref"):
        assert k in c, f"constante canonica ausente: {k}"
    # conformacao dependente de pressao adotada (driver effective, spec §7)
    assert out.get("conformation", {}).get("driver") == "effective"


# ------------------------------------------------- serving estatico + traversal
def test_content_type_for():
    assert S.content_type_for("x.html").startswith("text/html")
    assert S.content_type_for("g.svg") == "image/svg+xml"
    assert S.content_type_for("d.json").startswith("application/json")
    assert S.content_type_for("z.weird") == "application/octet-stream"


def test_resolve_static_serves_file_inside_base(tmp_path):
    (tmp_path / "sub").mkdir()
    (tmp_path / "sub" / "ok.html").write_text("<h1>ok</h1>", encoding="utf-8")
    got = S.resolve_static("sub/ok.html", base=tmp_path)
    assert got is not None
    assert got.read_text(encoding="utf-8") == "<h1>ok</h1>"
    # arquivo inexistente (mas caminho seguro) => None
    assert S.resolve_static("sub/missing.html", base=tmp_path) is None
    # string vazia => None
    assert S.resolve_static("", base=tmp_path) is None


def test_resolve_static_denies_traversal(tmp_path):
    base = tmp_path / "validation_html"
    base.mkdir()
    (tmp_path / "secret.txt").write_text("nope", encoding="utf-8")
    # subir de nivel deve ser bloqueado MESMO com o arquivo existindo
    assert S.resolve_static("../secret.txt", base=base) is None
    assert S.resolve_static("..\\secret.txt", base=base) is None
    assert S.resolve_static("../../secret.txt", base=base) is None
    # caminho absoluto injetado e' neutralizado (fica dentro da base) => None
    assert S.resolve_static("/etc/passwd", base=base) is None


def test_resolve_static_denies_traversal_against_real_base():
    # contra a base real validation_html/: nao pode escapar p/ src/ nem New_Theory/
    assert S.resolve_static(
        "../../src/bolt_analysis_studio/calibration/server.py") is None
    assert S.resolve_static("../joint_calibrations.json") is None
