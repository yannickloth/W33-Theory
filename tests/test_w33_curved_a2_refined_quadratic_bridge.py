from __future__ import annotations

from fractions import Fraction
import json
from pathlib import Path

from w33_curved_a2_refined_quadratic_bridge import (
    build_curved_a2_refined_quadratic_bridge_summary,
    refined_external_quadratic_profile,
    refined_product_quadratic_profile,
    write_summary,
)


def test_refined_external_profiles_are_exact() -> None:
    cp2 = refined_external_quadratic_profile("CP2")
    k3 = refined_external_quadratic_profile("K3")
    assert cp2.refined_f_vector == (255, 2916, 9144, 10800, 4320)
    assert cp2.external_trace == 196128
    assert cp2.external_second_moment == 2104848
    assert cp2.external_second_moment_density == Fraction(14617, 30)
    assert cp2.f_vector_matches_barycentric_transform is True
    assert k3.refined_f_vector == (1704, 22320, 72480, 86400, 34560)
    assert k3.external_trace == 1560960
    assert k3.external_second_moment == 22872000
    assert k3.external_second_moment_density == Fraction(23825, 36)
    assert k3.f_vector_matches_barycentric_transform is True


def test_refined_boundary_degree_distributions_and_product_coefficients_are_exact() -> None:
    cp2 = refined_external_quadratic_profile("CP2")
    k3 = refined_external_quadratic_profile("K3")
    assert cp2.boundary_square_layers[0].degree_distribution == {12: 21, 14: 27, 16: 117, 18: 9, 30: 36, 34: 36, 96: 9}
    assert cp2.boundary_square_layers[3].degree_distribution == {2: 10800}
    assert k3.boundary_square_layers[0].degree_distribution == {12: 80, 14: 240, 16: 720, 20: 240, 30: 288, 76: 120, 390: 16}
    assert k3.boundary_square_layers[3].degree_distribution == {2: 86400}

    cp2_product = refined_product_quadratic_profile("CP2")
    k3_product = refined_product_quadratic_profile("K3")
    assert cp2_product.product_second_moment == 3926556000
    assert cp2_product.quadratic_density_coefficient == Fraction(908925, 2)
    assert k3_product.product_second_moment == 31717388160
    assert k3_product.quadratic_density_coefficient == Fraction(1835497, 4)
    assert abs(cp2_product.quadratic_density_coefficient - k3_product.quadratic_density_coefficient) < abs(
        cp2_product.seed_quadratic_density_coefficient - k3_product.seed_quadratic_density_coefficient
    )


def test_write_summary_emits_json(tmp_path: Path) -> None:
    out = write_summary(tmp_path / "w33_curved_a2_refined_quadratic_bridge_summary.json")
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["status"] == "ok"
    assert data["refined_quadratic_theorem"]["cp2_sd1_product_quadratic_density_coefficient"] == "908925/2"
    assert data["refined_quadratic_theorem"]["k3_sd1_product_quadratic_density_coefficient"] == "1835497/4"
    assert "exact quadratic data at the first barycentric refinement step" in data["bridge_verdict"]
