#!/usr/bin/env python3
"""Grover-style search relaxing the exact support-shell theorem one sector at a time.

This keeps the factorized support shell fixed:

`120 = 10 support interleavings * 6 core orders * 2 free local tail orders`

and relaxes the two exact support theorems one sector at a time:

- the support interleaving theorem, fixing which `3` of `5` slots carry the core;
- the core-order theorem, fixing `(head_line, u1_plane, transport_avatar)`.

The local tail order remains free in every mode.
"""

from __future__ import annotations

import argparse
import json
import math
from collections import Counter

from toe_support_diagnostic_search import (
    build_support_states,
    decode_support_states,
    marked_support_core_order,
    marked_support_interleaving,
    support_core_orderings,
    support_interleavings,
)


RELAXATION_EXACT = "exact"
RELAXATION_INTERLEAVING = "interleaving-relaxed"
RELAXATION_CORE_ORDER = "core-order-relaxed"
RELAXATION_BOTH = "both-relaxed"


def relaxation_modes() -> list[str]:
    return [
        RELAXATION_EXACT,
        RELAXATION_INTERLEAVING,
        RELAXATION_CORE_ORDER,
        RELAXATION_BOTH,
    ]


def grover_iteration_count(search_space_size: int, marked_count: int) -> int:
    if marked_count <= 0:
        raise ValueError("marked_count must be positive")
    return max(1, int(round((math.pi / 4.0) * math.sqrt(search_space_size / marked_count))))


def expected_marked_count(relaxation: str) -> int:
    base = 2
    if relaxation == RELAXATION_EXACT:
        return base
    if relaxation == RELAXATION_INTERLEAVING:
        return base * 10
    if relaxation == RELAXATION_CORE_ORDER:
        return base * 6
    if relaxation == RELAXATION_BOTH:
        return 120
    raise ValueError(f"Unsupported relaxation mode: {relaxation}")


def build_marked_indices(relaxation: str) -> tuple[list[tuple[int, int, int]], set[int]]:
    if relaxation not in relaxation_modes():
        raise ValueError(f"Unsupported relaxation mode: {relaxation}")

    states = build_support_states()
    target_interleaving = support_interleavings().index(marked_support_interleaving())
    target_core_order = support_core_orderings().index(marked_support_core_order())
    require_interleaving = relaxation not in {RELAXATION_INTERLEAVING, RELAXATION_BOTH}
    require_core_order = relaxation not in {RELAXATION_CORE_ORDER, RELAXATION_BOTH}

    marked = {
        idx
        for idx, (interleaving_idx, core_idx, _local_idx) in enumerate(states)
        if (not require_interleaving or interleaving_idx == target_interleaving)
        and (not require_core_order or core_idx == target_core_order)
    }
    return states, marked


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the factorized TOE support relaxation search.")
    parser.add_argument("--relaxation", choices=relaxation_modes(), default=RELAXATION_EXACT)
    parser.add_argument("--shots", type=int, default=1024, help="Number of simulator shots")
    parser.add_argument("--iterations", type=int, default=None, help="Explicit Grover iteration count")
    parser.add_argument("--top", type=int, default=8, help="Number of decoded states to keep")
    parser.add_argument("--seed", type=int, default=7, help="Aer simulator and transpiler seed")
    return parser


def main() -> None:
    from qiskit import transpile
    from qiskit_aer import AerSimulator
    from permutation_grover_search import build_grover_circuit, normalize_counts

    args = build_parser().parse_args()
    states, marked_indices = build_marked_indices(args.relaxation)
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

    decoded_target, decoded_nontarget_valid, decoded_invalid = decode_support_states(
        counts, states, marked_indices, args.top
    )

    summary = {
        "search_name": "toe_support_diagnostic_relaxation_search",
        "relaxation": args.relaxation,
        "theorem_surface": "fixed factorized support shell with separate interleaving and core-order relaxations",
        "support_interleaving_count": len(support_interleavings()),
        "support_core_order_count": len(support_core_orderings()),
        "state_count": len(states),
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
