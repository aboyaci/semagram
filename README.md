# Semagram 🔷

An emoji-based written language, designed to carry ideas with a tiny vocabulary and a grammar a cold reader can crack from the text itself.

It started as a joke ("can we write a scientific paper in emoji?"), hit every wall emoji has (no grammar, no negation scope, no abstract vocabulary), and turned into a design exercise in how small a language can be and still say "not all mice sleep" without ambiguity.

A *semagram* is a sign that carries meaning with no phonetic value — the 📜 determinative and the 👤📍👥📦🐾 category glyphs are exactly that. The name is also the claim: every pictographic script that survived went phonetic, and that exit is closed to a language with no spoken form, so this one is semagrams all the way down.

```
📥🐟🌊🔷          in(fish, sea)          A fish is in the sea.
⬆️🐦🌊🔷          above(bird, sea)       A bird is above the sea.
👁️🐟🐦🔷          see(fish, bird)        The fish sees the bird.
🐟💬🎯🙋📍⬆️🔷    fish says: want(I, place-above)
```

## What it is

- **Logographic**, like Chinese: one glyph is one word. There is no alphabet and no spoken form.
- **Isolating**: no inflection of any kind. No gender, no case, no agreement, no irregular forms. Tense and number are optional and context-carried, as in Mandarin.
- **Predicate-first**, like Classical Arabic, Welsh, and Middle Egyptian: `predicate · agent · patient`. It is also how logic and maths write things, `sees(fish, bird)`, which is the closest thing to a language-neutral word order that exists.
- **A pidgin, not a programming language**: short sentences, no nesting, no brackets, heavy reliance on the previous sentence. Depth comes from chaining, never from embedding.
- **Layered vocabulary**: 63 semantic primes (after Wierzbicka and Goddard's Natural Semantic Metalanguage), 66 core roots, and unbounded per-document domain packs declared with `≔`.

## What it is not

It is not a universal language and nobody should learn to speak it. The realistic niche is a **notation**: a compact, language-neutral layer that sits alongside prose, like chemical formulas or Feynman diagrams, so that a Turkish and a Brazilian reader can both decode the same structured abstract with a one-page legend. Its native genre turned out to be the beginner picture book; the scientific paper is the stretch.

## Repository

| Path | What |
|---|---|
| [`dictionary/core.json`](dictionary/core.json) | The dictionary: Layer 0 primes, Layer 1 roots, declared compounds, with English and Turkish glosses and a transparency rating per glyph |
| [`dictionary/packs/`](dictionary/packs/) | Layer 2 domain packs (currently: `attention`) |
| [`dictionary/schema.json`](dictionary/schema.json) | Shape of the dictionary files; enforced by the test suite |
| [`DICTIONARY.md`](DICTIONARY.md) | Generated, human-readable view of the above |
| [`semagram/`](semagram/) | Tokenizer, segmenter, glosser, encoder and linter. No dependencies |
| [`docs/grammar.md`](docs/grammar.md) | The grammar, in full |
| [`docs/design-rules.md`](docs/design-rules.md) | The seven rules every glyph and compound must pass |
| [`docs/history.md`](docs/history.md) | Decision log: what was tried, what broke, what replaced it |
| [`docs/llm-pipeline.md`](docs/llm-pipeline.md) | Future work: the machine-translation pipeline, why it is not the current plan, and what a resumption would need |
| [`docs/ste100.md`](docs/ste100.md) | How much of ASD-STE100 Simplified Technical English this covers |
| [`docs/open-problems.md`](docs/open-problems.md) | What is unsolved |
| [`examples/`](examples/) | The fish and bird story; the abstract of *Attention Is All You Need* |

## The translator

It is honest about being a glosser. It segments text under the no-break rules, labels each word from the dictionary, and renders every sentence as `predicate(agent, patient)`. Producing fluent English is left to the reader, by design.

```sh
python3 -m semagram gloss examples/fish-and-bird.sem        # English gloss
python3 -m semagram gloss --tr examples/fish-and-bird.sem   # Turkish gloss
python3 -m semagram gloss --brief examples/attention-abstract.sem
python3 -m semagram lint  examples/attention-abstract.sem   # grammar checks
python3 -m semagram encode "see fish bird"                  # 👁️🐟🐦🔷
python3 -m semagram dict --pack attention > DICTIONARY.md
python3 -m pytest tests
```

The encoder is a word-by-word dictionary lookup. It will not reorder English for you: write the predicate first yourself. There is no machine translator here, by choice: a prototype existed and was set aside until the language stops moving. The design and the reasoning are in [docs/llm-pipeline.md](docs/llm-pipeline.md).

A document declares its pack with a comment line `# pack: attention`. Lines starting with `#` are comments.

## Status

v0.3. Two texts translate and lint clean. The grammar has stabilized across the last several revisions; the vocabulary is deliberately incomplete and grows by evidence (a word earns a slot when a translation needs it and its compound fails the 3-root rule). The next step is not more design but a cold-reader test: hand someone the fish story with no legend and record where they stall.

## License

Two licences, because there are two different things here.

- **Code** — `semagram/` and `tests/` — is [MIT](LICENSE).
- **The language** — `docs/`, `dictionary/`, `DICTIONARY.md`, `examples/` — is [CC BY 4.0](LICENSE-CC-BY-4.0.txt). Attribute as: *Semagram, by Ali Boyaci*, with a link back.

**Using the language needs no permission from anyone.** Copyright covers expression, not systems: the prose of `docs/grammar.md` and the wording of the glosses are licensed, the grammar and vocabulary themselves are not licensable. So writing a document in Semagram, teaching it, implementing a parser, or shipping a one-page legend in a book or paper carries no obligation under either licence. The CC BY term applies only if you copy or adapt the documentation and dictionary text itself.

One carve-out: `examples/attention-abstract.sem` encodes the structure and numbers of the abstract of *Attention Is All You Need* (Vaswani et al., 2017), which is not ours to relicense. It is included as a worked example of the notation, not as a substitute for the original. The fish-and-bird story is original.
