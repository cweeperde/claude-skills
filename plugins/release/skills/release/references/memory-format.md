# Release memory format

One Markdown file per project in `~/.release-memory/` (or `$RELEASE_MEMORY_DIR`), named after the project id that `release_memory.py id` prints. A project with a git remote keeps the same file across clones and machines.

```markdown
---
project: github.com/owner/repo
updated: 2026-11-23
---

## Rules
- Tags are `v<x.y.z>`. {source: git-tags v*.*.*}
- The version lives in package.json and src/version.ts, and both must agree. {source: file package.json sha256:<64 hex>} {source: file src/version.ts sha256:<64 hex>}
- The release workflow publishes to npm on tag push; do not run npm publish by hand. {source: file .github/workflows/release.yml sha256:<64 hex>}
- Releases go straight to main, no PR. {source: user 2026-11-23}

## Steps
1. npm test {source: file package.json sha256:<64 hex>}
2. Push main, wait for CI, then push the tag. {source: user 2026-11-23}

## History
- 2026-11-23 v1.4.0: ok
- 2026-12-02 v1.4.1: release workflow failed, NPM_TOKEN expired; user renewed it, re-ran: ok
```

## Sections

- `## Rules`: facts about how releases work here. Each list item is one rule.
- `## Steps`: the release procedure in order, as numbered items. These are rules too and are checked the same way.
- `## History`: one line per release attempt. It is a log, not knowledge, and is never checked. Do not put rules here.

Anything else in the file (notes, headings other than these three) is ignored by the checker. Keep it out rather than relying on it.

## Sources

Every rule and step ends with one or more `{source: ...}` tags. A rule is only as fresh as its worst source.

| Source | Means | `check` reports |
| --- | --- | --- |
| `{source: file <path> sha256:<hash>}` | Read from this file (path relative to the repo root) | STALE if the file changed or is gone |
| `{source: file <path> sha256:?, verified <date>}` | New file source, hash not filled in yet | STALE until `stamp` fills it |
| `{source: git-tags <glob>}` | Derived from tag names | STALE if none of the 3 newest tags match the glob |
| `{source: user <YYYY-MM-DD>}` | The user said so | ASK after 180 days |

Line endings don't matter for the hash: a CRLF checkout hashes like an LF one.

A file source with `, verified <date>` records when you last re-read that file and confirmed the rule. `stamp` updates the hash only on file sources verified today, so a source can't be refreshed without being re-read.

## Updating after a release

1. Correct or delete rules that were STALE and turned out wrong. Edit the text of rules that changed.
2. For every file you re-read and confirmed, set the source to `, verified <today>` (keep the old hash or use `sha256:?`).
3. Add new rules with `sha256:?, verified <today>`.
4. Run `release_memory.py stamp .`, then `release_memory.py check .`. It must exit 0.

## What does not belong here

- Secrets, tokens, or anything from `.env` files.
- Guesses ("probably", "usually") and rules you could not tie to a source.
- One-off details of a single release. Those go in History, and only briefly.
- Copies of the changelog or release notes.
