#!/usr/bin/env python3
"""Interactive helper to inspect monomial phase lifts for arbitrary permutation sets.

Usage: provide a JSON file mapping names to lists of permutation cycles or
explicit permutation lists; the script will attempt to find sign lifts and
compute the order of the resulting monomial group.

Example input format (JSON):

{
    "example": [[1,4],[3,10],...],        # cycles or complete permutation
    "another": [ [0,1,2], [3,4,5] ]       # etc.
}

Each element in the list may be either:
  - an explicit permutation list of length *n* (0-based or 1-based), or
  - a single cycle written as a list of integers (0-based or 1-based).

This tool is intended to make it easy to test new ladder rungs by supplying
candidate permutation generators without editing other scripts.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

# ensure top-level workspace root is on sys.path so we can import other scripts
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import numpy as np

from scripts.monomial_utils import (
    find_sign_lifts_for_group,
    monomial_group_order,
)
from scripts.derive_m12_p144_suborbits import perm_from_cycles


Perm = Tuple[int, ...]


def parse_value(val: Any) -> List[Perm]:
    """Interpret value from JSON as a list of permutations.

    Each element of ``val`` may be either a full permutation (tuple of length
    *n* containing all values 0..n-1 or 1..n) or a single cycle written as a
    sequence of integers.  The latter form is converted to a full permutation of
    size *n* by inferring the degree from the maximum index. Indices may be
    0-based or 1-based; cycle conversion uses :func:`perm_from_cycles`, which
    expects 1-based indices.
    """
    if not isinstance(val, list):
        raise ValueError("expected list of permutations")

    # Determine degree and indexing convention. If 0 appears anywhere, treat
    # data as 0-based (0..n-1); otherwise treat it as 1-based (1..n).
    max_idx = -1
    has_zero = False
    for item in val:
        if isinstance(item, list):
            for x in item:
                if isinstance(x, int) and x > max_idx:
                    max_idx = x
                if x == 0:
                    has_zero = True
    if max_idx < 0:
        raise ValueError("no integers found in permutation data")
    base = 0 if has_zero else 1
    n = max_idx + (1 if base == 0 else 0)

    perms: List[Perm] = []
    for item in val:
        if not (isinstance(item, list) and all(isinstance(x, int) for x in item)):
            raise ValueError(f"cannot parse permutation item: {item}")
        if len(item) == n:
            # explicit permutation: convert to 0-based if necessary
            perm = tuple(int(x) - 1 for x in item) if base == 1 else tuple(int(x) for x in item)
            if sorted(perm) != list(range(n)):
                raise ValueError(f"not a permutation of 0..{n-1}: {item}")
            perms.append(perm)
        else:
            # treat as cycle notation
            cyc = [int(x) + 1 for x in item] if base == 0 else [int(x) for x in item]
            perm = perm_from_cycles(n, [cyc])
            if sorted(perm) != list(range(n)):
                raise ValueError(f"cycle conversion did not produce a permutation: {item}")
            perms.append(perm)
    return perms


def load_generators_from_file(path: Path) -> Dict[str, List[Perm]]:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    result: Dict[str, List[Perm]] = {}
    for name, val in data.items():
        perms = parse_value(val)
        result[name] = perms
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("file", type=Path, help="JSON file with permutation lists")
    args = parser.parse_args()
    gens_map = load_generators_from_file(args.file)
    # build Golay code data for row check
    from tools.s12_universal_algebra import (
        enumerate_linear_code_f3,
        ternary_golay_generator_matrix,
    )
    gen = ternary_golay_generator_matrix()
    generator_rows = [tuple(int(x) % 3 for x in row) for row in gen]
    code_set = set(enumerate_linear_code_f3(gen))

    for name, perms in gens_map.items():
        print(f"Processing {name}: {len(perms)} generators")
        lifts = find_sign_lifts_for_group(perms, generator_rows, code_set)
        if lifts is None:
            print("  no sign lift found (generator rows alone)")
            continue
        order = monomial_group_order(list(zip(perms, lifts)))
        print(f"  sign lifts found; monomial group order = {order}")
    print("done")


if __name__ == "__main__":
    main()
