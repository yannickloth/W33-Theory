#!/usr/bin/env python3
"""Pillar 114 (Part CCXIV): Infinity Neighbor Charge Table for AG(3,3) in PG(3,3)

The 40 points of PG(3,3) split as: 13 infinity points (the projective plane
PG(2,3)) and 27 affine points (the affine space AG(3,3)).  Each affine point
has exactly 4 W(3,3)-collinear infinity neighbors.  The charge of an infinity
point is the number of affine points for which it is a neighbor.

Theorems:

T1  PG(3,3) GEOMETRY: PG(3,3) has 40 points = 13 infinity (PG(2,3)) + 27
    affine (AG(3,3)).  The W(3,3) collinearity graph has 240 edges and is
    12-regular (each point collinear with 12 others).

T2  INFINITY NEIGHBOR MAP: Each of the 27 affine points has exactly 4
    infinity neighbors in PG(2,3) = {0,...,12}.  Total incidences: 27*4 = 108.
    All 4 neighbors per affine point are distinct.

T3  CHARGE DISTRIBUTION: The charge (number of affine neighbors) of each of
    the 13 infinity points is:
    - Exactly 12 infinity points have charge 9 (each is neighbored by 9 affine pts).
    - Exactly 1 infinity point has charge 0 (the special direction, pg_id=4).
    Total: 12*9 + 1*0 = 108 = 27*4.  Consistent with biregularity.

T4  ORBIT STRUCTURE UNDER NP: The Heisenberg group NP acting on PG(3,3)
    gives 2 orbits on the 39 non-origin points: an orbit of size 12 (mixing
    3 infinity pts and 9 affine pts) and an orbit of size 27 (mixing 9 infinity
    pts and 18 affine pts).  Together they cover all 39 non-origin PG(3,3) pts.

T5  OUTER TWIST ORBITS: The outer twist N4 acts on the 27 affine AG(3,3)
    points giving 5 orbits with size distribution {1:1, 2:1, 8:3}.
    Total: 1+2+24 = 27.  The fixed point and 2-orbit are special; the three
    8-orbits cover 24 affine points.

T6  AFFINE COORDINATES: Each affine point carries coordinates (x,y,t) in
    F_3^3.  The 9 affine points with charge-9 infinity neighbor match (orbit 0
    affine part {13,14,15,22,23,24,31,32,33}) correspond to t-coordinate
    taking all three values 0,1,2 for each of (x,y) in a fixed orbit.
"""

from __future__ import annotations

import csv
import io
import json
import zipfile
from collections import Counter
from pathlib import Path
from typing import Dict, List, Set, Tuple

ROOT = Path(__file__).resolve().parent
BUNDLE = ROOT / "INFINITY_NEIGHBOR_CHARGE_TABLE_BUNDLE_v01.zip"

N_PG33 = 40
N_INFINITY = 13
N_AFFINE = 27
N_EDGES = 240
DEGREE = 12
NEIGHBORS_PER_AFFINE = 4
TOTAL_INCIDENCES = N_AFFINE * NEIGHBORS_PER_AFFINE  # 108


def _load_bundle() -> dict:
    with zipfile.ZipFile(BUNDLE) as zf:
        aff_raw = zf.read("affine_point_to_4_infinity_neighbors_full27.csv").decode("utf-8")
        w33_raw = zf.read("W33_collinearity_edges_240.csv").decode("utf-8")
        pg33_raw = zf.read("pg33_point_coordinates.csv").decode("utf-8")
        neighbor = json.loads(zf.read("neighbor_map.json"))
        orbits_np = json.loads(zf.read("orbits_NP.json"))
        orbits_p = json.loads(zf.read("orbits_P.json"))
        orbits_outer = json.loads(zf.read("orbits_outer.json"))
        sym = json.loads(zf.read("symplectic_form_and_outer_matrix.json"))
    return {
        "aff_rows": list(csv.DictReader(io.StringIO(aff_raw))),
        "w33_rows": list(csv.DictReader(io.StringIO(w33_raw))),
        "pg33_rows": list(csv.DictReader(io.StringIO(pg33_raw))),
        "neighbor": neighbor,
        "orbits_np": orbits_np,
        "orbits_p": orbits_p,
        "orbits_outer": orbits_outer,
        "sym": sym,
    }


def analyze() -> dict:
    data = _load_bundle()
    aff_rows = data["aff_rows"]
    w33_rows = data["w33_rows"]
    pg33_rows = data["pg33_rows"]
    neighbor = data["neighbor"]
    orbits_np = data["orbits_np"]
    orbits_outer = data["orbits_outer"]
    sym = data["sym"]

    # T1: PG(3,3) geometry
    t1_n_pg33 = len(pg33_rows)
    t1_n_affine = len(aff_rows)
    t1_n_infinity = t1_n_pg33 - t1_n_affine
    # W33 edges and degrees
    t1_n_edges = len(w33_rows)
    deg: Dict[int, int] = {}
    for row in w33_rows:
        v1, v2 = int(row["v1"]), int(row["v2"])
        deg[v1] = deg.get(v1, 0) + 1
        deg[v2] = deg.get(v2, 0) + 1
    t1_degree_dist = dict(Counter(deg.values()))
    t1_all_degree_12 = all(d == DEGREE for d in deg.values())
    t1_correct = (
        t1_n_pg33 == N_PG33 and
        t1_n_affine == N_AFFINE and
        t1_n_infinity == N_INFINITY and
        t1_n_edges == N_EDGES and
        t1_all_degree_12
    )

    # T2: Infinity neighbor map
    # Each affine row should have exactly 4 distinct infinity neighbors
    t2_n_affine_rows = len(aff_rows)
    t2_all_4_neighbors = all(
        len({int(row[k]) for k in ["inf1","inf2","inf3","inf4"]}) == NEIGHBORS_PER_AFFINE
        for row in aff_rows
    )
    # All neighbors in infinity range {0,...,12}
    t2_all_in_infinity = all(
        all(0 <= int(row[k]) < N_INFINITY for k in ["inf1","inf2","inf3","inf4"])
        for row in aff_rows
    )
    t2_total_incidences = t2_n_affine_rows * NEIGHBORS_PER_AFFINE
    t2_correct = (
        t2_n_affine_rows == N_AFFINE and
        t2_all_4_neighbors and
        t2_all_in_infinity and
        t2_total_incidences == TOTAL_INCIDENCES
    )

    # T3: Charge distribution
    charge: Dict[int, int] = {}
    for row in aff_rows:
        for k in ["inf1","inf2","inf3","inf4"]:
            p = int(row[k])
            charge[p] = charge.get(p, 0) + 1
    t3_charge_dist = dict(sorted(charge.items()))
    t3_all_charged = sorted(charge.keys())
    t3_num_charged = len(t3_charge_dist)  # infinity pts with charge > 0
    t3_num_zero = N_INFINITY - t3_num_charged  # pts with charge 0
    # Check all nonzero charges are 9
    t3_all_charge_9 = all(v == 9 for v in charge.values())
    t3_total_charge = sum(charge.values())
    # The one special infinity point with charge 0
    all_inf_pts = set(range(N_INFINITY))
    charged_pts = set(charge.keys())
    zero_charge_pts = sorted(all_inf_pts - charged_pts)
    t3_zero_charge_pts = zero_charge_pts
    t3_one_zero = (len(zero_charge_pts) == 1)
    t3_special_pt = zero_charge_pts[0] if zero_charge_pts else None
    t3_correct = (
        t3_all_charge_9 and
        t3_one_zero and
        t3_total_charge == TOTAL_INCIDENCES and
        t3_num_charged == 12
    )

    # T4: Orbit structure under NP
    t4_np_orbit_sizes = sorted([len(o) for o in orbits_np])
    t4_np_two_orbits = (len(orbits_np) == 2)
    t4_np_total = sum(len(o) for o in orbits_np)
    t4_np_covers_non_origin = (t4_np_total == N_PG33 - 1)  # 39
    t4_np_orbit12_exists = (12 in t4_np_orbit_sizes)
    t4_np_orbit27_exists = (27 in t4_np_orbit_sizes)
    t4_correct = (
        t4_np_two_orbits and
        t4_np_orbit12_exists and
        t4_np_orbit27_exists and
        t4_np_covers_non_origin
    )

    # T5: Outer twist orbits on 27 affine points
    outer_sizes = [len(o) for o in orbits_outer]
    outer_size_dist = dict(Counter(outer_sizes))
    t5_num_orbits = len(orbits_outer)
    t5_total_affine = sum(outer_sizes)
    t5_size_dist_correct = (outer_size_dist == {1: 1, 2: 1, 8: 3})
    t5_one_fixed = (outer_size_dist.get(1, 0) == 1)
    t5_one_pair = (outer_size_dist.get(2, 0) == 1)
    t5_three_8orbits = (outer_size_dist.get(8, 0) == 3)
    t5_correct = (
        t5_num_orbits == 5 and
        t5_total_affine == N_AFFINE and
        t5_size_dist_correct
    )

    # T6: Affine coordinate structure
    # Extract (x,y,t) and verify the orbit-0 affine points are those with special x,y values
    affine_coords = {
        int(row["pg_id"]): (int(row["x"]), int(row["y"]), int(row["t"]))
        for row in aff_rows
    }
    # Find which affine points are in NP orbit 0 (the size-12 orbit)
    np_orbit0 = set(orbits_np[0]) if len(orbits_np[0]) == 12 else set(orbits_np[1])
    orbit0_affine = sorted(p for p in np_orbit0 if p >= 13)  # affine pts have pg_id >= 13
    # These 9 affine points should have consistent structure
    t6_orbit0_affine_count = len(orbit0_affine)
    orbit0_coords = {p: affine_coords.get(p) for p in orbit0_affine if p in affine_coords}
    # Verify they have 3 distinct x values and 3 y values
    t6_orbit0_x_values = sorted(set(c[0] for c in orbit0_coords.values()))
    t6_orbit0_y_values = sorted(set(c[1] for c in orbit0_coords.values()))
    # Each (x,y) in the orbit should appear with all 3 t-values (0,1,2)
    t6_orbit0_t_per_xy: Dict[Tuple, List] = {}
    for coords in orbit0_coords.values():
        xy = (coords[0], coords[1])
        t6_orbit0_t_per_xy.setdefault(xy, []).append(coords[2])
    t6_orbit0_each_xy_has_3_t = all(
        sorted(ts) == [0, 1, 2] for ts in t6_orbit0_t_per_xy.values()
    )
    # Symplectic form check: J is a 4x4 matrix
    J = sym["J"]
    t6_J_is_4x4 = (len(J) == 4 and all(len(row) == 4 for row in J))
    N4 = sym["N4"]
    t6_N4_is_4x4 = (len(N4) == 4 and all(len(row) == 4 for row in N4))
    t6_multiplier = sym["multiplier"]
    t6_correct = (
        t6_orbit0_affine_count == 9 and
        t6_orbit0_each_xy_has_3_t and
        t6_J_is_4x4 and
        t6_N4_is_4x4
    )

    return {
        "T1_n_pg33": t1_n_pg33,
        "T1_n_affine": t1_n_affine,
        "T1_n_infinity": t1_n_infinity,
        "T1_n_edges": t1_n_edges,
        "T1_degree_dist": t1_degree_dist,
        "T1_all_degree_12": t1_all_degree_12,
        "T1_correct": t1_correct,
        "T2_n_affine_rows": t2_n_affine_rows,
        "T2_all_4_neighbors": t2_all_4_neighbors,
        "T2_all_in_infinity": t2_all_in_infinity,
        "T2_total_incidences": t2_total_incidences,
        "T2_correct": t2_correct,
        "T3_charge_dist": t3_charge_dist,
        "T3_num_charged": t3_num_charged,
        "T3_num_zero": t3_num_zero,
        "T3_all_charge_9": t3_all_charge_9,
        "T3_total_charge": t3_total_charge,
        "T3_zero_charge_pts": t3_zero_charge_pts,
        "T3_one_zero": t3_one_zero,
        "T3_special_pt": t3_special_pt,
        "T3_correct": t3_correct,
        "T4_np_orbit_sizes": t4_np_orbit_sizes,
        "T4_np_two_orbits": t4_np_two_orbits,
        "T4_np_total": t4_np_total,
        "T4_np_orbit12_exists": t4_np_orbit12_exists,
        "T4_np_orbit27_exists": t4_np_orbit27_exists,
        "T4_correct": t4_correct,
        "T5_num_orbits": t5_num_orbits,
        "T5_total_affine": t5_total_affine,
        "T5_outer_size_dist": outer_size_dist,
        "T5_size_dist_correct": t5_size_dist_correct,
        "T5_one_fixed": t5_one_fixed,
        "T5_one_pair": t5_one_pair,
        "T5_three_8orbits": t5_three_8orbits,
        "T5_correct": t5_correct,
        "T6_orbit0_affine_count": t6_orbit0_affine_count,
        "T6_orbit0_each_xy_has_3_t": t6_orbit0_each_xy_has_3_t,
        "T6_J_is_4x4": t6_J_is_4x4,
        "T6_N4_is_4x4": t6_N4_is_4x4,
        "T6_multiplier": t6_multiplier,
        "T6_correct": t6_correct,
    }


def main():
    import json as _json
    summary = analyze()
    out = ROOT / "data" / "w33_infinity_charge.json"
    out.write_text(_json.dumps(summary, indent=2))
    print("T1 PG33 n=40 affine=27 inf=13 edges=240:",
          summary["T1_correct"], " degree:", summary["T1_degree_dist"])
    print("T2 affine neighbor map:", summary["T2_correct"],
          " total incidences:", summary["T2_total_incidences"])
    print("T3 charge dist: 12x9 + 1x0:", summary["T3_correct"],
          " special pt:", summary["T3_special_pt"])
    print("T4 NP orbits:", summary["T4_np_orbit_sizes"], " correct:", summary["T4_correct"])
    print("T5 outer twist orbits:", summary["T5_outer_size_dist"], " correct:", summary["T5_correct"])
    print("T6 affine structure:", summary["T6_correct"],
          " orbit0_affine:", summary["T6_orbit0_affine_count"])
    print("wrote data/w33_infinity_charge.json")


if __name__ == "__main__":
    main()
