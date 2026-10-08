# The translator pipeline

Semagram is not a lossless interlingua and was never going to be one; fifty years of interlingua machine translation (Rosetta, KANT, UNL, DLT) failed on exactly the asymmetries this language has by design. What it is instead is a **lossy, auditable pivot**: English → Semagram → Turkish produces flat, correct Turkish, and the Semagram in the middle is three-word sentences a monolingual reviewer can check. No neural translator offers that; its interlingua is a vector.

## Shape

```
English ──LLM──▶ Semagram ──lint──▶ (errors fed back, ≤3 retries)
                  │
                  ├──LLM──▶ English' ──LLM judge──▶ keep / drop
                  └──LLM──▶ Turkish
```

- **English → Semagram** is the hard direction: scope, coreference, choosing which three roots to keep. An understanding problem, so a large model does it, with the grammar as a hard constraint. The linter rejects malformed output and the errors go back into the prompt. The grammar is small enough that acceptance is high within a retry or two.
- **Semagram → target** is easy and the glosser is already half of it. The LLM gets the Semagram *and* the mechanical gloss, so roles are never in doubt, and its job is fluency: merge chained sentences, resolve 👉, pick articles and verb forms. For Turkish it also picks -dı vs -mış, and Semagram's unmarked/🟡/🔴 distinction gives it exactly that information.
- **The judge** lists every claim in the original and marks it kept, lost or contradicted. Contradicted means a changed negation scope, a changed number, or a swapped agent and patient. Anything contradicted, or more than a third lost, drops the pair.

## Running it

```sh
# a frontier model
export ANTHROPIC_API_KEY=...            # SEMAGRAM_MODEL defaults to claude-sonnet-5-5
                                        # claude-opus-5-5 is the stronger choice for
                                        # English → Semagram, where scope and
                                        # coreference actually have to be got right
python3 tools/synth.py translate --to sem "Not all mice sleep."
python3 tools/synth.py translate --to tr examples/fish-and-bird.sem
python3 tools/synth.py roundtrip "The Transformer uses attention and nothing else."

# a local model (Ollama, vLLM, llama.cpp, LM Studio: anything OpenAI-compatible)
export SEMAGRAM_PROVIDER=openai SEMAGRAM_BASE_URL=http://localhost:11434/v1 SEMAGRAM_MODEL=qwen2.5:14b
python3 tools/synth.py synth corpus.txt --out data/pairs.jsonl

# a vocabulary-evidence round: small, repeatable, reads the gaps file
python3 tools/synth.py synth corpus.txt --out data/pairs.jsonl --limit 300

# offline, to test the plumbing
SEMAGRAM_PROVIDER=stub python3 tools/synth.py roundtrip "A fish is in the sea."
```

`synth` takes a text file (one paragraph per record) or JSONL with an `en` field, and writes three files: `pairs.jsonl` (kept), `pairs.rejects.jsonl` (dropped, with the reason), and `pairs.gaps.json`.

## The gaps file is the point

`pairs.gaps.json` counts every word the model wrote as `# gaps:` because no glyph or honest compound existed, and every lint error by type. This is the vocabulary growth rule from `design-rules.md` with volume behind it: a word enters Layer 1 when it is *frequent* in the genre and has no cheap compound, and frequency is now measured, not guessed. It is also the test of the language: a sentence that will not round-trip is a vocabulary gap or a design limit, and after a few thousand sentences you know which.

## Why training a model is not the current plan

The corpus this pipeline can produce is training data for a small model, and that was the original plan. It is on hold, for a reason that comes straight out of [open-problems.md](open-problems.md) #1: the cold-reader test settles the no-break decision. That decision determines segmentation, segmentation determines the tokenizer and the added-token list, and so a corpus generated now is hostage to an experiment that has not been run. Training first would mean paying for a corpus and then possibly discarding it.

A trained model is also a commitment device. It makes the grammar expensive to change at exactly the point where [design-rules.md](design-rules.md) still says vocabulary should grow by evidence, and where [history.md](history.md) is nineteen revisions deep without having converged.

So the pipeline is kept as a **measuring instrument**, not a data factory:

1. **Vocabulary evidence.** Run a few hundred paragraphs of one genre, read `pairs.gaps.json`, promote what clears the Test A and 3-root bar, repeat until the gaps curve flattens. This is the frequency half of the Layer 1 promotion rule, which two translated texts cannot supply.
2. **Expressiveness regression test.** Keep a fixed set of paragraphs. After a grammar change, re-run and see whether claims start getting lost. Nothing else in the repo can catch that.

What the plan would need, if it is ever resumed: a held-out eval set of a few hundred hand-verified pairs; a prefix validator (`valid_next_glyphs(prefix)`) so a small model cannot emit an ungrammatical sentence, which matters more at 1B than parameter count does; and the zero-training control run first — a local model with this grammar in context plus constrained decoding — because fine-tuning only means something as a delta against that. The direction asymmetry also survives: Semagram → English is nearly solved by the glosser, and English → Semagram carries all the difficulty.

## Cost and provenance

Two things make the pilot cheap enough to run repeatedly.

The system prompt is about 5.3k tokens, identical across every call, and sent in the `system` field, so it is cached (`cache_control: ephemeral` in `tools/llm.py`). Reads cost a tenth of input, writes 1.25×, so it pays off from the second call on. `synth` prints the token totals and warns if the cache was written but never read, which is the signature of something changing the prefix between calls.

Every kept pair carries a `lang` field: the dictionary version, a hash of `core.json`, a hash of `grammar.md`, and the packs in force. The system prompt is rebuilt from the repository on every call, so a dictionary edit silently changes what valid output is — the stamp is what distinguishes a stale pair from a current one without regenerating everything.

## Known limits

- The system prompt is ~5.3k tokens and rebuilt from the repo each call. Cached, so the repetition is nearly free on the Anthropic path; for a small local model, trim the dictionary to the glyphs the genre uses.
- The judge is an LLM judging an LLM. Spot-check the kept set by hand; Semagram's auditability is the whole reason you can.
- 👉 resolution in the back-translation is the most likely silent error. Prefer bound glyphs over pronouns in any text kept as evidence.
