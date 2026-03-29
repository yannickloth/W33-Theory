#!/usr/bin/env python3
"""Grover-style search on the exact cocycle-realization compatibility wall.

This replaces the old free 3-label enhancement axis by the exact 6-state wall
factor

`wall_layer x orbit_state`

with:

- wall layers:
  `current_refined_k3_object`, `slot_replacement_datum`,
  `formal_completion_object`
- orbit states:
  `zero_orbit`, `unique_nonzero_orbit`

Only 3 wall states are admissible, and only 2 of those carry the unique
nonzero orbit. Tensoring that factor with the corrected diagnostic shell gives

`57600 x 6 = 345600`

states on `19` qubits.
"""

from __future__ import annotations

import argparse
import itertools
import json
import math
from collections import Counter
from pathlib import Path
import sys

from toe_bridge_diagnostic_order_search import (
    exceptional_orderings,
    hyperbolic_orderings,
    interleaving_patterns,
    marked_exceptional_order,
    marked_hyperbolic_order,
    merge_factor_permutation,
)
from toe_bridge_diagnostic_relaxation_search import build_relaxation_states
from toe_bridge_line_factor_search import HEAD_LINE, NONZERO_GLUE, ZERO_GLUE


ROOT = Path(__file__).resolve().parents[2]
EXPLORATION = ROOT / "exploration"
if str(EXPLORATION) not in sys.path:
    sys.path.insert(0, str(EXPLORATION))

from w33_cocycle_realization_compatibility_bridge import (  # noqa: E402
    CURRENT_REFINED_K3_OBJECT,
    FORMAL_COMPLETION_OBJECT,
    SLOT_REPLACEMENT_DATUM,
    UNIQUE_NONZERO_ORBIT,
    ZERO_ORBIT,
    admissible_wall_states,
    nonzero_admissible_wall_states,
    wall_states,
)


FOCUS_ALL = "all-compatible"
FOCUS_NONZERO = "nonzero-compatible"


def focus_modes() -> list[str]:
    return [FOCUS_ALL, FOCUS_NONZERO]


def grover_iteration_count(search_space_size: int, marked_count: int) -> int:
    if marked_count <= 0:
        raise ValueError("marked_count must be positive")
    return max(1, int(round((math.pi / 4.0) * math.sqrt(search_space_size / marked_count))))


def compatible_wall_states(focus: str) -> list[tuple[str, str]]:
    if focus == FOCUS_ALL:
        return admissible_wall_states()
    if focus == FOCUS_NONZERO:
        return nonzero_admissible_wall_states()
    raise ValueError(f"Unsupported focus mode: {focus}")


def build_states() -> tuple[
    list[tuple[str, ...]],
    list[tuple[int, int, int, int, str, str, str, str]],
    list[tuple[str, str]],
    list[tuple[int, tuple[str, str]]],
]:
    support_permutations, diagnostic_states = build_relaxation_states()
    walls = wall_states()
    bridge_states = list(itertools.product(range(len(diagnostic_states)), walls))
    return support_permutations, diagnostic_states, walls, bridge_states


def build_marked_indices(
    focus: str,
) -> tuple[
    list[tuple[str, ...]],
    list[tuple[int, int, int, int, str, str, str, str]],
    list[tuple[str, str]],
    list[tuple[int, tuple[str, str]]],
    set[int],
]:
    if focus not in focus_modes():
        raise ValueError(f"Unsupported focus mode: {focus}")

    support_permutations, diagnostic_states, walls, bridge_states = build_states()
    support_marks = {
        idx
        for idx, perm in enumerate(support_permutations)
        if perm[:3] == ("head_line", "u1_plane", "transport_avatar")
    }
    hyper_target = hyperbolic_orderings().index(marked_hyperbolic_order())
    exceptional_target = exceptional_orderings().index(marked_exceptional_order())
    wall_targets = set(compatible_wall_states(focus))

    marked = set()
    for idx, (diagnostic_idx, wall_state) in enumerate(bridge_states):
        (
            support_idx,
            _interleaving_idx,
            hyper_idx,
            exceptional_idx,
            glue_state,
            line_state,
            hyper_weight_state,
            exceptional_weight_state,
        ) = diagnostic_states[diagnostic_idx]

        wall_layer, orbit_state = wall_state
        glue_matches_orbit = (
            glue_state == ZERO_GLUE
            if orbit_state == ZERO_ORBIT
            else glue_state == NONZERO_GLUE
        )

        if support_idx not in support_marks:
            continue
        if hyper_idx != hyper_target or exceptional_idx != exceptional_target:
            continue
        if line_state != HEAD_LINE:
            continue
        if hyper_weight_state != "hyperbolic_dominance_pass":
            continue
        if exceptional_weight_state != "exceptional_dominance_pass":
            continue
        if not glue_matches_orbit:
            continue
        if wall_state not in wall_targets:
            continue
        marked.add(idx)

    return support_permutations, diagnostic_states, walls, bridge_states, marked


def expected_marked_count(focus: str) -> int:
    if focus == FOCUS_ALL:
        return 60
    if focus == FOCUS_NONZERO:
        return 40
    raise ValueError(f"Unsupported focus mode: {focus}")


def decode_states(
    counts: Counter[str],
    support_permutations: list[tuple[str, ...]],
    diagnostic_states: list[tuple[int, int, int, int, str, str, str, str]],
    bridge_states: list[tuple[int, tuple[str, str]]],
    marked_indices: set[int],
    top: int,
) -> tuple[list[dict[str, object]], list[dict[str, object]], list[dict[str, object]]]:
    target_hits: list[dict[str, object]] = []
    nontarget_valid: list[dict[str, object]] = []
    invalid: list[dict[str, object]] = []

    for bitstring, count in counts.most_common(top):
        index = int(bitstring, 2)
        payload: dict[str, object] = {"bitstring": bitstring, "index": index, "count": count}
        if index >= len(bridge_states):
            invalid.append(payload)
            continue

        diagnostic_idx, wall_state = bridge_states[index]
        (
            support_idx,
            interleaving_idx,
            hyper_idx,
            exceptional_idx,
            glue_state,
            line_state,
            hyper_weight_state,
            exceptional_weight_state,
        ) = diagnostic_states[diagnostic_idx]

        payload["support_permutation"] = list(support_permutations[support_idx])
        payload["factor_interleaving"] = list(interleaving_patterns()[interleaving_idx])
        payload["hyperbolic_order"] = list(hyperbolic_orderings()[hyper_idx])
        payload["exceptional_order"] = list(exceptional_orderings()[exceptional_idx])
        payload["factor_permutation"] = list(
            merge_factor_permutation(
                hyperbolic_orderings()[hyper_idx],
                exceptional_orderings()[exceptional_idx],
                interleaving_patterns()[interleaving_idx],
            )
        )
        payload["glue_state"] = glue_state
        payload["line_state"] = line_state
        payload["hyperbolic_weight_state"] = hyper_weight_state
        payload["exceptional_weight_state"] = exceptional_weight_state
        payload["wall_layer"] = wall_state[0]
        payload["orbit_state"] = wall_state[1]

        if index in marked_indices:
            target_hits.append(payload)
        else:
            nontarget_valid.append(payload)

    return target_hits, nontarget_valid, invalid


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run the cocycle-realization compatibility Grover search."
    )
    parser.add_argument("--focus", choices=focus_modes(), default=FOCUS_NONZERO)
    parser.add_argument("--shots", type=int, default=256)
    parser.add_argument("--iterations", type=int, default=None)
    parser.add_argument("--top", type=int, default=8)
    parser.add_argument("--seed", type=int, default=7)
    return parser


def main() -> None:
    from qiskit import transpile
    from qiskit_aer import AerSimulator
    from permutation_grover_search import build_grover_circuit, normalize_counts

    args = build_parser().parse_args()
    support_permutations, diagnostic_states, walls, bridge_states, marked_indices = (
        build_marked_indices(args.focus)
    )
    search_space_size = 1 << math.ceil(math.log2(len(bridge_states)))
    num_qubits = int(math.log2(search_space_size))
    iterations = (
        args.iterations
        if args.iterations is not None
        else grover_iteration_count(search_space_size, len(marked_indices))
    )

    circuit = build_grover_circuit(num_qubits, marked_indices, iterations)
    simulator = AerSimulator(seed_simulator=args.seed)
    compiled = transpile(circuit, simulator, optimization_level=1, seed_transpiler=args.seed)
    result = simulator.run(compiled, shots=args.shots, seed_simulator=args.seed).result()
    counts = Counter(result.get_counts())

    decoded_target, decoded_nontarget_valid, decoded_invalid = decode_states(
        counts,
        support_permutations,
        diagnostic_states,
        bridge_states,
        marked_indices,
        args.top,
    )

    summary = {
        "search_name": "toe_bridge_cocycle_compatibility_search",
        "focus": args.focus,
        "theorem_surface": "corrected diagnostic shell tensored with the exact 6-state cocycle-realization compatibility wall",
        "diagnostic_state_count": len(diagnostic_states),
        "wall_state_count": len(walls),
        "bridge_state_count": len(bridge_states),
        "search_space_size": search_space_size,
        "num_qubits": num_qubits,
        "grover_iterations": iterations,
        "shots": args.shots,
        "seed": args.seed,
        "compatible_wall_states": [list(state) for state in compatible_wall_states(args.focus)],
        "marked_count": len(marked_indices),
        "expected_marked_count": expected_marked_count(args.focus),
        "marked_count_matches_formula": len(marked_indices) == expected_marked_count(args.focus),
        "top_counts": normalize_counts(counts, args.shots)[: args.top],
        "decoded_target_hits": decoded_target,
        "decoded_nontarget_valid_hits": decoded_nontarget_valid,
        "decoded_invalid_hits": decoded_invalid,
        "target_hit_count": sum(
            count for bitstring, count in counts.items() if int(bitstring, 2) in marked_indices
        ),
        "target_hit_probability": sum(
            count for bitstring, count in counts.items() if int(bitstring, 2) in marked_indices
        )
        / args.shots,
    }

    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
