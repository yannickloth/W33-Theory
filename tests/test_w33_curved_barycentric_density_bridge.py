from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path

from w33_curved_barycentric_density_bridge import (
    barycentric_subdivision_matrix,
    build_curved_barycentric_density_bridge_summary,
    exact_chain_density_formula,
    exact_neighborly_f_vector_from_modes,
    exact_trace_density_formula,
    product_chain_density_limit,
    product_trace_density_limit,
    relevant_eigenmodes,
    seed_density_samples,
    universal_chain_density_limit,
    universal_trace_density_limit,
    write_summary,
)
from w33_minimal_triangulation_bridge import barycentric_subdivision_f_vector, cp2_seed, k3_seed


def test_barycentric_subdivision_matrix_has_expected_diagonal_spectrum() -> None:
    matrix = barycentric_subdivision_matrix()
    assert tuple(matrix[index][index] for index in range(5)) == (1, 2, 6, 24, 120)


def test_relevant_eigenmodes_have_expected_exact_profiles() -> None:
    modes = relevant_eigenmodes()
    assert modes[1] == (Fraction(1), Fraction(0), Fraction(0), Fraction(0), Fraction(0))
    assert modes[6] == (Fraction(1, 2), Fraction(3, 2), Fraction(1), Fraction(0), Fraction(0))
    assert modes[120] == (Fraction(1, 19), Fraction(25, 38), Fraction(40, 19), Fraction(5, 2), Fraction(1))


def test_cp2_and_k3_neighborly_f_vectors_reconstruct_exactly_from_modes() -> None:
    cp2 = cp2_seed()
    k3 = k3_seed()
    for step in range(5):
        assert exact_neighborly_f_vector_from_modes(cp2.vertices, step) == barycentric_subdivision_f_vector(cp2.f_vector, steps=step)
        assert exact_neighborly_f_vector_from_modes(k3.vertices, step) == barycentric_subdivision_f_vector(k3.f_vector, steps=step)


def test_universal_external_density_limits_are_exact_rationals() -> None:
    assert universal_chain_density_limit() == Fraction(120, 19)
    assert universal_trace_density_limit() == Fraction(860, 19)


def test_seed_density_formulas_match_direct_refinement_samples() -> None:
    cp2 = cp2_seed()
    k3 = k3_seed()
    for seed in (cp2, k3):
        for sample in seed_density_samples(seed.vertices, seed.f_vector):
            assert sample.chain_density_per_top_simplex == exact_chain_density_formula(seed.vertices, sample.step)
            assert sample.trace_density_per_top_simplex == exact_trace_density_formula(seed.vertices, sample.step)


def test_product_density_limits_match_exact_internal_moments() -> None:
    assert product_chain_density_limit() == Fraction(19440, 19)
    assert product_trace_density_limit() == Fraction(7512120, 19)


def test_summary_records_mode_split_and_universal_limits() -> None:
    summary = build_curved_barycentric_density_bridge_summary()
    assert summary["status"] == "ok"
    assert summary["neighborly_mode_formulas"]["vanishing_modes"] == [2, 24]
    assert summary["universal_local_limits"]["external_chain_density_per_top_simplex"]["exact"] == "120/19"
    assert summary["universal_local_limits"]["external_trace_dk_squared_per_top_simplex"]["exact"] == "860/19"
    assert "exact mode decomposition" in summary["bridge_verdict"]


def test_write_summary_emits_json(tmp_path: Path) -> None:
    out = write_summary(tmp_path / "w33_curved_barycentric_density_bridge_summary.json")
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["status"] == "ok"
    assert data["seed_decompositions"][0]["density_samples"][0]["top_simplices"] == 36
    assert data["seed_decompositions"][1]["density_samples"][0]["top_simplices"] == 288
