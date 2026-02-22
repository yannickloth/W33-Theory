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


def test_export_we6_signed_action_on_27():
    repo_root = Path(__file__).resolve().parents[1]
    tool = _load_module(
        repo_root / "tools" / "export_we6_signed_action_on_27.py",
        "export_we6_signed_action_on_27",
    )
    tool.main()
    out_path = repo_root / "artifacts" / "we6_signed_action_on_27.json"
    data = json.loads(out_path.read_text(encoding="utf-8"))
    assert data["status"] == "ok"
    assert data["counts"]["generators"] == 6
    # Known: unsigned permutation action on the 27 lines has order 51840 (W(E6)).
    assert data["counts"]["perm_group_order"] == 51840
