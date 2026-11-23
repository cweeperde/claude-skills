#!/usr/bin/env python3
"""release_memory.py - keep per-project release knowledge outside the repo, and
refuse to trust any of it that may have gone stale.

Every rule in a memory file names its source, and this script checks each
source before the rule is used:

    {source: file <path> sha256:<hex>}   the file must still hash the same
    {source: git-tags <glob>}            the newest tags must still match
    {source: user <YYYY-MM-DD>}          the user said so; re-ask after 180 days

A rule without a source is invalid. See references/memory-format.md.

Usage (DIR defaults to the current directory):
    release_memory.py id [DIR]        project id and label
    release_memory.py path [DIR]      path of the memory file
    release_memory.py init [DIR]      create an empty memory file if none exists
    release_memory.py check [DIR]     verify every rule's source
    release_memory.py stamp [DIR]     refresh hashes of rules verified today
    release_memory.py hash FILE...    sha256 of files

Exit codes for check: 0 all OK, 3 something STALE/ASK/INVALID, 4 no memory yet.
Other errors exit 2. RELEASE_MEMORY_DIR overrides ~/.release-memory.
Only the Python standard library is used.
"""

from __future__ import annotations

import argparse
import datetime as dt
import fnmatch
import hashlib
import os
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

USER_MAX_AGE_DAYS = 180
TAGS_TO_CHECK = 3

SOURCE_RE = re.compile(r"\{source:\s*([^{}]*)\}")
FILE_RE = re.compile(r"^file\s+(.+?)\s+sha256:([0-9a-f]{64}|\?)(?:\s*,\s*verified\s+(\d{4}-\d{2}-\d{2}))?$")
TAGS_RE = re.compile(r"^git-tags\s+(\S+)(?:\s*,\s*verified\s+(\d{4}-\d{2}-\d{2}))?$")
USER_RE = re.compile(r"^user\s+(\d{4}-\d{2}-\d{2})$")
RULE_LINE = re.compile(r"^\s*(?:[-*]|\d+[.)])\s+")


# --- project identity ---------------------------------------------------------

def git(directory: Path, *args: str) -> str | None:
    try:
        out = subprocess.run(
            ["git", "-C", str(directory), *args],
            capture_output=True, text=True, timeout=10, check=True,
        ).stdout.strip()
        return out or None
    except (OSError, subprocess.SubprocessError):
        return None


def normalize_remote(url: str) -> str | None:
    """git@github.com:Owner/Repo.git, https://user:tok@github.com/owner/repo/
    and ssh://git@github.com:22/owner/repo all become github.com/owner/repo."""
    s = url.strip()
    if not s:
        return None
    # A remote on the local disk names no shared project; use the path fallback.
    if re.match(r"^(file://|/|\.{1,2}[/\\]|[A-Za-z]:[/\\])", s):
        return None
    had_scheme = re.match(r"^[a-z][a-z0-9+.-]*://", s, re.I) is not None
    s = re.sub(r"^[a-z][a-z0-9+.-]*://", "", s, flags=re.I)
    s = re.sub(r"^[^@/]+@", "", s)
    if had_scheme:
        s = re.sub(r"^([^/:]+):\d+(?=/)", r"\1", s)
    else:
        m = re.match(r"^([^/:]+):(.+)$", s)
        if m:
            s = f"{m.group(1)}/{m.group(2)}"
    s = s.rstrip("/")
    s = re.sub(r"\.git$", "", s, flags=re.I)
    s = re.sub(r"/{2,}", "/", s)
    return s.lower() or None


def _slug(text: str) -> str:
    return re.sub(r"[^a-z0-9.-]+", "_", text.lower()).strip("_")


@dataclass
class Project:
    id: str
    label: str
    root: Path


def identify(directory: Path) -> Project:
    top = git(directory, "rev-parse", "--show-toplevel")
    root = Path(top).resolve() if top else directory.resolve()
    url = git(root, "remote", "get-url", "origin")
    if not url:
        first = (git(root, "remote") or "").splitlines()
        url = git(root, "remote", "get-url", first[0]) if first else None
    remote = normalize_remote(url) if url else None
    if remote:
        return Project(_slug(remote), remote, root)
    key = str(root).lower() if os.name == "nt" else str(root)
    digest = hashlib.sha1(key.encode()).hexdigest()[:8]
    return Project(f"local_{_slug(root.name) or 'root'}_{digest}", str(root), root)


def memory_dir() -> Path:
    return Path(os.environ.get("RELEASE_MEMORY_DIR") or Path.home() / ".release-memory")


def memory_path(project: Project) -> Path:
    return memory_dir() / f"{project.id}.md"


# --- parsing and checking -----------------------------------------------------

def sha256(path: Path) -> str:
    # Normalise line endings so a checkout with CRLF hashes like one with LF.
    data = path.read_bytes().replace(b"\r\n", b"\n")
    return hashlib.sha256(data).hexdigest()


@dataclass
class Source:
    raw: str
    kind: str  # file | git-tags | user | invalid
    path: str = ""
    digest: str = ""
    pattern: str = ""
    date: str = ""
    verified: str = ""


@dataclass
class Rule:
    line: int  # 1-based line number in the memory file
    text: str
    section: str
    sources: list[Source] = field(default_factory=list)


def parse_source(raw: str) -> Source:
    raw = raw.strip()
    if m := FILE_RE.match(raw):
        return Source(raw, "file", path=m.group(1).strip("`\"'"), digest=m.group(2), verified=m.group(3) or "")
    if m := TAGS_RE.match(raw):
        return Source(raw, "git-tags", pattern=m.group(1).strip("`"), verified=m.group(2) or "")
    if m := USER_RE.match(raw):
        return Source(raw, "user", date=m.group(1))
    return Source(raw, "invalid")


def parse_rules(text: str) -> list[Rule]:
    """Rules are list items in the Rules and Steps sections. History is a log
    of past releases, not knowledge, so it is not checked."""
    rules: list[Rule] = []
    section = ""
    in_front = False
    for n, line in enumerate(text.splitlines(), 1):
        if n == 1 and line.strip() == "---":
            in_front = True
            continue
        if in_front:
            in_front = line.strip() != "---"
            continue
        heading = re.match(r"^##\s+(.+?)\s*$", line)
        if heading:
            section = heading.group(1).strip().lower()
            continue
        if section not in {"rules", "steps"} or not RULE_LINE.match(line):
            continue
        sources = [parse_source(s) for s in SOURCE_RE.findall(line)]
        body = SOURCE_RE.sub("", RULE_LINE.sub("", line)).strip()
        rules.append(Rule(n, body, section, sources))
    return rules


@dataclass
class Verdict:
    rule: Rule
    status: str  # OK | STALE | ASK | INVALID
    reasons: list[str]


def tags_newest_first(root: Path) -> list[str]:
    # Newest first by date; tags created in the same second fall back to version order.
    out = git(root, "tag", "--sort=-v:refname", "--sort=-creatordate") or ""
    return [t for t in out.splitlines() if t.strip()]


def check_rules(rules: list[Rule], root: Path, today: dt.date) -> list[Verdict]:
    tags: list[str] | None = None
    verdicts = []
    for rule in rules:
        reasons: list[str] = []
        status = "OK"

        def worse(new: str) -> None:
            nonlocal status
            order = ["OK", "ASK", "STALE", "INVALID"]
            if order.index(new) > order.index(status):
                status = new

        if not rule.sources:
            worse("INVALID")
            reasons.append("no {source: ...}")
        for src in rule.sources:
            if src.kind == "invalid":
                worse("INVALID")
                reasons.append(f"unreadable source: {src.raw}")
            elif src.kind == "file":
                target = (root / src.path).resolve()
                try:
                    target.relative_to(root)
                except ValueError:
                    worse("INVALID")
                    reasons.append(f"{src.path} is outside the repository")
                    continue
                if src.digest == "?":
                    worse("STALE")
                    reasons.append(f"{src.path}: no hash recorded yet (run stamp after verifying)")
                elif not target.is_file():
                    worse("STALE")
                    reasons.append(f"{src.path} no longer exists")
                elif sha256(target) != src.digest:
                    worse("STALE")
                    reasons.append(f"{src.path} changed since the rule was recorded")
            elif src.kind == "git-tags":
                if tags is None:
                    tags = tags_newest_first(root)
                recent = tags[:TAGS_TO_CHECK]
                if not recent:
                    worse("STALE")
                    reasons.append("repository has no tags to compare with")
                elif not any(fnmatch.fnmatchcase(t, src.pattern) for t in recent):
                    worse("STALE")
                    reasons.append(f"newest tags {', '.join(recent)} do not match {src.pattern}")
            elif src.kind == "user":
                try:
                    age = (today - dt.date.fromisoformat(src.date)).days
                except ValueError:
                    worse("INVALID")
                    reasons.append(f"bad date {src.date}")
                    continue
                if age > USER_MAX_AGE_DAYS:
                    worse("ASK")
                    reasons.append(f"user answer from {src.date} ({age} days old): confirm it again")
        verdicts.append(Verdict(rule, status, reasons))
    return verdicts


def stamp_text(text: str, root: Path, today: dt.date) -> tuple[str, int]:
    """Refresh sha256 of file sources marked `verified <today>`. Sources not
    verified today keep their old hash, so they stay STALE until checked."""
    day = today.isoformat()
    changed = 0

    def fix(match: re.Match[str]) -> str:
        nonlocal changed
        src = parse_source(match.group(1))
        if src.kind != "file" or src.verified != day:
            return match.group(0)
        target = (root / src.path).resolve()
        if not target.is_file():
            return match.group(0)
        digest = sha256(target)
        if digest != src.digest:
            changed += 1
        return f"{{source: file {src.path} sha256:{digest}, verified {day}}}"

    lines = text.splitlines(keepends=True)
    section = ""
    out = []
    for line in lines:
        heading = re.match(r"^##\s+(.+?)\s*$", line)
        if heading:
            section = heading.group(1).strip().lower()
        out.append(SOURCE_RE.sub(fix, line) if section in {"rules", "steps"} else line)
    result = "".join(out)
    result = re.sub(r"(?m)^updated:\s*\S+$", f"updated: {day}", result, count=1)
    return result, changed


TEMPLATE = """---
project: {label}
updated: {day}
---

Release knowledge for this project, kept by the release skill. Every rule
needs a {{source: ...}}; see the skill's references/memory-format.md.

## Rules

## Steps

## History
"""


# --- CLI ----------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Per-project release memory with source checks.")
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("id", "path", "init", "check", "stamp"):
        p = sub.add_parser(name)
        p.add_argument("dir", nargs="?", default=".")
    h = sub.add_parser("hash")
    h.add_argument("files", nargs="+")
    args = ap.parse_args(argv)
    today = dt.date.today()

    if args.cmd == "hash":
        status = 0
        for f in args.files:
            try:
                print(f"{sha256(Path(f))}  {f}")
            except OSError as e:
                print(f"release_memory: cannot read {f}: {e}", file=sys.stderr)
                status = 2
        return status

    directory = Path(args.dir)
    if not directory.is_dir():
        print(f"release_memory: not a directory: {directory}", file=sys.stderr)
        return 2
    project = identify(directory)
    path = memory_path(project)

    if args.cmd == "id":
        print(f"{project.id}\t{project.label}")
        return 0
    if args.cmd == "path":
        print(path)
        return 0
    if args.cmd == "init":
        if path.exists():
            print(f"exists: {path}")
            return 0
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(TEMPLATE.format(label=project.label, day=today.isoformat()), encoding="utf-8")
        print(f"created: {path}")
        return 0

    if not path.exists():
        print(f"no memory yet for {project.label} ({path}). Do a full discovery, then `init`.")
        return 4
    text = path.read_text(encoding="utf-8")

    if args.cmd == "stamp":
        new, changed = stamp_text(text, project.root, today)
        path.write_text(new, encoding="utf-8")
        print(f"stamped {path}: {changed} hash(es) updated")
        return 0

    rules = parse_rules(text)
    verdicts = check_rules(rules, project.root, today)
    print(f"memory: {path}")
    print(f"project: {project.label} (root {project.root})")
    if not verdicts:
        print("no rules recorded yet")
    for v in verdicts:
        print(f"{v.status:<7} L{v.rule.line:<4} [{v.rule.section}] {v.rule.text}")
        for r in v.reasons:
            print(f"        - {r}")
    bad = [v for v in verdicts if v.status != "OK"]
    counts = {s: sum(v.status == s for v in verdicts) for s in ("OK", "STALE", "ASK", "INVALID")}
    print(f"\n{counts['OK']} OK, {counts['STALE']} STALE, {counts['ASK']} ASK, {counts['INVALID']} INVALID")
    if bad:
        print("Do not use STALE, ASK or INVALID rules as they are: re-verify them from the repo or ask the user.")
    return 3 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
