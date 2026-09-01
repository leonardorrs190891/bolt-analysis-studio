# MSD Framework -- PART III: MATRIX ASSEMBLY AND COUPLING

**Complete Technical Reference for Bolt Analysis Studio**

**Authors:** L. Ribeiro, D. Carvalho, S.C. Naves, T. Santos, V. Marques, G. Arruda
**Institution:** LTAD/UFU -- Tribology and Wear Technology Laboratory, Federal University of Uberlandia
**Project:** Petrobras R&D -- Bolted Flange Joint Integrity

---

**Abstract.** This Part describes how the individual element properties (mass, stiffness, damping) described in Parts I and II are assembled into the global system matrices $[M]$, $[K]$, and $[C]$, and the force vector $\{F\}$. The assembly process follows the classical **direct stiffness method** (Chopra, 2012; Bathe, 1996), where each element contributes to the global matrices at the DOF locations specified by its connectivity. The key feature of bolted joint models -- distinguishing them from generic structural dynamics -- is the **helix coupling** between axial and torsional DOFs through the thread pitch, which creates off-diagonal terms in $[K]$ that are essential for modeling self-loosening (Nassar and Housari, 2006). Additionally, the tribological forces (friction, wear) contribute exclusively to the force vector $\{F\}$ and not to the stiffness or damping matrices -- a fundamental modeling principle emphasized throughout this document.

---

## 10. Global Mass Matrix Assembly [M]

### 10.1 Lumped Mass Formulation

For MSD systems, the mass matrix is diagonal (lumped mass). This is the standard approach for discrete multi-DOF systems where each node carries a concentrated mass or rotational inertia (Chopra, 2012):

$$[M] = \text{diag}(m_1, m_2, ..., m_n, J_1, J_2, ...)$$

**Component Mass Calculations:**

| Component | Mass Formula | Typical Value (M20) |
|-----------|-------------|---------------------|
| Bolt head | m = ρ × π/4 × D² × h | 0.050 kg |
| Stud | m = ρ × π/4 × d² × L | 0.150 kg |
| Nut | m = ρ × (AF² - d²) × h × 0.866 | 0.035 kg |
| Washer | m = ρ × π/4 × (D_o² - D_i²) × t | 0.015 kg |
| Flange (portion) | m = ρ × π/4 × (D_c² - d_h²) × t_f / n_bolts | 5.0 kg |

**Rotational Inertia:**

For solid cylinder: $J = \frac{1}{2}mr^2$

For hollow cylinder: $J = \frac{1}{2}m(r_o^2 + r_i^2)$

### 10.2 Mass Matrix Assembly Implementation

```python
def assemble_mass_matrix(components: List[Dict], n_dof: int) -> np.ndarray:
    """
    Assemble global mass matrix from component definitions.
    
    Args:
        components: List of component dictionaries with:
            - 'dof': DOF index
            - 'mass': Mass [kg] for translational DOF
            - 'inertia': Rotational inertia [kg·m²] for rotational DOF
        n_dof: Total number of DOFs
    
    Returns:
        Diagonal mass matrix [M] of shape (n_dof, n_dof)
    """
    M = np.zeros((n_dof, n_dof))
    
    for comp in components:
        dof = comp['dof']
        if 'mass' in comp and comp['mass'] > 0:
            M[dof, dof] = comp['mass']
        elif 'inertia' in comp and comp['inertia'] > 0:
            M[dof, dof] = comp['inertia']
    
    return M


# Example for 10-DOF system
def create_example_mass_matrix() -> np.ndarray:
    """Create example mass matrix for M20 bolted joint"""
    
    components = [
        {'dof': 0, 'mass': 0.050},      # Bolt head
        {'dof': 1, 'mass': 0.015},      # Washer 1
        {'dof': 2, 'mass': 5.000},      # Flange 1 (portion)
        {'dof': 3, 'mass': 0.100},      # Gasket
        {'dof': 4, 'mass': 5.000},      # Flange 2 (portion)
        {'dof': 5, 'mass': 0.015},      # Washer 2
        {'dof': 6, 'mass': 0.035},      # Nut
        {'dof': 7, 'inertia': 1.5e-6},  # Stud rotation
        {'dof': 8, 'inertia': 2.0e-6},  # Nut rotation
        {'dof': 9, 'mass': 0.500},      # Transverse mass
    ]
    
    return assemble_mass_matrix(components, 10)
```

---

## 11. Global Stiffness Matrix Assembly [K]

### 11.1 Assembly Principle

The global stiffness matrix is assembled from element contributions using the connectivity (incidence) matrix:

$$[K_{global}] = \sum_e [L_e]^T [K_e] [L_e]$$

Where:
- [K_e] = Local element stiffness matrix
- [L_e] = Connectivity matrix for element e

### 11.2 Component Stiffness Formulas

**Bolt Axial Stiffness:**

$$k_b = \frac{EA}{L}$$

For stepped bolt (series of sections):

$$\frac{1}{k_b} = \sum_i \frac{L_i}{E_i \cdot A_i}$$

**Bolt Torsional Stiffness:**

$$k_\theta = \frac{GJ_p}{L}$$

Where $J_p = \frac{\pi d^4}{32}$

**Clamped Member Stiffness (Rötscher Cone):**

$$k_m = \frac{\pi E_m \cdot d \cdot \tan\alpha}{\ln\left[\frac{(L\tan\alpha + D - d)(D + d)}{(L\tan\alpha + D + d)(D - d)}\right]}$$

Where:
- α ≈ 30° (cone half-angle)
- D = washer outer diameter
- d = hole diameter
- L = grip length

**Clamped Member Stiffness (Wileman et al., 1991):**

An alternative to the Rötscher cone model is the empirical formula by Wileman et al. (1991), which avoids the ambiguity of cone angle selection:

$$k_m = E \cdot d \cdot A_w \cdot \exp\left(B_w \cdot \frac{d}{L_{clamp}}\right)$$

where $A_w = 0.78715$ and $B_w = 0.62873$ for steel-on-steel joints. This formula was developed by fitting finite element results for a wide range of bolt sizes and grip lengths (Wileman, J., Choudhury, M., & Green, I. (1991). "Computation of member stiffness in bolted connections." *ASME Journal of Mechanical Design*, 113(4), 432--437. DOI: 10.1115/1.2912801).

**Contact Stiffness:**

$$k_c = \frac{E_{eff} \cdot A_c}{t_{eff}}$$

Where the effective modulus accounts for dissimilar materials at the interface (Hertzian contact theory; Johnson, 1985):

$$\frac{1}{E_{eff}} = \frac{1 - \nu_1^2}{E_1} + \frac{1 - \nu_2^2}{E_2}$$

**Thread Stiffness (Total):**

The total thread stiffness is the sum of per-thread contributions weighted by the load distribution law (see Part II, Section 6 for the five distribution models: Equal, Linear, Power, Exponential, Yamamoto):

$$k_{thread} = \sum_i \phi_i \cdot k_{base}$$

where $\phi_i$ is the load fraction carried by the $i$-th engaged thread.

### 11.3 Stiffness Matrix Assembly Implementation

```python
def assemble_stiffness_matrix(contacts: List[BaseContactElement],
                               n_dof: int) -> np.ndarray:
    """
    Assemble global stiffness matrix from contact elements.
    
    Uses scatter operation: K_global[i,j] += K_local[i_loc, j_loc]
    
    Args:
        contacts: List of contact element objects
        n_dof: Total number of DOFs
    
    Returns:
        Global stiffness matrix [K]
    """
    K = np.zeros((n_dof, n_dof))
    
    for contact in contacts:
        K_local = contact.get_stiffness_matrix()
        dof_map = contact.dof_indices
        
        # Scatter to global
        for i_loc, i_glob in enumerate(dof_map):
            for j_loc, j_glob in enumerate(dof_map):
                if i_glob >= 0 and j_glob >= 0:
                    K[i_glob, j_glob] += K_local[i_loc, j_loc]
    
    return K


def visualize_stiffness_matrix(K: np.ndarray, 
                                title: str = "Stiffness Matrix"):
    """Visualize stiffness matrix structure"""
    import matplotlib.pyplot as plt
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    
    # Sparsity pattern
    ax1.spy(K, markersize=10)
    ax1.set_title(f'{title} - Sparsity Pattern')
    
    # Log magnitude
    K_log = np.log10(np.abs(K) + 1)
    im = ax2.imshow(K_log, cmap='hot')
    ax2.set_title(f'{title} - Magnitude (log scale)')
    plt.colorbar(im, ax=ax2)
    
    plt.tight_layout()
    return fig
```

### 11.4 Example Assembled Stiffness Matrix (6-DOF)

```
[K] = 10⁸ × 

       x₁      x₂      x₃      x₄      x₅      x₆
    ┌──────────────────────────────────────────────┐
x₁  │  20.0   -20.0    0       0       0       0  │
x₂  │ -20.0    30.0  -10.0     0       0       0  │
x₃  │   0     -10.0   15.0   -5.0      0       0  │
x₄  │   0       0     -5.0   10.0    -5.0      0  │
x₅  │   0       0       0     -5.0   30.0   -20.0 │
x₆  │   0       0       0       0    -20.0   20.0 │
    └──────────────────────────────────────────────┘

Note: Tridiagonal structure from sequential contact elements
```

---

## 12. Global Damping Matrix Assembly [C]

### 12.1 Rayleigh Damping

$$[C] = \alpha_M [M] + \beta_K [K]$$

**Modal Damping Ratio:**

$$\zeta_i = \frac{\alpha_M}{2\omega_i} + \frac{\beta_K \omega_i}{2}$$

**Determining α_M and β_K from Two Target Modes:**

Given target damping ratios ζ₁, ζ₂ at frequencies ω₁, ω₂:

$$\begin{bmatrix} 1/(2\omega_1) & \omega_1/2 \\ 1/(2\omega_2) & \omega_2/2 \end{bmatrix} \begin{bmatrix} \alpha_M \\ \beta_K \end{bmatrix} = \begin{bmatrix} \zeta_1 \\ \zeta_2 \end{bmatrix}$$

### 12.2 Damping Matrix Assembly Implementation

```python
def compute_rayleigh_coefficients(omega1: float, zeta1: float,
                                   omega2: float, zeta2: float) -> Tuple[float, float]:
    """
    Compute Rayleigh damping coefficients from two target modes.
    
    Args:
        omega1, omega2: Natural frequencies [rad/s]
        zeta1, zeta2: Target damping ratios
    
    Returns:
        (alpha_M, beta_K)
    """
    A = np.array([
        [1/(2*omega1), omega1/2],
        [1/(2*omega2), omega2/2]
    ])
    b = np.array([zeta1, zeta2])
    
    coeffs = np.linalg.solve(A, b)
    
    return coeffs[0], coeffs[1]


def assemble_damping_matrix(M: np.ndarray, 
                             K: np.ndarray,
                             contacts: List[BaseContactElement],
                             alpha_M: float = 1.0,
                             beta_K: float = 1e-5) -> np.ndarray:
    """
    Assemble global damping matrix.
    
    [C] = α_M[M] + β_K[K] + [C_contact]
    
    Args:
        M: Mass matrix
        K: Stiffness matrix
        contacts: List of contact elements
        alpha_M: Mass-proportional coefficient
        beta_K: Stiffness-proportional coefficient
    
    Returns:
        Global damping matrix [C]
    """
    n_dof = M.shape[0]
    
    # Rayleigh damping
    C = alpha_M * M + beta_K * K
    
    # Add contact damping contributions
    for contact in contacts:
        C_local = contact.get_damping_matrix()
        dof_map = contact.dof_indices
        
        for i_loc, i_glob in enumerate(dof_map):
            for j_loc, j_glob in enumerate(dof_map):
                if i_glob >= 0 and j_glob >= 0:
                    C[i_glob, j_glob] += C_local[i_loc, j_loc]
    
    return C
```

---

## 13. Coupling Terms and Off-Diagonal Elements

### 13.1 Types of Coupling in Bolted Joints

Three distinct types of coupling arise in the bolted joint MSD model. Understanding which terms enter the stiffness matrix $[K]$ versus the force vector $\{F\}$ is critical for correct implementation and physical interpretation.

**1. Geometric Coupling (Thread Helix) -- enters [K]:**

The thread helix creates a kinematic constraint between axial displacement and rotation: a nut that rotates by angle $\Delta\theta$ on a thread of pitch $p$ must also translate axially by:

$$\Delta x = \frac{p}{2\pi} \Delta\theta$$

This coupling is *geometric*, not frictional -- it arises from the helical shape of the thread and is always present regardless of friction. It creates off-diagonal terms in $[K]$:

$$K_{x,\theta} = k_{thread} \cdot \frac{p}{2\pi} = k_{thread} \cdot \lambda$$

where $\lambda = p/(2\pi)$ is the helix coupling factor [m/rad]. **This coupling is the mechanism by which rotation causes preload loss** -- it is the mathematical expression of Junker's (1969) insight that nut back-rotation converts to axial displacement through the thread geometry.

**2. Sequential Element Coupling -- enters [K]:**

Adjacent elements share DOFs, creating the characteristic tridiagonal structure of a series-connected MSD chain:

$$K_{i,i+1} = -k_{contact}$$

This is identical to the standard finite element assembly for 1D bar elements (Bathe, 1996) and reflects Newton's third law: the force element $e$ exerts on node $i$ is equal and opposite to the force it exerts on node $i+1$.

**3. Tribological Coupling -- enters {F} only:**

Friction forces depend on displacement, velocity, and state variables, creating a nonlinear coupling that enters the force vector, **not** the stiffness or damping matrices:

$$F_{friction} = f(\mu, F_n, \dot{x}, z)$$

where $z$ may be a bristle state (LuGre model) or slip history. **This is a critical modeling principle**: friction is a force, not a stiffness or damping. While linearized friction models (e.g., equivalent viscous damping $c_{eq} = 4\mu F_n / (\pi \omega X)$) are sometimes used for computational convenience, the BAS framework maintains the correct nonlinear treatment for accuracy in loosening prediction.

### 13.2 Helix Coupling Matrix Derivation

**From strain energy:**

$$U = \frac{1}{2} k_{thread} \left( \Delta x - \frac{p}{2\pi}\Delta\theta \right)^2$$

**Stiffness matrix (3×3) for DOFs {x_nut, θ_stud, θ_nut}:**

$$[K_{helix}] = k_{thread} \begin{bmatrix}
1 & -\lambda & \lambda \\
-\lambda & \lambda^2 & -\lambda^2 \\
\lambda & -\lambda^2 & \lambda^2
\end{bmatrix}$$

Where $\lambda = \frac{p}{2\pi}$

### 13.3 Coupling Matrix Visualization

```
STIFFNESS MATRIX COUPLING STRUCTURE (10-DOF System):

       x₁   x₂   x₃   x₄   x₅   x₆   x₇   θ_s  θ_n  y_tr
    ┌─────────────────────────────────────────────────────┐
x₁  │ ●●●  ●●●                                           │ Bearing head
x₂  │ ●●●  ●●●  ●●●                                      │ Washer-flange
x₃  │      ●●●  ●●●  ●●●                                 │ Flange-gasket
x₄  │           ●●●  ●●●  ●●●                            │ Gasket
x₅  │                ●●●  ●●●  ●●●                       │ Flange-gasket
x₆  │                     ●●●  ●●●  ●●●                  │ Washer-flange
x₇  │                          ●●●  ●●●  ○○○  ○○○       │ Thread (axial)
θ_s │                               ○○○  ○○○  ○○○       │ Stud torsion
θ_n │                               ○○○  ○○○  ○○○       │ Nut torsion
y_tr│                                              ●●●   │ Transverse
    └─────────────────────────────────────────────────────┘

Legend: ●●● = Direct coupling (same physics)
        ○○○ = Helix coupling (axial-torsional)
```

---

## 14. Force Vector Assembly {F}

### 14.1 Force Vector Components

$$\{F_{global}\} = \{F_{ext}\} + \{F_{preload}\} + \{F_{tribo}\} + \{F_{thermal}\}$$

### 14.2 Preload Force Vector

**Critical: Preload is self-equilibrating (sum = 0)**

```python
def assemble_preload_vector(F_preload: float,
                             dof_map: Dict,
                             n_dof: int) -> np.ndarray:
    """
    Assemble preload force vector.
    
    Preload creates:
    - TENSION in bolt (negative at head/nut)
    - COMPRESSION in clamped members (positive at flanges)
    
    ∑F_preload = 0 (self-equilibrating)
    """
    F = np.zeros(n_dof)
    
    # Bolt in tension
    F[dof_map['bolt_head']] = -F_preload
    F[dof_map['nut']] = -F_preload
    
    # Flanges in compression
    F[dof_map['flange1']] = +F_preload
    F[dof_map['flange2']] = +F_preload
    
    # Verify self-equilibrium
    assert abs(np.sum(F)) < 1e-10, "Preload not self-equilibrating!"
    
    return F
```

### 14.3 External Force Application

**Axial Loading:**
```python
F[dof_map['flange1']] += F_axial
F[dof_map['flange2']] -= F_axial
```

**Transverse (Junker) Loading:**
```python
F[dof_map['y_trans']] = F_trans * np.sin(omega * t)
```

### 14.4 Tribological Force Assembly

```python
def assemble_tribological_forces(contacts: List[BaseContactElement],
                                   u: np.ndarray,
                                   v: np.ndarray,
                                   preload: float,
                                   n_dof: int) -> np.ndarray:
    """
    Assemble tribological force vector from all contacts.
    
    Includes:
    - Friction forces (velocity-dependent)
    - Friction torques (bearing, thread)
    """
    F_tribo = np.zeros(n_dof)
    
    for contact in contacts:
        dof_map = contact.dof_indices
        n_local = len(dof_map)
        
        u_local = u[dof_map] if n_local > 0 else np.array([])
        v_local = v[dof_map] if n_local > 0 else np.array([])
        
        F_local = contact.get_force_vector(u_local, v_local, preload)
        
        for i_loc, i_glob in enumerate(dof_map):
            if i_glob >= 0 and i_loc < len(F_local):
                F_tribo[i_glob] += F_local[i_loc]
    
    return F_tribo
```

---

## References -- Part III

1. Bathe, K.-J. (1996). *Finite Element Procedures*. Prentice Hall. -- Standard reference for the direct stiffness method, matrix assembly from element contributions, and the scatter/gather operations used in the assembly algorithm.

2. Bickford, J.H. (2008). *Introduction to the Design and Behavior of Bolted Joints*, 4th ed. CRC Press. -- Spring analogy for bolt ($k_b = A_t E / L_{eff}$) and member (frustum cone model) stiffness calculations. Sections 6.3--6.5 cover the bolt-as-spring concept central to the MSD stiffness matrix.

3. Canudas de Wit, C., Olsson, H., Astrom, K.J., & Lischinsky, P. (1995). "A new model for control of systems with friction." *IEEE Transactions on Automatic Control*, 40(3), 419--425. DOI: 10.1109/9.376053 -- The LuGre dynamic friction model contributes to the $\{F_{tribo}\}$ force vector, not to $[K]$ or $[C]$ matrices. This separation is a fundamental modeling principle in BAS.

4. Chopra, A.K. (2012). *Dynamics of Structures: Theory and Applications to Earthquake Engineering*, 4th ed. Prentice Hall. ISBN: 978-0-13-285803-8. -- Standard reference for lumped mass formulation, Rayleigh damping $[C] = \alpha[M] + \beta[K]$, and the direct stiffness assembly method.

5. Johnson, K.L. (1985). *Contact Mechanics*. Cambridge University Press. DOI: 10.1017/CBO9781139171731 -- Foundation for the effective contact modulus formula $1/E_{eff} = (1-\nu_1^2)/E_1 + (1-\nu_2^2)/E_2$ used in contact stiffness calculations.

6. Junker, G.H. (1969). "New criteria for self-loosening of fasteners under vibration." *SAE Technical Paper* 690055. DOI: 10.4271/690055 -- Established that rotation through the thread helix (now modeled as off-diagonal coupling in $[K]$) is the mechanism converting transverse vibration into preload loss.

7. Nassar, S.A. & Housari, B.A. (2006). "Effect of thread pitch and initial tension on the self-loosening of threaded fasteners." *ASME Journal of Pressure Vessel Technology*, 128(4), 590--598. DOI: 10.1115/1.2349572 -- Quantifies the helix coupling $K_{x,\theta} = k_{thread} \times p/(2\pi)$ and demonstrates its influence on loosening rate. Directly motivates the off-diagonal terms in the stiffness matrix.

8. VDI 2230 Part 1 (2015). "Systematic calculation of highly stressed bolted joints -- Joints with one cylindrical bolt." Verein Deutscher Ingenieure, Dusseldorf. -- System stiffness $k_{sys} = k_b k_m / (k_b + k_m)$, load introduction factor $n$, Rotscher cone model for member stiffness. The industrial-standard basis for all stiffness calculations.

9. Wileman, J., Choudhury, M., & Green, I. (1991). "Computation of member stiffness in bolted connections." *ASME Journal of Mechanical Design*, 113(4), 432--437. DOI: 10.1115/1.2912801 -- Empirical formula $k_m = E \cdot d \cdot A_w \cdot \exp(B_w \cdot d/L)$ fitted to finite element results. Provides an alternative to the Rotscher cone model that avoids cone angle ambiguity.

---

**END OF PART III**

*Part IV covers Loading Models*
*Part V covers Self-Loosening Models*
*Part VI covers Wear Models*
*Part VII covers Friction Models*
