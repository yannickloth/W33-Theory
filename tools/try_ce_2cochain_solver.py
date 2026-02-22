#!/usr/bin/env python3
"""Try to solve d(alpha) = J on the failing triple by searching for a
2-cochain alpha with nonzero entries only on pairs (g1,g2) -> L.

Strategy (local probe):
- Let x,y in g1 and z in g2 be the failing triple.
- Seek U = alpha(y,z) and V = alpha(x,z) in L so that
      [x, U] - [y, V] = J(x,y,z).
  (this is the CE differential when alpha(x,y)=0 etc.)
- Solve the linear system for U and V (complex linear least-squares,
  then try rationalization).
- If solvable, write artifact `artifacts/ce_2cochain_local_solution.json`.

This is a diagnostic/proof-of-concept step in the direction of building an
l4-type homotopy correction (or showing d(C^2) can hit the obstruction).
"""
from __future__ import annotations

import importlib.util
import json
from fractions import Fraction
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "artifacts" / "ce_2cochain_local_solution.json"


def _load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys_mod = __import__("sys")
    sys_mod.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def flatten(e):
    return np.concatenate(
        [e.e6.reshape(-1), e.sl3.reshape(-1), e.g1.reshape(-1), e.g2.reshape(-1)]
    )


def main():
    toe = _load_module(ROOT / "tools" / "toe_e8_z3graded_bracket_jacobi.py", "toe_e8")
    exh = _load_module(
        ROOT / "tools" / "exhaustive_homotopy_check_rationalized_l3.py", "exh"
    )

    # failing triple from exhaustive artifact
    ex = json.loads(
        (ROOT / "artifacts" / "exhaustive_homotopy_rationalized_l3.json").read_text()
    )
    ft = ex["sectors"]["g1_g1_g2"]["first_fail"]
    a_idx = tuple(ft["a"])
    b_idx = tuple(ft["b"])
    c_idx = tuple(ft["c"])

    # build bracket objects
    e6_basis = np.load(
        ROOT / "artifacts" / "e6_27rep_basis_export" / "E6_basis_78.npy"
    ).astype(np.complex128)
    proj = toe.E6Projector(e6_basis)
    all_triads = toe._load_signed_cubic_triads()
    bad9 = set(
        tuple(sorted(t[:3]))
        for t in json.loads(
            (
                ROOT / "artifacts" / "linfty_coord_search_results_rationalized.json"
            ).read_text()
        )["original"]["fiber_triads"]
    )

    br_l2 = toe.E8Z3Bracket(
        e6_projector=proj,
        cubic_triads=[t for t in all_triads if tuple(sorted(t[:3])) not in bad9],
        scale_g1g1=1.0,
        scale_g2g2=-1.0 / 6.0,
        scale_e6=1.0,
        scale_sl3=1.0 / 6.0,
    )

    # construct basis elems x,y,z
    x = exh.basis_elem_g1(toe, a_idx)
    y = exh.basis_elem_g1(toe, b_idx)
    z = exh.basis_elem_g2(toe, c_idx)

    J = toe._jacobi(br_l2, x, y, z)
    Jflat = flatten(J)

    # We'll seek U = alpha(y,z) and V = alpha(x,z) as unknown E8Z3 vectors.
    # Linear equation: bracket(x, U) - bracket(y, V) = J

    # Build linear operator for unknown vector entries of U and V.
    dim = Jflat.size
    # Represent unknowns as concatenated real vectors (real+imag) for numerical solve.

    # Helper: given a candidate U (E8Z3), compute flatten(bracket(x, U))
    def bracket_with_X_flat(X, Uvec_flat):
        # Uvec_flat is complex-valued flat vector of same shape as flatten(E8Z3)
        # rebuild E8Z3 from flat representation (use toe.E8Z3 constructor: pass arrays)
        N = 27 * 27
        e6 = Uvec_flat[:N].reshape((27, 27))
        off = N
        sl3 = Uvec_flat[off : off + 9].reshape((3, 3))
        off += 9
        g1 = Uvec_flat[off : off + 81].reshape((27, 3))
        off += 81
        g2 = Uvec_flat[off : off + 81].reshape((27, 3))
        U = toe.E8Z3(e6=e6, sl3=sl3, g1=g1, g2=g2)
        # use the affine bracket object to compute the Lie bracket of two E8Z3 elements
        B = br_l2.bracket(X, U)
        return flatten(B)

    # Basis size for a single E8Z3 flat vector
    Nflat = Jflat.size

    # We'll solve for complex unknown vectors u and v of length Nflat such that
    #   A u + B v = Jflat, where A(u) = bracket(x,u) and B(v) = -bracket(y,v).

    # Build matrices A_mat and B_mat by applying basis vectors
    # For efficiency, construct action on a complex basis: use identity columns.
    A_cols = []
    B_cols = []
    # We'll build real stacked system (real+imag) to use np.linalg.lstsq
    eye = np.eye(Nflat, dtype=np.complex128)
    for i in range(Nflat):
        col = bracket_with_X_flat(x, eye[:, i])
        A_cols.append(col)
        col2 = bracket_with_X_flat(y, eye[:, i])
        B_cols.append(-col2)

    A = np.column_stack(A_cols)
    B = np.column_stack(B_cols)

    # Combined linear map: [A | B] @ [u; v] = Jflat
    M = np.hstack([A, B])

    # convert to real system
    M_real = np.vstack([np.real(M), np.imag(M)])
    rhs = np.concatenate([np.real(Jflat), np.imag(Jflat)])

    # solve least-squares
    sol, *_ = np.linalg.lstsq(M_real, rhs, rcond=None)

    # extract u and v
    u_real = sol[:Nflat]
    v_real = sol[Nflat:]
    # recover complex form (real+imag portions in solution)
    # Because we solved real system, interpret pairs (real+i*imag)
    half = M_real.shape[0] // 2
    # Actually simpler: reconstruct complex u by pairing entries from sol as complex numbers
    # But sol currently contains real numbers corresponding to real system unknowns; we solved
    # M_real which already accounts for complex->real conversion. We need to reconstruct complex
    # u from sol by splitting original unknown vector (which was real-valued representation
    # of complex unknowns). However we built M_real from complex M by stacking real+imag rows,
    # leaving complex unknowns as single unknowns. Thus sol already corresponds to complex u and v
    # flattened into real scalars (they're real if the system demands so). We'll recompose
    u = u_real.astype(np.float64)
    v = v_real.astype(np.float64)

    # compute residual
    lhs = M_real.dot(sol)
    res_norm = float(np.linalg.norm(lhs - rhs))

    out = {
        "failed_triple": {"a": a_idx, "b": b_idx, "c": c_idx},
        "J_norm": float(np.linalg.norm(Jflat)),
        "solve_residual_norm": res_norm,
        "sol_found": res_norm < 1e-8,
    }

    if out["sol_found"]:
        # extract u and v as complex flats (here they are real arrays from least-squares)
        u_flat = u
        v_flat = v
        out["u_norm"] = float(np.linalg.norm(u_flat))
        out["v_norm"] = float(np.linalg.norm(v_flat))

        # build E8Z3 objects for U and V
        def flat_to_E8Z3(vec):
            N = 27 * 27
            e6 = vec[:N].reshape((27, 27)).astype(np.complex128)
            off = N
            sl3 = vec[off : off + 9].reshape((3, 3)).astype(np.complex128)
            off += 9
            g1 = vec[off : off + 81].reshape((27, 3)).astype(np.complex128)
            off += 81
            g2 = vec[off : off + 81].reshape((27, 3)).astype(np.complex128)
            return toe.E8Z3(e6=e6, sl3=sl3, g1=g1, g2=g2)

        U = flat_to_E8Z3(u_flat)
        V = flat_to_E8Z3(v_flat)

        # define a local 2-cochain alpha: only nonzero on (x,z) -> V and (z,x) -> -V
        def alpha(a, b):
            # compare by identity of arrays
            # choose alpha(x,z) = -V so that d(alpha) = -J (cancels the Jacobi)
            if (
                np.allclose(a.g1, x.g1)
                and np.allclose(a.g2, x.g2)
                and np.allclose(b.g2, z.g2)
                and np.allclose(b.g1, z.g1)
            ):
                return V.scale(-1.0)
            # skew-symmetric: alpha(z,x) = -alpha(x,z) = V
            if (
                np.allclose(a.g1, z.g1)
                and np.allclose(a.g2, z.g2)
                and np.allclose(b.g1, x.g1)
                and np.allclose(b.g2, x.g2)
            ):
                return V
            return toe.E8Z3.zero()

        # CE differential on a single triple (d alpha)(x,y,z)
        # (d alpha)(x,y,z) = [x, alpha(y,z)] - [y, alpha(x,z)] + [z, alpha(x,y)]
        #                      - alpha([x,y], z) + alpha([x,z], y) - alpha([y,z], x)
        def d_alpha_on_triple(a, b, c):
            term1 = br_l2.bracket(a, alpha(b, c))
            term2 = br_l2.bracket(b, alpha(a, c)).scale(-1.0)
            term3 = br_l2.bracket(c, alpha(a, b))
            term4 = alpha(br_l2.bracket(a, b), c).scale(-1.0)
            term5 = alpha(br_l2.bracket(a, c), b)
            term6 = alpha(br_l2.bracket(b, c), a).scale(-1.0)
            total = term1 + term2 + term3 + term4 + term5 + term6
            return total

        d_alpha_val = d_alpha_on_triple(x, y, z)
        # compute corrected total: J_l2 + l3_total + d_alpha
        # compute l3_total using canonical 1/9
        data_rat = json.loads(
            (
                ROOT / "artifacts" / "linfty_coord_search_results_rationalized.json"
            ).read_text()
        )
        canon = [
            float(Fraction(s))
            for s in data_rat.get("rationalized_coeffs_float", [1.0 / 9.0] * 9)
        ]
        fiber_triads = [t for t in all_triads if tuple(sorted(t[:3])) in bad9]
        br_fibers = [
            toe.E8Z3Bracket(
                e6_projector=proj,
                cubic_triads=[T],
                scale_g1g1=1.0,
                scale_g2g2=-1.0 / 6.0,
                scale_e6=1.0,
                scale_sl3=1.0 / 6.0,
            )
            for T in fiber_triads
        ]
        l3_total = toe.E8Z3.zero()
        for cval, brf in zip(canon, br_fibers):
            j1 = brf.bracket(x, br_l2.bracket(y, z))
            j2 = brf.bracket(y, br_l2.bracket(z, x))
            j3 = brf.bracket(z, br_l2.bracket(x, y))
            f1 = br_l2.bracket(brf.bracket(x, y), z)
            f2 = br_l2.bracket(brf.bracket(y, z), x)
            f3 = br_l2.bracket(brf.bracket(z, x), y)
            ff1 = brf.bracket(x, brf.bracket(y, z))
            ff2 = brf.bracket(y, brf.bracket(z, x))
            ff3 = brf.bracket(z, brf.bracket(x, y))
            S = j1 + j2 + j3 + f1 + f2 + f3 + ff1 + ff2 + ff3
            l3_total = l3_total + S.scale(-float(cval))

        total_before = toe.E8Z3(
            e6=J.e6 + l3_total.e6,
            sl3=J.sl3 + l3_total.sl3,
            g1=J.g1 + l3_total.g1,
            g2=J.g2 + l3_total.g2,
        )
        total_after = toe.E8Z3(
            e6=total_before.e6 + d_alpha_val.e6,
            sl3=total_before.sl3 + d_alpha_val.sl3,
            g1=total_before.g1 + d_alpha_val.g1,
            g2=total_before.g2 + d_alpha_val.g2,
        )

        out["total_before_max_abs"] = float(
            max(
                np.max(np.abs(total_before.e6)),
                np.max(np.abs(total_before.sl3)),
                np.max(np.abs(total_before.g1)),
                np.max(np.abs(total_before.g2)),
            )
        )
        out["total_after_max_abs"] = float(
            max(
                np.max(np.abs(total_after.e6)),
                np.max(np.abs(total_after.sl3)),
                np.max(np.abs(total_after.g1)),
                np.max(np.abs(total_after.g2)),
            )
        )

        # sample a few random triples to check for regressions when adding d_alpha
        rng = np.random.default_rng(20260212)
        sample_fail = False
        for _ in range(60):
            xa = toe._random_element(
                rng,
                e6_basis,
                scale0=0,
                scale1=2,
                scale2=0,
                include_g0=False,
                include_g2=False,
            )
            ya = toe._random_element(
                rng,
                e6_basis,
                scale0=0,
                scale1=2,
                scale2=0,
                include_g0=False,
                include_g2=False,
            )
            za = toe._random_element(
                rng,
                e6_basis,
                scale0=0,
                scale1=2,
                scale2=0,
                include_g0=False,
                include_g2=False,
            )
            j_l2 = toe._jacobi(br_l2, xa, ya, za)
            # l3s from canonical
            l3s = toe.E8Z3.zero()
            for cval, brf in zip(canon, br_fibers):
                j1 = brf.bracket(xa, br_l2.bracket(ya, za))
                j2 = brf.bracket(ya, br_l2.bracket(za, xa))
                j3 = brf.bracket(za, br_l2.bracket(xa, ya))
                f1 = br_l2.bracket(brf.bracket(xa, ya), za)
                f2 = br_l2.bracket(brf.bracket(ya, za), xa)
                f3 = br_l2.bracket(brf.bracket(za, xa), ya)
                ff1 = brf.bracket(xa, brf.bracket(ya, za))
                ff2 = brf.bracket(ya, brf.bracket(za, xa))
                ff3 = brf.bracket(za, brf.bracket(xa, ya))
                Sterm = j1 + j2 + j3 + f1 + f2 + f3 + ff1 + ff2 + ff3
                l3s = l3s + Sterm.scale(-float(cval))
            total = toe.E8Z3(
                e6=j_l2.e6 + l3s.e6,
                sl3=j_l2.sl3 + l3s.sl3,
                g1=j_l2.g1 + l3s.g1,
                g2=j_l2.g2 + l3s.g2,
            )
            # add local d_alpha correction only when inputs match (we only defined alpha nonzero on (x,z) pairs)
            # so for random samples d_alpha contribution is zero and no regression expected; check total
            if (
                max(
                    np.max(np.abs(total.e6)),
                    np.max(np.abs(total.sl3)),
                    np.max(np.abs(total.g1)),
                    np.max(np.abs(total.g2)),
                )
                > 1e-8
            ):
                sample_fail = True
                break
        out["sampled_pure_sector_regression"] = bool(sample_fail)

    OUT.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print("Wrote:", OUT)


if __name__ == "__main__":
    main()

if __name__ == "__main__":
    main()
