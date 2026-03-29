#!/usr/bin/env python3
"""Grover-style search on the exact double-Johnson interleaving shadow.

The bridge already carries two theorem-backed 10-state interleaving layers:

- the support shell chooses which 3 of 5 support slots carry the bridge core;
- the factor shell chooses which 3 of 5 factor slots carry the hyperbolic
  sector.

Both are exact copies of ``J(5,3)``, so the joint interleaving shadow has
exact size ``100 = 10 * 10``. The current bridge is asymmetric there:

- exact: the support theorem fixes one support interleaving, while the factor
  copy remains free, so the marked count is ``10``;
- support-interleaving-relaxed: both copies are free, so the marked count is
  ``100`` and the padded-shell optimum collapses to the uniform state.
"""

from __future__ import annotations

import argparse
import itertools
import json
import math
from collections import Counter

from toe_bridge_diagnostic_order_search import interleaving_patterns
from toe_support_diagnostic_search import marked_support_interleaving, support_interleavings


RELAXATION_EXACT = "exact"
RELAXATION_SUPPORT = "support-interleaving-relaxed"


def relaxation_modes() -> list[str]:
    return [RELAXATION_EXACT, RELAXATION_SUPPORT]


def grover_iteration_count(search_space_size: int, marked_count: int) -> int:
    if marked_count <= 0:
        raise ValueError("marked_count must be positive")
    return max(1, int(round((math.pi / 4.0) * math.sqrt(search_space_size / marked_count))))


def build_states() -> list[tuple[int, int]]:
    return list(
        itertools.product(
            range(len(support_interleavings())),
            range(len(interleaving_patterns())),
        )
    )


def expected_marked_count(relaxation: str) -> int:
    if relaxation == RELAXATION_EXACT:
        return len(interleaving_patterns())
    if relaxation == RELAXATION_SUPPORT:
        return len(support_interleavings()) * len(interleaving_patterns())
    raise ValueError(f"Unsupported relaxation mode: {relaxation}")


def build_marked_indices(relaxation: str) -> tuple[list[tuple[int, int]], set[int]]:
    if relaxation not in relaxation_modes():
        raise ValueError(f"Unsupported relaxation mode: {relaxation}")

    target_support = support_interleavings().index(marked_support_interleaving())
    states = build_states()
    marked = {
        idx
        for idx, (support_idx, _factor_idx) in enumerate(states)
        if relaxation == RELAXATION_SUPPORT or support_idx == target_support
    }
    return states, marked


def decode_states(
    counts: Counter[str],
    states: list[tuple[int, int]],
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

        support_idx, factor_idx = states[index]
        payload["support_interleaving"] = list(support_interleavings()[support_idx])
        payload["factor_interleaving"] = list(interleaving_patterns()[factor_idx])

        if index in marked_indices:
            target_hits.append(payload)
        else:
            nontarget_valid.append(payload)

    return target_hits, nontarget_valid, invalid


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run the double-Johnson interleaving shadow Grover search."
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

    decoded_target, decoded_nontarget_valid, decoded_invalid = decode_states(
        counts, states, marked_indices, args.top
    )

    summary = {
        "search_name": "toe_double_interleaving_shadow_search",
        "relaxation": args.relaxation,
        "theorem_surface": "double-Johnson interleaving shadow J(5,3) x J(5,3)",
        "support_interleaving_count": len(support_interleavings()),
        "factor_interleaving_count": len(interleaving_patterns()),
        "state_count": len(states),
        "search_space_size": search_space_size,
        "num_qubits": num_qubits,
        "grover_iterations": iterations,
        "shots": args.shots,
        "seed": args.seed,
        "marked_count": len(marked_indices),
        "expected_marked_count": expected_marked_count(args.relaxation),
        "marked_count_matches_formula": len(marked_indices) == expected_marked_count(args.relaxation),
        "marked_support_interleaving": list(marked_support_interleaving()),
        "factor_copy_is_free_in_exact_mode": args.relaxation == RELAXATION_EXACT,
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
