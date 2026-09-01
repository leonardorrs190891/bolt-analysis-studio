"""
Friction Evolution and Wear Models for Bolted Joints
====================================================

This module contains advanced friction and wear models including:
- Coulomb friction with regularization
- LuGre dynamic friction model
- Dahl friction model
- Iwan distributed element model
- Friction coefficient evolution over cycles
- Archard and Fouvry wear models

References:
- Canudas-de-Wit et al. (1995) IEEE Trans. Automatic Control
- Segalman (2002) Sandia Report SAND2002-3828
- Hintikka et al. (2020) Tribology International
- Fouvry et al. (2003) Wear

BAS +  R&D
"""

import numpy as np
from dataclasses import dataclass, field
from typing import Tuple, Optional, Callable, Dict
from enum import Enum
from abc import ABC, abstractmethod


# =============================================================================
# ENUMERATIONS
# =============================================================================

class FrictionModelType(Enum):
    """Types of friction models"""
    COULOMB = "coulomb"
    COULOMB_VISCOUS = "coulomb_viscous"
    LUGRE = "lugre"
    DAHL = "dahl"
    IWAN = "iwan"
    BOUC_WEN = "bouc_wen"


class LubricationRegime(Enum):
    """Stribeck lubrication regimes"""
    BOUNDARY = "boundary"        # λ < 1, μ = 0.1-0.3
    MIXED = "mixed"              # 1 < λ < 3, μ = 0.01-0.1
    HYDRODYNAMIC = "hydrodynamic"  # λ > 3, μ = 0.001-0.01


class WearRegime(Enum):
    """Fretting wear regimes"""
    PARTIAL_SLIP = "partial_slip"   # K ~ 10⁻⁷ to 10⁻⁸
    GROSS_SLIP = "gross_slip"       # K ~ 10⁻⁴ to 10⁻⁶


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class CoulombParameters:
    """Parameters for Coulomb friction model"""
    mu_static: float = 0.15       # Static friction coefficient
    mu_kinetic: float = 0.12      # Kinetic friction coefficient
    v_reg: float = 1e-4           # Regularization velocity (m/s)
    
    @property
    def stiction_ratio(self) -> float:
        return self.mu_static / self.mu_kinetic


@dataclass
class LuGreParameters:
    """
    Parameters for LuGre dynamic friction model.
    
    Typical ranges:
        σ0 (bristle stiffness): 10⁴ - 10⁶ N/m
        σ1 (bristle damping): 10² - 10⁴ N·s/m
        σ2 (viscous coefficient): 0.1 - 100 N·s/m
        vs (Stribeck velocity): 0.001 - 0.1 m/s
    """
    sigma0: float = 1e5          # Bristle stiffness (N/m)
    sigma1: float = 300.0        # Bristle damping (N·s/m)
    sigma2: float = 0.1          # Viscous friction coefficient (N·s/m)
    Fs: float = 100.0            # Maximum static friction force (N)
    Fc: float = 80.0             # Coulomb friction force (N)
    vs: float = 0.001            # Stribeck velocity (m/s)
    alpha: float = 2.0           # Stribeck exponent (typically 1-2)
    
    @property
    def stiction_ratio(self) -> float:
        return self.Fs / self.Fc


@dataclass
class DahlParameters:
    """
    Parameters for Dahl friction model.
    
    Correlation with Mindlin: σ = 8a/G*, α = 1/3
    where a = Hertzian contact radius, G* = combined shear compliance
    """
    sigma: float = 1e5           # Stiffness coefficient (N/m)
    Fc: float = 100.0            # Coulomb friction force (N)
    alpha: float = 1.0           # Shape exponent (0.33-1.0)


@dataclass
class IwanParameters:
    """
    Parameters for Segalman four-parameter Iwan model.
    
    Energy dissipation: W_d ∝ F_amp^β where β = χ + 3
    Typically β = 2.5-3.0 for mechanical joints
    """
    K_T: float = 1e6             # Initial tangent stiffness (N/m)
    F_s: float = 100.0           # Critical slip force (N)
    chi: float = 0.5             # Power law exponent
    R: float = 1.0               # Density function coefficient
    
    @property
    def energy_exponent(self) -> float:
        """Energy dissipation exponent β = χ + 3"""
        return self.chi + 3


@dataclass
class WearParameters:
    """Parameters for wear models"""
    K_archard: float = 1e-7      # Archard wear coefficient (dimensionless)
    k_dimensional: float = 1e-8  # Dimensional wear coefficient (mm³/N·m)
    hardness: float = 3000.0     # Surface hardness (MPa)
    alpha_fouvry: float = 3e-8   # Fouvry energy wear coefficient (MPa⁻¹)


@dataclass
class FrictionEvolutionParameters:
    """
    Parameters for friction coefficient evolution over cycles.
    
    Three-phase model (Hintikka et al. 2020):
    Phase 1 (N < 100): Running-in
    Phase 2 (100 < N < 10⁵): Steady state
    Phase 3 (N > 10⁵): Degradation
    """
    mu_initial: float = 0.14     # Initial coefficient
    mu_peak: float = 0.18        # Peak during running-in
    mu_steady: float = 0.12      # Steady-state coefficient
    N1: float = 50.0             # Running-in rise cycles
    N2: float = 500.0            # Peak decay cycles
    N3: float = 5000.0           # Stabilization cycles
    beta_degrade: float = 0.01   # Degradation rate (log scale)
    N_critical: float = 1e5      # Degradation onset cycles


# =============================================================================
# FRICTION MODELS
# =============================================================================

class FrictionModel(ABC):
    """Abstract base class for friction models"""
    
    @abstractmethod
    def friction_force(self, v: float, N: float, state: Optional[np.ndarray] = None) -> float:
        """Calculate friction force given velocity and normal force"""
        pass
    
    @abstractmethod
    def friction_coefficient(self, v: float) -> float:
        """Calculate effective friction coefficient"""
        pass


class CoulombFriction(FrictionModel):
    """
    Regularized Coulomb friction model.
    
    F = μN·tanh(v/v_reg) for smooth transition
    
    Or with static/kinetic distinction:
    F = μ(v)·N where μ(v) transitions from μs to μk
    """
    
    def __init__(self, params: CoulombParameters):
        self.params = params
        
    def friction_force(self, v: float, N: float, state: Optional[np.ndarray] = None) -> float:
        """
        Calculate friction force with regularization.
        
        Args:
            v: Relative velocity (m/s)
            N: Normal force (N)
            state: Not used for Coulomb
        """
        mu = self.friction_coefficient(v)
        # Regularized sign function
        return mu * N * np.tanh(v / self.params.v_reg)
    
    def friction_coefficient(self, v: float) -> float:
        """
        Velocity-dependent friction coefficient.
        Smooth transition from static to kinetic.
        """
        v_abs = np.abs(v)
        # Exponential transition
        v_trans = 0.01  # Transition velocity scale
        mu = (self.params.mu_kinetic + 
              (self.params.mu_static - self.params.mu_kinetic) * 
              np.exp(-v_abs / v_trans))
        return mu


class LuGreFriction(FrictionModel):
    """
    LuGre dynamic friction model.
    
    State equation: dz/dt = v - σ0|v|z/g(v)
    Friction: F = σ0·z + σ1·dz/dt + σ2·v
    Stribeck: g(v) = Fc + (Fs-Fc)·exp(-(|v|/vs)^α)
    
    Captures:
    - Pre-sliding displacement
    - Stick-slip transitions
    - Stribeck effect
    - Hysteresis
    """
    
    def __init__(self, params: LuGreParameters):
        self.params = params
        self.z = 0.0  # Bristle state
        
    def stribeck_function(self, v: float) -> float:
        """Calculate g(v) - the Stribeck function"""
        p = self.params
        return p.Fc + (p.Fs - p.Fc) * np.exp(-np.power(np.abs(v) / p.vs, p.alpha))
    
    def bristle_derivative(self, v: float, z: float) -> float:
        """Calculate dz/dt"""
        p = self.params
        g_v = self.stribeck_function(v)
        return v - p.sigma0 * np.abs(v) * z / g_v
    
    def friction_force(self, v: float, N: float, state: Optional[np.ndarray] = None,
                       dt: float = None) -> float:
        """
        Calculate LuGre friction force.

        If dt is provided, automatically integrates bristle state before
        computing the force. This prevents stale state issues when the
        caller forgets to call integrate_state() separately.

        Args:
            v: Relative velocity (m/s)
            N: Normal force (N) - used for scaling
            state: [z] bristle displacement state
            dt: Time step for auto-integration (optional)
        """
        p = self.params

        # Auto-integrate state if dt is provided (M10 fix)
        if dt is not None and dt > 0:
            self.integrate_state(v, dt)

        if state is not None:
            z = state[0]
        else:
            z = self.z

        dz_dt = self.bristle_derivative(v, z)

        # Friction force (normalized by reference normal force)
        F = p.sigma0 * z + p.sigma1 * dz_dt + p.sigma2 * v

        return F
    
    def friction_coefficient(self, v: float) -> float:
        """
        Steady-state friction coefficient.
        At constant velocity: z_ss = g(v)·sign(v)/σ0
        """
        p = self.params
        g_v = self.stribeck_function(v)
        F_ss = g_v * np.sign(v) + p.sigma2 * v
        # Assume reference normal force of 1000 N
        return np.abs(F_ss) / 1000.0
    
    def integrate_state(self, v: float, dt: float) -> float:
        """
        Integrate bristle state using implicit Euler.
        
        Returns new bristle state z.
        """
        p = self.params
        g_v = self.stribeck_function(v)
        
        # Implicit Euler: z_new = (z + dt*v) / (1 + dt*σ0*|v|/g(v))
        denominator = 1 + dt * p.sigma0 * np.abs(v) / g_v
        self.z = (self.z + dt * v) / denominator
        
        return self.z
    
    def reset_state(self):
        """Reset bristle state to zero"""
        self.z = 0.0


class DahlFriction(FrictionModel):
    """
    Dahl friction model - simpler alternative when Stribeck effects negligible.
    
    dF/dx = σ(1 - F/Fc·sign(v))^α
    
    In steady state, reduces to Coulomb: F = Fc·sign(v)
    """
    
    def __init__(self, params: DahlParameters):
        self.params = params
        self.F_state = 0.0  # Internal friction force state
        
    def force_derivative(self, v: float, F: float) -> float:
        """Calculate dF/dx"""
        p = self.params
        if np.abs(v) < 1e-10:
            return 0.0
        
        ratio = F / p.Fc * np.sign(v)
        ratio = np.clip(ratio, -1, 1)  # Prevent numerical issues
        
        return p.sigma * np.power(1 - ratio, p.alpha) * np.sign(v)
    
    def friction_force(self, v: float, N: float, state: Optional[np.ndarray] = None) -> float:
        """Calculate Dahl friction force"""
        if state is not None:
            return state[0]
        return self.F_state
    
    def friction_coefficient(self, v: float) -> float:
        """Steady-state friction coefficient"""
        return self.params.Fc / 1000.0  # Assume 1000 N reference
    
    def integrate_state(self, v: float, dx: float) -> float:
        """Integrate friction force state"""
        dF_dx = self.force_derivative(v, self.F_state)
        self.F_state += dF_dx * dx
        # Bound to Coulomb force
        self.F_state = np.clip(self.F_state, -self.params.Fc, self.params.Fc)
        return self.F_state


class IwanFriction(FrictionModel):
    """
    Segalman four-parameter Iwan model for microslip hysteresis.

    Uses parallel Jenkins elements with slip force distribution:
    ρ(φ) = R·χ·φ^(χ-1) / Fs^(χ+1)

    Backbone curve:
    F(u) = K_T·u·[1 - (K_T·u/Fs)^(χ+2)/(χ+2)]

    Energy dissipation: W_d ∝ F_amp^(χ+3)
    """

    def __init__(self, params: IwanParameters, n_elements: int = 50):
        self.params = params
        self.n_elements = n_elements

        # Initialize Jenkins elements
        self._setup_elements()

    def _setup_elements(self):
        """Setup parallel Jenkins elements"""
        p = self.params

        # Distribute slip forces according to power law
        self.slip_forces = np.linspace(0.01 * p.F_s, p.F_s, self.n_elements)

        # Calculate weights (density function)
        self.weights = (p.R * p.chi *
                       np.power(self.slip_forces, p.chi - 1) /
                       np.power(p.F_s, p.chi + 1))
        self.weights /= np.sum(self.weights)  # Normalize

        # Element stiffnesses (parallel split of total tangent stiffness)
        self.k_elements = np.full(self.n_elements, p.K_T / self.n_elements)

        # Element states (displacement)
        self.element_states = np.zeros(self.n_elements)

    def integrate_state(self, displacement: float, dt: float = None) -> None:
        """
        Evolve each Jenkins element based on displacement (C4 fix).

        Each Jenkins element is a spring-slider in parallel. The spring
        connects the global displacement to the slider position
        (element_state). When spring force exceeds the slip force,
        the slider moves so the force stays at ±F_slip.

        Args:
            displacement: Current total displacement
            dt: Time step (unused, displacement-driven)
        """
        self._current_displacement = displacement

        for i in range(self.n_elements):
            # Spring force = k * (displacement - slider_position)
            F_trial = self.k_elements[i] * (displacement - self.element_states[i])

            if np.abs(F_trial) <= self.slip_forces[i]:
                # Sticking: slider stays, spring stretches elastically
                pass
            else:
                # Slipping: move slider so force = ±F_slip
                slip_disp = self.slip_forces[i] / self.k_elements[i]
                self.element_states[i] = displacement - slip_disp * np.sign(F_trial)

    def friction_force(self, v: float, N: float, state: Optional[np.ndarray] = None) -> float:
        """
        Calculate Iwan friction force as sum of Jenkins elements (C4 fix).

        Each element contributes F_i = k_i * (u - s_i) weighted by the
        Segalman density function, where u = current displacement and
        s_i = slider position of element i.

        Args:
            v: Velocity (unused for displacement-driven model)
            N: Normal force (unused, force comes from element states)
            state: If provided, displacement used to call integrate_state()
        """
        if state is not None:
            disp = state[0] if isinstance(state, np.ndarray) else float(state)
            self.integrate_state(disp)

        u = getattr(self, '_current_displacement', 0.0)

        total_force = 0.0
        for i in range(self.n_elements):
            # Force = stiffness * (global displacement - slider position)
            F_i = self.k_elements[i] * (u - self.element_states[i])
            # Clamp to slip force (should already be satisfied after integrate_state)
            F_i = np.clip(F_i, -self.slip_forces[i], self.slip_forces[i])
            total_force += F_i * self.weights[i] * self.n_elements

        return total_force

    def friction_coefficient(self, v: float) -> float:
        """Effective friction coefficient"""
        return self.params.F_s / 1000.0

    def backbone_force(self, u: float) -> float:
        """Calculate backbone curve force"""
        p = self.params
        x = p.K_T * np.abs(u) / p.F_s
        if x >= 1:
            return p.F_s * np.sign(u)
        return p.K_T * u * (1 - np.power(x, p.chi + 2) / (p.chi + 2))

    def energy_dissipation(self, F_amp: float) -> float:
        """Calculate energy dissipation per cycle"""
        # W_d ∝ F_amp^β where β = χ + 3
        return np.power(F_amp, self.params.energy_exponent)

    def reset_state(self):
        """Reset all Jenkins element states to zero"""
        self.element_states = np.zeros(self.n_elements)


class BoucWenFriction(FrictionModel):
    """
    Bouc-Wen hysteretic friction model.

    dz/dt = A*v - β|v||z|^(n-1)*z - γ*v|z|^n
    F = α*k*z + c*v

    Captures smooth hysteresis without explicit yield point.
    Widely used for structural damping and joint modeling.

    Parameters:
        alpha: Post-yield stiffness ratio
        k: Pre-yield stiffness (N/m)
        c: Viscous damping (N·s/m)
        A: Hysteresis amplitude
        beta_bw: Hysteresis shape parameter
        gamma_bw: Hysteresis shape parameter
        n_bw: Sharpness of yield (1 = smooth, large = abrupt)
    """

    def __init__(self, alpha: float = 0.1, k: float = 1e5, c: float = 10.0,
                 A: float = 1.0, beta_bw: float = 0.5, gamma_bw: float = 0.5,
                 n_bw: float = 2.0):
        self.alpha = alpha
        self.k = k
        self.c = c
        self.A = A
        self.beta_bw = beta_bw
        self.gamma_bw = gamma_bw
        self.n_bw = n_bw
        self.z = 0.0  # Hysteretic state variable

    def friction_force(self, v: float, N: float, state: Optional[np.ndarray] = None) -> float:
        """
        Calculate Bouc-Wen friction force.

        F = α*k*z + c*v
        """
        if state is not None:
            self.z = state[0]
        return self.alpha * self.k * self.z + self.c * v

    def friction_coefficient(self, v: float) -> float:
        """Effective friction coefficient (approximate)"""
        return self.alpha * self.k * 1e-3 / 1000.0  # Rough estimate

    def integrate_state(self, v: float, dt: float) -> float:
        """
        Integrate hysteretic state z using forward Euler.

        dz/dt = A*v - β|v||z|^(n-1)*z - γ*v|z|^n
        """
        z_abs_n1 = np.power(np.abs(self.z), self.n_bw - 1) if np.abs(self.z) > 1e-15 else 0.0
        z_abs_n = np.power(np.abs(self.z), self.n_bw) if np.abs(self.z) > 1e-15 else 0.0

        dz_dt = self.A * v - self.beta_bw * np.abs(v) * z_abs_n1 * self.z - self.gamma_bw * v * z_abs_n

        self.z += dz_dt * dt
        return self.z

    def reset_state(self):
        """Reset hysteretic state to zero"""
        self.z = 0.0


class CoulombViscousFriction(FrictionModel):
    """
    Combined Coulomb + Viscous friction model.

    F = μ·N·sign(v) + c_visc·v

    Simple and robust for applications where Stribeck effects are negligible
    but viscous drag from lubricant is significant.

    Parameters:
        mu: Coulomb friction coefficient
        c_visc: Viscous drag coefficient (N·s/m)
        v_reg: Regularization velocity for smooth sign function (m/s)
    """

    def __init__(self, mu: float = 0.12, c_visc: float = 10.0, v_reg: float = 1e-4):
        self.mu = mu
        self.c_visc = c_visc
        self.v_reg = v_reg

    def friction_force(self, v: float, N: float, state: Optional[np.ndarray] = None) -> float:
        """
        Calculate combined Coulomb + viscous friction force.

        F = μ·N·tanh(v/v_reg) + c_visc·v
        """
        F_coulomb = self.mu * N * np.tanh(v / self.v_reg)
        F_viscous = self.c_visc * v
        return F_coulomb + F_viscous

    def friction_coefficient(self, v: float) -> float:
        """Effective friction coefficient (Coulomb part only)"""
        return self.mu


# =============================================================================
# FRICTION EVOLUTION MODELS
# =============================================================================

class FrictionEvolutionModel:
    """
    Model for friction coefficient evolution over cycles.
    
    Based on Hintikka et al. (2020) three-phase model:
    
    Phase 1 (N < N1): μ rises from μ_initial toward μ_peak (running-in)
    Phase 2 (N1 < N < N_critical): μ decays to μ_steady (stabilization)
    Phase 3 (N > N_critical): μ changes slowly (degradation)
    
    Complete model:
    μ(N) = μ0 + (μ_peak - μ0)·(1 - e^(-N/N1))·e^(-N/N2) + 
           (μ_ss - μ0)·(1 - e^(-N/N3))
    """
    
    def __init__(self, params: FrictionEvolutionParameters):
        self.params = params
        
    def friction_coefficient(self, N: np.ndarray) -> np.ndarray:
        """
        Calculate friction coefficient at cycle count N.
        
        Args:
            N: Cycle count (scalar or array)
            
        Returns:
            Friction coefficient μ(N)
        """
        N = np.atleast_1d(N)
        p = self.params
        
        # Running-in peak term
        peak_term = ((p.mu_peak - p.mu_initial) * 
                     (1 - np.exp(-N / p.N1)) * 
                     np.exp(-N / p.N2))
        
        # Stabilization term
        steady_term = (p.mu_steady - p.mu_initial) * (1 - np.exp(-N / p.N3))
        
        # Degradation term (for N > N_critical)
        degrade_mask = N > p.N_critical
        degrade_term = np.zeros_like(N, dtype=float)
        if np.any(degrade_mask):
            degrade_term[degrade_mask] = (
                p.beta_degrade * np.log(N[degrade_mask] / p.N_critical)
            )
        
        mu = p.mu_initial + peak_term + steady_term + degrade_term
        
        return np.clip(mu, 0.02, 0.5)  # Physical bounds
    
    def friction_rate(self, N: np.ndarray) -> np.ndarray:
        """
        Calculate dμ/dN - rate of friction change.
        """
        N = np.atleast_1d(N)
        p = self.params
        
        # Numerical derivative (can be replaced with analytical)
        dN = 1.0
        mu = self.friction_coefficient(N)
        mu_next = self.friction_coefficient(N + dN)
        
        return (mu_next - mu) / dN


class CoupledFrictionPreloadModel:
    """
    Coupled model for friction-preload evolution.
    
    Captures bidirectional coupling:
    - Decreasing preload reduces contact pressure → affects friction
    - Friction changes affect loosening rate → affects preload
    
    Based on Jiang two-stage model with friction evolution.
    """
    
    def __init__(self, 
                 friction_params: FrictionEvolutionParameters,
                 initial_preload: float,
                 k_bolt: float,
                 k_member: float):
        self.friction_model = FrictionEvolutionModel(friction_params)
        self.F0 = initial_preload
        self.k_bolt = k_bolt
        self.k_member = k_member
        
        # Coupling parameters
        self.pressure_exponent = -0.1  # μ ~ p^n, n typically -0.1 to +0.2
        self.preload_feedback = 0.1    # How much friction change affects preload rate
        
    def coupled_evolution(self, N_max: int, dt_cycles: float = 1.0) -> Dict[str, np.ndarray]:
        """
        Simulate coupled friction-preload evolution.
        
        Returns:
            Dictionary with N, friction, preload, contact_pressure
        """
        n_steps = int(N_max / dt_cycles)
        
        # Arrays for results
        N = np.zeros(n_steps)
        mu = np.zeros(n_steps)
        F = np.zeros(n_steps)
        p_contact = np.zeros(n_steps)
        
        # Initial conditions
        N[0] = 0
        F[0] = self.F0
        mu[0] = self.friction_model.params.mu_initial
        p_contact[0] = F[0] / 100.0  # Simplified contact pressure (MPa)
        
        # Time stepping
        for i in range(1, n_steps):
            N[i] = N[i-1] + dt_cycles
            
            # Base friction from evolution model
            mu_base = self.friction_model.friction_coefficient(np.array([N[i]]))[0]
            
            # Pressure correction
            p_ratio = p_contact[i-1] / p_contact[0]
            mu[i] = mu_base * np.power(p_ratio, self.pressure_exponent)
            
            # Preload decay (Jiang-like with friction feedback)
            if N[i] < 500:  # Stage I
                dF = -0.001 * F[i-1] * (1 + self.preload_feedback * (mu[i] - mu[0]) / mu[0])
            else:  # Stage II
                dF = -5.0 * (1 - self.preload_feedback * (mu[i] - mu[0]) / mu[0])
            
            F[i] = max(0, F[i-1] + dF * dt_cycles)
            
            # Update contact pressure
            p_contact[i] = F[i] / 100.0
            
        return {
            'cycles': N,
            'friction': mu,
            'preload': F,
            'contact_pressure': p_contact
        }


# =============================================================================
# WEAR MODELS
# =============================================================================

class WearModel:
    """
    Wear models for bolted joint interfaces.
    
    Classical Archard: V = K·W·L/H
    Energy-based (Fouvry): W_d = α·E_d where E_d = ∮F·dx
    """
    
    def __init__(self, params: WearParameters):
        self.params = params
        self.accumulated_wear = 0.0
        self.accumulated_energy = 0.0
        
    def archard_wear_depth(self, contact_pressure: float,
                           sliding_distance: float,
                           accumulate: bool = True) -> float:
        """
        Calculate wear depth using Archard equation.

        h = K·p·s/H

        Args:
            contact_pressure: Normal contact pressure (MPa)
            sliding_distance: Total sliding distance (mm)
            accumulate: If True, add to accumulated_wear (default).
                        Set False for read-only computation (M11 fix).

        Returns:
            Wear depth (mm)
        """
        p = self.params
        h = p.K_archard * contact_pressure * sliding_distance / p.hardness
        if accumulate:
            self.accumulated_wear += h
        return h

    def fouvry_energy_wear(self, friction_force: float,
                          displacement: float,
                          accumulate: bool = True) -> float:
        """
        Energy-based wear using Fouvry method.

        W = α·E_d where E_d is dissipated energy per full cycle.

        For a full rectangular hysteresis loop:
        E_d = 4·μ·N·δ (four quarter-cycles)

        Args:
            friction_force: Friction force amplitude (N)
            displacement: Displacement amplitude (mm)
            accumulate: If True, add to accumulated_energy (default).
                        Set False for read-only computation (M11 fix).

        Returns:
            Wear volume (mm³)
        """
        # Full-cycle dissipated energy (M12 fix: 4×F×δ, not quarter-cycle)
        E_d = 4.0 * friction_force * displacement
        if accumulate:
            self.accumulated_energy += E_d

        # Wear volume
        W = self.params.alpha_fouvry * E_d
        return W

    def wear_rate_per_cycle(self, contact_pressure: float,
                            displacement_amplitude: float,
                            friction_coefficient: float,
                            accumulate: bool = True) -> float:
        """
        Calculate wear rate per loading cycle.

        For fretting, typical values:
            Gross slip: K ~ 10⁻⁴ to 10⁻⁶
            Partial slip: K ~ 10⁻⁷ to 10⁻⁸

        Args:
            accumulate: If True, updates accumulated_wear. Set False for
                        read-only computation to avoid double-counting (M11).
        """
        # Sliding distance per cycle ≈ 4 × displacement amplitude
        s_cycle = 4 * displacement_amplitude

        # Archard wear per cycle
        h_cycle = self.archard_wear_depth(contact_pressure, s_cycle, accumulate=accumulate)

        return h_cycle


class WearEvolutionModel:
    """
    Nonlinear wear evolution model affecting preload over cycles.

    Wear → Contact geometry change → Stiffness change → Preload loss

    Implements:
    - Generalized Archard: dh/dN = K * p^α * v^β (nonlinear exponents)
    - Cumulative wear via power-law integration (not linear h = rate * N)
    - Stiffness degradation with compliance feedback

    References:
    - Goryacheva (1998) — Generalized Archard with nonlinear exponents
    - Argatov & Chai (2022) — Fractional wear accumulation
    - Pai & Hess (2002) — Wear-loosening positive feedback
    """

    def __init__(self,
                 wear_params: WearParameters,
                 initial_stiffness: float,
                 wear_to_stiffness_ratio: float = 0.1,
                 pressure_exponent: float = 1.2,
                 velocity_exponent: float = 0.8):
        self.wear_model = WearModel(wear_params)
        self.k0 = initial_stiffness
        self.wear_stiffness_ratio = wear_to_stiffness_ratio
        self.alpha = pressure_exponent   # Generalized Archard pressure exponent
        self.beta = velocity_exponent    # Generalized Archard velocity exponent

    def _cumulative_wear(self, N: np.ndarray, h_rate_base: float) -> np.ndarray:
        """
        Nonlinear cumulative wear depth.

        Instead of linear h(N) = h_rate * N, uses power-law accumulation:
        h(N) = h_rate * N^(1 + β/2) / (1 + β/2)

        This captures:
        - Running-in acceleration (surface roughening)
        - Self-limiting behavior at very high N (surface polishing)
        """
        N = np.atleast_1d(N).astype(float)

        # Running-in acceleration factor (first ~100 cycles wear faster)
        running_in = 1.0 + 2.0 * np.exp(-N / 50.0)

        # Power-law accumulation (slightly super-linear for fretting wear)
        accumulation_exp = 1.0 + self.beta / 4.0  # Typically ~1.2
        h_cumulative = h_rate_base * running_in * (N ** accumulation_exp) / (N.max() ** (accumulation_exp - 1) + 1)

        # Normalize to match physical wear rates
        # At N=1000 steady-state cycles, h should ≈ h_rate * 1000
        scale = 1000.0 ** (1 - accumulation_exp + 1) / (1000.0 ** accumulation_exp / (1000.0 ** (accumulation_exp - 1) + 1))
        h_cumulative *= min(scale, 5.0)  # Safety cap

        return h_cumulative

    def stiffness_evolution(self, N: np.ndarray,
                           contact_pressure: float,
                           displacement_amplitude: float,
                           friction_coefficient: float) -> np.ndarray:
        """
        Calculate stiffness evolution due to nonlinear wear.

        k(N) = k0 / (1 + γ * h(N))

        Uses hyperbolic degradation instead of linear (1 - γ*h),
        which naturally limits stiffness loss and provides realistic
        compliance increase at high wear depths.
        """
        N = np.atleast_1d(N)

        # Base wear rate per cycle - read-only to avoid double-counting (M11 fix)
        h_rate = self.wear_model.wear_rate_per_cycle(
            contact_pressure, displacement_amplitude, friction_coefficient,
            accumulate=False
        )

        # Nonlinear cumulative wear
        h_cumulative = self._cumulative_wear(N, h_rate)

        # Hyperbolic stiffness degradation (physically bounded)
        # k = k0 / (1 + γ*h) instead of k = k0*(1 - γ*h) which goes negative
        k = self.k0 / (1.0 + self.wear_stiffness_ratio * h_cumulative / 0.01)

        return np.maximum(k, 0.3 * self.k0)  # Limit reduction to 70%

    def preload_loss_from_wear(self, N: np.ndarray,
                               initial_preload: float,
                               contact_pressure: float,
                               displacement_amplitude: float,
                               friction_coefficient: float) -> np.ndarray:
        """
        Calculate preload loss due to wear-induced compliance increase.

        Nonlinear: as wear increases, compliance grows, which reduces
        clamping force, which allows more slip, accelerating wear.
        """
        k = self.stiffness_evolution(
            N, contact_pressure, displacement_amplitude, friction_coefficient
        )

        # Preload scales with stiffness ratio
        F = initial_preload * k / self.k0

        return F


# =============================================================================
# STRIBECK CURVE MODEL
# =============================================================================

class StribeckModel:
    """
    Stribeck curve model for lubrication regime transitions.
    
    μ = f(Hersey number) where He = ηN/P
    
    Three regimes:
    - Boundary (λ < 1): μ = 0.1-0.3
    - Mixed (1 < λ < 3): μ = 0.01-0.1
    - Hydrodynamic (λ > 3): μ = 0.001-0.01
    """
    
    def __init__(self,
                 mu_boundary: float = 0.15,
                 mu_mixed: float = 0.05,
                 mu_hydro: float = 0.005,
                 lambda_1: float = 1.0,
                 lambda_2: float = 3.0):
        self.mu_boundary = mu_boundary
        self.mu_mixed = mu_mixed
        self.mu_hydro = mu_hydro
        self.lambda_1 = lambda_1
        self.lambda_2 = lambda_2
        
    def friction_coefficient(self, lambda_ratio: np.ndarray) -> np.ndarray:
        """
        Calculate friction coefficient from specific film thickness λ.
        
        λ = h_c / √(Rq1² + Rq2²)
        """
        lam = np.atleast_1d(lambda_ratio)
        mu = np.zeros_like(lam)
        
        # Boundary regime
        mask_boundary = lam < self.lambda_1
        mu[mask_boundary] = self.mu_boundary
        
        # Mixed regime (log interpolation)
        mask_mixed = (lam >= self.lambda_1) & (lam < self.lambda_2)
        if np.any(mask_mixed):
            log_interp = (np.log(lam[mask_mixed]) - np.log(self.lambda_1)) / \
                        (np.log(self.lambda_2) - np.log(self.lambda_1))
            mu[mask_mixed] = self.mu_boundary * np.exp(
                log_interp * np.log(self.mu_hydro / self.mu_boundary)
            )
        
        # Hydrodynamic regime
        mask_hydro = lam >= self.lambda_2
        mu[mask_hydro] = self.mu_hydro
        
        return mu
    
    def get_regime(self, lambda_ratio: float) -> LubricationRegime:
        """Determine lubrication regime"""
        if lambda_ratio < self.lambda_1:
            return LubricationRegime.BOUNDARY
        elif lambda_ratio < self.lambda_2:
            return LubricationRegime.MIXED
        else:
            return LubricationRegime.HYDRODYNAMIC


# =============================================================================
# FACTORY FUNCTIONS
# =============================================================================

def create_friction_model(model_type: FrictionModelType,
                         **kwargs) -> FrictionModel:
    """Factory function to create friction models"""

    if model_type == FrictionModelType.COULOMB:
        params = CoulombParameters(**kwargs)
        return CoulombFriction(params)
    elif model_type == FrictionModelType.COULOMB_VISCOUS:
        return CoulombViscousFriction(**kwargs)
    elif model_type == FrictionModelType.LUGRE:
        params = LuGreParameters(**kwargs)
        return LuGreFriction(params)
    elif model_type == FrictionModelType.DAHL:
        params = DahlParameters(**kwargs)
        return DahlFriction(params)
    elif model_type == FrictionModelType.IWAN:
        params = IwanParameters(**kwargs)
        return IwanFriction(params)
    elif model_type == FrictionModelType.BOUC_WEN:
        return BoucWenFriction(**kwargs)
    else:
        raise ValueError(f"Unknown friction model type: {model_type}")


def get_standard_friction_parameters(surface_condition: str = "zinc_phosphate") -> Dict:
    """
    Get standard friction parameters for common surface conditions.
    
    Returns dictionary suitable for LuGre model initialization.
    """
    
    surface_data = {
        "bare_steel": {
            "mu_static": 0.20,
            "mu_kinetic": 0.15,
            "Fs": 200.0,
            "Fc": 150.0
        },
        "zinc_phosphate": {
            "mu_static": 0.15,
            "mu_kinetic": 0.12,
            "Fs": 150.0,
            "Fc": 120.0
        },
        "mos2": {
            "mu_static": 0.08,
            "mu_kinetic": 0.06,
            "Fs": 80.0,
            "Fc": 60.0
        },
        "ptfe": {
            "mu_static": 0.06,
            "mu_kinetic": 0.04,
            "Fs": 60.0,
            "Fc": 40.0
        }
    }
    
    if surface_condition not in surface_data:
        surface_condition = "zinc_phosphate"
        
    return surface_data[surface_condition]


def get_standard_wear_parameters(wear_regime: WearRegime = WearRegime.GROSS_SLIP) -> WearParameters:
    """Get standard wear parameters for different wear regimes"""
    
    if wear_regime == WearRegime.PARTIAL_SLIP:
        return WearParameters(
            K_archard=1e-7,
            k_dimensional=1e-10,
            hardness=3000.0,
            alpha_fouvry=1e-8
        )
    else:  # Gross slip
        return WearParameters(
            K_archard=1e-5,
            k_dimensional=1e-8,
            hardness=3000.0,
            alpha_fouvry=3e-8
        )
