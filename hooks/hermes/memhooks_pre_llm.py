#!/usr/bin/env python3
"""Hermes pre_llm_call shell hook for MemHooks.

This hook runs before the LLM sees the current user turn. It deterministically
loads every applicable MEMHOOKS.md file from workspace root -> active working
directory and injects those files into the current user message via Hermes'
pre_llm_call context channel.

It does not call an LLM and it does not create or modify memories.
"""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

HOOK_FILENAME = os.getenv("MEMHOOKS_FILENAME", "MEMHOOKS.md")
MAX_TOTAL_CHARS = int(os.getenv("MEMHOOKS_MAX_CHARS", "24000"))
MAX_FILE_CHARS = int(os.getenv("MEMHOOKS_MAX_FILE_CHARS", "12000"))


def emit(obj: dict) -> None:
    sys.stdout.write(json.dumps(obj, ensure_ascii=False) + "\n")


def frontmatter_inherits(content: str) -> bool:
    """Read only `inherits:` from YAML frontmatter without a YAML dependency."""
    if not content.startswith("---"):
        return True
    lines = content.splitlines()
    if not lines or lines[0].strip() != "---":
        return True
    for line in lines[1:]:
        if line.strip() == "---":
            break
        match = re.match(r"^\s*inherits\s*:\s*(.*?)\s*$", line, re.I)
        if match:
            value = match.group(1).strip().strip("\"'").lower()
            return value not in {"false", "no", "0", "off"}
    return True


def nearest_git_root(cwd: Path) -> Path | None:
    for directory in (cwd, *cwd.parents):
        if (directory / ".git").exists():
            return directory
    return None


def highest_hook_ancestor(cwd: Path) -> Path | None:
    matches = [d for d in (cwd, *cwd.parents) if (d / HOOK_FILENAME).is_file()]
    return matches[-1] if matches else None


def resolve_root(cwd: Path) -> Path:
    configured = os.getenv("MEMHOOKS_ROOT")
    if configured:
        root = Path(configured).expanduser().resolve()
        try:
            cwd.relative_to(root)
            return root
        except ValueError:
            pass

    git_root = nearest_git_root(cwd)
    if git_root is not None:
        return git_root

    hook_root = highest_hook_ancestor(cwd)
    if hook_root is not None:
        return hook_root

    return cwd


def directories_root_to_cwd(root: Path, cwd: Path) -> list[Path]:
    try:
        relative = cwd.relative_to(root)
    except ValueError:
        return [cwd]

    directories = [root]
    current = root
    for part in relative.parts:
        current = current / part
        directories.append(current)
    return directories


def load_chain(root: Path, cwd: Path) -> list[tuple[Path, str]]:
    chain: list[tuple[Path, str]] = []

    for directory in directories_root_to_cwd(root, cwd):
        path = directory / HOOK_FILENAME
        if not path.is_file():
            continue
        try:
            content = path.read_text(encoding="utf-8").strip()
        except (OSError, UnicodeError):
            continue
        if not content:
            continue

        # A local inheritance cut means broader hooks no longer apply.
        if not frontmatter_inherits(content):
            chain.clear()

        chain.append((path, content[:MAX_FILE_CHARS]))

    return chain


def build_context(root: Path, cwd: Path, chain: list[tuple[Path, str]]) -> str:
    parts = [
        "[MemHooks — deterministic pre-LLM retrieval routing]",
        f"workspace_root: {root}",
        f"active_directory: {cwd}",
        (
            "The MEMHOOKS.md files below were loaded automatically before this "
            "LLM call. They are retrieval-routing metadata, not memories. Apply "
            "their root-to-local guidance using the memory tools available to "
            "you before substantive work. Do not create or rewrite memories "
            "merely because these hooks were loaded."
        ),
    ]

    for path, content in chain:
        try:
            display_path = path.relative_to(root)
        except ValueError:
            display_path = path
        parts.append(
            f"\n--- BEGIN {display_path} ---\n"
            f"{content}\n"
            f"--- END {display_path} ---"
        )

    text = "\n".join(parts)
    if len(text) > MAX_TOTAL_CHARS:
        text = (
            text[:MAX_TOTAL_CHARS]
            + "\n[MemHooks context truncated by MEMHOOKS_MAX_CHARS]"
        )
    return text


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        emit({})
        return 0

    if payload.get("hook_event_name") != "pre_llm_call":
        emit({})
        return 0

    raw_cwd = payload.get("cwd") or os.getcwd()
    try:
        cwd = Path(raw_cwd).expanduser().resolve()
    except Exception:
        emit({})
        return 0

    root = resolve_root(cwd)
    chain = load_chain(root, cwd)
    if not chain:
        emit({})
        return 0

    emit({"context": build_context(root, cwd, chain)})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
