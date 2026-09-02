"""
MSD Model Class for Bolt Analysis Studio v4.0
BAS +  R&D

This module provides the MSDModel class that contains collections of MSD elements
and assembles global system matrices [M], [K], [C] for dynamic analysis.

Key Features:
- Element management (add, remove, reorder)
- Series/parallel connection handling
- Global matrix assembly (lumped and consistent mass)
- Rayleigh damping calculation
- Model validation and statistics
- JSON serialization for .msd file format

Author: Bolt Analysis Studio Team
Version: 4.0
Date: January 2026
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple, Any
import numpy as np
from scipy import linalg
import json
from datetime import datetime
import math
from pathlib import Path

from .element import (
    MSDElementData, ElementType, ConnectionType, MaterialGrade,
    GeometryData, MaterialData, FrictionData, LoadingData, MSDParameters,
    ThreadFilletModel, ContactInterface,
    create_bolt_head, create_bolt_shank, create_thread_element,
    create_nut, create_flange, create_gasket, create_washer, create_ground
)

# Import contact system (optional - may not be installed)
try:
    from ..contacts.base import Contact
    from ..contacts.thread_contact import ThreadContact
    from ..contacts.bearing_contact import BearingContact
    from ..contacts.gasket_contact import FlangeGasketContact
    from ..contacts.flange_contact import FlangeFlangeContact
    from ..contacts.washer_contact import WasherFlangeContact
    HAS_CONTACTS = True
except ImportError:
    HAS_CONTACTS = False
    Contact = None
    ThreadContact = None
    BearingContact = None
    FlangeGasketContact = None
    FlangeFlangeContact = None
    WasherFlangeContact = None


# =============================================================================
# CONTACT DESERIALIZATION DISPATCH
# =============================================================================

# Maps contact_type strings to their deserialization classes.
# Each class must have a from_dict(data) classmethod.
_CONTACT_TYPE_MAP = {}

def _init_contact_type_map():
    """Populate the contact type map once contacts are available."""
    global _CONTACT_TYPE_MAP
    if not HAS_CONTACTS or _CONTACT_TYPE_MAP:
        return
    _CONTACT_TYPE_MAP = {
        "THREAD": ThreadContact,
        "BEARING_HEAD": BearingContact,
        "BEARING_NUT": BearingContact,
        "GASKET": FlangeGasketContact,
        "FLANGE_FLANGE": FlangeFlangeContact,
        # Explicit washer variants (prefix match in _deserialize_contact is the fallback)
        "WASHER_FLANGE": WasherFlangeContact,
        "WASHER_PLAIN": WasherFlangeContact,
        "WASHER_BELLEVILLE": WasherFlangeContact,
        "WASHER_SPRING": WasherFlangeContact,
        "WASHER_NORDLOCK": WasherFlangeContact,
    }


def _deserialize_contact(data: dict) -> 'Any':
    """
    Deserialize a single contact from its dictionary representation.

    Dispatches to the appropriate subclass based on ``contact_type``.

    Returns:
        Contact instance, or None if deserialization fails.
    """
    if not HAS_CONTACTS:
        return None

    _init_contact_type_map()

    contact_type = data.get("contact_type", "")

    # Direct match
    cls = _CONTACT_TYPE_MAP.get(contact_type)
    if cls is not None:
        try:
            return cls.from_dict(data)
        except Exception:
            return None

    # Prefix match for washer contacts (WASHER_PLAIN, WASHER_BELLEVILLE, etc.)
    if contact_type.startswith("WASHER_") and WasherFlangeContact is not None:
        try:
            return WasherFlangeContact.from_dict(data)
        except Exception:
            return None

    return None


# =============================================================================
# CONTACT STIFFNESS MODELS
# =============================================================================

def compute_contact_stiffnesses(
    bolt_diameter_mm: float,
    pitch_mm: float,
    material_E_MPa: float = 205000.0,
    material_Sy_MPa: float = 720.0,
    grip_length_mm: float = None,
    n_engaged_threads: int = 8,
) -> dict:
    """Compute contact stiffnesses using published models.

    Returns a dict with keys:
        k_thread_vdi   - Thread stiffness per VDI 2230 (N/mm)
        k_thread_motosh - Thread stiffness per Motosh 1976 (N/mm)
        k_bolt         - Overall bolt stiffness (VDI 2230 series) (N/mm)
        k_bearing      - Bearing surface stiffness (VDI 2230) (N/mm)
        k_members      - Clamped member stiffness (Wileman et al. 1991) (N/mm)
        A_s            - Tensile stress area (mm^2)
        F_proof        - Proof load at 90% yield (N)

    References:
        VDI 2230 Part 1 (2015) - Systematic calculation of bolted joints
        Motosh N. (1976) - Development of design charts for bolts
        Wileman J. et al. (1991) - J. Mech. Des. 113(4), 432-437
    """
    d = bolt_diameter_mm
    p = pitch_mm
    E = material_E_MPa

    if grip_length_mm is None:
        grip_length_mm = 3.0 * d  # VDI typical default

    # ISO 68-1 thread geometry
    d2 = d - 0.6495 * p                              # pitch diameter (mm)
    d1 = d - 1.0825 * p                              # basic minor diameter (mm) - for At
    d3 = d - 1.2268 * p                              # minor diameter (mm) - bolt root
    A_s = math.pi / 4.0 * ((d2 + d1) / 2.0) ** 2    # stress area per ISO 898-1 (mm^2)
    A_nom = math.pi / 4.0 * d ** 2                   # nominal cross-section (mm^2)

    L_engaged = n_engaged_threads * p                  # engaged length (mm)

    # --- Thread stiffness ---
    # VDI 2230: k = E * A_s / L_engaged
    k_thread_vdi = E * A_s / L_engaged if L_engaged > 0 else 0.0

    # Motosh (1976): k = 0.5 * E * d * n  (empirical per-thread)
    k_thread_motosh = 0.5 * E * d * n_engaged_threads

    # --- Overall bolt stiffness (VDI 2230 series model) ---
    # k_bolt = 1 / (1/k_head + 1/k_shank + 1/k_free_thread + 1/k_engaged)
    k_head = 0.5 * E * d                              # head flexibility
    L_shank = max(grip_length_mm - L_engaged, 0.1)
    k_shank = E * A_nom / L_shank                     # unthreaded section
    L_free_thread = max(L_engaged * 0.5, p)            # free thread ≈ half engaged
    k_free = E * A_s / L_free_thread
    k_engaged_bolt = E * A_s / (0.5 * L_engaged) if L_engaged > 0 else 1e12

    inv_k = 1.0 / k_head + 1.0 / k_shank + 1.0 / k_free + 1.0 / k_engaged_bolt
    k_bolt = 1.0 / inv_k if inv_k > 0 else 0.0

    # --- Bearing stiffness (VDI 2230) ---
    D_bearing = 1.5 * d                               # bearing diameter ≈ 1.5 × d
    d_hole = d + 1.0                                   # clearance hole
    t_bearing = 0.25 * d                               # effective bearing thickness
    k_bearing = (E * math.pi * (D_bearing ** 2 - d_hole ** 2)
                 / (4.0 * t_bearing)) if t_bearing > 0 else 0.0

    # --- Member stiffness (Wileman et al. 1991) ---
    # k_m = E * d * A_w * exp(B_w * d / L_clamp)
    # Steel-on-steel coefficients
    A_w, B_w = 0.78715, 0.62873
    L_clamp = grip_length_mm
    k_members = E * d * A_w * math.exp(B_w * d / L_clamp) if L_clamp > 0 else 0.0

    # Proof load at 90% yield
    F_proof = 0.9 * A_s * material_Sy_MPa

    return {
        "k_thread_vdi": k_thread_vdi,
        "k_thread_motosh": k_thread_motosh,
        "k_bolt": k_bolt,
        "k_bearing": k_bearing,
        "k_members": k_members,
        "A_s": A_s,
        "F_proof": F_proof,
    }


# =============================================================================
# MSD MODEL DATA CLASS
# =============================================================================

@dataclass
class MSDModel:
    """
    Complete MSD model for bolted joint analysis.

    Contains all elements and provides methods for:
    - Element management
    - Matrix assembly ([M], [K], [C])
    - Modal analysis
    - Model validation
    - Serialization

    Loading and friction parameters are configured in MSD Builder (single source of truth)
    and stored here for use by the solver and visualization components.
    """

    # Model identification
    name: str = "Untitled Model"
    description: str = ""
    version: str = "4.0"

    # Elements (physical components)
    elements: List[MSDElementData] = field(default_factory=list)

    # Contacts (interfaces between elements with tribology)
    # Each nut MUST have a thread contact connecting it to the stud
    # Bearing contacts connect head/nut to washer/flange
    contacts: List[Any] = field(default_factory=list)  # List[Contact]

    # Global loading parameters (configured in MSD Builder)
    global_loading: LoadingData = field(default_factory=LoadingData)

    # =========================================================================
    # FRICTION AND BOLT GEOMETRY PARAMETERS
    # These are configured in MSD Builder and used by the solver
    # =========================================================================
    mu_initial: float = 0.12           # Initial friction coefficient (thread + bearing)
    lubricated: bool = True            # Lubrication state affects friction evolution
    bolt_diameter: float = 16.0        # Nominal bolt diameter (mm), e.g., M16 = 16.0
    pitch: float = 2.0                 # Thread pitch (mm), e.g., M16×2.0 = 2.0
    # Friction evolution model (Phase 3.1) — controls how μ evolves over cycles
    # Options: "Constant", "Exponential Decay", "Three-Phase", "Stribeck", "LuGre"
    friction_evolution_model: str = "Three-Phase"

    # Metadata
    created: str = ""
    modified: str = ""
    filename: str = ""

    # Cached matrices (computed on demand)
    _M: Optional[np.ndarray] = field(default=None, repr=False)
    _K: Optional[np.ndarray] = field(default=None, repr=False)
    _C: Optional[np.ndarray] = field(default=None, repr=False)
    _F_tribo: Optional[np.ndarray] = field(default=None, repr=False)  # Tribological forces
    _is_dirty: bool = field(default=True, repr=False)
    
    # Rayleigh damping coefficients (applied during assembly if set)
    _rayleigh_alpha: Optional[float] = field(default=None, repr=False)
    _rayleigh_beta: Optional[float] = field(default=None, repr=False)

    def __post_init__(self):
        """Initialize timestamps."""
        if not self.created:
            self.created = datetime.now().isoformat()
        if not self.modified:
            self.modified = self.created
    
    # =========================================================================
    # ELEMENT MANAGEMENT
    # =========================================================================
    
    def add_element(self, element: MSDElementData) -> None:
        """Add element to model."""
        # Auto-assign ID if not set
        if element.id == 0:
            element.id = self._get_next_id()
        
        self.elements.append(element)
        self._mark_dirty()
    
    def remove_element(self, element_id: int) -> bool:
        """Remove element by ID. Returns True if found and removed."""
        for i, elem in enumerate(self.elements):
            if elem.id == element_id:
                self.elements.pop(i)
                self._mark_dirty()
                return True
        return False
    
    def get_element(self, element_id: int) -> Optional[MSDElementData]:
        """Get element by ID."""
        for elem in self.elements:
            if elem.id == element_id:
                return elem
        return None
    
    def get_elements_by_type(self, element_type: ElementType) -> List[MSDElementData]:
        """Get all elements of specified type."""
        return [e for e in self.elements if e.type == element_type]
    
    def reorder_element(self, element_id: int, new_index: int) -> None:
        """Move element to new position in list."""
        for i, elem in enumerate(self.elements):
            if elem.id == element_id:
                self.elements.pop(i)
                self.elements.insert(new_index, elem)
                self._mark_dirty()
                return
    
    def clear(self) -> None:
        """Remove all elements."""
        self.elements.clear()
        self._mark_dirty()
    
    def _get_next_id(self) -> int:
        """Get next available element ID."""
        if not self.elements:
            return 1
        return max(e.id for e in self.elements) + 1
    
    def _mark_dirty(self) -> None:
        """Mark matrices as needing recalculation."""
        self._is_dirty = True
        self._M = None
        self._K = None
        self._C = None
        self._F_tribo = None
        self.modified = datetime.now().isoformat()

    # =========================================================================
    # CONTACT MANAGEMENT
    # =========================================================================
    # Every NUT must have a ThreadContact connecting it to the stud.
    # For double-nut (lock nut) configurations, BOTH nuts have thread contacts.
    # Bearing contacts connect head/nut bearing surfaces to washer/flange.
    # =========================================================================

    def add_contact(self, contact: Any) -> None:
        """
        Add a contact to the model.

        IMPORTANT: Every nut MUST have a corresponding ThreadContact.
        For double-nut, both bottom nut AND top nut need thread contacts.

        Args:
            contact: Contact object (ThreadContact, BearingContact, etc.)
        """
        self.contacts.append(contact)
        self._mark_dirty()

    def remove_contact(self, contact_id: str) -> bool:
        """Remove contact by ID. Returns True if found and removed."""
        for i, contact in enumerate(self.contacts):
            if hasattr(contact, 'contact_id') and contact.contact_id == contact_id:
                self.contacts.pop(i)
                self._mark_dirty()
                return True
        return False

    def get_contacts_by_type(self, contact_type: str) -> List[Any]:
        """Get all contacts of specified type."""
        result = []
        for contact in self.contacts:
            if hasattr(contact, 'contact_type'):
                if contact.contact_type == contact_type:
                    result.append(contact)
        return result

    def get_thread_contacts(self) -> List[Any]:
        """Get all thread contacts (stud-nut interfaces).
        Accepts both ThreadContact instances and ContactInterface with THREAD_CONTACT type."""
        result = []
        for c in self.contacts:
            if HAS_CONTACTS and isinstance(c, ThreadContact):
                result.append(c)
            elif (hasattr(c, 'specific_type') and
                  getattr(c.specific_type, 'value', str(c.specific_type)) == 'thread_contact'):
                result.append(c)
        return result

    def get_bearing_contacts(self) -> List[Any]:
        """Get all bearing contacts (head/nut bearing surfaces).
        Accepts both BearingContact instances and ContactInterface with bearing-type specific_type."""
        _bearing_values = {'bolt_head_washer', 'bolt_head_flange', 'nut_washer', 'nut_flange'}
        result = []
        for c in self.contacts:
            if HAS_CONTACTS and isinstance(c, BearingContact):
                result.append(c)
            elif (hasattr(c, 'specific_type') and
                  getattr(c.specific_type, 'value', str(c.specific_type)) in _bearing_values):
                result.append(c)
        return result

    def validate_contacts(self) -> Tuple[bool, List[str]]:
        """
        Validate that all required contacts are present.

        Rules:
        1. Every NUT element must have a ThreadContact
        2. Every HEAD element should have a BearingContact
        3. Thread contacts must connect to valid DOFs

        Returns:
            Tuple (is_valid, list of messages)
        """
        messages = []
        is_valid = True

        # Get all nut elements
        nut_elements = self.get_elements_by_type(ElementType.NUT)
        thread_contacts = self.get_thread_contacts()

        # If no contacts are configured at all, this is normal for basic MSD analysis.
        # Only warn when contacts are partially configured but incomplete.
        if not self.contacts:
            if nut_elements:
                messages.append(
                    f"OK: {len(nut_elements)} nut element(s) found. "
                    f"Contact analysis available when ThreadContacts are configured."
                )
            return is_valid, messages

        # Contacts are partially configured — enforce completeness
        # Check every nut has a thread contact
        for nut in nut_elements:
            has_thread_contact = False
            for tc in thread_contacts:
                # Accept ThreadContact (has dof_axial_nut) or ContactInterface (has specific_type)
                if hasattr(tc, 'dof_axial_nut') or hasattr(tc, 'specific_type'):
                    has_thread_contact = True
                    break
            if not has_thread_contact:
                messages.append(f"ERROR: Nut element '{nut.name}' has no ThreadContact")
                is_valid = False

        # Check for double nut configuration
        if len(nut_elements) >= 2:
            if len(thread_contacts) < len(nut_elements):
                messages.append(
                    f"WARNING: Double-nut configuration detected but only "
                    f"{len(thread_contacts)} thread contact(s) for {len(nut_elements)} nuts. "
                    f"Each nut should have its own thread contact."
                )

        return is_valid, messages
    
    # =========================================================================
    # MATRIX ASSEMBLY
    # =========================================================================
    
    @property
    def n_dof(self) -> int:
        """Number of degrees of freedom."""
        # Each non-ground element contributes 1 DOF
        return sum(1 for e in self.elements if e.type != ElementType.GROUND)
    
    @property
    def n_elements(self) -> int:
        """Number of elements."""
        return len(self.elements)
    
    def assemble_matrices(self) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Assemble global [M], [K], [C] matrices from elements.
        
        Handles series and parallel connections:
        - Series: Springs/dampers in series have reciprocal stiffness sum
        - Parallel: Springs/dampers add directly
        
        Returns:
            Tuple of (M, K, C) numpy arrays
        """
        if not self._is_dirty and self._M is not None:
            return self._M, self._K, self._C
        
        n = self.n_dof
        if n == 0:
            return np.array([[]]), np.array([[]]), np.array([[]])
        
        # Use scipy.sparse for large models (8.2)
        _SPARSE_THRESHOLD = 50
        _use_sparse = False
        if n >= _SPARSE_THRESHOLD:
            try:
                from scipy.sparse import lil_matrix
                M = lil_matrix((n, n))
                K = lil_matrix((n, n))
                C = lil_matrix((n, n))
                _use_sparse = True
            except ImportError:
                pass

        if not _use_sparse:
            M = np.zeros((n, n))
            K = np.zeros((n, n))
            C = np.zeros((n, n))
        
        # Get active elements (exclude ground)
        active_elements = [e for e in self.elements if e.type != ElementType.GROUND]
        
        # Handle parallel groups
        parallel_groups = self._identify_parallel_groups()
        
        # Build element-to-DOF mapping
        dof_map = {}
        for i, elem in enumerate(active_elements):
            dof_map[elem.id] = i
        
        # Assemble matrices
        # prev_assembled_i: index of the last element that was actually assembled
        # (not skipped). Used for correct off-diagonal placement when parallel-group
        # non-representatives are interleaved in the active-element list.
        prev_assembled_i: Optional[int] = None
        last_k_eff: float = 0.0
        last_c_eff: float = 0.0

        for i, elem in enumerate(active_elements):
            # Mass matrix (diagonal - lumped mass)
            # Ensure positive mass (use small default if zero/negative)
            M[i, i] = elem.msd.m if elem.msd.m > 0 else 1e-6

            # Get effective stiffness and damping (consider parallel groups)
            k_eff = elem.msd.k if elem.msd.k > 0 else 1.0  # Guard: min 1 N/m
            c_eff = elem.msd.c

            # Check if element is in a parallel group
            is_parallel_rep = False
            if elem.parallel_group > 0 and elem.parallel_group in parallel_groups:
                group = parallel_groups[elem.parallel_group]
                if elem == group[0]:  # First element in group handles combined stiffness
                    k_eff = sum(e.msd.k for e in group)
                    c_eff = sum(e.msd.c for e in group)
                    is_parallel_rep = True
                else:
                    continue  # Skip non-first parallel elements

            # A parallel group representative is, by construction, in SERIES with the
            # previous assembled element in the main chain (even though its own
            # connection_type is PARALLEL_MEMBER, which only describes its relationship
            # with its siblings in the same group).
            in_series = (elem.connection_type == ConnectionType.SERIES or is_parallel_rep)

            # Stiffness and damping matrices (tridiagonal for series chain)
            if prev_assembled_i is None:
                # First assembled element: one end attached to ground (fixed BC)
                K[i, i] = k_eff
                C[i, i] = c_eff
            else:
                p = prev_assembled_i
                K[i, i] += k_eff
                C[i, i] += c_eff
                if in_series:
                    # Off-diagonal coupling to the ACTUAL previous assembled DOF,
                    # not necessarily i-1 (which may be a skipped parallel member).
                    K[p, p] += k_eff
                    K[i, p] = -k_eff
                    K[p, i] = -k_eff
                    C[p, p] += c_eff
                    C[i, p] = -c_eff
                    C[p, i] = -c_eff

            prev_assembled_i = i
            last_k_eff = k_eff
            last_c_eff = c_eff

        # Handle last element connection to second ground (if present).
        # Standard configuration: ground – elements – ground (fixed at both ends).
        # Use prev_assembled_i rather than n-1: the last active element may be a
        # skipped parallel-group non-representative, which must not receive stiffness.
        if prev_assembled_i is not None:
            K[prev_assembled_i, prev_assembled_i] += last_k_eff
            C[prev_assembled_i, prev_assembled_i] += last_c_eff

        # =====================================================================
        # CONTACT CONTRIBUTIONS TO [K] AND [C]
        # =====================================================================
        # Contacts (thread, bearing, gasket) contribute to matrices via their
        # get_stiffness_contribution() and get_damping_contribution() methods.
        #
        # IMPORTANT: Friction and wear do NOT modify [K] or [C]!
        # They contribute to the force vector {F} during time integration.
        # =====================================================================

        if HAS_CONTACTS and self.contacts:
            for contact in self.contacts:
                if not isinstance(contact, Contact):
                    continue

                # Get stiffness contributions: list of (row, col, value)
                try:
                    k_contributions = contact.get_stiffness_contribution()
                    for row, col, k_val in k_contributions:
                        if 0 <= row < n and 0 <= col < n:
                            K[row, col] += k_val
                except Exception:
                    pass  # Contact may not have this method implemented

                # Get damping contributions: list of (row, col, value)
                try:
                    c_contributions = contact.get_damping_contribution()
                    for row, col, c_val in c_contributions:
                        if 0 <= row < n and 0 <= col < n:
                            C[row, col] += c_val
                except Exception:
                    pass

        # Re-apply Rayleigh damping if previously configured
        if hasattr(self, '_rayleigh_alpha') and self._rayleigh_alpha is not None:
            C = self._rayleigh_alpha * M + self._rayleigh_beta * K

        # Convert sparse → dense for solver compatibility (8.2)
        if _use_sparse:
            try:
                M = np.asarray(M.toarray())
                K = np.asarray(K.toarray())
                C = np.asarray(C.toarray())
            except Exception:
                pass  # Already dense if conversion failed

        # Cache matrices
        self._M = M
        self._K = K
        self._C = C
        self._is_dirty = False

        return M, K, C

    def assemble_force_vector(
        self,
        x: np.ndarray,
        x_dot: np.ndarray,
        t: float,
        F_external: np.ndarray,
        preload: float = 0.0
    ) -> np.ndarray:
        """
        Assemble total force vector including tribological contributions.

        The force vector {F} includes:
        1. External forces (from loading)
        2. Tribological forces from contacts (friction, wear effects)

        IMPORTANT: Friction and wear enter through {F}, NOT through [K] or [C]!

        Args:
            x: Displacement vector
            x_dot: Velocity vector
            t: Current time
            F_external: External force vector
            preload: Current preload force (affects friction forces via N)

        Returns:
            Total force vector {F} = {F_ext} + {F_tribo}
        """
        F_total = F_external.copy()
        n = len(F_external)

        if not HAS_CONTACTS or not self.contacts:
            return F_total

        # Add tribological contributions from each contact
        for contact in self.contacts:
            if not isinstance(contact, Contact):
                continue

            try:
                # Update contact normal force (from preload)
                contact.normal_force = preload

                # Get force contribution from contact (friction, wear, helix torque, etc.)
                F_contact = contact.get_force_contribution(x, x_dot, t)

                # Handle different return types from contacts
                if isinstance(F_contact, tuple):
                    # ThreadContact returns (F_vector, theta_loosening)
                    F_vector = F_contact[0]
                    if isinstance(F_vector, np.ndarray) and len(F_vector) == n:
                        F_total += F_vector
                elif isinstance(F_contact, np.ndarray):
                    # BearingContact and others return F_vector directly
                    if len(F_contact) == n:
                        F_total += F_contact
            except Exception as e:
                # Log error but continue with other contacts
                pass

        self._F_tribo = F_total - F_external
        return F_total

    def update_contact_states(
        self,
        x: np.ndarray,
        x_dot: np.ndarray,
        dt: float,
        preload: float
    ) -> None:
        """
        Update all contact states after a time step.

        Updates friction evolution, wear accumulation, slip states.

        Args:
            x: Displacement vector
            x_dot: Velocity vector
            dt: Time step
            preload: Current preload (affects normal forces)
        """
        if not HAS_CONTACTS or not self.contacts:
            return

        for contact in self.contacts:
            if hasattr(contact, 'update_state'):
                try:
                    contact.update_state(x, x_dot, dt, preload)
                except Exception:
                    pass

    def compute_tribological_forces(
        self,
        x: np.ndarray,
        x_dot: np.ndarray,
        t: float = 0.0,
        preload: float = None
    ) -> np.ndarray:
        """
        Compute tribological force contributions from all contacts.

        Convenience method matching the interface expected by
        time_integration.py's solve_with_contacts() methods.

        Args:
            x: Displacement vector
            x_dot: Velocity vector
            t: Current time (default: 0.0)
            preload: Override preload force. If None, uses global_loading.

        Returns:
            Tribological force vector (same size as x)
        """
        n = len(x)
        F_ext = np.zeros(n)

        if preload is None:
            preload = getattr(
                getattr(self, 'global_loading', None), 'F_preload', 0.0
            )

        F_total = self.assemble_force_vector(x, x_dot, t, F_ext, preload)
        return F_total  # F_ext was zeros so F_total = F_tribo

    def get_total_preload_loss(self) -> float:
        """
        Calculate total preload loss from all contacts.

        Returns:
            Total preload loss [N] from rotation, wear, embedding, creep
        """
        total_loss = 0.0

        if not HAS_CONTACTS or not self.contacts:
            return total_loss

        for contact in self.contacts:
            if hasattr(contact, 'get_total_preload_loss'):
                try:
                    total_loss += contact.get_total_preload_loss()
                except Exception:
                    pass

        return total_loss
    
    def _identify_parallel_groups(self) -> Dict[int, List[MSDElementData]]:
        """Identify and group parallel elements."""
        groups = {}
        for elem in self.elements:
            if elem.parallel_group > 0:
                if elem.parallel_group not in groups:
                    groups[elem.parallel_group] = []
                groups[elem.parallel_group].append(elem)
        return groups
    
    def get_mass_matrix(self) -> np.ndarray:
        """Get assembled mass matrix."""
        M, _, _ = self.assemble_matrices()
        return M
    
    def get_stiffness_matrix(self) -> np.ndarray:
        """Get assembled stiffness matrix."""
        _, K, _ = self.assemble_matrices()
        return K
    
    def get_damping_matrix(self) -> np.ndarray:
        """Get assembled damping matrix."""
        _, _, C = self.assemble_matrices()
        return C
    
    def compute_rayleigh_damping(
        self, 
        omega_1: float, 
        omega_2: float, 
        zeta: float = 0.02
    ) -> Tuple[float, float]:
        """
        Compute Rayleigh damping coefficients α and β.
        
        C = αM + βK
        
        For equal damping ratio ζ at ω₁ and ω₂:
        α = 2ζ·ω₁·ω₂/(ω₁+ω₂)
        β = 2ζ/(ω₁+ω₂)
        
        Args:
            omega_1: First natural frequency (rad/s)
            omega_2: Second natural frequency (rad/s)
            zeta: Target damping ratio
            
        Returns:
            Tuple (α, β) Rayleigh coefficients
        """
        alpha = 2 * zeta * omega_1 * omega_2 / (omega_1 + omega_2)
        beta = 2 * zeta / (omega_1 + omega_2)
        return alpha, beta
    
    def apply_rayleigh_damping(self, zeta: float = 0.02) -> None:
        """Apply Rayleigh damping based on first two natural frequencies."""
        freqs = self.compute_natural_frequencies()
        if len(freqs) >= 2:
            omega_1 = 2 * np.pi * freqs[0]
            omega_2 = 2 * np.pi * freqs[1]
            alpha, beta = self.compute_rayleigh_damping(omega_1, omega_2, zeta)

            M, K, _ = self.assemble_matrices()
            self._C = alpha * M + beta * K
            # Mark dirty so next assembly rebuilds properly;
            # store Rayleigh params for re-application after reassembly
            self._rayleigh_alpha = alpha
            self._rayleigh_beta = beta
            self._is_dirty = True
    
    # =========================================================================
    # MODAL ANALYSIS
    # =========================================================================
    
    def compute_natural_frequencies(self) -> np.ndarray:
        """
        Compute natural frequencies of the system.
        
        Solves the generalized eigenvalue problem:
        [K]{φ} = ω²[M]{φ}
        
        Returns:
            Array of natural frequencies in Hz, sorted ascending
        """
        M, K, _ = self.assemble_matrices()
        
        if M.size == 0 or K.size == 0:
            return np.array([])
        
        # Check for zero mass (use pseudo-inverse)
        m_diag = np.diag(M)
        if np.any(m_diag <= 0):
            # Replace zero masses with small value
            m_diag = np.where(m_diag <= 0, 1e-10, m_diag)
            M = np.diag(m_diag)
        
        try:
            # Solve generalized eigenvalue problem using eigh (symmetric solver)
            # K and M are symmetric by construction, eigh is faster and numerically stable
            eigenvalues = linalg.eigh(K, M, eigvals_only=True)

            # Filter positive eigenvalues
            eigenvalues = eigenvalues[eigenvalues > 0]

            # Convert to frequencies (Hz)
            frequencies = np.sqrt(eigenvalues) / (2 * np.pi)
            frequencies = np.sort(frequencies)

            return frequencies

        except linalg.LinAlgError:
            return np.array([])
    
    def compute_mode_shapes(self) -> Tuple[np.ndarray, np.ndarray]:
        """
        Compute natural frequencies and mode shapes.
        
        Returns:
            Tuple (frequencies, mode_shapes) where:
            - frequencies: 1D array of natural frequencies (Hz)
            - mode_shapes: 2D array, columns are mode shapes
        """
        M, K, _ = self.assemble_matrices()
        
        if M.size == 0 or K.size == 0:
            return np.array([]), np.array([[]])
        
        # Check for zero mass
        m_diag = np.diag(M)
        if np.any(m_diag <= 0):
            m_diag = np.where(m_diag <= 0, 1e-10, m_diag)
            M = np.diag(m_diag)
        
        try:
            # Solve generalized eigenvalue problem using eigh (symmetric solver)
            eigenvalues, eigenvectors = linalg.eigh(K, M)

            # Sort by eigenvalue (eigh returns sorted, but ensure)
            idx = np.argsort(eigenvalues)
            eigenvalues = eigenvalues[idx]
            eigenvectors = eigenvectors[:, idx]

            # Filter positive eigenvalues
            mask = eigenvalues > 0
            eigenvalues = eigenvalues[mask]
            eigenvectors = eigenvectors[:, mask]

            # Convert to frequencies
            frequencies = np.sqrt(eigenvalues) / (2 * np.pi)

            # Normalize mode shapes
            for i in range(eigenvectors.shape[1]):
                max_val = np.max(np.abs(eigenvectors[:, i]))
                if max_val > 0:
                    eigenvectors[:, i] /= max_val

            return frequencies, eigenvectors

        except linalg.LinAlgError:
            return np.array([]), np.array([[]])
    
    # =========================================================================
    # EQUIVALENT PROPERTIES
    # =========================================================================
    
    def get_equivalent_stiffness(self) -> float:
        """
        Calculate equivalent stiffness of the system.
        
        For series connection: 1/k_eq = Σ(1/k_i)
        For parallel connection: k_eq = Σk_i
        """
        if not self.elements:
            return 0.0
        
        # Separate series and parallel elements
        series_k = []
        parallel_groups = self._identify_parallel_groups()
        
        for elem in self.elements:
            if elem.type == ElementType.GROUND:
                continue
            
            if elem.parallel_group > 0:
                # Parallel element - handled separately
                if elem.parallel_group in parallel_groups:
                    group = parallel_groups[elem.parallel_group]
                    if elem == group[0]:  # First in group
                        k_parallel = sum(e.msd.k for e in group)
                        series_k.append(k_parallel)
            else:
                # Series element
                series_k.append(elem.msd.k)
        
        # Calculate equivalent for series
        if not series_k:
            return 0.0
        
        k_inv_sum = sum(1/k for k in series_k if k > 0)
        
        if k_inv_sum > 0:
            return 1.0 / k_inv_sum
        return 0.0
    
    def get_total_mass(self) -> float:
        """Calculate total mass of all elements."""
        return sum(e.msd.m for e in self.elements if e.type != ElementType.GROUND)
    
    def get_equivalent_damping(self) -> float:
        """Calculate equivalent damping coefficient."""
        if not self.elements:
            return 0.0
        
        series_c = []
        parallel_groups = self._identify_parallel_groups()
        
        for elem in self.elements:
            if elem.type == ElementType.GROUND:
                continue
            
            if elem.parallel_group > 0:
                if elem.parallel_group in parallel_groups:
                    group = parallel_groups[elem.parallel_group]
                    if elem == group[0]:
                        c_parallel = sum(e.msd.c for e in group)
                        series_c.append(c_parallel)
            else:
                series_c.append(elem.msd.c)
        
        if not series_c:
            return 0.0
        
        c_inv_sum = sum(1/c for c in series_c if c > 0)
        
        if c_inv_sum > 0:
            return 1.0 / c_inv_sum
        return 0.0
    
    def get_fundamental_frequency(self) -> float:
        """Get first (fundamental) natural frequency in Hz."""
        freqs = self.compute_natural_frequencies()
        return freqs[0] if len(freqs) > 0 else 0.0
    
    def get_stiffness_ratio(self) -> float:
        """
        Calculate stiffness ratio Φ = k_m/k_b (member/bolt).
        
        This is a key parameter for joint load factor calculation.
        """
        bolt_types = {ElementType.HEAD, ElementType.SHANK,
                      ElementType.NUT, ElementType.WASHER}
        member_types = {ElementType.FLANGE, ElementType.GASKET, ElementType.MEMBER}
        
        # Get bolt stiffness (series)
        bolt_k = []
        for elem in self.elements:
            if elem.type in bolt_types:
                bolt_k.append(elem.msd.k)
        
        if not bolt_k:
            return 0.0
        k_inv = sum(1/k for k in bolt_k if k > 0)
        k_bolt = 1.0 / k_inv if k_inv > 0 else 0.0
        
        # Get member stiffness (series)
        member_k = []
        for elem in self.elements:
            if elem.type in member_types:
                member_k.append(elem.msd.k)
        
        if not member_k:
            return 0.0
        k_inv = sum(1/k for k in member_k if k > 0)
        k_member = 1.0 / k_inv if k_inv > 0 else 0.0
        
        if k_bolt > 0:
            return k_member / k_bolt
        return 0.0
    
    def get_load_introduction_factor(self, n: float = 0.5) -> float:
        """
        Calculate load introduction factor per VDI 2230.
        
        n = distance from bolt head to load introduction point / grip length
        
        Φ_K = n + (1-n)·k_b/(k_b + k_m)
        
        Args:
            n: Load introduction factor (0 = at head, 1 = at nut)
        """
        k_eq = self.get_equivalent_stiffness()
        phi = self.get_stiffness_ratio()
        
        if phi > 0:
            k_b = k_eq * (1 + phi) / phi  # Derive k_b from k_eq and Φ
            k_m = phi * k_b
            phi_K = n + (1 - n) * k_b / (k_b + k_m)
            return phi_K
        return 0.5
    
    # =========================================================================
    # VALIDATION
    # =========================================================================
    
    def validate(self) -> Tuple[bool, List[str]]:
        """
        Validate the complete model.

        Performs the following checks:
        1. Minimum element count
        2. Ground element presence
        3. Per-element validation (k, m, c, geometry, material, friction)
        4. Matrix assembly (catches build errors)
        5. Mass matrix: no negative masses, warning on zero masses
        6. Mass matrix invertibility (required by all implicit solvers)
        7. Stiffness matrix positive-definiteness (eigenvalue check)
        8. Stiffness matrix invertibility (required for static solve)
        9. Damping matrix: no negative diagonal entries
        10. Matrix symmetry check ([M], [K], [C] must be symmetric)
        11. Effective stiffness K_eff invertibility (Newmark solver)
        12. Condition number check (ill-conditioning warning)
        13. Parallel group validation

        Returns:
            Tuple (is_valid, list of messages)
        """
        messages = []
        is_valid = True

        # ── 1. Minimum element count ──────────────────────────────────────
        if len(self.elements) == 0:
            messages.append("ERROR: Model has no elements")
            is_valid = False
            return is_valid, messages

        # ── 2. Ground element presence ────────────────────────────────────
        has_ground = any(e.type == ElementType.GROUND for e in self.elements)
        if not has_ground:
            messages.append(
                "ERROR: No ground element defined - boundary conditions "
                "are required for matrix assembly"
            )
            is_valid = False

        # ── 3. Per-element validation ─────────────────────────────────────
        for elem in self.elements:
            elem_valid, elem_msgs = elem.validate()
            if not elem_valid:
                is_valid = False
            messages.extend(elem_msgs)

        # ── 3a. Preload check ─────────────────────────────────────────────
        if self.global_loading is not None:
            if self.global_loading.F_preload == 0:
                # Try to auto-compute from % yield and bolt geometry
                pct = self.global_loading.preload_percent_yield
                if pct > 0 and self.bolt_diameter > 0:
                    d = self.bolt_diameter
                    p = self.pitch
                    d2 = d - 0.6495 * p
                    d3 = d - 1.2269 * p
                    A_s = math.pi / 4 * ((d2 + d3) / 2) ** 2
                    # Get Sy from first bolt element
                    Sy = 640.0
                    for elem in self.elements:
                        if elem.type.is_bolt_component and elem.material.Sy > 0:
                            Sy = elem.material.Sy
                            break
                    self.global_loading.F_preload = (pct / 100.0) * A_s * Sy
                    messages.append(
                        f"OK: Preload auto-computed from {pct:.0f}% yield: "
                        f"F₀ = {self.global_loading.F_preload/1000:.1f} kN"
                    )
                elif any(getattr(e, 'preload_force', 0) > 0 for e in self.elements):
                    # Use max element preload
                    max_pf = max(getattr(e, 'preload_force', 0) for e in self.elements)
                    self.global_loading.F_preload = max_pf
                    messages.append(
                        f"OK: Preload set from element data: "
                        f"F₀ = {max_pf/1000:.1f} kN"
                    )
                else:
                    messages.append(
                        "ERROR: No preload applied (F_preload = 0). "
                        "Set preload in the Loading panel."
                    )
                    is_valid = False

        # ── 3b. External load check ──────────────────────────────────────
        if self.global_loading is not None:
            gl = self.global_loading
            has_external = (
                gl.F_transverse != 0
                or gl.F_external != 0
                or gl.T_applied != 0
                or gl.F_amplitude != 0
            )
            if not has_external:
                messages.append(
                    "WARNING: No external loads applied. Without external "
                    "loads, the joint cannot lose preload (no loosening mechanism)."
                )

        # ── 4. Matrix assembly ────────────────────────────────────────────
        try:
            M, K, C = self.assemble_matrices()
        except Exception as e:
            messages.append(f"ERROR: Matrix assembly failed - {str(e)}")
            is_valid = False
            return is_valid, messages

        if M.size == 0 or K.size == 0:
            messages.append("ERROR: Assembled matrices are empty")
            is_valid = False
            return is_valid, messages

        n = M.shape[0]

        # ── 5. Mass matrix diagonal checks ────────────────────────────────
        m_diag = np.diag(M)
        if np.any(m_diag < 0):
            neg_idx = np.where(m_diag < 0)[0]
            messages.append(
                f"ERROR: Negative mass at DOF(s) {neg_idx.tolist()}"
            )
            is_valid = False
        if np.any(m_diag == 0):
            zero_idx = np.where(m_diag == 0)[0]
            messages.append(
                f"WARNING: Zero mass at DOF(s) {zero_idx.tolist()} "
                f"- implicit solvers require M to be invertible"
            )

        # ── 6. Mass matrix invertibility ──────────────────────────────────
        # NOTE: For lumped mass matrices, the determinant is the product of
        # all diagonal entries. With many small masses (contacts ~0.001 kg),
        # det(M) can be astronomically small (e.g. 1e-35) even when the
        # matrix IS invertible. Instead, check min diagonal entry directly.
        try:
            min_mass = np.min(m_diag) if len(m_diag) > 0 else 0.0
            if min_mass <= 0:
                zero_idx = np.where(m_diag <= 0)[0]
                active = [e for e in self.elements if e.type != ElementType.GROUND]
                elem_names = [active[i].name if i < len(active) else f"DOF {i}"
                              for i in zero_idx]
                messages.append(
                    f"ERROR: Mass matrix [M] is singular - zero mass at: "
                    f"{', '.join(elem_names)}. "
                    f"Set m > 0 for all elements (use Recalculate All)."
                )
                is_valid = False
            elif min_mass < 1e-6:
                messages.append(
                    f"WARNING: Very small mass detected (min = {min_mass:.2e} kg) "
                    f"- may cause numerical instability"
                )
                messages.append(f"OK: Mass matrix [M] is invertible (min mass = {min_mass:.2e} kg)")
            else:
                messages.append(f"OK: Mass matrix [M] is invertible (min mass = {min_mass:.2e} kg)")
        except Exception:
            messages.append("ERROR: Mass matrix [M] singularity check failed")
            is_valid = False

        # ── 7. Stiffness matrix positive-definiteness ─────────────────────
        # Parallel-group placeholder DOFs have zero diagonal by design
        # (their stiffness is already summed into the group representative).
        # Extract the assembled sub-matrix to avoid false semi-definite warnings.
        try:
            k_diag = np.diag(K)
            assembled_mask = k_diag > 0
            n_placeholder = int(np.sum(~assembled_mask))
            if n_placeholder > 0:
                messages.append(
                    f"OK: {n_placeholder} parallel-group placeholder DOF(s) identified "
                    f"(zero-stiffness rows expected for multi-fillet thread/bearing models)"
                )
                K_sub = K[np.ix_(assembled_mask, assembled_mask)]
            else:
                K_sub = K

            eigvals_K_sub = np.linalg.eigvalsh(K_sub)
            min_eig_K = np.min(eigvals_K_sub)
            max_eig_K = np.max(eigvals_K_sub)
            if np.any(eigvals_K_sub < -1e-10):
                neg_count = int(np.sum(eigvals_K_sub < -1e-10))
                messages.append(
                    f"ERROR: Stiffness matrix [K] has {neg_count} negative "
                    f"eigenvalue(s) (min = {min_eig_K:.2e}) - physically invalid"
                )
                is_valid = False
            elif np.any(eigvals_K_sub < 1e-10):
                messages.append(
                    f"WARNING: Stiffness matrix [K] is semi-definite "
                    f"(min eigenvalue = {min_eig_K:.2e}) - may indicate rigid body mode"
                )
            else:
                messages.append(
                    f"OK: Stiffness matrix [K] is positive definite "
                    f"(eigenvalues: {min_eig_K:.2e} to {max_eig_K:.2e})"
                )
        except np.linalg.LinAlgError:
            messages.append("WARNING: Could not compute eigenvalues of [K]")

        # ── 8. Stiffness matrix invertibility ─────────────────────────────
        # Use min eigenvalue of the assembled sub-matrix (computed above).
        try:
            if min_eig_K > 1e-10:
                cond_K_sub = max_eig_K / min_eig_K
                messages.append(
                    f"OK: Stiffness matrix [K] is invertible "
                    f"(condition number = {cond_K_sub:.2e})"
                )
            else:
                messages.append(
                    f"WARNING: Stiffness matrix [K] may be singular "
                    f"(min eigenvalue = {min_eig_K:.2e}) "
                    f"- static solve K*x = F may fail"
                )
        except Exception:
            messages.append("WARNING: Could not assess [K] invertibility")

        # ── 9. Damping matrix checks ──────────────────────────────────────
        c_diag = np.diag(C)
        if np.any(c_diag < 0):
            neg_idx = np.where(c_diag < 0)[0]
            messages.append(
                f"WARNING: Negative damping at DOF(s) {neg_idx.tolist()}"
            )

        # ── 10. Matrix symmetry checks ────────────────────────────────────
        sym_tol = 1e-10
        for name, mat in [("[M]", M), ("[K]", K), ("[C]", C)]:
            asym = np.max(np.abs(mat - mat.T))
            if asym > sym_tol:
                messages.append(
                    f"WARNING: {name} is not symmetric "
                    f"(max asymmetry = {asym:.2e})"
                )

        # ── 11. Effective stiffness K_eff invertibility (Newmark) ─────────
        # K_eff = K + (γ/βΔt)·C + (1/βΔt²)·M  with β=0.25, γ=0.5
        # Use a representative dt from loading frequency if available
        try:
            freq = 12.5  # default Hz
            if (hasattr(self, 'global_loading') and self.global_loading is not None
                    and hasattr(self.global_loading, 'frequency')
                    and self.global_loading.frequency > 0):
                freq = self.global_loading.frequency
            dt_est = 1.0 / (20.0 * freq)  # ~20 steps per cycle
            beta, gamma = 0.25, 0.5
            a0 = 1.0 / (beta * dt_est**2)
            a1 = gamma / (beta * dt_est)
            K_eff = K + a1 * C + a0 * M
            eigvals_Keff = np.linalg.eigvalsh(K_eff)
            min_eig_Keff = np.min(eigvals_Keff)
            if min_eig_Keff <= 0:
                messages.append(
                    f"ERROR: Effective stiffness K_eff is singular "
                    f"(min eigenvalue = {min_eig_Keff:.2e}, dt = {dt_est:.2e} s) "
                    f"- Newmark time integration will fail"
                )
                is_valid = False
            else:
                cond_Keff = np.max(eigvals_Keff) / min_eig_Keff
                messages.append(
                    f"OK: Effective stiffness K_eff is invertible "
                    f"(cond = {cond_Keff:.2e}, dt = {dt_est:.2e} s)"
                )
        except Exception as e:
            messages.append(f"WARNING: Could not verify K_eff invertibility - {e}")

        # ── 12. Condition number check ────────────────────────────────────
        # Use assembled sub-matrix (K_sub) to avoid cond=inf from placeholder zeros.
        try:
            cond_K = np.linalg.cond(K_sub)
            if cond_K > 1e12:
                messages.append(
                    f"WARNING: Stiffness matrix [K] is ill-conditioned "
                    f"(cond = {cond_K:.2e}) - numerical results may be inaccurate"
                )
            else:
                messages.append(
                    f"OK: Stiffness matrix condition number = {cond_K:.2e}"
                )
        except Exception:
            pass  # Skip if condition number fails (e.g. singular matrix)

        try:
            if np.all(m_diag > 0):
                cond_M = np.linalg.cond(M)
                if cond_M > 1e12:
                    messages.append(
                        f"WARNING: Mass matrix [M] is ill-conditioned "
                        f"(cond = {cond_M:.2e})"
                    )
        except Exception:
            pass

        # ── 13. Parallel group validation ─────────────────────────────────
        parallel_groups = self._identify_parallel_groups()
        for group_id, group in parallel_groups.items():
            if len(group) < 2:
                messages.append(
                    f"WARNING: Parallel group {group_id} has only "
                    f"{len(group)} element"
                )

        return is_valid, messages
    
    # =========================================================================
    # STATISTICS
    # =========================================================================
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get model statistics summary."""
        stats = {
            "name": self.name,
            "n_elements": self.n_elements,
            "n_dof": self.n_dof,
            "bolt_components": len([e for e in self.elements if e.type.is_bolt_component]),
            "member_components": len([e for e in self.elements if e.type.is_member]),
            "total_mass_kg": self.get_total_mass(),
            "k_eq_N_m": self.get_equivalent_stiffness(),
            "c_eq_Ns_m": self.get_equivalent_damping(),
            "f_n_Hz": self.get_fundamental_frequency(),
            "stiffness_ratio": self.get_stiffness_ratio(),
        }

        # Short-key aliases expected by update_summary() in the GUI
        stats["total_mass"] = stats["total_mass_kg"]
        stats["k_eq"]       = stats["k_eq_N_m"]
        stats["c_eq"]       = stats["c_eq_Ns_m"]
        stats["f_n"]        = stats["f_n_Hz"]
        stats["phi"]        = stats["stiffness_ratio"]

        is_valid, messages = self.validate()
        stats["is_valid"] = is_valid
        stats["n_warnings"] = len([m for m in messages if "WARNING" in m])
        stats["n_errors"] = len([m for m in messages if "ERROR" in m])

        return stats
    
    def print_summary(self) -> None:
        """Print model summary to console."""
        stats = self.get_statistics()
        
        print("\n" + "=" * 60)
        print(f"MSD MODEL: {stats['name']}")
        print("=" * 60)
        print(f"  Elements: {stats['n_elements']} ({stats['bolt_components']} bolt, "
              f"{stats['member_components']} member)")
        print(f"  DOF: {stats['n_dof']}")
        print("-" * 60)
        print(f"  Total Mass: {stats['total_mass_kg']:.4f} kg")
        print(f"  Equivalent k: {stats['k_eq_N_m']:.3e} N/m")
        print(f"  Equivalent c: {stats['c_eq_Ns_m']:.1f} N·s/m")
        print(f"  Fundamental f: {stats['f_n_Hz']:.1f} Hz")
        print(f"  Stiffness Ratio Φ: {stats['stiffness_ratio']:.2f}")
        print("-" * 60)
        status = "✓ VALID" if stats['is_valid'] else "✗ INVALID"
        print(f"  Status: {status} ({stats['n_warnings']} warnings, {stats['n_errors']} errors)")
        print("=" * 60)
    
    # =========================================================================
    # SERIALIZATION
    # =========================================================================
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary for JSON serialization."""
        # Serialize contacts -- each subclass has its own to_dict()
        contacts_list = []
        for contact in self.contacts:
            if hasattr(contact, 'to_dict'):
                try:
                    contacts_list.append(contact.to_dict())
                except Exception:
                    pass  # Skip contacts that fail to serialize

        return {
            "version": self.version,
            "name": self.name,
            "description": self.description,
            "created": self.created,
            "modified": self.modified,
            "elements": [e.to_dict() for e in self.elements],
            "contacts": contacts_list,
            "global_loading": self.global_loading.to_dict(),
            # Friction and bolt geometry parameters
            "friction_bolt": {
                "mu_initial": self.mu_initial,
                "lubricated": self.lubricated,
                "bolt_diameter": self.bolt_diameter,
                "pitch": self.pitch,
                "friction_evolution_model": self.friction_evolution_model,
            },
            # Calibrated overrides for TwoStageLooseningParams fields.
            # Written by CalibrationDialog.apply(); consumed in create_analyzer_from_msd_model.
            "two_stage_overrides": dict(getattr(self, '_two_stage_overrides', {}) or {}),
            # Calibrated fixture overrides (k_bolt, k_member, k_transverse_ratio,
            # damping_zeta, mu_thread, mu_bearing). Same persistence path.
            "fixture_overrides": dict(getattr(self, '_fixture_overrides', {}) or {}),
            # Os dois canais do V2, anexados por gui_bridge.build_case_model a
            # partir da configuracao ADOTADA do caso. Ficaram fora daqui ate'
            # 2026-09-02: salvar um caso da validacao devolvia o modelo com os
            # 11 elementos, F0 e mu certos e ZERO constantes adotadas, ou seja
            # parecia correto e nao era. O solver honra os dois
            # (solver_worker.py:1071 e :1092, onde override explicito VENCE),
            # logo a perda mudava resultado.
            "v2_tuner_overrides": dict(getattr(self, '_v2_tuner_overrides', {}) or {}),
            "v2_geometry_overrides": dict(getattr(self, '_v2_geometry_overrides', {}) or {}),
            "analysis": {
                "k_eq": self.get_equivalent_stiffness(),
                "m_total": self.get_total_mass(),
                "c_eq": self.get_equivalent_damping(),
                "f_n": self.get_fundamental_frequency(),
                "phi": self.get_stiffness_ratio()
            }
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MSDModel':
        """Create model from dictionary."""
        model = cls(
            name=data.get("name", "Untitled"),
            description=data.get("description", ""),
            version=data.get("version", "4.0"),
            created=data.get("created", ""),
            modified=data.get("modified", "")
        )

        # Load elements
        for elem_data in data.get("elements", []):
            elem = MSDElementData.from_dict(elem_data)
            model.elements.append(elem)

        # Load contacts (CB2: deserialize contacts from saved data)
        for contact_data in data.get("contacts", []):
            contact = _deserialize_contact(contact_data)
            if contact is None and "specific_type" in contact_data:
                # Fall back: ContactInterface (GUI-layer) saved via ContactInterface.to_dict()
                try:
                    contact = ContactInterface.from_dict(contact_data)
                except Exception:
                    contact = None
            if contact is not None:
                model.contacts.append(contact)

        # Load global loading
        if "global_loading" in data:
            model.global_loading = LoadingData.from_dict(data["global_loading"])

        # Load friction and bolt geometry parameters
        if "friction_bolt" in data:
            fb = data["friction_bolt"]
            model.mu_initial = fb.get("mu_initial", 0.12)
            model.lubricated = fb.get("lubricated", True)
            model.bolt_diameter = fb.get("bolt_diameter", 16.0)
            model.pitch = fb.get("pitch", 2.0)
            model.friction_evolution_model = fb.get("friction_evolution_model", "Three-Phase")

        # Load two-stage calibration overrides (Stage I/II fitted params)
        overrides = data.get("two_stage_overrides")
        if isinstance(overrides, dict) and overrides:
            model._two_stage_overrides = dict(overrides)

        # Load fixture overrides (calibrated k/c/μ — fixture profile)
        fix = data.get("fixture_overrides")
        if isinstance(fix, dict) and fix:
            model._fixture_overrides = dict(fix)

        # Os dois canais do V2 (constantes adotadas do caso e geometria). O
        # `and ov` nao e' redundante: dict vazio tem de deixar o atributo
        # AUSENTE, porque o solver liga o ramo de override pela presenca.
        for chave, attr in (("v2_tuner_overrides", "_v2_tuner_overrides"),
                            ("v2_geometry_overrides", "_v2_geometry_overrides")):
            ov = data.get(chave)
            if isinstance(ov, dict) and ov:
                setattr(model, attr, dict(ov))

        # Auto-compute F_preload from % yield if F_preload is 0
        if model.global_loading.F_preload == 0:
            pct = model.global_loading.preload_percent_yield
            d = model.bolt_diameter
            p = model.pitch
            if pct > 0 and d > 0:
                d2 = d - 0.6495 * p
                d3 = d - 1.2269 * p
                A_s = math.pi / 4 * ((d2 + d3) / 2) ** 2
                Sy = 640.0
                for elem in model.elements:
                    if elem.type.is_bolt_component and elem.material.Sy > 0:
                        Sy = elem.material.Sy
                        break
                model.global_loading.F_preload = (pct / 100.0) * A_s * Sy

        return model
    
    def save(self, filepath: str) -> None:
        """Save model to JSON file (.msd format)."""
        self.modified = datetime.now().isoformat()
        self.filename = filepath
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2)
    
    @classmethod
    def load(cls, filepath: str) -> 'MSDModel':
        """Load model from JSON file."""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        model = cls.from_dict(data)
        model.filename = filepath
        return model
    
    # =========================================================================
    # STATE SPACE REPRESENTATION
    # =========================================================================
    
    def get_state_space_matrices(self) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """
        Get state-space representation of the system.
        
        State vector: z = [x; ẋ]
        State equation: ż = Az + Bu
        Output equation: y = Cz + Du
        
        Returns:
            Tuple (A, B, C, D) state-space matrices
        """
        M, K, C_damp = self.assemble_matrices()
        n = self.n_dof
        
        if n == 0:
            return (np.array([[]]), np.array([[]]), 
                    np.array([[]]), np.array([[]]))
        
        # State matrix A
        M_inv = np.linalg.inv(M) if np.linalg.det(M) != 0 else np.eye(n)
        
        A = np.zeros((2*n, 2*n))
        A[:n, n:] = np.eye(n)           # dx/dt = v
        A[n:, :n] = -M_inv @ K          # dv/dt = M⁻¹(-Kx - Cv + F)
        A[n:, n:] = -M_inv @ C_damp
        
        # Input matrix B (force input to each DOF)
        B = np.zeros((2*n, n))
        B[n:, :] = M_inv
        
        # Output matrix C (output displacements)
        C_out = np.zeros((n, 2*n))
        C_out[:, :n] = np.eye(n)
        
        # Feedthrough matrix D
        D = np.zeros((n, n))
        
        return A, B, C_out, D


# =============================================================================
# PRESET MODELS
# =============================================================================

def create_single_bolt_joint(
    diameter: float = 12.0,
    pitch: float = 1.75,
    grip_length: float = 50.0,
    shank_length: float = 30.0,
    material: MaterialGrade = MaterialGrade.A193_B7,
    preload: float = 0.0,
    percent_yield: float = 70.0,
    name: str = "Single Bolt Joint"
) -> MSDModel:
    """
    Create a standard single bolt joint model.

    Configuration: Ground - Head - Shank - Nut

    Thread engagement is modeled on the NUT element via ThreadFilletModel.

    Args:
        diameter: Nominal bolt diameter (mm)
        pitch: Thread pitch (mm)
        grip_length: Total grip length (mm)
        shank_length: Unthreaded shank length (mm)
        material: Bolt material grade
        preload: Initial preload (N)
        name: Model name

    Returns:
        MSDModel with 4 elements configured
    """
    model = MSDModel(name=name)

    # Ground element
    ground = create_ground(id=1, x=50, y=0)
    model.add_element(ground)

    # Bolt head
    head = create_bolt_head(id=2, diameter=diameter, material=material, x=50, y=50)
    model.add_element(head)

    # Shank
    shank = create_bolt_shank(id=3, diameter=diameter, length=shank_length,
                              material=material, x=50, y=100)
    model.add_element(shank)

    # Nut (thread engagement modeled here via ThreadFilletModel)
    nut = create_nut(id=4, diameter=diameter, pitch=pitch, material=material, x=50, y=150)
    nut.thread_fillet_model = ThreadFilletModel(n_fillets=6, pitch=pitch)
    model.add_element(nut)
    
    # Always compute preload from bolt geometry (70% yield default)
    import math as _math
    d2 = diameter - 0.6495 * pitch
    d1 = diameter - 1.0825 * pitch
    A_s = _math.pi / 4 * ((d2 + d1) / 2) ** 2  # mm²
    Sy = head.material.Sy  # MPa
    computed_preload = (percent_yield / 100.0) * A_s * Sy  # N
    model.global_loading.F_preload = preload if preload > 0 else computed_preload
    model.global_loading.preload_percent_yield = percent_yield

    # Set sensible default loading
    model.global_loading.F_transverse = 10000.0  # N
    model.global_loading.frequency = 12.5  # Hz
    model.global_loading.n_cycles = 2000
    model.bolt_diameter = diameter
    model.pitch = pitch

    return model


def create_flanged_bolt_joint(
    bolt_diameter: float = 12.0,
    pitch: float = 1.75,
    flange_thickness: float = 25.0,
    gasket_thickness: float = 3.0,
    material: MaterialGrade = MaterialGrade.A320_L7,
    n_bolts: int = 1,
    preload: float = 0.0,
    percent_yield: float = 70.0,
    name: str = "Flanged Bolt Joint"
) -> MSDModel:
    """
    Create a flanged bolt joint model with gasket.

    Configuration: Ground - Head - Washer - Flange - Gasket - Flange - Nut

    Thread engagement is modeled on the NUT element via ThreadFilletModel.

    Args:
        bolt_diameter: Nominal bolt diameter (mm)
        pitch: Thread pitch (mm)
        flange_thickness: Each flange thickness (mm)
        gasket_thickness: Gasket thickness (mm)
        material: Bolt material grade
        n_bolts: Number of bolts (for parallel configuration)
        preload: Initial preload per bolt (N)
        name: Model name

    Returns:
        MSDModel with full flanged joint configuration
    """
    model = MSDModel(name=name)

    y_pos = 0
    elem_id = 1

    # Ground
    ground = create_ground(id=elem_id, x=50, y=y_pos)
    model.add_element(ground)
    elem_id += 1
    y_pos += 50

    # Bolt head
    head = create_bolt_head(id=elem_id, diameter=bolt_diameter, material=material,
                            x=50, y=y_pos)
    model.add_element(head)
    elem_id += 1
    y_pos += 40

    # Top washer
    washer_top = create_washer(id=elem_id, bolt_diameter=bolt_diameter,
                               material=material, x=50, y=y_pos)
    model.add_element(washer_top)
    elem_id += 1
    y_pos += 20

    # Top flange
    flange_top = create_flange(id=elem_id, thickness=flange_thickness,
                               bolt_diameter=bolt_diameter, x=50, y=y_pos)
    model.add_element(flange_top)
    elem_id += 1
    y_pos += 40

    # Gasket
    gasket = create_gasket(id=elem_id, inner_diameter=bolt_diameter*4,
                           outer_diameter=bolt_diameter*8, thickness=gasket_thickness,
                           x=50, y=y_pos)
    model.add_element(gasket)
    elem_id += 1
    y_pos += 20

    # Bottom flange
    flange_bot = create_flange(id=elem_id, thickness=flange_thickness,
                               bolt_diameter=bolt_diameter, x=50, y=y_pos)
    model.add_element(flange_bot)
    elem_id += 1
    y_pos += 40

    # Nut (thread engagement modeled here via ThreadFilletModel)
    nut = create_nut(id=elem_id, diameter=bolt_diameter, pitch=pitch,
                     material=material, x=50, y=y_pos)
    nut.thread_fillet_model = ThreadFilletModel(n_fillets=6, pitch=pitch)
    model.add_element(nut)
    
    # Always compute preload from bolt geometry
    import math as _math
    d2 = bolt_diameter - 0.6495 * pitch
    d1 = bolt_diameter - 1.0825 * pitch
    A_s = _math.pi / 4 * ((d2 + d1) / 2) ** 2
    Sy = nut.material.Sy
    computed_preload = (percent_yield / 100.0) * A_s * Sy * n_bolts
    model.global_loading.F_preload = preload * n_bolts if preload > 0 else computed_preload
    model.global_loading.preload_percent_yield = percent_yield

    # Set sensible default loading
    model.global_loading.F_transverse = 10000.0  # N
    model.global_loading.frequency = 12.5  # Hz
    model.global_loading.n_cycles = 2000
    model.bolt_diameter = bolt_diameter
    model.pitch = pitch

    return model


# =============================================================================
# TESTING
# =============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("MSD Model Class - Test Suite")
    print("Bolt Analysis Studio v4.0")
    print("=" * 70)
    
    # Test 1: Create single bolt joint
    print("\n[Test 1] Create Single Bolt Joint")
    model = create_single_bolt_joint(
        diameter=12.0,
        pitch=1.75,
        grip_length=50.0,
        shank_length=30.0,
        preload=50000.0
    )
    model.print_summary()
    
    # Test 2: Matrix assembly
    print("\n[Test 2] Matrix Assembly")
    M, K, C = model.assemble_matrices()
    print(f"  Mass matrix shape: {M.shape}")
    print(f"  Stiffness matrix shape: {K.shape}")
    print(f"  Damping matrix shape: {C.shape}")
    print(f"\n  [M] diagonal:\n  {np.diag(M)}")
    print(f"\n  [K]:\n{K}")
    
    # Test 3: Natural frequencies
    print("\n[Test 3] Natural Frequencies")
    freqs = model.compute_natural_frequencies()
    print(f"  Frequencies (Hz): {freqs}")
    
    # Test 4: Mode shapes
    print("\n[Test 4] Mode Shapes")
    freqs, modes = model.compute_mode_shapes()
    print(f"  Mode 1 ({freqs[0]:.1f} Hz): {modes[:, 0]}")
    if len(freqs) > 1:
        print(f"  Mode 2 ({freqs[1]:.1f} Hz): {modes[:, 1]}")
    
    # Test 5: Flanged joint
    print("\n[Test 5] Flanged Bolt Joint")
    flanged = create_flanged_bolt_joint(
        bolt_diameter=12.0,
        flange_thickness=25.0,
        gasket_thickness=3.0,
        material=MaterialGrade.A320_L7
    )
    flanged.print_summary()
    
    # Test 6: Validation
    print("\n[Test 6] Model Validation")
    is_valid, messages = flanged.validate()
    print(f"  Valid: {is_valid}")
    for msg in messages:
        print(f"    {msg}")
    
    # Test 7: State space
    print("\n[Test 7] State Space Representation")
    A, B, C_out, D = model.get_state_space_matrices()
    print(f"  A matrix shape: {A.shape}")
    print(f"  B matrix shape: {B.shape}")
    print(f"  C matrix shape: {C_out.shape}")
    print(f"  D matrix shape: {D.shape}")
    
    # Test 8: Save/Load
    print("\n[Test 8] Save/Load Model")
    test_file = "/home/claude/bolt_analysis_studio/test_model.msd"
    model.save(test_file)
    print(f"  Saved to: {test_file}")
    
    loaded = MSDModel.load(test_file)
    print(f"  Loaded model: {loaded.name}")
    print(f"  Elements: {loaded.n_elements}")
    print(f"  k_eq matches: {abs(loaded.get_equivalent_stiffness() - model.get_equivalent_stiffness()) < 1.0}")
    
    print("\n" + "=" * 70)
    print("All tests completed successfully!")
    print("=" * 70)
