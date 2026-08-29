#!/usr/bin/env python3
"""Zero-LLM MemHooks maintainer.

Two jobs:

1. ``event`` (default): consume a runtime hook event on stdin, extract touched
   project paths, and maintain a tiny auto-recall block in the nearest
   MEMHOOKS.md files. No model call is made.
2. ``note``: add one explicit retrieval cue discovered by the *current* agent
   while it is already reasoning. This costs no extra model call; it is just a
   deterministic file edit.

The script never writes memory content. It writes retrieval cues only.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shlex
import subprocess
import sys
from pathlib import Path
from typing import Any, Iterable

HOOK_FILENAME = os.getenv("MEMHOOKS_FILENAME", "MEMHOOKS.md")
AUTO_START = "<!-- memhooks:auto:start -->"
AUTO_END = "<!-- memhooks:auto:end -->"
NOTES_START = "<!-- memhooks:notes:start -->"
NOTES_END = "<!-- memhooks:notes:end -->"
MAX_AUTO_PATHS = int(os.getenv("MEMHOOKS_AUTO_PATHS", "12"))
MAX_NOTES = int(os.getenv("MEMHOOKS_MAX_NOTES", "16"))
SKIP_PARTS = {
    ".git", ".hg", ".svn", ".venv", "venv", "node_modules", "dist", "build",
    "__pycache__", ".idea", ".vscode", ".pytest_cache", ".mypy_cache",
}
PATH_KEYS = {
    "path", "file", "filename", "file_path", "filepath", "target", "source",
    "destination", "dest", "output", "output_path", "workdir", "cwd",
}
FILE_TOKEN = re.compile(r"(?<![\w:/.-])([A-Za-z0-9_.~/-]+\.[A-Za-z0-9_.-]{1,12})(?![\w.-])")


def _git_root(cwd: Path) -> Path | None:
    try:
        out = subprocess.run(
            ["git", "-C", str(cwd), "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            timeout=2,
            check=False,
        )
        if out.returncode == 0 and out.stdout.strip():
            return Path(out.stdout.strip()).resolve()
    except Exception:
        pass
    return None


def _nearest_enabled_root(cwd: Path) -> Path | None:
    """Return git root if it contains MEMHOOKS.md, else highest hooked ancestor."""
    git = _git_root(cwd)
    if git and (git / HOOK_FILENAME).is_file():
        return git
    hits = [d for d in (cwd, *cwd.parents) if (d / HOOK_FILENAME).is_file()]
    return hits[-1] if hits else None


def _safe_relative(candidate: str, cwd: Path, root: Path) -> Path | None:
    candidate = candidate.strip().strip("'\"`[](){}<>,;:")
    if not candidate or candidate.startswith(("http://", "https://", "git@")):
        return None
    candidate = os.path.expandvars(os.path.expanduser(candidate))
    p = Path(candidate)
    if not p.is_absolute():
        p = cwd / p
    try:
        p = p.resolve(strict=False)
        rel = p.relative_to(root)
    except Exception:
        return None
    if not rel.parts or any(part in SKIP_PARTS for part in rel.parts):
        return None
    if p.name == HOOK_FILENAME:
        return None
    if p.exists() and p.is_dir():
        return None
    if not p.suffix and not p.exists():
        return None
    return rel


def _strings(value: Any) -> Iterable[tuple[str | None, str]]:
    if isinstance(value, dict):
        for k, v in value.items():
            if isinstance(v, str):
                yield str(k).lower(), v
            else:
                yield from _strings(v)
    elif isinstance(value, list):
        for item in value:
            yield from _strings(item)
    elif isinstance(value, str):
        yield None, value


def _extract_paths(tool_input: Any, cwd: Path, root: Path) -> set[Path]:
    found: set[Path] = set()
    for key, text in _strings(tool_input):
        candidates: list[str] = []
        if key in PATH_KEYS:
            candidates.append(text)
        candidates.extend(m.group(1) for m in FILE_TOKEN.finditer(text))
        if any(ch in text for ch in " /\\"):
            try:
                candidates.extend(tok for tok in shlex.split(text) if "/" in tok or "\\" in tok)
            except Exception:
                pass
        for raw in candidates:
            rel = _safe_relative(raw, cwd, root)
            if rel is not None:
                found.add(rel)
    return found


def _read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ""
    except Exception:
        return ""


def _replace_block(text: str, start: str, end: str, block: str) -> str:
    if start in text and end in text:
        before = text.split(start, 1)[0].rstrip()
        after = text.split(end, 1)[1].lstrip("\n")
        pieces = [before, block.rstrip()]
        if after:
            pieces.append(after.rstrip())
        return "\n\n".join(p for p in pieces if p) + "\n"
    base = text.rstrip()
    return base + ("\n\n" if base else "") + block.rstrip() + "\n"


def _ensure_base(path: Path) -> str:
    text = _read(path)
    if text.strip():
        return text
    return "---\nschema: memhooks/v1\ninherits: true\n---\n\n# MemHooks\n"


def _parse_auto_paths(text: str) -> list[str]:
    if AUTO_START not in text or AUTO_END not in text:
        return []
    body = text.split(AUTO_START, 1)[1].split(AUTO_END, 1)[0]
    return re.findall(r"^- `([^`]+)`\s*$", body, flags=re.M)


def _auto_block(paths: list[str]) -> str:
    listing = "\n".join(f"- `{p}`" for p in paths)
    return (
        f"{AUTO_START}\n"
        "## Auto-maintained recall anchors\n\n"
        "Before substantive work here, recall prior **decisions, constraints, "
        "failures, fixes, rejected approaches, and unresolved issues** involving:\n"
        f"{listing}\n\n"
        "These are retrieval cues, not memory contents. If this turn establishes a "
        "durable non-obvious decision, failure, constraint, or rejected approach, "
        "record one concise future-retrieval question with the MemHooks note helper "
        "before finishing.\n"
        f"{AUTO_END}"
    )


def _update_directory(root: Path, rel_files: Iterable[Path]) -> int:
    grouped: dict[Path, list[str]] = {}
    for rel in rel_files:
        grouped.setdefault(rel.parent, []).append(rel.as_posix())

    writes = 0
    for rel_dir, additions in grouped.items():
        directory = root / rel_dir
        if not directory.is_dir():
            directory = root
        hook = directory / HOOK_FILENAME
        text = _ensure_base(hook)
        existing = _parse_auto_paths(text)
        ordered: list[str] = []
        for item in existing + additions:
            if item not in ordered:
                ordered.append(item)
        ordered = ordered[-MAX_AUTO_PATHS:]
        new = _replace_block(text, AUTO_START, AUTO_END, _auto_block(ordered))
        if new != text:
            hook.parent.mkdir(parents=True, exist_ok=True)
            hook.write_text(new, encoding="utf-8")
            writes += 1
    return writes


def _notes_from(text: str) -> list[str]:
    if NOTES_START not in text or NOTES_END not in text:
        return []
    body = text.split(NOTES_START, 1)[1].split(NOTES_END, 1)[0]
    return [m.strip() for m in re.findall(r"^- (.+)$", body, flags=re.M)]


def _notes_block(notes: list[str]) -> str:
    listing = "\n".join(f"- {n}" for n in notes)
    return (
        f"{NOTES_START}\n"
        "## In-session retrieval cues\n\n"
        f"{listing}\n\n"
        "Keep these as questions/cues; durable facts belong in the memory backend.\n"
        f"{NOTES_END}"
    )


def add_note(cwd: Path, query: str) -> int:
    root = _nearest_enabled_root(cwd)
    if root is None:
        print("MemHooks is not enabled here (no ancestor MEMHOOKS.md).", file=sys.stderr)
        return 2
    query = " ".join(query.strip().split())
    if not query:
        return 2
    target_dir = next((d for d in (cwd, *cwd.parents) if (d / HOOK_FILENAME).is_file()), cwd)
    try:
        target_dir.relative_to(root)
    except ValueError:
        target_dir = root
    hook = target_dir / HOOK_FILENAME
    text = _ensure_base(hook)
    notes = _notes_from(text)
    if query not in notes:
        notes.append(query)
    notes = notes[-MAX_NOTES:]
    new = _replace_block(text, NOTES_START, NOTES_END, _notes_block(notes))
    if new != text:
        hook.write_text(new, encoding="utf-8")
    return 0


def init(cwd: Path) -> int:
    root = _git_root(cwd) or cwd
    hook = root / HOOK_FILENAME
    if hook.exists():
        return 0
    name = root.name
    hook.write_text(
        "---\n"
        "schema: memhooks/v1\n"
        "inherits: true\n"
        "---\n\n"
        "# MemHooks\n\n"
        f"Recall prior decisions, constraints, failures, fixes, rejected approaches, "
        f"and unresolved issues concerning the `{name}` project before making "
        "substantive changes.\n\n"
        "If a turn establishes a durable non-obvious decision, failure, constraint, "
        "or rejected approach, record one concise future-retrieval question with "
        "the MemHooks note helper before finishing.\n",
        encoding="utf-8",
    )
    return 0


def handle_event(payload: dict[str, Any]) -> int:
    raw_cwd = payload.get("cwd") or os.getcwd()
    try:
        cwd = Path(raw_cwd).expanduser().resolve()
    except Exception:
        return 0
    root = _nearest_enabled_root(cwd)
    if root is None:
        return 0
    if str(payload.get("hook_event_name") or "") != "post_tool_call":
        return 0
    paths = _extract_paths(payload.get("tool_input"), cwd, root)
    if paths:
        _update_directory(root, paths)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Maintain MEMHOOKS.md with zero extra LLM calls.")
    sub = parser.add_subparsers(dest="cmd")
    sub.add_parser("event", help="read a hook event JSON object from stdin")
    p_init = sub.add_parser("init", help="enable MemHooks in this repository")
    p_init.add_argument("path", nargs="?", default=".")
    p_note = sub.add_parser("note", help="add one semantic retrieval cue")
    p_note.add_argument("--cwd", default=".")
    p_note.add_argument("--query", required=True)

    args = parser.parse_args()
    cmd = args.cmd or "event"
    if cmd == "init":
        return init(Path(args.path).expanduser().resolve())
    if cmd == "note":
        return add_note(Path(args.cwd).expanduser().resolve(), args.query)
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0
    return handle_event(payload if isinstance(payload, dict) else {})


if __name__ == "__main__":
    raise SystemExit(main())
