from __future__ import annotations

from fractions import Fraction

import numpy as np

from exploration.w33_three_channel_operator_bridge import (
    adjacency_moment,
    build_three_channel_operator_summary,
    build_w33_adjacency,
    coefficient_matrix,
    interpolate_three_channel,
    laplacian_pseudoinverse_coefficients,
    random_walk_power_coefficients,
    resolvent_coefficients,
    spectral_projector_coefficients,
)


def test_power_reduction_matches_exact_three_channel_coefficients() -> None:
    adjacency = build_w33_adjacency()
    coeffs = interpolate_three_channel(12**4, 2**4, (-4) ** 4)
    reduced = coefficient_matrix(coeffs, adjacency)
    direct = np.linalg.matrix_power(adjacency.astype(float), 4)

    assert np.array_equal(reduced.astype(int), direct.astype(int))


def test_nonnegative_spectral_projector_has_exact_three_entry_profile() -> None:
    adjacency = build_w33_adjacency().astype(float)
    coeffs = spectral_projector_coefficients()["E_nonnegative"]
    projector = coefficient_matrix(coeffs, adjacency)

    eigenvalues, eigenvectors = np.linalg.eigh(adjacency)
    mask = eigenvalues > -1e-9
    direct = eigenvectors[:, mask] @ eigenvectors[:, mask].T

    assert np.allclose(projector, direct, atol=1e-10)
    assert np.allclose(np.diag(projector), 5.0 / 8.0, atol=1e-10)
    edge_mask = adjacency.astype(bool)
    nonedge_mask = (~edge_mask) & (~np.eye(adjacency.shape[0], dtype=bool))
    assert np.allclose(projector[edge_mask], 1.0 / 8.0, atol=1e-10)
    assert np.allclose(projector[nonedge_mask], -1.0 / 24.0, atol=1e-10)


def test_laplacian_pseudoinverse_matches_exact_entry_values() -> None:
    adjacency = build_w33_adjacency().astype(float)
    laplacian = 12.0 * np.eye(adjacency.shape[0]) - adjacency
    pseudoinverse = np.linalg.pinv(laplacian)
    exact = coefficient_matrix(laplacian_pseudoinverse_coefficients(), adjacency)

    assert np.allclose(pseudoinverse, exact, atol=1e-10)
    assert np.allclose(np.diag(exact), 267.0 / 3200.0, atol=1e-10)
    edge_mask = adjacency.astype(bool)
    nonedge_mask = (~edge_mask) & (~np.eye(adjacency.shape[0], dtype=bool))
    assert np.allclose(exact[edge_mask], 7.0 / 3200.0, atol=1e-10)
    assert np.allclose(exact[nonedge_mask], -13.0 / 3200.0, atol=1e-10)


def test_random_walk_power_and_mixing_rate_are_exact() -> None:
    adjacency = build_w33_adjacency().astype(float)
    transition = adjacency / 12.0
    coeffs = random_walk_power_coefficients(6)
    exact = coefficient_matrix(coeffs, adjacency)
    direct = np.linalg.matrix_power(transition, 6)
    projector = np.ones_like(adjacency) / adjacency.shape[0]

    assert np.allclose(exact, direct, atol=1e-12)
    assert np.allclose(np.linalg.norm(direct - projector, 2), (1.0 / 3.0) ** 6, atol=1e-12)


def test_resolvent_at_five_matches_matrix_inverse() -> None:
    adjacency = build_w33_adjacency().astype(float)
    resolvent = np.linalg.inv(5.0 * np.eye(adjacency.shape[0]) - adjacency)
    exact = coefficient_matrix(resolvent_coefficients(5), adjacency)

    assert np.allclose(resolvent, exact, atol=1e-12)


def test_summary_records_recent_phase_unification() -> None:
    summary = build_three_channel_operator_summary()

    assert summary["graph"]["minimal_polynomial"] == "x^3 - 10x^2 - 32x + 96"
    assert summary["operator_calculus"]["every_kernel_is_three_valued"] is True
    assert summary["spectral_projectors"]["positive_projector_entry_values"] == {
        "diagonal": "5/8",
        "edge": "1/8",
        "nonedge": "-1/24",
    }
    assert summary["resistance_bridge"]["effective_resistance_adjacent"] == "13/80"
    assert summary["resistance_bridge"]["effective_resistance_nonadjacent"] == "7/40"
    assert summary["resistance_bridge"]["kemeny_constant"] == str(Fraction(801, 20))
    assert summary["moment_bridge"]["M6"] == adjacency_moment(6)
