#!/usr/bin/env python3
"""Search for qid assignment on spa=0 flags satisfying central translation.

We restrict attention to the five blocks supporting translation (4,5,6,7,46)
and their flags.  Each flag may belong to several pockets; we can choose which
pocket's qid to assign.  Try all possibilities via DFS.
"""
import json,zipfile,csv,os

# spa values
spa=json.load(open('spa_triality_summary.json'))['spa']
# blocks
bundle='TOE_block_twist_v02/TOE_tomotope_axis_block_twist_v02_20260228'
blocks=json.load(open(os.path.join(bundle,'blocks48_r0r3.json')))['orbits']
tr=json.load(open(os.path.join(bundle,'tomotope_r_generators_in_axis_coords.json')))
r1,r2=tr['r1'],tr['r2']
n=192

def compose(p,q): return tuple(p[q[i]] for i in range(n))
t=compose(r1,r2)
p=tuple(range(n))
for _ in range(4): p=compose(t,p)
t4=p
flag2block={fid:bi for bi,blk in enumerate(blocks) for fid in blk}

# spa0 blocks of interest
spa0_blocks=[4,5,6,7,46]
spa0_flags=[]
for b in spa0_blocks:
    spa0_flags.extend(blocks[b])
spa0_flags=sorted(set(spa0_flags))

# load pocket geometry
pg=json.load(open('pocket_geometry.json'))
pockets=pg['pockets']
# pocket -> qid
with zipfile.ZipFile('TOE_K27_HEISENBERG_S3_v01_20260228_bundle.zip') as zf:
    twin_csv=zf.read('TOE_K27_HEISENBERG_S3_v01_20260228/K54_to_K27_twin_map.csv').decode()
    pocket_to_qid={int(r['pocket_id']):int(r['qid']) for r in csv.DictReader(twin_csv.splitlines())}

# build flag -> candidate qids
flag2qids={}
for f in spa0_flags:
    qs=set()
    for pid,pk in enumerate(pockets):
        if f in pk and pid in pocket_to_qid:
            qs.add(pocket_to_qid[pid])
    if qs:
        flag2qids[f]=list(qs)
    else:
        flag2qids[f]=[]

# heis coords
with zipfile.ZipFile('TOE_K27_HEISENBERG_S3_v01_20260228_bundle.zip') as zf:
    coords_csv=zf.read('TOE_K27_HEISENBERG_S3_v01_20260228/K27_heisenberg_coords.csv').decode()
qid2coords={int(r['qid']):(int(r['x']),int(r['y']),int(r['z'])) for r in csv.DictReader(coords_csv.splitlines())}

CENTRAL=(0,0,1)
def diff(a,b): return tuple((a[i]-b[i])%3 for i in range(3))

# order flags
flags=spa0_flags
assignment={}
found=False

# sort flags by number of candidates ascending
flags.sort(key=lambda f: len(flag2qids.get(f,[])))


def dfs(idx):
    global found
    if idx==len(flags):
        found=True
        return
    f=flags[idx]
    for q in flag2qids.get(f,[]):
        # assign
        assignment[f]=q
        # check consistency for any previous neighbour f_prev with t4 link
        ok=True
        for g in flags[:idx]:
            if t4[g]==f or t4[f]==g:
                qg=assignment[g]
                qe=assignment[f]
                # require translation if both assigned
                if diff(qid2coords[qe], qid2coords[qg])!=CENTRAL:
                    ok=False
                    break
        if not ok:
            del assignment[f]
            continue
        dfs(idx+1)
        if found: return
        del assignment[f]

dfs(0)
if not found:
    print('no assignment found')
else:
    print('assignment found for',len(assignment),'flags')
    json.dump({str(f):assignment[f] for f in assignment}, open('spa0_flag_qids.json','w'), indent=2)
    print('wrote spa0_flag_qids.json')
