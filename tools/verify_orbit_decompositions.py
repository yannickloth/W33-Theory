#!/usr/bin/env python3
"""Verify orbit decompositions of two 120‑point PSp(4,3) actions.

Originally part of the WE6↔PSp43 bundle; now integrated into tools.
Reads:
  - artifacts/sp43_edgepair_generators.json
  - SP43_TO_WE6_TRUE_FIXED_BUNDLE_v01_2026-02-25/sp43_line_perms_fixed.json

and writes artifacts/line_action_orbits.json summarizing the orbit sizes.
"""
from pathlib import Path
from collections import deque
import json

ROOT = Path(__file__).resolve().parents[1]


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def orbits_from_gens(n, gens):
    seen = [False]*n
    orbits = []
    for start in range(n):
        if seen[start]:
            continue
        q = deque([start])
        seen[start] = True
        orb = [start]
        while q:
            x = q.popleft()
            for g in gens:
                y = g[x]
                if not seen[y]:
                    seen[y] = True
                    q.append(y)
                    orb.append(y)
        orbits.append(sorted(orb))
    orbits.sort(key=len, reverse=True)
    return orbits


def main():
    ep_path = ROOT / "artifacts" / "sp43_edgepair_generators.json"
    ep = load_json(ep_path)
    ep_gens = ep.get("pair_generators", ep)
    n_ep = len(ep_gens[0])
    ep_orbits = orbits_from_gens(n_ep, ep_gens)

    line_path = ROOT / "SP43_TO_WE6_TRUE_FIXED_BUNDLE_v01_2026-02-25" / "sp43_line_perms_fixed.json"
    line_gens = load_json(line_path)
    n_line = len(line_gens[0])
    line_orbits = orbits_from_gens(n_line, line_gens)

    print("=== ORBIT DECOMPOSITION CHECK ===")
    print(f"edgepair degree: {n_ep}  | orbits: {[len(o) for o in ep_orbits]}")
    print(f"line    degree: {n_line}| orbits: {[len(o) for o in line_orbits]}")
    if len(ep_orbits) == 1:
        print("edgepair action is TRANSITIVE [ok]")
    else:
        print("edgepair action is NOT transitive [fail]")
    if len(line_orbits) > 1:
        print("line action is INTRANSITIVE [ok]")
    else:
        print("line action is transitive (unexpected) [fail]")

    out = {
        "edgepair_degree": n_ep,
        "edgepair_orbit_sizes": [len(o) for o in ep_orbits],
        "line_degree": n_line,
        "line_orbit_sizes": [len(o) for o in line_orbits],
        "line_orbits": line_orbits,
    }
    (ROOT / "artifacts" / "line_action_orbits.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    print("Wrote artifacts/line_action_orbits.json")


if __name__ == "__main__":
    main()
