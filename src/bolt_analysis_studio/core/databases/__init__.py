"""
Databases module for Bolt Analysis Studio.

Contains:
- JSON databases: materials.json, threads.json
- Python database: materials_database.py (comprehensive with tribology)
"""

import json
from pathlib import Path

_DB_PATH = Path(__file__).parent

def load_materials():
    """Load materials database from JSON."""
    with open(_DB_PATH / "materials.json", "r") as f:
        return json.load(f)

def load_threads():
    """Load threads database from JSON."""
    with open(_DB_PATH / "threads.json", "r") as f:
        return json.load(f)

# Import comprehensive materials database
from .materials_database import (
    # Enums
    MaterialCategory,
    CoatingType,
    LubricantType,
    LoadDistributionLaw,
    EnvironmentType,
    GasketType,

    # Data classes
    MaterialProperties,
    FrictionCoefficients,
    ContactStiffnessParams,
    GasketProperties,

    # Databases
    MATERIALS_DATABASE,
    FRICTION_DATABASE,
    CONTACT_STIFFNESS_REFERENCE,
    EMBEDDING_FACTORS,
    GASKET_DATABASE,

    # Functions
    get_material,
    get_all_materials,
    get_materials_by_category,
    get_sour_service_materials,
    get_friction_coefficients,
    calculate_thread_load_factors,
    calculate_thread_stiffnesses,
    estimate_contact_stiffness,
    calculate_total_embedding,
    estimate_preload_loss_embedding,
    check_galvanic_compatibility,
)

__all__ = [
    'load_materials',
    'load_threads',
    # New database exports
    'MaterialCategory',
    'CoatingType',
    'LubricantType',
    'LoadDistributionLaw',
    'EnvironmentType',
    'GasketType',
    'MaterialProperties',
    'FrictionCoefficients',
    'ContactStiffnessParams',
    'GasketProperties',
    'MATERIALS_DATABASE',
    'FRICTION_DATABASE',
    'CONTACT_STIFFNESS_REFERENCE',
    'EMBEDDING_FACTORS',
    'GASKET_DATABASE',
    'get_material',
    'get_all_materials',
    'get_materials_by_category',
    'get_sour_service_materials',
    'get_friction_coefficients',
    'calculate_thread_load_factors',
    'calculate_thread_stiffnesses',
    'estimate_contact_stiffness',
    'calculate_total_embedding',
    'estimate_preload_loss_embedding',
    'check_galvanic_compatibility',
]
