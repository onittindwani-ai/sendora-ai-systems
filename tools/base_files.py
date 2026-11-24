"""Shared helpers: which files make up the base and how to hash them."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

BASE_DIRS = ("packages/core-py", "packages/ui-kit")
BASE_FILES = ("packages/ARCHITECTURE.md", "tools/check_env.py")
SKIP_DIRS = {"node_modules", ".venv", "__pycache__", ".pytest_cache", "coverage", "dist", ".next", ".turbo", "htmlcov"}
SKIP_FILES = {".coverage", ".DS_Store", "BASE_MANIFEST.json"}
MANIFEST_PATH = "packages/BASE_MANIFEST.json"


def iter_base_files(root: Path):
    """Yield (relative posix path, absolute path) for every base file under `root`, sorted."""
    for f in BASE_FILES:
        if (root / f).is_file():
            yield f, root / f
    for d in BASE_DIRS:
        base = root / d
        if not base.is_dir():
            continue
        for p in sorted(base.rglob("*")):
            if not p.is_file():
                continue
            rel = p.relative_to(root)
            if any(part in SKIP_DIRS for part in rel.parts) or p.name in SKIP_FILES or p.suffix == ".pyc":
                continue
            yield rel.as_posix(), p


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_manifest(root: Path, version: str) -> dict:
    return {"base_version": version, "files": {rel: sha256(p) for rel, p in iter_base_files(root)}}


def read_version(root: Path) -> str:
    return json.loads((root / "packages/ui-kit/package.json").read_text())["version"]
