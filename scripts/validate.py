"""Check that the marketplace, plugins and skills are consistent.

    python3 scripts/validate.py                      # whole repo
    python3 scripts/validate.py --tag interview-v1.1.0   # also check a release tag

Exits 1 and lists every problem if anything is off. Standard library only.
"""
import argparse
import json
import pathlib
import re
import sys

root = pathlib.Path(__file__).resolve().parent.parent
SEMVER = re.compile(r"^\d+\.\d+\.\d+$")
SKILL_NAME = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
# Paths a SKILL.md points at, e.g. `references/patterns.md`, scripts/slop_scan.py
LOCAL_REF = re.compile(r"\b((?:references|scripts|assets)/[\w./-]+\.\w+)")

errors = []


def err(where, msg):
    if isinstance(where, pathlib.PurePath):
        where = where.as_posix()
    errors.append(f"{where}: {msg}")


def load_json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        err(path.relative_to(root), f"cannot parse JSON ({e})")
        return None


def frontmatter(text):
    m = re.match(r"^---\r?\n(.*?)\r?\n---\r?\n", text, re.S)
    if not m:
        return None
    fields = {}
    for line in m.group(1).splitlines():
        k, sep, v = line.partition(":")
        if sep and not line.startswith((" ", "\t")):
            fields[k.strip()] = v.strip()
    return fields


def changelog_version(path):
    """Version of the newest '## x.y.z' entry, or None."""
    if not path.exists():
        return None
    m = re.search(r"^## \[?(\d+\.\d+\.\d+)\]?", path.read_text(encoding="utf-8"), re.M)
    return m.group(1) if m else None


def check_skill(skill_md):
    where = skill_md.relative_to(root)
    text = skill_md.read_text(encoding="utf-8")
    fm = frontmatter(text)
    if fm is None:
        err(where, "missing YAML frontmatter")
        return
    name, desc = fm.get("name", ""), fm.get("description", "")
    if name != skill_md.parent.name:
        err(where, f"frontmatter name '{name}' does not match folder '{skill_md.parent.name}'")
    if not SKILL_NAME.match(name) or len(name) > 64:
        err(where, f"name '{name}' must be lowercase-hyphenated, at most 64 chars")
    if not desc:
        err(where, "missing description")
    elif len(desc) > 1024:
        err(where, f"description is {len(desc)} chars (max 1024)")
    if len(text.splitlines()) > 500:
        err(where, "SKILL.md over 500 lines; move detail into references/")
    for ref in sorted(set(LOCAL_REF.findall(text))):
        if not (skill_md.parent / ref).exists():
            err(where, f"refers to missing file {ref}")


def check_plugin(pdir, entry):
    where = pdir.relative_to(root)
    meta = load_json(pdir / ".claude-plugin" / "plugin.json") if (pdir / ".claude-plugin" / "plugin.json").exists() else None
    if meta is None:
        err(where, "missing or invalid .claude-plugin/plugin.json")
        return None
    if meta.get("name") != pdir.name:
        err(where, f"plugin.json name '{meta.get('name')}' does not match folder")
    version = meta.get("version", "")
    if not SEMVER.match(version):
        err(where, f"plugin.json version '{version}' is not x.y.z")
    if entry and entry.get("description") != meta.get("description"):
        err(where, "description differs between plugin.json and marketplace.json")
    cl = changelog_version(pdir / "CHANGELOG.md")
    if cl is None:
        err(where, "missing CHANGELOG.md with a '## x.y.z' entry")
    elif cl != version:
        err(where, f"newest CHANGELOG entry is {cl}, plugin.json says {version}")
    skills = sorted(pdir.glob("skills/*/SKILL.md"))
    if not skills:
        err(where, "no skills/*/SKILL.md")
    for s in skills:
        check_skill(s)
    return version


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", help="release tag to check, e.g. interview-v1.1.0")
    args = ap.parse_args(argv)

    market = load_json(root / ".claude-plugin" / "marketplace.json") or {}
    entries = {}
    for e in market.get("plugins", []):
        name = e.get("name", "?")
        if name in entries:
            err("marketplace.json", f"duplicate plugin '{name}'")
        entries[name] = e
        src = (root / e.get("source", "")).resolve()
        if src.parent != (root / "plugins").resolve() or src.name != name:
            err("marketplace.json", f"'{name}' source should be ./plugins/{name}")

    versions = {}
    for pdir in sorted(p for p in (root / "plugins").iterdir() if p.is_dir()):
        if pdir.name not in entries:
            err(pdir.relative_to(root), "not listed in marketplace.json")
        versions[pdir.name] = check_plugin(pdir, entries.get(pdir.name))
    for name in entries.keys() - versions.keys():
        err("marketplace.json", f"lists '{name}' but plugins/{name} does not exist")

    if args.tag:
        m = re.match(r"^([a-z0-9-]+)-v(\d+\.\d+\.\d+)$", args.tag)
        if not m:
            err("tag", f"'{args.tag}' is not <plugin>-v<x.y.z>")
        elif m.group(1) not in versions:
            err("tag", f"no plugin named '{m.group(1)}'")
        elif versions[m.group(1)] != m.group(2):
            err("tag", f"{args.tag} but plugins/{m.group(1)} is at {versions[m.group(1)]}")
        else:
            cl = (root / "plugins" / m.group(1) / "CHANGELOG.md").read_text(encoding="utf-8")
            head = re.search(rf"^## \[?{re.escape(m.group(2))}\]?(.*)$", cl, re.M)
            if head and "unreleased" in head.group(1).lower():
                err("tag", f"CHANGELOG entry {m.group(2)} still says 'unreleased'; date it before tagging")

    if errors:
        print("\n".join(errors))
        print(f"\n{len(errors)} problem(s).")
        return 1
    print(f"OK: {len(versions)} plugins, marketplace consistent.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
