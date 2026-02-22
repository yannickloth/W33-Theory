#!/usr/bin/env python3
"""Debug harness to call orbit analysis functions and print exceptions.
"""
from __future__ import annotations

import traceback

from tools.forbid_full_aut_orbit_analysis import (
    build_schlafli_mapping,
    induce_27_action,
    triad_orbit,
)


def main():
    try:
        print("Calling build_schlafli_mapping()...")
        sch_to_w, wlines = build_schlafli_mapping()
        print("-> done. #wlines=", len(wlines))

        print("Inducing 27-action perms...")
        perms27 = induce_27_action(sch_to_w, wlines)
        print("-> done. #perms=", len(perms27))

        cand = (0, 18, 25)
        orb = triad_orbit(cand, perms27)
        print(f"Orbit for {cand}: size {len(orb)} sample: {orb[:6]}")
    except Exception as e:
        print("Exception during debug run:")
        traceback.print_exc()


if __name__ == "__main__":
    main()
