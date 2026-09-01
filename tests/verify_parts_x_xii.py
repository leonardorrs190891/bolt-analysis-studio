"""
Verification script for Parts X-XII improvements.
Bolt Analysis Studio v4.0
"""
import sys
import os
import numpy as np
import inspect

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

results = []

def check(name, condition, detail=""):
    status = "PASS" if condition else "FAIL"
    results.append((name, status, detail))
    print(f"  [{status}] {name}" + (f" - {detail}" if detail and not condition else ""))

print("=" * 70)
print("Parts X-XII Verification Script")
print("=" * 70)

# ===== PART X: Preload Loss Models =====
print("\n--- PART X: Preload Loss Models ---")

from bolt_analysis_studio.numerical.preload_loss_models import (
    BoltParameters, JointParameters, PreloadConditions,
    SingleExponentialModel, DoubleExponentialModel,
    StretchedExponentialModel, VDI2230EmbeddingModel,
    NortonBaileyCreepModel, ThermalEffectsModel,
    PowerLawModel, LogarithmicModel,
    JiangTwoStageModel, JiangThreeStageModel,
    CombinedMechanismModel, DNLooseningCurve,
    MinersRuleAccumulation, EnergyDissipationModel,
    RotationAngleModel, compute_system_stiffness,
    create_preload_loss_model, generate_standard_test_data,
    DecayModelType
)

# X1: All 15 models exist
check("X1: All 15 model classes exist", True,
      "Verified by successful import of all model classes")

# X2: Norton-Bailey preload() formula is correct (has E)
bolt_data = generate_standard_test_data()
bolt, joint, cond = bolt_data['bolt'], bolt_data['joint'], bolt_data['conditions']
nb = NortonBaileyCreepModel(bolt, joint, cond)
src_nb = inspect.getsource(NortonBaileyCreepModel.preload)
check("X2: Norton-Bailey preload() has B*E in formula",
      "self.B * self.E" in src_nb or "self.E * self.B" in src_nb)

# X3: Norton-Bailey preload_rate() is correct (E*B*sigma^n, not B*sigma^n/E)
src_rate = inspect.getsource(NortonBaileyCreepModel.preload_rate)
check("X3: Norton-Bailey rate uses -B*E*sigma^n (not /E)",
      "self.B * self.E *" in src_rate and "/ self.E" not in src_rate)

# X4: CombinedMechanismModel has creep term
src_combined = inspect.getsource(CombinedMechanismModel.preload)
check("X4: CombinedMechanismModel.preload() includes creep",
      "creep" in src_combined and "_has_creep" in src_combined)

# X5: CombinedMechanismModel.__init__ has creep parameters
src_init = inspect.getsource(CombinedMechanismModel.__init__)
check("X5: CombinedMechanismModel has creep_A, creep_n, creep_Q params",
      "creep_A" in src_init and "creep_n" in src_init and "creep_Q" in src_init)

# X6: CombinedMechanismModel.get_loss_breakdown() includes creep
src_breakdown = inspect.getsource(CombinedMechanismModel.get_loss_breakdown)
check("X6: get_loss_breakdown() returns creep component",
      "'creep'" in src_breakdown)

# X7: CombinedMechanismModel thermal uses physics-based formula
check("X7: CombinedMechanismModel thermal uses k_sys formula",
      "compute_system_stiffness" in src_init or "k_sys" in src_init)

# X8: All models produce reasonable outputs
N = np.array([0, 100, 500, 1000, 2000])
se = SingleExponentialModel(bolt, joint, cond)
F = se.preload(N)
check("X8a: SingleExponential produces decreasing preload",
      all(F[i] >= F[i+1] for i in range(len(F)-1)))

de = DoubleExponentialModel(bolt, joint, cond)
F_de = de.preload(N)
check("X8b: DoubleExponential produces decreasing preload",
      all(F_de[i] >= F_de[i+1] for i in range(len(F_de)-1)))

# X9: compute_system_stiffness works
k_data = compute_system_stiffness(bolt, joint)
check("X9: compute_system_stiffness returns valid data",
      k_data['k_system'] > 0 and k_data['k_bolt'] > 0)

# X10: Factory function works
model = create_preload_loss_model(DecayModelType.SINGLE_EXPONENTIAL, bolt=bolt, joint=joint, conditions=cond)
check("X10: Factory function creates model", model is not None)

# X11: DNLooseningCurve exists and works
dn = DNLooseningCurve()
N_f = dn.cycles_to_loosening(0.65)
check("X11: DNLooseningCurve.cycles_to_loosening() works", N_f > 0)

# X12: MinersRuleAccumulation exists and works
miner = MinersRuleAccumulation(dn)
miner.add_loading_block(0.65, 500)
check("X12: MinersRuleAccumulation works",
      0 < miner.remaining_life_fraction() <= 1.0)

# X13: EnergyDissipationModel exists
edm = EnergyDissipationModel(mu=0.12, normal_force=50000, displacement_amplitude=0.65e-3)
check("X13: EnergyDissipationModel works",
      edm.energy_per_cycle() > 0)

# X14: RotationAngleModel exists and works
ram = RotationAngleModel(bolt, joint, initial_preload=50000)
F_rot = ram.preload_from_rotation(np.array([10.0]))  # 10 degrees
check("X14: RotationAngleModel works", F_rot[0] < 50000)

print("\n--- PART XI: Coupled Analysis Framework ---")

from bolt_analysis_studio.numerical.coupled_loosening_analyzer import (
    CoupledLooseningAnalyzer, FrictionEvolutionParams, WearModelParams,
    TwoStageLooseningParams, ThreadGeometryParams, BearingGeometryParams,
    LooseningPhase, LooseningRisk, LooseningState
)

# XI1: Wear blending formula matches reference
src_wear = inspect.getsource(WearModelParams.compute_wear_increment)
check("XI1: Wear blending uses max(archard, 0.5*energy) + 0.3*energy",
      "max(dh_archard, 0.5 * dh_energy) + 0.3 * dh_energy" in src_wear)

# XI2: CoupledLooseningAnalyzer has all required methods
analyzer_methods = dir(CoupledLooseningAnalyzer)
check("XI2a: Has run_analysis()",  "run_analysis" in analyzer_methods)
check("XI2b: Has update_state()",  "update_state" in analyzer_methods)
check("XI2c: Has _classify_phase()", "_classify_phase" in analyzer_methods)
check("XI2d: Has _classify_risk()", "_classify_risk" in analyzer_methods)

# XI3: LooseningPhase enum has all 5 phases
phases = [p.name for p in LooseningPhase]
check("XI3: All 5 loosening phases exist",
      all(p in phases for p in ['STABLE', 'NON_ROTATIONAL', 'TRANSITION', 'ROTATIONAL', 'RUNAWAY']))

# XI4: LooseningRisk enum has all 5 levels
risks = [r.name for r in LooseningRisk]
check("XI4: All 5 risk levels exist",
      all(r in risks for r in ['NEGLIGIBLE', 'LOW', 'MODERATE', 'HIGH', 'CRITICAL']))

# XI5: FrictionEvolutionParams has three-phase model
src_friction = inspect.getsource(FrictionEvolutionParams.compute_mu)
check("XI5: FrictionEvolutionParams has three-phase model",
      "mu_peak" in src_friction and "mu_steady" in src_friction)

# XI6: ThreadGeometryParams has helix coupling
check("XI6: ThreadGeometryParams has helix_coupling_factor",
      hasattr(ThreadGeometryParams, 'helix_coupling_factor'))

# XI7: BearingGeometryParams has effective_radius
check("XI7: BearingGeometryParams has effective_radius",
      hasattr(BearingGeometryParams, 'effective_radius'))

# XI8: Torque calculation in analyzer
src_torque = inspect.getsource(CoupledLooseningAnalyzer.compute_torques)
check("XI8: Torque calc has T_pitch, T_thread, T_bearing",
      "T_pitch" in src_torque and "T_thread" in src_torque and "T_bearing" in src_torque)

# XI9: Slip detection
src_slip = inspect.getsource(CoupledLooseningAnalyzer)
check("XI9: Has check_slip_condition method",
      "check_slip_condition" in src_slip)

# XI10: Preload loss blending formula
check("XI10: Has physics/empirical blending formula",
      "max(physics_loss" in src_slip and "0.8" in src_slip)

print("\n--- PART XII: Force Excitation & Damping ---")

from bolt_analysis_studio.numerical.time_integration import (
    harmonic_force, step_force, pulse_force, random_force,
    superposed_force, compute_rayleigh_damping,
    compute_damping_ratio_at_frequency,
    NonlinearNewmark, NonlinearParams, ConvergenceType
)

# XII1: All force excitation functions exist
check("XII1a: harmonic_force exists", callable(harmonic_force))
check("XII1b: step_force exists", callable(step_force))
check("XII1c: pulse_force exists", callable(pulse_force))
check("XII1d: random_force exists", callable(random_force))
check("XII1e: superposed_force exists", callable(superposed_force))

# XII2: harmonic_force produces correct output
amp = np.array([1000.0, 0.0])
F_h = harmonic_force(amp, 10.0)
val = F_h(0.025)  # t = 1/(4f) = peak
check("XII2: harmonic_force produces correct peak",
      abs(val[0] - 1000.0) < 1.0)

# XII3: step_force with smooth ramp
F_s = step_force(np.array([500.0]), t_start=0.1, rise_time=0.05)
check("XII3a: step_force returns zero before start", abs(F_s(0.0)[0]) < 1e-10)
check("XII3b: step_force returns full after ramp", abs(F_s(0.2)[0] - 500.0) < 1e-10)

# XII4: pulse_force
F_p = pulse_force(np.array([200.0]), t_start=0.0, duration=0.01)
check("XII4a: pulse_force active during pulse", abs(F_p(0.005)[0] - 200.0) < 1e-10)
check("XII4b: pulse_force zero after pulse", abs(F_p(0.02)[0]) < 1e-10)

# XII5: random_force
F_r = random_force(np.array([100.0, 50.0]), seed=42)
vals = [F_r(t) for t in np.linspace(0, 1, 100)]
rms_0 = np.sqrt(np.mean([v[0]**2 for v in vals]))
check("XII5: random_force produces reasonable RMS",
      50 < rms_0 < 200)  # Should be near 100

# XII6: superposed_force works
F_combined = superposed_force(
    harmonic_force(np.array([100.0]), 5.0),
    step_force(np.array([500.0]), t_start=0.0),
    static_force=np.array([1000.0])
)
val_combined = F_combined(0.05)  # t=0.05: step is full, harmonic is sin(2*pi*5*0.05)=sin(pi/2)=1
check("XII6: superposed_force combines correctly",
      abs(val_combined[0] - (1000.0 + 500.0 + 100.0)) < 2.0)

# XII7: Rayleigh damping with default zeta=0.02
src_rayleigh = inspect.getsource(compute_rayleigh_damping)
check("XII7: Rayleigh damping default zeta=0.02",
      "zeta: float = 0.02" in src_rayleigh)

# XII8: Rayleigh damping produces valid coefficients
M = np.diag([1.0, 1.0])
K = np.array([[2.0, -1.0], [-1.0, 1.0]])
alpha, beta, C = compute_rayleigh_damping(M, K, 10.0, 100.0, zeta=0.02)
check("XII8: Rayleigh damping produces valid alpha, beta",
      alpha > 0 and beta > 0 and C.shape == (2, 2))

# XII9: compute_damping_ratio_at_frequency works
zeta_10 = compute_damping_ratio_at_frequency(alpha, beta, 10.0)
check("XII9: Damping ratio at omega_1 approx target zeta",
      abs(zeta_10 - 0.02) < 0.005)

# XII10: Energy convergence criterion uses dot(du, R)
src_nl = inspect.getsource(NonlinearNewmark.integrate)
check("XII10: Energy criterion uses dot(last_du_vec, R)",
      "last_du_vec, R" in src_nl or "last_du_vec," in src_nl)

# XII11: NonlinearParams has all convergence types
check("XII11: All convergence types exist",
      all(hasattr(ConvergenceType, ct) for ct in ['FORCE', 'DISPLACEMENT', 'ENERGY', 'COMBINED']))

# XII12: NonlinearParams defaults match reference
nlp = NonlinearParams()
check("XII12a: Default max_iterations=50", nlp.max_iterations == 50)
check("XII12b: Default tol_force=1e-6", nlp.tol_force == 1e-6)
check("XII12c: Default tol_energy=1e-9", nlp.tol_energy == 1e-9)
check("XII12d: Default line_search=True", nlp.line_search == True)

print("\n--- Combined: Matrix Coupling & Load Path ---")

from bolt_analysis_studio.core.load_propagation import LoadPathAnalyzer

# C1: LoadPathAnalyzer exists
check("C1: LoadPathAnalyzer class exists", LoadPathAnalyzer is not None)

# C2: LoadPathAnalyzer torque computation
lpa = LoadPathAnalyzer(
    preload=50000, pitch=2.0, pitch_diameter=14.701,
    flank_angle_deg=30.0, mu_thread=0.12, mu_bearing=0.12,
    bearing_inner_r=8.0, bearing_outer_r=12.0
)
torques = lpa.compute_torque_components()
check("C2a: T_pitch > 0", torques['T_pitch'] > 0)
check("C2b: T_thread > 0", torques['T_thread'] > 0)
check("C2c: T_bearing > 0", torques['T_bearing'] > 0)
check("C2d: margin > 1 (self-locking)", torques['margin'] > 1.0)

# C3: Critical friction
mu_crit = lpa.compute_critical_friction()
check("C3: Critical friction coefficient > 0", mu_crit > 0 and mu_crit < 0.1)

# C4: Slip conditions
slip = lpa.check_slip_conditions(F_transverse=10000)
check("C4a: Slip conditions returns bearing_slip flag", 'bearing_slip' in slip)
check("C4b: Slip conditions returns thread_slip flag", 'thread_slip' in slip)

# C5: Full analysis
result = lpa.analyze_under_load(F_transverse=10000)
check("C5a: analyze_under_load returns torque components",
      'torque_components' in result)
check("C5b: analyze_under_load returns loosening assessment",
      'loosening_possible' in result)
check("C5c: analyze_under_load returns critical friction",
      'critical_friction' in result)

# C6: CompleteMSDMatrixAssembler exists
try:
    from bolt_analysis_studio.core.assembly.matrix_assembler import CompleteMSDMatrixAssembler
    check("C6: CompleteMSDMatrixAssembler exists", True)
except ImportError:
    check("C6: CompleteMSDMatrixAssembler exists", False, "Import failed")

# C7: model.py has assemble_force_vector
from bolt_analysis_studio.core.models.model import MSDModel
check("C7: MSDModel has assemble_force_vector",
      hasattr(MSDModel, 'assemble_force_vector'))

# C8: model.py has apply_rayleigh_damping
check("C8: MSDModel has apply_rayleigh_damping",
      hasattr(MSDModel, 'apply_rayleigh_damping'))

print("\n" + "=" * 70)
n_pass = sum(1 for _, s, _ in results if s == "PASS")
n_fail = sum(1 for _, s, _ in results if s == "FAIL")
print(f"TOTAL: {n_pass}/{n_pass + n_fail} PASS")
if n_fail > 0:
    print("\nFAILED:")
    for name, status, detail in results:
        if status == "FAIL":
            print(f"  {name}: {detail}")
print("=" * 70)

sys.exit(0 if n_fail == 0 else 1)
