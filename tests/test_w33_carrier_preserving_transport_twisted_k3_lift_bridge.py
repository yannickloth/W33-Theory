from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXPLORATION = ROOT / "exploration"
if str(EXPLORATION) not in sys.path:
    sys.path.insert(0, str(EXPLORATION))

from w33_carrier_preserving_transport_twisted_k3_lift_bridge import (  # noqa: E402
    build_carrier_preserving_transport_twisted_k3_lift_bridge_summary,
)


def test_carrier_preserving_transport_twisted_k3_lift_summary() -> None:
    summary = build_carrier_preserving_transport_twisted_k3_lift_bridge_summary()
    theorem = summary["carrier_preserving_transport_twisted_k3_lift_theorem"]
    fixed = summary["fixed_external_carrier_package"]
    internal = summary["internal_transport_twisted_package"]

    assert fixed["carrier_plane"] == "U1"
    assert fixed["ordered_filtration_dimensions"] == [81, 162, 81]
    assert fixed["slot_direction"] == "tail_to_head"
    assert fixed["slot_shape"] == [81, 81]

    assert internal["twisted_cocycle_not_coboundary"] is True
    assert internal["matter_extension_dimension"] == 162
    assert internal["matter_extension_rank"] == 81
    assert internal["precomplex_curvature_rank"] == 42
    assert internal["precomplex_off_diagonal_rank"] == 36

    assert theorem[
        "the_external_carrier_package_is_already_fixed_before_any_genuine_k3_realization"
    ] is True
    assert theorem[
        "the_missing_internal_datum_is_already_a_nontrivial_twisted_cocycle"
    ] is True
    assert theorem[
        "the_missing_internal_datum_already_assembles_into_an_exact_transport_twisted_precomplex"
    ] is True
    assert theorem[
        "the_shared_nonzero_completion_wall_is_already_localized_as_datum_to_avatar_lift"
    ] is True
    assert theorem[
        "therefore_any_exact_k3_side_realization_must_be_a_carrier_preserving_transport_twisted_lift"
    ] is True
    assert theorem[
        "the_open_wall_is_existence_of_that_carrier_preserving_transport_twisted_k3_lift"
    ] is True
