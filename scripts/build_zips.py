"""Package skills as dist/<skill>.zip for upload to claude.ai.

Run from anywhere:
    python3 scripts/build_zips.py              # every skill
    python3 scripts/build_zips.py interview    # only the skills of these plugins

The zips are reproducible: same sources, same bytes. Releases build them in
CI (see .github/workflows/release.yml), so dist/ is not committed.
"""
import pathlib
import sys
import zipfile

root = pathlib.Path(__file__).resolve().parent.parent
dist = root / "dist"
SKIP = {"__pycache__", ".DS_Store"}
FIXED_TIME = (1980, 1, 1, 0, 0, 0)  # zip epoch; keeps builds byte-identical


def build(skill_dir: pathlib.Path) -> pathlib.Path:
    out = dist / f"{skill_dir.name}.zip"
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zf:
        for f in sorted(skill_dir.rglob("*")):
            if not f.is_file() or SKIP & set(f.parts) or f.suffix == ".pyc":
                continue
            # claude.ai expects the skill folder at the top of the zip
            info = zipfile.ZipInfo(f.relative_to(skill_dir.parent).as_posix(), FIXED_TIME)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            zf.writestr(info, f.read_bytes())
    return out


def main(plugins):
    skill_mds = sorted(root.glob("plugins/*/skills/*/SKILL.md"))
    if plugins:
        unknown = set(plugins) - {p.parents[2].name for p in skill_mds}
        if unknown:
            sys.exit(f"build_zips: no such plugin: {', '.join(sorted(unknown))}")
        skill_mds = [p for p in skill_mds if p.parents[2].name in plugins]
    dist.mkdir(exist_ok=True)
    for skill_md in skill_mds:
        out = build(skill_md.parent)
        print(f"built {out.relative_to(root)}")


if __name__ == "__main__":
    main(sys.argv[1:])
