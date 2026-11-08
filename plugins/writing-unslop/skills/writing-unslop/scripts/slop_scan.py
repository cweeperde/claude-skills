#!/usr/bin/env python3
"""slop_scan.py - flag common signs of AI-generated ("slop") writing.

Finds surface patterns that research and editors associate with LLM output:
chatbot leftovers, tool artifacts, placeholders, "AI vocabulary" density,
inflated significance, negative parallelisms, disclaimers, formatting tells,
and code-specific tells in comments, READMEs and commit messages.

It is a checklist with line numbers, not a detector. A clean scan does not
mean the text is good, and a noisy scan does not prove anything about who
wrote it. Content problems (vague claims, unverified facts) need a human or
model read; this script only points at places worth reading.

Usage:
    python slop_scan.py FILE [FILE ...]          # kind inferred from extension
    python slop_scan.py --kind commit msg.txt    # prose | markdown | code | commit
    cat draft.txt | python slop_scan.py -        # read stdin
    python slop_scan.py --json FILE              # machine-readable output
    python slop_scan.py --min-severity medium FILE

Exit code: 0 always (it is advisory), unless --fail-on is given:
    --fail-on high   exit 1 if any high-severity finding exists
Only the Python standard library is used.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, asdict
from pathlib import Path

SEVERITY_ORDER = {"low": 0, "medium": 1, "high": 2}

CODE_EXTS = {
    ".py", ".js", ".jsx", ".ts", ".tsx", ".go", ".rs", ".java", ".kt", ".kts",
    ".c", ".h", ".cc", ".cpp", ".hpp", ".cs", ".rb", ".php", ".swift", ".scala",
    ".sh", ".bash", ".zsh", ".lua", ".dart", ".m", ".mm", ".r", ".jl", ".ex",
    ".exs", ".hs", ".sql", ".yaml", ".yml", ".toml",
}
MARKDOWN_EXTS = {".md", ".markdown", ".mdx", ".rst"}


@dataclass
class Finding:
    file: str
    line: int
    category: str
    severity: str
    match: str
    advice: str


# ---------------------------------------------------------------------------
# Pattern tables. Each entry: (regex, category, severity, advice)
# Regexes are applied per line, case-insensitive unless noted.
# ---------------------------------------------------------------------------

CHAT_LEFTOVERS = [
    (r"\b(certainly|absolutely|of course)[!,.]\s", "chat-leftover", "high",
     "Reply to a prompt, not text for a reader. Delete."),
    (r"\bgreat question\b", "chat-leftover", "high", "Chat filler. Delete."),
    (r"\byou'?re (absolutely )?right\b", "chat-leftover", "medium",
     "Chat agreement phrase. Delete or state what changed."),
    (r"\bi hope this helps\b", "chat-leftover", "high", "Chat sign-off. Delete."),
    (r"\b(let me know if|feel free to (reach out|ask|let me know))\b", "chat-leftover", "high",
     "Chat sign-off addressed to the prompter. Delete."),
    (r"\bwould you like me to\b", "chat-leftover", "high", "Offer to the prompter. Delete."),
    (r"\bhere(?:'s| is) (a|an|the) (revised|updated|improved|detailed|comprehensive|quick)\b",
     "chat-leftover", "high", "Preamble from a chat reply. Delete."),
    (r"\bas an ai( language model)?\b|\bas a large language model\b", "chat-leftover", "high",
     "Model self-reference. Delete."),
    (r"\b(as of|up to) my (last|latest) (knowledge|training) (update|cutoff|cut-off)\b",
     "chat-leftover", "high", "Knowledge-cutoff disclaimer. Delete; verify the fact instead."),
    (r"\bin the (provided|available) (sources|search results|documents|context)\b",
     "chat-leftover", "high", "Refers to the model's inputs. Rewrite or cut."),
    (r"\bbased on (the )?available information\b", "hedge-gap", "medium",
     "Hedge that usually precedes speculation. Find out or cut."),
    (r"\b(specific )?(details|information) (about|on|regarding) .{0,60}\b(is|are) (limited|scarce|not (widely )?(available|documented))\b",
     "hedge-gap", "high", "Gap-hedge followed by guessing. Find the fact or say nothing."),
    (r"\bnot (widely|extensively|well) documented\b", "hedge-gap", "high",
     "Gap-hedge. Find the fact or cut the sentence."),
    (r"^\s*subject:\s", "chat-leftover", "medium",
     "Email subject line pasted into body text."),
    (r"\bin this (section|article|post|guide|document),? (we|i) will\b", "meta-statement", "medium",
     "Announces content instead of giving it. Start with the content."),
    (r"\b(this|the following) (article|guide|post|document) (explores|delves|dives)\b", "meta-statement", "medium",
     "Announces content instead of giving it."),
    (r"\blet'?s (dive|delve) in(to)?\b", "chat-leftover", "medium", "Chat opener. Delete."),
]

ARTIFACTS = [
    (r"(cite|i)turn\d+(search|news|image|file)\d+", "tool-artifact", "high",
     "ChatGPT citation token pasted from a chat. Remove and cite properly."),
    (r"contentReference\[oaicite", "tool-artifact", "high", "ChatGPT reference bug. Remove."),
    (r"oai_citation", "tool-artifact", "high", "ChatGPT citation label. Remove."),
    (r"attributableIndex", "tool-artifact", "high", "ChatGPT attribution JSON. Remove."),
    (r"utm_source=(chatgpt\.com|openai|perplexity|copilot)", "tool-artifact", "high",
     "Chatbot tracking parameter on a URL. Strip it and check the link."),
    (r"\[(attached_file|web):\d+\]", "tool-artifact", "high", "Chat citation tag. Remove."),
    (r"grok_card", "tool-artifact", "high", "Grok markup. Remove."),
    (r"<\|endoftext\|>|<\|im_(start|end)\|>", "tool-artifact", "high", "Model control token. Remove."),
    (r"```wikitext", "tool-artifact", "high", "Fenced chat code block pasted as content."),
    (r"↩", "tool-artifact", "medium", "Footnote back-arrow copied from rendered chat output."),
]

PLACEHOLDERS = [
    (r"\[(your|insert|add|describe|enter|project|company|name|author|date|link|url)[^\]]{0,60}\]",
     "placeholder", "high", "Unfilled template slot."),
    (r"\b(19|20)\d\d-(xx|XX)-(xx|XX)\b", "placeholder", "high", "Placeholder date."),
    (r"\b(your[-_]?(username|user|repo|project|api[-_]?key|token|email|name|domain|org))\b",
     "placeholder", "high", "Placeholder value left in."),
    (r"your-email@|you@example\.com|user@example\.com", "placeholder", "high", "Placeholder email."),
    (r"\blorem ipsum\b", "placeholder", "high", "Filler text."),
    (r"\[needs:[^\]]*\]", "open-marker", "high",
     "Open [needs: ...] marker from an unslop pass. Fill it with a real fact or cut the claim before publishing."),
    (r"<!--\s*(add|insert|todo|fill)[^>]*-->", "placeholder", "high", "Placeholder comment."),
]

INFLATION = [
    (r"\b(stands|serves) as (a|an|the)\b", "copula-avoidance", "low",
     "Usually 'is'. Use the plain verb."),
    (r"\b(is|as|remains) a (testament|reminder) (to|of)\b", "inflated-significance", "medium",
     "Asserts significance. Show a concrete consequence or cut."),
    (r"\bplays? an? (vital|significant|crucial|pivotal|key|important|critical|central) role\b",
     "inflated-significance", "medium", "Vague importance claim. Say what it does."),
    (r"\b(pivotal|key|significant) (moment|turning point|milestone)\b", "inflated-significance", "medium",
     "Asserted significance. Give the fact and its effect."),
    (r"\b(enduring|lasting|indelible) (legacy|impact|mark|influence)\b", "inflated-significance", "medium",
     "Legacy-speak. Cut or replace with evidence."),
    (r"\b(rich|vibrant|diverse) (tapestry|heritage|history|culture|landscape)\b", "promotional", "medium",
     "Stock praise. Replace with a specific detail."),
    (r"\b(deeply rooted|profound heritage|steadfast (dedication|commitment))\b", "inflated-significance", "medium",
     "Stock praise."),
    (r"\b(reflects|underscores|highlights|showcases|exemplifies) (the|its|their|a) (broader|growing|importance|significance|commitment|enduring)\b",
     "inflated-significance", "medium", "Interpretive claim with no actor. Attribute it or cut."),
    (r"\bnestled\b|\bin the heart of\b|\bboasts\b|\bbreathtaking\b|\bstunning\b|\bmust-(see|visit|have)\b",
     "promotional", "medium", "Advertising tone. Replace with a checkable fact."),
    (r"\b(continues to (captivate|inspire|thrive|evolve))\b", "promotional", "medium", "Stock ending. Cut."),
    (r"\b(game[- ]chang(er|ing)|cutting[- ]edge|state[- ]of[- ]the[- ]art|world[- ]class|best[- ]in[- ]class|next[- ]generation|revolutioni[sz]e)\b",
     "promotional", "medium", "Marketing claim. Back it with a number or cut."),
    (r"\b(blazing(ly)?[- ]fast|lightning[- ]fast|enterprise[- ]grade|production[- ]ready|battle[- ]tested)\b",
     "promotional", "low", "Unbacked technical claim. Give a benchmark or status instead."),
    (r"\bmaintains? an? (active|strong) (social media|online|digital) presence\b", "promotional", "medium",
     "Idiosyncratic AI phrasing. Cut."),
]

RHETORIC = [
    (r"\bnot only\b[^.?!]{1,120}\bbut (also)?\b", "negative-parallelism", "medium",
     "'Not only X but Y'. Usually just say Y."),
    (r"\b(it'?s|it is|this is|that'?s) not (just|only|merely|simply)?\s?(about )?[^.?!,;]{1,60}[,;—–-]\s*(it'?s|it is|but)\b",
     "negative-parallelism", "medium", "'It's not X, it's Y'. State Y directly."),
    (r"\bno [\w\s'-]{1,30}\.\s+no [\w\s'-]{1,30}\.\s+(just|only)\b", "outline-of-negatives", "high",
     "'No X. No Y. Just Z.' Make the positive claim once."),
    (r"\bnot [\w\s'-]{1,30},\s*not [\w\s'-]{1,30},\s*(and )?(certainly )?not\b", "outline-of-negatives", "high",
     "'Not A, not B, not C'. Make the positive claim once."),
    (r"\b(it'?s|it is) (important|crucial|critical|essential|worth|vital) (to )?(note|remember|consider|mention|noting|emphasi[sz]e)\b",
     "disclaimer", "medium", "Didactic aside. State the caveat as a fact where it applies, or cut."),
    (r"\b(results|experiences|mileage) may vary\b", "disclaimer", "low", "Generic disclaimer."),
    (r"^\W*(in (summary|conclusion|short|essence)|to (sum up|summari[sz]e|conclude)|overall),", "summary", "medium",
     "Restating summary. End when you are done."),
    (r"\bdespite (its|their|these|this|the) [^.]{0,60}\bchallenges\b", "challenges-formula", "medium",
     "'Despite challenges...' formula. Name the specific problem or cut."),
    (r"\b(faces|face) (several|numerous|many|a number of) challenges\b", "challenges-formula", "medium",
     "Challenges formula. Be specific."),
    (r"\b(future (outlook|prospects|directions)|looking ahead)\b", "challenges-formula", "low",
     "Speculative outlook section. Keep only if sourced and specific."),
    (r"\b(some|many) (critics|experts|observers|scholars|researchers) (argue|say|believe|note|suggest)\b",
     "vague-attribution", "medium", "Who, exactly? Name and link the source or cut."),
    (r"\b(industry (reports|experts)|observers have (noted|cited)|has been described as|is widely (regarded|considered|recognized))\b",
     "vague-attribution", "medium", "Weasel attribution. Name the source."),
    (r"\bfrom [\w\s'-]{2,40} to [\w\s'-]{2,40}, from [\w\s'-]{2,40} to\b", "false-range", "medium",
     "Stacked 'from X to Y' with no real scale. List plainly."),
    (r"[,;]\s+(highlighting|underscoring|emphasi[sz]ing|showcasing|reflecting|demonstrating|illustrating|symboli[sz]ing|cementing|solidifying|reinforcing)\s+(the|its|their|his|her|a|an|how)\b",
     "trailing-ing-analysis", "medium",
     "Trailing '-ing' interpretation. Delete it and check if anything was lost."),
    (r"[,;]\s+(ensuring|fostering|contributing to|paving the way for|aligning with)\b",
     "trailing-ing-analysis", "low", "Trailing '-ing' clause. Often filler."),
]

# Words that research found disproportionately in LLM output. Counted for density;
# a single hit is meaningless. Stems allow inflections.
AI_VOCAB = [
    "delve", "delves", "delving", "intricate", "intricacies", "tapestry", "testament",
    "underscore", "underscores", "underscoring", "pivotal", "realm", "showcase",
    "showcases", "showcasing", "multifaceted", "nuanced", "meticulous", "meticulously",
    "seamless", "seamlessly", "leverage", "leverages", "leveraging", "robust",
    "streamline", "streamlines", "streamlined", "foster", "fosters", "fostering",
    "garner", "garnered", "garnering", "vibrant", "crucial", "vital", "enduring",
    "interplay", "landscape", "underpin", "underpins", "underpinning", "notably",
    "comprehensive", "holistic", "paramount", "commendable", "embark", "embarks",
    "endeavor", "endeavour", "elevate", "elevates", "empower", "empowers",
    "empowering", "unlock", "unlocks", "unleash", "harness", "harnessing", "navigate",
    "navigating", "ever-evolving", "ever-changing", "transformative", "groundbreaking",
    "synergy", "bustling", "beacon", "symphony", "intrinsic", "noteworthy",
]
AI_PHRASES = [
    "shed light on", "sheds light on", "a testament to", "in today's fast-paced",
    "in the ever-evolving", "plays a crucial role", "plays a vital role",
    "plays a pivotal role", "aligns with", "align with", "key takeaways",
    "dive deep", "deep dive", "at the end of the day", "in the realm of",
    "navigate the complexities", "the intricacies of", "a rich tapestry",
    "it's worth noting", "it is worth noting",
]

CONNECTIVES = re.compile(
    r"(?:^|[.!?]\s+)(Additionally|Furthermore|Moreover|In addition|Consequently|Notably|Importantly|Ultimately|Overall),",
)

# Code-comment tells (applied to extracted comment text only)
CODE_COMMENT_RULES = [
    (r"^\s*step \d+\s*[:.)-]", "comment-step", "medium",
     "Tutorial step numbering in code. Comment the why, not the sequence."),
    (r"\b(replace (this )?with your|you (can|may|might|should|will) (adjust|change|modify|customi[sz]e|replace|want)|make sure (to|you)|don'?t forget to|feel free to)\b",
     "comment-to-user", "high", "Comment addressed to the prompter. Fix the code or delete."),
    (r"^\s*(updated|changed|modified|fixed|added|removed|new|edit)\s*:", "comment-changelog", "medium",
     "Change-history comment. History belongs in the commit message."),
    (r"^\s*(updated|changed|modified) to\b|^\s*now (handles|uses|supports|returns)\b", "comment-changelog", "low",
     "Describes a change rather than the code. Usually belongs in the commit message."),
    (r"\b(robust|comprehensive|elegant|seamless|powerful)\s+(and \w+ )?(implementation|solution|handling|approach)\b",
     "comment-promotional", "medium", "Self-praise in a comment. Say what it does or delete."),
    (r"\b(this should work( in most cases| for most|\.?$)|should handle most cases|may need (adjust|tweak)ment|adjust as needed|depending on your (use case|needs|requirements))\b",
     "comment-hedge", "medium", "Hedge comment. State the actual limitation."),
    (r"\b(implement (actual|real|proper)|add (your|actual|real) (logic|implementation|code)|placeholder (logic|implementation)|for (demo|demonstration|example) purposes|in a real (app|application|implementation|scenario))\b",
     "comment-placeholder", "high", "Placeholder presented as working code. Implement it or mark a tracked TODO."),
]
NARRATION_START = re.compile(
    r"^\s*(initiali[sz]e|create|define|declare|set|get|call|loop( through| over)?|iterate( through| over)?|"
    r"return|import|check (if|whether)|increment|append|add|print|store|assign|instantiate|open|close|"
    r"convert|calculate|compute|update)\b[\w\s,'()]{0,60}$",
    re.IGNORECASE,
)

EMOJI = re.compile(
    "[\U0001F300-\U0001FAFF\U00002600-\U000027BF\U0001F000-\U0001F2FF⭐⬆↔-⇿✅❌✨]"
)
CURLY = re.compile("[“”‘’]")
WORD = re.compile(r"[A-Za-z][A-Za-z'-]*")


def compile_table(table):
    return [(re.compile(rx, re.IGNORECASE), cat, sev, adv) for rx, cat, sev, adv in table]


TABLES_PROSE = compile_table(CHAT_LEFTOVERS + ARTIFACTS + PLACEHOLDERS + INFLATION + RHETORIC)
TABLE_ARTIFACTS = compile_table(ARTIFACTS + PLACEHOLDERS)
TABLE_COMMENTS = compile_table(CODE_COMMENT_RULES)
TABLE_COMMENT_PROSE = compile_table(CHAT_LEFTOVERS + INFLATION)
VOCAB_RE = re.compile(r"\b(" + "|".join(re.escape(w) for w in AI_VOCAB) + r")\b", re.IGNORECASE)
PHRASE_RE = re.compile("|".join(re.escape(p) for p in AI_PHRASES), re.IGNORECASE)


def infer_kind(path: str) -> str:
    if path == "-":
        return "prose"
    p = Path(path)
    name = p.name.upper()
    if name in {"COMMIT_EDITMSG", "MERGE_MSG"}:
        return "commit"
    ext = p.suffix.lower()
    if ext in MARKDOWN_EXTS:
        return "markdown"
    if ext in CODE_EXTS:
        return "code"
    return "prose"


def strip_fences(lines):
    """Yield (lineno, text, in_code_fence) for markdown/prose."""
    in_fence = False
    for i, line in enumerate(lines, 1):
        if line.lstrip().startswith(("```", "~~~")):
            in_fence = not in_fence
            yield i, line, True
            continue
        yield i, line, in_fence


def scan_table(fname, lineno, text, table, out):
    for rx, cat, sev, adv in table:
        m = rx.search(text)
        if m:
            out.append(Finding(fname, lineno, cat, sev, m.group(0).strip()[:80], adv))


def scan_prose(fname, lines, out, markdown=False):
    words_total = 0
    vocab_hits = []
    emdash = 0
    bold_spans = 0
    inline_header_bullets = []
    headings = []
    for lineno, line, in_fence in strip_fences(lines):
        if in_fence:
            # Code blocks in docs: curly quotes break commands; artifacts still count.
            if CURLY.search(line) and not line.lstrip().startswith(("```", "~~~")):
                out.append(Finding(fname, lineno, "curly-quotes-in-code", "high",
                                   CURLY.search(line).group(0),
                                   "Typographic quote inside a code block will break copy-paste."))
            scan_table(fname, lineno, line, TABLE_ARTIFACTS, out)
            continue
        scan_table(fname, lineno, line, TABLES_PROSE, out)
        words_total += len(WORD.findall(line))
        for m in VOCAB_RE.finditer(line):
            vocab_hits.append((lineno, m.group(0)))
        for m in PHRASE_RE.finditer(line):
            vocab_hits.append((lineno, m.group(0)))
        emdash += line.count("—")
        bold_spans += len(re.findall(r"\*\*[^*]+\*\*|__[^_]+__", line))
        if CONNECTIVES.search(line):
            out.append(Finding(fname, lineno, "formulaic-connective", "low",
                               CONNECTIVES.search(line).group(1),
                               "Stock connective. Keep only if the logical link is real."))
        if re.match(r"^\s*([-*+•]|\d+[.)])\s+\*\*[^*]{1,60}:?\*\*:?\s", line):
            inline_header_bullets.append(lineno)
        hm = re.match(r"^\s{0,3}(#{1,6})\s+(.*)$", line) if markdown else None
        if hm:
            htext = hm.group(2).strip()
            headings.append((lineno, htext))
            if EMOJI.search(htext):
                out.append(Finding(fname, lineno, "emoji-heading", "medium", htext[:60],
                                   "Decorative emoji in a heading. Remove unless it is the project's voice."))
        elif EMOJI.search(line) and re.match(r"^\s*([-*+•]|\d+[.)])\s", line):
            out.append(Finding(fname, lineno, "emoji-bullet", "low", line.strip()[:60],
                               "Emoji used as bullet decoration."))
        if re.search(r"(made with (❤️|love)|happy coding|star (this|the) repo|⭐)", line, re.I):
            out.append(Finding(fname, lineno, "readme-flourish", "medium", line.strip()[:60],
                               "Closing flourish. Delete."))
        if re.search(r"contributions are welcome!?\s*(please )?feel free", line, re.I):
            out.append(Finding(fname, lineno, "readme-boilerplate", "medium", line.strip()[:60],
                               "Boilerplate contributing line. Link CONTRIBUTING.md or say how to contribute."))

    # Density-based findings (whole document)
    if words_total:
        per_k = 1000 * len(vocab_hits) / words_total
        distinct = sorted({w.lower() for _, w in vocab_hits})
        if len(vocab_hits) >= 3 and per_k >= 6:
            sev = "high" if per_k >= 15 else "medium"
            first_lines = ", ".join(str(l) for l in sorted({l for l, _ in vocab_hits})[:10])
            out.append(Finding(fname, vocab_hits[0][0], "ai-vocabulary-density", sev,
                               f"{len(vocab_hits)} hits ({per_k:.1f}/1000 words): {', '.join(distinct[:12])}",
                               f"Lines {first_lines}. Replace each with the concrete claim or delete; do not just swap synonyms."))
        elif vocab_hits:
            out.append(Finding(fname, vocab_hits[0][0], "ai-vocabulary", "low",
                               ", ".join(distinct[:12]),
                               "A few hits are normal. Check each carries meaning."))
        em_per_k = 1000 * emdash / words_total
        if emdash >= 3 and em_per_k >= 8:
            out.append(Finding(fname, 1, "em-dash-density", "low",
                               f"{emdash} em dashes ({em_per_k:.1f}/1000 words)",
                               "Weak signal alone. Vary with commas, colons, parentheses, full stops."))
        bold_per_k = 1000 * bold_spans / words_total
        if bold_spans >= 5 and bold_per_k >= 15:
            out.append(Finding(fname, 1, "bold-density", "medium",
                               f"{bold_spans} bold spans ({bold_per_k:.1f}/1000 words)",
                               "Mechanical emphasis. Bold at most what a reader must not miss."))
    if len(inline_header_bullets) >= 3:
        out.append(Finding(fname, inline_header_bullets[0], "inline-header-list", "medium",
                           f"{len(inline_header_bullets)} '- **Label:** text' bullets",
                           "Use prose for reasoning; keep lists for parallel, scannable items."))
    titled = [(l, h) for l, h in headings if is_title_case(h)]
    if len(headings) >= 3 and len(titled) / len(headings) >= 0.6:
        out.append(Finding(fname, titled[0][0], "title-case-headings", "low",
                           f"{len(titled)}/{len(headings)} headings in Title Case",
                           "Most technical style guides use sentence case."))


SMALL_WORDS = {"a", "an", "the", "and", "or", "but", "for", "nor", "on", "at", "to", "by", "in",
               "of", "with", "vs", "via", "as", "is"}


def is_title_case(h: str) -> bool:
    words = [w for w in re.findall(r"[A-Za-z][\w'-]*", h)]
    content = [w for w in words if w.lower() not in SMALL_WORDS]
    if len(content) < 3:
        return False
    caps = sum(1 for w in content[1:] if w[0].isupper() and not w.isupper())
    return caps >= max(2, len(content[1:]) * 0.8)


# ---------------------------------------------------------------------------
# Code scanning
# ---------------------------------------------------------------------------

LINE_COMMENT = re.compile(r"(?:^|\s)(#|//|--|;)\s?(.*)$")


def extract_comments(lines, ext):
    """Return list of (lineno, comment_text, kind) where kind is 'line', 'block' or 'doc'."""
    comments = []
    in_block = False
    in_doc = None
    hash_langs = {".py", ".rb", ".sh", ".bash", ".zsh", ".r", ".jl", ".ex", ".exs", ".yaml", ".yml", ".toml"}
    dash_langs = {".sql", ".lua", ".hs"}
    for i, raw in enumerate(lines, 1):
        line = raw.rstrip("\n")
        stripped = line.strip()
        if in_doc:
            text = stripped
            if in_doc in text:
                text = text.split(in_doc)[0]
                in_doc = None
            if text:
                comments.append((i, text, "doc"))
            continue
        if in_block:
            text = stripped.lstrip("*").strip()
            if "*/" in text:
                text = text.split("*/")[0].strip()
                in_block = False
            if text:
                comments.append((i, text, "block"))
            continue
        if ext == ".py":
            m = re.match(r'^\s*[rubRUB]?("""|\'\'\')(.*)$', line)
            if m:
                q, rest = m.group(1), m.group(2)
                if q in rest:
                    comments.append((i, rest.split(q)[0].strip(), "doc"))
                else:
                    if rest.strip():
                        comments.append((i, rest.strip(), "doc"))
                    in_doc = q
                continue
        if "/*" in line and ext not in hash_langs:
            after = line.split("/*", 1)[1]
            if "*/" in after:
                comments.append((i, after.split("*/")[0].strip("* ").strip(), "block"))
            else:
                comments.append((i, after.strip("* ").strip(), "block"))
                in_block = True
            continue
        # Line comments: pick the marker for the language, avoid matching inside strings crudely
        marker = "#" if ext in hash_langs else ("--" if ext in dash_langs else "//")
        idx = find_comment_marker(line, marker)
        if idx is not None:
            comments.append((i, line[idx + len(marker):].strip(), "line"))
    return comments


def find_comment_marker(line, marker):
    """Find a comment marker outside simple string literals. Heuristic."""
    quote = None
    i = 0
    while i < len(line):
        ch = line[i]
        if quote:
            if ch == "\\":
                i += 2
                continue
            if ch == quote:
                quote = None
        else:
            if ch in "\"'`":
                quote = ch
            elif line.startswith(marker, i):
                if marker == "#" and i > 0 and line[i - 1] in "$&":  # shell $#, html entities
                    i += 1
                    continue
                if marker == "//" and i > 0 and line[i - 1] == ":":  # URLs
                    i += 1
                    continue
                return i
        i += 1
    return None


STRING_LIT = re.compile(r"(\"(?:[^\"\\]|\\.)*\"|'(?:[^'\\]|\\.)*'|`(?:[^`\\]|\\.)*`)")
CODE_PLACEHOLDER = re.compile(
    r"(your[-_ ]?(api[-_ ]?key|token|secret|password|username|domain|endpoint)[-_ ]?(here)?|"
    r"(api|secret)[-_]?key[-_]?here|(?<![\\\w])x{4,}(?!\w)|changeme|replace[-_ ]?me|example\.com|todo:? ?replace)",
    re.IGNORECASE,
)


def scan_code(fname, lines, out, ext):
    comments = extract_comments(lines, ext)
    code_lines = sum(1 for l in lines if l.strip())
    narr = []
    for lineno, text, kind in comments:
        if not text:
            continue
        scan_table(fname, lineno, text, TABLE_COMMENTS, out)
        scan_table(fname, lineno, text, TABLE_COMMENT_PROSE, out)
        if kind == "line" and NARRATION_START.match(text) and len(text.split()) <= 12:
            narr.append(lineno)
        if EMOJI.search(text):
            out.append(Finding(fname, lineno, "comment-emoji", "low", text[:60], "Emoji in a code comment."))
        if kind == "doc" and re.match(r"^(this (function|method|class)|a (simple|robust|powerful|helper|utility))\b", text, re.I):
            out.append(Finding(fname, lineno, "docstring-restates", "low", text[:60],
                               "Docstring opener that restates or praises. Say what it returns or does, specifically."))
    banners = [l for l, t, k in comments if re.match(r"^[=\-#*~]{3,}.*\w.*[=\-#*~]{3,}$", t)]
    if banners and code_lines and len(banners) / code_lines > 0.05:
        out.append(Finding(fname, banners[0], "comment-banner", "low", f"{len(banners)} section banners",
                           "Many banners for a short file. Usually template structure."))
    line_comments = [c for c in comments if c[2] == "line" and c[1]]
    if len(narr) >= 3 and len(narr) >= 0.2 * len(line_comments):
        out.append(Finding(fname, narr[0], "comment-narration", "medium",
                           f"{len(narr)} comments narrate the next line (lines {', '.join(map(str, narr[:8]))})",
                           "Comments that restate code add clutter and go stale. Keep only the why."))
    if code_lines and comments:
        ratio = len(comments) / code_lines
        if ratio > 0.6 and len(comments) >= 10:
            out.append(Finding(fname, 1, "comment-density", "low",
                               f"{len(comments)} comment lines for {code_lines} non-blank lines",
                               "Very high comment ratio; check for narration."))
    for i, line in enumerate(lines, 1):
        if re.match(r"^\s*except\s*(Exception|BaseException)?\s*(as \w+)?\s*:\s*$", line):
            nxt = next((l for l in lines[i:] if l.strip()), "")
            if nxt.strip() in {"pass", "..."}:
                out.append(Finding(fname, i, "swallowed-exception", "medium", line.strip()[:60],
                                   "Catch-all that silently swallows errors. Catch a specific error or let it raise."))
        for m in STRING_LIT.finditer(line):
            lit = m.group(0)
            if EMOJI.search(lit):
                out.append(Finding(fname, i, "emoji-in-string", "low", lit[:60],
                                   "Emoji in a log/print string. Unusual outside UI text."))
            if CODE_PLACEHOLDER.search(lit):
                out.append(Finding(fname, i, "placeholder-value", "high", lit[:60],
                                   "Placeholder credential or endpoint. Load from config or fail loudly."))
        if CURLY.search(line):
            out.append(Finding(fname, i, "curly-quotes-in-code", "high", CURLY.search(line).group(0),
                               "Typographic quote in code. Probably pasted from rendered chat; will break."))
        scan_table(fname, i, line, compile_table(ARTIFACTS), out)
        if re.search(r"except\s*(Exception)?\s*(as \w+)?\s*:\s*(pass|\.\.\.)\s*$", line) or \
                re.search(r"catch\s*\([^)]*\)\s*\{\s*\}", line):
            out.append(Finding(fname, i, "swallowed-exception", "medium", line.strip()[:60],
                               "Error swallowed silently. Handle a specific error or let it raise."))


# ---------------------------------------------------------------------------
# Commit messages
# ---------------------------------------------------------------------------

def scan_commit(fname, lines, out):
    # git strips lines starting with '#'; keep original line numbers for reporting
    numbered = [(i, l) for i, l in enumerate(lines, 1) if not l.startswith("#")]
    while numbered and not numbered[0][1].strip():
        numbered.pop(0)
    if not numbered:
        return
    stripped_md = [(i, l) for i, l in enumerate(lines, 1) if re.match(r"^#{1,6}\s+\S", l)]
    for i, l in stripped_md:
        out.append(Finding(fname, i, "commit-markdown", "medium", l.strip()[:60],
                           "Markdown heading in a commit message: git treats '#' lines as comments and deletes them."))
    subj_line, subject = numbered[0]
    rest = numbered[1:]
    if len(subject) > 72:
        out.append(Finding(fname, subj_line, "commit-subject-length", "medium", f"{len(subject)} chars",
                           "Keep the subject near 50 characters (hard limit ~72)."))
    elif len(subject) > 50:
        out.append(Finding(fname, subj_line, "commit-subject-length", "low", f"{len(subject)} chars",
                           "Aim for about 50 characters."))
    if subject.rstrip().endswith("."):
        out.append(Finding(fname, subj_line, "commit-subject-period", "low", subject[-20:],
                           "No period at the end of the subject."))
    first = re.sub(r"^(\w+(\([^)]*\))?!?:\s*)", "", subject).split(" ")[0] if subject else ""
    if re.match(r"^[A-Za-z]+ed$", first) and first.lower() not in {"embed", "need", "speed", "seed", "feed", "shed", "bed", "red"}:
        out.append(Finding(fname, subj_line, "commit-mood", "low", first,
                           "Use the imperative ('Fix', not 'Fixed')."))
    if re.search(r"\b(enhance|improve|refactor|update|optimi[sz]e|clean)\w*\b.*\b(readability|maintainability|robustness|performance|overall|code quality|various|several|codebase)\b",
                 subject, re.I):
        out.append(Finding(fname, subj_line, "commit-vague-subject", "medium", subject[:72],
                           "Vague, inflated subject. Name the concrete change."))
    if rest and rest[0][1].strip() and rest[0][0] == subj_line + 1:
        out.append(Finding(fname, rest[0][0], "commit-no-blank-line", "medium", rest[0][1][:40],
                           "Separate subject and body with a blank line."))
    for i, l in rest:
        if "**" in l:
            out.append(Finding(fname, i, "commit-markdown", "medium", l.strip()[:60],
                               "Bold markup renders as raw asterisks in git log."))
        if len(l.rstrip("\n")) > 100 and not re.search(r"https?://", l):
            out.append(Finding(fname, i, "commit-wrap", "low", f"{len(l)} chars", "Wrap the body near 72 characters."))
        if re.match(r"^\s*i (have )?(updated|changed|added|fixed|refactored|modified)\b", l, re.I):
            out.append(Finding(fname, i, "commit-first-person", "low", l.strip()[:60],
                               "First-person narration. Describe the change and why."))
    bullets = [l for _, l in rest if re.match(r"^\s*[-*]\s", l)]
    why = re.search(r"\b(because|so that|since|otherwise|caused|fails?|failing|bug|issue|#\d+|to avoid|to prevent|when|without)\b",
                    " ".join(l for _, l in rest), re.I)
    if len(bullets) >= 4 and not why:
        out.append(Finding(fname, rest[0][0], "commit-what-not-why", "medium", f"{len(bullets)} bullets, no stated reason",
                           "Body lists changes (the diff already shows them). Explain why."))
    body = [l for _, l in numbered]
    # Prose checks on body
    scan_prose(fname, body, out)


# ---------------------------------------------------------------------------

def scan_text(fname, text, kind):
    lines = text.splitlines()
    out: list[Finding] = []
    if kind == "code":
        scan_code(fname, lines, out, Path(fname).suffix.lower())
    elif kind == "commit":
        scan_commit(fname, lines, out)
    else:
        scan_prose(fname, lines, out, markdown=(kind == "markdown"))
    # de-duplicate identical (line, category)
    seen = set()
    uniq = []
    for f in out:
        key = (f.line, f.category, f.match)
        if key not in seen:
            seen.add(key)
            uniq.append(f)
    uniq.sort(key=lambda f: (f.file, f.line, -SEVERITY_ORDER[f.severity]))
    return uniq


def summarize(findings):
    counts = {"high": 0, "medium": 0, "low": 0}
    for f in findings:
        counts[f.severity] += 1
    score = counts["high"] * 5 + counts["medium"] * 2 + counts["low"]
    if counts["high"]:
        verdict = "Has leftovers/placeholders/artifacts: fix these first, they are near-certain problems."
    elif score >= 12:
        verdict = "Many stylistic tells: do a full unslop pass (content first, then style)."
    elif score >= 4:
        verdict = "Some tells: review the flagged lines."
    else:
        verdict = "Few surface tells. Still read for vague or unverified content; the scanner cannot see that."
    return counts, score, verdict


def main(argv=None):
    ap = argparse.ArgumentParser(description="Flag common signs of AI-generated writing (advisory).")
    ap.add_argument("files", nargs="+", help="files to scan, or - for stdin")
    ap.add_argument("--kind", choices=["prose", "markdown", "code", "commit"],
                    help="override kind inference")
    ap.add_argument("--json", action="store_true", help="emit JSON")
    ap.add_argument("--min-severity", choices=["low", "medium", "high"], default="low")
    ap.add_argument("--fail-on", choices=["low", "medium", "high"], help="exit 1 if a finding at this level exists")
    args = ap.parse_args(argv)

    all_findings = []
    for path in args.files:
        if path == "-":
            text = sys.stdin.read()
        else:
            try:
                text = Path(path).read_text(encoding="utf-8", errors="replace")
            except OSError as e:
                print(f"slop_scan: cannot read {path}: {e}", file=sys.stderr)
                continue
        kind = args.kind or infer_kind(path)
        all_findings.extend(scan_text(path, text, kind))

    minsev = SEVERITY_ORDER[args.min_severity]
    shown = [f for f in all_findings if SEVERITY_ORDER[f.severity] >= minsev]
    counts, score, verdict = summarize(all_findings)

    if args.json:
        print(json.dumps({"findings": [asdict(f) for f in shown], "counts": counts,
                          "score": score, "verdict": verdict}, indent=2, ensure_ascii=False))
    else:
        if not shown:
            print("No findings at this severity.")
        current = None
        for f in shown:
            if f.file != current:
                current = f.file
                print(f"\n== {f.file}")
            print(f"  L{f.line:<5} [{f.severity:<6}] {f.category}: {f.match}")
            print(f"         -> {f.advice}")
        print(f"\nSummary: {counts['high']} high, {counts['medium']} medium, {counts['low']} low (score {score}).")
        print(verdict)
        print("Signals, not proof: use them to find places to rewrite, never to judge authorship.")

    if args.fail_on:
        lvl = SEVERITY_ORDER[args.fail_on]
        if any(SEVERITY_ORDER[f.severity] >= lvl for f in all_findings):
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
