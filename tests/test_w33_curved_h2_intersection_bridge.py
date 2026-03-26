from __future__ import annotations

from w33_curved_h2_intersection_bridge import build_curved_h2_intersection_summary


def _profile(summary: dict, name: str) -> dict:
    for profile in summary["seed_profiles"]:
        if profile["name"] == name:
            return profile
    raise AssertionError(f"missing profile {name}")


def test_curved_h2_intersection_bridge_recovers_chain_level_signatures() -> None:
    summary = build_curved_h2_intersection_summary()
    assert summary["status"] == "ok"

    cp2 = _profile(summary, "CP2_9")
    assert cp2["h2_dimension"] == 1
    assert cp2["signature_positive"] == 1
    assert cp2["signature_negative"] == 0
    assert cp2["recovered_signature"] == 1
    assert cp2["fundamental_class_boundary_is_zero"] is True
    assert cp2["matches_topological_signature"] is True

    k3 = _profile(summary, "K3_16")
    assert k3["h2_dimension"] == 22
    assert k3["signature_positive"] == 3
    assert k3["signature_negative"] == 19
    assert k3["recovered_signature"] == -16
    assert k3["fundamental_class_boundary_is_zero"] is True
    assert k3["fundamental_class_positive_facets"] == 144
    assert k3["fundamental_class_negative_facets"] == 144
    assert k3["matches_topological_signature"] is True

    theorem = summary["bridge_theorem"]
    assert theorem["chain_level_cup_form_recovers_cp2_signature"] is True
    assert theorem["chain_level_cup_form_recovers_k3_signature"] is True


def test_curved_h2_intersection_bridge_selects_canonical_k3_mixed_plane() -> None:
    summary = build_curved_h2_intersection_summary()
    plane = summary["k3_canonical_mixed_plane"]

    assert plane["source_triangle_index"] == 0
    assert plane["source_triangle"] == [1, 2, 3]
    assert plane["plane_basis_order"] == ["positive_line", "negative_line"]
    assert plane["positive_line_nonzero_entries"] > 0
    assert plane["negative_line_nonzero_entries"] > 0
    assert plane["euclidean_orthogonality_error"] < 1e-10
    assert plane["positive_cup_value"] > 0.0
    assert plane["negative_cup_value"] < 0.0
    assert plane["cross_cup_value_abs"] < 1e-10
    assert plane["plane_is_mixed"] is True

    theorem = summary["bridge_theorem"]
    assert theorem["k3_canonical_mixed_plane_is_determined_by_projector_and_cup_form"] is True
    assert theorem["k3_canonical_mixed_plane_is_mixed_signature"] is True
