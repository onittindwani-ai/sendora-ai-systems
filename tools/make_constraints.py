#!/usr/bin/env python3
"""Write constraints.txt for a system repo from the packages installed in its virtual environment.

Usage: python3 tools/make_constraints.py <repo folder> [--check]

The file pins every third party package to the exact version the tests ran against, so a fresh clone
(make install, the Docker image, CI) installs the same set and not whatever is newest that day.
The repo's own packages (editable installs) are left out. `--check` exits 1 when the file does not match
the environment, so a package updated in .venv without refreshing the file is noticed.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

HEADER = """# Exact versions of every third party Python package the tests ran against.
# Used by `make install`, the Docker image and CI (pip install -c constraints.txt ...).
# Refresh after a deliberate upgrade: make constraints
"""
OWN = ("sendora-core", "sendora_core")


def frozen(repo: Path) -> list[str]:
    py = repo / ".venv" / "bin" / "python"
    if not py.is_file():
        raise SystemExit(f"No virtual environment at {py}. Run make install first.")
    if shutil.which("uv"):
        cmd = ["uv", "pip", "freeze", "--python", str(py)]
    else:
        cmd = [str(py), "-m", "pip", "freeze"]
    out = subprocess.run(cmd, capture_output=True, text=True, check=True).stdout.splitlines()
    pkg = repo.name.lower().replace("-", "_")
    keep = []
    for line in out:
        name = line.split("==")[0].split(" @ ")[0].strip().lower().replace("_", "-")
        if line.startswith("-e ") or " @ " in line or name in {n.replace("_", "-") for n in OWN} or name == pkg.replace("_", "-"):
            continue
        keep.append(line.strip())
    return sorted(set(keep), key=str.lower)


def render(repo: Path) -> str:
    return HEADER + "\n".join(frozen(repo)) + "\n"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("repo", type=Path)
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args(argv)
    repo = args.repo.resolve()
    target = repo / "constraints.txt"
    text = render(repo)
    if args.check:
        same = target.is_file() and target.read_text() == text
        print("constraints.txt matches the environment" if same else "constraints.txt differs from the environment")
        return 0 if same else 1
    target.write_text(text)
    print(f"wrote {target} ({len(text.splitlines()) - HEADER.count(chr(10))} packages)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
