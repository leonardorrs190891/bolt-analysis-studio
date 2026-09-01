"""
Tests for MSDModel matrix assembly including sparse path (8.2).

Verifies:
- Small model assembles correct matrices with expected shape
- Stiffness and damping matrices are symmetric
- Sparse path (n >= 50) returns dense-compatible numpy arrays
- Mass matrix is diagonal
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import pytest
import numpy as np


def _make_minimal_model(n_elements: int = 4):
    """Build a simple series chain model with n_elements."""
    from bolt_analysis_studio.core.models.model import MSDModel
    from bolt_analysis_studio.core.models.element import (
        MSDElementData, ElementType, MSDParameters, ConnectionType,
    )

    model = MSDModel(name="test_model")
    k = 1e6   # N/m
    c = 100.0  # N·s/m
    m = 0.1   # kg

    for i in range(n_elements):
        elem = MSDElementData(
            id=i,
            name=f"elem_{i}",
            type=ElementType.FLANGE,
            msd=MSDParameters(k=k, c=c, m=m),
        )
        model.add_element(elem)
    return model


def test_small_model_assembly_shape():
    """Assembled matrices have correct square shape."""
    model = _make_minimal_model(4)
    M, K, C = model.assemble_matrices()
    n = model.n_dof
    assert M.shape == (n, n)
    assert K.shape == (n, n)
    assert C.shape == (n, n)


def test_mass_matrix_is_diagonal():
    """Mass matrix should be diagonal (lumped mass model)."""
    model = _make_minimal_model(3)
    M, _, _ = model.assemble_matrices()
    n = M.shape[0]
    for i in range(n):
        for j in range(n):
            if i != j:
                assert M[i, j] == 0.0, f"M[{i},{j}] = {M[i, j]} is non-zero"


def test_stiffness_matrix_symmetry():
    """Stiffness matrix must be symmetric."""
    model = _make_minimal_model(5)
    _, K, _ = model.assemble_matrices()
    assert np.allclose(K, K.T, atol=1e-10), "K is not symmetric"


def test_damping_matrix_symmetry():
    """Damping matrix must be symmetric."""
    model = _make_minimal_model(5)
    _, _, C = model.assemble_matrices()
    assert np.allclose(C, C.T, atol=1e-10), "C is not symmetric"


def test_stiffness_matrix_positive_diagonal():
    """All diagonal entries of K should be positive."""
    model = _make_minimal_model(4)
    _, K, _ = model.assemble_matrices()
    for i in range(K.shape[0]):
        assert K[i, i] > 0, f"K[{i},{i}] = {K[i, i]} is not positive"


def test_sparse_assembly_returns_dense():
    """
    For large models (n >= 50), sparse assembly should still return
    standard numpy arrays (not scipy sparse objects).
    """
    pytest.importorskip("scipy.sparse")  # Skip if scipy not installed

    from bolt_analysis_studio.core.models.model import MSDModel
    from bolt_analysis_studio.core.models.element import (
        MSDElementData, ElementType, MSDParameters,
    )

    model = MSDModel(name="large_model")
    for i in range(52):   # n_dof = 52 → triggers sparse path
        elem = MSDElementData(
            id=i,
            name=f"elem_{i}",
            type=ElementType.FLANGE,
            msd=MSDParameters(k=1e6, c=100.0, m=0.1),
        )
        model.add_element(elem)

    M, K, C = model.assemble_matrices()

    # Must be numpy arrays, not scipy sparse
    assert isinstance(M, np.ndarray), f"M is {type(M)}, expected np.ndarray"
    assert isinstance(K, np.ndarray), f"K is {type(K)}, expected np.ndarray"
    assert isinstance(C, np.ndarray), f"C is {type(C)}, expected np.ndarray"

    # Sanity: shape and symmetry still hold
    n = M.shape[0]
    assert n == 52
    assert np.allclose(K, K.T, atol=1e-10)


def test_matrices_not_all_zero():
    """Assembled matrices should not be all zeros."""
    model = _make_minimal_model(3)
    M, K, C = model.assemble_matrices()
    assert np.any(M != 0), "Mass matrix is all zeros"
    assert np.any(K != 0), "Stiffness matrix is all zeros"


def test_dirty_flag_clears_after_assembly():
    """After assemble_matrices(), _is_dirty should be False."""
    model = _make_minimal_model(3)
    model.assemble_matrices()
    assert not model._is_dirty, "_is_dirty should be False after assembly"


def test_cache_returns_same_matrices():
    """Calling assemble_matrices() twice should return cached arrays."""
    model = _make_minimal_model(3)
    M1, K1, C1 = model.assemble_matrices()
    M2, K2, C2 = model.assemble_matrices()
    assert M1 is M2, "M should be the same cached object"
    assert K1 is K2, "K should be the same cached object"
