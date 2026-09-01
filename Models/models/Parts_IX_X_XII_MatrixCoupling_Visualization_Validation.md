# MSD Framework -- Supplementary: Matrix Coupling, Force Propagation, and Visualization

**Authors:** L. Ribeiro, D. Carvalho, S.C. Naves, T. Santos, V. Marques, G. Arruda
**Institution:** LTAD/UFU -- Tribology and Wear Technology Laboratory, Federal University of Uberlândia
**Project:** Petrobras R&D -- Bolted Flange Joint Integrity

---

**Abstract.** This supplementary document provides extended examples, worked derivations, and visualization details for the matrix coupling topics covered in Part III (Matrix Assembly), the coupled analysis topics of Part XI, and the force function topics of Part XII. The material includes a complete 14-DOF matrix assembly example showing how each contact type contributes to the global $[K]$, $[C]$, and $\{F\}$, a force propagation analysis tracing how external loads flow through the joint, and detailed visualization specifications for the Bolt Analysis Studio plot types. Section numbering is preserved from the original manuscript for cross-reference compatibility.

---

# SUPPLEMENTARY SECTION A: MATRIX COUPLING -- HOW ALL MODELS CONNECT

---

## 45. Complete Matrix Assembly with All Couplings

### 45.1 Overview of Matrix Coupling

The global stiffness matrix [K] contains multiple types of coupling that represent different physical phenomena:

```
╔═══════════════════════════════════════════════════════════════════════════════════╗
║                    COMPLETE MATRIX COUPLING DIAGRAM                                ║
║                    (14-DOF System with All Couplings)                             ║
╠═══════════════════════════════════════════════════════════════════════════════════╣
║                                                                                    ║
║       │ x1   x2   x3   x4   x5   x6   x7   x8   θs   θn   y1   z1   y2   z2  │  ║
║    ───┼──────────────────────────────────────────────────────────────────────┼─── ║
║    x1 │ A    B                                                               │    ║
║    x2 │ B    C    D                                                          │    ║
║    x3 │      D    E    F                             ║░░░░░░░░░░░░░░░░░░░░│    ║
║    x4 │           F    G    H                        ║ TRANSVERSE       │    ║
║    x5 │                H    I    J                   ║ COUPLING         │    ║
║    x6 │                     J    K    L              ║ (Junker)         │    ║
║    x7 │                          L    M         N  O ║░░░░░░░░░░░░░░░░░░░░│    ║
║    x8 │                               N              │                       ║
║    θs │                                   P  ─────R──│◄── HELIX COUPLING    ║
║    θn │                               O              R  S│   (Self-loosening)║
║    y1 │░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░T│                   ║
║    z1 │                                                  U│                   ║
║    y2 │                                                    V│                 ║
║    z2 │                                                      W│               ║
║    ───┴──────────────────────────────────────────────────────────────────────┴─── ║
║                                                                                    ║
║    LEGEND:                                                                         ║
║    A-M: Axial stiffness terms (component + contact)                               ║
║    N,O: Thread axial coupling                                                      ║
║    P,R: HELIX COUPLING - k_th × (p/2π) creates axial-torsional coupling           ║
║    S: Torsional stiffness (nut rotation DOF)                                       ║
║    T-W: Transverse stiffness for Junker loading                                   ║
║                                                                                    ║
║    KEY COUPLING MECHANISMS:                                                        ║
║    1. Sequential coupling (B,D,F,H,J,L): Adjacent elements share DOFs             ║
║    2. HELIX COUPLING (N,O,P,R): Thread pitch creates Δx = (p/2π)Δθ               ║
║    3. Transverse coupling: Junker mechanism loading                                ║
║    4. Friction coupling: State-dependent (in force vector)                        ║
║                                                                                    ║
╚═══════════════════════════════════════════════════════════════════════════════════╝
```

### 45.2 Detailed Matrix Assembly Algorithm

```python
class CompleteMSDMatrixAssembler:
    """
    Complete matrix assembly for bolted joint MSD system.
    
    Assembles global [M], [C], [K] matrices from:
    1. Component contributions (bulk material)
    2. Contact contributions (interface mechanics)
    3. Coupling terms (helix, friction)
    
    The assembly follows the equation:
    
    [G] = Σ [L_e]^T [G_e] [L_e]
    
    Where [G] is any global matrix, [G_e] is local element matrix,
    and [L_e] is the incidence (connectivity) matrix.
    """
    
    def __init__(self, n_dof: int = 14):
        """
        Initialize assembler.
        
        Args:
            n_dof: Total number of degrees of freedom
        """
        self.n_dof = n_dof
        self.M = np.zeros((n_dof, n_dof))
        self.C = np.zeros((n_dof, n_dof))
        self.K = np.zeros((n_dof, n_dof))
        
        # Track contributions for debugging
        self.K_contributions = {}
        
    def assemble_mass_matrix(self, components: List[Dict]) -> np.ndarray:
        """
        Assemble global mass matrix.
        
        Mass matrix is diagonal (lumped mass formulation):
        
        [M] = diag(m1, m2, ..., mn)
        
        For rotational DOFs, use rotational inertia:
        M_ii = J_i = (1/2) m r²
        
        Args:
            components: List of component dictionaries with:
                - 'dof_index': DOF index for this mass
                - 'mass': Mass value [kg]
                - 'inertia': Rotational inertia [kg·m²] (for rotational DOFs)
        
        Returns:
            Assembled mass matrix [M]
        """
        self.M = np.zeros((self.n_dof, self.n_dof))
        
        for comp in components:
            dof = comp['dof_index']
            
            if 'mass' in comp and comp['mass'] > 0:
                self.M[dof, dof] = comp['mass']
            
            if 'inertia' in comp and comp.get('is_rotational', False):
                self.M[dof, dof] = comp['inertia']
        
        return self.M
    
    def assemble_stiffness_matrix(self,
                                   contacts: List['BaseContactElement'],
                                   components: List[Dict]) -> np.ndarray:
        """
        Assemble global stiffness matrix including all couplings.
        
        The stiffness matrix has the following structure:
        
        [K] = [K_axial]   +  [K_torsional]  +  [K_helix]  +  [K_transverse]
              (diagonal)     (diagonal)        (off-diag)    (diagonal)
        
        The HELIX COUPLING is critical for self-loosening analysis:
        
        For thread contact connecting DOFs {x_nut, θ_stud, θ_nut}:
        
        [K_thread] = k_th × | 1      -λ       λ    |
                            | -λ      λ²     -λ²   |
                            | λ      -λ²      λ²   |
        
        where λ = p/(2π) is the helix coupling factor.
        
        Args:
            contacts: List of contact element objects
            components: List of component dictionaries
        
        Returns:
            Assembled stiffness matrix [K]
        """
        self.K = np.zeros((self.n_dof, self.n_dof))
        self.K_contributions = {}
        
        # 1. Component contributions (bulk stiffness)
        for comp in components:
            if 'stiffness' in comp:
                dof = comp['dof_index']
                k = comp['stiffness']
                self.K[dof, dof] += k
                self.K_contributions[f"component_{comp.get('name', dof)}"] = k
        
        # 2. Contact contributions
        for contact in contacts:
            K_local = contact.get_stiffness_matrix()
            dof_map = contact.dof_indices
            
            # Store contribution for debugging
            self.K_contributions[contact.contact_id] = {
                'K_local': K_local.copy(),
                'dof_map': dof_map
            }
            
            # Scatter to global
            for i_local, i_global in enumerate(dof_map):
                for j_local, j_global in enumerate(dof_map):
                    if i_global >= 0 and j_global >= 0:
                        self.K[i_global, j_global] += K_local[i_local, j_local]
        
        return self.K
    
    def assemble_damping_matrix(self,
                                 contacts: List['BaseContactElement'],
                                 alpha_M: float = 0.5,
                                 beta_K: float = 1e-5) -> np.ndarray:
        """
        Assemble global damping matrix.
        
        Damping has three components:
        
        [C] = α_M[M] + β_K[K] + [C_contact]
              (Rayleigh)         (friction)
        
        The contact damping includes:
        - Viscous friction: c_f = μ × F_n / v_ref
        - LuGre micro-damping: σ₁
        - Material damping at interfaces
        
        Args:
            contacts: List of contact elements
            alpha_M: Mass-proportional Rayleigh coefficient
            beta_K: Stiffness-proportional Rayleigh coefficient
        
        Returns:
            Assembled damping matrix [C]
        """
        # Rayleigh damping
        self.C = alpha_M * self.M + beta_K * self.K
        
        # Contact damping contributions
        for contact in contacts:
            C_local = contact.get_damping_matrix()
            dof_map = contact.dof_indices
            
            for i_local, i_global in enumerate(dof_map):
                for j_local, j_global in enumerate(dof_map):
                    if i_global >= 0 and j_global >= 0:
                        self.C[i_global, j_global] += C_local[i_local, j_local]
        
        return self.C
    
    def get_helix_coupling_submatrix(self,
                                      thread_contact: 'ThreadContactElement') -> Tuple[np.ndarray, List[int]]:
        """
        Extract the helix coupling submatrix for analysis.
        
        The helix coupling is the key mechanism enabling self-loosening.
        It couples axial displacement to rotation through the pitch.
        
        Returns:
            (3×3 coupling matrix, [dof_x_nut, dof_theta_stud, dof_theta_nut])
        """
        K_thread = thread_contact.get_stiffness_matrix()
        dofs = thread_contact.dof_indices
        
        return K_thread, dofs
    
    def print_matrix_structure(self, matrix: np.ndarray = None,
                                name: str = "K",
                                threshold: float = 1e-10):
        """
        Print visual representation of matrix structure.
        
        Shows non-zero pattern and identifies coupling terms.
        """
        if matrix is None:
            matrix = self.K
        
        print(f"\n{name} Matrix Structure ({self.n_dof}×{self.n_dof}):")
        print("=" * 60)
        
        # Header
        dof_labels = ['x1', 'x2', 'x3', 'x4', 'x5', 'x6', 'x7', 'x8', 
                      'θs', 'θn', 'y1', 'z1', 'y2', 'z2'][:self.n_dof]
        
        header = "    " + " ".join(f"{l:>6}" for l in dof_labels)
        print(header)
        print("    " + "-" * (7 * len(dof_labels)))
        
        for i in range(self.n_dof):
            row = f"{dof_labels[i]:>3}|"
            for j in range(self.n_dof):
                val = matrix[i, j]
                if abs(val) < threshold:
                    row += "     . "
                elif i == j:
                    row += f" {val:5.0e}" if abs(val) > 1e3 else f" {val:6.2f}"
                else:
                    # Off-diagonal (coupling)
                    row += f" {val:5.0e}" if abs(val) > 1e3 else f"[{val:5.2f}]"
            print(row)
        
        print("\nLegend: [...] = off-diagonal coupling term")
        print("        .     = zero (< threshold)")


def build_complete_msd_system(joint_config: Dict) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Build complete MSD system matrices for a bolted joint.
    
    This is the main entry point for matrix assembly.
    
    Args:
        joint_config: Dictionary with joint configuration:
            - 'bolt': Bolt geometry and material
            - 'flanges': Flange properties
            - 'gasket': Gasket properties (optional)
            - 'preload': Target preload
            - 'friction': Friction coefficients
    
    Returns:
        ([M], [C], [K]) tuple of assembled matrices
    
    Example:
        config = {
            'bolt': {
                'size': 'M20',
                'pitch': 2.5e-3,
                'length': 0.08,
                'material': 'ASTM_A320_L7'
            },
            'flanges': {
                'thickness': 0.025,
                'material': 'ASTM_A105'
            },
            'friction': {
                'mu_thread': 0.15,
                'mu_bearing': 0.15
            }
        }
        M, C, K = build_complete_msd_system(config)
    """
    # This would be implemented with full joint configuration
    # Placeholder showing structure
    
    n_dof = joint_config.get('n_dof', 14)
    
    assembler = CompleteMSDMatrixAssembler(n_dof)
    
    # ... (full implementation would process config)
    
    return assembler.M, assembler.C, assembler.K
```

### 45.3 Helix Coupling Matrix Derivation

The thread helix coupling is derived from the kinematic constraint:

**Constraint Equation:**

For relative axial displacement Δx and relative rotation Δθ:

$$\Delta x = \frac{p}{2\pi} \Delta\theta$$

**Strain Energy:**

The elastic energy stored in the thread contact:

$$U = \frac{1}{2} k_{thread} \left( \Delta x - \frac{p}{2\pi} \Delta\theta \right)^2$$

**Stiffness Matrix from Energy:**

Taking second derivatives:

$$K_{ij} = \frac{\partial^2 U}{\partial q_i \partial q_j}$$

For DOFs {x_nut, θ_stud, θ_nut}:

Let λ = p/(2π), and note:
- Δx = x_nut (relative to stud)
- Δθ = θ_nut - θ_stud (relative rotation)

$$U = \frac{1}{2} k_{th} \left( x_{nut} - \lambda(\theta_{nut} - \theta_{stud}) \right)^2$$

Taking derivatives:

$$\frac{\partial U}{\partial x_{nut}} = k_{th}(x_{nut} - \lambda\theta_{nut} + \lambda\theta_{stud})$$

$$\frac{\partial^2 U}{\partial x_{nut}^2} = k_{th}$$

$$\frac{\partial^2 U}{\partial x_{nut} \partial \theta_{stud}} = -k_{th}\lambda$$

$$\frac{\partial^2 U}{\partial x_{nut} \partial \theta_{nut}} = k_{th}\lambda$$

$$\frac{\partial^2 U}{\partial \theta_{stud}^2} = k_{th}\lambda^2$$

$$\frac{\partial^2 U}{\partial \theta_{nut}^2} = k_{th}\lambda^2$$

$$\frac{\partial^2 U}{\partial \theta_{stud} \partial \theta_{nut}} = -k_{th}\lambda^2$$

**Final Stiffness Matrix:**

$$[K_{helix}] = k_{th} \begin{bmatrix}
1 & -\lambda & \lambda \\
-\lambda & \lambda^2 & -\lambda^2 \\
\lambda & -\lambda^2 & \lambda^2
\end{bmatrix}$$

**Numerical Example (M20 × 2.5):**

- p = 2.5 mm = 0.0025 m
- λ = p/(2π) = 0.000398 m
- k_th = 5 × 10⁸ N/m

$$[K_{helix}] = \begin{bmatrix}
5.0 \times 10^8 & -1.99 \times 10^5 & 1.99 \times 10^5 \\
-1.99 \times 10^5 & 79.2 & -79.2 \\
1.99 \times 10^5 & -79.2 & 79.2
\end{bmatrix}$$

**Physical Interpretation of Coupling:**

| Matrix Term | Physical Meaning |
|-------------|------------------|
| K(1,1) = k_th | Axial stiffness of thread |
| K(1,2) = -k_th×λ | Axial force caused by stud rotation |
| K(1,3) = +k_th×λ | Axial force caused by nut rotation |
| K(2,2) = k_th×λ² | Torsional stiffness felt by stud |
| K(3,3) = k_th×λ² | Torsional stiffness felt by nut |
| K(2,3) = -k_th×λ² | Cross-coupling between rotations |

---

## 46. Force Vector Assembly and Load Distribution

### 46.1 Complete Force Vector Structure

The force vector contains all applied and reaction forces:

$$\{F\} = \{F_{preload}\} + \{F_{external}\} + \{F_{tribo}\} + \{F_{thermal}\}$$

### 46.2 Preload Force Vector

**Key Principle:** Preload is INTERNAL and SELF-EQUILIBRATING.

$$\sum_{i=1}^{n} F_{preload,i} = 0$$

```python
def assemble_preload_vector(F_preload: float,
                             dof_map: Dict,
                             n_dof: int) -> np.ndarray:
    """
    Assemble preload force vector.
    
    Preload creates:
    - TENSION in bolt (negative reaction at head and nut)
    - COMPRESSION in clamped members (positive at flanges)
    
    The sum must be zero (self-equilibrating internal force).
    
    Args:
        F_preload: Preload force magnitude [N]
        dof_map: Dictionary mapping component names to DOF indices
        n_dof: Total number of DOFs
    
    Returns:
        Preload force vector
    """
    F = np.zeros(n_dof)
    
    # Bolt in tension
    F[dof_map['bolt_head']] = -F_preload
    F[dof_map['nut']] = -F_preload
    
    # Flanges in compression
    F[dof_map['flange1']] = +F_preload
    F[dof_map['flange2']] = +F_preload
    
    # Verify self-equilibrium
    assert abs(np.sum(F)) < 1e-10, "Preload vector is not self-equilibrating!"
    
    return F
```

### 46.3 Tribological Force Vector Assembly

```python
def assemble_tribological_forces(contacts: List['BaseContactElement'],
                                   u: np.ndarray,
                                   v: np.ndarray,
                                   preload: float,
                                   n_dof: int) -> np.ndarray:
    """
    Assemble tribological force vector from all contacts.
    
    Tribological forces include:
    1. Friction forces (velocity-dependent)
    2. Friction torques (resisting rotation)
    3. LuGre/Dahl state-dependent forces
    
    These forces are NONLINEAR and STATE-DEPENDENT.
    
    Args:
        contacts: List of contact elements
        u: Current displacement vector
        v: Current velocity vector
        preload: Current preload
        n_dof: Total DOFs
    
    Returns:
        Tribological force vector
    """
    F_tribo = np.zeros(n_dof)
    
    for contact in contacts:
        dof_map = contact.dof_indices
        n_local = len(dof_map)
        
        # Get local displacements and velocities
        u_local = u[dof_map] if n_local > 0 else np.array([])
        v_local = v[dof_map] if n_local > 0 else np.array([])
        
        # Compute local tribological force
        F_local = contact.get_force_vector(u_local, v_local, preload)
        
        # Scatter to global
        for i_local, i_global in enumerate(dof_map):
            if i_global >= 0 and i_local < len(F_local):
                F_tribo[i_global] += F_local[i_local]
    
    return F_tribo
```

---

## 47. Load Path Analysis

### 47.1 Force Flow Through Joint

The load path shows how forces propagate through the joint:

```
                    LOAD PATH DIAGRAM
                    
    APPLIED TORQUE (Tightening)
           │
           ▼
    ┌──────────────────┐
    │    BOLT HEAD     │
    │                  │
    │    F_head = F_p  │ ◄── Reaction force (compression on washer)
    └────────┬─────────┘
             │
             ▼
    ╔════════════════════╗
    ║  BEARING CONTACT   ║
    ║                    ║
    ║  T_bearing = μ×F×r ║ ◄── Friction torque (resists tightening)
    ║                    ║
    ║  Wear, COF evolve  ║
    ╚════════╤═══════════╝
             │
             ▼
    ┌──────────────────┐
    │    WASHER 1      │
    │                  │
    │  Load spreading  │
    │  Embedding       │
    └────────┬─────────┘
             │
             ▼
    ┌────────────────────────────────────────────┐
    │              FLANGE 1                       │
    │                                            │
    │         RÖTSCHER CONE                      │
    │              ╱╲                            │
    │             ╱  ╲                           │
    │            ╱    ╲ 30°                      │
    │           ╱      ╲                         │
    │          ╱        ╲                        │
    │         ╱ PRESSURE ╲                       │
    │        ╱  DISTRIBUTION                     │
    │       ╱              ╲                     │
    │      ╱                ╲                    │
    │                                            │
    │      k_m = πEd·tanα / ln[...]             │
    └────────────────┬───────────────────────────┘
                     │
                     ▼
    ╔════════════════════════════════════════════╗
    ║              GASKET                         ║
    ║                                            ║
    ║  Nonlinear: F = f(δ)                      ║
    ║  Creep: δ(t) = δ₀ + Cr×log(t/t₀+1)       ║
    ║  Hysteresis: Loading ≠ Unloading          ║
    ║                                            ║
    ║  Sealing stress: σ_gasket = F_p / A_g    ║
    ╚════════════════════╤═══════════════════════╝
                         │
                         ▼
    ┌────────────────────────────────────────────┐
    │              FLANGE 2                       │
    │                                            │
    │         (Mirror of Flange 1)               │
    └────────────────┬───────────────────────────┘
                     │
                     ▼
    ┌──────────────────┐
    │    WASHER 2      │
    └────────┬─────────┘
             │
             ▼
    ╔════════════════════╗
    ║  BEARING CONTACT   ║
    ║  (Nut-Washer)      ║
    ║                    ║
    ║  T_bearing = μ×F×r ║ ◄── Second friction torque
    ╚════════╤═══════════╝
             │
             ▼
    ┌──────────────────┐
    │       NUT        │
    │                  │
    │  θ_nut rotation  │ ◄── LOOSENING occurs here
    └────────┬─────────┘
             │
             ▼
    ╔══════════════════════════════════════════════════╗
    ║              THREAD CONTACT                       ║
    ║                                                  ║
    ║  ┌─────────────────────────────────────────┐    ║
    ║  │  HELIX COUPLING:                        │    ║
    ║  │                                         │    ║
    ║  │  Δx_axial = (p/2π) × Δθ_rotation       │    ║
    ║  │                                         │    ║
    ║  │  This is the KEY to self-loosening!    │    ║
    ║  └─────────────────────────────────────────┘    ║
    ║                                                  ║
    ║  Torque balance:                                ║
    ║                                                  ║
    ║  T_pitch = F_p × p/(2π)      ← Drives loosening║
    ║  T_thread = μ×F×d₂/(2cosα)   ← Resists         ║
    ║  T_bearing (above)           ← Resists         ║
    ║                                                  ║
    ║  LOOSENING CONDITION:                           ║
    ║  T_pitch > T_thread + T_bearing                 ║
    ╚══════════════════════════════════════════════════╝
             │
             ▼
    ┌──────────────────┐
    │      STUD        │
    │                  │
    │  Preload stored  │
    │  F_p = k_b × δ_b │
    │                  │
    │  Torsion from    │
    │  thread friction │
    └──────────────────┘
```

### 47.2 Force Distribution Analysis

```python
class LoadPathAnalyzer:
    """
    Analyze force distribution through bolted joint.
    
    Tracks:
    - Axial forces at each interface
    - Friction forces and torques
    - Load sharing among threads
    - Pressure distribution
    """
    
    def __init__(self,
                 contacts: List['BaseContactElement'],
                 thread_element: 'ThreadContactElement',
                 k_bolt: float,
                 k_member: float):
        """
        Initialize load path analyzer.
        
        Args:
            contacts: List of all contacts
            thread_element: Thread contact (for thread analysis)
            k_bolt: Bolt stiffness
            k_member: Member stiffness
        """
        self.contacts = contacts
        self.thread = thread_element
        self.k_b = k_bolt
        self.k_m = k_member
        self.phi = k_bolt / (k_bolt + k_member)  # Load factor
        
    def analyze_under_load(self,
                           preload: float,
                           F_external: float = 0.0,
                           F_transverse: float = 0.0) -> Dict:
        """
        Analyze force distribution under given loading.
        
        Args:
            preload: Current preload [N]
            F_external: External axial force [N]
            F_transverse: External transverse force [N]
        
        Returns:
            Dictionary with force analysis results
        """
        results = {}
        
        # Bolt force
        results['F_bolt'] = preload + self.phi * F_external
        
        # Clamping force
        results['F_clamp'] = preload - (1 - self.phi) * F_external
        
        # Check separation
        results['separated'] = results['F_clamp'] <= 0
        
        # Bearing forces
        results['F_bearing_head'] = preload  # Normal force on bearing
        results['F_bearing_nut'] = preload
        
        # Friction torques
        for contact in self.contacts:
            if hasattr(contact, 'compute_bearing_torque'):
                name = contact.contact_id
                T = contact.compute_bearing_torque(preload)
                results[f'T_{name}'] = T
        
        # Thread load distribution
        if self.thread is not None:
            thread_summary = self.thread.get_thread_summary()
            results['thread_loads'] = thread_summary['threads']
            results['total_loosening_deg'] = thread_summary['total_loosening_deg']
        
        # Loosening analysis
        if self.thread is not None:
            torques = self.thread.compute_torque_components(preload)
            results['T_pitch'] = torques['T_pitch']
            results['T_thread'] = torques['T_thread']
            results['T_resistance'] = torques['T_resistance']
            results['loosening_possible'] = torques['loosening_possible']
        
        # Slip check
        if F_transverse > 0:
            mu_eff = 0.15  # Effective friction
            slip_force = mu_eff * preload
            results['slip_margin'] = slip_force - abs(F_transverse)
            results['slipping'] = results['slip_margin'] < 0
        
        return results
    
    def print_load_path_summary(self, preload: float, F_external: float = 0):
        """Print formatted load path summary."""
        results = self.analyze_under_load(preload, F_external)
        
        print("\n" + "=" * 60)
        print("LOAD PATH ANALYSIS SUMMARY")
        print("=" * 60)
        
        print(f"\nInput:")
        print(f"  Preload: {preload/1000:.1f} kN")
        print(f"  External axial: {F_external/1000:.1f} kN")
        print(f"  Load factor φ: {self.phi:.3f}")
        
        print(f"\nForce Distribution:")
        print(f"  Bolt force: {results['F_bolt']/1000:.1f} kN")
        print(f"  Clamping force: {results['F_clamp']/1000:.1f} kN")
        print(f"  Status: {'SEPARATED!' if results['separated'] else 'Intact'}")
        
        if 'T_pitch' in results:
            print(f"\nTorque Analysis:")
            print(f"  Pitch torque (drives loosening): {results['T_pitch']:.2f} Nm")
            print(f"  Thread friction (resists): {results['T_thread']:.2f} Nm")
            print(f"  Total resistance: {results['T_resistance']:.2f} Nm")
            status = "LOOSENING POSSIBLE" if results['loosening_possible'] else "Stable"
            print(f"  Status: {status}")
        
        if 'thread_loads' in results:
            print(f"\nThread Load Distribution:")
            for t in results['thread_loads'][:5]:  # Show first 5
                print(f"  Thread {t['index']+1}: {t['load_fraction_pct']:.1f}% "
                      f"({t['slip_state']})")
        
        print("=" * 60)
```

---

# PART X: VISUALIZATION AND POST-PROCESSING

---

## 53. Time History Plots

### 53.1 Complete Visualization System

```python
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.animation import FuncAnimation
import numpy as np
from typing import Dict, List, Tuple, Optional


class MSDVisualizationSystem:
    """
    Complete visualization system for MSD analysis results.
    
    Provides:
    - Time history plots
    - Preload decay curves
    - Phase space diagrams
    - Wear evolution
    - Friction maps
    - Matrix visualization
    - Animations
    """
    
    def __init__(self, style: str = 'default', figsize: Tuple = (12, 8)):
        """
        Initialize visualization system.
        
        Args:
            style: Matplotlib style ('default', 'dark', 'publication')
            figsize: Default figure size
        """
        self.figsize = figsize
        self._setup_style(style)
        
    def _setup_style(self, style: str):
        """Configure matplotlib style"""
        if style == 'dark':
            plt.style.use('dark_background')
            self.colors = {
                'primary': '#00ff88',
                'secondary': '#ff6b6b',
                'accent': '#4ecdc4',
                'text': '#ffffff',
                'grid': '#333333'
            }
        elif style == 'publication':
            plt.rcParams.update({
                'font.family': 'serif',
                'font.size': 10,
                'axes.labelsize': 11,
                'axes.titlesize': 12,
                'legend.fontsize': 9,
                'figure.dpi': 150
            })
            self.colors = {
                'primary': '#1f77b4',
                'secondary': '#ff7f0e',
                'accent': '#2ca02c',
                'text': '#000000',
                'grid': '#cccccc'
            }
        else:
            self.colors = {
                'primary': '#2196F3',
                'secondary': '#F44336',
                'accent': '#4CAF50',
                'text': '#212121',
                'grid': '#E0E0E0'
            }
    
    def plot_time_history(self,
                          results: Dict,
                          quantities: List[str] = None,
                          title: str = "MSD Analysis Results") -> plt.Figure:
        """
        Plot time history of selected quantities.
        
        Args:
            results: Dictionary with 'time' and quantity arrays
            quantities: List of quantities to plot (default: all)
            title: Plot title
        
        Returns:
            Matplotlib figure
        """
        time = results['time']
        
        if quantities is None:
            quantities = [k for k in results.keys() if k != 'time' and 
                         isinstance(results[k], np.ndarray) and
                         len(results[k]) == len(time)]
        
        n_plots = len(quantities)
        fig, axes = plt.subplots(n_plots, 1, figsize=(self.figsize[0], 3*n_plots),
                                  sharex=True)
        
        if n_plots == 1:
            axes = [axes]
        
        for ax, qty in zip(axes, quantities):
            data = results[qty]
            
            if data.ndim == 1:
                ax.plot(time, data, color=self.colors['primary'], linewidth=1)
            else:
                # Multiple DOFs - plot all
                for i in range(min(data.shape[1], 5)):  # Limit to 5 traces
                    ax.plot(time, data[:, i], label=f'DOF {i+1}', linewidth=0.8)
                ax.legend(loc='upper right', fontsize=8)
            
            ax.set_ylabel(qty.replace('_', ' ').title())
            ax.grid(True, alpha=0.3)
            ax.set_xlim([time[0], time[-1]])
        
        axes[-1].set_xlabel('Time [s]')
        fig.suptitle(title, fontsize=14)
        plt.tight_layout()
        
        return fig
    
    def plot_preload_decay(self,
                           preload_history: np.ndarray,
                           cycles: np.ndarray = None,
                           F_initial: float = None,
                           show_phases: bool = True) -> plt.Figure:
        """
        Plot preload decay curve with phase annotations.
        
        Args:
            preload_history: Array of preload values
            cycles: Cycle count array (or will use index)
            F_initial: Initial preload for normalization
            show_phases: Show Jiang two-stage phases
        
        Returns:
            Matplotlib figure
        """
        fig, ax = plt.subplots(figsize=self.figsize)
        
        if cycles is None:
            cycles = np.arange(len(preload_history))
        
        # Normalize if initial provided
        if F_initial is not None:
            y_data = preload_history / F_initial * 100
            ylabel = 'Remaining Preload [%]'
        else:
            y_data = preload_history / 1000  # Convert to kN
            ylabel = 'Preload [kN]'
        
        ax.plot(cycles, y_data, color=self.colors['primary'], 
                linewidth=2, label='Preload')
        
        # Add phase annotations
        if show_phases and len(cycles) > 100:
            # Estimate transition point (simplified)
            trans_idx = min(100, len(cycles)//5)
            
            ax.axvline(x=cycles[trans_idx], color=self.colors['accent'], 
                      linestyle='--', linewidth=1, alpha=0.7)
            ax.annotate('Stage 1→2\nTransition', 
                       xy=(cycles[trans_idx], y_data[trans_idx]),
                       xytext=(cycles[trans_idx]*1.1, y_data[trans_idx]*1.05),
                       fontsize=9, alpha=0.8,
                       arrowprops=dict(arrowstyle='->', color='gray'))
            
            # Phase labels
            ax.text(cycles[trans_idx//2], max(y_data)*0.95, 
                   'Stage 1:\nEmbedding',
                   ha='center', fontsize=9, style='italic')
            ax.text(cycles[min(trans_idx*3, len(cycles)-1)], max(y_data)*0.95,
                   'Stage 2:\nRotational',
                   ha='center', fontsize=9, style='italic')
        
        ax.set_xlabel('Cycles N')
        ax.set_ylabel(ylabel)
        ax.set_title('Preload Decay Curve (Jiang Two-Stage Model)')
        ax.grid(True, alpha=0.3)
        ax.set_xlim([0, cycles[-1]])
        
        if F_initial is not None:
            ax.set_ylim([0, 105])
            # Add safety threshold
            ax.axhline(y=70, color=self.colors['secondary'], 
                      linestyle=':', linewidth=1.5, label='70% threshold')
            ax.legend()
        
        plt.tight_layout()
        return fig
    
    def plot_thread_load_distribution(self,
                                       thread_loads: List[Dict],
                                       title: str = "Thread Load Distribution") -> plt.Figure:
        """
        Plot load distribution across engaged threads.
        
        Args:
            thread_loads: List of thread load dictionaries
            title: Plot title
        
        Returns:
            Matplotlib figure
        """
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=self.figsize)
        
        # Extract data
        thread_nums = [t['index'] + 1 for t in thread_loads]
        load_pcts = [t['load_fraction_pct'] for t in thread_loads]
        slip_states = [t['slip_state'] for t in thread_loads]
        
        # Color by slip state
        colors = []
        for state in slip_states:
            if state == 'stick':
                colors.append(self.colors['accent'])
            elif state == 'partial_slip':
                colors.append(self.colors['primary'])
            else:  # gross_slip
                colors.append(self.colors['secondary'])
        
        # Bar chart
        bars = ax1.bar(thread_nums, load_pcts, color=colors, edgecolor='black')
        ax1.set_xlabel('Thread Number')
        ax1.set_ylabel('Load Fraction [%]')
        ax1.set_title('Load per Thread')
        ax1.set_xticks(thread_nums)
        
        # Add cumulative line
        cumulative = np.cumsum(load_pcts)
        ax1_twin = ax1.twinx()
        ax1_twin.plot(thread_nums, cumulative, 'ko-', markersize=4)
        ax1_twin.set_ylabel('Cumulative [%]', color='black')
        ax1_twin.set_ylim([0, 105])
        
        # Legend
        from matplotlib.patches import Patch
        legend_elements = [
            Patch(facecolor=self.colors['accent'], label='Stick'),
            Patch(facecolor=self.colors['primary'], label='Partial Slip'),
            Patch(facecolor=self.colors['secondary'], label='Gross Slip')
        ]
        ax1.legend(handles=legend_elements, loc='upper right')
        
        # Schematic
        self._draw_thread_schematic(ax2, thread_loads)
        ax2.set_title('Thread Slip State')
        
        fig.suptitle(title, fontsize=14)
        plt.tight_layout()
        return fig
    
    def _draw_thread_schematic(self, ax, thread_loads):
        """Draw schematic of thread engagement"""
        ax.set_xlim([0, 10])
        ax.set_ylim([0, len(thread_loads) + 1])
        ax.set_aspect('equal')
        ax.axis('off')
        
        for i, t in enumerate(thread_loads):
            y = len(thread_loads) - i
            width = t['load_fraction_pct'] / 10
            
            if t['slip_state'] == 'stick':
                color = self.colors['accent']
            elif t['slip_state'] == 'partial_slip':
                color = self.colors['primary']
            else:
                color = self.colors['secondary']
            
            # Draw thread bar
            rect = plt.Rectangle((1, y-0.3), width, 0.6,
                                 facecolor=color, edgecolor='black')
            ax.add_patch(rect)
            
            # Thread number
            ax.text(0.5, y, f'T{i+1}', ha='center', va='center', fontsize=9)
            
            # Load percentage
            ax.text(1 + width + 0.2, y, f'{t["load_fraction_pct"]:.1f}%',
                   ha='left', va='center', fontsize=8)
    
    def plot_wear_evolution(self,
                            wear_history: Dict,
                            cycles: np.ndarray = None) -> plt.Figure:
        """
        Plot wear evolution at different contacts.
        
        Args:
            wear_history: Dictionary with wear depths per contact
            cycles: Cycle array
        
        Returns:
            Matplotlib figure
        """
        fig, ax = plt.subplots(figsize=self.figsize)
        
        if cycles is None:
            max_len = max(len(v) for v in wear_history.values())
            cycles = np.arange(max_len)
        
        for contact_name, wear_data in wear_history.items():
            wear_um = np.array(wear_data) * 1e6  # Convert to μm
            ax.plot(cycles[:len(wear_um)], wear_um, 
                   linewidth=1.5, label=contact_name)
        
        ax.set_xlabel('Cycles N')
        ax.set_ylabel('Wear Depth [μm]')
        ax.set_title('Wear Evolution at Contact Interfaces')
        ax.legend()
        ax.grid(True, alpha=0.3)
        ax.set_xlim([0, cycles[-1]])
        
        plt.tight_layout()
        return fig
    
    def plot_friction_evolution(self,
                                 mu_history: np.ndarray,
                                 cycles: np.ndarray = None,
                                 phases: bool = True) -> plt.Figure:
        """
        Plot friction coefficient evolution (three-phase model).
        
        Args:
            mu_history: Array of friction coefficient values
            cycles: Cycle array
            phases: Show phase annotations
        
        Returns:
            Matplotlib figure
        """
        fig, ax = plt.subplots(figsize=self.figsize)
        
        if cycles is None:
            cycles = np.arange(len(mu_history))
        
        ax.plot(cycles, mu_history, color=self.colors['primary'], 
                linewidth=2, label='μ(N)')
        
        if phases and len(cycles) > 100:
            # Identify phases from data
            mu_max_idx = np.argmax(mu_history)
            
            # Phase 1: Running-in (rising)
            ax.axvspan(0, mu_max_idx, alpha=0.1, color='green', 
                      label='Phase 1: Running-in')
            
            # Find steady-state region (simplified)
            steady_start = mu_max_idx + len(cycles)//10
            if steady_start < len(cycles):
                ax.axvspan(mu_max_idx, steady_start, alpha=0.1, color='blue',
                          label='Phase 2: Steady')
                ax.axvspan(steady_start, cycles[-1], alpha=0.1, color='orange',
                          label='Phase 3: Degradation')
        
        ax.set_xlabel('Cycles N')
        ax.set_ylabel('Friction Coefficient μ')
        ax.set_title('Friction Coefficient Evolution (Hintikka Model)')
        ax.legend(loc='upper right')
        ax.grid(True, alpha=0.3)
        ax.set_xlim([0, cycles[-1]])
        
        plt.tight_layout()
        return fig
    
    def plot_matrix_structure(self,
                               K: np.ndarray,
                               title: str = "Stiffness Matrix [K]",
                               annotate: bool = True) -> plt.Figure:
        """
        Visualize matrix structure with coupling identification.
        
        Args:
            K: Matrix to visualize
            title: Plot title
            annotate: Add coupling annotations
        
        Returns:
            Matplotlib figure
        """
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        
        n = K.shape[0]
        
        # Sparsity pattern
        ax1.spy(K, markersize=15 if n < 15 else 8)
        ax1.set_title('Sparsity Pattern')
        
        # DOF labels
        dof_labels = ['x₁', 'x₂', 'x₃', 'x₄', 'x₅', 'x₆', 'x₇', 'x₈',
                      'θₛ', 'θₙ', 'y₁', 'z₁', 'y₂', 'z₂'][:n]
        ax1.set_xticks(range(n))
        ax1.set_yticks(range(n))
        ax1.set_xticklabels(dof_labels, fontsize=8)
        ax1.set_yticklabels(dof_labels, fontsize=8)
        
        # Log magnitude heatmap
        K_log = np.log10(np.abs(K) + 1)
        im = ax2.imshow(K_log, cmap='hot', interpolation='nearest')
        ax2.set_title('Magnitude (log₁₀ scale)')
        ax2.set_xticks(range(n))
        ax2.set_yticks(range(n))
        ax2.set_xticklabels(dof_labels, fontsize=8)
        ax2.set_yticklabels(dof_labels, fontsize=8)
        plt.colorbar(im, ax=ax2, label='log₁₀(|K|+1)')
        
        # Annotate helix coupling if present
        if annotate and n >= 10:
            # Helix coupling region (DOFs 7, 9, 10 typically)
            for ax in [ax1, ax2]:
                rect = plt.Rectangle((6.5, 6.5), 3, 3, 
                                     fill=False, edgecolor='cyan',
                                     linewidth=2, linestyle='--')
                ax.add_patch(rect)
            ax2.text(8, 11.5, 'HELIX\nCOUPLING', ha='center', 
                    color='cyan', fontsize=9, weight='bold')
        
        fig.suptitle(title, fontsize=14)
        plt.tight_layout()
        return fig
    
    def create_dashboard(self,
                         results: Dict,
                         joint_name: str = "Bolted Joint") -> plt.Figure:
        """
        Create comprehensive dashboard with all key results.
        
        Args:
            results: Complete analysis results dictionary
            joint_name: Name for plot title
        
        Returns:
            Matplotlib figure
        """
        fig = plt.figure(figsize=(16, 12))
        gs = gridspec.GridSpec(3, 3, figure=fig, hspace=0.3, wspace=0.3)
        
        # 1. Preload decay (large)
        ax1 = fig.add_subplot(gs[0, :2])
        if 'preload_history' in results:
            cycles = np.arange(len(results['preload_history']))
            F0 = results.get('preload_initial', results['preload_history'][0])
            preload_pct = np.array(results['preload_history']) / F0 * 100
            ax1.plot(cycles, preload_pct, 'b-', linewidth=2)
            ax1.axhline(70, color='r', linestyle='--', label='70% threshold')
            ax1.set_xlabel('Cycles')
            ax1.set_ylabel('Preload [%]')
            ax1.set_title('Preload Decay')
            ax1.legend()
            ax1.grid(True, alpha=0.3)
        
        # 2. Loosening angle
        ax2 = fig.add_subplot(gs[0, 2])
        if 'loosening_history' in results:
            loosening_deg = np.degrees(results['loosening_history'])
            ax2.plot(loosening_deg, 'g-', linewidth=2)
            ax2.set_xlabel('Cycles')
            ax2.set_ylabel('Angle [°]')
            ax2.set_title('Loosening Angle')
            ax2.grid(True, alpha=0.3)
        
        # 3. Thread loads
        ax3 = fig.add_subplot(gs[1, 0])
        if 'thread_loads' in results:
            loads = [t['load_fraction_pct'] for t in results['thread_loads']]
            threads = range(1, len(loads)+1)
            ax3.bar(threads, loads, color='steelblue')
            ax3.set_xlabel('Thread #')
            ax3.set_ylabel('Load [%]')
            ax3.set_title('Thread Load Distribution')
        
        # 4. Friction evolution
        ax4 = fig.add_subplot(gs[1, 1])
        if 'mu_history' in results:
            ax4.plot(results['mu_history'], 'orange', linewidth=2)
            ax4.set_xlabel('Cycles')
            ax4.set_ylabel('μ')
            ax4.set_title('Friction Evolution')
            ax4.grid(True, alpha=0.3)
        
        # 5. Wear
        ax5 = fig.add_subplot(gs[1, 2])
        if 'wear_history' in results:
            for name, wear in results['wear_history'].items():
                ax5.plot(np.array(wear)*1e6, label=name[:10])
            ax5.set_xlabel('Cycles')
            ax5.set_ylabel('Wear [μm]')
            ax5.set_title('Wear Evolution')
            ax5.legend(fontsize=7)
            ax5.grid(True, alpha=0.3)
        
        # 6. Torque balance
        ax6 = fig.add_subplot(gs[2, 0])
        if 'T_pitch' in results and 'T_resistance' in results:
            labels = ['T_pitch\n(loosening)', 'T_thread\n(resist)', 'T_bearing\n(resist)']
            values = [results['T_pitch'], results.get('T_thread', 0), 
                     results.get('T_bearing', 0)]
            colors = ['red', 'green', 'green']
            ax6.bar(labels, values, color=colors)
            ax6.set_ylabel('Torque [Nm]')
            ax6.set_title('Torque Balance')
        
        # 7. Loss breakdown
        ax7 = fig.add_subplot(gs[2, 1])
        if 'loss_rotational' in results:
            losses = {
                'Rotational': results.get('loss_rotational', 0),
                'Embedding': results.get('loss_embedding', 0),
                'Wear': results.get('loss_wear', 0),
                'Other': results.get('loss_other', 0)
            }
            losses = {k: v for k, v in losses.items() if v > 0}
            if losses:
                ax7.pie(list(losses.values()), labels=list(losses.keys()),
                       autopct='%1.1f%%')
                ax7.set_title('Preload Loss Breakdown')
        
        # 8. Summary text
        ax8 = fig.add_subplot(gs[2, 2])
        ax8.axis('off')
        summary_text = f"""
        ANALYSIS SUMMARY
        ═══════════════════
        
        Initial Preload: {results.get('preload_initial', 0)/1000:.1f} kN
        Final Preload: {results.get('preload_final', 0)/1000:.1f} kN
        Preload Loss: {results.get('total_loss_pct', 0):.1f}%
        
        Total Loosening: {results.get('total_loosening_deg', 0):.2f}°
        Total Cycles: {results.get('total_cycles', 0)}
        
        Status: {results.get('status', 'N/A')}
        """
        ax8.text(0.1, 0.9, summary_text, transform=ax8.transAxes,
                fontsize=10, verticalalignment='top', fontfamily='monospace',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
        fig.suptitle(f'{joint_name} - Complete Analysis Dashboard', 
                    fontsize=16, weight='bold')
        
        return fig
```

### 53.2 Animation System

```python
class MSDAnimationSystem:
    """
    Animation system for MSD results visualization.
    
    Creates:
    - Joint motion animation
    - Preload decay animation
    - Real-time loosening visualization
    """
    
    def __init__(self, fps: int = 30):
        """
        Initialize animation system.
        
        Args:
            fps: Frames per second
        """
        self.fps = fps
        self.interval = 1000 // fps  # milliseconds
        
    def animate_loosening(self,
                          results: Dict,
                          n_frames: int = 200,
                          save_path: str = None) -> FuncAnimation:
        """
        Create animation of loosening process.
        
        Args:
            results: Analysis results
            n_frames: Number of animation frames
            save_path: If provided, save animation to file
        
        Returns:
            FuncAnimation object
        """
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        
        preload = np.array(results['preload_history'])
        loosening = np.degrees(results['loosening_history'])
        cycles = np.arange(len(preload))
        
        # Sample frames
        frame_indices = np.linspace(0, len(preload)-1, n_frames, dtype=int)
        
        # Initialize plots
        line1, = ax1.plot([], [], 'b-', linewidth=2)
        point1, = ax1.plot([], [], 'ro', markersize=10)
        ax1.set_xlim([0, cycles[-1]])
        ax1.set_ylim([0, max(preload)*1.1/1000])
        ax1.set_xlabel('Cycles')
        ax1.set_ylabel('Preload [kN]')
        ax1.set_title('Preload Evolution')
        ax1.grid(True, alpha=0.3)
        
        # Nut rotation visualization
        circle = plt.Circle((0.5, 0.5), 0.3, fill=False, linewidth=3)
        ax2.add_patch(circle)
        indicator, = ax2.plot([0.5, 0.5], [0.5, 0.8], 'r-', linewidth=3)
        ax2.set_xlim([0, 1])
        ax2.set_ylim([0, 1])
        ax2.set_aspect('equal')
        ax2.axis('off')
        ax2.set_title('Nut Rotation')
        
        text = ax2.text(0.5, 0.1, '', ha='center', fontsize=12)
        
        def init():
            line1.set_data([], [])
            point1.set_data([], [])
            indicator.set_data([0.5, 0.5], [0.5, 0.8])
            text.set_text('')
            return line1, point1, indicator, text
        
        def animate(frame):
            idx = frame_indices[frame]
            
            # Update preload plot
            line1.set_data(cycles[:idx+1], preload[:idx+1]/1000)
            point1.set_data([cycles[idx]], [preload[idx]/1000])
            
            # Update nut rotation
            angle_rad = np.radians(loosening[idx])
            x_end = 0.5 + 0.3 * np.sin(angle_rad)
            y_end = 0.5 + 0.3 * np.cos(angle_rad)
            indicator.set_data([0.5, x_end], [0.5, y_end])
            
            text.set_text(f'Cycle: {cycles[idx]}\nLoosening: {loosening[idx]:.2f}°')
            
            return line1, point1, indicator, text
        
        anim = FuncAnimation(fig, animate, init_func=init,
                            frames=n_frames, interval=self.interval, blit=True)
        
        if save_path:
            anim.save(save_path, writer='pillow', fps=self.fps)
        
        return anim
```

This completes Part 2 with the matrix coupling and visualization sections.
