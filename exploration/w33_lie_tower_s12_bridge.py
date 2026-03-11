"""Exact bridge from the s12 scripts into the transport/l6 Lie tower.

This module consolidates the exact pieces that now connect the old s12/Golay
scripts to the current finite W33 / transport / Lie-tower stack.

What is established:
  - the s12 grade-only model has exactly six Jacobi-failure triples, namely the
    six non-uniform triples in {1,2}^3, and those failures canonically encode
    the six oriented edges of the three-generation triangle;
  - the corrected l6 exceptional return has exactly six asymmetric sextuple
    patterns, and those patterns canonically encode the same six oriented
    generation channels;
  - the exact l6 A2 operator package already realizes those same six ordered
    generation-transfer channels on the 48-spinor space;
  - the s12 split (242,243,243) is uniquely the block-cyclic Z3 grading of
    sl_27 with partition 27 = 9 + 9 + 9;
  - the Monster 3B / extraspecial 3^(1+12) / Golay / Heisenberg / sl_27 bridge
    supplies the phase mechanism that resolves the grade-only s12 obstruction.

What is not claimed:
  - a literal isomorphism between the s12 toy algebra and the corrected l6
    operator package;
  - that the current linearized l6 Yukawa bridge already activates the A2
    channels dynamically;
  - the final curved 4D spectral-action theorem.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import asdict, dataclass
from functools import lru_cache
import json
from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
for candidate in (ROOT, ROOT / "exploration", ROOT / "scripts", ROOT / "tools"):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

import tools.s12_universal_algebra as s12
from scripts.w33_monster_3b_s12_sl27_bridge import analyze as analyze_monster_3b_s12_sl27
from w33_l6_chiral_gauge_bridge import build_l6_chiral_gauge_bridge_certificate
from w33_l6_exceptional_gauge_return import build_l6_exceptional_gauge_return_certificate
from w33_transport_lie_tower_bridge import l6_a2_generation_channels


DEFAULT_OUTPUT_PATH = ROOT / "data" / "w33_lie_tower_s12_bridge_summary.json"


@dataclass(frozen=True)
class S12FailureChannel:
    grades: tuple[int, int, int]
    jacobi_coeff_mod3: int
    oriented_generation_channel: tuple[int, int]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class L6AsymmetricPatternChannel:
    pattern: tuple[int, int, int, int, int, int]
    entry_count: int
    a2_term_count: int
    generation_multiplicities: tuple[int, int, int]
    oriented_generation_channel: tuple[int, int]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class LieTowerS12CrosswalkRow:
    oriented_generation_channel: tuple[int, int]
    s12_failure_grades: tuple[int, int, int]
    l6_asymmetric_pattern: tuple[int, int, int, int, int, int]
    l6_a2_mode_index: int

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _complete_oriented_generation_graph() -> tuple[tuple[int, int], ...]:
    return tuple((left, right) for left in range(3) for right in range(3) if left != right)


def _nonzero_golay_grade_split() -> dict[int, int]:
    counts = {0: 0, 1: 0, 2: 0}
    for word in s12.enumerate_linear_code_f3(s12.ternary_golay_generator_matrix()):
        if all(int(value) == 0 for value in word):
            continue
        counts[s12.grade_mod3(word)] += 1
    return counts


def _sl_n_block_cyclic_z3_dims(a: int, b: int, c: int) -> dict[str, int]:
    n = int(a + b + c)
    g1 = int(a * b + b * c + c * a)
    return {
        "n": n,
        "g0": int(a * a + b * b + c * c - 1),
        "g1": g1,
        "g2": g1,
        "total": int(n * n - 1),
    }


def _find_matching_sl27_partitions(
    target_g0: int,
    target_g1: int,
    target_g2: int,
    max_block_size: int = 30,
) -> tuple[dict[str, int], ...]:
    matches = []
    for a in range(1, int(max_block_size) + 1):
        for b in range(a, int(max_block_size) + 1):
            for c in range(b, int(max_block_size) + 1):
                dims = _sl_n_block_cyclic_z3_dims(a, b, c)
                if (
                    dims["g0"] == int(target_g0)
                    and dims["g1"] == int(target_g1)
                    and dims["g2"] == int(target_g2)
                ):
                    matches.append(
                        {
                            "a": int(a),
                            "b": int(b),
                            "c": int(c),
                            "n": int(dims["n"]),
                            "g0": int(dims["g0"]),
                            "g1": int(dims["g1"]),
                            "g2": int(dims["g2"]),
                            "total": int(dims["total"]),
                            "a_family_rank": int(dims["n"] - 1),
                        }
                    )
    return tuple(matches)


def s12_failure_to_generation_channel(grades: tuple[int, int, int]) -> tuple[int, int]:
    if len(grades) != 3 or any(int(value) not in {1, 2} for value in grades):
        raise ValueError("Expected a non-uniform s12 failure triple in {1,2}^3")
    equal_edges = [index for index in range(3) if int(grades[index]) == int(grades[(index + 1) % 3])]
    if len(equal_edges) != 1:
        raise ValueError("Expected exactly one equal cyclic edge in s12 failure triple")
    edge = int(equal_edges[0])
    repeated_grade = int(grades[edge])
    if repeated_grade == 1:
        return (edge, (edge + 1) % 3)
    return ((edge + 1) % 3, edge)


def l6_asymmetric_pattern_to_generation_channel(
    pattern: tuple[int, int, int, int, int, int]
) -> tuple[int, int]:
    counts = Counter(int(value) for value in pattern)
    if sorted(counts.values()) != [1, 2, 3]:
        raise ValueError("Expected an l6 asymmetric sextuple with multiplicities 1,2,3")
    source_generation = next(int(generation) for generation, count in counts.items() if count == 3)
    target_generation = next(int(generation) for generation, count in counts.items() if count == 1)
    return (source_generation, target_generation)


@lru_cache(maxsize=1)
def s12_failure_channels() -> tuple[S12FailureChannel, ...]:
    laws = s12.verify_universal_grade_laws()
    records = []
    for row in laws["jacobi_failures"]:
        grades = tuple(int(value) for value in row["grades"])
        records.append(
            S12FailureChannel(
                grades=grades,
                jacobi_coeff_mod3=int(row["jacobi_coeff_mod3"]),
                oriented_generation_channel=s12_failure_to_generation_channel(grades),
            )
        )
    return tuple(records)


@lru_cache(maxsize=1)
def l6_asymmetric_pattern_channels() -> tuple[L6AsymmetricPatternChannel, ...]:
    certificate = build_l6_exceptional_gauge_return_certificate()
    rows = []
    for summary in certificate.asymmetric_summaries:
        multiplicities = Counter(int(value) for value in summary.pattern)
        rows.append(
            L6AsymmetricPatternChannel(
                pattern=summary.pattern,
                entry_count=int(summary.entry_count),
                a2_term_count=int(summary.a2_term_count),
                generation_multiplicities=tuple(int(multiplicities[generation]) for generation in range(3)),
                oriented_generation_channel=l6_asymmetric_pattern_to_generation_channel(summary.pattern),
            )
        )
    return tuple(rows)


@lru_cache(maxsize=1)
def build_lie_tower_s12_bridge_summary() -> dict[str, Any]:
    grade_split = _nonzero_golay_grade_split()
    failures = s12_failure_channels()
    asymmetric_patterns = l6_asymmetric_pattern_channels()
    a2_channels = l6_a2_generation_channels()
    l6_chiral = build_l6_chiral_gauge_bridge_certificate()
    monster = analyze_monster_3b_s12_sl27()

    complete_edge_set = set(_complete_oriented_generation_graph())
    failure_channel_map = {
        row.oriented_generation_channel: row for row in failures
    }
    asymmetric_channel_map = {
        row.oriented_generation_channel: row for row in asymmetric_patterns
    }
    a2_channel_map = {
        (int(channel.source_generation), int(channel.target_generation)): int(channel.mode_index)
        for channel in a2_channels
    }

    sl27_matches = _find_matching_sl27_partitions(
        target_g0=int(grade_split[0]),
        target_g1=int(grade_split[1]),
        target_g2=int(grade_split[2]),
    )
    if len(sl27_matches) != 1:
        raise AssertionError("Expected a unique sl_n block-cyclic match for the s12 grade split")

    sl27_match = sl27_matches[0]
    crosswalk = []
    for channel in sorted(complete_edge_set):
        crosswalk.append(
            LieTowerS12CrosswalkRow(
                oriented_generation_channel=channel,
                s12_failure_grades=failure_channel_map[channel].grades,
                l6_asymmetric_pattern=asymmetric_channel_map[channel].pattern,
                l6_a2_mode_index=int(a2_channel_map[channel]),
            )
        )

    transport_group_bridge = {
        "complete_oriented_generation_graph": [list(edge) for edge in sorted(complete_edge_set)],
        "s12_failure_channels": [list(edge) for edge in sorted(failure_channel_map)],
        "l6_asymmetric_channels": [list(edge) for edge in sorted(asymmetric_channel_map)],
        "l6_a2_generation_channels": [list(edge) for edge in sorted(a2_channel_map)],
        "exact_channel_set_matches_across_layers": (
            set(failure_channel_map) == complete_edge_set
            and set(asymmetric_channel_map) == complete_edge_set
            and set(a2_channel_map) == complete_edge_set
        ),
    }

    return {
        "status": "ok",
        "s12_grade_only_model": {
            "total_nonzero_dimension": int(sum(grade_split.values())),
            "grade_split": [int(grade_split[0]), int(grade_split[1]), int(grade_split[2])],
            "jacobi_failure_count": int(len(failures)),
            "jacobi_failures": [row.to_dict() for row in failures],
            "nonuniform_grade_failures_are_exactly_six": int(len(failures)) == 6,
            "oriented_generation_graph_complete": set(failure_channel_map) == complete_edge_set,
        },
        "sl27_z3_bridge": {
            "match_count": int(len(sl27_matches)),
            "unique_partition": [int(sl27_match["a"]), int(sl27_match["b"]), int(sl27_match["c"])],
            "n": int(sl27_match["n"]),
            "a_family_rank": int(sl27_match["a_family_rank"]),
            "grade0": int(sl27_match["g0"]),
            "grade1": int(sl27_match["g1"]),
            "grade2": int(sl27_match["g2"]),
            "total_dimension": int(sl27_match["total"]),
            "bridge_claim_holds": (
                sl27_match["a"] == 9
                and sl27_match["b"] == 9
                and sl27_match["c"] == 9
                and sl27_match["total"] == 728
            ),
        },
        "l6_asymmetric_a2_bridge": {
            "democratic_pattern": list(build_l6_exceptional_gauge_return_certificate().democratic_pattern),
            "asymmetric_patterns": [row.to_dict() for row in asymmetric_patterns],
            "asymmetric_patterns_are_all_123_multiplicity_permutations": all(
                sorted(row.generation_multiplicities) == [1, 2, 3] for row in asymmetric_patterns
            ),
            "a2_mode_indices": [int(channel.mode_index) for channel in a2_channels],
            "a2_generation_channels": [
                {
                    "mode_index": int(channel.mode_index),
                    "source_generation": int(channel.source_generation),
                    "target_generation": int(channel.target_generation),
                }
                for channel in a2_channels
            ],
            "current_linearized_l6_bridge_activates_only_cartan_modes": (
                l6_chiral.a2_coefficients_all_zero
                and l6_chiral.active_a2_mode_indices == ()
            ),
        },
        "shared_channel_dictionary": {
            **transport_group_bridge,
            "crosswalk": [row.to_dict() for row in crosswalk],
        },
        "monster_heisenberg_closure": {
            "available": bool(monster.get("available") is True),
            "monster_class": str(monster["monster"]["class"]),
            "extraspecial_order": int(monster["monster"]["extraspecial_order"]),
            "heisenberg_irrep_dimension": int(monster["heisenberg"]["irrep_dim"]),
            "golay_codewords": int(monster["golay"]["n_codewords"]),
            "golay_nonzero_codewords": int(monster["golay"]["n_nonzero"]),
            "sl27_traceless_dimension": int(monster["sl27"]["traceless_dim"]),
            "two_suz_sp12_dimension": int(monster["2suz_sp12_embedding"]["dim"]),
            "golay_is_lagrangian": bool(
                monster["golay_lagrangian"]["systematic_generator"]
                and monster["golay_lagrangian"]["A_symmetric"]
                and monster["golay_lagrangian"]["symplectic_isotropic_all_pairs"]
            ),
            "phase_resolution_mechanism_exact": bool(
                monster.get("available") is True
                and int(monster["heisenberg"]["irrep_dim"]) == 729
                and int(monster["golay"]["n_codewords"]) == 729
                and int(monster["golay"]["n_nonzero"]) == 728
                and int(monster["sl27"]["traceless_dim"]) == 728
                and int(monster["2suz_sp12_embedding"]["dim"]) == 12
            ),
        },
        "bridge_verdict": (
            "The old s12 scripts now connect cleanly to the exact transport/Lie-tower "
            "stack. The grade-only s12 model has exactly six Jacobi-failure triples, "
            "and those six failures canonically encode the complete oriented "
            "three-generation graph. The corrected l6 exceptional return has exactly "
            "six asymmetric sextuple sectors, and those sectors encode the same six "
            "oriented channels. The exact l6 A2 operator slice then realizes those "
            "same six ordered generation transfers on the 48-spinor space. So the "
            "six-channel A2 package in the live Lie tower is the exact finite shadow "
            "of the six-channel obstruction already visible in the old s12 model. "
            "The sl_27 block-cyclic 9+9+9 bridge and the Monster 3B / Heisenberg / "
            "Golay closure show what resolves that obstruction: not more grade-only "
            "counting, but an honest phase/cocycle mechanism. The remaining open "
            "problem is dynamical selection: the exact A2 channels are present, but "
            "the current linearized l6 Yukawa bridge still selects only the Cartan slice."
        ),
    }


def write_summary(path: Path = DEFAULT_OUTPUT_PATH) -> Path:
    path.write_text(
        json.dumps(build_lie_tower_s12_bridge_summary(), indent=2),
        encoding="utf-8",
    )
    return path


def main() -> None:
    path = write_summary()
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
