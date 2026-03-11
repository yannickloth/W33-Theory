from __future__ import annotations

import json
from pathlib import Path

from w33_center_quad_transport_operator_bridge import (
    build_center_quad_transport_operator_summary,
    write_summary,
)


def test_connection_bundle_has_exact_integer_spectra() -> None:
    summary = build_center_quad_transport_operator_summary()
    bundle = summary["connection_bundle"]
    assert summary["status"] == "ok"
    assert bundle["base_vertices"] == 45
    assert bundle["fiber_dimension"] == 3
    assert bundle["total_dimension"] == 135
    assert bundle["adjacency_spectrum"] == {
        -16: 6,
        -4: 20,
        -1: 64,
        2: 24,
        8: 20,
        32: 1,
    }
    assert bundle["laplacian_spectrum"] == {
        0: 1,
        24: 20,
        30: 24,
        33: 64,
        36: 20,
        48: 6,
    }
    assert bundle["trace_a_squared"] == 4320
    assert bundle["trace_a_cubed"] == 17280


def test_trivial_and_standard_sectors_split_exactly() -> None:
    split = build_center_quad_transport_operator_summary()["trivial_standard_split"]
    assert split["trivial_dimension"] == 45
    assert split["standard_dimension"] == 90
    assert split["trivial_standard_coupling_max_abs"] < 1e-12
    assert split["trivial_block_equals_transport_adjacency"] is True
    assert split["trivial_block_spectrum"] == {-4: 20, 2: 24, 32: 1}
    assert split["standard_block_spectrum"] == {-16: 6, -1: 64, 8: 20}
    assert split["standard_block_laplacian_spectrum"] == {24: 20, 33: 64, 48: 6}
    assert split["standard_block_cubic_relation_exact_up_to_tolerance"] is True


def test_signed_holonomy_operator_is_quadratic_and_encodes_triangle_excess() -> None:
    signed = build_center_quad_transport_operator_summary()["signed_holonomy_operator"]
    assert signed["dimension"] == 45
    assert signed["spectrum"] == {-4: 30, 8: 15}
    assert signed["quadratic_identity_s_squared_equals_4s_plus_32i"] is True
    assert signed["laplacian_spectrum"] == {24: 15, 36: 30}
    assert signed["trace_s_squared"] == 1440
    assert signed["trace_s_cubed"] == 5760
    assert signed["triangle_parity_counts"] == {"parity0": 3120, "parity1": 2160}
    assert signed["signed_triangle_excess"] == 960
    assert signed["trace_s_cubed_equals_six_times_signed_triangle_excess"] is True


def test_summary_write_emits_json(tmp_path: Path) -> None:
    out = write_summary(tmp_path / "w33_center_quad_transport_operator_bridge_summary.json")
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["status"] == "ok"
    assert "explicit operator" in data["bridge_verdict"]
