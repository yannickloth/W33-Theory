from __future__ import annotations

from w33_klein_harmonic_vogel_bridge import build_klein_harmonic_vogel_summary


def test_harmonic_cube_packets_match_g2_shell() -> None:
    summary = build_klein_harmonic_vogel_summary()
    bridge = summary["harmonic_quartic_dictionary"]
    assert bridge["harmonic_cubes"] == 7
    assert bridge["harmonic_anticubes"] == 7
    assert bridge["harmonic_packet_total"] == 14
    assert bridge["g2_dimension"] == 14
    assert bridge["harmonic_packet_total_equals_g2_dimension"] is True


def test_klein_quartic_counts_match_promoted_live_factors() -> None:
    summary = build_klein_harmonic_vogel_summary()
    bridge = summary["harmonic_quartic_dictionary"]
    factorizations = summary["promoted_factorizations"]
    assert bridge["klein_quartic_vertices"] == 24
    assert bridge["klein_quartic_triangles"] == 56
    assert bridge["klein_quartic_edges"] == 84
    assert bridge["klein_quartic_automorphism_order"] == 168
    assert bridge["triangles_equals_packets_times_spacetime"] is True
    assert bridge["triangles_equals_two_times_bitangents"] is True
    assert bridge["triangles_equals_cartan_times_phi6"] is True
    assert factorizations["edges_equals_packets_times_shared_six"] is True
    assert factorizations["edges_equals_four_times_ag21"] is True
    assert factorizations["edges_equals_gauge_closure_times_phi6"] is True
    assert factorizations["automorphisms_equals_two_times_edges"] is True
    assert factorizations["automorphisms_equals_eight_times_ag21"] is True
    assert factorizations["automorphisms_equals_vertex_seed_times_phi6"] is True


def test_ambient_and_sl27_shells_close_exactly() -> None:
    summary = build_klein_harmonic_vogel_summary()
    bridge = summary["harmonic_quartic_dictionary"]
    factorizations = summary["promoted_factorizations"]
    assert bridge["ambient_pg53_points"] == 364
    assert bridge["w33_klein_slice_points"] == 40
    assert bridge["moonshine_gap"] == 324
    assert bridge["sl27_shell_dimension"] == 728
    assert bridge["phi3"] == 13
    assert bridge["bitangent_count"] == 28
    assert bridge["a26_rank"] == 26
    assert factorizations["ambient_equals_g2_times_a26"] is True
    assert factorizations["ambient_equals_bitangents_times_phi3"] is True
    assert factorizations["ambient_equals_w33_slice_plus_gap"] is True
    assert factorizations["sl27_equals_two_times_ambient"] is True
    assert factorizations["sl27_equals_bitangents_times_a26"] is True
    assert factorizations["sl27_equals_triangles_times_phi3"] is True
    assert factorizations["gap_equals_spacetime_times_logical_qutrits"] is True
