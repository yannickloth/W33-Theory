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


def test_e6_cubic_invariance_canonical_gauge():
    repo_root = Path(__file__).resolve().parents[1]
    tool = _load_module(
        repo_root / "tools" / "verify_e6_cubic_invariance_canonical_gauge.py",
        "verify_e6_cubic_invariance_canonical_gauge",
    )
    tool.main()
    out_path = repo_root / "artifacts" / "e6_cubic_invariance_canonical_gauge.json"
    data = json.loads(out_path.read_text(encoding="utf-8"))
    assert data["status"] == "ok"
    assert data["counts"]["failures_total"] == 0
