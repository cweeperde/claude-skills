"""Tests for plugins/release/skills/release/scripts/release_memory.py."""
import datetime as dt
import importlib.util
import pathlib
import subprocess
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "plugins/release/skills/release/scripts/release_memory.py"

spec = importlib.util.spec_from_file_location("release_memory", SCRIPT)
rm = importlib.util.module_from_spec(spec)
sys.modules["release_memory"] = rm  # dataclasses look the module up here
spec.loader.exec_module(rm)

TODAY = dt.date(2026, 11, 23)


def run(repo, *args):
    subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True)


@pytest.fixture
def repo(tmp_path):
    r = tmp_path / "proj"
    r.mkdir()
    run(r, "init", "-q")
    run(r, "config", "user.email", "t@example.org")
    run(r, "config", "user.name", "t")
    (r / "CHANGELOG.md").write_text("# Changelog\n\n## 1.0.0 - 2026-11-01\n", encoding="utf-8")
    run(r, "add", ".")
    run(r, "commit", "-qm", "init")
    run(r, "tag", "v1.0.0")
    return r


@pytest.fixture
def memdir(tmp_path, monkeypatch):
    d = tmp_path / "mem"
    monkeypatch.setenv("RELEASE_MEMORY_DIR", str(d))
    return d


# --- project identity -----------------------------------------------------------

@pytest.mark.parametrize("url", [
    "git@github.com:Me/Repo.git",
    "https://github.com/me/repo",
    "https://user:ghp_secret@github.com/me/repo.git",
    "ssh://git@github.com:22/me/repo",
    "git+https://github.com/me/repo.git/",
])
def test_normalize_remote(url):
    assert rm.normalize_remote(url) == "github.com/me/repo"


@pytest.mark.parametrize("url", ["/srv/git/repo.git", "C:/repos/x.git", "C:\\repos\\x.git", "file:///srv/x", "../x.git"])
def test_local_path_remotes_are_not_project_names(url):
    assert rm.normalize_remote(url) is None


def test_tags_in_the_same_second_sort_by_version(repo):
    run(repo, "tag", "v1.10.0")
    run(repo, "tag", "v1.2.0")
    assert rm.tags_newest_first(repo)[0] == "v1.10.0"


def test_normalize_nested_groups():
    assert rm.normalize_remote("git@gitlab.example.com:group/sub/proj.git") == "gitlab.example.com/group/sub/proj"


def test_identify_with_and_without_remote(repo):
    sub = repo / "deep" / "er"
    sub.mkdir(parents=True)
    local = rm.identify(sub)
    assert local.id.startswith("local_proj_")
    assert rm.identify(repo).id == local.id
    run(repo, "remote", "add", "origin", "git@github.com:Me/Thing.git")
    remote = rm.identify(sub)
    assert (remote.id, remote.label) == ("github.com_me_thing", "github.com/me/thing")


# --- parsing --------------------------------------------------------------------

MEMORY = """---
project: x
updated: 2026-11-01
---

## Rules
- Tags look like `v<x.y.z>`. {source: git-tags v*.*.*}
- Changelog entries are dated. {source: file CHANGELOG.md sha256:HASH}
- Wait for CI before tagging. {source: user 2026-11-20}
- A rule with no source.

## Steps
1. Run the tests. {source: file CHANGELOG.md sha256:HASH} {source: user 2026-01-01}

## History
- 2026-11-01 v1.0.0: ok (no source needed here)
"""


def memory_for(repo):
    return MEMORY.replace("HASH", rm.sha256(repo / "CHANGELOG.md"))


def test_parse_rules_reads_rules_and_steps_only(repo):
    rules = rm.parse_rules(memory_for(repo))
    assert [r.section for r in rules] == ["rules", "rules", "rules", "rules", "steps"]
    assert rules[0].text == "Tags look like `v<x.y.z>`."
    assert [s.kind for s in rules[4].sources] == ["file", "user"]


def test_check_ok_stale_ask_invalid(repo):
    verdicts = rm.check_rules(rm.parse_rules(memory_for(repo)), repo, TODAY)
    assert [v.status for v in verdicts] == ["OK", "OK", "OK", "INVALID", "ASK"]


def test_changed_file_makes_rule_stale(repo):
    text = memory_for(repo)
    (repo / "CHANGELOG.md").write_text("# Changelog\n\n## 1.1.0 - unreleased\n", encoding="utf-8")
    statuses = [v.status for v in rm.check_rules(rm.parse_rules(text), repo, TODAY)]
    assert statuses[1] == "STALE"
    assert statuses[4] == "STALE", "STALE wins over ASK"


def test_crlf_checkout_hashes_like_lf(repo):
    f = repo / "CHANGELOG.md"
    f.write_bytes(b"# Changelog\n\n## 1.0.0\n")
    text = memory_for(repo)
    f.write_bytes(b"# Changelog\r\n\r\n## 1.0.0\r\n")
    assert rm.check_rules(rm.parse_rules(text), repo, TODAY)[1].status == "OK"


def test_deleted_file_makes_rule_stale(repo):
    text = memory_for(repo)
    (repo / "CHANGELOG.md").unlink()
    v = rm.check_rules(rm.parse_rules(text), repo, TODAY)[1]
    assert v.status == "STALE" and "no longer exists" in v.reasons[0]


def test_tag_pattern_must_match_newest_tags(repo):
    rules = rm.parse_rules("## Rules\n- x {source: git-tags release-*}\n")
    assert rm.check_rules(rules, repo, TODAY)[0].status == "STALE"
    run(repo, "tag", "release-2")
    assert rm.check_rules(rules, repo, TODAY)[0].status == "OK"


def test_paths_outside_the_repo_are_invalid(repo):
    rules = rm.parse_rules(f"## Rules\n- x {{source: file ../../etc/passwd sha256:{'0' * 64}}}\n")
    assert rm.check_rules(rules, repo, TODAY)[0].status == "INVALID"


def test_placeholder_hash_is_stale_until_stamped(repo):
    text = "---\nupdated: 2026-01-01\n---\n## Rules\n- x {source: file CHANGELOG.md sha256:?, verified 2026-11-23}\n"
    assert rm.check_rules(rm.parse_rules(text), repo, TODAY)[0].status == "STALE"
    stamped, changed = rm.stamp_text(text, repo, TODAY)
    assert changed == 1
    assert "updated: 2026-11-23" in stamped
    assert rm.check_rules(rm.parse_rules(stamped), repo, TODAY)[0].status == "OK"


def test_stamp_only_touches_rules_verified_today(repo):
    old = "a" * 64
    text = (
        "## Rules\n"
        f"- not verified {{source: file CHANGELOG.md sha256:{old}}}\n"
        f"- verified earlier {{source: file CHANGELOG.md sha256:{old}, verified 2026-11-01}}\n"
        f"- verified today {{source: file CHANGELOG.md sha256:{old}, verified 2026-11-23}}\n"
        "## History\n"
        f"- {{source: file CHANGELOG.md sha256:{old}, verified 2026-11-23}} untouched outside Rules/Steps\n"
    )
    stamped, changed = rm.stamp_text(text, repo, TODAY)
    assert changed == 1
    statuses = [v.status for v in rm.check_rules(rm.parse_rules(stamped), repo, TODAY)]
    assert statuses == ["STALE", "STALE", "OK"]
    assert stamped.splitlines()[-1].count(old) == 1


# --- CLI ------------------------------------------------------------------------

def test_cli_exit_codes(repo, memdir, capsys):
    assert rm.main(["check", str(repo)]) == 4
    assert rm.main(["init", str(repo)]) == 0
    path = pathlib.Path(capsys.readouterr().out.split("created: ")[1].strip())
    assert path.parent == memdir
    assert rm.main(["check", str(repo)]) == 0, "an empty memory is fine"
    path.write_text(memory_for(repo), encoding="utf-8")
    assert rm.main(["check", str(repo)]) == 3
    out = capsys.readouterr().out
    assert "INVALID L" in out and "1 INVALID" in out
    assert rm.main(["init", str(repo)]) == 0
    assert "exists:" in capsys.readouterr().out


def test_cli_hash_and_errors(repo, capsys):
    assert rm.main(["hash", str(repo / "CHANGELOG.md")]) == 0
    assert capsys.readouterr().out.startswith(rm.sha256(repo / "CHANGELOG.md"))
    assert rm.main(["hash", str(repo / "missing")]) == 2
    assert rm.main(["check", str(repo / "missing-dir")]) == 2
