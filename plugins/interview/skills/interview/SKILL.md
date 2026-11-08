---
name: interview
description: Interview the user with structured multiple-choice questions before starting work, so the plan matches what they actually want. Every question carries a recommended default, alternatives, and an "other" option; the interview ends with a recap the user approves or edits before any work begins. Use when the user types /interview, asks to be questioned or "grilled" first, says "ask me questions before you start", or wants options and suggestions for a feature. Also use on your own initiative when a request is large and underspecified, such as "build me an app that...", vibe-coding a whole project from a one-line idea, a vague new feature, or "improve / rework / clean up this feature", where a wrong guess would waste significant work.
---

# Interview

Ask before you build. The goal is a plan the user has consciously shaped, without making them think up every detail themselves: you do the thinking, propose the best option as a default, and they confirm or redirect with a tap.

## When it runs

- **Invoked explicitly** (/interview, "question me first", "ask me stuff before you start"): run the full interview.
- **Self-triggered** on a big, vague task: start with one short line saying you'll ask a few questions first because the request leaves important choices open, then run the interview. If the user says to just start, skip straight to work using your defaults and list them briefly at the top so they can still redirect.
- **Skip it** for small, clear, or easily reversible tasks. A one-line fix does not need an interview, and an unnecessary one is annoying.

## Step 1: Understand before asking

Questions are only as good as your grasp of the situation, so look first:

- **Existing code or feature (refinement mode):** read the relevant files, see how it works today, and note weak spots, missing pieces, things that could go, and better approaches. Many of your questions will come from this.
- **New feature in an existing project:** check the stack, conventions, and neighbouring features so defaults fit what's already there.
- **From scratch / vibe coding:** nothing to read, so the first round covers the big picture.

Don't ask anything you can answer by looking, such as which framework the repo uses.

## Step 2: Ask in adaptive rounds

Work from broad to detailed. Each round's answers shape the next round's questions.

1. **Round 1, the shape of it:** purpose, audience, scope, the main approach or stack, must-haves versus nice-to-haves, and what "done" looks like.
2. **Round 2+, the details:** the specific behaviour, UI and UX, data, edge cases, error handling, integrations, performance, testing, and anything the earlier answers opened up.
3. **Refinement suggestions** (when working on something that exists): propose concrete changes, add-ons, and removals as questions, e.g. "Replace the polling with websockets?", "Drop the unused export button?". This is where you add the most value, so be specific and opinionated.

Stop when the remaining unknowns are ones your defaults handle fine. A typical interview is 2–4 rounds; a big vibe-coding project may take more, a modest feature fewer. Asking a lot is the point of this skill, but every question should change what gets built. Don't pad with questions whose answer wouldn't matter.

### What every question looks like

- **A recommended default:** your genuine best choice for this situation, listed first and marked "(Recommended)". The user should be able to accept every default and get a good result.
- **2–3 real alternatives:** distinct options that lead to different outcomes, not rewordings of the same thing.
- **"Other":** the user can always write their own answer.
- **Short descriptions** on options when the label alone isn't clear, especially the trade-off (e.g. "faster to build, harder to extend later").

Use multi-select when choices aren't exclusive (e.g. "Which extras should v1 include?").

### How to present them

**When the AskUserQuestion tool (or a similar multiple-choice tool) is available, use it.** It renders tappable cards, includes "Other" automatically, and takes up to 4 questions per call. Run one call per round; if a round needs more than 4 questions, make several calls in a row before moving on.

**Without such a tool, use a numbered text list** that's quick to answer:

```
**Round 1 — the big picture**

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

Use this structure:

```
## Plan recap

**Goal:** one or two sentences on what you'll build or change and why.

**Decisions**
- Topic: choice  (note "default" or "your pick" where useful)
- ...

**Scope**
- In: ...
- Out / later: ...

**Changes to existing code** (refinement only)
- Add: ... / Change: ... / Remove: ...

**Open assumptions:** anything you decided without asking.
```

Then ask whether to start, with tappable options when the tool is available:

- **Start implementation (Recommended)**
- **Change something**: ask what, update the plan, show the revised recap, and ask again
- **Ask more questions**: run another round on whatever they want to dig into

Don't begin the work until the user picks start. If they change something, show the updated recap rather than starting straight away, so the plan they approve is the plan you follow.

## Step 4: Do the work

Follow the approved plan. If something comes up during the work that contradicts the plan or forces a significant choice the interview didn't cover, pause and ask a single question in the same default + options format rather than guessing silently.

## Writing good questions

- **Be concrete.** "Should the list paginate (default: infinite scroll), or show numbered pages?" beats "How should we handle lots of items?"
- **Make defaults opinionated and justified.** A default is your recommendation, not the safest-sounding option. Pick what you'd actually build.
- **Mix general and specific.** Big-picture questions keep the plan coherent, detailed ones prevent rework later.
- **Use what the user already said.** Never ask about something already stated in their request; reflect it in the recap instead.
- **Keep labels short** (a few words) and put the nuance in the description.
