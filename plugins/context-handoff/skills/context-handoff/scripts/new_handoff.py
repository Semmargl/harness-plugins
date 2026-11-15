#!/usr/bin/env python3
"""Scaffold, list and scan session handoff folders.

Creates <root>/<dir>/YYYY-MM-DD_HHMM_<slug>/ with summary.md and next_steps.md
copied from this skill's templates/ folder, filling in date, slug and an optional
read-only git snapshot (branch, last 3 commits, changed files).

Standard library only, Python 3.8+. Makes no network connections.

Examples:
  python3 scripts/new_handoff.py --slug auth-token-refresh
  python3 scripts/new_handoff.py --slug api-cleanup --no-git --dir docs/handoffs
  python3 scripts/new_handoff.py --list
  python3 scripts/new_handoff.py --latest
  python3 scripts/new_handoff.py --scan .handoff/2026-01-31_1730_api-cleanup
"""
from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import List

SKILL_DIR = Path(__file__).resolve().parent.parent
TEMPLATE_DIR = SKILL_DIR / "templates"
TEMPLATES = ("summary.md", "next_steps.md")
DEFAULT_DIR = ".handoff"
FOLDER_RE = re.compile(r"^\d{4}-\d{2}-\d{2}_\d{4}_[a-z0-9-]+$")

# Heuristic patterns for secret-looking strings (used by --scan).
SECRET_PATTERNS = [
    ("LLM provider API key", re.compile(r"\bsk[-_][A-Za-z0-9_-]{16,}")),
    ("GitHub token", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}")),
    ("GitHub fine-grained token", re.compile(r"\bgithub_pat_[A-Za-z0-9_]{20,}")),
    ("AWS access key id", re.compile(r"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b")),
    ("Google API key", re.compile(r"\bAIza[0-9A-Za-z_-]{30,}")),
    ("Slack token", re.compile(r"\bxox[abprs]-[A-Za-z0-9-]{10,}")),
    ("Stripe key", re.compile(r"\b(?:rk|pk)_(?:live|test)_[A-Za-z0-9]{16,}")),
    ("JWT", re.compile(r"\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}")),
    ("Private key block", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
    ("Bearer token", re.compile(r"\bBearer\s+[A-Za-z0-9._~+/=-]{16,}")),
    ("URL with credentials", re.compile(r"\b[a-z][a-z0-9+.-]*://[^/\s:@]+:[^/\s@]+@")),
    (
        "Secret assignment",
        re.compile(
            r"(?i)\b(?:password|passwd|pwd|secret|api[_-]?key|access[_-]?token|auth[_-]?token|token)"
            r"\s*[:=]\s*['\"]?(?!\[REDACTED\])[^\s'\"<>]{8,}"
        ),
    ),
]


def slugify(raw: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", (raw or "").strip().lower()).strip("-")
    return s[:60].strip("-") or "session"


def run_git(root: Path, args: List[str]) -> str:
    try:
        out = subprocess.run(
            ["git"] + args,
            cwd=str(root),
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            universal_newlines=True,
            timeout=15,
        )
    except (OSError, subprocess.SubprocessError):
        return ""
    return out.stdout.strip() if out.returncode == 0 else ""


def git_block(root: Path, enabled: bool) -> str:
    if not enabled:
        return "- branch: n/a (--no-git)\n- last commits: n/a\n- changed files: n/a"
    branch = run_git(root, ["rev-parse", "--abbrev-ref", "HEAD"])
    if not branch:
        return "- branch: n/a (not a git repository or git unavailable)\n- last commits: n/a\n- changed files: n/a"
    log = run_git(root, ["log", "--oneline", "-3"]).replace("\n", " | ") or "n/a (no commits yet)"
    status = run_git(root, ["status", "--porcelain"])
    lines = status.splitlines()
    changed = [line[3:].strip().strip('"') for line in lines[:15] if len(line) > 3]
    more = " (+{} more)".format(len(lines) - 15) if len(lines) > 15 else ""
    changed_txt = ", ".join("`{}`".format(c) for c in changed) + more if changed else "clean"
    return (
        "- branch: `{}`\n- last commits: {}\n- changed files at handoff time: {}".format(
            branch, log, changed_txt
        )
    )


def storage_dir(root: Path, explicit: str) -> Path:
    raw = explicit or os.environ.get("HANDOFF_DIR") or DEFAULT_DIR
    p = Path(raw).expanduser()
    return p if p.is_absolute() else root / p


def handoffs(base: Path) -> List[Path]:
    if not base.is_dir():
        return []
    items = [p for p in base.iterdir() if p.is_dir() and FOLDER_RE.match(p.name)]
    return sorted(items, key=lambda p: (p.name[:15], p.stat().st_mtime), reverse=True)


def show(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def create(root: Path, base: Path, slug: str, use_git: bool) -> int:
    missing = [t for t in TEMPLATES if not (TEMPLATE_DIR / t).is_file()]
    if missing:
        print("error: missing templates in {}: {}".format(TEMPLATE_DIR, ", ".join(missing)), file=sys.stderr)
        return 2
    now = datetime.now()
    stamp = now.strftime("%Y-%m-%d_%H%M")
    target = base / "{}_{}".format(stamp, slug)
    n = 2
    while target.exists():
        target = base / "{}_{}-{}".format(stamp, slug, n)
        n += 1
    target.mkdir(parents=True)

    subs = {
        "{{DATE}}": now.strftime("%Y-%m-%d %H:%M"),
        "{{SLUG}}": slug,
        "{{GIT}}": git_block(root, use_git),
    }
    for name in TEMPLATES:
        text = (TEMPLATE_DIR / name).read_text(encoding="utf-8")
        for key, value in subs.items():
            text = text.replace(key, value)
        (target / name).write_text(text, encoding="utf-8")

    rel = show(target, root)
    print("created: {}".format(rel))
    print("  summary:    {}/summary.md".format(rel))
    print("  next_steps: {}/next_steps.md   (delete if there is no follow-up)".format(rel))
    gitignore = root / ".gitignore"
    if base.parent == root and gitignore.is_file():
        entries = {l.strip().rstrip("/") for l in gitignore.read_text(encoding="utf-8").splitlines()}
        if base.name not in entries and "/" + base.name not in entries:
            print("note: '{}/' is not in .gitignore. Ask the user whether to ignore or commit it.".format(base.name))
    return 0


def scan(folder: Path) -> int:
    if not folder.exists():
        print("error: {} does not exist".format(folder), file=sys.stderr)
        return 2
    files = [folder] if folder.is_file() else sorted(p for p in folder.rglob("*") if p.is_file())
    hits = 0
    for f in files:
        try:
            lines = f.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError:
            continue
        for i, line in enumerate(lines, 1):
            for label, rx in SECRET_PATTERNS:
                if rx.search(line):
                    hits += 1
                    print("{}:{}: possible {}".format(f, i, label))
                    break
    if hits:
        print("{} suspicious line(s). Replace secrets with [REDACTED] and re-scan.".format(hits))
        return 1
    print("scan clean: {} file(s) checked".format(len(files)))
    return 0


def main(argv: List[str] = None) -> int:
    ap = argparse.ArgumentParser(description="Create, list or scan session handoff folders (no network access).")
    ap.add_argument("slug_pos", nargs="?", metavar="SLUG", help="same as --slug")
    ap.add_argument("--slug", help="2-4 words describing the thread, e.g. auth-token-refresh (default: session)")
    ap.add_argument("--dir", default="", help="storage folder, relative to root or absolute (default: $HANDOFF_DIR or .handoff)")
    ap.add_argument("--root", default="", help="project root (default: current directory)")
    ap.add_argument("--no-git", action="store_true", help="skip the read-only git snapshot")
    ap.add_argument("--list", nargs="?", const=10, type=int, metavar="N", help="list the N most recent handoffs (default 10)")
    ap.add_argument("--latest", action="store_true", help="print the path of the newest handoff folder")
    ap.add_argument("--scan", metavar="PATH", help="scan a handoff folder or file for secret-looking strings")
    a = ap.parse_args(argv)

    root = Path(a.root).expanduser().resolve() if a.root else Path.cwd()
    if not root.is_dir():
        print("error: root {} is not a directory".format(root), file=sys.stderr)
        return 2
    base = storage_dir(root, a.dir)

    if a.scan:
        p = Path(a.scan).expanduser()
        return scan(p if p.is_absolute() else root / p)
    if a.latest:
        items = handoffs(base)
        if not items:
            print("no handoffs found in {}".format(show(base, root)), file=sys.stderr)
            return 1
        print(show(items[0], root))
        return 0
    if a.list is not None:
        items = handoffs(base)[: max(a.list, 1)]
        if not items:
            print("no handoffs found in {}".format(show(base, root)))
            return 0
        for p in items:
            nxt = "+next_steps" if (p / "next_steps.md").exists() else ""
            print("{}  {}".format(show(p, root), nxt).rstrip())
        return 0
    return create(root, base, slugify(a.slug or a.slug_pos or ""), not a.no_git)


if __name__ == "__main__":
    raise SystemExit(main())
