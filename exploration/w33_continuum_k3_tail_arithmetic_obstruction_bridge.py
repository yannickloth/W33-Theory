"""K3-side arithmetic obstruction for continuum tail realization.

CCCXCIV fixed the exact arithmetic compatibility of the continuum tail data:
on the fixed primitive tail line the exact transport realization is
characterized by the pair `(lcm, gcd) = (12, 217)`, and the exact matter lift
by `(4, 5859)`.

Independently, the K3-side realization wall was already localized as a
carrier-preserving transport-twisted lift on the fixed avatar shell
`81 -> 162 -> 81`.

This module combines those two promoted layers into the strongest clean
external obstruction currently available:

- any exact K3-side realization must preserve the fixed carrier package;
- it must realize the transport tail on the exact primitive line;
- and therefore it must satisfy the exact arithmetic compatibility pair
  `(12, 217)` on that tail channel, with induced matter pair `(4, 5859)`.

So the remaining wall is not another choice of carrier, shell, or scale. It is
existence of genuine K3-side data satisfying this already-fixed arithmetic
tail-channel obstruction.
"""

from __future__ import annotations

from functools import lru_cache
import json
from pathlib import Path
import sys
from typing import Any


if __package__ in {None, ""}:
    ROOT = Path(__file__).resolve().parents[1]
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
else:
    ROOT = Path(__file__).resolve().parents[1]

from w33_carrier_preserving_transport_twisted_k3_lift_bridge import (  # noqa: E402
    build_carrier_preserving_transport_twisted_k3_lift_bridge_summary,
)
from w33_continuum_tail_arithmetic_compatibility_bridge import (  # noqa: E402
    build_continuum_tail_arithmetic_compatibility_summary,
)
from w33_continuum_transport_realization_wall_bridge import (  # noqa: E402
    build_continuum_transport_realization_wall_summary,
)


DEFAULT_OUTPUT_PATH = (
    ROOT / "data" / "w33_continuum_k3_tail_arithmetic_obstruction_bridge_summary.json"
)


@lru_cache(maxsize=1)
def build_continuum_k3_tail_arithmetic_obstruction_summary() -> dict[str, Any]:
    k3_lift = build_carrier_preserving_transport_twisted_k3_lift_bridge_summary()
    tail_arith = build_continuum_tail_arithmetic_compatibility_summary()
    continuum = build_continuum_transport_realization_wall_summary()

    transport_profile = tail_arith["tail_arithmetic_compatibility"]["transport_profile"]
    matter_profile = tail_arith["tail_arithmetic_compatibility"]["matter_profile"]
    avatar = continuum["fixed_realization_avatar"]
    split = continuum["transport_channel_split"]

    return {
        "status": "ok",
        "fixed_k3_realization_channel": {
            "carrier_plane": k3_lift["fixed_external_carrier_package"]["carrier_plane"],
            "ordered_filtration_dimensions": k3_lift["fixed_external_carrier_package"]["ordered_filtration_dimensions"],
            "slot_direction": k3_lift["fixed_external_carrier_package"]["slot_direction"],
            "slot_shape": k3_lift["fixed_external_carrier_package"]["slot_shape"],
            "tail_channel_dimension": split["tail_channel_dimension"],
            "transport_arithmetic_pair": {
                "denominator_lcm": transport_profile["denominator_lcm"],
                "cleared_coordinate_gcd": transport_profile["cleared_coordinate_gcd"],
                "recovered_scale": transport_profile["recovered_scale"],
            },
            "matter_arithmetic_pair": {
                "denominator_lcm": matter_profile["denominator_lcm"],
                "cleared_coordinate_gcd": matter_profile["cleared_coordinate_gcd"],
                "recovered_scale": matter_profile["recovered_scale"],
            },
        },
        "continuum_k3_tail_arithmetic_obstruction_theorem": {
            "the_external_k3_carrier_package_is_already_fixed_before_realization": (
                k3_lift["carrier_preserving_transport_twisted_k3_lift_theorem"][
                    "the_external_carrier_package_is_already_fixed_before_any_genuine_k3_realization"
                ]
            ),
            "the_remaining_k3_realization_channel_is_exactly_the_curvature_sensitive_tail_81": (
                avatar["tail_line_dimension"] == 81
                and split["tail_channel_dimension"] == 81
                and continuum["continuum_transport_realization_wall_theorem"][
                    "the_remaining_81_copy_is_the_curvature_sensitive_tail_channel"
                ]
            ),
            "any_exact_k3_side_realization_must_satisfy_the_transport_arithmetic_pair_lcm12_gcd217": (
                transport_profile["denominator_lcm"] == 12
                and transport_profile["cleared_coordinate_gcd"] == 217
                and transport_profile["recovered_scale"] == "217/12"
            ),
            "the_induced_matter_side_realization_then_has_pair_lcm4_gcd5859": (
                matter_profile["denominator_lcm"] == 4
                and matter_profile["cleared_coordinate_gcd"] == 5859
                and matter_profile["recovered_scale"] == "5859/4"
            ),
            "therefore_the_live_external_wall_is_existence_of_genuine_k3_data_satisfying_the_fixed_tail_arithmetic_obstruction": (
                k3_lift["carrier_preserving_transport_twisted_k3_lift_theorem"][
                    "therefore_any_exact_k3_side_realization_must_be_a_carrier_preserving_transport_twisted_lift"
                ]
                and transport_profile["denominator_lcm"] == 12
                and transport_profile["cleared_coordinate_gcd"] == 217
            ),
        },
        "bridge_verdict": (
            "The external/K3 realization wall is now arithmetic as well as "
            "geometric. Any exact K3-side realization must preserve the fixed "
            "carrier package and realize its transport datum on the fixed "
            "curvature-sensitive tail 81. Because the exact tail line is already "
            "arithmetically rigid, that realization must satisfy the transport "
            "compatibility pair (lcm,gcd)=(12,217), with induced matter pair "
            "(4,5859). So the open wall is now existence of genuine K3-side "
            "data satisfying one fixed tail arithmetic obstruction."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_continuum_k3_tail_arithmetic_obstruction_summary(), indent=2),
        encoding="utf-8",
    )
    return path


def main() -> None:
    path = write_summary()
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
