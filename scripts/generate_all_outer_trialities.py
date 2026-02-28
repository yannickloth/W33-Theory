#!/usr/bin/env python3
"""Attempt to build conjugators implementing each of the six outer
triality automorphisms of W(D4).  We allow fixing one generator and
matching r3_tomo to any axis generator; the fixed generator can vary.
"""

import json

# helpers

def compose(p,q): return tuple(p[i] for i in q)
def inv(p):
    out=[0]*len(p)
    for i,a in enumerate(p): out[a]=i
    return tuple(out)

# load axis and tomotope generators
axis_adj=json.load(open('TOE_tomotope_flag_model_conjugacy_v01_20260228_bundle/TOE_tomotope_flag_model_conjugacy_v01_20260228/flag_adjacency_r0_r3_permutations.json'))
axis_r=[tuple(axis_adj[f'r{i}']) for i in range(4)]
with __import__('zipfile').ZipFile('TOE_tomotope_true_flag_model_v02_20260228_bundle.zip') as zf:
    tomo_adj=json.loads(zf.read('tomotope_r_generators_192.json'))
    tomo_r=[tuple(tomo_adj[f'r{i}']) for i in range(4)]

# build mapping function parameterized by fixed index

def build_pi_fixed(fixed_idx, target_idx):
    """Fix generator r_fixed = axis_r[fixed_idx];
    find pi commuting with r_fixed and sending tomo_r[3]->axis_r[target_idx]."""
    r_fixed = axis_r[fixed_idx]
    r3_tomo = tomo_r[3]
    r3_axis = axis_r[target_idx]
    n=192
    # compute r_fixed pairs
    seen=[False]*n
    pairs=[]
    flag2pair=[None]*n
    for i in range(n):
        if not seen[i]:
            j = r_fixed[i]
            a,b = sorted((i,j))
            pid=len(pairs)
            pairs.append((a,b))
            flag2pair[a]=flag2pair[b]=pid
            seen[a]=seen[b]=True
    # build matching on pairs for r3
    def match(r3):
        m={}
        for pid,(a,b) in enumerate(pairs):
            y = r3[a]
            qid = flag2pair[y]
            m[pid]=qid
        for k,v in m.items():
            if m[v]!=k or k==v:
                raise RuntimeError('involution check failed')
        edges=set()
        for k,v in m.items():
            if k<v: edges.add((k,v))
        return sorted(edges)
    E_t = match(r3_tomo)
    E_a = match(r3_axis)
    if len(E_t)!=len(E_a):
        raise RuntimeError('edge count mismatch')
    # map edges by sorted order
    edge_map = dict(zip(E_t, E_a))
    pi=[-1]*n
    # now assign by block similarly as before
    for (p,q) in E_t:
        P,Q=edge_map[(p,q)]
        seed_t = pairs[p][0]
        seed_a = pairs[P][0]
        # build block under r_fixed and corresponding axis r3?
        # we use both r_fixed and r3_tomo/axis to orbit
        def block(r3,seed):
            orb=set(); stack=[seed]
            while stack:
                x=stack.pop()
                if x in orb: continue
                orb.add(x)
                for g in (r_fixed,r3):
                    y=g[x]
                    if y not in orb: stack.append(y)
            return sorted(orb)
        bloc_t = block(r3_tomo, seed_t)
        bloc_a = block(r3_axis, seed_a)
        if len(bloc_t)!=len(bloc_a):
            raise RuntimeError('block size mismatch')
        # choose mapping via similiar procedure as before
        mapping={}
        for xt in bloc_t:
            found=False
            for a_bit in (0,1):
                for b_bit in (0,1):
                    u=seed_t
                    if b_bit: u = r3_tomo[u]
                    if a_bit: u = r_fixed[u]
                    if u==xt:
                        xa=seed_a
                        if b_bit: xa = r3_axis[xa]
                        if a_bit: xa = r_fixed[xa]
                        mapping[xt]=xa
                        found=True
                        break
                if found: break
            if not found:
                raise RuntimeError('cannot map element in block')
        for xt,xa in mapping.items():
            if pi[xt]!=-1 and pi[xt]!=xa:
                raise RuntimeError('pi conflict')
            pi[xt]=xa
    if any(v==-1 for v in pi):
        raise RuntimeError('pi incomplete')
    return tuple(pi)

# attempt all fixed, target combinations
dataset={}
for fixed in range(4):
    for target in range(4):
        try:
            pival=build_pi_fixed(fixed,target)
        except Exception as e:
            print(f'fixed {fixed} target {target} failed: {e}')
            continue
        print(f'fixed {fixed} target {target} succeeded')
        transported=[compose(pival, compose(tomo_r[i], inv(pival))) for i in range(4)]
        dataset[(fixed,target)] = {'pi':pival,'trans':transported}

json.dump({str(k):list(v['pi']) for k,v in dataset.items()}, open('all_triality_pi.json','w'), indent=2)
json.dump({str(k):{f'r{i}':list(v['trans'][i]) for i in range(4)} for k,v in dataset.items()}, open('all_triality_transported.json','w'), indent=2)
print('done, dataset keys',dataset.keys())
