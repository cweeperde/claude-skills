# Discovering how a project releases

Go through these in order. Note every fact with the file it came from; that file becomes the rule's source in memory. Skip a section only when you have checked that it does not apply.

## 1. Written rules

Search the repo root and `docs/` for release instructions:

- `RELEASING.md`, `RELEASE.md`, `CONTRIBUTING.md`, `MAINTAINERS.md`
- the README's "Release", "Publishing", "Development" or "Versioning" sections
- `CLAUDE.md`, `AGENTS.md`, `.github/copilot-instructions.md` and similar agent instructions
- PR or issue templates that mention releases or changelog entries

Written rules are the strongest evidence of intent, but they go stale. If a document says one thing and a workflow enforces another, the workflow describes what actually happens; mention the conflict to the user.

## 2. Version files

Find every place the version is written. Typical places:

- `package.json` (and `package-lock.json` / `pnpm-lock.yaml` / `bun.lock` only if they hold the root version)
- `pyproject.toml`, `setup.cfg`, `setup.py`, `src/<pkg>/__init__.py` (`__version__`), `_version.py`
- `Cargo.toml` (and `Cargo.lock` for the workspace members)
- `*.csproj`, `Directory.Build.props`, `gradle.properties`, `build.gradle(.kts)`, `pom.xml`
- `manifest.json` (browser extensions), `plugin.json` / `.claude-plugin/plugin.json`, `marketplace.json`
- `version.txt`, `VERSION`, constants in source code (`grep -rn "<current version>"` finds the ones you missed)

Several version files that must agree are a rule worth recording. So is a version that is derived from the tag (setuptools-scm, `git describe`), which means you must not edit any file.

## 3. Changelog

- The file: `CHANGELOG.md`, `HISTORY.md`, `NEWS`, `CHANGES.rst`, per-package changelogs, or none.
- The format: Keep a Changelog (`## [1.2.0] - 2026-01-31` with Added/Changed/Fixed), a plain `## 1.2.0 - date` list, or generated (changesets, release-please).
- Conventions: an "Unreleased" section to rename, link references at the bottom, and the language and tone of earlier entries.
- If no changelog exists, the release notes might live only on the GitHub release. Check `gh release view <last tag>`.

## 4. Tags and history

- `git tag --sort=-v:refname --sort=-creatordate | head` (newest first; same-second tags fall back to version order): the scheme (`v1.2.3`, `1.2.3`, `<name>-v1.2.3`, `<name>@1.2.3`), whether tags are annotated (`git cat-file -t <tag>`), and whether they are signed.
- `git log --oneline -20` and earlier release commits: the release commit message style, and whether releases are a separate commit or the tag sits on a normal one.
- Several units released separately (monorepo, plugin marketplace): how each unit maps to a directory and a tag prefix.

## 5. Automation

- `.github/workflows/*.yml` (or `.gitlab-ci.yml`, etc.) that run `on: push: tags`, `on: release` or `workflow_dispatch` with a version input. Read what they check, build and publish, and what they need (secrets, environments, a dated changelog, a tag that matches the version file).
- Scripts: `scripts/release*`, `scripts/bump*`, `Makefile` / `justfile` targets, `package.json` scripts (`release`, `version`, `prepublishOnly`, `postversion`).
- Release tools and their config: semantic-release (`.releaserc*`), changesets (`.changeset/`), release-please (`release-please-config.json`), release-it (`.release-it.*`), goreleaser (`.goreleaser.yml`), cargo-release (`release.toml`), bump-my-version / bumpversion (`.bumpversion.cfg`), np, standard-version. When a tool exists, use the tool rather than editing files by hand.
- Publishing targets: npm (`publishConfig`, `private: true` means no publish), PyPI, crates.io, Docker registries, GitHub releases with assets, app stores, marketplaces.

## 6. Policies

- `git config tag.gpgsign`, `commit.gpgsign`, and `user.signingkey` (whether to sign).
- The branch releases come from, and whether releases go through a PR (branch protection usually means a PR is needed). `gh api repos/{owner}/{repo}/branches/<branch>/protection` tells you if you have access.
- Required checks before release: CI status, a test command, a validation script.
- Anything the user stated in this or earlier conversations, recorded as `user` rules.

## Turning findings into rules

Write rules as short, checkable statements:

- Good: "Tags are `<plugin>-v<x.y.z>`, one per plugin."
- Good: "`validate.py --tag` rejects a tag whose newest CHANGELOG entry says 'unreleased'."
- Bad: "Be careful with tags."
- Bad: "Releases are usually done on Fridays." This has no source.
