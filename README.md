# claude-skills

Skills I wrote for Claude. Each one installs on its own.

- `interview`: before a big or vague task, Claude asks you rounds of multiple-choice questions. Every question comes with a recommended answer, so you can accept the defaults or steer. You approve a short plan recap before any work starts.
- `writing-unslop`: makes Claude's writing specific and plain, and cleans up text that reads like generic AI output. It covers prose, docs, READMEs, code comments and commit messages, and includes a script that flags common tells.
- `handoff`: writes a short `HANDOFF.md` with the checked state of the work, the decisions and their reasons, open problems and next steps, so a later session can pick up where this one stopped.
- `release`: cuts a release. Claude finds out how the project releases (version files, changelog, tag scheme, release workflows, written rules), proposes the next version, prepares everything locally and pushes only after you approve. What it learns per project is kept in `~/.release-memory/`, and every rule there is re-checked against the file it came from before it is used.

## Claude Code

```text
/plugin marketplace add cweeperde/claude-skills

/plugin install interview@cweeperde-skills
/plugin install writing-unslop@cweeperde-skills
/plugin install handoff@cweeperde-skills
/plugin install release@cweeperde-skills
```

Installed skills show up as `/interview:interview`, `/writing-unslop:writing-unslop`, `/handoff:handoff` and `/release:release`, and Claude also uses them on its own when a task fits. To update, open `/plugin`, go to Marketplaces and update `cweeperde-skills`.

You can also skip the plugin system and copy a skill folder into `~/.claude/skills/`, which gives you plain `/interview`:

```bash
git clone https://github.com/cweeperde/claude-skills.git
cp -r claude-skills/plugins/interview/skills/interview ~/.claude/skills/
```

## claude.ai

Download a skill's zip from the [latest release](https://github.com/cweeperde/claude-skills/releases/latest): [interview.zip](https://github.com/cweeperde/claude-skills/releases/latest/download/interview.zip), [writing-unslop.zip](https://github.com/cweeperde/claude-skills/releases/latest/download/writing-unslop.zip), [handoff.zip](https://github.com/cweeperde/claude-skills/releases/latest/download/handoff.zip), [release.zip](https://github.com/cweeperde/claude-skills/releases/latest/download/release.zip). Then go to Customize > Skills, click +, choose Create skill > Upload a skill and pick the zip. Skills need code execution, which you can turn on under Settings > Capabilities.

## License

[MIT](LICENSE)
