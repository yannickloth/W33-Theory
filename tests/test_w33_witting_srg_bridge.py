from __future__ import annotations

import json
from pathlib import Path

from w33_witting_srg_bridge import (
    build_witting_srg_bridge_summary,
    construct_witting_rays,
    mapped_witting_lines,
    symplectic_lines,
    witting_generalized_quadrangle_profile,
    witting_overlap_profile,
    witting_orthogonal_tetrads,
    witting_srg_parameters,
    witting_to_symplectic_isomorphism,
    write_summary,
)


def test_witting_ray_graph_has_srg_40_12_2_4_parameters() -> None:
    params = witting_srg_parameters()
    assert params.vertices == 40
    assert params.edges == 240
    assert params.degree == 12
    assert params.lambda_parameter == 2
    assert params.mu_parameter == 4
    assert params.spectrum == {"12": 1, "2": 24, "-4": 15}


def test_witting_pair_overlap_profile_is_zero_or_one_third() -> None:
    rays = construct_witting_rays()
    assert len(rays) == 40
    overlap = witting_overlap_profile()
    assert overlap["orthogonal_overlap_squared"] == 0.0
    assert abs(overlap["nonzero_overlap_squared"] - (1 / 3)) < 1e-12


def test_witting_orthogonal_tetrads_give_40_lines() -> None:
    tetrads = witting_orthogonal_tetrads()
    assert len(tetrads) == 40
    assert all(len(tetrad) == 4 for tetrad in tetrads)

    profile = witting_generalized_quadrangle_profile()
    assert profile.points == 40
    assert profile.lines == 40
    assert profile.line_size == 4
    assert profile.lines_through_point == 4
    assert profile.incidence_total == 160


def test_witting_incidence_satisfies_generalized_quadrangle_axiom() -> None:
    profile = witting_generalized_quadrangle_profile()
    assert profile.unique_collinear_point_on_offline_line is True


def test_witting_graph_matches_standard_symplectic_w33_model() -> None:
    mapping = witting_to_symplectic_isomorphism()
    assert len(mapping) == 40
    assert len(set(mapping.values())) == 40
    assert mapped_witting_lines() == symplectic_lines()


def test_write_summary_emits_json(tmp_path: Path) -> None:
    out = write_summary(tmp_path / "w33_witting_srg_bridge_summary.json")
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["status"] == "ok"
    assert data["orthogonality_graph"]["degree"] == 12
    assert data["generalized_quadrangle"]["lines"] == 40
    assert data["symplectic_model"]["graph_isomorphic_to_standard_w33"] is True
    assert "SRG(40,12,2,4)" in data["bridge_verdict"]
