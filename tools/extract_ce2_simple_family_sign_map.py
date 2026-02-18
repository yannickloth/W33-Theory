#!/usr/bin/env python3
"""Extract the CE2 simple-family sign map into a tiny commit-friendly artifact.

Background
----------
The global CE2 predictor for the (|val|=1/54) "simple family" needs a deterministic
sign s(c, match, other) in {+1,-1}. The current implementation can derive this
map by scanning the full sparse CE2 artifact (5832 entries), but that is heavier
than necessary at runtime.

This tool extracts just the 864-key sign map and writes it to:
  committed_artifacts/ce2_simple_family_sign_map.json

The resulting file is small (kB-scale) and can be loaded directly by
`scripts/ce2_global_cocycle.py`.

Usage
-----
  & .venv\\Scripts\\python.exe -X utf8 tools\\extract_ce2_simple_family_sign_map.py \\
      --in committed_artifacts\\ce2_sparse_local_solutions.json \\
      --out committed_artifacts\\ce2_simple_family_sign_map.json
"""

from __future__ import annotations

import argparse
import json
from fractions import Fraction
from pathlib import Path


def _collect_sign_map(entries: list[object]) -> dict[tuple[int, int, int], int]:
    sign_map: dict[tuple[int, int, int], int] = {}
    for rec in entries:
        if not isinstance(rec, dict):
            continue
        if not all(k in rec for k in ("a", "b", "c", "U", "V")):
            continue
        a = rec["a"]
        b = rec["b"]
        c = rec["c"]
        if not (isinstance(a, list) and isinstance(b, list) and isinstance(c, list)):
            continue
        if not (len(a) == len(b) == len(c) == 2):
            continue
        a_i, a_j = int(a[0]), int(a[1])
        b_i, b_j = int(b[0]), int(b[1])
        c_i, c_j = int(c[0]), int(c[1])

        U = rec["U"]
        V = rec["V"]
        if not (isinstance(U, list) and isinstance(V, list)):
            continue
        if len(U) + len(V) != 1:
            continue
        idx_val = U[0] if len(U) == 1 else V[0]
        if not (isinstance(idx_val, list) and len(idx_val) == 2):
            continue
        _idx, val = int(idx_val[0]), str(idx_val[1])
        try:
            frac = Fraction(val)
        except Exception:
            continue
        if abs(frac) != Fraction(1, 54):
            continue

        # Match/other selection uses the sl3 index equality with c_j, and is
        # the same rule used in the predictor.
        if a_j == c_j and b_j != c_j:
            match_i, other_i = a_i, b_i
        elif b_j == c_j and a_j != c_j:
            match_i, other_i = b_i, a_i
        else:
            continue

        s = 1 if frac > 0 else -1
        sign_map[(c_i, match_i, other_i)] = int(s)
    return sign_map


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--in", dest="in_path", type=Path, required=True)
    parser.add_argument("--out", dest="out_path", type=Path, required=True)
    args = parser.parse_args()

    raw = json.loads(args.in_path.read_text(encoding="utf-8"))
    entries = raw.get("entries", [])
    if not isinstance(entries, list):
        raise SystemExit("Unexpected CE2 sparse JSON format: missing entries list.")

    sign_map = _collect_sign_map(entries)
    if len(sign_map) != 864:
        raise SystemExit(f"Expected 864 sign keys, got {len(sign_map)}")

    out_entries = [
        {"c": c, "match": m, "other": o, "sign": int(s)}
        for (c, m, o), s in sorted(sign_map.items())
    ]
    payload = {
        "status": "ok",
        "source": str(args.in_path),
        "n_keys": len(out_entries),
        "entries": out_entries,
    }
    args.out_path.parent.mkdir(parents=True, exist_ok=True)
    args.out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"Wrote {args.out_path} (n_keys={len(out_entries)})")


if __name__ == "__main__":
    main()
