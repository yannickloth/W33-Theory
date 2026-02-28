#!/usr/bin/env python3
import json
from math import gcd

def compose(p,q): return tuple(p[i] for i in q)

def order(p):
    n=len(p); used=[False]*n; o=1
    for i in range(n):
        if not used[i]:
            j=i; cnt=0
            while not used[j]: used[j]=True; j=p[j]; cnt+=1
            o=o*cnt//gcd(o,cnt)
    return o

sols=json.load(open('unrestricted_solutions.json'))['solutions']
counts={}
for idx,sol in enumerate(sols):
    r=[tuple(sol[i]) for i in range(4)]
    t=compose(r[3],compose(r[2],compose(r[1],r[0])))
    counts[order(t)] = counts.get(order(t),0)+1
print(counts)

# find indices with order 80
for idx,sol in enumerate(sols):
    r=[tuple(sol[i]) for i in range(4)]
    t=compose(r[3],compose(r[2],compose(r[1],r[0])))
    o=order(t)
    if o==80:
        # compute intersection size
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
        A=closure(r[0:3])
        B=closure(r[1:4])
        print('index',idx,'intersection',len(A&B))
