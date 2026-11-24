#!/usr/bin/env python3
"""Check that every system repo carries an exact copy of the hub base.

Usage: python3 tools/check_base_copies.py <repo folder> [<repo folder> ...]
Prints OK per repo, or the files that differ, are missing or are extra. Exit code 1 on any drift.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from base_files import MANIFEST_PATH, build_manifest, iter_base_files, read_version, sha256  # noqa: E402

HUB = Path(__file__).resolve().parent.parent


def check(repo: Path, hub: Path = HUB) -> list[str]:
    expected = build_manifest(hub, read_version(hub))
    problems: list[str] = []
    mp = repo / MANIFEST_PATH
    if not mp.exists():
        return [f"missing {MANIFEST_PATH} (run tools/sync_base.py)"]
    recorded = json.loads(mp.read_text())
    if recorded.get("base_version") != expected["base_version"]:
        problems.append(f"base version {recorded.get('base_version')} differs from hub {expected['base_version']}")
    present = dict(iter_base_files(repo))
    for rel, digest in expected["files"].items():
        p = present.get(rel)
        if p is None:
            problems.append(f"missing {rel}")
        elif sha256(p) != digest:
            problems.append(f"changed {rel}")
    for rel in present:
        if rel not in expected["files"]:
            problems.append(f"extra {rel}")
    return problems


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("repos", nargs="+", type=Path)
    bad = 0
    for repo in ap.parse_args().repos:
        probs = check(repo)
        if probs:
            bad += 1
            print(f"DRIFT {repo}")
            for p in probs:
                print(f"  {p}")
        else:
            print(f"OK {repo}")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
