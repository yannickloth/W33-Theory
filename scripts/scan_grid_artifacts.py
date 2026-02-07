#!/usr/bin/env python3
"""Scan a GitHub Actions workflow run's artifacts for W33→E8 embedding results.

Usage (in GitHub Actions):
  python scripts/scan_grid_artifacts.py --run-id $RUN_ID --repo $GITHUB_REPOSITORY --run-url $RUN_URL --open-issue

Behavior:
- Downloads artifacts for the run that match prefix `PART_CVII_e8_embedding_sage`.
- Extracts any JSON artifact named `PART_CVII_e8_embedding_sage.json` (or similar).
- If any artifact contains "found": true, opens a GitHub issue (labelled `e8-embedding-found`) with details.

Requires: requests (install via pip)
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
import zipfile
from typing import Dict, List

try:
    import requests
except Exception:
    raise SystemExit("This script requires the 'requests' package. Please install it before running (pip install requests).")


def get_headers(token: str) -> Dict[str, str]:
    return {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github+json",
        "User-Agent": "scan-grid-artifacts-script",
    }


def list_artifacts(repo: str, run_id: int, token: str):
    base = f"https://api.github.com/repos/{repo}"
    url = f"{base}/actions/runs/{run_id}/artifacts"
    resp = requests.get(url, headers=get_headers(token), timeout=60)
    resp.raise_for_status()
    return resp.json().get("artifacts", [])


def download_artifact_zip(repo: str, artifact_id: int, token: str, dest_path: str):
    base = f"https://api.github.com/repos/{repo}"
    url = f"{base}/actions/artifacts/{artifact_id}/zip"
    with requests.get(url, headers=get_headers(token), stream=True, timeout=120) as r:
        r.raise_for_status()
        with open(dest_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)


def ensure_label(repo: str, label: str, token: str):
    base = f"https://api.github.com/repos/{repo}"
    lbl_url = f"{base}/labels/{label}"
    r = requests.get(lbl_url, headers=get_headers(token))
    if r.status_code == 200:
        return True
    # create label
    create_url = f"{base}/labels"
    data = {"name": label, "color": "b60205", "description": "Detected W33→E8 embedding found"}
    r2 = requests.post(create_url, headers=get_headers(token), json=data)
    return r2.status_code in (200, 201)


def issue_exists(repo: str, label: str, run_id: int, artifact_name: str, token: str) -> bool:
    base = f"https://api.github.com/repos/{repo}"
    # list open issues (paginated) and search for run_id and artifact name in body
    url = f"{base}/issues?state=open&labels={label}&per_page=100"
    r = requests.get(url, headers=get_headers(token), timeout=30)
    if r.status_code != 200:
        return False
    for iss in r.json():
        body = iss.get("body", "") or ""
        if str(run_id) in body and artifact_name in body:
            print("Existing issue found:", iss.get("html_url"))
            return True
    return False


def create_issue(repo: str, title: str, body: str, labels: List[str], token: str):
    base = f"https://api.github.com/repos/{repo}"
    url = f"{base}/issues"
    data = {"title": title, "body": body, "labels": labels}
    r = requests.post(url, headers=get_headers(token), json=data, timeout=30)
    r.raise_for_status()
    return r.json().get("html_url")


def scan_run_for_found(repo: str, run_id: int, run_url: str, token: str, artifact_prefix: str = "PART_CVII_e8_embedding_sage", issue_label: str = "e8-embedding-found", open_issue: bool = True, mention: str | None = None):
    artifacts = list_artifacts(repo, run_id, token)
    print(f"Found {len(artifacts)} artifacts for run {run_id}")

    for art in artifacts:
        name = art.get("name", "")
        if not name.startswith(artifact_prefix):
            continue
        aid = art.get("id")
        print(f"Inspecting artifact: {name} (id={aid})")
        with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as tmp:
            tmpzip = tmp.name
        try:
            download_artifact_zip(repo, aid, token, tmpzip)
        except Exception as ex:
            print(f"Failed to download artifact {name}: {ex}")
            try:
                os.unlink(tmpzip)
            except Exception:
                pass
            continue

        try:
            with zipfile.ZipFile(tmpzip, "r") as z:
                namelist = z.namelist()
                # find the JSON file of interest
                json_files = [f for f in namelist if f.endswith('.json') and 'PART_CVII_e8_embedding_sage' in f]
                if not json_files:
                    json_files = [f for f in namelist if f.endswith('.json')]
                for jf in json_files:
                    print(f"Reading {jf} from artifact {name}")
                    with z.open(jf) as fh:
                        try:
                            data = json.load(fh)
                        except Exception as ex:
                            print(f"Failed to parse JSON {jf}: {ex}")
                            continue

                        # Helper: compute best_assigned value from various artifact schemas
                        def extract_best_assigned(d):
                            vals = []
                            try:
                                if isinstance(d.get('best'), dict):
                                    m = d.get('best', {}).get('max_assigned')
                                    if isinstance(m, int):
                                        vals.append(m)
                            except Exception:
                                pass
                            for k in ('assigned_vertices', 'best_assigned', 'assigned'):
                                v = d.get(k)
                                if isinstance(v, int):
                                    vals.append(v)
                            return max(vals) if vals else None

                        best_assigned = extract_best_assigned(data)

                        if data.get("found"):
                            print(f"FOUND embedding in artifact {name} (run {run_id})")
                            if not args.no_issue and args.open_issue:
                                # make sure label exists
                                ensured = ensure_label(repo, args.issue_label, token)
                                if not ensured:
                                    print(f"Warning: could not create or verify label {args.issue_label}")
                                # avoid duplicate issues
                                if not issue_exists(repo, args.issue_label, run_id, name, token):
                                    title = f"W33→E8 embedding FOUND (run {run_id}, artifact {name})"
                                    body = f"An embedding was reported by the grid run [view run]({run_url}) in artifact **{name}**.\n\n"
                                    if args.mention:
                                        body += f"cc {args.mention}\n\n"
                                    body += (
                                        "Summary of result:\n\n```\n"
                                        + json.dumps({"found": data.get("found"), "time_seconds": data.get("time_seconds"), "best": data.get("best")}, indent=2)
                                        + "\n```\n\nFull artifact JSON:\n\n```\n"
                                        + json.dumps(data, indent=2)
                                        + "\n```\n"
                                    )
                                    try:
                                        url = create_issue(repo, title, body, [args.issue_label], token)
                                        print("Created issue:", url)
                                    except Exception as ex:
                                        print("Failed to create issue:", ex)
                                else:
                                    print("Issue already exists for this artifact; skipping creation.")
                            # save partial if requested (for found embedding we also save full artifact)
                            if args.save_partial:
                                os.makedirs(os.path.dirname(args.save_partial), exist_ok=True)
                                with open(args.save_partial, 'w', encoding='utf-8') as f:
                                    json.dump(data, f, indent=2)
                                print(f"Saved artifact JSON to {args.save_partial}")
                            # return success
                            return True

                        # check for large partials
                        if best_assigned is not None and best_assigned >= args.partial_threshold:
                            print(f"Large partial detected in {name}: best_assigned={best_assigned} (run {run_id})")
                            if args.save_partial:
                                os.makedirs(os.path.dirname(args.save_partial), exist_ok=True)
                                with open(args.save_partial, 'w', encoding='utf-8') as f:
                                    json.dump(data, f, indent=2)
                                print(f"Saved partial JSON to {args.save_partial}")
                            # open issue for partials
                            if not args.no_issue and args.open_issue:
                                ensured = ensure_label(repo, args.partial_label, token)
                                if not ensured:
                                    print(f"Warning: could not create or verify label {args.partial_label}")
                                if not issue_exists(repo, args.partial_label, run_id, name, token):
                                    title = f"W33→E8 large partial found: max_assigned={best_assigned} (run {run_id}, artifact {name})"
                                    body = f"A large partial (max_assigned={best_assigned}) was reported by the grid run [view run]({run_url}) in artifact **{name}**.\n\n"
                                    if args.mention:
                                        body += f"cc {args.mention}\n\n"
                                    body += "Partial JSON:\n\n```
" + json.dumps(data, indent=2) + "\n```
"
                                    try:
                                        url = create_issue(repo, title, body, [args.partial_label], token)
                                        print("Created issue:", url)
                                    except Exception as ex:
                                        print("Failed to create issue:", ex)
                                else:
                                    print("Issue already exists for this partial artifact; skipping creation.")
                            return True
                # end for json files
        finally:
            try:
                os.unlink(tmpzip)
            except Exception:
                pass
    print("No 'found: true' artifacts discovered for this run.")
    return False


def main(argv: List[str] | None = None):
    parser = argparse.ArgumentParser(description="Scan grid run artifacts for embedding 'found: true' or large partials.")
    parser.add_argument("--run-id", type=int, required=True, help="Workflow run id to inspect")
    parser.add_argument("--repo", type=str, default=os.environ.get("GITHUB_REPOSITORY"), help="Repository in 'owner/repo' format")
    parser.add_argument("--run-url", type=str, default=None, help="URL to the run (for inclusion in issue body)")
    parser.add_argument("--artifact-prefix", type=str, default="PART_CVII_e8_embedding_sage", help="Prefix of artifact names to inspect")
    parser.add_argument("--issue-label", type=str, default="e8-embedding-found", help="Label to apply to created issues when found")
    parser.add_argument("--partial-label", type=str, default="e8-embedding-partial", help="Label to apply to created issues when a large partial is found")
    parser.add_argument("--open-issue", action="store_true", help="Open a GitHub issue when a 'found: true' is observed")
    parser.add_argument("--partial-threshold", type=int, default=100, help="Trigger a partial alert when best.max_assigned >= threshold")
    parser.add_argument("--save-partial", type=str, default=None, help="Path to save the partial JSON when threshold is exceeded")
    parser.add_argument("--no-issue", action="store_true", help="Do not open an issue even if a match is detected")
    parser.add_argument("--mention", type=str, default=os.environ.get("MENTION"), help="Optional mention (e.g., @username) to add to issue body")
    args = parser.parse_args(argv)

    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        print("Error: GITHUB_TOKEN environment variable is required to call GitHub API.")
        return 2

    if not args.repo:
        print("Error: --repo must be provided (or GITHUB_REPOSITORY env var set)")
        return 2

    found = scan_run_for_found(args.repo, args.run_id, args.run_url or f"https://github.com/{args.repo}/actions/runs/{args.run_id}", token, artifact_prefix=args.artifact_prefix, issue_label=args.issue_label, open_issue=args.open_issue, mention=args.mention)

    return 0 if found else 1


if __name__ == "__main__":
    raise SystemExit(main())
