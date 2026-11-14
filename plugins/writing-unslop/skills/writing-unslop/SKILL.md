---
name: writing-unslop
description: Prevent and remove "AI slop" in writing - generic, inflated, unverified text with recognisable LLM tells (pivotal/testament/tapestry vocabulary, "not only... but", trailing "-ing" analysis, chat leftovers, emoji headings, bold-label bullet lists, placeholder text, fake citations). Use when writing longer text the user will publish or send under their name (articles, emails, docs, READMEs, PR descriptions, issues, release notes), and whenever the user asks to unslop, de-AI, humanize, tighten, "make it sound less like ChatGPT", remove fluff, or review text for AI tells. Also covers code comments, docstrings and commit messages plus code-level slop like hallucinated packages and placeholder values, but only load it for those when the user asks for a review or rewrite of them, not for every routine commit or comment. Use it even when the user only says the text "feels generic", "sounds robotic" or "reads like AI".
---

# Writing unslop

Slop is text that looks finished but carries little that is specific, verified, or owned by its author. The recognisable "AI tells" are symptoms. The disease is vagueness, inflation, unverified claims, and text written for no particular reader.

So the job is never camouflage. Swapping "delve" for "explore" leaves the slop in place and only makes it harder to see. The job is to make the text **specific, true, fitted to its genre and format, and cut to what matters**. When that is done, most tells disappear as a side effect.

This skill draws on Wikipedia's *Signs of AI writing* field guide and peer-reviewed research (Kobak et al. 2025, Liang et al. 2024, Juzek & Ward 2025, Reinhart et al. 2025, Russell et al. 2025, Spracklen et al. 2025). See `references/evidence.md` for what the research supports and where it is thin.

## Choose the mode

| The user wants... | Mode | Output |
|---|---|---|
| New writing (an email, a README, a commit message, an article) | **Write** | The text, written clean from the start |
| An existing text fixed ("unslop this", "make it less AI", "tighten") | **Unslop** | Revised text + short change note + open questions |
| A diagnosis only ("does this sound AI?", "review for tells") | **Audit** | Findings by severity, with fixes; no rewrite unless asked |

If the request is ambiguous between Unslop and Audit, rewrite: people who paste text usually want it fixed.

## Step 0: Identify genre, reader and destination

Before touching a word, decide:

- **Genre.** A commit message, a code comment, a README, a cover letter, an encyclopedic paragraph and a Slack message have different conventions. Research on LLM style finds genre shapes good writing more than anything else, and that chat-tuned models drift toward one dense, noun-heavy register regardless of genre. Matching the genre is half the cure.
- **Reader.** Who reads it, what do they already know, what will they do next?
- **Destination format.** Plain text field, Markdown renderer, git log, email client, wiki markup. Markdown in a commit body or an email is itself a tell.

Then read the references that apply:

- `references/patterns.md` - the full catalogue of tells with fixes (read for Unslop and Audit; skim for Write).
- `references/code.md` - comments, docstrings, READMEs, commits, PRs, issues, and code-level slop. Read whenever the text touches software.
- `references/examples.md` - before/after pairs, including over-corrections to avoid.

## The passes (in this order)

Order matters. Style edits on content that should be deleted are wasted work, and polishing an unverified claim makes it more convincing, not more true.

### 1. Content: what is actually being said?
For each sentence ask: is it **specific**, is it **true**, and **who says so**?
- Delete sentences that would be equally true of a different subject ("plays a vital role in the community").
- Delete interpretation with no actor: "the data highlights the need", "this underscores its importance". A fact cannot highlight anything. If the interpretation matters, attribute it to a real person or source, or state it as the author's own view.
- Delete gap-hedges and the guesses that follow ("While details are limited, it likely...").
- Replace adjectives with checkable facts where facts exist ("fast" -> "parses 1 GB in 3 s on an M2").

### 2. Verify
Anything checkable gets checked or flagged: citations (open them; DOIs resolve to the right paper), quotes, numbers, names, dates, package names, API calls, CLI flags, install commands. Fabricated references and hallucinated packages are among the most damaging forms of slop. If you cannot verify, say so to the user rather than presenting it as fact.

### 3. Cut
Remove: intensifiers, restating summaries ("In conclusion"), "It's important to note", meta-announcements ("In this section we will"), reflexive triplets, "Despite these challenges... continues to thrive" endings, closing flourishes, and anything the reader already knows.

### 4. Fit the genre
Apply the genre's conventions (`references/code.md` for software genres). A commit subject is imperative and about 50 characters; a code comment explains *why*; a README shows how to install and use; an email asks for one thing clearly.

### 5. Format for the destination
Prose for reasoning, lists only for genuinely parallel items. Bold at most what a reader must not miss. Sentence-case headings unless the house style says otherwise. No decorative emoji. No Markdown where it will not render.

### 6. Voice and sentences
Plain verbs ("is", "has", "use", not "serves as", "boasts", "leverages"). One term per concept, no synonym cycling. Say the positive claim directly instead of "not X, but Y". Vary sentence length because the content varies, not as a trick. Keep the author's own voice and vocabulary wherever it is not slop.

### 7. Scrub and scan
Run the scanner on the result (and on the original in Unslop/Audit mode, to see what was there):

```bash
python scripts/slop_scan.py draft.md                # kind from extension
python scripts/slop_scan.py --kind commit msg.txt   # prose | markdown | code | commit
python scripts/slop_scan.py --min-severity medium src/*.py
```

It flags chatbot leftovers, tool artifacts (`citeturn0search0`, `oaicite`, `utm_source=chatgpt.com`), placeholders, AI-vocabulary density, inflation phrases, negative parallelisms, disclaimer and summary formulas, emoji headings, bold-label lists, curly quotes in code, comment narration, comments addressed to "you", placeholder credentials, swallowed exceptions, and commit-message problems. **High** findings are near-certain problems; fix them all. **Medium** findings are worth reading. **Low** findings only matter in clusters. The scanner cannot see vagueness or false claims, so a clean scan is not the finish line. Scan the revised text on its own, not together with your change note (the note quotes the slop it removed). Open `[needs: ...]` markers are reported as high on purpose, so nobody publishes them by accident. If Python is unavailable, search manually using the strings in `references/patterns.md` (section "Search strings").

### 8. Final read
Read it once as the target reader. Could the author explain every sentence if asked? That is the strongest "human" signal there is, and the real test of whether the text is owned.

## The no-invention rule

When removing fluff you will often find nothing underneath: the original never had the fact that the fluff was standing in for. **Do not invent specifics to fill the gap.** A made-up number, date, benchmark or source is worse than the fluff it replaced, because it is slop that looks like evidence.

Instead, in order of preference:
1. Use facts available in the conversation, the user's files, the code, or a quick lookup you can actually perform.
2. Cut the claim.
3. Leave a visible marker such as `[needs: benchmark numbers]` and list it under "Needs your input".

Never fill gaps with plausible-sounding guesses, and say clearly what you could not verify.

## Preserve what should survive

- **Meaning and facts.** Unslopping must not change what the text claims, except to remove what is unsupported. Point out removed claims in the change note.
- **Required structure.** If a project template, journal format, legal form or style guide mandates a section (a PR template's "Testing" heading, an abstract's structure), keep it and fill it honestly.
- **Technical terms.** "Robust" in statistics, "leverage" in finance, "underscore" as a character, "landscape" as a page orientation are not slop.
- **The author's voice.** If the author uses em dashes, British spelling or a casual tone, keep it. Remove the tells, not the person.
- **Length the reader needs.** Cutting is the default, but if something essential is missing (how to install, why the change was made), add it.

## Avoid over-correction ("anti-slop slop")

Mechanically suppressing tells creates new ones. Watch for:
- Strings of short, punchy fragments everywhere. ("It works. It's fast. That's it.")
- Banning em dashes, lists or headings entirely when the content calls for them.
- Forced casualness, slang or invented anecdotes to "sound human".
- Deleting every transition so the logic disappears.
- Stripping all hedges, including honest uncertainty. A real limitation stated precisely ("untested on Windows") is good writing.
- Replacing banned words with near-synonyms of the same emptiness ("crucial" -> "essential").

The target is good writing for this reader, not the absence of a word list.

## Output formats

### Write mode
Give the finished text. Do not append a list of the slop you avoided. If you had to leave `[needs: ...]` markers or could not verify something, add one short line saying so after the text.

### Unslop mode

1. The revised text, complete and ready to use (in the original's format: Markdown stays Markdown, a commit stays a commit, code stays code).
2. **What changed** - three to six bullets grouped by type, not a line-by-line diff. Example: "Cut four sentences of significance claims with no facts behind them", "Replaced the emoji headings and bold-label feature list with a one-paragraph description and a usage example".
3. **Needs your input** - only if there are gaps: missing facts, unverifiable citations, claims you removed that the author may be able to support.

For long documents, edit in place in the user's file when they gave you one, and keep the change note in the reply.

### Audit mode

```
Overall: <one sentence: how sloppy, and the main problem>

High (fix first)
- L12 "As of my last knowledge update..." - chatbot leftover. Delete; verify the fact instead.

Medium
- L3-5 Significance claims with no facts ("testament to", "pivotal role"). Replace with what it actually did, or cut.

Low (only matters in clusters)
- 9 em dashes in 400 words. Vary punctuation.

Content concerns the scanner cannot see
- The benchmark claim in L20 has no source.
```

Frame findings as fixes to the text, never as a verdict on who wrote it.

## On detection and authorship

These signs are evidence for *where to edit*, not proof of *who wrote it*. Experienced human readers misjudge about one text in ten, and automated detectors are unreliable and biased against non-native English writers (Liang et al. 2023: about 61% of TOEFL essays falsely flagged). If a user asks whether someone else's text is AI-written, give the observable signs and their strength, say plainly that they are not proof, and suggest checking what matters instead: are the sources real, do the claims hold, can the author explain it.

If a user wants text to "pass a detector", help them make the text genuinely better and their own (their facts, their reasoning, their voice), and do not promise undetectability. Where a school, journal or project requires disclosure of AI assistance, mention it once without lecturing.

## Quick reference: the tells that matter most

| Tell | Strength | Fix |
|---|---|---|
| Chat leftovers ("Certainly!", "I hope this helps", "As of my last update") | Strong | Delete |
| Placeholders (`[Your Name]`, `yourusername/your-repo`, `2025-XX-XX`) | Strong | Fill with real values or delete |
| Tool artifacts (`citeturn0search0`, `oaicite`, `utm_source=chatgpt.com`) | Strong | Remove; cite properly |
| Fabricated or unverifiable citations, hallucinated packages/APIs | Strong | Verify or remove |
| Gap-hedge then speculation ("details are limited, but it likely...") | Strong | Find out or cut |
| Significance inflation ("testament to", "pivotal role", "enduring legacy") | Moderate | State the fact and its concrete effect |
| Trailing "-ing" interpretation (", highlighting its commitment to...") | Moderate | Delete or attribute |
| AI-vocabulary density (delve, intricate, tapestry, underscore, seamless...) | Strong in clusters | Replace with the concrete claim, not a synonym |
| "Not only X but Y" / "It's not X, it's Y" / "No X. No Y. Just Z." | Moderate | Say Y |
| Promotional tone ("nestled", "boasts", "blazing-fast", "seamless") | Moderate | Checkable facts instead |
| Vague attribution ("experts say", "has been described as") | Moderate | Name the source or own the claim |
| "It's important to note", "In conclusion", "Despite these challenges" | Moderate | Cut |
| Emoji headings, bold-label bullet lists, Title Case headings | Moderate | Prose, sentence case, no decoration |
| Code comments narrating code, addressed to "you", or logging changes | Moderate | Comment the why; history goes in git |
| Vague commit/PR text ("Enhance robustness and maintainability") | Moderate | Name the change and the reason |
| Em dashes, curly quotes, transition words, perfect grammar | Weak alone | Ignore unless clustered (curly quotes inside code are a real bug) |
