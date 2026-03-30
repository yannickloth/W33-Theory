#!/usr/bin/env python3
"""Scan exploration/w33_k3_* modules and collect any non-split flags.

Writes `data/find_non_split_k3_candidates.json` with per-module diagnostics.
"""
from __future__ import annotations

import importlib
import inspect
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

EXPL = ROOT / "exploration"
if str(EXPL) not in sys.path:
    # allow bare imports inside exploration modules (they often import sibling modules by name)
    sys.path.insert(0, str(EXPL))
OUT = ROOT / "data" / "find_non_split_k3_candidates.json"


def call_build_summary(module) -> Any:
    # find a callable that looks like a summary builder
    for name, obj in inspect.getmembers(module, inspect.isfunction):
        ln = name.lower()
        if ln.startswith("build_") and ("summary" in ln or "bridge" in ln or "report" in ln):
            try:
                return obj()
            except TypeError:
                try:
                    return obj
                except Exception as exc:
                    return {"error": f"call failed: {exc}"}
    # fallback: try callables in module that return dicts
    for name, obj in inspect.getmembers(module, inspect.isfunction):
        try:
            res = obj()
            if isinstance(res, dict):
                return res
        except Exception:
            continue
    return None


def extract_flags(d: Any) -> dict:
    flags = {}

    def walk(x, prefix=""):
        if isinstance(x, dict):
            for k, v in x.items():
                key = f"{prefix}.{k}" if prefix else k
                lk = k.lower()
                if "nonsplit" in lk or ("is_" in lk and ("nonsplit" in lk or "is_nonsplit" in lk)) or "is_split" in lk or "split" == lk or "is_split_two_line_package" in lk:
                    flags[key] = v
                walk(v, key)
        elif isinstance(x, list):
            for i, v in enumerate(x):
                walk(v, f"{prefix}[{i}]")

    walk(d)
    return flags


def main():
    out = {}
    for f in sorted(EXPL.glob("w33_k3_*.py")):
        modname = f.stem
        module_path = f"exploration.{modname}"
        rec = {"module": module_path, "status": "missing", "flags": {}, "error": None}
        try:
            mod = importlib.import_module(module_path)
            rec["status"] = "imported"
        except Exception as exc:
            rec["status"] = "import-error"
            rec["error"] = str(exc)
            out[module_path] = rec
            continue

        try:
            summary = call_build_summary(mod)
            rec["status"] = "ok"
            rec["summary_present"] = summary is not None
            if isinstance(summary, dict):
                rec["flags"] = extract_flags(summary)
            else:
                rec["flags"] = {}
        except Exception as exc:
            rec["status"] = "call-error"
            rec["error"] = str(exc)

        out[module_path] = rec

    # write output safely
    try:
        from utils.json_safe import dump_json

        dump_json(out, OUT, indent=2)
    except Exception:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(out, indent=2), encoding="utf-8")

    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
