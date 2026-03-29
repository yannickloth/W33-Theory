#!/usr/bin/env python3
"""Grover-style search with exact packet-concentration filter.

This refines the line-factor oracle by adding one theorem-backed concentration
bit:

- dominant_weight_filter_pass
- dominant_weight_filter_fail

The marked sector keeps only the exact pass state justified by the current
bridge theorems:

- U3 carries more than 4/5 of the hyperbolic selector packet
- E8_2 carries more than 8/9 of the exceptional selector packet
"""

from __future__ import annotations

import argparse
import itertools
import json
import math
from collections import Counter

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
from toe_bridge_permutation_search import five_factor_items, five_factor_predicate


WEIGHT_PASS = "dominant_weight_filter_pass"
WEIGHT_FAIL = "dominant_weight_filter_fail"


def grover_iteration_count(search_space_size: int, marked_count: int) -> int:
    if marked_count <= 0:
        raise ValueError("marked_count must be positive")
    return max(1, int(round((math.pi / 4.0) * math.sqrt(search_space_size / marked_count))))


def weight_filter_states() -> list[str]:
    return [WEIGHT_PASS, WEIGHT_FAIL]


def line_states() -> list[str]:
    return [HEAD_LINE, TAIL_LINE]


def build_weight_filter_states() -> tuple[list[tuple[str, ...]], list[tuple[str, ...]], list[tuple[int, int, str, str, str]]]:
    support_permutations = list(itertools.permutations(SUPPORT_ITEMS))
    factor_permutations = list(itertools.permutations(five_factor_items()))
    product_states = list(
        itertools.product(
            range(len(support_permutations)),
            range(len(factor_permutations)),
            [ZERO_GLUE, NONZERO_GLUE],
            line_states(),
            weight_filter_states(),
        )
    )
    return support_permutations, factor_permutations, product_states


def build_marked_indices(
    mode: str,
) -> tuple[list[tuple[str, ...]], list[tuple[str, ...]], list[tuple[int, int, str, str, str]], set[int]]:
    if mode not in {MODE_CURRENT_SHADOW, MODE_FORMAL_COMPLETION}:
        raise ValueError(f"Unsupported mode: {mode}")

    support_permutations, factor_permutations, product_states = build_weight_filter_states()
    support_marks = {
        support_permutations.index(perm) for perm in strict_support_marked_permutations(support_permutations)
    }
    factor_marks = {idx for idx, perm in enumerate(factor_permutations) if five_factor_predicate(perm)}
    glue_target = ZERO_GLUE if mode == MODE_CURRENT_SHADOW else NONZERO_GLUE

    marked_indices = {
        idx
        for idx, (support_idx, factor_idx, glue_state, line_state, weight_state) in enumerate(product_states)
        if support_idx in support_marks
        and factor_idx in factor_marks
        and glue_state == glue_target
        and line_state == HEAD_LINE
        and weight_state == WEIGHT_PASS
    }
    return support_permutations, factor_permutations, product_states, marked_indices


def decode_weight_filter_states(
    counts: Counter[str],
    support_permutations: list[tuple[str, ...]],
    factor_permutations: list[tuple[str, ...]],
    product_states: list[tuple[int, int, str, str, str]],
    marked_indices: set[int],
    top: int,
) -> tuple[list[dict[str, object]], list[dict[str, object]], list[dict[str, object]]]:
    target_hits: list[dict[str, object]] = []
    nontarget_valid: list[dict[str, object]] = []
    invalid: list[dict[str, object]] = []

    for bitstring, count in counts.most_common(top):
        index = int(bitstring, 2)
        payload: dict[str, object] = {"bitstring": bitstring, "index": index, "count": count}
        if index >= len(product_states):
            invalid.append(payload)
            continue

        support_idx, factor_idx, glue_state, line_state, weight_state = product_states[index]
        payload["support_permutation"] = list(support_permutations[support_idx])
        payload["factor_permutation"] = list(factor_permutations[factor_idx])
        payload["glue_state"] = glue_state
        payload["line_state"] = line_state
        payload["weight_filter_state"] = weight_state

        if index in marked_indices:
            target_hits.append(payload)
        else:
            nontarget_valid.append(payload)

    return target_hits, nontarget_valid, invalid


def theorem_sources_for_mode(mode: str) -> list[str]:
    common = [
        "exploration/w33_selector_a4_weight_hierarchy_bridge.py",
        "exploration/w33_global_local_carrier_split_bridge.py",
        "exploration/w33_u1_head_compatible_line_bridge.py",
        "exploration/w33_common_line_exact_image_bridge.py",
    ]
    if mode == MODE_CURRENT_SHADOW:
        return common + [
            "exploration/w33_transport_rigid_split_avatar_bridge.py",
            "exploration/w33_refined_k3_zero_orbit_bridge.py",
        ]
    return common + [
        "exploration/w33_formal_external_completion_avatar_bridge.py",
        "exploration/w33_transport_unique_nonzero_cocycle_orbit_bridge.py",
    ]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the exact TOE bridge weight-filter Grover search.")
    parser.add_argument(
        "--mode",
        choices=[MODE_CURRENT_SHADOW, MODE_FORMAL_COMPLETION],
        default=MODE_FORMAL_COMPLETION,
        help="Current split-shadow realization or formal nonzero completion",
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

    support_permutations, factor_permutations, product_states, marked_indices = build_marked_indices(args.mode)
    search_space_size = 1 << math.ceil(math.log2(len(product_states)))
    num_qubits = int(math.log2(search_space_size))
    iterations = args.iterations or grover_iteration_count(search_space_size, len(marked_indices))

    circuit = build_grover_circuit(num_qubits, marked_indices, iterations)
    simulator = AerSimulator(seed_simulator=args.seed)
    compiled = transpile(circuit, simulator, optimization_level=1, seed_transpiler=args.seed)
    result = simulator.run(compiled, shots=args.shots, seed_simulator=args.seed).result()
    counts = Counter(result.get_counts())

    decoded_target, decoded_nontarget_valid, decoded_invalid = decode_weight_filter_states(
        counts,
        support_permutations,
        factor_permutations,
        product_states,
        marked_indices,
        args.top,
    )

    summary = {
        "search_name": "toe_bridge_weight_filter_search",
        "mode": args.mode,
        "theorem_sources": theorem_sources_for_mode(args.mode),
        "support_permutation_count": len(support_permutations),
        "factor_permutation_count": len(factor_permutations),
        "glue_state_count": 2,
        "line_state_count": 2,
        "weight_filter_state_count": 2,
        "product_state_count": len(product_states),
        "search_space_size": search_space_size,
        "num_qubits": num_qubits,
        "grover_iterations": iterations,
        "shots": args.shots,
        "seed": args.seed,
        "marked_count": len(marked_indices),
        "forced_line_state": HEAD_LINE,
        "forced_weight_filter_state": WEIGHT_PASS,
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
