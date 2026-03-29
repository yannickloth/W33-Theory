#!/usr/bin/env python3
"""Grover-style search for support/enhancement decoupling.

This keeps the factorized support shell and the three-state enhancement wall on
one discrete space:

`360 = 120 support states * 3 enhancement states`

and tests whether support selectivity is unchanged across the exact external
enhancement hierarchy:

- current refined K3 zero-orbit object;
- minimal exact enhancement datum;
- formal completion avatar.

The exact marked sector always factorizes as

`Marked(relaxation, mode) = Marked_support(relaxation) * {enhancement(mode)}`

so the three enhancement modes are basis-permutation conjugates of one another
on the same padded `9`-qubit shell.
"""

from __future__ import annotations

import argparse
import itertools
import json
import math
from collections import Counter

from toe_bridge_enhancement_factor_search import (
    MODE_CURRENT_K3,
    MODE_FORMAL_COMPLETION,
    MODE_MINIMAL_ENHANCEMENT,
    enhancement_states,
    theorem_sources_for_mode,
    target_enhancement_state,
)
from toe_support_diagnostic_relaxation_search import (
    RELAXATION_BOTH,
    RELAXATION_CORE_ORDER,
    RELAXATION_EXACT,
    RELAXATION_INTERLEAVING,
    build_marked_indices as build_support_marked_indices,
    expected_marked_count as expected_support_marked_count,
    relaxation_modes,
)
from toe_support_diagnostic_search import (
    build_support_states,
    local_context_orderings,
    merge_support_permutation,
    support_core_orderings,
    support_interleavings,
)


def grover_iteration_count(search_space_size: int, marked_count: int) -> int:
    if marked_count <= 0:
        raise ValueError("marked_count must be positive")
    return max(1, int(round((math.pi / 4.0) * math.sqrt(search_space_size / marked_count))))


def build_states() -> list[tuple[int, str]]:
    return list(itertools.product(range(len(build_support_states())), enhancement_states()))


def expected_marked_count(relaxation: str) -> int:
    return expected_support_marked_count(relaxation)


def build_marked_indices(mode: str, relaxation: str) -> tuple[list[tuple[int, str]], set[int]]:
    if mode not in {MODE_CURRENT_K3, MODE_MINIMAL_ENHANCEMENT, MODE_FORMAL_COMPLETION}:
        raise ValueError(f"Unsupported mode: {mode}")
    if relaxation not in relaxation_modes():
        raise ValueError(f"Unsupported relaxation mode: {relaxation}")

    support_states, support_marked = build_support_marked_indices(relaxation)
    states = list(itertools.product(range(len(support_states)), enhancement_states()))
    enhancement_target = target_enhancement_state(mode)

    marked = {
        idx
        for idx, (support_idx, enhancement_state) in enumerate(states)
        if support_idx in support_marked and enhancement_state == enhancement_target
    }
    return states, marked


def build_mode_conjugacy_permutation(src_mode: str, dst_mode: str, relaxation: str) -> list[int]:
    """Return the exact basis permutation carrying one mode's marked set to another."""

    states, _ = build_marked_indices(src_mode, relaxation)
    state_to_index = {state: idx for idx, state in enumerate(states)}
    labels = enhancement_states()

    src_target = target_enhancement_state(src_mode)
    dst_target = target_enhancement_state(dst_mode)
    shift = labels.index(dst_target) - labels.index(src_target)
    relabel = {
        label: labels[(labels.index(label) + shift) % len(labels)]
        for label in labels
    }

    return [
        state_to_index[(support_idx, relabel[enhancement_state])]
        for support_idx, enhancement_state in states
    ]


def marked_support_projection(mode: str, relaxation: str) -> set[int]:
    states, marked_indices = build_marked_indices(mode, relaxation)
    return {states[idx][0] for idx in marked_indices}


def marked_enhancement_projection(mode: str, relaxation: str) -> set[str]:
    states, marked_indices = build_marked_indices(mode, relaxation)
    return {states[idx][1] for idx in marked_indices}


def decode_support_state_payload(support_idx: int) -> dict[str, object]:
    states = build_support_states()
    interleaving_idx, core_idx, local_idx = states[support_idx]
    interleaving = support_interleavings()[interleaving_idx]
    core_order = support_core_orderings()[core_idx]
    local_order = local_context_orderings()[local_idx]
    return {
        "interleaving": list(interleaving),
        "core_order": list(core_order),
        "local_order": list(local_order),
        "support_permutation": list(merge_support_permutation(interleaving, core_order, local_order)),
    }


def decode_states(
    counts: Counter[str],
    states: list[tuple[int, str]],
    relaxation: str,
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

        support_idx, enhancement_state = states[index]
        payload["enhancement_state"] = enhancement_state
        payload["support_state"] = decode_support_state_payload(support_idx)

        if index in marked_indices:
            target_hits.append(payload)
        else:
            nontarget_valid.append(payload)

    return target_hits, nontarget_valid, invalid


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the support/enhancement decoupling Grover search.")
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
    states, marked_indices = build_marked_indices(args.mode, args.relaxation)
    current_mode_conjugacy = build_mode_conjugacy_permutation(
        MODE_CURRENT_K3, args.mode, args.relaxation
    )
    search_space_size = 1 << math.ceil(math.log2(len(states)))
    num_qubits = int(math.log2(search_space_size))
    support_projection = marked_support_projection(args.mode, args.relaxation)
    enhancement_projection = marked_enhancement_projection(args.mode, args.relaxation)
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
        counts, states, args.relaxation, marked_indices, args.top
    )

    summary = {
        "search_name": "toe_support_enhancement_relaxation_search",
        "mode": args.mode,
        "relaxation": args.relaxation,
        "theorem_sources": theorem_sources_for_mode(args.mode)
        + [
            "exploration/w33_e13_a4_support_stratification_bridge.py",
            "exploration/w33_yukawa_transport_coupling_hierarchy_bridge.py",
        ],
        "support_state_count": 120,
        "enhancement_state_count": len(enhancement_states()),
        "bridge_state_count": len(states),
        "search_space_size": search_space_size,
        "num_qubits": num_qubits,
        "grover_iterations": iterations,
        "shots": args.shots,
        "seed": args.seed,
        "marked_count": len(marked_indices),
        "enhancement_target_state": target_enhancement_state(args.mode),
        "support_projection_count": len(support_projection),
        "support_projection_matches_support_formula": len(support_projection)
        == expected_marked_count(args.relaxation),
        "marked_enhancement_projection": sorted(enhancement_projection),
        "enhancement_mode_is_pure_relabeling_of_support_shell": enhancement_projection
        == {target_enhancement_state(args.mode)},
        "marked_sector_factorization": "Marked_support(relaxation) x {enhancement(mode)}",
        "enhancement_modes_are_basis_conjugate": True,
        "current_mode_conjugacy_is_permutation": sorted(current_mode_conjugacy) == list(range(len(states))),
        "expected_marked_count": expected_marked_count(args.relaxation),
        "marked_count_matches_exact_sector_formula": len(marked_indices) == expected_marked_count(args.relaxation),
        "top_counts": normalize_counts(counts, args.shots)[: args.top],
        "decoded_target_hits": decoded_target,
        "decoded_nontarget_valid_hits": decoded_nontarget_valid,
        "decoded_invalid_hits": decoded_invalid,
        "target_hit_count": sum(
            count for bitstring, count in counts.items() if int(bitstring, 2) in marked_indices
        ),
        "target_hit_probability": sum(
            count for bitstring, count in counts.items() if int(bitstring, 2) in marked_indices
        ) / args.shots,
    }

    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
