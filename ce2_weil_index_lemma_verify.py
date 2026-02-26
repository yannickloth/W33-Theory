#!/usr/bin/env python3
"""Verify the CE2 Weil-index lemma against the committed CE2 sign data.

This script is intentionally *deterministic* and uses only committed inputs.

What it checks
--------------
For every (c, match, other) triple in the committed 864-entry simple-family
sign map, it verifies that:

  predict_simple_family_sign_closed_form(c, match, other)

matches the committed sign.

Notes
-----
The predictor requires the E6 cubic affine Heisenberg model mapping:

  artifacts/e6_cubic_affine_heisenberg_model.json

If it is missing, generate it via the standard pipeline:

  python -X utf8 tools/solve_canonical_su3_gauge_and_cubic.py
  python -X utf8 tools/verify_e6_cubic_affine_heisenberg_model.py

Then re-run this verifier.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))

from scripts.ce2_global_cocycle import predict_simple_family_sign_closed_form  # noqa: E402


def load_committed_sign_map() -> dict[tuple[int, int, int], int]:
    compact_path = ROOT / "committed_artifacts" / "ce2_simple_family_sign_map.json"
    sparse_path = ROOT / "committed_artifacts" / "ce2_sparse_local_solutions.json"

    if compact_path.exists():
        data = json.loads(compact_path.read_text(encoding="utf-8"))
        entries = data.get("entries", [])
        out: dict[tuple[int, int, int], int] = {}
        for rec in entries:
            c = int(rec["c"])
            m = int(rec["match"])
            o = int(rec["other"])
            s = int(rec["sign"])
            out[(c, m, o)] = s
        if len(out) != 864:
            raise ValueError(f"unexpected compact sign-map size: {len(out)}")
        return out

    if not sparse_path.exists():
        raise FileNotFoundError("missing committed CE2 sign inputs")

    # Fallback: reconstruct the 864-map from the sparse local solutions.
    data = json.loads(sparse_path.read_text(encoding="utf-8"))
    entries = data.get("entries", [])
    out: dict[tuple[int, int, int], int] = {}
    for rec in entries:
        k = rec.get("k")
        if not isinstance(k, str):
            continue
        parts = k.split(":")
        if len(parts) != 3:
            continue
        def parse_pair(s: str) -> tuple[int, int]:
            a, b = s.split(",")
            return int(a), int(b)
        a, b, c = map(parse_pair, parts)
        U = rec.get("U", [])
        V = rec.get("V", [])
        if not isinstance(U, list) or not isinstance(V, list):
            continue
        nz = list(U) + list(V)
        if len(nz) != 1:
            continue
        idx, val_raw = nz[0]
        idx = int(idx)
        if not (0 <= idx < 27 * 27):
            continue
        # sign is determined by coefficient sign (denom=54 in simple family)
        val = str(val_raw)
        if "/54" not in val and "/-54" not in val:
            continue
        sgn = 1 if not val.startswith("-") else -1

        a_i, a_j = a
        b_i, b_j = b
        c_i, c_j = c
        if a_j == c_j and b_j != c_j:
            match_i, other_i = a_i, b_i
        elif b_j == c_j and a_j != c_j:
            match_i, other_i = b_i, a_i
        else:
            continue
        out[(int(c_i), int(match_i), int(other_i))] = sgn

    if len(out) != 864:
        raise ValueError(f"unexpected reconstructed sign-map size: {len(out)}")
    return out


def main() -> int:
    model_path = ROOT / "artifacts" / "e6_cubic_affine_heisenberg_model.json"
    if not model_path.exists():
        print("ERROR: missing artifacts/e6_cubic_affine_heisenberg_model.json")
        print("Generate it with:")
        print("  python -X utf8 tools/solve_canonical_su3_gauge_and_cubic.py")
        print("  python -X utf8 tools/verify_e6_cubic_affine_heisenberg_model.py")
        return 2

    sign_map = load_committed_sign_map()
    bad = []
    for (c, m, o), expected in sign_map.items():
        got = int(predict_simple_family_sign_closed_form(c, m, o))
        if got not in (-1, 1):
            bad.append((c, m, o, expected, got))
        elif got != int(expected):
            bad.append((c, m, o, expected, got))

    if bad:
        print(f"FAIL: {len(bad)} / {len(sign_map)} mismatches")
        print("First 20 mismatches:")
        for rec in bad[:20]:
            c, m, o, e, g = rec
            print(f"  (c,match,other)=({c},{m},{o}) expected={e} got={g}")
        return 1

    print(f"PASS: all {len(sign_map)} simple-family signs match the closed form")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
