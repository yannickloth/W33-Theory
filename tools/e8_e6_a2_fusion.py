#!/usr/bin/env python3
"""
E8 → E6 ⊕ A2 (= su(3)) decomposition, checked at the root-addition level.

This script treats the E8 Lie algebra in its adjoint (root) realization:
  - 240 roots = 72 (E6 roots) + 6 (A2 roots) + 162 (mixed roots)
  - 248 = 240 roots + 8 Cartan generators (rank(E6)+rank(A2)=6+2)

We use the existing `tools/compute_double_sixes.py` construction of E8 roots and
its BFS orbit decomposition under W(E6):
  240 = 72 + 6×27 + 6×1

Then we:
  - Identify the A2 simple roots orthogonal to the E6 sublattice:
      alpha = (1,-1,0,0,0,0,0,0)
      beta  = (0,1,0,0,0,0,0,-1)
    and label each W(E6) orbit by its A2 Dynkin labels (d1,d2) = (r·alpha, r·beta).
  - Compute "fusion rules" from root addition:
      [e_α, e_β] ≠ 0  iff  α+β is a root
    and summarize which orbit-types bracket into which orbit-types.
  - Extract the tri-linear selection rule on the 6×27 mixed roots by counting
    triples (α,β,γ) with α+β+γ=0 and grouping by A2 weights.

The output is a machine-readable JSON artifact plus a concise terminal summary.
"""

from __future__ import annotations

import importlib.util
import json
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

import numpy as np


def _load_compute_double_sixes():
    repo_root = Path(__file__).resolve().parents[1]
    path = repo_root / "tools" / "compute_double_sixes.py"
    spec = importlib.util.spec_from_file_location("compute_double_sixes", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Failed to load module from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_compute_double_sixes = _load_compute_double_sixes()
compute_we6_orbits = _compute_double_sixes.compute_we6_orbits
construct_e8_roots = _compute_double_sixes.construct_e8_roots

ROOT = Path(__file__).resolve().parents[1]

# A2 (= su(3)) simple roots orthogonal to the E6 subdiagram (alpha_3..alpha_8 in Bourbaki E8).
SU3_ALPHA = np.array([1.0, -1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
SU3_BETA = np.array([0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, -1.0])


def root_key(r: np.ndarray) -> Tuple[int, ...]:
    """
    Stable hash key for an E8 root: scale by 2 to avoid halves, then round to int.

    `construct_e8_roots()` uses entries in {±1,0,±1/2}, so 2*r is integral.
    """
    return tuple(int(round(2 * float(x))) for x in r.tolist())


@dataclass(frozen=True)
class OrbitInfo:
    orbit_index: int
    size: int
    su3_weight: Tuple[int, int]
    label: str


def orbit_su3_weight(roots: np.ndarray, orbit: List[int]) -> Tuple[int, int]:
    r = roots[orbit[0]]
    d1 = int(round(float(np.dot(r, SU3_ALPHA))))
    d2 = int(round(float(np.dot(r, SU3_BETA))))
    return (d1, d2)


def build_orbit_infos(roots: np.ndarray, orbits: List[List[int]]) -> List[OrbitInfo]:
    infos: List[OrbitInfo] = []
    for oi, orb in enumerate(orbits):
        w = orbit_su3_weight(roots, orb)
        sz = len(orb)
        if sz == 72:
            kind = "E6"
        elif sz == 1:
            kind = "A2"
        elif sz == 27:
            kind = "MIX27"
        else:
            kind = f"ORB{sz}"
        label = f"{kind}[{sz}]@{w[0]},{w[1]}"
        infos.append(OrbitInfo(orbit_index=oi, size=sz, su3_weight=w, label=label))
    return infos


def index_by_orbit(orbits: List[List[int]]) -> Dict[int, int]:
    idx: Dict[int, int] = {}
    for oi, orb in enumerate(orbits):
        for v in orb:
            idx[v] = oi
    return idx


def classify_3_and_3bar(
    mix_infos: Iterable[OrbitInfo],
) -> Tuple[List[OrbitInfo], List[OrbitInfo]]:
    """
    Partition the six MIX27 orbits into A2 fundamental 3 vs anti-fundamental 3bar.

    In Dynkin-label coordinates (d1,d2) with our chosen simple roots, the 3 weights are:
      (1,0), (-1,1), (0,-1)
    and the 3bar weights are:
      (0,1), (1,-1), (-1,0)
    """
    weights_3 = {(1, 0), (-1, 1), (0, -1)}
    weights_3bar = {(0, 1), (1, -1), (-1, 0)}
    reps_3: List[OrbitInfo] = []
    reps_3bar: List[OrbitInfo] = []
    for info in mix_infos:
        if info.su3_weight in weights_3:
            reps_3.append(info)
        elif info.su3_weight in weights_3bar:
            reps_3bar.append(info)
        else:
            raise RuntimeError(f"Unexpected MIX27 A2-weight: {info}")
    reps_3.sort(key=lambda x: x.su3_weight)
    reps_3bar.sort(key=lambda x: x.su3_weight)
    return reps_3, reps_3bar


def compute_root_addition_fusion(
    roots: np.ndarray,
    orbits: List[List[int]],
    orbit_infos: List[OrbitInfo],
) -> Dict[str, Dict[str, Dict[str, int]]]:
    """
    Count orbit-level fusion rules from root addition:
      α (in orbit A) + β (in orbit B) = γ (in orbit C).

    Returns nested dict: left_label -> right_label -> out_label -> count.
    """
    idx_orb = index_by_orbit(orbits)
    labels = {info.orbit_index: info.label for info in orbit_infos}

    root_to_index = {root_key(roots[i]): i for i in range(len(roots))}

    fusion: Dict[str, Dict[str, Counter[str]]] = defaultdict(
        lambda: defaultdict(Counter)
    )
    for i in range(len(roots)):
        ki = root_key(roots[i])
        oi = idx_orb[i]
        li = labels[oi]
        for j in range(len(roots)):
            s = tuple(ki[t] + root_key(roots[j])[t] for t in range(8))
            k = root_to_index.get(s)
            if k is None:
                continue
            oj = idx_orb[j]
            ok = idx_orb[k]
            lj = labels[oj]
            lk = labels[ok]
            fusion[li][lj][lk] += 1

    # Convert Counters to dicts for JSON.
    return {a: {b: dict(c) for b, c in bb.items()} for a, bb in fusion.items()}


def compute_triples_alpha_beta_gamma_zero(
    roots: np.ndarray,
    orbit_infos: List[OrbitInfo],
    idx_orb: Dict[int, int],
) -> Dict[str, object]:
    """
    Count mixed-root triples (α,β,γ) with α+β+γ=0, grouped by A2 weight triple.

    We report only triples where all three roots lie in MIX27 orbits.
    """
    root_to_index = {root_key(roots[i]): i for i in range(len(roots))}

    is_mix = {info.orbit_index for info in orbit_infos if info.size == 27}
    w_by_orb = {info.orbit_index: info.su3_weight for info in orbit_infos}

    wsum_counts: Counter[Tuple[int, int]] = Counter()
    weight_multiset_counts: Counter[str] = Counter()
    mix_indices = [i for i in range(len(roots)) if idx_orb[i] in is_mix]
    keys = {i: root_key(roots[i]) for i in mix_indices}

    for i in mix_indices:
        oi = idx_orb[i]
        wi = w_by_orb[oi]
        ki = keys[i]
        for j in mix_indices:
            oj = idx_orb[j]
            wj = w_by_orb[oj]
            kj = keys[j]
            s = tuple(-(ki[t] + kj[t]) for t in range(8))
            k = root_to_index.get(s)
            if k is None:
                continue
            ok = idx_orb[k]
            if ok not in is_mix:
                continue
            wk = w_by_orb[ok]
            wsum = (wi[0] + wj[0] + wk[0], wi[1] + wj[1] + wk[1])
            wsum_counts[wsum] += 1
            trip = tuple(sorted((wi, wj, wk)))
            weight_multiset_counts[str(trip)] += 1

    return {
        "wsum_counts": {f"{k[0]},{k[1]}": int(v) for k, v in wsum_counts.items()},
        "weight_multiset_counts": dict(weight_multiset_counts),
    }


def main() -> None:
    roots = construct_e8_roots()
    orbits = compute_we6_orbits(roots)
    orbit_infos = build_orbit_infos(roots, orbits)
    idx_orb = index_by_orbit(orbits)
    root_to_index = {root_key(roots[i]): i for i in range(len(roots))}

    sizes = sorted((info.size for info in orbit_infos), reverse=True)
    print("E8 roots:", len(roots))
    print("W(E6) orbit sizes:", sizes)

    # Basic SU3 checks
    print("\nA2 simple roots:")
    print("  alpha =", SU3_ALPHA.tolist())
    print("  beta  =", SU3_BETA.tolist())
    print("  <alpha,alpha> =", float(np.dot(SU3_ALPHA, SU3_ALPHA)))
    print("  <beta,beta>   =", float(np.dot(SU3_BETA, SU3_BETA)))
    print("  <alpha,beta>  =", float(np.dot(SU3_ALPHA, SU3_BETA)))

    # Summarize orbit labels
    print("\nOrbits labeled by A2 Dynkin coordinates (d1,d2)= (r·alpha, r·beta):")
    for info in sorted(
        orbit_infos, key=lambda x: (-x.size, x.su3_weight, x.orbit_index)
    ):
        print(f"  orbit {info.orbit_index:2d}: {info.label}")

    mix_infos = [info for info in orbit_infos if info.size == 27]
    reps_3, reps_3bar = classify_3_and_3bar(mix_infos)
    print("\nMIX27 A2-weights split as 3 ⊕ 3bar:")
    print("  3    =", [info.su3_weight for info in reps_3])
    print("  3bar =", [info.su3_weight for info in reps_3bar])

    # Fusion rules from root addition
    fusion = compute_root_addition_fusion(roots, orbits, orbit_infos)

    # A compact consistency check: E6 and A2 subsystems are closed under addition.
    e6_labels = {info.label for info in orbit_infos if info.size == 72}
    a2_labels = {info.label for info in orbit_infos if info.size == 1}
    e6_label = next(iter(e6_labels))
    a2_root_labels = sorted(a2_labels)
    print("\nClosure checks (root-addition):")
    print(
        "  E6 closed under addition? ",
        set(fusion.get(e6_label, {}).get(e6_label, {})).issubset(e6_labels),
    )
    a2_closed = True
    for la in a2_root_labels:
        for lb in a2_root_labels:
            outs = set(fusion.get(la, {}).get(lb, {}))
            if not outs.issubset(a2_labels):
                a2_closed = False
                break
    print("  A2 closed under addition? ", a2_closed)

    triples = compute_triples_alpha_beta_gamma_zero(roots, orbit_infos, idx_orb)
    print("\nMixed-root triples α+β+γ=0 (all three in MIX27):")
    print("  wsum_counts:", triples["wsum_counts"])

    # A2 action on mixed roots via root addition (ladder action in the Lie algebra picture).
    a2_infos = [info for info in orbit_infos if info.size == 1]
    mix_orb_indices = [info.orbit_index for info in orbit_infos if info.size == 27]
    label_by_orb = {info.orbit_index: info.label for info in orbit_infos}
    a2_action: Dict[str, Dict[str, Dict[str, int]]] = defaultdict(
        lambda: defaultdict(lambda: defaultdict(int))
    )
    for a2_info in a2_infos:
        delta_idx = orbits[a2_info.orbit_index][0]
        delta_key = root_key(roots[delta_idx])
        for src_orb in mix_orb_indices:
            for r_idx in orbits[src_orb]:
                s = tuple(delta_key[t] + root_key(roots[r_idx])[t] for t in range(8))
                k = root_to_index.get(s)
                if k is None:
                    continue
                dst_orb = idx_orb[k]
                a2_action[a2_info.label][label_by_orb[src_orb]][
                    label_by_orb[dst_orb]
                ] += 1

    # Print a compact view: for each A2 root, which MIX27 orbits it connects between (nonzero counts only).
    print("\nA2 ladder action on MIX27 (nonzero orbit-to-orbit transitions):")
    for a2_label in sorted(a2_action.keys()):
        transitions = []
        for src_label, outs in a2_action[a2_label].items():
            for dst_label, cnt in outs.items():
                if "MIX27" not in src_label or "MIX27" not in dst_label:
                    continue
                transitions.append((src_label, dst_label, cnt))
        transitions.sort(key=lambda x: (x[0], x[1]))
        print(f"  {a2_label}: {len(transitions)} transitions")
        for src_label, dst_label, cnt in transitions:
            print(f"    {src_label} -> {dst_label}: {cnt}")

    results = {
        "counts": {
            "e8_roots": int(len(roots)),
            "we6_orbit_sizes": [int(info.size) for info in orbit_infos],
        },
        "su3": {
            "alpha": SU3_ALPHA.tolist(),
            "beta": SU3_BETA.tolist(),
            "cartan_check": {
                "alpha_alpha": float(np.dot(SU3_ALPHA, SU3_ALPHA)),
                "beta_beta": float(np.dot(SU3_BETA, SU3_BETA)),
                "alpha_beta": float(np.dot(SU3_ALPHA, SU3_BETA)),
            },
        },
        "orbits": [
            {
                "orbit_index": info.orbit_index,
                "size": info.size,
                "su3_weight": list(info.su3_weight),
                "label": info.label,
            }
            for info in orbit_infos
        ],
        "mix27_split": {
            "three": [list(info.su3_weight) for info in reps_3],
            "threebar": [list(info.su3_weight) for info in reps_3bar],
        },
        "fusion": fusion,
        "a2_action_on_mix27": {
            a: {b: dict(c) for b, c in bb.items()} for a, bb in a2_action.items()
        },
        "triples_alpha_plus_beta_plus_gamma_eq_0": triples,
    }

    out_path = ROOT / "artifacts" / "e8_e6_a2_fusion.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"\nWrote {out_path}")


if __name__ == "__main__":
    main()
