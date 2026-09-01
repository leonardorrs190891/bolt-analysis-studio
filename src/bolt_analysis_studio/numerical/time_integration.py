"""
Time Integration Methods for Dynamic Analysis

Bolt Analysis Studio v4.0
Prof. Leonardo Rosa Ribeiro da Silva, PhD

This module implements numerical time integration schemes for solving
the equation of motion: M·ẍ + C·ẋ + K·x = F(t)

Methods implemented:
- Newmark-β (average acceleration, linear acceleration, constant acceleration)
- HHT-α (Hilber-Hughes-Taylor) with numerical damping
- Central Difference (explicit)
- Modal Superposition for linear systems
- Runge-Kutta 4th order for state-space systems

References:
- Newmark, N.M. (1959). "A Method of Computation for Structural Dynamics"
- Hughes, T.J.R. (1987). "The Finite Element Method"
- VDI 2230 Part 1 (2015). "Systematic Calculation of Highly Stressed Bolted Joints"
"""

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Callable, Optional, Tuple, List, Dict, Any
import numpy as np
from scipy import linalg
from scipy.sparse import csr_matrix, issparse
from scipy.sparse.linalg import spsolve, eigsh
import warnings


class IntegratorType(Enum):
    """Available time integration methods."""
    NEWMARK_BETA = auto()           # Implicit, unconditionally stable
    HHT_ALPHA = auto()              # Implicit with numerical damping
    CENTRAL_DIFFERENCE = auto()      # Explicit, conditionally stable
    MODAL_SUPERPOSITION = auto()     # For linear systems
    RUNGE_KUTTA_4 = auto()          # 4th order explicit
    ADAPTIVE_RK45 = auto()          # Adaptive Dormand-Prince RK4(5)


class ConvergenceType(Enum):
    """Convergence criteria for nonlinear iterations."""
    FORCE = auto()          # ||R|| < ε_F
    DISPLACEMENT = auto()   # ||Δx|| < ε_x
    ENERGY = auto()         # ||Δxᵀ·R|| < ε_E
    COMBINED = auto()       # All criteria must be satisfied


@dataclass
class TimeParams:
    """Time integration parameters."""
    t_start: float = 0.0            # Start time (s)
    t_end: float = 1.0              # End time (s)
    dt: float = 0.001               # Time step (s)
    output_interval: int = 1        # Output every n steps
    
    @property
    def n_steps(self) -> int:
        """Total number of time steps."""
        return int(np.ceil((self.t_end - self.t_start) / self.dt))
    
    @property
    def time_vector(self) -> np.ndarray:
        """Generate time vector."""
        return np.linspace(self.t_start, self.t_end, self.n_steps + 1)


@dataclass
class NewmarkParams:
    """Newmark-β method parameters."""
    beta: float = 0.25      # Newmark β (0.25 = average acceleration)
    gamma: float = 0.5      # Newmark γ (0.5 = no numerical damping)
    
    def __post_init__(self):
        """Validate parameters."""
        # Unconditional stability: γ ≥ 0.5, β ≥ 0.25(γ + 0.5)²
        if self.gamma < 0.5:
            warnings.warn("Newmark γ < 0.5 may cause instability")
        min_beta = 0.25 * (self.gamma + 0.5) ** 2
        if self.beta < min_beta:
            warnings.warn(f"Newmark β < {min_beta:.4f} may cause instability")
    
    @classmethod
    def average_acceleration(cls) -> 'NewmarkParams':
        """Average acceleration method (unconditionally stable)."""
        return cls(beta=0.25, gamma=0.5)
    
    @classmethod
    def linear_acceleration(cls) -> 'NewmarkParams':
        """Linear acceleration method (conditionally stable)."""
        return cls(beta=1/6, gamma=0.5)
    
    @classmethod
    def constant_acceleration(cls) -> 'NewmarkParams':
        """Constant acceleration method."""
        return cls(beta=0.5, gamma=1.0)


@dataclass
class HHTParams:
    """HHT-α method parameters."""
    alpha: float = -0.05    # HHT α ∈ [-1/3, 0], higher damping for more negative
    
    def __post_init__(self):
        """Validate and compute derived parameters."""
        if not -1/3 <= self.alpha <= 0:
            raise ValueError("HHT α must be in range [-1/3, 0]")
    
    @property
    def beta(self) -> float:
        """Derived Newmark β."""
        return (1 - self.alpha) ** 2 / 4
    
    @property
    def gamma(self) -> float:
        """Derived Newmark γ."""
        return (1 - 2 * self.alpha) / 2
    
    @classmethod
    def low_damping(cls) -> 'HHTParams':
        """Low numerical damping (α = -0.05)."""
        return cls(alpha=-0.05)
    
    @classmethod
    def medium_damping(cls) -> 'HHTParams':
        """Medium numerical damping (α = -0.1)."""
        return cls(alpha=-0.10)
    
    @classmethod
    def high_damping(cls) -> 'HHTParams':
        """High numerical damping for stiff problems (α = -0.3)."""
        return cls(alpha=-0.30)


@dataclass
class NonlinearParams:
    """Nonlinear solver parameters."""
    max_iterations: int = 50            # Maximum Newton-Raphson iterations
    tol_force: float = 1e-6             # Force convergence tolerance
    tol_disp: float = 1e-6              # Displacement convergence tolerance
    tol_energy: float = 1e-9            # Energy convergence tolerance
    convergence_type: ConvergenceType = ConvergenceType.COMBINED
    line_search: bool = True            # Enable line search
    line_search_max_iter: int = 10      # Max line search iterations
    line_search_factor: float = 0.5     # Line search reduction factor


@dataclass
class IntegrationResult:
    """Results from time integration."""
    time: np.ndarray                    # Time vector [n_steps+1]
    displacement: np.ndarray            # Displacement history [n_steps+1, n_dof]
    velocity: np.ndarray                # Velocity history [n_steps+1, n_dof]
    acceleration: np.ndarray            # Acceleration history [n_steps+1, n_dof]
    force: Optional[np.ndarray] = None  # Applied force history [n_steps+1, n_dof]
    internal_force: Optional[np.ndarray] = None  # Internal force history
    energy_kinetic: Optional[np.ndarray] = None   # Kinetic energy
    energy_potential: Optional[np.ndarray] = None # Potential energy
    energy_dissipated: Optional[np.ndarray] = None # Dissipated energy
    iterations: Optional[List[int]] = None  # Iterations per step (nonlinear)
    converged: bool = True              # Overall convergence status
    
    @property
    def n_steps(self) -> int:
        """Number of time steps."""
        return len(self.time) - 1
    
    @property
    def n_dof(self) -> int:
        """Number of degrees of freedom."""
        return self.displacement.shape[1] if self.displacement.ndim > 1 else 1
    
    def get_max_displacement(self) -> np.ndarray:
        """Get maximum displacement for each DOF."""
        return np.max(np.abs(self.displacement), axis=0)
    
    def get_max_velocity(self) -> np.ndarray:
        """Get maximum velocity for each DOF."""
        return np.max(np.abs(self.velocity), axis=0)
    
    def get_max_acceleration(self) -> np.ndarray:
        """Get maximum acceleration for each DOF."""
        return np.max(np.abs(self.acceleration), axis=0)
    
    def compute_energies(self, M: np.ndarray, K: np.ndarray, C: np.ndarray) -> None:
        """Compute energy history if not already computed."""
        n_steps = len(self.time)
        self.energy_kinetic = np.zeros(n_steps)
        self.energy_potential = np.zeros(n_steps)
        self.energy_dissipated = np.zeros(n_steps)
        
        for i in range(n_steps):
            v = self.velocity[i]
            u = self.displacement[i]
            self.energy_kinetic[i] = 0.5 * v @ M @ v
            self.energy_potential[i] = 0.5 * u @ K @ u
        
        # Cumulative dissipated energy
        dt = self.time[1] - self.time[0] if len(self.time) > 1 else 0.001
        for i in range(1, n_steps):
            v_avg = 0.5 * (self.velocity[i] + self.velocity[i-1])
            damping_force = C @ v_avg
            self.energy_dissipated[i] = (
                self.energy_dissipated[i-1] + 
                dt * np.dot(damping_force, v_avg)
            )


def _compute_system_stiffness_from_matrix(K: np.ndarray) -> float:
    """
    Compute system stiffness from stiffness matrix.

    For a series chain (tridiagonal K), extracts individual spring
    stiffnesses and computes series combination: k_sys = 1 / sum(1/k_i).

    Extracts:
    - Coupling springs from off-diagonal elements: k_i = |K[i, i+1]|
    - Ground springs from diagonal excess: k_ground = K[i,i] - sum|K[i,j!=i]|

    Falls back to harmonic mean of positive diagonal values for
    non-tridiagonal matrices.

    Args:
        K: Stiffness matrix

    Returns:
        Scalar system stiffness value
    """
    n = K.shape[0]
    if n == 1:
        return float(K[0, 0])

    # Extract spring stiffnesses from off-diagonal elements (tridiagonal)
    coupling_stiffnesses = []
    for j in range(n - 1):
        k_j = abs(K[j, j + 1])
        if k_j > 1e-20:
            coupling_stiffnesses.append(k_j)

    if coupling_stiffnesses:
        stiffnesses = list(coupling_stiffnesses)

        # Also extract ground springs (diagonal excess over coupling sum)
        for i in range(n):
            off_diag_sum = sum(abs(K[i, j]) for j in range(n) if j != i)
            k_ground = K[i, i] - off_diag_sum
            if k_ground > 1e-20:
                stiffnesses.append(k_ground)

        # Series combination: k_sys = 1 / sum(1/k_i)
        return 1.0 / sum(1.0 / k for k in stiffnesses)

    # Fallback: harmonic mean of positive diagonal values
    k_diag = np.diag(K)
    k_pos = k_diag[k_diag > 1e-20]
    if len(k_pos) > 0:
        return float(len(k_pos) / np.sum(1.0 / k_pos))
    return 1.0


class NewmarkIntegrator:
    """
    Newmark-β time integration method.

    Solves: M·ẍ + C·ẋ + K·x = F(t)

    The method is implicit and can be unconditionally stable for
    appropriate parameter choices (β=0.25, γ=0.5).
    """
    
    def __init__(
        self,
        M: np.ndarray,
        C: np.ndarray,
        K: np.ndarray,
        params: Optional[NewmarkParams] = None
    ):
        """
        Initialize Newmark integrator.
        
        Args:
            M: Mass matrix [n_dof × n_dof]
            C: Damping matrix [n_dof × n_dof]
            K: Stiffness matrix [n_dof × n_dof]
            params: Newmark parameters (default: average acceleration)
        """
        self.M = np.asarray(M)
        self.C = np.asarray(C)
        self.K = np.asarray(K)
        self.params = params or NewmarkParams.average_acceleration()
        self.n_dof = M.shape[0]
        
        # Precompute inverse mass if sparse
        self._M_is_diagonal = np.allclose(M, np.diag(np.diag(M)))
        if self._M_is_diagonal:
            self._M_diag_inv = 1.0 / np.diag(M)

    def validate_system(self, dt: float) -> Tuple[bool, str]:
        """
        Validate system matrices and time step.

        Args:
            dt: Proposed time step

        Returns:
            (is_valid, message) tuple
        """
        # Check for inf/nan in matrices
        if np.any(np.isinf(self.M)) or np.any(np.isnan(self.M)):
            return False, "Mass matrix contains inf or NaN values"
        if np.any(np.isinf(self.K)) or np.any(np.isnan(self.K)):
            return False, "Stiffness matrix contains inf or NaN values"
        if np.any(np.isinf(self.C)) or np.any(np.isnan(self.C)):
            return False, "Damping matrix contains inf or NaN values"

        # Estimate natural frequencies
        try:
            eigenvalues = np.linalg.eigvals(np.linalg.inv(self.M) @ self.K)
            natural_freqs = np.sqrt(np.abs(eigenvalues)) / (2 * np.pi)
            max_freq = np.max(natural_freqs)

            # Recommended time step: T_min / 10
            dt_recommended = 1.0 / (10 * max_freq)

            if dt > dt_recommended:
                msg = (
                    f"Time step {dt:.3e} s may be too large for stability.\n"
                    f"System has natural frequencies up to {max_freq:.1f} Hz.\n"
                    f"Recommended time step: {dt_recommended:.3e} s (period/10).\n"
                    f"Current time step is {dt/dt_recommended:.1f}x larger than recommended."
                )
                return False, msg

        except Exception as e:
            warnings.warn(f"Could not estimate natural frequencies: {e}")

        return True, "System validation passed"

    def _compute_effective_stiffness(self, dt: float) -> np.ndarray:
        """Compute effective stiffness matrix."""
        beta = self.params.beta
        gamma = self.params.gamma
        
        a0 = 1.0 / (beta * dt**2)
        a1 = gamma / (beta * dt)
        
        K_eff = self.K + a1 * self.C + a0 * self.M
        return K_eff
    
    def _compute_effective_force(
        self,
        F_next: np.ndarray,
        u: np.ndarray,
        v: np.ndarray,
        a: np.ndarray,
        dt: float
    ) -> np.ndarray:
        """Compute effective force vector."""
        beta = self.params.beta
        gamma = self.params.gamma
        
        a0 = 1.0 / (beta * dt**2)
        a1 = gamma / (beta * dt)
        a2 = 1.0 / (beta * dt)
        a3 = 1.0 / (2 * beta) - 1.0
        a4 = gamma / beta - 1.0
        a5 = dt * (gamma / (2 * beta) - 1.0)
        
        F_eff = (
            F_next + 
            self.M @ (a0 * u + a2 * v + a3 * a) +
            self.C @ (a1 * u + a4 * v + a5 * a)
        )
        return F_eff
    
    def _update_state(
        self,
        u_new: np.ndarray,
        u: np.ndarray,
        v: np.ndarray,
        a: np.ndarray,
        dt: float
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Update velocity and acceleration from new displacement."""
        beta = self.params.beta
        gamma = self.params.gamma
        
        a0 = 1.0 / (beta * dt**2)
        a2 = 1.0 / (beta * dt)
        a3 = 1.0 / (2 * beta) - 1.0
        
        a_new = a0 * (u_new - u) - a2 * v - a3 * a
        v_new = v + dt * ((1 - gamma) * a + gamma * a_new)
        
        return v_new, a_new
    
    def integrate(
        self,
        time_params: TimeParams,
        F_func: Callable[[float], np.ndarray],
        u0: Optional[np.ndarray] = None,
        v0: Optional[np.ndarray] = None
    ) -> IntegrationResult:
        """
        Perform time integration.

        Args:
            time_params: Time integration parameters
            F_func: Force function F(t) -> np.ndarray[n_dof]
            u0: Initial displacement (default: zeros)
            v0: Initial velocity (default: zeros)

        Returns:
            IntegrationResult with displacement, velocity, acceleration histories
        """
        dt = time_params.dt
        t = time_params.time_vector
        n_steps = len(t)

        # Validate system
        is_valid, msg = self.validate_system(dt)
        if not is_valid:
            raise ValueError(f"System validation failed:\n{msg}")
        
        # Initialize storage
        U = np.zeros((n_steps, self.n_dof))
        V = np.zeros((n_steps, self.n_dof))
        A = np.zeros((n_steps, self.n_dof))
        F = np.zeros((n_steps, self.n_dof))
        
        # Initial conditions
        U[0] = u0 if u0 is not None else np.zeros(self.n_dof)
        V[0] = v0 if v0 is not None else np.zeros(self.n_dof)
        F[0] = F_func(t[0])
        
        # Initial acceleration: M·a = F - C·v - K·u
        rhs = F[0] - self.C @ V[0] - self.K @ U[0]
        if self._M_is_diagonal:
            A[0] = self._M_diag_inv * rhs
        else:
            A[0] = linalg.solve(self.M, rhs, assume_a='pos')
        
        # Effective stiffness (constant for linear problems)
        K_eff = self._compute_effective_stiffness(dt)
        K_eff_lu = linalg.lu_factor(K_eff)
        
        # Time stepping
        for i in range(n_steps - 1):
            # Force at next time step
            F[i+1] = F_func(t[i+1])

            # Effective force
            F_eff = self._compute_effective_force(F[i+1], U[i], V[i], A[i], dt)

            # Check for overflow in effective force
            if np.any(np.isinf(F_eff)) or np.any(np.isnan(F_eff)):
                eigenvalues = np.linalg.eigvals(np.linalg.inv(self.M) @ self.K)
                natural_freqs = np.sqrt(np.abs(eigenvalues)) / (2 * np.pi)
                max_freq = np.max(natural_freqs)
                dt_rec = 1.0 / (10 * max_freq)
                raise ValueError(
                    f"Numerical overflow at time step {i} (t = {t[i]:.3e} s).\n"
                    f"Time step dt = {dt:.3e} s is too large.\n"
                    f"System natural frequency: {max_freq:.1f} Hz\n"
                    f"Recommended time step: {dt_rec:.3e} s\n"
                    f"Try reducing dt by a factor of {dt/dt_rec:.1f}"
                )

            # Solve for new displacement
            U[i+1] = linalg.lu_solve(K_eff_lu, F_eff)

            # Check for overflow in solution
            if np.any(np.isinf(U[i+1])) or np.any(np.isnan(U[i+1])):
                raise ValueError(
                    f"Solution contains inf/NaN at time step {i} (t = {t[i]:.3e} s).\n"
                    f"Try reducing time step or checking initial conditions."
                )

            # Update velocity and acceleration
            V[i+1], A[i+1] = self._update_state(U[i+1], U[i], V[i], A[i], dt)
        
        return IntegrationResult(
            time=t,
            displacement=U,
            velocity=V,
            acceleration=A,
            force=F
        )

    def solve_with_contacts(
        self,
        time_params: TimeParams,
        assembler: Any,  # CompleteMSDMatrixAssembler
        state_manager: Any,  # StateManager
        contacts: List[Any],  # List[Contact]
        preload_tracker: Any,  # PreloadTracker
        F_external: Callable[[float], np.ndarray],
        reassemble_interval: int = 10,
        preload_change_threshold: float = 0.05
    ) -> IntegrationResult:
        """
        Perform time integration with contact state updates.

        This method integrates with the contact system to handle:
        - Nonlinear tribological forces
        - Contact state evolution
        - Preload tracking
        - Matrix reassembly when preload changes significantly

        Args:
            time_params: Time integration parameters
            assembler: Matrix assembler with contacts
            state_manager: State manager for system state
            contacts: List of Contact objects
            preload_tracker: Preload tracking object
            F_external: External force function F(t)
            reassemble_interval: Reassemble K_eff every N steps (default: 10)
            preload_change_threshold: Reassemble if preload changes by this
                fraction since last assembly (default: 0.05 = 5%)

        Returns:
            IntegrationResult with full history
        """
        dt = time_params.dt
        t = time_params.time_vector
        n_steps = len(t)
        n_dof = self.n_dof

        # Initialize storage
        U = np.zeros((n_steps, n_dof))
        V = np.zeros((n_steps, n_dof))
        A = np.zeros((n_steps, n_dof))
        F = np.zeros((n_steps, n_dof))
        preload_history = np.zeros(n_steps)

        # Initial conditions
        U[0] = state_manager.state.displacement
        V[0] = state_manager.state.velocity
        F[0] = F_external(t[0])
        preload_history[0] = preload_tracker.current_preload

        # System stiffness for preload loss (series combination, not trace)
        k_sys = _compute_system_stiffness_from_matrix(self.K)

        # Initial acceleration
        F_trib = assembler.compute_tribological_forces(U[0], V[0])
        rhs = F[0] + F_trib - self.C @ V[0] - self.K @ U[0]
        A[0] = linalg.solve(self.M, rhs, assume_a='pos')

        # Effective stiffness
        K_eff = self._compute_effective_stiffness(dt)
        K_eff_lu = linalg.lu_factor(K_eff)
        preload_at_last_assembly = preload_tracker.current_preload

        # Time stepping with contact updates
        for i in range(n_steps - 1):
            # External forces
            F[i+1] = F_external(t[i+1])

            # Tribological forces (friction, wear effects)
            F_trib = assembler.compute_tribological_forces(U[i], V[i])

            # Total force
            F_total = F[i+1] + F_trib

            # Effective force
            F_eff = self._compute_effective_force(F_total, U[i], V[i], A[i], dt)

            # Solve for new displacement
            U[i+1] = linalg.lu_solve(K_eff_lu, F_eff)

            # Update velocity and acceleration
            V[i+1], A[i+1] = self._update_state(U[i+1], U[i], V[i], A[i], dt)

            # Update contact states
            for contact in contacts:
                contact.update_state(U[i+1], V[i+1], dt, preload_tracker.current_preload)

            # Update preload using proper system stiffness
            preload_loss = sum(c.get_preload_loss(k_sys) for c in contacts)
            preload_tracker.update(preload_loss, t[i+1])
            preload_history[i+1] = preload_tracker.current_preload

            # Reassemble matrices if needed (H4: periodic or preload-triggered)
            preload_change = abs(
                preload_history[i+1] - preload_at_last_assembly
            ) / (preload_at_last_assembly + 1e-10)
            if ((i + 1) % reassemble_interval == 0 or
                    preload_change > preload_change_threshold):
                if hasattr(assembler, 'assemble_matrices'):
                    M_new, K_new, C_new = assembler.assemble_matrices()
                    self.M = M_new
                    self.K = K_new
                    self.C = C_new
                    k_sys = _compute_system_stiffness_from_matrix(self.K)
                K_eff = self._compute_effective_stiffness(dt)
                K_eff_lu = linalg.lu_factor(K_eff)
                preload_at_last_assembly = preload_history[i+1]

        return IntegrationResult(
            time=t,
            displacement=U,
            velocity=V,
            acceleration=A,
            force=F
        )


class HHTIntegrator:
    """
    HHT-α (Hilber-Hughes-Taylor) time integration method.
    
    A variant of Newmark-β with controllable numerical damping
    for high-frequency components. Useful for stiff contact problems.
    
    Modified equation of motion:
    M·ẍₙ₊₁ + (1+α)C·ẋₙ₊₁ - αC·ẋₙ + (1+α)K·xₙ₊₁ - αK·xₙ = (1+α)Fₙ₊₁ - αFₙ
    """
    
    def __init__(
        self,
        M: np.ndarray,
        C: np.ndarray,
        K: np.ndarray,
        params: Optional[HHTParams] = None
    ):
        """
        Initialize HHT integrator.
        
        Args:
            M: Mass matrix
            C: Damping matrix
            K: Stiffness matrix
            params: HHT parameters
        """
        self.M = np.asarray(M)
        self.C = np.asarray(C)
        self.K = np.asarray(K)
        self.params = params or HHTParams.low_damping()
        self.n_dof = M.shape[0]
        
    def integrate(
        self,
        time_params: TimeParams,
        F_func: Callable[[float], np.ndarray],
        u0: Optional[np.ndarray] = None,
        v0: Optional[np.ndarray] = None
    ) -> IntegrationResult:
        """
        Perform time integration with HHT-α method.
        
        Args:
            time_params: Time integration parameters
            F_func: Force function F(t) -> np.ndarray[n_dof]
            u0: Initial displacement
            v0: Initial velocity
            
        Returns:
            IntegrationResult
        """
        alpha = self.params.alpha
        beta = self.params.beta
        gamma = self.params.gamma
        
        dt = time_params.dt
        t = time_params.time_vector
        n_steps = len(t)
        
        # Initialize storage
        U = np.zeros((n_steps, self.n_dof))
        V = np.zeros((n_steps, self.n_dof))
        A = np.zeros((n_steps, self.n_dof))
        F = np.zeros((n_steps, self.n_dof))
        
        # Initial conditions
        U[0] = u0 if u0 is not None else np.zeros(self.n_dof)
        V[0] = v0 if v0 is not None else np.zeros(self.n_dof)
        F[0] = F_func(t[0])
        
        # Initial acceleration
        rhs = F[0] - self.C @ V[0] - self.K @ U[0]
        A[0] = linalg.solve(self.M, rhs, assume_a='pos')
        
        # Integration constants
        a0 = 1.0 / (beta * dt**2)
        a1 = gamma / (beta * dt)
        a2 = 1.0 / (beta * dt)
        a3 = 1.0 / (2 * beta) - 1.0
        a4 = gamma / beta - 1.0
        a5 = dt * (gamma / (2 * beta) - 1.0)
        
        # Effective stiffness for HHT
        K_eff = (1 + alpha) * self.K + (1 + alpha) * a1 * self.C + a0 * self.M
        K_eff_lu = linalg.lu_factor(K_eff)
        
        # Time stepping
        for i in range(n_steps - 1):
            F[i+1] = F_func(t[i+1])
            
            # Effective force for HHT
            F_eff = (
                (1 + alpha) * F[i+1] - alpha * F[i] +
                alpha * self.K @ U[i] +
                alpha * self.C @ V[i] +
                self.M @ (a0 * U[i] + a2 * V[i] + a3 * A[i]) +
                (1 + alpha) * self.C @ (a1 * U[i] + a4 * V[i] + a5 * A[i])
            )
            
            # Solve for new displacement
            U[i+1] = linalg.lu_solve(K_eff_lu, F_eff)
            
            # Update acceleration
            A[i+1] = a0 * (U[i+1] - U[i]) - a2 * V[i] - a3 * A[i]
            
            # Update velocity
            V[i+1] = V[i] + dt * ((1 - gamma) * A[i] + gamma * A[i+1])
        
        return IntegrationResult(
            time=t,
            displacement=U,
            velocity=V,
            acceleration=A,
            force=F
        )

    def solve_with_contacts(
        self,
        time_params: TimeParams,
        assembler: Any,
        state_manager: Any,
        contacts: List[Any],
        preload_tracker: Any,
        F_external: Callable[[float], np.ndarray],
        reassemble_interval: int = 10,
        preload_change_threshold: float = 0.05
    ) -> IntegrationResult:
        """
        Perform HHT-α time integration with contact state updates.

        Similar to Newmark but with HHT-α parameters for enhanced damping.
        Uses Newmark predictor for tribological force evaluation at i+1.

        Args:
            time_params: Time integration parameters
            assembler: Matrix assembler
            state_manager: State manager
            contacts: List of contacts
            preload_tracker: Preload tracker
            F_external: External force function
            reassemble_interval: Reassemble K_eff every N steps (default: 10)
            preload_change_threshold: Reassemble if preload changes by this
                fraction since last assembly (default: 0.05 = 5%)

        Returns:
            IntegrationResult
        """
        alpha = self.params.alpha
        beta = self.params.beta
        gamma = self.params.gamma

        dt = time_params.dt
        t = time_params.time_vector
        n_steps = len(t)
        n_dof = self.n_dof

        # Initialize storage
        U = np.zeros((n_steps, n_dof))
        V = np.zeros((n_steps, n_dof))
        A = np.zeros((n_steps, n_dof))
        F = np.zeros((n_steps, n_dof))
        preload_history = np.zeros(n_steps)

        # Initial conditions
        U[0] = state_manager.state.displacement
        V[0] = state_manager.state.velocity
        F[0] = F_external(t[0])
        preload_history[0] = preload_tracker.current_preload

        # System stiffness for preload loss (series combination, not trace)
        k_sys = _compute_system_stiffness_from_matrix(self.K)

        # Initial acceleration
        F_trib = assembler.compute_tribological_forces(U[0], V[0])
        rhs = F[0] + F_trib - self.C @ V[0] - self.K @ U[0]
        A[0] = linalg.solve(self.M, rhs, assume_a='pos')

        # Integration constants
        a0 = 1.0 / (beta * dt**2)
        a1 = gamma / (beta * dt)
        a2 = 1.0 / (beta * dt)
        a3 = 1.0 / (2 * beta) - 1.0
        a4 = gamma / beta - 1.0
        a5 = dt * (gamma / (2 * beta) - 1.0)

        # Effective stiffness for HHT
        K_eff = (1 + alpha) * self.K + (1 + alpha) * a1 * self.C + a0 * self.M
        K_eff_lu = linalg.lu_factor(K_eff)
        preload_at_last_assembly = preload_tracker.current_preload

        # Time stepping
        for i in range(n_steps - 1):
            F[i+1] = F_external(t[i+1])
            F_trib_i = assembler.compute_tribological_forces(U[i], V[i])

            # Newmark predictor for step i+1
            U_pred = U[i] + dt * V[i] + 0.5 * dt**2 * A[i]
            V_pred = V[i] + dt * A[i]
            # Use predicted state for tribological forces at i+1
            F_trib_ip1 = assembler.compute_tribological_forces(U_pred, V_pred)

            # Effective force for HHT
            F_eff = (
                (1 + alpha) * (F[i+1] + F_trib_ip1) - alpha * (F[i] + F_trib_i) +
                alpha * self.K @ U[i] +
                alpha * self.C @ V[i] +
                self.M @ (a0 * U[i] + a2 * V[i] + a3 * A[i]) +
                (1 + alpha) * self.C @ (a1 * U[i] + a4 * V[i] + a5 * A[i])
            )

            # Solve
            U[i+1] = linalg.lu_solve(K_eff_lu, F_eff)

            # Update acceleration
            A[i+1] = a0 * (U[i+1] - U[i]) - a2 * V[i] - a3 * A[i]

            # Update velocity
            V[i+1] = V[i] + dt * ((1 - gamma) * A[i] + gamma * A[i+1])

            # Update contacts
            for contact in contacts:
                contact.update_state(U[i+1], V[i+1], dt, preload_tracker.current_preload)

            # Update preload using proper system stiffness
            preload_loss = sum(c.get_preload_loss(k_sys) for c in contacts)
            preload_tracker.update(preload_loss, t[i+1])
            preload_history[i+1] = preload_tracker.current_preload

            # Reassemble matrices if needed (H4: periodic or preload-triggered)
            preload_change = abs(
                preload_history[i+1] - preload_at_last_assembly
            ) / (preload_at_last_assembly + 1e-10)
            if ((i + 1) % reassemble_interval == 0 or
                    preload_change > preload_change_threshold):
                if hasattr(assembler, 'assemble_matrices'):
                    M_new, K_new, C_new = assembler.assemble_matrices()
                    self.M = M_new
                    self.K = K_new
                    self.C = C_new
                    k_sys = _compute_system_stiffness_from_matrix(self.K)
                K_eff = (1 + alpha) * self.K + (1 + alpha) * a1 * self.C + a0 * self.M
                K_eff_lu = linalg.lu_factor(K_eff)
                preload_at_last_assembly = preload_history[i+1]

        return IntegrationResult(
            time=t,
            displacement=U,
            velocity=V,
            acceleration=A,
            force=F
        )


class CentralDifferenceIntegrator:
    """
    Central Difference explicit time integration.
    
    Conditionally stable: Δt ≤ Tₘᵢₙ/π = 2/ωₘₐₓ
    
    Useful for high-frequency response and wave propagation problems.
    """
    
    def __init__(
        self,
        M: np.ndarray,
        C: np.ndarray,
        K: np.ndarray
    ):
        """
        Initialize Central Difference integrator.
        
        Args:
            M: Mass matrix (should be diagonal for efficiency)
            C: Damping matrix
            K: Stiffness matrix
        """
        self.M = np.asarray(M)
        self.C = np.asarray(C)
        self.K = np.asarray(K)
        self.n_dof = M.shape[0]
        
        # Check if mass is diagonal (for lumped mass)
        self._M_is_diagonal = np.allclose(M, np.diag(np.diag(M)))
        if not self._M_is_diagonal:
            warnings.warn("Central difference is most efficient with diagonal mass matrix")
    
    def get_critical_timestep(self) -> float:
        """
        Compute critical time step for stability.
        
        Returns:
            Maximum stable time step
        """
        # Compute maximum eigenvalue of M⁻¹K
        M_inv = np.linalg.inv(self.M)
        eigenvalues = np.real(linalg.eigvals(M_inv @ self.K))
        omega_max = np.sqrt(np.max(eigenvalues))
        
        # Critical time step: Δt_cr = 2/ω_max
        return 2.0 / omega_max
    
    def integrate(
        self,
        time_params: TimeParams,
        F_func: Callable[[float], np.ndarray],
        u0: Optional[np.ndarray] = None,
        v0: Optional[np.ndarray] = None
    ) -> IntegrationResult:
        """
        Perform explicit time integration.
        
        Args:
            time_params: Time integration parameters
            F_func: Force function
            u0: Initial displacement
            v0: Initial velocity
            
        Returns:
            IntegrationResult
        """
        dt = time_params.dt
        t = time_params.time_vector
        n_steps = len(t)
        
        # Check stability: Δt must be ≤ 2/ω_max for central difference
        dt_crit = self.get_critical_timestep()
        if dt > dt_crit:
            ratio = dt / dt_crit
            M_inv = np.linalg.inv(self.M)
            eigenvalues = np.real(linalg.eigvals(M_inv @ self.K))
            omega_max = np.sqrt(np.max(eigenvalues))
            f_max = omega_max / (2 * np.pi)
            warnings.warn(
                f"UNSTABLE: Time step dt={dt:.3e} s exceeds critical value "
                f"dt_crit=2/ω_max={dt_crit:.3e} s (ratio={ratio:.1f}x).\n"
                f"  Maximum natural frequency: {f_max:.1f} Hz (ω_max={omega_max:.1f} rad/s)\n"
                f"  Required: dt ≤ {dt_crit:.3e} s. Reduce dt by at least {ratio:.1f}x.",
                stacklevel=2
            )
        
        # Initialize
        U = np.zeros((n_steps, self.n_dof))
        V = np.zeros((n_steps, self.n_dof))
        A = np.zeros((n_steps, self.n_dof))
        F = np.zeros((n_steps, self.n_dof))
        
        U[0] = u0 if u0 is not None else np.zeros(self.n_dof)
        V[0] = v0 if v0 is not None else np.zeros(self.n_dof)
        F[0] = F_func(t[0])
        
        # Initial acceleration
        rhs = F[0] - self.C @ V[0] - self.K @ U[0]
        A[0] = linalg.solve(self.M, rhs, assume_a='pos')
        
        # u_{-1} for central difference start
        u_prev = U[0] - dt * V[0] + 0.5 * dt**2 * A[0]
        
        # Effective mass
        M_eff = self.M / dt**2 + self.C / (2 * dt)
        
        if self._M_is_diagonal:
            M_eff_diag_inv = 1.0 / np.diag(M_eff)
        else:
            M_eff_lu = linalg.lu_factor(M_eff)
        
        # Time stepping
        u_curr = U[0]
        for i in range(n_steps - 1):
            F[i+1] = F_func(t[i+1])

            # Effective force (use F at next step for better accuracy
            # with time-varying loads)
            F_eff = (
                F[i+1] -
                (self.K - 2 * self.M / dt**2) @ u_curr -
                (self.M / dt**2 - self.C / (2 * dt)) @ u_prev
            )
            
            # Solve for u_{n+1}
            if self._M_is_diagonal:
                u_next = M_eff_diag_inv * F_eff
            else:
                u_next = linalg.lu_solve(M_eff_lu, F_eff)
            
            # Store results
            U[i+1] = u_next
            V[i+1] = (u_next - u_prev) / (2 * dt)
            A[i+1] = (u_next - 2 * u_curr + u_prev) / dt**2
            
            # Advance
            u_prev = u_curr
            u_curr = u_next
        
        return IntegrationResult(
            time=t,
            displacement=U,
            velocity=V,
            acceleration=A,
            force=F
        )


class ModalSuperposition:
    """
    Modal superposition for linear dynamic analysis.
    
    Decomposes the system into modal coordinates and solves
    uncoupled SDOF equations. Efficient for systems with many DOFs
    when only a few modes contribute significantly.
    """
    
    def __init__(
        self,
        M: np.ndarray,
        C: np.ndarray,
        K: np.ndarray,
        n_modes: Optional[int] = None
    ):
        """
        Initialize modal superposition solver.
        
        Args:
            M: Mass matrix
            C: Damping matrix
            K: Stiffness matrix
            n_modes: Number of modes to use (default: all)
        """
        self.M = np.asarray(M)
        self.C = np.asarray(C)
        self.K = np.asarray(K)
        self.n_dof = M.shape[0]
        self.n_modes = n_modes if n_modes is not None else self.n_dof
        
        # Compute modal properties
        self._compute_modal_properties()
    
    def _compute_modal_properties(self):
        """Compute eigenvalues, eigenvectors, and modal parameters."""
        # Solve generalized eigenvalue problem: K·φ = ω²·M·φ
        eigenvalues, eigenvectors = linalg.eigh(self.K, self.M)
        
        # Sort by frequency (ascending)
        idx = np.argsort(eigenvalues)
        eigenvalues = eigenvalues[idx]
        eigenvectors = eigenvectors[:, idx]
        
        # Select modes
        n_modes = min(self.n_modes, len(eigenvalues))
        self.omega2 = eigenvalues[:n_modes]  # ω²
        self.omega = np.sqrt(np.maximum(self.omega2, 0))  # ω
        self.freq = self.omega / (2 * np.pi)  # Hz
        self.phi = eigenvectors[:, :n_modes]  # Mode shapes
        
        # Modal masses (should be 1 if properly normalized)
        self.modal_mass = np.diag(self.phi.T @ self.M @ self.phi)
        
        # Modal damping ratios (assuming proportional damping)
        modal_damping = np.diag(self.phi.T @ self.C @ self.phi)
        self.zeta = modal_damping / (2 * self.modal_mass * self.omega + 1e-10)
        
        # Damped frequencies
        self.omega_d = self.omega * np.sqrt(1 - self.zeta**2 + 1e-10)
    
    def integrate(
        self,
        time_params: TimeParams,
        F_func: Callable[[float], np.ndarray],
        u0: Optional[np.ndarray] = None,
        v0: Optional[np.ndarray] = None
    ) -> IntegrationResult:
        """
        Perform modal superposition integration.
        
        Args:
            time_params: Time parameters
            F_func: Force function
            u0: Initial displacement
            v0: Initial velocity
            
        Returns:
            IntegrationResult
        """
        dt = time_params.dt
        t = time_params.time_vector
        n_steps = len(t)
        n_modes = len(self.omega)
        
        # Initialize
        U = np.zeros((n_steps, self.n_dof))
        V = np.zeros((n_steps, self.n_dof))
        A = np.zeros((n_steps, self.n_dof))
        F_hist = np.zeros((n_steps, self.n_dof))
        
        # Initial conditions in modal coordinates
        u0 = u0 if u0 is not None else np.zeros(self.n_dof)
        v0 = v0 if v0 is not None else np.zeros(self.n_dof)
        
        q0 = self.phi.T @ self.M @ u0  # Modal displacements
        qdot0 = self.phi.T @ self.M @ v0  # Modal velocities
        
        U[0] = u0
        V[0] = v0
        F_hist[0] = F_func(t[0])
        
        # Modal responses using Duhamel integral (piecewise linear)
        q = np.zeros((n_steps, n_modes))
        qdot = np.zeros((n_steps, n_modes))
        
        q[0] = q0 / (self.modal_mass + 1e-10)
        qdot[0] = qdot0 / (self.modal_mass + 1e-10)
        
        for i in range(n_steps - 1):
            F_curr = F_func(t[i])
            F_next = F_func(t[i+1])
            F_hist[i+1] = F_next
            
            # Modal forces
            p_curr = self.phi.T @ F_curr
            p_next = self.phi.T @ F_next
            
            for j in range(n_modes):
                omega_j = self.omega[j]
                zeta_j = self.zeta[j]
                omega_d_j = self.omega_d[j]
                m_j = self.modal_mass[j]
                
                if omega_j < 1e-10:
                    # Rigid body mode
                    q[i+1, j] = q[i, j] + dt * qdot[i, j] + 0.5 * dt**2 * p_curr[j] / m_j
                    qdot[i+1, j] = qdot[i, j] + dt * p_curr[j] / m_j
                else:
                    # Use exact solution for SDOF with piecewise linear force
                    exp_factor = np.exp(-zeta_j * omega_j * dt)
                    cos_wd = np.cos(omega_d_j * dt)
                    sin_wd = np.sin(omega_d_j * dt)
                    
                    # Homogeneous solution coefficients
                    A_coef = q[i, j]
                    B_coef = (qdot[i, j] + zeta_j * omega_j * q[i, j]) / (omega_d_j + 1e-10)
                    
                    # Particular solution (constant force approximation)
                    p_avg = 0.5 * (p_curr[j] + p_next[j])
                    u_static = p_avg / (m_j * omega_j**2)
                    
                    # Combined response
                    q[i+1, j] = (
                        exp_factor * (A_coef * cos_wd + B_coef * sin_wd) +
                        u_static * (1 - exp_factor * (cos_wd + zeta_j * omega_j / omega_d_j * sin_wd))
                    )
                    qdot[i+1, j] = (
                        exp_factor * (
                            (B_coef * omega_d_j - A_coef * zeta_j * omega_j) * cos_wd -
                            (A_coef * omega_d_j + B_coef * zeta_j * omega_j) * sin_wd
                        )
                    )
        
        # Transform back to physical coordinates
        for i in range(n_steps):
            U[i] = self.phi @ q[i]
            V[i] = self.phi @ qdot[i]
            # Compute acceleration from equation of motion
            F_i = F_hist[i] if i < n_steps else F_func(t[-1])
            A[i] = linalg.solve(self.M, F_i - self.C @ V[i] - self.K @ U[i])
        
        return IntegrationResult(
            time=t,
            displacement=U,
            velocity=V,
            acceleration=A,
            force=F_hist
        )


class RungeKutta4:
    """
    4th order Runge-Kutta integrator for state-space systems.
    
    Solves: ż = f(t, z) where z = [x; ẋ]
    
    Useful for nonlinear systems or when state-space form is preferred.
    """
    
    def __init__(
        self,
        M: np.ndarray,
        C: np.ndarray,
        K: np.ndarray
    ):
        """
        Initialize RK4 integrator.
        
        Args:
            M: Mass matrix
            C: Damping matrix
            K: Stiffness matrix
        """
        self.M = np.asarray(M)
        self.C = np.asarray(C)
        self.K = np.asarray(K)
        self.n_dof = M.shape[0]
        
        # Compute state-space matrices: ż = Az + B·F
        self.M_inv = np.linalg.inv(M)
        self.A = np.block([
            [np.zeros((self.n_dof, self.n_dof)), np.eye(self.n_dof)],
            [-self.M_inv @ K, -self.M_inv @ C]
        ])
        self.B = np.block([
            [np.zeros((self.n_dof, self.n_dof))],
            [self.M_inv]
        ])
    
    def _state_derivative(self, t: float, z: np.ndarray, F_func: Callable) -> np.ndarray:
        """Compute state derivative."""
        F = F_func(t)
        return self.A @ z + self.B @ F
    
    def integrate(
        self,
        time_params: TimeParams,
        F_func: Callable[[float], np.ndarray],
        u0: Optional[np.ndarray] = None,
        v0: Optional[np.ndarray] = None
    ) -> IntegrationResult:
        """
        Perform RK4 integration.
        
        Args:
            time_params: Time parameters
            F_func: Force function
            u0: Initial displacement
            v0: Initial velocity
            
        Returns:
            IntegrationResult
        """
        dt = time_params.dt
        t = time_params.time_vector
        n_steps = len(t)
        
        # Initialize
        U = np.zeros((n_steps, self.n_dof))
        V = np.zeros((n_steps, self.n_dof))
        A = np.zeros((n_steps, self.n_dof))
        F_hist = np.zeros((n_steps, self.n_dof))
        
        u0 = u0 if u0 is not None else np.zeros(self.n_dof)
        v0 = v0 if v0 is not None else np.zeros(self.n_dof)
        
        z = np.concatenate([u0, v0])
        
        for i in range(n_steps):
            U[i] = z[:self.n_dof]
            V[i] = z[self.n_dof:]
            F_hist[i] = F_func(t[i])
            A[i] = self.M_inv @ (F_hist[i] - self.C @ V[i] - self.K @ U[i])
            
            if i < n_steps - 1:
                # RK4 step
                k1 = self._state_derivative(t[i], z, F_func)
                k2 = self._state_derivative(t[i] + 0.5*dt, z + 0.5*dt*k1, F_func)
                k3 = self._state_derivative(t[i] + 0.5*dt, z + 0.5*dt*k2, F_func)
                k4 = self._state_derivative(t[i] + dt, z + dt*k3, F_func)
                
                z = z + (dt/6) * (k1 + 2*k2 + 2*k3 + k4)
        
        return IntegrationResult(
            time=t,
            displacement=U,
            velocity=V,
            acceleration=A,
            force=F_hist
        )


class NonlinearNewmark:
    """
    Newmark-β integration with Newton-Raphson for nonlinear problems.
    
    Handles nonlinear stiffness and damping:
    M·ẍ + f_int(x, ẋ) = f_ext(t)
    
    where f_int is the internal force vector that may depend
    nonlinearly on displacement and velocity.
    """
    
    def __init__(
        self,
        M: np.ndarray,
        newmark_params: Optional[NewmarkParams] = None,
        nonlinear_params: Optional[NonlinearParams] = None
    ):
        """
        Initialize nonlinear Newmark integrator.
        
        Args:
            M: Mass matrix
            newmark_params: Newmark parameters
            nonlinear_params: Nonlinear solver parameters
        """
        self.M = np.asarray(M)
        self.n_dof = M.shape[0]
        self.newmark = newmark_params or NewmarkParams.average_acceleration()
        self.nl_params = nonlinear_params or NonlinearParams()
    
    def integrate(
        self,
        time_params: TimeParams,
        f_ext_func: Callable[[float], np.ndarray],
        f_int_func: Callable[[np.ndarray, np.ndarray], np.ndarray],
        K_tan_func: Callable[[np.ndarray, np.ndarray], np.ndarray],
        C_tan_func: Optional[Callable[[np.ndarray, np.ndarray], np.ndarray]] = None,
        u0: Optional[np.ndarray] = None,
        v0: Optional[np.ndarray] = None
    ) -> IntegrationResult:
        """
        Perform nonlinear time integration.
        
        Args:
            time_params: Time parameters
            f_ext_func: External force function f_ext(t)
            f_int_func: Internal force function f_int(u, v)
            K_tan_func: Tangent stiffness function K_t(u, v)
            C_tan_func: Tangent damping function C_t(u, v) (optional)
            u0: Initial displacement
            v0: Initial velocity
            
        Returns:
            IntegrationResult with iteration counts
        """
        dt = time_params.dt
        t = time_params.time_vector
        n_steps = len(t)
        beta = self.newmark.beta
        gamma = self.newmark.gamma
        
        # Initialize
        U = np.zeros((n_steps, self.n_dof))
        V = np.zeros((n_steps, self.n_dof))
        A = np.zeros((n_steps, self.n_dof))
        F_ext = np.zeros((n_steps, self.n_dof))
        F_int = np.zeros((n_steps, self.n_dof))
        iterations = []
        converged = True
        
        U[0] = u0 if u0 is not None else np.zeros(self.n_dof)
        V[0] = v0 if v0 is not None else np.zeros(self.n_dof)
        F_ext[0] = f_ext_func(t[0])
        F_int[0] = f_int_func(U[0], V[0])
        A[0] = linalg.solve(self.M, F_ext[0] - F_int[0], assume_a='pos')
        
        # Integration constants
        a0 = 1.0 / (beta * dt**2)
        a1 = gamma / (beta * dt)
        a2 = 1.0 / (beta * dt)
        a3 = 1.0 / (2 * beta) - 1.0
        a4 = gamma / beta - 1.0
        a5 = dt * (gamma / (2 * beta) - 1.0)
        
        for i in range(n_steps - 1):
            F_ext[i+1] = f_ext_func(t[i+1])
            
            # Predictor
            u_pred = U[i] + dt * V[i] + 0.5 * dt**2 * A[i]
            v_pred = V[i] + dt * A[i]
            a_pred = np.zeros(self.n_dof)
            
            # Newton-Raphson iteration
            u_new = u_pred.copy()
            v_new = v_pred.copy()
            a_new = a_pred.copy()
            
            n_iter = 0
            converged_step = False
            last_du_norm = np.inf  # Track Newton increment norm
            last_du_vec = None     # Track Newton increment vector for energy criterion

            for k in range(self.nl_params.max_iterations):
                # Update velocity and acceleration from displacement
                a_new = a0 * (u_new - U[i]) - a2 * V[i] - a3 * A[i]
                v_new = V[i] + dt * ((1 - gamma) * A[i] + gamma * a_new)

                # Residual
                f_int_new = f_int_func(u_new, v_new)
                R = self.M @ a_new + f_int_new - F_ext[i+1]

                # Check convergence using Newton increment norm (not total displacement)
                norm_R = np.linalg.norm(R)
                norm_du = last_du_norm  # Newton correction increment
                # Energy criterion: |Δu·R| per reference Section 50.3
                energy = abs(np.dot(last_du_vec, R)) if last_du_vec is not None else norm_R
                
                if self.nl_params.convergence_type == ConvergenceType.FORCE:
                    conv = norm_R < self.nl_params.tol_force
                elif self.nl_params.convergence_type == ConvergenceType.DISPLACEMENT:
                    conv = norm_du < self.nl_params.tol_disp
                elif self.nl_params.convergence_type == ConvergenceType.ENERGY:
                    conv = energy < self.nl_params.tol_energy
                else:  # COMBINED
                    conv = (
                        norm_R < self.nl_params.tol_force and
                        norm_du < self.nl_params.tol_disp and
                        energy < self.nl_params.tol_energy
                    )
                
                if conv:
                    converged_step = True
                    break
                
                # Tangent stiffness
                K_t = K_tan_func(u_new, v_new)
                if C_tan_func is not None:
                    C_t = C_tan_func(u_new, v_new)
                else:
                    C_t = np.zeros_like(K_t)
                
                # Effective tangent
                K_eff = K_t + a1 * C_t + a0 * self.M
                
                # Solve for displacement increment
                try:
                    du = linalg.solve(K_eff, -R)
                except linalg.LinAlgError:
                    warnings.warn(f"Singular tangent at step {i+1}, iteration {k}")
                    du = np.linalg.lstsq(K_eff, -R, rcond=None)[0]
                
                # Line search (optional)
                if self.nl_params.line_search:
                    alpha = 1.0
                    for ls_iter in range(self.nl_params.line_search_max_iter):
                        u_trial = u_new + alpha * du
                        a_trial = a0 * (u_trial - U[i]) - a2 * V[i] - a3 * A[i]
                        v_trial = V[i] + dt * ((1 - gamma) * A[i] + gamma * a_trial)
                        f_int_trial = f_int_func(u_trial, v_trial)
                        R_trial = self.M @ a_trial + f_int_trial - F_ext[i+1]

                        if np.linalg.norm(R_trial) < norm_R:
                            break
                        alpha *= self.nl_params.line_search_factor

                    actual_du = alpha * du
                    u_new = u_new + actual_du
                    last_du_norm = np.linalg.norm(actual_du)
                    last_du_vec = actual_du
                else:
                    u_new = u_new + du
                    last_du_norm = np.linalg.norm(du)
                    last_du_vec = du

                n_iter = k + 1
            
            if not converged_step:
                warnings.warn(f"Step {i+1} did not converge after {n_iter} iterations")
                converged = False
            
            iterations.append(n_iter)
            U[i+1] = u_new
            V[i+1] = v_new
            A[i+1] = a_new
            F_int[i+1] = f_int_func(u_new, v_new)
        
        return IntegrationResult(
            time=t,
            displacement=U,
            velocity=V,
            acceleration=A,
            force=F_ext,
            internal_force=F_int,
            iterations=iterations,
            converged=converged
        )


class AdaptiveRK45:
    """
    Adaptive Runge-Kutta 4(5) integrator (Dormand-Prince method).

    Uses embedded RK4/5 pair for automatic step size control.
    The local truncation error is estimated by comparing 4th and 5th
    order solutions, and the step size is adjusted to maintain the
    error within specified tolerances.

    Particularly useful for stiff or multi-scale problems where a
    fixed time step would be either too small (slow) or too large
    (inaccurate) throughout the simulation.
    """

    # Dormand-Prince coefficients
    _a = np.array([0, 1/5, 3/10, 4/5, 8/9, 1, 1])
    _b = np.array([
        [0, 0, 0, 0, 0, 0],
        [1/5, 0, 0, 0, 0, 0],
        [3/40, 9/40, 0, 0, 0, 0],
        [44/45, -56/15, 32/9, 0, 0, 0],
        [19372/6561, -25360/2187, 64448/6561, -212/729, 0, 0],
        [9017/3168, -355/33, 46732/5247, 49/176, -5103/18656, 0],
    ])
    # 5th order weights
    _c5 = np.array([35/384, 0, 500/1113, 125/192, -2187/6784, 11/84])
    # 4th order weights
    _c4 = np.array([5179/57600, 0, 7571/16695, 393/640, -92097/339200,
                     187/2100])
    # Error weights = c5 - c4
    _ce = _c5 - _c4

    def __init__(
        self,
        M: np.ndarray,
        C: np.ndarray,
        K: np.ndarray,
        atol: float = 1e-6,
        rtol: float = 1e-3,
        safety: float = 0.9,
        dt_min_factor: float = 0.2,
        dt_max_factor: float = 5.0
    ):
        """
        Initialize adaptive RK45 integrator.

        Args:
            M: Mass matrix
            C: Damping matrix
            K: Stiffness matrix
            atol: Absolute error tolerance (default: 1e-6 for structural dynamics)
            rtol: Relative error tolerance (default: 1e-3 for structural dynamics)
            safety: Safety factor for step size adjustment (< 1)
            dt_min_factor: Minimum step size reduction factor
            dt_max_factor: Maximum step size growth factor
        """
        self.M = np.asarray(M)
        self.C = np.asarray(C)
        self.K = np.asarray(K)
        self.n_dof = M.shape[0]
        self.atol = atol
        self.rtol = rtol
        self.safety = safety
        self.dt_min_factor = dt_min_factor
        self.dt_max_factor = dt_max_factor

        # Precompute state-space matrices
        self.M_inv = np.linalg.inv(M)
        n = self.n_dof
        self.A_mat = np.block([
            [np.zeros((n, n)), np.eye(n)],
            [-self.M_inv @ K, -self.M_inv @ C]
        ])
        self.B_mat = np.block([
            [np.zeros((n, n))],
            [self.M_inv]
        ])

    def _state_derivative(self, t: float, z: np.ndarray,
                          F_func: Callable) -> np.ndarray:
        return self.A_mat @ z + self.B_mat @ F_func(t)

    def integrate(
        self,
        time_params: TimeParams,
        F_func: Callable[[float], np.ndarray],
        u0: Optional[np.ndarray] = None,
        v0: Optional[np.ndarray] = None
    ) -> IntegrationResult:
        """
        Perform adaptive RK4(5) integration.

        The output is interpolated onto the uniform time grid defined by
        time_params, but internal steps are adaptive.

        Args:
            time_params: Time parameters (defines output grid and initial dt)
            F_func: Force function F(t) -> np.ndarray[n_dof]
            u0: Initial displacement
            v0: Initial velocity

        Returns:
            IntegrationResult with displacement, velocity, acceleration
        """
        t_out = time_params.time_vector
        n_out = len(t_out)
        n = self.n_dof

        # Initialize output storage
        U = np.zeros((n_out, n))
        V = np.zeros((n_out, n))
        A_out = np.zeros((n_out, n))
        F_hist = np.zeros((n_out, n))

        u0 = u0 if u0 is not None else np.zeros(n)
        v0 = v0 if v0 is not None else np.zeros(n)

        z = np.concatenate([u0, v0])
        U[0] = u0
        V[0] = v0
        F_hist[0] = F_func(t_out[0])
        A_out[0] = self.M_inv @ (F_hist[0] - self.C @ v0 - self.K @ u0)

        t_curr = t_out[0]
        dt = time_params.dt
        dt_base = dt  # Remember user-requested dt for step growth
        out_idx = 1
        n_accepted = 0
        n_rejected = 0
        max_steps = 100 * n_out  # Safety limit on total steps

        while out_idx < n_out and n_accepted + n_rejected < max_steps:
            # Clamp dt to hit the next output point exactly
            dt_to_out = t_out[out_idx] - t_curr
            dt_step = min(dt, dt_to_out)
            if dt_step < 1e-14:
                # Floating point: we're essentially at the output point
                U[out_idx] = z[:n]
                V[out_idx] = z[n:]
                F_hist[out_idx] = F_func(t_out[out_idx])
                A_out[out_idx] = self.M_inv @ (
                    F_hist[out_idx] - self.C @ V[out_idx] - self.K @ U[out_idx]
                )
                out_idx += 1
                t_curr = t_out[out_idx - 1]
                continue

            # Compute RK stages
            k = np.zeros((6, 2 * n))
            k[0] = self._state_derivative(t_curr, z, F_func)
            for s in range(1, 6):
                t_s = t_curr + self._a[s] * dt_step
                z_s = z + dt_step * sum(
                    self._b[s][j] * k[j] for j in range(s)
                )
                k[s] = self._state_derivative(t_s, z_s, F_func)

            # 5th order solution
            z5 = z + dt_step * sum(self._c5[j] * k[j] for j in range(6))

            # Error estimate (difference between 4th and 5th order)
            err_vec = dt_step * sum(self._ce[j] * k[j] for j in range(6))

            # Scaled error norm (use displacement DOFs only for scaling,
            # since displacement and velocity have very different magnitudes)
            z_ref = np.maximum(np.abs(z[:n]), np.abs(z5[:n]))
            scale_u = self.atol + self.rtol * z_ref
            # Scale velocity error by characteristic frequency
            omega_est = max(np.sqrt(np.max(np.abs(np.diag(self.K))) /
                           (np.max(np.abs(np.diag(self.M))) + 1e-30)), 1.0)
            scale_v = self.atol * omega_est + self.rtol * np.maximum(
                np.abs(z[n:]), np.abs(z5[n:]))
            scale = np.concatenate([scale_u, scale_v])
            err_norm = np.sqrt(np.mean((err_vec / scale) ** 2))

            if err_norm <= 1.0:
                # Accept step
                t_curr += dt_step
                z = z5
                n_accepted += 1

                # Output at grid points we've reached
                while (out_idx < n_out and
                       t_curr >= t_out[out_idx] - 1e-10):
                    U[out_idx] = z[:n]
                    V[out_idx] = z[n:]
                    F_hist[out_idx] = F_func(t_out[out_idx])
                    A_out[out_idx] = self.M_inv @ (
                        F_hist[out_idx] - self.C @ V[out_idx] -
                        self.K @ U[out_idx]
                    )
                    out_idx += 1

                # Grow step size
                if err_norm > 1e-20:
                    factor = self.safety * (1.0 / err_norm) ** 0.2
                else:
                    factor = self.dt_max_factor
                dt = dt_step * min(factor, self.dt_max_factor)
                dt = max(dt, dt_base * 0.01)  # Don't shrink below 1% of base
            else:
                # Reject step, shrink
                n_rejected += 1
                factor = self.safety * (1.0 / err_norm) ** 0.25
                dt = dt_step * max(factor, self.dt_min_factor)

        return IntegrationResult(
            time=t_out,
            displacement=U,
            velocity=V,
            acceleration=A_out,
            force=F_hist
        )


# =============================================================================
# Factory Functions
# =============================================================================

def create_integrator(
    integrator_type: IntegratorType,
    M: np.ndarray,
    C: np.ndarray,
    K: np.ndarray,
    **kwargs
) -> Any:
    """
    Create time integrator of specified type.

    Args:
        integrator_type: Type of integrator
        M: Mass matrix
        C: Damping matrix
        K: Stiffness matrix
        **kwargs: Additional parameters for specific integrators

    Returns:
        Integrator instance
    """
    # L7: Convert to sparse if n_dof > 30 and sparse mode requested
    use_sparse = kwargs.pop('use_sparse', None)
    n_dof = M.shape[0]
    if use_sparse is None:
        use_sparse = n_dof > 30
    if use_sparse and not issparse(M):
        M = csr_matrix(M)
        C = csr_matrix(C)
        K = csr_matrix(K)
    elif not use_sparse and issparse(M):
        M = np.asarray(M.todense())
        C = np.asarray(C.todense())
        K = np.asarray(K.todense())

    if integrator_type == IntegratorType.NEWMARK_BETA:
        params = kwargs.get('newmark_params', NewmarkParams.average_acceleration())
        return NewmarkIntegrator(M, C, K, params)

    elif integrator_type == IntegratorType.HHT_ALPHA:
        params = kwargs.get('hht_params', HHTParams.low_damping())
        return HHTIntegrator(M, C, K, params)

    elif integrator_type == IntegratorType.CENTRAL_DIFFERENCE:
        return CentralDifferenceIntegrator(M, C, K)

    elif integrator_type == IntegratorType.MODAL_SUPERPOSITION:
        n_modes = kwargs.get('n_modes', None)
        return ModalSuperposition(M, C, K, n_modes)

    elif integrator_type == IntegratorType.RUNGE_KUTTA_4:
        return RungeKutta4(M, C, K)

    elif integrator_type == IntegratorType.ADAPTIVE_RK45:
        return AdaptiveRK45(
            M, C, K,
            atol=kwargs.get('atol', 1e-6),
            rtol=kwargs.get('rtol', 1e-3)
        )

    else:
        raise ValueError(f"Unknown integrator type: {integrator_type}")


# =============================================================================
# Utility Functions
# =============================================================================

def compute_rayleigh_damping(
    M: np.ndarray,
    K: np.ndarray,
    omega1: float,
    omega2: float,
    zeta: float = 0.02
) -> Tuple[float, float, np.ndarray]:
    """
    Compute Rayleigh damping matrix: C = α·M + β·K

    Provides equal damping ratio ζ at two frequencies ω₁ and ω₂.

    Args:
        M: Mass matrix
        K: Stiffness matrix
        omega1: First circular frequency (rad/s)
        omega2: Second circular frequency (rad/s)
        zeta: Target damping ratio (default: 0.02 = 2% per VDI 2230)
        
    Returns:
        (alpha, beta, C) - Rayleigh coefficients and damping matrix
    """
    # Solve for α and β from:
    # ζ = (α/2ω + β·ω/2)
    # at ω₁ and ω₂ with same ζ
    
    A = np.array([
        [1 / (2 * omega1), omega1 / 2],
        [1 / (2 * omega2), omega2 / 2]
    ])
    b = np.array([zeta, zeta])
    
    coeffs = np.linalg.solve(A, b)
    alpha, beta = coeffs
    
    C = alpha * M + beta * K
    
    return alpha, beta, C


def harmonic_force(
    amplitude: np.ndarray,
    frequency: float,
    phase: float = 0.0
) -> Callable[[float], np.ndarray]:
    """
    Create harmonic force function: F(t) = A·sin(ω·t + φ)
    
    Args:
        amplitude: Force amplitude vector
        frequency: Frequency in Hz
        phase: Phase angle in radians
        
    Returns:
        Force function F(t)
    """
    omega = 2 * np.pi * frequency
    amplitude = np.asarray(amplitude)

    def F(t: float) -> np.ndarray:
        return amplitude * np.sin(omega * t + phase)

    return F


def biased_harmonic_force(
    F_mean: np.ndarray,
    F_alt: np.ndarray,
    frequency: float,
    phase: float = 0.0,
    waveform: str = "sinusoidal",
    dynamic_factor: float = 1.0
) -> Callable[[float], np.ndarray]:
    """
    Create a mean-biased harmonic (or non-sinusoidal) force function.

    VDI 2230 representation:
        F(t) = F_mean + φ · F_alt · w(ωt + φ₀)

    where:
        F_mean  = (F_max + F_min) / 2   — mean force vector [N]
        F_alt   = (F_max − F_min) / 2   — force amplitude vector [N]
        φ       = dynamic_factor         — dynamic amplification (>1 for vibration/shock)
        w(x)    = waveform function (sinusoidal / square / sawtooth)

    The stress ratio R = F_min / F_max can be recovered as:
        R = (F_mean − F_alt) / (F_mean + F_alt)

    Args:
        F_mean:         Mean force vector [N] (can be scalar-broadcast)
        F_alt:          Alternating force amplitude vector [N]
        frequency:      Excitation frequency [Hz]
        phase:          Phase offset [rad]
        waveform:       'sinusoidal' (default), 'square', or 'sawtooth'
        dynamic_factor: Dynamic amplification factor φ ≥ 1.0

    Returns:
        Force function F(t) → np.ndarray
    """
    omega = 2.0 * np.pi * frequency
    F_mean = np.asarray(F_mean, dtype=float)
    F_alt  = np.asarray(F_alt,  dtype=float)
    phi    = float(dynamic_factor)

    if waveform == "square":
        def w(x: float) -> float:
            return float(np.sign(np.sin(x)))
    elif waveform == "sawtooth":
        def w(x: float) -> float:
            # Normalised sawtooth ∈ [−1, +1]
            return 2.0 * ((x / (2.0 * np.pi)) % 1.0) - 1.0
    else:  # sinusoidal (default)
        def w(x: float) -> float:
            return float(np.sin(x))

    def F(t: float) -> np.ndarray:
        return F_mean + phi * F_alt * w(omega * t + phase)

    return F


def step_force(
    amplitude: np.ndarray,
    t_start: float = 0.0,
    rise_time: float = 0.0
) -> Callable[[float], np.ndarray]:
    """
    Create step force function with optional smooth ramp.
    
    Args:
        amplitude: Final force amplitude vector
        t_start: Start time of step
        rise_time: Rise time (0 for instant step)
        
    Returns:
        Force function F(t)
    """
    amplitude = np.asarray(amplitude)
    
    def F(t: float) -> np.ndarray:
        if t < t_start:
            return np.zeros_like(amplitude)
        elif rise_time > 0 and t < t_start + rise_time:
            # Smooth ramp (half-sine)
            progress = (t - t_start) / rise_time
            factor = 0.5 * (1 - np.cos(np.pi * progress))
            return amplitude * factor
        else:
            return amplitude.copy()
    
    return F


def pulse_force(
    amplitude: np.ndarray,
    t_start: float = 0.0,
    duration: float = 0.01
) -> Callable[[float], np.ndarray]:
    """
    Create pulse force function.
    
    Args:
        amplitude: Pulse amplitude vector
        t_start: Start time of pulse
        duration: Pulse duration
        
    Returns:
        Force function F(t)
    """
    amplitude = np.asarray(amplitude)
    
    def F(t: float) -> np.ndarray:
        if t_start <= t < t_start + duration:
            return amplitude.copy()
        else:
            return np.zeros_like(amplitude)
    
    return F


def random_force(
    rms_amplitude: np.ndarray,
    frequency_range: Tuple[float, float] = (1.0, 100.0),
    seed: Optional[int] = None,
    n_components: int = 200
) -> Callable[[float], np.ndarray]:
    """
    Create band-limited random force function.

    Note: This creates a simple approximation using superposition of
    random-phase sinusoids within the specified frequency band.

    Args:
        rms_amplitude: RMS amplitude vector
        frequency_range: (f_min, f_max) in Hz
        seed: Random seed for reproducibility
        n_components: Number of frequency components (default: 200)

    Returns:
        Force function F(t)
    """
    rng = np.random.default_rng(seed)
    rms_amplitude = np.asarray(rms_amplitude)
    n_dof = len(rms_amplitude)

    # Generate random frequency components
    f_min, f_max = frequency_range
    frequencies = rng.uniform(f_min, f_max, n_components)
    phases = rng.uniform(0, 2*np.pi, (n_dof, n_components))
    
    # Scale amplitudes for correct RMS
    component_amp = rms_amplitude[:, np.newaxis] * np.sqrt(2 / n_components)
    
    def F(t: float) -> np.ndarray:
        omega = 2 * np.pi * frequencies
        sinusoids = np.sin(omega * t + phases)
        return np.sum(component_amp * sinusoids, axis=1)
    
    return F


def superposed_force(
    *force_funcs: Callable[[float], np.ndarray],
    static_force: Optional[np.ndarray] = None
) -> Callable[[float], np.ndarray]:
    """
    Superpose multiple force functions (reference Section 48.5).

    F_total(t) = F_static + Σ F_i(t)

    Args:
        *force_funcs: Variable number of force functions F_i(t)
        static_force: Optional constant force vector (e.g., preload)

    Returns:
        Combined force function F_total(t)
    """
    def F(t: float) -> np.ndarray:
        total = static_force.copy() if static_force is not None else None
        for f_i in force_funcs:
            contribution = f_i(t)
            if total is None:
                total = contribution.copy()
            else:
                total = total + contribution
        return total if total is not None else np.array([0.0])

    return F


def compute_damping_ratio_at_frequency(
    alpha: float,
    beta: float,
    omega: float
) -> float:
    """
    Compute Rayleigh damping ratio at arbitrary frequency (reference Section 49.3).

    ζ(ω) = α/(2ω) + β·ω/2

    Args:
        alpha: Mass-proportional Rayleigh coefficient
        beta: Stiffness-proportional Rayleigh coefficient
        omega: Circular frequency (rad/s)

    Returns:
        Damping ratio ζ at the given frequency
    """
    if omega <= 0:
        return 0.0
    return alpha / (2 * omega) + beta * omega / 2


# =============================================================================
# Test Suite
# =============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("Time Integration Methods - Test Suite")
    print("Bolt Analysis Studio v4.0")
    print("=" * 70)
    
    # Create a simple 2-DOF system
    # Mass-spring-damper chain: |--[m1]--k1--[m2]--k2--|
    m1, m2 = 1.0, 1.0
    k1, k2 = 1000.0, 500.0
    zeta = 0.05
    
    M = np.array([[m1, 0], [0, m2]])
    K = np.array([[k1 + k2, -k2], [-k2, k2]])
    
    # Rayleigh damping
    omega1 = np.sqrt(k1 / m1)
    omega2 = np.sqrt((k1 + k2) / m2)
    alpha, beta, C = compute_rayleigh_damping(M, K, omega1, omega2, zeta)
    print(f"\n[Setup] 2-DOF System")
    print(f"  Masses: {m1}, {m2} kg")
    print(f"  Stiffnesses: {k1}, {k2} N/m")
    print(f"  Rayleigh damping: α={alpha:.4f}, β={beta:.6f}")
    
    # Time parameters
    time_params = TimeParams(t_start=0.0, t_end=0.5, dt=0.001)
    
    # Harmonic excitation at first DOF
    F_amp = np.array([100.0, 0.0])
    f_excite = 5.0  # Hz
    F_func = harmonic_force(F_amp, f_excite)
    
    print(f"\n[Test 1] Newmark-β (Average Acceleration)")
    newmark = NewmarkIntegrator(M, C, K, NewmarkParams.average_acceleration())
    result_newmark = newmark.integrate(time_params, F_func)
    print(f"  Steps: {result_newmark.n_steps}")
    print(f"  Max displacement: {result_newmark.get_max_displacement()}")
    print(f"  Max velocity: {result_newmark.get_max_velocity()}")
    
    print(f"\n[Test 2] HHT-α (Medium Damping)")
    hht = HHTIntegrator(M, C, K, HHTParams.medium_damping())
    result_hht = hht.integrate(time_params, F_func)
    print(f"  Max displacement: {result_hht.get_max_displacement()}")
    
    print(f"\n[Test 3] Central Difference (Explicit)")
    cd = CentralDifferenceIntegrator(M, C, K)
    dt_crit = cd.get_critical_timestep()
    print(f"  Critical time step: {dt_crit:.6f} s")
    time_params_cd = TimeParams(t_start=0.0, t_end=0.5, dt=min(0.001, 0.9*dt_crit))
    result_cd = cd.integrate(time_params_cd, F_func)
    print(f"  Max displacement: {result_cd.get_max_displacement()}")
    
    print(f"\n[Test 4] Modal Superposition")
    modal = ModalSuperposition(M, C, K)
    print(f"  Natural frequencies: {modal.freq} Hz")
    print(f"  Modal damping ratios: {modal.zeta}")
    result_modal = modal.integrate(time_params, F_func)
    print(f"  Max displacement: {result_modal.get_max_displacement()}")
    
    print(f"\n[Test 5] Runge-Kutta 4")
    rk4 = RungeKutta4(M, C, K)
    result_rk4 = rk4.integrate(time_params, F_func)
    print(f"  Max displacement: {result_rk4.get_max_displacement()}")
    
    print(f"\n[Test 6] Compare Methods")
    # Compare final displacements
    methods = {
        'Newmark-β': result_newmark,
        'HHT-α': result_hht,
        'Modal': result_modal,
        'RK4': result_rk4
    }
    ref = result_newmark.displacement[-1]
    print(f"  Reference (Newmark): {ref}")
    for name, res in methods.items():
        diff = np.linalg.norm(res.displacement[-1] - ref) / (np.linalg.norm(ref) + 1e-10)
        print(f"  {name} rel. error: {diff:.2e}")
    
    print(f"\n[Test 7] Energy Conservation")
    result_newmark.compute_energies(M, K, C)
    E_total_start = result_newmark.energy_kinetic[0] + result_newmark.energy_potential[0]
    E_total_end = (
        result_newmark.energy_kinetic[-1] + 
        result_newmark.energy_potential[-1] +
        result_newmark.energy_dissipated[-1]
    )
    print(f"  Initial energy (PE): {result_newmark.energy_potential[0]:.4f} J")
    print(f"  Final KE: {result_newmark.energy_kinetic[-1]:.4f} J")
    print(f"  Final PE: {result_newmark.energy_potential[-1]:.4f} J")
    print(f"  Dissipated: {result_newmark.energy_dissipated[-1]:.4f} J")
    
    print(f"\n[Test 8] Step Response")
    F_step = step_force(np.array([100.0, 0.0]), t_start=0.0, rise_time=0.01)
    time_params_step = TimeParams(t_start=0.0, t_end=0.2, dt=0.0005)
    result_step = newmark.integrate(time_params_step, F_step)
    static_disp = np.linalg.solve(K, np.array([100.0, 0.0]))
    overshoot = (np.max(result_step.displacement[:, 0]) / static_disp[0] - 1) * 100
    print(f"  Static displacement: {static_disp}")
    print(f"  Max dynamic: {result_step.get_max_displacement()}")
    print(f"  Overshoot DOF 1: {overshoot:.1f}%")
    
    print("\n" + "=" * 70)
    print("All tests completed successfully!")
    print("=" * 70)
