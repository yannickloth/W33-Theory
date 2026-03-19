from __future__ import annotations

import json
from pathlib import Path

from w33_heawood_harmonic_bridge import (
    build_heawood_harmonic_summary,
    write_summary,
)


def test_heawood_selector_packet_is_exact() -> None:
    summary = build_heawood_harmonic_summary()
    incidence = summary["incidence_operator"]
    assert incidence["matrix_shape"] == [7, 7]
    assert incidence["row_sum"] == 3
    assert incidence["column_sum"] == 3
    assert incidence["bbt_equals_2i_plus_j"] is True
    assert incidence["btb_equals_2i_plus_j"] is True
    assert incidence["selector_eigenvalues_exact"] == ["2", "2", "2", "2", "2", "2", "9"]


def test_heawood_adjacency_and_gap_are_exact() -> None:
    summary = build_heawood_harmonic_summary()
    operator = summary["heawood_operator"]
    assert operator["adjacency_matrix_shape"] == [14, 14]
    assert operator["adjacency_degree"] == 3
    assert operator["adjacency_minimal_polynomial"] == "x^4 - 11*x^2 + 18"
    assert operator["adjacency_quartic_relation_holds"] is True
    assert operator["adjacency_spectrum_exact"] == (
        ["-3"] + ["-sqrt(2)"] * 6 + ["sqrt(2)"] * 6 + ["3"]
    )
    assert operator["laplacian_spectrum_exact"] == (
        ["0"] + ["3 - sqrt(2)"] * 6 + ["sqrt(2) + 3"] * 6 + ["6"]
    )
    assert operator["laplacian_gap_exact"] == "3 - sqrt(2)"


def test_tetra_normalization_matches_heawood_gap() -> None:
    summary = build_heawood_harmonic_summary()
    local = summary["local_normalization"]
    assert local["tetra_weight_for_same_gap_exact"] == "3/4 - sqrt(2)/4"
    assert local["weighted_tetra_nonzero_laplacian_equals_heawood_gap"] is True
    assert "Szilassi dual carries an exact harmonic closure" in summary["bridge_verdict"]


def test_write_summary_emits_json(tmp_path: Path) -> None:
    out = write_summary(tmp_path / "w33_heawood_harmonic_bridge_summary.json")
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["status"] == "ok"
    assert data["heawood_operator"]["laplacian_gap_exact"] == "3 - sqrt(2)"
