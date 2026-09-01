"""
MSD Element Data Classes for Bolt Analysis Studio v4.0
BAS +  R&D

This module defines all data structures for Mass-Spring-Damper (MSD) model elements
including bolts, threads, flanges, gaskets, and washers per VDI 2230, ASTM A193/A320,
and API 6A specifications.

Author: Bolt Analysis Studio Team
Version: 4.0
Date: January 2026
"""

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Optional, List, Dict, Any, Tuple
import math
import numpy as np
from datetime import datetime
import json


# =============================================================================
# ENUMERATIONS
# =============================================================================

class ElementType(Enum):
    """MSD element types for bolted joint modeling."""
    # Bolt Components
    HEAD = auto()           # Bolt head with bearing surface
    SHANK = auto()          # Unthreaded portion of bolt
    NUT = auto()            # Nut with thread engagement
    WASHER = auto()         # Flat or spring washer

    # Joint Members
    FLANGE = auto()         # Flange member (clamped)
    GASKET = auto()         # Gasket (compressible)
    MEMBER = auto()         # Generic clamped member

    # Contact Interface Elements
    THREAD = auto()                 # Thread-nut engagement contact
    BEARING_HEAD = auto()           # Bolt head bearing interface
    BEARING_NUT = auto()            # Nut bearing interface
    FLANGE_FLANGE = auto()          # Flange-to-flange contact
    WASHER_CONTACT = auto()         # Washer bearing interface
    GASKET_CONTACT = auto()         # Gasket compression interface
    GENERIC_CONTACT = auto()        # Generic contact interface

    # Beam/Connector Elements
    BEAM_CONNECTOR = auto() # Timoshenko beam connector element

    # Boundary Elements
    GROUND = auto()         # Fixed boundary condition
    THERMAL = auto()        # Thermal expansion element
    
    @property
    def is_bolt_component(self) -> bool:
        """Returns True if element is part of bolt assembly."""
        return self in (ElementType.HEAD, ElementType.SHANK,
                       ElementType.NUT, ElementType.WASHER,
                       ElementType.BEAM_CONNECTOR)

    @property
    def is_member(self) -> bool:
        """Returns True if element is a clamped member."""
        return self in (ElementType.FLANGE, ElementType.GASKET, ElementType.MEMBER)

    @property
    def is_contact_interface(self) -> bool:
        """Returns True if element is a contact interface."""
        return self in (ElementType.THREAD, ElementType.BEARING_HEAD, ElementType.BEARING_NUT,
                       ElementType.FLANGE_FLANGE, ElementType.WASHER_CONTACT,
                       ElementType.GASKET_CONTACT, ElementType.GENERIC_CONTACT)

    @property
    def color_hex(self) -> str:
        """Color for element type from current theme."""
        try:
            from bolt_analysis_studio.gui.theme import Theme
        except ImportError:
            # Fallback if theme not available (e.g. headless)
            return "#cdd6f4"
        colors = {
            # Bolt elements
            ElementType.HEAD: Theme.BLUE,
            ElementType.SHANK: Theme.BLUE,
            ElementType.NUT: Theme.GREEN,
            ElementType.WASHER: Theme.MAUVE,
            # Member elements
            ElementType.FLANGE: Theme.TEAL,
            ElementType.GASKET: Theme.PEACH,
            ElementType.MEMBER: Theme.TEAL,
            # Contact elements
            ElementType.THREAD: Theme.YELLOW,
            ElementType.BEARING_HEAD: Theme.RED,
            ElementType.BEARING_NUT: Theme.RED,
            ElementType.FLANGE_FLANGE: Theme.MAUVE,
            ElementType.WASHER_CONTACT: Theme.MAUVE,
            ElementType.GASKET_CONTACT: Theme.PEACH,
            ElementType.GENERIC_CONTACT: Theme.RED,
            # Beam/Connector elements
            ElementType.BEAM_CONNECTOR: Theme.BLUE,
            # Boundary elements
            ElementType.GROUND: Theme.OVERLAY,
            ElementType.THERMAL: Theme.PINK,
        }
        return colors.get(self, Theme.TEXT)


class ConnectionType(Enum):
    """Connection types for series/parallel element arrangement."""
    SERIES = "series"                   # Sequential connection
    PARALLEL_START = "parallel_start"   # Begin parallel group
    PARALLEL_MEMBER = "parallel_member" # Inside parallel group
    PARALLEL_END = "parallel_end"       # End parallel group


class ThreadStandard(Enum):
    """Thread standards supported."""
    ISO_METRIC = "ISO Metric (M)"
    ISO_METRIC_FINE = "ISO Metric Fine"
    UNC = "Unified National Coarse"
    UNF = "Unified National Fine"
    ACME = "ACME Trapezoidal"
    WHITWORTH = "British Standard Whitworth"


class MaterialGrade(Enum):
    """ASTM material grades for bolted connections."""
    # ASTM A193 (High Temperature)
    A193_B7 = "A193 B7"           # Cr-Mo, up to 450°C
    A193_B7M = "A193 B7M"         # Cr-Mo, enhanced impact
    A193_B16 = "A193 B16"         # Cr-Mo-V, up to 540°C
    A193_B8 = "A193 B8"           # 304 SS
    A193_B8M = "A193 B8M"         # 316 SS
    
    # ASTM A320 (Low Temperature)
    A320_L7 = "A320 L7"           # Cr-Mo, down to -100°C
    A320_L7M = "A320 L7M"         # Cr-Mo, down to -100°C, enhanced impact
    A320_L43 = "A320 L43"         # Ni-Cr-Mo, down to -100°C
    
    # ASTM A354 (Structural)
    A354_BC = "A354 BC"           # Alloy steel, high strength
    A354_BD = "A354 BD"           # Alloy steel, higher strength
    
    # Generic
    STEEL_8_8 = "Steel 8.8"       # ISO grade 8.8
    STEEL_10_9 = "Steel 10.9"     # ISO grade 10.9
    STEEL_12_9 = "Steel 12.9"     # ISO grade 12.9


# =============================================================================
# MATERIAL GRADE → PROPERTIES LOOKUP
# =============================================================================

MATERIAL_GRADE_PROPERTIES: Dict[str, Dict[str, float]] = {
    # ASTM A193 (High Temperature)
    "A193 B7":   {"E": 205000.0, "G": 79000.0, "nu": 0.3, "Sy": 720.0, "Su": 860.0, "Sf": 360.0, "alpha": 11.5e-6, "rho": 7850.0},
    "A193 B7M":  {"E": 205000.0, "G": 79000.0, "nu": 0.3, "Sy": 550.0, "Su": 690.0, "Sf": 280.0, "alpha": 11.5e-6, "rho": 7850.0},
    "A193 B16":  {"E": 210000.0, "G": 81000.0, "nu": 0.3, "Sy": 690.0, "Su": 860.0, "Sf": 340.0, "alpha": 11.5e-6, "rho": 7850.0},
    "A193 B8":   {"E": 193000.0, "G": 77000.0, "nu": 0.3, "Sy": 210.0, "Su": 520.0, "Sf": 200.0, "alpha": 16.0e-6, "rho": 8000.0},
    "A193 B8M":  {"E": 193000.0, "G": 77000.0, "nu": 0.3, "Sy": 210.0, "Su": 520.0, "Sf": 200.0, "alpha": 16.0e-6, "rho": 8000.0},
    # ASTM A320 (Low Temperature)
    "A320 L7":   {"E": 205000.0, "G": 79000.0, "nu": 0.3, "Sy": 720.0, "Su": 860.0, "Sf": 360.0, "alpha": 11.5e-6, "rho": 7850.0},
    "A320 L7M":  {"E": 205000.0, "G": 79000.0, "nu": 0.3, "Sy": 550.0, "Su": 690.0, "Sf": 280.0, "alpha": 11.5e-6, "rho": 7850.0},
    "A320 L43":  {"E": 205000.0, "G": 79000.0, "nu": 0.3, "Sy": 860.0, "Su": 1000.0, "Sf": 430.0, "alpha": 11.0e-6, "rho": 7850.0},
    # ASTM A354 (Structural)
    "A354 BC":   {"E": 205000.0, "G": 79000.0, "nu": 0.3, "Sy": 630.0, "Su": 825.0, "Sf": 320.0, "alpha": 11.5e-6, "rho": 7850.0},
    "A354 BD":   {"E": 205000.0, "G": 79000.0, "nu": 0.3, "Sy": 900.0, "Su": 1035.0, "Sf": 450.0, "alpha": 11.5e-6, "rho": 7850.0},
    # ISO grades
    "Steel 8.8":  {"E": 205000.0, "G": 79000.0, "nu": 0.3, "Sy": 640.0, "Su": 800.0, "Sf": 320.0, "alpha": 11.5e-6, "rho": 7850.0},
    "Steel 10.9": {"E": 205000.0, "G": 79000.0, "nu": 0.3, "Sy": 900.0, "Su": 1040.0, "Sf": 450.0, "alpha": 11.5e-6, "rho": 7850.0},
    "Steel 12.9": {"E": 205000.0, "G": 79000.0, "nu": 0.3, "Sy": 1080.0, "Su": 1220.0, "Sf": 540.0, "alpha": 11.5e-6, "rho": 7850.0},
}


def material_data_from_grade(grade: 'MaterialGrade') -> 'MaterialData':
    """
    Create a MaterialData instance with properties populated from MaterialGrade.

    This resolves the issue where MaterialGrade was an enum label only, with no
    actual E, Sy, Su values populated from the grade.
    """
    grade_value = grade.value if isinstance(grade, MaterialGrade) else str(grade)
    props = MATERIAL_GRADE_PROPERTIES.get(grade_value, MATERIAL_GRADE_PROPERTIES["A193 B7"])
    return MaterialData(
        name=grade_value,
        grade=grade,
        E=props["E"],
        G=props["G"],
        nu=props["nu"],
        Sy=props["Sy"],
        Su=props["Su"],
        Sf=props["Sf"],
        alpha=props["alpha"],
        rho=props["rho"],
    )


class FrictionModel(Enum):
    """Friction models for thread/bearing interfaces."""
    COULOMB = "Coulomb"                   # μ·N
    COULOMB_REGULARIZED = "Regularized"   # μ·N·tanh(v/v_reg)
    LUGRE = "LuGre"                        # Dynamic with bristle state
    DAHL = "Dahl"                          # Hysteresis without Stribeck
    IWAN = "Iwan"                          # Distributed Jenkins elements


class LoadingType(Enum):
    """Types of cyclic loading."""
    AXIAL = "Axial"
    TRANSVERSE = "Transverse"
    COMBINED = "Combined"
    TORSIONAL = "Torsional"
    BENDING = "Bending"


class ContactType(Enum):
    """Contact interface types between elements."""
    RIGID = "rigid"              # Infinite stiffness (welded/bonded)
    ELASTIC = "elastic"          # Linear spring contact
    FRICTIONAL = "frictional"    # Coulomb friction capable
    NONLINEAR = "nonlinear"      # Hertzian or power-law contact


class SpecificContactType(Enum):
    """
    Element-pair-specific contact types based on physical interface.

    These define the specific mechanical interface between two components
    in a bolted joint, each with distinct tribological properties.
    """
    # Thread contacts (stud-nut engagement)
    THREAD_CONTACT = "thread_contact"          # Stud threads engaging nut

    # Bolt head contacts
    BOLT_HEAD_WASHER = "bolt_head_washer"      # Bolt head bearing on washer
    BOLT_HEAD_FLANGE = "bolt_head_flange"      # Bolt head bearing on flange (no washer)

    # Nut contacts
    NUT_WASHER = "nut_washer"                  # Nut bearing on washer
    NUT_FLANGE = "nut_flange"                  # Nut bearing on flange (no washer)

    # Washer contacts
    WASHER_FLANGE = "washer_flange"            # Washer bearing on flange
    WASHER_WASHER = "washer_washer"            # Stacked washers (lock washers)

    # Flange/member contacts
    FLANGE_FLANGE = "flange_flange"            # Flange-to-flange (metal-to-metal)
    FLANGE_GASKET = "flange_gasket"            # Flange bearing on gasket
    FLANGE_MEMBER = "flange_member"            # Generic member contact

    # Generic
    GENERIC_CONTACT = "generic"                # User-defined contact

    @classmethod
    def from_element_pair(cls, type_a: 'ElementType', type_b: 'ElementType') -> 'SpecificContactType':
        """Determine appropriate contact type from element pair."""
        pair = frozenset([type_a.name, type_b.name])

        mapping = {
            frozenset(["SHANK", "NUT"]): cls.THREAD_CONTACT,
            frozenset(["THREAD", "NUT"]): cls.THREAD_CONTACT,
            frozenset(["HEAD", "WASHER"]): cls.BOLT_HEAD_WASHER,
            frozenset(["HEAD", "FLANGE"]): cls.BOLT_HEAD_FLANGE,
            frozenset(["NUT", "WASHER"]): cls.NUT_WASHER,
            frozenset(["NUT", "FLANGE"]): cls.NUT_FLANGE,
            frozenset(["WASHER", "FLANGE"]): cls.WASHER_FLANGE,
            frozenset(["WASHER", "WASHER"]): cls.WASHER_WASHER,
            frozenset(["FLANGE", "FLANGE"]): cls.FLANGE_FLANGE,
            frozenset(["FLANGE", "GASKET"]): cls.FLANGE_GASKET,
            frozenset(["FLANGE", "MEMBER"]): cls.FLANGE_MEMBER,
            frozenset(["GASKET", "FLANGE"]): cls.FLANGE_GASKET,
        }

        return mapping.get(pair, cls.GENERIC_CONTACT)

    @property
    def default_friction_static(self) -> float:
        """Default static friction coefficient for this contact type."""
        defaults = {
            SpecificContactType.THREAD_CONTACT: 0.14,       # Lubricated threads
            SpecificContactType.BOLT_HEAD_WASHER: 0.12,     # Bearing surface
            SpecificContactType.BOLT_HEAD_FLANGE: 0.15,     # Steel-steel
            SpecificContactType.NUT_WASHER: 0.12,           # Bearing surface
            SpecificContactType.NUT_FLANGE: 0.15,           # Steel-steel
            SpecificContactType.WASHER_FLANGE: 0.15,        # Steel-steel
            SpecificContactType.WASHER_WASHER: 0.20,        # Steel-steel dry
            SpecificContactType.FLANGE_FLANGE: 0.15,        # Metal-to-metal seal
            SpecificContactType.FLANGE_GASKET: 0.25,        # Soft gasket
            SpecificContactType.FLANGE_MEMBER: 0.15,        # Generic
            SpecificContactType.GENERIC_CONTACT: 0.15,
        }
        return defaults.get(self, 0.15)

    @property
    def requires_thread_model(self) -> bool:
        """Returns True if this contact type needs thread fillet modeling."""
        return self == SpecificContactType.THREAD_CONTACT


class TimeVariation(Enum):
    """Time variation for loads."""
    STATIC = "static"
    HARMONIC = "harmonic"
    TRANSIENT = "transient"


class ConstraintType(Enum):
    """Boundary constraint types."""
    FIXED = "fixed"              # u = 0
    PRESCRIBED = "prescribed"    # u = u_0
    SPRING = "spring"            # k_ground spring to ground


# =============================================================================
# GRID POSITION FOR V2.0 LAYOUT
# =============================================================================

@dataclass
class GridPosition:
    """
    Position on the schematic grid for v2.0 layout.

    Row (Y-axis): Series position in load path
    Column (X-axis): Parallel branch position

    Elements in same row are PARALLEL (load splits)
    Elements in different rows are SERIES (load flows through)
    """
    row: int = 0      # Y-axis: series position (0 = top/input)
    column: int = 0   # X-axis: parallel branch (0 = main path)

    def to_dict(self) -> Dict[str, int]:
        return {"row": self.row, "column": self.column}

    @classmethod
    def from_dict(cls, data: Dict[str, int]) -> 'GridPosition':
        return cls(row=data.get("row", 0), column=data.get("column", 0))


# =============================================================================
# CONTACT INTERFACE FOR V2.0
# =============================================================================

@dataclass
class ContactInterface:
    """
    Defines contact interface between two elements.

    Used to model the mechanical connection/interface between
    adjacent elements with specific contact properties.

    The specific_type field determines the physical interface type
    (e.g., THREAD_CONTACT, BOLT_HEAD_WASHER, etc.) which affects
    default friction coefficients and tribological properties.
    """
    element_a_id: int = 0
    element_b_id: int = 0
    contact_type: ContactType = ContactType.ELASTIC
    specific_type: SpecificContactType = SpecificContactType.GENERIC_CONTACT

    # Contact stiffness
    k_normal: float = 1e10       # Normal stiffness (N/m)
    k_tangential: float = 5e9    # Tangential stiffness (N/m)

    # Damping
    c_normal: float = 100.0      # Normal damping (N·s/m)
    c_tangential: float = 50.0   # Tangential damping (N·s/m)

    # Friction (for frictional contact)
    mu_static: float = 0.15      # Static friction coefficient
    mu_kinetic: float = 0.12     # Kinetic friction coefficient

    # Nonlinear parameters (for Hertzian contact)
    hertz_exponent: float = 1.5  # k ∝ δ^n (n=1.5 for sphere)
    k_reference: float = 1e10    # Reference stiffness at δ_ref
    delta_reference: float = 1e-5  # Reference deformation (m)

    # Load transfer
    transfer_efficiency: float = 1.0  # 0.0 to 1.0 (losses)

    # Thread fillet model (only for THREAD_CONTACT)
    thread_model: Optional['ThreadFilletModel'] = None

    # Visual
    name: str = ""

    def __post_init__(self):
        if not self.name:
            type_name = self.specific_type.value.replace("_", " ").title()
            self.name = f"{type_name} {self.element_a_id}-{self.element_b_id}"
        # Initialize thread model for thread contacts
        if self.specific_type == SpecificContactType.THREAD_CONTACT and self.thread_model is None:
            self.thread_model = ThreadFilletModel()

    def get_contact_force(self, delta: float, velocity: float = 0.0) -> float:
        """Calculate contact force given penetration and velocity."""
        if delta <= 0:
            return 0.0

        if self.contact_type == ContactType.RIGID:
            return 1e15 * delta  # Very high stiffness

        elif self.contact_type == ContactType.ELASTIC:
            return self.k_normal * delta + self.c_normal * velocity

        elif self.contact_type == ContactType.NONLINEAR:
            # Hertzian: F = k_ref * (δ/δ_ref)^n
            F_elastic = self.k_reference * (delta / self.delta_reference) ** self.hertz_exponent
            return F_elastic + self.c_normal * velocity

        else:  # FRICTIONAL - normal component only here
            return self.k_normal * delta + self.c_normal * velocity

    def to_dict(self) -> Dict[str, Any]:
        result = {
            "element_a_id": self.element_a_id,
            "element_b_id": self.element_b_id,
            "contact_type": self.contact_type.value,
            "specific_type": self.specific_type.value,
            "k_normal": self.k_normal,
            "k_tangential": self.k_tangential,
            "c_normal": self.c_normal,
            "c_tangential": self.c_tangential,
            "mu_static": self.mu_static,
            "mu_kinetic": self.mu_kinetic,
            "hertz_exponent": self.hertz_exponent,
            "transfer_efficiency": self.transfer_efficiency,
            "name": self.name
        }
        if self.thread_model is not None:
            result["thread_model"] = self.thread_model.to_dict()
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ContactInterface':
        data = data.copy()  # Don't modify original
        if 'contact_type' in data and isinstance(data['contact_type'], str):
            for ct in ContactType:
                if ct.value == data['contact_type']:
                    data['contact_type'] = ct
                    break
        if 'specific_type' in data and isinstance(data['specific_type'], str):
            for st in SpecificContactType:
                if st.value == data['specific_type']:
                    data['specific_type'] = st
                    break
        if 'thread_model' in data and isinstance(data['thread_model'], dict):
            data['thread_model'] = ThreadFilletModel.from_dict(data['thread_model'])
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


# =============================================================================
# THREAD FILLET MODEL FOR V2.0
# =============================================================================

@dataclass
class ThreadFilletModel:
    """
    Parallel fillet model for threaded elements.

    Models thread engagement as N parallel spring elements with
    configurable load distribution. First threads (at bearing face)
    typically carry more load.

    Supported distributions:
    - uniform: Equal load on all threads (idealized)
    - linear: Linearly decreasing load
    - power_law: (n-i+1)^β distribution
    - exponential: Sopwith e^(-λi) decay (most common)
    - yamamoto: sinh-based, matches experiments

    References:
    - Sopwith (1948): Exponential decay model
    - Yamamoto (1980): Research-based distribution
    - VDI 2230: Design guidelines
    """
    n_fillets: int = 6           # Number of engaged thread fillets
    pitch: float = 1.75          # Thread pitch (mm)
    decay_constant: float = 0.38  # λ for exponential (typical 0.2-0.5)

    # Distribution model
    distribution: str = "exponential"  # "uniform", "linear", "power_law", "exponential", "yamamoto"
    power_exponent: float = 2.0  # β for power_law distribution
    yamamoto_gamma: float = 0.5  # γ for Yamamoto distribution

    # Connection type for fillets
    connection: str = "parallel"  # "parallel" or "series"

    def get_load_factors(self) -> np.ndarray:
        """
        Get normalized load factors for each fillet.
        Sum of factors = 1.0
        Thread 1 is at the bearing face (typically highest load).
        """
        n = self.n_fillets

        if self.distribution == "uniform":
            # Equal distribution: φ_i = 1/n
            return np.ones(n) / n

        elif self.distribution == "linear":
            # Linear: φ_i = 2(n-i+1) / n(n+1)
            factors = np.array([2 * (n - i) / (n * (n + 1)) for i in range(n)])
            return factors

        elif self.distribution == "exponential":
            # Sopwith exponential decay: φ_i = e^(-λi) / Σe^(-λj)
            factors = np.array([np.exp(-self.decay_constant * i) for i in range(n)])
            return factors / np.sum(factors)

        elif self.distribution == "power_law":
            # Power law: φ_i = (n-i+1)^β / Σj^β
            factors = np.array([(n - i) ** self.power_exponent for i in range(n)])
            if np.sum(factors) > 0:
                return factors / np.sum(factors)
            return np.ones(n) / n

        elif self.distribution == "yamamoto":
            # Yamamoto: φ_i = sinh(γ(n-i+0.5)) / Σsinh(γ(n-j+0.5))
            factors = np.array([np.sinh(self.yamamoto_gamma * (n - i + 0.5)) for i in range(n)])
            if np.sum(factors) > 0:
                return factors / np.sum(factors)
            return np.ones(n) / n

        else:
            return np.ones(n) / n

    def get_fillet_stiffnesses(self, k_total: float) -> np.ndarray:
        """
        Calculate individual fillet stiffnesses.

        For parallel connection: k_total = Σk_i, so k_i = factor_i × k_total
        For series connection: 1/k_total = Σ(1/k_i)
        """
        factors = self.get_load_factors()

        if self.connection == "parallel":
            # Each fillet stiffness proportional to load factor
            return factors * k_total
        else:
            # Series: more complex - equal compliance per unit load
            return k_total * self.n_fillets * factors

    def get_load_distribution(self, F_total: float) -> np.ndarray:
        """Calculate load on each fillet."""
        return self.get_load_factors() * F_total

    def get_first_fillet_stress_factor(self) -> float:
        """
        Get stress concentration factor for first fillet.
        Ratio of first fillet load to uniform load.
        """
        factors = self.get_load_factors()
        uniform_factor = 1.0 / self.n_fillets
        return factors[0] / uniform_factor

    def to_dict(self) -> Dict[str, Any]:
        return {
            "n_fillets": self.n_fillets,
            "pitch": self.pitch,
            "decay_constant": self.decay_constant,
            "distribution": self.distribution,
            "power_exponent": self.power_exponent,
            "yamamoto_gamma": self.yamamoto_gamma,
            "connection": self.connection
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ThreadFilletModel':
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


# =============================================================================
# APPLIED LOAD FOR V2.0
# =============================================================================

@dataclass
class AppliedLoad:
    """
    Load applied to an element in the model.

    Supports static, harmonic, and transient loading.
    """
    element_id: int = 0
    load_type: str = "force"     # "preload", "force", "displacement", "moment"

    # Magnitude and direction
    magnitude: float = 0.0       # N, m, or N·m depending on type
    direction: str = "axial"     # "axial", "transverse", "x", "y", "z"

    # Time variation
    time_variation: TimeVariation = TimeVariation.STATIC

    # Harmonic parameters
    frequency: float = 0.0       # Hz
    phase: float = 0.0           # radians

    # Transient - time history (t, value) pairs
    time_history: Optional[List[Tuple[float, float]]] = None

    # Load point location (0 = element start, 1 = element end)
    location: float = 0.5

    # Name/label
    name: str = ""

    def __post_init__(self):
        if not self.name:
            self.name = f"{self.load_type.title()} on #{self.element_id}"

    def get_value_at_time(self, t: float) -> float:
        """Get load value at time t."""
        if self.time_variation == TimeVariation.STATIC:
            return self.magnitude

        elif self.time_variation == TimeVariation.HARMONIC:
            omega = 2 * np.pi * self.frequency
            return self.magnitude * np.sin(omega * t + self.phase)

        elif self.time_variation == TimeVariation.TRANSIENT:
            if self.time_history is None or len(self.time_history) == 0:
                return self.magnitude
            # Linear interpolation
            times = [p[0] for p in self.time_history]
            values = [p[1] for p in self.time_history]
            return float(np.interp(t, times, values))

        return self.magnitude

    def to_dict(self) -> Dict[str, Any]:
        return {
            "element_id": self.element_id,
            "load_type": self.load_type,
            "magnitude": self.magnitude,
            "direction": self.direction,
            "time_variation": self.time_variation.value,
            "frequency": self.frequency,
            "phase": self.phase,
            "time_history": self.time_history,
            "location": self.location,
            "name": self.name
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AppliedLoad':
        if 'time_variation' in data and isinstance(data['time_variation'], str):
            for tv in TimeVariation:
                if tv.value == data['time_variation']:
                    data['time_variation'] = tv
                    break
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


# =============================================================================
# CONSTRAINT FOR V2.0
# =============================================================================

@dataclass
class Constraint:
    """
    Boundary constraint on an element.
    """
    element_id: int = 0
    constraint_type: ConstraintType = ConstraintType.FIXED

    # Constrained DOFs (0=x, 1=y, 2=z, 3=rx, 4=ry, 5=rz)
    dof: List[int] = field(default_factory=lambda: [0])

    # Value (for prescribed displacement or spring stiffness)
    value: float = 0.0

    # Time variation for prescribed displacement
    time_variation: TimeVariation = TimeVariation.STATIC
    frequency: float = 0.0
    phase: float = 0.0

    # Name/label
    name: str = ""

    def __post_init__(self):
        if not self.name:
            type_str = self.constraint_type.value.title()
            self.name = f"{type_str} BC on #{self.element_id}"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "element_id": self.element_id,
            "constraint_type": self.constraint_type.value,
            "dof": self.dof,
            "value": self.value,
            "time_variation": self.time_variation.value,
            "frequency": self.frequency,
            "phase": self.phase,
            "name": self.name
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Constraint':
        if 'constraint_type' in data and isinstance(data['constraint_type'], str):
            for ct in ConstraintType:
                if ct.value == data['constraint_type']:
                    data['constraint_type'] = ct
                    break
        if 'time_variation' in data and isinstance(data['time_variation'], str):
            for tv in TimeVariation:
                if tv.value == data['time_variation']:
                    data['time_variation'] = tv
                    break
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


# =============================================================================
# DATA CLASSES - GEOMETRY
# =============================================================================

@dataclass
class GeometryData:
    """Geometric parameters for MSD element."""
    # Primary dimensions (mm)
    diameter: float = 12.0          # Nominal diameter
    length: float = 25.0            # Element length
    thickness: float = 0.0          # For plates/flanges
    
    # Thread geometry
    pitch: float = 1.75             # Thread pitch (mm)
    thread_angle: float = 60.0      # Thread flank angle (degrees)
    helix_angle: float = 2.87       # Thread helix angle (degrees)
    
    # Derived thread dimensions (ISO 68-1)
    d2: Optional[float] = None      # Pitch diameter
    d1: Optional[float] = None      # Basic minor diameter (internal thread, for At)
    d3: Optional[float] = None      # Minor diameter (bolt root)
    At: Optional[float] = None      # Tensile stress area (mm²)
    As: Optional[float] = None      # Shear stress area (mm²)
    
    # Head/Nut dimensions
    head_diameter: float = 0.0      # Across flats (mm)
    head_height: float = 0.0        # Head height (mm)
    bearing_diameter: float = 0.0   # Bearing surface outer dia
    hole_diameter: float = 0.0      # Clearance hole diameter
    
    # Frustum cone parameters (clamped members)
    frustum_angle: float = 30.0     # Half-angle (degrees)
    frustum_depth: float = 0.0      # Equivalent depth
    
    def __post_init__(self):
        """Calculate derived dimensions if not provided."""
        if self.pitch > 0:
            # ISO 68-1 metric thread geometry
            H = 0.5 * math.sqrt(3) * self.pitch  # Fundamental triangle height

            if self.d2 is None:
                self.d2 = self.diameter - 0.6495 * self.pitch  # Pitch diameter

            if self.d1 is None:
                self.d1 = self.diameter - 1.0825 * self.pitch  # Basic minor diameter (internal thread)

            if self.d3 is None:
                self.d3 = self.diameter - 1.2268 * self.pitch  # Minor diameter (bolt root)

            if self.At is None:
                # Tensile stress area per ISO 898-1: uses d2 and d1 (NOT d3)
                d_eq = (self.d2 + self.d1) / 2
                self.At = math.pi / 4 * d_eq**2

            if self.As is None:
                # Shear area at minor diameter
                self.As = math.pi * self.d3 * self.length / self.pitch * 0.5
    
    def get_cross_section_area(self) -> float:
        """Returns cross-sectional area based on element type."""
        if self.At is not None and self.At > 0:
            return self.At
        return math.pi / 4 * self.diameter**2
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "diameter": self.diameter,
            "length": self.length,
            "thickness": self.thickness,
            "pitch": self.pitch,
            "thread_angle": self.thread_angle,
            "helix_angle": self.helix_angle,
            "d2": self.d2,
            "d1": self.d1,
            "d3": self.d3,
            "At": self.At,
            "As": self.As,
            "head_diameter": self.head_diameter,
            "head_height": self.head_height,
            "bearing_diameter": self.bearing_diameter,
            "hole_diameter": self.hole_diameter,
            "frustum_angle": self.frustum_angle,
            "frustum_depth": self.frustum_depth
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GeometryData':
        """Create from dictionary."""
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


@dataclass  
class MaterialData:
    """Material properties for MSD element."""
    # Identification
    name: str = "ASTM A193 B7"
    grade: MaterialGrade = MaterialGrade.A193_B7
    
    # Elastic properties (MPa)
    E: float = 205000.0             # Young's modulus
    G: float = 79000.0              # Shear modulus
    nu: float = 0.3                 # Poisson's ratio
    
    # Strength (MPa)
    Sy: float = 720.0               # Yield strength (0.2% offset)
    Su: float = 860.0               # Ultimate tensile strength
    Sf: float = 360.0               # Fatigue limit (1e7 cycles)
    
    # Thermal
    alpha: float = 11.5e-6          # Thermal expansion (1/K)
    T_ref: float = 20.0             # Reference temperature (°C)
    
    # Density (kg/m³)
    rho: float = 7850.0
    
    # Temperature dependent factors
    E_T: Optional[Dict[float, float]] = None    # E(T) lookup
    Sy_T: Optional[Dict[float, float]] = None   # Sy(T) lookup
    
    # NACE MR0175 compliance
    nace_compliant: bool = True
    max_hardness_hrc: float = 22.0  # HRC max for sour service
    
    def get_E_at_temperature(self, T: float) -> float:
        """Returns modulus at temperature T (°C)."""
        if self.E_T is not None:
            # Linear interpolation
            temps = sorted(self.E_T.keys())
            if T <= temps[0]:
                return self.E_T[temps[0]]
            if T >= temps[-1]:
                return self.E_T[temps[-1]]
            for i in range(len(temps) - 1):
                if temps[i] <= T <= temps[i + 1]:
                    t0, t1 = temps[i], temps[i + 1]
                    return self.E_T[t0] + (self.E_T[t1] - self.E_T[t0]) * (T - t0) / (t1 - t0)
        # Default reduction factor for steel
        if T <= 100:
            return self.E
        elif T <= 300:
            return self.E * (1 - 0.0003 * (T - 100))
        else:
            return self.E * (1 - 0.0006 * (T - 100))
    
    def get_Sy_at_temperature(self, T: float) -> float:
        """Returns yield strength at temperature T (°C)."""
        if self.Sy_T is not None:
            temps = sorted(self.Sy_T.keys())
            if T <= temps[0]:
                return self.Sy_T[temps[0]]
            if T >= temps[-1]:
                return self.Sy_T[temps[-1]]
            for i in range(len(temps) - 1):
                if temps[i] <= T <= temps[i + 1]:
                    t0, t1 = temps[i], temps[i + 1]
                    return self.Sy_T[t0] + (self.Sy_T[t1] - self.Sy_T[t0]) * (T - t0) / (t1 - t0)
        # Default reduction (ASME B31.3 style)
        if T <= 100:
            return self.Sy
        elif T <= 400:
            return self.Sy * (1 - 0.001 * (T - 100))
        else:
            return self.Sy * (1 - 0.002 * (T - 100))
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "name": self.name,
            "grade": self.grade.value if isinstance(self.grade, MaterialGrade) else self.grade,
            "E": self.E,
            "G": self.G,
            "nu": self.nu,
            "Sy": self.Sy,
            "Su": self.Su,
            "Sf": self.Sf,
            "alpha": self.alpha,
            "T_ref": self.T_ref,
            "rho": self.rho,
            "nace_compliant": self.nace_compliant,
            "max_hardness_hrc": self.max_hardness_hrc
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MaterialData':
        """Create from dictionary."""
        if 'grade' in data and isinstance(data['grade'], str):
            for g in MaterialGrade:
                if g.value == data['grade']:
                    data['grade'] = g
                    break
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


# =============================================================================
# DATA CLASSES - FRICTION
# =============================================================================

@dataclass
class FrictionData:
    """Friction parameters for thread and bearing surfaces."""
    # Friction model type
    model: FrictionModel = FrictionModel.COULOMB_REGULARIZED
    
    # Coulomb friction coefficients
    mu_thread: float = 0.12         # Thread friction coefficient
    mu_bearing: float = 0.14        # Bearing/nut face friction
    mu_static: float = 0.15         # Static friction (μ_s)
    mu_kinetic: float = 0.10        # Kinetic friction (μ_k)
    
    # LuGre model parameters
    sigma_0: float = 1e5            # Contact stiffness (N/m)
    sigma_1: float = 1e3            # Micro-damping (N·s/m)
    sigma_2: float = 0.0            # Viscous friction (N·s/m)
    v_s: float = 0.001              # Stribeck velocity (m/s)
    alpha_stribeck: float = 2.0     # Stribeck exponent
    
    # Regularization
    v_reg: float = 1e-5             # Regularization velocity (m/s)
    
    # Friction evolution parameters (Hintikka model)
    mu_initial: float = 0.12        # Initial coefficient
    mu_peak: float = 0.18           # Peak during running-in
    mu_steady: float = 0.14         # Steady-state value
    N1: float = 50.0                # Rise cycles
    N2: float = 5000.0              # Decay cycles
    N3: float = 50000.0             # Stabilization cycles
    
    # Surface treatment effects
    surface_treatment: str = "bare_steel"
    treatment_factor: float = 1.0   # Multiplier for μ
    
    def get_stribeck_function(self, v: float) -> float:
        """Stribeck friction curve g(v)."""
        return self.mu_kinetic + (self.mu_static - self.mu_kinetic) * \
               math.exp(-(abs(v) / self.v_s)**self.alpha_stribeck)
    
    def get_friction_force_coulomb(self, F_n: float, v: float) -> float:
        """Regularized Coulomb friction force."""
        mu = (self.mu_thread + self.mu_bearing) / 2
        return mu * F_n * math.tanh(v / self.v_reg)
    
    def get_friction_evolution(self, N: np.ndarray) -> np.ndarray:
        """
        Three-phase friction evolution model (Hintikka et al. 2020).
        Returns μ(N) array.
        """
        # Phase 1: Rise to peak
        rise = (self.mu_peak - self.mu_initial) * (1 - np.exp(-N / self.N1))
        # Phase 2: Decay from peak
        decay = rise * np.exp(-N / self.N2)
        # Phase 3: Stabilization to steady-state
        steady = (self.mu_steady - self.mu_initial) * (1 - np.exp(-N / self.N3))
        
        return self.mu_initial + decay + steady
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "model": self.model.value if isinstance(self.model, FrictionModel) else self.model,
            "mu_thread": self.mu_thread,
            "mu_bearing": self.mu_bearing,
            "mu_static": self.mu_static,
            "mu_kinetic": self.mu_kinetic,
            "sigma_0": self.sigma_0,
            "sigma_1": self.sigma_1,
            "sigma_2": self.sigma_2,
            "v_s": self.v_s,
            "alpha_stribeck": self.alpha_stribeck,
            "v_reg": self.v_reg,
            "surface_treatment": self.surface_treatment,
            "treatment_factor": self.treatment_factor
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FrictionData':
        """Create from dictionary."""
        if 'model' in data and isinstance(data['model'], str):
            for m in FrictionModel:
                if m.value == data['model']:
                    data['model'] = m
                    break
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


# =============================================================================
# DATA CLASSES - LOADING
# =============================================================================

@dataclass
class LoadingData:
    """Loading parameters for MSD element."""
    # Loading type
    type: LoadingType = LoadingType.AXIAL
    
    # Preload
    F_preload: float = 50000.0       # Initial preload (N) — default 50 kN
    preload_percent_yield: float = 70.0  # % of yield utilization
    
    # Cyclic loading
    F_amplitude: float = 5000.0     # Force amplitude (N)
    frequency: float = 25.0         # Frequency (Hz)
    n_cycles: int = 100000          # Total cycles (auto-calculated: freq × integration_time)
    integration_time: float = 160.0 # Integration time (s) — primary user input
    
    # Displacement-based loading
    delta_amplitude: float = 0.5    # Displacement amplitude (mm)
    
    # Transverse loading
    F_transverse: float = 0.0       # Transverse force (N)
    
    # Torsional loading
    T_applied: float = 0.0          # Applied torque (N·m)
    
    # External axial force
    F_external: float = 0.0         # External tension/compression (N)
    
    # Thermal loading
    delta_T: float = 0.0            # Temperature change (°C)
    
    # Phase angles for combined loading
    phase_axial: float = 0.0        # Phase angle (degrees)
    phase_transverse: float = 90.0  # Phase angle (degrees)

    # VDI 2230 / Phase-A load factor fields
    R_factor: float = 0.0                # Stress ratio R = F_min / F_max (−1 fully reversed)
    Phi_load: Optional[float] = None     # Force-introduction factor Φ (None = auto from geometry)
    n_load_plane: float = 0.5            # Load-plane factor n ∈ [0, 1] (0=bolt head, 1=mid-plane)
    dynamic_factor: float = 1.0          # Dynamic amplification φ (>1 for vibration/impact)
    load_waveform: str = "sinusoidal"    # Waveform shape: "sinusoidal" | "square" | "sawtooth"

    # Phase F / Locking device fields
    slip_onset_factor: float = 0.46      # Pai-Hess slip onset override (device-specific)
    locking_device_type: int = 0         # Index into locking_devices.json (0 = free_running_nut)
    friction_mu_increase: float = 0.0    # Additive μ from locking device

    # Control mode — which quantity drives the cyclic transverse load:
    #   "displacement" → impose δ (delta_amplitude); transverse force is derived
    #                    from δ × local stiffness (Junker / crank-driven rigs).
    #   "force"        → impose the transverse force directly (servo-hydraulic).
    # Maps to the V2 engine's disp- vs force-controlled step_cycle modes.
    control_mode: str = "displacement"   # "displacement" | "force"

    def get_loading_ratio(self) -> float:
        """Returns R ratio (F_min/F_max) for fatigue analysis."""
        if self.F_amplitude == 0:
            return 1.0
        F_max = self.F_preload + self.F_amplitude
        F_min = self.F_preload - self.F_amplitude
        return F_min / F_max if F_max != 0 else 0.0
    
    def get_stress_amplitude(self, area: float) -> float:
        """Returns stress amplitude (MPa)."""
        if area == 0:
            return 0.0
        return self.F_amplitude / area
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "type": self.type.value if isinstance(self.type, LoadingType) else self.type,
            "F_preload": self.F_preload,
            "preload_percent_yield": self.preload_percent_yield,
            "F_amplitude": self.F_amplitude,
            "frequency": self.frequency,
            "n_cycles": self.n_cycles,
            "integration_time": self.integration_time,
            "delta_amplitude": self.delta_amplitude,
            "F_transverse": self.F_transverse,
            "T_applied": self.T_applied,
            "F_external": self.F_external,
            "delta_T": self.delta_T,
            "phase_axial": self.phase_axial,
            "phase_transverse": self.phase_transverse,
            "R_factor": self.R_factor,
            "Phi_load": self.Phi_load,
            "n_load_plane": self.n_load_plane,
            "dynamic_factor": self.dynamic_factor,
            "load_waveform": self.load_waveform,
            "slip_onset_factor": self.slip_onset_factor,
            "locking_device_type": self.locking_device_type,
            "friction_mu_increase": self.friction_mu_increase,
            "control_mode": self.control_mode,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LoadingData':
        """Create from dictionary."""
        if 'type' in data and isinstance(data['type'], str):
            for t in LoadingType:
                if t.value == data['type']:
                    data['type'] = t
                    break
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


# =============================================================================
# MSD PARAMETERS DATA CLASS
# =============================================================================

@dataclass
class MSDParameters:
    """Mass-Spring-Damper parameters for element."""
    # Primary MSD values
    k: float = 0.0                  # Stiffness (N/m)
    c: float = 0.0                  # Damping coefficient (N·s/m)
    m: float = 0.0                  # Mass (kg)
    
    # Auto-calculation flags
    auto_calculate_k: bool = True
    auto_calculate_c: bool = True
    auto_calculate_m: bool = True
    
    # Nonlinear stiffness (Iwan model)
    k_tangent: float = 0.0          # Tangent stiffness at current state
    chi: float = 0.0                # Power-law exponent
    k_t_threshold: float = 0.0      # Micro-slip threshold
    
    # Damping model
    damping_ratio: float = 0.02     # ζ for critical damping calc
    alpha_rayleigh: float = 0.0     # Mass proportional
    beta_rayleigh: float = 0.0      # Stiffness proportional
    
    # Gasket nonlinear behavior
    is_nonlinear: bool = False
    loading_curve: Optional[List[Tuple[float, float]]] = None   # (F, δ) pairs
    unloading_factor: float = 1.0   # Hysteresis factor
    
    def calculate_from_geometry_material(
        self, 
        geometry: GeometryData, 
        material: MaterialData,
        element_type: ElementType
    ) -> None:
        """
        Auto-calculate MSD parameters from geometry and material.
        Uses VDI 2230 formulations.
        """
        k_before = self.k  # Save current k; restored at end if calculation produces k<=0
        E = material.E * 1e6  # Convert MPa to Pa
        rho = material.rho     # kg/m³

        # Length and area in meters
        L = geometry.length / 1000.0
        
        if element_type == ElementType.SHANK:
            # Unthreaded shank: k = EA/L
            A = math.pi / 4 * (geometry.diameter / 1000.0)**2
            if self.auto_calculate_k:
                k_computed = E * A / L if (L > 0 and A > 0) else 0
                if k_computed > 0:
                    self.k = k_computed
            if self.auto_calculate_m and A > 0:
                self.m = rho * A * L

        elif element_type == ElementType.THREAD:
            # Threaded portion: use tensile stress area
            At = (geometry.At or 84.3) / 1e6  # mm² to m²
            if self.auto_calculate_k:
                k_computed = E * At / L if (L > 0 and At > 0) else 0
                if k_computed > 0:
                    self.k = k_computed
            if self.auto_calculate_m:
                # Use minor diameter for mass
                d3 = (geometry.d3 or geometry.diameter * 0.84) / 1000.0
                A_minor = math.pi / 4 * d3**2
                self.m = rho * A_minor * L
                
        elif element_type == ElementType.HEAD:
            # Bolt head: high stiffness, small compliance
            d = geometry.diameter / 1000.0
            h = (geometry.head_height or geometry.diameter * 0.7) / 1000.0
            A = math.pi / 4 * d**2
            if self.auto_calculate_k:
                self.k = 0.5 * E * d  # VDI 2230 head compliance: k = 0.5·E·d
            if self.auto_calculate_m:
                # Head mass approximation
                d_head = (geometry.head_diameter or geometry.diameter * 1.5) / 1000.0
                self.m = rho * math.pi / 4 * d_head**2 * h
                
        elif element_type == ElementType.NUT:
            # Nut: similar to head
            d = geometry.diameter / 1000.0
            h = (geometry.head_height or geometry.diameter * 0.8) / 1000.0
            if self.auto_calculate_k:
                self.k = 0.5 * E * d  # VDI 2230 nut compliance: k = 0.5·E·d
            if self.auto_calculate_m:
                d_nut = (geometry.head_diameter or geometry.diameter * 1.8) / 1000.0
                A_nut = math.pi / 4 * (d_nut**2 - d**2)
                self.m = rho * A_nut * h
                
        elif element_type in (ElementType.FLANGE, ElementType.MEMBER):
            # Clamped member: frustum cone model
            d = geometry.diameter / 1000.0
            t = (geometry.thickness or geometry.length) / 1000.0
            d_w = (geometry.bearing_diameter or geometry.diameter * 1.6) / 1000.0
            d_hole = (geometry.hole_diameter or geometry.diameter * 1.1) / 1000.0
            alpha = math.radians(geometry.frustum_angle)
            
            if self.auto_calculate_k and t > 0 and d > 0:
                # VDI 2230 frustum model
                tan_a = math.tan(alpha)
                if d_w > d_hole:
                    numerator = math.pi * E * d * tan_a
                    arg1 = (2 * t * tan_a + d_w - d) * (d_w + d)
                    arg2 = (2 * t * tan_a + d_w + d) * (d_w - d)
                    if arg1 > 0 and arg2 > 0:
                        denominator = math.log(arg1 / arg2)
                        self.k = numerator / denominator if denominator != 0 else E * math.pi * d**2 / (4 * t)
                    else:
                        self.k = E * math.pi * d**2 / (4 * t)
                else:
                    self.k = E * math.pi * d**2 / (4 * t)
            
            if self.auto_calculate_m:
                # Approximate mass for frustum region
                d_avg = (d_w + d_hole) / 2
                A_avg = math.pi / 4 * (d_avg**2 - d_hole**2)
                self.m = rho * A_avg * t
                
        elif element_type == ElementType.GASKET:
            # Gasket: use gasket stiffness per unit area
            d_o = (geometry.bearing_diameter or geometry.diameter * 2) / 1000.0
            d_i = (geometry.hole_diameter or geometry.diameter * 1.1) / 1000.0
            t = geometry.thickness / 1000.0 if geometry.thickness > 0 else 0.003
            A_gasket = math.pi / 4 * (d_o**2 - d_i**2)
            
            # Typical metallic gasket: k_n = 27.5 GPa/mm
            k_n = 27.5e9  # N/m per m² per m thickness
            if self.auto_calculate_k:
                k_computed = k_n * A_gasket / t if (t > 0 and A_gasket > 0) else 0
                if k_computed > 0:
                    self.k = k_computed
                # If area or thickness are zero (no geometry set), keep current k
            if self.auto_calculate_m:
                rho_gasket = 2500  # Graphite/composite typical
                if A_gasket > 0:
                    self.m = rho_gasket * A_gasket * t
                
        elif element_type == ElementType.WASHER:
            # Washer: thin plate
            d_o = (geometry.bearing_diameter or geometry.diameter * 2) / 1000.0
            d_i = (geometry.hole_diameter or geometry.diameter * 1.1) / 1000.0
            t = geometry.thickness / 1000.0 if geometry.thickness > 0 else 0.003
            A_washer = math.pi / 4 * (d_o**2 - d_i**2)

            if self.auto_calculate_k:
                k_computed = E * A_washer / t if (t > 0 and A_washer > 0) else 0
                if k_computed > 0:
                    self.k = k_computed
            if self.auto_calculate_m and A_washer > 0:
                self.m = rho * A_washer * t

        elif element_type == ElementType.BEAM_CONNECTOR:
            # Timoshenko beam connector: k_axial = EA/L (primary)
            d = geometry.diameter / 1000.0
            A = math.pi / 4 * d**2
            if self.auto_calculate_k:
                self.k = E * A / L if L > 0 else 0
            if self.auto_calculate_m:
                self.m = rho * A * L

        # Top-level guard: never zero out a previously valid k due to missing geometry
        if self.auto_calculate_k and self.k <= 0 and k_before > 0:
            self.k = k_before

        # Calculate damping from damping ratio
        if self.auto_calculate_c and self.k > 0 and self.m > 0:
            omega_n = math.sqrt(self.k / self.m)
            self.c = 2 * self.damping_ratio * math.sqrt(self.k * self.m)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "k": self.k,
            "c": self.c,
            "m": self.m,
            "auto_calculate_k": self.auto_calculate_k,
            "auto_calculate_c": self.auto_calculate_c,
            "auto_calculate_m": self.auto_calculate_m,
            "damping_ratio": self.damping_ratio,
            "is_nonlinear": self.is_nonlinear
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MSDParameters':
        """Create from dictionary."""
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


# =============================================================================
# MAIN MSD ELEMENT DATA CLASS
# =============================================================================

@dataclass
class MSDElementData:
    """
    Complete MSD element data for bolted joint modeling.

    This is the primary data class used throughout the Bolt Analysis Studio
    for representing individual elements in the mass-spring-damper model.
    """
    # Identification
    id: int = 0
    name: str = ""
    type: ElementType = ElementType.MEMBER
    description: str = ""

    # Sub-data classes
    geometry: GeometryData = field(default_factory=GeometryData)
    material: MaterialData = field(default_factory=MaterialData)
    friction: FrictionData = field(default_factory=FrictionData)
    loading: LoadingData = field(default_factory=LoadingData)
    msd: MSDParameters = field(default_factory=MSDParameters)

    # Connection topology
    connection_type: ConnectionType = ConnectionType.SERIES
    parallel_group: int = 0         # Group ID for parallel elements
    connected_to: List[int] = field(default_factory=list)  # Adjacent element IDs

    # V2.0: Grid-based position
    grid_position: GridPosition = field(default_factory=GridPosition)

    # V2.0: Per-element preload as % of yield
    preload_percent_yield: float = 70.0   # Default 70% of yield
    preload_force: float = 0.0            # Computed F = (%/100) * A_s * Sy [N]

    # V2.0: Thread fillet model (for THREAD/NUT elements)
    thread_fillet_model: Optional[ThreadFilletModel] = None

    # V2.0: Applied loads and constraints
    applied_loads: List[AppliedLoad] = field(default_factory=list)
    constraints: List[Constraint] = field(default_factory=list)

    # Visual position (for schematic) - legacy, use grid_position for v2.0
    x: float = 0.0
    y: float = 0.0

    # Metadata
    created: str = ""
    modified: str = ""
    locked: bool = False            # Prevent editing
    visible: bool = True            # Show in schematic
    metadata: Dict[str, Any] = field(default_factory=dict)  # Extended properties

    # Analysis results (populated after solving)
    displacement: Optional[np.ndarray] = None
    velocity: Optional[np.ndarray] = None
    force: Optional[np.ndarray] = None
    
    def __post_init__(self):
        """Initialize timestamps and auto-calculate MSD params."""
        if not self.created:
            self.created = datetime.now().isoformat()
        if not self.modified:
            self.modified = self.created
        
        # Auto-generate name if empty
        if not self.name:
            self.name = f"{self.type.name.title()} #{self.id}"
        
        # Auto-calculate MSD parameters
        if any([self.msd.auto_calculate_k, self.msd.auto_calculate_c, self.msd.auto_calculate_m]):
            self.msd.calculate_from_geometry_material(
                self.geometry, self.material, self.type
            )
    
    def update_msd_parameters(self) -> None:
        """Recalculate MSD parameters from current geometry/material."""
        self.msd.calculate_from_geometry_material(
            self.geometry, self.material, self.type
        )
        self.modified = datetime.now().isoformat()
    
    def get_stiffness(self) -> float:
        """Returns element stiffness (N/m)."""
        return self.msd.k
    
    def get_mass(self) -> float:
        """Returns element mass (kg)."""
        return self.msd.m
    
    def get_damping(self) -> float:
        """Returns element damping (N·s/m)."""
        return self.msd.c
    
    def get_natural_frequency(self) -> float:
        """Returns natural frequency (Hz) of isolated element."""
        if self.msd.k > 0 and self.msd.m > 0:
            omega_n = math.sqrt(self.msd.k / self.msd.m)
            return omega_n / (2 * math.pi)
        return 0.0
    
    def validate(self) -> Tuple[bool, List[str]]:
        """
        Validate element data.
        Returns (is_valid, list of error/warning messages).
        """
        messages = []
        is_valid = True
        
        # Check stiffness
        if self.msd.k <= 0:
            messages.append(f"ERROR: Element {self.id} has k ≤ 0")
            is_valid = False
        
        # Check mass (can be zero for massless springs)
        if self.msd.m < 0:
            messages.append(f"ERROR: Element {self.id} has m < 0")
            is_valid = False
        
        # Check damping
        if self.msd.c < 0:
            messages.append(f"ERROR: Element {self.id} has c < 0")
            is_valid = False
        
        # Check geometry (skip for GROUND — no physical geometry)
        if self.geometry.diameter <= 0 and self.type != ElementType.GROUND and not self.type.is_contact_interface:
            messages.append(f"WARNING: Element {self.id} has zero diameter")

        if self.geometry.length <= 0 and self.type != ElementType.GROUND and not self.type.is_contact_interface:
            messages.append(f"WARNING: Element {self.id} has zero length")
        
        # Check material
        if self.material.E <= 0:
            messages.append(f"ERROR: Element {self.id} has E ≤ 0")
            is_valid = False
        
        # Check friction
        if self.friction.mu_thread < 0 or self.friction.mu_thread > 1:
            messages.append(f"WARNING: Element {self.id} has unusual μ_thread")
        
        return is_valid, messages
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        result = {
            "id": self.id,
            "name": self.name,
            "type": self.type.value if isinstance(self.type, ElementType) else self.type.name,
            "description": self.description,
            "geometry": self.geometry.to_dict(),
            "material": self.material.to_dict(),
            "friction": self.friction.to_dict(),
            "loading": self.loading.to_dict(),
            "msd": self.msd.to_dict(),
            "connection_type": self.connection_type.value,
            "parallel_group": self.parallel_group,
            "connected_to": self.connected_to,
            "grid_position": {"row": self.grid_position.row, "column": self.grid_position.column},
            "preload_percent_yield": self.preload_percent_yield,
            "preload_force": self.preload_force,
            # CB3: Serialize applied loads and constraints
            "applied_loads": [load.to_dict() for load in self.applied_loads],
            "constraints": [con.to_dict() for con in self.constraints],
            "x": self.x,
            "y": self.y,
            "created": self.created,
            "modified": self.modified,
            "locked": self.locked,
            "visible": self.visible,
            "metadata": self.metadata
        }
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MSDElementData':
        """Create MSDElementData from dictionary."""
        # Parse element type
        if 'type' in data:
            if isinstance(data['type'], str):
                # Handle string type names
                for t in ElementType:
                    if t.name == data['type']:
                        data['type'] = t
                        break
            elif isinstance(data['type'], int):
                # Handle integer type values
                try:
                    data['type'] = ElementType(data['type'])
                except ValueError:
                    # Unknown type ID, use GENERIC_CONTACT as fallback
                    print(f"Warning: Unknown element type ID {data['type']}, using GENERIC_CONTACT")
                    data['type'] = ElementType.GENERIC_CONTACT
        
        # Parse connection type
        if 'connection_type' in data and isinstance(data['connection_type'], str):
            for ct in ConnectionType:
                if ct.value == data['connection_type']:
                    data['connection_type'] = ct
                    break
        
        # Parse sub-data classes
        if 'geometry' in data and isinstance(data['geometry'], dict):
            data['geometry'] = GeometryData.from_dict(data['geometry'])
        if 'material' in data and isinstance(data['material'], dict):
            data['material'] = MaterialData.from_dict(data['material'])
        if 'friction' in data and isinstance(data['friction'], dict):
            data['friction'] = FrictionData.from_dict(data['friction'])
        if 'loading' in data and isinstance(data['loading'], dict):
            data['loading'] = LoadingData.from_dict(data['loading'])
        if 'msd' in data and isinstance(data['msd'], dict):
            data['msd'] = MSDParameters.from_dict(data['msd'])
        if 'grid_position' in data and isinstance(data['grid_position'], dict):
            data['grid_position'] = GridPosition.from_dict(data['grid_position'])

        # CB3: Parse applied loads and constraints
        if 'applied_loads' in data and isinstance(data['applied_loads'], list):
            data['applied_loads'] = [
                AppliedLoad.from_dict(ld) if isinstance(ld, dict) else ld
                for ld in data['applied_loads']
            ]
        if 'constraints' in data and isinstance(data['constraints'], list):
            data['constraints'] = [
                Constraint.from_dict(cd) if isinstance(cd, dict) else cd
                for cd in data['constraints']
            ]

        # Filter to valid fields
        valid_fields = {k: v for k, v in data.items() if k in cls.__dataclass_fields__}

        return cls(**valid_fields)
    
    def clone(self, new_id: Optional[int] = None) -> 'MSDElementData':
        """Create a deep copy of this element."""
        data = self.to_dict()
        if new_id is not None:
            data['id'] = new_id
        data['created'] = datetime.now().isoformat()
        data['modified'] = data['created']
        return MSDElementData.from_dict(data)


# =============================================================================
# FACTORY FUNCTIONS FOR COMMON ELEMENTS
# =============================================================================

def create_bolt_head(
    id: int,
    diameter: float = 12.0,
    material: MaterialGrade = MaterialGrade.A193_B7,
    x: float = 0.0,
    y: float = 0.0
) -> MSDElementData:
    """Create a bolt head element."""
    # Standard hex head dimensions (ISO 4014)
    head_size = {
        8: (13, 5.3),    # (across flats, height)
        10: (17, 6.4),
        12: (19, 7.5),
        14: (22, 8.8),
        16: (24, 10.0),
        18: (27, 11.5),
        20: (30, 12.5),
        22: (32, 14.0),
        24: (36, 15.0),
        27: (41, 17.0),
        30: (46, 18.7),
        36: (55, 22.5),
    }
    
    d_int = int(diameter)
    head_af, head_h = head_size.get(d_int, (diameter * 1.5, diameter * 0.7))
    
    return MSDElementData(
        id=id,
        name=f"Bolt Head M{d_int}",
        type=ElementType.HEAD,
        geometry=GeometryData(
            diameter=diameter,
            length=head_h,
            head_diameter=head_af,
            head_height=head_h,
            bearing_diameter=head_af * 1.1
        ),
        material=MaterialData(grade=material),
        x=x,
        y=y
    )


def create_bolt_shank(
    id: int,
    diameter: float = 12.0,
    length: float = 30.0,
    material: MaterialGrade = MaterialGrade.A193_B7,
    x: float = 0.0,
    y: float = 0.0
) -> MSDElementData:
    """Create a bolt shank (unthreaded) element."""
    return MSDElementData(
        id=id,
        name=f"Shank M{int(diameter)}×{int(length)}",
        type=ElementType.SHANK,
        geometry=GeometryData(
            diameter=diameter,
            length=length,
            pitch=0.0  # No threads
        ),
        material=MaterialData(grade=material),
        x=x,
        y=y
    )


def create_thread_element(
    id: int,
    diameter: float = 12.0,
    pitch: float = 1.75,
    length: float = 15.0,
    material: MaterialGrade = MaterialGrade.A193_B7,
    mu_thread: float = 0.12,
    x: float = 0.0,
    y: float = 0.0
) -> MSDElementData:
    """Create a thread engagement element."""
    return MSDElementData(
        id=id,
        name=f"Thread M{int(diameter)}×{pitch}",
        type=ElementType.THREAD,
        geometry=GeometryData(
            diameter=diameter,
            length=length,
            pitch=pitch
        ),
        material=MaterialData(grade=material),
        friction=FrictionData(mu_thread=mu_thread),
        x=x,
        y=y
    )


def create_nut(
    id: int,
    diameter: float = 12.0,
    pitch: float = 1.75,
    material: MaterialGrade = MaterialGrade.A193_B7,
    mu_bearing: float = 0.14,
    x: float = 0.0,
    y: float = 0.0
) -> MSDElementData:
    """Create a nut element."""
    # Standard hex nut dimensions (ISO 4032)
    nut_size = {
        8: (13, 6.8),    # (across flats, height)
        10: (17, 8.4),
        12: (19, 10.8),
        14: (22, 12.8),
        16: (24, 14.8),
        18: (27, 15.8),
        20: (30, 18.0),
        22: (32, 19.4),
        24: (36, 21.5),
        27: (41, 23.8),
        30: (46, 25.6),
        36: (55, 31.0),
    }
    
    d_int = int(diameter)
    nut_af, nut_h = nut_size.get(d_int, (diameter * 1.7, diameter * 0.9))
    
    return MSDElementData(
        id=id,
        name=f"Nut M{d_int}",
        type=ElementType.NUT,
        geometry=GeometryData(
            diameter=diameter,
            length=nut_h,
            pitch=pitch,
            head_diameter=nut_af,
            head_height=nut_h,
            bearing_diameter=nut_af * 1.1
        ),
        material=MaterialData(grade=material),
        friction=FrictionData(mu_bearing=mu_bearing),
        x=x,
        y=y
    )


def create_flange(
    id: int,
    thickness: float = 25.0,
    bolt_diameter: float = 12.0,
    material_name: str = "A105",
    x: float = 0.0,
    y: float = 0.0
) -> MSDElementData:
    """Create a flange member element."""
    # A105 carbon steel properties
    material = MaterialData(
        name=material_name,
        E=200000.0,
        Sy=250.0,
        Su=485.0,
        rho=7850.0
    )
    
    return MSDElementData(
        id=id,
        name=f"Flange t={int(thickness)}",
        type=ElementType.FLANGE,
        geometry=GeometryData(
            diameter=bolt_diameter,
            length=thickness,
            thickness=thickness,
            bearing_diameter=bolt_diameter * 2.0,
            hole_diameter=bolt_diameter * 1.1,
            frustum_angle=30.0
        ),
        material=material,
        x=x,
        y=y
    )


def create_gasket(
    id: int,
    inner_diameter: float = 50.0,
    outer_diameter: float = 80.0,
    thickness: float = 3.0,
    gasket_type: str = "spiral_wound",
    x: float = 0.0,
    y: float = 0.0
) -> MSDElementData:
    """Create a gasket element."""
    # Gasket stiffness lookup (GPa/mm)
    gasket_stiffness = {
        "spiral_wound": 27.5,
        "ring_joint": 50.0,
        "flat_metallic": 35.0,
        "graphite": 15.0,
        "ptfe": 5.0
    }
    
    k_n = gasket_stiffness.get(gasket_type, 20.0) * 1e9  # Convert to N/m/m²
    
    return MSDElementData(
        id=id,
        name=f"Gasket ({gasket_type})",
        type=ElementType.GASKET,
        geometry=GeometryData(
            diameter=(inner_diameter + outer_diameter) / 2,
            thickness=thickness,
            length=thickness,
            bearing_diameter=outer_diameter,
            hole_diameter=inner_diameter
        ),
        material=MaterialData(
            name=f"Gasket - {gasket_type}",
            E=k_n * thickness / 1e6,  # Effective E
            rho=2500.0  # Typical gasket density
        ),
        x=x,
        y=y
    )


def create_washer(
    id: int,
    bolt_diameter: float = 12.0,
    thickness: float = 3.0,
    material: MaterialGrade = MaterialGrade.A193_B7,
    x: float = 0.0,
    y: float = 0.0
) -> MSDElementData:
    """Create a washer element."""
    # Standard washer dimensions (ISO 7089)
    washer_size = {
        8: (8.4, 16, 1.6),    # (inner, outer, thickness)
        10: (10.5, 20, 2.0),
        12: (13.0, 24, 2.5),
        14: (15.0, 28, 2.5),
        16: (17.0, 30, 3.0),
        18: (19.0, 34, 3.0),
        20: (21.0, 37, 3.0),
        22: (23.0, 39, 3.0),
        24: (25.0, 44, 4.0),
        27: (28.0, 50, 4.0),
        30: (31.0, 56, 4.0),
        36: (37.0, 66, 5.0),
    }
    
    d_int = int(bolt_diameter)
    d_i, d_o, t_std = washer_size.get(d_int, (bolt_diameter * 1.1, bolt_diameter * 2, 3.0))
    
    if thickness == 0:
        thickness = t_std
    
    return MSDElementData(
        id=id,
        name=f"Washer M{d_int}",
        type=ElementType.WASHER,
        geometry=GeometryData(
            diameter=bolt_diameter,
            length=thickness,
            thickness=thickness,
            bearing_diameter=d_o,
            hole_diameter=d_i
        ),
        material=MaterialData(grade=material),
        x=x,
        y=y
    )


def create_ground(id: int, x: float = 0.0, y: float = 0.0) -> MSDElementData:
    """Create a ground (fixed) element."""
    return MSDElementData(
        id=id,
        name="Ground",
        type=ElementType.GROUND,
        geometry=GeometryData(diameter=0, length=0),
        material=MaterialData(name="Ground", E=1e15),
        msd=MSDParameters(k=1e15, m=0, c=0, auto_calculate_k=False, auto_calculate_m=False),
        x=x,
        y=y
    )


def create_distributed_thread(
    start_id: int,
    diameter: float = 12.0,
    pitch: float = 1.75,
    length: float = 15.0,
    material: MaterialGrade = MaterialGrade.A193_B7,
    distribution: str = 'exponential',
    lambda_decay: float = 0.3,
    n_power: float = 2.0,
    n_segments: int = 5,
    connection: str = 'series',
    x: float = 0.0,
    y: float = 0.0
) -> List[MSDElementData]:
    """
    Create a distributed thread element with load distribution.

    Thread load distribution follows VDI 2230 guidance where first engaged
    threads carry significantly more load than later threads.

    Distribution models:
    - 'uniform': Equal stiffness per segment
    - 'exponential': k(x) = k_base × exp(-λ × x / L)
    - 'power_law': k(x) = k_base × (1 - x/L)^n
    - 'linear_taper': k(x) = k_base × (1 - 0.5 × x/L)

    Args:
        start_id: Starting element ID
        diameter: Nominal thread diameter (mm)
        pitch: Thread pitch (mm)
        length: Total engaged thread length (mm)
        material: Material grade
        distribution: Distribution model ('uniform', 'exponential', 'power_law', 'linear_taper')
        lambda_decay: Decay constant for exponential (typical 0.2-0.5)
        n_power: Power exponent for power_law
        n_segments: Number of thread segments (3-20)
        connection: 'series' or 'parallel' for segment connection
        x, y: Base position

    Returns:
        List of MSDElementData for the thread segments
    """
    elements = []
    segment_length = length / n_segments

    # Calculate base stiffness for a single thread element
    base_thread = create_thread_element(
        id=0,
        diameter=diameter,
        pitch=pitch,
        length=length,
        material=material
    )
    k_total = base_thread.msd.k
    m_total = base_thread.msd.m

    # Calculate stiffness distribution factors
    x_positions = np.linspace(0, length, n_segments + 1)[:-1] + segment_length / 2
    x_normalized = x_positions / length

    if distribution == 'uniform':
        factors = np.ones(n_segments)
    elif distribution == 'exponential':
        # k(x) = k_base × exp(-λ × x / L)
        factors = np.exp(-lambda_decay * x_normalized * n_segments)
    elif distribution == 'power_law':
        # k(x) = k_base × (1 - x/L)^n
        factors = (1 - x_normalized) ** n_power
    elif distribution == 'linear_taper':
        # k(x) = k_base × (1 - 0.5 × x/L)
        factors = 1 - 0.5 * x_normalized
    else:
        factors = np.ones(n_segments)

    # Normalize factors so total stiffness matches
    if connection == 'series':
        # For series: 1/k_total = Σ(1/k_i) where k_i = factor_i × k_base
        # So: 1/k_total = (1/k_base) × Σ(1/factor_i)
        # Therefore: k_base = k_total × Σ(1/factor_i)
        inv_factor_sum = np.sum(1.0 / factors)
        k_base = k_total * inv_factor_sum if inv_factor_sum > 0 else k_total
    else:
        # For parallel: k_total = Σk_i
        factor_sum = np.sum(factors)
        k_base = k_total / factor_sum if factor_sum > 0 else k_total / n_segments

    # Create segment elements
    y_offset = y
    for i in range(n_segments):
        k_segment = k_base * factors[i]
        m_segment = m_total / n_segments

        segment = MSDElementData(
            id=start_id + i,
            name=f"Thread Seg {i+1}/{n_segments}",
            type=ElementType.THREAD,
            geometry=GeometryData(
                diameter=diameter,
                length=segment_length,
                pitch=pitch
            ),
            material=MaterialData(grade=material),
            msd=MSDParameters(
                k=k_segment,
                m=m_segment,
                auto_calculate_k=False,
                auto_calculate_m=False
            ),
            connection_type=ConnectionType.SERIES if connection == 'series' else ConnectionType.PARALLEL_MEMBER,
            x=x,
            y=y_offset
        )

        # Set parallel group if parallel connection
        if connection == 'parallel':
            segment.parallel_group = start_id  # Use start_id as group ID

        elements.append(segment)
        y_offset += 40

    return elements


def create_timoshenko_beam_element(
    id: int,
    diameter: float,              # Bolt diameter [mm]
    length: float,                # Element length [mm]
    E: float = 210e3,             # Young's modulus [MPa]
    G: float = 80e3,              # Shear modulus [MPa]
    rho: float = 7850e-12,        # Density [tonne/mm^3] (= 7850 kg/m^3)
    kappa: float = 6.0 / 7.0,    # Timoshenko shear correction factor (6/7 for circular)
    name: str = "Beam Connector"
) -> MSDElementData:
    """
    Create a Timoshenko beam connector element (NI1 - Phase 10).

    Models the bolt as a Timoshenko beam that includes shear deformation
    effects important for short, stocky bolts where the length-to-diameter
    ratio L/d < 10.

    The Timoshenko beam theory adds shear deformation to the classical
    Euler-Bernoulli beam, resulting in reduced bending stiffness through
    the shear parameter phi.

    Stiffness formulae:
    - Axial:    k_axial   = E * A / L
    - Bending:  k_bending = 12 * E * I / (L^3 * (1 + phi))
                where phi = 12 * E * I / (kappa * G * A * L^2)
    - Shear:    k_shear   = kappa * G * A / L
    - Torsion:  k_torsion = G * J / L

    The primary MSD stiffness is the axial stiffness; bending, shear,
    and torsional stiffnesses are stored in metadata for use by advanced
    solvers that resolve multi-DOF beam behavior.

    Reference:
    - Timoshenko, S. P. & Goodier, J. N. (1970), Theory of Elasticity.
    - Timoshenko, S. P. (1921), "On the correction for shear of the
      differential equation for transverse vibrations of prismatic bars",
      Philosophical Magazine, 41: 744-746.

    Args:
        id: Element ID
        diameter: Bolt nominal diameter [mm]
        length: Element length [mm]
        E: Young's modulus [MPa]
        G: Shear modulus [MPa]
        rho: Density [tonne/mm^3] (7850e-12 = 7850 kg/m^3)
        kappa: Timoshenko shear correction factor
               (6/7 for solid circular, 5/6 for rectangular)
        name: Element name

    Returns:
        MSDElementData with beam stiffness properties in metadata
    """
    # --- Section properties (all in mm) ---
    A = math.pi * diameter**2 / 4.0          # Cross-section area [mm^2]
    I = math.pi * diameter**4 / 64.0         # Second moment of area [mm^4]
    J = math.pi * diameter**4 / 32.0         # Polar moment of inertia [mm^4]

    # --- Timoshenko beam stiffnesses (N/mm units since E,G in MPa=N/mm^2) ---
    # Shear deformation parameter (dimensionless)
    if kappa > 0 and G > 0 and A > 0 and length > 0:
        phi = 12.0 * E * I / (kappa * G * A * length**2)
    else:
        phi = 0.0

    # Axial stiffness: k = EA/L
    k_axial = E * A / length if length > 0 else 0.0

    # Bending stiffness (Timoshenko): reduced by shear
    if length > 0:
        k_bending = 12.0 * E * I / (length**3 * (1.0 + phi))
    else:
        k_bending = 0.0

    # Shear stiffness
    k_shear = kappa * G * A / length if length > 0 else 0.0

    # Torsional stiffness
    k_torsion = G * J / length if length > 0 else 0.0

    # --- Convert to SI for MSD (N/m and kg) ---
    # 1 N/mm = 1e3 N/m
    k_eff = k_axial * 1e3          # Primary stiffness is axial [N/m]

    # Mass: rho [tonne/mm^3] * A [mm^2] * L [mm] = [tonne]
    # Convert tonne to kg: *1e3
    # BUT rho=7850e-12 tonne/mm^3, so:
    # mass = 7850e-12 * A * L [tonne] = 7850e-12 * A * L * 1e3 [kg]
    #      = 7850e-9 * A * L [kg]
    # Alternatively in pure SI: rho_SI = 7850 kg/m^3, A_SI = A*1e-6 m^2,
    #                           L_SI = L*1e-3 m
    # mass = 7850 * A*1e-6 * L*1e-3 = 7850 * A * L * 1e-9 [kg]
    rho_si = rho * 1e9  # Convert tonne/mm^3 to kg/m^3 (7850e-12 * 1e9 = 7850e-3... )
    # Direct: rho [tonne/mm^3] = rho * 1e3 [kg/mm^3] = rho * 1e12 [kg/m^3]
    # 7850e-12 * 1e12 = 7850 kg/m^3
    rho_kg_m3 = rho * 1e12     # kg/m^3
    A_m2 = A * 1e-6            # mm^2 -> m^2
    L_m = length * 1e-3        # mm -> m
    mass = rho_kg_m3 * A_m2 * L_m  # [kg]

    # Damping: 1% critical damping ratio
    zeta = 0.01
    if k_eff > 0 and mass > 0:
        c_eff = 2.0 * zeta * math.sqrt(k_eff * mass)
    else:
        c_eff = 0.0

    # Euler-Bernoulli bending stiffness for comparison (no shear correction)
    if length > 0:
        k_bending_eb = 12.0 * E * I / length**3
    else:
        k_bending_eb = 0.0

    # Slenderness ratio
    slenderness = length / diameter if diameter > 0 else 0.0

    return MSDElementData(
        id=id,
        name=name,
        type=ElementType.BEAM_CONNECTOR,
        description=(
            f"Timoshenko beam connector L/d={slenderness:.1f}, "
            f"phi={phi:.4f}"
        ),
        geometry=GeometryData(
            diameter=diameter,
            length=length,
            # Store cross-section area (mm^2) so it can be retrieved
        ),
        material=MaterialData(
            name="Custom Beam Material",
            E=E,
            G=G,
            rho=rho_kg_m3,
        ),
        msd=MSDParameters(
            k=k_eff,
            c=c_eff,
            m=mass,
            auto_calculate_k=False,
            auto_calculate_m=False,
            auto_calculate_c=False,
            damping_ratio=zeta,
        ),
        metadata={
            'element_model': 'timoshenko_beam',
            # Stiffnesses in N/mm (consistent with E in MPa = N/mm^2)
            'k_axial_N_per_mm': k_axial,
            'k_bending_N_per_mm': k_bending,
            'k_bending_euler_bernoulli_N_per_mm': k_bending_eb,
            'k_shear_N_per_mm': k_shear,
            'k_torsion_Nmm_per_rad': k_torsion,
            # Stiffnesses in SI (N/m or N*m/rad)
            'k_axial': k_axial * 1e3,         # N/m
            'k_bending': k_bending * 1e3,      # N/m
            'k_shear': k_shear * 1e3,          # N/m
            'k_torsion': k_torsion * 1e-3,     # N*m/rad
            # Beam parameters
            'shear_parameter_phi': phi,
            'shear_reduction_factor': 1.0 / (1.0 + phi),
            'moment_of_inertia_mm4': I,
            'polar_moment_mm4': J,
            'cross_section_area_mm2': A,
            'shear_correction_factor': kappa,
            'slenderness_ratio': slenderness,
            # Material (for reference)
            'E_MPa': E,
            'G_MPa': G,
            'rho_kg_m3': rho_kg_m3,
        },
    )


def create_equivalent_bolt(
    id: int,
    diameter: float = 12.0,
    pitch: float = 1.75,
    shank_length: float = 30.0,
    thread_length: float = 15.0,
    material: MaterialGrade = MaterialGrade.A193_B7,
    x: float = 0.0,
    y: float = 0.0
) -> MSDElementData:
    """
    Create a single equivalent bolt element combining HEAD + SHANK + THREAD + NUT.

    Uses series stiffness formula: k_eq = 1 / (1/k_head + 1/k_shank + 1/k_thread + 1/k_nut)

    This simplified model is useful for quick analysis where internal bolt
    dynamics are not of interest.

    Args:
        id: Element ID
        diameter: Nominal bolt diameter (mm)
        pitch: Thread pitch (mm)
        shank_length: Unthreaded shank length (mm)
        thread_length: Thread engagement length (mm)
        material: Material grade
        x, y: Position

    Returns:
        Single MSDElementData representing the entire bolt
    """
    # Create individual components
    head = create_bolt_head(id=0, diameter=diameter, material=material)
    shank = create_bolt_shank(id=0, diameter=diameter, length=shank_length, material=material)
    thread = create_thread_element(id=0, diameter=diameter, pitch=pitch, length=thread_length, material=material)
    nut = create_nut(id=0, diameter=diameter, pitch=pitch, material=material)

    # Calculate equivalent stiffness (series)
    k_values = [head.msd.k, shank.msd.k, thread.msd.k, nut.msd.k]
    k_eq = 1.0 / sum(1.0/k for k in k_values if k > 0)

    # Calculate total mass
    m_total = head.msd.m + shank.msd.m + thread.msd.m + nut.msd.m

    # Calculate equivalent damping (series)
    c_values = [head.msd.c, shank.msd.c, thread.msd.c, nut.msd.c]
    c_eq = 1.0 / sum(1.0/c for c in c_values if c > 0) if all(c > 0 for c in c_values) else sum(c_values) / 4

    return MSDElementData(
        id=id,
        name=f"Equivalent Bolt M{int(diameter)}",
        type=ElementType.SHANK,  # Use SHANK as generic bolt type
        description="Combined HEAD + SHANK + THREAD + NUT",
        geometry=GeometryData(
            diameter=diameter,
            length=shank_length + thread_length,
            pitch=pitch
        ),
        material=MaterialData(grade=material),
        msd=MSDParameters(
            k=k_eq,
            m=m_total,
            c=c_eq,
            auto_calculate_k=False,
            auto_calculate_m=False,
            auto_calculate_c=False
        ),
        x=x,
        y=y
    )


# =============================================================================
# TESTING
# =============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("MSD Element Data Classes - Test Suite")
    print("Bolt Analysis Studio v4.0")
    print("=" * 70)
    
    # Test 1: Create bolt head
    print("\n[Test 1] Create M12 Bolt Head")
    head = create_bolt_head(id=1, diameter=12.0)
    print(f"  Name: {head.name}")
    print(f"  Type: {head.type.name}")
    print(f"  k = {head.msd.k:.3e} N/m")
    print(f"  m = {head.msd.m:.6f} kg")
    print(f"  f_n = {head.get_natural_frequency():.1f} Hz")
    
    # Test 2: Create shank
    print("\n[Test 2] Create M12×30 Shank")
    shank = create_bolt_shank(id=2, diameter=12.0, length=30.0)
    print(f"  Name: {shank.name}")
    print(f"  k = {shank.msd.k:.3e} N/m")
    print(f"  m = {shank.msd.m:.6f} kg")
    
    # Test 3: Create thread element
    print("\n[Test 3] Create M12×1.75 Thread")
    thread = create_thread_element(id=3, diameter=12.0, pitch=1.75, length=15.0)
    print(f"  Name: {thread.name}")
    print(f"  At = {thread.geometry.At:.2f} mm²")
    print(f"  k = {thread.msd.k:.3e} N/m")
    
    # Test 4: Create flange
    print("\n[Test 4] Create Flange t=25mm")
    flange = create_flange(id=4, thickness=25.0, bolt_diameter=12.0)
    print(f"  Name: {flange.name}")
    print(f"  k = {flange.msd.k:.3e} N/m")
    print(f"  m = {flange.msd.m:.6f} kg")
    
    # Test 5: Create gasket
    print("\n[Test 5] Create Spiral Wound Gasket")
    gasket = create_gasket(id=5, inner_diameter=50, outer_diameter=80, thickness=3.0)
    print(f"  Name: {gasket.name}")
    print(f"  k = {gasket.msd.k:.3e} N/m")
    
    # Test 6: Validation
    print("\n[Test 6] Validate Elements")
    elements = [head, shank, thread, flange, gasket]
    for elem in elements:
        valid, messages = elem.validate()
        status = "✓ Valid" if valid else "✗ Invalid"
        print(f"  {elem.name}: {status}")
        for msg in messages:
            print(f"    - {msg}")
    
    # Test 7: Serialization
    print("\n[Test 7] JSON Serialization")
    json_data = json.dumps(head.to_dict(), indent=2)
    print(f"  Serialized head element: {len(json_data)} characters")
    
    # Deserialize
    restored = MSDElementData.from_dict(json.loads(json_data))
    print(f"  Restored element: {restored.name}")
    print(f"  k matches: {abs(restored.msd.k - head.msd.k) < 1.0}")
    
    # Test 8: Clone
    print("\n[Test 8] Clone Element")
    cloned = head.clone(new_id=100)
    print(f"  Original ID: {head.id}, Clone ID: {cloned.id}")
    print(f"  Same k value: {abs(cloned.msd.k - head.msd.k) < 1.0}")
    
    print("\n" + "=" * 70)
    print("All tests completed successfully!")
    print("=" * 70)
