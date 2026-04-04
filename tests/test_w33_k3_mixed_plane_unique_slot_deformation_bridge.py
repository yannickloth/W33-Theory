from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXPLORATION = ROOT / "exploration"
if str(EXPLORATION) not in sys.path:
    sys.path.insert(0, str(EXPLORATION))

from w33_k3_mixed_plane_unique_slot_deformation_bridge import (  # noqa: E402
    build_k3_mixed_plane_unique_slot_deformation_summary,
)


def test_slot_only_deformation_class_is_unique() -> None:
    summary = build_k3_mixed_plane_unique_slot_deformation_summary()
    deformation = summary["slot_only_deformation_class"]
    assert deformation["preserved_support_package"] is True
    assert deformation["field"] == "F3"
    assert deformation["nonzero_orbit_size"] == 2
    assert deformation["deformation_type"] == "support_preserving_slot_only"


def test_unique_slot_deformation_theorem_holds() -> None:
    theorem = build_k3_mixed_plane_unique_slot_deformation_summary()[
        "k3_mixed_plane_unique_slot_deformation_theorem"
    ]
    assert theorem[
        "any_exact_k3_tail_witness_must_preserve_the_canonical_mixed_plane_support_package"
    ] is True
    assert theorem[
        "up_to_the_natural_gauge_there_is_only_one_nonzero_slot_orbit_available_for_the_existing_tail_slot"
    ] is True
    assert theorem[
        "therefore_exact_k3_tail_realization_is_equivalent_to_one_unique_support_preserving_slot_only_deformation_class_on_the_canonical_mixed_plane_lift"
    ] is True
    assert theorem[
        "the_live_external_wall_is_now_one_unique_support_preserving_slot_only_deformation_existence_problem"
    ] is True
