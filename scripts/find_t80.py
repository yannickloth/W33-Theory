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
for idx,sol in enumerate(sols):
    r=[tuple(sol[i]) for i in range(4)]
    t=compose(r[3],compose(r[2],compose(r[1],r[0])))
    o=order(t)
    if o==80 or o==8:
        print('index',idx,'order',o)
