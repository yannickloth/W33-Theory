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

If the value is a list of lists of integers of length *n*, it is treated as
cycle notation and converted to a permutation of length *n* using the helper
from derive_m12_p144_suborbits.

This tool is intended to make it easy to test new ladder rungs by supplying
candidate permutation generators without editing other scripts.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np

from scripts.monomial_utils import (
    find_sign_lifts_for_group,
    monomial_group_order,
)
from scripts.derive_m12_p144_suborbits import perm_from_cycles


Perm = Tuple[int, ...]


def parse_value(val: Any) -> List[Perm]:
    """Interpret value from JSON as a list of permutations."""
    if not isinstance(val, list):
        raise ValueError("expected list of permutations")
    perms: List[Perm] = []
    for item in val:
        if isinstance(item, list) and item and all(isinstance(x, int) for x in item):
            # ambiguous: either cycle or full perm; decide by length relative to other items
            # if length equals n for some n, treat as explicit perm
            # else treat as single cycle
            perms.append(tuple(item))
        else:
            raise ValueError(f"cannot parse permutation item: {item}")
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
