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


def test_exact_l4_assembled_from_rationalized_ce2():
    """Run the assemble_exact_l4_from_local_ce2 tool and verify its artifact
    and numeric consequences (unit-test the exact/rational CE2 → l4 path).
    """
    import importlib.util
    import json
    from pathlib import Path

    ROOT = Path(__file__).resolve().parents[1]

    spec = importlib.util.spec_from_file_location(
        "assemble_ce2", ROOT / "tools" / "assemble_exact_l4_from_local_ce2.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    res = mod.main(max_den=720)
    assert res and "artifact" in res

    # expect certificates to be returned as well
    assert "certificates" in res and isinstance(res["certificates"], dict)

    art_path = Path(res["artifact"])
    assert art_path.exists()
    data = json.loads(art_path.read_text(encoding="utf-8"))

    # artifact should contain at least the failing triple key and rational arrays
    assert len(data) >= 1
    first_key = list(data.keys())[0]
    entry = data[first_key]
    assert "U_rats" in entry and "V_rats" in entry
    # denominators should be bounded by the supplied max_den
    from fractions import Fraction

    rats = [Fraction(s) for s in entry["V_rats"] if s != "0"]
    assert all(fr.denominator <= 720 for fr in rats)


def test_pslq_snf_ce2_uv_check_tool_runs_and_passes():
    """Run the PSLQ/SNF CE2 U/V verifier and assert it reports OK for all
    recorded local solutions."""
    import importlib.util
    from pathlib import Path

    ROOT = Path(__file__).resolve().parents[1]
    spec = importlib.util.spec_from_file_location(
        "pslq_ce2", ROOT / "tools" / "pslq_snf_ce2_uv_check.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    report = mod.main()
    assert report.get("ok", False) is True
    out_path = ROOT / "artifacts" / "pslq_snf_ce2_uv_check.json"
    assert out_path.exists()
    import json

    rep = json.loads(out_path.read_text(encoding="utf-8"))
    assert "entries" in rep and len(rep["entries"]) >= 1


def test_snf_certificate_ce2_uv_tool_runs_and_certifies():
    """Run SNF certificate builder and assert a valid integer-lift certificate
    exists for each recorded CE2 local solution."""
    import importlib.util
    from pathlib import Path

    ROOT = Path(__file__).resolve().parents[1]
    spec = importlib.util.spec_from_file_location(
        "snf_ce2", ROOT / "tools" / "snf_certificate_ce2_uv.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    report = mod.main()
    assert "entries" in report and len(report["entries"]) >= 1
    # every entry should have been verified
    for k, v in report["entries"].items():
        assert v.get("verified", False) is True
        assert v.get("D_found") is not None
        assert isinstance(v.get("snf_diag"), list)


def test_derive_symbolic_l4_and_exhaustive_l3_l4_passes():
    """Derive symbolic l4 constants, load them into the assembler, and run
    an exhaustive homotopy check for (l2 + l3 + l4)."""
    import importlib.util
    import json
    from pathlib import Path

    ROOT = Path(__file__).resolve().parents[1]

    # derive symbolic l4 from rational CE2 solutions
    spec = importlib.util.spec_from_file_location(
        "derive_l4", ROOT / "tools" / "derive_symbolic_l4.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    sym = mod.main()
    assert isinstance(sym, dict) and len(sym) >= 1

    # attach symbolic l4 in an LInfty instance and ensure it cancels failing triple
    from tools.build_linfty_firewall_extension import (
        LInftyE8Extension,
        _load_bad9,
        _load_bracket_tool,
    )

    toe = _load_bracket_tool()
    e6_basis = np.load("artifacts/e6_27rep_basis_export/E6_basis_78.npy").astype(
        np.complex128
    )
    proj = toe.E6Projector(e6_basis)
    all_triads = toe._load_signed_cubic_triads()
    bad9 = _load_bad9()

    linfty = LInftyE8Extension(toe, proj, all_triads, bad9, l3_scale=1.0 / 9.0)
    # attach symbolic constants
    linfty.attach_l4_from_symbolic_constants(
        ROOT / "artifacts" / "l4_symbolic_constants.json"
    )
    # the loader should also register a CE2 coboundary callback when the
    # assembled CE2 artifact is present
    assert (
        hasattr(linfty, "_l4_coboundary_on_triple")
        and linfty._l4_coboundary_on_triple is not None
    )

    # verify failing triple(s) vanish under homotopy_jacobi
    exh = json.loads(
        open(
            "artifacts/exhaustive_homotopy_rationalized_l3.json", "r", encoding="utf-8"
        ).read()
    )
    ft = exh["sectors"]["g1_g1_g2"]["first_fail"]
    from tools.exhaustive_homotopy_check_rationalized_l3 import (
        basis_elem_g1,
        basis_elem_g2,
    )

    x = basis_elem_g1(toe, tuple(ft["a"]))
    y = basis_elem_g1(toe, tuple(ft["b"]))
    z = basis_elem_g2(toe, tuple(ft["c"]))

    tot = linfty.homotopy_jacobi(x, y, z)
    assert (
        max(
            0.0 if tot.e6.size == 0 else float(np.max(np.abs(tot.e6))),
            0.0 if tot.sl3.size == 0 else float(np.max(np.abs(tot.sl3))),
            0.0 if tot.g1.size == 0 else float(np.max(np.abs(tot.g1))),
            0.0 if tot.g2.size == 0 else float(np.max(np.abs(tot.g2))),
        )
        < 1e-10
    )

    # run the exhaustive l3+l4 verifier tool
    spec2 = importlib.util.spec_from_file_location(
        "exh_l3_l4", ROOT / "tools" / "exhaustive_homotopy_check_l3_l4.py"
    )
    mod2 = importlib.util.module_from_spec(spec2)
    spec2.loader.exec_module(mod2)

    mod2.main()
    outp = ROOT / "artifacts" / "exhaustive_homotopy_l3_l4.json"
    assert outp.exists()
    rep = json.loads(outp.read_text(encoding="utf-8"))
    # expect all sectors to pass
    for s in ("g1_g1_g1", "g2_g2_g2", "g1_g1_g2", "g1_g2_g2"):
        assert rep["sectors"][s]["passed"] is True
