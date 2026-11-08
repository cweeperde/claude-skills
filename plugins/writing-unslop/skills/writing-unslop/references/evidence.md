# Evidence base

What the research supports, where it is thin, and how to talk about detection honestly. Read this when the user asks "how do you know", wants to judge someone else's text, or asks about AI detectors.

## Why models write this way

- **Regression to the mean.** A model predicts the most likely continuation, so rare specifics get replaced by common, positive generalities. Result: less specific and more exaggerated at the same time. (Wikipedia, *Signs of AI writing*.)
- **Instruction tuning sets a house style.** Reinhart et al. (PNAS 2025) found instruction-tuned GPT-4o and Llama 3 write in a noun-heavy, informationally dense style even when asked to imitate informal speech, using nominalisations at 1.5 to 2 times the human rate; base models were much closer to humans. Rallapalli et al. (2026 preprint, RAID dataset, 11 models, 8 genres) found the same dense profile, overuse of that-clauses as subjects and nominalisations, and underuse of concessives (*though*, *although*), downtoners and sentence-initial discourse particles. They also found genre shapes style more than human-vs-machine origin, which is why matching the genre is so effective.
- **Feedback training rewards certain words.** Juzek & Ward (COLING 2025) identified 21 "focal words" (e.g. *delve*, *intricate*, *underscore*) overused by ChatGPT; architecture and training data did not explain it, and a follow-up experiment found human raters preferred text containing some of these words.
- **Repetition penalties** cause synonym cycling (elegant variation).
- **Markdown defaults.** Chat products instruct models to format in Markdown. A 2026 preprint (Mahapatra) measured Markdown headers, bullets and numbered lists overproduced by very large factors relative to human baselines, with "In conclusion" and "delve into" also heavily amplified, across 13 models including frontier APIs.

## How much LLM text is out there

- Kobak et al. (Science Advances 2025): 15.1M PubMed abstracts; abrupt post-2022 rises in style words (*delves*, *showcasing*, *underscores*, *potential*, *findings*, *critical*); at least 13.5% of 2024 abstracts LLM-processed (lower bound), up to 40% in some subcorpora. The excess words were mostly verbs and adjectives, unlike the content nouns of the Covid years.
- Liang et al. (COLM 2024): ~950k papers; *realm*, *intricate*, *showcasing*, *pivotal* most disproportionately LLM-favoured; LLM-modified sentences reached 17.5% of computer-science abstracts.
- Kousha & Thelwall (ISSI 2025): confirms rises in *delve*, *crucial*, *intricate*, *meticulously*, *pivotal* across fields.

## Detection: what is and is not reliable

- **Experienced readers are good, not perfect.** Russell, Karpinska & Iyyer (ACL 2025): people who often use LLMs for writing detected AI articles very well; a majority vote of five such annotators misclassified 1 of 300, outperforming most automated detectors even after paraphrasing and "humanizing". Individually they were about 90% accurate, so roughly one in ten accusations would be wrong. People who rarely use LLMs did little better than chance. The experts relied on AI vocabulary plus formality, originality and clarity, not on any single word.
- **Automated detectors are unreliable and biased.** Liang et al. (Patterns 2023): seven detectors falsely flagged about 61% of TOEFL essays by non-native English writers as AI, because detectors reward unpredictable word choice. Prompting a model for more literary language pushed detection near zero. The RAID benchmark (Dugan et al., ACL 2024) shows detectors break under paraphrasing and unseen models.
- **Pre-2022 text** (before ChatGPT's public launch on 30 Nov 2022) is very unlikely to be LLM-generated even if it shows some signs.
- **Wikipedia's ineffective indicators:** perfect grammar, "bland" prose, fancy words in general, formal letters, transition words, odd markup.

Practical stance: signs tell you where to edit and what to verify. They never establish who wrote something.

## Where the evidence conflicts or is thin

- **Em dashes.** Journalistic analysis (Washington Post 2025, cited by Wikipedia) reports ChatGPT overusing em dashes; a 2026 preprint across 13 models measured em dashes and semicolons *under*produced relative to human baselines. Likely model- and genre-dependent. Treat em dashes as a weak signal and never remove them from an author who uses them on purpose.
- **Word lists drift.** *Delve* fell sharply in 2025. Lists are snapshots; the stable signal is the *function* of the words (interpretive verbs and intensifiers standing in for facts).
- **Code-specific tells** (comment narration, README emoji headings, vague commit messages) are widely reported by maintainers but I found no controlled study measuring them. They are derived from the general signs plus established guidance (Stack Overflow comment practices, GitHub and Google README guidance, Beams's commit rules).
- **Code quality data** (GitClear) is correlational and from a commercial vendor.
- The 2026 preprints (Rallapalli et al.; Mahapatra; the package-hallucination replication) are not yet peer-reviewed.

## Sources

1. Wikipedia: Signs of AI writing (WikiProject AI Cleanup). https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing
2. Kobak, González-Márquez, Horvát, Lause (2025). Delving into LLM-assisted writing in biomedical publications through excess vocabulary. *Science Advances* 11(27). https://arxiv.org/abs/2406.07016
3. Liang et al. (2024). Mapping the increasing use of LLMs in scientific papers. *COLM*. https://arxiv.org/abs/2404.01268
4. Juzek & Ward (2025). Why does ChatGPT "delve" so much? *COLING*. https://aclanthology.org/2025.coling-main.426
5. Reinhart et al. (2025). Do LLMs write like humans? Variation in grammatical and rhetorical styles. *PNAS* 122(8). https://arxiv.org/abs/2410.16107
6. Russell, Karpinska, Iyyer (2025). People who frequently use ChatGPT for writing tasks are accurate and robust detectors of AI-generated text. *ACL*. https://aclanthology.org/2025.acl-long.267
7. Liang, Yuksekgonul, Mao, Wu, Zou (2023). GPT detectors are biased against non-native English writers. *Patterns* 4(7). https://arxiv.org/abs/2304.02819
8. Spracklen et al. (2025). We have a package for you! Package hallucinations by code-generating LLMs. *USENIX Security*. https://www.usenix.org/conference/usenixsecurity25/presentation/spracklen
9. Kousha & Thelwall (2025). How much are LLMs changing the language of academic papers after ChatGPT? *ISSI*. https://arxiv.org/pdf/2509.09596
10. Rallapalli et al. (2026, preprint). Interpretable stylistic variation in human and LLM writing across genres, models, and decoding strategies. https://arxiv.org/abs/2604.14111
11. Mahapatra (2026, preprint). From context shift to stylistic collapse: why training objectives matter more than scale. https://arxiv.org/abs/2605.28826
12. GitHub Docs: About the repository README file. https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-readmes
13. Google documentation style guide: READMEs. https://google.github.io/styleguide/docguide/READMEs.html
14. Spertus, Best practices for writing code comments (Stack Overflow blog). https://stackoverflow.blog/2021/12/23/best-practices-for-writing-code-comments
15. Beams, How to write a Git commit message. https://chris.beams.io/posts/git-commit/
16. GitClear (2025). AI Copilot Code Quality. https://www.gitclear.com/ai_assistant_code_quality_2025_research
17. curl: bounty removal https://github.com/curl/curl/pull/20312 ; coverage https://hackaday.com/2026/01/26/the-curl-project-drops-bug-bounties-due-to-ai-slop ; RedMonk on maintainers and AI slop https://redmonk.com/kholterhoff/?p=434
