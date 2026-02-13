import numpy as np

from tools.build_linfty_firewall_extension import LInftyE8Extension, _load_bracket_tool


def max_abs(e):
    return float(
        max(
            0.0 if e.e6.size == 0 else np.max(np.abs(e.e6)),
            0.0 if e.sl3.size == 0 else np.max(np.abs(e.sl3)),
            0.0 if e.g1.size == 0 else np.max(np.abs(e.g1)),
            0.0 if e.g2.size == 0 else np.max(np.abs(e.g2)),
        )
    )


def basis_elem_g1(toe_mod, idx):
    i, j = idx
    e = toe_mod.E8Z3.zero()
    arr = np.zeros((27, 3), dtype=np.complex128)
    arr[i, j] = 1.0
    return toe_mod.E8Z3(e6=e.e6, sl3=e.sl3, g1=arr, g2=e.g2)


def test_failing_triple_cancelled():
    toe = _load_bracket_tool()
    basis_path = "artifacts/e6_27rep_basis_export/E6_basis_78.npy"
    e6_basis = np.load(basis_path).astype(np.complex128)
    proj = toe.E6Projector(e6_basis)
    all_triads = toe._load_signed_cubic_triads()

    # load bad9 from module helper
    from tools.build_linfty_firewall_extension import _load_bad9

    bad9 = _load_bad9()

    # build L∞ with canonical scale = 1/9 (constructor default in tool)
    linfty = LInftyE8Extension(toe, proj, all_triads, bad9, l3_scale=1.0 / 9.0)

    # previously failing triple discovered by exhaustive check
    a_idx = (0, 0)
    b_idx = (1, 1)
    c_idx = (21, 2)

    x = basis_elem_g1(toe, a_idx)
    y = basis_elem_g1(toe, b_idx)
    z = basis_elem_g1(toe, c_idx)

    # homotopy Jacobi should be (numerically) zero for this triple
    total = linfty.homotopy_jacobi(x, y, z)
    assert max_abs(total) < 1e-12


def test_random_g1_samples_reduce_to_zero():
    toe = _load_bracket_tool()
    basis_path = "artifacts/e6_27rep_basis_export/E6_basis_78.npy"
    e6_basis = np.load(basis_path).astype(np.complex128)
    proj = toe.E6Projector(e6_basis)
    all_triads = toe._load_signed_cubic_triads()
    from tools.build_linfty_firewall_extension import _load_bad9

    bad9 = _load_bad9()
    linfty = LInftyE8Extension(toe, proj, all_triads, bad9, l3_scale=1.0 / 9.0)

    rng = np.random.default_rng(20260212)

    # sample 20 random g1 triples where Jacobi(l2).e6 != 0 and assert homotopy residual==0
    count = 0
    for _ in range(200):
        x = toe._random_element(
            rng,
            e6_basis,
            scale0=0,
            scale1=2,
            scale2=0,
            include_g0=False,
            include_g2=False,
        )
        y = toe._random_element(
            rng,
            e6_basis,
            scale0=0,
            scale1=2,
            scale2=0,
            include_g0=False,
            include_g2=False,
        )
        z = toe._random_element(
            rng,
            e6_basis,
            scale0=0,
            scale1=2,
            scale2=0,
            include_g0=False,
            include_g2=False,
        )
        j_l2 = toe._jacobi(linfty.br_l2, x, y, z)
        if np.max(np.abs(j_l2.e6)) < 1e-12:
            continue
        total = linfty.homotopy_jacobi(x, y, z)
        assert max_abs(total) < 1e-10
        count += 1
        if count >= 20:
            break
    assert count >= 5


def test_mixed_triple_not_cancelled_by_rational_candidate():
    """Confirm the canonical/rationalized l3 alone does NOT cancel the known
    mixed g1_g1_g2 obstruction (regression test reproducing the documented
    failing triple).
    """
    import json

    from tools.build_linfty_firewall_extension import _load_bad9, _load_bracket_tool
    from tools.exhaustive_homotopy_check_rationalized_l3 import (
        assemble_l3_total_from_coeffs,
        basis_elem_g1,
        basis_elem_g2,
    )

    toe = _load_bracket_tool()
    basis_path = "artifacts/e6_27rep_basis_export/E6_basis_78.npy"
    e6_basis = np.load(basis_path).astype(np.complex128)
    proj = toe.E6Projector(e6_basis)
    all_triads = toe._load_signed_cubic_triads()

    # load the rationalized coefficients from artifact
    data = json.loads(
        open(
            "artifacts/linfty_coord_search_results_rationalized.json",
            "r",
            encoding="utf-8",
        ).read()
    )
    coeffs = data.get("rationalized_coeffs_float")
    assert coeffs is not None

    bad9 = _load_bad9()

    br_l2 = toe.E8Z3Bracket(
        e6_projector=proj,
        cubic_triads=[t for t in all_triads if tuple(sorted(t[:3])) not in bad9],
        scale_g1g1=1.0,
        scale_g2g2=-1.0 / 6.0,
        scale_e6=1.0,
        scale_sl3=1.0 / 6.0,
    )

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

    # failing triple from exhaustive check
    a_idx = (0, 0)
    b_idx = (17, 1)
    c_idx = (3, 0)

    x = basis_elem_g1(toe, a_idx)
    y = basis_elem_g1(toe, b_idx)
    z = basis_elem_g2(toe, c_idx)

    j_l2 = toe._jacobi(br_l2, x, y, z)
    l3_total = assemble_l3_total_from_coeffs(coeffs, br_l2, br_fibers, toe, x, y, z)
    total = toe.E8Z3(
        e6=j_l2.e6 + l3_total.e6,
        sl3=j_l2.sl3 + l3_total.sl3,
        g1=j_l2.g1 + l3_total.g1,
        g2=j_l2.g2 + l3_total.g2,
    )

    # rationalized l3 on the 9 fibers is NOT sufficient for this mixed triple
    assert max_abs(total) > 1e-10


def test_mixed_triple_cancelled_by_l3_plus_ce2chain():
    """Use the local CE 2-cochain solver (l4 prototype) to cancel the mixed
    obstruction without regressing pure sectors."""
    from tools.build_linfty_firewall_extension import (
        LInftyE8Extension,
        _load_bad9,
        _load_bracket_tool,
    )

    toe = _load_bracket_tool()
    basis_path = "artifacts/e6_27rep_basis_export/E6_basis_78.npy"
    e6_basis = np.load(basis_path).astype(np.complex128)
    proj = toe.E6Projector(e6_basis)
    all_triads = toe._load_signed_cubic_triads()
    bad9 = _load_bad9()

    linfty = LInftyE8Extension(toe, proj, all_triads, bad9, l3_scale=1.0 / 9.0)

    # failing triple
    a_idx = (0, 0)
    b_idx = (17, 1)
    c_idx = (3, 0)
    from tools.exhaustive_homotopy_check_rationalized_l3 import (
        basis_elem_g1,
        basis_elem_g2,
    )

    x = basis_elem_g1(toe, a_idx)
    y = basis_elem_g1(toe, b_idx)
    z = basis_elem_g2(toe, c_idx)

    alpha = linfty.compute_local_ce2_alpha_for_triple(x, y, z)
    assert alpha is not None

    linfty.attach_ce2_alpha(alpha)

    total = linfty.homotopy_jacobi(x, y, z)
    assert max_abs(total) < 1e-10

    # sanity: random pure-sector triples should not regress when alpha is attached
    rng = np.random.default_rng(20260212)
    for _ in range(30):
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
        hj = linfty.homotopy_jacobi(xa, ya, za)
        assert max_abs(hj) < 1e-8

    # promote the attached CE2 to a global l4 prototype and verify equivalence
    linfty.attach_l4_from_ce2(alpha)

    # detach the CE2 and ensure the l4 prototype alone cancels the triple
    linfty.detach_ce2_alpha()

    total_l4_only = linfty.homotopy_jacobi(x, y, z)
    assert max_abs(total_l4_only) < 1e-10

    # ensure pure sectors remain OK with l4 attached
    rng = np.random.default_rng(20260212)
    for _ in range(30):
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
        hj = linfty.homotopy_jacobi(xa, ya, za)
        assert max_abs(hj) < 1e-8

    linfty.detach_l4()


def test_global_l4_assembled_from_local_alphas():
    """Assemble a global CE2 -> l4 from local per‑triple solutions and verify
    it cancels every failing triple recorded by the exhaustive verifier.
    """
    from tools.build_linfty_firewall_extension import (
        LInftyE8Extension,
        _load_bad9,
        _load_bracket_tool,
    )

    toe = _load_bracket_tool()
    basis_path = "artifacts/e6_27rep_basis_export/E6_basis_78.npy"
    e6_basis = np.load(basis_path).astype(np.complex128)
    proj = toe.E6Projector(e6_basis)
    all_triads = toe._load_signed_cubic_triads()
    bad9 = _load_bad9()

    linfty = LInftyE8Extension(toe, proj, all_triads, bad9, l3_scale=1.0 / 9.0)

    # load exhaustive artifact (may contain one or more failing triples)
    import json

    exh = json.loads(
        open(
            "artifacts/exhaustive_homotopy_rationalized_l3.json", "r", encoding="utf-8"
        ).read()
    )

    # support two artifact shapes: either an explicit `failing_examples` list
    # or a single `first_fail` entry produced by the exhaustive verifier.
    g1g1g2 = exh["sectors"].get("g1_g1_g2", {})
    fails = g1g1g2.get("failing_examples")
    if not fails:
        ff = g1g1g2.get("first_fail")
        fails = [ff] if ff is not None else []

    # If no failing triples were recorded, there is nothing to assemble — pass.
    if len(fails) == 0:
        return

    local_alphas = []
    from tools.exhaustive_homotopy_check_rationalized_l3 import (
        basis_elem_g1,
        basis_elem_g2,
    )

    for ft in fails:
        a_idx = tuple(ft["a"])
        b_idx = tuple(ft["b"])
        c_idx = tuple(ft["c"])
        x = basis_elem_g1(toe, a_idx)
        y = basis_elem_g1(toe, b_idx)
        z = basis_elem_g2(toe, c_idx)

        alpha = linfty.compute_local_ce2_alpha_for_triple(x, y, z)
        assert alpha is not None
        local_alphas.append(alpha)

    # assemble global CE2 by summing local alphas pointwise
    def alpha_global(a, b):
        acc = toe.E8Z3.zero()
        for alpha in local_alphas:
            acc = acc + alpha(a, b)
        return acc

    # promote to global l4 and verify every recorded failing triple is fixed
    linfty.attach_l4_from_ce2(alpha_global)

    for ft in fails:
        a_idx = tuple(ft["a"])
        b_idx = tuple(ft["b"])
        c_idx = tuple(ft["c"])
        x = basis_elem_g1(toe, a_idx)
        y = basis_elem_g1(toe, b_idx)
        z = basis_elem_g2(toe, c_idx)

        total = linfty.homotopy_jacobi(x, y, z)
        assert max_abs(total) < 1e-10

    # sample pure g1 triples don't regress
    rng = np.random.default_rng(20260212)
    for _ in range(40):
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
        hj = linfty.homotopy_jacobi(xa, ya, za)
        assert max_abs(hj) < 1e-8

    linfty.detach_l4()


def test_local_ce2_uv_rationalization_and_l4_callable():
    """Ensure compute_local_ce2_alpha_for_triple can return/rationalize U/V and
    that the promoted l4 callable reflects the CE2 data (nonzero where expected).
    """
    from tools.build_linfty_firewall_extension import (
        LInftyE8Extension,
        _load_bad9,
        _load_bracket_tool,
    )

    toe = _load_bracket_tool()
    basis_path = "artifacts/e6_27rep_basis_export/E6_basis_78.npy"
    e6_basis = np.load(basis_path).astype(np.complex128)
    proj = toe.E6Projector(e6_basis)
    all_triads = toe._load_signed_cubic_triads()
    bad9 = _load_bad9()

    linfty = LInftyE8Extension(toe, proj, all_triads, bad9, l3_scale=1.0 / 9.0)

    # failing triple
    a_idx = (0, 0)
    b_idx = (17, 1)
    c_idx = (3, 0)
    from tools.exhaustive_homotopy_check_rationalized_l3 import (
        basis_elem_g1,
        basis_elem_g2,
    )

    x = basis_elem_g1(toe, a_idx)
    y = basis_elem_g1(toe, b_idx)
    z = basis_elem_g2(toe, c_idx)

    # request raw U/V and rationalized forms
    result = linfty.compute_local_ce2_alpha_for_triple(
        x, y, z, return_uv=True, rationalize_uv=True, max_den=720
    )
    assert result is not None
    alpha, U_flat, V_flat, U_rats, V_rats = result

    # confirm a rational with small denominator appears (V contains 1/6 in norm)
    from fractions import Fraction

    # at least one rational entry should be non-None and have small denominator
    non_none_v = [r for r in V_rats if r is not None]
    assert len(non_none_v) > 0
    # ensure the solver found a nontrivial V and the rationalized entries have small denominators
    import numpy as _np

    assert _np.linalg.norm(V_flat) > 1e-15
    denom_sizes = [r.denominator for r in non_none_v]
    assert min(denom_sizes) <= 720
    assert max(abs(r.numerator) for r in non_none_v) < 10000

    # promote to l4 and confirm the l4 callable is nonzero on a sensible 4-tuple
    linfty.attach_l4_from_ce2(alpha)
    # pick a 4-tuple where alpha is nonzero on (x,z) or (y,z)
    l4_val = linfty._l4_fn(x, y, z, x)
    assert (
        max(
            0.0 if l4_val.e6.size == 0 else float(np.max(np.abs(l4_val.e6))),
            0.0 if l4_val.sl3.size == 0 else float(np.max(np.abs(l4_val.sl3))),
            0.0 if l4_val.g1.size == 0 else float(np.max(np.abs(l4_val.g1))),
            0.0 if l4_val.g2.size == 0 else float(np.max(np.abs(l4_val.g2))),
        )
        > 1e-12
    )

    linfty.detach_l4()
