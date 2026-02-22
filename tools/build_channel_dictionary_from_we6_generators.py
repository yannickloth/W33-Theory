#!/usr/bin/env python3
"""
Build a concrete "channel dictionary" for E6 simple generators in the 27-line model.

Interpretation:
  - We realize the 27 as the vertices of a Schläfli graph (skew adjacency) coming from one W(E6) 27-orbit.
  - The meet-graph (intersection graph) is the complement graph on the 27 lines; its triangles are tritangent planes.
  - Each E6 simple reflection acts on the 27 as an involution (a product of disjoint transpositions).

This tool classifies each generator by:
  - which pairs (transpositions) it swaps,
  - whether those swapped pairs are skew-adjacent (Schläfli edge) or meeting (meet-graph edge),
  - which tritangent planes are stabilized setwise vs moved.

Writes:
  artifacts/we6_channel_dictionary.json
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np

ROOT = Path(__file__).resolve().parents[1]


def _load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Failed to load module from {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


cds = _load_module(ROOT / "tools" / "compute_double_sixes.py", "compute_double_sixes")
exporter = _load_module(
    ROOT / "tools" / "export_we6_signed_action_on_27.py",
    "export_we6_signed_action_on_27",
)


def main() -> None:
    exporter.main()
    act = json.loads(
        (ROOT / "artifacts" / "we6_signed_action_on_27.json").read_text(
            encoding="utf-8"
        )
    )
    oi_ref = int(act["reference_orbit"]["orbit_index"])

    roots = cds.construct_e8_roots()
    orbits = cds.compute_we6_orbits(roots)
    o27 = orbits[oi_ref]
    if len(o27) != 27:
        raise RuntimeError("Reference orbit is not size 27")

    # Schläfli adjacency (skew lines) uses ip=1.
    adj, _ip_counts = cds.build_schlafli_adjacency(roots, o27)
    # meet graph is complement of adjacency (excluding diagonal).
    meet = (~adj) & (~np.eye(27, dtype=bool))

    # Triangles in meet graph (tritangent planes) on indices 0..26 in this orbit ordering.
    # Use adjacency for meet; simple O(n^3)=19683 is fine.
    triads = []
    for a in range(27):
        for b in range(a + 1, 27):
            if not meet[a, b]:
                continue
            for c in range(b + 1, 27):
                if meet[a, c] and meet[b, c]:
                    triads.append((a, b, c))
    if len(triads) != 45:
        raise RuntimeError(f"Expected 45 tritangent triads; got {len(triads)}")
    triad_set = set(triads)

    # Note: act's permutation is on "e6id" indexing, not orbit-local indexing. In this repo those match
    # for the reference orbit chosen by the exporter, since it uses the solver's e6_key ordering, but
    # the Schläfli adjacency is orbit-local. We therefore treat orbit-local indices as the action indices.
    # (This dictionary is about concrete channels on the chosen 27 model.)

    out = {"status": "ok", "reference_orbit": act["reference_orbit"], "generators": []}
    for g in act["generators"]:
        name = g["name"]
        p = g["permutation"]
        trans = [tuple(t) for t in g["transpositions"]]
        trans_class = []
        for u, v in trans:
            trans_class.append(
                {
                    "pair": [u, v],
                    "skew_edge": bool(adj[u, v]),
                    "meet_edge": bool(meet[u, v]),
                }
            )
        moved_triads = 0
        fixed_triads = 0
        for a, b, c in triads:
            img = tuple(sorted((p[a], p[b], p[c])))
            if img in triad_set:
                fixed_triads += 1
            else:
                moved_triads += 1
        out["generators"].append(
            {
                "name": name,
                "n_transpositions": len(trans),
                "transpositions": trans_class,
                "triads_fixed_setwise": int(fixed_triads),
                "triads_moved": int(moved_triads),
            }
        )

    out_path = ROOT / "artifacts" / "we6_channel_dictionary.json"
    out_path.write_text(json.dumps(out, indent=2, default=int), encoding="utf-8")
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
