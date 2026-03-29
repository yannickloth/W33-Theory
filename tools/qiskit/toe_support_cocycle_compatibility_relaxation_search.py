#!/usr/bin/env python3
"""Support-relaxation shell tensored with the cocycle-compatibility wall.

This is the stronger replacement for the old support-enhancement family.
Instead of adjoining a free 3-label enhancement axis, it adjoins the exact
6-state cocycle-realization compatibility wall and keeps only either:

- all admissible wall states, or
- only the live nonzero-compatible wall states.

Because the support shell carries no glue degree of freedom, the marked sector
factorizes exactly:

`Marked_support(relaxation) x Compatible_wall(focus)`
"""

from __future__ import annotations

import argparse
import itertools
import json
import math
from collections import Counter
from pathlib import Path
import sys

from toe_support_diagnostic_relaxation_search import (
    RELAXATION_BOTH,
    RELAXATION_CORE_ORDER,
    RELAXATION_EXACT,
    RELAXATION_INTERLEAVING,
    build_marked_indices as build_support_marked_indices,
    expected_marked_count as expected_support_marked_count,
    relaxation_modes,
)
from toe_support_enhancement_relaxation_search import (
    decode_support_state_payload,
)


ROOT = Path(__file__).resolve().parents[2]
EXPLORATION = ROOT / "exploration"
if str(EXPLORATION) not in sys.path:
    sys.path.insert(0, str(EXPLORATION))

from w33_cocycle_realization_compatibility_bridge import (  # noqa: E402
    admissible_wall_states,
    nonzero_admissible_wall_states,
)


FOCUS_ALL = "all-compatible"
FOCUS_NONZERO = "nonzero-compatible"


def focus_modes() -> list[str]:
    return [FOCUS_ALL, FOCUS_NONZERO]


def compatible_wall_states(focus: str) -> list[tuple[str, str]]:
    if focus == FOCUS_ALL:
        return admissible_wall_states()
    if focus == FOCUS_NONZERO:
        return nonzero_admissible_wall_states()
    raise ValueError(f"Unsupported focus mode: {focus}")


def grover_iteration_count(search_space_size: int, marked_count: int) -> int:
    if marked_count <= 0:
        raise ValueError("marked_count must be positive")
    return max(1, int(round((math.pi / 4.0) * math.sqrt(search_space_size / marked_count))))


def wall_states() -> list[tuple[str, str]]:
    return admissible_wall_states() + [
        ("current_refined_k3_object", "unique_nonzero_orbit"),
        ("slot_replacement_datum", "zero_orbit"),
        ("formal_completion_object", "zero_orbit"),
    ]


def build_bridge_states() -> list[tuple[int, tuple[str, str]]]:
    support_states = build_support_marked_indices(RELAXATION_EXACT)[0]
    return list(itertools.product(range(len(support_states)), wall_states()))


def expected_marked_count(focus: str, relaxation: str) -> int:
    return expected_support_marked_count(relaxation) * len(compatible_wall_states(focus))


def build_marked_indices(
    focus: str,
    relaxation: str,
) -> tuple[list[tuple[int, int, int]], list[tuple[int, tuple[str, str]]], set[int]]:
    if focus not in focus_modes():
        raise ValueError(f"Unsupported focus mode: {focus}")
    if relaxation not in relaxation_modes():
        raise ValueError(f"Unsupported relaxation mode: {relaxation}")

    support_states, support_marked = build_support_marked_indices(relaxation)
    states = list(itertools.product(range(len(support_states)), wall_states()))
    wall_targets = set(compatible_wall_states(focus))
    marked = {
        idx
        for idx, (support_idx, wall_state) in enumerate(states)
        if support_idx in support_marked and wall_state in wall_targets
    }
    return support_states, states, marked


def decode_states(
    counts: Counter[str],
    support_states: list[tuple[int, int, int]],
    states: list[tuple[int, tuple[str, str]]],
    marked_indices: set[int],
    top: int,
) -> tuple[list[dict[str, object]], list[dict[str, object]], list[dict[str, object]]]:
    target_hits: list[dict[str, object]] = []
    nontarget_valid: list[dict[str, object]] = []
    invalid: list[dict[str, object]] = []

    for bitstring, count in counts.most_common(top):
        index = int(bitstring, 2)
        payload: dict[str, object] = {"bitstring": bitstring, "index": index, "count": count}
        if index >= len(states):
            invalid.append(payload)
            continue

        support_idx, wall_state = states[index]
        payload["support_state"] = decode_support_state_payload(support_idx)
        payload["wall_layer"] = wall_state[0]
        payload["orbit_state"] = wall_state[1]

        if index in marked_indices:
            target_hits.append(payload)
        else:
            nontarget_valid.append(payload)

    return target_hits, nontarget_valid, invalid


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run the support-relaxation x cocycle-compatibility Grover search."
    )
    parser.add_argument("--focus", choices=focus_modes(), default=FOCUS_NONZERO)
    parser.add_argument("--relaxation", choices=relaxation_modes(), default=RELAXATION_EXACT)
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
    support_states, states, marked_indices = build_marked_indices(args.focus, args.relaxation)
    search_space_size = 1 << math.ceil(math.log2(len(states)))
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
        counts, support_states, states, marked_indices, args.top
    )

    summary = {
        "search_name": "toe_support_cocycle_compatibility_relaxation_search",
        "focus": args.focus,
        "relaxation": args.relaxation,
        "theorem_surface": "factorized support-relaxation shell tensored with the exact cocycle-compatibility wall",
        "support_state_count": len(support_states),
        "wall_state_count": len(wall_states()),
        "bridge_state_count": len(states),
        "search_space_size": search_space_size,
        "num_qubits": num_qubits,
        "grover_iterations": iterations,
        "shots": args.shots,
        "seed": args.seed,
        "compatible_wall_states": [list(state) for state in compatible_wall_states(args.focus)],
        "marked_count": len(marked_indices),
        "expected_marked_count": expected_marked_count(args.focus, args.relaxation),
        "marked_count_matches_exact_factorization": len(marked_indices)
        == expected_marked_count(args.focus, args.relaxation),
        "marked_sector_factorization": "Marked_support(relaxation) x Compatible_wall(focus)",
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
