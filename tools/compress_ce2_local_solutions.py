#!/usr/bin/env python3
"""Compress CE2 local solutions into a sparse, commit-friendly JSON artifact.

The raw local-solution file `artifacts/ce2_rational_local_solutions.json` stores
U_rats/V_rats as length-900 arrays of Fraction strings with overwhelming zeros.
This script rewrites it into a sparse form that keeps only nonzero entries:

  - key: "a0,a1:b0,b1:c0,c1" (basis indices)
  - a,b,c: the original (i,j) indices
  - U/V: lists of [flat_index, "p/q"] pairs

This is intended to support analysis and portable demos without requiring a
100+MB ignored artifact to be present.

Usage:
  & .venv\\Scripts\\python.exe -X utf8 tools\\compress_ce2_local_solutions.py \\
      --in artifacts\\ce2_rational_local_solutions.json \\
      --out committed_artifacts\\ce2_sparse_local_solutions.json
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator


@dataclass
class CE2SparseEntry:
    key: str
    a: tuple[int, int]
    b: tuple[int, int]
    c: tuple[int, int]
    U: list[tuple[int, str]]
    V: list[tuple[int, str]]


ENTRY_RE = re.compile(r'^\s*"(?P<key>\d+,\d+:\d+,\d+:\d+,\d+)"\s*:\s*\{\s*$')


def iter_ce2_sparse_entries(path: Path) -> Iterator[CE2SparseEntry]:
    if not path.exists():
        raise FileNotFoundError(path)

    in_entry = False
    depth = 0
    key: str | None = None
    a: list[int] | None = None
    b: list[int] | None = None
    c: list[int] | None = None
    in_U = False
    in_V = False
    idx = 0
    U: list[tuple[int, str]] = []
    V: list[tuple[int, str]] = []

    with path.open("r", encoding="utf-8") as f:
        for line in f:
            if not in_entry:
                m = ENTRY_RE.match(line)
                if not m:
                    continue
                key = m.group("key")
                in_entry = True
                depth = line.count("{") - line.count("}")
                a = b = c = None
                in_U = in_V = False
                idx = 0
                U = []
                V = []
                continue

            depth += line.count("{") - line.count("}")
            s = line.strip()

            if s.startswith('"a"'):
                a = []
                continue
            if s.startswith('"b"'):
                b = []
                continue
            if s.startswith('"c"'):
                c = []
                continue

            if a is not None and len(a) < 2 and s.rstrip(",").isdigit():
                a.append(int(s.rstrip(",")))
                continue
            if b is not None and len(b) < 2 and s.rstrip(",").isdigit():
                b.append(int(s.rstrip(",")))
                continue
            if c is not None and len(c) < 2 and s.rstrip(",").isdigit():
                c.append(int(s.rstrip(",")))
                continue

            if s.startswith('"U_rats"'):
                in_U = True
                idx = 0
                continue
            if s.startswith('"V_rats"'):
                in_V = True
                idx = 0
                continue

            if in_U:
                if s.startswith("]"):
                    in_U = False
                    continue
                m = re.match(r'"([^"]+)"', s)
                if m:
                    val = m.group(1)
                    if val != "0":
                        U.append((idx, val))
                    idx += 1
                continue

            if in_V:
                if s.startswith("]"):
                    in_V = False
                    continue
                m = re.match(r'"([^"]+)"', s)
                if m:
                    val = m.group(1)
                    if val != "0":
                        V.append((idx, val))
                    idx += 1
                continue

            if in_entry and depth <= 0:
                in_entry = False
                if key is None or a is None or b is None or c is None:
                    raise ValueError(f"Malformed CE2 entry near key={key!r}")
                if len(a) != 2 or len(b) != 2 or len(c) != 2:
                    raise ValueError(f"Malformed indices for key={key!r}")
                yield CE2SparseEntry(
                    key=str(key),
                    a=(int(a[0]), int(a[1])),
                    b=(int(b[0]), int(b[1])),
                    c=(int(c[0]), int(c[1])),
                    U=list(U),
                    V=list(V),
                )
                key = None
                a = b = c = None
                U = []
                V = []


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--in", dest="in_path", type=Path, required=True)
    parser.add_argument("--out", dest="out_path", type=Path, required=True)
    args = parser.parse_args()

    entries_out: list[dict[str, object]] = []
    n = 0
    for e in iter_ce2_sparse_entries(args.in_path):
        entries_out.append(
            {
                "k": e.key,
                "a": [e.a[0], e.a[1]],
                "b": [e.b[0], e.b[1]],
                "c": [e.c[0], e.c[1]],
                "U": [[int(i), str(v)] for i, v in e.U],
                "V": [[int(i), str(v)] for i, v in e.V],
            }
        )
        n += 1

    payload = {
        "status": "ok",
        "source": str(args.in_path).replace("\\", "/"),
        "n_entries": int(n),
        "entries": entries_out,
    }

    args.out_path.parent.mkdir(parents=True, exist_ok=True)
    args.out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"Wrote {args.out_path} ({n} entries)")


if __name__ == "__main__":
    main()
