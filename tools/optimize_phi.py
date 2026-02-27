#!/usr/bin/env python3
"""Advanced search/optimization for edge->root bijections φ.

This tool implements a hill‑climbing/simulated‑annealing style optimizer that
combines edge swaps and occasional root sign flips.  It keeps track of both the
raw lift size and the gauge‑corrected lift size, saving the best candidate
found during the run.

Options allow configuration of iteration count, temperature schedule, and
output paths.  Results are written to artifacts/phi_optimize_candidate.json
(and sign gauge to artifacts/sign_gauge_candidate.json).

The algorithm is deliberately simple; more sophisticated techniques (e.g.
Genetic Algorithms, MeatAxe-based heuristics) could be added later.
"""
from __future__ import annotations

import argparse, json, random, math
from pathlib import Path
from typing import List, Tuple

ROOT = Path(__file__).resolve().parents[1]
import sys
sys.path.insert(0, str(ROOT))

from tools.compute_phi_lift_subgroup import compute_lift_for_roots, edges, edge_action_orbits
from tools.compute_phi_sign_gauge import compute_sign_gauge, load_root_list  # type: ignore

# helper to convert map -> ordered lists

def load_current_mapping(path: Path):
    edges_sorted, root_list = load_root_list(path)
    return edges_sorted, root_list


def save_mapping(edges_sorted: List[Tuple[int, int]], root_list: List[Tuple[int, ...]], fname: Path):
    m = len(root_list)
    out = {str(edges_sorted[i]): list(root_list[i]) for i in range(m)}
    fname.write_text(json.dumps(out, indent=2))


def random_swap(root_list: List[Tuple[int, ...]]):
    a,b = random.sample(range(len(root_list)),2)
    root_list[a], root_list[b] = root_list[b], root_list[a]
    return a,b


def random_sign_flip(root_list: List[Tuple[int, ...]]):
    i = random.randrange(len(root_list))
    root_list[i] = tuple(-x for x in root_list[i])
    return i


def optimize(trials: int, temp0: float, swap_prob: float, target_orbits: List[int]=None):
    edges_sorted, current = load_current_mapping(ROOT / "artifacts" / "edge_to_e8_root.json")
    best = list(current)
    best_raw = compute_lift_for_roots(current)
    best_gauged = compute_sign_gauge(current)[2]
    current_raw = best_raw
    current_list = list(current)

    def orbit_distance(lst):
        orbs = edge_action_orbits(lst)
        if target_orbits is None:
            return 0
        # compute symmetric difference sum
        # extend shorter with zeros
        a = sorted(orbs)
        b = sorted(target_orbits)
        # pad
        L = max(len(a), len(b))
        a += [0]*(L-len(a))
        b += [0]*(L-len(b))
        return sum(abs(x-y) for x,y in zip(a,b))

    best_orb_dist = orbit_distance(current_list)

    for t in range(trials):
        # temperature schedule
        temp = temp0 * (1 - t / trials)
        move = random.random()
        if move < swap_prob:
            a,b = random_swap(current_list)
            revert = lambda: current_list.__setitem__(a, current_list[b]) or current_list.__setitem__(b, current_list[a])
        else:
            i = random_sign_flip(current_list)
            revert = lambda: current_list.__setitem__(i, tuple(-x for x in current_list[i]))

        new_raw = compute_lift_for_roots(current_list)
        new_orb_dist = orbit_distance(current_list)
        # if we're targeting orbits, accept based on distance metric instead of raw
        if target_orbits is not None:
            # we want to *minimize* orbital distance
            delta_dist = best_orb_dist - new_orb_dist
            accept_move = False
            if delta_dist > 0:
                accept_move = True
            else:
                if random.random() < math.exp(delta_dist / (temp if temp>0 else 1e-6)):
                    accept_move = True
            if accept_move:
                current_raw = new_raw
                # if improvement record candidate
                if new_orb_dist < best_orb_dist:
                    best_orb_dist = new_orb_dist
                    save_mapping(edges_sorted, current_list, ROOT / "artifacts" / "phi_orbit_candidate.json")
                    print(f"improved orbit distance to {new_orb_dist} at trial {t}")
            else:
                revert()
        else:
            delta = new_raw - current_raw
            accept = False
            if delta >= 0:
                accept = True
            else:
                # metropolis criterion
                if random.random() < math.exp(delta / (temp if temp>0 else 1e-6)):
                    accept = True
            if accept:
                current_raw = new_raw
                if new_raw > best_raw:
                    # evaluate gauge
                    signvec, signed, new_gauged = compute_sign_gauge(current_list)
                    if new_gauged > best_gauged:
                        best_gauged = new_gauged
                        best = list(current_list)
                        save_mapping(edges_sorted, best, ROOT / "artifacts" / "phi_optimize_candidate.json")
                        (ROOT / "artifacts" / "sign_gauge_candidate.json").write_text(json.dumps(signvec, indent=2))
                        print(f"new best gauged lift {best_gauged} at trial {t}")
                    best_raw = new_raw
            else:
                revert()
    print("optimization finished, best_raw", best_raw, "best_gauged", best_gauged)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Optimize edge->root bijection with stochastic search")
    parser.add_argument("--trials", type=int, default=10000)
    parser.add_argument("--temp", type=float, default=1.0)
    parser.add_argument("--swap-prob", type=float, default=0.9, help="probability of choosing swap over sign flip")
    parser.add_argument("--target-orbits", help="comma-separated target orbit sizes, e.g. 36,27,27,27,1,1,1")
    args = parser.parse_args()
    target = None
    if args.target_orbits:
        target = sorted(int(x) for x in args.target_orbits.split(","))
    optimize(args.trials, args.temp, args.swap_prob, target)
