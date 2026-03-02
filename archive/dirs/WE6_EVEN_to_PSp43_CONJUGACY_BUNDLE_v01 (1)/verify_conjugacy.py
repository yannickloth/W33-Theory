import json, zipfile, os, sys

def to_bytes_perm(perm):
    return bytes(perm)

def compose(p,q):
    return [p[i] for i in q]

def inv_perm(p):
    inv=[0]*len(p)
    for i,pi in enumerate(p):
        inv[pi]=i
    return inv

def conjugate_perm(p, sigma, sigma_inv):
    return [sigma[p[sigma_inv[j]]] for j in range(len(p))]

def gen_group(perms):
    n=len(perms[0])
    idperm=list(range(n))
    seen={to_bytes_perm(idperm): idperm}
    frontier=[idperm]
    while frontier:
        cur=frontier.pop()
        for g in perms:
            nxt=compose(g,cur)
            b=to_bytes_perm(nxt)
            if b not in seen:
                seen[b]=nxt
                frontier.append(nxt)
    return set(seen.keys())

HERE=os.path.dirname(__file__)
with open(os.path.join(HERE,"sigma_we6coset_to_w33line.json"),"r") as f:
    dat=json.load(f)
sigma=dat["sigma_we6coset_to_w33line"]
sigma_inv=dat["sigma_inv_w33line_to_we6coset"]

with open(os.path.join(HERE,"we6coset_generators_10.json"),"r") as f:
    we6=json.load(f)["generators"]
with open(os.path.join(HERE,"psp43_line_generators_6.json"),"r") as f:
    psp=list(json.load(f)["generators"].values())

GB=gen_group(psp)

bad=[]
for k,g in enumerate(we6):
    conj=conjugate_perm(g, sigma, sigma_inv)
    if to_bytes_perm(conj) not in GB:
        bad.append(k)

if bad:
    print("FAILED: some conjugated generators are not in the PSp line group:", bad)
    sys.exit(1)
print("ALL CHECKS PASSED: σ conjugates WE6 coset generators into the PSp(4,3) line normal form group.")
