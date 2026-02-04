#!/usr/bin/env python3
"""
Compute a W(E6)-invariant gauge for the E6 cubic tensor by killing μ-signs in the 27-weight action.

We have a concrete Chevalley/cocycle basis for E8 root vectors. For each E6 simple reflection
generator s_α (as n_α(1)), the action on root vectors in a fixed 27-orbit is:
    s_α(e_β) = μ(β) e_{s_α β},  μ(β) ∈ {±1}.

Because the 27 is minuscule (weight multiplicities 1), the induced W(E6) action on the 27-weight
spaces is monomial (signed permutation). We can choose a diagonal gauge to remove these signs:
find a(β) and constants c_g so that in the rephased basis
    f_β := (-1)^{a(β)} e_β
the generators act as pure permutations (no β-dependent sign):
    s_g(f_β) = (-1)^{c_g} f_{gβ}.

We solve this as a GF(2) linear system separately on each of the three SU(3)=3 color 27-orbits.
Then we recompute the 45 E6 cubic coefficients d_t (triads) in that gauge, and verify that
the induced permutation action preserves d_t exactly (up to a global sign per generator).

Outputs:
  artifacts/e6_cubic_weyl_invariant_gauge.json
"""

from __future__ import annotations

import importlib.util
import json
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from fractions import Fraction
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


def sign_to_bit(s: int) -> int:
    return 1 if s == -1 else 0


def bit_to_sign(b: int) -> int:
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


def cheva_abs_N(
    alpha_k2: Tuple[int, ...],
    beta_k2: Tuple[int, ...],
    root_index: Dict[Tuple[int, ...], int],
) -> int:
    p = 0
    while True:
        cand = tuple(beta_k2[i] - (p + 1) * alpha_k2[i] for i in range(8))
        if cand in root_index:
            p += 1
            continue
        break
    return p + 1


def N(
    alpha_k2: Tuple[int, ...],
    beta_k2: Tuple[int, ...],
    root_index: Dict[Tuple[int, ...], int],
) -> int:
    s = tuple(alpha_k2[i] + beta_k2[i] for i in range(8))
    if s not in root_index:
        return 0
    return int(
        cocycle.epsilon_e8(alpha_k2, beta_k2)
        * cheva_abs_N(alpha_k2, beta_k2, root_index)
    )


def root_string_pq(
    beta_k2: Tuple[int, ...],
    alpha_k2: Tuple[int, ...],
    root_index: Dict[Tuple[int, ...], int],
) -> Tuple[int, int]:
    p = 0
    while True:
        cand = tuple(beta_k2[i] - (p + 1) * alpha_k2[i] for i in range(8))
        if cand in root_index:
            p += 1
            continue
        break
    q = 0
    while True:
        cand = tuple(beta_k2[i] + (q + 1) * alpha_k2[i] for i in range(8))
        if cand in root_index:
            q += 1
            continue
        break
    return p, q


def mat_mul(A: List[List[Fraction]], B: List[List[Fraction]]) -> List[List[Fraction]]:
    n = len(A)
    m = len(B[0])
    k = len(B)
    out = [[Fraction(0) for _ in range(m)] for _ in range(n)]
    for i in range(n):
        for j in range(m):
            s = Fraction(0)
            for t in range(k):
                s += A[i][t] * B[t][j]
            out[i][j] = s
    return out


def mat_eye(n: int) -> List[List[Fraction]]:
    return [
        [Fraction(1) if i == j else Fraction(0) for j in range(n)] for i in range(n)
    ]


def mat_pow(A: List[List[Fraction]], e: int) -> List[List[Fraction]]:
    if e == 0:
        return mat_eye(len(A))
    out = mat_eye(len(A))
    cur = A
    ee = e
    while ee:
        if ee & 1:
            out = mat_mul(cur, out)
        ee >>= 1
        if ee:
            cur = mat_mul(cur, cur)
    return out


def exp_nilpotent(M: List[List[Fraction]]) -> List[List[Fraction]]:
    n = len(M)
    out = mat_eye(n)
    fact = 1
    for k in range(1, n + 1):
        fact *= k
        P = mat_pow(M, k)
        for i in range(n):
            for j in range(n):
                out[i][j] += P[i][j] / fact
    return out


def apply_mat(M: List[List[Fraction]], v: List[Fraction]) -> List[Fraction]:
    n = len(M)
    out = [Fraction(0) for _ in range(n)]
    for i in range(n):
        s = Fraction(0)
        for j in range(n):
            s += M[i][j] * v[j]
        out[i] = s
    return out


def weyl_mu(
    alpha_k2: Tuple[int, ...],
    beta_k2: Tuple[int, ...],
    root_index: Dict[Tuple[int, ...], int],
) -> Tuple[Tuple[int, ...], int]:
    p, q = root_string_pq(beta_k2, alpha_k2, root_index)
    string = [
        tuple(beta_k2[i] + s * alpha_k2[i] for i in range(8)) for s in range(-p, q + 1)
    ]
    pos = {r: idx for idx, r in enumerate(string)}
    n = len(string)

    minus_alpha_k2 = tuple(-x for x in alpha_k2)
    E = [[Fraction(0) for _ in range(n)] for _ in range(n)]
    F = [[Fraction(0) for _ in range(n)] for _ in range(n)]
    for r, gamma in enumerate(string):
        gp = tuple(gamma[i] + alpha_k2[i] for i in range(8))
        if gp in pos:
            c = N(alpha_k2, gamma, root_index)
            E[pos[gp]][r] = Fraction(c)
        gm = tuple(gamma[i] - alpha_k2[i] for i in range(8))
        if gm in pos:
            c = N(minus_alpha_k2, gamma, root_index)
            F[pos[gm]][r] = Fraction(c)

    expE = exp_nilpotent(E)
    Fneg = [[-x for x in row] for row in F]
    expFneg = exp_nilpotent(Fneg)
    w = mat_mul(expE, mat_mul(expFneg, expE))

    v0 = [Fraction(0) for _ in range(n)]
    v0[p] = Fraction(1)
    v1 = apply_mat(w, v0)

    nz = [(i, v) for i, v in enumerate(v1) if v != 0]
    if len(nz) != 1:
        raise RuntimeError(f"Unexpected Weyl action support size: {nz}")
    idx, coeff = nz[0]
    if coeff not in (Fraction(1), Fraction(-1)):
        raise RuntimeError(f"Unexpected Weyl action coefficient: {coeff}")
    return string[idx], (1 if coeff == Fraction(1) else -1)


@dataclass(frozen=True)
class LinearSystemGF2:
    nvars: int
    rows: List[Tuple[int, int]]

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


def main() -> None:
    roots = cds.construct_e8_roots()
    orbits = cds.compute_we6_orbits(roots)
    orbit_sizes = [len(o) for o in orbits]
    idx_orb: Dict[int, int] = {}
    for oi, orb in enumerate(orbits):
        for v in orb:
            idx_orb[v] = oi

    root_index = {k2(roots[i]): i for i in range(len(roots))}

    mix_orbs = [oi for oi, sz in enumerate(orbit_sizes) if sz == 27]
    weights = {oi: su3_weight(roots[orbits[oi][0]]) for oi in mix_orbs}
    weights_3 = {(1, 0), (-1, 1), (0, -1)}
    color_orbs = sorted(
        [oi for oi in mix_orbs if weights[oi] in weights_3], key=lambda x: weights[x]
    )
    assert len(color_orbs) == 3

    # E6 id mapping
    e6_groups: Dict[Tuple[int, ...], int] = {}
    root_to_e6id: Dict[int, int] = {}
    for oi in color_orbs:
        for ridx in orbits[oi]:
            k = e6_key(roots[ridx])
            if k not in e6_groups:
                e6_groups[k] = len(e6_groups)
            root_to_e6id[ridx] = e6_groups[k]
    assert len(e6_groups) == 27

    # Build (color,e6id)->root index
    color_root_by_e6id = [[-1] * 27 for _ in range(3)]
    for c, oi in enumerate(color_orbs):
        for ridx in orbits[oi]:
            color_root_by_e6id[c][root_to_e6id[ridx]] = ridx
    if any(x == -1 for row in color_root_by_e6id for x in row):
        raise RuntimeError("Missing root for some (color,e6id)")

    # For each generator compute permutation p on e6ids and μ bits for each color and weight.
    gen_perms: List[Tuple[int, ...]] = []
    gen_mu_bits: List[List[List[int]]] = []  # gen -> color -> i -> bit

    for alpha in cds.E6_SIMPLE_ROOTS:
        alpha_k2 = k2(alpha)
        perms = []
        mu_by_color = []
        for c, oi in enumerate(color_orbs):
            perm = [-1] * 27
            mub = [0] * 27
            for i in range(27):
                ridx = color_root_by_e6id[c][i]
                beta_k2 = k2(roots[ridx])
                beta_prime_k2, mu = weyl_mu(alpha_k2, beta_k2, root_index)
                img_idx = root_index[beta_prime_k2]
                if idx_orb[img_idx] != oi:
                    raise RuntimeError("Generator left the orbit (unexpected)")
                perm[i] = root_to_e6id[img_idx]
                mub[i] = sign_to_bit(int(mu))
            perms.append(tuple(perm))
            mu_by_color.append(mub)
        if not (perms[0] == perms[1] == perms[2]):
            raise RuntimeError("Permutation differs by color (unexpected)")
        gen_perms.append(perms[0])
        gen_mu_bits.append(mu_by_color)

    # Solve gauge per color: a(p(i)) + a(i) + c_g = μ_g(i).
    gauge_solutions = []
    for c in range(3):
        # vars: a_i (27) + c_g (6) = 33
        def var_a(i: int) -> int:
            return i

        def var_cg(g: int) -> int:
            return 27 + g

        rows = []
        for g, p in enumerate(gen_perms):
            mu = gen_mu_bits[g][c]
            for i in range(27):
                mask = 0
                mask ^= 1 << var_a(i)
                mask ^= 1 << var_a(p[i])
                mask ^= 1 << var_cg(g)
                rows.append((mask, mu[i]))

        ok, sol, rank = LinearSystemGF2(nvars=33, rows=rows).solve()
        if not ok:
            raise RuntimeError(
                "Failed to solve gauge to kill μ (unexpected; should be a cocycle)"
            )
        a_bits = sol[:27]
        c_bits = sol[27:]
        gauge_solutions.append({"a_bits": a_bits, "c_bits": c_bits, "rank": rank})

    # Recompute symmetric triad signs d_t from couplings using these a_bits as phases.
    oa, ob, oc = color_orbs
    couplings = []
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
            raw = sign_to_bit(int(cocycle.epsilon_e8(ka, kb)))
            couplings.append((i, j, k, raw))
    assert len(couplings) == 270

    triads = sorted({tuple(sorted((i, j, k))) for (i, j, k, _) in couplings})
    assert len(triads) == 45
    triad_index = {t: idx for idx, t in enumerate(triads)}

    # Solve for d_t given fixed phases a_bits (one per color and weight).
    # Equation: a0(i)+a1(j)+a2(k)+d_t = raw
    d_bits = [None] * 45
    for i, j, k, raw in couplings:
        t = tuple(sorted((i, j, k)))
        rhs = (
            raw
            ^ gauge_solutions[0]["a_bits"][i]
            ^ gauge_solutions[1]["a_bits"][j]
            ^ gauge_solutions[2]["a_bits"][k]
        )
        idx = triad_index[t]
        if d_bits[idx] is None:
            d_bits[idx] = rhs
        elif d_bits[idx] != rhs:
            raise RuntimeError("Inconsistent d_t after μ-killing gauge (unexpected)")
    if any(x is None for x in d_bits):
        raise RuntimeError("Failed to assign all 45 d_t")

    d_signs = [bit_to_sign(int(b)) for b in d_bits]

    # Verify invariance: for each generator, d_{p(t)} differs from d_t by global bit g_g = c0+c1+c2 (mod 2).
    invariance = []
    for g, p in enumerate(gen_perms):
        gg = (
            gauge_solutions[0]["c_bits"][g]
            ^ gauge_solutions[1]["c_bits"][g]
            ^ gauge_solutions[2]["c_bits"][g]
        )
        ok = True
        for t in triads:
            tp = tuple(sorted((p[t[0]], p[t[1]], p[t[2]])))
            if d_bits[triad_index[tp]] != (d_bits[triad_index[t]] ^ gg):
                ok = False
                break
        invariance.append({"gen": g, "ok": ok, "global_bit": int(gg)})

    out = {
        "status": "ok",
        "counts": {
            "triads": 45,
            "couplings": 270,
            "d_sign_distribution": dict(Counter(d_signs)),
            "all_generators_ok": all(x["ok"] for x in invariance),
        },
        "color_orbits": [
            {"orbit": int(oi), "su3_weight": list(weights[oi])} for oi in color_orbs
        ],
        "gauge_solutions": gauge_solutions,
        "d_triples": [
            {"triple": list(triads[i]), "sign": int(d_signs[i])} for i in range(45)
        ],
        "invariance_check": invariance,
    }

    out_path = ROOT / "artifacts" / "e6_cubic_weyl_invariant_gauge.json"
    out_path.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(
        "PASS" if out["counts"]["all_generators_ok"] else "FAIL",
        "Computed μ-killing gauge and checked W(E6) invariance.",
    )
    print("Wrote", out_path)


if __name__ == "__main__":
    main()
