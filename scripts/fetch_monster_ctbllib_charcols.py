"""Fetch CTblLib and export minimal Monster character columns to JSON.

This script downloads a pinned CTblLib source archive (used by GAP's CTblLib
package), extracts the Monster ordinary character table `M` from
`ctomonst.tbl`, and exports a small subset of integer columns needed for
offline, deterministic tests and analyses:

  - 1A (degree)
  - 2A
  - 3B
  - 29A
  - 41A

The resulting file is written to `data/monster_ctbllib_charcols.json`.

Run:
  .venv\\Scripts\\python.exe -X utf8 scripts\\fetch_monster_ctbllib_charcols.py
"""

from __future__ import annotations

import ast
import json
import re
import tarfile
import urllib.request
from pathlib import Path

CTBLLIB_VERSION = "1.3.11"
CTBLLIB_URL = (
    "https://launchpad.net/ubuntu/+archive/primary/+sourcefiles/"
    "gap-ctbllib/1.3.11-1/gap-ctbllib_1.3.11.orig.tar.xz"
)


def _download(url: str, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.exists() and dst.stat().st_size > 0:
        return
    with urllib.request.urlopen(url, timeout=60) as r:  # nosec - pinned URL
        dst.write_bytes(r.read())


def _extract_member(archive: Path, member: str, out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    with tarfile.open(archive, mode="r:xz") as tf:
        m = tf.getmember(member)
        tf.extract(m, path=out_dir)  # nosec - member path is fixed
    return out_dir / member


def _parse_mot_args(tbl_text: str, table_id: str) -> list[str]:
    start = tbl_text.find(f'MOT("{table_id}"')
    if start < 0:
        raise ValueError(f'MOT("{table_id}") not found')

    j = tbl_text.find(f'"{table_id}"', tbl_text.find("(", start))
    j = tbl_text.find(",", j)
    pos = j + 1

    args: list[str] = []
    while len(args) < 5:
        while pos < len(tbl_text) and tbl_text[pos].isspace():
            pos += 1
        if pos >= len(tbl_text) or tbl_text[pos] != "[":
            raise ValueError(f"Unexpected token at {pos}: {tbl_text[pos:pos+20]!r}")

        depth = 0
        buf: list[str] = []
        in_str = False
        escape = False
        while pos < len(tbl_text):
            ch = tbl_text[pos]
            buf.append(ch)
            if in_str:
                if escape:
                    escape = False
                elif ch == "\\":
                    escape = True
                elif ch == '"':
                    in_str = False
            else:
                if ch == '"':
                    in_str = True
                elif ch == "[":
                    depth += 1
                elif ch == "]":
                    depth -= 1
                    if depth == 0:
                        pos += 1
                        break
            pos += 1

        args.append("".join(buf))
        while pos < len(tbl_text) and tbl_text[pos].isspace():
            pos += 1
        if pos < len(tbl_text) and tbl_text[pos] == ",":
            pos += 1

    return args


def _split_top_level_list_items(list_text: str) -> list[str]:
    """Split a GAP list string into top-level items (handles empty items)."""
    if not list_text.startswith("["):
        raise ValueError("expected list")

    depth = 1
    items: list[str] = []
    buf: list[str] = []
    in_str = False
    escape = False
    for ch in list_text[1:]:
        if in_str:
            buf.append(ch)
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == '"':
                in_str = False
            continue

        if ch == '"':
            in_str = True
            buf.append(ch)
            continue

        if ch == "[":
            depth += 1
        elif ch == "]":
            depth -= 1

        if ch == "," and depth == 1:
            items.append("".join(buf).strip())
            buf = []
            continue

        if depth == 0:
            items.append("".join(buf).strip())
            break

        buf.append(ch)

    return items


def _extract_cols(row_str: str, cols: list[int]) -> dict:
    if row_str.startswith("[GALOIS"):
        m = re.match(r"\[GALOIS,\[(\d+),(\d+)\]\]$", row_str)
        if not m:
            raise ValueError("bad GALOIS row")
        return {"GALOIS": (int(m.group(1)), int(m.group(2)))}

    if not (row_str.startswith("[") and row_str.endswith("]")):
        raise ValueError("bad row")

    cols_set = set(cols)
    out: dict[int, str] = {}
    col = 1
    token: list[str] = []
    paren = 0
    for ch in row_str[1:-1]:
        if ch == "(":
            paren += 1
        elif ch == ")":
            paren -= 1
        if ch == "," and paren == 0:
            if col in cols_set:
                out[col] = "".join(token).strip()
            token = []
            col += 1
            continue
        token.append(ch)
    if col in cols_set:
        out[col] = "".join(token).strip()
    return out


def build_monster_charcols_from_ctbllib(ctomonst_tbl: Path) -> dict[str, object]:
    txt = ctomonst_tbl.read_text(encoding="utf-8", errors="ignore")
    args = _parse_mot_args(txt, "M")

    centralizers = ast.literal_eval(args[1].replace("\n", " "))
    if not isinstance(centralizers, list) or len(centralizers) != 194:
        raise ValueError("unexpected centralizers list")

    pow_items = _split_top_level_list_items(args[2])
    # exponent p lives at index p-1 in the list (index 0 is the empty '1' slot)
    pm29 = ast.literal_eval(pow_items[28].replace("\n", " "))
    if not isinstance(pm29, list) or len(pm29) != 194:
        raise ValueError("unexpected powermap(29)")

    idx29_candidates = [
        i + 1 for i, (c, p) in enumerate(zip(centralizers, pm29)) if c == 87 and p == 1
    ]
    if idx29_candidates != [97]:
        raise ValueError(f"unexpected 29A candidates: {idx29_candidates}")
    idx29 = 97

    pm41 = ast.literal_eval(pow_items[40].replace("\n", " "))
    if not isinstance(pm41, list) or len(pm41) != 194:
        raise ValueError("unexpected powermap(41)")

    idx41_candidates = [
        i + 1 for i, (c, p) in enumerate(zip(centralizers, pm41)) if c == 41 and p == 1
    ]
    if idx41_candidates != [127]:
        raise ValueError(f"unexpected 41A candidates: {idx41_candidates}")
    idx41 = 127

    rows = _split_top_level_list_items(args[3])
    if len(rows) != 194:
        raise ValueError(f"expected 194 irreps, got {len(rows)}")

    cols_needed = [1, 2, 5, idx29, idx41]
    extracted = [_extract_cols(r, cols_needed) for r in rows]

    # Expand GALOIS rows: for these columns (orders 2,3,29), values are integers,
    # so the Galois action is trivial and we can copy the base row values.
    for i, d in enumerate(extracted, start=1):
        if "GALOIS" in d:
            base, _k = d["GALOIS"]
            extracted[i - 1] = extracted[base - 1].copy()

    irreps: list[dict[str, int]] = []
    for i, d in enumerate(extracted, start=1):
        irreps.append(
            {
                "index": i,
                "deg": int(d[1]),
                "2A": int(d[2]),
                "3B": int(d[5]),
                "29A": int(d[idx29]),
                "41A": int(d[idx41]),
            }
        )

    return {
        "source": {
            "ctbllib_version": CTBLLIB_VERSION,
            "source_archive_url": CTBLLIB_URL,
            "table_file": "ctbllib-1.3.11/data/ctomonst.tbl",
            "table_id": "M",
        },
        "classes": {
            "1A": {"ctbllib_index": 1},
            "2A": {"ctbllib_index": 2},
            "3B": {"ctbllib_index": 5},
            "29A": {"ctbllib_index": idx29},
            "41A": {"ctbllib_index": idx41},
        },
        "n_irreps": len(irreps),
        "irreps": irreps,
    }


def main() -> None:
    archive = (
        Path("outputs") / "ctbllib_cache" / f"gap-ctbllib_{CTBLLIB_VERSION}.tar.xz"
    )
    extracted_root = Path("outputs") / "ctbllib_cache"

    _download(CTBLLIB_URL, archive)
    member = f"ctbllib-{CTBLLIB_VERSION}/data/ctomonst.tbl"
    tbl_path = _extract_member(archive, member, extracted_root)

    payload = build_monster_charcols_from_ctbllib(tbl_path)
    out_path = Path("data") / "monster_ctbllib_charcols.json"
    out_path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(f"Wrote {out_path} ({out_path.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
