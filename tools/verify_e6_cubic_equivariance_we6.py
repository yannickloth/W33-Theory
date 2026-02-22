#!/usr/bin/env python3
"""
Verify W(E6) equivariance of the signed E6 cubic tensor using E8 root-space signs.

We work in the concrete E8 model with the maximal subalgebra E6 ⊕ A2:
  248 = (78,1) ⊕ (1,8) ⊕ (27,3) ⊕ (27̄,3̄)

In this repo we already computed:
  - the 45 nonzero E6 cubic monomials (tritangent planes),
  - a concrete ±1 sign assignment d_{ijk} on those 45 terms,
  - a basis gauge σ_c(i) on each color orbit c∈{0,1,2} for the (27,3) sector.

This script verifies that the 6 simple Weyl reflections of E6 act *equivariantly*
on d_{ijk} when you include:
  - the permutation of weights i -> p(i),
  - the induced ±1 action on root vectors from the Chevalley reflection formula
    for n_α(1):  e_β -> (-1)^p e_{s_α β}, where p is the root-string length on the
    negative side: p = max{k>=0 : β - k α is a root},
  - the saved gauge σ_c(i) used to define basis vectors f_{c,i} = (-1)^{σ_c(i)} e_{β(c,i)}.

Output:
  artifacts/e6_cubic_equivariance_we6.json
"""

from __future__ import annotations

import importlib.util
import json
import sys
from collections import Counter
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


def root_string_pq(
    beta_k2: Tuple[int, ...],
    alpha_k2: Tuple[int, ...],
    root_index: Dict[Tuple[int, ...], int],
) -> Tuple[int, int]:
    """
    (p,q) for the alpha-string through beta, using doubled integer coordinates:
      p = max{k>=0 : beta - k alpha is a root}
      q = max{k>=0 : beta + k alpha is a root}
    """

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


def cheva_abs_N(
    alpha_k2: Tuple[int, ...],
    beta_k2: Tuple[int, ...],
    root_index: Dict[Tuple[int, ...], int],
) -> int:
    """
    |N_{α,β}| from root strings (Chevalley normalization):
      if α,β,α+β are roots, let p = max{k>=0 : β - k α is a root}; then |N| = p+1.
    """

    p = 0
    while True:
        cand = tuple(beta_k2[i] - (p + 1) * alpha_k2[i] for i in range(8))
        if cand in root_index:
            p += 1
            continue
        break
    return p + 1


def lie_bracket_coeff(
    alpha_k2: Tuple[int, ...],
    beta_k2: Tuple[int, ...],
    root_index: Dict[Tuple[int, ...], int],
) -> int:
    """
    Coefficient N_{α,β} for [e_α, e_β] = N_{α,β} e_{α+β} in our cocycle convention.

    Returns 0 if α+β is not a root.
    """

    s = tuple(alpha_k2[i] + beta_k2[i] for i in range(8))
    if s not in root_index:
        return 0
    absN = cheva_abs_N(alpha_k2, beta_k2, root_index)
    eps = cocycle.epsilon_e8(alpha_k2, beta_k2)  # ±1
    return int(eps * absN)


def mat_mul(A: List[List[object]], B: List[List[object]]) -> List[List[object]]:
    n = len(A)
    m = len(B[0])
    k = len(B)
    out = [[0 for _ in range(m)] for _ in range(n)]
    for i in range(n):
        for j in range(m):
            s = 0
            for t in range(k):
                s += A[i][t] * B[t][j]
            out[i][j] = s
    return out


def mat_eye(n: int) -> List[List[int]]:
    return [[1 if i == j else 0 for j in range(n)] for i in range(n)]


def mat_pow(A: List[List[object]], e: int) -> List[List[object]]:
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


def exp_nilpotent(M: List[List[object]]) -> List[List[object]]:
    """
    exp(M) for a nilpotent matrix M, computed by truncated series.
    Uses Python rationals via Fraction (from the cocycle module, indirectly) if present.
    """

    from fractions import Fraction

    n = len(M)
    out: List[List[object]] = [[Fraction(0) for _ in range(n)] for _ in range(n)]
    I = mat_eye(n)
    for i in range(n):
        for j in range(n):
            out[i][j] = Fraction(I[i][j])

    # Truncate at n (sufficient for nilpotent in these small strings).
    fact = 1
    for k in range(1, n + 1):
        fact *= k
        P = mat_pow(M, k)
        for i in range(n):
            for j in range(n):
                out[i][j] += Fraction(P[i][j], fact)
    return out


def apply_mat(M: List[List[object]], v: List[object]) -> List[object]:
    n = len(M)
    out = [0 for _ in range(n)]
    for i in range(n):
        s = 0
        for j in range(n):
            s += M[i][j] * v[j]
        out[i] = s
    return out


def weyl_action_on_root_vector(
    alpha_k2: Tuple[int, ...],
    beta_k2: Tuple[int, ...],
    root_index: Dict[Tuple[int, ...], int],
) -> Tuple[Tuple[int, ...], int]:
    """
    Compute w_α(e_β) = s * e_{β'} where w_α is the Chevalley Weyl element
      w_α = exp(ad e_α) exp(ad e_{-α}) exp(ad e_α),
    using the cocycle-derived structure constants.

    Returns (beta_prime_k2, sign), where sign ∈ {±1}.
    """

    from fractions import Fraction

    # Build alpha-string through beta: beta - p alpha, ..., beta + q alpha
    p, q = root_string_pq(beta_k2, alpha_k2, root_index)
    string = [
        tuple(beta_k2[i] + s * alpha_k2[i] for i in range(8)) for s in range(-p, q + 1)
    ]
    pos = {r: idx for idx, r in enumerate(string)}
    n = len(string)

    # Build ad(e_alpha) and ad(e_-alpha) matrices in this basis.
    E = [[0 for _ in range(n)] for _ in range(n)]
    F = [[0 for _ in range(n)] for _ in range(n)]
    minus_alpha_k2 = tuple(-x for x in alpha_k2)

    for r, gamma in enumerate(string):
        # E: gamma -> gamma+alpha
        gp = tuple(gamma[i] + alpha_k2[i] for i in range(8))
        if gp in pos:
            c = lie_bracket_coeff(alpha_k2, gamma, root_index)
            E[pos[gp]][r] = Fraction(c)
        # F: gamma -> gamma-alpha
        gm = tuple(gamma[i] - alpha_k2[i] for i in range(8))
        if gm in pos:
            c = lie_bracket_coeff(minus_alpha_k2, gamma, root_index)
            F[pos[gm]][r] = Fraction(c)

    # Chevalley Weyl element: n_α(1) = exp(ad e_α) exp(ad e_{-α} * (-1)) exp(ad e_α)
    # i.e. the middle factor uses parameter -1.
    expE = exp_nilpotent(E)
    Fneg = [[-x for x in row] for row in F]
    expFneg = exp_nilpotent(Fneg)
    w = mat_mul(expE, mat_mul(expFneg, expE))

    # Apply to basis vector at beta (s=0 corresponds to index p).
    v0 = [Fraction(0) for _ in range(n)]
    v0[p] = Fraction(1)
    v1 = apply_mat(w, v0)

    # Expect a single ±1 coefficient at the reflected root position.
    nz = [(i, v) for i, v in enumerate(v1) if v != 0]
    if len(nz) != 1:
        raise RuntimeError(
            f"Weyl element did not map root vector to a single root vector: nz={nz}"
        )
    idx, coeff = nz[0]
    if coeff not in (Fraction(1), Fraction(-1)):
        raise RuntimeError(f"Unexpected coefficient for Weyl action: {coeff}")
    beta_prime = string[idx]
    return beta_prime, (1 if coeff == Fraction(1) else -1)


def build_color_orbit_data():
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

    # E6 id by projection across the three color orbits.
    e6_groups: Dict[Tuple[int, ...], int] = {}
    root_to_e6id: Dict[int, int] = {}
    for oi in color_orbs:
        for r_idx in orbits[oi]:
            k = e6_key(roots[r_idx])
            if k not in e6_groups:
                e6_groups[k] = len(e6_groups)
            root_to_e6id[r_idx] = e6_groups[k]
    assert len(e6_groups) == 27

    # Map (color, e6id) -> root index
    color_root_by_e6id: List[List[int]] = [[-1] * 27 for _ in range(3)]
    for c, oi in enumerate(color_orbs):
        for r_idx in orbits[oi]:
            e6id = root_to_e6id[r_idx]
            if color_root_by_e6id[c][e6id] != -1:
                raise RuntimeError("Non-unique E6 id within a color orbit (unexpected)")
            color_root_by_e6id[c][e6id] = r_idx

    if any(x == -1 for row in color_root_by_e6id for x in row):
        raise RuntimeError("Failed to fill color_root_by_e6id")

    root_index = {k2(roots[i]): i for i in range(len(roots))}
    return (
        roots,
        orbits,
        idx_orb,
        color_orbs,
        weights,
        root_to_e6id,
        color_root_by_e6id,
        root_index,
    )


def load_sign_gauge_artifact():
    data = json.loads(
        (ROOT / "artifacts" / "e6_cubic_sign_gauge_solution.json").read_text(
            encoding="utf-8"
        )
    )
    sigma_bits = data["solution"]["sigma_bits"]
    if len(sigma_bits) != 3 or any(len(row) != 27 for row in sigma_bits):
        raise ValueError("Unexpected sigma_bits shape")
    d: Dict[Tuple[int, int, int], int] = {}
    for ent in data["solution"]["d_triples"]:
        t = tuple(sorted(int(x) for x in ent["triple"]))
        d[t] = int(ent["sign"])
    if len(d) != 45:
        raise ValueError("Expected 45 d-triples")
    return sigma_bits, d


def main() -> None:
    (
        roots,
        _orbits,
        idx_orb,
        color_orbs,
        weights,
        root_to_e6id,
        color_root_by_e6id,
        root_index,
    ) = build_color_orbit_data()
    sigma_bits, d = load_sign_gauge_artifact()

    triples = sorted(d.keys())

    results = []
    global_bits = []

    for gen_idx, alpha in enumerate(cds.E6_SIMPLE_ROOTS):
        alpha_k2 = k2(alpha)
        per_color_perm = []
        per_color_tbits = []

        for c, oi in enumerate(color_orbs):
            perm = [-1] * 27
            tbits = [0] * 27
            for i in range(27):
                r_idx = color_root_by_e6id[c][i]
                beta_k2 = k2(roots[r_idx])
                beta_prime_k2, sgn = weyl_action_on_root_vector(
                    alpha_k2, beta_k2, root_index
                )
                img_idx = root_index.get(beta_prime_k2)
                if img_idx is None or idx_orb[img_idx] != oi:
                    raise RuntimeError("Weyl element left the color orbit (unexpected)")
                j = root_to_e6id[img_idx]
                perm[i] = j

                wsign_bit = sign_to_bit(int(sgn))
                tbits[i] = sigma_bits[c][i] ^ wsign_bit ^ sigma_bits[c][j]

            if sorted(perm) != list(range(27)):
                raise RuntimeError("Generator did not induce a permutation on e6ids")
            per_color_perm.append(tuple(perm))
            per_color_tbits.append(tbits)

        if not (per_color_perm[0] == per_color_perm[1] == per_color_perm[2]):
            raise RuntimeError("Permutation on e6ids depends on color (unexpected)")
        perm_e6 = per_color_perm[0]

        g = None
        ok = True
        for i, j, k in triples:
            tp = tuple(sorted((perm_e6[i], perm_e6[j], perm_e6[k])))
            lhs = sign_to_bit(d[tp])
            rhs_no_g = (
                sign_to_bit(d[(i, j, k)])
                ^ per_color_tbits[0][i]
                ^ per_color_tbits[1][j]
                ^ per_color_tbits[2][k]
            )
            if g is None:
                g = lhs ^ rhs_no_g
            elif (lhs ^ rhs_no_g) != g:
                ok = False
                break
        if g is None:
            raise RuntimeError("No triples?")

        results.append(
            {
                "generator_index": int(gen_idx),
                "ok": bool(ok),
                "global_bit": int(g),
            }
        )
        global_bits.append(int(g))

    out = {
        "status": "ok",
        "counts": {
            "generators": 6,
            "triples": 45,
            "all_generators_ok": all(r["ok"] for r in results),
            "global_bit_distribution": dict(Counter(global_bits)),
        },
        "generators": results,
    }

    out_path = ROOT / "artifacts" / "e6_cubic_equivariance_we6.json"
    out_path.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(
        "PASS" if out["counts"]["all_generators_ok"] else "FAIL",
        "W(E6) equivariance for cubic tensor (exact cocycle Weyl action).",
    )
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
