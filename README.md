# claude-skills

Skills I wrote for Claude. Each one installs on its own.

- **interview**: before starting a task, Claude asks you rounds of multiple-choice questions. Every question comes with a recommended answer, so you can accept the defaults or steer. You approve a short plan recap before any work starts.
- **writing-unslop**: makes Claude's writing specific and plain, and cleans up text that reads like generic AI output. It covers prose, docs, READMEs, code comments and commit messages, and includes a script that flags common tells.

## Claude Code

```text
/plugin marketplace add cweeperde/claude-skills
/plugin install interview@cweeperde-skills
/plugin install writing-unslop@cweeperde-skills
```

Installed skills show up as `/interview:interview` and `/writing-unslop:writing-unslop`, and Claude also uses them on its own when a task fits. To update, open `/plugin`, go to Marketplaces and update `cweeperde-skills`.

You can also skip the plugin system and copy a skill folder into `~/.claude/skills/`, which gives you plain `/interview`:

```bash
git clone https://github.com/cweeperde/claude-skills.git
cp -r claude-skills/plugins/interview/skills/interview ~/.claude/skills/
```

## claude.ai

Download the zip from [`dist/`](dist/), then go to Customize > Skills, click +, choose Create skill > Upload a skill and pick the zip. Skills need code execution, which you can turn on under Settings > Capabilities.

## License

[MIT](LICENSE)
