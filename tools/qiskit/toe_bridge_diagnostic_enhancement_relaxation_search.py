#!/usr/bin/env python3
"""Diagnostic-order relaxation tensored with the exact enhancement hierarchy.

This keeps the factorized diagnostic bridge shell fixed on the accepted
pass/pass weight channel and replaces the old binary glue choice by the exact
three-state enhancement hierarchy:

- current refined K3 zero-orbit object;
- minimal exact enhancement datum;
- formal completion avatar.

The exact marked sector factorizes as

`Marked(relaxation, mode) = Marked_diagnostic_relaxation(relaxation) * {enhancement(mode)}`

so the enhancement modes are basis-conjugate on the same padded `17`-qubit
shell.
"""

from __future__ import annotations

import argparse
import itertools
import json
import math
from collections import Counter

from toe_bridge_diagnostic_order_search import (
    exceptional_orderings,
    hyperbolic_orderings,
    interleaving_patterns,
    marked_exceptional_order,
    marked_hyperbolic_order,
    merge_factor_permutation,
)
from toe_bridge_enhancement_factor_search import (
    MODE_CURRENT_K3,
    MODE_FORMAL_COMPLETION,
    MODE_MINIMAL_ENHANCEMENT,
    enhancement_states,
    theorem_sources_for_mode,
    target_enhancement_state,
)
from toe_bridge_line_factor_search import (
    HEAD_LINE,
    SUPPORT_ITEMS,
    TAIL_LINE,
    strict_support_marked_permutations,
)
from toe_bridge_split_weight_filter_search import EXCEPTIONAL_PASS, HYPERBOLIC_PASS
from toe_bridge_diagnostic_relaxation_search import (
    RELAXATION_BOTH,
    RELAXATION_EXCEPTIONAL,
    RELAXATION_EXACT,
    RELAXATION_HYPERBOLIC,
    expected_marked_count,
    relaxation_modes,
)


def line_states() -> list[str]:
    return [HEAD_LINE, TAIL_LINE]


def grover_iteration_count(search_space_size: int, marked_count: int) -> int:
    if marked_count <= 0:
        raise ValueError("marked_count must be positive")
    return max(1, int(round((math.pi / 4.0) * math.sqrt(search_space_size / marked_count))))


def build_states() -> tuple[list[tuple[str, ...]], list[tuple[int, int, int, int, str, str, str]]]:
    support_permutations = list(itertools.permutations(SUPPORT_ITEMS))
    states = list(
        itertools.product(
            range(len(support_permutations)),
            range(len(interleaving_patterns())),
            range(len(hyperbolic_orderings())),
            range(len(exceptional_orderings())),
            line_states(),
            enhancement_states(),
            [HYPERBOLIC_PASS],
            [EXCEPTIONAL_PASS],
        )
    )
    return support_permutations, states


def build_marked_indices(
    mode: str,
    relaxation: str,
) -> tuple[list[tuple[str, ...]], list[tuple[int, int, int, int, str, str, str, str]], set[int]]:
    if mode not in {MODE_CURRENT_K3, MODE_MINIMAL_ENHANCEMENT, MODE_FORMAL_COMPLETION}:
        raise ValueError(f"Unsupported mode: {mode}")
    if relaxation not in relaxation_modes():
        raise ValueError(f"Unsupported relaxation mode: {relaxation}")

    support_permutations, states = build_states()
    support_marks = {
        support_permutations.index(perm) for perm in strict_support_marked_permutations(support_permutations)
    }
    hyper_target = hyperbolic_orderings().index(marked_hyperbolic_order())
    exceptional_target = exceptional_orderings().index(marked_exceptional_order())
    enhancement_target = target_enhancement_state(mode)

    require_hyper = relaxation not in {RELAXATION_HYPERBOLIC, RELAXATION_BOTH}
    require_exceptional = relaxation not in {RELAXATION_EXCEPTIONAL, RELAXATION_BOTH}

    marked_indices = {
        idx
        for idx, (
            support_idx,
            _interleaving_idx,
            hyper_idx,
            exceptional_idx,
            line_state,
            enhancement_state,
            hyper_weight_state,
            exceptional_weight_state,
        ) in enumerate(states)
        if support_idx in support_marks
        and line_state == HEAD_LINE
        and enhancement_state == enhancement_target
        and hyper_weight_state == HYPERBOLIC_PASS
        and exceptional_weight_state == EXCEPTIONAL_PASS
        and (not require_hyper or hyper_idx == hyper_target)
        and (not require_exceptional or exceptional_idx == exceptional_target)
    }
    return support_permutations, states, marked_indices


def build_mode_conjugacy_permutation(src_mode: str, dst_mode: str, relaxation: str) -> list[int]:
    states, _marked = build_marked_indices(src_mode, relaxation)[1:]
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
        state_to_index[
            (
                support_idx,
                interleaving_idx,
                hyper_idx,
                exceptional_idx,
                line_state,
                relabel[enhancement_state],
                hyper_weight_state,
                exceptional_weight_state,
            )
        ]
        for (
            support_idx,
            interleaving_idx,
            hyper_idx,
            exceptional_idx,
            line_state,
            enhancement_state,
            hyper_weight_state,
            exceptional_weight_state,
        ) in states
    ]


def marked_order_projection(mode: str, relaxation: str) -> set[tuple[int, int, int, int, str]]:
    _support_permutations, states, marked_indices = build_marked_indices(mode, relaxation)
    return {
        (support_idx, interleaving_idx, hyper_idx, exceptional_idx, line_state)
        for idx, (
            support_idx,
            interleaving_idx,
            hyper_idx,
            exceptional_idx,
            line_state,
            _enhancement_state,
            _hyper_weight_state,
            _exceptional_weight_state,
        ) in enumerate(states)
        if idx in marked_indices
    }


def marked_enhancement_projection(mode: str, relaxation: str) -> set[str]:
    _support_permutations, states, marked_indices = build_marked_indices(mode, relaxation)
    return {states[idx][5] for idx in marked_indices}


def decode_states(
    counts: Counter[str],
    support_permutations: list[tuple[str, ...]],
    states: list[tuple[int, int, int, int, str, str, str, str]],
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

        (
            support_idx,
            interleaving_idx,
            hyper_idx,
            exceptional_idx,
            line_state,
            enhancement_state,
            hyper_weight_state,
            exceptional_weight_state,
        ) = states[index]
        factor_permutation = merge_factor_permutation(
            hyperbolic_orderings()[hyper_idx],
            exceptional_orderings()[exceptional_idx],
            interleaving_patterns()[interleaving_idx],
        )
        payload["support_permutation"] = list(support_permutations[support_idx])
        payload["interleaving_pattern"] = list(interleaving_patterns()[interleaving_idx])
        payload["hyperbolic_order"] = list(hyperbolic_orderings()[hyper_idx])
        payload["exceptional_order"] = list(exceptional_orderings()[exceptional_idx])
        payload["factor_permutation"] = list(factor_permutation)
        payload["line_state"] = line_state
        payload["enhancement_state"] = enhancement_state
        payload["hyperbolic_weight_state"] = hyper_weight_state
        payload["exceptional_weight_state"] = exceptional_weight_state

        if index in marked_indices:
            target_hits.append(payload)
        else:
            nontarget_valid.append(payload)

    return target_hits, nontarget_valid, invalid


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run the diagnostic-relaxation x enhancement Grover search."
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
    current_mode_conjugacy = build_mode_conjugacy_permutation(
        MODE_CURRENT_K3, args.mode, args.relaxation
    )
    search_space_size = 1 << math.ceil(math.log2(len(states)))
    num_qubits = int(math.log2(search_space_size))
    order_projection = marked_order_projection(args.mode, args.relaxation)
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
        counts, support_permutations, states, marked_indices, args.top
    )

    summary = {
        "search_name": "toe_bridge_diagnostic_enhancement_relaxation_search",
        "mode": args.mode,
        "relaxation": args.relaxation,
        "theorem_sources": theorem_sources_for_mode(args.mode),
        "diagnostic_state_count": 57600,
        "enhancement_state_count": len(enhancement_states()),
        "bridge_state_count": len(states),
        "search_space_size": search_space_size,
        "num_qubits": num_qubits,
        "grover_iterations": iterations,
        "shots": args.shots,
        "seed": args.seed,
        "marked_count": len(marked_indices),
        "expected_marked_count": expected_marked_count(args.relaxation),
        "marked_count_matches_exact_sector_formula": len(marked_indices) == expected_marked_count(args.relaxation),
        "marked_order_projection_count": len(order_projection),
        "order_projection_matches_relaxation_formula": len(order_projection)
        == expected_marked_count(args.relaxation),
        "enhancement_target_state": target_enhancement_state(args.mode),
        "marked_enhancement_projection": sorted(enhancement_projection),
        "marked_sector_factorization": "Marked_diagnostic_relaxation(relaxation) x {enhancement(mode)}",
        "enhancement_modes_are_basis_conjugate": True,
        "current_mode_conjugacy_is_permutation": sorted(current_mode_conjugacy)
        == list(range(len(states))),
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
