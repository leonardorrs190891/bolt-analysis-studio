"""
Load Propagation System for MSD Model Builder
Bolt Analysis Studio v4.0
Prof. Leonardo Rosa Ribeiro da Silva, PhD
February 2026

This module implements automatic force and moment propagation through
bolted joint structures, following VDI 2230 methodology and modern
FEA load distribution principles.

Features:
- Load path graph construction
- Force distribution (series/parallel)
- Induced moment calculation (F × d)
- Bending moment distribution per VDI 2230
- Equilibrium validation
- Free body diagram data generation

Author: Bolt Analysis Studio Team
References:
    - VDI 2230 Part 1 (2015)
    - Springer 2024 FEM research
    - Engineering statics principles
"""

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import List, Tuple, Optional, Dict, Callable
import numpy as np
from datetime import datetime


# =============================================================================
# ENUMERATIONS
# =============================================================================

class LoadType(Enum):
    """Types of loads that can be applied to elements."""
    POINT_FORCE = auto()         # Concentrated force at a point
    DISTRIBUTED_LOAD = auto()    # Distributed over length/area
    MOMENT = auto()              # Bending or torsional moment
    TORQUE = auto()              # Pure torque (rotational)
    PRESSURE = auto()            # Surface pressure
    THERMAL = auto()             # Thermal expansion load
    PRELOAD = auto()             # Initial bolt preload


class LoadDirection(Enum):
    """Standard load directions in global coordinate system."""
    AXIAL = auto()          # Along bolt axis (z-direction)
    TRANSVERSE_X = auto()   # Perpendicular to axis (x-direction)
    TRANSVERSE_Y = auto()   # Perpendicular to axis (y-direction)
    ARBITRARY = auto()      # Custom direction vector


class DistributionType(Enum):
    """Distribution patterns for distributed loads."""
    UNIFORM = auto()        # Constant magnitude
    LINEAR = auto()         # Linear variation
    PARABOLIC = auto()      # Parabolic variation
    SINUSOIDAL = auto()     # Sinusoidal variation


# =============================================================================
# DATA STRUCTURES
# =============================================================================

@dataclass
class LoadApplication:
    """
    Represents a load applied to an element in the MSD model.

    This is the primary data structure for user-defined loads. Each load
    is associated with a specific element and has magnitude, direction,
    and optional time variation.

    Attributes:
        load_id: Unique identifier for this load
        element_id: Target element receiving the load
        load_type: Type of load (force, moment, etc.)
        magnitude: Load magnitude (N, N/m, or N·m)
        direction: Standard direction or ARBITRARY for custom
        direction_vector: Custom direction [x, y, z] if ARBITRARY
        point_of_application: Local coordinates on element [x, y, z] (m)
        time_function: Optional callable F(t) for dynamic loads
        distribution_type: For distributed loads only
        name: Optional descriptive name
        active: Whether load is currently active
    """
    load_id: int
    element_id: int
    load_type: LoadType
    magnitude: float
    direction: LoadDirection = LoadDirection.AXIAL
    direction_vector: Optional[Tuple[float, float, float]] = None
    point_of_application: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    time_function: Optional[Callable[[float], float]] = None
    distribution_type: DistributionType = DistributionType.UNIFORM
    name: str = ""
    active: bool = True

    def __post_init__(self):
        """Validate load data after initialization."""
        if self.direction == LoadDirection.ARBITRARY and self.direction_vector is None:
            raise ValueError("ARBITRARY direction requires direction_vector")

        if self.name == "":
            self.name = f"Load_{self.load_id}"

    def get_force_at_time(self, t: float) -> float:
        """
        Get load magnitude at time t.

        Args:
            t: Time in seconds

        Returns:
            Load magnitude at time t (N or N·m)
        """
        if self.time_function is None:
            return self.magnitude
        return self.magnitude * self.time_function(t)

    def get_force_vector(self, t: float = 0.0) -> np.ndarray:
        """
        Get 3D force vector at time t in global coordinates.

        Args:
            t: Time in seconds

        Returns:
            Force vector [Fx, Fy, Fz] in Newtons
        """
        mag = self.get_force_at_time(t)

        if self.direction == LoadDirection.AXIAL:
            return np.array([0.0, 0.0, mag])
        elif self.direction == LoadDirection.TRANSVERSE_X:
            return np.array([mag, 0.0, 0.0])
        elif self.direction == LoadDirection.TRANSVERSE_Y:
            return np.array([0.0, mag, 0.0])
        elif self.direction == LoadDirection.ARBITRARY:
            # Normalize direction vector
            vec = np.array(self.direction_vector, dtype=float)
            norm = np.linalg.norm(vec)
            if norm > 0:
                vec = vec / norm
            return mag * vec

        return np.zeros(3)

    def to_dict(self) -> dict:
        """Serialize to dictionary for JSON storage."""
        return {
            'load_id': self.load_id,
            'element_id': self.element_id,
            'load_type': self.load_type.name,
            'magnitude': self.magnitude,
            'direction': self.direction.name,
            'direction_vector': self.direction_vector,
            'point_of_application': self.point_of_application,
            'distribution_type': self.distribution_type.name,
            'name': self.name,
            'active': self.active
        }

    @staticmethod
    def from_dict(data: dict) -> 'LoadApplication':
        """Deserialize from dictionary."""
        return LoadApplication(
            load_id=data['load_id'],
            element_id=data['element_id'],
            load_type=LoadType[data['load_type']],
            magnitude=data['magnitude'],
            direction=LoadDirection[data['direction']],
            direction_vector=tuple(data['direction_vector']) if data.get('direction_vector') else None,
            point_of_application=tuple(data.get('point_of_application', (0, 0, 0))),
            distribution_type=DistributionType[data.get('distribution_type', 'UNIFORM')],
            name=data.get('name', ''),
            active=data.get('active', True)
        )


@dataclass
class ElementPosition:
    """
    Spatial position and orientation of an element in 3D space.

    Used by LoadPropagator to calculate moment arms and induced moments.

    Attributes:
        element_id: Element identifier
        position: Center point [x, y, z] in global coords (meters)
        orientation: 3x3 rotation matrix (identity = aligned with global)
        length: Element length along local axis (meters)
    """
    element_id: int
    position: np.ndarray  # [x, y, z] in meters
    orientation: np.ndarray = field(default_factory=lambda: np.eye(3))
    length: float = 0.01

    def distance_to(self, other: 'ElementPosition') -> float:
        """
        Calculate Euclidean distance to another element.

        Args:
            other: Another ElementPosition

        Returns:
            Distance in meters
        """
        return np.linalg.norm(self.position - other.position)

    def moment_arm(self, force_position: np.ndarray) -> np.ndarray:
        """
        Calculate moment arm vector from element center to force point.

        Args:
            force_position: Force application point [x, y, z] (m)

        Returns:
            Moment arm vector [rx, ry, rz] (m)
        """
        return force_position - self.position


@dataclass
class LoadPath:
    """
    Represents path of load propagation through connected elements.

    A load path traces how a load flows from its application point
    through the structure via series, parallel, or branch connections.

    Attributes:
        source_load: The applied load that generates this path
        element_chain: Ordered list of element IDs in the path
        connection_types: Connection type between adjacent elements
        stiffness_ratios: For parallel/branch, fraction of load this path carries
    """
    source_load: LoadApplication
    element_chain: List[int] = field(default_factory=list)
    connection_types: List[str] = field(default_factory=list)  # 'series', 'parallel', 'branch'
    stiffness_ratios: List[float] = field(default_factory=list)

    def get_force_at_element(self, element_id: int, base_force: float) -> float:
        """
        Calculate force magnitude at specific element in this path.

        Args:
            element_id: Target element ID
            base_force: Initial force magnitude (N)

        Returns:
            Force at element (N), accounting for series/parallel distribution
        """
        if element_id not in self.element_chain:
            return 0.0

        idx = self.element_chain.index(element_id)
        force = base_force

        # Apply load distribution based on connection types
        for i in range(idx):
            if i >= len(self.connection_types):
                break

            if self.connection_types[i] == 'series':
                # Full force propagates through series connection
                continue
            elif self.connection_types[i] in ('parallel', 'branch'):
                # Reduce by stiffness ratio
                if i < len(self.stiffness_ratios):
                    force *= self.stiffness_ratios[i]

        return force


# =============================================================================
# LOAD PROPAGATION ENGINE
# =============================================================================

class LoadPropagator:
    """
    Core engine for calculating force and moment propagation through MSD model.

    This class implements the automatic load distribution algorithm that:
    1. Builds load path graphs from applied loads
    2. Propagates forces through series/parallel connections
    3. Calculates induced moments from eccentric forces (M = r × F)
    4. Distributes bending moments per VDI 2230 methodology
    5. Validates equilibrium (ΣF = 0, ΣM = 0)

    Usage:
        propagator = LoadPropagator(model)
        propagator.add_load(load_application)
        forces = propagator.get_propagated_forces(element_id, t)
        moments = propagator.get_induced_moments(element_id, t)

    Attributes:
        model: Reference to parent MSDModel
        applied_loads: List of user-defined LoadApplications
        element_positions: Dict mapping element_id → ElementPosition
        load_paths: Calculated load paths through structure
    """

    def __init__(self, model=None):
        """
        Initialize load propagator.

        Args:
            model: Parent MSDModel instance (optional, can be set later)
        """
        self.model = model
        self.applied_loads: List[LoadApplication] = []
        self.element_positions: Dict[int, ElementPosition] = {}
        self.load_paths: List[LoadPath] = []
        self._origin = np.array([0.0, 0.0, 0.0])  # Global origin for moments
        self._next_load_id = 1

    def set_model(self, model):
        """Set or update the parent model reference."""
        self.model = model

    def set_origin(self, position: np.ndarray):
        """
        Set global coordinate origin for moment calculations.

        Args:
            position: Origin point [x, y, z] in meters
        """
        self._origin = np.array(position, dtype=float)

    def add_load(self, load: LoadApplication):
        """
        Add a load application to the system.

        This triggers rebuild of load paths.

        Args:
            load: LoadApplication to add
        """
        self.applied_loads.append(load)
        self._rebuild_load_paths()

    def remove_load(self, load_id: int):
        """
        Remove a load by ID.

        Args:
            load_id: ID of load to remove
        """
        self.applied_loads = [l for l in self.applied_loads if l.load_id != load_id]
        self._rebuild_load_paths()

    def clear_loads(self):
        """Remove all applied loads."""
        self.applied_loads.clear()
        self.load_paths.clear()

    def set_element_position(self, element_id: int, position: ElementPosition):
        """
        Register spatial position of an element.

        Args:
            element_id: Element identifier
            position: ElementPosition data
        """
        self.element_positions[element_id] = position

    def get_next_load_id(self) -> int:
        """Get next available load ID."""
        load_id = self._next_load_id
        self._next_load_id += 1
        return load_id

    def _rebuild_load_paths(self):
        """Rebuild load path graphs after load changes."""
        self.load_paths = []

        for load in self.applied_loads:
            if not load.active:
                continue

            path = self._build_path_from_load(load)
            self.load_paths.append(path)

    def _build_path_from_load(self, load: LoadApplication) -> LoadPath:
        """
        Build load path starting from a load application.

        Traces through element connections following series/parallel logic.

        Args:
            load: Source LoadApplication

        Returns:
            LoadPath object
        """
        if self.model is None:
            return LoadPath(source_load=load, element_chain=[load.element_id])

        # Get source element
        try:
            source_elem = self.model.get_element_by_id(load.element_id)
        except (AttributeError, KeyError, IndexError):
            # Model doesn't have get_element_by_id or element not found
            return LoadPath(source_load=load, element_chain=[load.element_id])

        element_chain = [source_elem.element_id]
        connection_types = []
        stiffness_ratios = []

        current_elem = source_elem
        visited = set([source_elem.element_id])

        # Traverse forward through connections
        max_iterations = 100  # Prevent infinite loops
        iterations = 0

        while iterations < max_iterations:
            iterations += 1

            # Get connected elements
            connected = self._get_connected_elements(current_elem)

            if not connected:
                break  # End of chain

            # Filter out already visited
            connected = [e for e in connected if e.element_id not in visited]

            if not connected:
                break

            if len(connected) == 1:
                # Series connection - full force transfer
                next_elem = connected[0]
                connection_types.append('series')
                stiffness_ratios.append(1.0)

            else:
                # Parallel or branch - distribute by stiffness
                k_total = sum(e.k for e in connected if hasattr(e, 'k') and e.k > 0)

                if k_total == 0:
                    break

                # Follow stiffest path (primary load path)
                next_elem = max(connected, key=lambda e: getattr(e, 'k', 0))
                k_ratio = next_elem.k / k_total if k_total > 0 else 0.0

                connection_types.append('parallel')
                stiffness_ratios.append(k_ratio)

            element_chain.append(next_elem.element_id)
            visited.add(next_elem.element_id)
            current_elem = next_elem

        return LoadPath(
            source_load=load,
            element_chain=element_chain,
            connection_types=connection_types,
            stiffness_ratios=stiffness_ratios
        )

    def _get_connected_elements(self, element) -> List:
        """
        Get elements connected to given element.

        Args:
            element: Source element

        Returns:
            List of connected element objects
        """
        if self.model is None:
            return []

        connected = []

        try:
            elem_idx = self.model.elements.index(element)

            # Next element in series chain (simple implementation)
            if elem_idx + 1 < len(self.model.elements):
                connected.append(self.model.elements[elem_idx + 1])

        except (ValueError, AttributeError):
            pass

        return connected

    def get_propagated_forces(self, element_id: int, t: float = 0.0) -> np.ndarray:
        """
        Calculate total propagated forces acting on element at time t.

        This sums contributions from all load paths passing through the element.

        Args:
            element_id: Target element ID
            t: Time in seconds

        Returns:
            3D force vector [Fx, Fy, Fz] in Newtons
        """
        force_total = np.zeros(3)

        for path in self.load_paths:
            if element_id in path.element_chain:
                # Get base force vector from load
                base_force_vec = path.source_load.get_force_vector(t)

                # Get magnitude at this element
                force_mag = path.get_force_at_element(
                    element_id,
                    np.linalg.norm(base_force_vec)
                )

                # Scale force vector maintaining direction
                if np.linalg.norm(base_force_vec) > 1e-12:
                    force_vec = base_force_vec * (force_mag / np.linalg.norm(base_force_vec))
                    force_total += force_vec

        return force_total

    def get_induced_moments(self, element_id: int, t: float = 0.0) -> np.ndarray:
        """
        Calculate induced bending moments on element from eccentric forces.

        Uses cross product: M = r × F
        where r is moment arm from element to force application point.

        Args:
            element_id: Target element ID
            t: Time in seconds

        Returns:
            3D moment vector [Mx, My, Mz] in N·m
        """
        if element_id not in self.element_positions:
            return np.zeros(3)

        elem_pos = self.element_positions[element_id]
        moment_total = np.zeros(3)

        for load in self.applied_loads:
            if not load.active:
                continue

            if load.load_type == LoadType.MOMENT:
                # Direct moment application
                if load.element_id == element_id:
                    moment_total[2] += load.get_force_at_time(t)  # Assume z-axis

            elif load.load_type == LoadType.POINT_FORCE:
                # Induced moment from force at distance

                # Get force position in global coordinates
                load_elem_pos = self.element_positions.get(load.element_id)
                if load_elem_pos is None:
                    continue

                force_global_pos = (load_elem_pos.position +
                                   np.array(load.point_of_application))

                # Moment arm from element center to force point
                r = force_global_pos - elem_pos.position

                # Force vector
                F = load.get_force_vector(t)

                # Moment = r × F (cross product)
                M = np.cross(r, F)
                moment_total += M

        return moment_total

    def calculate_vdi_2230_bending(
        self,
        bolt_positions: List[np.ndarray],
        external_load: LoadApplication,
        t: float = 0.0
    ) -> Dict[int, float]:
        """
        Calculate bending moment distribution per VDI 2230 for multi-bolt joint.

        VDI 2230 methodology:
        1. Calculate centroid of bolt pattern
        2. Determine eccentricity of external load
        3. Total moment M = F × e
        4. Distribute linearly based on distance from neutral axis

        Args:
            bolt_positions: List of [x, y, z] positions for each bolt
            external_load: External load creating eccentric loading
            t: Time in seconds

        Returns:
            Dict mapping bolt index → bending moment (N·m)
        """
        if not bolt_positions:
            return {}

        # Calculate centroid of bolt pattern
        centroid = np.mean(bolt_positions, axis=0)

        # Load position (element position + point of application)
        if external_load.element_id in self.element_positions:
            load_elem_pos = self.element_positions[external_load.element_id]
            load_pos = load_elem_pos.position + np.array(external_load.point_of_application)
        else:
            load_pos = np.array(external_load.point_of_application)

        # Eccentricity (distance from load to centroid)
        e = np.linalg.norm(load_pos - centroid)

        # Total external force
        F_ext = external_load.get_force_at_time(t)

        # Total bending moment
        M_total = F_ext * e

        # Distribute to bolts based on distance from neutral axis
        moments = {}
        distances = [np.linalg.norm(pos - centroid) for pos in bolt_positions]
        max_distance = max(distances) if distances else 1.0

        for i, (pos, dist) in enumerate(zip(bolt_positions, distances)):
            # Linear distribution per VDI 2230
            M_bolt = M_total * (dist / max_distance) if max_distance > 0 else 0
            moments[i] = M_bolt

        return moments

    def check_equilibrium(self, t: float = 0.0, tolerance: float = 1e-3) -> Tuple[bool, Dict[str, float]]:
        """
        Verify force and moment equilibrium for the system.

        Checks: ΣF = 0 and ΣM = 0 (within tolerance)

        Args:
            t: Time in seconds
            tolerance: Allowable imbalance (N or N·m)

        Returns:
            Tuple of (is_balanced, summary_dict)
            summary_dict contains: sum_Fx, sum_Fy, sum_Fz, sum_Mx, sum_My, sum_Mz, is_balanced
        """
        sum_F = np.zeros(3)
        sum_M = np.zeros(3)

        # Sum all applied forces
        for load in self.applied_loads:
            if not load.active:
                continue

            if load.load_type == LoadType.POINT_FORCE:
                sum_F += load.get_force_vector(t)
            elif load.load_type == LoadType.MOMENT:
                sum_M[2] += load.get_force_at_time(t)  # Assume z-axis moment

        # Check if balanced (reactions assumed to balance if ground element present)
        # For now, just check magnitude
        force_imbalance = np.linalg.norm(sum_F)
        moment_imbalance = np.linalg.norm(sum_M)

        is_balanced = (force_imbalance < tolerance and moment_imbalance < tolerance)

        summary = {
            'sum_Fx': float(sum_F[0]),
            'sum_Fy': float(sum_F[1]),
            'sum_Fz': float(sum_F[2]),
            'sum_Mx': float(sum_M[0]),
            'sum_My': float(sum_M[1]),
            'sum_Mz': float(sum_M[2]),
            'force_imbalance': float(force_imbalance),
            'moment_imbalance': float(moment_imbalance),
            'is_balanced': is_balanced,
            'tolerance': tolerance
        }

        return is_balanced, summary

    def get_load_summary(self, t: float = 0.0) -> dict:
        """
        Get summary of all loads in the system.

        Args:
            t: Time in seconds

        Returns:
            Dict with load statistics and details
        """
        summary = {
            'n_loads': len(self.applied_loads),
            'n_active_loads': sum(1 for l in self.applied_loads if l.active),
            'n_paths': len(self.load_paths),
            'loads': []
        }

        for load in self.applied_loads:
            load_info = {
                'id': load.load_id,
                'name': load.name,
                'element_id': load.element_id,
                'type': load.load_type.name,
                'magnitude': load.magnitude,
                'magnitude_at_t': load.get_force_at_time(t),
                'direction': load.direction.name,
                'active': load.active
            }
            summary['loads'].append(load_info)

        return summary


# =============================================================================
# TIME FUNCTION PRESETS
# =============================================================================

def constant_function(amplitude: float = 1.0) -> Callable[[float], float]:
    """Constant time function (F(t) = amplitude)."""
    return lambda t: amplitude


def harmonic_function(frequency: float, amplitude: float = 1.0,
                      phase: float = 0.0) -> Callable[[float], float]:
    """
    Harmonic (sinusoidal) time function.

    F(t) = amplitude * sin(2π*f*t + phase)

    Args:
        frequency: Frequency in Hz
        amplitude: Peak amplitude (default 1.0)
        phase: Phase offset in radians (default 0)

    Returns:
        Callable F(t)
    """
    omega = 2 * np.pi * frequency
    return lambda t: amplitude * np.sin(omega * t + phase)


def ramp_function(rate: float) -> Callable[[float], float]:
    """
    Linear ramp function.

    F(t) = rate * t

    Args:
        rate: Slope of ramp (units/second)

    Returns:
        Callable F(t)
    """
    return lambda t: rate * t


def step_function(step_time: float, amplitude: float = 1.0) -> Callable[[float], float]:
    """
    Step function (Heaviside).

    F(t) = 0 for t < step_time, amplitude for t >= step_time

    Args:
        step_time: Time of step (seconds)
        amplitude: Step magnitude

    Returns:
        Callable F(t)
    """
    return lambda t: amplitude if t >= step_time else 0.0


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def create_load_from_dict(data: dict) -> LoadApplication:
    """
    Factory function to create LoadApplication from dict.

    Args:
        data: Dictionary with load parameters

    Returns:
        LoadApplication instance
    """
    return LoadApplication.from_dict(data)


class LoadPathAnalyzer:
    """
    Analyzes force distribution through a bolted joint (reference Section 47.2).

    Provides:
    - Torque component calculation (T_pitch, T_thread, T_bearing)
    - Loosening possibility check via torque balance
    - Critical friction coefficient computation
    - Force flow summary through joint components

    Usage:
        analyzer = LoadPathAnalyzer(
            preload=50000, pitch=2.0, pitch_diameter=14.701,
            flank_angle_deg=30.0, mu_thread=0.12, mu_bearing=0.12,
            bearing_inner_r=8.0, bearing_outer_r=12.0
        )
        result = analyzer.analyze_under_load(F_transverse=10000)
    """

    def __init__(self,
                 preload: float,
                 pitch: float,
                 pitch_diameter: float,
                 flank_angle_deg: float = 30.0,
                 mu_thread: float = 0.12,
                 mu_bearing: float = 0.12,
                 bearing_inner_r: float = 8.0,
                 bearing_outer_r: float = 12.0):
        """
        Args:
            preload: Bolt preload force [N]
            pitch: Thread pitch [mm]
            pitch_diameter: Thread pitch diameter [mm]
            flank_angle_deg: Thread flank half-angle [degrees]
            mu_thread: Thread friction coefficient
            mu_bearing: Bearing surface friction coefficient
            bearing_inner_r: Bearing inner radius [mm]
            bearing_outer_r: Bearing outer radius [mm]
        """
        self.preload = preload
        self.pitch = pitch
        self.d2 = pitch_diameter
        self.alpha = np.radians(flank_angle_deg)
        self.mu_thread = mu_thread
        self.mu_bearing = mu_bearing
        self.r_inner = bearing_inner_r
        self.r_outer = bearing_outer_r

        # Derived quantities
        self.helix_angle = np.arctan(pitch / (np.pi * pitch_diameter))
        self.helix_coupling = pitch / (2 * np.pi)  # λ = p/(2π)

        # Effective bearing radius: (2/3)(r_o³ - r_i³)/(r_o² - r_i²)
        if bearing_outer_r > bearing_inner_r:
            self.r_eff = (2.0 / 3.0) * (bearing_outer_r**3 - bearing_inner_r**3) / \
                         (bearing_outer_r**2 - bearing_inner_r**2)
        else:
            self.r_eff = bearing_outer_r

    def compute_torque_components(self, F_p: float = None) -> Dict[str, float]:
        """
        Compute torque balance components per reference Section 43.

        T_pitch = F_p × p/(2π)
        T_thread = μ_t × F_p × d₂/(2·cos α)
        T_bearing = μ_b × F_p × r_eff

        Returns:
            Dict with T_pitch, T_thread, T_bearing, T_resistance, margin
        """
        F_p = F_p if F_p is not None else self.preload
        cos_alpha = np.cos(self.alpha)

        T_pitch = F_p * self.pitch / (2 * np.pi)
        T_thread = self.mu_thread * F_p * self.d2 / (2 * cos_alpha)
        T_bearing = self.mu_bearing * F_p * self.r_eff
        T_resistance = T_thread + T_bearing
        margin = T_resistance / T_pitch if T_pitch > 0 else float('inf')

        return {
            'T_pitch': T_pitch,
            'T_thread': T_thread,
            'T_bearing': T_bearing,
            'T_resistance': T_resistance,
            'margin': margin,
            'is_self_locking': margin > 1.0
        }

    def compute_critical_friction(self) -> float:
        """
        Compute critical friction coefficient for self-loosening (Section 44.1).

        μ_crit = p·cos(α) / (π·d₂ + 2π·r_eff·cos(α))

        Returns:
            Critical friction coefficient below which loosening is possible
        """
        cos_alpha = np.cos(self.alpha)
        numerator = self.pitch * cos_alpha
        denominator = np.pi * self.d2 + 2 * np.pi * self.r_eff * cos_alpha
        return numerator / denominator if denominator > 0 else 0.0

    def check_slip_conditions(self, F_transverse: float,
                              F_p: float = None) -> Dict[str, bool]:
        """
        Check bearing and thread slip conditions (Section 40.1).

        Bearing slip: |F_trans| > μ_b × F_p
        Thread slip:  |F_trans| > μ_t × F_p × cos(λ)

        Returns:
            Dict with bearing_slip, thread_slip, both_slip flags
        """
        F_p = F_p if F_p is not None else self.preload
        bearing_capacity = self.mu_bearing * F_p
        thread_capacity = self.mu_thread * F_p * np.cos(self.helix_angle)

        bearing_slip = abs(F_transverse) > bearing_capacity
        thread_slip = abs(F_transverse) > thread_capacity

        return {
            'bearing_slip': bearing_slip,
            'thread_slip': thread_slip,
            'both_slip': bearing_slip and thread_slip,
            'bearing_capacity': bearing_capacity,
            'thread_capacity': thread_capacity,
            'F_transverse': abs(F_transverse),
            'bearing_utilization': abs(F_transverse) / bearing_capacity if bearing_capacity > 0 else float('inf'),
            'thread_utilization': abs(F_transverse) / thread_capacity if thread_capacity > 0 else float('inf'),
        }

    def analyze_under_load(self, F_transverse: float = 0.0,
                           F_axial_external: float = 0.0,
                           F_p: float = None) -> Dict[str, any]:
        """
        Complete load path analysis under given loading (Section 47.2).

        Args:
            F_transverse: Transverse force amplitude [N]
            F_axial_external: External axial force [N] (+ = tension)
            F_p: Current preload [N] (defaults to initial)

        Returns:
            Comprehensive analysis dict
        """
        F_p = F_p if F_p is not None else self.preload

        # Effective preload after external axial load
        F_p_eff = F_p - F_axial_external * 0.1  # Simplified load factor n = 0.1

        torques = self.compute_torque_components(F_p_eff)
        mu_crit = self.compute_critical_friction()
        slip = self.check_slip_conditions(F_transverse, F_p_eff)

        # Loosening assessment
        loosening_possible = (
            slip['both_slip'] or
            self.mu_thread < mu_crit or
            self.mu_bearing < mu_crit
        )

        # Estimated loosening rate if both surfaces slip
        loosening_rate = 0.0
        if slip['both_slip'] and torques['T_pitch'] > 0:
            excess_ratio = (abs(F_transverse) - min(slip['bearing_capacity'],
                           slip['thread_capacity'])) / (F_p_eff + 1e-10)
            loosening_rate = 0.3 * excess_ratio * self.helix_coupling / self.d2

        return {
            'preload_effective': F_p_eff,
            'torque_components': torques,
            'critical_friction': mu_crit,
            'slip_conditions': slip,
            'loosening_possible': loosening_possible,
            'estimated_loosening_rate_rad_per_cycle': loosening_rate,
            'mu_thread': self.mu_thread,
            'mu_bearing': self.mu_bearing,
            'helix_angle_deg': np.degrees(self.helix_angle),
            'helix_coupling_mm': self.helix_coupling,
        }


def estimate_element_positions_from_chain(
    elements: List,
    start_position: np.ndarray = None
) -> Dict[int, ElementPosition]:
    """
    Estimate element positions for a series chain of elements.

    Args:
        elements: List of element objects with .element_id and .k attributes
        start_position: Starting [x, y, z] position (default origin)

    Returns:
        Dict mapping element_id → ElementPosition
    """
    if start_position is None:
        start_position = np.array([0.0, 0.0, 0.0])

    positions = {}
    z_pos = start_position[2]

    for elem in elements:
        # Estimate length from stiffness (k = EA/L → L = EA/k)
        # Typical values: E = 205 GPa, A = 200 mm² = 2e-4 m²
        E = 205e9  # Pa
        A = 2e-4  # m²

        if hasattr(elem, 'k') and elem.k > 0:
            length = E * A / elem.k
        else:
            length = 0.01  # Default 10 mm

        # Limit reasonable range
        length = np.clip(length, 0.001, 1.0)  # 1 mm to 1 m

        # Position at center of element
        pos = ElementPosition(
            element_id=elem.element_id,
            position=np.array([0.0, 0.0, z_pos + length/2]),
            orientation=np.eye(3),
            length=length
        )
        positions[elem.element_id] = pos

        z_pos += length

    return positions
