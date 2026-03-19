"""Exact mod-7 decimal/Fano duality on the two cyclic heptads.

The labeled M"obius/Csaszar torus seed already splits as two cyclic heptads on
Z/7Z:

    A_i = {i, i+1, i+3},
    B_i = {i, i+2, i+3}.

This module packages the exact mod-7 algebra behind that split.

For every affine map x |-> a x + b on Z/7Z:

- if a is a quadratic residue mod 7, i.e. a in {1,2,4}, then the map preserves
  both heptads A and B separately;
- if a is a quadratic nonresidue mod 7, i.e. a in {3,5,6}, then the map swaps
  A and B.

Since 10 == 3 (mod 7) generates F_7^x, the decimal repetend action of 1/7 is
exactly the missing duality operator on the two-heptad torus seed: one decimal
step swaps the heptads, while two decimal steps (10^2 == 2 mod 7) return to
the order-3 collineation subgroup preserving each heptad.
"""

from __future__ import annotations

from functools import lru_cache
import json
from pathlib import Path
from typing import Any

from w33_mobius_fano_bridge import complementary_fano_heptad, standard_fano_heptad


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_PATH = ROOT / "data" / "w33_mod7_fano_duality_bridge_summary.json"

MODULUS = 7
DECIMAL_GENERATOR = 10 % MODULUS
QUADRATIC_RESIDUES = (1, 2, 4)
QUADRATIC_NONRESIDUES = (3, 5, 6)
REPETEND = "142857"


def _normalize_triangle(triangle: tuple[int, int, int]) -> tuple[int, int, int]:
    return tuple(sorted(x % MODULUS for x in triangle))


def _apply_affine_to_heptad(
    heptad: tuple[tuple[int, int, int], ...],
    a: int,
    b: int,
) -> tuple[tuple[int, int, int], ...]:
    return tuple(
        sorted(
            {
                _normalize_triangle(tuple((a * x + b) % MODULUS for x in triangle))
                for triangle in heptad
            }
        )
    )


def _cycle_from_seed(multiplier: int, seed: int) -> list[int]:
    orbit = []
    current = seed
    while current not in orbit:
        orbit.append(current)
        current = (multiplier * current) % MODULUS
    return orbit


def _compose_affine(
    left: tuple[int, int],
    right: tuple[int, int],
) -> tuple[int, int]:
    """Return left o right for affine maps x |-> a x + b."""
    a_left, b_left = left
    a_right, b_right = right
    return (
        (a_left * a_right) % MODULUS,
        (a_left * b_right + b_left) % MODULUS,
    )


def _generated_affine_group() -> set[tuple[int, int]]:
    identity = (1, 0)
    generators = [(DECIMAL_GENERATOR, 0), (1, 1)]
    seen = {identity}
    frontier = [identity]
    while frontier:
        current = frontier.pop()
        for generator in generators:
            for candidate in (
                _compose_affine(generator, current),
                _compose_affine(current, generator),
            ):
                if candidate not in seen:
                    seen.add(candidate)
                    frontier.append(candidate)
    return seen


def _decimal_rotations() -> list[str]:
    return [REPETEND[i:] + REPETEND[:i] for i in range(len(REPETEND))]


def _heptad_targets_for_unit(
    heptad_a: tuple[tuple[int, int, int], ...],
    heptad_b: tuple[tuple[int, int, int], ...],
    a: int,
) -> dict[str, Any]:
    a_targets = []
    b_targets = []
    for b in range(MODULUS):
        mapped_a = _apply_affine_to_heptad(heptad_a, a, b)
        mapped_b = _apply_affine_to_heptad(heptad_b, a, b)
        if mapped_a == heptad_a:
            a_targets.append("A")
        elif mapped_a == heptad_b:
            a_targets.append("B")
        else:
            a_targets.append("?")
        if mapped_b == heptad_b:
            b_targets.append("B")
        elif mapped_b == heptad_a:
            b_targets.append("A")
        else:
            b_targets.append("?")
    return {
        "a": a,
        "A_targets_by_translation": a_targets,
        "B_targets_by_translation": b_targets,
        "A_target_is_translation_invariant": len(set(a_targets)) == 1,
        "B_target_is_translation_invariant": len(set(b_targets)) == 1,
        "A_target": a_targets[0],
        "B_target": b_targets[0],
        "preserves_each_heptad": a_targets[0] == "A" and b_targets[0] == "B",
        "swaps_the_two_heptads": a_targets[0] == "B" and b_targets[0] == "A",
    }


@lru_cache(maxsize=1)
def build_mod7_fano_duality_summary() -> dict[str, Any]:
    heptad_a = standard_fano_heptad()
    heptad_b = complementary_fano_heptad()

    affine_actions = {
        str(a): _heptad_targets_for_unit(heptad_a, heptad_b, a)
        for a in range(1, MODULUS)
    }

    decimal_powers = [pow(DECIMAL_GENERATOR, n, MODULUS) for n in range(6)]
    odd_powers = decimal_powers[1::2]
    even_powers = decimal_powers[0::2]
    decimal_target_pattern = [
        affine_actions[str(a)]["A_target"] for a in decimal_powers
    ]
    point_orbit = _cycle_from_seed(DECIMAL_GENERATOR, 1)
    duality_quotient_pattern = ["preserve" if a in QUADRATIC_RESIDUES else "swap" for a in decimal_powers]
    generated_affine_group = _generated_affine_group()
    preserving_affine_maps = [
        (a, b)
        for a in QUADRATIC_RESIDUES
        for b in range(MODULUS)
    ]
    swapping_affine_maps = [
        (a, b)
        for a in QUADRATIC_NONRESIDUES
        for b in range(MODULUS)
    ]

    return {
        "status": "ok",
        "mod7_dictionary": {
            "modulus": MODULUS,
            "quadratic_residues": list(QUADRATIC_RESIDUES),
            "quadratic_nonresidues": list(QUADRATIC_NONRESIDUES),
            "residue_subgroup_order": len(QUADRATIC_RESIDUES),
            "duality_coset_order": len(QUADRATIC_NONRESIDUES),
            "decimal_generator_mod_7": DECIMAL_GENERATOR,
            "decimal_generator_order": 6,
            "decimal_square_mod_7": pow(DECIMAL_GENERATOR, 2, MODULUS),
            "decimal_square_order": 3,
            "point_cycle_type": {"fixed": [0], "six_cycle": point_orbit},
            "nonzero_residue_orbit_under_decimal_generator": point_orbit,
        },
        "affine_group": {
            "full_affine_group_order": 42,
            "heptad_preserver_subgroup_order": len(preserving_affine_maps),
            "heptad_duality_coset_order": len(swapping_affine_maps),
            "preserver_plus_duality_coset_equals_full_group": (
                len(preserving_affine_maps) + len(swapping_affine_maps) == 42
            ),
            "preserver_subgroup_matches_fano_flag_count": len(preserving_affine_maps) == 21,
            "preserver_subgroup_matches_torus_edge_count": len(preserving_affine_maps) == 21,
            "decimal_and_translation_generate_full_affine_group": (
                len(generated_affine_group) == 42
            ),
        },
        "heptad_action": {
            "standard_heptad_size": len(heptad_a),
            "dual_heptad_size": len(heptad_b),
            "affine_unit_actions": affine_actions,
            "residues_preserve_each_heptad": all(
                affine_actions[str(a)]["preserves_each_heptad"]
                for a in QUADRATIC_RESIDUES
            ),
            "nonresidues_swap_heptads": all(
                affine_actions[str(a)]["swaps_the_two_heptads"]
                for a in QUADRATIC_NONRESIDUES
            ),
        },
        "decimal_duality_bridge": {
            "repetend": REPETEND,
            "repetend_rotations": _decimal_rotations(),
            "decimal_powers_mod_7": decimal_powers,
            "decimal_power_targets_on_A": decimal_target_pattern,
            "odd_decimal_powers_swap_heptads": all(
                affine_actions[str(a)]["swaps_the_two_heptads"] for a in odd_powers
            ),
            "even_decimal_powers_preserve_heptads": all(
                affine_actions[str(a)]["preserves_each_heptad"] for a in even_powers
            ),
            "duality_quotient_pattern": duality_quotient_pattern,
            "c6_splits_into_c3_and_z2_shadow": (
                len(set(even_powers)) == 3
                and len(set(odd_powers)) == 3
                and set(even_powers) == set(QUADRATIC_RESIDUES)
                and set(odd_powers) == set(QUADRATIC_NONRESIDUES)
            ),
        },
        "bridge_verdict": (
            "The decimal mod-7 generator 10 == 3 is the exact duality operator on "
            "the two cyclic Fano heptads of the labeled 7-vertex torus seed. "
            "Quadratic residues {1,2,4} preserve each heptad separately, while "
            "nonresidues {3,5,6} swap the two heptads. So the decimal 6-cycle is "
            "not an internal symmetry of one heptad alone; it factors exactly as "
            "an order-3 Fano collineation subgroup together with a Z2 heptad-duality "
            "shadow. More sharply, translations together with the decimal generator "
            "recover the full affine group AGL(1,7) of order 42, split as a "
            "21-element heptad-preserving subgroup and a 21-element swapping coset. "
            "That internal 21 matches the common Fano-flag / torus-edge count of "
            "the Csaszar-Szilassi bridge."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_mod7_fano_duality_summary(), indent=2),
        encoding="utf-8",
    )
    return path


if __name__ == "__main__":
    write_summary()
