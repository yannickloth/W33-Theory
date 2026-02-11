from __future__ import annotations

import tools.analyze_e6_f3_trilinear_symmetry_breaking as analyze


def test_gl2_3_involutions_conjugate_to_diag() -> None:
    """All GL(2,3) matrices with det=2 and matrix order 2 are conjugate to diag(-1,1)."""
    diag = (2, 0, 0, 1, 2)  # canonical diag(-1,1)

    mats = [
        m
        for m in analyze._gl2_3()
        if m[4] == 2 and analyze._affine_order((m, (0, 0))) == 2
    ]
    assert mats, "No candidate matrices found"

    for mat in mats:
        found = False
        for U in analyze._gl2_3():
            # conjugate mat by U: U^{-1} * mat * U
            U_inv = analyze._inverse_affine((U, (0, 0)))[0]
            conj = analyze._compose_affine((U_inv, (0, 0)), (mat, (0, 0)))
            conj = analyze._compose_affine(conj, (U, (0, 0)))
            if conj[0] == diag:
                found = True
                break
        assert found, f"Matrix {mat} is not conjugate to diag(-1,1)"
