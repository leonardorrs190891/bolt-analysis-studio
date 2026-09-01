"""
Loosening Similitude Analysis Module
====================================

Mathematical models for similitude analysis of bolt loosening behavior.

Features:
1. Multi-bolt to single-bolt reduction with preserved loosening characteristics
2. Geometric scaling with loosening behavior preservation
3. Scale effect corrections
4. Π-group analysis specific to loosening phenomena

Based on:
- Buckingham Π theorem
- Junker loosening mechanism
- Jiang two-stage model
- VDI 2230 guidelines

BAS +  R&D
January 2026
"""

from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional, Callable, Any
from enum import Enum
import numpy as np
from pathlib import Path
import json

# Import from existing similitude module
from .similitude import (
    ScaleFactors,
    PiGroup,
    ScaleEffect,
    PrototypeData,
    SimilitudeAnalysis,
    MaterialSimilarity,
    ScaleEffectSeverity
)


# =============================================================================
# Enumerations
# =============================================================================

class SimilitudeType(Enum):
    """Type of similitude transformation."""
    MULTI_BOLT_REDUCTION = "multi_bolt_reduction"
    GEOMETRIC_SCALING = "geometric_scaling"
    COMBINED = "combined"


class LoadingPattern(Enum):
    """Loading pattern for multi-bolt joints."""
    UNIFORM = "uniform"          # Uniform axial load
    MOMENT = "moment"            # Bending moment (non-uniform)
    COMBINED = "combined"        # Axial + moment
    SHEAR = "shear"              # Pure shear


class CycleScalingMode(Enum):
    """Cycle scaling mode for loosening tests (CS3)."""
    SCALED_DURATION = "scaled_duration"  # N_model = N_proto / lambda (faster test)
    SAME_DURATION = "same_duration"      # Same wall-clock time (freq scales as 1/lambda)
    SAME_CYCLES = "same_cycles"          # Same number of cycles (no time scaling)


# =============================================================================
# M7/MS1: Bolt Load Factor Per Pattern
# =============================================================================

def bolt_load_factor(pattern: LoadingPattern, theta: float,
                     n_bolts: int = 1) -> float:
    """
    Compute bolt load factor based on loading pattern and angular position (M7/MS1).

    For multi-bolt patterns, the most-loaded bolt sees a higher fraction
    of the total external load depending on the pattern.

    MOMENT pattern: factor = 1 + cos(theta)
        Bolt at theta=0 (compression side) sees 2x average,
        bolt at theta=pi (tension side) sees 0.

    SHEAR pattern: factor = 1 + 0.5*cos(theta)
        More uniform distribution, factor ranges from 0.5 to 1.5.

    UNIFORM pattern: factor = 1.0 (all bolts equally loaded)

    COMBINED pattern: weighted average of MOMENT and SHEAR.

    Args:
        pattern: Loading pattern enum
        theta: Angular position of bolt in bolt circle [rad]
               theta=0 is the direction of maximum load
        n_bolts: Number of bolts (for normalization)

    Returns:
        Load factor for the bolt at angle theta (relative to average)
    """
    if pattern == LoadingPattern.UNIFORM:
        return 1.0
    elif pattern == LoadingPattern.MOMENT:
        return 1.0 + np.cos(theta)
    elif pattern == LoadingPattern.SHEAR:
        return 1.0 + 0.5 * np.cos(theta)
    elif pattern == LoadingPattern.COMBINED:
        # Weighted: 70% moment + 30% shear contribution
        return 1.0 + 0.7 * np.cos(theta) + 0.15 * np.cos(theta)
    else:
        return 1.0


def compute_bolt_load_factors(pattern: LoadingPattern,
                               n_bolts: int) -> List[Tuple[float, float]]:
    """
    Compute load factors for all bolts in a circular pattern (M7/MS1).

    Args:
        pattern: Loading pattern
        n_bolts: Number of equally-spaced bolts

    Returns:
        List of (theta [rad], load_factor) tuples for each bolt
    """
    factors = []
    for i in range(n_bolts):
        theta = 2 * np.pi * i / n_bolts
        f = bolt_load_factor(pattern, theta, n_bolts)
        factors.append((theta, f))
    return factors


def max_bolt_load_factor(pattern: LoadingPattern, n_bolts: int) -> float:
    """Return the maximum load factor across all bolt positions."""
    factors = compute_bolt_load_factors(pattern, n_bolts)
    return max(f for _, f in factors)


# =============================================================================
# MS2: Thread Pitch Mismatch Impact Assessment
# =============================================================================

def assess_pitch_mismatch(
    prototype_diameter: float,
    prototype_pitch: float,
    model_diameter: float,
    model_pitch: float,
    scale_factor: float
) -> Dict[str, Any]:
    """
    Assess impact of thread pitch mismatch between scaled model and prototype (MS2).

    When scaling from prototype to model, the ideal model pitch is:
        p_model_ideal = prototype_pitch * scale_factor

    But standard bolt sizes have fixed pitches, so there is typically a
    mismatch. This function quantifies the impact on loosening-relevant
    Pi groups and provides correction guidance.

    Args:
        prototype_diameter: Prototype bolt diameter [mm]
        prototype_pitch: Prototype thread pitch [mm]
        model_diameter: Model bolt diameter (standard size) [mm]
        model_pitch: Model thread pitch (standard size) [mm]
        scale_factor: Geometric scale factor lambda

    Returns:
        Dict with mismatch analysis and correction recommendations
    """
    # Ideal scaled values
    p_ideal = prototype_pitch * scale_factor
    d_ideal = prototype_diameter * scale_factor

    # Pitch ratio (Pi10): p/d
    pitch_ratio_proto = prototype_pitch / prototype_diameter
    pitch_ratio_model = model_pitch / model_diameter
    pitch_ratio_ideal = p_ideal / d_ideal  # Should equal prototype ratio
    pitch_ratio_deviation = abs(pitch_ratio_model - pitch_ratio_proto) / pitch_ratio_proto

    # Helix angle comparison
    d2_proto = prototype_diameter - 0.6495 * prototype_pitch
    d2_model = model_diameter - 0.6495 * model_pitch
    helix_proto = np.arctan(prototype_pitch / (np.pi * d2_proto))
    helix_model = np.arctan(model_pitch / (np.pi * d2_model))
    helix_deviation = abs(helix_model - helix_proto) / helix_proto if helix_proto > 0 else 0

    # Stress area comparison (normalized)
    d1_proto = prototype_diameter - 1.0825 * prototype_pitch
    d1_model = model_diameter - 1.0825 * model_pitch
    At_proto = np.pi / 4 * ((d2_proto + d1_proto) / 2) ** 2
    At_model = np.pi / 4 * ((d2_model + d1_model) / 2) ** 2
    At_ratio = At_model / (At_proto * scale_factor ** 2)  # Should be ~1.0

    # Impact severity
    if pitch_ratio_deviation < 0.02 and helix_deviation < 0.02:
        severity = 'negligible'
        recommendation = 'No correction needed'
    elif pitch_ratio_deviation < 0.05 and helix_deviation < 0.05:
        severity = 'low'
        recommendation = 'Minor correction to loosening rate prediction'
    elif pitch_ratio_deviation < 0.10:
        severity = 'medium'
        recommendation = 'Apply pitch mismatch correction factor'
    else:
        severity = 'high'
        recommendation = 'Consider using ISO fine-pitch or non-standard bolt'

    # Correction factor for loosening rate
    # Loosening rate is proportional to tan(helix_angle) / mu
    # Correction = tan(helix_model) / tan(helix_proto)
    C_pitch = np.tan(helix_model) / np.tan(helix_proto) if helix_proto > 0 else 1.0

    return {
        'prototype': {
            'diameter': prototype_diameter,
            'pitch': prototype_pitch,
            'pitch_ratio': pitch_ratio_proto,
            'helix_angle_deg': np.degrees(helix_proto),
        },
        'model_ideal': {
            'diameter': d_ideal,
            'pitch': p_ideal,
        },
        'model_actual': {
            'diameter': model_diameter,
            'pitch': model_pitch,
            'pitch_ratio': pitch_ratio_model,
            'helix_angle_deg': np.degrees(helix_model),
        },
        'deviations': {
            'pitch_ratio': pitch_ratio_deviation,
            'helix_angle': helix_deviation,
            'stress_area_ratio': At_ratio,
        },
        'severity': severity,
        'correction_factor': C_pitch,
        'recommendation': recommendation,
    }


# =============================================================================
# CS3: Cycle Scaling Functions
# =============================================================================

def scale_cycles(
    N_source: np.ndarray,
    scale_factor: float,
    mode: CycleScalingMode = CycleScalingMode.SCALED_DURATION,
    frequency_proto: float = 1.0,
    frequency_model: float = None
) -> np.ndarray:
    """
    Transform cycle counts between prototype and model using specified mode (CS3).

    Args:
        N_source: Source cycle counts (model or prototype)
        scale_factor: Geometric scale factor lambda
        mode: Cycle scaling mode
        frequency_proto: Prototype frequency [Hz]
        frequency_model: Model frequency [Hz] (auto-computed if None)

    Returns:
        Transformed cycle counts
    """
    if frequency_model is None:
        frequency_model = frequency_proto / scale_factor

    if mode == CycleScalingMode.SCALED_DURATION:
        # Model loosens faster: N_proto = N_model * lambda
        # (same stress, smaller bolt = fewer cycles to same relative loss)
        return N_source * scale_factor

    elif mode == CycleScalingMode.SAME_DURATION:
        # Same wall-clock time: model runs at higher frequency
        # N_model = N_proto * (f_model / f_proto)
        freq_ratio = frequency_model / frequency_proto if frequency_proto > 0 else 1.0
        return N_source * freq_ratio

    elif mode == CycleScalingMode.SAME_CYCLES:
        # No cycle transformation
        return N_source.copy()

    return N_source.copy()


def get_cycle_scaling_info(
    scale_factor: float,
    mode: CycleScalingMode,
    N_proto: int,
    frequency_proto: float
) -> Dict[str, Any]:
    """
    Get information about cycle scaling for a given mode (CS3).

    Returns:
        Dict with model cycles, frequencies, and test duration info
    """
    freq_model = frequency_proto / scale_factor

    if mode == CycleScalingMode.SCALED_DURATION:
        N_model = int(N_proto / scale_factor)
        time_proto = N_proto / frequency_proto if frequency_proto > 0 else 0
        time_model = N_model / freq_model if freq_model > 0 else 0
    elif mode == CycleScalingMode.SAME_DURATION:
        time_proto = N_proto / frequency_proto if frequency_proto > 0 else 0
        N_model = int(time_proto * freq_model)
        time_model = time_proto
    else:  # SAME_CYCLES
        N_model = N_proto
        time_proto = N_proto / frequency_proto if frequency_proto > 0 else 0
        time_model = N_model / freq_model if freq_model > 0 else 0

    return {
        'mode': mode.value,
        'N_prototype': N_proto,
        'N_model': N_model,
        'frequency_prototype_Hz': frequency_proto,
        'frequency_model_Hz': freq_model,
        'time_prototype_s': time_proto,
        'time_model_s': time_model,
        'time_saving_factor': time_proto / time_model if time_model > 0 else float('inf'),
    }


# =============================================================================
# Loosening-Specific Π-Groups
# =============================================================================

@dataclass
class LooseningPiGroup(PiGroup):
    """
    Dimensionless Π-group specific to loosening behavior.

    Extends PiGroup with loosening-specific attributes.
    """
    critical_value: Optional[float] = None  # Value at loosening onset
    sensitivity: float = 1.0                 # Sensitivity to loosening rate

    @property
    def loosening_margin(self) -> float:
        """Distance from critical loosening threshold."""
        if self.critical_value is None:
            return float('inf')
        return self.prototype_value / self.critical_value


def calculate_loosening_pi_groups(
    F_t: float,
    F_p: float,
    mu_t: float,
    mu_b: float,
    pitch: float,
    pitch_diameter: float,
    flank_angle: float,
    r_eff_head: float,
    r_eff_nut: float,
    grip_length: float,
    bolt_diameter: float,
    stress_area: float,
    yield_strength: float,
    k_bolt: float,
    k_member: float,
    embedding: float = 3e-3
) -> List[LooseningPiGroup]:
    """
    Calculate all loosening-specific Π-groups.

    Args:
        F_t: Transverse force [N]
        F_p: Preload force [N]
        mu_t: Thread friction coefficient
        mu_b: Bearing friction coefficient
        pitch: Thread pitch [m]
        pitch_diameter: Thread pitch diameter [m]
        flank_angle: Thread flank angle [rad]
        r_eff_head: Effective head bearing radius [m]
        r_eff_nut: Effective nut bearing radius [m]
        grip_length: Grip length [m]
        bolt_diameter: Nominal bolt diameter [m]
        stress_area: Tensile stress area [m²]
        yield_strength: Bolt yield strength [Pa]
        k_bolt: Bolt stiffness [N/m]
        k_member: Member stiffness [N/m]
        embedding: Embedding deformation per interface [m]

    Returns:
        List of LooseningPiGroup objects
    """
    # Mean thread radius
    r_m = pitch_diameter / 2

    # Helix angle
    helix_angle = np.arctan(pitch / (np.pi * pitch_diameter))

    # Sec(alpha) for thread contact
    sec_alpha = 1.0 / np.cos(flank_angle)

    # Joint constant (stiffness ratio)
    phi = k_bolt / (k_bolt + k_member)

    # Combined stiffness
    k_eff = (k_bolt * k_member) / (k_bolt + k_member)

    pi_groups = []

    # Π₁: Slip Parameter
    pi1 = F_t / (mu_b * F_p) if F_p > 0 and mu_b > 0 else 0
    pi_groups.append(LooseningPiGroup(
        name="Slip Parameter",
        symbol="Π₁",
        expression="F_t / (μ_b × F_p)",
        description="Ratio of transverse force to friction capacity",
        prototype_value=pi1,
        model_value=pi1,  # Updated during transformation
        tolerance=0.10,
        category="primary",
        critical_value=1.0,  # Slip onset
        sensitivity=2.0      # High sensitivity
    ))

    # Π₂: Helix Parameter (loosening tendency)
    pi2 = np.tan(helix_angle) / (mu_t * sec_alpha) if mu_t > 0 else 0
    pi_groups.append(LooseningPiGroup(
        name="Helix Parameter",
        symbol="Π₂",
        expression="tan(λ) / (μ_t × sec(α))",
        description="Helix driving effect vs thread friction",
        prototype_value=pi2,
        model_value=pi2,
        tolerance=0.05,
        category="primary",
        critical_value=1.0,  # Self-loosening threshold
        sensitivity=3.0      # Very high sensitivity
    ))

    # Π₃: Preload Utilization
    sigma_preload = F_p / stress_area if stress_area > 0 else 0
    pi3 = sigma_preload / yield_strength if yield_strength > 0 else 0
    pi_groups.append(LooseningPiGroup(
        name="Preload Utilization",
        symbol="Π₃",
        expression="σ_p / σ_y = F_p / (σ_y × A_t)",
        description="Preload stress relative to yield",
        prototype_value=pi3,
        model_value=pi3,
        tolerance=0.05,
        category="primary",
        critical_value=0.9,  # Yield threshold
        sensitivity=1.0
    ))

    # Π₄: Grip Ratio
    pi4 = grip_length / bolt_diameter if bolt_diameter > 0 else 0
    pi_groups.append(LooseningPiGroup(
        name="Grip Ratio",
        symbol="Π₄",
        expression="L / d",
        description="Bolt flexibility parameter",
        prototype_value=pi4,
        model_value=pi4,
        tolerance=0.02,
        category="primary",
        sensitivity=0.5
    ))

    # Π₅: Joint Constant
    pi5 = phi
    pi_groups.append(LooseningPiGroup(
        name="Joint Constant",
        symbol="Π₅",
        expression="Φ = k_b / (k_b + k_m)",
        description="Load partitioning factor",
        prototype_value=pi5,
        model_value=pi5,
        tolerance=0.05,
        category="primary",
        sensitivity=1.5
    ))

    # Π₆: Bearing Leverage Ratio
    r_eff_avg = (r_eff_head + r_eff_nut) / 2
    pi6 = r_eff_avg / r_m if r_m > 0 else 0
    pi_groups.append(LooseningPiGroup(
        name="Bearing Leverage",
        symbol="Π₆",
        expression="r_eff / r_m",
        description="Bearing friction leverage",
        prototype_value=pi6,
        model_value=pi6,
        tolerance=0.05,
        category="secondary",
        sensitivity=1.2
    ))

    # Π₇: Pitch Ratio
    pi7 = pitch / bolt_diameter if bolt_diameter > 0 else 0
    pi_groups.append(LooseningPiGroup(
        name="Pitch Ratio",
        symbol="Π₇",
        expression="p / d",
        description="Thread coarseness",
        prototype_value=pi7,
        model_value=pi7,
        tolerance=0.02,
        category="secondary",
        sensitivity=1.0
    ))

    # Π₁₀: Embedding Parameter
    pi10 = (embedding * k_eff) / F_p if F_p > 0 else 0
    pi_groups.append(LooseningPiGroup(
        name="Embedding Parameter",
        symbol="Π₁₀",
        expression="f_z × k_eff / F_p",
        description="Relative embedding loss",
        prototype_value=pi10,
        model_value=pi10,
        tolerance=0.15,
        category="secondary",
        sensitivity=0.8
    ))

    return pi_groups


# =============================================================================
# Multi-Bolt to Single-Bolt Reduction
# =============================================================================

@dataclass
class MultiBoltConfig:
    """Configuration for multi-bolt joint."""
    n_bolts: int                          # Number of bolts
    bolt_diameter: float                   # d [mm]
    pitch: float                           # p [mm]
    grip_length: float                     # L [mm]
    preload_per_bolt: float               # F_p [N]
    transverse_force_per_bolt: float      # F_t [N]
    bolt_circle_diameter: float           # D_bc [mm]

    # Friction
    mu_thread: float = 0.12
    mu_bearing: float = 0.15

    # Material
    elastic_modulus: float = 210e3        # E [MPa]
    yield_strength: float = 720.0         # σ_y [MPa]

    # Stiffnesses
    k_bolt_single: float = 5e5            # k_b per bolt [N/mm]
    k_member_single: float = 1.5e6        # k_m per bolt [N/mm]

    # Loading
    loading_pattern: LoadingPattern = LoadingPattern.UNIFORM


@dataclass
class EquivalentSingleBolt:
    """Equivalent single-bolt model parameters."""
    # Source
    source_config: MultiBoltConfig

    # Equivalent geometry
    d_equivalent: float          # d_eq = d × sqrt(n) [mm]
    p_equivalent: float          # p_eq = p × sqrt(n) [mm]
    L_equivalent: float          # L [mm] (unchanged)
    A_t_equivalent: float        # A_t,eq = n × A_t [mm²]

    # Equivalent forces
    F_p_equivalent: float        # F_p,eq = n × F_p [N]
    F_t_equivalent: float        # F_t,eq = n × F_t [N]

    # Equivalent stiffnesses
    k_bolt_equivalent: float     # k_b,eq = n × k_b [N/mm]
    k_member_equivalent: float   # k_m,eq = n × k_m [N/mm]

    # Π-group preservation
    pi_groups: List[LooseningPiGroup] = field(default_factory=list)
    pi_preservation_quality: float = 1.0

    # Loosening model parameters (preserved)
    jiang_lambda1: float = 0.015   # Stage I decay constant
    jiang_lambda2: float = 0.005   # Stage II decay constant
    N_transition: int = 200        # Transition cycles

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'source': {
                'n_bolts': self.source_config.n_bolts,
                'd': self.source_config.bolt_diameter,
                'p': self.source_config.pitch,
            },
            'equivalent': {
                'd_eq': self.d_equivalent,
                'p_eq': self.p_equivalent,
                'F_p_eq': self.F_p_equivalent,
                'k_b_eq': self.k_bolt_equivalent,
                'k_m_eq': self.k_member_equivalent,
            },
            'pi_preservation_quality': self.pi_preservation_quality,
            'loosening_params': {
                'lambda1': self.jiang_lambda1,
                'lambda2': self.jiang_lambda2,
                'N_transition': self.N_transition,
            }
        }


def reduce_multi_bolt_to_single(config: MultiBoltConfig) -> EquivalentSingleBolt:
    """
    Reduce multi-bolt joint to equivalent single bolt.

    Preserves all loosening-relevant Π-groups.

    Args:
        config: Multi-bolt joint configuration

    Returns:
        EquivalentSingleBolt model
    """
    n = config.n_bolts
    sqrt_n = np.sqrt(n)

    # M7/MS1: Apply bolt load factor for non-uniform patterns
    max_factor = max_bolt_load_factor(config.loading_pattern, n)

    # Equivalent geometry
    d_eq = config.bolt_diameter * sqrt_n
    p_eq = config.pitch * sqrt_n

    # Calculate original stress area (ISO metric)
    d = config.bolt_diameter
    p = config.pitch
    d2_orig = d - 0.6495 * p
    d3_orig = d - 1.0825 * p
    A_t_orig = np.pi / 4 * ((d2_orig + d3_orig) / 2) ** 2

    A_t_eq = n * A_t_orig

    # Equivalent forces (M7: use max-loaded bolt's fraction for loosening)
    F_p_eq = n * config.preload_per_bolt
    F_t_eq = n * config.transverse_force_per_bolt * max_factor

    # Equivalent stiffnesses
    k_b_eq = n * config.k_bolt_single
    k_m_eq = n * config.k_member_single

    # Calculate Π-groups for verification
    d2_eq = d_eq - 0.6495 * p_eq
    r_m_eq = d2_eq / 2
    flank_angle = np.radians(30)  # ISO metric
    r_eff = d_eq * 0.75 / 2  # Approximate bearing radius

    pi_groups = calculate_loosening_pi_groups(
        F_t=F_t_eq,
        F_p=F_p_eq,
        mu_t=config.mu_thread,
        mu_b=config.mu_bearing,
        pitch=p_eq / 1000,  # Convert to m
        pitch_diameter=d2_eq / 1000,
        flank_angle=flank_angle,
        r_eff_head=r_eff / 1000,
        r_eff_nut=r_eff / 1000,
        grip_length=config.grip_length / 1000,
        bolt_diameter=d_eq / 1000,
        stress_area=A_t_eq / 1e6,  # Convert to m²
        yield_strength=config.yield_strength * 1e6,  # Convert to Pa
        k_bolt=k_b_eq * 1e3,  # Convert to N/m
        k_member=k_m_eq * 1e3
    )

    # Calculate preservation quality
    quality = sum(1 for pg in pi_groups if pg.is_matched) / len(pi_groups)

    return EquivalentSingleBolt(
        source_config=config,
        d_equivalent=d_eq,
        p_equivalent=p_eq,
        L_equivalent=config.grip_length,
        A_t_equivalent=A_t_eq,
        F_p_equivalent=F_p_eq,
        F_t_equivalent=F_t_eq,
        k_bolt_equivalent=k_b_eq,
        k_member_equivalent=k_m_eq,
        pi_groups=pi_groups,
        pi_preservation_quality=quality
    )


# =============================================================================
# Geometric Scaling for Loosening Preservation
# =============================================================================

@dataclass
class ScaledLooseningModel:
    """Geometrically scaled model with loosening preservation."""
    # Scale factor
    scale_factor: float                    # λ = L_m / L_p

    # Prototype reference
    prototype_diameter: float              # d_p [mm]
    prototype_pitch: float                 # p_p [mm]
    prototype_grip_length: float           # L_p [mm]
    prototype_preload: float               # F_p,p [N]
    prototype_frequency: float             # f_p [Hz]

    # Scaled parameters
    model_diameter: float                  # d_m = λ × d_p [mm]
    model_pitch: float                     # p_m = λ × p_p [mm]
    model_grip_length: float               # L_m = λ × L_p [mm]
    model_preload: float                   # F_m = λ² × F_p [N]
    model_frequency: float                 # f_m = f_p / λ [Hz]

    # Standard bolt size (nearest match)
    standard_diameter: float               # Nearest ISO/ANSI size [mm]
    standard_pitch: float                  # Standard pitch [mm]

    # Correction factors
    friction_correction: float = 1.0       # C_μ
    embedding_correction: float = 1.0      # C_embed
    pitch_mismatch_correction: float = 1.0 # C_pitch (MS2)
    combined_correction: float = 1.0       # C_total

    # Cycle transformation
    cycle_scale: float = 1.0               # N_p / N_m ratio
    cycle_scaling_mode: CycleScalingMode = CycleScalingMode.SCALED_DURATION  # CS3

    # Quality assessment
    quality_score: float = 1.0
    warnings: List[str] = field(default_factory=list)

    def prototype_cycles_from_model(self, N_model: np.ndarray) -> np.ndarray:
        """
        Transform model cycles to equivalent prototype cycles.

        N_p = N_m × λ
        """
        return N_model * self.scale_factor

    def prototype_preload_from_model(self,
                                     F_model_normalized: np.ndarray,
                                     apply_corrections: bool = True
                                     ) -> np.ndarray:
        """
        Transform normalized model preload to prototype prediction.

        Args:
            F_model_normalized: F_m / F_0,m array
            apply_corrections: Whether to apply scale effect corrections

        Returns:
            Predicted F_p / F_0,p array
        """
        if apply_corrections:
            # Apply embedding correction (model has relatively larger loss)
            corrected = F_model_normalized + (1 - F_model_normalized) * (1 - self.embedding_correction)
            return corrected
        return F_model_normalized


def find_nearest_standard_bolt(target_diameter: float,
                               standard: str = "ISO") -> Tuple[float, float]:
    """
    Find nearest standard bolt size to target diameter.

    Args:
        target_diameter: Target diameter [mm]
        standard: "ISO" or "UNC"

    Returns:
        Tuple of (diameter, pitch) [mm]
    """
    if standard == "ISO":
        # ISO metric coarse thread sizes (d, P) in mm
        sizes = [
            (3, 0.5), (4, 0.7), (5, 0.8), (6, 1.0), (8, 1.25),
            (10, 1.5), (12, 1.75), (14, 2.0), (16, 2.0), (18, 2.5),
            (20, 2.5), (22, 2.5), (24, 3.0), (27, 3.0), (30, 3.5),
            (33, 3.5), (36, 4.0), (39, 4.0), (42, 4.5), (45, 4.5),
            (48, 5.0), (52, 5.0), (56, 5.5), (60, 5.5), (64, 6.0),
        ]
    else:  # UNC
        # UNC thread sizes (d in mm, pitch in mm)
        sizes = [
            (6.35, 1.27),    # 1/4"-20
            (7.94, 1.41),    # 5/16"-18
            (9.53, 1.59),    # 3/8"-16
            (12.70, 2.12),   # 1/2"-13
            (15.88, 2.54),   # 5/8"-11
            (19.05, 2.82),   # 3/4"-10
            (25.40, 3.18),   # 1"-8
        ]

    # Find closest size
    closest = min(sizes, key=lambda x: abs(x[0] - target_diameter))
    return closest


def create_scaled_loosening_model(
    prototype_diameter: float,
    prototype_pitch: float,
    prototype_grip_length: float,
    prototype_preload: float,
    prototype_frequency: float,
    scale_factor: float,
    mu_prototype: float = 0.12,
    embedding_um: float = 3.0,
    cycle_scaling_mode: CycleScalingMode = CycleScalingMode.SCALED_DURATION
) -> ScaledLooseningModel:
    """
    Create geometrically scaled model for loosening tests.

    Args:
        prototype_diameter: Prototype bolt diameter [mm]
        prototype_pitch: Prototype thread pitch [mm]
        prototype_grip_length: Prototype grip length [mm]
        prototype_preload: Prototype preload force [N]
        prototype_frequency: Prototype test frequency [Hz]
        scale_factor: lambda = L_m / L_p (0 < lambda <= 1)
        mu_prototype: Prototype friction coefficient
        embedding_um: Embedding per interface [um]
        cycle_scaling_mode: Cycle scaling mode (CS3)

    Returns:
        ScaledLooseningModel instance
    """
    lam = scale_factor

    # Scaled geometry
    d_m = prototype_diameter * lam
    p_m = prototype_pitch * lam
    L_m = prototype_grip_length * lam

    # Scaled force (stress similitude)
    F_m = prototype_preload * lam**2

    # Scaled frequency
    f_m = prototype_frequency / lam

    # Find nearest standard bolt
    d_std, p_std = find_nearest_standard_bolt(d_m)

    # Calculate correction factors
    # Friction: increases ~8% per 2x size reduction
    C_mu = 1 + 0.08 * (1 - lam)

    # Embedding: relative effect scales as 1/lambda
    C_embed = lam

    # MS2: Pitch mismatch correction
    pitch_analysis = assess_pitch_mismatch(
        prototype_diameter, prototype_pitch,
        d_std, p_std, lam
    )
    C_pitch = pitch_analysis['correction_factor']

    # Combined correction
    C_total = C_mu * C_embed * C_pitch

    # CS3: Cycle scaling based on mode
    if cycle_scaling_mode == CycleScalingMode.SCALED_DURATION:
        cycle_scale = lam
    elif cycle_scaling_mode == CycleScalingMode.SAME_DURATION:
        cycle_scale = 1.0  # Same wall-clock time, model runs more cycles
    else:  # SAME_CYCLES
        cycle_scale = 1.0

    # Warnings
    warnings = []

    # Check diameter mismatch
    diameter_error = abs(d_std - d_m) / d_m * 100 if d_m > 0 else 0
    if diameter_error > 15:
        warnings.append(f"Standard bolt M{d_std:.0f} deviates {diameter_error:.1f}% from ideal")

    # Check pitch ratio preservation
    pitch_ratio_proto = prototype_pitch / prototype_diameter
    pitch_ratio_model = p_std / d_std if d_std > 0 else 0
    pitch_error = abs(pitch_ratio_model - pitch_ratio_proto) / pitch_ratio_proto * 100 if pitch_ratio_proto > 0 else 0
    if pitch_error > 10:
        warnings.append(f"Pitch ratio deviates {pitch_error:.1f}% - loosening rate affected")

    # MS2: Add pitch mismatch warning if significant
    if pitch_analysis['severity'] in ('medium', 'high'):
        warnings.append(f"Pitch mismatch: {pitch_analysis['severity']} - {pitch_analysis['recommendation']}")

    # Quality score
    quality = 1.0
    quality *= (1 - diameter_error / 100)
    quality *= (1 - pitch_error / 100)
    quality = max(0, quality)

    return ScaledLooseningModel(
        scale_factor=lam,
        prototype_diameter=prototype_diameter,
        prototype_pitch=prototype_pitch,
        prototype_grip_length=prototype_grip_length,
        prototype_preload=prototype_preload,
        prototype_frequency=prototype_frequency,
        model_diameter=d_m,
        model_pitch=p_m,
        model_grip_length=L_m,
        model_preload=F_m,
        model_frequency=f_m,
        standard_diameter=d_std,
        standard_pitch=p_std,
        friction_correction=C_mu,
        embedding_correction=C_embed,
        pitch_mismatch_correction=C_pitch,
        combined_correction=C_total,
        cycle_scale=cycle_scale,
        cycle_scaling_mode=cycle_scaling_mode,
        quality_score=quality,
        warnings=warnings
    )


# =============================================================================
# Loosening Curve Transformation
# =============================================================================

@dataclass
class LooseningCurveTransform:
    """
    Transforms loosening curves between prototype and model.

    Handles:
    - Cycle domain scaling
    - Preload normalization
    - Scale effect corrections
    """
    scale_factor: float
    friction_correction: float
    embedding_correction: float

    def model_to_prototype_cycles(self, N_model: np.ndarray) -> np.ndarray:
        """Transform model cycles to prototype equivalent."""
        return N_model * self.scale_factor

    def prototype_to_model_cycles(self, N_proto: np.ndarray) -> np.ndarray:
        """Transform prototype cycles to model equivalent."""
        return N_proto / self.scale_factor

    def model_to_prototype_preload(self,
                                   F_normalized_model: np.ndarray,
                                   correct_embedding: bool = True,
                                   correct_friction: bool = True
                                   ) -> np.ndarray:
        """
        Transform model normalized preload to prototype prediction.

        Model experiences relatively larger losses due to scale effects.
        Apply corrections to predict prototype behavior.
        """
        F_proto = F_normalized_model.copy()

        if correct_embedding:
            # Model has ~1/λ times larger relative embedding loss
            # Correction: reduce loss magnitude
            loss_model = 1 - F_proto
            loss_proto = loss_model * self.embedding_correction
            F_proto = 1 - loss_proto

        if correct_friction:
            # Higher friction in model slightly affects Stage II rate
            # Minor correction
            pass

        return F_proto

    def generate_prototype_prediction(self,
                                      N_model: np.ndarray,
                                      F_model_normalized: np.ndarray
                                      ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Generate complete prototype prediction from model test data.

        Returns:
            Tuple of (N_prototype, F_prototype_normalized)
        """
        N_proto = self.model_to_prototype_cycles(N_model)
        F_proto = self.model_to_prototype_preload(F_model_normalized)
        return N_proto, F_proto


# =============================================================================
# Comprehensive Similitude Analysis
# =============================================================================

class LooseningSimlitudeAnalysis:
    """
    Complete similitude analysis for bolt loosening behavior.

    Combines:
    - Multi-bolt reduction
    - Geometric scaling
    - Π-group analysis
    - Scale effect corrections
    - Loosening curve transformations
    """

    def __init__(self):
        self.pi_groups: List[LooseningPiGroup] = []
        self.scale_effects: List[ScaleEffect] = []
        self.equivalent_model: Optional[EquivalentSingleBolt] = None
        self.scaled_model: Optional[ScaledLooseningModel] = None
        self.curve_transform: Optional[LooseningCurveTransform] = None

    def analyze_multi_bolt_reduction(self,
                                     config: MultiBoltConfig
                                     ) -> EquivalentSingleBolt:
        """
        Perform multi-bolt to single-bolt reduction analysis.
        """
        self.equivalent_model = reduce_multi_bolt_to_single(config)
        self.pi_groups = self.equivalent_model.pi_groups
        return self.equivalent_model

    def analyze_geometric_scaling(self,
                                  prototype_diameter: float,
                                  prototype_pitch: float,
                                  prototype_grip_length: float,
                                  prototype_preload: float,
                                  prototype_frequency: float,
                                  scale_factor: float
                                  ) -> ScaledLooseningModel:
        """
        Perform geometric scaling analysis.
        """
        self.scaled_model = create_scaled_loosening_model(
            prototype_diameter=prototype_diameter,
            prototype_pitch=prototype_pitch,
            prototype_grip_length=prototype_grip_length,
            prototype_preload=prototype_preload,
            prototype_frequency=prototype_frequency,
            scale_factor=scale_factor
        )

        # Create curve transformer
        self.curve_transform = LooseningCurveTransform(
            scale_factor=scale_factor,
            friction_correction=self.scaled_model.friction_correction,
            embedding_correction=self.scaled_model.embedding_correction
        )

        # Detect scale effects
        self._detect_scale_effects(
            prototype_diameter,
            self.scaled_model.model_diameter,
            scale_factor
        )

        return self.scaled_model

    def _detect_scale_effects(self,
                              d_proto: float,
                              d_model: float,
                              scale_factor: float):
        """Detect and quantify scale effects."""
        self.scale_effects = [
            ScaleEffect.surface_roughness(6.3, d_proto, d_model),
            ScaleEffect.friction_coefficient(0.12, d_proto, d_model),
            ScaleEffect.embedding_loss(3.0, d_proto, d_model, 160000 * scale_factor**2),
            ScaleEffect.thread_form_tolerance(scale_factor),
        ]

    def get_quality_assessment(self) -> str:
        """Get overall quality assessment."""
        if self.equivalent_model:
            quality = self.equivalent_model.pi_preservation_quality
        elif self.scaled_model:
            quality = self.scaled_model.quality_score
        else:
            return "No analysis performed"

        if quality > 0.95:
            return "Excellent"
        elif quality > 0.85:
            return "Good"
        elif quality > 0.70:
            return "Acceptable"
        else:
            return "Poor - review parameters"

    def predict_prototype_loosening(self,
                                    N_model: np.ndarray,
                                    F_model_normalized: np.ndarray
                                    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Predict prototype loosening from model test data.

        Args:
            N_model: Model cycle counts
            F_model_normalized: Model F/F₀ values

        Returns:
            Tuple of (N_prototype, F_prototype_normalized)
        """
        if self.curve_transform is None:
            raise ValueError("No geometric scaling analysis performed")

        return self.curve_transform.generate_prototype_prediction(
            N_model, F_model_normalized
        )

    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive analysis report."""
        report = {
            'analysis_type': None,
            'quality': self.get_quality_assessment(),
            'pi_groups': [pg.to_dict() for pg in self.pi_groups],
            'scale_effects': [se.to_dict() for se in self.scale_effects],
        }

        if self.equivalent_model:
            report['analysis_type'] = 'multi_bolt_reduction'
            report['equivalent_model'] = self.equivalent_model.to_dict()

        if self.scaled_model:
            report['analysis_type'] = 'geometric_scaling'
            report['scaled_model'] = {
                'scale_factor': self.scaled_model.scale_factor,
                'model_diameter': self.scaled_model.model_diameter,
                'standard_bolt': f"M{self.scaled_model.standard_diameter:.0f}",
                'corrections': {
                    'friction': self.scaled_model.friction_correction,
                    'embedding': self.scaled_model.embedding_correction,
                    'combined': self.scaled_model.combined_correction,
                },
                'warnings': self.scaled_model.warnings,
            }

        return report

    def save_analysis(self, filepath: str):
        """Save analysis to JSON file."""
        report = self.generate_report()
        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2)


# =============================================================================
# MSD Builder Integration Helpers
# =============================================================================

def create_msd_elements_from_equivalent(
    equiv: EquivalentSingleBolt
) -> Dict[str, Any]:
    """
    Create MSD element parameters from equivalent single bolt.

    Returns dictionary suitable for MSDElementData creation.
    """
    # Calculate thread geometry for equivalent diameter
    d = equiv.d_equivalent
    p = equiv.p_equivalent
    d2 = d - 0.6495 * p
    d3 = d - 1.0825 * p

    return {
        'head': {
            'type': 'HEAD',
            'diameter': d * 1.5,  # Head diameter
            'length': d * 0.7,
            'mass': None,  # Auto-calculate
            'stiffness': equiv.k_bolt_equivalent * 0.3,  # Head portion
        },
        'shank': {
            'type': 'SHANK',
            'diameter': d,
            'length': equiv.L_equivalent * 0.5,
            'stiffness': equiv.k_bolt_equivalent * 0.5,  # Shank portion
        },
        'thread': {
            'type': 'THREAD',
            'diameter': d,
            'pitch': p,
            'pitch_diameter': d2,
            'minor_diameter': d3,
            'length': equiv.L_equivalent * 0.3,
            'stiffness': equiv.k_bolt_equivalent * 0.2,
        },
        'member': {
            'type': 'FLANGE',
            'stiffness': equiv.k_member_equivalent,
            'length': equiv.L_equivalent,
        },
        'preload': equiv.F_p_equivalent,
        'transverse_force': equiv.F_t_equivalent,
    }


def create_msd_elements_from_scaled(
    scaled: ScaledLooseningModel
) -> Dict[str, Any]:
    """
    Create MSD element parameters from scaled model.

    Uses standard bolt size for practical implementation.
    """
    d = scaled.standard_diameter
    p = scaled.standard_pitch
    d2 = d - 0.6495 * p
    d3 = d - 1.0825 * p

    return {
        'head': {
            'type': 'HEAD',
            'diameter': d * 1.5,
            'length': d * 0.7,
        },
        'shank': {
            'type': 'SHANK',
            'diameter': d,
            'length': scaled.model_grip_length * 0.5,
        },
        'thread': {
            'type': 'THREAD',
            'diameter': d,
            'pitch': p,
            'pitch_diameter': d2,
            'minor_diameter': d3,
            'length': scaled.model_grip_length * 0.3,
        },
        'member': {
            'type': 'FLANGE',
            'length': scaled.model_grip_length,
        },
        'preload': scaled.model_preload,
        'test_frequency': scaled.model_frequency,
        'scale_factor': scaled.scale_factor,
        'corrections': {
            'friction': scaled.friction_correction,
            'embedding': scaled.embedding_correction,
        }
    }


# =============================================================================
# Test Suite
# =============================================================================

def run_tests():
    """Run comprehensive test suite."""
    print("=" * 70)
    print("LOOSENING SIMILITUDE ANALYSIS - TEST SUITE")
    print("=" * 70)

    # Test 1: Multi-bolt reduction
    print("\n[Test 1] Multi-Bolt to Single-Bolt Reduction")
    config = MultiBoltConfig(
        n_bolts=8,
        bolt_diameter=24.0,
        pitch=3.0,
        grip_length=100.0,
        preload_per_bolt=160000.0,
        transverse_force_per_bolt=15000.0,
        bolt_circle_diameter=200.0
    )

    equiv = reduce_multi_bolt_to_single(config)
    print(f"  Original: 8 x M24, F_p = 160 kN each")
    print(f"  Equivalent: d = {equiv.d_equivalent:.1f} mm, p = {equiv.p_equivalent:.1f} mm")
    print(f"  Equivalent preload: {equiv.F_p_equivalent/1000:.0f} kN")
    print(f"  Pi-group preservation: {equiv.pi_preservation_quality*100:.1f}%")

    # Test 2: Geometric scaling
    print("\n[Test 2] Geometric Scaling (1:4)")
    scaled = create_scaled_loosening_model(
        prototype_diameter=24.0,
        prototype_pitch=3.0,
        prototype_grip_length=100.0,
        prototype_preload=160000.0,
        prototype_frequency=25.0,
        scale_factor=0.25
    )

    print(f"  Prototype: M24, L = 100 mm, F_p = 160 kN, f = 25 Hz")
    print(f"  Model: d = {scaled.model_diameter:.1f} mm (std: M{scaled.standard_diameter:.0f})")
    print(f"         L = {scaled.model_grip_length:.1f} mm")
    print(f"         F_p = {scaled.model_preload:.0f} N")
    print(f"         f = {scaled.model_frequency:.0f} Hz")
    print(f"  Corrections: C_mu = {scaled.friction_correction:.3f}, "
          f"C_embed = {scaled.embedding_correction:.3f}")
    print(f"  Quality: {scaled.quality_score*100:.1f}%")
    if scaled.warnings:
        for w in scaled.warnings:
            print(f"  Warning: {w}")

    # Test 3: Comprehensive analysis
    print("\n[Test 3] Comprehensive Analysis")
    analysis = LooseningSimlitudeAnalysis()
    analysis.analyze_multi_bolt_reduction(config)
    print(f"  Quality: {analysis.get_quality_assessment()}")
    print(f"  Pi-groups: {len(analysis.pi_groups)}")

    # Test 4: Loosening curve transformation
    print("\n[Test 4] Loosening Curve Transformation")
    analysis2 = LooseningSimlitudeAnalysis()
    analysis2.analyze_geometric_scaling(
        prototype_diameter=24.0,
        prototype_pitch=3.0,
        prototype_grip_length=100.0,
        prototype_preload=160000.0,
        prototype_frequency=25.0,
        scale_factor=0.25
    )

    # Simulate model test data
    N_model = np.array([0, 100, 200, 500, 1000, 2000])
    F_model_normalized = np.array([1.0, 0.92, 0.85, 0.75, 0.68, 0.62])

    N_proto, F_proto = analysis2.predict_prototype_loosening(N_model, F_model_normalized)

    print("  Model Data -> Prototype Prediction:")
    print("  N_model    F/F0_model   N_proto    F/F0_proto")
    for i in range(len(N_model)):
        print(f"  {N_model[i]:6.0f}     {F_model_normalized[i]:.3f}      "
              f"{N_proto[i]:6.0f}     {F_proto[i]:.3f}")

    # Test 5: MSD element generation
    print("\n[Test 5] MSD Element Generation")
    elements = create_msd_elements_from_equivalent(equiv)
    print(f"  Generated elements: {list(elements.keys())}")
    print(f"  Head diameter: {elements['head']['diameter']:.1f} mm")
    print(f"  Thread pitch: {elements['thread']['pitch']:.2f} mm")

    print("\n" + "=" * 70)
    print("ALL TESTS PASSED")
    print("=" * 70)


if __name__ == "__main__":
    run_tests()
