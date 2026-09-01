# MSD Framework - PART II: CONTACT ELEMENT LIBRARY

**Complete Technical Reference for Bolt Analysis Studio**

**Authors:** L. Ribeiro, D. Carvalho, S.C. Naves, T. Santos, V. Marques, G. Arruda
**Institution:** LTAD/UFU - Tribology and Wear Technology Laboratory, Federal University of Uberlândia
**Project:** Petrobras R&D - Bolted Flange Joint Integrity

---

**Abstract.** This document provides a complete technical specification of all contact element types used in the MSD representation of bolted flanged joints. In a physical bolted joint, mechanical behavior is governed not only by the bulk stiffness of components (bolt, flanges, gasket) but critically by the interfaces between them -- the thread engagement zone, the bearing surfaces under the bolt head and nut, and the flange-to-flange or flange-to-gasket interfaces. Each contact type exhibits distinct mechanical and tribological behavior: thread contacts feature helical coupling between axial and torsional DOFs (Nassar and Housari, 2006), bearing contacts provide the frictional resistance that prevents nut rotation (Junker, 1969), and gasket contacts display nonlinear viscoelastic response with creep relaxation (Bickford, 2008). The document defines the contact type enumeration, the DOF-coupling matrix, the base `Contact` class hierarchy, and the complete mathematical formulations for thread load distribution (Yamamoto, 1980; Sopwith, 1948), bearing friction torque, gasket nonlinearity, and flange-flange fretting. Each contact type is linked to the appropriate friction, wear, and lubrication sub-models described in Parts VI and VII.

---

## 4. Contact Element Classification and Properties

### 4.1 Contact Type Enumeration

```python
from enum import Enum, auto

class ContactType(Enum):
    """Classification of contact types in bolted joints"""
    
    # Thread contacts
    THREAD = auto()              # Aggregate thread contact
    THREAD_INDIVIDUAL = auto()   # Individual thread element
    
    # Bearing contacts
    BEARING_HEAD = auto()        # Bolt head bearing surface
    BEARING_NUT = auto()         # Nut bearing surface
    
    # Washer contacts
    WASHER_FLANGE = auto()       # Washer-to-flange interface
    
    # Flange contacts
    FLANGE_FLANGE = auto()       # Metal-to-metal flange contact
    FLANGE_GASKET = auto()       # Flange-to-gasket interface
    
    # Special contacts
    GASKET_INTERNAL = auto()     # Internal gasket behavior
    SHIM_CONTACT = auto()        # Shim/spacer contact
```

### 4.2 Contact Classification by Behavior

**Mechanical Behavior Classification:**

| Contact Type | Behavior | Key Characteristics |
|-------------|----------|---------------------|
| THREAD | Nonlinear elastic + friction | Helix coupling, load distribution |
| BEARING_HEAD | Linear elastic + friction | Torsional DOF coupling |
| BEARING_NUT | Linear elastic + friction | Resists loosening |
| WASHER_FLANGE | Linear + embedding | Surface settling |
| FLANGE_GASKET | Nonlinear viscoelastic | Creep, hysteresis |
| FLANGE_FLANGE | Linear + fretting | Microslip, wear |

**Tribological Behavior Classification:**

| Contact Type | Friction Model | Wear Model | Evolution Model |
|-------------|---------------|------------|-----------------|
| THREAD | LuGre/Coulomb | Archard + Fretting | Three-phase |
| BEARING | Stribeck | Archard | Three-phase |
| WASHER_FLANGE | Coulomb | Embedding | Exponential |
| FLANGE_GASKET | None (bonded) | Creep relaxation | Logarithmic |
| FLANGE_FLANGE | Coulomb | Fretting | Running-in |

### 4.3 Contact-DOF Coupling Summary

```
╔═══════════════════════════════════════════════════════════════════════════════════╗
║                    CONTACT-DOF COUPLING MATRIX                                     ║
╠═══════════════════════════════════════════════════════════════════════════════════╣
║                                                                                    ║
║  Contact Type         │ Axial │ Torsional │ Transverse │ Special Coupling         ║
║  ═════════════════════╪═══════╪═══════════╪════════════╪══════════════════════════║
║  THREAD               │   ✓   │     ✓     │            │ HELIX: Δx = (p/2π)Δθ   ║
║  THREAD_INDIVIDUAL    │   ✓   │     ✓     │            │ Helix + load fraction   ║
║  BEARING_HEAD         │   ✓   │     ✓     │            │ Friction torque          ║
║  BEARING_NUT          │   ✓   │     ✓     │            │ Friction torque          ║
║  WASHER_FLANGE        │   ✓   │           │            │ Embedding                ║
║  FLANGE_GASKET        │   ✓   │           │            │ Creep, nonlinear k       ║
║  FLANGE_FLANGE        │   ✓   │           │     ✓      │ Microslip, fretting      ║
║                                                                                    ║
╚═══════════════════════════════════════════════════════════════════════════════════╝
```

### 4.4 Base Contact Element Class

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional, Union
import numpy as np


@dataclass
class ContactGeometry:
    """Geometric properties of a contact interface"""
    
    # Primary dimensions
    outer_diameter: float = 0.0     # m
    inner_diameter: float = 0.0     # m
    thickness: float = 0.0          # m (effective contact layer thickness)
    
    # Derived properties
    @property
    def contact_area(self) -> float:
        """Annular contact area [m²]"""
        return np.pi / 4 * (self.outer_diameter**2 - self.inner_diameter**2)
    
    @property
    def effective_radius(self) -> float:
        """Effective radius for friction torque calculation [m]"""
        r_o = self.outer_diameter / 2
        r_i = self.inner_diameter / 2
        if r_o <= r_i:
            return 0.0
        # Weighted average radius
        return (2/3) * (r_o**3 - r_i**3) / (r_o**2 - r_i**2)
    
    @property
    def mean_radius(self) -> float:
        """Mean radius [m]"""
        return (self.outer_diameter + self.inner_diameter) / 4


@dataclass
class FrictionProperties:
    """Friction properties for a contact interface"""
    
    # Basic Coulomb parameters
    mu_static: float = 0.15
    mu_kinetic: float = 0.12
    
    # Friction model selection
    friction_model: str = 'COULOMB'  # 'COULOMB', 'STRIBECK', 'LUGRE', 'DAHL'
    
    # Stribeck parameters
    v_stribeck: float = 0.01        # Stribeck velocity [m/s]
    alpha_stribeck: float = 2.0     # Shape exponent
    
    # LuGre parameters
    sigma_0: float = 1e5            # Bristle stiffness [N/m]
    sigma_1: float = 100.0          # Micro-damping [Ns/m]
    sigma_2: float = 0.1            # Viscous coefficient [Ns/m]
    
    # Evolution parameters (three-phase model)
    mu_initial: float = None        # Initial μ (defaults to mu_static)
    mu_peak: float = None           # Peak μ during running-in
    mu_steady: float = None         # Long-term steady-state μ
    N_phase1: int = 100             # Running-in cycles
    N_phase2: int = 500             # Transition cycles
    N_phase3: int = 5000            # Stabilization cycles
    
    # Current state
    mu_current: float = field(default=None, init=False)
    
    def __post_init__(self):
        if self.mu_initial is None:
            self.mu_initial = self.mu_static
        if self.mu_peak is None:
            self.mu_peak = 1.3 * self.mu_static
        if self.mu_steady is None:
            self.mu_steady = self.mu_kinetic
        self.mu_current = self.mu_initial


@dataclass
class WearProperties:
    """Wear properties for a contact interface"""
    
    # Wear model selection
    wear_model: str = 'ARCHARD'  # 'ARCHARD', 'ENERGY', 'FRETTING', 'COMBINED'
    
    # Archard parameters
    K_archard: float = 1e-6         # Dimensionless wear coefficient
    hardness: float = 2e9           # Surface hardness [Pa]
    
    # Energy-based parameters
    alpha_energy: float = 3e-8      # Energy wear coefficient [m³/J]
    
    # Fretting parameters
    fretting_threshold: float = 5e-6  # Minimum slip for fretting [m]
    
    # State tracking
    accumulated_volume: float = field(default=0.0, init=False)
    accumulated_depth: float = field(default=0.0, init=False)
    accumulated_slip: float = field(default=0.0, init=False)


@dataclass
class ContactState:
    """Current state of a contact element"""
    
    # Contact status
    in_contact: bool = True
    slip_state: str = 'stick'       # 'stick', 'partial_slip', 'gross_slip'
    
    # Force state
    normal_force: float = 0.0       # N
    friction_force: float = 0.0     # N
    friction_torque: float = 0.0    # Nm
    
    # Kinematic state
    relative_displacement: float = 0.0  # m
    relative_velocity: float = 0.0      # m/s
    relative_rotation: float = 0.0      # rad
    
    # Pressure state
    contact_pressure: float = 0.0   # Pa
    
    # Accumulation
    total_slip_distance: float = 0.0  # m
    cycle_count: int = 0


class BaseContactElement(ABC):
    """
    Abstract base class for all contact elements.
    
    Provides common interface and functionality for:
    - Stiffness matrix computation
    - Damping matrix computation
    - Force vector computation
    - State update
    - Tribological model integration
    """
    
    def __init__(self,
                 contact_id: str,
                 contact_type: ContactType,
                 dof_indices: List[int],
                 geometry: ContactGeometry,
                 friction: FrictionProperties = None,
                 wear: WearProperties = None):
        """
        Initialize contact element.
        
        Args:
            contact_id: Unique identifier for this contact
            contact_type: Type of contact
            dof_indices: Global DOF indices for this contact
            geometry: Contact geometry specification
            friction: Friction properties (optional)
            wear: Wear properties (optional)
        """
        self.contact_id = contact_id
        self.contact_type = contact_type
        self.dof_indices = dof_indices
        self.geometry = geometry
        self.friction = friction if friction else FrictionProperties()
        self.wear = wear if wear else WearProperties()
        
        # State
        self.state = ContactState()
        
        # Local DOF count
        self.n_local_dof = len(dof_indices)
        
    @abstractmethod
    def get_stiffness_matrix(self) -> np.ndarray:
        """
        Compute local stiffness matrix.
        
        Returns:
            Local stiffness matrix [K_local] of shape (n_local, n_local)
        """
        pass
    
    @abstractmethod
    def get_damping_matrix(self) -> np.ndarray:
        """
        Compute local damping matrix.
        
        Returns:
            Local damping matrix [C_local] of shape (n_local, n_local)
        """
        pass
    
    @abstractmethod
    def get_force_vector(self,
                         u_local: np.ndarray,
                         v_local: np.ndarray,
                         preload: float) -> np.ndarray:
        """
        Compute local force vector including tribological forces.
        
        Args:
            u_local: Local displacement vector
            v_local: Local velocity vector
            preload: Current preload force [N]
        
        Returns:
            Local force vector {F_local} of shape (n_local,)
        """
        pass
    
    @abstractmethod
    def update_state(self,
                     u_local: np.ndarray,
                     v_local: np.ndarray,
                     preload: float,
                     dt: float):
        """
        Update contact state after time step.
        
        Args:
            u_local: Local displacement vector
            v_local: Local velocity vector
            preload: Current preload force [N]
            dt: Time step [s]
        """
        pass
    
    def compute_friction_force(self, 
                                normal_force: float, 
                                velocity: float) -> float:
        """
        Compute friction force using selected model.
        
        Args:
            normal_force: Normal contact force [N]
            velocity: Relative sliding velocity [m/s]
        
        Returns:
            Friction force [N]
        """
        model = self.friction.friction_model.upper()
        
        if model == 'COULOMB':
            return self._coulomb_friction(normal_force, velocity)
        elif model == 'STRIBECK':
            return self._stribeck_friction(normal_force, velocity)
        elif model == 'LUGRE':
            return self._lugre_friction(normal_force, velocity)
        elif model == 'DAHL':
            return self._dahl_friction(normal_force, velocity)
        else:
            return self._coulomb_friction(normal_force, velocity)
    
    def _coulomb_friction(self, F_n: float, v: float) -> float:
        """Regularized Coulomb friction"""
        mu = self.friction.mu_kinetic if abs(v) > 0.001 else self.friction.mu_static
        v_reg = 0.001
        return -mu * F_n * np.tanh(v / v_reg)
    
    def _stribeck_friction(self, F_n: float, v: float) -> float:
        """Stribeck friction with velocity dependence"""
        mu_s = self.friction.mu_static
        mu_k = self.friction.mu_kinetic
        v_s = self.friction.v_stribeck
        alpha = self.friction.alpha_stribeck
        
        stribeck = np.exp(-(abs(v) / v_s) ** alpha)
        mu = mu_k + (mu_s - mu_k) * stribeck
        
        return -mu * F_n * np.sign(v) if abs(v) > 1e-10 else 0.0
    
    def _lugre_friction(self, F_n: float, v: float) -> float:
        """LuGre dynamic friction (simplified)"""
        # Full LuGre requires state variable z
        # This is simplified version
        return self._stribeck_friction(F_n, v)
    
    def _dahl_friction(self, F_n: float, v: float) -> float:
        """Dahl friction (simplified)"""
        return self._coulomb_friction(F_n, v)
    
    def compute_wear_increment(self,
                                normal_force: float,
                                slip_distance: float,
                                dissipated_energy: float = None) -> Tuple[float, float]:
        """
        Compute wear increment.
        
        Args:
            normal_force: Normal force [N]
            slip_distance: Sliding distance [m]
            dissipated_energy: Friction energy dissipated [J] (for energy model)
        
        Returns:
            (volume_increment, depth_increment) [m³, m]
        """
        model = self.wear.wear_model.upper()
        A = self.geometry.contact_area
        
        if model == 'ARCHARD':
            K = self.wear.K_archard
            H = self.wear.hardness
            dV = K * normal_force * slip_distance / H
            
        elif model == 'ENERGY' and dissipated_energy is not None:
            alpha = self.wear.alpha_energy
            dV = alpha * dissipated_energy
            
        elif model == 'FRETTING':
            if slip_distance > self.wear.fretting_threshold:
                K = self.wear.K_archard * 10  # Enhanced for fretting
                H = self.wear.hardness
                dV = K * normal_force * slip_distance / H
            else:
                dV = 0.0
                
        elif model == 'COMBINED':
            # Use both Archard and energy
            K = self.wear.K_archard
            H = self.wear.hardness
            dV_archard = K * normal_force * slip_distance / H
            
            if dissipated_energy is not None:
                alpha = self.wear.alpha_energy
                dV_energy = alpha * dissipated_energy
                dV = 0.5 * (dV_archard + dV_energy)  # Average
            else:
                dV = dV_archard
        else:
            dV = 0.0
        
        dh = dV / A if A > 0 else 0.0
        
        # Update accumulated values
        self.wear.accumulated_volume += dV
        self.wear.accumulated_depth += dh
        self.wear.accumulated_slip += slip_distance
        
        return dV, dh
    
    def update_friction_coefficient(self, cycles: int):
        """
        Update friction coefficient based on cycles (three-phase model).
        
        Args:
            cycles: Current cycle count
        """
        mu_0 = self.friction.mu_initial
        mu_peak = self.friction.mu_peak
        mu_ss = self.friction.mu_steady
        N1 = self.friction.N_phase1
        N2 = self.friction.N_phase2
        N3 = self.friction.N_phase3
        
        # Three-phase model
        term1 = (mu_peak - mu_0) * (1 - np.exp(-cycles / N1)) * np.exp(-cycles / N2)
        term2 = (mu_ss - mu_0) * (1 - np.exp(-cycles / N3))
        
        self.friction.mu_current = mu_0 + term1 + term2
        self.friction.mu_current = np.clip(self.friction.mu_current, 0.01, 2.0)
```

---

## 5. Thread Contact Model with Individual Threads

### 5.1 Thread Geometry

```python
@dataclass
class ThreadGeometry:
    """Complete thread geometry specification"""
    
    # Primary dimensions (per ISO 68-1)
    major_diameter: float       # d [m] - nominal/major diameter
    pitch: float                # p [m] - thread pitch
    
    # Engagement
    engaged_threads: int = 8    # Number of engaged threads
    
    # Optional overrides (calculated if not provided)
    pitch_diameter: float = None      # d₂ [m]
    minor_diameter: float = None      # d₃ [m]
    flank_angle: float = 60.0         # 2α [degrees] - total included angle
    
    # Thread form
    thread_form: str = 'ISO_METRIC'   # 'ISO_METRIC', 'UN', 'ACME', 'BUTTRESS'
    
    def __post_init__(self):
        """Calculate derived dimensions if not provided"""
        if self.pitch_diameter is None:
            # ISO metric: d₂ = d - 0.6495p
            self.pitch_diameter = self.major_diameter - 0.6495 * self.pitch
        
        if self.minor_diameter is None:
            # ISO metric: d₃ = d - 1.2268p
            self.minor_diameter = self.major_diameter - 1.2268 * self.pitch
    
    @property
    def flank_angle_rad(self) -> float:
        """Half flank angle in radians"""
        return np.radians(self.flank_angle / 2)
    
    @property
    def helix_angle(self) -> float:
        """Helix angle [rad]"""
        return np.arctan(self.pitch / (np.pi * self.pitch_diameter))
    
    @property
    def helix_coupling_factor(self) -> float:
        """Helix coupling factor λ = p/(2π) [m/rad]"""
        return self.pitch / (2 * np.pi)
    
    @property
    def stress_area(self) -> float:
        """Thread stress area [m²]"""
        d_s = (self.pitch_diameter + self.minor_diameter) / 2
        return np.pi / 4 * d_s**2
    
    @property
    def thread_root_area(self) -> float:
        """Root area [m²]"""
        return np.pi / 4 * self.minor_diameter**2
    
    def get_thread_area(self, thread_index: int) -> float:
        """Get contact area for specific thread"""
        # Simplified: same area for all threads
        return np.pi * self.pitch_diameter * self.pitch / self.engaged_threads
```

### 5.2 Thread Load Distribution Theory

**Sopwith Distribution Model:**

The load distribution across engaged threads follows an exponential decay from the loaded face:

$$\phi_i = \frac{\lambda \sinh(\lambda)}{\cosh(\lambda n) - 1} \cdot \cosh(\lambda(n - i))$$

Where:
- φ_i = Load fraction on thread i
- λ ≈ 0.3 (distribution parameter for steel-steel)
- n = Number of engaged threads
- i = Thread index (1 = first engaged)

**Simplified Distribution Models:**

```python
def compute_thread_load_distribution(n_threads: int, 
                                      model: str = 'exponential',
                                      lambda_param: float = 0.3) -> List[float]:
    """
    Compute load distribution across engaged threads.
    
    Args:
        n_threads: Number of engaged threads
        model: Distribution model ('uniform', 'linear', 'power', 'exponential')
        lambda_param: Distribution parameter (for exponential/power)
    
    Returns:
        List of load fractions (sum = 1.0)
    """
    if model == 'uniform':
        # Equal load on all threads
        fractions = [1.0 / n_threads] * n_threads
        
    elif model == 'linear':
        # VDI 2230 linear approximation
        # Thread 1 carries more, linear decrease
        fractions = []
        total = 0
        for i in range(n_threads):
            f = n_threads - i
            fractions.append(f)
            total += f
        fractions = [f / total for f in fractions]
        
    elif model == 'power':
        # Power law distribution
        fractions = []
        total = 0
        for i in range(n_threads):
            f = (n_threads - i) ** lambda_param
            fractions.append(f)
            total += f
        fractions = [f / total for f in fractions]
        
    elif model == 'exponential':
        # Sopwith-based exponential distribution
        lam = lambda_param
        n = n_threads
        
        fractions = []
        total = 0
        
        for i in range(n_threads):
            # Thread i (0-indexed)
            f = np.cosh(lam * (n - 1 - i)) if n > 1 else 1.0
            fractions.append(f)
            total += f
        
        fractions = [f / total for f in fractions]
        
    else:
        raise ValueError(f"Unknown distribution model: {model}")
    
    return fractions


# Example for n=8 threads with λ=0.3:
# Thread 1: 19.0%
# Thread 2: 16.0%
# Thread 3: 13.5%
# Thread 4: 11.4%
# Thread 5:  9.6%
# Thread 6:  8.1%
# Thread 7:  6.8%
# Thread 8:  5.7%
```

### 5.3 Thread Contact Element Implementation

```python
class ThreadContactElement(BaseContactElement):
    """
    Thread contact element with individual thread modeling.
    
    Key features:
    - Helix coupling: Δx = (p/2π)Δθ
    - Non-uniform load distribution
    - Per-thread friction and wear tracking
    - Independent slip detection per thread
    """
    
    def __init__(self,
                 contact_id: str,
                 node_stud: int,
                 node_nut: int,
                 dof_axial_nut: int,
                 dof_theta_stud: int,
                 dof_theta_nut: int,
                 geometry: ThreadGeometry,
                 friction: FrictionProperties = None,
                 wear: WearProperties = None,
                 distribution_model: str = 'exponential',
                 distribution_parameter: float = 0.3):
        """
        Initialize thread contact element.
        
        Args:
            contact_id: Unique identifier
            node_stud: Stud node number
            node_nut: Nut node number
            dof_axial_nut: Global DOF for nut axial displacement
            dof_theta_stud: Global DOF for stud rotation
            dof_theta_nut: Global DOF for nut rotation
            geometry: Thread geometry specification
            friction: Friction properties
            wear: Wear properties
            distribution_model: Load distribution model
            distribution_parameter: Distribution parameter λ
        """
        # DOF indices: [x_nut, θ_stud, θ_nut]
        dof_indices = [dof_axial_nut, dof_theta_stud, dof_theta_nut]
        
        super().__init__(
            contact_id=contact_id,
            contact_type=ContactType.THREAD,
            dof_indices=dof_indices,
            geometry=ContactGeometry(
                outer_diameter=geometry.major_diameter,
                inner_diameter=geometry.minor_diameter,
                thickness=geometry.pitch
            ),
            friction=friction,
            wear=wear
        )
        
        self.thread_geometry = geometry
        self.node_stud = node_stud
        self.node_nut = node_nut
        self.distribution_model = distribution_model
        self.distribution_parameter = distribution_parameter
        
        # Compute load distribution
        self.load_fractions = compute_thread_load_distribution(
            geometry.engaged_threads,
            distribution_model,
            distribution_parameter
        )
        
        # Create individual thread sub-elements
        self.thread_elements = self._create_thread_elements()
        
        # Compute base stiffness
        self._compute_thread_stiffness()
        
    def _create_thread_elements(self) -> List[Dict]:
        """Create individual thread sub-elements"""
        threads = []
        
        for i in range(self.thread_geometry.engaged_threads):
            thread = {
                'index': i,
                'load_fraction': self.load_fractions[i],
                'friction': FrictionProperties(
                    mu_static=self.friction.mu_static,
                    mu_kinetic=self.friction.mu_kinetic,
                    friction_model=self.friction.friction_model
                ),
                'wear': WearProperties(
                    wear_model=self.wear.wear_model,
                    K_archard=self.wear.K_archard,
                    hardness=self.wear.hardness
                ),
                'state': {
                    'slip_state': 'stick',
                    'cumulative_slip': 0.0,
                    'cumulative_rotation': 0.0,
                    'mu_current': self.friction.mu_static,
                    'wear_depth': 0.0
                }
            }
            threads.append(thread)
        
        return threads
    
    def _compute_thread_stiffness(self):
        """Compute thread stiffness parameters"""
        geom = self.thread_geometry
        
        # Base thread stiffness (VDI 2230 approximation)
        # k_base ≈ 0.5 × E_eff × p × cos(α/2) / [tan(α/2) + μ]
        E_eff = 210e9  # Steel modulus (could be parameterized)
        p = geom.pitch
        alpha_half = geom.flank_angle_rad
        mu = self.friction.mu_static
        
        self.k_base = 0.5 * E_eff * p * np.cos(alpha_half) / (np.tan(alpha_half) + mu)
        
        # Total thread stiffness (sum of parallel threads)
        self.k_thread_total = self.k_base * sum(self.load_fractions)
        
        # Helix coupling factor
        self.lambda_helix = geom.helix_coupling_factor
    
    def get_stiffness_matrix(self) -> np.ndarray:
        """
        Compute 3×3 stiffness matrix with helix coupling.
        
        DOFs: [x_nut, θ_stud, θ_nut]
        
        The helix coupling creates off-diagonal terms:
        Δx = λ × Δθ  where λ = p/(2π)
        
        Returns:
            3×3 stiffness matrix
        """
        k = self.k_thread_total
        lam = self.lambda_helix
        
        # Stiffness matrix with helix coupling
        # Derived from strain energy: U = ½k(Δx - λΔθ)²
        K = k * np.array([
            [1.0,      -lam,       lam    ],
            [-lam,     lam**2,    -lam**2 ],
            [lam,     -lam**2,     lam**2 ]
        ])
        
        return K
    
    def get_damping_matrix(self) -> np.ndarray:
        """
        Compute damping matrix.
        
        Includes:
        - Material damping (small)
        - Friction damping contribution
        
        Returns:
            3×3 damping matrix
        """
        # Small structural damping
        c_struct = 0.001 * self.k_thread_total
        
        C = np.zeros((3, 3))
        C[0, 0] = c_struct  # Axial
        
        return C
    
    def get_force_vector(self,
                         u_local: np.ndarray,
                         v_local: np.ndarray,
                         preload: float) -> np.ndarray:
        """
        Compute force vector including friction torques.
        
        Args:
            u_local: [x_nut, θ_stud, θ_nut]
            v_local: [ẋ_nut, θ̇_stud, θ̇_nut]
            preload: Current preload [N]
        
        Returns:
            Force vector [F_x, T_stud, T_nut]
        """
        F = np.zeros(3)
        
        # Relative rotation rate (nut relative to stud)
        omega_rel = v_local[2] - v_local[1] if len(v_local) > 2 else 0.0
        
        # Thread friction torque
        geom = self.thread_geometry
        d2 = geom.pitch_diameter
        alpha_half = geom.flank_angle_rad
        mu = self.friction.mu_current
        
        # Thread friction torque (resists relative rotation)
        T_thread = mu * preload * d2 / (2 * np.cos(alpha_half))
        
        if abs(omega_rel) > 1e-10:
            T_friction = -np.sign(omega_rel) * T_thread
        else:
            T_friction = 0.0
        
        # Apply to stud and nut (equal and opposite)
        F[1] = -T_friction  # On stud
        F[2] = +T_friction  # On nut
        
        return F
    
    def update_state(self,
                     u_local: np.ndarray,
                     v_local: np.ndarray,
                     preload: float,
                     dt: float):
        """Update thread state"""
        self.state.normal_force = preload
        
        # Update relative motion
        if len(u_local) > 2:
            self.state.relative_rotation = u_local[2] - u_local[1]
        
        # Update each thread element
        for thread in self.thread_elements:
            F_thread = thread['load_fraction'] * preload
            
            # Update friction coefficient
            thread['state']['mu_current'] = self.friction.mu_current
    
    def compute_torque_components(self, preload: float) -> Dict:
        """
        Compute all torque components for loosening analysis.
        
        Returns:
            Dictionary with torque values
        """
        geom = self.thread_geometry
        p = geom.pitch
        d2 = geom.pitch_diameter
        alpha_half = geom.flank_angle_rad
        mu = self.friction.mu_current
        
        # Pitch torque (drives loosening)
        T_pitch = preload * p / (2 * np.pi)
        
        # Thread friction torque (resists loosening)
        T_thread = mu * preload * d2 / (2 * np.cos(alpha_half))
        
        return {
            'T_pitch': T_pitch,
            'T_thread': T_thread,
            'T_net': T_pitch - T_thread,
            'loosening_possible': T_pitch > T_thread
        }
    
    def compute_loosening_per_thread(self,
                                      preload: float,
                                      transverse_force: float,
                                      cycle: int,
                                      dt: float) -> Tuple[float, float]:
        """
        Compute loosening contribution from each thread.
        
        Args:
            preload: Current preload [N]
            transverse_force: Transverse force [N]
            cycle: Current cycle number
            dt: Time step [s]
        
        Returns:
            (total_loosening_angle, preload_loss)
        """
        total_theta = 0.0
        
        for thread in self.thread_elements:
            phi = thread['load_fraction']
            F_thread = phi * preload
            mu = thread['state']['mu_current']
            
            # Check slip condition for this thread
            F_friction_capacity = mu * F_thread
            F_trans_thread = phi * transverse_force
            
            if abs(F_trans_thread) > F_friction_capacity:
                # This thread is slipping
                thread['state']['slip_state'] = 'gross_slip'
                
                # Compute loosening angle for this thread
                torques = self.compute_torque_components(F_thread)
                
                if torques['loosening_possible']:
                    # Simplified: small rotation increment
                    d_theta = 0.001 * phi  # rad per cycle
                    total_theta += d_theta
                    thread['state']['cumulative_rotation'] += d_theta
            else:
                thread['state']['slip_state'] = 'stick'
        
        # Preload loss from rotation
        p = self.thread_geometry.pitch
        delta_preload = self.k_thread_total * (p / (2 * np.pi)) * total_theta
        
        return total_theta, delta_preload
    
    def get_thread_summary(self) -> Dict:
        """Get summary of thread states"""
        threads = []
        for t in self.thread_elements:
            threads.append({
                'index': t['index'],
                'load_fraction_pct': t['load_fraction'] * 100,
                'slip_state': t['state']['slip_state'],
                'mu_current': t['state']['mu_current'],
                'cumulative_rotation_deg': np.degrees(t['state']['cumulative_rotation']),
                'wear_depth_um': t['state']['wear_depth'] * 1e6
            })
        
        return {
            'threads': threads,
            'total_loosening_deg': sum(np.degrees(t['state']['cumulative_rotation']) 
                                       for t in self.thread_elements),
            'n_slipping': sum(1 for t in self.thread_elements 
                             if t['state']['slip_state'] != 'stick')
        }
```

---

## 6. Bearing Contact Models (Head and Nut)

### 6.1 Bearing Geometry and Effective Radius

```python
@dataclass
class BearingGeometry:
    """Bearing surface geometry"""
    
    outer_diameter: float    # m (under-head diameter or nut AF)
    inner_diameter: float    # m (hole diameter)
    
    @property
    def contact_area(self) -> float:
        """Annular contact area [m²]"""
        return np.pi / 4 * (self.outer_diameter**2 - self.inner_diameter**2)
    
    @property
    def effective_radius(self) -> float:
        """
        Effective radius for friction torque calculation.
        
        For annular contact: r_eff = (2/3) × (r_o³ - r_i³)/(r_o² - r_i²)
        """
        r_o = self.outer_diameter / 2
        r_i = self.inner_diameter / 2
        
        if r_o <= r_i:
            return 0.0
        
        return (2/3) * (r_o**3 - r_i**3) / (r_o**2 - r_i**2)
    
    @property
    def mean_radius(self) -> float:
        """Mean radius [m]"""
        return (self.outer_diameter + self.inner_diameter) / 4


class BearingContactElement(BaseContactElement):
    """
    Bearing contact element for bolt head or nut.
    
    Key features:
    - Friction torque calculation: T = μ × F_n × r_eff
    - Slip detection
    - Torsional DOF coupling
    """
    
    def __init__(self,
                 contact_id: str,
                 location: str,  # 'head' or 'nut'
                 dof_axial_1: int,
                 dof_axial_2: int,
                 dof_theta: int,
                 geometry: BearingGeometry,
                 friction: FrictionProperties = None,
                 wear: WearProperties = None):
        """
        Initialize bearing contact.
        
        Args:
            contact_id: Unique identifier
            location: 'head' or 'nut'
            dof_axial_1: First axial DOF (e.g., bolt head)
            dof_axial_2: Second axial DOF (e.g., washer)
            dof_theta: Torsional DOF (stud or nut)
            geometry: Bearing geometry
            friction: Friction properties
            wear: Wear properties
        """
        contact_type = ContactType.BEARING_HEAD if location == 'head' else ContactType.BEARING_NUT
        dof_indices = [dof_axial_1, dof_axial_2, dof_theta]
        
        super().__init__(
            contact_id=contact_id,
            contact_type=contact_type,
            dof_indices=dof_indices,
            geometry=ContactGeometry(
                outer_diameter=geometry.outer_diameter,
                inner_diameter=geometry.inner_diameter,
                thickness=0.001  # Nominal
            ),
            friction=friction,
            wear=wear
        )
        
        self.bearing_geometry = geometry
        self.location = location
        
        # Contact stiffness (high for metal-metal)
        self.k_contact = 2e9  # N/m (typical for bearing surfaces)
        
    def get_stiffness_matrix(self) -> np.ndarray:
        """
        Compute 3×3 stiffness matrix.
        
        DOFs: [x_1, x_2, θ]
        
        Axial coupling between x_1 and x_2.
        Small torsional stiffness.
        """
        k = self.k_contact
        k_theta = 100  # Small torsional stiffness [Nm/rad]
        
        K = np.array([
            [k,    -k,    0       ],
            [-k,    k,    0       ],
            [0,     0,    k_theta ]
        ])
        
        return K
    
    def get_damping_matrix(self) -> np.ndarray:
        """Compute damping matrix"""
        c = 0.001 * self.k_contact
        
        C = np.array([
            [c,   -c,   0  ],
            [-c,   c,   0  ],
            [0,    0,   1.0]
        ])
        
        return C
    
    def get_force_vector(self,
                         u_local: np.ndarray,
                         v_local: np.ndarray,
                         preload: float) -> np.ndarray:
        """
        Compute force vector including bearing friction torque.
        
        The bearing friction torque RESISTS loosening rotation.
        """
        F = np.zeros(3)
        
        # Angular velocity
        omega = v_local[2] if len(v_local) > 2 else 0.0
        
        # Friction torque
        r_eff = self.bearing_geometry.effective_radius
        mu = self.friction.mu_current
        
        T_bearing = mu * preload * r_eff
        
        if abs(omega) > 1e-10:
            F[2] = -np.sign(omega) * T_bearing
        
        self.state.friction_torque = T_bearing
        
        return F
    
    def update_state(self,
                     u_local: np.ndarray,
                     v_local: np.ndarray,
                     preload: float,
                     dt: float):
        """Update bearing state"""
        self.state.normal_force = preload
        self.state.contact_pressure = preload / self.bearing_geometry.contact_area
        
        # Check slip condition
        omega = v_local[2] if len(v_local) > 2 else 0.0
        if abs(omega) > 1e-8:
            self.state.slip_state = 'gross_slip'
        else:
            self.state.slip_state = 'stick'
    
    def compute_bearing_torque(self, preload: float) -> float:
        """Compute bearing friction torque capacity"""
        r_eff = self.bearing_geometry.effective_radius
        mu = self.friction.mu_current
        return mu * preload * r_eff
```

---

## 7. Washer-Flange Contact Model

### 7.1 Embedding Phenomenon

Surface roughness peaks flatten under load, causing preload loss:

$$\delta_{embed}(N) = \delta_{\infty} \cdot [1 - \exp(-N/N_c)]$$

Where:
- δ_embed = Current embedding depth [m]
- δ_∞ = Ultimate embedding depth [m]
- N = Number of cycles
- N_c = Characteristic cycles (typically 10-100)

**Ultimate Embedding Depth:**

$$\delta_{\infty} = f_z \cdot (R_{z,1} + R_{z,2})$$

Where:
- f_z = Embedding factor (0.5-0.8)
- R_z = Surface roughness (peak-to-valley) [m]

```python
class WasherFlangeContactElement(BaseContactElement):
    """
    Washer-flange contact element with embedding model.
    
    Key features:
    - Embedding (surface settling) model
    - Fretting wear capability
    - Preload loss calculation
    """
    
    def __init__(self,
                 contact_id: str,
                 dof_washer: int,
                 dof_flange: int,
                 geometry: ContactGeometry,
                 friction: FrictionProperties = None,
                 wear: WearProperties = None,
                 roughness_washer: float = 3e-6,     # Rz [m]
                 roughness_flange: float = 6e-6,     # Rz [m]
                 embedding_factor: float = 0.6,
                 characteristic_cycles: int = 50):
        """
        Initialize washer-flange contact.
        
        Args:
            contact_id: Unique identifier
            dof_washer: Washer axial DOF
            dof_flange: Flange axial DOF
            geometry: Contact geometry
            friction: Friction properties
            wear: Wear properties
            roughness_washer: Washer surface roughness Rz [m]
            roughness_flange: Flange surface roughness Rz [m]
            embedding_factor: f_z (0.5-0.8)
            characteristic_cycles: N_c
        """
        dof_indices = [dof_washer, dof_flange]
        
        super().__init__(
            contact_id=contact_id,
            contact_type=ContactType.WASHER_FLANGE,
            dof_indices=dof_indices,
            geometry=geometry,
            friction=friction,
            wear=wear
        )
        
        # Embedding parameters
        self.Rz_washer = roughness_washer
        self.Rz_flange = roughness_flange
        self.f_z = embedding_factor
        self.N_c = characteristic_cycles
        
        # Ultimate embedding depth
        self.delta_ultimate = self.f_z * (self.Rz_washer + self.Rz_flange)
        
        # Current embedding state
        self.embedding_depth = 0.0
        
        # Contact stiffness
        self.k_contact = 1e9  # N/m
        
    def get_embedding_depth(self, cycles: int) -> float:
        """
        Compute current embedding depth.
        
        Args:
            cycles: Number of completed cycles
        
        Returns:
            Embedding depth [m]
        """
        self.embedding_depth = self.delta_ultimate * (1 - np.exp(-cycles / self.N_c))
        return self.embedding_depth
    
    def compute_preload_loss_embedding(self, k_system: float, cycles: int) -> float:
        """
        Compute preload loss due to embedding.
        
        Args:
            k_system: Joint stiffness [N/m]
            cycles: Number of cycles
        
        Returns:
            Preload loss [N]
        """
        delta = self.get_embedding_depth(cycles)
        return k_system * delta
    
    def get_stiffness_matrix(self) -> np.ndarray:
        """Compute 2×2 stiffness matrix"""
        k = self.k_contact
        return np.array([
            [k,  -k],
            [-k,  k]
        ])
    
    def get_damping_matrix(self) -> np.ndarray:
        """Compute 2×2 damping matrix"""
        c = 0.001 * self.k_contact
        return np.array([
            [c,  -c],
            [-c,  c]
        ])
    
    def get_force_vector(self,
                         u_local: np.ndarray,
                         v_local: np.ndarray,
                         preload: float) -> np.ndarray:
        """Compute force vector (embedding effect handled separately)"""
        return np.zeros(2)
    
    def update_state(self,
                     u_local: np.ndarray,
                     v_local: np.ndarray,
                     preload: float,
                     dt: float):
        """Update washer-flange state"""
        self.state.normal_force = preload
        self.state.contact_pressure = preload / self.geometry.contact_area
```

---

## 8. Flange-Gasket Contact Model

### 8.1 Gasket Nonlinear Behavior

Gaskets exhibit highly nonlinear behavior:

**Loading Curve:**
$$F = F_0 \cdot (\delta / \delta_0)^n$$

**Unloading Curve (hysteresis):**
$$F = F_{max} \cdot (\delta / \delta_{max})^{n_u}$$

Where typically n_loading > n_unloading.

**Creep/Relaxation:**
$$\delta_{creep}(t) = \delta_0 \cdot C_r \cdot \log(t/t_0 + 1)$$

```python
@dataclass
class GasketProperties:
    """Gasket material and behavior properties"""
    
    gasket_type: str = 'spiral_wound'  # 'spiral_wound', 'graphite', 'ptfe', 'metal'
    
    # Stiffness parameters
    k_initial: float = 500e6       # Initial stiffness [N/m]
    n_loading: float = 0.8         # Loading exponent
    n_unloading: float = 0.5       # Unloading exponent
    
    # Reference values
    F_ref: float = 10000           # Reference force [N]
    delta_ref: float = 0.001       # Reference compression [m]
    
    # Creep parameters
    creep_coefficient: float = 0.05  # C_r
    t_ref: float = 3600            # Reference time [s] (1 hour)
    
    # Yield
    yield_stress: float = 100e6   # Gasket yield stress [Pa]
    
    # Current state
    loading_direction: int = 1     # +1 loading, -1 unloading
    max_compression: float = 0.0   # Maximum compression reached


class FlangeGasketContactElement(BaseContactElement):
    """
    Flange-gasket contact element with nonlinear behavior.
    
    Key features:
    - Nonlinear stiffness (loading curve)
    - Hysteresis (loading ≠ unloading)
    - Creep/relaxation
    - Sealing stress tracking
    """
    
    def __init__(self,
                 contact_id: str,
                 dof_flange: int,
                 dof_gasket: int,
                 geometry: ContactGeometry,
                 gasket: GasketProperties = None):
        """
        Initialize flange-gasket contact.
        
        Args:
            contact_id: Unique identifier
            dof_flange: Flange axial DOF
            dof_gasket: Gasket axial DOF
            geometry: Contact geometry
            gasket: Gasket properties
        """
        dof_indices = [dof_flange, dof_gasket]
        
        super().__init__(
            contact_id=contact_id,
            contact_type=ContactType.FLANGE_GASKET,
            dof_indices=dof_indices,
            geometry=geometry
        )
        
        self.gasket = gasket if gasket else GasketProperties()
        
        # State tracking
        self.current_compression = 0.0
        self.max_compression = 0.0
        self.creep_accumulated = 0.0
        self.time_under_load = 0.0
        
    def get_tangent_stiffness(self, compression: float) -> float:
        """
        Compute tangent stiffness at current compression.
        
        k_tangent = dF/dδ = n × F_ref/δ_ref × (δ/δ_ref)^(n-1)
        """
        if compression <= 0:
            return self.gasket.k_initial
        
        n = self.gasket.n_loading if self.gasket.loading_direction > 0 else self.gasket.n_unloading
        F_ref = self.gasket.F_ref
        d_ref = self.gasket.delta_ref
        
        k_tangent = n * F_ref / d_ref * (compression / d_ref) ** (n - 1)
        
        # Limit to reasonable range
        return np.clip(k_tangent, 1e6, 1e10)
    
    def get_gasket_force(self, compression: float) -> float:
        """
        Compute gasket force at given compression.
        
        F = F_ref × (δ/δ_ref)^n
        """
        if compression <= 0:
            return 0.0
        
        n = self.gasket.n_loading if self.gasket.loading_direction > 0 else self.gasket.n_unloading
        F_ref = self.gasket.F_ref
        d_ref = self.gasket.delta_ref
        
        F = F_ref * (compression / d_ref) ** n
        
        return F
    
    def compute_creep(self, dt: float) -> float:
        """
        Compute creep increment.
        
        δ_creep(t) = δ_0 × C_r × log(t/t_0 + 1)
        
        Args:
            dt: Time increment [s]
        
        Returns:
            Creep increment [m]
        """
        C_r = self.gasket.creep_coefficient
        t_ref = self.gasket.t_ref
        
        self.time_under_load += dt
        
        # Incremental creep
        if self.current_compression > 0:
            delta_creep = self.current_compression * C_r * dt / (self.time_under_load + t_ref)
        else:
            delta_creep = 0.0
        
        self.creep_accumulated += delta_creep
        
        return delta_creep
    
    def get_stiffness_matrix(self) -> np.ndarray:
        """Compute 2×2 stiffness matrix with tangent stiffness"""
        k = self.get_tangent_stiffness(self.current_compression)
        
        return np.array([
            [k,  -k],
            [-k,  k]
        ])
    
    def get_damping_matrix(self) -> np.ndarray:
        """Compute 2×2 damping matrix (viscoelastic)"""
        # Higher damping for gaskets
        c = 0.01 * self.gasket.k_initial
        
        return np.array([
            [c,  -c],
            [-c,  c]
        ])
    
    def get_force_vector(self,
                         u_local: np.ndarray,
                         v_local: np.ndarray,
                         preload: float) -> np.ndarray:
        """Compute force vector"""
        return np.zeros(2)
    
    def update_state(self,
                     u_local: np.ndarray,
                     v_local: np.ndarray,
                     preload: float,
                     dt: float):
        """Update gasket state"""
        # Compute compression
        compression = u_local[0] - u_local[1] if len(u_local) > 1 else 0.0
        
        # Detect loading direction
        if compression > self.current_compression:
            self.gasket.loading_direction = 1  # Loading
        else:
            self.gasket.loading_direction = -1  # Unloading
        
        # Update max compression
        if compression > self.max_compression:
            self.max_compression = compression
            self.gasket.max_compression = compression
        
        self.current_compression = max(compression, 0)
        
        # Update state
        self.state.normal_force = self.get_gasket_force(compression)
        self.state.contact_pressure = self.state.normal_force / self.geometry.contact_area
```

---

## 9. Flange-Flange Metal Contact Model

### 9.1 Metal-to-Metal Contact Characteristics

For metal-to-metal (MtM) flanges without gaskets:
- Very high contact stiffness
- Microslip/fretting under cyclic loading
- Important for Junker mechanism

```python
class FlangeFlangeContactElement(BaseContactElement):
    """
    Flange-to-flange metal contact element.
    
    Used for:
    - Metal-to-metal seals
    - RTJ connections
    - Transverse DOF coupling for Junker analysis
    """
    
    def __init__(self,
                 contact_id: str,
                 dof_flange1_axial: int,
                 dof_flange2_axial: int,
                 dof_flange1_trans_y: int = None,
                 dof_flange1_trans_z: int = None,
                 dof_flange2_trans_y: int = None,
                 dof_flange2_trans_z: int = None,
                 geometry: ContactGeometry = None,
                 friction: FrictionProperties = None,
                 wear: WearProperties = None):
        """
        Initialize flange-flange contact.
        
        Args:
            contact_id: Unique identifier
            dof_flange1_axial: Flange 1 axial DOF
            dof_flange2_axial: Flange 2 axial DOF
            dof_flange1_trans_y/z: Flange 1 transverse DOFs (optional)
            dof_flange2_trans_y/z: Flange 2 transverse DOFs (optional)
            geometry: Contact geometry
            friction: Friction properties
            wear: Wear properties
        """
        # Build DOF list
        dof_indices = [dof_flange1_axial, dof_flange2_axial]
        
        self.has_transverse = False
        if dof_flange1_trans_y is not None:
            dof_indices.extend([dof_flange1_trans_y, dof_flange1_trans_z,
                               dof_flange2_trans_y, dof_flange2_trans_z])
            self.has_transverse = True
        
        super().__init__(
            contact_id=contact_id,
            contact_type=ContactType.FLANGE_FLANGE,
            dof_indices=dof_indices,
            geometry=geometry if geometry else ContactGeometry(),
            friction=friction,
            wear=wear
        )
        
        # High stiffness for metal-metal
        self.k_axial = 5e9      # N/m
        self.k_transverse = 1e8  # N/m
        
    def get_stiffness_matrix(self) -> np.ndarray:
        """Compute stiffness matrix"""
        if self.has_transverse:
            # 6×6 matrix
            K = np.zeros((6, 6))
            
            # Axial coupling (DOFs 0, 1)
            K[0, 0] = self.k_axial
            K[0, 1] = -self.k_axial
            K[1, 0] = -self.k_axial
            K[1, 1] = self.k_axial
            
            # Transverse coupling (DOFs 2,3 to 4,5)
            for i in range(2):
                K[2+i, 2+i] = self.k_transverse
                K[2+i, 4+i] = -self.k_transverse
                K[4+i, 2+i] = -self.k_transverse
                K[4+i, 4+i] = self.k_transverse
            
            return K
        else:
            # 2×2 matrix (axial only)
            k = self.k_axial
            return np.array([
                [k,  -k],
                [-k,  k]
            ])
    
    def get_damping_matrix(self) -> np.ndarray:
        """Compute damping matrix"""
        n = 6 if self.has_transverse else 2
        return 0.001 * self.get_stiffness_matrix()
    
    def get_force_vector(self,
                         u_local: np.ndarray,
                         v_local: np.ndarray,
                         preload: float) -> np.ndarray:
        """Compute force vector including friction"""
        n = 6 if self.has_transverse else 2
        F = np.zeros(n)
        
        if self.has_transverse:
            # Friction force in transverse directions
            mu = self.friction.mu_current
            F_friction_capacity = mu * preload
            
            # Transverse velocities
            vy_rel = v_local[4] - v_local[2] if len(v_local) > 4 else 0.0
            vz_rel = v_local[5] - v_local[3] if len(v_local) > 5 else 0.0
            v_mag = np.sqrt(vy_rel**2 + vz_rel**2)
            
            if v_mag > 1e-10:
                F_fy = -F_friction_capacity * vy_rel / v_mag
                F_fz = -F_friction_capacity * vz_rel / v_mag
                
                F[2] = -F_fy
                F[3] = -F_fz
                F[4] = +F_fy
                F[5] = +F_fz
        
        return F
    
    def update_state(self,
                     u_local: np.ndarray,
                     v_local: np.ndarray,
                     preload: float,
                     dt: float):
        """Update contact state"""
        self.state.normal_force = preload
        
        if self.has_transverse:
            # Check transverse slip
            vy_rel = v_local[4] - v_local[2] if len(v_local) > 4 else 0.0
            vz_rel = v_local[5] - v_local[3] if len(v_local) > 5 else 0.0
            v_mag = np.sqrt(vy_rel**2 + vz_rel**2)
            
            if v_mag > 1e-8:
                self.state.slip_state = 'gross_slip'
            else:
                self.state.slip_state = 'stick'
```

---

## References -- Part II

[1] **Yamamoto, A. (1980).** *The Theory and Computation of Threads Connection* (in Japanese), Youkendo, Tokyo. -- *Foundational treatment of thread load distribution. Threads modeled as cantilever beams with five deformation types. Basis for the Yamamoto distribution law: $\varphi_i = \sinh(\gamma(n-i+0.5)) / \Sigma\sinh(\gamma(n-j+0.5))$.*

[2] **Sopwith, D.G. (1948).** "The Distribution of Load in Screw Threads." *Proceedings of the Institution of Mechanical Engineers*, Vol. 159, pp. 373--383. DOI: [10.1243/PIME_PROC_1948_159_030_02](https://doi.org/10.1243/PIME_PROC_1948_159_030_02). -- *Classic analytical model for exponential load distribution across engaged threads. Together with Yamamoto, forms the theoretical basis for the five distribution models (Uniform, Linear, Power Law, Exponential, Yamamoto).*

[3] **Goodier, J.N. (1940).** "The Distribution of Load on the Threads of Screws." *Trans. ASME, Journal of Applied Mechanics*, Vol. 62, pp. A10--A16. -- *First analytical treatment of thread load distribution showing that the first engaged thread carries the highest fraction of the total load.*

[4] **VDI 2230 Part 1 (2015).** "Systematic Calculation of Highly Stressed Bolted Joints -- Joints with One Cylindrical Bolt." Verein Deutscher Ingenieure, Düsseldorf. -- *Defines embedding loss per interface (Table A7): $f_z = 1.5\ \mu\text{m}$ ($R_a < 1.6\ \mu\text{m}$), $2.5\ \mu\text{m}$ ($R_a$ 1.6--3.2 $\mu\text{m}$), $4.0\ \mu\text{m}$ ($R_a > 3.2\ \mu\text{m}$). Basis for the washer-flange contact embedding model.*

[5] **Bickford, J.H. (2008).** *Introduction to the Design and Behavior of Bolted Joints*, 4th ed. CRC Press, Boca Raton, FL. ISBN: 978-0-8493-8176-8. -- *Contact stiffness models, gasket behavior (loading/unloading hysteresis, creep), and effective bearing radius formula: $r_{eff} = \frac{2}{3}\frac{r_o^3 - r_i^3}{r_o^2 - r_i^2}$.*

[6] **Nassar, S.A. and Housari, B.A. (2006).** "Effect of Thread Pitch and Initial Tension on the Self-Loosening of Threaded Fasteners." *ASME Journal of Pressure Vessel Technology*, Vol. 128, No. 4, pp. 590--598. DOI: [10.1115/1.2349572](https://doi.org/10.1115/1.2349572). -- *Thread contact mechanics and helix coupling: $\Delta x_{axial} = (p/2\pi) \times \Delta\theta_{rotation}$, creating off-diagonal terms in the stiffness matrix.*

[7] **Pai, N.G. and Hess, D.P. (2002).** "Three-Dimensional Finite Element Analysis of Threaded Fastener Loosening due to Dynamic Shear Load." *Engineering Failure Analysis*, Vol. 9, No. 4, pp. 383--402. DOI: [10.1016/S1350-6307(01)00024-3](https://doi.org/10.1016/S1350-6307(01)00024-3). -- *Four slip regimes (NO_SLIP, HEAD_ONLY, NUT_ONLY, COMPLETE_SLIP) used in the bearing contact slip classification.*

[8] **Junker, G.H. (1969).** "New Criteria for Self-Loosening of Fasteners Under Vibration." *SAE Transactions*, Vol. 78, pp. 314--335. SAE Paper 690055. DOI: [10.4271/690055](https://doi.org/10.4271/690055). -- *Identifies the bearing surface and thread surface as the two critical contact zones whose simultaneous slip enables loosening.*

[9] **Hintikka, J., Lehtovaara, A., and Mantyla, A. (2020).** "Running-in in Fretting, Transition from Near-Stable Friction Regime to Gross Sliding." *Tribology International*, Vol. 143, Art. 106073. DOI: [10.1016/j.triboint.2019.106073](https://doi.org/10.1016/j.triboint.2019.106073). -- *Three-phase friction evolution model applicable to all contact types: running-in, transition, and steady-state.*

[10] **Fouvry, S., Liskiewicz, T., Kapsa, Ph., Hannel, S., and Sauger, E. (2003).** "An Energy Description of Wear Mechanisms and Its Applications to Oscillating Sliding Contacts." *Wear*, Vol. 255, No. 1--6, pp. 287--298. DOI: [10.1016/S0043-1648(03)00117-0](https://doi.org/10.1016/S0043-1648(03)00117-0). -- *Energy-based wear model applicable to fretting at flange-flange and thread contacts.*

[11] **Johnson, K.L. (1985).** *Contact Mechanics*. Cambridge University Press. ISBN: 978-0-521-34796-9. -- *Hertzian contact theory, elastic-plastic contact, and surface traction distributions used for contact stiffness estimation.*

---

**END OF PART II**

*Part III covers Matrix Assembly and Coupling*
*Parts IV--VII cover Loading, Self-Loosening, Wear, and Friction Models*
*Part VIII covers Numerical Solvers*
*Part IX covers Similitude and Scaling*
*Part X covers Preload Loss Models*
*Part XI covers the Coupled Friction-Wear-Loosening Analysis Framework*
*Part XII covers Force Excitation Functions and Rayleigh Damping*
