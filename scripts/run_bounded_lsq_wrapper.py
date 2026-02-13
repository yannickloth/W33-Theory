#!/usr/bin/env python3
"""Wrapper to run constrained_lsq_mixed_patch.py by loading via file path.
This avoids package import issues when running from the workspace.
"""
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
mod_path = ROOT / "tools" / "constrained_lsq_mixed_patch.py"

spec = importlib.util.spec_from_file_location("constrained_lsq_mixed_patch", mod_path)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

if __name__ == "__main__":
    mod.main()
