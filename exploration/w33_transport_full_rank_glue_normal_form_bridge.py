"""Canonical full-rank normal form for any exact transport glue completion.

The transport frontier is already reduced to one tail-to-head ``81 x 81`` glue
slot on the canonical rigid split avatar. That still sounds like a lot of
freedom, but linear algebra compresses it one step further.

Inside the fixed polarized shell:

- head dimension = ``81``;
- tail dimension = ``81``;
- exact completion requires glue rank ``81``.

So any exact completion glue is automatically an isomorphism from tail to head.
Up to independent basis changes on the fixed head and tail shells, every such
isomorphism is the identity block. Equivalently, the completed polarized
nilpotent has one canonical normal form:

    J_2^{⊕81}

So the remaining wall is no longer glue shape. It is existence of a non-split
completion inside one already-fixed full-rank normal form.
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

from w33_transport_avatar_deformation_wall_bridge import (
    build_transport_avatar_deformation_wall_bridge_summary,
)
from w33_transport_jordan_shadow_bridge import (
    build_transport_jordan_shadow_bridge_summary,
)


DEFAULT_OUTPUT_PATH = (
    ROOT / "data" / "w33_transport_full_rank_glue_normal_form_bridge_summary.json"
)


@lru_cache(maxsize=1)
def build_transport_full_rank_glue_normal_form_bridge_summary() -> dict[str, Any]:
    deformation = build_transport_avatar_deformation_wall_bridge_summary()
    jordan = build_transport_jordan_shadow_bridge_summary()

    avatar = deformation["canonical_split_avatar"]
    slot = deformation["remaining_completion_datum"]
    jordan_packet = jordan["internal_transport_jordan_packet"]

    head_dim = int(avatar["ordered_filtration_dimensions"][0])
    middle_dim = int(avatar["ordered_filtration_dimensions"][1])
    tail_dim = int(avatar["ordered_filtration_dimensions"][2])
    required_rank = int(slot["required_internal_rank"])
    required_square_zero = bool(slot["required_internal_square_zero"])

    full_rank_slot = required_rank == head_dim == tail_dim

    return {
        "status": "ok",
        "fixed_polarized_shell": {
            "head_dimension": head_dim,
            "middle_dimension": middle_dim,
            "tail_dimension": tail_dim,
            "slot_direction": slot["slot_direction"],
            "slot_shape": slot["slot_shape"],
            "required_rank": required_rank,
            "required_square_zero": required_square_zero,
        },
        "canonical_full_rank_completion_normal_form": {
            "slot_matrix_normal_form": f"I_{required_rank}",
            "polarized_nilpotent_normal_form": f"J2^{required_rank}",
            "jordan_partition": jordan_packet["exact_jordan_partition"],
            "nilpotent_rank": jordan_packet["nilpotent_rank"],
            "nilpotent_nullity": jordan_packet["nilpotent_nullity"],
            "square_zero": jordan_packet["square_zero"],
        },
        "transport_full_rank_glue_normal_form_theorem": {
            "any_exact_completion_in_the_fixed_polarized_81_to_162_to_81_shell_has_full_rank_glue": (
                head_dim == 81
                and middle_dim == 162
                and tail_dim == 81
                and required_rank == 81
                and required_square_zero is True
            ),
            "up_to_independent_head_tail_basis_change_any_full_rank_glue_completion_has_identity_slot_matrix": (
                full_rank_slot is True
            ),
            "up_to_polarized_isomorphism_any_exact_completion_has_canonical_jordan_normal_form_two_power_81": (
                full_rank_slot is True
                and jordan["transport_jordan_shadow_theorem"][
                    "internal_transport_glue_has_exact_jordan_type_two_power_81"
                ]
            ),
            "the_remaining_transport_wall_is_existence_of_a_nonsplit_completion_not_glue_shape": (
                full_rank_slot is True
                and deformation["transport_avatar_deformation_wall_theorem"][
                    "the_remaining_transport_wall_is_a_nonsplit_deformation_problem_not_a_search_for_an_unfixed_external_packet"
                ]
            ),
        },
        "bridge_verdict": (
            "Inside the fixed polarized 81 -> 162 -> 81 shell, any exact "
            "completion glue is automatically full rank. So up to independent "
            "head/tail basis change the missing glue block has one canonical "
            "normal form, I_81, and the completed nilpotent has one canonical "
            "polarized Jordan normal form, J2^81. The remaining wall is "
            "therefore existence of a non-split completion, not glue shape."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_transport_full_rank_glue_normal_form_bridge_summary(), indent=2),
        encoding="utf-8",
    )
    return path


def main() -> None:
    path = write_summary()
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
