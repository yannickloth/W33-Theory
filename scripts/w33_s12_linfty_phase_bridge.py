#!/usr/bin/env python3
"""s12 -> Heisenberg -> E8 Z3/L∞: make the cocycle/phase bridge explicit.

This script ties together three threads in the repo:

1) **s12 (ternary Golay) grade-defined algebra** (`tools/s12_universal_algebra.py`)
   reproduces the Z3 grade split (242,243,243) for the 728 = 27^2-1 basis but
   exhibits a *finite Jacobi obstruction set* when you only keep grade-level
   coefficients (no phases).

2) **Weyl–Heisenberg closure** (`scripts/s12_sl27_heisenberg_algebra.py`) resolves
   this by upgrading "grade-only coefficients" to an honest associative algebra
   (3-qutrit Weyl operators) whose commutator bracket satisfies Jacobi
   automatically.  Algebraically: the missing ingredient is the **2-cocycle /
   phase** given by the symplectic pairing.

3) **E8 Z3 + L∞ firewall** (`tools/build_linfty_firewall_extension.py`) shows the
   same mechanism: the pure-sector Jacobi anomaly is cancelled by l3 supported
   on the 9 Heisenberg fibers ("bad9"), but a recorded **mixed-sector**
   obstruction requires an additional CE-2 coboundary term d(alpha) — i.e. an
   explicit cocycle/phase correction rather than grade-only coefficients.

Run:
  & .venv\\Scripts\\python.exe -X utf8 scripts\\w33_s12_linfty_phase_bridge.py
"""

from __future__ import annotations

import json
import random
import sys
from fractions import Fraction
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = ROOT / "scripts"
for p in (ROOT, SCRIPTS_DIR):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))


def max_abs(e) -> float:
    return float(
        max(
            0.0 if e.e6.size == 0 else np.max(np.abs(e.e6)),
            0.0 if e.sl3.size == 0 else np.max(np.abs(e.sl3)),
            0.0 if e.g1.size == 0 else np.max(np.abs(e.g1)),
            0.0 if e.g2.size == 0 else np.max(np.abs(e.g2)),
        )
    )


def _load_first_ce2_entry(path: Path) -> dict[str, object]:
    """Parse only the first key/value pair from the large CE2 JSON artifact.

    The artifact is a single top-level JSON object mapping "a:b:c" -> payload.
    This helper avoids loading the full 100+MB file when we only need one
    representative entry for demonstration.
    """
    if not path.exists():
        raise FileNotFoundError(path)

    buf: list[str] = ["{"]
    depth = 0
    started = False
    with open(path, "r", encoding="utf-8") as f:
        # skip the opening "{"
        first = f.readline()
        if "{" not in first:
            raise ValueError("Unexpected JSON header (expected '{').")

        for line in f:
            buf.append(line.rstrip("\n"))
            if not started:
                # first entry line contains the value object opening "{"
                if "{" in line:
                    started = True
                    depth += line.count("{") - line.count("}")
            else:
                depth += line.count("{") - line.count("}")

            if started and depth == 0:
                # strip trailing comma after the first entry, if present
                if buf[-1].rstrip().endswith(","):
                    buf[-1] = buf[-1].rstrip().rstrip(",")
                break

    buf.append("}")
    obj = json.loads("\n".join(buf))
    if not isinstance(obj, dict) or len(obj) != 1:
        raise ValueError("Failed to parse a single-entry CE2 payload.")
    key = next(iter(obj.keys()))
    payload = obj[key]
    if not isinstance(payload, dict):
        raise ValueError("Unexpected CE2 entry payload type.")
    return {"key": key, "payload": payload}


def _flat_to_e8(toe, vec_flat: np.ndarray):
    N = 27 * 27
    e6 = vec_flat[:N].reshape((27, 27)).astype(np.complex128)
    off = N
    sl3 = vec_flat[off : off + 9].reshape((3, 3)).astype(np.complex128)
    off += 9
    g1 = vec_flat[off : off + 81].reshape((27, 3)).astype(np.complex128)
    off += 81
    g2 = vec_flat[off : off + 81].reshape((27, 3)).astype(np.complex128)
    return toe.E8Z3(e6=e6, sl3=sl3, g1=g1, g2=g2)


def main() -> None:
    print("=" * 78)
    print("ALGEBRA BRIDGE: s12 grade obstruction -> Heisenberg cocycle -> E8 Z3/L∞")
    print("=" * 78)

    # -------------------------------------------------------------------------
    # §1. s12: grade-only Jacobi obstruction vs Heisenberg closure
    # -------------------------------------------------------------------------
    from s12_sl27_heisenberg_algebra import _build_golay_labels, jacobi_coeff

    import tools.s12_universal_algebra as s12

    labels = _build_golay_labels()
    by_grade = {0: 0, 1: 0, 2: 0}
    for lab in labels:
        by_grade[int(lab.grade)] += 1

    laws = s12.verify_universal_grade_laws()
    jacobi_fail = int(laws.get("jacobi_failure_count", -1))

    print()
    print("§1. s12 vs Weyl–Heisenberg closure")
    print("-" * 50)
    print(f"  Nonzero basis size: {len(labels)} (expected 728 = 27^2-1)")
    print(f"  Grade split: {by_grade} (expected 242/243/243)")
    print(f"  s12 grade-only Jacobi failure count: {jacobi_fail} (expected 6)")
    assert len(labels) == 728
    assert by_grade == {0: 242, 1: 243, 2: 243}
    assert jacobi_fail == 6

    rng = random.Random(42)
    trials = 5000
    for _ in range(trials):
        a, b, c = rng.sample(labels, 3)
        if jacobi_coeff(a.u, b.u, c.u) != 0:
            raise AssertionError("Heisenberg symplectic Jacobi coefficient nonzero")
    print(f"  Heisenberg symplectic Jacobi sample: 0 / {trials} failures")
    print("  ✓ Missing ingredient = phase/cocycle (symplectic pairing)")

    # -------------------------------------------------------------------------
    # §2. E6(27) Heisenberg coordinates: bad9 fibers are {u}×Z3
    # -------------------------------------------------------------------------
    model_path = ROOT / "artifacts" / "e6_cubic_affine_heisenberg_model.json"
    fw_path = ROOT / "artifacts" / "firewall_bad_triads_mapping.json"

    model = json.loads(model_path.read_text(encoding="utf-8"))
    fw = json.loads(fw_path.read_text(encoding="utf-8"))

    e6id_to_h = model["e6id_to_heisenberg"]
    fiber_triads = model["fiber_triads_e6id"]
    fw_bad = fw["bad_triangles_Schlafli_e6id"]

    fiber_set = {tuple(int(x) for x in t) for t in fiber_triads}
    fw_set = {tuple(int(x) for x in t) for t in fw_bad}
    assert fiber_set == fw_set

    u_points: set[tuple[int, int]] = set()
    print()
    print("§2. Firewall bad9 = Heisenberg fibers in E6 27-rep")
    print("-" * 50)
    for triad in sorted(fiber_set):
        coords = []
        for e6id in triad:
            h = e6id_to_h[str(e6id)]
            u = tuple(int(x) for x in h["u"])
            z = int(h["z"])
            coords.append((u, z))
        u0 = coords[0][0]
        zs = {z for _, z in coords}
        assert all(u == u0 for u, _ in coords)
        assert zs == {0, 1, 2}
        u_points.add(u0)
        print(f"  triad {triad}: u={u0} z-set={sorted(zs)}")

    all_u = {(i, j) for i in range(3) for j in range(3)}
    print(f"  distinct fibers (u points): {len(u_points)} (expected 9)")
    assert u_points == all_u
    print("  ✓ Each bad triad is a fiber {u}×Z3 and the 9 fibers cover F3^2")

    # -------------------------------------------------------------------------
    # §3. Mixed-sector obstruction: l3 supported on fibers is insufficient;
    #     a CE-2 coboundary (explicit cocycle) cancels the remaining anomaly.
    # -------------------------------------------------------------------------
    from tools.build_linfty_firewall_extension import (
        LInftyE8Extension,
        _load_bad9,
        _load_bracket_tool,
    )
    from tools.exhaustive_homotopy_check_rationalized_l3 import (
        basis_elem_g1,
        basis_elem_g2,
    )

    toe = _load_bracket_tool()
    e6_basis = np.load(ROOT / "artifacts" / "e6_27rep_basis_export" / "E6_basis_78.npy")
    e6_basis = e6_basis.astype(np.complex128)
    proj = toe.E6Projector(e6_basis)
    all_triads = toe._load_signed_cubic_triads()
    bad9 = _load_bad9()

    linfty = LInftyE8Extension(toe, proj, all_triads, bad9, l3_scale=1.0 / 9.0)

    a_idx = (0, 0)
    b_idx = (17, 1)
    c_idx = (3, 0)
    x = basis_elem_g1(toe, a_idx)
    y = basis_elem_g1(toe, b_idx)
    z = basis_elem_g2(toe, c_idx)

    j = toe._jacobi(linfty.br_l2, x, y, z)
    l3 = linfty.l3(x, y, z)
    residual_no_ce2 = j + l3

    print()
    print("§3. Mixed g1_g1_g2 obstruction and CE2 cocycle cancellation")
    print("-" * 50)
    print(f"  mixed triple: g1{a_idx}, g1{b_idx}, g2{c_idx}")
    print(f"  ||Jacobi(l2)||_inf = {max_abs(j):.6g}")
    print(f"  ||l3||_inf        = {max_abs(l3):.6g}")
    print(f"  ||J+l3||_inf      = {max_abs(residual_no_ce2):.6g}")
    assert max_abs(residual_no_ce2) > 1e-10

    # Load a representative sparse rational CE2 entry (stored as Fractions) and
    # attach it as an explicit cocycle/phase correction.
    ce2_path = ROOT / "artifacts" / "ce2_rational_local_solutions.json"
    first = _load_first_ce2_entry(ce2_path)
    ce2_key = str(first["key"])
    payload = first["payload"]
    if not isinstance(payload, dict):
        raise AssertionError("Unexpected CE2 payload type.")

    # This artifact is built around the canonical mixed triple:
    #   (0,0) : (17,1) : (3,0)
    print(f"  CE2 sample key: {ce2_key}")
    assert ce2_key == "0,0:17,1:3,0"

    U_rats = payload.get("U_rats", [])
    V_rats = payload.get("V_rats", [])
    if not isinstance(U_rats, list) or not isinstance(V_rats, list):
        raise AssertionError("Unexpected CE2 U/V arrays.")
    if len(U_rats) != 900 or len(V_rats) != 900:
        raise AssertionError("Expected flattened E8Z3 arrays of length 900.")

    U_nz = [(i, str(s)) for i, s in enumerate(U_rats) if str(s) != "0"]
    V_nz = [(i, str(s)) for i, s in enumerate(V_rats) if str(s) != "0"]
    print(f"  U nonzeros: {len(U_nz)}")
    print(f"  V nonzeros: {len(V_nz)}")
    if V_nz:
        idx0, val0 = V_nz[0]
        i0, j0 = idx0 // 27, idx0 % 27
        print(f"  V[flat={idx0}] = {val0}  (e6[{i0},{j0}] in flattened layout)")
    assert (len(U_nz), len(V_nz)) == (0, 1)
    assert V_nz[0][1] == "1/54" and V_nz[0][0] == 179

    # Build E8Z3 elements U and V from the sparse rational arrays.
    U_flat = np.zeros(900, dtype=np.complex128)
    V_flat = np.zeros(900, dtype=np.complex128)
    for idx, s in U_nz:
        U_flat[idx] = float(Fraction(s))
    for idx, s in V_nz:
        V_flat[idx] = float(Fraction(s))

    U = _flat_to_e8(toe, U_flat)
    V = _flat_to_e8(toe, V_flat)

    def alpha(a, b):
        # alpha(x, z) = V and skew-symmetry alpha(z, x) = -V
        if (
            np.allclose(a.g1, x.g1)
            and np.allclose(a.g2, x.g2)
            and np.allclose(b.g1, z.g1)
            and np.allclose(b.g2, z.g2)
        ):
            return V
        if (
            np.allclose(a.g1, z.g1)
            and np.allclose(a.g2, z.g2)
            and np.allclose(b.g1, x.g1)
            and np.allclose(b.g2, x.g2)
        ):
            return V.scale(-1.0)

        # (This sample entry has U=0, but keep the pattern explicit.)
        if max_abs(U) > 0 and (
            np.allclose(a.g1, y.g1)
            and np.allclose(a.g2, y.g2)
            and np.allclose(b.g1, z.g1)
            and np.allclose(b.g2, z.g2)
        ):
            return U
        if max_abs(U) > 0 and (
            np.allclose(a.g1, z.g1)
            and np.allclose(a.g2, z.g2)
            and np.allclose(b.g1, y.g1)
            and np.allclose(b.g2, y.g2)
        ):
            return U.scale(-1.0)
        return toe.E8Z3.zero()

    linfty.attach_ce2_alpha(alpha)

    dalpha = linfty.d_alpha_on_triple(x, y, z)
    residual_with_ce2 = residual_no_ce2 + dalpha
    print(f"  ||d(alpha)||_inf  = {max_abs(dalpha):.6g}")
    print(f"  ||J+l3+dα||_inf   = {max_abs(residual_with_ce2):.6g}")
    assert max_abs(residual_with_ce2) < 1e-10

    print("  ✓ Mixed-sector anomaly cancelled by an explicit CE-2 cocycle/phase")

    print()
    print("OK: same resolution mechanism across s12 and the E8 Z3/L∞ firewall.")


if __name__ == "__main__":
    main()
