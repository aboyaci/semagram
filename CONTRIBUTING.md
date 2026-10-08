# Contributing

- Vocabulary grows by evidence only. To propose a root or compound, include the sentence that needed it and show that the honest Layer 0 expression runs to 3+ roots or is ambiguous. Then check it against the seven rules in `docs/design-rules.md` and give it a transparency rating.
- Edit `dictionary/*.json`, never `DICTIONARY.md`; regenerate with `python3 -m semagram dict --pack attention > DICTIONARY.md`.
- Grammar changes need a sentence that breaks under the current rules. Add it to `tests/test_semagram.py` first.
- Every example must pass `python3 -m semagram lint`.
- Original texts only. Do not translate copyrighted prose; the abstract is quoted as structure and numbers, not as sentences.
