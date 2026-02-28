#!/usr/bin/env python3
import json
from collections import Counter

# load H elements
hdata=json.load(open('axis_line_stabilizer_192.json'))
elems=hdata['elements']
# load pi mapping
pi=tuple(json.load(open('pi_mapping.json')))

# each flag index corresponds to H element by stab_index? maybe mapping earlier used flag index sorted by stab_index
# in tomotope_flag_model_192.json ordering they sorted by stab_index as well
# assume flag index == position in elems sorted by stab_index
ordered=sorted(elems, key=lambda h: h['stab_index'])
# verify length
assert len(ordered)==192

# make list of perm+sign pairs
ps=[(tuple(h['perm']), tuple(h['signs'])) for h in ordered]

# apply pi to indices
mapped_ps=[ps[pi[i]] for i in range(192)]

# compare original vs mapped to see transformation pattern
counts=Counter()
for orig,mapped in zip(ps,mapped_ps):
    if orig!=mapped:
        counts[(orig,mapped)]+=1

print('number of elements moved',len(counts))
# Too many unique; instead try to detect a global permutation of coordinates

# attempt to see if there is a fixed permutation of the 7 coordinates that takes orig perm->mapped perm and orig sign->mapped sign

def apply_coord_perm(p,perm):
    return tuple(p[perm[i]-1] for i in range(7))

def apply_sign_perm(s,perm):
    return tuple(s[perm[i]-1] for i in range(7))

# try all 7! coordinate permutations to see if one matches majority
import itertools
best=None
for perm in itertools.permutations(range(7)):
    ok=True
    for orig,mapped in zip(ps,mapped_ps):
        newperm=apply_coord_perm(orig[0],perm)
        newsign=apply_sign_perm(orig[1],perm)
        if (newperm,newsign)!=mapped:
            ok=False
            break
    if ok:
        best=perm
        break

print('global coordinate permutation',best)
