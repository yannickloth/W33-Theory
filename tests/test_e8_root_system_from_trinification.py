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


def test_e8_root_system_from_trinification_verifies():
    repo_root = Path(__file__).resolve().parents[1]
    tool = _load_module(
        repo_root / "tools" / "verify_e8_root_system_from_trinification.py",
        "verify_e8_root_system_from_trinification",
    )
    tool.main()

    out_path = repo_root / "artifacts" / "verify_e8_root_system_from_trinification.json"
    data = json.loads(out_path.read_text(encoding="utf-8"))
    assert data["status"] == "ok"
    assert data["counts"]["e8_roots_total"] == 240
    assert data["form"]["rank"] == 8
    assert data["counts"]["negation_missing"] == 0
