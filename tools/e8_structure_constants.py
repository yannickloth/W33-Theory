#!/usr/bin/env python3
"""
E8 structure-constant mining for the E8 → E6 ⊕ A2(=SU3) decomposition.

Goal:
  1) Build an orbit-level "fusion table" for the Lie bracket using the root-addition rule:
       [e_α, e_β] ≠ 0  iff  α+β is a root.
  2) Refine it with Chevalley basis magnitudes |N_{α,β}| derived from root strings:
       If α,β,α+β are roots, let p = max{k≥0 : β - k α is a root}.
       Then |N_{α,β}| = p+1.  (Standard Chevalley normalization; sign ignored here.)
  3) Mine cubic "candidate couplings" among the mixed roots:
       α+β+γ=0  with α,β,γ in the 6×27 mixed roots.

This is purely algebraic (no dynamics): it produces rigid selection rules and coupling
combinatorics consistent with the established branching
  248 = (78,1) ⊕ (1,8) ⊕ (27,3) ⊕ (\bar27,\bar3).
"""

from __future__ import annotations

import importlib.util
import json
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

import numpy as np

ROOT = Path(__file__).resolve().parents[1]


def _load_compute_double_sixes():
    path = ROOT / "tools" / "compute_double_sixes.py"
    spec = importlib.util.spec_from_file_location("compute_double_sixes", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Failed to load module from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_cds = _load_compute_double_sixes()
construct_e8_roots = _cds.construct_e8_roots
compute_we6_orbits = _cds.compute_we6_orbits


# A2 (= su(3)) simple roots orthogonal to the E6 subdiagram.
SU3_ALPHA = np.array([1.0, -1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
SU3_BETA = np.array([0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, -1.0])


def key2(r: np.ndarray) -> Tuple[int, ...]:
    """Integral key for a root: use 2*r so all coordinates are integers."""
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


def cheva_abs_N(
    alpha_k: np.ndarray, beta_k: np.ndarray, root_index: Dict[Tuple[int, ...], int]
) -> int:
    """
    |N_{α,β}| for Chevalley basis, from the root string through β in direction α.

    Assumes α,β,α+β are roots (caller checks). Uses p = max{k≥0 : β - k α is root}.
    """
    p = 0
    while True:
        cand = tuple((beta_k - (p + 1) * alpha_k).tolist())
        if cand in root_index:
            p += 1
            continue
        break
    return p + 1


def classify_mix_rep(weight: Tuple[int, int]) -> str:
    weights_3 = {(1, 0), (-1, 1), (0, -1)}
    weights_3bar = {(0, 1), (1, -1), (-1, 0)}
    if weight in weights_3:
        return "3"
    if weight in weights_3bar:
        return "3bar"
    return "?"


def main() -> None:
    roots = construct_e8_roots()
    orbits = compute_we6_orbits(roots)
    orbit_infos = build_orbit_infos(roots, orbits)
    idx_orb = index_by_orbit(orbits)
    label_by_orb = {info.orbit_index: info.label for info in orbit_infos}
    kind_by_orb = {
        info.orbit_index: (
            "E6" if info.size == 72 else "A2" if info.size == 1 else "MIX27"
        )
        for info in orbit_infos
    }
    w_by_orb = {info.orbit_index: info.su3_weight for info in orbit_infos}

    # Precompute integral keys for fast arithmetic.
    keys = np.array(
        [[int(round(2 * float(x))) for x in roots[i]] for i in range(len(roots))],
        dtype=int,
    )
    root_index = {tuple(keys[i].tolist()): i for i in range(len(roots))}

    sizes = sorted((len(o) for o in orbits), reverse=True)
    print("W(E6) orbit sizes:", sizes)

    # Orbit roster
    print("\nOrbit labels:")
    for info in sorted(
        orbit_infos, key=lambda x: (-x.size, x.su3_weight, x.orbit_index)
    ):
        extra = ""
        if info.size == 27:
            extra = f"  rep={classify_mix_rep(info.su3_weight)}"
        print(f"  orbit {info.orbit_index:2d}: {info.label}{extra}")

    # Fusion tables.
    fusion_counts: Dict[str, Dict[str, Counter[str]]] = defaultdict(
        lambda: defaultdict(Counter)
    )
    fusion_N_dist: Dict[str, Dict[str, Dict[str, Counter[int]]]] = defaultdict(
        lambda: defaultdict(lambda: defaultdict(Counter))
    )
    N_values = Counter()
    kind_fusion: Dict[str, Dict[str, Counter[str]]] = defaultdict(
        lambda: defaultdict(Counter)
    )

    # Restrict to unordered pairs; record orbit-level coupling counts.
    for i in range(len(roots)):
        oi = idx_orb[i]
        li = label_by_orb[oi]
        ki = keys[i]
        for j in range(i + 1, len(roots)):
            oj = idx_orb[j]
            lj = label_by_orb[oj]
            s_key = tuple((ki + keys[j]).tolist())
            k = root_index.get(s_key)
            if k is None:
                continue
            ok = idx_orb[k]
            lk = label_by_orb[ok]
            kind_i = kind_by_orb[oi]
            kind_j = kind_by_orb[oj]
            kind_k = kind_by_orb[ok]

            # Compute |N_{α,β}| (ignoring sign).
            N = cheva_abs_N(ki, keys[j], root_index)
            N_values[N] += 1

            fusion_counts[li][lj][lk] += 1
            fusion_counts[lj][li][
                lk
            ] += 1  # add antisymmetric orientation for orbit-level bookkeeping
            fusion_N_dist[li][lj][lk][N] += 1
            fusion_N_dist[lj][li][lk][N] += 1
            kind_fusion[kind_i][kind_j][kind_k] += 1
            kind_fusion[kind_j][kind_i][kind_k] += 1

    print("\nChevalley |N_{α,β}| distribution (unordered α,β with α+β a root):")
    print(" ", dict(sorted(N_values.items())))
    print("\nKind-level fusion (counts are oriented pairs (α,β)):")
    for a in sorted(kind_fusion.keys()):
        for b in sorted(kind_fusion[a].keys()):
            outs = dict(kind_fusion[a][b])
            if outs:
                print(f"  {a} x {b} -> {outs}")

    # Mixed-root triple mining: α+β+γ=0 among MIX27 roots.
    mix_orb_indices = [info.orbit_index for info in orbit_infos if info.size == 27]
    mix_indices = [i for i in range(len(roots)) if idx_orb[i] in mix_orb_indices]

    triple_weight_sums = Counter()
    triple_weight_multisets = Counter()
    triple_rep_types = Counter()
    triple_orbit_multisets = Counter()
    triple_weight_distinctness = Counter()

    for a_pos, i in enumerate(mix_indices):
        ki = keys[i]
        wi = w_by_orb[idx_orb[i]]
        rep_i = classify_mix_rep(wi)
        for j in mix_indices[a_pos:]:
            kj = keys[j]
            wj = w_by_orb[idx_orb[j]]
            rep_j = classify_mix_rep(wj)
            need = tuple((-(ki + kj)).tolist())
            k = root_index.get(need)
            if k is None:
                continue
            if k not in root_index.values():
                continue
            if idx_orb[k] not in mix_orb_indices:
                continue
            wk = w_by_orb[idx_orb[k]]
            rep_k = classify_mix_rep(wk)
            wsum = (wi[0] + wj[0] + wk[0], wi[1] + wj[1] + wk[1])
            triple_weight_sums[wsum] += 1
            triple_weight_multisets[str(tuple(sorted((wi, wj, wk))))] += 1
            triple_rep_types[str(tuple(sorted((rep_i, rep_j, rep_k))))] += 1
            triple_orbit_multisets[
                str(tuple(sorted((idx_orb[i], idx_orb[j], idx_orb[k]))))
            ] += 1
            triple_weight_distinctness[str(len({wi, wj, wk}))] += 1

    print("\nMixed triples α+β+γ=0 (MIX27 only):")
    print(
        "  weight-sum counts:",
        {f"{k[0]},{k[1]}": v for k, v in triple_weight_sums.items()},
    )
    print("  rep-type counts:", dict(triple_rep_types))
    print("  distinct SU3-weights per triple:", dict(triple_weight_distinctness))
    if len(triple_orbit_multisets) <= 16:
        print("  orbit-multiset counts:", dict(triple_orbit_multisets))

    # Write JSON artifact.
    out_path = ROOT / "artifacts" / "e8_structure_constants.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)

    results = {
        "counts": {
            "e8_roots": int(len(roots)),
            "we6_orbit_sizes": [int(len(o)) for o in orbits],
        },
        "su3": {
            "alpha": SU3_ALPHA.tolist(),
            "beta": SU3_BETA.tolist(),
            "cartan_inner_products": {
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
                "mix_rep": (
                    classify_mix_rep(info.su3_weight) if info.size == 27 else None
                ),
            }
            for info in orbit_infos
        ],
        "fusion_counts": {
            a: {b: dict(c) for b, c in bb.items()} for a, bb in fusion_counts.items()
        },
        "fusion_counts_by_kind": {
            a: {b: dict(c) for b, c in bb.items()} for a, bb in kind_fusion.items()
        },
        "fusion_chevalley_absN_distributions": {
            a: {
                b: {c: {str(n): int(v) for n, v in nn.items()} for c, nn in cc.items()}
                for b, cc in bb.items()
            }
            for a, bb in fusion_N_dist.items()
        },
        "chevalley_absN_global_distribution": {
            str(k): int(v) for k, v in N_values.items()
        },
        "mixed_triples": {
            "weight_sum_counts": {
                f"{k[0]},{k[1]}": int(v) for k, v in triple_weight_sums.items()
            },
            "weight_multiset_counts": dict(triple_weight_multisets),
            "rep_type_counts": dict(triple_rep_types),
            "orbit_multiset_counts": dict(triple_orbit_multisets),
            "distinct_su3_weight_count_distribution": dict(triple_weight_distinctness),
        },
        "notes": {
            "lie_bracket_nonzero_rule": "Nonzero iff alpha+beta is a root (Chevalley basis, root vectors).",
            "chevalley_absN_rule": "|N_{α,β}| = p+1 where p=max{k>=0: β-kα is a root}, assuming α+β is a root.",
        },
    }

    out_path.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"\nWrote {out_path}")


if __name__ == "__main__":
    main()
