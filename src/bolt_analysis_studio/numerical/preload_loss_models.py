"""
Comprehensive Mathematical Models for Preload Loss and Self-Loosening
=====================================================================

This module contains all preload loss models from literature including:
- Jiang two-stage/three-stage models
- Exponential decay models (single, double, stretched)
- Power-law models
- D-N curves for life prediction
- Friction evolution models
- Wear models

References:
- Jiang et al. (2003-2004) ASME J. Mechanical Design
- Nassar & Housari (2005-2011) Oakland University
- Liu et al. (2017) Tribology International
- Lu et al. (2024) Sensors
- VDI 2230 (2015)

BAS +  R&D
"""

import numpy as np
from dataclasses import dataclass, field
from typing import Callable, Optional, Tuple, Dict, List
from enum import Enum
from abc import ABC, abstractmethod


# =============================================================================
# ENUMERATIONS
# =============================================================================

class LooseningStage(Enum):
    """Jiang model loosening stages"""
    STAGE_I = "material_loosening"      # Plastic deformation, no rotation
    STAGE_II = "structural_loosening"   # Rotational back-off
    STAGE_III = "fatigue_degradation"   # Crack propagation


class LoadingType(Enum):
    """Type of cyclic loading"""
    AXIAL = "axial"
    TRANSVERSE = "transverse"
    COMBINED = "combined"
    TORSIONAL = "torsional"


class DecayModelType(Enum):
    """Types of preload decay models"""
    SINGLE_EXPONENTIAL = "single_exp"
    DOUBLE_EXPONENTIAL = "double_exp"
    STRETCHED_EXPONENTIAL = "stretched_exp"
    POWER_LAW = "power_law"
    LOGARITHMIC = "logarithmic"
    POLYNOMIAL = "polynomial"
    JIANG_TWO_STAGE = "jiang_2stage"
    JIANG_THREE_STAGE = "jiang_3stage"


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class BoltParameters:
    """Bolt geometry and material parameters"""
    # Geometry
    diameter: float = 12.0        # mm, nominal diameter
    pitch: float = 1.75           # mm, thread pitch
    length: float = 60.0          # mm, grip length
    thread_length: float = 25.0   # mm, engaged thread length
    
    # Calculated geometry
    pitch_diameter: float = field(init=False)  # d2
    minor_diameter: float = field(init=False)  # d3
    stress_area: float = field(init=False)     # As
    thread_angle: float = 30.0    # deg, half flank angle (60° total)
    helix_angle: float = field(init=False)
    
    # Material
    elastic_modulus: float = 210e3   # MPa
    yield_strength: float = 720.0     # MPa (L7 grade)
    poisson_ratio: float = 0.3
    hardness: float = 3000.0          # MPa (Vickers)
    
    # Thermal
    thermal_expansion: float = 12e-6  # 1/K
    
    def __post_init__(self):
        # ISO metric thread calculations
        H = 0.866025 * self.pitch  # Thread height
        self.pitch_diameter = self.diameter - 0.6495 * self.pitch
        self.minor_diameter = self.diameter - 1.0825 * self.pitch  # d1 for At
        self.d3 = self.diameter - 1.2268 * self.pitch              # bolt root diameter
        d2 = self.pitch_diameter
        d1 = self.minor_diameter
        # Stress area per ISO 898-1 uses d2 and d1 (C3/C6 fix)
        self.stress_area = np.pi / 4 * ((d2 + d1) / 2) ** 2
        self.helix_angle = np.degrees(np.arctan(self.pitch / (np.pi * self.pitch_diameter)))


@dataclass
class JointParameters:
    """Joint stiffness and friction parameters"""
    # Stiffness
    bolt_stiffness: float = 5e5      # N/mm
    member_stiffness: float = 1.5e6  # N/mm
    
    # Friction coefficients
    mu_thread: float = 0.12          # Thread friction
    mu_bearing: float = 0.14         # Bearing surface friction
    mu_total: float = field(init=False)
    
    # Surface parameters
    surface_roughness: float = 3.2   # Ra in μm
    bearing_diameter: float = 18.0   # mm
    
    # K-factor (nut factor)
    k_factor: float = field(init=False)
    
    def __post_init__(self):
        self.mu_total = (self.mu_thread + self.mu_bearing) / 2
        # Simplified K-factor (updated with compute_vdi_k_factor for full calc)
        self.k_factor = 0.16 + 0.5 * self.mu_total

    def compute_vdi_k_factor(self, bolt: 'BoltParameters') -> float:
        """
        Full VDI 2230 K-factor (nut factor / torque coefficient):

        K = (d₂/2d)·[p/(πd₂) + μₜ/cos(α)] + μ_b·D_km/(2d)

        where:
            d   = nominal bolt diameter
            d₂  = pitch diameter
            p   = pitch
            α   = half flank angle (30° for metric)
            μₜ  = thread friction coefficient
            μ_b = bearing friction coefficient
            D_km = mean bearing diameter ≈ (D_bearing + d_hole) / 2
        """
        d = bolt.diameter
        d2 = bolt.pitch_diameter
        p = bolt.pitch
        alpha_rad = np.radians(bolt.thread_angle)
        D_km = self.bearing_diameter  # Mean bearing diameter

        # Thread torque component
        thread_term = (d2 / (2 * d)) * (p / (np.pi * d2) + self.mu_thread / np.cos(alpha_rad))

        # Bearing torque component
        bearing_term = self.mu_bearing * D_km / (2 * d)

        self.k_factor = thread_term + bearing_term
        return self.k_factor


@dataclass
class PreloadConditions:
    """Initial preload and loading conditions"""
    initial_preload: float = 50000.0   # N
    yield_utilization: float = 0.7     # Fraction of yield
    
    # Cyclic loading
    loading_type: LoadingType = LoadingType.AXIAL
    displacement_amplitude: float = 0.5  # mm
    load_amplitude: float = 5000.0       # N
    frequency: float = 25.0              # Hz
    
    # Thermal
    temperature: float = 20.0            # °C
    delta_temperature: float = 0.0       # °C change


# =============================================================================
# BASE MODEL CLASS
# =============================================================================

def compute_system_stiffness(bolt: 'BoltParameters',
                             joint: 'JointParameters') -> Dict[str, float]:
    """
    Compute proper bolt and member stiffnesses per VDI 2230 (C6 fix).

    Instead of using trace(K) or user-provided values, computes:
    - k_bolt as series combination of head, shank, free thread, engaged thread
    - k_member from Wileman frustum model or direct user value
    - k_sys = k_bolt * k_member / (k_bolt + k_member)

    Returns:
        Dict with k_bolt, k_member, k_system, load_factor
    """
    E = bolt.elastic_modulus  # MPa
    d = bolt.diameter
    d2 = bolt.pitch_diameter
    d1 = bolt.minor_diameter
    p = bolt.pitch
    A_s = bolt.stress_area  # mm^2
    A_nom = np.pi / 4 * d**2  # mm^2

    L_grip = bolt.length
    L_engaged = bolt.thread_length
    L_shank = max(L_grip - L_engaged, 0.1)

    # Bolt stiffness (VDI 2230 series model)
    k_head = 0.5 * E * d                                # Head compliance
    k_shank = E * A_nom / L_shank if L_shank > 0 else 1e12
    L_free_thread = max(L_engaged * 0.5, p)
    k_free = E * A_s / L_free_thread
    k_engaged = E * A_s / (0.5 * L_engaged) if L_engaged > 0 else 1e12

    inv_k_bolt = 1.0/k_head + 1.0/k_shank + 1.0/k_free + 1.0/k_engaged
    k_bolt = 1.0 / inv_k_bolt if inv_k_bolt > 0 else joint.bolt_stiffness

    # Member stiffness (use provided value or Wileman if available)
    k_member = joint.member_stiffness

    # System stiffness
    k_sys = k_bolt * k_member / (k_bolt + k_member) if (k_bolt + k_member) > 0 else 0.0

    # Load introduction factor
    n = k_bolt / (k_bolt + k_member) if (k_bolt + k_member) > 0 else 0.5

    return {
        'k_bolt': k_bolt,
        'k_member': k_member,
        'k_system': k_sys,
        'load_factor': n,
    }


class PreloadLossModel(ABC):
    """Abstract base class for preload loss models"""
    
    def __init__(self, 
                 bolt: BoltParameters,
                 joint: JointParameters,
                 conditions: PreloadConditions):
        self.bolt = bolt
        self.joint = joint
        self.conditions = conditions
        self.F0 = conditions.initial_preload
        
    @abstractmethod
    def preload(self, N: np.ndarray) -> np.ndarray:
        """Calculate preload at cycle count N"""
        pass
    
    @abstractmethod
    def preload_rate(self, N: np.ndarray) -> np.ndarray:
        """Calculate dF/dN at cycle count N"""
        pass
    
    def normalized_preload(self, N: np.ndarray) -> np.ndarray:
        """Calculate F/F0 ratio"""
        return self.preload(N) / self.F0
    
    def preload_loss(self, N: np.ndarray) -> np.ndarray:
        """Calculate preload loss ΔF = F0 - F(N)"""
        return self.F0 - self.preload(N)
    
    def preload_loss_percent(self, N: np.ndarray) -> np.ndarray:
        """Calculate percent preload loss"""
        return 100 * (1 - self.normalized_preload(N))


# =============================================================================
# BOUNDARY CONDITION SCALING
# =============================================================================

def _boundary_condition_factor(conditions: PreloadConditions,
                               joint: JointParameters) -> float:
    """
    Compute a scaling factor so that preload decay is proportional to
    boundary conditions (transverse displacement, friction, load ratio).

    Reference conditions (Junker test, DIN 65151):
        displacement = 0.65 mm, mu = 0.12, F_trans/F0 = 0.2

    Returns a factor >= 0.  Factor = 1.0 at reference conditions.
    Below displacement threshold (0.15 mm), factor is very small (embedding only).
    """
    disp = conditions.displacement_amplitude  # mm
    mu = joint.mu_total if joint.mu_total > 0 else 0.12
    F0 = conditions.initial_preload if conditions.initial_preload > 0 else 1.0

    # Displacement effect: quadratic (Junker mechanism)
    disp_ref = 0.65  # mm (DIN 65151 reference)
    disp_threshold = 0.15  # mm (below this, minimal loosening)
    if disp < disp_threshold:
        disp_factor = 0.02  # Embedding only
    else:
        disp_factor = (disp / disp_ref) ** 2.0
    disp_factor = min(disp_factor, 5.0)  # Cap at 5×

    # Friction effect: lower friction → faster loosening
    mu_ref = 0.12
    mu_factor = mu_ref / max(mu, 0.03)
    mu_factor = min(mu_factor, 4.0)  # Cap at 4×

    # Load ratio effect: higher F_trans/F0 → faster loosening
    F_trans = conditions.load_amplitude
    load_ratio = F_trans / F0 if F0 > 0 else 0.0
    load_ref = 0.2  # Reference F_trans/F0
    if load_ratio > 0:
        load_factor = load_ratio / load_ref
        load_factor = min(max(load_factor, 0.1), 3.0)
    else:
        load_factor = 1.0  # No transverse load info, use default

    return disp_factor * mu_factor * load_factor


# =============================================================================
# EXPONENTIAL DECAY MODELS
# =============================================================================

class SingleExponentialModel(PreloadLossModel):
    """
    Single exponential decay model: F(N) = F∞ + (F0 - F∞)·exp(-λN)

    Parameters:
        lambda_decay: Decay rate constant (cycles⁻¹), typical 0.0001-0.005
        F_inf: Residual/plateau preload (N)

    The decay rate is automatically scaled by boundary conditions:
        λ_eff = λ_base × (disp/0.65)² × (0.12/μ)
    so that loosening is proportional to transverse displacement
    and inversely proportional to friction.
    """

    def __init__(self,
                 bolt: BoltParameters,
                 joint: JointParameters,
                 conditions: PreloadConditions,
                 lambda_decay: float = 0.0005,
                 F_inf_ratio: float = 0.6):
        super().__init__(bolt, joint, conditions)
        # Scale decay rate by boundary conditions
        bc_factor = _boundary_condition_factor(conditions, joint)
        self.lambda_decay = lambda_decay * bc_factor
        self.F_inf = F_inf_ratio * self.F0
        
    def preload(self, N: np.ndarray) -> np.ndarray:
        N = np.atleast_1d(N)
        return self.F_inf + (self.F0 - self.F_inf) * np.exp(-self.lambda_decay * N)
    
    def preload_rate(self, N: np.ndarray) -> np.ndarray:
        N = np.atleast_1d(N)
        return -self.lambda_decay * (self.F0 - self.F_inf) * np.exp(-self.lambda_decay * N)
    
    @property
    def half_life(self) -> float:
        """Cycles to 50% of remaining preload loss"""
        return np.log(2) / self.lambda_decay


class DoubleExponentialModel(PreloadLossModel):
    """
    Double exponential decay model (Li et al., Tsinghua):
    F(N) = F∞ + A1·exp(-λ1·N) + A2·exp(-λ2·N)
    
    Captures two-mechanism decay:
    - Fast component (λ1): Embedding, plastic deformation
    - Slow component (λ2): Gradual thread slip, wear
    
    Typical ranges:
        λ1: 0.01-0.1 cycles⁻¹ (fast)
        λ2: 0.001-0.01 cycles⁻¹ (slow)
        λ1/λ2 ratio: 5-20
        A1/A2 ratio: 0.3-0.7
    """
    
    def __init__(self,
                 bolt: BoltParameters,
                 joint: JointParameters,
                 conditions: PreloadConditions,
                 lambda1: float = 0.005,
                 lambda2: float = 0.0005,
                 A1_ratio: float = 0.10,
                 A2_ratio: float = 0.15,
                 F_inf_ratio: float = 0.6):
        super().__init__(bolt, joint, conditions)
        # Scale decay rates by boundary conditions
        bc_factor = _boundary_condition_factor(conditions, joint)
        self.lambda1 = lambda1 * bc_factor  # Fast decay
        self.lambda2 = lambda2 * bc_factor  # Slow decay
        self.A1 = A1_ratio * self.F0
        self.A2 = A2_ratio * self.F0
        self.F_inf = F_inf_ratio * self.F0
        
    def preload(self, N: np.ndarray) -> np.ndarray:
        N = np.atleast_1d(N)
        return (self.F_inf + 
                self.A1 * np.exp(-self.lambda1 * N) + 
                self.A2 * np.exp(-self.lambda2 * N))
    
    def preload_rate(self, N: np.ndarray) -> np.ndarray:
        N = np.atleast_1d(N)
        return (-self.lambda1 * self.A1 * np.exp(-self.lambda1 * N) - 
                self.lambda2 * self.A2 * np.exp(-self.lambda2 * N))
    
    def fast_component(self, N: np.ndarray) -> np.ndarray:
        """Get fast decay component only"""
        N = np.atleast_1d(N)
        return self.A1 * np.exp(-self.lambda1 * N)
    
    def slow_component(self, N: np.ndarray) -> np.ndarray:
        """Get slow decay component only"""
        N = np.atleast_1d(N)
        return self.A2 * np.exp(-self.lambda2 * N)


class StretchedExponentialModel(PreloadLossModel):
    """
    Stretched exponential (Kohlrausch-Williams-Watts) model:
    F(N) = max(F_residual, F0·exp(-(N/N0)^β))

    For systems with distributed relaxation times.

    Parameters:
        N0: Characteristic relaxation cycles
        beta: Stretching exponent (0 < β ≤ 1)
            β = 1: Simple exponential (Debye relaxation)
            β < 1: Stretched exponential (heterogeneous)
            Typical mechanical: β = 0.3-0.8
        F_residual_ratio: Minimum residual preload as fraction of F0 (default 0.05 = 5%)
    """

    def __init__(self,
                 bolt: BoltParameters,
                 joint: JointParameters,
                 conditions: PreloadConditions,
                 N0: float = 500.0,
                 beta: float = 0.5,
                 F_residual_ratio: float = 0.05):
        super().__init__(bolt, joint, conditions)
        self.N0 = N0
        self.beta = beta
        self.F_residual = F_residual_ratio * self.F0  # H5: floor at 5% of F0

    def preload(self, N: np.ndarray) -> np.ndarray:
        N = np.atleast_1d(N)
        F = self.F0 * np.exp(-np.power(N / self.N0, self.beta))
        return np.maximum(F, self.F_residual)  # H5: enforce floor

    def preload_rate(self, N: np.ndarray) -> np.ndarray:
        N = np.atleast_1d(N)
        with np.errstate(divide='ignore', invalid='ignore'):
            rate = (-self.beta / self.N0 *
                    np.power(N / self.N0, self.beta - 1) *
                    self.F0 * np.exp(-np.power(N / self.N0, self.beta)))
            rate = np.where(N == 0, 0, rate)
        # Rate is zero when at floor
        F = self.preload(N)
        rate = np.where(F <= self.F_residual, 0.0, rate)
        return rate


# =============================================================================
# POWER-LAW AND LOGARITHMIC MODELS
# =============================================================================

class VDI2230EmbeddingModel(PreloadLossModel):
    """
    VDI 2230 Embedding Loss Model:
    
    ΔF_embed = f_Z × (k_b × k_m) / (k_b + k_m)
    
    Embedding values f_Z per interface (μm):
        - Ground surfaces (Rz < 10): 1-2 μm
        - Machined surfaces (Rz 10-40): 2-4 μm
        - Rough surfaces (Rz 40-160): 3-6 μm
    
    Typical total embedding loss: 5-10% of initial preload
    """
    
    def __init__(self,
                 bolt: BoltParameters,
                 joint: JointParameters,
                 conditions: PreloadConditions,
                 fz_per_interface: float = 3.0,  # μm
                 num_interfaces: int = 4,
                 settling_tau: float = 100.0):   # cycles
        super().__init__(bolt, joint, conditions)
        
        # Total embedding deformation (convert μm to mm)
        self.fz_total = fz_per_interface * num_interfaces / 1000.0  # mm
        
        # Combined stiffness
        kb = joint.bolt_stiffness
        km = joint.member_stiffness
        self.k_combined = (kb * km) / (kb + km)
        
        # Embedding preload loss
        self.delta_F_embed = self.k_combined * self.fz_total
        self.settling_tau = settling_tau
        
    def preload(self, N: np.ndarray) -> np.ndarray:
        N = np.atleast_1d(N)
        # Embedding occurs rapidly, modeled as exponential approach
        settling = 1 - np.exp(-N / self.settling_tau)
        F = self.F0 - self.delta_F_embed * settling
        return np.maximum(F, 0)
    
    def preload_rate(self, N: np.ndarray) -> np.ndarray:
        N = np.atleast_1d(N)
        return -self.delta_F_embed / self.settling_tau * np.exp(-N / self.settling_tau)
    
    def get_embedding_loss_percent(self) -> float:
        """Return percentage of initial preload lost to embedding"""
        return 100.0 * self.delta_F_embed / self.F0


class NortonBaileyCreepModel(PreloadLossModel):
    """
    Norton-Bailey Creep Relaxation Model for elevated temperature:
    
    ε_cr = A × σ^n × t^m
    
    For stress relaxation at constant strain (bolted joint):
    σ(t) = σ₀ × [1 + (n-1)×A×E×σ₀^(n-1)×exp(-Q/RT)×t]^(-1/(n-1))
    
    Converted to preload via: F = σ × A_s
    
    Parameters:
        n: Stress exponent (3-8 for metals)
        m: Time exponent (0.3-0.6 for primary creep)
        A: Creep rate coefficient
        Q: Activation energy (kJ/mol)
        T: Temperature (°C)
    
    Critical: Service T > 0.4×T_melt activates creep
    For L7/L7M: Significant above 300°C, severe above 400°C
    """
    
    def __init__(self,
                 bolt: BoltParameters,
                 joint: JointParameters,
                 conditions: PreloadConditions,
                 n: float = 5.0,           # Stress exponent
                 m: float = 0.4,           # Time exponent
                 A: float = 1e-20,         # Creep coefficient
                 Q: float = 250.0,         # Activation energy (kJ/mol)
                 reference_temp: float = 300.0):  # °C
        super().__init__(bolt, joint, conditions)
        
        self.n = n
        self.m = m
        self.A = A
        self.Q = Q * 1000  # Convert to J/mol
        self.R = 8.314     # Gas constant (J/mol·K)
        self.T = conditions.temperature + 273.15  # Kelvin
        self.ref_temp = reference_temp + 273.15
        
        # Initial stress
        self.sigma0 = self.F0 / bolt.stress_area
        self.E = bolt.elastic_modulus
        
        # Effective creep parameter
        self.B = self.A * np.exp(-self.Q / (self.R * self.T))
        
    def preload(self, N: np.ndarray) -> np.ndarray:
        """Preload as function of cycles (converted from time)"""
        N = np.atleast_1d(N)
        # Convert cycles to time using frequency
        t = N / self.conditions.frequency  # seconds
        t_hours = t / 3600  # hours (typical for creep)
        
        # Norton-Bailey stress relaxation
        if self.n == 1:
            sigma = self.sigma0 * np.exp(-self.B * self.E * t_hours)
        else:
            # General solution
            factor = 1 + (self.n - 1) * self.B * self.E * np.power(self.sigma0, self.n - 1) * t_hours
            factor = np.maximum(factor, 1e-10)  # Prevent negative
            sigma = self.sigma0 * np.power(factor, -1.0 / (self.n - 1))
        
        F = sigma * self.bolt.stress_area
        return np.maximum(F, 0)
    
    def preload_rate(self, N: np.ndarray) -> np.ndarray:
        N = np.atleast_1d(N)
        t = N / self.conditions.frequency
        t_hours = t / 3600
        
        # Derivative of preload: dσ/dt = -E·B·σⁿ (from constant-strain relaxation)
        sigma = self.preload(N) / self.bolt.stress_area
        dsdt = -self.B * self.E * np.power(sigma, self.n)
        
        # Convert to dF/dN
        dFdN = dsdt * self.bolt.stress_area / self.conditions.frequency / 3600
        return dFdN
    
    def get_loss_percent_at_hours(self, hours: float) -> float:
        """Calculate preload loss after given hours"""
        N_equiv = hours * 3600 * self.conditions.frequency
        F_final = self.preload(np.array([N_equiv]))[0]
        return 100.0 * (1 - F_final / self.F0)


class ThermalEffectsModel(PreloadLossModel):
    """
    Preload change due to differential thermal expansion:
    
    ΔF_thermal = (k_b × k_m)/(k_b + k_m) × L × ΔT × (α_m - α_b)
    
    Sign convention:
        α_m > α_b (e.g., aluminum members, steel bolt): Heating INCREASES preload
        α_m < α_b: Heating DECREASES preload
    
    Also includes temperature-dependent elastic modulus:
        E(T) = E₀ × [1 - β_E × (T - T₀)]
    """
    
    def __init__(self,
                 bolt: BoltParameters,
                 joint: JointParameters,
                 conditions: PreloadConditions,
                 alpha_member: float = 12e-6,  # Member thermal expansion (1/K)
                 beta_E: float = 3.5e-4,       # Modulus temp coefficient (1/°C)
                 reference_temp: float = 20.0):
        super().__init__(bolt, joint, conditions)
        
        self.alpha_bolt = bolt.thermal_expansion
        self.alpha_member = alpha_member
        self.delta_alpha = alpha_member - self.alpha_bolt
        self.beta_E = beta_E
        self.ref_temp = reference_temp
        
        # Combined stiffness
        kb = joint.bolt_stiffness
        km = joint.member_stiffness
        self.k_combined = (kb * km) / (kb + km)
        self.grip_length = bolt.length
        
    def preload_at_temperature(self, T: float) -> float:
        """Calculate preload at given temperature"""
        delta_T = T - self.ref_temp
        
        # Thermal preload change
        delta_F = self.k_combined * self.grip_length * delta_T * self.delta_alpha
        
        # Modulus reduction effect (reduces stiffness, affects preload)
        E_ratio = 1 - self.beta_E * delta_T
        E_ratio = max(E_ratio, 0.5)  # Limit reduction
        
        F = self.F0 + delta_F * E_ratio
        return max(F, 0)
    
    def preload(self, N: np.ndarray) -> np.ndarray:
        """For temperature cycling scenarios"""
        N = np.atleast_1d(N)
        # Assume temperature is constant (use conditions.temperature)
        T = self.conditions.temperature
        F_thermal = self.preload_at_temperature(T)
        return np.full_like(N, F_thermal, dtype=float)
    
    def preload_rate(self, N: np.ndarray) -> np.ndarray:
        """Zero rate for constant temperature"""
        return np.zeros_like(np.atleast_1d(N), dtype=float)


class CombinedMechanismModel(PreloadLossModel):
    """
    Combined preload loss from all mechanisms:
    
    ΔF_total = ΔF_embedding + ΔF_creep + ΔF_cyclic + ΔF_thermal
    
    This is the most comprehensive model combining:
    - VDI 2230 embedding (rapid, first 100 cycles)
    - Creep/relaxation (time-dependent)
    - Cyclic plastic deformation (Jiang Stage I)
    - Thermal effects (temperature-dependent)
    - Structural loosening (Jiang Stage II)
    
    For  L7/L7M application with axial loading.
    """
    
    def __init__(self,
                 bolt: BoltParameters,
                 joint: JointParameters,
                 conditions: PreloadConditions,
                 # Embedding parameters
                 embedding_ratio: float = 0.05,      # 5% typical
                 embedding_tau: float = 50.0,        # cycles
                 # Cyclic parameters (double exponential)
                 cyclic_fast_ratio: float = 0.05,
                 cyclic_slow_ratio: float = 0.04,
                 lambda1: float = 0.002,
                 lambda2: float = 0.0002,
                 # Thermal parameters
                 thermal_loss_ratio: float = 0.0,    # Per 100°C above reference
                 # Structural loosening (Stage II)
                 N_structural: float = 10000.0,
                 structural_rate: float = 0.1,       # N/cycle (base rate)
                 # Creep/relaxation parameters (Norton-Bailey)
                 creep_A: float = 1e-18,             # Creep coefficient [MPa^-n hr^-m]
                 creep_n: float = 5.0,               # Norton stress exponent
                 creep_Q: float = 280.0,             # Activation energy [kJ/mol]
                 reference_temp: float = 20.0):      # Reference temperature [°C]
        super().__init__(bolt, joint, conditions)

        # Scale by boundary conditions
        bc_factor = _boundary_condition_factor(conditions, joint)

        # Store parameters
        self.embed_loss = embedding_ratio * self.F0
        self.embed_tau = embedding_tau

        self.A1 = cyclic_fast_ratio * self.F0
        self.A2 = cyclic_slow_ratio * self.F0
        self.lambda1 = lambda1 * bc_factor
        self.lambda2 = lambda2 * bc_factor

        # Thermal loss: VDI 2230 physics-based formula
        # ΔF_thermal = k_sys × L × ΔT × (α_m - α_b)
        delta_T = conditions.temperature - reference_temp
        k_sys = compute_system_stiffness(bolt, joint)['k_system']
        alpha_diff = getattr(joint, 'alpha_member', 12e-6) - bolt.thermal_expansion
        self.thermal_loss = k_sys * bolt.length * delta_T * alpha_diff if abs(delta_T) > 0.1 else 0.0

        self.N_structural = N_structural / max(bc_factor, 0.1)
        self.structural_rate = structural_rate * bc_factor

        # Creep/relaxation parameters (Norton-Bailey, Section 45)
        self.creep_n = creep_n
        self.sigma0 = self.F0 / bolt.stress_area
        self.E = bolt.elastic_modulus
        R_gas = 8.314  # J/(mol·K)
        T_kelvin = conditions.temperature + 273.15
        self.creep_B = creep_A * np.exp(-creep_Q * 1000 / (R_gas * T_kelvin))
        self._has_creep = (conditions.temperature > reference_temp + 50)  # Only above threshold

        # Calculate asymptotic residual (floor)
        self.F_residual = self.F0 * 0.6  # 60% minimum residual
        
    def preload(self, N: np.ndarray) -> np.ndarray:
        N = np.atleast_1d(N)

        # Embedding loss (rapid saturation)
        embed = self.embed_loss * (1 - np.exp(-N / self.embed_tau))

        # Cyclic loss (double exponential)
        cyclic = self.A1 * (1 - np.exp(-self.lambda1 * N)) + \
                 self.A2 * (1 - np.exp(-self.lambda2 * N))

        # Creep/relaxation loss (Norton-Bailey, Section 51.3)
        # ΔF_creep(t) = F₀ × [1 - σ(t)/σ₀]
        creep = np.zeros_like(N, dtype=float)
        if self._has_creep and self.creep_B > 0:
            t_hours = N / max(self.conditions.frequency, 0.001) / 3600
            if self.creep_n == 1:
                sigma_ratio = np.exp(-self.creep_B * self.E * t_hours)
            else:
                factor = 1 + (self.creep_n - 1) * self.creep_B * self.E * \
                         np.power(self.sigma0, self.creep_n - 1) * t_hours
                factor = np.maximum(factor, 1e-10)
                sigma_ratio = np.power(factor, -1.0 / (self.creep_n - 1))
            creep = self.F0 * (1 - sigma_ratio)

        # Structural loosening (after transition)
        structural = np.where(N > self.N_structural,
                             self.structural_rate * (N - self.N_structural),
                             0)

        # Total preload
        F = self.F0 - embed - cyclic - creep - self.thermal_loss - structural

        # Apply residual floor
        F = np.maximum(F, self.F_residual)

        return F
    
    def preload_rate(self, N: np.ndarray) -> np.ndarray:
        N = np.atleast_1d(N)

        # Embedding rate
        embed_rate = -self.embed_loss / self.embed_tau * np.exp(-N / self.embed_tau)

        # Cyclic rate
        cyclic_rate = -self.A1 * self.lambda1 * np.exp(-self.lambda1 * N) - \
                      self.A2 * self.lambda2 * np.exp(-self.lambda2 * N)

        # Creep rate (dσ/dt = -E·B·σⁿ, convert to dF/dN)
        creep_rate = np.zeros_like(N, dtype=float)
        if self._has_creep and self.creep_B > 0:
            # Get current stress from preload
            F_current = self.preload(N)
            sigma = F_current / self.bolt.stress_area
            dsdt = -self.creep_B * self.E * np.power(sigma, self.creep_n)
            creep_rate = dsdt * self.bolt.stress_area / max(self.conditions.frequency, 0.001) / 3600

        # Structural rate
        structural_rate = np.where(N > self.N_structural, -self.structural_rate, 0)

        return embed_rate + cyclic_rate + creep_rate + structural_rate
    
    def get_loss_breakdown(self, N: float) -> Dict[str, float]:
        """Return breakdown of losses by mechanism at given cycle count"""
        embed = self.embed_loss * (1 - np.exp(-N / self.embed_tau))
        cyclic = self.A1 * (1 - np.exp(-self.lambda1 * N)) + \
                 self.A2 * (1 - np.exp(-self.lambda2 * N))
        structural = max(0, self.structural_rate * (N - self.N_structural)) if N > self.N_structural else 0

        # Creep loss
        creep = 0.0
        if self._has_creep and self.creep_B > 0:
            t_hours = N / max(self.conditions.frequency, 0.001) / 3600
            if self.creep_n == 1:
                sigma_ratio = np.exp(-self.creep_B * self.E * t_hours)
            else:
                factor = 1 + (self.creep_n - 1) * self.creep_B * self.E * \
                         np.power(self.sigma0, self.creep_n - 1) * t_hours
                factor = max(factor, 1e-10)
                sigma_ratio = factor ** (-1.0 / (self.creep_n - 1))
            creep = self.F0 * (1 - sigma_ratio)

        total = embed + cyclic + creep + self.thermal_loss + structural

        return {
            'embedding': embed,
            'cyclic': cyclic,
            'creep': creep,
            'thermal': self.thermal_loss,
            'structural': structural,
            'total': total,
            'remaining_percent': 100.0 * max(0, self.F0 - total) / self.F0
        }


class MinersRuleDamageModel:
    """
    Miner's Rule for variable amplitude loading damage accumulation:
    
    D = Σ(n_i / N_i)
    
    Loosening occurs when D ≥ 1.0 (validated range: D = 0.8-1.2)
    
    For two-block loading sequences:
    - High-low sequences: D < 1.0 typically
    - Low-high sequences: D > 1.0 typically
    
    Used with D-N curves for life prediction.
    """
    
    def __init__(self, dn_curve_params: Dict[str, float] = None):
        # Default bilinear D-N curve parameters
        if dn_curve_params is None:
            self.C1 = 1e6   # Low-cycle constant
            self.m1 = 3.0   # Low-cycle slope
            self.C2 = 1e8   # High-cycle constant
            self.m2 = 5.0   # High-cycle slope
            self.d_threshold = 0.3  # mm, transition amplitude
            self.d_endurance = 0.15  # mm, endurance limit
        else:
            self.C1 = dn_curve_params.get('C1', 1e6)
            self.m1 = dn_curve_params.get('m1', 3.0)
            self.C2 = dn_curve_params.get('C2', 1e8)
            self.m2 = dn_curve_params.get('m2', 5.0)
            self.d_threshold = dn_curve_params.get('d_threshold', 0.3)
            self.d_endurance = dn_curve_params.get('d_endurance', 0.15)
    
    def cycles_to_loosening(self, displacement_amplitude: float) -> float:
        """Calculate cycles to loosening from D-N curve"""
        if displacement_amplitude <= self.d_endurance:
            return np.inf  # Below endurance limit
        
        if displacement_amplitude > self.d_threshold:
            # Low-cycle region
            return self.C1 * np.power(displacement_amplitude, -self.m1)
        else:
            # High-cycle region
            return self.C2 * np.power(displacement_amplitude, -self.m2)
    
    def accumulate_damage(self, 
                          amplitudes: List[float], 
                          cycles: List[int]) -> Tuple[float, List[float]]:
        """
        Calculate cumulative damage for variable amplitude loading.
        
        Returns:
            total_damage: Cumulative Miner's damage
            partial_damages: Damage contribution from each block
        """
        partial_damages = []
        total_damage = 0.0
        
        for amp, n in zip(amplitudes, cycles):
            N_life = self.cycles_to_loosening(amp)
            if N_life < np.inf:
                d = n / N_life
            else:
                d = 0.0
            partial_damages.append(d)
            total_damage += d
        
        return total_damage, partial_damages
    
    def remaining_life(self, 
                       current_damage: float,
                       future_amplitude: float) -> float:
        """Calculate remaining cycles at given amplitude after accumulated damage"""
        if current_damage >= 1.0:
            return 0.0
        
        N_total = self.cycles_to_loosening(future_amplitude)
        if N_total == np.inf:
            return np.inf
        
        remaining_damage_capacity = 1.0 - current_damage
        return remaining_damage_capacity * N_total


class EnergyDissipationModel:
    """
    Energy-based analysis for friction and wear:
    
    E_diss = ∮ F · dx (hysteresis loop area per cycle)
    
    Wear is proportional to cumulative dissipated energy:
    V = α × E_d (Fouvry energy-based wear)
    
    Power-law energy dissipation (Iwan model):
    W_d ∝ F_amp^β where β ≈ χ + 3 (typically 2.5-3.0)
    """
    
    def __init__(self,
                 mu: float = 0.12,
                 normal_force: float = 50000.0,  # N
                 displacement_amplitude: float = 0.5e-3,  # m
                 alpha_wear: float = 3e-8):  # MPa⁻¹
        self.mu = mu
        self.N = normal_force
        self.delta = displacement_amplitude
        self.alpha = alpha_wear
        
    def energy_per_cycle(self) -> float:
        """Frictional energy dissipated per cycle (gross slip approximation)"""
        # Rectangular hysteresis loop approximation
        return 4 * self.mu * self.N * self.delta
    
    def cumulative_energy(self, cycles: int) -> float:
        """Total energy dissipated over cycles"""
        return self.energy_per_cycle() * cycles
    
    def wear_volume(self, cycles: int) -> float:
        """Wear volume based on energy dissipation (mm³)"""
        E_total = self.cumulative_energy(cycles)
        # Convert to consistent units and apply Fouvry coefficient
        return self.alpha * E_total * 1e6  # mm³
    
    def wear_depth(self, cycles: int, contact_area: float = 100.0) -> float:
        """Average wear depth (μm) given contact area (mm²)"""
        V = self.wear_volume(cycles)
        h = V / contact_area * 1000  # μm
        return h


class PowerLawModel(PreloadLossModel):
    """
    Power-law (allometric) decay model (Lu et al., 2024):
    F(N)/F0 = c·N^(-α) or F(N) = F0·(1 + N/Nc)^(-α)
    
    Achieves >85.5% fitting accuracy with only two parameters.
    
    Parameters:
        alpha: Power-law exponent (typically -0.1 to -0.5)
        Nc: Critical transition cycle number
    """
    
    def __init__(self,
                 bolt: BoltParameters,
                 joint: JointParameters,
                 conditions: PreloadConditions,
                 alpha: float = 0.15,
                 Nc: float = 10.0):
        super().__init__(bolt, joint, conditions)
        self.alpha = alpha
        self.Nc = Nc
        
    def preload(self, N: np.ndarray) -> np.ndarray:
        N = np.atleast_1d(N)
        return self.F0 * np.power(1 + N / self.Nc, -self.alpha)
    
    def preload_rate(self, N: np.ndarray) -> np.ndarray:
        N = np.atleast_1d(N)
        return (-self.alpha * self.F0 / self.Nc * 
                np.power(1 + N / self.Nc, -self.alpha - 1))


class LogarithmicModel(PreloadLossModel):
    """
    Logarithmic decay model: F(N) = max(F_residual, F0 - k·ln(N+1))

    For embedment-dominated relaxation during first few hundred cycles.

    Parameters:
        k: Logarithmic decay coefficient
        F_residual_ratio: Minimum residual preload as fraction of F0 (default 0.05 = 5%)
    """

    def __init__(self,
                 bolt: BoltParameters,
                 joint: JointParameters,
                 conditions: PreloadConditions,
                 k: float = 2000.0,
                 F_residual_ratio: float = 0.05):
        super().__init__(bolt, joint, conditions)
        self.k = k
        self.F_residual = F_residual_ratio * self.F0  # H5: floor at 5% of F0

    def preload(self, N: np.ndarray) -> np.ndarray:
        N = np.atleast_1d(N)
        F = self.F0 - self.k * np.log(N + 1)
        return np.maximum(F, self.F_residual)  # H5: enforce floor

    def preload_rate(self, N: np.ndarray) -> np.ndarray:
        N = np.atleast_1d(N)
        rate = -self.k / (N + 1)
        # Rate is zero when at floor
        F = self.preload(N)
        rate = np.where(F <= self.F_residual, 0.0, rate)
        return rate


# =============================================================================
# JIANG TWO-STAGE AND THREE-STAGE MODELS
# =============================================================================

class JiangTwoStageModel(PreloadLossModel):
    """
    Jiang et al. (2003-2004) two-stage loosening model:
    
    Stage I (Material Loosening, 0-N_trans cycles):
        - Rapid non-linear preload decrease
        - Localized cyclic plastic deformation at thread roots
        - No relative rotation
        - F(N) = F0 - ΔF_embed·[1 - exp(-N/N1)]
    
    Stage II (Structural Loosening, N > N_trans):
        - Gradual preload decrease due to nut back-off rotation
        - Approximately linear decay rate
        - F(N) = F_trans - k2·(N - N_trans)
    
    Transition: Occurs at ~0.5° nut rotation or ~90% of F0
    """
    
    def __init__(self,
                 bolt: BoltParameters,
                 joint: JointParameters,
                 conditions: PreloadConditions,
                 N_trans: float = 500.0,
                 delta_F_embed_ratio: float = 0.12,
                 N1: float = 50.0,
                 k2: float = 0.5):
        super().__init__(bolt, joint, conditions)
        # Scale transition cycles and decay rate by boundary conditions
        bc_factor = _boundary_condition_factor(conditions, joint)
        self.N_trans = N_trans / max(bc_factor, 0.1)  # Faster transition under severe BC
        self.delta_F_embed = delta_F_embed_ratio * self.F0
        self.N1 = N1 / max(bc_factor, 0.1)
        self.k2 = k2 * bc_factor  # Stage II linear rate (N/cycle), scaled by BC
        
        # Calculate preload at transition
        self.F_trans = self.F0 - self.delta_F_embed * (1 - np.exp(-self.N_trans / self.N1))
        
    def preload(self, N: np.ndarray) -> np.ndarray:
        N = np.atleast_1d(N)
        F = np.zeros_like(N, dtype=float)
        
        # Stage I: Material loosening (exponential)
        stage1_mask = N <= self.N_trans
        F[stage1_mask] = (self.F0 - 
                         self.delta_F_embed * (1 - np.exp(-N[stage1_mask] / self.N1)))
        
        # Stage II: Structural loosening (linear)
        stage2_mask = N > self.N_trans
        F[stage2_mask] = self.F_trans - self.k2 * (N[stage2_mask] - self.N_trans)
        
        return np.maximum(F, 0)
    
    def preload_rate(self, N: np.ndarray) -> np.ndarray:
        N = np.atleast_1d(N)
        rate = np.zeros_like(N, dtype=float)
        
        # Stage I rate
        stage1_mask = N <= self.N_trans
        rate[stage1_mask] = (-self.delta_F_embed / self.N1 * 
                            np.exp(-N[stage1_mask] / self.N1))
        
        # Stage II rate (constant)
        stage2_mask = N > self.N_trans
        rate[stage2_mask] = -self.k2
        
        return rate
    
    def get_stage(self, N: np.ndarray) -> np.ndarray:
        """Return stage number (1 or 2) for each cycle count"""
        N = np.atleast_1d(N)
        return np.where(N <= self.N_trans, 1, 2)


class JiangThreeStageModel(PreloadLossModel):
    """
    Extended Jiang model (Gong, Liu & Ding 2019; Yang et al. 2021):
    
    Stage I: Plastic deformation + stress redistribution (non-linear rapid)
    Stage II: Rotational loosening (linear steady)
    Stage III: Fatigue crack propagation (sharp accelerating)
    
    F(N) is piecewise with smooth transitions.
    """
    
    def __init__(self,
                 bolt: BoltParameters,
                 joint: JointParameters,
                 conditions: PreloadConditions,
                 N_trans_12: float = 500.0,
                 N_trans_23: float = 50000.0,
                 delta_F1_ratio: float = 0.15,
                 N1: float = 50.0,
                 k2: float = 0.3,
                 k3: float = 0.05,
                 n3: float = 1.5):
        super().__init__(bolt, joint, conditions)
        bc_factor = _boundary_condition_factor(conditions, joint)
        self.N_trans_12 = N_trans_12 / max(bc_factor, 0.1)
        self.N_trans_23 = N_trans_23 / max(bc_factor, 0.1)
        self.delta_F1 = delta_F1_ratio * self.F0
        self.N1 = N1 / max(bc_factor, 0.1)
        self.k2 = k2 * bc_factor  # Stage II linear rate, scaled
        self.k3 = k3 * bc_factor  # Stage III base rate, scaled
        self.n3 = n3  # Stage III acceleration exponent
        
        # Calculate preloads at transitions
        self.F_trans_12 = self.F0 - self.delta_F1 * (1 - np.exp(-self.N_trans_12 / self.N1))
        self.F_trans_23 = self.F_trans_12 - self.k2 * (self.N_trans_23 - self.N_trans_12)
        
    def preload(self, N: np.ndarray) -> np.ndarray:
        N = np.atleast_1d(N)
        F = np.zeros_like(N, dtype=float)
        
        # Stage I: Rapid non-linear
        s1 = N <= self.N_trans_12
        F[s1] = self.F0 - self.delta_F1 * (1 - np.exp(-N[s1] / self.N1))
        
        # Stage II: Linear steady
        s2 = (N > self.N_trans_12) & (N <= self.N_trans_23)
        F[s2] = self.F_trans_12 - self.k2 * (N[s2] - self.N_trans_12)
        
        # Stage III: Accelerating (power law)
        s3 = N > self.N_trans_23
        delta_N = N[s3] - self.N_trans_23
        F[s3] = self.F_trans_23 - self.k3 * np.power(delta_N, self.n3)
        
        return np.maximum(F, 0)
    
    def preload_rate(self, N: np.ndarray) -> np.ndarray:
        N = np.atleast_1d(N)
        rate = np.zeros_like(N, dtype=float)
        
        s1 = N <= self.N_trans_12
        rate[s1] = -self.delta_F1 / self.N1 * np.exp(-N[s1] / self.N1)
        
        s2 = (N > self.N_trans_12) & (N <= self.N_trans_23)
        rate[s2] = -self.k2
        
        s3 = N > self.N_trans_23
        delta_N = N[s3] - self.N_trans_23
        with np.errstate(divide='ignore', invalid='ignore'):
            rate[s3] = -self.k3 * self.n3 * np.power(delta_N, self.n3 - 1)
            rate[s3] = np.where(delta_N == 0, 0, rate[s3])
        
        return rate
    
    def get_stage(self, N: np.ndarray) -> np.ndarray:
        """Return stage number (1, 2, or 3)"""
        N = np.atleast_1d(N)
        stage = np.ones_like(N, dtype=int)
        stage[N > self.N_trans_12] = 2
        stage[N > self.N_trans_23] = 3
        return stage


# =============================================================================
# D-N CURVES (DISPLACEMENT-LIFE)
# =============================================================================

class DNLooseningCurve:
    """
    Displacement-Life (D-N) curve for loosening life prediction.
    Analogous to S-N fatigue curves.
    
    Bilinear form in log-log coordinates:
        High-cycle (small amplitude): log(N) = C1 - m1·log(d)
        Low-cycle (large amplitude):  log(N) = C2 - m2·log(d)
    
    Parameters:
        d_threshold: Critical displacement below which no loosening occurs
        C1, m1: High-cycle region parameters
        C2, m2: Low-cycle region parameters
        d_transition: Displacement at bilinear transition
    """
    
    def __init__(self,
                 d_threshold: float = 0.1,      # mm
                 C1: float = 5.0,
                 m1: float = 3.0,
                 C2: float = 4.0,
                 m2: float = 1.5,
                 d_transition: float = 0.5):    # mm
        self.d_threshold = d_threshold
        self.C1 = C1
        self.m1 = m1
        self.C2 = C2
        self.m2 = m2
        self.d_transition = d_transition
        
    def cycles_to_loosening(self, displacement: np.ndarray) -> np.ndarray:
        """Calculate cycles to loosening for given displacement amplitude"""
        d = np.atleast_1d(displacement)
        N = np.zeros_like(d, dtype=float)
        
        # Below threshold: infinite life
        below_thresh = d <= self.d_threshold
        N[below_thresh] = np.inf
        
        # High-cycle region
        high_cycle = (d > self.d_threshold) & (d <= self.d_transition)
        N[high_cycle] = np.power(10, self.C1 - self.m1 * np.log10(d[high_cycle]))
        
        # Low-cycle region
        low_cycle = d > self.d_transition
        N[low_cycle] = np.power(10, self.C2 - self.m2 * np.log10(d[low_cycle]))
        
        return N
    
    def critical_displacement(self, N_target: float) -> float:
        """Calculate displacement for target life"""
        if N_target <= 0:
            return np.inf
            
        # Try high-cycle region first
        d_high = np.power(10, (self.C1 - np.log10(N_target)) / self.m1)
        if d_high <= self.d_transition:
            return d_high
        
        # Low-cycle region
        d_low = np.power(10, (self.C2 - np.log10(N_target)) / self.m2)
        return d_low


class MinersRuleAccumulation:
    """
    Miner's rule for variable amplitude loading:
    D = Σ(ni/Ni), loosening when D ≥ 1
    
    For bolt loosening, validated range: D = 0.8-1.2
    High-low sequences: D < 1.0 typically
    Low-high sequences: D > 1.0 typically
    """
    
    def __init__(self, dn_curve: DNLooseningCurve, damage_limit: float = 1.0):
        self.dn_curve = dn_curve
        self.damage_limit = damage_limit
        self.damage_accumulated = 0.0
        self.history = []
        
    def add_loading_block(self, displacement: float, cycles: int):
        """Add a block of constant-amplitude loading"""
        N_life = self.dn_curve.cycles_to_loosening(displacement)
        if np.isinf(N_life):
            damage = 0.0
        else:
            damage = cycles / N_life
        
        self.damage_accumulated += damage
        self.history.append({
            'displacement': displacement,
            'cycles': cycles,
            'N_life': N_life,
            'block_damage': damage,
            'cumulative_damage': self.damage_accumulated
        })
        
    def is_loosened(self) -> bool:
        """Check if loosening has occurred"""
        return self.damage_accumulated >= self.damage_limit
    
    def remaining_life_fraction(self) -> float:
        """Return remaining life as fraction of total"""
        return max(0, 1 - self.damage_accumulated / self.damage_limit)


# =============================================================================
# ROTATION ANGLE MODELS
# =============================================================================

class RotationAngleModel:
    """
    Cumulative nut rotation model.
    
    Key finding (Jiang): 0.5° rotation marks boundary between 
    material (Stage I) and structural (Stage II) loosening.
    
    Rotation-preload relationship:
        ΔF = (P/2π)·θ·(Kb·Kj)/(Kb+Kj)
    """
    
    def __init__(self,
                 bolt: BoltParameters,
                 joint: JointParameters,
                 initial_preload: float):
        self.bolt = bolt
        self.joint = joint
        self.F0 = initial_preload
        
        # Combined stiffness
        kb = joint.bolt_stiffness
        km = joint.member_stiffness
        self.k_combined = (kb * km) / (kb + km)
        
    def preload_from_rotation(self, theta_deg: np.ndarray) -> np.ndarray:
        """Calculate preload loss from rotation angle (degrees)"""
        theta_rad = np.radians(theta_deg)
        delta_F = (self.bolt.pitch / (2 * np.pi)) * theta_rad * self.k_combined
        return self.F0 - delta_F
    
    def rotation_from_preload(self, F: np.ndarray) -> np.ndarray:
        """Calculate rotation angle (degrees) from preload"""
        delta_F = self.F0 - np.atleast_1d(F)
        theta_rad = delta_F * (2 * np.pi) / (self.bolt.pitch * self.k_combined)
        return np.degrees(theta_rad)
    
    def rotation_rate(self, N: np.ndarray, 
                      stage1_cycles: float = 500,
                      stage2_rate: float = 0.01) -> np.ndarray:
        """
        Rotation rate dθ/dN evolution.
        Stage I: Near zero (no rotation)
        Stage II: Maximum steady rate
        """
        N = np.atleast_1d(N)
        rate = np.zeros_like(N, dtype=float)
        
        # Transition function (smooth sigmoid)
        transition = 1 / (1 + np.exp(-(N - stage1_cycles) / (stage1_cycles * 0.1)))
        rate = stage2_rate * transition
        
        return rate  # deg/cycle


# =============================================================================
# EMBEDDING LOSS MODEL (VDI 2230)
# =============================================================================

class EmbeddingLossModel:
    """
    VDI 2230 embedding/settling loss model.
    
    FZ = Kb·fZ where fZ is total embedding (μm).
    
    Typical values per interface:
        Ground (Rz < 10 μm): 1-3 μm
        Medium roughness (Rz 10-40 μm): 2-4 μm
        Design assumption: 5% preload loss general
    """
    
    def __init__(self,
                 bolt: BoltParameters,
                 joint: JointParameters,
                 n_interfaces: int = 4):
        self.bolt = bolt
        self.joint = joint
        self.n_interfaces = n_interfaces
        
        # Embedding per interface based on roughness
        Ra = joint.surface_roughness
        if Ra < 1.6:
            self.embed_per_interface = 1.5e-3  # mm
        elif Ra < 3.2:
            self.embed_per_interface = 2.5e-3  # mm
        else:
            self.embed_per_interface = 4.0e-3  # mm
            
    def total_embedding(self) -> float:
        """Total embedding deformation (mm)"""
        return self.n_interfaces * self.embed_per_interface
    
    def embedding_preload_loss(self, initial_preload: float) -> float:
        """Preload loss due to embedding (N)"""
        fZ = self.total_embedding()
        return self.joint.bolt_stiffness * fZ
    
    def embedding_loss_fraction(self, initial_preload: float) -> float:
        """Embedding loss as fraction of initial preload"""
        return self.embedding_preload_loss(initial_preload) / initial_preload
    
    def preload_with_embedding(self, N: np.ndarray, 
                               initial_preload: float,
                               embed_time_constant: float = 20.0) -> np.ndarray:
        """
        Preload evolution including embedding (saturating).
        Embedding occurs rapidly in first ~100 cycles.
        """
        N = np.atleast_1d(N)
        delta_F_embed = self.embedding_preload_loss(initial_preload)
        embed_factor = 1 - np.exp(-N / embed_time_constant)
        return initial_preload - delta_F_embed * embed_factor


# =============================================================================
# COMBINED MODEL WITH MULTIPLE MECHANISMS
# =============================================================================

class CombinedPreloadLossModel(PreloadLossModel):
    """
    Combined model including all preload loss mechanisms:
    
    ΔF_total = ΔF_embedding + ΔF_creep + ΔF_cyclic + ΔF_thermal
    
    Uses Jiang two-stage as base with additional corrections.
    """
    
    def __init__(self,
                 bolt: BoltParameters,
                 joint: JointParameters,
                 conditions: PreloadConditions,
                 include_embedding: bool = True,
                 include_thermal: bool = True):
        super().__init__(bolt, joint, conditions)
        
        # Base Jiang model (k2 is already BC-scaled inside JiangTwoStageModel)
        self.base_model = JiangTwoStageModel(
            bolt, joint, conditions,
            N_trans=500, delta_F_embed_ratio=0.10, N1=50, k2=0.4
        )
        
        # Embedding model
        self.embedding_model = EmbeddingLossModel(bolt, joint) if include_embedding else None
        
        # Thermal effects
        self.include_thermal = include_thermal
        self.thermal_loss = self._calculate_thermal_loss() if include_thermal else 0.0
        
    def _calculate_thermal_loss(self) -> float:
        """Calculate preload change due to differential thermal expansion"""
        delta_T = self.conditions.delta_temperature
        alpha_b = self.bolt.thermal_expansion
        alpha_m = 11e-6  # Assume steel members
        
        # ΔF = (αm - αb)·ΔT·L·(Kb·Km)/(Kb+Km)
        L = self.bolt.length
        kb = self.joint.bolt_stiffness
        km = self.joint.member_stiffness
        k_eff = (kb * km) / (kb + km)
        
        delta_F_thermal = (alpha_m - alpha_b) * delta_T * L * k_eff
        return delta_F_thermal
        
    def preload(self, N: np.ndarray) -> np.ndarray:
        N = np.atleast_1d(N)
        
        # Start with base Jiang model
        F = self.base_model.preload(N)
        
        # Add thermal effect (constant offset)
        if self.include_thermal:
            F = F - self.thermal_loss
        
        # Embedding already included in Jiang stage I, but add additional if needed
        # (Jiang model accounts for plastic settling, VDI embedding adds surface settling)
        
        return np.maximum(F, 0)
    
    def preload_rate(self, N: np.ndarray) -> np.ndarray:
        return self.base_model.preload_rate(N)
    
    def get_loss_breakdown(self, N: float) -> Dict[str, float]:
        """Get breakdown of preload loss by mechanism"""
        N_arr = np.array([N])
        total_loss = self.F0 - self.preload(N_arr)[0]
        
        # Estimate contributions
        stage = self.base_model.get_stage(N_arr)[0]
        
        breakdown = {
            'embedding': self.base_model.delta_F_embed * (1 - np.exp(-N / self.base_model.N1)),
            'thermal': self.thermal_loss if self.include_thermal else 0.0,
            'cyclic_rotation': max(0, total_loss - self.base_model.delta_F_embed) if stage == 2 else 0.0,
            'total': total_loss
        }
        
        return breakdown


# =============================================================================
# FACTORY FUNCTION
# =============================================================================

def create_preload_loss_model(
    model_type: DecayModelType,
    bolt: BoltParameters,
    joint: JointParameters,
    conditions: PreloadConditions,
    **kwargs
) -> PreloadLossModel:
    """
    Factory function to create preload loss models.
    
    Args:
        model_type: Type of decay model
        bolt: Bolt parameters
        joint: Joint parameters  
        conditions: Loading conditions
        **kwargs: Model-specific parameters
    """
    
    models = {
        DecayModelType.SINGLE_EXPONENTIAL: SingleExponentialModel,
        DecayModelType.DOUBLE_EXPONENTIAL: DoubleExponentialModel,
        DecayModelType.STRETCHED_EXPONENTIAL: StretchedExponentialModel,
        DecayModelType.POWER_LAW: PowerLawModel,
        DecayModelType.LOGARITHMIC: LogarithmicModel,
        DecayModelType.JIANG_TWO_STAGE: JiangTwoStageModel,
        DecayModelType.JIANG_THREE_STAGE: JiangThreeStageModel,
    }
    
    if model_type not in models:
        raise ValueError(f"Unknown model type: {model_type}")
    
    return models[model_type](bolt, joint, conditions, **kwargs)


# =============================================================================
# STANDARD TEST DATA GENERATOR
# =============================================================================

def generate_standard_test_data() -> Dict:
    """
    Generate standard test data representing typical M12 L7 stud
    in API 6A flanged connection.
    """
    
    # Create parameters
    bolt = BoltParameters(
        diameter=12.0,
        pitch=1.75,
        length=60.0,
        thread_length=25.0,
        elastic_modulus=210e3,
        yield_strength=720.0
    )
    
    joint = JointParameters(
        bolt_stiffness=5e5,
        member_stiffness=1.5e6,
        mu_thread=0.12,
        mu_bearing=0.14,
        surface_roughness=3.2
    )
    
    conditions = PreloadConditions(
        initial_preload=50000.0,
        yield_utilization=0.7,
        loading_type=LoadingType.AXIAL,
        displacement_amplitude=0.5,
        frequency=25.0,
        temperature=20.0,
        delta_temperature=60.0
    )
    
    return {
        'bolt': bolt,
        'joint': joint,
        'conditions': conditions
    }
