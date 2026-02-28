#!/usr/bin/env python3
"""Recompute A5 sign-lift orbit signatures on the 480 octonion tables, and
compute the axis-fixed stabilizer subgroup (order 192) and its orbit signature.

Inputs expected in same folder (copy from TOE_WELD_480S_v01_20260227):
  - octonion_orbit_480_tables.json
  - octonion_stabilizer_1344.json

Outputs:
  - octonion_A5_degree6_signlift_groups.json
  - octonion_A5_degree5_signlift_groups.json
  - octonion_axis7_stabilizer_192_summary.json
"""
from __future__ import annotations
import json
import math
from collections import Counter, defaultdict, deque
from itertools import product, permutations

MOD=5

def decode(code:int):
    s=1 if code>0 else -1
    idx=abs(code)-1
    return s,idx
def encode(s:int, idx:int)->int:
    return int(s)*(idx+1)

def transform_key(key64, perm_arr, sign_arr):
    out=[0]*64
    for i in range(8):
        i2 = 0 if i==0 else perm_arr[i]
        si = 1 if i==0 else sign_arr[i]
        row=i*8
        for j in range(8):
            j2 = 0 if j==0 else perm_arr[j]
            sj = 1 if j==0 else sign_arr[j]
            code=key64[row+j]
            s,k=decode(code)
            k2=0 if k==0 else perm_arr[k]
            sk=1 if k==0 else sign_arr[k]
            out[i2*8+j2]=encode(si*sj*s*sk, k2)
    return tuple(out)

def induced_perm(keys, key_to_idx, perm7, signs7):
    perm_arr=[0]+perm7
    sign_arr=[1]+signs7
    out=[0]*len(keys)
    for i,k in enumerate(keys):
        kk=transform_key(k, perm_arr, sign_arr)
        out[i]=key_to_idx[kk]
    return out

def perm_inv(p):
    inv=[0]*len(p)
    for i,j in enumerate(p):
        inv[j]=i
    return inv

def orbit_signature(gens):
    invs=[perm_inv(g) for g in gens]
    steps=gens+invs
    n=len(gens[0])
    seen=[False]*n
    sizes=[]
    for i in range(n):
        if seen[i]: continue
        q=[i]; seen[i]=True; cnt=1
        while q:
            x=q.pop()
            for g in steps:
                y=g[x]
                if not seen[y]:
                    seen[y]=True; q.append(y); cnt+=1
        sizes.append(cnt)
    return Counter(sizes)

def mobius(mat, x):
    a,b,c,d=mat
    if x is None:
        if c%MOD==0: return None
        inv=pow(c,-1,MOD)
        return (a*inv)%MOD
    denom=(c*x+d)%MOD
    if denom==0: return None
    inv=pow(denom,-1,MOD)
    return ((a*x+b)*inv)%MOD

def perm_from_mat(mat):
    points=[None,0,1,2,3,4]
    pt_index={p:i for i,p in enumerate(points)}
    perm=[0]*6
    for i,p in enumerate(points):
        perm[i]=pt_index[mobius(mat,p)]
    return perm

def embed_perm6_to_units(perm6, fixed_unit=7, units_map=None):
    if units_map is None:
        units_map=[1,2,3,4,5,6]
    unit_to_pt={u:i for i,u in enumerate(units_map)}
    perm_arr=[0]*8
    perm_arr[0]=0
    perm_arr[fixed_unit]=fixed_unit
    for u in range(1,8):
        if u==fixed_unit: continue
        pt=unit_to_pt[u]
        perm_arr[u]=units_map[perm6[pt]]
    return perm_arr

def sign_vec(bits):
    sv=[1]*8
    for i in range(1,8):
        sv[i]= -1 if (bits>>(i-1))&1 else 1
    sv[0]=1
    return sv

def compose_signed(p1,s1,p2,s2):
    perm=[0]*8
    sign=[1]*8
    perm[0]=0; sign[0]=1
    for i in range(1,8):
        perm[i]=p1[p2[i]]
        sign[i]=s2[i]*s1[p2[i]]
    return perm, sign

def pow_signed(p,s,k):
    perm=list(range(8)); sign=[1]*8
    bp,bs=p,s
    while k>0:
        if k&1:
            perm,sign=compose_signed(bp,bs,perm,sign)
        bp,bs=compose_signed(bp,bs,bp,bs)
        k//=2
    return perm,sign

def is_identity(p,s):
    return all(p[i]==i for i in range(8)) and all(s[i]==1 for i in range(8))

def main():
    octo=json.load(open("octonion_orbit_480_tables.json","r"))
    stab=json.load(open("octonion_stabilizer_1344.json","r"))
    keys=[tuple(t["key"]) for t in octo["tables"]]
    key_to_idx={k:i for i,k in enumerate(keys)}

    # Degree-6 A5 embedding (PSL2(5) on P1(F5)), fix unit 7
    S_mat=(0,-1,1,0)
    T_mat=(1,1,0,1)
    s6=perm_from_mat(S_mat)
    t6=perm_from_mat(T_mat)
    s_units=embed_perm6_to_units(s6, fixed_unit=7)
    t_units=embed_perm6_to_units(t6, fixed_unit=7)

    valid=[]
    for bs in range(1<<7):
        ss=sign_vec(bs)
        if not is_identity(*compose_signed(s_units,ss,s_units,ss)):
            continue
        for bt in range(1<<7):
            ts=sign_vec(bt)
            if not is_identity(*pow_signed(t_units,ts,5)):
                continue
            stp,sts=compose_signed(s_units,ss,t_units,ts)
            if not is_identity(*pow_signed(stp,sts,3)):
                continue
            valid.append((bs,bt))

    groups=defaultdict(list)
    for bs,bt in valid:
        ss=sign_vec(bs); ts=sign_vec(bt)
        s_map=induced_perm(keys,key_to_idx, s_units[1:], ss[1:])
        t_map=induced_perm(keys,key_to_idx, t_units[1:], ts[1:])
        sig=orbit_signature([s_map,t_map])
        groups[tuple(sorted(sig.items()))].append((bs,bt))

    out=[]
    for key,lst in groups.items():
        out.append({"signature":dict(key),"count":len(lst),"sign_bit_pairs":lst})
    out.sort(key=lambda d:(-d["count"], sorted(d["signature"].items())))
    json.dump({"embedding":"PSL2(5) on 6 points fixing unit 7","num_valid_sign_lifts":len(valid),"groups":out},
              open("octonion_A5_degree6_signlift_groups.json","w"), indent=2)

    # Degree-5 A5 embedding: act on units 1..5, fix 6,7
    # choose generators x=(2 3)(4 5), y=(1 2 4)
    x_units=[0,1,3,2,5,4,6,7]
    y_units=[0,2,4,3,1,5,6,7]

    valid=[]
    for bx in range(1<<7):
        sx=sign_vec(bx)
        if not is_identity(*compose_signed(x_units,sx,x_units,sx)):
            continue
        for by in range(1<<7):
            sy=sign_vec(by)
            if not is_identity(*pow_signed(y_units,sy,3)):
                continue
            xy_p,xy_s=compose_signed(x_units,sx,y_units,sy)
            if not is_identity(*pow_signed(xy_p,xy_s,5)):
                continue
            valid.append((bx,by))

    groups=defaultdict(list)
    for bx,by in valid:
        sx=sign_vec(bx); sy=sign_vec(by)
        x_map=induced_perm(keys,key_to_idx, x_units[1:], sx[1:])
        y_map=induced_perm(keys,key_to_idx, y_units[1:], sy[1:])
        sig=orbit_signature([x_map,y_map])
        groups[tuple(sorted(sig.items()))].append((bx,by))

    out=[]
    for key,lst in groups.items():
        out.append({"signature":dict(key),"count":len(lst),"sign_bit_pairs":lst})
    out.sort(key=lambda d:(-d["count"], sorted(d["signature"].items())))
    json.dump({"embedding":"A5 on units 1..5 fixing 6,7","num_valid_sign_lifts":len(valid),"groups":out},
              open("octonion_A5_degree5_signlift_groups.json","w"), indent=2)

    # Axis-fixed stabilizer (axis=7) inside 1344 stabilizer
    stab_axis=[s for s in stab["stabilizer"] if s["perm"][6]==7]
    assert len(stab_axis)==192

    # greedy small generator set (3)
    all_perms=[induced_perm(keys,key_to_idx, s["perm"], s["signs"]) for s in stab_axis]

    def group_order(perms):
        invs=[perm_inv(p) for p in perms]
        steps=perms+invs
        seen={tuple(range(len(keys)))}; q=[tuple(range(len(keys)))]
        while q:
            h=q.pop()
            for g in steps:
                hg=[g[i] for i in h]
                hg=tuple(hg)
                if hg not in seen:
                    seen.add(hg); q.append(hg)
                    if len(seen)>5000:
                        return None
        return len(seen)

    chosen=[]
    gens=[]
    current=1
    for idx,p in enumerate(all_perms):
        test=group_order(gens+[p])
        if test is not None and test>current:
            gens.append(p); chosen.append(idx); current=test
            if current==192:
                break
    assert current==192 and len(gens)<=4

    sig=orbit_signature(gens)
    json.dump({
        "axis":7,
        "subgroup_order":192,
        "chosen_generator_indices":chosen,
        "chosen_generators_signed_perms":[stab_axis[i] for i in chosen],
        "orbit_signature_on_480_tables":dict(sig)
    }, open("octonion_axis7_stabilizer_192_summary.json","w"), indent=2)

if __name__=="__main__":
    main()
