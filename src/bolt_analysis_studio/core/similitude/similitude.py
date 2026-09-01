#!/usr/bin/env python3
"""
Similitude Analysis Module
Bolt Analysis Studio v4.0

Dimensional analysis and scaling laws for bolted flanged joints.
Based on Buckingham-Π theorem with scale effect corrections.

Prof. Leonardo Rosa Ribeiro da Silva, PhD
January 2026
"""

from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional, Any
from enum import Enum
import numpy as np
import copy
import json
from pathlib import Path


# =============================================================================
# Enumerations
# =============================================================================

class MaterialSimilarity(Enum):
    """Material similarity classification for scaled models."""
    SAME = "same"              # Identical material (λ_E = λ_ρ = 1)
    SIMILAR = "similar"        # Same E/ρ ratio (wave speed preserved)
    DIFFERENT = "different"    # Different material (requires compensation)


class ScaleEffectSeverity(Enum):
    """Scale effect severity classification."""
    NEGLIGIBLE = "negligible"  # < 2% deviation
    LOW = "low"                # 2-5% deviation
    MEDIUM = "medium"          # 5-15% deviation
    HIGH = "high"              # > 15% deviation
    CRITICAL = "critical"      # > 30% deviation


class SimilitudeType(Enum):
    """Type of similitude analysis."""
    GEOMETRIC = "geometric"     # Lengths only
    KINEMATIC = "kinematic"     # Lengths + velocities
    DYNAMIC = "dynamic"         # Lengths + velocities + forces
    COMPLETE = "complete"       # All parameters including friction


# =============================================================================
# Scale Factors Data Class
# =============================================================================

@dataclass
class ScaleFactors:
    """
    Derived scale factors from geometric scale λ.
    
    For same-material stress similitude:
    - Stress preserved: σ_m = σ_p
    - Strain preserved: ε_m = ε_p
    - Force scales as λ²
    - Frequency scales as 1/λ
    """
    geometric: float = 0.25      # λ (model/prototype length ratio)
    
    # Material similarity factors (default: same material)
    elastic_modulus_ratio: float = 1.0   # E_m / E_p
    density_ratio: float = 1.0           # ρ_m / ρ_p
    
    def __post_init__(self):
        """Validate scale factor."""
        if self.geometric <= 0 or self.geometric > 1:
            raise ValueError(f"Geometric scale must be in (0, 1], got {self.geometric}")
    
    @property
    def length(self) -> float:
        """Length scale factor λ."""
        return self.geometric
    
    @property
    def area(self) -> float:
        """Area scale factor λ²."""
        return self.geometric ** 2
    
    @property
    def volume(self) -> float:
        """Volume scale factor λ³."""
        return self.geometric ** 3
    
    @property
    def mass(self) -> float:
        """Mass scale factor λ³ × (ρ_m/ρ_p)."""
        return self.geometric ** 3 * self.density_ratio
    
    @property
    def force(self) -> float:
        """Force scale factor for stress similitude: λ² × (E_m/E_p)."""
        return self.geometric ** 2 * self.elastic_modulus_ratio
    
    @property
    def stress(self) -> float:
        """Stress scale factor (E_m/E_p for elastic similitude)."""
        return self.elastic_modulus_ratio
    
    @property
    def strain(self) -> float:
        """Strain scale factor (always 1 for elastic similitude)."""
        return 1.0
    
    @property
    def displacement(self) -> float:
        """Displacement scale factor λ × ε = λ."""
        return self.geometric
    
    @property
    def stiffness(self) -> float:
        """Stiffness scale factor λ × (E_m/E_p)."""
        return self.geometric * self.elastic_modulus_ratio
    
    @property
    def damping(self) -> float:
        """Damping scale factor λ² × √(E_m × ρ_m / E_p × ρ_p)."""
        return self.geometric ** 2 * np.sqrt(
            self.elastic_modulus_ratio * self.density_ratio
        )
    
    @property
    def frequency(self) -> float:
        """Frequency scale factor (1/λ) × √(E_m/ρ_m × ρ_p/E_p)."""
        return (1.0 / self.geometric) * np.sqrt(
            self.elastic_modulus_ratio / self.density_ratio
        )
    
    @property
    def time(self) -> float:
        """Time scale factor (1/frequency)."""
        return 1.0 / self.frequency
    
    @property
    def velocity(self) -> float:
        """Velocity scale factor √(E_m/ρ_m × ρ_p/E_p)."""
        return np.sqrt(self.elastic_modulus_ratio / self.density_ratio)
    
    @property
    def acceleration(self) -> float:
        """Acceleration scale factor (1/λ) × (E_m/ρ_m × ρ_p/E_p)."""
        return (1.0 / self.geometric) * (
            self.elastic_modulus_ratio / self.density_ratio
        )
    
    @property
    def energy(self) -> float:
        """Energy scale factor λ³ × (E_m/E_p)."""
        return self.geometric ** 3 * self.elastic_modulus_ratio
    
    @property
    def power(self) -> float:
        """Power scale factor λ² × √(E_m³/ρ_m × ρ_p/E_p³)."""
        return self.geometric ** 2 * np.sqrt(
            self.elastic_modulus_ratio ** 3 / self.density_ratio
        )
    
    @property
    def moment(self) -> float:
        """Moment/torque scale factor λ³ × (E_m/E_p)."""
        return self.geometric ** 3 * self.elastic_modulus_ratio
    
    @property
    def moment_of_inertia(self) -> float:
        """Area moment of inertia scale factor λ⁴."""
        return self.geometric ** 4
    
    @property
    def mass_moment_of_inertia(self) -> float:
        """Mass moment of inertia scale factor λ⁵ × (ρ_m/ρ_p)."""
        return self.geometric ** 5 * self.density_ratio
    
    def get_all_factors(self) -> Dict[str, float]:
        """Return dictionary of all scale factors."""
        return {
            'geometric': self.geometric,
            'length': self.length,
            'area': self.area,
            'volume': self.volume,
            'mass': self.mass,
            'force': self.force,
            'stress': self.stress,
            'strain': self.strain,
            'displacement': self.displacement,
            'stiffness': self.stiffness,
            'damping': self.damping,
            'frequency': self.frequency,
            'time': self.time,
            'velocity': self.velocity,
            'acceleration': self.acceleration,
            'energy': self.energy,
            'power': self.power,
            'moment': self.moment,
            'moment_of_inertia': self.moment_of_inertia,
            'mass_moment_of_inertia': self.mass_moment_of_inertia,
        }
    
    def to_table(self) -> List[Dict[str, str]]:
        """Return formatted table for display."""
        factors = [
            ('Length', 'λ', f'{self.length:.4f}'),
            ('Area', 'λ²', f'{self.area:.6f}'),
            ('Volume', 'λ³', f'{self.volume:.6f}'),
            ('Mass', 'λ³·(ρ_m/ρ_p)', f'{self.mass:.6f}'),
            ('Force', 'λ²·(E_m/E_p)', f'{self.force:.6f}'),
            ('Stress', 'E_m/E_p', f'{self.stress:.4f}'),
            ('Displacement', 'λ', f'{self.displacement:.4f}'),
            ('Stiffness', 'λ·(E_m/E_p)', f'{self.stiffness:.4f}'),
            ('Damping', 'λ²·√(E·ρ)', f'{self.damping:.6f}'),
            ('Frequency', '(1/λ)·√(E/ρ)', f'{self.frequency:.4f}'),
            ('Time', 'λ·√(ρ/E)', f'{self.time:.4f}'),
            ('Velocity', '√(E/ρ)', f'{self.velocity:.4f}'),
            ('Acceleration', '(1/λ)·(E/ρ)', f'{self.acceleration:.4f}'),
        ]
        return [{'Quantity': q, 'Factor': f, 'Value': v} for q, f, v in factors]


# =============================================================================
# Π-Group Data Class
# =============================================================================

@dataclass
class PiGroup:
    """
    Dimensionless Π-group for similitude analysis.
    
    Per Buckingham-Π theorem, complete similitude requires matching
    all independent dimensionless groups between prototype and model.
    """
    name: str                    # Human-readable name
    symbol: str                  # Mathematical symbol (Π₁, Π₂, etc.)
    expression: str              # Mathematical expression
    description: str             # Physical interpretation
    prototype_value: float       # Π value for prototype
    model_value: float           # Π value for model
    tolerance: float = 0.05      # Acceptable deviation (default 5%)
    units: str = "-"             # Always dimensionless
    category: str = "primary"    # primary, secondary, derived
    
    @property
    def deviation(self) -> float:
        """Absolute deviation between model and prototype."""
        return abs(self.model_value - self.prototype_value)
    
    @property
    def deviation_percent(self) -> float:
        """Percentage deviation."""
        if abs(self.prototype_value) < 1e-10:
            return 0.0 if abs(self.model_value) < 1e-10 else 100.0
        return 100.0 * abs(self.model_value - self.prototype_value) / abs(self.prototype_value)
    
    @property
    def is_matched(self) -> bool:
        """Check if model matches prototype within tolerance."""
        return self.deviation_percent <= self.tolerance * 100
    
    @property
    def match_status(self) -> str:
        """String status of match quality."""
        dev = self.deviation_percent
        if dev <= 1:
            return "Excellent"
        elif dev <= 5:
            return "Good"
        elif dev <= 10:
            return "Acceptable"
        elif dev <= 20:
            return "Marginal"
        else:
            return "Poor"
    
    @property
    def status_icon(self) -> str:
        """Unicode icon for match status."""
        dev = self.deviation_percent
        if dev <= self.tolerance * 100:
            return "✓"
        elif dev < 10:
            return "⚠"
        else:
            return "✗"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'name': self.name,
            'symbol': self.symbol,
            'expression': self.expression,
            'description': self.description,
            'prototype_value': self.prototype_value,
            'model_value': self.model_value,
            'tolerance': self.tolerance,
            'deviation_percent': self.deviation_percent,
            'is_matched': self.is_matched,
            'status': self.match_status,
        }


# =============================================================================
# Scale Effect Data Class
# =============================================================================

@dataclass
class ScaleEffect:
    """
    Scale effect description and correction factor.
    
    Scale effects arise from non-geometric parameters that don't
    scale proportionally with size, such as:
    - Surface roughness (manufacturing limitation)
    - Friction coefficients (contact mechanics)
    - Material microstructure effects
    """
    name: str                         # Effect name
    parameter: str                    # Affected parameter
    description: str                  # Physical explanation
    prototype_value: float            # Parameter in prototype
    model_value: float                # Parameter in model (estimated)
    deviation_percent: float          # Percentage deviation
    correction_factor: float          # Multiplicative correction
    severity: ScaleEffectSeverity     # Classification
    
    @classmethod
    def surface_roughness(cls, Rz_um: float, d_proto_mm: float, 
                          d_model_mm: float) -> 'ScaleEffect':
        """
        Create surface roughness scale effect.
        
        Surface roughness (Rz) does not scale with geometry because
        it depends on manufacturing processes, not component size.
        The dimensionless ratio Rz/d increases in scaled models.
        
        Args:
            Rz_um: Surface roughness in micrometers
            d_proto_mm: Prototype bolt diameter in mm
            d_model_mm: Model bolt diameter in mm
        """
        ratio_proto = Rz_um / (d_proto_mm * 1000)  # Rz/d for prototype
        ratio_model = Rz_um / (d_model_mm * 1000)  # Rz/d for model
        deviation = 100.0 * (ratio_model / ratio_proto - 1)
        
        # Correction based on VDI 2230 embedment sensitivity
        # Higher Rz/d leads to more relative embedment
        correction = 1 + 0.10 * (ratio_model - ratio_proto) / ratio_proto
        
        severity = cls._classify_severity(abs(deviation))
        
        return cls(
            name="Surface Roughness",
            parameter="Rz/d ratio",
            description=f"Rz = {Rz_um} μm constant; Rz/d increases {ratio_model/ratio_proto:.1f}× in model",
            prototype_value=ratio_proto,
            model_value=ratio_model,
            deviation_percent=deviation,
            correction_factor=max(1.0, correction),
            severity=severity
        )
    
    @classmethod
    def friction_coefficient(cls, mu_proto: float, d_proto_mm: float,
                             d_model_mm: float, surface_treatment: str = "standard") -> 'ScaleEffect':
        """
        Create friction coefficient scale effect.
        
        Friction coefficients tend to increase slightly in smaller joints
        due to higher contact pressures and surface area-to-volume ratios.
        
        Args:
            mu_proto: Friction coefficient in prototype
            d_proto_mm: Prototype bolt diameter in mm
            d_model_mm: Model bolt diameter in mm
            surface_treatment: Surface treatment type
        """
        scale = d_model_mm / d_proto_mm
        
        # Empirical correlation: μ increases ~8% per factor of 2 reduction
        # Based on tribological contact mechanics
        mu_model = mu_proto * (1 + 0.08 * (1 - scale))
        deviation = 100.0 * (mu_model / mu_proto - 1)
        
        # Correction factor for preload calculations
        correction = mu_model / mu_proto
        
        severity = cls._classify_severity(abs(deviation))
        
        return cls(
            name="Friction Coefficient",
            parameter="μ (thread & bearing)",
            description=f"Contact pressure increase → μ deviation +{deviation:.1f}%",
            prototype_value=mu_proto,
            model_value=mu_model,
            deviation_percent=deviation,
            correction_factor=correction,
            severity=severity
        )
    
    @classmethod
    def embedding_loss(cls, delta_fp_um: float, d_proto_mm: float,
                       d_model_mm: float, preload_proto: float) -> 'ScaleEffect':
        """
        Create embedding loss scale effect.
        
        Embedding (plastic settling) at interfaces has a constant absolute
        magnitude (~3 μm per interface) regardless of bolt size. This means
        the relative preload loss (ΔFp/Fp) is larger in scaled models.
        
        Args:
            delta_fp_um: Embedding deformation per interface (μm)
            d_proto_mm: Prototype bolt diameter in mm
            d_model_mm: Model bolt diameter in mm
            preload_proto: Prototype preload force (N)
        """
        scale = d_model_mm / d_proto_mm
        
        # Relative preload loss scales inversely with λ for same δfp
        # Because: k ~ λ, Fp ~ λ², δfp ~ constant
        # ΔFp/Fp = δfp × k / Fp ∝ 1/λ
        loss_ratio = 1 / scale
        deviation = 100.0 * (loss_ratio - 1)
        
        # Correction factor
        correction = 1 + 0.05 * (1/scale - 1)
        
        severity = cls._classify_severity(abs(deviation))
        
        return cls(
            name="Embedding Loss",
            parameter="ΔFp/Fp (relative preload loss)",
            description=f"δfp = {delta_fp_um} μm/interface → {loss_ratio:.1f}× relative loss in model",
            prototype_value=1.0,
            model_value=loss_ratio,
            deviation_percent=deviation,
            correction_factor=max(1.0, correction),
            severity=severity
        )
    
    @classmethod
    def thread_form_tolerance(cls, scale: float) -> 'ScaleEffect':
        """
        Create thread form tolerance scale effect.
        
        Thread manufacturing tolerances (class 6g/6H etc.) are specified
        as absolute values, not proportional to size. Smaller threads
        have relatively larger tolerance deviations.
        """
        # ISO tolerance grade increases effective tolerance ratio
        deviation = 100.0 * (1/scale - 1) * 0.3  # ~30% of geometric effect
        correction = 1 + 0.02 * (1/scale - 1)
        
        severity = cls._classify_severity(abs(deviation))
        
        return cls(
            name="Thread Form Tolerance",
            parameter="Thread geometry deviation",
            description=f"ISO tolerance grades → {deviation:.1f}% relative increase",
            prototype_value=1.0,
            model_value=1/scale * 0.3 + 0.7,
            deviation_percent=deviation,
            correction_factor=max(1.0, correction),
            severity=severity
        )
    
    @classmethod
    def stress_concentration(cls, d_proto_mm: float, d_model_mm: float,
                             root_radius_ratio: float = 0.144) -> 'ScaleEffect':
        """
        Create stress concentration scale effect.
        
        Thread root radius r scales with pitch P, which scales with d.
        The stress concentration factor Kt = f(r/P) is preserved if
        the thread form is geometrically similar.
        """
        # For standard ISO threads, r/P ratio is constant (~0.144)
        # Therefore Kt is preserved under geometric similitude
        deviation = 0.0  # Ideally preserved
        
        return cls(
            name="Stress Concentration",
            parameter="Kt (thread root)",
            description="Thread form similarity → Kt preserved",
            prototype_value=root_radius_ratio,
            model_value=root_radius_ratio,
            deviation_percent=deviation,
            correction_factor=1.0,
            severity=ScaleEffectSeverity.NEGLIGIBLE
        )
    
    @staticmethod
    def _classify_severity(deviation_percent: float) -> ScaleEffectSeverity:
        """Classify severity based on deviation magnitude."""
        if deviation_percent < 2:
            return ScaleEffectSeverity.NEGLIGIBLE
        elif deviation_percent < 5:
            return ScaleEffectSeverity.LOW
        elif deviation_percent < 15:
            return ScaleEffectSeverity.MEDIUM
        elif deviation_percent < 30:
            return ScaleEffectSeverity.HIGH
        else:
            return ScaleEffectSeverity.CRITICAL
    
    @property
    def severity_icon(self) -> str:
        """Unicode icon for severity level."""
        icons = {
            ScaleEffectSeverity.NEGLIGIBLE: "●",
            ScaleEffectSeverity.LOW: "◐",
            ScaleEffectSeverity.MEDIUM: "◑",
            ScaleEffectSeverity.HIGH: "⚠",
            ScaleEffectSeverity.CRITICAL: "⛔",
        }
        return icons.get(self.severity, "?")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'name': self.name,
            'parameter': self.parameter,
            'description': self.description,
            'prototype_value': self.prototype_value,
            'model_value': self.model_value,
            'deviation_percent': self.deviation_percent,
            'correction_factor': self.correction_factor,
            'severity': self.severity.value,
        }


# =============================================================================
# Prototype Data Class
# =============================================================================

@dataclass
class PrototypeData:
    """
    Prototype (full-scale) joint parameters.
    
    This dataclass contains all physical parameters of the prototype
    joint needed for similitude analysis and scaled model generation.
    """
    # Identification
    name: str = "Prototype Joint"
    description: str = ""
    
    # Geometric Parameters [mm]
    bolt_diameter: float = 24.0           # d - nominal bolt diameter
    grip_length: float = 100.0            # L - total clamped length
    flange_thickness: float = 30.0        # t - individual flange thickness
    bolt_circle_diameter: float = 200.0   # D_bc - bolt circle diameter
    thread_pitch: float = 3.0             # P - thread pitch
    washer_outer_diameter: float = 44.0   # d_w - washer OD
    clearance_hole_diameter: float = 26.0 # d_h - bolt hole diameter
    number_of_bolts: int = 8              # n - bolts in pattern
    
    # Material Parameters
    bolt_elastic_modulus: float = 205000.0    # E_b [MPa]
    member_elastic_modulus: float = 200000.0  # E_m [MPa]
    bolt_yield_strength: float = 724.0        # σ_y [MPa] (A193 B7)
    bolt_ultimate_strength: float = 862.0     # σ_u [MPa]
    bolt_density: float = 7850.0              # ρ_b [kg/m³]
    member_density: float = 7850.0            # ρ_m [kg/m³]
    bolt_poisson_ratio: float = 0.30          # ν_b
    member_poisson_ratio: float = 0.30        # ν_m
    
    # Loading Parameters
    preload_force: float = 160000.0       # F_p [N]
    external_axial_force: float = 48000.0 # F_ext [N]
    applied_torque: float = 450.0         # T [N·m] (tightening)
    
    # Friction Parameters
    thread_friction_coefficient: float = 0.15    # μ_t
    bearing_friction_coefficient: float = 0.15   # μ_b
    nut_factor: float = 0.18                     # K
    
    # Surface Parameters
    surface_roughness_Rz: float = 6.3     # Rz [μm]
    surface_roughness_Ra: float = 1.6     # Ra [μm]
    
    # Embedment
    embedding_per_interface: float = 3.0  # δfp [μm]
    
    def __post_init__(self):
        """Validate input parameters."""
        if self.bolt_diameter <= 0:
            raise ValueError("Bolt diameter must be positive")
        if self.grip_length <= 0:
            raise ValueError("Grip length must be positive")
        if self.preload_force <= 0:
            raise ValueError("Preload force must be positive")
    
    @property
    def tensile_stress_area(self) -> float:
        """Tensile stress area At [mm²] per ISO 262."""
        d = self.bolt_diameter
        P = self.thread_pitch
        d2 = d - 0.6495 * P  # Pitch diameter
        d3 = d - 1.2269 * P  # Minor diameter
        return np.pi / 4 * ((d2 + d3) / 2) ** 2
    
    @property
    def shank_area(self) -> float:
        """Shank cross-sectional area [mm²]."""
        return np.pi / 4 * self.bolt_diameter ** 2
    
    @property
    def preload_utilization(self) -> float:
        """Preload as fraction of yield (σ_preload / σ_y)."""
        sigma_preload = self.preload_force / self.tensile_stress_area
        return sigma_preload / self.bolt_yield_strength
    
    @property
    def load_ratio(self) -> float:
        """External load / preload ratio (separation margin)."""
        return self.external_axial_force / self.preload_force
    
    @property
    def grip_ratio(self) -> float:
        """Grip length / diameter ratio L/d."""
        return self.grip_length / self.bolt_diameter
    
    @property
    def flange_aspect_ratio(self) -> float:
        """Flange thickness / diameter ratio t/d."""
        return self.flange_thickness / self.bolt_diameter
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'name': self.name,
            'description': self.description,
            'geometry': {
                'bolt_diameter': self.bolt_diameter,
                'grip_length': self.grip_length,
                'flange_thickness': self.flange_thickness,
                'bolt_circle_diameter': self.bolt_circle_diameter,
                'thread_pitch': self.thread_pitch,
                'washer_outer_diameter': self.washer_outer_diameter,
                'clearance_hole_diameter': self.clearance_hole_diameter,
                'number_of_bolts': self.number_of_bolts,
            },
            'material': {
                'bolt_elastic_modulus': self.bolt_elastic_modulus,
                'member_elastic_modulus': self.member_elastic_modulus,
                'bolt_yield_strength': self.bolt_yield_strength,
                'bolt_ultimate_strength': self.bolt_ultimate_strength,
                'bolt_density': self.bolt_density,
                'member_density': self.member_density,
            },
            'loading': {
                'preload_force': self.preload_force,
                'external_axial_force': self.external_axial_force,
                'applied_torque': self.applied_torque,
            },
            'friction': {
                'thread_friction_coefficient': self.thread_friction_coefficient,
                'bearing_friction_coefficient': self.bearing_friction_coefficient,
                'nut_factor': self.nut_factor,
            },
            'surface': {
                'surface_roughness_Rz': self.surface_roughness_Rz,
                'surface_roughness_Ra': self.surface_roughness_Ra,
                'embedding_per_interface': self.embedding_per_interface,
            },
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PrototypeData':
        """Create instance from dictionary."""
        flat = {}
        flat['name'] = data.get('name', 'Prototype Joint')
        flat['description'] = data.get('description', '')
        
        for section in ['geometry', 'material', 'loading', 'friction', 'surface']:
            if section in data:
                flat.update(data[section])
        
        return cls(**flat)


# =============================================================================
# Main Similitude Analysis Class
# =============================================================================

@dataclass
class SimilitudeAnalysis:
    """
    Complete similitude analysis for bolted joint scaling.
    
    Performs Buckingham-Π dimensional analysis, calculates scale factors,
    detects scale effects, and computes correction factors for correlating
    scaled model tests to full-scale prototype behavior.
    
    Example:
        >>> proto = PrototypeData(bolt_diameter=24, grip_length=100, preload_force=160000)
        >>> analysis = SimilitudeAnalysis(prototype=proto, scale_factor=0.25)
        >>> print(f"Model diameter: {analysis.model_diameter:.1f} mm")
        >>> for pi in analysis.pi_groups:
        ...     print(f"{pi.symbol}: {pi.prototype_value:.3f} → {pi.model_value:.3f} {pi.status_icon}")
    """
    prototype: PrototypeData
    scale_factor: float = 0.25               # λ = L_model / L_prototype
    material_similarity: MaterialSimilarity = MaterialSimilarity.SAME
    
    # Calculated fields
    scales: ScaleFactors = field(default=None)
    pi_groups: List[PiGroup] = field(default_factory=list)
    scale_effects: List[ScaleEffect] = field(default_factory=list)
    combined_correction: float = 1.0
    
    # CS2/M6: Model material properties (for SIMILAR/DIFFERENT cases)
    model_elastic_modulus: float = 0.0       # E_model [MPa] (0 = same as prototype)
    model_yield_strength: float = 0.0        # σy_model [MPa] (0 = same as prototype)
    model_density: float = 0.0               # ρ_model [kg/m³] (0 = same as prototype)

    def __post_init__(self):
        """Initialize analysis calculations."""
        # CS2/M6: Create scale factors with material ratio propagation
        if self.material_similarity == MaterialSimilarity.SAME:
            self.scales = ScaleFactors(geometric=self.scale_factor)
        elif self.material_similarity == MaterialSimilarity.SIMILAR:
            # Same E/ρ ratio (wave speed preserved)
            E_ratio = (self.model_elastic_modulus / self.prototype.bolt_elastic_modulus
                       if self.model_elastic_modulus > 0 else 1.0)
            rho_ratio = (self.model_density / self.prototype.bolt_density
                         if self.model_density > 0 else 1.0)
            self.scales = ScaleFactors(
                geometric=self.scale_factor,
                elastic_modulus_ratio=E_ratio,
                density_ratio=rho_ratio,
            )
        else:  # DIFFERENT
            E_ratio = (self.model_elastic_modulus / self.prototype.bolt_elastic_modulus
                       if self.model_elastic_modulus > 0 else 1.0)
            rho_ratio = (self.model_density / self.prototype.bolt_density
                         if self.model_density > 0 else 1.0)
            self.scales = ScaleFactors(
                geometric=self.scale_factor,
                elastic_modulus_ratio=E_ratio,
                density_ratio=rho_ratio,
            )
        
        # Perform calculations
        self._calculate_pi_groups()
        self._detect_scale_effects()
        self._calculate_combined_correction()
    
    @property
    def model_diameter(self) -> float:
        """Model bolt diameter [mm]."""
        return self.prototype.bolt_diameter * self.scale_factor
    
    @property
    def model_grip_length(self) -> float:
        """Model grip length [mm]."""
        return self.prototype.grip_length * self.scale_factor
    
    @property
    def model_flange_thickness(self) -> float:
        """Model flange thickness [mm]."""
        return self.prototype.flange_thickness * self.scale_factor
    
    @property
    def model_preload(self) -> float:
        """Model preload force [N]."""
        return self.prototype.preload_force * self.scales.force
    
    @property
    def model_external_force(self) -> float:
        """Model external force [N]."""
        return self.prototype.external_axial_force * self.scales.force
    
    @property
    def scale_ratio_string(self) -> str:
        """Scale ratio as string (e.g., '1:4')."""
        ratio = int(round(1 / self.scale_factor))
        return f"1:{ratio}"
    
    def _compute_bolt_stiffness(self, d: float, P: float, L: float,
                                E: float = 205000.0) -> float:
        """
        Compute bolt stiffness using VDI 2230 series combination (CS1/M5).

        k_bolt = 1 / (1/k_head + 1/k_shank + 1/k_thread + 1/k_nut)

        Args:
            d: Bolt diameter [mm]
            P: Thread pitch [mm]
            L: Grip length [mm]
            E: Elastic modulus [MPa]

        Returns:
            Bolt stiffness [N/mm]
        """
        d2 = d - 0.6495 * P
        d3 = d - 1.2269 * P
        d_s = (d2 + d3) / 2
        A_s = np.pi / 4 * d_s ** 2  # Stress area

        A_shank = np.pi / 4 * d ** 2  # Shank area

        # Approximate lengths (VDI 2230 simplified)
        L_head = 0.5 * d           # Head flexibility
        L_shank = max(L * 0.6, 1)  # Unthreaded portion (~60%)
        L_thread = max(L * 0.4, 1) # Threaded portion (~40%)
        L_nut = 0.4 * d            # Nut flexibility

        # Series combination
        inv_k = (L_head / (E * A_shank) +
                 L_shank / (E * A_shank) +
                 L_thread / (E * A_s) +
                 L_nut / (E * A_s))

        return 1.0 / inv_k if inv_k > 0 else 1e9

    def _compute_member_stiffness(self, d: float, d_w: float, d_h: float,
                                   L: float, E: float = 200000.0) -> float:
        """
        Compute member stiffness using VDI 2230 frustum model (CS1/M5).

        k_member = E * π * d_w * tan(φ) / ln(((d_w + d_h) * (D_A - d_h)) /
                                               ((d_w - d_h) * (D_A + d_h)))

        where D_A = min(d_w + L*tan(φ), bolt_circle_sep/2) and φ ≈ 30°

        Args:
            d: Bolt diameter [mm]
            d_w: Washer OD [mm]
            d_h: Clearance hole diameter [mm]
            L: Grip length [mm]
            E: Member elastic modulus [MPa]

        Returns:
            Member stiffness [N/mm]
        """
        phi = np.radians(30)  # VDI 2230 deformation cone half-angle
        D_A = min(d_w + L * np.tan(phi), 3 * d)  # Effective frustum OD

        # VDI 2230 Eq. 5.1/25 (simplified)
        num = (d_w + d_h) * (D_A - d_h)
        den = (d_w - d_h) * (D_A + d_h)

        if den <= 0 or num <= 0 or d_w <= d_h:
            # Fallback: simple cylinder
            A_eff = np.pi / 4 * (d_w ** 2 - d_h ** 2)
            return E * A_eff / L if L > 0 else 1e9

        k = E * np.pi * d_w * np.tan(phi) / np.log(num / den)
        return k

    def _compute_joint_constant(self, p: 'PrototypeData') -> float:
        """Compute prototype joint constant C = kb/(kb+km) (CS1/M5)."""
        kb = self._compute_bolt_stiffness(
            p.bolt_diameter, p.thread_pitch, p.grip_length,
            p.bolt_elastic_modulus)
        km = self._compute_member_stiffness(
            p.bolt_diameter, p.washer_outer_diameter,
            p.clearance_hole_diameter, p.grip_length,
            p.member_elastic_modulus)
        return kb / (kb + km) if (kb + km) > 0 else 0.22

    def _compute_joint_constant_model(self, p: 'PrototypeData',
                                       lam: float) -> float:
        """Compute model joint constant with scaled geometry (CS1/M5)."""
        E_b = p.bolt_elastic_modulus * self.scales.elastic_modulus_ratio
        E_m = p.member_elastic_modulus * self.scales.elastic_modulus_ratio

        kb = self._compute_bolt_stiffness(
            p.bolt_diameter * lam, p.thread_pitch * lam,
            p.grip_length * lam, E_b)
        km = self._compute_member_stiffness(
            p.bolt_diameter * lam, p.washer_outer_diameter * lam,
            p.clearance_hole_diameter * lam, p.grip_length * lam, E_m)
        return kb / (kb + km) if (kb + km) > 0 else 0.22

    def _get_model_material_ratio(self, p: 'PrototypeData') -> float:
        """Get E/σy for model material (CS2/M6)."""
        E_m = self.model_elastic_modulus if self.model_elastic_modulus > 0 else p.bolt_elastic_modulus
        sy_m = self.model_yield_strength if self.model_yield_strength > 0 else p.bolt_yield_strength
        return E_m / sy_m

    def _calculate_pi_groups(self):
        """Calculate all dimensionless Π-groups."""
        p = self.prototype
        λ = self.scale_factor
        
        # Scaled model dimensions
        d_m = p.bolt_diameter * λ
        L_m = p.grip_length * λ
        t_m = p.flange_thickness * λ
        P_m = p.thread_pitch * λ
        
        # Stress area scales as λ²
        At_p = p.tensile_stress_area
        At_m = At_p * λ ** 2
        
        # Friction coefficient with scale effect
        mu_model = p.thread_friction_coefficient * (1 + 0.08 * (1 - λ))
        
        # Primary Π-groups (9 essential groups per literature)
        self.pi_groups = [
            # Π₁: Grip ratio (bolt flexibility)
            PiGroup(
                name="Grip Ratio",
                symbol="Π₁",
                expression="L/d",
                description="Bolt flexibility parameter",
                prototype_value=p.grip_length / p.bolt_diameter,
                model_value=L_m / d_m,
                tolerance=0.02,
                category="primary"
            ),
            
            # Π₂: Flange aspect ratio
            PiGroup(
                name="Flange Aspect",
                symbol="Π₂",
                expression="t/d",
                description="Flange stiffness parameter",
                prototype_value=p.flange_thickness / p.bolt_diameter,
                model_value=t_m / d_m,
                tolerance=0.02,
                category="primary"
            ),
            
            # Π₃: Preload utilization
            PiGroup(
                name="Preload Utilization",
                symbol="Π₃",
                expression="Fp/(σy·At)",
                description="Preload level relative to yield",
                prototype_value=p.preload_force / (p.bolt_yield_strength * At_p),
                model_value=(p.preload_force * self.scales.force) / (p.bolt_yield_strength * At_m),
                tolerance=0.05,
                category="primary"
            ),
            
            # Π₄: Load ratio (separation margin)
            PiGroup(
                name="Load Ratio",
                symbol="Π₄",
                expression="Fext/Fp",
                description="External load vs preload",
                prototype_value=p.external_axial_force / p.preload_force,
                model_value=p.external_axial_force / p.preload_force,  # Same ratio preserved
                tolerance=0.02,
                category="primary"
            ),
            
            # Π₅: Joint stiffness constant (CS1/M5: computed from actual stiffness)
            PiGroup(
                name="Joint Constant",
                symbol="Π₅",
                expression="C = kb/(kb+km)",
                description="Load partitioning factor",
                prototype_value=self._compute_joint_constant(p),
                model_value=self._compute_joint_constant_model(p, λ),
                tolerance=0.05,
                category="primary"
            ),
            
            # Π₆: Material ratio (CS2/M6: propagate model material when dissimilar)
            PiGroup(
                name="Material Ratio",
                symbol="Π₆",
                expression="E/σy",
                description="Material elasticity characteristic",
                prototype_value=p.bolt_elastic_modulus / p.bolt_yield_strength,
                model_value=self._get_model_material_ratio(p),
                tolerance=0.01 if self.material_similarity == MaterialSimilarity.SAME else 0.10,
                category="primary"
            ),
            
            # Π₇: Nut factor
            PiGroup(
                name="Nut Factor",
                symbol="Π₇",
                expression="K",
                description="Torque-tension relationship",
                prototype_value=p.nut_factor,
                model_value=p.nut_factor,  # Should be preserved
                tolerance=0.05,
                category="primary"
            ),
            
            # Π₈: Friction coefficient (subject to scale effects)
            PiGroup(
                name="Friction Coefficient",
                symbol="Π₈",
                expression="μ",
                description="Interface friction",
                prototype_value=p.thread_friction_coefficient,
                model_value=mu_model,
                tolerance=0.10,  # Higher tolerance for friction
                category="primary"
            ),
            
            # Π₉: Poisson's ratio
            PiGroup(
                name="Poisson's Ratio",
                symbol="Π₉",
                expression="ν",
                description="Lateral contraction ratio",
                prototype_value=p.bolt_poisson_ratio,
                model_value=p.bolt_poisson_ratio,
                tolerance=0.01,
                category="primary"
            ),
        ]
        
        # Secondary groups (geometric ratios)
        self.pi_groups.extend([
            PiGroup(
                name="Thread Pitch Ratio",
                symbol="Π₁₀",
                expression="P/d",
                description="Thread coarseness",
                prototype_value=p.thread_pitch / p.bolt_diameter,
                model_value=P_m / d_m,
                tolerance=0.02,
                category="secondary"
            ),
            
            PiGroup(
                name="Clearance Ratio",
                symbol="Π₁₁",
                expression="dh/d",
                description="Bolt hole clearance",
                prototype_value=p.clearance_hole_diameter / p.bolt_diameter,
                model_value=p.clearance_hole_diameter * λ / d_m,
                tolerance=0.05,
                category="secondary"
            ),
            
            PiGroup(
                name="Washer Coverage",
                symbol="Π₁₂",
                expression="dw/d",
                description="Washer load spread",
                prototype_value=p.washer_outer_diameter / p.bolt_diameter,
                model_value=p.washer_outer_diameter * λ / d_m,
                tolerance=0.05,
                category="secondary"
            ),
        ])
    
    def _detect_scale_effects(self):
        """Detect and quantify scale effects."""
        p = self.prototype
        λ = self.scale_factor
        d_m = p.bolt_diameter * λ
        
        self.scale_effects = [
            # Surface roughness (most significant)
            ScaleEffect.surface_roughness(
                p.surface_roughness_Rz,
                p.bolt_diameter,
                d_m
            ),
            
            # Friction coefficient
            ScaleEffect.friction_coefficient(
                p.thread_friction_coefficient,
                p.bolt_diameter,
                d_m
            ),
            
            # Embedding loss
            ScaleEffect.embedding_loss(
                p.embedding_per_interface,
                p.bolt_diameter,
                d_m,
                p.preload_force
            ),
            
            # Thread form tolerance
            ScaleEffect.thread_form_tolerance(λ),
            
            # Stress concentration (usually preserved)
            ScaleEffect.stress_concentration(
                p.bolt_diameter,
                d_m
            ),
        ]
    
    def _calculate_combined_correction(self):
        """Calculate combined correction factor from all scale effects."""
        self.combined_correction = 1.0
        for effect in self.scale_effects:
            if effect.severity not in [ScaleEffectSeverity.NEGLIGIBLE]:
                self.combined_correction *= effect.correction_factor
    
    def get_similitude_quality(self) -> str:
        """Assess overall similitude quality."""
        # Count matched Π-groups
        n_matched = sum(1 for pi in self.pi_groups if pi.is_matched)
        n_total = len(self.pi_groups)
        
        # Check critical effects
        critical_effects = [e for e in self.scale_effects 
                          if e.severity in [ScaleEffectSeverity.HIGH, 
                                           ScaleEffectSeverity.CRITICAL]]
        
        if n_matched == n_total and len(critical_effects) == 0:
            return "Excellent"
        elif n_matched >= n_total - 2 and len(critical_effects) == 0:
            return "Good"
        elif n_matched >= n_total - 3:
            return "Acceptable"
        else:
            return "Poor - review scale factor"
    
    def get_comparison_table(self) -> List[Dict[str, str]]:
        """Generate prototype vs model comparison table."""
        p = self.prototype
        λ = self.scale_factor
        
        # Force scale for stress similitude
        λ_F = self.scales.force
        λ_f = self.scales.frequency
        
        return [
            {
                "Parameter": "Bolt diameter (d)",
                "Prototype": f"{p.bolt_diameter:.1f} mm",
                "Model": f"{p.bolt_diameter * λ:.2f} mm",
                "Scale Factor": f"λ = {λ:.4f}"
            },
            {
                "Parameter": "Grip length (L)",
                "Prototype": f"{p.grip_length:.1f} mm",
                "Model": f"{p.grip_length * λ:.2f} mm",
                "Scale Factor": f"λ = {λ:.4f}"
            },
            {
                "Parameter": "Flange thickness (t)",
                "Prototype": f"{p.flange_thickness:.1f} mm",
                "Model": f"{p.flange_thickness * λ:.2f} mm",
                "Scale Factor": f"λ = {λ:.4f}"
            },
            {
                "Parameter": "Thread pitch (P)",
                "Prototype": f"{p.thread_pitch:.2f} mm",
                "Model": f"{p.thread_pitch * λ:.3f} mm",
                "Scale Factor": f"λ = {λ:.4f}"
            },
            {
                "Parameter": "Preload force (Fp)",
                "Prototype": f"{p.preload_force/1000:.1f} kN",
                "Model": f"{p.preload_force * λ_F / 1000:.2f} kN",
                "Scale Factor": f"λ² = {λ_F:.6f}"
            },
            {
                "Parameter": "External force (Fext)",
                "Prototype": f"{p.external_axial_force/1000:.1f} kN",
                "Model": f"{p.external_axial_force * λ_F / 1000:.2f} kN",
                "Scale Factor": f"λ² = {λ_F:.6f}"
            },
            {
                "Parameter": "Preload stress (σp)",
                "Prototype": f"{p.preload_utilization * p.bolt_yield_strength:.0f} MPa",
                "Model": f"{p.preload_utilization * p.bolt_yield_strength:.0f} MPa",
                "Scale Factor": "1.0 (preserved)"
            },
            {
                "Parameter": "Natural frequency (fn)",
                "Prototype": "f₀",
                "Model": f"f₀ × {λ_f:.2f}",
                "Scale Factor": f"1/λ = {λ_f:.4f}"
            },
            {
                "Parameter": "Tensile stress area (At)",
                "Prototype": f"{p.tensile_stress_area:.1f} mm²",
                "Model": f"{p.tensile_stress_area * λ**2:.2f} mm²",
                "Scale Factor": f"λ² = {λ**2:.6f}"
            },
        ]
    
    def get_pi_group_table(self) -> List[Dict[str, str]]:
        """Generate Π-group comparison table."""
        return [
            {
                "Symbol": pi.symbol,
                "Name": pi.name,
                "Expression": pi.expression,
                "Prototype": f"{pi.prototype_value:.4f}",
                "Model": f"{pi.model_value:.4f}",
                "Deviation": f"{pi.deviation_percent:.1f}%",
                "Status": pi.status_icon
            }
            for pi in self.pi_groups
        ]
    
    def get_scale_effects_table(self) -> List[Dict[str, str]]:
        """Generate scale effects summary table."""
        return [
            {
                "Effect": effect.name,
                "Parameter": effect.parameter,
                "Deviation": f"{effect.deviation_percent:+.1f}%",
                "Correction": f"{effect.correction_factor:.3f}",
                "Severity": effect.severity.value.upper(),
                "Icon": effect.severity_icon
            }
            for effect in self.scale_effects
        ]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get analysis statistics summary."""
        return {
            'scale_factor': self.scale_factor,
            'scale_ratio': self.scale_ratio_string,
            'prototype_diameter': self.prototype.bolt_diameter,
            'model_diameter': self.model_diameter,
            'prototype_preload': self.prototype.preload_force,
            'model_preload': self.model_preload,
            'n_pi_groups': len(self.pi_groups),
            'n_matched': sum(1 for pi in self.pi_groups if pi.is_matched),
            'n_scale_effects': len(self.scale_effects),
            'combined_correction': self.combined_correction,
            'quality': self.get_similitude_quality(),
        }
    
    def print_summary(self):
        """Print analysis summary to console."""
        stats = self.get_statistics()
        
        print("=" * 70)
        print(f"SIMILITUDE ANALYSIS SUMMARY - Scale {stats['scale_ratio']}")
        print("=" * 70)
        print(f"\nPrototype: d = {stats['prototype_diameter']:.1f} mm, "
              f"Fp = {stats['prototype_preload']/1000:.1f} kN")
        print(f"Model:     d = {stats['model_diameter']:.2f} mm, "
              f"Fp = {stats['model_preload']/1000:.3f} kN")
        
        print(f"\nΠ-Groups: {stats['n_matched']}/{stats['n_pi_groups']} matched")
        print("-" * 50)
        for pi in self.pi_groups[:9]:  # Primary groups
            print(f"  {pi.symbol} ({pi.name:20s}): "
                  f"{pi.prototype_value:8.4f} → {pi.model_value:8.4f} {pi.status_icon}")
        
        print(f"\nScale Effects:")
        print("-" * 50)
        for effect in self.scale_effects:
            print(f"  {effect.severity_icon} {effect.name:25s}: "
                  f"{effect.deviation_percent:+6.1f}% "
                  f"(Cf = {effect.correction_factor:.3f})")
        
        print(f"\nCombined Correction Factor: {stats['combined_correction']:.3f}")
        print(f"Overall Quality: {stats['quality']}")
        print("=" * 70)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert analysis to dictionary for serialization."""
        return {
            'prototype': self.prototype.to_dict(),
            'scale_factor': self.scale_factor,
            'material_similarity': self.material_similarity.value,
            'scale_factors': self.scales.get_all_factors(),
            'pi_groups': [pi.to_dict() for pi in self.pi_groups],
            'scale_effects': [effect.to_dict() for effect in self.scale_effects],
            'combined_correction': self.combined_correction,
            'statistics': self.get_statistics(),
        }
    
    def save(self, filepath: str):
        """Save analysis to JSON file."""
        with open(filepath, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SimilitudeAnalysis':
        """Create instance from dictionary."""
        prototype = PrototypeData.from_dict(data['prototype'])
        scale_factor = data['scale_factor']
        material_sim = MaterialSimilarity(data.get('material_similarity', 'same'))
        
        return cls(
            prototype=prototype,
            scale_factor=scale_factor,
            material_similarity=material_sim
        )
    
    @classmethod
    def load(cls, filepath: str) -> 'SimilitudeAnalysis':
        """Load analysis from JSON file."""
        with open(filepath, 'r') as f:
            data = json.load(f)
        return cls.from_dict(data)


# =============================================================================
# HS1: Thermal Scale Factors
# =============================================================================

@dataclass
class ThermalScaleFactors:
    """
    Thermal scaling factors for bolted joints (HS1).

    Accounts for thermal conductivity, diffusivity, and time constant
    differences between prototype and model.
    """
    # Thermal conductivity ratio (k_model / k_prototype)
    conductivity_ratio: float = 1.0    # [W/(m·K)]
    # Thermal diffusivity ratio (α_model / α_prototype)
    diffusivity_ratio: float = 1.0     # [m²/s]
    # Thermal expansion ratio (CTE_model / CTE_prototype)
    expansion_ratio: float = 1.0       # [1/K]
    # Geometric scale factor
    geometric: float = 0.25

    @property
    def time_constant_ratio(self) -> float:
        """Thermal time constant scales as λ² / α_ratio."""
        return self.geometric ** 2 / self.diffusivity_ratio

    @property
    def heat_flux_ratio(self) -> float:
        """Heat flux scales as k_ratio / λ."""
        return self.conductivity_ratio / self.geometric

    @property
    def thermal_stress_ratio(self) -> float:
        """Thermal stress scales with CTE and temperature."""
        return self.expansion_ratio  # σ_th ∝ α·ΔT·E

    def get_summary(self) -> Dict[str, float]:
        return {
            'conductivity_ratio': self.conductivity_ratio,
            'diffusivity_ratio': self.diffusivity_ratio,
            'expansion_ratio': self.expansion_ratio,
            'time_constant_ratio': self.time_constant_ratio,
            'heat_flux_ratio': self.heat_flux_ratio,
            'thermal_stress_ratio': self.thermal_stress_ratio,
        }


# =============================================================================
# HS2: Kuguel Fatigue Size Correction
# =============================================================================

def kuguel_fatigue_correction(V_model: float, V_prototype: float,
                               exponent: float = -0.07) -> float:
    """
    Kuguel fatigue size correction factor (HS2).

    C_fatigue = (V_model / V_prototype) ^ exponent

    Larger specimens have lower fatigue strength due to higher probability
    of containing critical defects (weakest-link theory).

    Args:
        V_model: Model stressed volume [mm³]
        V_prototype: Prototype stressed volume [mm³]
        exponent: Kuguel exponent (default -0.07 for steel)

    Returns:
        Fatigue correction factor (< 1 for larger specimens)
    """
    if V_prototype <= 0 or V_model <= 0:
        return 1.0
    return (V_model / V_prototype) ** exponent


def kuguel_from_scale(scale_factor: float, exponent: float = -0.07) -> float:
    """Kuguel correction from geometric scale (volume scales as λ³)."""
    V_ratio = scale_factor ** 3
    return V_ratio ** exponent


# =============================================================================
# HS3: Hersey Number Check for Lubrication Regime Preservation
# =============================================================================

def compute_hersey_number(mu: float, N: float, v: float,
                           F: float, A: float) -> float:
    """
    Compute Hersey number for lubrication regime check (HS3).

    H = μ·N·v / (F/A) = μ·N·v·A / F

    where:
    - μ: Dynamic viscosity of lubricant [Pa·s]
    - N: Rotational speed [rev/s]
    - v: Sliding velocity [m/s]
    - F: Normal force [N]
    - A: Contact area [m²]

    The Hersey number determines lubrication regime:
    - H < H_transition: Boundary lubrication
    - H ~ H_transition: Mixed lubrication
    - H > H_transition: Hydrodynamic lubrication

    Returns:
        Hersey number (dimensionless)
    """
    if F <= 0:
        return float('inf')
    return mu * N * v * A / F


def check_lubrication_regime_preservation(
    H_prototype: float, H_model: float,
    transition_H: float = 1e-7
) -> Dict[str, Any]:
    """
    Check if lubrication regime is preserved between prototype and model (HS3).

    Returns:
        Dictionary with regime comparison and warning flags
    """
    def classify(H):
        if H < transition_H * 0.1:
            return 'boundary'
        elif H < transition_H * 10:
            return 'mixed'
        else:
            return 'hydrodynamic'

    regime_p = classify(H_prototype)
    regime_m = classify(H_model)
    preserved = regime_p == regime_m

    return {
        'H_prototype': H_prototype,
        'H_model': H_model,
        'regime_prototype': regime_p,
        'regime_model': regime_m,
        'regime_preserved': preserved,
        'warning': None if preserved else
            f'Regime changed from {regime_p} to {regime_m}',
    }


# =============================================================================
# HS4: Multi-Scale Validation
# =============================================================================

@dataclass
class MultiScaleValidation:
    """
    Multi-scale validation analysis (HS4).

    Validates similitude by comparing results across multiple scale factors.
    Identifies optimal scale and detects scaling anomalies.
    """
    prototype: PrototypeData = None
    scale_factors: List[float] = field(default_factory=lambda: [0.5, 0.25, 0.125])

    # Results
    analyses: List[SimilitudeAnalysis] = field(default_factory=list)
    trend_quality: float = 0.0     # R² of scaling trend
    optimal_scale: float = 0.25    # Best trade-off scale
    outlier_scales: List[float] = field(default_factory=list)

    def run_validation(self):
        """Run similitude analysis at all scale factors."""
        if self.prototype is None:
            return

        self.analyses = []
        corrections = []

        for lam in self.scale_factors:
            analysis = SimilitudeAnalysis(
                prototype=self.prototype, scale_factor=lam)
            self.analyses.append(analysis)
            corrections.append(analysis.combined_correction)

        corrections = np.array(corrections)
        lams = np.array(self.scale_factors)

        # Trend verification: correction should vary smoothly with scale
        if len(corrections) >= 3:
            # Linear fit in log space
            log_lam = np.log(lams)
            log_corr = np.log(corrections)
            coeffs = np.polyfit(log_lam, log_corr, 1)
            fitted = np.polyval(coeffs, log_lam)
            ss_res = np.sum((log_corr - fitted) ** 2)
            ss_tot = np.sum((log_corr - np.mean(log_corr)) ** 2)
            self.trend_quality = 1 - ss_res / ss_tot if ss_tot > 0 else 1.0

            # Outlier detection: >2 std from trend
            residuals = log_corr - fitted
            std_res = np.std(residuals)
            self.outlier_scales = [
                lams[i] for i in range(len(residuals))
                if abs(residuals[i]) > 2 * std_res and std_res > 0
            ]

        # Optimal scale: closest to 1:4 that has good quality
        pi_qualities = [
            sum(1 for pi in a.pi_groups if pi.is_matched) / len(a.pi_groups)
            for a in self.analyses
        ]
        best_idx = max(range(len(pi_qualities)), key=lambda i: pi_qualities[i])
        self.optimal_scale = self.scale_factors[best_idx]

    def get_summary(self) -> Dict[str, Any]:
        return {
            'n_scales': len(self.scale_factors),
            'trend_quality_R2': self.trend_quality,
            'optimal_scale': self.optimal_scale,
            'outlier_scales': self.outlier_scales,
            'corrections': {
                f'1:{int(1/lam)}': a.combined_correction
                for lam, a in zip(self.scale_factors, self.analyses)
            },
        }


# =============================================================================
# HS5: Scale Effect With Uncertainty
# =============================================================================

@dataclass
class ScaleEffectWithUncertainty:
    """
    Scale effect with uncertainty range (HS5).

    Extends ScaleEffect with statistical uncertainty bounds.
    """
    name: str = ""
    correction_factor: float = 1.0
    uncertainty_low: float = 0.0     # Lower bound (Cf - uncertainty)
    uncertainty_high: float = 0.0    # Upper bound (Cf + uncertainty)
    confidence_level: float = 0.95   # Confidence level (default 95%)

    @property
    def uncertainty_range(self) -> Tuple[float, float]:
        """Correction factor range at specified confidence."""
        return (self.correction_factor - self.uncertainty_low,
                self.correction_factor + self.uncertainty_high)

    @classmethod
    def from_scale_effect(cls, effect: ScaleEffect,
                          relative_uncertainty: float = 0.10) -> 'ScaleEffectWithUncertainty':
        """Create from ScaleEffect with relative uncertainty estimate."""
        u = abs(effect.correction_factor - 1.0) * relative_uncertainty
        return cls(
            name=effect.name,
            correction_factor=effect.correction_factor,
            uncertainty_low=u,
            uncertainty_high=u,
        )


# =============================================================================
# HS6: Distorted Scale Factors (non-uniform scaling)
# =============================================================================

@dataclass
class DistortedScaleFactors:
    """
    Distorted (non-uniform) scale factors (HS6).

    When geometric similitude cannot be maintained in all directions,
    distorted scaling uses different factors for different dimensions.

    Reference: Liu et al. (2025) for distorted similitude methods.
    """
    lambda_axial: float = 0.25       # Axial direction scale factor
    lambda_radial: float = 0.25      # Radial direction scale factor
    lambda_thickness: float = 0.25   # Through-thickness scale factor

    # Material ratios
    elastic_modulus_ratio: float = 1.0
    density_ratio: float = 1.0

    @property
    def is_uniform(self) -> bool:
        """Check if scaling is geometrically uniform."""
        return (abs(self.lambda_axial - self.lambda_radial) < 1e-6 and
                abs(self.lambda_axial - self.lambda_thickness) < 1e-6)

    @property
    def distortion_ratio(self) -> float:
        """Ratio of max to min scale factor (1.0 = uniform)."""
        lams = [self.lambda_axial, self.lambda_radial, self.lambda_thickness]
        return max(lams) / min(lams) if min(lams) > 0 else float('inf')

    @property
    def force_axial(self) -> float:
        """Axial force scale: λ_r² × E_ratio."""
        return self.lambda_radial ** 2 * self.elastic_modulus_ratio

    @property
    def force_transverse(self) -> float:
        """Transverse force scale: λ_a × λ_r × E_ratio."""
        return self.lambda_axial * self.lambda_radial * self.elastic_modulus_ratio

    @property
    def stiffness_axial(self) -> float:
        """Axial stiffness: λ_r² × E_ratio / λ_a."""
        return self.lambda_radial ** 2 * self.elastic_modulus_ratio / self.lambda_axial

    @property
    def frequency(self) -> float:
        """Frequency scale: sqrt(E_ratio/ρ_ratio) / λ_a."""
        return np.sqrt(self.elastic_modulus_ratio / self.density_ratio) / self.lambda_axial

    def compute_distortion_corrections(self) -> Dict[str, float]:
        """Compute correction factors for distortion effects."""
        if self.is_uniform:
            return {'stiffness': 1.0, 'stress': 1.0, 'frequency': 1.0}

        # Stiffness distortion: member stiffness depends on both λ_r and λ_a
        k_ratio = self.lambda_radial / self.lambda_axial
        C_stiffness = k_ratio  # Stiffness changes with aspect ratio

        # Stress concentration: changes with thickness ratio
        t_ratio = self.lambda_thickness / self.lambda_radial
        C_stress = t_ratio ** 0.3  # Empirical exponent

        # Frequency distortion
        C_freq = (self.lambda_radial / self.lambda_axial) ** 0.5

        return {
            'stiffness': C_stiffness,
            'stress': C_stress,
            'frequency': C_freq,
            'combined': C_stiffness * C_stress,
        }


# =============================================================================
# HS7: Unified Pi Group Registry
# =============================================================================

class PiGroupCategory(Enum):
    """Category for Pi groups (HS7)."""
    CLASSICAL = "classical"       # Standard Buckingham-Pi groups
    LOOSENING = "loosening"       # Loosening-specific groups
    THERMAL = "thermal"           # Thermal scaling groups
    DYNAMIC = "dynamic"           # Dynamic response groups


@dataclass
class PiGroupDefinition:
    """Definition of a Pi group for the registry (HS7)."""
    name: str
    symbol: str
    expression: str
    description: str
    category: PiGroupCategory
    tolerance: float = 0.05
    is_critical: bool = False


class PiGroupRegistry:
    """
    Unified registry of all Pi groups used in similitude analysis (HS7).

    Combines CLASSICAL groups (from similitude.py) with LOOSENING groups
    (from loosening_similitude.py) into a single queryable registry.
    """

    _GROUPS = [
        # Classical groups
        PiGroupDefinition("Grip Ratio", "Pi1", "L/d", "Bolt flexibility",
                          PiGroupCategory.CLASSICAL, 0.02, True),
        PiGroupDefinition("Flange Aspect", "Pi2", "t/d", "Flange stiffness",
                          PiGroupCategory.CLASSICAL, 0.02, True),
        PiGroupDefinition("Preload Utilization", "Pi3", "Fp/(sy*At)", "Preload level",
                          PiGroupCategory.CLASSICAL, 0.05, True),
        PiGroupDefinition("Load Ratio", "Pi4", "Fext/Fp", "Separation margin",
                          PiGroupCategory.CLASSICAL, 0.02, True),
        PiGroupDefinition("Joint Constant", "Pi5", "kb/(kb+km)", "Load partition",
                          PiGroupCategory.CLASSICAL, 0.05, True),
        PiGroupDefinition("Material Ratio", "Pi6", "E/sy", "Material characteristic",
                          PiGroupCategory.CLASSICAL, 0.01),
        PiGroupDefinition("Nut Factor", "Pi7", "K", "Torque-tension",
                          PiGroupCategory.CLASSICAL, 0.05),
        PiGroupDefinition("Friction", "Pi8", "mu", "Interface friction",
                          PiGroupCategory.CLASSICAL, 0.10, True),
        PiGroupDefinition("Poisson Ratio", "Pi9", "nu", "Lateral contraction",
                          PiGroupCategory.CLASSICAL, 0.01),
        PiGroupDefinition("Pitch Ratio", "Pi10", "P/d", "Thread coarseness",
                          PiGroupCategory.CLASSICAL, 0.02),
        PiGroupDefinition("Clearance Ratio", "Pi11", "dh/d", "Hole clearance",
                          PiGroupCategory.CLASSICAL, 0.05),
        PiGroupDefinition("Washer Coverage", "Pi12", "dw/d", "Load spread",
                          PiGroupCategory.CLASSICAL, 0.05),

        # Loosening-specific groups
        PiGroupDefinition("Helix Ratio", "PiL1", "p/(pi*d2)", "Helix slope",
                          PiGroupCategory.LOOSENING, 0.02, True),
        PiGroupDefinition("Friction Margin", "PiL2", "mu/mu_crit", "Loosening margin",
                          PiGroupCategory.LOOSENING, 0.10, True),
        PiGroupDefinition("Slip Ratio", "PiL3", "Ft/(mu*Fp)", "Slip tendency",
                          PiGroupCategory.LOOSENING, 0.05, True),
        PiGroupDefinition("Preload Stiffness", "PiL4", "Fp/(kb*d)", "Preload-stiffness",
                          PiGroupCategory.LOOSENING, 0.10),
        PiGroupDefinition("Damping Ratio", "PiL5", "c/(2*sqrt(k*m))", "System damping",
                          PiGroupCategory.LOOSENING, 0.20),

        # Thermal groups
        PiGroupDefinition("Biot Number", "PiT1", "h*L/k", "Thermal coupling",
                          PiGroupCategory.THERMAL, 0.20),
        PiGroupDefinition("Thermal Expansion", "PiT2", "alpha*dT*E/sy", "Thermal stress",
                          PiGroupCategory.THERMAL, 0.10),
    ]

    @classmethod
    def get_all(cls) -> List[PiGroupDefinition]:
        """Get all Pi group definitions."""
        return cls._GROUPS.copy()

    @classmethod
    def get_by_category(cls, category: PiGroupCategory) -> List[PiGroupDefinition]:
        """Get Pi groups by category."""
        return [g for g in cls._GROUPS if g.category == category]

    @classmethod
    def get_critical(cls) -> List[PiGroupDefinition]:
        """Get critical Pi groups that must be matched."""
        return [g for g in cls._GROUPS if g.is_critical]

    @classmethod
    def get_by_symbol(cls, symbol: str) -> Optional[PiGroupDefinition]:
        """Get Pi group by symbol."""
        for g in cls._GROUPS:
            if g.symbol == symbol:
                return g
        return None


# =============================================================================
# MS3: Monte Carlo Uncertainty Propagation
# =============================================================================

def monte_carlo_prototype_prediction(
    model_values: np.ndarray,
    scale_factors: ScaleFactors,
    corrections: Dict[str, float],
    n_samples: int = 10000,
    param_uncertainty: float = 0.05,
    seed: int = None
) -> Dict[str, Any]:
    """
    Monte Carlo uncertainty propagation for prototype predictions (MS3).

    Propagates uncertainties in scale factors, corrections, and measurements
    through the scaling transformation to estimate prototype prediction bounds.

    Args:
        model_values: Measured model values (e.g., preload decay curve)
        scale_factors: Nominal scale factors
        corrections: Dict of correction factor names and values
        n_samples: Number of Monte Carlo samples
        param_uncertainty: Relative parameter uncertainty (default 5%)
        seed: Random seed for reproducibility

    Returns:
        Dictionary with mean, std, percentiles of prototype predictions
    """
    rng = np.random.default_rng(seed)

    n_data = len(model_values)
    predictions = np.zeros((n_samples, n_data))

    # Scale factor for the quantity (assume force)
    nominal_scale = scale_factors.force

    # Total correction
    nominal_correction = 1.0
    for v in corrections.values():
        nominal_correction *= v

    for i in range(n_samples):
        # Perturbed scale factor
        sf_perturbed = nominal_scale * (1 + rng.normal(0, param_uncertainty))

        # Perturbed corrections
        corr_perturbed = 1.0
        for v in corrections.values():
            corr_perturbed *= v * (1 + rng.normal(0, param_uncertainty * 0.5))

        # Perturbed measurement
        meas_perturbed = model_values * (1 + rng.normal(0, param_uncertainty * 0.3, n_data))

        # Prototype prediction: model / scale × correction
        predictions[i] = meas_perturbed / sf_perturbed * corr_perturbed

    return {
        'mean': np.mean(predictions, axis=0),
        'std': np.std(predictions, axis=0),
        'p5': np.percentile(predictions, 5, axis=0),
        'p95': np.percentile(predictions, 95, axis=0),
        'p25': np.percentile(predictions, 25, axis=0),
        'p75': np.percentile(predictions, 75, axis=0),
        'n_samples': n_samples,
        'nominal': model_values / nominal_scale * nominal_correction,
    }


# =============================================================================
# MS4: Equivalence Mode Enum
# =============================================================================

class EquivalenceMode(Enum):
    """Equivalence mode for multi-bolt reduction (MS4)."""
    AREA = "area"             # Match total stress area
    STIFFNESS = "stiffness"   # Match joint stiffness ratio
    PRELOAD = "preload"       # Match total preload
    LOOSENING = "loosening"   # Match loosening behavior (Pi groups)


# =============================================================================
# MS5: Expanded Bolt Database (UNF, BSP/BSW)
# =============================================================================

def find_standard_bolt_size(target_diameter: float, standard: str = "ISO") -> Tuple[float, float]:
    """
    Find nearest standard bolt size to target diameter (MS5 expanded).

    Args:
        target_diameter: Target diameter in mm
        standard: "ISO", "UNC", "UNF", "BSP", or "BSW"

    Returns:
        Tuple of (diameter, pitch)
    """
    bolt_databases = _get_bolt_databases()
    key = standard.upper()
    if key not in bolt_databases:
        raise ValueError(f"Unknown standard '{standard}'. Choose from: {list(bolt_databases.keys())}")

    sizes = bolt_databases[key]
    closest = min(sizes, key=lambda x: abs(x[0] - target_diameter))
    return closest


def _get_bolt_databases() -> Dict[str, List[Tuple[float, float]]]:
    """Return all bolt databases keyed by standard name (MS5)."""
    return {
        "ISO": [
            # ISO metric coarse thread sizes (d [mm], P [mm])
            (3, 0.5), (4, 0.7), (5, 0.8), (6, 1.0), (8, 1.25),
            (10, 1.5), (12, 1.75), (14, 2.0), (16, 2.0), (18, 2.5),
            (20, 2.5), (22, 2.5), (24, 3.0), (27, 3.0), (30, 3.5),
            (33, 3.5), (36, 4.0), (39, 4.0), (42, 4.5), (45, 4.5),
            (48, 5.0), (52, 5.0), (56, 5.5), (60, 5.5), (64, 6.0),
        ],
        "UNC": [
            # Unified National Coarse (d [mm], pitch [mm])
            (6.35, 1.27),    # 1/4"-20
            (7.94, 1.41),    # 5/16"-18
            (9.53, 1.59),    # 3/8"-16
            (11.11, 1.81),   # 7/16"-14
            (12.70, 2.12),   # 1/2"-13
            (14.29, 2.31),   # 9/16"-12
            (15.88, 2.54),   # 5/8"-11
            (19.05, 2.82),   # 3/4"-10
            (22.23, 3.18),   # 7/8"-9
            (25.40, 3.18),   # 1"-8
            (28.58, 3.63),   # 1-1/8"-7
            (31.75, 3.63),   # 1-1/4"-7
            (38.10, 4.23),   # 1-1/2"-6
        ],
        "UNF": [
            # Unified National Fine (d [mm], pitch [mm])
            (6.35, 0.907),   # 1/4"-28
            (7.94, 0.907),   # 5/16"-24
            (9.53, 1.058),   # 3/8"-24
            (11.11, 1.270),  # 7/16"-20
            (12.70, 1.270),  # 1/2"-20
            (14.29, 1.411),  # 9/16"-18
            (15.88, 1.411),  # 5/8"-18
            (19.05, 1.588),  # 3/4"-16
            (22.23, 1.814),  # 7/8"-14
            (25.40, 2.117),  # 1"-12
            (28.58, 2.117),  # 1-1/8"-12
            (31.75, 2.117),  # 1-1/4"-12
            (38.10, 2.117),  # 1-1/2"-12
        ],
        "BSP": [
            # British Standard Pipe (nominal bore→OD [mm], pitch [mm])
            (9.728, 0.907),   # 1/8" BSP - 28 TPI
            (13.157, 1.337),  # 1/4" BSP - 19 TPI
            (16.662, 1.337),  # 3/8" BSP - 19 TPI
            (20.955, 1.814),  # 1/2" BSP - 14 TPI
            (26.441, 1.814),  # 3/4" BSP - 14 TPI
            (33.249, 2.309),  # 1" BSP   - 11 TPI
            (41.910, 2.309),  # 1-1/4" BSP
            (47.803, 2.309),  # 1-1/2" BSP
            (59.614, 2.309),  # 2" BSP
        ],
        "BSW": [
            # British Standard Whitworth (d [mm], pitch [mm])
            (6.35, 1.270),    # 1/4" BSW - 20 TPI
            (7.94, 1.411),    # 5/16" BSW - 18 TPI
            (9.53, 1.588),    # 3/8" BSW - 16 TPI
            (11.11, 1.814),   # 7/16" BSW - 14 TPI
            (12.70, 2.117),   # 1/2" BSW - 12 TPI
            (15.88, 2.309),   # 5/8" BSW - 11 TPI
            (19.05, 2.540),   # 3/4" BSW - 10 TPI
            (22.23, 2.822),   # 7/8" BSW - 9 TPI
            (25.40, 3.175),   # 1" BSW - 8 TPI
            (31.75, 3.629),   # 1-1/4" BSW - 7 TPI
            (38.10, 4.233),   # 1-1/2" BSW - 6 TPI
        ],
    }


def get_available_standards() -> List[str]:
    """Return list of available bolt standards."""
    return list(_get_bolt_databases().keys())


def calculate_standard_scales() -> Dict[str, float]:
    """
    Return dictionary of common scale factors.
    
    Returns:
        Dictionary mapping scale ratio strings to lambda values
    """
    return {
        "1:1": 1.0,
        "1:2": 0.5,
        "1:2.5": 0.4,
        "1:3": 1/3,
        "1:4": 0.25,
        "1:5": 0.2,
        "1:6": 1/6,
        "1:8": 0.125,
        "1:10": 0.1,
    }


def interpolate_prototype_results(model_results: np.ndarray,
                                  scale_factors: ScaleFactors,
                                  quantity: str = "force") -> np.ndarray:
    """
    Scale model test results to prototype predictions.
    
    Args:
        model_results: Array of measured values from model test
        scale_factors: ScaleFactors instance
        quantity: Type of quantity ("force", "displacement", "stress", "time")
    
    Returns:
        Array of scaled prototype predictions
    """
    scale_map = {
        "force": scale_factors.force,
        "displacement": scale_factors.displacement,
        "stress": scale_factors.stress,
        "time": scale_factors.time,
        "frequency": scale_factors.frequency,
        "acceleration": scale_factors.acceleration,
    }
    
    if quantity not in scale_map:
        raise ValueError(f"Unknown quantity: {quantity}")
    
    # Prototype = Model / scale_factor
    return model_results / scale_map[quantity]


# =============================================================================
# MS6: Dynamic Similitude Verification
# =============================================================================

def verify_dynamic_similitude(
    prototype: 'PrototypeData',
    model_diameter: float,
    model_preload: float,
    model_external_force: float,
    model_frequency: float,
    scale_factor: float,
    tolerance: float = 0.10
) -> Dict[str, Any]:
    """
    Verify dynamic similitude between prototype and model (MS6).

    Checks that force ratios, frequency ratios, and stress ratios
    are consistent with the specified geometric scale factor.

    Args:
        prototype: Prototype data
        model_diameter: Model bolt diameter [mm]
        model_preload: Model preload force [N]
        model_external_force: Model external force [N]
        model_frequency: Model test frequency [Hz]
        scale_factor: Geometric scale factor lambda
        tolerance: Acceptable relative deviation

    Returns:
        Dict with verification results and pass/fail flags
    """
    lam = scale_factor
    checks = []

    # Force ratio: should scale as lambda^2
    expected_force_ratio = lam ** 2
    actual_force_ratio = model_preload / prototype.preload_force if prototype.preload_force > 0 else 0
    force_dev = abs(actual_force_ratio - expected_force_ratio) / expected_force_ratio if expected_force_ratio > 0 else 0
    checks.append({
        'parameter': 'Preload force ratio',
        'expected': expected_force_ratio,
        'actual': actual_force_ratio,
        'deviation': force_dev,
        'pass': force_dev <= tolerance,
    })

    # External force ratio
    if prototype.external_axial_force > 0 and model_external_force > 0:
        actual_ext_ratio = model_external_force / prototype.external_axial_force
        ext_dev = abs(actual_ext_ratio - expected_force_ratio) / expected_force_ratio
        checks.append({
            'parameter': 'External force ratio',
            'expected': expected_force_ratio,
            'actual': actual_ext_ratio,
            'deviation': ext_dev,
            'pass': ext_dev <= tolerance,
        })

    # Frequency ratio: should scale as 1/lambda
    expected_freq_ratio = 1.0 / lam
    proto_freq = getattr(prototype, 'frequency', 0)
    if proto_freq > 0 and model_frequency > 0:
        actual_freq_ratio = model_frequency / proto_freq
        freq_dev = abs(actual_freq_ratio - expected_freq_ratio) / expected_freq_ratio
        checks.append({
            'parameter': 'Frequency ratio',
            'expected': expected_freq_ratio,
            'actual': actual_freq_ratio,
            'deviation': freq_dev,
            'pass': freq_dev <= tolerance,
        })

    # Diameter ratio: should scale as lambda
    actual_d_ratio = model_diameter / prototype.bolt_diameter if prototype.bolt_diameter > 0 else 0
    d_dev = abs(actual_d_ratio - lam) / lam if lam > 0 else 0
    checks.append({
        'parameter': 'Diameter ratio',
        'expected': lam,
        'actual': actual_d_ratio,
        'deviation': d_dev,
        'pass': d_dev <= tolerance,
    })

    # Stress preservation: sigma_m / sigma_p should be ~1 (for same material)
    # Stress = F / A, A scales as lambda^2, F scales as lambda^2 => sigma_m = sigma_p
    proto_At = prototype.tensile_stress_area
    model_pitch = find_standard_bolt_size(model_diameter, "ISO")[1]
    d2_m = model_diameter - 0.6495 * model_pitch
    d1_m = model_diameter - 1.0825 * model_pitch
    model_At = np.pi / 4 * ((d2_m + d1_m) / 2) ** 2
    if proto_At > 0 and model_At > 0:
        sigma_proto = prototype.preload_force / proto_At
        sigma_model = model_preload / model_At
        stress_ratio = sigma_model / sigma_proto if sigma_proto > 0 else 0
        stress_dev = abs(stress_ratio - 1.0)
        checks.append({
            'parameter': 'Stress preservation',
            'expected': 1.0,
            'actual': stress_ratio,
            'deviation': stress_dev,
            'pass': stress_dev <= tolerance,
        })

    all_pass = all(c['pass'] for c in checks)
    n_pass = sum(1 for c in checks if c['pass'])

    return {
        'checks': checks,
        'all_pass': all_pass,
        'n_pass': n_pass,
        'n_total': len(checks),
        'quality': n_pass / len(checks) if checks else 0,
    }


# =============================================================================
# MS8: Scale Factor Sensitivity Analysis
# =============================================================================

def scale_factor_sensitivity(
    prototype: 'PrototypeData',
    base_scale: float = 0.25,
    perturbation: float = 0.01,
    parameters: List[str] = None
) -> Dict[str, Dict[str, float]]:
    """
    Sensitivity analysis of Pi groups to scale factor perturbation (MS8).

    Computes normalized sensitivity: dPi/dlambda * lambda/Pi for each
    Pi group, showing how sensitive each group is to scale changes.

    Args:
        prototype: Prototype data
        base_scale: Nominal scale factor
        perturbation: Relative perturbation for finite differences
        parameters: List of Pi group names to analyze (None = all)

    Returns:
        Dict mapping Pi group names to sensitivity metrics
    """
    lam = base_scale
    dlam = lam * perturbation

    # Base analysis
    analysis_base = SimilitudeAnalysis(prototype=prototype, scale_factor=lam)

    # Perturbed analysis
    analysis_plus = SimilitudeAnalysis(prototype=prototype, scale_factor=lam + dlam)
    analysis_minus = SimilitudeAnalysis(prototype=prototype, scale_factor=lam - dlam)

    sensitivities = {}

    for i, pi_base in enumerate(analysis_base.pi_groups):
        if parameters is not None and pi_base.name not in parameters:
            continue

        pi_plus = analysis_plus.pi_groups[i] if i < len(analysis_plus.pi_groups) else None
        pi_minus = analysis_minus.pi_groups[i] if i < len(analysis_minus.pi_groups) else None

        if pi_plus is None or pi_minus is None:
            continue

        # Central difference
        dpi = pi_plus.model_value - pi_minus.model_value
        dpi_dlam = dpi / (2 * dlam) if dlam > 0 else 0

        # Normalized sensitivity
        pi_val = pi_base.model_value
        normalized = dpi_dlam * lam / pi_val if abs(pi_val) > 1e-12 else 0

        sensitivities[pi_base.name] = {
            'pi_value': pi_val,
            'absolute_sensitivity': dpi_dlam,
            'normalized_sensitivity': normalized,
            'deviation_at_base': pi_base.deviation_percent,
            'is_sensitive': abs(normalized) > 0.5,
        }

    return sensitivities


# =============================================================================
# Test Suite
# =============================================================================

def run_tests():
    """Run comprehensive test suite."""
    print("=" * 70)
    print("SIMILITUDE ANALYSIS MODULE - TEST SUITE")
    print("Bolt Analysis Studio v4.0")
    print("=" * 70)
    
    # Test 1: Basic scale factors
    print("\n[Test 1] Scale Factors (λ = 0.25)")
    scales = ScaleFactors(geometric=0.25)
    print(f"  Length:      {scales.length:.4f}")
    print(f"  Area:        {scales.area:.6f}")
    print(f"  Force:       {scales.force:.6f}")
    print(f"  Frequency:   {scales.frequency:.4f}")
    print(f"  Stiffness:   {scales.stiffness:.4f}")
    
    assert abs(scales.length - 0.25) < 1e-10
    assert abs(scales.area - 0.0625) < 1e-10
    assert abs(scales.frequency - 4.0) < 1e-10
    print("  ✓ Scale factors correct")
    
    # Test 2: Prototype data
    print("\n[Test 2] Prototype Data")
    proto = PrototypeData(
        bolt_diameter=24.0,
        grip_length=100.0,
        flange_thickness=30.0,
        thread_pitch=3.0,
        preload_force=160000.0,
        external_axial_force=48000.0,
        bolt_yield_strength=724.0,
    )
    print(f"  At = {proto.tensile_stress_area:.1f} mm²")
    print(f"  Preload util = {proto.preload_utilization:.1%}")
    print(f"  Load ratio = {proto.load_ratio:.3f}")
    print(f"  Grip ratio L/d = {proto.grip_ratio:.2f}")
    
    assert proto.grip_ratio == 100/24
    assert proto.load_ratio == 48000/160000
    print("  ✓ Prototype data correct")
    
    # Test 3: Similitude analysis
    print("\n[Test 3] Complete Similitude Analysis")
    analysis = SimilitudeAnalysis(prototype=proto, scale_factor=0.25)
    print(f"  Model diameter: {analysis.model_diameter:.1f} mm")
    print(f"  Model preload:  {analysis.model_preload:.0f} N")
    print(f"  Π-groups: {len(analysis.pi_groups)}")
    print(f"  Scale effects: {len(analysis.scale_effects)}")
    
    # Check Π₁ (grip ratio) is preserved
    pi1 = analysis.pi_groups[0]
    assert abs(pi1.deviation_percent) < 0.1, "Grip ratio should be preserved"
    print(f"  Π₁ (L/d): {pi1.prototype_value:.3f} → {pi1.model_value:.3f} {pi1.status_icon}")
    print("  ✓ Π-groups calculated")
    
    # Test 4: Scale effects
    print("\n[Test 4] Scale Effects Detection")
    for effect in analysis.scale_effects[:3]:
        print(f"  {effect.severity_icon} {effect.name}: "
              f"{effect.deviation_percent:+.1f}% (Cf={effect.correction_factor:.3f})")
    
    assert analysis.combined_correction > 1.0, "Combined correction should be > 1"
    print(f"  Combined: {analysis.combined_correction:.3f}")
    print("  ✓ Scale effects detected")
    
    # Test 5: Serialization
    print("\n[Test 5] JSON Serialization")
    analysis.save("/tmp/test_similitude.json")
    loaded = SimilitudeAnalysis.load("/tmp/test_similitude.json")
    assert len(loaded.pi_groups) == len(analysis.pi_groups)
    print(f"  Saved and loaded: {len(loaded.pi_groups)} Π-groups")
    print("  ✓ Serialization works")
    
    # Test 6: Standard bolt size lookup
    print("\n[Test 6] Standard Bolt Size Lookup")
    d, P = find_standard_bolt_size(5.5, "ISO")
    print(f"  Target 5.5 mm → M{d} × {P}")
    assert d in [5.0, 6.0]  # Nearest to 5.5 can be M5 or M6
    
    d, P = find_standard_bolt_size(13.0, "UNC")
    print(f"  Target 13.0 mm → d={d:.2f} mm (1/2\" UNC)")
    print("  ✓ Bolt size lookup works")
    
    # Test 7: Different scale factors
    print("\n[Test 7] Multiple Scale Factors")
    for ratio, lam in [("1:2", 0.5), ("1:4", 0.25), ("1:8", 0.125)]:
        analysis_i = SimilitudeAnalysis(prototype=proto, scale_factor=lam)
        print(f"  {ratio}: d_m={analysis_i.model_diameter:.1f} mm, "
              f"Fp_m={analysis_i.model_preload:.0f} N, "
              f"Cf={analysis_i.combined_correction:.3f}")
    print("  ✓ Multi-scale analysis works")
    
    # Test 8: Summary output
    print("\n[Test 8] Analysis Summary")
    analysis.print_summary()
    
    print("\n" + "=" * 70)
    print("ALL TESTS PASSED ✓")
    print("=" * 70)


if __name__ == "__main__":
    run_tests()
