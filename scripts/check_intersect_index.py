#!/usr/bin/env python3
import json

solutions=json.load(open('unrestricted_solutions.json'))['solutions']
idx=457
sol=solutions[idx]

from collections import deque

def closure(gen_list):
    G={tuple(range(48))}
    changed=True
    while changed:
        changed=False
        for g in list(G):
            for h in gen_list:
                comp=tuple(h[g[i]] for i in range(48))
                if comp not in G:
                    G.add(comp); changed=True
    return G

r=[tuple(sol[i]) for i in range(4)]
A=closure(r[0:3])
B=closure(r[1:4])
print('intersection size',len(A&B))
