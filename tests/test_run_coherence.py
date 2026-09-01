"""Camada 2 (coerencia de caminho, fatia do filtro): TODO config adotado do
registro de calibracao (New_Theory/adopted_configs.json) deve atravessar
coerce_v2_overrides — o filtro do Run — sem perder nenhum campo de engine e
construir um JointMaterial valido. Pega a classe de bug 'campo descartado =>
usuario roda defaults achando que roda o validado'. End-to-end SolverWorker =
proximo passo da camada 2 (spec na memoria)."""
import json
from pathlib import Path
from bolt_analysis_studio.numerical.dynamic_stiffness_analyzer import JointMaterial
from bolt_analysis_studio.core.solver_worker import coerce_v2_overrides

ROOT = Path(__file__).resolve().parents[1]
NON_ENGINE = {"emb_um", "GA_member", "F_eff", "emb_depth", "N_emb", "C_creep"}
# emb_um/GA/F_eff sao parametros de HARNESS (viram emb_depth/k_member_shear/
# F_amp); os demais sao constantes fisicas passadas fora do dict de overrides.


def test_adopted_configs_survive_run_filter():
    reg = json.loads((ROOT / "New_Theory" / "adopted_configs.json").read_text(encoding="utf-8"))
    valid = JointMaterial.__dataclass_fields__
    checked = 0
    for name, src in reg["sources"].items():
        ov = {k: v for k, v in src["cfg"].items()
              if k not in NON_ENGINE and k in valid}
        if not ov:
            continue
        out = coerce_v2_overrides(ov, valid)
        missing = set(ov) - set(out)
        assert not missing, f"{name}: filtro do Run descartou {missing}"
        jm = JointMaterial(**out)          # constroi sem erro
        for k, v in ov.items():
            got = getattr(jm, k)
            if isinstance(v, (int, float)) and not isinstance(v, bool):
                assert abs(float(got) - float(v)) < 1e-12, f"{name}.{k}: {got} != {v}"
            checked += 1
    assert checked >= 25       # cobertura real (todas as fontes contribuem)


def test_new_forms_fields_pass_filter():
    valid = JointMaterial.__dataclass_fields__
    ov = dict(emb_load_frac=0.4, k_member_shear=8e6, dmg_dwell_exp=1.0,
              f_ref_dmg=10.0, free_spin=1.0, emb_amp_exp=2.375,
              rho_ref_emb=0.667, slip_regime_mode="cattaneo_mindlin",
              couple_famp_slip=True)
    out = coerce_v2_overrides(ov, valid)
    assert set(out) == set(ov)
    assert isinstance(out["slip_regime_mode"], str)
    assert isinstance(out["couple_famp_slip"], bool)
