#!/usr/bin/env python3
"""Verify that every quote in report.md appears verbatim in some findings file or in stimulus.md.

Called by the orchestrator after the synthesizer writes report.md. Usage:

    python3 verify_quotes.py <run-dir>

Exits 0 if all quotes verify, exits 1 with a list of unverified quotes otherwise.
"""

from __future__ import annotations

import re
import sys
import unicodedata
from pathlib import Path


QUOTE_PATTERNS = [
    re.compile(r'"([^"\n]{10,400})"'),
    re.compile(r"\u201c([^\u201d\n]{10,400})\u201d"),
    re.compile(r"^>\s+(.{10,400})$", re.MULTILINE),
]


def normalize(text: str) -> str:
    text = unicodedata.normalize("NFKC", text)
    text = text.replace("\u201c", '"').replace("\u201d", '"')
    text = text.replace("\u2018", "'").replace("\u2019", "'")
    text = text.replace("\u2014", "-").replace("\u2013", "-")
    return re.sub(r"\s+", " ", text).strip().lower()


def extract_quotes(report_text: str) -> list[str]:
    quotes: list[str] = []
    for pattern in QUOTE_PATTERNS:
        quotes.extend(pattern.findall(report_text))
    seen: set[str] = set()
    unique: list[str] = []
    for q in quotes:
        if q not in seen:
            seen.add(q)
            unique.append(q)
    return unique


def load_corpus(run_dir: Path) -> str:
    pieces: list[str] = []
    findings_dir = run_dir / "findings"
    if findings_dir.is_dir():
        for path in sorted(findings_dir.glob("*.md")):
            if "critic" in path.name:
                continue
            pieces.append(path.read_text(encoding="utf-8"))
    stimulus = run_dir / "stimulus.md"
    if stimulus.is_file():
        pieces.append(stimulus.read_text(encoding="utf-8"))
    return "\n\n".join(pieces)


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: verify_quotes.py <run-dir>", file=sys.stderr)
        return 2

    run_dir = Path(argv[1]).resolve()
    report_path = run_dir / "report.md"
    if not report_path.is_file():
        print(f"no report.md at {report_path}", file=sys.stderr)
        return 2

    report_text = report_path.read_text(encoding="utf-8")
    corpus = load_corpus(run_dir)
    if not corpus:
        print("empty corpus — did the run finish?", file=sys.stderr)
        return 2

    corpus_norm = normalize(corpus)
    quotes = extract_quotes(report_text)

    unverified: list[str] = []
    for quote in quotes:
        if normalize(quote) not in corpus_norm:
            unverified.append(quote)

    print(f"quotes found in report: {len(quotes)}")
    print(f"verified: {len(quotes) - len(unverified)}")
    print(f"unverified: {len(unverified)}")

    if unverified:
        print("\nUNVERIFIED QUOTES (not found verbatim in findings or stimulus):\n")
        for i, q in enumerate(unverified, 1):
            print(f"{i}. \u201c{q}\u201d")
        return 1

    print("\nall quotes verified against findings corpus.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
