"""Package every skill as dist/<skill>.zip for upload to claude.ai.

Run from the repo root: python3 scripts/build_zips.py
"""
import pathlib
import zipfile

root = pathlib.Path(__file__).resolve().parent.parent
dist = root / "dist"
dist.mkdir(exist_ok=True)

for skill_md in sorted(root.glob("plugins/*/skills/*/SKILL.md")):
    skill_dir = skill_md.parent
    out = dist / f"{skill_dir.name}.zip"
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zf:
        for f in sorted(skill_dir.rglob("*")):
            if f.is_file():
                # claude.ai expects the skill folder at the top of the zip
                zf.write(f, f.relative_to(skill_dir.parent))
    print(f"built {out.relative_to(root)}")
