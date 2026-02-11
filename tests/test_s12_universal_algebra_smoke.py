from __future__ import annotations

import tools.s12_universal_algebra as s12


def test_s12_universal_report_smoke():
    report = s12.build_s12_universal_report(jordan_sample_limit=200)

    assert report.get("status") == "ok"
    assert report.get("code_size") == 729

    dims = report["algebra_dimensions"]
    assert dims["total_nonzero"] == 728
    assert dims["grade0"] == 242
    assert dims["grade1"] == 243
    assert dims["grade2"] == 243
    assert dims["quotient_by_grade0"] == 486

    laws = report["universal_grade_laws"]
    assert laws["jacobi_coefficient_identity_holds"] is False
    assert laws["jacobi_failure_count"] == 6
    assert laws["ad3_coefficient_identity_holds"] is True
    assert laws["jordan_triple_xz_symmetry_holds"] is True

    checks = report["exhaustive_checks"]
    assert checks["g1_g1_symmetric"]["holds"] is True
    assert checks["g2_g2_symmetric"]["holds"] is True
    assert checks["g1_g2_antisymmetric"]["holds"] is True
    assert checks["g0_central"]["holds"] is True
    assert checks["ad3_zero_on_g1"]["holds"] is True
    assert checks["ad2_nontrivial_on_g1"]["nonzero_count"] > 0
    assert checks["jordan_triple_xz_symmetry_sample"]["holds"] is True
