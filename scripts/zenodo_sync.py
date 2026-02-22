#!/usr/bin/env python3
"""
Simple utility to find a Zenodo DOI for a GitHub release and insert it into
repository files (release draft, README, outreach). Intended to be run manually
or from CI (workflow_dispatch / scheduled).

Usage (dry-run):
  python scripts/zenodo_sync.py --repo wilcompute/W33-Theory --tag v2026-02-15-qec-mlut

Apply changes:
  python scripts/zenodo_sync.py --repo wilcompute/W33-Theory --tag v2026-02-15-qec-mlut --apply

CI: run with --apply and let the workflow commit/push the changes.
"""
import argparse
import json
import os
import re
import sys
from pathlib import Path
from urllib import parse, request

import requests

ZENODO_SEARCH_URL = "https://zenodo.org/api/records/"


def zenodo_search_by_repo_and_tag(repo_full: str, tag: str, max_results: int = 100):
    """Search Zenodo for records referencing the GitHub repo and tag.

    This function is resilient to HTTP errors and tries multiple query forms:
    1) search by repository URL, 2) fallback search by the release tag.
    Returns the first matching record dict or None.
    """
    queries = [repo_full, tag]

    for q in queries:
        try:
            query = parse.quote(q)
            url = f"{ZENODO_SEARCH_URL}?q={query}&size={max_results}"
            with request.urlopen(url, timeout=30) as resp:
                data = json.load(resp)
        except Exception:
            # Network/HTTP error from Zenodo API — skip this query and continue
            continue

        for hit in data.get("hits", {}).get("hits", []):
            md = hit.get("metadata", {})
            # quick text match for tag anywhere in the returned JSON
            text = json.dumps(hit)
            if tag in text:
                return hit
            # check related_identifiers for a release/tree/tag reference
            for rid in md.get("related_identifiers", []) or []:
                ident = rid.get("identifier", "")
                if repo_full in ident and tag in ident:
                    return hit
            # metadata.version may match the tag
            if md.get("version") and md.get("version").lower() == tag.lower():
                return hit
            # check custom.code:codeRepository for repo reference
            custom = md.get("custom", {}) or {}
            code_repo = custom.get("code:codeRepository")
            if code_repo and repo_full in code_repo:
                if tag in text:
                    return hit
    return None


def insert_doi_into_release_draft(draft_path: str, tag: str, doi_url: str) -> bool:
    if not os.path.exists(draft_path):
        return False
    with open(draft_path, "r", encoding="utf-8") as f:
        txt = f.read()

    # If DOI already present, no-op
    if doi_url in txt:
        return False

    # Insert DOI under "Post-release next steps" if present, else append to top
    anchor = "Post-release next steps"
    insert_text = f"\n- Zenodo DOI: {doi_url}  \n"
    if anchor in txt:
        # find anchor and the following list; insert DOI as the first bullet after the anchor
        parts = txt.split(anchor)
        head, tail = parts[0], parts[1]
        # insert DOI at start of tail (after the anchor heading)
        new_tail = anchor + tail
        # attempt to put DOI right after the anchor line-break
        new_txt = head + anchor + "\n" + insert_text + tail
    else:
        new_txt = f"Zenodo DOI: {doi_url}\n\n" + txt

    with open(draft_path, "w", encoding="utf-8") as f:
        f.write(new_txt)
    return True


def insert_doi_into_readme(readme_path: str, tag: str, doi_url: str) -> bool:
    if not os.path.exists(readme_path):
        return False
    with open(readme_path, "r", encoding="utf-8") as f:
        txt = f.read()

    if doi_url in txt:
        return False

    # Try to find the release badge link for the tag and append the DOI beside it
    pattern = re.escape(tag)
    if re.search(pattern, txt):
        # Simple approach: append a DOI line right after the first occurrence of the tag
        new_txt = re.sub(f"({pattern})", f"\\1 — Zenodo: {doi_url}", txt, count=1)
    else:
        # Fallback: add DOI under the title (first header)
        new_txt = txt
        lines = new_txt.splitlines()
        for i, line in enumerate(lines):
            if line.strip().startswith("# "):
                lines.insert(i + 1, f"**Zenodo DOI:** {doi_url}")
                new_txt = "\n".join(lines)
                break
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(new_txt)
    return True


def insert_doi_into_outreach(outreach_paths: list, doi_url: str) -> bool:
    changed = False
    for p in outreach_paths:
        if not os.path.exists(p):
            continue
        with open(p, "r", encoding="utf-8") as f:
            txt = f.read()
        if doi_url in txt:
            continue
        # Append DOI to the top of the file under title or at the end
        new_txt = txt + f"\n\nDOI: {doi_url}\n"
        with open(p, "w", encoding="utf-8") as f:
            f.write(new_txt)
        changed = True
    return changed


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", required=True, help="GitHub repo (owner/repo)")
    parser.add_argument("--tag", required=True, help="Release tag to look for")
    parser.add_argument("--apply", action="store_true", help="Write changes to files")
    parser.add_argument(
        "--commit", action="store_true", help="Create a local git commit after changes"
    )
    parser.add_argument(
        "--publish",
        action="store_true",
        help="Create & publish a Zenodo deposition using ZENODO_TOKEN (CI)",
    )
    args = parser.parse_args()

    repo = args.repo
    tag = args.tag
    repo_url = f"https://github.com/{repo}"

    doi_url = None

    # If requested, try to create/publish a deposition first (idempotent)
    if args.publish:
        print(
            f"Attempting to publish {repo_url} (tag={tag}) to Zenodo using ZENODO_TOKEN..."
        )
        published = publish_release_to_zenodo(repo, tag)
        if published:
            doi_url = (
                published
                if published.startswith("http")
                else f"https://doi.org/{published}"
            )
            print(f"Published DOI: {doi_url}")
        else:
            print("Publish attempt did not create a DOI; will search Zenodo instead.")

    # Search Zenodo (if needed)
    if not doi_url:
        print(f"Searching Zenodo for records referencing {repo_url} (tag={tag})...")
        hit = zenodo_search_by_repo_and_tag(repo_url, tag)
        if not hit:
            print("No Zenodo record found for that repo+tag (yet).")
            sys.exit(0)
        doi = hit.get("doi") or hit.get("metadata", {}).get("doi")
        if not doi:
            print(
                "Found Zenodo record but DOI not present in API response (unexpected)."
            )
            print(json.dumps(hit, indent=2)[:2000])
            sys.exit(1)
        doi_url = f"https://doi.org/{doi}" if not doi.startswith("http") else doi
        print(f"Found Zenodo DOI: {doi_url}")
    else:
        print(f"Using DOI from publish step: {doi_url}")

    if not args.apply:
        print("Dry-run mode (use --apply to modify files).")
        print(f"Would insert DOI into: RELEASES/DRAFT_{tag}.md, README.md, outreach/*")
        sys.exit(0)

    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    changed_any = False

    draft_path = os.path.join(repo_root, "RELEASES", f"DRAFT_{tag}.md")
    if insert_doi_into_release_draft(draft_path, tag, doi_url):
        print(f"Updated {draft_path}")
        changed_any = True
    else:
        print(f"No change to {draft_path}")

    readme_path = os.path.join(repo_root, "README.md")
    if insert_doi_into_readme(readme_path, tag, doi_url):
        print(f"Updated {readme_path}")
        changed_any = True
    else:
        print(f"No change to {readme_path}")

    outreach_files = [
        os.path.join(repo_root, "outreach", "social_posts.md"),
        os.path.join(repo_root, "outreach", "blog_post.md"),
    ]
    if insert_doi_into_outreach(outreach_files, doi_url):
        print("Updated outreach files")
        changed_any = True
    else:
        print("No change to outreach files")

    if changed_any and args.commit:
        try:
            import subprocess

            subprocess.check_call(
                [
                    "git",
                    "add",
                    "RELEASES/" + f"DRAFT_{tag}.md",
                    "README.md",
                    "outreach/social_posts.md",
                    "outreach/blog_post.md",
                ],
                cwd=repo_root,
            )
            subprocess.check_call(
                ["git", "commit", "-m", f"Add Zenodo DOI for {tag} (automated)"],
                cwd=repo_root,
            )
            print("Created local git commit (files staged and committed).")
        except Exception as e:
            print("Failed to create git commit:", e)

    if not changed_any:
        print("No files changed.")
    else:
        print("Files updated. If running in CI please commit & push changes.")


def publish_release_to_zenodo(repo, tag, zenodo_host=None):
    """Create and publish a Zenodo deposition for the given GitHub release.
    Returns the DOI string on success, or None on failure. This function is idempotent:
    it first searches Zenodo for an existing record by repo+tag and will return any found DOI.
    Requires ZENODO_TOKEN in the environment.
    """
    zenodo_host = zenodo_host or os.environ.get("ZENODO_HOST", "https://zenodo.org")
    zenodo_token = os.environ.get("ZENODO_TOKEN")
    if not zenodo_token:
        print("ZENODO_TOKEN not set; cannot publish to Zenodo from CI.")
        return None

    # check for existing record first
    repo_url = f"https://github.com/{repo}"
    existing = zenodo_search_by_repo_and_tag(repo_url, tag)
    if existing:
        doi = existing.get("doi") or existing.get("metadata", {}).get("doi")
        if doi:
            print(f"Existing Zenodo DOI found: {doi}")
            return doi

    headers = {"Authorization": f"Bearer {zenodo_token}"}
    session = requests.Session()
    session.headers.update(headers)

    # create a new draft deposition
    resp = session.post(f"{zenodo_host}/api/deposit/depositions", json={})
    resp.raise_for_status()
    dep = resp.json()
    dep_id = dep.get("id")
    print("Created Zenodo draft id=", dep_id)

    # download release assets from GitHub (if any) and upload to Zenodo draft
    gh_headers = {"Accept": "application/vnd.github+json"}
    gh_token = os.environ.get("GITHUB_TOKEN")
    if gh_token:
        gh_headers["Authorization"] = f"token {gh_token}"
    rel = requests.get(
        f"https://api.github.com/repos/{repo}/releases/tags/{tag}", headers=gh_headers
    )
    rel.raise_for_status()
    rj = rel.json()
    asset_paths = []
    for a in rj.get("assets", []):
        url = a.get("browser_download_url")
        fname = Path(url).name
        print("Downloading", url)
        with requests.get(url, headers=gh_headers, stream=True) as r:
            r.raise_for_status()
            with open(fname, "wb") as fh:
                for chunk in r.iter_content(32768):
                    fh.write(chunk)
        asset_paths.append(fname)

    for p in asset_paths:
        print("Uploading", p)
        with open(p, "rb") as fh:
            files = {"file": fh}
            up = session.post(
                f"{zenodo_host}/api/deposit/depositions/{dep_id}/files", files=files
            )
            up.raise_for_status()

    # set metadata
    metadata = {
        "metadata": {
            "title": f"Pillar-45 — GF(3) QEC primitives + MLUT ({tag})",
            "upload_type": "software",
            "publication_date": "2026-02-15",
            "creators": [{"name": "Wilj D."}],
            "description": f"Pillar-45 release (GitHub): https://github.com/{repo}/releases/tag/{tag}",
            "version": tag,
            "license": "MIT",
            "related_identifiers": [
                {
                    "identifier": f"https://github.com/{repo}/releases/tag/{tag}",
                    "relation": "isSupplementTo",
                    "scheme": "url",
                }
            ],
        }
    }
    setm = session.put(f"{zenodo_host}/api/deposit/depositions/{dep_id}", json=metadata)
    setm.raise_for_status()

    # publish
    pub = session.post(
        f"{zenodo_host}/api/deposit/depositions/{dep_id}/actions/publish"
    )
    pub.raise_for_status()
    pr = pub.json()
    doi = pr.get("doi") or pr.get("metadata", {}).get("doi")
    if doi:
        print("Published — DOI:", doi)
        return doi
    print("Publish response did not contain DOI:", pr)
    return None


if __name__ == "__main__":
    main()
