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


def test_e6_chevalley_commutator_table_serre_and_cartan():
    repo_root = Path(__file__).resolve().parents[1]
    tool = _load_module(
        repo_root / "tools" / "build_e6_chevalley_commutator_table.py",
        "build_e6_chevalley_commutator_table",
    )
    tool.main()

    out_path = repo_root / "artifacts" / "e6_chevalley_commutator_table.json"
    data = json.loads(out_path.read_text(encoding="utf-8"))
    assert data["status"] == "ok"
    assert data["dims"] == {"cartan": 6, "roots": 72, "total": 78}
    assert data["serre"]["ok"] is True
    assert data["serre"]["n_failures"] == 0
    assert data["cartan_matrix"] == [
        [2, -1, 0, 0, 0, 0],
        [-1, 2, -1, 0, 0, 0],
        [0, -1, 2, -1, -1, 0],
        [0, 0, -1, 2, 0, 0],
        [0, 0, -1, 0, 2, -1],
        [0, 0, 0, 0, -1, 2],
    ]
