from __future__ import annotations

import json
from pathlib import Path

from w33_center_quad_transport_a2_bridge import (
    build_center_quad_transport_a2_summary,
    write_summary,
)


def test_local_a2_fiber_is_exact_weyl_a2_data() -> None:
    summary = build_center_quad_transport_a2_summary()
    local = summary["local_a2_fiber"]
    assert summary["status"] == "ok"
    assert local["rank"] == 2
    assert local["cartan_matrix"] == [[2, -1], [-1, 2]]
    assert local["weyl_group_order"] == 6
    assert local["all_six_weyl_matrices_realized"] is True
    assert sum(local["edge_matrix_counts"].values()) == 720
    assert local["all_edge_weyl_matrices_preserve_cartan"] is True
    assert local["determinant_character_equals_permutation_parity"] is True


def test_a2_transport_operator_has_exact_spectrum_and_cubic_relation() -> None:
    operator = build_center_quad_transport_a2_summary()["a2_transport_operator"]
    assert operator["dimension"] == 90
    assert operator["spectrum"] == {-16: 6, -1: 64, 8: 20}
    assert operator["laplacian_spectrum"] == {24: 20, 33: 64, 48: 6}
    assert operator["trace_h_squared"] == 2880
    assert operator["trace_h_cubed"] == -14400
    assert operator["cubic_relation_h3_plus_9h2_minus_120h_minus_128i"] is True
    assert operator["matches_standard_sector_up_to_fixed_local_basis_change"] is True


def test_triangle_character_formula_matches_trace_cube() -> None:
    triangle = build_center_quad_transport_a2_summary()["triangle_character_formula"]
    assert triangle["transport_triangles"] == 5280
    assert triangle["holonomy_cycle_type_counts"] == {
        "identity": 240,
        "three_cycle": 2880,
        "transposition": 2160,
    }
    assert triangle["a2_character_values"] == {
        "identity": 2,
        "three_cycle": -1,
        "transposition": 0,
    }
    assert triangle["character_sum_over_triangle_holonomies"] == -2400
    assert triangle["trace_h_cubed_equals_six_character_sum"] is True


def test_summary_write_emits_json(tmp_path: Path) -> None:
    out = write_summary(tmp_path / "w33_center_quad_transport_a2_bridge_summary.json")
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["status"] == "ok"
    assert "A2 root-lattice local system" in data["bridge_verdict"]
