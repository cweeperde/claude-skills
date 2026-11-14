---
name: interview
description: Interview the user with structured multiple-choice questions before starting work, so the plan matches what they actually want. Every question carries a recommended default, alternatives, and an "other" option; the interview ends with a recap the user approves or edits before any work begins. Use when the user types /interview, asks to be questioned or "grilled" first, says "ask me questions before you start", or wants options and suggestions for a feature. Use it on your own initiative only for large, underspecified builds where a wrong guess would waste hours, such as "build me an app that...", a whole project from a one-line idea, or a big rework with several open design choices. Do not self-trigger for bug fixes, small features, refactors with a clear goal, or anything the user has already specified.
---

# Interview

Ask before you build. The goal is a plan the user has consciously shaped, without making them think up every detail themselves: you do the thinking, propose the best option as a default, and they confirm or redirect with a tap.

## When it runs

Run the full interview when the user invokes it explicitly (/interview, "question me first", "ask me stuff before you start").

When you trigger it yourself on a large, vague task, open with one short line saying you'll ask a few questions first because the request leaves important choices open. If the user says to just start, skip straight to work using your defaults and list them briefly at the top so they can still redirect.

Skip it for small, clear, or easily reversible tasks. A one-line fix does not need an interview, and an unnecessary one is annoying.

## Step 1: Understand before asking

Questions are only as good as your grasp of the situation, so look first.

- Existing code or feature (refinement mode): read the relevant files, see how it works today, and note weak spots, missing pieces, things that could go, and better approaches. Many of your questions will come from this.
- New feature in an existing project: check the stack, conventions, and neighbouring features so defaults fit what's already there.
- From scratch: nothing to read, so the first round covers the big picture.

Don't ask anything you can answer by looking, such as which framework the repo uses. When you did look, open the first round with two or three lines on what you found, so the user can see where the questions come from.

## Step 2: Ask in adaptive rounds

Work from broad to detailed. Each round's answers shape the next round's questions.

1. Round 1 covers the shape of it: purpose, audience, scope, the main approach or stack, must-haves versus nice-to-haves, and what "done" looks like.
2. Later rounds cover the details: specific behaviour, UI and UX, data, edge cases, error handling, integrations, performance, testing, and anything the earlier answers opened up.
3. When working on something that exists, propose concrete changes, add-ons, and removals as questions, e.g. "Replace the polling with websockets?", "Drop the unused export button?". This is where you add the most value, so be specific and opinionated.

Stop when the remaining unknowns are ones your defaults handle fine. A typical interview is 2–4 rounds; a big from-scratch project may take more, a modest feature fewer. Every question should change what gets built. Don't pad with questions whose answer wouldn't matter.

### What every question looks like

Each question has a recommended default: your genuine best choice for this situation, listed first and marked "(Recommended)". The user should be able to accept every default and get a good result.

Add two or three real alternatives that lead to different outcomes, not rewordings of the same thing. The user can always write their own answer ("Other"). Give options a short description when the label alone isn't clear, especially the trade-off ("faster to build, harder to extend later").

Use multi-select when choices aren't exclusive (e.g. "Which extras should v1 include?").

If an answer adds a constraint you didn't ask about (a rule like "never do X", a deadline, a tool to use), treat it as a decision, repeat it in the recap, and follow it for the rest of the task.

### How to present them

When the AskUserQuestion tool (or a similar multiple-choice tool) is available, use it. It renders tappable cards, includes "Other" automatically, and takes up to 4 questions per call with up to 4 options each. Run one call per round; if a round needs more than 4 questions, make several calls in a row before moving on. For choices that are easier to judge visually (a layout, a code shape), use the option preview field if the tool has one.

Without such a tool, use a numbered text list that's quick to answer:

```
Round 1 — the big picture

1. Who is this for?
   a) Just you, personal use (default)
   b) A small team
   c) Public users
   d) Other: ...

2. Which stack?
   a) Next.js + SQLite (default) — fast to start, easy to deploy
   b) Python + FastAPI
   c) Other: ...

Reply like "1a, 2b" or "all defaults", or write your own answer to any number.
```

Accept shorthand like "defaults", "default except 3b", or free text, and interpret it sensibly.

## Step 3: Recap and confirm

After the last round, always present a recap before doing any work. It's the user's last cheap chance to catch a misunderstanding.

```
## Plan recap

Goal: one or two sentences on what you'll build or change and why.

Decisions
- Topic: choice  (note "default" or "your pick" where useful)
- ...

Scope
- In: ...
- Out / later: ...

Changes to existing code (refinement only)
- Add: ... / Change: ... / Remove: ...

Open assumptions: anything you decided without asking.
```

Then ask whether to start, with tappable options when the tool is available:

- Start implementation (Recommended)
- Change something: ask what, update the plan, show the revised recap, and ask again
- Ask more questions: run another round on whatever they want to dig into

Don't begin the work until the user picks start. If they change something, show the updated recap rather than starting straight away, so the plan they approve is the plan you follow.

For a long build that may span sessions, offer to save the approved recap to a file in the project (e.g. `PLAN.md`) so it survives the conversation.

## Step 4: Do the work

Follow the approved plan. If something comes up during the work that contradicts the plan or forces a significant choice the interview didn't cover, pause and ask a single question in the same default + options format rather than guessing silently.

## Writing good questions

Be concrete. "Should the list paginate (default: infinite scroll), or show numbered pages?" beats "How should we handle lots of items?"

Make defaults opinionated. A default is your recommendation, not the safest-sounding option. Pick what you'd actually build.

Mix general and specific questions. Big-picture questions keep the plan coherent; detailed ones prevent rework later.

Never ask about something the user already stated in their request; reflect it in the recap instead.

Keep labels short (a few words) and put the nuance in the description.
