#!/usr/bin/env python3
"""
Compute the projective sign cocycle (double-cover obstruction) for W(E6) on a 27-orbit.

From the cocycle-derived Chevalley basis for E8, each E6 simple reflection s_i acts on
the 27 weight spaces (minuscule) as a signed permutation:
    s_i : v_x -> μ_i(x) * v_{p_i(x)},    μ_i(x) ∈ {±1}.

If the μ_i were a pure coboundary (up to generator constants), we could gauge them away.
In general this defines a nontrivial projective (double-cover) representation of W(E6).

We diagnose it by checking Coxeter relations:
  - s_i^2 = 1 should hold exactly (it does).
  - (s_i s_j)^{m_ij} = 1, where m_ij is 3 if i-j adjacent in the E6 Dynkin diagram, else 2.

In the signed action, these words may evaluate to a *central* sign ±1. If any relation
gives -1, the action factors through a nontrivial double cover.

Outputs:
  artifacts/we6_projective_cocycle.json
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


def k2(r: np.ndarray) -> Tuple[int, ...]:
    return tuple(int(round(2 * float(x))) for x in r.tolist())


def sign_to_bit(s: int) -> int:
    return 1 if s == -1 else 0


def bit_to_sign(b: int) -> int:
    return -1 if b else 1


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
class SignedPerm:
    perm: Tuple[int, ...]  # length 27
    sign: Tuple[int, ...]  # length 27, values ±1, meaning v_i -> sign[i] v_{perm[i]}

    def compose(self, other: "SignedPerm") -> "SignedPerm":
        # self ∘ other
        p = [0] * 27
        s = [1] * 27
        for i in range(27):
            j = other.perm[i]
            p[i] = self.perm[j]
            s[i] = other.sign[i] * self.sign[j]
        return SignedPerm(tuple(p), tuple(s))

    def pow(self, e: int) -> "SignedPerm":
        cur = self
        out = SignedPerm(tuple(range(27)), tuple([1] * 27))
        ee = e
        while ee:
            if ee & 1:
                out = cur.compose(out)
            ee >>= 1
            if ee:
                cur = cur.compose(cur)
        return out

    def is_central(self) -> Tuple[bool, int]:
        # Return (is identity perm, and whether sign is uniform)
        if self.perm != tuple(range(27)):
            return False, 0
        uniq = set(self.sign)
        if len(uniq) != 1:
            return False, 0
        return True, next(iter(uniq))


def main() -> None:
    roots = cds.construct_e8_roots()
    orbits = cds.compute_we6_orbits(roots)
    orbit27 = [o for o in orbits if len(o) == 27][0]
    local_roots = roots[orbit27]

    root_index = {k2(roots[i]): i for i in range(len(roots))}
    local_key_to_idx = {k2(local_roots[i]): i for i in range(27)}

    # Build signed perms for the 6 E6 simple reflections on this 27-orbit.
    gens: List[SignedPerm] = []
    for alpha in cds.E6_SIMPLE_ROOTS:
        alpha_k2 = k2(alpha)
        perm = [-1] * 27
        sgn = [1] * 27
        for i in range(27):
            beta_k2 = k2(local_roots[i])
            beta_prime_k2, mu = weyl_mu(alpha_k2, beta_k2, root_index)
            j = local_key_to_idx.get(beta_prime_k2)
            if j is None:
                raise RuntimeError("Generator left the chosen 27-orbit")
            perm[i] = j
            sgn[i] = int(mu)
        gens.append(SignedPerm(tuple(perm), tuple(sgn)))

    # Coxeter matrix m_ij from inner products of simple roots.
    simple = cds.E6_SIMPLE_ROOTS
    M = [[1] * 6 for _ in range(6)]
    for i in range(6):
        for j in range(6):
            if i == j:
                M[i][j] = 1
                continue
            ip = int(round(float(np.dot(simple[i], simple[j]))))
            if ip == 0:
                M[i][j] = 2
            elif ip == -1:
                M[i][j] = 3
            else:
                raise RuntimeError("Unexpected E6 simple-root inner product")

    relation_results = []
    central_counts = Counter()
    for i in range(6):
        # s_i^2
        w = gens[i].pow(2)
        ok, z = w.is_central()
        relation_results.append({"relation": f"s{i}^2", "central": ok, "z": int(z)})
        central_counts[int(z)] += int(ok)

    for i in range(6):
        for j in range(i + 1, 6):
            m = M[i][j]
            w = gens[i].compose(gens[j]).pow(m)
            ok, z = w.is_central()
            relation_results.append(
                {"relation": f"(s{i}s{j})^{m}", "central": ok, "z": int(z), "m": int(m)}
            )
            if ok:
                central_counts[int(z)] += 1

    out = {
        "status": "ok",
        "counts": {
            "relations_checked": len(relation_results),
            "central_relation_distribution": {
                str(k): int(v) for k, v in central_counts.items()
            },
        },
        "coxeter_m": M,
        "relations": relation_results,
    }

    out_path = ROOT / "artifacts" / "we6_projective_cocycle.json"
    out_path.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print("Wrote", out_path)


if __name__ == "__main__":
    main()
