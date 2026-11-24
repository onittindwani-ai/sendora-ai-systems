#!/usr/bin/env python3
"""Rename a system across a whole repo: text, folder names and package names.

Usage:
  rename_system.py REPO --old Closeline --new Pipecairn [--old-folder closeline --new-folder pipecairn] [--apply]
  rename_system.py REPO --old Closeline --new Pipecairn --check

Without --apply it only lists what it would change (dry run). The tool is case
aware: Closeline -> Pipecairn, closeline -> pipecairn, CLOSELINE -> PIPECAIRN. For a
multi word name ("Rain Maker") the spaced, hyphen, underscore, joined and
upper snake forms are all handled. A different repo folder name (for example
`rainmaker-sdr-kit` for the system "Rainmaker") is replaced first with
--old-folder / --new-folder.

It never touches: .git, node_modules, .venv, caches, build output, lockfile
hash lines, binary files, SQLite files, and the shared base copy (`packages/`
and `tools/check_env.py`, which belong to the hub and are synced). Files named
in --skip-name (default BUILD-LEDGER.md) keep their history. `--check` greps the
repo for leftovers of the old name, case insensitively, in file text and in
file and folder names, and exits 1 when anything is left (base copy hits are
listed separately and do not fail the check).
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

SKIP_DIRS = {
    ".git", "node_modules", ".venv", "venv", "__pycache__", ".pytest_cache", ".next", ".turbo",
    "dist", "coverage", "htmlcov", ".demo", "test-results", ".hypothesis", ".pgtmp", ".mypy_cache",
    ".ruff_cache", "playwright-report", ".cache",
}
BASE_PREFIXES = ("packages/",)
BASE_FILES = {"tools/check_env.py"}
BINARY_SUFFIXES = {
    ".png", ".jpg", ".jpeg", ".gif", ".webp", ".ico", ".pdf", ".zip", ".gz", ".tar", ".woff", ".woff2",
    ".ttf", ".otf", ".mp3", ".mp4", ".mov", ".sqlite", ".sqlite3", ".db", ".pyc", ".so", ".dylib",
}
LOCKFILES = {"pnpm-lock.yaml", "package-lock.json", "uv.lock", "yarn.lock", "poetry.lock"}
HASH_LINE = re.compile(r"(integrity|resolution|sha\d+-|hash\s*=|checksum)", re.I)
SKIP_FILES = {".DS_Store"}


def words(name: str) -> list[str]:
    parts = [p for p in re.split(r"[\s_\-]+", name.strip()) if p]
    return [p.lower() for p in parts]


def form_pairs(old: str, new: str) -> list[tuple[str, str]]:
    """Explicit (old form, new form) pairs, longest first, for multi word names."""
    ow, nw = words(old), words(new)
    pairs: list[tuple[str, str]] = []
    if len(ow) > 1 or len(nw) > 1:
        pairs += [
            (" ".join(w.capitalize() for w in ow), " ".join(w.capitalize() for w in nw)),
            ("-".join(ow), "-".join(nw)),
            ("_".join(ow), "_".join(nw)),
            ("_".join(ow).upper(), "_".join(nw).upper()),
            ("".join(w.capitalize() for w in ow), "".join(w.capitalize() for w in nw)),
            ("".join(ow), "".join(nw)),
            (" ".join(ow), " ".join(nw)),
        ]
    return sorted(set(pairs), key=lambda p: -len(p[0]))


def case_like(sample: str, target_words: list[str]) -> str:
    joined = "".join(target_words)
    if sample.isupper():
        return joined.upper()
    if sample[:1].isupper():
        return joined.capitalize()
    return joined.lower()


class Renamer:
    def __init__(self, old: str, new: str, old_folder: str | None = None, new_folder: str | None = None):
        if not old or not new or old.lower() == new.lower():
            raise ValueError("old and new names must be different and not empty")
        self.old, self.new = old, new
        self.pairs = form_pairs(old, new)
        if old_folder and new_folder and old_folder != new_folder:
            self.pairs.insert(0, (old_folder, new_folder))
            self.pairs.insert(1, (old_folder.upper().replace("-", "_"), new_folder.upper().replace("-", "_")))
            self.pairs.insert(2, (old_folder.replace("-", "_"), new_folder.replace("-", "_")))
        self.pairs = sorted(set(self.pairs), key=lambda p: -len(p[0]))
        self.old_words = words(old)
        self.new_words = words(new)
        joined = "".join(self.old_words)
        self.single = re.compile(re.escape(joined), re.I)
        self.leftover = re.compile("|".join(re.escape(p[0]) for p in self.pairs + [("".join(self.old_words), "")]), re.I)

    def replace_text(self, text: str) -> str:
        for a, b in self.pairs:
            text = text.replace(a, b)
        return self.single.sub(lambda m: case_like(m.group(0), self.new_words), text)

    def replace_name(self, name: str) -> str:
        return self.replace_text(name)


def is_base(rel: str) -> bool:
    return rel in BASE_FILES or rel.startswith(BASE_PREFIXES)


def iter_files(root: Path):
    for p in sorted(root.rglob("*")):
        rel = p.relative_to(root)
        if any(part in SKIP_DIRS for part in rel.parts):
            continue
        if p.is_file() and p.name not in SKIP_FILES:
            yield p, rel.as_posix()


def read_text(p: Path) -> str | None:
    if p.suffix.lower() in BINARY_SUFFIXES:
        return None
    try:
        data = p.read_bytes()
    except OSError:
        return None
    if b"\x00" in data[:8192]:
        return None
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        return None


def rename_content(r: Renamer, text: str, lockfile: bool) -> str:
    if not lockfile:
        return r.replace_text(text)
    return "".join(line if HASH_LINE.search(line) else r.replace_text(line) for line in text.splitlines(keepends=True))


def plan_and_apply(root: Path, r: Renamer, skip_names: set[str], apply: bool) -> dict:
    changed_files: list[str] = []
    for p, rel in iter_files(root):
        if is_base(rel) or p.name in skip_names:
            continue
        text = read_text(p)
        if text is None:
            continue
        new_text = rename_content(r, text, p.name in LOCKFILES)
        if new_text != text:
            changed_files.append(rel)
            if apply:
                p.write_text(new_text, encoding="utf-8")
    renamed_paths: list[tuple[str, str]] = []
    # deepest first so parents keep their path while children move
    entries = [p for p in root.rglob("*") if not any(part in SKIP_DIRS for part in p.relative_to(root).parts)]
    for p in sorted(entries, key=lambda x: -len(x.relative_to(root).parts)):
        rel = p.relative_to(root).as_posix()
        if is_base(rel) or p.name in skip_names:
            continue
        new_name = r.replace_name(p.name)
        if new_name != p.name:
            target = p.with_name(new_name)
            renamed_paths.append((rel, target.relative_to(root).as_posix()))
            if apply:
                if target.exists():
                    raise FileExistsError(f"{target} already exists")
                p.rename(target)
    return {"files": changed_files, "paths": renamed_paths}


def find_leftovers(root: Path, r: Renamer, skip_names: set[str]) -> dict:
    content: list[tuple[str, int, str]] = []
    base: list[tuple[str, int, str]] = []
    names: list[str] = []
    for p, rel in iter_files(root):
        if p.name in skip_names:
            continue
        if r.leftover.search(rel):
            names.append(rel)
        text = read_text(p)
        if text is None:
            continue
        for n, line in enumerate(text.splitlines(), 1):
            if p.name in LOCKFILES and HASH_LINE.search(line):
                continue
            if r.leftover.search(line):
                (base if is_base(rel) else content).append((rel, n, line.strip()[:120]))
    for d in sorted(x for x in root.rglob("*") if x.is_dir()):
        rel = d.relative_to(root).as_posix()
        if any(part in SKIP_DIRS for part in d.relative_to(root).parts):
            continue
        if r.leftover.search(d.name):
            names.append(rel + "/")
    return {"content": content, "base": base, "names": names}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("repo")
    ap.add_argument("--old", required=True)
    ap.add_argument("--new", required=True)
    ap.add_argument("--old-folder")
    ap.add_argument("--new-folder")
    ap.add_argument("--apply", action="store_true", help="write changes (default is a dry run)")
    ap.add_argument("--check", action="store_true", help="only look for leftovers of the old name")
    ap.add_argument("--skip-name", action="append", default=None, help="file name to leave alone (default BUILD-LEDGER.md)")
    a = ap.parse_args(argv)
    root = Path(a.repo).resolve()
    if not root.is_dir():
        print(f"not a folder: {root}", file=sys.stderr)
        return 2
    skip = set(a.skip_name or ["BUILD-LEDGER.md"])
    r = Renamer(a.old, a.new, a.old_folder, a.new_folder)
    if a.check:
        left = find_leftovers(root, r, skip)
        for rel, n, line in left["content"]:
            print(f"LEFTOVER {rel}:{n}: {line}")
        for rel in left["names"]:
            print(f"LEFTOVER NAME {rel}")
        for rel, n, line in left["base"]:
            print(f"BASE (hub owned, not edited here) {rel}:{n}: {line}")
        bad = len(left["content"]) + len(left["names"])
        print(f"check: {bad} leftovers, {len(left['base'])} in the shared base copy")
        return 1 if bad else 0
    res = plan_and_apply(root, r, skip, a.apply)
    verb = "changed" if a.apply else "would change"
    for rel in res["files"]:
        print(f"{verb} text: {rel}")
    for old_rel, new_rel in res["paths"]:
        print(f"{verb} path: {old_rel} -> {new_rel}")
    print(f"{len(res['files'])} files, {len(res['paths'])} paths {verb}" + ("" if a.apply else " (dry run, pass --apply)"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
