# claude-skills

Skills I wrote for Claude. Each one installs on its own.

- `interview`: before a big or vague task, Claude asks you rounds of multiple-choice questions. Every question comes with a recommended answer, so you can accept the defaults or steer. You approve a short plan recap before any work starts.
- `writing-unslop`: makes Claude's writing specific and plain, and cleans up text that reads like generic AI output. It covers prose, docs, READMEs, code comments and commit messages, and includes a script that flags common tells.
- `handoff`: writes a short `HANDOFF.md` with the checked state of the work, the decisions and their reasons, open problems and next steps, so a later session can pick up where this one stopped.

## Claude Code

```text
/plugin marketplace add cweeperde/claude-skills
/plugin install interview@cweeperde-skills
/plugin install writing-unslop@cweeperde-skills
/plugin install handoff@cweeperde-skills
```

Installed skills show up as `/interview:interview`, `/writing-unslop:writing-unslop` and `/handoff:handoff`, and Claude also uses them on its own when a task fits. To update, open `/plugin`, go to Marketplaces and update `cweeperde-skills`.

You can also skip the plugin system and copy a skill folder into `~/.claude/skills/`, which gives you plain `/interview`:

```bash
git clone https://github.com/cweeperde/claude-skills.git
cp -r claude-skills/plugins/interview/skills/interview ~/.claude/skills/
```

## claude.ai

Download the skill's zip from the [latest releases](https://github.com/cweeperde/claude-skills/releases), then go to Customize > Skills, click +, choose Create skill > Upload a skill and pick the zip. Skills need code execution, which you can turn on under Settings > Capabilities.

## Development

Each plugin lives in `plugins/<name>/` with its own `plugin.json` version and `CHANGELOG.md`.

```bash
python3 scripts/validate.py         # marketplace, plugin.json, SKILL.md frontmatter, changelogs
python3 -m pytest tests             # slop_scan.py tests
python3 scripts/build_zips.py       # zips into dist/ (not committed)
```

CI runs all three on every push and pull request.

To release a plugin:

1. Bump `version` in `plugins/<name>/.claude-plugin/plugin.json`.
2. Add a `## x.y.z - YYYY-MM-DD` entry at the top of its `CHANGELOG.md`. While you work, the entry can say `unreleased` instead of a date; the release check refuses it until it is dated.
3. Merge to `main`, then tag and push:

   ```bash
   git tag <name>-v<x.y.z>
   git push origin <name>-v<x.y.z>
   ```

The release workflow checks the tag against `plugin.json` and the changelog, builds that skill's zip, and publishes a GitHub Release with the changelog entry as notes. Claude Code users get the new version through `/plugin` once it is on `main`; the tag only matters for the claude.ai zip.

## License

[MIT](LICENSE)
