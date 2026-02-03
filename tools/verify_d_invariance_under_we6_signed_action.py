#!/usr/bin/env python3
"""
Verify how the extracted E6 cubic tensor signs transform under the *actual* signed Weyl action.

We have an extracted gauge (sigma_bits) and cubic coefficients d_t from:
  artifacts/e6_cubic_sign_gauge_solution.json

From the Chevalley/cocycle model for E8, each E6 simple reflection generator s_α acts on
each mixed root vector e_{β(c,i)} (color c, E6-id i) by:
  s_α(e_{β(c,i)}) = μ_{c,i} * e_{β(c,p(i))}
where p is the induced permutation on E6-ids and μ_{c,i}∈{±1} depends on i.

In the *sigma-gauged* basis f_{c,i} = (-1)^{sigma_c[i]} e_{β(c,i)}, the same action is:
  s_α(f_{c,i}) = (-1)^{t_{c,i}} f_{c,p(i)}
with t_{c,i} = sigma_c[i] ⊕ mu_{c,i} ⊕ sigma_c[p(i)]  (GF(2) bits).

If the cubic tensor is an invariant of the full E6 group, then under this signed permutation
the coefficients must satisfy:
  d_{p(t)} = d_t ⊕ t0(i) ⊕ t1(j) ⊕ t2(k) ⊕ g_α
for each triad t=(i,j,k) and some generator-dependent global bit g_α (since the invariant is
unique up to overall sign convention in our extracted normalization).

This script checks whether such a g_α exists for each simple generator.

Outputs:
  artifacts/e6_cubic_signed_we6_action_check.json
"""

from __future__ import annotations

import importlib.util
import json
import sys
from collections import Counter
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
    if s not in (-1, 1):
        raise ValueError("Expected ±1")
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
            E[pos[gp]][r] = Fraction(N(alpha_k2, gamma, root_index))
        gm = tuple(gamma[i] - alpha_k2[i] for i in range(8))
        if gm in pos:
            F[pos[gm]][r] = Fraction(N(minus_alpha_k2, gamma, root_index))

    expE = exp_nilpotent(E)
    Fneg = [[-x for x in row] for row in F]
    expFneg = exp_nilpotent(Fneg)
    w = mat_mul(expE, mat_mul(expFneg, expE))

    v0 = [Fraction(0) for _ in range(n)]
    v0[p] = Fraction(1)
    v1 = apply_mat(w, v0)
    nz = [(i, v) for i, v in enumerate(v1) if v != 0]
    if len(nz) != 1:
        raise RuntimeError(f"Bad Weyl action support: {nz}")
    idx, coeff = nz[0]
    if coeff not in (Fraction(1), Fraction(-1)):
        raise RuntimeError(f"Unexpected coefficient: {coeff}")
    return string[idx], (1 if coeff == Fraction(1) else -1)


def load_sigma_and_d() -> Tuple[List[List[int]], Dict[Tuple[int, int, int], int]]:
    data = json.loads(
        (ROOT / "artifacts" / "e6_cubic_sign_gauge_solution.json").read_text(
            encoding="utf-8"
        )
    )
    sigma = data["solution"]["sigma_bits"]
    d: Dict[Tuple[int, int, int], int] = {}
    for ent in data["solution"]["d_triples"]:
        t = tuple(sorted(int(x) for x in ent["triple"]))
        d[t] = sign_to_bit(int(ent["sign"]))
    return sigma, d


def main() -> None:
    sigma_bits, d_bits = load_sigma_and_d()

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
    oa, ob, oc = color_orbs

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

    # (color,e6id)->root index
    color_root_by_e6id = [[-1] * 27 for _ in range(3)]
    for c, oi in enumerate(color_orbs):
        for ridx in orbits[oi]:
            color_root_by_e6id[c][root_to_e6id[ridx]] = ridx
    if any(x == -1 for row in color_root_by_e6id for x in row):
        raise RuntimeError("Missing root for some (color,e6id)")

    triads = sorted(d_bits.keys())
    assert len(triads) == 45

    per_gen = []
    for gen_idx, alpha in enumerate(cds.E6_SIMPLE_ROOTS):
        alpha_k2 = k2(alpha)
        # compute p and mu bits and then t bits
        perms = []
        mu = [[0] * 27 for _ in range(3)]
        for c, oi in enumerate(color_orbs):
            perm = [-1] * 27
            for i in range(27):
                ridx = color_root_by_e6id[c][i]
                beta_k = k2(roots[ridx])
                beta_prime_k, mu_sign = weyl_mu(alpha_k2, beta_k, root_index)
                img_idx = root_index[beta_prime_k]
                if idx_orb[img_idx] != oi:
                    raise RuntimeError("Generator left orbit")
                j = root_to_e6id[img_idx]
                perm[i] = j
                mu[c][i] = sign_to_bit(int(mu_sign))
            perms.append(tuple(perm))
        if not (perms[0] == perms[1] == perms[2]):
            raise RuntimeError("Permutation differs by color")
        p = perms[0]

        tbits = [[0] * 27 for _ in range(3)]
        for c in range(3):
            for i in range(27):
                tbits[c][i] = sigma_bits[c][i] ^ mu[c][i] ^ sigma_bits[c][p[i]]

        g = None
        ok = True
        for i, j, k in triads:
            tp = tuple(sorted((p[i], p[j], p[k])))
            lhs = d_bits[tp]
            rhs_no_g = d_bits[(i, j, k)] ^ tbits[0][i] ^ tbits[1][j] ^ tbits[2][k]
            if g is None:
                g = lhs ^ rhs_no_g
            elif (lhs ^ rhs_no_g) != g:
                ok = False
                break
        per_gen.append(
            {"gen": gen_idx, "ok": ok, "g_bit": int(g if g is not None else 0)}
        )

    out = {
        "status": "ok",
        "counts": {"generators": 6, "all_ok": all(x["ok"] for x in per_gen)},
        "per_generator": per_gen,
    }
    out_path = ROOT / "artifacts" / "e6_cubic_signed_we6_action_check.json"
    out_path.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(
        "PASS" if out["counts"]["all_ok"] else "FAIL",
        "d_t transformation under signed Weyl generators.",
    )
    print("Wrote", out_path)


if __name__ == "__main__":
    main()
