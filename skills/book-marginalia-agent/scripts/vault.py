#!/usr/bin/env python3
"""Initialize and append to a private Book Marginalia vault."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
TIME_RE = re.compile(r"^\d{2}:\d{2}$")
PROFILE_TEMPLATE = """# Reader profile

## Current questions

## Projects and responsibilities

## Values and tensions

## Commentary preferences
"""


def clean_inline(value: Any, fallback: str = "unknown") -> str:
    if value is None:
        return fallback
    text = " ".join(str(value).split())
    return text or fallback


def safe_vault(raw_path: str) -> Path:
    vault = Path(raw_path).expanduser().resolve()
    home = Path.home().resolve()
    if vault in {Path("/").resolve(), home}:
        raise ValueError("Refusing to use a filesystem root or the home directory as the vault")
    return vault


def initialize(vault: Path) -> dict[str, Any]:
    vault.mkdir(parents=True, exist_ok=True)
    created: list[str] = []

    for name in ("memories", "highlights", "daily"):
        directory = vault / name
        if not directory.exists():
            directory.mkdir()
            created.append(str(directory))

    profile = vault / "profile.md"
    if not profile.exists():
        profile.write_text(PROFILE_TEMPLATE, encoding="utf-8")
        created.append(str(profile))

    return {"vault": str(vault), "created": created}


def validate_entry(entry: Any) -> dict[str, Any]:
    if not isinstance(entry, dict):
        raise ValueError("Entry must be a JSON object")

    date = clean_inline(entry.get("date"), "")
    time = clean_inline(entry.get("time"), "")
    quote = str(entry.get("quote", "")).strip()
    marginalia = entry.get("marginalia")

    if not DATE_RE.fullmatch(date):
        raise ValueError("date must use YYYY-MM-DD")
    if not TIME_RE.fullmatch(time):
        raise ValueError("time must use HH:MM")
    if not quote:
        raise ValueError("quote must not be empty")
    if not isinstance(marginalia, dict):
        raise ValueError("marginalia must be a JSON object")

    entry["date"] = date
    entry["time"] = time
    entry["quote"] = quote
    return entry


def markdown_entry(entry: dict[str, Any]) -> str:
    book = clean_inline(entry.get("book"), "Unknown book")
    chapter = clean_inline(entry.get("chapter"))
    location = clean_inline(entry.get("location"))
    mode = clean_inline(entry.get("mode"), "balanced")
    memory_sources = entry.get("memory_sources")
    if isinstance(memory_sources, list) and memory_sources:
        sources = "; ".join(clean_inline(item) for item in memory_sources)
    else:
        sources = "none"

    quote = "\n".join(f"> {line}" if line else ">" for line in entry["quote"].splitlines())
    note = entry["marginalia"]

    parts = [
        f"## {entry['time']} · {book}",
        "",
        f"- Chapter: {chapter}",
        f"- Location: {location}",
        f"- Mode: {mode}",
        f"- Memory sources: {sources}",
        "",
        quote,
        "",
        "### Agent marginalia",
        "",
        f"**原意：** {clean_inline(note.get('meaning'), '')}",
        "",
        f"**与你有关：** {clean_inline(note.get('connection'), '')}",
        "",
        f"**反面一问：** {clean_inline(note.get('challenge'), '')}",
        "",
        f"**带走什么：** {clean_inline(note.get('takeaway'), '')}",
    ]

    short_note = clean_inline(note.get("short_note"), "")
    if short_note:
        parts.extend(("", f"**书页旁短评：** {short_note}"))

    parts.extend(("", "### Reader response", ""))
    response = str(entry.get("reader_response", "")).strip()
    if response:
        parts.append(response)
    else:
        parts.append("<!-- Add the reader's own words or edits here. -->")

    return "\n".join(parts) + "\n"


def add_entry(vault: Path, entry_path: Path) -> dict[str, Any]:
    initialize(vault)
    entry = validate_entry(json.loads(entry_path.read_text(encoding="utf-8")))
    destination = vault / "highlights" / f"{entry['date']}.md"
    is_new = not destination.exists()

    with destination.open("a", encoding="utf-8") as handle:
        if is_new:
            handle.write(f"# Highlights · {entry['date']}\n\n")
        handle.write(markdown_entry(entry))
        handle.write("\n")

    return {"saved": str(destination)}


def list_day(vault: Path, date: str) -> str:
    if not DATE_RE.fullmatch(date):
        raise ValueError("date must use YYYY-MM-DD")
    source = vault / "highlights" / f"{date}.md"
    if not source.exists():
        raise FileNotFoundError(f"No saved highlights for {date}")
    return source.read_text(encoding="utf-8")


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description=__doc__)
    commands = root.add_subparsers(dest="command", required=True)

    init = commands.add_parser("init", help="Initialize a private local vault")
    init.add_argument("--vault", required=True)

    add = commands.add_parser("add", help="Append one JSON entry to a date file")
    add.add_argument("--vault", required=True)
    add.add_argument("--entry", required=True, type=Path)

    show = commands.add_parser("list-day", help="Print saved entries for a local date")
    show.add_argument("--vault", required=True)
    show.add_argument("--date", required=True)
    return root


def main() -> int:
    args = parser().parse_args()
    try:
        vault = safe_vault(args.vault)
        if args.command == "init":
            print(json.dumps(initialize(vault), ensure_ascii=False))
        elif args.command == "add":
            print(json.dumps(add_entry(vault, args.entry), ensure_ascii=False))
        else:
            print(list_day(vault, args.date), end="")
        return 0
    except (ValueError, OSError, json.JSONDecodeError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
