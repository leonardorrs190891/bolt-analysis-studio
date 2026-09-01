import json
import pytest
from bolt_analysis_studio.calibration import profiles as P
from bolt_analysis_studio.calibration.profiles import (
    load_profiles,
    save_profiles,
    upsert_profiles_bundle,
)


def test_load_missing_returns_empty(tmp_path):
    assert P.load_profiles(tmp_path / "nope.json") == {}


def test_save_then_load_roundtrip(tmp_path):
    fp = tmp_path / "j.json"
    data = {"profiles": {"nova": {"tuners": {"k_emb_scale": 1.2}}}}
    P.save_profiles(fp, data)
    assert P.load_profiles(fp) == data
    # arquivo e utf-8 valido e indentado
    raw = fp.read_text(encoding="utf-8")
    assert "k_emb_scale" in raw


def test_upsert_creates_and_updates(tmp_path):
    fp = tmp_path / "j.json"
    P.upsert_profile(fp, "nova", {"tuners": {"k_emb_scale": 1.0}})
    P.upsert_profile(fp, "reaperto", {"tuners": {"k_loose_scale_tr": 2.0}})
    data = P.load_profiles(fp)
    assert set(data["profiles"]) == {"nova", "reaperto"}
    P.upsert_profile(fp, "nova", {"tuners": {"k_emb_scale": 1.5}})
    data = P.load_profiles(fp)
    assert data["profiles"]["nova"]["tuners"]["k_emb_scale"] == 1.5


def test_no_temp_file_left_behind(tmp_path):
    fp = tmp_path / "j.json"
    P.save_profiles(fp, {"profiles": {}})
    leftovers = [p.name for p in tmp_path.iterdir() if p.name != "j.json"]
    assert leftovers == []


def test_upsert_profiles_bundle_preserves_shared_block(tmp_path):
    path = tmp_path / "joint_calibrations.json"
    # arquivo pre-existente com bloco shared (Estagio A) + profiles antigos
    save_profiles(path, {
        "schema": 2,
        "shared": {"constants": {"C_creep": 1.165e-11}, "mae_global": 0.0796},
        "profiles": {"old": {"tuners": {}}},
    })
    returned = upsert_profiles_bundle(
        path,
        description="desc nova",
        global_settings={"geometry": "M16"},
        profiles={"nova": {"tuners": {"k_emb_scale": 1.1}}},
    )
    # bloco shared + schema PRESERVADOS
    assert returned["schema"] == 2
    assert returned["shared"]["constants"]["C_creep"] == 1.165e-11
    assert returned["shared"]["mae_global"] == 0.0796
    # profiles/description/global_settings SUBSTITUIDOS
    assert returned["profiles"] == {"nova": {"tuners": {"k_emb_scale": 1.1}}}
    assert "old" not in returned["profiles"]
    assert returned["description"] == "desc nova"
    assert returned["global_settings"] == {"geometry": "M16"}
    # retorno == disco
    assert returned == load_profiles(path)


def test_upsert_profiles_bundle_on_missing_file(tmp_path):
    path = tmp_path / "new.json"
    returned = upsert_profiles_bundle(path, "d", {}, {"nova": {}})
    assert returned["profiles"] == {"nova": {}}
    assert "shared" not in returned  # nada a preservar; nao inventa bloco
