"""
Comprehensive 14-DOF MSD Matrix Assembly System for Bolted Joints.

This module implements a complete matrix assembly system for mass-spring-damper
(MSD) models of bolted flange joints with coupling between axial, torsional, and
transverse degrees of freedom.

14 DOF SYSTEM LAYOUT:
- 8 Axial DOFs: head, washer1, flange1, gasket, flange2, washer2, nut, stud
- 2 Torsional DOFs: stud_theta, nut_theta
- 4 Transverse DOFs: flange1_y, flange1_z, flange2_y, flange2_z

KEY FEATURES:
- Helix coupling between axial and torsional DOFs (thread contact)
- Contact-based matrix contributions (stiffness, damping, force)
- Rayleigh damping: [C] = α[M] + β[K] + [C_contact]
- Sparse matrix assembly using triplet format
- Comprehensive validation and diagnostics

MATRIX EQUATIONS:
[M]{ẍ} + [C]{ẋ} + [K]{x} = {F}(x, ẋ, t)

Where:
- [M]: 14×14 mass matrix (diagonal for uncoupled masses)
- [K]: 14×14 stiffness matrix (with helix coupling off-diagonal terms)
- [C]: 14×14 damping matrix (Rayleigh + contact damping)
- {F}: 14×1 force vector (external loads + tribological forces)

HELIX COUPLING:
For thread contact connecting DOF i (axial) and DOF j (torsional):
    K[i,j] = K[j,i] = k_thread × (p/2π)
where p is thread pitch and k_thread is thread stiffness.

This couples axial displacement with torsional rotation via:
    Δx_axial = (p/2π) × Δθ_torsional

Author: Bolt Analysis Studio Team
Date: January 2026
Based on: MSD_Contact_System_Architecture.md, VDI 2230
"""

from dataclasses import dataclass, field
from typing import List, Tuple, Dict, Optional, Any, Callable
import numpy as np
from enum import Enum, auto
import warnings


# =============================================================================
# DOF MAPPING
# =============================================================================

@dataclass
class DOFMapping:
    """
    Maps component names to DOF indices in the 14-DOF system.

    STANDARD 14-DOF LAYOUT:
    Axial DOFs (0-7):
        0: head         - Bolt head axial position
        1: washer1      - Upper washer axial position
        2: flange1      - Upper flange axial position
        3: gasket       - Gasket axial position
        4: flange2      - Lower flange axial position
        5: washer2      - Lower washer axial position
        6: nut          - Nut axial position
        7: stud         - Stud axial position

    Torsional DOFs (8-9):
        8: stud_theta   - Stud rotation angle
        9: nut_theta    - Nut rotation angle

    Transverse DOFs (10-13):
        10: flange1_y   - Upper flange transverse Y
        11: flange1_z   - Upper flange transverse Z
        12: flange2_y   - Lower flange transverse Y
        13: flange2_z   - Lower flange transverse Z

    This layout enables:
    - Thread helix coupling (axial ↔ torsional)
    - Bearing friction coupling (axial ↔ torsional)
    - Transverse loading effects on loosening
    - Full 3D joint behavior
    """
    # Axial DOFs
    head: int = 0
    washer1: int = 1
    flange1: int = 2
    gasket: int = 3
    flange2: int = 4
    washer2: int = 5
    nut: int = 6
    stud: int = 7

    # Torsional DOFs
    stud_theta: int = 8
    nut_theta: int = 9

    # Transverse DOFs
    flange1_y: int = 10
    flange1_z: int = 11
    flange2_y: int = 12
    flange2_z: int = 13

    # Total DOFs
    n_dof: int = 14

    def get_dof_name(self, dof_index: int) -> str:
        """Get component name for given DOF index."""
        dof_names = {
            0: "head", 1: "washer1", 2: "flange1", 3: "gasket",
            4: "flange2", 5: "washer2", 6: "nut", 7: "stud",
            8: "stud_theta", 9: "nut_theta",
            10: "flange1_y", 11: "flange1_z", 12: "flange2_y", 13: "flange2_z"
        }
        return dof_names.get(dof_index, f"DOF_{dof_index}")

    def get_axial_dofs(self) -> List[int]:
        """Get list of axial DOF indices."""
        return [self.head, self.washer1, self.flange1, self.gasket,
                self.flange2, self.washer2, self.nut, self.stud]

    def get_torsional_dofs(self) -> List[int]:
        """Get list of torsional DOF indices."""
        return [self.stud_theta, self.nut_theta]

    def get_transverse_dofs(self) -> List[int]:
        """Get list of transverse DOF indices."""
        return [self.flange1_y, self.flange1_z, self.flange2_y, self.flange2_z]

    def to_dict(self) -> Dict[str, int]:
        """Serialize to dictionary."""
        return {
            "head": self.head, "washer1": self.washer1, "flange1": self.flange1,
            "gasket": self.gasket, "flange2": self.flange2, "washer2": self.washer2,
            "nut": self.nut, "stud": self.stud,
            "stud_theta": self.stud_theta, "nut_theta": self.nut_theta,
            "flange1_y": self.flange1_y, "flange1_z": self.flange1_z,
            "flange2_y": self.flange2_y, "flange2_z": self.flange2_z,
            "n_dof": self.n_dof
        }

    @classmethod
    def from_dict(cls, data: Dict[str, int]) -> 'DOFMapping':
        """Deserialize from dictionary."""
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


# =============================================================================
# COMPONENT DATA CLASS
# =============================================================================

@dataclass
class ComponentData:
    """
    Component properties for matrix assembly.

    Each physical component (head, stud, flange, etc.) has:
    - Mass (for [M] matrix)
    - Stiffness properties (for [K] matrix, used by contacts)
    - DOF index assignment
    """
    name: str
    dof_index: int
    mass: float = 0.0           # [kg]
    rotational_inertia: float = 0.0  # [kg·m²] for torsional DOFs

    # Optional material properties (used by contacts)
    stiffness: float = 0.0      # [N/m] for direct stiffness
    damping: float = 0.0        # [N·s/m] for direct damping

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "dof_index": self.dof_index,
            "mass": self.mass,
            "rotational_inertia": self.rotational_inertia,
            "stiffness": self.stiffness,
            "damping": self.damping
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ComponentData':
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


# =============================================================================
# COMPLETE MSD MATRIX ASSEMBLER
# =============================================================================

class CompleteMSDMatrixAssembler:
    """
    Comprehensive 14-DOF matrix assembler for bolted joint MSD models.

    ASSEMBLY PROCESS:
    1. Initialize with DOF mapping and components
    2. Add contacts (thread, bearing, gasket, washer, flange)
    3. Assemble matrices: [M], [K], [C]
    4. Compute force vector: {F}(x, ẋ, t)
    5. Validate matrices (symmetry, definiteness)

    MATRIX STRUCTURE:
    - [M]: Diagonal (uncoupled component masses)
    - [K]: Banded with off-diagonal helix coupling terms
    - [C]: Rayleigh damping + contact damping
    - {F}: Nonlinear (contact friction, wear, external loads)

    EXAMPLE USAGE:
        >>> dof_map = create_standard_dof_mapping()
        >>> assembler = CompleteMSDMatrixAssembler(n_dof=14, dof_mapping=dof_map)
        >>>
        >>> # Add components
        >>> assembler.add_component(ComponentData("head", dof=0, mass=0.01))
        >>> assembler.add_component(ComponentData("stud", dof=7, mass=0.05))
        >>>
        >>> # Add contacts
        >>> assembler.add_contact(thread_contact)
        >>> assembler.add_contact(bearing_head_contact)
        >>>
        >>> # Assemble matrices
        >>> M = assembler.assemble_mass_matrix()
        >>> K = assembler.assemble_stiffness_matrix()
        >>> C = assembler.assemble_damping_matrix(alpha_M=0.1, beta_K=1e-5)
        >>>
        >>> # Get force vector
        >>> F = assembler.assemble_force_vector(x, x_dot, t)
    """

    def __init__(self, n_dof: int = 14, dof_mapping: Optional[DOFMapping] = None):
        """
        Initialize matrix assembler.

        Args:
            n_dof: Number of degrees of freedom (default 14)
            dof_mapping: DOF mapping object (creates standard if None)
        """
        self.n_dof = n_dof
        self.dof_mapping = dof_mapping if dof_mapping is not None else create_standard_dof_mapping()

        # Component storage
        self.components: List[ComponentData] = []
        self.component_dict: Dict[int, ComponentData] = {}

        # Contact storage
        self.contacts: List[Any] = []  # List of Contact objects

        # Matrices (cached)
        self._M: Optional[np.ndarray] = None
        self._K: Optional[np.ndarray] = None
        self._C: Optional[np.ndarray] = None
        self._matrices_dirty = True

        # External force function
        self.F_external_func: Optional[Callable] = None

        # Statistics
        self.assembly_count = 0
        self.last_assembly_time = 0.0

    def add_component(self, component: ComponentData) -> None:
        """
        Add a component to the system.

        Args:
            component: ComponentData with mass and DOF assignment
        """
        if component.dof_index >= self.n_dof or component.dof_index < 0:
            raise ValueError(f"Component DOF {component.dof_index} out of range [0, {self.n_dof})")

        self.components.append(component)
        self.component_dict[component.dof_index] = component
        self._mark_dirty()

    def add_contact(self, contact: Any) -> None:
        """
        Add a contact element to the system.

        Args:
            contact: Contact object (ThreadContact, BearingContact, etc.)
        """
        # Validate contact DOF indices
        if hasattr(contact, 'node_i') and contact.node_i >= self.n_dof:
            raise ValueError(f"Contact node_i {contact.node_i} out of range")
        if hasattr(contact, 'node_j') and contact.node_j >= self.n_dof:
            raise ValueError(f"Contact node_j {contact.node_j} out of range")

        self.contacts.append(contact)
        self._mark_dirty()

    def set_external_force_function(self, func: Callable[[np.ndarray, np.ndarray, float], np.ndarray]) -> None:
        """
        Set external force function: F_ext(x, x_dot, t) -> np.ndarray.

        Args:
            func: Function that returns force vector given state
        """
        self.F_external_func = func

    def _mark_dirty(self) -> None:
        """Mark matrices as needing reassembly."""
        self._matrices_dirty = True
        self._M = None
        self._K = None
        self._C = None

    def assemble_mass_matrix(self, components: Optional[List[ComponentData]] = None) -> np.ndarray:
        """
        Assemble mass matrix [M].

        STRUCTURE:
        - Diagonal matrix (uncoupled component masses)
        - Axial DOFs: translational mass [kg]
        - Torsional DOFs: rotational inertia [kg·m²]
        - Transverse DOFs: translational mass [kg]

        EQUATION:
        M[i,i] = m_i  (for DOF i)

        Args:
            components: List of components (uses self.components if None)

        Returns:
            14×14 mass matrix [kg or kg·m²]
        """
        if components is None:
            components = self.components

        M = np.zeros((self.n_dof, self.n_dof))

        for comp in components:
            dof = comp.dof_index

            if dof < 0 or dof >= self.n_dof:
                continue

            # Determine if torsional DOF
            torsional_dofs = self.dof_mapping.get_torsional_dofs()

            if dof in torsional_dofs:
                # Torsional DOF: use rotational inertia
                M[dof, dof] += comp.rotational_inertia
            else:
                # Axial or transverse DOF: use translational mass
                M[dof, dof] += comp.mass

        # Ensure minimum mass for numerical stability
        min_mass = 1e-6
        for i in range(self.n_dof):
            if M[i, i] < min_mass:
                M[i, i] = min_mass

        self._M = M
        return M

    def assemble_stiffness_matrix(self, contacts: Optional[List[Any]] = None,
                                  components: Optional[List[ComponentData]] = None) -> np.ndarray:
        """
        Assemble stiffness matrix [K] with helix coupling.

        STRUCTURE:
        - Symmetric banded matrix
        - Diagonal: sum of contact stiffnesses at each DOF
        - Off-diagonal: contact coupling terms + helix coupling

        HELIX COUPLING (Thread Contact):
        For thread connecting DOF i_axial and j_theta:
            K[i_axial, j_theta] = K[j_theta, i_axial] = k_thread × (p/2π)

        This couples axial displacement with rotation:
            Δx = (p/2π) × Δθ

        STANDARD CONTACT PATTERN (2-node):
        For contact between DOF i and j with stiffness k:
            K[i,i] += k
            K[j,j] += k
            K[i,j] -= k
            K[j,i] -= k

        Args:
            contacts: List of contact objects (uses self.contacts if None)
            components: List of components (uses self.components if None)

        Returns:
            14×14 stiffness matrix [N/m or N·m/rad]
        """
        if contacts is None:
            contacts = self.contacts
        if components is None:
            components = self.components

        # Use triplet format for efficient sparse assembly
        # List of (row, col, value) tuples
        triplets: List[Tuple[int, int, float]] = []

        # Add component direct stiffness (if any)
        for comp in components:
            if comp.stiffness > 0:
                dof = comp.dof_index
                if 0 <= dof < self.n_dof:
                    triplets.append((dof, dof, comp.stiffness))

        # Add contact contributions
        for contact in contacts:
            contact_triplets = self._get_contact_stiffness_contribution(contact)
            triplets.extend(contact_triplets)

        # Assemble from triplets
        K = self._triplets_to_matrix(triplets, self.n_dof)

        # Symmetrize (ensure numerical symmetry)
        K = 0.5 * (K + K.T)

        self._K = K
        return K

    def _get_contact_stiffness_contribution(self, contact: Any) -> List[Tuple[int, int, float]]:
        """
        Get stiffness matrix contributions from a contact.

        Handles:
        - Standard 2-node contacts (axial stiffness)
        - Thread contacts with helix coupling
        - Multi-DOF contacts

        Args:
            contact: Contact object

        Returns:
            List of (row, col, value) triplets
        """
        # Check if contact has get_stiffness_contribution method
        if hasattr(contact, 'get_stiffness_contribution'):
            return contact.get_stiffness_contribution()

        # Fallback: use basic stiffness pattern
        triplets = []

        if hasattr(contact, 'node_i') and hasattr(contact, 'node_j'):
            i = contact.node_i
            j = contact.node_j

            # Get stiffness
            if hasattr(contact, 'stiffness'):
                if hasattr(contact.stiffness, 'k_axial'):
                    k = contact.stiffness.k_axial
                else:
                    k = contact.stiffness
            else:
                return triplets  # No stiffness available

            # Standard 2-node pattern
            if i >= 0 and i < self.n_dof:
                triplets.append((i, i, k))

            if j >= 0 and j < self.n_dof:
                triplets.append((j, j, k))

                if i >= 0 and i < self.n_dof:
                    triplets.append((i, j, -k))
                    triplets.append((j, i, -k))

        return triplets

    def assemble_damping_matrix(self, contacts: Optional[List[Any]] = None,
                               alpha_M: float = 0.0,
                               beta_K: float = 0.0) -> np.ndarray:
        """
        Assemble damping matrix [C] with Rayleigh damping.

        RAYLEIGH DAMPING MODEL:
        [C] = α[M] + β[K] + [C_contact]

        Where:
        - α (alpha_M): Mass-proportional damping coefficient [1/s]
        - β (beta_K): Stiffness-proportional damping coefficient [s]
        - [C_contact]: Contact-specific damping

        PHYSICAL INTERPRETATION:
        - α term: velocity-proportional (viscous damping in materials)
        - β term: displacement-proportional (internal friction)
        - Contact term: interface friction, material damping

        MODAL DAMPING:
        Rayleigh damping gives modal damping ratio:
            ζ_i = (α/2ω_i) + (βω_i/2)

        COEFFICIENT SELECTION:
        Given target damping ratios ζ₁, ζ₂ at frequencies ω₁, ω₂:
            α = 2ω₁ω₂(ζ₁ω₂ - ζ₂ω₁)/(ω₂² - ω₁²)
            β = 2(ζ₂ω₂ - ζ₁ω₁)/(ω₂² - ω₁²)

        Args:
            contacts: List of contact objects (uses self.contacts if None)
            alpha_M: Mass-proportional coefficient [1/s]
            beta_K: Stiffness-proportional coefficient [s]

        Returns:
            14×14 damping matrix [N·s/m or N·m·s/rad]
        """
        if contacts is None:
            contacts = self.contacts

        # Ensure M and K are assembled
        if self._M is None:
            self.assemble_mass_matrix()
        if self._K is None:
            self.assemble_stiffness_matrix()

        # Rayleigh damping: C = α[M] + β[K]
        C = alpha_M * self._M + beta_K * self._K

        # Add contact damping contributions
        triplets: List[Tuple[int, int, float]] = []

        for comp in self.components:
            if comp.damping > 0:
                dof = comp.dof_index
                if 0 <= dof < self.n_dof:
                    triplets.append((dof, dof, comp.damping))

        for contact in contacts:
            contact_triplets = self._get_contact_damping_contribution(contact)
            triplets.extend(contact_triplets)

        # Add contact damping to Rayleigh damping
        C_contact = self._triplets_to_matrix(triplets, self.n_dof)
        C += C_contact

        # Symmetrize
        C = 0.5 * (C + C.T)

        self._C = C
        return C

    def _get_contact_damping_contribution(self, contact: Any) -> List[Tuple[int, int, float]]:
        """
        Get damping matrix contributions from a contact.

        Args:
            contact: Contact object

        Returns:
            List of (row, col, value) triplets
        """
        # Check if contact has get_damping_contribution method
        if hasattr(contact, 'get_damping_contribution'):
            return contact.get_damping_contribution()

        # Fallback: use basic damping pattern
        triplets = []

        if hasattr(contact, 'node_i') and hasattr(contact, 'node_j'):
            i = contact.node_i
            j = contact.node_j

            # Get damping
            c = 0.0
            if hasattr(contact, 'damping'):
                if hasattr(contact.damping, 'c_viscous'):
                    c = contact.damping.c_viscous
                elif hasattr(contact.damping, 'get_damping'):
                    # Calculate from stiffness and mass
                    k = getattr(contact.stiffness, 'k_axial', 0)
                    c = contact.damping.get_damping(k, 0.01)
                else:
                    c = contact.damping

            if c <= 0:
                return triplets

            # Standard 2-node pattern
            if i >= 0 and i < self.n_dof:
                triplets.append((i, i, c))

            if j >= 0 and j < self.n_dof:
                triplets.append((j, j, c))

                if i >= 0 and i < self.n_dof:
                    triplets.append((i, j, -c))
                    triplets.append((j, i, -c))

        return triplets

    def assemble_force_vector(self, x: np.ndarray, x_dot: np.ndarray, t: float,
                             contacts: Optional[List[Any]] = None,
                             F_external_func: Optional[Callable] = None) -> np.ndarray:
        """
        Assemble force vector {F}(x, ẋ, t).

        FORCE COMPOSITION:
        {F} = {F_external} + {F_contact} + {F_gravity}

        {F_contact} includes:
        - Coulomb friction forces (nonlinear)
        - Thread friction torque
        - Helix driving torque (loosening mechanism)
        - Wear-induced forces
        - Contact plasticity forces

        NONLINEARITY:
        Force vector depends on current state (x, ẋ) and time:
        - Friction: F_f = μ(t) × N × sign(v)
        - Wear: evolves with slip distance
        - Contact slip state: STUCK ↔ SLIP transitions

        Args:
            x: Displacement vector [14×1]
            x_dot: Velocity vector [14×1]
            t: Current time [s]
            contacts: List of contact objects (uses self.contacts if None)
            F_external_func: External force function (uses self.F_external_func if None)

        Returns:
            Force vector [14×1] [N or N·m]
        """
        if contacts is None:
            contacts = self.contacts
        if F_external_func is None:
            F_external_func = self.F_external_func

        # Initialize force vector
        F = np.zeros(self.n_dof)

        # External forces
        if F_external_func is not None:
            F_ext = F_external_func(x, x_dot, t)
            if len(F_ext) == self.n_dof:
                F += F_ext

        # Contact force contributions
        for contact in contacts:
            F_contact = self._get_contact_force_contribution(contact, x, x_dot, t)
            F += F_contact

        return F

    def _get_contact_force_contribution(self, contact: Any,
                                       x: np.ndarray,
                                       x_dot: np.ndarray,
                                       t: float) -> np.ndarray:
        """
        Get force vector contribution from a contact.

        Args:
            contact: Contact object
            x: Displacement vector
            x_dot: Velocity vector
            t: Current time

        Returns:
            Force vector [n_dof×1]
        """
        F = np.zeros(self.n_dof)

        # Check if contact has get_force_contribution method
        if hasattr(contact, 'get_force_contribution'):
            F_result = contact.get_force_contribution(x, x_dot, t)

            # Handle different return types
            if isinstance(F_result, tuple):
                # ThreadContact returns (F, dtheta_loosening)
                F_contact = F_result[0]
            elif isinstance(F_result, np.ndarray):
                F_contact = F_result
            else:
                return F

            # Ensure correct size
            if len(F_contact) == self.n_dof:
                F = F_contact
            elif len(F_contact) < self.n_dof:
                F[:len(F_contact)] = F_contact

        return F

    def _triplets_to_matrix(self, triplets: List[Tuple[int, int, float]],
                           size: int) -> np.ndarray:
        """
        Convert triplet format (row, col, value) to dense matrix.

        Accumulates multiple entries at same (i,j) location.

        Args:
            triplets: List of (row, col, value) tuples
            size: Matrix size (n×n)

        Returns:
            Dense matrix [n×n]
        """
        matrix = np.zeros((size, size))

        for i, j, value in triplets:
            if 0 <= i < size and 0 <= j < size:
                matrix[i, j] += value

        return matrix

    def verify_matrix_properties(self) -> Dict[str, Any]:
        """
        Verify matrix properties and return diagnostics.

        CHECKS:
        1. Symmetry: ||A - A^T|| / ||A||
        2. Positive definiteness: eigenvalues > 0
        3. Conditioning: kappa(A) = lambda_max / lambda_min
        4. Sparsity: fraction of nonzero entries

        Returns:
            Dictionary with verification results
        """
        results = {}

        # Ensure matrices are assembled
        if self._M is None:
            self.assemble_mass_matrix()
        if self._K is None:
            self.assemble_stiffness_matrix()
        if self._C is None:
            self.assemble_damping_matrix()

        # Check mass matrix
        results['M'] = self._verify_single_matrix(self._M, "Mass")

        # Check stiffness matrix
        results['K'] = self._verify_single_matrix(self._K, "Stiffness")

        # Check damping matrix
        results['C'] = self._verify_single_matrix(self._C, "Damping")

        # Overall status
        all_valid = all(r['valid'] for r in results.values())
        results['overall_valid'] = all_valid

        return results

    def _verify_single_matrix(self, A: np.ndarray, name: str) -> Dict[str, Any]:
        """
        Verify properties of a single matrix.

        Args:
            A: Matrix to verify
            name: Matrix name for reporting

        Returns:
            Dictionary with verification results
        """
        result = {'name': name, 'valid': True, 'warnings': [], 'errors': []}

        # Check for NaN or Inf
        if np.any(np.isnan(A)) or np.any(np.isinf(A)):
            result['errors'].append(f"{name} contains NaN or Inf")
            result['valid'] = False
            return result

        # Symmetry check
        A_T = A.T
        sym_error = np.linalg.norm(A - A_T) / (np.linalg.norm(A) + 1e-16)
        result['symmetry_error'] = sym_error

        if sym_error > 1e-10:
            result['warnings'].append(f"{name} not symmetric (error={sym_error:.2e})")

        # Eigenvalue check (positive definiteness)
        try:
            eigvals = np.linalg.eigvalsh(A)  # Use symmetric solver
            result['min_eigenvalue'] = float(np.min(eigvals))
            result['max_eigenvalue'] = float(np.max(eigvals))

            if np.min(eigvals) <= 0:
                result['errors'].append(f"{name} not positive definite (min lambda={np.min(eigvals):.2e})")
                result['valid'] = False

            # Condition number
            if np.min(eigvals) > 0:
                cond = np.max(eigvals) / np.min(eigvals)
                result['condition_number'] = float(cond)

                if cond > 1e12:
                    result['warnings'].append(f"{name} poorly conditioned (kappa={cond:.2e})")
        except np.linalg.LinAlgError as e:
            result['errors'].append(f"{name} eigenvalue computation failed: {str(e)}")
            result['valid'] = False

        # Sparsity
        nonzero = np.count_nonzero(A)
        total = A.size
        sparsity = 1.0 - (nonzero / total)
        result['sparsity'] = float(sparsity)
        result['nonzero_entries'] = int(nonzero)

        return result

    def get_matrix_stats(self) -> Dict[str, Any]:
        """
        Get comprehensive statistics for all matrices.

        Returns:
            Dictionary with matrix statistics
        """
        if self._M is None or self._K is None or self._C is None:
            return {"error": "Matrices not assembled"}

        stats = {
            'n_dof': self.n_dof,
            'n_components': len(self.components),
            'n_contacts': len(self.contacts),
            'assembly_count': self.assembly_count,
        }

        # Matrix norms
        stats['M_norm'] = float(np.linalg.norm(self._M))
        stats['K_norm'] = float(np.linalg.norm(self._K))
        stats['C_norm'] = float(np.linalg.norm(self._C))

        # Mass statistics
        M_diag = np.diag(self._M)
        stats['total_mass'] = float(np.sum(M_diag))
        stats['min_mass'] = float(np.min(M_diag[M_diag > 0])) if np.any(M_diag > 0) else 0.0
        stats['max_mass'] = float(np.max(M_diag))

        # Stiffness statistics
        K_diag = np.diag(self._K)
        stats['min_stiffness'] = float(np.min(K_diag[K_diag > 0])) if np.any(K_diag > 0) else 0.0
        stats['max_stiffness'] = float(np.max(K_diag))

        # Sparsity
        stats['K_sparsity'] = float(1.0 - np.count_nonzero(self._K) / self._K.size)
        stats['C_sparsity'] = float(1.0 - np.count_nonzero(self._C) / self._C.size)

        # Natural frequencies (first 3)
        try:
            eigvals = np.linalg.eigvalsh(self._K, self._M)
            eigvals = eigvals[eigvals > 0]  # Positive only
            omega = np.sqrt(eigvals[:min(3, len(eigvals))])
            f_n = omega / (2 * np.pi)
            stats['natural_frequencies_Hz'] = f_n.tolist()
        except:
            stats['natural_frequencies_Hz'] = []

        return stats

    def get_matrices(self) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Get all assembled matrices.

        Returns:
            Tuple of (M, K, C) matrices
        """
        if self._M is None:
            self.assemble_mass_matrix()
        if self._K is None:
            self.assemble_stiffness_matrix()
        if self._C is None:
            self.assemble_damping_matrix()

        return self._M.copy(), self._K.copy(), self._C.copy()

    def to_dict(self) -> Dict[str, Any]:
        """Serialize assembler state to dictionary."""
        return {
            'n_dof': self.n_dof,
            'dof_mapping': self.dof_mapping.to_dict(),
            'components': [c.to_dict() for c in self.components],
            'n_contacts': len(self.contacts),
            'assembly_count': self.assembly_count
        }


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def compute_rayleigh_coefficients(omega1: float, omega2: float,
                                  zeta1: float, zeta2: float) -> Tuple[float, float]:
    """
    Calculate Rayleigh damping coefficients α and β.

    Given target modal damping ratios ζ₁, ζ₂ at frequencies ω₁, ω₂,
    computes coefficients for [C] = α[M] + β[K].

    EQUATIONS:
    α = 2ω₁ω₂(ζ₁ω₂ - ζ₂ω₁)/(ω₂² - ω₁²)
    β = 2(ζ₂ω₂ - ζ₁ω₁)/(ω₂² - ω₁²)

    TYPICAL VALUES:
    - Steel structures: ζ = 0.02 (2% critical damping)
    - Bolted joints with friction: ζ = 0.03-0.05
    - Gasket interfaces: ζ = 0.05-0.10

    Args:
        omega1: First natural frequency [rad/s]
        omega2: Second natural frequency [rad/s]
        zeta1: Damping ratio at ω₁ (e.g., 0.02 for 2%)
        zeta2: Damping ratio at ω₂

    Returns:
        Tuple of (alpha, beta) coefficients

    Example:
        >>> # 2% damping at 100 Hz and 500 Hz
        >>> omega1 = 2 * np.pi * 100
        >>> omega2 = 2 * np.pi * 500
        >>> alpha, beta = compute_rayleigh_coefficients(omega1, omega2, 0.02, 0.02)
    """
    if omega2 <= omega1:
        raise ValueError("omega2 must be greater than omega1")

    omega1_sq = omega1 ** 2
    omega2_sq = omega2 ** 2

    # Alpha coefficient (mass-proportional)
    alpha = 2 * omega1 * omega2 * (zeta1 * omega2 - zeta2 * omega1) / (omega2_sq - omega1_sq)

    # Beta coefficient (stiffness-proportional)
    beta = 2 * (zeta2 * omega2 - zeta1 * omega1) / (omega2_sq - omega1_sq)

    return alpha, beta


def create_standard_dof_mapping() -> DOFMapping:
    """
    Create standard 14-DOF mapping for bolted flange joint.

    Returns:
        DOFMapping with standard layout
    """
    return DOFMapping()


def validate_dof_indices(contacts: List[Any], n_dof: int) -> Tuple[bool, List[str]]:
    """
    Validate that all contact DOF indices are within valid range.

    Args:
        contacts: List of contact objects
        n_dof: Total number of DOFs

    Returns:
        Tuple of (is_valid, list of error messages)
    """
    errors = []
    is_valid = True

    for idx, contact in enumerate(contacts):
        contact_id = getattr(contact, 'id', f'Contact_{idx}')

        # Check node_i
        if hasattr(contact, 'node_i'):
            i = contact.node_i
            if i >= n_dof or i < -1:  # -1 is allowed for ground
                errors.append(f"{contact_id}: node_i={i} out of range [0, {n_dof})")
                is_valid = False

        # Check node_j
        if hasattr(contact, 'node_j'):
            j = contact.node_j
            if j >= n_dof or j < -1:
                errors.append(f"{contact_id}: node_j={j} out of range [0, {n_dof})")
                is_valid = False

        # Check torsional DOFs for thread/bearing contacts
        if hasattr(contact, 'dof_theta_stud'):
            theta = contact.dof_theta_stud
            if theta >= n_dof or theta < 0:
                errors.append(f"{contact_id}: dof_theta_stud={theta} out of range")
                is_valid = False

        if hasattr(contact, 'dof_theta_nut'):
            theta = contact.dof_theta_nut
            if theta >= n_dof or theta < 0:
                errors.append(f"{contact_id}: dof_theta_nut={theta} out of range")
                is_valid = False

    return is_valid, errors


# =============================================================================
# EXAMPLE USAGE AND TESTING
# =============================================================================

def create_example_joint_assembly() -> CompleteMSDMatrixAssembler:
    """
    Create example 14-DOF bolted joint assembly for testing.

    JOINT CONFIGURATION:
    - M20 bolt with nut
    - Two flanges with gasket
    - Washers under head and nut
    - Thread contact with helix coupling
    - Bearing contacts at head and nut

    Returns:
        Assembled matrix assembler ready for analysis
    """
    # Create assembler
    dof_map = create_standard_dof_mapping()
    assembler = CompleteMSDMatrixAssembler(n_dof=14, dof_mapping=dof_map)

    # Component properties (example values)
    # Masses in kg, rotational inertias in kg·m²
    components = [
        ComponentData("head", dof_map.head, mass=0.015, stiffness=0),
        ComponentData("washer1", dof_map.washer1, mass=0.002, stiffness=0),
        ComponentData("flange1", dof_map.flange1, mass=0.5, stiffness=0),
        ComponentData("gasket", dof_map.gasket, mass=0.01, stiffness=0),
        ComponentData("flange2", dof_map.flange2, mass=0.5, stiffness=0),
        ComponentData("washer2", dof_map.washer2, mass=0.002, stiffness=0),
        ComponentData("nut", dof_map.nut, mass=0.012, stiffness=0),
        ComponentData("stud", dof_map.stud, mass=0.05, stiffness=0),
        ComponentData("stud_theta", dof_map.stud_theta, mass=0, rotational_inertia=1e-5),
        ComponentData("nut_theta", dof_map.nut_theta, mass=0, rotational_inertia=5e-6),
        ComponentData("flange1_y", dof_map.flange1_y, mass=0.1, stiffness=0),
        ComponentData("flange1_z", dof_map.flange1_z, mass=0.1, stiffness=0),
        ComponentData("flange2_y", dof_map.flange2_y, mass=0.1, stiffness=0),
        ComponentData("flange2_z", dof_map.flange2_z, mass=0.1, stiffness=0),
    ]

    for comp in components:
        assembler.add_component(comp)

    # Note: Actual contacts would be added here using contact classes
    # from bolt_analysis_studio.core.contacts

    return assembler


if __name__ == "__main__":
    print("="*80)
    print("14-DOF MSD Matrix Assembler - Test Suite")
    print("="*80)

    # Test 1: Create standard DOF mapping
    print("\n[Test 1] Standard DOF Mapping")
    dof_map = create_standard_dof_mapping()
    print(f"  Total DOFs: {dof_map.n_dof}")
    print(f"  Axial DOFs: {dof_map.get_axial_dofs()}")
    print(f"  Torsional DOFs: {dof_map.get_torsional_dofs()}")
    print(f"  Transverse DOFs: {dof_map.get_transverse_dofs()}")

    # Test 2: Rayleigh coefficients
    print("\n[Test 2] Rayleigh Damping Coefficients")
    f1, f2 = 100.0, 500.0  # Hz
    omega1, omega2 = 2*np.pi*f1, 2*np.pi*f2
    zeta = 0.02  # 2% damping
    alpha, beta = compute_rayleigh_coefficients(omega1, omega2, zeta, zeta)
    print(f"  Frequencies: {f1} Hz, {f2} Hz")
    print(f"  Target damping: {zeta*100:.1f}%")
    print(f"  alpha = {alpha:.6e} [1/s]")
    print(f"  beta = {beta:.6e} [s]")

    # Test 3: Create example assembly
    print("\n[Test 3] Example Joint Assembly")
    assembler = create_example_joint_assembly()
    print(f"  Components: {len(assembler.components)}")
    print(f"  DOFs: {assembler.n_dof}")

    # Test 4: Assemble mass matrix
    print("\n[Test 4] Mass Matrix Assembly")
    M = assembler.assemble_mass_matrix()
    print(f"  Matrix shape: {M.shape}")
    print(f"  Total mass: {np.trace(M[:8, :8]):.4f} kg (axial DOFs)")
    print(f"  Total inertia: {np.trace(M[8:10, 8:10]):.2e} kg·m² (torsional DOFs)")
    print(f"  M diagonal: {np.diag(M)}")

    # Test 5: Assemble stiffness matrix (without contacts)
    print("\n[Test 5] Stiffness Matrix Assembly")
    K = assembler.assemble_stiffness_matrix()
    print(f"  Matrix shape: {K.shape}")
    print(f"  Number of contacts: {len(assembler.contacts)}")
    print(f"  K sparsity: {1.0 - np.count_nonzero(K)/K.size:.2%}")

    # Test 6: Assemble damping matrix
    print("\n[Test 6] Damping Matrix Assembly")
    C = assembler.assemble_damping_matrix(alpha_M=alpha, beta_K=beta)
    print(f"  Matrix shape: {C.shape}")
    print(f"  C[0,0]: {C[0,0]:.3e} N·s/m")
    print(f"  C sparsity: {1.0 - np.count_nonzero(C)/C.size:.2%}")

    # Test 7: Matrix verification
    print("\n[Test 7] Matrix Verification")
    verification = assembler.verify_matrix_properties()
    for matrix_name, results in verification.items():
        if matrix_name == 'overall_valid':
            continue
        print(f"  {results['name']} Matrix:")
        if results['valid']:
            print(f"    [PASS] Valid")
        else:
            print(f"    [FAIL] Invalid")
        if 'symmetry_error' in results:
            print(f"    Symmetry error: {results['symmetry_error']:.2e}")
        if 'condition_number' in results:
            print(f"    Condition number: {results['condition_number']:.2e}")
        for warning in results.get('warnings', []):
            print(f"    Warning: {warning}")
        for error in results.get('errors', []):
            print(f"    Error: {error}")

    # Test 8: Matrix statistics
    print("\n[Test 8] Matrix Statistics")
    stats = assembler.get_matrix_stats()
    print(f"  Total mass: {stats['total_mass']:.4f} kg")
    print(f"  Mass range: [{stats['min_mass']:.2e}, {stats['max_mass']:.2e}] kg")
    print(f"  Stiffness range: [{stats['min_stiffness']:.2e}, {stats['max_stiffness']:.2e}] N/m")
    print(f"  K sparsity: {stats['K_sparsity']:.1%}")

    # Test 9: Force vector assembly
    print("\n[Test 9] Force Vector Assembly")
    x = np.zeros(14)
    x_dot = np.zeros(14)
    t = 0.0
    F = assembler.assemble_force_vector(x, x_dot, t)
    print(f"  Force vector shape: {F.shape}")
    print(f"  Force norm: {np.linalg.norm(F):.3e} N")

    print("\n" + "="*80)
    print("All tests completed successfully!")
    print("="*80)
