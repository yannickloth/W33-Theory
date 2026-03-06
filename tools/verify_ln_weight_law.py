#!/usr/bin/env python3
"""
Verify the "weight law" for computed l_n JSONL tables.

Let the E8 basis be indexed as in `artifacts/e8_structure_constants_w33_discrete.json`:
  - 0..7   : Cartan generators H_0..H_7
  - 8..247 : root vectors e_α, ordered by `basis.roots` ("root_orbit" coords)

For any table entry with input indices `in = [i1, ..., in]` (all roots, no Cartan),
define the total root

    S = root(i1) + ... + root(in)

in the simple-root coefficient basis used by `basis.roots`.

Claim (observed in V22/V23 exact tables and explained by root-space weight):
  - If S == 0, the output lies in the weight-0 subspace, i.e. Cartan only (indices 0..7),
    so multi-term outputs can occur only in Cartan directions.
  - If S is a root, the output (if nonzero) lies in the 1D root space g_S, so it must be
    proportional to the unique basis element e_S, hence single-term with `out = idx(S)`.

This script checks those implications *entry-by-entry* for an l_n JSONL file.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BRACKET_JSON = ROOT / "artifacts" / "e8_structure_constants_w33_discrete.json"
DEFAULT_JSONL = ROOT / "V23_output" / "l8_patch_octuples_full.jsonl"

Root = Tuple[int, ...]


def _parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Verify l_n weight-law consistency.")
    ap.add_argument("--jsonl", type=Path, default=DEFAULT_JSONL, help="l_n JSONL file")
    ap.add_argument(
        "--bracket-json",
        type=Path,
        default=DEFAULT_BRACKET_JSON,
        help="E8 structure-constants JSON (for root ordering/coords)",
    )
    ap.add_argument(
        "--max-lines",
        type=int,
        default=0,
        help="Stop after N non-empty lines (0 = all).",
    )
    ap.add_argument(
        "--progress-every",
        type=int,
        default=5_000_000,
        help="Print progress every N entries (0 disables).",
    )
    ap.add_argument(
        "--fail-fast",
        action="store_true",
        help="Exit on the first mismatch instead of counting all mismatches.",
    )
    return ap.parse_args()


def _load_roots(bracket_json: Path) -> List[Root]:
    data = json.loads(bracket_json.read_text(encoding="utf-8"))
    basis = data.get("basis")
    if not isinstance(basis, dict):
        raise RuntimeError("Missing or invalid `basis` in bracket JSON")

    cartan_dim = int(basis.get("cartan_dim", -1))
    root_dim = int(basis.get("root_dim", -1))
    n = int(basis.get("n", -1))
    roots_raw = basis.get("roots")

    if cartan_dim != 8 or root_dim != 240 or n != 248:
        raise RuntimeError(
            f"Unexpected basis sizing: cartan_dim={cartan_dim} root_dim={root_dim} n={n}"
        )
    if not isinstance(roots_raw, list) or len(roots_raw) != 240:
        raise RuntimeError("Invalid `basis.roots` in bracket JSON")

    roots: List[Root] = []
    for r in roots_raw:
        if not isinstance(r, list) or len(r) != 8:
            raise RuntimeError("Expected 8D root vectors in `basis.roots`")
        roots.append(tuple(int(x) for x in r))
    return roots


def _sum_roots(indices: Iterable[int], idx_to_root: Dict[int, Root]) -> Root:
    s0 = s1 = s2 = s3 = s4 = s5 = s6 = s7 = 0
    for idx in indices:
        r = idx_to_root.get(int(idx))
        if r is None:
            raise RuntimeError(f"Input index {idx} is not a root-basis index (>=8)")
        s0 += r[0]
        s1 += r[1]
        s2 += r[2]
        s3 += r[3]
        s4 += r[4]
        s5 += r[5]
        s6 += r[6]
        s7 += r[7]
    return (s0, s1, s2, s3, s4, s5, s6, s7)


def main() -> None:
    args = _parse_args()

    roots = _load_roots(args.bracket_json)
    idx_to_root: Dict[int, Root] = {8 + i: r for i, r in enumerate(roots)}
    root_to_idx: Dict[Root, int] = {r: 8 + i for i, r in enumerate(roots)}
    zero: Root = (0, 0, 0, 0, 0, 0, 0, 0)

    total = 0
    n_single = 0
    n_multi = 0
    n_single_root = 0
    n_single_cartan = 0
    n_multi_cartan = 0
    mismatches = 0
    first_mismatch: dict | None = None

    t0 = time.time()
    with args.jsonl.open("r", encoding="utf-8") as f:
        for line_no, line in enumerate(f, 1):
            if args.max_lines and total >= args.max_lines:
                break
            line = line.strip()
            if not line:
                continue

            total += 1
            entry = json.loads(line)
            ins = entry.get("in")
            if not isinstance(ins, list) or not ins:
                raise RuntimeError(f"Line {line_no}: missing/invalid `in` field")

            s = _sum_roots(ins, idx_to_root)
            is_zero = s == zero

            # Single-term: {"out": idx, "coeff": c}
            if "coeff" in entry:
                n_single += 1
                out = int(entry.get("out"))

                if is_zero:
                    # Weight-0 outputs must lie in Cartan.
                    if out >= 8:
                        mismatches += 1
                        if first_mismatch is None:
                            first_mismatch = {
                                "line": line_no,
                                "kind": "single_noncartan_at_zero_weight",
                                "sum_root": list(s),
                                "entry": entry,
                            }
                        if args.fail_fast:
                            break
                    else:
                        n_single_cartan += 1
                else:
                    expected = root_to_idx.get(s)
                    if expected is None or out != expected:
                        mismatches += 1
                        if first_mismatch is None:
                            first_mismatch = {
                                "line": line_no,
                                "kind": "single_root_mismatch",
                                "sum_root": list(s),
                                "expected_out": expected,
                                "entry": entry,
                            }
                        if args.fail_fast:
                            break
                    else:
                        n_single_root += 1

            # Multi-term: {"terms": [[idx, coeff], ...]}
            else:
                n_multi += 1
                terms = entry.get("terms")
                if not isinstance(terms, list) or not terms:
                    raise RuntimeError(f"Line {line_no}: missing/invalid `terms` field")

                ok = True
                if not is_zero:
                    ok = False
                    reason = "multi_nonzero_weight"
                else:
                    for t in terms:
                        if (
                            not isinstance(t, list)
                            or len(t) != 2
                            or int(t[0]) >= 8
                            or int(t[0]) < 0
                        ):
                            ok = False
                            reason = "multi_has_noncartan_term"
                            break

                if not ok:
                    mismatches += 1
                    if first_mismatch is None:
                        first_mismatch = {
                            "line": line_no,
                            "kind": reason,
                            "sum_root": list(s),
                            "entry": entry,
                        }
                    if args.fail_fast:
                        break
                else:
                    n_multi_cartan += 1

            if args.progress_every and (total % args.progress_every == 0):
                dt = time.time() - t0
                rate = total / max(dt, 1e-9)
                print(
                    f"checked={total:,} mismatches={mismatches:,} "
                    f"(single={n_single:,} multi={n_multi:,}) "
                    f"elapsed={dt:.1f}s rate={rate:,.0f}/s",
                    flush=True,
                )

    dt = time.time() - t0

    print("\n" + "=" * 70)
    print("l_n WEIGHT LAW CHECK")
    print("=" * 70)
    print(f"jsonl: {args.jsonl}")
    print(f"bracket_json: {args.bracket_json}")
    print(f"checked_entries: {total:,}")
    print(f"single_term: {n_single:,} (root={n_single_root:,} cartan={n_single_cartan:,})")
    print(f"multi_term: {n_multi:,} (cartan={n_multi_cartan:,})")
    print(f"mismatches: {mismatches:,}")
    print(f"elapsed_seconds: {dt:.1f}")

    if first_mismatch is not None:
        print("\nFirst mismatch:")
        print(json.dumps(first_mismatch, indent=2, sort_keys=True))

    if mismatches:
        sys.exit(1)


if __name__ == "__main__":
    main()

