"""Helpers for small, explicit persistent memory updates."""

from __future__ import annotations

import os
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent
MEMORY_FILE = PROJECT_DIR / "memory" / "MEMORY.md"


def _normalize_rule(rule: str) -> str:
    text = " ".join((rule or "").split()).strip()
    while text.startswith(("-", "*")):
        text = text[1:].strip()
    return text


def add_learned_pattern(rule: str) -> bool:
    """Insert a learned-pattern bullet into MEMORY.md if it isn't already present."""
    normalized = _normalize_rule(rule)
    if not normalized:
        return False

    bullet = f"- {normalized}"
    if MEMORY_FILE.exists():
        content = MEMORY_FILE.read_text(encoding="utf-8")
    else:
        MEMORY_FILE.parent.mkdir(parents=True, exist_ok=True)
        content = "## Learned Patterns\n\n"

    if bullet in content:
        return False

    heading = "## Learned Patterns"
    if heading not in content:
        if not content.endswith("\n"):
            content += "\n"
        content += f"\n{heading}\n\n{bullet}\n"
    else:
        idx = content.index(heading)
        insert_start = content.find("\n", idx)
        if insert_start == -1:
            insert_start = len(content)
        insert_pos = insert_start + 1
        next_heading = content.find("\n## ", insert_pos)
        if next_heading == -1:
            next_heading = len(content)

        before = content[:next_heading]
        after = content[next_heading:]
        if not before.endswith("\n"):
            before += "\n"
        before += f"{bullet}\n"
        content = before + after

    tmp = MEMORY_FILE.with_suffix(MEMORY_FILE.suffix + ".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(content)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, MEMORY_FILE)
    return True
