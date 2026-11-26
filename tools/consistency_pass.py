#!/usr/bin/env python3
"""Cross repo consistency pass over the hub and the seven system repos.

Checks: dash characters in shipped text, local paths, private links, mentions of private design material,
relative Markdown links, the CI workflow matching tools/make_ci.py, and base version agreement. Prints findings grouped by repo and kind.
Usage: python3 tools/consistency_pass.py [--root <folder with all repos>] [--show 5]
Exit code 1 when anything is found outside the allowed list below.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from urllib.parse import unquote
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import make_ci  # noqa: E402
import system_names  # noqa: E402


def repos(root: Path) -> list[str]:
    return ["sendora-ai-systems"] + [folder for _, folder in system_names.resolve(root)]
SKIP_DIRS = {"node_modules", ".git", ".venv", ".next", "test-results", ".demo", "__pycache__", ".hypothesis", "screenshots", ".pytest_cache"}
TEXT_EXT = {".md", ".py", ".ts", ".tsx", ".js", ".mjs", ".css", ".json", ".yaml", ".yml", ".toml", ".txt", ".sh", ".html", ".csv", ".example", ".ini"}
SKIP_NAMES = {"pnpm-lock.yaml", "package-lock.json", "openapi.json"}
DASH = re.compile("[\u2013\u2014\u2015\u2212]")
PRIVATE_LINK = re.compile(r"drive\.google\.com|docs\.google\.com|notion\.so|notion\.site|dropbox\.com/s/")
LOCAL_PATH = re.compile(r"/Users/[A-Za-z0-9_.-]+/|C:\\Users\\")
import os
# Names to keep out of every shipped file come from the environment (a "|" separated list), so this file does not spell them out.
_PRIVATE = os.environ.get("PRIVATE_NAME_LIST", "")
PRIVATE_SKILLS = re.compile(_PRIVATE, re.I) if _PRIVATE else re.compile(r"(?!x)x")
LINK = re.compile(r"\[[^\]]*\]\(([^)\s#]+)(?:#[^)]*)?\)")
# Intentional uses: held out and seed data may carry dashes on purpose to test redaction and parsing.
ALLOW_DASH_UNDER = ("data/eval/", "data/seed/", "data/kb/", "data/documents", "data/heldout", "mock/", "demo/screenshots", "apps/api/tests/", "tools/tests/")


def files(repo: Path):
    for p in repo.rglob("*"):
        if p.is_file() and not (set(p.relative_to(repo).parts) & SKIP_DIRS) and p.name not in SKIP_NAMES:
            if p.suffix in TEXT_EXT or p.name in {"Makefile", "Dockerfile", ".env.example", ".gitignore", "LICENSE"}:
                yield p


def scan(repo: Path):
    found = defaultdict(list)
    for p in files(repo):
        rel = str(p.relative_to(repo))
        try:
            text = p.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        for n, line in enumerate(text.splitlines(), 1):
            if DASH.search(line) and not rel.startswith(ALLOW_DASH_UNDER):
                found["dash"].append(f"{rel}:{n}")
            if LOCAL_PATH.search(line):
                found["local path"].append(f"{rel}:{n}")
            if PRIVATE_LINK.search(line):
                found["private link"].append(f"{rel}:{n}")
            if PRIVATE_SKILLS.search(line) and p.name != "consistency_pass.py":
                found["private design material"].append(f"{rel}:{n}")
        if p.suffix == ".md" and not rel.startswith(("data/seed/", "data/eval/", "data/kb/")):
            for m in LINK.finditer(text):
                target = m.group(1)
                if re.match(r"[a-z]+:", target) or target.startswith("/"):
                    continue
                if not (p.parent / unquote(target)).exists():
                    found["broken link"].append(f"{rel} -> {target}")
    if (repo / "apps" / "api").is_dir():  # a system repo, not the hub
        ci = repo / ".github" / "workflows" / "ci.yml"
        if not ci.is_file() or ci.read_text() != make_ci.render(repo):
            found["ci workflow differs from tools/make_ci.py"].append(".github/workflows/ci.yml")
    return found


def base_versions(root: Path):
    out = {}
    for r in repos(root):
        f = root / r / "packages" / "ui-kit" / "package.json"
        out[r] = json.loads(f.read_text())["version"] if f.exists() else "missing"
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=str(Path(__file__).resolve().parent.parent.parent))
    ap.add_argument("--show", type=int, default=5)
    a = ap.parse_args()
    root = Path(a.root)
    bad = 0
    for r in repos(root):
        res = scan(root / r)
        total = sum(len(v) for v in res.values())
        bad += total
        print(f"{r}: {'clean' if not total else str(total) + ' findings'}")
        for kind, items in res.items():
            print(f"  {kind}: {len(items)}")
            for it in items[: a.show]:
                print(f"    {it}")
    versions = base_versions(root)
    print("base versions:", versions)
    if len(set(versions.values())) != 1:
        bad += 1
        print("BASE VERSIONS DIFFER")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
