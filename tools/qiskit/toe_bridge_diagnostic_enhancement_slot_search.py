#!/usr/bin/env python3
"""Diagnostic enhancement shell refined by the exact cocycle-slot wall.

This keeps the corrected diagnostic-order relaxation shell and the exact
three-state enhancement hierarchy, then adjoins the cocycle-slot status itself:

- ``zero_by_splitness``
- ``unique_nonzero_orbit_in_existing_slot``

That new factor is not redundant with the enhancement hierarchy. The exact
compatibility law is:

- ``current_k3_zero_orbit -> zero_by_splitness``
- ``minimal_external_enhancement -> unique_nonzero_orbit_in_existing_slot``
- ``formal_completion_avatar -> unique_nonzero_orbit_in_existing_slot``

So the current K3 state is separated from both completion-side states by slot
status, while the minimal and formal states share the same nonzero slot.
"""

from __future__ import annotations

import argparse
import itertools
import json
import math
from collections import Counter

from toe_bridge_diagnostic_enhancement_relaxation_search import (
    build_marked_indices as build_base_marked_indices,
    build_states as build_base_states,
    decode_states as decode_base_states,
)
from toe_bridge_diagnostic_relaxation_search import (
    RELAXATION_BOTH,
    RELAXATION_EXCEPTIONAL,
    RELAXATION_EXACT,
    RELAXATION_HYPERBOLIC,
    expected_marked_count,
    relaxation_modes,
)
from toe_bridge_enhancement_factor_search import (
    CURRENT_K3_ZERO_ORBIT,
    FORMAL_COMPLETION_AVATAR,
    MINIMAL_EXTERNAL_ENHANCEMENT,
    MODE_CURRENT_K3,
    MODE_FORMAL_COMPLETION,
    MODE_MINIMAL_ENHANCEMENT,
    theorem_sources_for_mode,
    target_enhancement_state,
)


ZERO_SLOT = "zero_by_splitness"
UNIQUE_NONZERO_SLOT = "unique_nonzero_orbit_in_existing_slot"


def slot_states() -> list[str]:
    return [ZERO_SLOT, UNIQUE_NONZERO_SLOT]


def target_slot_state(mode: str) -> str:
    mapping = {
        MODE_CURRENT_K3: ZERO_SLOT,
        MODE_MINIMAL_ENHANCEMENT: UNIQUE_NONZERO_SLOT,
        MODE_FORMAL_COMPLETION: UNIQUE_NONZERO_SLOT,
    }
    try:
        return mapping[mode]
    except KeyError as exc:
        raise ValueError(f"Unsupported mode: {mode}") from exc


def compatible_enhancement_slot_pairs() -> list[tuple[str, str]]:
    return [
        (CURRENT_K3_ZERO_ORBIT, ZERO_SLOT),
        (MINIMAL_EXTERNAL_ENHANCEMENT, UNIQUE_NONZERO_SLOT),
        (FORMAL_COMPLETION_AVATAR, UNIQUE_NONZERO_SLOT),
    ]


def grover_iteration_count(search_space_size: int, marked_count: int) -> int:
    if marked_count <= 0:
        raise ValueError("marked_count must be positive")
    return max(1, int(round((math.pi / 4.0) * math.sqrt(search_space_size / marked_count))))


def build_states() -> tuple[list[tuple[str, ...]], list[tuple[int, str]]]:
    support_permutations, base_states = build_base_states()
    states = list(itertools.product(range(len(base_states)), slot_states()))
    return support_permutations, states


def build_marked_indices(
    mode: str,
    relaxation: str,
) -> tuple[list[tuple[str, ...]], list[tuple[int, str]], set[int]]:
    if relaxation not in relaxation_modes():
        raise ValueError(f"Unsupported relaxation mode: {relaxation}")

    support_permutations, base_states, base_marked = build_base_marked_indices(mode, relaxation)
    states = list(itertools.product(range(len(base_states)), slot_states()))
    slot_target = target_slot_state(mode)

    marked_indices = {
        idx
        for idx, (base_idx, slot_state) in enumerate(states)
        if base_idx in base_marked and slot_state == slot_target
    }
    return support_permutations, states, marked_indices


def marked_pair_projection(mode: str, relaxation: str) -> set[tuple[str, str]]:
    _support_permutations, states, marked_indices = build_marked_indices(mode, relaxation)
    _support_permutations, base_states = build_base_states()
    projection = set()
    for idx in marked_indices:
        base_idx, slot_state = states[idx]
        enhancement_state = base_states[base_idx][5]
        projection.add((enhancement_state, slot_state))
    return projection


def marked_slot_projection(mode: str, relaxation: str) -> set[str]:
    return {slot_state for _enhancement_state, slot_state in marked_pair_projection(mode, relaxation)}


def decode_states(
    counts: Counter[str],
    support_permutations: list[tuple[str, ...]],
    states: list[tuple[int, str]],
    marked_indices: set[int],
    top: int,
) -> tuple[list[dict[str, object]], list[dict[str, object]], list[dict[str, object]]]:
    _support_permutations, base_states = build_base_states()

    target_hits: list[dict[str, object]] = []
    nontarget_valid: list[dict[str, object]] = []
    invalid: list[dict[str, object]] = []

    for bitstring, count in counts.most_common(top):
        index = int(bitstring, 2)
        payload: dict[str, object] = {"bitstring": bitstring, "index": index, "count": count}
        if index >= len(states):
            invalid.append(payload)
            continue

        base_idx, slot_state = states[index]
        base_target, base_nontarget, _base_invalid = decode_base_states(
            Counter({format(base_idx, "b"): count}),
            support_permutations,
            base_states,
            {base_idx},
            top=1,
        )
        base_payload = (base_target or base_nontarget)[0]
        base_payload.pop("bitstring", None)
        base_payload.pop("index", None)
        base_payload.pop("count", None)
        payload.update(base_payload)
        payload["slot_state"] = slot_state

        if index in marked_indices:
            target_hits.append(payload)
        else:
            nontarget_valid.append(payload)

    return target_hits, nontarget_valid, invalid


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run the diagnostic-enhancement shell refined by the exact cocycle-slot wall."
    )
    parser.add_argument(
        "--mode",
        choices=[MODE_CURRENT_K3, MODE_MINIMAL_ENHANCEMENT, MODE_FORMAL_COMPLETION],
        default=MODE_FORMAL_COMPLETION,
    )
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
    support_permutations, states, marked_indices = build_marked_indices(args.mode, args.relaxation)
    _support_permutations, base_states = build_base_states()
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
        counts, support_permutations, states, marked_indices, args.top
    )

    marked_pair = next(iter(marked_pair_projection(args.mode, args.relaxation)))
    summary = {
        "search_name": "toe_bridge_diagnostic_enhancement_slot_search",
        "mode": args.mode,
        "relaxation": args.relaxation,
        "theorem_sources": theorem_sources_for_mode(args.mode)
        + [
            "exploration/w33_enhancement_slot_hierarchy_bridge.py",
            "exploration/w33_transport_single_glue_slot_bridge.py",
            "exploration/w33_refined_k3_zero_orbit_bridge.py",
        ],
        "diagnostic_enhancement_state_count": len(base_states),
        "slot_state_count": len(slot_states()),
        "bridge_state_count": len(states),
        "search_space_size": search_space_size,
        "num_qubits": num_qubits,
        "grover_iterations": iterations,
        "shots": args.shots,
        "seed": args.seed,
        "marked_count": len(marked_indices),
        "expected_marked_count": expected_marked_count(args.relaxation),
        "marked_count_matches_exact_sector_formula": len(marked_indices) == expected_marked_count(args.relaxation),
        "compatible_enhancement_slot_pairs": [list(pair) for pair in compatible_enhancement_slot_pairs()],
        "target_enhancement_state": target_enhancement_state(args.mode),
        "target_slot_state": target_slot_state(args.mode),
        "marked_pair_projection": [list(marked_pair)],
        "marked_slot_projection": sorted(marked_slot_projection(args.mode, args.relaxation)),
        "exact_mode_relation": "Marked_diagnostic_relaxation(relaxation) x {(enhancement(mode), slot(mode))}",
        "current_mode_uses_zero_slot_while_completion_modes_use_nonzero_slot": (
            target_slot_state(MODE_CURRENT_K3) == ZERO_SLOT
            and target_slot_state(MODE_MINIMAL_ENHANCEMENT) == UNIQUE_NONZERO_SLOT
            and target_slot_state(MODE_FORMAL_COMPLETION) == UNIQUE_NONZERO_SLOT
        ),
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
