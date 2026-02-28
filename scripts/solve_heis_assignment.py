#!/usr/bin/env python3
"""Find an assignment of a single qid to each spa block satisfying
central translation under t^4.

Each spa block has two candidate qids (the two pockets in the block).
Let b4 = t^4(b). We require
    coords[qid(b4)] - coords[qid(b)] == (0,0,1) mod 3

For fixed blocks (b4==b) this forces swapping the two qids with the
correct orientation.

We perform a simple DFS over spa blocks, propagating choices along
t4-cycles.  The set of spa blocks is small (24) so brute force search
is fast.

Output: JSON mapping block->chosen qid (and coords), written to
`block_heis_assign.json`.
"""
import json, zipfile, csv, os

# load spa blocks and qid sets from the existing bridge report
report = json.load(open('data/w33_triality_bridge.json'))
block_qids = {int(k): set(v) for k, v in report['T4b_block_qids'].items()}
spa_blocks = sorted(block_qids.keys())

# load coordinates for qids
with zipfile.ZipFile('TOE_K27_HEISENBERG_S3_v01_20260228_bundle.zip') as zf:
    coords_csv = zf.read('TOE_K27_HEISENBERG_S3_v01_20260228/K27_heisenberg_coords.csv').decode()
qid2coords = {int(r['qid']): (int(r['x']), int(r['y']), int(r['z']))
               for r in csv.DictReader(coords_csv.splitlines())}

# compute t4 mapping on blocks
bundle = 'TOE_block_twist_v02/TOE_tomotope_axis_block_twist_v02_20260228'
blocks = json.load(open(os.path.join(bundle, 'blocks48_r0r3.json')))['orbits']
tr = json.load(open(os.path.join(bundle, 'tomotope_r_generators_in_axis_coords.json')))
r1, r2 = tr['r1'], tr['r2']

n = 192

def compose(p, q): return tuple(p[q[i]] for i in range(n))

# build t^4
p = tuple(range(n))
t = compose(r1, r2)
for _ in range(4):
    p = compose(t, p)
t4 = p

flag2block = {fid: bi for bi, blk in enumerate(blocks) for fid in blk}
block_t4 = {}
for b in range(len(blocks)):
    f = blocks[b][0]
    block_t4[b] = flag2block[t4[f]]

# function to test difference equals central element
CENTRAL = (0, 0, 1)

def diff(a, b):
    return tuple((a[i] - b[i]) % 3 for i in range(3))

# backtracking search
assignment = {}
stack = []
# order spa blocks by cycle structure (fixed first for convenience)
visited = set()
order = []
for b in spa_blocks:
    if b not in visited:
        cyc = []
        cur = b
        while cur not in visited:
            visited.add(cur)
            cyc.append(cur)
            cur = block_t4[cur]
        order.extend(cyc)

# recursive DFS
success = False

def dfs(idx):
    global success
    if idx == len(order):
        success = True
        return
    b = order[idx]
    # candidates are qids in block_qids[b]
    for q in block_qids[b]:
        # if already assigned, skip if mismatch
        if b in assignment and assignment[b] != q:
            continue
        # tentative assign
        assignment[b] = q
        # propagate to b4 if possible
        b4 = block_t4[b]
        if b4 in spa_blocks:
            # compute required qid for b4
            coords_b = qid2coords[q]
            desired = None
            for q4 in block_qids[b4]:
                if diff(qid2coords[q4], coords_b) == CENTRAL:
                    desired = q4
                    break
            if desired is None:
                del assignment[b]
                continue
            if b4 in assignment and assignment[b4] != desired:
                del assignment[b]
                continue
            assignment[b4] = desired
        dfs(idx + 1)
        if success:
            return
        # undo assignments made by this step
        if b4 in assignment and assignment[b4] == desired:
            del assignment[b4]
        if b in assignment:
            del assignment[b]

# kickoff
for start in order:
    dfs(0)
    if success:
        break

if not success:
    raise RuntimeError("No valid assignment found")

# write out
with open('block_heis_assign.json', 'w') as f:
    json.dump({str(b): {'qid': assignment[b], 'coords': qid2coords[assignment[b]]}
               for b in sorted(assignment)}, f, indent=2)
print('wrote block_heis_assign.json with', len(assignment), 'entries')
