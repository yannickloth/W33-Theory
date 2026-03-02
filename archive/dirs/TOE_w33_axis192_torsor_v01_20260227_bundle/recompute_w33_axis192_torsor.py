#!/usr/bin/env python3
"""
Recompute: W33 axis-fixed 192 torsor aligned to Wilmot stabilizer.

Assumes the following zip bundles exist (default paths):
  /mnt/data/TOE_holonomy_Z2_flatZ3_v01_20260227_bundle.zip
  /mnt/data/TOE_pocket_transport_glue_orbit480_v01_20260227_bundle.zip

Outputs (in current working directory):
  SUMMARY.json
  local_table_encodings.json
  embeddings_enc0_1344.csv
  embeddings_enc1_1344.csv
  axis_fixed_enc0_192.csv
  axis_fixed_enc1_192.csv
  axis_line_stabilizer_192.json
  torsor_enc0_axis7_192.json
  torsor_enc1_axis7_192.json
"""
from __future__ import annotations
import io, json, csv
import zipfile
from itertools import permutations, product
from collections import Counter
import pandas as pd

TRIPLES_REF = [(1,2,3),(1,4,5),(1,7,6),(2,4,6),(2,5,7),(3,4,7),(3,6,5)]
BASE_POCKET = [0,1,2,14,15,17,27]  # SRG36 vertices
SILENT_LOCAL = 6
AXIS_UNIT = 7

def build_mul_from_triples(triples):
    d={}
    def add(i,j,k):
        d[(i,j)]=(1,k); d[(j,k)]=(1,i); d[(k,i)]=(1,j)
        d[(j,i)]=(-1,k); d[(k,j)]=(-1,i); d[(i,k)]=(-1,j)
    for i,j,k in triples:
        add(i,j,k)
    return d

MUL_REF = build_mul_from_triples(TRIPLES_REF)

def oct_mul(i,j):
    if i==0: return (1,j)
    if j==0: return (1,i)
    if i==j: return (-1,0)
    return MUL_REF[(i,j)]

def canon_table(tab):
    enc=[]
    for i in range(7):
        for j in range(7):
            s,out=tab[i][j]
            enc.append(int(s))
            enc.append(-1 if out is None else int(out))
    return tuple(enc)

def induced_table(phi, bits):
    inv={phi[i]: i for i in range(7)}
    signs=[-1 if b else 1 for b in bits]
    tab=[[None]*7 for _ in range(7)]
    for i in range(7):
        for j in range(7):
            if i==j:
                tab[i][j]=(-1,None)
                continue
            so,k=oct_mul(phi[i],phi[j])
            if k==0:
                tab[i][j]=(signs[i]*signs[j]*so, None)
            else:
                out=inv[k]
                tab[i][j]=(signs[i]*signs[j]*so*signs[out], out)
    return tab

def gf2_solutions(eqs, nvars=7):
    sols=[]
    for bits in product([0,1], repeat=nvars):
        ok=True
        for mask,rhs in eqs:
            s=rhs
            m=mask
            while m:
                lb=m & -m
                j=(lb.bit_length()-1)
                s ^= bits[j]
                m ^= lb
            if s!=0:
                ok=False; break
        if ok: sols.append(bits)
    return sols

def build_oriented_mult36(holonomy_zip_path):
    z=zipfile.ZipFile(holonomy_zip_path,'r')

    edge_bytes = z.read('TOE_holonomy_Z2_flatZ3_v01_20260227/TOE_edge_to_oriented_rootpairs_v01_20227_bundle.zip'.replace('20227','20260227'))
    tri_bytes  = z.read('TOE_holonomy_Z2_flatZ3_v01_20260227/TOE_E6pair_SRG_triangle_decomp_v01_20260227_bundle.zip')

    edge_z = zipfile.ZipFile(io.BytesIO(edge_bytes),'r')
    tri_z  = zipfile.ZipFile(io.BytesIO(tri_bytes),'r')

    edge_map = json.loads(edge_z.read('TOE_edge_to_oriented_rootpairs_v01_20260227/edge_to_oriented_rootpair_triple.json').decode('utf-8'))
    pairs36 = json.loads(tri_z.read('TOE_E6pair_SRG_triangle_decomp_v01_20260227/e6_antipode_pairs_36.json').decode('utf-8'))['pairs']
    pair_to_vertex = {frozenset(p):i for i,p in enumerate(pairs36)}
    w33_lines = json.loads(tri_z.read('TOE_E6pair_SRG_triangle_decomp_v01_20260227/w33_line_to_e6pair_triangles.json').decode('utf-8'))

    # orient all 120 blocks
    def lex_edge_key(e):
        a,b=sorted(e); return f"{a}-{b}"
    block_oriented={}
    for line in w33_lines:
        p0,p1,p2,p3=line['w33_points']
        matchings=[((p0,p1),(p2,p3)),((p0,p2),(p1,p3)),((p0,p3),(p1,p2))]
        for (ea,eb), _tri in zip(matchings, line['triangle_blocks']):
            eA=tuple(sorted(ea)); eB=tuple(sorted(eb))
            key=lex_edge_key(eA if eA<eB else eB)
            root_pairs=edge_map[key]
            verts=[pair_to_vertex[frozenset(rp)] for rp in root_pairs]
            block_oriented[frozenset(verts)]=verts

    # multiplication table on 36
    n=36
    mult=[[None]*n for _ in range(n)]
    for ori in block_oriented.values():
        a,b,c=ori
        mult[a][b]=(1,c); mult[b][c]=(1,a); mult[c][a]=(1,b)
        mult[b][a]=(-1,c); mult[c][b]=(-1,a); mult[a][c]=(-1,b)
    return mult

def main():
    holonomy_zip = '/mnt/data/TOE_holonomy_Z2_flatZ3_v01_20260227_bundle.zip'
    orbit_zip    = '/mnt/data/TOE_pocket_transport_glue_orbit480_v01_20260227_bundle.zip'

    # build SRG36 multiplication
    mult36 = build_oriented_mult36(holonomy_zip)

    # constraints on base pocket
    pocket_set=set(BASE_POCKET)
    idx={g:i for i,g in enumerate(BASE_POCKET)}
    constraints=[]
    for a in BASE_POCKET:
        for b in BASE_POCKET:
            if a==b: continue
            m=mult36[a][b]
            if m is None: continue
            s,c=m
            if c in pocket_set:
                constraints.append((idx[a], idx[b], s, idx[c]))

    def eqs_for_phi(phi):
        eqs=[]
        for x,y,spock,z in constraints:
            so,k=oct_mul(phi[x],phi[y])
            if k==0 or k!=phi[z]:
                return None
            rhs=(1 if so==-1 else 0) ^ (1 if spock==-1 else 0)
            mask=(1<<x)|(1<<y)|(1<<z)
            eqs.append((mask,rhs))
        return eqs

    embeddings=[]
    enc_counts=Counter()
    phi_solutions=0
    for phi in permutations(range(1,8),7):
        eqs=eqs_for_phi(phi)
        if eqs is None: continue
        sols=gf2_solutions(eqs,7)
        if not sols: continue
        phi_solutions += 1
        for bits in sols:
            enc=canon_table(induced_table(phi,bits))
            embeddings.append({'phi':phi,'bits':bits,'enc':enc})
            enc_counts[enc]+=1

    encs=list(enc_counts.keys())
    assert len(encs)==2 and enc_counts[encs[0]]==enc_counts[encs[1]]==1344

    # load stabilizer
    oz = zipfile.ZipFile(orbit_zip,'r')
    stab = json.loads(oz.read('TOE_WELD_480S_v01_20260227/octonion_stabilizer_1344.json').decode('utf-8'))['stabilizer']
    stab_list=[{'perm':tuple(g['perm']), 'signs':tuple(g['signs'])} for g in stab]
    stab_index={ (g['perm'],g['signs']):i for i,g in enumerate(stab_list) }
    H_indices=[i for i,g in enumerate(stab_list) if g['perm'][6]==AXIS_UNIT]
    assert len(H_indices)==192

    def bits_to_signs(bits):
        return tuple(-1 if b else 1 for b in bits)

    def build_torsor(enc):
        E=[e for e in embeddings if e['enc']==enc]
        base=next(e for e in E if e['phi'][SILENT_LOCAL]==AXIS_UNIT)
        phiB,bitsB=base['phi'],base['bits']
        tB=bits_to_signs(bitsB)

        rows=[]
        for e in E:
            phi,bits=e['phi'],e['bits']
            t=bits_to_signs(bits)
            perm=[None]*7
            signs=[None]*7
            for i in range(7):
                src=phiB[i]
                perm[src-1]=phi[i]
                signs[src-1]=t[i]*tB[i]
            idx=stab_index[(tuple(perm),tuple(signs))]
            rows.append((idx,phi,bits,phi[SILENT_LOCAL], (-1 if bits[SILENT_LOCAL] else 1)))
        # axis slice
        axis_rows=[r for r in rows if r[3]==AXIS_UNIT]
        assert len(axis_rows)==192
        axis_idx=set(r[0] for r in axis_rows)
        assert axis_idx==set(H_indices)
        return base, rows, axis_rows

    base0, rows0, axis0 = build_torsor(encs[0])
    base1, rows1, axis1 = build_torsor(encs[1])

    # write outputs
    summary={
        "base_pocket_vertices_36": BASE_POCKET,
        "constraints_count": len(constraints),
        "octonion_reference_triples": TRIPLES_REF,
        "phi_solutions": phi_solutions,
        "embedding_solutions_phi_bits": len(embeddings),
        "unique_local_tables": 2,
        "embeddings_per_table": 1344,
        "axis_fixed_embeddings_per_table": 192,
        "octonion_stabilizer_size": len(stab_list),
        "axis_line_stabilizer_size": len(H_indices),
        "torsor_verified": True,
    }
    json.dump(summary, open('SUMMARY.json','w'), indent=2)

    json.dump({"enc0": list(encs[0]), "enc1": list(encs[1])}, open('local_table_encodings.json','w'), indent=2)

    # write stabilizer H
    H_elems=[{"stab_index":i,"perm":list(stab_list[i]['perm']),"signs":list(stab_list[i]['signs'])} for i in sorted(H_indices)]
    json.dump({"count":len(H_elems),"elements":H_elems}, open('axis_line_stabilizer_192.json','w'), indent=2)

    def rows_to_df(rows):
        data=[]
        for idx,phi,bits,axis,ss in rows:
            row={"stab_index":idx,"axis_unit":axis,"silent_sign":ss}
            for i,u in enumerate(phi): row[f"phi{i}"]=u
            for i,b in enumerate(bits): row[f"bit{i}"]=b
            data.append(row)
        return pd.DataFrame(data)

    rows_to_df(rows0).to_csv('embeddings_enc0_1344.csv', index=False)
    rows_to_df(rows1).to_csv('embeddings_enc1_1344.csv', index=False)

    rows_to_df(axis0).to_csv('axis_fixed_enc0_192.csv', index=False)
    rows_to_df(axis1).to_csv('axis_fixed_enc1_192.csv', index=False)

    def axis_to_torsor(axis_rows, enc_id):
        items=[]
        for idx,phi,bits,axis,ss in sorted(axis_rows, key=lambda r:r[0]):
            items.append({"stab_index":idx,"phi":list(phi),"bits":list(bits),"axis_unit":axis,"silent_sign":ss})
        json.dump({"count":len(items),"enc_id":enc_id,"elements":items}, open(f"torsor_{enc_id}_axis7_192.json","w"), indent=2)

    axis_to_torsor(axis0, "enc0")
    axis_to_torsor(axis1, "enc1")

    print("done", summary)

if __name__ == "__main__":
    main()
