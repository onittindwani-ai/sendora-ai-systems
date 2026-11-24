#!/usr/bin/env python3
"""Copy the frozen base (core-py and ui-kit) from the hub into a system repo.

Usage: python3 tools/sync_base.py <target repo folder> [--dry-run]

The copy is exact. Files in the target's base folders that are not part of the base are removed, so the copy never drifts.
The target gets packages/BASE_MANIFEST.json, which tools/check_base_copies.py verifies.
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from base_files import BASE_DIRS, MANIFEST_PATH, build_manifest, iter_base_files, read_version  # noqa: E402

HUB = Path(__file__).resolve().parent.parent


def sync(target: Path, hub: Path = HUB, dry_run: bool = False) -> dict:
    if target.resolve() == hub.resolve():
        raise SystemExit("Target is the hub itself. Give a system repo folder.")
    if not target.is_dir():
        raise SystemExit(f"Target folder does not exist: {target}")
    manifest = build_manifest(hub, read_version(hub))
    wanted = set(manifest["files"])
    copied, removed = [], []
    for rel in sorted(wanted):
        src, dst = hub / rel, target / rel
        if not dst.exists() or dst.read_bytes() != src.read_bytes():
            copied.append(rel)
            if not dry_run:
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(src, dst)
    for rel, p in iter_base_files(target):
        if rel not in wanted:
            removed.append(rel)
            if not dry_run:
                p.unlink()
    if not dry_run:
        mp = target / MANIFEST_PATH
        mp.parent.mkdir(parents=True, exist_ok=True)
        mp.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    return {"copied": copied, "removed": removed, "version": manifest["base_version"], "files": len(wanted)}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("target", type=Path)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    r = sync(a.target, dry_run=a.dry_run)
    print(f"base {r['version']}: {r['files']} files, {len(r['copied'])} copied, {len(r['removed'])} removed{' (dry run)' if a.dry_run else ''}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
