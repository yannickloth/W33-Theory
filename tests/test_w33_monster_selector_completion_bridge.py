from __future__ import annotations

from exploration.w33_monster_selector_completion_bridge import (
    build_monster_selector_completion_summary,
)


def test_selector_completion_is_exact() -> None:
    summary = build_monster_selector_completion_summary()
    completion = summary["selector_completion"]
    assert completion["complement_states"] == 3**7
    assert completion["center_states"] == 3
    assert completion["heisenberg_completion_states"] == 3**6
    assert completion["sl27_traceless_dimension"] == 728
    assert completion["nonzero_golay_codewords"] == 728
    assert completion["full_golay_codewords"] == 729
    assert completion["selector_line_dimension"] == 1
    assert completion["projective_selector_line"] == [1, 2]
    assert completion["w33_kernel_dimension_mod_3"] == 1


def test_selector_completion_decomposition_matches_local_shell() -> None:
    summary = build_monster_selector_completion_summary()
    completion = summary["selector_completion"]
    assert completion["full_codewords_equal_sl27_plus_selector"] is True
    assert completion["nonzero_codewords_equal_sl27_traceless"] is True
    assert completion["complement_equals_center_times_selector_completion"] is True
    assert completion["selector_completion_decomposition_exact"] is True


def test_cross_bridge_dictionary_is_consistent() -> None:
    summary = build_monster_selector_completion_summary()
    bridge = summary["cross_bridge_dictionary"]
    assert bridge["sl27_z3_total_dimension"] == 728
    assert bridge["sl27_bridge_claim_holds"] is True
    assert bridge["golay_nonzero_equals_sl27_total"] is True
    assert bridge["transport_selector_is_unique"] is True
    assert bridge["w33_all_ones_spans_mod_3_kernel"] is True
    assert bridge["transport_projective_selector_line_is_unique"] is True
    assert bridge["path_groupoid_has_unique_invariant_line"] is True

