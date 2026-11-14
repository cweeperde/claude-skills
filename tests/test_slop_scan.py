"""Tests for plugins/writing-unslop/skills/writing-unslop/scripts/slop_scan.py."""
import importlib.util
import json
import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "plugins/writing-unslop/skills/writing-unslop/scripts/slop_scan.py"

spec = importlib.util.spec_from_file_location("slop_scan", SCRIPT)
slop_scan = importlib.util.module_from_spec(spec)
sys.modules["slop_scan"] = slop_scan  # dataclasses look the module up here
spec.loader.exec_module(slop_scan)


def categories(text, kind="prose", fname="x.txt"):
    return {f.category for f in slop_scan.scan_text(fname, text, kind)}


def findings(text, kind="prose", fname="x.txt"):
    return slop_scan.scan_text(fname, text, kind)


# --- kind inference ---------------------------------------------------------

@pytest.mark.parametrize("path,kind", [
    ("README.md", "markdown"),
    ("notes.rst", "markdown"),
    ("main.py", "code"),
    ("app.tsx", "code"),
    ("COMMIT_EDITMSG", "commit"),
    ("letter.txt", "prose"),
    ("-", "prose"),
])
def test_infer_kind(path, kind):
    assert slop_scan.infer_kind(path) == kind


# --- prose ------------------------------------------------------------------

@pytest.mark.parametrize("text,category", [
    ("Certainly! Here is the summary.", "chat-leftover"),
    ("I hope this helps with your project.", "chat-leftover"),
    ("As of my last knowledge update, it was open.", "chat-leftover"),
    ("See the source citeturn0search0 for more.", "tool-artifact"),
    ("Link: https://a.org/x?utm_source=chatgpt.com", "tool-artifact"),
    ("Contact [Your Name] for details.", "placeholder"),
    ("Released on 2025-XX-XX.", "placeholder"),
    ("The speed is [needs: benchmark numbers].", "open-marker"),
    ("The bridge is a testament to local engineering.", "inflated-significance"),
    ("It plays a pivotal role in the region.", "inflated-significance"),
    ("It is not only fast but also cheap.", "negative-parallelism"),
    ("It's important to note that the API is beta.", "disclaimer"),
    ("In conclusion, the tool works.", "summary"),
    ("Some experts argue that it is slow.", "vague-attribution"),
])
def test_prose_tells(text, category):
    assert category in categories(text)


def test_clean_prose_has_no_findings():
    text = (
        "The parser reads a 1 GB log in 3 seconds on a 2022 laptop.\n"
        "It needs Python 3.10 or newer and has no other dependencies.\n"
    )
    assert findings(text) == []


def test_phrase_and_word_are_not_double_counted():
    # "a testament to" is a phrase entry and "testament" a word entry;
    # one occurrence must count once.
    text = "This is a testament to the team. " + "word " * 20
    vocab = [f for f in findings(text) if f.category.startswith("ai-vocabulary")]
    assert len(vocab) == 1
    assert vocab[0].match.count("testament") == 1


def test_vocab_density_counts_distinct_occurrences():
    text = "We delve into the intricate tapestry of seamless synergy."
    vocab = [f for f in findings(text) if f.category == "ai-vocabulary-density"]
    assert vocab and vocab[0].match.startswith("5 hits")


def test_markdown_emoji_heading_and_bold_labels():
    text = "\n".join([
        "# 🚀 Features",
        "- **Fast:** it is fast",
        "- **Small:** it is small",
        "- **Easy:** it is easy",
    ])
    cats = categories(text, kind="markdown", fname="README.md")
    assert {"emoji-heading", "inline-header-list"} <= cats


def test_curly_quotes_inside_code_fence():
    text = "Run this:\n\n```bash\necho “hello”\n```\n"
    assert "curly-quotes-in-code" in categories(text, kind="markdown", fname="a.md")


def test_text_inside_code_fence_is_not_prose_scanned():
    text = "```\nCertainly! I hope this helps\n```\n"
    assert "chat-leftover" not in categories(text, kind="markdown", fname="a.md")


# --- code -------------------------------------------------------------------

def test_code_comment_tells():
    src = "\n".join([
        "def f(x):",
        "    # Replace this with your actual logic",
        "    api_key = 'YOUR_API_KEY_HERE'",
        "    try:",
        "        return x",
        "    except Exception:",
        "        pass",
    ])
    cats = categories(src, kind="code", fname="a.py")
    assert {"comment-to-user", "placeholder-value", "swallowed-exception"} <= cats


def test_hash_inside_string_is_not_a_comment():
    src = 'color = "#ff0000"  # brand red, matches the logo\n'
    assert findings(src, kind="code", fname="a.py") == []


def test_url_is_not_a_js_comment():
    src = 'const u = "https://example.org/a";\n'
    comments = slop_scan.extract_comments(src.splitlines(), ".js")
    assert comments == []


# --- commit messages ----------------------------------------------------------

def test_commit_tells():
    msg = "Enhanced overall robustness and maintainability.\nbody right after\n"
    cats = categories(msg, kind="commit")
    assert {"commit-vague-subject", "commit-subject-period", "commit-mood",
            "commit-no-blank-line"} <= cats


def test_good_commit_is_clean():
    msg = (
        "Retry uploads after a 503 from the CDN\n"
        "\n"
        "The CDN returns 503 during deploys, which failed the whole batch.\n"
        "Retry up to three times with backoff before giving up.\n"
    )
    assert findings(msg, kind="commit") == []


def test_git_template_comments_are_ignored():
    msg = (
        "Fix crash on empty input\n"
        "\n"
        "# Please enter the commit message for your changes. Lines starting\n"
        "# with '#' will be ignored, and an empty message aborts the commit.\n"
        "# On branch main\n"
        "# ------------------------ >8 ------------------------\n"
        "# Do not modify or remove the line above.\n"
        "diff --git a/x b/x\n"
        "+Certainly! I hope this helps\n"
    )
    assert findings(msg, kind="commit") == []


def test_markdown_heading_in_hand_written_commit_is_flagged():
    msg = "Add retry\n\n## Summary\nRetries 503s because deploys fail batches.\n"
    assert "commit-markdown" in categories(msg, kind="commit")


# --- CLI ----------------------------------------------------------------------

def test_cli_unreadable_file_exits_2(tmp_path, capsys):
    missing = tmp_path / "nope.md"
    assert slop_scan.main([str(missing)]) == 2
    out = capsys.readouterr()
    assert "cannot read" in out.err
    assert "No findings" not in out.out


def test_cli_partial_unreadable_still_scans_and_exits_2(tmp_path, capsys):
    good = tmp_path / "a.txt"
    good.write_text("Certainly! Done.\n", encoding="utf-8")
    assert slop_scan.main([str(good), str(tmp_path / "missing.txt")]) == 2
    out = capsys.readouterr().out
    assert "chat-leftover" in out
    assert "Not scanned (1 unreadable)" in out


def test_cli_fail_on(tmp_path):
    f = tmp_path / "a.txt"
    f.write_text("I hope this helps.\n", encoding="utf-8")
    assert slop_scan.main([str(f)]) == 0
    assert slop_scan.main(["--fail-on", "high", str(f)]) == 1


def test_cli_json_output(tmp_path, capsys):
    f = tmp_path / "a.txt"
    f.write_text("Great question! It works.\n", encoding="utf-8")
    slop_scan.main(["--json", str(f)])
    data = json.loads(capsys.readouterr().out)
    assert data["counts"]["high"] >= 1
    assert data["findings"][0]["category"] == "chat-leftover"
