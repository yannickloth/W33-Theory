#!/usr/bin/env python3
"""Search for single-site glider-like behaviour in ternary CA on W33.

A simple glider is a configuration where a single nonzero cell at t=0
produces exactly one nonzero cell at some later time t>0 (possibly at a
different vertex).  This script scans all vertices and several timesteps
for the specified rule type; any such propagation indicates a possible “signal
wire”.

Usage:
    python scripts/find_gliders.py --rule totalistic --steps 20

Returns a list of (start_vertex, end_vertex, time) triples.
"""

from __future__ import annotations

import argparse
from collections import Counter

import numpy as np

from w33_cellular_automaton import ternary_cellular_automaton
from e8_embedding_group_theoretic import build_w33


def simulate_rule(rule_type: str, steps: int):
    n, vertices, adj, edges = build_w33()
    gliders = []
    for start in range(n):
        # initial state: 1 at start, 0 elsewhere
        state = np.zeros(n, dtype=int)
        state[start] = 1
        history = [state.copy()]
        for t in range(steps):
            # step using CA update code from ternary_cellular_automaton
            new = np.zeros(n, dtype=int)
            for v in range(n):
                nbr_sum = sum(state[w] for w in adj[v]) % 3
                nbr_states = [state[w] for w in adj[v]]
                self_val = state[v]
                if rule_type == "totalistic":
                    new[v] = (self_val + nbr_sum) % 3
                elif rule_type == "majority":
                    cnt = Counter(nbr_states)
                    mode = cnt.most_common(1)[0][0]
                    new[v] = (mode + self_val) % 3
                elif rule_type == "life":
                    live = sum(1 for s in nbr_states if s > 0)
                    if live in (3, 4):
                        new[v] = (self_val + 1) % 3
                    elif live > 8:
                        new[v] = (self_val - 1) % 3
                    else:
                        new[v] = self_val
            state = new
            history.append(state.copy())
        # look for gliders: single nonzero at t=0 leading to single nonzero at t>0
        for t, st in enumerate(history[1:], start=1):
            if np.count_nonzero(st) == 1:
                end = int(np.nonzero(st)[0][0])
                if end != start:
                    gliders.append((start, end, t))
    return gliders


def main():
    parser = argparse.ArgumentParser(description="Find single-site gliders")
    parser.add_argument("--rule", choices=["totalistic", "majority", "life"],
                        default="totalistic")
    parser.add_argument("--steps", type=int, default=20)
    args = parser.parse_args()

    gl = simulate_rule(args.rule, args.steps)
    if not gl:
        print(f"no single-site gliders found for rule {args.rule} in {args.steps} steps")
    else:
        print(f"gliders for rule {args.rule}:")
        for start, end, t in gl:
            print(f"  {start} -> {end} at t={t}")

if __name__ == "__main__":
    main()
