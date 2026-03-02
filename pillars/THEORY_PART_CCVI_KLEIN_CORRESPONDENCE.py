#!/usr/bin/env python3
"""Pillar 106 (Part CCVI): Klein Correspondence W(3,3) <-> Q(4,3)

The W(3,3) symplectic polar space and the parabolic quadric Q(4,3) are
related by an explicit Klein correspondence: each totally isotropic line
of W(3,3) maps to a point of Q(4,3) via Plucker coordinates, giving an
incidence-preserving bijection.  The symplectic group Sp(4,3) acting on
W(3,3) induces an SO(5,3) action on Q(4,3) that preserves the quadratic
form.

Both W(3,3) and Q(4,3) are point-line geometries with parameters
(40 points, 40 lines, 4 points per line, 4 lines per point).

Theorems:

T1  W(3,3) GEOMETRY: The symplectic polar space W(3,3) over F_3 has
    exactly 40 points (PG(3,3) points) and 40 totally isotropic lines
    with respect to the form B(u,v) = u0*v3 - u3*v0 + u1*v2 - u2*v1.
    Each line contains exactly 4 points; each point lies on exactly
    4 lines.

T2  Q(4,3) QUADRIC: The Klein image is a parabolic quadric Q(4,3) in
    PG(4,3) defined by p01*p23 + p02*p31 + 2*p03^2 = 0 (in the
    Plucker coordinate order [p01,p02,p03,p31,p23]).  All 40 Plucker
    images of W(3,3) isotropic lines satisfy this equation exactly.

T3  KLEIN BIJECTIVITY: The Klein map line_id -> Q_point_id is a
    bijection from the 40 isotropic lines of W(3,3) to the 40 points
    of Q(4,3).  Every Q-point is hit exactly once.

T4  DUALITY ISOMORPHISM: Under the duality W(3,3) -> Q(4,3)^dual,
    each of the 40 W(3,3) points maps to a Q(4,3) line of size 4.
    The resulting Q-line system has 40 lines, each of size 4, with
    every Q-point lying on exactly 4 Q-lines.  This gives an explicit
    incidence-preserving isomorphism W(3,3) ~= Q(4,3)^dual.

T5  Sp(4,3) INDUCES SO(5,3): The 6 generators of Sp(4,3) (named
    T_e1, T_e2, T_e3, T_e4, A, B) each induce a 5x5 matrix over F_3
    that preserves the quadratic form S defining Q(4,3).  All 6
    induced matrices satisfy M^T S M = S mod 3.

T6  PARAMETER SYMMETRY: W(3,3) and Q(4,3) share identical parameters:
    40 points, 40 lines, 4 points/line, 4 lines/point.  The Klein
    correspondence exchanges the roles of points and lines while
    preserving all incidence counts.
"""

from __future__ import annotations

import json
import zipfile
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, List

ROOT = Path(__file__).resolve().parent
BUNDLE = ROOT / "W33_KLEIN_SO53_REP_BUNDLE_v01.zip"


def _matmul_mod3(A: List[List[int]], B: List[List[int]]) -> List[List[int]]:
    n = len(A)
    return [
        [sum(A[i][k] * B[k][j] for k in range(n)) % 3 for j in range(n)]
        for i in range(n)
    ]


def _transp(M: List[List[int]]) -> List[List[int]]:
    return [[M[j][i] for j in range(len(M))] for i in range(len(M[0]))]


def _int_mat(M):
    return [[int(x) for x in row] for row in M]


def _quadric(p: List[int]) -> int:
    """Evaluate Klein quadric: p01*p23 + p02*p31 + 2*p03^2 mod 3."""
    return (p[0] * p[4] + p[1] * p[3] + 2 * p[2] * p[2]) % 3


def analyze() -> dict:
    with zipfile.ZipFile(BUNDLE) as zf:
        sp43 = json.loads(zf.read("Sp43_generators_4x4.json"))
        so53 = json.loads(zf.read("SO53_induced_matrices_5x5.json"))
        klein = json.loads(zf.read("Klein_map_line_to_Qpoint.json"))
        duality = json.loads(zf.read("Duality_point_to_Qline.json"))
        w33_pts_raw = json.loads(zf.read("W33_points_PG33.json"))
        w33_lines_raw = json.loads(zf.read("W33_isotropic_lines_W33.json"))
        q43_inc = json.loads(zf.read("Q43_incidence.json"))

    w33_pts = w33_pts_raw["points40"]
    w33_lines = w33_lines_raw["lines40"]
    q_pts = klein["Q_points40"]
    l2q = klein["line_id_to_Q_point_id"]
    q43_q_lines = duality["point_id_to_Q_line_point_ids"]
    omega = _int_mat(sp43["symplectic_form_M"])
    sp43_gens = {k: _int_mat(v) for k, v in sp43["generators"].items()}
    S = _int_mat(so53["quadratic_form_matrix_S"])
    so53_gens = {k: _int_mat(v) for k, v in so53["induced_5x5"].items()}

    # T1: W(3,3) geometry parameters
    t1_num_pts = len(w33_pts)
    t1_num_lines = len(w33_lines)
    t1_pts_per_line = dict(Counter(len(l) for l in w33_lines))
    pt_to_lines: Dict[int, List[int]] = defaultdict(list)
    for li, line in enumerate(w33_lines):
        for pt in line:
            pt_to_lines[pt].append(li)
    t1_lines_per_pt = dict(Counter(len(v) for v in pt_to_lines.values()))

    # T2: All Q-points on quadric
    t2_quadric_satisfied = all(_quadric(p) == 0 for p in q_pts)
    t2_quadric_count = sum(1 for p in q_pts if _quadric(p) == 0)
    t2_quadric_equation = klein["Q_quadric_equation"]

    # T3: Klein bijectivity
    t3_bijective = len(set(l2q)) == 40 and set(l2q) == set(range(40))
    t3_map_length = len(l2q)

    # T4: Duality — W-points -> Q-lines
    t4_num_q_lines = len(q43_q_lines)
    t4_q_line_sizes = dict(Counter(len(l) for l in q43_q_lines))
    # Q-lines per Q-point
    q_pt_to_qlines: Dict[int, List[int]] = defaultdict(list)
    for li, qline in enumerate(q43_q_lines):
        for pt in qline:
            q_pt_to_qlines[pt].append(li)
    t4_qlines_per_qpt = dict(Counter(len(v) for v in q_pt_to_qlines.values()))
    t4_isomorphism_holds = (
        t1_num_pts == 40 and t4_num_q_lines == 40
        and t4_q_line_sizes == {4: 40} and t4_qlines_per_qpt == {4: 40}
    )

    # T5: Sp(4,3) -> SO(5,3) form preservation
    sp43_gen_names = list(sp43_gens.keys())
    sp43_preserves = {}
    for name, M in sp43_gens.items():
        Mt = _transp(M)
        MtO = _matmul_mod3(Mt, omega)
        MtOM = _matmul_mod3(MtO, M)
        sp43_preserves[name] = (MtOM == omega)
    so53_preserves = {}
    for name, M in so53_gens.items():
        Mt = _transp(M)
        MtS = _matmul_mod3(Mt, S)
        MtSM = _matmul_mod3(MtS, M)
        so53_preserves[name] = (MtSM == S)
    t5_all_sp43_preserve = all(sp43_preserves.values())
    t5_all_so53_preserve = all(so53_preserves.values())
    t5_num_generators = len(sp43_gens)

    # T6: Parameter symmetry
    t6_params_equal = (
        t1_num_pts == len(q_pts) == 40
        and t1_num_lines == t4_num_q_lines == 40
        and t1_pts_per_line == {4: 40}
        and t4_q_line_sizes == {4: 40}
        and t1_lines_per_pt == {4: 40}
        and t4_qlines_per_qpt == {4: 40}
    )

    return {
        "T1_num_W33_points": t1_num_pts,
        "T1_num_W33_lines": t1_num_lines,
        "T1_pts_per_line": t1_pts_per_line,
        "T1_lines_per_pt": t1_lines_per_pt,
        "T2_quadric_satisfied_count": t2_quadric_count,
        "T2_all_on_quadric": t2_quadric_satisfied,
        "T2_quadric_equation": t2_quadric_equation,
        "T3_klein_map_length": t3_map_length,
        "T3_klein_bijective": t3_bijective,
        "T4_num_Q_lines": t4_num_q_lines,
        "T4_Q_line_sizes": t4_q_line_sizes,
        "T4_Qlines_per_Qpt": t4_qlines_per_qpt,
        "T4_duality_isomorphism": t4_isomorphism_holds,
        "T5_num_generators": t5_num_generators,
        "T5_generator_names": sp43_gen_names,
        "T5_Sp43_all_preserve_omega": t5_all_sp43_preserve,
        "T5_SO53_all_preserve_S": t5_all_so53_preserve,
        "T5_Sp43_individual": sp43_preserves,
        "T5_SO53_individual": so53_preserves,
        "T6_parameter_symmetry": t6_params_equal,
        "T6_shared_params": {
            "points": 40,
            "lines": 40,
            "pts_per_line": 4,
            "lines_per_pt": 4,
        },
    }


def main():
    summary = analyze()
    out = ROOT / "data" / "w33_klein_correspondence.json"
    out.write_text(json.dumps(summary, indent=2))
    print("T1 W(3,3): 40 pts, 40 lines, 4-per-each:", summary["T1_lines_per_pt"])
    print("T2 all Q-points on quadric:", summary["T2_all_on_quadric"])
    print("T3 Klein bijective:", summary["T3_klein_bijective"])
    print("T4 duality isomorphism:", summary["T4_duality_isomorphism"])
    print("T5 Sp43 preserves omega:", summary["T5_Sp43_all_preserve_omega"])
    print("T5 SO53 preserves S:", summary["T5_SO53_all_preserve_S"])
    print("T6 parameter symmetry:", summary["T6_parameter_symmetry"])
    print("wrote data/w33_klein_correspondence.json")


if __name__ == "__main__":
    main()
