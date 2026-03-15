"""Exact Yukawa scaffold closure for the live Standard Model bridge.

This module packages the strongest exact Yukawa-side content already present in
the repo into one theorem-level object.

What is already exact:

  - the clean Higgs pair is H_2 and Hbar_2;
  - the canonical mixed seed is reconstructed exactly from native internal
    data: replicated diagonal Yukawa + one reference off-diagonal block + the
    slot-independent V4 label matrix

        [[AB, I, A],
         [AB, I, A],
         [ A, B, 0]];

  - the right-handed support splits rigidly under the V4 projector theorem:
        H_2:    2+2,
        Hbar_2: 1+3;

  - the minimal exact A2 full-activation seeds are the two fans [8,9] and
    [246,247];
  - the CE2 quark bridge gives an exact trivial closure and an exact no-go:
    the zero quark point is the unique fully clean point in the arbitrary
    screen.

So the exact Yukawa-side state of the theory is not "unknown". It is an exact
scaffold with one remaining frontier: the final nonzero eigenvalue spectrum.
"""

from __future__ import annotations

from functools import lru_cache
import json
from pathlib import Path
from typing import Any

from w33_ce2_quark_bridge import build_ce2_quark_bridge_certificate
from w33_l6_a2_mixed_seed_bridge import build_l6_a2_mixed_seed_bridge_summary
from w33_l6_v4_projector_bridge import build_l6_v4_projector_bridge_summary
from w33_l6_v4_seed_reconstruction_bridge import (
    build_l6_v4_seed_reconstruction_bridge_summary,
)
from w33_standard_model_action_backbone_bridge import (
    build_standard_model_action_backbone_summary,
)


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_PATH = ROOT / "data" / "w33_yukawa_scaffold_bridge_summary.json"


@lru_cache(maxsize=1)
def build_yukawa_scaffold_summary() -> dict[str, Any]:
    sm = build_standard_model_action_backbone_summary()
    seed = build_l6_v4_seed_reconstruction_bridge_summary()
    projectors = build_l6_v4_projector_bridge_summary()
    mixed = build_l6_a2_mixed_seed_bridge_summary()
    ce2 = build_ce2_quark_bridge_certificate()

    label_matrix = seed["seed_reconstruction_theorem"]["expected_label_matrix"]
    h2_proj = projectors["slot_profiles"]["H_2"]["projectors"]
    hbar2_proj = projectors["slot_profiles"]["Hbar_2"]["projectors"]
    minimal_full = mixed["activation_theorems"]["minimal_full_a2_activation_seed_modes"]
    minimal_rank_lift = mixed["activation_theorems"]["minimal_rank_lift_seed_modes"]

    return {
        "status": "ok",
        "sm_backbone_anchor": {
            "clean_higgs_slots": sm["fermion_representation_backbone"]["clean_higgs_slots"],
            "clean_higgs_pair_is_h2_hbar2": sm["fermion_representation_backbone"]["clean_higgs_pair_is_h2_hbar2"],
            "one_generation_spinor_dimension": sm["fermion_representation_backbone"]["one_generation_spinor_dimension"],
            "three_generation_matter_dimension": sm["fermion_representation_backbone"]["three_generation_matter_dimension"],
        },
        "canonical_texture": {
            "label_matrix": label_matrix,
            "label_matrix_is_slot_independent": seed["seed_reconstruction_theorem"]["label_matrix_is_slot_independent"],
            "reconstructs_exactly_for_both_slots": seed["seed_reconstruction_theorem"]["reconstructs_canonical_closure_exactly_for_both_slots"],
            "generation_0_diagonal_delta_equals_offdiag_1_to_0": seed["seed_reconstruction_theorem"]["generation_0_diagonal_delta_equals_offdiag_1_to_0_for_both_slots"],
            "generation_1_diagonal_delta_equals_offdiag_0_to_1": seed["seed_reconstruction_theorem"]["generation_1_diagonal_delta_equals_offdiag_0_to_1_for_both_slots"],
            "generation_2_diagonal_block_unchanged": seed["seed_reconstruction_theorem"]["generation_2_diagonal_block_is_unchanged_for_both_slots"],
        },
        "v4_projector_scaffold": {
            "minus_minus_projector_vanishes": projectors["projector_theorem"]["minus_minus_projector_vanishes_for_both_slots"],
            "plus_plus_is_inactive_support": projectors["projector_theorem"]["plus_plus_projector_is_exact_inactive_support_for_both_slots"],
            "h2_split": {
                "minus_plus": h2_proj["-+"]["support_labels"],
                "plus_minus": h2_proj["+-"]["support_labels"],
            },
            "hbar2_split": {
                "minus_plus": hbar2_proj["-+"]["support_labels"],
                "plus_minus": hbar2_proj["+-"]["support_labels"],
            },
            "h2_active_support_splits_as_2_plus_2": projectors["projector_theorem"]["h2_active_support_splits_as_2_plus_2"],
            "hbar2_active_support_splits_as_1_plus_3": projectors["projector_theorem"]["hbar2_active_support_splits_as_1_plus_3"],
        },
        "a2_activation_scaffold": {
            "minimal_full_a2_activation_seed_modes": minimal_full,
            "minimal_full_activation_is_exactly_fan_type": mixed["activation_theorems"]["minimal_full_activation_profiles_are_exactly_fans"],
            "minimal_rank_lift_seed_modes": minimal_rank_lift,
            "minimal_rank_lift_seed_size": mixed["activation_theorems"]["minimal_rank_lift_seed_size"],
            "max_response_rank_within_unit_seed_family": mixed["activation_theorems"]["max_response_rank_within_unit_a2_seed_family"],
            "max_augmented_rank_within_unit_seed_family": mixed["activation_theorems"]["max_augmented_rank_within_unit_a2_seed_family"],
            "fan_closure_has_full_3x3_support": mixed["activation_theorems"]["fan_closure_seeds_have_full_3x3_support"],
            "fan_closure_has_isotropic_offdiag_shell": mixed["activation_theorems"]["fan_closure_seeds_have_slotwise_isotropic_off_diagonal_shell"],
        },
        "ce2_boundary": {
            "generated_source_unit_count": ce2.generated_source_unit_count,
            "projected_mode_count": ce2.projected_mode_count,
            "response_rank": ce2.response_rank,
            "augmented_rank": ce2.augmented_rank,
            "arbitrary_quark_screen_rank": ce2.arbitrary_quark_screen_rank,
            "arbitrary_quark_screen_nullity": ce2.arbitrary_quark_screen_nullity,
            "trivial_closure_total_residual_norm": ce2.trivial_closure_total_residual_norm,
            "zero_is_unique_clean_point": ce2.zero_is_unique_clean_point,
            "l4_response_contained_in_ce2": ce2.l4_response_contained_in_ce2,
        },
        "frontier_boundary": {
            "yukawa_scaffold_is_exact": True,
            "nonzero_yukawa_eigenvalues_still_open": True,
            "exact_open_problem_is_spectrum_not_support_or_symmetry": True,
        },
        "bridge_verdict": (
            "The Yukawa side is now exact at scaffold level. The clean Higgs pair "
            "is H_2 and Hbar_2, the canonical mixed seed is reconstructed exactly "
            "from one reference block plus the slot-independent V4 label matrix "
            "[[AB,I,A],[AB,I,A],[A,B,0]], the right-handed support splits rigidly "
            "as 2+2 and 1+3, the minimal full A2 activation is given by the two "
            "fan seeds [8,9] and [246,247], the projected CE2 bridge has exact "
            "rank 28 on the 54-mode quark screen, and the full arbitrary quark "
            "screen has exact rank 36 with nullity 0, so the zero quark point is "
            "the unique fully clean point. So the remaining Yukawa problem is no "
            "longer support, symmetry, or action structure. It is the final "
            "nonzero eigenvalue spectrum."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_yukawa_scaffold_summary(), indent=2),
        encoding="utf-8",
    )
    return path


if __name__ == "__main__":
    write_summary()
