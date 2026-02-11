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
