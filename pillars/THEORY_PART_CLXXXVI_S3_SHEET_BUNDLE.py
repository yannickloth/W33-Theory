#!/usr/bin/env python3
"""Pillar 78 (Part CLXXXVI): Build the S3-sheet bundle & 9x6 coordinatization

This script packages all of the data underlying the S3-sheet transport law
and produces an explicit 54 \cong 9\times6 coordinatization (silent_vertex x
sheet_state).  The generated zip bundle contains:

  * L_table.json           -- 54 S3 elements giving the sheet label L(u)
  * s_g.json               -- generator constants in S3
  * silent_sheet.json      -- mapping orbit_idx->silent_vertex, sheet_id
  * verify_s3_sheet.py     -- script that recomputes and checks the relation
  * coords_9x6.csv         -- explicit (silent_index,sheet_id) for each index

The bundle is written as
  TOE_S3_SHEET_TRANSPORT_v01_20260228_bundle.zip

Caveat: the sheet labels L(u) constructed in Pillar 76 only use the cyclic
C3 subgroup; the bundle still records them as full S3 permutations to keep the
``sheet_state`` language ready for future generalisations.
"""

from __future__ import annotations

import csv
import io
import json
import zipfile
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPORT_FILE = ROOT / "data" / "w33_S3_sheet_transport.json"
WELD_BUNDLE = ROOT / "TOE_tomotope_triality_weld_v01_20260228_bundle.zip"

BUNDLE_NAME = "TOE_S3_SHEET_TRANSPORT_v01_20260228_bundle.zip"


def load_report():
    with open(REPORT_FILE) as f:
        return json.load(f)


def read_pockets54():
    with zipfile.ZipFile(WELD_BUNDLE) as zf:
        text = zf.read("TOE_tomotope_triality_weld_v01_20260228/K_orbit_pockets_54.csv").decode()
    reader = csv.DictReader(io.StringIO(text))
    rows = list(reader)
    return rows


def build_coords(rows):
    # compute silent_vertex list and sheet ids
    silent_vals = []
    sheet_id = {}
    counts = defaultdict(int)
    for r in rows:
        idx = int(r["orbit_idx"])
        sv = r["silent_vertex"]
        silent_vals.append(sv)
        sheet_id[idx] = counts[sv]
        counts[sv] += 1
    # compress silent values to indices 0..8
    unique_s = sorted(counts.keys(), key=int)
    silent_index = {sv: i for i, sv in enumerate(unique_s)}
    silent_idx_list = [silent_index[sv] for sv in silent_vals]
    # verify each count == 6
    assert all(c == 6 for c in counts.values()), counts
    return silent_vals, silent_idx_list, sheet_id


def write_bundle(report, rows, silent_vals, silent_idx_list, sheet_id):
    # prepare files contents
    L_table = report["L_table_canonical"]
    s_g = report["s_g_minimal"]
    # produce silent_sheet list of dicts
    silent_sheet = []
    for r in rows:
        idx = int(r["orbit_idx"])
        silent_sheet.append({
            "orbit_idx": idx,
            "silent_vertex": r["silent_vertex"],
            "silent_index": silent_index[r["silent_vertex"]],
            "sheet_id": sheet_id[idx],
        })
    # coords csv
    coords_csv = io.StringIO()
    w = csv.writer(coords_csv)
    w.writerow(["orbit_idx", "silent_index", "sheet_id"])
    for i in range(len(rows)):
        w.writerow([i, silent_idx_list[i], sheet_id[i]])

    # verification script
    verify_code = '''#!/usr/bin/env python3
import json, zipfile, csv, io

bundle = '%s'
with zipfile.ZipFile(bundle) as zf:
    L = json.loads(zf.read('L_table.json'))
    s_g = json.loads(zf.read('s_g.json'))
    rows = list(csv.DictReader(io.StringIO(zf.read('coords_9x6.csv').decode())))
    # sanity
    assert len(L) == 54

    # rebuild relation from weld data
    with zipfile.ZipFile('%s') as wz:
        text = wz.read('TOE_tomotope_triality_weld_v01_20260228/K_schreier_edges_voltage_Z3.csv').decode()
    reader = csv.DictReader(io.StringIO(text))
    edges = [(int(r['u']), int(r['v']), r['gen'], int(r['cocycle_Z3_exp'])) for r in reader]

    # S3 helpers
    def comp(p, q):
        return tuple(p[q[i]] for i in range(3))
    def perm_inv(p):
        inv = [0] * 3
        for i, j in enumerate(p):
            inv[j] = i
        return tuple(inv)
    c = (1, 2, 0)
    c2 = (2, 0, 1)
    idn = (0, 1, 2)
    c_pow = {0: idn, 1: c, 2: c2}

    ok = 0
    fail = 0
    for u, v, g, e in edges:
        exp = comp(s_g[g], comp(tuple(L[u]), c_pow[e]))
        if tuple(L[v]) == exp:
            ok += 1
        else:
            fail += 1
    print('edge check', ok, '/', ok + fail, 'errors', fail)
''' % (BUNDLE_NAME, WELD_BUNDLE)

    # write zip
    with zipfile.ZipFile(BUNDLE_NAME, 'w') as ob:
        ob.writestr('L_table.json', json.dumps(L_table))
        ob.writestr('s_g.json', json.dumps(s_g))
        ob.writestr('silent_sheet.json', json.dumps(silent_sheet))
        ob.writestr('coords_9x6.csv', coords_csv.getvalue())
        ob.writestr('verify_s3_sheet.py', verify_code)

    print('wrote bundle', BUNDLE_NAME)



def main():
    report = load_report()
    rows = read_pockets54()
    silent_vals, silent_idx_list, sheet_id = build_coords(rows)
    # compute silent_index mapping
    global silent_index
    unique_s = sorted(set(silent_vals), key=int)
    silent_index = {sv: i for i, sv in enumerate(unique_s)}
    # now write bundle
    write_bundle(report, rows, silent_vals, silent_idx_list, sheet_id)

if __name__=='__main__':
    main()
