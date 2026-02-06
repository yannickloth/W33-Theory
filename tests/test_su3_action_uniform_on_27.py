from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest


def _load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def test_su3_action_is_uniform_after_color_gauge():
    repo_root = Path(__file__).resolve().parents[1]
    # Skip if required artifact is missing
    if not (repo_root / "artifacts" / "su3_color_gauge_from_singletons.json").exists():
        pytest.skip(
            "Missing su3_color_gauge_from_singletons.json; skipping SU3 action uniformity test in this environment"
        )
    tool = _load_module(
        repo_root / "tools" / "verify_su3_action_uniform_on_27.py",
        "verify_su3_action_uniform_on_27",
    )
    tool.main()
    out_path = repo_root / "artifacts" / "su3_action_uniform_on_27.json"
    data = json.loads(out_path.read_text(encoding="utf-8"))
    assert data["status"] == "ok"
    assert data["counts"]["nonuniform_reports"] == 0
