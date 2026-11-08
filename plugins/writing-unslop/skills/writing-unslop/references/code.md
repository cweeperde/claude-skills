# Software writing: comments, docs, READMEs, commits, PRs, issues, code

Software genres have conventions that predate LLMs. Slop in software usually means the chat or essay register leaking into places that call for terse, factual, maintainable text, plus claims (features, tests, APIs, packages) that the code does not back up. The second kind is the dangerous one.

The general patterns in `patterns.md` all apply. This file adds what is specific to code.

Evidence labels: [Industry] = documented by maintainers or companies; [Research] = peer-reviewed; [Practitioner] = widely reported by reviewers and derived from the general signs plus established guidance, but not measured in a controlled study.

## Contents
1. Code comments
2. Docstrings and API docs
3. READMEs and repository presentation
4. Commit messages
5. Pull request descriptions
6. Issues, bug reports and security reports
7. Slop in the code itself
8. Before you hand over code-related text

---

## 1. Code comments

**Baseline** (Stack Overflow blog, Ellen Spertus, nine rules): comments should not duplicate the code; good comments do not excuse unclear code; if you cannot write a clear comment the code may be the problem; comments should dispel confusion, not cause it; explain unidiomatic code; link the source of copied code; link external references where they help; comment bug fixes; mark incomplete implementations. Comments that add nothing have negative value: clutter, reading time, and they go stale.

**Slop signs** [Practitioner]:

| Sign | Example | Fix |
|---|---|---|
| Narrating the obvious | `# Initialize an empty list to store results` | Delete |
| Tutorial steps | `# Step 1: Load the data` | Delete, or name a function after the step |
| Addressed to the prompter | `# Replace with your actual API key`, `# You can adjust this as needed` | Fix the code (load config, fail loudly) and delete |
| Change log in comments | `# Updated to use the new API`, `# Fixed: now handles None`, `# NEW:` | Move to the commit message |
| Self-praise | `# Robust and efficient implementation` | Say what it does, or delete |
| Hedges | `# This should work in most cases` | State the actual limitation: `# Fails on paths over 260 chars on Windows` |
| Placeholder logic presented as done | `# TODO: implement actual validation` above `return True` | Implement it, or raise `NotImplementedError` and link an issue |
| Banners around a few functions | `# ===== Helper Functions =====` | Delete in short files |
| Emoji in comments or log strings | `logger.info("🚀 Starting server")` | Remove unless the project does this |
| Style mismatch with the file | Full formal sentences in a file of terse lowercase notes | Match the file |

**Write comments like this:**
- The *why*, the constraint, the surprise: `# Retry: the upstream API returns 503 for ~1 s after each deploy (#412).`
- If a name needs a comment, rename instead (`n  # best child node` -> `best_node`).
- `TODO`/`FIXME` with an owner or issue link.
- Links to the spec, RFC, Stack Overflow answer or bug that explains odd code.

---

## 2. Docstrings and API docs

**Slop signs** [Practitioner]:
- Restates the signature: "This function takes a string and returns a string."
- Promotional opener: "A powerful and flexible utility that seamlessly..."
- Full Args/Returns/Raises/Example template on trivial private helpers, while the hard function gets no more depth than the easy one.
- **Documents behaviour the code does not have:** parameters, exceptions, return shapes, defaults. This is the serious one; check every documented item against the code.
- Examples that do not run (wrong import path, removed API).

**Write docstrings like this:**
- First line: what it does or returns, specifically. `Return the median of values, ignoring NaN.`
- Then what the caller cannot see from the signature: units, side effects, thread safety, complexity, failure modes, invariants, what it deliberately does not do.
- Run the examples (doctest, or paste them into a test).
- Follow the project's docstring convention (Google, NumPy, Sphinx, JSDoc, rustdoc) rather than inventing one.

---

## 3. READMEs and repository presentation

**Baseline guidance** [Industry]:
- *GitHub Docs*: a README says what the project does, why it is useful, how to get started, where to get help and who maintains it. It should hold only what someone needs to start using and contributing; longer docs go in a wiki or docs site. Use relative links for files in the repo.
- *Google documentation style guide*: every package README should say what is in it and what it is for, points of contact, status (deprecated, experimental, not for general release), how to use it with copyable commands, and links to fuller docs.

**Slop signs** [Practitioner]:

| Sign | Fix |
|---|---|
| Emoji on every heading (🚀 Getting Started, ✨ Features, 📦 Installation, 🤝 Contributing) | Plain headings |
| Opener like "X is a powerful, lightweight and blazing-fast solution that seamlessly..." | One plain sentence: what it is, for whom |
| Features as bold-label bullets of generic qualities (`- **Lightning Fast:** Optimized for performance`) | Real capabilities, or a usage example that shows them |
| Placeholders: `yourusername/your-repo`, `[Project Name]`, `your-email@example.com` | Real values |
| Install or usage commands that do not match the project (wrong package name, wrong toolchain, nonexistent flags) | Run every command in a clean environment |
| Features the code does not implement; a project tree that does not match the repo | Describe only what exists |
| Empty boilerplate sections: Roadmap, Acknowledgments, "Contributions are welcome! Feel free to submit a PR." | Delete, or link a real CONTRIBUTING.md |
| Badges for CI/coverage that is not configured | Remove broken badges |
| Table of contents on a short README | Remove |
| "Comprehensive", "robust", "production-ready", "enterprise-grade" with no evidence | A number, a status line, or nothing |
| Closing flourish: "Made with ❤️", "Happy coding!", "⭐ Star this repo!" | Delete |

**A clean README, in order:**
1. Name and one sentence: what it does and for whom.
2. Status if it is not obviously stable (alpha, unmaintained, Linux only).
3. Install: the minimal command, tested.
4. Usage: one real example with real output; a screenshot or GIF if it is visual.
5. Only then: configuration, limitations, how to get help, how to contribute, license (relative links).

Every section needs project-specific content. No content, no heading.

**Presentation.** Match the ecosystem's norms (a Rust crate README looks different from a design-system README). Prefer one honest screenshot over a wall of badges. Put numbers where adjectives would be ("about 3x faster than X on `bench/large.csv`").

---

## 4. Commit messages

**Baseline** (Chris Beams, seven rules, widely adopted): separate subject from body with a blank line; subject about 50 characters; capitalise the subject; no period at the end; imperative mood ("Fix", not "Fixed"); wrap the body at 72; the body explains what and why, not how. The diff shows what changed; only the message can say why.

Projects may use Conventional Commits (`fix(upload): retry on 503`) or other formats; follow the repository's existing style first.

**Slop signs** [Practitioner]:
- Vague, inflated subjects: "Refactor code to improve readability and maintainability", "Enhance error handling and overall robustness", "Update various files".
- A body that lists every file or trivial change (restating the diff) and never says why.
- Claims the diff does not support: "Add comprehensive tests" for one test; "Improve performance" with no measurement.
- Markdown headings or bold in the body. (git also treats lines starting with `#` as comments and deletes them.)
- Past tense, first person ("I updated the function to...").
- Several unrelated changes swept into one sentence.

**Write commits like this:** one logical change; subject names the concrete change (`Retry S3 uploads on 503 SlowDown`); body says why, what alternatives were rejected, and side effects; issue references at the bottom (`Fixes #318`). If you cannot summarise it in one line, split the commit.

---

## 5. Pull request descriptions

**Slop signs** [Practitioner, Industry]:
- A heavy template (Summary / Changes / Testing / Impact) filled with generic bullets that restate file names.
- "Testing: All tests pass ✅" with no evidence, or claims contradicted by CI.
- Overclaiming: "significantly improves robustness and performance of the codebase".
- Huge sweeping changes the author cannot explain line by line. Maintainers have reported multi-thousand-line generated refactors that take days to review.
- Fixes for problems the project does not have, or bugs nobody reported, sometimes generated from AI-written issues. tldraw's founder described low-effort AI issues turning into low-effort AI PRs, with AI on both sides [Industry].
- Review replies that open with "You're absolutely right!" and change something else.

**Write PRs like this:**
- First line: the problem, linked to an issue.
- What changed and why this approach (and what you rejected).
- How you tested it: commands, environment, what you observed.
- What you are unsure about. Reviewers trust a PR that names its own risks.
- Small enough to review. If the repo has a PR template, fill every section honestly; write "Not tested on Windows" rather than deleting the heading.
- Disclose AI assistance where the project asks.

---

## 6. Issues, bug reports, security reports

Maintainers have documented the cost [Industry]. curl's founder Daniel Stenberg has written since early 2024 about polished AI-generated security reports describing bugs that do not exist. By mid-2025 about 20% of curl's bug-bounty submissions were slop and the share of valid reports had fallen below 5%; curl ended its HackerOne bounty on 31 January 2026 and asks reporters to disclose AI use. Other projects (tldraw, Ghostty) restricted outside contributions.

**Slop signs:**
- Confident, heavily formatted reports for vulnerabilities that do not exist.
- Generic vulnerability-class language ("potential buffer overflow", "could lead to memory corruption") without a working proof of concept, pointing at code that does not do what the report says.
- Follow-ups that restate the report or change the story when asked a specific question.
- Headings and bullet lists where a reproduction recipe belongs.

**Write reports like this:** exact version and platform; minimal steps or a script; expected vs actual output; for security, a proof of concept that actually triggers the issue and the exact code location you verified; disclosure of AI use if asked; answers to follow-up questions from your own understanding.

---

## 7. Slop in the code itself

### 7.1 Hallucinated packages ("slopsquatting") [Research]
Spracklen et al. (USENIX Security 2025) generated 576,000 Python and JavaScript samples with 16 LLMs and found 205,474 unique non-existent package names; rates ranged from about 5% (commercial models) to about 22% (open-source models). Many fake names recur across runs, so attackers can register them with malicious code. A 2026 replication (preprint) on newer models found lower rates but the risk still present.

**Prevent:** before adding any dependency, confirm it exists, is the package you meant (not a look-alike), is maintained, and has a plausible history. Pin versions; use lockfiles; read new `import` lines in generated code with suspicion.

### 7.2 Duplication instead of reuse [Industry, correlational]
GitClear's 2025 report (211M changed lines, 2020 to 2024) found an eightfold rise in 2024 in commits with duplicated blocks of five or more lines, copy/paste exceeding moved code for the first time, and short-term churn rising from 3.3% to 5.7%. This tracks AI-assistant adoption but is not line-level proof; Google's DORA 2024 report is more positive on quality. **Prevent:** search for an existing helper before accepting generated code; refactor rather than paste.

### 7.3 Other code-level slop [Practitioner]
- `try/except Exception: pass` or empty `catch {}` everywhere; redundant `None` checks on values that cannot be `None`.
- Unused imports, variables and parameters from a template.
- Mixed conventions in one file (naming, quotes, error handling) from pasted generations.
- Placeholder values: `API_KEY = "your-api-key-here"`, `https://example.com/api`, functions returning `True` under a docstring promising validation.
- Invented APIs: methods, flags or options that do not exist in the installed version.
- Curly quotes, em dashes or non-breaking spaces inside strings, shell commands or YAML (copied from rendered chat). These break code.
- Tests that cannot fail: tautological assertions, mocks replacing the unit under test.
- Over-engineering: factories, abstract base classes and config layers for a 30-line script.

**Prevent:** run the linter, type checker and tests; make one test fail deliberately to prove it tests something; check unfamiliar API calls against the docs for the installed version; read the diff as a reviewer would.

---

## 8. Before you hand over code-related text

- [ ] Comments explain why; none narrate code, address "you", or log changes.
- [ ] Docstrings match real behaviour; examples run.
- [ ] README: one-sentence opener; status; tested install and usage; no placeholders; only sections with real content; numbers instead of adjectives.
- [ ] Commit: imperative subject near 50 chars, blank line, body says why, no Markdown, follows repo convention.
- [ ] PR: problem, approach, real testing evidence, risks; reviewable size.
- [ ] Report: reproduction or working PoC; exact versions.
- [ ] Every new dependency verified; no placeholder credentials, swallowed errors, invented APIs or curly quotes in code.
- [ ] `python scripts/slop_scan.py` run on changed files and messages; all high findings fixed.
