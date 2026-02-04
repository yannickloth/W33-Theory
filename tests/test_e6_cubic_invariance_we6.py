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


def test_we6_simple_generators_preserve_signed_cubic_projectively(tmp_path):
    repo_root = Path(__file__).resolve().parents[1]
    tool = _load_module(
        repo_root / "tools" / "verify_e6_cubic_invariance_under_we6.py",
        "verify_e6_cubic_invariance_under_we6",
    )

    # Run main() and ensure it writes a well-formed artifact.
    tool.main()
    out_path = repo_root / "artifacts" / "e6_cubic_invariance_we6.json"
    data = json.loads(out_path.read_text(encoding="utf-8"))
    assert data["status"] == "ok"
    assert data["counts"]["generators"] == 6
    assert "strict_solved" in data["counts"]
    assert "projective_solved" in data["counts"]
