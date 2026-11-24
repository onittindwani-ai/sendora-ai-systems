"""One table of the seven systems: old working name, new public name, and their repo folders.

Hub tools that list the systems call `resolve(root)`: for each system it returns the new name and
folder when the renamed folder exists under `root`, otherwise the old pair, so the hub stays
consistent while the systems are renamed one by one.
"""
from __future__ import annotations

from pathlib import Path

# (old name, old folder, new name, new folder)
SYSTEMS = [
    ("Closeline", "closeline", "Pipecairn", "pipecairn"),
    ("Rainmaker", "rainmaker-sdr-kit", "Ringlark", "ringlark"),
    ("Ledgerlight", "ledgerlight", "Booklantern", "booklantern"),
    ("Lighthouse", "lighthouse-support", "Deskfern", "deskfern"),
    ("Cortex", "cortex-brain", "Lorefern", "lorefern"),
    ("Voiceprint", "voiceprint", "Penlark", "penlark"),
    ("Crewforge", "crewforge", "Slatehire", "slatehire"),
]


def resolve(root: Path) -> list[tuple[str, str]]:
    """(display name, repo folder) for each system, preferring the renamed folder when it exists."""
    out = []
    for old_name, old_folder, new_name, new_folder in SYSTEMS:
        if (root / new_folder).is_dir():
            out.append((new_name, new_folder))
        else:
            out.append((old_name, old_folder))
    return out
