#!/usr/bin/env python3
"""
Export the signed W(E6) generator action on the 27 in the **canonical gauge**.

We represent each E6 simple reflection s_α via the Chevalley element n_α(1) acting on root vectors:
  s(e_β) = μ(β) * e_{sβ}.

On the (chosen) 27-orbit basis in the SU(3)=3 triangle, after applying the canonical phase gauge,
this becomes a signed permutation matrix M with entries ±1 and M^2 = I.

Writes:
  artifacts/we6_signed_action_on_27.json
"""

from __future__ import annotations

import importlib.util
import json
import sys
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


solver = _load_module(
    ROOT / "tools" / "solve_canonical_su3_gauge_and_cubic.py",
    "solve_canonical_su3_gauge_and_cubic",
)
cds = _load_module(ROOT / "tools" / "compute_double_sixes.py", "compute_double_sixes")
cocycle = _load_module(ROOT / "tools" / "e8_lattice_cocycle.py", "e8_lattice_cocycle")
we6 = _load_module(ROOT / "tools" / "weyl_e6_action.py", "weyl_e6_action")


def k2(r: np.ndarray) -> Tuple[int, ...]:
    return tuple(int(round(2 * float(x))) for x in r.tolist())


def bit(mu: int) -> int:
    if mu not in (-1, 1):
        raise ValueError("Expected ±1")
    return 1 if mu == -1 else 0


def bit_to_sign(b: int) -> int:
    if b not in (0, 1):
        raise ValueError("Expected bit 0/1")
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


def lie_bracket_coeff(
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


def mat_eye(n: int) -> List[List[Fraction]]:
    return [
        [Fraction(1) if i == j else Fraction(0) for j in range(n)] for i in range(n)
    ]


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


def weyl_mu_on_root(
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
    expFneg = exp_nilpotent([[-x for x in row] for row in F])
    w = mat_mul(expE, mat_mul(expFneg, expE))

    v0 = [Fraction(0) for _ in range(n)]
    v0[p] = Fraction(1)
    v1 = apply_mat(w, v0)

    nz = [(i, v) for i, v in enumerate(v1) if v != 0]
    if len(nz) != 1:
        raise RuntimeError(f"Unexpected Weyl action support size: {nz}")
    idx, coeff = nz[0]
    wbeta = string[idx]
    if coeff not in (Fraction(1), Fraction(-1)):
        raise RuntimeError(f"Unexpected Weyl coefficient: {coeff}")
    mu = 1 if coeff == 1 else -1
    return wbeta, mu


def cycle_decomposition(p: List[int]) -> List[List[int]]:
    n = len(p)
    seen = [False] * n
    cycles = []
    for i in range(n):
        if seen[i]:
            continue
        cur = i
        cyc = []
        while not seen[cur]:
            seen[cur] = True
            cyc.append(cur)
            cur = p[cur]
        cycles.append(cyc)
    return cycles


@dataclass(frozen=True)
class SignedGenerator:
    name: str
    permutation: List[int]
    signs: List[int]  # sign on each moved basis vector: e_i -> signs[i] * e_{p(i)}


def main() -> None:
    solver.main()
    sol_path = ROOT / "artifacts" / "canonical_su3_gauge_and_cubic.json"
    sol = json.loads(sol_path.read_text(encoding="utf-8"))
    if not sol.get("counts", {}).get("solvable", False):
        raise RuntimeError("canonical_su3_gauge_and_cubic.json is not solvable")

    phase_bits: Dict[str, List[int]] = sol["solution"]["phase_bits"]

    # Fixed reference 27-orbit in the SU(3)=3 triangle.
    oi_ref = int(sol["orbits_3"][0]["orbit"])
    e6_keys_27 = [tuple(int(x) for x in k) for k in sol["e6_keys_27_k2"]]
    key_to_id = {k: i for i, k in enumerate(e6_keys_27)}

    roots = cds.construct_e8_roots()
    orbits = cds.compute_we6_orbits(roots)
    root_index = {k2(roots[i]): i for i in range(len(roots))}

    orb_root_by_id = [-1] * 27
    for ridx in orbits[oi_ref]:
        kk = solver.e6_key(roots[ridx])
        j = key_to_id.get(kk)
        if j is None:
            raise RuntimeError("E6 key not in 27 list")
        orb_root_by_id[j] = ridx
    if any(v == -1 for v in orb_root_by_id):
        raise RuntimeError("Missing basis root for some e6id")

    e6_simple = we6.get_e6_simple_roots()
    e6_simple_k2 = [k2(np.array(v, dtype=float)) for v in e6_simple]
    gen_names = [f"s{i+1}" for i in range(len(e6_simple_k2))]

    gens: List[SignedGenerator] = []
    for name, alpha_k2 in zip(gen_names, e6_simple_k2):
        p = [-1] * 27
        sgn = [1] * 27
        sq = [1] * 27
        for i in range(27):
            ridx = orb_root_by_id[i]
            beta = k2(roots[ridx])
            wbeta, mu = weyl_mu_on_root(alpha_k2, beta, root_index)
            tidx = root_index.get(wbeta)
            if tidx is None:
                raise RuntimeError("weyl_mu_on_root produced a non-root")
            kk = solver.e6_key(roots[tidx])
            j = key_to_id.get(kk)
            if j is None:
                raise RuntimeError("Image root not in 27 key set")
            p[i] = j
            sign_bit = phase_bits[str(oi_ref)][i] ^ phase_bits[str(oi_ref)][j] ^ bit(mu)
            sgn[i] = bit_to_sign(sign_bit)

        if len(set(p)) != 27:
            raise RuntimeError("Generator map is not a permutation on 27")
        # reflection: involution
        if any(p[p[i]] != i for i in range(27)):
            raise RuntimeError("Permutation is not an involution")
        # In a Chevalley realization, n_α(1)^2 = h_α(-1), so the signed action squares to a diagonal
        # sign given on each root space by (-1)^{<β,α∨>} = (-1)^{β·α} (simply-laced, α·α=2).
        for i in range(27):
            ridx = orb_root_by_id[i]
            beta_k2 = k2(roots[ridx])
            ip_num = sum(beta_k2[t] * alpha_k2[t] for t in range(8))
            if ip_num % 4 != 0:
                raise RuntimeError("Non-integral inner product in k2 coords")
            ip = ip_num // 4
            expected_sq = -1 if ip != 0 else 1
            sq[i] = sgn[i] * sgn[p[i]]
            if sq[i] != expected_sq:
                raise RuntimeError(
                    "Signed square mismatch with h_alpha(-1) expectation"
                )

        gens.append(SignedGenerator(name=name, permutation=p, signs=sgn))

    # Optional sanity: compute order of the generated *unsigned* permutation group (should be 51840).
    # Use BFS closure on permutations of 27. This is small enough to do deterministically.
    def comp(p: Tuple[int, ...], q: Tuple[int, ...]) -> Tuple[int, ...]:
        return tuple(p[q[i]] for i in range(27))

    idp = tuple(range(27))
    gen_perm = [tuple(g.permutation) for g in gens]
    seen = {idp}
    frontier = [idp]
    while frontier:
        cur = frontier.pop()
        for g in gen_perm:
            nxt = comp(g, cur)
            if nxt not in seen:
                seen.add(nxt)
                frontier.append(nxt)
    perm_group_order = len(seen)

    out = {
        "status": "ok",
        "counts": {"generators": len(gens), "perm_group_order": int(perm_group_order)},
        "reference_orbit": {
            "orbit_index": int(oi_ref),
            "su3_weight": sol["orbits_3"][0]["su3_weight"],
        },
        "generators": [],
    }
    for g in gens:
        cyc = cycle_decomposition(g.permutation)
        out["generators"].append(
            {
                "name": g.name,
                "cycles": cyc,
                "cycle_type": sorted([len(c) for c in cyc]),
                "permutation": list(g.permutation),
                "signs": list(g.signs),
                "transpositions": [[c[0], c[1]] for c in cyc if len(c) == 2],
                "fixed_points": [c[0] for c in cyc if len(c) == 1],
            }
        )

    out_path = ROOT / "artifacts" / "we6_signed_action_on_27.json"
    out_path.write_text(json.dumps(out, indent=2, default=int), encoding="utf-8")
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
