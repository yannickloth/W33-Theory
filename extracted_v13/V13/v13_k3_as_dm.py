#!/usr/bin/env python3
"""
V13: Verify closed form for firewall-filtered Jacobiator K3 as coboundary of deleted cochain m.

Given:
- e8_structure_constants_w33_discrete.json (full bracket)
- e8_g1g1_couplings_cubic_firewall.json (marks forbidden pairs and removed single-term outputs)

Define:
- m(i,j): removed single-term for each forbidden g1×g1 pair
- filtered bracket [ , ]' = [ , ] - m

Then for g1 triples, Jacobiator of filtered bracket equals:
K3 = Part1 + Part2 + Part3 as in V13_REPORT.md

This script recomputes and confirms exact equality on all g1 triples.
"""
import json
from collections import defaultdict, Counter
from pathlib import Path

def load_json(p): return json.loads(Path(p).read_text(encoding="utf-8"))

def main(root):
    root = Path(root)
    art = root/"W33-Theory-master"/"artifacts"
    meta = load_json(art/"e8_root_metadata_table.json")
    rows = meta["rows"]
    sc = load_json(art/"e8_structure_constants_w33_discrete.json")
    cartan_dim = int(sc["basis"]["cartan_dim"])
    br_raw = sc["brackets"]
    br_full = {}
    for kk,lst in br_raw.items():
        i,j = (int(x) for x in kk.split(","))
        br_full[(i,j)] = tuple((int(k), int(c)) for k,c in lst)

    cpl = load_json(art/"e8_g1g1_couplings_cubic_firewall.json")
    bad = [x for x in cpl["couplings"] if x.get("firewall_forbidden")]
    m_map={}
    for e in bad:
        a=int(e["in"][0]["basis"]); b=int(e["in"][1]["basis"])
        out=int(e["out"]["basis"]); coeff=int(e["out"]["coeff"])
        if a>b: a,b=b,a; coeff=-coeff
        m_map[(a,b)] = (out, coeff)

    cache_full={}
    def bracket_basis(i,j):
        if i==j: return ()
        ck=(i,j)
        if ck in cache_full: return cache_full[ck]
        if i<j: key=(i,j); sgn=1
        else: key=(j,i); sgn=-1
        if key not in br_full or not br_full[key]:
            out=()
        else:
            out=tuple((k, sgn*c) for k,c in br_full[key])
        cache_full[ck]=out
        return out

    def m_vec(i,j):
        if i==j: return {}
        if i<j: key=(i,j); sgn=1
        else: key=(j,i); sgn=-1
        if key not in m_map: return {}
        outk,coeff=m_map[key]
        return {outk: sgn*coeff}

    def vec_add(acc, vec, sgn=1):
        for k,v in vec.items():
            acc[k]=acc.get(k,0)+sgn*v
            if acc[k]==0: acc.pop(k,None)

    def bracket_vec_with_basis(vec_terms, j):
        out={}
        for i,ci in vec_terms:
            pij=bracket_basis(i,j)
            for k,c in pij:
                out[k]=out.get(k,0)+ci*c
                if out[k]==0: out.pop(k,None)
        return out

    def K3_filtered(a,b,c):
        # compute from filtered bracket by removing m term in each pair
        def bracket_filt(i,j):
            out=list(bracket_basis(i,j))
            if i<j: key=(i,j); sgn=1
            else: key=(j,i); sgn=-1
            if key in m_map:
                outk, coeff = m_map[key]
                coeff_oriented = sgn*coeff
                out=[(k,v) for k,v in out if not (k==outk and v==coeff_oriented)]
            return tuple(out)
        def bracket_vec(vec_terms,j):
            out={}
            for i,ci in vec_terms:
                pij=bracket_filt(i,j)
                for k,c0 in pij:
                    out[k]=out.get(k,0)+ci*c0
                    if out[k]==0: out.pop(k,None)
            return out
        ab=bracket_filt(a,b); bc=bracket_filt(b,c); ca=bracket_filt(c,a)
        t1=bracket_vec(ab,c) if ab else {}
        t2=bracket_vec(bc,a) if bc else {}
        t3=bracket_vec(ca,b) if ca else {}
        out={}
        for t in (t1,t2,t3):
            vec_add(out,t,sgn=1)
        return out

    def jacobi_from_m(a,b,c):
        out={}
        # Part1
        for (x,y,z) in ((a,b,c),(b,c,a),(c,a,b)):
            mv=m_vec(x,y)
            if mv:
                bt=bracket_vec_with_basis(tuple(mv.items()), z)
                vec_add(out, bt, sgn=-1)
        # Part2
        for (x,y,z) in ((a,b,c),(b,c,a),(c,a,b)):
            xy=bracket_basis(x,y)
            if not xy: 
                continue
            acc={}
            for u,cu in xy:
                mv=m_vec(u,z)
                if mv:
                    for k,v in mv.items():
                        acc[k]=acc.get(k,0)+cu*v
                        if acc[k]==0: acc.pop(k,None)
            vec_add(out, acc, sgn=-1)
        # Part3
        for (x,y,z) in ((a,b,c),(b,c,a),(c,a,b)):
            mv=m_vec(x,y)
            if mv:
                for u,cu in mv.items():
                    m2=m_vec(u,z)
                    if m2:
                        for k,v in m2.items():
                            out[k]=out.get(k,0)+cu*v
                            if out[k]==0: out.pop(k,None)
        return out

    g1=[cartan_dim+ri for ri,r in enumerate(rows) if r.get("grade")=="g1"]
    g1=sorted(g1)
    stats=Counter()
    for ia,a in enumerate(g1):
        for ib,b in enumerate(g1[ia+1:], start=ia+1):
            for c in g1[ib+1:]:
                k3=K3_filtered(a,b,c)
                if not k3:
                    stats["zero"]+=1
                    continue
                stats["nonzero"]+=1
                pred=jacobi_from_m(a,b,c)
                if pred==k3: stats["match"]+=1
                else: stats["mismatch"]+=1
    print("Stats:", dict(stats))

if __name__ == "__main__":
    import sys
    main(sys.argv[1] if len(sys.argv)>1 else ".")
