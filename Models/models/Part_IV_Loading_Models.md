# MSD Framework - PART IV: LOADING MODELS

**Complete Technical Reference for Bolt Analysis Studio**

**Authors:** L. Ribeiro, D. Carvalho, S.C. Naves, T. Santos, V. Marques, G. Arruda
**Institution:** internal reference - Tribology and Wear Technology Laboratory, Federal University of Uberlândia
**Project:** Petrobras R&D - Bolted Flange Joint Integrity

---

**Abstract.** This document covers the loading models implemented in the Bolt Analysis Studio, from initial preload application through dynamic excitation during operation, and extends into the stiffness-based assessment of fatigue safety. Preload -- the initial tensile force in the bolt that creates the clamping force holding the joint together -- is the single most important parameter governing joint integrity (VDI 2230, 2015; Bickford, 2008). The torque-tension relationship $T = F_p [p/(2\pi) + \mu_t d_2/(2\cos\alpha) + \mu_b r_b]$ (Motosh, 1976) quantifies how applied torque converts to bolt tension, with the nut factor $K$ providing a simplified engineering estimate. Beyond preload, the document defines the five loading types supported by the MSD framework: axial, transverse, combined, torsional, and bending. Special attention is given to transverse loading, which Junker (1969) demonstrated to be the primary driver of self-loosening. The loading data structure (`LoadingData` dataclass) and its integration with the MSD Builder GUI are described, along with the force-displacement auto-conversion for transverse excitation. All loading parameters are defined as the single source of truth in the MSD Builder, with read-only summaries propagated to the Solver Tab. The second half of this document presents the bolted joint force-extension diagram (Verspannungsschaubild) from VDI 2230, including stiffness calculations (Wileman et al., 1991), load factor derivation, and step-by-step graphical construction (Sections 20--22). The Ljubojevic and Lazovic (2023) stiffness-based dynamic safety factor $S_D = 2\sigma_A A_3 / (\Phi F_w)$ is derived in full (Sections 23--27), followed by ten cycle-resolved extensions that transform the static DSF into a state-dependent diagnostic computable at each MSD time step (Sections 28--38). See Part XII for the detailed mathematical treatment of force excitation functions (harmonic, step, pulse, random) and Rayleigh damping.

---

## 15. Preload Treatment and Application

### 15.1 Preload Definition and Importance

Preload is the initial tensile force in the bolt that creates clamping force in the joint. For API 6A applications, proper preload is critical for:

- **Sealing integrity:** Maintains gasket stress above sealing threshold
- **Fatigue resistance:** Reduces bolt stress fluctuation under cyclic loading
- **Loosening resistance:** Provides friction capacity to resist rotation
- **Joint stiffness:** Maintains joint behavior under external loads

### 15.2 Torque-Tension Relationship

$$T = K \cdot d \cdot F_p$$

Where:
- T = Applied torque [Nm]
- K = Nut factor (0.12-0.25 depending on lubrication)
- d = Nominal bolt diameter [m]
- F_p = Preload force [N]

**Expanded Form (VDI 2230):**

$$T = F_p \left[ \frac{p}{2\pi} + \frac{\mu_t \cdot d_2}{2\cos\alpha} + \mu_b \cdot r_{bearing} \right]$$

Where:
- p = Thread pitch [m]
- μ_t = Thread friction coefficient
- d_2 = Pitch diameter [m]
- α = Half flank angle [rad]
- μ_b = Bearing friction coefficient
- r_bearing = Effective bearing radius [m]

### 15.3 Nut Factor Values

| Condition | K Range | Typical K |
|-----------|---------|-----------|
| Dry, unlubricated | 0.20-0.25 | 0.22 |
| Machine oil | 0.15-0.18 | 0.16 |
| MoS₂ grease | 0.12-0.15 | 0.13 |
| PTFE coating | 0.10-0.14 | 0.12 |
| Wax/Anti-seize | 0.13-0.17 | 0.15 |
| Zinc-phosphate | 0.14-0.18 | 0.16 |

### 15.4 Preload Application Implementation

```python
from dataclasses import dataclass
from typing import Tuple, Dict
import numpy as np


@dataclass
class PreloadSpecification:
    """Preload specification for bolted joint"""
    
    # Target preload
    target_preload: float           # N
    
    # Application method
    method: str = 'torque'          # 'torque', 'tension', 'angle', 'yield'
    
    # Torque method parameters
    applied_torque: float = None    # Nm (if method='torque')
    nut_factor: float = 0.15        # K factor
    
    # Angle method parameters (turn-of-nut)
    snug_torque: float = None       # Nm (snug tight torque)
    turn_angle: float = None        # degrees
    
    # Yield method parameters
    yield_percentage: float = 0.70  # Fraction of yield preload
    
    # Preload range (for tolerance analysis)
    preload_min: float = None       # N
    preload_max: float = None       # N
    
    def __post_init__(self):
        """Calculate preload range if not specified"""
        if self.preload_min is None:
            self.preload_min = 0.85 * self.target_preload  # -15%
        if self.preload_max is None:
            self.preload_max = 1.15 * self.target_preload  # +15%


class PreloadSolver:
    """
    Solves for initial preload state in bolted joint.
    
    Two-stage approach:
    1. Static preload analysis (find equilibrium)
    2. Set as initial state for dynamic analysis
    """
    
    def __init__(self,
                 k_bolt: float,
                 k_member: float,
                 dof_bolt_head: int,
                 dof_nut: int,
                 dof_flanges: Tuple[int, int],
                 n_dof: int):
        """
        Initialize preload solver.
        
        Args:
            k_bolt: Bolt stiffness [N/m]
            k_member: Member stiffness [N/m]
            dof_bolt_head: DOF index for bolt head
            dof_nut: DOF index for nut
            dof_flanges: DOF indices for flanges (tuple)
            n_dof: Total number of DOFs
        """
        self.k_b = k_bolt
        self.k_m = k_member
        self.dof_head = dof_bolt_head
        self.dof_nut = dof_nut
        self.dof_fl1 = dof_flanges[0]
        self.dof_fl2 = dof_flanges[1]
        self.n_dof = n_dof
        
        # Load factor
        self.phi = k_bolt / (k_bolt + k_member)
        
    def compute_preload_from_torque(self,
                                     torque: float,
                                     nut_factor: float,
                                     bolt_diameter: float) -> float:
        """
        Compute preload from applied torque.
        
        F_p = T / (K × d)
        """
        return torque / (nut_factor * bolt_diameter)
    
    def compute_torque_from_preload(self,
                                     preload: float,
                                     nut_factor: float,
                                     bolt_diameter: float) -> float:
        """
        Compute required torque for target preload.
        
        T = K × d × F_p
        """
        return nut_factor * bolt_diameter * preload
    
    def solve_preload_equilibrium(self, 
                                   F_preload: float,
                                   K: np.ndarray) -> np.ndarray:
        """
        Solve static equilibrium under preload.
        
        Preload creates:
        - Bolt elongation: δ_b = F_p / k_b
        - Member compression: δ_m = F_p / k_m
        
        Args:
            F_preload: Target preload [N]
            K: Global stiffness matrix
        
        Returns:
            Equilibrium displacement vector
        """
        # Create preload force vector
        F = np.zeros(self.n_dof)
        
        # Apply as displacement-controlled
        # Bolt elongation
        delta_bolt = F_preload / self.k_b
        
        # For displacement control, modify K and F
        K_mod = K.copy()
        F_mod = F.copy()
        
        # Apply bolt stretch as prescribed displacement
        # This is simplified - full implementation would use penalty or Lagrange
        
        # Alternative: directly set initial displacements
        u_initial = np.zeros(self.n_dof)
        u_initial[self.dof_head] = 0.0
        u_initial[self.dof_nut] = delta_bolt
        
        # Member compression distributed
        delta_member = F_preload / self.k_m
        # This compression is distributed across flanges
        
        return u_initial
    
    def get_preload_force_vector(self, F_preload: float) -> np.ndarray:
        """
        Create preload force vector for force-controlled solution.
        
        Returns:
            Self-equilibrating force vector
        """
        F = np.zeros(self.n_dof)
        
        # Bolt head reaction (compression on washer)
        F[self.dof_head] = -F_preload
        
        # Nut reaction (compression on washer)  
        F[self.dof_nut] = -F_preload
        
        # Flange reactions (tension to balance)
        F[self.dof_fl1] = +F_preload
        F[self.dof_fl2] = +F_preload
        
        # Verify self-equilibrium
        if abs(np.sum(F)) > 1e-6:
            raise ValueError("Preload force vector is not self-equilibrating")
        
        return F
    
    def compute_joint_diagram(self,
                               F_preload: float,
                               F_external_max: float) -> Dict:
        """
        Compute joint diagram parameters.
        
        The joint diagram shows:
        - Working line slopes for bolt and member
        - Load sharing based on stiffness ratio
        - Safety margins
        
        Returns:
            Dictionary with joint diagram parameters
        """
        k_b = self.k_b
        k_m = self.k_m
        phi = self.phi
        
        # At preload
        delta_preload = F_preload / k_b  # Bolt elongation
        
        # Under external load
        F_bolt_max = F_preload + phi * F_external_max
        F_clamp_min = F_preload - (1 - phi) * F_external_max
        
        # Separation force
        F_separation = F_preload / (1 - phi)
        
        # Bolt stress change
        delta_F_bolt = phi * F_external_max
        
        return {
            'preload': F_preload,
            'load_factor_phi': phi,
            'bolt_force_max': F_bolt_max,
            'clamp_force_min': F_clamp_min,
            'separation_force': F_separation,
            'bolt_force_change': delta_F_bolt,
            'bolt_elongation': delta_preload,
            'safety_margin_separation': F_separation - F_external_max
        }
```

### 15.5 Load Factor and Joint Stiffness

**Load Factor Definition:**

$$\Phi = \frac{k_b}{k_b + k_m}$$

**Physical Meaning:**
- Φ × F_ext goes to increasing bolt force
- (1-Φ) × F_ext goes to reducing clamping force

**Typical Values:**
- Φ ≈ 0.1-0.2 for soft gaskets
- Φ ≈ 0.2-0.4 for metal-to-metal

**Bolt Force Under External Load:**

$$F_{bolt} = F_p + \Phi \cdot F_{ext}$$

**Clamping Force Under External Load:**

$$F_{clamp} = F_p - (1-\Phi) \cdot F_{ext}$$

**Joint Separation Condition:**

$$F_{ext} > \frac{F_p}{1-\Phi}$$

---

## 16. External Axial Loading

### 16.1 Load Types

| Type | Characteristic | Mathematical Form |
|------|---------------|-------------------|
| **Static** | Constant | F(t) = F₀ |
| **Pulsating** | 0 to max | F(t) = F_m + F_a sin(ωt), F_m = F_a |
| **Alternating** | ±max | F(t) = F_a sin(ωt) |
| **Random** | Spectrum | F(t) = Σ F_i sin(ω_i t + φ_i) |

### 16.2 Load Distribution

```python
def compute_axial_load_effects(F_external: float,
                                phi: float,
                                F_preload: float) -> Dict:
    """
    Compute effects of external axial load on joint.
    
    Args:
        F_external: External axial force [N] (positive = tension)
        phi: Load factor
        F_preload: Initial preload [N]
    
    Returns:
        Dictionary with force changes
    """
    # Bolt force change
    delta_F_bolt = phi * F_external
    
    # Clamping force change
    delta_F_clamp = -(1 - phi) * F_external
    
    # New forces
    F_bolt = F_preload + delta_F_bolt
    F_clamp = F_preload + delta_F_clamp
    
    # Check separation
    separated = F_clamp <= 0
    
    if separated:
        # After separation, all load goes to bolt
        F_bolt = F_preload + F_external
        F_clamp = 0
    
    return {
        'delta_F_bolt': delta_F_bolt,
        'delta_F_clamp': delta_F_clamp,
        'F_bolt_total': F_bolt,
        'F_clamp_total': F_clamp,
        'separated': separated
    }
```

### 16.3 Force Vector Assembly for Axial Loading

```python
def assemble_axial_load_vector(F_axial: float,
                                dof_application: int,
                                dof_reaction: int,
                                n_dof: int) -> np.ndarray:
    """
    Assemble external axial load vector.
    
    Axial load is applied at one flange, reacted at other.
    """
    F = np.zeros(n_dof)
    
    F[dof_application] = +F_axial
    F[dof_reaction] = -F_axial
    
    return F
```

---

## 17. External Transverse (Shear) Loading

### 17.1 Critical Role in Self-Loosening

Transverse loading is the PRIMARY driver of self-loosening (Junker mechanism, 1969):

1. Transverse load overcomes bearing friction
2. Allows relative rotation between nut and joint
3. Pitch torque drives nut rotation (loosening)
4. Preload decreases due to nut back-off

**Critical Threshold:**

$$F_{trans,crit} = \mu_b \cdot F_p$$

When F_trans > F_trans,crit, the bearing surface begins to slip.

### 17.2 Junker Test Parameters (DIN 65151)

| Parameter | Standard Value | Notes |
|-----------|---------------|-------|
| Transverse amplitude | ±0.65 mm | Total displacement 1.3 mm |
| Frequency | 12.5 Hz | 750 cycles/min |
| Duration | 2000 cycles | Or until failure criterion |
| Preload range | 70-90% proof | Depends on application |
| Failure criterion | 20% preload loss | Or visible loosening |

### 17.3 Transverse Loading Implementation

```python
@dataclass
class TransverseLoadingParameters:
    """Parameters for transverse (Junker) loading"""
    
    amplitude: float = 0.65e-3      # m (default DIN 65151)
    frequency: float = 12.5         # Hz
    waveform: str = 'sine'          # 'sine', 'triangle', 'square'
    phase: float = 0.0              # rad
    
    @property
    def omega(self) -> float:
        """Angular frequency [rad/s]"""
        return 2 * np.pi * self.frequency
    
    @property
    def period(self) -> float:
        """Period [s]"""
        return 1.0 / self.frequency
    
    @property
    def peak_velocity(self) -> float:
        """Peak transverse velocity [m/s]"""
        return self.amplitude * self.omega


class TransverseLoadingModel:
    """
    Model for transverse loading effects on bolted joint.
    
    Key effects:
    - Overcomes bearing friction → enables rotation
    - Reduces effective thread friction
    - Drives Junker self-loosening mechanism
    """
    
    def __init__(self,
                 params: TransverseLoadingParameters,
                 k_transverse: float,
                 mu_bearing: float,
                 mu_thread: float):
        """
        Initialize transverse loading model.
        
        Args:
            params: Transverse loading parameters
            k_transverse: Transverse stiffness [N/m]
            mu_bearing: Bearing friction coefficient
            mu_thread: Thread friction coefficient
        """
        self.params = params
        self.k_trans = k_transverse
        self.mu_b = mu_bearing
        self.mu_t = mu_thread
        
        # State tracking
        self.bearing_slipping = False
        self.thread_slipping = False
        
    def get_displacement(self, t: float) -> float:
        """Get transverse displacement at time t"""
        A = self.params.amplitude
        omega = self.params.omega
        phi = self.params.phase
        
        if self.params.waveform == 'sine':
            return A * np.sin(omega * t + phi)
        elif self.params.waveform == 'triangle':
            return A * (2/np.pi) * np.arcsin(np.sin(omega * t + phi))
        else:  # square
            return A * np.sign(np.sin(omega * t + phi))
    
    def get_velocity(self, t: float) -> float:
        """Get transverse velocity at time t"""
        A = self.params.amplitude
        omega = self.params.omega
        phi = self.params.phase
        
        if self.params.waveform == 'sine':
            return A * omega * np.cos(omega * t + phi)
        else:
            # Numerical derivative for other waveforms
            dt = 1e-6
            return (self.get_displacement(t + dt) - self.get_displacement(t - dt)) / (2 * dt)
    
    def get_force(self, t: float) -> float:
        """Get transverse force at time t"""
        return self.k_trans * self.get_displacement(t)
    
    def check_slip_condition(self, preload: float, t: float) -> Dict:
        """
        Check slip conditions at bearing and thread.
        
        Returns:
            Dictionary with slip status
        """
        F_trans = abs(self.get_force(t))
        
        # Bearing slip threshold
        F_bearing_capacity = self.mu_b * preload
        self.bearing_slipping = F_trans > F_bearing_capacity
        
        # Thread friction reduction when bearing slips
        if self.bearing_slipping:
            # Effective thread friction reduced by transverse motion
            slip_ratio = F_trans / (self.mu_b * preload)
            mu_thread_eff = self.mu_t * np.sqrt(max(0, 1 - slip_ratio**2))
        else:
            mu_thread_eff = self.mu_t
        
        return {
            'bearing_slipping': self.bearing_slipping,
            'bearing_slip_margin': F_bearing_capacity - F_trans,
            'mu_thread_effective': mu_thread_eff,
            'F_transverse': F_trans,
            'F_bearing_capacity': F_bearing_capacity
        }
    
    def compute_loosening_potential(self, preload: float, t: float) -> float:
        """
        Compute loosening potential at current state.
        
        Loosening occurs when:
        T_pitch > T_thread_eff + T_bearing_eff
        
        Returns:
            Loosening potential (>0 means loosening possible)
        """
        slip_status = self.check_slip_condition(preload, t)
        
        if not slip_status['bearing_slipping']:
            return -1.0  # No loosening possible without bearing slip
        
        # This would need thread geometry - simplified here
        # Return normalized loosening potential
        return slip_status['mu_thread_effective'] - self.mu_t
```

---

## 18. Thermal Loading

### 18.1 Thermal Effects on Bolted Joints

**Three Primary Effects:**

1. **Differential Expansion:** Different materials expand at different rates
2. **Property Changes:** Elastic modulus and yield strength change with temperature
3. **Friction Changes:** Friction coefficients may change with temperature

### 18.2 Thermal Strain and Preload Change

**Thermal Strain:**

$$\epsilon_{thermal} = \alpha \cdot \Delta T$$

**Preload Change from Differential Expansion:**

$$\Delta F_p = k_{joint} \cdot (\Delta L_{bolt} - \Delta L_{flange})$$

$$\Delta F_p = k_{joint} \cdot L_{grip} \cdot (\alpha_{bolt} - \alpha_{flange}) \cdot \Delta T$$

Where:
- k_joint = Combined joint stiffness
- L_grip = Grip length
- α = Coefficient of thermal expansion [1/°C]

### 18.3 Material Properties vs Temperature

**Elastic Modulus:**

$$E(T) = E_0 \cdot [1 - \beta_E (T - T_0)]$$

Where β_E ≈ 3-5 × 10⁻⁴ /°C for steel

**Yield Strength:**

$$S_y(T) = S_{y,0} \cdot [1 - \beta_y (T - T_0)]$$

Where β_y ≈ 5-8 × 10⁻⁴ /°C for steel

### 18.4 Thermal Loading Implementation

```python
@dataclass
class ThermalProperties:
    """Thermal properties for a material"""
    
    alpha: float = 12e-6            # Thermal expansion [1/°C]
    E_ref: float = 210e9            # Reference modulus [Pa]
    T_ref: float = 20.0             # Reference temperature [°C]
    beta_E: float = 3e-4            # Modulus reduction coefficient [1/°C]
    
    def get_modulus(self, T: float) -> float:
        """Get elastic modulus at temperature T"""
        return self.E_ref * (1 - self.beta_E * (T - self.T_ref))
    
    def get_thermal_strain(self, T: float, T_initial: float = None) -> float:
        """Get thermal strain from temperature change"""
        if T_initial is None:
            T_initial = self.T_ref
        return self.alpha * (T - T_initial)


class ThermalLoadingModel:
    """
    Model for thermal effects on bolted joint.
    
    Handles:
    - Differential expansion between bolt and flanges
    - Temperature-dependent material properties
    - Thermal cycling effects
    """
    
    def __init__(self,
                 bolt_thermal: ThermalProperties,
                 flange_thermal: ThermalProperties,
                 grip_length: float,
                 k_bolt: float,
                 k_member: float):
        """
        Initialize thermal model.
        
        Args:
            bolt_thermal: Bolt thermal properties
            flange_thermal: Flange thermal properties
            grip_length: Total grip length [m]
            k_bolt: Bolt stiffness [N/m]
            k_member: Member stiffness [N/m]
        """
        self.bolt = bolt_thermal
        self.flange = flange_thermal
        self.L_grip = grip_length
        self.k_b = k_bolt
        self.k_m = k_member
        
        # Joint stiffness
        self.k_joint = (k_bolt * k_member) / (k_bolt + k_member)
        
        # Reference temperature
        self.T_ref = 20.0  # °C
        
    def compute_preload_change(self, T_current: float, T_initial: float = None) -> float:
        """
        Compute preload change due to temperature change.
        
        ΔF_p = k_joint × L_grip × (α_bolt - α_flange) × ΔT
        
        Positive ΔF_p means preload INCREASES (bolt expands more than flange)
        """
        if T_initial is None:
            T_initial = self.T_ref
        
        dT = T_current - T_initial
        
        # Differential expansion
        delta_alpha = self.bolt.alpha - self.flange.alpha
        
        # Preload change
        delta_F = self.k_joint * self.L_grip * delta_alpha * dT
        
        return delta_F
    
    def get_temperature_cycle(self, 
                               T_min: float,
                               T_max: float,
                               period: float,
                               t: float) -> float:
        """Get temperature at time t for thermal cycling"""
        T_mean = (T_max + T_min) / 2
        T_amp = (T_max - T_min) / 2
        
        return T_mean + T_amp * np.sin(2 * np.pi * t / period)
    
    def compute_thermal_ratcheting(self,
                                    T_min: float,
                                    T_max: float,
                                    preload_initial: float,
                                    n_cycles: int) -> np.ndarray:
        """
        Compute preload evolution under thermal cycling.
        
        Thermal ratcheting can cause cumulative preload loss
        due to plastic deformation at temperature extremes.
        
        Returns:
            Array of preload values after each cycle
        """
        preload = preload_initial
        preload_history = [preload]
        
        for cycle in range(n_cycles):
            # Heating phase
            dF_heat = self.compute_preload_change(T_max, T_min)
            
            # Cooling phase - may not fully recover
            # Simplified: small permanent loss each cycle
            permanent_loss = 0.001 * abs(dF_heat)  # 0.1% per cycle
            
            preload = max(0, preload - permanent_loss)
            preload_history.append(preload)
        
        return np.array(preload_history)
```

---

## 19. Combined Loading Scenarios

### 19.1 Load Superposition

For linear systems, loads can be superimposed:

$$\{F_{total}\} = \{F_{preload}\} + \{F_{axial}\} + \{F_{transverse}\} + \{F_{thermal}\} + \{F_{bending}\}$$

### 19.2 Loading Protocol Definition

```python
@dataclass
class LoadingProtocol:
    """Complete loading protocol specification"""
    
    # Preload
    preload: float                    # N
    
    # Axial loading
    axial_mean: float = 0.0           # N
    axial_amplitude: float = 0.0       # N
    axial_frequency: float = 0.0       # Hz
    axial_phase: float = 0.0           # rad
    
    # Transverse loading
    trans_amplitude: float = 0.0       # m
    trans_frequency: float = 0.0       # Hz
    trans_phase: float = 0.0           # rad
    
    # Thermal loading
    T_initial: float = 20.0            # °C
    T_operating: float = 20.0          # °C
    thermal_cycling: bool = False
    T_min: float = None                # °C
    T_max: float = None                # °C
    thermal_period: float = None       # s
    
    # Duration
    n_cycles: int = 1000
    
    def get_total_force(self, t: float, dof_map: Dict, n_dof: int) -> np.ndarray:
        """Get total force vector at time t"""
        F = np.zeros(n_dof)
        
        # Axial component
        if self.axial_amplitude > 0:
            F_ax = self.axial_mean + self.axial_amplitude * np.sin(
                2 * np.pi * self.axial_frequency * t + self.axial_phase
            )
            F[dof_map.get('axial', 0)] = F_ax
        
        # Transverse component
        if self.trans_amplitude > 0:
            # Force from displacement × stiffness
            y = self.trans_amplitude * np.sin(
                2 * np.pi * self.trans_frequency * t + self.trans_phase
            )
            # This would multiply by transverse stiffness
            F[dof_map.get('transverse', 0)] = y * 1e8  # Simplified
        
        return F


# Example: Junker test protocol
def create_junker_test_protocol(preload: float) -> LoadingProtocol:
    """Create standard Junker test protocol per DIN 65151"""
    return LoadingProtocol(
        preload=preload,
        axial_mean=0.0,
        axial_amplitude=0.0,
        trans_amplitude=0.65e-3,       # 0.65 mm
        trans_frequency=12.5,          # 12.5 Hz
        n_cycles=2000
    )
```

---

## 20. Bolted Joint Force-Extension Diagram: Overview

The **bolted joint diagram** (also known as the Verspannungsschaubild or force-deflection diagram) is the fundamental graphical tool from VDI 2230 for understanding how preload, external loads, and stiffness interact in a bolted joint. It provides a visual representation of:

- Bolt force increase under external loading
- Joint clamp force decrease under external loading
- The influence of bolt and member stiffness on load sharing
- The separation limit of the joint

Sections 20--22 provide all equations, variable definitions, and step-by-step methods to construct the diagram for **any** bolted joint configuration. The material follows VDI 2230 (2015), Bickford (2008), and the Ljubojevic and Lazovic (2023) stiffness criterion.

### 20.1 Variable Glossary and Symbol Conventions

All variables used throughout Sections 20--22 are defined below. Consistent notation follows VDI 2230 and Shigley conventions.

| Symbol | Name | Units | Definition |
|--------|------|-------|------------|
| $d$ | Nominal bolt diameter | mm | Major (shank) diameter of the bolt thread |
| $d_2$ | Pitch diameter | mm | Mean thread diameter between major and minor |
| $d_3$ | Minor diameter | mm | Root diameter of the thread |
| $d_h$ | Clearance hole diameter | mm | Bore through which the bolt passes in the joint members |
| $d_w$ | Bearing face diameter | mm | Effective contact diameter under bolt head or nut |
| $s$ | Width across flats | mm | Wrench size / hex flat-to-flat distance |
| $k$ | Bolt head height | mm | Axial height of the bolt head |
| $m$ | Nut height | mm | Axial height of the nut |
| $P$ | Thread pitch | mm | Axial advance per revolution |
| $l$ | Total bolt length | mm | End-to-end length of the bolt |
| $l_b$ | Grip length (clamped length) | mm | Distance between bolt head bearing face and nut bearing face |
| $l_t$ | Threaded length in grip | mm | Thread portion engaged within the grip zone; recommended $l_t = 2d + 6$ mm |
| $l_d$ ($l_2$) | Unthreaded shank length in grip | mm | Smooth shank portion within the grip zone |
| $l_1$ | Threaded portion length in grip | mm | Same as $l_t$ in Ljubojevic notation |
| $\zeta$ | Relative clamped length | -- | Dimensionless ratio $\zeta = l_b / d$ |
| $A_1$ | Threaded cross-sectional area | mm$^2$ | $A_1 = \frac{\pi}{4}\left(\frac{d_2 + d_3}{2}\right)^2$ |
| $A_2$ | Shank cross-sectional area | mm$^2$ | $A_2 = \frac{\pi}{4}d^2$ |
| $A_3$ | Minor diameter area | mm$^2$ | $A_3 = \frac{\pi}{4}d_3^2$ (smallest bolt cross-section) |
| $A_t$ | Tensile stress area | mm$^2$ | Effective area for bolt tensile stress calculation |
| $E$ | Elastic modulus (same material) | MPa | Young's modulus; $E = 2.1 \times 10^5$ MPa for steel |
| $E_b$ | Bolt elastic modulus | MPa | May differ from member modulus in bimetallic joints |
| $E_m$ | Member elastic modulus | MPa | May differ from bolt modulus |
| $\alpha$ | Cone half-angle (Rotscher) | deg | Pressure cone angle; experimentally $\tan\alpha = 0.4$--$0.5$, mean = 0.45 (24.2 deg) |
| $k_b$ | Bolt stiffness coefficient | N/mm | Axial force per unit elongation of the bolt |
| $k_{jm}$ ($k_m$) | Joint members stiffness | N/mm | Axial force per unit compression of the clamped members |
| $\Phi$ | Stiffness factor (load factor) | -- | $\Phi = k_b / (k_b + k_{jm})$; fraction of external load going to bolt |
| $n$ | Load introduction factor | -- | $n = 0$ at interface, $n = 1$ at bolt head; typical 0.25--0.50 |
| $F_c$ ($F_V$) | Clamping/Preload force | N | Initial bolt tension after tightening (= initial clamp force) |
| $F_w$ ($F_A$) | Working/External load | N | Axial tensile force applied to the joint in service |
| $F_b$ ($F_B$) | Total bolt force under load | N | $F_b = F_c + \Delta F_b$ |
| $F_{jm}$ | Residual clamp force under load | N | $F_{jm} = F_c - \Delta F_{jm}$ |
| $f_b$ ($\delta_b$) | Bolt elongation at preload | mm | $f_b = F_c / k_b$ |
| $f_{jm}$ ($\delta_m$) | Member compression at preload | mm | $f_{jm} = F_c / k_{jm}$ |
| $F_Z$ | Embedding/relaxation loss | N | Preload loss due to surface settling |
| $\sigma_A$ | Ultimate alternating stress | MPa | Fatigue endurance limit amplitude of the bolt |
| $S_D$ | Dynamic safety factor (DSF) | -- | $S_D = \sigma_A / \sigma_a$ |

### 20.2 Notation Cross-Reference

| Quantity | This Document | VDI 2230 | Ljubojevic (2023) | Shigley | Bickford |
|----------|--------------|----------|-------------------|---------|----------|
| Preload | $F_V$ / $F_c$ | $F_V$ | $F_c$ | $F_i$ | $F_p$ |
| External load | $F_A$ / $F_w$ | $F_A$ | $F_w$ | $P$ | $F_e$ |
| Bolt force | $F_B$ | $F_S$ | $F_b$ | $F_b$ | $F_b$ |
| Clamp force | $F_{clamp}$ | $F_{KR}$ | $F_{jm}$ | $F_m$ | $F_j$ |
| Load factor | $\Phi$ | $\Phi$ | $\Phi$ | $C$ | $\phi$ |
| Bolt stiffness | $k_b$ | $k_S$ | $k_b$ | $k_b$ | $k_b$ |
| Member stiffness | $k_m$ / $k_{jm}$ | $k_P$ | $k_{jm}$ | $k_m$ | $k_j$ |

---

## 21. Stiffness Calculations for the Joint Diagram

### 21.1 Bolt Stiffness ($k_b$)

The bolt acts as a tension spring. Its overall stiffness is the series combination of the stiffnesses of its structural parts: head, shank (threaded and unthreaded portions), and the nut engagement zone.

**Series compliance (resilience) method:**

$$\frac{1}{k_b} = \frac{1}{k_s} + \frac{1}{k_h} + \frac{1}{k_n}$$

where $k_s$ = shank stiffness, $k_h$ = bolt head stiffness, $k_n$ = nut engagement stiffness.

**Bolt shank stiffness** (variable cross-section):

$$\frac{1}{k_s} = \frac{1}{E}\left(\frac{l_1}{A_1} + \frac{l_2}{A_2}\right)$$

**Bolt head stiffness** (Ognjanovic, 2021):

$$\frac{1}{k_h} = \frac{0.15}{E \cdot k}$$

**Nut engagement stiffness** (same material bolt and nut):

$$\frac{1}{k_n} = \frac{0.8}{E \cdot d}$$

**Simplified bolt stiffness** (without head/nut contributions):

$$k_b = \frac{A_d \cdot A_t \cdot E_b}{A_d \cdot l_t + A_t \cdot l_d}$$

**Detailed VDI 2230 compliance breakdown:**

$$\delta_b = \frac{0.5 \cdot d}{E_b \cdot A_N} + \frac{l_d}{E_b \cdot A_d} + \frac{l_t}{E_b \cdot A_t} + \frac{0.5 \cdot d}{E_b \cdot A_t} + \frac{0.4 \cdot d}{E_b \cdot A_N}, \qquad k_b = 1/\delta_b$$

### 21.2 Member (Joint/Clamped Parts) Stiffness ($k_{jm}$)

The clamped members act as a compression spring. The stress distribution follows a frustum cone (Rotscher cone).

**Cone model** (Ljubojevic/Ognjanovic, for members of equal width with $l_b > d_h$):

$$k_{jm} = \frac{E\pi d_h \tan\alpha}{4.6\log\dfrac{(s+d_h)(s+\zeta d\tan\alpha - d_h)}{(s-d_h)(s+\zeta d\tan\alpha + d_h)}}$$

**For short grip lengths** ($l_b < d_h$), replace the cones with an equivalent cylinder:

$$k_{jm} = \frac{E \cdot A_{jm}}{l_b}, \quad A_{jm} = \frac{\pi}{4}(D^2 - d_h^2), \quad D = s + \frac{\zeta d}{2}\tan\alpha$$

**Shigley Frustum Cone Method** ($\alpha = 30$deg):

$$k_m = \frac{\pi E_m \cdot d \cdot \tan(\alpha)}{\ln\left[\frac{(L \tan\alpha + d_w - d)(d_w + d)}{(L \tan\alpha + d_w + d)(d_w - d)}\right]}$$

**Wileman's Empirical Correlation** (FEM-validated, error < 5%, valid for $0.5 \leq d/L \leq 2.0$):

$$k_m = 0.78952 \cdot E_m \cdot d \cdot e^{0.62914 \cdot (d/L)}$$

**For multi-material stacks:**

$$\frac{1}{k_m} = \frac{1}{k_{m1}} + \frac{1}{k_{m2}} + \cdots + \frac{1}{k_{mn}}$$

### 21.3 Load Factor (Stiffness Ratio)

**Concentric loading:**

$$\Phi = \frac{k_b}{k_b + k_{jm}} = \frac{1}{1 + \xi_k}, \qquad \xi_k = \frac{k_{jm}}{k_b}$$

$\Phi$ is the fraction of external load that additionally loads the bolt. Typical values: 0.10--0.30.

**Eccentric loading (VDI 2230):**

$$\Phi_n = n \cdot \Phi$$

where $n = 0$ (load at interface, most favorable) to $n = 1$ (load at bolt head, least favorable).

---

## 22. Force Relationships and Diagram Construction

### 22.1 Force Balance Under External Axial Load

When an external tensile working force $F_w$ is applied:

$$F_w = \Delta F_b + \Delta F_{jm}$$

where $\Delta F_b = \Phi \cdot F_w$ (bolt force increase) and $\Delta F_{jm} = (1 - \Phi) \cdot F_w$ (clamp force decrease).

**Bolt force:** $F_b = F_c + \Phi \cdot F_w$

**Clamping force:** $F_{jm} = F_c - (1 - \Phi) \cdot F_w$

**Separation condition:** $F_{w,sep} = F_c / (1 - \Phi)$

### 22.2 Deformation Relationships

At preload: $f_b = F_c / k_b$ (bolt elongation), $f_{jm} = F_c / k_{jm}$ (member compression).

Under external load, the common additional deflection is:

$$\Delta f = \frac{\Delta F_b}{k_b} = \frac{\Delta F_{jm}}{k_{jm}}$$

### 22.3 Step-by-Step Diagram Construction

**Step 1: Draw the Bolt Line.** From the origin upward-left with slope $k_b$: $F = k_b \cdot \delta_b$.

**Step 2: Draw the Member Line.** From the origin upward-right with slope $k_{jm}$: $F = k_{jm} \cdot \delta_m$.

**Step 3: Mark the Preload Point.** Horizontal line at $F = F_c$ intersecting both stiffness lines: $P_{bolt}$ at $(-F_c/k_b,\, F_c)$ and $P_{memb}$ at $(+F_c/k_{jm},\, F_c)$.

**Step 4: Apply External Load -- Construct the Load Triangle.** The bolt operating point moves **up** along the bolt line to $F_c + \Delta F_b$; the member point moves **down** to $F_c - \Delta F_{jm}$. The load triangle has vertical span $F_w = \Delta F_b + \Delta F_{jm}$.

**Step 5: Mark Critical Points.**

| Point | Force Value | Description |
|-------|-------------|-------------|
| $F_c$ | Assembly preload | Initial bolt tension = initial clamp force |
| $F_b = F_c + \Phi F_w$ | Max bolt force | Bolt force under external load |
| $F_{jm} = F_c - (1-\Phi)F_w$ | Residual clamp | Remaining joint clamping |
| $F_{w,sep} = F_c/(1-\Phi)$ | Separation load | External load causing joint opening |

**Step 6: Verify Compatibility.**

$$\Delta f = \frac{\Delta F_b}{k_b} = \frac{\Delta F_{jm}}{k_{jm}} \quad \checkmark$$

### 22.4 Hard Joint vs. Soft Joint Behavior

| Parameter | Hard Joint | Soft Joint |
|-----------|-----------|------------|
| $k_{jm} / k_b$ | $\gg 1$ (typ. 3--10) | $\ll 1$ (typ. 0.3--1) |
| $\Phi$ | 0.05 -- 0.15 | 0.30 -- 0.60+ |
| Bolt force increase | Small | Large |
| Fatigue behavior | Favorable | Unfavorable |
| Diagram shape | Tall, narrow triangle | Short, wide triangle |

### 22.5 Additional Considerations for Real Joints

**Preload losses (embedding):** $F_{V,eff} = F_V - F_Z$ where $F_Z = f_Z \cdot k_b k_{jm}/(k_b + k_{jm})$, with $f_Z \approx 3$--$10$ $\mu$m per interface.

**Thermal effects:** $\Delta F_{thermal} = (\alpha_m - \alpha_b) \cdot \Delta T \cdot L \cdot k_b k_{jm}/(k_b + k_{jm})$.

**Tightening scatter:** The tightening factor $\alpha_A = F_{M,max}/F_{M,min}$ ranges from 1.0--1.1 (hydraulic tensioning) to 1.4--1.6 (manual torque wrench).

**Post-separation behavior:** Beyond $F_{w,sep}$, the bolt carries the full external load directly: $F_b = F_w$.

### 22.6 Design Safety Factors (VDI 2230)

**Against separation:** $S_{sep} = F_{V,eff} / [(1 - \Phi_n) \cdot F_A] \geq 1.2$

**Against bolt yield:** $S_{yield} = R_{p0.2} \cdot A_t / [F_{M,max} + \Phi_n \cdot F_A] \geq 1.1$

**Fatigue (DSF):** $S_D = \sigma_A / \sigma_a \geq 1.2$ where $\sigma_a = \Phi_n \cdot \Delta F_A / (2 \cdot A_t)$

### 22.7 Worked Example -- M12 Joint

| Parameter | Value |
|-----------|-------|
| Bolt | M12 x 1.75, Property Class 10.9 |
| $A_t$ = 84.3 mm$^2$, $A_d$ = 113.1 mm$^2$, $E$ = 210,000 MPa | |
| $l_d$ = 15 mm, $l_t$ = 10 mm, $L$ = 25 mm | |
| $F_c$ = 50,000 N, $F_w$ = 15,000 N | |

**Bolt stiffness:** $k_b = 835{,}400$ N/mm

**Member stiffness (Wileman):** $k_m = 2{,}690{,}900$ N/mm

**Stiffness parameters:** $\xi_k = 3.22$, $\Phi = 0.237$

**Forces:** $\Delta F_b = 3{,}555$ N, $F_b = 53{,}555$ N, $F_{jm} = 38{,}555$ N, $F_{sep} = 65{,}530$ N

**Deflections:** $f_b = 0.0598$ mm, $f_{jm} = 0.0186$ mm, $\Delta f = 0.0043$ mm $\checkmark$

This joint has $\xi_k \approx 3.2$ (moderately hard), favorable for fatigue.

### 22.8 Quick Reference Formulas

| Quantity | Formula |
|----------|---------|
| Bolt stiffness (detailed) | $1/k_b = 1/k_s + 1/k_h + 1/k_n$ |
| Bolt stiffness (simple) | $k_b = A_d A_t E_b / (A_d l_t + A_t l_d)$ |
| Member stiffness (Wileman) | $k_m = 0.78952 \cdot E_m \cdot d \cdot e^{0.62914 \cdot d/L}$ |
| Load factor | $\Phi = k_b / (k_b + k_{jm})$ |
| Total bolt force | $F_b = F_c + \Phi \cdot F_w$ |
| Residual clamp force | $F_{jm} = F_c - (1 - \Phi) \cdot F_w$ |
| Separation load | $F_{w,sep} = F_c / (1 - \Phi)$ |
| DSF | $S_D = 2\sigma_A A_3 / (\Phi \cdot F_w) = (F_D / F_w)(1 + \xi_k)$ |

---

## 23. Stiffness-Based Dynamic Safety Factor -- Ljubojevic-Lazovic Model

This section reproduces the complete mathematical model from Ljubojevic and Lazovic (2023), which establishes bolt stiffness as a governing criterion for the dynamic load-carrying capacity of tension-loaded bolted joints. The key finding is that the dynamic safety factor $S_D = 2\sigma_A A_3 / (\Phi F_w)$ increases with decreasing joint stiffness -- achieved by increasing the relative clamped length $\zeta = l_b / d$.

### 23.1 Bolt Tightening Mechanics

During tightening, the total axial nut displacement equals bolt elongation plus member compression:

$$f = f_b + f_{jm}, \qquad F_c = k_b \cdot f_b = k_{jm} \cdot f_{jm}$$

### 23.2 Working Load Distribution

When a cyclic axial load $F_w$ acts on the joint:

$$F_w = \Delta F_b + \Delta F_{jm}, \qquad \Delta F_b = \Phi \cdot F_w, \qquad \Delta F_{jm} = (1 - \Phi) \cdot F_w$$

For a load cycling from 0 to $F_w$: bolt force amplitude = $\Delta F_b / 2$, which is the quantity relevant for fatigue.

### 23.3 DSF Definition and Derivation

The DSF is the ratio of ultimate to working stress amplitudes:

$$S_D = \frac{\sigma_A}{\sigma_a}, \qquad \sigma_a = \frac{\Delta F_b / 2}{A_3} = \frac{\Phi \cdot F_w}{2 A_3}$$

Therefore:

$$\boxed{S_D = \frac{2 \sigma_A A_3}{\Phi \cdot F_w} = \frac{F_D}{F_w}(1 + \xi_k)}$$

where $F_D = 2\sigma_A A_3$ is the **ultimate dynamic load** -- the load at which the bolt alone would fail by fatigue.

**Key conclusions:**

- $S_D$ **increases** with increasing $\xi_k$ (stiffer members relative to bolt)
- $S_D$ **increases** with decreasing $\Phi$ (more elastic bolt or stiffer members)
- The working load $F_w$ can exceed the ultimate dynamic load $F_D$ because the joint members absorb most of the load variation

---

## 24. Geometric Input Data and Stiffness Results (M6--M24)

### 24.1 Thread and Bolt Geometry (ISO Standards)

| Parameter | M6 | M8 | M10 | M12 | M14 | M16 | M18 | M20 | M22 | M24 |
|-----------|----|----|-----|-----|-----|-----|-----|-----|-----|-----|
| $d_3$ (mm) | 4.917 | 6.647 | 8.376 | 10.106 | 11.835 | 13.835 | 15.294 | 17.294 | 19.294 | 20.752 |
| $d_2$ (mm) | 5.350 | 7.188 | 9.026 | 10.863 | 12.701 | 14.701 | 16.376 | 18.376 | 20.376 | 22.051 |
| $P$ (mm) | 1.00 | 1.25 | 1.50 | 1.75 | 2.00 | 2.00 | 2.50 | 2.50 | 2.50 | 3.00 |
| $k$ (mm) | 4.0 | 5.3 | 6.4 | 7.5 | 8.8 | 10.0 | 11.5 | 12.5 | 14.0 | 15.0 |
| $m$ (mm) | 4.90 | 6.44 | 8.04 | 10.37 | 12.10 | 14.10 | 15.10 | 16.9 | 18.10 | 20.20 |
| $s$ (mm) | 10 | 13 | 17 | 19 | 22 | 24 | 27 | 30 | 32 | 36 |
| $d_h$ (mm) | 6.6 | 9.0 | 11.0 | 13.5 | 15.5 | 17.5 | 20.0 | 22.0 | 24.0 | 26.0 |

### 24.2 Cross-Sectional Areas

| Parameter | M6 | M8 | M10 | M12 | M14 | M16 | M18 | M20 | M22 | M24 |
|-----------|----|----|-----|-----|-----|-----|-----|-----|-----|-----|
| $A_1$ (mm$^2$) | 20.70 | 37.58 | 59.46 | 86.34 | 118.2 | 159.9 | 197.0 | 249.8 | 309.0 | 359.7 |
| $A_2$ (mm$^2$) | 28.27 | 50.27 | 78.54 | 113.1 | 153.9 | 201.1 | 254.5 | 314.2 | 380.1 | 452.4 |
| $A_3$ (mm$^2$) | 18.99 | 34.70 | 55.10 | 80.21 | 110.0 | 150.3 | 183.7 | 234.9 | 292.4 | 338.2 |

### 24.3 Combined Bolt Stiffness $k_b$ ($\times 10^5$ N/mm) vs. $\zeta$ and Bolt Size

| $\zeta$ | M6 | M8 | M10 | M12 | M14 | M16 | M18 | M20 | M22 | M24 |
|---------|----|----|-----|-----|-----|-----|-----|-----|-----|-----|
| 2.5 | 2.605 | 3.517 | 4.424 | 5.357 | 6.274 | 7.288 | 8.093 | 9.094 | 10.09 | 10.92 |
| 3.0 | 2.302 | 3.103 | 3.901 | 4.718 | 5.523 | 6.404 | 7.123 | 7.993 | 8.861 | 9.594 |
| 3.5 | 2.062 | 2.777 | 3.488 | 4.216 | 4.933 | 5.711 | 6.360 | 7.129 | 7.897 | 8.557 |
| 4.0 | 1.867 | 2.513 | 3.155 | 3.810 | 4.457 | 5.153 | 5.744 | 6.434 | 7.122 | 7.722 |
| 4.5 | 1.706 | 2.294 | 2.879 | 3.475 | 4.065 | 4.695 | 5.238 | 5.862 | 6.485 | 7.036 |
| 5.0 | 1.571 | 2.111 | 2.648 | 3.195 | 3.736 | 4.311 | 4.813 | 5.384 | 5.953 | 6.462 |
| 5.5 | 1.455 | 1.954 | 2.451 | 2.956 | 3.456 | 3.986 | 4.452 | 4.978 | 5.502 | 5.974 |

**Observations:** Bolt stiffness decreases with increasing $\zeta$. Larger bolts are more sensitive to stiffness change with $\zeta$.

---

## 25. DSF Analysis Results

### 25.1 Relative Stiffness and Stiffness Factor

**Key findings:**

- $\xi_k$ **increases** with increasing $\zeta$ (even though both $k_b$ and $k_{jm}$ individually decrease)
- M6 has the **highest** relative stiffness (most favorable for fatigue)
- M12 has the **lowest** relative stiffness
- For all cases: $\xi_k = 3.6$ to $6.5$; $\Phi = 0.134$ to $0.216$

### 25.2 DSF vs. Stiffness Factor (Design Chart)

For any $F_D/F_w$ ratio: $S_D = (1/\Phi) \cdot (F_D/F_w)$

| $\Phi$ | $S_D$ at $F_D/F_w = 0.5$ | $S_D$ at $F_D/F_w = 1.0$ | $S_D$ at $F_D/F_w = 1.5$ |
|---------|--------------------------|--------------------------|--------------------------|
| 0.10 | 5.0 | 10.0 | 15.0 |
| 0.14 | 3.57 | 7.14 | 10.71 |
| 0.18 | 2.78 | 5.56 | 8.33 |
| 0.22 | 2.27 | 4.55 | 6.82 |

### 25.3 DSF vs. Relative Stiffness (Design Chart)

$S_D = (1 + \xi_k) \cdot (F_D/F_w)$

| $\xi_k$ | $S_D$ at $F_D/F_w = 0.5$ | $S_D$ at $F_D/F_w = 1.0$ | $S_D$ at $F_D/F_w = 1.5$ |
|----------|--------------------------|--------------------------|--------------------------|
| 3.5 | 2.25 | 4.50 | 6.75 |
| 5.0 | 3.00 | 6.00 | 9.00 |
| 6.5 | 3.75 | 7.50 | 11.25 |

### 25.4 Design Implications

1. **Increase relative clamped length** $\zeta$ wherever possible -- reduces $\Phi$ and increases $S_D$.
2. **Stiffness is a design criterion**, not just strength -- a more elastic bolt has higher fatigue durability.
3. **Use the DSF charts** as quick design tools: determine $\Phi$ or $\xi_k$ from geometry and read off $S_D$.

### 25.5 Complete Equation Summary

$$A_1 = \frac{\pi}{4}\left(\frac{d_2 + d_3}{2}\right)^2, \quad A_2 = \frac{\pi}{4}d^2, \quad A_3 = \frac{\pi}{4}d_3^2$$

$$\frac{1}{k_b} = \frac{1}{E}\left(\frac{l_1}{A_1} + \frac{l_2}{A_2}\right) + \frac{0.15}{E \cdot k} + \frac{0.8}{E \cdot d}$$

$$k_{jm} = \frac{E\pi d_h \tan\alpha}{4.6\log\dfrac{(s+d_h)(s+\zeta d\tan\alpha - d_h)}{(s-d_h)(s+\zeta d\tan\alpha + d_h)}} \qquad (\tan\alpha = 0.45)$$

$$\xi_k = k_{jm}/k_b, \qquad \Phi = 1/(1 + \xi_k)$$

$$\boxed{S_D = \frac{F_D}{F_w} \cdot (1 + \xi_k) = \frac{2\sigma_A A_3}{\Phi \cdot F_w}}$$

---

## 26. Cycle-Resolved DSF Extensions -- Overview

The static DSF formula $S_D = 2\sigma_A A_3 / (\Phi F_w)$ treats all terms as constants. In reality, every quantity evolves over the joint's loading history: preload decays through embedding, creep, and loosening (Jiang et al., 2003); stiffness degrades through plastic deformation and fretting wear (Segalman, 2005); and fatigue damage accumulates at thread roots (Miner, 1945). Sections 26--31 develop ten extensions that transform the static DSF into a cycle-resolved, state-dependent diagnostic $S_D(N)$ computable at each MSD time step.

### 26.1 Cycle-Dependent Stiffness -- Evolving Load Factor $\Phi(N)$

The load factor is treated as static in VDI 2230 and the original Ljubojevic model. In reality, both $k_b$ and $k_{jm}$ degrade through four mechanisms:

1. **Embedding and settling** (first 5--100 cycles): $F_i(N) = F_{i0} - \Delta F_{emb} \cdot (1 - e^{-\lambda N})$ with $\lambda \approx 0.5$--$2.0$.
2. **Fretting wear** (ongoing): Archard wear depth $h_{wear} = k_w \cdot p \cdot s / H$ per cycle.
3. **Plastic deformation at thread roots**: $k_b(N) = k_{b0} \cdot [1 - \beta_p(N/N_f)^m]$ with $\beta_p \approx 0.05$--$0.15$.
4. **Contact stiffness evolution**: $K_{contact} = C \cdot F_n^\alpha$ with $\alpha \approx 0.5$--$0.9$; as preload relaxes, $k_{jm}$ drops.

The **Segalman four-parameter Iwan model** provides the most rigorous framework, representing the interface as parallel Jenkins elements with a power-law distribution of critical slip forces.

The composite evolving load factor:

$$\Phi(N) = \frac{k_b(N)}{k_b(N) + k_{jm}(N)}$$

### 26.2 Preload Decay -- Non-Monotonic DSF Trajectory

Preload loss follows the **double exponential decay model**:

$$F_c(N) = F_0 \cdot [\alpha \cdot e^{-\beta_1 N} + (1-\alpha) \cdot e^{-\beta_2 N}]$$

where $\beta_1$ captures rapid embedding/settling and $\beta_2 \ll \beta_1$ captures long-term creep.

| Parameter | Class 8.8 | Class 10.9 | Class 12.9 |
|-----------|-----------|------------|------------|
| $\alpha$ | 0.05--0.15 | 0.03--0.10 | 0.02--0.08 |
| $\beta_1$ (per cycle) | 0.005--0.05 | 0.003--0.03 | 0.002--0.02 |
| $\beta_2$ (per cycle) | $10^{-5}$--$5 \times 10^{-4}$ | $5 \times 10^{-6}$--$2 \times 10^{-4}$ | $3 \times 10^{-6}$--$10^{-4}$ |

**Coupling with DSF** reveals a counterintuitive trajectory: as preload decreases, the mean stress drops, increasing the allowable stress amplitude. **DSF initially rises.** However, once preload drops to the separation threshold, $\Phi$ jumps to 1.0 and **DSF collapses catastrophically**.

$$S_D(N) = \frac{2 \cdot \sigma_A(\sigma_m(N)) \cdot A_3}{\Phi(N) \cdot F_w}, \qquad \sigma_m(N) = F_c(N)/A_3$$

---

## 27. Mean Stress, Damage, and Dynamic Corrections

### 27.1 Mean Stress Corrections

Preloaded bolts operate at high stress ratios $R \approx 0.6$--$0.95$. The **Walker equation** provides the most physically grounded correction:

$$\sigma_{eq} = \sigma_{max}^{1-\gamma} \cdot \sigma_a^\gamma$$

The Walker exponent $\gamma$ correlates with $S_u$: $\gamma = 0.883 - 2 \times 10^{-4} \cdot S_u$ (MPa). Values: 0.72 (class 8.8), 0.68 (class 10.9), 0.64 (class 12.9).

**Important finding (Schneider, 1991):** Bolts with threads rolled after heat treatment (RAHT) are approximately insensitive to mean stress due to compressive residual stresses ($\sim -700$ MPa at thread roots).

VDI 2230 provides $\sigma_{ASV}$ directly: $\sigma_{ASV} = 0.85 \times (150/d + 45)$ MPa -- **independent of property class**.

### 27.2 Nonlinear Damage Accumulation

The **Chaboche CDM model**:

$$\frac{dD}{dN} = \left(\frac{1}{1-D}\right)^\alpha \cdot \left(\frac{\sigma_a}{M(\sigma_m)(1-D)}\right)^\beta$$

with $\beta \approx 1.7$--$2.8$ for bolt steels. Critical damage $D_c \approx 0.3$--$0.5$.

**Remaining DSF as damage accumulates (power-law):**

$$S_D(N) = S_{D,initial} \cdot (1 - D(N))^\gamma, \qquad \gamma = 1.0\text{--}1.5$$

The critical damage at which $S_D = 1.0$: $D_{cr} = 1 - (1/S_{D,initial})^{1/\gamma}$.

### 27.3 Dynamic Amplification

Under dynamic loading at frequency $\omega$: $F_{bolt,a} = \Phi_{static} \cdot F_w \cdot DAF(\omega)$ where $DAF = 1/\sqrt{(1-r^2)^2 + (2\zeta r)^2}$ and $r = \omega/\omega_n$.

Local bolt natural frequencies are 5,000--15,000 Hz -- far above the 0--100 Hz operating range, confirming DAF $\approx 1.0$ for individual bolt modes. However, **global flange modes** (50--500 Hz) can produce catastrophic amplification.

### 27.4 Thread Root Stress Concentration

Thread roots create severe stress concentrations ($K_t \approx 4.0$--$4.6$ for M16--M64). The fatigue notch factor $K_f = 1 + q(K_t - 1)$ with $K_f \approx 3.0$ (rolled threads) to 3.8 (cut threads).

**Critical rule:** If $\sigma_A$ comes from VDI 2230 $\sigma_{ASV}$ values, $K_f$ is **already embedded** and must NOT be applied again. If $\sigma_A$ comes from Marin-corrected smooth specimen data, then: $S_D = 2 \cdot S_e \cdot A_3 / (K_f \cdot \Phi \cdot F_w)$.

### 27.5 Multiaxial Criteria

The **Dang Van criterion** $\max_t[\tau(t) + a \cdot \sigma_H(t)] \leq b$ is the most validated for bolt fatigue, with $b = \tau_{-1} \approx 250$--$300$ MPa and $a \approx 0.25$--$0.33$ for high-strength bolt steels.

### 27.6 Separation Nonlinearity

A **power-law contact stiffness model** captures progressive contact opening: $k_{jm}(F_{jm}) = k_{jm0} \cdot (F_{jm}/F_i)^{n_c}$ with $n_c \approx 0.3$--$0.5$. For robust MSD integration, **hyperbolic tangent smoothing** is recommended: $k_{jm}(F_{jm}) = k_{jm0} \cdot \tanh(F_{jm}/F_{ref})$.

### 27.7 Marin Endurance Limit Corrections

$S_e = k_a \cdot k_b \cdot k_c \cdot k_d \cdot k_e \cdot S_e'$ where $S_e' = 0.5 \cdot S_{ut}$:

- $k_a$ (surface): RAHT 0.75--0.90; cut threads 0.65--0.73
- $k_b$ (size): 1.0 for axial loading
- $k_c$ (loading): 0.85 for axial
- $k_e$ (reliability): 0.897 (90%), 0.814 (99%), 0.753 (99.9%)

### 27.8 Probabilistic DSF

For **FORM implementation**, the reliability index:

$$\beta(N) = \frac{\mu_{S_D}(N) - 1}{\sigma_{S_D}(N)}$$

Target: $\beta = 3.5$--$4.0$ ($P_f \approx 2 \times 10^{-4}$ to $3 \times 10^{-5}$) for API 6A equipment.

---

## 28. Fully Coupled DSF(N) Algorithm for MSD Integration

Combining all extensions, the complete cycle-resolved DSF computation at each MSD time step:

1. **Update preload**: $F_c(N)$ via double exponential decay
2. **Update stiffnesses**: $k_b(N)$ via plastic degradation; $k_{jm}(N, F_{jm})$ via Iwan model; apply smooth separation function
3. **Compute dynamic load factor**: $\Phi_{eff}(\omega) = \Phi_{static}(N) \times DAF(\omega)$ if global modes are excited
4. **Compute bolt stress**: $\sigma_a = \Phi_{eff} \cdot F_w / (2A_3)$, $\sigma_m = F_c(N)/A_3$
5. **Apply corrections**: Mean stress via Walker; multiaxial via Dang Van; $K_f$ if using Marin-based $\sigma_A$
6. **Compute allowable amplitude**: $\sigma_{A,corrected} = S_e(\text{Marin}) / (K_f \cdot f_{MSC})$ or $\sigma_{ASV}(\text{VDI}) / k_{reliability}$
7. **Update damage**: $\Delta D$ via Chaboche CDM with cycle-jumping in stable regime
8. **Compute remaining DSF**: $S_D(N) = [2 \cdot \sigma_{A,corrected} \cdot A_3 \cdot (1-D)^\gamma] / [\Phi_{eff} \cdot F_w]$
9. **Compute probabilistic DSF**: $\beta(N) = (\mu_{S_D}(N) - 1) / \sigma_{S_D}(N)$ via FORM
10. **Check criteria**: $S_D(N) < 1.0$ (deterministic failure); $\beta(N) < \beta_{target}$ (reliability failure); $D(N) \geq D_c$ (CDM failure)

Three findings stand out: (i) preload decay creates a **non-monotonic DSF trajectory** -- the separation threshold is the critical parameter to track; (ii) conflating Marin-based and VDI-based $\sigma_A$ (applying $K_f$ to $\sigma_{ASV}$) is the most common implementation error; (iii) local bolt frequencies are far above operating ranges, so DAF is negligible for bolt modes but potentially catastrophic for global flange modes.

---

## References -- Part IV

[1] **Junker, G.H. (1969).** "New Criteria for Self-Loosening of Fasteners Under Vibration," *SAE Transactions*, Vol. 78, pp. 314--335. DOI: [10.4271/690055](https://doi.org/10.4271/690055). -- *Established transverse vibration as the primary loosening driver.*

[2] **VDI 2230 Part 1 (2015).** "Systematic Calculation of Highly Stressed Bolted Joints -- Joints with One Cylindrical Bolt," Verein Deutscher Ingenieure, Dusseldorf. -- *Preload specification, load factor $\Phi$, embedding loss, endurance limit $\sigma_{ASV}$, tightening factor $\alpha_A$.*

[3] **Jiang, Y., Zhang, M., and Lee, C.-H. (2003).** "A Study of Early Stage Self-Loosening of Bolted Joints," *ASME J. Mech. Des.*, Vol. 125, No. 3, pp. 518--526. DOI: [10.1115/1.1586936](https://doi.org/10.1115/1.1586936). -- *Two-stage loosening model; physical basis for preload decay terms.*

[4] **Bickford, J.H. (2008).** *Introduction to the Design and Behavior of Bolted Joints*, 4th ed., CRC Press. ISBN: 978-0-8493-8176-8. -- *Torque-tension relation, bolt stiffness models, joint diagram construction, preload scatter data.*

[5] **Motosh, N. (1976).** "Development of Design Charts for Bolts Preloaded up to the Plastic Range," *ASME J. Eng. Ind.*, Vol. 98, No. 3, pp. 849--851. DOI: [10.1115/1.3439041](https://doi.org/10.1115/1.3439041). -- *Extended torque-tension relationship separating pitch, thread friction, and bearing friction contributions.*

[6] **ASME PCC-1 (2019).** "Guidelines for Pressure Boundary Bolted Flange Joint Assembly," ASME, New York. -- *Assembly sequence, target preload levels, and torque procedures.*

[7] **Nassar, S.A. and Housari, B.A. (2006).** "Effect of Thread Pitch and Initial Tension on the Self-Loosening of Threaded Fasteners," *ASME J. Press. Vessel Technol.*, Vol. 128, No. 4, pp. 590--598. DOI: [10.1115/1.2349572](https://doi.org/10.1115/1.2349572). -- *Higher preload delays loosening onset.*

[8] **Pai, N.G. and Hess, D.P. (2002).** "Experimental Study of Loosening of Threaded Fasteners due to Dynamic Shear Loads," *J. Sound Vib.*, Vol. 253, No. 3, pp. 585--602. DOI: [10.1006/jsvi.2001.4006](https://doi.org/10.1006/jsvi.2001.4006). -- *Experimental validation under sinusoidal transverse loading.*

[9] **Budynas, R.G. and Nisbett, J.K. (2020).** *Shigley's Mechanical Engineering Design*, 11th ed., McGraw-Hill. ISBN: 978-0-07-339821-1. -- *Bolt/member stiffness, frustum cone model, Marin factors, fatigue safety factor methods.*

[10] **Wileman, J., Choudhury, M., and Green, I. (1991).** "Computation of Member Stiffness in Bolted Connections," *ASME J. Mech. Des.*, Vol. 113, No. 4, pp. 432--437. DOI: [10.1115/1.2912801](https://doi.org/10.1115/1.2912801). -- *FEA-derived exponential formula $k_m = 0.78952 \cdot E \cdot d \cdot \exp(0.62914 \cdot d/l)$ for member stiffness.*

[11] **Ljubojevic, P. and Lazovic, T. (2023).** "Stiffness as a Criterion of Dynamic Load Carrying Capacity of Tension-Loaded Bolted Joints," *Engineering Today*, Online First. DOI: [10.5937/engtoday2300004L](https://doi.org/10.5937/engtoday2300004L). -- *DSF formula $S_D = 2\sigma_A A_3 / (\Phi F_w)$ and its dependence on bolt size and relative clamped length.*

[12] **Ognjanovic, M. (2021).** *Machine Elements* (in Serbian), University of Belgrade. -- *Bolt geometry conventions used in the Ljubojevic model.*

[13] **Segalman, D.J. (2005).** "A Four-Parameter Iwan Model for Lap-Type Joints," *ASME J. Appl. Mech.*, Vol. 72, No. 5, pp. 752--760. DOI: [10.1115/1.1989354](https://doi.org/10.1115/1.1989354). -- *Iwan model for joint stiffness evolution under microslip.*

[14] **Miner, M.A. (1945).** "Cumulative Damage in Fatigue," *ASME J. Appl. Mech.*, Vol. 12, No. 3, pp. A159--A164. -- *Linear damage accumulation rule.*

[15] **Chaboche, J.L. (1981).** "Continuous Damage Mechanics -- A Tool to Describe Phenomena Before Crack Initiation," *Nuclear Eng. Des.*, Vol. 64, No. 2, pp. 233--247. DOI: [10.1016/0029-5493(81)90007-8](https://doi.org/10.1016/0029-5493(81)90007-8). -- *CDM framework for nonlinear damage evolution.*

[16] **Walker, K. (1970).** "The Effect of Stress Ratio During Crack Propagation and Fatigue for 2024-T3 and 7075-T6 Aluminum," *ASTM STP 462*, pp. 1--14. DOI: [10.1520/STP32032S](https://doi.org/10.1520/STP32032S). -- *Mean stress correction with material-specific exponent $\gamma$.*

[17] **Dang Van, K. (1993).** "Macro-Micro Approach in High-Cycle Multiaxial Fatigue," *ASTM STP 1191*, pp. 120--130. -- *Multiaxial fatigue criterion for thread root stress state.*

[18] **Schaumann, P. and Marten, F. (2009).** "Fatigue Resistance of High Strength Bolts with Large Diameters," *Proc. IABSE Symposium*, Bangkok, pp. 1--8. -- *Size effects on bolt fatigue for diameters larger than M36.*

[19] **Brake, M.R.W. (2018).** *The Mechanics of Jointed Structures*, Springer. DOI: [10.1007/978-3-319-56818-8](https://doi.org/10.1007/978-3-319-56818-8). -- *Extended Iwan models including Reduced Iwan Plus Pinning.*

[20] **Nassar, S.A. and Abboud, A. (2009).** "An Improved Stiffness Model for Bolted Joints," *ASME J. Mech. Des.*, Vol. 131, No. 12, Art. 121001. DOI: [10.1115/1.4000212](https://doi.org/10.1115/1.4000212). -- *Refined stiffness model for non-uniform pressure distribution.*

[21] **ISO 261 (1998)**, ISO 724 (1993), ISO 273 (1979), ISO 4032 (2012), ISO 4017 (2022). -- *Standards for metric thread profiles, clearance holes, nut and bolt dimensions.*

---

**END OF PART IV**

*Part V covers Self-Loosening Models*
*Part VI covers Wear Models*
*Part VII covers Friction Models*
*Part XI covers Coupled Analysis Framework*
*Part XII covers Force Excitation Functions and Rayleigh Damping*
