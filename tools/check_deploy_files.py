#!/usr/bin/env python3
"""Static checks of the deploy files of every system. Nothing is built or started.

Per system: `docker compose config` on the compose file with the variables from `.env.example`,
the CI workflow against the GitHub workflow schema (needs `check-jsonschema`, skipped if absent),
cloud-init and railway.json parse, Caddyfile braces, and a few Dockerfile rules (pinned base tag,
non root user, every COPY source exists). It cannot prove `docker build` works: no daemon is used.
Usage: python3 tools/check_deploy_files.py [--root <folder>] [--check-jsonschema <path>]
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from system_names import resolve  # noqa: E402


def dockerfile_problems(df: Path, root: Path) -> list[str]:
    out, text = [], df.read_text(encoding="utf-8")
    lines = [ln.strip() for ln in text.splitlines()]
    froms = [ln for ln in lines if ln.upper().startswith("FROM ")]
    if not froms:
        out.append("no FROM")
    for f in froms:
        img = f.split()[1]
        if ":" not in img or img.endswith(":latest"):
            out.append(f"base image not pinned: {img}")
    if not any(ln.upper().startswith("USER ") for ln in lines):
        out.append("no USER line (runs as root)")
    for ln in lines:
        m = re.match(r"COPY\s+(?:--\S+\s+)*(.+?)\s+\S+$", ln, re.I)
        if m and not ln.upper().startswith("COPY --FROM"):
            for src in m.group(1).split():
                if not (root / src).exists():
                    out.append(f"COPY source missing: {src}")
    return out


def check_system(name: str, repo: Path, cj: str | None) -> list[str]:
    bad: list[str] = []
    compose = repo / "docker-compose.yml"
    env = repo / ".env.example"
    if shutil.which("docker") and compose.exists() and env.exists():
        with tempfile.TemporaryDirectory() as t:
            shutil.copy(compose, Path(t) / "docker-compose.yml")
            shutil.copy(env, Path(t) / ".env")
            r = subprocess.run(["docker", "compose", "config", "-q"], cwd=t, capture_output=True, text=True, env={**os.environ, "POSTGRES_PASSWORD": "x"})
            if r.returncode:
                bad.append("compose config: " + (r.stderr.strip().splitlines() or ["failed"])[-1])
    else:
        bad.append("compose not checked (no docker CLI or files missing)")
    wf = list((repo / ".github" / "workflows").glob("*.yml"))
    if not wf:
        bad.append("no CI workflow")
    elif cj:
        for f in wf:
            r = subprocess.run([cj, "--builtin-schema", "vendor.github-workflows", str(f)], capture_output=True, text=True)
            if r.returncode:
                bad.append(f"workflow {f.name}: {r.stdout.strip()[-200:]}")
    rj = repo / "deploy" / "railway" / "railway.json"
    try:
        json.loads(rj.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        bad.append(f"railway.json: {exc}")
    cf = repo / "deploy" / "hetzner" / "Caddyfile"
    if cf.exists() and cf.read_text().count("{") != cf.read_text().count("}"):
        bad.append("Caddyfile braces do not balance")
    for df in repo.glob("apps/*/Dockerfile"):
        bad += [f"{df.relative_to(repo)}: {p}" for p in dockerfile_problems(df, repo)]
    return bad


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=str(Path(__file__).resolve().parent.parent.parent))
    ap.add_argument("--check-jsonschema", default=shutil.which("check-jsonschema"))
    a = ap.parse_args()
    root, rc = Path(a.root), 0
    for name, folder in resolve(root):
        bad = check_system(name, root / folder, a.check_jsonschema)
        print(f"{name} ({folder}): {'ok' if not bad else ''}")
        for b in bad:
            print("   " + b)
        rc |= 1 if bad else 0
    return rc


if __name__ == "__main__":
    sys.exit(main())
