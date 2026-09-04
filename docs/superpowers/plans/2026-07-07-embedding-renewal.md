# Embedding Renewal on Re-tightening — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a quasi-static `retighten()` operation with a damage-coupled embedding-renewal
rule and a torque→preload recovery model to the V2 engine, then validate it against the
Liu2022 sequential re-tightening dataset (dry vs oil).

**Architecture:** Three engine additions — a `tightening_torque` helper (Motosh, reusing
existing μ terms), a `JointMaterial.k_emb_renew` field (default 0 = inert), and a
`DynamicStiffnessAnalyzer.retighten()` state-operation — plus a `New_Theory` validation
harness that runs the real protocol (tighten → 5000 cyc → retighten ×4) and evaluates five
pre-registered gates. Falsify-first: no galling term; the frozen physics is left to
confirm or falsify the dry recovery/loosening trends.

**Tech Stack:** Python 3, numpy, pytest. Engine: `dynamic_stiffness_analyzer.py`. Data:
`Models/CALIBRATION_AND_VALIDATION/curve_library/digitized_csv/liu2022_*.csv`.

## Global Constraints

- **Opt-in / default-inert:** `k_emb_renew` default `0.0`; `retighten` is a new method never
  called by existing sims. With `k_emb_renew=0`, `retighten` must leave `δ_emb` exactly
  unchanged (bit-identical backward-compat).
- **File encoding:** always `encoding='utf-8'` for file I/O (Windows charmap otherwise).
- **Syntax-check after every engine edit:** `python -c "import ast; ast.parse(open('PATH', encoding='utf-8').read()); print('OK')"`.
- **Tests import via `tests/conftest.py`** (puts `src/` on `sys.path`; no editable install).
- **Frozen constants** for validation come from `New_Theory/library_common.frozen_constants(include_damage=True)`
  (`c_D=2.0`, `k_dmg_wear=4.0`; `k_dmg_mu` absent=0). `emb_depth` is overridden per-joint.
- **Falsify-first:** do NOT add a galling / geometric-recovery term (spec §7, deferred).
- Reference: spec `docs/superpowers/specs/2026-07-07-embedding-renewal-design.md`.

---

### Task 1: `tightening_torque` helper (Motosh torque↔preload)

**Files:**
- Modify: `src/bolt_analysis_studio/numerical/dynamic_stiffness_analyzer.py` (add module
  function near `T_resistance`, ~line 437)
- Test: `tests/test_retightening.py` (create)

**Interfaces:**
- Consumes: `SlowState`, `JointGeometry`, `JointMaterial`, `mu_bearing_eff`,
  `THREAD_FLANK_ANGLE` (all existing in the module).
- Produces: `tightening_torque(F0: float, state: SlowState, geom: JointGeometry, mat: JointMaterial) -> float`
  — tightening torque [N·m] to reach preload `F0` [N]. Linear in `F0`, so callers invert
  via `F0 = T / tightening_torque(1.0, state, geom, mat)`.

- [ ] **Step 1: Write the failing test**

Create `tests/test_retightening.py`:

```python
import numpy as np
import pytest
from bolt_analysis_studio.numerical.dynamic_stiffness_analyzer import (
    DynamicStiffnessAnalyzer, JointGeometry, JointMaterial, SlowState,
    tightening_torque, THREAD_FLANK_ANGLE,
)


def _m12_geom():
    # M12x1.75: A_s=84.3 mm^2, d2=10.86 mm, pitch=1.75 mm, r_bearing=9 mm, grip=30 mm
    return JointGeometry(A_s=84.3e-6, L_eff=30e-3, d_2=10.86e-3,
                         pitch=1.75e-3, r_bearing=9e-3, A_contact=117.6e-6)


def test_tightening_torque_roundtrip():
    geom = _m12_geom()
    mat = JointMaterial(mu_thread=0.2, mu_bearing=0.2)
    st = SlowState(F_0=20000.0, F_0_init=20000.0)
    T = tightening_torque(20000.0, st, geom, mat)
    coeff = tightening_torque(1.0, st, geom, mat)
    assert abs(T / coeff - 20000.0) < 1e-6                 # linear inversion
    assert 15e3 < 80.0 / coeff < 30e3                      # M12 dry: 80 Nm -> ~20-28 kN


def test_tightening_torque_zero_damage_no_mu_coupling():
    # Frozen physics has k_dmg_mu=0 -> damage must NOT change the coeff (flat recovery).
    geom = _m12_geom()
    mat = JointMaterial(mu_thread=0.2, mu_bearing=0.2)   # k_dmg_mu default 0.0
    c0 = tightening_torque(1.0, SlowState(F_0=2e4, F_0_init=2e4, D=0.0), geom, mat)
    cD = tightening_torque(1.0, SlowState(F_0=2e4, F_0_init=2e4, D=0.3), geom, mat)
    assert abs(cD - c0) < 1e-15                            # flat: D has no effect at k_dmg_mu=0


def test_tightening_torque_kdmgmu_raises_recovery():
    # If k_dmg_mu>0 were set, damage lowers mu_bearing_eff -> lower coeff -> MORE recovery.
    geom = _m12_geom()
    mat = JointMaterial(mu_thread=0.2, mu_bearing=0.2, k_dmg_mu=1.0)
    c0 = tightening_torque(1.0, SlowState(F_0=2e4, F_0_init=2e4, D=0.0), geom, mat)
    cD = tightening_torque(1.0, SlowState(F_0=2e4, F_0_init=2e4, D=0.3), geom, mat)
    assert cD < c0
    assert 80.0 / cD > 80.0 / c0                           # pre-registered wrong sign
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_retightening.py -q`
Expected: FAIL with `ImportError: cannot import name 'tightening_torque'`.

- [ ] **Step 3: Write minimal implementation**

In `dynamic_stiffness_analyzer.py`, immediately after `T_resistance` (~line 437), add:

```python
def tightening_torque(F0: float, state: SlowState, geom: JointGeometry,
                      mat: JointMaterial) -> float:
    """Torque de aperto (Motosh) para atingir a pre-carga F0 [N] -> T [N.m].

        T = F0 * ( p/2pi + mu_th*d2/(2 cos alpha) + mu_bearing_eff(D)*r_bearing )

    Reusa os termos de atrito de T_resistance + o termo de avanco (lead). Linear
    em F0, entao a pre-carga atingida por um torque T e
    F0 = T / tightening_torque(1.0, state, geom, mat). Reusa mu_bearing_eff(D):
    com k_dmg_mu=0 (frozen) o coeficiente independe de D (recuperacao plana).
    """
    coeff = (geom.lead_per_radian
             + mat.mu_thread * geom.d_2 / (2.0 * np.cos(THREAD_FLANK_ANGLE))
             + mu_bearing_eff(state, mat) * geom.r_bearing)
    return max(F0, 0.0) * coeff
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_retightening.py -q`
Expected: 3 passed.

- [ ] **Step 5: Syntax-check + commit**

```bash
python -c "import ast; ast.parse(open('src/bolt_analysis_studio/numerical/dynamic_stiffness_analyzer.py', encoding='utf-8').read()); print('OK')"
git add src/bolt_analysis_studio/numerical/dynamic_stiffness_analyzer.py tests/test_retightening.py
git commit -m "feat(engine): tightening_torque helper (Motosh torque<->preload)"
```

---

### Task 2: `k_emb_renew` field + `retighten()` operation

**Files:**
- Modify: `src/bolt_analysis_studio/numerical/dynamic_stiffness_analyzer.py`
  (add `k_emb_renew` field to `JointMaterial` near `k_emb_scale` ~line 144; add `retighten`
  method to `DynamicStiffnessAnalyzer` after `step_cycle` ~line 1060)
- Test: `tests/test_retightening.py` (append)

**Interfaces:**
- Consumes: `tightening_torque` (Task 1), `U_internal`, `EnergyBudget` (existing).
- Produces:
  - `JointMaterial.k_emb_renew: float = 0.0` — embedding renewal fraction per unit damage.
  - `DynamicStiffnessAnalyzer.retighten(applied_torque: Optional[float] = None, new_F0: Optional[float] = None) -> None`
    — exactly one arg. Sets `state.F_0` (predicted from torque, or explicit), renews
    `state.delta_emb ← delta_emb·(1 − k_emb_renew·D)` clamped `[0, target]`, sets
    `state.theta_loose = 0`, rebases the energy budget. Persists everything else incl.
    `_cycle_counter` (creep clock), `D`, `delta_creep`, `delta_wear`, `F_0_init`.

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_retightening.py`:

```python
def test_retighten_new_F0_sets_preload_and_resets_theta():
    ana = DynamicStiffnessAnalyzer(_m12_geom(), JointMaterial(), 20000.0)
    ana.state.theta_loose = 0.05
    ana.state.F_0 = 15000.0
    f0_init = ana.state.F_0_init
    ana.retighten(new_F0=19000.0)
    assert ana.state.F_0 == 19000.0
    assert ana.state.theta_loose == 0.0
    assert ana.state.F_0_init == f0_init            # GW reference unchanged


def test_retighten_default_keeps_delta_emb_backward_compat():
    ana = DynamicStiffnessAnalyzer(_m12_geom(), JointMaterial(), 20000.0)  # k_emb_renew=0
    ana.state.delta_emb = 5e-6
    ana.state.D = 0.3
    ana.retighten(new_F0=19000.0)
    assert ana.state.delta_emb == 5e-6              # inert: no renewal


def test_retighten_renews_delta_emb_with_damage():
    ana = DynamicStiffnessAnalyzer(_m12_geom(), JointMaterial(k_emb_renew=1.0), 20000.0)
    ana.state.delta_emb = 6e-6
    ana.state.D = 0.3
    ana.retighten(new_F0=19000.0)
    assert abs(ana.state.delta_emb - 6e-6 * (1.0 - 1.0 * 0.3)) < 1e-15   # 4.2e-6


def test_retighten_renewal_clamped_nonnegative():
    ana = DynamicStiffnessAnalyzer(_m12_geom(), JointMaterial(k_emb_renew=5.0), 20000.0)
    ana.state.delta_emb = 6e-6
    ana.state.D = 0.9                                # k*D=4.5 > 1 -> would go negative
    ana.retighten(new_F0=19000.0)
    assert ana.state.delta_emb == 0.0               # clamped


def test_retighten_persists_damage_creep_wear_and_clock():
    ana = DynamicStiffnessAnalyzer(_m12_geom(), JointMaterial(), 20000.0)
    for _ in range(10):
        ana.step_cycle(5000.0, np.pi / 2, 12.5, delta_amp=0.3e-3)
    cc, D, dc, dw = (ana._cycle_counter, ana.state.D,
                     ana.state.delta_creep, ana.state.delta_wear)
    ana.retighten(new_F0=19000.0)
    assert ana._cycle_counter == cc                 # creep clock persists
    assert ana.state.D == D
    assert ana.state.delta_creep == dc
    assert ana.state.delta_wear == dw


def test_retighten_torque_predicts_flat_recovery_at_kdmgmu0():
    geom = _m12_geom()
    mat = JointMaterial(mu_thread=0.2, mu_bearing=0.2)     # k_dmg_mu=0
    ana = DynamicStiffnessAnalyzer(geom, mat, 20000.0)
    ana.state.F_0 = 12000.0
    ana.state.D = 0.3
    ana.retighten(applied_torque=80.0)
    coeff = tightening_torque(1.0, ana.state, geom, mat)
    assert abs(ana.state.F_0 - 80.0 / coeff) < 1e-6
    assert 15e3 < ana.state.F_0 < 30e3


def test_retighten_rebases_energy_budget():
    ana = DynamicStiffnessAnalyzer(_m12_geom(), JointMaterial(), 20000.0)
    for _ in range(50):
        ana.step_cycle(5000.0, np.pi / 2, 12.5, delta_amp=0.3e-3)
    ana.retighten(new_F0=19000.0)
    assert ana.energy.W_ext == 0.0
    assert ana.energy.W_diss_total == 0.0
    assert abs(ana.energy.U_released) < 1e-9        # U_stored == U_stored_init (fresh baseline)
    assert abs(ana.energy.conservation_residual) < 1e-9


def test_retighten_requires_exactly_one_arg():
    ana = DynamicStiffnessAnalyzer(_m12_geom(), JointMaterial(), 20000.0)
    with pytest.raises(ValueError):
        ana.retighten()
    with pytest.raises(ValueError):
        ana.retighten(applied_torque=80.0, new_F0=19000.0)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/test_retightening.py -q`
Expected: FAIL — `TypeError: __init__() got an unexpected keyword argument 'k_emb_renew'`
and `AttributeError: 'DynamicStiffnessAnalyzer' object has no attribute 'retighten'`.

- [ ] **Step 3: Add the `k_emb_renew` field**

In `JointMaterial`, immediately after `k_emb_scale` (~line 144), add:

```python
    # Renovacao de embedding no re-aperto (spec 2026-07-07): no retighten,
    # delta_emb <- delta_emb*(1 - k_emb_renew*D). Superficies danificadas expoem
    # capacidade de assentamento fresca ~ D. 0.0 = inerte (re-aperto mantem
    # delta_emb; backward-compat exato). So atua em retighten(), nunca em step_cycle.
    k_emb_renew: float = 0.0
```

- [ ] **Step 4: Add the `retighten` method**

In `DynamicStiffnessAnalyzer`, immediately after `step_cycle` (before `energy_report`,
~line 1061), add:

```python
    def retighten(self, applied_torque: Optional[float] = None,
                  new_F0: Optional[float] = None) -> None:
        """Re-aperto quasi-estatico entre fases de ciclagem (spec 2026-07-07).

        Exatamente UM de:
          applied_torque [N.m]: preve a pre-carga recuperada via Motosh
            (tightening_torque, reusa mu_bearing_eff(D) -> falsify-first).
          new_F0 [N]: pre-carga pos-aperto explicita (override p/ testes/medido).

        Renova delta_emb (damage-coupled, k_emb_renew), zera theta_loose (porca
        girada de volta na direcao de aperto), rebaseia o segmento de energia.
        Persistem: D, delta_creep, delta_wear, W_slip_acc, W_conf, F_0_init e o
        _cycle_counter (relogio do creep -- resetar multiplicaria o creep inicial).
        O trabalho discreto do re-aperto fica fora do budget por-ciclo (spec 3.5).
        """
        if (applied_torque is None) == (new_F0 is None):
            raise ValueError("retighten: forneca exatamente um de "
                             "applied_torque ou new_F0")
        if applied_torque is not None:
            coeff = tightening_torque(1.0, self.state, self.geom, self.mat)
            F0 = applied_torque / max(coeff, 1e-12)
        else:
            F0 = float(new_F0)
        if F0 < 0.0:
            raise ValueError(f"retighten: pre-carga negativa (F0={F0})")
        # Renovacao de embedding: capacidade restaurada ~ D (clamp [0, target]).
        target = self.mat.k_emb_scale * self.mat.emb_depth
        renewed = self.state.delta_emb * (1.0 - self.mat.k_emb_renew * self.state.D)
        self.state.delta_emb = min(max(renewed, 0.0), target)
        # Re-estabelece pre-carga; porca girada de volta => theta_loose -> 0.
        self.state.F_0 = F0
        self.state.theta_loose = 0.0
        # Rebase do segmento de energia (novo baseline no estado pos-aperto).
        U_init = U_internal(self.state, self.geom, self.mat)
        self.energy = EnergyBudget(U_stored=U_init, U_stored_init=U_init)
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `python -m pytest tests/test_retightening.py -q`
Expected: all passed (3 from Task 1 + 8 new = 11).

- [ ] **Step 6: Run the full calibration suite (backward-compat)**

Run:
```bash
python -m pytest tests/test_surface_damage.py tests/test_v2_solver_preload.py \
  tests/test_slip_onset_incubation.py tests/test_embedding_state_based.py \
  tests/test_shared_calibrator.py tests/test_calibration_decomposition.py -q
```
Expected: all passed (no regression — `retighten` is unused by these; `k_emb_renew=0`).

- [ ] **Step 7: Syntax-check + commit**

```bash
python -c "import ast; ast.parse(open('src/bolt_analysis_studio/numerical/dynamic_stiffness_analyzer.py', encoding='utf-8').read()); print('OK')"
git add src/bolt_analysis_studio/numerical/dynamic_stiffness_analyzer.py tests/test_retightening.py
git commit -m "feat(engine): retighten() + k_emb_renew (damage-coupled embedding renewal)"
```

---

### Task 3: Validation harness `validate_retightening.py`

**Files:**
- Create: `New_Theory/validate_retightening.py`
- Reads: `Models/CALIBRATION_AND_VALIDATION/curve_library/digitized_csv/liu2022_fig6a_dry_release_t{0..3}.csv`,
  `liu2022_fig6b_oil_release_t{0..3}.csv`, `liu2022_fig7a_oil_direct_t{0..3}.csv`
- Uses: `library_common.frozen_constants(include_damage=True)`, `geometry_for`, `emb_depth_vdi`, `load_full_curve`

**Interfaces:**
- Consumes: engine `retighten`/`tightening_torque` (Tasks 1–2); `library_common` (existing).
- Produces: `run_sequence(mu, k_emb_renew, consts, geom, emb_m, F0_first, ...) -> (F0_first, list[np.ndarray])`
  (per-phase R_F arrays, normalised to F0_first); a `main()` that prints per-`tN` MAE and the
  G1–G5 verdicts and writes `New_Theory/retightening_results.json` + `.png`.

- [ ] **Step 1: Write the harness**

Create `New_Theory/validate_retightening.py`:

```python
"""Validacao da renovacao de embedding no re-aperto (spec 2026-07-07).

Reproduz o protocolo Liu2022 (Structures, M12, transverso disp 0.3mm 12.5Hz,
T=80 Nm): apertar -> 5000 ciclos -> retighten x4, para DRY e OIL, com UMA fisica
(constantes congeladas do Estagio A) diferindo SO por mu. Gates G1-G5 pre-registrados
(ver spec 5). NAO adota nada; e validacao falsify-first.

Run:  python New_Theory/validate_retightening.py [--quick]
"""
from __future__ import annotations
import json
import sys
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "New_Theory"))
from bolt_analysis_studio.numerical.dynamic_stiffness_analyzer import (  # noqa: E402
    DynamicStiffnessAnalyzer, JointMaterial)   # retighten() uses tightening_torque internally
from library_common import (  # noqa: E402
    frozen_constants, geometry_for, emb_depth_vdi, load_full_curve)

DIG = "Models/CALIBRATION_AND_VALIDATION/curve_library/digitized_csv"
N_PHASE = 5000
N_RETIGHT = 4
FREQ = 12.5
DELTA = 0.3e-3
F_AMP = 5000.0            # forca transversa (variante load-controlled 5 kN), prov=paper
TORQUE = 80.0            # N.m
GRIP_MM = 50.0           # 2 placas + celula de carga 20mm; prov=assumed (banda de sens.)

# Achieved first-tightening F0 (kN), medido no paper (prov=paper):
COND = {
    "dry_release": dict(mu=0.20, F0_first=20.6e3, grp="liu2022_fig6a_dry_release"),
    "oil_release": dict(mu=0.10, F0_first=27.0e3, grp="liu2022_fig6b_oil_release"),
    "oil_direct":  dict(mu=0.10, F0_first=27.0e3, grp="liu2022_fig7a_oil_direct"),
}


def run_sequence(mu, k_emb_renew, consts, geom, emb_m, F0_first, cap=None):
    """Roda apertar->N_PHASE->retighten x N_RETIGHT. Retorna (F0_first, [R_F por tN])."""
    n_phase = cap or N_PHASE
    mat = JointMaterial(mu_thread=mu, mu_bearing=mu, emb_depth=emb_m,
                        k_emb_renew=k_emb_renew, **consts)
    ana = DynamicStiffnessAnalyzer(geom, mat, F0_first)
    phases = []
    for t in range(N_RETIGHT + 1):
        rf = [max(ana.state.F_0, 0.0) / F0_first]
        for _ in range(n_phase):
            ana.step_cycle(F_AMP, np.pi / 2.0, FREQ, delta_amp=DELTA)
            rf.append(max(ana.state.F_0, 0.0) / F0_first)
        phases.append(np.array(rf))
        if t < N_RETIGHT:
            ana.retighten(applied_torque=TORQUE)   # preve recuperacao (plana em k_dmg_mu=0)
    return F0_first, phases


def _decay_mae(sim_rf, csv):
    """MAE da FORMA do afrouxamento: cada fase normalizada no PROPRIO inicio,
    isolando o decaimento da RECUPERACAO pos-aperto (o offset de recuperacao = G4)."""
    cyc_d, r_d = load_full_curve(csv)
    keep = cyc_d <= (len(sim_rf) - 1)
    cyc_d, r_d = cyc_d[keep], r_d[keep]
    if len(cyc_d) < 2:
        return float("nan")
    sim_loc = sim_rf / max(sim_rf[0], 1e-9)
    r_d_loc = r_d / max(r_d[0], 1e-9)
    pred = np.interp(cyc_d, np.arange(len(sim_loc)), sim_loc)
    return float(np.mean(np.abs(pred - r_d_loc)))


def _sim_phase_loss(phases):
    """Perda por fase do MODELO (forma local): 1 - R_F_local(fim)."""
    return [float(1.0 - p[-1] / max(p[0], 1e-9)) for p in phases]


def _data_series(grp, which):
    """which='loss' -> 1-R_F_local(fim) por fase; 'recovery' -> R_F(inicio) por fase."""
    vals = []
    for t in range(N_RETIGHT + 1):
        _, r_d = load_full_curve(f"{DIG}/{grp}_t{t}.csv")
        vals.append(float(1.0 - r_d[-1] / max(r_d[0], 1e-9)) if which == "loss"
                    else float(r_d[0]))
    return vals


def evaluate(consts, geom, emb_m, cap=None):
    out = {}
    # DRY: fit k_emb_renew by 1-D sweep to the dry-release DECAY shape (G5 parsimony).
    dry = COND["dry_release"]
    best = None
    for k in [0.0, 0.25, 0.5, 1.0, 2.0]:
        _, phases = run_sequence(dry["mu"], k, consts, geom, emb_m, dry["F0_first"], cap)
        maes = [_decay_mae(phases[t], f"{DIG}/{dry['grp']}_t{t}.csv")
                for t in range(N_RETIGHT + 1)]
        med = float(np.nanmedian(maes))
        if best is None or med < best["med"]:
            best = dict(k=k, med=med, maes=maes, phases=phases)
    out["dry_release"] = best
    # G5 parsimony: freeing k_emb_renew beats the k=0 baseline (wear-amp alone) by > tol?
    _, ph0 = run_sequence(dry["mu"], 0.0, consts, geom, emb_m, dry["F0_first"], cap)
    med0 = float(np.nanmedian([_decay_mae(ph0[t], f"{DIG}/{dry['grp']}_t{t}.csv")
                               for t in range(N_RETIGHT + 1)]))
    out["G5_med_k0"] = med0
    out["G5_renewal_justified"] = bool(med0 - best["med"] > 0.005)
    # OIL: PREDICT with the dry-fit k_emb_renew (zero-refit transfer), release + direct.
    for name in ("oil_release", "oil_direct"):
        c = COND[name]
        _, phases = run_sequence(c["mu"], best["k"], consts, geom, emb_m,
                                 c["F0_first"], cap)
        maes = [_decay_mae(phases[t], f"{DIG}/{c['grp']}_t{t}.csv")
                for t in range(N_RETIGHT + 1)]
        out[name] = dict(k=best["k"], maes=maes, phases=phases)
    return out


def _monotone_incr(xs):
    return all(xs[i] <= xs[i + 1] + 1e-9 for i in range(len(xs) - 1))


def main():
    quick = "--quick" in sys.argv
    cap = 500 if quick else None
    consts, _ = frozen_constants(include_damage=True)
    emb_m, _ = emb_depth_vdi("Rz<10", 2)     # M12 fino, 2 interfaces internas; prov=handbook
    geom = geometry_for("M12x1.75", GRIP_MM)
    res = evaluate(consts, geom, emb_m, cap)

    dry = res["dry_release"]
    sim_loss = _sim_phase_loss(dry["phases"])
    data_loss = _data_series(COND["dry_release"]["grp"], "loss")
    data_rec = _data_series(COND["dry_release"]["grp"], "recovery")
    print(f"DRY k_emb_renew*={dry['k']} decay-MAE/tN={[round(m,3) for m in dry['maes']]} "
          f"med={dry['med']:.3f} (k=0 med={res['G5_med_k0']:.3f})")
    print(f"  sim  per-phase loss={[round(x,3) for x in sim_loss]}")
    print(f"  data per-phase loss={[round(x,3) for x in data_loss]}")
    print(f"  data recovery t0..t4={[round(x,3) for x in data_rec]}  (sim recovery = flat ~1.0)")
    for name in ("oil_release", "oil_direct"):
        r = res[name]
        print(f"{name:12s} decay-MAE/tN={[round(m,3) for m in r['maes']]}")

    # ---- Gates (pre-registered, spec 5) ----
    oil = res["oil_release"]
    g1 = float(np.nanmedian(oil["maes"])) < 0.05
    g2 = (_monotone_incr(data_loss) and _monotone_incr(sim_loss)
          and all(sl <= 2 * dl + 1e-9 and dl <= 2 * sl + 1e-9
                  for sl, dl in zip(sim_loss, data_loss) if dl > 1e-6))
    g3 = (float(np.nanmedian(dry["maes"])) < 0.05) or _monotone_incr(sim_loss)
    g5 = res["G5_renewal_justified"]
    print(f"\nGATES: G1(oil decay MAE<0.05)={g1}  G2(dry accel model~data)={g2}  "
          f"G3(dry loosening shape)={g3}  G5(renewal justified +>0.005)={g5}")
    print("G4(recovery): frozen k_dmg_mu=0 => sim recovery FLAT ~1.0 each retighten; "
          f"data dry recovery {[round(x,3) for x in data_rec]} DECLINES => documented "
          "finding (missing galling/geometric term, spec 7), NOT a gate.")
    if quick:
        print("--quick: smoke only, nao grava artefatos.")
        return
    payload = dict(
        dry=dict(k=dry["k"], decay_mae=dry["maes"], med=dry["med"],
                 sim_loss=sim_loss, data_loss=data_loss, data_recovery=data_rec),
        oil_release=dict(decay_mae=res["oil_release"]["maes"]),
        oil_direct=dict(decay_mae=res["oil_direct"]["maes"]),
        gates=dict(G1=bool(g1), G2=bool(g2), G3=bool(g3), G5=bool(g5),
                   G5_med_k0=res["G5_med_k0"]))
    (ROOT / "New_Theory" / "retightening_results.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print("Artefato: New_Theory/retightening_results.json")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Syntax-check**

Run: `python -c "import ast; ast.parse(open('New_Theory/validate_retightening.py', encoding='utf-8').read()); print('OK')"`
Expected: `OK`.

- [ ] **Step 3: Smoke-run**

Run: `python New_Theory/validate_retightening.py --quick`
Expected: prints DRY/OIL MAE lines and a `GATES:` line without error (cap=500, ~1 min).
If a `liu2022_*` CSV path is missing, fix the `grp`/filename against
`digitized_csv/` before proceeding.

- [ ] **Step 4: Commit**

```bash
git add New_Theory/validate_retightening.py
git commit -m "feat(validate): harness da renovacao de embedding no re-aperto (Liu2022 dry/oil)"
```

---

### Task 4: Run validation, record AS-IS verdict, merge-ready

**Files:**
- Run: `New_Theory/validate_retightening.py` (full)
- Create: `New_Theory/retightening_results.json` (harness output)
- Modify: `New_Theory/MODEL_LEGITIMACY.md` (add §4.10)

**Interfaces:** consumes Task 3 output. Produces the AS-IS verdict.

- [ ] **Step 1: Full run**

Run: `python New_Theory/validate_retightening.py > New_Theory/retightening_validation.log 2>&1`
(Windows: prefix `PYTHONIOENCODING=utf-8` so the log is clean UTF-8.)
Expected: exit 0; `retightening_results.json` written; ~10–20 min (2×5 phases × up to
5000 cyc × sweep). Inspect the `GATES:` line and per-phase losses.

- [ ] **Step 2: Write the AS-IS verdict**

Append a new section `### 4.10 Renovacao de embedding no re-aperto (Liu2022, spec 2026-07-07)`
to `New_Theory/MODEL_LEGITIMACY.md` **using the actual numbers** from Step 1. It MUST state,
per the pre-registered gates:
- G1 (oil restore): pass/fail + oil MAE.
- G2/G3 (dry acceleration, dry-vs-oil from μ alone): pass/fail + per-phase losses.
- G4 (recovery): frozen `k_dmg_mu=0` ⇒ predicted flat ~100% restore vs the data's dry
  decline ⇒ documented finding (missing galling/geometric recovery term, spec §7).
- G5 (parsimony): whether freeing `k_emb_renew` beat `k=0` by > 0.005 — i.e. whether
  embedding renewal is *justified by this dataset* or wear-amplification alone suffices.
- Verdict line: is `retighten`/`k_emb_renew` a **validated capability** (like fretting) or
  **adopted**? State AS IS — do not overclaim.

- [ ] **Step 3: Commit**

```bash
git add New_Theory/MODEL_LEGITIMACY.md New_Theory/retightening_results.json New_Theory/retightening_validation.log
git commit -m "docs(4.10): validacao AS-IS da renovacao de embedding no re-aperto (Liu2022)"
```

- [ ] **Step 4: Request Opus code review**

Use `superpowers:requesting-code-review` on the branch diff before any merge — same
discipline as the fretting/loosening mechanisms (energy routing, backward-compat, gates).

---

## Self-Review (spec coverage)

- Spec §3.1 (retighten state transform) → Task 2. §3.2 (torque→preload) → Task 1. §3.3
  (renewal rule) → Task 2. §3.4 (API) → Tasks 1–2. §3.5 (energy rebase) → Task 2
  (test_retighten_rebases_energy_budget).
- Spec §4 (validation protocol, dry/oil, secondary âncora interna reaperto) → Task 3 (dry/oil);
  **secondary âncora interna-reaperto fidelity check is deferred** to a follow-up (noted here — it needs
  the âncora interna reaperto tightening history; not blocking the Liu2022 falsification).
- Spec §5 gates G1–G5 → Task 3 (`evaluate`/`main`) + Task 4 (verdict).
- Spec §6 discipline (opt-in, TDD, conservation, Opus review) → Tasks 2, 4.
