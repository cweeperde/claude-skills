"""Print release notes for a tag: the plugin's CHANGELOG entry plus the
version of every skill zip attached to the release.

    python3 scripts/release_notes.py interview-v1.1.0
    python3 scripts/release_notes.py --all     # every plugin's newest entry
"""
import json
import pathlib
import re
import sys

root = pathlib.Path(__file__).resolve().parent.parent


def version(plugin):
    meta = root / "plugins" / plugin / ".claude-plugin" / "plugin.json"
    return json.loads(meta.read_text(encoding="utf-8"))["version"]


def entry(plugin, ver):
    text = (root / "plugins" / plugin / "CHANGELOG.md").read_text(encoding="utf-8")
    m = re.search(rf"^## \[?{re.escape(ver)}\b.*?\n(.*?)(?=^## |\Z)", text, re.M | re.S)
    return m.group(1).strip() if m else ""


def main(argv):
    plugins = sorted(p.name for p in (root / "plugins").iterdir() if (p / ".claude-plugin").is_dir())
    if argv == ["--all"]:
        sections = [f"## {p} {version(p)}\n\n{entry(p, version(p))}" for p in plugins]
        print("\n\n".join(sections))
    elif len(argv) == 1 and re.match(r"^[a-z0-9-]+-v\d+\.\d+\.\d+$", argv[0]):
        plugin, ver = argv[0].rsplit("-v", 1)
        print(entry(plugin, ver))
    else:
        sys.exit(__doc__)
    print("\n## Included zips\n")
    for p in plugins:
        print(f"- `{p}.zip`: {p} {version(p)}")


if __name__ == "__main__":
    main(sys.argv[1:])
