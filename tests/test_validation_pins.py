"""PINOS DE REGRESSAO da fronteira validada (camada 1 da validacao de SOFTWARE,
2026-07-08): casos curtos da galeria rodam aqui com as configs ADOTADAS e o MAE
e' pinado ao valor publicado (+0.015 de folga). Se uma mudanca futura no engine
quebrar o comportamento validado, a suite fica vermelha ANTES do merge.
Fonte da verdade: New_Theory/report_data.json (galeria) + MODEL_LEGITIMACY 4.19/4.20/4.26."""
import io
import json
from pathlib import Path
import numpy as np
import pytest
from bolt_analysis_studio.numerical.dynamic_stiffness_analyzer import (
    DynamicStiffnessAnalyzer, JointMaterial)

ROOT = Path(__file__).resolve().parents[1]
import sys
sys.path.insert(0, str(ROOT / "New_Theory"))
from library_common import geometry_for, frozen_constants, load_full_curve  # noqa: E402

DIG = ROOT / "Models" / "CALIBRATION_AND_VALIDATION" / "curve_library" / "digitized_csv"
PACK = dict(conform_driver="effective", slip_regime_mode="cattaneo_mindlin",
            slip_regime_sharpness=1.0, k_tr_mode="bending",
            loose_torsion_mode="bolt_torsion", eta_loose=15.0)


def _gallery_mae(csv_key):
    """Valor publicado do caso. ATUALIZADO 2026-07-31: a fonte passa a ser o
    STORE CANONICO (validation_store.json), nao mais o report_data.json — a
    galeria de campanha e' um artefato CONGELADO (pre-P0 do LU_2024: pinava
    T16 sob a amplitude errada de 0.5 mm) enquanto o store e' re-carimbado a
    cada adocao/correcao de input. O pin segue medindo o que sempre mediu:
    o harness de refit com a config adotada reproduz o runner canonico."""
    st = json.loads((ROOT / "Models" / "CALIBRATION_AND_VALIDATION"
                     / "validation_store.json").read_text(encoding="utf-8"))
    return float(st[csv_key]["mae"])


def _run(geom, mat, F0, F_amp, freq, delta, n_max, csvpath, trim=0.30):
    ana = DynamicStiffnessAnalyzer(geom, mat, F0)
    cyc, ratio = load_full_curve(str(csvpath))
    keep = ratio >= trim
    cyc_d = cyc[keep]; r_al = ratio[keep] / ratio[keep][0]
    n0 = cyc_d[0]
    r = np.empty(n_max + 1); r[0] = 1.0
    for n in range(1, n_max + 1):
        ana.step_cycle(F_amp, np.pi / 2, freq, delta_amp=delta)
        r[n] = max(ana.state.F_0, 0.0) / F0
    r_alm = r / max(np.interp(n0, np.arange(n_max + 1), r), 1e-9)
    pred = np.interp(cyc_d, np.arange(n_max + 1), r_alm)
    return float(np.mean(np.abs(pred - r_al)))


def test_pin_lu_fig20_T16():
    # Fidelidade de config, 3a era (2026-08-20). Historia do pin:
    # 2026-07-31 ele deixou de congelar uma receita hardcoded e passou a LER a
    # config adotada, rodando-a pelo harness lu_fig20_refit. Em 2026-08-20 a
    # adocao lu2024-t16-emb-ancorado (per_case: floor 0,195 lido + emb 4um
    # ancorado no c1) expos que o harness e' de uma era PRE-PACK: ele nao
    # monta pack/modos (c_bend=30 sem k_tr_mode=bending e' inerte nele, gotcha
    # documentado) nem a geometria per-case do runner — medido: harness da
    # 0,139-0,148 onde o canonico da 0,0226, mesmo com o grupo INTEIRO. Um pin
    # que compara instrumentos DIFERENTES nao mede fidelidade de config.
    # O que "config adotada reproduz a galeria" significa hoje: o RUNNER
    # CANONICO com a config lida do kb tem de bater o STORE gravado — isso
    # pega o hazard real (store dessincronizado da config, ja aconteceu no
    # reinicio de 2026-07-28) e acompanha adocoes por construcao.
    import bolt_analysis_studio.validation.runner as rn
    from bolt_analysis_studio.validation.case_registry import record
    d = rn.simulate_case(record("lu2024_M8_fig20_T16Nm")).to_dict()
    assert abs(d["mae"] - _gallery_mae("lu2024_M8_fig20_T16Nm")) <= 1e-9, (
        "runner canonico com a config adotada nao reproduz o store: "
        f"{d['mae']:.6f} vs {_gallery_mae('lu2024_M8_fig20_T16Nm'):.6f} — "
        "store dessincronizado? re-simule (parallel_batch --store)")


def test_pin_hdpe_t10():
    # sec4.20: k_member_shear + F_eff stack-limited
    consts, _ = frozen_constants()
    geom = geometry_for("M12x1.75", 25.0)
    k_m = 8e4 / 0.010
    I = np.pi * geom.d_2 ** 4 / 64
    k_ser = 1.0 / (1.0 / max(4.0 * geom.E * I / geom.L_eff ** 3, 1.0) + 1.0 / k_m)
    F_eff = min(0.4 * 10250.0, k_ser * 0.5e-3)
    mat = JointMaterial(emb_depth=2e-6, mu_thread=0.15, mu_bearing=0.15,
                        k_j_init=2.0e7, k_member_shear=k_m,
                        c_bend=4.0, loose_arrest_floor=0.28,
                        **{k: v for k, v in PACK.items()}, **consts)
    mae = _run(geom, mat, 10250.0, F_eff, 1.0, 0.5e-3, 400,
               DIG / "rousseau2025_hdpe_t10.csv", trim=0.0)
    assert mae <= _gallery_mae("rousseau2025_hdpe_t10") + 0.015
