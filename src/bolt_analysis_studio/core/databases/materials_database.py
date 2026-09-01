"""
Materials and Tribology Database for Bolt Analysis Studio v4.0
BAS +  R&D

Comprehensive database of material properties, friction coefficients, coatings,
and lubricants for MSD-based bolted joint analysis with Oil & Gas focus.

Based on:
- ASTM A193/A194 specifications
- ISO 898-1 property classes
- NACE MR0175 / ISO 15156 (sour service)
- API 6A, 17D, 20E, 20F specifications
- VDI 2230 guidelines
-  N-1692 standards

Author: Bolt Analysis Studio Team
Version: 4.0
Date: January 2026
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum, auto
import math


# =============================================================================
# ENUMERATIONS
# =============================================================================

class MaterialCategory(Enum):
    """Material categories."""
    CARBON_STEEL = "Carbon Steel"
    LOW_ALLOY_STEEL = "Low Alloy Steel"
    STAINLESS_AUSTENITIC = "Austenitic Stainless Steel"
    STAINLESS_DUPLEX = "Duplex Stainless Steel"
    STAINLESS_SUPER_DUPLEX = "Super Duplex Stainless Steel"
    NICKEL_ALLOY = "Nickel Alloy"
    TITANIUM = "Titanium"
    GASKET_MATERIAL = "Gasket Material"


class CoatingType(Enum):
    """Surface coating types."""
    NONE = "None (Bare)"
    ZINC_ELECTROPLATED = "Zinc Electroplated"
    ZINC_HOT_DIP = "Hot-Dip Galvanized"
    ZINC_FLAKE = "Zinc Flake (Geomet/Dacromet)"
    ZINC_FLAKE_TOPCOAT = "Zinc Flake + Topcoat"
    PHOSPHATE_OIL = "Phosphate & Oil"
    CADMIUM = "Cadmium (Restricted)"
    PTFE = "PTFE Coating"
    MOLYBDENUM_DISULFIDE = "MoS2 Coating"
    NICKEL = "Nickel Plating"
    CHROME = "Chrome Plating"
    TSA = "Thermal Spray Aluminum"


class LubricantType(Enum):
    """Lubricant/anti-seize types."""
    NONE = "None (Dry)"
    MACHINE_OIL = "Machine Oil"
    MOLY_PASTE = "Molybdenum Disulfide Paste"
    COPPER_ANTISEIZE = "Copper Anti-Seize"
    NICKEL_ANTISEIZE = "Nickel Anti-Seize"
    PTFE_PASTE = "PTFE Paste"
    THREAD_COMPOUND = "Thread Compound (API)"
    NEVER_SEEZ = "Never-Seez (Nickel)"
    LOCTITE = "Loctite (Threadlocker)"
    BESTOLIFE = "Bestolife (O&G)"
    JET_LUBE = "Jet-Lube AP-5"


class LoadDistributionLaw(Enum):
    """Thread load distribution laws."""
    EQUAL = "Equal (1/n)"
    LINEAR = "Linear"
    POWER = "Power Law"
    EXPONENTIAL = "Exponential (Sopwith)"
    YAMAMOTO = "Yamamoto"
    CUSTOM = "Custom"


class EnvironmentType(Enum):
    """Service environment types."""
    ATMOSPHERIC_MILD = "Atmospheric - Mild"
    ATMOSPHERIC_INDUSTRIAL = "Atmospheric - Industrial"
    ATMOSPHERIC_MARINE = "Atmospheric - Marine"
    SPLASH_ZONE = "Splash Zone"
    IMMERSION_SEAWATER = "Seawater Immersion"
    SOUR_SERVICE = "Sour Service (H2S)"
    HIGH_TEMPERATURE = "High Temperature (>200°C)"
    CRYOGENIC = "Cryogenic (<-50°C)"
    SUBSEA = "Subsea"


class GasketType(Enum):
    """Gasket types."""
    SPIRAL_WOUND = "Spiral Wound"
    SPIRAL_WOUND_IR = "Spiral Wound with Inner Ring"
    RING_JOINT = "Ring Joint (RTJ)"
    SHEET_COMPRESSED = "Compressed Sheet"
    SHEET_PTFE = "PTFE Sheet"
    KAMMPROFILE = "Kammprofile"
    CORRUGATED_METAL = "Corrugated Metal"
    METAL_JACKETED = "Metal Jacketed"


# =============================================================================
# MATERIAL DATA CLASS
# =============================================================================

@dataclass
class MaterialProperties:
    """Complete material property definition."""
    # Identification
    name: str
    grade: str
    specification: str
    category: MaterialCategory

    # Mechanical Properties
    E: float = 205000.0          # Young's modulus [MPa]
    G: float = 80000.0           # Shear modulus [MPa]
    nu: float = 0.29             # Poisson's ratio [-]
    rho: float = 7850.0          # Density [kg/m³]
    Sy: float = 720.0            # Yield strength [MPa]
    Su: float = 860.0            # Ultimate strength [MPa]
    elongation: float = 16.0     # Elongation [%]
    hardness_hrc: float = 28.0   # Hardness [HRC]
    hardness_hb: float = 280.0   # Hardness [HB]

    # Thermal Properties
    alpha: float = 12.0e-6       # Thermal expansion [1/°C]
    k_thermal: float = 42.0      # Thermal conductivity [W/(m·K)]
    T_max: float = 450.0         # Max service temperature [°C]
    T_min: float = -40.0         # Min service temperature [°C]

    # Damping
    zeta: float = 0.003          # Material damping ratio [-]

    # Corrosion Properties
    PREN: Optional[float] = None  # Pitting Resistance Equivalent Number
    sour_service: bool = False    # NACE MR0175 compliant
    max_hardness_sour: float = 22.0  # Max HRC for sour service

    # Temperature Derating (percentage of Sy at temperature)
    temp_derating: Dict[float, float] = field(default_factory=lambda: {
        20: 1.0, 100: 1.0, 200: 0.93, 300: 0.88, 400: 0.82, 450: 0.78
    })

    # Notes
    applications: str = ""
    restrictions: str = ""
    pairing_nut: str = ""  # Recommended nut grade

    def get_Sy_at_temp(self, T: float) -> float:
        """Get yield strength at temperature with interpolation."""
        temps = sorted(self.temp_derating.keys())
        if T <= temps[0]:
            return self.Sy * self.temp_derating[temps[0]]
        if T >= temps[-1]:
            return self.Sy * self.temp_derating[temps[-1]]

        # Linear interpolation
        for i in range(len(temps) - 1):
            if temps[i] <= T <= temps[i+1]:
                t1, t2 = temps[i], temps[i+1]
                f1, f2 = self.temp_derating[t1], self.temp_derating[t2]
                factor = f1 + (f2 - f1) * (T - t1) / (t2 - t1)
                return self.Sy * factor
        return self.Sy


# =============================================================================
# MATERIALS DATABASE
# =============================================================================

MATERIALS_DATABASE: Dict[str, MaterialProperties] = {
    # -------------------------------------------------------------------------
    # ISO 898-1 Property Classes
    # -------------------------------------------------------------------------
    "ISO_8.8": MaterialProperties(
        name="Property Class 8.8",
        grade="8.8",
        specification="ISO 898-1",
        category=MaterialCategory.CARBON_STEEL,
        E=205000, G=80000, nu=0.29, rho=7850,
        Sy=640, Su=800, elongation=12,
        hardness_hrc=27, hardness_hb=280,
        alpha=11.7e-6, T_max=300, T_min=-40,
        zeta=0.003,
        applications="General purpose, non-critical",
        restrictions="Not for H2S, subsea, or high-temp",
        pairing_nut="ISO 8"
    ),

    "ISO_10.9": MaterialProperties(
        name="Property Class 10.9",
        grade="10.9",
        specification="ISO 898-1",
        category=MaterialCategory.LOW_ALLOY_STEEL,
        E=205000, G=80000, nu=0.29, rho=7850,
        Sy=900, Su=1040, elongation=9,
        hardness_hrc=35, hardness_hb=340,
        alpha=12.0e-6, T_max=300, T_min=-50,
        zeta=0.003,
        applications="High-strength applications",
        restrictions="H2 embrittlement risk, caution with H2S",
        pairing_nut="ISO 10"
    ),

    "ISO_12.9": MaterialProperties(
        name="Property Class 12.9",
        grade="12.9",
        specification="ISO 898-1",
        category=MaterialCategory.LOW_ALLOY_STEEL,
        E=205000, G=80000, nu=0.29, rho=7850,
        Sy=1080, Su=1220, elongation=8,
        hardness_hrc=42, hardness_hb=400,
        alpha=12.0e-6, T_max=300, T_min=-50,
        zeta=0.002,
        applications="Very high-strength applications",
        restrictions="High H2 embrittlement risk",
        pairing_nut="ISO 12"
    ),

    # -------------------------------------------------------------------------
    # ASTM A193 High-Temperature Grades
    # -------------------------------------------------------------------------
    "A193_B7": MaterialProperties(
        name="ASTM A193 Grade B7",
        grade="B7",
        specification="ASTM A193",
        category=MaterialCategory.LOW_ALLOY_STEEL,
        E=205000, G=80000, nu=0.29, rho=7850,
        Sy=720, Su=860, elongation=16,
        hardness_hrc=28, hardness_hb=280,
        alpha=12.3e-6, k_thermal=42, T_max=450, T_min=-40,
        zeta=0.003,
        sour_service=False,
        temp_derating={20: 1.0, 100: 1.0, 200: 0.93, 300: 0.88, 400: 0.82, 450: 0.78},
        applications="Pressure vessels, heat exchangers, valves, flanges - MOST COMMON O&G",
        restrictions="NOT for sour service (use B7M)",
        pairing_nut="A194 2H"
    ),

    "A193_B7M": MaterialProperties(
        name="ASTM A193 Grade B7M (Sour Service)",
        grade="B7M",
        specification="ASTM A193",
        category=MaterialCategory.LOW_ALLOY_STEEL,
        E=205000, G=80000, nu=0.29, rho=7850,
        Sy=550, Su=690, elongation=18,
        hardness_hrc=22, hardness_hb=235,  # MAX 22 HRC for sour
        alpha=12.3e-6, k_thermal=42, T_max=450, T_min=-40,
        zeta=0.003,
        sour_service=True,
        max_hardness_sour=22.0,
        applications="H2S environments, sour gas, amine systems - NACE MR0175 compliant",
        restrictions="Lower strength than B7",
        pairing_nut="A194 2HM"
    ),

    "A193_B16": MaterialProperties(
        name="ASTM A193 Grade B16",
        grade="B16",
        specification="ASTM A193",
        category=MaterialCategory.LOW_ALLOY_STEEL,
        E=205000, G=80000, nu=0.29, rho=7850,
        Sy=690, Su=860, elongation=16,
        hardness_hrc=28, hardness_hb=280,
        alpha=12.0e-6, k_thermal=42, T_max=540, T_min=-29,
        zeta=0.003,
        temp_derating={20: 1.0, 100: 1.0, 200: 0.97, 300: 0.95, 400: 0.90, 500: 0.83, 540: 0.78},
        applications="High-temperature service (steam, fired heaters, hydroprocessing)",
        restrictions="Not for sour service",
        pairing_nut="A194 4 or 7"
    ),

    "A320_L7": MaterialProperties(
        name="ASTM A320 Grade L7 (Low Temp)",
        grade="L7",
        specification="ASTM A320",
        category=MaterialCategory.LOW_ALLOY_STEEL,
        E=207000, G=80000, nu=0.29, rho=7850,
        Sy=724, Su=862, elongation=16,
        hardness_hrc=28, hardness_hb=280,
        alpha=12.3e-6, k_thermal=42, T_max=345, T_min=-101,
        zeta=0.003,
        sour_service=False,
        applications="Cryogenic / low-temperature service (LNG, cold-box piping, Junker test specimens)",
        restrictions="Requires Charpy V-notch impact test at -101 C",
        pairing_nut="A194 4 or 7"
    ),

    # -------------------------------------------------------------------------
    # ASTM A193 Stainless Steel
    # -------------------------------------------------------------------------
    "A193_B8": MaterialProperties(
        name="ASTM A193 Grade B8 (304 SS)",
        grade="B8 Class 1",
        specification="ASTM A193",
        category=MaterialCategory.STAINLESS_AUSTENITIC,
        E=193000, G=77000, nu=0.29, rho=8000,
        Sy=205, Su=515, elongation=30,
        hardness_hrc=20, hardness_hb=223,
        alpha=17.2e-6, k_thermal=16.2, T_max=815, T_min=-254,
        zeta=0.002,
        PREN=18.0,
        applications="Corrosive non-chloride service",
        restrictions="HIGH galling risk - ALWAYS lubricate! Chloride SCC above 60°C",
        pairing_nut="A194 8"
    ),

    "A193_B8M": MaterialProperties(
        name="ASTM A193 Grade B8M (316 SS)",
        grade="B8M Class 1",
        specification="ASTM A193",
        category=MaterialCategory.STAINLESS_AUSTENITIC,
        E=193000, G=77000, nu=0.29, rho=8000,
        Sy=205, Su=515, elongation=30,
        hardness_hrc=20, hardness_hb=223,
        alpha=16.0e-6, k_thermal=16.2, T_max=815, T_min=-254,
        zeta=0.002,
        PREN=24.0,
        applications="Marine/offshore, better chloride resistance than B8",
        restrictions="Galling risk - anti-seize essential",
        pairing_nut="A194 8M"
    ),

    # -------------------------------------------------------------------------
    # Duplex and Super Duplex
    # -------------------------------------------------------------------------
    "DUPLEX_2205": MaterialProperties(
        name="Duplex 2205",
        grade="F51 / S31803",
        specification="ASTM A182 F51",
        category=MaterialCategory.STAINLESS_DUPLEX,
        E=200000, G=77000, nu=0.29, rho=7800,
        Sy=450, Su=620, elongation=25,
        hardness_hrc=28, hardness_hb=290,
        alpha=13.0e-6, k_thermal=19, T_max=315, T_min=-40,
        zeta=0.002,
        PREN=35.0,
        sour_service=True,  # With limits per NACE
        applications="Offshore, seawater systems, chloride environments -  standard",
        restrictions="475°C embrittlement risk",
        pairing_nut="Duplex 2205"
    ),

    "SUPER_DUPLEX_2507": MaterialProperties(
        name="Super Duplex 2507",
        grade="F53 / S32750",
        specification="ASTM A182 F53",
        category=MaterialCategory.STAINLESS_SUPER_DUPLEX,
        E=200000, G=77000, nu=0.29, rho=7800,
        Sy=550, Su=795, elongation=15,
        hardness_hrc=32, hardness_hb=310,
        alpha=13.0e-6, k_thermal=17, T_max=315, T_min=-40,
        zeta=0.002,
        PREN=42.0,
        sour_service=True,
        applications="Severe subsea service, hot seawater -  premium",
        restrictions="475°C embrittlement risk",
        pairing_nut="Super Duplex 2507"
    ),

    # -------------------------------------------------------------------------
    # Nickel Alloys
    # -------------------------------------------------------------------------
    "ALLOY_625": MaterialProperties(
        name="Alloy 625 (Inconel 625)",
        grade="N06625",
        specification="ASTM B446",
        category=MaterialCategory.NICKEL_ALLOY,
        E=208000, G=79000, nu=0.31, rho=8440,
        Sy=415, Su=830, elongation=30,
        hardness_hrc=25, hardness_hb=250,
        alpha=12.8e-6, k_thermal=9.8, T_max=650, T_min=-200,
        zeta=0.002,
        PREN=51.0,
        sour_service=True,
        applications="Severe sour + seawater, HPHT wells, subsea",
        restrictions="Expensive, lead time",
        pairing_nut="Alloy 625"
    ),

    "ALLOY_718": MaterialProperties(
        name="Alloy 718 (Inconel 718)",
        grade="N07718",
        specification="API 20E / ASTM B637",
        category=MaterialCategory.NICKEL_ALLOY,
        E=205000, G=77000, nu=0.29, rho=8220,
        Sy=1035, Su=1240, elongation=12,
        hardness_hrc=40, hardness_hb=380,
        alpha=13.0e-6, k_thermal=11.4, T_max=650, T_min=-200,
        zeta=0.002,
        PREN=35.0,
        sour_service=True,  # With hardness limits
        applications="HPHT applications, critical subsea,  pre-salt",
        restrictions="Very expensive, hardness limits for sour",
        pairing_nut="Alloy 718"
    ),
}


# =============================================================================
# FRICTION COEFFICIENTS DATABASE
# =============================================================================

@dataclass
class FrictionCoefficients:
    """Friction coefficient pair for thread and bearing surfaces."""
    mu_thread_dry: Tuple[float, float]      # (min, max) range
    mu_thread_lubricated: Tuple[float, float]
    mu_bearing_dry: Tuple[float, float]
    mu_bearing_lubricated: Tuple[float, float]
    notes: str = ""


FRICTION_DATABASE: Dict[str, FrictionCoefficients] = {
    "steel_on_steel": FrictionCoefficients(
        mu_thread_dry=(0.12, 0.18),
        mu_thread_lubricated=(0.06, 0.10),
        mu_bearing_dry=(0.12, 0.20),
        mu_bearing_lubricated=(0.06, 0.12),
        notes="Standard carbon/low-alloy steel"
    ),
    "ss_on_ss": FrictionCoefficients(
        mu_thread_dry=(0.25, 0.50),
        mu_thread_lubricated=(0.08, 0.12),
        mu_bearing_dry=(0.20, 0.45),
        mu_bearing_lubricated=(0.08, 0.14),
        notes="Stainless on stainless - HIGH GALLING RISK"
    ),
    "cra_on_cra": FrictionCoefficients(
        mu_thread_dry=(0.20, 0.40),
        mu_thread_lubricated=(0.10, 0.15),
        mu_bearing_dry=(0.18, 0.35),
        mu_bearing_lubricated=(0.10, 0.15),
        notes="CRA materials (Duplex, Nickel alloys)"
    ),
    "zinc_plated": FrictionCoefficients(
        mu_thread_dry=(0.08, 0.14),
        mu_thread_lubricated=(0.06, 0.10),
        mu_bearing_dry=(0.10, 0.16),
        mu_bearing_lubricated=(0.06, 0.10),
        notes="Zinc electroplated or hot-dip"
    ),
    "zinc_flake": FrictionCoefficients(
        mu_thread_dry=(0.06, 0.10),
        mu_thread_lubricated=(0.05, 0.08),
        mu_bearing_dry=(0.08, 0.12),
        mu_bearing_lubricated=(0.05, 0.08),
        notes="Zinc flake coating (Geomet, Dacromet)"
    ),
    "phosphate_oil": FrictionCoefficients(
        mu_thread_dry=(0.10, 0.16),
        mu_thread_lubricated=(0.08, 0.12),
        mu_bearing_dry=(0.12, 0.18),
        mu_bearing_lubricated=(0.08, 0.12),
        notes="Phosphate conversion + oil"
    ),
    "ptfe_coated": FrictionCoefficients(
        mu_thread_dry=(0.04, 0.08),
        mu_thread_lubricated=(0.03, 0.06),
        mu_bearing_dry=(0.05, 0.10),
        mu_bearing_lubricated=(0.04, 0.08),
        notes="PTFE-based coating"
    ),
    "moly_paste": FrictionCoefficients(
        mu_thread_dry=(0.06, 0.10),
        mu_thread_lubricated=(0.04, 0.08),
        mu_bearing_dry=(0.08, 0.12),
        mu_bearing_lubricated=(0.05, 0.09),
        notes="MoS2 paste lubricant"
    ),
}


def get_friction_coefficients(
    material1: str,
    material2: str,
    coating: CoatingType = CoatingType.NONE,
    lubricant: LubricantType = LubricantType.NONE
) -> Tuple[float, float]:
    """
    Get friction coefficients for a material/coating/lubricant combination.

    Returns (mu_thread, mu_bearing) as mean values.
    """
    # Determine base friction category
    is_ss1 = "SS" in material1 or "STAINLESS" in material1.upper() or "B8" in material1
    is_ss2 = "SS" in material2 or "STAINLESS" in material2.upper() or "B8" in material2
    is_cra1 = "DUPLEX" in material1.upper() or "ALLOY" in material1.upper() or "625" in material1 or "718" in material1
    is_cra2 = "DUPLEX" in material2.upper() or "ALLOY" in material2.upper() or "625" in material2 or "718" in material2

    # Select base friction data
    if is_cra1 or is_cra2:
        base = FRICTION_DATABASE["cra_on_cra"]
    elif is_ss1 and is_ss2:
        base = FRICTION_DATABASE["ss_on_ss"]
    elif is_ss1 or is_ss2:
        base = FRICTION_DATABASE["ss_on_ss"]  # Conservative
    else:
        base = FRICTION_DATABASE["steel_on_steel"]

    # Apply coating effects
    if coating == CoatingType.ZINC_FLAKE or coating == CoatingType.ZINC_FLAKE_TOPCOAT:
        base = FRICTION_DATABASE["zinc_flake"]
    elif coating in (CoatingType.ZINC_ELECTROPLATED, CoatingType.ZINC_HOT_DIP):
        base = FRICTION_DATABASE["zinc_plated"]
    elif coating == CoatingType.PHOSPHATE_OIL:
        base = FRICTION_DATABASE["phosphate_oil"]
    elif coating == CoatingType.PTFE:
        base = FRICTION_DATABASE["ptfe_coated"]

    # Determine if lubricated
    is_lubricated = lubricant != LubricantType.NONE

    if is_lubricated:
        mu_thread = (base.mu_thread_lubricated[0] + base.mu_thread_lubricated[1]) / 2
        mu_bearing = (base.mu_bearing_lubricated[0] + base.mu_bearing_lubricated[1]) / 2
    else:
        mu_thread = (base.mu_thread_dry[0] + base.mu_thread_dry[1]) / 2
        mu_bearing = (base.mu_bearing_dry[0] + base.mu_bearing_dry[1]) / 2

    # Apply lubricant-specific adjustments
    if lubricant == LubricantType.MOLY_PASTE:
        mu_thread *= 0.8
        mu_bearing *= 0.85
    elif lubricant == LubricantType.PTFE_PASTE:
        mu_thread *= 0.7
        mu_bearing *= 0.75
    elif lubricant in (LubricantType.NICKEL_ANTISEIZE, LubricantType.NEVER_SEEZ, LubricantType.JET_LUBE):
        mu_thread *= 0.85
        mu_bearing *= 0.9

    return (mu_thread, mu_bearing)


# =============================================================================
# THREAD LOAD DISTRIBUTION
# =============================================================================

def calculate_thread_load_factors(
    n_threads: int,
    law: LoadDistributionLaw,
    beta: float = 2.0,
    lam: float = 0.4,
    gamma: float = 0.5,
    custom_factors: Optional[List[float]] = None
) -> List[float]:
    """
    Calculate load distribution factors for engaged threads.

    Thread 1 is at the bearing face (highest load typically).

    Args:
        n_threads: Number of engaged threads
        law: Distribution law to use
        beta: Exponent for power law
        lam: Decay rate for exponential (lambda)
        gamma: Parameter for Yamamoto model
        custom_factors: Custom factors (must sum to 1.0)

    Returns:
        List of load factors that sum to 1.0
    """
    n = n_threads

    if law == LoadDistributionLaw.EQUAL:
        return [1.0 / n] * n

    elif law == LoadDistributionLaw.LINEAR:
        # phi_i = 2(n-i+1) / n(n+1)
        factors = [2 * (n - i) / (n * (n + 1)) for i in range(n)]
        return factors

    elif law == LoadDistributionLaw.POWER:
        # phi_i = (n-i+1)^beta / sum(j^beta)
        raw = [(n - i) ** beta for i in range(n)]
        total = sum(raw)
        return [f / total for f in raw]

    elif law == LoadDistributionLaw.EXPONENTIAL:
        # phi_i = exp(-lambda*(i-1)) / sum(exp(-lambda*(j-1)))
        raw = [math.exp(-lam * i) for i in range(n)]
        total = sum(raw)
        return [f / total for f in raw]

    elif law == LoadDistributionLaw.YAMAMOTO:
        # phi_i = sinh(gamma*(n-i+0.5)) / sum(sinh(gamma*(n-j+0.5)))
        raw = [math.sinh(gamma * (n - i + 0.5)) for i in range(n)]
        total = sum(raw)
        return [f / total for f in raw]

    elif law == LoadDistributionLaw.CUSTOM:
        if custom_factors and len(custom_factors) == n:
            total = sum(custom_factors)
            return [f / total for f in custom_factors]
        else:
            return [1.0 / n] * n  # Fallback to equal

    return [1.0 / n] * n


def calculate_thread_stiffnesses(
    k_total: float,
    load_factors: List[float],
    connection: str = "parallel"
) -> List[float]:
    """
    Calculate individual thread stiffnesses from total and load factors.

    For parallel connection: k_i = factor_i * k_total
    This means higher load threads have higher stiffness contribution.

    Args:
        k_total: Total thread engagement stiffness [N/m]
        load_factors: Load distribution factors (sum to 1.0)
        connection: "parallel" or "series"

    Returns:
        List of individual thread stiffnesses [N/m]
    """
    if connection == "parallel":
        # k_total = sum(k_i), and k_i proportional to load factor
        return [f * k_total for f in load_factors]
    else:
        # Series: 1/k_total = sum(1/k_i)
        # More complex - approximate with equal compliance per unit load
        n = len(load_factors)
        return [k_total * n * f for f in load_factors]


# =============================================================================
# CONTACT STIFFNESS CALCULATIONS
# =============================================================================

@dataclass
class ContactStiffnessParams:
    """Parameters for contact stiffness calculation."""
    # Typical stiffness ranges [kN/μm] for M20 bolt reference
    k_min: float
    k_max: float
    description: str


CONTACT_STIFFNESS_REFERENCE: Dict[str, ContactStiffnessParams] = {
    "bolt_head_washer": ContactStiffnessParams(500, 2000, "Bolt head to washer contact (very stiff)"),
    "washer_flange": ContactStiffnessParams(300, 1500, "Washer to flange contact"),
    "flange_flange": ContactStiffnessParams(400, 2000, "Flange to flange metal contact"),
    "flange_gasket_sw": ContactStiffnessParams(100, 500, "Flange to spiral wound gasket"),
    "flange_gasket_rtj": ContactStiffnessParams(1000, 5000, "Flange to RTJ gasket"),
    "thread_single": ContactStiffnessParams(50, 200, "Single thread fillet contact"),
    "nut_washer": ContactStiffnessParams(400, 1800, "Nut to washer contact"),
}


def estimate_contact_stiffness(
    contact_type: str,
    diameter_mm: float,
    E_eff_MPa: float = 110000,  # Effective modulus for steel-steel
    area_factor: float = 1.0
) -> float:
    """
    Estimate contact stiffness based on type and geometry.

    Args:
        contact_type: Key from CONTACT_STIFFNESS_REFERENCE
        diameter_mm: Nominal bolt diameter [mm]
        E_eff_MPa: Effective elastic modulus [MPa]
        area_factor: Correction factor for actual vs nominal area

    Returns:
        Estimated stiffness [N/m]
    """
    if contact_type not in CONTACT_STIFFNESS_REFERENCE:
        return 1e9  # Default 1 GN/m

    ref = CONTACT_STIFFNESS_REFERENCE[contact_type]

    # Scale reference (for M20) to actual diameter
    # Stiffness scales approximately with diameter squared (area)
    scale = (diameter_mm / 20.0) ** 2

    # Use geometric mean of range
    k_ref = math.sqrt(ref.k_min * ref.k_max)  # kN/μm for M20

    # Convert to N/m: kN/μm * 1e3 N/kN * 1e6 μm/m = 1e9 N/m
    k_Nm = k_ref * 1e9 * scale * area_factor

    return k_Nm


# =============================================================================
# EMBEDDING FACTORS (VDI 2230)
# =============================================================================

EMBEDDING_FACTORS: Dict[str, Tuple[float, float]] = {
    # Surface condition: (f_z_min, f_z_max) in μm/mm
    "turned_ground": (1.0, 2.0),      # Ra < 10 μm
    "milled": (2.0, 4.0),              # Ra 10-40 μm
    "untreated_rough": (4.0, 8.0),     # Rough as-cast/forged
    "under_head_nut": (2.0, 4.0),      # Bearing surfaces
    "thread_engagement": (3.0, 5.0),   # Thread contact
    "galvanized": (4.0, 8.0),          # Hot-dip galvanized
    "zinc_flake": (2.0, 4.0),          # Zinc flake coating
}


def calculate_total_embedding(surfaces: List[str]) -> float:
    """
    Calculate total embedding from surface conditions.

    Args:
        surfaces: List of surface condition keys

    Returns:
        Total embedding in μm
    """
    total = 0.0
    for surface in surfaces:
        if surface in EMBEDDING_FACTORS:
            f_min, f_max = EMBEDDING_FACTORS[surface]
            total += (f_min + f_max) / 2  # Use mean
    return total


def estimate_preload_loss_embedding(embedding_um: float, grip_length_mm: float) -> float:
    """
    Estimate preload loss percentage due to embedding.

    Args:
        embedding_um: Total embedding [μm]
        grip_length_mm: Total grip length [mm]

    Returns:
        Estimated preload loss as fraction (e.g., 0.05 for 5%)
    """
    # Simplified estimate: loss proportional to embedding / grip
    # Typical 3-10% for new joints
    if grip_length_mm <= 0:
        return 0.05

    loss = embedding_um / (grip_length_mm * 1000)  # Convert grip to μm
    return min(max(loss * 100, 0.03), 0.15)  # Clamp 3-15%


# =============================================================================
# GASKET PROPERTIES
# =============================================================================

@dataclass
class GasketProperties:
    """Gasket material properties."""
    gasket_type: GasketType
    m_factor: float              # ASME gasket factor
    y_seating_MPa: float         # Minimum seating stress [MPa]
    max_stress_MPa: float        # Maximum allowable stress [MPa]
    typical_k_kN_mm: Tuple[float, float]  # Stiffness range [kN/mm]
    recovery_percent: float      # Typical recovery percentage
    max_temp_C: float            # Maximum temperature [°C]
    notes: str = ""


GASKET_DATABASE: Dict[str, GasketProperties] = {
    "spiral_wound_316_graphite": GasketProperties(
        gasket_type=GasketType.SPIRAL_WOUND,
        m_factor=3.0,
        y_seating_MPa=68.9,
        max_stress_MPa=180,
        typical_k_kN_mm=(100, 500),
        recovery_percent=15,
        max_temp_C=650,
        notes="Most common for O&G service"
    ),
    "spiral_wound_316_ptfe": GasketProperties(
        gasket_type=GasketType.SPIRAL_WOUND,
        m_factor=2.5,
        y_seating_MPa=51.7,
        max_stress_MPa=140,
        typical_k_kN_mm=(80, 400),
        recovery_percent=20,
        max_temp_C=260,
        notes="Lower temperature, chemical service"
    ),
    "rtj_r_oval": GasketProperties(
        gasket_type=GasketType.RING_JOINT,
        m_factor=6.5,
        y_seating_MPa=179,
        max_stress_MPa=400,
        typical_k_kN_mm=(1000, 5000),
        recovery_percent=0,
        max_temp_C=540,
        notes="High-pressure service, metal-to-metal seal"
    ),
    "kammprofile_graphite": GasketProperties(
        gasket_type=GasketType.KAMMPROFILE,
        m_factor=3.5,
        y_seating_MPa=75,
        max_stress_MPa=200,
        typical_k_kN_mm=(200, 800),
        recovery_percent=10,
        max_temp_C=450,
        notes="Good bolt load retention"
    ),
}


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def get_material(name: str) -> Optional[MaterialProperties]:
    """Get material properties by name or grade."""
    # Direct lookup
    if name in MATERIALS_DATABASE:
        return MATERIALS_DATABASE[name]

    # Search by grade
    for key, mat in MATERIALS_DATABASE.items():
        if mat.grade.lower() == name.lower():
            return mat
        if name.lower() in mat.name.lower():
            return mat

    return None


def get_all_materials() -> List[str]:
    """Get list of all material names."""
    return list(MATERIALS_DATABASE.keys())


def get_materials_by_category(category: MaterialCategory) -> Dict[str, MaterialProperties]:
    """Get all materials in a category."""
    return {k: v for k, v in MATERIALS_DATABASE.items() if v.category == category}


def get_sour_service_materials() -> Dict[str, MaterialProperties]:
    """Get all NACE MR0175 compliant materials."""
    return {k: v for k, v in MATERIALS_DATABASE.items() if v.sour_service}


def check_galvanic_compatibility(mat1: str, mat2: str) -> Tuple[bool, str]:
    """
    Check galvanic compatibility of two materials.

    Returns (compatible, warning_message)
    """
    m1 = get_material(mat1)
    m2 = get_material(mat2)

    if not m1 or not m2:
        return True, "Unknown materials - verify compatibility"

    # Check category combinations
    cat1, cat2 = m1.category, m2.category

    # Carbon steel with stainless - potential galvanic cell
    if (cat1 == MaterialCategory.CARBON_STEEL and
        cat2 in (MaterialCategory.STAINLESS_AUSTENITIC,
                 MaterialCategory.STAINLESS_DUPLEX,
                 MaterialCategory.STAINLESS_SUPER_DUPLEX)):
        return False, "Carbon steel + stainless: galvanic corrosion risk in electrolyte"

    if (cat2 == MaterialCategory.CARBON_STEEL and
        cat1 in (MaterialCategory.STAINLESS_AUSTENITIC,
                 MaterialCategory.STAINLESS_DUPLEX,
                 MaterialCategory.STAINLESS_SUPER_DUPLEX)):
        return False, "Carbon steel + stainless: galvanic corrosion risk in electrolyte"

    # Nickel alloy with carbon steel
    if ((cat1 == MaterialCategory.NICKEL_ALLOY and cat2 == MaterialCategory.CARBON_STEEL) or
        (cat2 == MaterialCategory.NICKEL_ALLOY and cat1 == MaterialCategory.CARBON_STEEL)):
        return False, "Nickel alloy + carbon steel: significant galvanic potential difference"

    return True, "Compatible"


def get_all_grade_names() -> List[str]:
    """Get list of human-readable grade names for UI combo boxes."""
    grade_display = {
        "ISO_8.8": "Steel 8.8 (ISO)",
        "ISO_10.9": "Steel 10.9 (ISO)",
        "ISO_12.9": "Steel 12.9 (ISO)",
        "A193_B7": "A193 B7 (Cr-Mo, HT)",
        "A193_B7M": "A193 B7M (Cr-Mo, impact)",
        "A193_B16": "A193 B16 (Cr-Mo-V)",
        "A193_B8": "A193 B8 (304 SS)",
        "A193_B8M": "A193 B8M (316 SS)",
        "A320_L7": "A320 L7 (Cr-Mo, LT)",
        "DUPLEX_2205": "Duplex 2205",
        "SUPER_DUPLEX_2507": "Super Duplex 2507",
        "ALLOY_625": "Alloy 625 (Ni)",
        "ALLOY_718": "Alloy 718 (Ni)",
    }
    return [grade_display.get(k, k) for k in MATERIALS_DATABASE.keys()]


def get_grade_key_from_display(display_name: str) -> Optional[str]:
    """Convert display name back to MATERIALS_DATABASE key."""
    display_to_key = {
        "Steel 8.8 (ISO)": "ISO_8.8",
        "Steel 10.9 (ISO)": "ISO_10.9",
        "Steel 12.9 (ISO)": "ISO_12.9",
        "A193 B7 (Cr-Mo, HT)": "A193_B7",
        "A193 B7M (Cr-Mo, impact)": "A193_B7M",
        "A193 B16 (Cr-Mo-V)": "A193_B16",
        "A193 B8 (304 SS)": "A193_B8",
        "A193 B8M (316 SS)": "A193_B8M",
        "A320 L7 (Cr-Mo, LT)": "A320_L7",
        "Duplex 2205": "DUPLEX_2205",
        "Super Duplex 2507": "SUPER_DUPLEX_2507",
        "Alloy 625 (Ni)": "ALLOY_625",
        "Alloy 718 (Ni)": "ALLOY_718",
    }
    return display_to_key.get(display_name)


def get_properties_for_grade(display_name: str) -> Optional[Dict[str, float]]:
    """Get material properties dict {E, Sy, Su, rho} for a display grade name.

    Values returned in MPa (E, Sy, Su) and kg/m³ (rho), matching the database units.
    """
    key = get_grade_key_from_display(display_name)
    if key and key in MATERIALS_DATABASE:
        mat = MATERIALS_DATABASE[key]
        return {
            "E": mat.E,        # MPa
            "Sy": mat.Sy,      # MPa
            "Su": mat.Su,      # MPa
            "rho": mat.rho,    # kg/m³
        }
    return None


def get_thread_geometry(diameter_mm: float, pitch_mm: Optional[float] = None) -> Optional[dict]:
    """Return full ISO thread geometry for a nominal diameter (and optionally pitch).

    Searches threads.json for an exact diameter match.  When ``pitch_mm`` is
    given the entry whose pitch is closest to that value is preferred; otherwise
    the ISO metric coarse entry is returned.

    Returns a dict with keys: ``P``, ``d2``, ``d3``, ``D1``, ``At``, ``As``,
    ``designation``.  Falls back to ISO-formula values when the DB has no
    matching entry.
    """
    import json
    import os

    threads_path = os.path.join(os.path.dirname(__file__), "threads.json")
    try:
        with open(threads_path, "r", encoding="utf-8") as f:
            db = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return _thread_geometry_fallback(diameter_mm, pitch_mm)

    best = None
    best_pitch_delta = float("inf")

    for series_key in ("iso_metric_coarse", "iso_metric_fine"):
        for entry in db.get(series_key, {}).get("dimensions", []):
            if abs(entry.get("d", 0) - diameter_mm) > 0.01:
                continue
            p = entry.get("P", 0)
            delta = abs(p - pitch_mm) if pitch_mm is not None else 0.0
            if pitch_mm is None:
                # Coarse series comes first — take the very first match
                if best is None:
                    best, best_pitch_delta = entry, delta
            else:
                if delta < best_pitch_delta:
                    best, best_pitch_delta = entry, delta

    if best is not None:
        p = best["P"]
        return {
            "P":           p,
            "d2":          best.get("d2",  diameter_mm - 0.6495 * p),
            "d3":          best.get("d3",  diameter_mm - 1.0825 * p),
            "D1":          best.get("D1",  diameter_mm - 1.0825 * p),
            "At":          best.get("At",  0.0),
            "As":          best.get("As",  0.0),
            "designation": best.get("designation", f"M{diameter_mm:.0f}"),
        }

    return _thread_geometry_fallback(diameter_mm, pitch_mm)


def _thread_geometry_fallback(diameter_mm: float, pitch_mm: Optional[float] = None) -> dict:
    """Compute thread geometry from ISO 724 formulas when DB lookup fails."""
    P = pitch_mm if (pitch_mm and pitch_mm > 0) else (
        get_standard_pitch_for_diameter(diameter_mm) or diameter_mm * 0.1)
    d2 = diameter_mm - 0.6495 * P
    d3 = diameter_mm - 1.0825 * P
    At = math.pi / 4 * ((d2 + d3) / 2) ** 2
    return {
        "P":           round(P, 3),
        "d2":          round(d2, 3),
        "d3":          round(d3, 3),
        "D1":          round(d3, 3),
        "At":          round(At, 2),
        "As":          round(At * 0.9, 2),
        "designation": f"M{diameter_mm:.0f}",
    }


def get_stress_area_from_threads(diameter_mm: float,
                                 pitch_mm: Optional[float] = None) -> Optional[float]:
    """
    Look up tensile stress area At (mm²) from threads.json for given nominal diameter.

    When ``pitch_mm`` is provided the matching fine/coarse entry is selected by
    pitch; otherwise the coarse entry is returned.  Falls back to the ISO 724
    formula if no DB entry exists.

    Returns At in mm², or None if no data.
    """
    geom = get_thread_geometry(diameter_mm, pitch_mm)
    if geom is not None:
        at = geom.get("At") or geom.get("As")
        if at:
            return float(at)
    return _stress_area_fallback(diameter_mm)


def _stress_area_fallback(diameter_mm: float) -> float:
    """Compute tensile stress area from VDI 2230 approximation for ISO metric."""
    # Approximate pitch for standard coarse thread
    if diameter_mm <= 6:
        P = diameter_mm * 0.167
    elif diameter_mm <= 16:
        P = diameter_mm * 0.125
    else:
        P = diameter_mm * 0.1
    d2 = diameter_mm - 0.6495 * P
    d3 = diameter_mm - 1.0825 * P
    return math.pi / 4 * ((d2 + d3) / 2) ** 2


# ISO metric coarse thread pitch table (ISO 261 / ISO 724)
_ISO_COARSE_PITCH: dict = {
    1: 0.25, 1.2: 0.25, 1.6: 0.35, 2: 0.4, 2.5: 0.45, 3: 0.5, 3.5: 0.6,
    4: 0.7, 5: 0.8, 6: 1.0, 7: 1.0, 8: 1.25, 10: 1.5, 12: 1.75, 14: 2.0,
    16: 2.0, 18: 2.5, 20: 2.5, 22: 2.5, 24: 3.0, 27: 3.0, 30: 3.5, 33: 3.5,
    36: 4.0, 39: 4.0, 42: 4.5, 45: 4.5, 48: 5.0, 52: 5.0, 56: 5.5, 60: 5.5,
    64: 6.0, 68: 6.0, 72: 6.0, 76: 6.0, 80: 6.0,
}


def get_standard_pitch_for_diameter(diameter_mm: float) -> Optional[float]:
    """Return ISO metric coarse thread pitch (mm) for a nominal bolt diameter.

    Performs an exact look-up in the ISO 261 coarse pitch table, then falls
    back to the nearest entry within ±0.5 mm tolerance.

    Args:
        diameter_mm: Nominal bolt diameter in mm (e.g. 16.0 for M16).

    Returns:
        Standard coarse pitch in mm, or None if no match found.
    """
    # Exact match first
    pitch = _ISO_COARSE_PITCH.get(round(diameter_mm, 1))
    if pitch is not None:
        return pitch
    # Nearest-neighbour fallback within 0.5 mm
    best_key, best_dist = None, float("inf")
    for key in _ISO_COARSE_PITCH:
        dist = abs(key - diameter_mm)
        if dist < best_dist:
            best_dist, best_key = dist, key
    if best_dist <= 0.5 and best_key is not None:
        return _ISO_COARSE_PITCH[best_key]
    return None
