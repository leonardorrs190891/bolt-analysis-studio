"""
Load Distribution Module for Multi-Bolt Joints

Implements VDI 2230 Part 1 (2015) methodology for distributing
external loads and bending moments across multiple bolts in a pattern.

Features:
- Centroid calculation for bolt patterns
- Bending moment distribution (linear with distance from neutral axis)
- Load factor calculation per bolt
- Pattern type detection (single, linear, circular, rectangular)

Author: Bolt Analysis Studio Team
Date: February 2026
"""

import numpy as np
from typing import List, Tuple, Dict, Optional
from dataclasses import dataclass
from enum import Enum, auto


class PatternType(Enum):
    """Bolt pattern types."""
    SINGLE = auto()
    LINEAR = auto()
    CIRCULAR = auto()
    RECTANGULAR = auto()
    CUSTOM = auto()


@dataclass
class BoltPosition:
    """Position of a bolt in the pattern."""
    bolt_id: int
    x: float  # [m]
    y: float  # [m]
    z: float = 0.0  # [m] (typically 0 for flange face)


@dataclass
class BoltLoadFactors:
    """Load factors for a single bolt."""
    bolt_id: int
    axial_factor: float  # Fraction of total axial load
    moment_x_factor: float  # Fraction of bending moment about x-axis
    moment_y_factor: float  # Fraction of bending moment about y-axis
    distance_from_centroid: float  # [m]


class VDI2230LoadDistributor:
    """
    Distributes loads to bolts per VDI 2230 Part 1 Section 5.5.

    VDI 2230 Key Principles:
    1. Axial Force: Distributed equally or by stiffness ratio
    2. Bending Moment: Distributed linearly with distance from neutral axis
    3. Eccentric Load: Creates bending moment M = F × e
    4. Multi-bolt: Each bolt takes portion based on position
    """

    def __init__(self, bolt_positions: List[BoltPosition]):
        """
        Initialize distributor with bolt pattern.

        Args:
            bolt_positions: List of bolt positions in pattern
        """
        self.bolts = bolt_positions
        self.n_bolts = len(bolt_positions)

        if self.n_bolts == 0:
            raise ValueError("At least one bolt position required")

        # Calculate pattern properties
        self.centroid = self._calculate_centroid()
        self.pattern_type = self._detect_pattern_type()
        self.distances_from_centroid = self._calculate_distances()

    def _calculate_centroid(self) -> Tuple[float, float, float]:
        """
        Calculate centroid of bolt pattern.

        Returns:
            (x_c, y_c, z_c) coordinates [m]
        """
        x_c = np.mean([b.x for b in self.bolts])
        y_c = np.mean([b.y for b in self.bolts])
        z_c = np.mean([b.z for b in self.bolts])

        return (x_c, y_c, z_c)

    def _detect_pattern_type(self) -> PatternType:
        """Detect bolt pattern type from positions."""
        if self.n_bolts == 1:
            return PatternType.SINGLE

        # Check if linear (all bolts in a line)
        if self.n_bolts >= 2:
            # Simple check: if all y-coordinates are same, it's linear along x
            y_coords = [b.y for b in self.bolts]
            if np.allclose(y_coords, y_coords[0], atol=1e-6):
                return PatternType.LINEAR

        # Check if circular (equidistant from center)
        distances = self._calculate_distances()
        if np.allclose(distances, distances[0], atol=1e-3):
            return PatternType.CIRCULAR

        # Check if rectangular grid
        x_unique = len(set(round(b.x, 6) for b in self.bolts))
        y_unique = len(set(round(b.y, 6) for b in self.bolts))
        if x_unique >= 2 and y_unique >= 2:
            return PatternType.RECTANGULAR

        return PatternType.CUSTOM

    def _calculate_distances(self) -> np.ndarray:
        """
        Calculate distance of each bolt from centroid.

        Returns:
            Array of distances [m]
        """
        x_c, y_c, z_c = self.centroid
        distances = []

        for bolt in self.bolts:
            dx = bolt.x - x_c
            dy = bolt.y - y_c
            dz = bolt.z - z_c
            distance = np.sqrt(dx**2 + dy**2 + dz**2)
            distances.append(distance)

        return np.array(distances)

    def distribute_axial_load(self, F_axial: float,
                              uniform: bool = True) -> Dict[int, float]:
        """
        Distribute axial force to bolts.

        Per VDI 2230 Section 5.5.2:
        - Uniform: Each bolt gets F/n
        - Stiffness-based: Each bolt gets F × (k_i / k_total)

        Args:
            F_axial: Total axial force [N]
            uniform: If True, equal distribution; if False, by stiffness

        Returns:
            Dict mapping bolt_id → axial force [N]
        """
        if uniform:
            # Equal distribution
            F_per_bolt = F_axial / self.n_bolts
            return {bolt.bolt_id: F_per_bolt for bolt in self.bolts}
        else:
            # TODO: Implement stiffness-based distribution
            # For now, fall back to uniform
            F_per_bolt = F_axial / self.n_bolts
            return {bolt.bolt_id: F_per_bolt for bolt in self.bolts}

    def distribute_bending_moment(self, M_x: float = 0.0, M_y: float = 0.0,
                                  M_z: float = 0.0) -> Dict[int, float]:
        """
        Distribute bending moment to bolts per VDI 2230.

        Per VDI 2230 Section 5.5.3:
        F_i = (M × r_i) / Σ(r_j²)

        Where:
        - M: Bending moment [N·m]
        - r_i: Distance of bolt i from neutral axis [m]
        - F_i: Additional axial force on bolt i [N]

        Args:
            M_x: Bending moment about x-axis [N·m]
            M_y: Bending moment about y-axis [N·m]
            M_z: Torsional moment about z-axis [N·m]

        Returns:
            Dict mapping bolt_id → additional axial force [N]
        """
        x_c, y_c, z_c = self.centroid

        # Calculate position vectors relative to centroid
        r_vectors = []
        for bolt in self.bolts:
            r_x = bolt.x - x_c
            r_y = bolt.y - y_c
            r_vectors.append((r_x, r_y))

        # Calculate moment of inertia terms
        I_xx = sum(r_y**2 for _, r_y in r_vectors)  # Σ(y_i²)
        I_yy = sum(r_x**2 for r_x, _ in r_vectors)  # Σ(x_i²)
        I_xy = sum(r_x * r_y for r_x, r_y in r_vectors)  # Σ(x_i × y_i)

        # Avoid division by zero
        if I_xx < 1e-12 or I_yy < 1e-12:
            # Degenerate pattern (all bolts at centroid)
            return {bolt.bolt_id: 0.0 for bolt in self.bolts}

        # Calculate additional force per bolt from bending
        bolt_forces = {}

        for bolt, (r_x, r_y) in zip(self.bolts, r_vectors):
            # Force from moment about y-axis (in-plane)
            # F_i = M_y × (x_i - x_c) / I_yy
            F_from_M_y = (M_y * r_x / I_yy) if I_yy > 0 else 0.0

            # Force from moment about x-axis (in-plane)
            # F_i = -M_x × (y_i - y_c) / I_xx
            F_from_M_x = (-M_x * r_y / I_xx) if I_xx > 0 else 0.0

            # Total additional force (tension positive)
            F_total = F_from_M_x + F_from_M_y

            bolt_forces[bolt.bolt_id] = F_total

        return bolt_forces

    def distribute_eccentric_load(self, F_x: float = 0.0, F_y: float = 0.0,
                                  F_z: float = 0.0,
                                  load_point: Tuple[float, float, float] = (0, 0, 0)
                                  ) -> Dict[int, Dict[str, float]]:
        """
        Distribute eccentric load to bolts.

        Eccentric load creates both direct force and bending moment:
        M = F × e (eccentricity)

        Args:
            F_x: Force in x-direction [N]
            F_y: Force in y-direction [N]
            F_z: Force in z-direction (axial) [N]
            load_point: Point of load application (x, y, z) [m]

        Returns:
            Dict mapping bolt_id → {'axial': F_axial, 'shear_x': F_x, 'shear_y': F_y} [N]
        """
        x_c, y_c, z_c = self.centroid
        x_load, y_load, z_load = load_point

        # Eccentricities
        e_x = x_load - x_c
        e_y = y_load - y_c
        e_z = z_load - z_c

        # Induced bending moments
        M_x = F_z * e_y  # Axial force with y-eccentricity → bending about x
        M_y = -F_z * e_x  # Axial force with x-eccentricity → bending about y

        # Distribute axial load
        F_axial_dist = self.distribute_axial_load(F_z, uniform=True)

        # Distribute bending
        F_bending_dist = self.distribute_bending_moment(M_x=M_x, M_y=M_y)

        # Distribute shear (uniform)
        F_x_per_bolt = F_x / self.n_bolts
        F_y_per_bolt = F_y / self.n_bolts

        # Combine results
        bolt_loads = {}
        for bolt in self.bolts:
            bolt_id = bolt.bolt_id
            bolt_loads[bolt_id] = {
                'axial': F_axial_dist[bolt_id] + F_bending_dist[bolt_id],
                'shear_x': F_x_per_bolt,
                'shear_y': F_y_per_bolt,
                'total_resultant': np.sqrt(
                    (F_axial_dist[bolt_id] + F_bending_dist[bolt_id])**2 +
                    F_x_per_bolt**2 +
                    F_y_per_bolt**2
                )
            }

        return bolt_loads

    def get_load_factors(self) -> List[BoltLoadFactors]:
        """
        Get load factors for all bolts (for 1 N of load).

        Returns load distribution coefficients that can be scaled
        by actual load magnitude.

        Returns:
            List of BoltLoadFactors for each bolt
        """
        # Unit axial load distribution
        axial_dist = self.distribute_axial_load(1.0, uniform=True)

        # Unit bending distribution
        moment_x_dist = self.distribute_bending_moment(M_x=1.0, M_y=0.0)
        moment_y_dist = self.distribute_bending_moment(M_x=0.0, M_y=1.0)

        factors = []
        for i, bolt in enumerate(self.bolts):
            factors.append(BoltLoadFactors(
                bolt_id=bolt.bolt_id,
                axial_factor=axial_dist[bolt.bolt_id],
                moment_x_factor=moment_x_dist[bolt.bolt_id],
                moment_y_factor=moment_y_dist[bolt.bolt_id],
                distance_from_centroid=self.distances_from_centroid[i]
            ))

        return factors

    def get_summary(self) -> Dict:
        """Get summary of bolt pattern and distribution."""
        return {
            'n_bolts': self.n_bolts,
            'pattern_type': self.pattern_type.name,
            'centroid': self.centroid,
            'max_distance_from_centroid': float(np.max(self.distances_from_centroid)),
            'bolt_positions': [
                {'id': b.bolt_id, 'x': b.x, 'y': b.y, 'z': b.z}
                for b in self.bolts
            ]
        }


# Factory function for common patterns
def create_circular_pattern(n_bolts: int, radius: float,
                           start_angle: float = 0.0) -> List[BoltPosition]:
    """
    Create circular bolt pattern.

    Args:
        n_bolts: Number of bolts
        radius: Bolt circle radius [m]
        start_angle: Starting angle [degrees]

    Returns:
        List of BoltPosition objects
    """
    positions = []
    angle_step = 360.0 / n_bolts

    for i in range(n_bolts):
        angle_deg = start_angle + i * angle_step
        angle_rad = np.radians(angle_deg)

        x = radius * np.cos(angle_rad)
        y = radius * np.sin(angle_rad)

        positions.append(BoltPosition(bolt_id=i, x=x, y=y))

    return positions


def create_rectangular_pattern(n_x: int, n_y: int,
                               spacing_x: float, spacing_y: float) -> List[BoltPosition]:
    """
    Create rectangular grid pattern.

    Args:
        n_x: Number of bolts in x-direction
        n_y: Number of bolts in y-direction
        spacing_x: Spacing in x-direction [m]
        spacing_y: Spacing in y-direction [m]

    Returns:
        List of BoltPosition objects
    """
    positions = []
    bolt_id = 0

    for i in range(n_x):
        for j in range(n_y):
            x = i * spacing_x
            y = j * spacing_y
            positions.append(BoltPosition(bolt_id=bolt_id, x=x, y=y))
            bolt_id += 1

    return positions


def create_linear_pattern(n_bolts: int, spacing: float) -> List[BoltPosition]:
    """
    Create linear bolt pattern along x-axis.

    Args:
        n_bolts: Number of bolts
        spacing: Spacing between bolts [m]

    Returns:
        List of BoltPosition objects
    """
    positions = []

    for i in range(n_bolts):
        x = i * spacing
        positions.append(BoltPosition(bolt_id=i, x=x, y=0.0))

    return positions
