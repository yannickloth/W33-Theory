#!/usr/bin/env python3
"""
Build the *3-generation* E8→E6×SU(3) coupling atlas in the canonical E6-id labeling,
and intersect it with the firewall (bad-triad) cut and SM field/component labels.

Key idea:
  `artifacts/canonical_su3_gauge_and_cubic.json` already contains the *exact* list of
  couplings between the three SU(3)-fundamental 27-orbits (oa,ob in 3) into the unique
  27bar-orbit (ocbar in 3bar), expressed in E6-id indices with the associated meet-triad.

Those couplings are in bijection with the 135 meet-edges of the Schläfli complement:
  - per ordered orbit pair (oa,ob): 270 directed couplings = 135 undirected meet-edges × 2
  - across 6 ordered orbit pairs: 1620 total couplings

The firewall blocks exactly the 9 bad meet-triangles = 27 bad meet-edges, hence
54 directed couplings per ordered orbit pair (20%), leaving 216 "kernel" couplings.

Outputs:
  - artifacts/toe_three_generation_coupling_atlas.json
  - artifacts/toe_three_generation_coupling_atlas.md
"""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Sequence, Tuple

ROOT = Path(__file__).resolve().parents[1]


def _load_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, data: Dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")


def _write_md(path: Path, lines: List[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


ColorW = Tuple[int, int]

COLOR_LABEL: Dict[ColorW, str] = {
    (0, 1): "c0",
    (1, -1): "c1",
    (-1, 0): "c2",
}


def _color_label(w12: ColorW, *, rep: str) -> str | None:
    if rep == "1":
        return None
    if rep == "3":
        key = w12
    elif rep == "3bar":
        key = (-w12[0], -w12[1])
    else:
        raise ValueError(f"Unexpected SU3 rep: {rep}")
    if key not in COLOR_LABEL:
        raise ValueError(f"Unexpected SU3 weight for color label: {w12} rep={rep}")
    return COLOR_LABEL[key]


def _su2_comp(w5: int, *, rep: str) -> str | None:
    if rep == "1":
        return None
    if w5 == 1:
        return "up"
    if w5 == -1:
        return "dn"
    raise ValueError("Expected SU2 doublet component w5=±1")


@dataclass(frozen=True)
class Vtx:
    i: int
    field: str
    su3: str
    su2: str
    y6: int
    q6: int
    w: Tuple[int, int, int, int, int, int]

    @property
    def w12(self) -> ColorW:
        return (self.w[1], self.w[2])

    @property
    def w5(self) -> int:
        return self.w[5]

    def label(self) -> str:
        parts: List[str] = []
        c = _color_label(self.w12, rep=self.su3)
        if c is not None:
            parts.append(c)
        comp = _su2_comp(self.w5, rep=self.su2)
        if comp is not None:
            parts.append(comp)
        if parts:
            return f"{self.field}[{','.join(parts)}]"
        return self.field


def main(argv: Sequence[str] | None = None) -> None:
    atlas_json = ROOT / "artifacts" / "toe_three_generation_coupling_atlas.json"
    atlas_md = ROOT / "artifacts" / "toe_three_generation_coupling_atlas.md"

    canon = _load_json(ROOT / "artifacts" / "canonical_su3_gauge_and_cubic.json")
    if not isinstance(canon, dict):
        raise RuntimeError("Invalid canonical_su3_gauge_and_cubic.json")
    couplings = (
        canon.get("instances", {}).get("couplings")
        if isinstance(canon.get("instances"), dict)
        else None
    )
    if not isinstance(couplings, list):
        raise RuntimeError(
            "canonical_su3_gauge_and_cubic.json missing instances.couplings"
        )

    orbits_3 = canon.get("orbits_3")
    orbits_3bar = canon.get("orbits_3bar")
    if not (isinstance(orbits_3, list) and isinstance(orbits_3bar, list)):
        raise RuntimeError(
            "canonical_su3_gauge_and_cubic.json missing orbits_3/orbits_3bar"
        )

    # Stable family ordering by SU(3) weight (lexicographic).
    o3_sorted = sorted(
        [
            {
                "orbit": int(x["orbit"]),
                "su3_weight": tuple(int(t) for t in x["su3_weight"]),
            }
            for x in orbits_3
        ],
        key=lambda d: d["su3_weight"],
    )
    o3b_sorted = sorted(
        [
            {
                "orbit": int(x["orbit"]),
                "su3_weight": tuple(int(t) for t in x["su3_weight"]),
            }
            for x in orbits_3bar
        ],
        key=lambda d: d["su3_weight"],
    )

    gen_of_orbit_3 = {d["orbit"]: gi for gi, d in enumerate(o3_sorted)}
    gen_of_orbit_3bar = {d["orbit"]: gi for gi, d in enumerate(o3b_sorted)}

    # SM labeling + firewall forbidden triads.
    sm = _load_json(ROOT / "artifacts" / "toe_sm_decomposition_27.json")
    if not isinstance(sm, dict):
        raise RuntimeError("Invalid toe_sm_decomposition_27.json")
    per_v = sm.get("per_vertex")
    triads_blob = sm.get("triads")
    if not (isinstance(per_v, list) and isinstance(triads_blob, dict)):
        raise RuntimeError("toe_sm_decomposition_27.json missing per_vertex/triads")
    bad_tri = {
        tuple(sorted(int(x) for x in t))
        for t in triads_blob.get("firewall_bad_triangles", [])
    }
    if len(bad_tri) != 9:
        raise RuntimeError(
            "Expected 9 firewall bad triads in toe_sm_decomposition_27.json"
        )

    vtx: Dict[int, Vtx] = {}
    for row in per_v:
        if not isinstance(row, dict):
            continue
        i = int(row["i"])
        vtx[i] = Vtx(
            i=i,
            field=str(row["field"]),
            su3=str(row["su3"]),
            su2=str(row["su2"]),
            y6=int(row["Y6"]),
            q6=int(row["Q6"]),
            w=tuple(int(x) for x in row["w"]),
        )
    if len(vtx) != 27:
        raise RuntimeError(
            "Expected 27 vertices in toe_sm_decomposition_27.json per_vertex"
        )

    # Optional parity annotation schemes.
    parity_by_scheme: Dict[str, Dict[Tuple[int, int, int], int]] = {}
    mapping_path = ROOT / "artifacts" / "firewall_bad_triads_mapping.json"
    if mapping_path.exists():
        mapping = _load_json(mapping_path)
        if isinstance(mapping, dict):
            sel = mapping.get("selection_parity_on_bad_triads")
            if isinstance(sel, dict):
                for scheme, blob in sel.items():
                    if not isinstance(blob, dict):
                        continue
                    tri_list = blob.get("bad_triads")
                    if not isinstance(tri_list, list):
                        continue
                    m: Dict[Tuple[int, int, int], int] = {}
                    for entry in tri_list:
                        if not isinstance(entry, dict):
                            continue
                        tri = entry.get("triad")
                        par = entry.get("parity")
                        if not (
                            isinstance(tri, list)
                            and len(tri) == 3
                            and isinstance(par, int)
                        ):
                            continue
                        t = tuple(sorted(int(x) for x in tri))
                        m[t] = int(par)
                    if m:
                        parity_by_scheme[str(scheme)] = m

    # Build detailed coupling records + aggregates.
    recs = []
    per_orbit_pair = Counter()
    per_orbit_pair_forbidden = Counter()
    per_input_fields = Counter()
    per_input_fields_forbidden = Counter()
    per_triad_type = Counter()
    per_triad_type_forbidden = Counter()

    for c in couplings:
        if not isinstance(c, dict):
            continue
        oa = int(c["oa"])
        ob = int(c["ob"])
        ocbar = int(c["ocbar"])
        i = int(c["i"])
        j = int(c["j"])
        kbar = int(c["kbar"])
        tri = tuple(sorted(int(x) for x in c["triad"]))
        raw_bit = int(c["raw_bit"])

        # Determine k as the third vertex in the triad (27-id, not bar).
        if i == j or i not in tri or j not in tri:
            raise RuntimeError("Invalid coupling triad: missing i/j")
        ks = [x for x in tri if x not in (i, j)]
        if len(ks) != 1:
            raise RuntimeError("Expected a unique third vertex k in triad")
        k = int(ks[0])

        forbidden = tri in bad_tri
        parity = (
            {scheme: int(m[tri]) for scheme, m in parity_by_scheme.items() if tri in m}
            if forbidden
            else {}
        )

        ga = gen_of_orbit_3.get(oa)
        gb = gen_of_orbit_3.get(ob)
        gcbar = gen_of_orbit_3bar.get(ocbar)
        if ga is None or gb is None or gcbar is None:
            raise RuntimeError("Coupling references orbit not in orbits_3/orbits_3bar")

        in_fields = (vtx[i].field, vtx[j].field)
        out_field = vtx[k].field
        triad_fields = tuple(sorted([vtx[t].field for t in tri]))

        key_pair = (oa, ob, ocbar)
        per_orbit_pair[key_pair] += 1
        if forbidden:
            per_orbit_pair_forbidden[key_pair] += 1

        per_input_fields[in_fields + (out_field,)] += 1
        if forbidden:
            per_input_fields_forbidden[in_fields + (out_field,)] += 1

        per_triad_type[triad_fields] += 1
        if forbidden:
            per_triad_type_forbidden[triad_fields] += 1

        recs.append(
            {
                "oa": oa,
                "ob": ob,
                "ocbar": ocbar,
                "gen_a": int(ga),
                "gen_b": int(gb),
                "gen_cbar": int(gcbar),
                "i": i,
                "j": j,
                "k": k,
                "kbar": kbar,
                "triad": list(tri),
                "forbidden": bool(forbidden),
                "parity": parity,
                "raw_bit": raw_bit,
                "in": {
                    "fields": [vtx[i].field, vtx[j].field],
                    "labels": [vtx[i].label(), vtx[j].label()],
                    "verts": [i, j],
                },
                "out": {"field": out_field, "label": vtx[k].label(), "vert": k},
                "triad_fields": list(triad_fields),
            }
        )

    # Global consistency checks.
    if len(recs) != 1620:
        raise RuntimeError(f"Expected 1620 couplings, got {len(recs)}")
    # 6 ordered orbit pairs; 270 each.
    if len(per_orbit_pair) != 6 or set(per_orbit_pair.values()) != {270}:
        raise RuntimeError(
            "Unexpected orbit-pair coupling counts (expected 6 pairs × 270)"
        )
    # Forbidden: 54 each (since 27 bad undirected edges => 54 directed).
    if set(per_orbit_pair_forbidden.values()) != {54}:
        raise RuntimeError("Unexpected forbidden counts per orbit-pair (expected 54)")

    out: Dict[str, object] = {
        "status": "ok",
        "family_orbits": {
            "orbits_3": [
                {"gen": int(gen_of_orbit_3[d["orbit"]]), **d} for d in o3_sorted
            ],
            "orbits_3bar": [
                {"gen": int(gen_of_orbit_3bar[d["orbit"]]), **d} for d in o3b_sorted
            ],
        },
        "counts": {
            "couplings_total": len(recs),
            "couplings_forbidden": int(sum(per_orbit_pair_forbidden.values())),
            "couplings_allowed": int(
                len(recs) - sum(per_orbit_pair_forbidden.values())
            ),
            "orbit_pairs": [
                {
                    "oa": oa,
                    "ob": ob,
                    "ocbar": ocbar,
                    "total": int(per_orbit_pair[(oa, ob, ocbar)]),
                    "forbidden": int(per_orbit_pair_forbidden[(oa, ob, ocbar)]),
                    "allowed": int(
                        per_orbit_pair[(oa, ob, ocbar)]
                        - per_orbit_pair_forbidden[(oa, ob, ocbar)]
                    ),
                }
                for (oa, ob, ocbar) in sorted(per_orbit_pair)
            ],
        },
        "top_interactions": [
            {
                "in_fields": [a, b],
                "out_field": c,
                "count": int(per_input_fields[(a, b, c)]),
                "forbidden": int(per_input_fields_forbidden.get((a, b, c), 0)),
                "forbidden_frac": float(
                    per_input_fields_forbidden.get((a, b, c), 0)
                    / per_input_fields[(a, b, c)]
                ),
            }
            for (a, b, c), _v in per_input_fields.most_common(40)
        ],
        "triad_types": [
            {
                "fields": list(k),
                "count": int(v),
                "forbidden": int(per_triad_type_forbidden.get(k, 0)),
                "forbidden_frac": float(per_triad_type_forbidden.get(k, 0) / v),
            }
            for k, v in sorted(per_triad_type.items(), key=lambda kv: (-kv[1], kv[0]))
        ],
        "records": recs,
    }
    _write_json(atlas_json, out)

    # Markdown summary.
    lines: List[str] = []
    lines.append("# TOE: 3-Generation Coupling Atlas (E8→E6×SU(3))")
    lines.append("")
    lines.append("## Family Orbits")
    lines.append("### 3 (generations)")
    for d in out["family_orbits"]["orbits_3"]:
        lines.append(
            f"- gen {d['gen']}: orbit {d['orbit']} su3_weight {list(d['su3_weight'])}"
        )
    lines.append("### 3bar (conjugates)")
    for d in out["family_orbits"]["orbits_3bar"]:
        lines.append(
            f"- gen {d['gen']}: orbit {d['orbit']} su3_weight {list(d['su3_weight'])}"
        )
    lines.append("")
    lines.append("## Global Counts")
    lines.append(f"- couplings: `{out['counts']['couplings_total']}`")
    lines.append(f"- forbidden (firewall): `{out['counts']['couplings_forbidden']}`")
    lines.append(f"- allowed (kernel): `{out['counts']['couplings_allowed']}`")
    lines.append("")
    lines.append("## Per Ordered Orbit-Pair (oa,ob→ocbar)")
    for row in out["counts"]["orbit_pairs"]:
        lines.append(
            f"- ({row['oa']},{row['ob']})→{row['ocbar']}: total `{row['total']}` forbidden `{row['forbidden']}` allowed `{row['allowed']}`"
        )
    lines.append("")
    lines.append("## Triad Types (via outputs)")
    for row in out["triad_types"]:
        lines.append(
            f"- {row['fields']}: count `{row['count']}` forbidden `{row['forbidden']}` frac `{row['forbidden_frac']:.3f}`"
        )
    lines.append("")
    lines.append("## Top Oriented Interactions  (field_i, field_j) -> field_k")
    for row in out["top_interactions"][:20]:
        lines.append(
            f"- {row['in_fields']} → {row['out_field']}: count `{row['count']}` forbidden `{row['forbidden']}` frac `{row['forbidden_frac']:.3f}`"
        )
    lines.append("")
    lines.append(f"- JSON: `{atlas_json}`")
    _write_md(atlas_md, lines)

    print(f"Wrote {atlas_json}")
    print(f"Wrote {atlas_md}")


if __name__ == "__main__":
    main()
