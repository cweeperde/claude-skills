# Before / after examples

These show the passes applied to realistic slop. Note what the rewrites do **not** do: they never invent facts that the original lacked. Where a fact is missing, the claim is cut or marked `[needs: ...]`. In real use, fill those markers from the user's material or ask.

## Contents
1. Encyclopedic paragraph
2. Work email
3. Social post
4. Code comments
5. Docstring
6. README
7. Commit message
8. Pull request description
9. Bug report
10. Over-correction: what not to do

---

## 1. Encyclopedic paragraph

**Before**
> Nestled in the heart of the Ruhr valley, the Altena Library stands as a testament to the town's enduring commitment to education. Founded in 1962, it has played a pivotal role in fostering community engagement, lifelong learning, and cultural enrichment. Not only does it lend books, but it also serves as a vibrant hub for local residents. Despite facing budget challenges, the library continues to thrive, underscoring its importance to the community.

**After**
> The Altena Library, founded in 1962, is the public library of Altena in the Ruhr valley. [needs: what it offers beyond lending, e.g. programmes, collection size] [needs: the budget problem, specifically, with a source]

**What changed:** kept the only facts (name, place, 1962, lends books, has had budget trouble). Cut significance claims, promotional tone, the "not only" construction, the triplet, and the trailing "-ing" interpretation. Flagged the two places where real information is needed.

---

## 2. Work email

**Before**
> Subject: Follow-Up Regarding Q3 Report
>
> Hi Sarah,
>
> I hope this email finds you well! I wanted to reach out to follow up on the Q3 report. It's important to note that the deadline is approaching, and your insights would be invaluable in ensuring a comprehensive and robust analysis. Please don't hesitate to let me know if you have any questions or need any additional information. I truly appreciate your time and dedication!
>
> Best regards,

**After**
> Subject: Q3 report: your section by Thursday?
>
> Hi Sarah,
>
> Could you send me the regional sales section of the Q3 report by Thursday? I need it to finish the draft before Friday's review.
>
> Thanks,

**What changed:** one clear ask with a deadline and the reason for it, taken from context. Removed the greeting formula, disclaimer, flattery and sign-off filler. (If "regional sales section", "Thursday" and "Friday's review" were not in the user's context, the right move is to ask for them, not to make them up.)

---

## 3. Social post

**Before**
> 🚀 Excited to announce that I've joined Acme as a Senior Engineer! 🎉
>
> This isn't just a new job. It's a new chapter. A chance to grow, to learn, and to make an impact.
>
> Grateful for the journey that brought me here. Here's to the next adventure! 💪 #NewBeginnings #Growth

**After**
> I've joined Acme as a senior engineer on the payments team. I'll be working on [needs: what you'll work on]. Thanks to [needs: people you want to thank] at my previous job for four good years.

**What changed:** replaced the "not just X, it's Y" frame, the triplet and the emoji with what the reader actually wants: where, what on, and who to thank.

---

## 4. Code comments

**Before**
```python
# Step 1: Initialize an empty dictionary to store the user data
users = {}
# Loop through each row in the data and add it to the dictionary
for row in rows:
    users[row.id] = row  # Store the row using its ID as the key

# Updated: now handles duplicates robustly
```

**After** (the author confirmed that later rows are newer)
```python
# Later rows win: the export repeats a user after an email change,
# and the last row has the current address.
users = {row.id: row for row in rows}
```

**What changed:** removed narration and the change-log comment; kept the one non-obvious fact (why duplicates are overwritten), which had to come from the author.

---

## 5. Docstring

**Before**
```python
def parse_duration(s: str) -> int:
    """
    A robust and flexible utility function that seamlessly parses duration strings.

    Args:
        s (str): The input string.

    Returns:
        int: The result.
    """
```

**After** (written from reading the function body)
```python
def parse_duration(s: str) -> int:
    """Return the number of seconds in a duration such as "1h30m" or "45s".

    Accepts h, m and s units in that order. Raises ValueError on an empty
    string or an unknown unit. Days are not supported.
    """
```

**What changed:** the summary says what it returns; the body documents what the signature does not show. Every claim was checked against the implementation.

---

## 6. README

**Before**
```markdown
# 🚀 FitConvert ✨

FitConvert is a powerful, lightweight, and blazing-fast tool that seamlessly transforms your fitness data, empowering athletes to unlock the full potential of their workouts!

## ✨ Key Features
- **Lightning Fast:** Optimized for performance
- **Easy to Use:** Intuitive interface
- **Cross-Platform:** Works everywhere

## 📦 Installation
git clone https://github.com/yourusername/fitconvert.git

## 🤝 Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

Made with ❤️ by [Your Name]
```

**After** (facts from the repository: a Python CLI, `pyproject.toml` entry point `fitconvert`, CI runs on Linux and macOS)
```markdown
# fitconvert

Converts Garmin `.fit` activity files to GPX for import into Strava, Komoot
or map editors.

## Install

    pipx install fitconvert

## Usage

    fitconvert run.fit -o run.gpx

Heart rate and cadence are written as GPX extensions. [needs: what happens to power data]

## Status

Tested in CI on Linux and macOS. Windows is untested.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). [needs: does this file exist?]
```

**What changed:** one-sentence opener; tested install and usage instead of generic feature claims; honest status; removed emoji, placeholders, boilerplate and the flourish. Speed claims were dropped because there is no benchmark.

---

## 7. Commit message

**Before**
```
Refactored code to enhance error handling and improve overall robustness.

## Changes
- Updated upload.py
- Updated retry.py
- Added tests
```

**After** (from the diff and the linked issue)
```
Retry S3 uploads on 503 SlowDown

Nightly backups failed intermittently with 503 SlowDown when the
bucket was under load (#318). Retry up to 5 times with exponential
backoff starting at 200 ms. Other 5xx errors still fail immediately
so real outages surface.

Fixes #318
```

---

## 8. Pull request description

**Before**
> ## Summary
> This PR significantly improves the codebase by enhancing error handling, improving performance, and adding comprehensive tests.
> ## Changes
> - Updated `upload.py`
> - Updated `tests/test_upload.py`
> ## Testing
> All tests pass ✅

**After**
> Fixes #318: nightly backups fail on S3 503 SlowDown.
>
> Adds retry with exponential backoff for 503 SlowDown only; other errors are unchanged. I considered retrying all 5xx but that would hide real outages for up to a minute.
>
> **Testing:** new unit test simulates three 503s then success. Ran the uploader against a local MinIO behind a proxy returning 503 for the first three requests; the upload succeeded on attempt four.
>
> **Unsure:** whether 5 retries is too many for the interactive CLI path.

(If the repo's PR template requires Summary/Changes/Testing headings, keep them and put this content under them.)

---

## 9. Bug report

**Before**
> ## Description
> I have identified a critical vulnerability in the URL parsing functionality that could potentially lead to memory corruption and arbitrary code execution. This represents a significant security risk.
> ## Impact
> Attackers could leverage this vulnerability to compromise systems.
> ## Recommendation
> Implement robust input validation.

**After**
> `parse_url("http://[::1")` (missing closing bracket) reads one byte past the end of the input buffer in `url.c:412` on version 8.10.1, Linux x86_64. Reproduce with the attached `poc.c`; ASan reports a heap-buffer-overflow READ of size 1. I have not found a way to turn this into a write.

**What changed:** a specific input, location, version, reproduction and an honest severity statement. If the reporter cannot produce these, there is no report to send yet.

---

## 10. Over-correction: what not to do

**Slop**
> The new caching layer plays a pivotal role in enhancing performance, seamlessly reducing latency and fostering a more responsive user experience.

**Over-corrected ("anti-slop slop")**
> Caching. It's fast now. Really fast. No more waiting. Just speed.

This swaps one set of tells for another: punchy fragments, an outline of negatives, and still no facts.

**Good**
> The cache cuts median page load from 820 ms to 140 ms on the product listing page. Cached entries expire after 5 minutes, so stock levels can lag by up to that long.

(Numbers from the author's measurements. Without them: "Adding a cache for product listings. [needs: before/after load times]".)
