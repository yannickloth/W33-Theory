import json
import subprocess
from pathlib import Path


def test_ce2_bicomplex_v09_nils_and_jordan_structure():
    script = Path("toe_session_20260316_v09") / "toe_session_20260316_v09" / "w33_ce2_bicomplex_v09.py"
    assert script.exists(), f"Expected v09 script at {script}"

    proc = subprocess.run(["py", "-3", str(script)], capture_output=True, text=True, check=True)
    data = json.loads(proc.stdout)

    gen = data["generation_operator"]
    assert gen["rank_g_minus_I"] == 54
    assert gen["rank_g_minus_I_squared"] == 27
    assert gen["nilpotent_index_g_minus_I"] == 3

    bicomp = data["combined_bicomplex"]
    assert bicomp["commuting_nilpotents_verified"]["U3_zero"]
    assert bicomp["commuting_nilpotents_verified"]["T2_zero"]
    assert bicomp["commuting_nilpotents_verified"]["UT_equal_TU"]

    # Verify the packet structure is 2x3x27
    assert bicomp["packet_shape"] == "2 x 3 x 27"

    anchor = data["six_mode_anchor_algebra"]
    assert anchor["monomial_ranks"]["U"] == 108
    assert anchor["monomial_ranks"]["U2"] == 54
    assert anchor["monomial_ranks"]["TU2"] == 27
    assert "U^3 = 0" in anchor["relations"]
    assert "T^2 = 0" in anchor["relations"]
    assert "UT = TU" in anchor["relations"]
