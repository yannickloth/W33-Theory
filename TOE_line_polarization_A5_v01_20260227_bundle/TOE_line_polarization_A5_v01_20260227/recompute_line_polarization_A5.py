#!/usr/bin/env python3
"""
Recompute the holonomy-induced line digraph and the hidden A5 structure.

Default inputs match the repository/bundle layout used in these TOE bundles.
You can override with command line flags.

Outputs are written into the current working directory.
"""
from __future__ import annotations
import argparse, json
from pathlib import Path
from collections import defaultdict, Counter, deque
import numpy as np
import networkx as nx
import pandas as pd
import itertools
import random
import sys, os
import time
# make sure the repository root is on sys.path so that "src" package is importable
sys.path.insert(0, os.getcwd())

# octonion multiplication helpers (copied from TOE_Wilmot_G2_Clifford_breakthrough bundle)

# oriented Fano cycles matching Cayley–Dickson basis
FANO_TRIPLES = [
    (1,2,3),
    (1,5,4),
    (1,7,6),
    (2,5,7),
    (2,6,4),
    (3,6,5),
    (3,7,4),
]

def build_imag_prod(triples=FANO_TRIPLES):
    d = {}
    for a,b,c in triples:
        d[(a,b)] = (1,c)
        d[(b,c)] = (1,a)
        d[(c,a)] = (1,b)
        d[(b,a)] = (-1,c)
        d[(c,b)] = (-1,a)
        d[(a,c)] = (-1,b)
    return d

def build_table(triples=FANO_TRIPLES):
    ip = build_imag_prod(triples)
    tab = [[(0,0) for _ in range(8)] for __ in range(8)]
    for i in range(8):
        for j in range(8):
            if i==0:
                tab[i][j] = (1,j)
                continue
            if j==0:
                tab[i][j] = (1,i)
                continue
            if i==j:
                tab[i][j] = (-1,0)
                continue
            s,k = ip[(i,j)]
            tab[i][j] = (s,k)
    return tab

def encode(sign: int, idx: int) -> int:
    return sign * (idx + 1)

def decode(code: int):
    sign = 1 if code > 0 else -1
    idx = abs(code) - 1
    return sign, idx

def build_code_table(triples=FANO_TRIPLES):
    tab = build_table(triples)
    return [[encode(s,k) for (s,k) in row] for row in tab]

TAB = build_code_table()

def canon_cycle(seq):
    s=list(seq)
    rots=[tuple(s[i:]+s[:i]) for i in range(len(s))]
    return min(rots)

def load_json(p: Path):
    return json.loads(p.read_text())

def _original_main_body(orig_args=None):
    # original script expected its own argparse but we now pass a namespace
    # from the wrapper.  If none provided, fall back to default parse.
    if orig_args is None:
        ap = argparse.ArgumentParser()
        ap.add_argument("--dir_srg", type=str, default="/mnt/data/TOE_E6pair_SRG_triangle_decomp_v01_20260227/TOE_E6pair_SRG_triangle_decomp_v01_20260227")
        ap.add_argument("--dir_map", type=str, default="/mnt/data/TOE_edge_to_oriented_rootpairs_v01_20260227/TOE_edge_to_oriented_rootpairs_v01_20260227")
        ap.add_argument("--sp43_w33_action_json", type=str, default="/mnt/data/TOE_pocket_transport_glue_orbit480_v01_20260227_bundle/TOE_WELD_480S_v01_20260227/sp43_generators_w33_action.json")
        ap.add_argument("--w33_line_map_json", type=str, default="/mnt/data/TOE_E6pair_SRG_triangle_decomp_v01_20260227/TOE_E6pair_SRG_triangle_decomp_v01_20260227/w33_line_to_e6pair_triangles.json")
        args = ap.parse_args()
    else:
        args = orig_args

    DIR_SRG = Path(args.dir_srg)
    DIR_MAP = Path(args.dir_map)

    A = np.load(DIR_SRG/"e6pair_srg_adj_36x36.npy")
    blocks = load_json(DIR_SRG/"triangle_decomposition_120_blocks.json")["blocks"]
    pairs36 = load_json(DIR_SRG/"e6_antipode_pairs_36.json")["pairs"]
    rootpair_to_id={frozenset(p):i for i,p in enumerate(pairs36)}

    edge_to_oriented_rootpairs = load_json(DIR_MAP/"edge_to_oriented_rootpair_triple.json")

    # face->two oriented lifts (cyclic order on the 3 vertices)
    tri_set_to_oriented=defaultdict(list)
    for ekey,pairs in edge_to_oriented_rootpairs.items():
        ids=[]
        for a,b in pairs:
            ids.append(rootpair_to_id[frozenset((a,b))])
        tri_set=tuple(sorted(ids))
        tri_set_to_oriented[tri_set].append((ekey, tuple(ids)))
    assert len(tri_set_to_oriented)==120
    assert all(len(v)==2 for v in tri_set_to_oriented.values())

    # canonical orientation per face
    tri_orient={}
    for tri_set,lst in tri_set_to_oriented.items():
        opts=[]
        for ekey, ids in lst:
            opts.append((canon_cycle(ids), ekey, ids))
        opts.sort(key=lambda x:x[0])
        tri_orient[tri_set]=opts[0][0]

    # edge->third vertex in chosen face
    edge_to_third={}
    for tri in blocks:
        a,b,c=tri
        for u,v,w in [(a,b,c),(a,c,b),(b,c,a)]:
            e=tuple(sorted((u,v)))
            edge_to_third[e]=w

    # edge tail orientation from chosen faces
    edge_tail={}
    for tri in blocks:
        tri_set=tuple(sorted(tri))
        x,y,z=tri_orient[tri_set]
        for (a,b) in [(x,y),(y,z),(z,x)]:
            e=tuple(sorted((a,b)))
            edge_tail[e]=a
    assert len(edge_tail)==360

    c_e={e:(0 if edge_tail[e]==e[0] else 1) for e in edge_tail}

    # build SRG graph
    G=nx.Graph()
    G.add_nodes_from(range(36))
    for i in range(36):
        for j in range(i+1,36):
            if A[i,j]:
                G.add_edge(i,j)

    chosen=set(tuple(sorted(tri)) for tri in blocks)

    # enumerate all SRG triangles and odd nonface ones
    all_tri=set()
    for u in range(36):
        nbr=list(G.neighbors(u))
        for i in range(len(nbr)):
            for j in range(i+1,len(nbr)):
                a,b=nbr[i],nbr[j]
                if G.has_edge(a,b):
                    all_tri.add(tuple(sorted((u,a,b))))
    assert len(all_tri)==1200

    odd_nonface=set()
    for tri in all_tri:
        a,b,c=tri
        edges=[tuple(sorted((a,b))),tuple(sorted((b,c))),tuple(sorted((c,a)))]
        back=sum(c_e[e] for e in edges)
        hol=back%2
        if tri not in chosen and hol==1:
            odd_nonface.add(tri)
    assert len(odd_nonface)==240

    def edge_face(u,v):
        w=edge_to_third[tuple(sorted((u,v)))]
        return tuple(sorted((u,v,w)))

    def img_face(tri):
        a,b,c=tri
        A_=edge_to_third[tuple(sorted((a,b)))]
        B_=edge_to_third[tuple(sorted((a,c)))]
        C_=edge_to_third[tuple(sorted((b,c)))]
        return tuple(sorted((A_,B_,C_)))

    # special faces: those hit by 6 odd nonface triangles under img_face
    pre=Counter(img_face(t) for t in odd_nonface)
    special_faces=set([f for f,k in pre.items() if k==6])
    assert len(special_faces)==40

    # map special face -> line_id via provided line map
    line_map = load_json(Path(args.w33_line_map_json))
    face_to_line={}
    for lm in line_map:
        lid=lm["line_id"]
        for tb in lm["triangle_blocks"]:
            f=tuple(sorted(tb))
            if f in special_faces:
                face_to_line[f]=lid
    assert len(face_to_line)==40

    # build the directed line digraph from odd nonface triangles
    dir_edges=[]
    rows=[]
    for tri in odd_nonface:
        F_img=img_face(tri)
        tail=face_to_line[F_img]
        a,b,c=tri
        ef=[edge_face(a,b),edge_face(a,c),edge_face(b,c)]
        sp=[f for f in ef if f in special_faces]
        assert len(sp)==1
        head=face_to_line[sp[0]]
        dir_edges.append((tail,head))
        rows.append({
            "tail_line": tail,
            "head_line": head,
            "tri_a": tri[0], "tri_b": tri[1], "tri_c": tri[2],
            "image_face": ",".join(map(str,F_img)),
            "edge_special_face": ",".join(map(str,sp[0])),
            "holonomy": 1
        })

    DG=nx.DiGraph()
    DG.add_nodes_from(range(40))
    DG.add_edges_from(dir_edges)
    assert DG.number_of_edges()==240
    assert set(dict(DG.out_degree()).values())=={6}
    assert set(dict(DG.in_degree()).values())=={6}

    UG=DG.to_undirected()
    comps=[sorted(list(c)) for c in nx.connected_components(UG)]
    comp_sizes=[len(c) for c in comps]

    # identify 10-component as L(K5)
    comp10=[c for c in comps if len(c)==10][0]
    sub10=UG.subgraph(comp10).copy()
    K5=nx.complete_graph(5)
    LK5=nx.line_graph(K5)
    gm=nx.isomorphism.GraphMatcher(sub10, LK5)
    assert gm.is_isomorphic()
    iso=next(gm.isomorphisms_iter())
    iso_map={int(k): tuple(sorted(map(int,v))) for k,v in iso.items()}

    # compute stabilizer subgroup (inside PSp action induced from Sp(4,3) matrices) that preserves DG
    sp_w33 = load_json(Path(args.sp43_w33_action_json))
    gens_perm40=[g["perm40"] for g in sp_w33["generators"]]

    # line_id -> set of points
    lineid_to_points={lm["line_id"]: tuple(sorted(lm["w33_points"])) for lm in line_map}
    line_sets=[set(lineid_to_points[lid]) for lid in range(40)]
    set_to_lineid={tuple(sorted(s)): lid for lid,s in enumerate(line_sets)}

    def induce_line_perm(perm40):
        out=[None]*40
        for lid,pts in enumerate(line_sets):
            img=tuple(sorted(perm40[p] for p in pts))
            out[lid]=set_to_lineid[img]
        return tuple(out)

    gens_line=[induce_line_perm(p) for p in gens_perm40]
    # generate PSp subgroup (size 25920) on lines
    idperm=tuple(range(40))
    seen={idperm}
    dq=deque([idperm])
    while dq:
        cur=dq.popleft()
        for g in gens_line:
            nxt=tuple(g[i] for i in cur)
            if nxt not in seen:
                seen.add(nxt); dq.append(nxt)
    # should be 25920
    # check stabilizer of DG
    DG_edge_set=set(dir_edges)
    DG_edge_list=list(DG_edge_set)
    def preserves(perm):
        for u,v in DG_edge_list:
            if (perm[u],perm[v]) not in DG_edge_set:
                return False
        return True
    stab=[perm for perm in seen if preserves(perm)]

    # export
    pd.DataFrame(rows).sort_values(["tail_line","head_line","tri_a","tri_b","tri_c"]).to_csv("line_digraph_edges_240.csv", index=False)
    ud=set(tuple(sorted((u,v))) for u,v in dir_edges)
    pd.DataFrame([{"u":u,"v":v} for u,v in sorted(ud)]).to_csv("line_undirected_edges_120.csv", index=False)
    Path("line_components.json").write_text(json.dumps({
        "components": comps,
        "sizes": comp_sizes,
        "comp10": comp10,
        "note": "Components of the undirected version of the holonomy-induced line graph."
    }, indent=2))
    Path("comp10_isomorphism_to_LK5.json").write_text(json.dumps(iso_map, indent=2))
    # find small generating set for stab
    def compose(p,q):
        return tuple(p[i] for i in q)
    gens_stab=[]
    cur=set([idperm])
    # greedy
    for _ in range(10):
        improved=False
        for g in stab:
            # closure size if added
            ss={idperm}
            dd=deque([idperm])
            for gg in gens_stab+[g]:
                pass
            dd=deque([idperm])
            ss={idperm}
            while dd:
                x=dd.popleft()
                for gg in gens_stab+[g]:
                    y=compose(gg,x)
                    if y not in ss:
                        ss.add(y); dd.append(y)
            if len(ss)>len(cur):
                gens_stab.append(g)
                cur=ss
                improved=True
                break
        if not improved:
            break
        if len(cur)==len(stab):
            break
    Path("stabilizer_A5_generators.json").write_text(json.dumps({
        "size": len(stab),
        "generators": [list(g) for g in gens_stab],
        "note": "Stabilizer subgroup inside PSp(4,3) on W33 lines preserving the line digraph. Size 60 (A5)."
    }, indent=2))

    print("OK")
    print("odd_nonface:", len(odd_nonface))
    print("special_faces:", len(special_faces))
    print("DG edges:", DG.number_of_edges())
    print("components:", comp_sizes)
    print("stab size:", len(stab))



def compose_signed(ga, gb):
    # compose two signed permutations
    # each argument is a pair (perm, sign) where perm and sign are length-8 sequences
    perm_a, sign_a = ga
    perm_b, sign_b = gb
    perm = [0] * 8
    sign = [1] * 8
    for i in range(1, 8):
        j = perm_b[i]
        perm[i] = perm_a[j]
        sign[i] = sign_a[j] * sign_b[i]
    # return as tuples so elements can be used as dict keys
    return (tuple(perm), tuple(sign))


def is_identity(elem):
    perm, sign = elem
    if any(perm[i] != i for i in range(8)):
        return False
    if any(sign[i] != 1 for i in range(8)):
        return False
    return True


def apply_to_code(code, elem):
    # reuse apply_code logic from octonion side
    s, idx = decode(code)
    if idx == 0:
        return code
    perm, sign = elem
    return s * sign[idx] * encode(1, perm[idx])


def enumerate_signed_group():
    """Enumerate all signed permutations on 7 imaginary units.

    Returns a tuple containing:
      - elements: list of elem representations (perm, sign)
      - elem_to_id: dict mapping representation -> integer id
      - order2_ids: list of ids with order exactly 2
      - order3_ids: list of ids with order exactly 3
      - orbit_dict: mapping from table rep -> orbit index
      - element_for_table: list of representative element id for each orbit index
      - orbit_index_for_elem: list mapping each element id to its orbit index
    """
    from itertools import permutations, product

    elements = []
    elem_to_id = {}
    order2_ids = []
    order3_ids = []
    orbit_dict = {}
    element_for_table = []
    orbit_index_for_elem = []

    # helper: compute table representation for element
    def table_rep(elem):
        # flatten 8x8 multiplication table under elem
        rows = []
        for i in range(8):
            for j in range(8):
                rows.append(apply_to_code(TAB[i][j], elem))
        return tuple(rows)

    id_counter = 0
    identity = (tuple(range(8)), tuple([1] * 8))

    for perm in permutations(range(1, 8)):
        perm_arr = [0] * 8
        for i, img in enumerate(perm, start=1):
            perm_arr[i] = img
        for sp in product([1, -1], repeat=7):
            sign_arr = [1] * 8
            for i, sg in enumerate(sp, start=1):
                sign_arr[i] = sg
            rep = (tuple(perm_arr), tuple(sign_arr))
            eid = id_counter
            id_counter += 1
            elements.append(rep)
            elem_to_id[rep] = eid
            # order checks
            # involution
            if compose_signed(rep, rep) == identity:
                order2_ids.append(eid)
            # order3
            if compose_signed(compose_signed(rep, rep), rep) == identity:
                order3_ids.append(eid)
            # orbit mapping
            rep_tab = table_rep(rep)
            if rep_tab not in orbit_dict:
                orbit_dict[rep_tab] = len(element_for_table)
                element_for_table.append(eid)
            orbit_index_for_elem.append(orbit_dict[rep_tab])
    return (
        elements,
        elem_to_id,
        order2_ids,
        order3_ids,
        orbit_dict,
        element_for_table,
        orbit_index_for_elem,
    )


def compute_order(elem, limit=10):
    """Compute the order of an element, stopping early if exceeds limit."""
    cur = elem
    for k in range(1, limit + 1):
        if is_identity(cur):
            return k
        cur = compose_signed(cur, elem)
    return None


def closure_from_generators(gen_ids, elements, elem_to_id):
    """Compute subgroup generated by element ids using BFS closure."""
    id_to_elem = elements
    seen = set(gen_ids)
    dq = deque(gen_ids)
    while dq:
        a_id = dq.popleft()
        a = id_to_elem[a_id]
        for b_id in list(seen):
            b = id_to_elem[b_id]
            c = compose_signed(a, b)
            c_id = elem_to_id[c]
            if c_id not in seen:
                seen.add(c_id)
                dq.append(c_id)
            d = compose_signed(b, a)
            d_id = elem_to_id[d]
            if d_id not in seen:
                seen.add(d_id)
                dq.append(d_id)
    return seen


def compute_orbit_partition(H_ids, element_for_table, orbit_index_for_elem, elements, elem_to_id):
    """Return sorted list of orbit sizes of H acting on the 480 tables."""
    # helper to apply element (by id) to a table index
    def apply_elem_to_index(eid, table_idx):
        g0_id = element_for_table[table_idx]
        g0 = elements[g0_id]
        elem = elements[eid]
        comp = compose_signed(elem, g0)
        comp_id = elem_to_id[comp]
        return orbit_index_for_elem[comp_id]

    visited = set()
    orbits = []
    for i in range(len(element_for_table)):
        if i in visited:
            continue
        queue = [i]
        orb = []
        while queue:
            j = queue.pop()
            if j in visited:
                continue
            visited.add(j)
            orb.append(j)
            for eid in H_ids:
                k = apply_elem_to_index(eid, j)
                if k not in visited:
                    queue.append(k)
        orbits.append(len(orb))
    orbits.sort()
    return orbits


def search_octonion_A5(max_g=None, max_h=None, random_seed=12345, verbose=False):
    """Search for A5 subgroups with the target orbit fingerprint.

    Returns a list of candidate dictionaries containing generator ids and
    orbit partitions.
    """
    (
        elements,
        elem_to_id,
        order2_ids,
        order3_ids,
        orbit_dict,
        element_for_table,
        orbit_index_for_elem,
    ) = enumerate_signed_group()

    if max_g is not None and max_g < len(order2_ids):
        random.seed(random_seed)
        order2_ids = random.sample(order2_ids, max_g)
    if max_h is not None and max_h < len(order3_ids):
        random.seed(random_seed + 1)
        order3_ids = random.sample(order3_ids, max_h)

    target_fingerprint = [20] * 6 + [60] * 6

    candidates = []
    count_pairs = 0
    for g_id in order2_ids:
        for h_id in order3_ids:
            count_pairs += 1
            # test relation (gh)^5 = 1
            gh = compose_signed(elements[g_id], elements[h_id])
            # quick order-5 check
            gh5 = gh
            for _ in range(4):
                gh5 = compose_signed(gh5, gh)
            if not is_identity(gh5):
                continue
            # generate subgroup and check size
            H = closure_from_generators([g_id, h_id], elements, elem_to_id)
            if len(H) != 60:
                continue
            orbits = compute_orbit_partition(H, element_for_table, orbit_index_for_elem, elements, elem_to_id)
            if orbits == target_fingerprint:
                candidates.append({
                    "gens": [g_id, h_id],
                    "orbit": orbits,
                    "H_size": len(H),
                })
                if verbose:
                    print(f"Found candidate with generators {g_id},{h_id}")
            # optional early break if one found
            if candidates and not verbose:
                return candidates
    return candidates


def package_octonion_bundle(result_file):
    import zipfile
    inner_dir = "TOE_octonion_A5_search_v01_20260227"
    bundle_name = "TOE_octonion_A5_search_v01_20260227_bundle.zip"
    with zipfile.ZipFile(bundle_name, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.write(result_file, f"{inner_dir}/{os.path.basename(result_file)}")
        readme = f"""Octonion A5 search results

Generated by recompute_line_polarization_A5.py with --search-octonion.
"""
        zf.writestr(f"{inner_dir}/README.md", readme)
    print("created octonion bundle", bundle_name)


def main(args=None):
    import argparse

    parser = argparse.ArgumentParser(description="Recompute line polarization and optionally search octonion A5")
    # original arguments from previous version
    parser.add_argument("--dir_srg", type=str, default="/mnt/data/TOE_E6pair_SRG_triangle_decomp_v01_20260227/TOE_E6pair_SRG_triangle_decomp_v01_20260227")
    parser.add_argument("--dir_map", type=str, default="/mnt/data/TOE_edge_to_oriented_rootpairs_v01_20260227/TOE_edge_to_oriented_rootpairs_v01_20260227")
    parser.add_argument("--sp43_w33_action_json", type=str, default="/mnt/data/TOE_pocket_transport_glue_orbit480_v01_20260227_bundle/TOE_WELD_480S_v01_20260227/sp43_generators_w33_action.json")
    parser.add_argument("--w33_line_map_json", type=str, default="/mnt/data/TOE_E6pair_SRG_triangle_decomp_v01_20260227/TOE_E6pair_SRG_triangle_decomp_v01_20260227/w33_line_to_e6pair_triangles.json")
    # new search options
    parser.add_argument("--search-octonion", action="store_true",
                        help="run the signed-perm A5 search on the octonion tables")
    parser.add_argument("--max-g", type=int, help="limit number of order-2 elements sampled")
    parser.add_argument("--max-h", type=int, help="limit number of order-3 elements sampled")
    parser.add_argument("--seed", type=int, default=12345,
                        help="random seed when sampling")
    parser.add_argument("--verbose", action="store_true")
    parsed = parser.parse_args(args)

    # original computation (unchanged) is expensive and may require
    # external data files.  When the user only wants to run the octonion
    # search we can skip this step.
    if not parsed.search_octonion:
        t0 = time.time()
        _original_main_body(parsed)
    else:
        print("skipping SRG/line-polarization computation (search-only mode)")

    if parsed.search_octonion:
        print("\nRunning octonion A5 subgroup search...")
        candidates = search_octonion_A5(max_g=parsed.max_g,
                                       max_h=parsed.max_h,
                                       random_seed=parsed.seed,
                                       verbose=parsed.verbose)
        outname = "octonion_A5_search_results.json"
        with open(outname, "w") as f:
            json.dump({"candidates": candidates}, f, indent=2)
        print(f"wrote results to {outname}")
        package_octonion_bundle(outname)

    return



if __name__ == "__main__":
    main()
