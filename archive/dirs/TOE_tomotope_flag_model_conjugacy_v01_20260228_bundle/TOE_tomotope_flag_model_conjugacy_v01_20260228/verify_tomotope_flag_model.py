#!/usr/bin/env python3
import json, sys

def compose(p,q):
    # p∘q, apply q then p
    return [p[i] for i in q]

def inv_perm(p):
    inv=[0]*len(p)
    for i,j in enumerate(p):
        inv[j]=i
    return inv

with open("tomotope_flag_model_192.json","r") as f:
    model=json.load(f)
with open("flag_adjacency_r0_r3_permutations.json","r") as f:
    R=json.load(f)
with open("left_action_perms_for_r0_r3.json","r") as f:
    L=json.load(f)
with open("conjugators.json","r") as f:
    C=json.load(f)

inv=C["inversion_conjugator_left_to_right"]
inv_inv=inv_perm(inv)

n=len(inv)
assert n==192

# Check involutions + commutations
for k in ["r0","r1","r2","r3"]:
    p=R[k]
    for i in range(n):
        assert p[p[i]]==i, f"{k} not involution"

def commutes(p,q):
    return all(p[q[i]]==q[p[i]] for i in range(n))

assert commutes(R["r0"],R["r2"])
assert commutes(R["r0"],R["r3"])
assert commutes(R["r1"],R["r3"])

# Check inversion conjugacy: inv ∘ L_g ∘ inv = R_{g^{-1}}.
# Here we test the stated identity: inv ∘ L_g ∘ inv == R_{g^{-1}}.
# In our construction, R is right multiplication by generator g (not inverse),
# so equivalently inv ∘ L_g ∘ inv == R_{g^{-1}}.
# We can validate by comparing to the provided left perms for the same g
# and verifying the identity with R.
for k in ["r0","r1","r2","r3"]:
    conj = compose(inv, compose(L[k], inv))
    # conj is right multiplication by g^{-1}; since our generators are involutions,
    # g^{-1}=g, so this equals R[k]
    assert conj==R[k], f"conjugacy failed for {k}"

print("OK: all checks passed.")
