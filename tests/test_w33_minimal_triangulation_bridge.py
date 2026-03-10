from __future__ import annotations

import json
from pathlib import Path

from w33_minimal_triangulation_bridge import (
    barycentric_subdivision_f_vector,
    build_minimal_triangulation_summary,
    cp2_seed,
    euler_characteristic_from_f_vector,
    flat_metric_topologically_forbidden,
    k3_seed,
    max_euler_characteristic_three_neighborly_4manifold,
    minimum_vertices_for_euler_characteristic,
    neighborly_4manifold_f_vector,
    write_summary,
)


def test_cp2_neighborly_seed_matches_classical_f_vector() -> None:
    seed = cp2_seed()
    assert seed.vertices == 9
    assert seed.euler_characteristic == 3
    assert seed.f_vector == (9, 36, 84, 90, 36)
    assert seed.flat_metric_topologically_forbidden is True


def test_k3_neighborly_seed_matches_classical_f_vector() -> None:
    seed = k3_seed()
    assert seed.vertices == 16
    assert seed.euler_characteristic == 24
    assert seed.f_vector == (16, 120, 560, 720, 288)
    assert seed.flat_metric_topologically_forbidden is True


def test_three_neighborly_bound_detects_minimal_vertex_counts_for_cp2_and_k3() -> None:
    assert minimum_vertices_for_euler_characteristic(3) == 9
    assert minimum_vertices_for_euler_characteristic(24) == 16
    assert max_euler_characteristic_three_neighborly_4manifold(8) < 3
    assert max_euler_characteristic_three_neighborly_4manifold(15) < 24


def test_barycentric_subdivision_preserves_dimension_and_multiplies_top_simplices() -> None:
    cp2 = cp2_seed()
    sd1 = barycentric_subdivision_f_vector(cp2.f_vector, steps=1)
    sd2 = barycentric_subdivision_f_vector(cp2.f_vector, steps=2)
    assert len(sd1) == 5
    assert euler_characteristic_from_f_vector(sd1) == cp2.euler_characteristic
    assert euler_characteristic_from_f_vector(sd2) == cp2.euler_characteristic
    assert sd1[-1] == 120 * cp2.f_vector[-1]
    assert sd2[-1] == 120 * sd1[-1]


def test_k3_subdivision_gives_a_real_4d_refinement_family() -> None:
    k3 = k3_seed()
    sd1 = barycentric_subdivision_f_vector(k3.f_vector, steps=1)
    sd2 = barycentric_subdivision_f_vector(k3.f_vector, steps=2)
    assert sd1[0] > k3.f_vector[0]
    assert sd2[0] > sd1[0]
    assert sd2[-1] > sd1[-1] > k3.f_vector[-1]


def test_flat_metric_obstruction_is_detected_by_euler_characteristic() -> None:
    assert flat_metric_topologically_forbidden(0) is False
    assert flat_metric_topologically_forbidden(3) is True
    assert flat_metric_topologically_forbidden(24) is True


def test_neighborly_formula_reconstructs_known_seeds() -> None:
    assert neighborly_4manifold_f_vector(9) == cp2_seed().f_vector
    assert neighborly_4manifold_f_vector(16) == k3_seed().f_vector


def test_summary_records_curved_seed_verdict() -> None:
    summary = build_minimal_triangulation_summary()
    assert summary["status"] == "ok"
    assert summary["three_neighborly_bound"]["cp2_min_vertices_from_chi"] == 9
    assert summary["three_neighborly_bound"]["k3_min_vertices_from_chi"] == 16
    assert summary["barycentric_subdivision"]["top_simplex_multiplier_per_step"] == 120
    assert "curved 4D simplicial seed geometries" in summary["bridge_verdict"]


def test_write_summary_emits_json(tmp_path: Path) -> None:
    out = write_summary(tmp_path / "w33_minimal_triangulation_bridge_summary.json")
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["status"] == "ok"
    assert len(data["seeds"]) == 2
