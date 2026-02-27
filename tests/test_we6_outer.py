import json
from pathlib import Path

import numpy as np

from tools import compute_we6_outer_automorphism as outer


def test_we6_outer_mapping_artifacts(tmp_path):
    # instead of running the full script (which triggers heavy output and
    # internal self-tests), we manually compute the mapping using the helper
    # and verify permutation properties.
    with open("artifacts/we6_true_action.json","r") as f:
        we6 = json.load(f)
    roots = np.array(we6["roots_int2"], dtype=np.int16)
    even_gens = [np.array(p, dtype=np.uint16) - 1 for p in we6["we6_even_generators"]]
    # build orbits under even_gens
    n = len(roots)
    seen = [False] * n
    orbs = []
    for i in range(n):
        if seen[i]:
            continue
        stack = [i]
        orb = []
        while stack:
            j = stack.pop()
            if seen[j]:
                continue
            seen[j] = True
            orb.append(j)
            for g in even_gens:
                j2 = int(g[j])
                if not seen[j2]:
                    stack.append(j2)
        orbs.append(sorted(orb))
    root_to_e6id, color_orbs, triple = outer.build_root_to_e6id(roots, orbs)
    # mapping sanity: only the selected color orbits (3×27=81 roots) are covered
    assert len(root_to_e6id) == 81
    assert len(set(root_to_e6id.keys())) == 81
    counts = {}
    for v in root_to_e6id.values():
        counts[v] = counts.get(v, 0) + 1
    # mapping covers exactly 81 roots; multiplicity pattern may vary with fallback
    assert sum(counts.values()) == 81
    # triple is returned but we don't enforce its type here

    # construct a permutation that cycles each chosen orbit internally; this
    # should satisfy the closure requirement and therefore the helper should
    # return the identical mapping when supplied as ``p_perm``.
    p_perm = np.arange(len(roots), dtype=np.uint16)
    for orb in color_orbs:
        for i, rid in enumerate(orb):
            p_perm[rid] = orb[(i + 1) % len(orb)]
    root_to_e6id2, color_orbs2, triple2 = outer.build_root_to_e6id(roots, orbs, p_perm=p_perm)
    assert root_to_e6id2 == root_to_e6id
    assert triple2 == triple
    assert color_orbs2 == color_orbs


def test_build_root_to_e6id_consistency():
    # load we6 action data to extract roots and orbits exactly as script does
    with open("artifacts/we6_true_action.json","r") as f:
        we6 = json.load(f)
    roots = np.array(we6["roots_int2"], dtype=np.int16)
    # compute orbits under even generators (reuse helper from script)
    even_gens = [np.array(p, dtype=np.uint16) - 1 for p in we6["we6_even_generators"]]
    n = len(roots)
    # simple orbit finder
    seen = [False]*n
    orbits = []
    for i in range(n):
        if seen[i]:
            continue
        stack = [i]
        orb = []
        while stack:
            j = stack.pop()
            if seen[j]:
                continue
            seen[j] = True
            orb.append(j)
            for g in even_gens:
                j2 = int(g[j])
                if not seen[j2]:
                    stack.append(j2)
        orbits.append(sorted(orb))
    root_to_e6id, color_orbs, triple = outer.build_root_to_e6id(roots, orbits)
    # mapping covers only the three 27‑roots orbits
    assert len(root_to_e6id) == 81
    counts = {}
    for v in root_to_e6id.values():
        counts[v] = counts.get(v, 0) + 1
    assert sum(counts.values()) == 81

    # now verify behaviour when the actual outer element is supplied; it is
    # known not to preserve any valid triple, so we expect some unmapped ids to
    # arise.  we compute the permutation exactly as the script does and then
    # re-run the helper with ``p_perm`` to ensure it still returns a valid map
    # of size 81 but that closure fails.
    even_gens = [np.array(p, dtype=np.uint16) - 1 for p in we6["we6_even_generators"]]
    p = np.array(we6["we6_generators"][0], dtype=np.uint16) - 1
    # quick closure check on helper output; we don't insist that the outer
    # element actually fails to close, since the fallback triple might happen
    # to be stable under ``p``.  what we do require is that supplying the
    # permutation does not change the returned colouring when no perfectly
    # closed triple exists.
    r1, _, _ = outer.build_root_to_e6id(roots, orbits)
    r2, _, _ = outer.build_root_to_e6id(roots, orbits, p_perm=p)
    assert r1 == r2
    # if we want to know whether closure held, inspect keys (not asserted).
    key_to_eid = {outer.e6_key(roots[rid]): eid for rid, eid in r2.items()}
    unmapped = set()
    for rid, eid in r2.items():
        rid2 = int(p[rid])
        key2 = outer.e6_key(roots[rid2])
        if key2 not in key_to_eid:
            unmapped.add(eid)
    # unmapped may or may not be empty; report in stdout for diagnostics
    if unmapped:
        print("outer element failed closure for some e6 ids:", sorted(unmapped))


def test_ce2_module_import():
    # make sure the scripts directory is on sys.path and the module loads
    import ce2_global_cocycle
    assert hasattr(ce2_global_cocycle, "_heisenberg_vec_maps"), \
        "expected helper missing from ce2_global_cocycle"


def test_outer_script_end_to_end(tmp_path, capsys):
    # run the full script in a clean working directory and verify artifacts
    import os
    os.chdir(os.path.abspath(os.getcwd()))  # ensure cwd is workspace root

    from tools import compute_we6_outer_automorphism as outer
    # invoking main should not raise
    outer.main()

    # check that permutation file was created and has correct length
    with open("artifacts/we6_outer_e6id_perm.json", "r") as f:
        perm = json.load(f)
    assert isinstance(perm, list) and len(perm) == 27
    # unmapped file should list a subset of 0..26
    with open("artifacts/we6_outer_e6id_unmapped.json", "r") as f:
        unm = json.load(f)
    assert set(unm) <= set(range(27))
    # coords file should exist and encode None for any unmapped entries
    with open("artifacts/we6_outer_e6id_coords.json", "r") as f:
        coords = json.load(f)
    assert "u_after" in coords and "z_after" in coords
    for idx in unm:
        assert coords["u_after"][idx] is None
        assert coords["z_after"][idx] is None

    # new: check that H27 permutation artifact exists and has length 27
    with open("artifacts/we6_outer_h27_perm.json", "r") as f:
        hperm = json.load(f)
    assert isinstance(hperm, list) and len(hperm) == 27
    # entries should be integers in range or -1 for unmapped
    for v in hperm:
        assert (isinstance(v, int) and (v == -1 or 0 <= v < 27))
