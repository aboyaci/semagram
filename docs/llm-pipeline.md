# The LLM pipeline — future work

**Nothing in this document is implemented in the current tree.** A working prototype existed and was set aside; it is preserved at the git tag `llm-pipeline-prototype` and comes back with:

```sh
git checkout llm-pipeline-prototype -- tools/
```

This file is the design and the reasoning, kept because the reasoning is the part worth keeping.

## Why it is not the current plan

The ordering argument is the whole of it. [open-problems.md](open-problems.md) #1 — nobody has read this cold — settles the no-break decision from [history.md](history.md) §16. That decision determines segmentation. Segmentation determines the tokenizer and the added-token list. So any corpus generated before the cold-reader test is hostage to an experiment that has not been run, and a translator trained on it could have to be thrown away wholesale.

A trained model is also a commitment device: it makes the grammar expensive to change at exactly the point where [design-rules.md](design-rules.md) still says vocabulary should grow by evidence, and where the decision log is nineteen revisions deep without having converged. The language is not finished enough to be frozen into weights.

Set against that, what the pipeline bought was measurement — and the vocabulary can also grow by hand, slowly, from texts a human translates. Slower, but it does not front-load a bet on a design that is still moving.

## What it was

A lossy, **auditable** pivot rather than an interlingua. Fifty years of interlingua machine translation (Rosetta, KANT, UNL, DLT) failed on exactly the asymmetries this language has by design. The interesting property was never translation quality: it was that English → Semagram → Turkish puts three-word sentences in the middle that a monolingual reviewer can check. No neural translator offers that; its interlingua is a vector.

```
English ──LLM──▶ Semagram ──lint──▶ (errors fed back, ≤3 retries)
                  │
                  ├──LLM──▶ English' ──LLM judge──▶ keep / drop
                  └──LLM──▶ Turkish
```

- **English → Semagram** is the hard direction: negation scope, coreference, and choosing which three roots to keep. An understanding problem, so a large model does it with the grammar as a hard constraint, and the linter rejects malformed output with the errors fed back into the prompt.
- **Semagram → target** is easy, and the glosser is already half of it. The model gets the text *and* the mechanical gloss, so argument roles are never in doubt and its only job is fluency. For Turkish, the unmarked/🟡/🔴 distinction supplies exactly the -dı/-mış choice.
- **The judge** lists every claim in the original as kept, lost or contradicted. A changed negation scope, a changed number, or a swapped agent and patient is a contradiction.

Two things it did that are worth preserving in any successor. The system prompt was built from the repository itself — `grammar.md`, the generated dictionary, the two examples — so editing the grammar changed model behaviour with no code change. And every kept record carried a stamp of the dictionary version and hashes of `core.json` and `grammar.md`, because the prompt is rebuilt per call and a dictionary edit silently changes what valid output is. Without that stamp there is no way to tell a stale pair from a current one.

## What a resumption would need, in order

1. **The cold-reader test, first.** It is free and it gates everything above.
2. **A held-out eval set**: a few hundred hand-verified pairs, over-sampling what actually breaks — negation scope, quantifier scope, agent/patient order, `👉` resolution across sentences. Graded by the claim metric, not BLEU, which is meaningless on three-word sentences with free sentence splitting.
3. **A prefix validator** — `valid_next_glyphs(prefix) -> set[str]`. The linter judges finished text; constrained decoding needs prefix validity. The grammar is close to regular (closed glyph inventory, fixed slot order, no recursion since the brackets came out in §14), so this is tractable, and it has a clean test: anything the decoder can emit must lint clean. At 1B parameters this matters more than parameter count.
4. **The zero-training control before any training.** A local model with the grammar in context plus constrained decoding. Fine-tuning only means something as a delta against that, and the control may well be enough.
5. **Only then** a corpus, and only in one genre. STE-style procedures are the right first target per [ste100.md](ste100.md): imperative, concrete, no figurative language, and an audience that already accepts a controlled language.

The direction asymmetry survives all of this: Semagram → English is nearly solved by the glosser, and English → Semagram carries the difficulty. If anything ever ships, it ships in that order.

## Known limits of the prototype

- The judge was an LLM judging an LLM. The kept set needed hand spot-checks — Semagram's auditability is the whole reason that was possible.
- `👉` resolution in the back-translation was the most likely silent error. Prefer bound glyphs over pronouns in anything kept as evidence.
- The system prompt ran about 5.3k tokens, rebuilt per call. Cached, so the repetition was nearly free; for a small local model it would need trimming to the glyphs one genre uses.
