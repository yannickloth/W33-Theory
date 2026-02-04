#!/usr/bin/env python3
"""
Solve for a consistent sign gauge for the E6 cubic tensor d_{ijk} from E8 data.

What we already have in this repo:
  - The *support* of the E6 cubic invariant on the 27 is exactly the 45 tritangent
    planes (meet-graph triangles) in a 27-orbit, and it lifts to 270 "mixed"
    E8 root triples in the (27,3) sector via the SU(3) epsilon (multiplicity 6).

What we still want:
  - A *deterministic* ±1 assignment compatible with a concrete sign convention for
    the E8 root-space bracket.

Approach:
  - Use a standard E8 lattice cocycle ε(α,β) in {±1}.
  - For ordered mixed triples (α,β,γ) with α+β+γ=0 (α in orbit A, β in orbit B, γ in orbit C),
    set a raw coupling sign s(α,β,γ) := ε(α,β).
  - Introduce gauge phases σ_a(i) for the three SU(3) colors a∈{A,B,C} and each E6 weight i∈{0..26},
    and unknown symmetric tensor signs d_T for each of the 45 unordered E6 triples T.

We enforce for every ordered coupling triple (i,j,k) (with colors fixed A,B,C):
    σ_A(i) σ_B(j) σ_C(k) * s(α_i^A, α_j^B, α_k^C) = d_{ {i,j,k} }.

This is a linear system over GF(2). We solve it and write a concrete gauge.

Outputs:
  artifacts/e6_cubic_sign_gauge_solution.json
"""

from __future__ import annotations

import importlib.util
import json
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np

ROOT = Path(__file__).resolve().parents[1]


def _load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Failed to load module from {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


cds = _load_module(ROOT / "tools" / "compute_double_sixes.py", "compute_double_sixes")
cocycle = _load_module(ROOT / "tools" / "e8_lattice_cocycle.py", "e8_lattice_cocycle")


SU3_ALPHA = np.array([1.0, -1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
SU3_BETA = np.array([0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, -1.0])


def k2(r: np.ndarray) -> Tuple[int, ...]:
    return tuple(int(round(2 * float(x))) for x in r.tolist())


def su3_weight(r: np.ndarray) -> Tuple[int, int]:
    return (
        int(round(float(np.dot(r, SU3_ALPHA)))),
        int(round(float(np.dot(r, SU3_BETA)))),
    )


def proj_to_su3(r: np.ndarray) -> np.ndarray:
    A = np.stack([SU3_ALPHA, SU3_BETA], axis=1)
    G = A.T @ A
    coeffs = np.linalg.solve(G, A.T @ r)
    return A @ coeffs


def e6_key(r: np.ndarray) -> Tuple[int, ...]:
    re6 = r - proj_to_su3(r)
    return tuple(int(round(2 * float(x))) for x in re6.tolist())


@dataclass(frozen=True)
class LinearSystemGF2:
    nvars: int
    rows: List[Tuple[int, int]]  # (mask over nvars, rhs bit)

    def solve(self) -> Tuple[bool, List[int], Dict[str, int]]:
        """
        Solve by Gaussian elimination over GF(2). Returns (ok, solution, stats).

        Solution uses 0 for free vars.
        """

        pivots: Dict[int, Tuple[int, int]] = {}
        inconsistent = False
        for mask, rhs in self.rows:
            m = mask
            r = rhs & 1
            while m:
                p = m.bit_length() - 1
                if p in pivots:
                    pm, pr = pivots[p]
                    m ^= pm
                    r ^= pr
                else:
                    pivots[p] = (m, r)
                    break
            if m == 0 and r == 1:
                inconsistent = True
                break

        if inconsistent:
            return False, [0] * self.nvars, {"rank": len(pivots), "inconsistent": 1}

        sol = [0] * self.nvars
        for p in sorted(pivots.keys(), reverse=True):
            m, r = pivots[p]
            rest = m & ~(1 << p)
            val = r
            while rest:
                q = rest & -rest
                idx = q.bit_length() - 1
                val ^= sol[idx]
                rest ^= q
            sol[p] = val

        return True, sol, {"rank": len(pivots), "inconsistent": 0}


def main() -> None:
    roots = cds.construct_e8_roots()
    orbits = cds.compute_we6_orbits(roots)
    orbit_sizes = [len(o) for o in orbits]
    assert sorted(orbit_sizes) == [1, 1, 1, 1, 1, 1, 27, 27, 27, 27, 27, 27, 72]

    idx_orb: Dict[int, int] = {}
    for oi, orb in enumerate(orbits):
        for v in orb:
            idx_orb[v] = oi

    root_index = {k2(roots[i]): i for i in range(len(roots))}

    mix_orbs = [oi for oi, sz in enumerate(orbit_sizes) if sz == 27]
    weights = {oi: su3_weight(roots[orbits[oi][0]]) for oi in mix_orbs}
    weights_3 = {(1, 0), (-1, 1), (0, -1)}

    # Fix a deterministic color order by sorting the three SU(3)=3 orbits by their weights.
    color_orbs = sorted(
        [oi for oi in mix_orbs if weights[oi] in weights_3], key=lambda x: weights[x]
    )
    assert len(color_orbs) == 3
    oa, ob, oc = color_orbs

    # Build E6 IDs (0..26) by E6 projection equality across these three color orbits.
    e6_groups: Dict[Tuple[int, ...], int] = {}
    root_to_e6id: Dict[int, int] = {}
    for oi in color_orbs:
        for r_idx in orbits[oi]:
            k = e6_key(roots[r_idx])
            if k not in e6_groups:
                e6_groups[k] = len(e6_groups)
            root_to_e6id[r_idx] = e6_groups[k]
    assert len(e6_groups) == 27

    # Map (color, e6id) -> root index and ensure it's a bijection per color orbit.
    color_root_by_e6id: List[List[int]] = [[-1] * 27 for _ in range(3)]
    for color, oi in enumerate(color_orbs):
        seen = set()
        for r_idx in orbits[oi]:
            e6id = root_to_e6id[r_idx]
            if color_root_by_e6id[color][e6id] != -1:
                raise RuntimeError("Non-unique E6 id inside a color orbit (unexpected)")
            color_root_by_e6id[color][e6id] = r_idx
            seen.add(e6id)
        if len(seen) != 27 or any(x == -1 for x in color_root_by_e6id[color]):
            raise RuntimeError(
                "Failed to build a full 27-bijection for this color orbit"
            )

    # Enumerate ordered couplings: roots from (oa,ob) determine root in oc by sum-to-zero.
    couplings: List[Tuple[int, int, int, int]] = []  # (i,j,k, raw_sign)
    for a_root in orbits[oa]:
        ka = k2(roots[a_root])
        i = root_to_e6id[a_root]
        for b_root in orbits[ob]:
            kb = k2(roots[b_root])
            j = root_to_e6id[b_root]
            need = tuple(-(ka[t] + kb[t]) for t in range(8))
            c_root = root_index.get(need)
            if c_root is None or idx_orb[c_root] != oc:
                continue
            k = root_to_e6id[c_root]
            raw = cocycle.epsilon_e8(ka, kb)  # ±1
            couplings.append((i, j, k, raw))

    assert len(couplings) == 270

    # Identify the 45 unordered E6 triples that occur (support of the cubic tensor).
    triples = sorted({tuple(sorted((i, j, k))) for (i, j, k, _) in couplings})
    assert len(triples) == 45
    triple_index = {t: idx for idx, t in enumerate(triples)}

    # Build linear system:
    # vars: sigma(color,i) for 3*27 = 81, then d_T for 45: total 126
    n_sigma = 81
    n_d = 45
    nvars = n_sigma + n_d

    def var_sigma(color: int, e6id: int) -> int:
        return color * 27 + e6id

    def var_d(t: Tuple[int, int, int]) -> int:
        return n_sigma + triple_index[t]

    rows: List[Tuple[int, int]] = []
    for i, j, k, raw_sign in couplings:
        t = tuple(sorted((i, j, k)))
        mask = 0
        mask ^= 1 << var_sigma(0, i)
        mask ^= 1 << var_sigma(1, j)
        mask ^= 1 << var_sigma(2, k)
        mask ^= 1 << var_d(t)
        rhs = cocycle.sign_to_bit(raw_sign)
        rows.append((mask, rhs))

    ok, sol, stats = LinearSystemGF2(nvars=nvars, rows=rows).solve()
    if not ok:
        raise RuntimeError(
            "Inconsistent sign gauge system (unexpected if cocycle is valid)"
        )

    sigma_bits = [[sol[var_sigma(c, i)] for i in range(27)] for c in range(3)]
    d_bits = [sol[n_sigma + t] for t in range(45)]
    d_signs = [cocycle.bit_to_sign(b) for b in d_bits]

    # Also attempt a gauge where all d_T are +1 (i.e. all d-bits forced to 0).
    rows_all_plus: List[Tuple[int, int]] = []
    for i, j, k, raw_sign in couplings:
        mask = 0
        mask ^= 1 << var_sigma(0, i)
        mask ^= 1 << var_sigma(1, j)
        mask ^= 1 << var_sigma(2, k)
        rhs = cocycle.sign_to_bit(raw_sign)
        rows_all_plus.append((mask, rhs))
    ok_plus, sol_plus, stats_plus = LinearSystemGF2(
        nvars=n_sigma, rows=rows_all_plus
    ).solve()

    # Summaries
    d_dist = Counter(d_signs)
    out = {
        "status": "ok",
        "colors": {
            "orbits": [int(oa), int(ob), int(oc)],
            "weights": [list(weights[oa]), list(weights[ob]), list(weights[oc])],
        },
        "counts": {
            "ordered_couplings": 270,
            "unordered_triples": 45,
            "variables": {"sigma": n_sigma, "d": n_d, "total": nvars},
            "rank": int(stats["rank"]),
            "rank_all_plus": int(stats_plus["rank"]),
        },
        "solution": {
            "sigma_bits": sigma_bits,
            "d_triples": [
                {"triple": list(t), "sign": int(d_signs[idx])}
                for idx, t in enumerate(triples)
            ],
            "d_sign_distribution": {str(int(k)): int(v) for k, v in d_dist.items()},
        },
        "all_plus_gauge": {
            "possible": bool(ok_plus),
            "sigma_bits": (
                [[sol_plus[var_sigma(c, i)] for i in range(27)] for c in range(3)]
                if ok_plus
                else None
            ),
        },
    }

    out_path = ROOT / "artifacts" / "e6_cubic_sign_gauge_solution.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print("PASS: solved sign-gauge system for E6 cubic tensor.")
    print(f"  all-plus gauge possible? {ok_plus}")
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
