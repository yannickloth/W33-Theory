#!/usr/bin/env python3
import json, numpy as np
from collections import Counter
from itertools import combinations

def main():
    A=np.load("e6pair_srg_adj_36x36.npy")
    n=A.shape[0]
    assert n==36
    deg=A.sum(axis=1)
    assert set(deg)=={20}

    # SRG parameters
    lam=Counter(); mu=Counter()
    for i in range(n):
        for j in range(i+1,n):
            cn=int((A[i]*A[j]).sum())
            if A[i,j]==1:
                lam[cn]+=1
            else:
                mu[cn]+=1
    assert list(lam.keys())==[10]
    assert list(mu.keys())==[12]

    blocks=json.load(open("triangle_decomposition_120_blocks.json"))["blocks"]
    # Check triangle decomposition partitions edges
    edges=set()
    for b in blocks:
        for i,j in combinations(sorted(b),2):
            edges.add((i,j))
            assert A[i,j]==1
    # SRG has 360 edges
    assert len(edges)==360
    print("OK: SRG(36,20,10,12) with 120-triangle edge partition verified.")

if __name__=="__main__":
    main()
