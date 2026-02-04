#!/usr/bin/env python3
"""
Solve the W(E6) equivariance gauge on the signed E6 cubic tensor.

We have:
  - a signed cubic tensor d_{ijk} on 45 unordered triples of E6-weights i,j,k,
    from `artifacts/e6_cubic_sign_gauge_solution.json`.
  - a concrete permutation action p on the 27 weights induced by each E6 simple reflection
    (computed directly by reflecting E8 mixed roots and collapsing to E6 projections).

Since the cubic invariant lives in (27,3) with an SU(3) epsilon contraction, the Weyl action
can rephase the three color components independently. So we solve, for each generator, whether
there exist bits:
  t0(i), t1(i), t2(i)  (i=0..26)  and a global bit g
such that for all triads (i,j,k) with d_{ijk}≠0:
  d_{p(i)p(j)p(k)} = (-1)^g * (-1)^{t0(i)+t1(j)+t2(k)} * d_{ijk}.

This is a linear system over GF(2), with 82 variables and 45 constraints.

Output:
  artifacts/we6_cubic_equivariance_gauges.json
"""

from __future__ import annotations

import importlib.util
import json
import sys
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

SU3_ALPHA = np.array([1.0, -1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
SU3_BETA = np.array([0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, -1.0])


def k2(r: np.ndarray) -> Tuple[int, ...]:
    return tuple(int(round(2 * float(x))) for x in r.tolist())


def sign_to_bit(s: int) -> int:
    if s not in (-1, 1):
        raise ValueError("Expected ±1 sign")
    return 1 if s == -1 else 0


def bit_to_sign(b: int) -> int:
    if b not in (0, 1):
        raise ValueError("Expected bit 0/1")
    return -1 if b else 1


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
    rows: List[Tuple[int, int]]  # (mask, rhs)

    def solve(self) -> Tuple[bool, List[int], int]:
        pivots: Dict[int, Tuple[int, int]] = {}
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
                return False, [0] * self.nvars, len(pivots)

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
        return True, sol, len(pivots)


def load_d_triples() -> Dict[Tuple[int, int, int], int]:
    data = json.loads(
        (ROOT / "artifacts" / "e6_cubic_sign_gauge_solution.json").read_text(
            encoding="utf-8"
        )
    )
    d: Dict[Tuple[int, int, int], int] = {}
    for ent in data["solution"]["d_triples"]:
        t = tuple(sorted(int(x) for x in ent["triple"]))
        d[t] = int(ent["sign"])
    if len(d) != 45:
        raise RuntimeError("Expected 45 d-triples")
    return d


def build_we6_generator_perms_on_e6ids() -> List[Tuple[int, ...]]:
    roots = cds.construct_e8_roots()
    orbits = cds.compute_we6_orbits(roots)
    orbit_sizes = [len(o) for o in orbits]
    assert sorted(orbit_sizes) == [1, 1, 1, 1, 1, 1, 27, 27, 27, 27, 27, 27, 72]

    idx_orb: Dict[int, int] = {}
    for oi, orb in enumerate(orbits):
        for v in orb:
            idx_orb[v] = oi

    mix_orbs = [oi for oi, sz in enumerate(orbit_sizes) if sz == 27]
    weights = {oi: su3_weight(roots[orbits[oi][0]]) for oi in mix_orbs}
    weights_3 = {(1, 0), (-1, 1), (0, -1)}
    color_orbs = sorted(
        [oi for oi in mix_orbs if weights[oi] in weights_3], key=lambda x: weights[x]
    )
    assert len(color_orbs) == 3
    base_orb = color_orbs[0]

    e6_groups: Dict[Tuple[int, ...], int] = {}
    root_to_e6id: Dict[int, int] = {}
    for oi in color_orbs:
        for ridx in orbits[oi]:
            k = e6_key(roots[ridx])
            if k not in e6_groups:
                e6_groups[k] = len(e6_groups)
            root_to_e6id[ridx] = e6_groups[k]
    assert len(e6_groups) == 27

    # Representatives from base color orbit.
    rep_root_by_e6id = [-1] * 27
    for ridx in orbits[base_orb]:
        rep_root_by_e6id[root_to_e6id[ridx]] = ridx
    if any(x == -1 for x in rep_root_by_e6id):
        raise RuntimeError("Missing representative root for some e6id")

    root_index = {k2(roots[i]): i for i in range(len(roots))}

    perms: List[Tuple[int, ...]] = []
    for alpha in cds.E6_SIMPLE_ROOTS:
        perm = []
        for i in range(27):
            r = roots[rep_root_by_e6id[i]]
            img = cds.weyl_reflect(r, alpha)
            kk = tuple(int(round(2 * float(x))) for x in cds.snap_to_lattice(img))
            img_idx = root_index.get(kk)
            if img_idx is None or idx_orb[img_idx] != base_orb:
                raise RuntimeError(
                    "Reflection moved representative out of base orbit (unexpected)"
                )
            perm.append(root_to_e6id[img_idx])
        if sorted(perm) != list(range(27)):
            raise RuntimeError("Not a permutation on e6ids")
        perms.append(tuple(perm))
    return perms


def main() -> None:
    d = load_d_triples()
    triples = sorted(d.keys())
    gens = build_we6_generator_perms_on_e6ids()

    # Variable indexing: t0(i), t1(i), t2(i) (81) + g (1) = 82
    def var_t(color: int, i: int) -> int:
        return color * 27 + i

    var_g = 81

    out_gens = []
    all_ok = True
    for gi, p in enumerate(gens):
        rows: List[Tuple[int, int]] = []
        for i, j, k in triples:
            tp = tuple(sorted((p[i], p[j], p[k])))
            rhs = sign_to_bit(d[tp]) ^ sign_to_bit(d[(i, j, k)])
            mask = 0
            mask ^= 1 << var_t(0, i)
            mask ^= 1 << var_t(1, j)
            mask ^= 1 << var_t(2, k)
            mask ^= 1 << var_g
            rows.append((mask, rhs))

        ok, sol, rank = LinearSystemGF2(nvars=82, rows=rows).solve()
        all_ok &= ok
        out_gens.append(
            {
                "generator_index": int(gi),
                "ok": bool(ok),
                "rank": int(rank),
                "g_bit": int(sol[var_g]) if ok else None,
                "t_bits_by_color": [sol[0:27], sol[27:54], sol[54:81]] if ok else None,
            }
        )

    out = {
        "status": "ok",
        "counts": {"generators": 6, "all_ok": bool(all_ok)},
        "generators": out_gens,
    }
    out_path = ROOT / "artifacts" / "we6_cubic_equivariance_gauges.json"
    out_path.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(
        "PASS" if all_ok else "FAIL",
        "Solved color-gauge equivariance for all generators.",
    )
    print("Wrote", out_path)


if __name__ == "__main__":
    main()
