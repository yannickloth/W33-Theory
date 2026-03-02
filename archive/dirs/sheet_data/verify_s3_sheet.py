#!/usr/bin/env python3
import json, zipfile, csv, io

bundle = 'TOE_S3_SHEET_TRANSPORT_v01_20260228_bundle.zip'
with zipfile.ZipFile(bundle) as zf:
    L = json.loads(zf.read('L_table.json'))
    s_g = json.loads(zf.read('s_g.json'))
    rows = list(csv.DictReader(io.StringIO(zf.read('coords_9x6.csv').decode())))
    # sanity
    assert len(L) == 54

    # rebuild relation from weld data
    with zipfile.ZipFile('C:\Repos\Theory of Everything\TOE_tomotope_triality_weld_v01_20260228_bundle.zip') as wz:
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
