from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


def _load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def test_effective_coupling_rule_has_expected_structure():
    repo_root = Path(__file__).resolve().parents[1]
    tool = _load_module(
        repo_root / "tools" / "derive_effective_coupling_rule.py",
        "derive_effective_coupling_rule",
    )
    tool.main()

    out_path = repo_root / "artifacts" / "effective_coupling_rule.json"
    data = json.loads(out_path.read_text(encoding="utf-8"))
    assert data["status"] == "ok"
    assert data["counts"] == {
        "triads_total": 45,
        "firewall_bad": 9,
        "firewall_good": 36,
    }
    assert data["sector_hist_all"] == {"A0B0R3": 15, "A1B1R1": 30}
    assert data["sector_hist_bad"] == {"A0B0R3": 3, "A1B1R1": 6}

    Y = data["cubic_ABR_matrix"]["Y"]
    Yeff = data["cubic_ABR_matrix"]["Y_effective"]
    assert len(Y) == 6 and all(len(r) == 6 for r in Y)
    assert len(Yeff) == 6 and all(len(r) == 6 for r in Yeff)

    # Full cubic ABR matrix is skew-symmetric with ±1 off-diagonal.
    for i in range(6):
        assert Y[i][i] == 0
        for j in range(6):
            if i == j:
                continue
            assert Y[i][j] in (-1, 1)
    for i in range(6):
        for j in range(i + 1, 6):
            assert Y[i][j] == -Y[j][i]

    # Firewall deletes exactly 6 oriented ABR couplings (so 24 survive).
    nonzero_eff = 0
    for i in range(6):
        assert Yeff[i][i] == 0
        for j in range(6):
            if i == j:
                continue
            assert Yeff[i][j] in (-1, 0, 1)
            if Yeff[i][j] != 0:
                nonzero_eff += 1
    assert nonzero_eff == 24

    rrr = data["cubic_RRR_matchings"]
    assert len(rrr) == 15
    assert sum(1 for m in rrr if m["is_firewall_bad"]) == 3

    sols = data["trinification_recognition"]["solutions"]
    assert isinstance(sols, list)
    assert len(sols) >= 1
