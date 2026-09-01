"""Bloco `shared` (schema 2) no joint_calibrations.json — spec 2026-07-02 §2.6."""
import json

from bolt_analysis_studio.calibration.profiles import (
    load_profiles, save_profiles, upsert_shared,
)


def test_upsert_shared_preserves_profiles_and_sets_schema(tmp_path):
    path = tmp_path / "joint_calibrations.json"
    save_profiles(path, {"profiles": {"nova": {"tuners": {"k_emb_scale": 1.0}}}})

    shared = {
        "calibrated_at": "2026-07-02",
        "free_constants": ["K_archard"],
        "constants": {"K_archard": 2e-4},
        "conditions": {
            "sobretorque": {
                "states": {"F0_test_N": 71000.0, "F0_provenance": "estimated"},
                "MAE": 0.02,
            },
        },
        "loco": {"sobretorque": {"MAE_pred": 0.03}},
    }
    upsert_shared(path, shared)

    data = load_profiles(path)
    assert data["schema"] == 2
    assert data["shared"]["constants"]["K_archard"] == 2e-4
    assert data["shared"]["conditions"]["sobretorque"]["states"]["F0_provenance"] == "estimated"
    # bloco antigo intocado (GUI continua lendo profiles no Estagio A)
    assert data["profiles"]["nova"]["tuners"]["k_emb_scale"] == 1.0
    # arquivo e json valido em utf-8
    assert json.loads(path.read_text(encoding="utf-8"))["schema"] == 2


def test_upsert_shared_on_missing_file_creates_it(tmp_path):
    path = tmp_path / "new.json"
    upsert_shared(path, {"constants": {}})
    data = load_profiles(path)
    assert data["schema"] == 2
    assert data["shared"] == {"constants": {}}


def test_upsert_shared_returns_merged_data_dict(tmp_path):
    path = tmp_path / "j.json"
    save_profiles(path, {"profiles": {"nova": {}}})
    returned = upsert_shared(path, {"constants": {"C_creep": 1e-11}})
    # o RETORNO e o dict completo mesclado (nao so o efeito colateral em disco)
    assert returned["schema"] == 2
    assert returned["shared"]["constants"]["C_creep"] == 1e-11
    assert returned["profiles"]["nova"] == {}
    # e coincide com o que foi persistido
    assert returned == load_profiles(path)


def test_canonical_shared_block_adopted_conformation():
    """Guarda do MILESTONE (2026-07-04): a conformacao (driver effective) foi
    ADOTADA no bloco shared canonico; sobretorque resolvido; escolha physics-first
    {W_conf_ref, C_creep} (emb_depth mantido como INPUT fixo, nao fitado). Guarda
    contra regressao que largue a conformacao ou reintroduza emb_depth no fit."""
    import json
    from pathlib import Path
    root = Path(__file__).resolve().parents[1]
    d = json.loads((root / "New_Theory" / "joint_calibrations.json")
                   .read_text(encoding="utf-8"))
    s = d["shared"]
    assert s["conformation"]["driver"] == "effective"
    assert s["conformation"]["conform_pressure_exp"] == 2.0
    assert set(s["free_constants"]) == {"W_conf_ref", "C_creep"}
    assert "emb_depth" not in s["free_constants"]        # input fixo, nao fitado
    assert s["constants"]["W_conf_ref"] > 0.0            # conformacao ativa
    assert s["conditions"]["sobretorque"]["MAE"] < 0.06  # falsificacao resolvida
