import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
EXH = ROOT / "artifacts" / "exhaustive_homotopy_rationalized_l3.json"


def test_detect_degenerate_sflats_in_failing_sectors():
    """Fail the test if any failing sector has degenerate S_flats (should be flagged).

    This prevents accepting SA/LSQ candidates that leave "nothing to solve" on a
    failing mixed triple support.
    """
    if not EXH.exists():
        pytest.skip("Missing artifacts/exhaustive_homotopy_rationalized_l3.json (integration-only)")
    data = json.loads(EXH.read_text(encoding="utf-8"))
    sectors = data.get("sectors", {})
    for sname, info in sectors.items():
        if not info.get("passed", True):
            first = info.get("first_fail")
            assert (
                first is not None
            ), f"Sector {sname} failed but no first_fail recorded"
            # use existing verify tool to inspect S_flats degeneracy
            from tools.compute_restricted_ce_h3 import analyze_triple

            toe_mod = __import__("tools.toe_e8_z3graded_bracket_jacobi", fromlist=["*"])
            res = analyze_triple(
                toe_mod, tuple(first["a"]), tuple(first["b"]), tuple(first["c"])
            )
            assert not res.get("degenerate", False), (
                f"Sector {sname} has degenerate S_flats for first failing triple;"
                " consider blocking this candidate or changing search penalties"
            )