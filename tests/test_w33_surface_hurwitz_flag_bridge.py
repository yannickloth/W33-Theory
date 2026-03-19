from __future__ import annotations

import json
from pathlib import Path

from w33_surface_hurwitz_flag_bridge import (
    build_surface_hurwitz_flag_summary,
    write_summary,
)


def test_surface_hurwitz_flag_shell_closes_exactly() -> None:
    summary = build_surface_hurwitz_flag_summary()
    shell = summary["surface_hurwitz_dictionary"]
    factors = summary["exact_factorizations"]
    assert shell["q"] == 3
    assert shell["q_plus_one"] == 4
    assert shell["phi6"] == 7
    assert shell["genus_denominator"] == 12
    assert shell["tetrahedron_fixed_point"] == 4
    assert shell["nonzero_surface_residues_mod_12"] == [3, 4, 7]
    assert shell["single_surface_flags"] == 84
    assert shell["dual_pair_flags"] == 168
    assert shell["heawood_preserving_order"] == 168
    assert shell["heawood_full_order"] == 336
    assert shell["heawood_vertices"] == 14
    assert shell["heawood_edges"] == 21
    assert shell["shared_six_channel"] == 6
    assert factors["nonzero_surface_residues_are_q_q_plus_one_phi6"] is True
    assert factors["nonzero_surface_residues_add_to_phi6"] is True
    assert factors["single_surface_flags_equals_product_of_nonzero_surface_residues"] is True
    assert factors["single_surface_flags_equals_genus_denominator_times_phi6"] is True
    assert factors["single_surface_flags_equals_heawood_vertices_times_shared_six"] is True
    assert factors["single_surface_flags_equals_heawood_edges_times_tetrahedron_fixed_point"] is True
    assert factors["dual_pair_flags_equals_heawood_preserving_order"] is True
    assert factors["full_heawood_order_equals_four_single_surface_flag_packets"] is True


def test_surface_flag_shell_selects_q3_uniquely() -> None:
    summary = build_surface_hurwitz_flag_summary()
    selection = summary["q3_selection"]
    assert selection["surface_flag_shell_formula"] == "q(q+1)Phi_6(q)"
    assert selection["phi6_formula"] == "q^2 - q + 1"
    assert selection["target_single_surface_flag_packet"] == 84
    assert selection["positive_integer_solutions"] == [3]
    assert selection["q3_is_unique_positive_solution"] is True
    assert "3+4=7 and 3*4*7=84" in summary["bridge_verdict"]


def test_write_summary_emits_json(tmp_path: Path) -> None:
    out = write_summary(tmp_path / "w33_surface_hurwitz_flag_bridge_summary.json")
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["status"] == "ok"
    assert data["surface_hurwitz_dictionary"]["single_surface_flags"] == 84
