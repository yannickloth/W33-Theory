#!/usr/bin/env python3
"""
Index the contents of the `More New Work/` drop folder.

This repo has accumulated many assistant-produced bundle zips. This script creates a
machine-readable inventory so downstream scripts can:
  - locate the newest bundle containing a given artifact,
  - diff bundle contents over time,
  - surface "what changed" without manually opening dozens of zips.

Outputs:
  - artifacts/more_new_work_index.json
  - artifacts/more_new_work_index.md
"""

from __future__ import annotations

import argparse
import hashlib
import json
import zipfile
from collections import Counter
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _utc_iso(ts: float) -> str:
    return datetime.fromtimestamp(ts, tz=timezone.utc).isoformat()


def _sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


@dataclass(frozen=True)
class ZipEntryInfo:
    name: str
    size: int
    compressed_size: int


@dataclass(frozen=True)
class FileInfo:
    relpath: str
    size: int
    mtime_utc: str
    sha256: str | None = None
    zip_total_entries: int | None = None
    zip_entries_listed: int | None = None
    zip_ext_counts: dict[str, int] | None = None
    zip_entries: list[ZipEntryInfo] | None = None


def _index_zip(path: Path, max_entries: int) -> tuple[list[ZipEntryInfo], Counter[str]]:
    entries: list[ZipEntryInfo] = []
    ext_counts: Counter[str] = Counter()
    with zipfile.ZipFile(path) as zf:
        infos = zf.infolist()
        for info in infos[:max_entries]:
            name = info.filename
            ext = Path(name).suffix.lower() or "(none)"
            ext_counts[ext] += 1
            entries.append(
                ZipEntryInfo(
                    name=name,
                    size=int(info.file_size),
                    compressed_size=int(info.compress_size),
                )
            )
        # Count remaining extensions without storing all names.
        for info in infos[max_entries:]:
            ext = Path(info.filename).suffix.lower() or "(none)"
            ext_counts[ext] += 1
    return entries, ext_counts


def _md_table(rows: list[list[str]], headers: list[str]) -> str:
    out = []
    out.append("| " + " | ".join(headers) + " |")
    out.append("| " + " | ".join(["---"] * len(headers)) + " |")
    for r in rows:
        out.append("| " + " | ".join(r) + " |")
    return "\n".join(out)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument(
        "--dir",
        type=Path,
        default=ROOT / "More New Work",
        help="Folder to index (default: repo-root/'More New Work').",
    )
    p.add_argument(
        "--max-zip-entries",
        type=int,
        default=200,
        help="Max entries to list per zip (counts still cover full zip).",
    )
    p.add_argument(
        "--hash",
        action="store_true",
        help="Compute sha256 of each file (slower, but deterministic inventory).",
    )
    args = p.parse_args()

    base: Path = args.dir
    if not base.exists() or not base.is_dir():
        raise SystemExit(f"Directory not found: {base}")

    file_infos: list[FileInfo] = []
    for path in sorted(base.rglob("*")):
        if not path.is_file():
            continue
        rel = str(path.relative_to(ROOT)).replace("\\", "/")
        st = path.stat()
        sha = _sha256_file(path) if args.hash else None
        info_kwargs: dict[str, object] = {
            "relpath": rel,
            "size": int(st.st_size),
            "mtime_utc": _utc_iso(st.st_mtime),
            "sha256": sha,
        }
        if path.suffix.lower() == ".zip":
            entries, ext_counts = _index_zip(path, max_entries=args.max_zip_entries)
            with zipfile.ZipFile(path) as zf:
                total = len(zf.infolist())
            info_kwargs.update(
                {
                    "zip_total_entries": total,
                    "zip_entries_listed": len(entries),
                    "zip_ext_counts": dict(ext_counts),
                    "zip_entries": entries,
                }
            )
        file_infos.append(FileInfo(**info_kwargs))

    out_json = ROOT / "artifacts" / "more_new_work_index.json"
    out_md = ROOT / "artifacts" / "more_new_work_index.md"
    out_json.parent.mkdir(parents=True, exist_ok=True)

    payload = {
        "generated_utc": datetime.now(tz=timezone.utc).isoformat(),
        "root": str(ROOT).replace("\\", "/"),
        "indexed_dir": str(base).replace("\\", "/"),
        "max_zip_entries": int(args.max_zip_entries),
        "hashes_included": bool(args.hash),
        "files": [asdict(fi) for fi in file_infos],
    }
    out_json.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

    zip_files = [fi for fi in file_infos if fi.relpath.lower().endswith(".zip")]
    nonzip = [fi for fi in file_infos if not fi.relpath.lower().endswith(".zip")]

    md: list[str] = []
    md.append("# More New Work index\n")
    md.append(f"- Generated (UTC): `{payload['generated_utc']}`")
    md.append(f"- Indexed dir: `{payload['indexed_dir']}`")
    md.append(f"- Zips: `{len(zip_files)}`  Non-zips: `{len(nonzip)}`\n")

    if zip_files:
        rows: list[list[str]] = []
        for fi in zip_files:
            ext_top = ""
            if fi.zip_ext_counts:
                top = sorted(fi.zip_ext_counts.items(), key=lambda kv: (-kv[1], kv[0]))[
                    :6
                ]
                ext_top = ", ".join([f"{k}:{v}" for k, v in top])
            rows.append(
                [
                    f"`{fi.relpath}`",
                    str(fi.size),
                    fi.mtime_utc,
                    str(fi.zip_total_entries or 0),
                    ext_top,
                ]
            )
        md.append("## Zip bundles\n")
        md.append(
            _md_table(
                rows,
                headers=["Zip", "Bytes", "MTime (UTC)", "Entries", "Top extensions"],
            )
        )
        md.append("")

    if nonzip:
        rows2: list[list[str]] = []
        for fi in nonzip[:80]:
            rows2.append([f"`{fi.relpath}`", str(fi.size), fi.mtime_utc])
        md.append("## Non-zip files (first 80)\n")
        md.append(_md_table(rows2, headers=["Path", "Bytes", "MTime (UTC)"]))
        if len(nonzip) > 80:
            md.append(f"\n(Truncated; total non-zip files: {len(nonzip)})")
        md.append("")

    out_md.write_text("\n".join(md), encoding="utf-8")
    print(f"Wrote: {out_json}")
    print(f"Wrote: {out_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
