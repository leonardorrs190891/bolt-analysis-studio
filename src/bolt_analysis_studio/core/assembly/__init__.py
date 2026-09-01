"""
Matrix Assembly System for Bolted Joint MSD Models.

This module provides comprehensive matrix assembly capabilities for
14-DOF mass-spring-damper models of bolted flange joints.

KEY CLASSES:
- DOFMapping: Maps component names to DOF indices
- ComponentData: Component properties (mass, stiffness, damping)
- CompleteMSDMatrixAssembler: Main assembly engine

MAIN FUNCTIONS:
- create_standard_dof_mapping(): Create standard 14-DOF layout
- compute_rayleigh_coefficients(): Calculate α, β for damping
- validate_dof_indices(): Validate contact DOF indices

USAGE:
    from bolt_analysis_studio.core.assembly import (
        CompleteMSDMatrixAssembler,
        create_standard_dof_mapping,
        ComponentData
    )

    # Create assembler
    dof_map = create_standard_dof_mapping()
    assembler = CompleteMSDMatrixAssembler(n_dof=14, dof_mapping=dof_map)

    # Add components and contacts
    assembler.add_component(ComponentData("head", dof=0, mass=0.015))
    assembler.add_contact(thread_contact)

    # Assemble matrices
    M, K, C = assembler.get_matrices()
    F = assembler.assemble_force_vector(x, x_dot, t)
"""

from .matrix_assembler import (
    DOFMapping,
    ComponentData,
    CompleteMSDMatrixAssembler,
    compute_rayleigh_coefficients,
    create_standard_dof_mapping,
    validate_dof_indices,
    create_example_joint_assembly,
)

__all__ = [
    'DOFMapping',
    'ComponentData',
    'CompleteMSDMatrixAssembler',
    'compute_rayleigh_coefficients',
    'create_standard_dof_mapping',
    'validate_dof_indices',
    'create_example_joint_assembly',
]
