#!/usr/bin/env python3
"""Grover-style search with factorized five-factor bridge ordering.

This repackages the exact five-factor bridge permutation sector into three
finite factors without changing the underlying 120-state space:

- a hyperbolic ordering on ``U1, U2, U3``;
- an exceptional ordering on ``E8_1, E8_2``;
- an interleaving pattern choosing which three of the five slots belong to the
  hyperbolic sector.

The factorization is exact:

    5! = C(5,3) * 3! * 2! = 10 * 6 * 2 = 120.

So this oracle is diagnostic rather than approximate: it localizes failures by
theorem sector while preserving the same factor-space cardinality used in the
earlier bridge searches.
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
from toe_bridge_split_weight_filter_search import (
    EXCEPTIONAL_FAIL,
    EXCEPTIONAL_PASS,
    HYPERBOLIC_FAIL,
    HYPERBOLIC_PASS,
)


HYPERBOLIC_ITEMS = ("U1", "U2", "U3")
EXCEPTIONAL_ITEMS = ("E8_1", "E8_2")


def grover_iteration_count(search_space_size: int, marked_count: int) -> int:
    if marked_count <= 0:
        raise ValueError("marked_count must be positive")
    return max(1, int(round((math.pi / 4.0) * math.sqrt(search_space_size / marked_count))))


def line_states() -> list[str]:
    return [HEAD_LINE, TAIL_LINE]


def hyperbolic_weight_states() -> list[str]:
    return [HYPERBOLIC_PASS, HYPERBOLIC_FAIL]


def exceptional_weight_states() -> list[str]:
    return [EXCEPTIONAL_PASS, EXCEPTIONAL_FAIL]


def hyperbolic_orderings() -> list[tuple[str, str, str]]:
    return list(itertools.permutations(HYPERBOLIC_ITEMS))


def exceptional_orderings() -> list[tuple[str, str]]:
    return list(itertools.permutations(EXCEPTIONAL_ITEMS))


def interleaving_patterns() -> list[tuple[int, int, int]]:
    return list(itertools.combinations(range(5), 3))


def merge_factor_permutation(
    hyperbolic_order: tuple[str, str, str],
    exceptional_order: tuple[str, str],
    interleaving_pattern: tuple[int, int, int],
) -> tuple[str, str, str, str, str]:
    slots: list[str | None] = [None] * 5
    hyper_iter = iter(hyperbolic_order)
    exceptional_iter = iter(exceptional_order)
    hyper_positions = set(interleaving_pattern)

    for idx in range(5):
        slots[idx] = next(hyper_iter) if idx in hyper_positions else next(exceptional_iter)

    return tuple(slots)  # type: ignore[return-value]


def marked_hyperbolic_order() -> tuple[str, str, str]:
    return ("U3", "U1", "U2")


def marked_exceptional_order() -> tuple[str, str]:
    return ("E8_2", "E8_1")


def build_marked_indices(
    mode: str,
) -> tuple[
    list[tuple[str, ...]],
    list[tuple[int, int, int, int, str, str, str, str]],
    set[int],
]:
    if mode not in {MODE_CURRENT_SHADOW, MODE_FORMAL_COMPLETION}:
        raise ValueError(f"Unsupported mode: {mode}")

    support_permutations = list(itertools.permutations(SUPPORT_ITEMS))
    interleavings = interleaving_patterns()
    hyper_orders = hyperbolic_orderings()
    exceptional_orders = exceptional_orderings()
    diagnostic_states = list(
        itertools.product(
            range(len(support_permutations)),
            range(len(interleavings)),
            range(len(hyper_orders)),
            range(len(exceptional_orders)),
            [ZERO_GLUE, NONZERO_GLUE],
            line_states(),
            hyperbolic_weight_states(),
            exceptional_weight_states(),
        )
    )

    support_marks = {
        support_permutations.index(perm) for perm in strict_support_marked_permutations(support_permutations)
    }
    hyper_target = hyper_orders.index(marked_hyperbolic_order())
    exceptional_target = exceptional_orders.index(marked_exceptional_order())
    glue_target = ZERO_GLUE if mode == MODE_CURRENT_SHADOW else NONZERO_GLUE

    marked_indices = {
        idx
        for idx, (
            support_idx,
            _interleaving_idx,
            hyper_idx,
            exceptional_idx,
            glue_state,
            line_state,
            hyper_weight_state,
            exceptional_weight_state,
        ) in enumerate(diagnostic_states)
        if support_idx in support_marks
        and hyper_idx == hyper_target
        and exceptional_idx == exceptional_target
        and glue_state == glue_target
        and line_state == HEAD_LINE
        and hyper_weight_state == HYPERBOLIC_PASS
        and exceptional_weight_state == EXCEPTIONAL_PASS
    }
    return support_permutations, diagnostic_states, marked_indices


def decode_diagnostic_order_states(
    counts: Counter[str],
    support_permutations: list[tuple[str, ...]],
    diagnostic_states: list[tuple[int, int, int, int, str, str, str, str]],
    marked_indices: set[int],
    top: int,
) -> tuple[list[dict[str, object]], list[dict[str, object]], list[dict[str, object]]]:
    interleavings = interleaving_patterns()
    hyper_orders = hyperbolic_orderings()
    exceptional_orders = exceptional_orderings()

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

        interleaving = interleavings[interleaving_idx]
        hyper_order = hyper_orders[hyper_idx]
        exceptional_order = exceptional_orders[exceptional_idx]
        factor_permutation = merge_factor_permutation(hyper_order, exceptional_order, interleaving)

        payload["support_permutation"] = list(support_permutations[support_idx])
        payload["interleaving_pattern"] = list(interleaving)
        payload["hyperbolic_order"] = list(hyper_order)
        payload["exceptional_order"] = list(exceptional_order)
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


def theorem_sources_for_mode(mode: str) -> list[str]:
    common = [
        "exploration/w33_selector_a4_weight_hierarchy_bridge.py",
        "exploration/w33_global_local_carrier_split_bridge.py",
        "exploration/w33_u1_head_compatible_line_bridge.py",
        "exploration/w33_common_line_exact_image_bridge.py",
        "exploration/w33_yukawa_transport_coupling_hierarchy_bridge.py",
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
    parser = argparse.ArgumentParser(description="Run the exact TOE bridge diagnostic-order Grover search.")
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

    support_permutations, diagnostic_states, marked_indices = build_marked_indices(args.mode)
    search_space_size = 1 << math.ceil(math.log2(len(diagnostic_states)))
    num_qubits = int(math.log2(search_space_size))
    iterations = args.iterations or grover_iteration_count(search_space_size, len(marked_indices))

    circuit = build_grover_circuit(num_qubits, marked_indices, iterations)
    simulator = AerSimulator(seed_simulator=args.seed)
    compiled = transpile(circuit, simulator, optimization_level=1, seed_transpiler=args.seed)
    result = simulator.run(compiled, shots=args.shots, seed_simulator=args.seed).result()
    counts = Counter(result.get_counts())

    decoded_target, decoded_nontarget_valid, decoded_invalid = decode_diagnostic_order_states(
        counts,
        support_permutations,
        diagnostic_states,
        marked_indices,
        args.top,
    )

    summary = {
        "search_name": "toe_bridge_diagnostic_order_search",
        "mode": args.mode,
        "theorem_sources": theorem_sources_for_mode(args.mode),
        "support_permutation_count": len(support_permutations),
        "interleaving_pattern_count": len(interleaving_patterns()),
        "hyperbolic_order_count": len(hyperbolic_orderings()),
        "exceptional_order_count": len(exceptional_orderings()),
        "glue_state_count": 2,
        "line_state_count": 2,
        "hyperbolic_weight_state_count": 2,
        "exceptional_weight_state_count": 2,
        "product_state_count": len(diagnostic_states),
        "search_space_size": search_space_size,
        "num_qubits": num_qubits,
        "grover_iterations": iterations,
        "shots": args.shots,
        "seed": args.seed,
        "marked_count": len(marked_indices),
        "factorization_identity": "5! = C(5,3) * 3! * 2! = 10 * 6 * 2",
        "forced_hyperbolic_order": list(marked_hyperbolic_order()),
        "forced_exceptional_order": list(marked_exceptional_order()),
        "forced_line_state": HEAD_LINE,
        "forced_hyperbolic_weight_state": HYPERBOLIC_PASS,
        "forced_exceptional_weight_state": EXCEPTIONAL_PASS,
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
