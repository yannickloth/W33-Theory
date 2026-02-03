#!/usr/bin/env python3
"""
Verify W(E6) preserves the signed E6 cubic tensor (up to a diagonal gauge).

We have a concrete ±1 assignment on the 45 tritangent-plane monomials
  P(x) = Σ_{(i,j,k) in T} d_{ijk} x_i x_j x_k
computed in `artifacts/e6_cubic_sign_gauge_solution.json`.

The Weyl group W(E6) acts on the 27 weights as a permutation (computed directly
from reflections in E6 simple roots). In a fixed coordinate basis, preservation
of P generally requires a *signed* permutation action:
  x_i  ->  (-1)^{t_i} x_{p(i)}

For each E6 simple reflection generator we solve for the diagonal signs t_i
so that P is invariant **up to an overall scalar ±1** (since the invariant cubic
is unique up to scale anyway).

Outputs:
  artifacts/e6_cubic_invariance_we6.json
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


def sign_to_bit(s: int) -> int:
    if s not in (-1, 1):
        raise ValueError("Expected ±1 sign")
    return 1 if s == -1 else 0


def bit_to_sign(b: int) -> int:
    if b not in (0, 1):
        raise ValueError("Expected bit 0/1")
    return -1 if b else 1


@dataclass(frozen=True)
class LinearSystemGF2:
    nvars: int
    rows: List[Tuple[int, int]]  # (mask, rhs_bit)

    def solve(self) -> Tuple[bool, List[int], Dict[str, int]]:
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


def build_e6_generator_perms_on_first_27_orbit() -> (
    Tuple[np.ndarray, List[Tuple[int, ...]]]
):
    raise RuntimeError("Deprecated (use build_we6_perms_on_e6ids)")


def build_we6_perms_on_e6ids() -> List[Tuple[int, ...]]:
    """
    Compute the 6 E6 simple reflection generators as permutations of the 27 E6-weights (e6ids).

    The e6ids here are exactly the ones used in `artifacts/e6_cubic_sign_gauge_solution.json`:
    they are defined by E6 projection equality across the three SU(3)=3 color 27-orbits.
    """

    # Recompute the same e6id dictionary as `tools/solve_e6_cubic_sign_gauge.py`.
    roots = cds.construct_e8_roots()
    orbits = cds.compute_we6_orbits(roots)
    orbit_sizes = [len(o) for o in orbits]
    assert sorted(orbit_sizes) == [1, 1, 1, 1, 1, 1, 27, 27, 27, 27, 27, 27, 72]

    su3_alpha = np.array([1.0, -1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
    su3_beta = np.array([0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, -1.0])

    def su3_weight(r: np.ndarray) -> Tuple[int, int]:
        return (
            int(round(float(np.dot(r, su3_alpha)))),
            int(round(float(np.dot(r, su3_beta)))),
        )

    def proj_to_su3(r: np.ndarray) -> np.ndarray:
        A = np.stack([su3_alpha, su3_beta], axis=1)
        G = A.T @ A
        coeffs = np.linalg.solve(G, A.T @ r)
        return A @ coeffs

    def e6_key(r: np.ndarray) -> Tuple[int, ...]:
        re6 = r - proj_to_su3(r)
        return tuple(int(round(2 * float(x))) for x in re6.tolist())

    mix_orbs = [oi for oi, sz in enumerate(orbit_sizes) if sz == 27]
    weights = {oi: su3_weight(roots[orbits[oi][0]]) for oi in mix_orbs}
    weights_3 = {(1, 0), (-1, 1), (0, -1)}
    color_orbs = sorted(
        [oi for oi in mix_orbs if weights[oi] in weights_3], key=lambda x: weights[x]
    )
    assert len(color_orbs) == 3

    # Build E6 ids.
    e6_groups: Dict[Tuple[int, ...], int] = {}
    root_to_e6id: Dict[int, int] = {}
    for oi in color_orbs:
        for r_idx in orbits[oi]:
            k = e6_key(roots[r_idx])
            if k not in e6_groups:
                e6_groups[k] = len(e6_groups)
            root_to_e6id[r_idx] = e6_groups[k]
    assert len(e6_groups) == 27

    # Choose deterministic representatives for the 27 weights from the first color orbit.
    rep_root_by_e6id = [-1] * 27
    first_color_orb = color_orbs[0]
    for r_idx in orbits[first_color_orb]:
        rep_root_by_e6id[root_to_e6id[r_idx]] = r_idx
    if any(x == -1 for x in rep_root_by_e6id):
        raise RuntimeError("Failed to pick one representative per e6id")

    # For each E6 simple root, reflect reps and map back to e6id.
    perms: List[Tuple[int, ...]] = []
    for alpha in cds.E6_SIMPLE_ROOTS:
        perm = []
        for i in range(27):
            r = roots[rep_root_by_e6id[i]]
            img = cds.weyl_reflect(r, alpha)
            k = cds.snap_to_lattice(img)
            # find the actual root index by searching (cheap: 240 items)
            # Use doubled-int key for deterministic matching.
            kk = tuple(int(round(2 * float(x))) for x in k)
            # Build root_index lazily once.
            perm.append(kk)  # placeholder; replaced below

        perms.append(tuple(perm))

    # Build root lookup once.
    root_index = {
        tuple(int(round(2 * float(x))) for x in roots[i]): i for i in range(len(roots))
    }

    out: List[Tuple[int, ...]] = []
    for perm_keys in perms:
        p = []
        for kk in perm_keys:
            ridx = root_index.get(kk)
            if ridx is None:
                raise RuntimeError("Reflected root not found in E8 root list")
            e6id = root_to_e6id.get(ridx)
            if e6id is None:
                # W(E6) should preserve SU3 weight, so reps from a 3-color orbit should
                # map within that same color orbit, hence have an e6id assignment.
                raise RuntimeError(
                    "Reflected root left the 3-color 27-orbits (unexpected)"
                )
            p.append(e6id)
        if sorted(p) != list(range(27)):
            raise RuntimeError("Generator did not induce a permutation on e6ids")
        out.append(tuple(p))

    return out


def load_signed_triples() -> (
    Tuple[List[Tuple[int, int, int]], Dict[Tuple[int, int, int], int]]
):
    path = ROOT / "artifacts" / "e6_cubic_sign_gauge_solution.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    triples: List[Tuple[int, int, int]] = []
    d: Dict[Tuple[int, int, int], int] = {}
    for ent in data["solution"]["d_triples"]:
        t = tuple(int(x) for x in ent["triple"])
        t = tuple(sorted(t))
        s = int(ent["sign"])
        if s not in (-1, 1):
            raise ValueError("Bad sign in artifact")
        triples.append(t)
        d[t] = s
    triples = sorted(set(triples))
    if len(triples) != 45:
        raise ValueError("Expected 45 signed triples")
    return triples, d


def solve_signed_perm_for_cubic(
    triples: List[Tuple[int, int, int]],
    d: Dict[Tuple[int, int, int], int],
    p: Tuple[int, ...],
    allow_global: bool,
) -> Tuple[bool, Dict[str, object]]:
    """
    Solve for diagonal bits t_i (and optional global bit g) such that:
      d_{ijk} = (-1)^g * (-1)^{t_i+t_j+t_k} * d_{p(i)p(j)p(k)}.
    """

    if len(p) != 27:
        raise ValueError("Expected permutation on 27")
    nvars = 27 + (1 if allow_global else 0)

    def var_t(i: int) -> int:
        return i

    def var_g() -> int:
        if not allow_global:
            raise RuntimeError
        return 27

    rows: List[Tuple[int, int]] = []
    for i, j, k in triples:
        tp = tuple(sorted((p[i], p[j], p[k])))
        rhs = sign_to_bit(d[(i, j, k)]) ^ sign_to_bit(d[tp])
        mask = 0
        mask ^= 1 << var_t(i)
        mask ^= 1 << var_t(j)
        mask ^= 1 << var_t(k)
        if allow_global:
            mask ^= 1 << var_g()
        rows.append((mask, rhs))

    ok, sol, stats = LinearSystemGF2(nvars=nvars, rows=rows).solve()
    if not ok:
        return False, {"ok": False, "stats": stats}

    t_bits = sol[:27]
    g_bit = sol[27] if allow_global else 0

    # Verify.
    for i, j, k in triples:
        tp = tuple(sorted((p[i], p[j], p[k])))
        lhs = sign_to_bit(d[(i, j, k)])
        rhs = sign_to_bit(d[tp]) ^ t_bits[i] ^ t_bits[j] ^ t_bits[k] ^ g_bit
        if lhs != rhs:
            return False, {"ok": False, "stats": stats, "verification_failed": True}

    return True, {
        "ok": True,
        "stats": stats,
        "t_bits": t_bits,
        "g_bit": g_bit if allow_global else None,
    }


def main() -> None:
    triples, d = load_signed_triples()
    gens = build_we6_perms_on_e6ids()

    gen_results = []
    for gi, p in enumerate(gens):
        strict_ok, strict = solve_signed_perm_for_cubic(
            triples, d, p, allow_global=False
        )
        proj_ok, proj = solve_signed_perm_for_cubic(triples, d, p, allow_global=True)
        gen_results.append(
            {
                "generator_index": gi,
                "strict_ok": bool(strict_ok),
                "projective_ok": bool(proj_ok),
                "strict": strict if strict_ok else strict,
                "projective": proj if proj_ok else proj,
            }
        )

    strict_count = sum(1 for r in gen_results if r["strict_ok"])
    proj_count = sum(1 for r in gen_results if r["projective_ok"])
    print(f"W(E6) simple generators: strict invariance solved for {strict_count}/6")
    print(f"W(E6) simple generators: up-to-global invariance solved for {proj_count}/6")

    # Summarize projective global signs.
    gdist = Counter()
    for r in gen_results:
        if r["projective_ok"]:
            gdist[int(r["projective"]["g_bit"])] += 1
    out = {
        "status": "ok",
        "inputs": {
            "signed_triples_artifact": "artifacts/e6_cubic_sign_gauge_solution.json",
        },
        "counts": {
            "triples": 45,
            "generators": 6,
            "strict_solved": int(strict_count),
            "projective_solved": int(proj_count),
            "projective_global_bit_distribution": dict(gdist),
        },
        "generators": gen_results,
    }

    out_path = ROOT / "artifacts" / "e6_cubic_invariance_we6.json"
    out_path.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
