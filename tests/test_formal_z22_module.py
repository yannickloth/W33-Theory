from __future__ import annotations

from tools import formal_z22_proof as fzp


def test_formal_z22_module_report() -> None:
    report = fzp.symbolic_exclude_z22_check()
    assert report["holds"] is True
    assert report["P"] == 1
    assert report["s(L,1)"] == -1
    assert "contradiction" in report["reason"]
    # z_map fixes z=1
    assert fzp.z_map(1) == 1
    assert report["z_map_fix_1"] is True
    # explicit z-map table and involution profile
    assert fzp.z_map_table() == {0: 2, 1: 1, 2: 0}
    assert report["z_map_table"] == {0: 2, 1: 1, 2: 0}
    assert report["z_map_is_involution"] is True
    assert report["no_fixed_point_stabilizer"] is True

    profile = report["vertical_line_sign_profile"]
    assert profile["no_fixed_point_stabilizer"] is True
    assert profile["fixed_point_candidates"] == [
        {
            "z": 1,
            "z_is_fixed_by_z_map": True,
            "P(L)": 1,
            "s(L,z)": -1,
            "P_equals_s": False,
        }
    ]
    assert profile["fixed_point_stabilizers"] == []
    table = {int(row["z"]): int(row["s(L,z)"]) for row in profile["rows"]}
    assert table == {0: -1, 1: -1, 2: 1}
