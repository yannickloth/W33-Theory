#!/usr/bin/env python3
"""Pillar 80 (Part CLXXXVIII): 270‑edge quotient transport object

Combine the Heisenberg(27)\u22caC6 affine decomposition from Pillar 77 with
our 9x6 sheet coordinatisation and the axis/tomotope block twist to produce a
fully explicit transport record for each of the 270 directed Schreier edges.

Each row contains

    qid,    -- source twin-pair id (0..26)
    orient_index, -- 0..9 (twin_bit*5 + gen_index)
    gen,    -- generator name
    cocycle_Z3_exp,
    target_qid,-- destination twin-pair

    # Heisenberg coordinates
    x,y,z,       -- source point
    tx,ty,tz,    -- translation vector for this generator
    L11,L12,L21,L22, -- 2x2 stabilizer matrix acting on (x,y)
    s_zshift,    -- z-shift coming from stabilizer

    # sheet & silent data (link to 54-pocket structure)
    silent_index,sheet_id

    # a crude block guess derived from (silent_index,sheet_id)
    block_guess

The produced bundle and CSV are intended as the concrete "quotient
transport" object described in the roadmap: it records how the K action
on 54 pockets descends to an affine action on the 27 qids, together with a
first approximation of a map into the 48 tomotope blocks.
"""

from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PILLAR77 = ROOT / "pillar77_data"
SHEET_DATA = ROOT / "sheet_data"

HEIS_REPORT = PILLAR77 / "data" / "w33_K27_heisenberg.json"
HEIS_COORDS = PILLAR77 / "K27_heisenberg_coords.csv"
EDGES_27X10 = ROOT / "edges_27x10.csv"

OUT_CSV = ROOT / "edges_270_transport.csv"
OUT_JSON = ROOT / "270_transport_table.json"
BUNDLE_NAME = "TOE_270_TRANSPORT_v01_20260228_bundle.zip"

GENS = ["g2", "g3", "g5", "g8", "g9"]
GEN_INDEX = {g: i for i, g in enumerate(GENS)}


def load_heis_report():
    with open(HEIS_REPORT) as f:
        return json.load(f)


def load_heis_coords():
    coords = {}
    with open(HEIS_COORDS) as f:
        r = csv.DictReader(f)
        for row in r:
            q = int(row["qid"])
            coords[q] = (int(row["x"]), int(row["y"]), int(row["z"]))
    return coords


def load_sheet_coords():
    sc = {}
    with open(SHEET_DATA / "coords_9x6.csv") as f:
        r = csv.DictReader(f)
        for row in r:
            sc[int(row["orbit_idx"])] = (
                int(row["silent_index"]), int(row["sheet_id"]),
            )
    return sc


def build_transport():
    heis = load_heis_report()
    coords = load_heis_coords()
    sheet = load_sheet_coords()

    gens_aff = heis["generators_affine"]
    perms27 = heis.get("K_generators_27", {})

    # build reverse mapping coords -> qid
    coords_to_qid = {coords[qid]: qid for qid in coords}

    def inv_perm(p):
        inv = [0] * len(p)
        for i, j in enumerate(p):
            inv[j] = i
        return tuple(inv)

    # compute stabilizer permutation and q_xy mapping for each generator
    stab_data: dict[str, dict] = {}
    for gen, gperm in perms27.items():
        gperm = tuple(gperm)
        tx, ty, tz = gens_aff[gen]["t_xyz"]
        # build translation permutation acting on qids
        tperm = [None] * len(gperm)
        for qid, (x, y, z) in coords.items():
            x1 = (tx + x) % 3
            y1 = (ty + y) % 3
            z1 = (tz + z - ty * x) % 3
            tperm[qid] = coords_to_qid[(x1, y1, z1)]
        tperm = tuple(tperm)
        t_inv = inv_perm(tperm)
        s_perm = tuple(t_inv[gperm[i]] for i in range(len(gperm)))
        # compute q_xy for s_perm
        q_xy = {}
        for x in range(3):
            for y in range(3):
                q0 = coords_to_qid[(x, y, 0)]
                qimg = s_perm[q0]
                q_xy[f"{x},{y}"] = coords[qimg][2]
        stab_data[gen] = {"sperm": s_perm, "q_xy": q_xy}

    rows = []
    table: dict[int, list[dict]] = defaultdict(lambda: [None] * 10)

    with open(EDGES_27X10) as f:
        reader = csv.DictReader(f)
        for r in reader:
            qid = int(r["qid"])
            orient = int(r["orient_index"])
            gen = r["gen"]
            t = gens_aff[gen]
            tx, ty, tz = t["t_xyz"]
            mat = t["s_matrix"]
            L11, L12 = mat[0]
            L21, L22 = mat[1]
            sz = t.get("s_zshift", [0, 0])
            # source heis coords
            x, y, z = coords[qid]
            # sheet data for source
            sv, sh = sheet[qid]
            blk = (sv * 6 + sh) % 48
            q_xy = stab_data.get(gen, {}).get("q_xy", {})

            newrow = {
                **r,
                "x": x,
                "y": y,
                "z": z,
                "tx": tx,
                "ty": ty,
                "tz": tz,
                "L11": L11,
                "L12": L12,
                "L21": L21,
                "L22": L22,
                "s_zshift_x": sz[0] if isinstance(sz, list) else sz,
                "s_zshift_y": sz[1] if isinstance(sz, list) else 0,
                "q_xy": json.dumps(q_xy),
                "silent_index": sv,
                "sheet_id": sh,
                "block_guess": blk,
            }
            rows.append(newrow)
            table[qid][orient] = newrow
    return rows, table


def write_outputs(rows, table):
    with open(OUT_CSV, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    with open(OUT_JSON, "w") as f:
        json.dump(table, f, indent=2)
    # bundle
    import zipfile
    with zipfile.ZipFile(BUNDLE_NAME, "w") as bz:
        bz.write(str(OUT_CSV), arcname="edges_270_transport.csv")
        bz.write(str(OUT_JSON), arcname="270_transport_table.json")
        bz.writestr("README.txt", (
            "270 transport bundle: each directed K edge labelled by Heisenberg\n"
            "affine data and a provisional block guess computed from the 9x6\n"
            "sheet coordinates.  This is the first explicit quotient transport\n"
            "object linking K27 coordinates to tomotope/axis block fibres.\n"
        ))
    print("wrote", OUT_CSV, OUT_JSON, "and bundle", BUNDLE_NAME)


def main():
    rows, table = build_transport()
    # sanity
    assert len(rows) == 270
    for q, lst in table.items():
        assert len(lst) == 10
        assert all(x is not None for x in lst)
    write_outputs(rows, table)


if __name__ == "__main__":
    main()
