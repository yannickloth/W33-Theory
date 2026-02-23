import json
from itertools import product

# build W33
def build_W33():
    def omega(v,w):
        return (v[0]*w[1]-v[1]*w[0]+v[2]*w[3]-v[3]*w[2])%3
    def normalize(v):
        for i,x in enumerate(v):
            if x!=0:
                inv=pow(x,-1,3)
                return tuple((inv*c)%3 for c in v)
        return v
    points=[p for p in product(range(3), repeat=4) if p!=(0,0,0,0)]
    vertices=list({normalize(p) for p in points})
    edges=[]
    for i,v in enumerate(vertices):
        for j,w in enumerate(vertices):
            if i<j and omega(v,w)==0:
                edges.append((i,j))
    return vertices, edges

vertices, edges = build_W33()
map_json=json.load(open('data/w33_e8_mapping.json'))
map_arr=[map_json[str(i)] for i in range(len(edges))]

# build roots
roots=[]
for i in range(8):
    for j in range(i+1,8):
        for si in [1,-1]:
            for sj in [1,-1]:
                r=[0]*8; r[i]=si; r[j]=sj; roots.append(tuple(r))
from itertools import product
for signs in product([0.5,-0.5], repeat=8):
    if sum(1 for s in signs if s<0)%2==0:
        roots.append(tuple(signs))
int_type=set(i for i,r in enumerate(roots) if all(float(c).is_integer() for c in r))

# try rule: integer root iff diff vector all even

def lift(v): return tuple(c if c<=1 else c-3 for c in v)

ok=0; total=0
for e,(i,j) in enumerate(edges):
    diff=[lift(vertices[i])[k]-lift(vertices[j])[k] for k in range(4)]
    rule=all(d%2==0 for d in diff)
    actual = map_arr[e] in int_type
    if rule==actual:
        ok+=1
    total+=1
print('rule all-diff-even matches',ok,'of',total)

# try another rule: integer root iff sum(diff) even
ok2=0
for e,(i,j) in enumerate(edges):
    diff=[lift(vertices[i])[k]-lift(vertices[j])[k] for k in range(4)]
    rule=(sum(diff)%2==0)
    actual = map_arr[e] in int_type
    if rule==actual:
        ok2+=1
print('rule sum-diff-even matches',ok2,'of',total)
