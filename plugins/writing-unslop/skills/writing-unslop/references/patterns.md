# Catalogue of slop patterns

Every pattern below lists what it looks like, why models produce it, how to fix it, and how much weight it deserves alone. Strength: **Strong** = rarely human in that context; **Moderate** = meaningful when several co-occur; **Weak** = common in human writing, only useful in clusters.

Sources are summarised in `evidence.md`. Most prose patterns come from Wikipedia's *Signs of AI writing* field guide (WikiProject AI Cleanup), which is descriptive and Wikipedia-centred; vocabulary findings come from corpus studies.

## Contents
1. Content and meaning
2. Vocabulary
3. Sentence-level rhetoric
4. Document structure
5. Formatting and punctuation
6. Chatbot leftovers
7. Citations and sourcing
8. Tool artifacts
9. Context and behaviour
10. Ineffective indicators
11. Search strings

---

## 1. Content and meaning

These matter most because they are about what the text says.

### 1.1 Inflated significance, symbolism, legacy
- **Looks like:** *stands/serves as*, *is a testament/reminder to*, *plays a vital/significant/crucial/pivotal role*, *underscores/highlights its importance*, *reflects broader trends*, *enduring/lasting impact*, *key turning point*, *indelible mark*, *deeply rooted*, *rich heritage*. A mundane fact (founding date, a renaming, a population figure) followed by what it "represents". Sometimes a concession that the subject is minor, then praise anyway. In biology: tenuous ecosystem links and long notes on conservation status.
- **Why:** models regress to the most statistically likely description, and notable subjects in training data are described in grand terms. Specific facts get smoothed into generic praise: the subject becomes less specific and more exaggerated at once.
- **Fix:** state the fact and stop. If it really mattered, show the consequence: "After the 1989 law, the region ran its own census" instead of "marking a pivotal moment in regional statistics".
- **Strength:** Moderate; strong when repeated.

### 1.2 Superficial analysis in trailing "-ing" clauses
- **Looks like:** *..., highlighting / underscoring / emphasizing / reflecting / showcasing / ensuring / fostering / contributing to / aligning with ...* at the end of a sentence. Stronger when the subject is inanimate: "the monument underscores its role", "the data highlights the need".
- **Why:** a fact cannot highlight anything; this is an unattributed opinion from a disembodied narrator. Search-enabled models attach such claims to real sources that may not say anything like it.
- **Fix:** delete the clause and check whether anything was lost. If the interpretation matters, name who makes it and confirm they do, or state it as the author's view.
- **Strength:** Strong with inanimate subjects.

### 1.3 Promotional, advertising tone
- **Looks like:** *nestled*, *in the heart of*, *boasts*, *vibrant*, *stunning*, *breathtaking*, *continues to captivate*, *groundbreaking*, *seamless*, *must-visit*, *world-class*, *cutting-edge*. Product text that reads like a TV commercial.
- **Fix:** replace each adjective with a checkable fact, or drop it.
- **Strength:** Moderate (humans write marketing too).

### 1.4 Undue emphasis on notability and coverage
- **Looks like:** "has been featured in *Wired*, *Forbes* and other outlets" with nothing about what they said; *independent coverage*; *maintains an active social media presence*; sources named in the sentence for trivial facts.
- **Fix:** report what the source said; put the citation in a link or footnote.
- **Strength:** Moderate; strong in encyclopedic text.

### 1.5 Vague attribution (weasel words)
- **Looks like:** *Some critics argue*, *Experts note*, *Industry reports suggest*, *has been described as*, *is widely regarded as*, *is of interest to researchers*. One source generalised into "experts".
- **Fix:** name and link the source, or own the claim, or cut it.
- **Strength:** Moderate.

### 1.6 Didactic disclaimers
- **Looks like:** *It's important to note/remember/consider*, *It is crucial to differentiate*, *may vary*, unrequested safety caveats.
- **Fix:** state a real caveat as a fact where it applies ("Requires root on Linux"). Delete reminders to an imagined reader.
- **Strength:** Moderate.

### 1.7 The "challenges and future prospects" formula
- **Looks like:** "Despite its [praise], X faces several challenges, including... Despite these challenges, X continues to thrive / is well positioned..." often followed by a "Future Outlook" section.
- **Fix:** name specific, sourced problems where they belong; drop speculative optimism. (Mentioning difficulties is fine; the rigid formula is the tell.)
- **Strength:** Strong when the formula is intact.

### 1.8 Gap-hedging followed by speculation
- **Looks like:** *While specific details are limited*, *not widely documented*, *based on available information*, *in the provided sources*, then what something "likely" is. Among the most common current signs on Wikipedia (2026).
- **Fix:** find the fact or say nothing about it.
- **Strength:** Strong.

### 1.9 Interchangeable sentences
- **Test:** would the sentence be equally true of a different subject? "The festival brings the community together and celebrates local culture" fits ten thousand festivals. Regression to the mean produces exactly these.
- **Fix:** replace with something only true of this subject, or cut.

---

## 2. Vocabulary

### 2.1 "AI vocabulary" density
- **Words to watch:** *delve* (mostly pre-2025), *intricate/intricacies*, *tapestry*, *testament*, *underscore*, *pivotal*, *realm*, *showcase/showcasing*, *multifaceted*, *nuanced*, *meticulous(ly)*, *seamless(ly)*, *leverage*, *robust*, *streamline*, *foster*, *garner*, *vibrant*, *crucial*, *vital*, *enduring*, *interplay*, *landscape* (figurative), *underpin*, *notably*, *comprehensive*, *align with*, *enhance*, *highlight* (verb), *key* (adjective), *shed light on*, *potential*, *findings*. Newer chat output adds *holistic*, *paramount*, *embark*, *elevate*, *empower*, *unlock*, *harness*, *navigate (the complexities of)*, *ever-evolving*, *transformative*.
- **How to read it:** one or two mean nothing. Many, repeatedly, in post-2022 text is one of the strongest tells, and they cluster. Lists drift by model and year (*delve* dropped sharply in 2025), so treat any list as a snapshot. Context matters: *robust* in statistics, *leverage* in finance, *landscape* as orientation.
- **Why:** corpus studies show abrupt post-2022 jumps in exactly these style words (verbs and adjectives, not content nouns). Experiments suggest human raters during feedback training preferred text containing some of them.
- **Fix:** ask what the word is doing. Usually it is an intensifier or an interpretive verb. Replace with the concrete claim or delete. "Robust error handling" -> "retries three times with backoff, then raises `TimeoutError`". Do **not** just swap synonyms.
- **Strength:** Strong in density; weak per word.

### 2.2 Copula avoidance
- **Looks like:** *serves as*, *stands as*, *functions as*, *represents*, *boasts*, *features*, where "is" or "has" would do. In a first sentence, *refers to*, as if the topic were the word.
- **Fix:** use "is", "are", "has".
- **Strength:** Moderate.

### 2.3 Stock metaphors and idioms
- **Looks like:** *landscape*, *tapestry*, *journey*, *beacon*, *symphony of*, *navigating the complexities*, *at the intersection of*, *a deep dive*.
- **Fix:** say it literally, or use a figure specific to the subject.
- **Strength:** Moderate.

---

## 3. Sentence-level rhetoric

### 3.1 Negative parallelism
- **Looks like:** "Not only X, but Y"; "It's not just about X, it's Y"; "It's not X. It's Y."; "X, however, ..." as a dramatic pivot.
- **Fix:** say Y. Contrast with an X nobody claimed is filler.
- **Strength:** Moderate; strong when frequent.

### 3.2 Outlines of negatives
- **Looks like:** "No X. No Y. Just Z." / "Not A, not B, and certainly not C."
- **Fix:** make the positive claim once, with evidence.
- **Strength:** Strong in arguments and comments.

### 3.3 Rule of three
- **Looks like:** triplets everywhere ("fast, reliable, and secure"; "keynotes, panels, and networking"). Used to make thin analysis look complete.
- **Fix:** list as many items as exist. Two is fine; four is fine.
- **Strength:** Weak alone; moderate in density.

### 3.4 Elegant variation (synonym cycling)
- **Looks like:** the same entity renamed each mention: "Yankilevsky... the artist... the visionary... the non-conformist". Caused by repetition penalties.
- **Fix:** repeat the name or use a pronoun. In technical text, one term per concept.
- **Strength:** Moderate.

### 3.5 False ranges
- **Looks like:** "from the Big Bang to the cosmic web, from the birth of stars to the dance of dark matter". "From X to Y" with no scale between the endpoints.
- **Fix:** list the examples plainly, or name the real range.
- **Strength:** Moderate.

### 3.6 Dense, nominalised style
- **Looks like:** "the implementation of improvements to the optimisation of processing". Chat-tuned models use nominalisations at 1.5 to 2 times the human rate, overuse that-clauses as subjects, and underuse concessive subordinators (*though*, *although*), downtoners (*somewhat*, *slightly*) and sentence-initial discourse particles (*well*, *anyway*).
- **Fix:** turn nouns back into verbs, give sentences actors, allow ordinary concessions and qualifiers.
- **Strength:** Weak alone (academic humans write this way too).

### 3.7 Formulaic connectives
- **Looks like:** *Additionally*, *Furthermore*, *Moreover*, *In addition*, *Notably*, *Ultimately* opening many sentences, implying links that are not there.
- **Fix:** use connectives only where the logical relation is real.
- **Strength:** Weak.

---

## 4. Document structure

- **Restating summaries:** "In summary", "In conclusion", "Overall", a "Conclusion" section on a short piece, paragraphs that end by restating themselves. Fix: end when done. Research on model output finds "In conclusion" massively overproduced relative to human text.
- **Rigid templates:** Overview / Background / Key Features / Benefits / Challenges / Future Outlook / Conclusion regardless of topic. Fix: structure around this reader's questions.
- **Title treated as a thing:** "'List of songs about Mexico' is a curated compilation of..." Fix: start with the subject.
- **Uniform rhythm:** every paragraph three to five sentences of similar length. Fix: let content set length; a one-line paragraph is allowed.
- **Over-structuring:** headings and bullets for content that is a few paragraphs of reasoning. Model output overproduces Markdown headers and bullet lists by large factors compared with human text in the same genre. Fix: prose for argument; lists for parallel, scannable items.

---

## 5. Formatting and punctuation

| Pattern | Looks like | Fix | Strength |
|---|---|---|---|
| Excessive bold | Every key term bolded, "key takeaways" style | Bold only what must not be missed, or nothing | Moderate |
| Bold-label bullets | `- **Feature:** description` for every point | Prose, or plain parallel bullets | Moderate |
| Title Case Headings | "Strategic Negotiations and Global Partnerships" | Sentence case unless house style differs | Weak-moderate |
| Decorative emoji | 🚀 ✨ 📦 🧠 before headings and bullets | Remove unless it is the established voice | Moderate |
| Em dashes everywhere | — doing the work of commas, colons, parentheses | Vary punctuation | Weak; evidence conflicts (see `evidence.md`) |
| Curly quotes | “ ” ’ | Ignore in prose; **fix in code, shell and config** | Weak in prose |
| Markdown in the wrong place | `**bold**`, `##` in email, commit, wiki, form | Write in the destination's format | Moderate-strong |
| Email framing in a form | "Subject: Request for review..." | Delete | Moderate |

---

## 6. Chatbot leftovers

Text meant for the prompter, not the reader. The most objective signs; Wikipedia's speedy-deletion criterion for unreviewed LLM pages rests on this category and fabricated citations.

| Sign | Typical wording | Strength |
|---|---|---|
| Collaborative phrases | *Certainly!*, *Of course!*, *Great question*, *You're absolutely right*, *I hope this helps*, *Let me know if...*, *Would you like me to...*, *Here is a revised...* | Strong |
| Knowledge cutoff | *As of my last knowledge update* | Strong |
| Refusal | *As an AI language model*, *I'm sorry, but I can't* | Strong |
| Unfilled placeholders | `[Your Name]`, `[Describe the issue]`, `2025-XX-XX`, `URL`, `<!-- Add if available -->` | Strong |
| Meta-statements | *In this section, we will discuss*, *This article explores* | Moderate |
| Notes to the reviewer | Self-assessment of why the text meets guidelines | Strong |
| Abrupt cut-off | Stops mid-thought (output limit) | Moderate |

Fix: delete; fill placeholders with real values only.

---

## 7. Citations and sourcing

- **Fabricated references:** plausible authors, titles, journals, DOIs that do not exist, or DOIs pointing at unrelated papers. Strong.
- **Invalid ISBN checksums and unresolvable DOIs.** Strong.
- **Several dead links never captured by any archive.** Strong when multiple.
- **Real but irrelevant sources; book citations without pages.** Moderate.
- **Fix:** open every source and find the supporting passage. Never paste model-supplied references unchecked.

---

## 8. Tool artifacts

Copy-paste residue from chat interfaces. All strong.

- `citeturn0search0`, `iturn0image0`, `citeturn0news0` (ChatGPT)
- `:contentReference[oaicite:0]{index=0}`, `oai_citation` (ChatGPT)
- `({"attribution":{"attributableIndex":"X-Y"}})` (ChatGPT)
- `utm_source=chatgpt.com` / `utm_source=openai` on URLs (shows ChatGPT found the link, not that it wrote the text)
- `[attached_file:1]`, `[web:1]` (reported, likely Perplexity)
- `grok_card` (Grok)
- `↩` footnote arrows, ` ```wikitext ` fences, `<|endoftext|>`

Fix: strip, and cite properly.

---

## 9. Context and behaviour

- **Sudden style shift:** a writer's text becomes suddenly flawless or changes register.
- **Sudden switch to American English:** models default to it. Non-native writers mix varieties, so only a sudden, complete switch counts.
- **Verbose first-person change summaries:** "Refined the language for a neutral tone, ensured factual accuracy, improved clarity..." This is the ancestor of the vague AI commit message and PR description.
- **Signs of a human author:** they can explain their choices and their mistakes, and supply the right link when a wrong one is pointed out.

---

## 10. Ineffective indicators

Do not treat these as evidence on their own (Wikipedia lists them as unreliable):
- Perfect grammar.
- "Bland" or "robotic" prose (modern models are effusive, not robotic).
- Fancy or academic words in general; the overuse is specific to certain words, and rare words are actually less likely in model output.
- Formal letter style; transition words; odd markup errors (usually editor bugs).
- Any AI-detector score.

---

## 11. Search strings

When the scanner is unavailable, search for:

```
Certainly  Of course  Great question  I hope this helps  Let me know  Would you like
As an AI  As of my last  knowledge update  based on available information  not widely documented
In this section  This article explores  It's important to note  In conclusion  In summary
testament  pivotal  tapestry  delve  underscore  showcasing  seamless  vibrant  nestled  boasts
Not only  It's not just  Despite these challenges  continues to thrive  Some critics argue
[  ]  XX  TODO  your-  yourusername  your_api_key  example.com  lorem
turn0  oaicite  contentReference  oai_citation  attributableIndex  utm_source=  grok_card  ↩
“  ”  ’   (inside code blocks, shell commands, config)
```
