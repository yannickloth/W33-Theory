#!/usr/bin/env python3
"""Constraint-relaxation diagnostic on the accepted order-and-weight channel.

This keeps the factorized support/order/line/glue state space fixed on the
already-promoted split-weight pass/pass channel and relaxes theorem order
constraints one sector at a time:

- exact: enforce both hyperbolic and exceptional order theorems
- hyperbolic-order-relaxed: enforce only the exceptional order theorem
- exceptional-order-relaxed: enforce only the hyperbolic order theorem
- both-orders-relaxed: enforce neither order theorem

The interleaving sector is already free in the exact diagnostic-order oracle,
and the split-weight pass/pass sector is held fixed here, so neither appears as
an additional relaxation factor in this diagnostic.
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
    theorem_sources_for_mode,
)
from toe_bridge_line_factor_search import (
    HEAD_LINE,
    MODE_CURRENT_SHADOW,
    MODE_FORMAL_COMPLETION,
    NONZERO_GLUE,
    SUPPORT_ITEMS,
    TAIL_LINE,
    ZERO_GLUE,
    strict_support_marked_permutations,
)
from toe_bridge_split_weight_filter_search import (
    EXCEPTIONAL_PASS,
    HYPERBOLIC_PASS,
)


RELAXATION_EXACT = "exact"
RELAXATION_HYPERBOLIC = "hyperbolic-order-relaxed"
RELAXATION_EXCEPTIONAL = "exceptional-order-relaxed"
RELAXATION_BOTH = "both-orders-relaxed"


def grover_iteration_count(search_space_size: int, marked_count: int) -> int:
    if marked_count <= 0:
        raise ValueError("marked_count must be positive")
    return max(1, int(round((math.pi / 4.0) * math.sqrt(search_space_size / marked_count))))


def line_states() -> list[str]:
    return [HEAD_LINE, TAIL_LINE]


def relaxation_modes() -> list[str]:
    return [
        RELAXATION_EXACT,
        RELAXATION_HYPERBOLIC,
        RELAXATION_EXCEPTIONAL,
        RELAXATION_BOTH,
    ]


def build_relaxation_states() -> tuple[
    list[tuple[str, ...]],
    list[tuple[int, int, int, int, str, str, str, str]],
]:
    support_permutations = list(itertools.permutations(SUPPORT_ITEMS))
    diagnostic_states = list(
        itertools.product(
            range(len(support_permutations)),
            range(len(interleaving_patterns())),
            range(len(hyperbolic_orderings())),
            range(len(exceptional_orderings())),
            [ZERO_GLUE, NONZERO_GLUE],
            line_states(),
            [HYPERBOLIC_PASS],
            [EXCEPTIONAL_PASS],
        )
    )
    return support_permutations, diagnostic_states


def build_marked_indices(
    mode: str,
    relaxation: str,
) -> tuple[
    list[tuple[str, ...]],
    list[tuple[int, int, int, int, str, str, str, str]],
    set[int],
]:
    if mode not in {MODE_CURRENT_SHADOW, MODE_FORMAL_COMPLETION}:
        raise ValueError(f"Unsupported mode: {mode}")
    if relaxation not in relaxation_modes():
        raise ValueError(f"Unsupported relaxation mode: {relaxation}")

    support_permutations, diagnostic_states = build_relaxation_states()
    support_marks = {
        support_permutations.index(perm) for perm in strict_support_marked_permutations(support_permutations)
    }
    hyper_target = hyperbolic_orderings().index(marked_hyperbolic_order())
    exceptional_target = exceptional_orderings().index(marked_exceptional_order())
    glue_target = ZERO_GLUE if mode == MODE_CURRENT_SHADOW else NONZERO_GLUE

    require_hyper = relaxation not in {RELAXATION_HYPERBOLIC, RELAXATION_BOTH}
    require_exceptional = relaxation not in {RELAXATION_EXCEPTIONAL, RELAXATION_BOTH}

    marked_indices = set()
    for idx, (
        support_idx,
        _interleaving_idx,
        hyper_idx,
        exceptional_idx,
        glue_state,
        line_state,
        hyper_weight_state,
        exceptional_weight_state,
    ) in enumerate(diagnostic_states):
        if support_idx not in support_marks:
            continue
        if glue_state != glue_target or line_state != HEAD_LINE:
            continue
        if hyper_weight_state != HYPERBOLIC_PASS or exceptional_weight_state != EXCEPTIONAL_PASS:
            continue
        if require_hyper and hyper_idx != hyper_target:
            continue
        if require_exceptional and exceptional_idx != exceptional_target:
            continue
        marked_indices.add(idx)

    return support_permutations, diagnostic_states, marked_indices


def decode_relaxation_states(
    counts: Counter[str],
    support_permutations: list[tuple[str, ...]],
    diagnostic_states: list[tuple[int, int, int, int, str, str, str, str]],
    marked_indices: set[int],
    top: int,
) -> tuple[list[dict[str, object]], list[dict[str, object]], list[dict[str, object]]]:
    target_hits: list[dict[str, object]] = []
    nontarget_valid: list[dict[str, object]] = []
    invalid: list[dict[str, object]] = []

    for bitstring, count in counts.most_common(top):
        index = int(bitstring, 2)
        payload: dict[str, object] = {"bitstring": bitstring, "index": index, "count": count}
        if index >= len(diagnostic_states):
            invalid.append(payload)
            continue

        (
            support_idx,
            interleaving_idx,
            hyper_idx,
            exceptional_idx,
            glue_state,
            line_state,
            hyper_weight_state,
            exceptional_weight_state,
        ) = diagnostic_states[index]
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
        payload["glue_state"] = glue_state
        payload["line_state"] = line_state
        payload["hyperbolic_weight_state"] = hyper_weight_state
        payload["exceptional_weight_state"] = exceptional_weight_state
        if index in marked_indices:
            target_hits.append(payload)
        else:
            nontarget_valid.append(payload)

    return target_hits, nontarget_valid, invalid


def expected_marked_count(relaxation: str) -> int:
    base = 2 * 10  # support-mark count times free interleavings
    if relaxation == RELAXATION_EXACT:
        return base
    if relaxation == RELAXATION_EXCEPTIONAL:
        return base * 2
    if relaxation == RELAXATION_HYPERBOLIC:
        return base * 6
    if relaxation == RELAXATION_BOTH:
        return base * 6 * 2
    raise ValueError(f"Unsupported relaxation mode: {relaxation}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the exact TOE bridge diagnostic-relaxation Grover search.")
    parser.add_argument(
        "--mode",
        choices=[MODE_CURRENT_SHADOW, MODE_FORMAL_COMPLETION],
        default=MODE_FORMAL_COMPLETION,
        help="Current split-shadow realization or formal nonzero completion",
    )
    parser.add_argument(
        "--relaxation",
        choices=relaxation_modes(),
        default=RELAXATION_EXACT,
        help="Which order theorem sector to relax while keeping the 18-qubit state space fixed",
    )
    parser.add_argument("--shots", type=int, default=256, help="Number of simulator shots")
    parser.add_argument("--iterations", type=int, default=None, help="Explicit Grover iteration count")
    parser.add_argument("--top", type=int, default=8, help="Number of top decoded states to keep")
    parser.add_argument("--seed", type=int, default=7, help="Aer simulator and transpiler seed")
    return parser


def main() -> None:
    from qiskit import transpile
    from qiskit_aer import AerSimulator
    from permutation_grover_search import build_grover_circuit, normalize_counts

    args = build_parser().parse_args()
    support_permutations, diagnostic_states, marked_indices = build_marked_indices(
        args.mode,
        args.relaxation,
    )
    search_space_size = 1 << math.ceil(math.log2(len(diagnostic_states)))
    num_qubits = int(math.log2(search_space_size))
    iterations = args.iterations or grover_iteration_count(search_space_size, len(marked_indices))

    circuit = build_grover_circuit(num_qubits, marked_indices, iterations)
    simulator = AerSimulator(seed_simulator=args.seed)
    compiled = transpile(circuit, simulator, optimization_level=1, seed_transpiler=args.seed)
    result = simulator.run(compiled, shots=args.shots, seed_simulator=args.seed).result()
    counts = Counter(result.get_counts())

    decoded_target, decoded_nontarget_valid, decoded_invalid = decode_relaxation_states(
        counts,
        support_permutations,
        diagnostic_states,
        marked_indices,
        args.top,
    )

    summary = {
        "search_name": "toe_bridge_diagnostic_relaxation_search",
        "mode": args.mode,
        "relaxation": args.relaxation,
        "theorem_sources": theorem_sources_for_mode(args.mode),
        "interleaving_sector_is_free_in_exact_diagnostic_order_oracle": True,
        "support_permutation_count": len(support_permutations),
        "interleaving_pattern_count": len(interleaving_patterns()),
        "hyperbolic_order_count": len(hyperbolic_orderings()),
        "exceptional_order_count": len(exceptional_orderings()),
        "product_state_count": len(diagnostic_states),
        "search_space_size": search_space_size,
        "num_qubits": num_qubits,
        "grover_iterations": iterations,
        "shots": args.shots,
        "seed": args.seed,
        "marked_count": len(marked_indices),
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
