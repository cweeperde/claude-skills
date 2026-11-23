---
name: release
description: Cut a new release of the current project. Works out on its own how releases are done here (version files, changelog format, tag scheme, release workflows, scripts, documented rules), asks only what it cannot find out, proposes the next version with reasons, prepares everything locally, and pushes, tags and publishes only after one explicit approval. Remembers each project's release rules in ~/.release-memory/, with every rule tied to a source that is re-checked before use, so stale knowledge is never trusted. Use when the user types /release, asks to "release", "cut a release", "ship a new version", "publish vX", "tag a release" or "bump the version and release". Not for writing a changelog alone without releasing.
---

# Release

Make a correct release with as little back-and-forth as possible. Correct comes first: a release is outward-facing and hard to undo, so nothing leaves the machine before the user approves it once, with the full picture in front of them.

The helper script lives next to this file: `scripts/release_memory.py` (Python 3, standard library only; call it with `python3`, or `python` on Windows). Run it with the full path to this skill's folder, for example `python3 <skill folder>/scripts/release_memory.py check .`. Below it is shortened to `release_memory.py`.

## Ground rules

- Never push, tag, create a release or publish a package before the approval in step 7. Preparing locally (editing files, running checks, a local commit) is fine.
- The repository wins. If memory and repo disagree, the repo is right and the memory gets corrected.
- Never use a memory rule that `release_memory.py check` reports as STALE, ASK or INVALID without re-verifying it first.
- Every rule you write to memory has a source. If you cannot name one, do not store it.
- Follow the repo's and the user's rules for commits (author, signing, message style, attribution) exactly as they do for any other commit.
- Report outcomes honestly. A failed workflow or a skipped check is said plainly, not smoothed over.

## Step 1: Load what is already known

```bash
python3 <skill folder>/scripts/release_memory.py check .
```

- Exit 4: no memory yet. Do the full discovery in step 2.
- Exit 0: every rule is still backed by its source. Do step 2 only as a quick pass: look for release-relevant files that the memory does not mention yet (a new workflow, a new package).
- Exit 3: re-verify exactly the flagged rules. Open the file each one cites, check what it now says, and fix or delete the rule. For ASK rules, confirm with the user in step 5. Rules reported OK can be used as they are.

## Step 2: Discover how releases work here

Follow `references/discovery.md`. In short:

- Look for written rules in RELEASING, CONTRIBUTING, README, CLAUDE.md and AGENTS.md.
- Look at the changelog format and the version files.
- Derive the tag scheme from `git tag`.
- Read the workflows that run on tags or releases.
- Look for release scripts and tools, signing settings and branch conventions.

Read the actual files; don't guess from file names. For each fact, note where it came from, since that becomes its source. When a workflow or script enforces something (for example "the tag must match plugin.json"), that is a rule; quote the check, not your idea of it.

## Step 3: Check the state

All of these must hold before preparing anything; report each one that fails and stop or ask:

- The working tree is clean (`git status --porcelain`). Untracked junk counts too.
- You are on the branch releases come from (from memory or discovery, usually `main`).
- The branch is up to date with its remote (`git fetch`, then `git rev-list --left-right --count @{u}...HEAD`; with no upstream set, compare with `origin/<branch>`).
- CI on HEAD passed, if the project has CI (`gh run list --branch <branch> --limit 5`).
- The project's own checks pass locally: tests, typecheck, lint, any validation script the release workflow runs.

## Step 4: Work out what to release

- Find the last release tag for each releasable unit (`git describe --tags --abbrev=0 --match '<pattern>'` from HEAD, or `git tag --list '<pattern>' --sort=-v:refname` for the highest version). Most repos have one unit. Some have several, for example one tag per plugin or per package (`<name>-v<x.y.z>`).
- For each unit, list the commits since its last tag that touch it (`git log <tag>..HEAD --oneline -- <path>`). Units without changes are not released unless the user asks.
- Propose the version per unit with semver and give the reason in one line each. Breaking changes mean major (or minor below 1.0), new features mean minor, and fixes, docs and internal changes mean patch. Commit messages are evidence, not truth: if a commit says "fix" but changes behaviour users rely on, say so.
- Draft the changelog entry from what changed for users, in the project's existing format and language. Be specific: "Retry uploads after a 503" beats "Improved reliability". Do not list internal churn that nobody outside cares about.

## Step 5: Ask, once

Use the AskUserQuestion tool if available (otherwise a short numbered list), with your recommendation first:

- The version for each unit, with your reason.
- Whether the changelog draft is right. Show it in full.
- Only the gaps: rules you could not find out (for example "Does this project publish to npm, or only tag?"), and ASK rules from step 1.

Do not ask what the repo already answers. Store each answer that is a lasting rule as a `user` rule in step 9.

## Step 6: Prepare locally

1. Bump the version in every file the project keeps it in, and only there. Lock files count if the project updates them on bumps (for example `npm install --package-lock-only`).
2. Write or date the changelog entry.
3. Run the project's checks again, including any check that the release workflow will run on the tag. Run it locally first when you can, for example `validate.py --tag <tag>`. A failure here is far cheaper than a failed release.
4. Commit locally following the project's conventions (look at earlier release commits: `git log --grep` for the version pattern). Do not push yet.

## Step 7: One approval

Present one short summary and ask once:

- The commit (hash, message) and what changed in it
- The tags to create, on which commit
- Where it goes: remote and branch, and whether a GitHub release or package publish will follow and through what (a workflow, or you running `gh release create` or `npm publish`)
- What happens automatically afterwards (which workflows run on the tag)
- Anything unusual: a skipped check, a red CI run the user chose to accept, a unit released without changes

Options: release now (recommended), change something, or stop. On "change something", go back to the relevant step and show the summary again.

## Step 8: Release and verify

Do the steps in the project's order. Usually that is:

1. Push the branch.
2. Wait for CI if the project requires it before tagging.
3. Push the tags one by one, so each tag triggers its own workflow run.
4. Publish, if that is done by hand.

Then check that it actually worked: wait for the triggered runs (`gh run watch <id>` or poll `gh run list`) and confirm the result exists (`gh release view <tag>`, the package registry page, the assets). If something failed, show the error, say what state things are in (for example "the tag is pushed but the release workflow failed"), and propose a fix. Do not delete or move tags without asking.

## Step 9: Update the memory

Follow `references/memory-format.md`:

1. Run `release_memory.py init .` if no memory file exists yet.
2. Add or correct rules and steps, each with its source.
3. Add `, verified <today>` to every file source you re-read this run, and use `sha256:?` for new file sources.
4. Run `release_memory.py stamp .` to fill in the hashes.
5. Add one History line: the date, the tags, and `ok`, or what failed and why.
6. Run `release_memory.py check .`. It must exit 0. If it doesn't, fix the flagged lines.

When something went wrong because of a rule that was missing or wrong, record the corrected rule with the source that proves it (the workflow line, the error output's file). Do not record guesses about causes.

Finish with one line to the user: what was released, where it can be seen, and anything they still need to do.
