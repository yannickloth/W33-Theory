import importlib.util
import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]

# load toe and LInfty helper
spec = importlib.util.spec_from_file_location(
    "toe", ROOT / "tools" / "toe_e8_z3graded_bracket_jacobi.py"
)
toe = importlib.util.module_from_spec(spec)
import sys

sys.modules[spec.name] = toe
spec.loader.exec_module(toe)

from tools.build_linfty_firewall_extension import LInftyE8Extension
from tools.exhaustive_homotopy_check_rationalized_l3 import basis_elem_g1, basis_elem_g2

# projector/br_l2 setup
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
linfty = LInftyE8Extension(toe, proj, all_triads, bad9, l3_scale=1.0 / 9.0)

# attach symbolic l4 (if present) and CE2 alpha from artifact
symp = ROOT / "artifacts" / "l4_symbolic_constants.json"
if symp.exists():
    linfty.attach_l4_from_symbolic_constants(symp)

ce2p = ROOT / "artifacts" / "ce2_rational_local_solutions.json"
if ce2p.exists():
    ce2 = json.loads(ce2p.read_text(encoding="utf-8"))
    from fractions import Fraction

    def flat_to_e8(vec_flat):
        N = 27 * 27
        e6 = vec_flat[:N].reshape((27, 27)).astype(np.complex128)
        off = N
        sl3 = vec_flat[off : off + 9].reshape((3, 3)).astype(np.complex128)
        off += 9
        g1 = vec_flat[off : off + 81].reshape((27, 3)).astype(np.complex128)
        off += 81
        g2 = vec_flat[off : off + 81].reshape((27, 3)).astype(np.complex128)
        return toe.E8Z3(e6=e6, sl3=sl3, g1=g1, g2=g2)

    def alpha_global(a, b):
        acc = toe.E8Z3.zero()
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
            U_e8 = flat_to_e8(U_num)
            V_e8 = flat_to_e8(V_num)
            # matching logic from assemble_exact_l4_from_local_ce2
            if np.allclose(a.g1, basis_elem_g1(toe, b_idx).g1) and np.allclose(
                b.g2, basis_elem_g2(toe, c_idx).g2
            ):
                acc = acc + U_e8
            if np.allclose(a.g1, basis_elem_g1(toe, c_idx).g1) and np.allclose(
                b.g2, basis_elem_g2(toe, b_idx).g2
            ):
                acc = acc - U_e8
            if np.allclose(a.g1, basis_elem_g1(toe, a_idx).g1) and np.allclose(
                b.g2, basis_elem_g2(toe, c_idx).g2
            ):
                acc = acc + V_e8
            if np.allclose(a.g1, basis_elem_g1(toe, c_idx).g1) and np.allclose(
                b.g2, basis_elem_g2(toe, a_idx).g2
            ):
                acc = acc - V_e8
        return acc

    linfty.attach_l4_from_ce2(alpha_global)

# evaluate homotopy_jacobi for two triples
x = basis_elem_g1(toe, (0, 0))
y = basis_elem_g1(toe, (17, 1))
z0 = basis_elem_g2(toe, (3, 0))
z1 = basis_elem_g2(toe, (3, 1))

hj0 = linfty.homotopy_jacobi(x, y, z0)
hj1 = linfty.homotopy_jacobi(x, y, z1)


def mag(e):
    return max(
        0.0 if e.e6.size == 0 else float(np.max(np.abs(e.e6))),
        0.0 if e.sl3.size == 0 else float(np.max(np.abs(e.sl3))),
        0.0 if e.g1.size == 0 else float(np.max(np.abs(e.g1))),
        0.0 if e.g2.size == 0 else float(np.max(np.abs(e.g2))),
    )


print("homotopy_jacobi mag for (3,0)=", mag(hj0))
print("homotopy_jacobi mag for (3,1)=", mag(hj1))
