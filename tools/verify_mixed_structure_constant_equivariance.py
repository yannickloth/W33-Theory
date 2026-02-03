#!/usr/bin/env python3
"""
Verify equivariance of mixed structure constants under E6 Weyl generators, including μ-signs.

We test, for each E6 simple reflection generator w and each mixed triple:
  α in color0 orbit, β in color1 orbit, γ in color2 orbit with α+β+γ=0,
the Chevalley relation:
  μ(α) μ(β) N(wα,wβ) = N(α,β) μ(-γ),
where μ(x) is defined by the Weyl element action on root vectors:
  w(e_x) = μ(x) e_{w x}.

If this fails, the μ computation (or bracket signs) are not internally consistent.

Outputs:
  artifacts/mixed_structure_constant_equivariance.json
"""

from __future__ import annotations

import importlib.util
import json
import sys
from collections import Counter
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


def su3_weight(r: np.ndarray) -> Tuple[int, int]:
    return (
        int(round(float(np.dot(r, SU3_ALPHA)))),
        int(round(float(np.dot(r, SU3_BETA)))),
    )


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


def lie_bracket_coeff(
    alpha_k2: Tuple[int, ...],
    beta_k2: Tuple[int, ...],
    root_index: Dict[Tuple[int, ...], int],
) -> int:
    return N(alpha_k2, beta_k2, root_index)


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
            c = lie_bracket_coeff(alpha_k2, gamma, root_index)
            E[pos[gp]][r] = Fraction(c)
        gm = tuple(gamma[i] - alpha_k2[i] for i in range(8))
        if gm in pos:
            c = lie_bracket_coeff(minus_alpha_k2, gamma, root_index)
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
        raise RuntimeError(f"Bad Weyl action support: {nz}")
    idx, coeff = nz[0]
    if coeff not in (Fraction(1), Fraction(-1)):
        raise RuntimeError(f"Unexpected coeff: {coeff}")
    return string[idx], (1 if coeff == Fraction(1) else -1)


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
    oa, ob, oc = color_orbs

    # Build couplings at the root-index level.
    couplings = []
    for a in orbits[oa]:
        ka = k2(roots[a])
        for b in orbits[ob]:
            kb = k2(roots[b])
            need = tuple(-(ka[i] + kb[i]) for i in range(8))
            c = root_index.get(need)
            if c is None or idx_orb[c] != oc:
                continue
            couplings.append((a, b, c))
    assert len(couplings) == 270

    failures = 0
    sample = []
    per_gen_fail = Counter()

    for gi, alpha in enumerate(cds.E6_SIMPLE_ROOTS):
        alpha_k2 = k2(alpha)

        for a, b, c in couplings:
            ak = k2(roots[a])
            bk = k2(roots[b])
            ck = k2(roots[c])
            # N(α,β) for α+β=-γ
            n_ab = N(ak, bk, root_index)
            assert n_ab != 0

            wa, mu_a = weyl_mu(alpha_k2, ak, root_index)
            wb, mu_b = weyl_mu(alpha_k2, bk, root_index)
            wc, mu_c = weyl_mu(alpha_k2, ck, root_index)

            # Verify that reflection permutes the colors correctly (stays within orbit):
            ia = root_index[wa]
            ib = root_index[wb]
            ic = root_index[wc]
            if idx_orb[ia] != oa or idx_orb[ib] != ob or idx_orb[ic] != oc:
                raise RuntimeError("Generator left color orbits (unexpected)")

            # Compare μ(α)μ(β)N(wα,wβ) with N(α,β)μ(-γ).
            n_w = N(wa, wb, root_index)
            if n_w == 0:
                raise RuntimeError("wα+wβ should be a root")

            minus_c = tuple(-x for x in ck)
            w_minus_c, mu_minus_c = weyl_mu(alpha_k2, minus_c, root_index)
            # w(-γ) should be -(wγ)
            if w_minus_c != tuple(-x for x in wc):
                raise RuntimeError("w(-γ) != -(wγ) (unexpected)")

            lhs = mu_a * mu_b * n_w
            rhs = n_ab * mu_minus_c
            if lhs != rhs:
                failures += 1
                per_gen_fail[gi] += 1
                if len(sample) < 5:
                    sample.append(
                        {
                            "gen": gi,
                            "a": a,
                            "b": b,
                            "c": c,
                            "lhs": int(lhs),
                            "rhs": int(rhs),
                            "mu_a": int(mu_a),
                            "mu_b": int(mu_b),
                            "mu_minus_c": int(mu_minus_c),
                            "n_ab": int(n_ab),
                            "n_w": int(n_w),
                        }
                    )

    out = {
        "status": "ok",
        "counts": {
            "couplings": 270,
            "generators": 6,
            "failures": int(failures),
            "failures_per_generator": {str(k): int(v) for k, v in per_gen_fail.items()},
        },
        "sample_failures": sample,
    }
    out_path = ROOT / "artifacts" / "mixed_structure_constant_equivariance.json"
    out_path.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print("Failures:", failures)
    print("Wrote", out_path)


if __name__ == "__main__":
    main()
