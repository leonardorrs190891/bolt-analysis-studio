# MSD Framework -- PART VIII: NUMERICAL SOLVERS

**Complete Technical Reference for Bolt Analysis Studio**

**Authors:** L. Ribeiro, D. Carvalho, S.C. Naves, T. Santos, V. Marques, G. Arruda
**Institution:** LTAD/UFU -- Tribology and Wear Technology Laboratory, Federal University of Uberlandia
**Project:** Petrobras R&D -- Bolted Flange Joint Integrity

---

**Abstract.** This Part presents the five time integration methods implemented in the Bolt Analysis Studio for solving the second-order dynamic equation of motion of the bolted joint MSD system. The methods range from the unconditionally stable implicit Newmark-$\beta$ method (Newmark, 1959) -- the workhorse for most analyses -- through the numerically dissipative HHT-$\alpha$ method (Hilber, Hughes, & Taylor, 1977) for stiff contact problems, the explicit Central Difference method for high-frequency response, Modal Superposition for efficient linear analysis, and the fourth-order Runge-Kutta method for general nonlinear state-space systems. For each method, we provide the governing equations, stability conditions, parameter selection guidance, and implementation considerations specific to bolted joint dynamics. Extended treatment of the Rayleigh damping model, force excitation functions, and the nonlinear Newton-Raphson solver is provided in Part XII.

---

## 37. Governing Equations and Problem Formulation

### 37.1 Complete System of Equations

The bolted joint MSD system is governed by the second-order ordinary differential equation (Chopra, 2012; Bathe, 1996):

$$[M]\{\ddot{u}\} + [C]\{\dot{u}\} + [K]\{u\} = \{F_{ext}(t)\} + \{F_{tribo}(u, \dot{u}, \text{state})\}$$

**Expanded Form for Each DOF i:**

$$m_i \ddot{u}_i + \sum_{j=1}^{n} c_{ij} \dot{u}_j + \sum_{j=1}^{n} k_{ij} u_j = F_{ext,i}(t) + F_{tribo,i}$$

**State-Space Formulation:**

Converting to first-order system by introducing velocity as state variable:

$$\{y\} = \begin{Bmatrix} \{u\} \\ \{\dot{u}\} \end{Bmatrix}$$

$$\{\dot{y}\} = \begin{bmatrix} [0] & [I] \\ -[M]^{-1}[K] & -[M]^{-1}[C] \end{bmatrix} \{y\} + \begin{Bmatrix} \{0\} \\ [M]^{-1}\{F\} \end{Bmatrix}$$

Or in compact form:

$$\{\dot{y}\} = [A]\{y\} + \{B(t)\}$$

Where:
- [A] = System matrix (2n × 2n)
- {B(t)} = Input vector including external and tribological forces

### 37.2 Nonlinearity Sources

The system exhibits nonlinearity from multiple sources:

| Source | Type | Mathematical Expression | When Significant |
|--------|------|------------------------|------------------|
| **Gasket** | Material | k_g = k_g(δ) nonlinear curve | Always (large compression) |
| **Friction** | State-dependent | F_f = f(v, z, μ(N)) | During slip |
| **Contact** | Geometric | k_c = 0 if separated | Near separation |
| **Wear** | Time-varying | Geometry changes with wear | Long-term simulation |
| **Thread slip** | Discontinuous | Stick-slip transitions | During loosening |

### 37.3 Problem Classification

**For Linear Analysis (small amplitude, no loosening):**
- Constant [M], [C], [K]
- Linear superposition valid
- Modal analysis applicable
- Direct time integration or modal methods

**For Nonlinear Analysis (loosening, large amplitude):**
- [K] updates required (gasket, contact)
- {F_tribo} is function of state
- Newton-Raphson iteration within time step
- Adaptive time stepping recommended

---

## 38. Newmark-β Time Integration Method

### 38.1 Method Overview

The Newmark-β method is an implicit time integration scheme widely used for structural dynamics. It is unconditionally stable for appropriate parameter choices.

**Newmark Assumptions:**

$$u_{n+1} = u_n + \Delta t \dot{u}_n + \frac{\Delta t^2}{2}\left[(1-2\beta)\ddot{u}_n + 2\beta\ddot{u}_{n+1}\right]$$

$$\dot{u}_{n+1} = \dot{u}_n + \Delta t\left[(1-\gamma)\ddot{u}_n + \gamma\ddot{u}_{n+1}\right]$$

**Parameter Selection:**

| Parameters | Method Name | Stability | Accuracy | Numerical Damping |
|-----------|-------------|-----------|----------|-------------------|
| β = 1/4, γ = 1/2 | Average Acceleration | Unconditional | O(Δt²) | None |
| β = 1/6, γ = 1/2 | Linear Acceleration | Conditional | O(Δt²) | None |
| β = 1/4, γ = 1/2 + α | Average + Damping | Unconditional | O(Δt) | Controlled |

**Recommended for Bolted Joints:** β = 1/4, γ = 1/2 (unconditional stability, no numerical damping)

### 38.2 Newmark-β Algorithm

```
ALGORITHM: Newmark-β Time Integration
═══════════════════════════════════════

INPUT:
  [M], [C], [K]           - System matrices
  {F(t)}                  - Force function
  {u₀}, {v₀}, {a₀}       - Initial conditions
  Δt                      - Time step
  β, γ                    - Newmark parameters
  t_end                   - End time

OUTPUT:
  {u(t)}, {v(t)}, {a(t)} - Time histories

INITIALIZATION:
  1. Compute effective stiffness matrix:
     [K_eff] = [K] + (γ/(β·Δt))[C] + (1/(β·Δt²))[M]
  
  2. Factorize [K_eff] (LU decomposition for efficiency)
  
  3. Compute initial acceleration:
     {a₀} = [M]⁻¹({F(0)} - [C]{v₀} - [K]{u₀})

TIME STEPPING LOOP:
  FOR n = 0, 1, 2, ... until t_n > t_end:
  
    4. Compute effective force:
       {F_eff} = {F(t_{n+1})} 
                 + [M]((1/(β·Δt²)){u_n} + (1/(β·Δt)){v_n} + (1/(2β) - 1){a_n})
                 + [C]((γ/(β·Δt)){u_n} + (γ/β - 1){v_n} + (Δt/2)(γ/β - 2){a_n})
    
    5. Solve for displacement:
       [K_eff]{u_{n+1}} = {F_eff}
    
    6. Compute acceleration:
       {a_{n+1}} = (1/(β·Δt²))({u_{n+1}} - {u_n}) - (1/(β·Δt)){v_n} - (1/(2β) - 1){a_n}
    
    7. Compute velocity:
       {v_{n+1}} = {v_n} + Δt((1-γ){a_n} + γ{a_{n+1}})
    
    8. Update time: t_{n+1} = t_n + Δt
    
    9. Store results
    
  END FOR

RETURN {u(t)}, {v(t)}, {a(t)}
```

### 38.3 Python Implementation

```python
import numpy as np
from scipy.linalg import lu_factor, lu_solve
from typing import Tuple, Callable, List, Dict
from dataclasses import dataclass


@dataclass
class NewmarkParameters:
    """Newmark-β integration parameters"""
    beta: float = 0.25       # Average acceleration
    gamma: float = 0.5       # No numerical damping
    
    def validate(self):
        """Check unconditional stability condition"""
        if self.gamma < 0.5:
            raise ValueError("γ < 0.5 leads to unstable integration")
        if self.beta < self.gamma / 2:
            raise ValueError("β < γ/2 leads to conditional stability")


class NewmarkBetaSolver:
    """
    Newmark-β time integration solver for structural dynamics.
    
    Solves: [M]{ü} + [C]{u̇} + [K]{u} = {F(t)}
    
    Features:
    - Unconditionally stable for β ≥ γ/2 ≥ 1/4
    - Second-order accurate for γ = 1/2
    - Efficient LU factorization reuse
    - Support for nonlinear forces
    """
    
    def __init__(self,
                 M: np.ndarray,
                 C: np.ndarray,
                 K: np.ndarray,
                 params: NewmarkParameters = None):
        """
        Initialize Newmark solver.
        
        Args:
            M: Mass matrix (n × n)
            C: Damping matrix (n × n)
            K: Stiffness matrix (n × n)
            params: Newmark parameters
        """
        self.M = M.copy()
        self.C = C.copy()
        self.K = K.copy()
        self.n_dof = M.shape[0]
        
        self.params = params if params else NewmarkParameters()
        self.params.validate()
        
        self.K_eff = None
        self.K_eff_lu = None
        self._compute_effective_stiffness()
        
    def _compute_effective_stiffness(self, dt: float = 0.001):
        """Compute and factorize effective stiffness matrix"""
        beta = self.params.beta
        gamma = self.params.gamma
        
        a0 = 1.0 / (beta * dt**2)
        a1 = gamma / (beta * dt)
        
        self.K_eff = self.K + a1 * self.C + a0 * self.M
        self.K_eff_lu = lu_factor(self.K_eff)
        self._dt_cached = dt
        
    def solve(self,
              F_func: Callable[[float], np.ndarray],
              u0: np.ndarray,
              v0: np.ndarray,
              dt: float,
              t_end: float,
              F_tribo_func: Callable = None,
              output_interval: int = 1) -> Dict:
        """
        Perform time integration.
        
        Args:
            F_func: External force function F(t) -> ndarray
            u0: Initial displacement
            v0: Initial velocity
            dt: Time step
            t_end: End time
            F_tribo_func: Optional tribological force function(u, v, t) -> ndarray
            output_interval: Store results every N steps
        
        Returns:
            Dictionary with time histories
        """
        # Update effective stiffness if dt changed
        if not hasattr(self, '_dt_cached') or abs(dt - self._dt_cached) > 1e-12:
            self._compute_effective_stiffness(dt)
        
        beta = self.params.beta
        gamma = self.params.gamma
        
        # Newmark coefficients
        a0 = 1.0 / (beta * dt**2)
        a1 = gamma / (beta * dt)
        a2 = 1.0 / (beta * dt)
        a3 = 1.0 / (2 * beta) - 1.0
        a4 = gamma / beta - 1.0
        a5 = dt / 2 * (gamma / beta - 2.0)
        a6 = dt * (1.0 - gamma)
        a7 = gamma * dt
        
        # Initialize
        u = u0.copy()
        v = v0.copy()
        
        # Initial force
        F0 = F_func(0.0)
        if F_tribo_func is not None:
            F0 = F0 + F_tribo_func(u, v, 0.0)
        
        # Initial acceleration
        a = np.linalg.solve(self.M, F0 - self.C @ v - self.K @ u)
        
        # Storage
        n_steps = int(t_end / dt) + 1
        n_stored = (n_steps - 1) // output_interval + 1
        
        results = {
            'time': np.zeros(n_stored),
            'displacement': np.zeros((n_stored, self.n_dof)),
            'velocity': np.zeros((n_stored, self.n_dof)),
            'acceleration': np.zeros((n_stored, self.n_dof)),
            'force': np.zeros((n_stored, self.n_dof))
        }
        
        # Store initial state
        results['time'][0] = 0.0
        results['displacement'][0] = u
        results['velocity'][0] = v
        results['acceleration'][0] = a
        results['force'][0] = F0
        
        store_idx = 1
        t = 0.0
        
        # Time stepping
        for step in range(1, n_steps):
            t = step * dt
            
            # External force at t_{n+1}
            F_ext = F_func(t)
            
            # Effective force
            F_eff = F_ext.copy()
            F_eff += self.M @ (a0 * u + a2 * v + a3 * a)
            F_eff += self.C @ (a1 * u + a4 * v + a5 * a)
            
            # Solve for new displacement
            u_new = lu_solve(self.K_eff_lu, F_eff)
            
            # Compute new acceleration and velocity
            a_new = a0 * (u_new - u) - a2 * v - a3 * a
            v_new = v + a6 * a + a7 * a_new
            
            # Add tribological forces (if nonlinear)
            if F_tribo_func is not None:
                F_tribo = F_tribo_func(u_new, v_new, t)
                
                # Correct with tribological force (simplified - could iterate)
                F_eff_corrected = F_eff + F_tribo
                u_new = lu_solve(self.K_eff_lu, F_eff_corrected)
                a_new = a0 * (u_new - u) - a2 * v - a3 * a
                v_new = v + a6 * a + a7 * a_new
            
            # Update
            u = u_new
            v = v_new
            a = a_new
            
            # Store results
            if step % output_interval == 0:
                results['time'][store_idx] = t
                results['displacement'][store_idx] = u
                results['velocity'][store_idx] = v
                results['acceleration'][store_idx] = a
                results['force'][store_idx] = F_ext + (F_tribo if F_tribo_func else 0)
                store_idx += 1
        
        # Trim arrays if needed
        for key in results:
            results[key] = results[key][:store_idx]
        
        return results
```

### 38.4 Stability Analysis

**Unconditional Stability Condition:**

For the Newmark method to be unconditionally stable:

$$\gamma \geq \frac{1}{2} \quad \text{and} \quad \beta \geq \frac{\gamma}{2}$$

**Spectral Radius for Single DOF:**

$$\rho = \max|\lambda_i| \quad \text{where } \lambda_i \text{ are eigenvalues of amplification matrix}$$

For β = 1/4, γ = 1/2:
$$\rho = 1 \quad \text{(no numerical damping)}$$

**Time Step Selection Guidelines:**

| Application | Recommended Δt | Criterion |
|-------------|---------------|-----------|
| Low frequency (< 10 Hz) | T/20 to T/50 | T = 1/f_max |
| Medium frequency (10-100 Hz) | T/50 to T/100 | Accuracy |
| High frequency (> 100 Hz) | T/100 to T/200 | Contact dynamics |
| Loosening analysis | 1/(20 × f_loading) | Capture slip events |

---

## 39. HHT-α Method (Hilber-Hughes-Taylor)

### 39.1 Method Description

The HHT-α method is a modification of Newmark that introduces controllable numerical damping to suppress high-frequency oscillations while maintaining accuracy at lower frequencies.

**Modified Equation of Motion:**

$$[M]\{\ddot{u}_{n+1}\} + (1+\alpha)[C]\{\dot{u}_{n+1}\} - \alpha[C]\{\dot{u}_n\} + (1+\alpha)[K]\{u_{n+1}\} - \alpha[K]\{u_n\} = (1+\alpha)\{F_{n+1}\} - \alpha\{F_n\}$$

**Parameter Relationships:**

$$\alpha \in [-1/3, 0]$$
$$\gamma = \frac{1 - 2\alpha}{2}$$
$$\beta = \frac{(1 - \alpha)^2}{4}$$

**Typical Values:**
- α = 0: Reduces to Newmark (no damping)
- α = -0.05: Mild damping
- α = -0.1: Moderate damping
- α = -0.3: Strong damping (maximum recommended)

### 39.2 HHT-α Implementation

```python
@dataclass
class HHTParameters:
    """HHT-α integration parameters"""
    alpha: float = -0.05    # Damping parameter [-1/3, 0]
    
    @property
    def gamma(self) -> float:
        return (1 - 2 * self.alpha) / 2
    
    @property
    def beta(self) -> float:
        return (1 - self.alpha)**2 / 4
    
    def validate(self):
        if self.alpha < -1/3 or self.alpha > 0:
            raise ValueError("α must be in [-1/3, 0]")


class HHTAlphaSolver:
    """
    Hilber-Hughes-Taylor (HHT-α) time integration solver.
    
    Advantages over Newmark:
    - Controllable high-frequency damping
    - Better handling of contact/impact
    - Maintains second-order accuracy
    
    Good for bolted joint analysis with stick-slip.
    """
    
    def __init__(self,
                 M: np.ndarray,
                 C: np.ndarray,
                 K: np.ndarray,
                 params: HHTParameters = None):
        """Initialize HHT solver"""
        self.M = M.copy()
        self.C = C.copy()
        self.K = K.copy()
        self.n_dof = M.shape[0]
        
        self.params = params if params else HHTParameters()
        self.params.validate()
        
    def solve(self,
              F_func: Callable[[float], np.ndarray],
              u0: np.ndarray,
              v0: np.ndarray,
              dt: float,
              t_end: float,
              F_tribo_func: Callable = None) -> Dict:
        """
        Perform HHT-α time integration.
        
        Args:
            F_func: External force function
            u0: Initial displacement
            v0: Initial velocity
            dt: Time step
            t_end: End time
            F_tribo_func: Optional tribological force function
        
        Returns:
            Dictionary with time histories
        """
        alpha = self.params.alpha
        beta = self.params.beta
        gamma = self.params.gamma
        
        # HHT coefficients
        a0 = 1.0 / (beta * dt**2)
        a1 = gamma / (beta * dt)
        a2 = 1.0 / (beta * dt)
        a3 = 1.0 / (2 * beta) - 1.0
        a4 = gamma / beta - 1.0
        a5 = dt / 2 * (gamma / beta - 2.0)
        a6 = dt * (1.0 - gamma)
        a7 = gamma * dt
        
        # Effective stiffness (includes HHT modification)
        K_eff = (1 + alpha) * self.K + (1 + alpha) * a1 * self.C + a0 * self.M
        K_eff_lu = lu_factor(K_eff)
        
        # Initialize
        u = u0.copy()
        v = v0.copy()
        
        F0 = F_func(0.0)
        a = np.linalg.solve(self.M, F0 - self.C @ v - self.K @ u)
        
        # Storage
        n_steps = int(t_end / dt) + 1
        results = {
            'time': np.zeros(n_steps),
            'displacement': np.zeros((n_steps, self.n_dof)),
            'velocity': np.zeros((n_steps, self.n_dof)),
            'acceleration': np.zeros((n_steps, self.n_dof))
        }
        
        results['time'][0] = 0.0
        results['displacement'][0] = u
        results['velocity'][0] = v
        results['acceleration'][0] = a
        
        F_prev = F0.copy()
        
        for step in range(1, n_steps):
            t = step * dt
            
            F_curr = F_func(t)
            
            # HHT effective force
            F_eff = (1 + alpha) * F_curr - alpha * F_prev
            F_eff += self.M @ (a0 * u + a2 * v + a3 * a)
            F_eff += (1 + alpha) * self.C @ (a1 * u + a4 * v + a5 * a)
            F_eff -= alpha * self.C @ v
            F_eff += alpha * self.K @ u
            
            # Solve
            u_new = lu_solve(K_eff_lu, F_eff)
            
            # Update acceleration and velocity
            a_new = a0 * (u_new - u) - a2 * v - a3 * a
            v_new = v + a6 * a + a7 * a_new
            
            # Tribological forces
            if F_tribo_func is not None:
                F_tribo = F_tribo_func(u_new, v_new, t)
                F_eff_corr = F_eff + (1 + alpha) * F_tribo
                u_new = lu_solve(K_eff_lu, F_eff_corr)
                a_new = a0 * (u_new - u) - a2 * v - a3 * a
                v_new = v + a6 * a + a7 * a_new
            
            # Store
            results['time'][step] = t
            results['displacement'][step] = u_new
            results['velocity'][step] = v_new
            results['acceleration'][step] = a_new
            
            # Update
            u = u_new
            v = v_new
            a = a_new
            F_prev = F_curr
        
        return results
```

---

## 40. Runge-Kutta Methods (RK4, RK45)

### 40.1 Fourth-Order Runge-Kutta (RK4)

For the first-order system:

$$\{\dot{y}\} = \{f(t, y)\}$$

**RK4 Algorithm:**

$$k_1 = f(t_n, y_n)$$
$$k_2 = f(t_n + \frac{\Delta t}{2}, y_n + \frac{\Delta t}{2}k_1)$$
$$k_3 = f(t_n + \frac{\Delta t}{2}, y_n + \frac{\Delta t}{2}k_2)$$
$$k_4 = f(t_n + \Delta t, y_n + \Delta t \cdot k_3)$$

$$y_{n+1} = y_n + \frac{\Delta t}{6}(k_1 + 2k_2 + 2k_3 + k_4)$$

### 40.2 Implementation

```python
class RungeKutta4Solver:
    """
    Fourth-order Runge-Kutta solver for MSD systems.
    
    Converts second-order ODE to first-order state-space form.
    
    Advantages:
    - Self-starting (no need for special first step)
    - Good for smooth problems
    - Easy to implement
    
    Disadvantages:
    - Conditionally stable
    - May require small time steps
    - Less efficient than implicit methods for stiff systems
    """
    
    def __init__(self,
                 M: np.ndarray,
                 C: np.ndarray,
                 K: np.ndarray):
        """Initialize RK4 solver"""
        self.M = M
        self.C = C
        self.K = K
        self.n_dof = M.shape[0]
        
        # Precompute M inverse
        self.M_inv = np.linalg.inv(M)
        
    def _derivatives(self, t: float, y: np.ndarray, 
                     F_func: Callable, F_tribo_func: Callable = None) -> np.ndarray:
        """
        Compute state derivatives.
        
        State: y = [u, v]
        Derivatives: dy/dt = [v, a]
        
        Where a = M^(-1)(F - Cv - Ku)
        """
        u = y[:self.n_dof]
        v = y[self.n_dof:]
        
        F = F_func(t)
        if F_tribo_func is not None:
            F = F + F_tribo_func(u, v, t)
        
        a = self.M_inv @ (F - self.C @ v - self.K @ u)
        
        return np.concatenate([v, a])
    
    def solve(self,
              F_func: Callable[[float], np.ndarray],
              u0: np.ndarray,
              v0: np.ndarray,
              dt: float,
              t_end: float,
              F_tribo_func: Callable = None) -> Dict:
        """
        Perform RK4 integration.
        
        Args:
            F_func: External force function
            u0: Initial displacement
            v0: Initial velocity
            dt: Time step
            t_end: End time
            F_tribo_func: Optional tribological force function
        
        Returns:
            Dictionary with time histories
        """
        n_steps = int(t_end / dt) + 1
        
        results = {
            'time': np.zeros(n_steps),
            'displacement': np.zeros((n_steps, self.n_dof)),
            'velocity': np.zeros((n_steps, self.n_dof))
        }
        
        # Initial state
        y = np.concatenate([u0, v0])
        
        results['time'][0] = 0.0
        results['displacement'][0] = u0
        results['velocity'][0] = v0
        
        for step in range(1, n_steps):
            t = (step - 1) * dt
            
            # RK4 stages
            k1 = self._derivatives(t, y, F_func, F_tribo_func)
            k2 = self._derivatives(t + dt/2, y + dt/2 * k1, F_func, F_tribo_func)
            k3 = self._derivatives(t + dt/2, y + dt/2 * k2, F_func, F_tribo_func)
            k4 = self._derivatives(t + dt, y + dt * k3, F_func, F_tribo_func)
            
            # Update state
            y = y + dt/6 * (k1 + 2*k2 + 2*k3 + k4)
            
            # Store results
            results['time'][step] = t + dt
            results['displacement'][step] = y[:self.n_dof]
            results['velocity'][step] = y[self.n_dof:]
        
        return results
```

---

## 41. Nonlinear Newton-Raphson Iteration

### 41.1 Residual Formulation

For nonlinear systems, the equilibrium equation at time step n+1:

$$\{R(u_{n+1})\} = \{F_{ext}\} + \{F_{tribo}\} - [M]\{\ddot{u}_{n+1}\} - [C]\{\dot{u}_{n+1}\} - \{F_{int}(u_{n+1})\}$$

where {F_int} = [K(u)]{u} for nonlinear stiffness.

**Goal:** Find {u_{n+1}} such that ||{R}|| < tolerance

### 41.2 Newton-Raphson Algorithm

```
ALGORITHM: Newton-Raphson Iteration within Time Step
═══════════════════════════════════════════════════════

INPUT:
  {u_n}, {v_n}, {a_n}     - State at time t_n
  {F_{n+1}}               - External force at t_{n+1}
  tolerance               - Convergence tolerance
  max_iterations          - Maximum iterations

OUTPUT:
  {u_{n+1}}, {v_{n+1}}, {a_{n+1}} - Converged state

INITIALIZATION:
  1. Predictor (Newmark):
     {u_{n+1}^(0)} = {u_n} + Δt{v_n} + (0.5-β)Δt²{a_n}
     {v_{n+1}^(0)} = {v_n} + (1-γ)Δt{a_n}

ITERATION LOOP:
  FOR iteration k = 0, 1, 2, ... max_iterations:
    
    2. Compute internal force:
       {F_int^(k)} = [K(u^(k))]{u^(k)}
    
    3. Compute tribological force:
       {F_tribo^(k)} = f(u^(k), v^(k))
    
    4. Compute residual:
       {R^(k)} = {F_{n+1}} + {F_tribo^(k)} - [M]{a^(k)} - [C]{v^(k)} - {F_int^(k)}
    
    5. Check convergence:
       IF ||{R^(k)}|| / ||{F_{n+1}}|| < tolerance:
         CONVERGED - EXIT LOOP
    
    6. Compute tangent stiffness:
       [K_T^(k)] = [K_eff] + ∂{F_tribo}/∂{u} + ∂{F_tribo}/∂{v} × (γ/(βΔt))
    
    7. Solve for correction:
       [K_T^(k)]{Δu^(k)} = {R^(k)}
    
    8. Update:
       {u^(k+1)} = {u^(k)} + {Δu^(k)}
       {a^(k+1)} = (1/(βΔt²))({u^(k+1)} - {u_n}) - (1/(βΔt)){v_n} - (1/(2β)-1){a_n}
       {v^(k+1)} = {v_n} + (1-γ)Δt{a_n} + γΔt{a^(k+1)}
    
  END FOR

  IF NOT CONVERGED:
    WARNING: Did not converge in max_iterations
    Consider: reducing Δt, relaxing tolerance, checking model

RETURN {u_{n+1}}, {v_{n+1}}, {a_{n+1}}
```

### 41.3 Implementation

```python
class NonlinearNewtonRaphsonSolver:
    """
    Nonlinear Newton-Raphson solver with Newmark time integration.
    
    Handles:
    - Nonlinear stiffness (gasket)
    - State-dependent friction (LuGre)
    - Contact opening/closing
    - Material nonlinearity
    """
    
    def __init__(self,
                 M: np.ndarray,
                 C: np.ndarray,
                 get_K: Callable[[np.ndarray], np.ndarray],
                 get_F_int: Callable[[np.ndarray], np.ndarray],
                 params: NewmarkParameters = None,
                 tol_residual: float = 1e-6,
                 tol_displacement: float = 1e-6,
                 max_iterations: int = 20):
        """
        Initialize nonlinear solver.
        
        Args:
            M: Mass matrix
            C: Damping matrix
            get_K: Function returning tangent stiffness K(u)
            get_F_int: Function returning internal force F_int(u)
            params: Newmark parameters
            tol_residual: Residual convergence tolerance
            tol_displacement: Displacement convergence tolerance
            max_iterations: Maximum Newton iterations
        """
        self.M = M
        self.C = C
        self.get_K = get_K
        self.get_F_int = get_F_int
        self.n_dof = M.shape[0]
        
        self.params = params if params else NewmarkParameters()
        self.tol_R = tol_residual
        self.tol_u = tol_displacement
        self.max_iter = max_iterations
        
        # Statistics
        self.iteration_history = []
        
    def _compute_effective_stiffness(self, K: np.ndarray, dt: float) -> np.ndarray:
        """Compute effective stiffness matrix"""
        beta = self.params.beta
        gamma = self.params.gamma
        
        a0 = 1.0 / (beta * dt**2)
        a1 = gamma / (beta * dt)
        
        K_eff = K + a1 * self.C + a0 * self.M
        return K_eff
    
    def _newton_iteration(self,
                          u_pred: np.ndarray,
                          v_pred: np.ndarray,
                          u_n: np.ndarray,
                          v_n: np.ndarray,
                          a_n: np.ndarray,
                          F_ext: np.ndarray,
                          F_tribo_func: Callable,
                          dt: float,
                          t: float) -> Tuple[np.ndarray, np.ndarray, np.ndarray, int, bool]:
        """
        Perform Newton-Raphson iteration for one time step.
        
        Returns:
            (u_new, v_new, a_new, n_iterations, converged)
        """
        beta = self.params.beta
        gamma = self.params.gamma
        
        a0 = 1.0 / (beta * dt**2)
        a1 = gamma / (beta * dt)
        a2 = 1.0 / (beta * dt)
        a3 = 1.0 / (2 * beta) - 1.0
        a6 = dt * (1.0 - gamma)
        a7 = gamma * dt
        
        u = u_pred.copy()
        v = v_pred.copy()
        
        # Initial acceleration
        a = a0 * (u - u_n) - a2 * v_n - a3 * a_n
        
        converged = False
        
        for iteration in range(self.max_iter):
            # Internal force
            F_int = self.get_F_int(u)
            
            # Tribological force
            F_tribo = F_tribo_func(u, v, t) if F_tribo_func else np.zeros(self.n_dof)
            
            # Residual
            R = F_ext + F_tribo - self.M @ a - self.C @ v - F_int
            
            # Check convergence
            R_norm = np.linalg.norm(R)
            F_norm = np.linalg.norm(F_ext) + 1e-10
            
            if R_norm / F_norm < self.tol_R:
                converged = True
                break
            
            # Tangent stiffness
            K = self.get_K(u)
            K_eff = self._compute_effective_stiffness(K, dt)
            
            # Solve for correction
            try:
                du = np.linalg.solve(K_eff, R)
            except np.linalg.LinAlgError:
                print(f"Warning: Singular matrix at iteration {iteration}")
                break
            
            # Check displacement convergence
            u_norm = np.linalg.norm(u) + 1e-10
            if np.linalg.norm(du) / u_norm < self.tol_u:
                converged = True
                break
            
            # Update
            u = u + du
            a = a0 * (u - u_n) - a2 * v_n - a3 * a_n
            v = v_n + a6 * a_n + a7 * a
        
        return u, v, a, iteration + 1, converged
    
    def solve(self,
              F_func: Callable[[float], np.ndarray],
              u0: np.ndarray,
              v0: np.ndarray,
              dt: float,
              t_end: float,
              F_tribo_func: Callable = None) -> Dict:
        """
        Solve nonlinear dynamic problem.
        
        Returns:
            Dictionary with time histories and convergence info
        """
        beta = self.params.beta
        gamma = self.params.gamma
        
        n_steps = int(t_end / dt) + 1
        
        results = {
            'time': np.zeros(n_steps),
            'displacement': np.zeros((n_steps, self.n_dof)),
            'velocity': np.zeros((n_steps, self.n_dof)),
            'acceleration': np.zeros((n_steps, self.n_dof)),
            'iterations': [],
            'converged': []
        }
        
        # Initial conditions
        u = u0.copy()
        v = v0.copy()
        F0 = F_func(0.0)
        F_int0 = self.get_F_int(u)
        a = np.linalg.solve(self.M, F0 - self.C @ v - F_int0)
        
        results['time'][0] = 0.0
        results['displacement'][0] = u
        results['velocity'][0] = v
        results['acceleration'][0] = a
        
        for step in range(1, n_steps):
            t = step * dt
            
            # Predictor
            u_pred = u + dt * v + (0.5 - beta) * dt**2 * a
            v_pred = v + (1 - gamma) * dt * a
            
            # External force
            F_ext = F_func(t)
            
            # Newton iteration
            u_new, v_new, a_new, n_iter, conv = self._newton_iteration(
                u_pred, v_pred, u, v, a, F_ext, F_tribo_func, dt, t
            )
            
            # Store results
            results['time'][step] = t
            results['displacement'][step] = u_new
            results['velocity'][step] = v_new
            results['acceleration'][step] = a_new
            results['iterations'].append(n_iter)
            results['converged'].append(conv)
            
            if not conv:
                print(f"Warning: Step {step} did not converge after {n_iter} iterations")
            
            # Update
            u = u_new
            v = v_new
            a = a_new
        
        return results
```

---

## 42. State Update Algorithms

### 42.1 Complete State Update Sequence

After solving for displacements and velocities, all state variables must be updated:

```python
class StateUpdateManager:
    """
    Manages state updates for all contact elements after each time step.
    
    State variables tracked:
    - Friction states (LuGre z, Dahl F)
    - Slip states (stick/partial/gross)
    - Wear accumulation
    - Friction coefficient evolution
    - Loosening angle
    - Preload
    - Cycle count
    """
    
    def __init__(self,
                 contacts: List['BaseContactElement'],
                 thread_element: 'ThreadContactElement',
                 k_bolt: float,
                 k_member: float):
        """
        Initialize state manager.
        
        Args:
            contacts: List of all contact elements
            thread_element: Thread contact element (for loosening)
            k_bolt: Bolt stiffness
            k_member: Member stiffness
        """
        self.contacts = contacts
        self.thread = thread_element
        self.k_bolt = k_bolt
        self.k_member = k_member
        
        # Global state
        self.preload = 0.0
        self.preload_initial = 0.0
        self.cycle_count = 0
        self.total_loosening = 0.0
        
        # Loss tracking
        self.loss_rotational = 0.0
        self.loss_embedding = 0.0
        self.loss_relaxation = 0.0
        self.loss_creep = 0.0
        self.loss_wear = 0.0
        self.loss_thermal = 0.0
        
        # History
        self.preload_history = []
        self.loosening_history = []
        
    def initialize_preload(self, F_p0: float):
        """Set initial preload"""
        self.preload = F_p0
        self.preload_initial = F_p0
        self.preload_history = [F_p0]
        self.loosening_history = [0.0]
        
    def update_all_states(self,
                          u: np.ndarray,
                          v: np.ndarray,
                          F_transverse: float,
                          dt: float,
                          t: float) -> Dict:
        """
        Perform complete state update for one time step.
        
        Args:
            u: Current displacement vector
            v: Current velocity vector
            F_transverse: Current transverse force
            dt: Time step
            t: Current time
        
        Returns:
            Dictionary with update summary
        """
        results = {}
        
        # 1. Update contact states (friction, slip)
        for contact in self.contacts:
            # Extract local DOFs
            dof_map = contact.dof_indices
            u_local = u[dof_map] if len(dof_map) > 0 else np.array([])
            v_local = v[dof_map] if len(dof_map) > 0 else np.array([])
            
            # Update contact state
            contact.update_state(u_local, v_local, self.preload, dt)
        
        # 2. Compute wear at all contacts
        total_wear = 0.0
        for contact in self.contacts:
            if hasattr(contact, 'wear'):
                total_wear += contact.wear.accumulated_depth
        
        # 3. Update thread loosening
        if self.thread is not None:
            delta_theta, delta_F_rot = self.thread.compute_loosening_per_thread(
                self.preload, F_transverse, self.cycle_count, dt
            )
            self.total_loosening += delta_theta
            self.loss_rotational += delta_F_rot
        else:
            delta_theta = 0.0
            delta_F_rot = 0.0
        
        # 4. Compute embedding loss
        delta_F_embed = 0.0
        for contact in self.contacts:
            if hasattr(contact, 'compute_embedding'):
                k_sys = (self.k_bolt * self.k_member) / (self.k_bolt + self.k_member)
                delta_embed = contact.compute_preload_loss_embedding(k_sys, self.cycle_count)
                delta_F_embed += delta_embed
        self.loss_embedding = delta_F_embed
        
        # 5. Compute wear-induced loss
        k_sys = (self.k_bolt * self.k_member) / (self.k_bolt + self.k_member)
        delta_F_wear = k_sys * total_wear
        self.loss_wear = delta_F_wear
        
        # 6. Update preload
        total_loss = delta_F_rot + delta_F_embed + delta_F_wear
        self.preload = max(0, self.preload - total_loss)
        
        # 7. Check for cycle completion (zero crossing detection)
        # This would normally check transverse displacement
        
        # 8. Update COF for all contacts based on cycles
        for contact in self.contacts:
            if hasattr(contact.friction, 'get_friction_coefficient'):
                contact.friction.get_friction_coefficient(
                    velocity=0,
                    cycles=self.cycle_count,
                    pressure=contact.state.contact_pressure,
                    wear_depth=contact.wear.accumulated_depth if hasattr(contact, 'wear') else 0
                )
        
        # Store history
        self.preload_history.append(self.preload)
        self.loosening_history.append(self.total_loosening)
        
        results = {
            'preload': self.preload,
            'preload_ratio': self.preload / self.preload_initial if self.preload_initial > 0 else 0,
            'loosening_deg': np.degrees(self.total_loosening),
            'total_wear_um': total_wear * 1e6,
            'loss_rotational': self.loss_rotational,
            'loss_embedding': self.loss_embedding,
            'loss_wear': self.loss_wear,
            'cycle_count': self.cycle_count
        }
        
        return results
    
    def increment_cycle(self):
        """Increment cycle counter"""
        self.cycle_count += 1
    
    def get_preload_breakdown(self) -> Dict:
        """Get breakdown of preload loss by mechanism"""
        return {
            'initial': self.preload_initial,
            'current': self.preload,
            'total_loss': self.preload_initial - self.preload,
            'loss_rotational': self.loss_rotational,
            'loss_embedding': self.loss_embedding,
            'loss_relaxation': self.loss_relaxation,
            'loss_creep': self.loss_creep,
            'loss_wear': self.loss_wear,
            'loss_thermal': self.loss_thermal,
            'loss_rotational_pct': 100 * self.loss_rotational / max(self.preload_initial, 1),
            'loss_embedding_pct': 100 * self.loss_embedding / max(self.preload_initial, 1),
            'loss_wear_pct': 100 * self.loss_wear / max(self.preload_initial, 1)
        }
```

---

## 43. Convergence Criteria and Error Control

### 43.1 Convergence Measures

**Residual Norm:**

$$\epsilon_R = \frac{||\{R\}||}{||\{F_{ext}\}||}$$

**Displacement Increment Norm:**

$$\epsilon_u = \frac{||\{\Delta u\}||}{||\{u\}||}$$

**Energy Norm:**

$$\epsilon_E = \frac{|\{\Delta u\}^T\{R\}|}{||\{u\}^T\{F_{ext}\}||}$$

**Typical Tolerances:**

| Application | Residual tol | Displacement tol | Notes |
|-------------|-------------|------------------|-------|
| Static analysis | 10⁻⁶ | 10⁻⁶ | High precision |
| Dynamic analysis | 10⁻⁴ | 10⁻⁴ | Balanced |
| Loosening analysis | 10⁻⁵ | 10⁻⁵ | Capture small rotations |
| Quick estimate | 10⁻³ | 10⁻³ | Design iteration |

### 43.2 Implementation

```python
@dataclass
class ConvergenceCriteria:
    """Convergence criteria for nonlinear solver"""
    
    tol_residual: float = 1e-5
    tol_displacement: float = 1e-5
    tol_energy: float = 1e-8
    max_iterations: int = 20
    
    # Optional: relative vs absolute
    use_relative_residual: bool = True
    use_relative_displacement: bool = True
    
    # Minimum reference values
    min_force_ref: float = 1.0
    min_disp_ref: float = 1e-12
    
    def check_convergence(self,
                          R: np.ndarray,
                          du: np.ndarray,
                          u: np.ndarray,
                          F: np.ndarray) -> Tuple[bool, Dict]:
        """
        Check all convergence criteria.
        
        Args:
            R: Residual vector
            du: Displacement increment
            u: Current displacement
            F: External force
        
        Returns:
            (converged, details_dict)
        """
        # Residual criterion
        R_norm = np.linalg.norm(R)
        if self.use_relative_residual:
            F_ref = max(np.linalg.norm(F), self.min_force_ref)
            eps_R = R_norm / F_ref
        else:
            eps_R = R_norm
        
        conv_R = eps_R < self.tol_residual
        
        # Displacement criterion
        du_norm = np.linalg.norm(du)
        if self.use_relative_displacement:
            u_ref = max(np.linalg.norm(u), self.min_disp_ref)
            eps_u = du_norm / u_ref
        else:
            eps_u = du_norm
        
        conv_u = eps_u < self.tol_displacement
        
        # Energy criterion
        energy = abs(np.dot(du, R))
        u_F = abs(np.dot(u, F)) + 1e-10
        eps_E = energy / u_F
        conv_E = eps_E < self.tol_energy
        
        # Overall convergence
        converged = conv_R and conv_u
        
        details = {
            'converged': converged,
            'residual_norm': R_norm,
            'residual_error': eps_R,
            'residual_converged': conv_R,
            'displacement_norm': du_norm,
            'displacement_error': eps_u,
            'displacement_converged': conv_u,
            'energy_error': eps_E,
            'energy_converged': conv_E
        }
        
        return converged, details
```

---

## 44. Adaptive Time Stepping

### 44.1 Error Estimation

For adaptive time stepping, estimate local truncation error:

$$\tau = ||u_{n+1}^{(2)} - u_{n+1}^{(1)}||$$

where superscripts indicate different order methods.

### 44.2 Time Step Adjustment

```python
class AdaptiveTimeStepController:
    """
    Adaptive time step controller for transient analysis.
    
    Adjusts time step based on:
    - Local truncation error
    - Convergence behavior
    - Contact state changes
    - Slip transitions
    """
    
    def __init__(self,
                 dt_initial: float = 0.001,
                 dt_min: float = 1e-6,
                 dt_max: float = 0.01,
                 safety_factor: float = 0.9,
                 error_tolerance: float = 1e-4,
                 max_increase: float = 2.0,
                 max_decrease: float = 0.5):
        """
        Initialize adaptive controller.
        
        Args:
            dt_initial: Initial time step
            dt_min: Minimum allowed time step
            dt_max: Maximum allowed time step
            safety_factor: Safety factor for step adjustment
            error_tolerance: Target error tolerance
            max_increase: Maximum factor for step increase
            max_decrease: Minimum factor for step decrease
        """
        self.dt = dt_initial
        self.dt_min = dt_min
        self.dt_max = dt_max
        self.safety = safety_factor
        self.tol = error_tolerance
        self.max_inc = max_increase
        self.max_dec = max_decrease
        
        # History
        self.dt_history = [dt_initial]
        self.error_history = []
        
    def estimate_error(self,
                       u_half: np.ndarray,
                       u_full: np.ndarray,
                       order: int = 2) -> float:
        """
        Estimate error using Richardson extrapolation.
        
        Args:
            u_half: Solution with dt/2 (two steps)
            u_full: Solution with dt (one step)
            order: Order of the method
        
        Returns:
            Error estimate
        """
        # Richardson extrapolation error estimate
        error = np.linalg.norm(u_half - u_full) / (2**order - 1)
        return error
    
    def compute_new_step(self,
                         error: float,
                         n_iterations: int = None,
                         contact_changed: bool = False) -> float:
        """
        Compute new time step based on error and convergence.
        
        Args:
            error: Current error estimate
            n_iterations: Number of Newton iterations (if applicable)
            contact_changed: Whether contact state changed
        
        Returns:
            New time step
        """
        self.error_history.append(error)
        
        # Basic error-based adjustment
        if error > 0:
            ratio = (self.tol / error) ** 0.5  # For 2nd order method
        else:
            ratio = self.max_inc
        
        # Apply safety factor
        ratio *= self.safety
        
        # Limit adjustment
        ratio = min(ratio, self.max_inc)
        ratio = max(ratio, self.max_dec)
        
        # Additional adjustments
        if n_iterations is not None:
            # Reduce step if many iterations needed
            if n_iterations > 10:
                ratio = min(ratio, 0.8)
            elif n_iterations < 3:
                ratio = min(ratio * 1.1, self.max_inc)
        
        if contact_changed:
            # Reduce step at contact transitions
            ratio = min(ratio, 0.5)
        
        # Compute new step
        dt_new = self.dt * ratio
        
        # Apply limits
        dt_new = max(dt_new, self.dt_min)
        dt_new = min(dt_new, self.dt_max)
        
        self.dt = dt_new
        self.dt_history.append(dt_new)
        
        return dt_new
    
    def reject_step(self) -> float:
        """
        Reject current step and compute reduced time step.
        
        Returns:
            Reduced time step
        """
        self.dt *= self.max_dec
        self.dt = max(self.dt, self.dt_min)
        return self.dt
```

---

## References -- Part VIII

1. Bathe, K.-J. (1996). *Finite Element Procedures*. Prentice Hall. -- Comprehensive treatment of direct time integration methods (Newmark, HHT, Central Difference), nonlinear solution strategies (Newton-Raphson), and convergence criteria. Chapters 9--10 are directly applicable.

2. Chopra, A.K. (2012). *Dynamics of Structures: Theory and Applications to Earthquake Engineering*, 4th ed. Prentice Hall. ISBN: 978-0-13-285803-8. -- Accessible introduction to Newmark-$\beta$ method, modal superposition, and Rayleigh damping. Chapter 5 covers single-DOF time integration; Chapters 13--14 cover multi-DOF methods.

3. Hilber, H.M., Hughes, T.J.R., & Taylor, R.L. (1977). "Improved numerical dissipation for time integration algorithms in structural dynamics." *Earthquake Engineering and Structural Dynamics*, 5(3), 283--292. DOI: 10.1002/eqe.4290050306 -- Original HHT-$\alpha$ paper. Introduces the $\alpha$ parameter for controlled numerical dissipation of high-frequency spurious modes while maintaining second-order accuracy. Essential for contact-dominated bolted joint problems where high-frequency chatter must be damped.

4. Hughes, T.J.R. (1987). *The Finite Element Method: Linear Static and Dynamic Finite Element Analysis*. Prentice Hall. -- Rigorous mathematical framework for time integration stability and accuracy analysis. Chapter 9 covers the Newmark family and proves unconditional stability for $\beta \geq (\gamma + 1/2)^2/4$.

5. Newmark, N.M. (1959). "A method of computation for structural dynamics." *ASCE Journal of the Engineering Mechanics Division*, 85(EM3), 67--94. -- Seminal paper introducing the Newmark-$\beta$ family of time integration methods. The average acceleration variant ($\beta = 1/4$, $\gamma = 1/2$) remains the most widely used implicit integrator in structural dynamics 65+ years later.

6. Butcher, J.C. (2016). *Numerical Methods for Ordinary Differential Equations*, 3rd ed. Wiley. DOI: 10.1002/9781119121534 -- Definitive reference for Runge-Kutta methods, including the classical RK4 used in BAS for state-space integration.

7. Wriggers, P. (2006). *Computational Contact Mechanics*, 2nd ed. Springer. DOI: 10.1007/978-3-540-32609-0 -- Treatment of Newton-Raphson iteration for contact problems, including line search strategies and convergence monitoring. Directly applicable to the nonlinear solver used for gasket and friction contact in BAS.

8. Crisfield, M.A. (1991). *Non-linear Finite Element Analysis of Solids and Structures*, Vol. 1. Wiley. ISBN: 0-471-92956-5 -- Comprehensive coverage of line search methods, arc-length control, and convergence criteria for nonlinear structural analysis. The combined convergence criterion (force + displacement + energy) used in BAS follows the approach recommended in Chapter 9.

---

**END OF PART VIII**

*Part IX covers Similitude and Scaling Analysis*
*Part X covers Preload Loss Models*
*Part XI covers Coupled Friction-Wear-Loosening Analysis Framework*
*Part XII covers Force Excitation Functions, Damping Models, and Nonlinear Solvers*
