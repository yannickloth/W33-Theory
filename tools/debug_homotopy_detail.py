#!/usr/bin/env python3
"""Detailed homotopy diagnostics for the recorded failing triple.
Prints the six coboundary terms, U/V support, and exact g1 indices where the
residual appears so we can find the missing/mis-signed component.
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]

# load modules
spec = importlib.util.spec_from_file_location(
    "build", ROOT / "tools" / "build_linfty_firewall_extension.py"
)
build = importlib.util.module_from_spec(spec)
spec.loader.exec_module(build)

spec2 = importlib.util.spec_from_file_location(
    "toe", ROOT / "tools" / "toe_e8_z3graded_bracket_jacobi.py"
)
toe = importlib.util.module_from_spec(spec2)
spec2.loader.exec_module(toe)

# setup
_e6 = np.load(ROOT / "artifacts" / "e6_27rep_basis_export" / "E6_basis_78.npy").astype(
    np.complex128
)
proj = toe.E6Projector(_e6)
all_triads = toe._load_signed_cubic_triads()
rat = json.loads(
    (ROOT / "artifacts" / "linfty_coord_search_results_rationalized.json").read_text()
)
bad9 = set(tuple(sorted(t)) for t in rat["original"]["fiber_triads"])
linfty = build.LInftyE8Extension(toe, proj, all_triads, bad9, l3_scale=1.0 / 9.0)

# attach symbolic l4 + assembled CE2 (loader will attach CE2 alpha)
linfty.attach_l4_from_symbolic_constants(
    ROOT / "artifacts" / "l4_symbolic_constants.json"
)

# failing triple
exh = json.loads(
    (ROOT / "artifacts" / "exhaustive_homotopy_rationalized_l3.json").read_text()
)
ft = exh["sectors"]["g1_g1_g2"]["first_fail"]
# load basis helpers via importlib so script works when run standalone
spec_exh = importlib.util.spec_from_file_location(
    "exh", ROOT / "tools" / "exhaustive_homotopy_check_rationalized_l3.py"
)
exh = importlib.util.module_from_spec(spec_exh)
spec_exh.loader.exec_module(exh)

x = exh.basis_elem_g1(toe, tuple(ft["a"]))
y = exh.basis_elem_g1(toe, tuple(ft["b"]))
z = exh.basis_elem_g2(toe, tuple(ft["c"]))


# helpers
def flat_g1_indices(arr):
    # return list of (i,j,val) for nonzero entries in g1 matrix
    res = []
    g1 = arr.g1
    nz = np.argwhere(np.abs(g1) > 1e-12)
    for r in nz:
        i, j = int(r[0]), int(r[1])
        res.append((i, j, float(g1[i, j])))
    return res


print("Failing triple:", ft)

J = toe._jacobi(linfty.br_l2, x, y, z)
print("Jacobi(l2).g1 nonzero entries:", flat_g1_indices(J))
print("||Jacobi(l2).g1|| =", float(np.max(np.abs(J.g1))))

l3v = linfty.l3(x, y, z)
print("l3(x,y,z).g1 nonzero entries:", flat_g1_indices(l3v))
print("||l3.g1|| =", float(np.max(np.abs(l3v.g1))))

# CE2 alpha callable — be robust if loader didn't attach _ce2_alpha
if hasattr(linfty, "_ce2_alpha") and linfty._ce2_alpha is not None:
    alpha_fn = linfty._ce2_alpha
else:
    print(
        "Warning: linfty._ce2_alpha not set by loader — constructing alpha from artifact for diagnosis"
    )
    ce2 = json.loads(
        (ROOT / "artifacts" / "ce2_rational_local_solutions.json").read_text()
    )

    # inspect CE2 artifact entry for the failing triple
    key_ft = (
        f"{ft['a'][0]},{ft['a'][1]}:{ft['b'][0]},{ft['b'][1]}:{ft['c'][0]},{ft['c'][1]}"
    )
    e_ft = ce2.get(key_ft)
    print("\nCE2 artifact entry for failing triple key=", key_ft)
    if e_ft is None:
        print("  <not present>")
    else:
        nonzero_U = [i for i, s in enumerate(e_ft.get("U_rats", [])) if s != "0"]
        nonzero_V = [i for i, s in enumerate(e_ft.get("V_rats", [])) if s != "0"]
        print("  U_nonzero_count=", len(nonzero_U), "V_nonzero_count=", len(nonzero_V))
        print(
            "  sample V_nonzero (first 6) indices and values=",
            [(i, e_ft["V_rats"][i]) for i in nonzero_V[:6]],
        )

        # map first few nonzero indices to sectors
        def idx_to_sector(idx):
            N = 27 * 27
            if idx < N:
                # e6: row = idx // 27, col = idx % 27
                return ("e6", idx // 27, idx % 27)
            idx -= N
            if idx < 9:
                return ("sl3", idx // 3, idx % 3)
            idx -= 9
            if idx < 81:
                return ("g1", idx // 3, idx % 3)
            idx -= 81
            if idx < 81:
                return ("g2", idx // 3, idx % 3)
            return ("unknown", idx)

        print(
            "  V_nonzero sector mapping (first 6)=",
            [idx_to_sector(i) for i in nonzero_V[:6]],
        )

    def alpha_from_artifact(A, B):
        # match the make_alpha_from_rats logic in assemble_exact_l4_from_local_ce2
        from fractions import Fraction

        for k, e in ce2.items():
            a_idx = tuple(e["a"])
            b_idx = tuple(e["b"])
            c_idx = tuple(e["c"])
            U_rats = [Fraction(s) if s != "0" else None for s in e.get("U_rats", [])]
            V_rats = [Fraction(s) if s != "0" else None for s in e.get("V_rats", [])]
            U_num = np.array(
                [float(fr) if fr is not None else 0.0 for fr in U_rats],
                dtype=np.complex128,
            )
            V_num = np.array(
                [float(fr) if fr is not None else 0.0 for fr in V_rats],
                dtype=np.complex128,
            )

            # numeric flat -> E8Z3
            def flat_to_e8(vec):
                N = 27 * 27
                e6 = vec[:N].reshape((27, 27)).astype(np.complex128)
                off = N
                sl3 = vec[off : off + 9].reshape((3, 3)).astype(np.complex128)
                off += 9
                g1 = vec[off : off + 81].reshape((27, 3)).astype(np.complex128)
                off += 81
                g2 = vec[off : off + 81].reshape((27, 3)).astype(np.complex128)
                return toe.E8Z3(e6=e6, sl3=sl3, g1=g1, g2=g2)

            U_e = flat_to_e8(U_num)
            V_e = flat_to_e8(V_num)
            # matching conditions as in assemble_exact_l4_from_local_ce2.make_alpha_from_rats
            if (np.allclose(A.g1, toe.E8Z3.zero().g1) is False) and (
                np.allclose(B.g2, toe.E8Z3.zero().g2) is False
            ):
                if (
                    np.allclose(A.g1, toe.E8Z3.zero().g1) is False
                    and np.allclose(B.g2, toe.E8Z3.zero().g2) is False
                ):
                    pass
            if np.allclose(A.g1, toe.E8Z3.zero().g1) and np.allclose(
                B.g2, toe.E8Z3.zero().g2
            ):
                continue
            # match explicit pairs
            if (
                np.allclose(A.g1, toe.E8Z3.zero().g1) is False
                and np.allclose(B.g2, toe.E8Z3.zero().g2) is False
            ):
                # alpha(y,z) = U
                if np.allclose(A.g1, toe.E8Z3.zero().g1) is False:
                    pass
            # comparisons using basis_elem helpers
            # use `exh` helpers already loaded in this script
            if np.allclose(A.g1, exh.basis_elem_g1(toe, b_idx).g1) and np.allclose(
                B.g2, exh.basis_elem_g2(toe, c_idx).g2
            ):
                return U_e
            if np.allclose(A.g1, exh.basis_elem_g1(toe, c_idx).g1) and np.allclose(
                B.g2, exh.basis_elem_g2(toe, b_idx).g2
            ):
                return U_e.scale(-1.0)
            if np.allclose(A.g1, exh.basis_elem_g1(toe, a_idx).g1) and np.allclose(
                B.g2, exh.basis_elem_g2(toe, c_idx).g2
            ):
                return V_e
            if np.allclose(A.g1, exh.basis_elem_g1(toe, c_idx).g1) and np.allclose(
                B.g2, exh.basis_elem_g2(toe, a_idx).g2
            ):
                return V_e.scale(-1.0)
        return toe.E8Z3.zero()

    alpha_fn = alpha_from_artifact

U_e8 = alpha_fn(y, z)
V_e8 = alpha_fn(x, z)
print("alpha(y,z)=U nonzero g1 entries:", flat_g1_indices(U_e8))
print("alpha(x,z)=V nonzero g1 entries:", flat_g1_indices(V_e8))
print(
    "||U||, ||V|| =",
    float(np.max(np.abs(U_e8.g1))) if U_e8.g1.size else 0.0,
    float(np.max(np.abs(V_e8.g1))) if V_e8.g1.size else 0.0,
)
# individual coboundary/bracket terms used in d(alpha)
term1 = linfty.br_l2.bracket(x, alpha_fn(y, z))
term2 = linfty.br_l2.bracket(y, alpha_fn(x, z)).scale(-1.0)
term3 = linfty.br_l2.bracket(z, alpha_fn(x, y))
term4 = alpha_fn(linfty.br_l2.bracket(x, y), z).scale(-1.0)
term5 = alpha_fn(linfty.br_l2.bracket(x, z), y)
term6 = alpha_fn(linfty.br_l2.bracket(y, z), x).scale(-1.0)

print("\nCoboundary individual terms (g1 nonzero indices):")
for idx, t in enumerate((term1, term2, term3, term4, term5, term6), start=1):
    print(
        f" term{idx} nonzero:",
        flat_g1_indices(t),
        "||g1||=",
        float(np.max(np.abs(t.g1))) if t.g1.size else 0.0,
    )

d_alpha = linfty.d_alpha_on_triple(x, y, z)
print("\nd_alpha_on_triple.g1 nonzero indices:", flat_g1_indices(d_alpha))
print("||d_alpha.g1|| =", float(np.max(np.abs(d_alpha.g1))))

# total homotopy
tot = linfty.homotopy_jacobi(x, y, z)
print("\nhomotopy_jacobi.g1 nonzero indices:", flat_g1_indices(tot))
print("||homotopy_jacobi.g1|| =", float(np.max(np.abs(tot.g1))))

# compare bracket(x,U) - bracket(y,V) vs -(J + l3)
lhs = linfty.br_l2.bracket(x, U_e8) + linfty.br_l2.bracket(y, V_e8).scale(-1.0)
rhs = -(J + l3v)
print("\nbracket(x,U) - bracket(y,V) g1 nonzero:", flat_g1_indices(lhs))
print("-(J + l3) g1 nonzero:", flat_g1_indices(rhs))
print("max abs diff (lhs - rhs) g1 =", float(np.max(np.abs(lhs.g1 - rhs.g1))))

print("\nDone")
