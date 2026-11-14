---
name: handoff
description: Write a short HANDOFF.md that lets a later session (or another person) pick up the current work without rereading the conversation - what the goal is, what is done and verified, what was decided and why, what is broken or unfinished, and the exact next steps. Use when the user types /handoff, says "write a handoff", "save where we are", "I'll continue this tomorrow", "summarize for the next session", or is about to end a long session with work still open. Also read an existing HANDOFF.md at the start when the user says "continue from the handoff" or "pick up where we left off". Not for changelogs, PR descriptions or end-user documentation.
---

# Handoff

A handoff is a note from you to a reader who has none of this conversation: a fresh session, a colleague, or the user in a week. It must let them continue in minutes, so it records state and intent, not a story of the session.

## Write a handoff

### 1. Gather facts, don't recall them

Before writing, check the real state instead of trusting memory of the conversation:

- `git status`, `git branch --show-current`, `git log --oneline -10`, and whether the branch is pushed (`git status -sb`).
- Uncommitted changes and stashes (`git stash list`).
- Whether tests or the build pass right now. If running them is slow or risky, say they were not re-run and when they last passed.
- Open PRs or issues tied to the work, if a forge CLI such as `gh` is available.
- Background processes, dev servers or watchers you started that are still running.

If the project is not a git repository, list the files you changed instead.

### 2. Write HANDOFF.md

Put it in the project root unless the user names another place. If one exists, read it first and replace it: a handoff describes the current state, so stale sections get rewritten, not appended to. Keep it under about 60 lines; link to files and commits rather than pasting code.

Use this structure and drop sections that would be empty:

```markdown
# Handoff: <task in a few words>

Updated <YYYY-MM-DD HH:MM> on branch `<branch>` at `<short sha>` (<pushed / not pushed>).

## Goal
One or two sentences: what we are trying to achieve and for whom.

## State
- Done and verified: <what, and how it was verified>
- Done, not verified: <what, and what check is missing>
- In progress: <what, which files, how far>
- Uncommitted: <files, or "nothing">

## Decisions
- <decision> - because <reason>. (Rejected: <alternative>, because <reason>.)

## Known problems
- <symptom, where it shows up, what was already tried>

## Next steps
1. <concrete action with file paths or commands>
2. ...

## Context
- How to run / test: `<command>`
- Key files: `<path>` - <role>
- Constraints from the user: <rules they stated, e.g. "no new dependencies">
```

### 3. Rules for the content

- Every claim about state comes from step 1. Never write "tests pass" because they passed an hour ago; write when and what was run.
- Next steps are actions, not themes. "Add a retry around `upload()` in `src/sync.py:88` and a test for 503" beats "improve error handling".
- Record decisions together with their reasons and the options you rejected. That is the part a new reader cannot reconstruct from the code.
- Carry over constraints and preferences the user stated during the session, in their words where possible.
- Leave out the session's history, dead ends that taught nothing, and pleasantries.
- No secrets: no tokens, passwords, or private URLs with credentials, even if they appeared in the session.

### 4. Commit or not

Ask the user whether HANDOFF.md should be committed, kept local, or added to `.gitignore`, unless the project already settles it (an existing tracked HANDOFF.md, or an ignore rule). Don't commit it on your own.

Finish with one line telling the user where the file is and the first next step.

## Resume from a handoff

When asked to continue from a handoff:

1. Read HANDOFF.md.
2. Check it against reality: branch, last commit, uncommitted changes. If they differ, tell the user what changed since the handoff before doing anything.
3. Restate the goal and the first next step in two lines, and start on it unless the handoff or the user says to wait.
4. When the work moves on, update HANDOFF.md at the end the same way, or delete it once the task is finished and the user agrees.
