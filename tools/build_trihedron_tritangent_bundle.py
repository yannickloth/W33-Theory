#!/usr/bin/env python3
"""
Build a trihedron–tritangent incidence bundle from the W33 ↔ cubic surface dictionary
bundle.

Usage:
  py -3 tools/build_trihedron_tritangent_bundle.py --bundle-zip <zip> --out-dir artifacts/trihedron_tritangent_bundle_20260209

What it does:
  - Extracts the provided zip (or reads an extracted dir)
  - Reads CSVs (H27↔Schlafli labels, N12 Steiner trihedra, plane edges/grades, missing-9)
  - Builds a bipartite incidence graph: Trihedron (N12) <-> TritangentPlane
  - Classifies planes (E/L/Q patterns), marks the 9 missing planes
  - If available, generates/loads W(E6) action on 27 and computes orbits of planes/trihedra
  - Writes JSON/CSV/MD summary files into the output directory

Notes:
  - This script is robust to differing CSV column names; it prints detected headers for inspection
  - If `artifacts/we6_signed_action_on_27.json` is missing, it attempts to run
    `tools/export_we6_signed_action_on_27.py` to generate it (may require extra deps)

Outputs (under --out-dir):
  - trihedra.json
  - tritangent_planes.json
  - incidence_graph.gml
  - trihedron_tritangent_report.md
  - trihedron_tritangent_orbits.json

"""
from __future__ import annotations

import argparse
import csv
import io
import json
import os
import shutil
import zipfile
from collections import defaultdict, deque
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

try:
    import networkx as nx
except Exception:  # pragma: no cover - networkx is usually available
    raise RuntimeError("networkx is required; please install it in your environment")

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT = ROOT / "artifacts" / "trihedron_tritangent_bundle_20260209"


def find_csv(path: Path, patterns: List[str]) -> Optional[Path]:
    for p in path.iterdir():
        name = p.name.lower()
        if any(q in name for q in patterns) and p.suffix.lower() in {".csv", ".tsv"}:
            return p
        # nested
        if p.is_dir():
            res = find_csv(p, patterns)
            if res is not None:
                return res
    return None


def read_csv(path: Path) -> Tuple[List[str], List[Dict[str, str]]]:
    with path.open("r", encoding="utf-8") as f:
        txt = f.read()
    # Normalize newlines and detect delimiter
    sample = txt[:4096]
    if "\t" in sample and sample.count("\t") > sample.count(","):
        delim = "\t"
    else:
        delim = ","
    rdr = csv.DictReader(io.StringIO(txt), delimiter=delim)
    rows = [dict(r) for r in rdr]
    return list(rdr.fieldnames or []), rows


def try_int(s: str) -> Optional[int]:
    try:
        return int(s)
    except Exception:
        return None


def canonical_split_list(text: str) -> List[str]:
    if not text:
        return []
    for sep in ["|", ";", ",", " "]:
        if sep in text:
            parts = [p.strip() for p in text.split(sep) if p.strip()]
            if parts:
                return parts
    return [text.strip()]


def extract_bundle(bundle_zip: Path, out_dir: Path) -> Path:
    assert bundle_zip.exists(), f"Missing bundle zip: {bundle_zip}"
    tmp = out_dir
    if tmp.exists():
        shutil.rmtree(tmp)
    tmp.mkdir(parents=True)
    with zipfile.ZipFile(bundle_zip) as zf:
        zf.extractall(path=tmp)
    return tmp


def build_incidence(data_dir: Path, out_dir: Path, run_we6: bool = True) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)

    # heuristic find CSVs
    h27_csv = find_csv(data_dir, ["h27", "vertices", "schlaefli"])
    n12_csv = find_csv(data_dir, ["n12", "steiner", "trihedra", "trihedron"])
    plane_edges_csv = find_csv(
        data_dir, ["plane_internal", "internal_tritangent", "edges"]
    )
    missing_csv = find_csv(data_dir, ["missing_9_tritangent", "missing_9", "missing9"])
    partition_csv = find_csv(data_dir, ["plane_point_triangles_partition", "partition"])

    print("Detected files:")
    print("  H27:", h27_csv)
    print("  N12:", n12_csv)
    print("  plane_edges:", plane_edges_csv)
    print("  missing:", missing_csv)
    print("  partition:", partition_csv)

    # H27 mapping: label -> info
    label_to_h27: Dict[str, Dict] = {}
    if h27_csv:
        heads, rows = read_csv(h27_csv)
        for r in rows:
            # try to find label and index columns
            label = None
            idx = None
            for k in r:
                if (
                    "label" in k.lower()
                    or "schlafli" in k.lower()
                    or "schlaefli" in k.lower()
                ):
                    label = r[k].strip()
                if "h27" in k.lower() or "vertex" in k.lower() or "id" == k.lower():
                    try:
                        idx = int(r[k])
                    except Exception:
                        pass
            if label:
                label_to_h27[label] = {"label": label, "h27_id": idx, "row": r}

    # N12 trihedra
    trihedra: Dict[str, Dict] = {}
    if n12_csv:
        heads, rows = read_csv(n12_csv)
        for r in rows:
            # find id and planes
            nid = None
            planes = None
            for k in r:
                kl = k.lower()
                if "n12" in kl or "trihedron" in kl or "id" == kl or "index" in kl:
                    if r[k].strip():
                        nid = r[k].strip()
                if (
                    "plane" in kl
                    or "tritangent" in kl
                    or "planes" in kl
                    or "triads" in kl
                ):
                    planes = canonical_split_list(r[k])
            if nid is None:
                # try to form id from row order
                nid = f"N12_{len(trihedra)}"
            trihedra[str(nid)] = {"id": str(nid), "planes": planes or [], "row": r}

    # plane edges / grades
    plane_edges = []
    if plane_edges_csv:
        heads, rows = read_csv(plane_edges_csv)
        for r in rows:
            plane_edges.append(r)

    # missing 9
    missing_planes: Set[str] = set()
    if missing_csv:
        heads, rows = read_csv(missing_csv)
        for r in rows:
            # heuristics: find a 'plane' or 'label' field or combine three line labels
            found = False
            for k in r:
                if (
                    "plane" in k.lower()
                    or "tritangent" in k.lower()
                    or "label" in k.lower()
                ):
                    vals = canonical_split_list(r[k])
                    for v in vals:
                        missing_planes.add(v)
                        found = True
            if not found:
                # maybe row lists three labels
                trip = [v for v in r.values() if v]
                if trip:
                    for v in trip:
                        missing_planes.add(v)

    # If partition file present, it may contain explicit tritangent planes by line labels
    plane_to_lines: Dict[str, List[str]] = {}
    if partition_csv:
        heads, rows = read_csv(partition_csv)
        for r in rows:
            plane_id = None
            lines = None
            for k in r:
                kl = k.lower()
                if "plane" in kl or "trihedron" in kl or "id" == kl:
                    plane_id = r[k].strip()
                if "points" in kl or "lines" in kl or "triple" in kl or "tri" in kl:
                    lines = canonical_split_list(r[k])
            if plane_id and lines:
                plane_to_lines[plane_id] = lines

    # If no partition found, attempt to use artifacts/e6_cubic_affine_heisenberg_model.json for triads (36)
    triads = []
    heis_path = ROOT / "artifacts" / "e6_cubic_affine_heisenberg_model.json"
    if not partition_csv and heis_path.exists():
        heis = json.loads(heis_path.read_text(encoding="utf-8"))
        triads = [
            tuple(sorted(tri))
            for item in heis.get("affine_u_lines", [])
            for tri in item.get("triads", [])
        ]
        # label triads by index
        for i, tri in enumerate(triads):
            lab = f"T{i:02d}"
            plane_to_lines[lab] = [str(x) for x in tri]

    # If N12 data used plane labels that aren't yet in plane_to_lines, keep them but unknown lines
    all_plane_labels = set(plane_to_lines.keys()) | {
        p for t in trihedra.values() for p in (t["planes"] or [])
    }

    # Build bipartite graph
    G = nx.Graph()
    for tid, t in trihedra.items():
        G.add_node(("trihedron", tid), bipartite=0, **{"planes": t["planes"]})
        for pl in t["planes"]:
            G.add_node(("plane", pl), bipartite=1)
            G.add_edge(("trihedron", tid), ("plane", pl))

    for pl, lines in plane_to_lines.items():
        if not G.has_node(("plane", pl)):
            G.add_node(("plane", pl), bipartite=1)
        # store lines
        G.nodes[("plane", pl)]["lines"] = lines
        G.nodes[("plane", pl)]["missing"] = pl in missing_planes

    # classify planes by Schläfli labels if available
    def classify_plane_lines(lines: List[str]) -> str:
        # classify by containing patterns E_ / L_ / Q_
        cats = [
            (
                None
                if not l
                else (
                    "E"
                    if l.upper().startswith("E")
                    else (
                        "L"
                        if l.upper().startswith("L")
                        else ("Q" if l.upper().startswith("Q") else "?")
                    )
                )
            )
            for l in lines
        ]
        counts = {"E": 0, "L": 0, "Q": 0, "?": 0}
        for c in cats:
            if c in counts:
                counts[c] += 1
        if counts["E"] == 1 and counts["L"] == 1 and counts["Q"] == 1:
            return "(E,L,Q)"
        if counts["L"] == 3:
            return "(L,L,L)"
        return "mixed"

    for n, d in list(G.nodes(data=True)):
        if n[0] == "plane":
            lines = d.get("lines") or []
            if lines:
                G.nodes[n]["type"] = classify_plane_lines(lines)
            else:
                G.nodes[n]["type"] = None

    # Save basic outputs
    out_trihedra = [
        {"id": tid, "planes": data["planes"]} for tid, data in trihedra.items()
    ]
    out_planes = []
    for node, data in G.nodes(data=True):
        if node[0] == "plane":
            out_planes.append(
                {
                    "id": node[1],
                    "lines": data.get("lines"),
                    "missing": bool(data.get("missing")),
                    "type": data.get("type"),
                }
            )

    (out_dir / "trihedra.json").write_text(
        json.dumps({"trihedra": out_trihedra}, indent=2), encoding="utf-8"
    )
    (out_dir / "tritangent_planes.json").write_text(
        json.dumps({"planes": out_planes}, indent=2), encoding="utf-8"
    )

    # write graph
    nx.write_gml(G, out_dir / "incidence_graph.gml")

    # Try to load/generate we6 action and compute orbits
    we6_path = ROOT / "artifacts" / "we6_signed_action_on_27.json"
    if we6_path.exists() or run_we6:
        # attempt to create if missing
        if not we6_path.exists():
            print(
                "we6 action missing; attempting to run export_we6_signed_action_on_27.py"
            )
            try:
                import importlib.util

                tool = _load_module(
                    ROOT / "tools" / "export_we6_signed_action_on_27.py",
                    "export_we6_signed_action_on_27",
                )
                tool.main()
            except Exception as e:
                print("Warning: failed to generate we6 action:", e)

        if we6_path.exists():
            act = json.loads(we6_path.read_text(encoding="utf-8"))
            gens = [
                g["permutation"]
                for g in act.get("generators", [])
                if g.get("permutation")
            ]

            # build triad index list if not built yet (from plane_to_lines mapping)
            # We will try to find mapping from plane labels to triads of 27-ids
            triad_list = []
            plane_label_to_tri_index = {}
            for i, (pl, lines) in enumerate(plane_to_lines.items()):
                # map lines to e6-ids or canonical positions if they look numeric
                tri = []
                for l in lines:
                    li = try_int(l)
                    if li is not None:
                        tri.append(li)
                    else:
                        # try to resolve by schlaefli label -> e6 id using artifacts/schlafli_e6id_to_w33_h27.json
                        mapf = ROOT / "artifacts" / "schlafli_e6id_to_w33_h27.json"
                        if mapf.exists():
                            mp = json.loads(mapf.read_text(encoding="utf-8"))
                            # mp contains maps; attempt label to e6id via canonical data
                            # Not implemented: user-supplied CSV should include numeric ids for convenience
                            pass
                if len(tri) == 3:
                    tri = tuple(sorted(tri))
                    plane_label_to_tri_index[pl] = i
                    triad_list.append(tri)
            # if triad_list non-empty and gens available, build triad perms
            triad_orbits = None
            if triad_list and gens:
                # induce permutations on triads
                triad_perm_gens = []
                for p in gens:
                    perm = list(range(len(triad_list)))
                    ok = True
                    for j, tri in enumerate(triad_list):
                        new_tri = tuple(sorted([p[v] for v in tri]))
                        if new_tri not in triad_list:
                            ok = False
                            break
                        perm[j] = triad_list.index(new_tri)
                    if ok:
                        triad_perm_gens.append(perm)

                def apply_perm_set(vec, perms):
                    res = set()
                    q = deque([tuple(vec)])
                    seen = {tuple(vec)}
                    while q:
                        cur = q.popleft()
                        res.add(cur)
                        for g in perms:
                            nxt = tuple(cur[g[j]] for j in range(len(cur)))
                            if nxt not in seen:
                                seen.add(nxt)
                                q.append(nxt)
                    return res

                triad_orbits = []
                for i in range(len(triad_list)):
                    vec = [0] * len(triad_list)
                    vec[i] = 1
                    orb = apply_perm_set(vec, triad_perm_gens)
                    triad_orbits.append(sorted([tuple(o) for o in orb]))

            # write orbit results
            outp = {"triad_list_count": len(triad_list)}
            if triad_orbits is not None:
                outp["triad_orbits_size_counts"] = {
                    str(len(set(tuple(o) for o in orb))): len(orb)
                    for orb in triad_orbits
                }
            (out_dir / "trihedron_tritangent_orbits.json").write_text(
                json.dumps(outp, indent=2), encoding="utf-8"
            )

    # Write a short markdown report
    md = []
    md.append("# Trihedron–Tritangent Bundle (auto-generated)")
    md.append("")
    md.append(f"- trihedra: `{len(trihedra)}`")
    n_planes = sum(1 for node in G.nodes() if node[0] == "plane")
    md.append(f"- tritangent planes (detected): `{n_planes}`")
    md.append(f"- missing_planes listed in CSV: `{len(missing_planes)}`")
    md.append("")
    md.append("## Plane type counts")
    types = defaultdict(int)
    for n, d in G.nodes(data=True):
        if n[0] == "plane":
            types[d.get("type") or "unknown"] += 1
    for k, v in sorted(types.items()):
        md.append(f"- {k}: `{v}`")
    md.append("")
    md.append(
        f"- JSON outputs: `{out_dir}/trihedra.json`, `{out_dir}/tritangent_planes.json`, `{out_dir}/incidence_graph.gml`"
    )
    (out_dir / "trihedron_tritangent_report.md").write_text(
        "\n".join(md), encoding="utf-8"
    )

    # Package output directory into a zip for easy download
    try:
        zip_path = out_dir.with_suffix(".zip")
        with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            for p in sorted(out_dir.rglob("*")):
                if p.is_file():
                    arcname = p.relative_to(out_dir.parent)
                    zf.write(p, arcname)
        print(f"Packaged bundle: {zip_path}")
    except Exception as e:
        print("Warning: failed to package bundle:", e)
    print("Wrote outputs to:", out_dir)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--bundle-zip", type=Path, default=None)
    p.add_argument("--bundle-dir", type=Path, default=None)
    p.add_argument("--out-dir", type=Path, default=DEFAULT_OUT)
    p.add_argument(
        "--no-we6",
        action="store_true",
        help="Don't attempt to generate/use W(E6) action",
    )
    args = p.parse_args()

    if args.bundle_zip and args.bundle_zip.exists():
        data_dir = extract_bundle(args.bundle_zip, args.out_dir / "extracted")
    elif args.bundle_dir and args.bundle_dir.exists():
        data_dir = args.bundle_dir
    else:
        raise RuntimeError(
            "Either --bundle-zip or --bundle-dir must point to existing data"
        )

    build_incidence(data_dir, args.out_dir, run_we6=not args.no_we6)


if __name__ == "__main__":
    main()
