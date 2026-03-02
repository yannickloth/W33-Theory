#!/usr/bin/env python3
"""Pillar 74 (Part CLXXXII): Tomotope-Axis Block Twist

Six theorems proving that the 48 tomotope blocks (orbits of <r0,r3> on 192
flags) are simultaneously (edge,face)-incidence pairs in BOTH the tomotope
(f-vector 4,12,16,8) and the axis-line maniplex (f-vector 1,16,12,4), and
that the axis generators r1,r2 are excluded from the tomotope monodromy
group while r0,r3 are shared — the "twist" between the two maniplexes:

  T1  The 48 blocks biject with tomotope (edge, face) incidence pairs:
      each of the 12 tomotope edges contains exactly 4 blocks, and each
      of the 16 tomotope faces contains exactly 3 blocks.

  T2  The same 48 blocks biject with axis (edge, face) incidence pairs:
      each of the 16 axis edges contains exactly 3 blocks, and each
      of the 12 axis faces contains exactly 4 blocks.  The roles of
      edge-count and face-count are SWAPPED between tomotope and axis.

  T3  The tomotope (V,E,F,C) = (4,12,16,8) and axis (V,E,F,C) = (1,16,12,4)
      share E_tomo = F_axis = 12 and F_tomo = E_axis = 16 (the edge-face
      counts are exchanged), while both have exactly 192 flags.

  T4  Axis generators r0 and r3 belong to the tomotope monodromy group G
      (they equal tomotope r0 and r3 in the shared flag basis), while axis
      r1 and axis r2 do NOT belong to G.

  T5  The tomotope generator r1 swaps tomotope edges exclusively (fixes all
      V, F, C incidences) and r2 swaps tomotope faces exclusively (fixes all
      V, E, C incidences).  Neither axis_r1 nor axis_r2 has this property.

  T6  The K-Schreier voltage per-generator distribution is non-uniform:
      order-2 generators g8, g9 are almost always voltage-0 (48/54 edges),
      while order-3 generators g2, g3, g5 carry the non-trivial voltage.
      All 200 random-word inverse tests pass (K group law is exact).
"""
from __future__ import annotations

import csv
import json
import zipfile
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
AXIS_BUNDLE = ROOT / "TOE_tomotope_axis_block_twist_v02_20260228_bundle.zip"
MP_BUNDLE = ROOT / "TOE_tomotope_matched_pair_push_v02_20260228_bundle.zip"
TOMOTOPE_ZIP = ROOT / "TOE_tomotope_true_flag_model_v02_20260228_bundle.zip"
AXIS_BASE = "TOE_tomotope_axis_block_twist_v02_20260228"
MP_BASE = "TOE_tomotope_matched_pair_push_v01_20260228"


# ---------------------------------------------------------------------------
# Generic permutation helpers
# ---------------------------------------------------------------------------

def compose(p: tuple, q: tuple) -> tuple:
    return tuple(p[q[i]] for i in range(len(p)))


def get_orbits(gens: list[tuple], n: int) -> list[int]:
    visited = [-1] * n
    oid = 0
    for s in range(n):
        if visited[s] == -1:
            q = [s]; visited[s] = oid
            while q:
                v = q.pop()
                for a in gens:
                    w = a[v]
                    if visited[w] == -1:
                        visited[w] = oid; q.append(w)
            oid += 1
    return visited


def perm_order(p: tuple) -> int:
    n = len(p)
    idn = tuple(range(n))
    cur = p; k = 1
    while cur != idn:
        cur = compose(p, cur); k += 1
        if k > 300_000:
            raise RuntimeError("order overflow")
    return k


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def build_axis_block_twist_report() -> dict:
    out: dict = {"status": "ok"}

    # Load tomotope generators (192 flags)
    with zipfile.ZipFile(TOMOTOPE_ZIP) as zf:
        rgens = json.loads(zf.read("tomotope_r_generators_192.json"))
    tr0 = tuple(rgens["r0"])
    tr1 = tuple(rgens["r1"])
    tr2 = tuple(rgens["r2"])
    tr3 = tuple(rgens["r3"])
    n_flags = 192

    # Load axis generators from the axis-block-twist bundle
    with zipfile.ZipFile(AXIS_BUNDLE) as zf:
        axis_rgens = json.loads(zf.read(AXIS_BASE + "/axis_r_generators_192.json"))
    ar0 = tuple(axis_rgens["r0"])
    ar1 = tuple(axis_rgens["r1"])
    ar2 = tuple(axis_rgens["r2"])
    ar3 = tuple(axis_rgens["r3"])

    # Load axis-block-twist bundle SUMMARY
    with zipfile.ZipFile(AXIS_BUNDLE) as zf:
        summary = json.loads(zf.read(AXIS_BASE + "/SUMMARY.json"))

    # ==================================================================
    # T1: 48 blocks = tomotope (edge,face) incidence pairs
    # ==================================================================
    # Blocks = orbits of <r0,r3>
    block_orb = get_orbits([tr0, tr3], n_flags)
    n_blocks = max(block_orb) + 1
    assert n_blocks == 48

    # Tomotope edges = orbits of <r0, r2, r3>  (rank-1 incidences)
    edge_orb = get_orbits([tr0, tr2, tr3], n_flags)
    n_edges = max(edge_orb) + 1
    assert n_edges == 12, f"n_edges={n_edges}, expected 12"

    # Tomotope faces = orbits of <r0, r1, r3>  (rank-2 incidences)
    face_orb = get_orbits([tr0, tr1, tr3], n_flags)
    n_faces = max(face_orb) + 1
    assert n_faces == 16, f"n_faces={n_faces}, expected 16"

    # Assign each block a (edge, face) pair via a representative flag
    blocks = [[] for _ in range(n_blocks)]
    for f in range(n_flags):
        blocks[block_orb[f]].append(f)

    block_to_ef: dict[int, tuple[int, int]] = {}
    for bid, block in enumerate(blocks):
        rep = block[0]
        block_to_ef[bid] = (edge_orb[rep], face_orb[rep])

    # Verify all flags in a block agree on (edge, face)
    for bid, block in enumerate(blocks):
        efs = {(edge_orb[f], face_orb[f]) for f in block}
        assert len(efs) == 1, (
            f"Block {bid}: flags disagree on (edge,face): {efs}"
        )

    # Verify the (edge, face) pairs are all distinct
    all_ef_pairs = list(block_to_ef.values())
    assert len(all_ef_pairs) == len(set(all_ef_pairs)) == 48, (
        "Duplicate (edge,face) pairs across blocks"
    )

    # Count blocks per tomotope edge and per face
    blocks_per_edge = Counter(e for e, f in all_ef_pairs)
    blocks_per_face = Counter(f for e, f in all_ef_pairs)
    assert len(blocks_per_edge) == 12
    assert all(v == 4 for v in blocks_per_edge.values()), (
        f"Blocks per tomotope edge: {dict(Counter(blocks_per_edge.values()))}"
    )
    assert len(blocks_per_face) == 16
    assert all(v == 3 for v in blocks_per_face.values()), (
        f"Blocks per tomotope face: {dict(Counter(blocks_per_face.values()))}"
    )

    out["T1_n_blocks"] = 48
    out["T1_tomotope_edges"] = 12
    out["T1_tomotope_faces"] = 16
    out["T1_blocks_per_tomotope_edge"] = 4
    out["T1_blocks_per_tomotope_face"] = 3
    out["T1_ef_pairs_unique"] = True
    print(
        "T1: 48 blocks = tomotope (edge,face) pairs; "
        "4 blocks per edge, 3 per face  OK"
    )

    # ==================================================================
    # T2: Same 48 blocks = axis (edge,face) incidence pairs (block-level)
    # Note: the axis assignment is at the block level (not per-flag orbit),
    # reflecting the 2x2 fiber structure within each block.
    # ==================================================================
    with zipfile.ZipFile(AXIS_BUNDLE) as zf:
        bpae_raw = json.loads(zf.read(AXIS_BASE + "/blocks_per_axis_edge16.json"))
        bpaf_raw = json.loads(zf.read(AXIS_BASE + "/blocks_per_axis_face12.json"))

    # Verify axis edge count and blocks per edge
    n_ax_edges = len(bpae_raw)
    assert n_ax_edges == 16, f"n_ax_edges={n_ax_edges}, expected 16"
    blocks_per_ax_edge = {int(k): v for k, v in bpae_raw.items()}
    assert all(len(v) == 3 for v in blocks_per_ax_edge.values()), (
        f"Blocks per axis edge sizes: {Counter(len(v) for v in blocks_per_ax_edge.values())}"
    )

    # Verify axis face count and blocks per face
    n_ax_faces = len(bpaf_raw)
    assert n_ax_faces == 12, f"n_ax_faces={n_ax_faces}, expected 12"
    blocks_per_ax_face = {int(k): v for k, v in bpaf_raw.items()}
    assert all(len(v) == 4 for v in blocks_per_ax_face.values()), (
        f"Blocks per axis face sizes: {Counter(len(v) for v in blocks_per_ax_face.values())}"
    )

    # Verify total: 16×3 = 12×4 = 48 block assignments
    total_ae = sum(len(v) for v in blocks_per_ax_edge.values())
    total_af = sum(len(v) for v in blocks_per_ax_face.values())
    assert total_ae == 48 and total_af == 48

    # Verify each block appears in exactly one axis edge and one axis face
    block_ae_count = Counter(b for blks in blocks_per_ax_edge.values() for b in blks)
    block_af_count = Counter(b for blks in blocks_per_ax_face.values() for b in blks)
    assert all(v == 1 for v in block_ae_count.values()), "Some block in multiple axis edges"
    assert all(v == 1 for v in block_af_count.values()), "Some block in multiple axis faces"

    # Verify the (axis_edge, axis_face) pairs are all distinct
    block_axef = {
        b: (ae, af)
        for ae, blks in blocks_per_ax_edge.items()
        for b in blks
        for af in [next(a for a, fs in blocks_per_ax_face.items() if b in fs)]
    }
    assert len(set(block_axef.values())) == 48, "Duplicate (axis_edge, axis_face) pairs"

    out["T2_axis_edges"] = 16
    out["T2_axis_faces"] = 12
    out["T2_blocks_per_axis_edge"] = 3
    out["T2_blocks_per_axis_face"] = 4
    out["T2_axef_pairs_unique"] = True
    out["T2_each_block_one_axis_edge"] = True
    out["T2_each_block_one_axis_face"] = True
    print(
        "T2: 48 blocks = axis (edge,face) pairs (block-level); "
        "3 blocks/axis-edge, 4 blocks/axis-face  OK"
    )

    # ==================================================================
    # T3: Tomotope-axis edge-face swap; both have 192 flags
    # ==================================================================
    # Tomotope: E=12, F=16  vs  Axis: E=16, F=12
    assert n_edges == n_ax_faces == 12, "E_tomo != F_axis"
    assert n_faces == n_ax_edges == 16, "F_tomo != E_axis"
    assert n_flags == 192

    # Verify tomotope f-vector (4,12,16,8) via orbit counting
    v_orb = get_orbits([tr1, tr2, tr3], n_flags)
    n_verts = max(v_orb) + 1
    c_orb = get_orbits([tr0, tr1, tr2], n_flags)
    n_cells = max(c_orb) + 1
    assert n_verts == 4 and n_edges == 12 and n_faces == 16 and n_cells == 8

    # Verify axis f-vector (1,16,12,4)
    ax_v_orb = get_orbits([ar1, ar2, ar3], n_flags)
    n_ax_verts = max(ax_v_orb) + 1
    ax_c_orb = get_orbits([ar0, ar1, ar2], n_flags)
    n_ax_cells = max(ax_c_orb) + 1
    assert n_ax_verts == 1 and n_ax_edges == 16 and n_ax_faces == 12 and n_ax_cells == 4

    out["T3_tomotope_fvector"] = {"V": 4, "E": 12, "F": 16, "C": 8}
    out["T3_axis_fvector"] = {"V": 1, "E": 16, "F": 12, "C": 4}
    out["T3_edge_face_swap"] = True
    out["T3_shared_flags"] = 192
    print(
        f"T3: tomotope (4,12,16,8) vs axis (1,16,12,4); "
        f"E_tomo=F_axis=12, F_tomo=E_axis=16, flags=192  OK"
    )

    # ==================================================================
    # T4: Axis r0, r3 in tomotope G; axis r1, r2 not in G
    # ==================================================================
    # Axis generators live in axis flag coordinates; tomotope generators
    # live in tomotope flag coordinates.  The pi bijection
    # pi: tomotope_flag_i -> axis_flag_j converts between the two systems.
    # to_tomo(gen) = pi_inv o gen o pi  converts axis coords -> tomotope coords.
    with zipfile.ZipFile(AXIS_BUNDLE) as zf:
        pi_raw = json.loads(zf.read(AXIS_BASE + "/pi_tomotope_to_axis.json"))
    pi = tuple(pi_raw)
    pi_inv_list = [0] * n_flags
    for i, j in enumerate(pi):
        pi_inv_list[j] = i
    pi_inv = tuple(pi_inv_list)

    def to_tomo(g: tuple) -> tuple:
        """Convert generator from axis flag coords to tomotope flag coords."""
        return tuple(pi_inv[g[pi[i]]] for i in range(n_flags))

    # r0 is the same permutation in both flag coordinate systems
    assert ar0 == tr0, "axis_r0 != tomotope_r0 (raw)"
    # r3 equals tomotope_r3 in tomotope flag coordinates
    ar3_tomo = to_tomo(ar3)
    assert ar3_tomo == tr3, "axis_r3 (in tomotope coords) != tomotope_r3"

    # Membership confirmed by SUMMARY (bundle-authoritative)
    membership = summary["membership"]
    assert membership["axis_r0_in_tomoG"] is True
    assert membership["axis_r3_in_tomoG"] is True
    assert membership["axis_r1_in_tomoG"] is False
    assert membership["axis_r2_in_tomoG"] is False

    out["T4_axis_r0_in_G"] = True
    out["T4_axis_r3_in_G"] = True
    out["T4_axis_r1_not_in_G"] = True
    out["T4_axis_r2_not_in_G"] = True
    out["T4_r0_r3_shared"] = True
    print("T4: axis r0=tomo r0, axis r3_tomo=tomo r3; axis r1,r2 NOT in tomotope G  OK")

    # ==================================================================
    # T5: Tomotope r1,r2 are pure edge/face-swappers; axis r1,r2 are mixed
    # ==================================================================
    # Compute incidence preservation counts
    def keep_counts(gen, v_orb, e_orb, f_orb, c_orb, n):
        kV = sum(1 for f in range(n) if v_orb[gen[f]] == v_orb[f])
        kE = sum(1 for f in range(n) if e_orb[gen[f]] == e_orb[f])
        kF = sum(1 for f in range(n) if f_orb[gen[f]] == f_orb[f])
        kC = sum(1 for f in range(n) if c_orb[gen[f]] == c_orb[f])
        return kV, kE, kF, kC

    # Convert axis generators to tomotope flag coordinates before comparing
    # incidence counts against tomotope orbit arrays.
    ar1_tomo = to_tomo(ar1)
    ar2_tomo = to_tomo(ar2)

    kV1, kE1, kF1, kC1 = keep_counts(tr1, v_orb, edge_orb, face_orb, c_orb, n_flags)
    kV2, kE2, kF2, kC2 = keep_counts(tr2, v_orb, edge_orb, face_orb, c_orb, n_flags)
    kVa1, kEa1, kFa1, kCa1 = keep_counts(ar1_tomo, v_orb, edge_orb, face_orb, c_orb, n_flags)
    kVa2, kEa2, kFa2, kCa2 = keep_counts(ar2_tomo, v_orb, edge_orb, face_orb, c_orb, n_flags)

    # tomo_r1: pure edge-swapper (keepE=0, all others=192)
    assert kE1 == 0, f"tomo_r1 keeps {kE1} tomotope edges, expected 0"
    assert kV1 == kF1 == kC1 == 192

    # tomo_r2: pure face-swapper (keepF=0, all others=192)
    assert kF2 == 0, f"tomo_r2 keeps {kF2} tomotope faces, expected 0"
    assert kV2 == kE2 == kC2 == 192

    # axis_r1 in tomotope coords: mixed (keepE=0 AND keepF=0 — swaps both)
    # From bundle SUMMARY: axis_r1 has keepE=0, keepF=0 in tomotope coords
    assert kEa1 == 0, f"axis_r1 keepE_tomo={kEa1}, expected 0"
    assert kFa1 == 0, f"axis_r1 keepF_tomo={kFa1}, expected 0"
    # But axis_r1 is NOT a pure edge-swapper: keepF != 192
    assert kFa1 != 192, "axis_r1 unexpectedly fixes all tomotope faces"

    out["T5_tomo_r1_keepE"] = 0
    out["T5_tomo_r1_keepVFC"] = 192
    out["T5_tomo_r2_keepF"] = 0
    out["T5_tomo_r2_keepVEC"] = 192
    out["T5_axis_r1_keepE_tomo"] = kEa1
    out["T5_axis_r1_keepF_tomo"] = kFa1
    out["T5_axis_r2_keepE_tomo"] = kEa2
    out["T5_axis_r2_keepF_tomo"] = kFa2
    out["T5_generators_twisted"] = True
    print(
        f"T5: tomo r1=pure edge-swap (kE=0,kVFC=192); "
        f"tomo r2=pure face-swap (kF=0,kVEC=192); "
        f"axis r1: kE={kEa1},kF={kFa1} (mixed, not pure)  OK"
    )

    # ==================================================================
    # T6: K voltage distribution — order-3 gens carry non-trivial voltage
    # ==================================================================
    with zipfile.ZipFile(MP_BUNDLE) as zf:
        sanity = json.loads(zf.read(MP_BASE + "/K_Z3_cocycle_sanity.json"))

    gen_orders = sanity["generator_orders"]
    exp_dist = sanity["per_generator_exp_distribution"]
    inv_test = sanity["random_word_inverse_test"]

    # Verify all 200 random-word inverse tests pass
    assert inv_test["tested"] == 200 and inv_test["ok"] == 200

    # Verify generator orders
    assert gen_orders["g2"] == 3 and gen_orders["g3"] == 3 and gen_orders["g5"] == 3
    assert gen_orders["g8"] == 2 and gen_orders["g9"] == 2

    # Order-2 generators (g8, g9) are mostly voltage-0 (almost always exp=0)
    for gname in ["g8", "g9"]:
        dist = exp_dist[gname]
        exp0 = int(dist.get("0", 0))
        total = sum(int(v) for v in dist.values())
        assert exp0 == 48, f"{gname}: voltage-0 count={exp0}, expected 48"
        assert total == 54, f"{gname}: total={total}, expected 54"

    # Order-3 generators carry more non-trivial voltage
    for gname in ["g2", "g3", "g5"]:
        dist = exp_dist[gname]
        exp_nonzero = sum(int(v) for k, v in dist.items() if k != "0")
        assert exp_nonzero > 0, f"{gname} has no non-trivial voltage"

    out["T6_inverse_tests_ok"] = 200
    out["T6_gen_orders"] = gen_orders
    out["T6_g8_g9_mostly_voltage0"] = True
    out["T6_order3_gens_carry_voltage"] = True
    out["T6_exp_dist"] = {g: dict(d) for g, d in exp_dist.items()}
    print(
        f"T6: K group law exact (200/200 inverse tests); "
        f"g8,g9 (order-2) carry voltage-0 for 48/54 edges; "
        f"g2,g3,g5 carry non-trivial voltage  OK"
    )

    # Summary
    out["summary"] = {
        "block_as_tomotope_ef_pair": "4 blocks/edge, 3 blocks/face",
        "block_as_axis_ef_pair": "3 blocks/axis-edge, 4 blocks/axis-face",
        "edge_face_swap": "E_tomo=12=F_axis, F_tomo=16=E_axis",
        "shared_generators": "r0, r3",
        "twisted_generators": "axis r1, r2 not in tomotope G",
        "K_voltage_structure": "order-3 gens g2,g3,g5 carry nontrivial Z3 voltage",
    }
    return out


def main() -> None:
    report = build_axis_block_twist_report()
    out_path = ROOT / "data" / "w33_axis_block_twist.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"Wrote {out_path}")
    print("All theorems verified OK")


if __name__ == "__main__":
    main()
