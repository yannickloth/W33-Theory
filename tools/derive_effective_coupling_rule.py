#!/usr/bin/env python3
"""
Derive an "effective interaction rule" by intersecting:
  - the canonical E6 cubic triads (45),
  - the firewall forbidden set (9),
  - an SU(6)×SU(2) decomposition defined by a double-six (A(6), B(6), R(15)).

The key (re-)verified structure is:
  - 45 triads split as 30 ABR + 15 RRR (relative to any double-six),
  - ABR triads are exactly {A_i, B_j, R_{ij}} for i≠j,
  - RRR triads are exactly perfect matchings on the 6 letters,
  - firewall deletes 6 ABR + 3 RRR, leaving 36 effective triads.

Additionally, for the canonical (lexicographically-first) double-six, we recognize a clean
"trinification-style" description of the firewall pattern on the 6 letters:
  - a 3+3 bipartition,
  - the 3 forbidden matchings are the even (A3) bijections between halves,
  - the 6 forbidden ABR couplings are one directed 3-cycle on each half.

Writes:
  - artifacts/effective_coupling_rule.json
  - artifacts/effective_coupling_rule.md
"""

from __future__ import annotations

import importlib.util
import itertools
import json
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

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


def _triad_key(t: Iterable[int]) -> Tuple[int, int, int]:
    a, b, c = (int(x) for x in t)
    return tuple(sorted((a, b, c)))


def _perm_parity(perm: Tuple[int, int, int]) -> int:
    inv = 0
    for i in range(3):
        for j in range(i + 1, 3):
            if perm[i] > perm[j]:
                inv += 1
    return inv % 2


def _even_matchings_between_halves(
    L: Tuple[int, int, int], R: Tuple[int, int, int]
) -> set[Tuple[Tuple[int, int], Tuple[int, int], Tuple[int, int]]]:
    Ls = list(L)
    Rs = list(R)
    out = set()
    for perm in itertools.permutations((0, 1, 2)):
        if _perm_parity(perm) != 0:
            continue
        pairs = tuple(sorted(tuple(sorted((Ls[i], Rs[perm[i]]))) for i in range(3)))
        out.add(pairs)  # type: ignore[arg-type]
    if len(out) != 3:
        raise RuntimeError("Expected 3 even matchings between halves")
    return out


def _directed_3cycle_edges(triple: Tuple[int, int, int]) -> set[Tuple[int, int]]:
    a, b, c = triple
    return {(a, b), (b, c), (c, a)}


@dataclass(frozen=True)
class LetterModel:
    A_order: Tuple[int, ...]  # 6 vertices (E6-id)
    B_order: Tuple[int, ...]  # 6 vertices matched to A_order
    rem_by_duad: Dict[Tuple[int, int], int]  # duad -> vertex
    duad_by_rem: Dict[int, Tuple[int, int]]  # vertex -> duad
    v_to_letter_side: Dict[int, Tuple[int, str]]  # vertex -> (letter 0..5, "A"/"B")


def _build_reference_schlafli_adj_e6id() -> np.ndarray:
    act = json.loads(
        (ROOT / "artifacts" / "we6_signed_action_on_27.json").read_text(
            encoding="utf-8"
        )
    )
    oi_ref = int(act["reference_orbit"]["orbit_index"])

    roots = cds.construct_e8_roots()
    orbits = cds.compute_we6_orbits(roots)
    o27 = orbits[oi_ref]
    adj_pos, _ = cds.build_schlafli_adjacency(roots, o27)

    canon_data = json.loads(
        (ROOT / "artifacts" / "canonical_su3_gauge_and_cubic.json").read_text(
            encoding="utf-8"
        )
    )
    e6_keys_27 = [tuple(int(x) for x in k) for k in canon_data["e6_keys_27_k2"]]
    key_to_e6id = {k: i for i, k in enumerate(e6_keys_27)}

    pos_to_e6id: List[int] = []
    for ridx in o27:
        kk = canon.e6_key(roots[ridx])
        pos_to_e6id.append(int(key_to_e6id[tuple(int(x) for x in kk)]))
    if sorted(pos_to_e6id) != list(range(27)):
        raise RuntimeError("orbit-local -> E6-id mapping is not a permutation")

    e6id_to_pos = [0] * 27
    for pos, eid in enumerate(pos_to_e6id):
        e6id_to_pos[eid] = pos

    adj = np.zeros((27, 27), dtype=bool)
    for i in range(27):
        pi = e6id_to_pos[i]
        for j in range(27):
            adj[i, j] = bool(adj_pos[pi, e6id_to_pos[j]])

    ok, msg = cds.verify_srg(adj, 27, 16, 10, 8)
    if not ok:
        raise RuntimeError(f"Schläfli SRG check failed: {msg}")
    return adj


def _choose_canonical_double_six_e6id() -> Tuple[Tuple[int, ...], Tuple[int, ...]]:
    rep = json.loads(
        (ROOT / "artifacts" / "bad_triads_vs_double_sixes.json").read_text(
            encoding="utf-8"
        )
    )
    ds_key = rep["per_double_six"][0]["ds_key_e6id"]
    A = tuple(int(x) for x in ds_key[0])
    B = tuple(int(x) for x in ds_key[1])
    if len(A) != 6 or len(B) != 6:
        raise RuntimeError("Unexpected ds_key shape")
    return (A, B)


def _letter_model_from_double_six(
    adj: np.ndarray, A: Tuple[int, ...], B: Tuple[int, ...]
) -> LetterModel:
    A_set = set(int(x) for x in A)
    B_set = set(int(x) for x in B)
    if A_set & B_set:
        raise RuntimeError("A,B overlap")

    # Determine the perfect matching A -> B by unique adjacency across halves.
    match: Dict[int, int] = {}
    inv: Dict[int, int] = {}
    for a in A_set:
        neigh = [b for b in B_set if bool(adj[a, b])]
        if len(neigh) != 1:
            raise RuntimeError("Not a double-six: A vertex lacks unique B neighbor")
        b = int(neigh[0])
        if b in inv:
            raise RuntimeError("Not a double-six: matching is not injective")
        match[int(a)] = b
        inv[b] = int(a)

    A_order = tuple(sorted(A_set))
    a_index = {a: i for i, a in enumerate(A_order)}
    B_order = tuple(int(match[a]) for a in A_order)

    v_to_letter_side: Dict[int, Tuple[int, str]] = {}
    for a in A_order:
        v_to_letter_side[a] = (a_index[a], "A")
    for b in B_order:
        v_to_letter_side[b] = (a_index[inv[b]], "B")

    # remaining15 duads: determined by the two A letters each remaining vertex is NOT adjacent to.
    rem = [v for v in range(27) if v not in A_set and v not in B_set]
    if len(rem) != 15:
        raise RuntimeError("Expected 15 remaining vertices")

    rem_by_duad: Dict[Tuple[int, int], int] = {}
    for v in rem:
        nonA = [a_index[a] for a in A_order if not bool(adj[v, a])]
        if len(nonA) != 2:
            raise RuntimeError("Remaining vertex does not have 2 non-neighbors in A")
        i, j = sorted(int(x) for x in nonA)
        key = (i, j)
        if key in rem_by_duad:
            raise RuntimeError("Duad collision in remaining15 labeling")
        rem_by_duad[key] = int(v)
    if len(rem_by_duad) != 15:
        raise RuntimeError("Expected 15 duads")
    duad_by_rem = {v: duad for duad, v in rem_by_duad.items()}

    return LetterModel(
        A_order=A_order,
        B_order=B_order,
        rem_by_duad=rem_by_duad,
        duad_by_rem=duad_by_rem,
        v_to_letter_side=v_to_letter_side,
    )


def main() -> None:
    canon_data = json.loads(
        (ROOT / "artifacts" / "canonical_su3_gauge_and_cubic.json").read_text(
            encoding="utf-8"
        )
    )
    d_sign: Dict[Tuple[int, int, int], int] = {}
    for t in canon_data["solution"]["d_triples"]:
        triad = _triad_key(t["triple"])
        d_sign[triad] = int(t["sign"])
    if len(d_sign) != 45:
        raise RuntimeError("Expected 45 cubic triads")

    fw = json.loads(
        (ROOT / "artifacts" / "firewall_bad_triads_mapping.json").read_text(
            encoding="utf-8"
        )
    )
    bad_triads = sorted({_triad_key(t) for t in fw["bad_triangles_Schlafli_e6id"]})
    if len(bad_triads) != 9:
        raise RuntimeError("Expected 9 firewall-bad triads")
    bad_set = set(bad_triads)

    adj = _build_reference_schlafli_adj_e6id()
    A, B = _choose_canonical_double_six_e6id()
    lm = _letter_model_from_double_six(adj, A, B)

    A_set = set(lm.A_order)
    B_set = set(lm.B_order)
    R_set = set(range(27)) - A_set - B_set

    # Sector histogram (all 45 / bad 9)
    hist_all = Counter()
    hist_bad = Counter()
    for t in d_sign:
        a = sum(1 for x in t if x in A_set)
        b = sum(1 for x in t if x in B_set)
        r = 3 - a - b
        key = f"A{a}B{b}R{r}"
        hist_all[key] += 1
        if t in bad_set:
            hist_bad[key] += 1

    if dict(hist_all) != {"A1B1R1": 30, "A0B0R3": 15}:
        raise RuntimeError(f"Unexpected triad sector distribution: {dict(hist_all)}")
    if dict(hist_bad) != {"A1B1R1": 6, "A0B0R3": 3}:
        raise RuntimeError(f"Unexpected firewall sector distribution: {dict(hist_bad)}")

    # Build the full ABR sign matrix Y_ij = sign(triad {A_i, B_j, R_ij}), i≠j.
    Y = [[0 for _ in range(6)] for _ in range(6)]
    for i in range(6):
        for j in range(6):
            if i == j:
                continue
            a_v = lm.A_order[i]
            b_v = lm.B_order[j]
            r_v = lm.rem_by_duad[tuple(sorted((i, j)))]
            tri = _triad_key((a_v, b_v, r_v))
            if tri not in d_sign:
                raise RuntimeError("Missing expected ABR triad")
            Y[i][j] = int(d_sign[tri])

    # Sanity: Y is skew-symmetric for the full E6 cubic.
    for i in range(6):
        for j in range(i + 1, 6):
            if Y[i][j] != -Y[j][i]:
                raise RuntimeError("ABR sign matrix is not skew-symmetric")

    # Extract the 15 RRR matchings and classify them as bad/ok.
    rrr_matchings = []
    for tri in sorted(d_sign.keys()):
        inR = [x for x in tri if x in R_set]
        if len(inR) != 3:
            continue
        duads = tuple(sorted(tuple(sorted(lm.duad_by_rem[v])) for v in inR))
        flat = sorted([x for p in duads for x in p])
        if flat != list(range(6)):
            raise RuntimeError("RRR triad is not a perfect matching on letters 0..5")
        rrr_matchings.append(
            {
                "triad": list(tri),
                "duads": [list(p) for p in duads],
                "d_sign": int(d_sign[tri]),
                "is_firewall_bad": bool(tri in bad_set),
            }
        )
    if len(rrr_matchings) != 15:
        raise RuntimeError(f"Expected 15 RRR matchings, got {len(rrr_matchings)}")

    # Decode firewall-bad triads in letter language.
    bad_oriented = set()
    bad_matching_duads = set()
    for tri in bad_triads:
        inA = [x for x in tri if x in A_set]
        inB = [x for x in tri if x in B_set]
        inR = [x for x in tri if x in R_set]
        if len(inA) == 1 and len(inB) == 1 and len(inR) == 1:
            i = lm.v_to_letter_side[inA[0]][0]
            j = lm.v_to_letter_side[inB[0]][0]
            bad_oriented.add((int(i), int(j)))
            # also verify it is the expected R_ij
            duad = tuple(sorted(lm.duad_by_rem[inR[0]]))
            if duad != tuple(sorted((i, j))):
                raise RuntimeError(
                    "Firewall-bad ABR triad is not of form (A_i,B_j,R_ij)"
                )
        elif len(inR) == 3:
            duads = tuple(sorted(tuple(sorted(lm.duad_by_rem[v])) for v in inR))
            bad_matching_duads.add(tuple(sorted(duads)))  # type: ignore[arg-type]
        else:
            raise RuntimeError("Firewall-bad triad not ABR/RRR")
    if len(bad_oriented) != 6 or len(bad_matching_duads) != 3:
        raise RuntimeError("Unexpected firewall bad ABR/RRR split")

    # Firewall-filtered ABR matrix (not necessarily skew-symmetric anymore): zero out forbidden oriented pairs.
    Y_eff = [[Y[i][j] for j in range(6)] for i in range(6)]
    for i, j in bad_oriented:
        Y_eff[i][j] = 0
    nonzero_eff = sum(
        1 for i in range(6) for j in range(6) if i != j and Y_eff[i][j] != 0
    )
    if nonzero_eff != 24:
        raise RuntimeError(f"Expected 24 surviving ABR couplings, got {nonzero_eff}")

    # Recognize a clean 3+3 bipartition pattern for the firewall.
    solutions = []
    letters = list(range(6))
    for L in itertools.combinations(letters, 3):
        L = tuple(sorted(int(x) for x in L))
        R = tuple(sorted(set(letters) - set(L)))
        even = _even_matchings_between_halves(L, R)
        if even != bad_matching_duads:
            continue
        for cycL in itertools.permutations(L, 3):
            edgesL = _directed_3cycle_edges(cycL)
            for cycR in itertools.permutations(R, 3):
                edgesR = _directed_3cycle_edges(cycR)
                if edgesL | edgesR == bad_oriented:
                    solutions.append(
                        {
                            "L": list(L),
                            "R": list(R),
                            "cycle_L": list(cycL),
                            "cycle_R": list(cycR),
                        }
                    )
    solutions = sorted(
        solutions,
        key=lambda s: (s["L"], s["cycle_L"], s["cycle_R"]),
    )
    if not solutions:
        raise RuntimeError(
            "Failed to recognize a clean 3+3 bipartition pattern for the firewall"
        )

    out = {
        "status": "ok",
        "canonical_double_six": {
            "A_e6id": list(lm.A_order),
            "B_e6id": list(lm.B_order),
        },
        "counts": {"triads_total": 45, "firewall_bad": 9, "firewall_good": 36},
        "sector_hist_all": {k: int(v) for k, v in sorted(hist_all.items())},
        "sector_hist_bad": {k: int(v) for k, v in sorted(hist_bad.items())},
        "letter_model": {
            "A_letters": [
                {"letter": i, "vertex": int(v)} for i, v in enumerate(lm.A_order)
            ],
            "B_letters": [
                {"letter": i, "vertex": int(v)} for i, v in enumerate(lm.B_order)
            ],
            "R_duads": [
                {"duad": [i, j], "vertex": int(v)}
                for (i, j), v in sorted(lm.rem_by_duad.items())
            ],
        },
        "cubic_ABR_matrix": {
            "Y": Y,
            "Y_effective": Y_eff,
            "forbidden_oriented_pairs": sorted([list(x) for x in bad_oriented]),
        },
        "cubic_RRR_matchings": rrr_matchings,
        "trinification_recognition": {
            "forbidden_matchings_duads": sorted(
                [[list(p) for p in m] for m in sorted(bad_matching_duads)]
            ),
            "solutions": solutions,
        },
    }

    out_json = ROOT / "artifacts" / "effective_coupling_rule.json"
    out_md = ROOT / "artifacts" / "effective_coupling_rule.md"
    out_json.write_text(json.dumps(out, indent=2), encoding="utf-8")

    # Compact markdown report.
    md = []
    md.append("# Effective coupling rule (cubic triads ∩ firewall)\n\n")
    md.append(
        f"- canonical double-six (E6-id): A={out['canonical_double_six']['A_e6id']} B={out['canonical_double_six']['B_e6id']}\n"
    )
    md.append(
        f"- triads: total={out['counts']['triads_total']} bad={out['counts']['firewall_bad']} good={out['counts']['firewall_good']}\n"
    )
    md.append(f"- sector hist all: `{out['sector_hist_all']}`\n")
    md.append(f"- sector hist bad: `{out['sector_hist_bad']}`\n\n")
    md.append("## ABR coupling matrix (signs)\n\n")
    md.append("`Y[i][j] = sign(triad {A_i, B_j, R_ij})` (i≠j)\n\n")
    for row in Y:
        md.append(f"- `{row}`\n")
    md.append("\n## Firewall-filtered ABR couplings\n\n")
    md.append(f"- forbidden oriented pairs (i->j): `{sorted(bad_oriented)}`\n\n")
    for row in Y_eff:
        md.append(f"- `{row}`\n")
    md.append("\n## Firewall forbidden RRR matchings\n\n")
    bad_rrr = [m for m in rrr_matchings if m["is_firewall_bad"]]
    for m in bad_rrr:
        md.append(f"- duads={m['duads']} triad={m['triad']}\n")
    md.append("\n## Recognized 3+3 (trinification) description\n\n")
    md.append(
        f"- solutions found: `{len(solutions)}` (symmetry/relabelling variants)\n"
    )
    md.append("```json\n")
    md.append(json.dumps(solutions[0], indent=2))
    md.append("\n```\n")

    out_md.write_text("".join(md), encoding="utf-8")

    print(f"Wrote {out_json}")
    print(f"Wrote {out_md}")


if __name__ == "__main__":
    main()
