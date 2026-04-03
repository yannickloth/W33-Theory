from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXPLORATION = ROOT / "exploration"
if str(EXPLORATION) not in sys.path:
    sys.path.insert(0, str(EXPLORATION))

from w33_continuum_seed_isolation_bridge import (  # noqa: E402
    build_continuum_seed_isolation_bridge_summary,
)


def test_first_order_seed_dependence_is_isolated_to_r20_channel() -> None:
    summary = build_continuum_seed_isolation_bridge_summary()
    transport = summary["first_order_seed_isolation"]["transport"]
    matter = summary["first_order_seed_isolation"]["matter_coupled"]

    assert transport["constant_limit_gap"]["exact"] == "0"
    assert transport["constant_corr120_gap"]["exact"] == "0"
    assert transport["linear_limit_gap"]["exact"] == "0"
    assert transport["linear_corr120_gap"]["exact"] == "0"
    assert transport["constant_corr20_gap"]["exact"] == "14105"
    assert transport["linear_corr20_gap"]["exact"] == "143654"
    assert transport["seed_dependence_is_only_in_r20_channel"] is True

    assert matter["constant_limit_gap"]["exact"] == "0"
    assert matter["constant_corr120_gap"]["exact"] == "0"
    assert matter["linear_limit_gap"]["exact"] == "0"
    assert matter["linear_corr120_gap"]["exact"] == "0"
    assert matter["constant_corr20_gap"]["exact"] == "1142505"
    assert matter["linear_corr20_gap"]["exact"] == "11635974"
    assert matter["seed_dependence_is_only_in_r20_channel"] is True


def test_quadratic_gap_contraction_is_exact() -> None:
    summary = build_continuum_seed_isolation_bridge_summary()
    theorem = summary["quadratic_gap_contraction"]

    assert theorem["transport_seed_gap"]["exact"] == "3396050/3"
    assert theorem["transport_sd1_gap"]["exact"] == "3904481/4"
    assert theorem["transport_first_refinement_contracts_gap"] is True

    assert theorem["matter_seed_gap"]["exact"] == "91693350"
    assert theorem["matter_sd1_gap"]["exact"] == "316262961/4"
    assert theorem["matter_first_refinement_contracts_gap"] is True


def test_continuum_seed_isolation_theorem_is_exact() -> None:
    summary = build_continuum_seed_isolation_bridge_summary()
    theorem = summary["continuum_seed_isolation_theorem"]

    assert theorem[
        "transport_first_order_limit_and_topological_corrections_are_seed_universal"
    ] is True
    assert theorem[
        "matter_first_order_limit_and_topological_corrections_are_seed_universal"
    ] is True
    assert theorem[
        "all_first_order_seed_dependence_is_isolated_to_the_r20_local_channel"
    ] is True
    assert theorem["transport_quadratic_gap_contracts_at_first_refinement"] is True
    assert theorem["matter_quadratic_gap_contracts_at_first_refinement"] is True
    assert theorem[
        "therefore_the_remaining_continuum_seed_dependence_is_a_contracting_local_tail_channel_effect"
    ] is True
