# Changelog

## 1.0.0 - unreleased

- First release: discovers how a project releases, proposes the version and changelog, prepares locally and pushes, tags and publishes after one approval.
- Keeps per-project release rules in `~/.release-memory/`; `release_memory.py check` marks a rule stale when the file it came from changed, its tag pattern no longer matches, or a user answer is older than 180 days.
