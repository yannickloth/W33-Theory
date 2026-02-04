#!/usr/bin/env python3
"""
Build the vertex map between:
  - the canonical Schläfli 27 (E6-id labeling, 0..26)
and
  - the canonical W33 embedding's H27 subset (W33 vertex ids, 0..39).

This is needed to pull the *real* W33 holonomy/clock data (defined on the 40-vertex
quotient graph Q = complement of W33) down onto the 27-state Schläfli sector used
by the E6-on-27 certificate + dynamics demos.

We compute the map by:
  1) constructing W33 from F3^4,
  2) extracting H12/H27 around v0=0 and building the kernel graph K on H27,
  3) building the Schläfli SRG(27,16,10,8) from the same E8 W(E6) 27-orbit used in
     artifacts/we6_signed_action_on_27.json,
  4) finding an explicit graph isomorphism K -> Schläfli via double-six matching,
  5) composing with the orbit-local -> E6-id permutation from canonical SU3+cubic artifacts.

Writes:
  - artifacts/schlafli_e6id_to_w33_h27.json
"""

from __future__ import annotations

import csv
import importlib.util
import io
import itertools
import json
import sys
import zipfile
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
canon = _load_module(
    ROOT / "tools" / "solve_canonical_su3_gauge_and_cubic.py",
    "solve_canonical_su3_gauge_and_cubic",
)


def _canonical_double_six_labeling(
    adj: np.ndarray, ds: tuple[tuple[int, ...], tuple[int, ...], dict[int, int]]
) -> tuple[list[int], list[int], dict[tuple[int, int], int]]:
    """
    Canonically label a double-six (A,B,match) by:
      - sorting A to get positions 0..5,
      - ordering B by the matching of those A positions,
      - labeling the remaining 15 vertices by duads (i,j) determined by which TWO A-vertices
        they are NON-adjacent to.
    """
    A, B, match = ds
    A_pos = sorted(A)
    B_pos = [int(match[a]) for a in A_pos]
    A_set = set(A_pos)
    B_set = set(B_pos)
    rem = [v for v in range(adj.shape[0]) if v not in A_set and v not in B_set]
    if len(rem) != 15:
        raise RuntimeError("Expected 15 remaining vertices")

    a_index = {a: i for i, a in enumerate(A_pos)}
    rem_by_duad: Dict[tuple[int, int], int] = {}
    for v in rem:
        nonA = [a_index[a] for a in A_pos if not bool(adj[v, a])]
        if len(nonA) != 2:
            raise RuntimeError("Remaining vertex does not have 2 non-neighbors in A")
        i, j = sorted(nonA)
        key = (i, j)
        if key in rem_by_duad:
            raise RuntimeError("Duad label collision")
        rem_by_duad[key] = int(v)
    if len(rem_by_duad) != 15:
        raise RuntimeError("Expected 15 duads")
    return A_pos, B_pos, rem_by_duad


def _find_isomorphism_via_double_sixes(
    adj1: np.ndarray, adj2: np.ndarray
) -> Dict[int, int]:
    """
    Find an isomorphism f: V1->V2 between two SRG(27,16,10,8) graphs by matching
    double-sixes and allowing all 6! permutations of A-labels plus optional A/B swaps.
    """
    k6_1 = cds.find_k_cliques(adj1, 6)
    ds_1 = cds.find_double_sixes(adj1, k6_1)
    k6_2 = cds.find_k_cliques(adj2, 6)
    ds_2 = cds.find_double_sixes(adj2, k6_2)
    if len(ds_1) != 36 or len(ds_2) != 36:
        raise RuntimeError("Expected 36 double-sixes in each graph")

    perms = list(itertools.permutations(range(6)))

    def is_iso(f: Dict[int, int]) -> bool:
        n = adj1.shape[0]
        for i in range(n):
            fi = f[i]
            for j in range(i + 1, n):
                if bool(adj1[i, j]) != bool(adj2[fi, f[j]]):
                    return False
        return True

    for ds1 in ds_1:
        for swap1 in (False, True):
            A1, B1, m1 = ds1
            if swap1:
                inv1 = {v: k for k, v in m1.items()}
                A1, B1, m1 = B1, A1, inv1
            A1_pos_raw, B1_pos_raw, rem1 = _canonical_double_six_labeling(
                adj1, (A1, B1, m1)
            )

            for ds2 in ds_2:
                for swap2 in (False, True):
                    A2, B2, m2 = ds2
                    if swap2:
                        inv2 = {v: k for k, v in m2.items()}
                        A2, B2, m2 = B2, A2, inv2
                    A2_pos_raw, B2_pos_raw, rem2_raw = _canonical_double_six_labeling(
                        adj2, (A2, B2, m2)
                    )

                    for pi in perms:
                        A1_pos = [A1_pos_raw[i] for i in range(6)]
                        B1_pos = [B1_pos_raw[i] for i in range(6)]

                        A2_pos = [A2_pos_raw[pi[i]] for i in range(6)]
                        B2_pos = [B2_pos_raw[pi[i]] for i in range(6)]
                        rem2: Dict[tuple[int, int], int] = {}
                        for (i, j), v in rem2_raw.items():
                            ii, jj = sorted((pi[i], pi[j]))
                            rem2[(ii, jj)] = int(v)

                        f: Dict[int, int] = {}
                        for i in range(6):
                            f[int(A1_pos[i])] = int(A2_pos[i])
                            f[int(B1_pos[i])] = int(B2_pos[i])
                        for key, v1 in rem1.items():
                            f[int(v1)] = int(rem2[key])

                        if len(f) != 27:
                            continue
                        if is_iso(f):
                            return f

    raise RuntimeError("Failed to find graph isomorphism via double-sixes")


def main() -> None:
    out_json = ROOT / "artifacts" / "schlafli_e6id_to_w33_h27.json"
    out_json.parent.mkdir(parents=True, exist_ok=True)

    # Build W33 (F3^4 model used by the existing firewall mapping tool) and H12/H27 around v0=0.
    pts_f3, w33_adj = cds.build_w33_f3()
    v0 = 0
    H12 = sorted(int(x) for x in np.nonzero(w33_adj[v0])[0])
    H27 = sorted(set(range(40)) - set(H12) - {v0})
    if len(H12) != 12 or len(H27) != 27:
        raise RuntimeError("Unexpected H12/H27 sizes")

    # Map the F3-model labeling to the canonical labeling used in the holonomy bundles.
    # Empirically this is just the coordinate swap (x0,x1,x2,x3)->(x0,x2,x1,x3) followed by projective normalization.
    symplectic_bundle = ROOT / "W33_symplectic_audit_bundle.zip"
    if not symplectic_bundle.exists():
        raise RuntimeError(f"Missing required bundle: {symplectic_bundle}")

    bundle_pts: List[Tuple[int, int, int, int]] = []
    with zipfile.ZipFile(symplectic_bundle) as zf:
        with zf.open("points.csv") as raw:
            text = io.TextIOWrapper(raw, encoding="utf-8")
            for r in csv.DictReader(text):
                s = r["rep_vector_GF3"].strip()
                bundle_pts.append(tuple(int(ch) for ch in s))

    rep_to_id = {v: i for i, v in enumerate(bundle_pts)}

    def normalize(vec: Tuple[int, int, int, int]) -> Tuple[int, int, int, int]:
        v = list(vec)
        for i in range(4):
            if v[i] != 0:
                inv = 1 if v[i] == 1 else 2
                v = [(x * inv) % 3 for x in v]
                break
        return tuple(int(x) for x in v)  # type: ignore[return-value]

    f3_to_bundle: List[int] = []
    for p in pts_f3:
        q = (p[0], p[2], p[1], p[3])  # swap coords 1 and 2
        qn = normalize(q)
        bid = rep_to_id.get(qn)
        if bid is None:
            raise RuntimeError("Failed to map F3 point to bundle point id")
        f3_to_bundle.append(int(bid))
    if len(set(f3_to_bundle)) != 40:
        raise RuntimeError("F3->bundle point-id map is not a bijection")

    # Build kernel adjacency on local indices 0..26 for H27 (good non-orth pairs).
    idx = {u: i for i, u in enumerate(H27)}
    kernel_adj = np.zeros((27, 27), dtype=bool)
    for a in range(len(H27)):
        for b in range(a + 1, len(H27)):
            u = H27[a]
            v = H27[b]
            # firewall applies to non-orth pairs: u,v are non-edges of W33
            if bool(w33_adj[u, v]):
                continue
            Nu = set(int(x) for x in np.nonzero(w33_adj[u])[0])
            Nv = set(int(x) for x in np.nonzero(w33_adj[v])[0])
            common = Nu & Nv
            if common <= set(H12):
                continue
            i, j = idx[u], idx[v]
            kernel_adj[i, j] = kernel_adj[j, i] = True

    # Build Schläfli graph from the reference orbit.
    act = json.loads(
        (ROOT / "artifacts" / "we6_signed_action_on_27.json").read_text(
            encoding="utf-8"
        )
    )
    oi_ref = int(act["reference_orbit"]["orbit_index"])
    roots = cds.construct_e8_roots()
    orbits = cds.compute_we6_orbits(roots)
    o27 = orbits[oi_ref]
    sch_adj, _ = cds.build_schlafli_adjacency(roots, o27)

    # Find kernel -> schlafli isomorphism (local indices -> orbit-local indices).
    f = _find_isomorphism_via_double_sixes(kernel_adj, sch_adj)
    if sorted(f.keys()) != list(range(27)) or sorted(f.values()) != list(range(27)):
        raise RuntimeError("Isomorphism is not a permutation")

    # Orbit-local -> canonical E6-id mapping via the canonical SU3+cubic key list.
    canon_data = json.loads(
        (ROOT / "artifacts" / "canonical_su3_gauge_and_cubic.json").read_text(
            encoding="utf-8"
        )
    )
    e6_keys_27 = [tuple(int(x) for x in k) for k in canon_data["e6_keys_27_k2"]]
    key_to_e6id = {k: i for i, k in enumerate(e6_keys_27)}
    pos_to_e6id: List[int] = []
    for ridx in o27:
        kk = canon.e6_key(roots[int(ridx)])
        eid = key_to_e6id.get(tuple(int(x) for x in kk))
        if eid is None:
            raise RuntimeError("Failed to map orbit vertex to canonical E6 id")
        pos_to_e6id.append(int(eid))
    if sorted(pos_to_e6id) != list(range(27)):
        raise RuntimeError("Orbit-local -> E6-id mapping is not a permutation")

    # Compose to get E6-id -> W33 vertex (in H27) mapping, in both labelings.
    e6id_to_w33_f3 = [-1] * 27
    e6id_to_w33_bundle = [-1] * 27
    e6id_to_h27local = [-1] * 27
    e6id_to_sch_pos = [-1] * 27
    for h27_local in range(27):
        sch_pos = int(f[h27_local])
        e6id = int(pos_to_e6id[sch_pos])
        w33_v_f3 = int(H27[h27_local])
        w33_v_bundle = int(f3_to_bundle[w33_v_f3])
        if e6id_to_w33_f3[e6id] != -1:
            raise RuntimeError("E6-id collision in mapping")
        e6id_to_w33_f3[e6id] = w33_v_f3
        e6id_to_w33_bundle[e6id] = w33_v_bundle
        e6id_to_h27local[e6id] = int(h27_local)
        e6id_to_sch_pos[e6id] = int(sch_pos)

    if sorted(e6id_to_w33_f3) != sorted(H27):
        raise RuntimeError("E6-id -> W33 mapping is not a bijection onto H27")

    out = {
        "status": "ok",
        "w33": {
            "v0_f3": int(v0),
            "H12_f3": H12,
            "H27_f3": H27,
            "v0_bundle": int(f3_to_bundle[v0]),
            "H12_bundle": [int(f3_to_bundle[x]) for x in H12],
            "H27_bundle": [int(f3_to_bundle[x]) for x in H27],
            "labeling_note": "bundle labeling = swap coords 1<->2 in GF3^4 rep_vector then renormalize",
        },
        "reference_orbit_index": int(oi_ref),
        "maps": {
            "e6id_to_w33_f3": e6id_to_w33_f3,
            "e6id_to_w33_bundle": e6id_to_w33_bundle,
            "e6id_to_h27local": e6id_to_h27local,
            "e6id_to_schlafli_orbit_pos": e6id_to_sch_pos,
            "w33_f3_to_bundle": f3_to_bundle,
        },
    }

    out_json.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"Wrote {out_json}")


if __name__ == "__main__":
    main()
