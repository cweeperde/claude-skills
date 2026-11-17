# Changelog

## 1.1.0 - 2026-11-17

- Loads automatically for longer text the user will publish or send; for commit messages and code comments only when asked to review or rewrite them.
- `slop_scan.py`: a word inside a matched phrase ("testament" in "a testament to") no longer counts twice.
- `slop_scan.py`: an unreadable file exits 2 and is listed as not scanned, instead of reporting "No findings".
- `slop_scan.py`: in a raw `COMMIT_EDITMSG`, git's template comments are no longer flagged as Markdown headings, and the diff below the `commit -v` scissors line is ignored.

## 1.0.0 - 2026-11-08

- First release.
